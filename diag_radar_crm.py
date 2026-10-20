"""
O CRM consegue aproveitar a base de solicitações de compra do Radar?

Uso (precisa do venv do RADAR, que é quem tem pandas):
    /srv/passini/venv/radar/bin/python /srv/passini/apps/crm-comercial/diag_radar_crm.py

Por que este diagnóstico existe:

A ideia é o CRM parar de pedir o mesmo CSV duas vezes e ler o que o Radar já
importou. Só que as duas bases falam línguas diferentes, e o encontro delas
depende de três coincidências que NINGUÉM conferiu ainda:

  1. O GTIN da solicitação tem de existir no catálogo do CRM. Se não existir,
     o CRM sabe que faltou "7891234567890" e não sabe que peça é essa — a tela
     mostra um número e nada mais.
  2. O nome da unidade tem de cruzar. O Radar escreve ZONASUL; o CRM escreve
     ZONA SUL. Se o de-para falhar, a falta aparece na unidade errada, que é
     pior que não aparecer.
  3. A peça que faltou precisa ter histórico de venda no CRM, senão não há
     carteira para avisar — e o cruzamento, que é o motivo de tudo isto, não
     acontece.

Qualquer uma das três abaixo de um patamar razoável muda o desenho da Etapa 5.
Melhor descobrir agora, com uma leitura, do que depois de construir a tela.

Também mede o PESO: a solicitação é um pickle de ~32 MB. Este diagnóstico
cronometra a leitura para mostrar por que o CRM não pode carregá-lo a cada
consulta, e qual seria o tamanho da tabela enxuta que resolve isso.

NÃO ALTERA NADA. Só lê — e abre o banco do CRM em modo somente-leitura.
"""
import os
import re
import sqlite3
import sys
import time
from collections import Counter
from pathlib import Path

try:
    import pandas as pd
except ImportError:
    print("pandas não encontrado. Rode com o venv do RADAR:")
    print("  /srv/passini/venv/radar/bin/python "
          "/srv/passini/apps/crm-comercial/diag_radar_crm.py")
    sys.exit(1)


# ── Onde estão as duas bases ────────────────────────────────────────────────
# Os caminhos vêm de variável de ambiente nos dois apps, então procuramos em
# vez de chutar. Caminho chutado é a origem clássica de "funciona na minha
# máquina".
def achar(candidatos, nome):
    for c in candidatos:
        p = Path(c)
        if p.exists():
            return p
    print(f"\n   >> NÃO ENCONTREI {nome}. Procurei em:")
    for c in candidatos:
        print(f"      {c}")
    return None


SOLIC = achar([
    os.environ.get("RUNTIME_DIR", "") + "/sources/solicitacao.pkl",
    "/srv/passini/apps/radar-rupturas/runtime_data/sources/solicitacao.pkl",
    "/srv/passini/data/radar/runtime_data/sources/solicitacao.pkl",
], "a solicitação de compra do Radar")

CRM_DB = achar([
    os.environ.get("PASSINI_CRM_DATA", "") + "/passini_dashboard.db",
    "/srv/passini/data/crm/passini_dashboard.db",
    "/srv/passini/data/passini_dashboard.db",
], "o banco do CRM")

if not SOLIC or not CRM_DB:
    sys.exit(1)

print(f"Solicitação (Radar): {SOLIC}")
print(f"Banco (CRM):         {CRM_DB}\n")

# ── 1. O peso ───────────────────────────────────────────────────────────────
print("1) QUANTO CUSTA LER O ARQUIVO DO RADAR")
mb = SOLIC.stat().st_size / 1024 / 1024
t0 = time.time()
req = pd.read_pickle(SOLIC)
seg = time.time() - t0
print(f"   Arquivo: {mb:,.1f} MB   ·   leitura: {seg:.2f}s   ·   linhas: {len(req):,}")
print("   >> O CRM atende uma requisição por vez. Pagar isto a cada clique")
print("      trava a tela para todos os usuários ao mesmo tempo.")

# ── 2. O que o arquivo traz ─────────────────────────────────────────────────
print("\n2) QUAIS COLUNAS A SOLICITAÇÃO TEM")
cols = [str(c) for c in req.columns]
print(f"   {len(cols)} colunas: " + ", ".join(cols[:18]) + ("..." if len(cols) > 18 else ""))


def coluna(df, *nomes):
    """Acha a coluna pelo nome, ignorando acento, caixa e espaço."""
    alvo = {re.sub(r"[^a-z0-9]", "", n.lower()) for n in nomes}
    for c in df.columns:
        if re.sub(r"[^a-z0-9]", "", str(c).lower()) in alvo:
            return c
    return None


