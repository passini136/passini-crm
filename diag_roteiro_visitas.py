"""
Por que o roteiro de visitas não trouxe a carteira do vendedor?

Uso (venv do CRM):
    /srv/passini/venv/crm/bin/python /srv/passini/apps/crm-comercial/diag_roteiro_visitas.py HEIDER

POR QUE ESTE DIAGNÓSTICO EXISTE

A tela do roteiro abriu e veio vazia. Vazio tem seis causas possíveis, e
todas se parecem na tela: escopo do usuário, cliente sem vendedor, filtro de
cidade, falta de ligação registrada, standby de 60 dias e nenhuma categoria
aplicável. Olhar o resultado não distingue uma da outra.

Este script refaz o caminho de suggest_visits passo a passo e conta quantos
clientes MORREM em cada filtro. O passo que zera é a resposta.

A primeira suspeita é minha: acabei de acrescentar a trava "cliente sem
vendedor não vira sugestão". A Zona Norte está em implantação e a carteira
de lá ainda está sendo montada — se os clientes não têm dono atribuído, eu
mesmo esvaziei o roteiro ontem. O diagnóstico confirma ou derruba isso.

NÃO ALTERA NADA.
"""
import os
import sys
from datetime import date, timedelta
from pathlib import Path

sys.path.insert(0, "/srv/passini/apps/crm-comercial")

if not os.environ.get("PASSINI_CRM_DATA"):
    for candidate in ("/srv/passini/data/crm", "/srv/passini/data"):
        if (Path(candidate) / "passini_dashboard.db").exists():
            os.environ["PASSINI_CRM_DATA"] = candidate
            break

import backend  # noqa: E402

procurado = (sys.argv[1] if len(sys.argv) > 1 else "HEIDER").upper()

conn = backend.get_connection()
company_id = conn.execute("SELECT id FROM companies LIMIT 1").fetchone()["id"]
print(f"Banco: {backend.DB_PATH}\n")

# ── 1. O usuário ────────────────────────────────────────────────────────────
print(f"1) USUÁRIO QUE CONTÉM '{procurado}'")
usuarios = [r for r in conn.execute(
    "SELECT * FROM users WHERE company_id = ?", (company_id,))
    if procurado in (backend.normalize_whitespace(
        f"{r['username']} {r['full_name']} {r['linked_person_name']}").upper())]
if not usuarios:
    print("   Nenhum usuário com esse nome. Passe parte do login ou do nome.")
    sys.exit(1)
for u in usuarios:
    escopo = backend.data_scope_for_user(conn, u)
    print(f"   login={u['username']}  papel={u['role']}  escopo={escopo}")
    print(f"   vinculado a: {u['linked_person_name'] or '— NÃO VINCULADO —'}")
    print(f"   unidades: {u['linked_units_json'] or '— nenhuma —'}")
    print(f"   identidade usada nas consultas: "
          f"{backend.seller_identity_for_user(u)!r}")
user = usuarios[0]
escopo = backend.data_scope_for_user(conn, user)
if not backend.normalize_whitespace(user["linked_person_name"]):
    print("\n   >> SEM PESSOA VINCULADA. O escopo 'proprio' filtra pelo nome do")
    print("      login, que não casa com o do faturamento — a carteira sai vazia")
    print("      sem erro nenhum.")

# ── 2. O recorte que a tela aplica ──────────────────────────────────────────
print("\n2) RECORTE DE PERMISSÃO")
competence = backend.crm_latest_competence(conn, company_id) or date.today().strftime("%Y-%m")
filtros = backend.build_filters_from_query({})
filtros["competence_start"] = competence
filtros["competence_end"] = competence
filtros = backend.crm_scoped_filters_for_user(conn, company_id, user, filtros)
print(f"   competência={competence}")
for k in ("unit_name", "seller_name", "allowed_units"):
    print(f"   {k} = {filtros.get(k)!r}")

clientes = backend.list_crm_clients(conn, company_id, filtros, attach_context=False)
print(f"\n   Clientes no recorte: {len(clientes):,}")
if not clientes:
    print("   >> ZERO AQUI. O problema é anterior ao roteiro: é o recorte de")
    print("      permissão ou a competência. O roteiro não tem o que filtrar.")
    # Sem recorte, para comparar
    livre = backend.list_crm_clients(
        conn, company_id, {"competence_start": competence,
                           "competence_end": competence}, attach_context=False)
    print(f"      (sem recorte nenhum a base tem {len(livre):,} cliente(s))")
    por_unidade = {}
    for c in livre:
        u = backend.normalize_unit(c.get("unitName"))
        por_unidade[u] = por_unidade.get(u, 0) + 1
    for u, n in sorted(por_unidade.items(), key=lambda x: -x[1]):
        print(f"      {u[:16]:<18}{n:>7,}")
    conn.close()
    sys.exit(0)

# ── 3. Onde cada cliente morre ──────────────────────────────────────────────
print("\n3) ONDE OS CLIENTES SE PERDEM, FILTRO A FILTRO")
hoje = backend.today_in_brazil()

limite_ligacao = (hoje - timedelta(days=backend.VISIT_CALL_WINDOW_DAYS)).isoformat()
com_ligacao = {
    backend.normalize_client_key(r["client_key"])
    for r in conn.execute(
        "SELECT DISTINCT client_key FROM crm_interactions"
        " WHERE company_id = ? AND contact_type_code = 'LIGACAO'"
        "   AND initiative = 'ATIVO'"
        "   AND date(substr(replace(occurred_at,'T',' '),1,10)) >= date(?)",
        (company_id, limite_ligacao))}

