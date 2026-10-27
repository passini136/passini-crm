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

# De-para de LOGIN DO RADAR para pessoa do CRM, mantido à mão.
#
# Por que não usar a tela de Equipe do CRM: ela associa grafias de pessoas
# que EXISTEM no cadastro — é para "Thielly Henrique" × "THIELLY HENRIQUES".
# "ANA CAROLINA" não é pessoa do CRM, é login de outro sistema; a tela não
# tem como oferecê-la, e eu cheguei a mandar o Felipe procurar lá.
#
# Um arquivo de texto resolve sem tocar no banco: dá para ver, versionar,
# corrigir e desfazer. O script cria um modelo com os nomes pendentes e os
# candidatos que ele mesmo encontrou, para a pessoa só preencher.
DEPARA_PADRAO = "/srv/passini/data/compartilhado/vendedores_faltas.csv"


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


def carregar_depara_manual(caminho: Path) -> dict[tuple[str, str], str]:
    """Lê o de-para à mão: login do Radar; unidade; vendedor do CRM.

    Unidade em branco vale para todas — é o caso comum. Unidade preenchida
    serve para o login compartilhado entre lojas, em que o mesmo primeiro
    nome é gente diferente em cada uma.

    Linha começando com # é comentário, e é onde o modelo guarda os
    candidatos que o script encontrou sozinho.
    """
    if not caminho.exists():
        return {}
    mapa: dict[tuple[str, str], str] = {}
    for linha in caminho.read_text(encoding="utf-8", errors="replace").splitlines():
        linha = linha.strip()
        if not linha or linha.startswith("#"):
            continue
        partes = [p.strip() for p in linha.split(";")]
        if len(partes) < 3:
            continue
        login, unidade, vendedor = partes[0], partes[1], partes[2]
        if login and vendedor:
            mapa[(login.upper(), unidade.upper())] = vendedor
    return mapa


def escrever_modelo_depara(
    caminho: Path, pendentes: list[tuple[str, str, int, str]],
) -> None:
    """Gera o arquivo para preencher, já com o que o script descobriu."""
    linhas = [
        "# DE-PARA: login do Radar  ->  vendedor do CRM",
        "#",
        "# Formato:  login_do_radar ; unidade ; nome exato do vendedor no CRM",
        "# A unidade pode ficar VAZIA: aí vale para todas as lojas.",
        "# Linha com # é ignorada. Apague o # para ativar a linha.",
        "#",
        "# As linhas abaixo são os logins que o script NÃO conseguiu resolver,",
        "# do que mais pesa para o que menos pesa. Ao lado, os candidatos que",
        "# ele encontrou — confira antes de usar: semelhança de nome não é",
        "# prova, e atribuir errado faz o vendedor ver pedido do colega.",
        "",
    ]
    for login, unidade, peso, dica in pendentes:
        linhas.append(f"# {peso:>7,} linha(s) · {login} em {unidade}")
        if dica:
            linhas.append(f"#   candidatos: {dica}")
        linhas.append(f"# {login};{unidade};")
        linhas.append("")
    caminho.parent.mkdir(parents=True, exist_ok=True)
    caminho.write_text("\n".join(linhas), encoding="utf-8")


