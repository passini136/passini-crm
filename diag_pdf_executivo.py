"""
O PDF executivo é gerado a partir do banco DE VERDADE?

Uso (venv do CRM, que é quem tem reportlab):
    /srv/passini/venv/crm/bin/python /srv/passini/apps/crm-comercial/diag_pdf_executivo.py

POR QUE ESTE DIAGNÓSTICO EXISTE

O PDF quebrou no primeiro download com TypeError: unhashable type: 'dict'. A
causa foi eu ter escrito a função de cor esperando que o farol fosse a string
"bom"/"alerta"/"ruim". O farol do sistema nunca foi isso: é um dicionário com
{"level": "good"|"warn"|"bad"|"neutral"}. Eu inventei um vocabulário em vez de
ler o que o dashboard devolve.

O teste que fiz antes de entregar não pegou porque EU MONTEI OS DADOS DE
TESTE — e dado que eu invento tem a forma que eu imaginei, não a forma real.
Teste assim só confirma o que já estava na minha cabeça, inclusive o erro.

Este diagnóstico faz o contrário: puxa o dashboard real, do banco real, e
gera o PDF. Se a forma do dado mudar de novo — campo que vira None, unidade
nova sem meta, farol com nível inédito — ele falha aqui, no terminal, e não
na mão de quem clicou em baixar.

Grava o PDF em /tmp para conferência visual. NÃO altera o banco.
"""
import os
import sys
import traceback
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

# ── 1. A forma do farol, antes de usar ──────────────────────────────────────
# O erro que derrubou o download foi de FORMA, não de valor. Então a forma é
# a primeira coisa que se confere.
print("1) QUE FORMA TEM O FAROL NO DADO REAL")
filtros = backend.build_filters_from_query({})
data = backend.get_dashboard_data(conn, company_id, filtros)
s = data.get("summary") or {}
farol = s.get("farol") or {}
print(f"   Competência: {data.get('primaryCompetence')}")
if not farol:
    print("   >> summary.farol veio VAZIO. O PDF sairia todo preto, sem erro —")
    print("      que é pior que quebrar, porque ninguém percebe.")
for chave, valor in farol.items():
    tipo = type(valor).__name__
    nivel = valor.get("level") if isinstance(valor, dict) else valor
    cor = backend._pdf_cor_farol(valor)
    print(f"   {chave:<24}{tipo:<8}level={str(nivel):<10}cor={cor}")
print("   >> Tem de ser dict com level em good/warn/bad/neutral. String aqui")
print("      significa que alguém mudou evaluate_farol e o PDF vai sair preto.")

# ── 2. As unidades, uma a uma ───────────────────────────────────────────────
# A tabela por unidade formata nove colunas numéricas. Basta uma unidade com
# campo faltando para a formatação estourar — e a Zona Norte, que não tem meta
# lançada, é a candidata natural.
print("\n2) CADA UNIDADE TEM OS CAMPOS QUE A TABELA FORMATA")
unidades = data.get("unitPerformance") or []
campos = ["unitName", "revenueNet", "revenueGoal", "goalAttainmentPct",
          "projectedRevenue", "returnRatioPct", "marginAverage",
          "qtySold", "ticketPerPiece"]
print(f"   {len(unidades)} linha(s) em unitPerformance")
print(f"   {'UNIDADE':<16}" + "".join(f"{c[:9]:>11}" for c in campos[1:]))
problemas = 0
for u in unidades:
    nome = backend.normalize_whitespace(u.get("unitName")) or "(sem nome)"
    marcas = []
    for c in campos[1:]:
        v = u.get(c)
        marcas.append("—" if v is None else ("0" if not v else "ok"))
    faltando = [c for c in campos if c not in u]
    if faltando:
        problemas += 1
    print(f"   {nome[:15]:<16}" + "".join(f"{m:>11}" for m in marcas)
          + ("   FALTA: " + ", ".join(faltando) if faltando else ""))
print("   >> '—' é None: formata como zero e não quebra. Campo AUSENTE, sim,")
print("      quebra — e é o que a coluna FALTA denuncia.")

# ── 3. Gerar o PDF de verdade ───────────────────────────────────────────────
print("\n3) GERANDO O PDF COM ESTE DADO")
destino = Path("/tmp/diag_executivo.pdf")
try:
    conteudo = backend.export_executivo_pdf(data)
    destino.write_bytes(conteudo)
    print(f"   OK · {len(conteudo) / 1024:.1f} KB · {destino}")
except Exception:
    print("   >> QUEBROU. Este é exatamente o erro que o usuário veria como")
    print("      'Algo deu errado' no download:\n")
    traceback.print_exc()
    conn.close()
    sys.exit(1)

# ── 4. Conferir o que saiu ──────────────────────────────────────────────────
print("\n4) O QUE SAIU DENTRO DO ARQUIVO")
try:
    from pypdf import PdfReader
except ImportError:
    try:
        from PyPDF2 import PdfReader  # type: ignore
    except ImportError:
        PdfReader = None  # type: ignore
if PdfReader is None:
    print("   (pypdf não instalado — pulando a leitura; o arquivo foi gerado)")
else:
    leitor = PdfReader(str(destino))
    texto = "\n".join((p.extract_text() or "") for p in leitor.pages)
    print(f"   Páginas: {len(leitor.pages)}")
    if len(leitor.pages) > 1:
        print("   >> MAIS DE UMA PÁGINA. O PDF foi desenhado para caber numa só;")
        print("      com mais unidades as larguras das colunas precisam mudar.")
    esperados = [backend.normalize_whitespace(u.get("unitName"))
                 for u in unidades if backend.normalize_whitespace(u.get("unitName"))]
    sumidas = [u for u in esperados if u not in texto]
    print(f"   Unidades no PDF: {len(esperados) - len(sumidas)} de {len(esperados)}")
    if sumidas:
        print(f"   >> SUMIRAM: {', '.join(sumidas)}")
    print(f"   Linha TOTAL presente: {'sim' if 'TOTAL' in texto.upper() else 'NÃO'}")
    comp = str(data.get("primaryCompetence") or "")
    print(f"   Competência impressa: {'sim' if comp and comp in texto else 'NÃO'}")

print("\n   Abra /tmp/diag_executivo.pdf para conferir o visual.")
conn.close()
