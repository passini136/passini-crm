"""
Mostra, dia a dia, QUEM trouxe o faturamento de um mês.

Uso no servidor:
    /srv/passini/venv/crm/bin/python /srv/passini/apps/crm-comercial/diag_cobertura.py 2026-08 88

Serve para responder uma pergunta só, antes de apagar qualquer coisa:
uma importação pode substituir as outras sem perder dia nenhum?

O relatório completo do Alfa (o que se baixa uma vez, com o mês inteiro) e os
relatórios diários descrevem as MESMAS vendas. Quando os dois estão na base, o
mês soma duas vezes. Só que eles não são intercambiáveis: o completo costuma
trazer campos que o diário não traz. Este diagnóstico compara os dois lados por
data de emissão para mostrar qual pode sair sem levar venda junto.

Não altera nada. A remoção é sempre pelo limpar_import.py.
"""
import os
import sys
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, "/srv/passini/apps/crm-comercial")

if not os.environ.get("PASSINI_CRM_DATA"):
    for candidate in ("/srv/passini/data/crm", "/srv/passini/data"):
        if (Path(candidate) / "passini_dashboard.db").exists():
            os.environ["PASSINI_CRM_DATA"] = candidate
            break

import backend  # noqa: E402

argumentos = [a for a in sys.argv[1:] if not a.startswith("--")]

conn = backend.get_connection()
company_id = conn.execute("SELECT id FROM companies LIMIT 1").fetchone()["id"]

competencia = next((a for a in argumentos if len(a) == 7 and a[4] == "-"), None) \
    or backend.crm_latest_competence(conn, company_id)
pivo = next((int(a) for a in argumentos if a.isdigit()), None)

print(f"Banco: {backend.DB_PATH}")
print(f"Competência: {competencia}\n")


def dinheiro(v):
    return f"{float(v or 0):>15,.2f}"


def dia_de(texto):
    """Data de emissão em dd/mm/aaaa ou aaaa-mm-dd, sempre devolvida ordenável."""
    t = backend.normalize_whitespace(texto or "")[:10]
    if len(t) == 10 and t[2] == "/" and t[5] == "/":
        return f"{t[6:10]}-{t[3:5]}-{t[0:2]}"
    return t


# ── Quando cada importação entrou ────────────────────────────────────────
quando = {}
for r in conn.execute(
    "SELECT d.import_id, MAX(i.imported_at) quando "
    "FROM fact_sales_detail d LEFT JOIN imports i ON i.id = d.import_id "
    "WHERE d.company_id = ? AND d.competence = ? GROUP BY d.import_id",
        (company_id, competencia)).fetchall():
    quando[r["import_id"]] = str(r["quando"] or "")

if not quando:
    print("Nenhuma linha de faturamento detalhado nesta competência.")
    conn.close()
    sys.exit(0)

# ── 1. Quem gravou a marca ───────────────────────────────────────────────
# A marca passou a ser gravada em certo momento. Importação anterior a isso
# tem venda, mas não tem marca — e por isso NÃO pode ser substituída por uma
# que tenha, nem o contrário, sem olhar antes.
print("1) PREENCHIMENTO DA MARCA POR IMPORTAÇÃO")
print(f"   {'IMPORT':<8}{'QUANDO':<21}{'LINHAS':>8}{'COM MARCA':>11}{'':>3}")
for r in conn.execute(
    "SELECT import_id, COUNT(*) n, "
    "       SUM(CASE WHEN TRIM(COALESCE(brand_name,'')) <> '' THEN 1 ELSE 0 END) com "
    "FROM fact_sales_detail WHERE company_id = ? AND competence = ? "
    "GROUP BY import_id", (company_id, competencia)).fetchall():
    pct = 100.0 * (r["com"] or 0) / (r["n"] or 1)
    aviso = "  <<< sem marca" if pct < 1 else ""
    print(f"   {str(r['import_id']):<8}{quando.get(r['import_id'], '')[:19]:<21}"
          f"{r['n']:>8}{pct:>10.0f}%{aviso}")