visitados = {
    backend.normalize_client_key(r["client_key"]): r["ultima"]
    for r in conn.execute(
        "SELECT client_key, MAX(date(occurred_at)) ultima FROM visits"
        " WHERE company_id = ? AND status = 'REALIZADA' GROUP BY client_key",
        (company_id,))}

ajustes = {
    backend.normalize_client_key(r["client_key"]): r["action"]
    for r in conn.execute(
        "SELECT client_key, action FROM visit_route_overrides"
        " WHERE company_id = ?", (company_id,))}

pedidos = {
    backend.normalize_client_key(r["client_key"])
    for r in conn.execute(
        "SELECT client_key FROM visit_requests"
        " WHERE company_id = ? AND status = 'PENDENTE'", (company_id,))}

perdas = {"tirado pelo gestor": 0, "SEM VENDEDOR": 0, "standby de visita": 0,
          "sem ligação na janela": 0, "nenhuma categoria": 0, "SOBROU": 0}
exemplos: dict[str, list[str]] = {k: [] for k in perdas}

for c in clientes:
    chave = backend.normalize_client_key(c["clientKey"])
    nome = backend.normalize_whitespace(c.get("clientName"))[:28]
    acao = ajustes.get(chave, "")
    incluido = acao == "DENTRO"

    def cai(motivo):
        perdas[motivo] += 1
        if len(exemplos[motivo]) < 3:
            exemplos[motivo].append(nome)

    if acao == "FORA":
        cai("tirado pelo gestor"); continue
    if not backend.normalize_whitespace(c.get("assignedSeller")) and not incluido:
        cai("SEM VENDEDOR"); continue

    dias_visita = None
    ultima = visitados.get(chave)
    if ultima:
        d = backend.parse_datetime_flexible(ultima)
        dias_visita = (hoje - d.date()).days if d else None
        if (dias_visita is not None
                and dias_visita < backend.VISIT_COOLDOWN_DAYS and not incluido):
            cai("standby de visita"); continue

    if chave in pedidos or incluido:
        cai("SOBROU"); continue
    if chave not in com_ligacao:
        cai("sem ligação na janela"); continue

    status = backend.normalize_upper(c.get("statusCode"))
    queda = float(c.get("dropPct") or 0.0)
    media = float(c.get("averageRevenue") or 0.0)
    atual = float(c.get("currentRevenue") or 0.0)
    if status in ("INATIVO", "PRE_INATIVO") or queda <= -0.30 or (atual <= 0 and media > 0):
        cai("SOBROU")
    elif media > 0 and (dias_visita is None
                        or dias_visita >= backend.VISIT_RELATIONSHIP_DAYS):
        cai("SOBROU")
    else:
        cai("nenhuma categoria")

print(f"   {'FILTRO':<24}{'CLIENTES':>10}  EXEMPLOS")
for motivo, n in perdas.items():
    if not n and motivo != "SOBROU":
        continue
    print(f"   {motivo:<24}{n:>10,}  {', '.join(exemplos[motivo])}")

print(f"\n   >> O filtro que leva quase todos é a causa. 'SOBROU' é o que a")
print("      tela deveria mostrar.")
if perdas["SEM VENDEDOR"] and perdas["SOBROU"] == 0:
    print("\n   >> FOI A TRAVA DE 'SEM VENDEDOR'. A unidade tem clientes, mas")
    print("      nenhum com dono atribuído — carteira ainda não distribuída.")
    print("      A regra está correta e o dado é que não está pronto.")

# ── 4. A carteira dessa unidade tem dono? ───────────────────────────────────
print("\n4) QUANTOS CLIENTES DA UNIDADE TÊM VENDEDOR ATRIBUÍDO")
print(f"   {'UNIDADE':<16}{'CLIENTES':>10}{'COM DONO':>10}{'SEM DONO':>10}")
por_unidade: dict[str, list[int]] = {}
todos = backend.list_crm_clients(
    conn, company_id,
    {"competence_start": competence, "competence_end": competence},
    attach_context=False)
for c in todos:
    u = backend.normalize_unit(c.get("unitName")) or "(sem unidade)"
    par = por_unidade.setdefault(u, [0, 0])
    par[0] += 1
    if backend.normalize_whitespace(c.get("assignedSeller")):
        par[1] += 1
for u, (total, com) in sorted(por_unidade.items(), key=lambda x: -x[1][0]):
    marca = "  ← CARTEIRA SEM DONO" if total and com == 0 else ""
    print(f"   {u[:15]:<16}{total:>10,}{com:>10,}{total - com:>10,}{marca}")

# ── 5. O vendedor existe no faturamento daquela unidade? ────────────────────
print("\n5) O NOME DO VENDEDOR APARECE NA CARTEIRA?")
alvo = backend.person_key(backend.seller_identity_for_user(user))
donos: dict[str, int] = {}
for c in todos:
    d = backend.normalize_whitespace(c.get("assignedSeller"))
    if d:
        donos[d] = donos.get(d, 0) + 1
casam = [d for d in donos if backend.person_key(d) == alvo]
print(f"   identidade do login: {backend.seller_identity_for_user(user)!r}")
print(f"   casa com {len(casam)} dono(s) de carteira: {casam[:3]}")
if not casam:
    print("   >> O NOME DO LOGIN NÃO É DONO DE NENHUM CLIENTE. Com escopo")
    print("      'proprio' isso devolve carteira vazia sem erro. Donos")
    print("      parecidos no cadastro:")
    curto = backend.short_person_key(backend.seller_identity_for_user(user))
    for d in sorted(donos):
        if backend.short_person_key(d) == curto or backend.person_key(d).startswith(
                alvo.split(" ")[0]):
            print(f"      · {d}  ({donos[d]} cliente(s))")

conn.close()
print("\nNada foi alterado.")
