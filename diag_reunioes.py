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
print("(É normal a maioria ficar sem conta — só quem usa o CRM precisa de login.)")

# ── Problemas que exigem ação ────────────────────────────────────────────
print("\n\nO QUE PRECISA DE AJUSTE")
achou_problema = False

# 1. Conta sem vínculo cujo nome não casa com nenhuma pessoa do cadastro
nomes_pessoas = [p["person_name"] for p in pessoas]
unidade_por_pessoa = {p["person_name"]: (p["base_unit"] or "?") for p in pessoas}
for u in usuarios:
    if u["linked_person_name"] or u["username"] == "admin":
        continue
    # Candidato só quando TODAS as palavras do nome do usuário aparecem no nome
    # do cadastro. A regra anterior comparava só o começo do primeiro nome e
    # sugeria "ANDREI BRAGA" para "Andre Christ" — sugestão errada é pior que
    # nenhuma, porque leva a vincular a pessoa errada.
    palavras_usuario = [w for w in backend.person_key(u["full_name"]).split() if len(w) > 2]
    candidatos = []
    if palavras_usuario:
        for n in nomes_pessoas:
            alvo = backend.person_key(n).split()
            if all(w in alvo for w in palavras_usuario):
                candidatos.append(n)
    unicos = list(dict.fromkeys(candidatos))[:5]
    if unicos:
        achou_problema = True
        # Se já casa pelo nome completo, o vínculo é recomendado mas não urgente.
        ja_casa = backend.resolve_user_for_person(conn, company_id, unicos[0]) == u["id"]
        marca = " (já funciona pelo nome, vincular é só garantia)" if ja_casa else " — PRECISA VINCULAR"
        print(f"\n  Conta '{u['username']}' ({u['full_name']}) está SEM pessoa vinculada{marca}.")
        print("  Candidatos no cadastro:")
        for c in unicos:
            print(f"     - {c}  [{unidade_por_pessoa.get(c, '?')}]")

# 2. Duas contas apontando para a mesma pessoa
from collections import Counter as _Counter  # noqa: E402
duplicadas = _Counter(
    backend.person_key(u["linked_person_name"]) for u in usuarios if u["linked_person_name"]
)
for chave, quantas in duplicadas.items():
    if quantas > 1:
        achou_problema = True
        contas = [u["username"] for u in usuarios if backend.person_key(u["linked_person_name"]) == chave]
        print(f"\n  {quantas} contas vinculadas à MESMA pessoa ({chave}): {', '.join(contas)}")
        print("  O sistema se recusa a escolher e não notifica ninguém.")
        print("  Desative ou apague a conta que não é usada.")

if not achou_problema:
    print("  Nada a ajustar — todas as contas em uso estão vinculadas corretamente.")
else:
    print("\n  Onde corrigir: Usuários e Perfis -> editar a conta -> campo 'Pessoa vinculada'.")

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
