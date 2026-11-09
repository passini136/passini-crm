"""Balanço 2026 por unidade para as reuniões individuais com os gerentes (nov/2026).

SOMENTE LEITURA. Usa as funções oficiais do backend (as mesmas das telas
Resultados e Produtividade), então os números batem com o CRM.

Saída: tabela CSV no terminal e em /srv/passini/data/crm/balanco_gerentes_2026.csv
"""
from __future__ import annotations

import csv
import importlib.util
import io
import os
import sys
from pathlib import Path

os.environ.setdefault("PASSINI_CRM_DATA", "/srv/passini/data/crm")
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))  # backend importa módulos irmãos (mes_cadastro etc.)
os.chdir(ROOT)
spec = importlib.util.spec_from_file_location("passini_backend", ROOT / "backend.py")
b = importlib.util.module_from_spec(spec)
spec.loader.exec_module(b)

MESES = [f"2026-{m:02d}" for m in range(1, 11)]
CID = 1


def mes_menos(comp: str, n: int) -> str:
    a, m = map(int, comp.split("-"))
    m -= n
    while m <= 0:
        m += 12
        a -= 1
    return f"{a}-{m:02d}"


conn = b.get_connection()
CID = conn.execute("SELECT id FROM companies ORDER BY id LIMIT 1").fetchone()[0]
unidades = sorted({b.normalize_unit(r[0]) for r in conn.execute(
    "SELECT DISTINCT unit_name FROM fact_unit_summary WHERE company_id = ? AND competence LIKE '2026-%'",
    (CID,)).fetchall() if r[0]})

linhas = []
for u in unidades:
    serie = {r["competence"]: r for r in b.resultados_serie(conn, CID, "unidade", u, 24)}
    for comp in MESES:
        s = serie.get(comp, {})
        row = {"unidade": u, "mes": comp,
               "faturamento": s.get("revenueNet"), "meta": s.get("revenueGoal"),
               "fat_p_meta": s.get("revenueForGoal"), "ating_pct": s.get("attainmentPct"),
               "devol_valor": s.get("returnsCommercial"), "devol_pct": s.get("returnRatioPct"),
               "mix": s.get("mixSku"), "clientes": s.get("clients")}
        try:
            p = b.resultados_produtividade(conn, CID, "unidade", u, comp) or {}
            row.update(posit_pct=p.get("positivationPct"), carteira=p.get("portfolioSize"),
                       carteira_atend=p.get("portfolioServed"), sem_dono=p.get("portfolioOrphan"))
        except Exception as e:  # noqa
            row.update(posit_pct=f"ERRO {e}")
        vend = b.sellers_of_unit(conn, CID, comp, u) or []
        row["vendedores"] = len(vend)
        try:
            row["contatos_ativos"] = sum(
                1 for r in conn.execute(
                    "SELECT unit_name FROM crm_interactions WHERE company_id = ? "
                    "AND initiative = 'ATIVO' AND result_code NOT IN ('NAO_ATENDEU','PEDIU_RETORNO') "
                    "AND substr(replace(occurred_at,'T',' '),1,7) = ?", (CID, comp)).fetchall()
                if b.normalize_unit(r[0]) == u)
        except Exception as e:  # noqa
            row["contatos_ativos"] = f"ERRO {e}"
        # Recuperados: comprou >= R$ 999 no mês e não comprou nos 2 meses anteriores
        # (mesma régua do Extra Positivação). Jan e fev não têm 2025 importado.
        if comp >= "2026-03" and vend:
            mv = ",".join("?" for _ in vend)
            q = (f"SELECT client_name FROM fact_sales_detail WHERE company_id = ? AND competence = ? "
                 f"AND seller_name IN ({mv}) AND client_name <> '' GROUP BY client_name "
                 f"HAVING SUM(net_value) >= 999")
            atual = {r[0] for r in conn.execute(q, (CID, comp, *vend)).fetchall()}
            antes = {r[0] for r in conn.execute(
                "SELECT DISTINCT client_name FROM fact_sales_detail WHERE company_id = ? "
                "AND competence IN (?, ?) AND net_value > 0",
                (CID, mes_menos(comp, 1), mes_menos(comp, 2))).fetchall()}
            row["recuperados"] = len(atual - antes)
        linhas.append(row)
    print(f"ok {u}", file=sys.stderr)

campos = list(linhas[0].keys()) if linhas else []
for r in linhas:
    for k in r:
        if k not in campos:
            campos.append(k)
buf = io.StringIO()
w = csv.DictWriter(buf, fieldnames=campos, delimiter=";")
w.writeheader()
for r in linhas:
    w.writerow(r)
saida = Path(os.environ["PASSINI_CRM_DATA"]) / "balanco_gerentes_2026.csv"
saida.write_text(buf.getvalue(), encoding="utf-8")
print(buf.getvalue())
print(f"# salvo em {saida}", file=sys.stderr)
