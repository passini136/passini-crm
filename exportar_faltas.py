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
    pedidos      INTEGER NOT NULL,   -- quantas vezes foi pedida no mês
    ultima_data  TEXT,
    item         TEXT,
    fabricante   TEXT,
    tipo         TEXT,
    usuarios     TEXT,               -- quem pediu, separado por vírgula
    fonte_codigo TEXT,               -- de qual coluna do Radar veio o código
    PRIMARY KEY (unidade, competencia, item_code)
);
CREATE INDEX idx_faltas_item ON faltas_resumo(item_code);
CREATE INDEX idx_faltas_comp ON faltas_resumo(competencia, unidade);
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

    # ── Montagem ────────────────────────────────────────────────────────────
    col_item = coluna(req, "Item")
    col_fab = coluna(req, "Fabricante")
    col_tipo = coluna(req, "Tipo")
    col_user = coluna(req, "Usuario", "usuário")

    base = pd.DataFrame({
        "unidade": unidades,
        "competencia": datas.dt.strftime("%Y-%m"),
        "item_code": codigo,
        "data": datas,
        "fonte_codigo": fonte,
        "item": req[col_item].map(limpa) if col_item else "",
        "fabricante": req[col_fab].map(limpa) if col_fab else "",
        "tipo": req[col_tipo].map(limpa) if col_tipo else "",
        "usuario": req[col_user].map(limpa) if col_user else "",
    })
    antes = len(base)
    base = base[base["item_code"].ne("") & base["unidade"].ne("") & ~ruins]
    print(f"\n5) APROVEITÁVEL: {len(base):,} de {antes:,} "
          f"({100 * len(base) / max(1, antes):.1f}%)")
    if base.empty:
        print(">> Nada sobrou. Não grava arquivo vazio por cima do bom.")
        return 1

    def juntar_usuarios(s) -> str:
        nomes = sorted({u for u in s if u})
        return ", ".join(nomes)[:200]

    resumo = base.groupby(["unidade", "competencia", "item_code"], as_index=False).agg(
        pedidos=("item_code", "size"),
        ultima_data=("data", "max"),
        item=("item", "last"),
        fabricante=("fabricante", "last"),
        tipo=("tipo", "last"),
        usuarios=("usuario", juntar_usuarios),
        fonte_codigo=("fonte_codigo", "first"),
    )
    resumo["ultima_data"] = resumo["ultima_data"].dt.strftime("%Y-%m-%d")
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
            "INSERT INTO faltas_resumo (unidade, competencia, item_code, pedidos,"
            " ultima_data, item, fabricante, tipo, usuarios, fonte_codigo)"
            " VALUES (?,?,?,?,?,?,?,?,?,?)",
            resumo[["unidade", "competencia", "item_code", "pedidos", "ultima_data",
                    "item", "fabricante", "tipo", "usuarios", "fonte_codigo"]]
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
    print(f"\n6) GRAVADO: {destino} · {tamanho:,.0f} KB")
    print("   O arquivo anterior só foi substituído depois do novo ficar pronto.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
