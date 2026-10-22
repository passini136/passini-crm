"""
Onde a tela de Cotações perde o tempo?

Uso (venv do CRM):
    /srv/passini/venv/crm/bin/python /srv/passini/apps/crm-comercial/diag_cotacoes_lenta.py HEIDER

POR QUE ESTE DIAGNÓSTICO EXISTE

A correção de ontem fez a carteira voltar a aparecer, mas a tela ficou lenta.
O custo é meu e eu sei qual é a suspeita: `seller_name_variants` varre NOVE
tabelas — incluindo o faturamento, com mais de 250 mil linhas — e eu passei a
chamá-la em toda requisição do módulo. Antes ela não era chamada ali.

Mas suspeita não é medida. Há três candidatos, e otimizar o errado deixa a
tela lenta e o código pior:

  1. `seller_name_variants` (as nove varreduras).
  2. `sem_acento(coluna)` na comparação: função Python chamada uma vez POR
     LINHA, o que impede qualquer índice e transforma a consulta numa
     varredura de 102 mil perfis.
  3. A própria consulta da carteira, por falta de índice.

O script cronometra os três separadamente e compara a consulta como está hoje
com a versão sem função na coluna. A diferença entre as duas é o ganho que a
correção pode render.

NÃO ALTERA NADA.
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

procurado = (sys.argv[1] if len(sys.argv) > 1 else "HEIDER").upper()
conn = backend.get_connection()
cid = conn.execute("SELECT id FROM companies LIMIT 1").fetchone()["id"]

user = next((r for r in conn.execute(
    "SELECT * FROM users WHERE company_id = ?", (cid,))
    if procurado in backend.normalize_whitespace(
        f"{r['username']} {r['full_name']} {r['linked_person_name']}").upper()), None)
if user is None:
    print(f"Nenhum usuário com '{procurado}'.")
    sys.exit(1)
vendedor = backend.seller_identity_for_user(user)
print(f"Banco: {backend.DB_PATH}")
print(f"Vendedor: {vendedor!r}\n")

# ── 1. Tamanho das tabelas que são varridas ─────────────────────────────────
print("1) O QUE seller_name_variants VARRE")
print(f"   {'TABELA':<26}{'LINHAS':>12}{'TEMPO':>9}")
total_scan = 0.0
for tabela, coluna in backend.SELLER_NAME_SOURCES:
    try:
        t0 = time.time()
        linhas = conn.execute(
            f"SELECT DISTINCT {coluna} FROM {tabela} WHERE company_id = ?",
            (cid,)).fetchall()
        seg = time.time() - t0
        total_scan += seg
        n = conn.execute(f"SELECT COUNT(*) n FROM {tabela} "
                         f"WHERE company_id = ?", (cid,)).fetchone()["n"]
        print(f"   {tabela + '.' + coluna:<26}{n:>12,}{seg:>8.2f}s")
    except Exception as exc:  # noqa: BLE001
        print(f"   {tabela + '.' + coluna:<26}{'erro':>12}  {exc}")
print(f"   {'SOMA':<26}{'':>12}{total_scan:>8.2f}s")

# ── 2. Quanto custa a função, com e sem cache ───────────────────────────────
print("\n2) seller_name_variants NA PRÁTICA")
conn2 = backend.get_connection()          # conexão nova = cache vazio, como no servidor
t0 = time.time()
variantes = backend.seller_name_variants(conn2, cid, vendedor)
primeira = time.time() - t0
t0 = time.time()
backend.seller_name_variants(conn2, cid, vendedor)
segunda = time.time() - t0
print(f"   1ª chamada (cache frio): {primeira:>6.2f}s")
print(f"   2ª chamada (cache quente): {segunda:>6.2f}s")
print(f"   Grafias encontradas: {variantes}")
print("   >> O servidor abre uma CONEXÃO POR REQUISIÇÃO, então toda chamada")
print("      da tela paga o tempo da 1ª. O cache não atravessa requisições.")

# ── 3. A consulta da carteira: com e sem função na coluna ───────────────────
print("\n3) A CONSULTA DA CARTEIRA")
n_perfis = conn.execute(
    "SELECT COUNT(*) n FROM crm_client_profiles WHERE company_id = ?",
    (cid,)).fetchone()["n"]
print(f"   crm_client_profiles: {n_perfis:,} linha(s)")

marcas = ",".join("sem_acento(?)" for _ in variantes)
t0 = time.time()
com_udf = conn.execute(
    f"SELECT COUNT(*) n FROM crm_client_profiles p WHERE p.company_id = ?"
    f"  AND sem_acento(COALESCE(p.internal_seller_name, '')) IN ({marcas})",
    (cid, *variantes)).fetchone()["n"]
t_udf = time.time() - t0

marcas2 = ",".join("?" for _ in variantes)
t0 = time.time()
sem_udf = conn.execute(
    f"SELECT COUNT(*) n FROM crm_client_profiles p WHERE p.company_id = ?"
    f"  AND p.internal_seller_name IN ({marcas2})",
    (cid, *variantes)).fetchone()["n"]
t_direto = time.time() - t0

marcas3 = ",".join("?" for _ in variantes)
t0 = time.time()
com_trim = conn.execute(
    f"SELECT COUNT(*) n FROM crm_client_profiles p WHERE p.company_id = ?"
    f"  AND TRIM(COALESCE(p.internal_seller_name, '')) IN ({marcas3})",
    (cid, *variantes)).fetchone()["n"]
t_trim = time.time() - t0

print(f"   {'VERSÃO':<34}{'CLIENTES':>10}{'TEMPO':>9}")
print(f"   {'sem_acento(coluna) IN (...)':<34}{com_udf:>10,}{t_udf:>8.2f}s")
print(f"   {'coluna IN (...)':<34}{sem_udf:>10,}{t_direto:>8.2f}s")
print(f"   {'TRIM(coluna) IN (...)  [adotado]':<34}{com_trim:>10,}{t_trim:>8.2f}s")
if com_trim != com_udf:
    print(f"   >> TRIM ACHA {com_trim} E sem_acento ACHA {com_udf}. Trocar perderia")
    print("      cliente — alguma grafia difere por acento ou caixa, não só por")
    print("      espaço. A troca NÃO pode ser feita.")
else:
    print("   >> TRIM acha os mesmos clientes, e sem a função Python por linha.")
if com_udf != sem_udf:
    print(f"   >> CONTAGENS DIFERENTES ({com_udf} x {sem_udf}). A comparação direta")
    print("      perde cliente — alguma grafia do cadastro não está na lista de")
    print("      variantes. Nesse caso NÃO dá para tirar a função.")
else:
    print("   >> Mesma contagem: a função na coluna pode sair sem perder ninguém,")
    print("      porque as variantes JÁ são as grafias que existem na tabela.")

# ── 4. O plano de execução ──────────────────────────────────────────────────
print("\n4) O SQLITE USA ÍNDICE?")
for rotulo, sql, par in (
    ("com sem_acento",
     f"SELECT 1 FROM crm_client_profiles p WHERE p.company_id = ?"
     f" AND sem_acento(COALESCE(p.internal_seller_name,'')) IN ({marcas})",
     (cid, *variantes)),
    ("direto",
     f"SELECT 1 FROM crm_client_profiles p WHERE p.company_id = ?"
     f" AND p.internal_seller_name IN ({marcas2})", (cid, *variantes)),
):
    plano = " | ".join(r["detail"] for r in
                       conn.execute("EXPLAIN QUERY PLAN " + sql, par))
    print(f"   {rotulo:<16}{plano[:92]}")
print("   >> SCAN = varre a tabela inteira. SEARCH ... USING INDEX = usa índice.")

indices = [r["name"] for r in conn.execute(
    "SELECT name FROM sqlite_master WHERE type='index'"
    "   AND tbl_name='crm_client_profiles'")]
print(f"   Índices em crm_client_profiles: {indices or '(nenhum)'}")

# ── 5. A tela inteira, ponta a ponta ────────────────────────────────────────
print("\n5) AS CHAMADAS DA TELA, COMO O SERVIDOR FAZ")
for rotulo, fn in (
    ("carteira (sem busca)",
     lambda c: backend.carteira_para_cotacao(
         c, user, backend._cotacao_contexto(c, user), {})),
    ("carteira (busca 'auto')",
     lambda c: backend.carteira_para_cotacao(
         c, user, backend._cotacao_contexto(c, user), {"q": "auto"})),
    ("listar cotações",
     lambda c: backend.listar_cotacoes(
         c, user, backend._cotacao_contexto(c, user), {})),
):
    c = backend.get_connection()          # conexão nova: igual ao servidor
    t0 = time.time()
    try:
        r = fn(c)
        n = len(r.get("clients", r.get("quotes", [])) or [])
        print(f"   {rotulo:<26}{time.time() - t0:>7.2f}s   {n} item(ns)")
    except Exception as exc:  # noqa: BLE001
        print(f"   {rotulo:<26}{time.time() - t0:>7.2f}s   ERRO: {exc}")
    c.close()
print("   >> Acima de 1s a tela parece travada. O alvo é ficar abaixo disso.")

conn.close()
conn2.close()
print("\nNada foi alterado.")
