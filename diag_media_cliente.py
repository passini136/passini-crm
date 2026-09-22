"""
Por que a média mensal está R$ 0,00 para os 101.269 clientes?

Uso:
    /srv/passini/venv/crm/bin/python /srv/passini/apps/crm-comercial/diag_media_cliente.py

A média alimenta MUITA coisa: a classe do cliente (Diamante/Ouro/Prata), a
queda de faturamento, a ordenação do roteiro de visitas, a dos inativos e as
prioridades da Missão do Dia. Com ela zerada, tudo isso para de funcionar em
silêncio — nenhuma tela dá erro, todas só mostram menos do que deveriam.

A conta é: soma do faturamento dos TRÊS MESES ANTERIORES a c0, dividida por 3.
E c0 vem do CONSOLIDADO POR CLIENTE, enquanto o faturamento dos três meses vem
do DETALHADO. Se as duas bases não estiverem no mesmo mês, c1/c2/c3 apontam
para meses sem linha nenhuma e a média zera para a base inteira.

Duas causas possíveis, e cada uma leva a um conserto diferente:
  A) as bases estão em meses diferentes → o problema é a importação
  B) as bases batem, mas o nome do cliente não casa entre elas → o problema
     é a chave de casamento

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

# ── 1. Em que mês cada base acha que está ───────────────────────────────────
c0 = backend.crm_summary_latest_competence(conn, company_id)
c1 = backend.shift_competence(c0, -1) if c0 else None
c2 = backend.shift_competence(c0, -2) if c0 else None
c3 = backend.shift_competence(c0, -3) if c0 else None

det_max = conn.execute(
    "SELECT MAX(competence) m FROM fact_sales_detail WHERE company_id = ?",
    (company_id,)).fetchone()["m"]

print("1) EM QUE MÊS CADA BASE ESTÁ")
print(f"   consolidado por cliente (define o c0): {c0}")
print(f"   faturamento detalhado (último mês)...: {det_max}")
print(f"   a média soma os meses...............: {c1}, {c2}, {c3}")
if c0 and det_max and c0 > det_max:
    print("\n   >> O consolidado está À FRENTE do detalhado. Os três meses da média")
    print("      caem onde não existe faturamento, e a média zera para todo mundo.")
    print("      CAUSA (A): importação. O conserto é acertar o mês, não o cálculo.")

# ── 2. Tem faturamento nesses três meses? ───────────────────────────────────
print("\n2) EXISTE FATURAMENTO NOS MESES DA MÉDIA?")
print(f"   {'MÊS':<10}{'LINHAS':>10}{'CLIENTES':>10}{'FATURAMENTO':>16}")
total_janela = 0
for comp in (c0, c1, c2, c3):
    if not comp:
        continue
    r = conn.execute(
        "SELECT COUNT(*) linhas, COUNT(DISTINCT client_name) clientes, "
        "COALESCE(SUM(net_value),0) v FROM fact_sales_detail "
        "WHERE company_id = ? AND competence = ?", (company_id, comp)).fetchone()
    marca = "  ← c0 (mês atual)" if comp == c0 else "  ← entra na média"
    print(f"   {comp:<10}{r['linhas']:>10}{r['clientes']:>10}"
          f"{backend.brl(r['v']):>16}{marca}")
    if comp != c0:
        total_janela += int(r["linhas"])
if total_janela == 0:
    print("\n   >> ZERO linhas nos três meses da média. Confirmada a CAUSA (A).")

# ── 3. Os meses que a base REALMENTE tem ────────────────────────────────────
print("\n3) OS MESES QUE EXISTEM EM CADA BASE")
print(f"   {'MÊS':<10}{'DETALHADO':>12}{'CONSOLIDADO':>14}")
meses_det = {r["c"]: r["n"] for r in conn.execute(
    "SELECT competence c, COUNT(*) n FROM fact_sales_detail WHERE company_id = ? "
    "GROUP BY competence", (company_id,)).fetchall()}
meses_con = {r["c"]: r["n"] for r in conn.execute(
    "SELECT competence c, COUNT(*) n FROM crm_client_summary WHERE company_id = ? "
    "GROUP BY competence", (company_id,)).fetchall()}
for comp in sorted(set(meses_det) | set(meses_con), reverse=True)[:18]:
    d, c = meses_det.get(comp, 0), meses_con.get(comp, 0)
    alerta = ""
    if c and not d:
        alerta = "  ← só no consolidado"
    elif d and not c:
        alerta = "  ← só no detalhado"
    print(f"   {comp:<10}{d:>12}{c:>14}{alerta}")

# ── 4. Se os meses baterem, o nome casa? ────────────────────────────────────
# Só faz sentido perguntar isto se houver faturamento na janela. Sem linhas,
# a taxa de casamento seria 0% por falta de dados e apontaria a culpa errada.
print("\n4) O NOME DO CLIENTE CASA ENTRE AS DUAS BASES?")
if total_janela == 0:
    print("   Pulado: não há faturamento na janela para comparar.")
    print("   Refazer esta conferência depois de acertar o mês.")
else:
    chaves_det = {
        backend.normalize_client_key(r["client_name"])
        for r in conn.execute(
            "SELECT DISTINCT client_name FROM fact_sales_detail "
            "WHERE company_id = ? AND competence IN (?,?,?)",
            (company_id, c1, c2, c3)).fetchall() if r["client_name"]
    }
    # A TAXA SE MEDE DO LADO DO FATURAMENTO, não do cadastro.
    #
    # Na primeira versão eu dividia pelos 95.116 nomes do cadastro e o
    # resultado dava 8,8% — parecia casamento quebrado. Mas o cadastro carrega
    # milhares de registros que nunca compraram (base morta pré-2022), e eles
    # nunca teriam faturamento para casar. A pergunta certa é a inversa: de
    # quem COMPROU, quantos o cadastro conhece? Ali a resposta foi 8.338 de
    # 8.339 — praticamente tudo.
    chaves_cad = {
        backend.normalize_client_key(r["client_name"])
        for r in conn.execute(
            "SELECT DISTINCT client_name FROM crm_client_profiles WHERE company_id = ?",
            (company_id,)).fetchall() if r["client_name"]
    }
    casaram = len(chaves_det & chaves_cad)
    pct = 100 * casaram / len(chaves_det) if chaves_det else 0
    print(f"   {len(chaves_det)} nome(s) compraram na janela")
    print(f"   {len(chaves_cad)} nome(s) no cadastro (inclui base morta, que nunca comprou)")
    print(f"   {casaram} dos que compraram estão no cadastro ({pct:.1f}%)")
    if pct < 90:
        print("   >> CAUSA (B): o casamento por nome está falhando. O conserto é na")
        print("      chave, não na importação.")
    else:
        print("   >> Casamento saudável. Se a média ainda zerar, o defeito está no")
        print("      merge dentro de build_crm_base_client_rows.")
    orfaos = len(chaves_det - chaves_cad)
    if orfaos:
        print(f"   ({orfaos} nome(s) faturaram sem estar no cadastro — vale olhar,")
        print("    mas não afeta a média de quem está cadastrado.)")

conn.close()
