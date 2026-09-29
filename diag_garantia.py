"""
A devolução em garantia está sendo deduzida do vendedor?

Uso:
    /srv/passini/venv/crm/bin/python /srv/passini/apps/crm-comercial/diag_garantia.py
    /srv/passini/venv/crm/bin/python /srv/passini/apps/crm-comercial/diag_garantia.py 2026-08

Garantia é defeito de peça, não erro de venda: sai do resultado comercial do
vendedor. A conta existe, mas depende de casar o nome entre DOIS arquivos
diferentes do Alfa — o relatório de devoluções e o custo × venda. Quando o nome
sai escrito de jeitos diferentes, a dedução acha zero e o vendedor leva a
garantia como se fosse devolução comercial dele: nota baixa no farol e ponto
perdido na premiação, sem explicação visível.

O que conferir: a coluna CASOU. Garantia órfã é garantia que está pesando contra
alguém que não errou nada.

Não altera nada.
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

conn = backend.get_connection()
company_id = conn.execute("SELECT id FROM companies LIMIT 1").fetchone()["id"]
comp = (sys.argv[1] if len(sys.argv) > 1
        else backend.crm_latest_competence(conn, company_id))

print(f"Banco: {backend.DB_PATH}")
print(f"Competência: {comp}\n")

# ── 1. Tem devolução importada? ─────────────────────────────────────────────
print("1) DEVOLUÇÕES DA COMPETÊNCIA")
for r in conn.execute(
    f"SELECT {backend.RETURN_KIND_SQL} tipo, COUNT(*) n, "
    f"ROUND(SUM(total_value),2) valor FROM fact_warranty_returns "
    f"WHERE company_id = ? AND competence = ? GROUP BY tipo",
        (company_id, comp)).fetchall():
    print(f"   {r['tipo']:<12}{r['n']:>6} linha(s)   {backend.brl(r['valor'])}")
garantia_total = conn.execute(
    "SELECT COALESCE(SUM(total_value),0) v FROM fact_warranty_returns "
    "WHERE company_id = ? AND competence = ? AND reason = ?",
    (company_id, comp, backend.RETURN_REASON_WARRANTY)).fetchone()["v"]
if not garantia_total:
    print("\n   Nenhuma garantia nesta competência — nada a deduzir.")
    conn.close()
    raise SystemExit(0)

# ── 2. O nome casa entre os dois arquivos? ──────────────────────────────────
# Esta é a pergunta que decide se a dedução funciona. Os dois lados vêm de
# arquivos diferentes do Alfa e não há garantia de que escrevam igual.
print("\n2) O NOME CASA ENTRE OS DOIS ARQUIVOS?")
do_custo = {
    backend.chave_canonica(conn, company_id, backend.normalize_whitespace(r["seller_name"]))
    for r in conn.execute(
        "SELECT DISTINCT seller_name FROM fact_vendor_summary "
        "WHERE company_id = ? AND competence = ?", (company_id, comp)).fetchall()
    if r["seller_name"]
}
print(f"   {'VENDEDOR NA GARANTIA':<34}{'VALOR':>14}  CASOU?")
casado = orfao = 0.0
for r in conn.execute(
    "SELECT seller_name, ROUND(SUM(total_value),2) v FROM fact_warranty_returns "
    "WHERE company_id = ? AND competence = ? AND reason = ? "
    "GROUP BY seller_name ORDER BY v DESC",
        (company_id, comp, backend.RETURN_REASON_WARRANTY)).fetchall():
    nome = backend.normalize_whitespace(r["seller_name"])
    bate = backend.chave_canonica(conn, company_id, nome) in do_custo
    if bate:
        casado += float(r["v"] or 0)
    else:
        orfao += float(r["v"] or 0)
    print(f"   {nome[:33]:<34}{backend.brl(r['v']):>14}  {'sim' if bate else 'NÃO'}")

pct = 100 * orfao / (casado + orfao) if (casado + orfao) else 0
print(f"\n   Casou: {backend.brl(casado)}   ·   Órfã: {backend.brl(orfao)} ({pct:.0f}%)")
if orfao > 0:
    print("   >> Essa parte NÃO é deduzida: está pesando como devolução comercial")
    print("      contra vendedores que não têm culpa. Associe as grafias em")
    print("      Administração → Equipe, botão 🔗.")
else:
    print("   >> Toda a garantia está sendo deduzida corretamente.")

# ── 3. Efeito no indicador ──────────────────────────────────────────────────
print("\n3) EFEITO NO % DE DEVOLUÇÃO")
print(f"   {'VENDEDOR':<28}{'TOTAL DEV.':>13}{'GARANTIA':>12}{'COMERCIAL':>12}{'% s/ LÍQ.':>11}")
for r in conn.execute(
    "SELECT seller_name, ROUND(SUM(return_value),2) dev, ROUND(SUM(net_value),2) liq "
    "FROM fact_vendor_summary WHERE company_id = ? AND competence = ? "
    "GROUP BY seller_name HAVING dev > 0 ORDER BY dev DESC LIMIT 15",
        (company_id, comp)).fetchall():
    nome = backend.normalize_whitespace(r["seller_name"])
    chave = backend.chave_canonica(conn, company_id, nome)
    gar = conn.execute(
        "SELECT COALESCE(SUM(total_value),0) v FROM fact_warranty_returns "
        "WHERE company_id = ? AND competence = ? AND reason = ?",
        (company_id, comp, backend.RETURN_REASON_WARRANTY)).fetchone()
    # Garantia da PESSOA, resolvendo grafia
    gar_pessoa = 0.0
    for g in conn.execute(
        "SELECT seller_name, SUM(total_value) v FROM fact_warranty_returns "
        "WHERE company_id = ? AND competence = ? AND reason = ? GROUP BY seller_name",
            (company_id, comp, backend.RETURN_REASON_WARRANTY)).fetchall():
        if backend.chave_canonica(conn, company_id,
                                  backend.normalize_whitespace(g["seller_name"])) == chave:
            gar_pessoa += float(g["v"] or 0)
    dev = float(r["dev"] or 0)
    liq = float(r["liq"] or 0)
    gar_pessoa = min(gar_pessoa, dev)
    comercial = max(dev - gar_pessoa, 0.0)
    pct_c = (100 * comercial / (liq + gar_pessoa)) if (liq + gar_pessoa) else 0
    print(f"   {nome[:27]:<28}{backend.brl(dev):>13}{backend.brl(gar_pessoa):>12}"
          f"{backend.brl(comercial):>12}{pct_c:>10.2f}%")
print("\n   A coluna COMERCIAL é a que vale para o farol e para a premiação.")

conn.close()
