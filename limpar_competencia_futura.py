"""
Remove dados importados com competência no FUTURO.

Uso:
    # 1. Ver o que seria removido (não apaga nada):
    /srv/passini/venv/crm/bin/python /srv/passini/apps/crm-comercial/limpar_competencia_futura.py

    # 2. Remover de verdade:
    /srv/passini/venv/crm/bin/python /srv/passini/apps/crm-comercial/limpar_competencia_futura.py --apagar

Em 22/09/2026 um consolidado por cliente entrou com competência 2029-09 (erro
de digitação). Como o c0 do CRM é o MAX(competence) dessa tabela, a média dos
três meses anteriores passou a somar meses vazios e zerou para a base inteira.

A remoção é SEMPRE por import_id, nunca por semelhança de dado. Apagar por
"parece errado" já custou vendas reais nesta base uma vez — a regra é remover
exatamente o que um import específico gravou, e nada além.

Roda em duas etapas de propósito: a primeira mostra, a segunda executa.
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

APAGAR = "--apagar" in sys.argv

conn = backend.get_connection()
company_id = conn.execute("SELECT id FROM companies LIMIT 1").fetchone()["id"]
limite = (backend.today_in_brazil().replace(day=1)
          + backend.timedelta(days=45)).strftime("%Y-%m")

print(f"Banco: {backend.DB_PATH}")
print(f"Competência máxima aceitável: {limite}")
print(f"Modo: {'APAGAR' if APAGAR else 'apenas mostrar'}\n")

# Tabelas com competência e import_id. Se aparecer competência futura em mais
# de uma, todas precisam sair — senão o c0 muda de lugar e o problema volta.
TABELAS = [
    ("crm_client_summary", "consolidado por cliente"),
    ("fact_sales_detail", "faturamento detalhado"),
    ("fact_vendor_summary", "custo x venda por vendedor"),
    ("fact_unit_summary", "custo x venda por unidade"),
]

total_geral = 0
for tabela, rotulo in TABELAS:
    try:
        linhas = conn.execute(
            f"SELECT competence, import_id, COUNT(*) n FROM {tabela} "
            f"WHERE company_id = ? AND competence > ? "
            f"GROUP BY competence, import_id ORDER BY competence",
            (company_id, limite)).fetchall()
    except Exception as erro:  # noqa: BLE001
        print(f"{tabela}: não consultada ({erro})")
        continue
    if not linhas:
        print(f"✓ {tabela:<24} nada no futuro")
        continue
    print(f"\n⚠ {tabela}  ({rotulo})")
    for r in linhas:
        total_geral += int(r["n"])
        imp = conn.execute(
            "SELECT i.competence, i.imported_at, "
            "       (SELECT GROUP_CONCAT(f.original_name, ', ') FROM import_files f "
            "        WHERE f.import_id = i.id) AS arquivos "
            "FROM imports i WHERE i.id = ?", (r["import_id"],)).fetchone()
        origem = (f"import #{r['import_id']} · {str(imp['imported_at'])[:16]} · "
                  f"{imp['arquivos'] or 'sem arquivo registrado'}"
                  ) if imp else f"import #{r['import_id']}"
        print(f"   {r['competence']}  {r['n']:>6} linha(s)  ·  {origem}")
        if APAGAR:
            # Por import_id E competência: o mesmo import pode ter gravado
            # meses corretos junto, e esses ficam.
            apagadas = conn.execute(
                f"DELETE FROM {tabela} WHERE company_id = ? AND import_id = ? "
                f"AND competence = ?",
                (company_id, r["import_id"], r["competence"])).rowcount
            print(f"      → {apagadas} linha(s) removida(s)")

if APAGAR and total_geral:
    conn.commit()
    backend.invalidate_crm_cache(company_id)
    print(f"\n{total_geral} linha(s) removida(s). Cache do CRM limpo.")
    print("Reinicie o serviço:  sudo systemctl restart passini-crm")
    print("Depois confira com:  /srv/passini/venv/crm/bin/python diag_media_cliente.py")
elif total_geral:
    print(f"\n{total_geral} linha(s) com competência futura.")
    print("Nada foi apagado. Para remover, rode de novo com --apagar")
else:
    print("\nNenhuma competência futura. Nada a fazer.")

conn.close()
