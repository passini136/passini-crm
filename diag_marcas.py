"""
Confere o faturamento de uma marca contra o que está gravado — e diz se há
linha duplicada.

Uso no servidor:
    /srv/passini/venv/crm/bin/python /srv/passini/apps/crm-comercial/diag_marcas.py NAKATA 2026-08

Sem argumentos, usa a marca líder e a última competência.

A tela de Marcas soma direto o faturamento detalhado, sem nenhum cálculo pelo
meio. Se o número dela está acima do relatório do Alfa, a diferença está nas
linhas gravadas — e o suspeito é reimportação que entrou duas vezes.

Não altera nada. Para CORRIGIR, rode com --corrigir no fim.
"""
import json
import os
import sys
from collections import Counter, defaultdict
from pathlib import Path

sys.path.insert(0, "/srv/passini/apps/crm-comercial")

if not os.environ.get("PASSINI_CRM_DATA"):
    for candidate in ("/srv/passini/data/crm", "/srv/passini/data"):
        if (Path(candidate) / "passini_dashboard.db").exists():
            os.environ["PASSINI_CRM_DATA"] = candidate
            break

import backend  # noqa: E402

argumentos = [a for a in sys.argv[1:] if not a.startswith("--")]
corrigir = "--corrigir" in sys.argv

conn = backend.get_connection()
company_id = conn.execute("SELECT id FROM companies LIMIT 1").fetchone()["id"]

competencia = next((a for a in argumentos if len(a) == 7 and a[4] == "-"), None) \
    or backend.crm_latest_competence(conn, company_id)
marca = next((a.upper() for a in argumentos if not (len(a) == 7 and a[4] == "-")), None)
if not marca:
    linha = conn.execute(
        "SELECT brand_name FROM fact_sales_detail WHERE company_id = ? AND competence = ? "
        "AND TRIM(COALESCE(brand_name,'')) <> '' GROUP BY brand_name "
        "ORDER BY SUM(net_value) DESC LIMIT 1", (company_id, competencia)).fetchone()
    marca = linha["brand_name"] if linha else ""

print(f"Banco: {backend.DB_PATH}")
print(f"Marca: {marca} · Competência: {competencia}\n")


def money(v):
    return f"R$ {float(v or 0):>15,.2f}"


# ── 1. O que está gravado ────────────────────────────────────────────────
r = conn.execute(
    "SELECT COUNT(*) n, ROUND(SUM(quantity),0) q, ROUND(SUM(net_value),2) v "
    "FROM fact_sales_detail WHERE company_id = ? AND competence = ? AND brand_name = ?",
    (company_id, competencia, marca)).fetchone()
print("1) O QUE ESTÁ GRAVADO (é o que a tela mostra)")
print(f"   {r['n']} linha(s) · {int(r['q'] or 0)} item(ns) · {money(r['v'])}")
print("   Compare com o relatório do Alfa para esta marca e mês.\n")

# ── 2. A migração de identidade já rodou? ────────────────────────────────
pendente = backend.sales_detail_needs_rehash(conn)
print("2) MIGRAÇÃO DE IDENTIDADE")
if pendente:
    print(f"   >> PENDENTE: a base está na versão "
          f"{backend.stored_signature_version(conn)} e o sistema usa a "
          f"{backend.SALES_SIGNATURE_VERSION}.")
    print("   Reinicie o serviço — a migração roda sozinha no boot.")
else:
    print("   OK: todas as linhas já estão no formato novo.")

# ── 3. Linhas duplicadas ─────────────────────────────────────────────────
print("\n3) LINHAS DUPLICADAS NESTA COMPETÊNCIA")
linhas = conn.execute(
    "SELECT id, import_id, seller_name, client_name, city_name, gtin_value, "
    "       manufacturer_sku, issue_date, quantity, gross_value, discount_value, "
    "       freight_value, return_quantity, return_value, net_value, sale_share, brand_name "
    "FROM fact_sales_detail WHERE company_id = ? AND competence = ?",
    (company_id, competencia)).fetchall()

grupos = defaultdict(list)
for x in linhas:
    payload = {
        "seller": x["seller_name"], "client": x["client_name"], "city": x["city_name"] or "",
        "gtin": x["gtin_value"] or "", "manufacturer": x["manufacturer_sku"] or "",
        "issue_date": backend.normalize_whitespace(x["issue_date"])[:10],
        "quantity": float(x["quantity"] or 0), "gross": float(x["gross_value"] or 0),
        "discount": float(x["discount_value"] or 0), "freight": float(x["freight_value"] or 0),
        "qty_return": float(x["return_quantity"] or 0),
        "value_return": float(x["return_value"] or 0),
        "net": float(x["net_value"] or 0), "sale_share": float(x["sale_share"] or 0),
    }
    grupos[json.dumps(payload, ensure_ascii=False, sort_keys=True)].append(x)

excedente_linhas = 0
excedente_valor = 0.0
excedente_marca = 0.0
for sig, grupo in grupos.items():
    if len(grupo) < 2:
        continue
    por_import = Counter(g["import_id"] for g in grupo)
    # Quantas vezes a venda existe de verdade: o máximo que UMA importação
    # trouxe. Cada arquivo do Alfa contém o período inteiro, então venda
    # legitimamente repetida aparece repetida em todo arquivo.
    verdadeiro = max(por_import.values())
    sobra = len(grupo) - verdadeiro
    if sobra > 0:
        excedente_linhas += sobra
        excedente_valor += sobra * float(grupo[0]["net_value"] or 0)
        if grupo[0]["brand_name"] == marca:
            excedente_marca += sobra * float(grupo[0]["net_value"] or 0)

