// SaborMix chat client. Talks to the FastAPI backend (POST /chat) and renders,
// on the right, a step-by-step trace of every turn: model calls, tool calls and
// their results, token usage and the final reply.

const API = "";

const COPY = {
  es: {
    documentTitle: "SaborMix · Plataforma de Agentes",
    brandTitle: "SaborMix · Plataforma de Agentes",
    brandSub: "Chat comercial · recetas · soporte técnico",
    langLabel: "Español",
    langMenuTitle: "Seleccionar idioma",
    statusConnecting: "Conectando…",
    statusConnected: "Conectado",
    statusDisconnected: "Sin conexión",
    modelTitle: "Modelo activo",
    resetTitle: "Nueva conversación",
    tabAriaLabel: "Agentes",
    tabPill: "Agente conversacional",
    emptyTitle: "Pega o escribe tu consulta",
    emptySub: "El agente responderá sobre productos SaborMix, recetas y soporte con trazas visibles para cada llamada al modelo y a las herramientas.",
    inputPlaceholder: "Escribe tu mensaje…",
    hint: "Enter para enviar · Shift + Enter para salto de línea",
    send: "Enviar",
    traceTitle: "Actividad del agente",
    traceSub: "Cada turno muestra modelo, herramientas y respuesta",
    clearTraceTitle: "Limpiar trazas",
    expandTurn: "Desplegar turno",
    collapseTurn: "Compactar turno",
    panelEmptyTitle: "Sin actividad aún",
    panelEmptySub: "El resumen estructurado del turno aparecerá aquí cuando envíes el primer mensaje.",
    statCalls: "Llamadas",
    statTokens: "Tokens",
    statTools: "Herramientas",
    userMeta: "Tú",
    agentMeta: "SaborMix",
    turn: "Turno",
    eventUser: "usuario",
    eventModel: "modelo",
    eventReply: "respuesta",
    eventError: "error",
    eventUserLabel: "Mensaje recibido",
    eventModelLabel: "El modelo razona y decide",
    eventModelMeta: (calls) => `${calls} llamada(s) al proveedor`,
    eventModelSummary: (calls, tools) => `${calls} llamada(s) al modelo · ${tools} herramienta(s) ejecutada(s)`,
    eventModelStepLabel: (index) => `Paso del modelo ${index}`,
    eventModelStepMeta: (model, stopReason) => `${model || "modelo desconocido"} · ${stopReason}`,
    eventReplyLabel: "Respuesta enviada",
    eventErrorLabel: "Fallo en el turno",
    toolError: "error",
    toolOk: "ok",
    toolInputLabel: "Entrada",
    toolOutputLabel: "Resultado",
    toolStepLabel: (index) => `Ejecución ligada al paso ${index}`,
    stopReasonToolUse: "solicita herramientas",
    stopReasonEndTurn: "emite respuesta final",
    stopReasonMaxTokens: "alcanza el límite de tokens",
    noVisibleModelText: "Sin texto visible del modelo en este paso.",
    noReply: "(sin respuesta)",
    contactError: (message) => `No se pudo contactar con el agente (${message}).`,
    inputPrefix: "input",
    languageChanged: "Idioma cambiado a Español. Se ha iniciado una conversación nueva.",
  },
  en: {
    documentTitle: "SaborMix · Agent Platform",
    brandTitle: "SaborMix · Agent Platform",
    brandSub: "Sales chat · recipes · technical support",
    langLabel: "English",
    langMenuTitle: "Select language",
    statusConnecting: "Connecting…",
    statusConnected: "Connected",
    statusDisconnected: "Offline",
    modelTitle: "Active model",
    resetTitle: "New conversation",
    tabAriaLabel: "Agents",
    tabPill: "Conversational agent",
    emptyTitle: "Paste or type your request",
    emptySub: "The agent will answer about SaborMix products, recipes, and support with visible traces for each model and tool call.",
    inputPlaceholder: "Type your message…",
    hint: "Enter to send · Shift + Enter for a new line",
    send: "Send",
    traceTitle: "Agent activity",
    traceSub: "Each turn shows model, tools, and response",
    clearTraceTitle: "Clear traces",
    expandTurn: "Expand turn",
    collapseTurn: "Collapse turn",
    panelEmptyTitle: "No activity yet",
    panelEmptySub: "The structured turn summary will appear here when you send the first message.",
    statCalls: "Calls",
    statTokens: "Tokens",
    statTools: "Tools",
    userMeta: "You",
    agentMeta: "SaborMix",
    turn: "Turn",
    eventUser: "user",
    eventModel: "model",
    eventReply: "reply",
    eventError: "error",
    eventUserLabel: "Message received",
    eventModelLabel: "The model reasons and decides",
    eventModelMeta: (calls) => `${calls} provider call(s)`,
    eventModelSummary: (calls, tools) => `${calls} model call(s) · ${tools} tool run(s)`,
    eventModelStepLabel: (index) => `Model step ${index}`,
    eventModelStepMeta: (model, stopReason) => `${model || "unknown model"} · ${stopReason}`,
    eventReplyLabel: "Reply sent",
    eventErrorLabel: "Turn failed",
    toolError: "error",
    toolOk: "ok",
    toolInputLabel: "Input",
    toolOutputLabel: "Result",
    toolStepLabel: (index) => `Execution linked to step ${index}`,
    stopReasonToolUse: "requests tools",
    stopReasonEndTurn: "returns final answer",
    stopReasonMaxTokens: "hits token limit",
    noVisibleModelText: "No visible model text for this step.",
    noReply: "(no response)",
    contactError: (message) => `Could not contact the agent (${message}).`,
    inputPrefix: "input",
    languageChanged: "Language changed to English. A new conversation has been started.",
  },
};

