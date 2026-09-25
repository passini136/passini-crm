"""
Cadastro de pessoas: duplicidade e quem o sistema considera desligado.

Uso:
    # panorama da bagunça
    /srv/passini/venv/crm/bin/python /srv/passini/apps/crm-comercial/diag_pessoas_duplicadas.py

    # investigar uma pessoa
    /srv/passini/venv/crm/bin/python /srv/passini/apps/crm-comercial/diag_pessoas_duplicadas.py marcelo

O mesmo vendedor aparece em people_records com vários sufixos — "(VENDAS)",
"(TELEVENDAS)", "(VENDAS NAC)", sem sufixo. O código trata todos como a mesma
pessoa (person_key ignora o que está entre parênteses), mas quem edita pela
tela vê quatro linhas parecidas e não sabe qual mexer. Foi assim que um
desligamento "feito" não surtiu efeito nenhum.

A seção 2 responde a pergunta prática: por que fulano ainda aparece na Missão
do Dia? Ela aplica a MESMA regra do painel, então o que ela disser é o que a
tela faz.

Não altera nada.
"""
import os
import sys
from collections import defaultdict
from datetime import date
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
procurado = backend.normalize_upper(backend.strip_accents(" ".join(sys.argv[1:]).strip()))
hoje = date.today().isoformat()

print(f"Banco: {backend.DB_PATH}")
print(f"Hoje: {hoje}\n")

# ── Carrega tudo indexado pela chave da pessoa ──────────────────────────────
registros = defaultdict(list)
for r in conn.execute(
    "SELECT person_name, role_classification, base_unit, valid_from, valid_to "
    "FROM people_records WHERE company_id = ? ORDER BY person_name, valid_from",
        (company_id,)).fetchall():
    if r["person_name"]:
        registros[backend.person_key(r["person_name"])].append(dict(r))

# SEM filtro por company_id, igual ao backend: há conta com company_id nulo ou
# diferente, e filtrar fazia a conta sumir do diagnóstico — dando a impressão
# de que a pessoa não tinha login quando tinha.
contas = defaultdict(list)
for r in conn.execute(
    "SELECT username, full_name, linked_person_name, role, is_active, company_id "
    "FROM users").fetchall():
    for nome in (r["linked_person_name"], r["full_name"]):
        if nome:
            contas[backend.person_key(nome)].append(dict(r))

# ── 1. Duplicidade ──────────────────────────────────────────────────────────
print("1) PESSOAS COM MAIS DE UM CADASTRO")
duplicados = {k: v for k, v in registros.items() if len(v) > 1}
print(f"   {len(duplicados)} de {len(registros)} pessoas têm cadastro repetido\n")
if duplicados:
    print(f"   {'PESSOA':<34}{'CADASTROS':>10}{'GRAFIAS DIFERENTES':>21}")
    piores = sorted(duplicados.items(), key=lambda kv: -len(kv[1]))[:15]
    for chave, v in piores:
        grafias = len({x["person_name"] for x in v})
        print(f"   {chave[:33]:<34}{len(v):>10}{grafias:>21}")
    print("\n   Repetido não quebra o cálculo — person_key trata como a mesma")
    print("   pessoa. O risco é humano: editar uma linha achando que resolveu.")

# ── 2. Quem o painel considera desligado, e por quê ─────────────────────────
# Reproduz a regra do compute_team_activity_today: vigência encerrada ANTES de
# hoje, ou conta de acesso inativa. Se aqui disser "aparece", a tela mostra.
print("\n2) SITUAÇÃO NA MISSÃO DO DIA")
alvos = [k for k in registros if not procurado or procurado in k]
if procurado and not alvos:
    print(f"   Ninguém com '{procurado}' no cadastro.")