if excedente_linhas:
    print(f"   >> {excedente_linhas} linha(s) a mais, somando {money(excedente_valor)}")
    print(f"      Sendo {money(excedente_marca)} da marca {marca}.")
    print("      Rode de novo com --corrigir para remover.")
else:
    print("   Nenhuma duplicidade. O número gravado é o que veio dos arquivos.")

# ── 4. De onde veio cada linha ───────────────────────────────────────────
print("\n4) IMPORTAÇÕES QUE ALIMENTAM ESTA COMPETÊNCIA")
for x in conn.execute(
    "SELECT d.import_id, i.imported_at, COUNT(*) linhas, ROUND(SUM(d.net_value),2) v "
    "FROM fact_sales_detail d LEFT JOIN imports i ON i.id = d.import_id "
    "WHERE d.company_id = ? AND d.competence = ? GROUP BY d.import_id "
    "ORDER BY i.imported_at", (company_id, competencia)).fetchall():
    # Valor por linha denuncia o arquivo estranho: os diários ficam todos na
    # mesma faixa, e o que destoa costuma ser o problema.
    _por_linha = float(x["v"] or 0) / (x["linhas"] or 1)
    print(f"   import {str(x['import_id']):<6} {str(x['imported_at'])[:19]:<20} "
          f"{x['linhas']:>7} linha(s)  {money(x['v'])}   {_por_linha:>8.2f}/linha")

# ── 4b. Confronto com a fonte oficial ────────────────────────────────────
print("\n5) DETALHADO x OFICIAL (relatório de custo x venda)")
det = conn.execute(
    "SELECT ROUND(SUM(net_value),2) v FROM fact_sales_detail "
    "WHERE company_id = ? AND competence = ?", (company_id, competencia)).fetchone()["v"] or 0
ofi = conn.execute(
    "SELECT ROUND(SUM(net_value),2) v FROM fact_unit_summary "
    "WHERE company_id = ? AND competence = ?", (company_id, competencia)).fetchone()["v"] or 0
print(f"   faturamento detalhado : {money(det)}")
print(f"   resumo por unidade    : {money(ofi)}")
if ofi:
    print(f"   diferença             : {money(det - ofi)}  ({100 * (det / ofi - 1):+.0f}%)")
    if abs(det - ofi) / ofi > 0.05:
        print("   >> O detalhado está acima do oficial. Ver o item 6.")

# ── 6. Repetição por chave frouxa ────────────────────────────────────────
# A assinatura exata não pega tudo: dois relatórios do Alfa podem descrever a
# mesma venda com pequenas diferenças. Aqui a comparação é só por cliente, dia
# e valor — se a MESMA combinação aparece em importações diferentes, é forte
# indício de que o mesmo dia entrou duas vezes.
print("\n6) MESMA VENDA EM IMPORTAÇÕES DIFERENTES (chave frouxa)")
frouxo = defaultdict(list)
for x in linhas:
    frouxo[(
        backend.normalize_client_key(x["client_name"]),
        backend.normalize_whitespace(x["issue_date"])[:10],
        round(float(x["net_value"] or 0), 2),
        backend.normalize_whitespace(x["seller_name"]),
    )].append(x)

repetido_valor = 0.0
repetido_linhas = 0
por_import_extra: Counter = Counter()
for k, grupo in frouxo.items():
    if len(grupo) < 2:
        continue
    imports = Counter(g["import_id"] for g in grupo)
    if len(imports) < 2:
        continue      # repetiu dentro do MESMO arquivo: pode ser venda real
    verdadeiro = max(imports.values())
    sobra = len(grupo) - verdadeiro
    if sobra > 0:
        repetido_linhas += sobra
        repetido_valor += sobra * float(grupo[0]["net_value"] or 0)
        ordenados = sorted(imports.items(), key=lambda x: (x[0] is None, x[0]))
        for imp, _ in ordenados[1:]:
            por_import_extra[imp] += 1

if repetido_linhas:
    print(f"   >> {repetido_linhas} linha(s) repetida(s) entre importações, "
          f"somando {money(repetido_valor)}")
    print("   Importações que mais trouxeram repetição:")
    for imp, qtd in por_import_extra.most_common(6):
        print(f"      import {imp}: {qtd} linha(s)")
else:
    print("   Nenhuma. Cada venda aparece em uma importação só.")

# ── 7. Correção ──────────────────────────────────────────────────────────
if repetido_linhas:
    print("\n   ATENÇÃO: esta contagem é só um INDÍCIO. A chave frouxa junta vendas")
    print("   diferentes de mesmo valor para o mesmo cliente no mesmo dia, então")
    print("   ela superestima. NÃO use como base para apagar — use limpar_import.py,")
    print("   que remove uma importação inteira e identificada.")

if corrigir and (excedente_linhas or pendente):
    print("\n7) CORRIGINDO")
    removidas = backend.rehash_sales_detail(conn)
    novo = conn.execute(
        "SELECT COUNT(*) n, ROUND(SUM(net_value),2) v FROM fact_sales_detail "
        "WHERE company_id = ? AND competence = ? AND brand_name = ?",
        (company_id, competencia, marca)).fetchone()
    print(f"   {removidas} linha(s) removida(s) no total.")
    print(f"   {marca} em {competencia} agora: {novo['n']} linha(s) · {money(novo['v'])}")
    backend.invalidate_crm_cache(company_id)
    print("   Cache limpo. Recarregue a tela.")
elif corrigir:
    print("\n7) Nada a corrigir.")

conn.close()