def carregar_apelidos_do_crm() -> dict[str, str]:
    """Grafia errada → grafia correta, do mapa de apelidos do CRM.

    O Radar grava "ANA CAROLINA"; o cadastro tem "ANNA", com dois N. Nenhuma
    comparação por prefixo resolve isso, e inventar semelhança aproximada
    aqui casaria nomes que não devem casar.

    O CRM já tem a tabela person_aliases justamente para grafia divergente, e
    ela é mantida por quem conhece a equipe. Usá-la significa que corrigir um
    nome UMA VEZ, no CRM, conserta as faltas, o placar e a carteira juntos —
    em vez de um de-para só das faltas, que ninguém lembraria de atualizar.

    Segue a cadeia (A→B→C) com limite, para apelido circular não travar.
    """
    caminho = Path(os.environ.get("PASSINI_CRM_DATA")
                   or "/srv/passini/data/crm") / "passini_dashboard.db"
    if not caminho.exists():
        return {}
    bruto: dict[str, str] = {}
    try:
        conn = sqlite3.connect(f"file:{caminho}?mode=ro", uri=True)
        cid = conn.execute("SELECT id FROM companies LIMIT 1").fetchone()[0]
        for r in conn.execute(
                "SELECT alias_key, canonical_key FROM person_aliases"
                " WHERE company_id = ?", (cid,)):
            if r[0] and r[1]:
                bruto[limpa(r[0]).upper()] = limpa(r[1]).upper()
        conn.close()
    except sqlite3.Error:
        return {}
    resolvido: dict[str, str] = {}
    for alias in bruto:
        destino, visto = alias, {alias}
        for _ in range(10):
            proximo = bruto.get(destino)
            if not proximo or proximo in visto:
                break
            destino, _ = proximo, visto.add(proximo)
        resolvido[alias] = destino
    return resolvido


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
            # TODA PESSOA CADASTRADA, COM OU SEM UNIDADE.
            #
            # A primeira versão exigia base_unit preenchida, porque é a
            # unidade que desfaz a ambiguidade entre dois homônimos. Só que
            # isso apagava do mapa quem está cadastrado SEM unidade — Alessana
            # e Alex, por exemplo — e o diagnóstico passava a afirmar "nenhum
            # vendedor começa com ALEX", que é falso. Exigir o dado que ajuda
            # a desempatar para sequer considerar a pessoa é trocar um
            # problema de ambiguidade por um de invisibilidade.
            #
            # Sem unidade a pessoa ainda resolve pela primeira passada (nome
            # único); só não participa do desempate por loja.
            #
            # ORDER BY valid_from DESC + só preencher o vazio = fica a unidade
            # mais recente de quem já mudou de loja.
            for r in conn.execute(
                    "SELECT person_name, base_unit FROM people_records"
                    " WHERE company_id = ?"
                    " ORDER BY date(valid_from) DESC", (cid,)):
                nome = limpa(r[0])
                if not nome:
                    continue
                if not nomes.get(nome):
                    nomes[nome] = limpa(r[1]).upper()
        except sqlite3.Error as exc:
            print(f"   (people_records indisponível: {exc})")
        conn.close()
    except sqlite3.Error as exc:
        print(f"   (não consegui ler os vendedores: {exc})")
    return nomes


def carregar_catalogo_do_crm() -> dict[str, dict[str, str]]:
    """item_code → marca, tipo e descrição, do catálogo do CRM.

    A MARCA NÃO VEM DO RADAR.
    A coluna que ele chama de "Fabricante" guarda a REFERÊNCIA do fabricante
    — números como 100031 —, não o nome. O filtro de marca da tela saiu
    cheio de código, sem sentido para quem olha. O nome existe na coluna
    "Referencial" ("00072 FRAS-LE"), grudado a um código de fornecedor, mas
    usar aquilo criaria um terceiro vocabulário de marca na empresa.

    O catálogo do CRM já tem marca, tipo e linha, e é o mesmo que alimenta a
    tela de Marcas. Puxar de lá faz o filtro de faltas falar a mesma língua
    do resto do sistema — "NAKATA" aqui é "NAKATA" lá.
    """
    caminho = Path(os.environ.get("PASSINI_CRM_DATA")
                   or "/srv/passini/data/crm") / "passini_dashboard.db"
    if not caminho.exists():
        return {}
    catalogo: dict[str, dict[str, str]] = {}
    try:
        conn = sqlite3.connect(f"file:{caminho}?mode=ro", uri=True)
        cid = conn.execute("SELECT id FROM companies LIMIT 1").fetchone()[0]
        # TIPO E DESCRIÇÃO do catálogo; MARCA, não.
        #
        # item_catalog.brand_name está sujo: a primeira versão puxou de lá e
        # o filtro encheu de "001/1LT", "0W20SP/7000 HYBRID" — código de
        # embalagem e especificação de lubrificante, não marca. A marca que a
        # empresa usa, e que alimenta a tela de Marcas, é
        # fact_sales_detail.brand_name (BRAND_FILTER_EXPR["brand"] no
        # backend). Trocar a fonte aqui é o que faz o filtro de faltas e o de
        # marcas listarem as mesmas marcas.
        for r in conn.execute(
                "SELECT item_code, item_type, item_subgroup, sub_description"
                "  FROM item_catalog WHERE company_id = ?", (cid,)):
            codigo = limpa(r[0])
            if codigo and codigo not in catalogo:
                catalogo[codigo] = {
                    "marca": "",
                    "tipo": limpa(r[1]),
                    "linha": limpa(r[2]),
                    "descricao": limpa(r[3]),
                }
        # A marca mais frequente no faturamento daquele código. Mais
        # frequente, não a última: uma linha digitada errada não deve
        # renomear a marca da peça inteira.
        melhor: dict[str, tuple[int, str]] = {}
        for r in conn.execute(
                "SELECT item_code, brand_name, COUNT(*) n"
                "  FROM fact_sales_detail"
                " WHERE company_id = ? AND TRIM(COALESCE(item_code,'')) <> ''"
                "   AND TRIM(COALESCE(brand_name,'')) <> ''"
                " GROUP BY item_code, brand_name", (cid,)):
            codigo, marca, n = limpa(r[0]), limpa(r[1]), int(r[2] or 0)
            if not codigo or not marca:
                continue
            if n > melhor.get(codigo, (0, ""))[0]:
                melhor[codigo] = (n, marca)
        for codigo, (_, marca) in melhor.items():
            catalogo.setdefault(codigo, {"marca": "", "tipo": "", "linha": "",
                                         "descricao": ""})["marca"] = marca
        print(f"   Marca do faturamento para {len(melhor):,} código(s)")
        conn.close()
    except sqlite3.Error as exc:
        print(f"   (catálogo do CRM indisponível: {exc})")
    return catalogo


