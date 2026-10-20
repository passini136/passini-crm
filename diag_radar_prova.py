"""
A chave de peça é real ou é colisão numérica?

Uso (venv do RADAR):
    /srv/passini/venv/radar/bin/python /srv/passini/apps/crm-comercial/diag_radar_prova.py

POR QUE ESTE TERCEIRO DIAGNÓSTICO EXISTE

A matriz anterior disse que a coluna Qtd do Radar cruza 89% com o código de
cliente do CRM. Quantidade pedida não é código de cliente. O cadastro tem
101.976 clientes com código numérico denso — qualquer coluna de números bate
com ele por acaso. A matriz estava medindo coincidência com a mesma régua que
mede cruzamento, e por isso não serve para decidir nada sozinha.

Aqui a pergunta é outra: o acerto SOBREVIVE a um controle?

Duas provas, e as duas têm de passar:

  1. CONTROLE CEGO. Troco cada código por um número aleatório do mesmo
     tamanho e cruzo de novo. Esse percentual é o quanto se acerta sem saber
     nada — o piso do acaso. Chave de verdade fica muito acima dele; colisão
     fica colada nele.

  2. O CADASTRO CONCORDA? Casada a peça, comparo o que as duas bases dizem
     dela: o Fabricante do Radar contra o fabricante do catálogo, o Tipo
     contra o tipo. Número igual por acaso é comum; número igual E descrição
     igual, não. Esta é a prova que não tem como fraudar.

Mede também o que interessa ao negócio: das peças que o CRM realmente vende,
quantas já tiveram falta registrada.

NÃO ALTERA NADA. Banco do CRM em modo somente-leitura.
"""
import os
import random
import re
import sqlite3
import sys
from pathlib import Path

try:
    import pandas as pd
except ImportError:
    print("Rode com o venv do RADAR: /srv/passini/venv/radar/bin/python ...")
    sys.exit(1)

random.seed(20261020)


def achar(candidatos, nome):
    for c in candidatos:
        if c and Path(c).exists():
            return Path(c)
    print(f">> Não encontrei {nome}.")
    sys.exit(1)


SOLIC = achar([
    (os.environ.get("RUNTIME_DIR", "") or "x") + "/sources/solicitacao.pkl",
    "/srv/passini/apps/radar-rupturas/runtime_data/sources/solicitacao.pkl",
], "a solicitação do Radar")
CRM_DB = achar([
    (os.environ.get("PASSINI_CRM_DATA", "") or "x") + "/passini_dashboard.db",
    "/srv/passini/data/crm/passini_dashboard.db",
], "o banco do CRM")

req = pd.read_pickle(SOLIC)
conn = sqlite3.connect(f"file:{CRM_DB}?mode=ro", uri=True)
conn.row_factory = sqlite3.Row
cid = conn.execute("SELECT id FROM companies LIMIT 1").fetchone()["id"]
print(f"Solicitação: {len(req):,} linhas\n")


def limpa(v):
    if v is None:
        return ""
    if isinstance(v, float):
        if pd.isna(v):
            return ""
        if v.is_integer():
            return str(int(v))
    t = re.sub(r"\s+", " ", str(v)).strip().upper()
    return t[:-2] if re.match(r"^\d+\.0$", t) else t


CANDIDATAS = [c for c in req.columns
              if str(c) in ("gtin", "GTIN", "GTIN_NORMALIZADO", "Codigo", "Qtd")]

CHAVES = {}
for nome, sql in (
    ("catálogo.item_code", "SELECT item_code FROM item_catalog WHERE company_id = ?"),
    ("cliente.client_code", "SELECT client_code FROM crm_client_profiles WHERE company_id = ?"),
):
    CHAVES[nome] = {limpa(r[0]) for r in conn.execute(sql, (cid,))} - {""}

# ── Prova 1: o controle cego ────────────────────────────────────────────────
print("1) CONTROLE CEGO — quanto se acerta chutando")
print("   Cada código vira um número aleatório do MESMO tamanho. O que sobrar")
print("   de acerto é puro acaso.\n")


def sortear_igual(v):
    """Número aleatório com a mesma quantidade de dígitos; texto fica texto."""
    if v.isdigit():
        return str(random.randint(10 ** (len(v) - 1), 10 ** len(v) - 1)) if len(v) > 1 \
            else str(random.randint(0, 9))
    return "".join(str(random.randint(0, 9)) if ch.isdigit() else ch for ch in v)


print(f"   {'COLUNA':<20}{'CHAVE DO CRM':<24}{'REAL':>9}{'ACASO':>9}{'VEREDITO':>14}")
for col in CANDIDATAS:
    vals = {limpa(v) for v in req[col].dropna().unique()} - {""}
    if len(vals) < 3:
        continue
    amostra = list(vals) if len(vals) <= 20000 else random.sample(sorted(vals), 20000)
    controle = {sortear_igual(v) for v in amostra}
    for nome_chave, chave in CHAVES.items():
        real = 100 * len({v for v in amostra if v in chave}) / len(amostra)
        acaso = 100 * len(controle & chave) / len(controle)
        if real < 5:
            continue
        # Acerto que o acaso explica não é chave. A folga é o que vale.
        if real >= acaso * 2 and real - acaso >= 25:
            vereditos = "CHAVE REAL"
        elif real - acaso >= 10:
            vereditos = "duvidoso"
        else:
            vereditos = "← COLISÃO"
        print(f"   {str(col)[:19]:<20}{nome_chave:<24}{real:>8.1f}%{acaso:>8.1f}%{vereditos:>14}")

