const state = {
  user: null,
  options: { competences: [], units: [], sellers: [], cities: [] },
  dashboard: null,
  admin: null,
  sellerScore: null,
  teamScore: null,
  missionProgress: { contactsToday: 0 },
  activeTab: "executivo",
  adminSection: "cadastros",
  filters: {
    competenceStart: "",
    competenceEnd: "",
    unit: "",
    seller: "",
    city: "",
  },
  ui: {
    loading: {
      dashboard: false,
      crmSummary: false,
      crmClients: false,
      crmAgenda: false,
      crmTasks: false,
      clientDrawer: false,
      admin: false,
      integrityAudit: false,
      filters: false,
    },
    executiveSections: {
      details: false,
      ranking: false,
      comparisons: false,
      units: false,
    },
    sellerSections: {
      ranking: false,
    },
    actionsMenuOpen: false,
    sidebarCollapsed: window.innerWidth <= 1280,
    filtersCollapsed: true,
    crmAgendaExpanded: {},
    crmClientDetailTab: "historico",
    clientDrawerOpen: false,
    clientDrawerError: "",
  },
  login: {
    username: "admin",
    password: "Passini@2026",
  },
  userEditor: {
    id: "",
    username: "",
    fullName: "",
    linkedPersonName: "",
    linkedUnits: [],
    role: "Administrador",
    password: "",
    isActive: true,
  },
  goalEditors: {
    seller: {
      competence: "",
      sellerName: "",
      baseUnit: "",
      revenueGoal: "",
      editing: false,
    },
    unit: {
      competence: "",
      unitName: "",
      revenueGoal: "",
      editing: false,
    },
  },
  messages: [],
  integrityAudit: {
    competence: "",
    data: null,
    error: "",
  },
  crm: {
    options: { contactTypes: [], contactResults: [] },
    summary: null,
    agenda: { top5: [], extended: [], total: 0 },
    clients: [],
    crmClientFilters: {
      status: "",
      purchaseMonth: "",
      growth: "",
      classCode: "",
      personType: "",
      search: "",
      unit: "",
      seller: "",
    },
    pagination: {
      page: 1,
      pageSize: 50,
      total: 0,
      totalPages: 0,
    },
    sellerFilters: {
      unit: "",
      status: "",
      orderBy: "score",
      search: "",
      mode: "summary",
    },
    selectedClientKey: "",
    selectedClient: null,
    selectedClientTabs: {
      historico: { rows: [], loaded: false, loading: false, error: "", page: 1, pageSize: 20, total: 0, totalPages: 0 },
      compras: { rows: [], loaded: false, loading: false, error: "" },
      itens: { rows: [], loaded: false, loading: false, error: "", page: 1, pageSize: 20, total: 0, totalPages: 0 },
      interacoes: { rows: [], loaded: false, loading: false, error: "", page: 1, pageSize: 20, total: 0, totalPages: 0 },
    },
    taskRows: [],
    interactionForm: {
      clientKey: "",
      clientName: "",
      clientCode: "",
      unitName: "",
      updatedPhone: "",
      primaryContactName: "",
      contactNotes: "",
      contactTypeCode: "LIGACAO",
      resultCode: "FALOU_CLIENTE",
      occurredAt: "",
      notes: "",
      questionUsed: "",
      hadProgress: false,
      offerTitle: "",
      nextAction: "",
      followupDueAt: "",
    },
    modal: null,
    teamActivity: null,
    autoImport: null,
    editingVacationId: null,
    editingVacation: null,
    showVacationForm: false,
    portfolioSummary: null,
    portfolioViewMode: "lista",
    portfolioFilters: { competence: "", unit: "", search: "", status: "", personType: "" },
  },
};

const CRM_IMPORT_KIND_LABELS = {
  cadastro_clientes: "cadastro de clientes",
  faturamento_cliente_consolidado: "faturamento consolidado",
};

const app = document.getElementById("app");
let renderScheduled = false;

function requestRender() {
  if (renderScheduled) return;
  renderScheduled = true;
  window.requestAnimationFrame(() => {
    renderScheduled = false;
    render();
  });
}

function setLoading(key, value) {
  if (!state.ui.loading) {
    state.ui.loading = {};
  }
  state.ui.loading[key] = Boolean(value);
}

function currency(value) {
  return new Intl.NumberFormat("pt-BR", { style: "currency", currency: "BRL" }).format(Number(value || 0));
}

function number(value) {
  return new Intl.NumberFormat("pt-BR").format(Number(value || 0));
}

function pct(value) {
  return `${Number(value || 0).toFixed(2)}%`;
}

function marginText(value) {
  return value === null || value === undefined ? "-" : Number(value).toFixed(2);
}

function escapeHtml(value) {
  return String(value ?? "")
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;");
}

function roleIsSeller() {
  return state.user?.role === "Vendedor";
}

function roleIsManager() {
  return state.user?.role === "Gerente";
}

function roleIsAdminLike() {
  return ["Administrador", "Analista", "Gerente"].includes(state.user?.role);
}

function firstName(value) {
  return String(value || "").trim().split(" ")[0] || "";
}

function growthLabel(value) {
  const numeric = Number(value || 0);
  if (numeric > 0.03) return "Crescimento acima";
  if (numeric < -0.03) return "Crescimento abaixo";
  return "Crescimento estável";
}

function emptyStateCard(message) {
  return `<div class="message success">${escapeHtml(message)}</div>`;
}

function buttonAction(label, handler, tone = "ghost") {
  return `<button class="btn btn-${tone}" onclick="${handler}">${escapeHtml(label)}</button>`;
}

function toggleSection(sectionKey) {
  state.ui.executiveSections[sectionKey] = !state.ui.executiveSections[sectionKey];
  requestRender();
}

function toggleAgendaDetails(clientKey) {
  state.ui.crmAgendaExpanded[clientKey] = !state.ui.crmAgendaExpanded[clientKey];
  requestRender();
}

async function setCrmClientDetailTab(tab) {
  state.ui.crmClientDetailTab = tab;
  await ensureCrmClientTabLoaded(tab);
  requestRender();
}

function setAdminSection(section) {
  state.adminSection = section;
  if (section === "auditoria-integridade") {
    if (!state.integrityAudit.competence) {
      state.integrityAudit.competence = state.filters.competenceEnd || state.filters.competenceStart || state.options.competences[0] || "";
    }
    const loadedCompetence = state.integrityAudit.data?.competence || "";
    if (!state.ui.loading.integrityAudit && (!state.integrityAudit.data || loadedCompetence !== state.integrityAudit.competence)) {
      void runIntegrityAudit(false);
    }
  }
  requestRender();
}

function toggleActionsMenu() {
  state.ui.actionsMenuOpen = !state.ui.actionsMenuOpen;
  requestRender();
}

function toggleMainFilters() {
  state.ui.filtersCollapsed = !state.ui.filtersCollapsed;
  requestRender();
}

function closeClientDrawer() {
  state.ui.clientDrawerOpen = false;
  setLoading("clientDrawer", false);
  state.ui.clientDrawerError = "";
  requestRender();
}

function emptyClientTabState(pageSize = 20) {
  return { rows: [], loaded: false, loading: false, error: "", page: 1, pageSize, total: 0, totalPages: 0 };
}

function resetSelectedClientTabs() {
  state.crm.selectedClientTabs = {
    historico: emptyClientTabState(20),
    compras: { rows: [], loaded: false, loading: false, error: "" },
    itens: emptyClientTabState(20),
    interacoes: emptyClientTabState(20),
  };
}

function crmPurchaseBadge(value) {
  return Number(value || 0) > 0
    ? '<span class="status-tag good">Com compra</span>'
    : '<span class="status-tag bad">Sem compra</span>';
}

async function api(path, options = {}) {
  const response = await fetch(path, {
    credentials: "same-origin",
    ...options,
    headers: {
      ...(options.body instanceof FormData ? {} : { "Content-Type": "application/json" }),
      ...(options.headers || {}),
    },
  });
  const contentType = response.headers.get("Content-Type") || "";
  if (!response.ok) {
    if (contentType.includes("application/json")) {
      const error = await response.json();
      throw new Error(error.error || "Erro na operação");
    }
    throw new Error("Erro na operação");
  }
  if (contentType.includes("application/json")) {
    return response.json();
  }
  return response.blob();
}

function addMessage(type, text) {
  const id = Date.now();
  state.messages = [{ type, text, id }, ...state.messages].slice(0, 3);
  requestRender();
  const delay = type === "error" ? 6000 : 4000;
  setTimeout(() => {
    state.messages = state.messages.filter((m) => m.id !== id);
    requestRender();
  }, delay);
}

function defaultTabForUser(user) {
  if (user?.role === "Vendedor") return "crm-agenda";
  if (user?.role === "Gerente") return "executivo";
  return "executivo";
}

function allowedTabsForUser(user) {
  if (!user) return ["executivo"];
  if (user.role === "Vendedor") {
    return ["crm-agenda", "meu-placar", "crm-clientes", "crm-tarefas", "executivo", "vendedores", "calendario"];
  }
  if (user.role === "Gerente") {
    return ["crm-agenda", "placar-equipe", "crm-clientes", "crm-tarefas", "executivo", "vendedores", "unidades", "clientes", "cidades", "descontos", "calendario", "importacoes", "administracao", "configuracoes"];
  }
  if (user.role === "Analista") {
    return ["crm-agenda", "placar-equipe", "crm-clientes", "crm-tarefas", "executivo", "vendedores", "unidades", "clientes", "cidades", "descontos", "calendario", "importacoes", "administracao", "configuracoes"];
  }
  return ["crm-agenda", "placar-equipe", "crm-clientes", "crm-tarefas", "executivo", "vendedores", "unidades", "clientes", "cidades", "descontos", "calendario", "importacoes", "administracao", "configuracoes"];
}

function ensureActiveTabForUser(user) {
  const allowed = allowedTabsForUser(user);
  if (!allowed.includes(state.activeTab)) {
    state.activeTab = defaultTabForUser(user);
  }
}

async function loadSellerScore(competence) {
  try {
    const qs = competence ? `?competence=${encodeURIComponent(competence)}` : "";
    state.sellerScore = await api(`/api/crm/seller-score${qs}`);
  } catch (_) {
    state.sellerScore = null;
  }
  requestRender();
}

async function loadTeamScore() {
  try {
    state.teamScore = await api("/api/crm/team-score");
  } catch (err) {
    console.error("loadTeamScore error:", err);
    state.teamScore = { error: err.message, sellers: [], summary: {} };
  }
  requestRender();
}

async function loadTeamActivity() {
  try {
    state.crm.teamActivity = await api("/api/crm/team-activity-today");
  } catch (err) {
    state.crm.teamActivity = { error: err.message, sellers: [], totalContactsToday: 0, teamGoal: 0 };
  }
  requestRender();
}

async function loadPortfolioSummary() {
  try {
    const _pf = state.crm.portfolioFilters || {};
    const _pq = new URLSearchParams();
    if (_pf.competence) _pq.set("competence", _pf.competence);
    if (_pf.unit) _pq.set("unit", _pf.unit);
    if (_pf.personType) _pq.set("personType", _pf.personType);
    const _pqs = _pq.toString();
    state.crm.portfolioSummary = await api("/api/crm/portfolio-summary" + (_pqs ? "?" + _pqs : ""));
  } catch (err) {
    state.crm.portfolioSummary = { error: err.message, sellers: [], totals: {} };
  }
  requestRender();
}

async function bootstrap() {
  const session = await api("/api/session");
  if (session.authenticated) {
    state.user = session.user;
    state.activeTab = defaultTabForUser(state.user);
    // Cargas essenciais em paralelo (options não bloqueia mais o restante)
    const loads = [loadOptions(), loadDashboard(), loadCrmOptions(), loadCrmData()];
    if (session.user.role === "Vendedor") loads.push(loadSellerScore());
    await Promise.all(loads);
    if (state.user.role !== "Vendedor") {
      // Cargas pesadas em background — nenhuma bloqueia a UI
      loadAdmin();
      loadTeamScore();
      loadTeamActivity();
      loadPortfolioSummary();
    }
  }
  requestRender();
}

async function loadOptions() {
  state.options = await api("/api/options");
  const now = new Date();
  const currentCompetence = `${now.getFullYear()}-${String(now.getMonth() + 1).padStart(2, "0")}`;
  if (!state.filters.competenceEnd) {
    state.filters.competenceEnd = currentCompetence;
    state.filters.competenceStart = currentCompetence;
  }
  if (state.options.competences.length && !state.options.competences.includes(state.filters.competenceEnd)) {
    state.filters.competenceEnd = state.options.competences[0];
    state.filters.competenceStart = state.options.competences[0];
  }
  syncUserEditorOptions();
}

function buildQuery() {
  const params = new URLSearchParams();
  Object.entries(state.filters).forEach(([key, value]) => {
    if (value) params.set(key, value);
  });
  return params.toString();
}

async function loadDashboard() {
  setLoading("dashboard", true);
  try {
    const dashboard = await api(`/api/dashboard?${buildQuery()}`);
    state.dashboard = dashboard;
  } finally {
    setLoading("dashboard", false);
  }
  requestRender();
}

function integrityAuditCompetenceOptions() {
  const values = new Set([
    state.integrityAudit.competence,
    state.filters.competenceEnd,
    state.filters.competenceStart,
    ...(state.options.competences || []),
  ].filter(Boolean));
  return Array.from(values);
}

function setIntegrityAuditCompetence(value) {
  state.integrityAudit.competence = value;
  state.integrityAudit.error = "";
  requestRender();
}

async function runIntegrityAudit(renderBeforeLoad = true) {
  const competence = state.integrityAudit.competence || state.filters.competenceEnd || state.filters.competenceStart || state.options.competences[0] || "";
  if (!competence) {
    state.integrityAudit.error = "Selecione uma competência para executar a auditoria.";
    requestRender();
    return;
  }
  state.integrityAudit.competence = competence;
  state.integrityAudit.error = "";
  setLoading("integrityAudit", true);
  if (renderBeforeLoad) {
    requestRender();
  }
  try {
    const auditResult = await api(`/api/audit/integrity?competence=${encodeURIComponent(competence)}`);
    state.integrityAudit.data = auditResult;
    if (window.__PASSINI_DEBUG_AUDIT__ === true) {
      console.log("[PASSINI INTEGRITY AUDIT]", auditResult);
    }
  } catch (error) {
    state.integrityAudit.error = error.message || "Não foi possível executar a auditoria.";
  } finally {
    setLoading("integrityAudit", false);
  }
  requestRender();
}

async function loadCrmOptions() {
  state.crm.options = await api("/api/crm/options");
}

async function loadCrmData() {
  const firstLoad = !state.crm.summary && !state.crm.agenda?.total && !(state.crm.taskRows || []).length;
  setLoading("crmSummary", true);
  setLoading("crmAgenda", true);
  setLoading("crmTasks", true);
  if (firstLoad) {
    requestRender();
  }
  try {
    const [summary, agenda, tasks] = await Promise.all([
      api(`/api/crm/summary?${buildQuery()}`),
      api(`/api/crm/agenda?${buildQuery()}`),
      api(`/api/crm/tasks`),
    ]);
    state.crm.summary = summary;
    state.crm.agenda = agenda;
    state.crm.taskRows = tasks.rows || [];
    if (state.crm.selectedClientKey) {
      await openCrmClient(state.crm.selectedClientKey, false, false);
    }
  } finally {
    setLoading("crmSummary", false);
    setLoading("crmAgenda", false);
    setLoading("crmTasks", false);
  }
  requestRender();
  // Carrega a lista de clientes em background — não bloqueia o render inicial
  loadCrmClients({ renderAfterLoad: true, reason: "reload" });
}

async function loadCrmClients({ renderAfterLoad = true, reason = "reload", pageAdjusted = false } = {}) {
  const query = new URLSearchParams();
  const filters = state.crm.crmClientFilters || {};
  // Filtros CRM têm precedência sobre filtros globais de unidade/vendedor
  if (filters.unit) query.set("unit", filters.unit);
  else if (state.filters.unit) query.set("unit", state.filters.unit);
  if (filters.seller) query.set("seller", filters.seller);
  if (filters.status) query.set("status", filters.status);
  if (filters.purchaseMonth) query.set("purchaseMonth", filters.purchaseMonth);
  if (filters.growth) query.set("growth", filters.growth);
  if (filters.classCode) query.set("classCode", filters.classCode);
  if (filters.personType) query.set("personType", filters.personType);
  if (filters.search) query.set("search", filters.search);
  // Vendedor vê toda a carteira de uma vez (sem paginação) para agrupar por status
  const isSeller = roleIsSeller();
  query.set("page", isSeller ? "1" : String(state.crm.pagination.page || 1));
  query.set("pageSize", isSeller ? "9999" : String(state.crm.pagination.pageSize || 50));
  setLoading("crmClients", true);
  requestRender(); // sempre mostra o banner de loading imediatamente
  try {
    const clients = await api(`/api/crm/clients?${query.toString()}`);
    const totalPages = Number(clients.totalPages || 1) || 1;
    const currentPage = Number(state.crm.pagination.page || 1);
    if (!pageAdjusted && currentPage > totalPages) {
      state.crm.pagination.page = totalPages;
      return loadCrmClients({ renderAfterLoad, reason, pageAdjusted: true });
    }
    state.crm.clients = clients.rows || [];
    state.crm.pagination = {
      page: Number(clients.page || 1),
      pageSize: Number(clients.pageSize || state.crm.pagination.pageSize || 50),
      total: Number(clients.total || 0),
      totalPages,
    };
  } finally {
    setLoading("crmClients", false);
  }
  if (renderAfterLoad) {
    requestRender();
  }
}

function sellersForCrmFilter() {
  const selectedUnit = state.crm.crmClientFilters.unit || state.filters.unit || "";
  const swu = state.options.sellersWithUnits || [];
  if (!selectedUnit || !swu.length) return state.options.sellers || [];
  const filtered = swu.filter((s) => s.unit === selectedUnit).map((s) => s.name);
  return filtered.length ? filtered : state.options.sellers || [];
}

// Atualiza filtro sem disparar busca — usada pelos selects
function updateCrmClientFilter(key, value) {
  state.crm.crmClientFilters[key] = value;
  if (key === "unit") {
    const available = sellersForCrmFilter();
    if (state.crm.crmClientFilters.seller && !available.includes(state.crm.crmClientFilters.seller)) {
      state.crm.crmClientFilters.seller = "";
    }
  }
  requestRender(); // re-renderiza para atualizar dropdown de vendedor
}

// Mantida para usos internos que precisam disparar busca imediatamente
async function setCrmClientFilter(key, value) {
  updateCrmClientFilter(key, value);
  state.crm.pagination.page = 1;
  await loadCrmClients({ reason: "filter-change" });
}

async function clearCrmClientFilters() {
  state.crm.crmClientFilters = {
    status: "",
    purchaseMonth: "",
    growth: "",
    classCode: "",
    personType: "",
    search: "",
    unit: "",
    seller: "",
  };
  state.crm.pagination.page = 1;
  await loadCrmClients({ reason: "filter-change" });
}

function filteredCrmClients() {
  return state.crm.clients || [];
}

async function setCrmClientPage(page) {
  const totalPages = Math.max(Number(state.crm.pagination.totalPages || 1), 1);
  state.crm.pagination.page = Math.min(Math.max(Number(page || 1), 1), totalPages);
  await loadCrmClients({ reason: "page-change" });
}

async function setCrmClientPageSize(pageSize) {
  state.crm.pagination.pageSize = Number(pageSize || 50);
  state.crm.pagination.page = 1;
  await loadCrmClients({ reason: "page-size-change" });
}

async function runCrmClientSearch() {
  state.crm.pagination.page = 1;
  await loadCrmClients({ reason: "filter-change" });
}

async function exportCrmClientsXLSX() {
  try {
    addMessage("info", "Gerando planilha…");
    const query = new URLSearchParams();
    const filters = state.crm.crmClientFilters || {};
    if (filters.unit) query.set("unit", filters.unit);
    else if (state.filters.unit) query.set("unit", state.filters.unit);
    if (filters.seller) query.set("seller", filters.seller);
    if (filters.status) query.set("status", filters.status);
    if (filters.purchaseMonth) query.set("purchaseMonth", filters.purchaseMonth);
    if (filters.growth) query.set("growth", filters.growth);
    if (filters.classCode) query.set("classCode", filters.classCode);
    if (filters.personType) query.set("personType", filters.personType);
    if (filters.search) query.set("search", filters.search);
    query.set("page", "1");
    query.set("pageSize", "9999");
    const data = await api(`/api/crm/clients?${query.toString()}`);
    const rows = data.rows || [];
    if (!rows.length) { addMessage("warn", "Nenhum cliente encontrado para exportar."); return; }

    // Carrega SheetJS dinamicamente se necessário
    if (!window.XLSX) {
      await new Promise((resolve, reject) => {
        const s = document.createElement("script");
        s.src = "https://cdnjs.cloudflare.com/ajax/libs/xlsx/0.18.5/xlsx.full.min.js";
        s.onload = resolve;
        s.onerror = reject;
        document.head.appendChild(s);
      });
    }

    const headers = ["Código","Cliente","Unidade","Vendedor","Cidade","Status","Classe","Telefone","Contato principal","Compra no mês (R$)","Média trim. (R$)","Última compra","Dias sem compra","Motivo principal"];
    const sheetData = [
      headers,
      ...rows.map(r => [
        r.clientKey || "",
        r.clientName || "",
        r.unitName || "",
        r.assignedSeller || "",
        r.cityName || "",
        r.statusCode || "",
        r.classCode || "",
        r.phone || "",
        r.primaryContactName || "",
        r.currentRevenue != null ? Number(r.currentRevenue) : 0,
        r.averageRevenue != null ? Number(r.averageRevenue) : 0,
        r.lastPurchaseAt ? r.lastPurchaseAt.slice(0, 10) : "",
        r.daysWithoutPurchase != null ? Number(r.daysWithoutPurchase) : "",
        r.primaryReason || "",
      ]),
    ];

    const ws = XLSX.utils.aoa_to_sheet(sheetData);
    // Larguras de colunas
    ws["!cols"] = [
      {wch:10},{wch:35},{wch:14},{wch:28},{wch:18},{wch:12},{wch:10},
      {wch:16},{wch:22},{wch:16},{wch:14},{wch:13},{wch:14},{wch:30},
    ];
    const wb = XLSX.utils.book_new();
    XLSX.utils.book_append_sheet(wb, ws, "Clientes");
    XLSX.writeFile(wb, `clientes_${new Date().toISOString().slice(0,10)}.xlsx`);
    addMessage("success", `Planilha exportada — ${rows.length} clientes.`);
  } catch (e) {
    addMessage("error", "Erro ao exportar: " + (e.message || e));
  }
}

async function ensureCrmClientTabLoaded(tab, silent = false) {
  const clientKey = state.crm.selectedClientKey;
  if (!clientKey) return;
  const current = state.crm.selectedClientTabs[tab];
  if (!current || current.loaded || current.loading) return;
  current.loading = true;
  current.error = "";
  // Só re-renderiza imediatamente se for carregamento individual (não preload paralelo)
  if (!silent) requestRender();
  try {
    let result;
    if (tab === "interacoes") {
      result = await api(`/api/crm/client/interactions?${buildQuery()}&clientKey=${encodeURIComponent(clientKey)}&page=${current.page}&pageSize=${current.pageSize}`);
      state.crm.selectedClientTabs.interacoes = { ...current, ...result, loaded: true, loading: false, error: "" };
      if (!silent) requestRender();
      return;
    }
    if (tab === "itens") {
      result = await api(`/api/crm/client/items?${buildQuery()}&clientKey=${encodeURIComponent(clientKey)}&page=${current.page}&pageSize=${current.pageSize}`);
      state.crm.selectedClientTabs.itens = { ...current, ...result, loaded: true, loading: false, error: "" };
      if (!silent) requestRender();
      return;
    }
    if (tab === "compras") {
      result = await api(`/api/crm/client/purchases?${buildQuery()}&clientKey=${encodeURIComponent(clientKey)}`);
      state.crm.selectedClientTabs.compras = { rows: result.rows || [], loaded: true, loading: false, error: "" };
      if (!silent) requestRender();
      return;
    }
    result = await api(`/api/crm/client/tasks?${buildQuery()}&clientKey=${encodeURIComponent(clientKey)}`);
    state.crm.selectedClientTabs.historico = { rows: result.rows || [], loaded: true, loading: false, error: "" };
    if (!silent) requestRender();
  } catch (error) {
    state.crm.selectedClientTabs[tab] = { ...current, loading: false, error: error.message || "Erro" };
  }
  if (!silent) requestRender();
}

async function loadAdmin() {
  setLoading("admin", true);
  try {
    state.admin = await api("/api/admin/all");
    syncUserEditorOptions();
  } finally {
    setLoading("admin", false);
  }
  requestRender();
}

async function loadAutoImportStatus() {
  try {
    state.autoImport = await api("/api/auto-import/status");
  } catch (e) {
    state.autoImport = { error: e.message, logs: [], folders: [] };
  }
  requestRender();
}

function sellerPeopleOptions() {
  return (state.admin?.people || [])
    .filter((person) => person.role_classification === "Vendedor" && !person.valid_to)
    .sort((left, right) => String(left.person_name || "").localeCompare(String(right.person_name || ""), "pt-BR"));
}

function syncUserEditorOptions() {
  const availableUnits = state.options.units || [];
  state.userEditor.linkedUnits = (state.userEditor.linkedUnits || []).filter((unit) => availableUnits.includes(unit));
  if (state.userEditor.role === "Vendedor") {
    const people = sellerPeopleOptions();
    if (!people.some((person) => person.person_name === state.userEditor.linkedPersonName)) {
      state.userEditor.linkedPersonName = "";
    }
    state.userEditor.linkedUnits = [];
  }
  if (!["Gerente", "Analista"].includes(state.userEditor.role)) {
    state.userEditor.linkedUnits = [];
  }
}

function resetUserEditor() {
  state.userEditor = {
    id: "",
    username: "",
    fullName: "",
    linkedPersonName: "",
    linkedUnits: [],
    role: "Administrador",
    password: "",
    isActive: true,
  };
}

function editUser(userId) {
  const user = (state.admin?.users || []).find((item) => Number(item.id) === Number(userId));
  if (!user) return;
  state.userEditor = {
    id: user.id,
    username: user.username || "",
    fullName: user.full_name || "",
    linkedPersonName: user.linked_person_name || "",
    linkedUnits: [...(user.linked_units || [])],
    role: user.role || "Administrador",
    password: "",
    isActive: Boolean(user.is_active),
  };
  syncUserEditorOptions();
  requestRender();
}

function setUserRole(value) {
  state.userEditor.role = value;
  if (value !== "Vendedor") {
    state.userEditor.linkedPersonName = "";
  }
  if (!["Gerente", "Analista"].includes(value)) {
    state.userEditor.linkedUnits = [];
  }
  syncUserEditorOptions();
  requestRender();
}

function toggleUserLinkedUnit(unit) {
  const normalized = unit;
  const current = new Set(state.userEditor.linkedUnits || []);
  if (current.has(normalized)) {
    current.delete(normalized);
  } else {
    current.add(normalized);
  }
  state.userEditor.linkedUnits = Array.from(current);
  requestRender();
}

async function handleLogin(event) {
  event.preventDefault();
  try {
    const result = await api("/api/login", {
      method: "POST",
      body: JSON.stringify(state.login),
    });
    state.user = result.user;
    state.activeTab = defaultTabForUser(state.user);
    const loginLoads = [loadOptions(), loadDashboard(), loadCrmOptions(), loadCrmData()];
    if (result.user.role === "Vendedor") loginLoads.push(loadSellerScore());
    await Promise.all(loginLoads);
    if (state.user.role !== "Vendedor") {
      loadAdmin();
      loadTeamScore();
      loadTeamActivity();
      loadPortfolioSummary();
    }
    addMessage("success", "Login realizado com sucesso.");
  } catch (error) {
    addMessage("error", error.message);
  }
}

async function logout() {
  await api("/api/logout", { method: "POST" });
  state.user = null;
  state.activeTab = "executivo";
  state.dashboard = null;
  state.admin = null;
  requestRender();
}

function messageHtml() {
  if (!state.messages.length) return "";
  return `
    <div class="stack">
      ${state.messages
        .map((item) => `<div class="message ${item.type}">${escapeHtml(item.text)}</div>`)
        .join("")}
    </div>
  `;
}