col_gtin = coluna(req, "GTIN_NORMALIZADO", "GTIN", "codigo")
col_emp = coluna(req, "Emp", "unidade", "Unidade_Normalizada")
col_user = coluna(req, "Usuario", "usuário")

# A PERGUNTA QUE DECIDE O ESCOPO. O Radar guarda O QUE faltou, não PARA QUEM.
# Se houver cliente aqui dentro, a Etapa 5 ganha uma perna inteira de graça.
col_cliente = coluna(req, "Cliente", "razao social", "razão social", "nome cliente",
                     "cnpj", "cpf", "documento")
col_valor = coluna(req, "Valor", "preco", "preço", "total", "custo")

print(f"   Código/GTIN: {col_gtin or '— ausente —'}")
print(f"   Unidade:     {col_emp or '— ausente —'}")
print(f"   Usuário:     {col_user or '— ausente —'}")
print(f"   Cliente:     {col_cliente or '— AUSENTE —'}")
print(f"   Valor:       {col_valor or '— AUSENTE —'}")
if not col_cliente:
    print("   >> Sem cliente, o Radar responde 'o que faltou na unidade', nunca")
    print("      'qual oficina ficou sem'. A falta por cliente continua sendo")
    print("      um dado que só nasce se o vendedor registrar no CRM.")

if not col_gtin:
    print("\n   >> Sem coluna de código não há cruzamento possível. Parando.")
    sys.exit(1)


def canonico(v):
    """Mesmo tratamento do Radar: tira o '.0' que o Excel cola nos números."""
    if v is None or (isinstance(v, float) and pd.isna(v)):
        return ""
    if isinstance(v, float) and v.is_integer():
        return str(int(v))
    t = str(v).strip()
    return t[:-2] if re.match(r"^\d+\.0$", t) else t


req["_gtin"] = req[col_gtin].map(canonico)
gtins = {g for g in req["_gtin"] if g}
print(f"\n   GTINs distintos na solicitação: {len(gtins):,}")
vazios = int((req['_gtin'].astype(str).str.strip() == "").sum())
print(f"   Linhas sem código: {vazios:,} de {len(req):,} "
      f"({100 * vazios / max(1, len(req)):.1f}%)")

# ── 3. O cruzamento com o catálogo do CRM ───────────────────────────────────
print("\n3) O GTIN DO RADAR EXISTE NO CATÁLOGO DO CRM?")
conn = sqlite3.connect(f"file:{CRM_DB}?mode=ro", uri=True)
conn.row_factory = sqlite3.Row
company_id = conn.execute("SELECT id FROM companies LIMIT 1").fetchone()["id"]

cat = {}
for r in conn.execute(
        "SELECT gtin, item_code FROM item_catalog "
        "WHERE company_id = ? AND TRIM(COALESCE(gtin,'')) <> ''", (company_id,)):
    cat.setdefault(canonico(r["gtin"]), r["item_code"])
print(f"   Catálogo do CRM com GTIN preenchido: {len(cat):,} itens")

achados = gtins & set(cat)
pct = 100 * len(achados) / max(1, len(gtins))
print(f"   GTINs do Radar encontrados no catálogo: {len(achados):,} de {len(gtins):,} ({pct:.1f}%)")
if pct < 50:
    print("   >> ABAIXO DE 50%. Metade das faltas apareceria no CRM como um")
    print("      número de barras sem peça, sem marca e sem preço. A tela")
    print("      precisaria de outra chave antes de ser construída.")
elif pct < 80:
    print("   >> Cruza, mas com buraco. Vale ver na amostra abaixo se o que não")
    print("      cruza é peça de verdade ou lixo de cadastro.")
else:
    print("   >> Cruza bem. O CRM consegue nomear a peça que faltou.")

perdidos = sorted(gtins - set(cat))[:10]
if perdidos:
    print("   Amostra do que NÃO cruzou: " + " · ".join(p[:16] for p in perdidos))

# ── 4. A peça que faltou tem comprador no CRM? ──────────────────────────────
# Este é o número que justifica a Etapa 5 inteira: faltou uma peça que gente
# COMPRA. Se ninguém compra, a falta é ruído de cadastro, não perda de venda.
print("\n4) QUEM FALTOU TEM HISTÓRICO DE VENDA NO CRM?")
codigos = [cat[g] for g in achados]
com_venda = 0
if codigos:
    t0 = time.time()
    for i in range(0, len(codigos), 400):
        lote = codigos[i:i + 400]
        marcas = ",".join("?" * len(lote))
        com_venda += conn.execute(
            f"SELECT COUNT(DISTINCT item_code) n FROM fact_sales_detail "
            f"WHERE company_id = ? AND item_code IN ({marcas})",
            [company_id, *lote]).fetchone()["n"]
    print(f"   Apurado em {time.time() - t0:.1f}s")
