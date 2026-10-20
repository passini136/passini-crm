"""
Transforma a solicitação de compra do Radar na tabela enxuta que o CRM lê.

Uso (venv do RADAR, que é quem tem pandas):
    /srv/passini/venv/radar/bin/python /srv/passini/apps/crm-comercial/exportar_faltas.py

    --destino CAMINHO   onde gravar (padrão: /srv/passini/data/compartilhado/faltas.db)
    --simular           apura e relata, sem gravar nada

POR QUE ESTE SCRIPT EXISTE, E POR QUE ELE NÃO MORA NO RADAR

O CRM precisa saber o que faltou para cruzar com a carteira. O dado existe
no Radar, e pedir o mesmo CSV duas vezes seria trabalho dobrado com dois
números divergentes na primeira vez que um dos uploads atrasasse.

O caminho óbvio seria o Radar gravar esta tabela ao fim de cada importação.
Não é o que fazemos: o Radar é um sistema em produção, estável, e não tem
caminho de deploy versionado. Alterá-lo para servir o CRM é arriscar o que
funciona em nome do que ainda não existe. Então este script mora no
repositório do CRM e apenas LÊ o arquivo do Radar. O Radar não sabe que ele
existe, e continua igual.

O QUE ELE RESOLVE, QUE O DADO CRU NÃO RESOLVE

1. O arquivo tem SEIS colunas de código, acrescentadas à mão ao longo do
   tempo: gtin, GTIN, GTIN_NORMALIZADO, Codigo, "unid + gtin", col_19.
   Nenhuma é GTIN de verdade — são o código interno da Passini. O
   diagnóstico diag_radar_prova.py mediu a fidelidade de cada uma comparando
   o fabricante do Radar com o do catálogo: Codigo 98,5%, GTIN_NORMALIZADO
   94,6%, gtin 94,5%, GTIN 93,2%. Usamos nessa ordem, por linha, e anotamos
   de qual coluna veio.

2. 6.873 linhas têm data vazia, que vira 1º de janeiro de 1970. Entrassem,
   toda unidade ganharia um histórico falso puxando as médias para baixo.

3. 263 mil linhas cruas viram algumas dezenas de milhares agrupadas por
   unidade × mês × peça. O CRM atende uma requisição por vez: ler 44 MB de
   pickle a cada clique travaria a tela para todos.

4. O Radar escreve ZONASUL; o CRM escreve ZONA SUL. O de-para sai do próprio
   backend do CRM, lido do código-fonte — este script roda no venv do Radar
   e não consegue importar o backend, que depende de reportlab e openpyxl.

NÃO ALTERA O RADAR NEM O BANCO DO CRM. Só lê o pickle e grava um arquivo novo.
"""
from __future__ import annotations

import argparse
import ast
import os
import re
import sqlite3
import sys
import tempfile
from collections import Counter
from datetime import datetime
from pathlib import Path

try:
    import pandas as pd
except ImportError:
    print("pandas não encontrado. Rode com o venv do RADAR:")
    print("  /srv/passini/venv/radar/bin/python "
          "/srv/passini/apps/crm-comercial/exportar_faltas.py")
    sys.exit(1)

# Ordem de confiança medida no dado real (diag_radar_prova.py, 20/10/2026):
# o percentual é quantas vezes o fabricante do Radar bateu com o do catálogo
# do CRM depois de casar a peça pelo código daquela coluna.
COLUNAS_CODIGO = ["Codigo", "GTIN_NORMALIZADO", "gtin", "GTIN"]

DESTINO_PADRAO = "/srv/passini/data/compartilhado/faltas.db"


def achar_pickle() -> Path:
    candidatos = [
        (os.environ.get("RUNTIME_DIR", "") or "x") + "/sources/solicitacao.pkl",
        "/srv/passini/apps/radar-rupturas/runtime_data/sources/solicitacao.pkl",
        "/srv/passini/data/radar/runtime_data/sources/solicitacao.pkl",
    ]
    for c in candidatos:
        if c and Path(c).exists():
            return Path(c)
    print(">> Não encontrei a solicitação do Radar. Procurei em:")
    for c in candidatos:
        print(f"   {c}")
    sys.exit(1)