function loginView() {
  return `
    <div class="login-shell">
      <div class="login-card">
        <div class="login-hero">
          <div class="login-badge">Dashboard Comercial Local</div>
          <h1>Passini<br />Resultados Comerciais</h1>
          <p>
            Painel estratégico para gerentes com visão consolidada, metas, devoluções, projeções,
            ticket médio, score de vendedores, quadrantes e governança de importação.
          </p>
          <div class="hero-grid">
            <div class="mini-card"><span>Foco</span><strong>Unidades, vendedores, cidades e competência</strong></div>
            <div class="mini-card"><span>Importação</span><strong>Custo e faturamento separados, com auditoria por competência</strong></div>
            <div class="mini-card"><span>Operação</span><strong>Servidor local, login protegido e banco local</strong></div>
            <div class="mini-card"><span>Expansão</span><strong>Estrutura pronta para servidor e multiempresa</strong></div>
          </div>
        </div>
        <form class="login-form" onsubmit="handleLogin(event)">
          <div>
            <h2>Entrar</h2>
            <p class="hint">Use o usuário padrão para o primeiro acesso. Depois você pode criar novos perfis administrativos.</p>
          </div>
          ${messageHtml()}
          <div class="field">
            <label>Usuário</label>
            <input value="${escapeHtml(state.login.username)}" oninput="state.login.username=this.value" />
          </div>
          <div class="field">
            <label>Senha</label>
            <input type="password" value="${escapeHtml(state.login.password)}" oninput="state.login.password=this.value" />
          </div>
          <button class="btn btn-primary" type="submit">Entrar no dashboard</button>
          <div class="credentials-box">
            <strong>Credencial inicial</strong>
            <div class="text-small">Usuário: <strong>admin</strong></div>
            <div class="text-small">Senha padrão: <strong>Passini@2026</strong></div>
          </div>
        </form>
      </div>
    </div>
  `;
}

function tabButton(id, title, desc) {
  return `
    <button class="tab-button ${state.activeTab === id ? "active" : ""}" onclick="switchTab('${id}')">
      <div>
        <div class="tab-title">${title}</div>
        <span class="tab-desc">${desc}</span>
      </div>
    </button>
  `;
}

function kpiCard(title, value, footLeft, footRight) {
  return `
    <div class="kpi-card">
      <span>${title}</span>
      <strong>${value}</strong>
      <div class="kpi-foot">
        <span>${footLeft || ""}</span>
        <span>${footRight || ""}</span>
      </div>
    </div>
  `;
}



function quadrantHtml(quadrant) {
  if (!quadrant) return "";
  const points = quadrant.points
    .slice(0, 10)
    .map((point) => {
      const left = Math.min(96, Math.max(2, point.x / 2));
      const top = Math.min(96, Math.max(2, 100 - point.y));
      return `<div class="point" data-label="${escapeHtml(point.sellerName)}" style="left:${left}%; top:${top}%"></div>`;
    })
    .join("");
  return `
    <div class="quadrant">
      <div class="quadrant-labels">
        <span style="top:0; left:0;">Desenvolver</span>
        <span style="top:0; right:0;">Excelência</span>
        <span style="bottom:0; left:0;">Intervir</span>
        <span style="bottom:0; right:0;">Entregando com risco</span>
      </div>
      ${points}
    </div>
    <div class="text-small">Eixo X = atingimento da meta. Eixo Y = score do vendedor.</div>
  `;
}

function sellerRows(rows) {
  return rows
    .map(
      (row) => `
      <tr>
        <td>${escapeHtml(row.sellerName)} ${row.pendingMapping ? '<span class="status-tag warn">Pendente</span>' : ""}</td>
        <td>${escapeHtml(row.baseUnit || "-")}</td>
        <td>${currency(row.revenueNet)}</td>
        <td>${currency(row.revenueGoal)}</td>
        <td>${pct(row.goalAttainmentPct)}</td>
        <td>${pct(row.projectedGoalAttainmentPct || 0)}</td>
        <td>${currency(row.ticketAverage)}</td>
        <td>${number(row.distinctClients)}</td>
        <td>${number(row.mixSku)}</td>
        <td>${currency(row.returnsValue)}</td>
        <td>${pct(row.returnRatioPct)}</td>
        <td>${pct(row.discountPct || 0)}</td>
        <td><span class="score-chip">${row.score}</span></td>
      </tr>
    `
    )
    .join("");
}

function unitRows(rows) {
  return rows
    .map(
      (row) => `
      <tr>
        <td>${escapeHtml(row.unitName)}</td>
        <td>${currency(row.revenueNet)}</td>
        <td>${currency(row.revenueGoal)}</td>
        <td>${pct(row.goalAttainmentPct)}</td>
        <td>${pct(row.projectedGoalAttainmentPct || 0)}</td>
        <td>${currency(row.returnsValue)}</td>
        <td>${pct(row.returnRatioPct || 0)}</td>
        <td>${marginText(row.marginValue)}</td>
        <td>${number(row.qtySold || 0)}</td>
        <td>${currency(row.ticketPerPiece || 0)}</td>
        <td>${currency(row.metaDiaria)}</td>
      </tr>
    `
    )
    .join("");
}

function cityRows(rows) {
  return rows
    .map(
      (row) => `
      <tr>
        <td>${escapeHtml(row.cityName)}</td>
        <td>${currency(row.revenueNet)}</td>
        <td>${currency(row.ticketAverage)}</td>
        <td>${number(row.distinctClients)}</td>
        <td>${currency(row.discountValue)}</td>
        <td>${pct(row.discountPct || 0)}</td>
        <td>${currency(row.returnsValue || 0)}</td>
      </tr>
    `
    )
    .join("");
}

async function refreshCurrentTab() {
  const tab = state.activeTab;
  const promises = [];
  // Dados gerais sempre recarregados
  if (["executivo", "vendedores", "unidades", "clientes", "cidades", "descontos", "calendario"].includes(tab)) {
    promises.push(loadDashboard());
  }
  if (tab === "crm-agenda") {
    promises.push(loadTeamActivity(), loadCrmData());
  }
  if (tab === "crm-clientes") {
    promises.push(loadCrmClients({ renderAfterLoad: true, reason: "reload" }), loadPortfolioSummary());
  }
  if (tab === "crm-tarefas" || tab === "crm-interacao") {
    promises.push(loadCrmData());
  }
  if (tab === "placar-equipe" || tab === "meu-placar") {
    promises.push(loadTeamScore());
  }
  if (tab === "importacoes") {
    promises.push(loadAutoImportStatus(), loadAdmin());
  }
  if (tab === "administracao" || tab === "configuracoes") {
    promises.push(loadAdmin());
  }
  // Fallback: recarrega tudo
  if (!promises.length) {
    promises.push(loadDashboard(), loadCrmData());
  }
  await Promise.all(promises);
  addMessage("success", "Dados atualizados.");
}

function topbarActions() {
  const dropdownItems = [
    !roleIsSeller() ? '<button class="dropdown-item" onclick="toggleActionsMenu(); bootstrapSample()">Carregar exemplo</button>' : "",
    `<button class="dropdown-item" onclick="toggleActionsMenu(); downloadFile('/api/export.xlsx?${buildQuery()}')">Exportar Excel</button>`,
    `<button class="dropdown-item" onclick="toggleActionsMenu(); downloadFile('/api/export.pdf?${buildQuery()}')">Exportar PDF</button>`,
  ].filter(Boolean).join("");
  return `
    <div style="display:flex;gap:8px;align-items:center;flex-wrap:wrap">
      <div class="actions-menu" style="flex:1">
        <button class="btn btn-secondary btn-sm" onclick="toggleActionsMenu()">Ações</button>
        <div class="actions-dropdown ${state.ui.actionsMenuOpen ? "open" : ""}">
          ${dropdownItems}
        </div>
      </div>
      <button class="btn btn-ghost btn-sm" onclick="refreshCurrentTab()" title="Atualizar dados da tela atual">↻ Atualizar</button>
      <button class="btn btn-ghost btn-sm" onclick="logout()" style="color:var(--bad);border-color:var(--bad);white-space:nowrap">Sair →</button>
    </div>
  `;
}

function crmStatusBadge(statusCode) {
  const map = {
    ATIVO: "good",
    PRE_INATIVO: "warn",
    INATIVO: "bad",
  };
  return `<span class="status-tag ${map[statusCode] || "warn"}">${escapeHtml(statusCode || "-")}</span>`;
}



function crmSummaryView() {
  if (!state.crm.summary) return `<div class="loader panel">Carregando CRM...</div>`;
  return `
    <div class="kpi-grid">
      ${kpiCard("Carteira priorizada", number(state.crm.summary.portfolioSize), "TOP 5", number(state.crm.summary.top5Count))}
      ${kpiCard("Contatos hoje", number(state.crm.summary.contactsToday), "Sucesso", number(state.crm.summary.successContactsToday))}
      ${kpiCard("Orçamentos hoje", number(state.crm.summary.quotesToday), "Pedidos hoje", number(state.crm.summary.ordersToday))}
      ${kpiCard("Inativos", number(state.crm.summary.inactiveClients), "Pré-inativos", number(state.crm.summary.preInactiveClients))}
      ${kpiCard("Tarefas abertas", number(state.crm.summary.openTasks), "Atrasadas", number(state.crm.summary.overdueTasks))}
    </div>
  `;
}












function vendedoresViewTableOnly() {
  if (!state.dashboard) return `<div class="loader panel">Carregando vendedores...</div>`;
  return `
    <div class="table-card">
      <div class="section-title">
        <div>
          <h3>Ranking completo de vendedores</h3>
          <div class="text-small">Considera apenas classificados como vendedor; pendentes entram na análise e ficam sinalizados.</div>
        </div>
        <div class="list-inline">
          ${Object.entries(state.dashboard.scoreWeights).map(([key, value]) => `<span class="soft-badge">${key}: ${value}%</span>`).join("")}
        </div>
      </div>
      <div class="table-wrap">
        <table>
          <thead>
            <tr>
              <th>Vendedor</th>
              <th>Unidade base</th>
              <th>Líquido</th>
                  <th>Meta</th>
                  <th>% Meta</th>
                  <th>% Meta Proj.</th>
                  <th>Meta diária</th>
                  <th>Ticket</th>
                  <th>Peças</th>
                  <th>Ticket/peça</th>
                  <th>Clientes</th>
                  <th>Mix</th>
                  <th>R$ Desconto</th>
                  <th>% Desconto</th>
                  <th>Devolução</th>
                  <th>% Dev.</th>
                  <th>Margem</th>
                  <th>Score</th>
            </tr>
          </thead>
          <tbody>
            ${state.dashboard.sellerRanking
              .map(
                (row) => `
                <tr>
                  <td>${escapeHtml(row.sellerName)} ${row.pendingMapping ? '<span class="status-tag warn">Pendente</span>' : ""}</td>
                  <td>${escapeHtml(row.baseUnit || "-")}</td>
                  <td>${currency(row.revenueNet)}</td>
                  <td>${currency(row.revenueGoal)}</td>
                  <td>${pct(row.goalAttainmentPct)}</td>
                  <td>${pct(row.projectedGoalAttainmentPct || 0)}</td>
                  <td>${currency(row.metaDiaria)}</td>
                  <td>${currency(row.ticketAverage)}</td>
                  <td>${number(row.qtySold || 0)}</td>
                  <td>${currency(row.ticketPerPiece || 0)}</td>
                  <td>${number(row.distinctClients)}</td>
                  <td>${number(row.mixSku)}</td>
                  <td>${currency(row.discountValue)}</td>
                  <td>${pct(row.discountPct || 0)}</td>
                  <td>${currency(row.returnsValue)}</td>
                  <td>${pct(row.returnRatioPct || 0)}</td>
                  <td>${marginText(row.marginValue)}</td>
                  <td><span class="score-chip">${row.score}</span></td>
                </tr>
              `
              )
              .join("")}
          </tbody>
        </table>
      </div>
    </div>
  `;
}

function cidadesView() {
  if (!state.dashboard) return `<div class="loader panel">Carregando cidades...</div>`;
  return `
    <div class="stack">
      ${loadingBanner()}
      <div class="table-card">
      <div class="section-title">
        <div>
          <h3>Ranking por cidade</h3>
          <div class="text-small">Visão com faturamento líquido, ticket médio e clientes distintos.</div>
        </div>
      </div>
      <div class="table-wrap">
        <table>
          <thead>
              <tr>
                <th>Cidade</th>
                <th>Faturamento líquido</th>
                <th>Ticket médio</th>
                <th>Clientes distintos</th>
                <th>R$ Desconto</th>
                <th>% Desconto</th>
                <th>Devolução</th>
              </tr>
          </thead>
          <tbody>${cityRows(state.dashboard.cityRanking)}</tbody>
        </table>
      </div>
    </div>
  `;
}

function vendedoresView() {
  if (!state.dashboard) return `<div class="loader panel">Carregando vendedores...</div>`;
  const topVisualSellers = state.dashboard.sellerRanking || [];
  return `
    <div class="stack">
      ${loadingBanner()}
      <div class="table-card">
        <div class="section-title">
          <div>
            <h3>Leitura visual dos vendedores</h3>
            <div class="text-small">Resumo rapido para destacar ritmo de meta, qualidade da venda e pontos de atencao.</div>
          </div>
        </div>
        <div class="seller-visual-grid">
          ${topVisualSellers.map((row) => {
            const actualPct = Number(row.goalAttainmentPct || 0);
            const projectedPct = Number(row.projectedGoalAttainmentPct || 0);
            const returnPct = Number(row.returnRatioPct || 0);
            const discountPct = Number(row.discountPct || 0);
            const score = Number(row.score || 0);
            const actualBar = Math.max(0, Math.min(100, (actualPct / 120) * 100));
            const projectedBar = Math.max(0, Math.min(100, (projectedPct / 120) * 100));
            let statusLabel = "Acompanhar";
            let statusTone = "warn";
            if (actualPct >= 100 && score >= 85 && returnPct <= 3) {
              statusLabel = "Destaque";
              statusTone = "good";
            } else if (projectedPct >= 100 && score >= 75) {
              statusLabel = "Boa rota";
              statusTone = "good";
            } else if (actualPct < 80 || returnPct > 4 || discountPct > 25) {
              statusLabel = "Intervir";
              statusTone = "bad";
            }
            return `
              <article class="seller-visual-card">
                <div class="seller-visual-top">
                  <div>
                    <strong>${escapeHtml(row.sellerName)}</strong>
                    <span>${escapeHtml(row.baseUnit || "-")}${row.pendingMapping ? " · pendente de mapeamento" : ""}</span>
                  </div>
                  <div class="seller-visual-badges">
                    <span class="status-tag ${statusTone}">${statusLabel}</span>
                    <span class="score-chip">${row.score}</span>
                  </div>
                </div>
                <div class="seller-visual-mini-grid">
                  <div>
                    <span>Liquido</span>
                    <strong>${currency(row.revenueNet)}</strong>
                  </div>
                  <div>
                    <span>Ticket</span>
                    <strong>${currency(row.ticketAverage)}</strong>
                  </div>
                  <div>
                    <span>Clientes</span>
                    <strong>${number(row.distinctClients)}</strong>
                  </div>
                  <div>
                    <span>Mix</span>
                    <strong>${number(row.mixSku)}</strong>
                  </div>
                </div>
                <div class="seller-visual-bars">
                  <div class="seller-visual-bar-row">
                    <div class="seller-visual-bar-head">
                      <span>% meta atual</span>
                      <strong>${pct(actualPct)}</strong>
                    </div>
                    <div class="seller-progress">
                      <span style="width:${actualBar}%"></span>
                    </div>
                  </div>
                  <div class="seller-visual-bar-row">
                    <div class="seller-visual-bar-head">
                      <span>% meta projetada</span>
                      <strong>${pct(projectedPct)}</strong>
                    </div>
                    <div class="seller-progress projected">
                      <span style="width:${projectedBar}%"></span>
                    </div>
                  </div>
                </div>
                <div class="seller-visual-foot">
                  <span>Dev. ${pct(returnPct)}</span>
                  <span>Desc. ${pct(discountPct)}</span>
                  <span>Ticket/peca ${currency(row.ticketPerPiece || 0)}</span>
                </div>
              </article>
            `;
          }).join("")}
        </div>
      </div>
      ${vendedoresViewTableOnly()}
    </div>
  `;
}

function clientesView() {
  if (!state.dashboard) return `<div class="loader panel">Carregando clientes...</div>`;
  const typeSummary = state.dashboard.clientTypeSummary || {};
  return `
    <div class="stack">
      <div class="grid-3">
        ${kpiCard("Clientes PF", number(typeSummary.PF?.clients || 0), "Faturamento", currency(typeSummary.PF?.revenueNet || 0))}
        ${kpiCard("Clientes PJ", number(typeSummary.PJ?.clients || 0), "Faturamento", currency(typeSummary.PJ?.revenueNet || 0))}
        ${kpiCard("Não classificados", number(typeSummary["Nao classificado"]?.clients || 0), "Faturamento", currency(typeSummary["Nao classificado"]?.revenueNet || 0))}
      </div>
      <div class="table-card">
        <div class="section-title">
          <div>
            <h3>Ranking de clientes</h3>
            <div class="text-small">Faturamento, devolução, desconto e classificação PF/PJ por cliente.</div>
          </div>
          <div class="soft-badge">Exibindo Top 100 clientes por faturamento</div>
        </div>
        <div class="table-wrap">
          <table>
            <thead>
              <tr>
                <th>Cliente</th>
                <th>Tipo</th>
                <th>Faturamento líquido</th>
                <th>R$ Desconto</th>
                <th>% Desconto</th>
                <th>Devolução</th>
              </tr>
            </thead>
            <tbody>
              ${state.dashboard.clientRanking
                .slice(0, 100)
                .map((row) => `<tr><td>${escapeHtml(row.clientName)}</td><td>${escapeHtml(row.personType || "-")}</td><td>${currency(row.revenueNet)}</td><td>${currency(row.discountValue)}</td><td>${pct(row.discountPct || 0)}</td><td>${currency(row.returnsValue || 0)}</td></tr>`)
                .join("")}
            </tbody>
          </table>
        </div>
      </div>
      <div class="stack">
        ${state.dashboard.clientTopByUnit
          .map((group) => `
            <div class="table-card">
              <div class="section-title">
                <div>
                  <h3>Top 10 clientes por unidade: ${escapeHtml(group.unitName)}</h3>
                </div>
              </div>
              <div class="table-wrap">
                <table>
                  <thead><tr><th>Cliente</th><th>Tipo</th><th>Faturamento líquido</th><th>R$ Desconto</th><th>% Desconto</th><th>Devolução</th></tr></thead>
                  <tbody>
                    ${group.clients.map((row) => `<tr><td>${escapeHtml(row.clientName)}</td><td>${escapeHtml(row.personType || "-")}</td><td>${currency(row.revenueNet)}</td><td>${currency(row.discountValue)}</td><td>${pct(row.discountPct || 0)}</td><td>${currency(row.returnsValue || 0)}</td></tr>`).join("")}
                  </tbody>
                </table>
              </div>
            </div>
          `)
          .join("")}
      </div>
    </div>
  `;
}
function calendarView() {
  if (!state.dashboard) return `<div class="loader panel">Carregando calendário...</div>`;
  const calendar = state.dashboard.calendar;
  return `
    <div class="grid-2">
      <div class="timeline-card">
        <div class="section-title">
          <div>
            <h3>Agenda comercial</h3>
            <div class="text-small">Dias úteis, feriados nacionais + RS e projeção da competência.</div>
          </div>
        </div>
        <div class="timeline-list">
          <div class="timeline-item"><strong>Dias úteis do mês</strong><div class="text-small">${calendar.totalWorkingDays}</div></div>
          <div class="timeline-item"><strong>Dias úteis transcorridos</strong><div class="text-small">${calendar.elapsedWorkingDays}</div></div>
          <div class="timeline-item"><strong>Dias úteis restantes</strong><div class="text-small">${calendar.remainingWorkingDays}</div></div>
        </div>
      </div>
      <div class="timeline-card">
        <div class="section-title">
          <div>
            <h3>Feriados da competência</h3>
          </div>
        </div>
        <div class="timeline-list">
          ${calendar.holidays.length ? calendar.holidays.map((item) => `<div class="timeline-item"><strong>${item.date}</strong><div class="text-small">${escapeHtml(item.name)}</div></div>`).join("") : '<div class="timeline-item"><div class="text-small">Nenhum feriado cadastrado no intervalo.</div></div>'}
        </div>
      </div>
    </div>
  `;
}


function adminTableCard(title, keys, rows) {
  return `
    <div class="table-card">
      <div class="section-title"><h3>${title}</h3></div>
      <div class="table-wrap">
        <table>
          <thead><tr>${keys.map((key) => `<th>${escapeHtml(key)}</th>`).join("")}</tr></thead>
          <tbody>
            ${rows
              .slice(0, 30)
              .map((row) => `<tr>${keys.map((key) => `<td>${escapeHtml(row[key] ?? "")}</td>`).join("")}</tr>`)
              .join("")}
          </tbody>
        </table>
      </div>
    </div>
  `;
}

function vacationTableCard() {
  const rows = (state.admin.vacations || []).slice(0, 100);
  const ev = state.crm.editingVacation;
  const showForm = state.crm.showVacationForm || ev !== null;
  const isEdit = ev !== null;

  const formHtml = showForm ? `
    <div style="background:var(--bg-subtle,#f4f6f9);border-radius:10px;padding:16px 18px;margin-bottom:12px;border:1.5px solid ${isEdit ? "var(--accent,#1a5276)" : "var(--border,#dde3ed)"}">
      <div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:12px">
        <strong style="font-size:14px">${isEdit ? "✏️ Editar férias" : "➕ Nova férias"}</strong>
        <button class="btn btn-ghost btn-sm" onclick="cancelEditVacation()">✕ Cancelar</button>
      </div>
      <form onsubmit="saveVacation(event)">
        <div class="two-column-form" style="margin-bottom:10px">
          <div class="field"><label>Nome</label><input id="vac-name" required value="${escapeHtml(ev?.person_name || "")}" /></div>
          <div class="field"><label>Observação</label><input id="vac-notes" value="${escapeHtml(ev?.notes || "")}" /></div>
          <div class="field"><label>Data inicial</label><input id="vac-start" type="date" required value="${escapeHtml(ev?.start_date || "")}" /></div>
          <div class="field"><label>Data final</label><input id="vac-end" type="date" required value="${escapeHtml(ev?.end_date || "")}" /></div>
        </div>
        <div class="actions">
          <button class="btn btn-primary" type="submit">${isEdit ? "💾 Salvar alterações" : "💾 Adicionar férias"}</button>
          <button class="btn btn-ghost" type="button" onclick="cancelEditVacation()">Cancelar</button>
        </div>
      </form>
    </div>
  ` : "";

  return `
    <div class="table-card">
      <div class="section-title">
        <div><h3>Férias</h3><div class="text-small">${rows.length} registro(s)</div></div>
        ${!showForm ? `<button class="btn btn-secondary btn-sm" onclick="state.crm.showVacationForm=true;requestRender()">+ Nova férias</button>` : ""}
      </div>
      ${formHtml}
      <div class="table-wrap">
        <table>
          <thead><tr><th>Colaborador</th><th>Início</th><th>Fim</th><th>Observação</th><th style="width:110px"></th></tr></thead>
          <tbody>
            ${rows.length === 0
              ? `<tr><td colspan="5" style="text-align:center;padding:20px;color:var(--muted)">Nenhuma férias cadastrada</td></tr>`
              : rows.map((row) => `
              <tr style="${ev?.id === row.id ? "background:var(--bg-subtle,#f0f4ff);outline:2px solid var(--accent,#1a5276);outline-offset:-1px" : ""}">
                <td><strong>${escapeHtml(row.person_name || "")}</strong></td>
                <td>${escapeHtml(row.start_date || "")}</td>
                <td>${escapeHtml(row.end_date || "")}</td>
                <td style="color:var(--muted);font-size:12px">${escapeHtml(row.notes || "—")}</td>
                <td style="white-space:nowrap;text-align:right">
                  <button class="btn btn-ghost btn-sm" title="Editar" onclick="editVacation(${row.id})">✏️</button>
                  <button class="btn btn-ghost btn-sm" title="Excluir" style="color:var(--bad)" onclick="deleteVacation(${row.id}, '${escapeHtml(row.person_name || "")}')">🗑</button>
                </td>
              </tr>`).join("")}
          </tbody>
        </table>
      </div>
    </div>
  `;
}

function resetSellerGoalEditor() {
  state.goalEditors.seller = {
    competence: "",
    sellerName: "",
    baseUnit: "",
    revenueGoal: "",
    editing: false,
  };
}

function resetUnitGoalEditor() {
  state.goalEditors.unit = {
    competence: "",
    unitName: "",
    revenueGoal: "",
    editing: false,
  };
}

function editSellerGoal(competence, sellerName) {
  const targetCompetence = decodeURIComponent(String(competence || ""));
  const targetSellerName = decodeURIComponent(String(sellerName || ""));
  const row = (state.admin?.goalsSeller || []).find(
    (item) => item.competence === targetCompetence && item.seller_name === targetSellerName
  );
  if (!row) return;
  state.goalEditors.seller = {
    competence: row.competence || "",
    sellerName: row.seller_name || "",
    baseUnit: row.base_unit || "",
    revenueGoal: row.revenue_goal ?? "",
    editing: true,
  };
  requestRender();
  setTimeout(() => {
    document.getElementById("seller-goal-form")?.scrollIntoView({
      behavior: "smooth",
      block: "start",
    });
    document.getElementById("goal-seller-revenue")?.focus();
  }, 50);
}

function editUnitGoal(competence, unitName) {
  const targetCompetence = decodeURIComponent(String(competence || ""));
  const targetUnitName = decodeURIComponent(String(unitName || ""));
  const row = (state.admin?.goalsUnit || []).find(
    (item) => item.competence === targetCompetence && item.unit_name === targetUnitName
  );
  if (!row) return;
  state.goalEditors.unit = {
    competence: row.competence || "",
    unitName: row.unit_name || "",
    revenueGoal: row.revenue_goal ?? "",
    editing: true,
  };
  requestRender();
  setTimeout(() => {
    document.getElementById("unit-goal-form")?.scrollIntoView({
      behavior: "smooth",
      block: "start",
    });
    document.getElementById("goal-unit-revenue")?.focus();
  }, 50);
}

function cancelSellerGoalEdit() {
  resetSellerGoalEditor();
  requestRender();
}

function cancelUnitGoalEdit() {
  resetUnitGoalEditor();
  requestRender();
}

async function saveSellerGoal(event) {
  event.preventDefault();
  const competence = (document.getElementById("goal-seller-competence")?.value || "").trim();
  const sellerName = (document.getElementById("goal-seller-name")?.value || "").trim();
  const baseUnit = (document.getElementById("goal-seller-unit")?.value || "").trim();
  const revenueGoal = parseFloat(document.getElementById("goal-seller-revenue")?.value || "0");
  if (!competence || !sellerName) return;
  try {
    await api("/api/admin/goals/seller", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ competence, seller_name: sellerName, base_unit: baseUnit, revenue_goal: revenueGoal }),
    });
    resetSellerGoalEditor();
    await loadAdmin();
  } catch (err) {
    alert("Erro ao salvar meta: " + (err.message || err));
  }
}

async function saveUnitGoal(event) {
  event.preventDefault();
  const competence = (document.getElementById("goal-unit-competence")?.value || "").trim();
  const unitName = (document.getElementById("goal-unit-name")?.value || "").trim();
  const revenueGoal = parseFloat(document.getElementById("goal-unit-revenue")?.value || "0");
  if (!competence || !unitName) return;
  try {
    await api("/api/admin/goals/unit", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ competence, unit_name: unitName, revenue_goal: revenueGoal }),
    });
    resetUnitGoalEditor();
    await loadAdmin();
  } catch (err) {
    alert("Erro ao salvar meta: " + (err.message || err));
  }
}

async function deleteSellerGoal(competence, sellerName) {
  const c = decodeURIComponent(String(competence || ""));
  const s = decodeURIComponent(String(sellerName || ""));
  if (!confirm(`Excluir meta de "${s}" em ${c}?`)) return;
  try {
    await api("/api/admin/goals/seller/delete", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ competence: c, seller_name: s }),
    });
    await loadAdmin();
  } catch (err) {
    alert("Erro ao excluir: " + (err.message || err));
  }
}

