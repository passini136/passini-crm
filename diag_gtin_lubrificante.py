"""
O GTIN resolve o custo dos lubrificantes?

Uso:
    /srv/passini/venv/crm/bin/python /srv/passini/apps/crm-comercial/diag_gtin_lubrificante.py
    /srv/passini/venv/crm/bin/python /srv/passini/apps/crm-comercial/diag_gtin_lubrificante.py MOBIL

A diretoria explicou a causa: em lubrificante compra-se caixa da fábrica, abre-se
a caixa e o custo é dividido. A REFERÊNCIA DO FABRICANTE é a mesma para todas as
embalagens do mesmo óleo — o que separa a caixa do litro é o GTIN. Como o custo
hoje casa por referência + marca, o litro vendido recebe o custo da caixa, e a
margem sai em -300%.

A correção óbvia seria casar por GTIN. Só que há um registro anterior deste
projeto dizendo que `gtin_value` no faturamento vem SEMPRE VAZIO do Alfa — foi
por isso que a chave antiga (item_code = gtin_value) casava zero e a tela de
linha ficou vazia por meses. Aquilo foi medido em 10/09/2026.

Então a primeira pergunta NÃO é "como casar por GTIN", é "existe GTIN no dado
de hoje?". Trocar a chave sem conferir isso substituiria uma margem errada por
uma margem ausente.

Não altera nada.
"""
import os
import sys
from pathlib import Path

sys.path.insert(0, "/srv/passini/apps/crm-comercial")

if not os.environ.get("PASSINI_CRM_DATA"):
    for candidate in ("/srv/passini/data/crm", "/srv/passini/data"):
        if (Path(candidate) / "passini_dashboard.db").exists():
            os.environ["PASSINI_CRM_DATA"] = candidate
            break

import backend  # noqa: E402

conn = backend.get_connection()
company_id = conn.execute("SELECT id FROM companies LIMIT 1").fetchone()["id"]
comp = backend.crm_latest_competence(conn, company_id)
marca_alvo = " ".join(sys.argv[1:]).strip().upper() or "MAXON"

print(f"Banco: {backend.DB_PATH}")
print(f"Competência: {comp}  ·  Marca examinada: {marca_alvo}\n")

LUBRIFICANTES = ("MAXON", "MOBIL", "MENZOIL", "HAVOLINE", "RADNAQ", "DX LUB",
                 "TUTELA", "LUBRAX", "VALVOLINE", "TEXACO")

# ── 1. Existe GTIN no faturamento? ──────────────────────────────────────────
print("1) O FATURAMENTO TRAZ GTIN?")
r = conn.execute(
    """SELECT COUNT(*) linhas,
              SUM(CASE WHEN TRIM(COALESCE(gtin_value,'')) <> '' THEN 1 ELSE 0 END) com_gtin,
              COALESCE(SUM(net_value),0) liquido,
              COALESCE(SUM(CASE WHEN TRIM(COALESCE(gtin_value,'')) <> ''
                           THEN net_value END),0) liquido_com_gtin
       FROM fact_sales_detail WHERE company_id = ? AND competence = ? AND net_value > 0""",
    (company_id, comp)).fetchone()
pct_l = 100 * r["com_gtin"] / r["linhas"] if r["linhas"] else 0
pct_v = 100 * r["liquido_com_gtin"] / r["liquido"] if r["liquido"] else 0
print(f"   {r['com_gtin']:,} de {r['linhas']:,} linha(s) com GTIN ({pct_l:.1f}%)")
print(f"   {backend.brl(r['liquido_com_gtin'])} de {backend.brl(r['liquido'])} ({pct_v:.1f}%)")

rl = conn.execute(
    f"""SELECT COUNT(*) linhas,
               SUM(CASE WHEN TRIM(COALESCE(gtin_value,'')) <> '' THEN 1 ELSE 0 END) com_gtin
        FROM fact_sales_detail WHERE company_id = ? AND competence = ? AND net_value > 0
          AND UPPER(TRIM(COALESCE(brand_name,''))) IN ({','.join('?' for _ in LUBRIFICANTES)})""",
    (company_id, comp, *LUBRIFICANTES)).fetchone()
pct_lub = 100 * rl["com_gtin"] / rl["linhas"] if rl["linhas"] else 0
print(f"   Só lubrificantes: {rl['com_gtin']:,} de {rl['linhas']:,} ({pct_lub:.1f}%)")

if pct_v < 1:
    print("\n   >> O GTIN CONTINUA VAZIO NO FATURAMENTO. Não dá para casar custo")
    print("      por GTIN: a conta ficaria sem custo nenhum, o que é pior que a")
    print("      margem errada de hoje. Duas saídas possíveis:")
    print("        a) pedir ao Alfa que exporte o GTIN no faturamento detalhado;")
    print("        b) usar a UNIDADE DE MEDIDA do catálogo para converter o custo")
    print("           da caixa para a unidade vendida — ver item 4.")

# ── 2. A referência realmente se repete entre embalagens? ───────────────────
# É esta repetição que faz a média do custo misturar caixa com litro.
print(f"\n2) A REFERÊNCIA SE REPETE ENTRE EMBALAGENS? ({marca_alvo})")
print(f"   {'REFERÊNCIA':<20}{'ITENS':>7}{'UNIDADES':<22}{'CUSTOS CADASTRADOS':<34}")
for r in conn.execute(
    """SELECT UPPER(TRIM(manufacturer_ref)) ref, COUNT(*) n,
              GROUP_CONCAT(DISTINCT COALESCE(unit_of_measure,'?')) unidades,
              GROUP_CONCAT(ROUND(cost_price,2)) custos
       FROM item_catalog
       WHERE company_id = ? AND UPPER(TRIM(COALESCE(brand_name,''))) = ?
         AND TRIM(COALESCE(manufacturer_ref,'')) <> ''
       GROUP BY ref HAVING n > 1 ORDER BY n DESC LIMIT 10""",
        (company_id, marca_alvo)).fetchall():
    print(f"   {r['ref'][:19]:<20}{r['n']:>7} {str(r['unidades'])[:21]:<22}"
          f"{str(r['custos'])[:33]:<34}")