const el = {
  brandTitle: document.querySelector(".brand-title"),
  brandSub: document.querySelector(".brand-sub"),
  tabbar: document.querySelector(".tabbar"),
  tabPill: document.querySelector(".tabbar-pill"),
  chat: document.getElementById("chat"),
  composer: document.getElementById("composer"),
  empty: document.getElementById("empty-state"),
  input: document.getElementById("input"),
  hint: document.querySelector(".hint"),
  sendLabel: document.querySelector(".btn-label"),
  send: document.getElementById("send"),
  reset: document.getElementById("reset-btn"),
  trace: document.getElementById("trace"),
  traceEmpty: document.getElementById("trace-empty"),  // panel-empty div; removed on first trace
  traceClear: document.getElementById("trace-clear"),
  traceTitle: document.querySelector(".trace-title"),
  traceSub: document.querySelector(".trace-sub"),
  status: document.getElementById("status"),
  statusText: document.getElementById("status-text"),
  modelPill: document.getElementById("model-pill"),
  statCalls: document.getElementById("stat-calls"),
  statTokens: document.getElementById("stat-tokens"),
  statTools: document.getElementById("stat-tools"),
  statCallsWrap: document.getElementById("stat-calls").parentElement,
  statTokensWrap: document.getElementById("stat-tokens").parentElement,
  statToolsWrap: document.getElementById("stat-tools").parentElement,
  langMenu: document.getElementById("lang-menu"),
  langTrigger: document.getElementById("lang-trigger"),
  langTriggerLabel: document.getElementById("lang-trigger-label"),
  langDropdown: document.getElementById("lang-dropdown"),
  langOptions: Array.from(document.querySelectorAll(".lang-option")),
};

const state = {
  sessionId: newSessionId(),
  lang: "es",
  turn: 0,
  totals: { calls: 0, inTokens: 0, outTokens: 0, tools: 0 },
};

function t() {
  return COPY[state.lang];
}

function newSessionId() {
  return "web-" + Math.random().toString(36).slice(2, 10);
}

// ───────── Helpers ─────────