async function deleteUnitGoal(competence, unitName) {
  const c = decodeURIComponent(String(competence || ""));
  const u = decodeURIComponent(String(unitName || ""));
  if (!confirm(`Excluir meta da unidade "${u}" em ${c}?`)) return;
  try {
    await api("/api/admin/goals/unit/delete", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ competence: c, unit_name: u }),
    });
    await loadAdmin();
  } catch (err) {
    alert("Erro ao excluir: " + (err.message || err));
  }
}

function sellerGoalsTableCard() {
  const rows = state.admin?.goalsSeller || [];
  return `
    <div class="table-card">
      <div class="section-title"><h3>Metas por vendedor</h3></div>
      <div class="table-wrap">
        <table>
          <thead>
            <tr>
              <th>Competência</th>
              <th>Vendedor</th>
              <th>Unidade base</th>
              <th>Meta faturamento</th>
              <th>Ações</th>
            </tr>
          </thead>
          <tbody>
            ${rows
              .slice(0, 50)
              .map(
                (row) => `<tr>
                  <td>${escapeHtml(row.competence || "")}</td>
                  <td>${escapeHtml(row.seller_name || "")}</td>
                  <td>${escapeHtml(row.base_unit || "")}</td>
                  <td>${currency(row.revenue_goal || 0)}</td>
                  <td>
                    <div class="table-actions">
                      <button class="btn btn-ghost btn-sm" type="button" onclick="editSellerGoal('${encodeURIComponent(row.competence || "")}','${encodeURIComponent(row.seller_name || "")}')">Editar</button>
                      <button class="btn btn-ghost btn-sm" type="button" onclick="deleteSellerGoal('${encodeURIComponent(row.competence || "")}','${encodeURIComponent(row.seller_name || "")}')">Excluir</button>
                    </div>
                  </td>
                </tr>`
              )
              .join("")}
          </tbody>
        </table>
      </div>
    </div>
  `;
}

function unitGoalsTableCard() {
  const rows = state.admin?.goalsUnit || [];
  return `
    <div class="table-card">
      <div class="section-title"><h3>Metas por unidade</h3></div>
      <div class="table-wrap">
        <table>
          <thead>
            <tr>
              <th>Competência</th>
              <th>Unidade</th>
              <th>Meta faturamento</th>
              <th>Ações</th>
            </tr>
          </thead>
          <tbody>
            ${rows
              .slice(0, 50)
              .map(
                (row) => `<tr>
                  <td>${escapeHtml(row.competence || "")}</td>
                  <td>${escapeHtml(row.unit_name || "")}</td>
                  <td>${currency(row.revenue_goal || 0)}</td>
                  <td>
                    <div class="table-actions">
                      <button class="btn btn-ghost btn-sm" type="button" onclick="editUnitGoal('${encodeURIComponent(row.competence || "")}','${encodeURIComponent(row.unit_name || "")}')">Editar</button>
                      <button class="btn btn-ghost btn-sm" type="button" onclick="deleteUnitGoal('${encodeURIComponent(row.competence || "")}','${encodeURIComponent(row.unit_name || "")}')">Excluir</button>
                    </div>
                  </td>
                </tr>`
              )
              .join("")}
          </tbody>
        </table>
      </div>
    </div>
  `;
}

function usersAdminTableCard() {
  const rows = state.admin?.users || [];
  return `
    <div class="table-card">
      <div class="section-title"><h3>Usuários</h3></div>
      <div class="table-wrap">
        <table>
          <thead>
            <tr>
              <th>Usuário</th>
              <th>Nome</th>
              <th>Perfil</th>
              <th>Pessoa vinculada</th>
              <th>Unidades vinculadas</th>
              <th>Status</th>
              <th>Ações</th>
            </tr>
          </thead>
          <tbody>
            ${rows
              .slice(0, 30)
              .map(
                (row) => `<tr>
                    <td>${escapeHtml(row.username || "")}</td>
                    <td>${escapeHtml(row.full_name || "")}</td>
                    <td>${escapeHtml(row.role || "")}</td>
                    <td>${escapeHtml(row.linked_person_name || "")}</td>
                    <td>${escapeHtml(row.linked_units_display || "")}</td>
                    <td>${row.is_active ? "Ativo" : "Inativo"}</td>
                    <td>
                      <div class="actions">
                        <button class="btn btn-ghost" type="button" onclick="editUser(${Number(row.id)})">Editar</button>
                        <button class="btn btn-ghost" type="button" onclick="startPasswordChange(${Number(row.id)})">Trocar senha</button>
                        <button class="btn btn-ghost" type="button" onclick="deleteUser(${Number(row.id)})">Excluir</button>
                      </div>
                    </td>
                  </tr>`
              )
              .join("")}
          </tbody>
        </table>
      </div>
    </div>
  `;
}

function pendingIssueDefaultDate(issue) {
  return issue?.competence ? `${issue.competence}-01` : "";
}

function pendingIssueCards() {
  const pendingIssues = (state.admin?.issues || []).filter((item) => item.status === "pendente");
  if (!pendingIssues.length) {
    return `<div class="message success">Nenhuma pendência aberta no momento.</div>`;
  }
  return pendingIssues
    .slice(0, 50)
    .map((issue) => {
      if (issue.issue_type === "vendedor_sem_vinculo") {
        return `
          <div class="form-card subtle-card">
            <div class="section-title">
              <div>
                <h3>Vendedor sem vínculo</h3>
                <div class="text-small">${escapeHtml(issue.reference_value)} · competência ${escapeHtml(issue.competence)}</div>
              </div>
              <div class="soft-badge">ID ${issue.id}</div>
            </div>
            <div class="two-column-form">
              <div class="field">
                <label>Nome</label>
                <input id="issue-person-name-${issue.id}" value="${escapeHtml(issue.reference_value)}" />
              </div>
              <div class="field">
                <label>Classificação</label>
                <select id="issue-person-role-${issue.id}">
                  <option>Vendedor</option>
                  <option>Gerente</option>
                  <option>Outro</option>
                </select>
              </div>
              <div class="field">
                <label>Unidade base</label>
                <select id="issue-person-unit-${issue.id}">
                  <option value="">Selecione</option>
                  ${state.options.units.map((unit) => `<option value="${escapeHtml(unit)}">${escapeHtml(unit)}</option>`).join("")}
                </select>
              </div>
              <div class="field">
                <label>Vigência inicial</label>
                <input id="issue-valid-from-${issue.id}" type="date" value="${pendingIssueDefaultDate(issue)}" />
              </div>
            </div>
            <div class="actions">
              <button class="btn btn-primary" onclick="resolveIssue(${issue.id}, 'seller')">Resolver vendedor</button>
              <button class="btn btn-ghost" onclick="ignoreIssue(${issue.id})">Ignorar</button>
            </div>
          </div>
        `;
      }
      if (issue.issue_type === "cidade_sem_correspondencia") {
        return `
          <div class="form-card subtle-card">
            <div class="section-title">
              <div>
                <h3>Cidade sem correspondência</h3>
                <div class="text-small">${escapeHtml(issue.reference_value)} · competência ${escapeHtml(issue.competence)}</div>
              </div>
              <div class="soft-badge">ID ${issue.id}</div>
            </div>
            <div class="two-column-form">
              <div class="field">
                <label>Cidade</label>
                <input id="issue-city-name-${issue.id}" value="${escapeHtml(issue.reference_value)}" />
              </div>
              <div class="field">
                <label>Unidade principal</label>
                <select id="issue-city-unit-${issue.id}">
                  <option value="">Selecione</option>
                  ${state.options.units.map((unit) => `<option value="${escapeHtml(unit)}">${escapeHtml(unit)}</option>`).join("")}
                </select>
              </div>
              <div class="field">
                <label>Vigência inicial</label>
                <input id="issue-city-valid-from-${issue.id}" type="date" value="${pendingIssueDefaultDate(issue)}" />
              </div>
            </div>
            <div class="actions">
              <button class="btn btn-primary" onclick="resolveIssue(${issue.id}, 'city')">Resolver cidade</button>
              <button class="btn btn-ghost" onclick="ignoreIssue(${issue.id})">Ignorar</button>
            </div>
          </div>
        `;
      }
      return `
        <div class="form-card subtle-card">
          <div class="section-title">
            <div>
              <h3>${escapeHtml(issue.issue_type)}</h3>
              <div class="text-small">${escapeHtml(issue.reference_value)} · competência ${escapeHtml(issue.competence)}</div>
            </div>
          </div>
          <div class="actions">
            <button class="btn btn-ghost" onclick="ignoreIssue(${issue.id})">Ignorar</button>
          </div>
        </div>
      `;
    })
    .join("");
}



function resetFilters() {
  state.filters = {
    competenceStart: state.options.competences[0] || "",
    competenceEnd: state.options.competences[0] || "",
    unit: "",
    seller: "",
    city: "",
  };
  applyMainFilters();
}

function switchTab(tab) {
  if (state.user && !allowedTabsForUser(state.user).includes(tab)) {
    state.activeTab = defaultTabForUser(state.user);
    state.ui.actionsMenuOpen = false;
    requestRender();
    return;
  }
  state.activeTab = tab;
  state.ui.actionsMenuOpen = false;
  requestRender();
}

function closeCrmModal() {
  state.crm.modal = null;
  requestRender();
}

function openAgendaActionModal(clientKey, clientName, actionType) {
  state.crm.modal = {
    type: "AGENDA_ACTION",
    clientKey,
    clientName,
    actionType,
    justification: "",
    nextVisibleAt: "",
  };
  requestRender();
}

function openTaskRescheduleModal(taskId) {
  state.crm.modal = {
    type: "TASK_RESCHEDULE",
    taskId,
    dueAt: "",
  };
  requestRender();
}

async function applyMainFilters() {
  setLoading("filters", true);
  requestRender();
  try {
    // Filtros de período/unidade/vendedor afetam só o dashboard.
    // CRM usa sua própria filtragem independente — não recarregar aqui.
    await loadDashboard();
  } finally {
    setLoading("filters", false);
  }
  requestRender();
}









// --- UX refresh: layout, CRM and role-specific home views ---

function crmRecommendedAction(item) {
  if (item.statusCode === "INATIVO") return "Reativar cliente com proposta objetiva e retorno agendado.";
  if (item.statusCode === "PRE_INATIVO") return "Contato preventivo hoje para não perder frequência.";
  if (Number(item.currentRevenue || 0) <= 0) return "Provocar compra no mês com foco no mix principal.";
  if (Number(item.growthPct || 0) < -0.03) return "Investigar queda recente e atuar na principal linha perdida.";
  return "Ampliar relacionamento e explorar crescimento de mix.";
}

function crmGrowthBadge(value) {
  const numeric = Number(value || 0);
  const tone = numeric > 0.03 ? "good" : numeric < -0.03 ? "bad" : "warn";
  return `<span class="status-tag ${tone}">${escapeHtml(growthLabel(numeric))}</span>`;
}

function sellerPerformanceSnapshot() {
  const sellerName = state.user?.linkedPersonName || state.user?.fullName || state.user?.username;
  return (state.dashboard?.sellerRanking || []).find((row) => row.sellerName === sellerName) || state.dashboard?.sellerRanking?.[0] || null;
}

function buildManagementAlerts() {
  const alerts = [];
  const units = state.dashboard?.unitPerformance || [];
  const sellers = state.dashboard?.sellerRanking || [];
  const cities = state.dashboard?.cityRanking || [];
  const crmClients = state.crm.clients || [];
  const issues = state.admin?.issues || [];

  const weakUnit = units.find((row) => Number(row.projectedGoalAttainmentPct || 0) < 90);
  if (weakUnit) {
    alerts.push({
      type: "Crítico",
      title: "Unidade abaixo da meta projetada",
      description: `${weakUnit.unitName} está com projeção de ${pct(weakUnit.projectedGoalAttainmentPct || 0)} da meta.`,
      actionLabel: "Ver unidade",
      action: "switchTab('unidades')",
    });
  }

  const highReturnSeller = sellers.find((row) => Number(row.returnRatioPct || 0) >= 5);
  if (highReturnSeller) {
    alerts.push({
      type: "Atenção",
      title: "Vendedor com devolução alta",
      description: `${highReturnSeller.sellerName} está com devolução em ${pct(highReturnSeller.returnRatioPct || 0)}.`,
      actionLabel: "Ver vendedor",
      action: "switchTab('vendedores')",
    });
  }

  const highDiscountSeller = sellers.find((row) => Number(row.discountPct || 0) >= 20);
  if (highDiscountSeller) {
    alerts.push({
      type: "Atenção",
      title: "Vendedor com desconto alto",
      description: `${highDiscountSeller.sellerName} aplicou ${pct(highDiscountSeller.discountPct || 0)} em desconto.`,
      actionLabel: "Ver vendedor",
      action: "switchTab('descontos')",
    });
  }

  const relevantPreInactive = crmClients.find((client) => client.statusCode === "PRE_INATIVO" && ["DIAMANTE", "OURO"].includes(client.classCode));
  if (relevantPreInactive) {
    alerts.push({
      type: "Atenção",
      title: "Cliente pré-inativo relevante",
      description: `${relevantPreInactive.clientName} exige contato preventivo imediato.`,
      actionLabel: "Ver cliente",
      action: `openCrmClient('${escapeHtml(relevantPreInactive.clientKey)}')`,
    });
  }

  const recoveryClient = crmClients.find((client) => client.statusCode === "INATIVO" && Number(client.averageRevenue || 0) > 1000);
  if (recoveryClient) {
    alerts.push({
      type: "Oportunidade",
      title: "Cliente inativo com potencial de recuperação",
      description: `${recoveryClient.clientName} tem histórico relevante e está sem compra.`,
      actionLabel: "Ir para CRM",
      action: `openCrmClient('${escapeHtml(recoveryClient.clientKey)}')`,
    });
  }

  const cityOpportunity = cities[0];
  if (cityOpportunity) {
    alerts.push({
      type: "Oportunidade",
      title: "Cidade com oportunidade comercial",
      description: `${cityOpportunity.cityName} concentra ${number(cityOpportunity.distinctClients || 0)} clientes e ticket médio de ${currency(cityOpportunity.ticketAverage)}.`,
      actionLabel: "Ver cidade",
      action: "switchTab('cidades')",
    });
  }

  const pendingIssue = issues.find((item) => item.status === "pendente");
  if (pendingIssue) {
    alerts.push({
      type: "Crítico",
      title: "Pendência de cadastro/importação",
      description: `${pendingIssue.issue_type}: ${pendingIssue.reference_value}.`,
      actionLabel: "Resolver pendência",
      action: "switchTab('administracao')",
    });
  }

  return alerts.slice(0, 6);
}

function managementAlertCard(item) {
  const toneClass = item.type === "Crítico" ? "bad" : item.type === "Oportunidade" ? "good" : "warn";
  return `
    <article class="alert-card ${toneClass}">
      <div class="alert-top">
        <span class="status-tag ${toneClass}">${escapeHtml(item.type)}</span>
        <strong>${escapeHtml(item.title)}</strong>
      </div>
      <p>${escapeHtml(item.description)}</p>
      <div class="actions">
        <button class="btn btn-secondary" onclick="${item.action}">${escapeHtml(item.actionLabel)}</button>
      </div>
    </article>
  `;
}

function crmAgendaCard(item) {
  const expanded = Boolean(state.ui.crmAgendaExpanded[item.clientKey]);
  return `
    <article class="crm-card clean">
      <div class="crm-card-top">
        <div>
          <strong>${escapeHtml(item.clientKey || "-")} · ${escapeHtml(item.clientName)}</strong>
          <div class="text-small">${escapeHtml(item.cityName || "-")} · ${escapeHtml(item.statusCode || "-")} · ${escapeHtml(item.classCode || "-")}</div>
        </div>
        ${crmStatusBadge(item.statusCode)}
      </div>
      <div class="crm-card-essentials">
        <div><span>Telefone atualizado</span><strong>${escapeHtml(item.phone || "Não informado")}</strong></div>
        <div><span>Contato principal</span><strong>${escapeHtml(item.primaryContactName || "Não informado")}</strong></div>
        <div><span>Compra no mês</span><strong>${Number(item.currentRevenue || 0) > 0 ? "Com compra" : "Sem compra"}</strong></div>
        <div><span>Motivo principal</span><strong>${escapeHtml(item.primaryReason || "-")}</strong></div>
        <div><span>Ação recomendada</span><strong>${escapeHtml(crmRecommendedAction(item))}</strong></div>
      </div>
      ${expanded ? `
        <div class="crm-mini-grid">
          <div><span>Classe</span><strong>${escapeHtml(item.classCode || "-")}</strong></div>
          <div><span>Última compra</span><strong>${escapeHtml(item.lastPurchaseAt ? item.lastPurchaseAt.slice(0, 10) : "-")}</strong></div>
          <div><span>Dias sem compra</span><strong>${number(item.daysWithoutPurchase || 0)}</strong></div>
          <div><span>Mês atual</span><strong>${currency(item.currentRevenue)}</strong></div>
          <div><span>Média trim.</span><strong>${currency(item.averageRevenue)}</strong></div>
          <div><span>Crescimento</span><strong>${pct((item.growthPct || 0) * 100)}</strong></div>
        </div>
      ` : ""}
      <div class="actions" style="padding-top:8px;border-top:1px solid var(--line)">
        <button class="btn btn-secondary" onclick="openCrmClient('${escapeHtml(item.clientKey)}', false)">Abrir ficha</button>
        <button class="btn btn-primary" onclick="prefillInteractionFromAgenda('${escapeHtml(item.clientKey)}')">Registrar contato</button>
        <button class="btn btn-ghost" onclick="openContactUpdateModal('${escapeHtml(item.clientKey)}')">Atualizar contato</button>
        <button class="btn btn-ghost" onclick="openAgendaActionModal('${escapeHtml(item.clientKey)}','${escapeHtml(item.clientName)}','ADIAR')">Adiar</button>
        <button class="btn btn-ghost" onclick="toggleAgendaDetails('${escapeHtml(item.clientKey)}')">${expanded ? "Ocultar detalhes" : "Ver detalhes"}</button>
      </div>
    </article>
  `;
}

function sellerHomeCards() {
  const seller = sellerPerformanceSnapshot();
  if (!seller) return "";
  return `
    <div class="grid-2">
      ${kpiCard("Meu resultado comercial", currency(seller.revenueNet), "Meta", currency(seller.revenueGoal))}
      ${kpiCard("Meus indicadores detalhados", pct(seller.goalAttainmentPct), "Score", seller.score)}
    </div>
  `;
}

function todayTaskGroups() {
  const rows = state.crm.taskRows || [];
  const today = new Date().toISOString().slice(0, 10);
  return {
    overdue: rows.filter((row) => row.status === "ATRASADA"),
    dueToday: rows.filter((row) => String(row.due_at || "").slice(0, 10) === today && row.status !== "CONCLUIDA"),
  };
}

function missionProgressBar(done, total) {
  const pct = total > 0 ? Math.round((done / total) * 100) : 0;
  const tone = done >= total ? "good" : done > 0 ? "warn" : "";
  return `
    <div style="margin-bottom:4px;display:flex;justify-content:space-between;align-items:center">
      <span style="font-weight:700;font-size:13px">${done >= total ? "🎯 Missão cumprida!" : `${done} de ${total} contatos feitos hoje`}</span>
      <span class="soft-badge">${pct}%</span>
    </div>
    <div class="score-bar-track" style="height:12px;border-radius:6px">
      <div class="score-bar-fill ${tone}" style="width:${pct}%;height:12px;border-radius:6px;transition:width 0.4s"></div>
    </div>
  `;
}

function crmAgendaView() {
  if (!state.crm.summary) return `<div class="loader panel">Carregando agenda do CRM...</div>`;
  const { overdue, dueToday } = todayTaskGroups();
  const top5 = state.crm.agenda.top5 || [];
  const contactsDone = state.crm.summary?.contactsToday || 0;

  // Motivo do contato por cliente
  function contactReason(item) {
    if (item.statusCode === "INATIVO") return "🔴 Inativo — reativar";
    if (item.statusCode === "PRE_INATIVO") return "🟡 Pré-inativo — prevenir";
    if (Number(item.currentRevenue || 0) <= 0) return "🟡 Sem compra este mês";
    return "🟢 Ativo — mix/recorrência";
  }

  function agendaCardV2(item) {
    const expanded = Boolean(state.ui.crmAgendaExpanded[item.clientKey]);
    const classBadge = { DIAMANTE: "💎", OURO: "🥇", PRATA: "🥈", BRONZE: "🥉" }[item.classCode] || "⚪";
    return `
      <article class="crm-card clean" style="border-left:4px solid ${item.statusCode === "INATIVO" ? "#e74c3c" : item.statusCode === "PRE_INATIVO" ? "#f39c12" : "#27ae60"}">
        <div class="crm-card-top">
          <div>
            <div style="font-size:12px;color:var(--muted);margin-bottom:4px">${contactReason(item)}</div>
            <strong>${classBadge} ${escapeHtml(item.clientName)}</strong>
            <div class="text-small">${escapeHtml(item.cityName || "-")} · ${escapeHtml(item.classCode || "-")}</div>
          </div>
          ${crmStatusBadge(item.statusCode)}
        </div>
        <div style="display:grid;grid-template-columns:1fr 1fr;gap:8px;margin:8px 0">
          <div class="crm-card-essentials" style="margin:0"><div><span>Telefone</span><strong>${escapeHtml(item.phone || "Não informado")}</strong></div></div>
          <div class="crm-card-essentials" style="margin:0"><div><span>Motivo principal</span><strong>${escapeHtml(item.primaryReason || "-")}</strong></div></div>
        </div>
        ${expanded ? `
          <div style="display:grid;grid-template-columns:repeat(3,1fr);gap:8px;margin:8px 0">
            <div class="crm-card-essentials" style="margin:0"><div><span>Última compra</span><strong>${escapeHtml(item.lastPurchaseAt ? item.lastPurchaseAt.slice(0,10) : "-")}</strong></div></div>
            <div class="crm-card-essentials" style="margin:0"><div><span>Mês atual</span><strong>${currency(item.currentRevenue)}</strong></div></div>
            <div class="crm-card-essentials" style="margin:0"><div><span>Média trim.</span><strong>${currency(item.averageRevenue)}</strong></div></div>
          </div>
        ` : ""}
        <div class="actions" style="padding-top:8px;border-top:1px solid var(--line)">
          <button class="btn btn-secondary" onclick="openCrmClient('${escapeHtml(item.clientKey)}', false)">Abrir ficha</button>
          <button class="btn btn-primary" onclick="prefillInteractionFromAgenda('${escapeHtml(item.clientKey)}')">Registrar contato</button>
          <button class="btn btn-ghost" onclick="openContactUpdateModal('${escapeHtml(item.clientKey)}')">Atualizar</button>
          <button class="btn btn-ghost" onclick="openAgendaActionModal('${escapeHtml(item.clientKey)}','${escapeHtml(item.clientName)}','ADIAR')">Adiar</button>
          <button class="btn btn-ghost" onclick="toggleAgendaDetails('${escapeHtml(item.clientKey)}')">${expanded ? "−" : "+"}</button>
        </div>
      </article>
    `;
  }

  if (roleIsSeller()) {
    return `
      <div class="stack">
        <div class="panel" style="background:linear-gradient(135deg,#0f3044,#1a5276);color:#fff;border:none;padding:20px 24px">
          <div class="eyebrow" style="color:#f4c25f;font-weight:800;margin-bottom:8px">🎯 MISSÃO DO DIA</div>
          <h3 style="color:#fff;margin:0 0 4px">${firstName(state.user?.fullName || state.user?.username)}, aqui está sua fila de hoje.</h3>
          <div style="font-size:13px;color:rgba(255,255,255,0.7);margin-bottom:16px">Regra de ouro: ligar sem proposta é desperdício. 1 oferta + 1 pergunta por cliente.</div>
          ${missionProgressBar(contactsDone, 5)}
        </div>

        ${overdue.length > 0 ? `
          <div class="table-card" style="border-left:4px solid #e74c3c">
            <div class="section-title">
              <div><h3>⚠️ Tarefas atrasadas</h3><div class="text-small">Resolva antes de começar os contatos do dia.</div></div>
              <div class="soft-badge" style="background:#fde8e8;color:#e74c3c">${overdue.length}</div>
            </div>
            <div class="timeline-list">
              ${overdue.map((row) => `<div class="timeline-item"><strong>${escapeHtml(row.client_name)}</strong><div class="text-small">${escapeHtml((row.due_at || "").replace("T", " ").slice(0,16))}</div><div class="actions"><button class="btn btn-secondary" onclick="completeCrmTask(${Number(row.id)})">Concluir</button><button class="btn btn-ghost" onclick="openTaskRescheduleModal(${Number(row.id)})">Reagendar</button></div></div>`).join("")}
            </div>
          </div>
        ` : ""}

        ${dueToday.length > 0 ? `
          <div class="table-card" style="border-left:4px solid #f39c12">
            <div class="section-title">
              <div><h3>📅 Retornos de hoje</h3></div>
              <div class="soft-badge">${dueToday.length}</div>
            </div>
            <div class="timeline-list">
              ${dueToday.map((row) => `<div class="timeline-item"><strong>${escapeHtml(row.client_name)}</strong><div class="text-small">${escapeHtml(row.title || "")}</div></div>`).join("")}
            </div>
          </div>
        ` : ""}

        <div>
          <div class="section-title" style="margin-bottom:12px">
            <h3>📋 TOP 5 — Contatos do dia</h3>
            <div class="text-small">2 Bronze/Prata · 2 Ouro/Diamante · 1 prospecção/inativo</div>
          </div>
          <div class="stack">
            ${top5.map((item) => agendaCardV2(item)).join("") || emptyStateCard("Sua fila está vazia. Todos os clientes estão ativos!")}
          </div>
        </div>

        ${sellerHomeCards()}
      </div>
    `;
  }

  // Visão gerente/admin — painel estratégico
  const ta = state.crm.teamActivity;
  const taLoading = !ta;
  const taSellers = ta?.sellers || [];

  // Agrupar vendedores por unidade para exibição
  const sellersByUnit = {};
  for (const s of taSellers) {
    const u = s.unit || "Sem Unidade";
    if (!sellersByUnit[u]) sellersByUnit[u] = [];
    sellersByUnit[u].push(s);
  }

  function sellerActivityCard(s) {
    const pct = ta?.teamGoal > 0 ? Math.min(Math.round((s.contactsToday / 5) * 100), 100) : 0;
    const color = s.contactsToday >= 5 ? "#27ae60" : s.contactsToday >= 3 ? "#f39c12" : s.contactsToday >= 1 ? "#e67e22" : "#e74c3c";
    return `
      <div style="background:#f7fafc;border:1px solid var(--line);border-radius:8px;padding:10px 12px;min-width:0;flex:1 1 150px;max-width:200px;overflow:hidden">
        <div style="display:flex;justify-content:space-between;align-items:flex-start;gap:8px">
          <div>
            <div style="font-size:12px;font-weight:700;color:var(--text);white-space:nowrap;overflow:hidden;text-overflow:ellipsis;max-width:110px">${escapeHtml(s.sellerName.split(" ")[0])}</div>
            <div style="font-size:10px;color:var(--muted);margin-top:2px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;max-width:110px">${escapeHtml(s.sellerName.split(" ").slice(1,3).join(" "))}</div>
          </div>
          <div style="text-align:right">
            <div style="font-size:22px;font-weight:800;color:${color};line-height:1">${s.contactsToday}</div>
            <div style="font-size:10px;color:var(--muted)">de 5</div>
          </div>
        </div>
        <div style="margin-top:8px;background:var(--line);border-radius:4px;height:5px">
          <div style="width:${pct}%;height:5px;border-radius:4px;background:${color};transition:width .3s"></div>
        </div>
        ${s.overdueTasks > 0 ? `<div style="font-size:11px;color:#e74c3c;margin-top:4px">⚠ ${s.overdueTasks} tarefa${s.overdueTasks > 1 ? "s" : ""} atrasada${s.overdueTasks > 1 ? "s" : ""}</div>` : ""}
      </div>
    `;
  }

  const noContactSellers = taSellers.filter((s) => s.contactsToday === 0);

  return `
    <div class="stack">

      <!-- Cabeçalho estratégico compacto -->
      <div class="panel" style="background:linear-gradient(135deg,#0f3044,#1a5276);color:#fff;border:none;padding:14px 20px">
        <div style="display:flex;align-items:center;justify-content:space-between;gap:12px;flex-wrap:wrap">
          <div>
            <div style="font-size:10px;font-weight:800;color:#f4c25f;letter-spacing:0.08em;text-transform:uppercase;margin-bottom:2px">📊 Painel Gerencial — Missão do Dia</div>
            <div style="font-size:13px;color:rgba(255,255,255,0.7)">Acompanhamento da equipe em tempo real</div>
          </div>
          <div style="display:flex;flex-wrap:wrap;gap:8px">
            <div style="background:rgba(255,255,255,0.12);border-radius:8px;padding:8px 16px;text-align:center;min-width:90px">
              <div style="font-size:24px;font-weight:800;color:#f4c25f;line-height:1.1">${taLoading ? "…" : number(ta.totalContactsToday)}</div>
              <div style="font-size:10px;color:rgba(255,255,255,0.7);margin-top:2px">Contatos hoje</div>
              <div style="font-size:10px;color:rgba(255,255,255,0.45)">meta ${taLoading ? "…" : number(ta.teamGoal)}</div>
            </div>
            <div style="background:rgba(255,255,255,0.12);border-radius:8px;padding:8px 16px;text-align:center;min-width:90px">
              <div style="font-size:24px;font-weight:800;color:${taLoading ? "#fff" : ta.goalPct >= 100 ? "#2ecc71" : ta.goalPct >= 60 ? "#f4c25f" : "#e74c3c"};line-height:1.1">${taLoading ? "…" : ta.goalPct + "%"}</div>
              <div style="font-size:10px;color:rgba(255,255,255,0.7);margin-top:2px">da meta</div>
            </div>
            <div style="background:rgba(255,255,255,0.12);border-radius:8px;padding:8px 16px;text-align:center;min-width:90px">
              <div style="font-size:24px;font-weight:800;color:#2ecc71;line-height:1.1">${taLoading ? "…" : number(ta.sellersWithContact)}</div>
              <div style="font-size:10px;color:rgba(255,255,255,0.7);margin-top:2px">Com contato</div>
            </div>
            <div style="background:rgba(255,255,255,0.12);border-radius:8px;padding:8px 16px;text-align:center;min-width:90px">
              <div style="font-size:24px;font-weight:800;color:${taLoading ? "#fff" : ta.sellersWithoutContact > 0 ? "#e74c3c" : "#2ecc71"};line-height:1.1">${taLoading ? "…" : number(ta.sellersWithoutContact)}</div>
              <div style="font-size:10px;color:rgba(255,255,255,0.7);margin-top:2px">Sem contato</div>
            </div>
          </div>
        </div>
      </div>

      <!-- Alerta: vendedores sem contato -->
      ${noContactSellers.length > 0 ? `
        <div class="message error" style="padding:10px 14px">
          <div style="display:flex;align-items:center;gap:8px;margin-bottom:6px">
            <span style="font-size:16px">🚨</span>
            <strong>Sem contato hoje (${noContactSellers.length}):</strong>
          </div>
          <div style="display:flex;flex-wrap:wrap;gap:4px">
            ${noContactSellers.map((s) => `<span style="background:rgba(191,78,78,0.12);color:var(--bad);padding:2px 8px;border-radius:4px;font-size:12px;white-space:nowrap">${escapeHtml(s.sellerName.split(" ")[0])}</span>`).join(" ")}
          </div>
        </div>
      ` : (taSellers.length > 0 ? `<div class="message success">✅ Todos os vendedores já realizaram contatos hoje.</div>` : "")}

      <!-- Cards por unidade -->
      ${taLoading ? `<div class="loader panel">Carregando atividade da equipe…</div>` : Object.entries(sellersByUnit).map(([unit, sellers]) => `
        <div class="table-card">
          <div class="section-title">
            <div><h3>${escapeHtml(unit)}</h3><div class="text-small">${sellers.length} vendedor${sellers.length !== 1 ? "es" : ""} · ${sellers.reduce((s, r) => s + r.contactsToday, 0)} contatos hoje</div></div>
          </div>
          <div style="display:flex;flex-wrap:wrap;gap:10px;padding:4px 0">
            ${sellers.map(sellerActivityCard).join("")}
          </div>
        </div>
      `).join("") || emptyStateCard("Nenhum vendedor com meta cadastrada neste mês.")}

      <!-- Clientes prioritários + tarefas -->
      <div class="grid-2 crm-grid">
        <div class="table-card">
          <div class="section-title">
            <div><h3>Clientes prioritários da unidade</h3><div class="text-small">Clientes de maior risco na fila.</div></div>
            <div class="soft-badge">${number(top5.length)}</div>
          </div>
          <div class="stack">
            ${top5.map((item) => crmAgendaCard(item)).join("") || emptyStateCard("Sem clientes priorizados no momento.")}
          </div>
        </div>
        <div class="stack">
          <div class="table-card">
            <div class="section-title">
              <div><h3>Tarefas atrasadas</h3></div>
              <div class="soft-badge" style="${overdue.length > 0 ? "background:#fde8e8;color:#e74c3c" : ""}">${number(overdue.length)}</div>
            </div>
            <div class="timeline-list">
              ${overdue.map((row) => `<div class="timeline-item"><strong>${escapeHtml(row.client_name)}</strong><div class="text-small">${escapeHtml((row.due_at || "").replace("T", " ").slice(0,16))}</div><div class="actions"><button class="btn btn-secondary" onclick="completeCrmTask(${Number(row.id)})">Concluir</button><button class="btn btn-ghost" onclick="openTaskRescheduleModal(${Number(row.id)})">Reagendar</button></div></div>`).join("") || '<div class="timeline-item"><div class="text-small">Nenhuma tarefa atrasada.</div></div>'}
            </div>
          </div>
          <div class="table-card">
            <div class="section-title">
              <div><h3>Retornos de hoje</h3></div>
              <div class="soft-badge">${number(dueToday.length)}</div>
            </div>
            <div class="timeline-list">
              ${dueToday.map((row) => `<div class="timeline-item"><strong>${escapeHtml(row.client_name)}</strong><div class="text-small">${escapeHtml(row.title || "")}</div></div>`).join("") || '<div class="timeline-item"><div class="text-small">Nenhum retorno vencendo hoje.</div></div>'}
            </div>
          </div>
        </div>
      </div>
    </div>
  `;
}