def de_para_unidades() -> dict[str, str]:
    """Lê UNIT_NORMALIZATION do backend do CRM sem importá-lo.

    Importar não é opção: este script roda no venv do Radar, que não tem as
    dependências do CRM. Copiar o dicionário para cá seria pior — no dia em
    que uma filial nova entrasse no CRM, a falta dela cairia em
    SEM_UNIDADE sem ninguém notar.
    """
    fonte = Path(__file__).resolve().parent / "backend.py"
    try:
        arvore = ast.parse(fonte.read_text(encoding="utf-8"))
    except Exception as exc:  # noqa: BLE001
        print(f">> Não consegui ler {fonte}: {exc}")
        return {}
    for no in arvore.body:
        if isinstance(no, ast.Assign) and any(
                getattr(a, "id", "") == "UNIT_NORMALIZATION" for a in no.targets):
            try:
                return ast.literal_eval(no.value)
            except Exception:  # noqa: BLE001
                return {}
    return {}


def chave_nome(valor: str) -> str:
    """Nome comparável: sem acento, sem (VENDAS), sem pontuação."""
    t = limpa(valor).upper()
    for a, b in zip("ÁÀÃÂÄÉÊËÍÏÓÕÔÖÚÜÇ", "AAAAAEEEIIOOOOUUC"):
        t = t.replace(a, b)
    t = re.sub(r"\((VENDAS|TELEVENDAS|BALCAO)\)", " ", t)
    return re.sub(r"[^A-Z0-9 ]", " ", t).strip()


# Sufixo de unidade grudado no login: GABRIELLAJEADO, TIAGOBALCAO.
# Tirar isso é o que transforma o login na pessoa.
SUFIXOS_LOGIN = ["ZONANORTE", "ZONASUL", "XANGRILA", "LAJEADO", "PELOTAS",
                 "MATRIZ", "BALCAO", "TELEVENDAS", "VENDAS", "POA"]


def carregar_vendedores_do_crm() -> dict[str, str]:
    """Nome do vendedor → unidade-base, do cadastro de pessoas do CRM.

    A unidade é o que desfaz a ambiguidade: há dois Carlos e dois Leonardos,
    e o que distingue é a loja. people_records é o cadastro de pessoas, com
    base_unit; os nomes que só aparecem no faturamento entram sem unidade e
    só podem ser resolvidos quando o primeiro nome já é único.
    """
    caminho = Path(os.environ.get("PASSINI_CRM_DATA")
                   or "/srv/passini/data/crm") / "passini_dashboard.db"
    if not caminho.exists():
        print(f"   (banco do CRM não encontrado em {caminho}; "
              f"nenhuma falta terá dono)")
        return {}
    nomes: dict[str, str] = {}
    try:
        conn = sqlite3.connect(f"file:{caminho}?mode=ro", uri=True)
        cid = conn.execute("SELECT id FROM companies LIMIT 1").fetchone()[0]
        for tabela in ("fact_sales_detail", "fact_vendor_summary",
                       "crm_client_summary"):
            try:
                for r in conn.execute(
                        f"SELECT DISTINCT seller_name FROM {tabela}"
                        f" WHERE company_id = ?", (cid,)):
                    if limpa(r[0]):
                        nomes.setdefault(limpa(r[0]), "")
            except sqlite3.Error:
                continue
        try:
            # ORDER BY valid_from DESC + setdefault = fica a unidade mais
            # recente de quem já mudou de loja.
            for r in conn.execute(
                    "SELECT person_name, base_unit FROM people_records"
                    " WHERE company_id = ? AND TRIM(COALESCE(base_unit,'')) <> ''"
                    " ORDER BY date(valid_from) DESC", (cid,)):
                nome = limpa(r[0])
                if nome and not nomes.get(nome):
                    nomes[nome] = limpa(r[1]).upper()
        except sqlite3.Error as exc:
            print(f"   (people_records indisponível: {exc})")
        conn.close()
    except sqlite3.Error as exc:
        print(f"   (não consegui ler os vendedores: {exc})")
    return nomes


