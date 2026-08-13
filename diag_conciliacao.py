"""
Mostra por que um cliente do faturamento não casou com o cadastro do CRM.

Uso no servidor:
    /srv/passini/venv/crm/bin/python /srv/passini/apps/crm-comercial/diag_conciliacao.py
    /srv/passini/venv/crm/bin/python /srv/passini/apps/crm-comercial/diag_conciliacao.py "POWERTECH"

Sem argumento, lista os clientes da tela "Sem Vendedor" que estão sem código e
diz qual das três tentativas de casamento falhou. Com argumento, investiga um
nome específico. Não altera nada no banco.
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
termo = " ".join(sys.argv[1:]).strip()

print(f"Banco: {backend.DB_PATH}\n")

total_cadastro = conn.execute(
    "SELECT COUNT(*) n FROM crm_client_profiles WHERE company_id = ?", (company_id,)
).fetchone()["n"]
com_documento = conn.execute(
    "SELECT COUNT(*) n FROM crm_client_profiles WHERE company_id = ? "
    "AND document_number IS NOT NULL AND TRIM(document_number) <> ''", (company_id,)
).fetchone()["n"]
ultima = conn.execute(
    "SELECT MAX(updated_at) u FROM crm_client_profiles WHERE company_id = ?", (company_id,)
).fetchone()["u"]
print(f"CADASTRO DE CLIENTES NO CRM: {total_cadastro} cliente(s), "
      f"{com_documento} com CNPJ/CPF · última atualização {ultima}")

# ── A importação do cadastro trouxe tudo? ────────────────────────────────
# O código do Alfa é sequencial: se o maior código do cadastro for MENOR que os
# códigos que aparecem no Alfa, a exportação veio truncada e nenhuma regra de
# casamento vai resolver — o cliente simplesmente não está no banco.
faixa = conn.execute(
    "SELECT MIN(CAST(client_code AS INTEGER)) mn, MAX(CAST(client_code AS INTEGER)) mx "
    "FROM crm_client_profiles WHERE company_id = ? AND client_code GLOB '[0-9]*'",
    (company_id,),
).fetchone()
print(f"  Faixa de códigos: {faixa['mn']} a {faixa['mx']}")

ultimo_import = conn.execute(
    "SELECT MAX(source_import_id) i FROM crm_client_profiles WHERE company_id = ?",
    (company_id,),
).fetchone()["i"]
if ultimo_import:
    linha = conn.execute(
        "SELECT imported_at, notes FROM imports WHERE id = ?", (ultimo_import,)
    ).fetchone()
    if linha:
        print(f"  Última importação de cadastro: {linha['imported_at']} · {linha['notes'] or ''}")
    carregados = conn.execute(
        "SELECT COUNT(*) n FROM crm_client_profiles WHERE company_id = ? AND source_import_id = ?",
        (company_id, ultimo_import),
    ).fetchone()["n"]
    print(f"  Clientes tocados nessa importação: {carregados}")

# Cobertura do cadastro sobre o faturamento.
#
# A primeira versão disto usava NOT EXISTS correlacionado com UPPER(TRIM(...))
# dos dois lados: sem índice utilizável, o SQLite varria o cadastro inteiro para
# CADA nome do faturamento e o diagnóstico simplesmente não terminava. Duas
# leituras sequenciais e um set em memória resolvem em segundos.
nomes_cadastro = {
    backend.normalize_client_key(r["client_name"])
    for r in conn.execute(
        "SELECT client_name FROM crm_client_profiles WHERE company_id = ?", (company_id,)
    ).fetchall()
}
nomes_faturamento = {
    backend.normalize_client_key(r["client_name"])
    for r in conn.execute(
        "SELECT DISTINCT client_name FROM fact_sales_detail WHERE company_id = ?", (company_id,)
    ).fetchall()
}
sem_cadastro = len(nomes_faturamento - nomes_cadastro)
print(f"  Clientes no faturamento: {len(nomes_faturamento)} · "
      f"sem nome igual no cadastro: {sem_cadastro} "
      f"({100 * sem_cadastro / max(len(nomes_faturamento), 1):.1f}%)")
print("\n  >> Se o MAIOR código acima for menor que os códigos novos do Alfa, ou se")
print("     'sem nome igual' for muito alto, a exportação do cadastro veio incompleta.\n")

# ── Mapas usados pelo sistema ────────────────────────────────────────────
por_nome: dict[str, str] = {}
por_empresa: dict[str, set[str]] = {}
for row in conn.execute(
    "SELECT client_code, client_name FROM crm_client_profiles WHERE company_id = ?",
    (company_id,),
).fetchall():
    chave = backend.normalize_client_key(row["client_name"])
    codigo = backend.normalize_whitespace(row["client_code"])
    if chave and codigo:
        por_nome.setdefault(chave, codigo)
    chave_empresa = backend.company_match_key(row["client_name"])
    if chave_empresa and codigo:
        por_empresa.setdefault(chave_empresa, set()).add(codigo)

docs_exatos, docs_raiz = backend.build_document_client_map(conn, company_id)
aliases = backend.client_alias_map(conn, company_id)


def investiga(nome: str) -> str:
    """Devolve o veredito para um nome do faturamento."""
    chave = backend.normalize_client_key(nome)
    if chave in por_nome:
        return f"OK pelo nome exato -> {por_nome[chave]}"
    if chave in aliases:
        return f"OK por conciliação manual -> {aliases[chave]['clientCode']}"
    codigo = backend.client_code_from_name_digits(nome, docs_exatos, docs_raiz)
    if codigo:
        return f"OK pelo documento no nome -> {codigo}"
    chave_empresa = backend.company_match_key(nome)
    candidatos = por_empresa.get(chave_empresa) or set()
    if len(candidatos) == 1:
        return f"OK pela razão social sem sufixo -> {next(iter(candidatos))}"
    if len(candidatos) > 1:
        return f"AMBÍGUO: {len(candidatos)} clientes com a mesma razão social {sorted(candidatos)}"
    # "Parecido" só vale se o TOKEN MAIS DISTINTIVO bater. Procurar pela
    # primeira palavra devolvia toda oficina mecânica do banco para qualquer
    # "MECANICA X LTDA" — ruído que faz parecer que existe candidato quando não
    # existe. O token mais longo é o que carrega o nome próprio.
    tokens = sorted((t for t in chave_empresa.split() if len(t) >= 5), key=len, reverse=True)
    parecidos: list[str] = []
    if tokens:
        parecidos = [
            r["client_name"] for r in conn.execute(
                "SELECT client_name FROM crm_client_profiles WHERE company_id = ? "
                "AND UPPER(client_name) LIKE ? LIMIT 3",
                (company_id, f"%{tokens[0]}%"),
            ).fetchall()
        ]
    if parecidos:
        return f"SEM CASAMENTO · parecidos ({tokens[0]}): {parecidos}"
    return "SEM CASAMENTO · NÃO EXISTE no cadastro do CRM (falta na importação)"


if termo:
    print(f"INVESTIGANDO '{termo}'\n")
    print("  No faturamento:")
    for r in conn.execute(
        "SELECT DISTINCT client_name FROM fact_sales_detail "
        "WHERE company_id = ? AND UPPER(client_name) LIKE ? LIMIT 10",
        (company_id, f"%{termo.upper()}%"),
    ).fetchall():
        print(f"    {r['client_name']}")
        print(f"      chave  = {backend.normalize_client_key(r['client_name'])!r}")
        print(f"      empresa= {backend.company_match_key(r['client_name'])!r}")
        print(f"      -> {investiga(r['client_name'])}")
    print("\n  No cadastro do CRM:")
    for r in conn.execute(
        "SELECT client_code, client_name, document_number, internal_seller_name "
        "FROM crm_client_profiles WHERE company_id = ? AND UPPER(client_name) LIKE ? LIMIT 10",
        (company_id, f"%{termo.upper()}%"),
    ).fetchall():
        print(f"    [{r['client_code']}] {r['client_name']}  doc={r['document_number']}  "
              f"vend={r['internal_seller_name'] or '—'}")
        print(f"      chave  = {backend.normalize_client_key(r['client_name'])!r}")
        print(f"      empresa= {backend.company_match_key(r['client_name'])!r}")
    sys.exit(0)

# ── Sem argumento: varre a lista Sem Vendedor ────────────────────────────
usuario = conn.execute(
    "SELECT * FROM users WHERE company_id = ? AND role IN ('Diretor','Administrador') LIMIT 1",
    (company_id,),
).fetchone()
if not usuario:
    print("Nenhum usuário diretor/administrador para simular a tela.")
    sys.exit(1)

print("Montando a lista Sem Vendedor (pode levar alguns segundos)...", flush=True)
dados = backend.compute_unassigned_clients(conn, company_id, usuario, limit=500)
sem_codigo = [i for i in dados["items"] if not i.get("clientKey")]
print(f"SEM VENDEDOR: {dados['total']} cliente(s), {len(sem_codigo)} sem código no CRM\n")

for item in sem_codigo[:60]:
    print(f"  {item['clientName'][:52]:<54}{investiga(item['clientName'])}")

if len(sem_codigo) > 60:
    print(f"\n  ... e mais {len(sem_codigo) - 60}.")

print("\nCOMO LER")
print("  OK ...            já casa, não precisa conciliar (recarregue a tela)")
print("  AMBÍGUO           dois cadastros com a mesma razão social — concilie à mão pelo código")
print("  SEM CASAMENTO     o cliente não está no cadastro do CRM com esse nome")
print("                    se houver 'parecidos', concilie pelo código")
print("                    se não houver nenhum, falta importar o cadastro de clientes")
