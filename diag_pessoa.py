"""
Por que uma pessoa não aparece na lista de presentes da ata.

Uso no servidor:
    /srv/passini/venv/crm/bin/python /srv/passini/apps/crm-comercial/diag_pessoa.py RONI
    /srv/passini/venv/crm/bin/python /srv/passini/apps/crm-comercial/diag_pessoa.py RONI ADAILTON

A lista de presença sai de people_records e passa por quatro peneiras: existir
no cadastro, estar vigente na data, ter unidade que o usuário enxerga e não
colidir de chave com outra pessoa. Quando alguém some, é sempre uma delas — e
o script diz qual, em vez de deixar adivinhar.

Não altera nada.
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

procurados = [a.strip().upper() for a in sys.argv[1:] if a.strip() and not a.startswith("-")]
if not procurados:
    print("Informe ao menos um nome. Ex.: diag_pessoa.py RONI ADAILTON")
    raise SystemExit(1)

conn = backend.get_connection()
company_id = conn.execute("SELECT id FROM companies LIMIT 1").fetchone()["id"]
competencia = backend.crm_latest_competence(conn, company_id) or ""
inicio, fim = backend.competence_window(competencia) if competencia else ("", "")
hoje = backend.today_in_brazil().isoformat()
corte = max(fim, hoje) if fim else hoje

print(f"Banco: {backend.DB_PATH}")
print(f"Competência mais recente: {competencia or '—'}  ·  hoje: {hoje}")
print(f"Corte de admissão usado pela lista: {corte}")
print(f"Corte de desligamento usado pela lista: {inicio or '—'}\n")

# Mapa de chaves para detectar colisão: person_key apaga o que vem em
# parênteses, então "FULANO (VENDAS)" e "FULANO (TELEVENDAS)" viram a mesma
# pessoa — e a segunda linha é descartada em silêncio.
todas = conn.execute(
    "SELECT person_name, base_unit, role_classification, valid_from, valid_to "
    "FROM people_records WHERE company_id = ? ORDER BY person_name",
    (company_id,),
).fetchall()

por_chave: dict[str, list[str]] = {}
for r in todas:
    chave = backend.person_key(backend.normalize_whitespace(r["person_name"]))
    por_chave.setdefault(chave, []).append(backend.normalize_whitespace(r["person_name"]))

for procurado in procurados:
    print("═" * 78)
    print(f"  {procurado}")
    print("═" * 78)
    achados = [r for r in todas
               if procurado in backend.normalize_upper(r["person_name"])]
    if not achados:
        print("  >> NÃO EXISTE em people_records.")
        print("     A lista de presença só mostra quem está no cadastro de pessoas.")
        print("     Confira se o nome no relatório de pessoas está escrito diferente,")
        print("     e reimporte o cadastro de pessoas se a pessoa foi incluída depois.")
        # Talvez exista só como usuário de login, sem cadastro de pessoa.
        usuarios = conn.execute(
            "SELECT username, full_name, linked_person_name, linked_units_json, role, "
            "       COALESCE(is_active,1) ativo "
            "FROM users WHERE company_id = ? AND ("
            "     UPPER(COALESCE(username,'')) LIKE ?"
            "  OR UPPER(COALESCE(full_name,'')) LIKE ?"
            "  OR UPPER(COALESCE(linked_person_name,'')) LIKE ?)",
            (company_id, f"%{procurado}%", f"%{procurado}%", f"%{procurado}%"),
        ).fetchall()
        for u in usuarios:
            unidades = ", ".join(backend.normalize_unit_list(u["linked_units_json"])) or "(nenhuma)"
            print(f"     Existe como LOGIN: {u['username']} · {u['full_name'] or '(sem nome)'} "
                  f"· {u['role']} · {'ativo' if u['ativo'] else 'INATIVO'}")
            print(f"        vinculado a....: {u['linked_person_name'] or '(ninguém)'}")
            print(f"        unidades.......: {unidades}")
            print("        >> Entra na lista pela segunda fonte (contas ativas do CRM),")
            print("           desde que tenha nome vinculado ou nome completo preenchido.")
        if not usuarios:
            print("     Também não existe como login. Nome escrito de outro jeito?")
        print()
        continue

    for r in achados:
        nome = backend.normalize_whitespace(r["person_name"])
        chave = backend.person_key(nome)
        unidade = backend.normalize_unit(r["base_unit"])
        de = str(r["valid_from"] or "")
        ate = str(r["valid_to"] or "")
        print(f"\n  {nome}")
        print(f"     unidade....: {unidade or '(vazia)'}")
        print(f"     função.....: {backend.normalize_whitespace(r['role_classification']) or '(vazia)'}")
        print(f"     vigência...: {de or '(vazia)'} até {ate or 'em aberto'}")
        print(f"     chave......: {chave}")

        motivos = []
        if not de:
            motivos.append("sem data de admissão — a peneira de vigência descarta a linha")
        elif de > corte:
            motivos.append(f"admissão {de} é POSTERIOR ao corte {corte} — entra na lista só a partir dessa data")
        if ate and inicio and ate < inicio:
            motivos.append(f"desligamento {ate} é anterior a {inicio} — tratado como já desligado")
        homonimos = [n for n in por_chave.get(chave, []) if n != nome]
        if homonimos:
            motivos.append("COLISÃO de chave com " + ", ".join(homonimos)
                           + " — só a primeira em ordem alfabética aparece")
        if not unidade:
            motivos.append("sem unidade — invisível para gerente (diretoria continua vendo)")

        login = backend.resolve_user_for_person(conn, company_id, nome)
        print(f"     login......: {'sim (id ' + str(login) + ')' if login else 'NÃO — não recebe a pendência de ciência'}")

        if motivos:
            for m in motivos:
                print(f"     >> {m}")
        else:
            print("     >> Deveria aparecer para a diretoria. Se não aparece,")
            print("        o usuário que abriu a tela é gerente e não enxerga essa unidade.")
    print()

# ── Prova final: a lista que a tela realmente monta ──────────────────────────
print("═" * 78)
print("  LISTA REAL DE PRESENTES (como a tela monta, pelos olhos da diretoria)")
print("═" * 78)
gestor = conn.execute(
    "SELECT * FROM users WHERE company_id = ? AND COALESCE(is_active,1) = 1 "
    "ORDER BY CASE role WHEN 'Administrador' THEN 0 WHEN 'Diretor' THEN 1 ELSE 2 END LIMIT 1",
    (company_id,),
).fetchone()
if not gestor:
    print("  Nenhum usuário ativo para simular.")
else:
    lista = backend.list_meeting_people(conn, company_id, gestor)
    print(f"  Simulando como {gestor['username']} ({gestor['role']}) · {len(lista)} pessoa(s)\n")
    for procurado in procurados:
        achou = [p for p in lista if procurado in backend.normalize_upper(p["personName"])]
        if achou:
            for p in achou:
                print(f"  ✔ {p['personName']:<38}{p['unitName'] or '(sem unidade)':<16}"
                      f"{p['role']}{'' if p['hasLogin'] else '  (sem login)'}")
        else:
            print(f"  ✘ {procurado} continua fora da lista.")

conn.close()