def _sem_sufixo(chave: str) -> str:
    """GABRIELLAJEADO → GABRIEL · TIAGOBALCAO → TIAGO."""
    compacto = chave.replace(" ", "")
    for suf in SUFIXOS_LOGIN:
        if compacto.endswith(suf) and len(compacto) > len(suf) + 2:
            return compacto[: -len(suf)]
    return chave


def resolver_vendedores(
    pares: set[tuple[str, str]], vendedores: dict[str, str],
    mapa_unidade: dict[str, str],
) -> tuple[dict[tuple[str, str], str], set[str], set[str]]:
    """(usuário do Radar, unidade do pedido) → vendedor do CRM.

    A chave é o PAR, não o nome sozinho. Foi assim que o Felipe descreveu a
    equipe — "o Carlos de Pelotas", "o Leonardo da Zona Norte" — e é a única
    informação que separa dois homônimos sem adivinhação.

    Três passadas, da mais segura para a menos:
      1. nome completo casa com UM vendedor → resolve;
      2. casa com vários, mas só um está NAQUELA unidade → resolve;
      3. só o primeiro nome casa, e só uma pessoa daquele nome está naquela
         unidade → resolve.

    A terceira é a mais frouxa e é onde entram os logins grudados
    (GABRIELLAJEADO) e os nomes que o Radar abrevia. Por isso o exportador
    imprime o mapa inteiro: resolução por primeiro nome precisa de olho
    humano antes de virar "as minhas solicitações" de alguém.
    """
    por_chave: dict[str, list[str]] = {}
    por_primeiro: dict[str, list[str]] = {}
    for v in vendedores:
        k = chave_nome(v)
        if not k:
            continue
        por_chave.setdefault(k, []).append(v)
        por_primeiro.setdefault(k.split(" ")[0], []).append(v)

    def unidade_do(nome: str) -> str:
        bruto = (vendedores.get(nome) or "").upper()
        return mapa_unidade.get(bruto, bruto)

    de_para: dict[tuple[str, str], str] = {}
    ambiguos: set[str] = set()
    orfaos: set[str] = set()
    # POR QUE não resolveu. Sem isso a lista de ambíguos é um beco: quem
    # conhece a equipe sabe de quem é o pedido, mas não sabe o que consertar.
    # Com os candidatos e as unidades deles à vista, fica evidente se o caso é
    # cadastro de pessoa sem unidade, pessoa em loja diferente da que pediu,
    # ou dois homônimos de verdade na mesma loja.
    motivos: dict[str, str] = {}
    for usuario, unidade in pares:
        k = chave_nome(usuario)
        if not k:
            continue
        candidatos = [v for kk, lista in por_chave.items() for v in lista
                      if kk == k or kk.startswith(k + " ")]
        if len(candidatos) == 1:
            de_para[(usuario, unidade)] = candidatos[0]
            continue
        def detalhar(lista: list[str]) -> str:
            return " | ".join(
                f"{v} [{unidade_do(v) or 'sem unidade'}]" for v in sorted(lista)[:4])

        if len(candidatos) > 1:
            na_unidade = [v for v in candidatos if unidade_do(v) == unidade]
            if len(na_unidade) == 1:
                de_para[(usuario, unidade)] = na_unidade[0]
            else:
                ambiguos.add(usuario)
                motivos[f"{usuario} / {unidade}"] = (
                    f"{len(candidatos)} nomes casam, {len(na_unidade)} em "
                    f"{unidade} → {detalhar(candidatos)}")
            continue
        # Terceira passada: primeiro nome, obrigatoriamente com a unidade.
        primeiro = _sem_sufixo(k).split(" ")[0]
        candidatos = [v for kk, lista in por_primeiro.items() for v in lista
                      if kk == primeiro]
        na_unidade = [v for v in candidatos if unidade_do(v) == unidade]
        if len(na_unidade) == 1:
            de_para[(usuario, unidade)] = na_unidade[0]
        elif candidatos:
            ambiguos.add(usuario)
            motivos[f"{usuario} / {unidade}"] = (
                f"por primeiro nome '{primeiro}': {len(candidatos)} candidato(s), "
                f"{len(na_unidade)} em {unidade} → {detalhar(candidatos)}")
        else:
            orfaos.add(usuario)
            motivos[f"{usuario} / {unidade}"] = (
                f"nenhum vendedor começa com '{primeiro}'")
    return de_para, ambiguos, orfaos, motivos


