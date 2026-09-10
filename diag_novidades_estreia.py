"""
O que aparece como novidade é novidade mesmo?

Uso:
    /srv/passini/venv/crm/bin/python /srv/passini/apps/crm-comercial/diag_novidades_estreia.py MATRIZ
    /srv/passini/venv/crm/bin/python /srv/passini/apps/crm-comercial/diag_novidades_estreia.py "ZONA NORTE"

A régua é a ESTREIA EM VENDAS: primeira venda de toda a base dentro da janela.
A hipótese do código sequencial foi medida e descartada (diag_novidade.py), mas
o código continua servindo de CONFERÊNCIA: se o que sai aqui como novidade
tiver, em média, código mais alto que o resto da base, é sinal de que a régua
está apontando para itens realmente novos.

O risco desta tela é específico e caro: apontar peça velha como lançamento. O
vendedor oferece como novidade, o cliente responde "isso eu compro há anos", e
ele para de acreditar em tudo que o sistema sugere.

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
unidade = " ".join(a for a in sys.argv[1:] if not a.startswith("-")).strip().upper() or "MATRIZ"

inicio = time.time()
d = backend.sales_debut_novelties(conn, company_id, unidade)
seg = time.time() - inicio

print(f"Banco: {backend.DB_PATH}")
print(f"Unidade: {d['unitName']}  ·  estreias desde {d['since']} ({d['days']} dias)  ·  {seg:.2f}s\n")
print("Régua:")
print("   estreia = PRIMEIRA venda de toda a base dentro da janela")
print(f"   mínimo de clientes: {backend.NOVELTY_MIN_CLIENTS} (uma venda só é acaso)")
print("   código interno: exibido como reforço, NUNCA como filtro\n")

print(f"1) VOLUME  ·  {d['totalItems']} item(ns) estrearam · "
      f"{d['inStockCount']} com saldo em {d['unitName']}")
if not d["items"]:
    print("\n   Nenhuma novidade na janela.")
    conn.close()
    raise SystemExit(0)

# ── 2. Conferência: o código dos "novos" é mais alto? ────────────────────────
print("\n2) CONFERÊNCIA PELO CÓDIGO (o descartado como critério, útil como prova)")
codigos_novos = sorted(int(i["code"]) for i in d["items"] if str(i["code"]).isdigit())
todos = sorted(int(r[0]) for r in conn.execute(
    "SELECT item_code FROM item_catalog WHERE company_id = ?", (company_id,)).fetchall()
    if str(r[0]).isdigit())
if codigos_novos and todos:
    med_novos = codigos_novos[len(codigos_novos) // 2]
    med_todos = todos[len(todos) // 2]
    acima = sum(1 for c in codigos_novos if c > med_todos)
    print(f"   código mediano dos estreantes: {med_novos}")
    print(f"   código mediano da base.......: {med_todos}")
    print(f"   {acima} de {len(codigos_novos)} estreantes "
          f"({100 * acima / len(codigos_novos):.0f}%) têm código acima da mediana da base")
    if acima > len(codigos_novos) * 0.6:
        print("   >> Concentração em código alto. A régua está pegando item novo mesmo.")
    else:
        print("   >> Sem concentração. Boa parte é item ANTIGO que só agora vendeu —")
        print("      pode ser reposição, não lançamento. Cuidado ao chamar de novidade.")

# ── 3. As novidades ──────────────────────────────────────────────────────────
print(f"\n3) AS NOVIDADES (top 20 por alcance)")
print(f"   {'REFERÊNCIA':<17}{'MARCA':<13}{'LINHA':<16}{'CÓDIGO':>8}{'ESTREIA':>12}"
      f"{'CLI':>5}{'QTD':>7}{'PREÇO':>11}  LOJA")
for i in d["items"][:20]:
    loja = "—" if i["inStock"] is None else ("tem" if i["inStock"] else "SEM")
    print(f"   {i['ref'][:16]:<17}{i['brand'][:12]:<13}{i['line'][:15]:<16}"
          f"{str(i['code']):>8}{i['debutAt']:>12}{i['clients']:>5}{int(i['quantity']):>7}"
          f"{backend.brl(i['unitPrice']):>11}  {loja}")

# ── 4. Marcas e linhas que estrearam ─────────────────────────────────────────
print(f"\n4) MARCAS QUE ESTREARAM ({len(d['brands'])})")
if d["brands"]:
    for b in d["brands"][:10]:
        print(f"   {b['name'][:24]:<26}estreou {b['debutAt']} · {b['items']} item(ns) · "
              f"{b['clients']} cliente(s) · {backend.brl(b['revenue'])}")
else:
    print("   Nenhuma marca nova na janela.")

print(f"\n   LINHAS QUE ESTREARAM ({len(d['lines'])})")
if d["lines"]:
    for l in d["lines"][:10]:
        print(f"   {l['name'][:24]:<26}estreou {l['debutAt']} · {l['items']} item(ns) · "
              f"{l['clients']} cliente(s) · {backend.brl(l['revenue'])}")
else:
    print("   Nenhuma linha nova na janela.")

print("\n5) LEITURA")
print("   Passe o olho na seção 3: se reconhecer peça que a casa vende há anos,")
print("   a régua está frouxa e eu aperto (janela maior, ou mínimo de clientes).")
print("   O que tem 'tem' na coluna LOJA é o que o vendedor pode oferecer hoje.")

conn.close()
