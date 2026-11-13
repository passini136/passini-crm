"""
Reclassifica como RECEPTIVO os contatos ATIVOS criados SOZINHOS pela cotação.

Uso (venv do CRM):
    # 1) Só mostra o que faria (padrão — não altera nada):
    /srv/passini/venv/crm/bin/python /srv/passini/apps/crm-comercial/corrigir_ligacao_cotacao.py
    # 2) Aplica (faz backup antes):
    /srv/passini/venv/crm/bin/python /srv/passini/apps/crm-comercial/corrigir_ligacao_cotacao.py --aplicar

O QUE ACONTECIA

Cotação de cliente SEM cadastro cria uma prospecção com a observação
"Criado a partir de uma cotação do dia.". O cadastro de prospecção, quando
tem observação e é feito pelo próprio vendedor, registra a observação como
LIGAÇÃO ATIVA — feito para a prospecção de verdade, em que o vendedor acabou
de ligar. Na cotação, quem ligou foi o cliente: o vendedor ganhava um contato
ativo no mesmo minuto da cotação, sem ter feito nada. O diagnóstico de
13/11/2026 achou 45 casos assim (quase todos na Zona Norte).

O QUE ESTE SCRIPT MUDA — E SÓ ISSO

Contato ATIVO cuja observação é EXATAMENTE o texto que o sistema grava, num
prospect que tem cotação RECEPTIVA (telefone/WhatsApp) com a mesma chave. Nada
é apagado e nada é escolhido "por semelhança": a marca é o texto fixo gerado
pelo código. O contato vira "Ligação recebida"/"Mensagem recebida", RECEPTIVO,
origem "Cotação recebida", e a cotação passa a apontar para ele (o desfecho
futuro atualiza a mesma linha em vez de criar outra).
"""
import os
import sqlite3
import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, "/srv/passini/apps/crm-comercial")

if not os.environ.get("PASSINI_CRM_DATA"):
    for candidate in ("/srv/passini/data/crm", "/srv/passini/data"):
        if (Path(candidate) / "passini_dashboard.db").exists():
            os.environ["PASSINI_CRM_DATA"] = candidate
            break

import backend as b  # noqa: E402

MARCA = "Criado a partir de uma cotação do dia."
APLICAR = "--aplicar" in sys.argv


def main() -> None:
    conn = sqlite3.connect(str(b.DB_PATH))
    conn.row_factory = sqlite3.Row
    casos = conn.execute(
        """
        SELECT i.id AS iid, i.client_key, i.client_name, i.seller_name, i.occurred_at,
               q.id AS qid, q.channel, q.interaction_id
        FROM crm_interactions i
        JOIN crm_quotes q ON q.company_id = i.company_id AND q.client_key = i.client_key
                         AND q.initiative = 'RECEPTIVO' AND q.channel IN ('TELEFONE','WHATSAPP')
        WHERE i.initiative = 'ATIVO' AND TRIM(i.notes) = ? AND i.client_key LIKE 'P-%'
        ORDER BY i.occurred_at
        """, (MARCA,)).fetchall()
    # Uma cotação por contato (a primeira daquela chave).
    vistos: dict[int, sqlite3.Row] = {}
    for c in casos:
        vistos.setdefault(c["iid"], c)
    casos = list(vistos.values())

    print(f"Banco: {b.DB_PATH}")
    print(f"Contatos ATIVOS gerados pela cotação: {len(casos)}")
    por_vendedor: dict[tuple[str, str], int] = {}
    for c in casos:
        k = (b.normalize_whitespace(c["seller_name"]), (c["occurred_at"] or "")[:7])
        por_vendedor[k] = por_vendedor.get(k, 0) + 1
    for (v, m), n in sorted(por_vendedor.items(), key=lambda x: (x[0][1], -x[1])):
        print(f"  {m}  {v[:40]:40} {n:4}")
    if not casos:
        return
    if not APLICAR:
        print("\nNada foi alterado. Para aplicar: acrescente --aplicar ao comando.")
        return

    destino = Path(b.DB_PATH).with_name(
        f"passini_dashboard.antes-corrigir-cotacao-{datetime.now():%Y%m%d-%H%M%S}.db")
    with sqlite3.connect(str(destino)) as bkp:
        conn.backup(bkp)       # WAL: copiar o arquivo daria backup incompleto
    print(f"\nBackup: {destino}")

    tipo = {"TELEFONE": "LIGACAO_RECEBIDA", "WHATSAPP": "MENSAGEM_RECEBIDA"}
    for c in casos:
        conn.execute(
            "UPDATE crm_interactions SET initiative = 'RECEPTIVO', contact_type_code = ?, "
            "result_code = 'OUTRO', origin = 'COTACAO', "
            "notes = 'Cliente pediu cotação (cliente sem cadastro, registrado na tela Cotações). "
            "Reclassificado de ativo para receptivo em ' || date('now') || '.' "
            "WHERE id = ?", (tipo[c["channel"]], c["iid"]))
        if not c["interaction_id"]:
            conn.execute("UPDATE crm_quotes SET interaction_id = ? WHERE id = ?", (c["iid"], c["qid"]))
    conn.commit()
    print(f"Reclassificados: {len(casos)}. Reinicie o CRM para o placar recalcular.")


if __name__ == "__main__":
    main()
