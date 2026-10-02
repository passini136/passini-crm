"""
A sugestão de meta fecha com a meta da unidade?

Uso:
    /srv/passini/venv/crm/bin/python /srv/passini/apps/crm-comercial/diag_metas.py
    /srv/passini/venv/crm/bin/python /srv/passini/apps/crm-comercial/diag_metas.py 2026-10

A tela distribui a meta da unidade entre os vendedores. A propriedade que faz
ela valer a pena é UMA: a soma das sugestões tem de dar exatamente a meta da
unidade. Se sobrar ou faltar, o gerente refaz a conta na mão — que é o trabalho
que a tela veio tirar — e deixa de confiar no resto.

Três coisas que podem quebrar isso em silêncio:
  1. ARREDONDAMENTO. Centavo a centavo em dez vendedores vira diferença visível.
  2. VENDEDOR SEM HISTÓRICO. Entra com base zero; se recebesse fatia, a conta
     daria errado, e se for ignorado sem avisar, o gerente esquece de lançar
     a meta dele.
  3. FÉRIAS. Quem fica fora metade do mês carrega metade — e o que ele deixa
     precisa ir para os outros, não evaporar.

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

conn = backend.get_connection()
company_id = conn.execute("SELECT id FROM companies LIMIT 1").fetchone()["id"]
comp = (sys.argv[1] if len(sys.argv) > 1
        else backend.crm_latest_competence(conn, company_id))

print(f"Banco: {backend.DB_PATH}")
print(f"Competência: {comp}\n")

unidades = [r["unit_name"] for r in conn.execute(
    "SELECT DISTINCT unit_name FROM fact_unit_summary WHERE company_id = ? ORDER BY unit_name",
    (company_id,)).fetchall() if r["unit_name"]]

# ── 1. A soma fecha? ────────────────────────────────────────────────────────
print("1) A SOMA DAS SUGESTÕES FECHA COM A META DA UNIDADE?")
print(f"   {'UNIDADE':<14}{'META UNIDADE':>16}{'SOMA SUGERIDA':>16}{'DIFERENÇA':>13}{'VEND':>6}")
problemas = 0
dados = {}
for u in unidades:
    d = backend.sugerir_metas_unidade(conn, company_id, u, comp)
    if not d:
        continue
    dados[u] = d
    com = [r for r in d["rows"] if r["suggested"] is not None]
    soma = sum(r["suggested"] for r in com)
    dif = soma - d["unitGoal"]
    if d["unitGoal"] and abs(dif) > 0.01:
        problemas += 1
    print(f"   {u[:13]:<14}{backend.brl(d['unitGoal']):>16}{backend.brl(soma):>16}"
          f"{backend.brl(dif):>13}{len(com):>6}"
          f"{'  ← NÃO FECHA' if d['unitGoal'] and abs(dif) > 0.01 else ''}")
print(f"\n   {problemas} unidade(s) com soma divergente")
if problemas:
    print("   >> Corrigir ANTES de abrir a tela. Meta que não soma o combinado")
    print("      faz o gerente refazer a conta na mão e desconfiar do resto.")
else:
    print("   >> Todas fecham ao centavo.")

# ── 2. A sugestão é plausível? ──────────────────────────────────────────────
# Distribuição que pede o dobro de um e metade de outro não vai ser usada,
# por mais correta que a matemática seja.
print("\n2) A DISTRIBUIÇÃO É DEFENSÁVEL?")
for u, d in dados.items():
    if not d["unitGoal"]:
        continue
    com = [r for r in d["rows"] if r["suggested"] is not None]
    if not com:
        continue
    cresc = [r["growthPct"] for r in com if r["growthPct"] is not None]
    print(f"\n   {u} · meta {backend.brl(d['unitGoal'])} · "
          f"ritmo atual {backend.brl(d['baselineTotal'])}"
          + (f" · precisa crescer {d['unitGrowthPct']:+.1f}%"
             if d["unitGrowthPct"] is not None else ""))
    print(f"   {'VENDEDOR':<26}{'R$/DIA HOJE':>13}{'SUGERIDA':>14}{'R$/DIA META':>13}"
          f"{'CRESC':>8}{'FATIA':>7}")
    for r in com:
        obs = ""
        if r.get("onLeave"):
            obs = f"  férias {r['absentDays']}d"
            if r.get("coveredBy"):
                obs += f" → {r['coveredBy'][:14]}"
        if r.get("coversFor"):
            obs += f"  cobre {', '.join(x[:12] for x in r['coversFor'])}"
        cresc_txt = "—" if r["growthPct"] is None else f"{r['growthPct']:+.0f}%"
        print(f"   {backend.normalize_whitespace(r['seller'])[:25]:<26}"
              f"{backend.brl(r['dailyAverage']):>13}{backend.brl(r['suggested']):>14}"
              f"{backend.brl(r['dailyTarget']):>13}"
              f"{cresc_txt:>8}{r['sharePct']:>6.1f}%{obs}")
    if cresc:
        print(f"      crescimento pedido: de {min(cresc):+.0f}% a {max(cresc):+.0f}%")
        if max(cresc) - min(cresc) > 60:
            print("      >> AMPLITUDE ALTA. Alguém está recebendo muito mais que os")
            print("         outros em proporção — confira se não é distorção do")
            print("         potencial em cima de histórico curto.")
    if d["withoutHistory"]:
        print(f"      SEM HISTÓRICO (meta manual): {', '.join(d['withoutHistory'])}")

# ── 3. Férias estão sendo consideradas? ─────────────────────────────────────
print("\n3) FÉRIAS NA COMPETÊNCIA")
ferias = conn.execute(
    "SELECT person_name, start_date, end_date, "
    "       COALESCE(cover_person_name,'') cobre FROM vacations "
    "WHERE company_id = ? AND date(end_date) >= date(?) AND date(start_date) <= date(?)",
    (company_id, backend.first_day_of_competence(comp).isoformat(),
     backend.last_day_of_competence(comp).isoformat())).fetchall()
if not ferias:
    print("   Nenhuma férias cadastrada tocando esta competência.")
    print("   >> Se houver vendedor de férias e não estiver aqui, a meta dele sai")
    print("      cheia e a unidade fica com um alvo que ninguém vai cumprir.")
else:
    for f in ferias:
        print(f"   {backend.normalize_whitespace(f['person_name'])[:28]:<30}"
              f"{f['start_date'][:10]} a {f['end_date'][:10]}"
              + (f"  · cobertura: {f['cobre']}" if f["cobre"] else "  · sem substituto"))
    print("\n   Efeito na sugestão:")
    for u, d in dados.items():
        for r in d["rows"]:
            if r.get("onLeave"):
                print(f"   {u} · {backend.normalize_whitespace(r['seller'])[:24]:<26}"
                      f"{r['workingDays']} de {d['workingDays']} dias úteis"
                      f" · fatia {r['sharePct'] if r['sharePct'] is not None else 0:.1f}%")

# ── 4. O painel responde no escopo certo? ───────────────────────────────────
print("\n4) PAINEL DE METAS")
usuario = conn.execute(
    "SELECT * FROM users WHERE company_id = ? ORDER BY id LIMIT 1", (company_id,)).fetchone()
if usuario:
    p = backend.metas_painel(conn, company_id, usuario)
    print(f"   Usuário de teste: {usuario['name'] if 'name' in usuario.keys() else usuario['id']}")
    print(f"   {len(p['competences'])} competência(s) · {len(p['units'])} unidade(s)")
    print(f"   Pode editar meta de unidade: {p['canEditUnitGoal']}")
    print(f"\n   {'UNIDADE':<14}{'MÊS':<9}{'META UN':>14}{'SOMA VEND':>14}{'FALTA':>13}")
    for un in p["units"]:
        for c in p["competences"][-3:]:
            m = un["months"][c]
            if m["goal"] is None and not m["sellerGoalSum"]:
                continue
            print(f"   {un['unit'][:13]:<14}{c:<9}"
                  f"{(backend.brl(m['goal']) if m['goal'] is not None else '—'):>14}"
                  f"{backend.brl(m['sellerGoalSum']):>14}"
                  f"{(backend.brl(m['gap']) if m['gap'] is not None else '—'):>13}")
    print("\n   >> A coluna FALTA é o que o gerente precisa zerar. Positivo quer")
    print("      dizer que ainda há meta de unidade não distribuída.")

conn.close()
