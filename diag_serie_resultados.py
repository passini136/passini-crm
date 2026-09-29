"""
A série do painel bate com o número oficial?

Uso:
    /srv/passini/venv/crm/bin/python /srv/passini/apps/crm-comercial/diag_serie_resultados.py
    /srv/passini/venv/crm/bin/python /srv/passini/apps/crm-comercial/diag_serie_resultados.py MATRIZ

Um painel de resultados que mostra número diferente do painel executivo é pior
que não ter painel: a reunião para de discutir o negócio e passa a discutir qual
tela está certa. Este diagnóstico compara, mês a mês, a série nova com a soma
direta do custo × venda.

Confere também o tempo: a série precisa sair em UMA consulta por indicador, não
uma por mês.

Não altera nada.
"""
import os
import sys
import time
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
unidade = " ".join(sys.argv[1:]).strip().upper()
nivel = "unidade" if unidade else "empresa"

print(f"Banco: {backend.DB_PATH}")
print(f"Nível: {nivel}{' · ' + unidade if unidade else ''}\n")

inicio = time.time()
serie = backend.resultados_serie(conn, company_id, nivel, unidade)
seg = time.time() - inicio
print(f"1) A SÉRIE SAIU EM {seg:.2f}s  ({len(serie)} competência(s))")
if seg > 2:
    print("   >> LENTO. Com poucos meses isso já pesa; confira se não virou")
    print("      uma consulta por mês.")
else:
    print("   >> Rápido. As consultas estão agrupadas por competência.")

print("\n2) A SÉRIE")
print(f"   {'MÊS':<9}{'LÍQUIDO':>14}{'META':>13}{'%':>7}{'DEV.COM':>12}{'GARANT':>11}"
      f"{'TICKET':>10}{'CLI':>6}")
for r in serie:
    pct = f"{r['attainmentPct']:.0f}%" if r["attainmentPct"] is not None else "—"
    print(f"   {r['competence']:<9}{backend.brl(r['revenueNet']):>14}"
          f"{backend.brl(r['revenueGoal']):>13}{pct:>7}"
          f"{backend.brl(r['returnsCommercial']):>12}"
          f"{backend.brl(r['returnsWarranty']):>11}"
          f"{backend.brl(r['ticketAverage']):>10}{r['clients']:>6}")

# ── 3. Bate com a fonte oficial? ────────────────────────────────────────────
# A série soma unidades; aqui a conferência vai direto na tabela, sem passar
# pela função. Se divergir, o painel nasceria com número próprio.
print("\n3) CONFERÊNCIA CONTRA O CUSTO × VENDA")
print(f"   {'MÊS':<9}{'SÉRIE':>15}{'TABELA':>15}{'DIFERENÇA':>14}")
problemas = 0
for r in serie:
    if unidade:
        row = conn.execute(
            "SELECT COALESCE(SUM(net_value),0) liq, COALESCE(SUM(return_value),0) dev "
            "FROM fact_unit_summary WHERE company_id = ? AND unit_name = ? AND competence = ?",
            (company_id, unidade, r["competence"])).fetchone()
    else:
        row = conn.execute(
            "SELECT COALESCE(SUM(net_value),0) liq, COALESCE(SUM(return_value),0) dev "
            "FROM fact_unit_summary WHERE company_id = ? AND competence = ?",
            (company_id, r["competence"])).fetchone()
    # A série soma a garantia de volta no líquido — para comparar, faz o mesmo.
    esperado = float(row["liq"] or 0) + r["returnsWarranty"]
    dif = r["revenueNet"] - esperado
    if abs(dif) > 1:
        problemas += 1
    print(f"   {r['competence']:<9}{backend.brl(r['revenueNet']):>15}"
          f"{backend.brl(esperado):>15}{backend.brl(dif):>14}"
          f"{'  ← DIVERGE' if abs(dif) > 1 else ''}")

print(f"\n   {problemas} mês(es) divergentes")
if problemas:
    print("   >> Corrigir ANTES de mostrar o painel numa reunião. Número que não")
    print("      bate faz a reunião discutir a tela em vez do negócio.")
else:
    print("   >> A série reproduz o oficial. Pode ir para a reunião.")

# ── 4. O histórico dá para comparar? ────────────────────────────────────────
print("\n4) O HISTÓRICO ALCANÇA O QUE A REUNIÃO PEDE?")
anos = sorted({r["competence"][:4] for r in serie})
print(f"   {len(serie)} competência(s), ano(s): {', '.join(anos)}")
if len(anos) < 2:
    print("   >> Só um ano na base. Dá para comparar mês contra mês e contra a")
    print("      média, mas NÃO ano contra ano. Importar 2025 destrava isso.")
else:
    print("   >> Dá para comparar o mesmo mês de anos diferentes.")

conn.close()
