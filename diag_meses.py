"""
Mostra a saúde de TODOS os meses de uma vez, para decidir quais refazer.

Uso no servidor:
    /srv/passini/venv/crm/bin/python /srv/passini/apps/crm-comercial/diag_meses.py
    /srv/passini/venv/crm/bin/python /srv/passini/apps/crm-comercial/diag_meses.py 2026

Para cada competência compara o faturamento detalhado com o resumo de custo x
venda e mostra de quantas importações o mês veio. Mês montado por vários
relatórios diários costuma estar inflado: os diários do Alfa trazem um intervalo
de dias e se sobrepõem. Mês vindo de uma importação só é o retrato correto.

Também mostra quanto do mês tem MARCA gravada. A marca só passou a ser gravada
em 20/08/2026, então mês anterior a isso aparece vazio na tela de Marcas até ser
reimportado do relatório completo.

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

filtro = next((a for a in sys.argv[1:] if not a.startswith("-")), "")

conn = backend.get_connection()
company_id = conn.execute("SELECT id FROM companies LIMIT 1").fetchone()["id"]

print(f"Banco: {backend.DB_PATH}")
print(f"Competências{' começando com ' + filtro if filtro else ''}\n")

detalhado = {r["competence"]: r for r in conn.execute(
    """
    SELECT competence, COUNT(*) linhas, ROUND(SUM(net_value), 2) valor,
           COUNT(DISTINCT import_id) imports,
           SUM(CASE WHEN TRIM(COALESCE(brand_name,'')) <> '' THEN 1 ELSE 0 END) com_marca
    FROM fact_sales_detail WHERE company_id = ? GROUP BY competence
    """, (company_id,)).fetchall()}
oficial = {r["competence"]: float(r["v"] or 0) for r in conn.execute(
    "SELECT competence, ROUND(SUM(net_value),2) v FROM fact_unit_summary "
    "WHERE company_id = ? GROUP BY competence", (company_id,)).fetchall()}
# Um mês só está completo quando as quatro fontes estão lá. Sem olhar as
# quatro, "está limpo" vira opinião.
consolidado = {r["competence"]: int(r["n"] or 0) for r in conn.execute(
    "SELECT competence, COUNT(*) n FROM crm_client_summary "
    "WHERE company_id = ? GROUP BY competence", (company_id,)).fetchall()}
devolucoes = {r["competence"]: float(r["v"] or 0) for r in conn.execute(
    "SELECT competence, ROUND(SUM(total_value),2) v FROM fact_warranty_returns "
    "WHERE company_id = ? GROUP BY competence", (company_id,)).fetchall()}
vendedor_oficial = {r["competence"] for r in conn.execute(
    "SELECT DISTINCT competence FROM fact_vendor_summary WHERE company_id = ?",
    (company_id,)).fetchall()}

meses = sorted(set(detalhado) | set(oficial) | set(consolidado) | set(devolucoes))
if filtro:
    meses = [m for m in meses if m.startswith(filtro)]
if not meses:
    print("Nenhuma competência encontrada.")
    conn.close()
    sys.exit(0)

print(f"   {'MÊS':<9}{'IMP':>4}{'LINHAS':>8}{'DETALHADO':>15}{'OFICIAL':>15}"
      f"{'DIF':>6}{'MARCA':>6}  DET CST CON DEV   SITUAÇÃO")

refazer = []
sem_marca = []
sem_oficial = []
pendencias: dict[str, list[str]] = {}
prontos = []
for m in meses:
    d = detalhado.get(m)
    o = oficial.get(m, 0.0)
    linhas = d["linhas"] if d else 0
    valor = float(d["valor"] or 0) if d else 0.0
    imports = d["imports"] if d else 0
    pct_marca = 100.0 * (d["com_marca"] or 0) / linhas if linhas else 0.0
    dif = (100 * (valor / o - 1)) if o else None

    # Mês com pouquíssimas linhas e soma negativa não é um mês carregado: são só
    # as devoluções que os relatórios recentes arrastam com a data da nota
    # original. Tratar isso como mês a refazer gera lista de alarme falso.
    so_devolucao = linhas > 0 and (valor <= 0 or linhas < 500)

    notas = []
    if so_devolucao:
        notas.append("só devoluções, sem carga de venda")
    else:
        # Número de importações NÃO é sinal de problema: entre relatórios
        # diários o descarte por repetição funciona, porque descrevem a venda do
        # mesmo jeito. O que estraga é misturar diário com relatório completo, e
        # isso aparece na diferença contra o oficial — não na contagem.
        if imports > 1:
            notas.append(f"{imports} importações")
        if dif is not None and dif > 15:
            notas.append("INFLADO")
        if linhas and pct_marca < 50:
            notas.append("sem marca")
    if o and not linhas:
        notas.append("só o resumo, sem detalhado")
    if not o and linhas and not so_devolucao:
        notas.append("falta o custo x venda para comparar")
        sem_oficial.append(m)

    if not so_devolucao and dif is not None and dif > 15:
        refazer.append(m)
    if not so_devolucao and linhas and pct_marca < 50:
        sem_marca.append(m)

    # As quatro fontes do mês. "ok" só quando o mês está inteiro.
    tem = {
        "DET": linhas > 0 and not so_devolucao,
        "CST": bool(o) and m in vendedor_oficial,
        "CON": consolidado.get(m, 0) > 0,
        "DEV": devolucoes.get(m, 0) > 0,
    }
    if not so_devolucao and linhas:
        faltando = [k for k, v in tem.items() if not v]
        if pct_marca < 50:
            faltando.append("MARCA")
        if dif is not None and dif > 15:
            faltando.append("INFLADO")
        if faltando:
            pendencias[m] = faltando
        else:
            prontos.append(m)
    marcadores = " ".join(" ✓ " if tem[k] else " · " for k in ("DET", "CST", "CON", "DEV"))

    _dif = f"{dif:+.0f}%" if dif is not None else "  —"
    print(f"   {m:<9}{imports:>4}{linhas:>8}{valor:>15,.2f}{o:>15,.2f}"
          f"{_dif:>6}{pct_marca:>5.0f}%  {marcadores}   {', '.join(notas)}")

print("\n   DET faturamento detalhado · CST custo x venda · CON consolidado por cliente"
      " · DEV devoluções")

print("\nCHECKLIST DA MIGRAÇÃO")
if prontos:
    print(f"   Completos ({len(prontos)}): {', '.join(prontos)}")
if pendencias:
    for m in sorted(pendencias):
        falta = pendencias[m]
        # Refazer é diferente de completar: se falta a marca ou o mês está
        # inflado, o detalhado precisa ser zerado antes. Se falta só uma fonte,
        # é importar por cima, sem apagar nada.
        precisa_zerar = "MARCA" in falta or "INFLADO" in falta
        rotulo = "REFAZER" if precisa_zerar else "completar"
        legiveis = {"DET": "faturamento detalhado", "CST": "custo x venda",
                    "CON": "consolidado por cliente", "DEV": "devoluções",
                    "MARCA": "marca", "INFLADO": "valor inflado"}
        print(f"\n   {m}  {rotulo}: falta {', '.join(legiveis.get(f, f) for f in falta)}")
        if precisa_zerar:
            print(f"      limpar_import.py --zerar-mes {m} --aplicar")
            print(f"      e importar: FAT DETALHADO do mês, depois o que mais faltar")
        else:
            print(f"      importar {', '.join(legiveis.get(f, f) for f in falta)} "
                  f"— não precisa zerar nada")
if not prontos and not pendencias:
    print("   Nenhum mês com carga de venda.")

print("\nVEREDITO")
if refazer:
    print(f"   1. INFLADO, refazer ({len(refazer)}): {', '.join(refazer)}")
    print("      Para cada um:")
    print("         limpar_import.py --zerar-mes <mês> --aplicar")
    print("      e depois importar o FAT DETALHADO completo do mês pelo CRM.")
else:
    print("   1. Nenhum mês está inflado. O número bate com o custo x venda.")

if sem_oficial:
    print(f"\n   2. Sem custo x venda ({len(sem_oficial)}): {', '.join(sem_oficial)}")
    print("      Sem ele não dá para saber se o mês está certo. Importar o")
    print("      custo x venda desses meses é barato e vem antes de refazer.")

if sem_marca:
    print(f"\n   3. Sem marca ({len(sem_marca)}): {', '.join(sem_marca)}")
    print("      Esses meses não aparecem na tela de Marcas. Só refazer resolve,")
    print("      e é um export por mês — decida se a tela de Marcas precisa do")
    print("      histórico ou se basta daqui para frente.")

conn.close()
