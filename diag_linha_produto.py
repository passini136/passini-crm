"""
A visão por Linha/Grupo fecha com o faturamento do mês?

Uso:
    /srv/passini/venv/crm/bin/python /srv/passini/apps/crm-comercial/diag_linha_produto.py

O JOIN entre catálogo e faturamento mudou de chave. Duas coisas podem dar
errado, e as duas são silenciosas:

  - FALTAR: a soma por linha fica abaixo do mês, e cada linha parece ter
    vendido menos do que vendeu.
  - SOBRAR: referência repetida no catálogo duplica a venda, e a soma passa do
    mês. Esse é o perigoso — número maior ninguém contesta.

Aqui as três dimensões (marca, linha, grupo) são somadas e comparadas com o
faturamento cru do mês. Marca não depende do catálogo, então serve de controle:
se marca fecha e linha não, o problema é o casamento, não a consulta.

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
comp = (backend.query_competences(conn, company_id) or [""])[0]
print(f"Banco: {backend.DB_PATH}")
print(f"Competência: {comp}\n")

bruto = conn.execute(
    "SELECT ROUND(SUM(net_value),2) v, COUNT(*) n FROM fact_sales_detail "
    "WHERE company_id = ? AND competence = ?", (company_id, comp)).fetchone()
total = float(bruto["v"] or 0)
print(f"Faturamento cru do mês: {backend.brl(total)} em {bruto['n']} linha(s)\n")

print(f"{'DIMENSÃO':<10}{'GRUPOS':>8}{'SOMA':>18}{'% DO MÊS':>10}   SITUAÇÃO")
problemas = 0
for dim in ("marca", "linha", "grupo"):
    linhas = backend.brand_ranking_rows(conn, company_id, comp, None, dim)
    soma = sum(v["revenue"] for v in linhas.values())
    pct = 100 * soma / total if total else 0
    if soma > total + 0.01:
        situacao = f"⚠ SOBRA {backend.brl(soma - total)} — está duplicando"
        problemas += 1
    elif pct >= 99:
        situacao = "ok"
    elif pct >= 90:
        situacao = f"falta {backend.brl(total - soma)} (item sem cadastro)"
    else:
        situacao = f"⚠ falta {backend.brl(total - soma)} — casamento ruim"
        problemas += 1
    print(f"{dim:<10}{len(linhas):>8}{backend.brl(soma):>18}{pct:>9.1f}%   {situacao}")

# ── As maiores linhas, para conferir se fazem sentido ────────────────────────
print("\nAS 12 MAIORES LINHAS DE PRODUTO DO MÊS")
linhas = backend.brand_ranking_rows(conn, company_id, comp, None, "linha")
top = sorted(linhas.values(), key=lambda x: -x["revenue"])[:12]
print(f"   {'LINHA':<32}{'FATURADO':>16}{'ITENS':>9}{'CLIENTES':>10}")
for r in top:
    print(f"   {str(r['brand'])[:31]:<32}{backend.brl(r['revenue']):>16}"
          f"{r['items']:>9}{r['clients']:>10}")

print("\nLEITURA")
if problemas:
    print("   >> Corrija antes de usar a tela. Número que sobra é pior que tela vazia:")
    print("      a tela vazia ninguém usa; o número inflado vira decisão de compra.")
else:
    print("   As três dimensões fecham. A visão por Linha/Grupo pode ser usada,")
    print("   e serve de base para a sugestão de recompra por linha.")
    print("   O que falta para 100% são itens vendidos que não estão no catálogo —")
    print("   normal, e o catálogo atualizado reduz isso sozinho.")

conn.close()
