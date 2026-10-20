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
    # _prepare_stock é privada, mas é A função do Radar que lê o estoque.
    #
    # A primeira versão deste diagnóstico redigitou a lista de nomes de
    # coluna candidatos e esqueceu "item" — que é justamente como a coluna se
    # chama no arquivo real. Resultado: "código do item — AUSENTE" e 100% de
    # "sem posição de estoque", um falso negativo perfeito. Terceira vez na
    # mesma sessão que recriar uma lista do sistema me faz errar. Então usa-se
    # a função, com privada e tudo: se ela mudar, este diagnóstico muda junto,
    # que é exatamente o que se quer.
    from analytics import _prepare_stock, gerar_familias_substitutos
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


c_ent = col(stock, "lastIncrementDate", "last increment date", "ultima entrada")
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
# _prepare_stock faz tudo: normaliza unidade, acha a coluna do código, aplica
# canonical_gtin, lê a última entrada e resolve a família. É a mesma leitura
# que o Radar usa para calcular ruptura, então os dois não podem divergir.
preparado = _prepare_stock(stock, familias)

# DUAS NORMALIZAÇÕES DE UNIDADE, E ELAS NÃO FALAM A MESMA LÍNGUA.
#
# _prepare_stock normaliza com o vocabulário do Radar: ZONASUL, ZONANORTE,
# sem espaço. O arquivo de faltas já saiu traduzido para o do CRM: ZONA SUL,
# ZONA NORTE. Sem converter aqui, essas duas unidades jamais casam — e a
# conta não dá erro, dá "sem posição de estoque" para um quarto das faltas,
# que é um número plausível o bastante para ninguém desconfiar.
#
# Foi o que aconteceu na execução anterior: 27% de "sem posição", e a Zona
# Sul mais a Zona Norte são ~24% do arquivo.
DE_PARA_UNIDADE: dict[str, str] = {}
_fonte_backend = Path(__file__).resolve().parent / "backend.py"
try:
    import ast
    for _no in ast.parse(_fonte_backend.read_text(encoding="utf-8")).body:
        if isinstance(_no, ast.Assign) and any(
                getattr(a, "id", "") == "UNIT_NORMALIZATION" for a in _no.targets):
            DE_PARA_UNIDADE = ast.literal_eval(_no.value)
            break
except Exception as _exc:  # noqa: BLE001
    print(f"   (não consegui ler UNIT_NORMALIZATION: {_exc})")


def para_unidade_do_crm(valor) -> str:
    bruto = re.sub(r"\s+", " ", str(valor or "").upper()).strip()
    return DE_PARA_UNIDADE.get(bruto, bruto)


_antes = sorted(set(preparado["Unidade_Normalizada"]))
est = pd.DataFrame({
    "unidade": preparado["Unidade_Normalizada"].map(para_unidade_do_crm),
    "codigo": preparado["GTIN"],
    "qtd": preparado["quantity"],
    "entrada": preparado["Ultima_Entrada"],
    "familia": preparado["FamiliaID"],
})
est = est[est["codigo"].astype(str).ne("")]
fam = est.groupby(["unidade", "familia"], as_index=False).agg(
    estoque=("qtd", "sum"), ultima_entrada=("entrada", "max"))
print(f"   {len(est):,} posições → {len(fam):,} combinações unidade × família")
_depois = sorted(set(est["unidade"]))
print(f"   Unidade no vocabulário do Radar: {', '.join(_antes)}")
print(f"   Traduzida para o do CRM:         {', '.join(_depois)}")
entradas = int(est["entrada"].notna().sum())
print(f"   Posições com data de última entrada: {entradas:,} "
      f"({100 * entradas / max(1, len(est)):.0f}%)")

# O estoque e a solicitação falam do mesmo código? Se não, o passo 4 dá 100%
# de "sem posição" e parece problema de dado quando é problema de chave.
cods_estoque = set(est["codigo"].astype(str))
print(f"   Códigos distintos no estoque: {len(cods_estoque):,}")
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

    # A CHAVE CRUZA, ANTES DE QUALQUER CONTA.
    #
    # Na primeira execução este passo deu 100% de "sem posição de estoque" e
    # pareceu divergência de cadastro. Não era: a leitura do estoque tinha
    # falhado antes, e o conjunto estava vazio. Conferir a interseção das
    # chaves separa "o dado não cruza" de "eu li errado" — e os dois produzem
    # exatamente o mesmo 100%.
    cods_falta = {r["item_code"] for r in linhas}
    comum = cods_falta & cods_estoque
    print(f"   Códigos das faltas: {len(cods_falta):,} · "
          f"também no estoque: {len(comum):,} "
          f"({100 * len(comum) / max(1, len(cods_falta)):.0f}%)")
    if not comum:
        print("   >> NENHUM código em comum. Ou o estoque não foi lido, ou as")
        print("      duas bases usam códigos diferentes. Sem isso, o resto do")
        print("      passo 4 não significa nada.")
    idx = {(r["unidade"], r["familia"]): (r["estoque"], r["ultima_entrada"])
           for r in fam.to_dict("records")}

    # "Sem posição" precisa dizer POR QUE. Unidade que não existe no estoque
    # é erro de de-para; família que não existe é cadastro. Os dois somavam
    # num número só e pareciam o mesmo problema.
    unidades_estoque = {u for u, _ in idx}
    sem_unidade = sem_familia = 0

    tem = zerado = sem_posicao = chegou_depois = 0
    for r in linhas:
        familia = familias.get(r["item_code"], {}).get("FamiliaID", r["item_code"])
        par = idx.get((r["unidade"], familia))
        if par is None:
            sem_posicao += 1
            if r["unidade"] not in unidades_estoque:
                sem_unidade += 1
            else:
                sem_familia += 1
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
    print(f"         · unidade fora do estoque:  {sem_unidade:>7,}  (erro de de-para)")
    print(f"         · família sem posição:      {sem_familia:>7,}  (cadastro)")
    print(f"      entrada APÓS o pedido:         {chegou_depois:>7,} ({100 * chegou_depois / tot:.0f}%)  → chegou")
    if sem_unidade:
        print("   >> UNIDADE FORA DO ESTOQUE é defeito de tradução, não de dado:")
        print("      o estoque e as faltas estão escrevendo o mesmo lugar com")
        print("      nomes diferentes. Tem de ser zero.")
    print("   >> 'Família sem posição' é peça que a unidade nunca teve em")
    print("      estoque — aí 'em aberto' é a leitura certa, não 'resolvido'.")
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
