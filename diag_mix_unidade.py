"""
As unidades vendem coisas diferentes, ou só em tamanhos diferentes?

Uso:
    /srv/passini/venv/crm/bin/python /srv/passini/apps/crm-comercial/diag_mix_unidade.py
    /srv/passini/venv/crm/bin/python /srv/passini/apps/crm-comercial/diag_mix_unidade.py 2026-08

A pergunta veio de um contraste: Lajeado vende 23,1 peças por cliente a R$ 69 a
peça; Zona Norte vende 9,1 a R$ 102. Faturamento não distingue as duas causas
possíveis, e elas pedem ações opostas:

  MIX DE PRODUTO — Lajeado vende muito item barato (filtro, óleo, vela) e Zona
  Norte vende item caro (embreagem, amortecedor). Corrige-se com compra,
  treinamento e campanha.

  PERFIL DE CLIENTE — Lajeado atende oficina que compra sortido e Zona Norte
  atende quem busca a peça específica. Corrige-se com carteira e prospecção.

O teste: se as unidades tiverem as MESMAS marcas em proporções parecidas, a
diferença é de cliente. Se as proporções destoarem, é de mix.

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
comp = (sys.argv[1] if len(sys.argv) > 1
        else backend.crm_latest_competence(conn, company_id))

print(f"Banco: {backend.DB_PATH}")
print(f"Competência: {comp}\n")

t0 = time.time()
d = backend.resultados_mix_unidade(conn, company_id, comp)
seg = time.time() - t0
if not d.get("units"):
    print("Sem dados.")
    conn.close()
    raise SystemExit(0)

print(f"1) APURADO EM {seg:.2f}s · {len(d['units'])} unidade(s)")
# Conferência: a soma das unidades tem de reproduzir o faturamento detalhado.
cru = float(conn.execute(
    "SELECT COALESCE(SUM(net_value),0) v FROM fact_sales_detail "
    "WHERE company_id = ? AND competence = ? AND net_value > 0",
    (company_id, comp)).fetchone()["v"])
soma = sum(u["revenue"] for u in d["units"])
print(f"   Soma das unidades {backend.brl(soma)} contra detalhado {backend.brl(cru)}")
falta = cru - soma
if abs(falta) > max(1.0, cru * 0.02):
    print(f"   >> FALTAM {backend.brl(falta)} ({100 * falta / cru:.1f}%) — vendedor sem")
    print("      unidade resolvida na competência. Some do mix e aparece no total.")
else:
    print("   >> Cobertura completa.")

# ── 2. O retrato por unidade ────────────────────────────────────────────────
print("\n2) PERFIL DE VENDA POR UNIDADE")
print(f"   {'UNIDADE':<14}{'LÍQUIDO':>15}{'PEÇAS':>9}{'R$/PEÇA':>11}"
      f"{'MARCAS':>8}{'TOP5':>7}{'OUTRAS':>8}")
for u in d["units"]:
    print(f"   {u['unit'][:13]:<14}{backend.brl(u['revenue']):>15}{u['pieces']:>9,.0f}"
          f"{backend.brl(u['ticketPerPiece']):>11}{u['brandsCount']:>8}"
          f"{u['top5SharePct']:>6.0f}%{u['othersSharePct']:>7.0f}%")
print("\n   TOP5 alto = venda dependente de poucos fornecedores.")

# ── 3. Quem vende diferente da empresa ──────────────────────────────────────
# A participação sozinha reflete tamanho. O DESVIO contra a empresa é que
# aponta a unidade que vende outra coisa.
print("\n3) DESVIO DE MIX — pontos percentuais contra a média da empresa")
marcas = d["brands"][:8]
print(f"   {'UNIDADE':<14}" + "".join(f"{m[:9]:>11}" for m in marcas))
print(f"   {'EMPRESA':<14}" + "".join(
    f"{next((c['sharePct'] for c in d['company'] if c['brand'] == m), 0):>10.1f}%"
    for m in marcas))
print("   " + "-" * (14 + 11 * len(marcas)))
for u in d["units"]:
    cels = []
    for m in marcas:
        c = next((x for x in u["brands"] if x["brand"] == m), None)
        dp = c["deltaPp"] if c else 0.0
        marca_txt = f"{dp:+.1f}" if abs(dp) >= 1.0 else "·"
        cels.append(f"{marca_txt:>11}")
    print(f"   {u['unit'][:13]:<14}" + "".join(cels))
print("\n   Cada célula é a participação da unidade MENOS a da empresa.")
print("   '·' significa que a unidade vende aquela marca na mesma proporção.")

# ── 4. O veredito ───────────────────────────────────────────────────────────
print("\n4) É MIX OU É CLIENTE?")
desvios = []
for u in d["units"]:
    # Distância total do mix da unidade contra o da empresa: metade da soma dos
    # desvios absolutos é a fatia do faturamento que teria de mudar de marca
    # para a unidade ficar igual à empresa.
    dist = sum(abs(c["deltaPp"]) for c in u["brands"]) / 2
    desvios.append((u["unit"], dist, u["ticketPerPiece"], u["pieces"]))
desvios.sort(key=lambda x: x[1], reverse=True)
print(f"   {'UNIDADE':<14}{'DISTÂNCIA DO MIX':>18}{'R$/PEÇA':>11}")
for nome, dist, tk, _ in desvios:
    print(f"   {nome[:13]:<14}{dist:>17.1f}p{backend.brl(tk):>11}")

maior = desvios[0][1]
tickets = [x[2] or 0 for x in desvios]
faixa_tk = (max(tickets) / min(tickets)) if min(tickets) else 0
print(f"\n   Maior distância de mix: {maior:.1f} pontos")
print(f"   Ticket por peça varia {faixa_tk:.1f}x entre a maior e a menor unidade")
if maior >= 15:
    print("\n   >> MIX DIFERENTE. As unidades vendem produtos distintos, não apenas")
    print("      volumes distintos. A conversa é de compra, campanha e treinamento")
    print("      — e comparar ticket entre elas sem ajustar o mix é injusto.")
elif faixa_tk >= 1.3:
    print("\n   >> MESMO MIX, TICKET DIFERENTE. Vendem as mesmas marcas em proporção")
    print("      parecida, mas o valor por peça muda muito. Isso é perfil de")
    print("      CLIENTE ou política de desconto, não sortimento.")
else:
    print("\n   >> Unidades parecidas em mix e em ticket. A diferença de peças por")
    print("      cliente vem do tamanho do pedido, não do que se vende.")

# ── 5. As marcas que mais separam as unidades ───────────────────────────────
print("\n5) AS MARCAS QUE MAIS SEPARAM AS UNIDADES")
espalhamento = []
for m in d["brands"]:
    vals = [next((c["sharePct"] for c in u["brands"] if c["brand"] == m), 0)
            for u in d["units"]]
    espalhamento.append((m, max(vals) - min(vals), max(vals), min(vals)))
espalhamento.sort(key=lambda x: x[1], reverse=True)
print(f"   {'MARCA':<20}{'AMPLITUDE':>11}{'MAIOR':>9}{'MENOR':>9}")
for m, amp, mx, mn in espalhamento[:8]:
    print(f"   {m[:19]:<20}{amp:>10.1f}p{mx:>8.1f}%{mn:>8.1f}%")
print("\n   >> Amplitude grande numa marca significa que ela é forte numa unidade")
print("      e ausente noutra. Se for marca que a empresa quer empurrar, a lista")
print("      acima já é a pauta da reunião de compras.")

conn.close()
