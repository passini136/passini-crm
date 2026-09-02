const state = {
  user: null,
  options: { competences: [], units: [], sellers: [], cities: [] },
  dashboard: null,
  admin: null,
  territories: null,   // mapa de bairro/cidade por unidade (Administração → Territórios)
  contacts: null,      // histórico de registros de contato
  inactives: null,     // clientes inativos da unidade, para reativação
  leads: null,         // base fria de empresas que ainda não são clientes
  leadFilters: { city: "", segment: "", search: "", withPhone: false, status: "", assignTo: "" },
  contactFilters: { start: "", end: "", seller: "", type: "", result: "", initiative: "",
                    search: "", portfolio: "", origin: "", limit: "300" },
  kpiThresholds: null,   // limites do farol
  content: null,          // biblioteca de vendas
  contentEditor: null,    // item em edição na biblioteca
  meetings: null,         // atas de reunião/treinamento + pendências de ciência
  meetingEditor: null,    // ata em edição (gestão)
  meetingDetail: null,    // ata aberta para leitura/ciência
  meetingFilters: { search: "", kind: "", from: "", to: "", mine: false },
  feedback: null,         // feedbacks + PDI + catálogo do MEC
  feedbackEditor: null,   // feedback em edição (gestão)
  feedbackDetail: null,   // feedback aberto para leitura/ciência
  pdiEditor: null,        // ponto de desenvolvimento em edição
  visits: null,           // visitas + pedidos
  visitRoute: null,        // roteiro sugerido por proximidade
  visitEditor: null,       // visita em registro
  visitFilters: { city: "", neighborhood: "", relationship: true },
  visitRequestEditor: null,  // pedido de visita a partir da ficha do cliente
  tasks: null,            // tarefas + filtros + contadores
  taskEditor: null,       // nova tarefa de direcionamento
  taskFilters: { status: "ABERTAS", seller: "", from: "", to: "", origin: "", search: "" },
  prospects: null,        // prospecção e fase da unidade
  prospectEditor: null,
  prospectFilters: { status: "", search: "", seller: "" },
  brands: null,
  sellerTargets: null,
  sellerTargetEdits: {},
  awards: null,
  awardFilters: null,
  awardEdits: {},
  brandFilters: { scope: "", dimension: "" },
  returns: null,
  returnFilters: { scope: "", dimension: "" },
  returnLoadingScope: null,
  prospectCadastro: null,  // dados prontos para pedir cadastro no WhatsApp
  sellerClients: null,     // relatório de clientes faturados por um vendedor
  brandOpen: {},   // marcas com o detalhe aberto
  brandLoadingScope: "",  // aba de marcas que está sendo carregada agora
  phaseEditor: null,           // fase da unidade (diretoria)
  activityGoalEditor: null,    // metas de atividade
  assistant: null,        // tutorial, FAQ e dicas
  helpEditor: null,       // dica/FAQ em edição (diretoria)
  noteEditor: null,       // registro pontual em edição
  feedbackFilters: { kind: "", competence: "", person: "" },
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
    // Marca que a unidade padrão do usuário já foi aplicada nesta sessão
    defaultUnitApplied: false,
    openScriptId: null,     // script expandido na ficha do cliente
    libraryCategory: "",    // categoria ativa na Biblioteca de Vendas
    tableSort: {},          // ordenação escolhida por tabela (cidades, clientes, vendedores...)
    clientRankingSearch: "", // busca por nome/código no ranking de clientes
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
      meetings: false,
      feedback: false,
      visits: false,
      visitRoute: false,
      prospects: false,
      territories: false,
      contacts: false,
      inactives: false,
      leads: false,
      brands: false,
      returns: false,
      awards: false,
    },
    visitOpenGroups: {},   // bairros abertos no roteiro
    bulkCities: new Set(), // cidades pendentes marcadas para resolver em lote
    bulkCityUnit: "",      // unidade escolhida para o lote
    analysisOpen: false,   // subgrupo Análises do menu aberto
    leadsOpen: false,      // painel da base fria de leads
    refreshing: {},        // botões de atualizar que estão rodando agora
    fichaAberta: null,     // null = decide sozinho; true/false = escolha da pessoa
    switching: {},         // troca de aba/filtro em andamento, por grupo de chips
    inactivesOpen: false,  // painel de inativos da unidade na Prospecção
    inactiveSearch: "",
    territoryCity: "",     // filtro de cidade na tela de territórios
    territoryDraft: null,  // linha em edição/criação no mapa de territórios
    personResults: null,   // resultados da busca de pessoa a vincular
    personSearching: false,
    personQuery: "",
    assistantOpen: false,
    assistantBubble: true,   // balão de chamada, some no primeiro clique
    assistantMenuOpen: false, // menu de presença do assistente (normal/discreto/oculto)
    assistantTab: "dicas",
    assistantAnswer: null,
    assistantSearching: false,
    tourOpen: false,
    tourStep: 0,
    tourManual: false,
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
    username: "",
    password: "",
  },
  userEditor: {
    id: "",
    username: "",
    fullName: "",
    linkedPersonName: "",
    linkedPersonSource: "",
    baseUnit: "",
    linkedUnits: [],
    role: "Administrador",
    profileId: "",
    password: "",
    isActive: true,
  },
  profileEditor: {
    id: "",
    name: "",
    description: "",
    modules: [],
    dataScope: "todos",
    canManageUsers: false,
    isSystem: false,
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
    agenda: { top5: [], extended: [], total: 0, rotation: null },
    clients: [],
    crmClientFilters: {
      status: "",
      purchaseMonth: "",
      growth: "",
      classCode: "",
      personType: "",
      creditLimit: "",   // COM_LIMITE | SEM_LIMITE | LIMITE_ESTOURADO
      search: "",
      itemCode: "",     // busca por peça comprada (código fabricante ou interno)
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
    missionUnit: "",   // filtro de unidade da Missão do Dia (diretor/admin)
    unassigned: null,  // clientes recorrentes sem vendedor
    copyFallback: null,  // modal de copia manual (HTTP sem clipboard API)
    assignTask: null,      // modal de cobrar contato (gestao)
    scheduleContact: null, // modal de agendar contato (vendedor, para si mesmo)
    reconcile: null,       // modal de conciliação por código (só "sem cadastro")
    support: null,         // modal de atendimento de cliente de outra carteira
    coverages: null,       // coberturas de carteira (férias, ausência)
    coverageOf: "",        // carteira coberta que o vendedor está enxergando agora
    coverageEditor: null,  // modal do gerente para autorizar cobertura
    receptive: null,       // modal de registro receptivo (não conta na meta)
    unassignedFilters: { minMonths: 2, window: 6 },
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
  // Ao COMEÇAR a carregar, repinta na hora. Sem isto o "Carregando" da tela só
  // apareceria depois da resposta — quando já não serve para nada, e a pessoa
  // conclui que o clique não funcionou. Desligar não força render: quem termina
  // já repinta com os dados novos.
  if (value && state.user) requestRender();
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

// O tipo de tela é decidido pelo ESCOPO DE DADOS do perfil, não pelo nome do
// papel. Assim perfis personalizados ("Supervisor", "Coordenador") herdam o
// comportamento correto sem precisar entrar numa lista fixa.
function roleIsSeller() {
  if (state.user?.dataScope) return state.user.dataScope === "proprio";
  return state.user?.role === "Vendedor";
}

function roleIsManager() {
  if (state.user?.dataScope) {
    return ["unidade", "unidade_consolidado"].includes(state.user.dataScope);
  }
  return state.user?.role === "Gerente";
}

function roleIsAdminLike() {
  if (state.user?.dataScope) return state.user.dataScope !== "proprio";
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
  if (section === "territorios" && !state.territories && !state.ui.loading.territories) {
    void loadTerritories();
  }
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
  const allowed = allowedTabsForUser(user);
  // Primeira aba disponível seguindo a preferência natural de cada perfil
  const preference = user?.dataScope === "proprio"
    ? ["crm-agenda", "crm-clientes", "executivo"]
    : ["executivo", "crm-agenda", "crm-clientes", "acessos"];
  return preference.find((tab) => allowed.includes(tab)) || allowed[0] || "executivo";
}

// Telas da campanha de premiação — seguem PLACAR_ENABLED, não o score
const PLACAR_TABS = ["placar-equipe"];

function allowedTabsForUser(user) {
  if (!user) return ["executivo"];
  const withoutScore = (tabs) => (placarEnabled() ? tabs : tabs.filter((t) => !PLACAR_TABS.includes(t)));
  // Fonte de verdade: os módulos do perfil de acesso (configurável pela tela).
  if (Array.isArray(user.modules) && user.modules.length) return withoutScore(user.modules);
  // Fallback para instalações antigas, antes dos perfis existirem
  if (user.role === "Vendedor") {
    return withoutScore(["crm-agenda", "crm-clientes", "crm-tarefas", "visitas", "prospeccao", "contatos", "reunioes", "feedback", "calendario"]);
  }
  return withoutScore(["crm-agenda", "placar-equipe", "crm-clientes", "crm-tarefas", "visitas", "prospeccao", "contatos", "reunioes", "feedback", "executivo", "vendedores", "unidades", "clientes", "cidades", "descontos", "calendario", "importacoes", "administracao", "configuracoes", "acessos"]);
}

function userCanManageUsers() {
  return Boolean(state.user?.canManageUsers);
}

/**
 * SCORE = índice ponderado 0–100 exibido como chip nas tabelas e cards de vendedor
 * (meta, ticket, clientes, mix, devolução com pesos configuráveis).
 * Desativado por decisão de negócio em 31/07/2026.
 */
const SCORE_ENABLED = false;

/**
 * PLACAR = campanha de premiação por pontos (meta, margem, itens, positivação,
 * devolução, ligações) com prêmio estimado em R$. É independente do score acima
 * e continua ATIVO — é o programa de incentivo da equipe.
 */
const PLACAR_ENABLED = true;

function placarEnabled() {
  return PLACAR_ENABLED;
}

/**
 * Selo de status do vendedor (Destaque / Boa rota / Acompanhar / Intervir).
 * Em standby junto com o score na primeira versão. Quando reativado, aparece
 * para todos os perfis MENOS o vendedor — é uma leitura de gestão, não do vendedor.
 */
const SELLER_STATUS_ENABLED = false;

function scoreEnabled() {
  return SCORE_ENABLED;
}

function showSellerStatus() {
  return SELLER_STATUS_ENABLED && !roleIsSeller();
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
  return state.teamScore;
}

async function loadTeamActivity() {
  try {
    // Diretor/Admin podem escolher a unidade; gerente é limitado no backend
    const qs = state.crm.missionUnit ? `?unit=${encodeURIComponent(state.crm.missionUnit)}` : "";
    state.crm.teamActivity = await api(`/api/crm/team-activity-today${qs}`);
  } catch (err) {
    state.crm.teamActivity = { error: err.message, sellers: [], totalContactsToday: 0, teamGoal: 0 };
  }
  requestRender();
}

function setMissionUnit(unit) {
  state.crm.missionUnit = unit || "";
  loadTeamActivity();
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
  return state.crm.portfolioSummary;
}

async function bootstrap() {
  const session = await api("/api/session");
  if (session.authenticated) {
    state.user = session.user;
    state.activeTab = defaultTabForUser(state.user);
    // Antes de qualquer carga: quem tem unidade vinculada abre já filtrado nela
    applyDefaultUnitForUser();
    // Cargas essenciais em paralelo (options não bloqueia mais o restante)
    const loads = [loadOptions(), loadDashboard(), loadCrmOptions(), loadCrmData()];
    if (session.user.role === "Vendedor" && placarEnabled()) loads.push(loadSellerScore());
    // Em background: alimenta o contador de ciência pendente no menu sem
    // atrasar a abertura do sistema.
    loadMeetings(true);
    loadFeedback(true);
    loadVisits(true);
    loadProspects(true);
    // Assistente e tutorial: carregam por último e abrem sozinhos só na
    // primeira entrada daquele perfil.
    loadAssistant(true).then(() => {
      if (state.assistant && !state.assistant.tourSeen && (state.assistant.tour || []).length) {
        abrirTour(false);
      }
      requestRender();
    });
    await Promise.all(loads);
    // O resumo da carteira vale para os dois perfis: o vendedor vê a própria
    // linha (o servidor recorta), o gestor vê a equipe.
    loadPortfolioSummary();
    loadCoverages();
    if (state.user.role !== "Vendedor") {
      // Cargas pesadas em background — nenhuma bloqueia a UI
      loadAdmin();
      if (placarEnabled()) loadTeamScore();
      loadTeamActivity();
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
  applyDefaultUnitForUser();
  syncUserEditorOptions();
}

/**
 * Ao entrar, quem tem unidades vinculadas abre o dashboard já na própria unidade.
 * Depois pode trocar livremente (inclusive para "Todas", se o perfil permitir).
 * Roda só uma vez por sessão para não desfazer a escolha do usuário.
 */
function applyDefaultUnitForUser() {
  if (state.ui.defaultUnitApplied) return;
  const units = state.user?.linkedUnits || [];
  if (!units.length) { state.ui.defaultUnitApplied = true; return; }
  // Prefere uma unidade que exista na lista de opções, se ela já tiver carregado
  const available = state.options?.units || [];
  const preferred = (available.length && units.find((u) => available.includes(u))) || units[0];
  if (preferred) state.filters.unit = preferred;
  state.ui.defaultUnitApplied = true;
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
    // Guarda o payload inteiro: a tela de Tarefas depende dos contadores,
    // da lista de pessoas e dos catálogos que vêm junto.
    state.tasks = tasks;
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
  if (filters.itemCode) query.set("itemCode", filters.itemCode);
  if (filters.creditLimit) query.set("creditLimit", filters.creditLimit);
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
    creditLimit: "",
    search: "",
    itemCode: "",
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

/** "2026-07" → "jul/26". Cabeçalho de planilha não comporta "2026-07". */
function competenceLabel(competencia) {
  const partes = String(competencia || "").split("-");
  if (partes.length < 2) return String(competencia || "");
  const mes = MONTH_ABBR[Number(partes[1]) - 1] || partes[1];
  return `${mes}/${partes[0].slice(2)}`;
}

/** Valor curto para caber no cabeçalho: R$ 1,2 mi / R$ 345,6 mil. */
function shortMoneyHeader(valor) {
  const n = Number(valor || 0);
  if (Math.abs(n) >= 1e6) return `R$ ${(n / 1e6).toLocaleString("pt-BR", { maximumFractionDigits: 1 })} mi`;
  if (Math.abs(n) >= 1e3) return `R$ ${(n / 1e3).toLocaleString("pt-BR", { maximumFractionDigits: 1 })} mil`;
  return currency(n);
}

/** Subindo / estável / caindo — mesma leitura do indicador da tela. */
function tendenciaCliente(atual, media) {
  const a = Number(atual || 0);
  const m = Number(media || 0);
  if (!m) return a > 0 ? "Novo/retomando" : "Sem base";
  const variacao = (a - m) / m;
  if (variacao >= 0.1) return "Subindo";
  if (variacao <= -0.1) return "Caindo";
  return "Estável";
}

/** Carrega a biblioteca de planilha sob demanda (é pesada, não vem no boot). */
async function garantirXLSX() {
  if (window.XLSX) return;
  await new Promise((resolve, reject) => {
    const s = document.createElement("script");
    s.src = "https://cdnjs.cloudflare.com/ajax/libs/xlsx/0.18.5/xlsx.full.min.js";
    s.onload = resolve;
    s.onerror = reject;
    document.head.appendChild(s);
  });
}

/** Gera e baixa uma planilha simples a partir de cabeçalhos + linhas. */
async function baixarPlanilha(nomeArquivo, aba, headers, linhas) {
  await garantirXLSX();
  const ws = XLSX.utils.aoa_to_sheet([headers, ...linhas]);
  ws["!cols"] = headers.map((h) => ({ wch: Math.min(Math.max(String(h).length + 4, 12), 46) }));
  ws["!autofilter"] = { ref: XLSX.utils.encode_range({
    s: { r: 0, c: 0 }, e: { r: linhas.length, c: headers.length - 1 } }) };
  ws["!freeze"] = { xSplit: 0, ySplit: 1 };
  const wb = XLSX.utils.book_new();
  XLSX.utils.book_append_sheet(wb, ws, aba);
  XLSX.writeFile(wb, `${nomeArquivo}_${new Date().toISOString().slice(0, 10)}.xlsx`);
}

/** Exporta a lista Sem Vendedor inteira — a tela mostra só os 200 maiores. */
/** PJ, PF ou nada. Sem documento não dá para afirmar — e chutar aqui é pior
 *  que omitir: o gestor usa isso para decidir a quem atribuir o cliente. */
function seloPessoa(tipo) {
  if (tipo === "PJ") return '<span class="status-tag" style="background:#e8f0fe;color:#1a5276">PJ</span>';
  if (tipo === "PF") return '<span class="status-tag" style="background:#fef7e0;color:#b06000">PF</span>';
  return '<span class="status-tag" style="background:#f1f3f4;color:#5f6368" title="Sem CNPJ ou CPF no cadastro">—</span>';
}

async function exportUnassignedXLSX() {
  try {
    addMessage("info", "Gerando planilha…");
    const c = state.crm.unassigned?.criteria || {};
    const q = new URLSearchParams({ export: "1" });
    if (c.minMonths) q.set("minMonths", String(c.minMonths));
    if (c.monthsWindow) q.set("window", String(c.monthsWindow));
    const data = await api(`/api/crm/unassigned?${q.toString()}`);
    const linhas = (data.items || []).map((i) => [
      i.clientName, i.personType || "", i.cityName || "", i.unitName || "", i.months,
      Number(i.revenue || 0), Number(i.avgMonthly || 0),
      (i.lastPurchaseAt || "").slice(0, 10),
      i.clientKey || "sem cadastro",
      (i.sellers || []).map((s) => `${s.sellerName} (${s.months}m)`).join(" · "),
    ]);
    if (!linhas.length) { addMessage("warn", "Nada para exportar."); return; }
    await baixarPlanilha("clientes_sem_vendedor", "Sem vendedor",
      ["Cliente", "Tipo", "Cidade", "Unidade", "Meses com compra", "Faturamento", "Média/mês",
       "Última compra", "Código no CRM", "Quem atendeu"], linhas);
    addMessage("success", `Planilha exportada — ${linhas.length} de ${number(data.total)} cliente(s).`);
  } catch (e) {
    addMessage("error", "Erro ao exportar: " + (e.message || e));
  }
}

/** Exporta o histórico de contatos do período filtrado. */
async function exportContatosXLSX() {
  try {
    addMessage("info", "Gerando planilha…");
    const f = state.contactFilters;
    const q = new URLSearchParams({ export: "1", limit: "20000" });
    Object.entries(f).forEach(([k, v]) => { if (v && k !== "limit") q.set(k, v); });
    const data = await api(`/api/crm/contacts?${q.toString()}`);
    const gerente = Boolean(data.isManagerView);
    const linhas = (data.items || []).map((i) => [
      (i.occurred_at || "").replace("T", " ").slice(0, 16),
      i.client_name || i.client_key,
      ...(gerente ? [i.seller_name || "", i.portfolioSeller || "", i.crossPortfolio ? "Sim" : "Não"] : []),
      i.type_label || i.contact_type_code,
      i.originLabel || "",
      i.initiative === "RECEPTIVO" ? "Receptivo" : (i.initiative === "APOIO" ? "Apoio" : "Ativo"),
      i.result_label || i.result_code,
      i.notes || "",
      (i.followup_due_at || "").slice(0, 10),
    ]);
    if (!linhas.length) { addMessage("warn", "Nenhum registro no período."); return; }
    await baixarPlanilha("contatos", "Contatos",
      ["Quando", "Cliente",
       ...(gerente ? ["Vendedor do contato", "Carteira", "Contato cruzado"] : []),
       "Tipo", "Origem", "Iniciativa", "Resultado", "Observação", "Retorno"], linhas);
    addMessage("success", `Planilha exportada — ${linhas.length} registro(s).`);
  } catch (e) {
    addMessage("error", "Erro ao exportar: " + (e.message || e));
  }
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
    if (filters.itemCode) query.set("itemCode", filters.itemCode);
    if (filters.creditLimit) query.set("creditLimit", filters.creditLimit);
    query.set("page", "1");
    query.set("pageSize", "20000");
    // export=1 libera o teto de 100 linhas da tela. Sem isso a planilha saía
    // com a primeira página apenas — 100 clientes de 190, sem nenhum aviso.
    query.set("export", "1");
    const data = await api(`/api/crm/clients?${query.toString()}`);
    const rows = data.rows || [];
    if (!rows.length) { addMessage("warn", "Nenhum cliente encontrado para exportar."); return; }
    if (data.total > rows.length) {
      addMessage("warn", `A planilha traz ${rows.length} de ${data.total} clientes — o limite de `
        + `exportação foi atingido. Estreite o filtro para levar o resto.`);
    }

    if (!window.XLSX) {
      await new Promise((resolve, reject) => {
        const s = document.createElement("script");
        s.src = "https://cdnjs.cloudflare.com/ajax/libs/xlsx/0.18.5/xlsx.full.min.js";
        s.onload = resolve;
        s.onerror = reject;
        document.head.appendChild(s);
      });
    }

    // Competências vêm da memória de cálculo da média, que é a mesma base que a
    // tela usa. Assim o cabeçalho nunca fica fora de sincronia com os valores.
    const base = rows.find((r) => r.averageBasis?.months?.length)?.averageBasis;
    const meses = base?.months?.map((m) => m.competence) || ["", "", ""];
    const mesAtual = base?.currentCompetence || "";

    // Somas de cada coluna, para o total ir no próprio cabeçalho.
    const soma = (fn) => rows.reduce((acc, r) => acc + Number(fn(r) || 0), 0);
    const totalAtual = soma((r) => r.currentRevenue);
    const totalM1 = soma((r) => r.trimesterRevenue1);
    const totalM2 = soma((r) => r.trimesterRevenue2);
    const totalM3 = soma((r) => r.trimesterRevenue3);
    const totalTri = totalM1 + totalM2 + totalM3;

    const headers = [
      "Código", "Cliente", "Unidade", "Vendedor", "Cidade", "Bairro",
      "PJ/PF", "Status", "Classe", "Telefone", "Contato principal",
      `${competenceLabel(mesAtual)} (atual) · ${shortMoneyHeader(totalAtual)}`,
      `${competenceLabel(meses[0])} · ${shortMoneyHeader(totalM1)}`,
      `${competenceLabel(meses[1])} · ${shortMoneyHeader(totalM2)}`,
      `${competenceLabel(meses[2])} · ${shortMoneyHeader(totalM3)}`,
      `Trimestre · ${shortMoneyHeader(totalTri)}`,
      "Média trim. (R$)", "Tendência",
      // Saldo previsto = limite − compra do mês. NÃO é o saldo real: parcela de
      // mês anterior ainda em aberto não entra. O nome da coluna carrega o aviso.
      "Limite de crédito", "Saldo previsto (limite − mês)",
      "Última compra", "Dias sem compra", "Último contato", "Motivo principal",
    ];

    const sheetData = [
      headers,
      ...rows.map((r) => {
        const m1 = Number(r.trimesterRevenue1 || 0);
        const m2 = Number(r.trimesterRevenue2 || 0);
        const m3 = Number(r.trimesterRevenue3 || 0);
        return [
          r.clientKey || "",
          r.clientName || "",
          r.unitName || "",
          r.assignedSeller || "",
          r.cityName || "",
          r.neighborhood || "",
          r.personType || "",
          r.statusCode || "",
          r.classCode || "",
          r.updatedPhone || r.phone || "",
          r.primaryContactName || "",
          Number(r.currentRevenue || 0),
          m1, m2, m3,
          Number((m1 + m2 + m3).toFixed(2)),
          Number(r.averageRevenue || 0),
          tendenciaCliente(r.currentRevenue, r.averageRevenue),
          Number(r.creditLimit || 0),
          Number(r.predictedBalance || 0),
          r.lastPurchaseAt ? r.lastPurchaseAt.slice(0, 10) : "",
          r.daysWithoutPurchase != null ? Number(r.daysWithoutPurchase) : "",
          r.lastInteractionAt ? String(r.lastInteractionAt).slice(0, 10) : "",
          r.primaryReason || "",
        ];
      }),
    ];

    const ws = XLSX.utils.aoa_to_sheet(sheetData);

    // Formato de moeda nas colunas de valor. Sem isso o Excel mostra 1234.5 e
    // quem abre a planilha perde tempo formatando antes de conseguir ler.
    const colunasValor = [11, 12, 13, 14, 15, 16];
    const totalLinhas = sheetData.length;
    colunasValor.forEach((c) => {
      for (let l = 1; l < totalLinhas; l++) {
        const celula = ws[XLSX.utils.encode_cell({ r: l, c })];
        if (celula && typeof celula.v === "number") celula.z = '#,##0.00';
      }
    });

    ws["!cols"] = [
      { wch: 10 }, { wch: 38 }, { wch: 14 }, { wch: 28 }, { wch: 18 }, { wch: 20 },
      { wch: 7 }, { wch: 12 }, { wch: 10 }, { wch: 16 }, { wch: 22 },
      { wch: 20 }, { wch: 18 }, { wch: 18 }, { wch: 18 }, { wch: 20 },
      { wch: 16 }, { wch: 14 }, { wch: 13 }, { wch: 14 }, { wch: 14 }, { wch: 34 },
    ];
    ws["!freeze"] = { xSplit: 2, ySplit: 1 };
    ws["!autofilter"] = { ref: XLSX.utils.encode_range({
      s: { r: 0, c: 0 }, e: { r: totalLinhas - 1, c: headers.length - 1 } }) };

    const wb = XLSX.utils.book_new();
    XLSX.utils.book_append_sheet(wb, ws, "Clientes");
    XLSX.writeFile(wb, `clientes_${new Date().toISOString().slice(0, 10)}.xlsx`);
    addMessage("success",
      `Planilha exportada — ${rows.length} clientes · trimestre ${currency(totalTri)}.`);
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

async function loadTerritories() {
  setLoading("territories", true);
  try {
    state.territories = await api("/api/admin/territories");
  } catch (error) {
    addMessage("error", error.message);
  } finally {
    setLoading("territories", false);
  }
  requestRender();
}

function novoTerritorio(cidade, bairro) {
  state.ui.territoryDraft = {
    id: "",
    cityName: cidade || "",
    neighborhood: bairro || "",
    unitName: "",
    validFrom: state.territories?.defaultValidFrom || "2026-09-01",
    notes: "",
  };
  requestRender();
}

function editarTerritorio(id) {
  const item = (state.territories?.territories || []).find((t) => Number(t.id) === Number(id));
  if (!item) return;
  state.ui.territoryDraft = {
    id: item.id,
    cityName: item.city_name,
    neighborhood: item.neighborhood === "*" ? "" : item.neighborhood,
    unitName: item.unit_name,
    validFrom: item.valid_from,
    notes: item.notes || "",
  };
  requestRender();
}

function fecharTerritorio() {
  state.ui.territoryDraft = null;
  requestRender();
}

async function salvarTerritorio() {
  const d = state.ui.territoryDraft;
  if (!d) return;
  if (!d.cityName.trim()) { addMessage("error", "Informe a cidade."); return; }
  if (!d.unitName) { addMessage("error", "Escolha a unidade."); return; }
  try {
    const r = await api("/api/admin/territories/save", { method: "POST", body: JSON.stringify(d) });
    addMessage("success", r.message || "Território salvo.");
    state.ui.territoryDraft = null;
    state.territories = null;
    await loadTerritories();
  } catch (error) {
    addMessage("error", error.message);
  }
}

async function excluirTerritorio(id) {
  if (!window.confirm("Remover este território? A cidade volta a valer pela regra antiga.")) return;
  try {
    const r = await api("/api/admin/territories/delete", { method: "POST", body: JSON.stringify({ id }) });
    addMessage("success", r.message || "Território removido.");
    state.territories = null;
    await loadTerritories();
  } catch (error) {
    addMessage("error", error.message);
  }
}

function setTerritoryCity(cidade) {
  state.ui.territoryCity = cidade;
  requestRender();
}

async function loadAutoImportStatus() {
  try {
    state.autoImport = await api("/api/auto-import/status");
  } catch (e) {
    state.autoImport = { error: e.message, logs: [], folders: [] };
  }
  requestRender();
  return state.autoImport;
}

async function runAutoImportNow() {
  const btn = document.getElementById("btn-auto-import-run");
  if (btn) { btn.disabled = true; btn.textContent = "⏳ Importando…"; }
  addMessage("info", "Verificando pastas e importando arquivos pendentes…");
  try {
    const result = await api("/api/auto-import/run", { method: "POST" });
    addMessage("success", result.message || "Importação executada.");
    (result.warnings || []).forEach((w) => addMessage("error", w));
    await loadAutoImportStatus();
    await Promise.all([loadDashboard(), loadCrmData()]);
    addMessage("success", "Dados do dashboard atualizados.");
  } catch (e) {
    addMessage("error", `Falha ao importar: ${e.message}`);
  } finally {
    if (btn) { btn.disabled = false; btn.textContent = "▶ Importar agora"; }
  }
}

/**
 * Chave para casar a mesma pessoa entre as fontes.
 * O faturamento traz o sufixo do setor — "FULANO (VENDAS)", "FULANO (TELEVENDAS)" —
 * e o cadastro manual frequentemente não traz. Sem remover o sufixo, a mesma
 * pessoa aparece duas vezes na lista.
 */
function personMatchKey(name) {
  return String(name || "")
    .replace(/\([^)]*\)/g, " ")   // remove (VENDAS), (TELEVENDAS)...
    .replace(/\s+/g, " ")
    .trim()
    .toUpperCase();
}

/**
 * Pessoas do cadastro indexadas pela chave de casamento, sem duplicar.
 * Quando há mais de um registro para a mesma pessoa (vigências diferentes),
 * vence o que tem unidade preenchida.
 */
function peopleByMatchKey() {
  const map = new Map();
  (state.admin?.people || [])
    .filter((person) => !person.valid_to)
    .forEach((person) => {
      const key = personMatchKey(person.person_name);
      if (!key) return;
      const atual = map.get(key);
      if (!atual || (!atual.base_unit && person.base_unit)) {
        map.set(key, {
          person_name: person.person_name,
          base_unit: person.base_unit || "",
          role_classification: person.role_classification || "",
        });
      }
    });
  return map;
}

/**
 * Lista para os seletores (metas, férias, usuários).
 * Inclui quem está no cadastro E quem só aparece emitindo venda, mas nunca
 * repete a mesma pessoa. O nome exibido prioriza o que vem do faturamento,
 * porque é por ele que metas e férias são vinculadas.
 */
function sellerPeopleOptions({ onlySellers = false } = {}) {
  const cadastro = peopleByMatchKey();
  const resultado = new Map();

  // 1) Nomes que aparecem no faturamento — são a referência para vínculo
  (state.admin?.salesSellers || []).forEach((name) => {
    if (!name) return;
    const key = personMatchKey(name);
    if (!key) return;
    const info = cadastro.get(key);
    resultado.set(key, {
      person_name: name,
      base_unit: info?.base_unit || "",
      role_classification: info?.role_classification || "",
      inSales: true,
    });
  });

  // 2) Vendedor interno/externo do CADASTRO DE CLIENTES.
  //    É a única fonte que enxerga quem ainda não vendeu: vendedor recém-
  //    contratado e gerente não aparecem no faturamento, mas estão no cadastro
  //    desde o primeiro dia. Sem isso eles ficavam de fora do vínculo.
  (state.admin?.clientSellers || []).forEach((name) => {
    if (!name) return;
    const key = personMatchKey(name);
    if (!key || resultado.has(key)) return;
    const info = cadastro.get(key);
    resultado.set(key, {
      person_name: name,
      base_unit: info?.base_unit || "",
      role_classification: info?.role_classification || "",
      inSales: false,
      fromClients: true,
    });
  });

  // 3) Cadastrados que ainda não emitiram venda
  cadastro.forEach((info, key) => {
    if (!resultado.has(key)) {
      resultado.set(key, { ...info, inSales: false });
    }
  });

  let lista = [...resultado.values()];
  if (onlySellers) {
    lista = lista.filter((p) => p.role_classification === "Vendedor");
  }
  return lista.sort((a, b) =>
    String(a.person_name || "").localeCompare(String(b.person_name || ""), "pt-BR"));
}

/** Pessoas que emitem venda mas ainda não foram classificadas no cadastro. */
function unclassifiedSellers() {
  return sellerPeopleOptions().filter((p) => p.inSales && !p.role_classification);
}

/** Unidades que podem ser marcadas no cadastro do usuário.
 *
 * Não dá para depender só de `state.options.units`: essa lista vem dos filtros
 * do dashboard e chega vazia quando o usuário entra direto em Acessos. Vazia,
 * a tela mostrava o título "Unidades vinculadas" sem nenhuma caixa para marcar
 * — parecia que a opção tinha sumido. Aqui a lista é reconstruída também a
 * partir do que já está gravado nos usuários e no cadastro de pessoas.
 */
function unitOptionsForEditor() {
  // `state.admin.units` vem da própria tela de Acessos e é a fonte principal;
  // as demais são reforço para o caso de a tela abrir antes do carregamento.
  const nomes = new Set([...(state.admin?.units || []), ...(state.options.units || [])]);
  (state.admin?.users || []).forEach((u) => (u.linked_units || []).forEach((x) => x && nomes.add(x)));
  (state.admin?.people || []).forEach((p) => p.base_unit && nomes.add(p.base_unit));
  (state.userEditor?.linkedUnits || []).forEach((x) => x && nomes.add(x));
  return [...nomes].sort((a, b) => String(a).localeCompare(String(b), "pt-BR"));
}

function syncUserEditorOptions() {
  // O vínculo com a pessoa NÃO é mais apagado aqui. Ele era descartado quando o
  // nome não estava na lista de vendedores — e agora ele pode vir da base de
  // clientes PF, que nunca esteve nessa lista. O efeito era apagar em silêncio
  // o vínculo de um gerente só por abrir a tela de edição dele.
  const disponiveis = unitOptionsForEditor();
  state.userEditor.linkedUnits = (state.userEditor.linkedUnits || [])
    .filter((unit) => !disponiveis.length || disponiveis.includes(unit));
  // Quem decide se há unidades é o ESCOPO do perfil, não o nome dele. Testar
  // pelo nome ("Gerente", "Analista") zerava as unidades de qualquer perfil
  // personalizado com escopo por unidade — e o salvamento então reclamava de
  // um campo que a própria tela tinha acabado de limpar.
  if (!["unidade", "unidade_consolidado"].includes(selectedUserProfileScope())) {
    state.userEditor.linkedUnits = [];
  }
  state.ui.personResults = null;
  state.ui.personQuery = "";
}

function resetUserEditor() {
  state.userEditor = {
    id: "",
    username: "",
    fullName: "",
    linkedPersonName: "",
    linkedPersonSource: "",
    baseUnit: "",
    linkedUnits: [],
    role: "Administrador",
    profileId: "",
    password: "",
    isActive: true,
  };
}

function resetProfileEditor() {
  state.profileEditor = {
    id: "",
    name: "",
    description: "",
    modules: [],
    dataScope: "todos",
    canManageUsers: false,
    isSystem: false,
  };
}

function accessProfiles() {
  return state.admin?.profiles || [];
}

function accessProfileById(id) {
  return accessProfiles().find((p) => String(p.id) === String(id)) || null;
}

/** Escopo do perfil escolhido no editor de usuário — define quais campos aparecem. */
function selectedUserProfileScope() {
  const profile = accessProfileById(state.userEditor.profileId);
  return profile ? profile.dataScope : "todos";
}

function editUser(userId) {
  const user = (state.admin?.users || []).find((item) => Number(item.id) === Number(userId));
  if (!user) return;
  // Perfil pelo id gravado; se o usuário é antigo, casa pelo nome do papel
  const profile = accessProfileById(user.profile_id)
    || accessProfiles().find((p) => p.name === user.role)
    || null;
  state.userEditor = {
    id: user.id,
    username: user.username || "",
    fullName: user.full_name || "",
    linkedPersonName: user.linked_person_name || "",
    linkedPersonSource: user.linked_person_name ? "vínculo já gravado" : "",
    baseUnit: user.person_unit || "",
    linkedUnits: [...(user.linked_units || [])],
    role: user.role || "Administrador",
    profileId: profile ? profile.id : "",
    password: "",
    isActive: Boolean(user.is_active),
  };
  syncUserEditorOptions();
  state.ui.personResults = null;
  state.ui.personQuery = "";
  requestRender();
  document.getElementById("user-editor-card")?.scrollIntoView({ behavior: "smooth", block: "center" });
}

function setUserProfile(profileId) {
  const profile = accessProfileById(profileId);
  state.userEditor.profileId = profileId;
  state.userEditor.role = profile ? profile.name : "";
  const scope = profile ? profile.dataScope : "todos";
  // O vínculo vale para qualquer perfil: é ele que liga o gerente ao nome do
  // cadastro na lista de presença das atas. Antes era apagado ao trocar de
  // perfil e o gerente ficava sem vínculo, sem opção de corrigir na tela.
  if (!["unidade", "unidade_consolidado"].includes(scope)) state.userEditor.linkedUnits = [];
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
    state.ui.defaultUnitApplied = false;
    applyDefaultUnitForUser();
    const loginLoads = [loadOptions(), loadDashboard(), loadCrmOptions(), loadCrmData()];
    if (result.user.role === "Vendedor" && placarEnabled()) loginLoads.push(loadSellerScore());
    await Promise.all(loginLoads);
    loadPortfolioSummary();
    loadCoverages();
    if (state.user.role !== "Vendedor") {
      loadAdmin();
      if (placarEnabled()) loadTeamScore();
      loadTeamActivity();
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
  state.filters.unit = "";
  state.ui.defaultUnitApplied = false;  // próximo login volta a abrir na unidade do usuário
  requestRender();
}

function messageHtml() {
  if (!state.messages.length) return "";
  // Fixo no topo e acima da camada dos modais. Antes ficava no fluxo da página,
  // isto é: atrás de qualquer janela aberta.
  return `
    <div class="toast-stack">
      ${state.messages
        .map((item) => `<div class="message ${item.type}">${escapeHtml(item.text)}</div>`)
        .join("")}
    </div>
  `;
}

/**
 * Tela de entrada.
 *
 * Duas metades: a marca à esquerda, o acesso à direita. O lado da marca traz o
 * ciclo do MEC girando — abrir, preparar, fazer, registrar, marcar, concluir.
 * Quem entra no sistema lê o método antes de digitar a senha; em três segundos
 * de espera, o hábito é reforçado sem custo nenhum.
 */
// ─── Assistente ─────────────────────────────────────────────────────────────
//
// Personagem, painel e tutorial. A caixa de perguntas busca na base de
// conhecimento — não é conversa com IA, e a tela diz isso. Prometer chat e
// entregar busca destrói a confiança na primeira pergunta.

/**
 * Mecânico da Passini, em SVG com volume.
 *
 * A primeira versão parecia policial: boné de aba reta somado a macacão escuro
 * fechado dá farda. Aqui os sinais são de oficina — boné virado para trás,
 * macacão grafite com gola aberta, zíper, crachá no peito e mancha de graxa no
 * rosto. O índigo da marca ficou nos detalhes (boné, gola, crachá) em vez de
 * cobrir o corpo inteiro.
 *
 * A sensação de 3D vem de degradês radiais com luz vindo de cima à esquerda,
 * sombra própria embaixo do queixo e do boné, e brilho especular nos olhos e no
 * metal. Vetor continua sendo a escolha certa: nítido de 32 a 200 px, sem peso
 * de arquivo e com a animação embutida.
 */
function assistantAvatar(tamanho, animar) {
  const id = `av${Math.random().toString(36).slice(2, 8)}`;
  const anima = (attr, valores, dur, extra) => animar
    ? `<animate attributeName="${attr}" values="${valores}" dur="${dur}" repeatCount="indefinite" ${extra || ""} />`
    : "";

  return `
    <svg viewBox="0 0 120 120" width="${tamanho}" height="${tamanho}"
         xmlns="http://www.w3.org/2000/svg" role="img" aria-label="Assistente Passini">
      <defs>
        <radialGradient id="${id}pele" cx="38%" cy="30%" r="78%">
          <stop offset="0%"   stop-color="#ffd9b3" />
          <stop offset="55%"  stop-color="#f0b98a" />
          <stop offset="100%" stop-color="#c98b5e" />
        </radialGradient>
        <linearGradient id="${id}macacao" x1="0.2" y1="0" x2="0.85" y2="1">
          <stop offset="0%"   stop-color="#5b6474" />
          <stop offset="45%"  stop-color="#3f4756" />
          <stop offset="100%" stop-color="#262c38" />
        </linearGradient>
        <linearGradient id="${id}gola" x1="0" y1="0" x2="0" y2="1">
          <stop offset="0%" stop-color="#4a2fb5" /><stop offset="100%" stop-color="#2a1a6e" />
        </linearGradient>
        <radialGradient id="${id}bone" cx="34%" cy="22%" r="80%">
          <stop offset="0%"   stop-color="#5f3ed6" />
          <stop offset="60%"  stop-color="#3b2582" />
          <stop offset="100%" stop-color="#221551" />
        </radialGradient>
        <linearGradient id="${id}metal" x1="0" y1="0" x2="1" y2="1">
          <stop offset="0%"   stop-color="#f2f4f8" />
          <stop offset="45%"  stop-color="#b9c0cc" />
          <stop offset="100%" stop-color="#79818f" />
        </linearGradient>
        <radialGradient id="${id}piso" cx="50%" cy="50%" r="50%">
          <stop offset="0%" stop-color="#000" stop-opacity="0.28" />
          <stop offset="100%" stop-color="#000" stop-opacity="0" />
        </radialGradient>
      </defs>

      <ellipse cx="60" cy="110" rx="34" ry="6" fill="url(#${id}piso)" />

      <g>
        ${anima("transform", "translate(0 0); translate(0 -1.8); translate(0 0)", "3.8s", 'type="translate" attributeType="XML"')}

        <path d="M28 108 C28 84 40 74 60 74 C80 74 92 84 92 108 Z" fill="url(#${id}macacao)" />
        <path d="M28 108 C28 92 34 82 44 77 L44 108 Z" fill="#fff" opacity="0.07" />

        <path d="M49 74 L60 90 L71 74 L64 71 L60 78 L56 71 Z" fill="url(#${id}gola)" />
        <rect x="58.4" y="86" width="3.2" height="22" rx="1.6" fill="#1b2029" />
        <g stroke="#8a93a3" stroke-width="0.9" opacity="0.75">
          <line x1="58.4" y1="90" x2="61.6" y2="90" /><line x1="58.4" y1="94" x2="61.6" y2="94" />
          <line x1="58.4" y1="98" x2="61.6" y2="98" /><line x1="58.4" y1="102" x2="61.6" y2="102" />
        </g>

        <g transform="translate(72 89)">
          <rect x="0" y="0" width="18" height="12" rx="3" fill="#2e3542" stroke="#79818f" stroke-width="0.8" />
          <rect x="2.5" y="3" width="13" height="2" rx="1" fill="#f4c25f" />
          <rect x="2.5" y="7" width="9" height="1.6" rx="0.8" fill="#aeb6c4" />
        </g>
        <rect x="34" y="90" width="12" height="9" rx="2.5" fill="#333b49" stroke="#5b6474" stroke-width="0.8" />

        <path d="M52 64 h16 v10 h-16 z" fill="#d9a071" />
        <ellipse cx="60" cy="70" rx="9" ry="4" fill="#000" opacity="0.16" />

        <ellipse cx="60" cy="46" rx="24" ry="25.5" fill="url(#${id}pele)" />
        <ellipse cx="36.5" cy="49" rx="4" ry="5.5" fill="#e8ab7c" />
        <ellipse cx="83.5" cy="49" rx="4" ry="5.5" fill="#e8ab7c" />
        <path d="M37.5 41 q-1.6 5 -0.6 9.5 q3 -4.6 3 -9.2 z" fill="#4a3728" />
        <path d="M82.5 41 q1.6 5 0.6 9.5 q-3 -4.6 -3 -9.2 z" fill="#4a3728" />

        <path d="M35 36 C35 21 46 14 60 14 C74 14 85 21 85 36 C74 31 46 31 35 36 Z" fill="url(#${id}bone)" />
        <path d="M40 32 C43 23 50 18 59 17.4 C50 20 44 25 40 32 Z" fill="#fff" opacity="0.13" />
        <path d="M84 32.5 C93 31.5 100 34.5 101 38.5 C101.6 41 98.5 42.6 93.5 42 C90.5 38.5 87 34.8 84 32.5 Z"
              fill="#2a1a6e" stroke="#1a1040" stroke-width="0.8" />
        <path d="M86 34 C92 34 97 36 98.6 38.4 C95 36.4 90.5 35 86 34 Z" fill="#fff" opacity="0.12" />
        <circle cx="60" cy="16.5" r="2.6" fill="#f4c25f" />
        <path d="M35 35 h50 v4.5 a2.2 2.2 0 0 1 -2.2 2.2 h-45.6 a2.2 2.2 0 0 1 -2.2 -2.2 z" fill="#1d1250" />
        <path d="M31 40 C31 30 37 22 45 19 C40 25 37 32 37 40 Z" fill="#000" opacity="0.10" />

        <g>
          <ellipse cx="50" cy="48" rx="4.6" ry="5" fill="#fff" />
          <ellipse cx="70" cy="48" rx="4.6" ry="5" fill="#fff" />
          <circle cx="50.8" cy="48.6" r="2.5" fill="#3b2a20" />
          <circle cx="70.8" cy="48.6" r="2.5" fill="#3b2a20" />
          <circle cx="49.7" cy="47.4" r="1" fill="#fff" />
          <circle cx="69.7" cy="47.4" r="1" fill="#fff" />
          ${animar ? `<animateTransform attributeName="transform" type="scale" additive="sum"
             values="1 1; 1 0.08; 1 1" dur="5.2s" begin="1.6s" repeatCount="indefinite"
             keyTimes="0;0.03;0.06" />` : ""}
        </g>
        <path d="M44.5 40.5 q5.5 -2.6 11 -0.4" stroke="#4a3728" stroke-width="2.2" fill="none" stroke-linecap="round" />
        <path d="M64.5 40.1 q5.5 -2.2 11 0.4" stroke="#4a3728" stroke-width="2.2" fill="none" stroke-linecap="round" />

        <path d="M58.6 52 q1.4 3.4 -1 4.6" stroke="#c98b5e" stroke-width="1.8" fill="none" stroke-linecap="round" />
        <path d="M51 61.5 q9 6.6 18 0" stroke="#8c5a37" stroke-width="2.6" fill="none" stroke-linecap="round" />
        <path d="M53.5 62.6 q6.5 4 13 0 q-6.5 1.6 -13 0 z" fill="#fff" opacity="0.85" />

        <g fill="#3f4048" opacity="0.72">
          <ellipse cx="75.5" cy="57.5" rx="6.2" ry="3.2" transform="rotate(-18 75.5 57.5)" />
          <ellipse cx="80.5" cy="52.8" rx="3.1" ry="1.8" transform="rotate(-18 80.5 52.8)" />
          <circle cx="71" cy="61.5" r="1.3" />
          <circle cx="83.5" cy="49.5" r="0.9" />
        </g>
        <ellipse cx="43.5" cy="55" rx="4.4" ry="2.8" fill="#e8825f" opacity="0.30" />
        <ellipse cx="76.5" cy="55" rx="4.4" ry="2.8" fill="#e8825f" opacity="0.22" />
      </g>

      <g transform="rotate(-28 92 94)">
        ${anima("transform", "rotate(0 92 94); rotate(-12 92 94); rotate(0 92 94)", "3.2s", 'type="rotate" attributeType="XML" additive="sum"')}
        <rect x="88.6" y="66" width="6.8" height="28" rx="3.2"
              fill="url(#${id}metal)" stroke="#5e6572" stroke-width="1.1" />
        <rect x="90" y="68" width="1.8" height="23" rx="0.9" fill="#fff" opacity="0.5" />
        <path d="M84.4 62 a7.6 7.6 0 0 1 4.2 -6.9 l0 6.2 l6.8 0 l0 -6.2 a7.6 7.6 0 1 1 -11 6.9 z"
              fill="url(#${id}metal)" stroke="#5e6572" stroke-width="1.1" />
        <ellipse cx="92" cy="94" rx="6" ry="4.4" fill="#e8ab7c" stroke="#c98b5e" stroke-width="0.8" />
        <path d="M86.4 93 q5.6 -3 11.2 0 q-5.6 2.6 -11.2 0 z" fill="#c98b5e" />
      </g>
    </svg>`;
}
async function loadAssistant(silencioso) {
  try {
    state.assistant = await api("/api/help");
  } catch (e) {
    state.assistant = { error: e.message, faq: [], tips: [] };
  }
  if (!silencioso) requestRender();
}

function toggleAssistant() {
  state.ui.assistantOpen = !state.ui.assistantOpen;
  state.ui.assistantBubble = false;
  if (state.ui.assistantOpen && !state.assistant) loadAssistant();
  requestRender();
}

function setAssistantTab(aba) { state.ui.assistantTab = aba; requestRender(); }

async function perguntarAssistente() {
  const campo = document.getElementById("as-question");
  const pergunta = campo ? campo.value.trim() : "";
  if (pergunta.length < 3) { addMessage("warn", "Escreva a pergunta com pelo menos 3 letras."); return; }
  state.ui.assistantSearching = true; requestRender();
  try {
    const r = await api("/api/help/ask", { method: "POST", body: JSON.stringify({ question: pergunta }) });
    state.ui.assistantAnswer = r;
    state.ui.assistantTab = "faq";
  } catch (e) {
    addMessage("error", e.message);
  } finally {
    state.ui.assistantSearching = false;
    requestRender();
  }
}

function limparRespostaAssistente() {
  state.ui.assistantAnswer = null;
  const campo = document.getElementById("as-question");
  if (campo) campo.value = "";
  requestRender();
}

// ─── Prospecção e unidade em implantação ────────────────────────────────────
//
// Prospect é oficina que ainda não existe no cadastro do Alfa. O contato dele
// usa a MESMA tabela de interações dos clientes, com a chave "P-<id>": conta no
// placar, gera tarefa de retorno e, quando o CNPJ for cadastrado, todo o
// histórico migra para a ficha do cliente em vez de se perder.

async function loadProspects(silencioso) {
  const f = state.prospectFilters;
  const q = new URLSearchParams();
  if (f.status) q.set("status", f.status);
  if (f.search) q.set("q", f.search);
  if (f.seller) q.set("seller", f.seller);
  if (!silencioso) {
    state.ui.loading.prospects = true;
    requestRender();   // pinta o "carregando" ANTES de ir à rede
  }
  try {
    state.prospects = await api(`/api/prospects?${q.toString()}`);
  } catch (e) {
    state.prospects = { error: e.message, prospects: [], funnel: {}, statuses: [] };
  } finally {
    state.ui.loading.prospects = false;
    requestRender();
  }
}

function setProspectStatus(status) {
  const novo = state.prospectFilters.status === status ? "" : status;
  state.prospectFilters.status = novo;
  trocarChip("prospectStatus", novo, () => loadProspects());
}

function applyProspectSearch() {
  // Lê do campo; se ele acabou de ser recriado por uma repintura, o estado
  // guarda o que foi digitado.
  const campo = document.getElementById("prospect-search");
  state.prospectFilters.search = (campo ? campo.value : state.prospectFilters.search || "").trim();
  loadProspects();
}

/** Escolher o vendedor traz a unidade dele junto — unidade errada tira o
 *  prospect da vista da equipe que deveria trabalhá-lo. */
function escolherVendedorProspect(nome) {
  if (!state.prospectEditor) return;
  state.prospectEditor.sellerName = nome;
  const unidade = (state.prospects?.sellerUnits || {})[nome];
  if (unidade) state.prospectEditor.unitName = unidade;
  requestRender();
}

function novoProspect() {
  const p = state.prospects || {};
  state.prospectEditor = {
    id: null, companyName: "", tradeName: "", documentNumber: "", phone: "",
    contactName: "", email: "", cityName: "", neighborhood: "", addressLine: "",
    origin: "", serviceType: "", carsWeek: "", mainLine: "", payment: "",
    closingTrigger: "", notes: "",
    // Campos da ficha cadastral — nascem vazios e são preenchidos pelo
    // comprovante da Receita ou à mão.
    stateRegistration: "", addressNumber: "", addressComplement: "", postalCode: "",
    stateName: "", landline: "", emailFinance: "", emailXml: "", paymentTerms: "",
    businessLine: "", buyers: ["", "", ""], cnaeCode: "", openedAt: "", registryStatus: "",
    unitName: p.unitName || "", sellerName: p.canManage ? "" : (p.myName || ""),
    saving: false, importando: false,
  };
  requestRender();
}

function editarProspect(p) {
  state.prospectEditor = { ...p, saving: false };
  requestRender();
}

function fecharProspectEditor() {
  state.prospectEditor = null;
  // A próxima oficina decide sozinha se abre a ficha; a escolha vale só para
  // o cadastro que estava aberto.
  state.ui.fichaAberta = null;
  requestRender();
}

/** Erro do formulário: aparece DENTRO da janela, onde a pessoa está olhando. */
function erroNoProspect(mensagem) {
  if (state.prospectEditor) state.prospectEditor.error = mensagem;
  requestRender();
}

/** Mesma regra do servidor, adiantada na tela para não gastar ida e volta. */
function validarProspect(p) {
  if (!String(p.companyName || "").trim()) return "Informe a razão social da oficina.";
  if (!String(p.sellerName || "").trim()) {
    return "Escolha o vendedor responsável — é ele que trabalha este prospect.";
  }
  if (p.id) return "";   // editar não exige os dados de cadastro
  const faltando = [
    ["CNPJ", p.documentNumber], ["telefone", p.phone], ["e-mail", p.email],
  ].filter(([, v]) => !String(v || "").trim()).map(([r]) => r);
  if (faltando.length) {
    return "Para abrir o cadastro faltam: " + faltando.join(", ") +
           ". São os dados que o setor de cadastro pede.";
  }
  const doc = String(p.documentNumber).replace(/\D/g, "");
  if (doc.length !== 14 && doc.length !== 11) {
    return `CNPJ/CPF com ${doc.length} dígito(s). Confira: CNPJ tem 14 e CPF tem 11.`;
  }
  const mail = String(p.email).trim();
  if (!mail.includes("@") || !mail.split("@").pop().includes(".")) {
    return `E-mail "${mail}" não parece válido.`;
  }
  return "";
}

async function salvarProspect() {
  const p = state.prospectEditor;
  if (!p) return;
  const problema = validarProspect(p);
  if (problema) { erroNoProspect(problema); return; }
  p.error = "";
  p.saving = true; requestRender();
  try {
    const r = await api("/api/prospects/save", { method: "POST", body: JSON.stringify(p) });
    if (r.duplicated) {
      addMessage("warn", r.message || "Este CNPJ já está cadastrado como prospect.");
    } else if (r.converted) {
      addMessage("success",
        `Oficina já existe no cadastro como ${r.clientName}. Vinculada — ela já está na carteira.`);
    } else {
      addMessage("success", "Oficina registrada.");
    }
    // Guarda os dados ANTES de limpar o editor: é deles que sai o texto do
    // pedido de cadastro. Só para cadastro novo — editar não gera pedido.
    const dados = p.id ? null : { ...p, id: r.prospectId };
    state.prospectEditor = null;
    if (dados && !r.duplicated) state.prospectCadastro = dados;
    // Deixa a oficina recém-criada NA FRENTE: sem isto ela cai no meio de uma
    // lista longa e a pessoa não a encontra para imprimir a ficha.
    if (!p.id && !r.duplicated) {
      state.prospectFilters.search = (p.companyName || "").trim();
      state.prospectFilters.status = "";
    }
    await loadProspects(true);
  } catch (e) {
    // O erro vem do servidor: mostra dentro da janela, não atrás dela.
    if (state.prospectEditor) state.prospectEditor.saving = false;
    erroNoProspect(e.message);
  }
}

async function excluirProspect(prospectId) {
  if (!confirm("Excluir este prospect? O histórico de contatos dele também some.")) return;
  try {
    await api("/api/prospects/delete", { method: "POST", body: JSON.stringify({ prospectId }) });
    await loadProspects(true);
  } catch (e) { addMessage("error", e.message); }
}

async function marcarProspectPerdido(prospectId) {
  const motivo = prompt("Por que este prospect foi perdido?");
  if (motivo === null) return;
  try {
    await api("/api/prospects/lost", { method: "POST", body: JSON.stringify({ prospectId, reason: motivo }) });
    addMessage("success", "Prospect marcado como perdido.");
    await loadProspects(true);
  } catch (e) { addMessage("error", e.message); }
}

async function reconciliarProspects() {
  try {
    const r = await api("/api/prospects/reconcile", { method: "POST", body: "{}" });
    addMessage("success", r.linked
      ? `${r.linked} prospect(s) viraram cliente e o histórico foi migrado.`
      : "Nenhum prospect novo encontrado no cadastro.");
    await loadProspects(true);
  } catch (e) { addMessage("error", e.message); }
}

/** Registrar contato em prospect reaproveita o formulário de interação. */
function contatarProspect(p) {
  state.crm.interactionForm = {
    clientKey: p.clientKey,
    clientCode: p.clientKey,
    clientName: p.companyName,
    unitName: p.unitName || "",
    updatedPhone: p.phone || "",
    primaryContactName: p.contactName || "",
    contactNotes: "",
    contactTypeCode: "LIGACAO",
    resultCode: "FALOU_CLIENTE",
    occurredAt: localDateTimeInput(),
    notes: "",
    questionUsed: "",
    hadProgress: false,
    offerTitle: "",
    nextAction: "Qualificar com as 4 perguntas e fechar com um gatilho",
    followupDueAt: "",
    requestVisit: false, visitReason: "",
    isProspect: true,
  };
  state.activeTab = "crm-interacao";
  requestRender();
}

function prospectStatusCfg(status) {
  return (state.prospects?.statuses || []).find((s) => s.id === status)
    || { label: status, icon: "•", color: "#5f6368", bg: "#f1f3f4" };
}

function prospectStatusBadge(status) {
  const c = prospectStatusCfg(status);
  return `<span class="status-tag" style="background:${c.bg};color:${c.color}">${c.icon} ${escapeHtml(c.label)}</span>`;
}

// ─── Configuração da fase e das metas de atividade ──────────────────────────
//
// Fica dentro da própria tela de Prospecção, e não em Configurações, porque é
// aqui que a decisão faz sentido: quem abre esta tela está olhando a unidade
// nova. Só aparece para quem pode gerenciar usuários.

function abrirConfigFase(unidade) {
  const d = state.prospects || {};
  const atual = (d.phases || []).find((p) => p.unitName === unidade) || {};
  state.phaseEditor = {
    unitName: unidade || d.unitName || "",
    phase: atual.phase || "IMPLANTACAO",
    openingDate: atual.openingDate || "",
    goalExemptUntil: atual.goalExemptUntil || "",
    notes: atual.notes || "",
    saving: false,
  };
  requestRender();
}

function fecharConfigFase() { state.phaseEditor = null; requestRender(); }

async function salvarConfigFase() {
  const f = state.phaseEditor;
  if (!f) return;
  if (!f.unitName) { addMessage("error", "Selecione a unidade."); return; }
  f.saving = true; requestRender();
  try {
    await api("/api/prospects/phase", { method: "POST", body: JSON.stringify(f) });
    addMessage("success", f.phase === "IMPLANTACAO"
      ? `${f.unitName} marcada como em implantação.`
      : `${f.unitName} voltou para operação normal.`);
    state.phaseEditor = null;
    await loadProspects(true);
    loadDashboard();
  } catch (e) {
    addMessage("error", e.message);
    if (state.phaseEditor) state.phaseEditor.saving = false;
    requestRender();
  }
}

function abrirMetasAtividade() {
  const d = state.prospects || {};
  const atuais = {};
  (d.activity || []).forEach((a) => { atuais[a.id] = a.target || ""; });
  state.activityGoalEditor = {
    competence: d.competence || "",
    unitName: d.unitName || (d.units || [])[0] || "",
    sellerName: "",
    targets: atuais,
    saving: false,
  };
  requestRender();
}

function fecharMetasAtividade() { state.activityGoalEditor = null; requestRender(); }

async function salvarMetasAtividade() {
  const g = state.activityGoalEditor;
  if (!g) return;
  if (!g.unitName || !g.competence) { addMessage("error", "Informe unidade e competência."); return; }
  g.saving = true; requestRender();
  try {
    // Uma chamada por indicador: o backend guarda cada meta separadamente,
    // o que permite meta de unidade e meta individual convivendo.
    const metricas = (state.prospects?.metrics || []).map((m) => m.id);
    for (const metric of metricas) {
      await api("/api/prospects/activity-goal", {
        method: "POST",
        body: JSON.stringify({
          competence: g.competence, unitName: g.unitName,
          sellerName: g.sellerName || "", metric,
          target: Number(g.targets[metric] || 0),
        }),
      });
    }
    addMessage("success", "Metas de atividade salvas.");
    state.activityGoalEditor = null;
    await loadProspects(true);
  } catch (e) {
    addMessage("error", e.message);
    if (state.activityGoalEditor) state.activityGoalEditor.saving = false;
    requestRender();
  }
}

function configFaseModal() {
  const f = state.phaseEditor;
  if (!f) return "";
  const d = state.prospects || {};
  const unidades = (state.options.units || []).length ? state.options.units : (d.units || []);
  const competencias = state.options.competences || [];
  return `
    <div class="client-drawer-overlay open modal-dim" onclick="fecharConfigFase()">
      <div class="panel modal-panel" style="max-width:600px;margin:8vh auto;padding:22px" onclick="event.stopPropagation()">
        <div class="section-title">
          <div><h3>🚧 Fase da unidade</h3>
            <div class="text-small">Define se a unidade é cobrada por meta de faturamento.</div></div>
          <button class="btn btn-ghost btn-sm" onclick="fecharConfigFase()">Fechar</button>
        </div>

        <div class="field" style="margin-top:12px"><label>Unidade</label>
          <select onchange="abrirConfigFase(this.value)">
            <option value="">Selecione…</option>
            ${unidades.map((u) => `<option value="${escapeHtml(u)}" ${f.unitName === u ? "selected" : ""}>${escapeHtml(u)}</option>`).join("")}
          </select></div>

        <div class="field"><label>Situação</label>
          <select onchange="state.phaseEditor.phase=this.value;requestRender()">
            <option value="IMPLANTACAO" ${f.phase === "IMPLANTACAO" ? "selected" : ""}>Em implantação — sem meta de faturamento</option>
            <option value="OPERACAO" ${f.phase === "OPERACAO" ? "selected" : ""}>Operação normal — com meta</option>
          </select></div>

        <div style="display:grid;grid-template-columns:1fr 1fr;gap:10px">
          <div class="field"><label>Data de inauguração</label>
            <input type="date" value="${escapeHtml(f.openingDate)}"
              oninput="state.phaseEditor.openingDate=this.value" /></div>
          <div class="field"><label>Isenta de meta até</label>
            <select onchange="state.phaseEditor.goalExemptUntil=this.value">
              <option value="">Não usar</option>
              ${competencias.map((c) => `<option value="${escapeHtml(c)}" ${f.goalExemptUntil === c ? "selected" : ""}>${escapeHtml(c)}</option>`).join("")}
              ${["2026-08","2026-09","2026-10","2026-11","2026-12"].filter((c) => !competencias.includes(c))
                .map((c) => `<option value="${escapeHtml(c)}" ${f.goalExemptUntil === c ? "selected" : ""}>${escapeHtml(c)}</option>`).join("")}
            </select></div>
        </div>
        <div class="text-small" style="color:var(--muted);margin-top:-4px">
          A isenção continua valendo depois da inauguração. Para a Zona Norte: inaugura em agosto,
          isenta até <strong>2026-12</strong>, e a meta entra em 2027.
        </div>

        <div class="field" style="margin-top:8px"><label>Observação</label>
          <input value="${escapeHtml(f.notes)}" oninput="state.phaseEditor.notes=this.value"
            placeholder="Ex.: inaugura 24/08, meta formal só em 2027" /></div>

        <div class="actions" style="margin-top:14px">
          <button class="btn btn-primary" ${f.saving ? "disabled" : ""} onclick="salvarConfigFase()">
            ${f.saving ? "Salvando…" : "Salvar"}</button>
          <button class="btn btn-ghost" onclick="fecharConfigFase()">Cancelar</button>
        </div>
      </div>
    </div>`;
}

function metasAtividadeModal() {
  const g = state.activityGoalEditor;
  if (!g) return "";
  const d = state.prospects || {};
  const unidades = (state.options.units || []).length ? state.options.units : (d.units || []);
  const competencias = state.options.competences || [];
  return `
    <div class="client-drawer-overlay open modal-dim" onclick="fecharMetasAtividade()">
      <div class="panel modal-panel" style="max-width:620px;margin:7vh auto;padding:22px" onclick="event.stopPropagation()">
        <div class="section-title">
          <div><h3>🎯 Metas de atividade</h3>
            <div class="text-small">O alvo de quem ainda não tem meta de faturamento.</div></div>
          <button class="btn btn-ghost btn-sm" onclick="fecharMetasAtividade()">Fechar</button>
        </div>

        <div style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:10px;margin-top:12px">
          <div class="field"><label>Competência</label>
            <select onchange="state.activityGoalEditor.competence=this.value">
              ${competencias.map((c) => `<option value="${escapeHtml(c)}" ${g.competence === c ? "selected" : ""}>${escapeHtml(c)}</option>`).join("")}
            </select></div>
          <div class="field"><label>Unidade</label>
            <select onchange="state.activityGoalEditor.unitName=this.value">
              ${unidades.map((u) => `<option value="${escapeHtml(u)}" ${g.unitName === u ? "selected" : ""}>${escapeHtml(u)}</option>`).join("")}
            </select></div>
          <div class="field"><label>Vendedor</label>
            <select onchange="state.activityGoalEditor.sellerName=this.value">
              <option value="">Meta da unidade</option>
              ${(d.sellers || []).map((s) => `<option value="${escapeHtml(s)}" ${g.sellerName === s ? "selected" : ""}>${escapeHtml(s)}</option>`).join("")}
            </select></div>
        </div>
        <div class="text-small" style="color:var(--muted);margin-top:-4px">
          Deixe em "Meta da unidade" para valer para a equipe toda, ou escolha um vendedor
          para definir o alvo individual dele.
        </div>

        <div class="subtle-card padded-card" style="margin-top:12px">
          ${(d.metrics || []).map((m) => `
            <div style="display:flex;justify-content:space-between;align-items:center;gap:12px;
                        padding:8px 0;border-bottom:1px solid var(--line)">
              <div style="flex:1">
                <div style="font-weight:700;font-size:13px">${m.icon} ${escapeHtml(m.label)}</div>
                <div class="text-small" style="color:var(--muted)">${escapeHtml(m.hint)}</div>
              </div>
              <input type="number" min="0" style="width:110px" value="${escapeHtml(String(g.targets[m.id] ?? ""))}"
                oninput="state.activityGoalEditor.targets['${m.id}']=this.value" placeholder="0" />
            </div>`).join("")}
        </div>
        <div class="text-small" style="color:var(--muted);margin-top:6px">
          Deixe em 0 o que não quiser acompanhar — indicador sem meta não aparece no painel.
        </div>

        <div class="actions" style="margin-top:14px">
          <button class="btn btn-primary" ${g.saving ? "disabled" : ""} onclick="salvarMetasAtividade()">
            ${g.saving ? "Salvando…" : "Salvar metas"}</button>
          <button class="btn btn-ghost" onclick="fecharMetasAtividade()">Cancelar</button>
        </div>
      </div>
    </div>`;
}

function blocoConfiguracaoUnidade() {
  const d = state.prospects || {};
  if (!d.canSetPhase) return "";
  const fases = d.phases || [];
  return `
    <div class="table-card">
      <div class="section-title">
        <div><h3>⚙️ Configuração de unidade nova</h3>
          <div class="text-small">Fase e metas de atividade. Visível apenas para a diretoria.</div></div>
        <div style="display:flex;gap:6px;flex-wrap:wrap">
          <button class="btn btn-secondary btn-sm" onclick="abrirConfigFase('')">🚧 Fase da unidade</button>
          <button class="btn btn-secondary btn-sm" onclick="abrirMetasAtividade()">🎯 Metas de atividade</button>
        </div>
      </div>
      ${fases.length ? `
        <div class="stack" style="padding-top:8px">
          ${fases.map((p) => `
            <div style="display:flex;justify-content:space-between;gap:10px;flex-wrap:wrap;align-items:center;
                        font-size:13px;padding:8px 10px;background:#f8f9fa;border-radius:6px">
              <div>
                <strong>${escapeHtml(p.unitName)}</strong>
                <span class="status-tag" style="margin-left:6px;background:${p.isDeployment ? "#fef7e0" : "#e6f4ea"};
                      color:${p.isDeployment ? "#b06000" : "#1e8e3e"}">
                  ${p.isDeployment ? "Em implantação" : "Operação"}
                </span>
                <div class="text-small" style="color:var(--muted)">
                  ${p.openingDate ? `inaugura ${shortDate(p.openingDate)}` : "sem data de inauguração"}
                  ${p.goalExemptUntil ? ` · isenta de meta até ${escapeHtml(p.goalExemptUntil)}` : ""}
                  ${p.notes ? ` · ${escapeHtml(p.notes)}` : ""}
                </div>
              </div>
              <button class="btn btn-ghost btn-sm" onclick="abrirConfigFase('${jsAttr(p.unitName)}')">Editar</button>
            </div>`).join("")}
        </div>`
      : `<div class="text-small" style="color:var(--muted);padding-top:8px">
           Nenhuma unidade configurada. Toda unidade sem configuração é tratada como operação normal, com meta.
         </div>`}
    </div>`;
}

// ─── Base fria: empresas que ainda não são clientes ────────────────────────
//
// 70 mil CNPJs do RS, filtrados pelas cidades que a unidade atende. É prospecção
// de verdade: quem está aqui nunca comprou da Passini. O lead só vira prospect
// quando alguém o assume — assim o funil continua medindo trabalho real, não
// tamanho de lista.

async function loadLeads() {
  if (state.ui.loading.leads) return;
  setLoading("leads", true);
  requestRender();
  try {
    const f = state.leadFilters;
    const q = new URLSearchParams();
    if (f.city) q.set("city", f.city);
    if (f.segment) q.set("segment", f.segment);
    if (f.search) q.set("q", f.search);
    if (f.withPhone) q.set("withPhone", "1");
    if (f.status) q.set("status", f.status);
    state.leads = await api(`/api/prospects/leads?${q.toString()}`);
  } catch (error) {
    addMessage("error", error.message);
    state.leads = { items: [], total: 0 };
  } finally {
    setLoading("leads", false);
  }
  requestRender();
}

function toggleLeads() {
  state.ui.leadsOpen = !state.ui.leadsOpen;
  requestRender();
  if (state.ui.leadsOpen && !state.leads) void loadLeads();
}

function setLeadFilter(campo, valor) {
  state.leadFilters[campo] = valor;
  void loadLeads();
}

async function assumirLead(id, nome) {
  // Gestor precisa dizer para QUEM vai o lead — ele não trabalha a oficina.
  let vendedor = "";
  if (state.leads?.canManage) {
    vendedor = state.leadFilters.assignTo || "";
    if (!vendedor) {
      addMessage("error", "Escolha primeiro, no alto da lista, para qual vendedor os leads vão.");
      return;
    }
  }
  try {
    const r = await api("/api/prospects/leads/claim", {
      method: "POST", body: JSON.stringify({ id, sellerName: vendedor }),
    });
    addMessage("success", r.message || "Lead assumido.");
    await Promise.all([loadLeads(), loadProspects(true)]);
  } catch (error) {
    addMessage("error", error.message);
  }
}

async function descartarLead(id, nome) {
  const motivo = window.prompt(
    `Descartar "${nome}" tira a empresa da base de TODOS os vendedores.\n\n`
    + `Motivo (telefone errado, empresa fechada, fora do público-alvo):`);
  if (motivo === null) return;
  try {
    const r = await api("/api/prospects/leads/discard", {
      method: "POST", body: JSON.stringify({ id, reason: motivo }),
    });
    addMessage("success", r.message || "Lead descartado.");
    await loadLeads();
  } catch (error) {
    addMessage("error", error.message);
  }
}

/** "Já é cliente": tenta achar o cadastro pelo CNPJ e guarda o vínculo.
 *  Esconder a linha resolveria hoje; guardar o código resolve para sempre. */
async function marcarLeadCliente(id, nome) {
  try {
    const r = await api("/api/prospects/leads/client", {
      method: "POST", body: JSON.stringify({ id }),
    });
    addMessage("success", r.message);
    if (r.clientCode && window.confirm(`${r.message}\n\nAbrir a ficha deste cliente?`)) {
      await openCrmClient(r.clientCode, true, true, { outside: true });
    }
    await loadLeads();
  } catch (error) {
    addMessage("error", error.message);
  }
}

/** Quando o CNPJ não bate, o gestor informa o código na mão. */
async function vincularLeadPorCodigo(id, nome) {
  const codigo = window.prompt(`Qual o código de "${nome}" no cadastro do Alfa?`);
  if (!codigo) return;
  try {
    const r = await api("/api/prospects/leads/client", {
      method: "POST", body: JSON.stringify({ id, clientCode: codigo.trim() }),
    });
    addMessage("success", r.message);
    await loadLeads();
  } catch (error) {
    addMessage("error", error.message);
  }
}

async function restaurarLead(id) {
  try {
    const r = await api("/api/prospects/leads/restore", { method: "POST", body: JSON.stringify({ id }) });
    addMessage("success", r.message || "Lead devolvido à base.");
    await loadLeads();
  } catch (error) {
    addMessage("error", error.message);
  }
}

/** Cor da chance de contato: é a probabilidade de o telefone funcionar. */
function chanceLead(valor) {
  const v = String(valor || "").toUpperCase();
  const cor = v.includes("MUITO ALTA") || v === "ALTA" ? "var(--good)"
    : v.includes("MUITO BAIXA") || v === "BAIXA" ? "var(--bad)" : "#b06000";
  return `<span style="color:${cor};font-weight:700;font-size:11px">${escapeHtml(valor || "—")}</span>`;
}

function blocoBaseDeLeads() {
  const aberto = state.ui.leadsOpen;
  const d = state.leads;
  const f = state.leadFilters;
  const carregando = Boolean(state.ui.loading.leads);
  const resumo = d?.summary || {};

  return `
    <div class="table-card">
      <div class="section-title">
        <div>
          <h3>🧭 Base de empresas para prospectar</h3>
          <div class="text-small">Empresas do RS que ainda não são clientes da Passini,
            nas cidades que a sua unidade atende. Assuma o lead e ele entra na sua prospecção.</div>
        </div>
        <button class="btn ${aberto ? "btn-ghost" : "btn-primary"} btn-sm" type="button"
          ${carregando ? "disabled" : ""} onclick="toggleLeads()">
          ${carregando && !aberto ? "⏳ Buscando…" : (aberto ? "Fechar" : "Abrir base")}
        </button>
      </div>

      ${aberto ? `
        <div class="two-column-form" style="margin-top:10px">
          <div class="field"><label>Cidade</label>
            <select onchange="setLeadFilter('city', this.value)">
              <option value="">Todas as cidades da unidade</option>
              ${(d?.cities || []).map((c) => `<option value="${escapeHtml(c)}" ${f.city === c ? "selected" : ""}>${escapeHtml(c)}</option>`).join("")}
            </select></div>
          <div class="field"><label>Segmento</label>
            <select onchange="setLeadFilter('segment', this.value)">
              <option value="">Todos</option>
              ${(d?.segments || []).map((sg) => `<option value="${escapeHtml(sg.id)}" ${f.segment === sg.id ? "selected" : ""}>${sg.icon} ${escapeHtml(sg.label)}</option>`).join("")}
            </select></div>
          <div class="field"><label>Buscar</label>
            <div style="display:flex;gap:8px">
              <input style="flex:1" value="${escapeHtml(f.search || "")}" placeholder="Nome ou CNPJ"
                oninput="state.leadFilters.search=this.value"
                onkeydown="if(event.key==='Enter'){event.preventDefault();loadLeads();}" />
              <button class="btn btn-secondary btn-sm" type="button"
                ${carregando ? "disabled" : ""} onclick="loadLeads()">
                ${carregando ? "⏳" : "Buscar"}</button>
              ${f.search ? `<button class="btn btn-ghost btn-sm" type="button"
                onclick="state.leadFilters.search='';loadLeads()">Limpar</button>` : ""}
            </div></div>
          <div class="field" style="align-self:end">
            <label class="check-row" style="font-weight:500">
              <input type="checkbox" ${f.withPhone ? "checked" : ""}
                onchange="setLeadFilter('withPhone', this.checked)" />
              <span>Só com telefone</span>
            </label></div>
          ${d?.canManage ? `
            <div class="field"><label>Situação</label>
              <select onchange="setLeadFilter('status', this.value)">
                <option value="">Disponíveis</option>
                <option value="DESCARTADO" ${f.status === "DESCARTADO" ? "selected" : ""}>Descartados</option>
                <option value="ADOTADO" ${f.status === "ADOTADO" ? "selected" : ""}>Já assumidos</option>
                <option value="CLIENTE" ${f.status === "CLIENTE" ? "selected" : ""}>Viraram clientes</option>
              </select></div>
            <div class="field">
              <label>Enviar leads para <span style="color:var(--bad)">*</span></label>
              <select onchange="state.leadFilters.assignTo=this.value;requestRender()">
                <option value="">Selecione o vendedor…</option>
                ${(d.sellers || []).map((v) => `<option value="${escapeHtml(v)}" ${f.assignTo === v ? "selected" : ""}>${escapeHtml(v)}</option>`).join("")}
              </select>
              <div class="text-small" style="color:var(--muted);margin-top:4px">
                Você não trabalha a oficina — o lead precisa de dono.
              </div></div>` : ""}
        </div>

        ${carregando ? `<div class="message" style="background:rgba(15,48,68,0.07);color:var(--accent);font-weight:600">
          ⏳ Buscando na base…</div>` : ""}

        ${d?.blocked ? `<div class="message error">${escapeHtml(d.blocked)}</div>` : ""}

        ${d && !d.unrestricted && !d.cities?.length && !d.blocked ? `
          <div class="message">Sua unidade ainda não tem cidades mapeadas. Fale com o gestor —
            o mapa fica em Administração → Territórios.</div>` : ""}
        ${d?.unrestricted ? `
          <div class="text-small" style="color:var(--muted);margin-top:4px">
            Seu perfil enxerga o estado inteiro. Vendedor e gerente veem só as cidades da unidade deles.
          </div>` : ""}

        ${d && d.items ? `
          <div style="${carregando ? "opacity:.45;pointer-events:none" : ""}">
            <div class="text-small" style="color:var(--muted);margin:8px 0">
              ${number(d.total)} empresa(s) disponível(is)
              ${d.limited ? ` · mostrando as ${number(d.items.length)} de melhor contato` : ""}
              ${resumo.ADOTADO ? ` · ${number(resumo.ADOTADO)} já assumida(s)` : ""}
            </div>
            <div class="table-wrap">
              <table class="table-sticky-actions">
                <thead><tr>
                  <th>Empresa</th><th>Segmento</th><th>Cidade</th><th>Telefone</th>
                  <th>Porte</th><th>Contato</th><th style="text-align:right">Ações</th>
                </tr></thead>
                <tbody>
                  ${d.items.length ? d.items.map((l) => `
                    <tr>
                      <td><strong>${escapeHtml(l.razao_social)}</strong>
                        ${l.nome_fantasia ? `<div class="text-small">${escapeHtml(l.nome_fantasia)}</div>` : ""}
                        <div class="text-small" style="color:var(--muted)">${escapeHtml(l.cnpj)}</div></td>
                      <td class="text-small">${escapeHtml((d.segments || []).find((sg) => sg.id === l.segmento)?.label || l.segmento || "-")}</td>
                      <td class="text-small">${escapeHtml(l.cidade || "-")}${l.bairro ? `<div style="color:var(--muted)">${escapeHtml(l.bairro)}</div>` : ""}</td>
                      <td class="text-small">${l.telefone ? escapeHtml(l.telefone) : '<span style="color:var(--muted)">sem telefone</span>'}</td>
                      <td class="text-small">${escapeHtml(l.porte || "-")}<div style="color:var(--muted)">${escapeHtml(l.faixa_faturamento || "")}</div></td>
                      <td>${chanceLead(l.chance_contato)}</td>
                      <td style="text-align:right;white-space:nowrap">
                        ${l.status === "CLIENTE" ? (l.client_code ? `
                          <button class="btn btn-ghost btn-sm" type="button"
                            onclick="openCrmClient('${jsAttr(l.client_code)}', true, true, { outside: true })">
                            Ficha ${escapeHtml(l.client_code)}</button>`
                          : `<button class="btn btn-ghost btn-sm" type="button"
                            onclick="vincularLeadPorCodigo(${Number(l.id)}, '${jsAttr(l.razao_social)}')">
                            Informar código</button>`)
                        : l.status === "DESCARTADO" ? `
                          <button class="btn btn-ghost btn-sm" type="button"
                            onclick="restaurarLead(${Number(l.id)})">Devolver à base</button>`
                        : l.status !== "NOVO" ? `<span class="text-small" style="color:var(--muted)">${escapeHtml(l.claimed_by || l.status)}</span>`
                        : `
                          <button class="btn btn-primary btn-sm" type="button"
                            onclick="assumirLead(${Number(l.id)}, '${jsAttr(l.razao_social)}')">Assumir</button>
                          <button class="btn btn-secondary btn-sm" type="button"
                            title="Esta empresa já é cliente da Passini — o sistema busca o código pelo CNPJ"
                            onclick="marcarLeadCliente(${Number(l.id)}, '${jsAttr(l.razao_social)}')">Já é cliente</button>
                          ${d.canManage ? `<button class="btn btn-ghost btn-sm" type="button"
                            title="Tira da base de todos os vendedores"
                            onclick="descartarLead(${Number(l.id)}, '${jsAttr(l.razao_social)}')">Descartar</button>` : ""}`}
                      </td>
                    </tr>`).join("")
                    : '<tr><td colspan="7" class="text-small">Nenhuma empresa com esse filtro.</td></tr>'}
                </tbody>
              </table>
            </div>
            <div class="text-small" style="color:var(--muted);margin-top:8px;line-height:1.6">
              Achou uma empresa que já compra da Passini? <strong>Já é cliente</strong> tira da fila
              e guarda o vínculo pelo CNPJ — na próxima carga da base ela não volta.<br>
              A ordem prioriza quem tem telefone confiável — ligação que não completa é tempo
              perdido antes da abordagem. <strong>Assumir</strong> cria o prospect no seu nome com
              os dados já preenchidos; <strong>Descartar</strong> tira da fila sem apagar o registro.
            </div>
          </div>` : ""}
      ` : ""}
    </div>`;
}

// ─── Reativação: inativos da unidade ───────────────────────────────────────
//
// Prospecção não é só oficina nova. Cliente que já comprou e parou é a
// oportunidade mais barata que existe: o cadastro está pronto, alguém já
// confiou na Passini uma vez e a objeção costuma ter nome. Aqui o vendedor
// acha esses clientes na unidade dele, tenham dono ou não.

async function loadInativos() {
  if (state.ui.loading.inactives) return;
  setLoading("inactives", true);
  requestRender();   // sem isto o "Buscando…" só apareceria depois da resposta
  try {
    const q = (state.ui.inactiveSearch || "").trim();
    state.inactives = await api(`/api/prospects/inactive${q ? `?q=${encodeURIComponent(q)}` : ""}`);
  } catch (error) {
    addMessage("error", error.message);
    state.inactives = { items: [], total: 0 };
  } finally {
    setLoading("inactives", false);
  }
  requestRender();
}

function toggleInativos() {
  state.ui.inactivesOpen = !state.ui.inactivesOpen;
  requestRender();                       // abre o painel na hora
  if (state.ui.inactivesOpen && !state.inactives) void loadInativos();
}

function blocoInativosDaUnidade() {
  const aberto = state.ui.inactivesOpen;
  const d = state.inactives;
  const carregando = Boolean(state.ui.loading.inactives);

  return `
    <div class="table-card">
      <div class="section-title">
        <div>
          <h3>♻️ Reativar inativos da unidade</h3>
          <div class="text-small">Clientes que já compraram e pararam — com ou sem vendedor.
            Cadastro pronto e objeção conhecida: é a prospecção mais barata que existe.</div>
        </div>
        <button class="btn ${aberto ? "btn-ghost" : "btn-primary"} btn-sm" type="button"
          ${carregando ? "disabled" : ""} onclick="toggleInativos()">
          ${carregando && !aberto ? "⏳ Buscando…" : (aberto ? "Fechar" : "Buscar inativos")}
        </button>
      </div>

      ${aberto ? `
        <div style="display:flex;gap:8px;margin:10px 0">
          <input style="flex:1" placeholder="Filtrar por nome, cidade ou código"
            value="${escapeHtml(state.ui.inactiveSearch || "")}"
            oninput="state.ui.inactiveSearch=this.value"
            onkeydown="if(event.key==='Enter'){event.preventDefault();loadInativos();}" />
          <button class="btn btn-secondary btn-sm" type="button"
            ${carregando ? "disabled" : ""} onclick="loadInativos()">
            ${carregando ? "⏳ Buscando…" : "Filtrar"}</button>
        </div>

        ${carregando ? `
          <div class="message" style="background:rgba(15,48,68,0.07);color:var(--accent);font-weight:600">
            ⏳ Buscando inativos da unidade… a varredura passa pela carteira inteira e pode
            levar alguns segundos.
          </div>` : ""}

        ${d ? `
          <div style="${carregando ? "opacity:.45;pointer-events:none" : ""}">
          <div class="text-small" style="color:var(--muted);margin-bottom:8px">
            ${number(d.total)} inativo(s) em <strong>${escapeHtml(d.unitName || "todas")}</strong>
            · ${number(d.withoutSeller)} sem vendedor
            ${d.total > (d.items || []).length ? ` · mostrando os ${number(d.items.length)} de maior potencial` : ""}
          </div>
          <div class="table-wrap">
            <table class="table-sticky-actions">
              <thead><tr>
                <th>Cliente</th><th>Cidade</th><th>Classe</th>
                <th style="text-align:right">Média/mês</th><th style="text-align:right">Dias parado</th>
                <th>Carteira</th><th style="text-align:right">Ações</th>
              </tr></thead>
              <tbody>
                ${(d.items || []).length ? d.items.map((c) => `
                  <tr>
                    <td><strong>${escapeHtml(c.clientName)}</strong>
                        <div class="text-small" style="color:var(--muted)">${escapeHtml(c.clientKey)}${c.phone ? ` · ${escapeHtml(c.phone)}` : ""}</div></td>
                    <td class="text-small">${escapeHtml([c.cityName, c.neighborhood].filter(Boolean).join(" · ") || "-")}</td>
                    <td class="text-small">${escapeHtml(c.classCode || "-")}</td>
                    <td style="text-align:right">${currency(c.averageRevenue || 0)}</td>
                    <td style="text-align:right;color:var(--bad);font-weight:700">${number(c.daysWithoutPurchase || 0)}</td>
                    <td class="text-small">
                      ${c.isMine ? '<span class="soft-badge">sua carteira</span>'
                        : (c.assignedSeller === "Sem vendedor"
                            ? '<span style="color:var(--good);font-weight:700">sem vendedor</span>'
                            : escapeHtml(c.assignedSeller))}
                    </td>
                    <td style="text-align:right;white-space:nowrap">
                      <button class="btn btn-primary btn-sm" type="button"
                        onclick="openCrmClient('${jsAttr(c.clientKey)}', false, true, { outside: true })">Abrir ficha</button>
                    </td>
                  </tr>`).join("")
                  : '<tr><td colspan="7" class="text-small">Nenhum cliente inativo com esse filtro.</td></tr>'}
              </tbody>
            </table>
          </div>
          <div class="text-small" style="color:var(--muted);margin-top:8px;line-height:1.6">
            Ordenado pela média histórica: quem já comprou mais vale mais o telefonema.
            Cliente <strong>sem vendedor</strong> é o alvo mais direto — ninguém responde por ele hoje.
          </div>
          </div>` : ""}
      ` : ""}
    </div>`;
}

function prospeccaoView() {
  if (!state.prospects) { loadProspects(); return `<div class="loader panel">Carregando prospecção…</div>`; }
  if (state.prospects.error) return `<div class="message error">${escapeHtml(state.prospects.error)}</div>`;

  const d = state.prospects;
  const f = state.prospectFilters;
  const lista = d.prospects || [];
  const fun = d.funnel || {};
  const fase = d.unitPhase || {};
  const podeGerir = Boolean(d.canManage);

  const kpi = (rotulo, valor, sub, cor) => `
    <div style="flex:1;min-width:130px;background:#fff;border:1px solid var(--line);border-radius:10px;padding:10px 12px">
      <div class="text-small" style="color:var(--muted)">${rotulo}</div>
      <div style="font-size:22px;font-weight:800;color:${cor || "inherit"}">${valor}</div>
      ${sub ? `<div class="text-small" style="color:var(--muted)">${sub}</div>` : ""}
    </div>`;

  return `
    <div class="stack">
      ${state.prospectEditor ? prospectEditorModal() : ""}
      ${pedidoCadastroModal()}
      ${configFaseModal()}
      ${metasAtividadeModal()}

      ${blocoConfiguracaoUnidade()}

      ${blocoBaseDeLeads()}
      ${blocoInativosDaUnidade()}

      ${fase.isDeployment ? `
        <div class="panel" style="padding:14px 18px;border-left:4px solid #f4c25f">
          <div style="font-weight:800;font-size:14px">🚧 ${escapeHtml(fase.unitName || "Unidade")} em implantação</div>
          <div class="text-small" style="margin-top:4px;line-height:1.55">
            ${fase.openingDate ? `Inauguração prevista para ${shortDate(fase.openingDate)}. ` : ""}
            Sem meta de faturamento nesta fase — o que mede o trabalho é o esforço de prospecção.
            A carteira se forma sozinha: cada oficina cadastrada no Alfa vira cliente aqui,
            levando junto o histórico de ligações.
          </div>
        </div>` : ""}

      ${(d.activity || []).some((a) => a.target > 0) ? `
        <div class="table-card">
          <div class="section-title">
            <div><h3>🎯 Metas de atividade — ${escapeHtml(d.competence || "")}</h3>
              <div class="text-small">Comparadas com o ritmo esperado para o dia do mês, como os faróis.</div></div>
          </div>
          <div style="display:flex;gap:10px;flex-wrap:wrap;padding-top:8px">
            ${d.activity.filter((a) => a.target > 0).map((a) => `
              <div style="flex:1;min-width:150px;background:#fff;border:1px solid var(--line);
                          border-left:3px solid ${a.onTrack === false ? "var(--bad)" : "var(--good)"};
                          border-radius:0 10px 10px 0;padding:10px 12px">
                <div class="text-small" style="color:var(--muted)">${a.icon} ${escapeHtml(a.label)}</div>
                <div style="font-size:20px;font-weight:800;color:${a.onTrack === false ? "var(--bad)" : "var(--good)"}">
                  ${number(a.actual)}<span style="font-size:13px;font-weight:500;color:var(--muted)"> / ${number(a.target)}</span>
                </div>
                <div class="text-small" style="color:var(--muted)">esperado até hoje: ${number(a.expectedToDate)}</div>
              </div>`).join("")}
          </div>
        </div>` : ""}

      <div style="display:flex;gap:10px;flex-wrap:wrap">
        ${kpi("Prospects", number(fun.total || 0), `${number(fun.withoutContact || 0)} sem contato`)}
        ${kpi("Qualificados", number(fun.byStatus?.QUALIFICADO || 0), "4 perguntas + gatilho", "var(--good)")}
        ${kpi("Viraram cliente", number(fun.byStatus?.CADASTRADO || 0), `${fun.conversionPct || 0}% de conversão`, "var(--accent)")}
        ${kpi("Parados há 7+ dias", number(fun.stale || 0), "precisam de retorno",
              (fun.stale || 0) > 0 ? "var(--bad)" : "")}
      </div>

      <div class="form-card" style="padding:14px 18px">
        <div style="display:flex;gap:8px;flex-wrap:wrap;align-items:center;margin-bottom:10px">
          <input id="prospect-search" style="flex:1;min-width:200px"
            placeholder="🔍 Buscar por nome, contato, CNPJ ou cidade — Enter"
            value="${escapeHtml(f.search)}"
            oninput="state.prospectFilters.search=this.value"
            onkeydown="if(event.key==='Enter'){event.preventDefault();applyProspectSearch();}" />
          <button class="btn btn-secondary btn-sm" onclick="applyProspectSearch()">Buscar</button>
          <button class="btn btn-primary btn-sm" onclick="novoProspect()">＋ Nova oficina</button>
          ${podeGerir ? `<button class="btn btn-ghost btn-sm" onclick="reconciliarProspects()"
            title="Procura no cadastro do Alfa os CNPJs dos prospects e vincula quem já foi cadastrado">↻ Buscar cadastros novos</button>` : ""}
        </div>
        <div style="display:flex;gap:6px;flex-wrap:wrap">
          ${(d.statuses || []).map((s) => `
            <button type="button" onclick="setProspectStatus('${s.id}')" title="${escapeHtml(s.hint)}"
              ${chipEmEspera("prospectStatus") ? "disabled" : ""}
              style="border:1px solid ${f.status === s.id ? s.color : "var(--line)"};
                     background:${f.status === s.id ? s.bg : "#fff"};
                     color:${f.status === s.id ? s.color : "var(--muted)"};
                     border-radius:14px;padding:4px 12px;font-size:12px;
                     font-weight:${f.status === s.id ? "700" : "500"};
                     ${chipEstadoCss("prospectStatus", f.status === s.id)}">
              ${chipTrocando("prospectStatus") === s.id
                ? `<span class="girando">↻</span> Carregando…`
                : `${s.icon} ${escapeHtml(s.label)} (${number(fun.byStatus?.[s.id] || 0)})`}
            </button>`).join("")}
        </div>
        <div class="text-small" style="color:var(--muted);margin-top:2px">
          A lista mostra o que ainda é trabalho de prospecção. Quem ganhou vendedor no
          cadastro virou carteira e quem foi dado como perdido saem daqui — clique no
          selo correspondente para revê-los.
        </div>
      </div>

      <div class="table-card">
        <div class="section-title">
          <div><h3>Oficinas em prospecção</h3>
            <div class="text-small">${lista.length} no filtro atual</div></div>
        </div>
        <div class="stack" style="padding-top:8px">
          ${state.ui.loading.prospects ? '<div class="loader">Buscando…</div>' : ""}
          ${lista.map((p) => prospectCard(p, podeGerir)).join("")
            || emptyStateCard("Nenhuma oficina aqui ainda. Comece pelo botão Nova oficina.")}
        </div>
      </div>
    </div>`;
}

// ─── Vendas por Marca ───────────────────────────────────────────────────────
//
// Três recortes na mesma tela. O vendedor abre nas próprias vendas e pode
// olhar a unidade e o grupo para se comparar; o gestor abre no grupo e desce
// até o vendedor. O que muda entre os perfis é o que cada um pode selecionar,
// nunca a forma da tabela — quem aprende a ler uma, lê as três.

// Cada chamada recebe um número. A resposta só é aceita se ainda for a mais
// recente. Sem isso, a carga que a tela dispara ao abrir — mais lenta, porque
// é a primeira — voltava DEPOIS da troca para Linha e sobrescrevia a tela com
// a visão por Marca, enquanto o botão continuava marcado em Linha.
let brandRequestSeq = 0;

async function loadBrands(silencioso) {
  const f = state.brandFilters;
  const q = new URLSearchParams();
  const mes = state.filters.competenceEnd || state.filters.competenceStart;
  if (mes) q.set("competence", mes);
  if (f.scope) q.set("scope", f.scope);
  if (f.dimension) q.set("dimension", f.dimension);
  const meuPedido = ++brandRequestSeq;
  if (!silencioso) {
    state.ui.loading.brands = true;
    // Pintar a tela ANTES de sair para a rede. Sem isto o "Carregando" só
    // apareceria depois da resposta — ou seja, nunca.
    requestRender();
  }
  let resposta;
  try {
    resposta = await api(`/api/brands?${q.toString()}`);
  } catch (e) {
    resposta = { error: e.message, rows: [], scopes: [], insights: [], totals: {} };
  }
  // Chegou atrasada: outra chamada já saiu depois desta. Descartar é o certo —
  // aplicar mostraria dados que ninguém pediu mais.
  if (meuPedido !== brandRequestSeq) return state.brands;
  state.brands = resposta;
  state.ui.loading.brands = false;
  requestRender();
  return state.brands;
}

async function setBrandScope(id) {
  // Segundo clique enquanto a troca ainda roda não faz nada: duas requisições
  // concorrentes podem voltar fora de ordem e mostrar o recorte errado.
  if (state.brandLoadingScope) return;
  if (state.brandFilters.scope === id && state.brands) return;
  state.brandFilters.scope = id;
  // A aba clicada já fica marcada e com "Carregando": a resposta pode demorar
  // (o detalhe por vendedor varre o mês inteiro) e botão que não reage a clique
  // parece quebrado — a pessoa clica de novo.
  state.brandLoadingScope = id;
  // O detalhe aberto no recorte anterior não faz sentido no novo: no grupo ele
  // mostra unidades, em "por vendedor" mostra pessoas.
  state.brandOpen = {};
  requestRender();
  try {
    await loadBrands();
  } finally {
    state.brandLoadingScope = "";
    requestRender();
  }
}

/** Troca de aba/filtro avisando que o comando foi recebido.
 *
 *  `chave` identifica o grupo de chips; `id` é o clicado. Enquanto a carga
 *  roda, `chipTrocando(chave)` devolve o id em andamento — é isso que faz o
 *  chip mostrar "Carregando…" e os vizinhos travarem. Sem esse retorno visual
 *  imediato o clique parece perdido e a pessoa clica de novo, disparando duas
 *  buscas que podem voltar fora de ordem.
 */
async function trocarChip(chave, id, carregar) {
  if (state.ui.switching[chave]) return;
  state.ui.switching[chave] = id || "__todos__";
  requestRender();
  try {
    await carregar();
  } finally {
    delete state.ui.switching[chave];
    requestRender();
  }
}

function chipTrocando(chave) {
  const v = state.ui.switching[chave];
  return v === "__todos__" ? "" : (v || null);
}

function chipEmEspera(chave) { return Boolean(state.ui.switching[chave]); }

/** Estilo do chip durante a troca: some o cursor de clique e esmaece o resto. */
function chipEstadoCss(chave, ativo) {
  if (!chipEmEspera(chave)) return "cursor:pointer";
  return `cursor:wait;opacity:${ativo ? "1" : "0.5"}`;
}

/** Troca entre olhar por marca, por linha ou por grupo. */
async function setBrandDimension(id) {
  if (state.brandLoadingScope) return;
  if ((state.brandFilters.dimension || "marca") === id) return;
  state.brandFilters.dimension = id;
  state.brandOpen = {};
  state.brandLoadingScope = "dim:" + id;
  requestRender();
  try {
    await loadBrands();
  } finally {
    state.brandLoadingScope = "";
    requestRender();
  }
}

function toggleBrand(marca) {
  if (state.brandOpen[marca]) delete state.brandOpen[marca];
  else state.brandOpen[marca] = true;
  requestRender();
}

/** Marca, linha ou grupo — o mesmo faturamento, três formas de enxergar. */
function blocoDimensaoMarca(d) {
  const atual = state.brandFilters.dimension || d.dimension || "marca";
  const trocando = String(state.brandLoadingScope || "");
  return `
    <div class="panel" style="padding:12px 18px">
      <div style="display:flex;gap:8px;flex-wrap:wrap;align-items:center">
        <span class="text-small" style="color:var(--muted);font-weight:700">Olhar por</span>
        ${(d.dimensions || []).map((x) => `
          <button type="button" onclick="setBrandDimension('${x.id}')"
            title="${escapeHtml(x.hint)}" ${trocando ? "disabled" : ""}
            style="border:1px solid ${atual === x.id ? "var(--accent)" : "var(--line)"};
                   background:${atual === x.id ? "var(--accent)" : "#fff"};
                   color:${atual === x.id ? "#fff" : "var(--text)"};
                   border-radius:14px;padding:5px 16px;font-size:13px;font-weight:700;
                   cursor:${trocando ? "wait" : "pointer"}">
            ${trocando === "dim:" + x.id
              ? `<span class="girando">↻</span> Carregando…`
              : escapeHtml(x.label)}
          </button>`).join("")}
        <span class="text-small" style="color:var(--muted);margin-left:4px">
          ${escapeHtml((d.dimensions || []).find((x) => x.id === atual)?.hint || "")}
        </span>
      </div>
    </div>`;
}

let returnsRequestSeq = 0;

async function loadReturns(silencioso) {
  const f = state.returnFilters;
  const q = new URLSearchParams();
  const mes = state.filters.competenceEnd || state.filters.competenceStart;
  if (mes) q.set("competence", mes);
  if (f.scope) q.set("scope", f.scope);
  if (f.dimension) q.set("dimension", f.dimension);
  const meuPedido = ++returnsRequestSeq;
  if (!silencioso) {
    state.ui.loading.returns = true;
    requestRender();
  }
  let resposta;
  try {
    resposta = await api(`/api/returns?${q.toString()}`);
  } catch (e) {
    resposta = { error: e.message, rows: [], scopes: [], insights: [], totals: {} };
  }
  // Resposta atrasada de uma troca de aba anterior: descartar, senão a tela
  // volta sozinha para o recorte que o usuário já abandonou.
  if (meuPedido !== returnsRequestSeq) return state.returns;
  state.returns = resposta;
  state.returnLoadingScope = null;
  state.ui.loading.returns = false;
  requestRender();
  return resposta;
}

function setReturnScope(id) {
  if (state.returnFilters.scope === id) return;
  state.returnFilters.scope = id;
  state.returnLoadingScope = id;
  requestRender();
  loadReturns(true);
}

function setReturnDimension(id) {
  if (state.returnFilters.dimension === id) return;
  state.returnFilters.dimension = id;
  state.returns = null;
  requestRender();
  loadReturns();
}

function devolucoesView() {
  if (!state.returns) {
    if (!state.ui.loading.returns) loadReturns();
    return `<div class="loader panel">Carregando devoluções…</div>`;
  }
  const d = state.returns;
  if (d.error) return `<div class="message error">${escapeHtml(d.error)}</div>`;

  const t = d.totals || {};
  const linhas = d.rows || [];
  const trocando = state.returnLoadingScope;
  const escopoAtual = trocando || d.scope;
  const rotuloDim = (d.dimensions || []).find((x) => x.id === d.dimension)?.label || "Motivo";

  const seta = (v) => v === null || v === undefined ? "" :
    `<span style="color:${v >= 0 ? "var(--bad)" : "var(--good)"};font-weight:700">
       ${v >= 0 ? "▲" : "▼"} ${Math.abs(v).toFixed(0)}%</span>`;

  const kpi = (rotulo, valor, sub, cor) => `
    <div style="flex:1;min-width:130px;background:#fff;border:1px solid var(--line);
                border-radius:10px;padding:10px 12px${cor ? `;border-left:4px solid ${cor}` : ""}">
      <div class="text-small" style="color:var(--muted)">${rotulo}</div>
      <div style="font-size:20px;font-weight:800">${valor}</div>
      ${sub ? `<div class="text-small" style="color:var(--muted)">${sub}</div>` : ""}
    </div>`;

  const seletorDimensao = `
    <div style="display:flex;gap:6px;flex-wrap:wrap">
      ${(d.dimensions || []).map((x) => `
        <button type="button" onclick="setReturnDimension('${x.id}')"
          style="border:1px solid ${d.dimension === x.id ? "var(--accent)" : "var(--line)"};
                 background:${d.dimension === x.id ? "#e8f0fe" : "#fff"};
                 color:${d.dimension === x.id ? "var(--accent)" : "var(--muted)"};
                 border-radius:14px;padding:5px 14px;font-size:13px;
                 font-weight:${d.dimension === x.id ? "700" : "500"};cursor:pointer">
          ${escapeHtml(x.label)}
        </button>`).join("")}
    </div>`;

  if (d.empty) {
    return `
      <div class="stack">
        <div class="panel" style="padding:18px;border-left:4px solid #f4c25f">
          <div style="font-weight:800;font-size:15px">Sem devoluções neste mês</div>
          <div class="text-small" style="margin-top:6px;line-height:1.6">${escapeHtml(d.empty)}</div>
        </div>
      </div>`;
  }

  return `
    <div class="stack">
      <div class="panel" style="padding:14px 18px">
        <div style="display:flex;gap:10px;flex-wrap:wrap;align-items:center">
          <div style="display:flex;gap:6px;flex-wrap:wrap">
            ${(d.scopes || []).map((s) => `
              <button type="button" onclick="setReturnScope('${s.id}')" ${trocando ? "disabled" : ""}
                style="border:1px solid ${escopoAtual === s.id ? "var(--accent)" : "var(--line)"};
                       background:${escopoAtual === s.id ? "#e8f0fe" : "#fff"};
                       color:${escopoAtual === s.id ? "var(--accent)" : "var(--muted)"};
                       border-radius:14px;padding:5px 14px;font-size:13px;
                       font-weight:${escopoAtual === s.id ? "700" : "500"};
                       cursor:${trocando ? "wait" : "pointer"};opacity:${trocando && escopoAtual !== s.id ? "0.5" : "1"}">
                ${trocando === s.id ? `<span class="girando">↻</span> Carregando…` : escapeHtml(s.label)}
              </button>`).join("")}
          </div>
          <span style="flex:1"></span>
          ${botaoAtualizar("returns", "loadReturns()", { mensagem: "Devoluções atualizadas." })}
        </div>
        <div style="margin-top:10px">${seletorDimensao}</div>
        <div class="text-small" style="color:var(--muted);margin-top:8px;line-height:1.5">
          Competência ${escapeHtml(d.competence || "—")} · comparado com ${escapeHtml(d.prevCompetence || "—")} ·
          a devolução entra no mês em que <strong>deu entrada</strong>, não no mês da nota de venda.
          Estes números são informativos: meta e comissão saem do relatório de custo × venda.
        </div>
      </div>

      <div style="display:flex;gap:10px;flex-wrap:wrap">
        ${kpi("Total devolvido", currency(t.value),
              t.deltaPct !== null && t.deltaPct !== undefined
                ? `${seta(t.deltaPct)} vs mês anterior` : "sem base de comparação")}
        ${kpi("Comercial", currency(t.commercialValue),
              "desistência, erro de venda e separação", "var(--accent)")}
        ${kpi("Garantia", currency(t.warrantyValue),
              "defeito de peça — assunto do fornecedor", "#e67e22")}
        ${kpi("% do faturamento", `${(t.ratioPct || 0).toFixed(2)}%`,
              `sobre ${currency(t.revenue || 0)}`)}
      </div>

      ${(d.insights || []).length ? `
        <div class="panel" style="padding:14px 18px">
          <div style="font-weight:800;font-size:14px;margin-bottom:8px">💡 Leituras do mês</div>
          <div class="stack" style="gap:8px">
            ${d.insights.map((i) => `
              <div style="display:flex;gap:10px;align-items:start;padding:9px 11px;border-radius:8px;
                          background:${i.tone === "alerta" ? "#fef7e0" : i.tone === "bom" ? "#e6f4ea" : "#e8f0fe"}">
                <div style="font-size:16px;line-height:1.2">${
                  i.tone === "alerta" ? "⚠️" : i.tone === "bom" ? "✅" : "ℹ️"}</div>
                <div>
                  <div style="font-weight:700;font-size:13px">${escapeHtml(i.title)}</div>
                  <div class="text-small" style="line-height:1.5">${escapeHtml(i.text)}</div>
                </div>
              </div>`).join("")}
          </div>
        </div>` : ""}

      <div class="panel">
        <div class="table-wrap">
          <table class="table">
            <thead>
              <tr>
                <th>${escapeHtml(rotuloDim)}</th>
                <th style="text-align:right">Devoluções</th>
                <th style="text-align:right">Itens</th>
                <th style="text-align:right">Comercial</th>
                <th style="text-align:right">Garantia</th>
                <th style="text-align:right">Total</th>
                <th style="text-align:right">% do mês</th>
                <th style="text-align:right">vs mês anterior</th>
              </tr>
            </thead>
            <tbody>
              ${linhas.map((r) => `
                <tr>
                  <td>
                    <strong>${escapeHtml(r.name)}</strong>
                    ${r.kind === "garantia"
                      ? `<span class="text-small" style="color:#e67e22"> · só garantia</span>` : ""}
                  </td>
                  <td style="text-align:right">${number(r.returns)}</td>
                  <td style="text-align:right">${number(r.items)}</td>
                  <td style="text-align:right">${currency(r.commercialValue)}</td>
                  <td style="text-align:right;color:${r.warrantyValue ? "#e67e22" : "var(--muted)"}">
                    ${currency(r.warrantyValue)}</td>
                  <td style="text-align:right;font-weight:700">${currency(r.value)}</td>
                  <td style="text-align:right">${(r.sharePct || 0).toFixed(1)}%</td>
                  <td style="text-align:right">
                    ${r.prevValue
                      ? `${seta(r.deltaPct)} <span class="text-small" style="color:var(--muted)">${
                          currency(r.prevValue)}</span>`
                      : `<span class="text-small" style="color:var(--muted)">novo</span>`}
                  </td>
                </tr>`).join("")}
            </tbody>
          </table>
        </div>
      </div>
    </div>`;
}

function marcasView() {
  if (!state.brands) {
    // Guarda contra disparar uma carga nova a cada repintura enquanto a
    // primeira ainda está no ar.
    if (!state.ui.loading.brands) loadBrands();
    return `<div class="loader panel">Carregando marcas…</div>`;
  }
  const d = state.brands;
  if (d.error) return `<div class="message error">${escapeHtml(d.error)}</div>`;

  const f = state.brandFilters;
  const t = d.totals || {};
  const linhas = d.rows || [];
  // Enquanto troca, vale a aba clicada — não a que o servidor ainda devolve.
  const trocando = state.brandLoadingScope;
  const escopoAtual = trocando || d.scope;
  const rotuloDim = (d.dimensions || []).find((x) => x.id === d.dimension)?.label || "Marca";

  if (d.needsCatalog) {
    return `
      <div class="stack">
        ${blocoDimensaoMarca(d)}
        <div class="panel" style="padding:18px;border-left:4px solid #f4c25f">
          <div style="font-weight:800;font-size:15px">Falta o cadastro de itens</div>
          <div class="text-small" style="margin-top:6px;line-height:1.6">
            ${escapeHtml(d.needsCatalog)}
          </div>
        </div>
      </div>`;
  }

  if (d.needsReimport) {
    return `
      <div class="panel" style="padding:18px;border-left:4px solid #f4c25f">
        <div style="font-weight:800;font-size:15px">A marca ainda não está no banco</div>
        <div class="text-small" style="margin-top:6px;line-height:1.6">
          A coluna <strong>Marca</strong> sempre veio no relatório de faturamento do Alfa,
          mas não era gravada — por isso os meses já importados estão sem ela.
          Reimporte o <strong>faturamento detalhado</strong> dos meses que quiser analisar em
          Importações. A reimportação não duplica nada: as linhas já existentes apenas
          recebem a marca.
        </div>
      </div>`;
  }

  const seta = (v) => v === null || v === undefined ? "" :
    `<span style="color:${v >= 0 ? "var(--good)" : "var(--bad)"};font-weight:700">
       ${v >= 0 ? "▲" : "▼"} ${Math.abs(v).toFixed(0)}%</span>`;

  const kpi = (rotulo, valor, sub) => `
    <div style="flex:1;min-width:120px;background:#fff;border:1px solid var(--line);border-radius:10px;padding:10px 12px">
      <div class="text-small" style="color:var(--muted)">${rotulo}</div>
      <div style="font-size:20px;font-weight:800">${valor}</div>
      ${sub ? `<div class="text-small" style="color:var(--muted)">${sub}</div>` : ""}
    </div>`;

  return `
    <div class="stack">
      ${blocoDimensaoMarca(d)}

      <div class="panel" style="padding:14px 18px">
        <div style="display:flex;gap:10px;flex-wrap:wrap;align-items:center">
          <div style="display:flex;gap:6px;flex-wrap:wrap">
            ${(d.scopes || []).map((s) => `
              <button type="button" onclick="setBrandScope('${s.id}')" ${trocando ? "disabled" : ""}
                style="border:1px solid ${escopoAtual === s.id ? "var(--accent)" : "var(--line)"};
                       background:${escopoAtual === s.id ? "#e8f0fe" : "#fff"};
                       color:${escopoAtual === s.id ? "var(--accent)" : "var(--muted)"};
                       border-radius:14px;padding:5px 14px;font-size:13px;
                       font-weight:${escopoAtual === s.id ? "700" : "500"};
                       cursor:${trocando ? "wait" : "pointer"};opacity:${trocando && escopoAtual !== s.id ? "0.5" : "1"}">
                ${trocando === s.id
                  ? `<span class="girando">↻</span> Carregando…`
                  : escapeHtml(s.label)}
              </button>`).join("")}
          </div>
          <span style="flex:1"></span>
          ${botaoAtualizar("marcas", "loadBrands()", { mensagem: "Ranking de marcas atualizado." })}
          <button class="btn btn-secondary btn-sm" onclick="exportBrandsXLSX()">⬇ Exportar</button>
        </div>
        <div class="text-small" style="color:var(--muted);margin-top:8px">
          Competência ${escapeHtml(d.competence || "—")} · comparado com ${escapeHtml(d.prevCompetence || "—")}
          ${escopoAtual === "vendedor" && d.seller ? ` · ${escapeHtml(d.seller)}` : ""}
          ${d.breakdownBy ? ` · clique no <strong>+</strong> para abrir a marca por ${escapeHtml(d.breakdownBy)}` : ""}
        </div>
      </div>

      <div style="display:flex;gap:10px;flex-wrap:wrap">
        ${kpi("Faturamento", currency(t.revenue), t.deltaPct !== null && t.deltaPct !== undefined
              ? `${seta(t.deltaPct)} vs mês anterior` : "sem base de comparação")}
        ${kpi(`${rotuloDim}s vendidas`, number(t.brands))}
        ${kpi("Itens vendidos", number(t.items))}
        ${kpi("Códigos distintos", number(t.skus))}
      </div>

      ${(d.insights || []).length ? `
        <div class="panel" style="padding:14px 18px">
          <div style="font-weight:800;font-size:14px;margin-bottom:8px">💡 Leituras do mês</div>
          <div class="stack" style="gap:8px">
            ${d.insights.map((i) => `
              <div style="display:flex;gap:10px;align-items:start;padding:9px 11px;border-radius:8px;
                          background:${i.kind === "atencao" ? "#fef7e0" : i.kind === "bom" ? "#e6f4ea" : "#e8f0fe"}">
                <div style="font-size:16px;line-height:1.2">${i.icon}</div>
                <div>
                  <div style="font-weight:700;font-size:13px">${escapeHtml(i.title)}</div>
                  <div class="text-small" style="line-height:1.5">${escapeHtml(i.text)}</div>
                </div>
              </div>`).join("")}
          </div>
        </div>` : ""}

      <div class="table-card">
        <div class="section-title">
          <div><h3>Ranking por ${escapeHtml(rotuloDim.toLowerCase())}</h3>
            <div class="text-small">${number(linhas.length)} ${escapeHtml(rotuloDim.toLowerCase())}(s) na lista</div></div>
        </div>
        ${state.ui.loading.brands ? '<div class="loader">Carregando…</div>' : ""}
        <div class="table-wrap" style="${state.ui.loading.brands
          ? "opacity:0.45;pointer-events:none;transition:opacity .15s" : ""}">
          <table class="data-table">
            <thead><tr>
              <th style="width:34px"></th>
              <th style="width:44px">#</th>
              <th>${escapeHtml(rotuloDim)}</th>
              <th style="text-align:right">Itens vendidos</th>
              <th style="text-align:right">Códigos distintos</th>
              <th style="text-align:right">Clientes</th>
              <th style="text-align:right">Valor</th>
              <th style="text-align:right">% do total</th>
              <th style="text-align:right">vs mês anterior</th>
            </tr></thead>
            <tbody>
              ${linhas.map((r) => {
                const abre = (r.breakdown || []).length > 0;
                const aberto = Boolean(state.brandOpen[r.brand]);
                return `
                <tr ${abre ? `style="cursor:pointer" onclick="toggleBrand('${jsAttr(r.brand)}')"` : ""}>
                  <td>${abre ? `<span style="display:inline-block;width:20px;height:20px;line-height:18px;
                        text-align:center;border:1px solid var(--line);border-radius:5px;
                        font-weight:700;color:var(--muted)">${aberto ? "−" : "+"}</span>` : ""}</td>
                  <td>${r.rank}</td>
                  <td><strong>${escapeHtml(r.brand)}</strong></td>
                  <td style="text-align:right">${number(r.items)}</td>
                  <td style="text-align:right">${number(r.skus)}</td>
                  <td style="text-align:right">${number(r.clients)}</td>
                  <td style="text-align:right">${currency(r.revenue)}</td>
                  <td style="text-align:right">${r.share.toFixed(1)}%</td>
                  <td style="text-align:right">
                    ${r.isNew ? '<span class="status-tag good">novo</span>' : seta(r.deltaPct)}
                  </td>
                </tr>
                ${aberto ? (r.breakdown || []).map((b) => `
                  <tr style="background:#f7f9fc">
                    <td></td><td></td>
                    <td style="padding-left:18px;color:var(--muted)">
                      ↳ ${escapeHtml(b.sellerName || b.unitName || "—")}
                      ${b.sellerName && b.unitName ? `<span class="text-small" style="color:var(--muted)"> · ${escapeHtml(b.unitName)}</span>` : ""}
                    </td>
                    <td style="text-align:right;color:var(--muted)">${number(b.items)}</td>
                    <td style="text-align:right;color:var(--muted)">${number(b.skus)}</td>
                    <td style="text-align:right;color:var(--muted)">${number(b.clients)}</td>
                    <td style="text-align:right;color:var(--muted)">${currency(b.revenue)}</td>
                    <td style="text-align:right;color:var(--muted)">
                      ${r.revenue ? (b.revenue / r.revenue * 100).toFixed(1) : "0.0"}%
                    </td>
                    <td></td>
                  </tr>`).join("") : ""}`;
              }).join("")
                || `<tr><td colspan="9">${emptyStateCard("Sem faturamento com marca nesta competência.")}</td></tr>`}
            </tbody>
          </table>
        </div>
        ${t.hiddenBrands ? `
          <div class="text-small" style="color:var(--muted);padding:8px 12px">
            ${number(t.hiddenBrands)} ${escapeHtml(rotuloDim.toLowerCase())}(s) abaixo de ${currency(t.minRevenue)} ficaram fora da lista
            (${currency(t.hiddenRevenue)}). Elas entram no total, não no ranking.
          </div>` : ""}
      </div>

      ${(d.disappeared || []).length ? `
        <div class="panel" style="padding:14px 18px">
          <div style="font-weight:800;font-size:14px">Vendiam no mês anterior e zeraram</div>
          <div class="text-small" style="color:var(--muted);margin-top:6px">
            ${d.disappeared.map((s) => `${escapeHtml(s.brand)} (${currency(s.prevRevenue)})`).join(" · ")}
          </div>
        </div>` : ""}
    </div>`;
}

async function exportBrandsXLSX() {
  const d = state.brands;
  if (!d || !(d.rows || []).length) { addMessage("warn", "Nada para exportar."); return; }
  const detalha = Boolean(d.breakdownBy);
  const rot = (d.dimensions || []).find((x) => x.id === d.dimension)?.label || "Marca";
  const cabecalho = ["#", rot, detalha ? "Detalhe" : "", "Unidade",
                     "Itens vendidos", "Códigos distintos", "Clientes",
                     "Valor", "% do total", "Mês anterior", "Variação %"];
  const linhas = [];
  d.rows.forEach((r) => {
    linhas.push([r.rank, r.brand, "TOTAL DA MARCA", "", r.items, r.skus, r.clients,
                 r.revenue, r.share, r.prevRevenue, r.isNew ? "novo" : r.deltaPct]);
    (r.breakdown || []).forEach((b) => {
      linhas.push(["", r.brand, b.sellerName || b.unitName || "",
                   b.sellerName ? (b.unitName || "") : "",
                   b.items, b.skus, b.clients, b.revenue,
                   r.revenue ? Number((b.revenue / r.revenue * 100).toFixed(1)) : 0, "", ""]);
    });
  });
  const rotulo = d.scope === "vendedor" ? (d.seller || "vendedor")
               : d.scope === "equipe"   ? "por-vendedor" : "grupo";
  baixarPlanilha(`${rot.toLowerCase()}-${rotulo}-${d.competence}`.replace(/\s+/g, "-").toLowerCase(),
                 "Marcas", cabecalho, linhas);
}


function prospectCard(p, podeGerir) {
  const parado = p.status !== "CADASTRADO" && p.status !== "PERDIDO"
    && (p.daysSinceContact === null || p.daysSinceContact >= 7);
  return `
    <div class="crm-card clean" style="padding:14px;${parado ? "border-left:3px solid #e74c3c" : ""}">
      <div style="display:flex;justify-content:space-between;gap:10px;flex-wrap:wrap;align-items:start">
        <div style="flex:1;min-width:240px">
          <div style="display:flex;gap:6px;align-items:center;flex-wrap:wrap;margin-bottom:3px">
            ${prospectStatusBadge(p.status)}
            ${p.isQualified ? '<span class="status-tag good">4 perguntas ✓</span>' : ""}
            ${parado ? `<span class="status-tag bad">${p.daysSinceContact === null ? "Sem contato" : `${p.daysSinceContact} dias parado`}</span>` : ""}
          </div>
          <div style="font-weight:700;font-size:14px">${escapeHtml(p.companyName)}</div>
          <div class="text-small" style="color:var(--muted)">
            ${p.documentNumber ? escapeHtml(p.documentNumber) : "⚠ sem CNPJ"}
            ${p.cityName ? ` · ${escapeHtml(p.cityName)}` : ""}
            ${p.neighborhood ? ` · ${escapeHtml(p.neighborhood)}` : ""}
            ${podeGerir ? ` · ${escapeHtml(p.sellerName)}` : ""}
          </div>
          <div class="text-small">
            ${p.phone ? `📞 ${escapeHtml(p.phone)}` : "sem telefone"}
            ${p.contactName ? ` · ${escapeHtml(p.contactName)}` : ""}
            ${p.contactCount ? ` · ${number(p.contactCount)} contato(s)` : ""}
          </div>
          ${p.isQualified ? `
            <div class="text-small" style="color:var(--muted);margin-top:3px">
              ${escapeHtml(p.serviceType)} · ${number(p.carsWeek)} carros/semana ·
              gira ${escapeHtml(p.mainLine)} · paga ${escapeHtml(p.payment)}
            </div>` : ""}
          ${p.clientCode ? `
            <div class="text-small" style="color:var(--good);font-weight:600;margin-top:3px">
              ✓ Virou cliente ${escapeHtml(p.clientCode)}${p.firstPurchaseAt ? ` · 1ª compra em ${shortDate(p.firstPurchaseAt)}` : " · ainda sem compra"}
            </div>
            ${p.portfolioSeller ? `
              <div class="text-small" style="color:var(--muted);margin-top:2px">
                👥 Já é carteira de <strong>${escapeHtml(p.portfolioSeller)}</strong> — saiu da fila de prospecção
              </div>`
            : `
              <div class="text-small" style="color:#b06000;margin-top:2px">
                ⚠ Cadastrado no Alfa, mas <strong>ainda sem vendedor</strong> no cadastro —
                segue em prospecção até alguém assumir
              </div>`}` : ""}
          ${p.lostReason ? `<div class="text-small" style="color:var(--bad)">Perdido: ${escapeHtml(p.lostReason)}</div>` : ""}
        </div>
        <div style="text-align:right;min-width:130px">
          ${p.nextTaskAt ? `<div class="text-small" style="color:var(--accent)">retorno ${shortDate(p.nextTaskAt)}</div>` : ""}
          ${p.lastContactAt ? `<div class="text-small" style="color:var(--muted)">último ${shortDate(p.lastContactAt)}</div>` : ""}
        </div>
      </div>
      <div class="actions" style="gap:6px;margin-top:10px;padding-top:8px;border-top:1px solid var(--line)">
        ${p.clientCode
          ? `<button class="btn btn-secondary btn-sm" onclick="openCrmClient('${jsAttr(p.clientCode)}', true)">Abrir ficha do cliente</button>`
          : `<button class="btn btn-primary btn-sm" onclick='contatarProspect(${JSON.stringify(p).replace(/'/g, "&#39;")})'>📞 Registrar contato</button>`}
        <button class="btn btn-ghost btn-sm" onclick='editarProspect(${JSON.stringify(p).replace(/'/g, "&#39;")})'>Editar</button>
        ${!p.clientCode ? `
          <button class="btn btn-ghost btn-sm" title="Copiar razão social, CNPJ, telefone e e-mail para mandar ao cadastro"
            onclick="copiarPedidoCadastro(${p.id})">📋 Pedir cadastro</button>
          <button class="btn btn-ghost btn-sm" title="Ficha cadastral em PDF para o cliente assinar"
            onclick="baixarFichaCadastral(${p.id})">📄 Ficha</button>` : ""}
        ${p.status !== "CADASTRADO" && p.status !== "PERDIDO"
          ? `<button class="btn btn-ghost btn-sm" onclick="marcarProspectPerdido(${p.id})">Perdido</button>` : ""}
        ${podeGerir ? `<button class="btn btn-ghost btn-sm" onclick="excluirProspect(${p.id})">Excluir</button>` : ""}
      </div>
    </div>`;
}

// ─── Pedido de cadastro para o setor ────────────────────────────────────────
//
// A oficina prospectada só vira cliente quando o setor de cadastro a abre no
// Alfa, e esse pedido vai por WhatsApp. Digitar tudo de novo na mão é onde o
// dado se perde: CNPJ trocado, e-mail sem o ponto. Aqui o texto sai do que já
// foi preenchido, sem redigitação.

/** Formata CNPJ/CPF só quando o tamanho bate — número torto vai como veio. */
function formatarDocumento(valor) {
  const d = String(valor || "").replace(/\D/g, "");
  if (d.length === 14) return `${d.slice(0,2)}.${d.slice(2,5)}.${d.slice(5,8)}/${d.slice(8,12)}-${d.slice(12)}`;
  if (d.length === 11) return `${d.slice(0,3)}.${d.slice(3,6)}.${d.slice(6,9)}-${d.slice(9)}`;
  return String(valor || "");
}

/** Texto do pedido. Os quatro obrigatórios primeiro, o resto como apoio. */
function textoPedidoCadastro(p) {
  const linhas = [
    "*SOLICITAÇÃO DE CADASTRO — PASSINI*",
    "",
    `*Razão social:* ${p.companyName || ""}`,
    `*CNPJ:* ${formatarDocumento(p.documentNumber)}`,
    `*Telefone:* ${p.phone || ""}`,
    `*E-mail:* ${p.email || ""}`,
  ];
  const apoio = [
    ["Nome fantasia", p.tradeName],
    ["Contato", p.contactName],
    ["Endereço", [p.addressLine, p.neighborhood].filter(Boolean).join(", ")],
    ["Cidade", p.cityName],
  ].filter(([, v]) => String(v || "").trim());
  if (apoio.length) {
    linhas.push("");
    apoio.forEach(([r, v]) => linhas.push(`${r}: ${v}`));
  }
  linhas.push("");
  linhas.push(`Vendedor: ${p.sellerName || "—"}${p.unitName ? ` · ${p.unitName}` : ""}`);
  return linhas.join("\n");
}

async function copiarPedidoCadastro(prospectId) {
  // Aceita tanto o que acabou de ser salvo quanto uma oficina da lista.
  const p = (prospectId
    ? (state.prospects?.prospects || []).find((x) => String(x.id) === String(prospectId))
    : state.prospectCadastro);
  if (!p) { addMessage("warn", "Oficina não encontrada."); return; }
  const texto = textoPedidoCadastro(p);
  if (await copyToClipboard(texto)) {
    addMessage("success", "Dados copiados. É só colar no WhatsApp do cadastro.");
  } else {
    // Servidor em HTTP não libera a área de transferência — abre para cópia manual.
    showCopyFallback(texto, "Solicitação de cadastro");
  }
}

function fecharPedidoCadastro() {
  state.prospectCadastro = null;
  requestRender();
}

/** Confirmação que aparece logo após salvar, com o texto pronto. */
function pedidoCadastroModal() {
  const p = state.prospectCadastro;
  if (!p) return "";
  const texto = textoPedidoCadastro(p);
  return `
    <div class="client-drawer-overlay open modal-dim" onclick="fecharPedidoCadastro()">
      <div class="panel modal-panel" style="max-width:560px;margin:8vh auto;padding:22px"
           onclick="event.stopPropagation()">
        <div class="section-title">
          <div><h3>✅ Oficina registrada</h3>
            <div class="text-small">Mande estes dados para o setor de cadastro abrir a ficha no Alfa.</div></div>
          <button class="btn btn-ghost btn-sm" onclick="fecharPedidoCadastro()">Fechar</button>
        </div>
        <textarea readonly onclick="this.select()" rows="12"
          style="width:100%;font-family:inherit;font-size:13px;line-height:1.6;margin-top:10px"
          >${escapeHtml(texto)}</textarea>
        <div class="actions" style="margin-top:12px">
          <button class="btn btn-primary" onclick="copiarPedidoCadastro()">📋 Copiar dados</button>
          ${p.id ? `<button class="btn btn-secondary" onclick="baixarFichaCadastral(${p.id})">
            📄 Gerar ficha para assinar</button>` : ""}
          <button class="btn btn-ghost" onclick="fecharPedidoCadastro()">Depois eu mando</button>
        </div>
        <div class="text-small" style="color:var(--muted);margin-top:8px">
          A oficina ficou filtrada na lista atrás desta janela — é só fechar para vê-la.
        </div>
      </div>
    </div>`;
}

// ─── Ficha cadastral do cliente ────────────────────────────────────────────
//
// O vendedor sobe o comprovante do CNPJ, o formulário se preenche e a ficha
// sai em PDF para o cliente só assinar. O que a Receita não tem — inscrição
// estadual, e-mail de XML, WhatsApp e quem pode comprar — continua manual.

const FICHA_CONDICOES = ["À vista", "Faturado"];
const FICHA_RAMOS = [
  "Autopeças Leve", "Autopeças Pesada", "Autopeças Mista", "Auto Center",
  "Oficina Mecânica Leve", "Oficina Mecânica Pesada", "Oficina Mecânica Mista",
  "Transportadora", "Órgão Público", "Consumo Manut. Própria", "Outros",
];

async function importarComprovanteReceita(input) {
  const arquivo = input?.files?.[0];
  if (!arquivo) return;
  const p = state.prospectEditor;
  if (!p) return;
  p.importando = true; p.error = ""; requestRender();
  try {
    const form = new FormData();
    form.append("receita", arquivo, arquivo.name);
    const r = await api("/api/prospects/receita", { method: "POST", body: form });
    const d = r.data || {};
    // Só preenche o que veio; o que a pessoa já digitou não é sobrescrito por
    // vazio. Campo em branco no comprovante não pode apagar trabalho feito.
    Object.entries({
      companyName: d.companyName, tradeName: d.tradeName, documentNumber: d.documentNumber,
      addressLine: d.addressLine, addressNumber: d.addressNumber,
      addressComplement: d.addressComplement, neighborhood: d.neighborhood,
      cityName: d.cityName, stateName: d.stateName, postalCode: d.postalCode,
      landline: d.landline, email: d.email, emailFinance: d.emailFinance,
      businessLine: d.businessLine, cnaeCode: d.cnaeCode, openedAt: d.openedAt,
      registryStatus: d.registryStatus, businessLineHint: d.businessLineHint,
    }).forEach(([campo, valor]) => { if (valor) p[campo] = valor; });
    const quantos = Object.values(d).filter(Boolean).length;
    addMessage("success", `Comprovante lido — ${quantos} campo(s) preenchido(s). `
      + "Falta a inscrição estadual, que não vem da Receita.");
    if (d.registryStatus && d.registryStatus !== "ATIVA") {
      addMessage("warn", `Situação na Receita: ${d.registryStatus}. Confira antes de cadastrar.`);
    }
    // Este CNPJ já está na casa? Descobrir agora evita cadastrar de novo.
    p.existing = r.existing && r.existing.kind ? r.existing : null;
  } catch (e) {
    erroNoProspect(e.message);
  } finally {
    if (state.prospectEditor) state.prospectEditor.importando = false;
    input.value = "";
    requestRender();
  }
}

function baixarFichaCadastral(prospectId) {
  if (!prospectId) { addMessage("warn", "Salve a oficina antes de gerar a ficha."); return; }
  downloadFile(`/api/prospects/ficha.pdf?id=${encodeURIComponent(prospectId)}`);
}

function setFichaComprador(indice, valor) {
  const p = state.prospectEditor;
  if (!p) return;
  p.buyers = p.buyers || [];
  while (p.buyers.length < 3) p.buyers.push("");
  p.buyers[indice] = valor;
}

/** Abre e fecha o bloco da ficha.
 *
 *  Recebe o estado que está NA TELA porque o bloco também abre sozinho quando
 *  já tem dado preenchido. Invertendo só a preferência guardada, o primeiro
 *  clique numa ficha auto-aberta não fazia nada.
 */
function alternarFichaCadastral(abertoAgora) {
  state.ui.fichaAberta = !abertoAgora;
  requestRender();
}

/** Bloco da ficha cadastral: só o que NÃO aparece na parte de cima.
 *
 *  Antes cidade, bairro e endereço estavam aqui E lá em cima — a pessoa via o
 *  mesmo campo duas vezes e não sabia qual valia. Agora cada dado tem um lugar
 *  só, e o que é exclusivo da ficha fica recolhido: para prospectar bastam
 *  quatro campos, e a ficha só importa quando a oficina vai virar cliente.
 */
/** Aviso de CNPJ que já está na base, com a saída pronta.
 *
 *  Sem isto o vendedor preenchia a ficha inteira para descobrir depois — ou não
 *  descobrir — que a oficina já era cliente. E dois cadastros do mesmo CNPJ
 *  significam duas fichas circulando e o histórico dividido em dois lugares.
 */
function blocoJaExiste(e) {
  if (e.kind === "cliente") {
    return `
      <div class="message" style="background:#e6f4ea;color:#1e8e3e;margin-top:12px;
                  display:flex;gap:10px;align-items:center;flex-wrap:wrap">
        <span>✓</span>
        <div style="flex:1;min-width:220px">
          <strong>Este CNPJ já é cliente:</strong> ${escapeHtml(e.clientName)} (cód. ${escapeHtml(e.clientCode)})
          ${e.sellerName ? ` · carteira de ${escapeHtml(e.sellerName)}` : " · sem vendedor"}
          <div class="text-small">Não precisa cadastrar de novo — abra a ficha dele e imprima ali.</div>
        </div>
        <button class="btn btn-secondary btn-sm" type="button"
          onclick="fecharProspectEditor();openCrmClient('${jsAttr(e.clientCode)}', true)">Abrir ficha</button>
        <button class="btn btn-ghost btn-sm" type="button"
          onclick="imprimirFichaCliente('${jsAttr(e.clientCode)}')">📄 Imprimir ficha</button>
      </div>`;
  }
  return `
    <div class="message" style="background:#fef7e0;color:#b06000;margin-top:12px;
                display:flex;gap:10px;align-items:center;flex-wrap:wrap">
      <span>⚠</span>
      <div style="flex:1;min-width:220px">
        <strong>Já existe prospect com este CNPJ:</strong> ${escapeHtml(e.clientName)}
        ${e.sellerName ? ` · com ${escapeHtml(e.sellerName)}` : ""}
        <div class="text-small">Salvar de novo vai recusar por duplicidade.</div>
      </div>
      <button class="btn btn-secondary btn-sm" type="button"
        onclick="abrirProspectExistente(${e.prospectId}, '${jsAttr(e.clientName)}')">Abrir o existente</button>
    </div>`;
}

/** Ficha em PDF de um cliente já cadastrado. */
function imprimirFichaCliente(codigo) {
  if (!codigo) { addMessage("warn", "Cliente sem código no cadastro."); return; }
  downloadFile(`/api/crm/clients/ficha.pdf?code=${encodeURIComponent(codigo)}`);
}

/** Abre o prospect que já existe, em vez de criar um segundo. */
async function abrirProspectExistente(prospectId, nome) {
  const achado = (state.prospects?.prospects || []).find((x) => String(x.id) === String(prospectId));
  if (achado) { editarProspect(achado); return; }
  // Não está na lista carregada: filtra pelo nome e abre quando aparecer.
  fecharProspectEditor();
  state.prospectFilters.search = nome || "";
  state.prospectFilters.status = "";
  await loadProspects();
  const agora = (state.prospects?.prospects || []).find((x) => String(x.id) === String(prospectId));
  if (agora) editarProspect(agora);
  else addMessage("warn", "O cadastro existe, mas está com outro vendedor ou unidade.");
}

function blocoFichaCadastral(p) {
  const compradores = [...(p.buyers || []), "", "", ""].slice(0, 3);
  const daFicha = [p.paymentTerms, p.stateRegistration, p.addressLine, p.addressNumber,
                   p.postalCode, p.stateName, p.businessLine];
  const preenchidos = daFicha.filter((v) => normalizeTexto(v)).length;
  // Sem escolha da pessoa (null), abre sozinha quando já há dado preenchido.
  const aberto = state.ui.fichaAberta === null || state.ui.fichaAberta === undefined
    ? preenchidos > 0 : Boolean(state.ui.fichaAberta);

  return `
    <div class="subtle-card padded-card" style="margin-top:10px">
      <button type="button" onclick="alternarFichaCadastral(${aberto})"
        style="width:100%;display:flex;justify-content:space-between;align-items:center;
               background:transparent;border:none;cursor:pointer;padding:0">
        <span style="font-weight:700;font-size:14px">
          ${aberto ? "▾" : "▸"} Dados da ficha cadastral
        </span>
        <span class="text-small" style="color:${preenchidos === daFicha.length ? "var(--good)" : "var(--muted)"}">
          ${preenchidos} de ${daFicha.length} preenchidos
        </span>
      </button>
      <div class="text-small" style="color:var(--muted);margin-top:2px">
        Só precisa quando a oficina for virar cliente. Para prospectar, deixe para depois.
      </div>

      ${aberto ? `
        <div style="display:grid;grid-template-columns:1fr 1fr;gap:10px;margin-top:10px">
          <div class="field"><label>Condição <span style="color:var(--muted);font-weight:400">(análise de crédito)</span></label>
            <select onchange="state.prospectEditor.paymentTerms=this.value">
              <option value="">A definir</option>
              ${FICHA_CONDICOES.map((c) => `<option ${p.paymentTerms === c ? "selected" : ""}>${c}</option>`).join("")}
            </select></div>
          <div class="field"><label>Inscrição Estadual</label>
            <input value="${escapeHtml(p.stateRegistration || "")}"
              oninput="state.prospectEditor.stateRegistration=this.value"
              placeholder="Em branco = isento" />
            ${!normalizeTexto(p.stateRegistration) ? `
              <div class="text-small" style="color:#b06000;margin-top:4px">
                Sem inscrição, a ficha sai marcada como <strong>isento</strong>.
              </div>` : ""}</div>
        </div>

        <div style="display:grid;grid-template-columns:2fr 70px 1fr;gap:10px">
          <div class="field"><label>Endereço</label>
            <input value="${escapeHtml(p.addressLine || "")}" oninput="state.prospectEditor.addressLine=this.value" /></div>
          <div class="field"><label>Número</label>
            <input value="${escapeHtml(p.addressNumber || "")}" oninput="state.prospectEditor.addressNumber=this.value" /></div>
          <div class="field"><label>Complemento</label>
            <input value="${escapeHtml(p.addressComplement || "")}" oninput="state.prospectEditor.addressComplement=this.value" /></div>
        </div>

        <div style="display:grid;grid-template-columns:70px 1fr 2fr;gap:10px">
          <div class="field"><label>UF</label>
            <input maxlength="2" value="${escapeHtml(p.stateName || "")}"
              oninput="state.prospectEditor.stateName=this.value.toUpperCase()" /></div>
          <div class="field"><label>CEP</label>
            <input value="${escapeHtml(p.postalCode || "")}" oninput="state.prospectEditor.postalCode=this.value" /></div>
          <div class="field"><label>Ramo de atividade</label>
            <select onchange="state.prospectEditor.businessLine=this.value">
              <option value="">—</option>
              ${FICHA_RAMOS.map((r) => `<option ${p.businessLine === r ? "selected" : ""}>${r}</option>`).join("")}
            </select>
            ${p.businessLineHint && !p.businessLine ? `
              <div class="text-small" style="color:#b06000;margin-top:4px">
                O CNAE indica <strong>${escapeHtml(p.businessLineHint)}</strong>, mas não diz se é
                leve, pesada ou mista — escolha aqui.
              </div>`
            : p.cnaeCode ? `<div class="text-small" style="color:var(--muted);margin-top:4px">
                Sugerido pelo CNAE ${escapeHtml(p.cnaeCode)}.
              </div>` : ""}</div>
        </div>

        <div class="field"><label>Pessoas autorizadas a comprar</label>
          <div style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:10px">
            ${compradores.map((nome, i) => `
              <input value="${escapeHtml(nome)}" placeholder="Nome ${i + 1}"
                oninput="setFichaComprador(${i}, this.value)" />`).join("")}
          </div></div>` : ""}
    </div>`;
}

/** Texto sem espaços sobrando — usado só para decidir se um campo está vazio. */
function normalizeTexto(v) { return String(v || "").trim(); }

function prospectEditorModal() {
  const p = state.prospectEditor;
  const d = state.prospects || {};
  return `
    <div class="client-drawer-overlay open modal-dim" onclick="fecharProspectEditor()">
      <div class="panel modal-panel" data-keep-scroll="prospect-editor"
           style="max-width:720px;margin:5vh auto;padding:22px;max-height:90vh;overflow:auto"
           onclick="event.stopPropagation()">
        <div class="section-title">
          <div><h3>${p.id ? "Editar oficina" : "Nova oficina"}</h3>
            <div class="text-small">Oficina que ainda não está no cadastro do Alfa.</div></div>
          <button class="btn btn-ghost btn-sm" onclick="fecharProspectEditor()">Fechar</button>
        </div>

        <!-- Primeira ação da tela: é ela que preenche a maior parte do resto. -->
        <div style="display:flex;gap:8px;align-items:center;flex-wrap:wrap;
                    background:#f5f9ff;border:1px solid var(--accent);border-radius:10px;
                    padding:10px 12px;margin-top:12px">
          <label class="btn btn-primary btn-sm" style="margin:0;cursor:pointer">
            ${p.importando ? "⏳ Lendo…" : "📄 Importar comprovante do CNPJ"}
            <input type="file" accept=".pdf" style="display:none"
              onchange="importarComprovanteReceita(this)" ${p.importando ? "disabled" : ""} />
          </label>
          <span class="text-small" style="color:var(--muted);flex:1;min-width:220px">
            Imprima a consulta do CNPJ no site da Receita como PDF e solte aqui —
            preenche razão social, endereço, telefone e ramo de uma vez.
          </span>
          ${p.registryStatus ? `<span class="status-tag ${p.registryStatus === "ATIVA" ? "good" : "bad"}">
            Receita: ${escapeHtml(p.registryStatus)}</span>` : ""}
        </div>

        ${p.existing ? blocoJaExiste(p.existing) : ""}

        <div class="text-small" style="color:var(--muted);font-weight:700;margin:14px 0 4px">IDENTIFICAÇÃO</div>
        <div style="display:grid;grid-template-columns:2fr 1fr;gap:10px">
          <div class="field"><label>Nome da oficina <span style="color:var(--bad)">*</span></label>
            <input value="${escapeHtml(p.companyName)}" oninput="state.prospectEditor.companyName=this.value;state.prospectEditor.error=''" /></div>
          <div class="field"><label>Nome fantasia</label>
            <input value="${escapeHtml(p.tradeName)}" oninput="state.prospectEditor.tradeName=this.value" /></div>
        </div>

        <div class="field">
          <label>CNPJ <span style="color:var(--bad)">*</span>
            <span style="color:var(--muted);font-weight:400">(o mais importante)</span></label>
          <input value="${escapeHtml(p.documentNumber)}" oninput="state.prospectEditor.documentNumber=this.value;state.prospectEditor.error=''"
            placeholder="00.000.000/0000-00" />
          <div class="text-small" style="color:var(--accent)">
            É o CNPJ que faz o sistema reconhecer sozinho quando a oficina virar cliente e levar
            todo o seu histórico de ligações para a ficha dela.
          </div>
        </div>

        <div class="text-small" style="color:var(--muted);font-weight:700;margin:14px 0 4px">CONTATO</div>
        <div style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:10px">
          <div class="field"><label>WhatsApp <span style="color:var(--bad)">*</span></label>
            <input value="${escapeHtml(p.phone)}" oninput="state.prospectEditor.phone=this.value;state.prospectEditor.error=''" /></div>
          <div class="field"><label>Telefone fixo</label>
            <input value="${escapeHtml(p.landline || "")}" oninput="state.prospectEditor.landline=this.value" /></div>
          <div class="field"><label>Contato</label>
            <input value="${escapeHtml(p.contactName)}" oninput="state.prospectEditor.contactName=this.value"
              placeholder="Quem decide a compra" /></div>
        </div>
        <div style="display:grid;grid-template-columns:1fr 1fr;gap:10px">
          <div class="field"><label>E-mail <span style="color:var(--bad)">*</span></label>
            <input value="${escapeHtml(p.email)}" oninput="state.prospectEditor.email=this.value;state.prospectEditor.error=''" /></div>
          <div class="field"><label>E-mail para XML</label>
            <input value="${escapeHtml(p.emailXml || "")}" oninput="state.prospectEditor.emailXml=this.value"
              placeholder="Onde recebe a nota eletrônica" /></div>
        </div>

        <div class="text-small" style="color:var(--muted);font-weight:700;margin:14px 0 4px">ONDE FICA</div>
        <div style="display:grid;grid-template-columns:1fr 1fr;gap:10px">
          <div class="field"><label>Cidade</label>
            <input value="${escapeHtml(p.cityName)}" oninput="state.prospectEditor.cityName=this.value" /></div>
          <div class="field"><label>Bairro</label>
            <input value="${escapeHtml(p.neighborhood)}" oninput="state.prospectEditor.neighborhood=this.value" />
            <div class="text-small" style="color:var(--muted);margin-top:4px">
              Cidade e bairro definem a unidade que atende.
            </div></div>
        </div>

        ${d.canManage ? `
          <div style="display:grid;grid-template-columns:1fr 1fr;gap:10px">
            <div class="field">
              <label>Vendedor responsável <span style="color:var(--bad)">*</span></label>
              <select onchange="escolherVendedorProspect(this.value)">
                <option value="">Selecione…</option>
                ${(d.sellers || []).map((s) => `<option value="${escapeHtml(s)}" ${p.sellerName === s ? "selected" : ""}>${escapeHtml(s)}</option>`).join("")}
              </select>
              <div class="text-small" style="color:var(--muted);margin-top:4px">
                Define a unidade e é por ele que a equipe enxerga este prospect.
              </div></div>
            <div class="field"><label>Unidade</label>
              <select onchange="state.prospectEditor.unitName=this.value">
                <option value="">—</option>
                ${(d.units || []).map((u) => `<option value="${escapeHtml(u)}" ${p.unitName === u ? "selected" : ""}>${escapeHtml(u)}</option>`).join("")}
              </select>
              ${p.sellerName && p.unitName ? `<div class="text-small" style="color:var(--muted);margin-top:4px">
                Preenchida pelo cadastro de ${escapeHtml(p.sellerName)}.</div>` : ""}
            </div>
          </div>` : ""}

        <div class="subtle-card padded-card" style="margin-top:8px">
          <div class="section-title">
            <div><h3>As 4 perguntas</h3>
              <div class="text-small">Preencha durante a ligação. Com as quatro respostas mais um
                gatilho, o prospect vira <strong>qualificado</strong>.</div></div>
          </div>
          <div style="display:grid;grid-template-columns:1fr 1fr;gap:10px;margin-top:8px">
            <div class="field"><label>1. Manutenção rápida ou corretiva pesada?</label>
              <select onchange="state.prospectEditor.serviceType=this.value">
                <option value="">—</option>
                ${["Rápida", "Pesada", "Ambas"].map((o) => `<option ${p.serviceType === o ? "selected" : ""}>${o}</option>`).join("")}
              </select></div>
            <div class="field"><label>2. Carros por semana</label>
              <input type="number" min="0" value="${escapeHtml(String(p.carsWeek ?? ""))}"
                oninput="state.prospectEditor.carsWeek=this.value" /></div>
            <div class="field"><label>3. Onde mais gira peças?</label>
              <select onchange="state.prospectEditor.mainLine=this.value">
                <option value="">—</option>
                ${["Suspensão", "Freio", "Motor", "Transmissão", "Direção", "Outra"].map((o) => `<option ${p.mainLine === o ? "selected" : ""}>${o}</option>`).join("")}
              </select></div>
            <div class="field"><label>4. Como costuma pagar?</label>
              <select onchange="state.prospectEditor.payment=this.value">
                <option value="">—</option>
                ${["À vista/PIX", "Cartão", "Faturado"].map((o) => `<option ${p.payment === o ? "selected" : ""}>${o}</option>`).join("")}
              </select></div>
          </div>
          <div class="field" style="margin-top:4px">
            <label>Gatilho de fechamento aceito</label>
            <select onchange="state.prospectEditor.closingTrigger=this.value">
              <option value="">Ainda não fechei com nenhum</option>
              ${(d.triggers || []).map((t) => `<option value="${t.id}" ${p.closingTrigger === t.id ? "selected" : ""}>${escapeHtml(t.label)}</option>`).join("")}
            </select>
            <div class="text-small" style="color:var(--muted)">
              Sem gatilho, a prospecção não conta como válida no funil.
            </div>
          </div>
        </div>

        ${blocoFichaCadastral(p)}

        <div style="display:grid;grid-template-columns:1fr 2fr;gap:10px;margin-top:8px">
          <div class="field"><label>Como chegou até ela</label>
            <input value="${escapeHtml(p.origin)}" oninput="state.prospectEditor.origin=this.value"
              placeholder="Indicação, rua, lista, internet" /></div>
          <div class="field"><label>Observações</label>
            <input value="${escapeHtml(p.notes)}" oninput="state.prospectEditor.notes=this.value"
              placeholder="O que a oficina disse na ligação" />
            ${!d.canManage && !p.id ? `
              <div class="text-small" style="color:var(--muted);margin-top:4px">
                Preenchendo aqui, o sistema já registra a <strong>ligação de prospecção</strong>
                no seu nome — não precisa lançar o contato de novo.
              </div>` : ""}</div>
        </div>

        ${p.error ? `
          <div class="message error" style="margin-top:12px;display:flex;gap:8px;align-items:start">
            <span>⚠</span><span>${escapeHtml(p.error)}</span>
          </div>` : ""}

        <div class="actions" style="margin-top:14px">
          <button class="btn btn-primary" ${p.saving ? "disabled" : ""} onclick="salvarProspect()">
            ${p.saving ? "Salvando…" : "Salvar"}</button>
          ${p.id ? `<button class="btn btn-secondary" onclick="baixarFichaCadastral(${p.id})">
            📄 Gerar ficha para assinar</button>` : ""}
          <button class="btn btn-ghost" onclick="fecharProspectEditor()">Cancelar</button>
        </div>
      </div>
    </div>`;
}

// ─── Presença do assistente ────────────────────────────────────────────────
//
// Três níveis, porque "sempre visível" e "desligado" são extremos ruins: o
// primeiro atrapalha a leitura da tela, o segundo faz a pessoa esquecer que o
// recurso existe. O nível intermediário resolve o incômodo sem esconder a
// ferramenta. A escolha fica gravada no navegador, por usuário.

const ASSISTANT_MODES = ["normal", "discreto", "oculto"];

function assistantMode() {
  const salvo = safeStorageGet(assistantModeKey());
  return ASSISTANT_MODES.includes(salvo) ? salvo : "normal";
}

function assistantModeKey() {
  return `passini.assistant.mode.${state.user?.username || "anon"}`;
}

function setAssistantMode(modo) {
  safeStorageSet(assistantModeKey(), modo);
  if (modo !== "normal") state.ui.assistantBubble = false;
  if (modo === "oculto") state.ui.assistantOpen = false;
  state.ui.assistantMenuOpen = false;
  requestRender();
}

function toggleAssistantMenu(event) {
  if (event) { event.preventDefault(); event.stopPropagation(); }
  state.ui.assistantMenuOpen = !state.ui.assistantMenuOpen;
  requestRender();
}

/** localStorage pode estar bloqueado (aba anônima, política do navegador).
 *  Falhar aqui não pode derrubar a tela — o padrão volta a ser "normal". */
function safeStorageGet(chave) {
  try { return window.localStorage.getItem(chave); } catch (e) { return null; }
}

function safeStorageSet(chave, valor) {
  try { window.localStorage.setItem(chave, valor); } catch (e) { /* sem persistência */ }
}

function assistantFab() {
  if (!state.user) return "";
  const a = state.assistant;
  const novidades = a ? (a.situationTips || []).length + (a.pendingQuestions || []).length : 0;
  const modo = assistantMode();

  // Oculto: sobra uma aba fina na borda. Some da tela sem sumir do sistema —
  // desligar de vez faria a pessoa nunca mais achar o assistente.
  if (modo === "oculto") {
    return `
      <button class="as-tab-oculto" onclick="setAssistantMode('normal')"
        title="Mostrar o assistente novamente">
        💡${novidades ? `<span class="as-tab-badge">${novidades}</span>` : ""}
      </button>
      ${state.ui.assistantOpen ? assistantPanel() : ""}`;
  }

  const menu = state.ui.assistantMenuOpen ? `
    <div class="as-menu">
      <div class="as-menu-title">Assistente</div>
      ${[["normal", "Normal", "Balão de dica e selo de novidades"],
         ["discreto", "Discreto", "Menor e translúcido, sem balão"],
         ["oculto", "Ocultar", "Vira uma aba fina na lateral"]].map(([id, rotulo, ajuda]) => `
        <button class="as-menu-item ${modo === id ? "ativo" : ""}" onclick="setAssistantMode('${id}')">
          <strong>${rotulo}</strong>
          <span>${escapeHtml(ajuda)}</span>
        </button>`).join("")}
    </div>` : "";

  return `
    ${state.ui.assistantBubble && !state.ui.assistantOpen && modo === "normal" && a?.messageOfDay ? `
      <div class="as-bubble">
        <button class="as-bubble-close" onclick="event.stopPropagation();state.ui.assistantBubble=false;requestRender()"
          title="Dispensar" aria-label="Dispensar">×</button>
        <div onclick="toggleAssistant()" style="cursor:pointer">
          <strong>${escapeHtml(a.messageOfDay.title)}</strong><br />
          <span style="color:var(--muted)">Clique para ver a dica de hoje</span>
        </div>
      </div>` : ""}
    ${menu}
    <button class="as-fab ${modo === "discreto" ? "as-fab-discreto" : ""}"
      onclick="toggleAssistant()" oncontextmenu="toggleAssistantMenu(event)"
      title="Assistente Passini — clique direito para ocultar" aria-label="Abrir assistente">
      ${assistantAvatar(modo === "discreto" ? 30 : 44, true)}
      ${novidades && modo === "normal" ? `<span class="as-fab-badge">${novidades}</span>` : ""}
      <span class="as-fab-gear" onclick="toggleAssistantMenu(event)" title="Como o assistente aparece">⋯</span>
    </button>
    ${state.ui.assistantOpen ? assistantPanel() : ""}`;
}

function assistantPanel() {
  const a = state.assistant;
  if (!a) return `<div class="as-panel"><div class="as-body"><div class="loader">Carregando…</div></div></div>`;
  if (a.error) return `<div class="as-panel"><div class="as-body"><div class="message error">${escapeHtml(a.error)}</div></div></div>`;

  const aba = state.ui.assistantTab || "dicas";
  const abas = [
    { id: "dicas", label: "Dicas" },
    { id: "faq", label: "Dúvidas" },
    ...(a.canManage ? [{ id: "admin", label: `Gerenciar${(a.pendingQuestions || []).length ? ` (${a.pendingQuestions.length})` : ""}` }] : []),
  ];

  return `
    <div class="as-panel">
      <div class="as-head">
        ${assistantAvatar(44, true)}
        <div>
          <div class="as-title">Assistente Passini</div>
          <div class="as-sub">Dicas do MEC, dúvidas e atalhos</div>
        </div>
        <button class="as-close" onclick="toggleAssistant()" aria-label="Fechar">×</button>
      </div>

      <div class="as-tabs">
        ${abas.map((t) => `
          <button class="as-tab ${aba === t.id ? "active" : ""}" onclick="setAssistantTab('${t.id}')">${escapeHtml(t.label)}</button>`).join("")}
      </div>

      <div class="as-body">
        ${aba === "dicas" ? assistantTipsTab(a) : ""}
        ${aba === "faq" ? assistantFaqTab(a) : ""}
        ${aba === "admin" ? assistantAdminTab(a) : ""}
      </div>

      ${aba !== "admin" ? `
        <div class="as-ask">
          <input id="as-question" placeholder="Tem uma dúvida? Escreva aqui…"
            onkeydown="if(event.key==='Enter'){event.preventDefault();perguntarAssistente();}" />
          <button onclick="perguntarAssistente()">${state.ui.assistantSearching ? "…" : "Buscar"}</button>
        </div>` : ""}
    </div>`;
}

function assistantTipsTab(a) {
  const porTipo = (k) => (a.tips || []).filter((t) => t.kind === k && !t.trigger);
  return `
    ${a.messageOfDay ? `
      <div class="as-card">
        <h4>💬 ${escapeHtml(a.messageOfDay.title)}</h4>
        <p>${escapeHtml(a.messageOfDay.body)}</p>
      </div>` : ""}

    ${(a.situationTips || []).length ? `
      <div class="eyebrow" style="margin:14px 0 8px">PARA A SUA SITUAÇÃO DE HOJE</div>
      ${a.situationTips.map((t) => `
        <div class="as-card warn">
          <h4>${escapeHtml(t.title)}</h4>
          <p>${escapeHtml(t.body)}</p>
        </div>`).join("")}` : ""}

    ${["MEC", "DESEMPENHO", "LEMBRETE"].map((k) => {
      const itens = porTipo(k);
      if (!itens.length) return "";
      const cfg = (a.tipKinds || []).find((x) => x.id === k) || { label: k, icon: "•" };
      return `
        <div class="eyebrow" style="margin:14px 0 8px">${cfg.icon} ${escapeHtml(cfg.label).toUpperCase()}</div>
        ${itens.map((t) => `
          <div class="as-card acc">
            <h4>${escapeHtml(t.title)}</h4>
            <p>${escapeHtml(t.body)}</p>
          </div>`).join("")}`;
    }).join("")}

    <button class="btn btn-secondary btn-sm" style="width:100%;margin-top:10px" onclick="abrirTour(true)">
      ▶ Rever o tutorial do meu perfil
    </button>`;
}

function assistantFaqTab(a) {
  const resposta = state.ui.assistantAnswer;
  const categorias = a.faqCategories || [];
  return `
    ${resposta ? `
      <div style="margin-bottom:12px">
        <div class="text-small" style="color:var(--muted)">Você perguntou: “${escapeHtml(resposta.question)}”</div>
        ${resposta.results?.length ? `
          <div class="eyebrow" style="margin:8px 0">${resposta.results.length} resposta(s) encontrada(s)</div>
          ${resposta.results.map((r) => `
            <details class="as-q" open>
              <summary>${escapeHtml(r.question)}</summary>
              <div class="as-a">${escapeHtml(r.answer)}</div>
            </details>`).join("")}` : `
          <div class="as-card warn" style="margin-top:8px">
            <h4>Não encontrei essa resposta</h4>
            <p>Registrei sua pergunta para a diretoria responder. Quando ela for respondida,
               passa a aparecer aqui para todo mundo. Se for urgente, fale com seu gerente.</p>
          </div>`}
        <button class="btn btn-ghost btn-sm" style="margin-top:8px" onclick="limparRespostaAssistente()">
          Ver todas as dúvidas
        </button>
      </div>` : `
      <div class="text-small" style="color:var(--muted);margin-bottom:10px">
        Busca nas dúvidas cadastradas — não é um chat, é uma pesquisa por palavras.
      </div>
      ${categorias.map((cat) => {
        const itens = (a.faq || []).filter((f) => f.category === cat.id);
        if (!itens.length) return "";
        return `
          <div class="eyebrow" style="margin:14px 0 8px">${cat.icon} ${escapeHtml(cat.label).toUpperCase()}</div>
          ${itens.map((f) => `
            <details class="as-q">
              <summary>${escapeHtml(f.question)}</summary>
              <div class="as-a">${escapeHtml(f.answer)}</div>
            </details>`).join("")}`;
      }).join("")}`}`;
}

function assistantAdminTab(a) {
  const pendentes = a.pendingQuestions || [];
  return `
    <div class="eyebrow" style="margin-bottom:8px">DÚVIDAS SEM RESPOSTA (${pendentes.length})</div>
    ${pendentes.map((q) => `
      <div class="as-card warn">
        <h4>${escapeHtml(q.question)}</h4>
        <p style="color:var(--muted);font-size:12px">${escapeHtml(q.userName)} · ${escapeHtml(q.userRole)} · ${shortDate(q.createdAt)}</p>
        <textarea id="as-ans-${q.id}" rows="3" style="width:100%;margin-top:8px;font-family:inherit;font-size:13px;
          border:1px solid var(--line);border-radius:8px;padding:8px" placeholder="Escreva a resposta…"></textarea>
        <label class="check-row" style="margin-top:6px;font-size:12px">
          <input type="checkbox" id="as-pub-${q.id}" checked />
          <span>Publicar no FAQ para todos</span>
        </label>
        <div class="actions" style="gap:6px;margin-top:8px">
          <button class="btn btn-primary btn-sm" onclick="responderDuvida(${q.id})">Responder</button>
          <button class="btn btn-ghost btn-sm" onclick="descartarDuvida(${q.id})">Descartar</button>
        </div>
      </div>`).join("") || '<div class="text-small" style="color:var(--muted)">Nenhuma dúvida esperando resposta.</div>'}

    <div class="eyebrow" style="margin:18px 0 8px">CONTEÚDO</div>
    <div class="actions" style="gap:6px;flex-wrap:wrap">
      <button class="btn btn-secondary btn-sm" onclick="novaDica()">＋ Nova dica</button>
      <button class="btn btn-secondary btn-sm" onclick="novoFaq()">＋ Nova dúvida no FAQ</button>
    </div>
    <div class="text-small" style="color:var(--muted);margin-top:8px">
      ${(a.allTips || []).length} dica(s) e ${(a.allFaq || []).length} pergunta(s) cadastradas.
      As criadas por você ficam marcadas como MANUAL e não são sobrescritas por atualizações do sistema.
    </div>
    <div class="stack" style="margin-top:10px">
      ${(a.allTips || []).filter((t) => t.source === "MANUAL").map((t) => `
        <div style="display:flex;justify-content:space-between;gap:8px;font-size:12px;
                    padding:6px 10px;background:#f8f9fa;border-radius:6px">
          <span>${escapeHtml(t.title)}</span>
          <span style="display:flex;gap:4px">
            <button class="btn btn-ghost btn-sm" onclick='editarDica(${JSON.stringify(t).replace(/'/g, "&#39;")})'>Editar</button>
            <button class="btn btn-ghost btn-sm" onclick="excluirDica(${t.id})">Excluir</button>
          </span>
        </div>`).join("")}
    </div>`;
}

async function responderDuvida(questionId) {
  const texto = document.getElementById(`as-ans-${questionId}`)?.value.trim() || "";
  const publicar = document.getElementById(`as-pub-${questionId}`)?.checked;
  if (!texto) { addMessage("error", "Escreva a resposta."); return; }
  try {
    await api("/api/help/question/answer", {
      method: "POST", body: JSON.stringify({ questionId, answer: texto, publish: publicar }),
    });
    addMessage("success", publicar ? "Respondida e publicada no FAQ." : "Respondida.");
    await loadAssistant();
  } catch (e) { addMessage("error", e.message); }
}

async function descartarDuvida(questionId) {
  try {
    await api("/api/help/question/answer", {
      method: "POST", body: JSON.stringify({ questionId, discard: true }),
    });
    await loadAssistant();
  } catch (e) { addMessage("error", e.message); }
}

function novaDica() {
  state.helpEditor = { type: "tip", id: null, kind: "MENSAGEM", title: "", body: "",
                       roles: "", trigger: "", saving: false };
  requestRender();
}
function editarDica(t) {
  state.helpEditor = { type: "tip", ...t, saving: false };
  requestRender();
}
function novoFaq() {
  state.helpEditor = { type: "faq", id: null, category: "dia-a-dia", question: "", answer: "",
                       keywords: "", roles: "", saving: false };
  requestRender();
}
function fecharHelpEditor() { state.helpEditor = null; requestRender(); }

async function salvarHelpEditor() {
  const h = state.helpEditor;
  if (!h) return;
  h.saving = true; requestRender();
  try {
    const rota = h.type === "tip" ? "/api/help/tip/save" : "/api/help/article/save";
    await api(rota, { method: "POST", body: JSON.stringify(h) });
    addMessage("success", "Conteúdo salvo.");
    state.helpEditor = null;
    await loadAssistant();
  } catch (e) {
    addMessage("error", e.message);
    if (state.helpEditor) state.helpEditor.saving = false;
    requestRender();
  }
}

async function excluirDica(tipId) {
  if (!confirm("Excluir esta dica?")) return;
  try {
    await api("/api/help/tip/delete", { method: "POST", body: JSON.stringify({ tipId }) });
    await loadAssistant();
  } catch (e) { addMessage("error", e.message); }
}

function helpEditorModal() {
  const h = state.helpEditor;
  if (!h) return "";
  const a = state.assistant || {};
  return `
    <div class="client-drawer-overlay open modal-dim" onclick="fecharHelpEditor()" style="z-index:95">
      <div class="panel modal-panel" style="max-width:560px;margin:8vh auto;padding:22px" onclick="event.stopPropagation()">
        <div class="section-title">
          <div><h3>${h.type === "tip" ? (h.id ? "Editar dica" : "Nova dica") : (h.id ? "Editar dúvida" : "Nova dúvida no FAQ")}</h3></div>
          <button class="btn btn-ghost btn-sm" onclick="fecharHelpEditor()">Fechar</button>
        </div>
        ${h.type === "tip" ? `
          <div style="display:grid;grid-template-columns:1fr 1fr;gap:10px;margin-top:10px">
            <div class="field"><label>Tipo</label>
              <select onchange="state.helpEditor.kind=this.value">
                ${(a.tipKinds || []).map((k) => `<option value="${k.id}" ${h.kind === k.id ? "selected" : ""}>${k.icon} ${escapeHtml(k.label)}</option>`).join("")}
              </select></div>
            <div class="field"><label>Para quais perfis</label>
              <select onchange="state.helpEditor.roles=this.value">
                <option value="" ${!h.roles ? "selected" : ""}>Todos</option>
                <option value="VENDEDOR" ${h.roles === "VENDEDOR" ? "selected" : ""}>Só vendedores</option>
                <option value="GERENTE DIRETOR" ${h.roles === "GERENTE DIRETOR" ? "selected" : ""}>Gestão</option>
              </select></div>
          </div>
          <div class="field"><label>Título</label>
            <input value="${escapeHtml(h.title)}" oninput="state.helpEditor.title=this.value" /></div>
          <div class="field"><label>Texto</label>
            <textarea rows="4" style="font-family:inherit" oninput="state.helpEditor.body=this.value">${escapeHtml(h.body)}</textarea></div>
        ` : `
          <div style="display:grid;grid-template-columns:1fr 1fr;gap:10px;margin-top:10px">
            <div class="field"><label>Categoria</label>
              <select onchange="state.helpEditor.category=this.value">
                ${(a.faqCategories || []).map((c) => `<option value="${c.id}" ${h.category === c.id ? "selected" : ""}>${escapeHtml(c.label)}</option>`).join("")}
              </select></div>
            <div class="field"><label>Para quais perfis</label>
              <select onchange="state.helpEditor.roles=this.value">
                <option value="" ${!h.roles ? "selected" : ""}>Todos</option>
                <option value="VENDEDOR" ${h.roles === "VENDEDOR" ? "selected" : ""}>Só vendedores</option>
                <option value="GERENTE DIRETOR" ${h.roles === "GERENTE DIRETOR" ? "selected" : ""}>Gestão</option>
              </select></div>
          </div>
          <div class="field"><label>Pergunta</label>
            <input value="${escapeHtml(h.question)}" oninput="state.helpEditor.question=this.value"
              placeholder="Escreva como a pessoa perguntaria" /></div>
          <div class="field"><label>Resposta</label>
            <textarea rows="4" style="font-family:inherit" oninput="state.helpEditor.answer=this.value">${escapeHtml(h.answer)}</textarea></div>
          <div class="field"><label>Palavras que levam a esta resposta</label>
            <input value="${escapeHtml(h.keywords)}" oninput="state.helpEditor.keywords=this.value"
              placeholder="senha login não entro acesso bloqueado" />
            <div class="text-small" style="color:var(--muted)">
              Escreva do jeito que a equipe fala. É por aqui que a busca encontra.
            </div></div>
        `}
        <div class="actions" style="margin-top:12px">
          <button class="btn btn-primary" ${h.saving ? "disabled" : ""} onclick="salvarHelpEditor()">
            ${h.saving ? "Salvando…" : "Salvar"}</button>
          <button class="btn btn-ghost" onclick="fecharHelpEditor()">Cancelar</button>
        </div>
      </div>
    </div>`;
}

// ─── Tutorial guiado ────────────────────────────────────────────────────────
//
// Passos em janela, não balões apontando para elementos da tela. Balão preso a
// um elemento quebra quando o layout muda, e este sistema muda toda semana.
// A janela sobrevive a qualquer mudança e ainda leva a pessoa para a tela real
// quando ela clica em "Ir para esta tela".

function abrirTour(manual) {
  const a = state.assistant;
  if (!a || !(a.tour || []).length) return;
  state.ui.tourStep = 0;
  state.ui.tourOpen = true;
  state.ui.tourManual = Boolean(manual);
  state.ui.assistantOpen = false;
  requestRender();
}

function passoTour(delta) {
  const total = (state.assistant?.tour || []).length;
  const novo = (state.ui.tourStep || 0) + delta;
  if (novo < 0) return;
  if (novo >= total) { concluirTour(false); return; }
  state.ui.tourStep = novo;
  requestRender();
}

async function concluirTour(pulou) {
  const a = state.assistant;
  state.ui.tourOpen = false;
  requestRender();
  // Só registra quando o tour abriu sozinho. Rever pelo assistente não deve
  // alterar o histórico de quem já tinha concluído.
  if (!state.ui.tourManual && a?.tourKey) {
    try {
      await api("/api/help/tour", {
        method: "POST", body: JSON.stringify({ tourKey: a.tourKey, skipped: Boolean(pulou) }),
      });
      state.assistant.tourSeen = true;
    } catch (e) { /* não impede o uso do sistema */ }
  }
}

function irParaTelaDoTour(tab) {
  if (tab) { state.activeTab = tab; }
  passoTour(1);
}

function tourOverlay() {
  if (!state.ui.tourOpen) return "";
  const a = state.assistant;
  const passos = a?.tour || [];
  const i = Math.min(state.ui.tourStep || 0, passos.length - 1);
  const p = passos[i];
  if (!p) return "";
  const ultimo = i === passos.length - 1;

  return `
    <div class="as-tour-overlay">
      <div class="as-tour">
        <div class="as-tour-head">
          ${assistantAvatar(62, true)}
          <div>
            <div class="as-step-n">PASSO ${i + 1} DE ${passos.length}</div>
            <h3>${p.icon ? p.icon + " " : ""}${escapeHtml(p.title)}</h3>
          </div>
        </div>
        <div class="as-tour-body">
          ${escapeHtml(p.body)}
          ${p.hint ? `<div class="as-tour-hint">💡 ${escapeHtml(p.hint)}</div>` : ""}
        </div>
        <div class="as-tour-foot">
          <div class="as-dots">
            ${passos.map((_, k) => `<span class="as-dot ${k === i ? "on" : ""}"></span>`).join("")}
          </div>
          ${i > 0 ? `<button class="btn btn-ghost btn-sm" onclick="passoTour(-1)">Voltar</button>` : ""}
          ${!ultimo ? `<button class="btn btn-ghost btn-sm" onclick="concluirTour(true)">Pular</button>` : ""}
          ${p.tab && !ultimo
            ? `<button class="btn btn-secondary btn-sm" onclick="irParaTelaDoTour('${p.tab}')">Ir para esta tela</button>`
            : ""}
          <button class="btn btn-primary btn-sm" onclick="${ultimo ? "concluirTour(false)" : "passoTour(1)"}">
            ${ultimo ? "Começar a usar" : "Próximo"}
          </button>
        </div>
      </div>
    </div>`;
}

function loginView() {
  return `
    <div class="pl-shell">
      <aside class="pl-brand">
        <div class="pl-mark">
          <!-- Logo original, sem qualquer alteração. A placa branca existe porque
               a arte tem fundo claro: sobre o índigo ela ficaria com um retângulo
               esbranquiçado em volta. Assim o logo aparece exatamente como é. -->
          <div class="pl-logo-plate">
            <img src="/logo.png" alt="Passini Distribuidora de Peças"
              onerror="this.closest('.pl-logo-plate').style.display='none';document.getElementById('pl-mark-fallback').style.display='block'" />
          </div>
          <div class="pl-mark-text" id="pl-mark-fallback" style="display:none">
            <div class="pl-name">PASSINI</div>
            <div class="pl-sub">DISTRIBUIDORA DE PEÇAS</div>
          </div>
        </div>

        <div>
          <div class="pl-eyebrow">MEC · Método de Execução Comercial</div>
          <h1 class="pl-headline">
            A venda não acontece por acaso.<br />
            Ela acontece <em>por método</em>.
          </h1>
        </div>

        <div class="pl-rotator">
          <p>Abra o CRM. Faça a primeira tarefa da fila. Registre o que aconteceu e marque o próximo passo.</p>
          <p>São 5 contatos por dia — 2 Bronze/Prata, 2 Ouro/Diamante e 1 prospecção. Cinco, não oito.</p>
          <p>Contato sem registro válido não conta. Atendimento sem próxima ação continua aberto.</p>
          <p>Orçamento enviado não é orçamento terminado. Ligue e pergunte o que falta para fechar.</p>
        </div>

        <div>
          <div class="pl-cycle-label">O ciclo de cada atendimento</div>
          <div class="pl-cycle">
            <span class="pl-step">ABRIR</span>
            <span class="pl-step">PREPARAR</span>
            <span class="pl-step">FAZER</span>
            <span class="pl-step">REGISTRAR</span>
            <span class="pl-step">MARCAR</span>
            <span class="pl-step">CONCLUIR</span>
          </div>
        </div>

        <div class="pl-foot">
          Carteira, metas, visitas, reuniões e desenvolvimento — a operação comercial em um só lugar.
        </div>
      </aside>

      <main class="pl-panel">
        <form class="pl-form" onsubmit="handleLogin(event)">
          <div>
            <h2>Bom trabalho hoje.</h2>
            <p class="pl-hint">Entre para ver sua fila do dia.</p>
          </div>

          ${messageHtml()}

          <div class="pl-field">
            <label>Usuário</label>
            <input autocomplete="username" value="${escapeHtml(state.login.username)}"
              oninput="state.login.username=this.value" required autofocus />
          </div>
          <div class="pl-field">
            <label>Senha</label>
            <input type="password" autocomplete="current-password" value="${escapeHtml(state.login.password)}"
              oninput="state.login.password=this.value" required />
          </div>

          <button class="pl-submit" type="submit">Entrar</button>

          <div class="pl-rule">
            <strong>Regra de ouro:</strong> ligar sem proposta é desperdício.
            Uma oferta e uma pergunta em cada contato.
          </div>

          <div class="pl-help">Esqueceu a senha? Fale com o administrador do sistema.</div>
        </form>
      </main>
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

/**
 * Farol de indicador: cor + ícone + rótulo.
 *
 * A cor NUNCA aparece sozinha — cerca de 8% dos homens não distinguem vermelho
 * de verde. O ícone (▲ ◆ ▼) e o texto garantem a leitura para todos, conforme
 * as diretrizes de acessibilidade WCAG.
 */
function farolBadge(farol, { compact = false } = {}) {
  if (!farol || !farol.level || farol.level === "neutral") return "";
  const titulo = farol.detail || farol.hint || farol.label;
  if (compact) {
    return `<span title="${escapeHtml(titulo)}" style="color:${farol.color};font-weight:800;margin-left:4px">${farol.icon}</span>`;
  }
  return `
    <span title="${escapeHtml(titulo)}"
      style="display:inline-flex;align-items:center;gap:4px;background:${farol.bg};color:${farol.color};
             border-radius:12px;padding:2px 8px;font-size:11px;font-weight:800;white-space:nowrap">
      ${farol.icon} ${escapeHtml(farol.label)}
    </span>`;
}

/** Aplica a cor do farol diretamente no número, mantendo o ícone ao lado. */
function farolValue(value, farol) {
  if (!farol || !farol.level || farol.level === "neutral") return value;
  return `<span style="color:${farol.color}" title="${escapeHtml(farol.detail || farol.hint || "")}">${value} ${farol.icon}</span>`;
}

/** KPI que abre um detalhe. Mesma aparência dos vizinhos, com o convite no pé. */
function kpiCardClicavel(title, value, chamada, onclick) {
  return `
    <button type="button" class="kpi-card" onclick="${onclick}"
      style="text-align:left;cursor:pointer;font:inherit;width:100%;display:block">
      <div style="display:flex;align-items:center;justify-content:space-between;gap:6px">
        <span>${title}</span>
      </div>
      <strong>${value}</strong>
      <div class="kpi-foot">
        <span style="color:var(--accent);font-weight:600">${escapeHtml(chamada)} →</span>
      </div>
    </button>`;
}

function kpiCard(title, value, footLeft, footRight, farol) {
  const temFarol = farol && farol.level && farol.level !== "neutral";
  return `
    <div class="kpi-card" ${temFarol ? `style="border-left:4px solid ${farol.color}"` : ""}>
      <div style="display:flex;align-items:center;justify-content:space-between;gap:6px">
        <span>${title}</span>
        ${temFarol ? farolBadge(farol) : ""}
      </div>
      <strong ${temFarol ? `style="color:${farol.color}"` : ""}>${value}</strong>
      <div class="kpi-foot">
        <span>${footLeft || ""}</span>
        <span>${footRight || ""}</span>
      </div>
      ${temFarol && farol.detail ? `<div class="text-small" style="color:var(--muted);margin-top:2px;font-size:10px">${escapeHtml(farol.detail)}</div>` : ""}
    </div>
  `;
}

/** Legenda do farol — explica o critério para quem olha a tela pela primeira vez. */
// Motivo da devolução, direto do relatório do Alfa. O valor total do painel vem
// do custo x venda; esta lista existe para explicar de onde ele veio — e é o
// motivo, não o valor, que aponta o que dá para corrigir na venda.
function blocoMotivosDevolucao(s) {
  const motivos = Array.isArray(s.returnsByReason) ? s.returnsByReason : [];
  if (!motivos.length) return "";
  const totalMotivos = motivos.reduce((soma, m) => soma + Number(m.value || 0), 0);
  const linhas = motivos.map((m) => {
    const fatia = totalMotivos ? (100 * Number(m.value || 0)) / totalMotivos : 0;
    const ehGarantia = m.kind === "garantia";
    return `
      <div style="display:flex;align-items:center;gap:8px;min-width:210px">
        <span style="width:8px;height:8px;border-radius:50%;flex:none;background:${
          ehGarantia ? "#e67e22" : "var(--accent)"}"></span>
        <span class="text-small" style="flex:1">${m.reason}
          <span style="color:var(--muted)"> · ${ehGarantia ? "garantia" : "comercial"}</span></span>
        <strong class="text-small">${currency(m.value || 0)}</strong>
        <span class="text-small" style="color:var(--muted);width:44px;text-align:right">${
          fatia.toFixed(0)}%</span>
      </div>`;
  }).join("");
  return `
    <div style="margin-top:10px;padding-top:10px;border-top:1px solid var(--border)">
      <div class="text-small" style="color:var(--muted);margin-bottom:6px">
        POR MOTIVO — ${number(motivos.length)} motivo(s) no relatório de devoluções
      </div>
      <div style="display:flex;gap:16px;flex-wrap:wrap">${linhas}</div>
    </div>`;
}

function farolLegend(paceExpectedPct) {
  return `
    <div class="form-card" style="padding:10px 16px">
      <div style="display:flex;gap:16px;flex-wrap:wrap;align-items:center">
        <span style="font-size:11px;font-weight:800;color:var(--muted);letter-spacing:0.06em">FAROL</span>
        <span style="display:inline-flex;align-items:center;gap:4px;font-size:12px"><span style="color:#1e8e3e;font-weight:800">▲</span> No ritmo</span>
        <span style="display:inline-flex;align-items:center;gap:4px;font-size:12px"><span style="color:#b06000;font-weight:800">◆</span> Atenção</span>
        <span style="display:inline-flex;align-items:center;gap:4px;font-size:12px"><span style="color:#c5221f;font-weight:800">▼</span> Crítico</span>
        ${paceExpectedPct != null ? `
          <span class="text-small" style="color:var(--muted);margin-left:auto">
            A meta é comparada com o <strong>ritmo esperado até hoje</strong> (${pct(paceExpectedPct)} do mês decorrido),
            não com os 100% do fechamento.
          </span>` : ""}
      </div>
    </div>`;
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

/** Situação do vínculo do vendedor no mês.
 *
 *  "Pendente" significa que ninguém cadastrou a pessoa em Administração →
 *  Pessoas: é tarefa aberta. Quem foi desligado não é pendência — o registro
 *  existe e está fechado. Misturar os dois fazia o gestor procurar problema
 *  onde já estava resolvido.
 */
function seloVinculoVendedor(row) {
  if (row.terminated) {
    return '<span class="status-tag" style="background:#f1f3f4;color:#5f6368"'
      + ' title="Desligado: sem vínculo vigente nesta competência">Desligado</span>';
  }
  if (row.pendingMapping) {
    return '<span class="status-tag warn"'
      + ' title="Sem cadastro em Administração → Pessoas">Pendente</span>';
  }
  return "";
}

// ─── Clientes faturados no mês, com o dono da carteira ─────────────────────
//
// Abre a partir dos números "Carteira" e "Fora" do ranking — que é onde a
// pergunta "quais clientes são esses?" nasce. Sai em PDF para levar impresso à
// conversa e em CSV para o gestor cruzar do jeito dele.

async function abrirClientesDoVendedor(vendedor, escopo) {
  // Sem vendedor definido, abre com o seletor: é o caminho de quem chegou pelo
  // botão do topo, sem ter clicado num número de alguém.
  if (!vendedor && !roleIsSeller()) {
    state.sellerClients = { loading: false, sellerName: "", scope: escopo || "todos",
                            items: [], totals: {}, precisaEscolher: true };
    requestRender();
    return;
  }
  state.sellerClients = { loading: true, sellerName: vendedor, scope: escopo || "todos" };
  requestRender();
  try {
    const q = new URLSearchParams({ seller: vendedor, scope: escopo || "todos" });
    const mes = state.filters.competenceEnd || state.filters.competenceStart;
    if (mes) q.set("competence", mes);
    const r = await api(`/api/crm/seller-clients?${q.toString()}`);
    state.sellerClients = { ...r, loading: false, scope: escopo || "todos" };
  } catch (e) {
    state.sellerClients = { error: e.message, loading: false, sellerName: vendedor, items: [] };
  }
  requestRender();
}

function fecharClientesDoVendedor() {
  state.sellerClients = null;
  requestRender();
}

function trocarEscopoClientesVendedor(escopo) {
  const d = state.sellerClients;
  if (d && !d.loading) abrirClientesDoVendedor(d.sellerName, escopo);
}

function baixarClientesDoVendedor(formato) {
  const d = state.sellerClients;
  if (!d || !d.sellerName) return;
  const q = new URLSearchParams({ seller: d.sellerName, scope: d.scope || "todos" });
  if (d.competence) q.set("competence", d.competence);
  downloadFile(`/api/crm/seller-clients.${formato}?${q.toString()}`);
}

function clientesDoVendedorModal() {
  const d = state.sellerClients;
  if (!d) return "";
  const t = d.totals || {};
  const itens = d.items || [];
  const aba = (id, rotulo, contador) => `
    <button type="button" onclick="trocarEscopoClientesVendedor('${id}')"
      ${d.loading ? "disabled" : ""}
      style="border:1px solid ${d.scope === id ? "var(--accent)" : "var(--line)"};
             background:${d.scope === id ? "#e8f0fe" : "#fff"};
             color:${d.scope === id ? "var(--accent)" : "var(--muted)"};
             border-radius:14px;padding:5px 14px;font-size:12px;
             font-weight:${d.scope === id ? "700" : "500"};cursor:pointer">
      ${rotulo}${contador != null ? ` (${number(contador)})` : ""}
    </button>`;

  return `
    <div class="client-drawer-overlay open modal-dim" onclick="fecharClientesDoVendedor()">
      <div class="panel modal-panel" style="max-width:1000px;margin:5vh auto;padding:22px;
                  max-height:90vh;overflow:auto" onclick="event.stopPropagation()">
        <div class="section-title">
          <div><h3>Clientes faturados no mês</h3>
            <div class="text-small">${escapeHtml(d.sellerName || "")}
              ${d.competence ? ` · ${escapeHtml(d.competence)}` : ""}</div></div>
          <button class="btn btn-ghost btn-sm" onclick="fecharClientesDoVendedor()">Fechar</button>
        </div>

        ${d.error ? `<div class="message error" style="margin-top:10px">${escapeHtml(d.error)}</div>` : ""}
        ${d.loading ? '<div class="loader">Carregando…</div>' : ""}

        ${vendedoresParaRelatorio().length ? `
          <div class="field" style="margin-top:10px;max-width:360px">
            <label>Vendedor</label>
            <select onchange="abrirClientesDoVendedor(this.value, '${d.scope || "todos"}')">
              <option value="">Escolha o vendedor…</option>
              ${vendedoresParaRelatorio().map((v) => `
                <option value="${escapeHtml(v)}" ${d.sellerName === v ? "selected" : ""}>${escapeHtml(v)}</option>`).join("")}
            </select>
          </div>` : ""}

        ${d.precisaEscolher ? `
          <div class="message" style="background:#e8f0fe;color:var(--accent);margin-top:10px">
            Escolha um vendedor acima para ver os clientes que ele faturou no mês.
          </div>` : ""}

        <div style="display:flex;gap:8px;flex-wrap:wrap;align-items:center;margin:12px 0">
          ${aba("todos", "Todos", t.clients)}
          ${aba("carteira", "Da carteira dele", t.ownClients)}
          ${aba("fora", "Fora da carteira", t.otherClients)}
          <span style="flex:1"></span>
          <button class="btn btn-secondary btn-sm" onclick="baixarClientesDoVendedor('csv')">⬇ CSV</button>
          <button class="btn btn-secondary btn-sm" onclick="baixarClientesDoVendedor('pdf')">📄 PDF</button>
        </div>

        ${avisoDivergenciaFaturamento(d)}

        <div style="display:flex;gap:10px;flex-wrap:wrap;margin-bottom:10px">
          ${[["Faturado no mês", currency(t.revenue), `${number(t.clients)} cliente(s)`],
             ["Da carteira dele", currency(t.ownRevenue), `${number(t.ownClients)} cliente(s)`],
             ["Fora da carteira", currency(t.otherRevenue), `${number(t.otherClients)} cliente(s)`],
             ["Sem vendedor no cadastro", currency(t.noOwnerRevenue), `${number(t.noOwnerClients)} cliente(s)`]]
            .map(([rot, val, sub]) => `
              <div style="flex:1;min-width:150px;background:#fff;border:1px solid var(--line);
                          border-radius:10px;padding:9px 11px">
                <div class="text-small" style="color:var(--muted)">${rot}</div>
                <div style="font-size:17px;font-weight:800">${val}</div>
                <div class="text-small" style="color:var(--muted)">${sub}</div>
              </div>`).join("")}
        </div>

        <div class="table-wrap">
          <table class="data-table">
            <thead><tr>
              <th>Código</th><th>Cliente</th><th>Cidade</th><th>Carteira de</th>
              <th style="text-align:right">Faturamento</th>
              <th style="text-align:right">Itens</th>
              <th>Última compra</th>
            </tr></thead>
            <tbody>
              ${itens.map((i) => `
                <tr>
                  <td class="text-small">${escapeHtml(i.clientCode || "—")}</td>
                  <td><strong>${escapeHtml(i.clientName)}</strong></td>
                  <td class="text-small">${escapeHtml(i.cityName || "—")}</td>
                  <td>${seloCarteira(i)}</td>
                  <td style="text-align:right">${currency(i.revenue)}</td>
                  <td style="text-align:right">${number(i.items)}</td>
                  <td class="text-small">${i.lastPurchaseAt ? shortDate(i.lastPurchaseAt) : "—"}</td>
                </tr>`).join("")
                || (d.loading ? "" : `<tr><td colspan="7">
                     ${emptyStateCard("Nenhum cliente faturado neste recorte.")}</td></tr>`)}
            </tbody>
          </table>
        </div>
      </div>
    </div>`;
}

/** Número clicável: abre a lista dos clientes por trás dele. */
function celulaCarteiraVendedor(row, escopo, valor) {
  const n = Number(valor || 0);
  if (!n) return "0";
  return `<button type="button" class="link-num"
    title="Ver os clientes e exportar"
    onclick="abrirClientesDoVendedor('${jsAttr(row.sellerName)}', '${escopo}')">${number(n)}</button>`;
}

/** Compara a soma da lista com o número oficial do vendedor.
 *
 *  A lista vem do faturamento DETALHADO; o ranking do dashboard vem do
 *  relatório de custo x venda. Quando as duas fontes discordam, mostrar só uma
 *  faz o gestor achar que o sistema mente. Melhor dizer que discordam, de
 *  quanto, e o que fazer.
 */
function avisoDivergenciaFaturamento(d) {
  const detalhe = Number(d?.totals?.revenue || 0);
  const oficial = Number(d?.officialRevenue || 0);
  if (!oficial || !detalhe) return "";
  const dif = detalhe - oficial;
  if (Math.abs(dif) / oficial <= 0.02) return "";   // até 2% é arredondamento
  return `
    <div class="message" style="background:#fef7e0;color:#b06000;margin-bottom:10px;line-height:1.55">
      <strong>⚠ Esta lista soma ${currency(detalhe)}, mas o resultado oficial do vendedor
      no mês é ${currency(oficial)}</strong> — diferença de ${currency(Math.abs(dif))}
      (${(Math.abs(dif) / oficial * 100).toFixed(0)}%).
      <div class="text-small" style="margin-top:4px">
        A lista vem do faturamento detalhado; o ranking vem do relatório de custo x venda.
        Diferença acima de 2% costuma ser linha repetida no detalhado — rode
        <code>diag_marcas.py</code> no servidor para medir. Use os nomes e a coluna
        <strong>Carteira de</strong>, que não dependem disso.
      </div>
    </div>`;
}

/** Vendedores que o gestor pode consultar. O vendedor não escolhe: é ele. */
function vendedoresParaRelatorio() {
  if (roleIsSeller()) return [];
  return (state.dashboard?.sellerRanking || [])
    .map((r) => r.sellerName)
    .filter(Boolean);
}

/** De quem é o cliente. É a coluna que dá sentido ao relatório. */
function seloCarteira(item) {
  if (item.isOwn) {
    return '<span class="status-tag good">própria</span>';
  }
  if (item.portfolioSeller === "Sem vendedor") {
    return '<span class="status-tag" style="background:#f1f3f4;color:#5f6368"'
      + ' title="Cliente sem vendedor interno no cadastro">Sem vendedor</span>';
  }
  return `<span class="status-tag" style="background:#fef7e0;color:#b06000"
    title="Cliente da carteira de outro vendedor">${escapeHtml(item.portfolioSeller)}</span>`;
}

function sellerRows(rows) {
  return rows
    .map(
      (row) => `
      <tr>
        <td>${escapeHtml(row.sellerName)} ${seloVinculoVendedor(row)}</td>
        <td>${escapeHtml(row.baseUnit || "-")}</td>
        <td>${currency(row.revenueNet)}</td>
        <td>${currency(row.revenueGoal)}</td>
        <td>${farolValue(pct(row.goalAttainmentPct), row.farol?.goalAttainment)}</td>
        <td>${celulaProjecao(row)}</td>
        <td>${farolValue(pct(row.projectedGoalAttainmentPct || 0), row.farol?.projectedAttainment)}</td>
        <td>${currency(row.ticketAverage)}</td>
        <td>${number(row.distinctClients)}</td>
        <td>${celulaCarteiraVendedor(row, "carteira", row.ownClients)}</td>
        <td>${celulaCarteiraVendedor(row, "fora", row.otherClients)}</td>
        <td>${number(row.mixSku)}</td>
        <td>${currency(row.returnsValue)}</td>
        <td>${farolValue(pct(row.returnRatioPct), row.farol?.returnRatio)}</td>
        <td>${currency(row.warrantyReturnsValue || 0)}</td>
        <td>${farolValue(pct(row.discountPct || 0), row.farol?.discountPct)}</td>
        ${scoreEnabled() ? `<td><span class="score-chip">${row.score}</span></td>` : ''}
      </tr>
    `
    )
    .join("");
}

/** Célula compacta de ritmo para as tabelas: realizado/dia → necessário/dia. */
function celulaRitmo(pace, alvo = 100) {
  if (!pace) return "-";
  const t = (pace.targets || []).find((x) => x.pct === alvo);
  if (!pace.hasGoal) return `<span class="text-small" style="color:var(--muted)">sem meta</span>`;
  if (!t) return "-";
  if (t.reached) return `<span style="color:var(--good);font-weight:700">✓ ${alvo}%</span>`;
  if (!pace.remainingDays) return `<span class="text-small" style="color:var(--muted)">mês encerrado</span>`;
  const pior = t.dailyNeeded > pace.dailyActual * 1.2;
  return `<strong style="color:${pior ? "var(--bad)" : "var(--text)"}">${currency(t.dailyNeeded)}</strong>
    <div class="text-small" style="color:var(--muted)">atual ${currency(pace.dailyActual)}</div>`;
}

/** Projeção de faturamento do mês em reais.
 *
 *  É o líquido de hoje esticado pelos dias úteis que faltam. Aparece junto do
 *  "% Proj." porque o percentual sozinho não diz quanto falta em dinheiro — e
 *  é em dinheiro que a conversa com o vendedor acontece.
 */
function celulaProjecao(row) {
  const projecao = Number(row.projectedRevenue || 0);
  if (!projecao) return "—";
  const meta = Number(row.revenueGoal || 0);
  const falta = meta - projecao;
  const cor = !meta ? "var(--muted)" : falta > 0 ? "var(--bad)" : "var(--good)";
  return `<div style="font-weight:700">${currency(projecao)}</div>`
    + (meta ? `<div class="text-small" style="color:${cor}">
        ${falta > 0 ? `faltam ${currency(falta)}` : `+${currency(-falta)}`}
      </div>` : "");
}

function unitRows(rows) {
  return rows
    .map(
      (row) => `
      <tr>
        <td>${escapeHtml(row.unitName)}</td>
        <td>${currency(row.revenueNet)}</td>
        <td>${currency(row.revenueGoal)}</td>
        <td>${farolValue(pct(row.goalAttainmentPct), row.farol?.goalAttainment)}</td>
        <td>${celulaProjecao(row)}</td>
        <td>${farolValue(pct(row.projectedGoalAttainmentPct || 0), row.farol?.projectedAttainment)}</td>
        <td>${currency(row.returnsValue)}</td>
        <td>${farolValue(pct(row.returnRatioPct || 0), row.farol?.returnRatio)}</td>
        <td>${currency(row.warrantyReturnsValue || 0)}</td>
        <td>${farolValue(marginText(row.marginValue), row.farol?.marginValue)}</td>
        <td>${number(row.qtySold || 0)}</td>
        <td>${currency(row.ticketPerPiece || 0)}</td>
        <td>${currency(row.metaDiaria)}</td>
        <td>${celulaRitmo(row.pace, 100)}</td>
      </tr>
    `
    )
    .join("");
}

// ─── Ordenação de tabelas por clique no cabeçalho ───────────────────────────

/**
 * Estado de ordenação por tabela. Cada tabela tem uma chave própria, então a
 * escolha feita em Cidades não interfere em Clientes.
 */
function tableSort(tableKey) {
  return state.ui.tableSort[tableKey] || null;
}

/** Alterna a coluna: primeiro clique ordena, segundo inverte, terceiro limpa. */
function toggleTableSort(tableKey, field, defaultDir) {
  const atual = state.ui.tableSort[tableKey];
  if (!atual || atual.field !== field) {
    state.ui.tableSort[tableKey] = { field, dir: defaultDir || "desc" };
  } else if (atual.dir === (defaultDir || "desc")) {
    state.ui.tableSort[tableKey] = { field, dir: atual.dir === "desc" ? "asc" : "desc" };
  } else {
    delete state.ui.tableSort[tableKey];   // volta à ordem original
  }
  requestRender();
}

/**
 * Cabeçalho clicável. `field` é a propriedade do objeto; `type` define o
 * comparador (número ou texto) e a direção inicial — números começam do maior,
 * textos do A ao Z, que é o que se espera em cada caso.
 */
function sortableTh(tableKey, label, field, type = "number", extraStyle = "") {
  const s = tableSort(tableKey);
  const ativo = s && s.field === field;
  const seta = ativo ? (s.dir === "asc" ? "▲" : "▼") : "⇅";
  const cor = ativo ? "var(--accent)" : "var(--muted)";
  const defaultDir = type === "text" ? "asc" : "desc";
  return `
    <th style="cursor:pointer;user-select:none;white-space:nowrap;${extraStyle}"
        onclick="toggleTableSort('${tableKey}','${field}','${defaultDir}')"
        title="Clique para ordenar. Clique de novo para inverter.">
      ${escapeHtml(label)} <span style="color:${cor};font-size:10px">${seta}</span>
    </th>`;
}

/** Aplica a ordenação escolhida. Sem escolha, devolve a ordem que veio do servidor. */
function applyTableSort(rows, tableKey) {
  const s = tableSort(tableKey);
  if (!s || !Array.isArray(rows)) return rows || [];
  const mult = s.dir === "asc" ? 1 : -1;
  return [...rows].sort((a, b) => {
    const va = a?.[s.field];
    const vb = b?.[s.field];
    // Vazios sempre no fim, independente da direção
    const aVazio = va === null || va === undefined || va === "";
    const bVazio = vb === null || vb === undefined || vb === "";
    if (aVazio && bVazio) return 0;
    if (aVazio) return 1;
    if (bVazio) return -1;
    if (typeof va === "number" || typeof vb === "number") {
      return (Number(va) - Number(vb)) * mult;
    }
    return String(va).localeCompare(String(vb), "pt-BR") * mult;
  });
}

/** Aviso discreto de que a tabela está reordenada, com botão de limpar. */
function sortHint(tableKey, labelPadrao) {
  const s = tableSort(tableKey);
  if (!s) return "";
  return `<span class="soft-badge" style="cursor:pointer" onclick="delete state.ui.tableSort['${tableKey}'];requestRender()"
    title="Voltar à ordem padrão">ordenado ✕</span>`;
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

/** Executa uma atualização mostrando que ela está rodando.
 *
 *  Botão que recarrega em silêncio parece quebrado: a pessoa clica, nada muda
 *  na tela (porque os dados vieram iguais) e ela clica de novo. Aqui o rótulo
 *  vira "Atualizando…", o botão trava contra o clique duplo e, no fim, sai um
 *  aviso dizendo que terminou — mesmo quando nada mudou.
 */
async function atualizarCom(chave, fn, mensagem) {
  if (state.ui.refreshing[chave]) return;
  state.ui.refreshing[chave] = true;
  requestRender();
  try {
    // As cargas não lançam exceção: guardam o erro no estado e o devolvem.
    // Sem olhar o retorno, uma falha viraria "Dados atualizados." em verde.
    const r = await fn();
    if (r && r.error) addMessage("error", r.error);
    else addMessage("success", mensagem || "Dados atualizados.");
  } catch (e) {
    addMessage("error", e.message || "Não foi possível atualizar agora.");
  } finally {
    delete state.ui.refreshing[chave];
    requestRender();
  }
}

/** Botão padrão de atualizar. `chamada` é o código que recarrega a tela. */
function botaoAtualizar(chave, chamada, opcoes = {}) {
  const rodando = Boolean(state.ui.refreshing[chave]);
  const msg = opcoes.mensagem ? `, '${jsAttr(opcoes.mensagem)}'` : "";
  return `<button class="btn ${opcoes.classe || "btn-ghost btn-sm"}" ${rodando ? "disabled" : ""}
    title="Atualizar os dados desta tela"
    onclick="atualizarCom('${chave}', () => ${chamada}${msg})">
    ${rodando ? '<span class="girando">↻</span> Atualizando…' : "↻ Atualizar"}</button>`;
}

async function refreshCurrentTab() {
  const tab = state.activeTab;
  const promises = [];
  // Dados gerais sempre recarregados
  if (["executivo", "vendedores", "unidades", "clientes", "cidades", "descontos", "calendario"].includes(tab)) {
    promises.push(loadDashboard());
  }
  if (tab === "marcas") {
    promises.push(loadBrands(true));
  }
  if (tab === "devolucoes") {
    promises.push(loadReturns(true));
  }
  if (tab === "metas-vendedor") {
    promises.push(loadSellerTargets());
  }
  if (tab === "placar-equipe") {
    promises.push(loadAwards(true));
  }
  if (tab === "crm-agenda") {
    promises.push(loadTeamActivity(), loadCrmData());
  }
  if (tab === "crm-clientes") {
    // O resumo e as coberturas valem para os dois perfis: o vendedor vê os
    // próprios números e as carteiras que está cobrindo; o gestor vê a equipe.
    promises.push(loadCrmClients({ renderAfterLoad: true, reason: "reload" }),
                  loadPortfolioSummary(), loadCoverages());
  }
  if (tab === "crm-tarefas" || tab === "crm-interacao") {
    promises.push(loadCrmData());
  }
  if (tab === "importacoes") {
    promises.push(loadAutoImportStatus(), loadAdmin());
  }
  if (tab === "sem-vendedor") {
    promises.push(loadUnassignedClients());
  }
  if (tab === "administracao" || tab === "configuracoes" || tab === "acessos") {
    promises.push(loadAdmin());
  }
  // Fallback: recarrega tudo
  if (!promises.length) {
    promises.push(loadDashboard(), loadCrmData());
  }
  await Promise.all(promises);
}

/** "Dados até 15/08" ao lado do título — presente em todas as telas.
 *
 * É a pergunta que precede qualquer número: alguém olha o painel no dia 15 e
 * conclui que a equipe vendeu pouco, quando o faturamento só entrou até o dia
 * 12. Fica em cinza, discreto, e só ganha cor quando o atraso passa de dois
 * dias úteis — aí deixa de ser informação e vira alerta.
 */
function selo_dados_ate() {
  const f = state.options.dataFreshness;
  if (!f || !f.salesThrough) return "";
  const detalhe = [
    `Faturamento até ${shortDate(f.salesThrough)}`,
    f.registryThrough ? `Cadastro de clientes até ${shortDate(f.registryThrough)}` : "",
    f.warrantyThrough ? `Devoluções em garantia até ${shortDate(f.warrantyThrough)}` : "",
    f.lastImportAt ? `Última importação em ${shortDate(f.lastImportAt)}` : "",
  ].filter(Boolean).join(" · ");
  const cor = f.stale ? "#b06000" : "var(--muted)";
  const fundo = f.stale ? "#fff8e6" : "rgba(15,40,60,0.05)";
  const borda = f.stale ? "#f0d68a" : "transparent";
  return `<span title="${escapeHtml(detalhe)}"
    style="font-size:11px;font-weight:700;color:${cor};background:${fundo};
           border:1px solid ${borda};border-radius:20px;padding:3px 10px;
           margin-left:8px;vertical-align:middle;white-space:nowrap;letter-spacing:0.01em">
    ${f.stale ? "⚠ " : ""}dados até ${escapeHtml(shortDate(f.salesThrough))}${
      f.stale ? ` · ${number(f.businessDaysBehind)} dia(s) útil(eis) atrás` : ""}
  </span>`;
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
      ${botaoAtualizar("telaAtual", "refreshCurrentTab()")}
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
                  <th title="Quanto precisa vender por dia útil restante para fechar em 100%">R$/dia p/ 100%</th>
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
                  ${scoreEnabled() ? '<th>Score</th>' : ''}
            </tr>
          </thead>
          <tbody>
            ${state.dashboard.sellerRanking
              .map(
                (row) => `
                <tr>
                  <td>${escapeHtml(row.sellerName)} ${seloVinculoVendedor(row)}</td>
                  <td>${escapeHtml(row.baseUnit || "-")}</td>
                  <td>${currency(row.revenueNet)}</td>
                  <td>${currency(row.revenueGoal)}</td>
                  <td>${pct(row.goalAttainmentPct)}</td>
                  <td>${pct(row.projectedGoalAttainmentPct || 0)}</td>
                  <td>${currency(row.metaDiaria)}</td>
                  <td>${celulaRitmo(row.pace, 100)}</td>
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
                  ${scoreEnabled() ? `<td><span class="score-chip">${row.score}</span></td>` : ''}
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
          <div class="text-small">Clique em qualquer coluna para reordenar.</div>
        </div>
        ${sortHint("cidades")}
      </div>
      <div class="table-wrap">
        <table>
          <thead>
              <tr>
                ${sortableTh("cidades", "Cidade", "cityName", "text")}
                ${sortableTh("cidades", "Faturamento líquido", "revenueNet")}
                ${sortableTh("cidades", "Ticket médio", "ticketAverage")}
                ${sortableTh("cidades", "Clientes distintos", "distinctClients")}
                ${sortableTh("cidades", "R$ Desconto", "discountValue")}
                ${sortableTh("cidades", "% Desconto", "discountPct")}
                ${sortableTh("cidades", "Devolução", "returnsValue")}
              </tr>
          </thead>
          <tbody>${cityRows(applyTableSort(state.dashboard.cityRanking, "cidades"))}</tbody>
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
          <button class="btn btn-secondary btn-sm" onclick="abrirClientesDoVendedor('', 'todos')"
            title="Lista dos clientes faturados no mês, com o dono da carteira de cada um">
            📄 Clientes faturados por vendedor
          </button>
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
            // Status calculado por meta, devolução e desconto. O score entra apenas
            // como reforço quando está ativo, para o selo funcionar sozinho depois.
            let statusLabel = "Acompanhar";
            let statusTone = "warn";
            const scoreOk = (min) => !scoreEnabled() || score >= min;
            if (actualPct >= 100 && returnPct <= 3 && scoreOk(85)) {
              statusLabel = "Destaque";
              statusTone = "good";
            } else if (projectedPct >= 100 && scoreOk(75)) {
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
                    ${showSellerStatus() ? `<span class="status-tag ${statusTone}">${statusLabel}</span>` : ""}
                    ${scoreEnabled() ? `<span class="score-chip">${row.score}</span>` : ""}
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
                    ${(row.ownClients != null || row.otherClients != null) ? `
                      <div style="font-size:10px;margin-top:2px;line-height:1.4">
                        <button type="button" class="link-num" style="color:var(--good);font-size:10px"
                          title="Ver os clientes da carteira dele"
                          onclick="abrirClientesDoVendedor('${jsAttr(row.sellerName)}','carteira')"
                          >${number(row.ownClients || 0)} carteira</button>
                        <span style="color:var(--muted)"> · </span>
                        <button type="button" class="link-num" style="color:#e67e22;font-size:10px"
                          title="Ver os clientes de fora da carteira dele"
                          onclick="abrirClientesDoVendedor('${jsAttr(row.sellerName)}','fora')"
                          >${number(row.otherClients || 0)} fora</button>
                      </div>` : ""}
                  </div>
                  <div>
                    <span>Mix</span>
                    <strong>${number(row.mixSku)}</strong>
                  </div>
                </div>
                <div class="seller-visual-bars">
                  <div class="seller-visual-bar-row">
                    <div class="seller-visual-bar-head">
                      <span>% meta atual ${farolBadge(row.farol?.goalAttainment, {compact:true})}</span>
                      <strong ${row.farol?.goalAttainment?.color ? `style="color:${row.farol.goalAttainment.color}"` : ""}>${pct(actualPct)}</strong>
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
                  ${Number(row.projectedRevenue || 0) ? `
                    <div class="seller-visual-bar-head" style="margin-top:2px">
                      <span>Projeção do mês</span>
                      <strong>${currency(row.projectedRevenue)}</strong>
                    </div>` : ""}
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

/**
 * Indicador de tendência do cliente: mês atual contra a média mensal do
 * trimestre anterior. Vem em coluna própria, ao lado do faturamento, para
 * não competir com o valor em si.
 */
function quarterTrendBadge(row) {
  const v = row.quarterVariationPct;
  if (v === null || v === undefined) {
    return `<span class="text-small" style="color:var(--muted)" title="Sem faturamento no trimestre anterior para comparar">—</span>`;
  }
  const media = currency(row.quarterAverage || 0);
  const meses = (row.quarterMonths || []).map(competenceShort).join(", ");
  const titulo = `Média mensal do trimestre anterior (${meses}): ${media}`;
  const cfg = v > 5
    ? { icon: "▲", cor: "#1e8e3e" }
    : v < -5
      ? { icon: "▼", cor: "#c5221f" }
      : { icon: "=", cor: "#5f6368" };
  const sinal = v > 0 ? "+" : "";
  return `<span style="color:${cfg.cor};font-weight:700;white-space:nowrap" title="${escapeHtml(titulo)}">
    ${cfg.icon} ${sinal}${v.toFixed(0)}%
  </span>`;
}

/** Filtra o ranking por nome ou código digitado na busca. */
function filteredClientRanking() {
  const termo = String(state.ui.clientRankingSearch || "").trim().toLowerCase();
  const base = state.dashboard.clientRanking || [];
  if (!termo) return base;
  return base.filter((r) =>
    String(r.clientName || "").toLowerCase().includes(termo) ||
    String(r.clientKey || "").toLowerCase().includes(termo));
}

/**
 * Aplica a busca só no Enter ou no botão.
 * Buscar a cada tecla obrigava a redesenhar a tabela inteira, o campo perdia o
 * foco e não dava para terminar de digitar.
 */
function applyClientRankingSearch() {
  const campo = document.getElementById("client-ranking-search");
  state.ui.clientRankingSearch = campo ? campo.value.trim() : "";
  requestRender();
  // Devolve o foco ao campo depois do redesenho
  setTimeout(() => {
    const novo = document.getElementById("client-ranking-search");
    if (novo) { novo.focus(); novo.setSelectionRange(novo.value.length, novo.value.length); }
  }, 0);
}

function clearClientRankingSearch() {
  state.ui.clientRankingSearch = "";
  requestRender();
  setTimeout(() => document.getElementById("client-ranking-search")?.focus(), 0);
}

function clientRankingCard() {
  const termo = state.ui.clientRankingSearch || "";
  const filtrados = filteredClientRanking();
  const ordenados = applyTableSort(filtrados, "clientes");
  const exibidos = ordenados.slice(0, 100);
  const total = state.dashboard.clientRanking?.length || 0;

  return `
    <div class="table-card">
      <div class="section-title">
        <div>
          <h3>Ranking de clientes</h3>
          <div class="text-small">Clique em qualquer coluna para reordenar.</div>
        </div>
        <div style="display:flex;gap:6px;align-items:center">
          ${sortHint("clientes")}
          <div class="soft-badge">${termo
            ? `${number(filtrados.length)} de ${number(total)}`
            : (tableSort("clientes") ? "Top 100 pela coluna escolhida" : "Top 100 por faturamento")}</div>
        </div>
      </div>

      <div style="display:flex;gap:8px;align-items:center;margin-bottom:12px;flex-wrap:wrap">
        <input id="client-ranking-search" style="flex:1;min-width:240px"
          placeholder="🔍 Buscar por nome ou código — Enter para buscar"
          value="${escapeHtml(termo)}"
          onkeydown="if(event.key==='Enter'){event.preventDefault();applyClientRankingSearch();}" />
        <button class="btn btn-secondary btn-sm" onclick="applyClientRankingSearch()">Buscar</button>
        ${termo ? `<button class="btn btn-ghost btn-sm" onclick="clearClientRankingSearch()">Limpar</button>` : ""}
      </div>

      <div class="table-wrap">
        <table>
          <thead>
            <tr>
              ${sortableTh("clientes", "Cliente", "clientName", "text")}
              ${sortableTh("clientes", "Código", "clientKey", "text")}
              ${sortableTh("clientes", "Tipo", "personType", "text")}
              ${sortableTh("clientes", "Faturamento líquido", "revenueNet")}
              ${sortableTh("clientes", "vs trimestre", "quarterVariationPct")}
              ${sortableTh("clientes", "R$ Desconto", "discountValue")}
              ${sortableTh("clientes", "% Desconto", "discountPct")}
              ${sortableTh("clientes", "Devolução", "returnsValue")}
              <th style="text-align:right">Ações</th>
            </tr>
          </thead>
          <tbody>
            ${exibidos.length ? exibidos.map((row) => `
              <tr>
                <td><strong>${escapeHtml(row.clientName)}</strong></td>
                <td class="text-small">${escapeHtml(row.clientKey || "-")}</td>
                <td>${escapeHtml(row.personType || "-")}</td>
                <td>${currency(row.revenueNet)}</td>
                <td>${quarterTrendBadge(row)}</td>
                <td>${currency(row.discountValue)}</td>
                <td>${pct(row.discountPct || 0)}</td>
                <td>${currency(row.returnsValue || 0)}</td>
                <td style="text-align:right;white-space:nowrap">
                  ${row.clientKey
                    ? `<button class="btn btn-ghost btn-sm" onclick="openCrmClient('${escapeHtml(row.clientKey)}', false)">Ficha</button>`
                    : `<span class="text-small" style="color:var(--muted)" title="Cliente sem cadastro no CRM — só aparece no faturamento">sem cadastro</span>`}
                </td>
              </tr>`).join("")
              : `<tr><td colspan="9" class="text-small" style="text-align:center;padding:20px;color:var(--muted)">
                   Nenhum cliente encontrado para "${escapeHtml(termo)}".
                 </td></tr>`}
          </tbody>
        </table>
      </div>
      ${ordenados.length > 100 ? `<div class="text-small" style="text-align:center;color:var(--muted);margin-top:8px">
        Exibindo 100 de ${number(ordenados.length)}. Use a busca para encontrar um cliente específico.
      </div>` : ""}
    </div>`;
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
      ${clientRankingCard()}
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
          <div class="field">
            <label>Vendedor</label>
            ${(() => {
              // Lista fechada: nome digitado diferente da base quebra o cálculo
              // ponderado de meta (o vínculo é feito pelo nome exato).
              const opcoes = sellerPeopleOptions();
              const atual = ev?.person_name || "";
              const naLista = opcoes.some((p) => p.person_name === atual);
              return `
                <select id="vac-name" required>
                  <option value="">Selecione o vendedor…</option>
                  ${opcoes.map((p) => `<option value="${escapeHtml(p.person_name)}" ${atual === p.person_name ? "selected" : ""}>${escapeHtml(p.person_name)}${p.base_unit ? ` · ${escapeHtml(p.base_unit)}` : ""}</option>`).join("")}
                  ${atual && !naLista ? `<option value="${escapeHtml(atual)}" selected>${escapeHtml(atual)} (fora da base)</option>` : ""}
                </select>
                ${atual && !naLista ? `<div class="text-small" style="color:#e67e22;margin-top:4px">⚠ Este nome não está na base de vendedores — o cálculo de meta pode não considerar estas férias.</div>` : ""}`;
            })()}
          </div>
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

/**
 * Vendedores ativos que ainda não têm meta na competência selecionada.
 * Sem meta, o % de atingimento fica zerado e o vendedor some do Placar e da
 * Missão do Dia — por isso vale sinalizar antes de o mês avançar.
 */
function sellersMissingGoal(competence) {
  const comp = competence || state.goalEditors?.seller?.competence
    || state.filters.competenceEnd || state.options.competences?.[0] || "";
  if (!comp) return { competence: "", pending: [] };
  const comGoal = new Set(
    (state.admin?.goalsSeller || [])
      .filter((g) => g.competence === comp)
      .map((g) => personMatchKey(g.seller_name))
  );
  // Só quem está classificado como Vendedor. Quem emite venda mas é de outra
  // função (balcão, caixa, administrativo) não tem meta e não deve poluir a lista.
  const pending = sellerPeopleOptions({ onlySellers: true })
    .filter((p) => !comGoal.has(personMatchKey(p.person_name)));
  return { competence: comp, pending };
}

function missingGoalsCard() {
  const { competence, pending } = sellersMissingGoal();
  if (!competence) return "";
  if (!pending.length) {
    return `<div class="message success" style="font-size:13px">
      ✅ Todos os vendedores têm meta cadastrada em ${escapeHtml(competence)}.
    </div>`;
  }
  return `
    <div class="form-card" style="border-left:4px solid #e67e22">
      <div class="section-title">
        <div>
          <h3 style="font-size:15px">⚠ Vendedores sem meta em ${escapeHtml(competence)}</h3>
          <div class="text-small">Sem meta, o atingimento fica zerado e o vendedor não entra no Placar.</div>
        </div>
        <span class="soft-badge" style="background:#fff3e0;color:#e65100">${pending.length}</span>
      </div>
      <div style="display:flex;flex-wrap:wrap;gap:6px">
        ${pending.map((p) => `
          <button class="btn btn-ghost btn-sm" type="button"
            onclick="prefillSellerGoal('${encodeURIComponent(p.person_name)}','${encodeURIComponent(p.base_unit || "")}','${encodeURIComponent(competence)}')"
            title="Cadastrar meta para ${escapeHtml(p.person_name)}">
            ${escapeHtml(p.person_name)}${p.base_unit ? ` · ${escapeHtml(p.base_unit)}` : ""}
          </button>`).join("")}
      </div>
      <div class="text-small" style="color:var(--muted);margin-top:8px">
        Clique em um nome para preencher o formulário de meta com esse vendedor.
      </div>
    </div>`;
}

/** Preenche o formulário de meta a partir do card de pendências. */
function prefillSellerGoal(nameEnc, unitEnc, competenceEnc) {
  const name = decodeURIComponent(nameEnc);
  const unit = decodeURIComponent(unitEnc || "");
  const competence = decodeURIComponent(competenceEnc || "");
  state.goalEditors.seller = {
    ...(state.goalEditors.seller || {}),
    competence,
    sellerName: name,
    baseUnit: unit,
    revenueGoal: "",
    editing: false,
  };
  requestRender();
  document.getElementById("goal-seller-name")?.scrollIntoView({ behavior: "smooth", block: "center" });
  setTimeout(() => document.getElementById("goal-seller-revenue")?.focus(), 300);
}

/**
 * Quem emite venda mas ainda não tem função definida no cadastro.
 * Enquanto não for classificado, não entra na lista de metas pendentes nem no
 * Placar — e é justamente por isso que precisa ser sinalizado.
 */
function unclassifiedSellersCard() {
  const pendentes = unclassifiedSellers();
  if (!pendentes.length) return "";
  return `
    <div class="form-card" style="border-left:4px solid #8e44ad">
      <div class="section-title">
        <div>
          <h3 style="font-size:15px">👤 Pessoas sem função definida</h3>
          <div class="text-small">Emitem venda mas não estão classificadas. Marque como Vendedor
          para entrarem nas metas, ou como Outro se não forem da equipe comercial.</div>
        </div>
        <span class="soft-badge" style="background:#f3e5f5;color:#6a1b9a">${pendentes.length}</span>
      </div>
      <div style="display:flex;flex-wrap:wrap;gap:6px">
        ${pendentes.map((p) => `
          <button class="btn btn-ghost btn-sm" type="button"
            onclick="prefillPersonClassification('${encodeURIComponent(p.person_name)}')"
            title="Classificar ${escapeHtml(p.person_name)}">
            ${escapeHtml(p.person_name)}
          </button>`).join("")}
      </div>
    </div>`;
}

/** Leva o nome para o formulário de cadastro de pessoa. */
function prefillPersonClassification(nameEnc) {
  const name = decodeURIComponent(nameEnc);
  requestRender();
  setTimeout(() => {
    const campo = document.getElementById("person-name");
    if (campo) {
      campo.value = name;
      campo.scrollIntoView({ behavior: "smooth", block: "center" });
      document.getElementById("person-role")?.focus();
    } else {
      addMessage("info", `Cadastre "${name}" em Administração › Cadastro de pessoa.`);
    }
  }, 100);
}

function sellerGoalsTableCard() {
  const rows = state.admin?.goalsSeller || [];
  return `
    ${missingGoalsCard()}
    ${unclassifiedSellersCard()}
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
              <div class="field field-span-2 text-small" style="color:var(--muted);align-self:end">
                Vale para <strong>todos os períodos</strong>, inclusive os meses já fechados —
                cidade não troca de unidade com o tempo.
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
  // A tela de acessos depende do payload administrativo (usuários e perfis)
  if (tab === "acessos" && !state.admin) loadAdmin();
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
    // Marcas lê a mesma competência do topo: sem isto, trocar o mês mudaria
    // todos os números da tela menos o ranking de marcas.
    if (state.activeTab === "marcas") await loadBrands(true);
    if (state.activeTab === "devolucoes") await loadReturns(true);
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

/**
 * Texto seguro dentro de um onclick="...('AQUI')".
 * escapeHtml não trata aspas simples, e nome de cliente com apóstrofo
 * (D'ALESSANDRO, D'AVILA) quebrava o handler inteiro.
 */
function jsAttr(valor) {
  return String(valor ?? "")
    .replace(/\\/g, "\\\\")
    .replace(/'/g, "\\'")
    .replace(/"/g, "&quot;")
    .replace(/</g, "&lt;");
}

// ─── Contatos: histórico e produtividade ───────────────────────────────────

async function loadContacts() {
  if (state.ui.loading.contacts) return;
  setLoading("contacts", true);
  try {
    const f = state.contactFilters;
    const q = new URLSearchParams();
    Object.entries(f).forEach(([k, v]) => { if (v) q.set(k, v); });
    state.contacts = await api(`/api/crm/contacts?${q.toString()}`);
  } catch (error) {
    addMessage("error", error.message);
  } finally {
    setLoading("contacts", false);
  }
  requestRender();
}

function setContactFilter(campo, valor) {
  state.contactFilters[campo] = valor;
  void loadContacts();
}

function contactPeriodPreset(preset) {
  const hoje = new Date();
  const iso = (d) => d.toISOString().slice(0, 10);
  if (preset === "hoje") {
    state.contactFilters.start = iso(hoje);
    state.contactFilters.end = iso(hoje);
  } else if (preset === "semana") {
    const inicio = new Date(hoje); inicio.setDate(hoje.getDate() - 6);
    state.contactFilters.start = iso(inicio);
    state.contactFilters.end = iso(hoje);
  } else {
    state.contactFilters.start = iso(new Date(hoje.getFullYear(), hoje.getMonth(), 1));
    state.contactFilters.end = iso(hoje);
  }
  void loadContacts();
}

/** Barra de ritmo: verde no ritmo, âmbar perto, vermelho atrás. */
function paceBar(pct) {
  const v = Math.max(0, Math.min(Number(pct) || 0, 130));
  const cor = v >= 100 ? "var(--good)" : v >= 70 ? "#e0a800" : "var(--bad)";
  return `<div style="display:flex;align-items:center;gap:8px">
      <div style="flex:1;height:6px;border-radius:3px;background:#eceff1;overflow:hidden">
        <div style="width:${Math.min(v, 100)}%;height:100%;background:${cor}"></div>
      </div>
      <strong style="font-size:12px;color:${cor}">${Math.round(v)}%</strong>
    </div>`;
}

function contatosView() {
  if (!state.contacts && !state.ui.loading.contacts) { void loadContacts(); }
  if (!state.contacts) return `<div class="loader panel">Carregando contatos…</div>`;

  const d = state.contacts;
  const f = state.contactFilters;
  const gerente = Boolean(d.isManagerView);
  const t = d.totals || {};

  const badgeIniciativa = (v) => v === "RECEPTIVO"
    ? '<span class="soft-badge" style="background:#eef1f4;color:#5b6b76">receptivo</span>'
    : '<span class="soft-badge">ativo</span>';

  return `
    <div class="stack">
      <div class="form-card">
        <div class="section-title">
          <div>
            <h3>Contatos</h3>
            <div class="text-small">Tudo que foi registrado no período — ${escapeHtml(f.start)} a ${escapeHtml(f.end)}.</div>
          </div>
          <div class="actions">
            <button class="btn btn-ghost btn-sm" type="button" onclick="contactPeriodPreset('hoje')">Hoje</button>
            <button class="btn btn-ghost btn-sm" type="button" onclick="contactPeriodPreset('semana')">7 dias</button>
            <button class="btn btn-ghost btn-sm" type="button" onclick="contactPeriodPreset('mes')">Mês</button>
          </div>
        </div>
        <div class="two-column-form">
          <div class="field"><label>De</label>
            <input type="date" value="${escapeHtml(f.start)}" onchange="setContactFilter('start', this.value)" /></div>
          <div class="field"><label>Até</label>
            <input type="date" value="${escapeHtml(f.end)}" onchange="setContactFilter('end', this.value)" /></div>
          ${gerente ? `
          <div class="field"><label>Vendedor</label>
            <select onchange="setContactFilter('seller', this.value)">
              <option value="">Todos</option>
              ${(d.sellerOptions || []).map((v) => `<option value="${escapeHtml(v)}" ${f.seller === v ? "selected" : ""}>${escapeHtml(v)}</option>`).join("")}
            </select></div>` : ""}
          ${gerente ? `
          <div class="field"><label>Carteira do cliente</label>
            <select onchange="setContactFilter('portfolio', this.value)">
              <option value="">Todas</option>
              <option value="__CRUZADOS__" ${f.portfolio === "__CRUZADOS__" ? "selected" : ""}>
                ⚠ Só contatos em carteira de outro${d.crossCount ? ` (${d.crossCount})` : ""}</option>
              <option value="__SEM_VENDEDOR__" ${f.portfolio === "__SEM_VENDEDOR__" ? "selected" : ""}>Sem vendedor</option>
              ${(d.portfolioOptions || []).map((v) => `<option value="${escapeHtml(v)}" ${f.portfolio === v ? "selected" : ""}>${escapeHtml(v)}</option>`).join("")}
            </select></div>` : ""}
          <div class="field"><label>Tipo</label>
            <select onchange="setContactFilter('type', this.value)">
              <option value="">Todos</option>
              ${(d.contactTypes || []).map((c) => `<option value="${escapeHtml(c.code)}" ${f.type === c.code ? "selected" : ""}>${escapeHtml(c.label)}</option>`).join("")}
            </select></div>
          <div class="field"><label>Resultado</label>
            <select onchange="setContactFilter('result', this.value)">
              <option value="">Todos</option>
              ${(d.contactResults || []).map((c) => `<option value="${escapeHtml(c.code)}" ${f.result === c.code ? "selected" : ""}>${escapeHtml(c.label)}</option>`).join("")}
            </select></div>
          <div class="field"><label>Origem do contato</label>
            <select onchange="setContactFilter('origin', this.value)">
              <option value="">Todas as origens</option>
              <option value="__TAREFA__" ${f.origin === "__TAREFA__" ? "selected" : ""}>
                📌 Veio de tarefa agendada${t.deTarefa ? ` (${number(t.deTarefa)})` : ""}</option>
              <option value="__SEM_TAREFA__" ${f.origin === "__SEM_TAREFA__" ? "selected" : ""}>
                📋 Carteira / Missão do Dia${t.espontaneos ? ` (${number(t.espontaneos)})` : ""}</option>
              ${(d.origins || []).map((o) => `<option value="${escapeHtml(o.id)}" ${f.origin === o.id ? "selected" : ""}>${o.icon} ${escapeHtml(o.label)}</option>`).join("")}
            </select></div>
          <div class="field"><label>Iniciativa</label>
            <select onchange="setContactFilter('initiative', this.value)">
              <option value="">Ativo e receptivo</option>
              <option value="ATIVO" ${f.initiative === "ATIVO" ? "selected" : ""}>Só ativo (conta na meta)</option>
              <option value="RECEPTIVO" ${f.initiative === "RECEPTIVO" ? "selected" : ""}>Só receptivo</option>
            </select></div>
          <div class="field field-span-2"><label>Cliente</label>
            <input value="${escapeHtml(f.search || "")}" placeholder="Nome ou código — Enter para buscar"
              onkeydown="if(event.key==='Enter'){setContactFilter('search', this.value);}" /></div>
        </div>
      </div>

      <div class="kpi-grid">
        ${kpiCard("Ligações ativas", number(t.ligacoes || 0),
                  `Esperado até hoje: ${number(t.callsTargetToDate || 0)}`, "")}
        ${kpiCard("Conversa efetiva", `${(t.talkRatePct || 0).toFixed(1)}%`,
                  `${number(t.falou || 0)} de ${number(t.ativos || 0)} contatos ativos`, "")}
        ${kpiCard("Gerou orçamento ou pedido", `${(t.conversionPct || 0).toFixed(1)}%`,
                  `${number(t.converteu || 0)} registros`, "")}
        ${kpiCard("Clientes distintos", number(t.clientes || 0),
                  `${number(t.receptivos || 0)} registro(s) receptivo(s)`, "")}
        ${kpiCard("Vieram de tarefa", number(t.deTarefa || 0),
                  `${number(t.espontaneos || 0)} da carteira/missão`, "")}
      </div>

      ${gerente && (d.sellers || []).length ? `
      <div class="form-card">
        <div class="section-title">
          <div><h3>Por vendedor</h3>
          <div class="text-small">A meta de ligações é o ritmo do mês, não o total fechado — cobrar 60 no dia 6 marcaria todo mundo como irregular.</div></div>
        </div>
        <div class="table-wrap">
          <table>
            <thead><tr>
              <th>Vendedor</th><th style="min-width:150px">Ligações no ritmo</th>
              <th style="text-align:right">Conversa</th><th style="text-align:right">Converteu</th>
              <th style="text-align:right">Clientes</th><th style="text-align:right">Receptivos</th>
              <th>Último registro</th>
            </tr></thead>
            <tbody>
              ${d.sellers.map((v) => `
                <tr>
                  <td><strong>${escapeHtml(v.seller_name || "-")}</strong></td>
                  <td>${paceBar(v.callsPacePct)}
                      <div class="text-small" style="color:var(--muted)">${number(v.ligacoes || 0)} de ${number(v.callsTargetToDate || 0)}</div></td>
                  <td style="text-align:right">${(v.talkRatePct || 0).toFixed(1)}%</td>
                  <td style="text-align:right">${(v.conversionPct || 0).toFixed(1)}%</td>
                  <td style="text-align:right">${number(v.clientes || 0)}</td>
                  <td style="text-align:right" class="text-small">${number(v.receptivos || 0)}</td>
                  <td class="text-small">${escapeHtml(shortDate(v.ultimo) || "-")}</td>
                </tr>`).join("")}
            </tbody>
          </table>
        </div>
      </div>` : ""}

      <div class="form-card">
        <div class="section-title">
          <div><h3>Registros</h3>
          <div class="text-small">${number((d.items || []).length)} registro(s)${d.truncated ? " — mostrando os mais recentes, refine o período" : ""}.</div></div>
          <button class="btn btn-ghost btn-sm" type="button" onclick="exportContatosXLSX()">↓ Exportar</button>
        </div>
        <div class="table-wrap">
          <table>
            <thead><tr>
              <th>Quando</th><th>Cliente</th>${gerente ? "<th>Vendedor</th><th>Carteira</th>" : ""}
              <th>Tipo</th><th>Resultado</th><th>Observação</th><th>Retorno</th>
            </tr></thead>
            <tbody>
              ${(d.items || []).length ? d.items.map((i) => `
                <tr>
                  <td class="text-small" style="white-space:nowrap">${escapeHtml(shortDate(i.occurred_at) || "-")}</td>
                  <td class="text-small">
                    <button class="btn btn-ghost btn-sm" type="button" style="padding:0;text-align:left"
                      onclick="openCrmClient('${jsAttr(i.client_key)}')">${escapeHtml(i.client_name || i.client_key)}</button>
                  </td>
                  ${gerente ? `
                    <td class="text-small">${escapeHtml(i.seller_name || "-")}</td>
                    <td class="text-small">
                      ${i.portfolioSeller === "Sem vendedor"
                        ? '<span style="color:var(--muted)">Sem vendedor</span>'
                        : escapeHtml(i.portfolioSeller)}
                      ${i.crossPortfolio ? '<div style="color:#b06000;font-weight:700">⚠ outra carteira</div>' : ""}
                    </td>` : ""}
                  <td class="text-small">${escapeHtml(i.type_label || i.contact_type_code)} ${badgeIniciativa(i.initiative)}
                    <div style="color:${i.fromTask ? "#1a5276" : "var(--muted)"};font-size:11px">
                      ${i.fromTask ? "📌 " : ""}${escapeHtml(i.originLabel || "")}</div>
                  </td>
                  <td class="text-small">${escapeHtml(i.result_label || i.result_code)}</td>
                  <td class="text-small" style="max-width:340px">${escapeHtml((i.notes || "").slice(0, 160))}${(i.notes || "").length > 160 ? "…" : ""}</td>
                  <td class="text-small">${escapeHtml(i.followup_due_at ? shortDate(i.followup_due_at) : "-")}</td>
                </tr>`).join("")
                : `<tr><td colspan="${gerente ? 8 : 6}" class="text-small">Nenhum registro no período.</td></tr>`}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  `;
}

/** Explica o rodízio: por que o cliente contatado sumiu e quando ele volta. */
function rodizioAviso() {
  const r = state.crm.agenda?.rotation;
  if (!r || !r.cycleDays) return "";
  if (r.recycled) {
    return `<div class="text-small" style="margin-bottom:10px;padding:10px 12px;border-radius:8px;
         background:#eef7ee;border:1px solid #cfe3cf;color:#2f6d33">
      <strong>Carteira inteira trabalhada.</strong> Todo mundo já foi contatado neste ciclo —
      a fila recomeça pelos que estão há mais tempo sem contato.
    </div>`;
  }
  if (!r.restingCount) return "";
  return `<div class="text-small" style="margin-bottom:10px;color:var(--muted)">
      ${number(r.restingCount)} cliente(s) em descanso: já foram contatados neste ciclo e voltam
      depois que a carteira girar, em até ${number(r.cycleDays)} dias.
    </div>`;
}

function goToTab(tab) {
  state.activeTab = tab;
  requestRender();
}

/**
 * Linha de tarefa com ação direta: registrar o contato, concluir ou reagendar
 * sem sair da Missão do Dia. Sem o botão de registrar, o vendedor precisava
 * caçar o cliente na carteira para lançar o retorno que ele mesmo agendou.
 */
function taskQuickRow(row, mostrarPrazo) {
  const clientKey = row.client_key || "";
  const nome = row.client_name || row.title || "Cliente";
  const prazo = (row.due_at || "").replace("T", " ").slice(0, 16);
  return `
    <div class="timeline-item">
      <strong>${escapeHtml(nome)}</strong>
      <div class="text-small">${escapeHtml(mostrarPrazo ? prazo : (row.title || ""))}</div>
      ${row.description ? `<div class="text-small" style="color:var(--muted)">${escapeHtml(row.description)}</div>` : ""}
      <div class="actions" style="gap:6px">
        <button class="btn btn-primary btn-sm" ${clientKey ? "" : "disabled"}
          onclick="prefillInteractionFromAgenda('${jsAttr(clientKey)}','${jsAttr(nome)}')">📞 Registrar contato</button>
        <button class="btn btn-secondary btn-sm" onclick="completeCrmTask(${Number(row.id)})">Concluir</button>
        <button class="btn btn-ghost btn-sm" onclick="openTaskRescheduleModal(${Number(row.id)})">Reagendar</button>
        ${clientKey ? `<button class="btn btn-ghost btn-sm" onclick="openCrmClient('${jsAttr(clientKey)}', false)">Ficha</button>` : ""}
      </div>
    </div>`;
}

/**
 * Fila de prospecção na Missão do Dia.
 *
 * Vendedor de unidade nova não tem carteira: a fila normal viria vazia e ele
 * abriria o sistema todo dia para não ver nada. Aqui a mesma tela mostra as
 * oficinas que ele está prospectando, com a mesma regra de prioridade — quem
 * está parado há mais tempo primeiro.
 */
function filaProspeccao() {
  const d = state.prospects;
  if (!d || d.error) return "";
  const emImplantacao = Boolean(d.unitPhase?.isDeployment);
  const abertos = (d.prospects || []).filter(
    (p) => ["NOVO", "EM_CONTATO", "QUALIFICADO"].includes(p.status));
  // Só toma a tela de quem realmente precisa: unidade em implantação ou
  // vendedor sem carteira montada.
  const semCarteira = !(state.crm.agenda?.top5 || []).length;
  if (!abertos.length || (!emImplantacao && !semCarteira)) return "";

  const fila = abertos
    .slice()
    .sort((a, b) => (b.daysSinceContact ?? 999) - (a.daysSinceContact ?? 999))
    .slice(0, 5);

  return `
    <div class="table-card" style="border-left:4px solid #27ae60">
      <div class="section-title">
        <div><h3>🌱 Prospecção do dia</h3>
          <div class="text-small">
            ${emImplantacao
              ? "Unidade em implantação — a carteira se forma pelo que você prospectar agora."
              : "Sua carteira ainda está pequena. Estas são as oficinas para trabalhar hoje."}
          </div></div>
        <div class="soft-badge">${abertos.length}</div>
      </div>
      <div class="stack" style="padding-top:8px">
        ${fila.map((p) => `
          <div class="crm-card clean" style="padding:12px">
            <div style="display:flex;justify-content:space-between;gap:10px;flex-wrap:wrap;align-items:start">
              <div style="flex:1;min-width:220px">
                <div style="display:flex;gap:6px;align-items:center;flex-wrap:wrap;margin-bottom:2px">
                  ${prospectStatusBadge(p.status)}
                  ${p.isQualified ? '<span class="status-tag good">4 perguntas ✓</span>' : ""}
                </div>
                <div style="font-weight:700;font-size:13px">${escapeHtml(p.companyName)}</div>
                <div class="text-small" style="color:var(--muted)">
                  ${p.phone ? `📞 ${escapeHtml(p.phone)}` : "sem telefone"}
                  ${p.contactName ? ` · ${escapeHtml(p.contactName)}` : ""}
                  ${p.cityName ? ` · ${escapeHtml(p.cityName)}` : ""}
                </div>
                <div class="text-small" style="color:${(p.daysSinceContact ?? 999) >= 7 ? "var(--bad)" : "var(--muted)"}">
                  ${p.daysSinceContact === null ? "Nunca contatada" : `${p.daysSinceContact} dia(s) sem contato`}
                  ${!p.documentNumber ? " · ⚠ sem CNPJ" : ""}
                </div>
              </div>
              <button class="btn btn-primary btn-sm"
                onclick='contatarProspect(${JSON.stringify(p).replace(/'/g, "&#39;")})'>📞 Registrar contato</button>
            </div>
          </div>`).join("")}
      </div>
      <div class="actions" style="padding-top:8px">
        <button class="btn btn-ghost btn-sm" onclick="goToTab('prospeccao')">Ver todas as oficinas →</button>
      </div>
    </div>`;
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
          <div><span>Média 3 meses ant.</span><strong>${currency(item.averageRevenue)}</strong></div>
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
      ${scoreEnabled()
        ? kpiCard("Meus indicadores detalhados", pct(seller.goalAttainmentPct), "Score", seller.score)
        : kpiCard("Atingimento da meta", pct(seller.goalAttainmentPct), "Ticket médio", currency(seller.ticketAverage || 0))}
    </div>
  `;
}

function todayTaskGroups() {
  const rows = state.crm.taskRows || [];
  // Data LOCAL. toISOString() devolve UTC e, depois das 21h no Brasil, os
  // retornos de hoje sumiam da tela por já ser "amanhã" em UTC.
  const today = dateInDays(0);
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
            <div class="crm-card-essentials" style="margin:0"><div><span>Média 3 meses ant.</span><strong>${currency(item.averageRevenue)}</strong></div></div>
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
              ${overdue.map((row) => taskQuickRow(row, true)).join("")}
            </div>
          </div>
        ` : ""}

        ${dueToday.length > 0 ? `
          <div class="table-card" style="border-left:4px solid #f39c12">
            <div class="section-title">
              <div>
                <h3>📅 Retornos de hoje</h3>
                <div class="text-small">Compromissos que você assumiu para hoje.</div>
              </div>
              <div style="display:flex;align-items:center;gap:8px">
                <button class="btn btn-ghost btn-sm" onclick="goToTab('crm-tarefas')">Ver todas as tarefas →</button>
                <div class="soft-badge">${dueToday.length}</div>
              </div>
            </div>
            <div class="timeline-list">
              ${dueToday.map((row) => taskQuickRow(row, false)).join("")}
            </div>
          </div>
        ` : ""}

        ${filaProspeccao()}

        ${top5.length || !(state.prospects?.unitPhase?.isDeployment) ? `
          <div>
            <div class="section-title" style="margin-bottom:12px">
              <h3>📋 TOP 5 — Contatos do dia</h3>
              <div class="text-small">2 Bronze/Prata · 2 Ouro/Diamante · 1 prospecção/inativo</div>
            </div>
            ${rodizioAviso()}
            <div class="stack">
              ${top5.map((item) => agendaCardV2(item)).join("")
                || emptyStateCard(state.prospects?.unitPhase?.isDeployment
                    ? "Sua carteira ainda está sendo formada. Trabalhe a fila de prospecção acima."
                    : "Sua fila está vazia. Todos os clientes estão ativos!")}
            </div>
          </div>` : ""}

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
        ${s.contactsToday === 0 && s.lastInteractionAt
          ? `<div style="font-size:10px;color:var(--muted);margin-top:4px">último contato ${escapeHtml(String(s.lastInteractionAt).slice(0, 10).split("-").reverse().join("/"))}</div>`
          : ""}
        ${s.contactsToday === 0 && !s.lastInteractionAt
          ? `<div style="font-size:10px;color:var(--muted);margin-top:4px">nunca registrou contato</div>`
          : ""}
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
            <div style="font-size:13px;color:rgba(255,255,255,0.7)">Execução da equipe e riscos que precisam de cobrança</div>
            ${(() => {
              // Seletor de unidade: só para quem enxerga mais de uma
              const scoped = ta?.scopeUnits;
              const units = (scoped && scoped.length ? scoped : (state.options.units || []));
              if (units.length < 2) return "";
              return `
                <select onchange="setMissionUnit(this.value)"
                  style="margin-top:8px;background:rgba(255,255,255,0.15);color:#fff;border:1px solid rgba(255,255,255,0.25);border-radius:6px;padding:4px 8px;font-size:12px">
                  <option value="" ${!state.crm.missionUnit ? "selected" : ""}>Todas as unidades</option>
                  ${units.map((u) => `<option value="${escapeHtml(u)}" ${state.crm.missionUnit === u ? "selected" : ""} style="color:#0f3044">${escapeHtml(u)}</option>`).join("")}
                </select>`;
            })()}
          </div>
          <div style="display:flex;flex-wrap:wrap;gap:8px">
            <div style="background:rgba(255,255,255,0.12);border-radius:8px;padding:8px 16px;text-align:center;min-width:90px">
              <div style="font-size:24px;font-weight:800;color:#f4c25f;line-height:1.1">${taLoading ? "…" : number(ta.totalContactsToday)}</div>
              <div style="font-size:10px;color:rgba(255,255,255,0.7);margin-top:2px">Contatos hoje</div>
              <div style="font-size:10px;color:rgba(255,255,255,0.45)">meta ${taLoading ? "…" : number(ta.teamGoal)}</div>
            </div>
            <div style="background:rgba(255,255,255,0.12);border-radius:8px;padding:8px 16px;text-align:center;min-width:90px">
              ${(() => {
                // Sem meta cadastrada o backend não devolve goalPct — evita "undefined%"
                const gp = Number(ta.goalPct);
                const hasGoal = Number.isFinite(gp) && Number(ta.teamGoal || 0) > 0;
                const color = taLoading || !hasGoal ? "#fff" : gp >= 100 ? "#2ecc71" : gp >= 60 ? "#f4c25f" : "#e74c3c";
                const label = taLoading ? "…" : hasGoal ? `${Math.round(gp)}%` : "—";
                return `<div style="font-size:24px;font-weight:800;color:${color};line-height:1.1">${label}</div>`;
              })()}
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
            <div style="background:rgba(255,255,255,0.12);border-radius:8px;padding:8px 16px;text-align:center;min-width:90px">
              <div style="font-size:24px;font-weight:800;color:${taLoading ? "#fff" : (ta.totalOverdueTasks || 0) > 0 ? "#e74c3c" : "#2ecc71"};line-height:1.1">${taLoading ? "…" : number(ta.totalOverdueTasks || 0)}</div>
              <div style="font-size:10px;color:rgba(255,255,255,0.7);margin-top:2px">Tarefas atrasadas</div>
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

      <!-- Risco na carteira: onde a gestão precisa agir -->
      ${managerRiskBlocks()}

      <!-- Tarefas -->
      <div class="grid-2 crm-grid">
        <div class="table-card">
          <div class="section-title">
            <div><h3>Retornos de hoje</h3><div class="text-small">Compromissos que a equipe assumiu para hoje.</div></div>
            <div class="soft-badge">${number(dueToday.length)}</div>
          </div>
          <div class="timeline-list">
            ${dueToday.map((row) => `<div class="timeline-item"><strong>${escapeHtml(row.client_name)}</strong><div class="text-small">${escapeHtml(row.seller_name || "")} · ${escapeHtml(row.title || "")}</div></div>`).join("") || '<div class="timeline-item"><div class="text-small">Nenhum retorno vencendo hoje.</div></div>'}
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
        </div>
      </div>
    </div>
  `;
}

/**
 * Blocos de risco da visão gerencial da Missão do Dia.
 * O gestor não recebe fila de ligações — recebe onde a execução falhou,
 * sempre com o vendedor responsável ao lado para cobrança direta.
 */
const MES_ABREV = ["jan","fev","mar","abr","mai","jun","jul","ago","set","out","nov","dez"];

/** Converte "2026-06" em "jun/26" para caber nos rótulos. */
function competenceShort(competence) {
  if (!competence || competence.length < 7) return competence || "";
  const ano = competence.slice(2, 4);
  const mes = parseInt(competence.slice(5, 7), 10) - 1;
  return `${MES_ABREV[mes] || "?"}/${ano}`;
}

/**
 * Rótulo da média com o período explícito.
 * A média é sempre a soma dos 3 meses ANTERIORES dividida por 3 — inclusive
 * meses sem compra. Sem dizer o período, o número parece arbitrário.
 */
function averageLabel(item) {
  const basis = item.averageBasis;
  const valor = currency(item.averageRevenue || 0);
  if (!basis || !basis.months?.length) return `média ${valor}/mês`;
  const meses = basis.months.map((m) => m.competence).sort();
  return `média ${valor}/mês (${competenceShort(meses[0])}–${competenceShort(meses[meses.length - 1])})`;
}

/** Memória de cálculo da média, para conferência na ficha do cliente. */
function averageBreakdown(item) {
  const basis = item.averageBasis;
  if (!basis || !basis.months?.length) return "";
  const meses = [...basis.months].sort((a, b) => a.competence.localeCompare(b.competence));
  const semCompra = 3 - (basis.monthsWithPurchase ?? 3);
  return `
    <div style="background:#f7fafc;border:1px solid var(--line);border-radius:6px;padding:10px 12px;margin-top:8px">
      <div style="font-size:11px;font-weight:800;color:var(--muted);letter-spacing:0.06em;margin-bottom:6px">
        COMO A MÉDIA É CALCULADA
      </div>
      <table style="width:100%;font-size:12px">
        <tbody>
          ${meses.map((m) => `
            <tr>
              <td style="padding:2px 0;color:var(--muted)">${escapeHtml(competenceShort(m.competence))}</td>
              <td style="text-align:right;${Number(m.revenue) <= 0 ? "color:var(--bad)" : ""}">${currency(m.revenue)}</td>
            </tr>`).join("")}
          <tr style="border-top:1px solid var(--line)">
            <td style="padding:4px 0;font-weight:700">Soma</td>
            <td style="text-align:right;font-weight:700">${currency(basis.total)}</td>
          </tr>
          <tr>
            <td style="color:var(--muted)">÷ ${basis.divisor} meses</td>
            <td style="text-align:right;font-weight:800;color:var(--accent)">${currency(item.averageRevenue || 0)}</td>
          </tr>
        </tbody>
      </table>
      ${semCompra > 0 ? `<div class="text-small" style="color:var(--muted);margin-top:6px">
        Dividimos sempre por 3, mesmo com ${semCompra} ${semCompra === 1 ? "mês" : "meses"} sem compra —
        a média mostra o volume mensal, não o valor por pedido.
      </div>` : ""}
      <div class="text-small" style="color:var(--muted);margin-top:4px">
        Base: faturamento total do cliente nos 3 meses anteriores a ${escapeHtml(competenceShort(basis.currentCompetence))},
        somando todos os vendedores.
      </div>
    </div>`;
}

function managerRiskBlocks() {
  const risk = state.crm.teamActivity?.risk;
  if (!risk) return "";

  function riskCard(item, mode) {
    const seller = item.assignedSeller || "Sem vendedor";
    const isGap = mode === "gap";
    const accent = isGap ? "#e74c3c" : "#e67e22";
    const motive = isGap
      ? `${item.daysWithoutPurchase != null ? `${item.daysWithoutPurchase} dias sem comprar` : "Sem compra registrada"} · ${
          item.daysWithoutContact == null ? "nunca contatado" : `${item.daysWithoutContact} dias sem contato`}`
      : `Queda de ${pct(Math.abs(Number(item.dropPct || 0)) * 100)} · ${averageLabel(item)}`;
    const classBadge = { DIAMANTE: "💎", OURO: "🥇", PRATA: "🥈", BRONZE: "🥉" }[item.classCode] || "";
    const payload = encodeURIComponent(JSON.stringify({
      clientKey: item.clientKey, clientName: item.clientName, sellerName: seller,
      motive: isGap ? "sem contato" : "queda de faturamento",
    }));
    return `
      <div style="border-left:3px solid ${accent};background:#f7fafc;border-radius:6px;padding:10px 12px;margin-bottom:8px">
        <div style="display:flex;justify-content:space-between;align-items:flex-start;gap:8px;flex-wrap:wrap">
          <div style="min-width:0;flex:1">
            <div style="font-weight:700;font-size:13px">${classBadge} ${escapeHtml(item.clientName || "")}</div>
            <div class="text-small" style="color:var(--muted)">${escapeHtml(item.cityName || "-")} · ${escapeHtml(motive)}</div>
            <div style="font-size:11px;margin-top:4px">
              <span style="background:rgba(15,48,68,0.08);padding:2px 8px;border-radius:4px">👤 ${escapeHtml(seller)}</span>
            </div>
          </div>
          <div style="display:flex;gap:6px;flex-wrap:wrap">
            <button class="btn btn-ghost btn-sm" onclick="openCrmClient('${escapeHtml(item.clientKey)}', false)">Ficha</button>
            <button class="btn btn-secondary btn-sm" onclick="assignTaskToSeller('${payload}')">Cobrar</button>
          </div>
        </div>
      </div>`;
  }

  function block(title, hint, items, total, bySeller, mode, emptyMsg) {
    return `
      <div class="table-card">
        <div class="section-title">
          <div><h3>${title}</h3><div class="text-small">${hint}</div></div>
          <div class="soft-badge" style="${total > 0 ? "background:#fde8e8;color:#e74c3c" : ""}">${number(total)}</div>
        </div>
        ${bySeller.length > 1 ? `
          <div style="display:flex;flex-wrap:wrap;gap:6px;margin-bottom:10px">
            ${bySeller.slice(0, 8).map((s) => `<span class="soft-badge" style="font-size:11px">${escapeHtml(s.sellerName.split(" ")[0])}: ${s.count}</span>`).join("")}
          </div>` : ""}
        <div>${items.map((i) => riskCard(i, mode)).join("") || emptyStateCard(emptyMsg)}</div>
        ${total > items.length ? `<div class="text-small" style="text-align:center;color:var(--muted);margin-top:6px">+ ${number(total - items.length)} cliente(s) nesta condição — veja em Carteira</div>` : ""}
      </div>`;
  }

  return `
    <div class="grid-2 crm-grid">
      ${block(
        "🔴 Cobertura falha",
        `Parou de comprar e ninguém contatou há ${risk.coverageGapDays}+ dias.`,
        risk.coverageGap || [], risk.coverageGapTotal || 0, risk.coverageGapBySeller || [],
        "gap", "✅ Nenhum cliente em risco sem contato.")}
      ${block(
        "🟠 Cliente grande em queda",
        "Diamante e Ouro comprando menos que a própria média.",
        risk.highValueDrop || [], risk.highValueDropTotal || 0, risk.highValueDropBySeller || [],
        "drop", "✅ Nenhum cliente de alto valor em queda.")}
    </div>
  `;
}

/** Cria tarefa de cobrança atribuída ao vendedor responsável pelo cliente. */
async function assignTaskToSeller(encodedPayload) {
  let data;
  try {
    data = JSON.parse(decodeURIComponent(encodedPayload));
  } catch (e) {
    addMessage("error", "Não foi possível identificar o cliente.");
    return;
  }
  if (!data.sellerName || data.sellerName === "Sem vendedor") {
    addMessage("error", "Este cliente não tem vendedor responsável definido.");
    return;
  }
  if (!confirm(`Criar tarefa para ${data.sellerName} contatar ${data.clientName}?`)) return;
  try {
    const result = await api("/api/crm/tasks/assign", {
      method: "POST",
      body: JSON.stringify({
        clientKey: data.clientKey,
        clientName: data.clientName,
        sellerName: data.sellerName,
        title: `Contatar ${data.clientName}`,
        description: `Cobrança da gestão — ${data.motive}.`,
      }),
    });
    addMessage(result.duplicated ? "warn" : "success", result.message || "Tarefa criada.");
    await loadCrmData();
  } catch (error) {
    addMessage("error", error.message);
  }
}

/**
 * Painel de ação da ficha do cliente.
 * Substitui o antigo bloco genérico: traz a próxima ação com números concretos,
 * ofertas rotuladas por motivo e os scripts prontos para copiar.
 */
function clientActionPanel(client) {
  const repurchase = client.offerRepurchase || [];
  const opportunity = client.offerOpportunity || [];
  const scripts = client.scripts || [];
  const openScript = state.ui.openScriptId;

  function offerRow(o) {
    const isRepurchase = o.type === "RECOMPRA";
    return `
      <div style="display:flex;gap:10px;align-items:flex-start;padding:8px 0;border-bottom:1px solid var(--line)">
        <span class="soft-badge" style="background:${isRepurchase ? "#e8f5e9" : "#fff3e0"};color:${isRepurchase ? "#2e7d32" : "#e65100"};white-space:nowrap;font-size:11px">
          ${isRepurchase ? "🔁 Recompra" : "✨ Oportunidade"}
        </span>
        <div style="min-width:0;flex:1">
          <div style="font-weight:700;font-size:13px">${escapeHtml(o.title)}</div>
          <div class="text-small" style="color:var(--muted)">${escapeHtml(o.reason || "")}</div>
        </div>
      </div>`;
  }

  const offers = [...repurchase.slice(0, 3), ...opportunity.slice(0, 2)];

  return `
    <div class="subtle-card padded-card">
      <div class="section-title">
        <div><h3>O que fazer agora</h3>
        <div class="text-small">Ação sugerida com base no histórico deste cliente.</div></div>
      </div>

      <div style="background:#0f3044;color:#fff;border-radius:8px;padding:12px 14px;margin-bottom:12px">
        <div style="font-size:10px;font-weight:800;color:#f4c25f;letter-spacing:0.08em;margin-bottom:4px">PRÓXIMA AÇÃO</div>
        <div style="font-size:14px;line-height:1.5">${escapeHtml(client.nextAction || crmRecommendedAction(client))}</div>
      </div>

      ${offers.length ? `
        <div style="margin-bottom:12px">
          <div style="font-size:11px;font-weight:800;color:var(--muted);letter-spacing:0.06em;margin-bottom:4px">O QUE OFERECER</div>
          ${offers.map(offerRow).join("")}
        </div>` : ""}

      ${client.questionPrimary ? `
        <div style="margin-bottom:12px">
          <div style="font-size:11px;font-weight:800;color:var(--muted);letter-spacing:0.06em;margin-bottom:4px">PERGUNTA PARA ABRIR A CONVERSA</div>
          <div style="font-style:italic;font-size:13px">"${escapeHtml(client.questionPrimary)}"</div>
        </div>` : ""}

      ${scripts.length ? `
        <div>
          <div style="font-size:11px;font-weight:800;color:var(--muted);letter-spacing:0.06em;margin-bottom:6px">
            SCRIPTS PRONTOS <span class="soft-badge">${scripts.length}</span>
          </div>
          ${scripts.map((s) => `
            <div style="border:1px solid var(--line);border-radius:6px;margin-bottom:6px;overflow:hidden">
              <div onclick="toggleScript(${s.id})" style="display:flex;justify-content:space-between;align-items:center;gap:8px;padding:8px 10px;cursor:pointer;background:#f7fafc">
                <div style="min-width:0">
                  <span style="font-size:14px">${s.category === "whatsapp" ? "💬" : "📞"}</span>
                  <strong style="font-size:12px">${escapeHtml(s.title)}</strong>
                </div>
                <span style="color:var(--muted);font-size:12px">${openScript === s.id ? "▲" : "▼"}</span>
              </div>
              ${openScript === s.id ? `
                <div style="padding:10px 12px">
                  ${s.hint ? `<div class="text-small" style="color:var(--muted);margin-bottom:8px;font-style:italic">${escapeHtml(s.hint)}</div>` : ""}
                  <pre style="white-space:pre-wrap;font-family:inherit;font-size:13px;line-height:1.6;margin:0">${escapeHtml(s.body)}</pre>
                  <div class="actions" style="margin-top:10px">
                    <button class="btn btn-secondary btn-sm" onclick="copyScript(${s.id})">📋 Copiar</button>
                    ${s.category === "whatsapp" && client.phone ? `<button class="btn btn-primary btn-sm" onclick="openWhatsApp('${escapeHtml(client.phone)}', ${s.id})">Abrir WhatsApp</button>` : ""}
                  </div>
                </div>` : ""}
            </div>`).join("")}
        </div>` : ""}
    </div>
  `;
}

function toggleScript(id) {
  state.ui.openScriptId = state.ui.openScriptId === id ? null : id;
  requestRender();
}

function currentScriptById(id) {
  const client = state.crm.selectedClient?.summary;
  return (client?.scripts || []).find((s) => s.id === id);
}

async function copyScript(id) {
  const script = currentScriptById(id);
  if (!script) return;
  if (await copyToClipboard(script.body)) {
    addMessage("success", "Texto copiado.");
  } else {
    showCopyFallback(script.body, script.title);
  }
}

function openWhatsApp(phone, scriptId) {
  const script = currentScriptById(scriptId);
  const digits = String(phone || "").replace(/\D/g, "");
  if (!digits) { addMessage("error", "Cliente sem telefone cadastrado."); return; }
  const withCountry = digits.length <= 11 ? `55${digits}` : digits;
  const text = script ? encodeURIComponent(script.body) : "";
  window.open(`https://wa.me/${withCountry}?text=${text}`, "_blank");
}

// ─── Biblioteca de vendas ───────────────────────────────────────────────────

async function loadContentLibrary() {
  try {
    const all = userCanManageUsers() ? "?all=1" : "";
    state.content = await api(`/api/content${all}`);
  } catch (e) {
    state.content = { error: e.message, items: [], categories: [], situations: [] };
  }
  requestRender();
}

function bibliotecaView() {
  if (!state.content) { loadContentLibrary(); return `<div class="loader panel">Carregando biblioteca…</div>`; }
  if (state.content.error) return `<div class="message error">${escapeHtml(state.content.error)}</div>`;

  const cats = state.content.categories || [];
  const sits = state.content.situations || [];
  const canEdit = Boolean(state.content.canEdit);
  const activeCat = state.ui.libraryCategory || cats[0]?.id || "ligacao";
  const items = (state.content.items || []).filter((i) => i.category === activeCat);
  const sitLabel = (id) => (sits.find((s) => s.id === id) || {}).label || id;
  const editor = state.contentEditor;

  return `
    <div class="stack">
      <div class="form-card" style="padding:12px 18px">
        <div style="display:flex;gap:8px;flex-wrap:wrap;align-items:center">
          ${cats.map((c) => `
            <button class="subtab-button ${activeCat === c.id ? "active" : ""}"
              onclick="state.ui.libraryCategory='${c.id}';requestRender()">
              ${c.icon} ${escapeHtml(c.label)}
              <span class="soft-badge" style="margin-left:4px">${(state.content.items || []).filter((i) => i.category === c.id).length}</span>
            </button>`).join("")}
          ${canEdit ? `<button class="btn btn-primary btn-sm" style="margin-left:auto" onclick="startContentEdit(null)">+ Novo conteúdo</button>` : ""}
        </div>
      </div>

      ${canEdit && editor ? contentEditorCard() : ""}

      ${items.length ? items.map((item) => `
        <div class="form-card ${item.isActive ? "" : "muted"}" style="${item.isActive ? "" : "opacity:.55"}">
          <div class="section-title">
            <div>
              <h3 style="font-size:15px">${escapeHtml(item.title)}</h3>
              <div class="text-small">
                <span class="soft-badge">${escapeHtml(sitLabel(item.situation))}</span>
                ${item.isSystem ? ' <span class="soft-badge">padrão</span>' : ""}
                ${item.isActive ? "" : ' <span class="soft-badge" style="background:#fde8e8;color:#e74c3c">inativo</span>'}
              </div>
            </div>
            <div style="display:flex;gap:6px">
              <button class="btn btn-ghost btn-sm" onclick="copyLibraryText(${item.id})">📋 Copiar</button>
              ${canEdit ? `<button class="btn btn-ghost btn-sm" onclick="startContentEdit(${item.id})">Editar</button>` : ""}
              ${canEdit && !item.isSystem ? `<button class="btn btn-ghost btn-sm" onclick="deleteContent(${item.id})">Excluir</button>` : ""}
            </div>
          </div>
          ${item.hint ? `<div class="message" style="font-size:12px;font-style:italic;margin-bottom:8px">${escapeHtml(item.hint)}</div>` : ""}
          <pre style="white-space:pre-wrap;font-family:inherit;font-size:13px;line-height:1.65;margin:0">${escapeHtml(item.body)}</pre>
        </div>`).join("") : emptyStateCard("Nenhum conteúdo nesta categoria ainda.")}

      <div class="message" style="font-size:12px">
        Os marcadores <strong>{cliente}</strong>, <strong>{vendedor}</strong>, <strong>{item}</strong> e
        <strong>{dias}</strong> são preenchidos automaticamente quando o script aparece na ficha do cliente.
      </div>
    </div>
  `;
}

function contentEditorCard() {
  const e = state.contentEditor;
  const cats = state.content.categories || [];
  const sits = state.content.situations || [];
  return `
    <div class="form-card" id="content-editor">
      <div class="section-title">
        <div><h3>${e.id ? "Editar conteúdo" : "Novo conteúdo"}</h3></div>
        <button class="btn btn-ghost btn-sm" onclick="cancelContentEdit()">Cancelar</button>
      </div>
      <form onsubmit="saveContent(event)" class="stack">
        <div class="two-column-form">
          <div class="field"><label>Categoria</label>
            <select onchange="state.contentEditor.category=this.value">
              ${cats.map((c) => `<option value="${c.id}" ${e.category === c.id ? "selected" : ""}>${escapeHtml(c.label)}</option>`).join("")}
            </select></div>
          <div class="field"><label>Situação</label>
            <select onchange="state.contentEditor.situation=this.value">
              ${sits.map((s) => `<option value="${s.id}" ${e.situation === s.id ? "selected" : ""}>${escapeHtml(s.label)}</option>`).join("")}
            </select></div>
          <div class="field field-span-2"><label>Título</label>
            <input value="${escapeHtml(e.title)}" oninput="state.contentEditor.title=this.value" required /></div>
          <div class="field field-span-2"><label>Dica para o vendedor (opcional)</label>
            <input value="${escapeHtml(e.hint)}" oninput="state.contentEditor.hint=this.value" placeholder="Objetivo da abordagem, o que evitar" /></div>
          <div class="field field-span-2"><label>Conteúdo</label>
            <textarea rows="14" style="font-family:inherit;line-height:1.6" oninput="state.contentEditor.body=this.value" required>${escapeHtml(e.body)}</textarea></div>
          <div class="field field-span-2">
            <label class="checkbox-item" style="cursor:pointer">
              <input type="checkbox" ${e.isActive ? "checked" : ""} onchange="state.contentEditor.isActive=this.checked" />
              <span>Ativo (aparece para os vendedores)</span>
            </label></div>
        </div>
        <div class="actions">
          <button class="btn btn-primary" type="submit">Salvar</button>
          <button class="btn btn-ghost" type="button" onclick="cancelContentEdit()">Cancelar</button>
        </div>
      </form>
    </div>`;
}

function startContentEdit(id) {
  const item = id ? (state.content.items || []).find((i) => i.id === id) : null;
  state.contentEditor = item
    ? { ...item }
    : { id: "", category: state.ui.libraryCategory || "ligacao", situation: "GERAL",
        title: "", body: "", hint: "", isActive: true };
  requestRender();
  document.getElementById("content-editor")?.scrollIntoView({ behavior: "smooth", block: "center" });
}

function cancelContentEdit() {
  state.contentEditor = null;
  requestRender();
}

async function saveContent(event) {
  if (event) event.preventDefault();
  const e = state.contentEditor;
  if (!e.title?.trim() || !e.body?.trim()) { addMessage("error", "Título e conteúdo são obrigatórios."); return; }
  try {
    const r = await api("/api/content/save", {
      method: "POST",
      body: JSON.stringify({
        id: e.id || undefined, category: e.category, situation: e.situation,
        title: e.title, body: e.body, hint: e.hint, isActive: e.isActive,
      }),
    });
    addMessage("success", r.message || "Conteúdo salvo.");
    state.contentEditor = null;
    await loadContentLibrary();
  } catch (err) {
    addMessage("error", err.message);
  }
}

async function deleteContent(id) {
  if (!confirm("Excluir este conteúdo?")) return;
  try {
    await api("/api/content/delete", { method: "POST", body: JSON.stringify({ id }) });
    addMessage("success", "Conteúdo excluído.");
    await loadContentLibrary();
  } catch (err) {
    addMessage("error", err.message);
  }
}

async function copyLibraryText(id) {
  const item = (state.content.items || []).find((i) => i.id === id);
  if (!item) return;
  if (await copyToClipboard(item.body)) {
    addMessage("success", "Texto copiado.");
  } else {
    showCopyFallback(item.body, item.title);
  }
}

// ─── Clientes recorrentes sem vendedor ──────────────────────────────────────

async function loadUnassignedClients() {
  const f = state.crm.unassignedFilters || {};
  try {
    const qs = new URLSearchParams();
    if (f.minMonths) qs.set("minMonths", f.minMonths);
    if (f.window) qs.set("window", f.window);
    state.crm.unassigned = await api(`/api/crm/unassigned-clients?${qs.toString()}`);
  } catch (e) {
    state.crm.unassigned = { error: e.message, items: [], total: 0 };
  }
  requestRender();
  return state.crm.unassigned;   // o helper lê o erro daqui para avisar
}

// ─── Conciliação por código do cliente ─────────────────────────────────────
//
// Só para as linhas marcadas "sem cadastro". O casamento automático por nome
// continua sendo a regra e não é tocado — aqui o gerente resolve à mão o que
// sobrou, informando o código do Alfa, que é o dado que ele tem em mãos.

function abrirConciliacao(nomeFaturamento) {
  state.crm.reconcile = { salesName: nomeFaturamento, code: "", found: null,
                          candidates: null, searching: false, saving: false, notFound: false };
  requestRender();
}

function fecharConciliacao() {
  state.crm.reconcile = null;
  requestRender();
}

async function buscarClientePorCodigo() {
  const r = state.crm.reconcile;
  if (!r) return;
  const codigo = (r.code || "").trim();
  if (!codigo) { addMessage("warn", "Informe o código do cliente."); return; }
  r.searching = true; r.found = null; r.notFound = false; r.candidates = null;
  requestRender();
  try {
    // Manda o nome do faturamento junto: não achando o código, o servidor
    // devolve candidatos por razão social em vez de só dizer "não existe".
    const url = `/api/crm/clients/by-code?code=${encodeURIComponent(codigo)}`
              + `&name=${encodeURIComponent(r.salesName || "")}`;
    const resposta = await api(url);
    if (state.crm.reconcile) {
      state.crm.reconcile.found = resposta.client || null;
      state.crm.reconcile.candidates = resposta.candidates || [];
      state.crm.reconcile.notFound = !resposta.client;
    }
  } catch (error) {
    addMessage("error", error.message);
  } finally {
    if (state.crm.reconcile) state.crm.reconcile.searching = false;
    requestRender();
  }
}

/** Sugere candidatos pela razão social, sem exigir o código. */
async function sugerirPorRazaoSocial() {
  const r = state.crm.reconcile;
  if (!r) return;
  r.searching = true; r.candidates = null; requestRender();
  try {
    const resposta = await api(
      `/api/crm/clients/by-code?code=&name=${encodeURIComponent(r.salesName || "")}`);
    if (state.crm.reconcile) {
      state.crm.reconcile.candidates = resposta.candidates || [];
      state.crm.reconcile.notFound = false;
    }
  } catch (error) {
    addMessage("error", error.message);
  } finally {
    if (state.crm.reconcile) state.crm.reconcile.searching = false;
    requestRender();
  }
}

function escolherCandidato(codigo) {
  const r = state.crm.reconcile;
  if (!r) return;
  r.found = (r.candidates || []).find((c) => String(c.client_code) === String(codigo)) || null;
  r.code = codigo;
  r.candidates = null;
  r.notFound = false;
  requestRender();
}

async function confirmarConciliacao() {
  const r = state.crm.reconcile;
  if (!r || !r.found || r.saving) return;
  r.saving = true; requestRender();
  try {
    const resposta = await api("/api/crm/clients/alias", {
      method: "POST",
      body: JSON.stringify({ salesName: r.salesName, clientCode: r.found.client_code }),
    });
    addMessage("success", resposta.message || "Cliente conciliado.");
    state.crm.reconcile = null;
    await loadUnassignedClients();
  } catch (error) {
    addMessage("error", error.message);
    if (state.crm.reconcile) state.crm.reconcile.saving = false;
  }
  requestRender();
}

function conciliacaoModal() {
  const r = state.crm.reconcile;
  if (!r) return "";
  const c = r.found;
  return `
    <div class="client-drawer-overlay open modal-dim" onclick="fecharConciliacao()">
      <div class="panel modal-panel" style="max-width:560px;margin:8vh auto;padding:22px" onclick="event.stopPropagation()">
        <div class="section-title">
          <div>
            <h3>🔗 Conciliar cliente</h3>
            <div class="text-small">No faturamento: <strong>${escapeHtml(r.salesName)}</strong></div>
          </div>
          <button class="btn btn-ghost btn-sm" onclick="fecharConciliacao()">Fechar</button>
        </div>

        <div class="text-small" style="color:var(--muted);margin:10px 0">
          Este nome não casou com nenhum cliente do cadastro. Informe o código do cliente
          no Alfa para ligar os dois.
        </div>

        <div style="display:flex;gap:8px">
          <input style="flex:1" value="${escapeHtml(r.code || "")}"
            placeholder="Código do cliente — ex: 70123"
            oninput="state.crm.reconcile.code=this.value"
            onkeydown="if(event.key==='Enter'){event.preventDefault();buscarClientePorCodigo();}" />
          <button class="btn btn-secondary" type="button" onclick="buscarClientePorCodigo()">
            ${r.searching ? "Buscando…" : "Buscar"}</button>
        </div>

        ${c ? `
          <div style="margin-top:12px;background:#f5f9ff;border:1px solid var(--accent);
                      border-radius:10px;padding:12px">
            <div style="font-weight:700;font-size:14px">${escapeHtml(c.client_name)}</div>
            <div class="text-small" style="color:var(--muted)">
              cód. ${escapeHtml(c.client_code)}${c.city_name ? ` · ${escapeHtml(c.city_name)}` : ""}
              ${c.document_number ? ` · ${escapeHtml(c.document_number)}` : ""}
            </div>
            <div class="text-small" style="margin-top:4px">
              ${c.seller_name
                ? `Vendedor no cadastro: <strong>${escapeHtml(c.seller_name)}</strong>`
                : '<span style="color:var(--bad)">Sem vendedor no cadastro</span> — segue nesta lista até você atribuir um.'}
            </div>
          </div>
          <div class="actions" style="margin-top:14px">
            <button class="btn btn-primary" ${r.saving ? "disabled" : ""} onclick="confirmarConciliacao()">
              ${r.saving ? "Vinculando…" : "Vincular este cliente"}</button>
            <button class="btn btn-ghost" onclick="fecharConciliacao()">Cancelar</button>
          </div>` : ""}

        ${r.notFound && !(r.candidates || []).length ? `
          <div class="text-small" style="margin-top:12px;color:var(--bad)">
            Nenhum cliente com este código no cadastro do CRM. Ele pode existir no Alfa e
            ainda não ter entrado na última importação de cadastro de clientes.
          </div>` : ""}

        ${!c ? `
          <div style="margin-top:12px">
            <button class="btn btn-ghost btn-sm" type="button" onclick="sugerirPorRazaoSocial()">
              Não sei o código — buscar pela razão social
            </button>
          </div>` : ""}

        ${(r.candidates || []).length ? `
          <div style="border:1px solid var(--line);border-radius:8px;max-height:260px;overflow:auto;margin-top:10px">
            <div class="text-small" style="padding:8px 10px;background:#f5f7f9;color:var(--muted)">
              ${number(r.candidates.length)} candidato(s) por razão social
            </div>
            ${r.candidates.map((cd) => `
              <button type="button" onclick="escolherCandidato('${jsAttr(cd.client_code)}')"
                style="width:100%;text-align:left;border:none;background:#fff;cursor:pointer;
                       padding:8px 10px;border-bottom:1px solid var(--line)">
                <div style="font-weight:700;font-size:13px">${escapeHtml(cd.client_name)}</div>
                <div class="text-small" style="color:var(--muted)">
                  cód. ${escapeHtml(cd.client_code)}${cd.city_name ? ` · ${escapeHtml(cd.city_name)}` : ""}
                  ${cd.seller_name ? ` · ${escapeHtml(cd.seller_name)}` : " · sem vendedor"}
                </div>
              </button>`).join("")}
          </div>` : ""}
      </div>
    </div>
  `;
}

function semVendedorView() {
  const data = state.crm.unassigned;
  if (!data) { loadUnassignedClients(); return `<div class="loader panel">Buscando clientes sem vendedor…</div>`; }
  if (data.error) return `<div class="message error">${escapeHtml(data.error)}</div>`;

  const f = state.crm.unassignedFilters || { minMonths: 2, window: 6 };
  const items = data.items || [];
  const c = data.criteria || {};

  return `
    <div class="stack">
      <div class="kpi-grid">
        ${kpiCard("Clientes sem dono", number(data.total), "Faturamento envolvido", currency(data.totalRevenue || 0))}
        ${kpiCard("Critério", `${c.minMonths || 2}+ meses`, "Janela analisada", `${escapeHtml(c.windowStart || "")} a ${escapeHtml(c.windowEnd || "")}`)}
      </div>

      <div class="form-card" style="padding:12px 18px">
        <div style="display:flex;gap:12px;flex-wrap:wrap;align-items:end">
          <div class="field" style="min-width:150px">
            <label>Compraram em pelo menos</label>
            <select onchange="state.crm.unassignedFilters.minMonths=this.value;loadUnassignedClients()">
              ${[2,3,4,6].map((v) => `<option value="${v}" ${String(f.minMonths) === String(v) ? "selected" : ""}>${v} meses</option>`).join("")}
            </select>
          </div>
          <div class="field" style="min-width:150px">
            <label>Janela de análise</label>
            <select onchange="state.crm.unassignedFilters.window=this.value;loadUnassignedClients()">
              ${[3,6,12].map((v) => `<option value="${v}" ${String(f.window) === String(v) ? "selected" : ""}>últimos ${v} meses</option>`).join("")}
            </select>
          </div>
          ${botaoAtualizar("semVendedor", "loadUnassignedClients()", { mensagem: "Lista de clientes sem vendedor atualizada." })}
          <button class="btn btn-ghost btn-sm" onclick="exportUnassignedXLSX()">↓ Exportar</button>
        </div>
        <div class="text-small" style="color:var(--muted);margin-top:8px">
          Clientes que compram com frequência mas não têm vendedor no cadastro do CRM.
          Sem dono definido, ninguém previne a perda. Use a coluna "Quem atendeu" para decidir a atribuição.
        </div>
      </div>

      ${items.length ? `
        <div class="table-card">
          <div class="table-wrap">
            <table class="table-sticky-actions">
              <thead>
                <tr>
                  <th>Cliente</th><th>Cidade</th><th>Unidade</th>
                  <th>Recorrência</th><th>Faturamento</th><th>Média/mês</th>
                  <th>Última compra</th><th>Quem atendeu</th><th style="text-align:right">Ações</th>
                </tr>
              </thead>
              <tbody>
                ${items.map((i) => `
                  <tr>
                    <td>
                      <div style="display:flex;gap:6px;align-items:center;flex-wrap:wrap">
                        ${seloPessoa(i.personType)}
                        <strong>${escapeHtml(i.clientName)}</strong>
                      </div>
                      ${i.clientKey ? `<div class="text-small" style="color:var(--muted)">cód. ${escapeHtml(i.clientKey)}</div>` : ""}
                      ${i.aliasOf ? `<div class="text-small" style="color:var(--muted)">conciliado com ${escapeHtml(i.aliasOf)}</div>` : ""}
                    </td>
                    <td class="text-small">${escapeHtml(i.cityName || "-")}</td>
                    <td class="text-small">${escapeHtml(i.unitName || "-")}</td>
                    <td><span class="soft-badge">${i.months} ${i.months === 1 ? "mês" : "meses"}</span></td>
                    <td>${currency(i.revenue)}</td>
                    <td>${currency(i.avgMonthly)}</td>
                    <td class="text-small">${escapeHtml((i.lastPurchaseAt || "").slice(0, 10))}</td>
                    <td class="text-small">
                      ${(i.sellers || []).map((sv) => `
                        <div style="white-space:nowrap">
                          ${escapeHtml(sv.sellerName)}
                          <span style="color:var(--muted)">· ${sv.months}m · ${currency(sv.revenue)}</span>
                        </div>`).join("") || '<span style="color:var(--muted)">—</span>'}
                      ${i.sellerCount > 5 ? `<div style="color:var(--muted)">+${i.sellerCount - 5} outros</div>` : ""}
                    </td>
                    <td style="text-align:right;white-space:nowrap">
                      ${i.clientKey
                        ? `<button class="btn btn-ghost btn-sm" type="button" onclick="openCrmClient('${escapeHtml(i.clientKey)}', false)">Ficha</button>`
                        : `<button class="btn btn-secondary btn-sm" type="button"
                             title="Sem cadastro: o nome do faturamento não casa com nenhum cliente. Informe o código para ligar os dois."
                             onclick="abrirConciliacao('${jsAttr(i.clientName)}')">🔗 Conciliar</button>`}
                    </td>
                  </tr>`).join("")}
              </tbody>
            </table>
          </div>
          ${data.total > items.length ? `<div class="text-small" style="text-align:center;color:var(--muted);margin-top:8px">Exibindo ${items.length} de ${number(data.total)}</div>` : ""}
        </div>` : emptyStateCard("Nenhum cliente recorrente sem vendedor com esse critério. 👏")}
    </div>
  `;
}

/**
 * Copia texto para a área de transferência.
 *
 * A API navigator.clipboard só existe em contexto seguro (HTTPS ou localhost).
 * O servidor é acessado por http://IP na rede local, então ela não está
 * disponível — daí o fallback com execCommand, que funciona em HTTP.
 * Retorna true se copiou.
 */
async function copyToClipboard(text) {
  if (!text) return false;
  // Caminho moderno (HTTPS/localhost)
  if (navigator.clipboard && window.isSecureContext) {
    try {
      await navigator.clipboard.writeText(text);
      return true;
    } catch (e) {
      // cai para o fallback
    }
  }
  // Fallback: textarea temporária fora da tela + execCommand
  try {
    const ta = document.createElement("textarea");
    ta.value = text;
    ta.setAttribute("readonly", "");
    ta.style.position = "fixed";
    ta.style.top = "-9999px";
    ta.style.left = "-9999px";
    ta.style.opacity = "0";
    document.body.appendChild(ta);
    ta.focus();
    ta.select();
    ta.setSelectionRange(0, ta.value.length);  // iOS
    const ok = document.execCommand("copy");
    document.body.removeChild(ta);
    return ok;
  } catch (e) {
    return false;
  }
}

/** Última alternativa: abre o texto para o usuário selecionar e copiar na mão. */
function showCopyFallback(text, title) {
  state.crm.copyFallback = { text, title: title || "Copie o texto" };
  requestRender();
}

function closeCopyFallback() {
  state.crm.copyFallback = null;
  requestRender();
}

function copyFallbackModal() {
  const cf = state.crm.copyFallback;
  if (!cf) return "";
  return `
    <div class="client-drawer-overlay open modal-dim" onclick="closeCopyFallback()">
      <div class="panel modal-panel" style="max-width:640px;margin:8vh auto;padding:20px" onclick="event.stopPropagation()">
        <div class="section-title">
          <div><h3>${escapeHtml(cf.title)}</h3>
          <div class="text-small">Selecione o texto abaixo e copie com Ctrl+C.</div></div>
          <button class="btn btn-ghost btn-sm" onclick="closeCopyFallback()">Fechar</button>
        </div>
        <textarea readonly onclick="this.select()" rows="14"
          style="width:100%;font-family:inherit;font-size:13px;line-height:1.6">${escapeHtml(cf.text)}</textarea>
        <div class="actions" style="margin-top:10px">
          <button class="btn btn-primary" onclick="document.querySelector('.panel textarea')?.select();document.execCommand('copy');addMessage('success','Texto copiado.');closeCopyFallback()">Selecionar e copiar</button>
        </div>
      </div>
    </div>`;
}

// ─── Limites do farol ───────────────────────────────────────────────────────

async function loadKpiThresholds() {
  try {
    state.kpiThresholds = await api("/api/kpi-thresholds");
  } catch (e) {
    state.kpiThresholds = { error: e.message, metrics: [] };
  }
  requestRender();
}

function kpiThresholdsCard() {
  if (!userCanManageUsers()) return "";
  const data = state.kpiThresholds;
  if (!data) { loadKpiThresholds(); return `<div class="loader panel">Carregando limites do farol…</div>`; }
  if (data.error) return `<div class="message error">${escapeHtml(data.error)}</div>`;

  const dirLabel = (d) => (d === "higher" ? "quanto maior, melhor" : "quanto menor, melhor");
  const basisLabel = (b) => (b === "pace" ? "compara com o ritmo esperado" : "valor absoluto");

  return `
    <div class="form-card">
      <div class="section-title">
        <div><h3>Limites do farol</h3>
        <div class="text-small">Define quando cada indicador fica verde, âmbar ou vermelho.</div></div>
      </div>
      <div class="table-wrap">
        <table>
          <thead>
            <tr>
              <th>Indicador</th><th>Critério</th>
              <th style="color:#1e8e3e">▲ No ritmo</th>
              <th style="color:#b06000">◆ Atenção</th>
              <th>Ativo</th><th></th>
            </tr>
          </thead>
          <tbody>
            ${(data.metrics || []).map((m) => `
              <tr>
                <td>
                  <strong>${escapeHtml(m.label)}</strong>
                  <div class="text-small" style="color:var(--muted)">${escapeHtml(m.hint || "")}</div>
                </td>
                <td class="text-small" style="color:var(--muted)">
                  ${escapeHtml(dirLabel(m.direction))}<br>${escapeHtml(basisLabel(m.basis))}
                </td>
                <td><input id="thr-good-${m.id}" type="number" step="0.01" value="${m.good_at}" style="width:90px" />${m.unit ? ` ${escapeHtml(m.unit)}` : ""}</td>
                <td><input id="thr-warn-${m.id}" type="number" step="0.01" value="${m.warn_at}" style="width:90px" />${m.unit ? ` ${escapeHtml(m.unit)}` : ""}</td>
                <td><input id="thr-active-${m.id}" type="checkbox" ${m.is_active ? "checked" : ""} /></td>
                <td><button class="btn btn-secondary btn-sm" type="button" onclick="saveKpiThreshold('${m.id}')">Salvar</button></td>
              </tr>`).join("")}
          </tbody>
        </table>
      </div>
      <div class="message" style="font-size:12px;margin-top:10px">
        <strong>Como o % de atingimento é avaliado:</strong> não contra os 100% do fechamento,
        e sim contra o ritmo esperado até hoje. No dia 3 de 21 dias úteis, espera-se 14,3% da meta —
        então 12,2% equivale a 85% do ritmo, o que é atenção e não crise.
      </div>
    </div>`;
}

async function saveKpiThreshold(metricId) {
  const goodAt = document.getElementById(`thr-good-${metricId}`)?.value;
  const warnAt = document.getElementById(`thr-warn-${metricId}`)?.value;
  const isActive = document.getElementById(`thr-active-${metricId}`)?.checked;
  if (goodAt === "" || warnAt === "") { addMessage("error", "Preencha os dois limites."); return; }
  try {
    const r = await api("/api/kpi-thresholds/save", {
      method: "POST",
      body: JSON.stringify({ metricId, goodAt: Number(goodAt), warnAt: Number(warnAt), isActive }),
    });
    addMessage("success", r.message || "Limites salvos.");
    await loadKpiThresholds();
    await loadDashboard();
  } catch (e) {
    addMessage("error", e.message);
  }
}

// ─── Cobrar contato a partir da ficha do cliente ────────────────────────────

/**
 * Abre o modal de cobrança. Se o cliente já tem vendedor no cadastro, ele vem
 * pré-selecionado; se não tem, o gestor escolhe entre os vendedores da unidade.
 */
function openAssignTaskModal(clientKey) {
  const detail = state.crm.selectedClient;
  const client = detail?.summary || {};
  if (!clientKey || !detail?.canAssignTask) return;

  const sugerido = client.assignedSeller || "";
  const hoje = new Date();
  hoje.setDate(hoje.getDate() + 1);      // vencimento padrão: amanhã
  const venc = hoje.toISOString().slice(0, 10);

  state.crm.assignTask = {
    clientKey,
    clientName: client.clientName || clientKey,
    sellerName: sugerido,
    hadSeller: Boolean(sugerido),
    dueAt: venc,
    reason: sugerirMotivoCobranca(client),
    saving: false,
  };
  requestRender();
}

/** Motivo pré-preenchido conforme a situação do cliente. */
function sugerirMotivoCobranca(client) {
  const dias = client.daysWithoutPurchase;
  if (client.statusCode === "INATIVO") return `Cliente inativo há ${dias || "?"} dias — entender o motivo da parada`;
  if (client.statusCode === "PRE_INATIVO") return "Cliente espaçando pedidos — contato preventivo";
  if (Number(client.currentRevenue || 0) <= 0) return "Sem compra neste mês — provocar reposição";
  if (Number(client.dropPct || 0) <= -0.1) return "Queda de faturamento — investigar";
  return "Contato de acompanhamento";
}

function closeAssignTaskModal() {
  state.crm.assignTask = null;
  requestRender();
}

function assignTaskModal() {
  const t = state.crm.assignTask;
  if (!t) return "";
  const vendedores = state.crm.selectedClient?.assignableSellers || [];
  const preferidos = vendedores.filter((v) => v.preferred);
  const demais = vendedores.filter((v) => !v.preferred);

  return `
    <div class="client-drawer-overlay open modal-dim" onclick="closeAssignTaskModal()">
      <div class="panel modal-panel" style="max-width:520px;margin:10vh auto;padding:22px" onclick="event.stopPropagation()">
        <div class="section-title">
          <div>
            <h3>📣 Cobrar contato</h3>
            <div class="text-small">${escapeHtml(t.clientName)}</div>
          </div>
          <button class="btn btn-ghost btn-sm" onclick="closeAssignTaskModal()">Fechar</button>
        </div>

        ${!t.hadSeller ? `
          <div class="message" style="background:#fff3e0;color:#e65100;font-size:12px">
            ⚠ Este cliente não tem vendedor no cadastro. Escolha quem deve fazer o contato.
          </div>` : ""}

        <div class="field" style="margin-top:12px">
          <label>Vendedor responsável ${!t.hadSeller ? '<span style="color:var(--bad)">*</span>' : ""}</label>
          <select onchange="state.crm.assignTask.sellerName=this.value;requestRender()" required>
            <option value="">Selecione o vendedor…</option>
            ${t.hadSeller && !vendedores.some((v) => v.sellerName === t.sellerName)
              ? `<option value="${escapeHtml(t.sellerName)}" selected>${escapeHtml(t.sellerName)} (do cadastro)</option>` : ""}
            ${preferidos.length ? `<optgroup label="Unidade que atende a cidade">
              ${preferidos.map((v) => `<option value="${escapeHtml(v.sellerName)}" ${t.sellerName === v.sellerName ? "selected" : ""}>${escapeHtml(v.sellerName)}${v.baseUnit ? ` · ${escapeHtml(v.baseUnit)}` : ""}</option>`).join("")}
            </optgroup>` : ""}
            ${demais.length ? `<optgroup label="${preferidos.length ? "Outras unidades" : "Vendedores"}">
              ${demais.map((v) => `<option value="${escapeHtml(v.sellerName)}" ${t.sellerName === v.sellerName ? "selected" : ""}>${escapeHtml(v.sellerName)}${v.baseUnit ? ` · ${escapeHtml(v.baseUnit)}` : ""}</option>`).join("")}
            </optgroup>` : ""}
          </select>
          ${!vendedores.length ? '<div class="text-small" style="color:var(--muted);margin-top:4px">Nenhum vendedor cadastrado nas suas unidades. Verifique o cadastro de pessoas.</div>' : ""}
        </div>

        <div class="field">
          <label>Motivo da cobrança</label>
          <input value="${escapeHtml(t.reason)}" oninput="state.crm.assignTask.reason=this.value"
            placeholder="O que o vendedor precisa fazer" />
        </div>

        <div class="field">
          <label>Prazo</label>
          <input type="date" value="${escapeHtml(t.dueAt)}" oninput="state.crm.assignTask.dueAt=this.value" />
        </div>

        <div class="actions" style="margin-top:16px">
          <button class="btn btn-primary" ${t.saving || !t.sellerName ? "disabled" : ""} onclick="confirmAssignTask()">
            ${t.saving ? "Criando…" : "Criar tarefa"}
          </button>
          <button class="btn btn-ghost" onclick="closeAssignTaskModal()">Cancelar</button>
        </div>
      </div>
    </div>`;
}

async function confirmAssignTask() {
  const t = state.crm.assignTask;
  if (!t || !t.sellerName) { addMessage("error", "Selecione o vendedor."); return; }
  state.crm.assignTask.saving = true;
  requestRender();
  try {
    const r = await api("/api/crm/tasks/assign", {
      method: "POST",
      body: JSON.stringify({
        clientKey: t.clientKey,
        clientName: t.clientName,
        sellerName: t.sellerName,
        title: `Contatar ${t.clientName}`,
        description: `Cobrança da gestão — ${t.reason}`,
        dueAt: t.dueAt,
      }),
    });
    addMessage(r.duplicated ? "warn" : "success", r.message || "Tarefa criada.");
    closeAssignTaskModal();
    await loadCrmData();
  } catch (e) {
    addMessage("error", e.message);
    if (state.crm.assignTask) state.crm.assignTask.saving = false;
    requestRender();
  }
}

// ─── Agendar contato (vendedor, para si mesmo) ─────────────────────────────
//
// Atalho da ficha do cliente: o vendedor marca uma ligação futura e ela vira
// tarefa dele em Tarefas. Usa o mesmo endpoint da cobrança do gestor, mas o
// backend força o nome do vendedor logado — ninguém agenda para outro.

/** Data de hoje + N dias no fuso local (toISOString devolveria UTC). */
function dateInDays(dias) {
  const d = new Date();
  d.setDate(d.getDate() + dias);
  const p = (n) => String(n).padStart(2, "0");
  return `${d.getFullYear()}-${p(d.getMonth() + 1)}-${p(d.getDate())}`;
}

const SCHEDULE_PRESETS = [
  { label: "Amanhã", dias: 1 },
  { label: "Em 3 dias", dias: 3 },
  { label: "Em 7 dias", dias: 7 },
  { label: "Em 15 dias", dias: 15 },
];

const SCHEDULE_MOTIVOS = [
  "Retomar negociação",
  "Cliente pediu para ligar depois",
  "Enviar cotação / orçamento",
  "Conferir se o pedido chegou",
  "Oferecer itens da sugestão",
];

function openScheduleContactModal(clientKey) {
  const client = state.crm.selectedClient?.summary || {};
  if (!clientKey) return;
  state.crm.scheduleContact = {
    clientKey,
    clientName: client.clientName || clientKey,
    phone: client.updatedPhone || client.phone || "",
    date: dateInDays(1),
    time: "09:00",
    reason: sugerirMotivoAgendamento(client),
    saving: false,
  };
  requestRender();
}

/** Motivo sugerido conforme a situação do cliente — o vendedor pode trocar. */
function sugerirMotivoAgendamento(client) {
  const dias = client.daysWithoutPurchase;
  if (client.statusCode === "INATIVO") return `Retomar contato — inativo há ${dias || "?"} dias`;
  if (client.statusCode === "PRE_INATIVO") return "Contato preventivo — cliente espaçando pedidos";
  if (Number(client.currentRevenue || 0) <= 0) return "Sem compra no mês — provocar reposição";
  return "Retomar negociação";
}

function closeScheduleContactModal() {
  state.crm.scheduleContact = null;
  requestRender();
}

function setSchedulePreset(dias) {
  if (!state.crm.scheduleContact) return;
  state.crm.scheduleContact.date = dateInDays(dias);
  requestRender();
}

/** Recebe o índice, não o texto — evita quebrar o HTML com aspas no motivo. */
function setScheduleReason(indice) {
  if (!state.crm.scheduleContact) return;
  state.crm.scheduleContact.reason = SCHEDULE_MOTIVOS[indice] || state.crm.scheduleContact.reason;
  requestRender();
}

// ─── Registro receptivo ────────────────────────────────────────────────────

const RECEPTIVE_TYPES = [
  { code: "LIGACAO_RECEBIDA",  label: "Ligação recebida",  hint: "O cliente ligou para a Passini" },
  { code: "MENSAGEM_RECEBIDA", label: "Mensagem recebida", hint: "WhatsApp, e-mail ou recado" },
  { code: "ANOTACAO",          label: "Anotação",          hint: "Informação sobre o cliente" },
];

function openReceptiveModal(clientKey) {
  const client = state.crm.selectedClient?.summary || {};
  if (!clientKey) return;
  state.crm.receptive = {
    clientKey,
    clientName: client.clientName || clientKey,
    typeCode: "LIGACAO_RECEBIDA",
    notes: "",
    saving: false,
  };
  requestRender();
}

function closeReceptiveModal() {
  state.crm.receptive = null;
  requestRender();
}

async function salvarRegistroReceptivo() {
  const r = state.crm.receptive;
  if (!r || r.saving) return;
  if (!r.notes.trim()) { addMessage("error", "Escreva o que aconteceu."); return; }
  state.crm.receptive.saving = true;
  requestRender();
  try {
    await api("/api/crm/interactions", {
      method: "POST",
      body: JSON.stringify({
        clientKey: r.clientKey,
        clientName: r.clientName,
        contactTypeCode: r.typeCode,
        initiative: "RECEPTIVO",
        notes: r.notes.trim(),
      }),
    });
    addMessage("success", "Registro salvo no histórico do cliente.");
    state.crm.receptive = null;
    state.contacts = null;                     // força recarregar a tela Contatos
    await openCrmClient(r.clientKey, false);   // atualiza a ficha aberta
  } catch (error) {
    addMessage("error", error.message);
    if (state.crm.receptive) state.crm.receptive.saving = false;
  }
  requestRender();
}

function receptiveModal() {
  const r = state.crm.receptive;
  if (!r) return "";
  return `
    <div class="client-drawer-overlay open modal-dim" onclick="closeReceptiveModal()">
      <div class="panel modal-panel" style="max-width:520px;margin:8vh auto;padding:22px" onclick="event.stopPropagation()">
        <div class="section-title">
          <div>
            <h3>📝 Registro receptivo</h3>
            <div class="text-small">${escapeHtml(r.clientName)}</div>
          </div>
          <button class="btn btn-ghost btn-sm" onclick="closeReceptiveModal()">Fechar</button>
        </div>

        <div class="field" style="margin-top:12px">
          <label>O que foi</label>
          <div style="display:flex;gap:6px;flex-wrap:wrap">
            ${RECEPTIVE_TYPES.map((t) => `
              <button class="btn btn-sm ${r.typeCode === t.code ? "btn-primary" : "btn-ghost"}"
                title="${escapeHtml(t.hint)}"
                onclick="state.crm.receptive.typeCode='${t.code}';requestRender()">${escapeHtml(t.label)}</button>`).join("")}
          </div>
        </div>

        <div class="field">
          <label>O que aconteceu</label>
          <textarea rows="4" placeholder="Ex: ligou perguntando prazo da peça X; combinei retornar com o preço"
            oninput="state.crm.receptive.notes=this.value">${escapeHtml(r.notes)}</textarea>
        </div>

        <div class="text-small" style="color:var(--muted);background:#f5f7f9;border-radius:8px;padding:10px 12px">
          Entra no histórico do cliente e na tela Contatos, mas <strong>não conta na meta de ligações
          ativas</strong> — a meta mede o que você foi buscar, não o que chegou sozinho.
        </div>

        <div class="actions" style="margin-top:14px">
          <button class="btn btn-primary" ${r.saving ? "disabled" : ""} onclick="salvarRegistroReceptivo()">
            ${r.saving ? "Salvando…" : "Salvar registro"}</button>
          <button class="btn btn-ghost" onclick="closeReceptiveModal()">Cancelar</button>
        </div>
      </div>
    </div>
  `;
}

function scheduleContactModal() {
  const s = state.crm.scheduleContact;
  if (!s) return "";
  const hoje = dateInDays(0);

  return `
    <div class="client-drawer-overlay open modal-dim" onclick="closeScheduleContactModal()">
      <div class="panel modal-panel" style="max-width:520px;margin:8vh auto;padding:22px" onclick="event.stopPropagation()">
        <div class="section-title">
          <div>
            <h3>📅 Agendar contato</h3>
            <div class="text-small">${escapeHtml(s.clientName)}${s.phone ? ` · ${escapeHtml(s.phone)}` : ""}</div>
          </div>
          <button class="btn btn-ghost btn-sm" onclick="closeScheduleContactModal()">Fechar</button>
        </div>

        <div class="field" style="margin-top:12px">
          <label>Quando voltar a falar</label>
          <div style="display:flex;gap:6px;flex-wrap:wrap;margin-bottom:8px">
            ${SCHEDULE_PRESETS.map((p) => `
              <button class="btn btn-sm ${s.date === dateInDays(p.dias) ? "btn-primary" : "btn-ghost"}"
                onclick="setSchedulePreset(${p.dias})">${p.label}</button>`).join("")}
          </div>
          <div style="display:flex;gap:8px">
            <input type="date" style="flex:2" min="${hoje}" value="${escapeHtml(s.date)}"
              oninput="state.crm.scheduleContact.date=this.value" />
            <input type="time" style="flex:1" value="${escapeHtml(s.time)}"
              oninput="state.crm.scheduleContact.time=this.value" />
          </div>
        </div>

        <div class="field">
          <label>Motivo do contato</label>
          <input value="${escapeHtml(s.reason)}" oninput="state.crm.scheduleContact.reason=this.value"
            placeholder="O que você precisa tratar com o cliente" />
          <div style="display:flex;gap:6px;flex-wrap:wrap;margin-top:6px">
            ${SCHEDULE_MOTIVOS.map((m, i) => `
              <button class="btn btn-ghost btn-sm" style="font-size:11px"
                onclick="setScheduleReason(${i})">${escapeHtml(m)}</button>`).join("")}
          </div>
        </div>

        <div class="text-small" style="color:var(--muted);margin-top:4px">
          A tarefa aparece em <strong>Tarefas</strong> e vira pendência de follow-up na data marcada.
        </div>

        <div class="actions" style="margin-top:16px">
          <button class="btn btn-primary" ${s.saving || !s.date ? "disabled" : ""} onclick="confirmScheduleContact()">
            ${s.saving ? "Agendando…" : "Agendar"}
          </button>
          <button class="btn btn-ghost" onclick="closeScheduleContactModal()">Cancelar</button>
        </div>
      </div>
    </div>`;
}

async function confirmScheduleContact() {
  const s = state.crm.scheduleContact;
  if (!s || !s.date) { addMessage("error", "Escolha a data do contato."); return; }
  state.crm.scheduleContact.saving = true;
  requestRender();
  try {
    const r = await api("/api/crm/tasks/assign", {
      method: "POST",
      body: JSON.stringify({
        clientKey: s.clientKey,
        clientName: s.clientName,
        // sellerName vai vazio de propósito: o backend preenche com o vendedor logado.
        title: `Contatar ${s.clientName}`,
        description: `Agendado pelo vendedor — ${s.reason}${s.time ? ` (${s.time})` : ""}`,
        dueAt: s.time ? `${s.date} ${s.time}:00` : s.date,
      }),
    });
    addMessage(r.duplicated ? "warn" : "success", r.message || "Contato agendado.");
    closeScheduleContactModal();
    await loadCrmData();
  } catch (e) {
    addMessage("error", e.message);
    if (state.crm.scheduleContact) state.crm.scheduleContact.saving = false;
    requestRender();
  }
}

// ─── Reuniões e Treinamentos ────────────────────────────────────────────────
//
// Duas telas na mesma view, separadas pelo perfil:
//  - Gestão: registra a ata, marca os presentes, anexa material e publica.
//    Depois acompanha quem já deu ciência e lê os feedbacks.
//  - Vendedor: vê as reuniões em que esteve, confirma ciência e pode deixar
//    sugestão. Não vê rascunho nem o feedback dos colegas.

async function loadMeetings(silencioso) {
  const f = state.meetingFilters;
  const q = new URLSearchParams();
  if (f.search) q.set("q", f.search);
  if (f.kind) q.set("kind", f.kind);
  if (f.from) q.set("from", f.from);
  if (f.to) q.set("to", f.to);
  if (f.mine) q.set("mine", "1");
  if (!silencioso) {
    state.ui.loading.meetings = true;
    requestRender();   // pinta o "carregando" ANTES de ir à rede
  }
  try {
    state.meetings = await api(`/api/meetings?${q.toString()}`);
  } catch (e) {
    state.meetings = { error: e.message, meetings: [], kinds: [], people: [] };
  } finally {
    state.ui.loading.meetings = false;
    requestRender();
  }
}

function applyMeetingSearch() {
  const campo = document.getElementById("meeting-search");
  state.meetingFilters.search = (campo ? campo.value : state.meetingFilters.search || "").trim();
  loadMeetings();
}

function setMeetingKindFilter(kind) {
  const novo = state.meetingFilters.kind === kind ? "" : kind;
  state.meetingFilters.kind = novo;
  trocarChip("meetingKind", novo, () => loadMeetings());
}

function clearMeetingFilters() {
  state.meetingFilters = { search: "", kind: "", from: "", to: "", mine: false };
  loadMeetings();
}

// ─── Editor da ata ──────────────────────────────────────────────────────────

function novaAtaModal(kind) {
  state.meetingEditor = {
    id: null, kind: kind || "REUNIAO", title: "", topic: "",
    unitName: state.meetings?.defaultUnit || (state.meetings?.units || [])[0] || "",
    occurredAt: localDateTimeInput(), durationMin: 60, location: "",
    agenda: "", summary: "", decisions: "",
    organizerName: state.meetings?.myName || "",
    visibility: "UNIDADE",
    participants: [], attachments: [], status: "RASCUNHO", saving: false,
  };
  requestRender();
}

async function editarAta(meetingId) {
  try {
    const r = await api("/api/meetings/detail", {
      method: "POST", body: JSON.stringify({ meetingId }),
    });
    const m = r.meeting;
    state.meetingEditor = {
      id: m.id, kind: m.kind, title: m.title, topic: m.topic,
      unitName: m.unitName, occurredAt: (m.occurredAt || "").replace(" ", "T").slice(0, 16),
      durationMin: m.durationMin, location: m.location, agenda: m.agenda,
      summary: m.summary, decisions: m.decisions, organizerName: m.organizerName,
      visibility: m.visibility || "UNIDADE",
      participants: m.participants.map((p) => ({
        personName: p.personName, personKey: p.personKey, unitName: p.unitName,
        acknowledgedAt: p.acknowledgedAt,
      })),
      attachments: m.attachments, status: m.status, saving: false,
    };
    requestRender();
  } catch (e) { addMessage("error", e.message); }
}

function fecharAtaEditor() { state.meetingEditor = null; requestRender(); }

function togglePresente(personKey) {
  const e = state.meetingEditor;
  if (!e) return;
  const pessoa = (state.meetings?.people || []).find((p) => p.personKey === personKey);
  if (!pessoa) return;
  const idx = e.participants.findIndex((p) => p.personKey === personKey);
  if (idx >= 0) {
    // Quem já deu ciência não sai por clique acidental — precisa confirmar.
    if (e.participants[idx].acknowledgedAt
        && !confirm(`${e.participants[idx].personName} já deu ciência. Remover mesmo assim?`)) return;
    e.participants.splice(idx, 1);
  } else {
    e.participants.push({ personName: pessoa.personName, personKey: pessoa.personKey, unitName: pessoa.unitName });
  }
  requestRender();
}

function marcarTodosPresentes(unidade) {
  const e = state.meetingEditor;
  if (!e) return;
  const alvo = (state.meetings?.people || []).filter((p) => !unidade || p.unitName === unidade);
  const jaTem = new Set(e.participants.map((p) => p.personKey));
  alvo.forEach((p) => {
    if (!jaTem.has(p.personKey)) {
      e.participants.push({ personName: p.personName, personKey: p.personKey, unitName: p.unitName });
    }
  });
  requestRender();
}

function limparPresentes() {
  const e = state.meetingEditor;
  if (!e) return;
  const comCiencia = e.participants.filter((p) => p.acknowledgedAt);
  e.participants = comCiencia;   // preserva quem já confirmou
  requestRender();
}

async function salvarAta(depoisPublicar) {
  const e = state.meetingEditor;
  if (!e) return;
  if (!e.title.trim()) { addMessage("error", "Informe o assunto."); return; }
  e.saving = true; requestRender();
  try {
    const r = await api("/api/meetings/save", {
      method: "POST",
      body: JSON.stringify({ ...e, occurredAt: (e.occurredAt || "").replace("T", " ") }),
    });
    e.id = r.meetingId;
    if (depoisPublicar) {
      await api("/api/meetings/publish", {
        method: "POST", body: JSON.stringify({ meetingId: r.meetingId }),
      });
      const comLogin = e.participants.filter((p) =>
        (state.meetings?.people || []).find((x) => x.personKey === p.personKey)?.hasLogin).length;
      if (comLogin < e.participants.length) {
        addMessage("warn", `${comLogin} de ${e.participants.length} presentes têm login e receberão a pendência.`);
      }
      addMessage("success", "Ata publicada. A equipe já recebeu a pendência de ciência.");
      state.meetingEditor = null;
    } else {
      addMessage("success", "Rascunho salvo.");
    }
    await loadMeetings(true);
  } catch (err) {
    addMessage("error", err.message);
  } finally {
    if (state.meetingEditor) state.meetingEditor.saving = false;
    requestRender();
  }
}

async function excluirAta(meetingId) {
  if (!confirm("Excluir esta ata e seus anexos? A ação não pode ser desfeita.")) return;
  try {
    await api("/api/meetings/delete", { method: "POST", body: JSON.stringify({ meetingId }) });
    addMessage("success", "Ata excluída.");
    state.meetingEditor = null;
    state.meetingDetail = null;
    await loadMeetings(true);
  } catch (e) { addMessage("error", e.message); }
}

// ─── Anexos ─────────────────────────────────────────────────────────────────

async function enviarAnexos(input) {
  const e = state.meetingEditor;
  if (!e || !input.files?.length) return;
  if (!e.id) {
    addMessage("warn", "Salve o rascunho antes de anexar — o arquivo precisa de uma ata para ficar vinculado.");
    input.value = "";
    return;
  }
  const form = new FormData();
  form.append("meetingId", String(e.id));
  Array.from(input.files).forEach((f) => form.append("files", f));
  try {
    const resp = await fetch("/api/meetings/attachment/upload", {
      method: "POST", body: form, credentials: "same-origin",
    });
    const data = await resp.json();
    if (!resp.ok) throw new Error(data.error || "Falha ao anexar.");
    e.attachments = [...(e.attachments || []), ...(data.attachments || []).map((a) => ({
      id: a.attachmentId, fileName: a.fileName, sizeBytes: a.sizeBytes,
    }))];
    addMessage("success", `${data.attachments.length} arquivo(s) anexado(s).`);
  } catch (err) {
    addMessage("error", err.message);
  } finally {
    input.value = "";
    requestRender();
  }
}

async function removerAnexo(attachmentId) {
  try {
    await api("/api/meetings/attachment/delete", {
      method: "POST", body: JSON.stringify({ attachmentId }),
    });
    if (state.meetingEditor) {
      state.meetingEditor.attachments = state.meetingEditor.attachments.filter((a) => a.id !== attachmentId);
    }
    requestRender();
  } catch (e) { addMessage("error", e.message); }
}

/** Extensões que o navegador consegue exibir sem baixar. */
const ANEXO_VISUALIZAVEL = [".pdf", ".png", ".jpg", ".jpeg", ".webp", ".gif", ".txt"];

function anexoPodeAbrir(nome) {
  const n = String(nome || "").toLowerCase();
  return ANEXO_VISUALIZAVEL.some((ext) => n.endsWith(ext));
}

/**
 * Baixa o anexo via fetch em vez de link direto.
 *
 * O <a target="_blank"> com Content-Disposition: attachment abre uma aba que
 * fecha no mesmo instante — quando algo dava errado (sessão, permissão), o
 * vendedor via exatamente nada e concluía que não tinha acesso. Assim, ou o
 * arquivo baixa, ou aparece o motivo na tela.
 */
async function baixarAnexo(attachmentId, fileName) {
  try {
    const resp = await fetch(`/api/meetings/attachment/${attachmentId}`, { credentials: "same-origin" });
    if (!resp.ok) {
      let motivo = `Não foi possível baixar (erro ${resp.status}).`;
      try { motivo = (await resp.json()).error || motivo; } catch (_) { /* resposta não-JSON */ }
      addMessage("error", motivo);
      return;
    }
    const blob = await resp.blob();
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.download = fileName || "anexo";
    document.body.appendChild(link);
    link.click();
    link.remove();
    setTimeout(() => URL.revokeObjectURL(url), 10000);
  } catch (e) {
    addMessage("error", `Falha ao baixar o anexo: ${e.message}`);
  }
}

function abrirAnexo(attachmentId) {
  window.open(`/api/meetings/attachment/${attachmentId}?inline=1`, "_blank", "noopener");
}

function fileSizeLabel(bytes) {
  const n = Number(bytes || 0);
  if (n >= 1024 * 1024) return `${(n / 1024 / 1024).toFixed(1)} MB`;
  if (n >= 1024) return `${Math.round(n / 1024)} KB`;
  return `${n} B`;
}

// ─── Ciência do participante ────────────────────────────────────────────────

/**
 * Ligações e visitas do cliente, com o efeito medido de cada visita.
 * Responde a pergunta prática: "adiantou ter ido lá?".
 */
async function loadClientVisitHistory(clientKey) {
  if (!clientKey) return;
  try {
    state.crm.clientVisits = await api("/api/visits/client", {
      method: "POST", body: JSON.stringify({ clientKey }),
    });
  } catch (e) {
    state.crm.clientVisits = { error: e.message, visits: [] };
  }
  requestRender();
}

// ─── Pedido de visita a partir da ficha ─────────────────────────────────────

function abrirPedidoVisita(clientKey, clientName) {
  state.visitRequestEditor = {
    clientKey, clientName: clientName || clientKey, reason: "", saving: false,
  };
  requestRender();
}

function fecharPedidoVisita() { state.visitRequestEditor = null; requestRender(); }

async function enviarPedidoVisita() {
  const p = state.visitRequestEditor;
  if (!p) return;
  if (!p.reason.trim()) { addMessage("error", "Diga por que a visita resolve o que a ligação não resolveu."); return; }
  p.saving = true; requestRender();
  try {
    const r = await api("/api/visits/request", {
      method: "POST",
      body: JSON.stringify({ clientKey: p.clientKey, clientName: p.clientName, reason: p.reason }),
    });
    addMessage(r.duplicated ? "warn" : "success", r.message || "Pedido enviado.");
    state.visitRequestEditor = null;
    await loadClientVisitHistory(p.clientKey);
    loadVisits(true);
  } catch (e) {
    addMessage("error", e.message);
    if (state.visitRequestEditor) state.visitRequestEditor.saving = false;
    requestRender();
  }
}

const MOTIVOS_VISITA = [
  "Liguei várias vezes e não consigo falar com o responsável",
  "Cliente parou de comprar e não diz o motivo por telefone",
  "Concorrente entrou na conta — precisa de presença",
  "Negociação de volume/tabela que não fecha por telefone",
  "Problema antigo mal resolvido, o cliente está chateado",
];

function usarMotivoVisita(indice) {
  if (!state.visitRequestEditor) return;
  state.visitRequestEditor.reason = MOTIVOS_VISITA[indice] || state.visitRequestEditor.reason;
  requestRender();
}

function pedidoVisitaModal() {
  const p = state.visitRequestEditor;
  if (!p) return "";
  return `
    <div class="client-drawer-overlay open modal-dim" onclick="fecharPedidoVisita()" style="z-index:60">
      <div class="panel modal-panel" style="max-width:560px;margin:10vh auto;padding:22px" onclick="event.stopPropagation()">
        <div class="section-title">
          <div><h3>🙋 Pedir visita do gerente</h3>
            <div class="text-small">${escapeHtml(p.clientName)}</div></div>
          <button class="btn btn-ghost btn-sm" onclick="fecharPedidoVisita()">Fechar</button>
        </div>
        <div class="field" style="margin-top:12px">
          <label>Por que a visita resolve o que a ligação não resolveu? <span style="color:var(--bad)">*</span></label>
          <textarea rows="3" style="font-family:inherit" oninput="state.visitRequestEditor.reason=this.value"
            placeholder="Seja específico — é o que o gerente lê para montar a rota da semana">${escapeHtml(p.reason)}</textarea>
          <div style="display:flex;gap:6px;flex-wrap:wrap;margin-top:6px">
            ${MOTIVOS_VISITA.map((m, i) => `
              <button class="btn btn-ghost btn-sm" style="font-size:11px"
                onclick="usarMotivoVisita(${i})">${escapeHtml(m)}</button>`).join("")}
          </div>
        </div>
        <div class="actions" style="margin-top:12px">
          <button class="btn btn-primary" ${p.saving ? "disabled" : ""} onclick="enviarPedidoVisita()">
            ${p.saving ? "Enviando…" : "Enviar pedido"}</button>
          <button class="btn btn-ghost" onclick="fecharPedidoVisita()">Cancelar</button>
        </div>
      </div>
    </div>`;
}

function clientVisitBlock(clientKey) {
  const d = state.crm.clientVisits;
  if (!d || d.error) return "";
  const podeGerir = Boolean(state.visits?.canManage);
  return `
    <div class="subtle-card padded-card">
      <div class="section-title">
        <div><h3>📞 Contatos e visitas</h3>
          <div class="text-small">
            ${number(d.callsTotal)} ligação(ões) no total · ${number(d.callsRecent)} nos últimos ${d.callWindowDays} dias
          </div></div>
        <div style="display:flex;gap:6px">
          ${!podeGerir && d.canRequestVisit ? `
            <button class="btn btn-primary btn-sm"
              onclick="abrirPedidoVisita('${jsAttr(clientKey)}','${jsAttr(state.crm.selectedClient?.summary?.clientName || "")}')">🙋 Pedir visita</button>` : ""}
          ${!podeGerir && !d.canRequestVisit && !d.pendingRequest ? `
            <button class="btn btn-ghost btn-sm" disabled
              title="Registre uma ligação para este cliente antes de pedir a visita">🙋 Pedir visita</button>` : ""}
          ${podeGerir ? `
            <button class="btn btn-secondary btn-sm"
              onclick='novaVisita({clientKey:"${jsAttr(clientKey)}",clientName:"${jsAttr(state.crm.selectedClient?.summary?.clientName || "")}"})'>Registrar visita</button>` : ""}
        </div>
      </div>

      ${d.pendingRequest ? `
        <div class="message" style="background:#fdecea;color:#c0392b;font-size:12px;margin-top:8px">
          🙋 ${escapeHtml(d.pendingRequest.sellerName)} pediu visita em ${shortDate(d.pendingRequest.createdAt)}:
          ${escapeHtml(d.pendingRequest.reason)}
        </div>` : ""}

      ${!d.eligibleForVisit && !d.pendingRequest ? `
        <div class="message" style="background:#fff3e0;color:#e65100;font-size:12px;margin-top:8px">
          Sem ligação registrada nos últimos ${d.callWindowDays} dias. Ligue e registre o contato —
          só então dá para pedir visita ou o cliente entrar no roteiro do gerente. O telefone vem antes.
        </div>` : ""}

      <div class="stack" style="margin-top:8px">
        ${(d.visits || []).map((v) => `
          <div style="border-left:3px solid var(--accent);background:#fafbfc;border-radius:0 6px 6px 0;padding:8px 10px">
            <div style="display:flex;justify-content:space-between;gap:8px;flex-wrap:wrap;align-items:start">
              <div style="flex:1;min-width:200px">
                <div style="display:flex;gap:6px;align-items:center;flex-wrap:wrap">
                  ${visitTypeBadge(v.visitType)}
                  <span class="text-small">${v.occurredAt ? shortDate(v.occurredAt) : "planejada"}</span>
                </div>
                <div class="text-small" style="color:var(--muted)">
                  ${escapeHtml(v.managerName)}${v.sellerName ? ` com ${escapeHtml(v.sellerName)}` : ""}</div>
                ${v.outcome ? `<div style="font-size:12px;margin-top:3px;white-space:pre-wrap">${escapeHtml(v.outcome)}</div>` : ""}
                ${v.agreement ? `<div style="font-size:12px"><strong>Combinado:</strong> ${escapeHtml(v.agreement)}</div>` : ""}
              </div>
              <div style="text-align:right">${v.status === "REALIZADA" ? efeitoVisita(v) : ""}</div>
            </div>
          </div>`).join("") || '<div class="text-small" style="color:var(--muted)">Nenhuma visita registrada para este cliente.</div>'}
      </div>
    </div>`;
}

async function abrirAta(meetingId) {
  try {
    const r = await api("/api/meetings/detail", {
      method: "POST", body: JSON.stringify({ meetingId }),
    });
    state.meetingDetail = { ...r.meeting, feedbackDraft: "", saving: false };
    requestRender();
  } catch (e) { addMessage("error", e.message); }
}

function fecharAta() { state.meetingDetail = null; requestRender(); }

async function darCiencia() {
  const d = state.meetingDetail;
  if (!d) return;
  const campo = document.getElementById("meeting-feedback");
  const texto = campo ? campo.value.trim() : "";
  d.saving = true; requestRender();
  try {
    await api("/api/meetings/acknowledge", {
      method: "POST", body: JSON.stringify({ meetingId: d.id, feedback: texto }),
    });
    addMessage("success", texto ? "Ciência registrada e feedback enviado ao gestor." : "Ciência registrada.");
    state.meetingDetail = null;
    await loadMeetings(true);
  } catch (e) {
    addMessage("error", e.message);
    if (state.meetingDetail) state.meetingDetail.saving = false;
    requestRender();
  }
}

// ─── Views ──────────────────────────────────────────────────────────────────

function meetingKindChip(kind) {
  const cfg = { REUNIAO: { icon: "🗓️", label: "Reunião", bg: "#e8f0fe", fg: "#1a5276" },
                TREINAMENTO: { icon: "🎓", label: "Treinamento", bg: "#e6f4ea", fg: "#1e8e3e" } }[kind]
             || { icon: "📄", label: kind, bg: "#f1f3f4", fg: "#5f6368" };
  return `<span class="status-tag" style="background:${cfg.bg};color:${cfg.fg}">${cfg.icon} ${cfg.label}</span>`;
}

function meetingCard(m, podeGerir) {
  const pendente = m.iAmParticipant && !m.myAcknowledgedAt && m.status === "PUBLICADA";
  const progresso = m.participantCount
    ? Math.round((m.acknowledgedCount / m.participantCount) * 100) : 0;
  return `
    <div class="crm-card clean" style="padding:14px;${pendente ? "border-left:4px solid #f39c12" : ""}">
      <div style="display:flex;justify-content:space-between;align-items:start;gap:10px;flex-wrap:wrap">
        <div style="flex:1;min-width:220px">
          <div style="display:flex;gap:6px;align-items:center;flex-wrap:wrap;margin-bottom:4px">
            ${meetingKindChip(m.kind)}
            ${m.status === "RASCUNHO" ? '<span class="status-tag warn">✎ Rascunho — só você vê</span>' : ""}
            ${m.visibility === "EMPRESA" ? '<span class="status-tag" style="background:#e8f0fe;color:#1a5276">🌐 Compartilhada</span>' : ""}
            ${pendente ? '<span class="status-tag bad">Sua ciência pendente</span>' : ""}
            ${m.iAmParticipant && m.myAcknowledgedAt ? '<span class="status-tag good">✓ Você deu ciência</span>' : ""}
          </div>
          <div style="font-weight:700;font-size:14px">${escapeHtml(m.title)}</div>
          <div class="text-small">
            ${shortDate(m.occurredAt)} ${escapeHtml((m.occurredAt || "").slice(11, 16))}
            ${m.unitName ? ` · ${escapeHtml(m.unitName)}` : " · Corporativa"}
            ${m.durationMin ? ` · ${m.durationMin} min` : ""}
            · por ${escapeHtml(m.organizerName)}
          </div>
        </div>
        <div style="text-align:right;font-size:12px;min-width:130px">
          <div style="font-weight:700">${m.acknowledgedCount}/${m.participantCount} cientes</div>
          <div class="score-bar-track" style="margin-top:4px">
            <div class="score-bar-fill ${progresso >= 100 ? "good" : progresso >= 50 ? "warn" : ""}"
                 style="width:${progresso}%;height:6px"></div>
          </div>
          ${m.feedbackCount ? `<div style="color:var(--accent);font-weight:600;margin-top:4px">💬 ${m.feedbackCount} feedback(s)</div>` : ""}
          ${m.attachmentCount ? `<div class="text-small">📎 ${m.attachmentCount} anexo(s)</div>` : ""}
        </div>
      </div>
      ${m.topic ? `<div class="text-small" style="color:var(--muted);margin-top:6px">${escapeHtml(m.topic)}</div>` : ""}
      <div class="actions" style="gap:6px;margin-top:10px;padding-top:8px;border-top:1px solid var(--line)">
        <button class="btn ${pendente ? "btn-primary" : "btn-secondary"} btn-sm" onclick="abrirAta(${m.id})">
          ${pendente ? "✋ Dar ciência" : "Abrir"}
        </button>
        ${podeGerir ? `
          <button class="btn btn-ghost btn-sm" onclick="editarAta(${m.id})">Editar</button>
          <button class="btn btn-ghost btn-sm" onclick="excluirAta(${m.id})">Excluir</button>` : ""}
      </div>
    </div>`;
}

function reunioesView() {
  if (!state.meetings) { loadMeetings(); return `<div class="loader panel">Carregando reuniões…</div>`; }
  if (state.meetings.error) return `<div class="message error">${escapeHtml(state.meetings.error)}</div>`;

  const podeGerir = Boolean(state.meetings.canManage);
  const f = state.meetingFilters;
  const itens = state.meetings.meetings || [];
  const pendentes = itens.filter((m) => m.iAmParticipant && !m.myAcknowledgedAt && m.status === "PUBLICADA");
  const demais = itens.filter((m) => !pendentes.includes(m));
  const temFiltro = Boolean(f.search || f.kind || f.from || f.to || f.mine);

  return `
    <div class="stack">
      ${state.meetingEditor ? ataEditorModal() : ""}
      ${state.meetingDetail ? ataDetalheModal() : ""}

      ${pendentes.length ? `
        <div class="table-card" style="border-left:4px solid #f39c12">
          <div class="section-title">
            <div>
              <h3>✋ Aguardando sua ciência</h3>
              <div class="text-small">Confirme que participou. Se tiver sugestão, escreva — vai direto para quem conduziu.</div>
            </div>
            <div class="soft-badge" style="background:#fef7e0;color:#b06000">${pendentes.length}</div>
          </div>
          <div class="stack" style="padding-top:8px">
            ${pendentes.map((m) => meetingCard(m, podeGerir)).join("")}
          </div>
        </div>` : ""}

      <div class="form-card" style="padding:14px 18px">
        <div style="display:flex;gap:8px;flex-wrap:wrap;align-items:center;margin-bottom:10px">
          <input id="meeting-search" style="flex:1;min-width:220px"
            placeholder="🔍 Buscar por assunto, tema, decisão ou participante — Enter para buscar"
            value="${escapeHtml(f.search)}"
            oninput="state.meetingFilters.search=this.value"
            onkeydown="if(event.key==='Enter'){event.preventDefault();applyMeetingSearch();}" />
          <button class="btn btn-secondary btn-sm" onclick="applyMeetingSearch()">Buscar</button>
          ${temFiltro ? `<button class="btn btn-ghost btn-sm" onclick="clearMeetingFilters()">Limpar</button>` : ""}
          ${podeGerir ? `
            <button class="btn btn-primary btn-sm" onclick="novaAtaModal('REUNIAO')">🗓️ Nova reunião</button>
            <button class="btn btn-primary btn-sm" onclick="novaAtaModal('TREINAMENTO')">🎓 Novo treinamento</button>` : ""}
        </div>
        <div style="display:flex;gap:8px;flex-wrap:wrap;align-items:center">
          ${(state.meetings.kinds || []).map((k) => `
            <button type="button" onclick="setMeetingKindFilter('${k.id}')"
              ${chipEmEspera("meetingKind") ? "disabled" : ""}
              style="border:1px solid ${f.kind === k.id ? "var(--accent)" : "var(--line)"};
                     background:${f.kind === k.id ? "var(--accent)" : "#fff"};
                     color:${f.kind === k.id ? "#fff" : "var(--text)"};
                     border-radius:14px;padding:4px 12px;font-size:12px;font-weight:600;
                     ${chipEstadoCss("meetingKind", f.kind === k.id)}">
              ${chipTrocando("meetingKind") === k.id
                ? `<span class="girando">↻</span> Carregando…`
                : `${k.icon} ${escapeHtml(k.label)}`}
            </button>`).join("")}
          <span class="text-small" style="color:var(--muted);margin-left:4px">Período</span>
          <input type="date" style="width:150px" value="${escapeHtml(f.from)}"
            onchange="state.meetingFilters.from=this.value;loadMeetings()" />
          <span class="text-small">até</span>
          <input type="date" style="width:150px" value="${escapeHtml(f.to)}"
            onchange="state.meetingFilters.to=this.value;loadMeetings()" />
          ${podeGerir ? `
            <label class="check-row" style="font-weight:500">
              <input type="checkbox" ${f.mine ? "checked" : ""}
                onchange="state.meetingFilters.mine=this.checked;loadMeetings()" />
              <span>Só as que eu conduzi</span>
            </label>` : ""}
        </div>
      </div>

      <div class="stack">
        ${state.ui.loading.meetings ? '<div class="loader panel">Buscando…</div>' : ""}
        ${demais.length
          ? demais.map((m) => meetingCard(m, podeGerir)).join("")
          : (pendentes.length ? "" : emptyStateCard(temFiltro
              ? "Nenhuma ata encontrada com esses filtros."
              : (podeGerir
                  ? "Nenhuma ata registrada ainda. Comece pela primeira reunião da equipe."
                  : "Você ainda não participou de nenhuma reunião registrada.")))}
      </div>
    </div>`;
}

function ataEditorModal() {
  const e = state.meetingEditor;
  const pessoas = state.meetings?.people || [];
  const unidades = [...new Set(pessoas.map((p) => p.unitName).filter(Boolean))];
  const marcados = new Set(e.participants.map((p) => p.personKey));
  const maxMb = state.meetings?.maxAttachmentMb || 15;

  return `
    <div class="client-drawer-overlay open modal-dim" onclick="fecharAtaEditor()">
      <div class="panel modal-panel" data-keep-scroll="ata-editor"
           style="max-width:900px;margin:4vh auto;padding:22px;max-height:90vh;overflow:auto"
           onclick="event.stopPropagation()">
        <div class="section-title">
          <div>
            <h3>${e.id ? "Editar" : "Nova"} ${e.kind === "TREINAMENTO" ? "ata de treinamento" : "ata de reunião"}</h3>
            <div class="text-small">${e.status === "PUBLICADA"
              ? "Publicada — editar não apaga as ciências já dadas."
              : "Rascunho. A equipe só é notificada quando você publicar."}</div>
          </div>
          <button class="btn btn-ghost btn-sm" onclick="fecharAtaEditor()">Fechar</button>
        </div>

        <div style="display:grid;grid-template-columns:2fr 1fr;gap:12px;margin-top:12px">
          <div class="field"><label>Assunto <span style="color:var(--bad)">*</span></label>
            <input value="${escapeHtml(e.title)}" oninput="state.meetingEditor.title=this.value"
              placeholder="Ex.: Alinhamento comercial de agosto" /></div>
          <div class="field"><label>Tipo</label>
            <select onchange="state.meetingEditor.kind=this.value;requestRender()">
              ${(state.meetings?.kinds || []).map((k) => `
                <option value="${k.id}" ${e.kind === k.id ? "selected" : ""}>${k.icon} ${escapeHtml(k.label)}</option>`).join("")}
            </select></div>
        </div>

        <div style="display:grid;grid-template-columns:1fr 1fr 1fr 1fr;gap:12px">
          <div class="field"><label>Data e hora</label>
            <input type="datetime-local" value="${escapeHtml(e.occurredAt)}"
              oninput="state.meetingEditor.occurredAt=this.value" /></div>
          <div class="field"><label>Duração (min)</label>
            <input type="number" min="0" step="15" value="${Number(e.durationMin || 0)}"
              oninput="state.meetingEditor.durationMin=Number(this.value)" /></div>
          <div class="field"><label>Unidade</label>
            ${(state.meetings?.units || []).length === 1 && !state.meetings?.canBeCorporate
              ? `<input value="${escapeHtml(state.meetings.units[0])}" disabled
                   title="Você registra atas apenas para a sua unidade" />`
              : `<select onchange="state.meetingEditor.unitName=this.value">
                  ${state.meetings?.canBeCorporate ? `<option value="" ${!e.unitName ? "selected" : ""}>Corporativa (todas)</option>` : ""}
                  ${(state.meetings?.units || []).map((u) => `
                    <option value="${escapeHtml(u)}" ${e.unitName === u ? "selected" : ""}>${escapeHtml(u)}</option>`).join("")}
                </select>`}
            ${!state.meetings?.canBeCorporate && !(state.meetings?.units || []).length
              ? '<div class="text-small" style="color:var(--bad);margin-top:4px">Seu usuário não tem unidade vinculada. Peça ao administrador para vincular.</div>'
              : ""}</div>
          <div class="field"><label>Local</label>
            <input value="${escapeHtml(e.location)}" oninput="state.meetingEditor.location=this.value"
              placeholder="Sala, loja, online" /></div>
        </div>

        <div class="field"><label>Tema / palavras-chave <span style="color:var(--muted);font-weight:400">(ajuda a achar depois)</span></label>
          <input value="${escapeHtml(e.topic)}" oninput="state.meetingEditor.topic=this.value"
            placeholder="Ex.: correias, tensionador, política de desconto" /></div>

        <div class="field"><label>Pauta</label>
          <textarea rows="3" style="font-family:inherit;line-height:1.5"
            oninput="state.meetingEditor.agenda=this.value"
            placeholder="Os pontos previstos para o encontro">${escapeHtml(e.agenda)}</textarea></div>

        <div class="field"><label>O que foi tratado <span style="color:var(--bad)">*</span></label>
          <textarea rows="6" style="font-family:inherit;line-height:1.5"
            oninput="state.meetingEditor.summary=this.value"
            placeholder="O registro da reunião. É o que a equipe vai ler ao dar ciência.">${escapeHtml(e.summary)}</textarea></div>

        <div class="field"><label>Decisões e encaminhamentos</label>
          <textarea rows="3" style="font-family:inherit;line-height:1.5"
            oninput="state.meetingEditor.decisions=this.value"
            placeholder="Quem faz o quê e até quando">${escapeHtml(e.decisions)}</textarea></div>

        <div style="background:#f5f9ff;border:1px solid var(--accent);border-radius:12px;padding:14px;margin-top:8px">
          <label class="check-row" style="color:var(--accent)">
            <input type="checkbox" ${e.visibility === "EMPRESA" ? "checked" : ""}
              onchange="state.meetingEditor.visibility=this.checked?'EMPRESA':'UNIDADE';requestRender()" />
            <span>🌐 Liberar esta ata para as outras unidades</span>
          </label>
          <div class="text-small" style="margin-top:6px;color:var(--muted)">
            ${e.visibility === "EMPRESA"
              ? "Todos os gerentes vão poder ler. Use em treinamento e conteúdo que serve para a empresa toda."
              : "Por padrão, só a sua unidade e a diretoria enxergam. Marque quando o conteúdo servir para as outras equipes."}
          </div>
        </div>

        <div class="subtle-card padded-card" style="margin-top:8px">
          <div class="section-title">
            <div><h3>Presentes</h3>
              <div class="text-small">${e.participants.length} marcado(s) de ${pessoas.length} da sua equipe</div></div>
            <div style="display:flex;gap:6px">
              ${unidades.map((u) => `
                <button class="btn btn-ghost btn-sm" onclick="marcarTodosPresentes('${jsAttr(u)}')">Toda ${escapeHtml(u)}</button>`).join("")}
              <button class="btn btn-ghost btn-sm" onclick="limparPresentes()">Limpar</button>
            </div>
          </div>
          ${(() => {
            const semLogin = e.participants.filter((p) =>
              !(state.meetings?.people || []).find((x) => x.personKey === p.personKey)?.hasLogin);
            return semLogin.length ? `
              <div class="message" style="background:#fff3e0;color:#e65100;font-size:12px;margin-top:8px">
                ⚠ ${semLogin.map((p) => escapeHtml(p.personName)).join(", ")}
                ${semLogin.length === 1 ? "não tem" : "não têm"} login no CRM.
                ${semLogin.length === 1 ? "Fica registrado" : "Ficam registrados"} como
                ${semLogin.length === 1 ? "presente" : "presentes"}, mas
                ${semLogin.length === 1 ? "não recebe" : "não recebem"} a pendência de ciência.
              </div>` : "";
          })()}
          <div data-keep-scroll="ata-presentes"
               style="display:flex;gap:6px;flex-wrap:wrap;margin-top:8px;max-height:180px;overflow:auto">
            ${pessoas.map((p) => {
              const on = marcados.has(p.personKey);
              const ciente = e.participants.find((x) => x.personKey === p.personKey)?.acknowledgedAt;
              return `
                <button type="button" onclick="togglePresente('${jsAttr(p.personKey)}')"
                  title="${escapeHtml(p.role)}${p.unitName ? " · " + escapeHtml(p.unitName) : ""}${p.hasLogin ? " · recebe a pendência de ciência" : " · sem login no CRM"}"
                  style="border:1px solid ${on ? "var(--accent)" : "var(--line)"};
                         background:${on ? "var(--accent)" : "#fff"};color:${on ? "#fff" : "var(--text)"};
                         border-radius:14px;padding:4px 10px;font-size:12px;font-weight:600;cursor:pointer">
                  ${ciente ? "✓ " : on ? "● " : "○ "}${escapeHtml(p.personName)}${p.hasLogin ? "" : " ⚠"}
                </button>`;
            }).join("") || '<div class="text-small">Nenhuma pessoa ativa nas suas unidades. Verifique o cadastro em Administração.</div>'}
          </div>
        </div>

        <div class="subtle-card padded-card" style="margin-top:8px">
          <div class="section-title">
            <div><h3>Anexos</h3>
              <div class="text-small">Até ${maxMb} MB por arquivo · PDF, Office, imagens e ZIP</div></div>
          </div>
          <input type="file" multiple onchange="enviarAnexos(this)" style="margin-top:8px" />
          <div class="stack" style="margin-top:8px">
            ${(e.attachments || []).map((a) => `
              <div style="display:flex;justify-content:space-between;align-items:center;gap:8px;flex-wrap:wrap;
                          font-size:12px;padding:6px 10px;background:#f8f9fa;border-radius:6px">
                <span>📎 ${escapeHtml(a.fileName)} <span style="color:var(--muted)">${fileSizeLabel(a.sizeBytes)}</span></span>
                <span style="display:flex;gap:6px">
                  ${anexoPodeAbrir(a.fileName)
                    ? `<button class="btn btn-ghost btn-sm" onclick="abrirAnexo(${a.id})">Abrir</button>` : ""}
                  <button class="btn btn-ghost btn-sm" onclick="removerAnexo(${a.id})">Remover</button>
                </span>
              </div>`).join("") || '<div class="text-small" style="color:var(--muted)">Nenhum anexo.</div>'}
          </div>
        </div>

        <div class="actions" style="margin-top:16px">
          <button class="btn btn-secondary" ${e.saving ? "disabled" : ""} onclick="salvarAta(false)">
            ${e.saving ? "Salvando…" : "Salvar rascunho"}
          </button>
          <button class="btn btn-primary" ${e.saving ? "disabled" : ""} onclick="salvarAta(true)">
            ${e.status === "PUBLICADA" ? "Salvar alterações" : "Publicar e notificar equipe"}
          </button>
          <button class="btn btn-ghost" onclick="fecharAtaEditor()">Cancelar</button>
        </div>
      </div>
    </div>`;
}

function ataDetalheModal() {
  const m = state.meetingDetail;
  // Quem sou eu na lista vem marcado do servidor (isMe). Comparar pelo nome do
  // login aqui não funcionava: o cadastro tem "THIELLY HENRIQUES ROCHA (VENDAS)"
  // e o login é "Thielly Rocha" — o botão de ciência nunca aparecia.
  const euNaLista = (m.participants || []).find((p) => p.isMe);
  const souParticipante = Boolean(euNaLista);
  const jaCiente = Boolean(euNaLista?.acknowledgedAt);
  const podeGerir = Boolean(state.meetings?.canManage);
  const feedbacks = (m.participants || []).filter((p) => p.feedback);

  const bloco = (titulo, texto) => texto ? `
    <div style="margin-top:12px">
      <div class="eyebrow">${titulo}</div>
      <div style="white-space:pre-wrap;line-height:1.6;font-size:13px">${escapeHtml(texto)}</div>
    </div>` : "";

  return `
    <div class="client-drawer-overlay open modal-dim" onclick="fecharAta()">
      <div class="panel modal-panel" data-keep-scroll="ata-detalhe"
           style="max-width:820px;margin:4vh auto;padding:22px;max-height:90vh;overflow:auto"
           onclick="event.stopPropagation()">
        <div class="section-title">
          <div>
            <div style="margin-bottom:4px">${meetingKindChip(m.kind)}
              ${m.visibility === "EMPRESA" ? '<span class="status-tag" style="background:#e8f0fe;color:#1a5276">🌐 Compartilhada</span>' : ""}</div>
            <h3>${escapeHtml(m.title)}</h3>
            <div class="text-small">
              ${shortDate(m.occurredAt)} ${escapeHtml((m.occurredAt || "").slice(11, 16))}
              ${m.location ? ` · ${escapeHtml(m.location)}` : ""}
              ${m.unitName ? ` · ${escapeHtml(m.unitName)}` : " · Corporativa"}
              · conduzida por ${escapeHtml(m.organizerName)}
            </div>
          </div>
          <button class="btn btn-ghost btn-sm" onclick="fecharAta()">Fechar</button>
        </div>

        ${bloco("PAUTA", m.agenda)}
        ${bloco("O QUE FOI TRATADO", m.summary)}
        ${bloco("DECISÕES E ENCAMINHAMENTOS", m.decisions)}

        ${(m.attachments || []).length ? `
          <div class="subtle-card padded-card" style="margin-top:12px">
            <div class="section-title"><div><h3>📎 Material</h3>
              <div class="text-small">${m.attachments.length} arquivo(s) desta ${m.kind === "TREINAMENTO" ? "capacitação" : "reunião"}</div></div></div>
            <div class="stack" style="margin-top:8px">
              ${m.attachments.map((a) => `
                <div style="display:flex;justify-content:space-between;align-items:center;gap:8px;flex-wrap:wrap;
                            font-size:13px;padding:8px 10px;background:#f8f9fa;border-radius:6px">
                  <span style="font-weight:600">📎 ${escapeHtml(a.fileName)}
                    <span style="color:var(--muted);font-weight:400">${fileSizeLabel(a.sizeBytes)}</span></span>
                  <span style="display:flex;gap:6px">
                    ${anexoPodeAbrir(a.fileName)
                      ? `<button class="btn btn-secondary btn-sm" onclick="abrirAnexo(${a.id})">Abrir</button>` : ""}
                    <button class="btn btn-ghost btn-sm" onclick="baixarAnexo(${a.id}, '${jsAttr(a.fileName)}')">Baixar</button>
                  </span>
                </div>`).join("")}
            </div>
          </div>` : ""}

        <div class="subtle-card padded-card" style="margin-top:14px">
          <div class="section-title">
            <div><h3>Presentes</h3>
              <div class="text-small">${m.acknowledgedCount} de ${m.participantCount} deram ciência</div></div>
          </div>
          <div style="display:flex;gap:6px;flex-wrap:wrap;margin-top:8px">
            ${(m.participants || []).map((p) => `
              <span class="status-tag ${p.acknowledgedAt ? "good" : ""}"
                style="${p.isMe ? "outline:2px solid var(--accent);outline-offset:1px" : ""}"
                title="${p.acknowledgedAt ? "Ciente em " + escapeHtml(p.acknowledgedAt.slice(0, 16).replace("T", " ")) : "Pendente"}">
                ${p.acknowledgedAt ? "✓" : "○"} ${escapeHtml(p.personName)}${p.isMe ? " (você)" : ""}
              </span>`).join("")}
          </div>
        </div>

        ${podeGerir && feedbacks.length ? `
          <div class="subtle-card padded-card" style="margin-top:10px">
            <div class="section-title"><div><h3>💬 Retorno da equipe</h3></div></div>
            <div class="stack" style="margin-top:8px">
              ${feedbacks.map((p) => `
                <div style="border-left:3px solid var(--accent);padding:6px 10px;background:#f5f9ff;border-radius:0 6px 6px 0">
                  <div style="font-weight:700;font-size:12px">${escapeHtml(p.personName)}</div>
                  <div style="font-size:13px;white-space:pre-wrap;line-height:1.5">${escapeHtml(p.feedback)}</div>
                </div>`).join("")}
            </div>
          </div>` : ""}

        ${souParticipante && !jaCiente && m.status === "PUBLICADA" ? `
          <div class="subtle-card padded-card" style="margin-top:14px;border:1px solid var(--accent)">
            <div class="section-title"><div><h3>✋ Confirmar ciência</h3>
              <div class="text-small">Sugestão ou dúvida? Escreva abaixo — só ${escapeHtml(m.organizerName)} e a diretoria leem.</div></div></div>
            <div class="field" style="margin-top:8px">
              <textarea id="meeting-feedback" rows="3" style="font-family:inherit;line-height:1.5"
                placeholder="Opcional: o que ficou claro, o que faltou, o que você sugere"></textarea>
            </div>
            <div class="actions">
              <button class="btn btn-primary" ${m.saving ? "disabled" : ""} onclick="darCiencia()">
                ${m.saving ? "Registrando…" : "Estou ciente"}
              </button>
            </div>
          </div>` : ""}

        ${!souParticipante && m.status === "PUBLICADA" && !state.meetings?.canManage ? `
          <div class="message" style="margin-top:14px">
            Você não consta na lista de presença desta reunião, então não há ciência a dar.
          </div>` : ""}

        ${jaCiente ? `
          <div class="message success" style="margin-top:14px">
            ✓ Você deu ciência nesta ${m.kind === "TREINAMENTO" ? "capacitação" : "reunião"}.
          </div>` : ""}

        ${podeGerir ? `
          <div class="actions" style="margin-top:14px">
            <button class="btn btn-secondary" onclick="fecharAta();editarAta(${m.id})">Editar ata</button>
          </div>` : ""}
      </div>
    </div>`;
}

// ─── Feedback e PDI ─────────────────────────────────────────────────────────
//
// Três telas na mesma view:
//  - Gestão: lista quem já recebeu feedback no mês e quem falta; abre o
//    formulário com os indicadores da pessoa já carregados e o guia da conversa.
//  - Avaliado: lê o próprio feedback, dá ciência e escolhe para quem manda
//    observação — gestor ou diretoria.
//  - PDI: pontos de desenvolvimento vivos, que atravessam os meses.

async function loadFeedback(silencioso) {
  const f = state.feedbackFilters;
  const q = new URLSearchParams();
  if (f.kind) q.set("kind", f.kind);
  if (f.competence) q.set("competence", f.competence);
  if (f.person) q.set("person", f.person);
  if (!silencioso) {
    state.ui.loading.feedback = true;
    requestRender();   // pinta o "carregando" ANTES de ir à rede
  }
  try {
    state.feedback = await api(`/api/feedback?${q.toString()}`);
    if (!state.feedbackFilters.competence && state.feedback.latestCompetence) {
      state.feedbackFilters.competence = state.feedback.latestCompetence;
    }
  } catch (e) {
    state.feedback = { error: e.message, feedbacks: [], kinds: [], levels: [], people: [] };
  } finally {
    state.ui.loading.feedback = false;
    requestRender();
  }
}

function setFeedbackCompetence(valor) {
  state.feedbackFilters.competence = valor;
  loadFeedback();
}

function setFeedbackKind(kind) {
  const novo = state.feedbackFilters.kind === kind ? "" : kind;
  state.feedbackFilters.kind = novo;
  trocarChip("feedbackKind", novo, () => loadFeedback());
}

function applyFeedbackPersonSearch() {
  const campo = document.getElementById("feedback-person-search");
  state.feedbackFilters.person = (campo ? campo.value : state.feedbackFilters.person || "").trim();
  loadFeedback();
}

// ─── Formulário do gestor ───────────────────────────────────────────────────

async function novoFeedback(kind, personName, unitName) {
  const competence = state.feedbackFilters.competence || state.feedback?.latestCompetence || "";
  state.feedbackEditor = {
    id: null, kind, personName: personName || "", unitName: unitName || "",
    competence, highlights: "", improvements: "", agreements: "",
    tacticalGoal: "", tacticalReality: "", tacticalOptions: "", tacticalWill: "",
    ratings: {}, indicators: {}, guidance: [], items: [], groups: [], script: [], pdi: [],
    status: "RASCUNHO", saving: false, loading: true, tab: "conversa",
  };
  requestRender();
  await carregarPreviaFeedback();
}

async function carregarPreviaFeedback() {
  const e = state.feedbackEditor;
  if (!e) return;
  try {
    const r = await api("/api/feedback/preview", {
      method: "POST",
      body: JSON.stringify({
        kind: e.kind, personName: e.personName, unitName: e.unitName, competence: e.competence,
      }),
    });
    Object.assign(e, {
      indicators: r.indicators || {}, guidance: r.guidance || [],
      items: r.items || [], groups: r.groups || [], script: r.script || [],
      pdi: r.pdi || [], notes: r.notes || [],
      loading: false,
    });
  } catch (err) {
    e.loading = false;
    addMessage("error", err.message);
  }
  requestRender();
}

async function editarFeedback(feedbackId) {
  try {
    const r = await api("/api/feedback/detail", {
      method: "POST", body: JSON.stringify({ feedbackId }),
    });
    const fb = r.feedback;
    state.feedbackEditor = {
      id: fb.id, kind: fb.kind, personName: fb.personName, unitName: fb.unitName,
      competence: fb.competence, highlights: fb.highlights, improvements: fb.improvements,
      agreements: fb.agreements, tacticalGoal: fb.tacticalGoal, tacticalReality: fb.tacticalReality,
      tacticalOptions: fb.tacticalOptions, tacticalWill: fb.tacticalWill,
      ratings: fb.ratings || {}, indicators: fb.indicators || {}, guidance: fb.guidance || [],
      items: fb.items || [], groups: fb.groups || [], script: fb.script || [],
      pdi: fb.pdi || [], notes: fb.notes || [],
      status: fb.status, saving: false, loading: false, tab: "conversa",
    };
    requestRender();
  } catch (e) { addMessage("error", e.message); }
}

function fecharFeedbackEditor() { state.feedbackEditor = null; requestRender(); }
function setFeedbackTab(aba) { if (state.feedbackEditor) { state.feedbackEditor.tab = aba; requestRender(); } }

function marcarNivel(itemId, level) {
  const e = state.feedbackEditor;
  if (!e) return;
  const atual = e.ratings[itemId] || {};
  e.ratings[itemId] = { ...atual, level: atual.level === level ? "" : level };
  if (!e.ratings[itemId].level) delete e.ratings[itemId];
  requestRender();
}

async function salvarFeedback(depoisPublicar) {
  const e = state.feedbackEditor;
  if (!e) return;
  if (!e.personName) { addMessage("error", "Selecione a pessoa."); return; }
  e.saving = true; requestRender();
  try {
    const r = await api("/api/feedback/save", { method: "POST", body: JSON.stringify(e) });
    e.id = r.feedbackId;
    if (depoisPublicar) {
      await api("/api/feedback/publish", { method: "POST", body: JSON.stringify({ feedbackId: r.feedbackId }) });
      addMessage("success", `Feedback publicado. ${e.personName} recebeu a pendência de ciência.`);
      state.feedbackEditor = null;
    } else {
      addMessage("success", "Rascunho salvo.");
      e.status = "RASCUNHO";
    }
    await loadFeedback(true);
  } catch (err) {
    addMessage("error", err.message);
  } finally {
    if (state.feedbackEditor) state.feedbackEditor.saving = false;
    requestRender();
  }
}

async function excluirFeedback(feedbackId) {
  if (!confirm("Excluir este feedback? A ação não pode ser desfeita.")) return;
  try {
    await api("/api/feedback/delete", { method: "POST", body: JSON.stringify({ feedbackId }) });
    state.feedbackEditor = null; state.feedbackDetail = null;
    addMessage("success", "Feedback excluído.");
    await loadFeedback(true);
  } catch (e) { addMessage("error", e.message); }
}

// ─── Leitura e ciência ──────────────────────────────────────────────────────

async function abrirFeedback(feedbackId) {
  try {
    const r = await api("/api/feedback/detail", { method: "POST", body: JSON.stringify({ feedbackId }) });
    state.feedbackDetail = { ...r.feedback, saving: false };
    requestRender();
  } catch (e) { addMessage("error", e.message); }
}

function fecharFeedbackDetalhe() { state.feedbackDetail = null; requestRender(); }

async function darCienciaFeedback() {
  const d = state.feedbackDetail;
  if (!d) return;
  const note = document.getElementById("feedback-note")?.value.trim() || "";
  const conf = document.getElementById("feedback-confidential")?.value.trim() || "";
  d.saving = true; requestRender();
  try {
    const r = await api("/api/feedback/acknowledge", {
      method: "POST", body: JSON.stringify({ feedbackId: d.id, note, confidential: conf }),
    });
    let msg = "Ciência registrada.";
    if (r.hasNote && r.hasConfidential) msg = "Ciência registrada. Sua observação foi para o gestor e a confidencial para a diretoria.";
    else if (r.hasNote) msg = "Ciência registrada e observação enviada ao gestor.";
    else if (r.hasConfidential) msg = "Ciência registrada. Sua observação foi apenas para a diretoria.";
    addMessage("success", msg);
    state.feedbackDetail = null;
    await loadFeedback(true);
  } catch (e) {
    addMessage("error", e.message);
    if (state.feedbackDetail) state.feedbackDetail.saving = false;
    requestRender();
  }
}

// ─── PDI ────────────────────────────────────────────────────────────────────

function novoPdi(personName, unitName, feedbackId) {
  state.pdiEditor = {
    id: null, personName: personName || "", unitName: unitName || "",
    title: "", why: "", action: "", support: state.feedback?.myName || "",
    dueDate: dateInDays(30), status: "ABERTO", progressNote: "",
    originFeedbackId: feedbackId || null, saving: false,
  };
  requestRender();
}

function editarPdi(item, personName, unitName) {
  state.pdiEditor = { ...item, personName: item.personName || personName, unitName: unitName || "", saving: false };
  requestRender();
}

function fecharPdiEditor() { state.pdiEditor = null; requestRender(); }

async function salvarPdi() {
  const p = state.pdiEditor;
  if (!p) return;
  if (!p.title.trim()) { addMessage("error", "Informe o que precisa ser desenvolvido."); return; }
  p.saving = true; requestRender();
  try {
    await api("/api/feedback/pdi/save", { method: "POST", body: JSON.stringify(p) });
    addMessage("success", "PDI salvo.");
    state.pdiEditor = null;
    if (state.feedbackEditor) await carregarPreviaFeedback();
    await loadFeedback(true);
  } catch (e) {
    addMessage("error", e.message);
    if (state.pdiEditor) state.pdiEditor.saving = false;
    requestRender();
  }
}

async function excluirPdi(pdiId) {
  if (!confirm("Excluir este ponto do PDI?")) return;
  try {
    await api("/api/feedback/pdi/delete", { method: "POST", body: JSON.stringify({ pdiId }) });
    if (state.feedbackEditor) await carregarPreviaFeedback();
    await loadFeedback(true);
  } catch (e) { addMessage("error", e.message); }
}

// ─── Componentes ────────────────────────────────────────────────────────────

function nivelConfig(levelId) {
  return (state.feedback?.levels || []).find((n) => n.id === levelId)
    || { id: "", label: "—", icon: "○", color: "#5f6368", bg: "#f1f3f4" };
}

function nivelBadge(levelId) {
  const n = nivelConfig(levelId);
  return `<span class="status-tag" style="background:${n.bg};color:${n.color}">${n.icon} ${escapeHtml(n.label)}</span>`;
}

function pdiStatusBadge(status) {
  const s = (state.feedback?.pdiStatuses || []).find((x) => x.id === status)
    || { label: status, color: "#5f6368", bg: "#f1f3f4" };
  return `<span class="status-tag" style="background:${s.bg};color:${s.color}">${escapeHtml(s.label)}</span>`;
}

/** Linha de indicador com o valor, a referência e a leitura em uma frase. */
function indicadorLinha(rotulo, valor, referencia, ok) {
  return `
    <div style="display:flex;justify-content:space-between;align-items:baseline;gap:8px;
                padding:6px 0;border-bottom:1px solid var(--line);font-size:13px">
      <span style="color:var(--muted)">${escapeHtml(rotulo)}</span>
      <span style="text-align:right">
        <strong style="color:${ok === false ? "var(--bad)" : ok === true ? "var(--good)" : "inherit"}">${valor}</strong>
        ${referencia ? `<span class="text-small" style="color:var(--muted);display:block">${referencia}</span>` : ""}
      </span>
    </div>`;
}

function painelIndicadores(ind, kind) {
  if (!ind || !ind.found) {
    // Mostra COM QUEM tentou casar. "Sem dados" sozinho faz o gerente achar que
    // o vendedor não faturou, quando o problema é o nome estar grafado diferente
    // no cadastro e no faturamento.
    const nomes = ind?.availableNames || [];
    return `
      <div class="message" style="font-size:12px">
        <strong>Sem números para ${escapeHtml(ind?.competence || "esta competência")}.</strong>
        ${ind?.reason ? ` ${escapeHtml(ind.reason)}` : ""}
        <div style="margin-top:6px">O feedback pode ser feito assim mesmo, mas a conversa fica sem base.</div>
        ${nomes.length ? `
          <details style="margin-top:6px">
            <summary style="cursor:pointer">Nomes que faturaram nesta competência (${nomes.length})</summary>
            <div style="margin-top:4px;line-height:1.6">${nomes.map((n) => escapeHtml(n)).join(" · ")}</div>
            <div style="margin-top:4px">Se o nome da pessoa aparece aqui com outra grafia, o vínculo precisa
              ser corrigido em Usuários e Perfis ou no cadastro de pessoas.</div>
          </details>` : ""}
      </div>`;
  }
  const aviso = ind.matchedName ? `
    <div class="text-small" style="color:var(--muted);margin-bottom:6px">
      Números de <strong>${escapeHtml(ind.matchedName)}</strong>, como o nome aparece no faturamento.
    </div>` : "";
  if (kind === "GERENTE") {
    const ritos = ind.feedbacksExpected
      ? `${ind.feedbacksDone} de ${ind.feedbacksExpected} vendedores` : "—";
    return `
      <div>
        ${indicadorLinha("Faturamento líquido", currency(ind.revenueNet), `meta ${currency(ind.revenueGoal)}`)}
        ${indicadorLinha("Atingimento", pct(ind.goalAttainmentPct), "", Number(ind.goalAttainmentPct) >= 95)}
        ${indicadorLinha("Devolução", pct(ind.returnsPct), "", Number(ind.returnsPct) <= 3)}
        ${indicadorLinha("Desconto médio", pct(ind.discountPct), "")}
        ${indicadorLinha("Ticket médio", currency(ind.ticketAverage), "")}
        ${indicadorLinha("Feedbacks do mês", ritos, "", ind.feedbacksDone >= ind.feedbacksExpected)}
        ${indicadorLinha("Reuniões registradas", number(ind.meetingsPublished), "", ind.meetingsPublished > 0)}
        ${indicadorLinha("PDIs ativos", number(ind.pdiActive), ind.pdiOverdue ? `${ind.pdiOverdue} com prazo vencido` : "", ind.pdiOverdue === 0)}
      </div>`;
  }
  const metaCallsMes = Number(ind.callsTarget || 60);
  const metaCallsHoje = Number(ind.callsTargetToDate || metaCallsMes);
  const ritmo = ind.projectedGoalAttainmentPct ?? ind.goalAttainmentPct;
  const dias = ind.elapsedWorkingDays && ind.totalWorkingDays
    ? `${ind.elapsedWorkingDays} de ${ind.totalWorkingDays} dias úteis` : "";
  return `
    <div>
      ${aviso}
      ${indicadorLinha("Faturamento líquido", currency(ind.revenueNet), `meta ${currency(ind.revenueGoal)}`)}
      ${indicadorLinha("Atingimento", pct(ind.goalAttainmentPct), dias)}
      ${indicadorLinha("Projeção para o mês", pct(ritmo), "é o que diz se está no ritmo", Number(ritmo) >= 95)}
      ${indicadorLinha("Ligações", `${number(ind.calls)}`,
          `esperado até hoje: ${metaCallsHoje} · mês: ${metaCallsMes}`, Number(ind.calls) >= metaCallsHoje)}
      ${indicadorLinha("Contatos registrados", number(ind.contacts), "")}
      ${indicadorLinha("Clientes atendidos", number(ind.distinctClients), `média da unidade: ${number(ind.distinctClientsUnit)}`, Number(ind.distinctClients) >= Number(ind.distinctClientsUnit))}
      ${indicadorLinha("Ticket médio", currency(ind.ticketAverage), `unidade: ${currency(ind.ticketAverageUnit)}`, Number(ind.ticketAverage) >= Number(ind.ticketAverageUnit))}
      ${indicadorLinha("Devolução", pct(ind.returnsPct), "", Number(ind.returnsPct) <= 3)}
      ${indicadorLinha("Desconto", pct(ind.discountPct), `unidade: ${pct(ind.discountPctUnit)}`, Number(ind.discountPct) <= Number(ind.discountPctUnit))}
      ${indicadorLinha("Carteira", `${number(ind.portfolioActive)} ativos`, `${number(ind.portfolioPreInactive)} pré-inativos · ${number(ind.portfolioInactive)} inativos`)}
    </div>`;
}

function painelGuia(guidance) {
  if (!guidance?.length) return "";
  return `
    <div class="stack" style="margin-top:8px">
      ${guidance.map((g) => `
        <div style="border-left:3px solid var(--accent);background:#f5f9ff;border-radius:0 6px 6px 0;padding:8px 12px">
          <div style="font-weight:700;font-size:13px;color:var(--accent)">${escapeHtml(g.titulo)}</div>
          <div style="font-size:12px;line-height:1.5;margin-top:4px">${escapeHtml(g.leitura)}</div>
          <div style="font-size:12px;margin-top:6px"><strong>Perguntar:</strong>
            <ul style="margin:4px 0 0 16px;padding:0">
              ${g.perguntar.map((p) => `<li>${escapeHtml(p)}</li>`).join("")}
            </ul>
          </div>
          <div style="font-size:12px;margin-top:6px"><strong>Combinar:</strong> ${escapeHtml(g.combinar)}</div>
        </div>`).join("")}
    </div>`;
}

function painelRoteiro(script) {
  if (!script?.length) return "";
  return `
    <div class="stack" style="margin-top:8px">
      ${script.map((s) => `
        <div style="display:flex;gap:10px;font-size:12px;padding:6px 0;border-bottom:1px solid var(--line)">
          <div style="min-width:150px;font-weight:700">${escapeHtml(s.etapa)}
            <span style="color:var(--muted);font-weight:400;display:block">${escapeHtml(s.tempo)}</span></div>
          <div style="line-height:1.5">${escapeHtml(s.texto)}</div>
        </div>`).join("")}
    </div>`;
}

function painelPdi(itens, personName, unitName, feedbackId, podeEditar) {
  const ativos = (itens || []).filter((i) => ["ABERTO", "EVOLUINDO"].includes(i.status));
  const fechados = (itens || []).filter((i) => !["ABERTO", "EVOLUINDO"].includes(i.status));
  const max = state.feedback?.pdiMaxActive || 3;
  return `
    <div class="subtle-card padded-card" style="margin-top:10px">
      <div class="section-title">
        <div><h3>🎯 PDI — plano de desenvolvimento</h3>
          <div class="text-small">${ativos.length} de ${max} pontos ativos. O plano continua vivo entre um feedback e outro.</div></div>
        ${podeEditar && ativos.length < max ? `
          <button class="btn btn-secondary btn-sm" onclick="novoPdi('${jsAttr(personName)}','${jsAttr(unitName || "")}',${feedbackId || "null"})">Novo ponto</button>` : ""}
      </div>
      <div class="stack" style="margin-top:8px">
        ${ativos.map((i) => `
          <div style="border-left:3px solid ${i.overdue ? "var(--bad)" : "var(--accent)"};
                      background:#fafbfc;border-radius:0 6px 6px 0;padding:8px 12px">
            <div style="display:flex;justify-content:space-between;gap:8px;flex-wrap:wrap;align-items:start">
              <div style="flex:1;min-width:200px">
                <div style="font-weight:700;font-size:13px">${escapeHtml(i.title)}</div>
                ${i.why ? `<div class="text-small" style="color:var(--muted)">${escapeHtml(i.why)}</div>` : ""}
                ${i.action ? `<div style="font-size:12px;margin-top:4px"><strong>Como:</strong> ${escapeHtml(i.action)}</div>` : ""}
                ${i.support ? `<div style="font-size:12px"><strong>Apoio:</strong> ${escapeHtml(i.support)}</div>` : ""}
                ${i.progressNote ? `<div style="font-size:12px;margin-top:4px;color:var(--muted)">Evolução: ${escapeHtml(i.progressNote)}</div>` : ""}
              </div>
              <div style="text-align:right">
                ${pdiStatusBadge(i.status)}
                ${i.dueDate ? `<div class="text-small" style="color:${i.overdue ? "var(--bad)" : "var(--muted)"};margin-top:4px">
                  ${i.overdue ? "vencido em " : "até "}${shortDate(i.dueDate)}</div>` : ""}
              </div>
            </div>
            ${podeEditar ? `
              <div class="actions" style="gap:6px;margin-top:6px">
                <button class="btn btn-ghost btn-sm" onclick='editarPdi(${JSON.stringify(i).replace(/'/g, "&#39;")},"${jsAttr(personName)}","${jsAttr(unitName || "")}")'>Atualizar</button>
                <button class="btn btn-ghost btn-sm" onclick="excluirPdi(${i.id})">Excluir</button>
              </div>` : ""}
          </div>`).join("") || '<div class="text-small" style="color:var(--muted)">Nenhum ponto de desenvolvimento em aberto.</div>'}
        ${fechados.length ? `
          <details style="margin-top:6px">
            <summary class="text-small" style="cursor:pointer;color:var(--muted)">Histórico (${fechados.length})</summary>
            ${fechados.map((i) => `
              <div style="font-size:12px;padding:4px 0;color:var(--muted)">
                ${pdiStatusBadge(i.status)} ${escapeHtml(i.title)}
                ${i.closedAt ? ` · ${shortDate(i.closedAt)}` : ""}
              </div>`).join("")}
          </details>` : ""}
      </div>
    </div>`;
}

// ─── Registro pontual ───────────────────────────────────────────────────────
//
// A conversa que não espera o fechamento do mês. Rápido de escrever e datado,
// para virar memória do feedback mensal em vez de se perder.

function novoRegistro(personName, unitName, kind) {
  const tipo = kind || "ORIENTACAO";
  const cfg = (state.feedback?.noteKinds || []).find((k) => k.id === tipo);
  state.noteEditor = {
    id: null, personName: personName || "", unitName: unitName || "",
    occurredAt: dateInDays(0), kind: tipo, summary: "", agreement: "",
    requiresAck: Boolean(cfg?.defaultAck), saving: false,
  };
  requestRender();
}

function editarRegistro(nota) {
  state.noteEditor = { ...nota, saving: false };
  requestRender();
}

function fecharRegistro() { state.noteEditor = null; requestRender(); }

/** Trocar o tipo reposiciona a ciência no padrão daquele tipo — correção já vem marcada. */
function setNoteKind(kind) {
  const n = state.noteEditor;
  if (!n) return;
  const cfg = (state.feedback?.noteKinds || []).find((k) => k.id === kind);
  n.kind = kind;
  if (!n.id) n.requiresAck = Boolean(cfg?.defaultAck);
  requestRender();
}

async function salvarRegistro() {
  const n = state.noteEditor;
  if (!n) return;
  if (!n.personName) { addMessage("error", "Selecione a pessoa."); return; }
  if (!n.summary.trim()) { addMessage("error", "Descreva o que aconteceu."); return; }
  n.saving = true; requestRender();
  try {
    const r = await api("/api/feedback/note/save", { method: "POST", body: JSON.stringify(n) });
    addMessage("success", r.requiresAck
      ? `Registro salvo. ${n.personName} recebeu a pendência de ciência.`
      : "Registro salvo.");
    state.noteEditor = null;
    if (state.feedbackEditor) await carregarPreviaFeedback();
    await loadFeedback(true);
  } catch (e) {
    addMessage("error", e.message);
    if (state.noteEditor) state.noteEditor.saving = false;
    requestRender();
  }
}

async function excluirRegistro(noteId) {
  if (!confirm("Excluir este registro?")) return;
  try {
    await api("/api/feedback/note/delete", { method: "POST", body: JSON.stringify({ noteId }) });
    if (state.feedbackEditor) await carregarPreviaFeedback();
    await loadFeedback(true);
  } catch (e) { addMessage("error", e.message); }
}

async function darCienciaRegistro(noteId) {
  const campo = document.getElementById(`note-reply-${noteId}`);
  try {
    await api("/api/feedback/note/acknowledge", {
      method: "POST",
      body: JSON.stringify({ noteId, note: campo ? campo.value.trim() : "" }),
    });
    addMessage("success", "Ciência registrada.");
    await loadFeedback(true);
  } catch (e) { addMessage("error", e.message); }
}

function noteKindCfg(kind) {
  return (state.feedback?.noteKinds || []).find((k) => k.id === kind)
    || { label: kind, icon: "•", color: "#5f6368", bg: "#f1f3f4" };
}

function registroCard(n, podeEditar, compacto) {
  const cfg = noteKindCfg(n.kind);
  const pendente = n.isMe && n.requiresAck && !n.acknowledgedAt;
  return `
    <div style="border-left:3px solid ${cfg.color};background:${compacto ? "#fafbfc" : "#fff"};
                border-radius:0 6px 6px 0;padding:8px 12px;${compacto ? "" : "border:1px solid var(--line);border-left-width:3px"}">
      <div style="display:flex;justify-content:space-between;gap:8px;flex-wrap:wrap;align-items:start">
        <div style="flex:1;min-width:220px">
          <div style="display:flex;gap:6px;align-items:center;flex-wrap:wrap;margin-bottom:2px">
            <span class="status-tag" style="background:${cfg.bg};color:${cfg.color}">${cfg.icon} ${escapeHtml(cfg.label)}</span>
            <span class="text-small" style="color:var(--muted)">${shortDate(n.occurredAt)}</span>
            ${!compacto ? `<strong style="font-size:13px">${escapeHtml(n.personName)}</strong>` : ""}
            ${n.requiresAck ? (n.acknowledgedAt
              ? '<span class="status-tag good">✓ Ciente</span>'
              : '<span class="status-tag warn">Aguardando ciência</span>') : ""}
          </div>
          <div style="font-size:13px;line-height:1.5;white-space:pre-wrap">${escapeHtml(n.summary)}</div>
          ${n.agreement ? `<div style="font-size:12px;margin-top:4px"><strong>Combinado:</strong> ${escapeHtml(n.agreement)}</div>` : ""}
          ${n.personNote ? `<div style="font-size:12px;margin-top:4px;color:var(--accent)">💬 ${escapeHtml(n.personNote)}</div>` : ""}
          <div class="text-small" style="color:var(--muted);margin-top:2px">por ${escapeHtml(n.authorName)}</div>
        </div>
        ${podeEditar ? `
          <div style="display:flex;gap:4px">
            <button class="btn btn-ghost btn-sm" onclick='editarRegistro(${JSON.stringify(n).replace(/'/g, "&#39;")})'>Editar</button>
            <button class="btn btn-ghost btn-sm" onclick="excluirRegistro(${n.id})">Excluir</button>
          </div>` : ""}
      </div>
      ${pendente ? `
        <div style="margin-top:8px;padding-top:8px;border-top:1px solid var(--line)">
          <input id="note-reply-${n.id}" style="font-size:12px" placeholder="Quer responder algo? (opcional)" />
          <div class="actions" style="margin-top:6px">
            <button class="btn btn-primary btn-sm" onclick="darCienciaRegistro(${n.id})">Estou ciente</button>
          </div>
        </div>` : ""}
    </div>`;
}

function registroEditorModal() {
  const n = state.noteEditor;
  const cfg = noteKindCfg(n.kind);
  const pessoas = state.feedback?.people || [];
  return `
    <div class="client-drawer-overlay open modal-dim" onclick="fecharRegistro()" style="z-index:60">
      <div class="panel modal-panel" style="max-width:620px;margin:6vh auto;padding:22px" onclick="event.stopPropagation()">
        <div class="section-title">
          <div><h3>${n.id ? "Editar" : "Novo"} registro de acompanhamento</h3>
            <div class="text-small">Rápido e datado. Vira memória do feedback mensal.</div></div>
          <button class="btn btn-ghost btn-sm" onclick="fecharRegistro()">Fechar</button>
        </div>

        <div style="display:flex;gap:6px;flex-wrap:wrap;margin-top:12px">
          ${(state.feedback?.noteKinds || []).map((k) => `
            <button type="button" onclick="setNoteKind('${k.id}')" title="${escapeHtml(k.hint)}"
              style="border:1px solid ${n.kind === k.id ? k.color : "var(--line)"};
                     background:${n.kind === k.id ? k.bg : "#fff"};
                     color:${n.kind === k.id ? k.color : "var(--muted)"};
                     border-radius:14px;padding:5px 12px;font-size:12px;
                     font-weight:${n.kind === k.id ? "700" : "500"};cursor:pointer">
              ${k.icon} ${escapeHtml(k.label)}
            </button>`).join("")}
        </div>
        <div class="text-small" style="color:var(--muted);margin-top:6px">${escapeHtml(cfg.hint || "")}</div>

        <div style="display:grid;grid-template-columns:2fr 1fr;gap:12px;margin-top:12px">
          <div class="field"><label>Pessoa <span style="color:var(--bad)">*</span></label>
            ${n.id ? `<input value="${escapeHtml(n.personName)}" disabled />`
              : `<select onchange="state.noteEditor.personName=this.value;
                    state.noteEditor.unitName=(this.selectedOptions[0]||{}).dataset?.unit||''">
                  <option value="">Selecione…</option>
                  ${pessoas.map((p) => `<option value="${escapeHtml(p.personName)}" data-unit="${escapeHtml(p.unitName || "")}"
                    ${n.personName === p.personName ? "selected" : ""}>${escapeHtml(p.personName)}</option>`).join("")}
                </select>`}
          </div>
          <div class="field"><label>Data do fato</label>
            <input type="date" value="${escapeHtml(n.occurredAt)}" oninput="state.noteEditor.occurredAt=this.value" /></div>
        </div>

        <div class="field"><label>O que aconteceu <span style="color:var(--bad)">*</span></label>
          <textarea rows="3" style="font-family:inherit" oninput="state.noteEditor.summary=this.value"
            placeholder="Descreva o fato, não o julgamento. 'O orçamento do dia 12 ficou sem retorno e o cliente comprou fora.'">${escapeHtml(n.summary)}</textarea></div>

        <div class="field"><label>O que ficou combinado</label>
          <input value="${escapeHtml(n.agreement)}" oninput="state.noteEditor.agreement=this.value"
            placeholder="A ação e o prazo, se houve" /></div>

        <label class="check-row" style="margin-top:8px">
          <input type="checkbox" ${n.requiresAck ? "checked" : ""}
            onchange="state.noteEditor.requiresAck=this.checked;requestRender()" />
          <span>Exigir ciência da pessoa</span>
        </label>
        <div class="text-small" style="color:var(--muted);margin-top:2px">
          ${n.requiresAck
            ? "Vira pendência na tela dela, com espaço para responder. Use em correção."
            : "Fica só no histórico, sem notificar. Suficiente para reconhecimento e orientação do dia a dia."}
        </div>

        <div class="actions" style="margin-top:14px">
          <button class="btn btn-primary" ${n.saving ? "disabled" : ""} onclick="salvarRegistro()">
            ${n.saving ? "Salvando…" : "Salvar registro"}</button>
          <button class="btn btn-ghost" onclick="fecharRegistro()">Cancelar</button>
        </div>
      </div>
    </div>`;
}

// ─── Visitas gerenciais ─────────────────────────────────────────────────────
//
// Três blocos: pedidos do vendedor esperando resposta, roteiro sugerido por
// proximidade e o histórico do que já foi feito, com o efeito medido.

async function loadVisits(silencioso) {
  if (!silencioso) {
    state.ui.loading.visits = true;
    requestRender();   // pinta o "carregando" ANTES de ir à rede
  }
  try {
    state.visits = await api("/api/visits");
    if (state.visits.canManage) await loadVisitSuggestions(true);
  } catch (e) {
    state.visits = { error: e.message, visits: [], requests: [], types: [] };
  } finally {
    state.ui.loading.visits = false;
    requestRender();
  }
}

async function loadVisitSuggestions(silencioso) {
  const f = state.visitFilters;
  const q = new URLSearchParams();
  if (f.city) q.set("city", f.city);
  if (f.neighborhood) q.set("neighborhood", f.neighborhood);
  q.set("relationship", f.relationship ? "1" : "0");
  if (!silencioso) {
    state.ui.loading.visitRoute = true;
    requestRender();   // pinta o "carregando" ANTES de ir à rede
  }
  try {
    state.visitRoute = await api(`/api/visits/suggestions?${q.toString()}`);
  } catch (e) {
    state.visitRoute = { error: e.message, route: [] };
  } finally {
    state.ui.loading.visitRoute = false;
    requestRender();
  }
  return state.visitRoute;
}

function setVisitCity(cidade) {
  state.visitFilters.city = cidade;
  // Bairro pertence à cidade: trocar de cidade sem limpar deixaria um bairro
  // de outra praça selecionado e o roteiro voltaria vazio sem explicação.
  state.visitFilters.neighborhood = "";
  loadVisitSuggestions();
}

function setVisitNeighborhood(bairro) {
  state.visitFilters.neighborhood = bairro;
  loadVisitSuggestions();
}

function toggleVisitRelationship() {
  state.visitFilters.relationship = !state.visitFilters.relationship;
  loadVisitSuggestions();
}

function toggleBairro(chave) {
  state.ui.visitOpenGroups[chave] = !state.ui.visitOpenGroups[chave];
  requestRender();
}

// ─── Registro da visita ─────────────────────────────────────────────────────

function novaVisita(cliente) {
  state.visitEditor = {
    id: null,
    clientSearch: "",   // o que foi digitado na busca de cliente
    clientKey: cliente?.clientKey || "",
    clientName: cliente?.clientName || "",
    cityName: cliente?.cityName || "",
    unitName: "",
    visitType: cliente?.visitType || "RELACIONAMENTO",
    status: "REALIZADA",
    scheduledFor: "",
    occurredAt: dateInDays(0),
    managerName: state.visits?.myName || "",
    sellerName: cliente?.assignedSeller || "",
    objective: cliente?.reason || "",
    outcome: "", agreement: "", nextAction: "", nextActionDue: dateInDays(7),
    requestId: cliente?.requestId || null,
    addressLine: cliente?.addressLine || "",
    neighborhood: cliente?.neighborhood || "",
    phone: cliente?.phone || "",
    results: null, searching: false,
    saving: false,
  };
  requestRender();
}

function editarVisita(v) {
  state.visitEditor = { ...v, saving: false };
  requestRender();
}

function fecharVisitaEditor() { state.visitEditor = null; requestRender(); }

/**
 * Busca o cliente na base para vincular à visita.
 *
 * Digitar o código na mão é fonte de erro silencioso: um dígito trocado grava a
 * visita no cliente errado e o efeito é medido em quem nunca foi visitado.
 * Aqui o vínculo vem da própria base, junto com o endereço.
 */
async function buscarClienteVisita() {
  const e = state.visitEditor;
  if (!e) return;
  const campo = document.getElementById("visit-client-search");
  const termo = (campo ? campo.value : e.clientSearch || "").trim();
  e.clientSearch = termo;
  if (termo.length < 2) { addMessage("warn", "Digite ao menos 2 caracteres."); return; }
  e.searching = true; e.results = null; requestRender();
  try {
    const r = await api(`/api/visits/client-search?q=${encodeURIComponent(termo)}`);
    e.results = r.clients || [];
    if (!e.results.length) addMessage("warn", "Nenhum cliente encontrado com esse código ou nome.");
  } catch (err) {
    addMessage("error", err.message);
    e.results = [];
  } finally {
    e.searching = false;
    requestRender();
  }
}

function escolherClienteVisita(indice) {
  const e = state.visitEditor;
  if (!e || !e.results) return;
  const c = e.results[indice];
  if (!c) return;
  Object.assign(e, {
    clientKey: c.clientKey,
    clientName: c.clientName,
    cityName: c.cityName,
    addressLine: c.addressLine,
    neighborhood: c.neighborhood,
    phone: c.phone,
    sellerName: e.sellerName || c.assignedSeller || "",
    results: null,
  });
  requestRender();
}

function trocarClienteVisita() {
  const e = state.visitEditor;
  if (!e) return;
  Object.assign(e, { clientKey: "", clientName: "", addressLine: "", results: null });
  requestRender();
}

async function salvarVisita() {
  const v = state.visitEditor;
  if (!v) return;
  if (!v.clientKey) { addMessage("error", "Selecione o cliente."); return; }
  v.saving = true; requestRender();
  try {
    const r = await api("/api/visits/save", { method: "POST", body: JSON.stringify(v) });
    addMessage("success", r.taskId
      ? "Visita registrada. A ação combinada virou tarefa do vendedor."
      : "Visita registrada.");
    state.visitEditor = null;
    await loadVisits(true);
  } catch (e) {
    addMessage("error", e.message);
    if (state.visitEditor) state.visitEditor.saving = false;
    requestRender();
  }
}

async function excluirVisita(visitId) {
  if (!confirm("Excluir esta visita?")) return;
  try {
    await api("/api/visits/delete", { method: "POST", body: JSON.stringify({ visitId }) });
    await loadVisits(true);
  } catch (e) { addMessage("error", e.message); }
}

async function responderPedido(requestId, aceitar) {
  try {
    await api("/api/visits/request/resolve", {
      method: "POST", body: JSON.stringify({ requestId, accept: aceitar }),
    });
    addMessage("success", aceitar ? "Pedido aceito." : "Pedido recusado.");
    await loadVisits(true);
  } catch (e) { addMessage("error", e.message); }
}

// ─── Componentes ────────────────────────────────────────────────────────────

function visitTypeCfg(tipo) {
  return (state.visits?.types || []).find((t) => t.id === tipo)
    || { label: tipo, icon: "📍", color: "#5f6368", bg: "#f1f3f4" };
}

function visitTypeBadge(tipo) {
  const t = visitTypeCfg(tipo);
  return `<span class="status-tag" style="background:${t.bg};color:${t.color}">${t.icon} ${escapeHtml(t.label)}</span>`;
}

/** Efeito da visita: verde quando cresceu, vermelho quando caiu. */
function efeitoVisita(v) {
  if (v.revenueBefore === null || v.revenueBefore === undefined) {
    return `<span class="text-small" style="color:var(--muted)">efeito em apuração</span>`;
  }
  const pct = v.effectPct;
  const cor = pct === null ? "var(--muted)" : pct >= 0 ? "var(--good)" : "var(--bad)";
  const seta = pct === null ? "" : pct >= 0 ? "▲" : "▼";
  return `
    <span class="text-small">
      <strong style="color:${cor}">${seta} ${pct === null ? "—" : pct + "%"}</strong>
      <span style="color:var(--muted)"> · ${currency(v.revenueBefore)} → ${currency(v.revenueAfter)}</span>
    </span>`;
}

function clienteRoteiroLinha(c, podeGerir) {
  return `
    <div style="display:flex;justify-content:space-between;gap:10px;flex-wrap:wrap;align-items:start;
                padding:8px 10px;border-bottom:1px solid var(--line)">
      <div style="flex:1;min-width:230px">
        <div style="display:flex;gap:6px;align-items:center;flex-wrap:wrap">
          ${visitTypeBadge(c.visitType)}
          <strong style="font-size:13px">${escapeHtml(c.clientName)}</strong>
        </div>
        <div class="text-small" style="color:var(--muted)">
          ${c.addressLine ? escapeHtml(c.addressLine) : "Endereço não cadastrado"}
          ${c.postalCode ? ` · ${escapeHtml(c.postalCode)}` : ""}
        </div>
        <div class="text-small">${escapeHtml(c.reason)}</div>
        ${c.requestedBy ? `<div class="text-small" style="color:var(--bad);font-weight:600">Pedido por ${escapeHtml(c.requestedBy)}</div>` : ""}
      </div>
      <div style="text-align:right;min-width:130px">
        <div class="text-small">média ${currency(c.averageRevenue)}/mês</div>
        ${c.phone ? `<div class="text-small" style="color:var(--muted)">📞 ${escapeHtml(c.phone)}</div>` : ""}
        ${c.assignedSeller ? `<div class="text-small" style="color:var(--muted)">${escapeHtml(c.assignedSeller)}</div>` : ""}
        <div class="actions" style="gap:4px;margin-top:4px;justify-content:flex-end">
          <button class="btn btn-ghost btn-sm" onclick="openCrmClient('${jsAttr(c.clientKey)}', false)">Ficha</button>
          ${podeGerir ? `<button class="btn btn-primary btn-sm" onclick='novaVisita(${JSON.stringify(c).replace(/'/g, "&#39;")})'>Registrar visita</button>` : ""}
        </div>
      </div>
    </div>`;
}

function visitaCard(v, podeGerir) {
  return `
    <div class="crm-card clean" style="padding:12px">
      <div style="display:flex;justify-content:space-between;gap:10px;flex-wrap:wrap;align-items:start">
        <div style="flex:1;min-width:230px">
          <div style="display:flex;gap:6px;align-items:center;flex-wrap:wrap;margin-bottom:2px">
            ${visitTypeBadge(v.visitType)}
            ${v.status === "PLANEJADA" ? '<span class="status-tag warn">Planejada</span>' : ""}
            ${v.status === "CANCELADA" ? '<span class="status-tag">Cancelada</span>' : ""}
          </div>
          <div style="font-weight:700;font-size:13px">${escapeHtml(v.clientName)}</div>
          <div class="text-small" style="color:var(--muted)">
            ${v.occurredAt ? shortDate(v.occurredAt) : (v.scheduledFor ? `agendada ${shortDate(v.scheduledFor)}` : "")}
            ${v.cityName ? ` · ${escapeHtml(v.cityName)}` : ""}
            ${v.neighborhood ? ` · ${escapeHtml(v.neighborhood)}` : ""}
            · ${escapeHtml(v.managerName)}${v.sellerName ? ` com ${escapeHtml(v.sellerName)}` : ""}
          </div>
          ${v.outcome ? `<div style="font-size:12px;margin-top:4px;white-space:pre-wrap">${escapeHtml(v.outcome)}</div>` : ""}
          ${v.agreement ? `<div style="font-size:12px;margin-top:2px"><strong>Combinado:</strong> ${escapeHtml(v.agreement)}</div>` : ""}
          ${v.nextAction ? `<div style="font-size:12px"><strong>Próximo passo:</strong> ${escapeHtml(v.nextAction)}${v.nextActionDue ? ` (${shortDate(v.nextActionDue)})` : ""}</div>` : ""}
        </div>
        <div style="text-align:right;min-width:150px">
          ${v.status === "REALIZADA" ? efeitoVisita(v) : ""}
          ${podeGerir ? `
            <div class="actions" style="gap:4px;margin-top:6px;justify-content:flex-end">
              <button class="btn btn-ghost btn-sm" onclick='editarVisita(${JSON.stringify(v).replace(/'/g, "&#39;")})'>Editar</button>
              <button class="btn btn-ghost btn-sm" onclick="excluirVisita(${v.id})">Excluir</button>
            </div>` : ""}
        </div>
      </div>
    </div>`;
}

// ─── Roteiro impresso e texto para WhatsApp ─────────────────────────────────
//
// Duas saídas para o mesmo roteiro, porque o gerente usa as duas: a folha (ou
// PDF) que vai no carro e o texto que ele manda no grupo antes de sair.

/** Só as cidades/bairros que interessam agora — respeita o filtro da tela. */
function roteiroParaSaida() {
  const rota = state.visitRoute || {};
  const cidades = (rota.route || []).filter(
    (c) => !state.visitFilters.city || c.cityName === state.visitFilters.city)
    // O que o gestor imprime tem de ser o que ele está vendo na tela.
    .map((c) => !state.visitFilters.neighborhood ? c : {
      ...c,
      neighborhoods: (c.neighborhoods || []).filter(
        (b) => b.neighborhood === state.visitFilters.neighborhood),
    })
    .filter((c) => (c.neighborhoods || []).length);
  return cidades;
}

function dataPorExtenso() {
  const d = new Date();
  const dias = ["domingo", "segunda-feira", "terça-feira", "quarta-feira", "quinta-feira", "sexta-feira", "sábado"];
  const meses = ["janeiro", "fevereiro", "março", "abril", "maio", "junho",
                 "julho", "agosto", "setembro", "outubro", "novembro", "dezembro"];
  return `${dias[d.getDay()]}, ${d.getDate()} de ${meses[d.getMonth()]} de ${d.getFullYear()}`;
}

/**
 * Monta a folha e chama a impressão.
 *
 * O conteúdo é escrito num container da própria página e o @media print troca
 * o que fica visível. Abrir janela nova esbarraria no bloqueador de pop-up e
 * perderia o estilo.
 */
function imprimirRoteiro() {
  const cidades = roteiroParaSaida();
  if (!cidades.length) { addMessage("warn", "Não há clientes no roteiro para imprimir."); return; }

  const totalClientes = cidades.reduce((s, c) => s + c.count, 0);
  const totalPotencial = cidades.reduce((s, c) => s + c.potential, 0);

  const html = `
    <div class="print-header">
      <h1>Roteiro de visitas${state.visitFilters.city ? ` — ${escapeHtml(state.visitFilters.city)}` : ""}</h1>
      <div class="sub">
        ${escapeHtml(dataPorExtenso())} ·
        ${escapeHtml(state.visits?.myName || "")} ·
        ${totalClientes} cliente(s) · potencial ${currency(totalPotencial)}/mês
      </div>
    </div>
    ${cidades.map((cidade) => `
      ${cidades.length > 1 ? `<div class="print-bairro" style="background:#000;color:#fff">${escapeHtml(cidade.cityName)}</div>` : ""}
      ${cidade.neighborhoods.map((b) => `
        <div class="print-bairro">${escapeHtml(b.neighborhood)} — ${b.count} cliente(s) · ${currency(b.potential)}/mês</div>
        ${b.clients.map((c) => `
          <div class="print-client">
            <div class="nome">☐ ${escapeHtml(c.clientName)}</div>
            <div class="linha"><span class="rotulo">Endereço:</span> ${escapeHtml(c.addressLine || "não cadastrado")}${c.postalCode ? ` — CEP ${escapeHtml(c.postalCode)}` : ""}</div>
            <div class="linha"><span class="rotulo">Telefone:</span> ${escapeHtml(c.phone || "—")} &nbsp;·&nbsp;
              <span class="rotulo">Vendedor:</span> ${escapeHtml(c.assignedSeller || "sem vendedor")}</div>
            <div class="linha"><span class="rotulo">Motivo:</span> ${escapeHtml(c.reason)}${c.requestedBy ? ` (pedido por ${escapeHtml(c.requestedBy)})` : ""}</div>
            <div class="linha"><span class="rotulo">Média mensal:</span> ${currency(c.averageRevenue)} &nbsp;·&nbsp;
              <span class="rotulo">Situação:</span> ${escapeHtml(c.statusCode || "—")}${c.daysWithoutPurchase ? ` (${c.daysWithoutPurchase} dias sem compra)` : ""}${c.classCode ? ` · ${escapeHtml(c.classCode)}` : ""}</div>
            <div class="print-anotacao">
              O que foi tratado / o que ficou combinado:
              <div class="risco"></div><div class="risco"></div>
            </div>
          </div>`).join("")}
      `).join("")}
    `).join("")}
    <div class="print-footer">
      Passini Autopeças · CRM Comercial · Registre a visita no sistema no mesmo dia —
      visita sem registro não conta e o efeito não é medido.
    </div>`;

  let area = document.getElementById("print-area");
  if (!area) {
    area = document.createElement("div");
    area.id = "print-area";
    area.className = "print-area";
    document.body.appendChild(area);
  }
  area.innerHTML = html;
  window.print();
}

/** Texto enxuto para colar no WhatsApp. Sem tabela — celular quebra tudo. */
function textoRoteiroWhatsapp() {
  const cidades = roteiroParaSaida();
  const linhas = [];
  const totalClientes = cidades.reduce((s, c) => s + c.count, 0);
  linhas.push(`*ROTEIRO DE VISITAS*`);
  linhas.push(`${dataPorExtenso()}`);
  linhas.push(`${totalClientes} cliente(s)${state.visitFilters.city ? ` · ${state.visitFilters.city}` : ""}`);

  cidades.forEach((cidade) => {
    if (cidades.length > 1) linhas.push(`\n*${cidade.cityName}*`);
    cidade.neighborhoods.forEach((b) => {
      linhas.push(`\n*${b.neighborhood}*`);
      b.clients.forEach((c, i) => {
        linhas.push(`${i + 1}. *${c.clientName}*`);
        linhas.push(`   ${c.addressLine || "endereço não cadastrado"}`);
        if (c.phone) linhas.push(`   ${c.phone}`);
        linhas.push(`   ${c.reason}`);
        if (c.requestedBy) linhas.push(`   Pedido por ${c.requestedBy}`);
      });
    });
  });
  linhas.push(`\n_Registrar a visita no CRM no mesmo dia._`);
  return linhas.join("\n");
}

async function copiarRoteiroWhatsapp() {
  const cidades = roteiroParaSaida();
  if (!cidades.length) { addMessage("warn", "Não há clientes no roteiro para copiar."); return; }
  const texto = textoRoteiroWhatsapp();
  if (await copyToClipboard(texto)) {
    addMessage("success", "Roteiro copiado. É só colar no WhatsApp.");
  } else {
    // Servidor em HTTP não libera a área de transferência — abre para cópia manual.
    showCopyFallback(texto, "Roteiro de visitas");
  }
}

/** Situação do pedido, na linguagem do vendedor. */
function pedidoStatusBadge(status) {
  const cfg = {
    PENDENTE: { label: "Aguardando o gerente", color: "#b06000", bg: "#fef7e0" },
    ACEITA:   { label: "✓ Aceito",             color: "#1e8e3e", bg: "#e6f4ea" },
    RECUSADA: { label: "Recusado",             color: "#c5221f", bg: "#fce8e6" },
  }[status] || { label: status, color: "#5f6368", bg: "#f1f3f4" };
  return `<span class="status-tag" style="background:${cfg.bg};color:${cfg.color}">${escapeHtml(cfg.label)}</span>`;
}

/**
 * Tela do vendedor. Duas perguntas que ele faz:
 * "o que aconteceu com o que eu pedi?" e "o que o gerente combinou no meu cliente?".
 * A segunda importa mais do que parece — cliente cobra do vendedor o que foi
 * prometido na visita, e ele precisa saber antes de ser pego de surpresa.
 */
function visitasViewVendedor() {
  const pedidos = state.visits.requests || [];
  const visitas = state.visits.visits || [];
  const pendentes = pedidos.filter((p) => p.status === "PENDENTE");
  const respondidos = pedidos.filter((p) => p.status !== "PENDENTE");

  return `
    <div class="stack">
      ${state.visitRequestEditor ? pedidoVisitaModal() : ""}

      <div class="panel" style="padding:14px 18px">
        <div class="text-small" style="line-height:1.6">
          Precisa da presença do gerente num cliente? Registre a ligação e marque
          <strong>“Pedir visita do gerente”</strong>, ou peça direto pela ficha do cliente.
          Só é possível pedir depois de uma ligação registrada — é o telefone antes da rua.
        </div>
      </div>

      <div class="table-card">
        <div class="section-title">
          <div><h3>🙋 Meus pedidos de visita</h3>
            <div class="text-small">${pendentes.length} aguardando resposta</div></div>
          <div class="soft-badge">${pedidos.length}</div>
        </div>
        <div class="stack" style="padding-top:8px">
          ${pedidos.map((p) => `
            <div style="border-left:3px solid ${p.status === "PENDENTE" ? "#f39c12" : p.status === "ACEITA" ? "#1e8e3e" : "#c5221f"};
                        background:#fff;border:1px solid var(--line);border-left-width:3px;
                        border-radius:0 6px 6px 0;padding:10px 12px">
              <div style="display:flex;justify-content:space-between;gap:10px;flex-wrap:wrap;align-items:start">
                <div style="flex:1;min-width:220px">
                  <div style="display:flex;gap:6px;align-items:center;flex-wrap:wrap;margin-bottom:2px">
                    ${pedidoStatusBadge(p.status)}
                    <span class="text-small" style="color:var(--muted)">pedido em ${shortDate(p.createdAt)}</span>
                  </div>
                  <div style="font-weight:700;font-size:13px">${escapeHtml(p.clientName)}</div>
                  <div style="font-size:12px;margin-top:2px">${escapeHtml(p.reason)}</div>
                  ${p.managerNote ? `
                    <div style="font-size:12px;margin-top:4px;color:var(--accent)">
                      <strong>Resposta do gerente:</strong> ${escapeHtml(p.managerNote)}</div>` : ""}
                </div>
                <button class="btn btn-ghost btn-sm" onclick="openCrmClient('${jsAttr(p.clientKey)}', false)">Ficha</button>
              </div>
            </div>`).join("")
            || emptyStateCard("Você ainda não pediu nenhuma visita.")}
        </div>
      </div>

      <div class="table-card">
        <div class="section-title">
          <div><h3>🗺️ Visitas na minha carteira</h3>
            <div class="text-small">
              O que o gerente tratou e o que ficou combinado com o cliente.
              O efeito compara o faturamento 60 dias antes e depois.
            </div></div>
          <div class="soft-badge">${visitas.length}</div>
        </div>
        <div class="stack" style="padding-top:8px">
          ${visitas.map((v) => `
            <div class="crm-card clean" style="padding:12px">
              <div style="display:flex;justify-content:space-between;gap:10px;flex-wrap:wrap;align-items:start">
                <div style="flex:1;min-width:230px">
                  <div style="display:flex;gap:6px;align-items:center;flex-wrap:wrap;margin-bottom:2px">
                    ${visitTypeBadge(v.visitType)}
                    ${v.status === "PLANEJADA" ? '<span class="status-tag warn">Planejada</span>' : ""}
                    ${v.sellerName ? '<span class="status-tag good">Você foi junto</span>' : ""}
                  </div>
                  <div style="font-weight:700;font-size:13px">${escapeHtml(v.clientName)}</div>
                  <div class="text-small" style="color:var(--muted)">
                    ${v.occurredAt ? shortDate(v.occurredAt) : (v.scheduledFor ? `prevista ${shortDate(v.scheduledFor)}` : "")}
                    · ${escapeHtml(v.managerName)}
                  </div>
                  ${v.outcome ? `<div style="font-size:12px;margin-top:4px;white-space:pre-wrap">${escapeHtml(v.outcome)}</div>` : ""}
                  ${v.agreement ? `
                    <div style="font-size:12px;margin-top:4px;background:#fff9e6;border-left:3px solid #f4c25f;
                                padding:4px 8px;border-radius:0 4px 4px 0">
                      <strong>Combinado com o cliente:</strong> ${escapeHtml(v.agreement)}
                    </div>` : ""}
                  ${v.nextAction ? `
                    <div style="font-size:12px;margin-top:4px;color:var(--accent)">
                      <strong>Sua tarefa:</strong> ${escapeHtml(v.nextAction)}${v.nextActionDue ? ` — até ${shortDate(v.nextActionDue)}` : ""}
                    </div>` : ""}
                </div>
                <div style="text-align:right;min-width:140px">
                  ${v.status === "REALIZADA" ? efeitoVisita(v) : ""}
                  <div class="actions" style="gap:4px;margin-top:6px;justify-content:flex-end">
                    <button class="btn btn-ghost btn-sm" onclick="openCrmClient('${jsAttr(v.clientKey)}', false)">Ficha</button>
                    ${v.nextAction ? `<button class="btn btn-secondary btn-sm" onclick="goToTab('crm-tarefas')">Ver tarefa</button>` : ""}
                  </div>
                </div>
              </div>
            </div>`).join("")
            || emptyStateCard("Nenhuma visita registrada nos seus clientes ainda.")}
        </div>
      </div>
    </div>`;
}

function visitasView() {
  if (!state.visits) { loadVisits(); return `<div class="loader panel">Carregando visitas…</div>`; }
  if (state.visits.error) return `<div class="message error">${escapeHtml(state.visits.error)}</div>`;

  const podeGerir = Boolean(state.visits.canManage);
  if (!podeGerir) return visitasViewVendedor();

  const pedidos = state.visits.requests || [];
  const visitas = state.visits.visits || [];
  const rota = state.visitRoute || {};
  const f = state.visitFilters;

  return `
    <div class="stack">
      ${state.visitEditor ? visitaEditorModal() : ""}
      ${state.visitRequestEditor ? pedidoVisitaModal() : ""}

      ${pedidos.length ? `
        <div class="table-card" style="border-left:4px solid #e74c3c">
          <div class="section-title">
            <div><h3>🙋 Pedidos de visita da equipe</h3>
              <div class="text-small">${podeGerir
                ? "O vendedor já ligou e pediu sua presença. Aceite e registre, ou recuse com o motivo."
                : "Pedidos que você enviou ao gerente."}</div></div>
            <div class="soft-badge" style="background:#fde8e8;color:#e74c3c">${pedidos.length}</div>
          </div>
          <div class="stack" style="padding-top:8px">
            ${pedidos.map((p) => `
              <div style="border-left:3px solid #e74c3c;background:#fff;border:1px solid var(--line);
                          border-left-width:3px;border-radius:0 6px 6px 0;padding:10px 12px">
                <div style="display:flex;justify-content:space-between;gap:10px;flex-wrap:wrap;align-items:start">
                  <div style="flex:1;min-width:220px">
                    <div style="font-weight:700;font-size:13px">${escapeHtml(p.clientName)}</div>
                    <div class="text-small" style="color:var(--muted)">
                      ${escapeHtml(p.sellerName)}${p.cityName ? ` · ${escapeHtml(p.cityName)}` : ""} · ${shortDate(p.createdAt)}</div>
                    <div style="font-size:13px;margin-top:4px">${escapeHtml(p.reason)}</div>
                  </div>
                  <div class="actions" style="gap:6px">
                    <button class="btn btn-ghost btn-sm" onclick="openCrmClient('${jsAttr(p.clientKey)}', false)">Ficha</button>
                    ${podeGerir ? `
                      <button class="btn btn-primary btn-sm"
                        onclick='novaVisita({clientKey:"${jsAttr(p.clientKey)}",clientName:"${jsAttr(p.clientName)}",cityName:"${jsAttr(p.cityName)}",visitType:"SOLICITADA",reason:"${jsAttr(p.reason)}",requestId:${p.id}})'>Registrar visita</button>
                      <button class="btn btn-ghost btn-sm" onclick="responderPedido(${p.id}, false)">Recusar</button>` : ""}
                  </div>
                </div>
              </div>`).join("")}
          </div>
        </div>` : ""}

      ${podeGerir ? `
        <div class="table-card">
          <div class="section-title">
            <div><h3>🗺️ Roteiro sugerido</h3>
              <div class="text-small">
                Agrupado por bairro e rua para você não cruzar a cidade duas vezes.
                Só entra quem teve ligação registrada nos últimos ${rota.params?.callWindowDays || 30} dias.
              </div></div>
            <div class="soft-badge">${rota.total || 0}</div>
          </div>
          <div style="display:flex;gap:8px;flex-wrap:wrap;align-items:center;padding:10px 0">
            <span class="text-small" style="font-weight:700;color:var(--muted)">CIDADE</span>
            <select style="min-width:160px" onchange="setVisitCity(this.value)">
              <option value="">Todas</option>
              ${(rota.cities || []).map((c) => `<option value="${escapeHtml(c)}" ${f.city === c ? "selected" : ""}>${escapeHtml(c)}</option>`).join("")}
            </select>
            <span class="text-small" style="font-weight:700;color:var(--muted)">BAIRRO</span>
            <select style="min-width:170px" onchange="setVisitNeighborhood(this.value)">
              <option value="">Todos${f.city ? ` de ${escapeHtml(f.city)}` : ""}</option>
              ${(rota.neighborhoods || []).map((b) => `
                <option value="${escapeHtml(b)}" ${f.neighborhood === b ? "selected" : ""}>${escapeHtml(b)}</option>`).join("")}
            </select>
            ${f.neighborhood ? `<button class="btn btn-ghost btn-sm" onclick="setVisitNeighborhood('')">Limpar bairro</button>` : ""}
            <label class="check-row" style="font-weight:500">
              <input type="checkbox" ${f.relationship ? "checked" : ""} onchange="toggleVisitRelationship()" />
              <span>Incluir visitas de relacionamento no caminho</span>
            </label>
            ${botaoAtualizar("visitas", "loadVisitSuggestions()", { mensagem: "Sugestões de visita atualizadas." })}
            <span style="flex:1"></span>
            <button class="btn btn-secondary btn-sm" onclick="imprimirRoteiro()">🖨️ Imprimir / PDF</button>
            <button class="btn btn-secondary btn-sm" onclick="copiarRoteiroWhatsapp()">💬 Copiar p/ WhatsApp</button>
          </div>
          ${state.ui.loading.visitRoute ? '<div class="loader">Montando roteiro…</div>' : ""}
          ${rota.error ? `<div class="message error">${escapeHtml(rota.error)}</div>` : ""}
          <div class="stack">
            ${(rota.route || []).map((cidade) => `
              <div>
                <div style="display:flex;justify-content:space-between;align-items:baseline;
                            padding:6px 0;border-bottom:2px solid var(--accent)">
                  <strong style="font-size:14px">📍 ${escapeHtml(cidade.cityName)}</strong>
                  <span class="text-small">${cidade.count} cliente(s) · potencial ${currency(cidade.potential)}/mês</span>
                </div>
                ${cidade.neighborhoods.map((b) => {
                  const chave = `${cidade.cityName}|${b.neighborhood}`;
                  const aberto = state.ui.visitOpenGroups[chave] !== false;
                  return `
                    <div style="margin-top:6px">
                      <button type="button" onclick="toggleBairro('${jsAttr(chave)}')"
                        style="width:100%;text-align:left;border:none;background:#f5f9ff;border-radius:6px;
                               padding:6px 10px;cursor:pointer;display:flex;justify-content:space-between;
                               align-items:center;font-size:13px;font-weight:700;color:var(--accent)">
                        <span>${aberto ? "▾" : "▸"} ${escapeHtml(b.neighborhood)}</span>
                        <span style="font-weight:500;color:var(--muted)">${b.count} · ${currency(b.potential)}/mês</span>
                      </button>
                      ${aberto ? b.clients.map((c) => clienteRoteiroLinha(c, podeGerir)).join("") : ""}
                    </div>`;
                }).join("")}
              </div>`).join("") || (state.ui.loading.visitRoute ? "" : emptyStateCard(
                "Nenhuma sugestão. Lembre que o cliente só entra depois de uma ligação registrada pelo vendedor."))}
          </div>
        </div>` : ""}

      <div class="table-card">
        <div class="section-title">
          <div><h3>Visitas registradas</h3>
            <div class="text-small">O efeito compara o faturamento 60 dias antes e 60 dias depois.</div></div>
          <div style="display:flex;gap:8px;align-items:center">
            ${podeGerir ? `<button class="btn btn-secondary btn-sm" onclick="novaVisita(null)">＋ Nova visita</button>` : ""}
            <div class="soft-badge">${visitas.length}</div>
          </div>
        </div>
        <div class="stack" style="padding-top:8px">
          ${visitas.map((v) => visitaCard(v, podeGerir)).join("")
            || emptyStateCard("Nenhuma visita registrada ainda.")}
        </div>
      </div>
    </div>`;
}

function visitaEditorModal() {
  const v = state.visitEditor;
  const realizada = v.status === "REALIZADA";
  return `
    <div class="client-drawer-overlay open modal-dim" onclick="fecharVisitaEditor()">
      <div class="panel modal-panel" data-keep-scroll="visita-editor"
           style="max-width:720px;margin:5vh auto;padding:22px;max-height:90vh;overflow:auto"
           onclick="event.stopPropagation()">
        <div class="section-title">
          <div><h3>${v.id ? "Editar" : "Registrar"} visita</h3>
            <div class="text-small">${escapeHtml(v.clientName || "Selecione o cliente")}
              ${v.addressLine ? ` · ${escapeHtml(v.addressLine)}` : ""}</div></div>
          <button class="btn btn-ghost btn-sm" onclick="fecharVisitaEditor()">Fechar</button>
        </div>

        <div style="display:flex;gap:6px;flex-wrap:wrap;margin-top:12px">
          ${(state.visits?.types || []).map((t) => `
            <button type="button" onclick="state.visitEditor.visitType='${t.id}';requestRender()"
              title="${escapeHtml(t.hint)}"
              style="border:1px solid ${v.visitType === t.id ? t.color : "var(--line)"};
                     background:${v.visitType === t.id ? t.bg : "#fff"};
                     color:${v.visitType === t.id ? t.color : "var(--muted)"};
                     border-radius:14px;padding:5px 12px;font-size:12px;
                     font-weight:${v.visitType === t.id ? "700" : "500"};cursor:pointer">
              ${t.icon} ${escapeHtml(t.label)}
            </button>`).join("")}
        </div>
        <div class="text-small" style="color:var(--muted);margin-top:6px">
          ${escapeHtml(visitTypeCfg(v.visitType).hint || "")}
        </div>

        ${!v.clientKey ? `
          <div class="field" style="margin-top:12px">
            <label>Cliente <span style="color:var(--bad)">*</span></label>
            <div style="display:flex;gap:8px">
              <input id="visit-client-search" style="flex:1"
                placeholder="Buscar por código, razão social ou nome fantasia — Enter para buscar"
                value="${escapeHtml(v.clientSearch || "")}"
                oninput="state.visitEditor.clientSearch=this.value"
                onkeydown="if(event.key==='Enter'){event.preventDefault();buscarClienteVisita();}" />
              <button class="btn btn-secondary" onclick="buscarClienteVisita()">
                ${v.searching ? "Buscando…" : "Buscar"}</button>
            </div>
            ${v.results ? `
              <div style="border:1px solid var(--line);border-radius:8px;max-height:230px;overflow:auto;margin-top:8px">
                ${v.results.map((c, i) => `
                  <button type="button" onclick="escolherClienteVisita(${i})"
                    style="width:100%;text-align:left;border:none;background:#fff;cursor:pointer;
                           padding:8px 10px;border-bottom:1px solid var(--line)">
                    <div style="font-weight:700;font-size:13px">${escapeHtml(c.clientName)}
                      <span style="color:var(--muted);font-weight:400">· ${escapeHtml(c.clientKey)}</span></div>
                    <div class="text-small" style="color:var(--muted)">
                      ${escapeHtml(c.addressLine || "endereço não cadastrado")}
                      ${c.neighborhood ? ` · ${escapeHtml(c.neighborhood)}` : ""}
                      ${c.cityName ? ` · ${escapeHtml(c.cityName)}` : ""}
                    </div>
                    ${c.assignedSeller ? `<div class="text-small" style="color:var(--muted)">Vendedor: ${escapeHtml(c.assignedSeller)}</div>` : ""}
                  </button>`).join("")
                  || '<div class="text-small" style="padding:10px;color:var(--muted)">Nenhum cliente encontrado.</div>'}
              </div>` : `
              <div class="text-small" style="color:var(--muted)">
                Ou use o roteiro sugerido — ele já preenche cliente e endereço.
              </div>`}
          </div>` : `
          <div class="subtle-card padded-card" style="margin-top:12px">
            <div style="display:flex;justify-content:space-between;gap:10px;align-items:start;flex-wrap:wrap">
              <div>
                <div style="font-weight:700;font-size:13px">${escapeHtml(v.clientName)}
                  <span style="color:var(--muted);font-weight:400">· ${escapeHtml(v.clientKey)}</span></div>
                <div class="text-small" style="color:var(--muted)">
                  ${escapeHtml(v.addressLine || "endereço não cadastrado")}
                  ${v.neighborhood ? ` · ${escapeHtml(v.neighborhood)}` : ""}
                  ${v.cityName ? ` · ${escapeHtml(v.cityName)}` : ""}
                  ${v.phone ? ` · ${escapeHtml(v.phone)}` : ""}
                </div>
              </div>
              ${!v.id ? `<button class="btn btn-ghost btn-sm" onclick="trocarClienteVisita()">Trocar cliente</button>` : ""}
            </div>
          </div>`}

        <div style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:10px;margin-top:8px">
          <div class="field"><label>Situação</label>
            <select onchange="state.visitEditor.status=this.value;requestRender()">
              ${(state.visits?.statuses || []).map((s) => `
                <option value="${s.id}" ${v.status === s.id ? "selected" : ""}>${escapeHtml(s.label)}</option>`).join("")}
            </select></div>
          <div class="field"><label>${realizada ? "Data da visita" : "Data prevista"}</label>
            <input type="date" value="${escapeHtml(realizada ? (v.occurredAt || "") : (v.scheduledFor || ""))}"
              oninput="${realizada ? "state.visitEditor.occurredAt=this.value" : "state.visitEditor.scheduledFor=this.value"}" /></div>
          <div class="field"><label>Vendedor foi junto?</label>
            <select onchange="state.visitEditor.sellerName=this.value">
              <option value="">Fui sozinho</option>
              ${(state.visits?.sellers || []).map((s) => `
                <option value="${escapeHtml(s)}" ${v.sellerName === s ? "selected" : ""}>${escapeHtml(s)}</option>`).join("")}
            </select></div>
        </div>

        <div class="field"><label>Objetivo da visita</label>
          <input value="${escapeHtml(v.objective)}" oninput="state.visitEditor.objective=this.value"
            placeholder="O que você foi resolver" /></div>

        ${realizada ? `
          <div class="field"><label>O que aconteceu <span style="color:var(--bad)">*</span></label>
            <textarea rows="3" style="font-family:inherit" oninput="state.visitEditor.outcome=this.value"
              placeholder="O que o cliente disse, o motivo real do problema, o que você observou na oficina">${escapeHtml(v.outcome)}</textarea></div>
          <div class="field"><label>O que ficou combinado com o cliente</label>
            <input value="${escapeHtml(v.agreement)}" oninput="state.visitEditor.agreement=this.value"
              placeholder="Condição, prazo, teste de uma linha, volume" /></div>
          <div style="display:grid;grid-template-columns:2fr 1fr;gap:10px">
            <div class="field"><label>Ação para o vendedor</label>
              <input value="${escapeHtml(v.nextAction)}" oninput="state.visitEditor.nextAction=this.value"
                placeholder="Vira tarefa dele automaticamente" /></div>
            <div class="field"><label>Prazo</label>
              <input type="date" value="${escapeHtml(v.nextActionDue || "")}"
                oninput="state.visitEditor.nextActionDue=this.value" /></div>
          </div>
          <div class="text-small" style="color:var(--muted)">
            A ação vira tarefa do vendedor selecionado acima — é o que faz a visita continuar
            depois que você sai de lá.
          </div>` : ""}

        <div class="actions" style="margin-top:16px">
          <button class="btn btn-primary" ${v.saving ? "disabled" : ""} onclick="salvarVisita()">
            ${v.saving ? "Salvando…" : "Salvar visita"}</button>
          <button class="btn btn-ghost" onclick="fecharVisitaEditor()">Cancelar</button>
        </div>
      </div>
    </div>`;
}

function feedbackView() {
  if (!state.feedback) { loadFeedback(); return `<div class="loader panel">Carregando feedback…</div>`; }
  if (state.feedback.error) return `<div class="message error">${escapeHtml(state.feedback.error)}</div>`;

  const podeDar = Boolean(state.feedback.canGive);
  const f = state.feedbackFilters;
  const itens = state.feedback.feedbacks || [];
  const notas = state.feedback.notes || [];
  const notasPendentes = notas.filter((n) => n.isMe && n.requiresAck && !n.acknowledgedAt);
  const notasDemais = notas.filter((n) => !notasPendentes.includes(n));
  const pendentes = itens.filter((x) => x.isMe && x.status === "PUBLICADO" && !x.acknowledgedAt);
  const meus = itens.filter((x) => x.isMe && !pendentes.includes(x));
  const daEquipe = itens.filter((x) => !x.isMe);

  // Quem da equipe ainda não recebeu feedback na competência escolhida
  const jaFeito = new Set(daEquipe.filter((x) => x.competence === f.competence).map((x) => x.personKey));
  const equipe = (state.feedback.people || []).filter((p) => p.role === "Vendedor");
  const faltando = equipe.filter((p) => !jaFeito.has(p.personKey));

  return `
    <div class="stack">
      ${state.feedbackEditor ? feedbackEditorModal() : ""}
      ${state.feedbackDetail ? feedbackDetalheModal() : ""}
      ${state.pdiEditor ? pdiEditorModal() : ""}
      ${state.noteEditor ? registroEditorModal() : ""}

      ${notasPendentes.length ? `
        <div class="table-card" style="border-left:4px solid #e74c3c">
          <div class="section-title">
            <div><h3>✋ Registros aguardando sua ciência</h3>
              <div class="text-small">Conversas do dia a dia que o gestor registrou. Confirme e responda se quiser.</div></div>
            <div class="soft-badge" style="background:#fde8e8;color:#e74c3c">${notasPendentes.length}</div>
          </div>
          <div class="stack" style="padding-top:8px">
            ${notasPendentes.map((n) => registroCard(n, false, false)).join("")}
          </div>
        </div>` : ""}

      ${pendentes.length ? `
        <div class="table-card" style="border-left:4px solid #f39c12">
          <div class="section-title">
            <div><h3>✋ Seu feedback está aguardando ciência</h3>
              <div class="text-small">Leia com calma. Você pode responder ao gestor e, se preferir, escrever separadamente para a diretoria.</div></div>
            <div class="soft-badge" style="background:#fef7e0;color:#b06000">${pendentes.length}</div>
          </div>
          <div class="stack" style="padding-top:8px">
            ${pendentes.map((x) => feedbackCard(x, podeDar)).join("")}
          </div>
        </div>` : ""}

      <div class="form-card" style="padding:14px 18px">
        <div style="display:flex;gap:8px;flex-wrap:wrap;align-items:center">
          <span style="font-size:12px;font-weight:700;color:var(--muted)">COMPETÊNCIA</span>
          <select style="min-width:130px" onchange="setFeedbackCompetence(this.value)">
            ${(state.feedback.competences || []).map((c) => `
              <option value="${escapeHtml(c)}" ${f.competence === c ? "selected" : ""}>${escapeHtml(c)}</option>`).join("")}
          </select>
          ${(state.feedback.kinds || []).map((k) => `
            <button type="button" onclick="setFeedbackKind('${k.id}')"
              ${chipEmEspera("feedbackKind") ? "disabled" : ""}
              style="border:1px solid ${f.kind === k.id ? "var(--accent)" : "var(--line)"};
                     background:${f.kind === k.id ? "var(--accent)" : "#fff"};
                     color:${f.kind === k.id ? "#fff" : "var(--text)"};
                     border-radius:14px;padding:4px 12px;font-size:12px;font-weight:600;
                     ${chipEstadoCss("feedbackKind", f.kind === k.id)}">
              ${chipTrocando("feedbackKind") === k.id
                ? `<span class="girando">↻</span> Carregando…`
                : `${k.icon} ${escapeHtml(k.label)}`}
            </button>`).join("")}
          ${podeDar ? `
            <input id="feedback-person-search" style="flex:1;min-width:180px" placeholder="🔍 Buscar por nome — Enter"
              value="${escapeHtml(f.person)}"
              oninput="state.feedbackFilters.person=this.value"
              onkeydown="if(event.key==='Enter'){event.preventDefault();applyFeedbackPersonSearch();}" />
            <button class="btn btn-secondary btn-sm" onclick="applyFeedbackPersonSearch()">Buscar</button>` : ""}
          ${podeDar ? `
            <button class="btn btn-primary btn-sm" onclick="novoRegistro('','','ORIENTACAO')">＋ Registro rápido</button>` : ""}
          ${state.feedback.canGiveManagerFeedback ? `
            <button class="btn btn-secondary btn-sm" onclick="novoFeedback('GERENTE','','')">🎯 Feedback de gerente</button>` : ""}
        </div>
      </div>

      ${podeDar && faltando.length && (!f.kind || f.kind === "VENDEDOR") ? `
        <div class="table-card">
          <div class="section-title">
            <div><h3>Ainda sem feedback em ${escapeHtml(f.competence || "—")}</h3>
              <div class="text-small">O MEC prevê acompanhamento mensal. Clique no nome para começar.</div></div>
            <div class="soft-badge">${faltando.length}</div>
          </div>
          <div style="display:flex;gap:6px;flex-wrap:wrap;padding-top:8px">
            ${faltando.map((p) => `
              <button class="btn btn-ghost btn-sm" onclick="novoFeedback('VENDEDOR','${jsAttr(p.personName)}','${jsAttr(p.unitName || "")}')">
                ＋ ${escapeHtml(p.personName)}
              </button>`).join("")}
          </div>
        </div>` : ""}

      ${notasDemais.length ? `
        <div class="table-card">
          <div class="section-title">
            <div><h3>📌 Registros de ${escapeHtml(f.competence || "—")}</h3>
              <div class="text-small">A linha do tempo do mês. Vira memória na hora do feedback mensal.</div></div>
            <div class="soft-badge">${notasDemais.length}</div>
          </div>
          <div class="stack" style="padding-top:8px">
            ${notasDemais.map((n) => registroCard(n, podeDar && !n.isMe, false)).join("")}
          </div>
        </div>` : ""}

      ${meus.length ? `
        <div class="table-card">
          <div class="section-title"><div><h3>Meus feedbacks</h3></div></div>
          <div class="stack" style="padding-top:8px">${meus.map((x) => feedbackCard(x, podeDar)).join("")}</div>
        </div>` : ""}

      ${podeDar ? `
        <div class="table-card">
          <div class="section-title">
            <div><h3>Feedbacks registrados</h3>
              <div class="text-small">${daEquipe.length} no filtro atual</div></div>
          </div>
          <div class="stack" style="padding-top:8px">
            ${state.ui.loading.feedback ? '<div class="loader">Buscando…</div>' : ""}
            ${daEquipe.map((x) => feedbackCard(x, podeDar)).join("")
              || emptyStateCard("Nenhum feedback registrado nesta competência.")}
          </div>
        </div>` : (meus.length || pendentes.length ? "" :
          emptyStateCard("Você ainda não recebeu nenhum feedback registrado."))}
    </div>`;
}

function feedbackCard(x, podeDar) {
  const pendente = x.isMe && x.status === "PUBLICADO" && !x.acknowledgedAt;
  const evoluir = x.ratingSummary?.EVOLUIR || 0;
  const supera = x.ratingSummary?.SUPERA || 0;
  return `
    <div class="crm-card clean" style="padding:14px;${pendente ? "border-left:4px solid #f39c12" : ""}">
      <div style="display:flex;justify-content:space-between;align-items:start;gap:10px;flex-wrap:wrap">
        <div style="flex:1;min-width:220px">
          <div style="display:flex;gap:6px;align-items:center;flex-wrap:wrap;margin-bottom:4px">
            <span class="status-tag" style="background:#e8f0fe;color:#1a5276">
              ${x.kind === "GERENTE" ? "🎯 Gerente" : "👤 Vendedor"}</span>
            ${x.status === "RASCUNHO" ? '<span class="status-tag warn">Rascunho</span>' : ""}
            ${pendente ? '<span class="status-tag bad">Sua ciência pendente</span>' : ""}
            ${x.isMe && x.acknowledgedAt ? '<span class="status-tag good">✓ Você deu ciência</span>' : ""}
            ${!x.isMe && x.status === "PUBLICADO" ? (x.acknowledgedAt
              ? '<span class="status-tag good">✓ Ciente</span>'
              : '<span class="status-tag warn">Aguardando ciência</span>') : ""}
          </div>
          <div style="font-weight:700;font-size:14px">${escapeHtml(x.personName)}</div>
          <div class="text-small">
            ${escapeHtml(x.competence)}${x.unitName ? ` · ${escapeHtml(x.unitName)}` : ""} · por ${escapeHtml(x.authorName)}
          </div>
        </div>
        <div style="text-align:right;font-size:12px">
          ${supera ? `<div style="color:var(--good);font-weight:700">▲ ${supera} supera</div>` : ""}
          ${evoluir ? `<div style="color:var(--bad);font-weight:700">▼ ${evoluir} a evoluir</div>` : ""}
          ${x.hasNote && podeDar ? '<div style="color:var(--accent);font-weight:600">💬 respondeu</div>' : ""}
          ${x.hasConfidentialNote && state.feedback?.canReadConfidential
            ? '<div style="color:#b06000;font-weight:600">🔒 confidencial</div>' : ""}
        </div>
      </div>
      <div class="actions" style="gap:6px;margin-top:10px;padding-top:8px;border-top:1px solid var(--line)">
        <button class="btn ${pendente ? "btn-primary" : "btn-secondary"} btn-sm" onclick="abrirFeedback(${x.id})">
          ${pendente ? "✋ Ler e dar ciência" : "Abrir"}
        </button>
        ${podeDar && !x.isMe ? `
          <button class="btn btn-ghost btn-sm" onclick="novoRegistro('${jsAttr(x.personName)}','${jsAttr(x.unitName || "")}','ORIENTACAO')">＋ Registro</button>
          <button class="btn btn-ghost btn-sm" onclick="editarFeedback(${x.id})">Editar</button>
          <button class="btn btn-ghost btn-sm" onclick="excluirFeedback(${x.id})">Excluir</button>` : ""}
      </div>
    </div>`;
}

function feedbackEditorModal() {
  const e = state.feedbackEditor;
  const pessoas = (state.feedback?.people || []);
  const avaliados = Object.keys(e.ratings || {}).length;
  const total = (e.items || []).length;
  const abas = [
    { id: "conversa", label: "Conversa" },
    { id: "avaliacao", label: `Avaliação (${avaliados}/${total})` },
    { id: "registros", label: `Registros do mês (${(e.notes || []).length})` },
    { id: "pdi", label: `PDI (${(e.pdi || []).filter((i) => ["ABERTO","EVOLUINDO"].includes(i.status)).length})` },
    { id: "guia", label: "Guia do gestor" },
  ];

  return `
    <div class="client-drawer-overlay open modal-dim" onclick="fecharFeedbackEditor()">
      <div class="panel modal-panel" data-keep-scroll="feedback-editor"
           style="max-width:1000px;margin:3vh auto;padding:22px;max-height:92vh;overflow:auto"
           onclick="event.stopPropagation()">
        <div class="section-title">
          <div>
            <h3>${e.id ? "Editar" : "Novo"} feedback ${e.kind === "GERENTE" ? "de gerente" : "de vendedor"}</h3>
            <div class="text-small">${e.status === "PUBLICADO"
              ? "Publicado — a pessoa já pode ler."
              : "Rascunho. A pessoa só é notificada quando você publicar."}</div>
          </div>
          <button class="btn btn-ghost btn-sm" onclick="fecharFeedbackEditor()">Fechar</button>
        </div>

        <div style="display:grid;grid-template-columns:2fr 1fr 1fr;gap:12px;margin-top:12px">
          <div class="field"><label>${e.kind === "GERENTE" ? "Gerente" : "Vendedor"} <span style="color:var(--bad)">*</span></label>
            ${e.id ? `<input value="${escapeHtml(e.personName)}" disabled />`
              : `<select onchange="state.feedbackEditor.personName=this.value;
                    state.feedbackEditor.unitName=(this.selectedOptions[0]||{}).dataset?.unit||'';
                    carregarPreviaFeedback()">
                  <option value="">Selecione…</option>
                  ${pessoas.map((p) => `<option value="${escapeHtml(p.personName)}" data-unit="${escapeHtml(p.unitName || "")}"
                    ${e.personName === p.personName ? "selected" : ""}>${escapeHtml(p.personName)}${p.unitName ? ` · ${escapeHtml(p.unitName)}` : ""}</option>`).join("")}
                </select>`}
          </div>
          <div class="field"><label>Competência</label>
            <select onchange="state.feedbackEditor.competence=this.value;carregarPreviaFeedback()">
              ${(state.feedback?.competences || []).map((c) => `
                <option value="${escapeHtml(c)}" ${e.competence === c ? "selected" : ""}>${escapeHtml(c)}</option>`).join("")}
            </select>
          </div>
          <div class="field"><label>Unidade</label>
            <select onchange="state.feedbackEditor.unitName=this.value;carregarPreviaFeedback()">
              ${(state.feedback?.units || []).map((u) => `
                <option value="${escapeHtml(u)}" ${e.unitName === u ? "selected" : ""}>${escapeHtml(u)}</option>`).join("")}
            </select>
          </div>
        </div>

        <div class="subtle-card padded-card" style="margin-top:4px">
          <div class="section-title"><div><h3>📊 Os números de ${escapeHtml(e.competence || "")}</h3>
            <div class="text-small">Ficam gravados junto com o feedback — a conversa continua fazendo sentido daqui a seis meses.</div></div></div>
          ${e.loading ? '<div class="loader">Buscando indicadores…</div>' : painelIndicadores(e.indicators, e.kind)}
        </div>

        <div style="display:flex;gap:6px;flex-wrap:wrap;margin-top:14px;border-bottom:1px solid var(--line);padding-bottom:8px">
          ${abas.map((a) => `
            <button type="button" onclick="setFeedbackTab('${a.id}')"
              style="border:none;background:${e.tab === a.id ? "var(--accent)" : "transparent"};
                     color:${e.tab === a.id ? "#fff" : "var(--text)"};border-radius:8px;
                     padding:6px 14px;font-size:13px;font-weight:600;cursor:pointer">
              ${escapeHtml(a.label)}
            </button>`).join("")}
        </div>

        ${e.tab === "conversa" ? `
          ${e.kind === "GERENTE" ? `
            <div class="text-small" style="color:var(--muted);margin-top:10px">
              Estrutura GROW: objetivo, realidade, caminhos e compromisso. Deixe o gerente propor antes de você dar a solução.
            </div>
            <div class="field"><label>Objetivo — onde a unidade precisa chegar</label>
              <textarea rows="2" style="font-family:inherit" oninput="state.feedbackEditor.tacticalGoal=this.value"
                placeholder="O destino do próximo trimestre e por quê">${escapeHtml(e.tacticalGoal)}</textarea></div>
            <div class="field"><label>Realidade — onde estamos hoje</label>
              <textarea rows="3" style="font-family:inherit" oninput="state.feedbackEditor.tacticalReality=this.value"
                placeholder="Leitura dos números sem filtro. Peça a versão dele primeiro.">${escapeHtml(e.tacticalReality)}</textarea></div>
            <div class="field"><label>Caminhos — o que pode ser feito</label>
              <textarea rows="3" style="font-family:inherit" oninput="state.feedbackEditor.tacticalOptions=this.value"
                placeholder="Opções levantadas na conversa">${escapeHtml(e.tacticalOptions)}</textarea></div>
            <div class="field"><label>Compromisso e apoio necessário</label>
              <textarea rows="3" style="font-family:inherit" oninput="state.feedbackEditor.tacticalWill=this.value"
                placeholder="O que ele vai fazer, até quando, e o que precisa da diretoria">${escapeHtml(e.tacticalWill)}</textarea></div>
          ` : ""}
          <div class="field"><label>O que foi bem</label>
            <textarea rows="3" style="font-family:inherit" oninput="state.feedbackEditor.highlights=this.value"
              placeholder="Cite fato e número. Elogio sem dado não é levado a sério.">${escapeHtml(e.highlights)}</textarea></div>
          <div class="field"><label>O que precisa evoluir</label>
            <textarea rows="3" style="font-family:inherit" oninput="state.feedbackEditor.improvements=this.value"
              placeholder="Situação, comportamento e efeito. Descreva o que aconteceu, não como a pessoa é.">${escapeHtml(e.improvements)}</textarea></div>
          <div class="field"><label>O que ficou combinado <span style="color:var(--bad)">*</span></label>
            <textarea rows="3" style="font-family:inherit" oninput="state.feedbackEditor.agreements=this.value"
              placeholder="É o que a pessoa leva da conversa. Sem isso, o feedback vira desabafo.">${escapeHtml(e.agreements)}</textarea></div>
        ` : ""}

        ${e.tab === "avaliacao" ? `
          <div class="text-small" style="color:var(--muted);margin-top:10px">
            ${(state.feedback?.levels || []).map((n) => `<strong style="color:${n.color}">${n.icon} ${escapeHtml(n.label)}</strong>: ${escapeHtml(n.hint)}`).join(" &nbsp;·&nbsp; ")}
          </div>
          ${(e.groups || []).map((grupo) => `
            <div style="margin-top:14px">
              <div class="eyebrow">${escapeHtml(grupo)}</div>
              ${(e.items || []).filter((i) => i.group === grupo).map((item) => {
                const atual = e.ratings[item.id]?.level || "";
                return `
                  <div style="padding:8px 0;border-bottom:1px solid var(--line)">
                    <div style="display:flex;justify-content:space-between;gap:10px;flex-wrap:wrap;align-items:start">
                      <div style="flex:1;min-width:240px">
                        <div style="font-weight:700;font-size:13px">${escapeHtml(item.label)}</div>
                        <div class="text-small" style="color:var(--muted)">${escapeHtml(item.hint)}</div>
                        <div class="text-small" style="color:var(--accent);margin-top:2px">Onde conferir: ${escapeHtml(item.evidence)}</div>
                      </div>
                      <div style="display:flex;gap:4px">
                        ${(state.feedback?.levels || []).map((n) => `
                          <button type="button" onclick="marcarNivel('${item.id}','${n.id}')"
                            title="${escapeHtml(n.hint)}"
                            style="border:1px solid ${atual === n.id ? n.color : "var(--line)"};
                                   background:${atual === n.id ? n.bg : "#fff"};
                                   color:${atual === n.id ? n.color : "var(--muted)"};
                                   border-radius:12px;padding:4px 10px;font-size:12px;
                                   font-weight:${atual === n.id ? "700" : "500"};cursor:pointer;white-space:nowrap">
                            ${n.icon} ${escapeHtml(n.label)}
                          </button>`).join("")}
                      </div>
                    </div>
                    ${atual ? `
                      <input style="margin-top:6px;font-size:12px" placeholder="Exemplo concreto (opcional, mas é o que dá peso)"
                        value="${escapeHtml(e.ratings[item.id]?.comment || "")}"
                        oninput="state.feedbackEditor.ratings['${item.id}'].comment=this.value" />` : ""}
                  </div>`;
              }).join("")}
            </div>`).join("")}
        ` : ""}

        ${e.tab === "registros" ? `
          <div class="text-small" style="color:var(--muted);margin-top:10px">
            O que você registrou sobre ${escapeHtml(e.personName || "esta pessoa")} durante ${escapeHtml(e.competence || "o mês")}.
            Use como base para escrever a conversa — assim o feedback cobre o mês inteiro, não só a última semana.
          </div>
          <div class="actions" style="margin-top:8px">
            <button class="btn btn-secondary btn-sm"
              onclick="novoRegistro('${jsAttr(e.personName)}','${jsAttr(e.unitName || "")}','ORIENTACAO')">＋ Novo registro</button>
          </div>
          <div class="stack" style="margin-top:8px">
            ${(e.notes || []).map((n) => registroCard(n, true, true)).join("")
              || '<div class="text-small" style="color:var(--muted)">Nenhum registro neste mês. Os fatos do dia a dia se perdem quando não são anotados na hora.</div>'}
          </div>` : ""}

        ${e.tab === "pdi" ? painelPdi(e.pdi, e.personName, e.unitName, e.id, true) : ""}

        ${e.tab === "guia" ? `
          ${e.guidance?.length ? `
            <div style="margin-top:12px"><div class="eyebrow">O QUE OS NÚMEROS ESTÃO DIZENDO</div>
              ${painelGuia(e.guidance)}</div>` : ""}
          <div style="margin-top:14px"><div class="eyebrow">ROTEIRO DA CONVERSA</div>
            ${painelRoteiro(e.script)}</div>
        ` : ""}

        <div class="actions" style="margin-top:16px">
          <button class="btn btn-secondary" ${e.saving ? "disabled" : ""} onclick="salvarFeedback(false)">
            ${e.saving ? "Salvando…" : "Salvar rascunho"}
          </button>
          <button class="btn btn-primary" ${e.saving ? "disabled" : ""} onclick="salvarFeedback(true)">
            ${e.status === "PUBLICADO" ? "Salvar alterações" : "Publicar para a pessoa"}
          </button>
          <button class="btn btn-ghost" onclick="fecharFeedbackEditor()">Cancelar</button>
        </div>
      </div>
    </div>`;
}

function feedbackDetalheModal() {
  const d = state.feedbackDetail;
  const podeDar = Boolean(state.feedback?.canGive);
  const jaCiente = Boolean(d.acknowledgedAt);
  const bloco = (titulo, texto) => texto ? `
    <div style="margin-top:12px">
      <div class="eyebrow">${titulo}</div>
      <div style="white-space:pre-wrap;line-height:1.6;font-size:13px">${escapeHtml(texto)}</div>
    </div>` : "";

  return `
    <div class="client-drawer-overlay open modal-dim" onclick="fecharFeedbackDetalhe()">
      <div class="panel modal-panel" data-keep-scroll="feedback-detalhe"
           style="max-width:900px;margin:3vh auto;padding:22px;max-height:92vh;overflow:auto"
           onclick="event.stopPropagation()">
        <div class="section-title">
          <div>
            <h3>${escapeHtml(d.personName)}</h3>
            <div class="text-small">${escapeHtml(d.kindLabel)} · ${escapeHtml(d.competence)}
              ${d.unitName ? ` · ${escapeHtml(d.unitName)}` : ""} · por ${escapeHtml(d.authorName)}</div>
          </div>
          <button class="btn btn-ghost btn-sm" onclick="fecharFeedbackDetalhe()">Fechar</button>
        </div>

        <div class="subtle-card padded-card" style="margin-top:12px">
          <div class="section-title"><div><h3>📊 Números de ${escapeHtml(d.competence)}</h3></div></div>
          ${painelIndicadores(d.indicators, d.kind)}
        </div>

        ${bloco("OBJETIVO", d.tacticalGoal)}
        ${bloco("REALIDADE", d.tacticalReality)}
        ${bloco("CAMINHOS", d.tacticalOptions)}
        ${bloco("COMPROMISSO E APOIO", d.tacticalWill)}
        ${bloco("O QUE FOI BEM", d.highlights)}
        ${bloco("O QUE PRECISA EVOLUIR", d.improvements)}
        ${bloco("O QUE FICOU COMBINADO", d.agreements)}

        <div class="subtle-card padded-card" style="margin-top:12px">
          <div class="section-title"><div><h3>Avaliação</h3></div></div>
          ${(d.groups || []).map((grupo) => `
            <div style="margin-top:8px">
              <div class="eyebrow">${escapeHtml(grupo)}</div>
              ${(d.items || []).filter((i) => i.group === grupo).map((item) => {
                const r = d.ratings?.[item.id];
                if (!r) return "";
                return `
                  <div style="display:flex;justify-content:space-between;gap:8px;flex-wrap:wrap;
                              padding:6px 0;border-bottom:1px solid var(--line);font-size:13px">
                    <div style="flex:1;min-width:220px">
                      ${escapeHtml(item.label)}
                      ${r.comment ? `<div class="text-small" style="color:var(--muted)">${escapeHtml(r.comment)}</div>` : ""}
                    </div>
                    ${nivelBadge(r.level)}
                  </div>`;
              }).join("")}
            </div>`).join("")}
        </div>

        ${(d.notes || []).length ? `
          <div class="subtle-card padded-card" style="margin-top:10px">
            <div class="section-title"><div><h3>📌 Registros de ${escapeHtml(d.competence)}</h3>
              <div class="text-small">As conversas do dia a dia que originaram este feedback.</div></div></div>
            <div class="stack" style="margin-top:8px">
              ${d.notes.map((n) => registroCard(n, false, true)).join("")}
            </div>
          </div>` : ""}

        ${painelPdi(d.pdi, d.personName, d.unitName, d.id, podeDar && !d.isMe)}

        ${d.personNote ? `
          <div class="subtle-card padded-card" style="margin-top:10px">
            <div class="section-title"><div><h3>💬 Resposta de ${escapeHtml(d.personName)}</h3></div></div>
            <div style="white-space:pre-wrap;font-size:13px;line-height:1.5;margin-top:6px">${escapeHtml(d.personNote)}</div>
          </div>` : ""}

        ${d.canReadConfidential && d.confidentialNote ? `
          <div class="subtle-card padded-card" style="margin-top:10px;border:1px solid #b06000">
            <div class="section-title"><div><h3>🔒 Observação confidencial</h3>
              <div class="text-small">Enviada apenas para a diretoria. O gestor que conduziu não tem acesso.</div></div></div>
            <div style="white-space:pre-wrap;font-size:13px;line-height:1.5;margin-top:6px">${escapeHtml(d.confidentialNote)}</div>
          </div>` : ""}
        ${!d.canReadConfidential && d.hasConfidentialNote ? `
          <div class="message" style="margin-top:10px;font-size:12px">
            🔒 ${escapeHtml(d.personName)} deixou uma observação endereçada à diretoria.
          </div>` : ""}

        ${d.isMe && !jaCiente && d.status === "PUBLICADO" ? `
          <div class="subtle-card padded-card" style="margin-top:14px;border:1px solid var(--accent)">
            <div class="section-title"><div><h3>✋ Confirmar ciência</h3>
              <div class="text-small">Você escolhe para quem vai cada observação. Nenhuma das duas é obrigatória.</div></div></div>
            <div class="field" style="margin-top:8px">
              <label>Observação para ${escapeHtml(d.authorName)}</label>
              <textarea id="feedback-note" rows="3" style="font-family:inherit"
                placeholder="O que você concorda, discorda ou precisa de apoio"></textarea>
              <div class="text-small" style="color:var(--muted)">Vai para quem conduziu o feedback.</div>
            </div>
            <div class="field">
              <label>🔒 Observação para a diretoria</label>
              <textarea id="feedback-confidential" rows="3" style="font-family:inherit"
                placeholder="Algo que você prefere tratar fora da linha direta"></textarea>
              <div class="text-small" style="color:#b06000">
                Não é lida por ${escapeHtml(d.authorName)}. Só a diretoria tem acesso.
              </div>
            </div>
            <div class="actions">
              <button class="btn btn-primary" ${d.saving ? "disabled" : ""} onclick="darCienciaFeedback()">
                ${d.saving ? "Registrando…" : "Estou ciente"}
              </button>
            </div>
          </div>` : ""}

        ${d.isMe && jaCiente ? `
          <div class="message success" style="margin-top:14px">✓ Você deu ciência neste feedback.</div>` : ""}
      </div>
    </div>`;
}

function pdiEditorModal() {
  const p = state.pdiEditor;
  return `
    <div class="client-drawer-overlay open modal-dim" onclick="fecharPdiEditor()" style="z-index:60">
      <div class="panel modal-panel" style="max-width:560px;margin:8vh auto;padding:22px" onclick="event.stopPropagation()">
        <div class="section-title">
          <div><h3>${p.id ? "Atualizar" : "Novo"} ponto de desenvolvimento</h3>
            <div class="text-small">${escapeHtml(p.personName)}</div></div>
          <button class="btn btn-ghost btn-sm" onclick="fecharPdiEditor()">Fechar</button>
        </div>
        <div class="field" style="margin-top:10px"><label>O que desenvolver <span style="color:var(--bad)">*</span></label>
          <input value="${escapeHtml(p.title)}" oninput="state.pdiEditor.title=this.value"
            placeholder="Ex.: retorno de orçamento no mesmo dia" /></div>
        <div class="field"><label>Por que importa</label>
          <input value="${escapeHtml(p.why)}" oninput="state.pdiEditor.why=this.value"
            placeholder="O efeito que isso tem no resultado dele" /></div>
        <div class="field"><label>Como, na prática</label>
          <textarea rows="2" style="font-family:inherit" oninput="state.pdiEditor.action=this.value"
            placeholder="A ação concreta, não a intenção">${escapeHtml(p.action)}</textarea></div>
        <div style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:10px">
          <div class="field"><label>Quem apoia</label>
            <input value="${escapeHtml(p.support)}" oninput="state.pdiEditor.support=this.value" /></div>
          <div class="field"><label>Até quando</label>
            <input type="date" value="${escapeHtml(p.dueDate || "")}" oninput="state.pdiEditor.dueDate=this.value" /></div>
          <div class="field"><label>Situação</label>
            <select onchange="state.pdiEditor.status=this.value">
              ${(state.feedback?.pdiStatuses || []).map((s) => `
                <option value="${s.id}" ${p.status === s.id ? "selected" : ""}>${escapeHtml(s.label)}</option>`).join("")}
            </select></div>
        </div>
        <div class="field"><label>Evolução</label>
          <textarea rows="2" style="font-family:inherit" oninput="state.pdiEditor.progressNote=this.value"
            placeholder="O que mudou desde a última conversa">${escapeHtml(p.progressNote || "")}</textarea></div>
        <div class="actions" style="margin-top:12px">
          <button class="btn btn-primary" ${p.saving ? "disabled" : ""} onclick="salvarPdi()">
            ${p.saving ? "Salvando…" : "Salvar"}</button>
          <button class="btn btn-ghost" onclick="fecharPdiEditor()">Cancelar</button>
        </div>
      </div>
    </div>`;
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
          <label>Limite de crédito</label>
          <select onchange="updateCrmClientFilter('creditLimit', this.value)">
            <option value="">Todos</option>
            <option value="COM_LIMITE" ${filters.creditLimit === "COM_LIMITE" ? "selected" : ""}>Com limite cadastrado</option>
            <option value="SEM_LIMITE" ${filters.creditLimit === "SEM_LIMITE" ? "selected" : ""}>Sem limite</option>
            <option value="LIMITE_ESTOURADO" ${filters.creditLimit === "LIMITE_ESTOURADO" ? "selected" : ""}>Passou do limite no mês</option>
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

/** Valor curto em milhares: 11882 -> "11,9k". Mantém a linha do card enxuta. */
/**
 * Data e hora LOCAIS no formato aceito pelo input datetime-local.
 * Nunca usar toISOString(): ela converte para UTC e, no Brasil (UTC-3),
 * qualquer registro após as 21h cai no dia seguinte.
 */
function localDateTimeInput() {
  const d = new Date();
  const p = (n) => String(n).padStart(2, "0");
  return `${d.getFullYear()}-${p(d.getMonth() + 1)}-${p(d.getDate())}T${p(d.getHours())}:${p(d.getMinutes())}`;
}

/** Mesma data e hora locais, no formato que o servidor grava. */
function localDateTimeString() {
  return localDateTimeInput().replace("T", " ") + ":00";
}

function shortMoney(value) {
  const n = Number(value || 0);
  if (n === 0) return "0";
  if (Math.abs(n) < 1000) return String(Math.round(n));
  const k = n / 1000;
  return (Math.abs(k) >= 100 ? Math.round(k) : k.toFixed(1).replace(".", ",")) + "k";
}

/**
 * Trajetória de faturamento em UMA linha: 3 meses anteriores + mês atual.
 * O vendedor lê a tendência pela sequência dos números, sem precisar abrir nada.
 * Card cresce uma linha, não quatro — com 50+ clientes na fila isso importa.
 */
function revenueTrendLine(item) {
  const meses = item.averageBasis?.months;
  if (!meses || !meses.length) return "";
  const ordenados = [...meses].sort((a, b) => String(a.competence).localeCompare(String(b.competence)));
  const atual = { competence: item.averageBasis.currentCompetence, revenue: Number(item.currentRevenue || 0) };
  const serie = [...ordenados, atual];

  const g = Number(item.growthPct || 0);
  const tend = g > 0.03
    ? { icon: "▲", cor: "#1e8e3e", txt: `+${Math.round(g * 100)}%` }
    : g < -0.03
      ? { icon: "▼", cor: "#c5221f", txt: `${Math.round(g * 100)}%` }
      : { icon: "=", cor: "#5f6368", txt: "estável" };

  return `
    <div style="display:flex;align-items:center;gap:6px;flex-wrap:wrap;font-size:11px;margin-bottom:8px;
                background:#f7fafc;border-radius:6px;padding:5px 8px"
         title="Faturamento dos 3 meses anteriores e do mês atual">
      ${serie.map((m, i) => {
        const ultimo = i === serie.length - 1;
        const zerado = Number(m.revenue || 0) <= 0;
        return `${i > 0 ? '<span style="color:var(--line)">→</span>' : ""}
          <span style="white-space:nowrap;${ultimo ? "font-weight:800" : ""};${zerado && ultimo ? "color:#c5221f" : "color:var(--muted)"}">
            ${escapeHtml(competenceShort(m.competence))} <strong style="color:${zerado ? (ultimo ? "#c5221f" : "var(--muted)") : "var(--text)"}">${shortMoney(m.revenue)}</strong>
          </span>`;
      }).join("")}
      <span style="margin-left:auto;color:${tend.cor};font-weight:800;white-space:nowrap">${tend.icon} ${tend.txt}</span>
    </div>`;
}

// ─── Filtros rápidos da carteira do vendedor ────────────────────────────────

/**
 * Chips de um toque. Reaproveitam os filtros que já existem no backend
 * (status, com/sem compra, classe, PJ/PF) — nada de regra nova.
 * A ordem dos blocos da carteira NÃO muda: os chips só reduzem o conjunto.
 */
const SELLER_FILTER_CHIPS = [
  { group: "purchaseMonth", value: "SEM_COMPRA", label: "Sem compra no mês", icon: "○" },
  { group: "status",     value: "INATIVO",     label: "Inativos",     icon: "🔴" },
  { group: "status",     value: "PRE_INATIVO", label: "Pré-inativos", icon: "🟡" },
  { group: "status",     value: "ATIVO",       label: "Ativos",       icon: "🟢" },
  { group: "classCode",  value: "DIAMANTE",    label: "Diamante",     icon: "💎" },
  { group: "classCode",  value: "OURO",        label: "Ouro",         icon: "🥇" },
  { group: "classCode",  value: "PRATA",       label: "Prata",        icon: "🥈" },
  { group: "classCode",  value: "BRONZE",      label: "Bronze",       icon: "🥉" },
  { group: "creditLimit", value: "COM_LIMITE",       label: "Com limite",       icon: "💳" },
  { group: "creditLimit", value: "LIMITE_ESTOURADO", label: "Passou do limite", icon: "⚠" },
  { group: "personType", value: "PJ",          label: "PJ",           icon: "🏢" },
  { group: "personType", value: "PF",          label: "PF",           icon: "👤" },
];

function toggleSellerChip(group, value) {
  const f = state.crm.crmClientFilters;
  const novo = f[group] === value ? "" : value;   // clicar de novo desliga
  f[group] = novo;
  trocarChip("sellerChips", `${group}:${novo}`, () => runCrmClientSearch());
}

function activeSellerFilterCount() {
  const f = state.crm.crmClientFilters || {};
  return ["purchaseMonth", "status", "classCode", "personType", "itemCode", "creditLimit"]
    .filter((k) => f[k]).length;
}

function clearSellerFilters() {
  const f = state.crm.crmClientFilters;
  ["purchaseMonth", "status", "classCode", "personType", "itemCode", "search"].forEach((k) => { f[k] = ""; });
  runCrmClientSearch();
}

function sellerFilterBar() {
  const f = state.crm.crmClientFilters || {};
  const ativos = activeSellerFilterCount();
  return `
    <div class="form-card" style="padding:12px 18px">
      <div style="display:flex;align-items:center;gap:8px;flex-wrap:wrap;margin-bottom:10px">
        <input style="flex:1;min-width:200px" placeholder="Buscar por nome, código ou cidade"
          value="${escapeHtml(f.search || "")}"
          oninput="state.crm.crmClientFilters.search=this.value"
          onkeydown="if(event.key==='Enter'){runCrmClientSearch();}" />
        <input style="flex:1;min-width:170px" placeholder="🔧 Comprou o item (código)"
          title="Digite o código do fabricante ou o interno para ver quem comprou essa peça"
          value="${escapeHtml(f.itemCode || "")}"
          oninput="state.crm.crmClientFilters.itemCode=this.value"
          onkeydown="if(event.key==='Enter'){runCrmClientSearch();}" />
        <button class="btn btn-secondary btn-sm" onclick="runCrmClientSearch()">Buscar</button>
        ${ativos ? `<button class="btn btn-ghost btn-sm" onclick="clearSellerFilters()">Limpar (${ativos})</button>` : ""}
      </div>
      <div style="display:flex;gap:6px;flex-wrap:wrap">
        ${SELLER_FILTER_CHIPS.map((c) => {
          const on = f[c.group] === c.value;
          return `
            <button type="button" onclick="toggleSellerChip('${c.group}','${c.value}')"
              ${chipEmEspera("sellerChips") ? "disabled" : ""}
              style="border:1px solid ${on ? "var(--accent)" : "var(--line)"};
                     background:${on ? "var(--accent)" : "#fff"};
                     color:${on ? "#fff" : "var(--text)"};
                     border-radius:14px;padding:4px 12px;font-size:12px;font-weight:600;
                     white-space:nowrap;transition:all .15s;${chipEstadoCss("sellerChips", on)}">
              ${chipTrocando("sellerChips") === `${c.group}:${c.value}`
                ? `<span class="girando">↻</span> Carregando…`
                : `${c.icon} ${escapeHtml(c.label)}`}
            </button>`;
        }).join("")}
      </div>
      ${f.itemCode ? `
        <div class="text-small" style="color:var(--accent);margin-top:8px;font-weight:600">
          🔧 Mostrando apenas quem comprou "${escapeHtml(f.itemCode)}" nos últimos 12 meses.
        </div>` : ""}
    </div>`;
}

const MONTH_ABBR = ["jan", "fev", "mar", "abr", "mai", "jun", "jul", "ago", "set", "out", "nov", "dez"];

/** "2026-07-12" ou "2026-07" → "12/07/26" / "jul/26". Aguenta data vazia. */
function shortDate(valor) {
  const texto = String(valor || "").slice(0, 10);
  const partes = texto.split("-");
  if (partes.length >= 3) return `${partes[2]}/${partes[1]}/${partes[0].slice(2)}`;
  if (partes.length === 2) return `${MONTH_ABBR[Number(partes[1]) - 1] || partes[1]}/${partes[0].slice(2)}`;
  return texto || "-";
}

/** Quantidade sem casas decimais quando é inteira — "4 un" e não "4,00 un". */
function qtyLabel(valor) {
  const n = Number(valor || 0);
  const texto = Number.isInteger(n) ? String(n) : n.toLocaleString("pt-BR", { maximumFractionDigits: 2 });
  return `${texto} un`;
}

/**
 * Faixa com o histórico do item pesquisado — só aparece quando há filtro de peça.
 * Uma linha com a última compra (quando/quanto/por quanto) e, se houve mais de
 * uma, uma segunda linha discreta com o acumulado dos 12 meses.
 */
function itemPurchaseLine(item) {
  const c = item.itemPurchase;
  if (!c) return "";
  const preco = c.lastUnitPrice != null ? `${currency(c.lastUnitPrice)}/un` : "preço n/d";
  const repetiu = Number(c.purchaseCount || 0) > 1;
  return `
    <div style="border-left:3px solid var(--accent);background:#f5f9ff;border-radius:0 6px 6px 0;
                padding:6px 10px;margin-bottom:8px;font-size:12px">
      <div style="display:flex;justify-content:space-between;gap:8px;flex-wrap:wrap">
        <span style="font-weight:700;color:var(--accent)">🔧 ${escapeHtml(c.itemCode || "Item")}</span>
        <span style="font-weight:600">${shortDate(c.lastPurchaseAt)} · ${qtyLabel(c.lastQuantity)} · ${preco}</span>
      </div>
      ${repetiu ? `
        <div style="color:var(--muted);margin-top:2px">
          ${number(c.purchaseCount)} compras em 12m · ${qtyLabel(c.totalQuantity)} · ${currency(c.totalValue)}
          ${c.avgUnitPrice != null ? ` · média ${currency(c.avgUnitPrice)}/un` : ""}
        </div>` : ""}
    </div>`;
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
      ${revenueTrendLine(item)}
      ${itemPurchaseLine(item)}
      <div style="display:flex;gap:8px;font-size:12px;color:var(--muted);margin-bottom:10px">
        <span>📞 ${escapeHtml(item.phone || "Sem tel.")}</span>
        <span style="color:${hasPurchase ? "var(--good)" : "#e67e22"}">${hasPurchase ? "✅ Comprou" : "○ Sem compra"}</span>
      </div>
      ${Number(item.creditLimit || 0) > 0 ? `
        <div class="text-small" style="display:flex;justify-content:space-between;gap:8px;
             background:#f5f7f9;border-radius:6px;padding:5px 8px;margin:6px 0">
          <span style="color:var(--muted)">💳 Limite ${currency(item.creditLimit)}</span>
          <span style="font-weight:700;color:${Number(item.predictedBalance) < 0 ? "var(--bad)" : "var(--good)"}"
            title="Limite menos as compras do mês. Não considera parcelas de meses anteriores em aberto.">
            saldo previsto ${currency(item.predictedBalance)}
          </span>
        </div>` : ""}
      <div class="actions" style="gap:6px">
        <!-- Só Ficha. Registrar e Atualizar saíram do card de propósito: o
             registro tem de ser feito COM a ficha aberta, olhando histórico,
             última compra e o que oferecer. Registrar direto da lista convida
             ao "falei com o cliente" sem contexto nenhum. -->
        <button class="btn btn-primary btn-sm" onclick="openCrmClient('${escapeHtml(item.clientKey)}', false)">Abrir ficha</button>
      </div>
    </div>
  `;
}

/** Sinais de relacionamento na lista da carteira.
 *
 * Quatro marcas curtas em vez de quatro colunas: a carteira já tem doze e mais
 * colunas tornariam a leitura impossível. Cada marca tem title, então o
 * ponteiro conta a data sem ocupar espaço.
 */
function engagementMarks(e) {
  if (!e) return '<span class="text-small" style="color:var(--muted)">—</span>';
  const marca = (icone, cor, titulo) =>
    `<span title="${escapeHtml(titulo)}" style="font-size:13px;color:${cor};margin-right:4px">${icone}</span>`;
  const partes = [];
  if (e.neverContacted) {
    partes.push(marca("○", "var(--bad)", "Nunca contatado — nenhum registro na ficha"));
  } else if (e.activeRecent) {
    partes.push(marca("●", "var(--good)",
      `Contato ativo em ${shortDate(e.lastActiveContactAt) || "período recente"}`));
  } else if (e.lastActiveContactAt) {
    partes.push(marca("●", "#c9ced3",
      `Último contato ativo em ${shortDate(e.lastActiveContactAt)} — fora dos 30 dias`));
  }
  if (e.lastVisitAt) {
    partes.push(marca("◆", "var(--accent)", `Visita em ${shortDate(e.lastVisitAt)}`));
  }
  if (e.pendingFollowupAt) {
    partes.push(marca("↩", "#e0a800", `Retorno pendente para ${shortDate(e.pendingFollowupAt)}`));
  }
  return partes.join("") || '<span class="text-small" style="color:var(--muted)">—</span>';
}

// ─── Atendimento de apoio (cliente de outra carteira) ──────────────────────
//
// Só por CÓDIGO exato, e sem valores na ficha. As duas restrições são de
// propósito: por nome, o vendedor varreria a carteira do colega; com
// faturamento, veria o resultado dele. Aqui vai o que serve para ATENDER.

function abrirApoio(codigoSugerido) {
  state.crm.support = { code: codigoSugerido || "", client: null, searching: false,
                        notes: "", typeCode: "LIGACAO", saving: false, notFound: false };
  requestRender();
}

function fecharApoio() {
  state.crm.support = null;
  requestRender();
}

async function buscarClienteApoio() {
  const a = state.crm.support;
  if (!a) return;
  const codigo = (a.code || "").trim();
  if (!codigo) { addMessage("warn", "Informe o código do cliente."); return; }
  a.searching = true; a.client = null; a.notFound = false; requestRender();
  try {
    const r = await api(`/api/crm/client/support?code=${encodeURIComponent(codigo)}`);
    if (state.crm.support) state.crm.support.client = r.client || null;
  } catch (error) {
    if (state.crm.support) state.crm.support.notFound = true;
  } finally {
    if (state.crm.support) state.crm.support.searching = false;
    requestRender();
  }
}

/** Abre a ficha COMPLETA de um cliente fora da carteira (histórico e vendas). */
async function abrirFichaApoio(codigo) {
  state.crm.support = null;
  await openCrmClient(codigo, true, true, { outside: true });
}

async function registrarApoio() {
  const a = state.crm.support;
  if (!a || !a.client || a.saving) return;
  if (!a.notes.trim()) { addMessage("error", "Escreva o que foi tratado."); return; }
  a.saving = true; requestRender();
  try {
    await api("/api/crm/interactions", {
      method: "POST",
      body: JSON.stringify({
        clientKey: a.client.client_code,
        clientName: a.client.client_name,
        contactTypeCode: a.typeCode,
        resultCode: "FALOU_CLIENTE",
        initiative: a.client.isOwnClient ? "ATIVO" : "APOIO",
        notes: a.notes.trim(),
      }),
    });
    addMessage("success", a.client.isOwnClient
      ? "Contato registrado na sua carteira."
      : "Atendimento registrado. O vendedor responsável recebeu uma tarefa para retomar o contato.");
    state.crm.support = null;
    state.contacts = null;
    await loadCrmData();
  } catch (error) {
    addMessage("error", error.message);
    if (state.crm.support) state.crm.support.saving = false;
  }
  requestRender();
}

function apoioModal() {
  const a = state.crm.support;
  if (!a) return "";
  const c = a.client;
  return `
    <div class="client-drawer-overlay open modal-dim" onclick="fecharApoio()">
      <div class="panel modal-panel" style="max-width:600px;margin:6vh auto;padding:22px" onclick="event.stopPropagation()">
        <div class="section-title">
          <div>
            <h3>🤝 Atender cliente de outra carteira</h3>
            <div class="text-small">Busque pelo código que o cliente informou.</div>
          </div>
          <button class="btn btn-ghost btn-sm" onclick="fecharApoio()">Fechar</button>
        </div>

        <div style="display:flex;gap:8px;margin-top:12px">
          <input style="flex:1" value="${escapeHtml(a.code || "")}"
            placeholder="Código do cliente"
            oninput="state.crm.support.code=this.value"
            onkeydown="if(event.key==='Enter'){event.preventDefault();buscarClienteApoio();}" />
          <button class="btn btn-secondary" type="button" onclick="buscarClienteApoio()">
            ${a.searching ? "Buscando…" : "Buscar"}</button>
        </div>

        ${a.notFound ? `<div class="text-small" style="margin-top:10px;color:var(--bad)">
          Nenhum cliente com este código. Confirme o número com o cliente.</div>` : ""}

        ${c ? `
          <div class="actions" style="margin-top:12px">
            <button class="btn btn-secondary btn-sm" type="button"
              onclick="abrirFichaApoio('${jsAttr(c.client_code)}')">Abrir ficha completa</button>
          </div>
          <div style="margin-top:14px;background:#f5f9ff;border:1px solid var(--accent);border-radius:10px;padding:12px">
            <div style="font-weight:700;font-size:15px">${escapeHtml(c.client_name)}</div>
            <div class="text-small" style="color:var(--muted);margin-top:2px">
              cód. ${escapeHtml(c.client_code)}
              ${c.document_number ? ` · ${escapeHtml(c.document_number)}` : ""}
            </div>
            <div class="crm-mini-grid crm-detail-grid" style="margin-top:10px">
              <div><span>Telefone</span><strong>${escapeHtml(c.updated_phone || c.phone || "Não informado")}</strong></div>
              <div><span>Contato</span><strong>${escapeHtml(c.primary_contact_name || "Não informado")}</strong></div>
              <div><span>Cidade</span><strong>${escapeHtml([c.city_name, c.neighborhood].filter(Boolean).join(" · ") || "-")}</strong></div>
              <div><span>Endereço</span><strong>${escapeHtml([c.address_line, c.address_number].filter(Boolean).join(", ") || "-")}</strong></div>
              <div><span>Última compra</span><strong>${escapeHtml(shortDate(c.last_sale_at) || "-")}</strong></div>
              <div><span>Vendedor responsável</span><strong>${escapeHtml(c.owner_name || "Sem vendedor")}</strong></div>
            </div>
            ${c.contact_notes ? `<div class="text-small" style="margin-top:8px;color:var(--muted)">
              Observações do cadastro: ${escapeHtml(c.contact_notes)}</div>` : ""}
          </div>

          ${(c.openTasks || []).length ? `
            <div class="text-small" style="margin-top:10px;padding:8px 10px;border-radius:8px;background:#fff8e6;border:1px solid #f0d68a;color:#7a5c00">
              <strong>Retorno em aberto:</strong>
              ${c.openTasks.map((t) => `${escapeHtml(t.title)} (${escapeHtml(shortDate(t.due_at) || "")})`).join(" · ")}
            </div>` : ""}

          ${(c.interactions || []).length ? `
            <div style="margin-top:10px">
              <div class="text-small" style="font-weight:700;margin-bottom:4px">Últimos contatos</div>
              <div style="border:1px solid var(--line);border-radius:8px;max-height:140px;overflow:auto">
                ${c.interactions.map((i) => `
                  <div style="padding:6px 10px;border-bottom:1px solid var(--line)" class="text-small">
                    <strong>${escapeHtml(shortDate(i.occurred_at) || "")}</strong> ·
                    ${escapeHtml(i.seller_name || "")} · ${escapeHtml(i.type_label || "")}
                    <div style="color:var(--muted)">${escapeHtml((i.notes || "").slice(0, 90))}</div>
                  </div>`).join("")}
              </div>
            </div>` : ""}

          <div class="field" style="margin-top:12px">
            <label>O que foi tratado</label>
            <textarea rows="3" placeholder="Ex: cliente pediu preço da pastilha X, passei o orçamento"
              oninput="state.crm.support.notes=this.value">${escapeHtml(a.notes)}</textarea>
          </div>

          ${c.isOwnClient ? `
            <div class="text-small" style="color:var(--muted)">
              Este cliente é da sua carteira — o contato conta normalmente na sua meta.
            </div>` : `
            <div class="text-small" style="color:var(--muted);background:#f5f7f9;border-radius:8px;padding:10px 12px">
              Atendimento de apoio: <strong>não conta na sua meta de ligações</strong>, mas fica no
              seu histórico e o gerente enxerga. ${escapeHtml(c.owner_name || "O responsável")}
              recebe uma tarefa para retomar o contato.
            </div>`}

          <div class="actions" style="margin-top:12px">
            <button class="btn btn-primary" ${a.saving ? "disabled" : ""} onclick="registrarApoio()">
              ${a.saving ? "Registrando…" : "Registrar atendimento"}</button>
            <button class="btn btn-ghost" onclick="fecharApoio()">Cancelar</button>
          </div>` : ""}
      </div>
    </div>
  `;
}

// ─── Cobertura de carteira ─────────────────────────────────────────────────
//
// O gerente autoriza, com prazo, um vendedor a enxergar a carteira de outro.
// Para o vendedor isso aparece como um par de chips no topo da Carteira —
// "Minha carteira" e o nome de quem ele cobre. Duas listas separadas, sem
// misturar os clientes e sem poluir a tela de quem não tem cobertura nenhuma.

async function loadCoverages() {
  try {
    state.crm.coverages = await api("/api/crm/coverages");
  } catch (error) {
    state.crm.coverages = { mine: [], canManage: false };
  }
  requestRender();
}

function trocarCarteira(nome) {
  state.crm.coverageOf = nome || "";
  state.crm.pagination.page = 1;
  void loadCrmClients();
}

function abrirCobertura(registro) {
  const c = registro || {};
  state.crm.coverageEditor = {
    id: c.id || "",
    coveringSeller: c.covering_seller || "",
    coveredSeller: c.covered_seller || "",
    startDate: c.start_date || dateInDays(0),
    endDate: c.end_date || "",
    reason: c.reason || "",
  };
  requestRender();
}

function fecharCobertura() {
  state.crm.coverageEditor = null;
  requestRender();
}

async function salvarCobertura() {
  const c = state.crm.coverageEditor;
  if (!c) return;
  try {
    const r = await api("/api/crm/coverages/save", { method: "POST", body: JSON.stringify(c) });
    addMessage("success", r.message || "Cobertura salva.");
    state.crm.coverageEditor = null;
    await loadCoverages();
  } catch (error) {
    addMessage("error", error.message);
  }
}

async function encerrarCobertura(id) {
  if (!window.confirm("Encerrar esta cobertura? O vendedor deixa de enxergar a carteira.")) return;
  try {
    const r = await api("/api/crm/coverages/delete", { method: "POST", body: JSON.stringify({ id }) });
    addMessage("success", r.message || "Cobertura encerrada.");
    await loadCoverages();
  } catch (error) {
    addMessage("error", error.message);
  }
}

/** Chips do vendedor: só aparecem quando existe cobertura ativa. */
function coberturaChips() {
  const c = state.crm.coverages;
  if (!c || c.canManage || !(c.mine || []).length) return "";
  const atual = state.crm.coverageOf;
  const chip = (nome, rotulo, sub) => `
    <button class="btn btn-sm ${(atual || "") === nome ? "btn-primary" : "btn-ghost"}"
      type="button" onclick="trocarCarteira('${jsAttr(nome)}')" style="text-align:left">
      ${escapeHtml(rotulo)}${sub ? `<div class="text-small" style="opacity:.75">${escapeHtml(sub)}</div>` : ""}
    </button>`;
  return `
    <div class="form-card" style="padding:12px 14px">
      <div style="display:flex;gap:8px;flex-wrap:wrap;align-items:center">
        <span class="text-small" style="color:var(--muted);margin-right:4px">Carteira:</span>
        ${chip("", "Minha carteira", "")}
        ${c.mine.map((cv) => chip(cv.covered_seller, cv.covered_seller,
            cv.end_date ? `cobertura até ${shortDate(cv.end_date)}` : "cobertura sem prazo")).join("")}
      </div>
      ${atual ? `<div class="text-small" style="margin-top:8px;color:#7a5c00;background:#fff8e6;
                   border:1px solid #f0d68a;border-radius:8px;padding:8px 10px">
        Você está vendo a carteira de <strong>${escapeHtml(atual)}</strong>. Os contatos que
        registrar aqui ficam no histórico do cliente e aparecem para o gerente como cobertura.
      </div>` : ""}
    </div>`;
}

/** Painel do gerente: quem cobre quem, com prazo. */
function coberturaGestaoCard() {
  const c = state.crm.coverages;
  if (!c || !c.canManage) return "";
  const linhas = c.all || [];
  const hoje = dateInDays(0);
  const vigente = (l) => l.start_date <= hoje && (!l.end_date || l.end_date >= hoje);
  return `
    <div class="form-card">
      <div class="section-title">
        <div><h3>Cobertura de carteira</h3>
        <div class="text-small">Férias e ausências: autorize um vendedor a enxergar a carteira de outro, com prazo.</div></div>
        <button class="btn btn-primary btn-sm" type="button" onclick="abrirCobertura()">+ Autorizar</button>
      </div>
      ${linhas.length ? `
        <div class="table-wrap">
          <table>
            <thead><tr><th>Quem cobre</th><th>Carteira coberta</th><th>Período</th><th>Motivo</th><th style="text-align:right">Ações</th></tr></thead>
            <tbody>
              ${linhas.map((l) => `
                <tr style="${vigente(l) ? "" : "opacity:.55"}">
                  <td><strong>${escapeHtml(l.covering_seller)}</strong></td>
                  <td>${escapeHtml(l.covered_seller)}</td>
                  <td class="text-small">${escapeHtml(shortDate(l.start_date) || "")} →
                      ${escapeHtml(l.end_date ? shortDate(l.end_date) : "sem prazo")}
                      ${vigente(l) ? '<span class="soft-badge" style="margin-left:6px">vigente</span>' : ""}</td>
                  <td class="text-small">${escapeHtml(l.reason || "-")}</td>
                  <td style="text-align:right;white-space:nowrap">
                    <button class="btn btn-ghost btn-sm" type="button" onclick='abrirCobertura(${JSON.stringify(l).replace(/'/g, "&#39;")})'>Editar</button>
                    <button class="btn btn-ghost btn-sm" type="button" onclick="encerrarCobertura(${Number(l.id)})">Encerrar</button>
                  </td>
                </tr>`).join("")}
            </tbody>
          </table>
        </div>` : '<div class="text-small" style="color:var(--muted)">Nenhuma cobertura ativa.</div>'}
    </div>`;
}

function coberturaModal() {
  const c = state.crm.coverageEditor;
  if (!c) return "";
  const vendedores = (state.crm.coverages?.sellers || []).map((v) => v.personName || v.person_name || v);
  const opcoes = (valor) => vendedores.map((v) =>
    `<option value="${escapeHtml(v)}" ${valor === v ? "selected" : ""}>${escapeHtml(v)}</option>`).join("");
  return `
    <div class="client-drawer-overlay open modal-dim" onclick="fecharCobertura()">
      <div class="panel modal-panel" style="max-width:520px;margin:8vh auto;padding:22px" onclick="event.stopPropagation()">
        <div class="section-title">
          <div><h3>🤝 Autorizar cobertura</h3>
          <div class="text-small">Quem cobre passa a enxergar a carteira do colega no período.</div></div>
          <button class="btn btn-ghost btn-sm" onclick="fecharCobertura()">Fechar</button>
        </div>
        <div class="two-column-form" style="margin-top:10px">
          <div class="field"><label>Quem cobre</label>
            <select onchange="state.crm.coverageEditor.coveringSeller=this.value">
              <option value="">Selecione…</option>${opcoes(c.coveringSeller)}
            </select></div>
          <div class="field"><label>Carteira coberta</label>
            <select onchange="state.crm.coverageEditor.coveredSeller=this.value">
              <option value="">Selecione…</option>${opcoes(c.coveredSeller)}
            </select></div>
          <div class="field"><label>Início</label>
            <input type="date" value="${escapeHtml(c.startDate)}" onchange="state.crm.coverageEditor.startDate=this.value" /></div>
          <div class="field"><label>Fim <span style="color:var(--muted);font-weight:400">(vazio = sem prazo)</span></label>
            <input type="date" value="${escapeHtml(c.endDate || "")}" onchange="state.crm.coverageEditor.endDate=this.value" /></div>
          <div class="field field-span-2"><label>Motivo</label>
            <input value="${escapeHtml(c.reason || "")}" placeholder="Ex: férias de 01/09 a 20/09"
              oninput="state.crm.coverageEditor.reason=this.value" /></div>
        </div>
        <div class="text-small" style="color:var(--muted)">
          Sem data final a cobertura não expira sozinha — prefira sempre definir o fim.
        </div>
        <div class="actions" style="margin-top:12px">
          <button class="btn btn-primary" type="button" onclick="salvarCobertura()">Salvar cobertura</button>
          <button class="btn btn-ghost" type="button" onclick="fecharCobertura()">Cancelar</button>
        </div>
      </div>
    </div>`;
}

/** Resumo da carteira do vendedor, com os mesmos números do painel do gerente.
 *
 * Reaproveita /api/crm/portfolio-summary de propósito, em vez de recontar no
 * navegador: se a régua de ativo, pré-inativo e queda for calculada em dois
 * lugares, os dois divergem no primeiro ajuste — e a conversa de feedback vira
 * discussão sobre qual tela está certa.
 */
function resumoCarteiraVendedor() {
  const ps = state.crm.portfolioSummary;
  if (!ps || ps.error) return "";
  const linhas = ps.sellers || [];
  // Para o vendedor o servidor já devolve UMA linha — a dele. Casar por nome
  // aqui só criaria um segundo lugar para o vínculo falhar, que é o defeito
  // que já custou caro nas atas e no feedback. Só quando vier mais de uma
  // linha é que o nome decide.
  const eu = meuNomeDeVendas();
  const linha = linhas.length === 1
    ? linhas[0]
    : linhas.find((s) => personKeyJs(s.sellerName) === personKeyJs(eu));
  if (!linha || !linha.total) return "";

  const share = (n) => `${((Number(n || 0) / linha.total) * 100).toFixed(1)}%`;
  const bloco = (rotulo, valor, cor, detalhe) => `
    <div style="flex:1;min-width:104px">
      <div class="text-small" style="color:var(--muted)">${rotulo}</div>
      <div style="font-size:19px;font-weight:800;${cor ? `color:${cor}` : ""}">${number(valor || 0)}</div>
      ${detalhe ? `<div class="text-small" style="color:var(--muted)">${detalhe}</div>` : ""}
    </div>`;

  return `
    <div class="form-card" style="padding:14px 18px">
      <div class="section-title" style="margin-bottom:10px">
        <div>
          <h3 style="font-size:15px">Minha carteira em números</h3>
          <div class="text-small">Competência ${escapeHtml(ps.competence || "—")} · mesma régua do painel do gerente</div>
        </div>
      </div>
      <div style="display:flex;gap:14px;flex-wrap:wrap">
        ${bloco("Carteira", linha.total, "", "clientes no seu nome")}
        ${bloco("Compraram no mês", linha.comVendaMes, "var(--good)", share(linha.comVendaMes))}
        ${bloco("Mês anterior", linha.comVendaMesAnterior, "", "para comparar")}
        ${bloco("Ativos", linha.ativos, "var(--good)", share(linha.ativos))}
        ${bloco("Pré-inativos", linha.preInativos, "#e0a800", share(linha.preInativos))}
        ${bloco("Inativos", linha.inativos, "var(--bad)", share(linha.inativos))}
        ${bloco("Queda >30%", linha.queda30, "var(--bad)", "vs mês anterior")}
        ${bloco("Queda >20%", linha.queda20, "#e0a800", "vs mês anterior")}
      </div>
      <div class="text-small" style="color:var(--muted);margin-top:10px;line-height:1.6">
        Pré-inativo é quem está entre 30 e 60 dias sem comprar — ainda dá para reverter com
        uma ligação. Passou de 60, vira inativo e a conversa é outra.
      </div>
    </div>`;
}

/** Nome do vendedor logado como aparece no faturamento. */
function meuNomeDeVendas() {
  return state.assistant?.myName || state.user?.linkedPersonName || state.user?.fullName || "";
}

/** Mesma normalização de nome do servidor: sem acento, sem sufixo, sem pontuação. */
function personKeyJs(nome) {
  return String(nome || "")
    .normalize("NFD").replace(/[\u0300-\u036f]/g, "")
    .toUpperCase().replace(/\([^)]*\)/g, " ")
    .replace(/[^A-Z0-9 ]/g, " ").replace(/\s+/g, " ").trim();
}

/** Saída para o vendedor quando a busca na própria carteira não achou nada.
 *
 * O caso real: ele atende um cliente de outro vendedor e procura pelo nome.
 * Não acha, porque a carteira dele não tem esse cliente — e ficava sem saber
 * que existe um caminho. Aqui o aviso aparece só quando ele buscou algo, e
 * deixa claro que o atalho é pelo CÓDIGO, não pelo nome.
 */
function buscaSemResultadoVendedor(rows) {
  const termo = (state.crm.crmClientFilters?.search || "").trim();
  if (!termo || rows.length) return "";
  const pareceCodigo = /^\d+$/.test(termo);
  return `
    <div class="form-card" style="border-left:4px solid var(--accent)">
      <div style="font-weight:700;font-size:14px">Nada encontrado na sua carteira para "${escapeHtml(termo)}"</div>
      <div class="text-small" style="color:var(--muted);margin-top:6px;line-height:1.6">
        Se este cliente é de outra carteira, você ainda pode atendê-lo — mas a busca aí é
        <strong>pelo código</strong>, não pelo nome. Peça o código ao cliente.
        ${pareceCodigo ? "" : `<br>O que você digitou não parece um código.`}
      </div>
      <div class="actions" style="margin-top:10px">
        <button class="btn btn-primary btn-sm" type="button"
          onclick="abrirApoio('${pareceCodigo ? jsAttr(termo) : ""}')">
          🤝 Atender cliente de outra carteira pelo código
        </button>
      </div>
    </div>`;
}

function crmClientsView() {
  if (!state.crm.summary) return `<div class="loader panel">Carregando clientes CRM...</div>`;
  const rows = filteredCrmClients();
  const blocoCobertura = coberturaChips() + coberturaGestaoCard();

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
        ${blocoCobertura}
        ${resumoCarteiraVendedor()}
        ${sellerFilterBar()}
        ${isLoading ? `<div class="message" style="background:rgba(15,48,68,0.07);color:var(--accent);font-weight:600">⏳ Atualizando carteira…</div>` : ""}
        ${activeSellerFilterCount() > 0 ? `
          <div class="message" style="font-size:12px;background:rgba(15,48,68,0.06)">
            Filtro ativo — mostrando ${number(rows.length)} cliente(s) da sua carteira.
            A ordem dos blocos continua a mesma: urgentes primeiro.
          </div>` : ""}
        ${buscaSemResultadoVendedor(rows)}
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

    // Os cartões somam a MESMA lista que a tabela mostra.
    // Antes vinham prontos do servidor, que só conhece competência e PJ/PF —
    // filtrar por unidade, status ou vendedor mudava a tabela e deixava os
    // números de cima parados, dizendo outra coisa.
    const linhasFiltradas = applyLocalFilters(psSellers);
    const somar = (campo) => linhasFiltradas.reduce((acc, r) => acc + Number(r[campo] || 0), 0);
    const totalFiltrado = somar("total");
    const totF = {
      total: totalFiltrado,
      ativos: somar("ativos"),
      preInativos: somar("preInativos"),
      inativos: somar("inativos"),
      comVendaMes: somar("comVendaMes"),
      comVendaMesAnterior: somar("comVendaMesAnterior"),
    };
    totF.semVendaMes = Math.max(0, totF.total - totF.comVendaMes);
    totF.pctAtivos = totalFiltrado ? Math.round(totF.ativos / totalFiltrado * 1000) / 10 : 0;
    totF.pctInativos = totalFiltrado ? Math.round(totF.inativos / totalFiltrado * 1000) / 10 : 0;
    const filtroLigado = Boolean(pfState.search || pfState.unit || pfState.status);

    return `
      <div class="stack">
        <!-- Filtros -->
        ${portfolioFilterBar()}

        ${filtroLigado ? `
          <div class="message" style="font-size:12px;background:rgba(15,48,68,0.06)">
            Filtro ativo — os números abaixo somam ${number(linhasFiltradas.length)} de
            ${number(psSellers.length)} vendedor(es).
          </div>` : ""}

        <!-- Totais -->
        <div class="kpi-grid">
          <div class="kpi-card"><div class="kpi-value">${number(totF.total)}</div><div class="kpi-label">Total de clientes</div><div class="kpi-sub">${number(totF.comVendaMes)} com compra no mês</div></div>
          <div class="kpi-card"><div class="kpi-value" style="color:var(--good)">${number(totF.ativos)}</div><div class="kpi-label">Ativos <span style="font-size:12px;font-weight:400">(${totF.pctAtivos}%)</span></div><div class="kpi-sub">${number(totF.preInativos)} pré-inativos</div></div>
          <div class="kpi-card"><div class="kpi-value" style="color:var(--bad)">${number(totF.inativos)}</div><div class="kpi-label">Inativos <span style="font-size:12px;font-weight:400">(${totF.pctInativos}%)</span></div><div class="kpi-sub">Prioridade de reativação</div></div>
          <div class="kpi-card"><div class="kpi-value">${number(totF.comVendaMesAnterior)}</div><div class="kpi-label">Compraram mês anterior</div><div class="kpi-sub">${number(totF.semVendaMes)} sem compra este mês</div></div>
        </div>

        <!-- Tabela por vendedor -->
        <div class="table-card">
          <div class="section-title">
            <div><h3>Resumo por Vendedor</h3><div class="text-small">Competência ${escapeHtml(ps.competence || "—")} · mês anterior ${escapeHtml(ps.prevCompetence || "—")}</div></div>
            ${botaoAtualizar("resumoCarteira", "loadPortfolioSummary()", { mensagem: "Resumo por vendedor atualizado." })}
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
                ${linhasFiltradas.map((r) => `
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
      ${blocoCobertura}
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
                  <th title="Contato ativo, visita, retorno pendente ou nunca contatado">Sinais</th>
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
                    <td style="white-space:nowrap">${engagementMarks(item.engagement)}</td>
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
                `).join("") || `<tr><td colspan="13">
                    Nenhum cliente encontrado com os filtros selecionados.
                    ${roleIsSeller() ? `
                      <div style="margin-top:8px">
                        <button class="btn btn-secondary btn-sm" type="button"
                          onclick="abrirApoio('${jsAttr(state.crm.crmClientFilters?.search || "")}')">
                          🤝 Atender cliente de outra carteira pelo código
                        </button>
                      </div>` : ""}
                  </td></tr>`}
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
          ${detail && detail.isOwnClient === false && roleIsSeller() ? `
            <span class="soft-badge" style="background:#e0f2f1;color:#00695c;align-self:center">
              🤝 cliente de outra carteira — o registro entra como apoio
            </span>` : ""}
          <button class="btn btn-secondary" ${client.clientKey ? "" : "disabled"} onclick="openContactUpdateModal('${escapeHtml(client.clientKey || "")}')">Atualizar contato</button>
          <button class="btn btn-secondary" ${client.clientKey ? "" : "disabled"}
            onclick="openReceptiveModal('${escapeHtml(client.clientKey || "")}')"
            title="Ligação que você recebeu, mensagem trocada ou informação sobre o cliente. Não conta na meta de ligações ativas.">
            📝 Registro receptivo
          </button>
          ${roleIsSeller() ? `
            <button class="btn btn-secondary" ${client.clientKey ? "" : "disabled"}
              onclick="openScheduleContactModal('${escapeHtml(client.clientKey || "")}')"
              title="Criar uma tarefa para você voltar a falar com este cliente">
              📅 Agendar contato
            </button>` : ""}
          ${detail?.canAssignTask ? `
            <button class="btn btn-secondary" ${client.clientKey ? "" : "disabled"}
              onclick="openAssignTaskModal('${escapeHtml(client.clientKey || "")}')"
              title="Criar tarefa de contato para o vendedor responsável">
              📣 Cobrar contato
            </button>` : ""}
          <button class="btn btn-ghost" ${client.clientCode || client.clientKey ? "" : "disabled"}
            onclick="imprimirFichaCliente('${jsAttr(client.clientCode || client.clientKey || "")}')"
            title="Ficha cadastral em PDF, já preenchida com o que existe no cadastro, para o cliente assinar">
            📄 Ficha para assinatura
          </button>
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
                ${profile.territory ? `
                <div><span>Território</span><strong>${escapeHtml(profile.territory.unit || "compartilhado")}</strong>
                  <div class="text-small" style="color:var(--muted)">${escapeHtml(profile.territory.reason || "")}</div>
                </div>` : ""}
              </div>
              ${profile.territory && profile.territory.unit && client.unitName
                 && profile.territory.unit !== client.unitName ? `
                <div class="text-small" style="margin-top:8px;padding:8px 10px;border-radius:8px;
                     background:#fff8e6;border:1px solid #f0d68a;color:#7a5c00">
                  O bairro é território da <strong>${escapeHtml(profile.territory.unit)}</strong>, mas quem
                  atende hoje é a <strong>${escapeHtml(client.unitName)}</strong>. A carteira não muda sozinha —
                  vale a decisão do gerente.
                </div>` : ""}
            </div>
            <div class="subtle-card padded-card">
              <div class="section-title"><h3>Situação comercial</h3></div>
              <div class="crm-mini-grid crm-detail-grid">
                <div><span>Última compra</span><strong>${escapeHtml(client.lastPurchaseAt ? client.lastPurchaseAt.slice(0, 10) : "-")}</strong></div>
                <div><span>Dias sem compra</span><strong>${number(client.daysWithoutPurchase || 0)}</strong></div>
                ${Number(client.creditLimit || profile.credit_limit || 0) > 0 ? `
                  <div><span>Limite de crédito</span><strong>${currency(client.creditLimit || profile.credit_limit)}</strong></div>
                  <div><span>Saldo previsto</span>
                    <strong style="color:${Number(client.predictedBalance) < 0 ? "var(--bad)" : "var(--good)"}">
                      ${currency(client.predictedBalance)}</strong>
                    <div class="text-small" style="color:var(--muted)">
                      limite − compras do mês · não inclui parcelas anteriores em aberto</div>
                  </div>` : ""}
                <div><span>Faturamento mês atual</span><strong>${currency(client.currentRevenue)}</strong></div>
                <div><span>Média dos 3 meses anteriores</span><strong>${currency(client.averageRevenue)}</strong></div>
                <div><span>Crescimento ou queda</span><strong>${pct((client.growthPct || 0) * 100)}</strong></div>
                <div><span>Motivo principal</span><strong>${escapeHtml(client.primaryReason || "-")}</strong></div>
              </div>
              ${client.duplicateOfCode ? `
                <div class="message" style="background:#fff3e0;color:#e65100;font-size:12px;margin-top:8px">
                  ⚠ Cadastro duplicado: este cliente também existe no código
                  <strong>${escapeHtml(client.duplicateOfCode)}</strong>, que é onde o faturamento está
                  contabilizado. Vale unificar os cadastros no Alfa.
                </div>` : ""}
              ${averageBreakdown(client)}
            </div>
            ${clientVisitBlock(client.clientKey || state.crm.selectedClientKey || "")}
            ${clientActionPanel(client)}
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

// ─── Tarefas ────────────────────────────────────────────────────────────────

async function loadCrmTasks(silencioso) {
  const f = state.taskFilters;
  const q = new URLSearchParams();
  q.set("status", f.status || "ABERTAS");
  if (f.seller) q.set("seller", f.seller);
  if (f.from) q.set("from", f.from);
  if (f.to) q.set("to", f.to);
  if (f.origin) q.set("origin", f.origin);
  if (f.search) q.set("q", f.search);
  if (!silencioso) {
    state.ui.loading.crmTasks = true;
    requestRender();   // pinta o "carregando" ANTES de ir à rede
  }
  try {
    const r = await api(`/api/crm/tasks?${q.toString()}`);
    state.crm.taskRows = r.rows || [];
    state.tasks = r;
  } catch (e) {
    state.tasks = { error: e.message, rows: [] };
  } finally {
    state.ui.loading.crmTasks = false;
    requestRender();
  }
}

function setTaskFilter(campo, valor) {
  const novo = state.taskFilters[campo] === valor ? "" : valor;
  state.taskFilters[campo] = novo;
  trocarChip(`task_${campo}`, novo, () => loadCrmTasks());
}

function setTaskStatus(valor) {
  state.taskFilters.status = valor;
  trocarChip("taskStatus", valor, () => loadCrmTasks());
}

function applyTaskSearch() {
  const campo = document.getElementById("task-search");
  state.taskFilters.search = (campo ? campo.value : state.taskFilters.search || "").trim();
  loadCrmTasks();
}

function limparFiltrosTarefa() {
  state.taskFilters = { status: "ABERTAS", seller: "", from: "", to: "", origin: "", search: "" };
  loadCrmTasks();
}

function taskOriginCfg(origem) {
  return (state.tasks?.origins || []).find((o) => o.id === origem)
    || { label: origem, icon: "•", color: "#5f6368", bg: "#f1f3f4" };
}

// ─── Nova tarefa (direcionamento) ───────────────────────────────────────────

function novaTarefa() {
  state.taskEditor = {
    title: "", description: "", dueAt: dateInDays(1), priority: "NORMAL",
    clientKey: "", clientName: "", assignees: [], saving: false,
  };
  requestRender();
}

function fecharNovaTarefa() { state.taskEditor = null; requestRender(); }

function toggleDestinatario(nome) {
  const t = state.taskEditor;
  if (!t) return;
  const i = t.assignees.indexOf(nome);
  if (i >= 0) t.assignees.splice(i, 1); else t.assignees.push(nome);
  requestRender();
}

function selecionarTodosDestinatarios(apenasVendedores) {
  const t = state.taskEditor;
  if (!t) return;
  const alvo = (state.tasks?.people || [])
    .filter((p) => !apenasVendedores || p.role === "Vendedor")
    .map((p) => p.personName);
  t.assignees = t.assignees.length === alvo.length ? [] : alvo;
  requestRender();
}

function atribuirParaMim() {
  const t = state.taskEditor;
  if (!t) return;
  const eu = state.tasks?.myName;
  if (!eu) return;
  t.assignees = t.assignees.includes(eu) ? t.assignees.filter((n) => n !== eu) : [...t.assignees, eu];
  requestRender();
}

async function salvarNovaTarefa() {
  const t = state.taskEditor;
  if (!t) return;
  if (!t.title.trim()) { addMessage("error", "Escreva o que precisa ser feito."); return; }
  if (!t.assignees.length) { addMessage("error", "Escolha quem vai receber a tarefa."); return; }
  t.saving = true; requestRender();
  try {
    const r = await api("/api/crm/tasks/create", { method: "POST", body: JSON.stringify(t) });
    addMessage("success", r.created === 1
      ? "Tarefa criada."
      : `Tarefa criada para ${r.created} pessoas — cada uma conclui a sua.`);
    state.taskEditor = null;
    await loadCrmTasks(true);
  } catch (e) {
    addMessage("error", e.message);
    if (state.taskEditor) state.taskEditor.saving = false;
    requestRender();
  }
}

async function excluirTarefa(taskId) {
  if (!confirm("Excluir esta tarefa?")) return;
  try {
    await api("/api/crm/tasks/delete", { method: "POST", body: JSON.stringify({ taskId }) });
    await loadCrmTasks(true);
  } catch (e) { addMessage("error", e.message); }
}

// ─── View ───────────────────────────────────────────────────────────────────

function crmTasksView() {
  if (!state.tasks) { loadCrmTasks(); return `<div class="loader panel">Carregando tarefas…</div>`; }
  if (state.tasks.error) return `<div class="message error">${escapeHtml(state.tasks.error)}</div>`;

  const f = state.taskFilters;
  const rows = state.tasks.rows || [];
  const c = state.tasks.counters || {};
  const podeCriar = Boolean(state.tasks.canCreate);
  const temFiltro = Boolean(f.seller || f.from || f.to || f.origin || f.search || f.status !== "ABERTAS");

  const kpi = (rotulo, valor, cor) => `
    <div style="flex:1;min-width:110px;background:#fff;border:1px solid var(--line);border-radius:10px;padding:10px 12px">
      <div class="text-small" style="color:var(--muted)">${rotulo}</div>
      <div style="font-size:22px;font-weight:800;color:${cor || "inherit"}">${number(valor || 0)}</div>
    </div>`;

  return `
    <div class="stack">
      ${state.taskEditor ? novaTarefaModal() : ""}

      <div style="display:flex;gap:10px;flex-wrap:wrap">
        ${kpi("Em aberto", c.open)}
        ${kpi("Atrasadas", c.overdue, c.overdue ? "var(--bad)" : "")}
        ${kpi("Vencem hoje", c.today, c.today ? "var(--warn, #b06000)" : "")}
        ${kpi("Concluídas no mês", c.doneMonth, "var(--good)")}
      </div>

      <div class="form-card" style="padding:14px 18px">
        <div style="display:flex;gap:8px;flex-wrap:wrap;align-items:center;margin-bottom:10px">
          ${(state.tasks.statusFilters || []).map((s) => `
            <button type="button" onclick="setTaskStatus('${s.id}')"
              ${chipEmEspera("taskStatus") ? "disabled" : ""}
              style="border:1px solid ${f.status === s.id ? "var(--accent)" : "var(--line)"};
                     background:${f.status === s.id ? "var(--accent)" : "#fff"};
                     color:${f.status === s.id ? "#fff" : "var(--text)"};
                     border-radius:14px;padding:5px 14px;font-size:12px;font-weight:600;
                     ${chipEstadoCss("taskStatus", f.status === s.id)}">
              ${chipTrocando("taskStatus") === s.id
                ? `<span class="girando">↻</span> Carregando…`
                : escapeHtml(s.label)}
            </button>`).join("")}
          <span style="flex:1"></span>
          ${podeCriar ? `<button class="btn btn-primary btn-sm" onclick="novaTarefa()">＋ Nova tarefa</button>` : ""}
        </div>

        <div style="display:flex;gap:8px;flex-wrap:wrap;align-items:center">
          <input id="task-search" style="flex:1;min-width:200px"
            placeholder="🔍 Buscar por título, cliente ou descrição — Enter"
            value="${escapeHtml(f.search)}"
            oninput="state.taskFilters.search=this.value"
            onkeydown="if(event.key==='Enter'){event.preventDefault();applyTaskSearch();}" />
          <button class="btn btn-secondary btn-sm" onclick="applyTaskSearch()">Buscar</button>
          ${(state.tasks.sellers || []).length > 1 ? `
            <select style="min-width:190px" onchange="state.taskFilters.seller=this.value;loadCrmTasks()">
              <option value="">Todos os vendedores</option>
              ${(state.tasks.sellers || []).map((s) => `
                <option value="${escapeHtml(s)}" ${f.seller === s ? "selected" : ""}>${escapeHtml(s)}</option>`).join("")}
            </select>` : ""}
          <span class="text-small" style="color:var(--muted)">Vencimento</span>
          <input type="date" style="width:150px" value="${escapeHtml(f.from)}"
            onchange="state.taskFilters.from=this.value;loadCrmTasks()" />
          <span class="text-small">até</span>
          <input type="date" style="width:150px" value="${escapeHtml(f.to)}"
            onchange="state.taskFilters.to=this.value;loadCrmTasks()" />
          ${temFiltro ? `<button class="btn btn-ghost btn-sm" onclick="limparFiltrosTarefa()">Limpar</button>` : ""}
        </div>

        <div style="display:flex;gap:6px;flex-wrap:wrap;margin-top:10px">
          ${(state.tasks.origins || []).map((o) => `
            <button type="button" onclick="setTaskFilter('origin','${o.id}')" title="${escapeHtml(o.hint)}"
              ${chipEmEspera("task_origin") ? "disabled" : ""}
              style="border:1px solid ${f.origin === o.id ? o.color : "var(--line)"};
                     background:${f.origin === o.id ? o.bg : "#fff"};
                     color:${f.origin === o.id ? o.color : "var(--muted)"};
                     border-radius:14px;padding:4px 12px;font-size:12px;
                     font-weight:${f.origin === o.id ? "700" : "500"};
                     ${chipEstadoCss("task_origin", f.origin === o.id)}">
              ${chipTrocando("task_origin") === o.id
                ? `<span class="girando">↻</span> Carregando…`
                : `${o.icon} ${escapeHtml(o.label)}`}
            </button>`).join("")}
        </div>
      </div>

      <div class="table-card">
        <div class="section-title">
          <div><h3>Tarefas</h3>
            <div class="text-small">${rows.length} no filtro atual</div></div>
        </div>
        <div class="timeline-list">
          ${state.ui.loading.crmTasks ? '<div class="loader">Buscando…</div>' : ""}
          ${rows.map((row) => taskRow(row, podeCriar)).join("")
            || emptyStateCard(f.status === "CONCLUIDAS"
                ? "Nenhuma tarefa concluída no filtro atual."
                : "Nenhuma tarefa pendente. Fila limpa.")}
        </div>
      </div>
    </div>`;
}

function taskRow(row, podeGerir) {
  const concluida = row.status === "CONCLUIDA";
  const cfg = taskOriginCfg(row.origin);
  const cor = concluida ? "var(--good)" : row.overdue ? "var(--bad)" : "var(--accent)";
  const prazo = (row.due_at || "").replace("T", " ").slice(0, 16);
  return `
    <div class="timeline-item" style="border-left:3px solid ${cor};padding-left:12px;${concluida ? "opacity:.75" : ""}">
      <div style="display:flex;justify-content:space-between;align-items:flex-start;gap:8px;flex-wrap:wrap">
        <div style="flex:1;min-width:230px">
          <div style="display:flex;gap:6px;align-items:center;flex-wrap:wrap;margin-bottom:2px">
            <span class="status-tag" style="background:${cfg.bg};color:${cfg.color}">${cfg.icon} ${escapeHtml(cfg.label)}</span>
            ${row.priority === "ALTA" ? '<span class="status-tag bad">Prioridade alta</span>' : ""}
            ${row.overdue ? '<span class="status-tag bad">Atrasada</span>' : ""}
            ${concluida ? '<span class="status-tag good">✓ Concluída</span>' : ""}
          </div>
          <strong>${escapeHtml(row.title || "—")}</strong>
          ${row.client_name ? `<div class="text-small">Cliente: ${escapeHtml(row.client_name)}</div>` : ""}
          ${row.description ? `<div class="text-small" style="color:var(--muted)">${escapeHtml(row.description)}</div>` : ""}
          <div class="text-small" style="color:var(--muted)">
            ${escapeHtml(row.seller_name || "")}${row.created_by_name ? ` · por ${escapeHtml(row.created_by_name)}` : ""}
          </div>
        </div>
        <div style="text-align:right;white-space:nowrap">
          <div class="text-small" style="color:${row.overdue ? "var(--bad)" : "var(--muted)"}">
            ${concluida ? "concluída " + shortDate(row.completed_at || "") : escapeHtml(prazo)}
          </div>
        </div>
      </div>
      ${!concluida ? `
        <div class="actions" style="margin-top:10px;gap:6px">
          ${row.client_key ? `
            <button class="btn btn-primary btn-sm" onclick="prefillInteractionFromAgenda('${jsAttr(row.client_key)}','${jsAttr(row.client_name || "")}')">📞 Registrar contato</button>` : ""}
          <button class="btn btn-secondary btn-sm" onclick="completeCrmTask(${Number(row.id)})">✅ Concluir</button>
          <button class="btn btn-ghost btn-sm" onclick="openTaskRescheduleModal(${Number(row.id)})">📅 Reagendar</button>
          ${row.client_key ? `<button class="btn btn-ghost btn-sm" onclick="openCrmClient('${jsAttr(row.client_key)}', false)">Ficha</button>` : ""}
          ${podeGerir ? `<button class="btn btn-ghost btn-sm" onclick="excluirTarefa(${Number(row.id)})">Excluir</button>` : ""}
        </div>` : ""}
    </div>`;
}

function novaTarefaModal() {
  const t = state.taskEditor;
  const pessoas = state.tasks?.people || [];
  const vendedores = pessoas.filter((p) => p.role === "Vendedor");
  const eu = state.tasks?.myName || "";
  return `
    <div class="client-drawer-overlay open modal-dim" onclick="fecharNovaTarefa()">
      <div class="panel modal-panel" data-keep-scroll="nova-tarefa"
           style="max-width:660px;margin:6vh auto;padding:22px;max-height:88vh;overflow:auto"
           onclick="event.stopPropagation()">
        <div class="section-title">
          <div><h3>🎯 Nova tarefa</h3>
            <div class="text-small">Direcionamento para a equipe. Cliente é opcional.</div></div>
          <button class="btn btn-ghost btn-sm" onclick="fecharNovaTarefa()">Fechar</button>
        </div>

        <div class="field" style="margin-top:12px">
          <label>O que precisa ser feito <span style="color:var(--bad)">*</span></label>
          <input value="${escapeHtml(t.title)}" oninput="state.taskEditor.title=this.value"
            placeholder="Ex.: Revisar os orçamentos do dia e levantar os motivos de desistência" />
        </div>

        <div class="field">
          <label>Detalhe <span style="color:var(--muted);font-weight:400">(opcional)</span></label>
          <textarea rows="3" style="font-family:inherit" oninput="state.taskEditor.description=this.value"
            placeholder="O que esperar como resultado, onde buscar a informação">${escapeHtml(t.description)}</textarea>
        </div>

        <div style="display:grid;grid-template-columns:1fr 1fr 2fr;gap:10px">
          <div class="field"><label>Prazo</label>
            <input type="date" value="${escapeHtml(t.dueAt)}" oninput="state.taskEditor.dueAt=this.value" /></div>
          <div class="field"><label>Prioridade</label>
            <select onchange="state.taskEditor.priority=this.value">
              ${(state.tasks?.priorities || []).map((p) => `
                <option value="${p.id}" ${t.priority === p.id ? "selected" : ""}>${escapeHtml(p.label)}</option>`).join("")}
            </select></div>
          <div class="field"><label>Cliente <span style="color:var(--muted);font-weight:400">(opcional)</span></label>
            <input value="${escapeHtml(t.clientKey)}" oninput="state.taskEditor.clientKey=this.value"
              placeholder="Código, se a tarefa for de um cliente" /></div>
        </div>

        <div class="subtle-card padded-card" style="margin-top:8px">
          <div class="section-title">
            <div><h3>Para quem</h3>
              <div class="text-small">${t.assignees.length} selecionado(s). Cada pessoa recebe a sua tarefa e conclui separadamente.</div></div>
            <div style="display:flex;gap:6px;flex-wrap:wrap">
              ${eu ? `<button class="btn btn-ghost btn-sm" onclick="atribuirParaMim()">Para mim</button>` : ""}
              ${vendedores.length ? `<button class="btn btn-ghost btn-sm" onclick="selecionarTodosDestinatarios(true)">Toda a equipe de vendas</button>` : ""}
            </div>
          </div>
          <div style="display:flex;gap:6px;flex-wrap:wrap;margin-top:8px;max-height:200px;overflow:auto">
            ${pessoas.map((p) => {
              const on = t.assignees.includes(p.personName);
              return `
                <button type="button" onclick="toggleDestinatario('${jsAttr(p.personName)}')"
                  title="${escapeHtml(p.role)}${p.unitName ? " · " + escapeHtml(p.unitName) : ""}"
                  style="border:1px solid ${on ? "var(--accent)" : "var(--line)"};
                         background:${on ? "var(--accent)" : "#fff"};color:${on ? "#fff" : "var(--text)"};
                         border-radius:14px;padding:4px 10px;font-size:12px;font-weight:600;cursor:pointer">
                  ${on ? "● " : "○ "}${escapeHtml(p.personName)}${p.hasLogin ? "" : " ⚠"}
                </button>`;
            }).join("") || '<div class="text-small">Nenhuma pessoa disponível nas suas unidades.</div>'}
          </div>
          ${t.assignees.some((n) => !(pessoas.find((p) => p.personName === n)?.hasLogin)) ? `
            <div class="message" style="background:#fff3e0;color:#e65100;font-size:12px;margin-top:8px">
              ⚠ Alguém selecionado não tem login no CRM e não vai ver a tarefa.
            </div>` : ""}
        </div>

        <div class="actions" style="margin-top:14px">
          <button class="btn btn-primary" ${t.saving ? "disabled" : ""} onclick="salvarNovaTarefa()">
            ${t.saving ? "Criando…" : "Criar tarefa"}</button>
          <button class="btn btn-ghost" onclick="fecharNovaTarefa()">Cancelar</button>
        </div>
      </div>
    </div>`;
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

            <div style="background:#f5f9ff;border:1px solid var(--accent);border-radius:12px;padding:14px">
              <label class="check-row" style="color:var(--accent)">
                <input type="checkbox" ${form.requestVisit ? "checked" : ""}
                  onchange="state.crm.interactionForm.requestVisit=this.checked;requestRender()" />
                <span>🙋 Pedir visita do gerente para este cliente</span>
              </label>
              ${form.requestVisit ? `
                <div class="field" style="margin-top:10px">
                  <input value="${escapeHtml(form.visitReason || "")}"
                    oninput="state.crm.interactionForm.visitReason=this.value"
                    placeholder="Por que a visita resolve o que a ligação não resolveu?" />
                </div>
                <div class="text-small" style="color:var(--muted)">
                  O pedido entra na fila do gerente com o motivo que você escrever. Seja específico —
                  é o que ele lê para montar a rota da semana.
                </div>` : `
                <div class="text-small" style="margin-top:6px;color:var(--muted)">
                  Use quando o telefone não resolve: cliente parado, problema antigo ou negociação que
                  precisa de presença.
                </div>`}
            </div>

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

async function openCrmClient(clientKey, switchToClientsTab = true, renderAfterLoad = true,
                             { outside = false } = {}) {
  if (!clientKey) return;
  state.crm.selectedClientKey = clientKey;
  state.ui.crmClientDetailTab = "historico";
  state.ui.clientDrawerOpen = true;
  state.crm.clientVisits = null;          // some o histórico do cliente anterior
  loadClientVisitHistory(clientKey);      // em paralelo, não atrasa a abertura
  setLoading("clientDrawer", true);
  state.ui.clientDrawerError = "";
  resetSelectedClientTabs();
  if (switchToClientsTab) {
    state.activeTab = "crm-clientes";
  }
  if (renderAfterLoad) requestRender();

  try {
    // 1. Carrega só o summary — abre o drawer imediatamente
    state.crm.selectedClient = await api(
      `/api/crm/client/summary?${buildQuery()}&clientKey=${encodeURIComponent(clientKey)}`
      + (outside ? "&outside=1" : ""));
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

/**
 * Abre o formulário de interação já preenchido com os dados do cliente.
 *
 * `fallbackName` existe para os atalhos vindos de tarefas: o cliente da tarefa
 * pode não estar na página de carteira carregada no momento, e sem isso a função
 * saía calada — o botão parecia quebrado.
 */
function prefillInteractionFromAgenda(clientKey, fallbackName) {
  const source = state.crm.clients.find((item) => item.clientKey === clientKey)
    || state.crm.agenda.top5.find((item) => item.clientKey === clientKey)
    || state.crm.agenda.extended.find((item) => item.clientKey === clientKey)
    || (state.crm.selectedClient?.summary?.clientKey === clientKey ? state.crm.selectedClient.summary : null)
    || (clientKey ? { clientKey, clientName: fallbackName || clientKey } : null);
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
    // Horário LOCAL, não UTC. toISOString() devolve UTC e um contato feito
    // às 21h no Brasil virava "amanhã", nunca saindo da fila do dia.
    occurredAt: localDateTimeInput(),
    notes: "",
    questionUsed: source.questionPrimary || "",
    hadProgress: false,
    offerTitle: source.offerPrimary?.title || "",
    nextAction: crmRecommendedAction(source),
    followupDueAt: "",
    requestVisit: false,
    visitReason: "",
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
    requestVisit: false, visitReason: "",
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
        // Cliente de outra carteira: o servidor confirma e grava como APOIO,
        // fora da meta de ligações. Marcar aqui evita depender da tela.
        initiative: form.initiative
          || (state.crm.selectedClient?.isOwnClient === false ? "APOIO" : "ATIVO"),
        clientKey: form.clientCode || form.clientKey,
        occurredAt: form.occurredAt ? form.occurredAt.replace("T", " ") : localDateTimeString(),
        followupDueAt: form.followupDueAt ? form.followupDueAt.replace("T", " ") : "",
        hadProgress: form.resultCode === "GEROU_PEDIDO" || form.resultCode === "GEROU_ORCAMENTO",
      }),
    });
    // Contato em prospect: recarrega para o status e o "dias sem contato"
    // acompanharem o que acabou de acontecer.
    if (String(form.clientCode || form.clientKey || "").startsWith("P-")) {
      loadProspects(true);
    }
    // Pedido de visita: sai depois da interação porque nasce dela. Se falhar,
    // o contato já está registrado — o vendedor não perde o trabalho.
    if (form.requestVisit) {
      try {
        const rv = await api("/api/visits/request", {
          method: "POST",
          body: JSON.stringify({
            clientKey: form.clientCode || form.clientKey,
            clientName: form.clientName,
            reason: form.visitReason || form.notes || "Solicitado durante ligação",
          }),
        });
        addMessage(rv.duplicated ? "warn" : "success", rv.message || "Pedido de visita enviado.");
      } catch (err) {
        addMessage("warn", `Contato registrado, mas o pedido de visita falhou: ${err.message}`);
      }
    }
    // Atualizar placar de ligações em background
    if (roleIsSeller() && placarEnabled()) loadSellerScore();
    const resultLabel = {
      GEROU_PEDIDO: "🎉 Venda registrada!",
      GEROU_ORCAMENTO: "📋 Orçamento registrado!",
      PEDIU_RETORNO: "📅 Retorno agendado!",
      FALOU_CLIENTE: "✅ Contato registrado!",
      NAO_ATENDEU: "✅ Tentativa registrada.",
    }[form.resultCode] || "✅ Contato registrado!";
    addMessage("success", resultLabel);
    // Remove da fila na hora, sem esperar o reload. A comparação normaliza os
    // códigos do mesmo jeito que o servidor faz — comparar as strings cruas
    // deixava o cliente na lista quando havia diferença de espaço ou zero à esquerda.
    const norm = (v) => String(v || "").toUpperCase().replace(/[^A-Z0-9]/g, "");
    const contactedKey = norm(form.clientCode || form.clientKey);
    if (state.crm.agenda) {
      state.crm.agenda.top5 = (state.crm.agenda.top5 || []).filter((c) => norm(c.clientKey) !== contactedKey);
      state.crm.agenda.extended = (state.crm.agenda.extended || []).filter((c) => norm(c.clientKey) !== contactedKey);
    }
    if (Array.isArray(state.crm.clients)) {
      state.crm.clients = state.crm.clients.map((c) =>
        norm(c.clientKey) === contactedKey ? { ...c, lastInteractionAt: localDateTimeString() } : c);
    }
    // O backend conclui as tarefas abertas desse cliente ao registrar o contato;
    // marca aqui também para o retorno sumir da Missão do Dia sem piscar.
    if (Array.isArray(state.crm.taskRows)) {
      state.crm.taskRows = state.crm.taskRows.map((t) =>
        norm(t.client_key) === contactedKey && t.status !== "CONCLUIDA"
          ? { ...t, status: "CONCLUIDA" } : t);
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
            <tr><th>Unidade</th><th>Líquido</th><th>Meta</th><th>% Meta</th><th>% Proj.</th><th>Dev. comercial</th><th>% Dev.</th><th>Dev. garantia</th><th>Margem</th><th>Qtd. Peças</th><th>Ticket/Peça</th><th>Meta diária</th><th title="Quanto precisa vender por dia útil restante para fechar em 100%">R$/dia p/ 100%</th></tr>
          </thead>
          <tbody>${unitRows(applyTableSort(state.dashboard.unitPerformance || [], "unidades"))}</tbody>
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

/**
 * Blocos operacionais da gestão: alertas da unidade e clientes em risco.
 * Ficam no fim do Executivo para quem tem escopo de gestão — são acionáveis
 * no dia a dia e não existiam na visão consolidada.
 */
function managementOperationalBlocks() {
  const alerts = buildManagementAlerts();
  const clientsAtRisk = (state.crm.clients || []).filter((item) => item.statusCode !== "ATIVO").slice(0, 6);
  return `
    <div class="grid-2">
      <div class="table-card">
        <div class="section-title">
          <div><h3>Alertas da unidade</h3><div class="text-small">Pontos que pedem ação da gestão.</div></div>
          <span class="soft-badge">${number(alerts.length)}</span>
        </div>
        <div class="alert-grid">${alerts.map(managementAlertCard).join("") || emptyStateCard("Nenhum alerta relevante no momento.")}</div>
      </div>
      <div class="table-card">
        <div class="section-title">
          <div><h3>Clientes em risco</h3><div class="text-small">Inativos e pré-inativos no recorte atual.</div></div>
          <span class="soft-badge">${number(clientsAtRisk.length)}</span>
        </div>
        <div class="timeline-list">
          ${clientsAtRisk.map((item) => `<div class="timeline-item"><strong>${escapeHtml(item.clientName)}</strong><div class="text-small">${escapeHtml(item.statusCode)} · ${escapeHtml(item.primaryReason || "-")}</div><div class="actions"><button class="btn btn-secondary" onclick="openCrmClient('${escapeHtml(item.clientKey)}', false)">Ver cliente</button></div></div>`).join("") || '<div class="timeline-item"><div class="text-small">Sem clientes em risco no recorte.</div></div>'}
        </div>
      </div>
    </div>`;
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
  const tipos = ai?.types || [];

  function statusIcon(s) {
    return s === "sucesso" ? "✅" : s === "erro" ? "❌" : s === "alerta" ? "⚠️" : "⏳";
  }

  function folderCard(f) {
    const hasPending = f.pendingFiles.length > 0;
    const icons = { sales: "📊", cost: "💰", crm_clients: "👥", crm_summary: "🧾", crm: "👥",
                    warranty: "↩️", catalog: "🏷️", stock: "📦" };
    return `
      <div style="background:var(--surface);border:1px solid var(--line);border-radius:10px;padding:14px 16px">
        <div style="display:flex;align-items:center;gap:8px;margin-bottom:6px">
          <span style="font-size:18px">${icons[f.scope] || "📁"}</span>
          <strong style="font-size:13px">${escapeHtml(f.label)}</strong>
          ${hasPending ? `<span class="soft-badge" style="background:#f39c12;color:#fff">${f.pendingFiles.length} pendente${f.pendingFiles.length > 1 ? "s" : ""}</span>` : `<span class="soft-badge">Vazia</span>`}
        </div>
        <div style="font-size:11px;color:var(--muted);margin-bottom:6px;word-break:break-all">${escapeHtml(f.folder)}/</div>
        ${(f.types || []).map(selosDoTipo).join("")}
        ${f.hint ? `<div style="font-size:11px;color:var(--muted);margin:6px 0;line-height:1.4">${escapeHtml(f.hint)}</div>` : ""}
        ${hasPending ? `<div style="font-size:12px;color:var(--accent)">${f.pendingFiles.map((n) => `📄 ${escapeHtml(n)}`).join("<br>")}</div>` : ""}
      </div>`;
  }

  const recentLogs = logs.slice(0, 10);

  return `
    <div class="form-card">
      <div class="section-title">
        <div>
          <h3>🤖 Auto-Import</h3>
          <div class="text-small">Coloque o CSV na pasta correspondente — o sistema verifica automaticamente a cada ${ai?.intervalMinutes || 60} minutos. Use "Importar agora" para antecipar.</div>
        </div>
        <div style="display:flex;gap:8px">
          <button class="btn btn-primary btn-sm" id="btn-auto-import-run" onclick="runAutoImportNow()">▶ Importar agora</button>
          ${botaoAtualizar("statusImport", "loadAutoImportStatus()", { mensagem: "Status da importação atualizado." })}
        </div>
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
                <td style="font-size:12px;color:${l.status === "erro" ? "var(--bad)" : l.status === "alerta" ? "#e67e22" : "inherit"}">${escapeHtml(l.message || "")}</td>
              </tr>`).join("")}
          </tbody>
        </table>
      </div>` : `<div class="message">Nenhum import automático registrado ainda.</div>`}
      `}
    </div>`;
}

// Cor por política: substituir apaga o que estava lá, acrescentar não. Quem vai
// largar um arquivo na pasta precisa saber disso ANTES, não depois.
const CORES_POLITICA = {
  base:        { fundo: "#fdecea", texto: "#c0392b", rotulo: "SUBSTITUI TUDO" },
  competencia: { fundo: "#fef7e0", texto: "#b9770e", rotulo: "SUBSTITUI O MÊS" },
  acrescenta:  { fundo: "#e6f4ea", texto: "#1e8449", rotulo: "ACRESCENTA" },
};

function dataBr(iso) {
  const t = String(iso || "").slice(0, 10);
  if (/^\d{4}-\d{2}-\d{2}$/.test(t)) return `${t.slice(8,10)}/${t.slice(5,7)}/${t.slice(0,4)}`;
  if (/^\d{4}-\d{2}$/.test(String(iso || "").slice(0, 7))) return String(iso).slice(0, 7);
  return t || "—";
}

function selosDoTipo(t) {
  const c = CORES_POLITICA[t.policy] || CORES_POLITICA.acrescenta;
  const ate = t.dataThrough ? dataBr(t.dataThrough) : "";
  return `
    <div style="display:flex;align-items:center;gap:6px;flex-wrap:wrap;margin:4px 0">
      <span style="background:${c.fundo};color:${c.texto};border-radius:10px;padding:2px 8px;
                   font-size:10px;font-weight:800;letter-spacing:0.03em">${c.rotulo}</span>
      <span style="font-size:11px;color:var(--muted)">
        ${escapeHtml(t.label)}${ate ? ` · até <strong>${ate}</strong>` : " · <em>sem dados</em>"}
      </span>
    </div>`;
}

function guiaDeImportacao(tipos) {
  if (!tipos.length) return "";
  return `
    <div class="form-card">
      <div class="section-title">
        <div>
          <h3>O que cada arquivo faz na base</h3>
          <div class="text-small">
            Substituir apaga o que já estava e põe o do arquivo no lugar; acrescentar soma ao
            histórico e descarta linha repetida. A data é a do <strong>dado</strong>, não a do
            arquivo — importar relatório velho não deixa a base nova.
          </div>
        </div>
      </div>
      <div class="table-wrap">
        <table class="table">
          <thead>
            <tr>
              <th>Arquivo</th><th>O que faz</th><th>Dados até</th>
              <th>Último mês</th><th style="text-align:right">Linhas</th>
            </tr>
          </thead>
          <tbody>
            ${tipos.map((t) => {
              const c = CORES_POLITICA[t.policy] || CORES_POLITICA.acrescenta;
              const vazio = !t.rows;
              return `
                <tr${vazio ? ' style="opacity:0.65"' : ""}>
                  <td><strong>${escapeHtml(t.label)}</strong></td>
                  <td><span style="background:${c.fundo};color:${c.texto};border-radius:10px;
                        padding:2px 8px;font-size:10px;font-weight:800">${c.rotulo}</span>
                    <span class="text-small" style="color:var(--muted)"> ${escapeHtml(t.policyLabel)}</span></td>
                  <td>${t.dataThrough ? dataBr(t.dataThrough) : "—"}</td>
                  <td>${t.lastCompetence || "—"}</td>
                  <td style="text-align:right">${vazio
                    ? '<span class="text-small" style="color:var(--bad)">nada importado</span>'
                    : number(t.rows)}</td>
                </tr>`;
            }).join("")}
          </tbody>
        </table>
      </div>
    </div>`;
}

async function loadSellerTargets() {
  const mes = state.filters.competenceEnd || state.filters.competenceStart || "";
  try {
    state.sellerTargets = await api(`/api/seller-targets?competence=${encodeURIComponent(mes)}`);
  } catch (e) {
    state.sellerTargets = { error: e.message, sellers: [] };
  }
  state.sellerTargetEdits = {};
  requestRender();
  return state.sellerTargets;
}

function editarMeta(nome, campo, valor) {
  state.sellerTargetEdits = state.sellerTargetEdits || {};
  const atual = state.sellerTargetEdits[nome] || {};
  atual[campo] = valor;
  state.sellerTargetEdits[nome] = atual;
  // Sem requestRender: repintar a cada tecla tiraria o foco do campo.
}

function preencherMetasSugeridas() {
  const d = state.sellerTargets;
  if (!d?.sellers) return;
  state.sellerTargetEdits = state.sellerTargetEdits || {};
  // Só preenche quem está vazio. Meta já cadastrada é decisão tomada — a
  // sugestão não passa por cima dela.
  d.sellers.forEach((s) => {
    if (s.hasTargets) return;
    state.sellerTargetEdits[s.sellerName] = {
      mixTarget: s.suggestedMix ?? "",
      marginTarget: s.suggestedMargin ?? "",
      marginTargetMid: s.suggestedMarginMid ?? "",
      marginTargetTop: s.suggestedMarginTop ?? "",
      callsTarget: s.suggestedCalls ?? "",
    };
  });
  requestRender();
  addMessage("success", "Sugestões preenchidas. Ajuste o que for diferente e salve.");
}

async function salvarMetasVendedor() {
  const d = state.sellerTargets;
  if (!d?.sellers) return;
  const edits = state.sellerTargetEdits || {};
  const linhas = d.sellers.map((s) => {
    const e = edits[s.sellerName] || {};
    return {
      sellerName: s.sellerName,
      mixTarget: e.mixTarget !== undefined ? e.mixTarget : s.mixTarget,
      marginTarget: e.marginTarget !== undefined ? e.marginTarget : s.marginTarget,
      marginTargetMid: e.marginTargetMid !== undefined ? e.marginTargetMid : s.marginTargetMid,
      marginTargetTop: e.marginTargetTop !== undefined ? e.marginTargetTop : s.marginTargetTop,
      callsTarget: e.callsTarget !== undefined ? e.callsTarget : s.callsTarget,
    };
  }).filter((l) => l.mixTarget != null || l.marginTarget != null || l.callsTarget != null);
  if (!linhas.length) return addMessage("error", "Nenhuma meta preenchida para salvar.");
  try {
    const r = await api("/api/seller-targets/save", {
      method: "POST", body: JSON.stringify({ sellers: linhas }) });
    addMessage("success", r.message || "Metas salvas.");
    await loadSellerTargets();
  } catch (e) {
    addMessage("error", "Não foi possível salvar: " + e.message);
  }
}

async function loadAwards(silencioso) {
  const f = state.awardFilters || {};
  const q = new URLSearchParams();
  if (f.from) q.set("from", f.from);
  if (f.to) q.set("to", f.to);
  if (!silencioso) { state.ui.loading.awards = true; requestRender(); }
  try {
    state.awards = await api(`/api/awards?${q.toString()}`);
    if (!f.from && state.awards.from) {
      state.awardFilters = { from: state.awards.from, to: state.awards.to };
    }
  } catch (e) {
    state.awards = { error: e.message, sellers: [] };
  }
  state.ui.loading.awards = false;
  requestRender();
  return state.awards;
}

function setAwardPeriod(campo, valor) {
  state.awardFilters = { ...(state.awardFilters || {}), [campo]: valor };
  const f = state.awardFilters;
  // Intervalo invertido não é erro do usuário, é ordem trocada: arruma sozinho.
  if (f.from && f.to && f.from > f.to) {
    state.awardFilters = { from: f.to, to: f.from };
  }
  // Trocar de período NÃO exige salvar nada. Lançamento é por mês, então o que
  // estava digitado e não foi salvo pertence ao mês anterior e é descartado —
  // carregá-lo para o mês novo gravaria ponto no lugar errado.
  state.awardEdits = {};
  loadAwards();
}

function editarLancamento(nome, campo, valor) {
  state.awardEdits = state.awardEdits || {};
  state.awardEdits[nome] = { ...(state.awardEdits[nome] || {}), [campo]: valor };
}

async function salvarLancamentos() {
  const d = state.awards;
  const edits = state.awardEdits || {};
  const nomes = Object.keys(edits);
  if (!nomes.length) return addMessage("error", "Nada alterado para lançar.");
  if (d.competences?.length !== 1) {
    return addMessage("error", "Lançamento é por mês. Escolha um mês só no período.");
  }
  try {
    const r = await api("/api/awards/manual", {
      method: "POST",
      body: JSON.stringify({
        competence: d.competences[0],
        sellers: nomes.map((n) => ({ sellerName: n, ...edits[n] })),
      }),
    });
    addMessage("success", r.message || "Lançamentos gravados.");
    state.awardEdits = {};
    await loadAwards(true);
  } catch (e) {
    addMessage("error", "Não foi possível lançar: " + e.message);
  }
}

// As duas porcentagens que decidem quem recebe. O documento tem três gatilhos:
// unidade em 95%, individual em 90% (que só valem juntos) e individual em 105%
// (que vale sozinho). Mostrar o número sem o gatilho ao lado obriga quem lê a
// lembrar de cor qual era o corte de cada um.
function gatilhoMeta(rotulo, valor, corte, corteSozinho) {
  if (valor === null || valor === undefined) {
    return `<div><span class="text-small" style="color:var(--muted)">${rotulo}: sem meta</span></div>`;
  }
  const passouSozinho = corteSozinho !== null && valor >= corteSozinho;
  const passou = valor >= corte;
  const cor = passouSozinho ? "var(--good)" : passou ? "#e67e22" : "var(--bad)";
  const marca = passouSozinho ? "✓✓" : passou ? "✓" : "✕";
  return `
    <div style="display:flex;align-items:baseline;gap:5px">
      <span class="text-small" style="color:var(--muted)">${rotulo}</span>
      <strong style="color:${cor};font-size:14px">${valor.toFixed(1)}%</strong>
      <span style="color:${cor};font-size:11px;font-weight:700">${marca}</span>
      <span class="text-small" style="color:var(--muted)">
        (corte ${corte}%${corteSozinho ? ` · sozinho ${corteSozinho}%` : ""})</span>
    </div>`;
}

function barraPontos(pontos, maximo) {
  const pct = maximo ? Math.min(100, (100 * pontos) / maximo) : 0;
  const cor = pct >= 66 ? "var(--good)" : pct >= 40 ? "#e67e22" : "var(--bad)";
  return `<div style="background:var(--line);border-radius:6px;height:7px;width:110px;overflow:hidden">
    <div style="width:${pct.toFixed(0)}%;height:100%;background:${cor}"></div></div>`;
}

function cartaoIndicador(i) {
  const pct = i.max ? (100 * i.points) / i.max : 0;
  const cor = i.missing ? "var(--muted)" : pct >= 100 ? "var(--good)"
    : pct > 0 ? "#e67e22" : "var(--bad)";
  const v = i.value;
  const texto = v === null || v === undefined ? "—"
    : i.format === "pct" ? `${Number(v).toFixed(1)}%`
    : i.format === "ratio" ? Number(v).toFixed(4)
    : Number(v).toFixed(0);
  return `
    <div style="border:1px solid var(--line);border-left:3px solid ${cor};border-radius:0;
                padding:8px 10px;min-width:150px;flex:1">
      <div class="text-small" style="color:var(--muted)">${escapeHtml(i.label)}</div>
      <div style="display:flex;align-items:baseline;gap:6px">
        <strong style="font-size:16px">${texto}</strong>
        <span class="text-small" style="color:${cor};font-weight:700">
          ${i.points}/${i.max} pts</span>
      </div>
      <div class="text-small" style="color:var(--muted);line-height:1.35">
        ${i.missing ? "falta cadastrar/lançar" : escapeHtml(i.detail || "")}</div>
    </div>`;
}

// A folha de impressão é montada dentro da própria página, num container
// escondido que o @media print revela. É o mesmo caminho do roteiro de visitas:
// abrir janela nova esbarra em bloqueador de pop-up e perde o estilo.
function placarParaImpressao(d) {
  const f = state.awardFilters || { from: d.from, to: d.to };
  const periodo = f.from === f.to ? f.from : `${f.from} a ${f.to}`;
  const linha = (v) => {
    const s = v.single;
    const inds = s
      ? s.indicators.map((i) => `${i.label}: ${i.points}/${i.max}`).join(" · ")
      : `média de ${v.avgPoints} pontos por mês`;
    return `
      <div class="print-client">
        <div style="display:flex;justify-content:space-between;font-weight:bold">
          <span>${escapeHtml(v.sellerName)}</span>
          <span>${number(v.points)} pts · ${currency(v.value)}</span>
        </div>
        <div style="font-size:9pt;color:#333;margin:2px 0">
          ${escapeHtml(v.unitName || "sem unidade")} ·
          ${v.goalPct !== null ? `${v.goalPct.toFixed(1)}% da meta` : "sem meta"} ·
          ${currency(v.revenue)}
          ${s ? ` · ${escapeHtml(s.eligibilityReason || "")}` : ""}
        </div>
        <div style="font-size:9pt">${escapeHtml(inds)}</div>
      </div>`;
  };
  const porUnidade = {};
  (d.sellers || []).forEach((v) => {
    (porUnidade[v.unitName || "SEM UNIDADE"] ||= []).push(v);
  });
  return `
    <div class="print-area">
      <div class="print-header">
        <h1>Apuração da premiação</h1>
        <div class="sub">Período ${escapeHtml(periodo)} · cesta ${escapeHtml(d.basket || "")} ·
          ${number(d.totals?.sellers || 0)} vendedor(es) ·
          ${number(d.totals?.eligible || 0)} elegível(is) ·
          total ${currency(d.totals?.value || 0)}</div>
      </div>
      ${Object.keys(porUnidade).sort().map((un) => `
        <div class="print-bairro">${escapeHtml(un)}</div>
        ${porUnidade[un].map(linha).join("")}`).join("")}
    </div>`;
}

function placarEquipeView() {
  if (!state.awards) {
    if (!state.ui.loading.awards) loadAwards();
    return `<div class="loader panel">Apurando a premiação…</div>`;
  }
  const d = state.awards;
  if (d.error) return `<div class="message error">${escapeHtml(d.error)}</div>`;
  const f = state.awardFilters || { from: d.from, to: d.to };
  const meses = d.allCompetences || [];
  const mesUnico = (d.competences || []).length === 1;
  const edits = state.awardEdits || {};

  const seletor = (campo, valor) => `
    <select onchange="setAwardPeriod('${campo}', this.value)"
      style="padding:6px 10px;border:1px solid var(--line);border-radius:6px;font-size:13px">
      ${meses.map((m) => `<option value="${m}" ${m === valor ? "selected" : ""}>${m}</option>`).join("")}
    </select>`;

  return `
    <div class="stack">
      <div class="form-card">
        <div class="section-title">
          <div>
            <h3>Apuração da premiação</h3>
            <div class="text-small">
              Cesta ${escapeHtml(d.basket || "")} · ${(d.competences || []).length} mês(es) ·
              pontos e valores são somados mês a mês, porque cada mês tem a sua premiação.
            </div>
          </div>
          <div style="display:flex;gap:8px;align-items:center;flex-wrap:wrap">
            <span class="text-small">de</span>${seletor("from", f.from)}
            <span class="text-small">até</span>${seletor("to", f.to)}
            ${d.canInput && mesUnico
              ? `<button class="btn btn-primary btn-sm" onclick="salvarLancamentos()">
                   Salvar lançamentos</button>`
              : ""}
            <button class="btn btn-secondary btn-sm" onclick="window.print()">⬇ PDF</button>
          </div>
        </div>
        <div style="display:flex;gap:10px;flex-wrap:wrap">
          ${[["Vendedores", number(d.totals?.sellers || 0)],
             ["Elegíveis", number(d.totals?.eligible || 0)],
             ["Pontos somados", number(d.totals?.points || 0)],
             ["Premiação do período", currency(d.totals?.value || 0)]].map(([r, v]) => `
            <div style="flex:1;min-width:130px;background:var(--surface);border:1px solid var(--line);
                        border-radius:10px;padding:10px 12px">
              <div class="text-small" style="color:var(--muted)">${r}</div>
              <div style="font-size:20px;font-weight:800">${v}</div>
            </div>`).join("")}
        </div>
      </div>

      ${placarParaImpressao(d)}

      ${(d.sellers || []).map((v, idx) => {
        const s = v.single;
        const e = edits[v.sellerName] || {};
        return `
        <div class="form-card" style="padding:14px 18px">
          <div style="display:flex;gap:12px;align-items:center;flex-wrap:wrap">
            <div style="font-size:20px;font-weight:800;color:var(--muted);width:28px">${idx + 1}</div>
            <div style="flex:1;min-width:220px">
              <div style="font-weight:800">${escapeHtml(v.sellerName)}</div>
              <div class="text-small" style="color:var(--muted)">
                ${escapeHtml(v.unitName || "sem unidade")} · ${currency(v.revenue)}
              </div>
              ${s ? `
                <div style="display:flex;gap:14px;margin-top:5px;flex-wrap:wrap">
                  ${gatilhoMeta("Individual", s.goalPct, 90, 105)}
                  ${gatilhoMeta("Unidade", s.unitAttainment, 95, null)}
                </div>` : ""}
            </div>
            <div style="text-align:center">
              <div style="font-size:22px;font-weight:800">${number(v.points)}</div>
              <div class="text-small" style="color:var(--muted)">de ${number(v.maxPoints)} pts</div>
              ${barraPontos(v.points, v.maxPoints)}
            </div>
            <div style="text-align:right;min-width:120px">
              <div style="font-size:20px;font-weight:800;color:${v.value > 0 ? "var(--good)" : "var(--muted)"}">
                ${currency(v.value)}</div>
              <div class="text-small" style="color:var(--muted)">
                ${v.eligibleMonths}/${v.months.length} mês(es) elegível</div>
            </div>
          </div>
          ${s ? `
            <div class="text-small" style="color:var(--muted);margin:8px 0 6px">
              ${escapeHtml(s.eligibilityReason || "")}</div>
            <div style="display:flex;gap:8px;flex-wrap:wrap">
              ${s.indicators.map(cartaoIndicador).join("")}
            </div>
            ${d.canInput ? `
              <div style="display:flex;gap:10px;align-items:center;margin-top:10px;
                          padding-top:10px;border-top:1px solid var(--line)">
                <span class="text-small" style="color:var(--muted)">Lançar pontos:</span>
                <label class="text-small">EAD
                  <input type="text" inputmode="numeric" style="width:60px;margin-left:4px;padding:4px 6px;
                         border:1px solid var(--line);border-radius:6px"
                    value="${e.eadPoints ?? (s.indicators.find((x) => x.code === "ead")?.value ?? "")}"
                    oninput="editarLancamento('${v.sellerName.replace(/'/g, "\\'")}','eadPoints',this.value)"></label>
                <label class="text-small">Redes
                  <input type="text" inputmode="numeric" style="width:60px;margin-left:4px;padding:4px 6px;
                         border:1px solid var(--line);border-radius:6px"
                    value="${e.socialPoints ?? (s.indicators.find((x) => x.code === "redes")?.value ?? "")}"
                    oninput="editarLancamento('${v.sellerName.replace(/'/g, "\\'")}','socialPoints',this.value)"></label>
              </div>` : ""}
          ` : `
            <div class="text-small" style="color:var(--muted);margin-top:8px">
              Média de ${v.avgPoints} pontos por mês.
              ${v.points >= (d.highlightThreshold || 900)
                ? `<strong style="color:var(--good)">Acima dos ${d.highlightThreshold} pontos
                   do gatilho de Vendedor Destaque.</strong>` : ""}
            </div>`}
        </div>`;
      }).join("")}
      ${!(d.sellers || []).length
        ? `<div class="message">Nenhum vendedor com faturamento no período.</div>` : ""}
    </div>`;
}

// De qual campo da resposta sai o placeholder de cada coluna. Antes eu derivava
// o nome por manipulação de texto, o que quebrou assim que apareceu "marginTargetMid".
const SUGESTAO_POR_CAMPO = {
  mixTarget: "suggestedMix",
  marginTarget: "suggestedMargin",
  marginTargetMid: "suggestedMarginMid",
  marginTargetTop: "suggestedMarginTop",
  callsTarget: "suggestedCalls",
};

function metasVendedorView() {
  if (!state.sellerTargets) { loadSellerTargets(); return `<div class="loader panel">Carregando metas…</div>`; }
  const d = state.sellerTargets;
  if (d.error) return `<div class="message error">${escapeHtml(d.error)}</div>`;
  const edits = state.sellerTargetEdits || {};
  const sellers = d.sellers || [];
  const semMeta = sellers.filter((s) => !s.hasTargets).length;

  const campo = (s, nome, passo) => {
    const e = edits[s.sellerName] || {};
    const valor = e[nome] !== undefined ? e[nome] : (s[nome] ?? "");
    return `<input type="text" inputmode="decimal" value="${valor === null ? "" : valor}"
      placeholder="${SUGESTAO_POR_CAMPO[nome] ? (s[SUGESTAO_POR_CAMPO[nome]] ?? "") : ""}"
      oninput="editarMeta('${s.sellerName.replace(/'/g, "\\'")}','${nome}',this.value)"
      style="width:88px;text-align:right;padding:5px 8px;border:1px solid var(--line);
             border-radius:6px;font-size:13px">`;
  };

  return `
    <div class="stack">
      <div class="form-card">
        <div class="section-title">
          <div>
            <h3>Metas por vendedor</h3>
            <div class="text-small">
              Valem até você mudar — não precisa cadastrar todo mês. Em mês de férias,
              <strong>mix e ligações</strong> são reduzidos na proporção dos dias úteis
              trabalhados; a <strong>margem</strong> não muda, porque é qualidade da venda
              e não volume. <strong>Campo vazio significa sem meta, e sem meta o indicador
              não pontua.</strong>
            </div>
          </div>
          <div style="display:flex;gap:8px">
            <button class="btn btn-secondary btn-sm" onclick="preencherMetasSugeridas()">
              Preencher sugestões</button>
            <button class="btn btn-primary btn-sm" onclick="salvarMetasVendedor()">Salvar</button>
          </div>
        </div>
        ${semMeta ? `<div class="message" style="margin-bottom:10px">
          ${semMeta} vendedor(es) ainda sem meta cadastrada. Enquanto estiverem assim,
          eles não pontuam em mix, margem nem ligações.</div>` : ""}
        <div class="table-wrap">
          <table class="table">
            <thead>
              <tr>
                <th>Vendedor</th><th>Unidade</th><th>Tipo</th>
                <th style="text-align:right">Mix (itens)</th>
                <th style="text-align:right" title="Margem mínima para começar a pontuar">Margem 1</th>
                <th style="text-align:right">Margem 2</th>
                <th style="text-align:right" title="Pontuação cheia">Margem 3</th>
                <th style="text-align:right">Ligações</th>
                <th></th>
              </tr>
            </thead>
            <tbody>
              ${sellers.map((s) => `
                <tr>
                  <td><strong>${escapeHtml(s.sellerName)}</strong></td>
                  <td>${escapeHtml(s.unitName || "—")}</td>
                  <td><span class="text-small" style="color:var(--muted)">${
                    s.insideSales ? "televendas" : "balcão"}</span></td>
                  <td style="text-align:right">${campo(s, "mixTarget")}</td>
                  <td style="text-align:right">${campo(s, "marginTarget")}</td>
                  <td style="text-align:right">${campo(s, "marginTargetMid")}</td>
                  <td style="text-align:right">${campo(s, "marginTargetTop")}</td>
                  <td style="text-align:right">${campo(s, "callsTarget")}</td>
                  <td>${s.hasTargets
                    ? `<span class="soft-badge">cadastrada</span>`
                    : `<span class="soft-badge" style="background:#fdecea;color:#c0392b">sem meta</span>`}</td>
                </tr>`).join("")}
            </tbody>
          </table>
        </div>
      </div>
    </div>`;
}

function importacoesView() {
  if (!state.admin) return `<div class="loader panel">Carregando importações...</div>`;
  if (!state.autoImport) loadAutoImportStatus();
  return `
    <div class="stack">
      ${autoImportPanel()}
      ${guiaDeImportacao(state.autoImport?.types || [])}
      ${(() => {
        const cov = state.admin?.salesCoverage;
        const fmt = (iso) => { if (!iso) return "—"; const d = String(iso).slice(0, 10).split("-"); return d.length === 3 ? `${d[2]}/${d[1]}/${d[0]}` : iso; };
        if (!cov || !cov.total) return `<div class="message">Faturamento detalhado: base vazia (nenhum dado importado ainda).</div>`;
        return `<div class="form-card"><div class="section-title"><div><h3>Cobertura do faturamento detalhado</h3><div class="text-small">Período que a base de faturamento detalhado abrange.</div></div></div><div style="font-size:15px">De <strong>${fmt(cov.min)}</strong> até <strong>${fmt(cov.max)}</strong> · <strong>${Number(cov.total || 0).toLocaleString("pt-BR")}</strong> linhas.</div></div>`;
      })()}
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

            <div class="form-card subtle-card">
              <div class="section-title"><div><h3>Produtos</h3>
                <div class="text-small">Cadastro de itens e posição de estoque. Nenhum dos dois
                  tem competência — cada envio atualiza a fotografia atual.</div></div></div>
              <div class="stack">
                <div class="two-column-form">
                  <div class="field">
                    <label>Cadastro de itens</label>
                    <input id="import-catalog-file" type="file" accept=".csv" />
                    <div class="text-small" style="color:var(--muted);margin-top:4px">
                      Traz a <strong>linha do produto</strong> (amortecedor, kit de embreagem,
                      filtro), a marca e o preço. Reenvie quando entrar linha nova.
                    </div>
                  </div>
                  <div class="field">
                    <label>Posição de estoque</label>
                    <input id="import-stock-file" type="file" accept=".xlsx,.csv" />
                    <div class="text-small" style="color:var(--muted);margin-top:4px">
                      Saldo <strong>por unidade</strong>, giro F1–F4 e curva ABC de cada filial.
                      É o arquivo do Alfa em xlsx. Atualizar 1x ao dia.
                    </div>
                  </div>
                </div>
                <div class="actions">
                  <button class="btn btn-secondary" onclick="previewImport('catalog')">Analisar itens</button>
                  <button class="btn btn-primary" onclick="submitImport('catalog')">Importar itens</button>
                  <span style="width:12px"></span>
                  <button class="btn btn-secondary" onclick="previewImport('stock')">Analisar estoque</button>
                  <button class="btn btn-primary" onclick="submitImport('stock')">Importar estoque</button>
                </div>
                <div id="import-catalog-feedback" class="text-small"></div>
                <div id="import-stock-feedback" class="text-small"></div>
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
                  <option value="cidade-unidade">Cidades × Unidade</option>
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

function adminEditorCards() {
  const UNITS = ["MATRIZ", "LAJEADO", "PELOTAS", "ZONA SUL", "ZONA NORTE", "XANGRILA"];
  const unitOptions = UNITS.map((u) => `<option value="${u}">${u}</option>`).join("");
  const people = state.admin?.people || [];
  const cities = state.admin?.cityMappings || [];
  const issues = state.admin?.issues || [];
  const sellerNames = [
    ...people.map((p) => p.person_name),
    ...(state.admin?.salesSellers || []),
    ...issues.filter((i) => i.issue_type === "vendedor_sem_vinculo").map((i) => i.reference_value),
  ].filter(Boolean);
  const cityNames = [
    ...cities.map((c) => c.city_name),
    ...(state.admin?.salesCities || []),
    ...issues.filter((i) => i.issue_type === "cidade_sem_correspondencia").map((i) => i.reference_value),
  ].filter(Boolean);
  const sellerOpts = [...new Set(sellerNames)].sort().map((n) => `<option value="${escapeHtml(n)}"></option>`).join("");
  const cityOpts = [...new Set(cityNames)].sort().map((n) => `<option value="${escapeHtml(n)}"></option>`).join("");
  const peopleNames = new Set(people.map((p) => p.person_name));
  const pendingSellers = [...new Set((state.admin?.salesSellers || []).filter((n) => n && !peopleNames.has(n)))].sort();
  return `
    <div class="grid-2">
      <div class="form-card">
        <div class="section-title">
          <div><h3>Cadastrar pessoa</h3>
            <div class="text-small">Para quem ainda não apareceu no faturamento — vendedor de
              unidade nova, por exemplo. Aqui a função é definida, não adivinhada pelo nome.</div></div>
        </div>
        <div class="two-column-form">
          <div class="field"><label>Nome completo</label>
            <input id="new-person-name" placeholder="Como aparece (ou vai aparecer) no faturamento" /></div>
          <div class="field"><label>Função</label>
            <select id="new-person-role">
              <option value="Vendedor">Vendedor</option>
              <option value="Gerente">Gerente</option>
              <option value="Outro">Outro (não entra em metas nem ranking)</option>
            </select></div>
          <div class="field"><label>Unidade</label><select id="new-person-unit">${unitOptions}</select></div>
          <div class="field"><label>Válido a partir de</label>
            <input type="date" id="new-person-from" value="${dateInDays(0)}" /></div>
        </div>
        <div class="actions"><button class="btn btn-primary" onclick="submitNewPerson()">Cadastrar pessoa</button></div>
        <div class="text-small" style="color:var(--muted);margin-top:8px">
          Dica: use exatamente o nome que virá do Alfa quando ele começar a faturar — assim o
          histórico dele não fica dividido em dois cadastros.
        </div>
      </div>

      <div class="form-card">
        <div class="section-title">
          <div><h3>Desligamento</h3>
            <div class="text-small">Fecha a vigência da pessoa. O histórico é preservado —
              ela some das listas de equipe, meta e presença dos meses seguintes.</div></div>
        </div>
        <div class="two-column-form">
          <div class="field"><label>Pessoa</label>
            <input id="term-person-name" list="term-person-options" placeholder="Digite o nome" />
            <datalist id="term-person-options">
              ${/* Inclui quem só aparece no faturamento ou no cadastro de clientes.
                    Quem saiu antes de existir cadastro de pessoas não estava aqui,
                    e por isso não havia como registrar o desligamento. */""}
              ${[...new Set([
                  ...(state.admin?.people || []).filter((p) => !p.valid_to).map((p) => p.person_name),
                  ...(state.admin?.salesSellers || []),
                  ...(state.admin?.clientSellers || []),
                ].filter(Boolean))]
                .filter((n) => !(state.admin?.people || []).some((p) => p.person_name === n && p.valid_to))
                .sort((a, b) => a.localeCompare(b, "pt-BR"))
                .map((n) => `<option value="${escapeHtml(n)}"></option>`).join("")}
            </datalist></div>
          <div class="field"><label>Mês de desligamento</label>
            <input type="month" id="term-person-month" value="${new Date().toISOString().slice(0,7)}" /></div>
        </div>
        <div class="actions">
          <button class="btn btn-primary" onclick="submitPersonTermination()">Registrar desligamento</button>
          <button class="btn btn-ghost" onclick="submitPersonTermination(true)">Reativar</button>
        </div>
        <div class="text-small" style="color:var(--muted);margin-top:8px">
          A conta de acesso vinculada também é desativada. Nada é apagado: os meses em que a
          pessoa trabalhou continuam intactos no histórico e nos relatórios.
        </div>
        ${(state.admin?.people || []).some((p) => p.valid_to) ? `
          <div class="text-small" style="font-weight:600;margin-top:10px">Já desligados:</div>
          <div style="display:flex;gap:6px;flex-wrap:wrap;margin-top:4px">
            ${[...new Map((state.admin.people || []).filter((p) => p.valid_to)
                .map((p) => [p.person_name, p])).values()]
              .map((p) => `<span class="status-tag" title="até ${escapeHtml(p.valid_to)}">${escapeHtml(p.person_name)} · ${escapeHtml(String(p.valid_to).slice(0,7))}</span>`).join("")}
          </div>` : ""}
      </div>

      <div class="form-card">
        <div class="section-title"><div><h3>Ajustar vendedor × unidade</h3><div class="text-small">Busque o vendedor pelo nome e defina a unidade correta.</div></div></div>
        <div class="two-column-form">
          <div class="field"><label>Vendedor</label><input id="edit-seller-name" list="sellers-datalist" placeholder="Digite o nome" /></div>
          <div class="field"><label>Unidade</label><select id="edit-seller-unit">${unitOptions}</select></div>
        </div>
        <div class="actions"><button class="btn btn-primary" onclick="submitPersonUnit()">Salvar vendedor</button></div>
        ${pendingSellers.length
          ? `<div class="text-small" style="margin-top:10px;font-weight:600">Vendedores sem unidade (${pendingSellers.length}) — clique para preencher:</div>
        <div style="display:flex;flex-wrap:wrap;gap:6px;margin-top:6px">${pendingSellers.slice(0, 60).map((n) => `
            <span style="display:inline-flex;align-items:center;border:1px solid var(--line);border-radius:8px;overflow:hidden">
              <button type="button" class="btn btn-ghost btn-sm" style="border:none;border-radius:0"
                onclick="document.getElementById('edit-seller-name').value='${jsAttr(n)}';document.getElementById('edit-seller-name').focus()">${escapeHtml(n)}</button>
              <button type="button" class="btn btn-ghost btn-sm" style="border:none;border-radius:0;border-left:1px solid var(--line);color:var(--bad)"
                title="Não trabalha mais na Passini — registrar desligamento"
                onclick="prepararDesligamento('${jsAttr(n)}')">saiu</button>
            </span>`).join("")}</div>
        <div class="text-small" style="color:var(--muted);margin-top:6px">
          Clique no nome para definir a unidade, ou em <strong>saiu</strong> para registrar o desligamento.
        </div>`
          : `<div class="text-small" style="margin-top:10px;color:var(--muted)">Nenhum vendedor sem unidade. ✅</div>`}
        <datalist id="sellers-datalist">${sellerOpts}</datalist>
      </div>
      <div class="form-card">
        <div class="section-title"><div><h3>Ajustar cidade × unidade</h3><div class="text-small">Busque a cidade pelo nome e defina a unidade correta.</div></div></div>
        <div class="two-column-form">
          <div class="field"><label>Cidade</label><input id="edit-city-name" list="cities-datalist" placeholder="Digite a cidade" /></div>
          <div class="field"><label>Unidade</label><select id="edit-city-unit">${unitOptions}</select></div>
        </div>
        <div class="actions"><button class="btn btn-primary" onclick="submitCityUnit()">Salvar cidade</button></div>
        <datalist id="cities-datalist">${cityOpts}</datalist>
      </div>
    </div>
  `;
}

function territoriosView() {
  if (state.ui.loading.territories) return `<div class="loader panel">Carregando territórios...</div>`;
  const dados = state.territories;
  if (!dados) return `<div class="loader panel">Carregando territórios...</div>`;

  const todos = dados.territories || [];
  const unidades = [...(dados.units || []), dados.sharedLabel || "COMPARTILHADA"];
  const cidades = [...new Set(todos.map((t) => t.city_name))].sort((a, b) => a.localeCompare(b, "pt-BR"));
  const cidadeFiltro = state.ui.territoryCity;
  const lista = cidadeFiltro ? todos.filter((t) => t.city_name === cidadeFiltro) : todos;
  const faltando = dados.coverage?.missing || [];
  const draft = state.ui.territoryDraft;

  const badgeUnidade = (u) => u === (dados.sharedLabel || "COMPARTILHADA")
    ? `<span class="soft-badge" style="background:#eef1f4;color:#5b6b76">compartilhada</span>`
    : `<span class="soft-badge">${escapeHtml(u)}</span>`;

  return `
    <div class="stack">
      <div class="form-card">
        <div class="section-title">
          <div>
            <h3>Territórios</h3>
            <div class="text-small">Quem é dono de cada bairro e cidade.</div>
          </div>
          <button class="btn btn-primary btn-sm" type="button" onclick="novoTerritorio()">+ Adicionar</button>
        </div>
        <div class="text-small" style="color:var(--muted);line-height:1.6">
          Porto Alegre tem duas unidades, então a cidade sozinha não diz mais de quem é o cliente.
          Este mapa <strong>decide a prospecção, o agrupamento do roteiro de visita e o território
          mostrado na ficha</strong>. Ele <strong>não decide faturamento</strong>: a venda continua
          contando para a unidade do vendedor que a fez.
          Cidade marcada como <em>compartilhada</em> é de propósito — quem manda ali é o vendedor
          que já atende o cliente.
        </div>
      </div>

      ${faltando.length ? `
      <div class="form-card">
        <div class="section-title">
          <div><h3>Bairros sem dono</h3>
          <div class="text-small">Têm cliente na base, mas caíram na regra da cidade. ${dados.coverage.total} no total.</div></div>
        </div>
        <div class="table-wrap">
          <table>
            <thead><tr><th>Cidade</th><th>Bairro</th><th style="text-align:right">Clientes</th><th></th></tr></thead>
            <tbody>
              ${faltando.slice(0, 25).map((f) => `
                <tr>
                  <td class="text-small">${escapeHtml(f.city)}</td>
                  <td class="text-small"><strong>${escapeHtml(f.neighborhood)}</strong></td>
                  <td class="text-small" style="text-align:right">${number(f.clients)}</td>
                  <td style="text-align:right">
                    <button class="btn btn-ghost btn-sm" type="button"
                      onclick="novoTerritorio('${jsAttr(f.city)}','${jsAttr(f.neighborhood)}')">Mapear</button>
                  </td>
                </tr>`).join("")}
            </tbody>
          </table>
        </div>
      </div>` : ""}

      ${draft ? `
      <div class="form-card">
        <div class="section-title">
          <div><h3>${draft.id ? "Editar território" : "Novo território"}</h3></div>
          <button class="btn btn-ghost btn-sm" type="button" onclick="fecharTerritorio()">Cancelar</button>
        </div>
        <div class="two-column-form">
          <div class="field">
            <label>Cidade</label>
            <input value="${escapeHtml(draft.cityName)}" oninput="state.ui.territoryDraft.cityName=this.value" />
          </div>
          <div class="field">
            <label>Bairro <span style="color:var(--muted);font-weight:400">(vazio = cidade inteira)</span></label>
            <input value="${escapeHtml(draft.neighborhood)}" oninput="state.ui.territoryDraft.neighborhood=this.value" />
          </div>
          <div class="field">
            <label>Unidade</label>
            <select onchange="state.ui.territoryDraft.unitName=this.value">
              <option value="">Selecione…</option>
              ${unidades.map((u) => `<option value="${escapeHtml(u)}" ${draft.unitName === u ? "selected" : ""}>${escapeHtml(u)}</option>`).join("")}
            </select>
          </div>
          <div class="field">
            <label>Vale a partir de</label>
            <input type="date" value="${escapeHtml(draft.validFrom)}" onchange="state.ui.territoryDraft.validFrom=this.value" />
          </div>
          <div class="field field-span-2">
            <label>Observação</label>
            <input value="${escapeHtml(draft.notes || "")}" oninput="state.ui.territoryDraft.notes=this.value" />
          </div>
        </div>
        <div class="actions">
          <button class="btn btn-primary" type="button" onclick="salvarTerritorio()">Salvar território</button>
        </div>
      </div>` : ""}

      <div class="form-card">
        <div class="section-title">
          <div><h3>Mapa atual</h3><div class="text-small">${lista.length} de ${todos.length} registros.</div></div>
          <select onchange="setTerritoryCity(this.value)" style="max-width:240px">
            <option value="">Todas as cidades</option>
            ${cidades.map((c) => `<option value="${escapeHtml(c)}" ${cidadeFiltro === c ? "selected" : ""}>${escapeHtml(c)}</option>`).join("")}
          </select>
        </div>
        <div class="table-wrap">
          <table>
            <thead><tr><th>Cidade</th><th>Bairro</th><th>Unidade</th><th>Desde</th><th>Origem</th><th style="text-align:right">Ações</th></tr></thead>
            <tbody>
              ${lista.length ? lista.map((t) => `
                <tr>
                  <td class="text-small">${escapeHtml(t.city_name)}</td>
                  <td class="text-small">${t.neighborhood === "*"
                      ? '<em style="color:var(--muted)">toda a cidade</em>'
                      : `<strong>${escapeHtml(t.neighborhood)}</strong>`}</td>
                  <td>${badgeUnidade(t.unit_name)}</td>
                  <td class="text-small">${escapeHtml(t.valid_from)}</td>
                  <td class="text-small" style="color:var(--muted)">${escapeHtml(t.source)}</td>
                  <td style="text-align:right;white-space:nowrap">
                    <button class="btn btn-ghost btn-sm" type="button" onclick="editarTerritorio(${Number(t.id)})">Editar</button>
                    <button class="btn btn-ghost btn-sm" type="button" onclick="excluirTerritorio(${Number(t.id)})">Excluir</button>
                  </td>
                </tr>`).join("")
                : '<tr><td colspan="6" class="text-small">Nenhum território mapeado.</td></tr>'}
            </tbody>
          </table>
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
        <button class="btn ${section === "territorios" ? "btn-primary" : "btn-ghost"}" onclick="setAdminSection('territorios')">Territórios</button>
        <button class="btn ${section === "auditoria-integridade" ? "btn-primary" : "btn-ghost"}" onclick="setAdminSection('auditoria-integridade')">Auditoria de Integridade</button>
      </div>
    </div>
  `;
  if (section === "auditoria-integridade") {
    return `<div class="stack">${adminSectionNav}${integrityAuditView()}</div>`;
  }
  if (section === "territorios") {
    return `<div class="stack">${adminSectionNav}${territoriosView()}</div>`;
  }
  return `
    <div class="stack">
      ${adminSectionNav}
      ${adminEditorCards()}
      <div class="form-card">
        <div class="section-title"><div><h3>Pendências</h3><div class="text-small">Resolva vínculos e correspondências sem abrir telas gigantes.</div></div></div>
        <div class="stack">${cidadesPendentesEmLote()}${pendingIssueCards()}</div>
      </div>
      ${userCanManageUsers() ? `
      <div class="form-card">
        <div class="section-title">
          <div><h3>Usuários e permissões</h3>
          <div class="text-small">A gestão de contas e perfis fica em uma tela dedicada.</div></div>
          <button class="btn btn-primary btn-sm" onclick="switchTab('acessos')">Abrir Usuários e Perfis →</button>
        </div>
      </div>` : ""}
      <div class="grid-2">
        ${personEditorCard()}
        ${adminTableCard("Cadastros de pessoas", ["person_name", "role_classification", "base_unit", "valid_from", "valid_to", "source"], state.admin.people)}
      </div>
      <div class="grid-2">
        ${adminTableCard("Base de clientes PF/PJ", ["client_name", "document_number", "person_type", "source", "confidence_score", "notes"], state.admin.clients)}
        ${adminTableCard("Mapeamento de cidades", ["city_name", "principal_unit", "valid_from", "valid_to", "source"], state.admin.cityMappings || [])}
      </div>
      <div class="grid-2">
        ${adminTableCard("Pendências de importação", ["issue_type", "reference_value", "status", "competence"], state.admin.issues)}
        ${adminTableCard("Auditoria", ["entity_type", "action", "entity_id", "created_at"], state.admin.audit)}
      </div>
    </div>
  `;
};

function userEditorCard() {
  const profiles = accessProfiles();
  const editor = state.userEditor;
  const passwordLabel = editor.id ? "Nova senha (deixe vazio para manter)" : "Senha inicial";
  const submitLabel = editor.id ? "Salvar ajustes" : "Criar usuário";
  const title = editor.id ? `Editar usuário: ${escapeHtml(editor.username)}` : "Novo usuário";
  const scope = selectedUserProfileScope();
  const unidadesDisponiveis = unitOptionsForEditor();
  const chosen = accessProfileById(editor.profileId);
  const scopeInfo = (state.admin?.dataScopes || []).find((s) => s.id === scope);

  return `
    <div class="form-card" id="user-editor-card">
      <div class="section-title">
        <div><h3>${title}</h3>
        <div class="text-small">O perfil define as telas que a pessoa acessa e o alcance dos dados.</div></div>
        ${editor.id ? '<button class="btn btn-ghost btn-sm" type="button" onclick="cancelUserEdit()">Cancelar</button>' : ""}
      </div>
      <form onsubmit="saveUser(event)" class="stack">
        <input id="user-id" type="hidden" value="${escapeHtml(editor.id)}" />
        <div class="two-column-form">
          <div class="field">
            <label>Login</label>
            <input id="user-username" value="${escapeHtml(editor.username)}" oninput="state.userEditor.username=this.value" required />
          </div>
          <div class="field">
            <label>Nome completo</label>
            <input id="user-full-name" value="${escapeHtml(editor.fullName)}" oninput="state.userEditor.fullName=this.value" required />
          </div>
          <div class="field field-span-2">
            <label>Perfil de acesso</label>
            <select id="user-profile" onchange="setUserProfile(this.value)" required>
              <option value="">Selecione o perfil…</option>
              ${profiles.map((p) => `<option value="${p.id}" ${String(editor.profileId) === String(p.id) ? "selected" : ""}>${escapeHtml(p.name)}</option>`).join("")}
            </select>
            ${chosen ? `<div class="text-small" style="margin-top:6px;color:var(--muted)">
              ${escapeHtml(chosen.description || "")}
              <br><strong>${chosen.modules.length} tela(s)</strong> · ${escapeHtml(scopeInfo ? scopeInfo.label : scope)}${chosen.canManageUsers ? " · pode gerenciar usuários" : ""}
            </div>` : ""}
          </div>
          <div class="field field-span-2">
            <label>Pessoa vinculada ${scope === "proprio" ? '<span style="color:var(--bad)">*</span>' : '<span style="color:var(--muted);font-weight:400">(recomendado)</span>'}</label>
            ${editor.linkedPersonName ? `
              <div style="display:flex;justify-content:space-between;align-items:center;gap:10px;
                          background:#f5f9ff;border:1px solid var(--accent);border-radius:10px;padding:10px 12px">
                <div>
                  <div style="font-weight:700;font-size:13px">${escapeHtml(editor.linkedPersonName)}</div>
                  ${editor.linkedPersonSource ? `<div class="text-small" style="color:var(--muted)">${escapeHtml(editor.linkedPersonSource)}</div>` : ""}
                </div>
                <button type="button" class="btn btn-ghost btn-sm" onclick="limparPessoaVinculada()">Trocar</button>
              </div>` : `
              <div style="display:flex;gap:8px">
                <input id="person-search-input" style="flex:1"
                  value="${escapeHtml(state.ui.personQuery || "")}"
                  placeholder="Buscar por nome — 3 letras já bastam"
                  oninput="state.ui.personQuery=this.value"
                  onkeydown="if(event.key==='Enter'){event.preventDefault();buscarPessoaVinculada();}" />
                <button type="button" class="btn btn-secondary" onclick="buscarPessoaVinculada()">
                  ${state.ui.personSearching ? "Buscando…" : "Buscar"}</button>
              </div>
              ${state.ui.personResults ? `
                <div style="border:1px solid var(--line);border-radius:8px;max-height:220px;overflow:auto;margin-top:8px">
                  ${state.ui.personResults.map((c, i) => `
                    <button type="button" onclick="escolherPessoaVinculada(${i})"
                      style="width:100%;text-align:left;border:none;background:#fff;cursor:pointer;
                             padding:8px 10px;border-bottom:1px solid var(--line)">
                      <div style="font-weight:700;font-size:13px">${escapeHtml(c.personName)}</div>
                      <div class="text-small" style="color:var(--muted)">
                        ${escapeHtml(c.source)}${c.detail ? ` · ${escapeHtml(c.detail)}` : ""}
                      </div>
                    </button>`).join("")
                    || '<div class="text-small" style="padding:10px;color:var(--muted)">Nenhuma pessoa encontrada com esse nome.</div>'}
                </div>` : ""}`}
            <div class="text-small" style="margin-top:4px;color:var(--muted)">
              ${scope === "proprio"
                ? "É por este vínculo que o sistema sabe quais clientes são desta pessoa e que ela participou de uma reunião."
                : "Liga a conta ao nome do cadastro. Sem isso, a pessoa não recebe a ciência quando é marcada como presente numa ata."}
              A busca varre quatro fontes: cadastro de pessoas, faturamento, vendedor no cadastro
              de clientes e <strong>cliente pessoa física</strong> — onde todo funcionário aparece,
              mesmo sem venda. Não dá para digitar à mão: um caractere trocado quebra o vínculo
              em silêncio, e o problema só aparece semanas depois.
            </div>
          </div>
          ${scope === "proprio" ? `
          <div class="field field-span-2">
            <label>Unidade do vendedor ${editor.baseUnit ? "" : '<span style="color:var(--bad)">*</span>'}</label>
            ${unidadesDisponiveis.length ? `
              <select id="user-base-unit" onchange="state.userEditor.baseUnit=this.value">
                <option value="">Selecione a unidade…</option>
                ${unidadesDisponiveis.map((u) => `<option value="${escapeHtml(u)}" ${editor.baseUnit === u ? "selected" : ""}>${escapeHtml(u)}</option>`).join("")}
              </select>` : `
              <div class="message">Nenhuma unidade carregada. Recarregue a tela.</div>`}
            <div class="text-small" style="margin-top:4px;color:var(--muted)">
              ${editor.baseUnit
                ? "Gravada no cadastro de pessoas — é de lá que saem carteira, meta, feedback e roteiro de visita. Alterar aqui atualiza o cadastro."
                : '<span style="color:var(--bad)">Este vendedor está sem unidade.</span> Sem ela ele não entra nas listas de equipe, meta e visita. Escolha a unidade e salve.'}
            </div>
          </div>` : ""}
          ${["unidade", "unidade_consolidado"].includes(scope) ? `
          <div class="field field-span-2">
            <label>Unidades vinculadas <span style="color:var(--bad)">*</span></label>
            ${unidadesDisponiveis.length ? `
              <div class="checkbox-grid">
                ${unidadesDisponiveis.map((unit) => `<label class="checkbox-item"><input type="checkbox" ${editor.linkedUnits.includes(unit) ? "checked" : ""} onchange="toggleUserLinkedUnit('${jsAttr(unit)}')" /><span>${escapeHtml(unit)}</span></label>`).join("")}
              </div>
              <div class="text-small" style="margin-top:4px;color:var(--muted)">
                Define quais unidades este perfil enxerga. É diferente da pessoa vinculada acima:
                a unidade filtra os dados, a pessoa liga a conta ao nome nas atas e feedbacks.
              </div>` : `
              <div class="message">
                Nenhuma unidade carregada. Abra o Dashboard uma vez e volte aqui —
                a lista de unidades vem dos filtros e ainda não foi carregada nesta sessão.
              </div>`}
          </div>` : ""}
          <div class="field field-span-2">
            <label>${passwordLabel}</label>
            <input id="user-password" type="password" value="${escapeHtml(editor.password || "")}" oninput="state.userEditor.password=this.value" ${editor.id ? "" : "required"} />
          </div>
        </div>
        <div class="actions">
          <button class="btn btn-primary" type="submit">${submitLabel}</button>
          ${editor.id ? '<button class="btn btn-ghost" type="button" onclick="cancelUserEdit()">Cancelar edição</button>' : ""}
        </div>
      </form>
    </div>
  `;
}

function profileEditorCard() {
  const editor = state.profileEditor;
  const modules = state.admin?.accessModules || [];
  const scopes = state.admin?.dataScopes || [];
  const groups = [...new Set(modules.map((m) => m.group))];
  const title = editor.id ? `Editar perfil: ${escapeHtml(editor.name)}` : "Novo perfil";

  return `
    <div class="form-card" id="profile-editor-card">
      <div class="section-title">
        <div><h3>${title}</h3>
        <div class="text-small">Marque as telas que este perfil acessa e defina o alcance dos dados.</div></div>
        ${editor.id ? '<button class="btn btn-ghost btn-sm" type="button" onclick="cancelProfileEdit()">Cancelar</button>' : ""}
      </div>
      <form onsubmit="saveProfile(event)" class="stack">
        <div class="two-column-form">
          <div class="field">
            <label>Nome do perfil</label>
            <input value="${escapeHtml(editor.name)}" oninput="state.profileEditor.name=this.value"
              ${editor.isSystem ? "readonly title='Perfil padrão do sistema — o nome não pode mudar'" : ""} required />
            ${editor.isSystem ? '<div class="text-small" style="margin-top:4px;color:var(--muted)">Perfil padrão: pode editar telas e escopo, mas não renomear nem excluir.</div>' : ""}
          </div>
          <div class="field">
            <label>Descrição</label>
            <input value="${escapeHtml(editor.description)}" oninput="state.profileEditor.description=this.value" placeholder="Para que serve este perfil" />
          </div>
          <div class="field field-span-2">
            <label>Alcance dos dados</label>
            <select onchange="state.profileEditor.dataScope=this.value; requestRender()">
              ${scopes.map((s) => `<option value="${s.id}" ${editor.dataScope === s.id ? "selected" : ""}>${escapeHtml(s.label)}</option>`).join("")}
            </select>
            ${(() => { const s = scopes.find((x) => x.id === editor.dataScope); return s ? `<div class="text-small" style="margin-top:4px;color:var(--muted)">${escapeHtml(s.hint)}</div>` : ""; })()}
          </div>
          <div class="field field-span-2">
            <label class="checkbox-item" style="cursor:pointer">
              <input type="checkbox" ${editor.canManageUsers ? "checked" : ""}
                onchange="state.profileEditor.canManageUsers=this.checked; requestRender()" />
              <span>Pode criar e editar usuários e perfis</span>
            </label>
          </div>
        </div>

        <div class="field">
          <label>Telas acessíveis <span class="soft-badge">${(editor.modules || []).length} selecionada(s)</span></label>
          ${groups.map((group) => {
            const groupModules = modules.filter((m) => m.group === group);
            const allOn = groupModules.every((m) => (editor.modules || []).includes(m.id));
            return `
              <div style="margin-top:10px">
                <div style="display:flex;align-items:center;gap:8px;margin-bottom:6px">
                  <strong style="font-size:12px;color:var(--muted);letter-spacing:0.04em">${escapeHtml(group.toUpperCase())}</strong>
                  <button type="button" class="btn btn-ghost btn-sm" onclick="toggleProfileModuleGroup('${escapeHtml(group)}')">${allOn ? "Desmarcar todas" : "Marcar todas"}</button>
                </div>
                <div class="checkbox-grid">
                  ${groupModules.map((m) => `
                    <label class="checkbox-item">
                      <input type="checkbox" ${(editor.modules || []).includes(m.id) ? "checked" : ""} onchange="toggleProfileModule('${m.id}')" />
                      <span>${escapeHtml(m.label)}</span>
                    </label>`).join("")}
                </div>
              </div>`;
          }).join("")}
        </div>

        <div class="actions">
          <button class="btn btn-primary" type="submit">${editor.id ? "Salvar perfil" : "Criar perfil"}</button>
          ${editor.id ? '<button class="btn btn-ghost" type="button" onclick="cancelProfileEdit()">Cancelar</button>' : ""}
        </div>
      </form>
    </div>
  `;
}

function acessosView() {
  if (!state.admin) return `<div class="loader panel">Carregando usuários e perfis...</div>`;
  if (!userCanManageUsers()) {
    return `<div class="message">Seu perfil não permite gerenciar usuários. Fale com o Diretor ou Administrador.</div>`;
  }
  const users = state.admin.users || [];
  const profiles = accessProfiles();
  const scopes = state.admin.dataScopes || [];
  const scopeLabel = (id) => (scopes.find((s) => s.id === id) || {}).label || id;
  const usersByProfile = {};
  users.forEach((u) => {
    const key = u.profile_name || u.role || "—";
    usersByProfile[key] = (usersByProfile[key] || 0) + 1;
  });

  return `
    <div class="stack">
      <div class="kpi-grid">
        ${kpiCard("Usuários ativos", number(users.filter((u) => u.is_active).length), "Total cadastrado", number(users.length))}
        ${kpiCard("Perfis", number(profiles.length), "Personalizados", number(profiles.filter((p) => !p.isSystem).length))}
      </div>

      <div class="form-card">
        <div class="section-title">
          <div><h3>Usuários</h3><div class="text-small">Contas de acesso ao sistema.</div></div>
          <button class="btn btn-primary btn-sm" onclick="cancelUserEdit()">+ Novo usuário</button>
        </div>
        <div class="table-wrap">
          <table>
            <thead><tr><th>Login</th><th>Nome</th><th>Perfil</th><th>Vínculo</th><th>Status</th><th style="text-align:right">Ações</th></tr></thead>
            <tbody>
              ${users.length ? users.map((row) => {
                const profile = accessProfileById(row.profile_id) || profiles.find((p) => p.name === row.role);
                // Pessoa e unidades são vínculos DIFERENTES e um gerente tem os dois.
                // Mostrar só um escondia o outro e dava a impressão de que não salvou.
                const vinculo = [
                  row.linked_person_name
                    ? `<div>${escapeHtml(row.linked_person_name)}</div>`
                    : '<div style="color:var(--bad)">sem pessoa vinculada</div>',
                  row.linked_units_display
                    ? `<div style="color:var(--muted)">${escapeHtml(row.linked_units_display)}</div>`
                    : (row.person_unit
                        ? `<div style="color:var(--muted)">unidade da pessoa: ${escapeHtml(row.person_unit)}</div>`
                        : '<div style="color:var(--muted)">Toda a empresa</div>'),
                ].join("");
                return `
                <tr>
                  <td><strong>${escapeHtml(row.username)}</strong></td>
                  <td>${escapeHtml(row.full_name || "")}</td>
                  <td><span class="soft-badge">${escapeHtml(row.profile_name || row.role || "—")}</span>
                      ${profile ? `<div class="text-small" style="color:var(--muted)">${escapeHtml(scopeLabel(profile.dataScope))}</div>` : ""}</td>
                  <td class="text-small">${vinculo}</td>
                  <td>${row.is_active ? '<span style="color:var(--good)">● Ativo</span>' : '<span style="color:var(--muted)">○ Inativo</span>'}</td>
                  <td style="text-align:right;white-space:nowrap">
                    <button class="btn btn-ghost btn-sm" type="button" onclick="editUser(${Number(row.id)})">Editar</button>
                    <button class="btn btn-ghost btn-sm" type="button" onclick="startPasswordChange(${Number(row.id)})">Senha</button>
                    <button class="btn btn-ghost btn-sm" type="button" onclick="deleteUser(${Number(row.id)})">Excluir</button>
                  </td>
                </tr>`;
              }).join("") : '<tr><td colspan="6" class="text-small">Nenhum usuário cadastrado.</td></tr>'}
            </tbody>
          </table>
        </div>
      </div>

      ${userEditorCard()}

      <div class="form-card">
        <div class="section-title">
          <div><h3>Perfis de acesso</h3><div class="text-small">Cada perfil define telas visíveis e alcance dos dados.</div></div>
          <button class="btn btn-primary btn-sm" onclick="cancelProfileEdit()">+ Novo perfil</button>
        </div>
        <div class="table-wrap">
          <table>
            <thead><tr><th>Perfil</th><th>Telas</th><th>Alcance</th><th>Gerencia usuários</th><th>Usuários</th><th style="text-align:right">Ações</th></tr></thead>
            <tbody>
              ${profiles.map((p) => `
                <tr>
                  <td><strong>${escapeHtml(p.name)}</strong>${p.isSystem ? ' <span class="soft-badge">padrão</span>' : ""}
                      ${p.description ? `<div class="text-small" style="color:var(--muted)">${escapeHtml(p.description)}</div>` : ""}</td>
                  <td>${p.modules.length}</td>
                  <td class="text-small">${escapeHtml(scopeLabel(p.dataScope))}</td>
                  <td>${p.canManageUsers ? "Sim" : "Não"}</td>
                  <td>${number(usersByProfile[p.name] || 0)}</td>
                  <td style="text-align:right;white-space:nowrap">
                    <button class="btn btn-ghost btn-sm" type="button" onclick="startProfileEdit(${Number(p.id)})">Editar</button>
                    ${p.isSystem ? "" : `<button class="btn btn-ghost btn-sm" type="button" onclick="deleteProfile(${Number(p.id)})">Excluir</button>`}
                  </td>
                </tr>`).join("")}
            </tbody>
          </table>
        </div>
      </div>

      ${profileEditorCard()}
    </div>
  `;
}

function personEditorCard() {
  return `
        <div class="form-card">
          <div class="section-title"><div><h3>Cadastro de pessoa</h3><div class="text-small">Cadastro manual de vendedor/gerente e classificação.</div></div></div>
          <form onsubmit="savePerson(event)" class="stack">
            <div class="two-column-form">
              <div class="field"><label>Nome</label><input id="person-name" required /></div>
              <div class="field"><label>Classificação</label><select id="person-role"><option>Vendedor</option><option>Gerente</option><option>Outro</option></select></div>
              <div class="field"><label>Unidade base</label><input id="person-unit" placeholder="MATRIZ" /></div>
              <div class="field"><label>Vigência inicial</label><input id="person-valid-from" type="date" required /></div>
            </div>
            <button class="btn btn-secondary" type="submit">Salvar pessoa</button>
          </form>
        </div>
  `;
}

configuracoesView = function adminViewGoalsSellerUnitFinal() {
  if (!state.admin) return `<div class="loader panel">Carregando configurações...</div>`;
  const userPasswordLabel = state.userEditor.id ? "Nova senha (opcional)" : "Senha inicial";
  const userSubmitLabel = state.userEditor.id ? "Salvar ajustes do usuário" : "Salvar usuário";
  const userTitle = state.userEditor.id ? "Editar usuário" : "Criar usuário";
  const userRole = state.userEditor.role || "Administrador";
  const sellerGoalEditor = state.goalEditors.seller;
  const unitGoalEditor = state.goalEditors.unit;

  return `
    <div class="stack">
      <div class="stack">
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

            ${scoreEnabled() && userCanManageUsers() ? `
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
            </form>` : ""}
          </div>
        </div>
      </div>
      <div class="grid-2">
        <div class="form-card">
          <div class="section-title"><div><h3>Feriados</h3><div class="text-small">Cadastro de feriados do calendário comercial.</div></div></div>
          <div class="stack">
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
          ${kpiThresholdsCard()}
          ${scoreEnabled() && userCanManageUsers() ? adminTableCard("Configuração do score", ["valid_from_competence", "weight_goal", "weight_ticket", "weight_clients", "weight_mix", "weight_returns"], state.admin.scoreConfigs) : ""}
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
          ${botaoAtualizar("placar", "loadTeamScore()", { mensagem: "Placar atualizado." })}
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
  // Antes o título ficava travado por perfil em TODAS as abas. Agora o título
  // acompanha a tela aberta; o perfil só muda o texto da aba inicial.
  if (roleIsSeller() && state.activeTab === "crm-agenda") {
    return { title: "Minha Agenda do Dia", description: "Execução comercial orientada à ação, com foco na sua carteira e nos seus retornos." };
  }
  if (roleIsManager() && state.activeTab === "executivo") {
    return { title: "Visão Executiva da Unidade", description: "Resultados, equipe, alertas e clientes em risco da sua unidade." };
  }
  const map = {
    "executivo":      { title: "Visão Executiva",         description: "Panorama consolidado de resultados, metas e comparativos." },
    "vendedores":     { title: "Análise de Vendedores",   description: "Ranking, score e desempenho individual de vendedores." },
    "unidades":       { title: "Análise de Unidades",     description: "Comparativo de desempenho entre unidades." },
    "marcas":         { title: "Vendas por Marca",        description: "Ranking de marcas por itens, códigos e valor, com leitura do mês." },
    "devolucoes":     { title: "Devoluções",              description: "Devolução comercial e de garantia por motivo, vendedor, marca e cliente." },
    "clientes":       { title: "Base de Clientes",        description: "Carteira ativa, inativos e métricas por cliente." },
    "cidades":        { title: "Cobertura Geográfica",    description: "Distribuição de vendas e clientes por cidade." },
    "descontos":      { title: "Política de Descontos",   description: "Análise de desconto médio por vendedor." },
    "calendario":     { title: "Calendário Comercial",    description: "Feriados, dias úteis e distribuição mensal." },
    "importacoes":    { title: "Importações",             description: "Gestão de arquivos, pacotes e auditoria de dados." },
    "administracao":  { title: "Administração",           description: "Pendências, cadastros e integridade dos dados." },
    "metas-vendedor": { title: "Metas do Vendedor",       description: "Mix, margem e ligações por vendedor. Valem até você mudar." },
    "placar-equipe":  { title: "Placar da Equipe",         description: "Apuração da premiação por vendedor: indicadores, pontos e valor." },
    "configuracoes":  { title: "Configurações",           description: "Metas, score e parâmetros operacionais." },
    "acessos":        { title: "Usuários e Perfis",       description: "Contas de acesso e permissões por perfil." },
    "crm-agenda":     { title: "Missão do Dia",            description: "Sua fila de 5 contatos. 1 oferta + 1 pergunta por cliente." },
    "crm-clientes":   { title: "Carteira CRM",            description: "Clientes ativos, riscos e oportunidades." },
    "crm-tarefas":    { title: "Tarefas CRM",             description: "Tarefas pendentes de follow-up e interação." },
    "reunioes":       { title: "Reuniões e Treinamentos", description: "Atas, presença, ciência da equipe e acervo de treinamentos." },
    "feedback":       { title: "Feedback e PDI",         description: "Feedback mensal com base no MEC, plano de desenvolvimento e ciência." },
    "visitas":        { title: "Visitas",                description: "Roteiro sugerido, registro da visita e efeito no faturamento." },
    "prospeccao":     { title: "Prospecção",             description: "Oficinas que ainda não são clientes, qualificação e conversão." },
    "contatos":       { title: "Contatos",               description: "Histórico dos registros e produtividade por vendedor." },
    "biblioteca":     { title: "Biblioteca de Vendas",    description: "Abordagens, mensagens, objeções e garantia." },
    "sem-vendedor":   { title: "Clientes sem Vendedor",   description: "Clientes recorrentes que ninguém responde por eles." },
    "crm-interacao":  { title: "Interação CRM",           description: "Registro de interações com clientes." },
  };
  return map[state.activeTab] || { title: "Dashboard", description: "Visão geral." };
}

/** Subgrupo recolhível: consultas ocasionais que não merecem o primeiro nível.
 *  Abre sozinho quando a tela ativa está dentro dele — ninguém fica preso. */
function sidebarSubGroup(title, tabs) {
  if (!tabs.length) return "";
  if (state.ui.sidebarCollapsed) return sidebarTabGroup("", tabs);
  const contémAtiva = tabs.some((t) => t.id === state.activeTab);
  const aberto = state.ui.analysisOpen || contémAtiva;
  return `
    <button class="sidebar-subtoggle" onclick="state.ui.analysisOpen=!state.ui.analysisOpen;requestRender()">
      <span>${aberto ? "▾" : "▸"} ${escapeHtml(title)}</span>
      <span class="text-small" style="color:var(--muted)">${tabs.length}</span>
    </button>
    ${aberto ? sidebarTabGroup("", tabs) : ""}`;
}

function sidebarTabGroup(title, tabs) {
  if (!tabs.length) return "";
  const collapsed = state.ui.sidebarCollapsed;
  return `
    <div class="nav-section">
      ${!collapsed && title ? `<div class="nav-section-label">${escapeHtml(title)}</div>` : ""}
      ${tabs.map((tab) => `
        <button class="tab-button ${state.activeTab === tab.id ? "active" : ""} ${collapsed ? "tab-collapsed" : ""}"
          onclick="switchTab('${tab.id}')" title="${escapeHtml(tab.title)}">
          ${tab.icon ? `<span class="tab-icon">${tab.icon}</span>` : ""}
          ${!collapsed ? `<div class="tab-text">
            <span class="tab-title">${escapeHtml(tab.title)}</span>
            ${tab.desc ? `<span class="tab-desc">${escapeHtml(tab.desc)}</span>` : ""}
          </div>` : ""}
          ${tab.badge ? `<span style="background:#e74c3c;color:#fff;border-radius:10px;padding:1px 7px;
            font-size:11px;font-weight:800;margin-left:auto">${tab.badge}</span>` : ""}
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

/** Ritmo diário: o que está sendo vendido por dia e o que falta por dia útil.
 *
 * A conta que todo mundo faz de cabeça e erra, porque divide pelos dias
 * corridos. Aqui é por dia ÚTIL restante — no fim do mês, a diferença entre os
 * dois é o que separa "dá tempo" de "não deu".
 */
function blocoRitmoDiario(pace, titulo) {
  if (!pace) return "";
  if (!pace.hasGoal) {
    return `
      <div class="form-card" style="padding:12px 18px">
        <div style="font-size:11px;font-weight:800;color:var(--muted);letter-spacing:0.06em">RITMO DIÁRIO</div>
        <div style="margin-top:6px">Média vendida por dia útil: <strong>${currency(pace.dailyActual)}</strong>
          <span class="text-small" style="color:var(--muted)"> · ${number(pace.elapsedDays)} de
          ${number(pace.elapsedDays + pace.remainingDays)} dias úteis</span></div>
        <div class="text-small" style="color:var(--muted);margin-top:4px">
          Sem meta definida nesta competência, não há quanto perseguir por dia.
        </div>
      </div>`;
  }

  const fim = pace.remainingDays <= 0;
  return `
    <div class="form-card" style="padding:14px 18px">
      <div class="section-title" style="margin-bottom:8px">
        <div>
          <h3 style="font-size:15px">${escapeHtml(titulo)}</h3>
          <div class="text-small">Média atual <strong>${currency(pace.dailyActual)}</strong>/dia útil ·
            ${number(pace.elapsedDays)} dia(s) corrido(s), <strong>${number(pace.remainingDays)}</strong> restante(s)</div>
        </div>
      </div>
      ${fim ? `<div class="text-small" style="color:var(--muted)">Mês encerrado — não há dias úteis restantes.</div>` : `
        <div style="display:flex;gap:12px;flex-wrap:wrap">
          ${pace.targets.map((t) => {
            const cor = t.pct >= 105 ? "#6a1b9a" : t.pct >= 100 ? "var(--accent)" : t.pct >= 95 ? "#b06000" : "var(--muted)";
            return `
            <div style="flex:1;min-width:150px;background:#fff;border:1px solid var(--line);
                        border-left:3px solid ${cor};border-radius:0 10px 10px 0;padding:10px 12px">
              <div class="text-small" style="color:var(--muted)">Para fechar em <strong>${t.pct}%</strong></div>
              ${t.reached
                ? `<div style="font-size:18px;font-weight:800;color:var(--good)">✓ atingido</div>
                   <div class="text-small" style="color:var(--muted)">meta ${currency(t.targetValue)}</div>`
                : `<div style="font-size:19px;font-weight:800;color:${cor}">${currency(t.dailyNeeded)}<span
                       style="font-size:12px;font-weight:500;color:var(--muted)">/dia</span></div>
                   <div class="text-small" style="color:var(--muted)">faltam ${currency(t.missing)}</div>
                   <div class="text-small" style="color:${t.deltaVsActual > 0 ? "var(--bad)" : "var(--good)"}">
                     ${t.deltaVsActual > 0 ? `+${currency(t.deltaVsActual)}/dia vs ritmo atual`
                                           : `${currency(Math.abs(t.deltaVsActual))}/dia abaixo do ritmo atual`}
                   </div>`}
            </div>`;
          }).join("")}
        </div>`}
    </div>`;
}

function executivoView() {
  if (!state.dashboard) return `<div class="loader panel">Carregando dashboard…</div>`;
  // Gerente vê o MESMO Executivo de diretor e admin — os dados já vêm recortados
  // pela unidade dele. Os blocos operacionais próprios da gestão (alertas e
  // clientes em risco) são acrescentados no fim, em vez de substituírem a tela.
  const s = state.dashboard.summary || {};
  const comp = state.dashboard.comparisons || {};
  const ranking = state.dashboard.sellerRanking || [];
  const units = state.dashboard.unitPerformance || [];
  return `
    <div class="stack">
      ${loadingBanner()}
      <div class="kpi-grid">
        ${kpiCard("Faturamento líquido", currency(s.revenueNet), "Meta", currency(s.revenueGoal), s.farol?.goalAttainment)}
        ${kpiCard("% Atingimento", pct(s.goalAttainmentPct), "Projeção", pct(s.projectedGoalAttainmentPct), s.farol?.goalAttainment)}
        ${kpiCardClicavel("Clientes faturados", number(s.distinctClients || 0),
                          "Ver a lista com a carteira de cada um",
                          "abrirClientesDoVendedor('','todos')")}
        ${kpiCard("Projeção do mês", currency(s.projectedRevenue || 0),
                  Number(s.revenueGoal || 0) > Number(s.projectedRevenue || 0) ? "Faltam" : "Acima da meta",
                  currency(Math.abs(Number(s.revenueGoal || 0) - Number(s.projectedRevenue || 0))),
                  s.farol?.projectedAttainment)}
        ${kpiCard("Ticket médio", currency(s.ticketAverage), "Clientes", number(s.distinctClients))}
        ${kpiCard("Ticket PJ", currency(s.ticketAveragePj || 0), "Clientes PJ", number(s.pjClients || 0))}
        ${kpiCard("Ticket PF", currency(s.ticketAveragePf || 0), "Clientes PF", number(s.pfClients || 0))}
        ${kpiCard("Devolução comercial", currency(s.returnsValue), "% Devolução", pct(s.returnRatioPct), s.farol?.returnRatio)}
        ${kpiCard("Devolução em garantia", currency(s.warrantyReturnsValue || 0), "% Garantia", pct(s.warrantyRatioPct || 0))}
        ${kpiCard("Desconto médio", pct(s.discountPct), "Mix SKU", number(s.mixSku), s.farol?.discountPct)}
        ${kpiCard("Dias úteis", `${number(s.workingDaysElapsed)}/${number(s.workingDaysTotal)}`, "Meta diária", currency(s.dailyRevenueTarget))}
      </div>
      ${farolLegend(s.paceExpectedPct)}
      ${(() => {
        // O vendedor vê o ritmo DELE, que inclui a faixa de 105% — a faixa de
        // premiação. O consolidado e a unidade param em 100%.
        if (!roleIsSeller()) return blocoRitmoDiario(s.pace, "Ritmo diário — quanto precisa vender por dia");
        const eu = (state.dashboard.sellerRanking || [])
          .find((r) => personKeyJs(r.sellerName) === personKeyJs(meuNomeDeVendas()));
        const minha = (state.dashboard.sellerRanking || []).length === 1
          ? state.dashboard.sellerRanking[0] : eu;
        return blocoRitmoDiario((minha && minha.pace) || s.pace,
                                "Meu ritmo diário — quanto preciso vender por dia");
      })()}
      ${(Number(s.ownClients || 0) + Number(s.otherClients || 0)) > 0 ? `
        <div class="form-card" style="padding:12px 18px">
          <div style="display:flex;gap:20px;flex-wrap:wrap;align-items:center">
            <div>
              <div style="font-size:11px;font-weight:800;color:var(--muted);letter-spacing:0.06em">CLIENTES ATENDIDOS</div>
              <div class="text-small" style="color:var(--muted)">Carteira = cliente com vendedor definido no cadastro CRM.
                Os valores são a proporção do relatório detalhado aplicada ao faturamento oficial.</div>
              ${Number(s.detailSourceGapPct || 0) > 5 ? `
                <div class="text-small" style="margin-top:4px;color:#7a5c00;background:#fff8e6;
                     border:1px solid #f0d68a;border-radius:6px;padding:4px 8px;display:inline-block">
                  ⚠ Relatório detalhado difere ${pct(s.detailSourceGapPct)} do oficial — rode
                  <strong>diag_faturamento.py</strong> para achar a causa.
                </div>` : ""}
            </div>
            <div style="display:flex;gap:18px;flex-wrap:wrap">
              <div><span class="text-small" style="color:var(--muted)">Total</span><br>
                <strong>${number(s.distinctClients)}</strong>
                <span class="text-small" style="color:var(--muted)"> · ${currency(s.revenueNet)}</span></div>
              <div><span class="text-small" style="color:var(--muted)">De carteira</span><br>
                <strong style="color:var(--good)">${number(s.ownClients || 0)}</strong>
                <span class="text-small" style="color:var(--muted)"> · ${currency(s.ownRevenue || 0)} · ticket ${currency(s.ticketAverageOwn || 0)}</span></div>
              <div><span class="text-small" style="color:var(--muted)">Fora da carteira</span><br>
                <strong style="color:#e67e22">${number(s.otherClients || 0)}</strong>
                <span class="text-small" style="color:var(--muted)"> · ${currency(s.otherRevenue || 0)} · ticket ${currency(s.ticketAverageOther || 0)}</span></div>
              <div><span class="text-small" style="color:var(--muted)">PJ / PF</span><br>
                <strong>${number(s.pjClients || 0)}</strong>
                <span class="text-small" style="color:var(--muted)"> · ${currency(s.pjRevenue || 0)}</span>
                &nbsp;|&nbsp;
                <strong>${number(s.pfClients || 0)}</strong>
                <span class="text-small" style="color:var(--muted)"> · ${currency(s.pfRevenue || 0)}</span></div>
            </div>
          </div>
        </div>` : ""}
      ${Number(s.warrantyReturnsValue || 0) > 0 ? `
        <div class="form-card" style="padding:12px 18px">
          <div style="display:flex;gap:20px;flex-wrap:wrap;align-items:center">
            <div>
              <div style="font-size:11px;font-weight:800;color:var(--muted);letter-spacing:0.06em">COMPOSIÇÃO DAS DEVOLUÇÕES</div>
              <div class="text-small" style="color:var(--muted)">A garantia não entra no resultado comercial.</div>
            </div>
            <div style="display:flex;gap:18px;flex-wrap:wrap">
              <div><span class="text-small" style="color:var(--muted)">Total devolvido</span><br>
                <strong>${currency(s.returnsTotalValue || 0)}</strong>
                <span class="text-small" style="color:var(--muted)"> (${pct(s.returnsTotalRatioPct || 0)})</span></div>
              <div><span class="text-small" style="color:var(--muted)">− Garantia</span><br>
                <strong style="color:#e67e22">${currency(s.warrantyReturnsValue || 0)}</strong>
                <span class="text-small" style="color:var(--muted)"> (${pct(s.warrantyRatioPct || 0)})</span></div>
              <div><span class="text-small" style="color:var(--muted)">= Comercial</span><br>
                <strong style="color:var(--accent)">${currency(s.returnsValue || 0)}</strong>
                <span class="text-small" style="color:var(--muted)"> (${pct(s.returnRatioPct || 0)})</span></div>
            </div>
          </div>
          ${blocoMotivosDevolucao(s)}
        </div>` : ""}
      <div class="grid-2">
        ${summaryDiffCard("Receita líquida — comparativos", comp.group)}
        ${kpiCard("Vendedores ativos", number(ranking.length), "Unidades", number(units.length))}
      </div>
      ${executiveExpandSection("details", "Ver ranking de vendedores", `
        <div class="table-wrap">
          <table>
            <thead><tr>
              ${sortableTh("vendedores","Vendedor","sellerName","text")}
              ${sortableTh("vendedores","Unidade","baseUnit","text")}
              ${sortableTh("vendedores","Líquido","revenueNet")}
              ${sortableTh("vendedores","Meta","revenueGoal")}
              ${sortableTh("vendedores","% Meta","goalAttainmentPct")}
              ${sortableTh("vendedores","Projeção","projectedRevenue")}
              ${sortableTh("vendedores","% Proj.","projectedGoalAttainmentPct")}
              ${sortableTh("vendedores","Ticket","ticketAverage")}
              ${sortableTh("vendedores","Clientes","distinctClients")}
              ${sortableTh("vendedores","Carteira","ownClients")}
              ${sortableTh("vendedores","Fora","otherClients")}
              ${sortableTh("vendedores","Mix","mixSku")}
              ${sortableTh("vendedores","Dev. comercial","returnsValue")}
              ${sortableTh("vendedores","% Dev.","returnRatioPct")}
              ${sortableTh("vendedores","Dev. garantia","warrantyReturnsValue")}
              ${sortableTh("vendedores","% Desc.","discountPct")}
              ${scoreEnabled() ? sortableTh("vendedores","Score","score") : ''}
            </tr></thead>
            <tbody>${sellerRows(applyTableSort(ranking, "vendedores"))}</tbody>
          </table>
        </div>
      `)}
      ${executiveExpandSection("units", "Ver performance por unidade", `
        <div class="table-wrap">
          <table>
            <thead><tr>
              ${sortableTh("unidades","Unidade","unitName","text")}
              ${sortableTh("unidades","Líquido","revenueNet")}
              ${sortableTh("unidades","Meta","revenueGoal")}
              ${sortableTh("unidades","% Meta","goalAttainmentPct")}
              ${sortableTh("unidades","Projeção","projectedRevenue")}
              ${sortableTh("unidades","% Proj.","projectedGoalAttainmentPct")}
              ${sortableTh("unidades","Dev. comercial","returnsValue")}
              ${sortableTh("unidades","% Dev.","returnRatioPct")}
              ${sortableTh("unidades","Dev. garantia","warrantyReturnsValue")}
              ${sortableTh("unidades","Margem","marginValue")}
              ${sortableTh("unidades","Qtd. Peças","qtySold")}
              ${sortableTh("unidades","Ticket/Peça","ticketPerPiece")}
              ${sortableTh("unidades","Meta diária","metaDiaria")}
            </tr></thead>
            <tbody>${unitRows(applyTableSort(units, "unidades"))}</tbody>
          </table>
        </div>
      `)}
      ${scoreEnabled() ? executiveExpandSection("ranking", "Ver quadrante de vendedores", quadrantHtml(state.dashboard.quadrant)) : ""}
      ${executiveExpandSection("comparisons", "Ver comparativos de período", `
        <div class="kpi-grid">
          ${summaryDiffCard("Receita do grupo", comp.group)}
          ${(state.dashboard.unitPerformance || []).slice(0, 4).map((u) => kpiCard(escapeHtml(u.unitName), currency(u.revenueNet), "Meta", currency(u.revenueGoal))).join("")}
        </div>
      `)}
      ${roleIsManager() ? managementOperationalBlocks() : ""}
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
          <div class="text-small">Clique em qualquer coluna para reordenar.</div>
        </div>
        ${sortHint("descontos")}
      </div>
      <div class="table-wrap">
        <table>
          <thead>
            <tr>
              ${sortableTh("descontos","Vendedor","sellerName","text")}
              ${sortableTh("descontos","Unidade","baseUnit","text")}
              ${sortableTh("descontos","% Desconto","discountPct")}
              ${sortableTh("descontos","Líquido","revenueNet")}
              ${sortableTh("descontos","% Meta","goalAttainmentPct")}
              ${scoreEnabled() ? sortableTh("descontos","Score","score") : ''}
            </tr>
          </thead>
          <tbody>
            ${applyTableSort(rows, "descontos").map((row) => `
              <tr>
                <td>${escapeHtml(row.sellerName)}</td>
                <td>${escapeHtml(row.baseUnit || "-")}</td>
                <td>${pct(row.discountPct || 0)}</td>
                <td>${currency(row.revenueNet)}</td>
                <td>${pct(row.goalAttainmentPct)}</td>
                ${scoreEnabled() ? `<td><span class="score-chip">${row.score}</span></td>` : ''}
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

  // Grupos por INTENÇÃO, na ordem de frequência de uso — o diário no topo.
  // "Meu Dia" é o ciclo do MEC na ordem em que o dia acontece: abrir a fila,
  // resolver o atrasado, trabalhar a carteira, conferir o que registrou.
  const meuDiaTabs = [
    { id: "crm-agenda",    title: "Missão do Dia",    desc: "5 contatos prioritários", icon: "📅" },
    { id: "crm-tarefas",   title: "Tarefas",          desc: "Pendências de follow-up",  icon: "✅" },
    { id: "crm-clientes",  title: "Carteira",         desc: "Clientes e status",        icon: "👥" },
    { id: "contatos",      title: "Contatos",         desc: "Histórico e produtividade", icon: "📇" },
  ].filter((t) => allowed.includes(t.id));

  const crescerTabs = [
    { id: "prospeccao",    title: "Prospecção",       desc: "Oficinas novas",           icon: "🌱" },
    { id: "visitas",       title: "Visitas",          desc: "Roteiro e resultado",      icon: "🗺️",
      // Só o gestor tem o que responder. Para o vendedor, pedido pendente é
      // espera, não pendência — contador vermelho ali só geraria ansiedade.
      badge: state.visits?.canManage
        ? (state.visits?.requests || []).filter((r) => r.status === "PENDENTE").length : 0 },
    { id: "sem-vendedor",  title: "Sem Vendedor",     desc: "Clientes no limpo",        icon: "🔍" },
  ].filter((t) => allowed.includes(t.id));

  const equipeTabs = [
    { id: "placar-equipe", title: "Placar Equipe",    desc: "Apuração da premiação",    icon: "🏆" },
    { id: "biblioteca",    title: "Biblioteca",       desc: "Scripts e abordagens",     icon: "📚" },
    { id: "reunioes", title: "Reuniões",  desc: "Atas e treinamentos",  icon: "🗓️",
      badge: state.meetings?.pendingCount || 0 },
    { id: "feedback", title: "Feedback",  desc: "Avaliação e PDI",      icon: "🎯",
      badge: state.feedback?.pendingCount || 0 },
  ].filter((t) => allowed.includes(t.id));

  const resultTabs = [
    { id: "executivo",  title: "Executivo",  desc: "Panorama e KPIs",          icon: "📊" },
    { id: "vendedores", title: "Vendedores", desc: "Ranking e score",           icon: "👤" },
    { id: "unidades",   title: "Unidades",   desc: "Comparativo",               icon: "🏢" },
    { id: "marcas",     title: "Marcas",     desc: "Ranking por marca",         icon: "🏷️" },
    { id: "devolucoes", title: "Devoluções", desc: "Comercial x garantia",      icon: "↩️" },
  ].filter((t) => allowed.includes(t.id));

  // Consultas ocasionais recolhidas: no mesmo nível do Executivo elas puxavam
  // o menu para baixo sem merecer o espaço — são abertas algumas vezes por mês.
  const analiseTabs = [
    { id: "clientes",   title: "Clientes",   desc: "Carteira ativa",            icon: "🧑" },
    { id: "cidades",    title: "Cidades",    desc: "Cobertura geográfica",      icon: "🌍" },
    { id: "descontos",  title: "Descontos",  desc: "Política de desconto",      icon: "🏷" },
    { id: "calendario", title: "Calendário", desc: "Dias úteis e feriados",     icon: "📆" },
  ].filter((t) => allowed.includes(t.id));

  const opsTabs = [
    { id: "importacoes",   title: "Importações",    desc: "Arquivos e auditoria",    icon: "📥" },
    { id: "metas-vendedor", title: "Metas",         desc: "Mix, margem e ligações", icon: "🎯" },
    { id: "administracao", title: "Administração",  desc: "Pendências e cadastros",  icon: "⚙️" },
    { id: "configuracoes", title: "Configurações",  desc: "Metas e parâmetros",      icon: "🔧" },
    { id: "acessos",       title: "Usuários e Perfis", desc: "Contas e permissões",  icon: "🔑" },
  ].filter((t) => allowed.includes(t.id));

  const filtersLoading = Boolean(state.ui.loading.filters);
  const dis = filtersLoading ? "disabled" : "";
  const isCrmTab = state.activeTab.startsWith("crm-") || state.activeTab === "placar-equipe";
  // Telas com período próprio não devem mostrar o seletor de competência: dois
  // filtros de tempo na mesma tela, um deles sem efeito, só geram dúvida sobre
  // qual está valendo. Contatos filtra por data de/até dentro da própria tela.
  const TELAS_SEM_COMPETENCIA = ["contatos", "reunioes", "visitas", "prospeccao", "administracao", "acessos"];
  // O vendedor não escolhe unidade nem vendedor (o escopo já força os dele),
  // mas precisa trocar de mês para acompanhar o próprio histórico.
  const sellerFilterBar = sellerRole && !isCrmTab ? `
    <div class="form-card" style="padding:12px 18px">
      <div style="display:flex;align-items:center;gap:10px;flex-wrap:wrap">
        <span style="font-size:12px;font-weight:700;color:var(--muted);white-space:nowrap">COMPETÊNCIA</span>
        <select onchange="state.filters.competenceStart = state.filters.competenceEnd = this.value; applyMainFilters()" ${dis} style="flex:1;min-width:130px;max-width:220px">
          ${(state.options.competences || []).map((c) => `<option value="${escapeHtml(c)}" ${state.filters.competenceEnd === c ? "selected" : ""}>${escapeHtml(c)}</option>`).join("")}
        </select>
        ${filtersLoading ? '<span class="text-small" style="color:var(--accent);font-weight:600">Buscando…</span>' : ""}
      </div>
    </div>
  ` : "";
  const filterBar = TELAS_SEM_COMPETENCIA.includes(state.activeTab) ? "" : (sellerRole || isCrmTab ? sellerFilterBar : `
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
  `);

  // Score resumido no sidebar para vendedor — DESLIGADO enquanto a apuração da
  // premiação é reconstruída. Ele mostra a pontuação da cesta antiga (5
  // componentes, 0–100), que não corresponde à premiação real, e levava para
  // uma tela que o vendedor não tem mais. Volta quando o placar do vendedor for
  // refeito sobre os 9 indicadores.
  const sidebarScore = false && placarEnabled() && roleIsSeller() && state.sellerScore ? `
    <div style="padding:10px 12px;background:linear-gradient(135deg,#0f3044,#1a5276);border-radius:12px;margin-top:8px;cursor:pointer" onclick="switchTab('placar-equipe')">
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
        <nav class="sidebar ${state.ui.sidebarCollapsed ? 'sidebar-collapsed' : ''}" data-keep-scroll="sidebar">
          <div>
            <div class="brand-pill ${state.ui.sidebarCollapsed ? 'brand-collapsed' : ''}">
              ${!state.ui.sidebarCollapsed ? '<span class="dot"></span>' : ''}
              ${!state.ui.sidebarCollapsed ? 'Passini Autopeças' : '<span class="dot"></span>'}
            </div>
            <button class="sidebar-toggle" onclick="toggleSidebar()" title="${state.ui.sidebarCollapsed ? 'Expandir menu' : 'Recolher menu'}">
              ${state.ui.sidebarCollapsed ? '▶' : '◀'}
            </button>
            ${sidebarTabGroup("Meu Dia", meuDiaTabs)}
            ${sidebarTabGroup("Crescer", crescerTabs)}
            ${sidebarTabGroup("Equipe", equipeTabs)}
            ${sidebarTabGroup("Resultados", resultTabs)}
            ${sidebarSubGroup("Análises", analiseTabs)}
            ${sidebarTabGroup("Operações", opsTabs)}
          </div>
          <div class="sidebar-footer">
            ${!state.ui.sidebarCollapsed ? sidebarScore : ""}
          </div>
        </nav>
        <div class="main">
          <div class="topbar">
            <div>
              <h2>${escapeHtml(title)} ${selo_dados_ate()}</h2>
              <p>${escapeHtml(description)}</p>
            </div>
            ${topbarActions()}
          </div>
          ${filterBar}
          ${messageHtml()}
          ${!allowed.includes(state.activeTab) ? `<div class="message">Seu perfil não tem acesso a esta tela.</div>` : ""}
          ${state.activeTab === "crm-agenda"    ? crmAgendaView()      : ""}
          ${state.activeTab === "crm-clientes"  ? crmClientsView()     : ""}
          ${state.activeTab === "crm-tarefas"   ? crmTasksView()       : ""}
          ${state.activeTab === "biblioteca"    ? bibliotecaView()     : ""}
          ${state.activeTab === "reunioes"      ? reunioesView()       : ""}
          ${state.activeTab === "feedback"      ? feedbackView()       : ""}
          ${state.activeTab === "visitas"       ? visitasView()        : ""}
          ${state.activeTab === "prospeccao"    ? prospeccaoView()     : ""}
          ${state.activeTab === "contatos"      ? contatosView()       : ""}
          ${state.activeTab === "sem-vendedor"  ? semVendedorView()    : ""}
          ${state.activeTab === "crm-interacao" ? crmInteractionView() : ""}
          ${state.activeTab === "executivo"     ? executivoView()      : ""}
          ${state.activeTab === "vendedores"    ? vendedoresView()     : ""}
          ${state.activeTab === "unidades"      ? unitsView()          : ""}
          ${state.activeTab === "marcas"        ? marcasView()         : ""}
          ${state.activeTab === "devolucoes"    ? devolucoesView()     : ""}
          ${state.activeTab === "clientes"      ? clientesView()       : ""}
          ${state.activeTab === "cidades"       ? cidadesView()        : ""}
          ${state.activeTab === "descontos"     ? descontosView()      : ""}
          ${state.activeTab === "calendario"    ? calendarView()       : ""}
          ${state.activeTab === "importacoes"   ? importacoesView()    : ""}
          ${state.activeTab === "administracao" ? administracaoView()  : ""}
          ${state.activeTab === "metas-vendedor" ? metasVendedorView() : ""}
          ${state.activeTab === "placar-equipe"  ? placarEquipeView()  : ""}
          ${state.activeTab === "configuracoes" ? configuracoesView()  : ""}
          ${state.activeTab === "acessos"       ? acessosView()        : ""}
        </div>
      </div>
      ${crmModalView()}
      ${copyFallbackModal()}
      ${assignTaskModal()}
      ${scheduleContactModal()}
      ${conciliacaoModal()}
      ${clientesDoVendedorModal()}
      ${apoioModal()}
      ${coberturaModal()}
      ${receptiveModal()}
      ${state.visitRequestEditor ? pedidoVisitaModal() : ""}
      ${assistantFab()}
      ${helpEditorModal()}
      ${tourOverlay()}
      ${clientDrawerView()}
    </div>
  `;
}

function render() {
  // Cada render reconstrói o DOM inteiro, e o navegador zera o scroll dos
  // elementos novos. Em telas longas dentro de modal (ata de reunião, por
  // exemplo) qualquer clique que atualize o estado jogava a pessoa de volta
  // ao topo. Qualquer elemento com data-keep-scroll tem a posição restaurada.
  // Guarda TODA posição, inclusive zero: o menu lateral precisa disso. Ao
  // clicar num item lá embaixo, a tela trocava e o menu voltava ao topo,
  // escondendo justamente o item recém-escolhido.
  const posicoes = new Map();
  document.querySelectorAll("[data-keep-scroll]").forEach((el) => {
    posicoes.set(el.getAttribute("data-keep-scroll"), el.scrollTop);
  });
  const drawerEl = document.querySelector(".client-drawer");
  const drawerScroll = drawerEl ? drawerEl.scrollTop : 0;

  app.innerHTML = state.user ? dashboardView() : loginView();

  if (drawerScroll > 0) {
    const newDrawer = document.querySelector(".client-drawer");
    if (newDrawer) newDrawer.scrollTop = drawerScroll;
  }
  posicoes.forEach((topo, chave) => {
    const el = document.querySelector(`[data-keep-scroll="${chave}"]`);
    if (el && topo > 0) el.scrollTop = topo;
  });
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

// ─── Cidades pendentes em lote ─────────────────────────────────────────────

function toggleCidadePendente(cidade) {
  const atual = state.ui.bulkCities;
  if (atual.has(cidade)) atual.delete(cidade); else atual.add(cidade);
  requestRender();
}

function marcarTodasCidades(cidades, marcar) {
  cidades.forEach((c) => (marcar ? state.ui.bulkCities.add(c) : state.ui.bulkCities.delete(c)));
  requestRender();
}

async function aplicarUnidadeEmLote() {
  const cidades = [...state.ui.bulkCities];
  const unidade = state.ui.bulkCityUnit;
  if (!cidades.length) { addMessage("error", "Marque ao menos uma cidade."); return; }
  if (!unidade) { addMessage("error", "Escolha a unidade."); return; }
  try {
    const r = await api("/api/admin/issues/cities/bulk", {
      method: "POST",
      body: JSON.stringify({ cities: cidades, unitName: unidade }),
    });
    addMessage("success", r.message || "Cidades direcionadas.");
    state.ui.bulkCities = new Set();
    state.ui.bulkCityUnit = "";
    await loadAdmin();
  } catch (error) {
    addMessage("error", error.message);
  }
}

/** Resolve várias cidades de uma vez. Uma a uma, com três campos cada, a
 *  pendência simplesmente não era feita — e cidade sem unidade tira o
 *  faturamento do painel. */
function cidadesPendentesEmLote() {
  const pendentes = (state.admin?.issues || [])
    .filter((i) => i.issue_type === "cidade_sem_correspondencia" && i.status === "pendente");
  if (pendentes.length < 2) return "";

  const cidades = [...new Set(pendentes.map((i) => i.reference_value))]
    .sort((a, b) => String(a).localeCompare(String(b), "pt-BR"));
  const marcadas = state.ui.bulkCities;
  const unidades = unitOptionsForEditor();

  return `
    <div class="form-card">
      <div class="section-title">
        <div>
          <h3>Direcionar cidades em lote</h3>
          <div class="text-small">${number(cidades.length)} cidade(s) sem unidade. Marque as da mesma região e aplique de uma vez.</div>
        </div>
        <div class="actions">
          <button class="btn btn-ghost btn-sm" type="button"
            onclick='marcarTodasCidades(${JSON.stringify(cidades).replace(/'/g, "&#39;")}, true)'>Marcar todas</button>
          <button class="btn btn-ghost btn-sm" type="button"
            onclick='marcarTodasCidades(${JSON.stringify(cidades).replace(/'/g, "&#39;")}, false)'>Limpar</button>
        </div>
      </div>

      <div class="checkbox-grid" style="max-height:260px;overflow:auto">
        ${cidades.map((c) => `
          <label class="checkbox-item">
            <input type="checkbox" ${marcadas.has(c) ? "checked" : ""}
              onchange="toggleCidadePendente('${jsAttr(c)}')" />
            <span>${escapeHtml(c)}</span>
          </label>`).join("")}
      </div>

      <div class="two-column-form" style="margin-top:12px">
        <div class="field">
          <label>Unidade para as ${number(marcadas.size)} cidade(s) marcada(s)</label>
          <select onchange="state.ui.bulkCityUnit=this.value;requestRender()">
            <option value="">Selecione a unidade…</option>
            ${unidades.map((u) => `<option value="${escapeHtml(u)}" ${state.ui.bulkCityUnit === u ? "selected" : ""}>${escapeHtml(u)}</option>`).join("")}
          </select>
        </div>
        <div class="field" style="align-self:end">
          <button class="btn btn-primary" type="button" ${marcadas.size && state.ui.bulkCityUnit ? "" : "disabled"}
            onclick="aplicarUnidadeEmLote()">
            Aplicar a ${number(marcadas.size)} cidade(s)
          </button>
        </div>
      </div>
      <div class="text-small" style="color:var(--muted)">
        Vale para todos os períodos, inclusive os meses já fechados. O faturamento dessas
        cidades volta a aparecer no painel da unidade escolhida.
      </div>
    </div>
  `;
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
    if (!city || !unit) { addMessage("error", "Informe cidade e unidade principal."); return; }
    payload = { ...payload, city_name: city, principal_unit: unit };
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
  if (!name) { addMessage("error", "Selecione o vendedor na lista."); return; }
  if (!start || !end) { addMessage("error", "Data inicial e data final são obrigatórias."); return; }
  if (end < start) { addMessage("error", "A data final não pode ser anterior à inicial."); return; }
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

/** Mês corrente como AAAA-MM — rótulo das importações que não têm competência. */
function hojeCompetencia() {
  const d = new Date();
  return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, "0")}`;
}

function importDomConfig(scope) {
  const configs = {
    cost: { files: ["import-cost-unit-file", "import-cost-vendor-file"], competence: "import-cost-competence", action: null, feedback: "import-cost-feedback", importScope: "cost" },
    sales: { files: ["import-sales-file"], competence: "import-sales-competence", action: "import-sales-action", feedback: "import-sales-feedback", importScope: "sales" },
    crm: { files: ["import-crm-clients-file", "import-crm-summary-file"], competence: "import-crm-competence", action: null, feedback: "import-crm-feedback", importScope: "crm" },
    // Bases mestre: sem campo de competência, porque não têm mês.
    catalog: { files: ["import-catalog-file"], competence: null, action: null, feedback: "import-catalog-feedback", importScope: "catalog" },
    stock: { files: ["import-stock-file"], competence: null, action: null, feedback: "import-stock-feedback", importScope: "stock" },
  };
  return configs[scope] || null;
}

async function completeCrmTask(taskId) {
  try {
    await api("/api/crm/tasks/complete", { method: "POST", body: JSON.stringify({ taskId }) });
    addMessage("success", "Tarefa concluída.");
    // Recarrega respeitando o filtro escolhido, senão a tela volta para "em aberto".
    await loadCrmTasks(true);
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
  if (cfg.competence) {
    const compEl = document.getElementById(cfg.competence);
    if (compEl?.value) form.set("competence", compEl.value.trim());
  } else {
    form.set("competence", hojeCompetencia());
  }
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
  let escolheuArquivo = false;
  for (const fileId of cfg.files) {
    const fileEl = document.getElementById(fileId);
    if (fileEl?.files[0]) {
      form.append(fileId, fileEl.files[0], fileEl.files[0].name);
      escolheuArquivo = true;
    }
  }
  // Dois envios no mesmo bloco: sem esta checagem, clicar no botão errado
  // manda um pacote vazio e o erro vem do servidor, sem dizer o que faltou.
  if (!escolheuArquivo) {
    addMessage("error", "Escolha o arquivo antes de importar.");
    if (feedbackEl) feedbackEl.textContent = "";
    return;
  }
  // Bases mestre (catálogo, estoque) não têm competência: o mês entra só como
  // rótulo do registro de importação.
  let competence = hojeCompetencia();
  if (cfg.competence) {
    const compEl = document.getElementById(cfg.competence);
    competence = compEl?.value?.trim() || "";
    if (!competence) { addMessage("error", "Informe a competência antes de importar."); if (feedbackEl) feedbackEl.textContent = ""; return; }
  }
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

// ─── Busca da pessoa a vincular ─────────────────────────────────────────────

async function buscarPessoaVinculada() {
  const campo = document.getElementById("person-search-input");
  const termo = ((campo ? campo.value : state.ui.personQuery) || "").trim();
  state.ui.personQuery = termo;
  if (termo.length < 3) { addMessage("warn", "Digite ao menos 3 letras."); return; }
  state.ui.personSearching = true; requestRender();
  try {
    const r = await api("/api/admin/people/search", {
      method: "POST", body: JSON.stringify({ q: termo }),
    });
    state.ui.personResults = r.candidates || [];
    if (!state.ui.personResults.length) {
      addMessage("warn", "Nenhuma pessoa encontrada. Confira a grafia ou cadastre a pessoa primeiro.");
    }
  } catch (e) {
    addMessage("error", e.message);
    state.ui.personResults = [];
  } finally {
    state.ui.personSearching = false;
    requestRender();
  }
}

function escolherPessoaVinculada(indice) {
  const c = (state.ui.personResults || [])[indice];
  if (!c || !state.userEditor) return;
  state.userEditor.linkedPersonName = c.personName;
  state.userEditor.linkedPersonSource = [c.source, c.detail].filter(Boolean).join(" · ");
  state.ui.personResults = null;
  state.ui.personQuery = "";
  requestRender();
}

function limparPessoaVinculada() {
  if (!state.userEditor) return;
  state.userEditor.linkedPersonName = "";
  state.userEditor.linkedPersonSource = "";
  state.ui.personResults = null;
  state.ui.personQuery = "";
  requestRender();
}

/** Leva o nome para o formulário de desligamento e rola até ele. */
function prepararDesligamento(nome) {
  const campo = document.getElementById("term-person-name");
  if (!campo) return;
  campo.value = nome;
  campo.focus();
  campo.scrollIntoView({ behavior: "smooth", block: "center" });
  addMessage("info", `Informe o mês em que ${nome} saiu e clique em Registrar desligamento.`);
}

async function submitPersonTermination(reativar) {
  const nome = document.getElementById("term-person-name")?.value?.trim();
  const mes = document.getElementById("term-person-month")?.value;
  if (!nome) { addMessage("error", "Informe a pessoa."); return; }
  if (!reativar && !mes) { addMessage("error", "Informe o mês de desligamento."); return; }
  if (!reativar && !confirm(
      `Registrar o desligamento de ${nome} em ${mes}?\n\n` +
      "Ela sai das listas de equipe, meta e presença a partir daí, e a conta de acesso é " +
      "desativada. O histórico dos meses trabalhados continua intacto.")) return;
  try {
    const r = await api("/api/admin/people/terminate", {
      method: "POST",
      body: JSON.stringify({ personName: nome, terminationMonth: mes, reactivate: Boolean(reativar) }),
    });
    addMessage("success", r.message || "Atualizado.");
    document.getElementById("term-person-name").value = "";
    await loadAdmin();
    loadCrmData();
  } catch (e) { addMessage("error", e.message); }
}

async function submitNewPerson() {
  const nome = document.getElementById("new-person-name")?.value?.trim();
  const funcao = document.getElementById("new-person-role")?.value;
  const unidade = document.getElementById("new-person-unit")?.value;
  const inicio = document.getElementById("new-person-from")?.value;
  if (!nome || !unidade) { addMessage("error", "Informe o nome e a unidade."); return; }
  try {
    const r = await api("/api/admin/people/save", {
      method: "POST",
      body: JSON.stringify({ personName: nome, roleClassification: funcao,
                             baseUnit: unidade, validFrom: inicio }),
    });
    addMessage("success", r.message || "Pessoa cadastrada.");
    document.getElementById("new-person-name").value = "";
    await loadAdmin();
    loadProspects(true);
  } catch (e) { addMessage("error", e.message); }
}

async function submitPersonUnit() {
  const name = document.getElementById("edit-seller-name")?.value?.trim();
  const unit = document.getElementById("edit-seller-unit")?.value;
  if (!name || !unit) { addMessage("error", "Selecione o vendedor e a unidade."); return; }
  try {
    const result = await api("/api/admin/people/update-unit", { method: "POST", body: JSON.stringify({ person_name: name, base_unit: unit }) });
    addMessage("success", result.message || "Vendedor atualizado.");
    await loadAdmin();
  } catch (error) {
    addMessage("error", error.message);
  }
}

async function submitCityUnit() {
  const name = document.getElementById("edit-city-name")?.value?.trim();
  const unit = document.getElementById("edit-city-unit")?.value;
  if (!name || !unit) { addMessage("error", "Selecione a cidade e a unidade."); return; }
  try {
    const result = await api("/api/admin/city/update-unit", { method: "POST", body: JSON.stringify({ city_name: name, principal_unit: unit }) });
    addMessage("success", result.message || "Cidade atualizada.");
    await loadAdmin();
  } catch (error) {
    addMessage("error", error.message);
  }
}

async function saveUser(event) {
  if (event) event.preventDefault();
  const editor = state.userEditor || {};
  const username = (document.getElementById("user-username")?.value ?? editor.username ?? "").trim();
  const fullName = (document.getElementById("user-full-name")?.value ?? editor.fullName ?? "").trim();
  const password = document.getElementById("user-password")?.value ?? editor.password ?? "";
  const profile = accessProfileById(editor.profileId);
  if (!username || !fullName) { addMessage("error", "Informe o usuário e o nome completo."); return; }
  if (!profile) { addMessage("error", "Selecione o perfil de acesso."); return; }
  if (!editor.id && !password) { addMessage("error", "Defina a senha inicial."); return; }

  const scope = profile.dataScope;
  // Lê o vínculo para qualquer perfil — obrigatório só para vendedor, mas
  // salvo sempre: é o que liga a conta ao nome nas listas de presença das atas.
  // Vem só da busca — não há mais campo de digitação livre.
  const linkedPerson = (editor.linkedPersonName || "").trim();
  const linkedUnits = ["unidade", "unidade_consolidado"].includes(scope) ? (editor.linkedUnits || []) : [];

  if (scope === "proprio" && !linkedPerson) {
    addMessage("error", "Este perfil exige vincular a pessoa (vendedor)."); return;
  }
  if (scope === "proprio" && !(editor.baseUnit || "").trim()) {
    addMessage("error", "Escolha a unidade do vendedor — é ela que define carteira, meta e equipe.");
    return;
  }
  if (["unidade", "unidade_consolidado"].includes(scope) && !linkedUnits.length) {
    addMessage("error", "Este perfil exige ao menos uma unidade vinculada."); return;
  }

  const payload = {
    id: editor.id || undefined,
    username,
    full_name: fullName,
    profile_id: profile.id,
    role: profile.name,
    linked_person_name: linkedPerson,
    linked_units: linkedUnits,
    base_unit: scope === "proprio" ? (editor.baseUnit || "") : "",
    password,
  };
  try {
    const result = await api("/api/admin/users", { method: "POST", body: JSON.stringify(payload) });
    addMessage("success", result.message || "Usuário salvo.");
    resetUserEditor();
    await loadAdmin();
  } catch (error) {
    addMessage("error", error.message);
  }
}

// ─── Perfis de acesso ───────────────────────────────────────────────────────

function startProfileEdit(profileId) {
  const profile = accessProfileById(profileId);
  if (!profile) return;
  state.profileEditor = {
    id: profile.id,
    name: profile.name,
    description: profile.description || "",
    modules: [...(profile.modules || [])],
    dataScope: profile.dataScope || "todos",
    canManageUsers: Boolean(profile.canManageUsers),
    isSystem: Boolean(profile.isSystem),
  };
  requestRender();
  document.getElementById("profile-editor-card")?.scrollIntoView({ behavior: "smooth", block: "center" });
}

function cancelProfileEdit() {
  resetProfileEditor();
  requestRender();
}

function toggleProfileModule(moduleId) {
  const list = state.profileEditor.modules || [];
  state.profileEditor.modules = list.includes(moduleId)
    ? list.filter((m) => m !== moduleId)
    : [...list, moduleId];
  requestRender();
}

function toggleProfileModuleGroup(group) {
  const groupIds = (state.admin?.accessModules || []).filter((m) => m.group === group).map((m) => m.id);
  const current = state.profileEditor.modules || [];
  const allSelected = groupIds.every((id) => current.includes(id));
  state.profileEditor.modules = allSelected
    ? current.filter((id) => !groupIds.includes(id))
    : Array.from(new Set([...current, ...groupIds]));
  requestRender();
}

async function saveProfile(event) {
  if (event) event.preventDefault();
  const editor = state.profileEditor || {};
  const name = (editor.name || "").trim();
  if (!name) { addMessage("error", "Informe o nome do perfil."); return; }
  if (!(editor.modules || []).length) { addMessage("error", "Selecione ao menos uma tela."); return; }
  try {
    const result = await api("/api/admin/profiles", {
      method: "POST",
      body: JSON.stringify({
        id: editor.id || undefined,
        name,
        description: editor.description || "",
        modules: editor.modules,
        dataScope: editor.dataScope || "todos",
        canManageUsers: Boolean(editor.canManageUsers),
      }),
    });
    addMessage("success", result.message || "Perfil salvo.");
    resetProfileEditor();
    await loadAdmin();
  } catch (error) {
    addMessage("error", error.message);
  }
}

async function deleteProfile(profileId) {
  const profile = accessProfileById(profileId);
  if (!profile) return;
  if (!confirm(`Excluir o perfil "${profile.name}"?`)) return;
  try {
    await api("/api/admin/profiles/delete", { method: "POST", body: JSON.stringify({ id: profileId }) });
    addMessage("success", "Perfil excluído.");
    await loadAdmin();
  } catch (error) {
    addMessage("error", error.message);
  }
}

function cancelUserEdit() {
  resetUserEditor();
  state.ui.personResults = null;
  state.ui.personQuery = "";
  requestRender();
}

async function startPasswordChange(userId) {
  const pwd = window.prompt("Nova senha para este usuário:");
  if (!pwd) return;
  try {
    await api("/api/admin/users/password", { method: "POST", body: JSON.stringify({ id: userId, password: pwd }) });
    addMessage("success", "Senha atualizada.");
  } catch (error) {
    addMessage("error", error.message);
  }
}

async function deleteUser(userId) {
  if (!confirm("Excluir este usuário? Esta ação não pode ser desfeita.")) return;
  try {
    await api("/api/admin/users/delete", { method: "POST", body: JSON.stringify({ id: userId }) });
    addMessage("success", "Usuário excluído.");
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
