"""
Código maior é mesmo item mais recente?

Uso:
    /srv/passini/venv/crm/bin/python /srv/passini/apps/crm-comercial/diag_novidade.py

A hipótese é que o Alfa numera os itens em sequência, então código alto = item
cadastrado depois. Se ela valer, "novidades" sai de graça. Se não valer, uma
tela de novidades apontaria peça velha como lançamento — e o vendedor que
oferecer uma dessas como novidade passa vergonha na frente do cliente.

O teste: para cada item, a PRIMEIRA venda registrada. Se o código acompanha a
ordem de cadastro, item de código alto deve ter primeira venda mais recente.

Limite conhecido e declarado: o faturamento na base começa em 2026-01. Item
vendido desde antes aparece como "primeira venda em janeiro" mesmo sendo de
2015 — por isso a leitura olha a PONTA ALTA dos códigos, onde a censura da
janela não atrapalha.

Não altera nada.
"""
import os
import sys
from collections import defaultdict
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
print(f"Banco: {backend.DB_PATH}\n")

# ── 1. O código é numérico e sequencial? ─────────────────────────────────────
print("1) O CÓDIGO INTERNO SERVE DE RÉGUA?")
total = numericos = 0
menor = maior = None
for r in conn.execute(
    "SELECT item_code FROM item_catalog WHERE company_id = ?", (company_id,)).fetchall():
    total += 1
    c = (r["item_code"] or "").strip()
    if c.isdigit():
        numericos += 1
        v = int(c)
        menor = v if menor is None else min(menor, v)
        maior = v if maior is None else max(maior, v)
print(f"   {numericos} de {total} códigos são numéricos "
      f"({100 * numericos / max(total, 1):.1f}%)")
print(f"   faixa: {menor} a {maior}")
if numericos < total * 0.9:
    print("   >> Boa parte não é numérica. A régua por código não se aplica a todos.")

# ── 2. Primeira venda por item ───────────────────────────────────────────────
print("\n2) CÓDIGO x PRIMEIRA VENDA REGISTRADA")
ref_por_codigo = {}
for r in conn.execute(
    "SELECT item_code, UPPER(TRIM(manufacturer_ref)) ref FROM item_catalog "
    "WHERE company_id = ? AND TRIM(COALESCE(manufacturer_ref,'')) <> ''",
    (company_id,)).fetchall():
    c = (r["item_code"] or "").strip()
    if c.isdigit() and r["ref"]:
        ref_por_codigo.setdefault(r["ref"], []).append(int(c))

primeira = {}
for r in conn.execute(
    "SELECT UPPER(TRIM(sku_key)) ref, MIN(date(issue_date)) inicio "
    "FROM fact_sales_detail WHERE company_id = ? AND net_value > 0 "
    "AND TRIM(COALESCE(sku_key,'')) <> '' GROUP BY ref", (company_id,)).fetchall():
    if r["inicio"]:
        primeira[r["ref"]] = r["inicio"]

pares = []
for ref, codigos in ref_por_codigo.items():
    if ref in primeira:
        pares.append((min(codigos), primeira[ref], ref))
pares.sort()
print(f"   {len(pares)} item(ns) com código numérico E venda registrada\n")

if len(pares) < 50:
    print("   Amostra pequena demais para concluir.")
    conn.close()
    raise SystemExit(0)

# Decis do código: se a hipótese vale, a data sobe junto com o decil.
print(f"   {'DECIL DO CÓDIGO':<20}{'FAIXA':<22}{'1ª VENDA MEDIANA':<18}{'ITENS':>7}")
n = len(pares)
for d in range(10):
    fatia = pares[int(d * n / 10):int((d + 1) * n / 10)]
    if not fatia:
        continue
    datas = sorted(p[1] for p in fatia)
    print(f"   {d + 1:>2}º                  "
          f"{fatia[0][0]}–{fatia[-1][0]:<12}"
          f"{datas[len(datas) // 2]:<18}{len(fatia):>7}")

# ── 3. Quem estreou recentemente ─────────────────────────────────────────────
print("\n3) ITENS QUE ESTREARAM NOS ÚLTIMOS 90 DIAS")
corte = (backend.today_in_brazil() - __import__("datetime").timedelta(days=90)).isoformat()
novos = [p for p in pares if p[1] >= corte]
print(f"   {len(novos)} item(ns) venderam pela primeira vez desde {corte}")
if novos:
    codigos_novos = sorted(p[0] for p in novos)
    meio_novos = codigos_novos[len(codigos_novos) // 2]
    meio_todos = sorted(p[0] for p in pares)[len(pares) // 2]
    print(f"   código mediano dos novos.: {meio_novos}")
    print(f"   código mediano de todos..: {meio_todos}")
    if meio_novos > meio_todos * 1.05:
        print("   >> Os que estrearam têm código MAIS ALTO. A hipótese se sustenta.")
    elif meio_novos < meio_todos * 0.95:
        print("   >> Os que estrearam têm código MAIS BAIXO. A hipótese se inverte —")
        print("      são itens antigos que só agora venderam, não lançamentos.")
    else:
        print("   >> Sem diferença. O código NÃO indica novidade; a estreia em vendas")
        print("      é um sinal melhor do que o número do cadastro.")
    print(f"\n   Os 12 de código mais alto entre os que estrearam:")
    print(f"      {'CÓDIGO':<10}{'REFERÊNCIA':<18}{'1ª VENDA':<12}")
    for cod, dt, ref in sorted(novos, reverse=True)[:12]:
        print(f"      {cod:<10}{ref[:17]:<18}{dt:<12}")

print("\n4) LEITURA")
print("   Se a hipótese se sustentar, 'novidade' pode sair do código do cadastro.")
print("   Se não, o sinal honesto é a ESTREIA EM VENDAS — item que nunca tinha")
print("   vendido e passou a vender. Esse não depende de como o Alfa numera, e é")
print("   o que o vendedor percebe como novidade de verdade.")

conn.close()
