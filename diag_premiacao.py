"""
De onde vem cada número da apuração da premiação.

Uso no servidor:
    /srv/passini/venv/crm/bin/python /srv/passini/apps/crm-comercial/diag_premiacao.py 2026-08
    /srv/passini/venv/crm/bin/python /srv/passini/apps/crm-comercial/diag_premiacao.py 2026-08 CARLOS

A premiação sai de quatro fontes diferentes, e quando o número parece errado a
pergunta é sempre a mesma: qual delas está incompleta? Este script mostra as
quatro lado a lado, sem calcular nada por cima.

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

argumentos = [a for a in sys.argv[1:] if not a.startswith("-")]
competencia = next((a for a in argumentos if len(a) == 7 and a[4] == "-"), "")
procurado = " ".join(a for a in argumentos
                     if not (len(a) == 7 and a[4] == "-")).strip().upper()

conn = backend.get_connection()
company_id = conn.execute("SELECT id FROM companies LIMIT 1").fetchone()["id"]
competencia = backend.valid_competence(competencia) or \
    backend.crm_latest_competence(conn, company_id) or ""

print(f"Banco: {backend.DB_PATH}")
print(f"Competência: {competencia}\n")


def brl(v):
    return f"{float(v or 0):>14,.2f}"


# ── 1. As unidades ───────────────────────────────────────────────────────
print("1) UNIDADES — realizado x meta (fact_unit_summary x goals_unit)")
print(f"   {'UNIDADE':<14}{'REALIZADO':>16}{'META':>16}{'ATING':>8}")
for u in backend.CANONICAL_UNITS:
    real = conn.execute(
        "SELECT COALESCE(SUM(net_value),0) v FROM fact_unit_summary "
        "WHERE company_id = ? AND competence = ? AND unit_name = ?",
        (company_id, competencia, u)).fetchone()["v"]
    meta = conn.execute(
        "SELECT COALESCE(SUM(revenue_goal),0) v FROM goals_unit "
        "WHERE company_id = ? AND competence = ? AND unit_name = ?",
        (company_id, competencia, u)).fetchone()["v"]
    ating = f"{100 * real / meta:.1f}%" if meta else "—"
    alerta = ""
    if meta and real and (100 * real / meta) < 50:
        # Atingimento muito baixo quase nunca é venda ruim: é dado faltando.
        alerta = "  << realizado parece parcial"
    elif meta and not real:
        alerta = "  << sem realizado"
    elif real and not meta:
        alerta = "  << sem meta cadastrada"
    print(f"   {u:<14}{brl(real)}{brl(meta)}{ating:>8}{alerta}")

# ── 2. Quantas importações alimentam cada resumo ─────────────────────────
print("\n2) DE QUANTAS IMPORTAÇÕES VEIO CADA RESUMO")
for tabela, rotulo in (("fact_unit_summary", "por unidade"),
                       ("fact_vendor_summary", "por vendedor")):
    linha = conn.execute(
        f"SELECT COUNT(*) linhas, COUNT(DISTINCT import_id) imports, "
        f"       MAX(created_at) quando, ROUND(SUM(net_value),2) valor "
        f"FROM {tabela} WHERE company_id = ? AND competence = ?",
        (company_id, competencia)).fetchone()
    print(f"   {rotulo:<14}{linha['linhas']:>4} linha(s) · "
          f"{linha['imports']} importação(ões) · {brl(linha['valor'])} · "
          f"gravado em {str(linha['quando'])[:16]}")
print("   Se os dois totais divergem muito, um dos dois arquivos é de outra data.")

# ── 3. Vendedores ────────────────────────────────────────────────────────
print("\n3) VENDEDORES — realizado x meta x metas de indicador")
linhas = conn.execute(
    "SELECT seller_name, ROUND(SUM(net_value),2) liquido, ROUND(SUM(sale_value),2) bruto, "
    "       AVG(margin_value) margem "
    "FROM fact_vendor_summary WHERE company_id = ? AND competence = ? "
    "GROUP BY seller_name ORDER BY liquido DESC", (company_id, competencia)).fetchall()
if procurado:
    linhas = [r for r in linhas if procurado in backend.normalize_upper(r["seller_name"])]

print(f"   {'VENDEDOR':<34}{'REALIZADO':>15}{'META':>15}{'ATING':>8}"
      f"{'MARGEM':>8}  METAS DE INDICADOR")
sem_meta_venda = 0
sem_metas_indicador = 0
for r in linhas:
    nome = backend.normalize_whitespace(r["seller_name"])
    metas_venda = backend.entries_for_person(
        {x["seller_name"]: x for x in conn.execute(
            "SELECT seller_name, revenue_goal FROM goals_seller "
            "WHERE company_id = ? AND competence = ?",
            (company_id, competencia)).fetchall()}, nome)
    meta = float(metas_venda[0]["revenue_goal"] or 0) if metas_venda else 0.0
    alvos = backend.seller_targets_for(conn, company_id, nome, competencia)
    faltando = [r for r, v in (("mix", alvos["mixTarget"]),
                               ("margem", alvos["marginTarget"]),
                               ("ligações", alvos["callsTarget"])) if v is None]
    if not meta:
        sem_meta_venda += 1
    if faltando:
        sem_metas_indicador += 1
    ating = f"{100 * float(r['liquido'] or 0) / meta:.1f}%" if meta else "—"
    marg = f"{float(r['margem']):.4f}" if r["margem"] else "—"
    nota = ("falta " + ", ".join(faltando)) if faltando else "ok"
    if alvos["onVacation"]:
        nota += f" · férias ({alvos['workingDays']}/{alvos['monthDays']} dias)"
    print(f"   {nome[:33]:<34}{brl(r['liquido'])}{brl(meta)}{ating:>8}{marg:>8}  {nota}")

print(f"\n   {len(linhas)} vendedor(es) · {sem_meta_venda} sem meta de venda · "
      f"{sem_metas_indicador} sem alguma meta de indicador")

# ── 4. O que a apuração faria ────────────────────────────────────────────
print("\n4) LEITURA")
if sem_meta_venda:
    print(f"   >> {sem_meta_venda} vendedor(es) SEM meta de venda em {competencia}.")
    print("      Sem ela não há atingimento, e sem atingimento ninguém é elegível.")
if sem_metas_indicador:
    print(f"   >> {sem_metas_indicador} vendedor(es) sem alguma meta de indicador.")
    print("      Cadastre em Operações → Metas. Sem meta, o indicador não pontua.")
if not sem_meta_venda and not sem_metas_indicador:
    print("   Metas completas. Se o atingimento ainda parecer baixo, o problema")
    print("   está no REALIZADO: confira o item 2 e reimporte o custo x venda.")

conn.close()