print(f"   Peças que faltaram E já venderam no CRM: {com_venda:,} de {len(achados):,}")
if achados:
    print(f"   >> {100 * com_venda / len(achados):.0f}% das faltas são de peça com")
    print("      demanda comprovada. É sobre essas que a carteira tem o que dizer.")

# ── 5. As unidades cruzam? ──────────────────────────────────────────────────
# O Radar escreve ZONASUL; o CRM escreve ZONA SUL. Errar aqui não dá erro:
# dá número certo na unidade errada, que ninguém percebe.
print("\n5) O NOME DA UNIDADE CRUZA ENTRE OS DOIS?")
if col_emp:
    radar_un = Counter(str(v).strip() for v in req[col_emp].fillna("") if str(v).strip())
    crm_un = {r["unit_name"] for r in conn.execute(
        "SELECT DISTINCT unit_name FROM fact_unit_summary WHERE company_id = ?",
        (company_id,)) if r["unit_name"]}
    print(f"   Unidades no CRM: {', '.join(sorted(crm_un))}")

    # A TABELA DE VERDADE, NÃO SEMELHANÇA DE NOME.
    #
    # A primeira versão daqui comparava os rótulos por parecença e acusou
    # "04 POA" como sem destino — quando o CRM sabe há muito tempo que 04 POA
    # é a Zona Sul. Diagnóstico que inventa problema é pior que diagnóstico
    # nenhum: manda consertar o que está certo. Então lemos o de-para real do
    # backend do CRM, sem importá-lo (isto roda no venv do Radar, que não tem
    # as dependências do CRM) — só extraímos o dicionário do código-fonte.
    de_para = {}
    fonte = Path(__file__).resolve().parent / "backend.py"
    try:
        import ast
        arvore = ast.parse(fonte.read_text(encoding="utf-8"))
        for no in arvore.body:
            if isinstance(no, ast.Assign) and any(
                    getattr(a, "id", "") == "UNIT_NORMALIZATION" for a in no.targets):
                de_para = ast.literal_eval(no.value)
                break
    except Exception as e:
        print(f"   (não consegui ler UNIT_NORMALIZATION de backend.py: {e})")
    print(f"   De-para do CRM: {len(de_para)} rótulos conhecidos")
    print(f"\n   {'RÓTULO NO RADAR':<28}{'LINHAS':>10}   DE-PARA NO CRM")

    sem_para = 0
    for rotulo, n in radar_un.most_common(14):
        # normalize_unit() do CRM: maiúscula, espaço colapsado, consulta o mapa.
        base = re.sub(r"\s+", " ", str(rotulo).upper()).strip()
        destino = de_para.get(base, "")
        if destino not in crm_un:
            destino = destino if destino in crm_un else ""
        if not destino:
            sem_para += 1
        print(f"   {rotulo[:27]:<28}{n:>10}   {destino or '← SEM DE-PARA'}")
    if sem_para:
        print(f"\n   >> {sem_para} rótulo(s) sem destino. Esses viram falta em")
        print("      unidade nenhuma, ou pior, na unidade errada.")
    else:
        print("\n   >> Todo rótulo do Radar encontra unidade no CRM.")
else:
    print("   Coluna de unidade ausente — impossível conferir.")

# ── 6. O tamanho da tabela enxuta ───────────────────────────────────────────
# A proposta é o Radar gravar isto uma vez por importação, e o CRM só ler.
print("\n6) QUANTO FICARIA A TABELA ENXUTA QUE O CRM LERIA")
col_data = coluna(req, "Data", "Registro", "AnoMes")
if col_data is not None and col_gtin and col_emp:
    tmp = pd.DataFrame({
        "unidade": req[col_emp].fillna("").astype(str),
        "gtin": req["_gtin"],
    })
    tmp["mes"] = pd.to_datetime(req[col_data], errors="coerce", dayfirst=True).dt.strftime("%Y-%m")
    tmp = tmp[tmp["gtin"].ne("") & tmp["mes"].notna()]
    agrup = tmp.groupby(["unidade", "mes", "gtin"]).size()
    print(f"   Linhas cruas hoje:            {len(req):,}")
    print(f"   Linhas agrupadas por unidade × mês × GTIN: {len(agrup):,}")
    print(f"   Redução: {100 * (1 - len(agrup) / max(1, len(req))):.0f}%")
    meses = sorted(tmp['mes'].unique())
    print(f"   Período coberto: {meses[0]} a {meses[-1]} ({len(meses)} meses)")
    print("   >> Isso cabe num SQLite de poucos MB, lido em milissegundos,")
    print("      e é tudo que a tela do CRM precisa mostrar.")
else:
    print("   Faltou coluna de data, unidade ou código para estimar.")

conn.close()
print("\nNada foi alterado.")
