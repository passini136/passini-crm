"""
Dá para dizer QUEM pediu a peça e SE ela foi resolvida?

Uso (venv do RADAR, que é quem tem pandas):
    /srv/passini/venv/radar/bin/python /srv/passini/apps/crm-comercial/diag_radar_resolucao.py

POR QUE ESTE DIAGNÓSTICO EXISTE

O painel de faltas mudou de finalidade. Não é lista de compras: é
acompanhamento. O gerente precisa ver as faltas da unidade dele; o vendedor,
as solicitações DELE — e, principalmente, o que aconteceu depois. Chegou?
Foi comprada? A ideia é mostrar que ruptura está sendo olhada, não dizer ao
comprador o que comprar.

Isso exige dois dados que eu NÃO exportei e nem sei se existem:

  1. QUEM PEDIU. O arquivo tem a coluna Usuario, com 83 valores distintos.
     Se esses nomes não casarem com os vendedores do CRM, não há como montar
     "as minhas solicitações" — e um painel que mostra as faltas de todo
     mundo para cada vendedor não é acompanhamento, é ruído.

  2. O QUE ACONTECEU DEPOIS. Há colunas chamadas "Ordem Compra", "P. Entrada"
     e "Registro.1" que o Radar não usa, além de outras sem nome. Elas podem
     conter exatamente o desfecho — ou podem estar vazias. Nunca olhei o
     conteúdo delas.

Este diagnóstico lê o conteúdo real dessas colunas antes de eu projetar
qualquer tela em cima delas. Também testa um caminho alternativo que não
depende do Radar: perguntar ao próprio faturamento do CRM se a peça que
faltou voltou a vender depois.

NÃO ALTERA NADA.
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
RADAR_DB = achar([
    os.environ.get("DATABASE_PATH", "") or "x",
    "/srv/passini/data/radar/radar.db",
], "o banco do Radar")

req = pd.read_pickle(SOLIC)
conn = sqlite3.connect(f"file:{CRM_DB}?mode=ro", uri=True)
conn.row_factory = sqlite3.Row
cid = conn.execute("SELECT id FROM companies LIMIT 1").fetchone()["id"]
print(f"Solicitação: {len(req):,} linhas\n")


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


def chave(v: str) -> str:
    """Nome comparável: sem acento, sem (VENDAS), sem pontuação."""
    t = limpa(v).upper()
    for a, b in zip("ÁÀÃÂÄÉÊËÍÏÓÕÔÖÚÜÇ", "AAAAAEEEIIOOOOUUC"):
        t = t.replace(a, b)
    t = re.sub(r"\((VENDAS|TELEVENDAS|BALCAO)\)", " ", t)
    return re.sub(r"[^A-Z0-9 ]", " ", t).strip()


# ── 1. O que há nas colunas que ninguém usa ─────────────────────────────────
print("1) O CONTEÚDO DAS COLUNAS QUE O RADAR IGNORA")
print("   Antes de projetar tela em cima delas, olhar o que têm dentro.\n")
candidatas = ["Ordem Compra", "P. Entrada", "Registro.1", "Lote Producao",
              "Obs", "Obs.1", "Referencial", "Numero", "col_19",
              "Unnamed: 18", "LAGOM UNIDADE", "Sub"]
print(f"   {'COLUNA':<18}{'PREENCHIDA':>12}{'DISTINTOS':>11}  AMOSTRA")
for nome in candidatas:
    if nome not in req.columns:
        print(f"   {nome[:17]:<18}{'— não existe —':>12}")
        continue
    vals = req[nome].map(limpa)
    cheias = vals[vals.ne("")]
    pct = 100 * len(cheias) / max(1, len(req))
    amostra = " | ".join(str(v)[:16] for v in cheias.unique()[:4]) if len(cheias) else ""
    print(f"   {nome[:17]:<18}{pct:>11.1f}%{cheias.nunique():>11,}  {amostra[:58]}")
print("\n   >> Coluna com 0% é coluna morta: não dá para dizer 'chegou' a partir")
print("      dela, por mais que o nome prometa.")

# ── 2. Quem pediu casa com os vendedores do CRM? ────────────────────────────
print("\n2) A COLUNA Usuario SÃO OS VENDEDORES?")
col_user = next((c for c in req.columns if str(c).strip().lower() == "usuario"), None)
if col_user is None:
    print("   Ausente.")
else:
    usuarios = req[col_user].map(limpa)
    cheias = usuarios[usuarios.ne("")]
    print(f"   Preenchida em {len(cheias):,} de {len(req):,} "
          f"({100 * len(cheias) / len(req):.1f}%) · {cheias.nunique()} distintos")

    vendedores = set()
    for tabela, coluna in (("fact_sales_detail", "seller_name"),
                           ("fact_vendor_summary", "seller_name"),
                           ("crm_client_summary", "seller_name")):
        try:
            vendedores |= {limpa(r[0]) for r in conn.execute(
                f"SELECT DISTINCT {coluna} FROM {tabela} WHERE company_id = ?", (cid,))}
        except sqlite3.Error:
            pass
    vendedores -= {""}
    chaves_crm = {chave(v) for v in vendedores} - {""}
    print(f"   Vendedores conhecidos no CRM: {len(vendedores):,}")

    casam = {u for u in cheias.unique() if chave(u) in chaves_crm}
    # Nome do Radar pode ser só o primeiro nome ou o login. Testa também se o
    # nome do Radar é PREFIXO de algum vendedor — "GABRIELY" x "GABRIELY X".
    parciais = set()
    for u in cheias.unique():
        k = chave(u)
        if not k or k in chaves_crm:
            continue
        if any(c.startswith(k + " ") or c == k for c in chaves_crm):
            parciais.add(u)
    print(f"   Casam exato:   {len(casam)} de {cheias.nunique()}")
    print(f"   Casam parcial: {len(parciais)} (nome do Radar é o começo do nome do CRM)")

    contagem = cheias.value_counts()
    print(f"\n   {'USUÁRIO NO RADAR':<28}{'LINHAS':>10}  CASA COM O CRM?")
    for u, n in contagem.head(15).items():
        if u in casam:
            veredito = "sim, exato"
        elif u in parciais:
            alvo = next((c for c in chaves_crm
                         if c.startswith(chave(u) + " ") or c == chave(u)), "")
            veredito = f"parcial → {alvo[:24]}"
        else:
            veredito = "← NÃO"
        print(f"   {str(u)[:27]:<28}{n:>10,}  {veredito}")
    cobertura = cheias.isin(casam | parciais).sum()
    print(f"\n   Linhas com usuário identificável: {cobertura:,} "
          f"({100 * cobertura / max(1, len(req)):.1f}% do arquivo)")
    print("   >> Abaixo de 50% não dá para montar 'as minhas solicitações':")
    print("      metade dos vendedores veria uma lista vazia e concluiria que")
    print("      o painel não funciona.")

# ── 3. O Radar já tem tratativa registrada? ─────────────────────────────────
# O radar.db tem tabela treatments (status, responsável, previsão). Se a
# equipe já usa, o desfecho está ali e não precisa ser inventado no CRM.
print("\n3) O RADAR JÁ REGISTRA TRATATIVA?")
try:
    rconn = sqlite3.connect(f"file:{RADAR_DB}?mode=ro", uri=True)
    rconn.row_factory = sqlite3.Row
    total = rconn.execute("SELECT COUNT(*) n FROM treatments").fetchone()["n"]
    print(f"   Tratativas registradas: {total:,}")
    if total:
        print(f"   {'STATUS':<18}{'QTD':>8}  {'PERÍODO':<18}")
        for r in rconn.execute(
                "SELECT status, COUNT(*) n, MIN(periodo) a, MAX(periodo) b"
                " FROM treatments GROUP BY status ORDER BY n DESC"):
            print(f"   {str(r['status'])[:17]:<18}{r['n']:>8,}  {r['a']} a {r['b']}")
        ult = rconn.execute(
            "SELECT MAX(updated_at) u FROM treatments").fetchone()["u"]
        print(f"   Última atualização: {ult}")
        print("   >> Se a equipe usa isto, o desfecho já existe e o CRM só precisa")
        print("      mostrar. Se está parado há meses, o painel não tem o que dizer")
        print("      sobre 'foi resolvido' — e prometer isso seria mentira.")
    else:
        print("   >> VAZIA. Ninguém registra tratativa no Radar. O 'chegou?' terá")
        print("      de sair de outro lugar — veja o passo 4.")
    rconn.close()
except sqlite3.Error as exc:
    print(f"   Não consegui ler {RADAR_DB}: {exc}")

# ── 4. O caminho que não depende do Radar ───────────────────────────────────
# Se a peça faltou no mês M e VENDEU no mês M ou depois, ela chegou. Isso o
# CRM responde sozinho, com o faturamento que já tem.
print("\n4) A PEÇA QUE FALTOU VOLTOU A VENDER?")
faltas_db = Path("/srv/passini/data/compartilhado/faltas.db")
if not faltas_db.exists():
    print(f"   {faltas_db} não existe — rode o exportar_faltas.py antes.")
else:
    fconn = sqlite3.connect(f"file:{faltas_db}?mode=ro", uri=True)
    fconn.row_factory = sqlite3.Row
    ultima_comp = fconn.execute(
        "SELECT MAX(competencia) c FROM faltas_resumo").fetchone()["c"]
    # Janela fechada: o mês corrente ainda está acontecendo e contaria como
    # "não resolvido" tudo que vai ser resolvido semana que vem.
    anterior = fconn.execute(
        "SELECT competencia FROM faltas_resumo WHERE competencia < ?"
        " ORDER BY competencia DESC LIMIT 1", (ultima_comp,)).fetchone()
    comp_fechada = anterior["competencia"] if anterior else ultima_comp
    alvo = fconn.execute(
        "SELECT unidade, competencia, item_code, pedidos FROM faltas_resumo"
        " WHERE competencia = ? ORDER BY pedidos DESC LIMIT 300",
        (comp_fechada,)).fetchall()
    print(f"   Mês analisado: {comp_fechada} (o mais recente FECHADO; "
          f"{ultima_comp} ainda está correndo)")
    resolvidas = sem_venda = 0
    for r in alvo:
        vendeu = conn.execute(
            "SELECT 1 FROM fact_sales_detail WHERE company_id = ?"
            "   AND UPPER(item_code) = ? AND competence >= ? AND net_value > 0"
            " LIMIT 1", (cid, r["item_code"].upper(), r["competencia"])).fetchone()
        if vendeu:
            resolvidas += 1
        else:
            sem_venda += 1
    tot = max(1, len(alvo))
    print(f"   Das {len(alvo)} peças mais pedidas em {comp_fechada}:")
    print(f"      voltaram a vender no mês ou depois: {resolvidas:>4} ({100 * resolvidas / tot:.0f}%)")
    print(f"      não venderam desde então:           {sem_venda:>4} ({100 * sem_venda / tot:.0f}%)")
    print("   >> 'Voltou a vender' é prova de que chegou. 'Não vendeu' NÃO prova")
    print("      que não chegou — pode ter chegado e ninguém ter procurado mais.")
    print("      Serve para dizer RESOLVIDO com segurança; o resto fica EM ABERTO.")
    fconn.close()

conn.close()
print("\nNada foi alterado.")
