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
    responseModeLabel: "Formato de respuesta",
    responseModeText: "Texto",
    responseModeVoice: "Voz",
    hint: "Enter para enviar · Shift + Enter para salto de línea",
    send: "Enviar",
    recordAudio: "Grabar audio",
    recorderIdle: "Listo para grabar",
    recorderRecording: "Grabando…",
    recorderPaused: "Grabacion en pausa",
    recorderResume: "Reanudar",
    recorderPause: "Pausar",
    recorderSend: "Enviar audio",
    recorderDelete: "Borrar",
    recorderSending: "Enviando audio…",
    recorderUnsupported: "Este navegador no permite grabar audio desde el microfono.",
    recorderPermissionError: "No se pudo acceder al microfono del sistema.",
    audioSent: (duration) => `Audio enviado · ${duration}`,
    userAudioMeta: "Tu audio",
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
    statFrustration: "Frustración",
    eventExtraction: "extraccion",
    eventExtractionLabel: "Parámetros extraídos",
    extractionCardTitle: "Resumen extraído",
    sessionExtractionTitle: "Estado de la entrevista",
    sessionExtractionSub: "Los datos estructurados recogidos en la sesión se actualizan aquí.",
    sessionExtractionEmpty: "Aún no hay datos estructurados en esta sesión.",
    extractionOrderNumber: "Número de pedido",
    extractionProblemCategory: "Categoría",
    extractionProblemDescription: "Descripción",
    extractionUrgencyLevel: "Urgencia",
    extractionMissing: "sin dato",
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
    playVoice: "Reproducir audio",
    stopVoice: "Detener audio",
    rewindVoice: "Retroceder 10 segundos",
    forwardVoice: "Avanzar 10 segundos",
    seekVoice: "Mover reproduccion",
    voiceMeta: "Respuesta de voz",
    voiceFallback: "Audio no disponible. Se muestra la respuesta en texto.",
    voiceLoading: "Cargando…",
    voiceUnavailable: "Audio no disponible",
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
    responseModeLabel: "Reply format",
    responseModeText: "Text",
    responseModeVoice: "Voice",
    hint: "Enter to send · Shift + Enter for a new line",
    send: "Send",
    recordAudio: "Record audio",
    recorderIdle: "Ready to record",
    recorderRecording: "Recording…",
    recorderPaused: "Recording paused",
    recorderResume: "Resume",
    recorderPause: "Pause",
    recorderSend: "Send audio",
    recorderDelete: "Delete",
    recorderSending: "Sending audio…",
    recorderUnsupported: "This browser cannot record audio from the microphone.",
    recorderPermissionError: "Could not access the system microphone.",
    audioSent: (duration) => `Audio sent · ${duration}`,
    userAudioMeta: "Your audio",
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
    statFrustration: "Frustration",
    eventExtraction: "extraction",
    eventExtractionLabel: "Extracted parameters",
    extractionCardTitle: "Extracted summary",
    sessionExtractionTitle: "Interview state",
    sessionExtractionSub: "The structured data collected in the session is updated here.",
    sessionExtractionEmpty: "No structured data has been collected in this session yet.",
    extractionOrderNumber: "Order number",
    extractionProblemCategory: "Category",
    extractionProblemDescription: "Description",
    extractionUrgencyLevel: "Urgency",
    extractionMissing: "missing",
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
    playVoice: "Play audio",
    stopVoice: "Stop audio",
    rewindVoice: "Rewind 10 seconds",
    forwardVoice: "Forward 10 seconds",
    seekVoice: "Seek playback",
    voiceMeta: "Voice reply",
    voiceFallback: "Audio unavailable. Showing the text reply instead.",
    voiceLoading: "Loading…",
    voiceUnavailable: "Audio unavailable",
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
  replyMode: document.getElementById("reply-mode"),
  replyModeLabel: document.getElementById("reply-mode-label"),
  replyModeButtons: Array.from(document.querySelectorAll(".reply-mode-btn")),
  recorderDot: document.getElementById("recorder-dot"),
  recorder: document.getElementById("recorder"),
  recorderText: document.getElementById("recorder-text"),
  recorderTime: document.getElementById("recorder-time"),
  recorderToggle: document.getElementById("recorder-toggle"),
  recorderSend: document.getElementById("recorder-send"),
  recorderDelete: document.getElementById("recorder-delete"),
  recordBtn: document.getElementById("record-btn"),
  hint: document.querySelector(".hint"),
  sendLabel: document.querySelector(".btn-label"),
  send: document.getElementById("send"),
  reset: document.getElementById("reset-btn"),
  sessionExtraction: document.getElementById("session-extraction"),
  sessionExtractionTitle: document.getElementById("session-extraction-title"),
  sessionExtractionSub: document.getElementById("session-extraction-sub"),
  sessionExtractionBody: document.getElementById("session-extraction-body"),
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
  statFrustration: document.getElementById("stat-frustration"),
  statCallsWrap: document.getElementById("stat-calls").parentElement,
  statTokensWrap: document.getElementById("stat-tokens").parentElement,
  statToolsWrap: document.getElementById("stat-tools").parentElement,
  statFrustrationWrap: document.getElementById("stat-frustration").parentElement,
  langMenu: document.getElementById("lang-menu"),
  langTrigger: document.getElementById("lang-trigger"),
  langTriggerLabel: document.getElementById("lang-trigger-label"),
  langDropdown: document.getElementById("lang-dropdown"),
  langOptions: Array.from(document.querySelectorAll(".lang-option")),
};

