"""
O painel aponta FATO e CAUSA que servem para a reunião?

Uso:
    /srv/passini/venv/crm/bin/python /srv/passini/apps/crm-comercial/diag_fca.py
    /srv/passini/venv/crm/bin/python /srv/passini/apps/crm-comercial/diag_fca.py MATRIZ

Dois riscos opostos, e os dois estragam a reunião:
  - acusar DEMAIS: se todo indicador vira fato, o painel não prioriza nada e o
    gestor volta a decidir pelo faro;
  - acusar de MENOS: se nada aparece num mês que caiu 8%, ninguém confia.

E a causa precisa EXPLICAR. "Caiu" o gestor já sabia; o que ele não sabe é qual
vendedor, qual marca ou qual linha puxou.

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
alvo = " ".join(sys.argv[1:]).strip().upper()
nivel = "unidade" if alvo else "empresa"

serie = backend.resultados_serie(conn, company_id, nivel, alvo)
if len(serie) < 2:
    print("Série curta demais para comparar.")
    conn.close()
    raise SystemExit(0)

print(f"Banco: {backend.DB_PATH}")
print(f"Nível: {nivel}{' · ' + alvo if alvo else ''}\n")

# Roda para os 3 últimos meses: um mês só não diz se a régua é sensata.
print("1) A RÉGUA ACUSA NA MEDIDA CERTA?")
print(f"   {'MÊS':<10}{'FATOS':>7}{'PIORA':>7}{'MELHORA':>9}   PRINCIPAL")
for alvo_comp in [r["competence"] for r in serie][-3:]:
    d = backend.resultados_fatos(conn, company_id, serie, alvo_comp)
    f = d["facts"]
    piora = [x for x in f if x["worse"]]
    principal = (f"{piora[0]['label']} {piora[0]['variationPct']:+.0f}%"
                 if piora else "—")
    print(f"   {alvo_comp:<10}{len(f):>7}{len(piora):>7}{len(f) - len(piora):>9}   {principal}")
print("\n   >> Entre 2 e 6 fatos por mês é o ponto útil. Zero significa régua")
print("      frouxa demais; mais de 8 vira lista que ninguém lê.")

# ── 2. O mês corrente é tratado com justiça? ────────────────────────────────
ultimo = serie[-1]["competence"]
d = backend.resultados_fatos(conn, company_id, serie, ultimo)
print(f"\n2) FATOS DE {ultimo}")
if d["monthProgress"] < 0.999:
    print(f"   Mês em curso: {d['monthProgress'] * 100:.0f}% dos dias úteis.")
    print("   As referências de volume estão ajustadas a essa fatia.")
print(f"   Comparado com a média de {d['comparedWith']} mês(es) anteriores.\n")
if not d["facts"]:
    print("   Nenhum desvio relevante.")
for f in d["facts"]:
    seta = "▼" if f["worse"] else "▲"
    print(f"   {seta} {f['label']:<26}{f['variationPct']:+7.1f}%   "
          f"{f['value']:>12,.2f} contra {f['reference']:>12,.2f}")
    print(f"      referência: {f['referenceLabel']} · gravidade {f['severity']}")

# ── 3. A causa explica? ─────────────────────────────────────────────────────
# Este é o teste que decide se o painel vale a pena: se a decomposição não
# apontar nomes concretos, o gestor sai da reunião sem saber onde agir.
idx = [r["competence"] for r in serie].index(ultimo)
anterior = serie[idx - 1]["competence"] if idx > 0 else ""
print(f"\n3) CAUSA — o que mudou de {anterior} para {ultimo}")
causas = backend.resultados_causas(conn, company_id, nivel, alvo, ultimo, anterior)
for rotulo, itens in causas.items():
    piores = [i for i in itens if i["delta"] < 0][:5]
    if not piores:
        continue
    print(f"\n   POR {rotulo.upper()} — quem mais deixou de faturar:")
    for i in piores:
        var = f"{i['variationPct']:+.0f}%" if i["variationPct"] is not None else "novo"
        print(f"      {str(i['name'])[:34]:<36}{backend.brl(i['delta']):>14}  ({var})")

total_explicado = sum(
    abs(i["delta"]) for itens in causas.values() for i in itens if i["delta"] < 0)
print(f"\n   Soma das quedas apontadas: {backend.brl(total_explicado)}")
print("   >> Se nenhum nome aparecer acima, a causa não está explicando e o")
print("      painel não serve para a reunião.")

conn.close()