def familia_e_estoque(
    sources: Path, mapa_unidade: dict[str, str]
) -> tuple[dict, "pd.DataFrame"]:
    """Famílias de substitutos e estoque consolidado, pela regra do Radar.

    Usa gerar_familias_substitutos e _prepare_stock IMPORTADAS do Radar, não
    reescritas. Reimplementar a regra criaria um segundo Radar que diverge do
    primeiro no primeiro ajuste — e já errei uma vez redigitando a lista de
    nomes de coluna do estoque, o que produziu "sem posição" para tudo.

    A unidade sai do _prepare_stock no vocabulário do Radar (ZONASUL) e é
    traduzida para o do CRM (ZONA SUL). Sem isso, duas unidades inteiras
    nunca casariam com as faltas — e o resultado seria um percentual
    plausível de "sem informação", não um erro visível.
    """
    import importlib

    vazio = pd.DataFrame(columns=["unidade", "familia", "estoque", "ultima_entrada"])
    sys.path.insert(0, "/srv/passini/apps/radar-rupturas")
    try:
        analytics = importlib.import_module("analytics")
    except ImportError as exc:
        print(f"   >> analytics do Radar indisponível ({exc}); "
              f"sem família e sem estoque.")
        return {}, vazio

    familias = {}
    p_subs = sources / "substitutos.pkl"
    if p_subs.exists():
        familias = analytics.gerar_familias_substitutos(pd.read_pickle(p_subs))
        print(f"\n7) FAMÍLIAS — {len(familias):,} códigos em "
              f"{len({e['FamiliaID'] for e in familias.values()}):,} famílias")
    else:
        print(f"\n7) FAMÍLIAS — {p_subs} não existe; cada peça vira a própria "
              f"família e a ruptura sai inflada.")

    p_stock = sources / "stock.pkl"
    if not p_stock.exists():
        print(f"   >> {p_stock} não existe; sem estoque não há 'resolvido'.")
        return familias, vazio

    preparado = analytics._prepare_stock(pd.read_pickle(p_stock), familias)
    est = pd.DataFrame({
        "unidade": preparado["Unidade_Normalizada"].map(
            lambda v: mapa_unidade.get(
                re.sub(r"\s+", " ", str(v or "").upper()).strip(),
                re.sub(r"\s+", " ", str(v or "").upper()).strip())),
        "familia": preparado["FamiliaID"].astype(str),
        "qtd": preparado["quantity"],
        "entrada": preparado["Ultima_Entrada"],
    })
    est = est[est["familia"].ne("")]
    fam = est.groupby(["unidade", "familia"], as_index=False).agg(
        estoque=("qtd", "sum"), ultima_entrada=("entrada", "max"))
    fam["ultima_entrada"] = fam["ultima_entrada"].dt.strftime("%Y-%m-%d")
    com = int((fam["estoque"] > 0).sum())
    print(f"   ESTOQUE — {len(est):,} posições → {len(fam):,} unidade × família")
    print(f"   Com saldo: {com:,} ({100 * com / max(1, len(fam)):.0f}%) · "
          f"zeradas: {len(fam) - com:,}")
    print(f"   Unidades: {', '.join(sorted(set(est['unidade'])))}")
    return familias, fam