function node(tag, className, text) {
  const n = document.createElement(tag);
  if (className) n.className = className;
  if (text != null) n.textContent = text;
  return n;
}

function truncate(value, max = 800) {
  const s = typeof value === "string" ? value : JSON.stringify(value);
  return s.length > max ? s.slice(0, max) + " …" : s;
}

function prettyValue(value) {
  if (value == null) return "";
  if (typeof value === "string") return value;
  try {
    return JSON.stringify(value, null, 2);
  } catch {
    return String(value);
  }
}

function nowTime() {
  const locale = state.lang === "en" ? "en-US" : "es-ES";
  return new Date().toLocaleTimeString(locale, { hour12: false });
}

function scrollToEnd(container) {
  container.scrollTop = container.scrollHeight;
}

function escapeHtml(text) {
  return String(text)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#39;");
}

function formatInline(text) {
  let html = escapeHtml(text);
  html = html.replace(/`([^`]+)`/g, "<code>$1</code>");
  html = html.replace(/\*\*([^*]+)\*\*/g, "<strong>$1</strong>");
  html = html.replace(/__([^_]+)__/g, "<strong>$1</strong>");
  html = html.replace(/(^|[^*])\*([^*]+)\*(?!\*)/g, "$1<em>$2</em>");
  html = html.replace(/(^|[^_])_([^_]+)_(?!_)/g, "$1<em>$2</em>");
  return html;
}

function tokenizeBlocks(text) {
  const normalized = String(text || "").replace(/\r\n/g, "\n").trim();
  if (!normalized) return [];

  const lines = normalized.split("\n");
  const blocks = [];
  let paragraph = [];
  let list = [];

  function flushParagraph() {
    if (!paragraph.length) return;
    blocks.push({ type: "paragraph", lines: paragraph });
    paragraph = [];
  }

  function flushList() {
    if (!list.length) return;
    blocks.push({ type: "list", items: list });
    list = [];
  }

  for (const rawLine of lines) {
    const line = rawLine.trim();
    if (!line) {
      flushParagraph();
      flushList();
      continue;
    }

    if (/^---+$/.test(line)) {
      flushParagraph();
      flushList();
      continue;
    }

    const headingMatch = line.match(/^#{1,6}\s+(.+)$/);
    if (headingMatch) {
      flushParagraph();
      flushList();
      blocks.push({ type: "heading", text: headingMatch[1].trim() });
      continue;
    }

    const listMatch = line.match(/^[-*•]\s+(.+)$/);
    if (listMatch) {
      flushParagraph();
      list.push(listMatch[1].trim());
      continue;
    }

    flushList();
    paragraph.push(line);
  }

  flushParagraph();
  flushList();
  return blocks;
}

function renderRichText(container, text) {
  const blocks = tokenizeBlocks(text);
  if (!blocks.length) {
    container.textContent = text || "";
    return;
  }

  for (const block of blocks) {
    if (block.type === "heading") {
      const heading = node("div", "msg-heading");
      heading.innerHTML = formatInline(block.text);
      container.appendChild(heading);
      continue;
    }

    if (block.type === "list") {
      const list = node("ul", "msg-list");
      for (const itemText of block.items) {
        const item = node("li");
        item.innerHTML = formatInline(itemText);
        list.appendChild(item);
      }
      container.appendChild(list);
      continue;
    }

    const paragraph = node("p", "msg-paragraph");
    paragraph.innerHTML = block.lines.map(formatInline).join("<br>");
    container.appendChild(paragraph);
  }
}

function localizeStopReason(reason) {
  if (reason === "tool_use") return t().stopReasonToolUse;
  if (reason === "max_tokens") return t().stopReasonMaxTokens;
  return t().stopReasonEndTurn;
}

function stepDetail(step) {
  return [
    `${t().toolInputLabel}:`,
    truncate(prettyValue(step.input), 1000),
    "",
    `${t().toolOutputLabel}:`,
    truncate(prettyValue(step.result), 1600),
  ].join("\n");
}

function modelCallDetail(call) {
  const parts = [];
  if (call.visible_text) parts.push(call.visible_text);
  if (call.tool_names && call.tool_names.length) {
    parts.push(`tools: ${call.tool_names.join(", ")}`);
  }
  if (!parts.length) parts.push(t().noVisibleModelText);
  return parts.join("\n\n");
}

// ───────── Chat rendering ─────────

function addBubble(role, text, { error = false } = {}) {
  if (el.empty) el.empty.remove();
  const bubble = node("div", `bubble ${role}${error ? " error" : ""}`);
  const meta = node("div", "bubble-meta", role === "user" ? t().userMeta : t().agentMeta);
  const body = node("div", `bubble-body${role === "agent" && !error ? " rich-text" : ""}`);
  if (role === "agent" && !error) {
    renderRichText(body, text);
  } else {
    body.textContent = text;
  }
  bubble.append(meta, body);
  el.chat.appendChild(bubble);
  scrollToEnd(el.chat);
  return bubble;
}

function addTyping() {
  if (el.empty) el.empty.remove();
  const bubble = node("div", "bubble agent");
  const typing = node("div", "typing");
  typing.append(node("span"), node("span"), node("span"));
  bubble.appendChild(typing);
  el.chat.appendChild(bubble);
  scrollToEnd(el.chat);
  return bubble;
}

// ───────── Trace rendering ─────────

function evt(kind, cls, label, { detail, tag, meta } = {}) {
  const row = node("div", `evt ${cls}`);
  row.appendChild(node("span", "evt-dot"));
  const main = node("div", "evt-main");
  const labelEl = node("div", "evt-label");
  labelEl.appendChild(node("span", "evt-kind", kind));
  labelEl.appendChild(document.createTextNode(label));
  if (tag) {
    const t = node("span", `evt-tag ${tag.ok ? "ok" : "err"}`, tag.text);
    labelEl.appendChild(t);
  }
  main.appendChild(labelEl);
  if (meta) main.appendChild(node("div", "evt-meta", meta));
  if (detail) main.appendChild(node("div", "evt-detail", detail));
  row.appendChild(main);
  return row;
}

function renderTrace(userText, data) {
  if (el.traceEmpty) el.traceEmpty.remove();
  state.turn += 1;

  const trace = data.trace || {};
  const usage = trace.usage || { input_tokens: 0, output_tokens: 0 };
  const steps = trace.steps || [];
  const traceCalls = trace.calls || [];
  const calls = trace.provider_calls || 0;

  const turn = node("div", "trace-turn");

  const head = node("div", "trace-turn-head");
  const headContent = node("div", "trace-turn-content");
  const headMain = node("div", "trace-turn-main");
  headMain.appendChild(node("span", "turn-index", `${t().turn} ${state.turn}`));
  headMain.appendChild(node("span", "turn-time",
    `↑${usage.input_tokens} ↓${usage.output_tokens} · ${nowTime()}`));

  const headMeta = node("div", "trace-turn-summary");
  headMeta.textContent = t().eventModelSummary(calls, steps.length);
  headContent.append(headMain, headMeta);

  head.appendChild(headContent);
  turn.appendChild(head);

  const body = node("div", "trace-turn-body");
  const events = node("div", "trace-events");

  events.appendChild(evt(t().eventUser, "request", t().eventUserLabel, { detail: userText }));

  events.appendChild(
    evt(t().eventModel, "llm", t().eventModelLabel, {
      meta: t().eventModelSummary(calls, steps.length),
    }),
  );

  if (traceCalls.length) {
    for (const call of traceCalls) {
      events.appendChild(
        evt(t().eventModel, "llm step", t().eventModelStepLabel(call.index), {
          meta: t().eventModelStepMeta(call.model || data.model, localizeStopReason(call.stop_reason)),
          detail: modelCallDetail(call),
        }),
      );

      for (const step of steps.filter((item) => item.call_index === call.index)) {
        events.appendChild(
          evt("tool", `tool${step.error ? " error" : ""}`, step.tool, {
            meta: t().toolStepLabel(step.call_index),
            detail: stepDetail(step),
            tag: step.error ? { ok: false, text: t().toolError } : { ok: true, text: t().toolOk },
          }),
        );
      }
    }
  } else {
    for (const step of steps) {
      events.appendChild(
        evt("tool", `tool${step.error ? " error" : ""}`, step.tool, {
          detail: stepDetail(step),
          tag: step.error ? { ok: false, text: t().toolError } : { ok: true, text: t().toolOk },
        }),
      );
    }
  }

  if (data.error) {
    events.appendChild(evt(t().eventError, "error", t().eventErrorLabel, { detail: data.error }));
  } else {
    events.appendChild(evt(t().eventReply, "reply", t().eventReplyLabel, { detail: truncate(data.reply) }));
  }

  body.appendChild(events);
  turn.appendChild(body);
  el.trace.prepend(turn);
  el.trace.scrollTop = 0;

  // Running totals in the footer.
  state.totals.calls += calls;
  state.totals.inTokens += usage.input_tokens || 0;
  state.totals.outTokens += usage.output_tokens || 0;
  state.totals.tools += steps.length;
  el.statCalls.textContent = state.totals.calls;
  el.statTokens.textContent = `${state.totals.inTokens} / ${state.totals.outTokens}`;
  el.statTools.textContent = state.totals.tools;

  const model = data.model || trace.model;
  if (model) el.modelPill.textContent = model;
}

// ───────── Networking ─────────

async function checkHealth() {
  try {
    const res = await fetch(`${API}/openapi.json`, { method: "GET" });
    setStatus(res.ok);
  } catch {
    setStatus(false);
  }
}

function setStatus(ok) {
  el.status.classList.toggle("ok", ok);
  el.status.classList.toggle("err", !ok);
  el.statusText.textContent = ok ? t().statusConnected : t().statusDisconnected;
}

async function sendMessage() {
  const text = el.input.value.trim();
  if (!text) return;

  el.input.value = "";
  autoResize();
  el.send.disabled = true;
  addBubble("user", text);
  const typing = addTyping();

  try {
    const res = await fetch(`${API}/chat`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ session_id: state.sessionId, message: text, lang: state.lang }),
    });
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    const data = await res.json();

    typing.remove();
    addBubble("agent", data.reply || t().noReply);
    renderTrace(text, data);
    setStatus(true);
  } catch (err) {
    typing.remove();
    const message = t().contactError(err.message);
    addBubble("agent", message, { error: true });
    renderTrace(text, { error: message, reply: message, trace: {} });
    setStatus(false);
  } finally {
    el.send.disabled = false;
    el.input.focus();
  }
}

// ───────── Reset / clear ─────────

function resetConversation() {
  state.sessionId = newSessionId();
  state.turn = 0;
  state.totals = { calls: 0, inTokens: 0, outTokens: 0, tools: 0 };
  el.chat.innerHTML = "";
  el.chat.appendChild(emptyState());
  clearTraces();
  el.input.focus();
}

function emptyState() {
  const wrap = node("div", "empty-state");
  wrap.id = "empty-state";
  wrap.appendChild(node("div", "empty-title", t().emptyTitle));
  wrap.appendChild(
    node("div", "empty-sub", t().emptySub),
  );
  el.empty = wrap;
  return wrap;
}

function clearTraces() {
  el.trace.innerHTML = "";
  const wrap = node("div", "panel-empty");
  wrap.id = "trace-empty";
  wrap.innerHTML = `
    <div class="pe-icon">
      <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor"
           stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round">
        <polyline points="22 12 18 12 15 21 9 3 6 12 2 12" />
      </svg>
    </div>
    <div class="pe-title">${t().panelEmptyTitle}</div>
    <div class="pe-sub">${t().panelEmptySub}</div>
  `;
  el.trace.appendChild(wrap);
  el.traceEmpty = wrap;
  state.totals = { calls: 0, inTokens: 0, outTokens: 0, tools: 0 };
  el.statCalls.textContent = "0";
  el.statTokens.textContent = "0 / 0";
  el.statTools.textContent = "0";
}

function applyLanguage(copyChanged = false) {
  const copy = t();
  document.documentElement.lang = state.lang;
  document.title = copy.documentTitle;
  el.brandTitle.textContent = copy.brandTitle;
  el.brandSub.textContent = copy.brandSub;
  el.tabbar.setAttribute("aria-label", copy.tabAriaLabel);
  el.tabPill.textContent = copy.tabPill;
  el.statusText.textContent = copy.statusConnecting;
  el.modelPill.title = copy.modelTitle;
  el.reset.title = copy.resetTitle;
  el.reset.setAttribute("aria-label", copy.resetTitle);
  el.input.placeholder = copy.inputPlaceholder;
  el.hint.textContent = copy.hint;
  el.sendLabel.textContent = copy.send;
  el.send.title = `${copy.send} (Enter)`;
  el.send.setAttribute("aria-label", copy.send);
  el.traceTitle.textContent = copy.traceTitle;
  el.traceSub.textContent = copy.traceSub;
  el.traceClear.title = copy.clearTraceTitle;
  el.traceClear.setAttribute("aria-label", copy.clearTraceTitle);
  el.statCallsWrap.firstChild.textContent = `${copy.statCalls} `;
  el.statTokensWrap.firstChild.textContent = `${copy.statTokens} `;
  el.statToolsWrap.firstChild.textContent = `${copy.statTools} `;
  el.langTrigger.title = copy.langMenuTitle;
  el.langTriggerLabel.textContent = copy.langLabel;
  for (const option of el.langOptions) {
    const active = option.dataset.lang === state.lang;
    option.classList.toggle("active", active);
    option.setAttribute("aria-checked", active ? "true" : "false");
  }
  if (copyChanged) {
    resetConversation();
    addBubble("agent", copy.languageChanged);
  } else {
    clearTraces();
    el.chat.innerHTML = "";
    el.chat.appendChild(emptyState());
  }
}

function toggleLangMenu(forceOpen) {
  const open = forceOpen ?? !el.langMenu.classList.contains("open");
  el.langMenu.classList.toggle("open", open);
  el.langTrigger.setAttribute("aria-expanded", open ? "true" : "false");
  el.langDropdown.hidden = !open;
}

function setLanguage(lang) {
  if (!COPY[lang] || lang === state.lang) {
    toggleLangMenu(false);
    return;
  }
  state.lang = lang;
  toggleLangMenu(false);
  applyLanguage(true);
  checkHealth();
}

// ───────── Input behavior ─────────

function autoResize() {
  el.input.style.height = "auto";
  el.input.style.height = Math.min(el.input.scrollHeight, 160) + "px";
}

el.input.addEventListener("input", autoResize);
el.input.addEventListener("keydown", (e) => {
  if (e.key === "Enter" && !e.shiftKey) {
    e.preventDefault();
    sendMessage();
  }
});
el.composer.addEventListener("submit", (e) => {
  e.preventDefault();
  sendMessage();
});
el.langTrigger.addEventListener("click", () => {
  toggleLangMenu();
});
for (const option of el.langOptions) {
  option.addEventListener("click", () => {
    setLanguage(option.dataset.lang);
  });
}
document.addEventListener("click", (e) => {
  if (!el.langMenu.contains(e.target)) {
    toggleLangMenu(false);
  }
});
el.reset.addEventListener("click", resetConversation);
el.traceClear.addEventListener("click", clearTraces);

applyLanguage(false);
checkHealth();
el.input.focus();