# ── Prova 2: as duas bases descrevem a mesma peça? ──────────────────────────
print("\n2) O CADASTRO CONCORDA COM O RADAR?")
print("   Casada a peça pelo código, as descrições têm de bater. Número igual")
print("   por acaso acontece; número igual e fabricante igual, não.\n")

cat = {}
for r in conn.execute(
        "SELECT item_code, manufacturer_ref, item_type, brand_name "
        "FROM item_catalog WHERE company_id = ?", (cid,)):
    cat.setdefault(limpa(r["item_code"]), r)

col_fab = next((c for c in req.columns if str(c).strip().lower() == "fabricante"), None)
col_tipo = next((c for c in req.columns if str(c).strip().lower() == "tipo"), None)

print(f"   {'COLUNA':<22}{'CASOU':>10}{'FABRIC. IGUAL':>16}{'TIPO IGUAL':>13}")
melhor = ("", -1.0)
for col in CANDIDATAS:
    sub = req[[c for c in (col, col_fab, col_tipo) if c is not None]].copy()
    sub["_k"] = sub[col].map(limpa)
    sub = sub[sub["_k"].ne("")]
    if sub.empty:
        continue
    # Amostra: 20 mil linhas bastam e mantêm o diagnóstico em segundos.
    if len(sub) > 20000:
        sub = sub.sample(20000, random_state=1)
    casou = fab_ok = tipo_ok = 0
    for _, linha in sub.iterrows():
        c = cat.get(linha["_k"])
        if not c:
            continue
        casou += 1
        if col_fab is not None and limpa(linha[col_fab]):
            if limpa(linha[col_fab]) == limpa(c["manufacturer_ref"]):
                fab_ok += 1
        if col_tipo is not None and limpa(linha[col_tipo]):
            if limpa(linha[col_tipo]) == limpa(c["item_type"]):
                tipo_ok += 1
    if not casou:
        print(f"   {str(col)[:21]:<22}{0:>10}{'—':>16}{'—':>13}")
        continue
    pf, pt = 100 * fab_ok / casou, 100 * tipo_ok / casou
    print(f"   {str(col)[:21]:<22}{casou:>10,}{pf:>15.1f}%{pt:>12.1f}%")
    if pf > melhor[1]:
        melhor = (str(col), pf)

print(f"\n   >> Campeã: {melhor[0]} com {melhor[1]:.1f}% de fabricante igual.")
print("      Acima de 80% é a chave. Abaixo de 20% é número batendo por acaso")
print("      com peça que não tem nada a ver — e a tela mostraria a peça errada,")
print("      que é o pior desfecho possível: confiável e errado.")

# ── 3. Quanto do que a Passini vende já teve falta ──────────────────────────
print("\n3) DAS PEÇAS QUE A PASSINI VENDE, QUANTAS JÁ FALTARAM?")
vendidas = {limpa(r[0]) for r in conn.execute(
    "SELECT DISTINCT item_code FROM fact_sales_detail WHERE company_id = ? "
    "AND TRIM(COALESCE(item_code,'')) <> ''", (cid,))} - {""}
if melhor[0]:
    pedidas = {limpa(v) for v in req[melhor[0]].dropna().unique()} - {""}
    cruz = vendidas & pedidas
    print(f"   Peças com venda no CRM:        {len(vendidas):,}")
    print(f"   Peças com falta no Radar:      {len(pedidas):,}")
    print(f"   Vendem E faltaram:             {len(cruz):,} "
          f"({100 * len(cruz) / max(1, len(vendidas)):.1f}% do que se vende)")
    print("   >> Esta é a lista que interessa à carteira: peça com demanda")
    print("      comprovada que a loja não tinha. O resto é ruído de cadastro.")

# ── 4. As datas, direito ────────────────────────────────────────────────────
# O diagnóstico anterior imprimiu "inválidas: 0 · válidas: 263.091" e ainda
# assim 6.873 linhas em 1970. A conta estava errada: eu somava como válida a
# linha que virou epoch. Aqui a válida exclui o epoch, como tem de ser.
print("\n4) DATAS APROVEITÁVEIS")
col_data = next((c for c in req.columns if str(c).strip().lower() == "registro"), None)
if col_data is not None:
    d = pd.to_datetime(req[col_data], errors="coerce", dayfirst=True)
    epoch = (d.dt.year <= 1970) | d.isna()
    boas = d[~epoch]
    print(f"   Descartar (vazia ou 1970): {int(epoch.sum()):,}")
    print(f"   Aproveitáveis:             {len(boas):,} "
          f"({100 * len(boas) / len(req):.1f}%)")
    if len(boas):
        print(f"   Período real: {boas.min():%Y-%m} a {boas.max():%Y-%m} "
              f"({boas.dt.strftime('%Y-%m').nunique()} meses)")
        ult = boas.dt.strftime("%Y-%m").value_counts().sort_index().tail(6)
        print("   Últimos meses: " + " · ".join(f"{m}:{n:,}" for m, n in ult.items()))

conn.close()
print("\nNada foi alterado.")
