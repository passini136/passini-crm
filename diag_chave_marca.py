"""
A marca do catálogo é escrita igual à do faturamento?

Uso:
    /srv/passini/venv/crm/bin/python /srv/passini/apps/crm-comercial/diag_chave_marca.py

Duas perguntas que decidem como escrever o JOIN, e errar qualquer uma INFLA
FATURAMENTO — o mesmo estrago que custou agosto:

  1. Se a marca no catálogo ("VISCONDE") não for escrita como no faturamento
     ("VISCONDE RADIADORES", por exemplo), incluir a marca na chave derruba o
     casamento de 99,6% para quase nada.
  2. 2.148 referências existem em mais de um item do catálogo. Um LEFT JOIN
     contra lado direito repetido DUPLICA a linha de venda e multiplica o
     valor. Hoje isso não aparece porque a chave casa zero; com a chave certa,
     apareceria na hora — e como número maior, que ninguém questiona.

Não altera nada.
"""
import os
import sys
from collections import defaultdict
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
comp = (backend.query_competences(conn, company_id) or [""])[0]
print(f"Banco: {backend.DB_PATH}")
print(f"Competência: {comp}\n")


def n(v):
    return (v or "").strip().upper()


# ── 1. As marcas dos dois lados ──────────────────────────────────────────────
print("1) COMO A MARCA É ESCRITA DE CADA LADO")
marcas_cat = {n(r[0]) for r in conn.execute(
    "SELECT DISTINCT brand_name FROM item_catalog WHERE company_id = ?", (company_id,)).fetchall() if n(r[0])}
marcas_venda = {n(r[0]) for r in conn.execute(
    "SELECT DISTINCT brand_name FROM fact_sales_detail WHERE company_id = ? AND competence = ?",
    (company_id, comp)).fetchall() if n(r[0])}
print(f"   catálogo...: {len(marcas_cat)} marca(s) · exemplos: "
      + ", ".join(sorted(marcas_cat)[:6]))
print(f"   faturamento: {len(marcas_venda)} marca(s) · exemplos: "
      + ", ".join(sorted(marcas_venda)[:6]))
comuns = marcas_cat & marcas_venda
print(f"\n   {len(comuns)} marca(s) escritas EXATAMENTE igual nos dois")
so_venda = sorted(marcas_venda - marcas_cat)
if so_venda:
    print(f"   {len(so_venda)} marca(s) do faturamento sem par no catálogo: "
          + ", ".join(so_venda[:10]))

# ── 2. O casamento com e sem a marca na chave ────────────────────────────────
print("\n2) O QUE ACONTECE COM O CASAMENTO")
cat_por_ref: dict[str, set] = defaultdict(set)
cat_por_ref_marca: dict[tuple, set] = defaultdict(set)
for r in conn.execute(
    "SELECT manufacturer_ref, brand_name, item_subgroup FROM item_catalog "
    "WHERE company_id = ? AND TRIM(COALESCE(manufacturer_ref,'')) <> ''",
    (company_id,)).fetchall():
    linha = n(r["item_subgroup"])
    cat_por_ref[n(r["manufacturer_ref"])].add(linha)
    cat_por_ref_marca[(n(r["manufacturer_ref"]), n(r["brand_name"]))].add(linha)

vendas = conn.execute(
    "SELECT sku_key, brand_name, net_value FROM fact_sales_detail "
    "WHERE company_id = ? AND competence = ?", (company_id, comp)).fetchall()
total = sum(float(r["net_value"] or 0) for r in vendas)

so_ref = so_ref_v = com_marca = com_marca_v = 0.0
duplicaria = duplicaria_v = 0.0
for r in vendas:
    v = float(r["net_value"] or 0)
    chave = n(r["sku_key"])
    if chave in cat_por_ref:
        so_ref += 1
        so_ref_v += v
        # Quantos itens do catálogo essa venda encontraria? Mais de um = a linha
        # de venda sairia repetida no LEFT JOIN, e o valor sairia multiplicado.
        if len(cat_por_ref[chave]) > 1:
            duplicaria += 1
            duplicaria_v += v
    if (chave, n(r["brand_name"])) in cat_por_ref_marca:
        com_marca += 1
        com_marca_v += v

def pct(x):
    return 100 * x / total if total else 0

print(f"   {'chave':<28}{'% LINHAS':>10}{'% VALOR':>10}")
print(f"   {'só a referência':<28}{100 * so_ref / len(vendas):>9.1f}%{pct(so_ref_v):>9.1f}%")
print(f"   {'referência + marca':<28}{100 * com_marca / len(vendas):>9.1f}%{pct(com_marca_v):>9.1f}%")

print("\n3) O RISCO DE INFLAR")
print(f"   {int(duplicaria)} linha(s) · {backend.brl(duplicaria_v)} ({pct(duplicaria_v):.1f}% do mês)")
print("   casariam com MAIS DE UM item do catálogo. Num LEFT JOIN direto, essas")
print("   linhas sairiam repetidas e o valor da tela ficaria acima do real.")

print("\n4) LEITURA")
if com_marca_v >= so_ref_v * 0.95:
    print("   >> A marca é escrita igual nos dois. Use referência + marca no JOIN:")
    print("      mantém o casamento e mata quase toda a ambiguidade.")
else:
    perdido = pct(so_ref_v) - pct(com_marca_v)
    print(f"   >> Incluir a marca DERRUBA o casamento em {perdido:.1f} ponto(s) do valor.")
    print("      A marca é escrita diferente nos dois arquivos — não sirva de chave.")
    print("      Junte só pela referência e resolva a ambiguidade agrupando o")
    print("      catálogo antes do JOIN (uma linha por referência).")
print("\n   Em qualquer caso, o catálogo precisa ser AGRUPADO antes de entrar no")
print("   JOIN. Sem isso, referência repetida duplica a venda — e o número sobe,")
print("   que é o tipo de erro que ninguém contesta.")

conn.close()
