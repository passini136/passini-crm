"""
O que a oficina nova compra na PRIMEIRA vez?

Uso:
    /srv/passini/venv/crm/bin/python /srv/passini/apps/crm-comercial/diag_prospeccao.py MATRIZ
    /srv/passini/venv/crm/bin/python /srv/passini/apps/crm-comercial/diag_prospeccao.py "ZONA NORTE"

O palpite fácil para prospecção é "ofereça o mais barato". O dado responde
melhor: entre os clientes que compraram pela primeira vez no último ano, o que
eles levaram NAQUELA primeira compra? Isso não é teoria de vendas — é o que
aconteceu, e dá ao vendedor uma frase que já funcionou com outras oficinas.

O que conferir aqui: se as linhas do topo fizerem sentido como porta de
entrada. Se aparecer algo caro e raro no topo, a janela de "primeira compra"
está larga demais e está pegando relacionamento, não abertura.

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
d = backend.prospecting_entry_items(conn, company_id, unidade)
seg = time.time() - inicio

print(f"Banco: {backend.DB_PATH}")
print(f"Unidade: {d['unitName']}  ·  {seg:.2f}s\n")
print("Régua:")
print(f"   dados começam em...: {d.get('baseStart', '—')}")
print(f"   carência...........: {d.get('guardDays')} dias — antes disso não dá para saber")
print("                         se a estreia é do cliente ou do arquivo")
print(f"   cliente novo.......: primeira compra NA UNIDADE desde {d.get('since', '—')}")
print(f"   primeira compra....: o que entrou em até {d.get('firstDays')} dias da estreia")
print(f"   vendedores da loja.: {d.get('sellers', 0)}")
print(f"   mínimo de clientes.: {backend.PROSPECT_MIN_CLIENTS}\n")

# Proporção, não número absoluto. O limite fixo que eu tinha posto (3.000) era
# um chute meu e disparou alarme num número que pode estar certo: distribuidora
# de autopeças atende muito balcão, e balcão renova rápido.
total = d.get("totalClients") or 0
pct = (100 * d["newClients"] / total) if total else 0
print(f"1) {d['newClients']} de {total} oficinas desta loja compraram pela primeira vez "
      f"na janela ({pct:.0f}%)")
if pct > 60:
    print("   >> Proporção alta. Ou a loja renovou muito a carteira, ou a janela")
    print("      ainda está pegando a censura do início dos dados.")

# ── Por que 100%? O histórico da unidade cobre mesmo o período todo? ─────────
# Se as vendas dos vendedores desta loja só existirem nos meses recentes, todo
# cliente parece estreante — e o defeito não está na régua, está no recorte.
print("\n1b) O HISTÓRICO DESTA LOJA COBRE A JANELA?")
competencias = backend.query_competences(conn, company_id)
mapa = backend.build_seller_unit_map(conn, company_id, competencias[0] if competencias else "")
vendedores = sorted({
    backend.normalize_whitespace(r["seller_name"])
    for r in conn.execute(
        "SELECT DISTINCT seller_name FROM fact_sales_detail WHERE company_id = ?",
        (company_id,)).fetchall()
    if r["seller_name"] and (
        mapa.get(backend.person_key(backend.normalize_whitespace(r["seller_name"])))
        or mapa.get(backend.short_person_key(backend.normalize_whitespace(r["seller_name"])))
    ) == d["unitName"]
})
print(f"   {len(vendedores)} vendedor(es) casaram com {d['unitName']}")
if vendedores:
    marc = ",".join("?" for _ in vendedores)
    linhas_ano = conn.execute(
        f"SELECT substr(competence,1,4) ano, COUNT(*) linhas, "
        f"COUNT(DISTINCT client_name) clientes "
        f"FROM fact_sales_detail WHERE company_id = ? AND seller_name IN ({marc}) "
        f"GROUP BY ano ORDER BY ano", (company_id, *vendedores)).fetchall()
    print(f"   {'ANO':<8}{'LINHAS':>10}{'CLIENTES':>10}")
    for r in linhas_ano:
        print(f"   {r['ano']:<8}{r['linhas']:>10}{r['clientes']:>10}")
    geral = conn.execute(
        "SELECT substr(competence,1,4) ano, COUNT(*) linhas FROM fact_sales_detail "
        "WHERE company_id = ? GROUP BY ano ORDER BY ano", (company_id,)).fetchall()
    print(f"\n   A empresa toda, para comparar:")
    for r in geral:
        print(f"   {r['ano']:<8}{r['linhas']:>10}")
    print("\n   Se a loja não tiver linhas em 2025 e a empresa tiver, o recorte por")
    print("   vendedor está perdendo histórico — provavelmente nomes que mudaram.")
if not d["lines"]:
    print("\n   Sem dados suficientes. Janela curta, ou poucos clientes novos.")
    conn.close()
    raise SystemExit(0)

print("\n2) AS LINHAS QUE ABREM CLIENTE (por quantas oficinas levaram na estreia)")
print(f"   {'LINHA':<24}{'OFICINAS':>9}{'% DOS NOVOS':>13}{'PREÇO MÉDIO':>14}")
for l in d["lines"]:
    print(f"   {l['name'][:23]:<24}{l['clients']:>9}{l['sharePct']:>12.1f}%"
          f"{backend.brl(l['unitPrice']):>14}")

print("\n3) AS PEÇAS QUE ABREM CLIENTE")
print(f"   {'REFERÊNCIA':<17}{'MARCA':<13}{'LINHA':<16}{'OFIC':>6}{'PREÇO':>11}  LOJA")
for i in d["items"]:
    loja = "—" if i.get("inStock") is None else ("tem" if i["inStock"] else "SEM")
    print(f"   {i['name'][:16]:<17}{str(i.get('brand', ''))[:12]:<13}"
          f"{str(i.get('line', ''))[:15]:<16}{i['clients']:>6}"
          f"{backend.brl(i['unitPrice']):>11}  {loja}")

print("\n4) LEITURA")
top = d["lines"][0]
print(f"   {top['sharePct']:.0f}% das oficinas novas levaram {top['name']} na primeira compra.")
print("   Se as linhas do topo fizerem sentido como porta de entrada, a régua está boa.")
print("   Se aparecer peça cara e rara no topo, a janela de primeira compra está larga")
print("   demais — está medindo relacionamento, não abertura.")

conn.close()
