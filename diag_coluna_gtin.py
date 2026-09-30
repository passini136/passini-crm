"""
O GTIN da coluna E está chegando no banco?

Uso:
    /srv/passini/venv/crm/bin/python /srv/passini/apps/crm-comercial/diag_coluna_gtin.py
    /srv/passini/venv/crm/bin/python /srv/passini/apps/crm-comercial/diag_coluna_gtin.py /caminho/arquivo.csv

A diretoria informou que o GTIN está na coluna E do faturamento detalhado, entre
Cidade e Marca, e que é ele — não a referência do fabricante — que separa a
caixa do litro nos lubrificantes.

O importador JÁ tenta ler essa coluna: `row.get("")`, porque o cabeçalho dela
vem em branco. Mesmo assim `gtin_value` está vazio no banco. A suspeita é
mecânica: `csv.DictReader` usa o cabeçalho como chave de dicionário, e quando
DUAS colunas têm o mesmo nome — duas colunas sem título, por exemplo — a última
sobrescreve a primeira. O código pediria a coluna E e receberia outra, vazia.

Este diagnóstico não conserta nada: ele mostra o cabeçalho cru, o que o leitor
entrega, e o que existe no banco. Sem os três lado a lado, qualquer correção
seria chute — e já troquei uma chave de item por chute neste projeto.

Não altera nada.
"""
import csv
import io
import os
import sys
from pathlib import Path

sys.path.insert(0, "/srv/passini/apps/crm-comercial")

if not os.environ.get("PASSINI_CRM_DATA"):
    for candidate in ("/srv/passini/data/crm", "/srv/passini/data"):
        if (Path(candidate) / "passini_dashboard.db").exists():
            os.environ["PASSINI_CRM_DATA"] = candidate
            break

import backend  # noqa: E402


def letra(i: int) -> str:
    """Índice 0 → 'A', para falar a mesma língua da planilha."""
    s = ""
    i += 1
    while i:
        i, r = divmod(i - 1, 26)
        s = chr(65 + r) + s
    return s


# ── Achar o arquivo ─────────────────────────────────────────────────────────
alvo = Path(sys.argv[1]) if len(sys.argv) > 1 else None
if not alvo:
    candidatos = []
    for base in (getattr(backend, "AUTO_IMPORT_BASE", None),
                 Path("/srv/passini/data/auto-import"),
                 Path("/srv/passini/auto-import")):
        if base and Path(base).exists():
            candidatos += list(Path(base).rglob("*.csv"))
    fat = [p for p in candidatos if "faturamento" in str(p).lower()
           and "consolidado" not in str(p).lower()]
    alvo = max(fat, key=lambda p: p.stat().st_mtime) if fat else None

print(f"Banco: {backend.DB_PATH}")
if not alvo or not alvo.exists():
    print("\nNenhum arquivo de faturamento detalhado encontrado.")
    print("Passe o caminho: diag_coluna_gtin.py /srv/.../auto-import/faturamento/arquivo.csv")
else:
    print(f"Arquivo: {alvo}\n")
    bruto = alvo.read_bytes()
    texto = None
    for cod in ("utf-8-sig", "latin-1"):
        try:
            texto = bruto.decode(cod)
            print(f"Codificação: {cod}")
            break
        except UnicodeDecodeError:
            continue

    linhas = texto.splitlines()
    cabecalho = linhas[0].split(";")

    # ── 1. O cabeçalho cru ──────────────────────────────────────────────────
    print("\n1) CABEÇALHO DO ARQUIVO")
    print(f"   {'COL':<5}{'NOME DO CABEÇALHO':<28}EXEMPLO DA 1a LINHA")
    exemplo = linhas[1].split(";") if len(linhas) > 1 else []
    vazios = []
    for i, nome in enumerate(cabecalho):
        n = nome.strip()
        if not n:
            vazios.append(i)
        val = exemplo[i].strip() if i < len(exemplo) else ""
        marca = "  ← SEM NOME" if not n else ""
        print(f"   {letra(i):<5}{(n or '(vazio)')[:27]:<28}{val[:24]}{marca}")

    # ── 2. O leitor perde alguma coluna? ────────────────────────────────────
    print("\n2) O LEITOR CONSEGUE PEGAR A COLUNA E?")
    nomes = [c.strip() for c in cabecalho]
    repetidos = {n for n in nomes if nomes.count(n) > 1}
    print(f"   Colunas sem nome: {len(vazios)} "
          f"({', '.join(letra(i) for i in vazios) if vazios else '—'})")
    if repetidos:
        print(f"   Nomes REPETIDOS: {', '.join(repr(n) for n in sorted(repetidos))}")
    print("   csv.DictReader usa o cabeçalho como chave: com nome repetido, a")
    print("   ÚLTIMA coluna sobrescreve as anteriores.")

    reader = csv.DictReader(io.StringIO(texto, newline=""), delimiter=";")
    primeira = next(reader, None)
    if primeira is not None:
        lido = primeira.get("")
        idx_e = 4
        cru_e = exemplo[idx_e].strip() if len(exemplo) > idx_e else ""
        print(f"\n   Coluna E no arquivo:        {cru_e!r}")
        print(f"   row.get('') devolve:        {lido!r}")
        if str(lido or "").strip() == cru_e and cru_e:
            print("   >> O leitor PEGA a coluna certa. O problema não é aqui.")
        else:
            print("   >> O leitor NÃO entrega a coluna E. É por isso que o GTIN")
            print("      chega vazio no banco, mesmo o código pedindo por ela.")
            print("      Correção: ler por POSIÇÃO (índice 4), não por nome.")
        # Mostra o que o dicionário tem sob chaves suspeitas
        for chave in ("", None):
            if chave in primeira:
                print(f"   chave {chave!r}: {primeira[chave]!r}")

