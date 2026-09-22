"""
Por que "Cliente grande em queda" vem vazio?

Uso:
    /srv/passini/venv/crm/bin/python /srv/passini/apps/crm-comercial/diag_cliente_queda.py

O bloco exige DUAS coisas ao mesmo tempo: ser cliente de classe alta E estar
comprando menos que a própria média. Vazio pode ser qualquer uma das duas — ou
as duas. Chutar qual delas é o caminho para "consertar" o lado errado.

A classe vem da média dos 3 meses ANTERIORES ao mês em curso:
    DIAMANTE > R$ 10.000/mês · OURO >= R$ 6.000 · PRATA >= R$ 3.000
    BRONZE >= R$ 500 · abaixo disso, NAO_CLASSIFICADO

O que conferir: se quase toda a base for BRONZE e NAO_CLASSIFICADO, o corte de
classe é alto demais para esta carteira e o bloco nunca teria o que mostrar.

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
filtros = backend.build_filters_from_query({})
linhas = backend.crm_base_client_rows_cached(conn, company_id, filtros)

print(f"Banco: {backend.DB_PATH}")
print(f"Competência de referência: {filtros.get('competence') or '(a mais recente)'}")
print(f"{len(linhas)} cliente(s) na base\n")

# ── 1. A base alcança as classes altas? ─────────────────────────────────────
print("1) COMO A BASE SE DISTRIBUI POR CLASSE")
por_classe = defaultdict(lambda: {"n": 0, "media": 0.0, "queda": 0})
for c in linhas:
    classe = c.get("classCode") or "SEM_CLASSE"
    alvo = por_classe[classe]
    alvo["n"] += 1
    alvo["media"] += float(c.get("averageRevenue") or 0)
    if float(c.get("dropPct") or 0) <= backend.HIGH_VALUE_DROP_PCT:
        alvo["queda"] += 1

ordem = ["DIAMANTE", "OURO", "PRATA", "BRONZE", "NAO_CLASSIFICADO", "SEM_CLASSE"]
print(f"   {'CLASSE':<20}{'CLIENTES':>10}{'% DA BASE':>11}{'MÉDIA/MÊS':>14}{'EM QUEDA':>10}")
for classe in ordem:
    if classe not in por_classe:
        continue
    d = por_classe[classe]
    pct = 100 * d["n"] / len(linhas) if linhas else 0
    media = d["media"] / d["n"] if d["n"] else 0
    print(f"   {classe:<20}{d['n']:>10}{pct:>10.1f}%{backend.brl(media):>14}{d['queda']:>10}")

altas = sum(por_classe[c]["n"] for c in ("DIAMANTE", "OURO") if c in por_classe)
print(f"\n   DIAMANTE + OURO = {altas} cliente(s).")
if altas == 0:
    print("   >> A régua antiga não tinha como achar nada: não existe cliente")
    print("      nessas duas classes na base atual.")
elif altas < 10:
    print("   >> Punhado de contas. Qualquer exigência adicional zera o bloco.")

# ── 2. O funil, passo a passo ───────────────────────────────────────────────
# Mostra onde cada corte derruba, para não trocar a régua errada.
print("\n2) O FUNIL DO BLOCO")
com_media = [c for c in linhas if float(c.get("averageRevenue") or 0) > 0]
print(f"   {len(linhas):>7} clientes na base")
print(f"   {len(com_media):>7} têm média > 0 nos 3 meses anteriores")
for conjunto, rotulo in ((("DIAMANTE", "OURO"), "Diamante + Ouro (régua antiga)"),
                         (("DIAMANTE", "OURO", "PRATA"), "Diamante + Ouro + Prata (nova)")):
    da_classe = [c for c in linhas if c.get("classCode") in conjunto]
    em_queda = [c for c in da_classe
                if float(c.get("dropPct") or 0) <= backend.HIGH_VALUE_DROP_PCT]
    perdido = sum(float(c.get("averageRevenue") or 0) - float(c.get("currentRevenue") or 0)
                  for c in em_queda)
    print(f"\n   {rotulo}")
    print(f"   {len(da_classe):>7} na classe")
    print(f"   {len(em_queda):>7} caindo mais de {abs(backend.HIGH_VALUE_DROP_PCT) * 100:.0f}%"
          f"  → {backend.brl(perdido)} a menos que a média")

# ── 3. Quem apareceria ──────────────────────────────────────────────────────
print("\n3) OS 15 QUE MAIS PESAM NA NOVA RÉGUA")
candidatos = [c for c in linhas
              if c.get("classCode") in backend.HIGH_VALUE_CLASSES
              and float(c.get("dropPct") or 0) <= backend.HIGH_VALUE_DROP_PCT]
candidatos.sort(key=lambda c: -(float(c.get("averageRevenue") or 0)
                                - float(c.get("currentRevenue") or 0)))
if not candidatos:
    print("   Nenhum. Se a seção 1 mostrar clientes nas classes altas, então o")
    print("   problema é o corte de queda, não a classe.")
else:
    print(f"   {'CLIENTE':<32}{'CLASSE':<11}{'MÉDIA':>12}{'ATUAL':>12}{'QUEDA':>8}")
    for c in candidatos[:15]:
        media = float(c.get("averageRevenue") or 0)
        atual = float(c.get("currentRevenue") or 0)
        print(f"   {str(c.get('clientName'))[:31]:<32}{str(c.get('classCode'))[:10]:<11}"
              f"{backend.brl(media):>12}{backend.brl(atual):>12}"
              f"{float(c.get('dropPct') or 0) * 100:>7.0f}%")

# ── 4. O mês em curso atrapalha? ────────────────────────────────────────────
# O "atual" é o mês corrente, que não terminou. Comparar meio mês contra a
# média de três meses inteiros acusa queda em quase todo mundo — e aí o bloco
# vira ruído em vez de alerta. Vale saber o tamanho desse efeito.
print("\n4) O MÊS EM CURSO ESTÁ INCOMPLETO?")
_amostra = next((c for c in linhas if c.get("dropBasis")), None)
if _amostra:
    _b = _amostra["dropBasis"]
    print(f"   Parte do mês já decorrida (dias úteis): {_b['monthProgress'] * 100:.0f}%")
    print("   A queda compara o realizado com a média AJUSTADA a essa fatia,")
    print("   não com o mês cheio.")
caindo_todos = sum(1 for c in linhas
                   if float(c.get("averageRevenue") or 0) > 0
                   and float(c.get("dropPct") or 0) <= backend.HIGH_VALUE_DROP_PCT)
pct_caindo = 100 * caindo_todos / len(com_media) if com_media else 0
print(f"   {caindo_todos} de {len(com_media)} clientes com média > 0 aparecem em queda "
      f"({pct_caindo:.0f}%)")
if pct_caindo > 70:
    print("   >> Quase todo mundo 'em queda'. Isso é o mês incompleto falando, não")
    print("      o comportamento do cliente. Vale comparar contra o mesmo dia do")
    print("      mês anterior, ou só usar o mês fechado.")
else:
    print("   >> Proporção saudável: a queda está medindo comportamento.")

# ── 5. Nome repetido inflando a média ───────────────────────────────────────
# ARCELORMITTAL apareceu 4× com a MESMA média de R$ 18.545,44, CONECTA idem.
# O faturamento é indexado por nome e existe uma vez só: se N códigos recebem
# o valor inteiro, a carteira mostra dinheiro que não entrou.
# ── 4b. "Em queda" ou "não comprou ainda"? ──────────────────────────────────
# São dois problemas diferentes com duas conversas diferentes, e misturá-los
# faz o alerta perder o sentido. O ajuste por dias úteis não resolveu (87% →
# 84%), o que já indica que o peso não está em quem comprou menos.
print("\n4b) QUEM ESTÁ CAINDO x QUEM NÃO COMPROU")
em_queda = [c for c in linhas
            if float(c.get("averageRevenue") or 0) > 0
            and float(c.get("dropPct") or 0) <= backend.HIGH_VALUE_DROP_PCT]
zerados = [c for c in em_queda if float(c.get("currentRevenue") or 0) <= 0]
comprando = [c for c in em_queda if float(c.get("currentRevenue") or 0) > 0]
print(f"   {len(zerados):>6} sem NENHUMA compra no mês  ({100 * len(zerados) / len(em_queda):.0f}%)")
print(f"   {len(comprando):>6} compraram, mas abaixo do esperado")
if len(zerados) > len(comprando):
    print("\n   >> A lista é dominada por quem ainda não comprou. Isso não é")
    print("      'comprando menos' — é 'parou de comprar', que já tem bloco")
    print("      próprio (Cobertura falha) e pede outra conversa com o cliente.")
# E dentro das classes altas, que é o que o painel mostra de fato.
altos = [c for c in em_queda if c.get("classCode") in backend.HIGH_VALUE_CLASSES]
altos_zero = [c for c in altos if float(c.get("currentRevenue") or 0) <= 0]
print(f"\n   Nas classes do painel: {len(altos)} em queda, "
      f"{len(altos_zero)} deles sem compra nenhuma")

print("\n5) O MESMO NOME EM VÁRIOS CÓDIGOS")
por_nome = defaultdict(list)
for c in linhas:
    nome = backend.normalize_client_key(c.get("clientName"))
    if nome:
        por_nome[nome].append(c)
repetidos = {n: v for n, v in por_nome.items() if len(v) > 1}
com_media = [(n, v) for n, v in repetidos.items()
             if sum(float(x.get("averageRevenue") or 0) for x in v) > 0]
print(f"   {len(repetidos)} nome(s) com mais de um código · "
      f"{len(com_media)} com faturamento")
if com_media:
    # Quanto a média TOTAL da carteira cresce por causa da repetição.
    inflado = 0.0
    for _, v in com_media:
        medias = sorted((float(x.get("averageRevenue") or 0) for x in v), reverse=True)
        inflado += sum(medias[1:])   # tudo além do maior é repetição
    print(f"   {backend.brl(inflado)} de média/mês repetida entre códigos do mesmo nome")
    if inflado < 1:
        print("   >> CORRETO: o faturamento ficou com UM código por nome.")
    else:
        print("   >> INFLADO: mais de um código do mesmo nome recebeu o valor.")
    print(f"\n   {'NOME':<34}{'CÓDIGOS':>8}{'DONO DO VALOR':>16}{'OS OUTROS':>12}")
    piores = sorted(com_media,
                    key=lambda kv: -max(float(x.get("averageRevenue") or 0)
                                        for x in kv[1]))[:10]
    for nome, v in piores:
        medias = sorted((float(x.get("averageRevenue") or 0) for x in v), reverse=True)
        print(f"   {str(v[0].get('clientName'))[:33]:<34}{len(v):>8}"
              f"{backend.brl(medias[0]):>16}{backend.brl(sum(medias[1:])):>12}")
    print("\n   'OS OUTROS' precisa ser R$ 0,00: o faturamento vem por NOME e")
    print("   existe uma vez só. Valor ali é dinheiro contado duas vezes.")

conn.close()
