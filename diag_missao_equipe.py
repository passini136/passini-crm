"""
Quem aparece no painel gerencial da Missão do Dia — e quem deveria aparecer.

Uso:
    /srv/passini/venv/crm/bin/python /srv/passini/apps/crm-comercial/diag_missao_equipe.py

A lista de vendedores do painel vinha só de goals_seller: sem meta, o vendedor
não existia para a tela. Agora entra também quem é vendedor ativo numa unidade
marcada como IMPLANTAÇÃO. Isso depende de duas coisas estarem certas no
cadastro, e é o que este script confere:

  1. a unidade estar com fase IMPLANTACAO em unit_phases;
  2. a pessoa estar em people_records, vigente, classificada como Vendedor.

Faltando qualquer uma, o vendedor continua invisível — e a tela não tem como
avisar, porque para ela a pessoa simplesmente não existe.

Não altera nada.
"""
import os
import sys
from datetime import date
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
competencia = date.today().strftime("%Y-%m")
print(f"Banco: {backend.DB_PATH}")
print(f"Competência do painel: {competencia}  ·  hoje: {date.today().isoformat()}\n")

# ── 1. Fase das unidades ─────────────────────────────────────────────────────
print("1) FASE DAS UNIDADES (unit_phases)")
fases = backend.list_unit_phases(conn, company_id)
if not fases:
    print("   >> NENHUMA unidade cadastrada em unit_phases.")
    print("      Sem isso não existe 'unidade em implantação', e nenhum vendedor")
    print("      sem meta vai aparecer. Cadastre em Administração → Unidades.")
else:
    for f in fases:
        marca = "  << implantação" if f["isDeployment"] else ""
        print(f"   {f['unitName']:<16}{f['phase']:<14}"
              f"isento até {f['goalExemptUntil'] or '—'}{marca}")
implantacao = {f["unitName"] for f in fases if f["isDeployment"]}
if not implantacao:
    print("\n   >> Nenhuma unidade em IMPLANTACAO. A regra nova não vai pegar ninguém.")

# ── 2. Quem tem meta no mês ──────────────────────────────────────────────────
print("\n2) VENDEDORES COM META EM " + competencia)
com_meta = conn.execute(
    "SELECT seller_name, MAX(base_unit) u FROM goals_seller "
    "WHERE company_id = ? AND competence = ? GROUP BY seller_name ORDER BY seller_name",
    (company_id, competencia)).fetchall()
por_unidade: dict[str, int] = {}
for r in com_meta:
    u = backend.normalize_unit(r["u"]) or "(sem unidade)"
    por_unidade[u] = por_unidade.get(u, 0) + 1
print(f"   {len(com_meta)} vendedor(es) com meta · " +
      " · ".join(f"{u}: {n}" for u, n in sorted(por_unidade.items())))

# ── 3. Quem entra pela regra nova ────────────────────────────────────────────
print("\n3) VENDEDORES SEM META QUE A REGRA NOVA TRAZ")
if not implantacao:
    print("   (nenhuma unidade em implantação — nada a trazer)")
else:
    ja = {backend.person_key(backend.normalize_whitespace(r["seller_name"])) for r in com_meta}
    trazidos = []
    for r in conn.execute(
        "SELECT person_name, base_unit, role_classification, valid_from, valid_to "
        "FROM people_records WHERE company_id = ? AND date(valid_from) <= date(?) "
        "  AND (valid_to IS NULL OR valid_to = '' OR date(valid_to) >= date(?)) "
        "ORDER BY person_name",
        (company_id, date.today().isoformat(),
         backend.first_day_of_competence(competencia).isoformat())).fetchall():
        nome = backend.normalize_whitespace(r["person_name"])
        unidade = backend.normalize_unit(r["base_unit"])
        if unidade not in implantacao:
            continue
        papel = backend.normalize_whitespace(r["role_classification"]) or "(vazio)"
        eh_vendedor = "VENDEDOR" in backend.normalize_upper(papel)
        ja_tinha = backend.person_key(nome) in ja
        if eh_vendedor and not ja_tinha:
            trazidos.append((nome, unidade, papel))
        else:
            motivo = "já tem meta" if ja_tinha else f"função é '{papel}', não Vendedor"
            print(f"   ✘ {nome[:34]:<36}{unidade[:12]:<14}{motivo}")
    for nome, unidade, papel in trazidos:
        print(f"   ✔ {nome[:34]:<36}{unidade[:12]:<14}{papel}")
    print(f"\n   {len(trazidos)} vendedor(es) passam a aparecer no painel.")
    if not trazidos:
        print("   >> Nenhum. Confira se as pessoas da unidade estão em people_records")
        print("      com função 'Vendedor' e vigência aberta (Administração → Pessoas).")

# ── 4. O painel, como a diretoria vê ─────────────────────────────────────────
print("\n4) O PAINEL COMO A DIRETORIA VÊ")
diretor = conn.execute(
    "SELECT * FROM users WHERE company_id = ? AND COALESCE(is_active,1)=1 "
    "ORDER BY CASE role WHEN 'Diretor' THEN 0 WHEN 'Administrador' THEN 1 ELSE 2 END LIMIT 1",
    (company_id,)).fetchone()
if not diretor:
    print("   Nenhum usuário para simular.")
else:
    dados = backend.compute_team_activity_today(conn, company_id, diretor)
    print(f"   {len(dados['sellers'])} vendedor(es) no painel · "
          f"{dados['totalContactsToday']} ligação(ões) hoje · meta do time {dados['teamGoal']}")
    print(f"\n   {'VENDEDOR':<34}{'UNIDADE':<14}{'HOJE':>6}{'ATRASADAS':>11}  MARCA")
    for s in dados["sellers"]:
        marca = "IMPLANTAÇÃO" if (s.get("inDeployment") and not s.get("hasRevenueGoal")) else ""
        print(f"   {s['sellerName'][:33]:<34}{(s['unit'] or '—')[:13]:<14}"
              f"{s['contactsToday']:>6}{s['overdueTasks']:>11}  {marca}")

conn.close()
