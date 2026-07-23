from __future__ import annotations

import importlib.util
import json
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
    project_root = Path(__file__).resolve().parents[1]
    backend = load_backend(project_root)
    with backend.get_connection() as conn:
        top_sellers = conn.execute(
            """
            SELECT seller_name, COUNT(1) AS total
            FROM crm_client_summary
            WHERE company_id = 1 AND competence = '2026-04'
            GROUP BY seller_name
            ORDER BY total DESC
            LIMIT 5
            """
        ).fetchall()
        print("TOP_SELLERS", [tuple(row) for row in top_sellers])

        user = conn.execute("SELECT * FROM users WHERE id = 1").fetchone()
        filters = {"seller_name": "TIAGO RODRIGUES (VENDAS)", "unit_name": None, "city_name": None}
        summary = backend.crm_summary_for_user(conn, 1, user, filters)
        clients = backend.list_crm_clients(conn, 1, filters, 20)
        agenda = {"top5": clients[:5], "extended": clients[5:20]}
        first = (agenda.get("top5") or agenda.get("extended") or [None])[0]
        detail = backend.get_crm_client_360(conn, 1, filters, first["clientKey"]) if first else None
        print("SUMMARY", json.dumps(summary, ensure_ascii=False))
        print("AGENDA_COUNTS", {"top5": len(agenda.get("top5") or []), "extended": len(agenda.get("extended") or [])})
        print("FIRST_CLIENT", json.dumps(first, ensure_ascii=False) if first else None)
        print("DETAIL_OK", bool(detail))
        if detail:
            print("DETAIL_CLIENT", detail.get("clientName"), detail.get("statusCode"), detail.get("classCode"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
