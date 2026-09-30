"""
Os indicadores de produtividade descrevem o trabalho ou só repetem o faturamento?

Uso:
    /srv/passini/venv/crm/bin/python /srv/passini/apps/crm-comercial/diag_produtividade.py
    /srv/passini/venv/crm/bin/python /srv/passini/apps/crm-comercial/diag_produtividade.py 2026-08

Faturamento já existe em quatro telas. O que este bloco precisa entregar de novo
é o COMO: se o resultado veio de carteira trabalhada ou de dois pedidos grandes,
se o vendedor liga e não vende, se o mix encolheu. Se os números aqui forem só o
faturamento dividido de outro jeito, a tela não vale a tela.

Quatro modos de falhar em silêncio, todos já vistos neste projeto:
  1. LENTIDÃO — client_person_type_map já classificou a base inteira para usar
     duzentos clientes (1,6s contra 191ms). Aqui ele recebe só os nomes do mês.
  2. NÚMERO PRÓPRIO — se a soma dos quatro baldes não bater com a série do
     painel, a reunião discute qual tela está certa em vez do negócio.
  3. CARTEIRA VAZIA — se quase nenhum cliente faturado estiver na carteira, a
     positivação vira ficção e o vínculo cadastral é que está furado.
  4. DENOMINADOR ERRADO — faturamento por dia com dia corrido em vez de dia útil
     muda o número em ~30% e ninguém percebe.

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

# ── 1. Empresa: o retrato geral e o tempo ───────────────────────────────────
inicio = time.time()
emp = backend.resultados_produtividade(conn, company_id, "empresa", "", comp)
seg = time.time() - inicio
if not emp:
    print("Sem dados para esta competência.")
    conn.close()
    raise SystemExit(0)

print(f"1) EMPRESA — apurado em {seg:.2f}s")
print(f"   Dias úteis: {emp['workingDays']} de {emp['totalWorkingDays']}"
      f"{'  (mês em curso)' if emp['monthOpen'] else ''}")
print(f"   Líquido {backend.brl(emp['revenueNet'])}  ·  "
      f"por dia útil {backend.brl(emp['revenuePerDay'])}")
print(f"   {emp['clients']} cliente(s) faturado(s)  ·  {emp['mixSku']} item(ns) distintos")
cob = emp.get("detailCoveragePct")
print(f"   Composição por cliente cobre {cob:.1f}% do oficial "
      f"({backend.brl(emp['detailRevenue'])})" if cob else "")
if emp.get("clientsUnregistered"):
    print(f"   {emp['clientsUnregistered']} cliente(s) faturado(s) SEM cadastro — "
          f"classificados pelo nome")
if emp.get("clientsNegative"):
    print(f"   {emp['clientsNegative']} cliente(s) só devolveram no mês "
          f"({backend.brl(emp['negativeValue'])}) — fora da contagem de faturados,"
          f" dentro do total oficial")
print(f"   Desvio do arquivo de composição: {emp['compositionDeviationPct']:+.1f}% "
      f"— {'dentro do padrão' if emp['compositionReliable'] else 'FORA DO PADRÃO'}")
if not emp["compositionReliable"]:
    print("   >> Ticket e divisão PF/PJ deste mês NÃO são confiáveis: o arquivo")
    print("      de composição destoa dos outros meses. A tela precisa avisar.")
else:
    print("   >> Proporções confiáveis. Os valores são alocados do oficial, então")
    print("      o ticket não carrega o desvio do arquivo.")
if seg > 2:
    print("   >> LENTO. Confira se a classificação PF/PJ não voltou a varrer a")
    print("      base inteira — é o padrão que já custou 1,6s numa consulta.")

print("\n   PF x PJ")
print(f"   {'TIPO':<6}{'CLIENTES':>10}{'LÍQUIDO':>16}{'TICKET':>14}{'% FAT.':>9}")
for t in ("PF", "PJ"):
    d = emp["byType"][t]
    part = 100 * d["revenue"] / emp["revenueNet"] if emp["revenueNet"] else 0
    print(f"   {t:<6}{d['clients']:>10}{backend.brl(d['revenue']):>16}"
          f"{backend.brl(d['ticket']):>14}{part:>8.0f}%")

print("\n   CARTEIRA x FORA DELA")
print(f"   {'BALDE':<16}{'CLIENTES':>10}{'LÍQUIDO':>16}{'TICKET':>14}")
for k, d in emp["byOrigin"].items():
    print(f"   {k:<16}{d['clients']:>10}{backend.brl(d['revenue']):>16}"
          f"{backend.brl(d['ticket']):>14}")

# ── 2. A soma bate com a série do painel? ───────────────────────────────────
# Esta é a pergunta que decide se a tela pode ir para a reunião.
print("\n1b) A COMPOSIÇÃO SOMA O OFICIAL?")
soma_baldes = sum(d["revenue"] for d in emp["byOrigin"].values())
print(f"   Soma dos baldes {backend.brl(soma_baldes)} · "
      f"oficial {backend.brl(emp['revenueNet'])} · "
      f"diferença {backend.brl(soma_baldes - emp['revenueNet'])}")
if abs(soma_baldes - emp["revenueNet"]) > 1:
    print("   >> A alocação não fechou. Os baldes precisam somar o oficial.")
else:
    print("   >> Fecha. Tickets e segmentos falam a mesma moeda do painel.")

print("\n1c) ALGUM MÊS COM COMPOSIÇÃO QUEBRADA?")
desvios = backend.composicao_desvio(conn, company_id)
for c in sorted(desvios):
    ok, _ = backend.composicao_confiavel(conn, company_id, c)
    print(f"   {c:<10}{desvios[c]:+7.1f}%   {'ok' if ok else 'FORA DO PADRÃO'}")
quebrados = [c for c in sorted(desvios)
             if not backend.composicao_confiavel(conn, company_id, c)[0]]
if quebrados:
    print(f"\n   >> {', '.join(quebrados)} com arquivo incompleto. Reimportar o")
    print("      faturamento por cliente desses meses destrava o histórico de")
    print("      ticket e de carteira x balcão.")

print("\n2) BATE COM A SÉRIE DO PAINEL?")
serie = backend.resultados_serie(conn, company_id, "empresa", "")
oficial = next((r["revenueNet"] for r in serie if r["competence"] == comp), None)
if oficial is None:
    print("   Competência ausente da série — nada a comparar.")
else:
    dif = emp["revenueNet"] - oficial
    print(f"   Produtividade {backend.brl(emp['revenueNet'])}  ·  "
          f"série {backend.brl(oficial)}  ·  diferença {backend.brl(dif)}")
    if abs(dif) > 1:
        print("   >> DIVERGE. A série soma a garantia de volta no líquido e esta")
        print("      função não — confira se é só isso antes de mostrar as duas")
        print("      telas na mesma reunião.")
    else:
        print("   >> Mesma base. As duas telas contam a mesma história.")

# ── 3. A carteira sustenta a positivação? ───────────────────────────────────
# Positivação sobre carteira vazia é divisão por quase-zero: dá número grande e
# sem sentido. Se o vínculo cadastral estiver furado, é melhor não mostrar o
# indicador do que mostrar um que engana.
print("\n3) CARTEIRA x BALCÃO")
# Cliente sem vendedor interno é BALCÃO, não falha de cadastro — regra de
# negócio confirmada pela diretoria. Fica fora do denominador da positivação:
# cobrar o vendedor por quem nunca foi dele seria inventar um problema.
print(f"   {'SEGMENTO':<12}{'CLIENTES':>10}{'LÍQUIDO':>16}{'TICKET':>13}{'% FAT.':>9}")
for chave, rot in (("portfolio", "Carteira"), ("counter", "Balcão")):
    d = emp[chave]
    sh = f"{d['sharePct']:.0f}%" if d["sharePct"] is not None else "—"
    print(f"   {rot:<12}{d['clients']:>10}{backend.brl(d['revenue']):>16}"
          f"{backend.brl(d['ticket']):>13}{sh:>9}")
print(f"\n   Carteira: {emp['portfolioSize']} cliente(s)")
print(f"   Compraram no mês: {emp['portfolioServed']}")
print(f"   SEM DONO: {emp['portfolioOrphan']} "
      f"({emp['portfolioOrphanServed']} compraram mesmo assim)")
if emp["portfolioOrphan"]:
    print("   >> Vendedor desligado ou PJ recorrente nunca vinculado. Não é")
    print("      desempenho: é lista de redistribuição.")
if emp["positivationPct"] is not None:
    print(f"   Positivação: {emp['positivationPct']:.1f}%")
    ocioso = emp["portfolioSize"] - emp["portfolioServed"]
    print(f"   >> {ocioso} cliente(s) da carteira NÃO compraram. Esse é o número")
    print("      que vira ação na reunião — não o total de clientes atendidos.")
if emp["portfolioSize"] < emp["portfolioServed"]:
    print("   >> Carteira menor que os atendidos dela: positivação acima de 100%")
    print("      é sintoma de vínculo quebrado, não desempenho.")

# ── 4. Ligação vira venda? ──────────────────────────────────────────────────
print("\n4) LIGAÇÃO ATIVA E CONVERSÃO")
print(f"   {emp['activeCalls']} ligação(ões) ativa(s) · "
      f"{emp['callsPerDay']:.1f} por dia útil")
print(f"   {emp['clientsCalled']} cliente(s) contatado(s) · "
      f"{emp['converted']} compraram no mês")
if emp["conversionPct"] is not None:
    print(f"   Conversão: {emp['conversionPct']:.1f}%")
else:
    print("   >> Nenhuma ligação registrada. O indicador não mede a equipe: mede")
    print("      o registro. Cobrar conversão antes de o registro existir faz o")
    print("      vendedor desconfiar da tela inteira.")

# ── 5. Os níveis se sustentam separados? ────────────────────────────────────
# O painel mostra unidade e vendedor. Se o recorte não filtrar de verdade, cada
# unidade mostra o número da empresa — foi exatamente o que aconteceu com a
# MATRIZ na primeira versão da série (4.466 clientes, ticket R$ 425).
print("\n5) O RECORTE FILTRA DE VERDADE?")
unidades = [r["unit_name"] for r in conn.execute(
    "SELECT DISTINCT unit_name FROM fact_unit_summary WHERE company_id = ? "
    "AND competence = ? ORDER BY unit_name", (company_id, comp)).fetchall()
    if r["unit_name"]]
print(f"   {'UNIDADE':<16}{'LÍQUIDO':>15}{'/DIA':>12}{'CLI':>6}{'MIX':>6}"
      f"{'POSIT':>8}{'CONV':>7}")
soma = 0.0
for u in unidades:
    p = backend.resultados_produtividade(conn, company_id, "unidade", u, comp)
    if not p:
        continue
    soma += p["revenueNet"]
    pos = f"{p['positivationPct']:.0f}%" if p["positivationPct"] is not None else "—"
    cv = f"{p['conversionPct']:.0f}%" if p["conversionPct"] is not None else "—"
    print(f"   {u[:15]:<16}{backend.brl(p['revenueNet']):>15}"
          f"{backend.brl(p['revenuePerDay']):>12}{p['clients']:>6}{p['mixSku']:>6}"
          f"{pos:>8}{cv:>7}")
    if p["revenueNet"] > emp["revenueNet"] * 0.99 and len(unidades) > 1:
        print(f"      >> {u} mostra QUASE O TOTAL DA EMPRESA. O filtro não pegou.")

dif_u = soma - emp["revenueNet"]
print(f"\n   Soma das unidades {backend.brl(soma)} contra empresa "
      f"{backend.brl(emp['revenueNet'])} · diferença {backend.brl(dif_u)}")
if abs(dif_u) > max(1.0, emp["revenueNet"] * 0.01):
    print("   >> Sobra ou falta faturamento entre os níveis. Provável vendedor")
    print("      sem unidade resolvida na competência — some no recorte e")
    print("      aparece só no total.")

# ── 6. Vendedores: o ranking separa quem trabalha de quem só fatura? ────────
print("\n6) VENDEDORES — produtividade além do faturamento")
vendedores = [r["seller_name"] for r in conn.execute(
    "SELECT seller_name, SUM(net_value) v FROM fact_sales_detail "
    "WHERE company_id = ? AND competence = ? GROUP BY seller_name "
    "ORDER BY v DESC LIMIT 12", (company_id, comp)).fetchall() if r["seller_name"]]
print(f"   {'VENDEDOR':<24}{'/DIA':>12}{'CLI':>5}{'MIX':>5}{'CART':>6}"
      f"{'POSIT':>7}{'LIG':>6}{'CONV':>7}{'TK PJ':>12}")
for v in vendedores:
    p = backend.resultados_produtividade(conn, company_id, "vendedor", v, comp)
    if not p:
        continue
    pos = f"{p['positivationPct']:.0f}%" if p["positivationPct"] is not None else "—"
    cv = f"{p['conversionPct']:.0f}%" if p["conversionPct"] is not None else "—"
    print(f"   {backend.normalize_whitespace(v)[:23]:<24}"
          f"{backend.brl(p['revenuePerDay']):>12}{p['clients']:>5}{p['mixSku']:>5}"
          f"{p['portfolioSize']:>6}{pos:>7}{p['activeCalls']:>6}{cv:>7}"
          f"{backend.brl(p['byType']['PJ']['ticket']):>12}")

# ── 7. A tela aguenta? ──────────────────────────────────────────────────────
# O endpoint monta uma linha por vendedor. Se cada linha custar meio segundo, a
# tela leva 20 segundos para abrir e o gerente desiste antes de ver o número.
print("\n7) CUSTO DA TELA — uma chamada por vendedor")
todos = [r["seller_name"] for r in conn.execute(
    "SELECT DISTINCT seller_name FROM fact_vendor_summary "
    "WHERE company_id = ? AND competence = ?", (company_id, comp)).fetchall()
    if r["seller_name"]]
t0 = time.time()
for v in todos:
    backend.resultados_produtividade(conn, company_id, "vendedor", v, comp)
gasto = time.time() - t0
print(f"   {len(todos)} vendedor(es) em {gasto:.2f}s "
      f"({gasto / len(todos) * 1000 if todos else 0:.0f}ms cada)")
if gasto > 4:
    print("   >> LENTO DEMAIS para uma tela. Algum trecho ainda repete trabalho")
    print("      por vendedor — provável varredura de tabela grande sem cache.")
elif gasto > 2:
    print("   >> No limite. Aceitável, mas não crescerá bem com mais vendedores.")
else:
    print("   >> Rápido. Os caches por conexão estão segurando.")

print("\n   >> O teste da tela: se as colunas de produtividade apenas repetirem a")
print("      ordem do faturamento, elas não acrescentam nada à reunião. O valor")
print("      está em achar quem fatura bem com carteira abandonada — e quem")
print("      trabalha a carteira sem converter.")

conn.close()
