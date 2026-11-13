"""
Quanto da meta de contatos ATIVOS veio de cliente que procurou (cotação recebida)?

Uso (venv do CRM):
    /srv/passini/venv/crm/bin/python /srv/passini/apps/crm-comercial/diag_ligacao_cotacao.py
    /srv/passini/venv/crm/bin/python /srv/passini/apps/crm-comercial/diag_ligacao_cotacao.py 2026-10-01

POR QUE ESTE DIAGNÓSTICO EXISTE

Até 13/11/2026 a tela Cotações não registrava contato nenhum, e o formulário de
contato nascia sempre ATIVO. O cliente ligava pedindo cotação, o vendedor
anotava o atendimento pelo formulário e o ponto ia para a meta de contatos
ativos — sem o vendedor ter ligado.

O script cruza cada cotação RECEPTIVA (telefone/WhatsApp) com contatos ATIVOS
do MESMO vendedor, para o MESMO cliente, no MESMO dia, e separa em duas faixas:

  * até 30 min depois da cotação  → quase certamente o mesmo atendimento
                                    anotado como ativo (o cliente procurou);
  * mais de 30 min depois          → pode ser o RETORNO que o MEC pede
                                    (ligar em até 10 min é ativo legítimo,
                                    mas retorno horas depois também é).

Contato ativo registrado ANTES da cotação fica fora: o vendedor ligou e o
cliente pediu preço na ligação — é ativo legítimo.

NÃO ALTERA NADA. Para corrigir o passado, a decisão é da diretoria.
"""
import os
import sqlite3
import sys
from collections import defaultdict
from datetime import datetime
from pathlib import Path

sys.path.insert(0, "/srv/passini/apps/crm-comercial")

if not os.environ.get("PASSINI_CRM_DATA"):
    for candidate in ("/srv/passini/data/crm", "/srv/passini/data"):
        if (Path(candidate) / "passini_dashboard.db").exists():
            os.environ["PASSINI_CRM_DATA"] = candidate
            break

import backend as b  # noqa: E402

DESDE = sys.argv[1] if len(sys.argv) > 1 else "2026-10-01"
JANELA_MIN = 30


def quando(txt: str) -> datetime | None:
    txt = (txt or "").replace("T", " ")
    for fmt, n in (("%Y-%m-%d %H:%M:%S", 19), ("%Y-%m-%d %H:%M", 16)):
        try:
            return datetime.strptime(txt[:n], fmt)
        except ValueError:
            continue
    return None


def main() -> None:
    conn = sqlite3.connect(f"file:{b.DB_PATH}?mode=ro", uri=True)
    conn.row_factory = sqlite3.Row
    cotacoes = conn.execute(
        "SELECT id, client_key, client_name, seller_name, channel, quoted_at FROM crm_quotes "
        "WHERE initiative = 'RECEPTIVO' AND channel IN ('TELEFONE','WHATSAPP') "
        "AND substr(quoted_at,1,10) >= ? ORDER BY quoted_at", (DESDE,)).fetchall()
    print(f"Cotações receptivas (telefone/WhatsApp) desde {DESDE}: {len(cotacoes)}")
    if not cotacoes:
        return

    perto: dict[tuple[str, str], int] = defaultdict(int)   # (vendedor, mês)
    depois: dict[tuple[str, str], int] = defaultdict(int)
    usados: set[int] = set()
    exemplos = []
    for q in cotacoes:
        tq = quando(q["quoted_at"])
        if not tq:
            continue
        dia = tq.date().isoformat()
        for i in conn.execute(
            "SELECT id, occurred_at, contact_type_code, result_code FROM crm_interactions "
            "WHERE client_key = ? AND UPPER(seller_name) = UPPER(?) AND initiative = 'ATIVO' "
            "AND substr(replace(occurred_at,'T',' '),1,10) = ?",
            (q["client_key"], q["seller_name"], dia)).fetchall():
            if i["id"] in usados:
                continue
            ti = quando(i["occurred_at"])
            if not ti or ti < tq:
                continue
            usados.add(i["id"])
            chave = (b.normalize_whitespace(q["seller_name"]), dia[:7])
            minutos = (ti - tq).total_seconds() / 60
            if minutos <= JANELA_MIN:
                perto[chave] += 1
                if len(exemplos) < 15:
                    exemplos.append((dia, q["seller_name"], q["client_name"], q["channel"],
                                     tq.strftime("%H:%M"), ti.strftime("%H:%M"), i["contact_type_code"]))
            else:
                depois[chave] += 1

    ativos_mes: dict[tuple[str, str], int] = defaultdict(int)
    for r in conn.execute(
        "SELECT seller_name, substr(replace(occurred_at,'T',' '),1,7) mes, COUNT(*) n FROM crm_interactions "
        "WHERE initiative = 'ATIVO' AND substr(replace(occurred_at,'T',' '),1,10) >= ? "
        "GROUP BY seller_name, mes", (DESDE,)).fetchall():
        ativos_mes[(b.normalize_whitespace(r["seller_name"]), r["mes"])] += int(r["n"])

    chaves = sorted(set(perto) | set(depois), key=lambda k: (k[1], -(perto[k] + depois[k])))
    print(f"\nContatos ATIVOS do mesmo vendedor/cliente/dia, DEPOIS da cotação receptiva")
    print(f"{'Mês':8} {'Vendedor':38} {'≤30min':>7} {'>30min':>7} {'Ativos no mês':>14} {'% suspeito':>11}")
    tot_p = tot_d = 0
    for k in chaves:
        tot = ativos_mes.get(k, 0)
        pct = 100 * perto[k] / tot if tot else 0
        tot_p += perto[k]
        tot_d += depois[k]
        print(f"{k[1]:8} {k[0][:38]:38} {perto[k]:7} {depois[k]:7} {tot:14} {pct:10.1f}%")
    print(f"\nTOTAL: {tot_p} quase certamente o mesmo atendimento (≤{JANELA_MIN} min) · "
          f"{tot_d} possivelmente retorno legítimo (>{JANELA_MIN} min)")
    if exemplos:
        print("\nExemplos (≤30 min):")
        for e in exemplos:
            print(f"  {e[0]} {e[1][:28]:28} {e[2][:30]:30} cotação {e[3]:8} {e[4]} → contato ativo {e[5]} ({e[6]})")


if __name__ == "__main__":
    main()