const state = {
  sessionId: newSessionId(),
  lang: "es",
  responseMode: "text",
  turn: 0,
  totals: { calls: 0, inTokens: 0, outTokens: 0, tools: 0 },
  activeAudio: null,
  activeAudioButton: null,
  activeAudioBubble: null,
  activeAudioWave: null,
  activeAudioSeek: null,
  activeAudioTime: null,
  mediaRecorder: null,
  recordingStream: null,
  recordingChunks: [],
  recordingBlob: null,
  recordingMimeType: "audio/webm",
  recordingStatus: "idle",
  recordingElapsedMs: 0,
  recordingStartedAt: 0,
  recordingTimer: null,
  recordingStopResolve: null,
  latestExtraction: null,
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

function formatDuration(seconds) {
  const safe = Number.isFinite(seconds) && seconds > 0 ? Math.floor(seconds) : 0;
  const mins = Math.floor(safe / 60);
  const secs = String(safe % 60).padStart(2, "0");
  return `${mins}:${secs}`;
}

function formatDurationMs(ms) {
  return formatDuration(Math.round(ms / 1000));
}

function scrollToEnd(container) {
  container.scrollTop = container.scrollHeight;
}

function preferredRecordingMimeType() {
  if (typeof MediaRecorder === "undefined") return "";
  const candidates = [
    "audio/webm;codecs=opus",
    "audio/webm",
    "audio/ogg;codecs=opus",
    "audio/ogg",
    "audio/mp4",
  ];
  for (const candidate of candidates) {
    if (typeof MediaRecorder.isTypeSupported !== "function" || MediaRecorder.isTypeSupported(candidate)) {
      return candidate;
    }
  }
  return "";
}

function recordingDurationMs() {
  if (state.recordingStatus !== "recording") {
    return state.recordingElapsedMs;
  }
  return state.recordingElapsedMs + Math.max(0, Date.now() - state.recordingStartedAt);
}

function stopRecordingTimer() {
  if (state.recordingTimer) {
    clearInterval(state.recordingTimer);
    state.recordingTimer = null;
  }
}

function startRecordingTimer() {
  stopRecordingTimer();
  state.recordingTimer = setInterval(() => {
    el.recorderTime.textContent = formatDurationMs(recordingDurationMs());
  }, 250);
}

function stopRecordingTracks() {
  if (!state.recordingStream) return;
  for (const track of state.recordingStream.getTracks()) {
    track.stop();
  }
  state.recordingStream = null;
}

function resetRecorderState() {
  stopRecordingTimer();
  stopRecordingTracks();
  state.mediaRecorder = null;
  state.recordingChunks = [];
  state.recordingBlob = null;
  state.recordingMimeType = "audio/webm";
  state.recordingStatus = "idle";
  state.recordingElapsedMs = 0;
  state.recordingStartedAt = 0;
  state.recordingStopResolve = null;
}

function applyRecorderUI() {
  const copy = t();
  const active = state.recordingStatus !== "idle";
  el.recorder.hidden = !active;
  el.recordBtn.disabled = state.recordingStatus === "sending";
  el.recordBtn.title = copy.recordAudio;
  el.recordBtn.setAttribute("aria-label", copy.recordAudio);
  el.recorderDot.classList.remove("idle", "recording", "paused", "sending");

  if (!active) {
    el.recorderDot.classList.add("idle");
    el.recorderText.textContent = copy.recorderIdle;
    el.recorderTime.textContent = "0:00";
    el.recorderToggle.textContent = copy.recorderPause;
    el.recorderSend.textContent = copy.recorderSend;
    el.recorderDelete.textContent = copy.recorderDelete;
    el.recorderToggle.disabled = true;
    el.recorderSend.disabled = true;
    el.recorderDelete.disabled = true;
    return;
  }

  el.recorderTime.textContent = formatDurationMs(recordingDurationMs());
  el.recorderSend.textContent = copy.recorderSend;
  el.recorderDelete.textContent = copy.recorderDelete;

  if (state.recordingStatus === "recording") {
    el.recorderDot.classList.add("recording");
    el.recorderText.textContent = copy.recorderRecording;
    el.recorderToggle.textContent = copy.recorderPause;
    el.recorderToggle.disabled = false;
    el.recorderSend.disabled = false;
    el.recorderDelete.disabled = false;
    return;
  }

  if (state.recordingStatus === "paused") {
    el.recorderDot.classList.add("paused");
    el.recorderText.textContent = copy.recorderPaused;
    el.recorderToggle.textContent = copy.recorderResume;
    el.recorderToggle.disabled = false;
    el.recorderSend.disabled = false;
    el.recorderDelete.disabled = false;
    return;
  }

  if (state.recordingStatus === "sending") {
    el.recorderDot.classList.add("sending");
    el.recorderText.textContent = copy.recorderSending;
    el.recorderToggle.textContent = copy.recorderPause;
    el.recorderToggle.disabled = true;
    el.recorderSend.disabled = true;
    el.recorderDelete.disabled = true;
  }
}

function recorderFilename() {
  if (state.recordingMimeType.includes("ogg")) return "recording.ogg";
  if (state.recordingMimeType.includes("mp4")) return "recording.m4a";
  return "recording.webm";
}

async function blobToBase64(blob) {
  const buffer = await blob.arrayBuffer();
  let binary = "";
  const bytes = new Uint8Array(buffer);
  const chunkSize = 0x8000;
  for (let index = 0; index < bytes.length; index += chunkSize) {
    binary += String.fromCharCode(...bytes.subarray(index, index + chunkSize));
  }
  return btoa(binary);
}

function waitForRecorderStop() {
  return new Promise((resolve) => {
    state.recordingStopResolve = resolve;
  });
}

function finalizeRecordingBlob() {
  if (!state.recordingChunks.length) return null;
  return new Blob(state.recordingChunks, { type: state.recordingMimeType || "audio/webm" });
}

async function startRecording() {
  if (!navigator.mediaDevices?.getUserMedia || typeof MediaRecorder === "undefined") {
    addBubble("agent", t().recorderUnsupported, { error: true });
    return;
  }

  try {
    const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
    const mimeType = preferredRecordingMimeType();
    const recorder = mimeType ? new MediaRecorder(stream, { mimeType }) : new MediaRecorder(stream);

    state.recordingStream = stream;
    state.mediaRecorder = recorder;
    state.recordingChunks = [];
    state.recordingBlob = null;
    state.recordingMimeType = recorder.mimeType || mimeType || "audio/webm";
    state.recordingElapsedMs = 0;
    state.recordingStartedAt = Date.now();
    state.recordingStatus = "recording";
    applyRecorderUI();
    startRecordingTimer();

    recorder.addEventListener("dataavailable", (event) => {
      if (event.data && event.data.size > 0) {
        state.recordingChunks.push(event.data);
      }
    });

    recorder.addEventListener("pause", () => {
      state.recordingElapsedMs = recordingDurationMs();
      state.recordingStartedAt = 0;
      state.recordingBlob = finalizeRecordingBlob();
      state.recordingStatus = "paused";
      stopRecordingTimer();
      applyRecorderUI();
    });

    recorder.addEventListener("resume", () => {
      state.recordingStartedAt = Date.now();
      state.recordingStatus = "recording";
      startRecordingTimer();
      applyRecorderUI();
    });

    recorder.addEventListener("stop", () => {
      state.recordingElapsedMs = recordingDurationMs();
      state.recordingStartedAt = 0;
      state.recordingBlob = finalizeRecordingBlob();
      stopRecordingTimer();
      stopRecordingTracks();
      if (typeof state.recordingStopResolve === "function") {
        state.recordingStopResolve(state.recordingBlob);
        state.recordingStopResolve = null;
      }
      if (state.recordingStatus !== "sending") {
        state.recordingStatus = state.recordingBlob ? "paused" : "idle";
        applyRecorderUI();
      }
    });

    recorder.start(250);
  } catch {
    resetRecorderState();
    applyRecorderUI();
    addBubble("agent", t().recorderPermissionError, { error: true });
  }
}

async function toggleRecorder() {
  const recorder = state.mediaRecorder;
  if (!recorder) return;
  if (state.recordingStatus === "recording") {
    recorder.pause();
    recorder.requestData();
    return;
  }
  if (state.recordingStatus === "paused") {
    recorder.resume();
  }
}

async function deleteRecording() {
  const recorder = state.mediaRecorder;
  if (recorder && recorder.state !== "inactive") {
    state.recordingChunks = [];
    recorder.stop();
  }
  resetRecorderState();
  applyRecorderUI();
}

async function ensureRecordingBlob() {
  if (state.recordingBlob) return state.recordingBlob;
  const recorder = state.mediaRecorder;
  if (!recorder) return null;
  if (recorder.state !== "inactive") {
    const stopped = waitForRecorderStop();
    recorder.stop();
    return stopped;
  }
  state.recordingBlob = finalizeRecordingBlob();
  return state.recordingBlob;
}

function renderAgentTurn(data, fallbackUserText) {
  const output = data.output || { mode: "text", text: data.reply };
  if (output.mode === "voice" && output.audio_base64) {
    addVoiceBubble(output, { role: "agent" });
  } else {
    addBubble("agent", output.text || data.reply || t().noReply, {
      metaText: output.voice_error ? `${t().agentMeta} · ${t().voiceFallback}` : "",
    });
  }
  renderTrace(data.input_text || fallbackUserText, data);
}

async function sendRecordedAudio() {
  if (state.recordingStatus !== "paused" && state.recordingStatus !== "recording") return;
  const blob = await ensureRecordingBlob();
  if (!blob) return;

  const duration = formatDurationMs(state.recordingElapsedMs);
  const mimeType = blob.type || state.recordingMimeType || "audio/webm";
  const filename = recorderFilename();
  const audioBase64 = await blobToBase64(blob);

  state.recordingStatus = "sending";
  applyRecorderUI();
  el.send.disabled = true;
  addVoiceBubble(
    {
      audio_base64: audioBase64,
      mime_type: mimeType,
      voice_label: t().userAudioMeta,
    },
    { role: "user", metaText: `${t().userMeta} · ${t().userAudioMeta} · ${duration}` },
  );
  const typing = addTyping();

  try {
    const res = await fetch(`${API}/chat/audio`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        session_id: state.sessionId,
        audio_base64: audioBase64,
        mime_type: mimeType,
        filename,
        lang: state.lang,
        response_mode: state.responseMode,
      }),
    });
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    const data = await res.json();

    typing.remove();
    renderAgentTurn(data, t().audioSent(duration));
    setStatus(true);
  } catch (err) {
    typing.remove();
    const message = t().contactError(err.message);
    addBubble("agent", message, { error: true });
    renderTrace(t().audioSent(duration), { error: message, reply: message, trace: {}, input_text: t().audioSent(duration) });
    setStatus(false);
  } finally {
    resetRecorderState();
    applyRecorderUI();
    el.send.disabled = false;
    el.input.focus();
  }
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


