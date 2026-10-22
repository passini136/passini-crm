"""
O CRM tem dado para montar o Dashboard Executivo do modelo?

Uso (venv do CRM):
    /srv/passini/venv/crm/bin/python /srv/passini/apps/crm-comercial/diag_dashboard_gerente.py [DIAS]

POR QUE ESTE DIAGNÓSTICO EXISTE

O modelo trazido tem oito cartões, um gráfico diário e um mix PJ×PF. A conta
dele se revela sozinha: 9.387 perdidos ÷ (10.787 vendas + 9.387 perdidos) =
46,5%, que é a "taxa de perda média" mostrada. Ou seja, "Total de vendas" ali
NÃO é faturamento — são ORÇAMENTOS QUE FECHARAM. O painel inteiro se apoia
numa base de orçamentos.

No nosso CRM, orçamento é o módulo Cotações, que está em piloto. Se ele tiver
dezenas de registros em vez de dezenas de milhares, copiar o modelo produz um
painel honesto e inútil — números reais que não representam a operação.

Então, antes de desenhar qualquer tela, este script mede cartão por cartão:
o que dá para preencher com o dado de hoje, o que dá com aproximação (e qual),
e o que não dá de jeito nenhum. Também confere o recorte por vendedor e por
período, que são as duas exigências do pedido.

NÃO ALTERA NADA.
"""
import os
import sqlite3
import sys
from datetime import timedelta
from pathlib import Path

sys.path.insert(0, "/srv/passini/apps/crm-comercial")

if not os.environ.get("PASSINI_CRM_DATA"):
    for candidate in ("/srv/passini/data/crm", "/srv/passini/data"):
        if (Path(candidate) / "passini_dashboard.db").exists():
            os.environ["PASSINI_CRM_DATA"] = candidate
            break

import backend  # noqa: E402

DIAS = int(sys.argv[1]) if len(sys.argv) > 1 else 30
conn = backend.get_connection()
cid = conn.execute("SELECT id FROM companies LIMIT 1").fetchone()["id"]
hoje = backend.today_in_brazil()
desde = (hoje - timedelta(days=DIAS)).isoformat()
print(f"Banco: {backend.DB_PATH}")
print(f"Janela: últimos {DIAS} dias ({desde} a {hoje})\n")


def cab(t):
    print(f"\n{t}")
    print("-" * len(t))


# ── 1. Orçamentos: a base do modelo ─────────────────────────────────────────
cab("1) COTAÇÕES — é daqui que o modelo tira vendas, perdidos e taxa de perda")
try:
    tot = conn.execute(
        "SELECT COUNT(*) n, MIN(date(quoted_at)) a, MAX(date(quoted_at)) b"
        "  FROM crm_quotes WHERE company_id = ?", (cid,)).fetchone()
    print(f"   Total de cotações na base: {tot['n']:,}")
    print(f"   Período com registro: {tot['a'] or '—'} a {tot['b'] or '—'}")
    janela = conn.execute(
        "SELECT status, COUNT(*) n FROM crm_quotes"
        " WHERE company_id = ? AND date(quoted_at) >= date(?)"
        " GROUP BY status", (cid, desde)).fetchall()
    por_status = {r["status"]: r["n"] for r in janela}
    fechou = por_status.get("FECHOU", 0)
    perdeu = por_status.get("NAO_FECHOU", 0)
    base = fechou + perdeu
    print(f"\n   Na janela de {DIAS} dias:")
    for s, n in sorted(por_status.items(), key=lambda x: -x[1]):
        print(f"      {s:<14}{n:>8,}")
    print(f"      {'TOTAL':<14}{sum(por_status.values()):>8,}")
    if base:
        print(f"   Taxa de perda: {100 * perdeu / base:.1f}%  "
              f"({perdeu} de {base} com desfecho)")
    else:
        print("   Taxa de perda: — (nenhuma cotação com desfecho na janela)")

    if sum(por_status.values()) < 200:
        print("\n   >> VOLUME BAIXO. O modelo mostra 20 mil orçamentos em 30 dias;")
        print("      aqui o módulo é piloto. Os cartões sairiam corretos e sem")
        print("      significado — e um painel que ninguém reconhece é pior que")
        print("      painel nenhum, porque ensina a equipe a desconfiar da tela.")
except sqlite3.Error as exc:
    print(f"   crm_quotes indisponível: {exc}")

# ── 2. Por vendedor e por unidade ───────────────────────────────────────────
cab("2) O RECORTE POR VENDEDOR E POR UNIDADE EXISTE NA COTAÇÃO?")
try:
    r = conn.execute(
        "SELECT COUNT(DISTINCT seller_name) v, COUNT(DISTINCT unit_name) u,"
        "       SUM(CASE WHEN TRIM(COALESCE(unit_name,'')) = '' THEN 1 ELSE 0 END) sem_un"
        "  FROM crm_quotes WHERE company_id = ?", (cid,)).fetchone()
    print(f"   Vendedores distintos: {r['v']}   Unidades distintas: {r['u']}")
    print(f"   Cotações sem unidade: {r['sem_un']:,}")
    for row in conn.execute(
            "SELECT seller_name, unit_name, COUNT(*) n,"
            "       SUM(status='FECHOU') f, SUM(status='NAO_FECHOU') p"
            "  FROM crm_quotes WHERE company_id = ?"
            " GROUP BY seller_name ORDER BY n DESC LIMIT 8", (cid,)):
        taxa = (100 * row["p"] / (row["f"] + row["p"])) if (row["f"] + row["p"]) else 0
        print(f"      {str(row['seller_name'])[:26]:<28}{str(row['unit_name'] or '—')[:12]:<13}"
              f"{row['n']:>5} cot · perda {taxa:.0f}%")