# ── 3. O que existe no banco ────────────────────────────────────────────────
conn = backend.get_connection()
company_id = conn.execute("SELECT id FROM companies LIMIT 1").fetchone()["id"]
comp = backend.crm_latest_competence(conn, company_id)
print(f"\n3) GTIN NO BANCO — competência {comp}")
r = conn.execute(
    """SELECT COUNT(*) n,
              SUM(CASE WHEN TRIM(COALESCE(gtin_value,'')) <> '' THEN 1 ELSE 0 END) com
       FROM fact_sales_detail WHERE company_id = ? AND competence = ?""",
    (company_id, comp)).fetchone()
print(f"   {r['com']:,} de {r['n']:,} linha(s) com gtin_value "
      f"({100 * r['com'] / r['n'] if r['n'] else 0:.1f}%)")
if r["com"]:
    print("   Amostra:")
    for x in conn.execute(
        "SELECT gtin_value, sku_key, brand_name, manufacturer_sku FROM fact_sales_detail "
        "WHERE company_id = ? AND competence = ? AND TRIM(COALESCE(gtin_value,'')) <> '' "
        "LIMIT 5", (company_id, comp)).fetchall():
        print(f"      gtin={x['gtin_value']!r}  sku_key={x['sku_key']!r}  "
              f"marca={x['brand_name']!r}  fabricante={x['manufacturer_sku']!r}")

# ── 4. O catálogo tem essa mesma chave? ─────────────────────────────────────
print("\n4) O CATÁLOGO CASA COM ESSA CHAVE?")
rc = conn.execute(
    "SELECT COUNT(*) n, "
    "SUM(CASE WHEN TRIM(COALESCE(gtin,'')) <> '' THEN 1 ELSE 0 END) com_gtin, "
    "SUM(CASE WHEN TRIM(COALESCE(item_code,'')) <> '' THEN 1 ELSE 0 END) com_code "
    "FROM item_catalog WHERE company_id = ?", (company_id,)).fetchone()
print(f"   Catálogo: {rc['n']:,} item(ns) · {rc['com_gtin']:,} com GTIN · "
      f"{rc['com_code']:,} com código interno")
print("   Amostra do catálogo:")
for x in conn.execute(
    "SELECT item_code, gtin, manufacturer_ref, brand_name, unit_of_measure, cost_price "
    "FROM item_catalog WHERE company_id = ? AND UPPER(TRIM(COALESCE(brand_name,''))) = 'MAXON' "
    "ORDER BY manufacturer_ref LIMIT 8", (company_id,)).fetchall():
    print(f"      code={x['item_code']!r} gtin={x['gtin']!r} ref={x['manufacturer_ref']!r} "
          f"un={x['unit_of_measure']!r} custo={x['cost_price']}")
print("\n   >> Comparar a amostra do item 3 com esta: a coluna do faturamento")
print("      precisa casar com ALGUMA coluna do catálogo. Se o valor da coluna E")
print("      (ex.: 68177) parecer código interno e não EAN de 13 dígitos, a")
print("      junção certa é item_code, não gtin.")

conn.close()
