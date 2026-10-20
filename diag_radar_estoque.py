"""
O estoque da família responde "a falta foi resolvida?" — e de quem é o pedido?

Uso (venv do RADAR):
    /srv/passini/venv/radar/bin/python /srv/passini/apps/crm-comercial/diag_radar_estoque.py

DUAS PERGUNTAS, PORQUE AS DUAS BLOQUEIAM O PAINEL

(A) RESOLVEU? A regra central do Radar é que ruptura total só existe quando
    o estoque da FAMÍLIA de substitutos, naquela unidade, é zero. Peça pedida
    cujo substituto está na prateleira não é ruptura — é escolha. Perguntar
    "tem estoque?" item a item ignoraria isso e inflaria a ruptura.

    Este diagnóstico usa as funções do PRÓPRIO Radar (gerar_familias_substitutos
    e _prepare_stock), importadas, não reescritas. Reimplementar a regra aqui
    criaria um segundo Radar que diverge do primeiro no primeiro ajuste.

    O estoque traz ainda lastIncrementDate — a última entrada. Entrada depois
    do pedido é a prova de que chegou; é melhor evidência que "voltou a
    vender", porque não depende de alguém ter procurado a peça de novo.

(B) DE QUEM É O PEDIDO? A coluna Usuario traz só o primeiro nome: "EDUARDO",
    "CARLOS". O casamento com o CRM é por prefixo, e prefixo é ambíguo —
    dois Eduardos no cadastro e as solicitações de um vão para a lista do
    outro. Mostrar ao vendedor pedidos que não são dele é pior que não
    mostrar nada. Aqui medimos quantos primeiros nomes casam com MAIS DE UM
    vendedor; esses não podem ser atribuídos, e precisam de de-para manual.

NÃO ALTERA NADA.
"""
import os
import re
import sqlite3
import sys
import time
from pathlib import Path

sys.path.insert(0, "/srv/passini/apps/radar-rupturas")

try:
    import pandas as pd
except ImportError:
    print("Rode com o venv do RADAR: /srv/passini/venv/radar/bin/python ...")
    sys.exit(1)

try:
    from analytics import (canonical_gtin, gerar_familias_substitutos,
                           normalizar_unidade)
except ImportError as exc:
    print(f">> Não consegui importar o analytics do Radar: {exc}")
    print("   Esperava encontrá-lo em /srv/passini/apps/radar-rupturas")
    sys.exit(1)

SOURCES = Path(os.environ.get("RUNTIME_DIR")
               or "/srv/passini/apps/radar-rupturas/runtime_data") / "sources"
CRM_DB = next((Path(p) for p in (
    (os.environ.get("PASSINI_CRM_DATA", "") or "x") + "/passini_dashboard.db",
    "/srv/passini/data/crm/passini_dashboard.db") if Path(p).exists()), None)
FALTAS_DB = Path("/srv/passini/data/compartilhado/faltas.db")


def limpa(v) -> str:
    if v is None:
        return ""
    if isinstance(v, float):
        if pd.isna(v):
            return ""
        if v.is_integer():
            return str(int(v))
    t = re.sub(r"\s+", " ", str(v)).strip()
    return t[:-2] if re.match(r"^\d+\.0$", t) else t


# ── 1. O arquivo de estoque ─────────────────────────────────────────────────
print("1) O QUE O ESTOQUE DO RADAR TEM")
caminho = SOURCES / "stock.pkl"
if not caminho.exists():
    print(f"   >> {caminho} não existe.")
    sys.exit(1)
t0 = time.time()
stock = pd.read_pickle(caminho)
print(f"   {len(stock):,} linhas · {stock.shape[1]} colunas · "
      f"lido em {time.time() - t0:.1f}s")
print("   Colunas: " + ", ".join(str(c) for c in stock.columns)[:300])


def col(df, *nomes):
    alvo = {re.sub(r"[^a-z0-9]", "", n.lower()) for n in nomes}
    for c in df.columns:
        if re.sub(r"[^a-z0-9]", "", str(c).lower()) in alvo:
            return c
    return None


c_un = col(stock, "branchName", "unidade")
c_item = col(stock, "itemExternalCode", "item external code", "codigo externo")
c_qtd = col(stock, "quantity", "quantidade")
c_ent = col(stock, "lastIncrementDate", "last increment date", "ultima entrada")
print(f"\n   {'PAPEL':<20}{'COLUNA':<28}PREENCHIDA")
for papel, c in (("unidade", c_un), ("código do item", c_item),
                 ("quantidade", c_qtd), ("última entrada", c_ent)):
    if c is None:
        print(f"   {papel:<20}{'— AUSENTE —':<28}")
        continue
    cheia = stock[c].map(limpa).ne("").sum()
    print(f"   {papel:<20}{str(c)[:27]:<28}{100 * cheia / len(stock):.1f}%")
