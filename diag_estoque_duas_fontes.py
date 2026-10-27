"""
O estoque do CRM e o do Radar concordam?

Uso (venv do RADAR, que é quem tem pandas):
    /srv/passini/venv/radar/bin/python /srv/passini/apps/crm-comercial/diag_estoque_duas_fontes.py [CODIGO...]

POR QUE ESTE DIAGNÓSTICO EXISTE

O mesmo relatório do Alfa (Stock Position) é importado DUAS VEZES: uma no
Radar e outra no CRM. O CRM guarda na tabela `item_stock`; o Radar, no
stock.pkl. As duas importações acontecem em momentos diferentes.

A aba Faltas lê a cópia do RADAR. O resto do CRM — ficha do cliente, sugestão
de mix, peça-isca — lê a cópia do CRM. Se as duas discordarem, o mesmo item
tem dois saldos no mesmo sistema, e nenhuma tela avisa qual está vendo.

Foi assim que a peça 80539 apareceu com 5 na Zona Sul numa tela, enquanto a
loja não tinha. Este script responde: as duas fontes dizem a mesma coisa? E
qual delas é a mais recente?

NÃO ALTERA NADA.
"""
import os
import sqlite3
import sys
from datetime import datetime
from pathlib import Path

try:
    import pandas as pd
except ImportError:
    print("Rode com o venv do RADAR: /srv/passini/venv/radar/bin/python ...")
    sys.exit(1)

STOCK_PKL = Path("/srv/passini/apps/radar-rupturas/runtime_data/sources/stock.pkl")
CRM_DB = Path(os.environ.get("PASSINI_CRM_DATA")
              or "/srv/passini/data/crm") / "passini_dashboard.db"
CODIGOS = [c.strip() for c in sys.argv[1:]] or ["101487", "80539"]

DE_PARA = {"PASSINI MATRIZ SAO LEOPOLDO": "MATRIZ", "PASSINI LAJEADO": "LAJEADO",
           "PASSINI PELOTAS": "PELOTAS", "PASSINI POA-ZONA SUL": "ZONA SUL",
           "PASSINI XANGRI-LÁ": "XANGRILA", "PASSINI POA-ZONA NORTE": "ZONA NORTE"}

conn = sqlite3.connect(f"file:{CRM_DB}?mode=ro", uri=True)
conn.row_factory = sqlite3.Row
cid = conn.execute("SELECT id FROM companies LIMIT 1").fetchone()["id"]

# ── 1. Qual é a mais nova ───────────────────────────────────────────────────
print("1) IDADE DAS DUAS CÓPIAS DO MESMO RELATÓRIO")
if STOCK_PKL.exists():
    q = datetime.fromtimestamp(STOCK_PKL.stat().st_mtime)
    print(f"   Radar  (stock.pkl)      {q:%d/%m/%Y %H:%M}")
else:
    print(f"   Radar  — {STOCK_PKL} não existe")
r = conn.execute(
    "SELECT MAX(updated_at) u, COUNT(*) n, COUNT(DISTINCT unit_name) un"
    "  FROM item_stock WHERE company_id = ?", (cid,)).fetchone()
print(f"   CRM    (item_stock)     {str(r['u'] or '—')[:16].replace('T', ' ')}"
      f"   {r['n']:,} linha(s), {r['un']} unidade(s)")
print("   >> Importações separadas do MESMO arquivo. A diferença de horário é")
print("      a diferença entre as duas verdades.")

# ── 2. O caso relatado ──────────────────────────────────────────────────────
print("\n2) OS CÓDIGOS PEDIDOS, LADO A LADO")
st = pd.read_pickle(STOCK_PKL) if STOCK_PKL.exists() else pd.DataFrame()
if not st.empty:
    st["item"] = st["item"].astype(str).str.strip()

