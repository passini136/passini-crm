"""
Remove do faturamento tudo que UMA importação trouxe.

Uso no servidor:
    # ver o que seria removido (não altera nada)
    /srv/passini/venv/crm/bin/python /srv/passini/apps/crm-comercial/limpar_import.py 88

    # remover de verdade
    /srv/passini/venv/crm/bin/python /srv/passini/apps/crm-comercial/limpar_import.py 88 --aplicar

    # deixar o mês com UMA fonte só: fica a 130, sai todo o resto de agosto
    /srv/passini/venv/crm/bin/python /srv/passini/apps/crm-comercial/limpar_import.py 2026-08 --exceto 130

Serve para desfazer um arquivo que não devia ter entrado: um relatório na pasta
errada, ou uma reimportação manual por cima do que os diários já traziam.

O --exceto existe porque os relatórios diários do Alfa trazem um intervalo de
dias, não um dia só. Importados todo dia, eles se sobrepõem e o mês soma mais de
uma vez a mesma venda. Quando o mês fecha, o certo é subir um relatório completo
e deixar só ele.

É o caminho SEGURO. Procurar linha repetida por semelhança apaga venda de
verdade — duas peças diferentes de mesmo preço, para o mesmo cliente, no mesmo
dia, são duas vendas legítimas e parecem uma repetição. Aqui não há palpite:
cada linha sabe de qual importação veio.

O sistema grava uma cópia de segurança sozinho antes de remover, em
/srv/passini/data/crm/backups/. As 10 mais recentes ficam guardadas.
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

argv = sys.argv[1:]
aplicar = "--aplicar" in argv
# Passar 2026-08 (pode repetir) limita a remoção a certas competências
meses = [a for a in argv if len(a) == 7 and a[4] == "-"]

# --exceto inverte a conta: em vez de dizer o que sai, diz o único que FICA.
# É o caminho para "esse mês vai ter uma fonte só", quando um arquivo completo
# substitui vários parciais que se sobrepõem.
if "--exceto" in argv:
    corte = argv.index("--exceto")
    manter = [int(a) for a in argv[corte + 1:] if a.isdigit()]
    ids = [int(a) for a in argv[:corte] if a.isdigit()]
else:
    manter = []
    ids = [int(a) for a in argv if a.isdigit()]

conn = backend.get_connection()
company_id = conn.execute("SELECT id FROM companies LIMIT 1").fetchone()["id"]


def money(v):
    return f"R$ {float(v or 0):>15,.2f}"


print(f"Banco: {backend.DB_PATH}\n")


def resumo_import(import_id, competencia):
    return conn.execute(
        "SELECT COUNT(*) n, ROUND(SUM(net_value),2) v, "
        "       SUM(CASE WHEN TRIM(COALESCE(brand_name,'')) <> '' THEN 1 ELSE 0 END) com, "
        "       MIN(issue_date) de, MAX(issue_date) ate "
        "FROM fact_sales_detail WHERE company_id = ? AND competence = ? AND import_id = ?",
        (company_id, competencia, import_id)).fetchone()


if manter:
    if len(meses) != 1:
        print("Com --exceto é obrigatório informar UM mês, ex:")
        print("   limpar_import.py 2026-08 --exceto 130")
        conn.close()
        sys.exit(1)
    competencia = meses[0]
    presentes = [r["import_id"] for r in conn.execute(
        "SELECT DISTINCT import_id FROM fact_sales_detail "
        "WHERE company_id = ? AND competence = ? ORDER BY import_id",
        (company_id, competencia)).fetchall()]
    faltando = [i for i in manter if i not in presentes]
    if faltando:
        # Guardar um número que não existe no mês apagaria o mês inteiro.
        print(f"A(s) importação(ões) {', '.join(str(i) for i in faltando)} não tem "
              f"linha nenhuma em {competencia}.")
        print("Confira o número antes de continuar — nada foi alterado.")
        conn.close()
        sys.exit(1)
    print(f"FICA em {competencia}:")
    for i in manter:
        r = resumo_import(i, competencia)
        pct = 100.0 * (r["com"] or 0) / (r["n"] or 1)
        print(f"   import {i}: {r['n']} linha(s) · {money(r['v']).strip()} · "
              f"{pct:.0f}% com marca")
        print(f"      emissões de {str(r['de'])[:10]} a {str(r['ate'])[:10]}")
    ids = [i for i in presentes if i not in manter]
    print(f"\nSAI: {len(ids)} importação(ões) — {', '.join(str(i) for i in ids)}\n")
    if not ids:
        print("Não há mais nada neste mês. Nada a fazer.")
        conn.close()
        sys.exit(0)

if not ids:
    print("Informe o número da importação. As do faturamento detalhado:\n")
    print(f"   {'IMPORT':<8}{'QUANDO':<22}{'LINHAS':>9}{'VALOR':>20}{'POR LINHA':>12}"
          f"   MESES QUE ALIMENTA")
    for r in conn.execute(
        """
        SELECT d.import_id, MAX(i.imported_at) quando, COUNT(*) n,
               ROUND(SUM(d.net_value), 2) v,
               COUNT(DISTINCT d.competence) meses,
               MIN(d.competence) primeiro, MAX(d.competence) ultimo
        FROM fact_sales_detail d LEFT JOIN imports i ON i.id = d.import_id
        WHERE d.company_id = ? GROUP BY d.import_id ORDER BY quando DESC LIMIT 40
        """, (company_id,)).fetchall():
        por_linha = float(r["v"] or 0) / (r["n"] or 1)
        # O valor por linha denuncia o arquivo errado: os diários ficam todos na
        # mesma faixa e o consolidado por cliente destoa em várias vezes.
        marca = "  <<< destoa" if por_linha > 400 else ""
        # Sem os meses a lista engana: uma carga histórica tem valor gigante por
        # cobrir o ano inteiro, e um diário pode nem tocar no mês que se procura.
        if r["meses"] == 1:
            periodo = str(r["primeiro"])
        else:
            periodo = f"{r['primeiro']} a {r['ultimo']} ({r['meses']} meses)"
        print(f"   {str(r['import_id']):<8}{str(r['quando'])[:19]:<22}{r['n']:>9}"
              f"{money(r['v']):>20}{por_linha:>12.2f}   {periodo}{marca}")
    print("\nRode de novo passando o número, ex: limpar_import.py 88")
    conn.close()
    sys.exit(0)

total_linhas = 0
total_valor = 0.0
for import_id in ids:
    res = backend.delete_import_rows(conn, company_id, import_id,
                                     competences=meses or None, simular=not aplicar)
    print(f"IMPORTAÇÃO {import_id}")
    if not res["rows"]:
        print("   Nada gravado por esta importação"
              + (f" nos meses {', '.join(meses)}." if meses else ".") + "\n")
        continue
    print(f"   {'MÊS':<10}{'LINHAS':>8}{'VALOR':>19}   OUTRAS IMPORTAÇÕES DO MESMO MÊS")
    sozinho = []
    for c in res["byCompetence"]:
        if c["otherImports"]:
            nota = (f"{c['otherImports']} importação(ões), {c['otherRows']} linha(s), "
                    f"{money(c['otherValue']).strip()}")
        else:
            # Sem outra fonte, remover apaga o mês inteiro. É o caso em que a
            # limpeza deixa de ser correção e vira perda de dado.
            nota = ">> NENHUMA — é a única fonte deste mês, NÃO REMOVER"
            sozinho.append(c["competence"])
        print(f"   {c['competence']:<10}{c['rows']:>8}{money(c['value']):>19}   {nota}")
    print(f"   {'TOTAL':<10}{res['rows']:>8}{money(res['value']):>19}")
    if sozinho and not meses:
        print(f"\n   ATENÇÃO: {', '.join(sozinho)} só tem esta importação.")
        print("   Remover tudo apagaria esses meses. Use --mes para escolher:")
        seguros = [c["competence"] for c in res["byCompetence"] if c["otherImports"]]
        if seguros:
            print(f"      limpar_import.py {import_id} "
                  + " ".join(seguros) + " --aplicar")
    if res["applied"]:
        print("   REMOVIDO")
        if res.get("backup"):
            print(f"   Cópia de segurança: {res['backup']}")
        else:
            print("   ATENÇÃO: não consegui gravar a cópia de segurança.")
    else:
        print("   SIMULAÇÃO — nada foi apagado")
    print()
    total_linhas += res["rows"]
    total_valor += res["value"]

if len(ids) > 1:
    print(f"SOMA: {total_linhas} linha(s) · {money(total_valor)}\n")

if manter:
    # Mostrar como o mês fica, para conferir contra o relatório do Alfa antes
    # (na simulação) e depois (quando aplicado) — é a prova de que deu certo.
    competencia = meses[0]
    if aplicar:
        agora = conn.execute(
            "SELECT COUNT(*) n, ROUND(SUM(net_value),2) v FROM fact_sales_detail "
            "WHERE company_id = ? AND competence = ?",
            (company_id, competencia)).fetchone()
        rotulo, linhas_fim, valor_fim = "O mês ficou com", agora["n"], agora["v"]
    else:
        rotulo = "O mês ficaria com"
        linhas_fim = sum(resumo_import(i, competencia)["n"] or 0 for i in manter)
        valor_fim = sum(float(resumo_import(i, competencia)["v"] or 0) for i in manter)
    oficial = conn.execute(
        "SELECT ROUND(SUM(net_value),2) v FROM fact_unit_summary "
        "WHERE company_id = ? AND competence = ?",
        (company_id, competencia)).fetchone()["v"] or 0
    print(f"{rotulo} {linhas_fim} linha(s) · {money(valor_fim).strip()}")
    if oficial:
        print(f"Resumo por unidade (oficial): {money(oficial).strip()}   "
              f"({100 * (float(valor_fim) / oficial - 1):+.0f}%)")
    print()

if aplicar and total_linhas:
    backend.invalidate_crm_cache(company_id)
    print("Cache limpo. Reinicie o serviço e confira os números.")
elif not aplicar and total_linhas:
    print("Nada foi alterado. Para remover, repita o comando com --aplicar no fim.")

conn.close()
