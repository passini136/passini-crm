"""
A busca de item na carteira acha a peça por QUALQUER código?

Uso:
    /srv/passini/venv/crm/bin/python /srv/passini/apps/crm-comercial/diag_busca_item.py

No balcão circulam quatro códigos da mesma peça: o do fabricante (o que o
mecânico fala), o interno da Passini (o da etiqueta), o GTIN de barras e a
referência do catálogo. A busca cobria só os dois primeiros — quem digitasse o
código interno, que é o mais natural para quem está no balcão, recebia
"nenhum cliente comprou essa peça" e concluía que ninguém compra.

O GTIN é o caso mais delicado: ele chega SEMPRE VAZIO no faturamento do Alfa.
A busca por código de barras só funciona resolvendo GTIN → código interno no
catálogo. Este diagnóstico confirma que esse caminho existe no dado real.

O teste é feito com peças REAIS: pega itens que venderam no período e procura
cada um pelos seus próprios códigos. Se a busca não achar a peça pelo código
que ela mesma tem, não vai achar nada no uso de verdade.

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

print(f"Banco: {backend.DB_PATH}")
print(f"Competência mais recente: {comp}\n")

# ── 1. Os códigos existem no faturamento? ───────────────────────────────────
print("1) QUAIS CÓDIGOS O FATURAMENTO TRAZ")
r = conn.execute(
    """SELECT COUNT(*) n,
              SUM(CASE WHEN TRIM(COALESCE(manufacturer_sku,'')) <> '' THEN 1 ELSE 0 END) fab,
              SUM(CASE WHEN TRIM(COALESCE(item_code,'')) <> '' THEN 1 ELSE 0 END) interno,
              SUM(CASE WHEN TRIM(COALESCE(gtin_value,'')) <> '' THEN 1 ELSE 0 END) gtin,
              SUM(CASE WHEN TRIM(COALESCE(sku_key,'')) <> '' THEN 1 ELSE 0 END) sku
       FROM fact_sales_detail WHERE company_id = ? AND competence = ?""",
    (company_id, comp)).fetchone()
n = r["n"] or 1
for rot, v in (("Fabricante", r["fab"]), ("Código interno", r["interno"]),
               ("GTIN", r["gtin"]), ("sku_key", r["sku"])):
    print(f"   {rot:<18}{v or 0:>9,} de {n:,} ({100 * (v or 0) / n:.0f}%)")
if not (r["interno"] or 0):
    print("\n   >> O CÓDIGO INTERNO ESTÁ VAZIO. A competência não foi reimportada")
    print("      depois da correção da coluna E — a busca por ele não vai achar")
    print("      nada, e não é defeito da busca.")

# ── 2. Buscar a peça pelos códigos dela mesma ───────────────────────────────
print("\n2) A BUSCA ACHA A PEÇA POR CADA UM DOS CÓDIGOS DELA?")
amostra = conn.execute(
    """SELECT f.manufacturer_sku, f.item_code, f.sku_key, f.brand_name,
              MAX(c.gtin) AS gtin, COUNT(DISTINCT f.client_name) AS clientes
       FROM fact_sales_detail f
       LEFT JOIN item_catalog c
              ON c.company_id = f.company_id
             AND UPPER(TRIM(c.item_code)) = UPPER(TRIM(COALESCE(f.item_code,'')))
       WHERE f.company_id = ? AND f.competence = ? AND f.net_value > 0
         AND TRIM(COALESCE(f.item_code,'')) <> ''
       GROUP BY f.item_code HAVING clientes >= 3
       ORDER BY clientes DESC LIMIT 6""",
    (company_id, comp)).fetchall()

if not amostra:
    print("   Nenhum item com código interno e 3+ clientes. Reimporte a competência.")
else:
    print(f"   {'PEÇA':<22}{'CÓDIGO':<14}{'TIPO DE CÓDIGO':<20}{'CLIENTES ACHADOS':>17}")
    falhas = 0
    for a in amostra:
        testes = [
            ("fabricante", a["manufacturer_sku"]),
            ("interno", a["item_code"]),
            ("sku_key", a["sku_key"]),
            ("GTIN (catálogo)", a["gtin"]),
        ]
        rotulo = backend.normalize_whitespace(a["manufacturer_sku"] or a["item_code"])[:21]
        primeiro = True
        for nome_tipo, codigo in testes:
            codigo = backend.normalize_whitespace(codigo)
            if not codigo:
                continue
            achado = backend.item_purchase_details(conn, company_id, codigo)
            qtd = len(achado or {})
            marca = ""
            if qtd == 0:
                marca = "  ← NÃO ACHOU"
                falhas += 1
            print(f"   {(rotulo if primeiro else ''):<22}{codigo[:13]:<14}"
                  f"{nome_tipo:<20}{qtd:>17}{marca}")
            primeiro = False
        print()
    print(f"   {falhas} busca(s) sem resultado")
    if falhas:
        print("   >> Código que a própria peça tem e a busca não acha é defeito")
        print("      da busca, não do dado.")
    else:
        print("   >> Todos os códigos encontram a peça.")

# ── 3. Os filtros de marca, linha e tipo devolvem gente? ────────────────────
print("3) FILTRAR POR MARCA, LINHA E TIPO")
op = backend.opcoes_compra_carteira(conn, company_id)
print(f"   Opções oferecidas: {len(op['brands'])} marca(s), "
      f"{len(op['lines'])} linha(s), {len(op['types'])} tipo(s)")
print(f"\n   {'FILTRO':<16}{'VALOR':<24}{'CLIENTES':>10}")
for chave, rotulo in (("brands", "marca"), ("lines", "linha"), ("types", "tipo")):
    for valor in (op[chave] or [])[:3]:
        kwargs = {"marca": valor} if chave == "brands" else (
            {"linha": valor} if chave == "lines" else {"tipo": valor})
        achados = backend.clientes_que_compraram(conn, company_id, **kwargs)
        n_ach = len(achados or [])
        print(f"   {rotulo:<16}{valor[:23]:<24}{n_ach:>10}"
              f"{'  ← VAZIO' if not n_ach else ''}")
print("\n   >> Opção oferecida no filtro que devolve zero cliente é armadilha:")
print("      o gestor escolhe, a tela esvazia e ele acha que quebrou.")

# ── 4. Sem filtro continua sendo sem filtro ─────────────────────────────────
# A distinção entre None ("não filtre") e conjunto vazio ("ninguém comprou") é
# o que impede a carteira inteira de sumir quando nada foi escolhido.
print("\n4) SEM FILTRO, A CARTEIRA NÃO PODE SUMIR")
vazio = backend.clientes_que_compraram(conn, company_id)
print(f"   clientes_que_compraram() sem argumentos devolve: {vazio!r}")
print("   >> Tem de ser None. Conjunto vazio esvaziaria a carteira inteira."
      if vazio is None else "   >> ERRADO: deveria ser None.")

conn.close()
