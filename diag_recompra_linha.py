"""
A recompra por linha está certa? Confere contra o histórico real.

Uso:
    /srv/passini/venv/crm/bin/python /srv/passini/apps/crm-comercial/diag_recompra_linha.py
    /srv/passini/venv/crm/bin/python /srv/passini/apps/crm-comercial/diag_recompra_linha.py MATRIZ

Uma sugestão errada custa mais que sugestão nenhuma: o vendedor liga, fala de
uma peça que o cliente não usa, e passa a ignorar o sistema. Por isso, antes de
qualquer tela, este script abre a conta de alguns clientes — as datas de compra
uma a uma, o intervalo que saiu delas e o atraso — para dar para conferir na
mão se a régua faz sentido.

Mostra também quanto do estoque da unidade cobre as linhas sugeridas: sugestão
sem saldo é promessa que o vendedor não cumpre.

Não altera nada.
"""
import os
import sys
import time
from collections import Counter
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
unidade = " ".join(a for a in sys.argv[1:] if not a.startswith("-")).strip().upper()
hoje = backend.today_in_brazil()
print(f"Banco: {backend.DB_PATH}")
print(f"Hoje: {hoje.isoformat()}  ·  unidade: {unidade or '(sem cruzar estoque)'}\n")

print("Régua em uso:")
print(f"   rajada.............: compras em até {backend.LINE_REPURCHASE_BURST_DAYS} dias contam como 1 ocasião")
print(f"   mínimo de ocasiões.: {backend.LINE_REPURCHASE_MIN_OCCASIONS}")
print(f"   intervalo típico...: mediana · folga de {backend.LINE_REPURCHASE_GRACE:.2f}x")
print(f"   atraso mínimo......: {backend.LINE_REPURCHASE_MIN_OVERDUE_DAYS} dias")
print(f"   intervalo máximo...: {backend.LINE_REPURCHASE_MAX_INTERVAL_DAYS} dias")
print(f"   histórico..........: {backend.LINE_REPURCHASE_HISTORY_MONTHS} meses\n")

# ── Amostra de clientes ativos ───────────────────────────────────────────────
filtros = backend.build_filters_from_query({})
if unidade:
    filtros["unit_name"] = unidade
clientes = [
    r["client_name"] for r in conn.execute(
        "SELECT client_name, SUM(net_value) v FROM fact_sales_detail "
        "WHERE company_id = ? AND net_value > 0 GROUP BY client_name "
        "ORDER BY v DESC LIMIT 300", (company_id,)).fetchall()
]
inicio = time.time()
sugestoes = backend.line_repurchase_for_clients(conn, company_id, clientes, unidade, hoje)
seg = time.time() - inicio
total_sug = sum(len(v) for v in sugestoes.values())
print(f"1) VOLUME  ·  {len(clientes)} clientes analisados em {seg:.2f}s")
pct_clientes = 100 * len(sugestoes) / len(clientes) if clientes else 0
print(f"   {len(sugestoes)} cliente(s) com alguma linha vencida ({pct_clientes:.0f}%)"
      f" · {total_sug} sugestão(ões)")
valor = sum(s["averageValue"] for v in sugestoes.values() for s in v)
print(f"   {backend.brl(valor)} em jogo, somando o valor típico de cada ocasião perdida")
# Se quase todo cliente é sinalizado, não há sinal: é ruído com cara de alerta,
# e o vendedor aprende a rolar a tela sem ler.
if pct_clientes > 60:
    print(f"\n   >> {pct_clientes:.0f}% dos clientes sinalizados é ALTO DEMAIS para ser útil.")
    print("      Aperte a régua antes de levar isso para a tela.")
elif pct_clientes > 35:
    print(f"\n   >> {pct_clientes:.0f}% é muito, mas defensável se a ordenação por valor")
    print("      colocar as boas no topo. Confira a seção 3.")
else:
    print(f"\n   {pct_clientes:.0f}% dos clientes com alguma linha vencida — dá para trabalhar.")
if not sugestoes:
    print("\n   Nenhuma sugestão. Régua apertada demais, ou histórico curto.")
    conn.close()
    raise SystemExit(0)

# ── Quais linhas mais aparecem ───────────────────────────────────────────────
print("\n2) LINHAS MAIS SUGERIDAS")
cont = Counter(s["line"] for v in sugestoes.values() for s in v)
com_saldo = sem_saldo = sem_saber = 0
for v in sugestoes.values():
    for s in v:
        if s["inStock"] is None:
            sem_saber += 1
        elif s["inStock"]:
            com_saldo += 1
        else:
            sem_saldo += 1
for linha, n in cont.most_common(10):
    print(f"   {n:>5}  {linha}")
print(f"\n   Estoque na unidade: {com_saldo} com saldo · {sem_saldo} SEM saldo"
      + (f" · {sem_saber} sem cruzar (unidade não informada)" if sem_saber else ""))
if sem_saldo and (com_saldo + sem_saldo):
    pct = 100 * sem_saldo / (com_saldo + sem_saldo)
    print(f"   {pct:.0f}% das sugestões não têm peça na loja — essas não podem ir para o")
    print("   vendedor como estão: viram promessa que ele não cumpre.")

# ── A conta aberta, cliente a cliente ────────────────────────────────────────
print("\n3) A CONTA ABERTA (5 clientes, para conferir na mão)")
mostrados = 0
for cliente, itens in sugestoes.items():
    if mostrados >= 5:
        break
    mostrados += 1
    print(f"\n   {cliente}")
    for s in itens:
        saldo = ("estoque não cruzado" if s["inStock"] is None
                 else (f"tem na loja ({s['stockItems']} código/s)"
                       if s["inStock"] else "SEM SALDO NA LOJA"))
        print(f"      {s['line'][:24]:<26}compra a cada {s['intervalDays']:>3}d · "
              f"faz {s['daysSinceLast']:>3}d (atraso {s['overdueDays']:>3}d) · "
              f"{s['occasions']} ocasiões ({s['purchases']} pedidos) · "
              f"vale {backend.brl(s['averageValue'])}")
        print(f"      {'':<26}última {s['lastPurchaseAt']} · {saldo}")
        # As datas cruas, para conferir o intervalo na mão
        datas = [r["dia"] for r in conn.execute(
            f"""{backend.CATALOGO_AGRUPADO_SQL}
            SELECT date(f.issue_date) dia FROM fact_sales_detail f
            {backend.CATALOGO_JOIN_SQL}
            WHERE f.company_id = ? AND f.client_name = ? AND f.net_value > 0
              AND UPPER(TRIM(c.item_subgroup)) = ?
            GROUP BY dia ORDER BY dia DESC LIMIT 8""",
            (company_id, company_id, cliente, s["line"])).fetchall()]
        print(f"      {'':<26}datas: {', '.join(datas)}")

print("\n4) LEITURA")
print("   Confira nas datas acima se o intervalo calculado bate com o que se vê.")
print("   Se um cliente aparecer com linha que ele claramente não usa, o problema")
print("   é o casamento do item, não a régua — rode diag_linha_produto.py.")

conn.close()
