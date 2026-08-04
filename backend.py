from __future__ import annotations

import csv
import cgi
import hashlib
import hmac
import io
import json
import math
import os
import re
import secrets
import shutil
import sqlite3
import sys
import tempfile
import functools
import threading
import time
import traceback
import unicodedata
from collections import Counter, defaultdict
from contextlib import closing
from dataclasses import dataclass
from datetime import date, datetime, timedelta
from decimal import Decimal, InvalidOperation
from http import HTTPStatus
from http.cookies import SimpleCookie
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any
from urllib.parse import parse_qs, urlparse
from zoneinfo import ZoneInfo

import openpyxl
from openpyxl import Workbook
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle


ROOT_DIR = Path(__file__).resolve().parent
LEGACY_APPDATA_DIR = Path(os.environ.get("LOCALAPPDATA", str(ROOT_DIR / "runtime_data"))) / "PassiniDashboard"
STATIC_DIR = ROOT_DIR / "static"
DEFAULT_COMPANY = "Passini Distribuidora de Autopeças"
DEFAULT_ADMIN_USER = os.environ.get("PASSINI_ADMIN_USER", "admin")
# Semente usada APENAS na criação do banco. Pode ser definida em crm.env
# (PASSINI_ADMIN_PASSWORD). Não é exibida em nenhuma tela.
DEFAULT_ADMIN_PASSWORD = os.environ.get("PASSINI_ADMIN_PASSWORD", "Passini@2026")

# ── Cache para competências fechadas (não mudam após importação) ─────────────
import threading as _threading
_summary_cache: dict[str, tuple[float, dict]] = {}
_summary_cache_lock = _threading.Lock()
_SUMMARY_CACHE_TTL_CLOSED = 3600  # 1h para meses fechados
_SUMMARY_CACHE_TTL_OPEN   = 30    # 30s para mês corrente

def _summary_cache_key(company_id: int, competence: str, filters: dict) -> str:
    import json
    relevant = {k: v for k, v in (filters or {}).items() if k in ("unit_name", "seller_name", "city_name", "allowed_units")}
    return f"{company_id}:{competence}:{json.dumps(relevant, sort_keys=True)}"

def _cached_single_competence_summary(conn, company_id, competence, filters=None):
    """Wraps single_competence_summary com cache por competência fechada."""
    import time
    if not competence:
        return {}
    today = date.today()
    current_comp = today.strftime("%Y-%m")
    is_open = (competence >= current_comp)
    ttl = _SUMMARY_CACHE_TTL_OPEN if is_open else _SUMMARY_CACHE_TTL_CLOSED
    key = _summary_cache_key(company_id, competence, filters or {})
    with _summary_cache_lock:
        if key in _summary_cache:
            ts, cached = _summary_cache[key]
            if time.monotonic() - ts < ttl:
                return cached
    result = single_competence_summary(conn, company_id, competence, filters)
    with _summary_cache_lock:
        _summary_cache[key] = (time.monotonic(), result)
    return result

# ─────────────────────────────────────────────────────────────────────────────

SESSION_COOKIE = "passini_session"
SESSION_TTL_HOURS = 24
# Host/porta configuráveis por variável de ambiente (padrão preserva o comportamento local no Windows).
# No servidor Linux, definir em crm.env: PASSINI_CRM_HOST e PASSINI_CRM_PORT.
DEFAULT_PORT = int(os.environ.get("PASSINI_CRM_PORT", "8876"))
DEFAULT_HOST = os.environ.get("PASSINI_CRM_HOST", "0.0.0.0")
APP_TIMEZONE = ZoneInfo("America/Sao_Paulo")

PASSINI_MAPPING_WORKBOOK = Path(
    r"C:\Users\felip\OneDrive\PASSINI\CARTEIRA DE CLIENTES\UNIDADE X VENDEDOR E CIDADE X UNIDADE.xlsx"
)
SAMPLE_FILES = {
    "faturamento_detalhado": Path(r"C:\Users\felip\Downloads\030-relatorioFaturamento detalhado.csv"),
    "custo_vendedor": Path(r"C:\Users\felip\Downloads\030-relatorioCustoVenda vendedor consolidado.csv"),
    "custo_unidade": Path(r"C:\Users\felip\Downloads\030-relatorioCustoVenda unidade.csv"),
}
SAMPLE_CLIENTS_FILE = Path(r"C:\Users\felip\Downloads\030-relatorioPessoas.csv")


def resolve_data_dir() -> Path:
    # PASSINI_CRM_DATA: diretorio persistente do banco no servidor (ex.: /srv/passini/data/crm).
    # Tem prioridade. No Windows, se nao definida, mantem o comportamento anterior.
    _env_data = os.environ.get("PASSINI_CRM_DATA")
    candidates = [
        Path(_env_data) if _env_data else None,
        Path(os.environ.get("LOCALAPPDATA", "")) / "PassiniDashboardV2" if os.environ.get("LOCALAPPDATA") else None,
        Path(tempfile.gettempdir()) / "PassiniDashboardV2",
        ROOT_DIR / "runtime_data",
    ]
    for candidate in candidates:
        if candidate and (candidate / "passini_dashboard.db").exists():
            return candidate
    for candidate in candidates:
        if not candidate:
            continue
        try:
            candidate.mkdir(parents=True, exist_ok=True)
            probe = candidate / ".write_probe"
            probe.write_text("ok", encoding="utf-8")
            probe.unlink(missing_ok=True)
            return candidate
        except OSError:
            continue
    return ROOT_DIR


DATA_DIR = resolve_data_dir()
DB_PATH = DATA_DIR / "passini_dashboard.db"

AUTO_IMPORT_BASE = ROOT_DIR / "auto-import"
AUTO_IMPORT_INTERVAL = 3600  # 1 hora (era 5 min — reduzia risco de reimport em loop)
# A base de clientes do Alfa vem em vários arquivos complementares. Só importamos
# quando nenhum arquivo foi modificado nos últimos N segundos, evitando processar
# a base pela metade enquanto a segunda exportação ainda está sendo copiada.
CRM_CLIENTS_SETTLE_SECONDS = 120
# Logs de depuração do dashboard (projeção e comparativos). Desligados por padrão —
# eram impressos a cada cálculo, poluindo o journal. Ative com PASSINI_DEBUG_DASHBOARD=1
DASHBOARD_DEBUG_LOG = os.environ.get("PASSINI_DEBUG_DASHBOARD", "").strip() in {"1", "true", "yes"}
AUTO_IMPORT_FOLDERS = [
    {"folder": "faturamento",  "scope": "sales", "label": "Faturamento Detalhado"},
    {"folder": "custo-venda",  "scope": "cost",  "label": "Custo de Venda"},
    # CRM separado em duas pastas — cada base importa de forma independente
    {"folder": "crm/clientes", "scope": "crm_clients",
     "label": "CRM · Cadastro de Clientes",
     "hint": "Base do Alfa, sem competência. Coloque TODAS as exportações juntas (a base vem "
             "dividida em 2 arquivos) — elas são importadas como uma só e substituem a base "
             "anterior. Atualizar 1x ao dia."},
    {"folder": "crm/faturamento-consolidado", "scope": "crm_summary",
     "label": "CRM · Faturamento Consolidado",
     "hint": "Competência obrigatória no nome do arquivo, ex: 2026-07_faturamento_cliente.csv"},
    {"folder": "devolucao-garantia", "scope": "warranty",
     "label": "Devolução em Garantia",
     "hint": "Relatório de devoluções em garantia. A competência sai da data de cada devolução — "
             "não precisa do mês no nome do arquivo."},
]

# Ordem canônica das unidades (inclui unidades sem dados ainda, ex: Zona Norte)
CANONICAL_UNITS: list[str] = [
    "MATRIZ",
    "LAJEADO",
    "PELOTAS",
    "ZONA SUL",
    "ZONA NORTE",
    "XANGRILA",
]

UNIT_NORMALIZATION = {
    # Matriz
    "01 MATRIZ": "MATRIZ",
    "MATRIZ": "MATRIZ",
    # Lajeado
    "02 LAJEADO": "LAJEADO",
    "LAJEADO": "LAJEADO",
    # Pelotas
    "03 PELOTAS": "PELOTAS",
    "PELOTAS": "PELOTAS",
    # Porto Alegre → renomeada para Zona Sul (Zona Sul assumiu o lugar de POA)
    "04 POA": "ZONA SUL",
    "04 PORTO ALEGRE": "ZONA SUL",
    "04 PORTOALEGRE": "ZONA SUL",
    "PORTO ALEGRE": "ZONA SUL",
    "POA": "ZONA SUL",
    "PORTOALEGRE": "ZONA SUL",   # compatibilidade com dados históricos no banco
    # Zona Sul (novo nome)
    "04 ZONA SUL": "ZONA SUL",
    "ZONA SUL": "ZONA SUL",
    "ZONASUL": "ZONA SUL",
    "POA ZONA SUL": "ZONA SUL",
    # Zona Norte (nova unidade, ainda sem operação)
    "04 ZONA NORTE": "ZONA NORTE",
    "ZONA NORTE": "ZONA NORTE",
    "ZONANORTE": "ZONA NORTE",
    "POA ZONA NORTE": "ZONA NORTE",
    # Xangrila
    "05 XANGRILA": "XANGRILA",
    "05 XANGRI-LA": "XANGRILA",
    "XANGRI LA": "XANGRILA",
    "XANGRI-LA": "XANGRILA",
    "XANGRILÁ": "XANGRILA",
    "XANGRILA": "XANGRILA",
}

# ─────────────────────────────────────────────────────────────────────────────
# Módulos (telas) disponíveis para montar perfis de acesso.
# A ordem aqui define a ordem de exibição na tela de perfis.
# ─────────────────────────────────────────────────────────────────────────────
ACCESS_MODULES: list[dict[str, str]] = [
    # CRM
    {"id": "crm-agenda",     "label": "Missão do Dia",      "group": "CRM"},
    {"id": "crm-clientes",   "label": "Carteira",           "group": "CRM"},
    {"id": "crm-tarefas",    "label": "Tarefas",            "group": "CRM"},
    {"id": "crm-interacao",  "label": "Registrar interação","group": "CRM"},
    {"id": "meu-placar",     "label": "Meu Placar",         "group": "CRM"},
    {"id": "placar-equipe",  "label": "Placar da Equipe",   "group": "CRM"},
    {"id": "biblioteca",     "label": "Biblioteca de Vendas","group": "CRM"},
    {"id": "sem-vendedor",   "label": "Clientes sem Vendedor","group": "CRM"},
    # Resultados
    {"id": "executivo",      "label": "Executivo",          "group": "Resultados"},
    {"id": "vendedores",     "label": "Vendedores",         "group": "Resultados"},
    {"id": "unidades",       "label": "Unidades",           "group": "Resultados"},
    {"id": "clientes",       "label": "Clientes",           "group": "Resultados"},
    {"id": "cidades",        "label": "Cidades",            "group": "Resultados"},
    {"id": "descontos",      "label": "Descontos",          "group": "Resultados"},
    {"id": "calendario",     "label": "Calendário",         "group": "Resultados"},
    # Operações
    {"id": "importacoes",    "label": "Importações",        "group": "Operações"},
    {"id": "administracao",  "label": "Administração",      "group": "Operações"},
    {"id": "configuracoes",  "label": "Configurações",      "group": "Operações"},
    {"id": "acessos",        "label": "Usuários e Perfis",  "group": "Operações"},
]
ACCESS_MODULE_IDS = {m["id"] for m in ACCESS_MODULES}

# Escopo de dados que o perfil enxerga
DATA_SCOPES: list[dict[str, str]] = [
    {"id": "todos", "label": "Todas as unidades",
     "hint": "Sem restrição — enxerga a empresa inteira."},
    {"id": "unidade_consolidado", "label": "Unidades vinculadas + consolidado",
     "hint": "Detalhe das unidades do usuário e também os totais da empresa para comparação."},
    {"id": "unidade", "label": "Somente unidades vinculadas",
     "hint": "Restrito às unidades do usuário. Não vê outras unidades nem o consolidado."},
    {"id": "proprio", "label": "Somente a própria carteira",
     "hint": "Vendedor: enxerga apenas os próprios clientes e resultados."},
]
DATA_SCOPE_IDS = {s["id"] for s in DATA_SCOPES}

# Perfis criados automaticamente na primeira execução. is_system impede exclusão,
# mas o conteúdo (telas/escopo) continua editável pela tela.
DEFAULT_ACCESS_PROFILES: list[dict[str, Any]] = [
    {
        "name": "Diretor",
        "description": "Acesso total, incluindo gestão de usuários e perfis.",
        "modules": [m["id"] for m in ACCESS_MODULES],
        "data_scope": "todos",
        "can_manage_users": 1,
    },
    {
        "name": "Administrador",
        "description": "Acesso total, incluindo gestão de usuários e perfis.",
        "modules": [m["id"] for m in ACCESS_MODULES],
        "data_scope": "todos",
        "can_manage_users": 1,
    },
    {
        "name": "Gerente",
        "description": "Gestão da unidade: resultados, carteira e equipe. Sem acesso a configurações.",
        "modules": [
            "crm-agenda", "crm-clientes", "crm-tarefas", "crm-interacao", "placar-equipe", "biblioteca", "sem-vendedor",
            "executivo", "vendedores", "unidades", "clientes", "cidades", "descontos", "calendario",
        ],
        "data_scope": "unidade_consolidado",
        "can_manage_users": 0,
    },
    {
        "name": "Analista",
        "description": "Consulta de resultados e apoio a importações.",
        "modules": [
            "crm-clientes", "executivo", "vendedores", "unidades", "clientes",
            "cidades", "descontos", "calendario", "importacoes",
        ],
        "data_scope": "todos",
        "can_manage_users": 0,
    },
    {
        "name": "Vendedor",
        "description": "Rotina diária de vendas: missão do dia, carteira própria e placar.",
        "modules": ["crm-agenda", "crm-clientes", "crm-tarefas", "crm-interacao", "meu-placar", "biblioteca", "calendario"],
        "data_scope": "proprio",
        "can_manage_users": 0,
    },
]

CSV_FILE_TYPES = {
    "030-relatorioFaturamento detalhado.csv": "faturamento_detalhado",
    "030-relatorioCustoVenda vendedor consolidado.csv": "custo_vendedor",
    "030-relatorioCustoVenda unidade.csv": "custo_unidade",
    "030-relatorioFaturamento conslidado cliente.csv": "faturamento_cliente_consolidado",
    "030-relatorioPessoas.csv": "cadastro_clientes",
    "030-relatorioDevolucao.csv": "devolucao_garantia",
    "01fat.csv": "faturamento_detalhado",
    "02unidade.csv": "custo_unidade",
    "03vendedor.csv": "custo_vendedor",
}
IMPORT_SCOPE_REQUIREMENTS = {
    "full": {"faturamento_detalhado", "custo_vendedor", "custo_unidade"},
    "sales": {"faturamento_detalhado"},
    "cost": {"custo_vendedor", "custo_unidade"},
    "crm": {"cadastro_clientes", "faturamento_cliente_consolidado"},
    # Escopos individuais do CRM — cada base é importada de forma independente
    "crm_clients": {"cadastro_clientes"},
    "crm_summary": {"faturamento_cliente_consolidado"},
    "warranty": {"devolucao_garantia"},
}
IMPORT_SCOPE_LABELS = {
    "full": "pacote completo",
    "sales": "faturamento detalhado",
    "cost": "custo venda",
    "crm": "crm carteira",
    "crm_clients": "cadastro de clientes",
    "crm_summary": "faturamento consolidado por cliente",
    "warranty": "devolução em garantia",
}
IMPORT_SCOPE_TABLES = {
    "faturamento_detalhado": ("fact_sales_detail",),
    "custo_vendedor": ("fact_vendor_summary",),
    "custo_unidade": ("fact_unit_summary",),
    "cadastro_clientes": ("crm_client_profiles",),
    "faturamento_cliente_consolidado": ("crm_client_summary",),
    "devolucao_garantia": ("fact_warranty_returns",),
}
UPLOAD_FIELD_TYPE_OVERRIDES = {
    "cost_unit_file": "custo_unidade",
    "cost_vendor_file": "custo_vendedor",
    "import-cost-unit-file": "custo_unidade",
    "import-cost-vendor-file": "custo_vendedor",
    "sales_file": "faturamento_detalhado",
    "import-sales-file": "faturamento_detalhado",
    "crm_clients_file": "cadastro_clientes",
    "crm_summary_file": "faturamento_cliente_consolidado",
    "import-crm-clients-file": "cadastro_clientes",
    "import-crm-summary-file": "faturamento_cliente_consolidado",
    "warranty_file": "devolucao_garantia",
    "import-warranty-file": "devolucao_garantia",
    "files": None,
}

NATIONAL_AND_RS_HOLIDAYS = {
    2025: [
        ("2025-01-01", "Confraternização Universal"),
        ("2025-03-04", "Carnaval"),
        ("2025-03-05", "Quarta-feira de Cinzas"),
        ("2025-04-18", "Sexta-feira Santa"),
        ("2025-04-21", "Tiradentes"),
        ("2025-05-01", "Dia do Trabalho"),
        ("2025-06-19", "Corpus Christi"),
        ("2025-09-20", "Revolução Farroupilha"),
        ("2025-10-12", "Nossa Senhora Aparecida"),
        ("2025-11-02", "Finados"),
        ("2025-11-15", "Proclamação da República"),
        ("2025-12-25", "Natal"),
    ],
    2026: [
        ("2026-01-01", "Confraternização Universal"),
        ("2026-02-17", "Carnaval"),
        ("2026-02-18", "Quarta-feira de Cinzas"),
        ("2026-04-03", "Sexta-feira Santa"),
        ("2026-04-21", "Tiradentes"),
        ("2026-05-01", "Dia do Trabalho"),
        ("2026-06-04", "Corpus Christi"),
        ("2026-09-20", "Revolução Farroupilha"),
        ("2026-10-12", "Nossa Senhora Aparecida"),
        ("2026-11-02", "Finados"),
        ("2026-11-15", "Proclamação da República"),
        ("2026-12-25", "Natal"),
    ],
}

CRM_CONTACT_TYPES = [
    ("LIGACAO", "Ligacao"),
    ("WHATSAPP", "WhatsApp"),
    ("VISITA", "Visita"),
    ("ORCAMENTO", "Orcamento/Cotacao"),
    ("OUTRO", "Outro"),
]

CRM_CONTACT_RESULTS = [
    ("FALOU_CLIENTE", "Falou com o cliente", 0, 0),
    ("NAO_ATENDEU", "Nao atendeu", 1, 1),
    ("SEM_SUCESSO", "Sem sucesso / nao consegui falar", 0, 0),
    ("PEDIU_RETORNO", "Pediu retorno", 1, 1),
    ("GEROU_ORCAMENTO", "Gerou orcamento", 1, 1),
    ("GEROU_PEDIDO", "Gerou pedido", 0, 0),
    ("SEM_INTERESSE", "Sem interesse", 0, 0),
    ("CLIENTE_FECHADO", "Cliente inativo / fechado", 0, 0),
    ("OUTRO", "Outro", 0, 0),
]

CRM_PRIORITY_ORDER = [
    "REATIVACAO_INATIVO",
    "PRE_INATIVO",
    "SEM_COMPRA_MES",
    "QUEDA_FATURAMENTO",
    "CLIENTE_CLASSE_ALTA",
    "OPORTUNIDADE_MIX",
    "PROSPECCAO_NOVA",
]

CRM_PRIORITY_LABELS = {
    "REATIVACAO_INATIVO": "Reativacao de inativo",
    "PRE_INATIVO": "Pre-inativo",
    "SEM_COMPRA_MES": "Sem compra no mes",
    "QUEDA_FATURAMENTO": "Queda de faturamento",
    "CLIENTE_CLASSE_ALTA": "Cliente classe alta",
    "OPORTUNIDADE_MIX": "Oportunidade de mix",
    "PROSPECCAO_NOVA": "Prospeccao nova",
}


def ensure_dirs() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    STATIC_DIR.mkdir(parents=True, exist_ok=True)


def migrate_legacy_db_if_needed() -> None:
    legacy_db = LEGACY_APPDATA_DIR / "passini_dashboard.db"
    if DB_PATH.exists() or not legacy_db.exists():
        return
    try:
        source = sqlite3.connect(f"file:{legacy_db}?mode=ro", uri=True)
        target = sqlite3.connect(DB_PATH)
        with source, target:
            source.backup(target)
        source.close()
        target.close()
    except sqlite3.Error:
        try:
            shutil.copy2(legacy_db, DB_PATH)
        except OSError:
            pass
    except OSError:
        pass


def now_iso() -> str:
    return datetime.now().isoformat(timespec="seconds")


def today_in_brazil() -> date:
    return datetime.now(APP_TIMEZONE).date()


def dashboard_cutoff_date(today_value: date | None = None) -> date:
    reference_today = today_value or today_in_brazil()
    return reference_today - timedelta(days=1)


def normalize_whitespace(value: str | None) -> str:
    return re.sub(r"\s+", " ", (value or "").strip())


def normalize_upper(value: str | None) -> str:
    return normalize_whitespace(value).upper()


def strip_accents(value: str | None) -> str:
    text = normalize_whitespace(value)
    if not text:
        return ""
    return "".join(char for char in unicodedata.normalize("NFKD", text) if not unicodedata.combining(char))


def normalize_client_key(value: str | None) -> str:
    text = strip_accents(value).upper()
    text = re.sub(r"[^A-Z0-9\s]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def normalize_unit(value: str | None) -> str:
    base = normalize_upper(value)
    return UNIT_NORMALIZATION.get(base, base)


def parse_decimal(value: str | None) -> float:
    if value is None:
        return 0.0
    text = normalize_whitespace(value)
    if not text:
        return 0.0
    if "," in text and "." in text:
        text = text.replace(".", "").replace(",", ".")
    elif "," in text:
        text = text.replace(",", ".")
    try:
        number = float(Decimal(text))
    except (InvalidOperation, ValueError):
        return 0.0
    # Blinda contra "inf"/"nan" vindos do CSV — gravar isso no banco gera JSON inválido
    return number if math.isfinite(number) else 0.0


def parse_int(value: str | None) -> int:
    if value is None:
        return 0
    text = normalize_whitespace(value)
    if not text:
        return 0
    text = text.replace(".", "").replace(",", ".")
    try:
        return int(float(text))
    except ValueError:
        return 0


def parse_datetime_pt(value: str | None) -> datetime | None:
    text = normalize_whitespace(value)
    if not text:
        return None
    for fmt in ("%d/%m/%Y %H:%M:%S", "%d/%m/%Y"):
        try:
            return datetime.strptime(text, fmt)
        except ValueError:
            continue
    return None


def competence_from_date(dt_value: datetime | None) -> str | None:
    if not dt_value:
        return None
    return dt_value.strftime("%Y-%m")


# Nomes aceitos para a coluna de data no faturamento detalhado, em ordem de prioridade.
# A comparação ignora acentos, maiúsculas, espaços e pontuação.
SALES_DATE_COLUMN_CANDIDATES = (
    "DATA EMISSAO", "DT EMISSAO", "EMISSAO", "DATA DA EMISSAO",
    "DATA MOVIMENTO", "DATA MOVIMENTACAO", "DT MOVIMENTO", "MOVIMENTO",
    "DATA", "DATA VENDA", "DT VENDA", "ULT COMPRA", "ULTIMA COMPRA",
)


def _column_lookup_key(value: str | None) -> str:
    """Normaliza um nome de coluna para comparação tolerante."""
    return re.sub(r"[^A-Z0-9]", "", strip_accents(value).upper())


def find_sales_date_value(row: dict[str, str]) -> str | None:
    """Retorna o valor da coluna de data do faturamento, tolerando variações de nome.

    O relatório do Alfa nem sempre exporta o cabeçalho igual (acento em EMISSÃO,
    caixa diferente, ponto em ULT.COMPRA). Buscar pelo nome exato fazia a
    importação falhar com 'não foi possível determinar a competência'.
    """
    if not row:
        return None
    normalized = {_column_lookup_key(k): v for k, v in row.items() if k}
    for candidate in SALES_DATE_COLUMN_CANDIDATES:
        value = normalized.get(_column_lookup_key(candidate))
        if normalize_whitespace(value):
            return value
    # Último recurso: qualquer coluna cujo nome contenha DATA/EMISSAO e tenha valor
    for key, value in normalized.items():
        if ("DATA" in key or "EMISSAO" in key) and normalize_whitespace(value):
            return value
    return None


def parse_excel_serial_date(value: str | None) -> datetime | None:
    """Converte número de série do Excel em data (ex.: '45659,3378' -> 02/01/2025).

    Quando o relatório do Alfa passa pelo Excel antes de virar CSV, a coluna de data
    é exportada como número de série (dias desde 30/12/1899, com a fração indicando
    a hora). Sem esta conversão a competência não é reconhecida.
    """
    text = normalize_whitespace(value)
    if not text or "/" in text or "-" in text or ":" in text:
        return None
    try:
        serial = float(text.replace(",", "."))
    except ValueError:
        return None
    # Faixa segura: 1954 a 2064. Evita interpretar códigos/quantidades como data.
    if not (20000 <= serial <= 60000):
        return None
    try:
        return datetime(1899, 12, 30) + timedelta(days=serial)
    except (OverflowError, ValueError):
        return None


def parse_sales_row_date(row: dict[str, str]) -> datetime | None:
    """Data de uma linha do faturamento detalhado, aceitando vários formatos."""
    raw = find_sales_date_value(row)
    return (
        parse_datetime_pt(raw)
        or parse_excel_serial_date(raw)
        or parse_datetime_flexible(raw)
    )


def parse_datetime_flexible(value: str | None) -> datetime | None:
    text = normalize_whitespace(value)
    if not text:
        return None
    normalized = text.replace("T", " ")
    for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%d", "%d/%m/%Y %H:%M:%S", "%d/%m/%Y"):
        try:
            return datetime.strptime(normalized, fmt)
        except ValueError:
            continue
    try:
        return datetime.fromisoformat(text)
    except ValueError:
        return None


def crm_status_from_days(days_without_purchase: int | None) -> str:
    days = 9999 if days_without_purchase is None else days_without_purchase
    if days <= 29:
        return "ATIVO"
    if days <= 60:
        return "PRE_INATIVO"
    return "INATIVO"


def crm_class_from_average(avg_revenue: float) -> str:
    if avg_revenue > 10000:
        return "DIAMANTE"
    if avg_revenue >= 6000:
        return "OURO"
    if avg_revenue >= 3000:
        return "PRATA"
    if avg_revenue >= 500:
        return "BRONZE"
    return "NAO_CLASSIFICADO"


def crm_class_rank(class_code: str) -> int:
    order = {
        "DIAMANTE": 0,
        "OURO": 1,
        "PRATA": 2,
        "BRONZE": 3,
        "NAO_CLASSIFICADO": 4,
    }
    return order.get(class_code, 99)


def crm_scope_clause(
    conn: sqlite3.Connection, company_id: int, filters: dict[str, str | None]
) -> tuple[str, list[Any]]:
    clauses: list[str] = ["company_id = ?"]
    params: list[Any] = [company_id]
    seller_name = normalize_whitespace(filters.get("seller_name"))
    if seller_name:
        clauses.append("seller_name = ?")
        params.append(seller_name)
    unit_name = normalize_unit(filters.get("unit_name"))
    allowed_units = normalize_unit_list(filters.get("allowed_units"))
    scoped_units = [unit_name] if unit_name else allowed_units
    if scoped_units:
        cities = active_mapped_cities_for_units(conn, company_id, scoped_units)
        if cities:
            placeholders = ", ".join("?" for _ in cities)
            clauses.append(f"city_name IN ({placeholders})")
            params.extend(cities)
        else:
            clauses.append("1 = 0")
    city_name = normalize_upper(filters.get("city_name"))
    if city_name:
        clauses.append("city_name = ?")
        params.append(city_name)
    return " AND ".join(clauses), params


def init_crm_schema(conn: sqlite3.Connection) -> None:
    conn.executescript(
        """
        CREATE TABLE IF NOT EXISTS crm_contact_types (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            code TEXT NOT NULL UNIQUE,
            label TEXT NOT NULL,
            is_active INTEGER NOT NULL DEFAULT 1
        );

        CREATE TABLE IF NOT EXISTS crm_contact_results (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            code TEXT NOT NULL UNIQUE,
            label TEXT NOT NULL,
            generates_followup INTEGER NOT NULL DEFAULT 0,
            requires_followup_date INTEGER NOT NULL DEFAULT 0,
            is_active INTEGER NOT NULL DEFAULT 1
        );

        CREATE TABLE IF NOT EXISTS crm_interactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            company_id INTEGER NOT NULL,
            client_key TEXT NOT NULL,
            client_name TEXT NOT NULL,
            seller_name TEXT NOT NULL,
            unit_name TEXT,
            contact_phone TEXT,
            contact_name TEXT,
            contact_type_code TEXT NOT NULL,
            result_code TEXT NOT NULL,
            occurred_at TEXT NOT NULL,
            notes TEXT NOT NULL,
            question_used TEXT,
            had_progress INTEGER NOT NULL DEFAULT 0,
            offer_title TEXT,
            next_action TEXT,
            followup_due_at TEXT,
            created_at TEXT NOT NULL,
            created_by_user_id INTEGER,
            FOREIGN KEY (company_id) REFERENCES companies(id),
            FOREIGN KEY (created_by_user_id) REFERENCES users(id)
        );

        CREATE TABLE IF NOT EXISTS crm_tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            company_id INTEGER NOT NULL,
            client_key TEXT NOT NULL,
            client_name TEXT NOT NULL,
            seller_name TEXT NOT NULL,
            title TEXT NOT NULL,
            description TEXT,
            due_at TEXT NOT NULL,
            status TEXT NOT NULL DEFAULT 'ABERTA',
            source_interaction_id INTEGER,
            created_at TEXT NOT NULL,
            completed_at TEXT,
            FOREIGN KEY (company_id) REFERENCES companies(id),
            FOREIGN KEY (source_interaction_id) REFERENCES crm_interactions(id)
        );

        CREATE INDEX IF NOT EXISTS idx_crm_interactions_client_date
            ON crm_interactions(company_id, client_key, occurred_at DESC);

        CREATE INDEX IF NOT EXISTS idx_crm_interactions_seller_date
            ON crm_interactions(company_id, seller_name, occurred_at DESC);

        CREATE INDEX IF NOT EXISTS idx_crm_tasks_seller_status_due
            ON crm_tasks(company_id, seller_name, status, due_at);

            CREATE TABLE IF NOT EXISTS crm_agenda_actions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                company_id INTEGER NOT NULL,
                seller_name TEXT NOT NULL,
            client_key TEXT NOT NULL,
            client_name TEXT NOT NULL,
            action_type TEXT NOT NULL,
            justification TEXT NOT NULL,
            next_visible_at TEXT,
            created_at TEXT NOT NULL,
            created_by_user_id INTEGER,
            FOREIGN KEY (company_id) REFERENCES companies(id),
            FOREIGN KEY (created_by_user_id) REFERENCES users(id)
        );

            CREATE INDEX IF NOT EXISTS idx_crm_agenda_actions_lookup
                ON crm_agenda_actions(company_id, seller_name, client_key, created_at DESC);

            CREATE TABLE IF NOT EXISTS crm_client_profiles (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                company_id INTEGER NOT NULL,
                client_code TEXT NOT NULL,
                client_name TEXT NOT NULL,
                trade_name TEXT,
                document_number TEXT,
                state_registration TEXT,
                address_line TEXT,
                address_number TEXT,
                neighborhood TEXT,
                city_name TEXT,
                state_name TEXT,
                phone TEXT,
                updated_phone TEXT,
                primary_contact_name TEXT,
                contact_notes TEXT,
                contact_updated_at TEXT,
                contact_updated_by_user_id INTEGER,
                postal_code TEXT,
                first_sale_at TEXT,
                last_sale_at TEXT,
                credit_limit REAL NOT NULL DEFAULT 0,
                economic_group TEXT,
                internal_seller_name TEXT,
                external_seller_name TEXT,
                email TEXT,
                source_import_id INTEGER,
                updated_at TEXT NOT NULL,
                created_at TEXT NOT NULL,
                UNIQUE(company_id, client_code),
                FOREIGN KEY (company_id) REFERENCES companies(id),
                FOREIGN KEY (source_import_id) REFERENCES imports(id),
                FOREIGN KEY (contact_updated_by_user_id) REFERENCES users(id)
            );

            CREATE TABLE IF NOT EXISTS crm_client_summary (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                company_id INTEGER NOT NULL,
                competence TEXT NOT NULL,
                import_id INTEGER NOT NULL,
                client_code TEXT NOT NULL,
                client_name TEXT NOT NULL,
                seller_name TEXT,
                city_name TEXT,
                last_purchase_at TEXT,
                gross_value REAL NOT NULL DEFAULT 0,
                discount_value REAL NOT NULL DEFAULT 0,
                freight_value REAL NOT NULL DEFAULT 0,
                return_quantity REAL NOT NULL DEFAULT 0,
                return_value REAL NOT NULL DEFAULT 0,
                net_value REAL NOT NULL DEFAULT 0,
                sale_share REAL NOT NULL DEFAULT 0,
                created_at TEXT NOT NULL,
                UNIQUE(company_id, competence, client_code),
                FOREIGN KEY (company_id) REFERENCES companies(id),
                FOREIGN KEY (import_id) REFERENCES imports(id)
            );

            CREATE INDEX IF NOT EXISTS idx_crm_profiles_company_code
                ON crm_client_profiles(company_id, client_code);

            CREATE INDEX IF NOT EXISTS idx_crm_profiles_company_name
                ON crm_client_profiles(company_id, client_name);

            CREATE INDEX IF NOT EXISTS idx_crm_summary_company_competence_code
                ON crm_client_summary(company_id, competence, client_code);

            CREATE INDEX IF NOT EXISTS idx_crm_summary_company_seller_competence
                ON crm_client_summary(company_id, seller_name, competence);

            CREATE INDEX IF NOT EXISTS idx_city_mappings_company_city
                ON city_mappings(company_id, city_name);

            CREATE INDEX IF NOT EXISTS idx_crm_interactions_company_client
                ON crm_interactions(company_id, client_key);
        """
    )
    interaction_columns = {row["name"] for row in conn.execute("PRAGMA table_info(crm_interactions)").fetchall()}
    if "contact_phone" not in interaction_columns:
        conn.execute("ALTER TABLE crm_interactions ADD COLUMN contact_phone TEXT")
    if "contact_name" not in interaction_columns:
        conn.execute("ALTER TABLE crm_interactions ADD COLUMN contact_name TEXT")

    profile_columns = {row["name"] for row in conn.execute("PRAGMA table_info(crm_client_profiles)").fetchall()}
    if "updated_phone" not in profile_columns:
        conn.execute("ALTER TABLE crm_client_profiles ADD COLUMN updated_phone TEXT")
    if "primary_contact_name" not in profile_columns:
        conn.execute("ALTER TABLE crm_client_profiles ADD COLUMN primary_contact_name TEXT")
    if "contact_notes" not in profile_columns:
        conn.execute("ALTER TABLE crm_client_profiles ADD COLUMN contact_notes TEXT")
    if "contact_updated_at" not in profile_columns:
        conn.execute("ALTER TABLE crm_client_profiles ADD COLUMN contact_updated_at TEXT")
    if "contact_updated_by_user_id" not in profile_columns:
        conn.execute("ALTER TABLE crm_client_profiles ADD COLUMN contact_updated_by_user_id INTEGER")


def seed_crm_catalogs(conn: sqlite3.Connection) -> None:
    for code, label in CRM_CONTACT_TYPES:
        conn.execute(
            """
            INSERT INTO crm_contact_types (code, label)
            VALUES (?, ?)
            ON CONFLICT(code) DO UPDATE SET label = excluded.label, is_active = 1
            """,
            (code, label),
        )
    for code, label, generates_followup, requires_followup_date in CRM_CONTACT_RESULTS:
        conn.execute(
            """
            INSERT INTO crm_contact_results (code, label, generates_followup, requires_followup_date)
            VALUES (?, ?, ?, ?)
            ON CONFLICT(code) DO UPDATE SET
                label = excluded.label,
                generates_followup = excluded.generates_followup,
                requires_followup_date = excluded.requires_followup_date,
                is_active = 1
            """,
            (code, label, generates_followup, requires_followup_date),
        )


def crm_recent_competences(conn: sqlite3.Connection, company_id: int, limit: int = 3) -> list[str]:
    return query_competences(conn, company_id)[:limit]


def crm_latest_competence(conn: sqlite3.Connection, company_id: int) -> str | None:
    competences = crm_recent_competences(conn, company_id, 1)
    return competences[0] if competences else None


def crm_summary_latest_competence(conn: sqlite3.Connection, company_id: int) -> str | None:
    """Competência mais recente nos dados CRM (crm_client_summary).
    Independente da competência do faturamento — permite importar CRM de junho
    mesmo que o faturamento ainda seja de maio."""
    row = conn.execute(
        "SELECT MAX(competence) AS competence FROM crm_client_summary WHERE company_id = ?",
        (company_id,),
    ).fetchone()
    crm_comp = row["competence"] if row else None
    # Fallback para competência do faturamento se não houver dados CRM
    return crm_comp or crm_latest_competence(conn, company_id)


def first_day_of_competence(competence: str) -> date:
    year, month = competence.split("-")
    return date(int(year), int(month), 1)


def last_day_of_competence(competence: str) -> date:
    start = first_day_of_competence(competence)
    if start.month == 12:
        return date(start.year, 12, 31)
    return date(start.year, start.month + 1, 1) - timedelta(days=1)


def shift_competence(competence: str, delta_months: int) -> str:
    start = first_day_of_competence(competence)
    absolute_month = start.year * 12 + (start.month - 1) + delta_months
    year = absolute_month // 12
    month = absolute_month % 12 + 1
    return f"{year:04d}-{month:02d}"


def daterange(start: date, end: date):
    current = start
    while current <= end:
        yield current
        current += timedelta(days=1)


def hash_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def pbkdf2_hash(password: str, salt: str | None = None) -> tuple[str, str]:
    salt = salt or secrets.token_hex(16)
    pwd_hash = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt.encode("utf-8"), 120000).hex()
    return pwd_hash, salt


def verify_password(password: str, stored_hash: str, salt: str) -> bool:
    candidate, _ = pbkdf2_hash(password, salt)
    return hmac.compare_digest(candidate, stored_hash)


def _json_sanitize(value: Any) -> Any:
    """Substitui Infinity/-Infinity/NaN por None em toda a estrutura.

    O json do Python emite literais `Infinity` e `NaN`, que NÃO são JSON válido:
    o JSON.parse do navegador lança SyntaxError e a tela trava carregando. Isso
    acontecia, por exemplo, em marginValue quando a base de custo tinha divisão
    degenerada. Sanear na serialização resolve a classe inteira do problema.
    """
    if isinstance(value, float):
        return value if math.isfinite(value) else None
    if isinstance(value, dict):
        return {k: _json_sanitize(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [_json_sanitize(v) for v in value]
    return value


def json_dumps(data: Any) -> bytes:
    # allow_nan=False faria levantar exceção; preferimos sanear e sempre responder.
    return json.dumps(_json_sanitize(data), ensure_ascii=False, allow_nan=False).encode("utf-8")


def get_connection() -> sqlite3.Connection:
    ensure_dirs()
    migrate_legacy_db_if_needed()
    conn = sqlite3.connect(DB_PATH, timeout=30)
    conn.row_factory = sqlite3.Row
    # PRAGMAs seguros por conexão (sem escrita no DB)
    conn.execute("PRAGMA cache_size=-16000")   # 16 MB page cache por conexão
    conn.execute("PRAGMA temp_store=MEMORY")
    return conn


def audit_log(conn: sqlite3.Connection, company_id: int, user_id: int | None, action: str, entity_type: str, entity_id: str, changes: dict[str, Any]) -> None:
    conn.execute(
        """
        INSERT INTO audit_logs (company_id, user_id, action, entity_type, entity_id, changes_json, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        (company_id, user_id, action, entity_type, entity_id, json.dumps(changes, ensure_ascii=False), now_iso()),
    )


# ─────────────────────────────────────────────────────────────────────────────
# Perfis de acesso
# ─────────────────────────────────────────────────────────────────────────────

def normalize_module_list(value: Any) -> list[str]:
    """Aceita lista ou JSON e devolve só ids de módulo válidos, na ordem canônica."""
    if isinstance(value, str):
        try:
            value = json.loads(value or "[]")
        except json.JSONDecodeError:
            value = []
    if not isinstance(value, (list, tuple, set)):
        return []
    wanted = {normalize_whitespace(str(v)) for v in value}
    return [m["id"] for m in ACCESS_MODULES if m["id"] in wanted]


def seed_access_profiles(conn: sqlite3.Connection, company_id: int) -> None:
    """Cria os perfis base uma única vez e vincula usuários existentes pelo nome do papel."""
    for spec in DEFAULT_ACCESS_PROFILES:
        conn.execute(
            """
            INSERT OR IGNORE INTO access_profiles
                (company_id, name, description, modules_json, data_scope, can_manage_users, is_system, created_at)
            VALUES (?, ?, ?, ?, ?, ?, 1, ?)
            """,
            (
                company_id,
                spec["name"],
                spec["description"],
                json.dumps(spec["modules"], ensure_ascii=False),
                spec["data_scope"],
                spec["can_manage_users"],
                now_iso(),
            ),
        )
    conn.commit()

    # Módulos novos criados depois da primeira execução não entram pelo INSERT OR IGNORE
    # acima. Aqui os perfis de sistema recebem as telas que passaram a existir na
    # especificação. Só ADICIONA — nunca remove, para preservar ajustes feitos na tela.
    for spec in DEFAULT_ACCESS_PROFILES:
        row = conn.execute(
            "SELECT id, modules_json FROM access_profiles "
            "WHERE company_id = ? AND name = ? AND is_system = 1",
            (company_id, spec["name"]),
        ).fetchone()
        if not row:
            continue
        current = normalize_module_list(row["modules_json"])
        missing = [m for m in spec["modules"] if m not in current]
        if missing:
            merged = normalize_module_list(current + missing)
            conn.execute(
                "UPDATE access_profiles SET modules_json = ?, updated_at = ? WHERE id = ?",
                (json.dumps(merged, ensure_ascii=False), now_iso(), row["id"]),
            )
            print(f"[perfis] '{spec['name']}' recebeu novas telas: {', '.join(missing)}")
    conn.commit()

    # Usuários criados antes dos perfis: liga cada um ao perfil de mesmo nome do role
    conn.execute(
        """
        UPDATE users
        SET profile_id = (
            SELECT p.id FROM access_profiles p
            WHERE p.company_id = users.company_id AND p.name = users.role
        )
        WHERE profile_id IS NULL
          AND EXISTS (
            SELECT 1 FROM access_profiles p
            WHERE p.company_id = users.company_id AND p.name = users.role
          )
        """
    )
    conn.commit()


def access_profile_row_to_dict(row: sqlite3.Row) -> dict[str, Any]:
    return {
        "id": row["id"],
        "name": row["name"],
        "description": row["description"] or "",
        "modules": normalize_module_list(row["modules_json"]),
        "dataScope": row["data_scope"] or "todos",
        "canManageUsers": bool(row["can_manage_users"]),
        "isSystem": bool(row["is_system"]),
    }


def list_access_profiles(conn: sqlite3.Connection, company_id: int) -> list[dict[str, Any]]:
    rows = conn.execute(
        "SELECT * FROM access_profiles WHERE company_id = ? ORDER BY is_system DESC, name",
        (company_id,),
    ).fetchall()
    return [access_profile_row_to_dict(r) for r in rows]


def get_access_profile_for_user(conn: sqlite3.Connection, user: Any) -> dict[str, Any] | None:
    """Perfil do usuário. Se não houver vínculo, cai no perfil de mesmo nome do role."""
    profile_id = None
    try:
        profile_id = user["profile_id"]
    except (KeyError, IndexError, TypeError):
        profile_id = None
    row = None
    if profile_id:
        row = conn.execute(
            "SELECT * FROM access_profiles WHERE id = ? AND company_id = ?",
            (profile_id, user["company_id"]),
        ).fetchone()
    if row is None:
        row = conn.execute(
            "SELECT * FROM access_profiles WHERE company_id = ? AND name = ?",
            (user["company_id"], user["role"]),
        ).fetchone()
    return access_profile_row_to_dict(row) if row else None


def upsert_access_profile(
    conn: sqlite3.Connection, company_id: int, user_id: int, payload: dict[str, Any]
) -> dict[str, Any]:
    name = normalize_whitespace(payload.get("name"))
    if not name:
        raise ValueError("Nome do perfil é obrigatório.")
    modules = normalize_module_list(payload.get("modules"))
    if not modules:
        raise ValueError("Selecione ao menos uma tela para o perfil.")
    data_scope = normalize_whitespace(payload.get("dataScope")) or "todos"
    if data_scope not in DATA_SCOPE_IDS:
        raise ValueError("Escopo de dados inválido.")
    can_manage = 1 if payload.get("canManageUsers") else 0
    description = normalize_whitespace(payload.get("description"))
    profile_id = payload.get("id")

    if profile_id:
        existing = conn.execute(
            "SELECT * FROM access_profiles WHERE id = ? AND company_id = ?", (profile_id, company_id)
        ).fetchone()
        if not existing:
            raise ValueError("Perfil não encontrado.")
        # Perfis de sistema podem ser editados, mas não renomeados (usuários referenciam pelo nome)
        if existing["is_system"] and name != existing["name"]:
            raise ValueError(f"O perfil '{existing['name']}' é padrão do sistema e não pode ser renomeado.")
        conn.execute(
            """
            UPDATE access_profiles
            SET name = ?, description = ?, modules_json = ?, data_scope = ?,
                can_manage_users = ?, updated_at = ?
            WHERE id = ? AND company_id = ?
            """,
            (name, description, json.dumps(modules, ensure_ascii=False), data_scope,
             can_manage, now_iso(), profile_id, company_id),
        )
        audit_log(conn, company_id, user_id, "editar", "access_profiles", str(profile_id),
                  {"name": name, "modules": len(modules), "dataScope": data_scope})
        created = False
    else:
        duplicate = conn.execute(
            "SELECT id FROM access_profiles WHERE company_id = ? AND name = ?", (company_id, name)
        ).fetchone()
        if duplicate:
            raise ValueError(f"Já existe um perfil chamado '{name}'.")
        cursor = conn.execute(
            """
            INSERT INTO access_profiles
                (company_id, name, description, modules_json, data_scope, can_manage_users, is_system, created_at)
            VALUES (?, ?, ?, ?, ?, ?, 0, ?)
            """,
            (company_id, name, description, json.dumps(modules, ensure_ascii=False),
             data_scope, can_manage, now_iso()),
        )
        profile_id = cursor.lastrowid
        audit_log(conn, company_id, user_id, "criar", "access_profiles", str(profile_id),
                  {"name": name, "modules": len(modules), "dataScope": data_scope})
        created = True
    return {"id": profile_id, "created": created}


def delete_access_profile(conn: sqlite3.Connection, company_id: int, user_id: int, profile_id: Any) -> None:
    row = conn.execute(
        "SELECT * FROM access_profiles WHERE id = ? AND company_id = ?", (profile_id, company_id)
    ).fetchone()
    if not row:
        raise ValueError("Perfil não encontrado.")
    if row["is_system"]:
        raise ValueError(f"O perfil '{row['name']}' é padrão do sistema e não pode ser excluído.")
    in_use = conn.execute(
        "SELECT COUNT(*) AS n FROM users WHERE company_id = ? AND profile_id = ?", (company_id, profile_id)
    ).fetchone()["n"]
    if in_use:
        raise ValueError(f"Há {in_use} usuário(s) usando este perfil. Troque o perfil deles antes de excluir.")
    conn.execute("DELETE FROM access_profiles WHERE id = ? AND company_id = ?", (profile_id, company_id))
    audit_log(conn, company_id, user_id, "excluir", "access_profiles", str(profile_id), {"name": row["name"]})


# ─────────────────────────────────────────────────────────────────────────────
# Biblioteca de conteúdo comercial
# ─────────────────────────────────────────────────────────────────────────────

CONTENT_CATEGORIES = [
    {"id": "ligacao",  "label": "Abordagem por telefone", "icon": "📞"},
    {"id": "whatsapp", "label": "Mensagem de WhatsApp",   "icon": "💬"},
    {"id": "objecao",  "label": "Tratamento de objeção",  "icon": "🛡"},
    {"id": "garantia", "label": "Devolução e garantia",   "icon": "📋"},
]
CONTENT_CATEGORY_IDS = {c["id"] for c in CONTENT_CATEGORIES}

CONTENT_SITUATIONS = [
    {"id": "GERAL",          "label": "Qualquer situação"},
    {"id": "INATIVO",        "label": "Cliente inativo"},
    {"id": "PRE_INATIVO",    "label": "Cliente pré-inativo"},
    {"id": "SEM_COMPRA_MES", "label": "Sem compra no mês"},
    {"id": "QUEDA",          "label": "Queda de faturamento"},
    {"id": "MIX",            "label": "Ampliar mix"},
    {"id": "NOVO",           "label": "Cliente novo"},
]
CONTENT_SITUATION_IDS = {s["id"] for s in CONTENT_SITUATIONS}


def seed_content_library(conn: sqlite3.Connection, company_id: int) -> None:
    """Popula a biblioteca uma única vez. Edições do usuário não são sobrescritas."""
    existing = conn.execute(
        "SELECT COUNT(*) AS n FROM content_library WHERE company_id = ?", (company_id,)
    ).fetchone()["n"]
    if existing:
        return
    try:
        from content_seed import CONTENT_SEED
    except ImportError:
        print("[content] content_seed.py não encontrado — biblioteca iniciada vazia")
        return
    for item in CONTENT_SEED:
        conn.execute(
            """
            INSERT INTO content_library
                (company_id, category, situation, title, body, hint, sort_order, is_active, is_system, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, 1, 1, ?)
            """,
            (company_id, item["category"], item["situation"], item["title"],
             item["body"], item.get("hint"), item.get("sort_order", 0), now_iso()),
        )
    conn.commit()
    print(f"[content] biblioteca iniciada com {len(CONTENT_SEED)} conteúdos")


def content_row_to_dict(row: sqlite3.Row) -> dict[str, Any]:
    return {
        "id": row["id"],
        "category": row["category"],
        "situation": row["situation"],
        "title": row["title"],
        "body": row["body"],
        "hint": row["hint"] or "",
        "sortOrder": row["sort_order"],
        "isActive": bool(row["is_active"]),
        "isSystem": bool(row["is_system"]),
    }


def list_content_library(
    conn: sqlite3.Connection, company_id: int, category: str | None = None,
    situation: str | None = None, only_active: bool = True,
) -> list[dict[str, Any]]:
    where = ["company_id = ?"]
    params: list[Any] = [company_id]
    if category:
        where.append("category = ?")
        params.append(category)
    if situation:
        # GERAL sempre acompanha a situação específica
        where.append("(situation = ? OR situation = 'GERAL')")
        params.append(situation)
    if only_active:
        where.append("is_active = 1")
    rows = conn.execute(
        f"SELECT * FROM content_library WHERE {' AND '.join(where)} "
        "ORDER BY category, CASE situation WHEN 'GERAL' THEN 1 ELSE 0 END, sort_order, id",
        params,
    ).fetchall()
    return [content_row_to_dict(r) for r in rows]


def render_content_text(text: str, context: dict[str, Any]) -> str:
    """Substitui os marcadores {cliente}, {vendedor}, {item}, {dias} etc."""
    result = text or ""
    for key, value in context.items():
        result = result.replace("{" + key + "}", str(value) if value is not None else "")
    # Marcadores sem valor viram um placeholder visível para o vendedor preencher
    result = re.sub(r"\{(\w+)\}", lambda m: f"[{m.group(1)}]", result)
    return result


def content_context_for_client(client: dict[str, Any], seller_name: str | None) -> dict[str, Any]:
    offer = client.get("offerPrimary") or {}
    dias = client.get("daysWithoutPurchase")
    return {
        "cliente": client.get("clientName") or "cliente",
        "vendedor": seller_name or "",
        "item": offer.get("title") or "",
        "dias": dias if dias is not None else "",
        "unidade": client.get("unitName") or "",
    }


def upsert_content_item(
    conn: sqlite3.Connection, company_id: int, user_id: int, payload: dict[str, Any]
) -> dict[str, Any]:
    category = normalize_whitespace(payload.get("category"))
    situation = normalize_upper(payload.get("situation")) or "GERAL"
    title = normalize_whitespace(payload.get("title"))
    body = (payload.get("body") or "").strip()
    hint = normalize_whitespace(payload.get("hint"))
    sort_order = int(payload.get("sortOrder") or 0)
    is_active = 1 if payload.get("isActive", True) else 0
    item_id = payload.get("id")

    if category not in CONTENT_CATEGORY_IDS:
        raise ValueError("Categoria inválida.")
    if situation not in CONTENT_SITUATION_IDS:
        raise ValueError("Situação inválida.")
    if not title or not body:
        raise ValueError("Título e conteúdo são obrigatórios.")

    if item_id:
        exists = conn.execute(
            "SELECT id FROM content_library WHERE id = ? AND company_id = ?", (item_id, company_id)
        ).fetchone()
        if not exists:
            raise ValueError("Conteúdo não encontrado.")
        conn.execute(
            """
            UPDATE content_library
            SET category = ?, situation = ?, title = ?, body = ?, hint = ?,
                sort_order = ?, is_active = ?, updated_at = ?
            WHERE id = ? AND company_id = ?
            """,
            (category, situation, title, body, hint, sort_order, is_active, now_iso(), item_id, company_id),
        )
        audit_log(conn, company_id, user_id, "editar", "content_library", str(item_id), {"title": title})
        return {"id": item_id, "created": False}

    cur = conn.execute(
        """
        INSERT INTO content_library
            (company_id, category, situation, title, body, hint, sort_order, is_active, is_system, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, 0, ?)
        """,
        (company_id, category, situation, title, body, hint, sort_order, is_active, now_iso()),
    )
    audit_log(conn, company_id, user_id, "criar", "content_library", str(cur.lastrowid), {"title": title})
    return {"id": cur.lastrowid, "created": True}


def delete_content_item(conn: sqlite3.Connection, company_id: int, user_id: int, item_id: Any) -> None:
    row = conn.execute(
        "SELECT * FROM content_library WHERE id = ? AND company_id = ?", (item_id, company_id)
    ).fetchone()
    if not row:
        raise ValueError("Conteúdo não encontrado.")
    conn.execute("DELETE FROM content_library WHERE id = ? AND company_id = ?", (item_id, company_id))
    audit_log(conn, company_id, user_id, "excluir", "content_library", str(item_id), {"title": row["title"]})


def user_can_manage_users(conn: sqlite3.Connection, user: Any) -> bool:
    profile = get_access_profile_for_user(conn, user)
    if profile:
        return profile["canManageUsers"]
    return user["role"] in {"Administrador", "Diretor"}


def init_db() -> None:
    ensure_dirs()
    with closing(get_connection()) as conn:
        # WAL mode: aplicado apenas uma vez na inicialização (é operação de escrita)
        conn.execute("PRAGMA journal_mode=WAL")
        conn.executescript(
            """
            PRAGMA foreign_keys = ON;

            CREATE TABLE IF NOT EXISTS companies (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE,
                code TEXT,
                created_at TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                company_id INTEGER NOT NULL,
                username TEXT NOT NULL UNIQUE,
                full_name TEXT,
                linked_person_name TEXT,
                linked_units_json TEXT,
                password_hash TEXT NOT NULL,
                password_salt TEXT NOT NULL,
                role TEXT NOT NULL,
                is_active INTEGER NOT NULL DEFAULT 1,
                created_at TEXT NOT NULL,
                FOREIGN KEY (company_id) REFERENCES companies(id)
            );

            CREATE TABLE IF NOT EXISTS sessions (
                id TEXT PRIMARY KEY,
                user_id INTEGER NOT NULL,
                created_at TEXT NOT NULL,
                expires_at TEXT NOT NULL,
                FOREIGN KEY (user_id) REFERENCES users(id)
            );

            -- Devoluções em garantia: chegam misturadas no custo/venda e precisam ser
            -- deduzidas do resultado comercial (defeito de fábrica não é erro de venda)
            CREATE TABLE IF NOT EXISTS fact_warranty_returns (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                company_id INTEGER NOT NULL,
                competence TEXT NOT NULL,
                import_id INTEGER NOT NULL,
                row_hash TEXT NOT NULL,
                unit_name TEXT NOT NULL,
                seller_name TEXT NOT NULL,
                client_name TEXT,
                city_name TEXT,
                return_number TEXT,
                return_date TEXT,
                reason TEXT,
                invoice_number TEXT,
                issue_date TEXT,
                item_code TEXT,
                item_type TEXT,
                item_description TEXT,
                brand_name TEXT,
                supplier_name TEXT,
                quantity REAL NOT NULL DEFAULT 0,
                cost_value REAL NOT NULL DEFAULT 0,
                total_value REAL NOT NULL DEFAULT 0,
                created_at TEXT NOT NULL,
                UNIQUE(company_id, competence, row_hash),
                FOREIGN KEY (company_id) REFERENCES companies(id)
            );

            CREATE INDEX IF NOT EXISTS idx_warranty_company_competence
                ON fact_warranty_returns(company_id, competence);
            CREATE INDEX IF NOT EXISTS idx_warranty_company_comp_seller
                ON fact_warranty_returns(company_id, competence, seller_name);
            CREATE INDEX IF NOT EXISTS idx_warranty_company_comp_unit
                ON fact_warranty_returns(company_id, competence, unit_name);

            -- Biblioteca de conteúdo comercial: scripts, mensagens e orientações
            CREATE TABLE IF NOT EXISTS content_library (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                company_id INTEGER NOT NULL,
                category TEXT NOT NULL,        -- ligacao | whatsapp | objecao | garantia
                situation TEXT NOT NULL,       -- INATIVO | PRE_INATIVO | SEM_COMPRA_MES | QUEDA | MIX | NOVO | GERAL
                title TEXT NOT NULL,
                body TEXT NOT NULL,
                hint TEXT,
                sort_order INTEGER NOT NULL DEFAULT 0,
                is_active INTEGER NOT NULL DEFAULT 1,
                is_system INTEGER NOT NULL DEFAULT 0,
                created_at TEXT NOT NULL,
                updated_at TEXT,
                FOREIGN KEY (company_id) REFERENCES companies(id)
            );

            CREATE INDEX IF NOT EXISTS idx_content_library_lookup
                ON content_library(company_id, category, situation, is_active);

            -- Perfis de acesso configuráveis pela tela (antes as permissões eram fixas no código)
            CREATE TABLE IF NOT EXISTS access_profiles (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                company_id INTEGER NOT NULL,
                name TEXT NOT NULL,
                description TEXT,
                modules_json TEXT NOT NULL DEFAULT '[]',
                data_scope TEXT NOT NULL DEFAULT 'todos',
                can_manage_users INTEGER NOT NULL DEFAULT 0,
                is_system INTEGER NOT NULL DEFAULT 0,
                created_at TEXT NOT NULL,
                updated_at TEXT,
                UNIQUE(company_id, name),
                FOREIGN KEY (company_id) REFERENCES companies(id)
            );

            CREATE TABLE IF NOT EXISTS people_records (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                company_id INTEGER NOT NULL,
                person_name TEXT NOT NULL,
                role_classification TEXT NOT NULL,
                base_unit TEXT,
                valid_from TEXT NOT NULL,
                valid_to TEXT,
                source TEXT NOT NULL,
                is_active INTEGER NOT NULL DEFAULT 1,
                created_at TEXT NOT NULL,
                UNIQUE(company_id, person_name, valid_from, source),
                FOREIGN KEY (company_id) REFERENCES companies(id)
            );

            CREATE TABLE IF NOT EXISTS city_mappings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                company_id INTEGER NOT NULL,
                city_name TEXT NOT NULL,
                principal_unit TEXT NOT NULL,
                state_name TEXT,
                country_name TEXT,
                valid_from TEXT NOT NULL,
                valid_to TEXT,
                source TEXT NOT NULL,
                created_at TEXT NOT NULL,
                UNIQUE(company_id, city_name, valid_from, source),
                FOREIGN KEY (company_id) REFERENCES companies(id)
            );

            CREATE TABLE IF NOT EXISTS client_registry (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                company_id INTEGER NOT NULL,
                client_name TEXT NOT NULL,
                normalized_client_name TEXT NOT NULL,
                document_number TEXT,
                document_digits TEXT,
                person_type TEXT NOT NULL,
                source TEXT NOT NULL,
                confidence_score REAL NOT NULL DEFAULT 1,
                notes TEXT,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                UNIQUE(company_id, normalized_client_name),
                FOREIGN KEY (company_id) REFERENCES companies(id)
            );

            CREATE TABLE IF NOT EXISTS holidays (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                company_id INTEGER NOT NULL,
                holiday_date TEXT NOT NULL,
                holiday_name TEXT NOT NULL,
                scope TEXT NOT NULL DEFAULT 'NACIONAL_RS',
                created_at TEXT NOT NULL,
                UNIQUE(company_id, holiday_date, holiday_name),
                FOREIGN KEY (company_id) REFERENCES companies(id)
            );

            CREATE TABLE IF NOT EXISTS vacations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                company_id INTEGER NOT NULL,
                person_name TEXT NOT NULL,
                start_date TEXT NOT NULL,
                end_date TEXT NOT NULL,
                notes TEXT,
                created_at TEXT NOT NULL,
                UNIQUE(company_id, person_name, start_date, end_date),
                FOREIGN KEY (company_id) REFERENCES companies(id)
            );

            CREATE TABLE IF NOT EXISTS score_configs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                company_id INTEGER NOT NULL,
                valid_from_competence TEXT NOT NULL,
                valid_to_competence TEXT,
                weight_goal REAL NOT NULL,
                weight_ticket REAL NOT NULL,
                weight_clients REAL NOT NULL,
                weight_mix REAL NOT NULL,
                weight_returns REAL NOT NULL,
                created_at TEXT NOT NULL,
                UNIQUE(company_id, valid_from_competence),
                FOREIGN KEY (company_id) REFERENCES companies(id)
            );

            CREATE TABLE IF NOT EXISTS goals_seller (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                company_id INTEGER NOT NULL,
                competence TEXT NOT NULL,
                seller_name TEXT NOT NULL,
                base_unit TEXT,
                revenue_goal REAL NOT NULL DEFAULT 0,
                returns_goal REAL NOT NULL DEFAULT 0,
                created_at TEXT NOT NULL,
                UNIQUE(company_id, competence, seller_name),
                FOREIGN KEY (company_id) REFERENCES companies(id)
            );

            CREATE TABLE IF NOT EXISTS goals_unit (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                company_id INTEGER NOT NULL,
                competence TEXT NOT NULL,
                unit_name TEXT NOT NULL,
                revenue_goal REAL NOT NULL DEFAULT 0,
                returns_goal REAL NOT NULL DEFAULT 0,
                created_at TEXT NOT NULL,
                UNIQUE(company_id, competence, unit_name),
                FOREIGN KEY (company_id) REFERENCES companies(id)
            );


            CREATE TABLE IF NOT EXISTS imports (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                company_id INTEGER NOT NULL,
                competence TEXT NOT NULL,
                import_action TEXT NOT NULL,
                suggested_competence TEXT,
                imported_by INTEGER,
                imported_at TEXT NOT NULL,
                duplicate_rows_skipped INTEGER NOT NULL DEFAULT 0,
                notes TEXT,
                FOREIGN KEY (company_id) REFERENCES companies(id),
                FOREIGN KEY (imported_by) REFERENCES users(id)
            );

            CREATE TABLE IF NOT EXISTS import_files (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                import_id INTEGER NOT NULL,
                file_type TEXT NOT NULL,
                original_name TEXT NOT NULL,
                file_hash TEXT NOT NULL,
                row_count INTEGER NOT NULL DEFAULT 0,
                UNIQUE(import_id, file_type),
                FOREIGN KEY (import_id) REFERENCES imports(id)
            );

            CREATE TABLE IF NOT EXISTS import_issues (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                company_id INTEGER NOT NULL,
                import_id INTEGER,
                competence TEXT NOT NULL,
                issue_type TEXT NOT NULL,
                reference_value TEXT NOT NULL,
                status TEXT NOT NULL DEFAULT 'pendente',
                details_json TEXT,
                created_at TEXT NOT NULL,
                FOREIGN KEY (company_id) REFERENCES companies(id),
                FOREIGN KEY (import_id) REFERENCES imports(id)
            );

            CREATE TABLE IF NOT EXISTS fact_sales_detail (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                company_id INTEGER NOT NULL,
                competence TEXT NOT NULL,
                import_id INTEGER NOT NULL,
                row_hash TEXT NOT NULL,
                seller_name TEXT NOT NULL,
                client_name TEXT NOT NULL,
                city_name TEXT,
                gtin_value TEXT,
                manufacturer_sku TEXT,
                sku_key TEXT,
                issue_date TEXT,
                quantity REAL NOT NULL DEFAULT 0,
                gross_value REAL NOT NULL DEFAULT 0,
                discount_value REAL NOT NULL DEFAULT 0,
                freight_value REAL NOT NULL DEFAULT 0,
                return_quantity REAL NOT NULL DEFAULT 0,
                return_value REAL NOT NULL DEFAULT 0,
                net_value REAL NOT NULL DEFAULT 0,
                sale_share REAL NOT NULL DEFAULT 0,
                created_at TEXT NOT NULL,
                UNIQUE(company_id, competence, row_hash),
                FOREIGN KEY (company_id) REFERENCES companies(id),
                FOREIGN KEY (import_id) REFERENCES imports(id)
            );

            CREATE TABLE IF NOT EXISTS fact_vendor_summary (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                company_id INTEGER NOT NULL,
                competence TEXT NOT NULL,
                import_id INTEGER NOT NULL,
                row_hash TEXT NOT NULL,
                seller_name TEXT NOT NULL,
                qty_sold REAL NOT NULL DEFAULT 0,
                cost_value REAL NOT NULL DEFAULT 0,
                sale_value REAL NOT NULL DEFAULT 0,
                profit_value REAL NOT NULL DEFAULT 0,
                net_profit_value REAL NOT NULL DEFAULT 0,
                profit_pct REAL NOT NULL DEFAULT 0,
                return_cost REAL NOT NULL DEFAULT 0,
                return_value REAL NOT NULL DEFAULT 0,
                net_value REAL NOT NULL DEFAULT 0,
                margin_value REAL NOT NULL DEFAULT 0,
                created_at TEXT NOT NULL,
                UNIQUE(company_id, competence, row_hash),
                FOREIGN KEY (company_id) REFERENCES companies(id),
                FOREIGN KEY (import_id) REFERENCES imports(id)
            );

            CREATE TABLE IF NOT EXISTS fact_unit_summary (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                company_id INTEGER NOT NULL,
                competence TEXT NOT NULL,
                import_id INTEGER NOT NULL,
                row_hash TEXT NOT NULL,
                unit_name TEXT NOT NULL,
                qty_sold REAL NOT NULL DEFAULT 0,
                cost_value REAL NOT NULL DEFAULT 0,
                sale_value REAL NOT NULL DEFAULT 0,
                profit_value REAL NOT NULL DEFAULT 0,
                net_profit_value REAL NOT NULL DEFAULT 0,
                profit_pct REAL NOT NULL DEFAULT 0,
                return_cost REAL NOT NULL DEFAULT 0,
                return_value REAL NOT NULL DEFAULT 0,
                net_value REAL NOT NULL DEFAULT 0,
                margin_value REAL NOT NULL DEFAULT 0,
                created_at TEXT NOT NULL,
                UNIQUE(company_id, competence, row_hash),
                FOREIGN KEY (company_id) REFERENCES companies(id),
                FOREIGN KEY (import_id) REFERENCES imports(id)
            );

            CREATE TABLE IF NOT EXISTS audit_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                company_id INTEGER NOT NULL,
                user_id INTEGER,
                action TEXT NOT NULL,
                entity_type TEXT NOT NULL,
                entity_id TEXT NOT NULL,
                changes_json TEXT NOT NULL,
                created_at TEXT NOT NULL,
                FOREIGN KEY (company_id) REFERENCES companies(id),
                FOREIGN KEY (user_id) REFERENCES users(id)
            );

            CREATE INDEX IF NOT EXISTS idx_sales_company_competence
                ON fact_sales_detail(company_id, competence);

            CREATE INDEX IF NOT EXISTS idx_sales_company_seller_competence_client
                ON fact_sales_detail(company_id, seller_name, competence, client_name);

            CREATE INDEX IF NOT EXISTS idx_sales_company_client_competence
                ON fact_sales_detail(company_id, client_name, competence);

            CREATE INDEX IF NOT EXISTS idx_sales_company_seller_issue
                ON fact_sales_detail(company_id, seller_name, issue_date);

            CREATE INDEX IF NOT EXISTS idx_vendor_summary_company_competence_seller
                ON fact_vendor_summary(company_id, competence, seller_name);

            CREATE INDEX IF NOT EXISTS idx_unit_summary_company_competence_unit
                ON fact_unit_summary(company_id, competence, unit_name);
            """
        )
        init_crm_schema(conn)
        # Migração: Porto Alegre → Zona Sul (renomeação de unidade)
        _OLD_UNIT = "PORTOALEGRE"
        _NEW_UNIT = "ZONA SUL"
        try:
            conn.execute("UPDATE fact_sales_detail   SET unit_name  = ? WHERE unit_name  = ?", (_NEW_UNIT, _OLD_UNIT))
            conn.execute("UPDATE fact_vendor_summary SET unit_name  = ? WHERE unit_name  = ?", (_NEW_UNIT, _OLD_UNIT))
            conn.execute("UPDATE fact_unit_summary   SET unit_name  = ? WHERE unit_name  = ?", (_NEW_UNIT, _OLD_UNIT))
            conn.execute("UPDATE people_records      SET base_unit  = ? WHERE base_unit  = ?", (_NEW_UNIT, _OLD_UNIT))
            conn.execute("UPDATE goals_seller        SET unit_name  = ? WHERE unit_name  = ?", (_NEW_UNIT, _OLD_UNIT))
            conn.execute("UPDATE goals_unit          SET unit_name  = ? WHERE unit_name  = ?", (_NEW_UNIT, _OLD_UNIT))
            conn.execute("UPDATE city_unit_mapping   SET principal_unit = ? WHERE principal_unit = ?", (_NEW_UNIT, _OLD_UNIT))
            conn.commit()
        except sqlite3.OperationalError:
            pass  # tabela ainda não existe em ambientes novos
        conn.executescript("""
            CREATE TABLE IF NOT EXISTS auto_import_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ran_at TEXT NOT NULL,
                folder TEXT NOT NULL,
                scope TEXT NOT NULL,
                competence TEXT,
                status TEXT NOT NULL,
                message TEXT,
                files_json TEXT
            );
        """)
        user_columns = {row["name"] for row in conn.execute("PRAGMA table_info(users)").fetchall()}
        if "linked_person_name" not in user_columns:
            conn.execute("ALTER TABLE users ADD COLUMN linked_person_name TEXT")
            conn.commit()
        if "linked_units_json" not in user_columns:
            conn.execute("ALTER TABLE users ADD COLUMN linked_units_json TEXT")
            conn.commit()
        if "profile_id" not in user_columns:
            conn.execute("ALTER TABLE users ADD COLUMN profile_id INTEGER")
            conn.commit()
        try:
            conn.execute("UPDATE fact_vendor_summary SET margin_value = margin_value / 100 WHERE margin_value > 100")
            conn.execute("UPDATE fact_unit_summary SET margin_value = margin_value / 100 WHERE margin_value > 100")
        except sqlite3.OperationalError:
            # Some local test environments mount the sqlite file read-only.
            pass
        conn.commit()
        company = conn.execute("SELECT id FROM companies WHERE name = ?", (DEFAULT_COMPANY,)).fetchone()
        if not company:
            conn.execute("INSERT INTO companies (name, code, created_at) VALUES (?, ?, ?)", (DEFAULT_COMPANY, "PASSINI", now_iso()))
            conn.commit()
            company = conn.execute("SELECT id FROM companies WHERE name = ?", (DEFAULT_COMPANY,)).fetchone()
        company_id = company["id"]

        seed_access_profiles(conn, company_id)
        seed_content_library(conn, company_id)

        user = conn.execute("SELECT id FROM users WHERE username = ?", (DEFAULT_ADMIN_USER,)).fetchone()
        if not user:
            pwd_hash, salt = pbkdf2_hash(DEFAULT_ADMIN_PASSWORD)
            conn.execute(
                """
                INSERT INTO users (company_id, username, full_name, linked_person_name, password_hash, password_salt, role, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (company_id, DEFAULT_ADMIN_USER, "Administrador padrão", None, pwd_hash, salt, "Administrador", now_iso()),
            )
            conn.commit()

        score = conn.execute("SELECT id FROM score_configs WHERE company_id = ?", (company_id,)).fetchone()
        if not score:
            conn.execute(
                """
                INSERT INTO score_configs (
                    company_id, valid_from_competence, valid_to_competence,
                    weight_goal, weight_ticket, weight_clients, weight_mix, weight_returns, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (company_id, "2025-01", None, 30, 15, 15, 15, 25, now_iso()),
            )
            conn.commit()

        seed_holidays(conn, company_id)
        seed_mapping_workbook(conn, company_id)
        seed_crm_catalogs(conn)
        sanitize_unit_goals(conn, company_id)
        conn.commit()


def seed_holidays(conn: sqlite3.Connection, company_id: int) -> None:
    existing = conn.execute("SELECT COUNT(*) AS total FROM holidays WHERE company_id = ?", (company_id,)).fetchone()["total"]
    if existing:
        return
    for year, rows in NATIONAL_AND_RS_HOLIDAYS.items():
        for holiday_date, holiday_name in rows:
            conn.execute(
                """
                INSERT OR IGNORE INTO holidays (company_id, holiday_date, holiday_name, scope, created_at)
                VALUES (?, ?, ?, 'NACIONAL_RS', ?)
                """,
                (company_id, holiday_date, holiday_name, now_iso()),
            )
    conn.commit()


def infer_role_from_name(person_name: str) -> str:
    upper = normalize_upper(person_name)
    if "(VENDAS)" in upper or "(TELEVENDAS)" in upper or "(VAREJO)" in upper:
        return "Vendedor"
    if "GERENTE" in upper:
        return "Gerente"
    return "Outro"


def seed_mapping_workbook(conn: sqlite3.Connection, company_id: int) -> None:
    if not PASSINI_MAPPING_WORKBOOK.exists():
        return
    people_count = conn.execute("SELECT COUNT(*) AS total FROM people_records WHERE company_id = ?", (company_id,)).fetchone()["total"]
    city_count = conn.execute("SELECT COUNT(*) AS total FROM city_mappings WHERE company_id = ?", (company_id,)).fetchone()["total"]
    if people_count and city_count:
        return
    workbook = openpyxl.load_workbook(PASSINI_MAPPING_WORKBOOK, data_only=True)
    if not people_count and "VENDEDOR X UNIDADE" in workbook.sheetnames:
        sheet = workbook["VENDEDOR X UNIDADE"]
        for row in sheet.iter_rows(min_row=2, values_only=True):
            person_name = normalize_whitespace(row[1] if len(row) > 1 else None)
            if not person_name:
                continue
            base_unit = normalize_unit(row[3] if len(row) > 3 and row[3] else row[2] if len(row) > 2 else "")
            conn.execute(
                """
                INSERT OR IGNORE INTO people_records
                    (company_id, person_name, role_classification, base_unit, valid_from, valid_to, source, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (company_id, person_name, infer_role_from_name(person_name), base_unit, "2025-01-01", None, "planilha_apoio", now_iso()),
            )
    if not city_count and "cidade x unidade" in workbook.sheetnames:
        sheet = workbook["cidade x unidade"]
        for row in sheet.iter_rows(min_row=3, values_only=True):
            city_name = normalize_upper(row[0] if len(row) > 0 else None)
            if not city_name:
                continue
            principal_unit = normalize_unit(row[1] if len(row) > 1 else None)
            state_name = normalize_upper(row[2] if len(row) > 2 else None)
            country_name = normalize_upper(row[3] if len(row) > 3 else None)
            conn.execute(
                """
                INSERT OR IGNORE INTO city_mappings
                    (company_id, city_name, principal_unit, state_name, country_name, valid_from, valid_to, source, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (company_id, city_name, principal_unit, state_name, country_name, "2025-01-01", None, "planilha_apoio", now_iso()),
            )
    conn.commit()


def get_company_id(conn: sqlite3.Connection) -> int:
    return conn.execute("SELECT id FROM companies WHERE name = ?", (DEFAULT_COMPANY,)).fetchone()["id"]


def current_role_and_unit(conn: sqlite3.Connection, company_id: int, person_name: str, competence: str | None = None) -> tuple[str | None, str | None]:
    competence = competence or date.today().strftime("%Y-%m")
    target = first_day_of_competence(competence).isoformat()
    row = conn.execute(
        """
        SELECT role_classification, base_unit
        FROM people_records
        WHERE company_id = ? AND person_name = ? AND date(valid_from) <= date(?)
          AND (valid_to IS NULL OR date(valid_to) >= date(?))
        ORDER BY date(valid_from) DESC
        LIMIT 1
        """,
        (company_id, person_name, target, target),
    ).fetchone()
    if row:
        return row["role_classification"], row["base_unit"]
    return None, None


def resolve_city_unit(conn: sqlite3.Connection, company_id: int, city_name: str | None, competence: str | None = None) -> str | None:
    normalized_city = normalize_upper(city_name)
    if not normalized_city:
        return None
    competence = competence or date.today().strftime("%Y-%m")
    target = first_day_of_competence(competence).isoformat()
    row = conn.execute(
        """
        SELECT principal_unit
        FROM city_mappings
        WHERE company_id = ? AND city_name = ? AND date(valid_from) <= date(?)
          AND (valid_to IS NULL OR date(valid_to) >= date(?))
        ORDER BY date(valid_from) DESC
        LIMIT 1
        """,
        (company_id, normalized_city, target, target),
    ).fetchone()
    if row:
        return normalize_unit(row["principal_unit"])
    return None


def build_city_unit_map(conn: sqlite3.Connection, company_id: int, competence: str | None = None) -> dict[str, str | None]:
    """Precarrega todos os mapeamentos cidade→unidade em um dict para evitar N+1 queries."""
    competence = competence or date.today().strftime("%Y-%m")
    target = first_day_of_competence(competence).isoformat()
    rows = conn.execute(
        """
        SELECT city_name, principal_unit
        FROM city_mappings
        WHERE company_id = ? AND date(valid_from) <= date(?)
          AND (valid_to IS NULL OR date(valid_to) >= date(?))
        ORDER BY city_name, date(valid_from) DESC
        """,
        (company_id, target, target),
    ).fetchall()
    # Mantém apenas o mapeamento mais recente por cidade (ORDER BY garante isso)
    city_map: dict[str, str | None] = {}
    for row in rows:
        city = normalize_upper(row["city_name"])
        if city and city not in city_map:
            city_map[city] = normalize_unit(row["principal_unit"])
    return city_map


def projection_metrics(realized_value: float, elapsed_days: int, total_days: int) -> tuple[float, float]:
    if elapsed_days <= 0 or total_days <= 0:
        return realized_value, 0.0
    projected = realized_value / elapsed_days * total_days
    pace_pct = projected / realized_value * 100 if realized_value else 0.0
    return projected, pace_pct


def dashboard_metric_projection(realized_value: float, elapsed_days: int, total_days: int) -> tuple[float, float]:
    if elapsed_days <= 0 or total_days <= 0:
        return 0.0, 0.0
    daily_actual = safe_div(realized_value, elapsed_days)
    projected = daily_actual * total_days
    return daily_actual, projected


def load_goal_maps(
    conn: sqlite3.Connection,
    company_id: int,
    competence: str,
    table_name: str,
    key_field: str,
    normalizer,
) -> tuple[dict[str, dict[str, Any]], list[dict[str, Any]]]:
    rows = conn.execute(
        f"""
        SELECT id, competence, {key_field} AS goal_key, revenue_goal, returns_goal
        FROM {table_name}
        WHERE company_id = ? AND competence = ?
        ORDER BY id DESC
        """,
        (company_id, competence),
    ).fetchall()
    latest_by_raw: dict[str, sqlite3.Row] = {}
    duplicate_raw: list[dict[str, Any]] = []
    raw_counts: dict[str, int] = defaultdict(int)
    raw_totals: dict[str, float] = defaultdict(float)
    for row in rows:
        raw_key = normalize_whitespace(row["goal_key"])
        raw_counts[raw_key] += 1
        raw_totals[raw_key] += float(row["revenue_goal"] or 0.0)
        if raw_key not in latest_by_raw:
            latest_by_raw[raw_key] = row
    for raw_key, count in raw_counts.items():
        if count > 1:
            duplicate_raw.append(
                {
                    "competence": competence,
                    "key": raw_key,
                    "count": count,
                    "summedRevenueGoal": round(raw_totals[raw_key], 2),
                    "table": table_name,
                }
            )
    aggregated: dict[str, dict[str, Any]] = {}
    for raw_key, row in latest_by_raw.items():
        normalized_key = normalizer(raw_key)
        if not normalized_key:
            continue
        bucket = aggregated.setdefault(
            normalized_key,
            {
                "revenueGoal": 0.0,
                "returnsGoal": 0.0,
                "sourceKeys": [],
            },
        )
        bucket["revenueGoal"] += float(row["revenue_goal"] or 0.0)
        bucket["returnsGoal"] += float(row["returns_goal"] or 0.0)
        bucket["sourceKeys"].append(raw_key)
    for bucket in aggregated.values():
        bucket["revenueGoal"] = round(bucket["revenueGoal"], 2)
        bucket["returnsGoal"] = round(bucket["returnsGoal"], 2)
        bucket["sourceKeys"].sort()
    return aggregated, duplicate_raw


def normalized_goal_duplicates(
    conn: sqlite3.Connection,
    company_id: int,
    table_name: str,
    key_field: str,
    normalizer,
    competence: str | None = None,
) -> list[dict[str, Any]]:
    sql = f"""
        SELECT id, competence, {key_field} AS goal_key, revenue_goal, created_at
        FROM {table_name}
        WHERE company_id = ?
    """
    params: list[Any] = [company_id]
    if competence:
        sql += " AND competence = ?"
        params.append(competence)
    sql += " ORDER BY competence DESC, id DESC"
    rows = conn.execute(sql, params).fetchall()
    grouped: dict[tuple[str, str], list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        raw_key = normalize_whitespace(row["goal_key"])
        normalized_key = normalizer(raw_key)
        if not normalized_key:
            continue
        grouped[(row["competence"], normalized_key)].append(
            {
                "id": row["id"],
                "goalKey": raw_key,
                "revenueGoal": audit_round(row["revenue_goal"]),
                "createdAt": row["created_at"],
            }
        )
    duplicates: list[dict[str, Any]] = []
    for (row_competence, normalized_key), duplicate_rows in grouped.items():
        if len(duplicate_rows) <= 1:
            continue
        duplicates.append(
            {
                "competence": row_competence,
                "normalizedKey": normalized_key,
                "rows": duplicate_rows,
            }
        )
    duplicates.sort(key=lambda item: (item["competence"], item["normalizedKey"]), reverse=True)
    return duplicates


def sanitize_unit_goals(conn: sqlite3.Connection, company_id: int, actor_user_id: int | None = None) -> list[dict[str, Any]]:
    rows = conn.execute(
        """
        SELECT id, competence, unit_name, revenue_goal, returns_goal, created_at
        FROM goals_unit
        WHERE company_id = ?
        ORDER BY competence DESC, datetime(created_at) DESC, id DESC
        """,
        (company_id,),
    ).fetchall()
    grouped: dict[tuple[str, str], list[sqlite3.Row]] = defaultdict(list)
    for row in rows:
        grouped[(row["competence"], normalize_unit(row["unit_name"]))].append(row)

    changes_made: list[dict[str, Any]] = []
    for (competence, normalized_unit), group_rows in grouped.items():
        if not normalized_unit:
            continue
        distinct_values = {
            (audit_round(row["revenue_goal"]), audit_round(row["returns_goal"]))
            for row in group_rows
        }
        prefer_latest = len(distinct_values) > 1
        sorted_rows = sorted(
            group_rows,
            key=lambda row: (
                row["created_at"] or "",
                row["id"],
            )
            if prefer_latest
            else (
                1 if normalize_whitespace(row["unit_name"]) == normalized_unit else 0,
                row["created_at"] or "",
                row["id"],
            ),
            reverse=True,
        )
        kept_row = sorted_rows[0]
        deleted_rows = sorted_rows[1:]
        needs_update = normalize_whitespace(kept_row["unit_name"]) != normalized_unit
        if not deleted_rows and not needs_update:
            continue
        if needs_update:
            conn.execute(
                "UPDATE goals_unit SET unit_name = ? WHERE id = ?",
                (normalized_unit, kept_row["id"]),
            )
        deleted_ids: list[int] = []
        if deleted_rows:
            deleted_ids = [int(row["id"]) for row in deleted_rows]
            placeholders = ", ".join("?" for _ in deleted_ids)
            conn.execute(f"DELETE FROM goals_unit WHERE id IN ({placeholders})", deleted_ids)
        values = [
            {
                "id": int(row["id"]),
                "unitName": row["unit_name"],
                "revenueGoal": audit_round(row["revenue_goal"]),
            }
            for row in group_rows
        ]
        audit_payload = {
            "competence": competence,
            "normalizedUnit": normalized_unit,
            "keptId": int(kept_row["id"]),
            "deletedIds": deleted_ids,
            "values": values,
        }
        audit_log(
            conn,
            company_id,
            actor_user_id,
            "sanitize_unit_goals",
            "goals_unit",
            f"{competence}:{normalized_unit}",
            audit_payload,
        )
        changes_made.append(audit_payload)
    return changes_made


def delete_goal_unit_record(
    conn: sqlite3.Connection,
    company_id: int,
    actor_user_id: int | None,
    competence: str,
    unit_name: str,
) -> None:
    normalized_unit = normalize_unit(unit_name)
    row = conn.execute(
        """
        SELECT id, revenue_goal, returns_goal
        FROM goals_unit
        WHERE company_id = ? AND competence = ? AND unit_name = ?
        """,
        (company_id, competence, normalized_unit),
    ).fetchone()
    if not row:
        raise ValueError("Meta da unidade não encontrada.")
    conn.execute(
        "DELETE FROM goals_unit WHERE company_id = ? AND competence = ? AND unit_name = ?",
        (company_id, competence, normalized_unit),
    )
    audit_log(
        conn,
        company_id,
        actor_user_id,
        "delete_goal_unit",
        "goals_unit",
        f"{competence}:{normalized_unit}",
        {
            "competence": competence,
            "unitName": normalized_unit,
            "deletedId": int(row["id"]),
            "revenueGoal": audit_round(row["revenue_goal"]),
            "returnsGoal": audit_round(row["returns_goal"]),
        },
    )


def delete_goal_seller_record(
    conn: sqlite3.Connection,
    company_id: int,
    actor_user_id: int | None,
    competence: str,
    seller_name: str,
) -> None:
    normalized_seller = normalize_whitespace(seller_name)
    row = conn.execute(
        """
        SELECT id, revenue_goal, returns_goal
        FROM goals_seller
        WHERE company_id = ? AND competence = ? AND seller_name = ?
        """,
        (company_id, competence, normalized_seller),
    ).fetchone()
    if not row:
        raise ValueError("Meta do vendedor não encontrada.")
    conn.execute(
        "DELETE FROM goals_seller WHERE company_id = ? AND competence = ? AND seller_name = ?",
        (company_id, competence, normalized_seller),
    )
    audit_log(
        conn,
        company_id,
        actor_user_id,
        "delete_goal_seller",
        "goals_seller",
        f"{competence}:{normalized_seller}",
        {
            "competence": competence,
            "sellerName": normalized_seller,
            "deletedId": int(row["id"]),
            "revenueGoal": audit_round(row["revenue_goal"]),
            "returnsGoal": audit_round(row["returns_goal"]),
        },
    )


def get_score_config(conn: sqlite3.Connection, company_id: int, competence: str) -> sqlite3.Row:
    row = conn.execute(
        """
        SELECT *
        FROM score_configs
        WHERE company_id = ? AND valid_from_competence <= ?
          AND (valid_to_competence IS NULL OR valid_to_competence >= ?)
        ORDER BY valid_from_competence DESC
        LIMIT 1
        """,
        (company_id, competence, competence),
    ).fetchone()
    if row:
        return row
    return conn.execute("SELECT * FROM score_configs WHERE company_id = ? ORDER BY valid_from_competence DESC LIMIT 1", (company_id,)).fetchone()


def decode_text_content(content: bytes) -> str:
    encodings = ["utf-8-sig", "utf-8", "cp1252", "latin-1"]
    last_error: UnicodeDecodeError | None = None
    for encoding in encodings:
        try:
            return content.decode(encoding)
        except UnicodeDecodeError as exc:
            last_error = exc
    if last_error:
        raise last_error
    return content.decode("utf-8", errors="replace")


def parse_csv_bytes(content: bytes) -> list[dict[str, str]]:
    text = decode_text_content(content)
    reader = csv.DictReader(io.StringIO(text, newline=""), delimiter=";")
    return [dict(row) for row in reader]


def file_hash(content: bytes) -> str:
    return hashlib.sha256(content).hexdigest()


def detect_file_type(filename: str) -> str | None:
    clean = Path(filename).name
    clean_lower = clean.lower()
    if clean_lower in {key.lower() for key in CSV_FILE_TYPES}:
        for key, value in CSV_FILE_TYPES.items():
            if key.lower() == clean_lower:
                return value
    stem_lower = Path(filename).stem.lower()
    aliases = {
        "01fat": "faturamento_detalhado",
        "02unidade": "custo_unidade",
        "03vendedor": "custo_vendedor",
        "030-relatoriofaturamento detalhado": "faturamento_detalhado",
        "030-relatoriofaturamento conslidado cliente": "faturamento_cliente_consolidado",
        "030-relatoriofaturamento consolidado cliente": "faturamento_cliente_consolidado",
        "030-relatoriopessoas": "cadastro_clientes",
        "030-relatoriodevolucao": "devolucao_garantia",
        "030-relatoriocustovenda unidade": "custo_unidade",
        "030-relatoriocustovenda vendedor consolidado": "custo_vendedor",
    }
    alias_match = aliases.get(stem_lower)
    if alias_match:
        return alias_match
    if re.fullmatch(r"030-relatoriocustovenda\(\d+\)", stem_lower):
        # Não distingue unidade de vendedor pelo nome — campo do formulário já faz isso via override
        return "custo_unidade"  # fallback conservador; fieldName override tem prioridade
    if re.fullmatch(r"030-relatoriofaturamento\(\d+\)", stem_lower):
        return "faturamento_detalhado"
    if re.fullmatch(r"030-relatoriofaturamento detalhado\(\d+\)", stem_lower):
        return "faturamento_detalhado"
    if re.fullmatch(r"030-relatoriofaturamento detalhado \(\d+\)", stem_lower):
        return "faturamento_detalhado"
    if re.fullmatch(r"030-relatoriofaturamento conslidado cliente\(\d+\)", stem_lower):
        return "faturamento_cliente_consolidado"
    if re.fullmatch(r"030-relatoriofaturamento conslidado cliente \(\d+\)", stem_lower):
        return "faturamento_cliente_consolidado"
    if re.fullmatch(r"030-relatoriofaturamento consolidado cliente\(\d+\)", stem_lower):
        return "faturamento_cliente_consolidado"
    if re.fullmatch(r"030-relatoriofaturamento consolidado cliente \(\d+\)", stem_lower):
        return "faturamento_cliente_consolidado"
    if re.fullmatch(r"030-relatoriopessoas\(\d+\)", stem_lower):
        return "cadastro_clientes"
    if re.fullmatch(r"030-relatoriopessoas \(\d+\)", stem_lower):
        return "cadastro_clientes"
    return None


def normalize_upload_entries(files_payload: dict[str, bytes] | list[dict[str, Any]]) -> list[dict[str, Any]]:
    if isinstance(files_payload, dict):
        return [{"fieldName": "files", "fileName": filename, "content": content} for filename, content in files_payload.items()]
    return files_payload


def detect_upload_file_type(file_name: str, field_name: str | None = None) -> str | None:
    override = UPLOAD_FIELD_TYPE_OVERRIDES.get(field_name or "")
    if override:
        return override
    return detect_file_type(file_name)


def suggest_competence(rows: list[dict[str, str]]) -> str | None:
    counts = Counter()
    for row in rows:
        dt_value = parse_sales_row_date(row)
        competence = competence_from_date(dt_value)
        if competence:
            counts[competence] += 1
    if not counts:
        return None
    return counts.most_common(1)[0][0]


def normalize_sku(gtin_value: str | None, manufacturer_sku: str | None) -> str:
    gtin = normalize_whitespace(gtin_value)
    manufacturer = normalize_whitespace(manufacturer_sku)
    return gtin or manufacturer or "SKU_DESCONHECIDO"


def seller_should_be_counted(conn: sqlite3.Connection, company_id: int, seller_name: str, competence: str) -> bool:
    role, _ = current_role_and_unit(conn, company_id, seller_name, competence)
    if role is None:
        return True
    return role == "Vendedor"


def register_issue(conn: sqlite3.Connection, company_id: int, import_id: int, competence: str, issue_type: str, reference_value: str, details: dict[str, Any]) -> None:
    exists = conn.execute(
        """
        SELECT id FROM import_issues
        WHERE company_id = ? AND competence = ? AND issue_type = ? AND reference_value = ? AND status = 'pendente'
        """,
        (company_id, competence, issue_type, reference_value),
    ).fetchone()
    if exists:
        return
    conn.execute(
        """
        INSERT INTO import_issues (company_id, import_id, competence, issue_type, reference_value, details_json, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        (company_id, import_id, competence, issue_type, reference_value, json.dumps(details, ensure_ascii=False), now_iso()),
    )


def normalize_import_scope(value: str | None) -> str:
    scope = normalize_whitespace(value).lower()
    return scope if scope in IMPORT_SCOPE_REQUIREMENTS else "full"


def preview_import_package(files_payload: dict[str, bytes] | list[dict[str, Any]], import_scope: str = "full") -> dict[str, Any]:
    import_scope = normalize_import_scope(import_scope)
    required_file_types = IMPORT_SCOPE_REQUIREMENTS[import_scope]
    file_types = {}
    row_counts = {}
    files_meta = []
    suggested_values = []
    missing = []
    unsupported_files = []

    for entry in normalize_upload_entries(files_payload):
        filename = entry["fileName"]
        field_name = entry.get("fieldName")
        content = entry["content"]
        extension = Path(filename).suffix.lower()
        if extension and extension != ".csv":
            unsupported_files.append({"fileName": filename, "fieldName": field_name, "reason": "Formato inválido. Use CSV."})
            continue
        kind = detect_upload_file_type(filename, field_name)
        if not kind:
            continue
        rows = parse_csv_bytes(content)
        # Detecção pelo conteúdo: custo venda com nome genérico (NNNN) distingue por coluna
        if kind == "custo_unidade" and rows:
            first_col = (list(rows[0].keys()) or [""])[0].strip().upper()
            if first_col in {"VENDEDOR", "VENDEDOR CONSOLIDADO"}:
                kind = "custo_vendedor"
        file_types[kind] = rows
        row_counts[kind] = row_counts.get(kind, 0) + len(rows)
        files_meta.append({"fileName": filename, "fieldName": field_name, "fileType": kind, "rows": len(rows), "hash": file_hash(content)})
        if import_scope == "cost":
            suggested_values.append(date.today().strftime("%Y-%m"))
        elif kind == "faturamento_detalhado" and import_scope in {"full", "sales"}:
            suggestion = suggest_competence(rows)
            if suggestion:
                suggested_values.append(suggestion)
        elif kind == "devolucao_garantia":
            # Competência mais frequente pela data da devolução
            counts = Counter()
            for r in rows:
                dt = parse_datetime_pt(r.get("Data")) or parse_datetime_flexible(r.get("Data"))
                comp = competence_from_date(dt)
                if comp:
                    counts[comp] += 1
            if counts:
                suggested_values.append(counts.most_common(1)[0][0])

    detected_file_types = set(file_types)
    if import_scope == "crm":
        if not detected_file_types:
            missing = sorted(required_file_types)
    else:
        for required in required_file_types:
            if required not in file_types:
                missing.append(required)

    suggestion = Counter(suggested_values).most_common(1)[0][0] if suggested_values else None
    return {
        "isValid": len(missing) == 0 and len(unsupported_files) == 0 and bool(detected_file_types),
        "importScope": import_scope,
        "importScopeLabel": IMPORT_SCOPE_LABELS[import_scope],
        "missingFileTypes": missing,
        "unsupportedFiles": unsupported_files,
        "suggestedCompetence": suggestion,
        "rowCounts": row_counts,
        "files": files_meta,
        "detectedFileTypes": sorted(detected_file_types),
    }


def delete_competence_data(
    conn: sqlite3.Connection,
    company_id: int,
    competence: str,
    file_types: set[str] | None = None,
) -> None:
    selected_file_types = file_types or set(IMPORT_SCOPE_TABLES)
    # Cadastro de clientes: base mestre sem competência — substitui TODA a base anterior.
    if "cadastro_clientes" in selected_file_types:
        conn.execute("DELETE FROM crm_client_profiles WHERE company_id = ?", (company_id,))
    # Faturamento consolidado por cliente: competência vem do nome do arquivo — substitui só o mês.
    if "faturamento_cliente_consolidado" in selected_file_types:
        conn.execute(
            "DELETE FROM crm_client_summary WHERE company_id = ? AND competence = ?",
            (company_id, competence),
        )
    target_tables = set()
    for file_type in selected_file_types:
        # APPEND-ONLY: competência derivada da data de cada linha e dedupe por row_hash.
        # Nunca apagar o histórico dessas tabelas.
        if file_type in {
            "cadastro_clientes", "faturamento_cliente_consolidado",
            "faturamento_detalhado", "devolucao_garantia",
        }:
            continue
        target_tables.update(IMPORT_SCOPE_TABLES.get(file_type, ()))
    for table in target_tables:
        conn.execute(f"DELETE FROM {table} WHERE company_id = ? AND competence = ?", (company_id, competence))


def import_package(
    conn: sqlite3.Connection,
    company_id: int,
    user_id: int,
    competence: str,
    import_action: str,
    import_scope: str,
    preview: dict[str, Any],
    files_payload: dict[str, bytes] | list[dict[str, Any]],
) -> dict[str, Any]:
    import_scope = normalize_import_scope(import_scope)
    selected_file_types = {
        item["fileType"]
        for item in preview.get("files", [])
        if item.get("fileType")
    }
    actual_action = import_action or "substituir"
    # Guarda a contagem anterior da base de clientes para detectar exportação incompleta
    clients_before = 0
    if "cadastro_clientes" in selected_file_types:
        clients_before = int(conn.execute(
            "SELECT COUNT(*) FROM crm_client_profiles WHERE company_id = ?", (company_id,)
        ).fetchone()[0] or 0)
    if actual_action == "substituir":
        delete_competence_data(conn, company_id, competence, selected_file_types)

    import_cursor = conn.execute(
        """
        INSERT INTO imports (company_id, competence, import_action, suggested_competence, imported_by, imported_at)
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (company_id, competence, actual_action, preview.get("suggestedCompetence"), user_id, now_iso()),
    )
    import_id = import_cursor.lastrowid

    duplicate_rows_skipped = 0
    sales_competences_seen: set[str] = set()
    sales_rows_by_competence: Counter = Counter()
    sales_rows_without_date = 0
    warranty_competences_seen: set[str] = set()
    warranty_total_value = 0.0

    for entry in normalize_upload_entries(files_payload):
        filename = entry["fileName"]
        field_name = entry.get("fieldName")
        content = entry["content"]
        kind = detect_upload_file_type(filename, field_name)
        if not kind:
            continue
        rows = parse_csv_bytes(content)
        # Um mesmo import pode receber VÁRIOS arquivos do mesmo tipo (ex.: a base de
        # clientes do Alfa vem em duas exportações complementares). O UNIQUE
        # (import_id, file_type) é preservado acumulando nomes e contagem de linhas.
        conn.execute(
            """
            INSERT INTO import_files (import_id, file_type, original_name, file_hash, row_count)
            VALUES (?, ?, ?, ?, ?)
            ON CONFLICT(import_id, file_type) DO UPDATE SET
                original_name = original_name || ' + ' || excluded.original_name,
                file_hash = excluded.file_hash,
                row_count = row_count + excluded.row_count
            """,
            (import_id, kind, filename, file_hash(content), len(rows)),
        )

        if kind == "faturamento_detalhado":
            # Duas vendas idênticas no mesmo dia são possíveis (mesma peça, mesmo
            # cliente, dois atendimentos). O contador de ocorrência evita descartar
            # a segunda como duplicata, mantendo o dedupe de reimportação.
            sales_occurrence: Counter = Counter()
            for row in rows:
                seller_name = normalize_whitespace(row.get("Vendedor"))
                client_name = normalize_whitespace(row.get("Cliente") or row.get("CLIENTE") or row.get("Razao Social/Nome")) or "CLIENTE NÃO INFORMADO"
                city_name = normalize_upper(row.get("Cidade"))
                gtin_value = normalize_whitespace(row.get(""))
                manufacturer_sku = normalize_whitespace(row.get("Fabricante"))
                dt_value = parse_sales_row_date(row)
                # Competência POR LINHA, derivada da data de emissão. Um único arquivo
                # pode conter vários meses; cada linha vai para o mês correto.
                row_competence = competence_from_date(dt_value) or competence
                if not competence_from_date(dt_value):
                    sales_rows_without_date += 1
                sales_competences_seen.add(row_competence)
                sales_rows_by_competence[row_competence] += 1
                sku_key = normalize_sku(gtin_value, manufacturer_sku)
                payload = {
                    "seller": seller_name,
                    "client": client_name,
                    "city": city_name,
                    "gtin": gtin_value,
                    "manufacturer": manufacturer_sku,
                    "issue_date": dt_value.isoformat() if dt_value else "",
                    "quantity": parse_decimal(row.get("Quant.")),
                    "gross": parse_decimal(row.get("Bruto")),
                    "discount": parse_decimal(row.get("Desconto")),
                    "freight": parse_decimal(row.get("Frete")),
                    "qty_return": parse_decimal(row.get("QTD. Dev.")),
                    "value_return": parse_decimal(row.get("vlr. dev.")),
                    "net": parse_decimal(row.get("Liquido")),
                    "sale_share": parse_decimal(row.get("%venda")),
                }
                _sig = json.dumps(payload, ensure_ascii=False, sort_keys=True)
                sales_occurrence[_sig] += 1
                row_hash = hash_text(f"{_sig}#{sales_occurrence[_sig]}")
                try:
                    conn.execute(
                        """
                        INSERT INTO fact_sales_detail (
                            company_id, competence, import_id, row_hash, seller_name, client_name, city_name,
                            gtin_value, manufacturer_sku, sku_key, issue_date, quantity, gross_value,
                            discount_value, freight_value, return_quantity, return_value, net_value, sale_share, created_at
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                        """,
                        (
                            company_id,
                            row_competence,
                            import_id,
                            row_hash,
                            seller_name,
                            client_name,
                            city_name,
                            gtin_value,
                            manufacturer_sku,
                            sku_key,
                            dt_value.isoformat() if dt_value else None,
                            payload["quantity"],
                            payload["gross"],
                            payload["discount"],
                            payload["freight"],
                            payload["qty_return"],
                            payload["value_return"],
                            payload["net"],
                            payload["sale_share"],
                            now_iso(),
                        ),
                    )
                except sqlite3.IntegrityError:
                    duplicate_rows_skipped += 1
                role, _ = current_role_and_unit(conn, company_id, seller_name, row_competence)
                if role is None:
                    register_issue(conn, company_id, import_id, row_competence, "vendedor_sem_vinculo", seller_name, {"kind": "seller"})
                if city_name:
                    _comp_day = first_day_of_competence(row_competence).isoformat()
                    city_match = conn.execute(
                        """
                        SELECT id FROM city_mappings
                        WHERE company_id = ? AND city_name = ? AND date(valid_from) <= date(?)
                          AND (valid_to IS NULL OR date(valid_to) >= date(?))
                        LIMIT 1
                        """,
                        (company_id, city_name, _comp_day, _comp_day),
                    ).fetchone()
                    if not city_match:
                        register_issue(conn, company_id, import_id, row_competence, "cidade_sem_correspondencia", city_name, {"kind": "city"})
        elif kind == "cadastro_clientes":
            for row in rows:
                client_code = normalize_whitespace(row.get("Codigo"))
                client_name = normalize_whitespace(row.get("Razao Social/Nome"))
                if not client_code or not client_name:
                    continue
                conn.execute(
                    """
                    INSERT INTO crm_client_profiles (
                        company_id, client_code, client_name, trade_name, document_number, state_registration,
                        address_line, address_number, neighborhood, city_name, state_name, phone, postal_code,
                        first_sale_at, last_sale_at, credit_limit, economic_group, internal_seller_name,
                        external_seller_name, email, source_import_id, updated_at, created_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ON CONFLICT(company_id, client_code) DO UPDATE SET
                        client_name = excluded.client_name,
                        trade_name = excluded.trade_name,
                        document_number = excluded.document_number,
                        state_registration = excluded.state_registration,
                        address_line = excluded.address_line,
                        address_number = excluded.address_number,
                        neighborhood = excluded.neighborhood,
                        city_name = excluded.city_name,
                        state_name = excluded.state_name,
                        phone = excluded.phone,
                        postal_code = excluded.postal_code,
                        first_sale_at = excluded.first_sale_at,
                        last_sale_at = excluded.last_sale_at,
                        credit_limit = excluded.credit_limit,
                        economic_group = excluded.economic_group,
                        internal_seller_name = excluded.internal_seller_name,
                        external_seller_name = excluded.external_seller_name,
                        email = excluded.email,
                        source_import_id = excluded.source_import_id,
                        updated_at = excluded.updated_at
                    """,
                    (
                        company_id,
                        client_code,
                        client_name,
                        normalize_whitespace(row.get("Fantasia")),
                        normalize_whitespace(row.get("CNPJ/CPF")),
                        normalize_whitespace(row.get("IE")),
                        normalize_whitespace(row.get("Endereco")),
                        normalize_whitespace(row.get("Num")),
                        normalize_whitespace(row.get("Bairro")),
                        normalize_upper(row.get("Cidade")),
                        normalize_upper(row.get("Uf")),
                        normalize_whitespace(row.get("Telefone")),
                        normalize_whitespace(row.get("CEP")),
                        parse_datetime_flexible(row.get("Primeira Venda")).isoformat() if parse_datetime_flexible(row.get("Primeira Venda")) else None,
                        parse_datetime_flexible(row.get("Ultima Venda")).isoformat() if parse_datetime_flexible(row.get("Ultima Venda")) else None,
                        parse_decimal(row.get("Limite Credito")),
                        normalize_whitespace(row.get("Grupo Economico")),
                        normalize_whitespace(row.get("Vend. Interno")),
                        normalize_whitespace(row.get("Vend. Externo")),
                        normalize_whitespace(row.get("Email")),
                        import_id,
                        now_iso(),
                        now_iso(),
                    ),
                )
        elif kind == "faturamento_cliente_consolidado":
            for row in rows:
                client_code = normalize_whitespace(row.get("CODIGO"))
                client_name = normalize_whitespace(row.get("CLIENTE"))
                if not client_code or not client_name:
                    continue
                dt_value = parse_datetime_flexible(row.get("ULT.COMPRA"))
                try:
                    conn.execute(
                        """
                        INSERT INTO crm_client_summary (
                            company_id, competence, import_id, client_code, client_name, seller_name,
                            city_name, last_purchase_at, gross_value, discount_value, freight_value,
                            return_quantity, return_value, net_value, sale_share, created_at
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                        """,
                        (
                            company_id,
                            competence,
                            import_id,
                            client_code,
                            client_name,
                            normalize_whitespace(row.get("Vendedor")),
                            normalize_upper(row.get("Cidade")),
                            dt_value.isoformat() if dt_value else None,
                            parse_decimal(row.get("Bruto")),
                            parse_decimal(row.get("Desconto")),
                            parse_decimal(row.get("Frete")),
                            parse_decimal(row.get("QTD. Dev.")),
                            parse_decimal(row.get("vlr. dev.")),
                            parse_decimal(row.get("Liquido")),
                            parse_decimal(row.get("%venda")),
                            now_iso(),
                        ),
                    )
                except sqlite3.IntegrityError:
                    duplicate_rows_skipped += 1
        elif kind == "custo_vendedor":
            for row in rows:
                seller_name = normalize_whitespace(row.get("VENDEDOR"))
                payload = {
                    "seller": seller_name,
                    "qty_sold": parse_decimal(row.get("QTD VENDIDA")),
                    "cost": parse_decimal(row.get("CUSTO")),
                    "sale": parse_decimal(row.get("VENDA")),
                    "profit": parse_decimal(row.get("R$ LUCRO")),
                    "net_profit": parse_decimal(row.get("R$ LUCRO LIQUIDO")),
                    "profit_pct": parse_decimal(row.get("% LUCRO")),
                    "return_cost": parse_decimal(row.get("CUSTO DEVOLUCAO")),
                    "return_value": parse_decimal(row.get("VALOR DA DEVOLUCAO")),
                    "net": parse_decimal(row.get("VALOR LIQUIDO")),
                    "margin": parse_decimal(row.get("MARGEM")),
                }
                row_hash = hash_text(json.dumps(payload, ensure_ascii=False, sort_keys=True))
                try:
                    conn.execute(
                        """
                        INSERT INTO fact_vendor_summary (
                            company_id, competence, import_id, row_hash, seller_name, qty_sold, cost_value,
                            sale_value, profit_value, net_profit_value, profit_pct, return_cost,
                            return_value, net_value, margin_value, created_at
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                        """,
                        (
                            company_id,
                            competence,
                            import_id,
                            row_hash,
                            seller_name,
                            payload["qty_sold"],
                            payload["cost"],
                            payload["sale"],
                            payload["profit"],
                            payload["net_profit"],
                            payload["profit_pct"],
                            payload["return_cost"],
                            payload["return_value"],
                            payload["net"],
                            payload["margin"],
                            now_iso(),
                        ),
                    )
                except sqlite3.IntegrityError:
                    duplicate_rows_skipped += 1
                role, _ = current_role_and_unit(conn, company_id, seller_name, competence)
                if role is None:
                    register_issue(conn, company_id, import_id, competence, "vendedor_sem_vinculo", seller_name, {"kind": "seller"})
        elif kind == "devolucao_garantia":
            # A competência sai da DATA de cada devolução, linha a linha — o relatório
            # pode cobrir mais de um mês e cada devolução pertence ao mês em que ocorreu.
            # Linhas idênticas são LEGÍTIMAS (2 unidades da mesma peça na mesma
            # devolução vêm em linhas separadas). O contador de ocorrência distingue
            # essas linhas sem quebrar o dedupe de reimportação do mesmo arquivo.
            occurrence_counter: Counter = Counter()
            for row in rows:
                unit_name = normalize_unit(row.get("Empresa"))
                seller_name = normalize_whitespace(row.get("Vendedor"))
                return_dt = parse_datetime_pt(row.get("Data")) or parse_datetime_flexible(row.get("Data"))
                row_competence = competence_from_date(return_dt) or competence
                total_value = parse_decimal(row.get("Total"))
                if not unit_name and not seller_name and not total_value:
                    continue
                payload = {
                    "unit": unit_name,
                    "seller": seller_name,
                    "client": normalize_whitespace(row.get("Cliente")),
                    "return_number": normalize_whitespace(row.get("Devolucao")),
                    "return_date": return_dt.isoformat() if return_dt else "",
                    "invoice": normalize_whitespace(row.get("Nota")),
                    "item": normalize_whitespace(row.get("Codigo")),
                    "qty": parse_decimal(row.get("Qtd.")),
                    "cost": parse_decimal(row.get("P. Custo.")),
                    "total": total_value,
                }
                base_signature = json.dumps(payload, ensure_ascii=False, sort_keys=True)
                occurrence_counter[base_signature] += 1
                row_hash = hash_text(f"{base_signature}#{occurrence_counter[base_signature]}")
                issue_dt = parse_datetime_pt(row.get("Emissao")) or parse_datetime_flexible(row.get("Emissao"))
                try:
                    conn.execute(
                        """
                        INSERT INTO fact_warranty_returns (
                            company_id, competence, import_id, row_hash, unit_name, seller_name,
                            client_name, city_name, return_number, return_date, reason,
                            invoice_number, issue_date, item_code, item_type, item_description,
                            brand_name, supplier_name, quantity, cost_value, total_value, created_at
                        ) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
                        """,
                        (
                            company_id, row_competence, import_id, row_hash, unit_name, seller_name,
                            normalize_whitespace(row.get("Cliente")),
                            normalize_upper(row.get("Cidade")),
                            normalize_whitespace(row.get("Devolucao")),
                            return_dt.isoformat() if return_dt else None,
                            normalize_upper(row.get("Motivo")),
                            normalize_whitespace(row.get("Nota")),
                            issue_dt.isoformat() if issue_dt else None,
                            normalize_whitespace(row.get("Codigo")),
                            normalize_whitespace(row.get("Tipo")),
                            normalize_whitespace(row.get("Descricao")),
                            normalize_whitespace(row.get("Marca")),
                            normalize_whitespace(row.get("Forn. ref.")),
                            parse_decimal(row.get("Qtd.")),
                            parse_decimal(row.get("P. Custo.")),
                            total_value,
                            now_iso(),
                        ),
                    )
                    warranty_competences_seen.add(row_competence)
                    warranty_total_value += total_value
                except sqlite3.IntegrityError:
                    duplicate_rows_skipped += 1
        elif kind == "custo_unidade":
            for row in rows:
                unit_name = normalize_unit(row.get("EMPRESA"))
                payload = {
                    "unit": unit_name,
                    "qty_sold": parse_decimal(row.get("QTD VENDIDA")),
                    "cost": parse_decimal(row.get("CUSTO")),
                    "sale": parse_decimal(row.get("VENDA")),
                    "profit": parse_decimal(row.get("R$ LUCRO")),
                    "net_profit": parse_decimal(row.get("R$ LUCRO LIQUIDO")),
                    "profit_pct": parse_decimal(row.get("% LUCRO")),
                    "return_cost": parse_decimal(row.get("CUSTO DEVOLUCAO")),
                    "return_value": parse_decimal(row.get("VALOR DA DEVOLUCAO")),
                    "net": parse_decimal(row.get("VALOR LIQUIDO")),
                    "margin": parse_decimal(row.get("MARGEM")),
                }
                row_hash = hash_text(json.dumps(payload, ensure_ascii=False, sort_keys=True))
                try:
                    conn.execute(
                        """
                        INSERT INTO fact_unit_summary (
                            company_id, competence, import_id, row_hash, unit_name, qty_sold, cost_value,
                            sale_value, profit_value, net_profit_value, profit_pct, return_cost,
                            return_value, net_value, margin_value, created_at
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                        """,
                        (
                            company_id,
                            competence,
                            import_id,
                            row_hash,
                            unit_name,
                            payload["qty_sold"],
                            payload["cost"],
                            payload["sale"],
                            payload["profit"],
                            payload["net_profit"],
                            payload["profit_pct"],
                            payload["return_cost"],
                            payload["return_value"],
                            payload["net"],
                            payload["margin"],
                            now_iso(),
                        ),
                    )
                except sqlite3.IntegrityError:
                    duplicate_rows_skipped += 1

    conn.execute("UPDATE imports SET duplicate_rows_skipped = ? WHERE id = ?", (duplicate_rows_skipped, import_id))
    audit_log(
        conn,
        company_id,
        user_id,
        "importar",
        "import",
        str(import_id),
        {"competence": competence, "action": actual_action, "scope": import_scope},
    )
    ensure_client_registry_for_sales(conn, company_id)
    conn.commit()
    # Dados mudaram: derruba caches derivados (dashboard e CRM)
    invalidate_crm_cache(company_id)
    result: dict[str, Any] = {
        "importId": import_id,
        "duplicateRowsSkipped": duplicate_rows_skipped,
        "importAction": actual_action,
        "importScope": import_scope,
        "importedFileTypes": sorted(selected_file_types),
    }
    if sales_competences_seen:
        _ordered = sorted(sales_competences_seen)
        result["salesCompetences"] = _ordered
        result["salesRowsByCompetence"] = dict(sorted(sales_rows_by_competence.items()))
        result["salesRowsWithoutDate"] = sales_rows_without_date
        # Mostra as competências com mais linhas; resume o restante
        _top = sales_rows_by_competence.most_common(8)
        _detail = ", ".join(f"{c}:{n}" for c, n in sorted(_top))
        _rest = len(_ordered) - len(_top)
        _msg = f"Faturamento detalhado — {len(_ordered)} competência(s) ({_ordered[0]}…{_ordered[-1]}): {_detail}"
        if _rest > 0:
            _msg += f" +{_rest} outra(s)"
        _msg += f" | {duplicate_rows_skipped} linha(s) já existentes ignoradas"
        if sales_rows_without_date:
            _msg += f" | {sales_rows_without_date} sem data usaram {competence}"
        result["message"] = _msg

    if warranty_competences_seen:
        _wc = sorted(warranty_competences_seen)
        result["warrantyCompetences"] = _wc
        result["warrantyTotalValue"] = round(warranty_total_value, 2)
        result["message"] = (
            f"Devolução em garantia — {', '.join(_wc)}: {brl(warranty_total_value)} "
            f"| {duplicate_rows_skipped} linha(s) já existentes ignoradas"
        )

    # Cadastro de clientes: reporta o tamanho da base e alerta se encolheu muito
    # (indício de exportação parcial do Alfa — a base vem em vários arquivos).
    if "cadastro_clientes" in selected_file_types:
        clients_after = int(conn.execute(
            "SELECT COUNT(*) FROM crm_client_profiles WHERE company_id = ?", (company_id,)
        ).fetchone()[0] or 0)
        _files_count = len([
            e for e in normalize_upload_entries(files_payload)
            if detect_upload_file_type(e["fileName"], e.get("fieldName")) == "cadastro_clientes"
        ])
        result["clientsBefore"] = clients_before
        result["clientsAfter"] = clients_after
        result["clientsFileCount"] = _files_count
        _msg = f"Cadastro de clientes: {clients_after} clientes de {_files_count} arquivo(s)"
        if clients_before:
            _delta = clients_after - clients_before
            _msg += f" (antes: {clients_before}, variação: {_delta:+d})"
            if clients_after < clients_before * 0.7:
                result["warning"] = (
                    f"ATENÇÃO: a base caiu de {clients_before} para {clients_after} clientes. "
                    "Verifique se todas as exportações do Alfa estavam na pasta."
                )
                _msg += " ⚠ possível exportação incompleta"
        result["message"] = _msg
    return result


def query_competences(conn: sqlite3.Connection, company_id: int) -> list[str]:
    rows = conn.execute(
        """
        SELECT competence FROM (
            SELECT competence FROM fact_sales_detail WHERE company_id = ?
            UNION
            SELECT competence FROM fact_vendor_summary WHERE company_id = ?
            UNION
            SELECT competence FROM fact_unit_summary WHERE company_id = ?
        )
        ORDER BY competence DESC
        """,
        (company_id, company_id, company_id),
    ).fetchall()
    return [row["competence"] for row in rows]


def build_filters_from_query(query: dict[str, list[str]]) -> dict[str, str | None]:
    return {
        "competence_start": query.get("competenceStart", [None])[0],
        "competence_end": query.get("competenceEnd", [None])[0],
        "unit_name": normalize_unit(query.get("unit", [None])[0]),
        "seller_name": normalize_whitespace(query.get("seller", [None])[0]),
        "city_name": normalize_upper(query.get("city", [None])[0]),
        "status": normalize_upper(query.get("status", [None])[0]),
        "purchaseMonth": normalize_upper(query.get("purchaseMonth", [None])[0]),
        "growth": normalize_upper(query.get("growth", [None])[0]),
        "classCode": normalize_upper(query.get("classCode", [None])[0]),
        "personType": normalize_upper(query.get("personType", [None])[0]),
        "search": normalize_whitespace(query.get("search", [None])[0]),
    }


def competence_range_clause(filters: dict[str, str | None]) -> tuple[str, list[Any]]:
    params: list[Any] = []
    clauses: list[str] = []
    if filters["competence_start"]:
        clauses.append("competence >= ?")
        params.append(filters["competence_start"])
    if filters["competence_end"]:
        clauses.append("competence <= ?")
        params.append(filters["competence_end"])
    return " AND ".join(clauses), params


def selected_primary_competence(filters: dict[str, str | None], competences: list[str]) -> str | None:
    if filters["competence_end"]:
        return filters["competence_end"]
    if filters["competence_start"]:
        return filters["competence_start"]
    return competences[0] if competences else None


def dashboard_competence_state(competence: str, today_value: date | None = None) -> dict[str, Any]:
    today_local = today_value or today_in_brazil()
    current_competence = today_local.strftime("%Y-%m")
    return {
        "today": today_local,
        "cutoffDate": dashboard_cutoff_date(today_local),
        "isCurrentCompetence": competence == current_competence,
        "isPastCompetence": competence < current_competence,
        "isFutureCompetence": competence > current_competence,
    }


# Cache de feriados e férias por (empresa, competência). Estes dados quase nunca mudam
# e get_business_calendar é chamado uma vez POR VENDEDOR dentro do dashboard — sem cache
# eram 2 queries × dezenas de vendedores a cada troca de competência.
_calendar_cache: dict[tuple, tuple[dict[str, str], dict[str, list[dict[str, Any]]]]] = {}
_calendar_cache_lock = threading.Lock()


def invalidate_calendar_cache(company_id: int | None = None) -> None:
    with _calendar_cache_lock:
        if company_id is None:
            _calendar_cache.clear()
        else:
            for k in list(_calendar_cache.keys()):
                if k[0] == company_id:
                    del _calendar_cache[k]


def _calendar_reference_data(
    conn: sqlite3.Connection, company_id: int, competence: str, start: date, end: date
) -> tuple[dict[str, str], dict[str, list[dict[str, Any]]]]:
    """Feriados da competência e férias agrupadas por pessoa, com cache."""
    key = (company_id, competence)
    with _calendar_cache_lock:
        hit = _calendar_cache.get(key)
    if hit is not None:
        return hit
    holidays = {
        row["holiday_date"]: row["holiday_name"]
        for row in conn.execute(
            "SELECT holiday_date, holiday_name FROM holidays WHERE company_id = ? AND holiday_date BETWEEN ? AND ?",
            (company_id, start.isoformat(), end.isoformat()),
        ).fetchall()
    }
    vacations_by_person: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in conn.execute(
        """
        SELECT person_name, start_date, end_date, notes
        FROM vacations
        WHERE company_id = ? AND date(end_date) >= date(?) AND date(start_date) <= date(?)
        """,
        (company_id, start.isoformat(), end.isoformat()),
    ).fetchall():
        vacations_by_person[normalize_whitespace(row["person_name"])].append(dict(row))
    result = (holidays, dict(vacations_by_person))
    with _calendar_cache_lock:
        _calendar_cache[key] = result
    return result


def get_business_calendar(
    conn: sqlite3.Connection,
    company_id: int,
    competence: str,
    seller_name: str | None = None,
    reference_today: date | None = None,
    include_current_day: bool = True,
) -> dict[str, Any]:
    start = first_day_of_competence(competence)
    end = last_day_of_competence(competence)
    holidays, vacations_by_person = _calendar_reference_data(conn, company_id, competence, start, end)
    vacation_dates = set()
    vacations = []
    if seller_name:
        for row in vacations_by_person.get(normalize_whitespace(seller_name), []):
            vacations.append(dict(row))
            try:
                _vs = date.fromisoformat(row["start_date"])
                _ve = date.fromisoformat(row["end_date"])
            except (TypeError, ValueError):
                continue
            for day in daterange(max(start, _vs), min(end, _ve)):
                vacation_dates.add(day.isoformat())

    actual_today = reference_today or today_in_brazil()
    effective_today = actual_today if include_current_day else actual_today - timedelta(days=1)
    is_past_competence = effective_today > end
    is_future_competence = effective_today < start
    total_working = 0
    elapsed_working = 0
    seller_working = 0
    elapsed_seller_working = 0
    for day in daterange(start, end):
        if day.weekday() >= 5 or day.isoformat() in holidays:
            continue
        total_working += 1
        if is_past_competence or (not is_future_competence and day <= effective_today):
            elapsed_working += 1
        if day.isoformat() in vacation_dates:
            continue
        seller_working += 1
        if is_past_competence or (not is_future_competence and day <= effective_today):
            elapsed_seller_working += 1
    return {
        "competence": competence,
        "holidays": [{"date": key, "name": value} for key, value in sorted(holidays.items())],
        "vacations": vacations,
        "totalWorkingDays": total_working,
        "elapsedWorkingDays": min(elapsed_working, total_working),
        "remainingWorkingDays": max(total_working - min(elapsed_working, total_working), 0),
        "sellerWorkingDays": seller_working if seller_name else total_working,
        "sellerElapsedWorkingDays": min(elapsed_seller_working, seller_working) if seller_name else min(elapsed_working, total_working),
        "referenceToday": actual_today.isoformat(),
        "effectiveToday": effective_today.isoformat(),
    }


def safe_div(numerator: float, denominator: float) -> float:
    if not denominator:
        return 0.0
    result = numerator / denominator
    return result if math.isfinite(result) else 0.0


def brl(value: float | int | None) -> str:
    """Formata em real brasileiro para textos exibidos ao vendedor."""
    try:
        number = float(value or 0)
    except (TypeError, ValueError):
        number = 0.0
    inteiro = f"{number:,.2f}"
    return "R$ " + inteiro.replace(",", "@").replace(".", ",").replace("@", ".")


def finite_or_none(value: Any) -> float | None:
    """Converte para float finito; devolve None para inf/NaN/valor inválido."""
    if value is None:
        return None
    try:
        number = float(value)
    except (TypeError, ValueError):
        return None
    return number if math.isfinite(number) else None


def official_cost_net(sale_value: float | int | None, return_value: float | int | None) -> float:
    return float(sale_value or 0) - float(return_value or 0)


def weighted_margin_average(rows: Iterable[dict[str, Any]]) -> float | None:
    weighted_total = 0.0
    base_total = 0.0
    for row in rows:
        revenue_net = float(row.get("net_value") or official_cost_net(row.get("sale_value"), row.get("return_value")) or 0.0)
        margin_value = row.get("margin_value")
        if margin_value is None:
            continue
        weighted_total += float(margin_value or 0.0) * revenue_net
        base_total += revenue_net
    if base_total <= 0:
        return None
    return weighted_total / base_total


def aggregate_official_summary_rows(rows: Iterable[dict[str, Any]]) -> dict[str, float | None]:
    rows_list = list(rows)
    revenue_net = float(sum(float(row.get("net_value") or 0.0) for row in rows_list))
    revenue_gross = float(sum(float(row.get("sale_value") or 0.0) for row in rows_list))
    returns_value = float(sum(float(row.get("return_value") or 0.0) for row in rows_list))
    return_cost = float(sum(float(row.get("return_cost") or 0.0) for row in rows_list))
    qty_sold = float(sum(float(row.get("qty_sold") or 0.0) for row in rows_list))
    cost_value = float(sum(float(row.get("cost_value") or 0.0) for row in rows_list))
    profit_value = float(sum(float(row.get("profit_value") or 0.0) for row in rows_list))
    net_profit_value = float(sum(float(row.get("net_profit_value") or 0.0) for row in rows_list))
    margin_average = weighted_margin_average(rows_list)
    return {
        "revenueNet": revenue_net,
        "revenueGross": revenue_gross,
        "returnsValue": returns_value,
        "returnCost": return_cost,
        "qtySold": qty_sold,
        "costValue": cost_value,
        "profitValue": profit_value,
        "netProfitValue": net_profit_value,
        "marginAverage": margin_average,
        "ticketPerPiece": safe_div(revenue_net, qty_sold),
        "returnRatioPct": safe_div(returns_value, revenue_net) * 100 if revenue_net else 0.0,
    }


def seller_identity_for_user(user: sqlite3.Row) -> str:
    return normalize_whitespace(user["linked_person_name"] or user["full_name"] or user["username"])


def normalize_unit_list(values: Any) -> list[str]:
    if values is None:
        return []
    if isinstance(values, str):
        text = values.strip()
        if not text:
            return []
        try:
            parsed = json.loads(text)
        except json.JSONDecodeError:
            parsed = re.split(r"[;,|]", text)
        values = parsed
    if not isinstance(values, (list, tuple, set)):
        values = [values]
    normalized: list[str] = []
    seen: set[str] = set()
    for value in values:
        unit = normalize_unit(str(value))
        if not unit or unit in seen:
            continue
        normalized.append(unit)
        seen.add(unit)
    return normalized


def linked_units_for_user(user: sqlite3.Row | dict[str, Any]) -> list[str]:
    raw_value = user["linked_units_json"] if isinstance(user, sqlite3.Row) else user.get("linked_units_json")
    return normalize_unit_list(raw_value)


def active_mapped_cities_for_units(conn: sqlite3.Connection, company_id: int, unit_names: list[str]) -> list[str]:
    normalized_units = normalize_unit_list(unit_names)
    if not normalized_units:
        return []
    placeholders = ", ".join("?" for _ in normalized_units)
    rows = conn.execute(
        f"""
        SELECT DISTINCT city_name
        FROM city_mappings
        WHERE company_id = ?
          AND principal_unit IN ({placeholders})
          AND city_name IS NOT NULL
          AND city_name <> ''
          AND (valid_to IS NULL OR valid_to = '')
        ORDER BY city_name
        """,
        [company_id, *normalized_units],
    ).fetchall()
    return [row["city_name"] for row in rows if row["city_name"]]


def data_scope_for_user(conn: sqlite3.Connection, user: sqlite3.Row) -> str:
    """Escopo de dados vindo do perfil, com fallback pelo nome do papel (legado)."""
    profile = get_access_profile_for_user(conn, user)
    if profile:
        return profile["dataScope"]
    if user["role"] == "Vendedor":
        return "proprio"
    if user["role"] in {"Gerente", "Analista"}:
        return "unidade"
    return "todos"


def scoped_filters_for_user(conn: sqlite3.Connection, company_id: int, user: sqlite3.Row, filters: dict[str, str | None]) -> dict[str, str | None]:
    scoped = dict(filters)
    data_scope = data_scope_for_user(conn, user)

    if data_scope == "todos":
        return scoped

    if data_scope == "proprio":
        seller_name = seller_identity_for_user(user)
        _, base_unit = current_role_and_unit(conn, company_id, seller_name, selected_primary_competence(scoped, query_competences(conn, company_id)) or date.today().strftime("%Y-%m"))
        scoped["seller_name"] = seller_name
        # Sempre sobrescreve a unidade pedida: o vendedor só enxerga a própria base.
        # Sem unidade cadastrada, zera o filtro (o recorte por vendedor já delimita).
        scoped["unit_name"] = normalize_unit(base_unit) if base_unit else None
        return scoped

    # unidade / unidade_consolidado
    linked_units = linked_units_for_user(user)
    if not linked_units:
        scoped["unit_name"] = "__NO_ACCESS__"
        scoped["city_name"] = None
        scoped["seller_name"] = None
        return scoped

    requested_unit = normalize_unit(scoped.get("unit_name"))
    requested_city = normalize_upper(scoped.get("city_name"))
    requested_seller = normalize_whitespace(scoped.get("seller_name"))
    competence = selected_primary_competence(scoped, query_competences(conn, company_id)) or date.today().strftime("%Y-%m")

    # "unidade + consolidado": pode escolher "Todas" para ver o total da empresa,
    # mas ao filtrar por uma unidade específica só valem as vinculadas a ele.
    if data_scope == "unidade_consolidado":
        scoped["allowed_units"] = []
        if requested_unit:
            scoped["unit_name"] = requested_unit if requested_unit in linked_units else linked_units[0]
    else:
        scoped["allowed_units"] = linked_units
        scoped["unit_name"] = (
            requested_unit if requested_unit in linked_units else (requested_unit and linked_units[0]) or None
        )

    # Cidade e vendedor pedidos precisam pertencer ao escopo permitido
    scope_units = [scoped["unit_name"]] if scoped.get("unit_name") else linked_units
    if requested_city:
        valid_cities = set(active_mapped_cities_for_units(conn, company_id, scope_units))
        if requested_city not in valid_cities:
            scoped["city_name"] = None
    if requested_seller:
        _, seller_base_unit = current_role_and_unit(conn, company_id, requested_seller, competence)
        if normalize_unit(seller_base_unit) not in linked_units:
            scoped["seller_name"] = None
    return scoped


def crm_allowed_units_for_user(conn: sqlite3.Connection, user: sqlite3.Row) -> list[str] | None:
    """Unidades que o usuário pode ver NO CRM.

    Diferente do dashboard de resultados, a carteira nunca é consolidada: mesmo o
    perfil "unidade + consolidado" enxerga só as unidades vinculadas. O consolidado
    serve para comparar números, não para acessar a carteira de outras equipes.
    Retorna None quando não há restrição.
    """
    scope = data_scope_for_user(conn, user)
    if scope in {"unidade", "unidade_consolidado"}:
        return linked_units_for_user(user)
    return None


def crm_unit_filter_for_user(
    conn: sqlite3.Connection, user: sqlite3.Row, requested_unit: str | None
) -> list[str] | None:
    """Resolve o filtro de unidade do CRM respeitando o vínculo do usuário."""
    allowed = crm_allowed_units_for_user(conn, user)
    requested = normalize_unit(requested_unit) if requested_unit else None
    if allowed is None:
        return [requested] if requested else None
    if not allowed:
        return ["__NO_ACCESS__"]
    if requested and requested in allowed:
        return [requested]
    return allowed


def crm_scoped_filters_for_user(
    conn: sqlite3.Connection, company_id: int, user: sqlite3.Row, filters: dict[str, str | None]
) -> dict[str, str | None]:
    """Filtros do CRM. Igual ao dashboard, exceto que NUNCA consolida:
    o perfil "unidade + consolidado" fica restrito às unidades vinculadas aqui."""
    scoped = scoped_filters_for_user(conn, company_id, user, filters)
    allowed = crm_allowed_units_for_user(conn, user)
    if allowed is None:
        return scoped
    if not allowed:
        scoped["unit_name"] = "__NO_ACCESS__"
        scoped["allowed_units"] = []
        return scoped
    scoped["allowed_units"] = allowed
    current_unit = normalize_unit(scoped.get("unit_name"))
    if not current_unit or current_unit not in allowed:
        # Sem unidade escolhida (ou fora do vínculo): usa a primeira unidade do usuário
        scoped["unit_name"] = allowed[0]
    return scoped


def crm_base_client_scope_query(
    conn: sqlite3.Connection, company_id: int, filters: dict[str, str | None]
) -> tuple[str | None, list[Any], str | None]:
    current_competence = crm_summary_latest_competence(conn, company_id)
    if not current_competence:
        return None, [], None
    seller_name = normalize_upper(filters.get("seller_name"))
    unit_name = normalize_unit(filters.get("unit_name"))
    city_name = normalize_upper(filters.get("city_name"))
    where_clauses = ["base.client_code IS NOT NULL", "base.client_code <> ''"]
    base_params: list[Any] = [company_id, current_competence, company_id, company_id, current_competence, company_id]
    filter_params: list[Any] = []
    if seller_name:
        where_clauses.append(
            "UPPER(COALESCE(NULLIF(p.internal_seller_name, ''), NULLIF(p.external_seller_name, ''), s.summary_seller_name)) = ?"
        )
        filter_params.append(seller_name)
    if city_name:
        where_clauses.append("COALESCE(p.city_name, s.summary_city_name) = ?")
        filter_params.append(city_name)
    if unit_name:
        where_clauses.append(
            """
            EXISTS (
                SELECT 1
                FROM city_mappings cm
                WHERE cm.company_id = ?
                  AND cm.principal_unit = ?
                  AND cm.city_name = COALESCE(p.city_name, s.summary_city_name)
                    AND (cm.valid_to IS NULL OR cm.valid_to = '')
            )
            """
        )
        filter_params.extend([company_id, unit_name])
    scope_query = f"""
        WITH current_summary AS (
            SELECT
                client_code,
                MAX(client_name) AS summary_client_name,
                MAX(city_name) AS summary_city_name,
                MAX(seller_name) AS summary_seller_name,
                ROUND(SUM(net_value), 2) AS current_revenue,
                MAX(last_purchase_at) AS last_purchase_at
            FROM crm_client_summary
            WHERE company_id = ? AND competence = ?
            GROUP BY client_code
        ),
        base_clients AS (
            SELECT client_code
            FROM crm_client_profiles
            WHERE company_id = ?
            UNION
            SELECT client_code
            FROM crm_client_summary
            WHERE company_id = ? AND competence = ?
        )
        SELECT
            base.client_code,
            s.summary_client_name,
            COALESCE(NULLIF(p.client_name, ''), NULLIF(s.summary_client_name, ''), base.client_code) AS client_name,
            p.trade_name,
            COALESCE(NULLIF(p.city_name, ''), NULLIF(s.summary_city_name, '')) AS city_name,
            p.phone,
            p.updated_phone,
            p.primary_contact_name,
            p.contact_notes,
            p.document_number,
            p.credit_limit,
            p.economic_group,
            COALESCE(NULLIF(p.internal_seller_name, ''), NULLIF(p.external_seller_name, ''), s.summary_seller_name) AS assigned_seller,
            COALESCE(s.current_revenue, 0) AS current_revenue,
            COALESCE(s.last_purchase_at, p.last_sale_at) AS last_purchase_at
        FROM base_clients base
        LEFT JOIN crm_client_profiles p
          ON p.company_id = ? AND p.client_code = base.client_code
        LEFT JOIN current_summary s
          ON s.client_code = base.client_code
        WHERE {" AND ".join(where_clauses)}
    """
    return scope_query, [*base_params, *filter_params], current_competence


def crm_base_client_rows(
    conn: sqlite3.Connection, company_id: int, filters: dict[str, str | None]
) -> list[dict[str, Any]]:
    scope_query, params, current_competence = crm_base_client_scope_query(conn, company_id, filters)
    if not scope_query or not current_competence:
        return []
    c0 = current_competence
    c1 = shift_competence(c0, -1)
    c2 = shift_competence(c0, -2)
    c3 = shift_competence(c0, -3)
    previous_competences = [c1, c2, c3]

    aggregate_rows = conn.execute(scope_query, params).fetchall()

    # Precarrega mapeamento cidade→unidade em uma única query (evita N+1)
    city_unit_map = build_city_unit_map(conn, company_id, c0)

    # Agrega fact_sales_detail por cliente no SQL — evita iterar milhares de linhas no Python
    detail_rows = conn.execute(
        """
        SELECT
            client_name,
            SUM(CASE WHEN competence = ? THEN net_value ELSE 0 END) AS revenue_c1,
            SUM(CASE WHEN competence = ? THEN net_value ELSE 0 END) AS revenue_c2,
            SUM(CASE WHEN competence = ? THEN net_value ELSE 0 END) AS revenue_c3,
            MAX(issue_date) AS last_purchase_at,
            COUNT(DISTINCT CASE WHEN competence = ? AND net_value > 0 THEN
                COALESCE(NULLIF(manufacturer_sku, ''), NULLIF(sku_key, ''), NULLIF(gtin_value, ''), 'ITEM')
            END) AS current_sku_count
        FROM fact_sales_detail
        WHERE company_id = ? AND competence IN (?, ?, ?, ?)
        GROUP BY client_name
        """,
        [c1, c2, c3, c0, company_id, c0, c1, c2, c3],
    ).fetchall()

    # Receita c0 scoped por vendedor — query separada para não contaminar c1/c2/c3 (sem filtro de vendedor)
    seller_name_for_c0 = normalize_upper(filters.get("seller_name"))
    c0_seller_revenue: dict[str, float] = {}
    if seller_name_for_c0:
        c0_rows = conn.execute(
            """
            SELECT client_name, SUM(net_value) AS revenue_c0
            FROM fact_sales_detail
            WHERE company_id = ? AND competence = ? AND UPPER(seller_name) = ?
            GROUP BY client_name
            """,
            [company_id, c0, seller_name_for_c0],
        ).fetchall()
        for c0row in c0_rows:
            key = normalize_client_key(c0row["client_name"])
            if key:
                c0_seller_revenue[key] = c0_seller_revenue.get(key, 0.0) + float(c0row["revenue_c0"] or 0.0)

    interaction_rows = conn.execute(
        """
        SELECT client_key, MAX(occurred_at) AS last_interaction_at
        FROM crm_interactions
        WHERE company_id = ?
        GROUP BY client_key
        """,
        (company_id,),
    ).fetchall()
    interaction_map = {row["client_key"]: row["last_interaction_at"] for row in interaction_rows}

    # Constrói mapa de métricas por cliente já agregado (uma entrada por nome único)
    detail_metrics: dict[str, dict[str, Any]] = {}
    for row in detail_rows:
        client_name_value = normalize_whitespace(row["client_name"])
        if not client_name_value:
            continue
        name_key = normalize_client_key(client_name_value)
        if not name_key:
            continue
        detail_metrics[name_key] = {
            "revenues_c123": [
                float(row["revenue_c1"] or 0.0),
                float(row["revenue_c2"] or 0.0),
                float(row["revenue_c3"] or 0.0),
            ],
            "currentSkuCount": int(row["current_sku_count"] or 0),
            "lastPurchaseAt": parse_datetime_flexible(row["last_purchase_at"]),
        }

    # ── Cadastros duplicados: mesmo cliente com mais de um código ──────────────
    # O faturamento detalhado é indexado por NOME; a carteira, por CÓDIGO. Quando a
    # mesma empresa tem código antigo e novo (recadastro), os dois códigos casariam
    # com o mesmo faturamento e o valor apareceria em dobro nos totais.
    # Regra: o faturamento fica com um único código — o que tem movimento no mês
    # corrente; sem movimento em nenhum, fica com o de compra mais recente.
    revenue_owner_by_name: dict[str, str] = {}
    _candidates_by_name: dict[str, list[tuple[float, str, str]]] = defaultdict(list)
    for row in aggregate_rows:
        code = normalize_whitespace(row["client_code"])
        if not code:
            continue
        for key in {
            normalize_client_key(row["client_name"]),
            normalize_client_key(row["summary_client_name"]),
            normalize_client_key(row["trade_name"]),
        }:
            if key:
                _candidates_by_name[key].append((
                    float(row["current_revenue"] or 0.0),
                    normalize_whitespace(row["last_purchase_at"]) or "",
                    code,
                ))
    for name_key, candidates in _candidates_by_name.items():
        if len(candidates) < 2:
            revenue_owner_by_name[name_key] = candidates[0][2]
            continue
        # Maior receita no mês corrente; empate resolve pela compra mais recente
        candidates.sort(key=lambda c: (c[0], c[1]), reverse=True)
        revenue_owner_by_name[name_key] = candidates[0][2]

    client_rows: list[dict[str, Any]] = []
    for row in aggregate_rows:
        current_revenue = float(row["current_revenue"] or 0.0)
        client_key = normalize_whitespace(row["client_code"])
        # O cliente pode ser encontrado por razão social, nome do resumo ou nome
        # fantasia. DEDUPLICAR é essencial: quando dois desses campos normalizam
        # para a mesma chave (o caso comum — razão social igual em ambos), o loop
        # abaixo somava o MESMO faturamento duas ou três vezes, dobrando a média.
        candidate_keys = list(dict.fromkeys(
            key for key in (
                normalize_client_key(row["client_name"]),
                normalize_client_key(row["summary_client_name"]),
                normalize_client_key(row["trade_name"]),
            ) if key
        ))
        merged_revenues = [0.0, 0.0, 0.0]
        merged_current_sku_count = 0
        merged_last_purchase_at: datetime | None = None
        merged_detail_c0_revenue = 0.0
        duplicated_codes: list[str] = []
        for name_key in candidate_keys:
            # Só o código eleito dono recebe o faturamento daquele nome
            owner = revenue_owner_by_name.get(name_key)
            if owner and owner != client_key:
                duplicated_codes.append(owner)
                continue
            if name_key in detail_metrics:
                metrics = detail_metrics[name_key]
                for i, v in enumerate(metrics["revenues_c123"]):
                    merged_revenues[i] += v
                merged_current_sku_count = max(merged_current_sku_count, metrics["currentSkuCount"])
                m_last = metrics["lastPurchaseAt"]
                if m_last and (merged_last_purchase_at is None or m_last > merged_last_purchase_at):
                    merged_last_purchase_at = m_last
            if name_key in c0_seller_revenue:
                merged_detail_c0_revenue += c0_seller_revenue[name_key]

        # Usa o maior entre CRM summary e faturamento detalhado scoped por vendedor
        current_revenue = max(current_revenue, merged_detail_c0_revenue)
        previous_revenues = merged_revenues
        # MÉDIA = soma dos 3 meses ANTERIORES a c0, dividida por 3 (sempre por 3,
        # inclusive meses sem compra — mede volume médio mensal, não ticket médio).
        # Base: fact_sales_detail, faturamento total do cliente (todos os vendedores).
        average_revenue = sum(previous_revenues) / 3
        months_with_purchase = sum(1 for v in previous_revenues if v > 0)
        summary_last_purchase = parse_datetime_flexible(row["last_purchase_at"])
        last_purchase_at = summary_last_purchase
        if merged_last_purchase_at and (last_purchase_at is None or merged_last_purchase_at > last_purchase_at):
            last_purchase_at = merged_last_purchase_at
        days_without_purchase = (date.today() - last_purchase_at.date()).days if last_purchase_at else None
        status_code = crm_status_from_days(days_without_purchase)
        class_code = crm_class_from_average(average_revenue)
        drop_pct = safe_div(current_revenue - average_revenue, average_revenue) if average_revenue else 0.0
        has_mix_opportunity = current_revenue > 0 and merged_current_sku_count <= 2
        resolved_unit_name = city_unit_map.get(normalize_upper(row["city_name"]))
        priorities: list[str] = []
        if status_code == "INATIVO":
            priorities.append("REATIVACAO_INATIVO")
        if status_code == "PRE_INATIVO":
            priorities.append("PRE_INATIVO")
        if current_revenue <= 0:
            priorities.append("SEM_COMPRA_MES")
        if average_revenue > 0 and drop_pct <= -0.1:
            priorities.append("QUEDA_FATURAMENTO")
        if class_code in {"DIAMANTE", "OURO"}:
            priorities.append("CLIENTE_CLASSE_ALTA")
        if has_mix_opportunity:
            priorities.append("OPORTUNIDADE_MIX")
        primary_reason_code = priorities[0] if priorities else "PROSPECCAO_NOVA"
        secondary_reasons = priorities[1:]
        # Determina tipo de pessoa pelo documento; fallback por heurística de nome
        doc_person_type, _ = person_type_from_document(row["document_number"])
        if doc_person_type:
            person_type = doc_person_type
        else:
            person_type, _, _ = infer_person_type_from_name(row["client_name"])
        row_summary = {"daysWithoutPurchase": days_without_purchase, "dropPct": drop_pct, "classCode": class_code}
        client_rows.append(
            {
                "clientKey": client_key,
                "clientCode": client_key,
                "clientName": row["client_name"],
                "summaryClientName": row["summary_client_name"],
                "tradeName": row["trade_name"],
                "cityName": row["city_name"],
                "phone": row["updated_phone"] or row["phone"],
                "phoneRaw": row["phone"],
                "updatedPhone": row["updated_phone"],
                "primaryContactName": row["primary_contact_name"],
                "contactNotes": row["contact_notes"],
                "documentNumber": row["document_number"],
                "personType": person_type,
                "creditLimit": float(row["credit_limit"] or 0.0),
                "economicGroup": row["economic_group"],
                "assignedSeller": row["assigned_seller"],
                "unitName": resolved_unit_name,
                "currentRevenue": round(current_revenue, 2),
                "averageRevenue": round(average_revenue, 2),
                "growthPct": round(drop_pct, 4),
                "trimesterRevenue1": round(previous_revenues[0], 2),
                "trimesterRevenue2": round(previous_revenues[1], 2),
                "trimesterRevenue3": round(previous_revenues[2], 2),
                # Sinaliza cadastro duplicado: o faturamento deste nome está em outro código
                "duplicateOfCode": duplicated_codes[0] if duplicated_codes else None,
                # Memória de cálculo da média — permite auditar o número na tela
                "averageBasis": {
                    "currentCompetence": c0,
                    "months": [
                        {"competence": c1, "revenue": round(previous_revenues[0], 2)},
                        {"competence": c2, "revenue": round(previous_revenues[1], 2)},
                        {"competence": c3, "revenue": round(previous_revenues[2], 2)},
                    ],
                    "total": round(sum(previous_revenues), 2),
                    "divisor": 3,
                    "monthsWithPurchase": months_with_purchase,
                    "formula": "soma dos 3 meses anteriores ÷ 3",
                },
                "dropPct": round(drop_pct, 4),
                "classCode": class_code,
                "statusCode": status_code,
                "daysWithoutPurchase": days_without_purchase,
                "lastPurchaseAt": last_purchase_at.isoformat(timespec="seconds") if last_purchase_at else None,
                "lastInteractionAt": interaction_map.get(client_key),
                "currentSkuCount": merged_current_sku_count,
                "primaryReasonCode": primary_reason_code,
                "primaryReason": crm_reason_message(row_summary, primary_reason_code),
                "secondaryReasonCodes": secondary_reasons,
            }
        )
    return client_rows


# --- Cache TTL para crm_base_client_rows (90s) ---
_crm_base_cache: dict[tuple, tuple[float, list]] = {}
_crm_base_cache_lock = threading.Lock()
_CRM_CACHE_TTL = 90  # segundos


def _crm_cache_key(company_id: int, filters: dict) -> tuple:
    return (
        company_id,
        normalize_whitespace(filters.get("seller_name")) or "",
        normalize_whitespace(filters.get("unit_name")) or "",
        normalize_whitespace(filters.get("competenceEnd") or filters.get("competence")) or "",
    )


def crm_base_client_rows_cached(conn: sqlite3.Connection, company_id: int, filters: dict) -> list:
    key = _crm_cache_key(company_id, filters)
    now = time.monotonic()
    with _crm_base_cache_lock:
        entry = _crm_base_cache.get(key)
    if entry and now - entry[0] < _CRM_CACHE_TTL:
        return entry[1]
    result = crm_base_client_rows(conn, company_id, filters)
    with _crm_base_cache_lock:
        _crm_base_cache[key] = (now, result)
    return result


def invalidate_crm_cache(company_id: int | None = None) -> None:
    with _crm_base_cache_lock:
        if company_id is None:
            _crm_base_cache.clear()
        else:
            for k in list(_crm_base_cache.keys()):
                if k[0] == company_id:
                    del _crm_base_cache[k]
    invalidate_dashboard_cache(company_id)
    invalidate_calendar_cache(company_id)


# ─────────────────────────────────────────────────────────────────────────────
# Cache do dashboard
#
# Entre importações os dados são estáticos, então o resultado de get_dashboard_data
# pode ser reaproveitado integralmente. Sem isso, cada troca de competência
# reprocessava dezenas de milhares de linhas do faturamento detalhado em Python.
# O cache é invalidado em toda importação e pré-aquecido em segundo plano.
# ─────────────────────────────────────────────────────────────────────────────
_dashboard_cache: dict[tuple, dict[str, Any]] = {}
_dashboard_cache_lock = threading.Lock()
_DASHBOARD_CACHE_MAX = 400


def _dashboard_cache_key(company_id: int, filters: dict[str, str | None]) -> tuple:
    # A competência efetiva vem de competence_end/competence_start (ver
    # selected_primary_competence); competence_start vazio significa "mais recente".
    return (
        company_id,
        normalize_whitespace(filters.get("competence_start")),
        normalize_whitespace(filters.get("competence_end")),
        normalize_whitespace(filters.get("unit_name")),
        normalize_whitespace(filters.get("seller_name")),
        normalize_whitespace(filters.get("city_name")),
        tuple(sorted(normalize_unit_list(filters.get("allowed_units")))),
    )


def invalidate_dashboard_cache(company_id: int | None = None) -> None:
    with _dashboard_cache_lock:
        if company_id is None:
            _dashboard_cache.clear()
        else:
            for k in list(_dashboard_cache.keys()):
                if k[0] == company_id:
                    del _dashboard_cache[k]


def get_dashboard_data_cached(
    conn: sqlite3.Connection, company_id: int, filters: dict[str, str | None]
) -> dict[str, Any]:
    key = _dashboard_cache_key(company_id, filters)
    with _dashboard_cache_lock:
        hit = _dashboard_cache.get(key)
    if hit is not None:
        print(f"[dashboard] CACHE HIT {key[1:5]}", flush=True)
        return hit
    started = time.time()
    data = get_dashboard_data(conn, company_id, filters)
    elapsed = time.time() - started
    with _dashboard_cache_lock:
        if len(_dashboard_cache) >= _DASHBOARD_CACHE_MAX:
            _dashboard_cache.clear()
        _dashboard_cache[key] = data
    print(f"[dashboard] CALCULADO {key[1:5]} em {elapsed:.1f}s", flush=True)
    return data


def warm_dashboard_cache(company_id: int | None = None) -> None:
    """Pré-calcula o dashboard de cada competência para que a troca seja instantânea."""
    try:
        with closing(get_connection()) as conn:
            if company_id is None:
                company_ids = [r["id"] for r in conn.execute("SELECT id FROM companies").fetchall()]
            else:
                company_ids = [company_id]
            started = time.time()
            for cid in company_ids:
                competences = query_competences(conn, cid)
                units = [
                    normalize_unit(r["unit_name"])
                    for r in conn.execute(
                        "SELECT DISTINCT unit_name FROM fact_unit_summary WHERE company_id = ?", (cid,)
                    ).fetchall()
                    if r["unit_name"]
                ]
                # Visão padrão (sem competência escolhida = mais recente)
                try:
                    get_dashboard_data_cached(conn, cid, build_filters_from_query({}))
                except Exception:
                    traceback.print_exc()

                # A tela envia competenceStart e competenceEnd com o mesmo valor.
                # Competências recentes sem filtro de unidade.
                for competence in competences[:8]:
                    filters = build_filters_from_query({})
                    filters["competence_start"] = competence
                    filters["competence_end"] = competence
                    try:
                        get_dashboard_data_cached(conn, cid, filters)
                    except Exception:
                        traceback.print_exc()

                # Combinação competência × unidade para as 3 competências mais recentes,
                # que é o recorte usado no dia a dia.
                for competence in competences[:3]:
                    for unit in units:
                        filters = build_filters_from_query({})
                        filters["competence_start"] = competence
                        filters["competence_end"] = competence
                        filters["unit_name"] = unit
                        try:
                            get_dashboard_data_cached(conn, cid, filters)
                        except Exception:
                            traceback.print_exc()
            print(f"[dashboard] cache pré-aquecido: {len(_dashboard_cache)} combinação(ões) "
                  f"em {time.time() - started:.0f}s")
    except Exception:
        traceback.print_exc()


def crm_base_client_count(conn: sqlite3.Connection, company_id: int, filters: dict[str, str | None]) -> int:
    scope_query, params, _ = crm_base_client_scope_query(conn, company_id, filters)
    if not scope_query:
        return 0
    row = conn.execute(
        f"""
        SELECT COUNT(*) AS total
        FROM (
            {scope_query}
        ) scoped_clients
        """,
        params,
    ).fetchone()
    return int(row["total"] or 0)


def crm_reason_message(summary: dict[str, Any], reason_code: str) -> str:
    if reason_code == "REATIVACAO_INATIVO":
        days = summary.get("daysWithoutPurchase")
        return f"Inativo ha {days} dias" if days is not None else "Inativo sem data recente de compra"
    if reason_code == "PRE_INATIVO":
        days = summary.get("daysWithoutPurchase")
        return f"Pre-inativo ha {days} dias sem compra" if days is not None else "Pre-inativo sem data recente de compra"
    if reason_code == "SEM_COMPRA_MES":
        return "Sem compra no mes atual"
    if reason_code == "QUEDA_FATURAMENTO":
        return f"Queda de {abs(summary['dropPct']) * 100:.0f}% vs media do trimestre"
    if reason_code == "CLIENTE_CLASSE_ALTA":
        return f"Cliente {summary['classCode']}"
    if reason_code == "OPORTUNIDADE_MIX":
        return "Baixa variedade recente de itens para o perfil"
    return "Prospeccao nova"


def crm_generate_questions(summary: dict[str, Any]) -> dict[str, Any]:
    if summary["statusCode"] == "INATIVO":
        return {
            "primary": "O que mudou na sua rotina de compra desde o ultimo pedido?",
            "secondary": [
                "Qual linha esta com mais giro hoje na oficina/loja?",
                "Tem alguma ruptura ou fornecedor que deixou de atender bem?",
                "Qual dia da semana faz mais sentido eu te acompanhar?",
            ],
        }
    if summary["statusCode"] == "PRE_INATIVO":
        return {
            "primary": "Qual item voce esta precisando girar nesta semana para eu te ajudar antes da proxima compra?",
            "secondary": [
                "O mix atual esta cobrindo bem freio, suspensao e direcao?",
                "Tem alguma marca ou linha com falta recente?",
                "Qual proximo pedido voce imagina fazer?",
            ],
        }
    if summary["primaryReasonCode"] == "QUEDA_FATURAMENTO":
        return {
            "primary": "O volume deste mes caiu frente ao seu ritmo normal; onde voce sentiu mais essa queda?",
            "secondary": [
                "Qual linha perdeu mais giro recentemente?",
                "Teve mudanca de demanda, estoque ou fornecedor?",
                "Que oferta faria sentido para retomar compra agora?",
            ],
        }
    return {
        "primary": "Qual linha esta girando mais no momento para eu te apoiar com oferta certa?",
        "secondary": [
            "Tem algum item que voce costumava comprar e precisa voltar a girar?",
            "Existe alguma necessidade de reposicao imediata?",
            "Qual dia voce costuma comprar para eu te acompanhar melhor?",
        ],
    }


def crm_get_offer_suggestions(
    conn: sqlite3.Connection, company_id: int, client_name: str, city_name: str | None = None
) -> dict[str, Any]:
    """Sugestões de oferta com contexto para o vendedor conseguir abordar.

    Dois tipos, sempre rotulados:
      - RECOMPRA: item que o cliente comprava e parou. Traz meses de compra,
        valor médio e há quanto tempo não pede — dá o gancho da conversa.
      - OPORTUNIDADE: item que oficinas da mesma praça compram bastante e este
        cliente nunca comprou. Abre mix novo.
    """
    latest = crm_latest_competence(conn, company_id)
    if not latest:
        return {"primary": None, "secondary": [], "repurchase": [], "opportunity": []}

    ITEM_EXPR = "COALESCE(NULLIF(manufacturer_sku, ''), NULLIF(sku_key, ''), NULLIF(gtin_value, ''), 'ITEM')"

    # Histórico do cliente por item (fora do mês corrente)
    history = conn.execute(
        f"""
        SELECT {ITEM_EXPR} AS item_code,
               COUNT(DISTINCT competence) AS meses,
               SUM(net_value) AS total,
               SUM(quantity) AS qtd,
               MAX(competence) AS ultima_competencia
        FROM fact_sales_detail
        WHERE company_id = ? AND client_name = ? AND competence <> ? AND net_value > 0
        GROUP BY item_code
        ORDER BY meses DESC, total DESC
        LIMIT 25
        """,
        (company_id, client_name, latest),
    ).fetchall()

    current_items = {
        r["item_code"]
        for r in conn.execute(
            f"SELECT DISTINCT {ITEM_EXPR} AS item_code FROM fact_sales_detail "
            "WHERE company_id = ? AND client_name = ? AND competence = ?",
            (company_id, client_name, latest),
        ).fetchall()
    }
    all_client_items = {r["item_code"] for r in history} | current_items

    def months_since(competence: str | None) -> int | None:
        if not competence or len(competence) < 7:
            return None
        try:
            y1, m1 = int(latest[:4]), int(latest[5:7])
            y2, m2 = int(competence[:4]), int(competence[5:7])
            return (y1 - y2) * 12 + (m1 - m2)
        except ValueError:
            return None

    repurchase: list[dict[str, Any]] = []
    for r in history:
        if r["item_code"] in current_items:
            continue
        meses = int(r["meses"] or 0)
        gap = months_since(r["ultima_competencia"])
        media = float(r["total"] or 0) / max(meses, 1)
        if meses >= 2:
            freq = f"comprava em {meses} meses"
        else:
            freq = "comprou uma vez"
        gap_txt = "sem pedido no mês atual" if not gap else f"sem pedido há {gap} {'mês' if gap == 1 else 'meses'}"
        repurchase.append({
            "itemCode": r["item_code"],
            "type": "RECOMPRA",
            "typeLabel": "Recompra",
            "title": r["item_code"],
            "reason": f"{freq} · {gap_txt} · média {brl(media)}/mês",
            "months": meses,
            "avgValue": round(media, 2),
            "monthsSincePurchase": gap,
        })

    # Oportunidade: itens girando na praça que este cliente nunca comprou
    opportunity: list[dict[str, Any]] = []
    if city_name:
        peer_rows = conn.execute(
            f"""
            SELECT {ITEM_EXPR} AS item_code,
                   COUNT(DISTINCT client_name) AS clientes,
                   SUM(net_value) AS total
            FROM fact_sales_detail
            WHERE company_id = ? AND city_name = ? AND client_name <> ? AND net_value > 0
              AND competence >= ?
            GROUP BY item_code
            HAVING clientes >= 3
            ORDER BY clientes DESC, total DESC
            LIMIT 40
            """,
            (company_id, normalize_upper(city_name), client_name, shift_competence(latest, -3)),
        ).fetchall()
        for r in peer_rows:
            if r["item_code"] in all_client_items:
                continue
            opportunity.append({
                "itemCode": r["item_code"],
                "type": "OPORTUNIDADE",
                "typeLabel": "Oportunidade",
                "title": r["item_code"],
                "reason": f"{int(r['clientes'])} oficinas da região compram e ele nunca pediu",
                "peerClients": int(r["clientes"]),
            })
            if len(opportunity) >= 5:
                break

    # Prioriza recompra: gancho mais forte e conversão mais provável
    primary = repurchase[0] if repurchase else (opportunity[0] if opportunity else None)
    secondary = ([o for o in repurchase[1:3]] + [o for o in opportunity[:2]])[:4]
    return {
        "primary": primary,
        "secondary": secondary,
        "repurchase": repurchase[:5],
        "opportunity": opportunity[:5],
    }


def crm_situation_for_client(summary: dict[str, Any]) -> str:
    """Traduz o estado do cliente na situação usada pela biblioteca de conteúdo."""
    status = summary.get("statusCode")
    if status == "INATIVO":
        return "INATIVO"
    if status == "PRE_INATIVO":
        return "PRE_INATIVO"
    if float(summary.get("currentRevenue") or 0) <= 0:
        return "SEM_COMPRA_MES"
    if float(summary.get("dropPct") or 0) <= -0.1:
        return "QUEDA"
    if int(summary.get("currentSkuCount") or 0) <= 2:
        return "MIX"
    return "GERAL"


def crm_next_action(summary: dict[str, Any]) -> str:
    """Próxima ação concreta, com número e prazo — não frase genérica."""
    status = summary.get("statusCode")
    dias = summary.get("daysWithoutPurchase")
    offer = (summary.get("offerPrimary") or {}).get("title")
    media = float(summary.get("averageRevenue") or 0)

    if status == "INATIVO":
        base = f"Ligar hoje e perguntar por que parou de comprar há {dias} dias" if dias else "Ligar hoje e entender o motivo da parada"
        if offer:
            base += f". Oferecer {offer} como gancho"
        if media > 0:
            base += f". Cliente valia {brl(media)}/mês"
        return base + ". Agendar retorno na própria ligação."
    if status == "PRE_INATIVO":
        base = "Contato preventivo ainda esta semana"
        if offer:
            base += f", puxando {offer} que ele deixou de pedir"
        return base + ". Fechar pedido pequeno para não perder a frequência."
    if float(summary.get("currentRevenue") or 0) <= 0:
        base = "Ligar para reposição do mês"
        if offer:
            base += f" — confirmar se {offer} ainda tem em estoque"
        return base + ". Fechar antes do corte de entrega."
    if float(summary.get("dropPct") or 0) <= -0.1:
        queda = abs(float(summary.get("dropPct") or 0)) * 100
        return (f"Investigar queda de {queda:.0f}% na compra. Perguntar que linha migrou para "
                "outro fornecedor e cotar 2 ou 3 códigos hoje.")
    if int(summary.get("currentSkuCount") or 0) <= 2:
        base = "Cliente compra pouca variedade. Perguntar que serviço a oficina mais faz"
        if offer:
            base += f" e oferecer {offer} para teste de giro"
        return base + "."
    return "Manter frequência: confirmar reposição e explorar uma linha que ele ainda não compra."


def crm_attach_context(
    conn: sqlite3.Connection, company_id: int, summaries: list[dict[str, Any]],
    seller_name: str | None = None, with_scripts: bool = False,
) -> list[dict[str, Any]]:
    enriched: list[dict[str, Any]] = []
    # Carrega a biblioteca uma vez só quando os scripts forem necessários
    library = list_content_library(conn, company_id) if with_scripts else []
    for summary in summaries:
        offers = crm_get_offer_suggestions(
            conn, company_id, summary["clientName"], summary.get("cityName")
        )
        questions = crm_generate_questions(summary)
        summary["primaryReason"] = crm_reason_message(summary, summary["primaryReasonCode"])
        summary["secondaryReasons"] = [crm_reason_message(summary, code) for code in summary["secondaryReasonCodes"]]
        summary["offerPrimary"] = offers["primary"]
        summary["offerSecondary"] = offers["secondary"]
        summary["offerRepurchase"] = offers.get("repurchase", [])
        summary["offerOpportunity"] = offers.get("opportunity", [])
        summary["questionPrimary"] = questions["primary"]
        summary["questionSecondary"] = questions["secondary"]
        summary["situationCode"] = crm_situation_for_client(summary)
        summary["nextAction"] = crm_next_action(summary)
        if with_scripts:
            ctx = content_context_for_client(summary, seller_name)
            situation = summary["situationCode"]
            summary["scripts"] = [
                {**item, "body": render_content_text(item["body"], ctx)}
                for item in library
                if item["situation"] in {situation, "GERAL"} and item["category"] in {"ligacao", "whatsapp"}
            ]
        enriched.append(summary)
    return enriched


def crm_agenda_action_map(
    conn: sqlite3.Connection, company_id: int, seller_name: str
) -> dict[str, dict[str, Any]]:
    rows = conn.execute(
        """
        SELECT a1.*
        FROM crm_agenda_actions a1
        JOIN (
            SELECT client_key, MAX(id) AS max_id
            FROM crm_agenda_actions
            WHERE company_id = ? AND seller_name = ?
            GROUP BY client_key
        ) latest ON latest.max_id = a1.id
        WHERE a1.company_id = ? AND a1.seller_name = ?
        """,
        (company_id, seller_name, company_id, seller_name),
    ).fetchall()
    return {row["client_key"]: dict(row) for row in rows}


def crm_priority_sort_key(summary: dict[str, Any]) -> tuple[Any, ...]:
    code = summary["primaryReasonCode"]
    priority_index = CRM_PRIORITY_ORDER.index(code) if code in CRM_PRIORITY_ORDER else len(CRM_PRIORITY_ORDER)
    return (
        priority_index,
        crm_class_rank(summary["classCode"]),
        -(summary["daysWithoutPurchase"] or 0),
        summary["dropPct"],
        -summary["currentRevenue"],
        summary["clientName"],
    )


def list_crm_clients(
    conn: sqlite3.Connection,
    company_id: int,
    filters: dict[str, str | None],
    limit: int | None = None,
    attach_context: bool = True,
    exclude_contacted_today: bool = False,
) -> list[dict[str, Any]]:
    seller_name = normalize_whitespace(filters.get("seller_name"))
    rows = crm_base_client_rows_cached(conn, company_id, filters)
    action_map = crm_agenda_action_map(conn, company_id, seller_name) if seller_name else {}
    # Clientes já contactados hoje por este vendedor (só usado na Missão do Dia)
    contacted_today: set[str] = set()
    if exclude_contacted_today and seller_name:
        today_str = date.today().isoformat()
        rows_today = conn.execute(
            """SELECT DISTINCT client_key FROM crm_interactions
               WHERE company_id = ? AND seller_name = ?
                 AND substr(occurred_at, 1, 10) = ?""",
            (company_id, seller_name, today_str),
        ).fetchall()
        contacted_today = {normalize_client_key(r["client_key"]) for r in rows_today}
        with open("debug_agenda.log", "a", encoding="utf-8") as _dbg:
            _dbg.write(f"seller={seller_name!r} today={today_str} contacted={contacted_today}\n")
    visible_rows: list[dict[str, Any]] = []
    now_dt = datetime.now()
    for row in rows:
        action = action_map.get(row["clientKey"])
        row["agendaAction"] = action
        if action and action.get("action_type") == "ADIAR":
            next_visible_at = parse_datetime_flexible(action.get("next_visible_at"))
            if next_visible_at and next_visible_at > now_dt:
                continue
        if normalize_client_key(row["clientKey"]) in contacted_today:
            continue
        visible_rows.append(row)
    visible_rows.sort(key=crm_priority_sort_key)
    if limit is not None:
        visible_rows = visible_rows[:limit]
    if not attach_context:
        return visible_rows
    return crm_attach_context(conn, company_id, visible_rows)


def crm_matches_search(row: dict[str, Any], search_value: str) -> bool:
    haystack = " ".join(
        [
            normalize_whitespace(row.get("clientKey")),
            normalize_whitespace(row.get("clientCode")),
            normalize_whitespace(row.get("clientName")),
            normalize_whitespace(row.get("cityName")),
            normalize_whitespace(row.get("phone")),
            normalize_whitespace(row.get("primaryContactName")),
        ]
    ).lower()
    return search_value.lower() in haystack


def filter_crm_client_rows(rows: list[dict[str, Any]], filters: dict[str, str | None]) -> list[dict[str, Any]]:
    status_filter = normalize_upper(filters.get("status"))
    purchase_filter = normalize_upper(filters.get("purchaseMonth"))
    growth_filter = normalize_upper(filters.get("growth"))
    class_filter = normalize_upper(filters.get("classCode"))
    person_type_filter = normalize_upper(filters.get("personType"))
    search_filter = normalize_whitespace(filters.get("search"))
    filtered: list[dict[str, Any]] = []
    for row in rows:
        if status_filter and row.get("statusCode") != status_filter:
            continue
        current_revenue = float(row.get("currentRevenue") or 0.0)
        if purchase_filter == "COM_COMPRA" and current_revenue <= 0:
            continue
        if purchase_filter == "SEM_COMPRA" and current_revenue > 0:
            continue
        growth_pct = float(row.get("growthPct") or 0.0)
        if growth_filter == "ACIMA" and growth_pct <= 0.03:
            continue
        if growth_filter == "ESTAVEL" and not (-0.03 <= growth_pct <= 0.03):
            continue
        if growth_filter == "ABAIXO" and growth_pct >= -0.03:
            continue
        class_code = normalize_upper(row.get("classCode"))
        if class_filter == "SEM_CLASSE" and class_code:
            continue
        if class_filter and class_filter != "SEM_CLASSE" and class_code != class_filter:
            continue
        if person_type_filter and normalize_upper(row.get("personType")) != person_type_filter:
            continue
        if search_filter and not crm_matches_search(row, search_filter):
            continue
        filtered.append(row)
    return filtered


def query_crm_clients_page(
    conn: sqlite3.Connection,
    company_id: int,
    filters: dict[str, str | None],
    page: int,
    page_size: int,
) -> dict[str, Any]:
    all_rows = list_crm_clients(conn, company_id, filters, attach_context=False)
    filtered_rows = filter_crm_client_rows(all_rows, filters)
    total = len(filtered_rows)
    safe_page_size = min(max(int(page_size or 50), 1), 100)
    total_pages = max(math.ceil(total / safe_page_size), 1) if total else 1
    safe_page = min(max(int(page or 1), 1), total_pages)
    offset = (safe_page - 1) * safe_page_size
    visible_rows = filtered_rows[offset : offset + safe_page_size]
    rows = crm_attach_context(conn, company_id, visible_rows)
    print(
        "[CRM CLIENTS PAGE DEBUG]",
        {
            "baseRows": len(all_rows),
            "filteredRows": len(filtered_rows),
            "total": total,
            "page": safe_page,
            "pageSize": safe_page_size,
            "totalPages": total_pages,
            "rowsReturned": len(rows),
            "filters": filters,
        },
    )
    return {
        "rows": rows,
        "total": total,
        "page": safe_page,
        "pageSize": safe_page_size,
        "totalPages": total_pages,
    }


def count_crm_clients(
    conn: sqlite3.Connection,
    company_id: int,
    filters: dict[str, str | None],
) -> int:
    has_client_filters = any(
        normalize_whitespace(filters.get(key))
        for key in ("status", "purchaseMonth", "growth", "classCode", "search")
    )
    if not has_client_filters:
        return crm_base_client_count(conn, company_id, filters)
    filtered_rows = filter_crm_client_rows(list_crm_clients(conn, company_id, filters, attach_context=False), filters)
    return len(filtered_rows)


def get_crm_client_summary(
    conn: sqlite3.Connection, company_id: int, filters: dict[str, str | None], client_key: str,
    seller_name: str | None = None,
) -> dict[str, Any] | None:
    base_summary = next(
        (row for row in list_crm_clients(conn, company_id, filters, attach_context=False) if row["clientKey"] == client_key),
        None,
    )
    if not base_summary:
        return None
    # A ficha traz os scripts prontos, já com o nome do cliente preenchido
    summary = crm_attach_context(
        conn, company_id, [base_summary], seller_name=seller_name, with_scripts=True
    )[0]
    profile = conn.execute(
        """
        SELECT client_code, client_name, city_name, phone, updated_phone, primary_contact_name, contact_notes
        FROM crm_client_profiles
        WHERE company_id = ? AND client_code = ?
        """,
        (company_id, client_key),
    ).fetchone()
    profile_payload = {
        "clientKey": client_key,
        "clientCode": summary.get("clientCode") or client_key,
        "clientName": summary.get("clientName"),
        "cityName": summary.get("cityName"),
        "city_name": summary.get("cityName"),
        "phone": None,
        "updatedPhone": None,
        "primaryContactName": None,
        "contactNotes": None,
    }
    if profile:
        profile_payload.update(
            {
                "clientCode": profile["client_code"],
                "clientName": profile["client_name"] or profile_payload["clientName"],
                "cityName": profile["city_name"] or profile_payload["cityName"],
                "city_name": profile["city_name"] or profile_payload["city_name"],
                "phone": profile["phone"],
                "updatedPhone": profile["updated_phone"],
                "primaryContactName": profile["primary_contact_name"],
                "contactNotes": profile["contact_notes"],
            }
        )
    summary_payload = {
        **summary,
        "clientCode": summary.get("clientCode") or summary.get("clientKey"),
        "phone": summary.get("phone") or (profile["phone"] if profile else None),
        "updatedPhone": summary.get("updatedPhone") or (profile["updated_phone"] if profile else None),
        "primaryContactName": summary.get("primaryContactName") or (profile["primary_contact_name"] if profile else None),
        "contactNotes": summary.get("contactNotes") or (profile["contact_notes"] if profile else None),
    }
    return {"summary": summary_payload, "profile": profile_payload}


def crm_client_detail_name(
    conn: sqlite3.Connection, company_id: int, filters: dict[str, str | None], client_key: str
) -> tuple[dict[str, Any] | None, str | None]:
    summary_data = get_crm_client_summary(conn, company_id, filters, client_key)
    if not summary_data:
        return None, None
    summary = summary_data["summary"]
    detail_name = summary.get("summaryClientName") or summary.get("clientName")
    return summary_data, detail_name


def get_crm_client_purchases(
    conn: sqlite3.Connection, company_id: int, filters: dict[str, str | None], client_key: str
) -> list[dict[str, Any]] | None:
    summary_data, detail_name = crm_client_detail_name(conn, company_id, filters, client_key)
    if not summary_data:
        return None
    current_month_rows = conn.execute(
        """
        SELECT competence, ROUND(SUM(net_value), 2) AS revenue
        FROM crm_client_summary
        WHERE company_id = ? AND client_code = ?
        GROUP BY competence
        ORDER BY competence DESC
        LIMIT 6
        """,
        (company_id, client_key),
    ).fetchall()
    current_competence = crm_latest_competence(conn, company_id)
    history_competences = [shift_competence(current_competence, -offset) for offset in range(1, 6)] if current_competence else []
    candidate_names = {
        normalize_whitespace(summary_data["summary"].get("clientName")),
        normalize_whitespace(summary_data["summary"].get("summaryClientName")),
        normalize_whitespace(detail_name),
    }
    candidate_names = {name for name in candidate_names if name}
    detail_history: dict[str, float] = {}
    if candidate_names and history_competences:
        placeholders_names = ", ".join("?" for _ in candidate_names)
        placeholders_competences = ", ".join("?" for _ in history_competences)
        detail_history_rows = conn.execute(
            f"""
            SELECT competence, ROUND(SUM(net_value), 2) AS revenue
            FROM fact_sales_detail
            WHERE company_id = ? AND client_name IN ({placeholders_names}) AND competence IN ({placeholders_competences})
            GROUP BY competence
            ORDER BY competence DESC
            """,
            [company_id] + list(candidate_names) + history_competences,
        ).fetchall()
        detail_history = {row["competence"]: float(row["revenue"] or 0.0) for row in detail_history_rows}
    monthly_map = {row["competence"]: float(row["revenue"] or 0.0) for row in current_month_rows}
    for competence, revenue in detail_history.items():
        monthly_map.setdefault(competence, revenue)
    return [
        {"competence": competence, "revenue": round(monthly_map[competence], 2)}
        for competence in sorted(monthly_map.keys(), reverse=True)[:6]
    ]


def get_crm_client_items(
    conn: sqlite3.Connection, company_id: int, filters: dict[str, str | None], client_key: str, page: int, page_size: int
) -> dict[str, Any] | None:
    _, detail_name = crm_client_detail_name(conn, company_id, filters, client_key)
    if not detail_name:
        return None
    safe_page_size = min(max(int(page_size or 20), 1), 100)
    safe_page = max(int(page or 1), 1)
    offset = (safe_page - 1) * safe_page_size
    total_row = conn.execute(
        """
        SELECT COUNT(*) AS total
        FROM (
            SELECT issue_date, COALESCE(NULLIF(manufacturer_sku, ''), NULLIF(sku_key, ''), NULLIF(gtin_value, ''), 'ITEM') AS item_code
            FROM fact_sales_detail
            WHERE company_id = ? AND client_name = ?
            GROUP BY issue_date, item_code
        )
        """,
        (company_id, detail_name),
    ).fetchone()
    total = int(total_row["total"] or 0)
    total_pages = max(math.ceil(total / safe_page_size), 1) if total else 1
    safe_page = min(safe_page, total_pages)
    rows = conn.execute(
        """
        SELECT
            issue_date,
            COALESCE(NULLIF(manufacturer_sku, ''), NULLIF(sku_key, ''), NULLIF(gtin_value, ''), 'ITEM') AS item_code,
            SUM(quantity) AS quantity,
            ROUND(SUM(net_value), 2) AS net_value
        FROM fact_sales_detail
        WHERE company_id = ? AND client_name = ?
        GROUP BY issue_date, item_code
        ORDER BY datetime(issue_date) DESC
        LIMIT ? OFFSET ?
        """,
        (company_id, detail_name, safe_page_size, (safe_page - 1) * safe_page_size),
    ).fetchall()
    return {"rows": [dict(row) for row in rows], "total": total, "page": safe_page, "pageSize": safe_page_size, "totalPages": total_pages}


def get_crm_client_interactions(
    conn: sqlite3.Connection, company_id: int, filters: dict[str, str | None], client_key: str, page: int, page_size: int
) -> dict[str, Any] | None:
    summary_data = get_crm_client_summary(conn, company_id, filters, client_key)
    if not summary_data:
        return None
    safe_page_size = min(max(int(page_size or 20), 1), 100)
    total_row = conn.execute("SELECT COUNT(*) AS total FROM crm_interactions WHERE company_id = ? AND client_key = ?", (company_id, client_key)).fetchone()
    total = int(total_row["total"] or 0)
    total_pages = max(math.ceil(total / safe_page_size), 1) if total else 1
    safe_page = min(max(int(page or 1), 1), total_pages)
    rows = conn.execute(
        """
        SELECT id, contact_type_code, result_code, occurred_at, notes, question_used, had_progress,
               offer_title, next_action, followup_due_at, contact_phone, contact_name
        FROM crm_interactions
        WHERE company_id = ? AND client_key = ?
        ORDER BY datetime(occurred_at) DESC
        LIMIT ? OFFSET ?
        """,
        (company_id, client_key, safe_page_size, (safe_page - 1) * safe_page_size),
    ).fetchall()
    return {"rows": [dict(row) for row in rows], "total": total, "page": safe_page, "pageSize": safe_page_size, "totalPages": total_pages}


def get_crm_client_tasks(
    conn: sqlite3.Connection, company_id: int, filters: dict[str, str | None], client_key: str
) -> list[dict[str, Any]] | None:
    summary_data = get_crm_client_summary(conn, company_id, filters, client_key)
    if not summary_data:
        return None
    rows = conn.execute(
        """
        SELECT id, title, description, due_at, status, created_at, completed_at
        FROM crm_tasks
        WHERE company_id = ? AND client_key = ?
        ORDER BY
            CASE status WHEN 'ATRASADA' THEN 0 WHEN 'ABERTA' THEN 1 WHEN 'REAGENDADA' THEN 2 ELSE 3 END,
            datetime(due_at) ASC
        LIMIT 20
        """,
        (company_id, client_key),
    ).fetchall()
    return [dict(row) for row in rows]


def get_crm_client_360(
    conn: sqlite3.Connection, company_id: int, filters: dict[str, str | None], client_key: str
) -> dict[str, Any] | None:
    summaries = {row["clientKey"]: row for row in list_crm_clients(conn, company_id, filters)}
    summary = summaries.get(client_key)
    if not summary:
        return None
    detail_name = summary.get("summaryClientName") or summary["clientName"]
    profile = conn.execute(
        """
        SELECT client_code, client_name, trade_name, document_number, state_registration, address_line, address_number,
               neighborhood, city_name, state_name, phone, updated_phone, primary_contact_name, contact_notes,
               contact_updated_at, postal_code, first_sale_at, last_sale_at,
               credit_limit, economic_group, internal_seller_name, external_seller_name, email
        FROM crm_client_profiles
        WHERE company_id = ? AND client_code = ?
        """,
        (company_id, client_key),
    ).fetchone()
    current_month_rows = conn.execute(
        """
        SELECT competence, ROUND(SUM(net_value), 2) AS revenue
        FROM crm_client_summary
        WHERE company_id = ? AND client_code = ?
        GROUP BY competence
        ORDER BY competence DESC
        LIMIT 6
        """,
        (company_id, client_key),
    ).fetchall()
    current_competence = crm_latest_competence(conn, company_id)
    history_competences = [shift_competence(current_competence, -offset) for offset in range(1, 6)] if current_competence else []
    candidate_names = {
        normalize_whitespace(summary.get("clientName")),
        normalize_whitespace(summary.get("summaryClientName")),
        normalize_whitespace(profile["client_name"]) if profile else "",
        normalize_whitespace(profile["trade_name"]) if profile else "",
    }
    candidate_names = {name for name in candidate_names if name}
    detail_history: dict[str, float] = {}
    if candidate_names and history_competences:
        placeholders_names = ", ".join("?" for _ in candidate_names)
        placeholders_competences = ", ".join("?" for _ in history_competences)
        detail_history_rows = conn.execute(
            f"""
            SELECT competence, ROUND(SUM(net_value), 2) AS revenue
            FROM fact_sales_detail
            WHERE company_id = ? AND client_name IN ({placeholders_names}) AND competence IN ({placeholders_competences})
            GROUP BY competence
            ORDER BY competence DESC
            """,
            [company_id] + list(candidate_names) + history_competences,
        ).fetchall()
        detail_history = {row["competence"]: float(row["revenue"] or 0.0) for row in detail_history_rows}
    monthly_map = {row["competence"]: float(row["revenue"] or 0.0) for row in current_month_rows}
    for competence, revenue in detail_history.items():
        monthly_map.setdefault(competence, revenue)
    monthly_rows = [
        {"competence": competence, "revenue": round(monthly_map[competence], 2)}
        for competence in sorted(monthly_map.keys(), reverse=True)[:6]
    ]
    recent_items = conn.execute(
        """
        SELECT
            issue_date,
            COALESCE(NULLIF(manufacturer_sku, ''), NULLIF(sku_key, ''), NULLIF(gtin_value, ''), 'ITEM') AS item_code,
            SUM(quantity) AS quantity,
            ROUND(SUM(net_value), 2) AS net_value
        FROM fact_sales_detail
        WHERE company_id = ? AND client_name = ?
        GROUP BY issue_date, item_code
        ORDER BY datetime(issue_date) DESC
        LIMIT 15
        """,
        (company_id, detail_name),
    ).fetchall()
    interaction_rows = conn.execute(
        """
        SELECT id, contact_type_code, result_code, occurred_at, notes, question_used, had_progress,
               offer_title, next_action, followup_due_at, contact_phone, contact_name
        FROM crm_interactions
        WHERE company_id = ? AND client_key = ?
        ORDER BY datetime(occurred_at) DESC
        LIMIT 20
        """,
        (company_id, client_key),
    ).fetchall()
    task_rows = conn.execute(
        """
        SELECT id, title, description, due_at, status, created_at, completed_at
        FROM crm_tasks
        WHERE company_id = ? AND client_key = ?
        ORDER BY
            CASE status WHEN 'ATRASADA' THEN 0 WHEN 'ABERTA' THEN 1 WHEN 'REAGENDADA' THEN 2 ELSE 3 END,
            datetime(due_at) ASC
        LIMIT 20
        """,
        (company_id, client_key),
    ).fetchall()
    profile_payload = None
    if profile:
        profile_payload = {
            **dict(profile),
            "clientKey": client_key,
            "clientCode": profile["client_code"],
            "clientName": profile["client_name"],
            "cityName": profile["city_name"],
            "unitName": summary.get("unitName"),
            "classCode": summary.get("classCode"),
            "statusCode": summary.get("statusCode"),
            "currentRevenue": summary.get("currentRevenue"),
            "averageRevenue": summary.get("averageRevenue"),
            "growthPct": summary.get("growthPct"),
            "lastPurchaseAt": summary.get("lastPurchaseAt"),
            "daysWithoutPurchase": summary.get("daysWithoutPurchase"),
            "primaryReason": summary.get("primaryReason"),
            "updatedPhone": profile["updated_phone"],
            "primaryContactName": profile["primary_contact_name"],
            "contactNotes": profile["contact_notes"],
        }
    summary_payload = {**summary, "clientCode": summary.get("clientCode") or summary.get("clientKey")}
    return {
        "summary": summary_payload,
        "profile": profile_payload,
        "monthlyRevenue": monthly_rows,
        "recentItems": [dict(row) for row in recent_items],
        "interactions": [dict(row) for row in interaction_rows],
        "tasks": [dict(row) for row in task_rows],
    }


def crm_summary_for_user(
    conn: sqlite3.Connection, company_id: int, user: sqlite3.Row, filters: dict[str, str | None]
) -> dict[str, Any]:
    seller_name = normalize_whitespace(filters.get("seller_name")) or seller_identity_for_user(user)
    base_clients = crm_base_client_rows_cached(conn, company_id, filters)
    today_str = date.today().isoformat()  # "2026-06-02" — funciona com ambos separadores T e espaço
    contacts_today = conn.execute(
        """
        SELECT
            COUNT(*) AS total_contacts,
            SUM(CASE WHEN result_code NOT IN ('NAO_ATENDEU','PEDIU_RETORNO') THEN 1 ELSE 0 END) AS active_contacts,
            SUM(CASE WHEN result_code = 'FALOU_CLIENTE' THEN 1 ELSE 0 END) AS success_contacts,
            SUM(CASE WHEN result_code = 'GEROU_ORCAMENTO' THEN 1 ELSE 0 END) AS generated_quotes,
            SUM(CASE WHEN result_code = 'GEROU_PEDIDO' THEN 1 ELSE 0 END) AS generated_orders
        FROM crm_interactions
        WHERE company_id = ? AND seller_name = ? AND substr(occurred_at, 1, 10) = ?
        """,
        (company_id, seller_name, today_str),
    ).fetchone()
    open_tasks = conn.execute(
        """
        SELECT
            SUM(CASE WHEN status IN ('ABERTA', 'REAGENDADA') THEN 1 ELSE 0 END) AS open_tasks,
            SUM(CASE WHEN status = 'ATRASADA' THEN 1 ELSE 0 END) AS overdue_tasks
        FROM crm_tasks
        WHERE company_id = ? AND seller_name = ?
        """,
        (company_id, seller_name),
    ).fetchone()
    return {
        "portfolioSize": len(base_clients),
        "top5Count": min(len(base_clients), 5),
        "contactsToday": int(contacts_today["active_contacts"] or 0),
        "successContactsToday": int(contacts_today["success_contacts"] or 0),
        "quotesToday": int(contacts_today["generated_quotes"] or 0),
        "ordersToday": int(contacts_today["generated_orders"] or 0),
        "inactiveClients": sum(1 for client in base_clients if client["statusCode"] == "INATIVO"),
        "preInactiveClients": sum(1 for client in base_clients if client["statusCode"] == "PRE_INATIVO"),
        "openTasks": int(open_tasks["open_tasks"] or 0),
        "overdueTasks": int(open_tasks["overdue_tasks"] or 0),
    }


def save_crm_client_contact(
    conn: sqlite3.Connection,
    company_id: int,
    user: sqlite3.Row,
    payload: dict[str, Any],
) -> dict[str, Any]:
    client_key = normalize_client_key(payload.get("clientKey"))
    client_name = normalize_whitespace(payload.get("clientName"))
    updated_phone = normalize_whitespace(payload.get("updatedPhone"))
    primary_contact_name = normalize_whitespace(payload.get("primaryContactName"))
    contact_notes = normalize_whitespace(payload.get("notes") or payload.get("contactNotes"))
    if not client_key or not client_name:
        raise ValueError("Cliente invalido para atualizacao de contato")

    existing = conn.execute(
        """
        SELECT id, phone, updated_phone, primary_contact_name, contact_notes
        FROM crm_client_profiles
        WHERE company_id = ? AND client_code = ?
        """,
        (company_id, client_key),
    ).fetchone()

    if existing:
        conn.execute(
            """
            UPDATE crm_client_profiles
            SET client_name = ?,
                updated_phone = ?,
                primary_contact_name = ?,
                contact_notes = ?,
                contact_updated_at = ?,
                contact_updated_by_user_id = ?,
                updated_at = ?
            WHERE company_id = ? AND client_code = ?
            """,
            (
                client_name,
                updated_phone or None,
                primary_contact_name or None,
                contact_notes or None,
                now_iso(),
                user["id"],
                now_iso(),
                company_id,
                client_key,
            ),
        )
        return {
            "clientKey": client_key,
            "updatedPhone": updated_phone or existing["updated_phone"] or existing["phone"],
            "primaryContactName": primary_contact_name or existing["primary_contact_name"],
        }

    conn.execute(
        """
        INSERT INTO crm_client_profiles (
            company_id, client_code, client_name, updated_phone, primary_contact_name,
            contact_notes, contact_updated_at, contact_updated_by_user_id, updated_at, created_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            company_id,
            client_key,
            client_name,
            updated_phone or None,
            primary_contact_name or None,
            contact_notes or None,
            now_iso(),
            user["id"],
            now_iso(),
            now_iso(),
        ),
    )
    return {
        "clientKey": client_key,
        "updatedPhone": updated_phone,
        "primaryContactName": primary_contact_name,
    }


def create_crm_interaction(
    conn: sqlite3.Connection, company_id: int, user: sqlite3.Row, payload: dict[str, Any]
) -> dict[str, Any]:
    client_key = normalize_client_key(payload.get("clientKey"))
    client_name = normalize_whitespace(payload.get("clientName"))
    contact_phone = normalize_whitespace(payload.get("updatedPhone") or payload.get("contactPhone"))
    contact_name = normalize_whitespace(payload.get("primaryContactName") or payload.get("contactName"))
    contact_type_code = normalize_upper(payload.get("contactTypeCode"))
    result_code = normalize_upper(payload.get("resultCode"))
    occurred_at = normalize_whitespace(payload.get("occurredAt")) or now_iso()
    notes = normalize_whitespace(payload.get("notes"))
    next_action = normalize_whitespace(payload.get("nextAction"))
    followup_due_at = normalize_whitespace(payload.get("followupDueAt"))
    if not client_key or not client_name:
        raise ValueError("Cliente invalido para registro de interacao")
    if not contact_type_code:
        raise ValueError("Tipo de contato obrigatorio")
    if not result_code:
        raise ValueError("Resultado do contato obrigatorio")
    if not notes:
        raise ValueError("Observacao obrigatoria")
    contact_type = conn.execute("SELECT code FROM crm_contact_types WHERE code = ? AND is_active = 1", (contact_type_code,)).fetchone()
    if not contact_type:
        raise ValueError("Tipo de contato invalido")
    result = conn.execute("SELECT * FROM crm_contact_results WHERE code = ? AND is_active = 1", (result_code,)).fetchone()
    if not result:
        raise ValueError("Resultado do contato invalido")
    if result["requires_followup_date"] and not followup_due_at:
        raise ValueError("Este resultado exige data de retorno")
    seller_name = seller_identity_for_user(user)
    unit_name = normalize_unit(payload.get("unitName"))
    if contact_phone or contact_name:
        save_crm_client_contact(
            conn,
            company_id,
            user,
            {
                "clientKey": client_key,
                "clientName": client_name,
                "updatedPhone": contact_phone,
                "primaryContactName": contact_name,
                "notes": normalize_whitespace(payload.get("contactNotes")),
            },
        )
    cursor = conn.execute(
        """
        INSERT INTO crm_interactions (
            company_id, client_key, client_name, seller_name, unit_name,
            contact_phone, contact_name,
            contact_type_code, result_code, occurred_at, notes, question_used,
            had_progress, offer_title, next_action, followup_due_at, created_at, created_by_user_id
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            company_id,
            client_key,
            client_name,
            seller_name,
            unit_name,
            contact_phone or None,
            contact_name or None,
            contact_type_code,
            result_code,
            occurred_at,
            notes,
            normalize_whitespace(payload.get("questionUsed")),
            1 if payload.get("hadProgress") else 0,
            normalize_whitespace(payload.get("offerTitle")),
            next_action,
            followup_due_at or None,
            now_iso(),
            user["id"],
        ),
    )
    interaction_id = cursor.lastrowid
    task_id = None
    if result["generates_followup"] and followup_due_at:
        task_cursor = conn.execute(
            """
            INSERT INTO crm_tasks (
                company_id, client_key, client_name, seller_name, title, description,
                due_at, status, source_interaction_id, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, 'ABERTA', ?, ?)
            """,
            (
                company_id,
                client_key,
                client_name,
                seller_name,
                next_action or result["label"],
                notes,
                followup_due_at,
                interaction_id,
                now_iso(),
            ),
        )
        task_id = task_cursor.lastrowid
    conn.commit()
    return {"interactionId": interaction_id, "taskId": task_id}


def save_crm_agenda_action(
    conn: sqlite3.Connection, company_id: int, user: sqlite3.Row, payload: dict[str, Any]
) -> dict[str, Any]:
    client_key = normalize_client_key(payload.get("clientKey"))
    client_name = normalize_whitespace(payload.get("clientName"))
    action_type = normalize_upper(payload.get("actionType"))
    justification = normalize_whitespace(payload.get("justification"))
    next_visible_at = normalize_whitespace(payload.get("nextVisibleAt"))
    if not client_key or not client_name:
        raise ValueError("Cliente invalido para acao de agenda")
    if action_type not in {"ADIAR", "REORDENAR"}:
        raise ValueError("Acao de agenda invalida")
    if not justification:
        raise ValueError("Justificativa obrigatoria")
    seller_name = seller_identity_for_user(user)
    cursor = conn.execute(
        """
        INSERT INTO crm_agenda_actions (
            company_id, seller_name, client_key, client_name, action_type,
            justification, next_visible_at, created_at, created_by_user_id
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            company_id,
            seller_name,
            client_key,
            client_name,
            action_type,
            justification,
            next_visible_at or None,
            now_iso(),
            user["id"],
        ),
    )
    conn.commit()
    return {"actionId": cursor.lastrowid}


def complete_crm_task(
    conn: sqlite3.Connection, company_id: int, user: sqlite3.Row, task_id: int
) -> None:
    seller_name = seller_identity_for_user(user)
    row = conn.execute(
        """
        SELECT id FROM crm_tasks
        WHERE id = ? AND company_id = ? AND (? != 'Vendedor' OR seller_name = ?)
        """,
        (task_id, company_id, user["role"], seller_name),
    ).fetchone()
    if not row:
        raise ValueError("Tarefa nao encontrada")
    conn.execute(
        "UPDATE crm_tasks SET status = 'CONCLUIDA', completed_at = ? WHERE id = ?",
        (now_iso(), task_id),
    )
    conn.commit()


def reschedule_crm_task(
    conn: sqlite3.Connection, company_id: int, user: sqlite3.Row, task_id: int, due_at: str
) -> None:
    seller_name = seller_identity_for_user(user)
    row = conn.execute(
        """
        SELECT id FROM crm_tasks
        WHERE id = ? AND company_id = ? AND (? != 'Vendedor' OR seller_name = ?)
        """,
        (task_id, company_id, user["role"], seller_name),
    ).fetchone()
    if not row:
        raise ValueError("Tarefa nao encontrada")
    if not normalize_whitespace(due_at):
        raise ValueError("Nova data obrigatoria")
    conn.execute(
        "UPDATE crm_tasks SET status = 'REAGENDADA', due_at = ?, completed_at = NULL WHERE id = ?",
        (due_at, task_id),
    )
    conn.commit()


CORPORATE_HINTS = {
    "LTDA",
    "ME",
    "MEI",
    "EIRELI",
    "EPP",
    "SA",
    "S A",
    "S/A",
    "AUTO PECAS",
    "AUTOPECAS",
    "DISTRIBUIDORA",
    "COMERCIO",
    "COMERCIAL",
    "INDUSTRIA",
    "INDUSTRIAL",
    "OFICINA",
    "MECANICA",
    "CENTRO AUTOMOTIVO",
    "SERVICOS",
    "SERVICOS AUTOMOTIVOS",
    "PECAS",
    "TRANSPORTES",
    "BORRACHARIA",
    "POSTO",
    "RESTAURANTE",
    "MERCADO",
    "SUPERMERCADO",
    "FERRAGENS",
}


@functools.lru_cache(maxsize=4096)
def infer_person_type_from_name(client_name: str | None) -> tuple[str, float, str]:
    normalized = normalize_client_key(client_name)
    if not normalized:
        return "PF", 0.3, "nome_vazio"
    if any(hint in normalized for hint in CORPORATE_HINTS):
        return "PJ", 0.9, "palavra_corporativa"
    if re.search(r"\d", normalized):
        return "PJ", 0.85, "nome_com_numero"
    tokens = [token for token in normalized.split() if token]
    if len(tokens) >= 2 and all(token.isalpha() for token in tokens):
        return "PF", 0.7, "nome_pessoal"
    if len(tokens) == 1 and tokens[0].isalpha():
        return "PF", 0.55, "nome_curto"
    return "PJ", 0.6, "heuristica_empresa"


def person_type_from_document(document_value: str | None) -> tuple[str | None, str]:
    digits = re.sub(r"\D", "", document_value or "")
    if len(digits) == 11:
        return "PF", digits
    if len(digits) == 14:
        return "PJ", digits
    return None, digits


def upsert_client_registry_row(
    conn: sqlite3.Connection,
    company_id: int,
    client_name: str,
    document_number: str | None,
    person_type: str,
    source: str,
    confidence_score: float,
    notes: str | None = None,
) -> None:
    normalized_client_name = normalize_client_key(client_name)
    _, document_digits = person_type_from_document(document_number)
    now = now_iso()
    conn.execute(
        """
        INSERT INTO client_registry
            (company_id, client_name, normalized_client_name, document_number, document_digits, person_type, source, confidence_score, notes, created_at, updated_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(company_id, normalized_client_name) DO UPDATE SET
            client_name = excluded.client_name,
            document_number = excluded.document_number,
            document_digits = excluded.document_digits,
            person_type = excluded.person_type,
            source = excluded.source,
            confidence_score = excluded.confidence_score,
            notes = excluded.notes,
            updated_at = excluded.updated_at
        """,
        (
            company_id,
            normalize_whitespace(client_name),
            normalized_client_name,
            normalize_whitespace(document_number),
            document_digits,
            person_type,
            source,
            confidence_score,
            notes,
            now,
            now,
        ),
    )


def ensure_client_registry_for_sales(conn: sqlite3.Connection, company_id: int) -> None:
    existing = {
        row["normalized_client_name"]
        for row in conn.execute("SELECT normalized_client_name FROM client_registry WHERE company_id = ?", (company_id,)).fetchall()
    }
    missing_rows = conn.execute(
        """
        SELECT DISTINCT client_name
        FROM fact_sales_detail
        WHERE company_id = ? AND client_name IS NOT NULL AND TRIM(client_name) <> ''
        """,
        (company_id,),
    ).fetchall()
    created = 0
    for row in missing_rows:
        client_name = normalize_whitespace(row["client_name"])
        normalized = normalize_client_key(client_name)
        if not normalized or normalized in existing:
            continue
        person_type, confidence, reason = infer_person_type_from_name(client_name)
        upsert_client_registry_row(conn, company_id, client_name, None, person_type, "heuristica", confidence, reason)
        existing.add(normalized)
        created += 1
    if created:
        conn.commit()


def get_dashboard_data(conn: sqlite3.Connection, company_id: int, filters: dict[str, str | None]) -> dict[str, Any]:
    competences = query_competences(conn, company_id)
    primary_competence = selected_primary_competence(filters, competences)
    primary_competence = primary_competence or date.today().strftime("%Y-%m")
    competence_state = dashboard_competence_state(primary_competence)
    cutoff_date = competence_state["cutoffDate"]
    allowed_units = normalize_unit_list(filters.get("allowed_units"))
    scoped_units = [normalize_unit(filters["unit_name"])] if filters.get("unit_name") else allowed_units

    detail_conditions = ["company_id = ?", "competence = ?"]
    detail_params: list[Any] = [company_id, primary_competence]
    summary_vendor_conditions = ["company_id = ?", "competence = ?"]
    summary_vendor_params: list[Any] = [company_id, primary_competence]
    summary_unit_conditions = ["company_id = ?", "competence = ?"]
    summary_unit_params: list[Any] = [company_id, primary_competence]

    if filters["seller_name"]:
        detail_conditions.append("seller_name = ?")
        detail_params.append(filters["seller_name"])
        summary_vendor_conditions.append("seller_name = ?")
        summary_vendor_params.append(filters["seller_name"])

    detail_source_rows = conn.execute(
        f"""
        SELECT seller_name, client_name, city_name, sku_key, gross_value, discount_value, return_value, net_value, competence, sale_share, issue_date
        FROM fact_sales_detail
        WHERE {' AND '.join(detail_conditions)}
        """,
        detail_params,
    ).fetchall()

    # ── PRÉ-CARREGAR LOOKUPS (elimina N+1 queries) ──────────────────────────
    _comp_target = first_day_of_competence(primary_competence).isoformat()

    _city_map: dict[str, str | None] = {}
    for _r in conn.execute(
        """
        SELECT city_name, principal_unit
        FROM city_mappings
        WHERE company_id = ? AND date(valid_from) <= date(?)
          AND (valid_to IS NULL OR date(valid_to) >= date(?))
        ORDER BY date(valid_from) DESC
        """,
        (company_id, _comp_target, _comp_target),
    ).fetchall():
        _city_name_key = normalize_upper(_r["city_name"])
        if _city_name_key and _city_name_key not in _city_map:
            _city_map[_city_name_key] = normalize_unit(_r["principal_unit"])

    _seller_unit_map: dict[str, str | None] = {}
    _seller_role_map: dict[str, str | None] = {}
    for _r in conn.execute(
        """
        SELECT person_name, base_unit, role_classification
        FROM people_records
        WHERE company_id = ? AND date(valid_from) <= date(?)
          AND (valid_to IS NULL OR date(valid_to) >= date(?))
        ORDER BY date(valid_from) DESC
        """,
        (company_id, _comp_target, _comp_target),
    ).fetchall():
        _pname_key = normalize_whitespace(_r["person_name"])
        if _pname_key and _pname_key not in _seller_unit_map:
            _seller_unit_map[_pname_key] = normalize_unit(_r["base_unit"])
            _seller_role_map[_pname_key] = _r["role_classification"]
    # ────────────────────────────────────────────────────────────────────────

    detail_rows_all: list[dict[str, Any]] = []
    for row in detail_source_rows:
        issue_dt = parse_datetime_flexible(row["issue_date"])
        if competence_state["isFutureCompetence"]:
            continue
        if competence_state["isCurrentCompetence"]:
            # Exclui só se a data é conhecida E está no futuro; issue_date nulo = inclui (confia na competência)
            if issue_dt and issue_dt.date() > cutoff_date:
                continue
        seller_name = normalize_whitespace(row["seller_name"])
        city_name = normalize_upper(row["city_name"])
        resolved_unit = _city_map.get(city_name)
        seller_base_unit = _seller_unit_map.get(seller_name)
        enriched = dict(row)
        enriched["seller_name"] = seller_name
        enriched["client_name"] = normalize_whitespace(row["client_name"])
        enriched["city_name"] = city_name
        enriched["resolved_unit"] = resolved_unit
        enriched["seller_base_unit"] = normalize_unit(seller_base_unit)
        detail_rows_all.append(enriched)

    if filters["city_name"]:
        detail_rows_all = [row for row in detail_rows_all if row["city_name"] == filters["city_name"]]

    detail_rows_scope = detail_rows_all
    if scoped_units:
        detail_rows_scope = [row for row in detail_rows_scope if row["resolved_unit"] in scoped_units]
    if filters["unit_name"]:
        detail_rows_scope = [row for row in detail_rows_scope if row["resolved_unit"] == filters["unit_name"]]

    seller_detail_rows = detail_rows_all
    if scoped_units:
        seller_detail_rows = [row for row in seller_detail_rows if row["seller_base_unit"] in scoped_units]
    if filters["city_name"]:
        seller_detail_rows = [row for row in seller_detail_rows if row["city_name"] == filters["city_name"]]
    if filters["unit_name"]:
        seller_detail_rows = [row for row in seller_detail_rows if row["seller_base_unit"] == filters["unit_name"]]

    if scoped_units:
        placeholders = ", ".join("?" for _ in scoped_units)
        summary_unit_conditions.append(f"unit_name IN ({placeholders})")
        summary_unit_params.extend(scoped_units)
    if filters["unit_name"]:
        summary_unit_conditions.append("unit_name = ?")
        summary_unit_params.append(filters["unit_name"])

    vendor_summary_rows = [dict(row) for row in conn.execute(
        f"""
        SELECT
            seller_name,
            SUM(qty_sold) AS qty_sold,
            SUM(cost_value) AS cost_value,
            SUM(sale_value) AS sale_value,
            SUM(profit_value) AS profit_value,
            SUM(net_profit_value) AS net_profit_value,
            AVG(profit_pct) AS profit_pct,
            SUM(return_cost) AS return_cost,
            SUM(return_value) AS return_value,
            SUM(net_value) AS net_value,
            AVG(margin_value) AS margin_value
        FROM fact_vendor_summary
        WHERE {' AND '.join(summary_vendor_conditions)}
        GROUP BY seller_name
        ORDER BY net_value DESC
        """,
        summary_vendor_params,
    ).fetchall()]
    unit_summary_rows = [dict(row) for row in conn.execute(
        f"""
        SELECT
            unit_name,
            SUM(qty_sold) AS qty_sold,
            SUM(cost_value) AS cost_value,
            SUM(sale_value) AS sale_value,
            SUM(profit_value) AS profit_value,
            SUM(net_profit_value) AS net_profit_value,
            AVG(profit_pct) AS profit_pct,
            SUM(return_cost) AS return_cost,
            SUM(return_value) AS return_value,
            SUM(net_value) AS net_value,
            AVG(margin_value) AS margin_value
        FROM fact_unit_summary
        WHERE {' AND '.join(summary_unit_conditions)}
        GROUP BY unit_name
        ORDER BY net_value DESC
        """,
        summary_unit_params,
    ).fetchall()]

    vendor_summary_by_seller = {normalize_whitespace(row["seller_name"]): row for row in vendor_summary_rows}
    unit_summary_by_unit = {normalize_unit(row["unit_name"]): row for row in unit_summary_rows}

    goal_by_seller, duplicate_seller_goals = load_goal_maps(
        conn,
        company_id,
        primary_competence,
        "goals_seller",
        "seller_name",
        normalize_whitespace,
    )
    goal_by_unit, duplicate_unit_goals = load_goal_maps(
        conn,
        company_id,
        primary_competence,
        "goals_unit",
        "unit_name",
        normalize_unit,
    )
    if scoped_units:
        goal_by_unit = {unit_name: values for unit_name, values in goal_by_unit.items() if normalize_unit(unit_name) in scoped_units}
    total_unit_goal = float(sum(item["revenueGoal"] or 0 for item in goal_by_unit.values()))
    total_unit_returns_goal = float(sum(item["returnsGoal"] or 0 for item in goal_by_unit.values()))

    client_registry = {
        row["normalized_client_name"]: dict(row)
        for row in conn.execute(
            "SELECT client_name, normalized_client_name, document_number, person_type, source, confidence_score, notes FROM client_registry WHERE company_id = ?",
            (company_id,),
        ).fetchall()
    }

    # ── Devoluções em garantia ────────────────────────────────────────────────
    # Vêm dentro do total de devoluções do custo/venda, mas são defeito de peça,
    # não erro de venda. Ficam separadas para não penalizar o resultado comercial.
    warranty_by_seller: dict[str, float] = {}
    for _w in conn.execute(
        "SELECT seller_name, SUM(total_value) AS total FROM fact_warranty_returns "
        "WHERE company_id = ? AND competence = ? GROUP BY seller_name",
        (company_id, primary_competence),
    ).fetchall():
        warranty_by_seller[normalize_whitespace(_w["seller_name"])] = float(_w["total"] or 0.0)

    warranty_by_unit: dict[str, float] = {}
    for _w in conn.execute(
        "SELECT unit_name, SUM(total_value) AS total FROM fact_warranty_returns "
        "WHERE company_id = ? AND competence = ? GROUP BY unit_name",
        (company_id, primary_competence),
    ).fetchall():
        warranty_by_unit[normalize_unit(_w["unit_name"])] = float(_w["total"] or 0.0)

    # ── Dono do cliente no cadastro CRM ───────────────────────────────────────
    # Permite separar o que o vendedor faturou da PRÓPRIA carteira do que faturou
    # de clientes de outros (ou sem dono). Chave é o nome normalizado, porque o
    # faturamento não traz o código do cliente.
    client_owner_map: dict[str, str] = {}
    for _o in conn.execute(
        "SELECT client_name, internal_seller_name, external_seller_name "
        "FROM crm_client_profiles WHERE company_id = ?",
        (company_id,),
    ).fetchall():
        _key = normalize_client_key(_o["client_name"])
        if not _key:
            continue
        _owner = normalize_whitespace(_o["internal_seller_name"]) or normalize_whitespace(_o["external_seller_name"])
        if _owner:
            client_owner_map[_key] = _owner

    city_metrics: dict[str, dict[str, Any]] = defaultdict(lambda: {"revenueNet": 0.0, "grossSales": 0.0, "grossSalesPct": 0.0, "discountValue": 0.0, "returnValue": 0.0, "clients": set()})
    detail_by_seller: dict[str, dict[str, Any]] = defaultdict(lambda: {
        "revenueNet": 0.0, "grossSales": 0.0, "grossSalesPct": 0.0, "discountValue": 0.0,
        "returnValue": 0.0, "clients": set(), "sku": set(), "baseUnit": None,
        # Carteira própria x fora da carteira
        "ownClients": set(), "otherClients": set(),
        "ownRevenue": 0.0, "otherRevenue": 0.0,
    })
    detail_by_client: dict[str, dict[str, Any]] = defaultdict(lambda: {"revenueNet": 0.0, "grossSales": 0.0, "grossSalesPct": 0.0, "discountValue": 0.0, "returnValue": 0.0, "cities": set(), "personType": None, "typeSource": None, "typeConfidence": 0.0})
    detail_by_unit: dict[str, dict[str, Any]] = defaultdict(lambda: {"revenueNet": 0.0, "grossSales": 0.0, "grossSalesPct": 0.0, "discountValue": 0.0, "returnValue": 0.0, "clients": set()})
    client_top_by_unit_source: dict[str, dict[str, dict[str, Any]]] = defaultdict(lambda: defaultdict(lambda: {"revenueNet": 0.0, "grossSales": 0.0, "grossSalesPct": 0.0, "discountValue": 0.0, "returnValue": 0.0}))

    for row in detail_rows_scope:
        city_name = row["city_name"]
        seller_name = row["seller_name"]
        client_name = row["client_name"]
        resolved_unit = row["resolved_unit"] or "NAO_MAPEADO"
        net_value = float(row["net_value"] or 0)
        gross_value = float(row["gross_value"] or 0)
        gross_pct_base = max(gross_value, 0.0)
        discount_value = float(row["discount_value"] or 0)
        return_value = float(row["return_value"] or 0)
        if city_name:
            city_metrics[city_name]["revenueNet"] += net_value
            city_metrics[city_name]["grossSales"] += gross_value
            city_metrics[city_name]["grossSalesPct"] += gross_pct_base
            city_metrics[city_name]["discountValue"] += discount_value
            city_metrics[city_name]["returnValue"] += return_value
            if client_name:
                city_metrics[city_name]["clients"].add(client_name)
        if client_name:
            client_key = normalize_client_key(client_name)
            registry_row = client_registry.get(client_key)
            if registry_row:
                person_type = registry_row["person_type"]
                type_source = registry_row["source"]
                type_confidence = float(registry_row["confidence_score"] or 0)
            else:
                person_type, type_confidence, type_source = infer_person_type_from_name(client_name)
            detail_by_client[client_name]["revenueNet"] += net_value
            detail_by_client[client_name]["grossSales"] += gross_value
            detail_by_client[client_name]["grossSalesPct"] += gross_pct_base
            detail_by_client[client_name]["discountValue"] += discount_value
            detail_by_client[client_name]["returnValue"] += return_value
            detail_by_client[client_name]["personType"] = person_type
            detail_by_client[client_name]["typeSource"] = type_source
            detail_by_client[client_name]["typeConfidence"] = type_confidence
            if city_name:
                detail_by_client[client_name]["cities"].add(city_name)
            client_top_by_unit_source[resolved_unit][client_name]["revenueNet"] += net_value
            client_top_by_unit_source[resolved_unit][client_name]["grossSales"] += gross_value
            client_top_by_unit_source[resolved_unit][client_name]["grossSalesPct"] += gross_pct_base
            client_top_by_unit_source[resolved_unit][client_name]["discountValue"] += discount_value
            client_top_by_unit_source[resolved_unit][client_name]["returnValue"] += return_value
        detail_by_unit[resolved_unit]["revenueNet"] += net_value
        detail_by_unit[resolved_unit]["grossSales"] += gross_value
        detail_by_unit[resolved_unit]["grossSalesPct"] += gross_pct_base
        detail_by_unit[resolved_unit]["discountValue"] += discount_value
        detail_by_unit[resolved_unit]["returnValue"] += return_value
        if client_name:
            detail_by_unit[resolved_unit]["clients"].add(client_name)

    for row in seller_detail_rows:
        seller_name = row["seller_name"]
        client_name = row["client_name"]
        net_value = float(row["net_value"] or 0)
        gross_value = float(row["gross_value"] or 0)
        gross_pct_base = max(gross_value, 0.0)
        discount_value = float(row["discount_value"] or 0)
        return_value = float(row["return_value"] or 0)
        detail_by_seller[seller_name]["revenueNet"] += net_value
        detail_by_seller[seller_name]["grossSales"] += gross_value
        detail_by_seller[seller_name]["grossSalesPct"] += gross_pct_base
        detail_by_seller[seller_name]["discountValue"] += discount_value
        detail_by_seller[seller_name]["returnValue"] += return_value
        detail_by_seller[seller_name]["baseUnit"] = row["seller_base_unit"]
        if client_name:
            detail_by_seller[seller_name]["clients"].add(client_name)
            # Cliente é da carteira do vendedor se o cadastro CRM aponta para ele
            owner = client_owner_map.get(normalize_client_key(client_name))
            if owner and normalize_upper(owner) == normalize_upper(seller_name):
                detail_by_seller[seller_name]["ownClients"].add(client_name)
                detail_by_seller[seller_name]["ownRevenue"] += net_value
            else:
                detail_by_seller[seller_name]["otherClients"].add(client_name)
                detail_by_seller[seller_name]["otherRevenue"] += net_value
        if row["sku_key"]:
            detail_by_seller[seller_name]["sku"].add(row["sku_key"])

    city_ranking = []
    for city_name, metrics in city_metrics.items():
        distinct_clients = len(metrics["clients"])
        city_ranking.append(
            {
                "cityName": city_name,
                "revenueNet": round(metrics["revenueNet"], 2),
                "ticketAverage": round(safe_div(metrics["revenueNet"], distinct_clients), 2),
                "distinctClients": distinct_clients,
                "discountValue": round(metrics["discountValue"], 2),
                "discountPct": round(safe_div(metrics["discountValue"], metrics["grossSalesPct"]) * 100, 2),
                "returnsValue": round(metrics["returnValue"], 2),
            }
        )
    city_ranking.sort(key=lambda item: item["revenueNet"], reverse=True)

    client_ranking = []
    client_type_summary: dict[str, dict[str, Any]] = defaultdict(lambda: {"revenueNet": 0.0, "clients": 0})
    for client_name, metrics in detail_by_client.items():
        person_type = metrics["personType"] or "Nao classificado"
        client_type_summary[person_type]["revenueNet"] += metrics["revenueNet"]
        client_type_summary[person_type]["clients"] += 1
        client_ranking.append(
            {
                "clientName": client_name,
                "personType": person_type,
                "typeSource": metrics["typeSource"],
                "typeConfidence": round(float(metrics["typeConfidence"] or 0), 2),
                "revenueNet": round(metrics["revenueNet"], 2),
                "discountValue": round(metrics["discountValue"], 2),
                "discountPct": round(safe_div(metrics["discountValue"], metrics["grossSalesPct"]) * 100, 2),
                "returnsValue": round(metrics["returnValue"], 2),
                "citiesCount": len(metrics["cities"]),
            }
        )
    client_ranking.sort(key=lambda item: item["revenueNet"], reverse=True)

    client_top_by_unit = []
    for unit_name, clients in client_top_by_unit_source.items():
        if scoped_units and unit_name not in scoped_units:
            continue
        top_clients = []
        for client_name, metrics in clients.items():
            client_registry_row = client_registry.get(normalize_client_key(client_name))
            if client_registry_row:
                person_type = client_registry_row["person_type"]
            else:
                person_type, _, _ = infer_person_type_from_name(client_name)
            top_clients.append(
                {
                    "clientName": client_name,
                    "personType": person_type,
                    "revenueNet": round(metrics["revenueNet"], 2),
                    "discountValue": round(metrics["discountValue"], 2),
                    "discountPct": round(safe_div(metrics["discountValue"], metrics["grossSalesPct"]) * 100, 2),
                    "returnsValue": round(metrics["returnValue"], 2),
                }
            )
        top_clients.sort(key=lambda item: item["revenueNet"], reverse=True)
        client_top_by_unit.append({"unitName": unit_name, "clients": top_clients[:10]})
    client_top_by_unit.sort(key=lambda item: item["unitName"])

    summary_calendar = get_business_calendar(
        conn,
        company_id,
        primary_competence,
        reference_today=competence_state["today"],
        include_current_day=False,
    )
    score_config = get_score_config(conn, company_id, primary_competence)
    max_ticket = 1.0
    max_clients = 1.0
    max_mix = 1.0
    candidate_sellers = []
    for seller_name, official_row in vendor_summary_by_seller.items():
        metrics = detail_by_seller.get(
            seller_name,
            {"revenueNet": 0.0, "grossSales": 0.0, "grossSalesPct": 0.0, "discountValue": 0.0, "returnValue": 0.0, "clients": set(), "sku": set(), "baseUnit": None},
        )
        role = _seller_role_map.get(seller_name)
        base_unit = _seller_unit_map.get(seller_name)
        resolved_base_unit = normalize_unit(base_unit or metrics.get("baseUnit"))
        if role not in (None, "Vendedor"):
            continue
        if scoped_units and resolved_base_unit not in scoped_units:
            continue
        if filters["unit_name"] and resolved_base_unit != filters["unit_name"]:
            continue
        official_revenue_net = float(official_row.get("net_value") or 0.0)
        ticket = safe_div(official_revenue_net, len(metrics["clients"]))
        max_ticket = max(max_ticket, ticket)
        max_clients = max(max_clients, len(metrics["clients"]))
        max_mix = max(max_mix, len(metrics["sku"]))
        candidate_sellers.append((seller_name, metrics, official_row, role, resolved_base_unit))

    seller_rows = []
    total_company_seller_goal = 0.0
    total_company_seller_returns_goal = 0.0
    for seller_name, metrics, official_row, role, base_unit in candidate_sellers:
        gross_sales = float(official_row.get("sale_value") or 0.0)
        revenue_net_raw = float(official_row.get("net_value") or 0.0)
        gross_sales_pct = float(metrics.get("grossSalesPct") or 0.0)
        returns_total = float(official_row.get("return_value") or 0.0)
        # Devolução em garantia é defeito de peça, não erro de venda: sai do
        # resultado comercial e é devolvida ao líquido do vendedor.
        warranty_value = min(warranty_by_seller.get(seller_name, 0.0), returns_total)
        returns_value = max(returns_total - warranty_value, 0.0)
        revenue_net = revenue_net_raw + warranty_value
        qty_sold = float(official_row.get("qty_sold") or 0)
        return_cost = float(official_row.get("return_cost") or 0.0)
        cost_value = float(official_row.get("cost_value") or 0.0)
        profit_value = float(official_row.get("profit_value") or 0.0)
        net_profit_value = float(official_row.get("net_profit_value") or 0.0)
        distinct_clients = len(metrics["clients"])
        mix_count = len(metrics["sku"])
        ticket = safe_div(revenue_net, distinct_clients)
        ticket_per_piece = safe_div(revenue_net, qty_sold)
        seller_goal = goal_by_seller.get(seller_name, {"revenueGoal": 0.0, "returnsGoal": 0.0})
        revenue_goal = float(seller_goal["revenueGoal"] or 0)
        returns_goal = float(seller_goal["returnsGoal"] or 0)
        total_company_seller_goal += revenue_goal
        total_company_seller_returns_goal += returns_goal
        goal_attainment = safe_div(revenue_net, revenue_goal) * 100 if revenue_goal else 0.0
        # Calendário individual do vendedor (ajusta por férias)
        seller_calendar = get_business_calendar(
            conn, company_id, primary_competence,
            reference_today=competence_state["today"],
            include_current_day=False,
            seller_name=seller_name,
        )
        seller_total_days = seller_calendar["sellerWorkingDays"] or summary_calendar["totalWorkingDays"]
        seller_elapsed_days = seller_calendar["sellerElapsedWorkingDays"] or summary_calendar["elapsedWorkingDays"]
        daily_revenue_actual, projected_revenue_raw = dashboard_metric_projection(
            revenue_net,
            seller_elapsed_days,
            seller_total_days,
        )
        projected_revenue = round(projected_revenue_raw, 2)
        projected_goal_attainment = safe_div(projected_revenue, revenue_goal) * 100 if revenue_goal else 0.0
        return_ratio = safe_div(returns_value, revenue_net) * 100 if revenue_net else 0.0
        discount_pct = safe_div(metrics["discountValue"], gross_sales_pct) * 100
        margin_value = float(official_row.get("margin_value") or 0) if official_row and not filters["city_name"] else None
        goal_component = min(goal_attainment, 120) / 120 * 100
        ticket_component = safe_div(ticket, max_ticket) * 100
        client_component = safe_div(distinct_clients, max_clients) * 100
        mix_component = safe_div(mix_count, max_mix) * 100
        returns_component = max(0.0, 100 - min(return_ratio, 8) / 8 * 100)
        score = (
            goal_component * float(score_config["weight_goal"])
            + ticket_component * float(score_config["weight_ticket"])
            + client_component * float(score_config["weight_clients"])
            + mix_component * float(score_config["weight_mix"])
            + returns_component * float(score_config["weight_returns"])
        ) / 100
        daily_goal_value = safe_div(revenue_goal, seller_total_days) if seller_total_days else 0.0
        seller_rows.append(
            {
                "sellerName": seller_name,
                "baseUnit": base_unit,
                "role": role or "Pendente",
                "revenueNet": round(revenue_net, 2),
                "revenueGoal": round(revenue_goal, 2),
                "projectedRevenue": projected_revenue,
                "returnsValue": round(returns_value, 2),
                "warrantyReturnsValue": round(warranty_value, 2),
                "returnsTotalValue": round(returns_total, 2),
                "revenueNetWithWarranty": round(revenue_net_raw, 2),
                "returnCost": round(return_cost, 2),
                "revenueGross": round(gross_sales, 2),
                "costValue": round(cost_value, 2),
                "profitValue": round(profit_value, 2),
                "netProfitValue": round(net_profit_value, 2),
                "returnsGoal": round(returns_goal, 2),
                "goalAttainmentPct": round(goal_attainment, 2),
                "projectedGoalAttainmentPct": round(projected_goal_attainment, 2),
                "dailyRevenueActual": round(daily_revenue_actual, 2),
                "dailyGoal": round(daily_goal_value, 2),
                "ticketAverage": round(ticket, 2),
                "qtySold": round(qty_sold, 2),
                "ticketPerPiece": round(ticket_per_piece, 2),
                "distinctClients": distinct_clients,
                # Clientes da própria carteira x atendidos fora dela
                "ownClients": len(metrics.get("ownClients") or set()),
                "otherClients": len(metrics.get("otherClients") or set()),
                "ownRevenue": round(float(metrics.get("ownRevenue") or 0.0), 2),
                "otherRevenue": round(float(metrics.get("otherRevenue") or 0.0), 2),
                "mixSku": mix_count,
                "discountValue": round(metrics["discountValue"], 2),
                "discountPct": round(discount_pct, 2),
                "returnRatioPct": round(return_ratio, 2),
                "warrantyRatioPct": round(safe_div(warranty_value, revenue_net) * 100 if revenue_net else 0.0, 2),
                "returnsTotalRatioPct": round(safe_div(returns_total, revenue_net) * 100 if revenue_net else 0.0, 2),
                "marginValue": (lambda _m: round(_m, 2) if _m is not None else None)(finite_or_none(margin_value)),
                "score": round(score, 2),
                "pendingMapping": role is None,
                "missingGoal": revenue_goal <= 0,
                "metaDiaria": round(daily_goal_value, 2),
                "sellerWorkingDays": seller_total_days,
                "sellerElapsedWorkingDays": seller_elapsed_days,
                "vacationDays": summary_calendar["totalWorkingDays"] - seller_total_days,
            }
        )
    seller_rows.sort(key=lambda item: item["score"], reverse=True)

    unit_calendar = summary_calendar
    unit_rows = []
    unit_names = sorted(set(unit_summary_by_unit) | set(goal_by_unit))
    for unit_name in unit_names:
        official_row = unit_summary_by_unit.get(unit_name, {})
        unit_goal = goal_by_unit.get(unit_name, {"revenueGoal": 0.0, "returnsGoal": 0.0})
        revenue_goal = float(unit_goal["revenueGoal"] or 0)
        returns_goal = float(unit_goal["returnsGoal"] or 0)
        revenue_net_raw = float(official_row.get("net_value") or 0.0)
        gross_sales = float(official_row.get("sale_value") or 0.0)
        returns_total = float(official_row.get("return_value") or 0.0)
        # Garantia sai do resultado comercial: devolução comercial = total − garantia,
        # e o líquido volta a somar a garantia (que o custo/venda já havia descontado).
        warranty_value = min(warranty_by_unit.get(unit_name, 0.0), returns_total)
        returns_value = max(returns_total - warranty_value, 0.0)
        revenue_net = revenue_net_raw + warranty_value
        qty_sold = float(official_row.get("qty_sold") or 0.0)
        return_cost = float(official_row.get("return_cost") or 0.0)
        cost_value = float(official_row.get("cost_value") or 0.0)
        profit_value = float(official_row.get("profit_value") or 0.0)
        net_profit_value = float(official_row.get("net_profit_value") or 0.0)
        daily_revenue_actual, projected_revenue_raw = dashboard_metric_projection(
            revenue_net,
            unit_calendar["elapsedWorkingDays"],
            unit_calendar["totalWorkingDays"],
        )
        projected_revenue = round(projected_revenue_raw, 2)
        daily_goal_value = safe_div(revenue_goal, unit_calendar["totalWorkingDays"]) if unit_calendar["totalWorkingDays"] else 0.0
        unit_rows.append(
            {
                "unitName": unit_name,
                "revenueNet": round(revenue_net, 2),
                "revenueGoal": round(revenue_goal, 2),
                "projectedRevenue": projected_revenue,
                "dailyRevenueActual": round(daily_revenue_actual, 2),
                "dailyGoal": round(daily_goal_value, 2),
                "returnsValue": round(returns_value, 2),
                "warrantyReturnsValue": round(warranty_value, 2),
                "returnsTotalValue": round(returns_total, 2),
                "revenueNetWithWarranty": round(revenue_net_raw, 2),
                "returnCost": round(return_cost, 2),
                "revenueGross": round(gross_sales, 2),
                "costValue": round(cost_value, 2),
                "profitValue": round(profit_value, 2),
                "netProfitValue": round(net_profit_value, 2),
                "returnsGoal": round(returns_goal, 2),
                "returnRatioPct": round(safe_div(returns_value, revenue_net) * 100 if revenue_net else 0.0, 2),
                "warrantyRatioPct": round(safe_div(warranty_value, revenue_net) * 100 if revenue_net else 0.0, 2),
                "returnsTotalRatioPct": round(safe_div(returns_total, revenue_net) * 100 if revenue_net else 0.0, 2),
                "goalAttainmentPct": round(safe_div(revenue_net, revenue_goal) * 100 if revenue_goal else 0.0, 2),
                "projectedGoalAttainmentPct": round(safe_div(projected_revenue, revenue_goal) * 100 if revenue_goal else 0.0, 2),
                "marginValue": round(finite_or_none(official_row.get("margin_value")) or 0, 2) if official_row else None,
                "qtySold": round(qty_sold, 2),
                "ticketPerPiece": round(safe_div(revenue_net, qty_sold), 2),
                "metaDiaria": round(daily_goal_value, 2),
            }
        )
    unit_rows.sort(key=lambda item: item["revenueNet"], reverse=True)

    detail_totals = {
        "revenueNet": float(sum(row["net_value"] or 0 for row in detail_rows_scope)),
        "grossSales": float(sum(row["gross_value"] or 0 for row in detail_rows_scope)),
        "grossSalesPct": float(sum(max(float(row["gross_value"] or 0), 0.0) for row in detail_rows_scope)),
        "discountValue": float(sum(row["discount_value"] or 0 for row in detail_rows_scope)),
        "returnsValue": float(sum(row["return_value"] or 0 for row in detail_rows_scope)),
        "distinctClients": len({row["client_name"] for row in detail_rows_scope if row["client_name"]}),
    }
    detail_totals["ticketAverage"] = safe_div(detail_totals["revenueNet"], detail_totals["distinctClients"])
    detail_totals["discountPct"] = safe_div(detail_totals["discountValue"], detail_totals["grossSalesPct"]) * 100
    detail_totals["returnRatioPct"] = safe_div(detail_totals["returnsValue"], detail_totals["revenueNet"]) * 100 if detail_totals["revenueNet"] else 0.0

    # ── Carteira x fora da carteira e quebra PJ/PF no consolidado ─────────────
    _own_clients: set[str] = set()
    _other_clients: set[str] = set()
    _own_revenue = 0.0
    _other_revenue = 0.0
    _pj_clients: set[str] = set()
    _pf_clients: set[str] = set()
    _pj_revenue = 0.0
    _pf_revenue = 0.0
    for row in detail_rows_scope:
        _cname = row["client_name"]
        if not _cname:
            continue
        _net = float(row["net_value"] or 0)
        _ckey = normalize_client_key(_cname)
        _owner = client_owner_map.get(_ckey)
        if _owner and normalize_upper(_owner) == normalize_upper(row["seller_name"]):
            _own_clients.add(_cname)
            _own_revenue += _net
        else:
            _other_clients.add(_cname)
            _other_revenue += _net
        _reg = client_registry.get(_ckey)
        _ptype = _reg["person_type"] if _reg else (infer_person_type_from_name(_cname)[0])
        if normalize_upper(_ptype) == "PJ":
            _pj_clients.add(_cname)
            _pj_revenue += _net
        elif normalize_upper(_ptype) == "PF":
            _pf_clients.add(_cname)
            _pf_revenue += _net

    detail_totals["ownClients"] = len(_own_clients)
    detail_totals["otherClients"] = len(_other_clients)
    detail_totals["ownRevenue"] = round(_own_revenue, 2)
    detail_totals["otherRevenue"] = round(_other_revenue, 2)
    detail_totals["pjClients"] = len(_pj_clients)
    detail_totals["pfClients"] = len(_pf_clients)
    detail_totals["pjRevenue"] = round(_pj_revenue, 2)
    detail_totals["pfRevenue"] = round(_pf_revenue, 2)
    detail_totals["ticketAveragePj"] = round(safe_div(_pj_revenue, len(_pj_clients)), 2)
    detail_totals["ticketAveragePf"] = round(safe_div(_pf_revenue, len(_pf_clients)), 2)
    detail_totals["ticketAverageOwn"] = round(safe_div(_own_revenue, len(_own_clients)), 2)
    detail_totals["ticketAverageOther"] = round(safe_div(_other_revenue, len(_other_clients)), 2)

    official_totals_vendor = aggregate_official_summary_rows(vendor_summary_rows)
    official_totals_unit = aggregate_official_summary_rows(unit_summary_rows)

    use_detail_summary = bool(filters["city_name"])
    if filters["seller_name"] and not filters["city_name"]:
        seller_metrics = detail_by_seller.get(filters["seller_name"], {})
        official_seller = vendor_summary_by_seller.get(filters["seller_name"], {})
        seller_goal = goal_by_seller.get(filters["seller_name"], {"revenueGoal": 0.0, "returnsGoal": 0.0})
        summary_revenue = float(official_seller.get("net_value") or 0.0)
        summary_goal = float(seller_goal["revenueGoal"] or 0)
        summary_returns = float(official_seller.get("return_value") or 0.0)
        summary_returns_goal = float(seller_goal["returnsGoal"] or 0)
        summary_margin = float(official_seller.get("margin_value") or 0) if official_seller else None
        summary_qty_sold = float(official_seller.get("qty_sold") or 0)
        summary_gross = float(official_seller.get("sale_value") or 0.0)
        summary_return_cost = float(official_seller.get("return_cost") or 0.0)
        summary_cost_value = float(official_seller.get("cost_value") or 0.0)
        summary_profit_value = float(official_seller.get("profit_value") or 0.0)
        summary_net_profit_value = float(official_seller.get("net_profit_value") or 0.0)
    elif use_detail_summary:
        summary_revenue = detail_totals["revenueNet"]
        summary_goal = total_unit_goal
        summary_returns = detail_totals["returnsValue"]
        summary_returns_goal = total_unit_returns_goal
        summary_margin = None
        summary_qty_sold = 0.0
        summary_gross = detail_totals["grossSales"]
        summary_return_cost = 0.0
        summary_cost_value = 0.0
        summary_profit_value = 0.0
        summary_net_profit_value = 0.0
    else:
        summary_revenue = float(official_totals_unit["revenueNet"] or 0.0)
        summary_goal = total_unit_goal
        summary_returns = float(official_totals_unit["returnsValue"] or 0.0)
        summary_returns_goal = total_unit_returns_goal
        summary_margin = official_totals_unit["marginAverage"]
        summary_qty_sold = float(official_totals_unit["qtySold"] or 0.0)
        summary_gross = float(official_totals_unit["revenueGross"] or 0.0)
        summary_return_cost = float(official_totals_unit["returnCost"] or 0.0)
        summary_cost_value = float(official_totals_unit["costValue"] or 0.0)
        summary_profit_value = float(official_totals_unit["profitValue"] or 0.0)
        summary_net_profit_value = float(official_totals_unit["netProfitValue"] or 0.0)

    # ── Dedução da garantia no consolidado ────────────────────────────────────
    # Aplica o mesmo tratamento do vendedor e da unidade no total do grupo,
    # respeitando o recorte de vendedor/unidade que estiver ativo.
    _warranty_conditions = ["company_id = ?", "competence = ?"]
    _warranty_params: list[Any] = [company_id, primary_competence]
    if filters.get("seller_name"):
        _warranty_conditions.append("seller_name = ?")
        _warranty_params.append(filters["seller_name"])
    if filters.get("unit_name"):
        _warranty_conditions.append("unit_name = ?")
        _warranty_params.append(normalize_unit(filters["unit_name"]))
    elif scoped_units:
        _ph = ", ".join("?" for _ in scoped_units)
        _warranty_conditions.append(f"unit_name IN ({_ph})")
        _warranty_params.extend(scoped_units)
    summary_warranty = float(conn.execute(
        f"SELECT COALESCE(SUM(total_value), 0) AS total FROM fact_warranty_returns "
        f"WHERE {' AND '.join(_warranty_conditions)}",
        _warranty_params,
    ).fetchone()["total"] or 0.0)

    summary_returns_total = summary_returns
    summary_warranty = min(summary_warranty, summary_returns_total)
    summary_returns = max(summary_returns_total - summary_warranty, 0.0)
    summary_revenue_with_warranty = summary_revenue
    summary_revenue = summary_revenue + summary_warranty

    elapsed_days_current = summary_calendar["elapsedWorkingDays"]
    total_days_current = summary_calendar["totalWorkingDays"]
    daily_revenue_actual_raw, projection_revenue_raw = dashboard_metric_projection(summary_revenue, elapsed_days_current, total_days_current)
    projection_revenue = round(projection_revenue_raw, 2)
    score_average = round(sum(item["score"] for item in seller_rows) / len(seller_rows), 2) if seller_rows else 0.0
    daily_revenue_actual = round(daily_revenue_actual_raw, 2)
    daily_goal = round(safe_div(summary_goal, total_days_current), 2) if total_days_current else 0.0
    revenue_pf_pct = round(safe_div(client_type_summary.get("PF", {}).get("revenueNet", 0.0), detail_totals["revenueNet"]) * 100, 2) if detail_totals["revenueNet"] else 0.0
    revenue_pj_pct = round(safe_div(client_type_summary.get("PJ", {}).get("revenueNet", 0.0), detail_totals["revenueNet"]) * 100, 2) if detail_totals["revenueNet"] else 0.0
    summary_distinct_clients = detail_totals["distinctClients"]
    summary_ticket_average = round(safe_div(summary_revenue, summary_distinct_clients), 2)
    summary_ticket_per_piece = round(safe_div(summary_revenue, summary_qty_sold), 2)
    summary_discount_value = round(detail_totals["discountValue"], 2)
    summary_discount_pct = round(safe_div(detail_totals["discountValue"], summary_gross) * 100, 2)

    comparison_previous = {}
    comparison_yoy = {}
    if primary_competence:
        year, month = map(int, primary_competence.split("-"))
        prev_date = first_day_of_competence(primary_competence)
        previous_date = (prev_date.replace(day=1) - timedelta(days=1)).replace(day=1)
        comparison_previous = _cached_single_competence_summary(
            conn,
            company_id,
            previous_date.strftime("%Y-%m"),
            filters,
        )
        comparison_yoy = _cached_single_competence_summary(
            conn,
            company_id,
            f"{year - 1:04d}-{month:02d}",
            filters,
        )

    data_quality = {
        "pendingSellers": conn.execute(
            "SELECT COUNT(*) AS total FROM import_issues WHERE company_id = ? AND status = 'pendente' AND issue_type = 'vendedor_sem_vinculo'",
            (company_id,),
        ).fetchone()["total"],
        "pendingCities": conn.execute(
            "SELECT COUNT(*) AS total FROM import_issues WHERE company_id = ? AND status = 'pendente' AND issue_type = 'cidade_sem_correspondencia'",
            (company_id,),
        ).fetchone()["total"],
        "duplicateRowsSkipped": conn.execute(
            "SELECT COALESCE(SUM(duplicate_rows_skipped), 0) AS total FROM imports WHERE company_id = ?",
            (company_id,),
        ).fetchone()["total"],
    }

    debug_projection = {
        "timezone": "America/Sao_Paulo",
        "today": competence_state["today"].isoformat(),
        "cutoffDate": cutoff_date.isoformat(),
        "competenceUsed": primary_competence,
        "isCurrentCompetence": competence_state["isCurrentCompetence"],
        "isPastCompetence": competence_state["isPastCompetence"],
        "isFutureCompetence": competence_state["isFutureCompetence"],
        "revenueNet": round(summary_revenue, 2),
        "revenueNetUntilCutoff": round(summary_revenue, 2),
        "revenueGoal": round(summary_goal, 2),
        "expectedGroupGoal": 6477000,
        "totalWorkingDays": total_days_current,
        "elapsedWorkingDays": elapsed_days_current,
        "remainingWorkingDays": summary_calendar["remainingWorkingDays"],
        "dailyRevenueActual": daily_revenue_actual,
        "dailyGoal": daily_goal,
        "projectedRevenue": projection_revenue,
        "goalAttainmentPct": round(safe_div(summary_revenue, summary_goal) * 100 if summary_goal else 0.0, 2),
        "projectedGoalAttainmentPct": round(safe_div(projection_revenue, summary_goal) * 100 if summary_goal else 0.0, 2),
        "formula": {
            "cutoffDate": "today - 1 day",
            "dailyRevenueActual": "revenueNet / elapsedWorkingDays",
            "projectedRevenue": "dailyRevenueActual * totalWorkingDays",
            "dailyGoal": "revenueGoal / totalWorkingDays",
            "goalAttainmentPct": "revenueNet / revenueGoal * 100",
            "projectedGoalAttainmentPct": "projectedRevenue / revenueGoal * 100",
        },
        "unitGoalsBreakdown": [
            {"unitName": unit_name, "revenueGoal": round(values["revenueGoal"], 2)}
            for unit_name, values in sorted(goal_by_unit.items())
        ],
        "unitGoalsSum": round(total_unit_goal, 2),
        "sellerGoalsSum": round(total_company_seller_goal, 2),
        "duplicateUnitGoals": duplicate_unit_goals,
        "duplicateSellerGoals": duplicate_seller_goals,
    }
    if DASHBOARD_DEBUG_LOG:
        print("[DASHBOARD D-1 PROJECTION DEBUG]", debug_projection)
    debug_comparisons = {
        "current": {
            "competence": primary_competence,
            "unit": filters.get("unit_name"),
            "seller": filters.get("seller_name"),
            "city": filters.get("city_name"),
            "revenueNet": round(summary_revenue, 2),
        },
        "previousCompetence": {
            "competence": comparison_previous.get("competence"),
            "unit": comparison_previous.get("unit"),
            "seller": comparison_previous.get("seller"),
            "city": comparison_previous.get("city"),
            "revenueNet": comparison_previous.get("revenueNet"),
        },
        "yearOverYear": {
            "competence": comparison_yoy.get("competence"),
            "unit": comparison_yoy.get("unit"),
            "seller": comparison_yoy.get("seller"),
            "city": comparison_yoy.get("city"),
            "revenueNet": comparison_yoy.get("revenueNet"),
        },
    }
    if DASHBOARD_DEBUG_LOG:
        print("[debugComparisons]", debug_comparisons)

    return {
        "filters": filters,
        "revenueSourcePolicy": {
            "executiveSummary": "fact_unit_summary" if not filters.get("seller_name") and not filters.get("city_name") else ("fact_vendor_summary" if filters.get("seller_name") and not filters.get("city_name") else "fact_sales_detail"),
            "unitPerformance": "fact_unit_summary",
            "sellerRanking": "fact_vendor_summary",
            "cityRanking": "fact_sales_detail",
            "clientRanking": "fact_sales_detail",
            "crm": "crm_client_summary + fact_sales_detail",
        },
        "availableCompetences": competences,
        "primaryCompetence": primary_competence,
        "calendar": summary_calendar,
        "summary": {
            "revenueNet": round(summary_revenue, 2),
            "revenueGoal": round(summary_goal, 2),
            "projectedRevenue": projection_revenue,
            "returnsValue": round(summary_returns, 2),
            # Garantia separada do resultado comercial
            "warrantyReturnsValue": round(summary_warranty, 2),
            "returnsTotalValue": round(summary_returns_total, 2),
            "revenueNetWithWarranty": round(summary_revenue_with_warranty, 2),
            "returnCost": round(summary_return_cost, 2),
            "revenueGross": round(summary_gross, 2),
            "costValue": round(summary_cost_value, 2),
            "profitValue": round(summary_profit_value, 2),
            "netProfitValue": round(summary_net_profit_value, 2),
            "returnsGoal": round(summary_returns_goal, 2),
            "returnRatioPct": round(safe_div(summary_returns, summary_revenue) * 100 if summary_revenue else 0.0, 2),
            "warrantyRatioPct": round(safe_div(summary_warranty, summary_revenue) * 100 if summary_revenue else 0.0, 2),
            "returnsTotalRatioPct": round(safe_div(summary_returns_total, summary_revenue) * 100 if summary_revenue else 0.0, 2),
            "goalAttainmentPct": round(safe_div(summary_revenue, summary_goal) * 100 if summary_goal else 0.0, 2),
            "projectedGoalAttainmentPct": round(safe_div(projection_revenue, summary_goal) * 100 if summary_goal else 0.0, 2),
            "dailyRevenueActual": daily_revenue_actual,
            "dailyGoal": daily_goal,
            "revenuePfPct": revenue_pf_pct,
            "revenuePjPct": revenue_pj_pct,
            "ticketAverage": summary_ticket_average,
            "qtySold": round(summary_qty_sold, 2),
            "ticketPerPiece": summary_ticket_per_piece,
            "distinctClients": summary_distinct_clients,
            # Clientes atendidos: quantos são de carteira e quantos vieram de fora
            "ownClients": detail_totals["ownClients"],
            "otherClients": detail_totals["otherClients"],
            "ownRevenue": detail_totals["ownRevenue"],
            "otherRevenue": detail_totals["otherRevenue"],
            "ticketAverageOwn": detail_totals["ticketAverageOwn"],
            "ticketAverageOther": detail_totals["ticketAverageOther"],
            # Quebra por tipo de pessoa
            "pjClients": detail_totals["pjClients"],
            "pfClients": detail_totals["pfClients"],
            "pjRevenue": detail_totals["pjRevenue"],
            "pfRevenue": detail_totals["pfRevenue"],
            "ticketAveragePj": detail_totals["ticketAveragePj"],
            "ticketAveragePf": detail_totals["ticketAveragePf"],
            "marginAverage": round(summary_margin, 2) if summary_margin is not None else None,
            "discountValue": summary_discount_value,
            "discountPct": summary_discount_pct,
            "scoreAverage": score_average,
            "workingDaysTotal": total_days_current,
            "workingDaysElapsed": elapsed_days_current,
            "dailyRevenueTarget": daily_goal,
        },
        "debugProjection": debug_projection,
        "debugComparisons": debug_comparisons,
        "comparisons": {
            "previousCompetence": comparison_previous,
            "yearOverYear": comparison_yoy,
        },
        "sellerRanking": seller_rows,
        "sellerTop10": seller_rows[:10],
        "unitPerformance": unit_rows,
        "cityRanking": city_ranking,
        "clientRanking": client_ranking,
        "clientTopByUnit": client_top_by_unit,
        "clientTypeSummary": {key: {"revenueNet": round(value["revenueNet"], 2), "clients": value["clients"]} for key, value in client_type_summary.items()},
        "scoreWeights": {
            "goal": score_config["weight_goal"],
            "ticket": score_config["weight_ticket"],
            "clients": score_config["weight_clients"],
            "mix": score_config["weight_mix"],
            "returns": score_config["weight_returns"],
        },
        "quadrant": {
            "xReference": 100,
            "yReference": score_average,
            "points": [{"sellerName": row["sellerName"], "x": row["goalAttainmentPct"], "y": row["score"]} for row in seller_rows],
        },
        "dataQuality": data_quality,
    }


def single_competence_summary(
    conn: sqlite3.Connection,
    company_id: int,
    competence: str | None,
    filters: dict[str, str | None] | None = None,
) -> dict[str, Any]:
    if not competence:
        return {}

    scoped_filters = dict(filters or {})
    scoped_filters.setdefault("unit_name", None)
    scoped_filters.setdefault("seller_name", None)
    scoped_filters.setdefault("city_name", None)
    scoped_filters.setdefault("allowed_units", None)
    allowed_units = normalize_unit_list(scoped_filters.get("allowed_units"))
    scoped_units = [normalize_unit(scoped_filters["unit_name"])] if scoped_filters.get("unit_name") else allowed_units

    detail_conditions = ["company_id = ?", "competence = ?"]
    detail_params: list[Any] = [company_id, competence]
    summary_vendor_conditions = ["company_id = ?", "competence = ?"]
    summary_vendor_params: list[Any] = [company_id, competence]
    summary_unit_conditions = ["company_id = ?", "competence = ?"]
    summary_unit_params: list[Any] = [company_id, competence]

    if scoped_filters["seller_name"]:
        detail_conditions.append("seller_name = ?")
        detail_params.append(scoped_filters["seller_name"])
        summary_vendor_conditions.append("seller_name = ?")
        summary_vendor_params.append(scoped_filters["seller_name"])

    detail_source_rows = conn.execute(
        f"""
        SELECT seller_name, client_name, city_name, gross_value, discount_value, return_value, net_value, competence, issue_date
        FROM fact_sales_detail
        WHERE {' AND '.join(detail_conditions)}
        """,
        detail_params,
    ).fetchall()

    competence_state = dashboard_competence_state(competence)
    cutoff_date = competence_state["cutoffDate"]

    # ── PRÉ-CARREGAR LOOKUPS (elimina N+1 queries) ──────────────────────────
    _comp_target = first_day_of_competence(competence).isoformat()

    _city_map: dict[str, str | None] = {}
    for _r in conn.execute(
        """
        SELECT city_name, principal_unit FROM city_mappings
        WHERE company_id = ? AND date(valid_from) <= date(?)
          AND (valid_to IS NULL OR date(valid_to) >= date(?))
        ORDER BY date(valid_from) DESC
        """,
        (company_id, _comp_target, _comp_target),
    ).fetchall():
        _k = normalize_upper(_r["city_name"])
        if _k and _k not in _city_map:
            _city_map[_k] = normalize_unit(_r["principal_unit"])

    _seller_unit_map: dict[str, str | None] = {}
    for _r in conn.execute(
        """
        SELECT person_name, base_unit FROM people_records
        WHERE company_id = ? AND date(valid_from) <= date(?)
          AND (valid_to IS NULL OR date(valid_to) >= date(?))
        ORDER BY date(valid_from) DESC
        """,
        (company_id, _comp_target, _comp_target),
    ).fetchall():
        _k = normalize_whitespace(_r["person_name"])
        if _k and _k not in _seller_unit_map:
            _seller_unit_map[_k] = normalize_unit(_r["base_unit"])
    # ────────────────────────────────────────────────────────────────────────

    detail_rows_all: list[dict[str, Any]] = []
    for row in detail_source_rows:
        issue_dt = parse_datetime_flexible(row["issue_date"])
        if competence_state["isFutureCompetence"]:
            continue
        if competence_state["isCurrentCompetence"] and issue_dt and issue_dt.date() > cutoff_date:
            continue
        seller_name = normalize_whitespace(row["seller_name"])
        city_name = normalize_upper(row["city_name"])
        resolved_unit = _city_map.get(city_name)
        seller_base_unit = _seller_unit_map.get(seller_name)
        enriched = dict(row)
        enriched["seller_name"] = seller_name
        enriched["client_name"] = normalize_whitespace(row["client_name"])
        enriched["city_name"] = city_name
        enriched["resolved_unit"] = resolved_unit
        enriched["seller_base_unit"] = normalize_unit(seller_base_unit)
        detail_rows_all.append(enriched)

    if scoped_filters["city_name"]:
        detail_rows_all = [row for row in detail_rows_all if row["city_name"] == scoped_filters["city_name"]]

    detail_rows_scope = detail_rows_all
    if scoped_units:
        detail_rows_scope = [row for row in detail_rows_scope if row["resolved_unit"] in scoped_units]
    if scoped_filters["unit_name"]:
        detail_rows_scope = [row for row in detail_rows_scope if row["resolved_unit"] == scoped_filters["unit_name"]]

    seller_detail_rows = detail_rows_all
    if scoped_units:
        seller_detail_rows = [row for row in seller_detail_rows if row["seller_base_unit"] in scoped_units]
    if scoped_filters["city_name"]:
        seller_detail_rows = [row for row in seller_detail_rows if row["city_name"] == scoped_filters["city_name"]]
    if scoped_filters["unit_name"]:
        seller_detail_rows = [row for row in seller_detail_rows if row["seller_base_unit"] == scoped_filters["unit_name"]]

    if scoped_units:
        placeholders = ", ".join("?" for _ in scoped_units)
        summary_unit_conditions.append(f"unit_name IN ({placeholders})")
        summary_unit_params.extend(scoped_units)
    if scoped_filters["unit_name"]:
        summary_unit_conditions.append("unit_name = ?")
        summary_unit_params.append(scoped_filters["unit_name"])

    vendor_summary_rows = [
        dict(row)
        for row in conn.execute(
            f"""
        SELECT
            seller_name,
            SUM(qty_sold) AS qty_sold,
            SUM(cost_value) AS cost_value,
            SUM(sale_value) AS sale_value,
            SUM(profit_value) AS profit_value,
            SUM(net_profit_value) AS net_profit_value,
            SUM(return_cost) AS return_cost,
            SUM(return_value) AS return_value,
            SUM(net_value) AS net_value,
            AVG(margin_value) AS margin_value
        FROM fact_vendor_summary
            WHERE {' AND '.join(summary_vendor_conditions)}
            GROUP BY seller_name
            """,
            summary_vendor_params,
        ).fetchall()
    ]
    unit_summary_rows = [
        dict(row)
        for row in conn.execute(
            f"""
        SELECT
            unit_name,
            SUM(qty_sold) AS qty_sold,
            SUM(cost_value) AS cost_value,
            SUM(sale_value) AS sale_value,
            SUM(profit_value) AS profit_value,
            SUM(net_profit_value) AS net_profit_value,
            SUM(return_cost) AS return_cost,
            SUM(return_value) AS return_value,
            SUM(net_value) AS net_value,
            AVG(margin_value) AS margin_value
        FROM fact_unit_summary
            WHERE {' AND '.join(summary_unit_conditions)}
            GROUP BY unit_name
            """,
            summary_unit_params,
        ).fetchall()
    ]
    vendor_summary_by_seller = {normalize_whitespace(row["seller_name"]): row for row in vendor_summary_rows}

    goal_by_seller, _ = load_goal_maps(
        conn,
        company_id,
        competence,
        "goals_seller",
        "seller_name",
        normalize_whitespace,
    )
    goal_by_unit, _ = load_goal_maps(
        conn,
        company_id,
        competence,
        "goals_unit",
        "unit_name",
        normalize_unit,
    )
    if scoped_units:
        goal_by_unit = {
            unit_name: values
            for unit_name, values in goal_by_unit.items()
            if normalize_unit(unit_name) in scoped_units
        }
    total_unit_goal = float(sum(item["revenueGoal"] or 0 for item in goal_by_unit.values()))
    total_unit_returns_goal = float(sum(item["returnsGoal"] or 0 for item in goal_by_unit.values()))

    detail_by_seller: dict[str, dict[str, Any]] = defaultdict(
        lambda: {"revenueNet": 0.0, "grossSales": 0.0, "returnValue": 0.0, "clients": set()}
    )
    detail_by_unit: dict[str, dict[str, Any]] = defaultdict(
        lambda: {"revenueNet": 0.0, "grossSales": 0.0, "returnValue": 0.0, "clients": set()}
    )

    for row in detail_rows_scope:
        resolved_unit = row["resolved_unit"] or "NAO_MAPEADO"
        net_value = float(row["net_value"] or 0.0)
        gross_value = float(row["gross_value"] or 0.0)
        return_value = float(row["return_value"] or 0.0)
        client_name = row["client_name"]
        detail_by_unit[resolved_unit]["revenueNet"] += net_value
        detail_by_unit[resolved_unit]["grossSales"] += gross_value
        detail_by_unit[resolved_unit]["returnValue"] += return_value
        if client_name:
            detail_by_unit[resolved_unit]["clients"].add(client_name)

    for row in seller_detail_rows:
        seller_name = row["seller_name"]
        net_value = float(row["net_value"] or 0.0)
        gross_value = float(row["gross_value"] or 0.0)
        return_value = float(row["return_value"] or 0.0)
        client_name = row["client_name"]
        detail_by_seller[seller_name]["revenueNet"] += net_value
        detail_by_seller[seller_name]["grossSales"] += gross_value
        detail_by_seller[seller_name]["returnValue"] += return_value
        if client_name:
            detail_by_seller[seller_name]["clients"].add(client_name)

    detail_totals = {
        "revenueNet": float(sum(float(row["net_value"] or 0.0) for row in detail_rows_scope)),
        "grossSales": float(sum(float(row["gross_value"] or 0.0) for row in detail_rows_scope)),
        "returnsValue": float(sum(float(row["return_value"] or 0.0) for row in detail_rows_scope)),
        "discountValue": float(sum(float(row["discount_value"] or 0.0) for row in detail_rows_scope)),
        "distinctClients": len({row["client_name"] for row in detail_rows_scope if row["client_name"]}),
    }
    official_totals_unit = aggregate_official_summary_rows(unit_summary_rows)

    if scoped_filters["seller_name"] and not scoped_filters["city_name"]:
        seller_metrics = detail_by_seller.get(scoped_filters["seller_name"], {})
        official_seller = vendor_summary_by_seller.get(scoped_filters["seller_name"], {})
        seller_goal = goal_by_seller.get(scoped_filters["seller_name"], {"revenueGoal": 0.0, "returnsGoal": 0.0})
        summary_revenue = float(official_seller.get("net_value") or 0.0)
        summary_goal = float(seller_goal["revenueGoal"] or 0)
        summary_returns = float(official_seller.get("return_value") or 0.0)
        summary_returns_goal = float(seller_goal["returnsGoal"] or 0)
        summary_margin = float(official_seller.get("margin_value") or 0) if official_seller else None
        summary_qty_sold = float(official_seller.get("qty_sold") or 0.0)
        summary_gross = float(official_seller.get("sale_value") or 0.0)
    elif scoped_filters["city_name"]:
        summary_revenue = detail_totals["revenueNet"]
        summary_goal = total_unit_goal
        summary_returns = detail_totals["returnsValue"]
        summary_returns_goal = total_unit_returns_goal
        summary_margin = None
        summary_qty_sold = 0.0
        summary_gross = detail_totals["grossSales"]
    else:
        summary_revenue = float(official_totals_unit["revenueNet"] or 0.0)
        summary_goal = total_unit_goal
        summary_returns = float(official_totals_unit["returnsValue"] or 0.0)
        summary_returns_goal = total_unit_returns_goal
        summary_margin = official_totals_unit["marginAverage"]
        summary_qty_sold = float(official_totals_unit["qtySold"] or 0.0)
        summary_gross = float(official_totals_unit["revenueGross"] or 0.0)

    calendar = get_business_calendar(conn, company_id, competence)
    return {
        "competence": competence,
        "unit": scoped_filters.get("unit_name"),
        "seller": scoped_filters.get("seller_name"),
        "city": scoped_filters.get("city_name"),
        "revenueNet": round(summary_revenue, 2),
        "revenueGoal": round(summary_goal, 2),
        "returnsValue": round(summary_returns, 2),
        "returnsGoal": round(summary_returns_goal, 2),
        "returnRatioPct": round(safe_div(summary_returns, summary_revenue) * 100 if summary_revenue else 0.0, 2),
        "dailyRevenue": round(safe_div(summary_revenue, max(calendar["totalWorkingDays"], 1)), 2),
        "marginAverage": round(summary_margin, 2) if summary_margin is not None else None,
        "distinctClients": detail_totals["distinctClients"],
        "discountValue": round(detail_totals["discountValue"], 2),
        "qtySold": round(summary_qty_sold, 2),
    }


AUDIT_TOLERANCE = 0.05


def audit_filters_for_competence(competence: str, **overrides: Any) -> dict[str, str | None]:
    filters: dict[str, str | None] = {
        "competence_start": competence,
        "competence_end": competence,
        "unit_name": None,
        "seller_name": None,
        "city_name": None,
        "status": None,
        "purchaseMonth": None,
        "growth": None,
        "classCode": None,
        "search": None,
        "allowed_units": None,
    }
    filters.update(overrides)
    return filters


def audit_round(value: float | int | None) -> float:
    return round(float(value or 0.0), 2)


def audit_same(a: float | int | None, b: float | int | None, tolerance: float = AUDIT_TOLERANCE) -> bool:
    return abs(float(a or 0.0) - float(b or 0.0)) <= tolerance


def append_audit_issue(
    issues: list[dict[str, Any]],
    severity: str,
    area: str,
    message: str,
    expected: Any,
    actual: Any,
) -> None:
    issues.append(
        {
            "severity": severity,
            "area": area,
            "message": message,
            "expected": expected,
            "actual": actual,
        }
    )


def count_rows_for_import_file(conn: sqlite3.Connection, import_id: int, file_type: str) -> int:
    table_map = {
        "faturamento_detalhado": "fact_sales_detail",
        "custo_vendedor": "fact_vendor_summary",
        "custo_unidade": "fact_unit_summary",
        "cadastro_clientes": "crm_client_profiles",
        "faturamento_cliente_consolidado": "crm_client_summary",
    }
    table_name = table_map.get(file_type)
    if not table_name:
        return 0
    if file_type == "cadastro_clientes":
        row = conn.execute(
            f"SELECT COUNT(*) AS total FROM {table_name} WHERE source_import_id = ?",
            (import_id,),
        ).fetchone()
    else:
        row = conn.execute(
            f"SELECT COUNT(*) AS total FROM {table_name} WHERE import_id = ?",
            (import_id,),
        ).fetchone()
    return int(row["total"] or 0)


def summarize_imports_for_competence(conn: sqlite3.Connection, company_id: int, competence: str) -> dict[str, Any]:
    import_rows = conn.execute(
        """
        SELECT imports.*, users.username AS imported_by_username
        FROM imports
        LEFT JOIN users ON users.id = imports.imported_by
        WHERE imports.company_id = ? AND imports.competence = ?
        ORDER BY datetime(imports.imported_at) DESC, imports.id DESC
        """,
        (company_id, competence),
    ).fetchall()
    summaries: list[dict[str, Any]] = []
    totals = {
        "imports": 0,
        "files": 0,
        "rowsRead": 0,
        "rowsWritten": 0,
        "duplicateRowsSkipped": 0,
        "errors": 0,
        "pendingIssues": 0,
    }
    for import_row in import_rows:
        file_rows = conn.execute(
            """
            SELECT file_type, original_name, row_count, file_hash
            FROM import_files
            WHERE import_id = ?
            ORDER BY id
            """,
            (import_row["id"],),
        ).fetchall()
        pending_issues = int(
            conn.execute(
                "SELECT COUNT(*) AS total FROM import_issues WHERE import_id = ?",
                (import_row["id"],),
            ).fetchone()["total"]
            or 0
        )
        files_summary = []
        rows_read = 0
        rows_written = 0
        for file_row in file_rows:
            read_count = int(file_row["row_count"] or 0)
            written_count = count_rows_for_import_file(conn, import_row["id"], file_row["file_type"])
            rows_read += read_count
            rows_written += written_count
            files_summary.append(
                {
                    "fileType": file_row["file_type"],
                    "fileName": file_row["original_name"],
                    "rowsRead": read_count,
                    "rowsWritten": written_count,
                    "fileHash": file_row["file_hash"],
                }
            )
        summaries.append(
            {
                "importId": import_row["id"],
                "competence": import_row["competence"],
                "importedAt": import_row["imported_at"],
                "importedBy": import_row["imported_by_username"],
                "action": import_row["import_action"],
                "suggestedCompetence": import_row["suggested_competence"],
                "files": files_summary,
                "rowsRead": rows_read,
                "rowsWritten": rows_written,
                "duplicateRowsSkipped": int(import_row["duplicate_rows_skipped"] or 0),
                "errors": 0,
                "pendingIssues": pending_issues,
            }
        )
        totals["imports"] += 1
        totals["files"] += len(files_summary)
        totals["rowsRead"] += rows_read
        totals["rowsWritten"] += rows_written
        totals["duplicateRowsSkipped"] += int(import_row["duplicate_rows_skipped"] or 0)
        totals["pendingIssues"] += pending_issues
    return {"competence": competence, "imports": summaries, "totals": totals}


def audit_revenue_gap_detail(
    conn: sqlite3.Connection,
    company_id: int,
    competence: str,
    dashboard: dict[str, Any],
    filters: dict[str, Any] | None = None,
) -> dict[str, Any]:
    scoped_filters = dict(filters or {})
    scoped_filters.setdefault("unit_name", None)
    scoped_filters.setdefault("seller_name", None)
    scoped_filters.setdefault("city_name", None)
    scoped_filters.setdefault("allowed_units", None)
    allowed_units = normalize_unit_list(scoped_filters.get("allowed_units"))
    scoped_units = [normalize_unit(scoped_filters["unit_name"])] if scoped_filters.get("unit_name") else allowed_units

    detail_rows = conn.execute(
        """
        SELECT seller_name, city_name, net_value, competence, issue_date
        FROM fact_sales_detail
        WHERE company_id = ? AND competence = ?
        """,
        (company_id, competence),
    ).fetchall()
    competence_state = dashboard_competence_state(competence)
    cutoff_date = competence_state["cutoffDate"]

    raw_detail_revenue = 0.0
    raw_detail_rows = 0
    scope_detail_revenue = 0.0
    scope_detail_rows = 0
    unit_revenue_map: dict[str, float] = defaultdict(float)
    seller_revenue_map: dict[str, float] = defaultdict(float)
    missing_unit_revenue_map: dict[str, float] = defaultdict(float)
    missing_seller_revenue_map: dict[str, float] = defaultdict(float)
    missing_city_revenue_map: dict[str, float] = defaultdict(float)

    discarded = {
        "unitWithoutMapping": {"rows": 0, "revenue": 0.0},
        "sellerWithoutMapping": {"rows": 0, "revenue": 0.0},
        "cityWithoutMapping": {"rows": 0, "revenue": 0.0},
        "invalidCompetence": {"rows": 0, "revenue": 0.0},
        "userScope": {"rows": 0, "revenue": 0.0},
        "nonSellerRole": {"rows": 0, "revenue": 0.0},
    }

    # ── PRÉ-CARREGAR LOOKUPS ────────────────────────────────────────────────
    _comp_target_a = first_day_of_competence(competence).isoformat()
    _city_map_a: dict[str, str | None] = {}
    for _r in conn.execute(
        "SELECT city_name, principal_unit FROM city_mappings WHERE company_id = ? AND date(valid_from) <= date(?) AND (valid_to IS NULL OR date(valid_to) >= date(?)) ORDER BY date(valid_from) DESC",
        (company_id, _comp_target_a, _comp_target_a),
    ).fetchall():
        _k = normalize_upper(_r["city_name"])
        if _k and _k not in _city_map_a:
            _city_map_a[_k] = normalize_unit(_r["principal_unit"])
    _seller_role_map_a: dict[str, tuple[str | None, str | None]] = {}
    for _r in conn.execute(
        "SELECT person_name, role_classification, base_unit FROM people_records WHERE company_id = ? AND date(valid_from) <= date(?) AND (valid_to IS NULL OR date(valid_to) >= date(?)) ORDER BY date(valid_from) DESC",
        (company_id, _comp_target_a, _comp_target_a),
    ).fetchall():
        _k = normalize_whitespace(_r["person_name"])
        if _k and _k not in _seller_role_map_a:
            _seller_role_map_a[_k] = (_r["role_classification"], normalize_unit(_r["base_unit"]))
    # ────────────────────────────────────────────────────────────────────────

    for row in detail_rows:
        issue_dt = parse_datetime_flexible(row["issue_date"])
        net_value = float(row["net_value"] or 0.0)
        if competence_state["isFutureCompetence"]:
            discarded["invalidCompetence"]["rows"] += 1
            discarded["invalidCompetence"]["revenue"] += net_value
            continue
        if competence_state["isCurrentCompetence"] and issue_dt and issue_dt.date() > cutoff_date:
            discarded["invalidCompetence"]["rows"] += 1
            discarded["invalidCompetence"]["revenue"] += net_value
            continue

        raw_detail_rows += 1
        raw_detail_revenue += net_value

        seller_name = normalize_whitespace(row["seller_name"])
        city_name = normalize_upper(row["city_name"])
        resolved_unit = _city_map_a.get(city_name)
        role, seller_base_unit = _seller_role_map_a.get(seller_name, (None, None))
        seller_base_unit = normalize_unit(seller_base_unit)

        if not city_name:
            discarded["cityWithoutMapping"]["rows"] += 1
            discarded["cityWithoutMapping"]["revenue"] += net_value
            missing_city_revenue_map["SEM_CIDADE"] += net_value
        if not resolved_unit:
            discarded["unitWithoutMapping"]["rows"] += 1
            discarded["unitWithoutMapping"]["revenue"] += net_value
            missing_unit_revenue_map[city_name or "SEM_CIDADE"] += net_value
        if role is None:
            discarded["sellerWithoutMapping"]["rows"] += 1
            discarded["sellerWithoutMapping"]["revenue"] += net_value
            missing_seller_revenue_map[seller_name or "SEM_VENDEDOR"] += net_value
        elif role != "Vendedor":
            discarded["nonSellerRole"]["rows"] += 1
            discarded["nonSellerRole"]["revenue"] += net_value

        in_scope = True
        if scoped_filters.get("seller_name") and seller_name != scoped_filters["seller_name"]:
            in_scope = False
        if scoped_filters.get("city_name") and city_name != scoped_filters["city_name"]:
            in_scope = False
        if scoped_units and resolved_unit not in scoped_units:
            in_scope = False
        if scoped_filters.get("unit_name") and resolved_unit != scoped_filters["unit_name"]:
            in_scope = False
        if scoped_units and seller_base_unit and scoped_filters.get("seller_name") and seller_base_unit not in scoped_units:
            in_scope = False

        if not in_scope:
            discarded["userScope"]["rows"] += 1
            discarded["userScope"]["revenue"] += net_value
            continue

        scope_detail_rows += 1
        scope_detail_revenue += net_value
        unit_revenue_map[resolved_unit or "SEM_MAPEAMENTO"] += net_value
        seller_revenue_map[seller_name or "SEM_VENDEDOR"] += net_value

    official_unit_rows = conn.execute(
        """
        SELECT unit_name, SUM(sale_value) AS sale_value, SUM(return_value) AS return_value, SUM(net_value) AS net_value
        FROM fact_unit_summary
        WHERE company_id = ? AND competence = ?
        GROUP BY unit_name
        """,
        (company_id, competence),
    ).fetchall()
    official_vendor_rows = conn.execute(
        """
        SELECT seller_name, SUM(sale_value) AS sale_value, SUM(return_value) AS return_value, SUM(net_value) AS net_value
        FROM fact_vendor_summary
        WHERE company_id = ? AND competence = ?
        GROUP BY seller_name
        """,
        (company_id, competence),
    ).fetchall()
    official_unit_map = {
        normalize_unit(row["unit_name"]) or "SEM_MAPEAMENTO": round(float(row["net_value"] or 0.0), 2)
        for row in official_unit_rows
    }
    official_vendor_map = {
        normalize_whitespace(row["seller_name"]) or "SEM_VENDEDOR": round(float(row["net_value"] or 0.0), 2)
        for row in official_vendor_rows
    }

    missing_units = []
    for unit_name in sorted(set(official_unit_map) | set(unit_revenue_map), key=lambda value: value or ""):
        official_value = round(float(official_unit_map.get(unit_name, 0.0)), 2)
        detail_value = round(float(unit_revenue_map.get(unit_name, 0.0)), 2)
        delta_value = round(official_value - detail_value, 2)
        if abs(delta_value) > 0.01:
            missing_units.append(
                {
                    "unitName": unit_name,
                    "officialRevenue": official_value,
                    "detailRevenue": detail_value,
                    "deltaRevenue": delta_value,
                }
            )

    missing_sellers = []
    for seller_name in sorted(set(official_vendor_map) | set(seller_revenue_map), key=lambda value: value or ""):
        official_value = round(float(official_vendor_map.get(seller_name, 0.0)), 2)
        detail_value = round(float(seller_revenue_map.get(seller_name, 0.0)), 2)
        delta_value = round(official_value - detail_value, 2)
        if abs(delta_value) > 0.01:
            missing_sellers.append(
                {
                    "sellerName": seller_name,
                    "officialRevenue": official_value,
                    "detailRevenue": detail_value,
                    "deltaRevenue": delta_value,
                }
            )

    missing_cities = [
        {"cityName": city_name, "revenue": round(revenue, 2)}
        for city_name, revenue in sorted(missing_city_revenue_map.items(), key=lambda item: item[1], reverse=True)
        if abs(revenue) > 0.01
    ]

    official_unit_revenue = round(sum(official_unit_map.values()), 2)
    official_vendor_revenue = round(sum(official_vendor_map.values()), 2)
    dashboard_revenue = round(float(dashboard["summary"]["revenueNet"] or 0.0), 2)
    unit_revenue_sum = round(sum(float(row["revenueNet"] or 0.0) for row in dashboard["unitPerformance"]), 2)
    seller_revenue_sum = round(sum(float(row["revenueNet"] or 0.0) for row in dashboard["sellerRanking"]), 2)

    return {
        "competence": competence,
        "officialUnitRevenue": official_unit_revenue,
        "officialVendorRevenue": official_vendor_revenue,
        "importedRevenue": round(raw_detail_revenue, 2),
        "detailRevenue": round(raw_detail_revenue, 2),
        "importedRows": raw_detail_rows,
        "dashboardRevenue": dashboard_revenue,
        "unitRevenueSum": unit_revenue_sum,
        "sellerRevenueSum": seller_revenue_sum,
        "discardedRevenue": round(official_unit_revenue - dashboard_revenue, 2),
        "discardedRows": {
            "total": sum(int(item["rows"]) for item in discarded.values()),
            **{key: {"rows": int(value["rows"]), "revenue": round(float(value["revenue"]), 2)} for key, value in discarded.items()},
        },
        "missingUnits": missing_units,
        "missingSellers": missing_sellers,
        "missingCities": missing_cities,
        "sourceGapRevenue": round(official_unit_revenue - raw_detail_revenue, 2),
        "gapUnitVsDetail": round(official_unit_revenue - raw_detail_revenue, 2),
        "gapSellerVsDetail": round(official_vendor_revenue - raw_detail_revenue, 2),
        "gapUnitVsSeller": round(official_unit_revenue - official_vendor_revenue, 2),
        "sourceGapRows": max(raw_detail_rows - scope_detail_rows, 0),
        "scopeRevenue": round(scope_detail_revenue, 2),
        "scopeRows": scope_detail_rows,
        "mappingRevenue": {
            "missingUnitMapping": round(sum(item["revenue"] for item in [discarded["unitWithoutMapping"]]), 2),
            "missingSellerMapping": round(sum(item["revenue"] for item in [discarded["sellerWithoutMapping"]]), 2),
            "missingCityMapping": round(sum(item["revenue"] for item in [discarded["cityWithoutMapping"]]), 2),
            "nonSellerRole": round(sum(item["revenue"] for item in [discarded["nonSellerRole"]]), 2),
        },
        "classification": {
            "executiveSummary": "OK" if audit_same(dashboard_revenue, official_unit_revenue) else ("ERRO" if audit_same(dashboard_revenue, raw_detail_revenue) else "ATENCAO"),
            "sellerSummary": "OK" if audit_same(seller_revenue_sum, official_vendor_revenue) else "ATENCAO",
        },
    }


def audit_revenue_integrity(
    conn: sqlite3.Connection,
    company_id: int,
    competence: str,
    dashboard: dict[str, Any],
    issues: list[dict[str, Any]],
) -> dict[str, Any]:
    revenue_gap = audit_revenue_gap_detail(conn, company_id, competence, dashboard, dashboard.get("filters"))
    summary = dashboard["summary"]
    unit_rows = dashboard["unitPerformance"]
    seller_rows = dashboard["sellerRanking"]
    city_rows = dashboard["cityRanking"]
    client_rows = dashboard["clientRanking"]
    official_unit = conn.execute(
        """
        SELECT
            ROUND(COALESCE(SUM(net_value), 0), 2) AS revenue_net,
            ROUND(COALESCE(SUM(return_value), 0), 2) AS returns_value,
            ROUND(COALESCE(SUM(sale_value), 0), 2) AS gross_sales
        FROM fact_unit_summary
        WHERE company_id = ? AND competence = ?
        """,
        (company_id, competence),
    ).fetchone()
    official_vendor = conn.execute(
        """
        SELECT ROUND(COALESCE(SUM(net_value), 0), 2) AS revenue_net
        FROM fact_vendor_summary
        WHERE company_id = ? AND competence = ?
        """,
        (company_id, competence),
    ).fetchone()
    detail_scope = conn.execute(
        """
        SELECT
            ROUND(COALESCE(SUM(net_value), 0), 2) AS revenue_net,
            ROUND(COALESCE(SUM(return_value), 0), 2) AS returns_value,
            ROUND(COALESCE(SUM(gross_value), 0), 2) AS gross_sales,
            ROUND(COALESCE(SUM(CASE WHEN city_name IS NULL OR city_name = '' THEN net_value ELSE 0 END), 0), 2) AS revenue_without_city
        FROM fact_sales_detail
        WHERE company_id = ? AND competence = ?
        """,
        (company_id, competence),
    ).fetchone()
    summary_revenue = audit_round(summary["revenueNet"])
    unit_sum = audit_round(sum(row["revenueNet"] for row in unit_rows))
    seller_sum = audit_round(sum(row["revenueNet"] for row in seller_rows))
    city_sum = audit_round(sum(row["revenueNet"] for row in city_rows))
    client_sum = audit_round(sum(row["revenueNet"] for row in client_rows))
    official_unit_revenue = audit_round(official_unit["revenue_net"])
    official_vendor_revenue = audit_round(official_vendor["revenue_net"])
    detail_revenue = audit_round(detail_scope["revenue_net"])
    missing_city_revenue = audit_round(detail_scope["revenue_without_city"])
    if not audit_same(revenue_gap["officialUnitRevenue"], revenue_gap["importedRevenue"]):
        append_audit_issue(
            issues,
            "CRITICO",
            "FATURAMENTO",
            "A base detalhada importada não bate com o valor oficial do custo por unidade.",
            revenue_gap["officialUnitRevenue"],
            revenue_gap["importedRevenue"],
        )
    if not audit_same(summary_revenue, unit_sum):
        append_audit_issue(issues, "CRITICO", "FATURAMENTO", "Resumo do grupo não bate com a soma das unidades.", unit_sum, summary_revenue)
    if not audit_same(summary_revenue, official_unit_revenue):
        append_audit_issue(issues, "CRITICO", "FATURAMENTO", "Resumo do grupo não bate com o valor oficial do custo por unidade.", official_unit_revenue, summary_revenue)
    if not audit_same(seller_sum, official_vendor_revenue):
        append_audit_issue(issues, "ATENCAO", "FATURAMENTO", "Soma do ranking de vendedores diverge do valor oficial do custo por vendedor.", official_vendor_revenue, seller_sum)
    expected_city_sum = audit_round(detail_revenue - missing_city_revenue)
    if not audit_same(city_sum, expected_city_sum):
        append_audit_issue(issues, "ATENCAO", "FATURAMENTO", "Soma das cidades diverge do faturamento detalhado esperado para cidades válidas.", expected_city_sum, city_sum)
    if not audit_same(client_sum, detail_revenue):
        append_audit_issue(issues, "ATENCAO", "FATURAMENTO", "Soma do ranking de clientes diverge do faturamento detalhado.", detail_revenue, client_sum)
    filter_samples: dict[str, Any] = {}
    if unit_rows:
        sample_unit = unit_rows[0]["unitName"]
        sample_unit_summary = single_competence_summary(conn, company_id, competence, audit_filters_for_competence(competence, unit_name=sample_unit))
        filter_samples["unit"] = {"unitName": sample_unit, "summaryRevenueNet": sample_unit_summary.get("revenueNet"), "rankingRevenueNet": unit_rows[0]["revenueNet"]}
        if not audit_same(sample_unit_summary.get("revenueNet"), unit_rows[0]["revenueNet"]):
            append_audit_issue(issues, "CRITICO", "FATURAMENTO", "Filtro por unidade não retorna o mesmo faturamento da linha da unidade no ranking.", unit_rows[0]["revenueNet"], sample_unit_summary.get("revenueNet"))
    if seller_rows:
        sample_seller = seller_rows[0]["sellerName"]
        sample_seller_summary = single_competence_summary(conn, company_id, competence, audit_filters_for_competence(competence, seller_name=sample_seller))
        filter_samples["seller"] = {"sellerName": sample_seller, "summaryRevenueNet": sample_seller_summary.get("revenueNet"), "rankingRevenueNet": seller_rows[0]["revenueNet"]}
        if not audit_same(sample_seller_summary.get("revenueNet"), seller_rows[0]["revenueNet"]):
            append_audit_issue(issues, "CRITICO", "FATURAMENTO", "Filtro por vendedor não retorna o mesmo faturamento da linha do vendedor no ranking.", seller_rows[0]["revenueNet"], sample_seller_summary.get("revenueNet"))
    return {
        "summaryRevenueNet": summary_revenue,
        "officialUnitRevenueNet": official_unit_revenue,
        "officialVendorRevenueNet": official_vendor_revenue,
        "detailRevenueNet": detail_revenue,
        "sumUnitsRevenueNet": unit_sum,
        "sumSellersRevenueNet": seller_sum,
        "sumCitiesRevenueNet": city_sum,
        "sumClientsRevenueNet": client_sum,
        "revenueWithoutCity": missing_city_revenue,
        "filterSamples": filter_samples,
        "gapDetail": revenue_gap,
    }


def audit_goals_integrity(
    conn: sqlite3.Connection,
    company_id: int,
    competence: str,
    dashboard: dict[str, Any],
    issues: list[dict[str, Any]],
) -> dict[str, Any]:
    summary_goal = audit_round(dashboard["summary"]["revenueGoal"])
    unit_sum = audit_round(sum(row["revenueGoal"] for row in dashboard["unitPerformance"]))
    seller_sum = audit_round(sum(row["revenueGoal"] for row in dashboard["sellerRanking"]))
    goal_by_seller, duplicate_seller = load_goal_maps(conn, company_id, competence, "goals_seller", "seller_name", normalize_whitespace)
    goal_by_unit, duplicate_unit = load_goal_maps(conn, company_id, competence, "goals_unit", "unit_name", normalize_unit)
    duplicate_unit_normalized = normalized_goal_duplicates(conn, company_id, "goals_unit", "unit_name", normalize_unit)
    duplicate_seller_normalized = normalized_goal_duplicates(conn, company_id, "goals_seller", "seller_name", normalize_whitespace)
    official_unit_goal = audit_round(sum(item["revenueGoal"] for item in goal_by_unit.values()))
    official_seller_goal = audit_round(sum(item["revenueGoal"] for item in goal_by_seller.values()))
    if not audit_same(summary_goal, official_unit_goal):
        append_audit_issue(issues, "CRITICO", "META", "Meta do grupo não bate com a soma das metas das unidades.", official_unit_goal, summary_goal)
    if not audit_same(summary_goal, unit_sum):
        append_audit_issue(issues, "CRITICO", "META", "Resumo da meta do grupo não bate com a soma das metas exibidas por unidade.", unit_sum, summary_goal)
    if duplicate_unit:
        append_audit_issue(issues, "ATENCAO", "META", "Foram encontradas metas duplicadas de unidade na competência.", "Sem duplicidades", duplicate_unit)
    if duplicate_seller:
        append_audit_issue(issues, "ATENCAO", "META", "Foram encontradas metas duplicadas de vendedor na competência.", "Sem duplicidades", duplicate_seller)
    for duplicate in duplicate_unit_normalized:
        append_audit_issue(
            issues,
            "CRITICO" if duplicate["competence"] == competence else "ATENCAO",
            "META",
            "Foram encontradas metas duplicadas por unidade normalizada.",
            "Uma meta por unidade normalizada",
            duplicate,
        )
    for duplicate in duplicate_seller_normalized:
        append_audit_issue(
            issues,
            "CRITICO" if duplicate["competence"] == competence else "ATENCAO",
            "META",
            "Foram encontradas metas duplicadas por vendedor normalizado.",
            "Uma meta por vendedor normalizado",
            duplicate,
        )
    sample_checks: dict[str, Any] = {}
    if dashboard["unitPerformance"]:
        sample_unit = dashboard["unitPerformance"][0]
        expected = audit_round(goal_by_unit.get(normalize_unit(sample_unit["unitName"]), {}).get("revenueGoal"))
        actual = audit_round(sample_unit["revenueGoal"])
        sample_checks["unit"] = {"unitName": sample_unit["unitName"], "expectedGoal": expected, "actualGoal": actual}
        if not audit_same(expected, actual):
            append_audit_issue(issues, "CRITICO", "META", "Meta exibida na unidade diverge da meta cadastrada.", expected, actual)
    if dashboard["sellerRanking"]:
        sample_seller = dashboard["sellerRanking"][0]
        expected = audit_round(goal_by_seller.get(normalize_whitespace(sample_seller["sellerName"]), {}).get("revenueGoal"))
        actual = audit_round(sample_seller["revenueGoal"])
        sample_checks["seller"] = {"sellerName": sample_seller["sellerName"], "expectedGoal": expected, "actualGoal": actual}
        if not audit_same(expected, actual):
            append_audit_issue(issues, "CRITICO", "META", "Meta exibida no vendedor diverge da meta cadastrada.", expected, actual)
    return {
        "summaryRevenueGoal": summary_goal,
        "officialUnitRevenueGoal": official_unit_goal,
        "dashboardUnitGoalsSum": unit_sum,
        "officialSellerGoalsSum": official_seller_goal,
        "dashboardSellerGoalsSum": seller_sum,
        "duplicateUnitGoals": duplicate_unit,
        "duplicateSellerGoals": duplicate_seller,
        "duplicateUnitGoalsNormalized": [
            {
                "competence": item["competence"],
                "normalizedUnit": item["normalizedKey"],
                "rows": [
                    {
                        "id": row["id"],
                        "unitName": row["goalKey"],
                        "revenueGoal": row["revenueGoal"],
                    }
                    for row in item["rows"]
                ],
                "recommendation": "Manter unidade normalizada e excluir duplicadas",
            }
            for item in duplicate_unit_normalized
        ],
        "duplicateSellerGoalsNormalized": [
            {
                "competence": item["competence"],
                "normalizedSeller": item["normalizedKey"],
                "rows": [
                    {
                        "id": row["id"],
                        "sellerName": row["goalKey"],
                        "revenueGoal": row["revenueGoal"],
                    }
                    for row in item["rows"]
                ],
            }
            for item in duplicate_seller_normalized
        ],
        "sampleChecks": sample_checks,
    }


def audit_projection_integrity(
    conn: sqlite3.Connection,
    company_id: int,
    competence: str,
    dashboard: dict[str, Any],
    issues: list[dict[str, Any]],
) -> dict[str, Any]:
    summary = dashboard["summary"]
    calendar = dashboard["calendar"]
    debug_projection = dashboard["debugProjection"]
    competence_state = dashboard_competence_state(competence)
    expected_daily = audit_round(safe_div(summary["revenueNet"], calendar["elapsedWorkingDays"]))
    expected_projected = audit_round(expected_daily * calendar["totalWorkingDays"]) if calendar["elapsedWorkingDays"] and calendar["totalWorkingDays"] else 0.0
    expected_daily_goal = audit_round(safe_div(summary["revenueGoal"], calendar["totalWorkingDays"]))
    expected_goal_attainment = audit_round(safe_div(summary["revenueNet"], summary["revenueGoal"]) * 100 if summary["revenueGoal"] else 0.0)
    expected_projected_goal_attainment = audit_round(safe_div(expected_projected, summary["revenueGoal"]) * 100 if summary["revenueGoal"] else 0.0)
    expected_cutoff = dashboard_cutoff_date(competence_state["today"]).isoformat()
    if debug_projection.get("cutoffDate") != expected_cutoff:
        append_audit_issue(issues, "CRITICO", "PROJECAO", "Cutoff D-1 está incorreto.", expected_cutoff, debug_projection.get("cutoffDate"))
    if competence_state["isCurrentCompetence"] and calendar["effectiveToday"] != expected_cutoff:
        append_audit_issue(issues, "CRITICO", "PROJECAO", "Calendário da competência atual está incluindo o dia atual.", expected_cutoff, calendar["effectiveToday"])
    if competence_state["isPastCompetence"] and calendar["elapsedWorkingDays"] != calendar["totalWorkingDays"]:
        append_audit_issue(issues, "CRITICO", "PROJECAO", "Competência passada não está fechando com mês completo.", calendar["totalWorkingDays"], calendar["elapsedWorkingDays"])
    future_competence = shift_competence(competence, 1)
    future_summary = single_competence_summary(conn, company_id, future_competence, audit_filters_for_competence(future_competence))
    if future_summary and audit_round(future_summary.get("revenueNet")) == 0.0 and audit_round(future_summary.get("dailyRevenue")) != 0.0:
        append_audit_issue(issues, "ATENCAO", "PROJECAO", "Competência futura tem média diária diferente de zero.", 0.0, future_summary.get("dailyRevenue"))
    for label, expected, actual in [
        ("dailyRevenueActual", expected_daily, summary["dailyRevenueActual"]),
        ("dailyGoal", expected_daily_goal, summary["dailyGoal"]),
        ("projectedRevenue", expected_projected, summary["projectedRevenue"]),
        ("goalAttainmentPct", expected_goal_attainment, summary["goalAttainmentPct"]),
        ("projectedGoalAttainmentPct", expected_projected_goal_attainment, summary["projectedGoalAttainmentPct"]),
    ]:
        if not audit_same(expected, actual):
            append_audit_issue(issues, "CRITICO", "PROJECAO", f"Cálculo de {label} divergente.", expected, actual)
    return {
        "calendar": calendar,
        "cutoffDate": debug_projection.get("cutoffDate"),
        "expectedCutoffDate": expected_cutoff,
        "dailyRevenueActual": {"expected": expected_daily, "actual": audit_round(summary["dailyRevenueActual"])},
        "dailyGoal": {"expected": expected_daily_goal, "actual": audit_round(summary["dailyGoal"])},
        "projectedRevenue": {"expected": expected_projected, "actual": audit_round(summary["projectedRevenue"])},
        "goalAttainmentPct": {"expected": expected_goal_attainment, "actual": audit_round(summary["goalAttainmentPct"])},
        "projectedGoalAttainmentPct": {"expected": expected_projected_goal_attainment, "actual": audit_round(summary["projectedGoalAttainmentPct"])},
        "futureCompetenceCheck": {"competence": future_competence, "dailyRevenue": future_summary.get("dailyRevenue") if future_summary else None},
    }


def audit_comparisons_integrity(
    conn: sqlite3.Connection,
    company_id: int,
    competence: str,
    dashboard: dict[str, Any],
    issues: list[dict[str, Any]],
) -> dict[str, Any]:
    previous = dashboard["comparisons"]["previousCompetence"]
    yoy = dashboard["comparisons"]["yearOverYear"]
    previous_expected = shift_competence(competence, -1)
    yoy_expected = shift_competence(competence, -12)
    if previous.get("competence") and previous.get("competence") != previous_expected:
        append_audit_issue(issues, "CRITICO", "COMPARATIVO", "Comparativo do mês anterior está apontando competência incorreta.", previous_expected, previous.get("competence"))
    if yoy.get("competence") and yoy.get("competence") != yoy_expected:
        append_audit_issue(issues, "CRITICO", "COMPARATIVO", "Comparativo ano contra ano está apontando competência incorreta.", yoy_expected, yoy.get("competence"))
    scope_samples: dict[str, Any] = {}
    if dashboard["unitPerformance"]:
        sample_unit = dashboard["unitPerformance"][0]["unitName"]
        sample_previous = single_competence_summary(conn, company_id, previous_expected, audit_filters_for_competence(previous_expected, unit_name=sample_unit))
        sample_yoy = single_competence_summary(conn, company_id, yoy_expected, audit_filters_for_competence(yoy_expected, unit_name=sample_unit))
        scope_samples["unit"] = {"unitName": sample_unit, "previous": sample_previous, "yearOverYear": sample_yoy}
        if sample_previous.get("unit") != sample_unit or sample_yoy.get("unit") != sample_unit:
            append_audit_issue(issues, "CRITICO", "COMPARATIVO", "Comparativos filtrados por unidade não mantêm o mesmo escopo.", sample_unit, {"previous": sample_previous.get("unit"), "yearOverYear": sample_yoy.get("unit")})
    if dashboard["sellerRanking"]:
        sample_seller = dashboard["sellerRanking"][0]["sellerName"]
        sample_previous = single_competence_summary(conn, company_id, previous_expected, audit_filters_for_competence(previous_expected, seller_name=sample_seller))
        sample_yoy = single_competence_summary(conn, company_id, yoy_expected, audit_filters_for_competence(yoy_expected, seller_name=sample_seller))
        scope_samples["seller"] = {"sellerName": sample_seller, "previous": sample_previous, "yearOverYear": sample_yoy}
        if sample_previous.get("seller") != sample_seller or sample_yoy.get("seller") != sample_seller:
            append_audit_issue(issues, "CRITICO", "COMPARATIVO", "Comparativos filtrados por vendedor não mantêm o mesmo escopo.", sample_seller, {"previous": sample_previous.get("seller"), "yearOverYear": sample_yoy.get("seller")})
    return {
        "group": {"current": competence, "previousExpected": previous_expected, "yearOverYearExpected": yoy_expected, "previousActual": previous, "yearOverYearActual": yoy},
        "scopeSamples": scope_samples,
    }


def audit_crm_integrity(
    conn: sqlite3.Connection,
    company_id: int,
    competence: str,
    issues: list[dict[str, Any]],
) -> dict[str, Any]:
    filters = audit_filters_for_competence(competence)
    all_rows = list_crm_clients(conn, company_id, filters, attach_context=False)
    base_count = len(all_rows)
    filtered_base = filter_crm_client_rows(all_rows, filters)
    page_50_rows_raw = filtered_base[:50]
    page_100_rows_raw = filtered_base[:100]
    page_50_rows = crm_attach_context(conn, company_id, page_50_rows_raw)
    page_100_rows = crm_attach_context(conn, company_id, page_100_rows_raw)
    page_50 = {
        "total": len(filtered_base),
        "page": 1,
        "pageSize": 50,
        "totalPages": max(math.ceil(len(filtered_base) / 50), 1) if filtered_base else 1,
        "rows": page_50_rows,
    }
    page_100 = {
        "total": len(filtered_base),
        "page": 1,
        "pageSize": 100,
        "totalPages": max(math.ceil(len(filtered_base) / 100), 1) if filtered_base else 1,
        "rows": page_100_rows,
    }
    first_row = page_50_rows[0] if page_50_rows else None
    sample_status = first_row["statusCode"] if first_row else None
    sample_class = normalize_upper(first_row["classCode"]) if first_row else None
    status_page_total = len(filter_crm_client_rows(all_rows, {**filters, "status": sample_status})) if sample_status else 0
    class_page_total = len(filter_crm_client_rows(all_rows, {**filters, "classCode": sample_class})) if sample_class else 0
    purchase_with_total = len(filter_crm_client_rows(all_rows, {**filters, "purchaseMonth": "COM_COMPRA"}))
    purchase_without_total = len(filter_crm_client_rows(all_rows, {**filters, "purchaseMonth": "SEM_COMPRA"}))
    growth_above_total = len(filter_crm_client_rows(all_rows, {**filters, "growth": "ACIMA"}))
    growth_stable_total = len(filter_crm_client_rows(all_rows, {**filters, "growth": "ESTAVEL"}))
    growth_below_total = len(filter_crm_client_rows(all_rows, {**filters, "growth": "ABAIXO"}))
    profile_count = int(conn.execute("SELECT COUNT(*) AS total FROM crm_client_profiles WHERE company_id = ?", (company_id,)).fetchone()["total"] or 0)
    summary_distinct_count = int(
        conn.execute(
            "SELECT COUNT(DISTINCT client_code) AS total FROM crm_client_summary WHERE company_id = ? AND competence = ?",
            (company_id, competence),
        ).fetchone()["total"]
        or 0
    )
    detail_checks: dict[str, Any] = {}
    expected_pages_50 = max(math.ceil(base_count / 50), 1) if base_count else 1
    expected_pages_100 = max(math.ceil(base_count / 100), 1) if base_count else 1
    if page_50["total"] != base_count:
        append_audit_issue(issues, "CRITICO", "CRM", "Total do CRM Clientes diverge da base real.", base_count, page_50["total"])
    if page_50["totalPages"] != expected_pages_50:
        append_audit_issue(issues, "CRITICO", "CRM", "Paginação do CRM Clientes com pageSize 50 está incorreta.", expected_pages_50, page_50["totalPages"])
    if page_100["totalPages"] != expected_pages_100:
        append_audit_issue(issues, "CRITICO", "CRM", "Paginação do CRM Clientes com pageSize 100 está incorreta.", expected_pages_100, page_100["totalPages"])
    search_sample_total = 0
    if first_row:
        search_sample_total = len(filter_crm_client_rows(all_rows, {**filters, "search": first_row["clientKey"]}))
        summary_data = get_crm_client_summary(conn, company_id, filters, first_row["clientKey"])
        purchases_data = get_crm_client_purchases(conn, company_id, filters, first_row["clientKey"])
        items_data = get_crm_client_items(conn, company_id, filters, first_row["clientKey"], 1, 20)
        interactions_data = get_crm_client_interactions(conn, company_id, filters, first_row["clientKey"], 1, 20)
        tasks_data = get_crm_client_tasks(conn, company_id, filters, first_row["clientKey"])
        detail_checks = {
            "clientKey": first_row["clientKey"],
            "summaryFound": summary_data is not None,
            "purchasesFound": purchases_data is not None,
            "itemsFound": items_data is not None,
            "interactionsFound": interactions_data is not None,
            "tasksFound": tasks_data is not None,
            "searchRows": search_sample_total,
        }
        if not summary_data:
            append_audit_issue(issues, "CRITICO", "CRM", "Ficha 360 não encontrou o cliente de teste no summary.", True, False)
        if items_data is None:
            append_audit_issue(issues, "CRITICO", "CRM", "Ficha 360 não encontrou itens do cliente de teste.", "rows ou lista vazia", None)
        if interactions_data is None:
            append_audit_issue(issues, "CRITICO", "CRM", "Ficha 360 não encontrou interações do cliente de teste.", "rows ou lista vazia", None)
        if search_sample_total <= 0:
            append_audit_issue(issues, "ATENCAO", "CRM", "Busca por clientKey não retornou o cliente de teste.", first_row["clientKey"], 0)
    return {
        "crmClientProfiles": profile_count,
        "crmClientSummaryDistinct": summary_distinct_count,
        "baseCount": int(base_count or 0),
        "page50": {"total": page_50["total"], "page": page_50["page"], "pageSize": page_50["pageSize"], "totalPages": page_50["totalPages"], "rowsReturned": len(page_50["rows"])},
        "page100": {"total": page_100["total"], "page": page_100["page"], "pageSize": page_100["pageSize"], "totalPages": page_100["totalPages"], "rowsReturned": len(page_100["rows"])},
        "filters": {
            "status": {"value": sample_status, "total": status_page_total},
            "purchaseWith": {"total": purchase_with_total},
            "purchaseWithout": {"total": purchase_without_total},
            "growthAbove": {"total": growth_above_total},
            "growthStable": {"total": growth_stable_total},
            "growthBelow": {"total": growth_below_total},
            "classCode": {"value": sample_class, "total": class_page_total},
            "search": {"query": first_row["clientKey"] if first_row else None, "total": search_sample_total},
        },
        "detailChecks": detail_checks,
    }


def audit_permissions_integrity(
    conn: sqlite3.Connection,
    company_id: int,
    competence: str,
    issues: list[dict[str, Any]],
) -> dict[str, Any]:
    all_users = [dict(row) for row in conn.execute("SELECT * FROM users WHERE company_id = ? AND is_active = 1 ORDER BY id", (company_id,)).fetchall()]
    users: list[dict[str, Any]] = []
    seen_roles: set[str] = set()
    for user in all_users:
        role = user["role"]
        if role in seen_roles:
            continue
        users.append(user)
        seen_roles.add(role)
    checks: list[dict[str, Any]] = []
    for user in users:
        scoped = scoped_filters_for_user(conn, company_id, user, audit_filters_for_competence(competence))
        if user["role"] == "Vendedor":
            expected_seller = seller_identity_for_user(user)
            if scoped.get("seller_name") != expected_seller:
                append_audit_issue(issues, "CRITICO", "PERMISSAO", "Escopo do vendedor não foi travado no vendedor vinculado.", expected_seller, scoped.get("seller_name"))
            allowed_units = []
        elif user["role"] in {"Gerente", "Analista"}:
            expected_units = linked_units_for_user(user)
            allowed_units = normalize_unit_list(scoped.get("allowed_units"))
            if allowed_units != expected_units:
                append_audit_issue(issues, "CRITICO", "PERMISSAO", "Escopo do gerente/analista não corresponde às unidades vinculadas.", expected_units, allowed_units)
        else:
            allowed_units = []
        dashboard = get_dashboard_data(conn, company_id, scoped)
        visible_units = sorted({normalize_unit(row["unitName"]) for row in dashboard["unitPerformance"]})
        if user["role"] in {"Gerente", "Analista"} and allowed_units:
            unauthorized = [unit for unit in visible_units if unit not in allowed_units]
            if unauthorized:
                append_audit_issue(issues, "CRITICO", "PERMISSAO", "Usuário de unidade está vendo unidades fora do vínculo.", allowed_units, unauthorized)
        if user["role"] == "Vendedor":
            expected_seller = seller_identity_for_user(user)
            visible_sellers = {normalize_whitespace(row["sellerName"]) for row in dashboard["sellerRanking"]}
            if visible_sellers and visible_sellers != {expected_seller}:
                append_audit_issue(issues, "CRITICO", "PERMISSAO", "Vendedor está vendo ranking fora do próprio escopo.", [expected_seller], sorted(visible_sellers))
        checks.append(
            {
                "username": user["username"],
                "role": user["role"],
                "linkedPersonName": user.get("linked_person_name"),
                "linkedUnits": linked_units_for_user(user),
                "scopedFilters": {
                    "unit": scoped.get("unit_name"),
                    "seller": scoped.get("seller_name"),
                    "city": scoped.get("city_name"),
                    "allowedUnits": normalize_unit_list(scoped.get("allowed_units")),
                },
                "visibleUnits": visible_units,
                "sellerCount": len(dashboard["sellerRanking"]),
            }
        )
    return {"users": checks}


def build_integrity_audit(conn: sqlite3.Connection, company_id: int, competence: str) -> dict[str, Any]:
    issues: list[dict[str, Any]] = []
    dashboard = get_dashboard_data(conn, company_id, audit_filters_for_competence(competence))
    imports_check = summarize_imports_for_competence(conn, company_id, competence)
    revenue_check = audit_revenue_integrity(conn, company_id, competence, dashboard, issues)
    goals_check = audit_goals_integrity(conn, company_id, competence, dashboard, issues)
    projection_check = audit_projection_integrity(conn, company_id, competence, dashboard, issues)
    comparisons_check = audit_comparisons_integrity(conn, company_id, competence, dashboard, issues)
    crm_check = audit_crm_integrity(conn, company_id, competence, issues)
    permission_check = audit_permissions_integrity(conn, company_id, competence, issues)
    return {
        "competence": competence,
        "revenueSourcePolicy": {
            "executiveSummary": "fact_unit_summary",
            "unitPerformance": "fact_unit_summary",
            "sellerRanking": "fact_vendor_summary",
            "cityRanking": "fact_sales_detail",
            "clientRanking": "fact_sales_detail",
            "crm": "crm_client_summary + fact_sales_detail",
        },
        "imports": imports_check,
        "revenueCheck": revenue_check,
        "revenueGapReport": revenue_check.get("gapDetail", {}),
        "goalsCheck": goals_check,
        "projectionCheck": projection_check,
        "comparisonsCheck": comparisons_check,
        "crmCheck": crm_check,
        "permissionCheck": permission_check,
        "issues": issues,
    }


def filter_admin_data_for_user(
    conn: sqlite3.Connection, company_id: int, user: sqlite3.Row, data: dict[str, Any]
) -> dict[str, Any]:
    """Aplica o recorte por unidade nos cadastros administrativos.

    Um gerente só administra a própria unidade: metas de vendedor da equipe dele,
    meta da unidade dele e férias das pessoas da unidade dele. Quem tem escopo
    "todos" não sofre restrição.
    """
    scope = data_scope_for_user(conn, user)
    if scope not in {"unidade", "unidade_consolidado"}:
        return data
    allowed = set(linked_units_for_user(user))
    if not allowed:
        for key in ("goalsSeller", "goalsUnit", "vacations", "people"):
            data[key] = []
        return data

    # Mapa pessoa -> unidade base, para filtrar férias e metas sem base_unit gravada
    person_unit: dict[str, str] = {}
    for r in conn.execute(
        "SELECT person_name, base_unit FROM people_records WHERE company_id = ? ORDER BY valid_from DESC",
        (company_id,),
    ).fetchall():
        key = normalize_whitespace(r["person_name"])
        if key and key not in person_unit:
            person_unit[key] = normalize_unit(r["base_unit"])

    def unit_of_person(name: str | None) -> str:
        return person_unit.get(normalize_whitespace(name), "")

    data["goalsSeller"] = [
        g for g in data.get("goalsSeller", [])
        if (normalize_unit(g.get("base_unit")) or unit_of_person(g.get("seller_name"))) in allowed
    ]
    data["goalsUnit"] = [
        g for g in data.get("goalsUnit", []) if normalize_unit(g.get("unit_name")) in allowed
    ]
    data["vacations"] = [
        v for v in data.get("vacations", []) if unit_of_person(v.get("person_name")) in allowed
    ]
    data["people"] = [
        p for p in data.get("people", []) if normalize_unit(p.get("base_unit")) in allowed
    ]
    # Configuração de score é exclusiva de quem administra o sistema
    data["scoreConfigs"] = []
    return data


def list_admin_data(conn: sqlite3.Connection, company_id: int) -> dict[str, Any]:
    sanitize_unit_goals(conn, company_id)
    conn.commit()
    users: list[dict[str, Any]] = []
    for row in conn.execute(
        """
        SELECT id, username, full_name, linked_person_name, linked_units_json, role, is_active, created_at
        FROM users
        WHERE company_id = ?
        ORDER BY username
        """,
        (company_id,),
    ).fetchall():
        item = dict(row)
        linked_units = normalize_unit_list(item.get("linked_units_json"))
        item["linked_units"] = linked_units
        item["linked_units_display"] = ", ".join(linked_units)
        users.append(item)
    profiles = list_access_profiles(conn, company_id)
    profile_name_by_id = {p["id"]: p["name"] for p in profiles}
    for item in users:
        item["profile_name"] = profile_name_by_id.get(item.get("profile_id")) or item.get("role") or ""
    return {
        "users": users,
        "profiles": profiles,
        "accessModules": ACCESS_MODULES,
        "dataScopes": DATA_SCOPES,
        "clients": [dict(row) for row in conn.execute("SELECT * FROM client_registry WHERE company_id = ? ORDER BY updated_at DESC, client_name LIMIT 300", (company_id,)).fetchall()],
        "people": [dict(row) for row in conn.execute("SELECT * FROM people_records WHERE company_id = ? ORDER BY person_name, valid_from DESC", (company_id,)).fetchall()],
        "salesSellers": [row["seller_name"] for row in conn.execute("SELECT DISTINCT seller_name FROM fact_sales_detail WHERE company_id = ? AND seller_name IS NOT NULL AND TRIM(seller_name) <> '' ORDER BY seller_name", (company_id,)).fetchall()],
        "salesCities": [row["city_name"] for row in conn.execute("SELECT DISTINCT city_name FROM fact_sales_detail WHERE company_id = ? AND city_name IS NOT NULL AND TRIM(city_name) <> '' ORDER BY city_name", (company_id,)).fetchall()],
        "salesCoverage": dict(zip(("min", "max", "total"), conn.execute("SELECT MIN(issue_date), MAX(issue_date), COUNT(*) FROM fact_sales_detail WHERE company_id = ? AND issue_date IS NOT NULL AND TRIM(issue_date) <> ''", (company_id,)).fetchone())),
        "cityMappings": [dict(row) for row in conn.execute("SELECT * FROM city_mappings WHERE company_id = ? ORDER BY city_name, valid_from DESC", (company_id,)).fetchall()],
        "vacations": [dict(row) for row in conn.execute("SELECT * FROM vacations WHERE company_id = ? ORDER BY start_date DESC", (company_id,)).fetchall()],
        "holidays": [dict(row) for row in conn.execute("SELECT * FROM holidays WHERE company_id = ? ORDER BY holiday_date DESC", (company_id,)).fetchall()],
        "goalsSeller": [dict(row) for row in conn.execute("SELECT * FROM goals_seller WHERE company_id = ? ORDER BY competence DESC, seller_name ASC", (company_id,)).fetchall()],
        "goalsUnit": [dict(row) for row in conn.execute("SELECT * FROM goals_unit WHERE company_id = ? ORDER BY competence DESC, unit_name ASC", (company_id,)).fetchall()],
        "issues": [dict(row) for row in conn.execute("SELECT * FROM import_issues WHERE company_id = ? ORDER BY created_at DESC LIMIT 200", (company_id,)).fetchall()],
        "imports": [dict(row) for row in conn.execute("SELECT * FROM imports WHERE company_id = ? ORDER BY imported_at DESC LIMIT 100", (company_id,)).fetchall()],
        "audit": [dict(row) for row in conn.execute("SELECT * FROM audit_logs WHERE company_id = ? ORDER BY created_at DESC LIMIT 200", (company_id,)).fetchall()],
        "scoreConfigs": [dict(row) for row in conn.execute("SELECT * FROM score_configs WHERE company_id = ? ORDER BY valid_from_competence DESC", (company_id,)).fetchall()],
        "salesDetailSummary": [
            dict(row) for row in conn.execute(
                """
                SELECT competence,
                       MAX(issue_date) AS last_issue_date,
                       COUNT(*) AS row_count
                FROM fact_sales_detail
                WHERE company_id = ?
                GROUP BY competence
                ORDER BY competence DESC
                LIMIT 6
                """,
                (company_id,),
            ).fetchall()
        ],
    }


def resolve_import_issue(conn: sqlite3.Connection, company_id: int, user_id: int, payload: dict[str, Any]) -> dict[str, Any]:
    issue_id = int(payload.get("issueId") or 0)
    action = normalize_whitespace(payload.get("action")).lower() or "resolve"
    issue = conn.execute("SELECT * FROM import_issues WHERE id = ? AND company_id = ?", (issue_id, company_id)).fetchone()
    if not issue:
        raise ValueError("Pendência não encontrada")
    issue = dict(issue)
    if issue["status"] != "pendente":
        raise ValueError("Essa pendência já foi tratada")

    updates = {
        "resolvedBy": user_id,
        "resolvedAt": now_iso(),
        "action": action,
    }

    if action == "ignore":
        new_status = "ignorada"
    elif issue["issue_type"] == "vendedor_sem_vinculo":
        person_name = normalize_whitespace(payload.get("person_name") or issue["reference_value"])
        role_classification = normalize_whitespace(payload.get("role_classification") or "Vendedor") or "Vendedor"
        base_unit = normalize_unit(payload.get("base_unit"))
        valid_from = payload.get("valid_from") or first_day_of_competence(issue["competence"]).isoformat()
        valid_to = payload.get("valid_to")
        if not person_name or not base_unit:
            raise ValueError("Informe nome e unidade base para resolver o vendedor")
        conn.execute(
            """
            INSERT OR REPLACE INTO people_records
                (company_id, person_name, role_classification, base_unit, valid_from, valid_to, source, is_active, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (company_id, person_name, role_classification, base_unit, valid_from, valid_to, "resolucao_pendencia", 1, now_iso()),
        )
        updates.update({"person_name": person_name, "role_classification": role_classification, "base_unit": base_unit, "valid_from": valid_from})
        new_status = "resolvida"
    elif issue["issue_type"] == "cidade_sem_correspondencia":
        city_name = normalize_upper(payload.get("city_name") or issue["reference_value"])
        principal_unit = normalize_unit(payload.get("principal_unit"))
        valid_from = payload.get("valid_from") or first_day_of_competence(issue["competence"]).isoformat()
        valid_to = payload.get("valid_to")
        if not city_name or not principal_unit:
            raise ValueError("Informe cidade e unidade principal para resolver a cidade")
        conn.execute(
            """
            INSERT OR REPLACE INTO city_mappings
                (company_id, city_name, principal_unit, state_name, country_name, valid_from, valid_to, source, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (company_id, city_name, principal_unit, payload.get("state_name"), payload.get("country_name"), valid_from, valid_to, "resolucao_pendencia", now_iso()),
        )
        updates.update({"city_name": city_name, "principal_unit": principal_unit, "valid_from": valid_from})
        new_status = "resolvida"
    else:
        raise ValueError("Tipo de pendência ainda não suportado")

    conn.execute(
        """
        UPDATE import_issues
        SET status = ?, details_json = ?
        WHERE company_id = ? AND issue_type = ? AND reference_value = ? AND status = 'pendente'
        """,
        (
            new_status,
            json.dumps(updates, ensure_ascii=False),
            company_id,
            issue["issue_type"],
            issue["reference_value"],
        ),
    )
    audit_log(conn, company_id, user_id, "resolver_pendencia", "import_issue", str(issue_id), updates | {"status": new_status})
    conn.commit()
    return {"issueId": issue_id, "status": new_status, "issueType": issue["issue_type"], "referenceValue": issue["reference_value"]}


def save_json_payload(conn: sqlite3.Connection, company_id: int, user_id: int, table_name: str, rows: list[dict[str, Any]]) -> int:
    created = 0
    if table_name == "people_records":
        for row in rows:
            conn.execute(
                """
                INSERT OR REPLACE INTO people_records
                    (company_id, person_name, role_classification, base_unit, valid_from, valid_to, source, is_active, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    company_id,
                    normalize_whitespace(row["person_name"]),
                    row["role_classification"],
                    normalize_unit(row.get("base_unit")),
                    row["valid_from"],
                    row.get("valid_to"),
                    row.get("source", "manual"),
                    1 if row.get("is_active", True) else 0,
                    now_iso(),
                ),
            )
            created += 1
    elif table_name == "vacations":
        for row in rows:
            _sd = parse_datetime_flexible(row.get("start_date"))
            _ed = parse_datetime_flexible(row.get("end_date"))
            conn.execute(
                """
                INSERT OR REPLACE INTO vacations
                    (company_id, person_name, start_date, end_date, notes, created_at)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    company_id,
                    normalize_whitespace(row["person_name"]),
                    _sd.strftime("%Y-%m-%d") if _sd else (row.get("start_date") or ""),
                    _ed.strftime("%Y-%m-%d") if _ed else (row.get("end_date") or ""),
                    row.get("notes"),
                    now_iso(),
                ),
            )
            created += 1
    elif table_name == "holidays":
        for row in rows:
            conn.execute(
                """
                INSERT OR REPLACE INTO holidays
                    (company_id, holiday_date, holiday_name, scope, created_at)
                VALUES (?, ?, ?, ?, ?)
                """,
                (company_id, row["holiday_date"], row["holiday_name"], row.get("scope", "NACIONAL_RS"), now_iso()),
            )
            created += 1
    elif table_name == "goals_seller":
        for row in rows:
            seller_name = normalize_whitespace(row["seller_name"])
            conn.execute(
                """
                INSERT INTO goals_seller
                    (company_id, competence, seller_name, base_unit, revenue_goal, returns_goal, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(company_id, competence, seller_name)
                DO UPDATE SET
                    base_unit = excluded.base_unit,
                    revenue_goal = excluded.revenue_goal,
                    returns_goal = excluded.returns_goal,
                    created_at = excluded.created_at
                """,
                (
                    company_id,
                    row["competence"],
                    seller_name,
                    normalize_unit(row.get("base_unit")),
                    float(row.get("revenue_goal") or 0),
                    float(row.get("returns_goal") or 0),
                    now_iso(),
                ),
            )
            created += 1
    elif table_name == "goals_unit":
        for row in rows:
            normalized_unit = normalize_unit(row["unit_name"])
            conn.execute(
                """
                INSERT INTO goals_unit
                    (company_id, competence, unit_name, revenue_goal, returns_goal, created_at)
                VALUES (?, ?, ?, ?, ?, ?)
                ON CONFLICT(company_id, competence, unit_name)
                DO UPDATE SET
                    revenue_goal = excluded.revenue_goal,
                    returns_goal = excluded.returns_goal,
                    created_at = excluded.created_at
                """,
                (
                    company_id,
                    row["competence"],
                    normalized_unit,
                    float(row.get("revenue_goal") or 0),
                    float(row.get("returns_goal") or 0),
                    now_iso(),
                ),
            )
            created += 1
    elif table_name == "score_configs":
        for row in rows:
            conn.execute(
                """
                INSERT OR REPLACE INTO score_configs
                    (company_id, valid_from_competence, valid_to_competence, weight_goal, weight_ticket, weight_clients, weight_mix, weight_returns, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    company_id,
                    row["valid_from_competence"],
                    row.get("valid_to_competence"),
                    float(row["weight_goal"]),
                    float(row["weight_ticket"]),
                    float(row["weight_clients"]),
                    float(row["weight_mix"]),
                    float(row["weight_returns"]),
                    now_iso(),
                ),
            )
            created += 1
    elif table_name == "users":
        for row in rows:
            username = normalize_whitespace(row.get("username")).lower()
            if not username:
                continue
            linked_units = normalize_unit_list(row.get("linked_units") or row.get("linked_units_json") or row.get("linked_units_csv"))
            password = row.get("password")
            existing = None
            row_id = row.get("id")
            if row_id:
                existing = conn.execute("SELECT * FROM users WHERE company_id = ? AND id = ?", (company_id, int(row_id))).fetchone()
            if not existing:
                existing = conn.execute("SELECT * FROM users WHERE company_id = ? AND username = ?", (company_id, username)).fetchone()
            duplicate = conn.execute("SELECT id FROM users WHERE company_id = ? AND username = ?", (company_id, username)).fetchone()
            if duplicate and (not existing or duplicate["id"] != existing["id"]):
                raise ValueError(f"Já existe um usuário cadastrado com o login {username}")
            if existing:
                pwd_hash = existing["password_hash"]
                salt = existing["password_salt"]
                if password:
                    pwd_hash, salt = pbkdf2_hash(str(password))
                conn.execute(
                    """
                    UPDATE users
                    SET username = ?, full_name = ?, linked_person_name = ?, linked_units_json = ?, role = ?, is_active = ?, password_hash = ?, password_salt = ?
                    WHERE company_id = ? AND id = ?
                    """,
                    (
                        username,
                        normalize_whitespace(row.get("full_name")),
                        normalize_whitespace(row.get("linked_person_name")),
                        json.dumps(linked_units, ensure_ascii=False),
                        row["role"],
                        1 if row.get("is_active", True) not in {False, "0", 0, "false", "False"} else 0,
                        pwd_hash,
                        salt,
                        company_id,
                        existing["id"],
                    ),
                )
                created += 1
                continue
            if not password:
                continue
            pwd_hash, salt = pbkdf2_hash(str(password))
            conn.execute(
                """
                INSERT INTO users
                    (company_id, username, full_name, linked_person_name, linked_units_json, password_hash, password_salt, role, is_active, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    company_id,
                    username,
                    normalize_whitespace(row.get("full_name")),
                    normalize_whitespace(row.get("linked_person_name")),
                    json.dumps(linked_units, ensure_ascii=False),
                    pwd_hash,
                    salt,
                    row["role"],
                    1 if row.get("is_active", True) not in {False, "0", 0, "false", "False"} else 0,
                    now_iso(),
                ),
            )
            created += 1
    elif table_name == "client_registry":
        for row in rows:
            raw_name = row.get("client_name") or row.get("Razao Social/Nome") or row.get("razao_social_nome")
            client_name = normalize_whitespace(raw_name)
            if not client_name:
                continue
            raw_document = row.get("document_number") or row.get("CNPJ/CPF") or row.get("cnpj_cpf")
            doc_person_type, _ = person_type_from_document(raw_document)
            if doc_person_type:
                person_type = doc_person_type
                confidence_score = 1.0
                notes = "documento"
            else:
                person_type = row.get("person_type") or row.get("tipo_pessoa")
                if not person_type:
                    person_type, confidence_score, notes = infer_person_type_from_name(client_name)
                else:
                    confidence_score = float(row.get("confidence_score") or 0.9)
                    notes = row.get("notes")
            upsert_client_registry_row(
                conn,
                company_id,
                client_name,
                raw_document,
                person_type,
                row.get("source", "importacao_clientes"),
                confidence_score,
                notes,
            )
            created += 1
    if table_name == "goals_unit":
        sanitize_unit_goals(conn, company_id, user_id)
    audit_log(conn, company_id, user_id, "salvar", table_name, "batch", {"rows": created})
    conn.commit()
    # Metas, férias, feriados e cadastros alteram o dashboard — derruba os caches
    invalidate_calendar_cache(company_id)
    invalidate_dashboard_cache(company_id)
    return created


def csv_template(kind: str) -> bytes:
    buffer = io.StringIO()
    writer = csv.writer(buffer, delimiter=";")
    if kind == "people":
        writer.writerow(["person_name", "role_classification", "base_unit", "valid_from", "valid_to", "source"])
        writer.writerow(["NOME DO VENDEDOR", "Vendedor", "MATRIZ", "2026-04-01", "", "importacao"])
    elif kind == "vacations":
        writer.writerow(["person_name", "start_date", "end_date", "notes"])
        writer.writerow(["NOME DO VENDEDOR", "2026-04-10", "2026-04-20", "Ferias abril"])
    elif kind == "holidays":
        writer.writerow(["holiday_date", "holiday_name", "scope"])
        writer.writerow(["2026-09-20", "Revolução Farroupilha", "NACIONAL_RS"])
    elif kind == "goals_seller":
        writer.writerow(["competence", "seller_name", "base_unit", "revenue_goal"])
        writer.writerow(["2026-04", "NOME DO VENDEDOR", "MATRIZ", "150000"])
    elif kind == "goals_unit":
        writer.writerow(["competence", "unit_name", "revenue_goal"])
        writer.writerow(["2026-04", "MATRIZ", "1100000"])
    elif kind == "users":
        writer.writerow(["username", "full_name", "linked_person_name", "linked_units_csv", "role", "password"])
        writer.writerow(["gerente.matriz", "Gerente Matriz", "", "MATRIZ;LAJEADO", "Gerente", "Senha@123"])
    elif kind == "clients":
        writer.writerow(["client_name", "document_number", "person_type", "source", "confidence_score", "notes"])
        writer.writerow(["CLIENTE EXEMPLO LTDA", "12.345.678/0001-90", "PJ", "importacao_clientes", "1", "documento"])
    return buffer.getvalue().encode("utf-8-sig")


def delete_user_record(conn: sqlite3.Connection, company_id: int, actor_user_id: int, target_user_id: int) -> None:
    target = conn.execute("SELECT * FROM users WHERE company_id = ? AND id = ?", (company_id, target_user_id)).fetchone()
    if not target:
        raise ValueError("Usuário não encontrado")
    if target["id"] == actor_user_id:
        raise ValueError("Não é permitido excluir o próprio usuário logado")
    if target["role"] == "Administrador":
        admin_count = conn.execute(
            "SELECT COUNT(*) AS total FROM users WHERE company_id = ? AND role = 'Administrador' AND is_active = 1",
            (company_id,),
        ).fetchone()["total"]
        if admin_count <= 1:
            raise ValueError("Mantenha pelo menos um administrador ativo no sistema")
    conn.execute("DELETE FROM sessions WHERE user_id = ?", (target_user_id,))
    conn.execute("DELETE FROM users WHERE company_id = ? AND id = ?", (company_id, target_user_id))
    audit_log(conn, company_id, actor_user_id, "excluir", "users", str(target_user_id), {"username": target["username"]})


ALLOWED_USER_ROLES = {"Administrador", "Gerente", "Analista", "Vendedor"}


def upsert_user(conn: sqlite3.Connection, company_id: int, actor_user_id: int, payload: dict[str, Any]) -> dict[str, Any]:
    """Cria ou atualiza um usuário. Faz o hash da senha quando informada."""
    username = normalize_whitespace(payload.get("username"))
    full_name = normalize_whitespace(payload.get("full_name"))
    if not username or not full_name:
        raise ValueError("Informe o usuário e o nome completo.")

    # O perfil é a fonte de verdade das permissões. A coluna `role` é mantida em
    # sincronia com o NOME do perfil para compatibilidade com o código legado.
    profile_id = payload.get("profile_id") or None
    profile_row = None
    if profile_id:
        profile_row = conn.execute(
            "SELECT * FROM access_profiles WHERE id = ? AND company_id = ?", (profile_id, company_id)
        ).fetchone()
        if not profile_row:
            raise ValueError("Perfil selecionado não existe.")
        role = profile_row["name"]
    else:
        role = normalize_whitespace(payload.get("role")) or "Administrador"
        profile_row = conn.execute(
            "SELECT * FROM access_profiles WHERE company_id = ? AND name = ?", (company_id, role)
        ).fetchone()
        if not profile_row:
            raise ValueError("Selecione um perfil de acesso.")
        profile_id = profile_row["id"]

    data_scope = profile_row["data_scope"] or "todos"
    linked_person = normalize_whitespace(payload.get("linked_person_name")) or None
    linked_units_raw = payload.get("linked_units") or []
    if not isinstance(linked_units_raw, list):
        linked_units_raw = []
    linked_units = [normalize_unit(u) for u in linked_units_raw if u]

    # Escopo "próprio" exige vínculo com a pessoa; escopos por unidade exigem unidades.
    if data_scope == "proprio":
        linked_units = []
        if not linked_person:
            raise ValueError("Perfis com escopo 'própria carteira' exigem a pessoa vinculada.")
    else:
        linked_person = None
        if data_scope in {"unidade", "unidade_consolidado"} and not linked_units:
            raise ValueError("Este perfil exige ao menos uma unidade vinculada.")

    linked_units_json = json.dumps(linked_units, ensure_ascii=False) if linked_units else None
    password = (payload.get("password") or "").strip()
    user_id = payload.get("id")

    if user_id:
        existing = conn.execute("SELECT * FROM users WHERE company_id = ? AND id = ?", (company_id, user_id)).fetchone()
        if not existing:
            raise ValueError("Usuário não encontrado.")
        dup = conn.execute("SELECT id FROM users WHERE username = ? AND id <> ?", (username, user_id)).fetchone()
        if dup:
            raise ValueError("Já existe um usuário com esse login.")
        conn.execute(
            "UPDATE users SET username = ?, full_name = ?, role = ?, profile_id = ?, linked_person_name = ?, linked_units_json = ? WHERE company_id = ? AND id = ?",
            (username, full_name, role, profile_id, linked_person, linked_units_json, company_id, user_id),
        )
        if password:
            pwd_hash, salt = pbkdf2_hash(password)
            conn.execute("UPDATE users SET password_hash = ?, password_salt = ? WHERE company_id = ? AND id = ?", (pwd_hash, salt, company_id, user_id))
        audit_log(conn, company_id, actor_user_id, "atualizar", "users", str(user_id), {"username": username, "role": role})
        return {"id": user_id, "created": False}

    if not password:
        raise ValueError("Defina a senha inicial.")
    dup = conn.execute("SELECT id FROM users WHERE username = ?", (username,)).fetchone()
    if dup:
        raise ValueError("Já existe um usuário com esse login.")
    pwd_hash, salt = pbkdf2_hash(password)
    cur = conn.execute(
        "INSERT INTO users (company_id, username, full_name, linked_person_name, linked_units_json, password_hash, password_salt, role, profile_id, is_active, created_at) VALUES (?,?,?,?,?,?,?,?,?,1,?)",
        (company_id, username, full_name, linked_person, linked_units_json, pwd_hash, salt, role, profile_id, now_iso()),
    )
    audit_log(conn, company_id, actor_user_id, "criar", "users", str(cur.lastrowid), {"username": username, "role": role})
    return {"id": cur.lastrowid, "created": True}


def set_user_password(conn: sqlite3.Connection, company_id: int, actor_user_id: int, target_user_id: Any, new_password: str | None) -> None:
    password = (new_password or "").strip()
    if not password:
        raise ValueError("Informe a nova senha.")
    target = conn.execute("SELECT id FROM users WHERE company_id = ? AND id = ?", (company_id, target_user_id)).fetchone()
    if not target:
        raise ValueError("Usuário não encontrado.")
    pwd_hash, salt = pbkdf2_hash(password)
    conn.execute("UPDATE users SET password_hash = ?, password_salt = ? WHERE company_id = ? AND id = ?", (pwd_hash, salt, company_id, target_user_id))
    audit_log(conn, company_id, actor_user_id, "trocar_senha", "users", str(target_user_id), {})


def import_admin_csv(conn: sqlite3.Connection, company_id: int, user_id: int, table_name: str, content: bytes) -> int:
    text = decode_text_content(content)
    reader = csv.DictReader(io.StringIO(text, newline=""), delimiter=";")
    rows = [dict(row) for row in reader]
    total = save_json_payload(conn, company_id, user_id, table_name, rows)
    if table_name == "client_registry":
        ensure_client_registry_for_sales(conn, company_id)
    return total


def import_city_mappings_csv(conn: sqlite3.Connection, company_id: int, user_id: int, content: bytes) -> dict[str, Any]:
    """Importa em lote o vinculo cidade->unidade a partir de um CSV e resolve as
    pendencias de 'cidade_sem_correspondencia' correspondentes.
    Colunas aceitas (cabecalho, sem diferenciar maiusculas/acentos):
      CIDADE (obrigatoria), PRINCIPAL ou UNIDADE (obrigatoria), ESTADO (opcional), PAIS (opcional).
    Separador ; ou , detectado automaticamente. O CSV e autoritativo: substitui o
    vinculo existente de cada cidade."""
    text = decode_text_content(content)
    first_line = next((ln for ln in text.splitlines() if ln.strip()), "")
    delimiter = ";" if first_line.count(";") >= first_line.count(",") else ","
    reader = csv.DictReader(io.StringIO(text, newline=""), delimiter=delimiter)

    field_map: dict[str, str] = {}
    for header in (reader.fieldnames or []):
        key = normalize_upper(header)
        if key in ("CIDADE", "CITY", "MUNICIPIO"):
            field_map["city"] = header
        elif key in ("PRINCIPAL", "UNIDADE", "UNIDADE PRINCIPAL", "UNIT"):
            field_map["unit"] = header
        elif key in ("ESTADO", "UF", "STATE"):
            field_map["state"] = header
        elif key in ("PAIS", "PAÍS", "COUNTRY"):
            field_map["country"] = header
    if "city" not in field_map or "unit" not in field_map:
        raise ValueError("O CSV precisa ter as colunas CIDADE e PRINCIPAL (ou UNIDADE).")

    now = now_iso()
    updated = 0
    for row in reader:
        city = normalize_upper(row.get(field_map["city"]))
        unit = normalize_unit(row.get(field_map["unit"]))
        if not city or not unit:
            continue
        state = normalize_upper(row.get(field_map["state"])) if field_map.get("state") else None
        country = normalize_upper(row.get(field_map["country"])) if field_map.get("country") else None
        conn.execute("DELETE FROM city_mappings WHERE company_id = ? AND city_name = ?", (company_id, city))
        conn.execute(
            """
            INSERT INTO city_mappings
                (company_id, city_name, principal_unit, state_name, country_name, valid_from, valid_to, source, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (company_id, city, unit, state or None, country or None, "2025-01-01", None, "csv_lote", now),
        )
        updated += 1

    # Resolve as pendencias de cidade que agora tem vinculo
    cur = conn.execute(
        """
        UPDATE import_issues
        SET status = 'resolvida'
        WHERE company_id = ? AND issue_type = 'cidade_sem_correspondencia' AND status = 'pendente'
          AND reference_value IN (SELECT city_name FROM city_mappings WHERE company_id = ?)
        """,
        (company_id, company_id),
    )
    resolved = cur.rowcount if (cur.rowcount and cur.rowcount > 0) else 0
    return {"updated": updated, "resolved": resolved}


def update_person_unit(conn: sqlite3.Connection, company_id: int, user_id: int, person_name: str | None, base_unit: str | None) -> str:
    """Corrige a unidade de um vendedor/pessoa. Aplica a todos os registros da pessoa
    (fica consistente entre competencias). Cria o registro se ainda nao existir."""
    person = normalize_whitespace(person_name)
    unit = normalize_unit(base_unit)
    if not person or not unit:
        raise ValueError("Informe o vendedor e a unidade.")
    cur = conn.execute(
        "UPDATE people_records SET base_unit = ? WHERE company_id = ? AND person_name = ?",
        (unit, company_id, person),
    )
    if not cur.rowcount:
        conn.execute(
            """
            INSERT INTO people_records
                (company_id, person_name, role_classification, base_unit, valid_from, valid_to, source, is_active, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, 1, ?)
            """,
            (company_id, person, infer_role_from_name(person), unit, "2025-01-01", None, "edicao_manual", now_iso()),
        )
    conn.execute(
        """
        UPDATE import_issues SET status = 'resolvida'
        WHERE company_id = ? AND issue_type = 'vendedor_sem_vinculo' AND status = 'pendente' AND reference_value = ?
        """,
        (company_id, person),
    )
    audit_log(conn, company_id, user_id, "ajustar_unidade", "people_records", person, {"base_unit": unit})
    return unit


def update_city_unit(conn: sqlite3.Connection, company_id: int, user_id: int, city_name: str | None, principal_unit: str | None) -> str:
    """Corrige a unidade principal de uma cidade e resolve a pendencia correspondente."""
    city = normalize_upper(city_name)
    unit = normalize_unit(principal_unit)
    if not city or not unit:
        raise ValueError("Informe a cidade e a unidade.")
    cur = conn.execute(
        "UPDATE city_mappings SET principal_unit = ? WHERE company_id = ? AND city_name = ?",
        (unit, company_id, city),
    )
    if not cur.rowcount:
        conn.execute(
            """
            INSERT INTO city_mappings
                (company_id, city_name, principal_unit, state_name, country_name, valid_from, valid_to, source, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (company_id, city, unit, None, None, "2025-01-01", None, "edicao_manual", now_iso()),
        )
    conn.execute(
        """
        UPDATE import_issues SET status = 'resolvida'
        WHERE company_id = ? AND issue_type = 'cidade_sem_correspondencia' AND status = 'pendente' AND reference_value = ?
        """,
        (company_id, city),
    )
    audit_log(conn, company_id, user_id, "ajustar_unidade", "city_mappings", city, {"principal_unit": unit})
    return unit


def export_dashboard_xlsx(data: dict[str, Any]) -> bytes:
    wb = Workbook()
    ws = wb.active
    ws.title = "Resumo"
    ws.append(["Indicador", "Valor"])
    for key, value in data["summary"].items():
        ws.append([key, value])

    ws_sellers = wb.create_sheet("Vendedores")
    ws_sellers.append(["Vendedor", "Unidade Base", "Faturamento Líquido", "Meta", "% Meta", "Ticket",
                       "Clientes", "Mix", "Devolução Comercial", "Devolução Garantia", "Devolução Total", "Score"])
    for row in data["sellerRanking"]:
        ws_sellers.append([
            row["sellerName"],
            row.get("baseUnit"),
            row["revenueNet"],
            row["revenueGoal"],
            row["goalAttainmentPct"],
            row["ticketAverage"],
            row["distinctClients"],
            row["mixSku"],
            row["returnsValue"],
            row.get("warrantyReturnsValue", 0),
            row.get("returnsTotalValue", row["returnsValue"]),
            row["score"],
        ])

    ws_units = wb.create_sheet("Unidades")
    ws_units.append(["Unidade", "Faturamento Líquido", "Meta", "% Meta",
                     "Devolução Comercial", "Devolução Garantia", "Devolução Total", "Margem"])
    for row in data["unitPerformance"]:
        ws_units.append([row["unitName"], row["revenueNet"], row["revenueGoal"], row["goalAttainmentPct"],
                         row["returnsValue"], row.get("warrantyReturnsValue", 0),
                         row.get("returnsTotalValue", row["returnsValue"]), row["marginValue"]])

    ws_cities = wb.create_sheet("Cidades")
    ws_cities.append(["Cidade", "Faturamento Líquido", "Ticket Médio", "Clientes Distintos", "Desconto"])
    for row in data["cityRanking"]:
        ws_cities.append([row["cityName"], row["revenueNet"], row["ticketAverage"], row["distinctClients"], row["discountValue"]])

    output = io.BytesIO()
    wb.save(output)
    return output.getvalue()


def export_dashboard_pdf(data: dict[str, Any]) -> bytes:
    output = io.BytesIO()
    doc = SimpleDocTemplate(output, pagesize=landscape(A4), leftMargin=24, rightMargin=24, topMargin=24, bottomMargin=24)
    styles = getSampleStyleSheet()
    elements = [
        Paragraph("Dashboard Comercial Passini", styles["Title"]),
        Spacer(1, 12),
        Paragraph(f"Competência principal: {data.get('primaryCompetence') or 'Não definida'}", styles["Normal"]),
        Spacer(1, 12),
    ]

    summary_table = [["Indicador", "Valor"]]
    for key, value in data["summary"].items():
        summary_table.append([key, str(value)])
    table = Table(summary_table, repeatRows=1)
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#12324a")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#bfd7ea")),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ]
        )
    )
    elements.append(table)
    elements.append(Spacer(1, 18))

    top10 = [["Vendedor", "% Meta", "Score", "Faturamento Líquido", "Clientes", "Mix"]]
    for row in data["sellerTop10"]:
        top10.append([row["sellerName"], row["goalAttainmentPct"], row["score"], row["revenueNet"], row["distinctClients"], row["mixSku"]])
    table_top = Table(top10, repeatRows=1)
    table_top.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1e5f74")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#dce6ef")),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ]
        )
    )
    elements.append(Paragraph("Top 10 vendedores", styles["Heading2"]))
    elements.append(table_top)

    doc.build(elements)
    return output.getvalue()


def compute_seller_score(conn: sqlite3.Connection, company_id: int, user: sqlite3.Row, competence: str | None = None) -> dict[str, Any]:
    """Calcula os 9 indicadores de premiação para o vendedor logado."""
    seller_name = seller_identity_for_user(user)
    today = date.today()
    if not competence:
        competence = today.strftime("%Y-%m")
    comp_start = first_day_of_competence(competence).isoformat()
    comp_end = (first_day_of_competence(competence).replace(day=28) + timedelta(days=4)).replace(day=1) - timedelta(days=1)
    comp_end_iso = comp_end.isoformat()

    # ── 1. META DE VENDAS ────────────────────────────────────────────────────
    goal_row = conn.execute(
        "SELECT revenue_goal FROM goals_seller WHERE company_id = ? AND competence = ? AND seller_name = ?",
        (company_id, competence, seller_name),
    ).fetchone()
    revenue_goal = float(goal_row["revenue_goal"]) if goal_row else 0.0

    vendor_row = conn.execute(
        "SELECT COALESCE(SUM(net_value),0) AS net_value FROM fact_vendor_summary WHERE company_id = ? AND competence = ? AND seller_name = ?",
        (company_id, competence, seller_name),
    ).fetchone()
    revenue_actual = float(vendor_row["net_value"]) if vendor_row else 0.0
    goal_pct = (revenue_actual / revenue_goal * 100) if revenue_goal > 0 else 0.0

    if goal_pct >= 110:
        goal_pts = 50
    elif goal_pct >= 100:
        goal_pts = 30
    elif goal_pct >= 95:
        goal_pts = 15
    elif goal_pct >= 90:
        goal_pts = 5
    else:
        goal_pts = 0

    # ── 2. MARGEM DE VENDA ───────────────────────────────────────────────────
    margin_row = conn.execute(
        "SELECT COALESCE(AVG(margin_value),0) AS margin FROM fact_vendor_summary WHERE company_id = ? AND competence = ? AND seller_name = ?",
        (company_id, competence, seller_name),
    ).fetchone()
    margin_actual = float(margin_row["margin"]) if margin_row else 0.0
    if margin_actual >= 1.59:
        margin_pts = 20
    elif margin_actual >= 1.52:
        margin_pts = 10
    elif margin_actual >= 1.50:
        margin_pts = 5
    else:
        margin_pts = 0

    # ── 3. MIX DE ITENS (SKU distintos) ──────────────────────────────────────
    base_unit_row = conn.execute(
        "SELECT base_unit FROM people_records WHERE company_id = ? AND person_name = ? AND (valid_to IS NULL OR valid_to >= ?) ORDER BY valid_from DESC LIMIT 1",
        (company_id, seller_name, comp_start),
    ).fetchone()
    base_unit = normalize_unit(base_unit_row["base_unit"]) if base_unit_row else ""
    unit_item_goals = {
        "MATRIZ": 650, "LAJEADO": 1000, "PELOTAS": 850,
        "PORTO ALEGRE": 900, "XANGRI-LA": 750,
    }
    item_goal = unit_item_goals.get(base_unit, 800)

    sku_row = conn.execute(
        """SELECT COUNT(DISTINCT sku_key) AS sku_count
           FROM fact_sales_detail
           WHERE company_id = ? AND competence = ? AND seller_name = ? AND sku_key IS NOT NULL AND sku_key != ''""",
        (company_id, competence, seller_name),
    ).fetchone()
    sku_actual = int(sku_row["sku_count"]) if sku_row else 0
    item_pts = 10 if sku_actual >= item_goal else 0

    # ── GATILHO DA UNIDADE ───────────────────────────────────────────────────
    # Elegível se: unidade >= 95% da meta OU vendedor individualmente >= 105%
    unit_goal_row = conn.execute(
        "SELECT revenue_goal FROM goals_unit WHERE company_id = ? AND competence = ? AND unit_name = ?",
        (company_id, competence, base_unit),
    ).fetchone()
    unit_revenue_goal = float(unit_goal_row["revenue_goal"]) if unit_goal_row else 0.0
    unit_revenue_row = conn.execute(
        "SELECT COALESCE(SUM(net_value),0) AS net FROM fact_unit_summary WHERE company_id = ? AND competence = ? AND unit_name = ?",
        (company_id, competence, base_unit),
    ).fetchone()
    unit_revenue_actual = float(unit_revenue_row["net"]) if unit_revenue_row else 0.0
    unit_goal_pct = (unit_revenue_actual / unit_revenue_goal * 100) if unit_revenue_goal > 0 else 0.0
    unit_gate_met = unit_goal_pct >= 95.0
    seller_overrides_gate = goal_pct >= 105.0  # vendedor dispensa o gatilho

    # ── 4. POSITIVAÇÃO DA CARTEIRA ────────────────────────────────────────────
    total_clients_row = conn.execute(
        """SELECT COUNT(DISTINCT client_code) AS total
           FROM crm_client_summary WHERE company_id = ? AND seller_name = ?""",
        (company_id, seller_name),
    ).fetchone()
    total_clients = int(total_clients_row["total"]) if total_clients_row else 0

    active_clients_row = conn.execute(
        """SELECT COUNT(DISTINCT client_code) AS active
           FROM crm_client_summary WHERE company_id = ? AND competence = ? AND seller_name = ? AND net_value > 0""",
        (company_id, competence, seller_name),
    ).fetchone()
    active_clients = int(active_clients_row["active"]) if active_clients_row else 0
    pos_pct = (active_clients / total_clients * 100) if total_clients > 0 else 0.0
    if pos_pct >= 85:
        pos_pts = 20
    elif pos_pct >= 50:
        pos_pts = 10
    else:
        pos_pts = 0

    # ── 5. DEVOLUÇÕES ─────────────────────────────────────────────────────────
    returns_row = conn.execute(
        """SELECT COALESCE(SUM(return_value),0) AS returns, COALESCE(SUM(net_value),0) AS net
           FROM fact_vendor_summary WHERE company_id = ? AND competence = ? AND seller_name = ?""",
        (company_id, competence, seller_name),
    ).fetchone()
    returns_val = float(returns_row["returns"]) if returns_row else 0.0
    net_val = float(returns_row["net"]) if returns_row else 0.0
    return_pct = (returns_val / (net_val + returns_val) * 100) if (net_val + returns_val) > 0 else 0.0
    dev_pts = 10 if return_pct <= 4.5 else 0

    # ── 6. EXTRA POSITIVAÇÃO (inativos reativados) ────────────────────────────
    # Clientes PJ da carteira do vendedor que estavam inativos (sem compra ≥2 meses) e compraram este mês ≥R$999
    prev_comp = (first_day_of_competence(competence).replace(day=1) - timedelta(days=1)).strftime("%Y-%m")
    prev2_comp = (first_day_of_competence(prev_comp).replace(day=1) - timedelta(days=1)).strftime("%Y-%m")

    inactive_reactivated = conn.execute(
        """SELECT COUNT(*) AS cnt
           FROM crm_client_summary curr
           WHERE curr.company_id = ? AND curr.competence = ? AND curr.seller_name = ? AND curr.net_value >= 999
             AND NOT EXISTS (
                 SELECT 1 FROM crm_client_summary prev
                 WHERE prev.company_id = curr.company_id AND prev.client_code = curr.client_code
                   AND prev.competence IN (?, ?) AND prev.net_value > 0
             )""",
        (company_id, competence, seller_name, prev_comp, prev2_comp),
    ).fetchone()
    extra_pos = int(inactive_reactivated["cnt"]) if inactive_reactivated else 0
    extra_pts = min(extra_pos, 10)

    # ── 7. TREINAMENTOS EAD (manual — sem integração disponível) ─────────────
    training_pts = 0  # placeholder — integrar quando EAD Passini tiver API
    training_done = False

    # ── 8. LIGAÇÕES ATIVAS (interações registradas no mês) ───────────────────
    calls_row = conn.execute(
        """SELECT COUNT(*) AS cnt FROM crm_interactions
           WHERE company_id = ? AND seller_name = ?
             AND substr(occurred_at, 1, 7) = ?
             AND result_code NOT IN ('NAO_ATENDEU', 'PEDIU_RETORNO')""",
        (company_id, seller_name, competence),
    ).fetchone()
    calls_actual = int(calls_row["cnt"]) if calls_row else 0
    calls_pts = 10 if calls_actual >= 60 else 0

    # ── 9. REDES SOCIAIS (manual — sem integração disponível) ────────────────
    social_pts = 0  # placeholder
    social_count = 0

    # ── TOTAL ─────────────────────────────────────────────────────────────────
    total_pts = goal_pts + margin_pts + item_pts + pos_pts + dev_pts + extra_pts + training_pts + calls_pts + social_pts
    max_pts = 150

    # ── PREMIAÇÃO ESTIMADA ────────────────────────────────────────────────────
    base_prize = 185 if revenue_goal < 160000 else (380 if revenue_goal < 310000 else 530)
    prize_pct = min(total_pts / 100, 1.5) if total_pts >= 60 else (total_pts / 100)
    estimated_prize = round(base_prize * prize_pct, 2) if total_pts >= 60 else 0.0
    gate_ok = unit_gate_met or seller_overrides_gate
    eligible = goal_pts > 0 and gate_ok  # precisa bater meta própria E gatilho da unidade (ou 105%+)

    return {
        "competence": competence,
        "sellerName": seller_name,
        "totalPoints": total_pts,
        "maxPoints": max_pts,
        "estimatedPrize": estimated_prize,
        "basePrize": base_prize,
        "eligible": eligible,
        "unitGate": {
            "unitName": base_unit,
            "unitGoalPct": round(unit_goal_pct, 1),
            "unitGoal": round(unit_revenue_goal, 2),
            "unitActual": round(unit_revenue_actual, 2),
            "gateMet": unit_gate_met,
            "sellerOverrides": seller_overrides_gate,
            "gateOk": gate_ok,
        },
        "indicators": {
            "goalSales":       {"pts": goal_pts,    "max": 50, "actual": round(goal_pct, 1),   "goal": 100.0,    "unit": "%",  "label": "Meta de Vendas"},
            "margin":          {"pts": margin_pts,  "max": 20, "actual": round(margin_actual,2),"goal": 1.59,     "unit": "x",  "label": "Margem de Venda"},
            "mix":             {"pts": item_pts,    "max": 10, "actual": sku_actual,           "goal": item_goal,"unit": "itens","label": "Mix de Itens"},
            "positivacao":     {"pts": pos_pts,     "max": 20, "actual": round(pos_pct, 1),    "goal": 85.0,     "unit": "%",  "label": "Positivação da Carteira"},
            "returns":         {"pts": dev_pts,     "max": 10, "actual": round(return_pct, 2), "goal": 4.5,      "unit": "%",  "label": "Devoluções"},
            "extraPos":        {"pts": extra_pts,   "max": 10, "actual": extra_pos,            "goal": 10,       "unit": "clientes","label": "Extra Positivação"},
            "training":        {"pts": training_pts,"max": 10, "actual": 0,                    "goal": 100,      "unit": "%",  "label": "Treinamentos EAD"},
            "calls":           {"pts": calls_pts,   "max": 10, "actual": calls_actual,         "goal": 60,       "unit": "lig.","label": "Ligações Ativas"},
            "social":          {"pts": social_pts,  "max": 10, "actual": social_count,         "goal": 10,       "unit": "posts","label": "Redes Sociais"},
        },
    }


def compute_team_score(conn: sqlite3.Connection, company_id: int, user: sqlite3.Row) -> dict[str, Any]:
    """Calcula o score de todos os vendedores visíveis ao gerente/admin no mês corrente."""
    today = date.today()
    competence = today.strftime("%Y-%m")
    comp_start = first_day_of_competence(competence).isoformat()

    # Determinar quais vendedores estão no escopo do usuário
    allowed_units = linked_units_for_user(user) if user["role"] in {"Gerente", "Analista"} else []

    # Buscar todos os vendedores com metas no mês ou com vendas no mês
    sellers_in_scope: list[str] = []
    goal_rows = conn.execute(
        "SELECT DISTINCT seller_name FROM goals_seller WHERE company_id = ? AND competence = ?",
        (company_id, competence),
    ).fetchall()
    vendor_rows = conn.execute(
        "SELECT DISTINCT seller_name FROM fact_vendor_summary WHERE company_id = ? AND competence = ?",
        (company_id, competence),
    ).fetchall()
    all_sellers = {normalize_whitespace(r["seller_name"]) for r in goal_rows + vendor_rows if r["seller_name"]}

    # Filtrar por unidades do gerente se aplicável
    for seller_name in sorted(all_sellers):
        if allowed_units:
            _, base_unit = current_role_and_unit(conn, company_id, seller_name, competence)
            if normalize_unit(base_unit) not in allowed_units:
                continue
        sellers_in_scope.append(seller_name)

    # Pré-carregar metas e vendas em batch
    goal_map: dict[str, float] = {
        normalize_whitespace(r["seller_name"]): float(r["revenue_goal"])
        for r in conn.execute(
            "SELECT seller_name, revenue_goal FROM goals_seller WHERE company_id = ? AND competence = ?",
            (company_id, competence),
        ).fetchall()
    }
    vendor_map: dict[str, dict] = {
        normalize_whitespace(r["seller_name"]): dict(r)
        for r in conn.execute(
            "SELECT seller_name, SUM(net_value) AS net_value, SUM(return_value) AS return_value, AVG(margin_value) AS margin_value FROM fact_vendor_summary WHERE company_id = ? AND competence = ? GROUP BY seller_name",
            (company_id, competence),
        ).fetchall()
    }

    # Pré-carregar positivação
    pos_map: dict[str, int] = {}
    total_clients_map: dict[str, int] = {}
    for r in conn.execute(
        "SELECT seller_name, COUNT(DISTINCT client_code) AS total FROM crm_client_summary WHERE company_id = ? GROUP BY seller_name",
        (company_id,),
    ).fetchall():
        total_clients_map[normalize_whitespace(r["seller_name"])] = int(r["total"])
    for r in conn.execute(
        "SELECT seller_name, COUNT(DISTINCT client_code) AS active FROM crm_client_summary WHERE company_id = ? AND competence = ? AND net_value > 0 GROUP BY seller_name",
        (company_id, competence),
    ).fetchall():
        pos_map[normalize_whitespace(r["seller_name"])] = int(r["active"])

    # Pré-carregar ligações ativas
    calls_map: dict[str, int] = {
        normalize_whitespace(r["seller_name"]): int(r["cnt"])
        for r in conn.execute(
            "SELECT seller_name, COUNT(*) AS cnt FROM crm_interactions WHERE company_id = ? AND substr(occurred_at,1,7) = ? AND result_code NOT IN ('NAO_ATENDEU', 'PEDIU_RETORNO') GROUP BY seller_name",
            (company_id, competence),
        ).fetchall()
    }

    # Pré-carregar SKUs por vendedor
    sku_map: dict[str, int] = {
        normalize_whitespace(r["seller_name"]): int(r["sku_count"])
        for r in conn.execute(
            "SELECT seller_name, COUNT(DISTINCT sku_key) AS sku_count FROM fact_sales_detail WHERE company_id = ? AND competence = ? GROUP BY seller_name",
            (company_id, competence),
        ).fetchall()
    }

    # Pré-carregar unidades dos vendedores
    unit_item_goals = {"MATRIZ": 650, "LAJEADO": 1000, "PELOTAS": 850, "PORTO ALEGRE": 900, "XANGRI-LA": 750}
    _comp_target = first_day_of_competence(competence).isoformat()
    seller_unit_map: dict[str, str] = {
        normalize_whitespace(r["person_name"]): normalize_unit(r["base_unit"]) or ""
        for r in conn.execute(
            "SELECT person_name, base_unit FROM people_records WHERE company_id = ? AND date(valid_from) <= date(?) AND (valid_to IS NULL OR date(valid_to) >= date(?)) ORDER BY valid_from DESC",
            (company_id, _comp_target, _comp_target),
        ).fetchall()
    }

    results = []
    for seller_name in sellers_in_scope:
        revenue_goal = goal_map.get(seller_name, 0.0)
        vendor = vendor_map.get(seller_name, {})
        revenue_actual = float(vendor.get("net_value") or 0)
        returns_val = float(vendor.get("return_value") or 0)
        margin = float(vendor.get("margin_value") or 0)
        goal_pct = (revenue_actual / revenue_goal * 100) if revenue_goal > 0 else 0.0

        if goal_pct >= 110: goal_pts = 50
        elif goal_pct >= 100: goal_pts = 30
        elif goal_pct >= 95: goal_pts = 15
        elif goal_pct >= 90: goal_pts = 5
        else: goal_pts = 0

        margin_pts = 20 if margin >= 1.59 else (10 if margin >= 1.52 else (5 if margin >= 1.50 else 0))

        base_unit = seller_unit_map.get(seller_name, "")
        item_goal = unit_item_goals.get(base_unit, 800)
        sku_actual = sku_map.get(seller_name, 0)
        item_pts = 10 if sku_actual >= item_goal else 0

        total_clients = total_clients_map.get(seller_name, 0)
        active_clients = pos_map.get(seller_name, 0)
        pos_pct = (active_clients / total_clients * 100) if total_clients > 0 else 0.0
        pos_pts = 20 if pos_pct >= 85 else (10 if pos_pct >= 50 else 0)

        net_val = revenue_actual
        return_pct = (returns_val / (net_val + returns_val) * 100) if (net_val + returns_val) > 0 else 0.0
        dev_pts = 10 if return_pct <= 4.5 else 0

        calls_actual = calls_map.get(seller_name, 0)
        calls_pts = 10 if calls_actual >= 60 else 0

        total_pts = goal_pts + margin_pts + item_pts + pos_pts + dev_pts + calls_pts
        base_prize = 185 if revenue_goal < 160000 else (380 if revenue_goal < 310000 else 530)
        eligible = goal_pts > 0

        results.append({
            "sellerName": seller_name,
            "baseUnit": base_unit,
            "totalPoints": total_pts,
            "eligible": eligible,
            "estimatedPrize": round(base_prize * min(total_pts / 100, 1.5), 2) if total_pts >= 60 else 0.0,
            "goalPct": round(goal_pct, 1),
            "goalPts": goal_pts,
            "positivacaoPct": round(pos_pct, 1),
            "positivacaoPts": pos_pts,
            "callsActual": calls_actual,
            "callsPts": calls_pts,
            "returnPct": round(return_pct, 2),
            "devPts": dev_pts,
            "marginPts": margin_pts,
            "itemPts": item_pts,
            "revenueActual": round(revenue_actual, 2),
            "revenueGoal": round(revenue_goal, 2),
        })

    results.sort(key=lambda r: r["totalPoints"], reverse=True)

    return {
        "competence": competence,
        "sellers": results,
        "summary": {
            "total": len(results),
            "eligible": sum(1 for r in results if r["eligible"]),
            "inPrizeZone": sum(1 for r in results if r["totalPoints"] >= 60),
            "fullPrize": sum(1 for r in results if r["totalPoints"] >= 100),
        },
    }


# Meta diária de contatos por vendedor na Missão do Dia
DAILY_CONTACT_GOAL = 5
# Dias sem interação para considerar que a cobertura falhou
COVERAGE_GAP_DAYS = 7


def compute_unassigned_clients(
    conn: sqlite3.Connection, company_id: int, user: sqlite3.Row,
    min_months: int = 2, months_window: int = 6, limit: int = 200,
) -> dict[str, Any]:
    """Clientes que compram com recorrência mas não têm vendedor no cadastro CRM.

    São clientes "no limpo": ninguém responde por eles, então ninguém previne a
    perda. O gestor usa esta lista para atribuir dono. Mostra quem já atendeu o
    cliente, o que ajuda a decidir a atribuição.
    """
    latest = crm_latest_competence(conn, company_id) or date.today().strftime("%Y-%m")
    window_start = shift_competence(latest, -(months_window - 1))

    # Clientes COM dono no cadastro — excluídos do resultado
    owned: set[str] = set()
    for row in conn.execute(
        "SELECT client_name FROM crm_client_profiles WHERE company_id = ? "
        "AND (TRIM(COALESCE(internal_seller_name,'')) <> '' OR TRIM(COALESCE(external_seller_name,'')) <> '')",
        (company_id,),
    ).fetchall():
        key = normalize_client_key(row["client_name"])
        if key:
            owned.add(key)

    allowed_units = crm_allowed_units_for_user(conn, user)
    city_unit = build_city_unit_map(conn, company_id, latest)

    rows = conn.execute(
        """
        SELECT client_name,
               MAX(city_name) AS city_name,
               COUNT(DISTINCT competence) AS meses,
               ROUND(SUM(net_value), 2) AS receita,
               MAX(issue_date) AS ultima_compra,
               COUNT(DISTINCT seller_name) AS qtd_vendedores
        FROM fact_sales_detail
        WHERE company_id = ? AND competence >= ? AND net_value > 0
        GROUP BY client_name
        HAVING meses >= ?
        ORDER BY receita DESC
        """,
        (company_id, window_start, min_months),
    ).fetchall()

    # Vendedores que atenderam cada cliente, com receita de cada um
    sellers_by_client: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for r in conn.execute(
        """
        SELECT client_name, seller_name,
               COUNT(DISTINCT competence) AS meses,
               ROUND(SUM(net_value), 2) AS receita
        FROM fact_sales_detail
        WHERE company_id = ? AND competence >= ? AND net_value > 0
        GROUP BY client_name, seller_name
        ORDER BY receita DESC
        """,
        (company_id, window_start),
    ).fetchall():
        sellers_by_client[normalize_client_key(r["client_name"])].append({
            "sellerName": normalize_whitespace(r["seller_name"]),
            "months": int(r["meses"] or 0),
            "revenue": float(r["receita"] or 0.0),
        })

    items: list[dict[str, Any]] = []
    total_revenue = 0.0
    for r in rows:
        key = normalize_client_key(r["client_name"])
        if not key or key in owned:
            continue
        unit = city_unit.get(normalize_upper(r["city_name"]))
        if allowed_units and unit not in allowed_units:
            continue
        sellers = sellers_by_client.get(key, [])[:5]
        receita = float(r["receita"] or 0.0)
        total_revenue += receita
        items.append({
            "clientName": r["client_name"],
            "cityName": r["city_name"],
            "unitName": unit,
            "months": int(r["meses"] or 0),
            "revenue": round(receita, 2),
            "avgMonthly": round(safe_div(receita, int(r["meses"] or 1)), 2),
            "lastPurchaseAt": r["ultima_compra"],
            "sellerCount": int(r["qtd_vendedores"] or 0),
            "sellers": sellers,
            "mainSeller": sellers[0]["sellerName"] if sellers else None,
        })

    return {
        "items": items[:limit],
        "total": len(items),
        "totalRevenue": round(total_revenue, 2),
        "criteria": {
            "minMonths": min_months,
            "monthsWindow": months_window,
            "windowStart": window_start,
            "windowEnd": latest,
        },
    }


def compute_manager_mission(
    conn: sqlite3.Connection, company_id: int, user: sqlite3.Row,
    filters: dict[str, str | None], limit: int = 12,
) -> dict[str, Any]:
    """Missão do Dia na ótica de gestão: onde a execução está falhando.

    Diferente da visão do vendedor (fila de quem ligar), o gestor recebe dois
    recortes de risco, ambos com o vendedor responsável ao lado para cobrança:
      - coverageGap: cliente parou de comprar E ninguém o contatou há dias
      - highValueDrop: cliente Diamante/Ouro comprando menos
    """
    rows = crm_base_client_rows_cached(conn, company_id, filters)
    today = date.today()

    def days_since(value: Any) -> int | None:
        dt = parse_datetime_flexible(value) if value else None
        return (today - dt.date()).days if dt else None

    coverage_gap: list[dict[str, Any]] = []
    high_value_drop: list[dict[str, Any]] = []

    for row in rows:
        seller = normalize_whitespace(row.get("assignedSeller")) or "Sem vendedor"
        days_no_contact = days_since(row.get("lastInteractionAt"))
        status = row.get("statusCode")
        item = {
            "clientKey": row.get("clientKey"),
            "clientName": row.get("clientName"),
            "cityName": row.get("cityName"),
            "unitName": row.get("unitName"),
            "assignedSeller": seller,
            "statusCode": status,
            "classCode": row.get("classCode"),
            "daysWithoutPurchase": row.get("daysWithoutPurchase"),
            "daysWithoutContact": days_no_contact,
            "averageRevenue": row.get("averageRevenue"),
            "currentRevenue": row.get("currentRevenue"),
            "dropPct": row.get("dropPct"),
            "phone": row.get("phone"),
        }
        # Bloco 1 — cobertura falha: parou de comprar e ninguém falou com ele
        if status in {"INATIVO", "PRE_INATIVO"} and (days_no_contact is None or days_no_contact >= COVERAGE_GAP_DAYS):
            coverage_gap.append(item)
        # Bloco 2 — cliente grande perdendo volume
        if row.get("classCode") in {"DIAMANTE", "OURO"} and float(row.get("dropPct") or 0) <= -0.1:
            high_value_drop.append(item)

    # Prioriza o que dói mais no bolso: maior média histórica primeiro
    coverage_gap.sort(key=lambda r: float(r.get("averageRevenue") or 0), reverse=True)
    high_value_drop.sort(key=lambda r: float(r.get("averageRevenue") or 0), reverse=True)

    def by_seller(items: list[dict[str, Any]]) -> list[dict[str, Any]]:
        agg: dict[str, int] = defaultdict(int)
        for i in items:
            agg[i["assignedSeller"]] += 1
        return [{"sellerName": k, "count": v} for k, v in sorted(agg.items(), key=lambda x: -x[1])]

    return {
        "coverageGap": coverage_gap[:limit],
        "coverageGapTotal": len(coverage_gap),
        "coverageGapBySeller": by_seller(coverage_gap),
        "highValueDrop": high_value_drop[:limit],
        "highValueDropTotal": len(high_value_drop),
        "highValueDropBySeller": by_seller(high_value_drop),
        "coverageGapDays": COVERAGE_GAP_DAYS,
    }


def compute_team_activity_today(
    conn: sqlite3.Connection, company_id: int, user: sqlite3.Row
) -> dict[str, Any]:
    """Retorna atividade de hoje por vendedor para visão gerencial da Missão do Dia."""
    today_str = date.today().isoformat()
    competence = date.today().strftime("%Y-%m")
    comp_target = first_day_of_competence(competence).isoformat()

    contacts_rows = conn.execute(
        """
        SELECT seller_name,
               COUNT(*) AS total,
               SUM(CASE WHEN result_code NOT IN ('NAO_ATENDEU','PEDIU_RETORNO') THEN 1 ELSE 0 END) AS active
        FROM crm_interactions
        WHERE company_id = ? AND substr(occurred_at,1,10) = ?
        GROUP BY seller_name
        """,
        (company_id, today_str),
    ).fetchall()

    tasks_rows = conn.execute(
        "SELECT seller_name, COUNT(*) AS overdue FROM crm_tasks WHERE company_id = ? AND status = 'ATRASADA' GROUP BY seller_name",
        (company_id,),
    ).fetchall()

    open_rows = conn.execute(
        "SELECT seller_name, COUNT(*) AS abertas FROM crm_tasks WHERE company_id = ? AND status = 'ABERTA' GROUP BY seller_name",
        (company_id,),
    ).fetchall()
    open_map = {normalize_whitespace(r["seller_name"]): int(r["abertas"]) for r in open_rows}

    # Última vez que cada vendedor registrou qualquer interação
    last_interaction_map = {
        normalize_whitespace(r["seller_name"]): r["last_at"]
        for r in conn.execute(
            "SELECT seller_name, MAX(occurred_at) AS last_at FROM crm_interactions WHERE company_id = ? GROUP BY seller_name",
            (company_id,),
        ).fetchall()
    }

    # Vendedores com meta cadastrada no mês atual. A própria meta guarda a unidade
    # base — usar isso evita depender de people_records estar atualizado.
    seller_rows = conn.execute(
        "SELECT seller_name, MAX(base_unit) AS base_unit FROM goals_seller "
        "WHERE company_id = ? AND competence = ? GROUP BY seller_name",
        (company_id, competence),
    ).fetchall()

    seller_unit_map: dict[str, str] = {}
    for r in conn.execute(
        "SELECT person_name, base_unit FROM people_records WHERE company_id = ? AND date(valid_from) <= date(?) AND (valid_to IS NULL OR date(valid_to) >= date(?)) ORDER BY valid_from DESC",
        (company_id, comp_target, comp_target),
    ).fetchall():
        key = normalize_whitespace(r["person_name"])
        if key and key not in seller_unit_map:
            seller_unit_map[key] = normalize_unit(r["base_unit"]) or ""

    # Escopo pelo perfil (não pelo nome do papel): a Missão do Dia é uma visão de CRM,
    # então mesmo "unidade + consolidado" fica restrito às unidades vinculadas.
    allowed_units = crm_allowed_units_for_user(conn, user) or []
    contacts_map = {normalize_whitespace(r["seller_name"]): {"total": int(r["total"]), "active": int(r["active"])} for r in contacts_rows}
    overdue_map = {normalize_whitespace(r["seller_name"]): int(r["overdue"]) for r in tasks_rows}

    results = []
    for row in seller_rows:
        seller_name = normalize_whitespace(row["seller_name"])
        if not seller_name:
            continue
        # Unidade da meta tem prioridade; people_records é o complemento
        unit = normalize_unit(row["base_unit"]) or seller_unit_map.get(seller_name, "")
        if allowed_units and unit not in allowed_units:
            continue
        c = contacts_map.get(seller_name, {"total": 0, "active": 0})
        results.append({
            "sellerName": seller_name,
            "unit": unit,
            "contactsToday": c["active"],
            "totalInteractionsToday": c["total"],
            "overdueTasks": overdue_map.get(seller_name, 0),
            "openTasks": open_map.get(seller_name, 0),
            "lastInteractionAt": last_interaction_map.get(seller_name),
            "dailyGoal": DAILY_CONTACT_GOAL,
        })

    # Quem não trabalhou aparece primeiro — é onde o gerente precisa agir
    results.sort(key=lambda r: (r["contactsToday"], -r["overdueTasks"]))
    team_goal = len(results) * DAILY_CONTACT_GOAL
    total_contacts = sum(r["contactsToday"] for r in results)
    return {
        "date": today_str,
        "sellers": results,
        "totalContactsToday": total_contacts,
        "teamGoal": team_goal,
        "dailyGoalPerSeller": DAILY_CONTACT_GOAL,
        "sellersWithContact": sum(1 for r in results if r["contactsToday"] > 0),
        "sellersWithoutContact": sum(1 for r in results if r["contactsToday"] == 0),
        "totalOverdueTasks": sum(r["overdueTasks"] for r in results),
        "goalPct": round(total_contacts / team_goal * 100, 1) if team_goal > 0 else 0.0,
    }


def compute_portfolio_summary_by_seller(
    conn: sqlite3.Connection, company_id: int, user: sqlite3.Row,
    competence: str | None = None, unit_filter: str | list[str] | None = None,
    person_type_filter: str | None = None,
) -> dict[str, Any]:
    """Retorna resumo da carteira por vendedor para dashboard gerencial.

    Baseia a contagem de clientes em crm_client_profiles (relatório de cadastro),
    independente de importações de faturamento. Calcula status a partir da compra
    mais recente em crm_client_summary (qualquer competência), com fallback para
    last_sale_at do perfil.
    """
    today = date.today()
    # unit_filter aceita string única ou lista (gerente pode ter várias unidades).
    # None = sem restrição.
    if unit_filter is None:
        unit_filter_set = None
    else:
        values = [unit_filter] if isinstance(unit_filter, str) else list(unit_filter)
        unit_filter_set = {normalize_unit(v) for v in values if v}
    # Usa a competência mais recente com dados de CRM como padrão
    if not competence:
        competence = crm_summary_latest_competence(conn, company_id) or today.strftime("%Y-%m")
    # Calcula mês anterior relativo à competência solicitada
    comp_year, comp_month = int(competence[:4]), int(competence[5:7])
    if comp_month == 1:
        prev_competence = f"{comp_year - 1}-12"
    else:
        prev_competence = f"{comp_year}-{comp_month - 1:02d}"

    # Busca todos os clientes do cadastro, enriquecidos com:
    # - data de compra mais recente (pré-agregada via CTE para evitar subconsulta correlacionada)
    # - receita no mês atual e anterior (para comVendaMes e queda)
    rows = conn.execute(
        """
        WITH latest_purchase AS (
            SELECT client_code, MAX(last_purchase_at) AS latest_purchase_at
            FROM crm_client_summary
            WHERE company_id = ?
            GROUP BY client_code
        ),
        seller_units AS (
            SELECT person_name, base_unit,
                ROW_NUMBER() OVER (PARTITION BY company_id, person_name ORDER BY valid_from DESC) AS rn
            FROM people_records
            WHERE company_id = ?
        )
        SELECT
            COALESCE(NULLIF(TRIM(p.internal_seller_name), ''), 'Sem Vendedor') AS seller,
            COALESCE(su.base_unit, '') AS seller_unit,
            COALESCE(lp.latest_purchase_at, p.last_sale_at) AS effective_last_sale,
            COALESCE(cs.net_value, 0) AS current_revenue,
            COALESCE(cs_prev.net_value, 0) AS prev_revenue,
            p.document_number AS document_number,
            CASE WHEN COALESCE(cs.net_value, 0) > 0 THEN 1 ELSE 0 END AS bought_current,
            CASE WHEN COALESCE(cs_prev.net_value, 0) > 0 THEN 1 ELSE 0 END AS bought_prev
        FROM crm_client_profiles p
        LEFT JOIN latest_purchase lp ON lp.client_code = p.client_code
        LEFT JOIN crm_client_summary cs
            ON cs.company_id = p.company_id
            AND cs.client_code = p.client_code
            AND cs.competence = ?
        LEFT JOIN crm_client_summary cs_prev
            ON cs_prev.company_id = p.company_id
            AND cs_prev.client_code = p.client_code
            AND cs_prev.competence = ?
        LEFT JOIN seller_units su
            ON su.person_name = COALESCE(NULLIF(TRIM(p.internal_seller_name), ''), 'Sem Vendedor')
            AND su.rn = 1
        WHERE p.company_id = ?
        """,
        (company_id, company_id, competence, prev_competence, company_id),
    ).fetchall()

    by_seller: dict[str, dict[str, Any]] = {}

    for row in rows:
        seller = row["seller"]
        unit = row["seller_unit"] or ""

        # Aplica filtro por unidade no backend (case-insensitive)
        if unit_filter_set is not None and normalize_unit(unit) not in unit_filter_set:
            continue

        # Aplica filtro por tipo de pessoa (PJ/PF)
        if person_type_filter:
            doc_pt, _ = person_type_from_document(row["document_number"])
            if not doc_pt:
                doc_pt, _, _ = infer_person_type_from_name(row["seller"])
            if normalize_upper(doc_pt) != normalize_upper(person_type_filter):
                continue

        if seller not in by_seller:
            by_seller[seller] = {
                "sellerName": seller, "unit": unit,
                "total": 0, "ativos": 0, "preInativos": 0, "inativos": 0,
                "comVendaMes": 0, "semVendaMes": 0, "comVendaMesAnterior": 0,
                "queda30": 0, "queda20": 0, "queda10": 0,
            }
        d = by_seller[seller]
        d["total"] += 1

        # Status a partir da data de compra mais recente (crm_client_summary ou perfil)
        last_sale = row["effective_last_sale"]
        if last_sale:
            try:
                last_date = date.fromisoformat(str(last_sale)[:10])
                days_since = (today - last_date).days
                if days_since <= 29:
                    d["ativos"] += 1
                elif days_since <= 60:
                    d["preInativos"] += 1
                else:
                    d["inativos"] += 1
            except (ValueError, TypeError):
                d["inativos"] += 1
        else:
            d["inativos"] += 1

        if row["bought_current"]:
            d["comVendaMes"] += 1
        else:
            d["semVendaMes"] += 1

        if row["bought_prev"]:
            d["comVendaMesAnterior"] += 1

        # Queda de faturamento: somente clientes que compraram nos dois meses
        cur_rev = float(row["current_revenue"] or 0)
        prev_rev = float(row["prev_revenue"] or 0)
        if cur_rev > 0 and prev_rev > 0:
            growth_pct = (cur_rev - prev_rev) / prev_rev * 100
            if growth_pct < -30:
                d["queda30"] += 1
            elif growth_pct < -20:
                d["queda20"] += 1
            elif growth_pct < -10:
                d["queda10"] += 1

    result = sorted(by_seller.values(), key=lambda r: r["total"], reverse=True)
    for d in result:
        t = max(d["total"], 1)
        d["pctAtivos"] = round(d["ativos"] / t * 100, 1)
        d["pctPreInativos"] = round(d["preInativos"] / t * 100, 1)
        d["pctInativos"] = round(d["inativos"] / t * 100, 1)
        d["pctComVendaMes"] = round(d["comVendaMes"] / t * 100, 1)

    totals: dict[str, Any] = {k: sum(d[k] for d in result) for k in ("total", "ativos", "preInativos", "inativos", "comVendaMes", "semVendaMes", "comVendaMesAnterior", "queda30", "queda20", "queda10")}
    t2 = max(totals["total"], 1)
    totals["pctAtivos"] = round(totals["ativos"] / t2 * 100, 1)
    totals["pctPreInativos"] = round(totals["preInativos"] / t2 * 100, 1)
    totals["pctInativos"] = round(totals["inativos"] / t2 * 100, 1)
    totals["pctComVendaMes"] = round(totals["comVendaMes"] / t2 * 100, 1)

    return {
        "competence": competence,
        "prevCompetence": prev_competence,
        "sellers": result,
        "totals": totals,
    }


class AppHandler(BaseHTTPRequestHandler):
    server_version = "PassiniDashboard/1.0"

    def log_message(self, format: str, *args) -> None:
        return

    def handle(self) -> None:
        try:
            super().handle()
        except Exception:
            traceback.print_exc()
            raise

    def handle_one_request(self) -> None:
        try:
            super().handle_one_request()
        except Exception:
            traceback.print_exc()
            raise

    def _set_headers(self, status: int = 200, content_type: str = "application/json; charset=utf-8", extra_headers: dict[str, str] | None = None) -> None:
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Cache-Control", "no-store")
        if extra_headers:
            for key, value in extra_headers.items():
                self.send_header(key, value)
        self.end_headers()

    def _read_json(self) -> dict[str, Any]:
        length = int(self.headers.get("Content-Length", "0"))
        raw = self.rfile.read(length) if length else b"{}"
        return json.loads(raw.decode("utf-8") or "{}")

    def _parse_multipart(self) -> tuple[list[dict[str, Any]], dict[str, str]]:
        environ = {"REQUEST_METHOD": "POST", "CONTENT_TYPE": self.headers.get("Content-Type", "")}
        form = cgi.FieldStorage(fp=self.rfile, headers=self.headers, environ=environ, keep_blank_values=True)
        files: list[dict[str, Any]] = []
        fields: dict[str, str] = {}
        if form.list:
            for item in form.list:
                if item.filename:
                    files.append({"fieldName": item.name, "fileName": item.filename, "content": item.file.read()})
                else:
                    fields[item.name] = item.value
        return files, fields

    def _serve_file(self, file_path: Path, content_type: str) -> None:
        if not file_path.exists():
            self._set_headers(404)
            self.wfile.write(json_dumps({"error": "Arquivo não encontrado"}))
            return
        self._set_headers(200, content_type)
        self.wfile.write(file_path.read_bytes())

    def _current_user(self) -> dict[str, Any] | None:
        cookie = SimpleCookie(self.headers.get("Cookie"))
        session_cookie = cookie.get(SESSION_COOKIE)
        if not session_cookie:
            return None
        session_id = session_cookie.value
        with closing(get_connection()) as conn:
            row = conn.execute(
                """
                SELECT users.*
                FROM sessions
                JOIN users ON users.id = sessions.user_id
                WHERE sessions.id = ? AND datetime(sessions.expires_at) >= datetime(?)
                """,
                (session_id, now_iso()),
            ).fetchone()
            return dict(row) if row else None

    def _require_auth(self) -> dict[str, Any] | None:
        user = self._current_user()
        if not user:
            self._set_headers(401)
            self.wfile.write(json_dumps({"error": "Sessão expirada"}))
            return None
        return user

    # Módulos que caracterizam a área administrativa — basta ter um deles no perfil
    _ADMIN_AREA_MODULES = {"configuracoes", "administracao", "importacoes", "acessos"}

    def _require_admin_area(self, user: dict[str, Any] | None) -> bool:
        if not user:
            return False
        with closing(get_connection()) as conn:
            profile = get_access_profile_for_user(conn, user)
        if profile is not None:
            if not (set(profile["modules"]) & self._ADMIN_AREA_MODULES):
                self._set_headers(403)
                self.wfile.write(json_dumps(
                    {"error": f"O perfil '{profile['name']}' não tem acesso à área administrativa."}
                ))
                return False
            return True
        # Sem perfil cadastrado: mantém a regra antiga
        if user["role"] == "Vendedor":
            self._set_headers(403)
            self.wfile.write(json_dumps({"error": "Perfil sem acesso a area administrativa"}))
            return False
        return True

    def _require_unit_allowed(self, user: dict[str, Any] | None, unit_name: str | None) -> bool:
        """Impede gravar dados de unidade fora do vínculo do usuário."""
        if not user:
            return False
        with closing(get_connection()) as conn:
            scope = data_scope_for_user(conn, user)
            if scope not in {"unidade", "unidade_consolidado"}:
                return True
            allowed = linked_units_for_user(user)
        target = normalize_unit(unit_name)
        if target and target in allowed:
            return True
        self._set_headers(403)
        self.wfile.write(json_dumps(
            {"error": f"Seu perfil só permite alterar dados de: {', '.join(allowed) or 'nenhuma unidade'}."}
        ))
        return False

    def _require_user_management(self, user: dict[str, Any] | None) -> bool:
        """Gestão de usuários e perfis é restrita a quem tem a permissão no perfil."""
        if not user:
            return False
        with closing(get_connection()) as conn:
            allowed = user_can_manage_users(conn, user)
        if not allowed:
            self._set_headers(403)
            self.wfile.write(json_dumps(
                {"error": "Seu perfil não permite gerenciar usuários. Fale com o Diretor ou Administrador."}
            ))
            return False
        return True

    def do_OPTIONS(self) -> None:
        self.send_response(204)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def do_GET(self) -> None:
        _t0 = time.time()
        try:
            self._do_GET_inner()
        finally:
            _elapsed = time.time() - _t0
            if _elapsed > 1.0 and "/api/" in self.path:
                print(f"[req] {_elapsed:6.1f}s  GET {self.path}", flush=True)

    def _do_GET_inner(self) -> None:
        try:
            parsed = urlparse(self.path)
            path = parsed.path
            if path == "/":
                self._serve_file(STATIC_DIR / "index.html", "text/html; charset=utf-8")
                return
            if path == "/app.js":
                self._serve_file(STATIC_DIR / "app.js", "application/javascript; charset=utf-8")
                return
            if path == "/styles.css":
                self._serve_file(STATIC_DIR / "styles.css", "text/css; charset=utf-8")
                return
            if path == "/api/health":
                self._set_headers(200)
                self.wfile.write(json_dumps({"ok": True, "timestamp": now_iso(), "build": "v20260602-agenda-fix"}))
                return
            if path == "/api/debug/data-summary":
                user = self._require_auth()
                if not user:
                    return
                conn = get_db()
                cid = user["company_id"]
                def q(sql, *p):
                    return [dict(r) for r in conn.execute(sql, p).fetchall()]
                result = {
                    "db_path": str(DB_PATH),
                    "db_size_mb": round(DB_PATH.stat().st_size / 1024 / 1024, 2) if DB_PATH.exists() else 0,
                    "fact_sales_detail": q("SELECT competence, COUNT(DISTINCT client_name) AS clientes, COUNT(DISTINCT seller_name) AS vendedores, ROUND(SUM(net_value),2) AS total FROM fact_sales_detail WHERE company_id=? GROUP BY competence ORDER BY competence", cid),
                    "fact_vendor_summary": q("SELECT competence, COUNT(*) AS linhas, ROUND(SUM(sale_value),2) AS total FROM fact_vendor_summary WHERE company_id=? GROUP BY competence ORDER BY competence", cid),
                    "crm_client_summary": q("SELECT competence, COUNT(DISTINCT client_code) AS clientes, SUM(CASE WHEN net_value>0 THEN 1 ELSE 0 END) AS com_valor, ROUND(SUM(net_value),2) AS total FROM crm_client_summary WHERE company_id=? GROUP BY competence ORDER BY competence", cid),
                    "crm_client_profiles": q("SELECT COUNT(*) AS total FROM crm_client_profiles WHERE company_id=?", cid),
                    "fact_unit_summary": q("SELECT competence, COUNT(*) AS linhas FROM fact_unit_summary WHERE company_id=? GROUP BY competence ORDER BY competence", cid),
                    "imports_recentes": q("SELECT file_type, competence, status, created_at FROM imports WHERE company_id=? ORDER BY created_at DESC LIMIT 20", cid),
                }
                conn.close()
                self._set_headers(200)
                self.wfile.write(json_dumps(result))
                return
            if path == "/api/session":
                user = self._current_user()
                if not user:
                    self._set_headers(200)
                    self.wfile.write(json_dumps({"authenticated": False}))
                    return
                with closing(get_connection()) as conn:
                    profile = get_access_profile_for_user(conn, user)
                self._set_headers(200)
                self.wfile.write(
                    json_dumps(
                        {
                            "authenticated": True,
                            "user": {
                                "username": user["username"],
                                "fullName": user["full_name"],
                                "linkedPersonName": user["linked_person_name"],
                                "linkedUnits": linked_units_for_user(user),
                                "role": user["role"],
                                # Permissões vindas do perfil — a tela usa isso para montar o menu
                                "profileName": profile["name"] if profile else user["role"],
                                "modules": profile["modules"] if profile else [],
                                "dataScope": profile["dataScope"] if profile else "todos",
                                "canManageUsers": profile["canManageUsers"] if profile else False,
                            },
                        }
                    )
                )
                return
            if path == "/api/options":
                user = self._require_auth()
                if not user:
                    return
                with closing(get_connection()) as conn:
                    company_id = user["company_id"]
                    competences = query_competences(conn, company_id)
                    if user["role"] == "Vendedor":
                        seller_name = seller_identity_for_user(user)
                        _, base_unit = current_role_and_unit(conn, company_id, seller_name, competences[0] if competences else date.today().strftime("%Y-%m"))
                        units = [normalize_unit(base_unit)] if base_unit else []
                        sellers = [seller_name]
                        cities = [
                            row["city_name"]
                            for row in conn.execute(
                                "SELECT DISTINCT city_name FROM fact_sales_detail WHERE company_id = ? AND seller_name = ? AND city_name IS NOT NULL AND city_name <> '' ORDER BY city_name",
                                (company_id, seller_name),
                            ).fetchall()
                        ]
                    elif user["role"] in {"Gerente", "Analista"}:
                        linked_units = linked_units_for_user(user)
                        if linked_units:
                            units = linked_units
                            seller_competence = competences[0] if competences else date.today().strftime("%Y-%m")
                            sellers = []
                            for row in conn.execute(
                                "SELECT DISTINCT seller_name FROM fact_vendor_summary WHERE company_id = ? ORDER BY seller_name",
                                (company_id,),
                            ).fetchall():
                                seller_name = normalize_whitespace(row["seller_name"])
                                _, seller_base_unit = current_role_and_unit(conn, company_id, seller_name, seller_competence)
                                if normalize_unit(seller_base_unit) in linked_units:
                                    sellers.append(seller_name)
                            cities = active_mapped_cities_for_units(conn, company_id, linked_units)
                        else:
                            units = []
                            sellers = []
                            cities = []
                    else:
                        _db_units = {normalize_unit(row["unit_name"]) for row in conn.execute("SELECT DISTINCT unit_name FROM fact_unit_summary WHERE company_id = ?", (company_id,)).fetchall() if row["unit_name"]}
                        _all_units = list(dict.fromkeys([u for u in CANONICAL_UNITS if u in _db_units or True] + sorted(_db_units - set(CANONICAL_UNITS))))
                        units = _all_units
                        sellers = [row["seller_name"] for row in conn.execute("SELECT DISTINCT seller_name FROM fact_vendor_summary WHERE company_id = ? ORDER BY seller_name", (company_id,)).fetchall()]
                        cities = [row["city_name"] for row in conn.execute("SELECT DISTINCT city_name FROM fact_sales_detail WHERE company_id = ? AND city_name IS NOT NULL AND city_name <> '' ORDER BY city_name", (company_id,)).fetchall()]
                    # Mapeia vendedor → unidade base via people_records
                    seller_unit_map: dict[str, str | None] = {}
                    for r in conn.execute(
                        "SELECT person_name, base_unit FROM people_records WHERE company_id = ? AND valid_to IS NULL ORDER BY valid_from DESC",
                        (company_id,),
                    ).fetchall():
                        pname = normalize_whitespace(r["person_name"])
                        if pname and pname not in seller_unit_map:
                            seller_unit_map[pname] = normalize_whitespace(r["base_unit"])
                    sellers_with_units = [{"name": s, "unit": seller_unit_map.get(s)} for s in sellers]
                    self._set_headers(200)
                    self.wfile.write(json_dumps({"competences": competences, "units": units, "sellers": sellers, "sellersWithUnits": sellers_with_units, "cities": cities}))
                return
            if path == "/api/dashboard":
                user = self._require_auth()
                if not user:
                    return
                query = parse_qs(parsed.query)
                with closing(get_connection()) as conn:
                    filters = scoped_filters_for_user(conn, user["company_id"], user, build_filters_from_query(query))
                    data = get_dashboard_data_cached(conn, user["company_id"], filters)
                self._set_headers(200)
                self.wfile.write(json_dumps(data))
                return
            if path == "/api/audit/integrity":
                user = self._require_auth()
                if not user:
                    return
                query = parse_qs(parsed.query)
                with closing(get_connection()) as conn:
                    competence = normalize_whitespace(query.get("competence", [None])[0]) or (
                        query_competences(conn, user["company_id"])[0] if query_competences(conn, user["company_id"]) else date.today().strftime("%Y-%m")
                    )
                    audit_result = build_integrity_audit(conn, user["company_id"], competence)
                self._set_headers(200)
                self.wfile.write(json_dumps(audit_result))
                return
            if path == "/api/crm/options":
                user = self._require_auth()
                if not user:
                    return
                self._set_headers(200)
                self.wfile.write(
                    json_dumps(
                        {
                            "contactTypes": [{"code": code, "label": label} for code, label in CRM_CONTACT_TYPES],
                            "contactResults": [
                                {
                                    "code": code,
                                    "label": label,
                                    "generatesFollowup": bool(generates_followup),
                                    "requiresFollowupDate": bool(requires_followup_date),
                                }
                                for code, label, generates_followup, requires_followup_date in CRM_CONTACT_RESULTS
                            ],
                        }
                    )
                )
                return
            if path == "/api/crm/seller-score":
                user = self._require_auth()
                if not user:
                    return
                query = parse_qs(parsed.query)
                req_comp = normalize_whitespace(query.get("competence", [None])[0])
                with closing(get_connection()) as conn:
                    score_data = compute_seller_score(conn, user["company_id"], user, req_comp or None)
                self._set_headers(200)
                self.wfile.write(json_dumps(score_data))
                return
            if path == "/api/crm/team-score":
                user = self._require_auth()
                if not user:
                    return
                try:
                    with closing(get_connection()) as conn:
                        team_data = compute_team_score(conn, user["company_id"], user)
                    self._set_headers(200)
                    self.wfile.write(json_dumps(team_data))
                except Exception as _e:
                    traceback.print_exc()
                    self._set_headers(500)
                    self.wfile.write(json_dumps({"error": str(_e), "sellers": [], "summary": {"total": 0, "eligible": 0, "inPrizeZone": 0, "fullPrize": 0}, "competence": ""}))
                return
            if path == "/api/crm/team-activity-today":
                # Painel de gestão da Missão do Dia. Gerente precisa dele, então não é
                # tratado como área administrativa — o recorte por unidade já limita.
                user = self._require_auth()
                if not user:
                    return
                try:
                    with closing(get_connection()) as conn:
                        if data_scope_for_user(conn, user) == "proprio":
                            self._set_headers(403)
                            self.wfile.write(json_dumps({"error": "Visão exclusiva de gestão."}))
                            return
                        data = compute_team_activity_today(conn, user["company_id"], user)
                        query = parse_qs(parsed.query)
                        filters = crm_scoped_filters_for_user(
                            conn, user["company_id"], user, build_filters_from_query(query)
                        )
                        data["risk"] = compute_manager_mission(conn, user["company_id"], user, filters)
                        data["scopeUnits"] = crm_allowed_units_for_user(conn, user)
                    self._set_headers(200)
                    self.wfile.write(json_dumps(data))
                except Exception as _e:
                    traceback.print_exc()
                    self._set_headers(500)
                    self.wfile.write(json_dumps({"error": str(_e), "sellers": [], "totalContactsToday": 0, "teamGoal": 0}))
                return
            if path == "/api/auto-import/status":
                user = self._require_auth()
                if not user:
                    return
                if not self._require_admin_area(user):
                    return
                try:
                    with closing(get_connection()) as conn:
                        rows = conn.execute(
                            "SELECT ran_at, folder, scope, competence, status, message, files_json "
                            "FROM auto_import_log ORDER BY ran_at DESC LIMIT 50"
                        ).fetchall()
                    logs = [
                        {
                            "ranAt": r["ran_at"], "folder": r["folder"], "scope": r["scope"],
                            "competence": r["competence"], "status": r["status"],
                            "message": r["message"], "files": json.loads(r["files_json"] or "[]"),
                        }
                        for r in rows
                    ]
                    folders_info = []
                    for cfg in AUTO_IMPORT_FOLDERS:
                        p = AUTO_IMPORT_BASE / cfg["folder"]
                        pending = [f.name for f in p.glob("*.csv")] if p.exists() else []
                        folders_info.append({
                            "folder": cfg["folder"], "label": cfg["label"],
                            "scope": cfg["scope"], "path": str(p),
                            "hint": cfg.get("hint", ""),
                            "pendingFiles": pending,
                        })
                    self._set_headers(200)
                    self.wfile.write(json_dumps({
                        "logs": logs,
                        "folders": folders_info,
                        "intervalMinutes": AUTO_IMPORT_INTERVAL // 60,
                        "running": _AUTO_IMPORT_RUNNING.is_set(),
                    }))
                except Exception as exc:
                    traceback.print_exc()
                    self._set_headers(500)
                    self.wfile.write(json_dumps({"error": str(exc)}))
                return
            if path == "/api/crm/unassigned-clients":
                # Clientes recorrentes sem vendedor no cadastro — visão de gestão
                user = self._require_auth()
                if not user:
                    return
                try:
                    query = parse_qs(parsed.query)
                    min_months = max(1, min(int(query.get("minMonths", ["2"])[0]), 12))
                    window = max(2, min(int(query.get("window", ["6"])[0]), 24))
                    with closing(get_connection()) as conn:
                        if data_scope_for_user(conn, user) == "proprio":
                            self._set_headers(403)
                            self.wfile.write(json_dumps({"error": "Visão exclusiva de gestão."}))
                            return
                        data = compute_unassigned_clients(
                            conn, user["company_id"], user,
                            min_months=min_months, months_window=window,
                        )
                    self._set_headers(200)
                    self.wfile.write(json_dumps(data))
                except Exception as exc:
                    traceback.print_exc()
                    self._set_headers(500)
                    self.wfile.write(json_dumps({"error": str(exc), "items": [], "total": 0}))
                return
            if path == "/api/content":
                # Biblioteca de conteúdo. Leitura liberada a todos os autenticados —
                # é material de trabalho do vendedor.
                user = self._require_auth()
                if not user:
                    return
                query = parse_qs(parsed.query)
                category = normalize_whitespace(query.get("category", [None])[0]) or None
                situation = normalize_upper(query.get("situation", [None])[0]) or None
                include_inactive = query.get("all", ["0"])[0] == "1"
                with closing(get_connection()) as conn:
                    can_edit = user_can_manage_users(conn, user)
                    items = list_content_library(
                        conn, user["company_id"], category, situation,
                        only_active=not (include_inactive and can_edit),
                    )
                self._set_headers(200)
                self.wfile.write(json_dumps({
                    "items": items,
                    "categories": CONTENT_CATEGORIES,
                    "situations": CONTENT_SITUATIONS,
                    "canEdit": can_edit,
                }))
                return
            if path == "/api/crm/portfolio-summary":
                # Visão de carteira por vendedor: gerente precisa dela. Não é área
                # administrativa — o recorte por unidade é aplicado abaixo.
                user = self._require_auth()
                if not user:
                    return
                try:
                    query = parse_qs(parsed.query)
                    req_competence = query.get("competence", [None])[0] or None
                    req_unit = query.get("unit", [None])[0] or None
                    req_person_type = normalize_upper(query.get("personType", [None])[0]) or None
                    with closing(get_connection()) as conn:
                        req_unit = crm_unit_filter_for_user(conn, user, req_unit)
                        data = compute_portfolio_summary_by_seller(
                            conn, user["company_id"], user,
                            competence=req_competence, unit_filter=req_unit,
                            person_type_filter=req_person_type,
                        )
                    self._set_headers(200)
                    self.wfile.write(json_dumps(data))
                except Exception as _e:
                    traceback.print_exc()
                    self._set_headers(500)
                    self.wfile.write(json_dumps({"error": str(_e), "sellers": [], "totals": {}}))
                return
            if path == "/api/crm/summary":
                user = self._require_auth()
                if not user:
                    return
                query = parse_qs(parsed.query)
                with closing(get_connection()) as conn:
                    filters = crm_scoped_filters_for_user(conn, user["company_id"], user, build_filters_from_query(query))
                    data = crm_summary_for_user(conn, user["company_id"], user, filters)
                self._set_headers(200)
                self.wfile.write(json_dumps(data))
                return
            if path == "/api/crm/agenda":
                user = self._require_auth()
                if not user:
                    return
                query = parse_qs(parsed.query)
                limit = max(1, min(int(query.get("limit", ["20"])[0]), 50))
                with closing(get_connection()) as conn:
                    filters = crm_scoped_filters_for_user(conn, user["company_id"], user, build_filters_from_query(query))
                    clients = list_crm_clients(conn, user["company_id"], filters, limit, exclude_contacted_today=True)
                self._set_headers(200)
                self.wfile.write(
                    json_dumps(
                        {
                            "top5": clients[:5],
                            "extended": clients[5:limit],
                            "total": len(clients),
                        }
                    )
                )
                return
            if path == "/api/crm/clients":
                user = self._require_auth()
                if not user:
                    return
                query = parse_qs(parsed.query)
                with closing(get_connection()) as conn:
                    filters = crm_scoped_filters_for_user(conn, user["company_id"], user, build_filters_from_query(query))
                    clients = query_crm_clients_page(
                        conn,
                        user["company_id"],
                        filters,
                        parse_int(query.get("page", [1])[0]) or 1,
                        parse_int(query.get("pageSize", [50])[0]) or 50,
                    )
                print(
                    "[CRM CLIENTS DEBUG]",
                    {
                        "total": clients["total"],
                        "page": clients["page"],
                        "pageSize": clients["pageSize"],
                        "totalPages": clients["totalPages"],
                        "rowsReturned": len(clients["rows"]),
                    },
                )
                self._set_headers(200)
                self.wfile.write(json_dumps(clients))
                return
            if path == "/api/crm/client":
                user = self._require_auth()
                if not user:
                    return
                query = parse_qs(parsed.query)
                client_key = normalize_client_key(query.get("clientKey", [None])[0])
                if not client_key:
                    self._set_headers(400)
                    self.wfile.write(json_dumps({"error": "Informe clientKey"}))
                    return
                with closing(get_connection()) as conn:
                    filters = scoped_filters_for_user(conn, user["company_id"], user, build_filters_from_query(query))
                    data = get_crm_client_360(conn, user["company_id"], filters, client_key)
                if not data:
                    self._set_headers(404)
                    self.wfile.write(json_dumps({"error": "Cliente nao encontrado"}))
                    return
                payload = json_dumps(data)
                self._set_headers(200)
                self.wfile.write(payload)
                return
            if path == "/api/crm/client/summary":
                user = self._require_auth()
                if not user:
                    return
                query = parse_qs(parsed.query)
                client_key = normalize_client_key(query.get("clientKey", [None])[0])
                if not client_key:
                    self._set_headers(400)
                    self.wfile.write(json_dumps({"error": "Informe clientKey"}))
                    return
                with closing(get_connection()) as conn:
                    filters = crm_scoped_filters_for_user(conn, user["company_id"], user, build_filters_from_query(query))
                    data = get_crm_client_summary(
                        conn, user["company_id"], filters, client_key,
                        seller_name=user["full_name"] or user["username"],
                    )
                if not data:
                    self._set_headers(404)
                    self.wfile.write(json_dumps({"error": "Cliente nao encontrado"}))
                    return
                payload = json_dumps(data)
                self._set_headers(200)
                self.wfile.write(payload)
                return
            if path == "/api/crm/client/interactions":
                user = self._require_auth()
                if not user:
                    return
                query = parse_qs(parsed.query)
                client_key = normalize_client_key(query.get("clientKey", [None])[0])
                if not client_key:
                    self._set_headers(400)
                    self.wfile.write(json_dumps({"error": "Informe clientKey"}))
                    return
                with closing(get_connection()) as conn:
                    filters = scoped_filters_for_user(conn, user["company_id"], user, build_filters_from_query(query))
                    data = get_crm_client_interactions(
                        conn,
                        user["company_id"],
                        filters,
                        client_key,
                        parse_int(query.get("page", [1])[0]) or 1,
                        parse_int(query.get("pageSize", [20])[0]) or 20,
                    )
                if not data:
                    self._set_headers(404)
                    self.wfile.write(json_dumps({"error": "Cliente nao encontrado"}))
                    return
                self._set_headers(200)
                self.wfile.write(json_dumps(data))
                return
            if path == "/api/crm/client/purchases":
                user = self._require_auth()
                if not user:
                    return
                query = parse_qs(parsed.query)
                client_key = normalize_client_key(query.get("clientKey", [None])[0])
                if not client_key:
                    self._set_headers(400)
                    self.wfile.write(json_dumps({"error": "Informe clientKey"}))
                    return
                with closing(get_connection()) as conn:
                    filters = scoped_filters_for_user(conn, user["company_id"], user, build_filters_from_query(query))
                    data = get_crm_client_purchases(conn, user["company_id"], filters, client_key)
                if data is None:
                    self._set_headers(404)
                    self.wfile.write(json_dumps({"error": "Cliente nao encontrado"}))
                    return
                self._set_headers(200)
                self.wfile.write(json_dumps({"rows": data}))
                return
            if path == "/api/crm/client/items":
                user = self._require_auth()
                if not user:
                    return
                query = parse_qs(parsed.query)
                client_key = normalize_client_key(query.get("clientKey", [None])[0])
                if not client_key:
                    self._set_headers(400)
                    self.wfile.write(json_dumps({"error": "Informe clientKey"}))
                    return
                with closing(get_connection()) as conn:
                    filters = scoped_filters_for_user(conn, user["company_id"], user, build_filters_from_query(query))
                    data = get_crm_client_items(
                        conn,
                        user["company_id"],
                        filters,
                        client_key,
                        parse_int(query.get("page", [1])[0]) or 1,
                        parse_int(query.get("pageSize", [20])[0]) or 20,
                    )
                if not data:
                    self._set_headers(404)
                    self.wfile.write(json_dumps({"error": "Cliente nao encontrado"}))
                    return
                self._set_headers(200)
                self.wfile.write(json_dumps(data))
                return
            if path == "/api/crm/client/tasks":
                user = self._require_auth()
                if not user:
                    return
                query = parse_qs(parsed.query)
                client_key = normalize_client_key(query.get("clientKey", [None])[0])
                if not client_key:
                    self._set_headers(400)
                    self.wfile.write(json_dumps({"error": "Informe clientKey"}))
                    return
                with closing(get_connection()) as conn:
                    filters = scoped_filters_for_user(conn, user["company_id"], user, build_filters_from_query(query))
                    data = get_crm_client_tasks(conn, user["company_id"], filters, client_key)
                if data is None:
                    self._set_headers(404)
                    self.wfile.write(json_dumps({"error": "Cliente nao encontrado"}))
                    return
                self._set_headers(200)
                self.wfile.write(json_dumps({"rows": data}))
                return
            if path == "/api/crm/tasks":
                user = self._require_auth()
                if not user:
                    return
                query = parse_qs(parsed.query)
                status_filter = normalize_upper(query.get("status", [None])[0])
                seller_name = seller_identity_for_user(user) if user["role"] == "Vendedor" else normalize_whitespace(query.get("seller", [None])[0])
                sql = """
                    SELECT id, client_key, client_name, seller_name, title, description, due_at, status, source_interaction_id, created_at, completed_at
                    FROM crm_tasks
                    WHERE company_id = ?
                """
                params: list[Any] = [user["company_id"]]
                with closing(get_connection()) as conn:
                    if user["role"] in {"Gerente", "Analista"}:
                        linked_units = linked_units_for_user(user)
                        if linked_units:
                            allowed_sellers: list[str] = []
                            seller_competence = query_competences(conn, user["company_id"])
                            seller_competence = seller_competence[0] if seller_competence else date.today().strftime("%Y-%m")
                            for row in conn.execute(
                                "SELECT DISTINCT seller_name FROM crm_tasks WHERE company_id = ?",
                                (user["company_id"],),
                            ).fetchall():
                                current_seller = normalize_whitespace(row["seller_name"])
                                _, seller_base_unit = current_role_and_unit(conn, user["company_id"], current_seller, seller_competence)
                                if normalize_unit(seller_base_unit) in linked_units:
                                    allowed_sellers.append(current_seller)
                            if seller_name:
                                if seller_name not in allowed_sellers:
                                    allowed_sellers = []
                                else:
                                    allowed_sellers = [seller_name]
                            if allowed_sellers:
                                placeholders = ", ".join("?" for _ in allowed_sellers)
                                sql += f" AND seller_name IN ({placeholders})"
                                params.extend(allowed_sellers)
                            else:
                                sql += " AND 1 = 0"
                        else:
                            sql += " AND 1 = 0"
                    elif seller_name:
                        sql += " AND seller_name = ?"
                        params.append(seller_name)
                    if status_filter:
                        sql += " AND status = ?"
                        params.append(status_filter)
                    else:
                        sql += " AND status NOT IN ('CONCLUIDA', 'CANCELADA')"
                    sql += " ORDER BY CASE status WHEN 'ATRASADA' THEN 0 WHEN 'ABERTA' THEN 1 WHEN 'REAGENDADA' THEN 2 ELSE 3 END, datetime(due_at) ASC"
                    rows = [dict(row) for row in conn.execute(sql, params).fetchall()]
                self._set_headers(200)
                self.wfile.write(json_dumps({"rows": rows, "total": len(rows)}))
                return
            if path == "/api/crm/agenda/actions":
                user = self._require_auth()
                if not user:
                    return
                if self.command != "POST":
                    self._set_headers(405)
                    self.wfile.write(json_dumps({"error": "Metodo nao permitido"}))
                    return
            if path == "/api/admin/all":
                # Payload usado por várias telas (pessoas, metas, mapeamentos). Perfis sem
                # gestão de usuários recebem a versão sem dados sensíveis.
                user = self._require_auth()
                if not user:
                    return
                with closing(get_connection()) as conn:
                    if data_scope_for_user(conn, user) == "proprio":
                        self._set_headers(403)
                        self.wfile.write(json_dumps({"error": "Perfil sem acesso a esses dados."}))
                        return
                    data = list_admin_data(conn, user["company_id"])
                    data = filter_admin_data_for_user(conn, user["company_id"], user, data)
                    if not user_can_manage_users(conn, user):
                        for sensitive in ("users", "profiles", "audit"):
                            data[sensitive] = []
                self._set_headers(200)
                self.wfile.write(json_dumps(data))
                return
            if path.startswith("/api/templates/"):
                user = self._require_auth()
                if not user or not self._require_admin_area(user):
                    return
                kind = path.split("/")[-1]
                content = csv_template(kind)
                self._set_headers(
                    200,
                    "text/csv; charset=utf-8",
                    {"Content-Disposition": f'attachment; filename="{kind}_template.csv"'},
                )
                self.wfile.write(content)
                return
            if path == "/api/export.xlsx":
                user = self._require_auth()
                if not user:
                    return
                query = parse_qs(parsed.query)
                with closing(get_connection()) as conn:
                    filters = scoped_filters_for_user(conn, user["company_id"], user, build_filters_from_query(query))
                    data = get_dashboard_data(conn, user["company_id"], filters)
                content = export_dashboard_xlsx(data)
                self._set_headers(
                    200,
                    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    {"Content-Disposition": 'attachment; filename="dashboard_passini.xlsx"'},
                )
                self.wfile.write(content)
                return
            if path == "/api/export.pdf":
                user = self._require_auth()
                if not user:
                    return
                query = parse_qs(parsed.query)
                with closing(get_connection()) as conn:
                    filters = scoped_filters_for_user(conn, user["company_id"], user, build_filters_from_query(query))
                    data = get_dashboard_data(conn, user["company_id"], filters)
                content = export_dashboard_pdf(data)
                self._set_headers(200, "application/pdf", {"Content-Disposition": 'attachment; filename="dashboard_passini.pdf"'})
                self.wfile.write(content)
                return
            if path == "/api/backup/database":
                user = self._require_auth()
                if not user or not self._require_admin_area(user):
                    return
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                self._set_headers(
                    200,
                    "application/octet-stream",
                    {"Content-Disposition": f'attachment; filename="passini_dashboard_backup_{timestamp}.db"'},
                )
                self.wfile.write(DB_PATH.read_bytes())
                return
            self._set_headers(404)
            self.wfile.write(json_dumps({"error": "Rota não encontrada"}))
        except Exception as exc:
            traceback.print_exc()
            self._set_headers(500)
            self.wfile.write(json_dumps({"error": f"Erro interno: {exc}"}))

    def do_POST(self) -> None:
        try:
            parsed = urlparse(self.path)
            path = parsed.path
            if path == "/api/login":
                payload = self._read_json()
                username = payload.get("username", "")
                password = payload.get("password", "")
                with closing(get_connection()) as conn:
                    user = conn.execute("SELECT * FROM users WHERE username = ? AND is_active = 1", (username,)).fetchone()
                    if not user or not verify_password(password, user["password_hash"], user["password_salt"]):
                        self._set_headers(401)
                        self.wfile.write(json_dumps({"error": "Usuário ou senha inválidos"}))
                        return
                    user = dict(user)
                    session_id = secrets.token_hex(24)
                    expires_at = (datetime.now() + timedelta(hours=SESSION_TTL_HOURS)).isoformat(timespec="seconds")
                    conn.execute("INSERT INTO sessions (id, user_id, created_at, expires_at) VALUES (?, ?, ?, ?)", (session_id, user["id"], now_iso(), expires_at))
                    conn.commit()
                    profile = get_access_profile_for_user(conn, user)
                headers = {"Set-Cookie": f"{SESSION_COOKIE}={session_id}; HttpOnly; Path=/; SameSite=Lax"}
                self._set_headers(200, extra_headers=headers)
                self.wfile.write(
                    json_dumps(
                        {
                            "ok": True,
                            "user": {
                                "username": user["username"],
                                "fullName": user["full_name"],
                                "linkedPersonName": user["linked_person_name"],
                                "linkedUnits": linked_units_for_user(user),
                                "role": user["role"],
                                "profileName": profile["name"] if profile else user["role"],
                                "modules": profile["modules"] if profile else [],
                                "dataScope": profile["dataScope"] if profile else "todos",
                                "canManageUsers": profile["canManageUsers"] if profile else False,
                            },
                        }
                    )
                )
                return
            if path == "/api/logout":
                user = self._current_user()
                cookie = SimpleCookie(self.headers.get("Cookie"))
                session_cookie = cookie.get(SESSION_COOKIE)
                if session_cookie:
                    with closing(get_connection()) as conn:
                        conn.execute("DELETE FROM sessions WHERE id = ?", (session_cookie.value,))
                        conn.commit()
                headers = {"Set-Cookie": f"{SESSION_COOKIE}=deleted; HttpOnly; Path=/; Max-Age=0; SameSite=Lax"}
                self._set_headers(200, extra_headers=headers)
                self.wfile.write(json_dumps({"ok": True}))
                return
            if path == "/api/crm/interactions":
                user = self._require_auth()
                if not user:
                    return
                payload = self._read_json()
                try:
                    with closing(get_connection()) as conn:
                        result = create_crm_interaction(conn, user["company_id"], user, payload)
                except ValueError as exc:
                    self._set_headers(400)
                    self.wfile.write(json_dumps({"error": str(exc)}))
                    return
                self._set_headers(200)
                self.wfile.write(json_dumps({"ok": True, "result": result}))
                return
            if path == "/api/crm/client/contact":
                user = self._require_auth()
                if not user:
                    return
                payload = self._read_json()
                try:
                    with closing(get_connection()) as conn:
                        result = save_crm_client_contact(conn, user["company_id"], user, payload)
                except ValueError as exc:
                    self._set_headers(400)
                    self.wfile.write(json_dumps({"error": str(exc)}))
                    return
                self._set_headers(200)
                self.wfile.write(json_dumps({"ok": True, "result": result}))
                return
            if path == "/api/crm/agenda/actions":
                user = self._require_auth()
                if not user:
                    return
                payload = self._read_json()
                try:
                    with closing(get_connection()) as conn:
                        result = save_crm_agenda_action(conn, user["company_id"], user, payload)
                except ValueError as exc:
                    self._set_headers(400)
                    self.wfile.write(json_dumps({"error": str(exc)}))
                    return
                self._set_headers(200)
                self.wfile.write(json_dumps({"ok": True, "result": result}))
                return
            if path == "/api/crm/tasks/assign":
                # Gestor cria uma tarefa atribuída ao vendedor responsável pelo cliente,
                # transformando a cobrança verbal em pendência rastreável.
                user = self._require_auth()
                if not user:
                    return
                payload = self._read_json()
                try:
                    with closing(get_connection()) as conn:
                        if data_scope_for_user(conn, user) == "proprio":
                            self._set_headers(403)
                            self.wfile.write(json_dumps({"error": "Ação exclusiva de gestão."}))
                            return
                        client_key = normalize_whitespace(payload.get("clientKey"))
                        client_name = normalize_whitespace(payload.get("clientName"))
                        seller_name = normalize_whitespace(payload.get("sellerName"))
                        title = normalize_whitespace(payload.get("title")) or "Contatar cliente"
                        description = normalize_whitespace(payload.get("description"))
                        due_at = normalize_whitespace(payload.get("dueAt")) or date.today().isoformat()
                        if not client_key or not seller_name:
                            self._set_headers(400)
                            self.wfile.write(json_dumps({"error": "Cliente e vendedor são obrigatórios."}))
                            return
                        # Evita duplicar cobrança para o mesmo cliente/vendedor
                        existing = conn.execute(
                            "SELECT id FROM crm_tasks WHERE company_id = ? AND client_key = ? "
                            "AND seller_name = ? AND status IN ('ABERTA','ATRASADA')",
                            (user["company_id"], client_key, seller_name),
                        ).fetchone()
                        if existing:
                            self._set_headers(200)
                            self.wfile.write(json_dumps({
                                "ok": True, "duplicated": True,
                                "message": f"{seller_name} já tem uma tarefa aberta para este cliente.",
                            }))
                            return
                        conn.execute(
                            """
                            INSERT INTO crm_tasks
                                (company_id, client_key, client_name, seller_name, title, description, due_at, status, created_at)
                            VALUES (?, ?, ?, ?, ?, ?, ?, 'ABERTA', ?)
                            """,
                            (user["company_id"], client_key, client_name, seller_name,
                             title, description, due_at, now_iso()),
                        )
                        audit_log(conn, user["company_id"], user["id"], "criar", "crm_tasks", client_key,
                                  {"seller": seller_name, "origem": "cobranca_gestor"})
                        conn.commit()
                    self._set_headers(200)
                    self.wfile.write(json_dumps({
                        "ok": True,
                        "message": f"Tarefa criada para {seller_name}.",
                    }))
                except Exception as exc:
                    traceback.print_exc()
                    self._set_headers(400)
                    self.wfile.write(json_dumps({"error": str(exc)}))
                return
            if path == "/api/crm/tasks/complete":
                user = self._require_auth()
                if not user:
                    return
                payload = self._read_json()
                try:
                    with closing(get_connection()) as conn:
                        complete_crm_task(conn, user["company_id"], user, int(payload.get("taskId") or 0))
                except (ValueError, TypeError) as exc:
                    self._set_headers(400)
                    self.wfile.write(json_dumps({"error": str(exc)}))
                    return
                self._set_headers(200)
                self.wfile.write(json_dumps({"ok": True}))
                return
            if path == "/api/crm/tasks/reschedule":
                user = self._require_auth()
                if not user:
                    return
                payload = self._read_json()
                try:
                    with closing(get_connection()) as conn:
                        reschedule_crm_task(
                            conn,
                            user["company_id"],
                            user,
                            int(payload.get("taskId") or 0),
                            normalize_whitespace(payload.get("dueAt") or "").replace("T", " "),
                        )
                except (ValueError, TypeError) as exc:
                    self._set_headers(400)
                    self.wfile.write(json_dumps({"error": str(exc)}))
                    return
                self._set_headers(200)
                self.wfile.write(json_dumps({"ok": True}))
                return
            if path in ("/api/admin/goals/seller", "/api/admin/goals/unit"):
                user = self._require_auth()
                if not user or not self._require_admin_area(user):
                    return
                body = json.loads(self.rfile.read(int(self.headers.get("Content-Length", 0))) or b"{}")
                competence = normalize_whitespace(body.get("competence", ""))
                if not competence:
                    self._set_headers(400)
                    self.wfile.write(json_dumps({"error": "Competência obrigatória"}))
                    return
                try:
                    datetime.strptime(competence[:7], "%Y-%m")
                    competence = competence[:7]
                except ValueError:
                    self._set_headers(400)
                    self.wfile.write(json_dumps({"error": f"Competência inválida: {competence}. Use YYYY-MM."}))
                    return
                with closing(get_connection()) as conn:
                    if path == "/api/admin/goals/seller":
                        seller_name = normalize_whitespace(body.get("seller_name", ""))
                        base_unit = normalize_unit(body.get("base_unit", ""))
                        revenue_goal = float(body.get("revenue_goal") or 0)
                        if not seller_name:
                            self._set_headers(400)
                            self.wfile.write(json_dumps({"error": "Vendedor obrigatório"}))
                            return
                        if not self._require_unit_allowed(user, base_unit):
                            return
                        conn.execute(
                            """
                            INSERT INTO goals_seller
                                (company_id, competence, seller_name, base_unit, revenue_goal, returns_goal, created_at)
                            VALUES (?, ?, ?, ?, ?, 0, ?)
                            ON CONFLICT(company_id, competence, seller_name)
                            DO UPDATE SET
                                base_unit = excluded.base_unit,
                                revenue_goal = excluded.revenue_goal,
                                created_at = excluded.created_at
                            """,
                            (user["company_id"], competence, seller_name, base_unit, revenue_goal, now_iso()),
                        )
                        conn.commit()
                    else:
                        unit_name = normalize_unit(body.get("unit_name", ""))
                        revenue_goal = float(body.get("revenue_goal") or 0)
                        if not unit_name:
                            self._set_headers(400)
                            self.wfile.write(json_dumps({"error": "Unidade obrigatória"}))
                            return
                        if not self._require_unit_allowed(user, unit_name):
                            return
                        conn.execute(
                            """
                            INSERT INTO goals_unit
                                (company_id, competence, unit_name, revenue_goal, returns_goal, created_at)
                            VALUES (?, ?, ?, ?, 0, ?)
                            ON CONFLICT(company_id, competence, unit_name)
                            DO UPDATE SET
                                revenue_goal = excluded.revenue_goal,
                                created_at = excluded.created_at
                            """,
                            (user["company_id"], competence, unit_name, revenue_goal, now_iso()),
                        )
                        conn.commit()
                invalidate_dashboard_cache(user["company_id"])
                self._set_headers(200)
                self.wfile.write(json_dumps({"ok": True}))
                return
            if path == "/api/admin/goals/seller/delete":
                user = self._require_auth()
                if not user or not self._require_admin_area(user):
                    return
                body = json.loads(self.rfile.read(int(self.headers.get("Content-Length", 0))) or b"{}")
                competence = normalize_whitespace(body.get("competence", ""))
                seller_name = normalize_whitespace(body.get("seller_name", ""))
                with closing(get_connection()) as conn:
                    conn.execute(
                        "DELETE FROM goals_seller WHERE company_id = ? AND competence = ? AND seller_name = ?",
                        (user["company_id"], competence, seller_name),
                    )
                    conn.commit()
                invalidate_dashboard_cache(user["company_id"])
                self._set_headers(200)
                self.wfile.write(json_dumps({"ok": True}))
                return
            if path == "/api/admin/goals/unit/delete":
                user = self._require_auth()
                if not user or not self._require_admin_area(user):
                    return
                body = json.loads(self.rfile.read(int(self.headers.get("Content-Length", 0))) or b"{}")
                competence = normalize_whitespace(body.get("competence", ""))
                unit_name = normalize_unit(body.get("unit_name", ""))
                with closing(get_connection()) as conn:
                    conn.execute(
                        "DELETE FROM goals_unit WHERE company_id = ? AND competence = ? AND unit_name = ?",
                        (user["company_id"], competence, unit_name),
                    )
                    conn.commit()
                invalidate_dashboard_cache(user["company_id"])
                self._set_headers(200)
                self.wfile.write(json_dumps({"ok": True}))
                return
            if path == "/api/auto-import/run":
                user = self._require_auth()
                if not user or not self._require_admin_area(user):
                    return
                if _AUTO_IMPORT_RUNNING.is_set():
                    self._set_headers(409)
                    self.wfile.write(json_dumps({"error": "Uma importação já está em andamento. Aguarde."}))
                    return
                try:
                    _AUTO_IMPORT_WARNINGS.clear()
                    auto_import_tick()
                    self._set_headers(200)
                    self.wfile.write(json_dumps({
                        "ok": True,
                        "message": "Verificação de importação executada.",
                        "warnings": list(_AUTO_IMPORT_WARNINGS),
                    }))
                except Exception as exc:
                    traceback.print_exc()
                    self._set_headers(500)
                    self.wfile.write(json_dumps({"error": str(exc)}))
                return
            if path == "/api/admin/issues/resolve":
                user = self._require_auth()
                if not user or not self._require_admin_area(user):
                    return
                payload = self._read_json()
                try:
                    with closing(get_connection()) as conn:
                        result = resolve_import_issue(conn, user["company_id"], user["id"], payload)
                except ValueError as exc:
                    self._set_headers(400)
                    self.wfile.write(json_dumps({"error": str(exc)}))
                    return
                self._set_headers(200)
                self.wfile.write(json_dumps(result))
                return
            if path == "/api/admin/vacation":
                user = self._require_auth()
                if not user or not self._require_admin_area(user):
                    return
                payload = self._read_json()
                person_name = normalize_whitespace(payload.get("person_name") or "")
                start_date = normalize_whitespace(payload.get("start_date") or "")
                end_date = normalize_whitespace(payload.get("end_date") or "")
                notes = normalize_whitespace(payload.get("notes") or "") or None
                if not person_name or not start_date or not end_date:
                    self._set_headers(400)
                    self.wfile.write(json_dumps({"error": "Nome, data inicial e data final são obrigatórios"}))
                    return
                with closing(get_connection()) as conn:
                    # Verificar sobreposição de datas com outras entradas do mesmo colaborador
                    overlap = conn.execute(
                        """SELECT id, start_date, end_date FROM vacations
                           WHERE company_id = ? AND person_name = ?
                             AND date(end_date) >= date(?) AND date(start_date) <= date(?)""",
                        (user["company_id"], person_name, start_date, end_date),
                    ).fetchall()
                    if overlap:
                        overlap_info = [f"{r['start_date']} a {r['end_date']}" for r in overlap]
                        self._set_headers(409)
                        self.wfile.write(json_dumps({"error": f"Já existe férias para {person_name} no período sobreposto: {'; '.join(overlap_info)}. Edite ou exclua a entrada existente."}))
                        return
                    conn.execute(
                        "INSERT INTO vacations (company_id, person_name, start_date, end_date, notes, created_at) VALUES (?, ?, ?, ?, ?, ?)",
                        (user["company_id"], person_name, start_date, end_date, notes, now_iso()),
                    )
                    audit_log(conn, user["company_id"], user["id"], "criar", "vacations", "", {"person_name": person_name, "start_date": start_date, "end_date": end_date})
                    conn.commit()
                invalidate_calendar_cache(user["company_id"])
                invalidate_dashboard_cache(user["company_id"])
                self._set_headers(200)
                self.wfile.write(json_dumps({"ok": True}))
                return
            if path == "/api/admin/vacation/update":
                user = self._require_auth()
                if not user or not self._require_admin_area(user):
                    return
                payload = self._read_json()
                vac_id = int(payload.get("id") or 0)
                person_name = normalize_whitespace(payload.get("person_name") or "")
                start_date = normalize_whitespace(payload.get("start_date") or "")
                end_date = normalize_whitespace(payload.get("end_date") or "")
                notes = normalize_whitespace(payload.get("notes") or "") or None
                if not vac_id or not person_name or not start_date or not end_date:
                    self._set_headers(400)
                    self.wfile.write(json_dumps({"error": "ID, nome, data inicial e data final são obrigatórios"}))
                    return
                with closing(get_connection()) as conn:
                    row = conn.execute("SELECT id FROM vacations WHERE id = ? AND company_id = ?", (vac_id, user["company_id"])).fetchone()
                    if not row:
                        self._set_headers(404)
                        self.wfile.write(json_dumps({"error": "Férias não encontradas"}))
                        return
                    conn.execute(
                        "UPDATE vacations SET person_name = ?, start_date = ?, end_date = ?, notes = ? WHERE id = ? AND company_id = ?",
                        (person_name, start_date, end_date, notes, vac_id, user["company_id"]),
                    )
                    audit_log(conn, user["company_id"], user["id"], "editar", "vacations", str(vac_id), {"person_name": person_name, "start_date": start_date, "end_date": end_date})
                    conn.commit()
                invalidate_calendar_cache(user["company_id"])
                invalidate_dashboard_cache(user["company_id"])
                self._set_headers(200)
                self.wfile.write(json_dumps({"ok": True}))
                return
            if path == "/api/admin/vacation/delete":
                user = self._require_auth()
                if not user or not self._require_admin_area(user):
                    return
                payload = self._read_json()
                vac_id = int(payload.get("id") or 0)
                if not vac_id:
                    self._set_headers(400)
                    self.wfile.write(json_dumps({"error": "ID obrigatório"}))
                    return
                with closing(get_connection()) as conn:
                    row = conn.execute("SELECT id FROM vacations WHERE id = ? AND company_id = ?", (vac_id, user["company_id"])).fetchone()
                    if not row:
                        self._set_headers(404)
                        self.wfile.write(json_dumps({"error": "Férias não encontradas"}))
                        return
                    conn.execute("DELETE FROM vacations WHERE id = ? AND company_id = ?", (vac_id, user["company_id"]))
                    audit_log(conn, user["company_id"], user["id"], "excluir", "vacations", str(vac_id), {})
                    conn.commit()
                invalidate_calendar_cache(user["company_id"])
                invalidate_dashboard_cache(user["company_id"])
                self._set_headers(200)
                self.wfile.write(json_dumps({"ok": True}))
                return
            if path == "/api/import/preview":
                user = self._require_auth()
                if not user:
                    return
                if not self._require_admin_area(user):
                    return
                files_payload, fields = self._parse_multipart()
                import_scope = normalize_import_scope(fields.get("importScope"))
                preview = preview_import_package(files_payload, import_scope)
                self._set_headers(200)
                self.wfile.write(json_dumps(preview))
                return
            if path == "/api/import/package":
                user = self._require_auth()
                if not user:
                    return
                if not self._require_admin_area(user):
                    return
                files_payload, fields = self._parse_multipart()
                import_scope = normalize_import_scope(fields.get("importScope"))
                preview = preview_import_package(files_payload, import_scope)
                if not preview.get("isValid"):
                    unsupported = preview.get("unsupportedFiles", [])
                    if unsupported:
                        error_message = "Formato invalido para importacao operacional. Use CSV. Arquivos: " + ", ".join(
                            f["fileName"] for f in unsupported
                        )
                    else:
                        error_message = "Importacao invalida: " + str(preview.get("errors", ["Erro desconhecido"])[0] if preview.get("errors") else "Erro desconhecido")
                    self._set_headers(400)
                    self.wfile.write(json_dumps({"error": error_message}))
                    return
                competence_raw = normalize_whitespace(fields.get("competence") or preview.get("detectedCompetence") or "")
                if not competence_raw:
                    self._set_headers(400)
                    self.wfile.write(json_dumps({"error": "Competencia nao informada"}))
                    return
                # Valida formato YYYY-MM
                try:
                    datetime.strptime(competence_raw[:7], "%Y-%m")
                    competence = competence_raw[:7]
                except ValueError:
                    self._set_headers(400)
                    self.wfile.write(json_dumps({"error": f"Competencia invalida: {competence_raw}. Use formato YYYY-MM."}))
                    return
                import_action = fields.get("importAction") or ""
                try:
                    with closing(get_connection()) as conn:
                        result = import_package(conn, user["company_id"], user["id"], competence, import_action, import_scope, preview, files_payload)
                except Exception as exc:
                    self._set_headers(500)
                    self.wfile.write(json_dumps({"error": str(exc)}))
                    return
                invalidate_crm_cache(user["company_id"])
                self._set_headers(200)
                self.wfile.write(json_dumps(result))
                return
            if path == "/api/admin/import-file/clientes":
                user = self._require_auth()
                if not user:
                    return
                if not self._require_admin_area(user):
                    return
                files_payload, _ = self._parse_multipart()
                if not files_payload:
                    self._set_headers(400)
                    self.wfile.write(json_dumps({"error": "Nenhum arquivo enviado"}))
                    return
            if path == "/api/content/save":
                user = self._require_auth()
                if not user or not self._require_user_management(user):
                    return
                payload = self._read_json()
                try:
                    with closing(get_connection()) as conn:
                        res = upsert_content_item(conn, user["company_id"], user["id"], payload)
                        conn.commit()
                    self._set_headers(200)
                    self.wfile.write(json_dumps({
                        "message": "Conteúdo criado." if res.get("created") else "Conteúdo atualizado.",
                        **res,
                    }))
                except ValueError as exc:
                    self._set_headers(400)
                    self.wfile.write(json_dumps({"error": str(exc)}))
                except Exception as exc:
                    traceback.print_exc()
                    self._set_headers(400)
                    self.wfile.write(json_dumps({"error": str(exc)}))
                return
            if path == "/api/content/delete":
                user = self._require_auth()
                if not user or not self._require_user_management(user):
                    return
                payload = self._read_json()
                try:
                    with closing(get_connection()) as conn:
                        delete_content_item(conn, user["company_id"], user["id"], payload.get("id"))
                        conn.commit()
                    self._set_headers(200)
                    self.wfile.write(json_dumps({"message": "Conteúdo excluído."}))
                except ValueError as exc:
                    self._set_headers(400)
                    self.wfile.write(json_dumps({"error": str(exc)}))
                return
            if path == "/api/admin/profiles":
                user = self._require_auth()
                if not user or not self._require_user_management(user):
                    return
                payload = self._read_json()
                try:
                    with closing(get_connection()) as conn:
                        res = upsert_access_profile(conn, user["company_id"], user["id"], payload)
                        conn.commit()
                    self._set_headers(200)
                    self.wfile.write(json_dumps({
                        "message": "Perfil criado." if res.get("created") else "Perfil atualizado.",
                        **res,
                    }))
                except ValueError as exc:
                    self._set_headers(400)
                    self.wfile.write(json_dumps({"error": str(exc)}))
                except Exception as exc:
                    traceback.print_exc()
                    self._set_headers(400)
                    self.wfile.write(json_dumps({"error": str(exc)}))
                return
            if path == "/api/admin/profiles/delete":
                user = self._require_auth()
                if not user or not self._require_user_management(user):
                    return
                payload = self._read_json()
                try:
                    with closing(get_connection()) as conn:
                        delete_access_profile(conn, user["company_id"], user["id"], payload.get("id"))
                        conn.commit()
                    self._set_headers(200)
                    self.wfile.write(json_dumps({"message": "Perfil excluído."}))
                except ValueError as exc:
                    self._set_headers(400)
                    self.wfile.write(json_dumps({"error": str(exc)}))
                except Exception as exc:
                    traceback.print_exc()
                    self._set_headers(400)
                    self.wfile.write(json_dumps({"error": str(exc)}))
                return
            if path == "/api/admin/users":
                user = self._require_auth()
                if not user or not self._require_user_management(user):
                    return
                payload = self._read_json()
                try:
                    with closing(get_connection()) as conn:
                        res = upsert_user(conn, user["company_id"], user["id"], payload)
                        conn.commit()
                    self._set_headers(200)
                    self.wfile.write(json_dumps({"message": "Usuário criado com sucesso." if res.get("created") else "Usuário atualizado.", **res}))
                except Exception as exc:
                    traceback.print_exc()
                    self._set_headers(400)
                    self.wfile.write(json_dumps({"error": str(exc)}))
                return
            if path == "/api/admin/users/password":
                user = self._require_auth()
                if not user or not self._require_user_management(user):
                    return
                payload = self._read_json()
                try:
                    with closing(get_connection()) as conn:
                        set_user_password(conn, user["company_id"], user["id"], payload.get("id"), payload.get("password"))
                        conn.commit()
                    self._set_headers(200)
                    self.wfile.write(json_dumps({"message": "Senha atualizada com sucesso."}))
                except Exception as exc:
                    traceback.print_exc()
                    self._set_headers(400)
                    self.wfile.write(json_dumps({"error": str(exc)}))
                return
            if path == "/api/admin/users/delete":
                user = self._require_auth()
                if not user or not self._require_user_management(user):
                    return
                payload = self._read_json()
                try:
                    with closing(get_connection()) as conn:
                        delete_user_record(conn, user["company_id"], user["id"], payload.get("id"))
                        conn.commit()
                    self._set_headers(200)
                    self.wfile.write(json_dumps({"message": "Usuário excluído."}))
                except Exception as exc:
                    traceback.print_exc()
                    self._set_headers(400)
                    self.wfile.write(json_dumps({"error": str(exc)}))
                return
            if path == "/api/admin/people/update-unit":
                user = self._require_auth()
                if not user or not self._require_admin_area(user):
                    return
                payload = self._read_json()
                try:
                    with closing(get_connection()) as conn:
                        unit = update_person_unit(conn, user["company_id"], user["id"], payload.get("person_name"), payload.get("base_unit"))
                        conn.commit()
                    self._set_headers(200)
                    self.wfile.write(json_dumps({"message": f"Vendedor '{normalize_whitespace(payload.get('person_name'))}' ajustado para {unit}."}))
                except Exception as exc:
                    traceback.print_exc()
                    self._set_headers(400)
                    self.wfile.write(json_dumps({"error": str(exc)}))
                return
            if path == "/api/admin/city/update-unit":
                user = self._require_auth()
                if not user or not self._require_admin_area(user):
                    return
                payload = self._read_json()
                try:
                    with closing(get_connection()) as conn:
                        unit = update_city_unit(conn, user["company_id"], user["id"], payload.get("city_name"), payload.get("principal_unit"))
                        conn.commit()
                    self._set_headers(200)
                    self.wfile.write(json_dumps({"message": f"Cidade '{normalize_upper(payload.get('city_name'))}' ajustada para {unit}."}))
                except Exception as exc:
                    traceback.print_exc()
                    self._set_headers(400)
                    self.wfile.write(json_dumps({"error": str(exc)}))
                return
            if path.startswith("/api/admin/import/"):
                user = self._require_auth()
                if not user or not self._require_admin_area(user):
                    return
                import_type = path.split("/api/admin/import/")[-1]
                if import_type == "cidade-unidade":
                    files_payload, _ = self._parse_multipart()
                    file_entry = next((f for f in files_payload if f.get("content")), None)
                    if not file_entry:
                        self._set_headers(400)
                        self.wfile.write(json_dumps({"error": "Nenhum arquivo encontrado na requisição."}))
                        return
                    try:
                        with closing(get_connection()) as conn:
                            res = import_city_mappings_csv(conn, user["company_id"], user["id"], file_entry["content"])
                            audit_log(conn, user["company_id"], user["id"], "importar", "city_mappings", import_type, res)
                            conn.commit()
                        self._set_headers(200)
                        self.wfile.write(json_dumps({"message": f"{res['updated']} cidade(s) atualizada(s); {res['resolved']} pendência(s) de cidade resolvida(s)."}))
                    except Exception as exc:
                        traceback.print_exc()
                        self._set_headers(500)
                        self.wfile.write(json_dumps({"error": str(exc)}))
                    return
                TABLE_MAP = {
                    "people":       "people_records",
                    "vacations":    "vacations",
                    "holidays":     "holidays",
                    "goals-seller": "goals_seller",
                    "goals-unit":   "goals_unit",
                    "clients":      "client_registry",
                }
                table_name = TABLE_MAP.get(import_type)
                if not table_name:
                    self._set_headers(400)
                    self.wfile.write(json_dumps({"error": f"Tipo de importação desconhecido: {import_type}"}))
                    return
                files_payload, _ = self._parse_multipart()
                file_entry = next((f for f in files_payload if f.get("content")), None)
                if not file_entry:
                    self._set_headers(400)
                    self.wfile.write(json_dumps({"error": "Nenhum arquivo encontrado na requisição."}))
                    return
                try:
                    with closing(get_connection()) as conn:
                        total = import_admin_csv(conn, user["company_id"], user["id"], table_name, file_entry["content"])
                        audit_log(conn, user["company_id"], user["id"], "importar", table_name, import_type, {"rows": total})
                        conn.commit()
                    self._set_headers(200)
                    self.wfile.write(json_dumps({"message": f"{total} registro(s) importado(s) com sucesso."}))
                except Exception as exc:
                    traceback.print_exc()
                    self._set_headers(500)
                    self.wfile.write(json_dumps({"error": str(exc)}))
                return
            self._set_headers(404)
            self.wfile.write(json_dumps({"error": "rota nao encontrada"}))
        except Exception as exc:
            traceback.print_exc()
            self._set_headers(500)
            self.wfile.write(json_dumps({"error": f"Erro interno: {exc}"}))


_AUTO_IMPORT_LOCK = threading.Lock()
_AUTO_IMPORT_RUNNING = threading.Event()
# Avisos da última execução (ex.: base de clientes encolheu) — lidos pelo botão manual
_AUTO_IMPORT_WARNINGS: list[str] = []


def _auto_import_get_admin_user(conn: sqlite3.Connection) -> sqlite3.Row | None:
    """Retorna o primeiro usuário Admin/Diretor da empresa para usar nos imports automáticos."""
    return conn.execute(
        "SELECT u.id, u.company_id FROM users u WHERE u.role IN ('Administrador','Admin','Diretor') ORDER BY u.id LIMIT 1"
    ).fetchone()


def _auto_import_extract_competence(filename: str) -> str | None:
    """Extrai YYYY-MM do nome do arquivo. Ex: faturamento_2025-06.csv → 2025-06."""
    m = re.search(r"(\d{4}[-/]\d{2})|\b(\d{2}[-/]\d{4})\b", filename)
    if not m:
        return None
    raw = m.group(1) or m.group(2)
    parts = re.split(r"[-/]", raw)
    if len(parts[0]) == 4:
        return f"{parts[0]}-{parts[1]}"   # YYYY-MM
    return f"{parts[1]}-{parts[0]}"       # MM/YYYY → YYYY-MM


def _auto_import_log(conn: sqlite3.Connection, folder: str, scope: str,
                     competence: str | None, status: str, message: str,
                     files: list[str]) -> None:
    conn.execute(
        "INSERT INTO auto_import_log (ran_at, folder, scope, competence, status, message, files_json) VALUES (?,?,?,?,?,?,?)",
        (now_iso(), folder, scope, competence, status, message, json.dumps(files)),
    )
    conn.commit()


def _auto_import_header_cols(content: bytes) -> list[str]:
    """Retorna os nomes das colunas (primeira linha) de um CSV."""
    try:
        first_line = content.decode("latin-1", errors="replace").splitlines()[0]
        sep = ";" if ";" in first_line else ","
        return [c.strip().strip('"') for c in first_line.split(sep)]
    except Exception:
        return []


def _auto_import_detect_cost_field(content: bytes) -> str:
    """Detecta se um CSV de custo é de unidade ou vendedor pela primeira coluna."""
    cols = _auto_import_header_cols(content)
    first_col = cols[0].upper() if cols else ""
    if first_col in {"VENDEDOR", "VENDEDOR CONSOLIDADO"}:
        return "import-cost-vendor-file"
    return "import-cost-unit-file"


def _auto_import_detect_crm_field(content: bytes, filename: str = "") -> str:
    """Detecta se um CSV de CRM é cadastro de clientes ou faturamento consolidado."""
    cols_raw = _auto_import_header_cols(content)
    cols_upper = {c.strip().upper() for c in cols_raw}
    # Cadastro de clientes: colunas típicas
    cadastro_markers = {"RAZAO SOCIAL/NOME", "RAZAO SOCIAL", "NOME FANTASIA", "CPF/CNPJ", "CODIGO CLIENTE"}
    if cadastro_markers & cols_upper:
        return "import-crm-clients-file"
    # Faturamento consolidado: colunas típicas
    consolidado_markers = {"ULT.COMPRA", "ULTIMA COMPRA", "FATURAMENTO", "VALOR LIQUIDO"}
    if consolidado_markers & cols_upper:
        return "import-crm-summary-file"
    # Fallback por nome de arquivo
    stem = Path(filename).stem.lower()
    if any(k in stem for k in ("pessoa", "cadastro", "cliente", "crm", "perfil")):
        return "import-crm-clients-file"
    return "import-crm-summary-file"


def _auto_import_build_payload(files: list[Path], scope: str) -> list[dict[str, Any]]:
    """
    Monta o files_payload como lista de dicts com fieldName correto.
    Escopos com pasta dedicada (crm_clients / crm_summary) dispensam detecção por
    conteúdo — a pasta já define o tipo, evitando classificação errada.
    """
    payload = []
    for f in files:
        content = f.read_bytes()
        if scope == "crm_clients":
            field_name = "import-crm-clients-file"
        elif scope == "crm_summary":
            field_name = "import-crm-summary-file"
        elif scope == "warranty":
            field_name = "import-warranty-file"
        elif scope == "cost":
            field_name = _auto_import_detect_cost_field(content)
        elif scope == "crm":
            field_name = _auto_import_detect_crm_field(content, f.name)
        else:
            field_name = "import-sales-file"  # faturamento: override garante tipo faturamento_detalhado
        payload.append({"fieldName": field_name, "fileName": f.name, "content": content})
    return payload


def auto_import_tick() -> None:
    """Verifica as pastas de auto-import e processa CSVs pendentes."""
    if not _AUTO_IMPORT_LOCK.acquire(blocking=False):
        print("[auto-import] já em execução, ignorando chamada concorrente")
        return
    _AUTO_IMPORT_RUNNING.set()
    try:
        _auto_import_tick_inner()
    finally:
        _AUTO_IMPORT_RUNNING.clear()
        _AUTO_IMPORT_LOCK.release()


def _auto_import_tick_inner() -> None:
    imported_any = False
    for cfg in AUTO_IMPORT_FOLDERS:
        folder_path = AUTO_IMPORT_BASE / cfg["folder"]
        if not folder_path.exists():
            folder_path.mkdir(parents=True, exist_ok=True)
            continue

        csv_files = sorted(folder_path.glob("*.csv"))
        if not csv_files:
            continue

        scope = cfg["scope"]

        # Cadastro de clientes: base mestre do Alfa, SEM competência.
        # O Alfa não exporta a base inteira em um arquivo — são DUAS (ou mais)
        # exportações COMPLEMENTARES. Portanto TODOS os CSVs da pasta entram em
        # UM ÚNICO import: o delete da base acontece uma vez e as linhas de todos
        # os arquivos são inseridas juntas (upsert por client_code).
        # Se cada arquivo virasse um import próprio, o segundo apagaria o primeiro.
        if scope == "crm_clients":
            # Só processa quando os arquivos estão "estáveis" (nenhuma escrita recente),
            # evitando importar meia base enquanto a segunda exportação ainda é copiada.
            _now_ts = time.time()
            _unstable = [f for f in csv_files if (_now_ts - f.stat().st_mtime) < CRM_CLIENTS_SETTLE_SECONDS]
            if _unstable:
                print(f"[auto-import] crm/clientes: {len(_unstable)} arquivo(s) ainda sendo gravado(s), "
                      f"aguardando {CRM_CLIENTS_SETTLE_SECONDS}s de estabilidade")
                continue
            by_competence: dict[str, list[Path]] = {"_clients__all": list(csv_files)}
        else:
            # Agrupa arquivos por competência extraída do nome
            by_competence = {}
            no_comp: list[Path] = []
            for f in csv_files:
                comp = _auto_import_extract_competence(f.name)
                if comp:
                    by_competence.setdefault(comp, []).append(f)
                else:
                    no_comp.append(f)

            # Faturamento: competência lida do conteúdo — aceita sem data no nome.
            # IMPORTANTE: cada arquivo vai em seu próprio grupo (_from_content__N).
            # Agrupar vários arquivos sob uma única chave fazia a competência de UM
            # arquivo ser aplicada a TODOS, gravando dados no mês errado e apagando
            # (import "substituir") o mês correto.
            if no_comp:
                # sales e warranty derivam a competência da data de cada linha,
                # então dispensam o mês no nome do arquivo.
                if scope in {"sales", "warranty"}:
                    for _idx, _f in enumerate(no_comp):
                        by_competence[f"_from_content__{_idx}"] = [_f]
                else:
                    _exemplo = "2026-07" if scope == "crm_summary" else "2026-06"
                    with closing(get_connection()) as conn:
                        for f in no_comp:
                            _auto_import_log(
                                conn, cfg["folder"], scope, None, "erro",
                                f"Competência não encontrada no nome do arquivo '{f.name}'. "
                                f"Inclua o mês no nome, ex: {_exemplo}_{f.name}",
                                [f.name],
                            )
                            print(f"[auto-import] REJEITADO {f.name}: sem competência no nome")

        required_kinds = IMPORT_SCOPE_REQUIREMENTS[scope]

        for competence_key, files in by_competence.items():
            # Monta payload com fieldName correto por escopo/conteúdo
            files_payload = _auto_import_build_payload(files, scope)
            try:
                preview = preview_import_package(files_payload, scope)
            except Exception as exc:
                with closing(get_connection()) as conn:
                    _auto_import_log(conn, cfg["folder"], scope, competence_key,
                                     "erro", f"Erro ao analisar arquivos: {exc}",
                                     [f.name for f in files])
                continue

            # Para faturamento sem data no nome, usa a competência sugerida pelo conteúdo
            if competence_key.startswith("_from_content"):
                suggested = preview.get("suggestedCompetence")
                if not suggested:
                    with closing(get_connection()) as conn:
                        _auto_import_log(conn, cfg["folder"], scope, None, "erro",
                                         "Não foi possível determinar a competência pelo conteúdo do arquivo.",
                                         [f.name for f in files])
                    continue
                competence = suggested
            elif competence_key.startswith("_clients__"):
                # Cadastro de clientes não tem competência; usa o mês atual como rótulo
                competence = date.today().strftime("%Y-%m")
            else:
                competence = competence_key

            detected_kinds = {fi["fileType"] for fi in preview.get("files", []) if fi.get("fileType")}
            if not detected_kinds:
                print(f"[auto-import] {cfg['folder']}/{competence}: nenhum arquivo reconhecido, aguardando")
                continue
            # Escopo "crm" (legado, pasta única) aceita import parcial.
            # Escopos individuais e demais: exige os tipos necessários.
            if scope != "crm":
                missing = required_kinds - detected_kinds
                if missing:
                    print(f"[auto-import] {cfg['folder']}/{competence}: aguardando {missing}")
                    continue

            # Executa o import — pasta de destino espelha a origem para rastreabilidade
            _dest_sub = cfg["folder"].replace("/", "-")
            dest_ok  = AUTO_IMPORT_BASE / "processados" / _dest_sub / competence
            dest_err = AUTO_IMPORT_BASE / "erros" / _dest_sub / competence
            try:
                with closing(get_connection()) as conn:
                    user = _auto_import_get_admin_user(conn)
                    if not user:
                        _auto_import_log(conn, cfg["folder"], scope, competence,
                                         "erro", "Nenhum usuário Admin/Diretor encontrado.", [f.name for f in files])
                        continue
                    result = import_package(
                        conn, user["company_id"], user["id"],
                        competence, "substituir", scope, preview, files_payload,
                    )
                    invalidate_crm_cache(user["company_id"])
                    imported_any = True
                    msg = result.get("message", "OK")
                    _warning = result.get("warning")
                    _auto_import_log(conn, cfg["folder"], scope, competence,
                                     "alerta" if _warning else "sucesso",
                                     f"{msg} — {_warning}" if _warning else msg,
                                     [f.name for f in files])
                    print(f"[auto-import] {cfg['folder']}/{competence}: {msg}")
                    if _warning:
                        print(f"[auto-import] ⚠ {_warning}")
                        _AUTO_IMPORT_WARNINGS.append(_warning)

                dest_ok.mkdir(parents=True, exist_ok=True)
                for f in files:
                    _target = dest_ok / f.name
                    if _target.exists():
                        _stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
                        _target = dest_ok / f"{f.stem}__{_stamp}{f.suffix}"
                    shutil.move(str(f), str(_target))

            except Exception as exc:
                traceback.print_exc()
                with closing(get_connection()) as conn:
                    _auto_import_log(conn, cfg["folder"], scope, competence,
                                     "erro", str(exc), [f.name for f in files])
                dest_err.mkdir(parents=True, exist_ok=True)
                for f in files:
                    try:
                        _target = dest_err / f.name
                        if _target.exists():
                            _stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
                            _target = dest_err / f"{f.stem}__{_stamp}{f.suffix}"
                        shutil.move(str(f), str(_target))
                    except Exception:
                        pass

    # Importou algo: recalcula o dashboard de todas as competências para que a
    # primeira visualização já venha pronta.
    if imported_any:
        warm_dashboard_cache()


def _auto_import_loop() -> None:
    """Thread de background que roda auto_import_tick periodicamente."""
    time.sleep(10)  # Aguarda o servidor inicializar
    while True:
        try:
            auto_import_tick()
        except Exception:
            traceback.print_exc()
        time.sleep(AUTO_IMPORT_INTERVAL)


def _migrate_legacy_crm_folder() -> None:
    """Move CSVs soltos na antiga pasta crm/ para as novas subpastas dedicadas.

    A pasta crm/ passou a ter subpastas (clientes / faturamento-consolidado). Arquivos
    que ficaram na raiz são classificados por conteúdo e movidos uma única vez.
    """
    legacy = AUTO_IMPORT_BASE / "crm"
    if not legacy.exists():
        return
    for f in sorted(legacy.glob("*.csv")):
        try:
            field = _auto_import_detect_crm_field(f.read_bytes(), f.name)
            sub = "clientes" if field == "import-crm-clients-file" else "faturamento-consolidado"
            dest_dir = legacy / sub
            dest_dir.mkdir(parents=True, exist_ok=True)
            shutil.move(str(f), str(dest_dir / f.name))
            print(f"[auto-import] migrado {f.name} -> crm/{sub}/")
        except Exception:
            traceback.print_exc()


def run_server(host: str = DEFAULT_HOST, port: int = DEFAULT_PORT) -> None:
    # Cria pastas de auto-import se não existirem
    for cfg in AUTO_IMPORT_FOLDERS:
        (AUTO_IMPORT_BASE / cfg["folder"]).mkdir(parents=True, exist_ok=True)
    (AUTO_IMPORT_BASE / "processados").mkdir(parents=True, exist_ok=True)
    (AUTO_IMPORT_BASE / "erros").mkdir(parents=True, exist_ok=True)
    _migrate_legacy_crm_folder()

    t = threading.Thread(target=_auto_import_loop, daemon=True, name="auto-import")
    t.start()

    # Pré-aquece o cache do dashboard em segundo plano — o servidor já sobe atendendo
    threading.Thread(target=warm_dashboard_cache, daemon=True, name="dashboard-warmup").start()

    server = ThreadingHTTPServer((host, port), AppHandler)
    print(f"Servidor rodando em http://{host}:{port}")
    server.serve_forever()

if __name__ == "__main__":
    init_db()
    run_server()
