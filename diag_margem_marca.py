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
# `margin_value` é MULTIPLICADOR, não percentual — a régua do farol trata 1,55
# como bom. Comparar 1,52 com "35%" e concluir que o catálogo está errado foi
# exatamente o erro que este bloco cometeu na primeira versão. A margem oficial
# comparável sai de LUCRO ÷ VENDA, que existe no próprio arquivo.
of = conn.execute(
    "SELECT COALESCE(SUM(profit_value),0) lucro, COALESCE(SUM(sale_value),0) venda, "
    "       COALESCE(SUM(cost_value),0) custo, AVG(margin_value) mult "
    "FROM fact_vendor_summary WHERE company_id = ? AND competence = ?",
    (company_id, comp)).fetchone()
venda_of = float(of["venda"] or 0)
oficial = (100 * float(of["lucro"] or 0) / venda_of) if venda_of else None
mult = float(of["mult"] or 0)
print(f"   Multiplicador médio do Alfa: {mult:.3f}x  "
      f"(equivale a {100 * (1 - 1 / mult):.1f}% de margem)" if mult > 1 else "")
print(f"   Oficial (lucro ÷ venda): {oficial:.2f}%" if oficial is not None else "   Oficial: —")

com_custo = sum(b["revenue"] * b["coveragePct"] / 100 for b in d["brands"])
custo_tot = sum(b["cost"] for b in d["brands"])
estimada = (100 * (com_custo - custo_tot) / com_custo) if com_custo else None
print(f"   Estimada (catálogo):     {estimada:.2f}%" if estimada is not None else "   Estimada: —")

# A média geral é contaminada pelas marcas com cadastro furado. A mediana
# ponderada das marcas plausíveis diz se o catálogo serve para as OUTRAS.
sadias = [b for b in d["brands"]
          if b["marginPct"] is not None and -20 <= b["marginPct"] <= 80]
rec_s = sum(b["revenue"] * b["coveragePct"] / 100 for b in sadias)
cus_s = sum(b["cost"] for b in sadias)
est_s = (100 * (rec_s - cus_s) / rec_s) if rec_s else None
parte = 100 * sum(b["revenue"] for b in sadias) / d["totalRevenue"] if d["totalRevenue"] else 0
print(f"\n   Excluindo marcas com margem impossível "
      f"({len(d['brands']) - len(sadias)} de {len(d['brands'])}, "
      f"{100 - parte:.1f}% do faturamento):")
print(f"   Estimada nas marcas plausíveis: {est_s:.2f}%" if est_s is not None else "")
if est_s is not None and oficial is not None:
    gap = est_s - oficial
    print(f"   Diferença contra a oficial: {gap:+.2f} pontos")
    if abs(gap) > 10:
        print("   >> Longe. O custo do catálogo não representa o custo real.")
    elif abs(gap) > 4:
        print("   >> Deslocada, mas na mesma faixa. Serve para COMPARAR marcas;")
        print("      o valor absoluto continua sendo o oficial.")
    else:
        print("   >> Próxima. A estimativa é utilizável marca a marca.")

# ── 3b. Quem está com o cadastro furado? ────────────────────────────────────
# Margem de -300% não é margem ruim: é unidade de medida trocada entre o
# faturamento e o catálogo. Óleo vendido a litro com custo cadastrado por
# balde produz exatamente este retrato.
print("\n3b) MARCAS COM MARGEM IMPOSSÍVEL — cadastro a revisar")
ruins = [b for b in d["brands"]
         if b["marginPct"] is not None and not (-20 <= b["marginPct"] <= 80)]
ruins.sort(key=lambda b: b["revenue"], reverse=True)
if not ruins:
    print("   Nenhuma.")
else:
    print(f"   {len(ruins)} marca(s), {backend.brl(sum(b['revenue'] for b in ruins))} "
          f"({100 - parte:.1f}% do faturamento)")
    print(f"   {'MARCA':<20}{'LÍQUIDO':>14}{'MARGEM':>12}{'R$/PEÇA':>11}")
    for b in ruins[:10]:
        print(f"   {b['brand'][:19]:<20}{backend.brl(b['revenue']):>14}"
              f"{b['marginPct']:>11.0f}%{backend.brl(b['ticketPerPiece']):>11}")

    # Amostra de itens da pior marca: é aqui que a causa aparece.
    pior = ruins[0]["brand"]
    print(f"\n   Amostra de itens de {pior} — venda contra custo do catálogo:")
    print(f"   {'SKU':<16}{'QTD':>8}{'LÍQUIDO':>13}{'R$/UN VEND':>13}{'CUSTO CAD':>12}")
    for r in conn.execute(
        """SELECT f.sku_key, SUM(f.quantity) q, SUM(f.net_value) v, MAX(c.custo) custo
           FROM fact_sales_detail f
           LEFT JOIN catalogo_custo c ON c.ref = UPPER(TRIM(f.sku_key))
                                     AND c.marca = UPPER(TRIM(COALESCE(f.brand_name,'')))
           WHERE f.company_id = ? AND f.competence = ? AND f.net_value > 0
             AND UPPER(TRIM(COALESCE(f.brand_name,''))) = ?
           GROUP BY f.sku_key ORDER BY v DESC LIMIT 8""",
            (company_id, comp, pior)).fetchall():
        q = float(r["q"] or 0)
        v = float(r["v"] or 0)
        print(f"   {str(r['sku_key'])[:15]:<16}{q:>8,.0f}{backend.brl(v):>13}"
              f"{backend.brl(v / q if q else 0):>13}{backend.brl(r['custo'] or 0):>12}")
    print("\n   >> Se o CUSTO CADASTRADO for muito maior que o preço unitário")
    print("      vendido, a unidade de medida está trocada (litro x balde, peça")
    print("      x caixa) — não é margem negativa, é cadastro.")

# ── 4. O ranking por marca ──────────────────────────────────────────────────
print("\n4) MARGEM POR MARCA — as 15 maiores em faturamento")
# POR CÓDIGO é a coluna decisiva: custo casado pelo código interno vem da
# embalagem exata. Casado só pela referência, mistura caixa com litro.
print(f"   {'MARCA':<22}{'LÍQUIDO':>15}{'PEÇAS':>10}{'R$/PEÇA':>11}"
      f"{'MARGEM':>9}{'P/CÓDIGO':>10}")
for b in d["brands"][:15]:
    mg = f"{b['marginPct']:.1f}%" if b["marginPct"] is not None else "—"
    print(f"   {b['brand'][:21]:<22}{backend.brl(b['revenue']):>15}"
          f"{b['pieces']:>10,.0f}{backend.brl(b['ticketPerPiece']):>11}"
          f"{mg:>9}{b.get('byCodePct', 0):>9.0f}%"
          f"{'' if not b['costSuspect'] else '  ← revisar custo'}")

por_codigo = sum(b["revenue"] * b.get("byCodePct", 0) / 100 for b in d["brands"])
pct_cod = 100 * por_codigo / d["totalRevenue"] if d["totalRevenue"] else 0
print(f"\n   Custo casado pelo CÓDIGO INTERNO: {pct_cod:.1f}% do faturamento")
if pct_cod < 50:
    print("   >> A maior parte ainda casa pela REFERÊNCIA, que mistura caixa com")
    print("      litro. Reimportar a competência traz o código da coluna E e")
    print("      corrige a margem dos lubrificantes.")
else:
    print("   >> A embalagem exata está sendo usada na maior parte da venda.")

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
