"""
Remove do faturamento tudo que UMA importação trouxe.

Uso no servidor:
    # ver o que seria removido (não altera nada)
    /srv/passini/venv/crm/bin/python /srv/passini/apps/crm-comercial/limpar_import.py 88

    # remover de verdade
    /srv/passini/venv/crm/bin/python /srv/passini/apps/crm-comercial/limpar_import.py 88 --aplicar

Serve para desfazer um arquivo que não devia ter entrado: um relatório na pasta
errada, ou uma reimportação manual por cima do que os diários já traziam.

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

aplicar = "--aplicar" in sys.argv
ids = [int(a) for a in sys.argv[1:] if a.isdigit()]
# --mes 2026-08 (pode repetir) limita a remoção a certas competências
meses = [a for a in sys.argv[1:] if len(a) == 7 and a[4] == "-"]

conn = backend.get_connection()
company_id = conn.execute("SELECT id FROM companies LIMIT 1").fetchone()["id"]


def money(v):
    return f"R$ {float(v or 0):>15,.2f}"


print(f"Banco: {backend.DB_PATH}\n")

if not ids:
    print("Informe o número da importação. As do faturamento detalhado:\n")
    print(f"   {'IMPORT':<8}{'QUANDO':<22}{'LINHAS':>9}{'VALOR':>20}{'POR LINHA':>12}")
    for r in conn.execute(
        """
        SELECT d.import_id, MAX(i.imported_at) quando, COUNT(*) n,
               ROUND(SUM(d.net_value), 2) v
        FROM fact_sales_detail d LEFT JOIN imports i ON i.id = d.import_id
        WHERE d.company_id = ? GROUP BY d.import_id ORDER BY quando DESC LIMIT 40
        """, (company_id,)).fetchall():
        por_linha = float(r["v"] or 0) / (r["n"] or 1)
        # O valor por linha denuncia o arquivo errado: os diários ficam todos na
        # mesma faixa e o consolidado por cliente destoa em várias vezes.
        marca = "  <<< destoa" if por_linha > 400 else ""
        print(f"   {str(r['import_id']):<8}{str(r['quando'])[:19]:<22}{r['n']:>9}"
              f"{money(r['v'])}{por_linha:>12.2f}{marca}")
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

if aplicar and total_linhas:
    backend.invalidate_crm_cache(company_id)
    print("Cache limpo. Reinicie o serviço e confira os números.")
elif not aplicar and total_linhas:
    print("Nada foi alterado. Para remover, repita o comando com --aplicar no fim.")

conn.close()
