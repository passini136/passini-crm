"""
Compara o faturamento entre as três fontes e aponta onde elas divergem.

Uso no servidor:
    /srv/passini/venv/crm/bin/python /srv/passini/apps/crm-comercial/diag_faturamento.py
    /srv/passini/venv/crm/bin/python /srv/passini/apps/crm-comercial/diag_faturamento.py 2026-08

O painel usa DUAS bases diferentes:
  - fact_unit_summary / fact_vendor_summary → o total do executivo
  - fact_sales_detail                       → as quebras (carteira, PJ/PF, cidade)

Quando as duas discordam, os cartões mostram parte maior que o todo. Este
script diz de quanto é a diferença, em qual unidade e qual a causa provável.
Não altera nada no banco.
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
competencia = sys.argv[1] if len(sys.argv) > 1 else (
    backend.crm_latest_competence(conn, company_id) or backend.date.today().strftime("%Y-%m"))

print(f"Banco: {backend.DB_PATH}")
print(f"Competência: {competencia}\n")


def money(v):
    return f"R$ {float(v or 0):>16,.2f}"


# ── 1. Total por fonte ───────────────────────────────────────────────────
detalhe = conn.execute(
    "SELECT COALESCE(SUM(net_value),0) v, COUNT(*) n, COUNT(DISTINCT client_name) c "
    "FROM fact_sales_detail WHERE company_id = ? AND competence = ?",
    (company_id, competencia)).fetchone()
unidade = conn.execute(
    "SELECT COALESCE(SUM(net_value),0) v FROM fact_unit_summary "
    "WHERE company_id = ? AND competence = ?", (company_id, competencia)).fetchone()
vendedor = conn.execute(
    "SELECT COALESCE(SUM(net_value),0) v FROM fact_vendor_summary "
    "WHERE company_id = ? AND competence = ?", (company_id, competencia)).fetchone()

print("1) TOTAL POR FONTE")
print(f"   Detalhado (fact_sales_detail)   {money(detalhe['v'])}   "
      f"{detalhe['n']} linha(s), {detalhe['c']} cliente(s)")
print(f"   Resumo por unidade              {money(unidade['v'])}")
print(f"   Resumo por vendedor             {money(vendedor['v'])}")

base = float(unidade["v"] or 0)
if base:
    dif = float(detalhe["v"] or 0) - base
    print(f"\n   Diferença detalhado − unidade:  {money(dif)}  "
          f"({100 * dif / base:+.1f}%)")
    if abs(dif) / base > 0.05:
        print("   >> ACIMA DE 5%: não é arredondamento. Ver os itens 2 e 3.")

# ── 2. Diferença por unidade ─────────────────────────────────────────────
print("\n2) POR UNIDADE")
por_unidade = {backend.normalize_unit(r["unit_name"]): float(r["v"] or 0) for r in conn.execute(
    "SELECT unit_name, SUM(net_value) v FROM fact_unit_summary "
    "WHERE company_id = ? AND competence = ? GROUP BY unit_name",
    (company_id, competencia)).fetchall()}
det_unidade = {backend.normalize_unit(r["unit_name"]): float(r["v"] or 0) for r in conn.execute(
    "SELECT unit_name, SUM(net_value) v FROM fact_sales_detail "
    "WHERE company_id = ? AND competence = ? GROUP BY unit_name",
    (company_id, competencia)).fetchall()}
for u in sorted(set(por_unidade) | set(det_unidade)):
    o, d = por_unidade.get(u, 0.0), det_unidade.get(u, 0.0)
    marca = "  <<< divergente" if o and abs(d - o) / o > 0.05 else ""
    print(f"   {u or '(sem unidade)':<16} oficial {money(o)}   detalhado {money(d)}{marca}")

# ── 3. Causas prováveis ──────────────────────────────────────────────────
print("\n3) CAUSAS PROVÁVEIS")

dupes = conn.execute(
    "SELECT COUNT(*) n FROM (SELECT row_hash, COUNT(*) c FROM fact_sales_detail "
    " WHERE company_id = ? AND competence = ? GROUP BY row_hash HAVING c > 1)",
    (company_id, competencia)).fetchone()["n"]
print(f"   Linhas com row_hash repetido no detalhado: {dupes}")
if dupes:
    print("   >> Reimportação do mesmo arquivo somou de novo. É a causa mais comum.")

imports = conn.execute(
    "SELECT COUNT(DISTINCT import_id) n FROM fact_sales_detail "
    "WHERE company_id = ? AND competence = ?", (company_id, competencia)).fetchone()["n"]
print(f"   Importações distintas alimentando esta competência: {imports}")
if imports > 1:
    print("   >> Mais de uma importação. Confira se o mesmo período entrou duas vezes:")
    for r in conn.execute(
        "SELECT d.import_id, i.imported_at, COUNT(*) linhas, SUM(d.net_value) v "
        "FROM fact_sales_detail d LEFT JOIN imports i ON i.id = d.import_id "
        "WHERE d.company_id = ? AND d.competence = ? GROUP BY d.import_id ORDER BY i.imported_at",
        (company_id, competencia)).fetchall():
        print(f"      import {r['import_id']:<5} {str(r['imported_at'])[:19]}  "
              f"{r['linhas']:>7} linha(s)  {money(r['v'])}")

sem_cliente = conn.execute(
    "SELECT COALESCE(SUM(net_value),0) v FROM fact_sales_detail "
    "WHERE company_id = ? AND competence = ? AND TRIM(COALESCE(client_name,'')) = ''",
    (company_id, competencia)).fetchone()["v"]
print(f"   Faturamento sem nome de cliente no detalhado: {money(sem_cliente)}")
print("   (fica fora das quebras por cliente, mas dentro do total)")

print("\nCOMO LER")
print("  O painel mostra as quebras como PROPORÇÃO do total oficial, então os")
print("  cartões sempre somam o total. Este script mostra a diferença real entre")
print("  as bases — que continua existindo e merece correção na origem.")
