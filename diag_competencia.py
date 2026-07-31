"""
Diagnostica travamento do dashboard em uma competência específica.

Uso no servidor:
    /srv/passini/venv/crm/bin/python /srv/passini/apps/crm-comercial/diag_competencia.py 2026-06

Se travar, após 25s imprime o stack trace mostrando a linha exata onde está parado.
"""
import sys, time, faulthandler

sys.path.insert(0, "/srv/passini/apps/crm-comercial")

competence = sys.argv[1] if len(sys.argv) > 1 else "2026-06"

import backend  # noqa: E402

print(f"Banco: {backend.DB_PATH}")
print(f"Competência testada: {competence}\n")

conn = backend.get_connection()
company_id = conn.execute("SELECT id FROM companies LIMIT 1").fetchone()["id"]

# Contagens da competência
for label, sql in [
    ("fact_sales_detail",   "SELECT COUNT(*) n FROM fact_sales_detail WHERE company_id=? AND competence=?"),
    ("fact_vendor_summary", "SELECT COUNT(*) n FROM fact_vendor_summary WHERE company_id=? AND competence=?"),
    ("fact_unit_summary",   "SELECT COUNT(*) n FROM fact_unit_summary WHERE company_id=? AND competence=?"),
    ("goals_seller",        "SELECT COUNT(*) n FROM goals_seller WHERE company_id=? AND competence=?"),
    ("goals_unit",          "SELECT COUNT(*) n FROM goals_unit WHERE company_id=? AND competence=?"),
    ("crm_client_summary",  "SELECT COUNT(*) n FROM crm_client_summary WHERE company_id=? AND competence=?"),
]:
    n = conn.execute(sql, (company_id, competence)).fetchone()["n"]
    print(f"  {label:22} {n}")

print("\nChamando get_dashboard_data... (stack trace automático se passar de 25s)\n")
faulthandler.dump_traceback_later(25, exit=True)

filters = backend.build_filters_from_query({})
filters["competence_start"] = competence
filters["competence_end"] = competence

started = time.time()
data = backend.get_dashboard_data(conn, company_id, filters)
elapsed = time.time() - started
faulthandler.cancel_dump_traceback_later()

print(f"CONCLUIDO em {elapsed:.1f}s")
print(f"  vendedores no retorno: {len(data.get('sellers', []))}")
print(f"  clientes no ranking:   {len(data.get('clientRanking', []))}")
print(f"  cidades no ranking:    {len(data.get('cityRanking', []))}")

import json  # noqa: E402
payload = json.dumps(data, default=str)
print(f"  tamanho do JSON:       {len(payload)/1024/1024:.2f} MB")
