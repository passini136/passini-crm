"""
O CRM enxerga as faltas do Radar, e elas apontam para peça que vende?

Uso (venv do CRM):
    /srv/passini/venv/crm/bin/python /srv/passini/apps/crm-comercial/diag_faltas.py

POR QUE ESTE DIAGNÓSTICO EXISTE

O arquivo de faltas foi gerado fora do CRM, por um script que roda com outro
python, lendo um pickle de outro sistema. Entre "o arquivo existe" e "a tela
mostra a informação certa" há três coisas que podem falhar em silêncio:

  1. O CRM não acha o arquivo (caminho diferente do que o exportador usou) —
     e, como ausência não vira erro de propósito, a tela simplesmente não
     mostra faltas. Ninguém reclama de algo que nunca apareceu.
  2. O código casa, mas aponta para peça errada. Número bate por acaso e a
     tela fica confiável e errada, que é o pior desfecho.
  3. O arquivo envelhece. "Nenhuma falta" num arquivo de três meses atrás é
     uma afirmação diferente de "nenhuma falta" num arquivo de ontem.

Este diagnóstico testa os três, com peças REAIS: pega as mais pedidas no
Radar, procura cada uma no catálogo do CRM e confere se a descrição bate.

NÃO ALTERA NADA.
"""
import os
import sys
import time
from pathlib import Path

sys.path.insert(0, "/srv/passini/apps/crm-comercial")

if not os.environ.get("PASSINI_CRM_DATA"):
    for candidate in ("/srv/passini/data/crm", "/srv/passini/data"):
        if (Path(candidate) / "passini_dashboard.db").exists():
            os.environ["PASSINI_CRM_DATA"] = candidate
            break

import backend  # noqa: E402

print(f"Banco do CRM:     {backend.DB_PATH}")
print(f"Arquivo de faltas: {backend.FALTAS_DB_PATH}\n")

# ── 1. O CRM acha o arquivo? ────────────────────────────────────────────────
print("1) O CRM ENCONTRA O ARQUIVO?")
status = backend.faltas_status()
if not status.get("disponivel"):
    print("   >> NÃO. O CRM procura em:")
    print(f"      {backend.FALTAS_DB_PATH}")
    print("      O exportador gravou em outro lugar, ou ainda não rodou.")
    print("      Rode: /srv/passini/venv/radar/bin/python "
          "/srv/passini/apps/crm-comercial/exportar_faltas.py")
    sys.exit(1)
print(f"   Gerado em:  {status['geradoEm']}")
print(f"   Período:    {status['competenciaMin']} a {status['competenciaMax']}")
print(f"   Linhas:     {status['linhas']:,}")

# Arquivo velho não é erro, mas quem decide precisa saber.
import datetime  # noqa: E402
try:
    gerado = datetime.datetime.strptime(status["geradoEm"], "%Y-%m-%d %H:%M:%S")
    dias = (datetime.datetime.now() - gerado).days
    print(f"   Idade:      {dias} dia(s)")
    if dias > 40:
        print("   >> MAIS DE 40 DIAS. A tela vai mostrar falta antiga como se")
        print("      fosse a situação de hoje. Rode o exportador de novo.")
except Exception:  # noqa: BLE001
    print("   (não consegui ler a data de geração)")

conn = backend.get_connection()
company_id = conn.execute("SELECT id FROM companies LIMIT 1").fetchone()["id"]

# ── 2. As peças mais pedidas existem no catálogo? ───────────────────────────
print("\n2) AS PEÇAS MAIS PEDIDAS SÃO PEÇAS DE VERDADE?")
fconn = backend.faltas_conexao()
top = fconn.execute(
    "SELECT item_code, SUM(pedidos) p, MAX(item) item, MAX(fabricante) fab,"
    "       COUNT(DISTINCT unidade) unid"
    "  FROM faltas_resumo GROUP BY item_code ORDER BY p DESC LIMIT 12").fetchall()
print(f"   {'CÓDIGO':<12}{'PEDIDOS':>9}{'UN':>4}  {'RADAR DIZ':<22}{'CATÁLOGO DIZ':<22}{'':<4}")
discordam = ausentes = 0
for r in top:
    cat = conn.execute(
        "SELECT item_type, sub_description, manufacturer_ref, brand_name, sale_price"
        "  FROM item_catalog WHERE company_id = ? AND item_code = ? LIMIT 1",
        (company_id, r["item_code"])).fetchone()
    radar = backend.normalize_whitespace(f"{r['item'] or ''} {r['fab'] or ''}")[:21]
    if not cat:
        ausentes += 1
        print(f"   {r['item_code'][:11]:<12}{r['p']:>9,}{r['unid']:>4}  {radar:<22}"
              f"{'— não existe —':<22}← ")
        continue
    catalogo = backend.normalize_whitespace(
        f"{cat['item_type'] or ''} {cat['manufacturer_ref'] or ''}")[:21]
    bate = (backend.normalize_whitespace(r["fab"]).upper()
            == backend.normalize_whitespace(cat["manufacturer_ref"]).upper())
    if not bate:
        discordam += 1
    print(f"   {r['item_code'][:11]:<12}{r['p']:>9,}{r['unid']:>4}  {radar:<22}"
          f"{catalogo:<22}{'' if bate else '← fabricante diverge'}")