except sqlite3.Error as exc:
    print(f"   erro: {exc}")

# ── 3. O que o faturamento oferece no lugar ─────────────────────────────────
cab("3) FATURAMENTO — a alternativa para 'quantidade de vendas'")
r = conn.execute(
    "SELECT COUNT(*) linhas, COUNT(DISTINCT issue_date) dias,"
    "       SUM(CASE WHEN TRIM(COALESCE(issue_date,'')) = '' THEN 1 ELSE 0 END) sem_data"
    "  FROM fact_sales_detail WHERE company_id = ?", (cid,)).fetchone()
print(f"   Linhas de faturamento: {r['linhas']:,}")
print(f"   Linhas SEM data de emissão: {r['sem_data']:,}")
print("   >> fact_sales_detail NÃO tem número de nota nem de pedido. 'Quantidade")
print("      de vendas' só sai por aproximação: cliente + dia + vendedor como")
print("      um atendimento. Dois pedidos do mesmo cliente no mesmo dia contam")
print("      como um — é preciso dizer isso na tela, não esconder.")

atendimentos = conn.execute(
    "SELECT COUNT(*) n FROM (SELECT DISTINCT client_name, issue_date, seller_name"
    "  FROM fact_sales_detail WHERE company_id = ? AND date(issue_date) >= date(?)"
    "    AND net_value > 0)", (cid, desde)).fetchone()["n"]
linhas_janela = conn.execute(
    "SELECT COUNT(*) n FROM fact_sales_detail"
    "  WHERE company_id = ? AND date(issue_date) >= date(?) AND net_value > 0",
    (cid, desde)).fetchone()["n"]
print(f"\n   Na janela: {linhas_janela:,} linha(s) → {atendimentos:,} atendimento(s)")

# ── 4. PJ x PF ──────────────────────────────────────────────────────────────
cab("4) MIX PJ × PF")
nomes = [r[0] for r in conn.execute(
    "SELECT DISTINCT client_name FROM fact_sales_detail"
    "  WHERE company_id = ? AND date(issue_date) >= date(?) AND net_value > 0"
    " LIMIT 4000", (cid, desde))]
tipos = backend.client_person_type_map(conn, cid, nomes)
pj = sum(1 for n in nomes if tipos.get(backend.normalize_client_key(n)) == "PJ")
print(f"   Clientes faturados na janela (amostra): {len(nomes):,}")
print(f"   PJ: {pj:,} ({100 * pj / max(1, len(nomes)):.1f}%)   "
      f"PF: {len(nomes) - pj:,} ({100 * (len(nomes) - pj) / max(1, len(nomes)):.1f}%)")
print("   >> Classificação pela MESMA função da carteira. Disponível.")

# ── 5. Itens em falta ───────────────────────────────────────────────────────
cab("5) ITENS ÚNICOS EM FALTA")
fconn = backend.faltas_conexao()
if fconn is None:
    print("   Arquivo de faltas ausente — rode exportar_faltas.py.")
else:
    comp = hoje.strftime("%Y-%m")
    r = fconn.execute(
        "SELECT COUNT(DISTINCT item_code) itens, SUM(pedidos) ped"
        "  FROM faltas_resumo WHERE competencia = ?", (comp,)).fetchone()
    top = fconn.execute(
        "SELECT item_code, SUM(pedidos) p FROM faltas_resumo"
        "  WHERE competencia = ? GROUP BY item_code ORDER BY p DESC LIMIT 1",
        (comp,)).fetchone()
    print(f"   Competência {comp}: {r['itens'] or 0:,} item(ns) único(s), "
          f"{r['ped'] or 0:,} pedido(s)")
    if top:
        print(f"   Top: {top['item_code']} ({top['p']} pedidos)")
    print("   >> Disponível. Atenção: a base de faltas é por MÊS (competência),")
    print("      não por dia — um seletor de 'últimos 30 dias' não casa com ela")
    print("      sem arredondar para o mês.")
    fconn.close()

# ── 6. Veredito por cartão ──────────────────────────────────────────────────
cab("6) CARTÃO A CARTÃO — o que dá para entregar hoje")
print(f"   {'CARTÃO DO MODELO':<28}{'FONTE NO CRM':<26}SITUAÇÃO")
for cartao, fonte, situacao in [
    ("Total de vendas", "crm_quotes FECHOU", "depende do volume do piloto"),
    ("Vendas PJ / PF", "catálogo + cadastro", "pronto"),
    ("Orçamentos perdidos", "crm_quotes NAO_FECHOU", "depende do volume do piloto"),
    ("Taxa de perda média", "crm_quotes", "depende do volume do piloto"),
    ("Melhor unidade", "crm_quotes por unidade", "depende do volume do piloto"),
    ("Pior taxa de perda", "crm_quotes por unidade", "depende do volume do piloto"),
    ("Itens únicos em falta", "faltas.db (Radar)", "pronto, mas por MÊS"),
    ("Evolução diária", "quotes.quoted_at / issue_date", "pronto"),
    ("Mix PJ × PF", "catálogo + cadastro", "pronto"),
    ("Filtro de período", "todas", "pronto, menos faltas (mês)"),
    ("Visão por vendedor", "quotes.seller_name", "pronto"),
]:
    print(f"   {cartao:<28}{fonte:<26}{situacao}")

conn.close()
print("\nNada foi alterado.")
