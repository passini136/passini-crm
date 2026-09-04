"""
Confere a linha do tempo de ticket médio semanal.

Uso:
    /srv/passini/venv/crm/bin/python /srv/passini/apps/crm-comercial/diag_ticket_semanal.py GABRIELY
    /srv/passini/venv/crm/bin/python /srv/passini/apps/crm-comercial/diag_ticket_semanal.py --todos

Gráfico bonito com número errado é pior que nenhum gráfico: o vendedor cobra o
gerente em cima dele. Este script mostra as doze semanas, soma as que caem no
mês corrente e compara com o total do mesmo período no faturamento detalhado —
se as duas contas divergirem, a agregação por semana está perdendo ou dobrando
linha. Também cronometra a consulta, porque a tela abre por clique.

Não altera nada.
"""
import os
import sys
import time
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
todos = "--todos" in sys.argv
procurado = " ".join(a for a in sys.argv[1:] if not a.startswith("-")).strip().upper()

print(f"Banco: {backend.DB_PATH}\n")

vendedores = [
    backend.normalize_whitespace(r["seller_name"])
    for r in conn.execute(
        "SELECT DISTINCT seller_name FROM fact_vendor_summary WHERE company_id = ? "
        "ORDER BY seller_name", (company_id,)).fetchall()
    if r["seller_name"]
]
if procurado:
    vendedores = [v for v in vendedores if procurado in backend.normalize_upper(v)]
elif not todos:
    vendedores = vendedores[:1]
if not vendedores:
    print("Nenhum vendedor encontrado. Use --todos ou informe parte do nome.")
    raise SystemExit(1)

total_seg = 0.0
for nome in vendedores:
    inicio = time.time()
    dados = backend.seller_ticket_timeline(conn, company_id, nome)
    seg = time.time() - inicio
    total_seg += seg
    semanas = dados["weeks"]

    print("═" * 78)
    print(f"  {nome}   ({seg * 1000:.0f} ms)")
    print("═" * 78)
    print(f"  {'SEMANA':<14}{'LÍQUIDO':>14}{'CLIENTES':>10}{'TICKET':>12}")
    for s in semanas:
        marca = " <<" if s["current"] else ""
        print(f"  {s['weekStart'][8:10]}/{s['weekStart'][5:7]} a "
              f"{s['weekEnd'][8:10]}/{s['weekEnd'][5:7]}"
              f"{backend.brl(s['revenue']):>14}{s['clients']:>10}"
              f"{backend.brl(s['ticket']):>12}{marca}")
    print(f"\n  média {backend.brl(dados['averageTicket'])} · "
          f"melhor {backend.brl(dados['bestTicket'])} · "
          f"{dados['weeksWithSales']} de {len(semanas)} semanas com venda")

    # ── Reconciliação: as semanas somam o mesmo que o período inteiro? ────────
    if semanas:
        de, ate = semanas[0]["weekStart"], semanas[-1]["weekEnd"]
        condicao, valores = backend.seller_filter_sql(conn, company_id, nome)
        direto = conn.execute(
            f"SELECT ROUND(SUM(net_value),2) v, COUNT(DISTINCT client_name) c "
            f"FROM fact_sales_detail WHERE company_id = ? AND {condicao} "
            f"AND date(issue_date) BETWEEN date(?) AND date(?) AND net_value > 0",
            (company_id, *valores, de, ate)).fetchone()
        soma_semanas = round(sum(s["revenue"] for s in semanas), 2)
        bruto = round(float(direto["v"] or 0), 2)
        dif = round(soma_semanas - bruto, 2)
        print(f"\n  Conferência {de} a {ate}:")
        print(f"     soma das semanas..: {backend.brl(soma_semanas)}")
        print(f"     consulta direta...: {backend.brl(bruto)}")
        if abs(dif) > 0.01:
            print(f"     >> DIVERGE em {backend.brl(dif)} — a agregação semanal está")
            print("        perdendo ou duplicando linha. Não confie no gráfico.")
        else:
            print("     batem. A soma das semanas é o período inteiro.")
        # Clientes NÃO somam: quem compra em duas semanas conta em cada uma.
        # É esperado, e o ticket semanal continua certo — mas registrar evita
        # alguém "corrigir" isso achando que é erro.
        soma_clientes = sum(s["clients"] for s in semanas)
        print(f"     clientes: {soma_clientes} somando semanas x {direto['c']} distintos no período")
        print("     (a diferença é o cliente que comprou em mais de uma semana — esperado)")
    print()

print(f"Tempo total: {total_seg:.2f}s para {len(vendedores)} vendedor(es) "
      f"({total_seg / len(vendedores) * 1000:.0f} ms cada)")
conn.close()