if c_ent is None:
    print("   >> Sem data de última entrada não dá para dizer 'chegou depois")
    print("      do pedido'. Sobra só 'tem agora', que é bem menos.")

# ── 2. As famílias de substitutos ───────────────────────────────────────────
print("\n2) AS FAMÍLIAS DE SUBSTITUTOS")
subs_path = SOURCES / "substitutos.pkl"
familias = {}
if subs_path.exists():
    t0 = time.time()
    subs = pd.read_pickle(subs_path)
    familias = gerar_familias_substitutos(subs)
    tamanhos = {}
    for g, e in familias.items():
        tamanhos[e["FamiliaID"]] = len(e["GTINs"])
    print(f"   {len(subs):,} linha(s) de substituto · {len(familias):,} códigos "
          f"com família · {len(tamanhos):,} famílias · {time.time() - t0:.1f}s")
    if tamanhos:
        grandes = sum(1 for n in tamanhos.values() if n > 1)
        print(f"   Famílias com mais de um código: {grandes:,} "
              f"({100 * grandes / len(tamanhos):.0f}%)")
        print(f"   Maior família: {max(tamanhos.values())} códigos")
else:
    print(f"   >> {subs_path} não existe. Sem substitutos, cada peça é a própria")
    print("      família — e a ruptura sai inflada, porque peça com substituto")
    print("      na prateleira conta como falta.")

# ── 3. Estoque por unidade × família ────────────────────────────────────────
print("\n3) ESTOQUE CONSOLIDADO POR UNIDADE × FAMÍLIA")
est = pd.DataFrame({
    "unidade": stock[c_un].map(normalizar_unidade) if c_un else "SEM_UNIDADE",
    "codigo": stock[c_item].map(canonical_gtin) if c_item else "",
    "qtd": pd.to_numeric(stock[c_qtd], errors="coerce").fillna(0) if c_qtd else 0,
})
est["entrada"] = (pd.to_datetime(stock[c_ent], errors="coerce", dayfirst=True)
                  if c_ent else pd.NaT)
est = est[est["codigo"].ne("")]
est["familia"] = est["codigo"].map(
    lambda x: familias.get(x, {}).get("FamiliaID", x))
fam = est.groupby(["unidade", "familia"], as_index=False).agg(
    estoque=("qtd", "sum"), ultima_entrada=("entrada", "max"))
print(f"   {len(est):,} posições → {len(fam):,} combinações unidade × família")
print(f"\n   {'UNIDADE':<14}{'FAMÍLIAS':>10}{'COM ESTOQUE':>13}{'ZERADAS':>10}")
for u, g in fam.groupby("unidade"):
    com = int((g["estoque"] > 0).sum())
    print(f"   {str(u)[:13]:<14}{len(g):>10,}{com:>13,}{len(g) - com:>10,}")

# ── 4. A pergunta que o painel faz ──────────────────────────────────────────
print("\n4) AS FALTAS DO ÚLTIMO MÊS FECHADO FORAM RESOLVIDAS?")
if not FALTAS_DB.exists():
    print(f"   {FALTAS_DB} não existe — rode o exportar_faltas.py antes.")
else:
    fconn = sqlite3.connect(f"file:{FALTAS_DB}?mode=ro", uri=True)
    fconn.row_factory = sqlite3.Row
    comps = [r[0] for r in fconn.execute(
        "SELECT DISTINCT competencia FROM faltas_resumo ORDER BY competencia")]
    alvo_comp = comps[-2] if len(comps) > 1 else comps[-1]
    print(f"   Mês: {alvo_comp} (último FECHADO; {comps[-1]} ainda corre)")
    linhas = fconn.execute(
        "SELECT unidade, item_code, pedidos, ultima_data FROM faltas_resumo"
        " WHERE competencia = ?", (alvo_comp,)).fetchall()
    idx = {(r["unidade"], r["familia"]): (r["estoque"], r["ultima_entrada"])
           for r in fam.to_dict("records")}

    tem = zerado = sem_posicao = chegou_depois = 0
    for r in linhas:
        familia = familias.get(r["item_code"], {}).get("FamiliaID", r["item_code"])
        par = idx.get((r["unidade"], familia))
        if par is None:
            sem_posicao += 1
            continue
        estoque, entrada = par
        if estoque > 0:
            tem += 1
        else:
            zerado += 1
        if pd.notna(entrada) and r["ultima_data"]:
            if str(entrada)[:10] >= r["ultima_data"]:
                chegou_depois += 1
    tot = max(1, len(linhas))
    print(f"   Faltas no mês: {len(linhas):,}")
    print(f"      com estoque da família HOJE:   {tem:>7,} ({100 * tem / tot:.0f}%)  → resolvido")
    print(f"      família ainda zerada:          {zerado:>7,} ({100 * zerado / tot:.0f}%)  → em aberto")
    print(f"      sem posição de estoque:        {sem_posicao:>7,} ({100 * sem_posicao / tot:.0f}%)  → não dá para dizer")
    print(f"      entrada APÓS o pedido:         {chegou_depois:>7,} ({100 * chegou_depois / tot:.0f}%)  → chegou")
    print("   >> 'Sem posição' alto significa que o estoque e a solicitação")
    print("      falam de peças diferentes — e aí o painel não pode afirmar nada.")
    fconn.close()