def limpa(v) -> str:
    """Tira o '.0' que o Excel cola em número, colapsa espaço, sobe a caixa."""
    if v is None:
        return ""
    if isinstance(v, float):
        if pd.isna(v):
            return ""
        if v.is_integer():
            return str(int(v))
    t = re.sub(r"\s+", " ", str(v)).strip()
    return t[:-2] if re.match(r"^\d+\.0$", t) else t


def coluna(df, *nomes):
    alvo = {re.sub(r"[^a-z0-9]", "", n.lower()) for n in nomes}
    for c in df.columns:
        if re.sub(r"[^a-z0-9]", "", str(c).lower()) in alvo:
            return c
    return None


ESQUEMA = """
CREATE TABLE faltas_resumo (
    unidade      TEXT NOT NULL,
    competencia  TEXT NOT NULL,      -- AAAA-MM
    item_code    TEXT NOT NULL,      -- código interno da Passini
    vendedor     TEXT NOT NULL,      -- nome do CRM, ou '' quando não dá para dizer
    familia      TEXT,               -- família de substitutos (regra do Radar)
    pedidos      INTEGER NOT NULL,   -- quantas vezes foi pedida no mês
    ultima_data  TEXT,
    item         TEXT,
    fabricante   TEXT,
    tipo         TEXT,
    usuario      TEXT,               -- como o Radar gravou, antes do de-para
    custo        REAL,               -- P. Entrada: o preço de entrada da peça
    fonte_codigo TEXT,
    PRIMARY KEY (unidade, competencia, item_code, vendedor)
);
CREATE INDEX idx_faltas_item ON faltas_resumo(item_code);
CREATE INDEX idx_faltas_comp ON faltas_resumo(competencia, unidade);
CREATE INDEX idx_faltas_vend ON faltas_resumo(vendedor, competencia);

-- Estoque consolidado por família, que é a regra central do Radar: ruptura
-- só existe quando a família INTEIRA de substitutos está zerada na unidade.
-- Perguntar item a item inflaria a ruptura, porque peça pedida com
-- substituto na prateleira não é falta — é escolha.
CREATE TABLE estoque_familia (
    unidade        TEXT NOT NULL,
    familia        TEXT NOT NULL,
    estoque        REAL NOT NULL,
    ultima_entrada TEXT,
    PRIMARY KEY (unidade, familia)
);
CREATE TABLE faltas_meta (chave TEXT PRIMARY KEY, valor TEXT);
"""


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--destino", default=DESTINO_PADRAO)
    ap.add_argument("--simular", action="store_true",
                    help="apura e relata sem gravar")
    args = ap.parse_args()

    origem = achar_pickle()
    print(f"Origem:  {origem}")
    print(f"Destino: {args.destino}{'  (SIMULAÇÃO, nada será gravado)' if args.simular else ''}\n")

    req = pd.read_pickle(origem)
    total_cru = len(req)
    print(f"1) LIDO: {total_cru:,} linhas")

    # ── Código da peça: primeira coluna confiável que tiver valor ───────────
    disponiveis = [c for c in COLUNAS_CODIGO if c in req.columns]
    if not disponiveis:
        print(">> Nenhuma das colunas de código existe no arquivo. "
              f"Procurei: {', '.join(COLUNAS_CODIGO)}")
        return 1
    print(f"\n2) CÓDIGO DA PEÇA — ordem de confiança: {' > '.join(disponiveis)}")

    codigo = pd.Series([""] * len(req), index=req.index, dtype="object")
    fonte = pd.Series([""] * len(req), index=req.index, dtype="object")
    for nome in disponiveis:
        valores = req[nome].map(limpa)
        # Só preenche onde ainda está vazio: a coluna mais confiável manda.
        vazio = codigo.eq("") & valores.ne("")
        codigo.loc[vazio] = valores.loc[vazio]
        fonte.loc[vazio] = nome
        print(f"   {nome:<20}preencheu {int(vazio.sum()):>9,} linha(s)")
    sem_codigo = int(codigo.eq("").sum())
    print(f"   {'sem código':<20}{sem_codigo:>19,} linha(s) — descartadas")

    # ── Data: AAAA-MM, sem epoch ────────────────────────────────────────────
    col_data = coluna(req, "Registro")
    if col_data is None:
        print("\n>> Coluna Registro ausente. Sem data não há competência.")
        return 1
    datas = pd.to_datetime(req[col_data], errors="coerce", dayfirst=True)
    ruins = datas.isna() | (datas.dt.year <= 1970)
    print(f"\n3) DATA — descartando {int(ruins.sum()):,} linha(s) vazias ou em 1970")

    # ── Unidade ─────────────────────────────────────────────────────────────
    col_emp = coluna(req, "Emp", "unidade")
    mapa = de_para_unidades()
    print(f"\n4) UNIDADE — {len(mapa)} rótulo(s) no de-para do CRM")
    if col_emp is None:
        print(">> Coluna de unidade ausente.")
        return 1
    rotulos = req[col_emp].map(lambda v: re.sub(r"\s+", " ", str(v or "").upper()).strip())
    unidades = rotulos.map(lambda r: mapa.get(r, ""))
    nao_mapeados = Counter(r for r, u in zip(rotulos, unidades) if r and not u)
    for r, n in nao_mapeados.most_common(8):
        print(f"   SEM DE-PARA: {r[:30]:<32}{n:>9,} linha(s)")
    if not nao_mapeados:
        print("   Todo rótulo encontrou unidade no CRM.")

    # ── Vendedor: o Radar grava só o primeiro nome ──────────────────────────
    #
    # "EDUARDO", "CARLOS". Casar por prefixo resolve 74% das linhas, mas
    # prefixo é AMBÍGUO: há dois Carlos e dois Leonardos no cadastro. Atribuir
    # no chute faria o vendedor abrir a tela e ver pedido do colega como se
    # fosse dele — pior que não mostrar lista nenhuma. Então só entra o nome
    # que casa com UM único vendedor; o resto fica sem dono, e a falta conta
    # para a unidade.
    col_user = coluna(req, "Usuario", "usuário")
    vendedores = carregar_vendedores_do_crm()
    usuario_bruto = (req[col_user].map(limpa) if col_user
                     else pd.Series([""] * len(req), index=req.index))
    pares = {(u, un) for u, un in zip(usuario_bruto, unidades) if u and un}
    de_para_vend, ambiguos, orfaos, motivos = resolver_vendedores(
        pares, vendedores, mapa)
    # Quanto do ARQUIVO cada grupo representa. Contar nomes engana: um nome
    # sem dono com 12 mil linhas pesa mais que dez com cem.
    peso = {}
    for u, un in zip(usuario_bruto, unidades):
        if u and un:
            peso[(u, un)] = peso.get((u, un), 0) + 1
    linhas_ok = sum(n for p, n in peso.items() if p in de_para_vend)

    print(f"\n5) VENDEDOR — {len(vendedores)} nome(s) conhecido(s) no CRM")
    print(f"   Pares usuário × unidade: {len(pares)}")
    print(f"   resolvidos:   {len(de_para_vend):>4}")
    print(f"   AMBÍGUO:      {len(ambiguos):>4} "
          f"({', '.join(sorted(ambiguos)[:6]) or '—'})")
    print(f"   sem vendedor: {len(orfaos):>4} "
          f"({', '.join(sorted(orfaos)[:4]) or '—'}…)")
    # O MAPA INTEIRO, PARA CONFERÊNCIA.
    #
    # A terceira passada resolve por primeiro nome + unidade, que é um palpite
    # informado, não um fato. Atribuir errado faz o vendedor abrir a tela e
    # ver pedido do colega — então o mapa é impresso para alguém que conhece
    # a equipe bater o olho antes de virar "as minhas solicitações".
    if de_para_vend:
        print(f"\n   {'USUÁRIO (RADAR)':<20}{'UNIDADE':<13}VENDEDOR (CRM)")
        for (u, un), v in sorted(de_para_vend.items()):
            print(f"   {u[:19]:<20}{un[:12]:<13}{v}")
    if motivos:
        print(f"\n   POR QUE OS OUTROS {len(motivos)} NÃO RESOLVERAM")
        for rotulo in sorted(motivos, key=lambda r: -peso.get(
                (r.split(" / ")[0], r.split(" / ")[1]), 0)):
            u, un = rotulo.split(" / ")
            print(f"   {rotulo[:30]:<32}{peso.get((u, un), 0):>8,} linhas")
            print(f"      {motivos[rotulo][:150]}")
    total_linhas = sum(peso.values()) or 1
    print(f"\n   Linhas COM dono: {linhas_ok:,} de {total_linhas:,} "
          f"({100 * linhas_ok / total_linhas:.0f}%)")
    print("   >> Ambíguo e sem vendedor entram como falta da unidade, sem dono.")

    # ── Montagem ────────────────────────────────────────────────────────────
    col_item = coluna(req, "Item")
    col_fab = coluna(req, "Fabricante")
    col_tipo = coluna(req, "Tipo")
    col_user = coluna(req, "Usuario", "usuário")

    col_custo = coluna(req, "P. Entrada", "P Entrada")
    base = pd.DataFrame({
        "unidade": unidades,
        "competencia": datas.dt.strftime("%Y-%m"),
        "item_code": codigo,
        "data": datas,
        "fonte_codigo": fonte,
        "item": req[col_item].map(limpa) if col_item else "",
        "fabricante": req[col_fab].map(limpa) if col_fab else "",
        "tipo": req[col_tipo].map(limpa) if col_tipo else "",
        "usuario": usuario_bruto,
        # O dono depende do par usuário+unidade: o mesmo primeiro nome em
        # duas lojas é, de fato, duas pessoas diferentes.
        "vendedor": [de_para_vend.get((u, un), "")
                     for u, un in zip(usuario_bruto, unidades)],
        # "P. Entrada" parece data pelo nome e é PREÇO: 108,71 · 73,15.
        # É o que permite dizer quanto vale a peça que faltou — a coluna Qtd
        # é inaproveitável (10% preenchida, com linha de 500 milhões).
        "custo": (pd.to_numeric(req[col_custo], errors="coerce")
                  if col_custo else pd.Series([None] * len(req), index=req.index)),
    })
    antes = len(base)
    base = base[base["item_code"].ne("") & base["unidade"].ne("") & ~ruins]
    print(f"\n6) APROVEITÁVEL: {len(base):,} de {antes:,} "
          f"({100 * len(base) / max(1, antes):.1f}%)")
    if base.empty:
        print(">> Nada sobrou. Não grava arquivo vazio por cima do bom.")
        return 1

    resumo = base.groupby(
        ["unidade", "competencia", "item_code", "vendedor"], as_index=False).agg(
        pedidos=("item_code", "size"),
        ultima_data=("data", "max"),
        item=("item", "last"),
        fabricante=("fabricante", "last"),
        tipo=("tipo", "last"),
        usuario=("usuario", "last"),
        custo=("custo", "median"),
        fonte_codigo=("fonte_codigo", "first"),
    )
    resumo["ultima_data"] = resumo["ultima_data"].dt.strftime("%Y-%m-%d")
    # A mediana de um grupo sai com ruído de ponto flutuante (220,77499...).
    # Arredondar na gravação evita que cada tela resolva isso do seu jeito.
    resumo["custo"] = resumo["custo"].round(2)

    # ── Família e estoque ───────────────────────────────────────────────────
    familias, estoque = familia_e_estoque(origem.parent, mapa)
    resumo["familia"] = resumo["item_code"].map(
        lambda c: familias.get(c, {}).get("FamiliaID", c))
    meses = sorted(resumo["competencia"].unique())
    print(f"   Agrupado em {len(resumo):,} linha(s) "
          f"(redução de {100 * (1 - len(resumo) / len(base)):.0f}%)")
    print(f"   Período: {meses[0]} a {meses[-1]} ({len(meses)} meses)")
    print(f"   Peças distintas: {resumo['item_code'].nunique():,}")
    print(f"\n   {'UNIDADE':<14}{'LINHAS':>10}{'PEDIDOS':>12}{'PEÇAS':>10}")
    for u, g in resumo.groupby("unidade"):
        print(f"   {u[:13]:<14}{len(g):>10,}{int(g['pedidos'].sum()):>12,}"
              f"{g['item_code'].nunique():>10,}")

    if args.simular:
        print("\nSIMULAÇÃO: nada foi gravado.")
        return 0

    # ── Gravação atômica ────────────────────────────────────────────────────
    # Grava num arquivo temporário e só então substitui o bom. Se este script
    # morrer no meio, o CRM continua lendo o arquivo anterior inteiro em vez
    # de um banco pela metade.
    destino = Path(args.destino)
    destino.parent.mkdir(parents=True, exist_ok=True)
    fd, temporario = tempfile.mkstemp(dir=str(destino.parent), suffix=".parcial")
    os.close(fd)
    try:
        conn = sqlite3.connect(temporario)
        conn.executescript(ESQUEMA)
        conn.executemany(
            "INSERT INTO faltas_resumo (unidade, competencia, item_code, vendedor,"
            " familia, pedidos, ultima_data, item, fabricante, tipo, usuario,"
            " custo, fonte_codigo) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)",
            resumo[["unidade", "competencia", "item_code", "vendedor", "familia",
                    "pedidos", "ultima_data", "item", "fabricante", "tipo",
                    "usuario", "custo", "fonte_codigo"]]
            .astype(object).where(pd.notna(resumo[[
                "unidade", "competencia", "item_code", "vendedor", "familia",
                "pedidos", "ultima_data", "item", "fabricante", "tipo",
                "usuario", "custo", "fonte_codigo"]]), None)
            .itertuples(index=False, name=None),
        )
        if len(estoque):
            conn.executemany(
                "INSERT OR REPLACE INTO estoque_familia"
                " (unidade, familia, estoque, ultima_entrada) VALUES (?,?,?,?)",
                estoque[["unidade", "familia", "estoque", "ultima_entrada"]]
                .astype(object).where(pd.notna(estoque[[
                    "unidade", "familia", "estoque", "ultima_entrada"]]), None)
                .itertuples(index=False, name=None),
            )
        conn.executemany(
            "INSERT INTO faltas_meta (chave, valor) VALUES (?,?)",
            [
                ("gerado_em", datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
                ("origem", str(origem)),
                ("linhas_cruas", str(total_cru)),
                ("linhas_resumo", str(len(resumo))),
                ("competencia_min", meses[0]),
                ("competencia_max", meses[-1]),
                ("ordem_codigo", " > ".join(disponiveis)),
                ("linhas_estoque", str(len(estoque))),
                # Quanto da base tem dono. A tela do vendedor precisa dizer
                # isso: lista curta pode ser carteira tranquila ou nome que o
                # de-para não resolveu, e as duas se parecem.
                ("vendedores_atribuidos", str(len(de_para_vend))),
                ("usuarios_ambiguos", ", ".join(sorted(ambiguos))),
                ("usuarios_sem_vendedor", ", ".join(sorted(orfaos))[:500]),
            ],
        )
        conn.commit()
        conn.close()
        os.replace(temporario, destino)
        os.chmod(destino, 0o644)
    except Exception:
        Path(temporario).unlink(missing_ok=True)
        raise

    tamanho = destino.stat().st_size / 1024
    print(f"\n8) GRAVADO: {destino} · {tamanho:,.0f} KB")
    print("   O arquivo anterior só foi substituído depois do novo ficar pronto.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
