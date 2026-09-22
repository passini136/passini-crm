"""
O log de atividade está crescendo demais? E cada um vê só o que deve?

Uso:
    /srv/passini/venv/crm/bin/python /srv/passini/apps/crm-comercial/diag_atividade.py

Duas perguntas, e as duas só o dado real responde:

1. VOLUME. Toda abertura de ficha grava. A régua é uma linha por pessoa +
   cliente + DIA, justamente para o vendedor que abre a mesma oficina vinte
   vezes não gerar vinte linhas. Se o crescimento diário passar de alguns
   milhares, a régua está errada e o banco vai inchar em silêncio.

2. PERMISSÃO. A tela segue a hierarquia: vendedor vê o próprio, gerente vê a
   unidade dele, diretoria vê tudo. Isso é fácil de errar e difícil de
   perceber — ninguém reclama de ver dados demais. Aqui cada conta ativa é
   simulada e o resultado é conferido contra o que ela deveria ver.

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
print(f"Banco: {backend.DB_PATH}\n")

# ── 1. Volume ───────────────────────────────────────────────────────────────
print("1) QUANTO O LOG ESTÁ GRAVANDO")
total = conn.execute("SELECT COUNT(*) c FROM client_views WHERE company_id = ?",
                     (company_id,)).fetchone()["c"]
aberturas = conn.execute("SELECT COALESCE(SUM(views),0) c FROM client_views "
                         "WHERE company_id = ?", (company_id,)).fetchone()["c"]
print(f"   {total} linha(s) representando {aberturas} abertura(s) de ficha")
if total:
    print(f"   A régua de 1 linha por pessoa/cliente/dia economizou "
          f"{aberturas - total} linha(s).")
por_dia = conn.execute(
    "SELECT view_date, COUNT(*) linhas, COUNT(DISTINCT user_id) pessoas, "
    "COALESCE(SUM(views),0) aberturas FROM client_views WHERE company_id = ? "
    "GROUP BY view_date ORDER BY view_date DESC LIMIT 14", (company_id,)).fetchall()
if por_dia:
    print(f"\n   {'DIA':<12}{'LINHAS':>8}{'PESSOAS':>9}{'ABERTURAS':>11}")
    for r in por_dia:
        print(f"   {r['view_date']:<12}{r['linhas']:>8}{r['pessoas']:>9}{r['aberturas']:>11}")
    pico = max(r["linhas"] for r in por_dia)
    print(f"\n   Pico de {pico} linhas/dia → ~{pico * 365 // 1000}k linhas/ano.")
    if pico > 3000:
        print("   >> ALTO. Vale guardar só os últimos meses ou agregar por semana.")
    else:
        print("   >> Volume tranquilo para SQLite.")
else:
    print("   Ainda sem registros — a tela acabou de entrar no ar.")

# ── 2. Acessos ──────────────────────────────────────────────────────────────
print("\n2) ACESSOS REGISTRADOS")
logins = conn.execute("SELECT COUNT(*) c FROM login_events WHERE company_id = ?",
                      (company_id,)).fetchone()["c"]
print(f"   {logins} login(s) gravado(s)")
for r in conn.execute(
    "SELECT person_name, COUNT(*) n, MAX(logged_at) ultimo FROM login_events "
    "WHERE company_id = ? GROUP BY user_id ORDER BY ultimo DESC LIMIT 15",
        (company_id,)).fetchall():
    print(f"   {str(r['person_name'])[:28]:<30}{r['n']:>4} entrada(s) · "
          f"último {str(r['ultimo'])[:16]}")

# ── 3. Cada um vê só o que deve? ────────────────────────────────────────────
# A pergunta que ninguém faz sozinho: quem está vendo demais. Vazamento de
# permissão não gera reclamação — só aparece quando já causou problema.
print("\n3) O QUE CADA CONTA ENXERGA")
print(f"   {'CONTA':<24}{'PERFIL':<14}{'ESCOPO':<10}{'PESSOAS':>8}{'FICHAS':>8}  SITUAÇÃO")
problemas = 0
for u in conn.execute(
    "SELECT * FROM users WHERE company_id = ? AND is_active = 1 ORDER BY role, username",
        (company_id,)).fetchall():
    try:
        acesso = backend.crm_access_log(conn, company_id, u)
        feed = backend.client_activity_feed(conn, company_id, u, dias=30)
    except Exception as erro:  # noqa: BLE001
        print(f"   {u['username'][:23]:<24}ERRO: {erro}")
        problemas += 1
        continue
    modo = acesso["scope"]
    n_pessoas, n_fichas = len(acesso["people"]), len(feed["items"])
    situacao = "ok"
    # Vendedor só pode ver a si mesmo. Um número maior que 1 aqui é vazamento.
    if modo == "proprio" and n_pessoas > 1:
        situacao = f"VAZOU — vendedor vendo {n_pessoas} pessoas"
        problemas += 1
    # Gerente não pode enxergar a empresa toda.
    if modo == "unidade":
        unidades = {p["unitName"] for p in acesso["people"] if p["unitName"]}
        if len(unidades) > 2:
            situacao = f"VAZOU — gerente vendo {len(unidades)} unidades"
            problemas += 1
    print(f"   {u['username'][:23]:<24}{str(u['role'])[:13]:<14}{modo:<10}"
          f"{n_pessoas:>8}{n_fichas:>8}  {situacao}")

print(f"\n   {problemas} problema(s) de permissão")
if problemas == 0:
    print("   >> Hierarquia respeitada em todas as contas ativas.")
else:
    print("   >> CORRIGIR ANTES DE ANUNCIAR A TELA PARA A EQUIPE.")

conn.close()
