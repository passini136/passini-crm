"""
Carrega a base fria de prospecção a partir do CSV enxuto.

Uso no servidor:
    /srv/passini/venv/crm/bin/python /srv/passini/apps/crm-comercial/carregar_leads.py \
        /srv/passini/apps/crm-comercial/leads_prospeccao.csv

Pode rodar de novo sempre que a base for atualizada: o CNPJ é único e a linha
existente é atualizada sem perder o que já aconteceu com ela — lead assumido
continua assumido, descartado continua descartado.
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

padrao = Path(__file__).with_name("leads_prospeccao.csv.gz")
arquivo = Path(sys.argv[1]) if len(sys.argv) > 1 else padrao
if not arquivo.exists():
    print(f"Arquivo não encontrado: {arquivo}")
    sys.exit(1)

conn = backend.get_connection()
company_id = conn.execute("SELECT id FROM companies LIMIT 1").fetchone()["id"]
print(f"Banco: {backend.DB_PATH}\nArquivo: {arquivo} ({arquivo.stat().st_size // 1024} KB)\n")

# Aceita .csv ou .csv.gz — o arquivo tem 20 MB e comprime para menos de 4 MB,
# o que faz diferença no git e no envio para o servidor.
if arquivo.suffix == ".gz":
    import gzip
    conteudo = gzip.decompress(arquivo.read_bytes())
else:
    conteudo = arquivo.read_bytes()

resultado = backend.import_prospect_leads(conn, company_id, conteudo)
print(resultado["message"])

resumo = backend.prospect_leads_summary(conn, company_id)
print("\nSITUAÇÃO DA BASE")
for situacao, quantidade in sorted(resumo.items()):
    print(f"  {situacao:<12} {quantidade}")

print("\nPOR SEGMENTO (disponíveis)")
for r in conn.execute(
    "SELECT segmento, COUNT(*) c FROM prospect_leads "
    "WHERE company_id = ? AND status = 'NOVO' GROUP BY segmento ORDER BY c DESC",
    (company_id,),
).fetchall():
    print(f"  {r['segmento']:<12} {r['c']}")

print("\nTOP CIDADES (disponíveis)")
for r in conn.execute(
    "SELECT cidade, COUNT(*) c FROM prospect_leads "
    "WHERE company_id = ? AND status = 'NOVO' GROUP BY cidade ORDER BY c DESC LIMIT 10",
    (company_id,),
).fetchall():
    print(f"  {r['cidade']:<22} {r['c']}")
