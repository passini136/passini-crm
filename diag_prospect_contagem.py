"""
Por que o número no selo de status não bate com a lista?

Uso:
    /srv/passini/venv/crm/bin/python /srv/passini/apps/crm-comercial/diag_prospect_contagem.py

Relato: o selo "Cadastrado" mostrava (3) e, ao clicar, a lista trouxe mais que
três. Número que não bate com a própria lista ao lado é pior que número
ausente: quem usa para de confiar na tela inteira, inclusive nas partes certas.

CAUSA ENCONTRADA no código, antes de rodar isto: o selo contava sobre uma
lista carregada com LIMIT 5000, e a ordenação dessa lista põe CADASTRADO e
PERDIDO no fim. Passando de 5.000 prospects, eram exatamente esses dois status
que o corte comia — o selo dizia (3) e a lista trazia o que existe de verdade.
A contagem passou a ser feita com COUNT(*) no banco, sem teto.

Este diagnóstico CONFIRMA a correção: roda a contagem e a lista lado a lado,
com o mesmo usuário, e os dois têm de bater em todos os status. Serve também
de rede para o futuro, porque a regra de permissão agora é compartilhada entre
as duas consultas e qualquer divergência aparece aqui.

Não altera nada.
"""
import os
import sys
from collections import Counter
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

print(f"Banco: {backend.DB_PATH}\n")

# ── 1. Quantos prospects existem, cru ───────────────────────────────────────
print("1) NA TABELA, SEM PASSAR POR FUNÇÃO NENHUMA")
print(f"   {'STATUS':<16}{'PROSPECTS':>11}")
cru = {}
for r in conn.execute(
    "SELECT status, COUNT(*) n FROM prospects WHERE company_id = ? GROUP BY status",
        (company_id,)).fetchall():
    cru[r["status"]] = r["n"]
    print(f"   {str(r['status']):<16}{r['n']:>11}")
print(f"   {'TOTAL':<16}{sum(cru.values()):>11}")

# ── 2. O JOIN duplica? ──────────────────────────────────────────────────────
# Mesmo teste que pegou a duplicação na tela de Marcas: a contagem com o JOIN
# tem de ser igual à contagem sem ele.
print("\n2) O JOIN COM O CADASTRO DUPLICA LINHA?")
sem_join = conn.execute(
    "SELECT COUNT(*) n FROM prospects WHERE company_id = ?", (company_id,)).fetchone()["n"]
com_join = conn.execute(
    """SELECT COUNT(*) n FROM prospects p
       LEFT JOIN crm_client_profiles c
         ON TRIM(c.document_number) = TRIM(p.document_number)
        AND c.company_id = p.company_id
       WHERE p.company_id = ?""", (company_id,)).fetchone()["n"]
print(f"   Sem JOIN: {sem_join}   ·   Com JOIN: {com_join}   ·   diferença: {com_join - sem_join}")
if com_join > sem_join:
    print("   >> DUPLICA. Um prospect casa com mais de um cadastro — a lista mostra")
    print("      a mesma oficina duas vezes e o selo, que conta outra coisa, não bate.")
    print("\n   Quem duplica:")
    for r in conn.execute(
        """SELECT p.company_name, p.document_number, COUNT(*) n FROM prospects p
           LEFT JOIN crm_client_profiles c
             ON TRIM(c.document_number) = TRIM(p.document_number)
            AND c.company_id = p.company_id
           WHERE p.company_id = ? GROUP BY p.id HAVING n > 1
           ORDER BY n DESC LIMIT 10""", (company_id,)).fetchall():
        print(f"      {str(r['company_name'])[:38]:<40}{str(r['document_number'])[:18]:<20}{r['n']}x")
else:
    print("   >> Sem duplicação por aqui.")

# ── 3. Funil contra lista, com o MESMO usuário ──────────────────────────────
print("\n3) FUNIL (o número do selo) CONTRA A LISTA (o que aparece ao clicar)")
usuarios = conn.execute(
    "SELECT * FROM users WHERE company_id = ? ORDER BY id", (company_id,)).fetchall()
for u in usuarios[:4]:
    nome = u["full_name"] if "full_name" in u.keys() else u["username"]
    escopo = backend.data_scope_for_user(conn, u)
    funil = backend.prospect_funnel(conn, company_id, u)
    print(f"\n   Usuário: {str(nome)[:28]:<30} escopo={escopo}")
    print(f"   {'STATUS':<16}{'SELO (funil)':>14}{'LISTA (tela)':>14}{'':>4}")
    for s in backend.PROSPECT_STATUSES:
        sid = s["id"]
        no_selo = funil["byStatus"].get(sid, 0)
        # A lista da tela: mesma chamada que o endpoint faz ao clicar no selo.
        lista = backend.list_prospects(conn, company_id, u, status=sid)
        marca = "" if no_selo == len(lista) else "  ← DIVERGE"
        print(f"   {sid:<16}{no_selo:>14}{len(lista):>14}{marca}")
        if no_selo != len(lista):
            chaves = Counter(p.get("id") for p in lista)
            repetidos = [k for k, v in chaves.items() if v > 1]
            if repetidos:
                print(f"      {len(repetidos)} prospect(s) repetido(s) NA LISTA "
                      f"— é duplicação, não contagem.")
            else:
                print("      Sem repetição na lista: a diferença é de RECORTE "
                      "(limite, encerrados ou escopo).")

# ── 4. O limite corta? ──────────────────────────────────────────────────────
print("\n4) O LIMITE CORTA ALGUMA LISTA?")
print("   O funil usa limite 5.000 e inclui encerrados; a lista da tela usa 500.")
total = sum(cru.values())
print(f"   Prospects na base: {total}")
if total > 500:
    print("   >> ACIMA DE 500. A lista da tela pode estar cortando, e aí o selo")
    print("      (que conta tudo) fica MAIOR que a lista — não menor.")
else:
    print("   >> Abaixo de 500: o limite não explica diferença nenhuma.")

print("\n   >> Leitura: selo MAIOR que a lista é corte ou encerrado de fora;")
print("      selo MENOR que a lista é duplicação. O relato foi selo menor.")

conn.close()
