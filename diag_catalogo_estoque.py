"""
O catálogo casa com o faturamento? O estoque tem massa para sugerir recompra?

Uso:
    /srv/passini/venv/crm/bin/python /srv/passini/apps/crm-comercial/diag_catalogo_estoque.py

Duas perguntas antes de investir em qualquer coisa que dependa desses arquivos:

  1. A tela de Linha/Grupo junta catálogo e faturamento por uma chave. Se a
     chave errar, a tela mostra MENOS do que existe e não avisa — parece que a
     linha vendeu pouco, quando na verdade o item não foi encontrado. O script
     testa a chave em uso e as alternativas, para saber se há chave melhor.
  2. A posição de estoque hoje não é lida por nada. Antes de construir a
     sugestão de recompra em cima dela, vale saber se ela tem giro de verdade.

Não altera nada.
"""
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

conn = backend.get_connection()
company_id = conn.execute("SELECT id FROM companies LIMIT 1").fetchone()["id"]
competencias = backend.query_competences(conn, company_id)
comp = competencias[0] if competencias else ""
print(f"Banco: {backend.DB_PATH}")
print(f"Competência de referência: {comp or '—'}\n")


def um(sql, params=()):
    return conn.execute(sql, params).fetchone()


# ── 1. Tamanho das bases ─────────────────────────────────────────────────────
print("1) O QUE ESTÁ IMPORTADO")
cat = um("SELECT COUNT(*) n, MAX(updated_at) quando FROM item_catalog WHERE company_id = ?",
         (company_id,))
est = um("SELECT COUNT(*) n, COUNT(DISTINCT item_code) itens, COUNT(DISTINCT unit_name) unidades, "
         "MAX(updated_at) quando FROM item_stock WHERE company_id = ?", (company_id,))
print(f"   catálogo: {cat['n']:>8} itens   · atualizado {str(cat['quando'] or '—')[:16]}")
print(f"   estoque.: {est['n']:>8} linhas  · {est['itens']} itens em {est['unidades']} unidade(s)"
      f" · atualizado {str(est['quando'] or '—')[:16]}")
if not cat["n"]:
    print("\n   Sem catálogo importado. As perguntas abaixo não se aplicam.")
    conn.close()
    raise SystemExit(0)

# ── 2. A chave de casamento ──────────────────────────────────────────────────
print("\n2) O CASAMENTO CATÁLOGO x FATURAMENTO")
print("   A tela de Linha/Grupo usa item_code = gtin_value. As outras colunas do")
print("   faturamento entram aqui como alternativa, para ver se existe chave melhor.\n")
print(f"   {'CHAVE DO FATURAMENTO':<26}{'LINHAS':>10}{'% LINHAS':>10}{'VALOR CASADO':>18}{'% VALOR':>9}")

total = um("SELECT COUNT(*) n, COALESCE(SUM(net_value),0) v FROM fact_sales_detail "
           "WHERE company_id = ? AND competence = ?", (company_id, comp))
melhor = ("", 0.0)
for rotulo, coluna in (("gtin_value (em uso)", "f.gtin_value"),
                       ("manufacturer_sku", "f.manufacturer_sku"),
                       ("sku_key", "f.sku_key")):
    r = um(f"""
        SELECT COUNT(*) n, COALESCE(SUM(f.net_value),0) v
        FROM fact_sales_detail f
        JOIN item_catalog c ON c.company_id = f.company_id
                           AND c.item_code = {coluna} AND TRIM(COALESCE({coluna},'')) <> ''
        WHERE f.company_id = ? AND f.competence = ?
    """, (company_id, comp))
    pl = 100 * r["n"] / total["n"] if total["n"] else 0
    pv = 100 * float(r["v"]) / float(total["v"]) if total["v"] else 0
    if pv > melhor[1]:
        melhor = (rotulo, pv)
    print(f"   {rotulo:<26}{r['n']:>10}{pl:>9.1f}%{backend.brl(r['v']):>18}{pv:>8.1f}%")
print(f"   {'TOTAL DO MÊS':<26}{total['n']:>10}{100.0:>9.1f}%{backend.brl(total['v']):>18}{100.0:>8.1f}%")