function crmFilterToolbar() {
  const filters = state.crm.crmClientFilters;
  const pagination = state.crm.pagination;
  const start = pagination.total ? ((pagination.page - 1) * pagination.pageSize) + 1 : 0;
  const end = pagination.total ? Math.min(pagination.page * pagination.pageSize, pagination.total) : 0;
  const isLoading = Boolean(state.ui.loading.crmClients);
  return `
    <div class="crm-filter-shell">
      ${isLoading ? `<div class="message" style="background:rgba(15,48,68,0.07);color:var(--accent);font-weight:600;margin-bottom:8px">⏳ Filtrando clientes…</div>` : ""}
      <div class="crm-search-row">
        <div class="field field-grow">
          <label>Buscar cliente</label>
          <input
            value="${escapeHtml(filters.search || "")}"
            placeholder="Código, nome, cidade, telefone ou contato"
            oninput="state.crm.crmClientFilters.search=this.value"
            onkeydown="if(event.key==='Enter'){event.preventDefault();runCrmClientSearch();}"
          />
        </div>
        <div class="actions">
          <button class="btn btn-secondary" onclick="runCrmClientSearch()">Buscar</button>
          <button class="btn btn-ghost" onclick="clearCrmClientFilters()">Limpar filtros</button>
        </div>
      </div>
      <div class="filter-grid crm-filter-grid">
        <div class="field">
          <label>Unidade</label>
          <select onchange="updateCrmClientFilter('unit', this.value)">
            <option value="">Todas</option>
            ${(state.options.units || []).map((u) => `<option value="${escapeHtml(u)}" ${filters.unit === u ? "selected" : ""}>${escapeHtml(u)}</option>`).join("")}
          </select>
        </div>
        <div class="field">
          <label>Vendedor</label>
          <select onchange="updateCrmClientFilter('seller', this.value)">
            <option value="">Todos</option>
            ${sellersForCrmFilter().map((s) => `<option value="${escapeHtml(s)}" ${filters.seller === s ? "selected" : ""}>${escapeHtml(s)}</option>`).join("")}
          </select>
        </div>
        <div class="field">
          <label>Status do cliente</label>
          <select onchange="updateCrmClientFilter('status', this.value)">
            <option value="">Todos</option>
            <option value="ATIVO" ${filters.status === "ATIVO" ? "selected" : ""}>Ativo</option>
            <option value="PRE_INATIVO" ${filters.status === "PRE_INATIVO" ? "selected" : ""}>Pré-inativo</option>
            <option value="INATIVO" ${filters.status === "INATIVO" ? "selected" : ""}>Inativo</option>
          </select>
        </div>
        <div class="field">
          <label>Compras no mês</label>
          <select onchange="updateCrmClientFilter('purchaseMonth', this.value)">
            <option value="">Todos</option>
            <option value="COM_COMPRA" ${filters.purchaseMonth === "COM_COMPRA" ? "selected" : ""}>Com compra no mês</option>
            <option value="SEM_COMPRA" ${filters.purchaseMonth === "SEM_COMPRA" ? "selected" : ""}>Sem compra no mês</option>
          </select>
        </div>
        <div class="field">
          <label>Crescimento</label>
          <select onchange="updateCrmClientFilter('growth', this.value)">
            <option value="">Todos</option>
            <option value="ACIMA" ${filters.growth === "ACIMA" ? "selected" : ""}>Acima</option>
            <option value="ESTAVEL" ${filters.growth === "ESTAVEL" ? "selected" : ""}>Estável</option>
            <option value="ABAIXO" ${filters.growth === "ABAIXO" ? "selected" : ""}>Abaixo</option>
          </select>
        </div>
        <div class="field">
          <label>Classe</label>
          <select onchange="updateCrmClientFilter('classCode', this.value)">
            <option value="">Todas</option>
            <option value="DIAMANTE" ${filters.classCode === "DIAMANTE" ? "selected" : ""}>Diamante</option>
            <option value="OURO" ${filters.classCode === "OURO" ? "selected" : ""}>Ouro</option>
            <option value="PRATA" ${filters.classCode === "PRATA" ? "selected" : ""}>Prata</option>
            <option value="BRONZE" ${filters.classCode === "BRONZE" ? "selected" : ""}>Bronze</option>
            <option value="SEM_CLASSE" ${filters.classCode === "SEM_CLASSE" ? "selected" : ""}>Sem classe</option>
          </select>
        </div>
        <div class="field">
          <label>Tipo de pessoa</label>
          <select onchange="updateCrmClientFilter('personType', this.value)">
            <option value="">Todos</option>
            <option value="PJ" ${filters.personType === "PJ" ? "selected" : ""}>PJ</option>
            <option value="PF" ${filters.personType === "PF" ? "selected" : ""}>PF</option>
          </select>
        </div>
        <div class="field">
          <label>Por página</label>
          <select onchange="setCrmClientPageSize(this.value)">
            <option value="25" ${pagination.pageSize === 25 ? "selected" : ""}>25</option>
            <option value="50" ${pagination.pageSize === 50 ? "selected" : ""}>50</option>
            <option value="100" ${pagination.pageSize === 100 ? "selected" : ""}>100</option>
          </select>
        </div>
        <div class="field" style="display:flex;align-items:flex-end;gap:8px">
          <button class="btn btn-primary" onclick="runCrmClientSearch()">Filtrar</button>
        </div>
      </div>
      <div class="crm-pagination-bar">
        <div class="soft-badge">Mostrando ${number(start)}-${number(end)} de ${number(pagination.total)} clientes</div>
        <div class="actions">
          ${!roleIsSeller() ? `<button class="btn btn-ghost btn-sm" onclick="exportCrmClientsXLSX()">↓ Exportar</button>` : ""}
          <button class="btn btn-ghost" ${pagination.page <= 1 ? "disabled" : ""} onclick="setCrmClientPage(${pagination.page - 1})">Anterior</button>
          <div class="soft-badge">Página ${number(pagination.page)} de ${number(Math.max(pagination.totalPages || 1, 1))}</div>
          <button class="btn btn-ghost" ${pagination.page >= pagination.totalPages ? "disabled" : ""} onclick="setCrmClientPage(${pagination.page + 1})">Próxima</button>
        </div>
      </div>
    </div>
  `;
}

function sellerClientCard(item) {
  const classBadge = { DIAMANTE: "💎", OURO: "🥇", PRATA: "🥈", BRONZE: "🥉" }[item.classCode] || "⚪";
  const hasPurchase = Number(item.currentRevenue || 0) > 0;
  return `
    <div class="crm-card clean" style="padding:14px">
      <div style="display:flex;justify-content:space-between;align-items:start;gap:8px;margin-bottom:8px">
        <div>
          <div style="font-weight:700;font-size:14px">${classBadge} ${escapeHtml(item.clientName)}</div>
          <div class="text-small">${escapeHtml(item.cityName || "-")} · ${escapeHtml(item.primaryReason || "")}</div>
        </div>
        ${crmStatusBadge(item.statusCode)}
      </div>
      <div style="display:flex;gap:8px;font-size:12px;color:var(--muted);margin-bottom:10px">
        <span>📞 ${escapeHtml(item.phone || "Sem tel.")}</span>
        <span style="color:${hasPurchase ? "var(--good)" : "#e67e22"}">${hasPurchase ? "✅ Comprou" : "○ Sem compra"}</span>
      </div>
      <div class="actions" style="gap:6px">
        <button class="btn btn-secondary btn-sm" onclick="openCrmClient('${escapeHtml(item.clientKey)}', false)">Ficha</button>
        <button class="btn btn-primary btn-sm" onclick="prefillInteractionFromAgenda('${escapeHtml(item.clientKey)}')">Registrar</button>
        <button class="btn btn-ghost btn-sm" onclick="openContactUpdateModal('${escapeHtml(item.clientKey)}')">Atualizar</button>
      </div>
    </div>
  `;
}

function crmClientsView() {
  if (!state.crm.summary) return `<div class="loader panel">Carregando clientes CRM...</div>`;
  const rows = filteredCrmClients();

  if (roleIsSeller()) {
    const urgent = rows.filter((r) => r.statusCode === "INATIVO" || r.statusCode === "PRE_INATIVO");
    const noSale = rows.filter((r) => r.statusCode === "ATIVO" && Number(r.currentRevenue || 0) <= 0);
    const active = rows.filter((r) => r.statusCode === "ATIVO" && Number(r.currentRevenue || 0) > 0);
    const isLoading = Boolean(state.ui.loading.crmClients);

    function groupSection(title, color, items, emptyMsg) {
      return `
        <div>
          <div style="display:flex;align-items:center;gap:10px;margin-bottom:10px">
            <span style="width:12px;height:12px;border-radius:50%;background:${color};display:inline-block"></span>
            <strong style="font-size:14px">${title}</strong>
            <span class="soft-badge">${items.length}</span>
          </div>
          ${items.length
            ? `<div style="display:grid;grid-template-columns:repeat(auto-fill,minmax(260px,1fr));gap:10px">${items.map(sellerClientCard).join("")}</div>`
            : `<div class="message" style="font-size:13px">${emptyMsg}</div>`}
        </div>
      `;
    }

    return `
      <div class="stack">
        <div class="form-card" style="padding:12px 18px">
          <div style="display:flex;align-items:center;gap:10px;flex-wrap:wrap">
            <span style="font-size:12px;font-weight:700;color:var(--muted)">BUSCAR</span>
            <input style="flex:1;min-width:200px" placeholder="Nome, código ou cidade"
              value="${escapeHtml(state.crm.crmClientFilters.search || "")}"
              oninput="state.crm.crmClientFilters.search=this.value"
              onkeydown="if(event.key==='Enter'){runCrmClientSearch();}" />
            <button class="btn btn-secondary btn-sm" onclick="runCrmClientSearch()">Buscar</button>
            <button class="btn btn-ghost btn-sm" onclick="clearCrmClientFilters()">Limpar</button>
          </div>
        </div>
        ${isLoading ? `<div class="message" style="background:rgba(15,48,68,0.07);color:var(--accent);font-weight:600">⏳ Atualizando carteira…</div>` : ""}
        ${groupSection("🔴 Urgente — Contatar agora", "#e74c3c", urgent, "✅ Nenhum pré-inativo ou inativo.")}
        ${groupSection("🟡 Ativos sem compra este mês", "#f39c12", noSale, "✅ Todos os ativos já compraram este mês.")}
        ${groupSection("🟢 Ativos com compra", "#27ae60", active, "Nenhum ativo com compra este mês.")}
      </div>
    `;
  }

  // Visão gerente/admin — toggle entre Dashboard e Lista
  const viewMode = state.crm.portfolioViewMode || "lista";
  const ps = state.crm.portfolioSummary;

  function portfolioDashboard() {
    if (!ps) return `<div class="loader panel">Carregando dashboard de carteira…</div>`;
    if (ps.error) return `<div class="message error">Erro ao carregar: ${escapeHtml(ps.error)}</div>`;
    const psSellers = ps.sellers || [];
    const tot = ps.totals || {};

    function statusBar(ativos, pre, inat, total) {
      const t = total || 1;
      const wa = Math.round(ativos / t * 100);
      const wp = Math.round(pre / t * 100);
      const wi = Math.max(0, 100 - wa - wp);
      return `<div style="display:flex;height:6px;border-radius:4px;overflow:hidden;margin-top:4px">
        <div style="width:${wa}%;background:#27ae60"></div>
        <div style="width:${wp}%;background:#f39c12"></div>
        <div style="width:${wi}%;background:#e74c3c"></div>
      </div>`;
    }

    const pfState = state.crm.portfolioFilters || {};
    const pfUnits = state.options.units || [];
    const pfCompetences = state.options.competences || [];

    // Filtro client-side por busca, unidade e status
    function applyLocalFilters(sellers) {
      let result = sellers;
      const search = (pfState.search || "").trim().toLowerCase();
      const unit = (pfState.unit || "").trim().toLowerCase();
      if (search) result = result.filter((r) => (r.sellerName || "").toLowerCase().includes(search));
      if (unit) result = result.filter((r) => (r.unit || r.baseUnit || "").toLowerCase().includes(unit));
      if (pfState.status === "ativo") result = result.filter((r) => r.ativos > 0);
      else if (pfState.status === "pre_inativo") result = result.filter((r) => r.preInativos > 0);
      else if (pfState.status === "inativo") result = result.filter((r) => r.inativos > 0);
      return result;
    }

    function portfolioFilterBar() {
      const hasActiveFilter = pfState.competence || pfState.search || pfState.unit || pfState.status || pfState.personType;
      return `
        <div class="form-card" style="padding:10px 16px">
          <div style="display:flex;align-items:center;gap:10px;flex-wrap:wrap">
            <span style="font-size:12px;font-weight:700;color:var(--muted)">FILTROS</span>
            <select style="flex:1;min-width:140px"
              onchange="state.crm.portfolioFilters.competence=this.value; loadPortfolioSummary()">
              <option value="">Competência atual</option>
              ${pfCompetences.map((c) => `<option value="${escapeHtml(c)}" ${pfState.competence === c ? "selected" : ""}>${escapeHtml(c)}</option>`).join("")}
            </select>
            <select style="flex:1;min-width:140px"
              onchange="state.crm.portfolioFilters.status=this.value; requestRender()">
              <option value="">Todos os status</option>
              <option value="ativo" ${pfState.status === "ativo" ? "selected" : ""}>Ativos</option>
              <option value="pre_inativo" ${pfState.status === "pre_inativo" ? "selected" : ""}>Pré-inativos</option>
              <option value="inativo" ${pfState.status === "inativo" ? "selected" : ""}>Inativos</option>
            </select>
            <select style="flex:1;min-width:140px"
              onchange="state.crm.portfolioFilters.unit=this.value; requestRender()">
              <option value="">Todas as unidades</option>
              ${pfUnits.map((u) => `<option value="${escapeHtml(u)}" ${pfState.unit === u ? "selected" : ""}>${escapeHtml(u)}</option>`).join("")}
            </select>
            <select style="flex:1;min-width:120px"
              onchange="state.crm.portfolioFilters.personType=this.value; loadPortfolioSummary()">
              <option value="">PJ + PF</option>
              <option value="PJ" ${pfState.personType === "PJ" ? "selected" : ""}>Somente PJ</option>
              <option value="PF" ${pfState.personType === "PF" ? "selected" : ""}>Somente PF</option>
            </select>
            <input id="pf-search-input" type="text" placeholder="Buscar vendedor…" style="flex:2;min-width:160px"
              value="${escapeHtml(pfState.search || "")}"
              onkeydown="if(event.key==='Enter'){state.crm.portfolioFilters.search=this.value;requestRender()}">
            <button class="btn btn-primary btn-sm" onclick="state.crm.portfolioFilters.search=document.getElementById('pf-search-input').value;requestRender()">Buscar</button>
            ${hasActiveFilter ? `<button class="btn btn-ghost btn-sm" onclick="state.crm.portfolioFilters={competence:'',unit:'',search:'',status:'',personType:''};loadPortfolioSummary()">✕ Limpar</button>` : ""}
          </div>
        </div>
      `;
    }

    return `
      <div class="stack">
        <!-- Filtros -->
        ${portfolioFilterBar()}

        <!-- Totais -->
        <div class="kpi-grid">
          <div class="kpi-card"><div class="kpi-value">${number(tot.total)}</div><div class="kpi-label">Total de clientes</div><div class="kpi-sub">${number(tot.comVendaMes)} com compra no mês</div></div>
          <div class="kpi-card"><div class="kpi-value" style="color:var(--good)">${number(tot.ativos)}</div><div class="kpi-label">Ativos <span style="font-size:12px;font-weight:400">(${tot.pctAtivos}%)</span></div><div class="kpi-sub">${number(tot.preInativos)} pré-inativos</div></div>
          <div class="kpi-card"><div class="kpi-value" style="color:var(--bad)">${number(tot.inativos)}</div><div class="kpi-label">Inativos <span style="font-size:12px;font-weight:400">(${tot.pctInativos}%)</span></div><div class="kpi-sub">Prioridade de reativação</div></div>
          <div class="kpi-card"><div class="kpi-value">${number(tot.comVendaMesAnterior)}</div><div class="kpi-label">Compraram mês anterior</div><div class="kpi-sub">${number(tot.semVendaMes)} sem compra este mês</div></div>
        </div>

        <!-- Tabela por vendedor -->
        <div class="table-card">
          <div class="section-title">
            <div><h3>Resumo por Vendedor</h3><div class="text-small">Competência ${escapeHtml(ps.competence || "—")} · mês anterior ${escapeHtml(ps.prevCompetence || "—")}</div></div>
            <button class="btn btn-ghost btn-sm" onclick="loadPortfolioSummary(); addMessage('success','Atualizado.')">↻ Atualizar</button>
          </div>
          <div class="table-wrap">
            <table>
              <thead>
                <tr>
                  <th>Vendedor</th>
                  <th>Carteira</th>
                  <th>C/ Venda Mês</th>
                  <th>Mês Anterior</th>
                  <th>Ativos</th>
                  <th>Pré-inativos</th>
                  <th>Inativos</th>
                  <th style="background:#fff3cd">⚠ Queda &gt;30%</th>
                  <th style="background:#fde8e8">🚨 Queda &gt;20%</th>
                </tr>
              </thead>
              <tbody>
                ${applyLocalFilters(psSellers).map((r) => `
                  <tr>
                    <td><strong>${escapeHtml(r.sellerName)}</strong></td>
                    <td><strong>${number(r.total)}</strong></td>
                    <td>
                      <strong style="color:${r.pctComVendaMes >= 50 ? "var(--good)" : r.pctComVendaMes >= 30 ? "#f39c12" : "var(--bad)"}">${number(r.comVendaMes)}</strong>
                      <div class="text-small">${r.pctComVendaMes}%</div>
                    </td>
                    <td><strong>${number(r.comVendaMesAnterior)}</strong></td>
                    <td>
                      <strong style="color:var(--good)">${number(r.ativos)}</strong>
                      <div style="font-size:11px;color:var(--muted)">${r.pctAtivos}%</div>
                      ${statusBar(r.ativos, r.preInativos, r.inativos, r.total)}
                    </td>
                    <td>
                      <strong style="color:#f39c12">${number(r.preInativos)}</strong>
                      <div style="font-size:11px;color:var(--muted)">${r.pctPreInativos}%</div>
                    </td>
                    <td>
                      <strong style="color:${r.inativos > 0 ? "var(--bad)" : "inherit"}">${number(r.inativos)}</strong>
                      <div style="font-size:11px;color:var(--muted)">${r.pctInativos}%</div>
                    </td>
                    <td style="background:${r.queda30 > 0 ? "rgba(243,156,18,0.1)" : ""}">
                      <strong style="color:${r.queda30 > 0 ? "#f39c12" : "var(--muted)"}">${number(r.queda30)}</strong>
                    </td>
                    <td style="background:${r.queda20 > 0 ? "rgba(231,76,60,0.07)" : ""}">
                      <strong style="color:${r.queda20 > 0 ? "var(--bad)" : "var(--muted)"}">${number(r.queda20)}</strong>
                    </td>
                  </tr>
                `).join("") || `<tr><td colspan="10">Nenhum dado disponível.</td></tr>`}
              </tbody>
              <tfoot>
                <tr style="font-weight:700;border-top:2px solid var(--line)">
                  <td>TOTAL</td>
                  <td>${number(tot.total)}</td>
                  <td>${number(tot.comVendaMes)} <span class="text-small">${tot.pctComVendaMes}%</span></td>
                  <td>${number(tot.comVendaMesAnterior)}</td>
                  <td>${number(tot.ativos)} <span class="text-small">${tot.pctAtivos}%</span></td>
                  <td>${number(tot.preInativos)} <span class="text-small">${tot.pctPreInativos}%</span></td>
                  <td>${number(tot.inativos)} <span class="text-small">${tot.pctInativos}%</span></td>
                  <td>${number(tot.queda30)}</td>
                  <td>${number(tot.queda20)}</td>
                </tr>
              </tfoot>
            </table>
          </div>
        </div>
      </div>
    `;
  }

  return `
    <div class="stack">
      <!-- Toggle de visualização -->
      <div class="form-card" style="padding:10px 16px">
        <div style="display:flex;align-items:center;gap:12px;flex-wrap:wrap">
          <div class="subtabs" style="margin:0">
            <button class="subtab-button ${viewMode === "dashboard" ? "active" : ""}" onclick="state.crm.portfolioViewMode='dashboard';requestRender()">📊 Dashboard Vendedores</button>
            <button class="subtab-button ${viewMode === "lista" ? "active" : ""}" onclick="state.crm.portfolioViewMode='lista';requestRender()">📋 Lista de Clientes</button>
          </div>
        </div>
      </div>

      ${viewMode === "dashboard" ? portfolioDashboard() : `
        ${crmFilterToolbar()}
        <div class="table-card">
          <div class="table-wrap">
            <table>
              <thead>
                <tr>
                  <th>Código</th>
                  <th>Cliente</th>
                  <th>Vendedor</th>
                  <th>Cidade</th>
                  <th>Status</th>
                  <th>Classe</th>
                  <th>Telefone</th>
                  <th>Contato principal</th>
                  <th>Compra no mês</th>
                  <th>Crescimento</th>
                  <th>Motivo principal</th>
                  <th>Ações</th>
                </tr>
              </thead>
              <tbody>
                ${rows.map((item) => `
                  <tr class="${Number(item.currentRevenue || 0) > 0 ? "" : "crm-row-no-purchase"}">
                    <td><strong>${escapeHtml(item.clientKey || "-")}</strong></td>
                    <td><strong>${escapeHtml(item.clientName)}</strong><div class="text-small">${escapeHtml(item.unitName || "-")}</div></td>
                    <td><span class="${item.assignedSeller ? "" : "text-small"}" style="${item.assignedSeller ? "" : "color:var(--muted)"}">${escapeHtml(item.assignedSeller || "Sem vendedor")}</span></td>
                    <td>${escapeHtml(item.cityName || "-")}</td>
                    <td>${crmStatusBadge(item.statusCode)}</td>
                    <td>${escapeHtml(item.classCode || "-")}</td>
                    <td>${escapeHtml(item.phone || "Não informado")}</td>
                    <td>${escapeHtml(item.primaryContactName || "Não informado")}</td>
                    <td>${crmPurchaseBadge(item.currentRevenue)}</td>
                    <td>${crmGrowthBadge(item.growthPct)}</td>
                    <td>${escapeHtml(item.primaryReason || "-")}</td>
                    <td>
                      <div class="table-actions">
                        <button class="btn btn-secondary btn-sm" onclick="openCrmClient('${escapeHtml(item.clientKey)}')">Abrir ficha</button>
                        <button class="btn btn-ghost btn-sm" onclick="openContactUpdateModal('${escapeHtml(item.clientKey)}')">Atualizar contato</button>
                      </div>
                    </td>
                  </tr>
                `).join("") || '<tr><td colspan="12">Nenhum cliente encontrado com os filtros selecionados.</td></tr>'}
              </tbody>
            </table>
          </div>
        </div>
      `}
    </div>
  `;
}

