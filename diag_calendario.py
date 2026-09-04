"""
Dias úteis, feriados e o que o sistema realmente conta.

Uso:
    /srv/passini/venv/crm/bin/python /srv/passini/apps/crm-comercial/diag_calendario.py
    /srv/passini/venv/crm/bin/python /srv/passini/apps/crm-comercial/diag_calendario.py 2026-09

Dia útil errado não parece erro: parece meta agressiva. O número entra na meta
diária, no ritmo esperado e na proporcional de férias, e ninguém desconfia dele.
Este script abre a conta — dia a dia — e mostra qual feriado o calendário
enxergou e qual ficou cadastrado sem efeito.

Não altera nada.
"""
import calendar as _cal
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

conn = backend.get_connection()
company_id = conn.execute("SELECT id FROM companies LIMIT 1").fetchone()["id"]
alvo = next((a for a in sys.argv[1:] if len(a) == 7 and a[4] == "-"), "")
competencia = backend.valid_competence(alvo) or \
    backend.crm_latest_competence(conn, company_id) or date.today().strftime("%Y-%m")

print(f"Banco: {backend.DB_PATH}")
print(f"Competência: {competencia}\n")

# ── 1. O que está gravado ────────────────────────────────────────────────────
print("1) FERIADOS GRAVADOS NO BANCO (todos os anos)")
linhas = conn.execute(
    "SELECT holiday_date, holiday_name, scope FROM holidays WHERE company_id = ? "
    "ORDER BY holiday_date", (company_id,)).fetchall()
invalidos = []
for r in linhas:
    d = str(r["holiday_date"] or "")
    ok = len(d) == 10 and d[4] == "-" and d[7] == "-"
    if not ok:
        invalidos.append(r)
print(f"   {len(linhas)} feriado(s) cadastrado(s)")
if invalidos:
    print(f"\n   >> {len(invalidos)} com a DATA EM FORMATO ERRADO. Estão na lista da tela")
    print("      mas o calendário nunca casa com eles — feriado cadastrado e sem efeito:")
    for r in invalidos:
        print(f"      {r['holiday_date']!r:<24}{r['holiday_name']}")
    print("      Corrija para 2026-09-07 (ano-mês-dia) e reimporte.")

# ── 2. O mês, dia a dia ──────────────────────────────────────────────────────
inicio, fim = backend.competence_window(competencia)
d0 = date.fromisoformat(inicio)
d1 = date.fromisoformat(fim)
feriados = {
    r["holiday_date"]: r["holiday_name"]
    for r in conn.execute(
        "SELECT holiday_date, holiday_name FROM holidays "
        "WHERE company_id = ? AND holiday_date BETWEEN ? AND ?",
        (company_id, inicio, fim)).fetchall()
}

print(f"\n2) {competencia} DIA A DIA")
SEMANA = ["seg", "ter", "qua", "qui", "sex", "SÁB", "DOM"]
uteis = 0
dia = d0
while dia <= d1:
    iso = dia.isoformat()
    fds = dia.weekday() >= 5
    feriado = feriados.get(iso)
    if fds:
        marca, motivo = " ", "fim de semana"
    elif feriado:
        marca, motivo = " ", f"FERIADO — {feriado}"
    else:
        marca, motivo = "•", ""
        uteis += 1
    print(f"   {marca} {dia.strftime('%d/%m')} {SEMANA[dia.weekday()]}  {motivo}")
    dia += timedelta(days=1)
print(f"\n   {uteis} dias úteis nesta conta")

# ── 3. O que o sistema devolve ───────────────────────────────────────────────
print("\n3) O QUE O SISTEMA CALCULA")
cal = backend.get_business_calendar(conn, company_id, competencia, include_current_day=False)
# Os nomes dos campos são conferidos contra o dicionário de verdade. Chutar
# nome de campo devolve None em silêncio, e None passa por "divergência" —
# o diagnóstico acusaria o sistema por um erro dele mesmo.
esperados = ["totalWorkingDays", "elapsedWorkingDays", "remainingWorkingDays",
             "referenceToday", "effectiveToday"]
faltando = [c for c in esperados if c not in cal]
if faltando:
    print(f"   ⚠ Campo(s) que este script esperava e não existem mais: {', '.join(faltando)}")
    print(f"     Campos disponíveis: {', '.join(sorted(cal))}")
for campo in esperados:
    if campo in cal:
        print(f"   {campo:<22}: {cal[campo]}")
print(f"   {'feriados vistos':<22}: {len(cal.get('holidays') or [])}")
for h in (cal.get("holidays") or []):
    print(f"      {h['date']}  {h['name']}")

print("\n4) LEITURA")
calculado = cal.get("totalWorkingDays")
if calculado != uteis:
    print(f"   >> DIVERGÊNCIA: a conta dia a dia dá {uteis}, o sistema devolve {calculado}.")
    print("      Quase sempre é cache: reinicie o serviço e rode de novo.")
else:
    total_dias = _cal.monthrange(d0.year, d0.month)[1]
    print(f"   Conferem: {uteis} dias úteis em {total_dias} dias de calendário.")
    if not feriados:
        print("   Nenhum feriado neste mês — confira se é isso mesmo.")

conn.close()
