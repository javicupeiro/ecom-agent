// SaborMix chat client. Talks to the FastAPI backend (POST /chat) and renders,
// on the right, a step-by-step trace of every turn: model calls, tool calls and
// their results, token usage and the final reply.

const API = "";

const el = {
  chat: document.getElementById("chat"),
  composer: document.getElementById("composer"),
  empty: document.getElementById("empty-state"),
  input: document.getElementById("input"),
  send: document.getElementById("send"),
  reset: document.getElementById("reset-btn"),
  trace: document.getElementById("trace"),
  traceEmpty: document.getElementById("trace-empty"),  // panel-empty div; removed on first trace
  traceClear: document.getElementById("trace-clear"),
  status: document.getElementById("status"),
  statusText: document.getElementById("status-text"),
  modelPill: document.getElementById("model-pill"),
  statCalls: document.getElementById("stat-calls"),
  statTokens: document.getElementById("stat-tokens"),
  statTools: document.getElementById("stat-tools"),
};

const state = {
  sessionId: newSessionId(),
  turn: 0,
  totals: { calls: 0, inTokens: 0, outTokens: 0, tools: 0 },
};

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

function nowTime() {
  return new Date().toLocaleTimeString("es-ES", { hour12: false });
}

function scrollToEnd(container) {
  container.scrollTop = container.scrollHeight;
}

// ───────── Chat rendering ─────────

function addBubble(role, text, { error = false } = {}) {
  if (el.empty) el.empty.remove();
  const bubble = node("div", `bubble ${role}${error ? " error" : ""}`);
  const meta = node("div", "bubble-meta", role === "user" ? "Tú" : "SaborMix");
  const body = node("div", "bubble-body", text);
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
  const main = node("div");
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
  const calls = trace.provider_calls || 0;

  const turn = node("div", "trace-turn");

  const head = node("div", "trace-turn-head");
  head.appendChild(node("span", "turn-index", `Turno ${state.turn}`));
  const headRight = node("span", "turn-time",
    `↑${usage.input_tokens} ↓${usage.output_tokens} · ${nowTime()}`);
  head.appendChild(headRight);
  turn.appendChild(head);

  const events = node("div", "trace-events");

  // 1) The user request that started the turn.
  events.appendChild(evt("usuario", "request", "Mensaje recibido", { detail: userText }));

  // 2) The agent loop: the model reasons and may call tools.
  events.appendChild(
    evt("modelo", "llm", "El modelo razona y decide", {
      meta: `${calls} llamada(s) al proveedor`,
    }),
  );

  // 3) Each tool the model invoked, with input and result.
  for (const step of steps) {
    const detail = `input: ${truncate(step.input)}\n→ ${truncate(step.result)}`;
    events.appendChild(
      evt("tool", `tool${step.error ? " error" : ""}`, step.tool, {
        detail,
        tag: step.error ? { ok: false, text: "error" } : { ok: true, text: "ok" },
      }),
    );
  }

  // 4) The final answer (or error).
  if (data.error) {
    events.appendChild(evt("error", "error", "Fallo en el turno", { detail: data.error }));
  } else {
    events.appendChild(evt("respuesta", "reply", "Respuesta enviada", { detail: truncate(data.reply) }));
  }

  turn.appendChild(events);
  el.trace.appendChild(turn);
  scrollToEnd(el.trace);

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
  el.statusText.textContent = ok ? "Conectado" : "Sin conexión";
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
      body: JSON.stringify({ session_id: state.sessionId, message: text }),
    });
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    const data = await res.json();

    typing.remove();
    addBubble("agent", data.reply || "(sin respuesta)");
    renderTrace(text, data);
    setStatus(true);
  } catch (err) {
    typing.remove();
    const message = `No se pudo contactar con el agente (${err.message}).`;
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
  wrap.appendChild(node("div", "empty-title", "Pega o escribe tu consulta"));
  wrap.appendChild(
    node("div", "empty-sub",
      "El agente responderá sobre productos SaborMix, recetas y soporte con trazas visibles para cada llamada al modelo y a las herramientas."),
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
    <div class="pe-title">Sin actividad aún</div>
    <div class="pe-sub">El resumen estructurado del turno aparecerá aquí cuando envíes el primer mensaje.</div>
  `;
  el.trace.appendChild(wrap);
  el.traceEmpty = wrap;
  state.totals = { calls: 0, inTokens: 0, outTokens: 0, tools: 0 };
  el.statCalls.textContent = "0";
  el.statTokens.textContent = "0 / 0";
  el.statTools.textContent = "0";
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
el.reset.addEventListener("click", resetConversation);
el.traceClear.addEventListener("click", clearTraces);

checkHealth();
el.input.focus();