# ── 3. O que a tela de Linha perde ───────────────────────────────────────────
print("\n3) O QUE A TELA DE LINHA/GRUPO DEIXA DE FORA")
sem_linha = um("""
    SELECT COUNT(*) n, COALESCE(SUM(f.net_value),0) v
    FROM fact_sales_detail f
    LEFT JOIN item_catalog c ON c.company_id = f.company_id AND c.item_code = f.gtin_value
    WHERE f.company_id = ? AND f.competence = ?
      AND TRIM(COALESCE(c.item_subgroup,'')) = ''
""", (company_id, comp))
pv = 100 * float(sem_linha["v"]) / float(total["v"]) if total["v"] else 0
print(f"   {sem_linha['n']} linha(s) · {backend.brl(sem_linha['v'])} ({pv:.1f}% do mês) ficam sem")
print("   linha de produto — não aparecem em nenhum agrupamento da tela.")
if pv > 20:
    print("   >> Mais de um quinto do faturamento invisível na visão por linha.")
    print("      Quem olhar essa tela vai subestimar toda linha, sem perceber.")
elif pv > 5:
    print("   >> Perda relevante, mas não descaracteriza a leitura.")
else:
    print("   Cobertura boa. A visão por linha pode ser usada como está.")

if melhor[0] and "em uso" not in melhor[0]:
    print(f"\n   >> A chave {melhor[0]} casaria {melhor[1]:.1f}% do valor, mais que a atual.")
    print("      Vale trocar a chave do JOIN antes de construir qualquer coisa em cima.")

# ── 4. O estoque tem giro? ───────────────────────────────────────────────────
if est["n"]:
    print("\n4) A POSIÇÃO DE ESTOQUE TEM MASSA PARA SUGERIR RECOMPRA?")
    # O "vendeu nos 3 meses" sai de UM conjunto em memória, não de uma consulta
    # correlacionada por item. A versão anterior varria o faturamento uma vez
    # para cada um dos 57 mil itens, vezes seis unidades — o mesmo padrão que
    # deixou a carteira lenta, agora dentro do próprio diagnóstico.
    tres = competencias[:3]
    marcadores = ",".join("?" for _ in tres) or "''"
    vendidos: set[str] = set()
    if tres:
        for coluna in ("gtin_value", "manufacturer_sku", "sku_key"):
            vendidos |= {
                (r[0] or "").strip()
                for r in conn.execute(
                    f"SELECT DISTINCT {coluna} FROM fact_sales_detail "
                    f"WHERE company_id = ? AND competence IN ({marcadores}) AND net_value > 0",
                    (company_id, *tres)).fetchall()
                if (r[0] or "").strip()
            }
    print(f"   (giro medido contra {len(vendidos)} códigos vendidos em {', '.join(tres) or '—'},"
          f" somando as três colunas do faturamento)\n")
    print(f"   {'UNIDADE':<16}{'ITENS':>9}{'COM SALDO':>11}{'VENDEU 3M':>11}{'PARADO':>9}")
    for u in conn.execute("SELECT DISTINCT unit_name FROM item_stock WHERE company_id = ? "
                          "ORDER BY unit_name", (company_id,)).fetchall():
        unidade = u["unit_name"]
        itens = com_saldo = vendeu = 0
        for r in conn.execute(
            "SELECT item_code, quantity FROM item_stock WHERE company_id = ? AND unit_name = ?",
            (company_id, unidade),
        ).fetchall():
            itens += 1
            tem_saldo = float(r["quantity"] or 0) > 0
            if tem_saldo:
                com_saldo += 1
            if tem_saldo and (r["item_code"] or "").strip() in vendidos:
                vendeu += 1
        print(f"   {unidade[:15]:<16}{itens:>9}{com_saldo:>11}"
              f"{vendeu:>11}{max(com_saldo - vendeu, 0):>9}")

    print("\n   Curva ABC na filial e frequência de giro (o que o Alfa já classificou):")
    for coluna, rotulo in (("abc_branch", "curva"), ("sales_frequency", "frequência")):
        linhas = conn.execute(
            f"SELECT COALESCE(NULLIF(TRIM({coluna}),''),'(vazio)') k, COUNT(*) n "
            f"FROM item_stock WHERE company_id = ? GROUP BY k ORDER BY n DESC LIMIT 8",
            (company_id,)).fetchall()
        resumo = " · ".join(f"{r['k']}: {r['n']}" for r in linhas)
        print(f"      {rotulo:<12}{resumo}")
    print("\n   'Vendeu 3M' é o que teve saída nas 3 competências mais recentes. Se esse")
    print("   número for alto, há giro real para a sugestão de recompra se apoiar.")
    print("   Se 'parado' dominar, a sugestão viraria uma lista de encalhe.")

conn.close()