print(f"   {'CÓDIGO':<10}{'UNIDADE':<13}{'RADAR':>8}{'CRM':>8}   {'ATUALIZADO NO CRM':<20}")
divergem = 0
for cod in CODIGOS:
    radar = {}
    if not st.empty:
        for _, linha in st[st["item"] == cod].iterrows():
            un = DE_PARA.get(str(linha["branchName"]).strip(),
                             str(linha["branchName"]).strip())
            radar[un] = float(linha["quantity"] or 0)
    crm = {r["unit_name"]: (float(r["quantity"] or 0), r["updated_at"])
           for r in conn.execute(
               "SELECT unit_name, quantity, updated_at FROM item_stock"
               " WHERE company_id = ? AND item_code = ?", (cid, cod))}
    for un in sorted(set(radar) | set(crm)):
        v_radar = radar.get(un)
        v_crm, quando = crm.get(un, (None, ""))
        marca = ""
        if v_radar is not None and v_crm is not None and abs(v_radar - v_crm) > 0.001:
            marca = "  << DIVERGEM"
            divergem += 1
        elif v_crm is None:
            marca = "  (só no Radar)"
        elif v_radar is None:
            marca = "  (só no CRM)"
        print(f"   {cod:<10}{un:<13}"
              f"{('—' if v_radar is None else f'{v_radar:.0f}'):>8}"
              f"{('—' if v_crm is None else f'{v_crm:.0f}'):>8}"
              f"   {str(quando or '')[:19]:<20}{marca}")

print(f"\n   {divergem} divergência(s) nos códigos pedidos.")

# ── 3. A divergência é geral ou só nestes itens? ────────────────────────────
print("\n3) AS DUAS FONTES DIVERGEM NO GERAL?")
if st.empty:
    print("   (sem o arquivo do Radar não dá para comparar)")
else:
    amostra = conn.execute(
        "SELECT unit_name, item_code, quantity FROM item_stock"
        " WHERE company_id = ? ORDER BY RANDOM() LIMIT 4000", (cid,)).fetchall()
    radar_idx = {}
    sub = st[st["item"].isin({r["item_code"] for r in amostra})]
    for _, linha in sub.iterrows():
        un = DE_PARA.get(str(linha["branchName"]).strip(),
                         str(linha["branchName"]).strip())
        radar_idx[(un, str(linha["item"]).strip())] = float(linha["quantity"] or 0)

    iguais = dif = ausentes = 0
    exemplos = []
    for r in amostra:
        chave = (r["unit_name"], r["item_code"])
        if chave not in radar_idx:
            ausentes += 1
            continue
        if abs(radar_idx[chave] - float(r["quantity"] or 0)) > 0.001:
            dif += 1
            if len(exemplos) < 6:
                exemplos.append(
                    f"{r['item_code']} em {r['unit_name']}: "
                    f"Radar {radar_idx[chave]:.0f} x CRM {float(r['quantity'] or 0):.0f}")
        else:
            iguais += 1
    total = iguais + dif
    print(f"   Amostra de {len(amostra):,} posições do CRM")
    print(f"      iguais nas duas fontes: {iguais:,}")
    print(f"      DIVERGENTES:            {dif:,}"
          + (f" ({100 * dif / total:.1f}%)" if total else ""))
    print(f"      sem par no Radar:       {ausentes:,}")
    for e in exemplos:
        print(f"      · {e}")
    if dif and total and dif / total > 0.02:
        print("\n   >> DIVERGÊNCIA GENERALIZADA. As duas cópias são de momentos")
        print("      diferentes. A aba Faltas usa a do Radar; o resto do CRM usa")
        print("      a dele. Precisa sobrar UMA fonte — e deve ser a do CRM, que")
        print("      é a que o sistema inteiro já consulta.")
    elif total:
        print("\n   >> As duas fontes concordam. A divergência relatada está entre")
        print("      o RELATÓRIO e a prateleira, não entre os nossos sistemas.")

conn.close()
print("\nNada foi alterado.")
