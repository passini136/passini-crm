"""
Rastreia um cliente pela carteira e diz EXATAMENTE onde ele some.

Uso no servidor:
    /srv/passini/venv/crm/bin/python /srv/passini/apps/crm-comercial/diag_carteira.py 99856

A carteira passa por cinco estágios até chegar na tela. Este script percorre os
cinco com o código informado e mostra em qual deles o cliente é descartado.
Não altera nada no banco.
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
    print("Informe o código do cliente. Ex: diag_carteira.py 99856")
    sys.exit(1)

codigo = backend.normalize_whitespace(sys.argv[1])
conn = backend.get_connection()
company_id = conn.execute("SELECT id FROM companies LIMIT 1").fetchone()["id"]
print(f"Banco: {backend.DB_PATH}\nRastreando o cliente {codigo}\n")

# ── 1. Cadastro ──────────────────────────────────────────────────────────
perfil = conn.execute(
    "SELECT * FROM crm_client_profiles WHERE company_id = ? AND TRIM(client_code) = ?",
    (company_id, codigo),
).fetchone()
print("1) CADASTRO DE CLIENTES")
if not perfil:
    print("   NÃO ESTÁ no cadastro. A carteira não tem como mostrá-lo.")
    sys.exit(0)
vendedor = (backend.normalize_whitespace(perfil["internal_seller_name"])
            or backend.normalize_whitespace(perfil["external_seller_name"]))
print(f"   OK · {perfil['client_name']}")
print(f"   cidade={perfil['city_name']} · bairro={perfil['neighborhood']} · vendedor={vendedor or '— SEM VENDEDOR —'}")

# ── 2. Competência corrente e faturamento ────────────────────────────────
competencia = backend.crm_summary_latest_competence(conn, company_id)
print(f"\n2) COMPETÊNCIA CORRENTE DA CARTEIRA: {competencia}")
resumo = conn.execute(
    "SELECT competence, net_value, seller_name FROM crm_client_summary "
    "WHERE company_id = ? AND client_code = ? ORDER BY competence DESC LIMIT 5",
    (company_id, codigo),
).fetchall()
if resumo:
    for r in resumo:
        print(f"   resumo {r['competence']}: R$ {r['net_value']:.2f} · {r['seller_name']}")
else:
    print("   sem linha em crm_client_summary (normal para quem não comprou no mês)")

# ── 3. Unidade resolvida ─────────────────────────────────────────────────
mapa_vend = backend.build_seller_unit_map(conn, company_id, competencia)
mapa_terr = backend.build_territory_map(conn, company_id, competencia)
mapa_cid = backend.build_city_unit_map(conn, company_id, competencia)
unidade = backend.unit_for_client_row(
    vendedor, perfil["city_name"], perfil["neighborhood"], mapa_vend, mapa_terr, mapa_cid)
print(f"\n3) UNIDADE RESOLVIDA: {unidade}")
if vendedor:
    chave = backend.person_key(vendedor)
    print(f"   pelo vendedor {vendedor!r} (chave {chave!r}) -> "
          f"{mapa_vend.get(chave) or mapa_vend.get(backend.short_person_key(vendedor)) or 'SEM UNIDADE no cadastro de pessoas'}")
else:
    print("   sem vendedor: vale o território (bairro, depois cidade)")

# ── 4. A carteira monta a linha? ─────────────────────────────────────────
print("\n4) LINHA NA CARTEIRA")
filtros = backend.build_filters_from_query({})
linhas = backend.crm_base_client_rows(conn, company_id, filtros)
achado = next((l for l in linhas if backend.normalize_whitespace(l.get("clientKey")) == codigo), None)
print(f"   a carteira tem {len(linhas)} linha(s) no total")
if not achado:
    print("   >> O CLIENTE NÃO ENTRA NA CARTEIRA. Causas possíveis:")
    print("      - código duplicado: o faturamento foi atribuído a outro código do mesmo nome")
    dup = conn.execute(
        "SELECT client_code, client_name FROM crm_client_profiles "
        "WHERE company_id = ? AND UPPER(client_name) = ?",
        (company_id, backend.normalize_upper(perfil["client_name"])),
    ).fetchall()
    if len(dup) > 1:
        print(f"      >> ENCONTRADO: {len(dup)} códigos com o mesmo nome: "
              f"{[d['client_code'] for d in dup]}")
        print("         A carteira elege UM dono do faturamento por nome; os demais são ocultados.")
    sys.exit(0)
print(f"   OK · unidade={achado.get('unitName')} · vendedor={achado.get('assignedSeller')} "
      f"· status={achado.get('statusCode')} · compra no mês=R$ {achado.get('currentRevenue', 0):.2f}")
if achado.get("duplicateOfCode"):
    print(f"   ATENÇÃO: marcado como duplicata de {achado['duplicateOfCode']}")

# ── 5. Filtros da tela ───────────────────────────────────────────────────
print("\n5) FILTROS DA TELA")
for rotulo, filtro in [
    ("busca pelo código", {"search": codigo}),
    ("unidade da própria linha", {"unit_name": achado.get("unitName") or ""}),
    ("vendedor da própria linha", {"seller_name": achado.get("assignedSeller") or ""}),
]:
    if not list(filtro.values())[0]:
        print(f"   {rotulo:<26} pulado (sem valor)")
        continue
    f = backend.build_filters_from_query({})
    f.update(filtro)
    resultado = backend.list_crm_clients(conn, company_id, f, attach_context=False)
    presente = any(backend.normalize_whitespace(l.get("clientKey")) == codigo for l in resultado)
    print(f"   {rotulo:<26} {'APARECE' if presente else 'SOME'} "
          f"({len(resultado)} linha(s) no resultado)")

print("\nSe aparecer em todos os filtros acima, o problema está na tela (cache do"
      "\nnavegador ou paginação). Ctrl+F5 e teste de novo.")