function clientDrawerView() {
  if (!state.ui.clientDrawerOpen && !state.ui.loading.clientDrawer && !state.ui.clientDrawerError) return "";
  const detail = state.crm.selectedClient;
  const client = detail?.summary || {};
  const profile = detail?.profile || {};
  return `
    <div class="client-drawer-overlay ${state.ui.clientDrawerOpen ? "open" : ""}" onclick="closeClientDrawer()">
      <aside class="client-drawer ${state.ui.clientDrawerOpen ? "open" : ""}" onclick="event.stopPropagation()">
        <div class="client-drawer-header">
          <div>
            <div class="eyebrow">Ficha 360</div>
            <h3>${escapeHtml(client.clientKey || state.crm.selectedClientKey || "Cliente")}</h3>
            <div class="text-small">${escapeHtml(client.clientName || "Carregando ficha do cliente...")}</div>
          </div>
          <button class="btn btn-ghost btn-sm" onclick="closeClientDrawer()">Fechar</button>
        </div>
        <div class="client-drawer-actions">
          <button class="btn btn-primary" ${client.clientKey ? "" : "disabled"} onclick="prefillInteractionFromAgenda('${escapeHtml(client.clientKey || "")}')">Registrar contato</button>
          <button class="btn btn-secondary" ${client.clientKey ? "" : "disabled"} onclick="openContactUpdateModal('${escapeHtml(client.clientKey || "")}')">Atualizar contato</button>
        </div>
        ${state.ui.loading.clientDrawer ? `<div class="message success">Carregando ficha do cliente...</div>` : ""}
        ${state.ui.clientDrawerError ? `<div class="message error">Não foi possível abrir a ficha do cliente.</div>` : ""}
        ${detail ? `
          <div class="stack">
            <div class="subtle-card padded-card">
              <div class="section-title"><h3>Identificação</h3></div>
              <div class="crm-mini-grid crm-detail-grid">
                <div><span>Código do cliente</span><strong>${escapeHtml(client.clientCode || client.clientKey || "-")}</strong></div>
                <div><span>Nome do cliente</span><strong>${escapeHtml(client.clientName || "-")}</strong></div>
                <div><span>Cidade</span><strong>${escapeHtml(client.cityName || profile.city_name || "-")}</strong></div>
                <div><span>Unidade</span><strong>${escapeHtml(client.unitName || "-")}</strong></div>
                <div><span>Classe</span><strong>${escapeHtml(client.classCode || "-")}</strong></div>
                <div><span>Status</span><strong>${escapeHtml(client.statusCode || "-")}</strong></div>
                <div><span>Telefone atualizado</span><strong>${escapeHtml(client.updatedPhone || client.phone || profile.updatedPhone || profile.phone || "Não informado")}</strong></div>
                <div><span>Contato principal</span><strong>${escapeHtml(client.primaryContactName || profile.primaryContactName || "Não informado")}</strong></div>
              </div>
            </div>
            <div class="subtle-card padded-card">
              <div class="section-title"><h3>Situação comercial</h3></div>
              <div class="crm-mini-grid crm-detail-grid">
                <div><span>Última compra</span><strong>${escapeHtml(client.lastPurchaseAt ? client.lastPurchaseAt.slice(0, 10) : "-")}</strong></div>
                <div><span>Dias sem compra</span><strong>${number(client.daysWithoutPurchase || 0)}</strong></div>
                <div><span>Faturamento mês atual</span><strong>${currency(client.currentRevenue)}</strong></div>
                <div><span>Média trimestre</span><strong>${currency(client.averageRevenue)}</strong></div>
                <div><span>Crescimento ou queda</span><strong>${pct((client.growthPct || 0) * 100)}</strong></div>
                <div><span>Motivo principal</span><strong>${escapeHtml(client.primaryReason || "-")}</strong></div>
              </div>
            </div>
            <div class="subtle-card padded-card">
              <div class="section-title"><h3>Ação recomendada</h3></div>
              <div class="crm-mini-grid crm-detail-grid">
                <div><span>Oferta sugerida</span><strong>${escapeHtml(client.offerPrimary?.title || "-")}</strong></div>
                <div><span>Pergunta sugerida</span><strong>${escapeHtml(client.questionPrimary || "-")}</strong></div>
                <div><span>Próxima melhor ação</span><strong>${escapeHtml(crmRecommendedAction(client))}</strong></div>
              </div>
            </div>
            <div class="table-card">
              <div class="section-title">
                <div>
                  <h3>Histórico</h3>
                  <div class="text-small">Compras, itens, interações e tarefas organizados em abas.</div>
                </div>
              </div>
              <div class="subtabs">
                <button class="subtab-button ${state.ui.crmClientDetailTab === "historico" ? "active" : ""}" onclick="setCrmClientDetailTab('historico')">Tarefas</button>
                <button class="subtab-button ${state.ui.crmClientDetailTab === "compras" ? "active" : ""}" onclick="setCrmClientDetailTab('compras')">Compras</button>
                <button class="subtab-button ${state.ui.crmClientDetailTab === "itens" ? "active" : ""}" onclick="setCrmClientDetailTab('itens')">Itens</button>
                <button class="subtab-button ${state.ui.crmClientDetailTab === "interacoes" ? "active" : ""}" onclick="setCrmClientDetailTab('interacoes')">Interações</button>
              </div>
              ${crmClientHistoryPanel(detail)}
            </div>
          </div>
        ` : ""}
      </aside>
    </div>
  `;
}

function crmClientHistoryPanel(clientDetail) {
  const tab = state.ui.crmClientDetailTab;
  const tabState = state.crm.selectedClientTabs[tab];
  if (tabState?.loading) {
    return `<div class="message success">Carregando dados da aba...</div>`;
  }
  if (tabState?.error) {
    return `<div class="message error">Não foi possível carregar esta aba.</div>`;
  }
  if (tab === "compras") {
    return `
      <div class="table-wrap">
        <table>
          <thead><tr><th>Competência</th><th>Faturamento</th></tr></thead>
          <tbody>
            ${(tabState?.rows || []).map((row) => `<tr><td>${escapeHtml(row.competence)}</td><td>${currency(row.revenue)}</td></tr>`).join("") || '<tr><td colspan="2">Sem histórico mensal.</td></tr>'}
          </tbody>
        </table>
      </div>
    `;
  }
  if (tab === "itens") {
    return `
      <div class="table-wrap">
        <table>
          <thead><tr><th>Data</th><th>Item</th><th>Qtd</th><th>Valor</th></tr></thead>
          <tbody>
            ${(tabState?.rows || []).map((row) => `<tr><td>${escapeHtml((row.issue_date || "").slice(0, 10))}</td><td>${escapeHtml(row.item_code)}</td><td>${number(row.quantity)}</td><td>${currency(row.net_value)}</td></tr>`).join("") || '<tr><td colspan="4">Sem itens recentes.</td></tr>'}
          </tbody>
        </table>
      </div>
    `;
  }
  if (tab === "interacoes") {
    return `
      <div class="timeline-list">
        ${(tabState?.rows || []).map((row) => `<div class="timeline-item"><strong>${escapeHtml(row.contact_type_code)} · ${escapeHtml(row.result_code)}</strong><div class="text-small">${escapeHtml((row.occurred_at || "").replace("T", " ").slice(0, 16))}</div><div class="text-small">${escapeHtml(row.contact_name || row.contact_phone || "")}</div><div class="text-small">${escapeHtml(row.notes || "")}</div></div>`).join("") || '<div class="timeline-item"><div class="text-small">Sem interações registradas.</div></div>'}
      </div>
    `;
  }
  return `
    <div class="timeline-list">
      ${(tabState?.rows || []).map((row) => `<div class="timeline-item"><strong>${escapeHtml(row.title)}</strong><div class="text-small">${escapeHtml(row.status)} · ${escapeHtml((row.due_at || "").replace("T", " ").slice(0, 16))}</div><div class="text-small">${escapeHtml(row.description || "")}</div></div>`).join("") || '<div class="timeline-item"><div class="text-small">Sem tarefas para este cliente.</div></div>'}
    </div>
  `;
}

function crmClientDetailView() {
  return "";
}

function crmTasksView() {
  if (!state.crm.summary) return `<div class="loader panel">Carregando tarefas CRM...</div>`;
  return `
    <div class="table-card">
      <div class="section-title">
        <div>
          <h3>Tarefas</h3>
          <div class="text-small">Fila operacional de follow-ups e retornos do CRM.</div>
        </div>
      </div>
      <div class="timeline-list">
        ${(state.crm.taskRows || []).map((row) => {
          const isOverdue = row.status === "ATRASADA";
          const statusColor = isOverdue ? "var(--bad)" : "var(--accent)";
          const dueLabel = (row.due_at || "").replace("T", " ").slice(0, 16);
          return `<div class="timeline-item" style="border-left:3px solid ${statusColor};padding-left:12px">
            <div style="display:flex;justify-content:space-between;align-items:flex-start;gap:8px;flex-wrap:wrap">
              <div>
                <strong>${escapeHtml(row.client_name || "—")}</strong>
                <div class="text-small">${escapeHtml(row.title || "")}</div>
                ${row.description ? `<div class="text-small" style="color:var(--muted)">${escapeHtml(row.description)}</div>` : ""}
              </div>
              <div style="text-align:right;white-space:nowrap">
                <span class="status-tag ${isOverdue ? "bad" : "warn"}">${escapeHtml(row.status)}</span>
                <div class="text-small" style="margin-top:4px">${escapeHtml(dueLabel)}</div>
              </div>
            </div>
            <div class="actions" style="margin-top:10px">
              <button class="btn btn-primary btn-sm" onclick="prefillInteractionFromAgenda('${escapeHtml(row.client_key || "")}')">📞 Registrar contato</button>
              <button class="btn btn-secondary btn-sm" onclick="completeCrmTask(${Number(row.id)})">✅ Concluir</button>
              <button class="btn btn-ghost btn-sm" onclick="openTaskRescheduleModal(${Number(row.id)})">📅 Reagendar</button>
            </div>
          </div>`;
        }).join("") || emptyStateCard("Sem tarefas abertas.")}
      </div>
    </div>
  `;
}

function setInteractionResult(resultCode, contactTypeCode) {
  state.crm.interactionForm.resultCode = resultCode;
  if (contactTypeCode) state.crm.interactionForm.contactTypeCode = contactTypeCode;
  // Resultado exige data de retorno → pré-preencher followupDueAt com amanhã se vazio
  if (["NAO_ATENDEU", "PEDIU_RETORNO"].includes(resultCode) && !state.crm.interactionForm.followupDueAt) {
    const tomorrow = new Date();
    tomorrow.setDate(tomorrow.getDate() + 1);
    tomorrow.setHours(9, 0, 0, 0);
    state.crm.interactionForm.followupDueAt = tomorrow.toISOString().slice(0, 16);
  }
  requestRender();
}

function crmInteractionView() {
  const form = state.crm.interactionForm;
  const hasClient = Boolean(form.clientName || form.clientKey);
  const needsReturn = ["NAO_ATENDEU", "PEDIU_RETORNO"].includes(form.resultCode);
  const resultSold = form.resultCode === "GEROU_PEDIDO";

  // Mapeamento visual dos 4 resultados principais
  const resultButtons = [
    { code: "GEROU_PEDIDO",    type: "LIGACAO",   label: "✅ Vendeu",          tone: "btn-primary",   desc: "Gerou pedido" },
    { code: "FALOU_CLIENTE",   type: "LIGACAO",   label: "💬 Falou, não vendeu", tone: "btn-secondary", desc: "Falou com o cliente" },
    { code: "NAO_ATENDEU",     type: "LIGACAO",   label: "📵 Não atendeu",      tone: "btn-ghost",     desc: "Nao atendeu" },
    { code: "PEDIU_RETORNO",   type: "LIGACAO",   label: "📅 Agendou retorno",  tone: "btn-ghost",     desc: "Pediu retorno" },
  ];

  return `
    <div class="stack">

      ${!hasClient ? `
        <div class="form-card" style="border-left:4px solid #f39c12">
          <div class="section-title"><h3>📋 Selecione um cliente para registrar</h3></div>
          <div class="text-small">Clique em <strong>Registrar contato</strong> em um cliente da <strong>Missão do Dia</strong> ou da <strong>Carteira</strong>.</div>
          <div class="actions" style="margin-top:12px">
            <button class="btn btn-secondary" onclick="switchTab('crm-agenda')">Ir para Missão do Dia</button>
            <button class="btn btn-ghost" onclick="switchTab('crm-clientes')">Ir para Carteira</button>
          </div>
        </div>
      ` : `
        <div class="form-card" style="background:linear-gradient(135deg,#f8fbfd,#fff)">
          <div class="section-title">
            <div>
              <div class="eyebrow" style="color:var(--accent);font-weight:800;font-size:10px;letter-spacing:0.08em">REGISTRAR CONTATO</div>
              <h3 style="margin:4px 0">${escapeHtml(form.clientName || form.clientKey || "—")}</h3>
              ${form.clientKey ? `<div class="text-small">Cód. ${escapeHtml(form.clientKey)}${form.unitName ? " · " + escapeHtml(form.unitName) : ""}</div>` : ""}
            </div>
            <button class="btn btn-ghost btn-sm" onclick="resetInteractionForm()">Trocar cliente</button>
          </div>
        </div>

        <div class="form-card">
          <div class="section-title"><h3>Como foi o contato?</h3></div>
          <div style="display:grid;grid-template-columns:repeat(2,1fr);gap:10px;margin-bottom:4px">
            ${resultButtons.map((btn) => `
              <button class="btn ${btn.code === form.resultCode ? "btn-primary" : "btn-ghost"}"
                style="${btn.code === form.resultCode ? "font-weight:800" : ""}"
                onclick="setInteractionResult('${btn.code}','${btn.type}')">
                ${escapeHtml(btn.label)}
              </button>
            `).join("")}
          </div>
          <div style="font-size:12px;color:var(--muted);margin-top:4px;text-align:center">
            Selecionado: <strong>${resultButtons.find((b) => b.code === form.resultCode)?.desc || form.resultCode}</strong>
          </div>
        </div>

        <div class="form-card">
          <div class="stack" style="gap:14px">

            <div class="field">
              <label>Oferta apresentada <span style="color:var(--muted);font-weight:400">(o que você ofereceu?)</span></label>
              <input
                placeholder="Ex: filtros de óleo linha pesada, promoção de freios..."
                value="${escapeHtml(form.offerTitle || "")}"
                oninput="state.crm.interactionForm.offerTitle=this.value"
              />
            </div>

            <div class="field">
              <label>Observação <span style="color:var(--bad)">*</span></label>
              <textarea
                rows="3"
                placeholder="O que foi dito? Qual o contexto? Anote tudo que for útil."
                oninput="state.crm.interactionForm.notes=this.value"
              >${escapeHtml(form.notes)}</textarea>
            </div>

            ${needsReturn ? `
              <div class="field" style="background:#fff9e6;border:1px solid #f4c25f;border-radius:12px;padding:12px">
                <label style="color:#c0832a">📅 Data e hora do retorno <span style="color:var(--bad)">*</span></label>
                <input type="datetime-local" value="${escapeHtml(form.followupDueAt)}" oninput="state.crm.interactionForm.followupDueAt=this.value" />
                <div class="text-small" style="margin-top:6px;color:#c0832a">O sistema cria uma tarefa de retorno automaticamente.</div>
              </div>
            ` : ""}

            ${resultSold ? `
              <div class="field" style="background:#eafaf1;border:1px solid #27ae60;border-radius:12px;padding:12px">
                <div style="color:#1e8449;font-weight:700">🎉 Venda registrada — isso conta para sua positivação!</div>
                <div class="text-small" style="color:#1e8449;margin-top:4px">Lembre-se: ticket médio e mix de itens também pontuam na premiação.</div>
              </div>
            ` : ""}

            <div style="display:grid;grid-template-columns:1fr 1fr;gap:10px">
              <div class="field">
                <label>Telefone atualizado <span style="color:var(--muted);font-weight:400">(opcional)</span></label>
                <input placeholder="(00) 00000-0000" value="${escapeHtml(form.updatedPhone || "")}" oninput="state.crm.interactionForm.updatedPhone=this.value" />
              </div>
              <div class="field">
                <label>Nome do contato <span style="color:var(--muted);font-weight:400">(opcional)</span></label>
                <input placeholder="Ex: João, gerente" value="${escapeHtml(form.primaryContactName || "")}" oninput="state.crm.interactionForm.primaryContactName=this.value" />
              </div>
            </div>

          </div>
        </div>

        <div class="actions" style="position:sticky;bottom:18px;z-index:10;background:rgba(255,255,255,0.95);padding:12px;border-radius:14px;box-shadow:0 4px 20px rgba(0,0,0,0.1)">
          <button class="btn btn-primary" style="flex:1;min-height:48px;font-size:15px" onclick="submitCrmInteraction()">
            Salvar contato
          </button>
          <button class="btn btn-ghost" onclick="resetInteractionForm()">Cancelar</button>
        </div>
      `}
    </div>
  `;
}

async function openContactUpdateModal(clientKey) {
  if (!clientKey) {
    addMessage("error", "Cliente não encontrado para atualização de contato.");
    return;
  }
  let source = state.crm.selectedClient?.summary?.clientKey === clientKey
    ? state.crm.selectedClient
    : null;
  let summary = source?.summary
    || state.crm.clients.find((item) => item.clientKey === clientKey)
    || state.crm.agenda.top5.find((item) => item.clientKey === clientKey)
    || state.crm.agenda.extended.find((item) => item.clientKey === clientKey);
  let profile = source?.profile || {};
  if (!summary) {
    try {
      source = await api(`/api/crm/client/summary?${buildQuery()}&clientKey=${encodeURIComponent(clientKey)}`);
      summary = source?.summary;
      profile = source?.profile || {};
    } catch (error) {
      addMessage("error", error.message || "Cliente não encontrado para atualização de contato.");
      return;
    }
  }
  if (!summary) {
    addMessage("error", "Cliente não encontrado para atualização de contato.");
    return;
  }
  state.crm.modal = {
    type: "CONTACT_UPDATE",
    clientKey: summary.clientKey,
    clientName: summary.clientName,
    updatedPhone: summary.updatedPhone || summary.phone || profile.updatedPhone || profile.updated_phone || profile.phone || "",
    primaryContactName: summary.primaryContactName || profile.primaryContactName || profile.primary_contact_name || "",
    notes: summary.contactNotes || profile.contactNotes || profile.contact_notes || "",
  };
  requestRender();
}

function crmModalView() {
  const modal = state.crm.modal;
  if (!modal) return "";
  if (modal.type === "CONTACT_UPDATE") {
    return `
      <div class="crm-modal-backdrop" onclick="closeCrmModal()">
        <div class="crm-modal" onclick="event.stopPropagation()">
          <div class="section-title">
            <div>
              <h3>Atualizar contato</h3>
              <div class="text-small">${escapeHtml(modal.clientKey)} · ${escapeHtml(modal.clientName)}</div>
            </div>
          </div>
          <div class="stack">
            <div class="field"><label>Código do cliente</label><input value="${escapeHtml(modal.clientKey)}" disabled /></div>
            <div class="field"><label>Nome do cliente</label><input value="${escapeHtml(modal.clientName)}" disabled /></div>
            <div class="field"><label>Telefone atualizado</label><input value="${escapeHtml(modal.updatedPhone || "")}" oninput="state.crm.modal.updatedPhone=this.value" /></div>
            <div class="field"><label>Nome do contato principal</label><input value="${escapeHtml(modal.primaryContactName || "")}" oninput="state.crm.modal.primaryContactName=this.value" /></div>
            <div class="field"><label>Observação opcional</label><textarea rows="4" oninput="state.crm.modal.notes=this.value">${escapeHtml(modal.notes || "")}</textarea></div>
            <div class="actions">
              <button class="btn btn-ghost" onclick="closeCrmModal()">Cancelar</button>
              <button class="btn btn-primary" onclick="submitCrmModalAction()">Salvar</button>
            </div>
          </div>
        </div>
      </div>
    `;
  }
  if (modal.type === "AGENDA_ACTION") {
    return `
      <div class="crm-modal-backdrop" onclick="closeCrmModal()">
        <div class="crm-modal" onclick="event.stopPropagation()">
          <div class="section-title">
            <div>
              <h3>${modal.actionType === "ADIAR" ? "Adiar cliente" : "Reordenar cliente"}</h3>
              <div class="text-small">${escapeHtml(modal.clientName)}</div>
            </div>
          </div>
          <div class="stack">
            <div class="field">
              <label>Justificativa</label>
              <textarea rows="4" oninput="state.crm.modal.justification=this.value">${escapeHtml(modal.justification || "")}</textarea>
            </div>
            ${modal.actionType === "ADIAR" ? `
              <div class="field">
                <label>Nova data/hora para voltar à agenda</label>
                <input type="datetime-local" value="${escapeHtml(modal.nextVisibleAt || "")}" oninput="state.crm.modal.nextVisibleAt=this.value" />
              </div>
            ` : ""}
            <div class="actions">
              <button class="btn btn-ghost" onclick="closeCrmModal()">Cancelar</button>
              <button class="btn btn-primary" onclick="submitCrmModalAction()">Salvar</button>
            </div>
          </div>
        </div>
      </div>
    `;
  }
  if (modal.type === "TASK_RESCHEDULE") {
    return `
      <div class="crm-modal-backdrop" onclick="closeCrmModal()">
        <div class="crm-modal" onclick="event.stopPropagation()">
          <div class="section-title">
            <div>
              <h3>Reagendar tarefa</h3>
              <div class="text-small">Tarefa #${number(modal.taskId)}</div>
            </div>
          </div>
          <div class="stack">
            <div class="field">
              <label>Nova data/hora do retorno</label>
              <input type="datetime-local" value="${escapeHtml(modal.dueAt || "")}" oninput="state.crm.modal.dueAt=this.value" />
            </div>
            <div class="actions">
              <button class="btn btn-ghost" onclick="closeCrmModal()">Cancelar</button>
              <button class="btn btn-primary" onclick="submitCrmModalAction()">Salvar</button>
            </div>
          </div>
        </div>
      </div>
    `;
  }
  return "";
}

async function submitCrmModalAction() {
  const modal = state.crm.modal;
  if (!modal) return;
  try {
    if (modal.type === "CONTACT_UPDATE") {
      await api("/api/crm/client/contact", {
        method: "POST",
        body: JSON.stringify({
          clientKey: modal.clientKey,
          clientName: modal.clientName,
          updatedPhone: modal.updatedPhone,
          primaryContactName: modal.primaryContactName,
          notes: modal.notes,
        }),
      });
      addMessage("success", "Contato do cliente atualizado.");
      state.crm.modal = null;
      await loadCrmData();
      await openCrmClient(modal.clientKey, false);
      return;
    }
    if (modal.type === "AGENDA_ACTION") {
      if (!modal.justification || !modal.justification.trim()) {
        addMessage("error", "Justificativa obrigatória.");
        return;
      }
      await api("/api/crm/agenda/actions", {
        method: "POST",
        body: JSON.stringify({
          clientKey: modal.clientKey,
          clientName: modal.clientName,
          actionType: modal.actionType,
          justification: modal.justification,
          nextVisibleAt: modal.nextVisibleAt ? modal.nextVisibleAt.replace("T", " ") : "",
        }),
      });
      addMessage("success", "Ação da agenda registrada.");
      state.crm.modal = null;
      await loadCrmData();
      return;
    }
    if (modal.type === "TASK_RESCHEDULE") {
      if (!modal.dueAt || !modal.dueAt.trim()) {
        addMessage("error", "Nova data obrigatória.");
        return;
      }
      await api("/api/crm/tasks/reschedule", {
        method: "POST",
        body: JSON.stringify({ taskId: modal.taskId, dueAt: modal.dueAt }),
      });
      addMessage("success", "Tarefa reagendada.");
      state.crm.modal = null;
      await loadCrmData();
    }
  } catch (error) {
    addMessage("error", error.message);
  }
}

async function openCrmClient(clientKey, switchToClientsTab = true, renderAfterLoad = true) {
  if (!clientKey) return;
  state.crm.selectedClientKey = clientKey;
  state.ui.crmClientDetailTab = "historico";
  state.ui.clientDrawerOpen = true;
  setLoading("clientDrawer", true);
  state.ui.clientDrawerError = "";
  resetSelectedClientTabs();
  if (switchToClientsTab) {
    state.activeTab = "crm-clientes";
  }
  if (renderAfterLoad) requestRender();

  try {
    // 1. Carrega só o summary — abre o drawer imediatamente
    state.crm.selectedClient = await api(`/api/crm/client/summary?${buildQuery()}&clientKey=${encodeURIComponent(clientKey)}`);
    state.ui.clientDrawerError = "";
  } catch (error) {
    state.crm.selectedClient = null;
    state.ui.clientDrawerError = error.message || "Não foi possível abrir a ficha do cliente.";
    setLoading("clientDrawer", false);
    if (renderAfterLoad) requestRender();
    return;
  }

  // 2. Drawer visível imediatamente após o summary
  setLoading("clientDrawer", false);
  if (renderAfterLoad) requestRender();

  // 3. Precarrega as abas em background sem bloquear — troca de aba fica instantânea
  Promise.all([
    ensureCrmClientTabLoaded("historico", true),
    ensureCrmClientTabLoaded("compras", true),
    ensureCrmClientTabLoaded("itens", true),
    ensureCrmClientTabLoaded("interacoes", true),
  ]).then(() => {
    if (renderAfterLoad) requestRender();
  }).catch(() => {});
}

function prefillInteractionFromAgenda(clientKey) {
  const source = state.crm.clients.find((item) => item.clientKey === clientKey)
    || state.crm.agenda.top5.find((item) => item.clientKey === clientKey)
    || state.crm.agenda.extended.find((item) => item.clientKey === clientKey)
    || state.crm.selectedClient?.summary;
  if (!source) return;
  state.crm.interactionForm = {
    clientKey: source.clientKey,
    clientCode: source.clientKey,
    clientName: source.clientName,
    unitName: source.unitName || state.filters.unit || "",
    updatedPhone: source.updatedPhone || source.phone || "",
    primaryContactName: source.primaryContactName || "",
    contactNotes: source.contactNotes || "",
    contactTypeCode: "LIGACAO",
    resultCode: "FALOU_CLIENTE",
    occurredAt: new Date().toISOString().slice(0, 16),
    notes: "",
    questionUsed: source.questionPrimary || "",
    hadProgress: false,
    offerTitle: source.offerPrimary?.title || "",
    nextAction: crmRecommendedAction(source),
    followupDueAt: "",
  };
  state.activeTab = "crm-interacao";
  requestRender();
}

function resetInteractionForm() {
  state.crm.interactionForm = {
    clientKey: "", clientCode: "", clientName: "", unitName: "",
    updatedPhone: "", primaryContactName: "", contactNotes: "",
    contactTypeCode: "LIGACAO", resultCode: "FALOU_CLIENTE",
    occurredAt: "", notes: "", questionUsed: "", hadProgress: false,
    offerTitle: "", nextAction: "", followupDueAt: "",
  };
  requestRender();
}

