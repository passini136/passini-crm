"""
Qual coluna do Radar casa com qual chave do CRM?

Uso (venv do RADAR, que é quem tem pandas):
    /srv/passini/venv/radar/bin/python /srv/passini/apps/crm-comercial/diag_radar_chaves.py

POR QUE ESTE SEGUNDO DIAGNÓSTICO EXISTE

O primeiro cruzou a coluna chamada "gtin" do Radar com o campo GTIN do CRM e
achou 2 de 32.911. Zero, na prática. Mas a amostra do que não cruzou era
100000, 100001, 100002 — número sequencial de seis dígitos, que não é código
de barras nenhum. A coluna se chama gtin e não é GTIN.

A lição é não adivinhar de novo. Em vez de eu escolher a próxima coluna e
torcer, este diagnóstico TESTA TODAS contra TODAS: cada coluna de texto da
solicitação do Radar contra cada chave do CRM, e mostra a matriz. A chave
certa aparece sozinha, com percentual alto, e as erradas ficam no chão.

O mesmo vale para o cliente. A coluna Cliente existe — eu havia dito que não,
olhando o analytics.py, que a descarta porque o Radar não precisa dela. Ela
está lá, e se cruzar com o cadastro do CRM, a falta deixa de ser "faltou esta
peça nesta unidade" e passa a ser "esta oficina pediu e a gente não tinha".

Também confere o que o primeiro diagnóstico deixou passar: a quantidade
pedida, e as datas de 1970 (epoch) que apareceram no período coberto.

NÃO ALTERA NADA. Abre o banco do CRM em modo somente-leitura.
"""
import os
import re
import sqlite3
import sys
from pathlib import Path

try:
    import pandas as pd
except ImportError:
    print("Rode com o venv do RADAR: /srv/passini/venv/radar/bin/python ...")
    sys.exit(1)


def achar(candidatos, nome):
    for c in candidatos:
        if c and Path(c).exists():
            return Path(c)
    print(f">> Não encontrei {nome}. Procurei em: {candidatos}")
    sys.exit(1)


SOLIC = achar([
    (os.environ.get("RUNTIME_DIR", "") or "x") + "/sources/solicitacao.pkl",
    "/srv/passini/apps/radar-rupturas/runtime_data/sources/solicitacao.pkl",
    "/srv/passini/data/radar/runtime_data/sources/solicitacao.pkl",
], "a solicitação do Radar")
CRM_DB = achar([
    (os.environ.get("PASSINI_CRM_DATA", "") or "x") + "/passini_dashboard.db",
    "/srv/passini/data/crm/passini_dashboard.db",
], "o banco do CRM")

req = pd.read_pickle(SOLIC)
conn = sqlite3.connect(f"file:{CRM_DB}?mode=ro", uri=True)
conn.row_factory = sqlite3.Row
cid = conn.execute("SELECT id FROM companies LIMIT 1").fetchone()["id"]
print(f"Solicitação: {len(req):,} linhas, {req.shape[1]} colunas")
print(f"Banco CRM:   {CRM_DB}\n")

print("TODAS AS COLUNAS DA SOLICITAÇÃO:")
print("   " + " · ".join(str(c) for c in req.columns))


def limpa(v):
    """Tira o '.0' do Excel, espaço e caixa. Mesmo tratamento dos dois lados."""
    if v is None:
        return ""
    if isinstance(v, float):
        if pd.isna(v):
            return ""
        if v.is_integer():
            return str(int(v))
    t = re.sub(r"\s+", " ", str(v)).strip().upper()
    return t[:-2] if re.match(r"^\d+\.0$", t) else t


def conjunto_sql(sql, params=()):
    return {limpa(r[0]) for r in conn.execute(sql, params)} - {""}


# ── As chaves que o CRM tem para oferecer ───────────────────────────────────
print("\nCarregando as chaves do CRM...")
CHAVES = {
    "catálogo.item_code": conjunto_sql(
        "SELECT item_code FROM item_catalog WHERE company_id = ?", (cid,)),
    "catálogo.gtin": conjunto_sql(
        "SELECT gtin FROM item_catalog WHERE company_id = ?", (cid,)),
    "catálogo.manufacturer_ref": conjunto_sql(
        "SELECT manufacturer_ref FROM item_catalog WHERE company_id = ?", (cid,)),
    "faturamento.item_code": conjunto_sql(
        "SELECT DISTINCT item_code FROM fact_sales_detail WHERE company_id = ?", (cid,)),
    "faturamento.sku_key": conjunto_sql(
        "SELECT DISTINCT sku_key FROM fact_sales_detail WHERE company_id = ?", (cid,)),
    "faturamento.manufacturer_sku": conjunto_sql(
        "SELECT DISTINCT manufacturer_sku FROM fact_sales_detail WHERE company_id = ?", (cid,)),
    "cliente.client_code": conjunto_sql(
        "SELECT client_code FROM crm_client_profiles WHERE company_id = ?", (cid,)),
    "cliente.document_number": conjunto_sql(
        "SELECT document_number FROM crm_client_profiles WHERE company_id = ?", (cid,)),
    "cliente.client_name": conjunto_sql(
        "SELECT client_name FROM crm_client_profiles WHERE company_id = ?", (cid,)),
}
for nome, s in CHAVES.items():
    print(f"   {nome:<30}{len(s):>9,} valores")

