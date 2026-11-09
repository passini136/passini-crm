"""Grava as metas de UNIDADE de jan a jun/2026 (planilha "01 METAS GRUPO - 2026", aba METAS 2026,
linha META MÊS 2026). Jul a dez já estavam no CRM e conferem com a planilha.

Padrão: SÓ MOSTRA o que faria. Para gravar, rode com --gravar.
Antes de gravar, faz backup do banco com a API do SQLite (o banco roda em WAL).
Não sobrescreve meta que já exista com valor > 0, a não ser com --forcar.
"""
from __future__ import annotations

import importlib.util
import os
import sqlite3
import sys
from datetime import datetime
from pathlib import Path

os.environ.setdefault("PASSINI_CRM_DATA", "/srv/passini/data/crm")
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
os.chdir(ROOT)
spec = importlib.util.spec_from_file_location("passini_backend", ROOT / "backend.py")
b = importlib.util.module_from_spec(spec)
spec.loader.exec_module(b)

METAS = {  # jan, fev, mar, abr, mai, jun
    "MATRIZ":   [1980000, 1800000, 2243516, 2140000, 2236000, 2280000],
    "LAJEADO":  [800000, 720000, 902000, 820000, 838000, 840000],
    "PELOTAS":  [1120000, 969000, 1298000, 1197000, 1200000, 1220000],
    "ZONA SUL": [700000, 557600, 858000, 780000, 800000, 800000],  # "PORTO ALEGRE" na planilha
    "XANGRILA": [390000, 342000, 462000, 380000, 400000, 420000],
}
GRAVAR = "--gravar" in sys.argv
FORCAR = "--forcar" in sys.argv

conn = b.get_connection()
cid = conn.execute("SELECT id FROM companies ORDER BY id LIMIT 1").fetchone()[0]
existentes = {b.normalize_unit(r[0]) for r in conn.execute(
    "SELECT DISTINCT unit_name FROM goals_unit WHERE company_id = ?", (cid,)).fetchall()}

plano = []
for unidade, valores in METAS.items():
    un = b.normalize_unit(unidade)
    if un not in existentes:
        print(f"ATENCAO: unidade {un} nao existe em goals_unit (jul-dez). Confira o nome antes de gravar.")
    for i, valor in enumerate(valores, start=1):
        comp = f"2026-{i:02d}"
        atual = conn.execute(
            "SELECT revenue_goal FROM goals_unit WHERE company_id = ? AND competence = ? AND unit_name = ?",
            (cid, comp, un)).fetchone()
        atual_v = float(atual[0]) if atual else None
        if atual_v and not FORCAR:
            acao = "MANTER (ja tem meta)"
        else:
            acao = "GRAVAR"
            plano.append((comp, un, float(valor)))
        print(f"{un:10s} {comp}  atual={atual_v if atual_v is not None else '-':>12}  nova={valor:>12,.0f}  {acao}")

print(f"\n{len(plano)} metas a gravar.")
if not GRAVAR:
    print("Nada foi gravado. Rode de novo com --gravar para aplicar.")
    sys.exit(0)

destino = Path(os.environ["PASSINI_CRM_DATA"]) / f"backup_antes_metas_{datetime.now():%Y%m%d_%H%M%S}.db"
bk = sqlite3.connect(destino)
conn.backup(bk)
bk.close()
print(f"Backup: {destino}")

agora = b.now_iso()
for comp, un, valor in plano:
    conn.execute(
        "INSERT INTO goals_unit (company_id, competence, unit_name, revenue_goal, returns_goal, created_at) "
        "VALUES (?, ?, ?, ?, 0, ?) ON CONFLICT(company_id, competence, unit_name) "
        "DO UPDATE SET revenue_goal = excluded.revenue_goal",
        (cid, comp, un, valor, agora))
conn.commit()
print(f"{len(plano)} metas gravadas. Reinicie o servico para limpar o cache das telas.")