async function submitCrmInteraction() {
  const form = state.crm.interactionForm;
  if (!form.clientKey && !form.clientCode) {
    addMessage("error", "Selecione um cliente antes de registrar o contato.");
    return;
  }
  if (!form.notes || !form.notes.trim()) {
    addMessage("error", "Preencha a observação — ela é obrigatória.");
    return;
  }
  if (["NAO_ATENDEU", "PEDIU_RETORNO"].includes(form.resultCode) && !form.followupDueAt) {
    addMessage("error", "Informe a data e hora do retorno.");
    return;
  }
  try {
    const now = new Date();
    await api("/api/crm/interactions", {
      method: "POST",
      body: JSON.stringify({
        ...form,
        clientKey: form.clientCode || form.clientKey,
        occurredAt: form.occurredAt ? form.occurredAt.replace("T", " ") : now.toISOString().replace("T", " ").slice(0, 19),
        followupDueAt: form.followupDueAt ? form.followupDueAt.replace("T", " ") : "",
        hadProgress: form.resultCode === "GEROU_PEDIDO" || form.resultCode === "GEROU_ORCAMENTO",
      }),
    });
    // Atualizar placar de ligações em background
    if (roleIsSeller()) loadSellerScore();
    const resultLabel = {
      GEROU_PEDIDO: "🎉 Venda registrada!",
      GEROU_ORCAMENTO: "📋 Orçamento registrado!",
      PEDIU_RETORNO: "📅 Retorno agendado!",
      FALOU_CLIENTE: "✅ Contato registrado!",
      NAO_ATENDEU: "✅ Tentativa registrada.",
    }[form.resultCode] || "✅ Contato registrado!";
    addMessage("success", resultLabel);
    // Remover cliente da Missão do Dia imediatamente (sem esperar reload)
    const contactedKey = form.clientCode || form.clientKey;
    if (state.crm.agenda) {
      state.crm.agenda.top5 = (state.crm.agenda.top5 || []).filter((c) => c.clientKey !== contactedKey);
      state.crm.agenda.extended = (state.crm.agenda.extended || []).filter((c) => c.clientKey !== contactedKey);
    }
    // Atualizar contador do summary imediatamente
    const _noCountForSummary = ["NAO_ATENDEU", "PEDIU_RETORNO"];
    if (state.crm.summary && !_noCountForSummary.includes(form.resultCode)) {
      state.crm.summary.contactsToday = (state.crm.summary.contactsToday || 0) + 1;
    }
    resetInteractionForm();
    await loadCrmData();
    state.activeTab = roleIsSeller() ? "crm-agenda" : "crm-clientes";
  } catch (error) {
    addMessage("error", error.message);
  }
}

function unitsView() {
  if (!state.dashboard) return `<div class="loader panel">Carregando unidades...</div>`;
  return `
    <div class="stack">
      ${loadingBanner()}
      <div class="table-card">
      <div class="section-title">
        <div>
          <h3>Unidades</h3>
          <div class="text-small">Resultado por unidade com foco em decisão gerencial.</div>
        </div>
      </div>
      <div class="table-wrap">
        <table>
          <thead>
            <tr><th>Unidade</th><th>Líquido</th><th>Meta</th><th>% Meta</th><th>% Proj.</th><th>Devolução</th><th>% Dev.</th><th>Margem</th><th>Qtd. Peças</th><th>Ticket/Peça</th><th>Meta diária</th></tr>
          </thead>
          <tbody>${unitRows(state.dashboard.unitPerformance || [])}</tbody>
        </table>
      </div>
    </div>
  `;
}

function executiveExpandSection(key, label, content) {
  const open = Boolean(state.ui.executiveSections[key]);
  return `
    <div class="table-card expandable-card ${open ? "open" : ""}">
      <div class="section-title">
        <div><h3>${escapeHtml(label)}</h3></div>
        <button class="btn btn-ghost" onclick="toggleSection('${key}')">${open ? "Ocultar" : label}</button>
      </div>
      ${open ? content : ""}
    </div>
  `;
}

function managerExecutiveView() {
  const alerts = buildManagementAlerts();
  const clientsAtRisk = (state.crm.clients || []).filter((item) => item.statusCode !== "ATIVO").slice(0, 6);
  return `
    <div class="stack">
      <div class="panel spotlight-panel">
        <div>
          <div class="eyebrow">Resumo da Unidade</div>
          <h3>Leitura rápida da unidade para tomada de decisão.</h3>
          <div class="text-small">Resultado da unidade, vendedores, alertas, clientes em risco e tarefas da equipe sem abrir tabelas pesadas primeiro.</div>
        </div>
        <div class="actions">
          <button class="btn btn-secondary" onclick="switchTab('crm-agenda')">CRM da equipe</button>
          <button class="btn btn-primary" onclick="switchTab('vendedores')">Indicadores detalhados</button>
        </div>
      </div>
      <div class="kpi-grid">
        ${kpiCard("Resultado da unidade", currency(state.dashboard.summary.revenueNet), "Meta", currency(state.dashboard.summary.revenueGoal))}
        ${kpiCard("Atingimento", pct(state.dashboard.summary.goalAttainmentPct), "Proj.", pct(state.dashboard.summary.projectedGoalAttainmentPct))}
        ${kpiCard("Clientes em risco", number(clientsAtRisk.length), "Tarefas abertas", number(state.crm.summary.openTasks))}
        ${kpiCard("Alertas da unidade", number(alerts.length), "Vendedores", number((state.dashboard.sellerRanking || []).length))}
      </div>
      <div class="grid-2">
        <div class="table-card">
          <div class="section-title"><h3>Alertas da unidade</h3></div>
          <div class="alert-grid">${alerts.map(managementAlertCard).join("") || emptyStateCard("Nenhum alerta relevante no momento.")}</div>
        </div>
        <div class="table-card">
          <div class="section-title"><h3>Clientes em risco</h3></div>
          <div class="timeline-list">
            ${clientsAtRisk.map((item) => `<div class="timeline-item"><strong>${escapeHtml(item.clientName)}</strong><div class="text-small">${escapeHtml(item.statusCode)} · ${escapeHtml(item.primaryReason || "-")}</div><div class="actions"><button class="btn btn-secondary" onclick="openCrmClient('${escapeHtml(item.clientKey)}')">Ver cliente</button></div></div>`).join("") || '<div class="timeline-item"><div class="text-small">Sem clientes em risco no recorte.</div></div>'}
          </div>
        </div>
      </div>
      ${executiveExpandSection("details", "Ver análise detalhada", `<div class="table-wrap"><table><thead><tr><th>Vendedor</th><th>Líquido</th><th>Meta</th><th>% Meta</th><th>Score</th></tr></thead><tbody>${sellerRows((state.dashboard.sellerRanking || []).slice(0, 12))}</tbody></table></div>`)}
      ${executiveExpandSection("units", "Ver performance por unidade", `<div class="table-wrap"><table><thead><tr><th>Unidade</th><th>Líquido</th><th>Meta</th><th>% Meta</th><th>% Proj.</th><th>Devolução</th><th>% Dev.</th><th>Margem</th><th>Qtd. Peças</th><th>Ticket/Peça</th><th>Meta diária</th></tr></thead><tbody>${unitRows(state.dashboard.unitPerformance || [])}</tbody></table></div>`)}
    </div>
  `;
}

function auditBadge(issueCount) {
  if (issueCount <= 0) return '<span class="status-tag good">Sem inconsistências</span>';
  if (issueCount <= 3) return `<span class="status-tag warning">${number(issueCount)} alertas</span>`;
  return `<span class="status-tag bad">${number(issueCount)} inconsistências</span>`;
}

function auditMetricValue(label, value, formatter = number) {
  return `<div class="text-small"><strong>${escapeHtml(label)}:</strong> ${escapeHtml(formatter(value))}</div>`;
}

function auditValueText(value) {
  if (value === null || value === undefined || value === "") return "-";
  if (typeof value === "number") return Number.isInteger(value) ? number(value) : String(value);
  if (typeof value === "object") return JSON.stringify(value);
  return String(value);
}

function integrityAuditCard(title, issueCount, detailLines = []) {
  return `
    <div class="table-card">
      <div class="section-title">
        <div>
          <h3>${escapeHtml(title)}</h3>
          <div class="text-small">${auditBadge(issueCount)}</div>
        </div>
      </div>
      <div class="stack">
        ${detailLines.join("") || '<div class="text-small">Sem dados.</div>'}
      </div>
    </div>
  `;
}

function integrityAuditIssuesTable(rows) {
  if (!(rows || []).length) {
    return `<div class="message success">Nenhuma inconsistência encontrada na competência selecionada.</div>`;
  }
  return `
    <div class="table-card">
      <div class="section-title">
        <div>
          <h3>Inconsistências encontradas</h3>
          <div class="text-small">${number(rows.length)} registros para análise operacional.</div>
        </div>
      </div>
      <div class="table-wrap">
        <table>
          <thead>
            <tr>
              <th>Severidade</th>
              <th>Área</th>
              <th>Mensagem</th>
              <th>Esperado</th>
              <th>Atual</th>
            </tr>
          </thead>
          <tbody>
            ${rows.map((row) => `<tr>
              <td>${escapeHtml(row.severity || "")}</td>
              <td>${escapeHtml(row.area || "")}</td>
              <td>${escapeHtml(row.message || "")}</td>
              <td>${escapeHtml(auditValueText(row.expected))}</td>
              <td>${escapeHtml(auditValueText(row.actual))}</td>
            </tr>`).join("")}
          </tbody>
        </table>
      </div>
    </div>
  `;
}

function integrityAuditView() {
  const audit = state.integrityAudit.data;
  const issueRows = audit?.issues || [];
  const issueCountByArea = issueRows.reduce((acc, item) => {
    const key = item.area || "GERAL";
    acc[key] = (acc[key] || 0) + 1;
    return acc;
  }, {});
  const importTotals = audit?.imports?.totals || {};
  const revenue = audit?.revenueCheck || {};
  const goals = audit?.goalsCheck || {};
  const projection = audit?.projectionCheck || {};
  const comparisons = audit?.comparisonsCheck || {};
  const crm = audit?.crmCheck || {};
  const permissions = audit?.permissionCheck || {};
  const competenceOptions = integrityAuditCompetenceOptions();
  return `
    <div class="stack">
      <div class="form-card">
        <div class="section-title">
          <div>
            <h3>Auditoria de Integridade</h3>
            <div class="text-small">Execute a verificação sob demanda para validar importações, cálculos, comparativos, CRM e permissões.</div>
          </div>
        </div>
        <div class="two-column-form">
          <div class="field">
            <label>Competência</label>
            <select onchange="setIntegrityAuditCompetence(this.value)">
              <option value="">Selecione</option>
              ${competenceOptions.map((item) => `<option value="${escapeHtml(item)}" ${state.integrityAudit.competence === item ? "selected" : ""}>${escapeHtml(item)}</option>`).join("")}
            </select>
          </div>
          <div class="field">
            <label>Ação</label>
            <div class="actions">
              <button class="btn btn-primary" onclick="runIntegrityAudit()">${state.ui.loading.integrityAudit ? "Executando..." : "Executar auditoria"}</button>
            </div>
          </div>
        </div>
        ${state.integrityAudit.error ? `<div class="message error">${escapeHtml(state.integrityAudit.error)}</div>` : ""}
        ${state.ui.loading.integrityAudit ? '<div class="loader panel">Executando auditoria de integridade...</div>' : ""}
      </div>
      ${audit ? `
        <div class="grid-3">
          ${integrityAuditCard("Importações", issueCountByArea.IMPORTACOES || 0, [
            auditMetricValue("Competência", audit.competence, (value) => String(value || "-")),
            auditMetricValue("Pacotes", importTotals.imports || 0),
            auditMetricValue("Linhas lidas", importTotals.rowsRead || 0),
            auditMetricValue("Linhas gravadas", importTotals.rowsWritten || 0),
            auditMetricValue("Duplicidades ignoradas", importTotals.duplicateRowsSkipped || 0),
            auditMetricValue("Pendências", importTotals.pendingIssues || 0),
          ])}
          ${integrityAuditCard("Faturamento", issueCountByArea.FATURAMENTO || 0, [
            auditMetricValue("Resumo", revenue.summaryRevenueNet || 0, currency),
            auditMetricValue("Soma unidades", revenue.sumUnitsRevenueNet || 0, currency),
            auditMetricValue("Oficial unidades", revenue.officialUnitRevenueNet || 0, currency),
            auditMetricValue("Soma vendedores", revenue.sumSellersRevenueNet || 0, currency),
            auditMetricValue("Soma cidades", revenue.sumCitiesRevenueNet || 0, currency),
          ])}
          ${integrityAuditCard("Metas", issueCountByArea.META || 0, [
            auditMetricValue("Meta grupo", goals.summaryRevenueGoal || 0, currency),
            auditMetricValue("Meta oficial unidades", goals.officialUnitRevenueGoal || 0, currency),
            auditMetricValue("Soma metas unidade", goals.dashboardUnitGoalsSum || 0, currency),
            auditMetricValue("Duplicidade unidade", (goals.duplicateUnitGoals || []).length),
            auditMetricValue("Duplicidade vendedor", (goals.duplicateSellerGoals || []).length),
          ])}
          ${integrityAuditCard("Projeção D-1", issueCountByArea.PROJECAO || 0, [
            auditMetricValue("Cutoff", projection.cutoffDate || "-", (value) => String(value)),
            auditMetricValue("Dias úteis totais", projection.calendar?.totalWorkingDays || 0),
            auditMetricValue("Dias transcorridos", projection.calendar?.elapsedWorkingDays || 0),
            auditMetricValue("Realizado diário", projection.dailyRevenueActual?.actual || 0, currency),
            auditMetricValue("Projeção", projection.projectedRevenue?.actual || 0, currency),
          ])}
          ${integrityAuditCard("Comparativos", issueCountByArea.COMPARATIVO || 0, [
            auditMetricValue("Competência atual", audit.competence, (value) => String(value || "-")),
            auditMetricValue("Mês anterior", comparisons.group?.previousActual?.competence || "-", (value) => String(value)),
            auditMetricValue("Ano anterior", comparisons.group?.yearOverYearActual?.competence || "-", (value) => String(value)),
            auditMetricValue("Amostra unidade", comparisons.scopeSamples?.unit?.unitName || "-", (value) => String(value)),
            auditMetricValue("Amostra vendedor", comparisons.scopeSamples?.seller?.sellerName || "-", (value) => String(value)),
          ])}
          ${integrityAuditCard("CRM", issueCountByArea.CRM || 0, [
            auditMetricValue("Base clientes", crm.baseCount || 0),
            auditMetricValue("Perfis importados", crm.crmClientProfiles || 0),
            auditMetricValue("Resumo distinto", crm.crmClientSummaryDistinct || 0),
            auditMetricValue("Páginas @50", crm.page50?.totalPages || 0),
            auditMetricValue("Páginas @100", crm.page100?.totalPages || 0),
          ])}
          ${integrityAuditCard("Permissões", issueCountByArea.PERMISSAO || 0, [
            auditMetricValue("Usuários auditados", (permissions.users || []).length),
            auditMetricValue("Primeiro perfil", permissions.users?.[0]?.role || "-", (value) => String(value)),
            auditMetricValue("Primeiro usuário", permissions.users?.[0]?.username || "-", (value) => String(value)),
          ])}
        </div>
        ${integrityAuditIssuesTable(issueRows)}
      ` : '<div class="message success">Selecione uma competência e execute a auditoria para ver os resultados.</div>'}
    </div>
  `;
}

function autoImportPanel() {
  const ai = state.autoImport;
  const folders = ai?.folders || [];
  const logs = ai?.logs || [];

  function statusIcon(s) {
    return s === "sucesso" ? "✅" : s === "erro" ? "❌" : "⏳";
  }

  function folderCard(f) {
    const hasPending = f.pendingFiles.length > 0;
    return `
      <div style="background:var(--surface);border:1px solid var(--line);border-radius:10px;padding:14px 16px">
        <div style="display:flex;align-items:center;gap:8px;margin-bottom:6px">
          <span style="font-size:18px">${f.scope === "sales" ? "📊" : f.scope === "cost" ? "💰" : "👥"}</span>
          <strong style="font-size:13px">${escapeHtml(f.label)}</strong>
          ${hasPending ? `<span class="soft-badge" style="background:#f39c12;color:#fff">${f.pendingFiles.length} pendente${f.pendingFiles.length > 1 ? "s" : ""}</span>` : `<span class="soft-badge">Vazia</span>`}
        </div>
        <div style="font-size:11px;color:var(--muted);margin-bottom:6px;word-break:break-all">${escapeHtml(f.folder)}/</div>
        ${hasPending ? `<div style="font-size:12px;color:var(--accent)">${f.pendingFiles.map((n) => `📄 ${escapeHtml(n)}`).join("<br>")}</div>` : ""}
      </div>`;
  }

  const recentLogs = logs.slice(0, 10);

  return `
    <div class="form-card">
      <div class="section-title">
        <div>
          <h3>🤖 Auto-Import</h3>
          <div class="text-small">Coloque o CSV na pasta correspondente — o sistema importa automaticamente a cada 5 minutos.</div>
        </div>
        <button class="btn btn-ghost btn-sm" onclick="loadAutoImportStatus(); addMessage('success','Status atualizado.')">↻ Atualizar</button>
      </div>
      ${!ai ? `<div class="message">Carregando status… <button class="btn btn-ghost btn-sm" onclick="loadAutoImportStatus()">Carregar</button></div>` : `
      <div style="display:grid;grid-template-columns:repeat(auto-fill,minmax(200px,1fr));gap:12px;margin-bottom:16px">
        ${folders.map(folderCard).join("")}
      </div>
      ${recentLogs.length ? `
      <div class="table-wrap">
        <table>
          <thead><tr><th>Quando</th><th>Pasta</th><th>Competência</th><th>Status</th><th>Mensagem</th></tr></thead>
          <tbody>
            ${recentLogs.map((l) => `
              <tr>
                <td style="white-space:nowrap;font-size:12px">${escapeHtml((l.ranAt || "").slice(0, 16).replace("T"," "))}</td>
                <td>${escapeHtml(l.folder)}</td>
                <td>${escapeHtml(l.competence || "—")}</td>
                <td>${statusIcon(l.status)} ${escapeHtml(l.status)}</td>
                <td style="font-size:12px;color:${l.status === "erro" ? "var(--bad)" : "inherit"}">${escapeHtml(l.message || "")}</td>
              </tr>`).join("")}
          </tbody>
        </table>
      </div>` : `<div class="message">Nenhum import automático registrado ainda.</div>`}
      `}
    </div>`;
}

function importacoesView() {
  if (!state.admin) return `<div class="loader panel">Carregando importações...</div>`;
  if (!state.autoImport) loadAutoImportStatus();
  return `
    <div class="stack">
      ${autoImportPanel()}
      <div class="grid-3">
        <div class="timeline-card"><div class="section-title"><h3>Importações</h3></div><div class="text-small">${state.admin.imports.length} registros auditáveis</div><div class="timeline-list">${state.admin.imports.slice(0, 5).map((item) => `<div class="timeline-item"><strong>${item.competence}</strong><div class="text-small">${item.import_action}</div></div>`).join("")}</div></div>
        <div class="timeline-card"><div class="section-title"><h3>Pendências</h3></div><div class="timeline-list">${state.admin.issues.slice(0, 5).map((item) => `<div class="timeline-item"><strong>${escapeHtml(item.issue_type)}</strong><div class="text-small">${escapeHtml(item.reference_value)} · ${escapeHtml(item.status)}</div></div>`).join("")}</div></div>
        <div class="timeline-card"><div class="section-title"><h3>Auditoria</h3></div><div class="timeline-list">${state.admin.audit.slice(0, 5).map((item) => `<div class="timeline-item"><strong>${escapeHtml(item.entity_type)}</strong><div class="text-small">${escapeHtml(item.action)} · ${escapeHtml(item.created_at)}</div></div>`).join("")}</div></div>
      </div>
      <div class="grid-2">
        <div class="form-card">
          <div class="section-title"><div><h3>Importações operacionais</h3><div class="text-small">Fluxos de custo, faturamento e CRM em cards separados.</div></div></div>
          <div class="stack">
            <div class="form-card subtle-card">
              <div class="section-title"><div><h3>Custo venda</h3><div class="text-small">Envie unidade e vendedor para substituir a base da competência.</div></div></div>
              <div class="stack">
                <div class="two-column-form">
                  <div class="field"><label>Custo venda unidade</label><input id="import-cost-unit-file" type="file" /></div>
                  <div class="field"><label>Custo venda vendedor</label><input id="import-cost-vendor-file" type="file" /></div>
                </div>
                <div class="field"><label>Competência confirmada</label><input id="import-cost-competence" placeholder="AAAA-MM" /></div>
                <div class="actions"><button class="btn btn-secondary" onclick="previewImport('cost')">Analisar custo venda</button><button class="btn btn-primary" onclick="submitImport('cost')">Importar custo venda</button></div>
                <div id="import-cost-feedback" class="text-small"></div>
              </div>
            </div>
            <div class="form-card subtle-card">
              <div class="section-title"><div><h3>Faturamento detalhado</h3><div class="text-small">Somar ou substituir o 01fat.</div></div></div>
              <div class="stack">
                ${(() => {
                  const summary = (state.admin?.salesDetailSummary || []);
                  if (!summary.length) return "";
                  const current = summary[0];
                  const lastDate = current?.last_issue_date ? current.last_issue_date.slice(0, 10) : "—";
                  const rows = Number(current?.row_count || 0).toLocaleString("pt-BR");
                  return `
                    <div style="display:flex;flex-wrap:wrap;gap:12px;padding:10px 14px;background:rgba(15,48,68,0.06);border-radius:8px;font-size:13px">
                      <div><span style="color:var(--muted);font-weight:600">Competência atual: </span><strong>${escapeHtml(current?.competence || "—")}</strong></div>
                      <div><span style="color:var(--muted);font-weight:600">Última data no banco: </span><strong style="color:var(--accent)">${escapeHtml(lastDate)}</strong></div>
                      <div><span style="color:var(--muted);font-weight:600">Registros: </span><strong>${rows}</strong></div>
                    </div>`;
                })()}
                <input id="import-sales-file" type="file" />
                <div class="two-column-form">
                  <div class="field"><label>Competência confirmada</label><input id="import-sales-competence" placeholder="AAAA-MM" /></div>
                  <div class="field"><label>Ação</label><select id="import-sales-action"><option value="somar">Somar/incorporar</option><option value="substituir">Substituir</option></select></div>
                </div>
                <div class="actions"><button class="btn btn-secondary" onclick="previewImport('sales')">Analisar faturamento</button><button class="btn btn-primary" onclick="submitImport('sales')">Importar faturamento</button></div>
                <div id="import-sales-feedback" class="text-small"></div>
              </div>
            </div>
            <div class="form-card subtle-card">
              <div class="section-title"><div><h3>CRM carteira</h3><div class="text-small">Importe cadastro de clientes e consolidado por cliente.</div></div></div>
              <div class="stack">
                <div class="two-column-form">
                  <div class="field"><label>Cadastro de clientes <span style="font-size:11px;color:var(--muted)">(opcional)</span></label><input id="import-crm-clients-file" type="file" /></div>
                  <div class="field"><label>Faturamento consolidado cliente</label><input id="import-crm-summary-file" type="file" /></div>
                </div>
                <div class="field"><label>Competência do pacote CRM</label><input id="import-crm-competence" placeholder="AAAA-MM" /></div>
                <div class="actions"><button class="btn btn-secondary" onclick="previewImport('crm')">Analisar CRM</button><button class="btn btn-primary" onclick="submitImport('crm')">Importar CRM</button></div>
                <div id="import-crm-feedback" class="text-small"></div>
              </div>
            </div>
          </div>
        </div>
        <div class="form-card">
          <div class="section-title"><div><h3>Importação administrativa</h3><div class="text-small">Templates, importação administrativa e backup.</div></div></div>
          <div class="stack">
            <div class="actions">
              <button class="btn btn-ghost" onclick="downloadFile('/api/templates/people')">Pessoas</button>
              <button class="btn btn-ghost" onclick="downloadFile('/api/templates/vacations')">Férias</button>
              <button class="btn btn-ghost" onclick="downloadFile('/api/templates/holidays')">Feriados</button>
              <button class="btn btn-ghost" onclick="downloadFile('/api/templates/goals_seller')">Meta vendedor</button>
              <button class="btn btn-ghost" onclick="downloadFile('/api/templates/goals_unit')">Meta unidade</button>
              <button class="btn btn-ghost" onclick="downloadFile('/api/templates/clients')">Clientes PF/PJ</button>
              <button class="btn btn-ghost" onclick="downloadFile('/api/templates/users')">Usuários</button>
              <button class="btn btn-secondary" onclick="downloadFile('/api/backup/database')">Backup</button>
            </div>
            <div class="two-column-form">
              <div class="field">
                <label>Tipo de cadastro</label>
                <select id="admin-import-type">
                  <option value="people">Pessoas</option>
                  <option value="vacations">Férias</option>
                  <option value="holidays">Feriados</option>
                  <option value="goals-seller">Meta vendedor</option>
                  <option value="goals-unit">Meta unidade</option>
                  <option value="clients">Clientes PF/PJ</option>
                  <option value="users">Usuários</option>
                </select>
              </div>
              <div class="field"><label>Arquivo CSV</label><input id="admin-import-file" type="file" /></div>
            </div>
            <div class="actions"><button class="btn btn-primary" onclick="submitAdminImport()">Importar cadastro</button></div>
          </div>
        </div>
      </div>
    </div>
  `;
}

administracaoView = function administracaoViewOverride() {
  if (!state.admin) return `<div class="loader panel">Carregando administração...</div>`;
  const section = state.adminSection || "cadastros";
  const adminSectionNav = `
    <div class="form-card">
      <div class="section-title">
        <div>
          <h3>Administração</h3>
          <div class="text-small">Escolha a frente de governança que deseja operar.</div>
        </div>
      </div>
      <div class="actions">
        <button class="btn ${section === "cadastros" ? "btn-primary" : "btn-ghost"}" onclick="setAdminSection('cadastros')">Cadastros e pendências</button>
        <button class="btn ${section === "auditoria-integridade" ? "btn-primary" : "btn-ghost"}" onclick="setAdminSection('auditoria-integridade')">Auditoria de Integridade</button>
      </div>
    </div>
  `;
  if (section === "auditoria-integridade") {
    return `<div class="stack">${adminSectionNav}${integrityAuditView()}</div>`;
  }
  return `
    <div class="stack">
      ${adminSectionNav}
      <div class="form-card">
        <div class="section-title"><div><h3>Pendências</h3><div class="text-small">Resolva vínculos e correspondências sem abrir telas gigantes.</div></div></div>
        <div class="stack">${pendingIssueCards()}</div>
      </div>
      <div class="grid-2">
        ${usersAdminTableCard()}
        ${adminTableCard("Pendências de importação", ["issue_type", "reference_value", "status", "competence"], state.admin.issues)}
      </div>
      <div class="grid-2">
        ${adminTableCard("Cadastros de pessoas", ["person_name", "role_classification", "base_unit", "valid_from", "valid_to", "source"], state.admin.people)}
        ${adminTableCard("Base de clientes PF/PJ", ["client_name", "document_number", "person_type", "source", "confidence_score", "notes"], state.admin.clients)}
      </div>
      <div class="grid-2">
        ${adminTableCard("Auditoria", ["entity_type", "action", "entity_id", "created_at"], state.admin.audit)}
        ${adminTableCard("Mapeamento de cidades", ["city_name", "principal_unit", "valid_from", "valid_to", "source"], state.admin.cityMappings || [])}
      </div>
    </div>
  `;
};

