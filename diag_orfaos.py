"""
Os clientes que não caem em nenhuma unidade — e se algum deles ainda compra.

Uso:
    /srv/passini/venv/crm/bin/python /srv/passini/apps/crm-comercial/diag_orfaos.py
    /srv/passini/venv/crm/bin/python /srv/passini/apps/crm-comercial/diag_orfaos.py --listar

A carteira do gerente filtra por unidade, então cliente sem unidade resolvida
não aparece para ninguém além da diretoria. A pergunta que decide se isso é
problema não é "quantos são", é "algum deles ainda compra": cadastro velho e
parado é ruído; cliente ativo invisível é carteira que ninguém está trabalhando.

A unidade sai em cascata (ver unit_for_client_row): vendedor interno → bairro →
cidade inteira → mapa antigo de cidades. O script diz em qual degrau cada
cliente caiu fora.

Não altera nada.
"""
import os
import sys
from collections import Counter, defaultdict
from datetime import date
from pathlib import Path

sys.path.insert(0, "/srv/passini/apps/crm-comercial")

if not os.environ.get("PASSINI_CRM_DATA"):
    for candidate in ("/srv/passini/data/crm", "/srv/passini/data"):
        if (Path(candidate) / "passini_dashboard.db").exists():
            os.environ["PASSINI_CRM_DATA"] = candidate
            break

import backend  # noqa: E402

listar = "--listar" in sys.argv
conn = backend.get_connection()
company_id = conn.execute("SELECT id FROM companies LIMIT 1").fetchone()["id"]
print(f"Banco: {backend.DB_PATH}")

filtros = backend.build_filters_from_query({})
linhas = backend.crm_base_client_rows_cached(conn, company_id, filtros)
orfaos = [r for r in linhas if not backend.normalize_unit(r.get("unitName"))]
print(f"{len(linhas)} clientes na base · {len(orfaos)} sem unidade "
      f"({100 * len(orfaos) / max(len(linhas), 1):.0f}%)\n")

if not orfaos:
    print("Nenhum órfão. Nada a investigar.")
    conn.close()
    raise SystemExit(0)

# ── 1. Em que degrau da cascata cada um caiu fora ────────────────────────────
print("1) POR QUE NÃO TÊM UNIDADE")
motivos: Counter = Counter()
for r in orfaos:
    tem_vendedor = bool(backend.normalize_whitespace(r.get("assignedSeller")))
    tem_cidade = bool(backend.normalize_whitespace(r.get("cityName")))
    if not tem_vendedor and not tem_cidade:
        motivos["sem vendedor E sem cidade"] += 1
    elif tem_vendedor and not tem_cidade:
        motivos["tem vendedor, mas o vendedor não tem unidade"] += 1
    elif not tem_vendedor and tem_cidade:
        motivos["tem cidade, mas a cidade não está mapeada"] += 1
    else:
        motivos["tem vendedor e cidade — nenhum dos dois resolve"] += 1
for motivo, n in motivos.most_common():
    print(f"   {n:>7}  {motivo}")

# ── 2. Estão vivos? ──────────────────────────────────────────────────────────
print("\n2) AINDA COMPRAM? (pela última compra registrada)")
hoje = date.today()
faixas: Counter = Counter()
ativos_recentes = []
for r in orfaos:
    dt = backend.parse_datetime_flexible(r.get("lastPurchaseAt"))
    if not dt:
        faixas["nunca comprou / sem registro"] += 1
        continue
    dias = (hoje - dt.date()).days
    if dias <= 60:
        faixas["comprou nos últimos 60 dias"] += 1
        ativos_recentes.append((r, dias))
    elif dias <= 365:
        faixas["comprou no último ano"] += 1
    elif dt.date().year >= 2023:
        faixas["última compra em 2023 ou 2024"] += 1
    else:
        faixas["última compra até 2022"] += 1
ordem = ["comprou nos últimos 60 dias", "comprou no último ano",
         "última compra em 2023 ou 2024", "última compra até 2022",
         "nunca comprou / sem registro"]
for faixa in ordem:
    if faixas.get(faixa):
        print(f"   {faixas[faixa]:>7}  {faixa}")

# ── 3. Quanto isso vale ──────────────────────────────────────────────────────
receita_mes = sum(float(r.get("currentRevenue") or 0) for r in orfaos)
receita_total = sum(float(r.get("currentRevenue") or 0) for r in linhas)
print(f"\n3) PESO NO FATURAMENTO DO MÊS CORRENTE")
print(f"   Órfãos.: {backend.brl(receita_mes)}")
print(f"   Base...: {backend.brl(receita_total)}")
if receita_total:
    print(f"   Os sem unidade representam {100 * receita_mes / receita_total:.1f}% do mês.")

# ── 4. Onde o conserto rende mais ────────────────────────────────────────────
print("\n4) SE FOR CONSERTAR, COMECE POR AQUI")
por_cidade: dict[str, list] = defaultdict(list)
for r, _dias in ativos_recentes:
    por_cidade[backend.normalize_upper(r.get("cityName")) or "(sem cidade)"].append(r)
if ativos_recentes:
    print(f"   {len(ativos_recentes)} cliente(s) compraram nos últimos 60 dias e não")
    print("   aparecem na carteira de nenhum gerente. Por cidade:")
    for cidade, itens in sorted(por_cidade.items(), key=lambda kv: -len(kv[1]))[:15]:
        valor = sum(float(x.get("currentRevenue") or 0) for x in itens)
        print(f"      {len(itens):>5}  {cidade[:28]:<30}{backend.brl(valor)}")
    print("\n   Mapear essas cidades (ou vincular o vendedor interno) devolve")
    print("   cliente ativo para a carteira de alguém.")
else:
    print("   Nenhum órfão comprou nos últimos 60 dias — é base histórica parada,")
    print("   e não carteira viva escondida. Não há urgência.")

if listar and ativos_recentes:
    print("\n5) OS ATIVOS SEM UNIDADE (até 60)")
    print(f"   {'CÓDIGO':<12}{'CLIENTE':<40}{'CIDADE':<22}{'VENDEDOR':<22}DIAS")
    for r, dias in sorted(ativos_recentes, key=lambda x: x[1])[:60]:
        print(f"   {str(r.get('clientKey'))[:11]:<12}"
              f"{str(r.get('clientName'))[:39]:<40}"
              f"{str(r.get('cityName') or '—')[:21]:<22}"
              f"{str(r.get('assignedSeller') or '—')[:21]:<22}{dias}")
elif ativos_recentes:
    print("\n   Rode com --listar para ver os clientes um a um.")

conn.close()
