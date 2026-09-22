"""
Por que a cidade escolhida não devolve empresa nenhuma?

Uso:
    /srv/passini/venv/crm/bin/python /srv/passini/apps/crm-comercial/diag_base_leads.py
    /srv/passini/venv/crm/bin/python /srv/passini/apps/crm-comercial/diag_base_leads.py "capao da canoa"

A base fria tem a cidade como veio do arquivo — com acento. O filtro da tela
tirava o acento antes de comparar, então "CAPAO DA CANOA" era confrontado com
"CAPÃO DA CANOA" e nunca casava. Este diagnóstico mostra as duas grafias lado a
lado e conta quantas empresas existem em cada situação.

O que conferir: se a cidade aparecer aqui com empresas em NOVO e a tela disser
"nenhuma empresa", o problema é o filtro. Se aparecer 0 em NOVO, a base
realmente não tem o que mostrar — e aí a conversa é outra.

Não altera nada.
"""
import os
import sys
import unicodedata
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
procurado = " ".join(sys.argv[1:]).strip()

print(f"Banco: {backend.DB_PATH}\n")

total = conn.execute(
    "SELECT COUNT(*) c FROM prospect_leads WHERE company_id = ?", (company_id,)
).fetchone()["c"]
print(f"1) A BASE TEM {total} EMPRESA(S)")
for r in conn.execute(
    "SELECT status, COUNT(*) c FROM prospect_leads WHERE company_id = ? "
    "GROUP BY status ORDER BY c DESC", (company_id,)).fetchall():
    print(f"   {r['status']:<14}{r['c']:>8}")

# ── 2. A grafia da cidade ───────────────────────────────────────────────────
# O ponto do bug: comparar com acento de um lado e sem do outro.
print("\n2) CIDADES COM ACENTO NO CADASTRO")
com_acento = [
    r for r in conn.execute(
        "SELECT cidade, COUNT(*) c FROM prospect_leads WHERE company_id = ? "
        "AND TRIM(COALESCE(cidade,'')) <> '' GROUP BY cidade ORDER BY c DESC",
        (company_id,)).fetchall()
    if unicodedata.normalize("NFD", r["cidade"] or "") != (r["cidade"] or "")
]
print(f"   {len(com_acento)} cidade(s) têm acento — todas quebravam no filtro antigo.")
for r in com_acento[:12]:
    sem = backend.normalize_upper(backend.strip_accents(r["cidade"]))
    print(f"   {r['cidade']:<28}→ filtro mandava '{sem}'  ({r['c']} empresas)")

# ── 3. A cidade que o Felipe procurou ───────────────────────────────────────
if procurado:
    alvo = backend.normalize_upper(backend.strip_accents(procurado))
    print(f"\n3) '{procurado.upper()}' NA BASE")
    linhas = conn.execute(
        "SELECT cidade, status, COUNT(*) c FROM prospect_leads "
        "WHERE company_id = ? AND sem_acento(cidade) = ? "
        "GROUP BY cidade, status ORDER BY cidade, c DESC", (company_id, alvo)).fetchall()
    if not linhas:
        print("   Nenhuma empresa. A base realmente não tem essa cidade —")
        print("   confira a grafia no arquivo que foi importado.")
    else:
        print(f"   {'GRAFIA GRAVADA':<28}{'STATUS':<14}{'QTD':>6}")
        for r in linhas:
            print(f"   {r['cidade']:<28}{r['status']:<14}{r['c']:>6}")
        # A régua da tela esconde quem já foi dado como perdido.
        perdidos = conn.execute(
            "SELECT COUNT(*) c FROM prospect_leads l WHERE l.company_id = ? "
            "AND sem_acento(l.cidade) = ? AND l.status = 'NOVO' "
            "AND EXISTS (SELECT 1 FROM prospects pp WHERE pp.company_id = l.company_id "
            "            AND pp.status = 'PERDIDO' AND pp.document_digits = l.cnpj)",
            (company_id, alvo)).fetchone()["c"]
        novos = sum(r["c"] for r in linhas if r["status"] == "NOVO")
        print(f"\n   Disponíveis de verdade: {novos - perdidos}")
        print(f"   ({novos} em NOVO menos {perdidos} já dados como PERDIDO no funil)")
        if novos - perdidos > 0:
            print("   >> Havia o que mostrar. A tela vazia era o filtro, não a base.")

# ── 4. O número que não mudava ──────────────────────────────────────────────
print("\n4) O '44 JÁ ASSUMIDAS'")
adotados = conn.execute(
    "SELECT COUNT(*) c FROM prospect_leads WHERE company_id = ? AND status = 'ADOTADO'",
    (company_id,)).fetchone()["c"]
print(f"   {adotados} na empresa toda — era esse número fixo que aparecia em todo filtro.")
print("   Agora a tela mostra também quantas já foram assumidas DENTRO do filtro atual.")

conn.close()