configuracoesView = function adminViewGoalsSellerUnitFinal() {
  if (!state.admin) return `<div class="loader panel">Carregando configurações...</div>`;
  const sellerOptions = sellerPeopleOptions();
  const userPasswordLabel = state.userEditor.id ? "Nova senha (opcional)" : "Senha inicial";
  const userSubmitLabel = state.userEditor.id ? "Salvar ajustes do usuário" : "Salvar usuário";
  const userTitle = state.userEditor.id ? "Editar usuário" : "Criar usuário";
  const userRole = state.userEditor.role || "Administrador";
  const sellerGoalEditor = state.goalEditors.seller;
  const unitGoalEditor = state.goalEditors.unit;

  return `
    <div class="stack">
      <div class="grid-2">
        <div class="form-card">
          <div class="section-title"><div><h3>Usuários</h3><div class="text-small">Controle de acesso por vendedor, gerente, analista e administrador.</div></div></div>
          <form onsubmit="saveUser(event)" class="stack">
            <input id="user-id" type="hidden" value="${escapeHtml(state.userEditor.id)}" />
            <strong>${userTitle}</strong>
            <div class="two-column-form">
              <div class="field"><label>Usuário</label><input id="user-username" value="${escapeHtml(state.userEditor.username)}" required /></div>
              <div class="field"><label>Nome completo</label><input id="user-full-name" value="${escapeHtml(state.userEditor.fullName)}" required /></div>
              <div class="field"><label>Perfil</label><select id="user-role" onchange="setUserRole(this.value)"><option ${userRole === "Administrador" ? "selected" : ""}>Administrador</option><option ${userRole === "Gerente" ? "selected" : ""}>Gerente</option><option ${userRole === "Analista" ? "selected" : ""}>Analista</option><option ${userRole === "Vendedor" ? "selected" : ""}>Vendedor</option></select></div>
              ${userRole === "Vendedor"
                ? `<div class="field"><label>Pessoa vinculada</label><select id="user-linked-person"><option value="">Selecione</option>${sellerOptions.map((person) => `<option value="${escapeHtml(person.person_name)}" ${state.userEditor.linkedPersonName === person.person_name ? "selected" : ""}>${escapeHtml(person.person_name)}${person.base_unit ? ` · ${escapeHtml(person.base_unit)}` : ""}</option>`).join("")}</select></div>`
                : ""}
              ${["Gerente", "Analista"].includes(userRole)
                ? `<div class="field field-span-2"><label>Unidades vinculadas</label><div class="checkbox-grid">${(state.options.units || []).map((unit) => `<label class="checkbox-item"><input type="checkbox" ${state.userEditor.linkedUnits.includes(unit) ? "checked" : ""} onchange="toggleUserLinkedUnit('${unit}')" /><span>${escapeHtml(unit)}</span></label>`).join("")}</div></div>`
                : ""}
              <div class="field"><label>${userPasswordLabel}</label><input id="user-password" type="password" ${state.userEditor.id ? "" : "required"} /></div>
            </div>
            <div class="actions">
              <button class="btn btn-primary" type="submit">${userSubmitLabel}</button>
              ${state.userEditor.id ? '<button class="btn btn-ghost" type="button" onclick="cancelUserEdit()">Cancelar edição</button>' : ""}
            </div>
          </form>
        </div>
        <div class="form-card">
          <div class="section-title"><div><h3>Metas e score</h3><div class="text-small">Metas por vendedor, unidade e pesos do score.</div></div></div>
          <div class="stack">
            <form id="seller-goal-form" onsubmit="saveSellerGoal(event)" class="stack">
              <div class="section-title compact">
                <div>
                  <strong>${sellerGoalEditor.editing ? "Editar meta por vendedor" : "Meta por vendedor"}</strong>
                  <div class="text-small">Meta individual por competência.</div>
                </div>
                ${sellerGoalEditor.editing === true ? '<span class="status-tag warn">Modo edição</span>' : ""}
              </div>

              <div class="two-column-form">
                <div class="field">
                  <label>Competência</label>
                  <input
                    id="goal-seller-competence"
                    placeholder="2026-04"
                    value="${escapeHtml(sellerGoalEditor.competence)}"
                    required
                  />
                </div>

                <div class="field">
                  <label>Vendedor</label>
                  <select id="goal-seller-name" required onchange="(function(){const sel=document.getElementById('goal-seller-name');const opt=sel.options[sel.selectedIndex];const unit=opt?opt.dataset.unit||'':'';const unitSel=document.getElementById('goal-seller-unit');if(unitSel&&unit)unitSel.value=unit;})()">
                    <option value="">Selecione</option>
                    ${sellerPeopleOptions().map(p => `<option value="${escapeHtml(p.person_name)}" data-unit="${escapeHtml(p.base_unit||'')}" ${sellerGoalEditor.sellerName === p.person_name ? "selected" : ""}>${escapeHtml(p.person_name)}${p.base_unit ? ` · ${escapeHtml(p.base_unit)}` : ""}</option>`).join("")}
                  </select>
                </div>

                <div class="field">
                  <label>Unidade base</label>
                  <select id="goal-seller-unit">
                    <option value="">Selecione</option>
                    ${(state.options.units || []).map(u => `<option value="${escapeHtml(u)}" ${sellerGoalEditor.baseUnit === u ? "selected" : ""}>${escapeHtml(u)}</option>`).join("")}
                  </select>
                </div>

                <div class="field">
                  <label>Meta faturamento</label>
                  <input
                    id="goal-seller-revenue"
                    type="number"
                    step="0.01"
                    value="${escapeHtml(String(sellerGoalEditor.revenueGoal || ""))}"
                    required
                  />
                </div>
              </div>

              <div class="actions">
                <button class="btn btn-primary" type="submit">
                  ${sellerGoalEditor.editing === true ? "Atualizar meta vendedor" : "Salvar meta vendedor"}
                </button>

                ${sellerGoalEditor.editing === true ? `<button
type="button"
class="btn btn-ghost"
onclick="cancelSellerGoalEdit()"
>
Cancelar edição
</button>` : ""}
              </div>
            </form>

            <form id="unit-goal-form" onsubmit="saveUnitGoal(event)" class="stack">
              <div class="section-title compact">
                <div>
                  <strong>${unitGoalEditor.editing ? "Editar meta por unidade" : "Meta por unidade"}</strong>
                  <div class="text-small">Meta consolidada por unidade e competência.</div>
                </div>
                ${unitGoalEditor.editing === true ? '<span class="status-tag warn">Modo edição</span>' : ""}
              </div>

              <div class="two-column-form">
                <div class="field">
                  <label>Competência</label>
                  <input
                    id="goal-unit-competence"
                    placeholder="2026-04"
                    value="${escapeHtml(unitGoalEditor.competence)}"
                    required
                  />
                </div>

                <div class="field">
                  <label>Unidade</label>
                  <select id="goal-unit-name" required>
                    <option value="">Selecione</option>
                    ${(state.options.units || []).map(u => `<option value="${escapeHtml(u)}" ${unitGoalEditor.unitName === u ? "selected" : ""}>${escapeHtml(u)}</option>`).join("")}
                  </select>
                </div>

                <div class="field">
                  <label>Meta faturamento</label>
                  <input
                    id="goal-unit-revenue"
                    type="number"
                    step="0.01"
                    value="${escapeHtml(String(unitGoalEditor.revenueGoal || ""))}"
                    required
                  />
                </div>
              </div>

              <div class="actions">
                <button class="btn btn-primary" type="submit">
                  ${unitGoalEditor.editing === true ? "Atualizar meta unidade" : "Salvar meta unidade"}
                </button>

                ${unitGoalEditor.editing === true ? `<button
type="button"
class="btn btn-ghost"
onclick="cancelUnitGoalEdit()"
>
Cancelar edição
</button>` : ""}
              </div>
            </form>

            <form onsubmit="saveScoreConfig(event)" class="stack">
              <strong>Pesos do score</strong>
              <div class="two-column-form">
                <div class="field"><label>Vigência inicial</label><input id="score-valid-from" placeholder="2026-04" required /></div>
                <div class="field"><label>Meta</label><input id="score-goal" type="number" step="0.01" value="30" required /></div>
                <div class="field"><label>Ticket</label><input id="score-ticket" type="number" step="0.01" value="15" required /></div>
                <div class="field"><label>Clientes</label><input id="score-clients" type="number" step="0.01" value="15" required /></div>
                <div class="field"><label>Mix</label><input id="score-mix" type="number" step="0.01" value="15" required /></div>
                <div class="field"><label>Devolução</label><input id="score-returns" type="number" step="0.01" value="25" required /></div>
              </div>
              <button class="btn btn-primary" type="submit">Salvar score</button>
            </form>
          </div>
        </div>
      </div>
      <div class="grid-2">
        <div class="form-card">
          <div class="section-title"><div><h3>Pessoas e feriados</h3><div class="text-small">Cadastros operacionais essenciais.</div></div></div>
          <div class="stack">
            <form onsubmit="savePerson(event)" class="stack">
              <strong>Pessoa e classificação</strong>
              <div class="two-column-form">
                <div class="field"><label>Nome</label><input id="person-name" required /></div>
                <div class="field"><label>Classificação</label><select id="person-role"><option>Vendedor</option><option>Gerente</option><option>Outro</option></select></div>
                <div class="field"><label>Unidade base</label><input id="person-unit" placeholder="MATRIZ" /></div>
                <div class="field"><label>Vigência inicial</label><input id="person-valid-from" type="date" required /></div>
              </div>
              <button class="btn btn-secondary" type="submit">Salvar pessoa</button>
            </form>
            <form onsubmit="saveHoliday(event)" class="stack">
              <strong>Feriado</strong>
              <div class="two-column-form">
                <div class="field"><label>Data</label><input id="holiday-date" type="date" required /></div>
                <div class="field"><label>Descrição</label><input id="holiday-name" required /></div>
              </div>
              <button class="btn btn-secondary" type="submit">Salvar feriado</button>
            </form>
          </div>
        </div>
        <div class="stack">
          ${adminTableCard("Configuração do score", ["valid_from_competence", "weight_goal", "weight_ticket", "weight_clients", "weight_mix", "weight_returns"], state.admin.scoreConfigs)}
          ${sellerGoalsTableCard()}
          ${unitGoalsTableCard()}
          ${adminTableCard("Feriados", ["holiday_date", "holiday_name", "scope"], state.admin.holidays || [])}
          ${vacationTableCard()}
        </div>
      </div>
    </div>
  `;
};

// ─── PLACAR DA EQUIPE ────────────────────────────────────────────────────────

function placardaEquipeView() {
  if (!state.teamScore) return `<div class="loader panel">Carregando placar da equipe…</div>`;
  if (state.teamScore.error) return `<div class="panel"><div class="section-title"><h3>Erro ao carregar placar</h3></div><div class="text-small">${escapeHtml(state.teamScore.error)}</div><button class="btn btn-secondary" onclick="loadTeamScore(); addMessage('success','Tentando novamente…')">↻ Tentar novamente</button></div>`;
  const ts = state.teamScore;
  const allSellers = ts.sellers || [];
  const s = ts.summary || {};

  // Scoping por papel: Gerente vê apenas sua(s) unidade(s); Admin/Diretor filtra livremente
  const isManager = roleIsManager();
  const managerUnits = isManager ? (state.user?.linkedUnits || []).map((u) => u.trim().toUpperCase()) : [];
  const scopedSellers = isManager && managerUnits.length
    ? allSellers.filter((r) => managerUnits.includes((r.baseUnit || "").trim().toUpperCase()))
    : allSellers;

  // Filtro de unidade (apenas Admin/Diretor)
  const unitFilter = !isManager ? (state.crm.sellerFilters.unit || "") : "";
  const sellers = unitFilter ? scopedSellers.filter((r) => (r.baseUnit || "").toUpperCase() === unitFilter.toUpperCase()) : scopedSellers;

  // Todas as unidades presentes
  const units = [...new Set(scopedSellers.map((r) => r.baseUnit || "").filter(Boolean))].sort();

  function zoneBadge(row) {
    if (!row.eligible)              return `<span class="status-tag bad">Fora da meta</span>`;
    if (row.totalPoints >= 100)     return `<span class="status-tag good">🏆 Premiação completa</span>`;
    if (row.totalPoints >= 60)      return `<span class="status-tag warn">⚡ Na zona</span>`;
    return `<span class="status-tag">Acumulando</span>`;
  }

  function miniBar(pts, max, tone) {
    const w = max > 0 ? Math.min(Math.round((pts / max) * 100), 100) : 0;
    return `<div class="score-bar-track" style="height:6px;margin-top:3px"><div class="score-bar-fill ${tone}" style="width:${w}%;height:6px"></div></div>`;
  }

  // KPIs por unidade (visão gerencial consolidada)
  const byUnit = {};
  for (const row of scopedSellers) {
    const u = row.baseUnit || "Sem Unidade";
    if (!byUnit[u]) byUnit[u] = { total: 0, eligible: 0, inZone: 0, full: 0, totalPts: 0, totalPrize: 0 };
    byUnit[u].total++;
    if (row.eligible) byUnit[u].eligible++;
    if (row.totalPoints >= 60) byUnit[u].inZone++;
    if (row.totalPoints >= 100) byUnit[u].full++;
    byUnit[u].totalPts += row.totalPoints;
    byUnit[u].totalPrize += row.estimatedPrize || 0;
  }

  function unitSummaryCards() {
    return Object.entries(byUnit).sort(([a],[b]) => a.localeCompare(b)).map(([unit, u]) => `
      <div style="background:var(--surface);border:1px solid var(--line);border-radius:10px;padding:14px 16px;cursor:pointer"
           onclick="state.crm.sellerFilters.unit = state.crm.sellerFilters.unit === '${escapeHtml(unit)}' ? '' : '${escapeHtml(unit)}'; requestRender()"
           style="border:2px solid ${unitFilter === unit ? "var(--accent)" : "var(--line)"}">
        <div style="font-weight:700;font-size:13px;margin-bottom:8px;color:var(--accent)">${escapeHtml(unit)}</div>
        <div style="display:grid;grid-template-columns:1fr 1fr;gap:6px;font-size:12px">
          <div><span style="color:var(--muted)">Vendedores</span><br><strong>${u.total}</strong></div>
          <div><span style="color:var(--muted)">Elegíveis</span><br><strong style="color:${u.eligible === u.total ? "var(--good)" : u.eligible > 0 ? "#f39c12" : "var(--bad)"}">${u.eligible}</strong></div>
          <div><span style="color:var(--muted)">Na zona</span><br><strong style="color:${u.inZone >= u.total * 0.7 ? "var(--good)" : "#f39c12"}">${u.inZone}</strong></div>
          <div><span style="color:var(--muted)">Premiação est.</span><br><strong style="color:var(--good)">${currency(u.totalPrize)}</strong></div>
        </div>
      </div>
    `).join("");
  }

  function attentionList() {
    const needs = sellers.filter((r) => !r.eligible || r.positivacaoPct < 50 || r.callsActual < 30 || r.returnPct > 4.5);
    if (!needs.length) return `<div class="message success">✅ Nenhum alerta crítico${unitFilter ? " em " + unitFilter : " na equipe"}.</div>`;
    return needs.map((r) => {
      const alerts = [];
      if (!r.eligible)             alerts.push(`Meta em ${r.goalPct}% — fora da zona de premiação`);
      if (r.positivacaoPct < 50)   alerts.push(`Positivação baixa: ${r.positivacaoPct}% da carteira`);
      if (r.callsActual < 30)      alerts.push(`Poucas ligações: ${r.callsActual} de 60`);
      if (r.returnPct > 4.5)       alerts.push(`Devolução alta: ${r.returnPct}%`);
      return `
        <div class="timeline-item">
          <strong>${escapeHtml(r.sellerName)}</strong>
          <div class="text-small" style="color:var(--muted)">${escapeHtml(r.baseUnit || "-")}</div>
          ${alerts.map((a) => `<div class="text-small" style="color:var(--bad)">⚠ ${escapeHtml(a)}</div>`).join("")}
        </div>
      `;
    }).join("");
  }

  return `
    <div class="stack">
      <!-- KPIs globais -->
      <div class="kpi-grid">
        ${kpiCard("Vendedores no placar", number(s.total), "Elegíveis", number(s.eligible))}
        ${kpiCard("Na zona de premiação", number(s.inPrizeZone), "Premiação completa", number(s.fullPrize))}
        ${kpiCard("Competência", escapeHtml(ts.competence), "Mês de apuração", "")}
        ${kpiCard("Fora da meta", number(s.total - s.eligible), "Precisam de atenção", number(s.total - s.inPrizeZone))}
      </div>

      <!-- Cards por unidade (apenas Admin/Diretor) -->
      ${!isManager ? `
      <div class="table-card">
        <div class="section-title">
          <div><h3>Visão por Unidade</h3><div class="text-small">Clique em uma unidade para filtrar o ranking abaixo.</div></div>
          <button class="btn btn-ghost btn-sm" onclick="loadTeamScore(); addMessage('success','Placar atualizado.')">↻ Atualizar</button>
        </div>
        <div style="display:grid;grid-template-columns:repeat(auto-fill,minmax(200px,1fr));gap:12px;padding:4px 0">
          ${unitSummaryCards() || '<div class="text-small" style="color:var(--muted)">Nenhuma unidade com dados neste mês.</div>'}
        </div>
      </div>
      ` : `
      <div class="message" style="background:rgba(15,48,68,0.06);padding:10px 16px;font-size:13px">
        📍 Exibindo vendedores da sua unidade: <strong>${escapeHtml(managerUnits.join(", ") || "—")}</strong>
      </div>
      `}

      <!-- Filtro ativo (apenas Admin/Diretor) -->
      ${!isManager && unitFilter ? `<div class="message" style="background:rgba(15,48,68,0.08);display:flex;align-items:center;gap:10px;padding:10px 16px"><span>Filtrando por: <strong>${escapeHtml(unitFilter)}</strong></span><button class="btn btn-ghost btn-sm" onclick="state.crm.sellerFilters.unit='';requestRender()">✕ Limpar filtro</button></div>` : ""}

      <!-- Ranking -->
      <div class="table-card">
        <div class="section-title">
          <div><h3>🏆 Ranking — ${unitFilter ? escapeHtml(unitFilter) : "Toda a equipe"}</h3><div class="text-small">${number(sellers.length)} vendedor${sellers.length !== 1 ? "es" : ""} · ordenado por pontuação</div></div>
        </div>
        <div class="table-wrap">
          <table>
            <thead>
              <tr>
                <th>#</th>
                <th>Vendedor</th>
                ${!unitFilter ? "<th>Unidade</th>" : ""}
                <th>Pontos</th>
                <th>Meta %</th>
                <th>Positivação</th>
                <th>Ligações</th>
                <th>Devoluções</th>
                <th>Status</th>
                <th>Premiação est.</th>
              </tr>
            </thead>
            <tbody>
              ${sellers.map((row, i) => `
                <tr style="${!row.eligible ? "opacity:0.6" : ""}">
                  <td style="font-weight:700;color:${i === 0 ? "#f4c25f" : i === 1 ? "#aaa" : i === 2 ? "#cd7f32" : "inherit"}">${i + 1}º</td>
                  <td><strong>${escapeHtml(row.sellerName)}</strong></td>
                  ${!unitFilter ? `<td class="text-small">${escapeHtml(row.baseUnit || "-")}</td>` : ""}
                  <td>
                    <strong style="font-size:18px;color:${row.totalPoints >= 100 ? "var(--good)" : row.totalPoints >= 60 ? "#f39c12" : "var(--bad)"}">${row.totalPoints}</strong>
                    ${miniBar(row.totalPoints, 150, row.totalPoints >= 100 ? "good" : row.totalPoints >= 60 ? "warn" : "bad")}
                  </td>
                  <td>
                    ${pct(row.goalPct)}
                    ${miniBar(row.goalPts, 50, row.goalPts >= 30 ? "good" : row.goalPts > 0 ? "warn" : "bad")}
                  </td>
                  <td>
                    ${pct(row.positivacaoPct)}
                    ${miniBar(row.positivacaoPts, 20, row.positivacaoPts >= 20 ? "good" : row.positivacaoPts > 0 ? "warn" : "bad")}
                  </td>
                  <td>
                    ${number(row.callsActual)}<span class="text-small">/60</span>
                    ${miniBar(row.callsActual, 60, row.callsActual >= 60 ? "good" : row.callsActual >= 30 ? "warn" : "bad")}
                  </td>
                  <td><span style="color:${row.returnPct > 4.5 ? "var(--bad)" : "inherit"}">${pct(row.returnPct)}</span></td>
                  <td>${zoneBadge(row)}</td>
                  <td><strong style="color:${row.estimatedPrize > 0 ? "var(--good)" : "var(--muted)"}">${row.estimatedPrize > 0 ? currency(row.estimatedPrize) : "-"}</strong></td>
                </tr>
              `).join("") || `<tr><td colspan="${unitFilter ? 9 : 10}">Nenhum vendedor com meta cadastrada neste mês.</td></tr>`}
            </tbody>
          </table>
        </div>
      </div>

      <div class="grid-2">
        <div class="table-card">
          <div class="section-title"><h3>⚠️ Atenção necessária</h3><div class="text-small">Vendedores com alertas críticos este mês.</div></div>
          <div class="timeline-list">${attentionList()}</div>
        </div>
        <div class="table-card">
          <div class="section-title"><h3>📋 Como ler o placar</h3></div>
          <div class="stack" style="gap:8px;font-size:13px">
            <div>🏆 <strong>Premiação completa</strong> — 100+ pontos, premiação 100% garantida</div>
            <div>⚡ <strong>Na zona</strong> — 60–99 pontos, premiação parcial</div>
            <div>🎯 <strong>Elegível</strong> — bateu 90%+ da meta, pode concorrer</div>
            <div>⚠️ <strong>Fora da meta</strong> — abaixo de 90%, não concorre</div>
            <div style="margin-top:8px;color:var(--muted);font-size:12px">Pontuação máxima: 150 pts. Acima de 100 pts → até 150% da premiação base.</div>
          </div>
        </div>
      </div>
    </div>
  `;
}

// ─── MEU PLACAR (GAMIFICAÇÃO) ────────────────────────────────────────────────

function scorePts(pts, max) {
  const pct = max > 0 ? Math.round((pts / max) * 100) : 0;
  const filled = Math.round(pct / 10);
  const bar = "█".repeat(filled) + "░".repeat(10 - filled);
  return bar;
}

function scoreIndicatorRow(key, ind) {
  const pct = ind.max > 0 ? Math.min((ind.pts / ind.max) * 100, 100) : 0;
  const tone = ind.pts >= ind.max ? "good" : ind.pts > 0 ? "warn" : "bad";
  const icon = ind.pts >= ind.max ? "✅" : ind.pts > 0 ? "⚡" : "○";
  const barWidth = Math.round(pct);
  return `
    <div class="score-indicator-row">
      <div class="score-ind-label">
        <span>${icon} ${escapeHtml(ind.label)}</span>
        <span class="score-ind-pts ${tone}">${ind.pts}/${ind.max} pts</span>
      </div>
      <div class="score-bar-track">
        <div class="score-bar-fill ${tone}" style="width:${barWidth}%"></div>
      </div>
      <div class="score-ind-meta">
        <span class="text-small">Atual: <strong>${ind.unit === "%" ? pct.toFixed(0) + "%" : ind.actual + " " + ind.unit}</strong></span>
        <span class="text-small">Meta: ${ind.unit === "%" ? ind.goal + "%" : ind.goal + " " + ind.unit}</span>
      </div>
    </div>
  `;
}

function meuPlacarView() {
  if (!roleIsSeller()) return "";
  if (!state.sellerScore) return `<div class="loader panel">Carregando seu placar…</div>`;
  const sc = state.sellerScore;
  const ind = sc.indicators;
  const totalPct = Math.min(Math.round((sc.totalPoints / sc.maxPoints) * 100), 150);
  const prizeBarPct = Math.min(Math.round((sc.totalPoints / 100) * 100), 150);

  // Próximo marco
  let nextMilestone = "";
  if (sc.totalPoints < 60)       nextMilestone = `Faltam ${60 - sc.totalPoints} pontos para desbloquear a premiação.`;
  else if (sc.totalPoints < 100) nextMilestone = `Faltam ${100 - sc.totalPoints} pontos para premiação completa (100%).`;
  else if (sc.totalPoints < 130) nextMilestone = `Faltam ${130 - sc.totalPoints} pontos para 130% da premiação!`;
  else                           nextMilestone = `🔥 Acima de 130 pontos! Você está no topo.`;

  // Dica mais impactante
  const gaps = Object.entries(ind)
    .filter(([, v]) => v.pts < v.max)
    .sort(([, a], [, b]) => (b.max - b.pts) - (a.max - a.pts));
  const topGap = gaps[0];
  const dica = topGap
    ? `💡 Foco imediato: <strong>${topGap[1].label}</strong> — você pode ganhar mais ${topGap[1].max - topGap[1].pts} pontos.`
    : `🏆 Você maximizou todos os indicadores mensuráveis!`;

  // Badge de elegibilidade com contexto do gatilho
  const ug = sc.unitGate || {};
  let eligibleBadge;
  if (sc.eligible) {
    const via = ug.sellerOverrides ? " (acima de 105% individual)" : " (unidade atingiu meta)";
    eligibleBadge = `<span class="status-tag good">✅ Elegível à premiação${via}</span>`;
  } else if (!ug.gateOk && !ug.sellerOverrides) {
    eligibleBadge = `<span class="status-tag bad">🔒 Gatilho da unidade não atingido (${ug.unitGoalPct ?? 0}% de 95%)</span>`;
  } else {
    eligibleBadge = `<span class="status-tag bad">❌ Bata 90% da sua meta para ser elegível</span>`;
  }

  const competences = state.options.competences || [];

  return `
    <div class="stack">

      ${competences.length > 1 ? `
        <div class="form-card" style="padding:10px 14px">
          <div style="display:flex;align-items:center;gap:10px;flex-wrap:wrap">
            <label style="font-size:13px;font-weight:600;color:var(--muted)">Período:</label>
            <select style="font-size:13px;padding:6px 10px;border-radius:8px;border:1px solid var(--border)"
              onchange="loadSellerScore(this.value)">
              ${competences.map((c) => `<option value="${escapeHtml(c)}" ${c === sc.competence ? "selected" : ""}>${escapeHtml(c)}</option>`).join("")}
            </select>
          </div>
        </div>
      ` : ""}

      <div class="panel spotlight-panel" style="background:linear-gradient(135deg,#0f3044 0%,#1a5276 100%);color:#fff;border:none">
        <div>
          <div class="eyebrow" style="color:#f4c25f;font-weight:800">MEU PLACAR — ${escapeHtml(sc.competence)}</div>
          <h3 style="color:#fff;margin:8px 0 4px">${escapeHtml(sc.sellerName)}</h3>
          <div style="font-size:13px;color:rgba(255,255,255,0.7)">Acompanhe seus pontos e premiação estimada em tempo real</div>
          <div style="margin-top:12px;display:flex;align-items:center;gap:16px;flex-wrap:wrap">
            ${eligibleBadge}
          </div>
        </div>
        <div style="text-align:center;min-width:160px;max-width:200px;overflow:hidden;flex-shrink:0">
          <div style="font-size:56px;font-weight:900;color:#f4c25f;line-height:1">${sc.totalPoints}</div>
          <div style="font-size:14px;color:rgba(255,255,255,0.7)">de ${sc.maxPoints} pontos</div>
          <div style="margin-top:12px;font-size:22px;font-weight:700;color:#fff">${currency(sc.estimatedPrize)}</div>
          <div style="font-size:12px;color:rgba(255,255,255,0.6)">premiação estimada</div>
        </div>
      </div>

      <div class="form-card">
        <div class="section-title"><h3>📊 Progresso da premiação</h3></div>
        <div style="margin-bottom:8px;font-size:13px;color:var(--muted)">${dica}</div>
        <div class="score-bar-track" style="height:20px;border-radius:10px;margin-bottom:8px">
          <div class="score-bar-fill good" style="width:${Math.min(prizeBarPct, 100)}%;height:20px;border-radius:10px;transition:width 0.5s;position:relative">
            ${sc.totalPoints >= 60 ? `<span style="position:absolute;right:8px;top:2px;font-size:11px;font-weight:700;color:#fff">${sc.totalPoints} pts</span>` : ""}
          </div>
        </div>
        <div style="display:flex;justify-content:space-between;font-size:11px;color:var(--muted);margin-bottom:16px">
          <span>0 (sem premiação)</span><span>60 (mín.)</span><span>100 (100%)</span><span>150 (150%) 🏆</span>
        </div>
        <div class="message" style="background:rgba(15,48,68,0.06);color:var(--text)">${nextMilestone}</div>
      </div>

      ${ug.unitName ? `
        <div class="form-card" style="border-left:4px solid ${ug.gateOk ? "var(--good)" : "var(--bad)"}">
          <div class="section-title">
            <h3>${ug.gateOk ? "🟢" : "🔴"} Gatilho da Unidade — ${escapeHtml(ug.unitName)}</h3>
            <div class="text-small">${ug.sellerOverrides ? "Dispensado — você está acima de 105% individual" : `Meta da unidade: ${ug.unitGoalPct}% de 95% necessários`}</div>
          </div>
          <div style="display:flex;gap:24px;flex-wrap:wrap;margin-top:8px">
            <div><div class="text-small">Realizado</div><strong>R$ ${currency(ug.unitActual)}</strong></div>
            <div><div class="text-small">Meta</div><strong>R$ ${currency(ug.unitGoal)}</strong></div>
            <div><div class="text-small">% Atingimento</div><strong style="color:${ug.gateOk ? "var(--good)" : "var(--bad)"}">${ug.unitGoalPct}%</strong></div>
          </div>
          <div style="margin-top:10px">
            <div class="score-bar-track">
              <div class="score-bar-fill ${ug.gateMet ? "good" : "bad"}" style="width:${Math.min(ug.unitGoalPct, 100)}%"></div>
              <div style="position:absolute;left:95%;top:0;bottom:0;width:2px;background:var(--accent);border-radius:2px" title="95% — gatilho"></div>
            </div>
            <div style="font-size:11px;color:var(--muted);margin-top:4px">Gatilho em 95% · Prêmio individual dispensado em 105%</div>
          </div>
        </div>
      ` : ""}

      <div class="form-card">
        <div class="section-title"><h3>🎯 Seus 9 indicadores</h3><div class="text-small">Clique em qualquer indicador pendente para saber o que fazer</div></div>
        <div class="stack" style="gap:12px">
          ${Object.entries(ind).map(([k, v]) => scoreIndicatorRow(k, v)).join("")}
        </div>
      </div>

      <div class="grid-2">
        <div class="form-card" style="background:linear-gradient(135deg,#fff9e6,#fffdf5)">
          <div class="section-title"><h3>⭐ Vendedor Destaque 2026</h3></div>
          <div class="text-small" style="margin-bottom:12px">Precisa de 900 pontos anuais acumulados. 1 vencedor por unidade.</div>
          <div style="font-size:28px;font-weight:900;color:#f4c25f">${sc.totalPoints} pts</div>
          <div class="text-small">este mês · meta anual: 900</div>
          <div style="margin-top:12px" class="message" style="background:rgba(244,194,95,0.15)">
            Se mantiver essa média, você acumula ~${sc.totalPoints * 12} pts no ano.
          </div>
        </div>
        <div class="form-card">
          <div class="section-title"><h3>📞 Ligações ativas</h3></div>
          <div style="font-size:36px;font-weight:900;color:${ind.calls.actual >= 60 ? "var(--good)" : "var(--accent)"}">${ind.calls.actual}</div>
          <div class="text-small">de 60 ligações registradas este mês</div>
          <div class="score-bar-track" style="margin-top:12px">
            <div class="score-bar-fill ${ind.calls.actual >= 60 ? "good" : "warn"}" style="width:${Math.min(Math.round((ind.calls.actual/60)*100),100)}%"></div>
          </div>
          <div class="text-small" style="margin-top:8px">
            ${ind.calls.actual >= 60 ? "✅ Meta batida! +10 pontos garantidos." : `Faltam ${60 - ind.calls.actual} ligações para +10 pontos.`}
          </div>
        </div>
      </div>
    </div>
  `;
}

