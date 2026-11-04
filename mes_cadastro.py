"""Mês de cadastro do cliente, controlado por FAIXA DE CÓDIGO.

O Alfa não exporta a data de cadastro. O que existe é o controle que o Felipe
mantinha à mão: como o código do cliente é sequencial, cada mês corresponde a
uma faixa contínua de códigos (ex.: 102321–103151 = jul/2026).

Por que uma tabela própria, e não uma coluna em crm_client_profiles:
a importação do cadastro de clientes SUBSTITUI a base inteira. Uma coluna lá
seria apagada a cada importação; a faixa sobrevive a todas.

Por que faixa, e não código a código: é assim que o controle sempre foi feito,
a planilha original (99.675 códigos) vira 34 faixas sem perder nada, e um
código novo que chegue depois dentro de uma faixa já informada é resolvido
sozinho.

Granularidade é MÊS E ANO, nunca data. Dois casos antigos não têm mês:
"até dez/2022" (ate=1) e "ano 2023" (mes vazio).
"""
from __future__ import annotations

import bisect
import re
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Any

MESES_ABREV = ["jan", "fev", "mar", "abr", "mai", "jun",
               "jul", "ago", "set", "out", "nov", "dez"]

SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS client_mes_cadastro_faixa (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    company_id INTEGER NOT NULL,
    code_start INTEGER NOT NULL,
    code_end INTEGER NOT NULL,
    ano INTEGER NOT NULL,
    mes INTEGER,                    -- NULL = só o ano é conhecido
    ate INTEGER NOT NULL DEFAULT 0, -- 1 = "até dez/<ano>" (cadastro antigo)
    source TEXT NOT NULL,           -- PLANILHA | MANUAL
    created_by_user_id INTEGER,
    created_at TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_mes_cadastro_faixa
    ON client_mes_cadastro_faixa(company_id, code_start);
"""


def garantir_tabela(conn: sqlite3.Connection) -> None:
    conn.executescript(SCHEMA_SQL)


def rotulo(ano: int | None, mes: int | None, ate: int | bool = 0) -> str:
    if not ano:
        return ""
    if ate:
        return f"até dez/{ano}"
    if not mes:
        return f"{ano} (mês não informado)"
    return f"{MESES_ABREV[int(mes) - 1]}/{ano}"


def competencia(ano: int | None, mes: int | None, ate: int | bool = 0) -> str:
    """AAAA-MM quando o mês é conhecido; vazio nos dois casos antigos."""
    if not ano or not mes or ate:
        return ""
    return f"{int(ano):04d}-{int(mes):02d}"


def codigo_numerico(valor: Any) -> int | None:
    texto = str(valor or "").strip()
    return int(texto) if texto.isdigit() else None


def carregar_planilha_inicial(conn: sqlite3.Connection, company_id: int, seed: Path,
                              agora: str) -> int:
    """Carga da planilha antiga, faixa a faixa.

    Só insere a faixa que não se sobrepõe a nenhuma existente: reiniciar o
    servidor não duplica, e uma faixa acrescentada ao arquivo depois (como
    ago–out/2026) entra no próximo restart sem mexer no que já foi lançado
    pela tela ou pela importação.
    """
    if not seed.exists():
        return 0
    novas = 0
    for linha in seed.read_text(encoding="utf-8").splitlines():
        texto = linha.strip()
        if not texto or texto.startswith("#") or texto.lower().startswith("code_start"):
            continue
        a, b, ano, mes, ate = (texto.split(";") + ["", "", "", "", ""])[:5]
        a, b = int(a), int(b)
        if conn.execute("SELECT 1 FROM client_mes_cadastro_faixa WHERE company_id = ? "
                        "AND code_start <= ? AND code_end >= ? LIMIT 1",
                        (company_id, b, a)).fetchone():
            continue
        conn.execute(
            "INSERT INTO client_mes_cadastro_faixa (company_id, code_start, code_end, ano, mes, ate, "
            "source, created_by_user_id, created_at) VALUES (?,?,?,?,?,?,'PLANILHA',NULL,?)",
            (company_id, a, b, int(ano), int(mes) if mes else None,
             1 if ate.strip() == "1" else 0, agora))
        novas += 1
    conn.commit()
    if novas:
        print(f"[mes-cadastro] carga da planilha: {novas} faixa(s) nova(s)", flush=True)
    return novas


def listar_faixas(conn: sqlite3.Connection, company_id: int) -> list[dict[str, Any]]:
    rows = conn.execute(
        "SELECT id, code_start, code_end, ano, mes, ate, source, created_at "
        "FROM client_mes_cadastro_faixa WHERE company_id = ? ORDER BY code_start",
        (company_id,)).fetchall()
    return [{
        "id": r["id"], "codeStart": r["code_start"], "codeEnd": r["code_end"],
        "ano": r["ano"], "mes": r["mes"], "ate": bool(r["ate"]),
        "rotulo": rotulo(r["ano"], r["mes"], r["ate"]),
        "competencia": competencia(r["ano"], r["mes"], r["ate"]),
        "source": r["source"], "createdAt": r["created_at"],
    } for r in rows]


class Resolvedor:
    """Código → faixa, por busca binária. Montado uma vez por requisição."""

    def __init__(self, faixas: list[dict[str, Any]]):
        self.faixas = faixas
        self.inicios = [f["codeStart"] for f in faixas]

    def faixa(self, codigo: Any) -> dict[str, Any] | None:
        n = codigo_numerico(codigo)
        if n is None:
            return None
        i = bisect.bisect_right(self.inicios, n) - 1
        if i >= 0 and self.faixas[i]["codeStart"] <= n <= self.faixas[i]["codeEnd"]:
            return self.faixas[i]
        return None

    def indice(self, n: int) -> int:
        return bisect.bisect_right(self.inicios, n)


def mes_cadastro_do_cliente(conn: sqlite3.Connection, company_id: int,
                            codigo: Any) -> dict[str, Any] | None:
    n = codigo_numerico(codigo)
    if n is None:
        return None
    r = conn.execute(
        "SELECT ano, mes, ate FROM client_mes_cadastro_faixa WHERE company_id = ? "
        "AND code_start <= ? AND code_end >= ? ORDER BY code_start DESC LIMIT 1",
        (company_id, n, n)).fetchone()
    if not r:
        return None
    return {"ano": r["ano"], "mes": r["mes"], "ate": bool(r["ate"]),
            "rotulo": rotulo(r["ano"], r["mes"], r["ate"]),
            "competencia": competencia(r["ano"], r["mes"], r["ate"])}


_ISO_MES = re.compile(r"^(\d{4})-(\d{2})")


def pendencias(conn: sqlite3.Connection, company_id: int) -> dict[str, Any]:
    """Códigos do cadastro que nenhuma faixa cobre, agrupados em blocos.

    Um bloco termina onde começa uma faixa já informada — é a lacuna que o
    Felipe tem de preencher. A 1ª compra de cada código vai junto como PISTA
    (o cliente não compra antes de existir), nunca como resposta.
    """
    resolv = Resolvedor(listar_faixas(conn, company_id))
    sem_faixa: list[tuple[int, str]] = []
    nao_numericos = 0
    total = 0
    for r in conn.execute("SELECT client_code, first_sale_at FROM crm_client_profiles "
                          "WHERE company_id = ?", (company_id,)):
        total += 1
        n = codigo_numerico(r["client_code"])
        if n is None:
            nao_numericos += 1
            continue
        if resolv.faixa(n) is None:
            sem_faixa.append((n, r["first_sale_at"] or ""))
    sem_faixa.sort()

    blocos: list[dict[str, Any]] = []
    atual: list[tuple[int, str]] = []
    idx_atual = None
    for n, primeira in sem_faixa:
        idx = resolv.indice(n)
        if atual and idx != idx_atual:
            blocos.append(_bloco(atual))
            atual = []
        atual.append((n, primeira))
        idx_atual = idx
    if atual:
        blocos.append(_bloco(atual))
    blocos.sort(key=lambda b: b["codeStart"], reverse=True)  # o mais recente primeiro

    return {
        "totalClientes": total,
        "semMes": len(sem_faixa),
        "naoNumericos": nao_numericos,
        "cobertos": total - len(sem_faixa) - nao_numericos,
        "ultimoCodigoCoberto": resolv.faixas[-1]["codeEnd"] if resolv.faixas else None,
        "blocos": blocos,
    }


def _bloco(itens: list[tuple[int, str]]) -> dict[str, Any]:
    pista: dict[str, list[int]] = {}
    for n, primeira in itens:
        m = _ISO_MES.match(primeira)
        if m:
            pista.setdefault(f"{m.group(1)}-{m.group(2)}", []).append(n)
    return {
        "codeStart": itens[0][0], "codeEnd": itens[-1][0], "quantidade": len(itens),
        "pistaPrimeiraCompra": [
            {"competencia": c, "codeMin": min(v), "codeMax": max(v), "clientes": len(v),
             "rotulo": rotulo(int(c[:4]), int(c[5:7]))}
            for c, v in sorted(pista.items())],
        "semCompra": sum(1 for _, p in itens if not _ISO_MES.match(p)),
    }


def registrar_codigos_novos(conn: sqlite3.Connection, company_id: int, hoje: Any,
                            agora: str) -> dict[str, Any] | None:
    """A partir de nov/2026 o CRM mantém o controle sozinho.

    Código novo que aparece ACIMA do último código com mês é um cliente
    cadastrado desde a importação anterior — recebe o mês/ano da importação.
    Como o código é sequencial, isso vira uma faixa contínua:
      - se a última faixa já é deste mês, ela é estendida até o novo maior código;
      - senão, abre-se a faixa do mês, começando logo depois da última.
    Código sem mês ABAIXO do último coberto é lacuna antiga: não é adivinhado,
    continua na lista de pendentes para ser informado na tela.
    """
    ultima = conn.execute(
        "SELECT id, code_start, code_end, ano, mes, ate FROM client_mes_cadastro_faixa "
        "WHERE company_id = ? ORDER BY code_end DESC LIMIT 1", (company_id,)).fetchone()
    if not ultima:
        return None  # sem nenhuma referência não há de onde partir
    maior = None
    for r in conn.execute("SELECT client_code FROM crm_client_profiles WHERE company_id = ?",
                          (company_id,)):
        n = codigo_numerico(r["client_code"])
        if n is not None and n > ultima["code_end"] and (maior is None or n > maior):
            maior = n
    if maior is None:
        return None
    ano, mes = hoje.year, hoje.month
    novos = conn.execute(
        "SELECT COUNT(*) FROM crm_client_profiles WHERE company_id = ? "
        "AND CAST(client_code AS INTEGER) > ? AND CAST(client_code AS INTEGER) <= ? "
        "AND TRIM(client_code) GLOB '[0-9]*'", (company_id, ultima["code_end"], maior)).fetchone()[0]
    inicio = ultima["code_end"] + 1
    if not ultima["ate"] and ultima["ano"] == ano and ultima["mes"] == mes:
        conn.execute("UPDATE client_mes_cadastro_faixa SET code_end = ? WHERE id = ?",
                     (maior, ultima["id"]))
        faixa_ini = ultima["code_start"]
    elif ultima["mes"] and (ultima["ano"], ultima["mes"]) > (ano, mes):
        return None  # última faixa no futuro: não arrisca, fica pendente
    else:
        conn.execute(
            "INSERT INTO client_mes_cadastro_faixa (company_id, code_start, code_end, ano, mes, ate, "
            "source, created_by_user_id, created_at) VALUES (?,?,?,?,?,0,'AUTO',NULL,?)",
            (company_id, inicio, maior, ano, mes, agora))
        faixa_ini = inicio
    conn.commit()
    return {"codeStart": inicio, "codeEnd": maior, "faixaInicio": faixa_ini,
            "novos": int(novos or 0), "rotulo": rotulo(ano, mes)}


def resumo_para_importacao(conn: sqlite3.Connection, company_id: int) -> str:
    """Frase curta para o histórico de cada importação do cadastro."""
    p = pendencias(conn, company_id)
    if not p["semMes"]:
        return ""
    faixas = ", ".join(f"{b['codeStart']}–{b['codeEnd']}" for b in p["blocos"][:3])
    return (f" · {p['semMes']} código(s) sem mês de cadastro ({faixas}) — "
            f"informar em Importações › Mês de cadastro")


def salvar_faixa(conn: sqlite3.Connection, company_id: int, user_id: int | None,
                 payload: dict[str, Any], hoje: datetime, agora: str) -> dict[str, Any]:
    """Valida e grava uma faixa. Erro sai como ValueError com texto para a tela."""
    a = codigo_numerico(payload.get("codeStart"))
    b = codigo_numerico(payload.get("codeEnd"))
    if a is None or b is None:
        raise ValueError("Informe o código inicial e o final (só números).")
    if a > b:
        raise ValueError("O código inicial é maior que o final.")
    try:
        ano = int(payload.get("ano"))
        mes = int(payload.get("mes"))
    except (TypeError, ValueError):
        raise ValueError("Informe o mês e o ano.")
    if not 1 <= mes <= 12:
        raise ValueError("Mês inválido.")
    if ano < 2000 or (ano, mes) > (hoje.year, hoje.month):
        raise ValueError("Mês/ano fora do período possível (não pode ser no futuro).")
    choque = conn.execute(
        "SELECT code_start, code_end, ano, mes, ate FROM client_mes_cadastro_faixa "
        "WHERE company_id = ? AND code_start <= ? AND code_end >= ? ORDER BY code_start LIMIT 3",
        (company_id, b, a)).fetchall()
    if choque:
        txt = "; ".join(f"{r['code_start']}–{r['code_end']} = {rotulo(r['ano'], r['mes'], r['ate'])}"
                        for r in choque)
        raise ValueError(f"A faixa {a}–{b} se sobrepõe a faixa já informada: {txt}. "
                         f"Exclua a antiga ou ajuste os códigos.")
    # Ordem dos meses tem de acompanhar a ordem dos códigos (código é sequencial).
    antes = conn.execute(
        "SELECT ano, mes, ate FROM client_mes_cadastro_faixa WHERE company_id = ? "
        "AND code_end < ? ORDER BY code_end DESC LIMIT 1", (company_id, a)).fetchone()
    depois = conn.execute(
        "SELECT ano, mes, ate FROM client_mes_cadastro_faixa WHERE company_id = ? "
        "AND code_start > ? ORDER BY code_start LIMIT 1", (company_id, b)).fetchone()
    chave = (ano, mes)
    if antes and antes["mes"] and (antes["ano"], antes["mes"]) > chave:
        raise ValueError(f"Códigos anteriores já estão em {rotulo(antes['ano'], antes['mes'])}, "
                         f"depois de {rotulo(ano, mes)}. Confira o mês ou os códigos.")
    if depois and depois["mes"] and (depois["ano"], depois["mes"]) < chave:
        raise ValueError(f"Códigos posteriores já estão em {rotulo(depois['ano'], depois['mes'])}, "
                         f"antes de {rotulo(ano, mes)}. Confira o mês ou os códigos.")
    cur = conn.execute(
        "INSERT INTO client_mes_cadastro_faixa (company_id, code_start, code_end, ano, mes, ate, "
        "source, created_by_user_id, created_at) VALUES (?,?,?,?,?,0,'MANUAL',?,?)",
        (company_id, a, b, ano, mes, user_id, agora))
    conn.commit()
    return {"id": cur.lastrowid, "codeStart": a, "codeEnd": b, "rotulo": rotulo(ano, mes)}


def excluir_faixa(conn: sqlite3.Connection, company_id: int, faixa_id: Any) -> dict[str, Any]:
    r = conn.execute("SELECT * FROM client_mes_cadastro_faixa WHERE company_id = ? AND id = ?",
                     (company_id, faixa_id)).fetchone()
    if not r:
        raise ValueError("Faixa não encontrada.")
    conn.execute("DELETE FROM client_mes_cadastro_faixa WHERE company_id = ? AND id = ?",
                 (company_id, faixa_id))
    conn.commit()
    return {"codeStart": r["code_start"], "codeEnd": r["code_end"],
            "rotulo": rotulo(r["ano"], r["mes"], r["ate"]), "source": r["source"]}