# ── 5. O primeiro nome é ambíguo? ───────────────────────────────────────────
print("\n5) DÁ PARA DIZER DE QUEM É O PEDIDO?")
if CRM_DB is None:
    print("   Banco do CRM não encontrado.")
else:
    conn = sqlite3.connect(f"file:{CRM_DB}?mode=ro", uri=True)
    cid = conn.execute("SELECT id FROM companies LIMIT 1").fetchone()[0]
    vend = set()
    for tabela in ("fact_sales_detail", "fact_vendor_summary", "crm_client_summary"):
        try:
            vend |= {limpa(r[0]) for r in conn.execute(
                f"SELECT DISTINCT seller_name FROM {tabela} WHERE company_id = ?",
                (cid,))}
        except sqlite3.Error:
            pass
    vend -= {""}

    def chave(v: str) -> str:
        t = limpa(v).upper()
        for a, b in zip("ÁÀÃÂÄÉÊËÍÏÓÕÔÖÚÜÇ", "AAAAAEEEIIOOOOUUC"):
            t = t.replace(a, b)
        t = re.sub(r"\((VENDAS|TELEVENDAS|BALCAO)\)", " ", t)
        return re.sub(r"[^A-Z0-9 ]", " ", t).strip()

    req = pd.read_pickle(SOURCES / "solicitacao.pkl")
    usuarios = req["Usuario"].map(limpa).value_counts() if "Usuario" in req.columns \
        else pd.Series(dtype=int)
    print(f"   {len(vend)} vendedor(es) no CRM · {len(usuarios)} usuário(s) no Radar")
    print(f"\n   {'USUÁRIO':<18}{'LINHAS':>9}  SITUAÇÃO")
    ambiguos = unicos = orfaos = 0
    linhas_amb = linhas_un = linhas_orf = 0
    for u, n in usuarios.items():
        k = chave(u)
        if not k:
            continue
        casam = [v for v in vend if chave(v) == k or chave(v).startswith(k + " ")]
        if len(casam) == 1:
            unicos += 1
            linhas_un += n
        elif len(casam) > 1:
            ambiguos += 1
            linhas_amb += n
            if ambiguos <= 8:
                print(f"   {u[:17]:<18}{n:>9,}  AMBÍGUO → "
                      + " / ".join(c[:22] for c in casam[:3]))
        else:
            orfaos += 1
            linhas_orf += n
            if orfaos <= 6:
                print(f"   {u[:17]:<18}{n:>9,}  sem vendedor no CRM")
    total_linhas = max(1, int(usuarios.sum()))
    print(f"\n   {'':<18}{'USUÁRIOS':>9}{'LINHAS':>12}")
    print(f"   {'nome único':<18}{unicos:>9}{linhas_un:>12,} "
          f"({100 * linhas_un / total_linhas:.0f}%)")
    print(f"   {'AMBÍGUO':<18}{ambiguos:>9}{linhas_amb:>12,} "
          f"({100 * linhas_amb / total_linhas:.0f}%)")
    print(f"   {'sem vendedor':<18}{orfaos:>9}{linhas_orf:>12,} "
          f"({100 * linhas_orf / total_linhas:.0f}%)")
    print("   >> Só 'nome único' pode ser atribuído automaticamente. AMBÍGUO")
    print("      precisa de de-para manual — atribuir no chute faria o vendedor")
    print("      ver pedido do colega como se fosse dele.")
    conn.close()

print("\nNada foi alterado.")
