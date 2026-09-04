"""
Onde o CRM gasta o tempo, por usuário.

Uso:
    /srv/passini/venv/crm/bin/python /srv/passini/apps/crm-comercial/diag_performance.py

Mede o custo da carteira em dois regimes que se comportam de forma oposta:
frio (ninguém construiu ainda — o primeiro do dia paga) e quente (a base já
está em memória — todos os outros pegam de graça). Confundir os dois faz
otimizar o que já está rápido.

Também confere se o recorte por unidade continua correto depois de a base ter
virado compartilhada: as fatias precisam ser disjuntas e caber no total.

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
print(f"Banco: {backend.DB_PATH}\n")


def cronometrar(funcao):
    inicio = time.time()
    resultado = funcao()
    return resultado, time.time() - inicio


# ── 1. A construção da base, do zero ─────────────────────────────────────────
print("1) CONSTRUÇÃO DA BASE (frio — o primeiro usuário do dia paga isto)")
backend.invalidate_crm_cache(company_id)
diretor = conn.execute(
    "SELECT * FROM users WHERE company_id = ? AND COALESCE(is_active,1)=1 "
    "ORDER BY CASE role WHEN 'Diretor' THEN 0 WHEN 'Administrador' THEN 1 ELSE 2 END LIMIT 1",
    (company_id,),
).fetchone()
filtros_dir = backend.crm_scoped_filters_for_user(
    conn, company_id, diretor, backend.build_filters_from_query({}))
base, seg = cronometrar(
    lambda: backend.crm_base_client_rows_cached(conn, company_id, filtros_dir))
print(f"   {len(base)} clientes em {seg:.1f}s")
print("   (a quebra por etapa saiu acima, na linha [carteira])\n")

# ── 2. O mesmo, quente ───────────────────────────────────────────────────────
print("2) A MESMA BASE, JÁ EM MEMÓRIA (todos os outros usuários)")
_, seg_quente = cronometrar(
    lambda: backend.crm_base_client_rows_cached(conn, company_id, filtros_dir))
print(f"   {seg_quente * 1000:.0f} ms")
if seg > 0.5:
    print(f"   Economia por usuário que chega depois: {seg - seg_quente:.1f}s\n")
else:
    print()

# ── 3. Cada gestor, com a base quente ────────────────────────────────────────
print("3) CADA GESTOR, COM A BASE QUENTE")
print(f"   {'LOGIN':<16}{'UNIDADE':<16}{'CLIENTES':>9}{'CARTEIRA':>10}{'RESUMO':>9}{'LISTA':>9}")
fatias: dict[str, set] = {}
for u in conn.execute(
    "SELECT * FROM users WHERE company_id = ? AND COALESCE(is_active,1)=1 "
    "AND role <> 'Vendedor' ORDER BY username",
    (company_id,),
).fetchall():
    filtros = backend.crm_scoped_filters_for_user(
        conn, company_id, u, backend.build_filters_from_query({}))
    unidade = backend.normalize_unit(filtros.get("unit_name")) or "(todas)"
    linhas, t_carteira = cronometrar(
        lambda: backend.crm_client_rows_for_scope(conn, company_id, filtros))
    _, t_resumo = cronometrar(
        lambda: backend.crm_summary_for_user(conn, company_id, u, filtros))
    _, t_lista = cronometrar(
        lambda: backend.list_crm_clients(conn, company_id, filtros, 50, stats={}))
    fatias[u["username"]] = {r["clientKey"] for r in linhas}
    alerta = "  << LENTO" if max(t_resumo, t_lista) > 2 else ""
    print(f"   {u['username'][:15]:<16}{unidade[:15]:<16}{len(linhas):>9}"
          f"{t_carteira:>9.2f}s{t_resumo:>8.2f}s{t_lista:>8.2f}s{alerta}")

# ── 4. O recorte continua correto? ───────────────────────────────────────────
print("\n4) CONFERÊNCIA DO RECORTE (a base virou compartilhada — as fatias mudaram?)")
gerentes = {k: v for k, v in fatias.items() if v and len(v) < len(base)}
sobreposto = False
nomes = sorted(gerentes)
for i, a in enumerate(nomes):
    for b in nomes[i + 1:]:
        comum = gerentes[a] & gerentes[b]
        if comum:
            sobreposto = True
            print(f"   >> {a} e {b} compartilham {len(comum)} cliente(s) — unidades deveriam ser disjuntas")
if not sobreposto and gerentes:
    soma = sum(len(v) for v in gerentes.values())
    print(f"   Fatias disjuntas. {soma} clientes distribuídos de {len(base)} na base.")
    print(f"   Os {len(base) - soma} restantes são de unidades sem gerente ativo ou sem unidade resolvida.")
elif not gerentes:
    print("   Nenhum gestor com recorte de unidade para conferir.")

conn.close()