print(f"\n   {ausentes} fora do catálogo · {discordam} com fabricante diferente")
print("   >> Fora do catálogo é peça que o Radar conhece e o CRM não: a tela")
print("      mostraria um código sem nome. Fabricante diferente pode ser")
print("      cadastro atualizado — a tela sempre exibe o do CRM, que manda.")

# ── 3. A consulta que a tela vai usar funciona e é rápida? ──────────────────
print("\n3) A CONSULTA DA TELA")
print(f"   {'CÓDIGO':<12}{'PEDIDOS':>9}{'UNIDADES':>10}{'MESES':>7}{'ÚLTIMA':>12}{'TEMPO':>8}")
for r in top[:5]:
    t0 = time.time()
    f = backend.faltas_por_item({r["item_code"]}, meses=12)
    seg = time.time() - t0
    print(f"   {r['item_code'][:11]:<12}{f['pedidos']:>9,}{len(f['porUnidade']):>10}"
          f"{len(f['porMes']):>7}{f['ultimaData'] or '—':>12}{seg:>7.2f}s")
print("   >> Acima de 1s a busca da carteira fica desconfortável: o gerente")
print("      digita o código e acha que travou.")

# ── 4. Falta de peça que a casa vende — o que interessa ─────────────────────
print("\n4) FALTA DE PEÇA COM DEMANDA COMPROVADA")
t0 = time.time()
vendidas = {backend.normalize_whitespace(r["item_code"]).upper()
            for r in conn.execute(
                "SELECT DISTINCT item_code FROM fact_sales_detail"
                " WHERE company_id = ? AND TRIM(COALESCE(item_code,'')) <> ''",
                (company_id,))} - {""}
comp_ini = backend.shift_competence(status["competenciaMax"], -11)
faltaram = {backend.normalize_whitespace(r["item_code"]).upper(): r["p"]
            for r in fconn.execute(
                "SELECT item_code, SUM(pedidos) p FROM faltas_resumo"
                " WHERE competencia >= ? GROUP BY item_code", (comp_ini,))}
cruz = {c: n for c, n in faltaram.items() if c in vendidas}
print(f"   Apurado em {time.time() - t0:.1f}s · janela {comp_ini} a {status['competenciaMax']}")
print(f"   Peças que a Passini vende:        {len(vendidas):,}")
print(f"   Peças com falta na janela:        {len(faltaram):,}")
print(f"   VENDEM e FALTARAM:                {len(cruz):,} "
      f"({100 * len(cruz) / max(1, len(vendidas)):.1f}% do que se vende)")
print(f"   Pedidos dessas peças:             {sum(cruz.values()):,}")

if cruz:
    print("\n   AS 8 MAIORES — peça que vende e faltou:")
    print(f"   {'CÓDIGO':<12}{'PEDIDOS':>9}  {'PEÇA':<26}{'CLIENTES 12M':>13}")
    for codigo, n in sorted(cruz.items(), key=lambda x: -x[1])[:8]:
        cat = conn.execute(
            "SELECT item_type, manufacturer_ref FROM item_catalog"
            "  WHERE company_id = ? AND item_code = ? LIMIT 1",
            (company_id, codigo)).fetchone()
        nome = backend.normalize_whitespace(
            f"{cat['item_type'] or ''} {cat['manufacturer_ref'] or ''}")[:25] if cat else "—"
        clientes = conn.execute(
            "SELECT COUNT(DISTINCT client_name) n FROM fact_sales_detail"
            "  WHERE company_id = ? AND UPPER(item_code) = ? AND net_value > 0",
            (company_id, codigo)).fetchone()["n"]
        print(f"   {codigo[:11]:<12}{n:>9,}  {nome:<26}{clientes:>13,}")
    print("\n   >> Peça com muitos pedidos de compra E muitos clientes é venda")
    print("      que a loja já perdeu mais de uma vez. É por onde a tela começa.")

fconn.close()
conn.close()
print("\nNada foi alterado.")
