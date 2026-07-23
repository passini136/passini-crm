from __future__ import annotations

import argparse
import importlib.util
from pathlib import Path


def load_backend(project_root: Path):
    backend_path = project_root / "backend.py"
    spec = importlib.util.spec_from_file_location("passini_backend", backend_path)
    if not spec or not spec.loader:
        raise RuntimeError(f"Não foi possível carregar {backend_path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def main() -> int:
    parser = argparse.ArgumentParser(description="Importa a carteira crua do CRM para o banco local do dashboard.")
    parser.add_argument("--competence", required=True, help="Competência no formato AAAA-MM.")
    parser.add_argument("--clients", required=True, help="CSV completo de cadastro de clientes.")
    parser.add_argument("--summary", required=True, help="CSV consolidado de faturamento por cliente.")
    parser.add_argument("--company-id", type=int, default=1)
    parser.add_argument("--user-id", type=int, default=1)
    args = parser.parse_args()

    project_root = Path(__file__).resolve().parents[1]
    backend = load_backend(project_root)
    backend.init_db()

    files = [
        {
            "fieldName": "crm_clients_file",
            "fileName": Path(args.clients).name,
            "content": Path(args.clients).read_bytes(),
        },
        {
            "fieldName": "crm_summary_file",
            "fileName": Path(args.summary).name,
            "content": Path(args.summary).read_bytes(),
        },
    ]

    preview = backend.preview_import_package(files, "crm")
    print("PREVIEW", preview["isValid"], preview["missingFileTypes"], preview["rowCounts"])
    if not preview["isValid"]:
        raise SystemExit("Importação CRM inválida.")

    with backend.get_connection() as conn:
        result = backend.import_package(
            conn,
            args.company_id,
            args.user_id,
            args.competence,
            "substituir",
            "crm",
            preview,
            files,
        )
        conn.commit()
        profiles_total = conn.execute(
            "SELECT COUNT(*) FROM crm_client_profiles WHERE company_id = ?",
            (args.company_id,),
        ).fetchone()[0]
        summary_total = conn.execute(
            "SELECT COUNT(*) FROM crm_client_summary WHERE company_id = ? AND competence = ?",
            (args.company_id, args.competence),
        ).fetchone()[0]

    print("RESULT", result)
    print("COUNTS", {"profiles": profiles_total, "summary": summary_total})
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