print("\n   >> Se a mesma referência aparece com custos muito diferentes, a média")
print("      por referência está somando caixa com unidade — é a raiz do -256%.")

# ── 3. O catálogo tem GTIN? ─────────────────────────────────────────────────
print("\n3) O CATÁLOGO TEM GTIN PARA ESSES ITENS?")
r = conn.execute(
    """SELECT COUNT(*) n, SUM(CASE WHEN TRIM(COALESCE(gtin,'')) <> '' THEN 1 ELSE 0 END) com
       FROM item_catalog WHERE company_id = ?
         AND UPPER(TRIM(COALESCE(brand_name,''))) = ?""",
    (company_id, marca_alvo)).fetchone()
print(f"   {r['com']} de {r['n']} item(ns) de {marca_alvo} têm GTIN cadastrado")
rg = conn.execute(
    "SELECT COUNT(*) n, SUM(CASE WHEN TRIM(COALESCE(gtin,'')) <> '' THEN 1 ELSE 0 END) com "
    "FROM item_catalog WHERE company_id = ?", (company_id,)).fetchone()
print(f"   No catálogo inteiro: {rg['com']:,} de {rg['n']:,} "
      f"({100 * rg['com'] / rg['n'] if rg['n'] else 0:.1f}%)")

# ── 4. A unidade de medida explica o fator? ─────────────────────────────────
# Se o GTIN não vier no faturamento, esta é a saída: o catálogo diz se o item
# é CX, LT ou UN, e o fator entre o custo e o preço vendido deve bater com o
# tamanho da embalagem.
print(f"\n4) A UNIDADE DE MEDIDA EXPLICA O FATOR? ({marca_alvo})")
print(f"   {'SKU VENDIDO':<18}{'QTD':>7}{'R$/UN VEND':>12}{'CUSTO CAD':>12}"
      f"{'FATOR':>7}  UNIDADES NO CATÁLOGO")
backend.ensure_catalogo_custo_temp(conn, company_id)
for r in conn.execute(
    """SELECT f.sku_key, SUM(f.quantity) q, SUM(f.net_value) v, MAX(c.custo) custo
       FROM fact_sales_detail f
       LEFT JOIN catalogo_custo c ON c.ref = UPPER(TRIM(f.sku_key))
                                 AND c.marca = UPPER(TRIM(COALESCE(f.brand_name,'')))
       WHERE f.company_id = ? AND f.competence = ? AND f.net_value > 0
         AND UPPER(TRIM(COALESCE(f.brand_name,''))) = ?
       GROUP BY f.sku_key ORDER BY v DESC LIMIT 10""",
        (company_id, comp, marca_alvo)).fetchall():
    q = float(r["q"] or 0)
    v = float(r["v"] or 0)
    unit = v / q if q else 0
    custo = float(r["custo"] or 0)
    fator = custo / unit if unit else 0
    det = conn.execute(
        """SELECT GROUP_CONCAT(COALESCE(unit_of_measure,'?') || ':' || ROUND(cost_price,2)) d
           FROM item_catalog WHERE company_id = ?
             AND UPPER(TRIM(manufacturer_ref)) = ?
             AND UPPER(TRIM(COALESCE(brand_name,''))) = ?""",
        (company_id, str(r["sku_key"]).strip().upper(), marca_alvo)).fetchone()["d"]
    print(f"   {str(r['sku_key'])[:17]:<18}{q:>7,.0f}{backend.brl(unit):>12}"
          f"{backend.brl(custo):>12}{fator:>6.1f}x  {str(det or '—')[:40]}")
print("\n   >> Fator próximo de 12, 20 ou 24 confirma embalagem: caixa de 12x1L,")
print("      balde de 20L. Fator irregular significa custo cadastrado errado")
print("      item a item, e aí só o cadastro resolve.")

# ── 5. Quanto do problema é lubrificante? ───────────────────────────────────
print("\n5) O PROBLEMA É SÓ DE LUBRIFICANTE?")
d = backend.resultados_margem_marca(conn, company_id, "empresa", "", comp, limite=300)
suspeitas = [b for b in d["brands"] if b["costSuspect"]]
lub = [b for b in suspeitas if any(x in b["brand"] for x in LUBRIFICANTES)]
outras = [b for b in suspeitas if b not in lub]
print(f"   {len(suspeitas)} marca(s) com margem impossível")
print(f"   Lubrificantes conhecidos: {len(lub)} · "
      f"{backend.brl(sum(b['revenue'] for b in lub))}")
print(f"   Outras: {len(outras)} · {backend.brl(sum(b['revenue'] for b in outras))}")
if outras:
    print(f"\n   {'MARCA':<22}{'LÍQUIDO':>14}{'MARGEM':>10}{'R$/PEÇA':>11}")
    for b in sorted(outras, key=lambda x: x["revenue"], reverse=True)[:12]:
        print(f"   {b['brand'][:21]:<22}{backend.brl(b['revenue']):>14}"
              f"{b['marginPct']:>9.0f}%{backend.brl(b['ticketPerPiece']):>11}")
    print("\n   >> Estas NÃO são óleo. Se o padrão for o mesmo (custo muito maior")
    print("      que o preço unitário), o problema de embalagem é mais amplo que")
    print("      lubrificante e a correção do cadastro precisa ser mais larga.")

conn.close()
