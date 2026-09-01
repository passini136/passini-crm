"""
Por que o usuário não enxerga os dados dele.

Uso no servidor:
    /srv/passini/venv/crm/bin/python /srv/passini/apps/crm-comercial/diag_usuario.py MARCELO.SANTOS
    /srv/passini/venv/crm/bin/python /srv/passini/apps/crm-comercial/diag_usuario.py       (lista todos)

O usuário do CRM e o vendedor do Alfa são duas coisas diferentes, ligadas por um
NOME. Quando o nome muda de um lado e não do outro — "(VENDAS)" que vira
"(TELEVENDAS)", casamento, apelido — o vínculo se rompe em silêncio: a tela não
dá erro, só fica vazia.

Este script mostra, para cada usuário, com que nome ele está vinculado e se esse
nome existe no faturamento, no cadastro de clientes e na lista de pessoas.

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

procurado = " ".join(a for a in sys.argv[1:] if not a.startswith("-")).strip().upper()

conn = backend.get_connection()
company_id = conn.execute("SELECT id FROM companies LIMIT 1").fetchone()["id"]
comp = backend.crm_latest_competence(conn, company_id) or ""

print(f"Banco: {backend.DB_PATH}")
print(f"Competência de referência: {comp}\n")

# ── Os nomes que existem em cada fonte ───────────────────────────────────
faturamento = [r["seller_name"] for r in conn.execute(
    "SELECT DISTINCT seller_name FROM fact_vendor_summary WHERE company_id = ? AND competence = ?",
    (company_id, comp)).fetchall()]
detalhado = [r["seller_name"] for r in conn.execute(
    "SELECT DISTINCT seller_name FROM fact_sales_detail WHERE company_id = ? AND competence = ?",
    (company_id, comp)).fetchall()]
carteira = [r["v"] for r in conn.execute(
    "SELECT DISTINCT internal_seller_name AS v FROM crm_client_profiles "
    "WHERE company_id = ? AND TRIM(COALESCE(internal_seller_name,'')) <> ''",
    (company_id,)).fetchall()]
pessoas = [r["person_name"] for r in conn.execute(
    "SELECT DISTINCT person_name FROM people_records WHERE company_id = ?",
    (company_id,)).fetchall()]


def indice(nomes):
    """Nome real por chave normalizada — é assim que o sistema deveria casar."""
    mapa = {}
    for n in nomes:
        mapa.setdefault(backend.person_key(n), []).append(n)
    return mapa


idx = {"faturamento": indice(faturamento), "detalhado": indice(detalhado),
       "carteira": indice(carteira), "lista de pessoas": indice(pessoas)}

usuarios = conn.execute(
    "SELECT id, username, full_name, linked_person_name, is_active "
    "FROM users WHERE company_id = ? ORDER BY username", (company_id,)).fetchall()
if procurado:
    usuarios = [u for u in usuarios
                if procurado in (u["username"] or "").upper()
                or procurado in (u["full_name"] or "").upper()
                or procurado in (u["linked_person_name"] or "").upper()]
if not usuarios:
    print("Nenhum usuário encontrado com esse texto.")
    conn.close()
    sys.exit(0)

problemas = 0
for u in usuarios:
    vinculo = backend.normalize_whitespace(u["linked_person_name"] or "")
    usado = vinculo or backend.normalize_whitespace(u["full_name"] or u["username"])
    chave = backend.person_key(usado)
    print(f"── {u['username']}{'' if u['is_active'] else '  (INATIVO)'}")
    print(f"   nome do cadastro : {u['full_name'] or '—'}")
    print(f"   vinculado a      : {vinculo or '(nenhum — usa o nome do cadastro)'}")
    print(f"   chave de busca   : {chave or '(vazia)'}")
    ruim = False
    for fonte, mapa in idx.items():
        exatos = [n for n in mapa.get(chave, []) if n == usado]
        equivalentes = [n for n in mapa.get(chave, []) if n != usado]
        if exatos:
            situacao = "OK (nome idêntico)"
        elif equivalentes:
            # É o caso do "(TELEVENDAS)": a pessoa existe, o nome mudou, e a
            # consulta por nome exato não acha. A tela fica vazia sem erro.
            situacao = f">> NOME DIFERENTE: a base tem '{equivalentes[0]}'"
            ruim = True
        else:
            situacao = ">> NÃO EXISTE nesta fonte"
            ruim = True
        print(f"      {fonte:<18}{situacao}")
    if ruim:
        problemas += 1
        # Sugere o nome certo a partir da fonte mais confiável que tiver achado.
        for fonte in ("faturamento", "detalhado", "carteira"):
            achados = idx[fonte].get(chave, [])
            if achados:
                print(f"      >> Vincule este usuário a: {achados[0]}")
                break
    print()

print(f"{problemas} usuário(s) com vínculo quebrado de {len(usuarios)} analisado(s).")
if problemas:
    print("\nO vínculo é por NOME EXATO. Quando o Alfa muda o nome do vendedor")
    print("(acrescenta (TELEVENDAS), corrige grafia), o usuário para de enxergar")
    print("os próprios dados — sem mensagem de erro, só telas vazias.")
    print("Ajuste em Usuários e Perfis, no campo de pessoa vinculada.")

conn.close()