function extractionDetail(extraction) {
  const info = extraction || {};
  const frustrationValue = typeof info.frustration === "number"
    ? `${Math.round(info.frustration * 100)}%`
    : t().extractionMissing;
  return [
    `${t().extractionOrderNumber}: ${info.order_number || t().extractionMissing}`,
    `${t().extractionProblemCategory}: ${info.problem_category || t().extractionMissing}`,
    `${t().extractionProblemDescription}: ${info.problem_description || t().extractionMissing}`,
    `${t().statFrustration}: ${frustrationValue}`,
    `${t().extractionUrgencyLevel}: ${info.urgency_level || t().extractionMissing}`,
  ].join("\n");
}

function extractionPillClass(frustration) {
  if (frustration >= 0.7) return "high";
  if (frustration >= 0.4) return "medium";
  return "low";
}

function renderExtractionCard(extraction) {
  const info = extraction || {};
  const wrap = node("section", "extraction-card");
  const title = node("div", "extraction-card-title", t().extractionCardTitle);
  const grid = node("div", "extraction-grid");
  const frustration = typeof info.frustration === "number" ? info.frustration : 0;
  const frustrationPct = `${Math.round(frustration * 100)}%`;

  const items = [
    [t().extractionOrderNumber, info.order_number || t().extractionMissing],
    [t().extractionProblemCategory, info.problem_category || t().extractionMissing],
    [t().extractionProblemDescription, info.problem_description || t().extractionMissing],
    [t().extractionUrgencyLevel, info.urgency_level || t().extractionMissing],
  ];

  for (const [label, value] of items) {
    const item = node("div", "extraction-item");
    item.appendChild(node("div", "extraction-label", label));
    item.appendChild(node("div", "extraction-value", value));
    grid.appendChild(item);
  }

  const frustrationItem = node("div", "extraction-item extraction-item-frustration");
  frustrationItem.appendChild(node("div", "extraction-label", t().statFrustration));
  const frustrationRow = node("div", "extraction-frustration-row");
  const pill = node(
    "span",
    `extraction-pill ${extractionPillClass(frustration)}`,
    frustrationPct,
  );
  const meter = node("div", "extraction-meter");
  const fill = node("div", `extraction-meter-fill ${extractionPillClass(frustration)}`);
  fill.style.width = frustrationPct;
  meter.appendChild(fill);
  frustrationRow.append(pill, meter);
  frustrationItem.appendChild(frustrationRow);
  grid.appendChild(frustrationItem);

  wrap.append(title, grid);
  return wrap;
}