def _sem_sufixo(chave: str) -> str:
    """GABRIELLAJEADO → GABRIEL · TIAGOBALCAO → TIAGO."""
    compacto = chave.replace(" ", "")
    for suf in SUFIXOS_LOGIN:
        if compacto.endswith(suf) and len(compacto) > len(suf) + 2:
            return compacto[: -len(suf)]
    return chave


def resolver_vendedores(
    pares: set[tuple[str, str]], vendedores: dict[str, str],
    mapa_unidade: dict[str, str], apelidos: dict[str, str] | None = None,
) -> tuple[dict[tuple[str, str], str], set[str], set[str], dict[str, str]]:
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
    # UMA PESSOA, VÁRIAS GRAFIAS — isso não é ambiguidade.
    #
    # O cadastro guarda "NICOLAS DA SILVA" e "NICOLAS DA SILVA (VENDAS)" como
    # entradas distintas; o mesmo vale para Heider, Leonardo Santos, Marcelo
    # Rossner e Adriana Barros. chave_nome() derruba o sufixo do papel, então
    # as duas viram a mesma chave — mas a primeira versão guardava as duas
    # como candidatas e declarava ambiguidade. Resultado: cinco pessoas
    # ficaram sem dono por um defeito meu, não por falta de dado.
    #
    # Agora cada chave guarda UM nome canônico: prefiro o que tem unidade no
    # cadastro e, empatando, o mais longo — que costuma ser a grafia completa
    # usada no faturamento.
    def melhor(a: str, b: str) -> str:
        tem_a, tem_b = bool(vendedores.get(a)), bool(vendedores.get(b))
        if tem_a != tem_b:
            return a if tem_a else b
        return a if len(a) >= len(b) else b

    por_chave: dict[str, str] = {}
    for v in vendedores:
        k = chave_nome(v)
        if not k:
            continue
        por_chave[k] = melhor(por_chave[k], v) if k in por_chave else v

    por_primeiro: dict[str, list[str]] = {}
    # Nome grudado com o sobrenome: NATHANPEGLOW é NATHAN MARTINS PEGLOW.
    # Guardamos também primeiro+último compactados para alcançar esses.
    por_compacto: dict[str, str] = {}
    for k, v in por_chave.items():
        partes = k.split(" ")
        por_primeiro.setdefault(partes[0], []).append(v)
        por_compacto.setdefault(k.replace(" ", ""), v)
        if len(partes) > 1:
            por_compacto.setdefault(partes[0] + partes[-1], v)

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
    apelidos = apelidos or {}
    for usuario, unidade in pares:
        k = chave_nome(usuario)
        if not k:
            continue
        # Apelido do CRM primeiro: "ANA CAROLINA" vira "ANNA ..." antes de
        # qualquer comparação, então as três passadas seguintes trabalham já
        # com a grafia certa.
        k = apelidos.get(k, k)
        candidatos = [v for kk, v in por_chave.items()
                      if kk == k or kk.startswith(k + " ")]
        if len(candidatos) == 1:
            de_para[(usuario, unidade)] = candidatos[0]
            continue
        if not candidatos:
            # Login grudado: NATHANPEGLOW → NATHAN MARTINS PEGLOW.
            achado = por_compacto.get(_sem_sufixo(k).replace(" ", ""))
            if achado:
                de_para[(usuario, unidade)] = achado
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
    sources: Path, mapa_unidade: dict[str, str],
    codigos_pedidos: set[str] | None = None,
) -> tuple[dict, "pd.DataFrame", "pd.DataFrame"]:
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
    vazio_item = pd.DataFrame(
        columns=["unidade", "codigo", "familia", "estoque", "ultima_entrada"])
    sys.path.insert(0, "/srv/passini/apps/radar-rupturas")
    try:
        analytics = importlib.import_module("analytics")
    except ImportError as exc:
        print(f"   >> analytics do Radar indisponível ({exc}); "
              f"sem família e sem estoque.")
        return {}, vazio, vazio_item

    familias = {}
    p_subs = sources / "substitutos.pkl"
    if p_subs.exists():
        familias = analytics.gerar_familias_substitutos(pd.read_pickle(p_subs))
        print(f"\n8) FAMÍLIAS — {len(familias):,} códigos em "
              f"{len({e['FamiliaID'] for e in familias.values()}):,} famílias")
    else:
        print(f"\n8) FAMÍLIAS — {p_subs} não existe; cada peça vira a própria "
              f"família e a ruptura sai inflada.")

    p_stock = sources / "stock.pkl"
    if not p_stock.exists():
        print(f"   >> {p_stock} não existe; sem estoque não há 'resolvido'.")
        return familias, vazio, vazio_item

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
    est["codigo"] = preparado["GTIN"].astype(str)
    fam = est.groupby(["unidade", "familia"], as_index=False).agg(
        estoque=("qtd", "sum"), ultima_entrada=("entrada", "max"))
    fam["ultima_entrada"] = fam["ultima_entrada"].dt.strftime("%Y-%m-%d")
    com = int((fam["estoque"] > 0).sum())
    print(f"   ESTOQUE — {len(est):,} posições → {len(fam):,} unidade × família")
    print(f"   Com saldo: {com:,} ({100 * com / max(1, len(fam)):.0f}%) · "
          f"zeradas: {len(fam) - com:,}")
    print(f"   Unidades: {', '.join(sorted(set(est['unidade'])))}")

    # Item a item: tudo que tem saldo, MAIS os códigos pedidos mesmo com zero.
    # O zero é o que permite a tela dizer "a peça pedida está zerada, quem tem
    # é o substituto" em vez de um "Tem na loja" que manda o gerente procurar
    # na prateleira errada.
    com_saldo = est["qtd"] > 0
    pedido = est["codigo"].isin(codigos_pedidos) if codigos_pedidos else False
    itens = est[com_saldo | pedido].groupby(
        ["unidade", "codigo"], as_index=False).agg(
        familia=("familia", "first"), estoque=("qtd", "sum"),
        ultima_entrada=("entrada", "max"))
    itens["ultima_entrada"] = itens["ultima_entrada"].dt.strftime("%Y-%m-%d")
    zerados = int((itens["estoque"] <= 0).sum())
    print(f"   Posições guardadas: {len(itens):,} "
          f"({len(itens) - zerados:,} com saldo, {zerados:,} zeradas de peça pedida)")
    return familias, fam, itens


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
-- Posição por CÓDIGO, dentro da família.
--
-- Guarda duas coisas diferentes e as duas são necessárias:
--   · quem da família TEM saldo (para dizer "pediu A, chegou B");
--   · quanto o código PEDIDO tem, mesmo que seja ZERO.
--
-- O zero é o que faltava e gerou erro de leitura: a peça 101487 (SYL) tem 0
-- na Zona Sul e a família tem 5, que são de outro código (80539, TRW). A tela
-- mostrava "Estoque 5 · Tem na loja" numa linha identificada como 101487/SYL,
-- e o gerente foi conferir na prateleira e não achou. Sem a linha de zero não
-- há como a tela distinguir "a peça está lá" de "o substituto está lá".
--
-- Só os códigos que aparecem nas faltas entram: guardar as 343 mil posições
-- do estoque inteiro triplicaria o arquivo para responder o que ninguém
-- pergunta.
CREATE TABLE estoque_item (
    unidade        TEXT NOT NULL,
    item_code      TEXT NOT NULL,
    familia        TEXT NOT NULL,
    estoque        REAL NOT NULL,
    ultima_entrada TEXT,
    PRIMARY KEY (unidade, item_code)
);
CREATE INDEX idx_estoque_item_fam ON estoque_item(unidade, familia);
CREATE TABLE faltas_meta (chave TEXT PRIMARY KEY, valor TEXT);
"""


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--destino", default=DESTINO_PADRAO)
    ap.add_argument("--simular", action="store_true",
                    help="apura e relata sem gravar")
    ap.add_argument("--depara", default=DEPARA_PADRAO,
                    help="arquivo de de-para login do Radar → vendedor do CRM")
    ap.add_argument("--se-mudou", action="store_true",
                    help="só reprocessa se o arquivo do Radar for mais novo que "
                         "o destino (para rodar de hora em hora sem custo)")
    args = ap.parse_args()

    origem = achar_pickle()

    # SAI ANTES DE LER OS 44 MB.
    #
    # A comparação é de data de modificação, feita antes de abrir qualquer
    # coisa. É o que permite agendar de hora em hora: nos dias em que o Radar
    # não foi importado, o script custa milissegundos e não toca no arquivo
    # que o CRM está lendo. O de-para à mão também conta como mudança — editar
    # o CSV e não ver efeito até o Radar ser importado seria desconcertante.
    if args.se_mudou and not args.simular:
        destino_atual = Path(args.destino)
        if destino_atual.exists():
            t_destino = destino_atual.stat().st_mtime
            t_origem = origem.stat().st_mtime
            dp = Path(args.depara)
            t_depara = dp.stat().st_mtime if dp.exists() else 0
            if t_origem <= t_destino and t_depara <= t_destino:
                from datetime import datetime as _dt
                print(f"Sem novidade: {origem.name} de "
                      f"{_dt.fromtimestamp(t_origem):%d/%m %H:%M} e destino de "
                      f"{_dt.fromtimestamp(t_destino):%d/%m %H:%M}. Nada a fazer.")
                return 0

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
    apelidos = carregar_apelidos_do_crm()
    de_para_vend, ambiguos, orfaos, motivos = resolver_vendedores(
        pares, vendedores, mapa, apelidos)

    # O DE-PARA À MÃO MANDA.
    #
    # Ele é a decisão de quem conhece a equipe; o resto é inferência. Aplicar
    # depois, por cima, garante que uma correção humana nunca seja desfeita
    # por um palpite do script — e que ela também sobreponha um acerto
    # automático que esteja errado.
    manual = carregar_depara_manual(Path(args.depara))

    # NOME DE DESTINO QUE NÃO EXISTE É PIOR QUE NENHUM DE-PARA.
    #
    # Se a linha apontar para um vendedor que o CRM não conhece — um erro de
    # digitação no nome completo, por exemplo —, a falta recebe um "dono"
    # com quem nenhum login casa. A tela do vendedor abre vazia e ninguém
    # descobre, porque vazia é indistinguível de "não faltou nada".
    conhecidos = {chave_nome(v) for v in vendedores}
    invalidos = {alvo for alvo in manual.values()
                 if chave_nome(alvo) not in conhecidos}

    aplicados = 0
    for (login, unidade) in list(pares):
        alvo = (manual.get((login.upper(), unidade.upper()))
                or manual.get((login.upper(), "")))
        if alvo:
            de_para_vend[(login, unidade)] = alvo
            ambiguos.discard(login)
            orfaos.discard(login)
            motivos.pop(f"{login} / {unidade}", None)
            aplicados += 1
    # Quanto do ARQUIVO cada grupo representa. Contar nomes engana: um nome
    # sem dono com 12 mil linhas pesa mais que dez com cem.
    peso = {}
    for u, un in zip(usuario_bruto, unidades):
        if u and un:
            peso[(u, un)] = peso.get((u, un), 0) + 1
    linhas_ok = sum(n for p, n in peso.items() if p in de_para_vend)

    print(f"\n5) VENDEDOR — {len(vendedores)} nome(s) conhecido(s) no CRM")
    print(f"   Apelidos de grafia vindos do CRM: {len(apelidos)}")
    print(f"   De-para à mão ({args.depara}): "
          f"{len(manual)} regra(s), {aplicados} aplicada(s)")
    if invalidos:
        print(f"   >> {len(invalidos)} destino(s) NÃO EXISTEM no CRM — a falta")
        print("      ficaria com dono que nenhum login encontra, e a tela do")
        print("      vendedor abriria vazia. Corrija no arquivo:")
        for alvo in sorted(invalidos)[:6]:
            print(f"      · {alvo}")
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
    # Modelo para preencher, com os pendentes e os candidatos já apurados.
    alvo_modelo = Path(args.depara)
    if motivos and not alvo_modelo.exists():
        escrever_modelo_depara(
            alvo_modelo,
            sorted(((r.split(" / ")[0], r.split(" / ")[1],
                     peso.get((r.split(" / ")[0], r.split(" / ")[1]), 0),
                     motivos[r].split("→")[-1].strip() if "→" in motivos[r] else "")
                    for r in motivos), key=lambda x: -x[2]))
        print(f"\n   >> Criei {alvo_modelo} com os {len(motivos)} pendentes.")
        print("      Preencha as linhas que souber e rode de novo.")

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

    # ── Marca, tipo e descrição: do catálogo do CRM ─────────────────────────
    catalogo = carregar_catalogo_do_crm()
    achou = resumo["item_code"].isin(catalogo.keys()).sum()
    print(f"\n7) CATÁLOGO — {len(catalogo):,} item(ns) no CRM")
    print(f"   Linhas reconhecidas (tipo e descrição): {achou:,} de "
          f"{len(resumo):,} ({100 * achou / max(1, len(resumo)):.0f}%)")
    # MARCA DESCONHECIDA FICA VAZIA, não vira o código do Radar.
    #
    # O "Fabricante" do Radar é referência numérica (100031). Usá-lo de
    # reserva encheria o filtro de marca com código — foi exatamente o que
    # apareceu na tela. Vazio é honesto: a peça não tem marca conhecida, e o
    # filtro simplesmente não a oferece.
    resumo["fabricante"] = [catalogo.get(c, {}).get("marca", "")
                            for c in resumo["item_code"]]
    resumo["tipo"] = [
        catalogo.get(c, {}).get("tipo") or t
        for c, t in zip(resumo["item_code"], resumo["tipo"])]
    resumo["item"] = [
        catalogo.get(c, {}).get("descricao") or i
        for c, i in zip(resumo["item_code"], resumo["item"])]
    marcas = sorted({m for m in resumo["fabricante"] if m})
    com_marca = int(sum(1 for m in resumo["fabricante"] if m))
    print(f"   Linhas com marca: {com_marca:,} de {len(resumo):,} "
          f"({100 * com_marca / max(1, len(resumo)):.0f}%)")
    print(f"   Marcas distintas: {len(marcas):,} · "
          f"amostra: {', '.join(marcas[:8])}")
    # Marca que parece código é cadastro sujo chegando na tela.
    numericas = [m for m in marcas if m.replace("/", "").replace(".", "").isdigit()]
    if numericas:
        print(f"   >> {len(numericas)} marca(s) com cara de código "
              f"({', '.join(numericas[:5])}) — vale olhar o cadastro.")

    # ── Família e estoque ───────────────────────────────────────────────────
    familias, estoque, estoque_itens = familia_e_estoque(
        origem.parent, mapa, set(resumo["item_code"]))
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
        if len(estoque_itens):
            conn.executemany(
                "INSERT OR REPLACE INTO estoque_item"
                " (unidade, item_code, familia, estoque, ultima_entrada)"
                " VALUES (?,?,?,?,?)",
                estoque_itens[["unidade", "codigo", "familia", "estoque",
                               "ultima_entrada"]]
                .astype(object).where(pd.notna(estoque_itens[[
                    "unidade", "codigo", "familia", "estoque",
                    "ultima_entrada"]]), None)
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
    print(f"\n9) GRAVADO: {destino} · {tamanho:,.0f} KB")
    print("   O arquivo anterior só foi substituído depois do novo ficar pronto.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
