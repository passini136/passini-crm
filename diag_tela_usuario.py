"""
Reproduz, no servidor, as telas que um usuário carrega ao entrar.

Uso:
    /srv/passini/venv/crm/bin/python /srv/passini/apps/crm-comercial/diag_tela_usuario.py RONI

Quando a tela fica presa em "Carregando…", há dois suspeitos e eles pedem
remédios opostos: ou o servidor demorou, ou o servidor quebrou. Este script
chama as mesmas funções que os endpoints chamam, com o usuário de verdade,
cronometra cada uma e imprime o traceback inteiro se alguma estourar.

Não altera nada.
"""
import json
import os
import sys
import time
import traceback
from pathlib import Path

sys.path.insert(0, "/srv/passini/apps/crm-comercial")

if not os.environ.get("PASSINI_CRM_DATA"):
    for candidate in ("/srv/passini/data/crm", "/srv/passini/data"):
        if (Path(candidate) / "passini_dashboard.db").exists():
            os.environ["PASSINI_CRM_DATA"] = candidate
            break

import backend  # noqa: E402

todos = "--todos" in sys.argv
procurado = " ".join(a for a in sys.argv[1:] if not a.startswith("-")).strip()
if not procurado and not todos:
    print("Informe o login (diag_tela_usuario.py RONI) ou use --todos para varrer todo mundo.")
    raise SystemExit(1)

conn = backend.get_connection()
company_id = conn.execute("SELECT id FROM companies LIMIT 1").fetchone()["id"]

if todos:
    # Varredura de permissão. A maioria dos defeitos deste sistema aparece só
    # para quem tem escopo restrito — testar com a conta da diretoria, que vê
    # tudo, não exercita nenhum dos filtros. Aqui roda o caminho de permissão
    # de CADA conta ativa, de graça: são as chamadas baratas, sem os relatórios
    # pesados. Se uma linha marcar ✘, aquele perfil está com a tela quebrada.
    print("VARREDURA — caminho de permissão de cada conta ativa\n")
    print(f"  {'LOGIN':<16}{'PERFIL':<16}{'ESCOPO':<22}RESULTADO")
    problemas = 0
    for u in conn.execute(
        "SELECT * FROM users WHERE company_id = ? AND COALESCE(is_active,1) = 1 ORDER BY username",
        (company_id,),
    ).fetchall():
        try:
            escopo_u = backend.data_scope_for_user(conn, u)
            backend.crm_scoped_filters_for_user(
                conn, company_id, u, backend.build_filters_from_query({}))
            pessoas = backend.task_assignable_people(conn, company_id, u)
            backend.task_visible_sellers(conn, company_id, u)
            backend.crm_task_counters(conn, company_id, u)
            backend.list_meeting_people(conn, company_id, u)
            resultado = f"✔ ok · {len(pessoas)} pessoa(s) visível(is)"
        except Exception as exc:
            problemas += 1
            escopo_u = "?"
            resultado = f"✘ {type(exc).__name__}: {exc}"
        print(f"  {u['username'][:15]:<16}{(u['role'] or '')[:15]:<16}{str(escopo_u)[:21]:<22}{resultado}")
    print(f"\n  {problemas} conta(s) com problema.")
    if not problemas:
        print("  Todo perfil monta as telas. Diferença entre perfis costuma ser aqui.")
    conn.close()
    raise SystemExit(0)
user = conn.execute(
    "SELECT * FROM users WHERE company_id = ? AND UPPER(username) = ?",
    (company_id, procurado.upper()),
).fetchone()
if not user:
    print(f"Login '{procurado}' não encontrado.")
    raise SystemExit(1)

escopo = backend.data_scope_for_user(conn, user)
permitidas = backend.crm_allowed_units_for_user(conn, user)
print(f"Banco: {backend.DB_PATH}")
print(f"Usuário: {user['username']} · {user['full_name'] or '(sem nome)'} · {user['role']}")
print(f"Escopo de dados....: {escopo}")
print(f"Unidades permitidas: {', '.join(sorted(permitidas)) if permitidas else 'TODAS'}")
print(f"Vinculado a........: {user['linked_person_name'] or '(ninguém)'}\n")

filtros = backend.crm_scoped_filters_for_user(
    conn, company_id, user, backend.build_filters_from_query({}))
print(f"Filtros aplicados: {filtros}\n")

falhou = False


def etapa(rotulo, funcao):
    """Roda uma etapa medindo tempo e tamanho, sem deixar exceção escapar."""
    global falhou
    inicio = time.time()
    try:
        resultado = funcao()
    except Exception:
        falhou = True
        print(f"  ✘ {rotulo:<26} QUEBROU em {time.time() - inicio:.1f}s")
        print("─" * 78)
        traceback.print_exc()
        print("─" * 78 + "\n")
        return None
    duracao = time.time() - inicio
    try:
        # O navegador precisa conseguir ler o JSON. Um valor não-finito aqui
        # derruba o JSON.parse do lado de lá e a tela trava sem erro nenhum
        # no servidor — já aconteceu, e custou horas.
        bruto = backend.json_dumps(resultado)
        tamanho = f"{len(bruto) / 1024:.0f} KB"
        json.loads(bruto)
        aviso = ""
    except Exception as exc:
        falhou = True
        tamanho = "?"
        aviso = f"   << JSON INVÁLIDO: {exc}"
    alerta = "  << LENTO" if duracao > 5 else ""
    print(f"  {'✔' if not aviso else '✘'} {rotulo:<26}{duracao:>7.1f}s  {tamanho:>9}{alerta}{aviso}")
    return resultado


print("AS TRÊS CHAMADAS QUE A CARTEIRA FAZ AO ABRIR")
etapa("/api/crm/summary", lambda: backend.crm_summary_for_user(conn, company_id, user, filtros))
etapa("/api/crm/agenda", lambda: backend.list_crm_clients(
    conn, company_id, filtros, 20, exclude_contacted_today=True, stats={}))
etapa("/api/crm/tasks · rows", lambda: backend.list_crm_tasks(conn, company_id, user, status="ABERTAS"))
etapa("/api/crm/tasks · contadores", lambda: backend.crm_task_counters(conn, company_id, user))
etapa("/api/crm/tasks · pessoas", lambda: backend.task_assignable_people(conn, company_id, user))
etapa("/api/crm/tasks · vendedores", lambda: backend.task_visible_sellers(conn, company_id, user))

print("\nA LISTA DE CLIENTES (carregada logo depois, em segundo plano)")
etapa("/api/crm/clients", lambda: backend.list_crm_clients(conn, company_id, filtros, 50, stats={}))

print("\nLEITURA")
if falhou:
    print("  >> Alguma etapa quebrou ou devolveu JSON ilegível. É por isso que a tela")
    print("     fica em 'Carregando…': o navegador não recebe resposta utilizável.")
    print("     O traceback acima aponta a linha exata.")
else:
    print("  Nenhuma etapa quebrou. Se a tela ainda não carrega, o problema não está")
    print("  no cálculo: veja os tempos acima e o console do navegador (F12 → Console).")

conn.close()
