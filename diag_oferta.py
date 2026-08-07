"""
Confere como um cliente está sendo classificado nas sugestões de oferta.

Serve para calibrar os parâmetros (janela de recompra, giro na praça, mínimo de
oficinas) olhando um caso concreto em vez de no escuro.

Uso no servidor:
    /srv/passini/venv/crm/bin/python /srv/passini/apps/crm-comercial/diag_oferta.py "THIAGO BATISTA" WO120

O primeiro argumento é parte do nome do cliente; o segundo (opcional) é o código
do item que você quer investigar.
"""
import os
import sys
from pathlib import Path

sys.path.insert(0, "/srv/passini/apps/crm-comercial")

if not os.environ.get("PASSINI_CRM_DATA"):
    for candidate in ("/srv/passini/data/crm", "/srv/passini/data"):
        if (Path(candidate) / "passini_dashboard.db").exists():
            os.environ["PASSINI_CRM_DATA"] = candidate
            break

import backend  # noqa: E402

termo_cliente = sys.argv[1] if len(sys.argv) > 1 else ""
termo_item = sys.argv[2] if len(sys.argv) > 2 else ""

if not termo_cliente:
    print('Informe parte do nome do cliente. Ex.: diag_oferta.py "THIAGO BATISTA" WO120')
    sys.exit(1)

conn = backend.get_connection()
company_id = conn.execute("SELECT id FROM companies LIMIT 1").fetchone()["id"]

print(f"Banco: {backend.DB_PATH}")
print("\nParâmetros em vigor:")
print(f"  Janela de recompra .............. {backend.OFFER_REPURCHASE_WINDOW_MONTHS} meses")
print(f"  Janela do giro na praça ......... {backend.OFFER_PEER_WINDOW_MONTHS} meses")
print(f"  Mínimo de oficinas na cidade .... {backend.OFFER_PEER_MIN_CLIENTS}")
print(f"  Sugestões por tipo .............. {backend.OFFER_MAX_SUGGESTIONS}")

# ── Qual nome exato existe no faturamento ────────────────────────────────
nomes = conn.execute(
    """
    SELECT client_name, city_name, COUNT(*) linhas, SUM(net_value) total
    FROM fact_sales_detail
    WHERE company_id = ? AND UPPER(client_name) LIKE ?
    GROUP BY client_name, city_name
    ORDER BY total DESC
    """,
    (company_id, f"%{termo_cliente.upper()}%"),
).fetchall()

if not nomes:
    print(f"\nNenhum cliente com '{termo_cliente}' no faturamento.")
    sys.exit(0)

print(f"\nNomes encontrados no faturamento ({len(nomes)}):")
for r in nomes:
    print(f"  {r['client_name']!r} · {r['city_name']} · {r['linhas']} linhas · {backend.brl(r['total'] or 0)}")

alvo = nomes[0]
client_name = alvo["client_name"]
city_name = alvo["city_name"]
print(f"\nAnalisando: {client_name!r} ({city_name})")

# ── O item específico ────────────────────────────────────────────────────
if termo_item:
    padrao = f"%{termo_item.upper()}%"
    compras = conn.execute(
        """
        SELECT competence, issue_date, manufacturer_sku, sku_key, gtin_value,
               SUM(quantity) q, SUM(net_value) v
        FROM fact_sales_detail
        WHERE company_id = ? AND client_name = ? AND net_value > 0
          AND (UPPER(COALESCE(manufacturer_sku,'')) LIKE ?
            OR UPPER(COALESCE(sku_key,'')) LIKE ?
            OR UPPER(COALESCE(gtin_value,'')) LIKE ?)
        GROUP BY competence, issue_date, manufacturer_sku, sku_key, gtin_value
        ORDER BY competence
        """,
        (company_id, client_name, padrao, padrao, padrao),
    ).fetchall()
    print(f"\nCompras do item '{termo_item}' por este cliente: {len(compras)}")
    for r in compras:
        print(f"  {r['competence']} · {r['issue_date']} · fab={r['manufacturer_sku']!r} "
              f"sku={r['sku_key']!r} gtin={r['gtin_value']!r} · {r['q']} un · {backend.brl(r['v'] or 0)}")

# ── Como o motor classifica hoje ─────────────────────────────────────────
ofertas = backend.crm_get_offer_suggestions(conn, company_id, client_name, city_name)

print("\nRECOMPRA sugerida:")
for o in ofertas["repurchase"]:
    print(f"  {o['title']:28} {o['reason']}")
if not ofertas["repurchase"]:
    print("  (nenhuma)")

print("\nOPORTUNIDADE sugerida:")
for o in ofertas["opportunity"]:
    print(f"  {o['title']:28} {o['reason']}")
if not ofertas["opportunity"]:
    print("  (nenhuma)")

if termo_item:
    achou = [o for o in ofertas["repurchase"] + ofertas["opportunity"]
             if termo_item.upper() in (o["title"] or "").upper()]
    print(f"\nItem '{termo_item}' nas sugestões: "
          + (", ".join(f"{o['type']} — {o['reason']}" for o in achou) if achou
             else "não aparece (correto se ele já compra o item com frequência)"))