# ── A matriz: cada coluna do Radar contra cada chave do CRM ─────────────────
# Teimar numa coluna porque o nome dela parece certo foi exatamente o erro do
# primeiro diagnóstico. Aqui o dado escolhe, não eu.
print("\nCRUZAMENTO DE TODAS CONTRA TODAS")
print("   (% dos valores distintos da coluna que existem na chave do CRM)\n")

colunas = {}
for c in req.columns:
    vals = {limpa(v) for v in req[c].dropna().unique()} - {""}
    # Coluna com 2 valores é bandeira, não chave; com 1 valor por linha e
    # nenhuma repetição costuma ser número de documento, não código.
    if 2 < len(vals) <= 400_000:
        colunas[str(c)] = vals

melhores = []
for nome_col, vals in colunas.items():
    for nome_chave, chave in CHAVES.items():
        if not chave:
            continue
        pct = 100 * len(vals & chave) / len(vals)
        if pct >= 5:
            melhores.append((pct, nome_col, nome_chave, len(vals & chave), len(vals)))

melhores.sort(reverse=True)
if not melhores:
    print("   NENHUM par cruzou acima de 5%. As duas bases não têm chave comum —")
    print("   a integração precisaria de um de-para construído à mão.")
else:
    print(f"   {'COLUNA DO RADAR':<22}{'CHAVE DO CRM':<30}{'CASA':>10}{'DE':>10}{'%':>8}")
    for pct, col, ch, n, tot in melhores[:18]:
        print(f"   {col[:21]:<22}{ch:<30}{n:>10,}{tot:>10,}{pct:>7.1f}%")

print("\n   >> Leitura: a chave de PEÇA e a chave de CLIENTE devem aparecer")
print("      cada uma com um campeão folgado. Dois campeões empatados na mesma")
print("      coluna querem dizer que as duas chaves do CRM são a mesma coisa.")

# ── A coluna Cliente, de perto ──────────────────────────────────────────────
print("\nA COLUNA CLIENTE")
col_cli = next((c for c in req.columns if str(c).strip().lower() == "cliente"), None)
if col_cli is None:
    print("   Ausente.")
else:
    vals = req[col_cli].map(limpa)
    preenchido = int(vals.ne("").sum())
    print(f"   Preenchida em {preenchido:,} de {len(req):,} "
          f"({100 * preenchido / len(req):.1f}%) · {vals.nunique():,} clientes distintos")
    amostra = [v for v in vals.unique() if v][:8]
    print("   Amostra: " + " | ".join(a[:28] for a in amostra))
    for nome_chave in ("cliente.client_code", "cliente.document_number", "cliente.client_name"):
        s = {v for v in vals.unique() if v}
        n = len(s & CHAVES[nome_chave])
        print(f"   contra {nome_chave:<26}{n:>8,} de {len(s):,} ({100 * n / max(1, len(s)):.1f}%)")
    print("   >> Se cruzar, a falta passa a ter dono: deixa de ser 'faltou peça")
    print("      na unidade' e vira 'esta oficina pediu e a gente não tinha'.")

# ── Quantidade e data ───────────────────────────────────────────────────────
print("\nQUANTIDADE PEDIDA")
col_qtd = next((c for c in req.columns if str(c).strip().lower() in ("qtd", "quantidade")), None)
if col_qtd is None:
    print("   Ausente — a perda só poderia ser contada em número de pedidos.")
else:
    q = pd.to_numeric(req[col_qtd], errors="coerce")
    print(f"   Numérica em {int(q.notna().sum()):,} de {len(req):,} linhas")
    print(f"   Soma: {q.sum():,.0f} · mediana: {q.median():.1f} · máximo: {q.max():,.0f}")
    extremos = int((q > 500).sum())
    if extremos:
        print(f"   >> {extremos:,} linha(s) acima de 500 unidades. Pedido de peça de")
        print("      reposição raramente passa disso — provável erro de digitação,")
        print("      e um só desses distorce o valor perdido do mês inteiro.")

print("\nDATAS")
col_data = next((c for c in req.columns if str(c).strip().lower() == "registro"), None)
if col_data is None:
    print("   Coluna Registro ausente.")
else:
    d = pd.to_datetime(req[col_data], errors="coerce", dayfirst=True)
    invalidas = int(d.isna().sum())
    epoch = int((d.dt.year <= 1970).sum())
    print(f"   Inválidas: {invalidas:,} · ano <= 1970: {epoch:,} · "
          f"válidas: {len(req) - invalidas:,}")
    boas = d[(d.dt.year > 1970)]
    if len(boas):
        print(f"   Período real: {boas.min():%Y-%m} a {boas.max():%Y-%m}")
    print("   >> O 1970 que apareceu no primeiro diagnóstico é data vazia virando")
    print("      epoch. Essas linhas têm de ficar de fora, senão todo mês ganha")
    print("      um histórico falso de janeiro de 1970.")

conn.close()
print("\nNada foi alterado.")