for chave in sorted(alvos)[: (60 if procurado else 0) or len(alvos)]:
    v = registros[chave]
    if not procurado and not any("VENDEDOR" in backend.normalize_upper(
            x["role_classification"] or "") for x in v):
        continue
    fins = [str(x["valid_to"])[:10] for x in v if x["valid_to"]]
    fim = max(fins) if fins else ""
    # Só conta como saída quando TODAS as vigências terminaram — vigência
    # aberta em qualquer grafia significa que a pessoa continua na casa.
    saiu_vigencia = bool(fins) and len(fins) == len(v) and fim < hoje
    minhas_contas = contas.get(chave, [])
    conta_inativa = bool(minhas_contas) and all(
        not c["is_active"] for c in minhas_contas)
    fora = saiu_vigencia or conta_inativa

    if not procurado and not fora:
        continue   # panorama mostra só quem está fora; com nome, mostra tudo

    print(f"\n   {chave}")
    for x in v:
        print(f"      cadastro: {x['person_name'][:40]:<42}"
              f"{x['valid_from']} → {x['valid_to'] or 'aberto'}"
              f"  [{x['base_unit'] or '—'}]")
    if minhas_contas:
        for c in minhas_contas:
            estado = "ATIVA" if c["is_active"] else "INATIVA"
            emp = "" if c["company_id"] == company_id else f"  ⚠ company_id={c['company_id']}"
            print(f"      conta...: {c['username'][:40]:<42}{estado}  ({c['role']}){emp}")
    else:
        print("      conta...: nenhuma conta de acesso vinculada")
    if fora:
        motivo = ("vigência encerrada" if saiu_vigencia else "conta desativada")
        print(f"      >> FORA da Missão do Dia ({motivo})")
    else:
        pendencias = []
        if not fins:
            pendencias.append("nenhuma vigência tem data de saída")
        elif len(fins) != len(v):
            pendencias.append(f"{len(v) - len(fins)} cadastro(s) sem data de saída")
        elif fim >= hoje:
            pendencias.append(f"sai só em {fim}")
        if minhas_contas and not conta_inativa:
            pendencias.append("conta de acesso ainda ativa")
        print(f"      >> APARECE na Missão do Dia — {'; '.join(pendencias) or 'ativo'}")

if not procurado:
    print("\n   (Acima, só quem o sistema considera desligado. Para investigar")
    print("    alguém específico, rode com o nome: ... diag_pessoas_duplicadas.py marcelo)")

# ── 3. Vigências impossíveis ────────────────────────────────────────────────
# Saída antes da entrada não é só feio: build_seller_unit_map procura o mês
# DENTRO do período, e num período invertido nenhum mês casa. A pessoa fica sem
# unidade em toda competência — e "sem unidade" já causou problema em carteira,
# meta e ranking nesta base.
print("\n3) VIGÊNCIAS COM PERÍODO INVERTIDO")
# SÓ o período invertido é defeito.
#
# A primeira versão desta seção também acusava "entrada em 2000-03-01" como
# problema e dizia que isso quebrava o casamento de unidade. Não quebra: a
# busca procura o mês DENTRO do período (valid_from <= mês <= valid_to), e
# entrada antiga casa normalmente — é marcador de "está aqui desde sempre" da
# carga inicial. O JOSE LUIS XAVIER RAMOS, gerente ativo, tem entrada em 2000 e
# funciona. Acusar isso mandaria corrigir 13 cadastros à toa.
invertidos = []
antigos = 0
for chave, v in registros.items():
    for x in v:
        ini = str(x["valid_from"] or "")[:10]
        fim = str(x["valid_to"] or "")[:10]
        if fim and ini and fim < ini:
            invertidos.append((x, ini, fim))
        elif ini and ini < "2015-01-01":
            antigos += 1

if not invertidos:
    print("   Nenhuma. Todas as vigências têm entrada antes da saída.")
else:
    print(f"   {len(invertidos)} registro(s) com saída ANTES da entrada:\n")
    for x, ini, fim in invertidos:
        print(f"   {x['person_name'][:44]:<46}{ini} → {fim}")
    print("\n   >> Corrigir no cadastro. Período invertido não casa com mês")
    print("      nenhum: se a pessoa ainda estiver ativa, ela fica SEM UNIDADE")
    print("      em toda competência, o que afeta carteira, meta e ranking.")
    print("      Nos casos acima, se todos já estão desligados, o efeito hoje")
    print("      é nenhum — mas o cadastro errado volta a incomodar se a")
    print("      pessoa for recontratada.")

if antigos:
    print(f"\n   ({antigos} cadastro(s) com entrada anterior a 2015 — provável")
    print("    marcador de 'desde sempre' da carga inicial. NÃO é problema:")
    print("    entrada antiga casa com qualquer mês. Só atrapalha a leitura.)")

conn.close()
