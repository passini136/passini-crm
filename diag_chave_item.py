"""
Qual coluna do catálogo casa com qual coluna do faturamento.

Uso:
    /srv/passini/venv/crm/bin/python /srv/passini/apps/crm-comercial/diag_chave_item.py

A tela de Linha/Grupo junta catálogo e faturamento por uma chave, e a chave em
uso casa ZERO. Antes de escolher outra no chute, este script testa TODAS as
combinações — quatro colunas do catálogo contra três do faturamento, cada uma
em quatro formas de normalizar — e mostra a amostra dos valores dos dois lados.

Ver os valores importa tanto quanto a taxa: código com zero à esquerda, com
traço, ou com prefixo de fabricante não casa por igualdade, mas casa depois de
limpo. A amostra diz qual limpeza é a certa.

Não altera nada.
"""
import os
import re
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

# ── Normalizações candidatas ─────────────────────────────────────────────────
def cru(v):
    return (v or "").strip()

def maiusculo(v):
    return cru(v).upper()

def sem_zeros(v):
    return maiusculo(v).lstrip("0")

def so_alfanumerico(v):
    return re.sub(r"[^0-9A-Z]", "", maiusculo(v)).lstrip("0")

FORMAS = [("cru", cru), ("maiúsculo", maiusculo),
          ("sem zero à esq.", sem_zeros), ("só alfanumérico", so_alfanumerico)]

COLS_CATALOGO = ["item_code", "gtin", "supplier_ref", "manufacturer_ref"]
COLS_VENDA = ["manufacturer_sku", "sku_key", "gtin_value"]

# ── 1. Amostra dos valores ───────────────────────────────────────────────────
print("1) COMO OS IDENTIFICADORES SE PARECEM (5 exemplos de cada)")
print("\n   CATÁLOGO (item_catalog)")
for c in COLS_CATALOGO:
    vals = [str(r[0]) for r in conn.execute(
        f"SELECT {c} FROM item_catalog WHERE company_id = ? AND TRIM(COALESCE({c},'')) <> '' LIMIT 5",
        (company_id,)).fetchall()]
    print(f"      {c:<20}{' | '.join(vals) if vals else '(todos vazios)'}")

print("\n   FATURAMENTO (fact_sales_detail)")
for c in COLS_VENDA:
    vals = [str(r[0]) for r in conn.execute(
        f"SELECT {c} FROM fact_sales_detail WHERE company_id = ? AND competence = ? "
        f"AND TRIM(COALESCE({c},'')) <> '' LIMIT 5", (company_id, comp)).fetchall()]
    print(f"      {c:<20}{' | '.join(vals) if vals else '(todos vazios)'}")

# ── 2. Carrega os dois lados uma vez ─────────────────────────────────────────
catalogo = conn.execute(
    f"SELECT {', '.join(COLS_CATALOGO)} FROM item_catalog WHERE company_id = ?",
    (company_id,)).fetchall()
vendas = conn.execute(
    f"SELECT {', '.join(COLS_VENDA)}, net_value FROM fact_sales_detail "
    f"WHERE company_id = ? AND competence = ?", (company_id, comp)).fetchall()
valor_total = sum(float(r["net_value"] or 0) for r in vendas)
print(f"\n   {len(catalogo)} itens no catálogo · {len(vendas)} linhas de venda no mês "
      f"· {backend.brl(valor_total)}")

# ── 3. Todas as combinações ──────────────────────────────────────────────────
print("\n2) TAXA DE CASAMENTO — TODAS AS COMBINAÇÕES")
print(f"   {'CATÁLOGO':<18}{'FATURAMENTO':<20}{'FORMA':<18}{'% LINHAS':>10}{'% VALOR':>10}")
resultados = []
for forma_nome, forma in FORMAS:
    conjuntos = {c: {forma(r[c]) for r in catalogo if forma(r[c])} for c in COLS_CATALOGO}
    for cc in COLS_CATALOGO:
        alvo = conjuntos[cc]
        if not alvo:
            continue
        for cv in COLS_VENDA:
            casou = 0
            valor = 0.0
            for r in vendas:
                if forma(r[cv]) and forma(r[cv]) in alvo:
                    casou += 1
                    valor += float(r["net_value"] or 0)
            pl = 100 * casou / len(vendas) if vendas else 0
            pv = 100 * valor / valor_total if valor_total else 0
            resultados.append((pv, pl, cc, cv, forma_nome))

resultados.sort(reverse=True)
for pv, pl, cc, cv, forma_nome in resultados[:12]:
    marca = ""
    if cc == "item_code" and cv == "gtin_value" and forma_nome == "cru":
        marca = "  << a que está em uso"
    print(f"   {cc:<18}{cv:<20}{forma_nome:<18}{pl:>9.1f}%{pv:>9.1f}%{marca}")

print("\n3) LEITURA")
melhor = resultados[0] if resultados else None
if not melhor or melhor[0] < 5:
    print("   >> NENHUMA combinação casa. Os dois arquivos não compartilham identificador.")
    print("      A visão por Linha/Grupo não tem como funcionar com os dados de hoje —")
    print("      o cadastro de itens precisa sair do Alfa com a mesma coluna que o")
    print("      faturamento traz, ou o faturamento com a coluna que o catálogo traz.")
elif melhor[0] < 80:
    print(f"   >> A melhor é {melhor[2]} x {melhor[3]} ({melhor[4]}): {melhor[0]:.1f}% do valor.")
    print("      Melhor que zero, mas ainda deixa muita venda de fora. Vale entender")
    print("      o que não casa antes de construir em cima.")
else:
    print(f"   >> Trocar para {melhor[2]} x {melhor[3]} ({melhor[4]}) casa {melhor[0]:.1f}% do valor.")
    print("      É a chave certa. Ajustar o JOIN da tela de Marcas resolve.")

conn.close()
