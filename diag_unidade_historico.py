"""
Venda antiga está sendo atribuída à loja ERRADA?

Uso:
    /srv/passini/venv/crm/bin/python /srv/passini/apps/crm-comercial/diag_unidade_historico.py

Quando um vendedor muda de loja, a venda que ele fez ANTES da mudança continua
sendo dele — mas é da loja antiga, não da nova. O sistema guarda isso direito
(people_records tem valid_from/valid_to), mas só acerta quem consulta o mapa
DAQUELA competência. Quem pega o mapa de hoje e aplica ao histórico inteiro
transfere a carteira antiga junto com a pessoa.

Foi assim que a Zona Norte, aberta em agosto/2026, apareceu com 736 linhas em
janeiro: são vendas dos 3 vendedores dela quando estavam na loja anterior.

O que este diagnóstico responde: quantas linhas e quanto dinheiro mudam de
unidade conforme se usa o mapa de hoje ou o mapa da competência. Se der zero,
ninguém trocou de loja e o assunto morre aqui.

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
competencias = sorted(backend.query_competences(conn, company_id))

print(f"Banco: {backend.DB_PATH}")
print(f"Competências: {competencias[0]} a {competencias[-1]} ({len(competencias)} meses)\n")

# ── 1. Quem tem mais de uma vigência de unidade ─────────────────────────────
print("1) PESSOAS QUE TROCARAM DE LOJA (segundo o cadastro)")
vigencias: dict[str, list] = {}
for r in conn.execute(
    "SELECT person_name, base_unit, valid_from, valid_to FROM people_records "
    "WHERE company_id = ? AND base_unit IS NOT NULL AND TRIM(base_unit) <> '' "
    "ORDER BY person_name, date(valid_from)", (company_id,)).fetchall():
    vigencias.setdefault(backend.normalize_whitespace(r["person_name"]), []).append(r)

trocaram = {n: v for n, v in vigencias.items()
            if len({backend.normalize_unit(x["base_unit"]) for x in v}) > 1}
if not trocaram:
    print("   Nenhuma pessoa tem duas unidades no cadastro.")
    print("   >> ATENÇÃO: isso NÃO quer dizer que ninguém mudou. Quer dizer que a")
    print("      mudança não foi registrada com data — o cadastro foi sobrescrito.")
    print("      Nesse caso o histórico é irrecuperável pelo sistema e a correção")
    print("      é lançar a vigência antiga à mão.")
else:
    for nome, v in trocaram.items():
        print(f"   {nome}")
        for x in v:
            ate = x["valid_to"] or "hoje"
            print(f"      {backend.normalize_unit(x['base_unit']):<16} "
                  f"{x['valid_from']} → {ate}")

# ── 2. O que muda na prática ────────────────────────────────────────────────
# Não basta olhar o cadastro: o que importa é quanta VENDA cai em outra loja.
print("\n2) QUANTA VENDA MUDA DE LOJA")
mapa_hoje = backend.build_seller_unit_map(conn, company_id, competencias[-1])


def unidade_de(mapa, nome):
    return (mapa.get(backend.person_key(nome))
            or mapa.get(backend.short_person_key(nome)) or "")


divergentes: dict[tuple, dict] = {}
total_linhas = total_div = 0
valor_div = 0.0
for comp in competencias:
    mapa_comp = backend.build_seller_unit_map(conn, company_id, comp)
    for r in conn.execute(
        "SELECT seller_name, COUNT(*) linhas, SUM(net_value) valor "
        "FROM fact_sales_detail WHERE company_id = ? AND competence = ? "
        "AND seller_name IS NOT NULL AND TRIM(seller_name) <> '' "
        "GROUP BY seller_name", (company_id, comp)).fetchall():
        nome = backend.normalize_whitespace(r["seller_name"])
        u_hoje, u_comp = unidade_de(mapa_hoje, nome), unidade_de(mapa_comp, nome)
        total_linhas += int(r["linhas"])
        if u_hoje and u_comp and u_hoje != u_comp:
            total_div += int(r["linhas"])
            valor_div += float(r["valor"] or 0)
            chave = (nome, u_comp, u_hoje)
            alvo = divergentes.setdefault(chave, {"linhas": 0, "valor": 0.0, "meses": []})
            alvo["linhas"] += int(r["linhas"])
            alvo["valor"] += float(r["valor"] or 0)
            alvo["meses"].append(comp)

pct = (100 * total_div / total_linhas) if total_linhas else 0
print(f"   {total_div} de {total_linhas} linhas ({pct:.1f}%) · {backend.brl(valor_div)}")
if not divergentes:
    print("   >> Nenhuma divergência. Usar o mapa de hoje dá o mesmo resultado que")
    print("      usar o mapa da competência: nada a corrigir nas outras telas.")
else:
    print(f"\n   {'VENDEDOR':<26}{'ERA':<14}{'VIROU':<14}{'LINHAS':>8}{'VALOR':>14}")
    for (nome, era, virou), v in sorted(
            divergentes.items(), key=lambda kv: -kv[1]["linhas"]):
        print(f"   {nome[:25]:<26}{era[:13]:<14}{virou[:13]:<14}"
              f"{v['linhas']:>8}{backend.brl(v['valor']):>14}")
        print(f"      meses afetados: {', '.join(sorted(v['meses']))}")

# ── 3. Onde isso aparece ────────────────────────────────────────────────────
print("\n3) LEITURA")
if not divergentes:
    print("   Nada a fazer.")
else:
    por_unidade: dict[str, float] = {}
    for (_, era, virou), v in divergentes.items():
        por_unidade[virou] = por_unidade.get(virou, 0) + v["valor"]
        por_unidade[era] = por_unidade.get(era, 0) - v["valor"]
    print("   Efeito líquido por loja (quanto cada uma GANHA de indevido):")
    for u, val in sorted(por_unidade.items(), key=lambda kv: -kv[1]):
        sinal = "+" if val >= 0 else "−"
        print(f"      {u[:20]:<22}{sinal}{backend.brl(abs(val))}")
    print("\n   Toda tela que recorta por unidade usando o mapa de HOJE carrega esse")
    print("   desvio: carteira, meta, ranking, mix, recompra. As que recortam por")
    print("   competência estão certas. O próximo passo é conferir uma a uma —")
    print("   este diagnóstico só diz o tamanho do problema, não onde ele está.")

conn.close()
