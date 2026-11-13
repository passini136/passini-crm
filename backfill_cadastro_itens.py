"""
Reconstrói a data de cadastro dos itens a partir dos catálogos já importados.

Uso (venv do CRM):
    # 1) Só mostra o que faria (padrão — não altera nada):
    /srv/passini/venv/crm/bin/python /srv/passini/apps/crm-comercial/backfill_cadastro_itens.py
    # 2) Aplica (faz backup antes):
    /srv/passini/venv/crm/bin/python /srv/passini/apps/crm-comercial/backfill_cadastro_itens.py --aplicar

O PROBLEMA

A importação do catálogo substitui a base inteira. Cada troca regravava todos
os itens com a data daquele dia: em Novidades, tudo aparecia "cadastrado hoje".

A FONTE PARA RECONSTRUIR

Todo catálogo que passou pela importação automática fica guardado em
auto-import/processados/catalogo/. Lendo os arquivos em ordem de data, o
primeiro arquivo em que um código aparece diz quando ele entrou no catálogo
(com a precisão da frequência de importação). O que já estava no PRIMEIRO
arquivo é "base inicial": existia antes, sem data conhecida.

Se o relatório do Alfa trouxer uma coluna de data de cadastro, ela tem
prioridade — é a data real.
"""
import os
import sqlite3
import sys
from collections import Counter
from datetime import date, datetime
from pathlib import Path

sys.path.insert(0, "/srv/passini/apps/crm-comercial")

if not os.environ.get("PASSINI_CRM_DATA"):
    for candidate in ("/srv/passini/data/crm", "/srv/passini/data"):
        if (Path(candidate) / "passini_dashboard.db").exists():
            os.environ["PASSINI_CRM_DATA"] = candidate
            break

import backend as b  # noqa: E402

APLICAR = "--aplicar" in sys.argv


def main() -> None:
    pasta = b.AUTO_IMPORT_BASE / "processados" / "catalogo"
    arquivos = sorted([*pasta.rglob("*.csv"), *pasta.rglob("*.xlsx")], key=lambda p: p.stat().st_mtime)
    print(f"Banco: {b.DB_PATH}")
    print(f"Catálogos guardados em {pasta}: {len(arquivos)}")
    conn = sqlite3.connect(str(b.DB_PATH))
    conn.row_factory = sqlite3.Row
    cid = conn.execute("SELECT id FROM companies LIMIT 1").fetchone()["id"]

    primeiro: dict[str, tuple[str, int]] = {}      # código → (data, base inicial?)
    data_alfa: dict[str, str] = {}
    cabecalho: list[str] = []
    for n, arq in enumerate(arquivos):
        dia = date.fromtimestamp(arq.stat().st_mtime).isoformat()
        try:
            linhas = b.parse_table_bytes(arq.read_bytes(), arq.name)
        except Exception as exc:  # noqa: BLE001
            print(f"  ignorado {arq.name}: {exc}")
            continue
        if linhas and not cabecalho:
            cabecalho = list(linhas[0].keys())
        if linhas and "CODIGO" not in {b.normalize_upper(k) for k in linhas[0].keys()}:
            print(f"  ignorado {arq.name}: não parece catálogo (sem coluna CODIGO)")
            continue
        novos = 0
        for row in linhas:
            codigo = b.unwrap_excel_text(row.get("CODIGO"))
            if not codigo:
                continue
            if codigo not in primeiro:
                primeiro[codigo] = (dia, 1 if n == 0 else 0)
                novos += 1
            dt = b.item_data_cadastro_da_linha(row)
            if dt:
                data_alfa[codigo] = dt
        print(f"  {dia}  {arq.name[:60]:60} {len(linhas):7} linhas · {novos:6} códigos novos")

    if cabecalho:
        tem_data = any(b.normalize_upper(b.strip_accents(c)) in b.ITEM_DATA_CADASTRO_COLUNAS for c in cabecalho)
        print(f"\nColunas do catálogo: {', '.join(cabecalho)}")
        print("Coluna de DATA DE CADASTRO no relatório: "
              + ("SIM — usada como data real." if tem_data else
                 "NÃO. Pedir ao Alfa para incluir; até lá, vale a data em que o código apareceu."))

    hoje = date.today().isoformat()
    atuais = [str(r["item_code"]) for r in conn.execute(
        "SELECT item_code FROM item_catalog WHERE company_id = ?", (cid,)).fetchall()]
    sem_arquivo = [c for c in atuais if c not in primeiro]
    for c in sem_arquivo:
        primeiro[c] = (hoje, 1)

    base = sum(1 for d, bl in primeiro.values() if bl)
    por_mes = Counter(d[:7] for c, (d, bl) in primeiro.items() if not bl)
    print(f"\nItens no catálogo hoje: {len(atuais)} · base inicial (sem data): {base} · "
          f"com data de entrada: {len(primeiro) - base} · com data do Alfa: {len(data_alfa)}")
    for m, n in sorted(por_mes.items()):
        print(f"  entraram em {m}: {n}")
    recentes = sorted(((d, c) for c, (d, bl) in primeiro.items() if not bl), reverse=True)[:15]
    if recentes:
        print("\nMais recentes:")
        for d, c in recentes:
            r = conn.execute("SELECT manufacturer_ref, brand_name FROM item_catalog WHERE company_id = ? "
                             "AND item_code = ?", (cid, c)).fetchone()
            print(f"  {d}  cód. {c:8} {(r['manufacturer_ref'] if r else '') or '':20} {(r['brand_name'] if r else '') or ''}")

    if not APLICAR:
        print("\nNada foi alterado. Para aplicar: acrescente --aplicar ao comando.")
        return

    destino = Path(b.DB_PATH).with_name(
        f"passini_dashboard.antes-cadastro-itens-{datetime.now():%Y%m%d-%H%M%S}.db")
    with sqlite3.connect(str(destino)) as bkp:
        conn.backup(bkp)
    print(f"\nBackup: {destino}")
    b.ensure_item_first_seen(conn)
    conn.execute("DELETE FROM item_first_seen WHERE company_id = ?", (cid,))
    conn.executemany(
        "INSERT INTO item_first_seen (company_id, item_code, first_seen_at, baseline, registered_at) "
        "VALUES (?, ?, ?, ?, ?)",
        [(cid, c, d, bl, data_alfa.get(c)) for c, (d, bl) in primeiro.items()])
    conn.execute(
        "UPDATE item_catalog SET created_at = COALESCE((SELECT COALESCE(f.registered_at, f.first_seen_at) "
        "FROM item_first_seen f WHERE f.company_id = item_catalog.company_id "
        "AND f.item_code = item_catalog.item_code), created_at) WHERE company_id = ?", (cid,))
    conn.commit()
    print(f"Gravado: {len(primeiro)} código(s). Reinicie o CRM.")


if __name__ == "__main__":
    main()