function updateSessionExtraction(extraction = null) {
  state.latestExtraction = extraction;
  el.sessionExtractionBody.innerHTML = "";

  if (!extraction) {
    el.sessionExtractionBody.appendChild(
      node("div", "session-extraction-empty", t().sessionExtractionEmpty),
    );
    return;
  }

  const card = renderExtractionCard(extraction);
  card.classList.add("session-extraction-card");
  el.sessionExtractionBody.appendChild(card);
}
function addBubble(role, text, { error = false, metaText = "" } = {}) {
  if (el.empty) el.empty.remove();
  const bubble = node("div", `bubble ${role}${error ? " error" : ""}`);
  const meta = node("div", "bubble-meta", metaText || (role === "user" ? t().userMeta : t().agentMeta));
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

function playIcon() {
  return `
    <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor" aria-hidden="true">
      <path d="M8 6.5v11l9-5.5-9-5.5Z" />
    </svg>
  `;
}

function stopIcon() {
  return `
    <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor" aria-hidden="true">
      <rect x="7" y="7" width="10" height="10" rx="1.8" />
    </svg>
  `;
}

function setVoiceButtonState(button, isPlaying) {
  button.innerHTML = isPlaying ? stopIcon() : playIcon();
  button.setAttribute("aria-label", isPlaying ? t().stopVoice : t().playVoice);
  button.title = isPlaying ? t().stopVoice : t().playVoice;
}

function stopActiveVoice() {
  const audio = state.activeAudio;
  if (!audio) return;
  audio.pause();
  audio.currentTime = 0;
  if (state.activeAudioBubble) state.activeAudioBubble.classList.remove("playing");
  if (state.activeAudioWave) state.activeAudioWave.style.setProperty("--progress", "0%");
  if (state.activeAudioSeek) state.activeAudioSeek.value = "0";
  if (state.activeAudioTime) {
    const total = Number(state.activeAudioTime.dataset.duration || 0);
    state.activeAudioTime.textContent = formatDuration(total);
  }
  if (state.activeAudioButton) setVoiceButtonState(state.activeAudioButton, false);
  state.activeAudio = null;
  state.activeAudioButton = null;
  state.activeAudioBubble = null;
  state.activeAudioWave = null;
  state.activeAudioSeek = null;
  state.activeAudioTime = null;
}

function clampTime(value, duration) {
  if (!Number.isFinite(duration) || duration <= 0) return 0;
  return Math.max(0, Math.min(duration, value));
}

function seekAudio(audio, nextTime) {
  const duration = Number.isFinite(audio.duration) ? audio.duration : 0;
  audio.currentTime = clampTime(nextTime, duration);
}

function addVoiceBubble(output, { role = "agent", metaText = "" } = {}) {
  if (el.empty) el.empty.remove();

  const bubble = node("div", `bubble ${role} voice`);
  const voiceLabel = output.voice_label || t().voiceMeta;
  const defaultMeta = role === "user" ? `${t().userMeta} · ${voiceLabel}` : `${t().agentMeta} · ${voiceLabel}`;
  const meta = node("div", "bubble-meta", metaText || defaultMeta);
  const player = node("div", "voice-player");
  const transport = node("div", "voice-transport");
  const button = document.createElement("button");
  button.className = "voice-play-btn";
  button.type = "button";
  setVoiceButtonState(button, false);

  const rewind = document.createElement("button");
  rewind.className = "voice-skip-btn";
  rewind.type = "button";
  rewind.textContent = "-10";
  rewind.setAttribute("aria-label", t().rewindVoice);
  rewind.title = t().rewindVoice;

  const forward = document.createElement("button");
  forward.className = "voice-skip-btn";
  forward.type = "button";
  forward.textContent = "+10";
  forward.setAttribute("aria-label", t().forwardVoice);
  forward.title = t().forwardVoice;

  const wave = node("div", "voice-wave");
  wave.style.setProperty("--progress", "0%");
  const fill = node("div", "voice-wave-fill");
  wave.appendChild(fill);
  for (const h of [20, 34, 26, 42, 18, 30, 40, 24, 36, 22, 38, 26, 16, 31, 43, 28]) {
    const bar = node("span", "voice-wave-bar");
    bar.style.setProperty("--bar-h", `${h}%`);
    wave.appendChild(bar);
  }

  const seek = document.createElement("input");
  seek.className = "voice-seek";
  seek.type = "range";
  seek.min = "0";
  seek.max = "1000";
  seek.step = "1";
  seek.value = "0";
  seek.setAttribute("aria-label", t().seekVoice);

  const time = node("div", "voice-time", t().voiceLoading);
  time.dataset.duration = "0";
  transport.append(rewind, button, forward);
  player.append(transport, wave, seek, time);
  bubble.append(meta, player);
  el.chat.appendChild(bubble);
  scrollToEnd(el.chat);

  if (!output.audio_base64) {
    time.textContent = t().voiceUnavailable;
    button.disabled = true;
    rewind.disabled = true;
    forward.disabled = true;
    seek.disabled = true;
    return bubble;
  }

  const audio = new Audio(`data:${output.mime_type || "audio/mpeg"};base64,${output.audio_base64}`);
  audio.preload = "metadata";

  function syncFromPlayback() {
    const duration = Number.isFinite(audio.duration) ? audio.duration : 0;
    const current = audio.currentTime || 0;
    const progress = duration > 0 ? Math.max(0, Math.min(100, (current / duration) * 100)) : 0;
    wave.style.setProperty("--progress", `${progress}%`);
    seek.value = String(duration > 0 ? Math.round((current / duration) * 1000) : 0);
    time.dataset.duration = String(duration);
    time.textContent = `${formatDuration(current)} / ${formatDuration(duration)}`;
  }

  audio.addEventListener("loadedmetadata", syncFromPlayback);
  audio.addEventListener("timeupdate", syncFromPlayback);
  audio.addEventListener("ended", stopActiveVoice);
  audio.addEventListener("error", () => {
    stopActiveVoice();
    time.textContent = t().voiceUnavailable;
    button.disabled = true;
    rewind.disabled = true;
    forward.disabled = true;
    seek.disabled = true;
  });

  function seekFromRatio(ratio) {
    const duration = Number.isFinite(audio.duration) ? audio.duration : 0;
    if (duration <= 0) return;
    seekAudio(audio, duration * ratio);
    syncFromPlayback();
  }

  wave.addEventListener("click", (e) => {
    const rect = wave.getBoundingClientRect();
    if (!rect.width) return;
    const ratio = Math.max(0, Math.min(1, (e.clientX - rect.left) / rect.width));
    seekFromRatio(ratio);
  });

  seek.addEventListener("input", () => {
    seekFromRatio(Number(seek.value) / 1000);
  });

  rewind.addEventListener("click", () => {
    seekAudio(audio, (audio.currentTime || 0) - 10);
    syncFromPlayback();
  });

  forward.addEventListener("click", () => {
    seekAudio(audio, (audio.currentTime || 0) + 10);
    syncFromPlayback();
  });

  button.addEventListener("click", async () => {
    if (state.activeAudio === audio && !audio.paused) {
      stopActiveVoice();
      return;
    }
    stopActiveVoice();
    try {
      await audio.play();
      bubble.classList.add("playing");
      state.activeAudio = audio;
      state.activeAudioButton = button;
      state.activeAudioBubble = bubble;
      state.activeAudioWave = wave;
      state.activeAudioSeek = seek;
      state.activeAudioTime = time;
      setVoiceButtonState(button, true);
      syncFromPlayback();
    } catch {
      time.textContent = t().voiceUnavailable;
    }
  });

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
  const extraction = trace.extraction || null;
  if (extraction) updateSessionExtraction(extraction);

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
  if (extraction) {
    body.appendChild(renderExtractionCard(extraction));
  }
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

  if (extraction) {
    events.appendChild(
      evt(t().eventExtraction, "llm", t().eventExtractionLabel, {
        detail: extractionDetail(extraction),
      }),
    );
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

  const frustration = typeof extraction?.frustration === "number" ? extraction.frustration : null;
  if (frustration !== null) {
    const pct = Math.round(frustration * 100);
    const color = frustration < 0.4 ? "var(--green, #4ade80)" : frustration < 0.7 ? "var(--yellow, #facc15)" : "var(--red, #f87171)";
    el.statFrustration.innerHTML = `<span style="color:${color};font-weight:600">${pct}%</span>`;
  }

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
      body: JSON.stringify({
        session_id: state.sessionId,
        message: text,
        lang: state.lang,
        response_mode: state.responseMode,
      }),
    });
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    const data = await res.json();

    typing.remove();
    renderAgentTurn(data, text);
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
  stopActiveVoice();
  deleteRecording();
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
  stopActiveVoice();
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
  state.latestExtraction = null;
  el.statCalls.textContent = "0";
  el.statTokens.textContent = "0 / 0";
  el.statTools.textContent = "0";
  el.statFrustration.textContent = "—";
  updateSessionExtraction(null);
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
  el.recordBtn.title = copy.recordAudio;
  el.recordBtn.setAttribute("aria-label", copy.recordAudio);
  el.replyMode.setAttribute("aria-label", copy.responseModeLabel);
  el.replyModeLabel.textContent = copy.responseModeLabel;
  for (const button of el.replyModeButtons) {
    button.textContent = button.dataset.mode === "voice" ? copy.responseModeVoice : copy.responseModeText;
    const active = button.dataset.mode === state.responseMode;
    button.classList.toggle("active", active);
    button.setAttribute("aria-pressed", active ? "true" : "false");
  }
  el.hint.textContent = copy.hint;
  el.sendLabel.textContent = copy.send;
  el.send.title = `${copy.send} (Enter)`;
  el.send.setAttribute("aria-label", copy.send);
  el.traceTitle.textContent = copy.traceTitle;
  el.traceSub.textContent = copy.traceSub;
  el.sessionExtractionTitle.textContent = copy.sessionExtractionTitle;
  el.sessionExtractionSub.textContent = copy.sessionExtractionSub;
  el.traceClear.title = copy.clearTraceTitle;
  el.traceClear.setAttribute("aria-label", copy.clearTraceTitle);
  el.statCallsWrap.firstChild.textContent = `${copy.statCalls} `;
  el.statTokensWrap.firstChild.textContent = `${copy.statTokens} `;
  el.statToolsWrap.firstChild.textContent = `${copy.statTools} `;
  el.statFrustrationWrap.firstChild.textContent = `${copy.statFrustration} `;
  el.langTrigger.title = copy.langMenuTitle;
  el.langTriggerLabel.textContent = copy.langLabel;
  for (const option of el.langOptions) {
    const active = option.dataset.lang === state.lang;
    option.classList.toggle("active", active);
    option.setAttribute("aria-checked", active ? "true" : "false");
  }
  applyRecorderUI();
  updateSessionExtraction(state.latestExtraction);
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

function setResponseMode(mode) {
  if (mode !== "text" && mode !== "voice") return;
  state.responseMode = mode;
  for (const button of el.replyModeButtons) {
    const active = button.dataset.mode === mode;
    button.classList.toggle("active", active);
    button.setAttribute("aria-pressed", active ? "true" : "false");
  }
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
el.recordBtn.addEventListener("click", () => {
  startRecording();
});
el.recorderToggle.addEventListener("click", () => {
  toggleRecorder();
});
el.recorderDelete.addEventListener("click", () => {
  deleteRecording();
});
el.recorderSend.addEventListener("click", () => {
  sendRecordedAudio();
});
el.langTrigger.addEventListener("click", (e) => {
  e.stopPropagation();
  toggleLangMenu();
});
for (const button of el.replyModeButtons) {
  button.addEventListener("click", () => {
    setResponseMode(button.dataset.mode);
  });
}
for (const option of el.langOptions) {
  option.addEventListener("click", (e) => {
    e.stopPropagation();
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
setResponseMode(state.responseMode);
applyRecorderUI();
checkHealth();
el.input.focus();