// ─── FUNÇÕES RECONSTRUÍDAS (após limpeza de overrides) ───────────────────────

function topbarTitle() {
  if (roleIsSeller()) return { title: "Minha Agenda do Dia", description: "Execução comercial orientada à ação, com foco na sua carteira e nos seus retornos." };
  if (roleIsManager()) return { title: "Resumo da Unidade", description: "Visão rápida da unidade, da equipe e dos clientes em risco." };
  const map = {
    "executivo":      { title: "Visão Executiva",         description: "Panorama consolidado de resultados, metas e comparativos." },
    "vendedores":     { title: "Análise de Vendedores",   description: "Ranking, score e desempenho individual de vendedores." },
    "unidades":       { title: "Análise de Unidades",     description: "Comparativo de desempenho entre unidades." },
    "clientes":       { title: "Base de Clientes",        description: "Carteira ativa, inativos e métricas por cliente." },
    "cidades":        { title: "Cobertura Geográfica",    description: "Distribuição de vendas e clientes por cidade." },
    "descontos":      { title: "Política de Descontos",   description: "Análise de desconto médio por vendedor." },
    "calendario":     { title: "Calendário Comercial",    description: "Feriados, dias úteis e distribuição mensal." },
    "importacoes":    { title: "Importações",             description: "Gestão de arquivos, pacotes e auditoria de dados." },
    "administracao":  { title: "Administração",           description: "Pendências, cadastros e integridade dos dados." },
    "configuracoes":  { title: "Configurações",           description: "Usuários, metas, score e parâmetros operacionais." },
    "crm-agenda":     { title: "Missão do Dia",            description: "Sua fila de 5 contatos. 1 oferta + 1 pergunta por cliente." },
    "meu-placar":     { title: "Meu Placar",              description: "Seus pontos, indicadores e premiação estimada do mês." },
    "placar-equipe":  { title: "Placar da Equipe",        description: "Ranking de vendedores, zonas de premiação e alertas." },
    "crm-clientes":   { title: "Carteira CRM",            description: "Clientes ativos, riscos e oportunidades." },
    "crm-tarefas":    { title: "Tarefas CRM",             description: "Tarefas pendentes de follow-up e interação." },
    "crm-interacao":  { title: "Interação CRM",           description: "Registro de interações com clientes." },
  };
  return map[state.activeTab] || { title: "Dashboard", description: "Visão geral." };
}

function sidebarTabGroup(title, tabs) {
  if (!tabs.length) return "";
  const collapsed = state.ui.sidebarCollapsed;
  return `
    <div class="nav-section">
      ${!collapsed ? `<div class="nav-section-label">${escapeHtml(title)}</div>` : ""}
      ${tabs.map((tab) => `
        <button class="tab-button ${state.activeTab === tab.id ? "active" : ""} ${collapsed ? "tab-collapsed" : ""}"
          onclick="switchTab('${tab.id}')" title="${escapeHtml(tab.title)}">
          ${tab.icon ? `<span class="tab-icon">${tab.icon}</span>` : ""}
          ${!collapsed ? `<div class="tab-text">
            <span class="tab-title">${escapeHtml(tab.title)}</span>
            ${tab.desc ? `<span class="tab-desc">${escapeHtml(tab.desc)}</span>` : ""}
          </div>` : ""}
        </button>
      `).join("")}
    </div>
  `;
}

function toggleSidebar() {
  state.ui.sidebarCollapsed = !state.ui.sidebarCollapsed;
  requestRender();
}

function summaryDiffCard(label, data) {
  if (!data) return "";
  const prev = data.previousActual;
  const yoy = data.yearOverYearActual;
  return `
    <div class="kpi-card">
      <span>${escapeHtml(label)}</span>
      <strong>${currency(data.actual || 0)}</strong>
      <div class="kpi-foot">
        <span>Mês ant. ${prev ? currency(prev.actual || 0) : "-"}</span>
        <span>Ano ant. ${yoy ? currency(yoy.actual || 0) : "-"}</span>
      </div>
    </div>
  `;
}

function loadingBanner() {
  if (!state.ui.loading.filters && !state.ui.loading.dashboard) return "";
  return `<div class="message" style="background:rgba(15,48,68,0.07);color:var(--accent);font-weight:600">⏳ Atualizando dados…</div>`;
}

function executivoView() {
  if (!state.dashboard) return `<div class="loader panel">Carregando dashboard…</div>`;
  if (roleIsManager()) return managerExecutiveView();
  const s = state.dashboard.summary || {};
  const comp = state.dashboard.comparisons || {};
  const ranking = state.dashboard.sellerRanking || [];
  const units = state.dashboard.unitPerformance || [];
  return `
    <div class="stack">
      ${loadingBanner()}
      <div class="kpi-grid">
        ${kpiCard("Faturamento líquido", currency(s.revenueNet), "Meta", currency(s.revenueGoal))}
        ${kpiCard("% Atingimento", pct(s.goalAttainmentPct), "Projeção", pct(s.projectedGoalAttainmentPct))}
        ${kpiCard("Ticket médio", currency(s.ticketAverage), "Clientes", number(s.distinctClients))}
        ${kpiCard("Devolução", currency(s.returnsValue), "% Devolução", pct(s.returnRatioPct))}
        ${kpiCard("Desconto médio", pct(s.discountPct), "Mix SKU", number(s.mixSku))}
        ${kpiCard("Dias úteis", `${number(s.workingDaysElapsed)}/${number(s.workingDaysTotal)}`, "Meta diária", currency(s.dailyRevenueTarget))}
      </div>
      <div class="grid-2">
        ${summaryDiffCard("Receita líquida — comparativos", comp.group)}
        ${kpiCard("Vendedores ativos", number(ranking.length), "Unidades", number(units.length))}
      </div>
      ${executiveExpandSection("details", "Ver ranking de vendedores", `
        <div class="table-wrap">
          <table>
            <thead><tr><th>Vendedor</th><th>Unidade</th><th>Líquido</th><th>Meta</th><th>% Meta</th><th>% Proj.</th><th>Ticket</th><th>Clientes</th><th>Mix</th><th>Devolução</th><th>% Dev.</th><th>% Desc.</th><th>Score</th></tr></thead>
            <tbody>${sellerRows(ranking)}</tbody>
          </table>
        </div>
      `)}
      ${executiveExpandSection("units", "Ver performance por unidade", `
        <div class="table-wrap">
          <table>
            <thead><tr><th>Unidade</th><th>Líquido</th><th>Meta</th><th>% Meta</th><th>% Proj.</th><th>Devolução</th><th>% Dev.</th><th>Margem</th><th>Qtd. Peças</th><th>Ticket/Peça</th><th>Meta diária</th></tr></thead>
            <tbody>${unitRows(units)}</tbody>
          </table>
        </div>
      `)}
      ${executiveExpandSection("ranking", "Ver quadrante de vendedores", quadrantHtml(state.dashboard.quadrant))}
      ${executiveExpandSection("comparisons", "Ver comparativos de período", `
        <div class="kpi-grid">
          ${summaryDiffCard("Receita do grupo", comp.group)}
          ${(state.dashboard.unitPerformance || []).slice(0, 4).map((u) => kpiCard(escapeHtml(u.unitName), currency(u.revenueNet), "Meta", currency(u.revenueGoal))).join("")}
        </div>
      `)}
    </div>
  `;
}

function descontosView() {
  if (!state.dashboard) return `<div class="loader panel">Carregando descontos...</div>`;
  const rows = (state.dashboard.sellerRanking || []).slice().sort((a, b) => Number(b.discountPct || 0) - Number(a.discountPct || 0));
  return `
    <div class="stack">
      ${loadingBanner()}
      <div class="table-card">
      <div class="section-title">
        <div>
          <h3>Política de Descontos</h3>
          <div class="text-small">Desconto médio por vendedor, ordenado do maior para o menor.</div>
        </div>
      </div>
      <div class="table-wrap">
        <table>
          <thead>
            <tr><th>Vendedor</th><th>Unidade</th><th>% Desconto</th><th>Líquido</th><th>% Meta</th><th>Score</th></tr>
          </thead>
          <tbody>
            ${rows.map((row) => `
              <tr>
                <td>${escapeHtml(row.sellerName)}</td>
                <td>${escapeHtml(row.baseUnit || "-")}</td>
                <td>${pct(row.discountPct || 0)}</td>
                <td>${currency(row.revenueNet)}</td>
                <td>${pct(row.goalAttainmentPct)}</td>
                <td><span class="score-chip">${row.score}</span></td>
              </tr>
            `).join("")}
          </tbody>
        </table>
      </div>
    </div>
  `;
}

function dashboardView() {
  const sellerRole = roleIsSeller();
  const allowed = allowedTabsForUser(state.user);
  const { title, description } = topbarTitle();

  const crmTabs = [
    { id: "crm-agenda",    title: "Missão do Dia",    desc: "5 contatos prioritários", icon: "📅" },
    { id: "meu-placar",    title: "Meu Placar",       desc: "Pontos e premiação",       icon: "⭐" },
    { id: "placar-equipe", title: "Placar Equipe",    desc: "Ranking e alertas",        icon: "🏆" },
    { id: "crm-clientes",  title: "Carteira",         desc: "Clientes e status",        icon: "👥" },
    { id: "crm-tarefas",   title: "Tarefas",          desc: "Pendências de follow-up",  icon: "✅" },
  ].filter((t) => allowed.includes(t.id));

  const resultTabs = [
    { id: "executivo",  title: "Executivo",  desc: "Panorama e KPIs",          icon: "📊" },
    { id: "vendedores", title: "Vendedores", desc: "Ranking e score",           icon: "👤" },
    { id: "unidades",   title: "Unidades",   desc: "Comparativo",               icon: "🏢" },
    { id: "clientes",   title: "Clientes",   desc: "Carteira ativa",            icon: "🧑" },
    { id: "cidades",    title: "Cidades",    desc: "Cobertura geográfica",      icon: "🌍" },
    { id: "descontos",  title: "Descontos",  desc: "Política de desconto",      icon: "🏷" },
    { id: "calendario", title: "Calendário", desc: "Dias úteis e feriados",     icon: "📆" },
  ].filter((t) => allowed.includes(t.id));

  const opsTabs = [
    { id: "importacoes",   title: "Importações",    desc: "Arquivos e auditoria",    icon: "📥" },
    { id: "administracao", title: "Administração",  desc: "Pendências e cadastros",  icon: "⚙️" },
    { id: "configuracoes", title: "Configurações",  desc: "Usuários e metas",        icon: "🔧" },
  ].filter((t) => allowed.includes(t.id));

  const filtersLoading = Boolean(state.ui.loading.filters);
  const dis = filtersLoading ? "disabled" : "";
  const isCrmTab = state.activeTab.startsWith("crm-") || state.activeTab === "meu-placar" || state.activeTab === "placar-equipe";
  const filterBar = sellerRole || isCrmTab ? "" : `
    <div class="form-card" style="padding:12px 18px">
      <div style="display:flex;align-items:center;gap:10px;flex-wrap:wrap">
        <span style="font-size:12px;font-weight:700;color:var(--muted);white-space:nowrap">COMPETÊNCIA</span>
        <select onchange="state.filters.competenceStart = state.filters.competenceEnd = this.value" ${dis} style="flex:1;min-width:110px">
          ${(state.options.competences || []).map((c) => `<option value="${escapeHtml(c)}" ${state.filters.competenceEnd === c ? "selected" : ""}>${escapeHtml(c)}</option>`).join("")}
        </select>
        <span style="font-size:12px;font-weight:700;color:var(--muted);white-space:nowrap;margin-left:8px">UNIDADE</span>
        <select onchange="state.filters.unit = this.value" ${dis} style="flex:1;min-width:110px">
          <option value="">Todas</option>
          ${(state.options.units || []).map((u) => `<option value="${escapeHtml(u)}" ${state.filters.unit === u ? "selected" : ""}>${escapeHtml(u)}</option>`).join("")}
        </select>
        <span style="font-size:12px;font-weight:700;color:var(--muted);white-space:nowrap;margin-left:8px">VENDEDOR</span>
        <select onchange="state.filters.seller = this.value" ${dis} style="flex:1;min-width:130px">
          <option value="">Todos</option>
          ${(state.options.sellers || []).map((s) => `<option value="${escapeHtml(s)}" ${state.filters.seller === s ? "selected" : ""}>${escapeHtml(s)}</option>`).join("")}
        </select>
        <button class="btn btn-primary btn-sm" onclick="applyMainFilters()" ${dis} style="white-space:nowrap">
          ${filtersLoading ? "Buscando…" : "Aplicar"}
        </button>
        <button class="btn btn-ghost btn-sm" onclick="resetFilters()" ${dis}>Limpar</button>
      </div>
    </div>
  `;

  // Score resumido no sidebar para vendedor
  const sidebarScore = roleIsSeller() && state.sellerScore ? `
    <div style="padding:10px 12px;background:linear-gradient(135deg,#0f3044,#1a5276);border-radius:12px;margin-top:8px;cursor:pointer" onclick="switchTab('meu-placar')">
      <div style="font-size:10px;font-weight:800;color:#f4c25f;letter-spacing:0.08em">MEU PLACAR</div>
      <div style="display:flex;align-items:baseline;gap:6px;margin-top:4px">
        <span style="font-size:24px;font-weight:900;color:#fff">${state.sellerScore.totalPoints}</span>
        <span style="font-size:12px;color:rgba(255,255,255,0.6)">/ ${state.sellerScore.maxPoints} pts</span>
      </div>
      <div class="score-bar-track">
        <div class="score-bar-fill good" style="width:${Math.min(Math.round((state.sellerScore.totalPoints/100)*100),100)}%;height:6px"></div>
      </div>
      <div style="font-size:12px;color:#f4c25f;font-weight:700;margin-top:4px">R$ ${currency(state.sellerScore.estimatedPrize)}</div>
    </div>
  ` : "";

  return `
    <div class="shell">
      <div class="app-shell ${state.ui.sidebarCollapsed ? 'shell-collapsed' : ''}">
        <nav class="sidebar ${state.ui.sidebarCollapsed ? 'sidebar-collapsed' : ''}">
          <div>
            <div class="brand-pill ${state.ui.sidebarCollapsed ? 'brand-collapsed' : ''}">
              ${!state.ui.sidebarCollapsed ? '<span class="dot"></span>' : ''}
              ${!state.ui.sidebarCollapsed ? 'Passini Autopeças' : '<span class="dot"></span>'}
            </div>
            <button class="sidebar-toggle" onclick="toggleSidebar()" title="${state.ui.sidebarCollapsed ? 'Expandir menu' : 'Recolher menu'}">
              ${state.ui.sidebarCollapsed ? '▶' : '◀'}
            </button>
            ${sidebarTabGroup("CRM", crmTabs)}
            ${sidebarTabGroup("Resultados", resultTabs)}
            ${sidebarTabGroup("Operações", opsTabs)}
          </div>
          <div class="sidebar-footer">
            ${!state.ui.sidebarCollapsed ? sidebarScore : ""}
          </div>
        </nav>
        <div class="main">
          <div class="topbar">
            <div>
              <h2>${escapeHtml(title)}</h2>
              <p>${escapeHtml(description)}</p>
            </div>
            ${topbarActions()}
          </div>
          ${filterBar}
          ${messageHtml()}
          ${state.activeTab === "crm-agenda"    ? crmAgendaView()      : ""}
          ${state.activeTab === "meu-placar"    ? meuPlacarView()      : ""}
          ${state.activeTab === "placar-equipe" ? placardaEquipeView() : ""}
          ${state.activeTab === "crm-clientes"  ? crmClientsView()     : ""}
          ${state.activeTab === "crm-tarefas"   ? crmTasksView()       : ""}
          ${state.activeTab === "crm-interacao" ? crmInteractionView() : ""}
          ${state.activeTab === "executivo"     ? executivoView()      : ""}
          ${state.activeTab === "vendedores"    ? vendedoresView()     : ""}
          ${state.activeTab === "unidades"      ? unitsView()          : ""}
          ${state.activeTab === "clientes"      ? clientesView()       : ""}
          ${state.activeTab === "cidades"       ? cidadesView()        : ""}
          ${state.activeTab === "descontos"     ? descontosView()      : ""}
          ${state.activeTab === "calendario"    ? calendarView()       : ""}
          ${state.activeTab === "importacoes"   ? importacoesView()    : ""}
          ${state.activeTab === "administracao" ? administracaoView()  : ""}
          ${state.activeTab === "configuracoes" ? configuracoesView()  : ""}
        </div>
      </div>
      ${crmModalView()}
      ${clientDrawerView()}
    </div>
  `;
}

function render() {
  // Preserva scroll do drawer antes de reconstruir o DOM
  const drawerEl = document.querySelector(".client-drawer");
  const drawerScroll = drawerEl ? drawerEl.scrollTop : 0;
  app.innerHTML = state.user ? dashboardView() : loginView();
  if (drawerScroll > 0) {
    const newDrawer = document.querySelector(".client-drawer");
    if (newDrawer) newDrawer.scrollTop = drawerScroll;
  }
}

async function ignoreIssue(issueId) {
  try {
    await api("/api/admin/issues/resolve", { method: "POST", body: JSON.stringify({ issueId, action: "ignore" }) });
    addMessage("success", "Pendência ignorada.");
    await loadAdmin();
  } catch (error) {
    addMessage("error", error.message);
  }
}

async function resolveIssue(issueId, type) {
  let payload = { issueId, action: "resolve" };
  if (type === "seller") {
    const name = document.getElementById(`issue-person-name-${issueId}`)?.value?.trim();
    const role = document.getElementById(`issue-person-role-${issueId}`)?.value?.trim();
    const unit = document.getElementById(`issue-person-unit-${issueId}`)?.value?.trim();
    const validFrom = document.getElementById(`issue-valid-from-${issueId}`)?.value;
    if (!name || !unit) { addMessage("error", "Informe nome e unidade base."); return; }
    payload = { ...payload, person_name: name, role_classification: role || "vendedor", base_unit: unit, valid_from: validFrom };
  } else if (type === "city") {
    const city = document.getElementById(`issue-city-name-${issueId}`)?.value?.trim();
    const unit = document.getElementById(`issue-city-unit-${issueId}`)?.value?.trim();
    const validFrom = document.getElementById(`issue-city-valid-from-${issueId}`)?.value;
    if (!city || !unit) { addMessage("error", "Informe cidade e unidade principal."); return; }
    payload = { ...payload, city_name: city, principal_unit: unit, valid_from: validFrom };
  }
  try {
    await api("/api/admin/issues/resolve", { method: "POST", body: JSON.stringify(payload) });
    addMessage("success", "Pendência resolvida com sucesso.");
    await loadAdmin();
  } catch (error) {
    addMessage("error", error.message);
  }
}

async function saveVacation(event) {
  event.preventDefault();
  const name = document.getElementById("vac-name")?.value?.trim();
  const start = document.getElementById("vac-start")?.value;
  const end = document.getElementById("vac-end")?.value;
  const notes = document.getElementById("vac-notes")?.value?.trim();
  if (!name || !start || !end) { addMessage("error", "Nome, data inicial e data final são obrigatórios."); return; }
  const editingId = state.crm.editingVacation?.id;
  try {
    if (editingId) {
      await api("/api/admin/vacation/update", { method: "POST", body: JSON.stringify({ id: editingId, person_name: name, start_date: start, end_date: end, notes }) });
      addMessage("success", "Férias atualizadas.");
    } else {
      await api("/api/admin/vacation", { method: "POST", body: JSON.stringify({ person_name: name, start_date: start, end_date: end, notes }) });
      addMessage("success", "Férias salvas.");
    }
    cancelEditVacation();
    await loadAdmin();
  } catch (error) {
    addMessage("error", error.message);
  }
}

function editVacation(id) {
  const row = (state.admin.vacations || []).find((v) => v.id === id);
  if (!row) return;
  state.crm.editingVacation = { id: row.id, person_name: row.person_name || "", start_date: row.start_date || "", end_date: row.end_date || "", notes: row.notes || "" };
  state.crm.showVacationForm = true;
  requestRender();
  setTimeout(() => document.getElementById("vac-name")?.scrollIntoView({ behavior: "smooth", block: "center" }), 50);
}

function cancelEditVacation() {
  state.crm.editingVacation = null;
  state.crm.showVacationForm = false;
  requestRender();
}

async function deleteVacation(id, personName) {
  if (!confirm(`Excluir férias de "${personName}"?`)) return;
  try {
    await api("/api/admin/vacation/delete", { method: "POST", body: JSON.stringify({ id }) });
    addMessage("success", "Férias excluídas.");
    if (state.crm.editingVacation?.id === id) cancelEditVacation();
    await loadAdmin();
  } catch (error) {
    addMessage("error", error.message);
  }
}

function importDomConfig(scope) {
  const configs = {
    cost: { files: ["import-cost-unit-file", "import-cost-vendor-file"], competence: "import-cost-competence", action: null, feedback: "import-cost-feedback", importScope: "cost" },
    sales: { files: ["import-sales-file"], competence: "import-sales-competence", action: "import-sales-action", feedback: "import-sales-feedback", importScope: "sales" },
    crm: { files: ["import-crm-clients-file", "import-crm-summary-file"], competence: "import-crm-competence", action: null, feedback: "import-crm-feedback", importScope: "crm" },
  };
  return configs[scope] || null;
}

async function completeCrmTask(taskId) {
  try {
    await api("/api/crm/tasks/complete", { method: "POST", body: JSON.stringify({ taskId }) });
    addMessage("success", "Tarefa concluída.");
    await loadCrmData();
  } catch (error) {
    addMessage("error", error.message);
  }
}

function downloadFile(url) {
  const link = document.createElement("a");
  link.href = url;
  link.download = "";
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
}

async function previewImport(scope) {
  const cfg = importDomConfig(scope);
  if (!cfg) return;
  const feedbackEl = document.getElementById(cfg.feedback);
  if (feedbackEl) feedbackEl.textContent = "Analisando...";
  const form = new FormData();
  for (const fileId of cfg.files) {
    const fileEl = document.getElementById(fileId);
    if (fileEl?.files[0]) form.append(fileId, fileEl.files[0], fileEl.files[0].name);
  }
  const compEl = document.getElementById(cfg.competence);
  if (compEl?.value) form.set("competence", compEl.value.trim());
  if (cfg.action) {
    const actionEl = document.getElementById(cfg.action);
    if (actionEl?.value) form.set("importAction", actionEl.value);
  }
  form.set("importScope", cfg.importScope);
  try {
    const result = await api("/api/import/preview", { method: "POST", body: form });
    if (feedbackEl) {
      if (result.isValid) {
        feedbackEl.innerHTML = `<span style="color:var(--good)">✓ ${escapeHtml(result.message || "Arquivo válido para importação.")}</span>`;
      } else {
        feedbackEl.innerHTML = `<span style="color:var(--bad)">✗ ${escapeHtml(result.error || result.message || "Arquivo inválido.")}</span>`;
      }
    }
  } catch (error) {
    if (feedbackEl) feedbackEl.innerHTML = `<span style="color:var(--bad)">Erro: ${escapeHtml(error.message)}</span>`;
  }
}

async function submitImport(scope) {
  const cfg = importDomConfig(scope);
  if (!cfg) return;
  const feedbackEl = document.getElementById(cfg.feedback);
  if (feedbackEl) feedbackEl.textContent = "Importando...";
  const form = new FormData();
  for (const fileId of cfg.files) {
    const fileEl = document.getElementById(fileId);
    if (fileEl?.files[0]) form.append(fileId, fileEl.files[0], fileEl.files[0].name);
  }
  const compEl = document.getElementById(cfg.competence);
  const competence = compEl?.value?.trim() || "";
  if (!competence) { addMessage("error", "Informe a competência antes de importar."); if (feedbackEl) feedbackEl.textContent = ""; return; }
  form.set("competence", competence);
  if (cfg.action) {
    const actionEl = document.getElementById(cfg.action);
    if (actionEl?.value) form.set("importAction", actionEl.value);
  }
  form.set("importScope", cfg.importScope);
  try {
    const result = await api("/api/import/package", { method: "POST", body: form });
    const msg = result.message || "Importação concluída.";
    if (feedbackEl) feedbackEl.innerHTML = `<span style="color:var(--good)">✓ ${escapeHtml(msg)}</span>`;
    addMessage("success", msg);
    await loadDashboard();
  } catch (error) {
    if (feedbackEl) feedbackEl.innerHTML = `<span style="color:var(--bad)">✗ ${escapeHtml(error.message)}</span>`;
    addMessage("error", error.message);
  }
}

async function submitAdminImport() {
  const typeEl = document.getElementById("admin-import-type");
  const fileEl = document.getElementById("admin-import-file");
  if (!typeEl?.value || !fileEl?.files[0]) { addMessage("error", "Selecione o tipo e o arquivo CSV."); return; }
  const form = new FormData();
  form.append("file", fileEl.files[0], fileEl.files[0].name);
  try {
    const result = await api(`/api/admin/import/${typeEl.value}`, { method: "POST", body: form });
    addMessage("success", result.message || "Importação concluída.");
    await loadAdmin();
  } catch (error) {
    addMessage("error", error.message);
  }
}

window.addEventListener("resize", () => {
  const shouldCollapse = window.innerWidth <= 1280;
  if (state.ui.sidebarCollapsed !== shouldCollapse) {
    state.ui.sidebarCollapsed = shouldCollapse;
    requestRender();
  }
});
bootstrap();
