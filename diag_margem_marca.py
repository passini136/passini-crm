"""
A margem por marca pode ir para a reunião?

Uso:
    /srv/passini/venv/crm/bin/python /srv/passini/apps/crm-comercial/diag_margem_marca.py
    /srv/passini/venv/crm/bin/python /srv/passini/apps/crm-comercial/diag_margem_marca.py 2026-08

Margem é o indicador mais perigoso do painel, por um motivo simples: ninguém
contesta margem alta. Faturamento errado alguém percebe, porque conhece o
número de cor. Margem de 38% numa marca que dá 22% passa batido, vira decisão
de compra, e o erro só aparece no resultado do trimestre.

Esta margem é ESTIMADA: custo do catálogo (custo de hoje) contra o faturamento
detalhado. A margem oficial da empresa continua vindo do custo × venda. Então a
pergunta não é "bate exatamente?" — não vai bater. É:

  1. O JOIN não duplica? Referência repetida do lado direito infla faturamento.
  2. Quanto do faturamento tem custo cadastrado? Sem cobertura, a margem
     descreve um pedaço e finge descrever a marca.
  3. O total estimado fica perto do oficial? Longe demais significa que o custo
     do catálogo não representa o custo real, e aí o número não serve nem para
     comparar marcas entre si.

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

# ── 1. O JOIN duplica linha de venda? ───────────────────────────────────────
# Teste direto: o faturamento com o JOIN tem de ser IGUAL ao faturamento sem
# ele. Sobra é duplicação — o estrago que já aconteceu na tela de linha.
print("1) O JOIN DO CATÁLOGO DUPLICA FATURAMENTO?")
backend.ensure_catalogo_custo_temp(conn, company_id)
cru = float(conn.execute(
    "SELECT COALESCE(SUM(net_value),0) v FROM fact_sales_detail "
    "WHERE company_id = ? AND competence = ? AND net_value > 0",
    (company_id, comp)).fetchone()["v"])
com_join = float(conn.execute(
    """SELECT COALESCE(SUM(f.net_value),0) v FROM fact_sales_detail f
       LEFT JOIN catalogo_custo c ON c.ref = UPPER(TRIM(f.sku_key))
                                 AND c.marca = UPPER(TRIM(COALESCE(f.brand_name,'')))
       WHERE f.company_id = ? AND f.competence = ? AND f.net_value > 0""",
    (company_id, comp)).fetchone()["v"])
dif = com_join - cru
print(f"   Sem JOIN {backend.brl(cru)}  ·  com JOIN {backend.brl(com_join)}  ·  "
      f"diferença {backend.brl(dif)}")
if abs(dif) > 1:
    print("   >> DUPLICOU. O catálogo não está agrupado por referência + marca.")
    print("      Parar aqui: toda margem calculada em cima disso está errada.")
    conn.close()
    raise SystemExit(1)
print("   >> Sem duplicação. O agrupamento por referência + marca está segurando.")

# ── 2. Quanto do faturamento tem custo? ─────────────────────────────────────
print("\n2) COBERTURA DE CUSTO")
t0 = time.time()
d = backend.resultados_margem_marca(conn, company_id, "empresa", "", comp, limite=200)
seg = time.time() - t0
print(f"   Apurado em {seg:.2f}s · {d['brandsTotal']} marca(s)")
print(f"   Cobertura geral: {d['coveragePct']}% do faturamento tem custo cadastrado")
if d["coveragePct"] is None or d["coveragePct"] < 60:
    print("   >> BAIXA. A margem descreveria menos de dois terços da venda.")
    print("      Vale mostrar a cobertura na tela e não a margem consolidada.")
elif d["coveragePct"] < 85:
    print("   >> PARCIAL. Serve para COMPARAR marcas entre si, não para dizer")
    print("      'a margem da empresa é X'. A oficial continua no custo × venda.")
else:
    print("   >> Boa. A estimativa representa a venda.")

# ── 3. A estimativa chega perto da margem oficial? ──────────────────────────
# Se o custo do catálogo estiver muito defasado, a margem estimada não serve
# nem para ranquear marca, porque o erro não é uniforme entre elas.
print("\n3) ESTIMADA CONTRA A MARGEM OFICIAL DO CUSTO x VENDA")
oficial = conn.execute(
    "SELECT AVG(margin_value) m FROM fact_unit_summary "
    "WHERE company_id = ? AND competence = ?", (company_id, comp)).fetchone()["m"]
com_custo = sum(b["revenue"] * b["coveragePct"] / 100 for b in d["brands"])
custo_tot = sum(b["cost"] for b in d["brands"])
estimada = (100 * (com_custo - custo_tot) / com_custo) if com_custo else None
print(f"   Oficial (custo × venda): {float(oficial or 0):.2f}%")
print(f"   Estimada (catálogo):     {estimada:.2f}%" if estimada is not None else "   Estimada: —")
if estimada is not None and oficial:
    gap = estimada - float(oficial)
    print(f"   Diferença: {gap:+.2f} pontos")
    if abs(gap) > 10:
        print("   >> MUITO LONGE. O custo do catálogo não representa o custo real.")
        print("      Não usar para decidir preço nem mix — no máximo para ver")
        print("      QUAL marca destoa, e mesmo assim com desconfiança.")
    elif abs(gap) > 4:
        print("   >> Deslocada, mas na mesma faixa. Serve para comparar marcas")
        print("      entre si; o valor absoluto continua sendo o oficial.")
    else:
        print("   >> Próxima. A estimativa é utilizável.")

# ── 4. O ranking por marca ──────────────────────────────────────────────────
print("\n4) MARGEM POR MARCA — as 15 maiores em faturamento")
print(f"   {'MARCA':<22}{'LÍQUIDO':>15}{'PEÇAS':>10}{'R$/PEÇA':>11}"
      f"{'MARGEM':>9}{'COBERT':>9}")
for b in d["brands"][:15]:
    mg = f"{b['marginPct']:.1f}%" if b["marginPct"] is not None else "—"
    print(f"   {b['brand'][:21]:<22}{backend.brl(b['revenue']):>15}"
          f"{b['pieces']:>10,.0f}{backend.brl(b['ticketPerPiece']):>11}"
          f"{mg:>9}{b['coveragePct']:>8.0f}%"
          f"{'' if b['reliable'] else '  ← pouca cobertura'}")

confiaveis = [b for b in d["brands"] if b["reliable"] and b["marginPct"] is not None]
if len(confiaveis) >= 4:
    confiaveis.sort(key=lambda b: b["marginPct"])
    print(f"\n   Menor margem: {confiaveis[0]['brand']} ({confiaveis[0]['marginPct']:.1f}%)")
    print(f"   Maior margem: {confiaveis[-1]['brand']} ({confiaveis[-1]['marginPct']:.1f}%)")
    faixa = confiaveis[-1]["marginPct"] - confiaveis[0]["marginPct"]
    print(f"   Amplitude entre marcas confiáveis: {faixa:.1f} pontos")
    if faixa < 5:
        print("   >> Marcas com margem parecida. O painel de margem por marca não")
        print("      vai gerar decisão — o ganho está em mix, não em troca de marca.")
    else:
        print("   >> Há diferença real entre marcas. Vale decisão de mix e compra.")

# ── 5. Peças e ticket por peça ──────────────────────────────────────────────
print("\n5) PEÇAS VENDIDAS E TICKET POR PEÇA (fonte oficial)")
p = backend.resultados_produtividade(conn, company_id, "empresa", "", comp)
print(f"   {p['pieces']:,.0f} peça(s) · {p['piecesPerDay']:,.1f} por dia útil")
print(f"   Ticket por peça: {backend.brl(p['ticketPerPiece'])}")
print(f"   Peças por cliente: {p['piecesPerClient']}")
# Conferência: o ticket por peça x peças tem de reconstruir o líquido.
recomposto = (p["ticketPerPiece"] or 0) * p["pieces"]
print(f"   Conferência: {backend.brl(recomposto)} contra {backend.brl(p['revenueNet'])}")
if abs(recomposto - p["revenueNet"]) > max(1.0, p["revenueNet"] * 0.001):
    print("   >> NÃO FECHA. Peças e líquido vêm de fontes diferentes.")
else:
    print("   >> Fecha. Peças e faturamento saem da mesma fonte.")

print("\n6) POR UNIDADE")
print(f"   {'UNIDADE':<14}{'PEÇAS':>10}{'R$/PEÇA':>12}{'PÇ/CLIENTE':>12}{'COBERT.CUSTO':>14}")
for r in conn.execute(
    "SELECT DISTINCT unit_name FROM fact_unit_summary WHERE company_id = ? "
    "AND competence = ? ORDER BY unit_name", (company_id, comp)).fetchall():
    u = r["unit_name"]
    if not u:
        continue
    pu = backend.resultados_produtividade(conn, company_id, "unidade", u, comp)
    mu = backend.resultados_margem_marca(conn, company_id, "unidade", u, comp, limite=200)
    print(f"   {u[:13]:<14}{pu['pieces']:>10,.0f}"
          f"{backend.brl(pu['ticketPerPiece']):>12}{pu['piecesPerClient']:>12}"
          f"{(mu.get('coveragePct') or 0):>13.0f}%")

conn.close()
