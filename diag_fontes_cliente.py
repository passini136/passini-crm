"""
Os R$ 170 mil entre o resumo por cliente e o custo × venda são estruturais?

Uso:
    /srv/passini/venv/crm/bin/python /srv/passini/apps/crm-comercial/diag_fontes_cliente.py

A composição por cliente (ticket, PF/PJ, carteira x balcão) sai de
`crm_client_summary`; o resultado oficial sai do custo × venda. São arquivos
DIFERENTES do Alfa, e já sabemos que arquivos diferentes não fecham entre si.
Mas "não fecha" tem duas versões, e elas pedem ações opostas:

  A) DIFERENÇA ESTRUTURAL — os dois relatórios medem coisas ligeiramente
     diferentes, todo mês, na mesma proporção. Nesse caso a tela só precisa
     declarar a cobertura e seguir: a composição descreve bem o mês.
  B) DEFEITO DE IMPORTAÇÃO — mês com arquivo faltando, sobreposto ou parcial.
     Aí a composição está errada e corrigir o dado vem antes da tela.

O que separa: CONSISTÊNCIA. Desvio parecido em todos os meses é (A). Desvio que
pula de 0% para 20% é (B) — foi assim que o detalhado apareceu 69% acima do
oficial em agosto, por sobreposição dos relatórios diários.

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

# ── 1. O desvio é o mesmo todo mês? ─────────────────────────────────────────
print("1) O DESVIO É CONSISTENTE ENTRE OS MESES?")
print(f"   {'MÊS':<9}{'RESUMO CLIENTE':>17}{'CUSTO x VENDA':>17}{'DIFERENÇA':>15}{'%':>8}{'IMPORTS':>9}")
desvios = []
for c in sorted(backend.query_competences(conn, company_id))[-8:]:
    cli = float(conn.execute(
        "SELECT COALESCE(SUM(net_value),0) v FROM crm_client_summary "
        "WHERE company_id = ? AND competence = ?", (company_id, c)).fetchone()["v"])
    ofi = float(conn.execute(
        "SELECT COALESCE(SUM(net_value),0) v FROM fact_unit_summary "
        "WHERE company_id = ? AND competence = ?", (company_id, c)).fetchone()["v"])
    imps = int(conn.execute(
        "SELECT COUNT(DISTINCT import_id) n FROM crm_client_summary "
        "WHERE company_id = ? AND competence = ?", (company_id, c)).fetchone()["n"])
    if not ofi:
        continue
    pct = 100 * (cli - ofi) / ofi
    desvios.append(pct)
    alerta = "  ← MAIS DE 1 ARQUIVO" if imps > 1 else ""
    print(f"   {c:<9}{backend.brl(cli):>17}{backend.brl(ofi):>17}"
          f"{backend.brl(cli - ofi):>15}{pct:>7.1f}%{imps:>9}{alerta}")

if len(desvios) >= 3:
    faixa = max(desvios) - min(desvios)
    print(f"\n   Desvio entre {min(desvios):.1f}% e {max(desvios):.1f}% "
          f"· amplitude {faixa:.1f} pontos")
    if faixa < 3:
        print("   >> ESTRUTURAL. Os dois relatórios medem coisas um pouco")
        print("      diferentes, de forma estável. A composição descreve bem o")
        print("      mês; a tela só precisa declarar a cobertura.")
    else:
        print("   >> INSTÁVEL. Isso não é diferença de relatório, é problema de")
        print("      importação em algum mês. Achar qual antes de confiar na")
        print("      composição — ver o mês que destoa acima.")

# ── 2. De onde vem a diferença: vendedor ou cliente? ────────────────────────
# Se um punhado de vendedores concentra o desvio, é recorte de arquivo. Se está
# espalhado por todos, é diferença de critério do relatório.
comp = backend.crm_latest_competence(conn, company_id)
print(f"\n2) ONDE ESTÁ A DIFERENÇA EM {comp} — por vendedor")
print(f"   {'VENDEDOR':<28}{'RESUMO CLI':>15}{'CUSTO x VENDA':>16}{'DIF':>14}{'%':>8}")
por_vendedor = {}
for r in conn.execute(
    "SELECT seller_name, COALESCE(SUM(net_value),0) v FROM crm_client_summary "
    "WHERE company_id = ? AND competence = ? GROUP BY seller_name",
        (company_id, comp)).fetchall():
    chave = backend.chave_canonica(conn, company_id,
                                   backend.normalize_whitespace(r["seller_name"]))
    por_vendedor.setdefault(chave, [r["seller_name"], 0.0, 0.0])[1] += float(r["v"])
for r in conn.execute(
    "SELECT seller_name, COALESCE(SUM(net_value),0) v FROM fact_vendor_summary "
    "WHERE company_id = ? AND competence = ? GROUP BY seller_name",
        (company_id, comp)).fetchall():
    chave = backend.chave_canonica(conn, company_id,
                                   backend.normalize_whitespace(r["seller_name"]))
    por_vendedor.setdefault(chave, [r["seller_name"], 0.0, 0.0])[2] += float(r["v"])

linhas = sorted(por_vendedor.values(), key=lambda x: abs(x[1] - x[2]), reverse=True)
soma_dif = sum(abs(x[1] - x[2]) for x in linhas)
for nome, cli, ofi in linhas[:12]:
    pct = (100 * (cli - ofi) / ofi) if ofi else None
    ptxt = f"{pct:.0f}%" if pct is not None else "só resumo"
    print(f"   {backend.normalize_whitespace(nome)[:27]:<28}{backend.brl(cli):>15}"
          f"{backend.brl(ofi):>16}{backend.brl(cli - ofi):>14}{ptxt:>8}")

top3 = sum(abs(x[1] - x[2]) for x in linhas[:3])
print(f"\n   Os 3 maiores concentram {100 * top3 / soma_dif if soma_dif else 0:.0f}% "
      f"da diferença absoluta")
if soma_dif and top3 / soma_dif > 0.6:
    print("   >> CONCENTRADO em poucos vendedores. Cheira a recorte de arquivo ou")
    print("      vendedor que existe num relatório e não no outro — não a")
    print("      diferença de critério.")
else:
    print("   >> ESPALHADO por todos. É diferença de CRITÉRIO entre os dois")
    print("      relatórios, não arquivo faltando. Conviver e declarar.")

# ── 3. Alguém existe só de um lado? ────────────────────────────────────────
print(f"\n3) VENDEDOR PRESENTE EM UM RELATÓRIO E AUSENTE NO OUTRO")
achou = False
for nome, cli, ofi in linhas:
    if (cli > 0) != (ofi > 0):
        achou = True
        lado = "só no resumo por cliente" if cli > 0 else "só no custo × venda"
        print(f"   {backend.normalize_whitespace(nome)[:32]:<34}"
              f"{backend.brl(max(cli, ofi)):>14}   {lado}")
if not achou:
    print("   Nenhum. Os dois relatórios cobrem as mesmas pessoas.")

conn.close()