if pivo is None:
    print("\nInforme também a importação a comparar, ex: diag_cobertura.py "
          f"{competencia} 88")
    conn.close()
    sys.exit(0)

if pivo not in quando:
    print(f"\nA importação {pivo} não tem linhas em {competencia}.")
    conn.close()
    sys.exit(0)

# ── 2. Cobertura por dia de emissão ──────────────────────────────────────
marco = quando.get(pivo, "")
por_dia: dict[str, list[float]] = defaultdict(lambda: [0.0, 0.0, 0.0])
for r in conn.execute(
    "SELECT import_id, issue_date, SUM(net_value) v FROM fact_sales_detail "
    "WHERE company_id = ? AND competence = ? GROUP BY import_id, issue_date",
        (company_id, competencia)).fetchall():
    d = dia_de(r["issue_date"])
    if not d:
        continue
    if r["import_id"] == pivo:
        coluna = 0
    elif quando.get(r["import_id"], "") < marco:
        coluna = 1
    else:
        coluna = 2
    por_dia[d][coluna] += float(r["v"] or 0)

print(f"\n2) COBERTURA POR DIA DE EMISSÃO (pivô = importação {pivo})")
print(f"   {'DIA':<12}{'PIVÔ ' + str(pivo):>16}{'ANTES DELE':>16}"
      f"{'DEPOIS DELE':>16}   SITUAÇÃO")

descobertos = []
for d in sorted(por_dia):
    a, b, c = por_dia[d]
    if b > 0 and a <= 0:
        # O pivô não tem este dia. Tirar os anteriores apagaria a venda dele.
        situacao = ">> só os anteriores têm este dia"
        descobertos.append((d, b))
    elif a > 0 and b > 0:
        situacao = "os dois têm — soma dobrada"
    else:
        situacao = ""
    print(f"   {d:<12}{dinheiro(a):>16}{dinheiro(b):>16}{dinheiro(c):>16}   {situacao}")

soma_pivo = sum(v[0] for v in por_dia.values())
soma_antes = sum(v[1] for v in por_dia.values())
soma_depois = sum(v[2] for v in por_dia.values())
print(f"   {'TOTAL':<12}{dinheiro(soma_pivo):>16}{dinheiro(soma_antes):>16}"
      f"{dinheiro(soma_depois):>16}")

# ── 3. Veredito ──────────────────────────────────────────────────────────
anteriores = sorted(i for i, q in quando.items() if q < marco and i != pivo)
oficial = conn.execute(
    "SELECT ROUND(SUM(net_value),2) v FROM fact_unit_summary "
    "WHERE company_id = ? AND competence = ?",
    (company_id, competencia)).fetchone()["v"] or 0

print("\n3) VEREDITO")
if not anteriores:
    print(f"   Não há importação anterior à {pivo} nesta competência. Nada a decidir.")
elif descobertos:
    print(f"   >> NÃO remova as anteriores. {len(descobertos)} dia(s) existem só nelas,")
    print(f"      somando {dinheiro(sum(v for _, v in descobertos))}:")
    for d, v in descobertos[:10]:
        print(f"         {d}   {dinheiro(v)}")
    print("      Removê-las apagaria essas vendas do mês.")
else:
    print(f"   A importação {pivo} cobre TODOS os dias que as anteriores cobrem.")
    print(f"   As anteriores podem sair: {', '.join(str(i) for i in anteriores)}")
    restante = soma_pivo + soma_depois
    print(f"\n   Sairiam        {dinheiro(soma_antes)}")
    print(f"   Ficaria o mês  {dinheiro(restante)}")
    if oficial:
        print(f"   Oficial        {dinheiro(oficial)}   "
              f"({100 * (restante / oficial - 1):+.0f}%)")
    print(f"\n   Simule antes (não altera nada):")
    print(f"      limpar_import.py {' '.join(str(i) for i in anteriores)} {competencia}")
    print(f"   E só então acrescente --aplicar no fim.")

conn.close()
