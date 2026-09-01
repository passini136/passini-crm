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

meses = sorted(set(detalhado) | set(oficial))
if filtro:
    meses = [m for m in meses if m.startswith(filtro)]
if not meses:
    print("Nenhuma competência encontrada.")
    conn.close()
    sys.exit(0)

print(f"   {'MÊS':<9}{'IMPORTS':>8}{'LINHAS':>9}{'DETALHADO':>16}{'OFICIAL':>16}"
      f"{'DIF':>7}{'MARCA':>7}   SITUAÇÃO")

refazer = []
sem_marca = []
for m in meses:
    d = detalhado.get(m)
    o = oficial.get(m, 0.0)
    linhas = d["linhas"] if d else 0
    valor = float(d["valor"] or 0) if d else 0.0
    imports = d["imports"] if d else 0
    pct_marca = 100.0 * (d["com_marca"] or 0) / linhas if linhas else 0.0
    dif = (100 * (valor / o - 1)) if o else None

    notas = []
    # Um mês correto vem de UM relatório completo. Vários imports quase sempre
    # querem dizer diários sobrepostos.
    if imports > 1:
        notas.append(f"{imports} importações")
    if dif is not None and dif > 15:
        notas.append("inflado")
    if linhas and pct_marca < 50:
        notas.append("sem marca")
    if o and not linhas:
        notas.append("só o resumo, sem detalhado")
    if not o and linhas:
        notas.append("sem resumo para comparar")

    if linhas and (imports > 1 or (dif is not None and dif > 15)):
        refazer.append(m)
    if linhas and pct_marca < 50:
        sem_marca.append(m)

    _dif = f"{dif:+.0f}%" if dif is not None else "  —"
    print(f"   {m:<9}{imports:>8}{linhas:>9}{valor:>16,.2f}{o:>16,.2f}"
          f"{_dif:>7}{pct_marca:>6.0f}%   {', '.join(notas)}")

print("\nVEREDITO")
if refazer:
    print(f"   Refazer ({len(refazer)}): {', '.join(refazer)}")
    print("   Para cada um, a sequência é:")
    print("      limpar_import.py --zerar-mes <mês> --aplicar")
    print("      e depois importar o FAT DETALHADO completo daquele mês pelo CRM.")
else:
    print("   Nenhum mês precisa ser refeito.")
if sem_marca:
    print(f"\n   Sem marca ({len(sem_marca)}): {', '.join(sem_marca)}")
    print("   Esses meses não aparecem na tela de Marcas. Refazer resolve junto.")

conn.close()
