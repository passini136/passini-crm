"""
Mostra por que um presente da ata está (ou não) sendo ligado a uma conta do CRM.

Uso no servidor:
    /srv/passini/venv/crm/bin/python /srv/passini/apps/crm-comercial/diag_reunioes.py

Lista os usuários com os nomes que o sistema usa para casar, as pessoas do
cadastro e o resultado do casamento — sem alterar nada no banco.
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
print(f"Banco: {backend.DB_PATH}\n")

# ── Usuários ─────────────────────────────────────────────────────────────
print("USUÁRIOS DO CRM")
print(f"  {'login':<16}{'nome completo':<34}{'pessoa vinculada':<34}ativo")
print("  " + "-" * 92)
usuarios = conn.execute(
    "SELECT id, username, full_name, linked_person_name, is_active, role "
    "FROM users WHERE company_id = ? ORDER BY username",
    (company_id,),
).fetchall()
for u in usuarios:
    print(f"  {u['username'] or '':<16}{(u['full_name'] or '—'):<34}"
          f"{(u['linked_person_name'] or '— SEM VÍNCULO —'):<34}{u['is_active']}")

print("\n  Chaves de comparação por usuário:")
for u in usuarios:
    print(f"    {u['username']:<16} -> {backend.user_person_keys(u)}")

# ── Pessoas ativas e o casamento ─────────────────────────────────────────
print("\n\nPESSOAS DO CADASTRO x CONTA DE LOGIN")
competence = backend.crm_latest_competence(conn, company_id) or "2026-08"
comp_day = backend.first_day_of_competence(competence).isoformat()
pessoas = conn.execute(
    """
    SELECT DISTINCT person_name, base_unit, role_classification
    FROM people_records
    WHERE company_id = ?
      AND date(valid_from) <= date(?)
      AND (valid_to IS NULL OR valid_to = '' OR date(valid_to) >= date(?))
    ORDER BY person_name
    """,
    (company_id, comp_day, comp_day),
).fetchall()

por_login = {u["id"]: u["username"] for u in usuarios}
sem_login = []
for p in pessoas:
    nome = p["person_name"]
    uid = backend.resolve_user_for_person(conn, company_id, nome)
    marca = f"-> {por_login.get(uid)}" if uid else "SEM LOGIN"
    if not uid:
        sem_login.append(nome)
    print(f"  {nome:<40}{(p['base_unit'] or ''):<14}{marca}")
    print(f"      chave={backend.person_key(nome)!r}  curta={backend.short_person_key(nome)!r}")

print(f"\nResumo: {len(pessoas) - len(sem_login)} de {len(pessoas)} pessoas ligadas a uma conta.")
if sem_login:
    print("Sem conta (não recebem pendência de ciência):")
    for n in sem_login:
        print(f"  - {n}")
    print("\nPara resolver: em Usuários e Perfis, edite a conta da pessoa e preencha")
    print("'pessoa vinculada' com exatamente o nome que aparece acima.")

# ── Atas e presentes ─────────────────────────────────────────────────────
print("\n\nATAS REGISTRADAS")
for m in conn.execute(
    "SELECT id, title, status, occurred_at, unit_name FROM meetings WHERE company_id = ? "
    "ORDER BY id DESC LIMIT 10", (company_id,),
).fetchall():
    print(f"\n  #{m['id']} [{m['status']}] {m['title']} · {m['occurred_at']} · {m['unit_name'] or 'corporativa'}")
    if m["status"] != "PUBLICADA":
        print("      ⚠ RASCUNHO — ninguém é notificado enquanto não for publicada.")
    for p in conn.execute(
        "SELECT person_name, user_id, acknowledged_at FROM meeting_participants "
        "WHERE meeting_id = ? ORDER BY person_name", (m["id"],),
    ).fetchall():
        estado = "ciente" if p["acknowledged_at"] else "pendente"
        conta = por_login.get(p["user_id"], "SEM CONTA VINCULADA")
        print(f"      {p['person_name']:<40}{conta:<16}{estado}")
