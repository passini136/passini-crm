"""
Oportunidade de mix: o que a unidade vende e o vendedor não.

Uso:
    /srv/passini/venv/crm/bin/python /srv/passini/apps/crm-comercial/diag_mix.py MATRIZ
    /srv/passini/venv/crm/bin/python /srv/passini/apps/crm-comercial/diag_mix.py XANGRILA

A ideia é a peça-isca: item de giro alto e preço acessível que muita oficina
compra. O vendedor que não oferece uma dessas não está perdendo uma venda
grande — está deixando de ter motivo para ligar.

Antes de virar tela, três coisas precisam ser conferidas na mão:

  1. a régua de "ticket baixo" é por LINHA, não em reais fixos. Óleo e
     embreagem têm patamares diferentes, e um teto único reprovaria toda a
     embreagem sem dizer nada sobre nenhuma das duas;
  2. os itens sugeridos precisam fazer sentido para quem conhece a loja;
  3. a lista por vendedor não pode ser a mesma para todos — se for, ela não
     está olhando o que cada um vende.

Não altera nada.
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

conn = backend.get_connection()
company_id = conn.execute("SELECT id FROM companies LIMIT 1").fetchone()["id"]
unidade = " ".join(a for a in sys.argv[1:] if not a.startswith("-")).strip().upper() or "MATRIZ"

inicio = time.time()
d = backend.mix_opportunities(conn, company_id, unidade)
seg = time.time() - inicio

print(f"Banco: {backend.DB_PATH}")
print(f"Unidade: {d['unitName']}  ·  janela: {', '.join(d['window'])}  ·  {seg:.2f}s\n")
print("Régua:")
print(f"   mínimo de clientes distintos: {backend.MIX_MIN_CLIENTS}")
print("   ticket: preço unitário do item ABAIXO da média da linha dele")
print(f"   top por vendedor: {backend.MIX_TOP_PER_SELLER}\n")

if not d["items"]:
    print("Nenhum item elegível. Confira se a unidade tem vendedores mapeados.")
    conn.close()
    raise SystemExit(0)

# ── 1. Os itens-isca da unidade ──────────────────────────────────────────────
print("1) OS ITENS-ISCA DA UNIDADE (top 15 por frequência)")
print(f"   {'REFERÊNCIA':<16}{'MARCA':<14}{'LINHA':<18}{'CLI':>5}{'QTD':>8}"
      f"{'PREÇO':>11}{'MÉDIA LINHA':>13}  LOJA")
for i in d["items"][:15]:
    loja = "—" if i["inStock"] is None else ("tem" if i["inStock"] else "SEM")
    print(f"   {i['ref'][:15]:<16}{i['brand'][:13]:<14}{i['line'][:17]:<18}"
          f"{i['clients']:>5}{int(i['quantity']):>8}"
          f"{backend.brl(i['unitPrice']):>11}{backend.brl(i['linePrice']):>13}  {loja}")

# ── 2. Por vendedor ──────────────────────────────────────────────────────────
print(f"\n2) POR VENDEDOR ({len(d['sellers'])} vendedor(es) na unidade)")
assinaturas = {}
for vendedor in d["sellers"]:
    sug = d["bySeller"].get(vendedor) or []
    nunca = sum(1 for s in sug if s["status"] == "NUNCA")
    parou = sum(1 for s in sug if s["status"] == "PAROU")
    assinaturas[vendedor] = tuple(s["ref"] for s in sug)
    print(f"\n   {vendedor}  —  {len(sug)} sugestão(ões) · {nunca} nunca vendeu · {parou} parou")
    for s in sug[:6]:
        etiqueta = "nunca vendeu" if s["status"] == "NUNCA" else "PAROU de vender"
        loja = "" if s["inStock"] is None else ("" if s["inStock"] else " · SEM SALDO")
        print(f"      {s['ref'][:14]:<16}{s['brand'][:12]:<14}{s['line'][:16]:<18}"
              f"{s['clients']:>4} cli · {backend.brl(s['unitPrice']):>10} · {etiqueta}{loja}")

# ── 3. As listas são diferentes entre si? ────────────────────────────────────
print("\n3) AS LISTAS SÃO PERSONALIZADAS?")
unicas = len(set(assinaturas.values()))
print(f"   {unicas} lista(s) distinta(s) para {len(assinaturas)} vendedor(es)")
if unicas <= 1 and len(assinaturas) > 1:
    print("   >> TODOS recebem a mesma lista. O cálculo não está olhando o que cada")
    print("      um vende — a sugestão vira cartaz, não orientação.")
elif unicas < len(assinaturas) / 2:
    print("   >> Muita repetição entre vendedores. Vale conferir se o mapeamento")
    print("      vendedor x unidade está certo.")
else:
    print("   Listas majoritariamente distintas — cada um recebe o próprio recorte.")

# ── 4. A lacuna entre unidades ───────────────────────────────────────────────
print(f"\n4) O QUE OUTRAS UNIDADES VENDEM E {d['unitName']} NÃO ({len(d['unitGap'])} itens)")
if d["unitGap"]:
    print(f"   {'REFERÊNCIA':<16}{'MARCA':<14}{'LINHA':<18}{'CLI':>5}{'QTD':>8}{'PREÇO':>11}  LOJA")
    for i in d["unitGap"][:15]:
        loja = "—" if i["inStock"] is None else ("tem" if i["inStock"] else "SEM")
        print(f"   {i['ref'][:15]:<16}{i['brand'][:13]:<14}{i['line'][:17]:<18}"
              f"{i['clients']:>5}{int(i['quantity']):>8}{backend.brl(i['unitPrice']):>11}  {loja}")
    tem = sum(1 for i in d["unitGap"] if i["inStock"])
    print(f"\n   {tem} de {len(d['unitGap'])} já têm saldo na loja — esses dão para oferecer hoje.")
    print("   Os demais são conversa de compra, não de venda.")
else:
    print("   Nenhuma lacuna: a unidade vende tudo o que as outras vendem.")

conn.close()
