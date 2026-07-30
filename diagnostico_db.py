"""
Diagnóstico do banco de dados Passini — rode com: python diagnostico_db.py
"""
import sqlite3, os, tempfile, traceback
from pathlib import Path

try:
    ROOT_DIR = Path(__file__).parent

    def resolve_data_dir():
        _env_data = os.environ.get("PASSINI_CRM_DATA")
        candidates = [
            Path(_env_data) if _env_data else None,
            Path(os.environ.get("LOCALAPPDATA", "")) / "PassiniDashboardV2" if os.environ.get("LOCALAPPDATA") else None,
            Path(tempfile.gettempdir()) / "PassiniDashboardV2",
            ROOT_DIR / "runtime_data",
        ]
        for c in candidates:
            if c and (c / "passini_dashboard.db").exists():
                return c
        return candidates[1] or candidates[2]

    DATA_DIR = resolve_data_dir()
    DB_PATH = DATA_DIR / "passini_dashboard.db"

    print(f"\n{'='*60}")
    print(f"Banco: {DB_PATH}")
    print(f"Existe: {DB_PATH.exists()}")
    if DB_PATH.exists():
        print(f"Tamanho: {DB_PATH.stat().st_size / 1024 / 1024:.2f} MB")
    print(f"{'='*60}\n")

    if not DB_PATH.exists():
        print("BANCO NAO ENCONTRADO nesse caminho!")
        _env_data = os.environ.get("PASSINI_CRM_DATA")
        candidates = [
            Path(_env_data) if _env_data else None,
            Path(os.environ.get("LOCALAPPDATA", "")) / "PassiniDashboardV2" if os.environ.get("LOCALAPPDATA") else None,
            Path(tempfile.gettempdir()) / "PassiniDashboardV2",
            ROOT_DIR / "runtime_data",
        ]
        print("Candidatos verificados:")
        for c in candidates:
            if c:
                db = c / "passini_dashboard.db"
                existe = db.exists()
                tamanho = f"{db.stat().st_size / 1024 / 1024:.2f} MB" if existe else "-"
                print(f"  {'OK' if existe else 'XX'} {db}  {tamanho}")
    else:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row

        companies = conn.execute("SELECT id, name FROM companies").fetchall()
        if not companies:
            print("Nenhuma empresa cadastrada.")
        else:
            for company in companies:
                cid = company["id"]
                print(f"Empresa: {company['name']} (id={cid})\n")

                queries = [
                    ("Faturamento detalhado (fact_sales_detail)",
                     f"SELECT competence, COUNT(DISTINCT client_name) AS clientes, COUNT(DISTINCT seller_name) AS vendedores, ROUND(SUM(net_value),2) AS total FROM fact_sales_detail WHERE company_id={cid} GROUP BY competence ORDER BY competence"),
                    ("Custo/venda vendedor (fact_vendor_summary)",
                     f"SELECT competence, COUNT(*) AS linhas, ROUND(SUM(sale_value),2) AS total FROM fact_vendor_summary WHERE company_id={cid} GROUP BY competence ORDER BY competence"),
                    ("Resumo unidades (fact_unit_summary)",
                     f"SELECT competence, COUNT(*) AS linhas FROM fact_unit_summary WHERE company_id={cid} GROUP BY competence ORDER BY competence"),
                    ("Cadastro CRM - clientes (crm_client_profiles)",
                     f"SELECT COUNT(*) AS total FROM crm_client_profiles WHERE company_id={cid}"),
                    ("Faturamento CRM consolidado (crm_client_summary)",
                     f"SELECT competence, COUNT(DISTINCT client_code) AS clientes, SUM(CASE WHEN net_value>0 THEN 1 ELSE 0 END) AS com_valor, ROUND(SUM(net_value),2) AS total FROM crm_client_summary WHERE company_id={cid} GROUP BY competence ORDER BY competence"),
                ]

                for label, sql in queries:
                    rows = conn.execute(sql).fetchall()
                    print(f"  [{label}]")
                    if not rows:
                        print("    (vazio)")
                    else:
                        for r in rows:
                            print("   ", dict(r))
                    print()

                print("  [Ultimos 15 imports]")
                for r in conn.execute(
                    """SELECT i.competence, i.import_action, i.imported_at,
                              GROUP_CONCAT(f.file_type, ', ') AS arquivos
                       FROM imports i
                       LEFT JOIN import_files f ON f.import_id = i.id
                       WHERE i.company_id=?
                       GROUP BY i.id
                       ORDER BY i.imported_at DESC LIMIT 15""",
                    (cid,)
                ).fetchall():
                    print(f"    {str(r['imported_at'])[:16]}  {str(r['import_action'] or ''):<25}  {str(r['competence'] or '-'):<8}  {r['arquivos'] or '-'}")

        conn.close()

    print(f"\n{'='*60}")

except Exception:
    print("\n\nERRO DURANTE DIAGNOSTICO:")
    traceback.print_exc()

input("\nPressione Enter para sair.")
