"""
Por que 733 clientes contatados e ZERO compraram?

Uso:
    /srv/passini/venv/crm/bin/python /srv/passini/apps/crm-comercial/diag_conversao.py
    /srv/passini/venv/crm/bin/python /srv/passini/apps/crm-comercial/diag_conversao.py 2026-09

Zero é resposta impossível. Com 3.944 clientes faturados e 733 contatados, o
acaso sozinho já produziria dezenas de coincidências. Então ou a chave não casa,
ou a equipe só liga para quem ainda não é cliente.

As duas hipóteses pedem ações OPOSTAS, e é por isso que este diagnóstico existe
em vez de um palpite:
  A) CHAVE NÃO CASA → é bug meu, conserto no código e ninguém fica sabendo.
  B) SÓ LIGAM PARA PROSPECT → o dado está certo, e o que a reunião precisa saber
     é que a equipe não trabalha a carteira por telefone. Mostrar "conversão 0%"
     sem essa distinção faria o gerente cobrar o vendedor por um número quebrado.

O teste que separa as duas: se as chaves NUNCA casam, em nenhum mês, é bug. Se
casam em outros meses, é comportamento.

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
ini = backend.first_day_of_competence(comp).isoformat()
fim = backend.last_day_of_competence(comp).isoformat()

print(f"Banco: {backend.DB_PATH}")
print(f"Competência: {comp}\n")

# ── 1. Como são as chaves dos dois lados? ───────────────────────────────────
# Ver os valores crus é o passo que eu pulei quando escrevi a função.
print("1) AMOSTRA DAS CHAVES — os dois lados lado a lado")
print("\n   INTERAÇÕES (ligação ativa no mês)")
print(f"   {'client_key GRAVADO':<34}{'normalize(client_name)':<34}IGUAL?")
amostra = conn.execute(
    "SELECT client_key, client_name FROM crm_interactions "
    "WHERE company_id = ? AND initiative = 'ATIVO' AND contact_type_code = 'LIGACAO' "
    "AND date(substr(replace(occurred_at,'T',' '),1,10)) BETWEEN date(?) AND date(?) "
    "LIMIT 12", (company_id, ini, fim)).fetchall()
for r in amostra:
    recalc = backend.normalize_client_key(r["client_name"])
    igual = "sim" if recalc == (r["client_key"] or "") else "NÃO"
    print(f"   {str(r['client_key'])[:33]:<34}{recalc[:33]:<34}{igual}")

print("\n   FATURAMENTO DETALHADO")
print(f"   {'client_name':<40}{'normalize(client_name)':<34}")
for r in conn.execute(
    "SELECT DISTINCT client_name FROM fact_sales_detail "
    "WHERE company_id = ? AND competence = ? LIMIT 8", (company_id, comp)).fetchall():
    print(f"   {str(r['client_name'])[:39]:<40}"
          f"{backend.normalize_client_key(r['client_name'])[:33]:<34}")

# ── 2. O teste decisivo: casam em ALGUM mês? ────────────────────────────────
# Se a interseção é zero em todos os meses, os dois lados vivem em espaços de
# chave diferentes e o problema é meu. Se casa em algum, a chave funciona.
print("\n2) AS CHAVES CASAM EM ALGUM MÊS?")
print(f"   {'MÊS':<10}{'CONTATADOS':>12}{'FATURADOS':>12}{'CASARAM':>10}{'%':>7}")
algum = False
for c in sorted(backend.query_competences(conn, company_id))[-6:]:
    a = backend.first_day_of_competence(c).isoformat()
    b = backend.last_day_of_competence(c).isoformat()
    contatados = {r["client_key"] for r in conn.execute(
        "SELECT DISTINCT client_key FROM crm_interactions WHERE company_id = ? "
        "AND initiative = 'ATIVO' AND contact_type_code = 'LIGACAO' "
        "AND date(substr(replace(occurred_at,'T',' '),1,10)) BETWEEN date(?) AND date(?)",
        (company_id, a, b)).fetchall() if r["client_key"]}
    faturados = {backend.normalize_client_key(r["client_name"]) for r in conn.execute(
        "SELECT DISTINCT client_name FROM fact_sales_detail "
        "WHERE company_id = ? AND competence = ?", (company_id, c)).fetchall()
        if r["client_name"]}
    casou = contatados & faturados
    pct = 100 * len(casou) / len(contatados) if contatados else 0
    if casou:
        algum = True
    print(f"   {c:<10}{len(contatados):>12}{len(faturados):>12}{len(casou):>10}{pct:>6.0f}%")

# ── 3. Quem são os contatados? ──────────────────────────────────────────────
# Prospect nunca vai casar com faturamento: por definição ainda não é cliente.
print("\n3) OS CONTATADOS SÃO CLIENTES OU PROSPECTS?")
prospect = cliente = 0
for r in conn.execute(
    "SELECT DISTINCT client_key FROM crm_interactions WHERE company_id = ? "
    "AND initiative = 'ATIVO' AND contact_type_code = 'LIGACAO' "
    "AND date(substr(replace(occurred_at,'T',' '),1,10)) BETWEEN date(?) AND date(?)",
        (company_id, ini, fim)).fetchall():
    if str(r["client_key"] or "").startswith("P-"):
        prospect += 1
    else:
        cliente += 1
total = prospect + cliente
print(f"   Prospects: {prospect} ({100 * prospect / total if total else 0:.0f}%)")
print(f"   Clientes:  {cliente} ({100 * cliente / total if total else 0:.0f}%)")
if prospect and not cliente:
    print("   >> SÓ PROSPECTS. A conversão de carteira não existe porque a")
    print("      carteira não é trabalhada por telefone — e a métrica certa")
    print("      para este time é conversão de PROSPECT EM CLIENTE, outra conta.")

# ── 4. Os contatados que são clientes existem no faturamento? ──────────────
print("\n4) OS CONTATADOS-CLIENTES APARECEM NO FATURAMENTO DO MÊS?")
faturados_mes = {backend.normalize_client_key(r["client_name"]) for r in conn.execute(
    "SELECT DISTINCT client_name FROM fact_sales_detail "
    "WHERE company_id = ? AND competence = ?", (company_id, comp)).fetchall()
    if r["client_name"]}
print(f"   {'CHAVE CONTATADA':<40}{'FATUROU?':<10}EXISTE NO CADASTRO?")
achou = falta = 0
for r in conn.execute(
    "SELECT DISTINCT client_key, client_name FROM crm_interactions WHERE company_id = ? "
    "AND initiative = 'ATIVO' AND contact_type_code = 'LIGACAO' "
    "AND date(substr(replace(occurred_at,'T',' '),1,10)) BETWEEN date(?) AND date(?) "
    "LIMIT 400", (company_id, ini, fim)).fetchall():
    k = r["client_key"] or ""
    if k.startswith("P-"):
        continue
    no_mes = k in faturados_mes
    no_cadastro = conn.execute(
        "SELECT 1 FROM crm_client_profiles WHERE company_id = ? AND client_name = ? LIMIT 1",
        (company_id, r["client_name"])).fetchone() is not None
    if no_mes:
        achou += 1
    else:
        falta += 1
        if falta <= 10:
            print(f"   {k[:39]:<40}{'não':<10}{'sim' if no_cadastro else 'NÃO'}")
print(f"\n   Faturaram no mês: {achou}   ·   Não faturaram: {falta}")
if not algum:
    print("\n   >> AS CHAVES NUNCA CASAM, EM NENHUM MÊS. Isso é bug de chave, não")
    print("      comportamento de equipe. A conversão sai da tela até funcionar.")
elif achou:
    print("\n   >> A chave casa. O zero em setembro é comportamento, não bug.")

conn.close()
