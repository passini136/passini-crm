"""
Confere a carteira de um vendedor: cadastro x painel x lista.

Uso no servidor:
    /srv/passini/venv/crm/bin/python /srv/passini/apps/crm-comercial/diag_vendedor.py "ANNA CAROLINA"

Regra da casa: CARTEIRA = clientes com o nome do vendedor na coluna VENDEDOR
INTERNO do cadastro de clientes. Este script parte dessa contagem crua e mostra
onde as telas divergem dela — e por quê. Não altera nada no banco.
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

if len(sys.argv) < 2:
    print('Informe parte do nome. Ex: diag_vendedor.py "ANNA CAROLINA"')
    sys.exit(1)

termo = " ".join(sys.argv[1:]).strip().upper()
conn = backend.get_connection()
company_id = conn.execute("SELECT id FROM companies LIMIT 1").fetchone()["id"]
print(f"Banco: {backend.DB_PATH}\n")

# ── Nome exato como está no cadastro ─────────────────────────────────────
nomes = [r["nome"] for r in conn.execute(
    "SELECT DISTINCT TRIM(internal_seller_name) AS nome FROM crm_client_profiles "
    "WHERE company_id = ? AND UPPER(internal_seller_name) LIKE ? ORDER BY nome",
    (company_id, f"%{termo}%"),
).fetchall() if r["nome"]]

if not nomes:
    print(f"Nenhum vendedor interno com '{termo}' no cadastro de clientes.")
    sys.exit(0)
if len(nomes) > 1:
    print("ATENÇÃO: mais de uma grafia no cadastro — cada uma vira uma carteira separada:")
    for n in nomes:
        qt = conn.execute(
            "SELECT COUNT(*) c FROM crm_client_profiles WHERE company_id = ? AND TRIM(internal_seller_name) = ?",
            (company_id, n)).fetchone()["c"]
        print(f"   {n!r}: {qt} cliente(s)")
    print()

vendedor = nomes[0]
print(f"VENDEDOR: {vendedor!r}\n")

# ── 1. Contagem crua no cadastro (a verdade) ─────────────────────────────
total = conn.execute(
    "SELECT COUNT(*) c FROM crm_client_profiles WHERE company_id = ? AND TRIM(internal_seller_name) = ?",
    (company_id, vendedor),
).fetchone()["c"]
distintos = conn.execute(
    "SELECT COUNT(DISTINCT TRIM(client_code)) c FROM crm_client_profiles "
    "WHERE company_id = ? AND TRIM(internal_seller_name) = ?",
    (company_id, vendedor),
).fetchone()["c"]
print(f"1) CADASTRO DE CLIENTES (vendedor interno = este nome)")
print(f"   {total} linha(s) · {distintos} código(s) distinto(s)")
if total != distintos:
    print("   >> há códigos repetidos no cadastro")

# Mesmo cliente (mesmo CNPJ) com mais de um código
dups = conn.execute(
    """
    SELECT REPLACE(REPLACE(REPLACE(COALESCE(document_number,''),'.',''),'/',''),'-','') AS doc,
           COUNT(*) n, GROUP_CONCAT(client_code) codigos
    FROM crm_client_profiles
    WHERE company_id = ? AND TRIM(internal_seller_name) = ? AND COALESCE(document_number,'') <> ''
    GROUP BY doc HAVING n > 1 ORDER BY n DESC LIMIT 10
    """,
    (company_id, vendedor),
).fetchall()
if dups:
    extras = sum(d["n"] - 1 for d in dups)
    print(f"   >> {len(dups)} CNPJ/CPF com mais de um código ({extras} código(s) a mais):")
    for d in dups[:5]:
        print(f"      {d['doc']}: {d['codigos']}")

# ── 2. Painel (Resumo por Vendedor) ──────────────────────────────────────
usuario = conn.execute(
    "SELECT * FROM users WHERE company_id = ? AND role IN ('Diretor','Administrador') LIMIT 1",
    (company_id,),
).fetchone()
resumo = backend.compute_portfolio_summary_by_seller(conn, company_id, usuario)
linha = next((s for s in resumo["sellers"]
              if backend.person_key(s["sellerName"]) == backend.person_key(vendedor)), None)
print(f"\n2) PAINEL Resumo por Vendedor: {linha['total'] if linha else 'não aparece'}")

# ── 3. Lista de Clientes ─────────────────────────────────────────────────
filtros = backend.build_filters_from_query({})
filtros["seller_name"] = vendedor
lista = backend.list_crm_clients(conn, company_id, filtros, attach_context=False)
print(f"3) LISTA de Clientes: {len(lista)}")

# ── 4. Onde está a diferença ─────────────────────────────────────────────
print("\n4) DIFERENÇA")
codigos_cadastro = {
    backend.normalize_whitespace(r["client_code"]) for r in conn.execute(
        "SELECT client_code FROM crm_client_profiles WHERE company_id = ? AND TRIM(internal_seller_name) = ?",
        (company_id, vendedor)).fetchall()
}
codigos_lista = {backend.normalize_whitespace(l["clientKey"]) for l in lista}
so_na_lista = codigos_lista - codigos_cadastro
so_no_cadastro = codigos_cadastro - codigos_lista

if not so_na_lista and not so_no_cadastro:
    print("   Nenhuma. Cadastro e lista batem.")
else:
    if so_na_lista:
        print(f"   {len(so_na_lista)} na LISTA e não no cadastro dela: {sorted(so_na_lista)[:10]}")
        print("      (cliente veio do faturamento do mês sem estar no cadastro com este vendedor)")
    if so_no_cadastro:
        print(f"   {len(so_no_cadastro)} no CADASTRO e não na lista: {sorted(so_no_cadastro)[:10]}")
        for cod in sorted(so_no_cadastro)[:5]:
            row = next((l for l in lista if l["clientKey"] == cod), None)
            print(f"      {cod}: {'oculto por duplicidade' if row else 'não entrou na carteira'}")

print("\nSe a contagem 1 não bater com o Alfa, o filtro do relatório é diferente")
print("(situação do cliente, por exemplo). A contagem 1 é a verdade para o CRM.")
