"""
Por que esta peça aparece com estoque se a loja não tem?

Uso (venv do CRM):
    /srv/passini/venv/crm/bin/python /srv/passini/apps/crm-comercial/diag_falta_item.py 101487 "ZONA SUL"

POR QUE ESTE DIAGNÓSTICO EXISTE

Relato: a peça 101487 aparece como "Tem na loja" na Zona Sul, com 5 unidades
vindas do código 80539 da mesma família — e a loja não tem nada.

Três explicações possíveis, e elas pedem correções opostas:

  1. O ESTOQUE ESTÁ VELHO. O arquivo de estoque vem do Radar e só muda quando
     alguém importa lá. Se a foto for de semanas atrás, o painel está
     mostrando o saldo de outro dia com cara de saldo de agora. É o pior dos
     três, porque afeta TODAS as linhas, não só esta.
  2. A FAMÍLIA ESTÁ ERRADA. Se 80539 não é substituto de 101487, a regra de
     família está juntando peças diferentes e a ruptura some indevidamente.
  3. O SALDO É REAL MAS INÚTIL — peça reservada, avariada, em outra filial da
     mesma unidade. Aí o dado está certo e a régua é que precisa mudar.

O script mostra a idade de cada fonte e abre a família inteira, para separar
as três. NÃO ALTERA NADA.
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

import backend  # noqa: E402

codigo = (sys.argv[1] if len(sys.argv) > 1 else "101487").strip()
unidade = (sys.argv[2] if len(sys.argv) > 2 else "ZONA SUL").strip().upper()

fconn = backend.faltas_conexao()
if fconn is None:
    print(f"Arquivo de faltas não encontrado em {backend.FALTAS_DB_PATH}")
    sys.exit(1)

print(f"Peça {codigo} · unidade {unidade}\n")

# ── 1. Quando cada fonte foi tirada ─────────────────────────────────────────
print("1) IDADE DE CADA FONTE — a pergunta que vem antes de todas")
meta = {r["chave"]: r["valor"] for r in fconn.execute(
    "SELECT chave, valor FROM faltas_meta")}
print(f"   faltas.db gerado em: {meta.get('gerado_em', '—')}")

for rotulo, caminho in (
    ("solicitação (pedidos)",
     "/srv/passini/apps/radar-rupturas/runtime_data/sources/solicitacao.pkl"),
    ("ESTOQUE", "/srv/passini/apps/radar-rupturas/runtime_data/sources/stock.pkl"),
    ("substitutos (famílias)",
     "/srv/passini/apps/radar-rupturas/runtime_data/sources/substitutos.pkl"),
):
    p = Path(caminho)
    if not p.exists():
        print(f"   {rotulo:<24}— arquivo não encontrado —")
        continue
    quando = datetime.fromtimestamp(p.stat().st_mtime)
    idade = (datetime.now() - quando).days
    alerta = "  << DESATUALIZADO" if idade > 7 else ""
    print(f"   {rotulo:<24}{quando:%d/%m/%Y %H:%M}  ({idade} dia(s)){alerta}")

print("   >> O estoque é uma FOTO do momento da importação no Radar. Se a foto")
print("      for antiga, 'tem na loja' quer dizer 'tinha naquele dia' — e isso")
print("      vale para o painel inteiro, não só para esta peça.")

# ── 2. A família desta peça ─────────────────────────────────────────────────
print(f"\n2) A FAMÍLIA DE {codigo}")
linha = fconn.execute(
    "SELECT DISTINCT familia FROM faltas_resumo WHERE item_code = ?",
    (codigo,)).fetchone()
familia = linha["familia"] if linha else ""
print(f"   FamíliaID: {familia or '— sem família (a peça é a própria família) —'}")

print(f"\n   QUEM TEM SALDO nesta família, em {unidade}:")
print(f"   {'CÓDIGO':<12}{'ESTOQUE':>9}{'ÚLTIMA ENTRADA':>17}   {'ERA PEDIDO?':<12}")
pedidos_codigos = {r["item_code"] for r in fconn.execute(
    "SELECT DISTINCT item_code FROM faltas_resumo WHERE familia = ? AND unidade = ?",
    (familia, unidade))}
achou = False
for r in fconn.execute(
        "SELECT item_code, estoque, ultima_entrada FROM estoque_item"
        " WHERE unidade = ? AND familia = ? ORDER BY estoque DESC",
        (unidade, familia)):
    achou = True
    marca = "sim" if r["item_code"] in pedidos_codigos else "NÃO — substituto"
    print(f"   {r['item_code']:<12}{r['estoque']:>9.0f}{(r['ultima_entrada'] or '—'):>17}   {marca:<12}")
if not achou:
    print("   (nenhum código da família com saldo)")

fam = fconn.execute(
    "SELECT estoque, ultima_entrada FROM estoque_familia"
    " WHERE unidade = ? AND familia = ?", (unidade, familia)).fetchone()
print(f"\n   Saldo somado da família: {fam['estoque'] if fam else '— sem posição —'}")
print("   >> É esse número que vira 'Tem na loja'. Se o saldo está num código")
print("      que NÃO é a peça pedida, a tela precisa deixar isso evidente —")
print("      e é possível que o substituto não sirva para o cliente.")

# ── 3. O que o catálogo do CRM diz dos dois ─────────────────────────────────
print("\n3) AS DUAS PEÇAS SÃO MESMO EQUIVALENTES?")
conn = backend.get_connection()
cid = conn.execute("SELECT id FROM companies LIMIT 1").fetchone()["id"]
codigos = sorted({codigo} | {r["item_code"] for r in fconn.execute(
    "SELECT item_code FROM estoque_item WHERE unidade = ? AND familia = ?",
    (unidade, familia))})
print(f"   {'CÓDIGO':<12}{'TIPO':<22}{'SUBGRUPO':<18}{'DESCRIÇÃO':<28}")
for c in codigos[:10]:
    r = conn.execute(
        "SELECT item_type, item_subgroup, sub_description, manufacturer_ref"
        "  FROM item_catalog WHERE company_id = ? AND item_code = ? LIMIT 1",
        (cid, c)).fetchone()
    if not r:
        print(f"   {c:<12}— fora do catálogo do CRM —")
        continue
    print(f"   {c:<12}{backend.normalize_whitespace(r['item_type'])[:21]:<22}"
          f"{backend.normalize_whitespace(r['item_subgroup'])[:17]:<18}"
          f"{backend.normalize_whitespace(r['sub_description'])[:27]:<28}")
print("   >> Tipo e subgrupo diferentes entre os códigos da mesma família é")
print("      sinal de que o cadastro de substitutos está juntando o que não")
print("      se substitui. Aí o erro é do arquivo de substitutos, não do CRM.")

# ── 4. O estoque conferido contra o próprio catálogo ────────────────────────
print("\n4) O QUE O CADASTRO DO CRM DIZ DO SALDO")
print("   (item_catalog.stock_qty é o saldo da MATRIZ no momento do cadastro —")
print("    serve de referência grosseira, não substitui o estoque do Radar)")
for c in codigos[:10]:
    r = conn.execute(
        "SELECT stock_qty, updated_at FROM item_catalog"
        "  WHERE company_id = ? AND item_code = ? LIMIT 1", (cid, c)).fetchone()
    if r:
        print(f"   {c:<12}saldo matriz {float(r['stock_qty'] or 0):>8.0f}"
              f"   cadastro de {str(r['updated_at'])[:10]}")

# ── 5. Vendeu depois da data do estoque? ────────────────────────────────────
print("\n5) ESSAS PEÇAS VENDERAM DEPOIS DA FOTO DO ESTOQUE?")
p = Path("/srv/passini/apps/radar-rupturas/runtime_data/sources/stock.pkl")
if p.exists():
    corte = datetime.fromtimestamp(p.stat().st_mtime).date().isoformat()
    print(f"   Foto do estoque: {corte}")
    for c in codigos[:10]:
        r = conn.execute(
            "SELECT COUNT(*) n, SUM(quantity) q, MAX(issue_date) ult"
            "  FROM fact_sales_detail WHERE company_id = ? AND item_code = ?"
            "    AND issue_date > ? AND net_value > 0", (cid, c, corte)).fetchone()
        if r and r["n"]:
            print(f"   {c:<12}vendeu {int(r['q'] or 0):>5} peça(s) depois da foto"
                  f"  (última em {r['ult']})")
    print("   >> Venda depois da foto explica saldo que não existe mais. Com a")
    print("      foto de hoje, o problema desaparece sozinho.")

fconn.close()
conn.close()
print("\nNada foi alterado.")
