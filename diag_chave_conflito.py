"""
A chave nova é única? E o estoque tem giro, medido pela chave certa?

Uso:
    /srv/passini/venv/crm/bin/python /srv/passini/apps/crm-comercial/diag_chave_conflito.py

O casamento catálogo x faturamento vai passar a ser
`item_catalog.manufacturer_ref = fact_sales_detail.sku_key`, que casa 99,6% do
valor. Só que manufacturer_ref é a REFERÊNCIA DO FABRICANTE, não um código
interno: nada impede que duas marcas usem "1010" para peças diferentes.

Se isso acontecer, o JOIN casa a venda com o item errado e a tela de Linha
mostra a linha errada — com número bonito e conclusão falsa, que é pior do que
a tela vazia de hoje. Este script mede o conflito e diz se a marca precisa
entrar na chave.

Mede também o giro do estoque pela chave certa: a medição anterior usou a chave
quebrada e devolveu quase zero, o que faria descartar a sugestão de recompra
por um defeito de medição.

Não altera nada.
"""
import os
import sys
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, "/srv/passini/apps/crm-comercial")

if not os.environ.get("PASSINI_CRM_DATA"):
    for candidate in ("/srv/passini/data/crm", "/srv/passini/data"):
        if (Path(candidate) / "passini_dashboard.db").exists():
            os.environ["PASSINI_CRM_DATA"] = candidate
            break

import backend  # noqa: E402

conn = backend.get_connection()
company_id = conn.execute("SELECT id FROM companies LIMIT 1").fetchone()["id"]
competencias = backend.query_competences(conn, company_id)
comp = competencias[0] if competencias else ""
print(f"Banco: {backend.DB_PATH}")
print(f"Competência: {comp}\n")


def ref(v):
    return (v or "").strip().upper()


# ── 1. A referência do fabricante se repete? ─────────────────────────────────
print("1) A CHAVE NOVA É ÚNICA NO CATÁLOGO?")
por_ref: dict[str, list] = defaultdict(list)
for r in conn.execute(
    "SELECT manufacturer_ref, brand_name, item_subgroup, item_group, item_type "
    "FROM item_catalog WHERE company_id = ? AND TRIM(COALESCE(manufacturer_ref,'')) <> ''",
    (company_id,),
).fetchall():
    por_ref[ref(r["manufacturer_ref"])].append(dict(r))

repetidas = {k: v for k, v in por_ref.items() if len(v) > 1}
print(f"   {len(por_ref)} referência(s) distinta(s) · {len(repetidas)} usada(s) por mais de um item")

# O que importa não é repetir: é repetir apontando para LINHAS diferentes.
conflito_linha = {
    k: v for k, v in repetidas.items()
    if len({(x["item_subgroup"] or "").strip().upper() for x in v}) > 1
}
conflito_marca = {k: v for k, v in repetidas.items()
                  if len({(x["brand_name"] or "").strip().upper() for x in v}) > 1}
print(f"   {len(conflito_marca)} referência(s) compartilhada(s) por MARCAS diferentes")
print(f"   {len(conflito_linha)} referência(s) que apontam para LINHAS diferentes  << o que estraga")

if conflito_linha:
    print("\n   Exemplos do conflito que importa:")
    for k, v in list(conflito_linha.items())[:6]:
        print(f"      {k}")
        for x in v[:4]:
            print(f"         {(x['brand_name'] or '—')[:18]:<20}"
                  f"{(x['item_subgroup'] or '—')[:26]:<28}{(x['item_type'] or '—')[:22]}")

# ── 2. Quanto do faturamento cai numa referência ambígua ─────────────────────
print("\n2) QUANTO DO MÊS CAI NUMA REFERÊNCIA AMBÍGUA")
total = ambiguo = 0.0
linhas_amb = 0
for r in conn.execute(
    "SELECT sku_key, brand_name, net_value FROM fact_sales_detail "
    "WHERE company_id = ? AND competence = ?", (company_id, comp)).fetchall():
    v = float(r["net_value"] or 0)
    total += v
    if ref(r["sku_key"]) in conflito_linha:
        ambiguo += v
        linhas_amb += 1
pct = 100 * ambiguo / total if total else 0
print(f"   {linhas_amb} linha(s) · {backend.brl(ambiguo)} ({pct:.1f}% do mês) casariam com mais")
print("   de uma linha de produto.")

# ── 3. A marca resolve o empate? ─────────────────────────────────────────────
print("\n3) INCLUIR A MARCA NA CHAVE RESOLVE?")
por_ref_marca: dict[tuple, set] = defaultdict(set)
for k, v in por_ref.items():
    for x in v:
        por_ref_marca[(k, (x["brand_name"] or "").strip().upper())].add(
            (x["item_subgroup"] or "").strip().upper())
resta = {k for k, linhas in por_ref_marca.items() if len(linhas) > 1}
print(f"   Com (referência + marca): {len(resta)} par(es) ainda ambíguo(s), de {len(por_ref_marca)}.")
if pct < 0.5:
    print("   >> O conflito é irrelevante no faturamento real. Pode juntar só pela")
    print("      referência; incluir a marca é preciosismo que não muda número.")
elif len(resta) < len(conflito_linha) / 2:
    print("   >> A marca resolve a maior parte. Vale incluí-la no JOIN.")
else:
    print("   >> Nem com a marca. Cuidado: parte da tela de Linha vai mentir.")

# ── 4. O estoque tem giro, medido pela chave certa ───────────────────────────
print("\n4) GIRO DO ESTOQUE — AGORA PELA CHAVE CERTA")
print("   (estoque → catálogo pelo código interno → referência → faturamento)")
interno_para_ref = {
    (r["item_code"] or "").strip(): ref(r["manufacturer_ref"])
    for r in conn.execute(
        "SELECT item_code, manufacturer_ref FROM item_catalog WHERE company_id = ?",
        (company_id,)).fetchall()
    if (r["item_code"] or "").strip()
}
tres = competencias[:3]
marcadores = ",".join("?" for _ in tres) or "''"
vendidos = {
    ref(r[0]) for r in conn.execute(
        f"SELECT DISTINCT sku_key FROM fact_sales_detail "
        f"WHERE company_id = ? AND competence IN ({marcadores}) AND net_value > 0",
        (company_id, *tres)).fetchall() if ref(r[0])
} if tres else set()
print(f"   {len(interno_para_ref)} itens do catálogo com referência · "
      f"{len(vendidos)} referência(s) vendida(s) em {', '.join(tres) or '—'}\n")
print(f"   {'UNIDADE':<16}{'COM SALDO':>11}{'VENDEU 3M':>11}{'% GIRO':>9}{'PARADO':>9}")
for u in conn.execute("SELECT DISTINCT unit_name FROM item_stock WHERE company_id = ? "
                      "ORDER BY unit_name", (company_id,)).fetchall():
    com_saldo = vendeu = 0
    for r in conn.execute(
        "SELECT item_code, quantity FROM item_stock WHERE company_id = ? AND unit_name = ? "
        "AND quantity > 0", (company_id, u["unit_name"])).fetchall():
        com_saldo += 1
        if interno_para_ref.get((r["item_code"] or "").strip()) in vendidos:
            vendeu += 1
    giro = 100 * vendeu / com_saldo if com_saldo else 0
    print(f"   {u['unit_name'][:15]:<16}{com_saldo:>11}{vendeu:>11}{giro:>8.1f}%"
          f"{com_saldo - vendeu:>9}")
print("\n   Agora sim: se o giro passar de 20%, há massa para a sugestão de recompra.")

conn.close()
