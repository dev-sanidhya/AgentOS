import http, { IncomingMessage, ServerResponse } from "http";
import { exec } from "child_process";
import path from "path";
import {
  AgentResult,
  configure,
  getBuiltInAgentById,
  getBuiltInAgents,
  listRunRecords,
  listSavedAgentDefinitions,
  loadAgent,
} from "@axiomcm/agents";

export interface DashboardOptions {
  projectDir?: string;
  port?: number;
  open?: boolean;
}

export interface DashboardServerHandle {
  port: number;
  projectDir: string;
  url: string;
  close(): Promise<void>;
}

function readRequestBody(req: IncomingMessage): Promise<string> {
  return new Promise((resolve, reject) => {
    const chunks: Buffer[] = [];
    req.on("data", (chunk) => chunks.push(Buffer.from(chunk)));
    req.on("end", () => resolve(Buffer.concat(chunks).toString("utf8")));
    req.on("error", reject);
  });
}

function json(res: ServerResponse, payload: unknown, statusCode = 200): void {
  res.writeHead(statusCode, { "Content-Type": "application/json; charset=utf-8" });
  res.end(JSON.stringify(payload));
}

function html(res: ServerResponse, markup: string): void {
  res.writeHead(200, { "Content-Type": "text/html; charset=utf-8" });
  res.end(markup);
}

function openBrowser(url: string): void {
  const command =
    process.platform === "win32"
      ? `start "" "${url}"`
      : process.platform === "darwin"
        ? `open "${url}"`
        : `xdg-open "${url}"`;

  exec(command);
}

function dashboardPage(projectName: string): string {
  return `<!doctype html>
<html lang="en">
  <head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <title>axiom — ${projectName}</title>
    <link rel="preconnect" href="https://fonts.googleapis.com" />
    <link href="https://fonts.googleapis.com/css2?family=Inter:opsz,wght@14..32,400;14..32,500;14..32,600;14..32,700&display=swap" rel="stylesheet" />
    <style>
      :root {
        --bg-from: #f7f0e3;
        --bg-to: #ece3cf;
        --panel: rgba(255, 251, 244, 0.88);
        --panel-border: rgba(255, 255, 255, 0.72);
        --ink: #1a1f2e;
        --ink-2: #374151;
        --muted: #6b7280;
        --accent: #b45309;
        --accent-light: rgba(180, 83, 9, 0.09);
        --accent-ring: rgba(180, 83, 9, 0.18);
        --success: #059669;
        --success-light: rgba(5, 150, 105, 0.09);
        --danger: #dc2626;
        --danger-light: rgba(220, 38, 38, 0.09);
        --line: rgba(26, 31, 46, 0.09);
        --shadow-panel: 0 32px 72px rgba(65, 49, 32, 0.1), 0 2px 8px rgba(0, 0, 0, 0.04);
        --shadow-card: 0 4px 18px rgba(0, 0, 0, 0.07);
        --r: 22px;
        --r-sm: 13px;
        --r-xs: 9px;
      }

      *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

      body {
        font-family: 'Inter', 'Segoe UI', system-ui, sans-serif;
        font-size: 14px;
        line-height: 1.55;
        color: var(--ink);
        background:
          radial-gradient(ellipse at 4% 4%, rgba(180, 83, 9, 0.14) 0%, transparent 42%),
          radial-gradient(ellipse at 96% 96%, rgba(16, 93, 63, 0.13) 0%, transparent 42%),
          radial-gradient(ellipse at 50% 0%, rgba(245, 239, 228, 0.9) 0%, transparent 60%),
          linear-gradient(155deg, var(--bg-from) 0%, var(--bg-to) 100%);
        min-height: 100vh;
        -webkit-font-smoothing: antialiased;
      }

      .shell { max-width: 1460px; margin: 0 auto; padding: 36px 28px 72px; }

      /* ── Header ── */
      .header {
        display: flex;
        align-items: center;
        justify-content: space-between;
        margin-bottom: 30px;
        gap: 16px;
      }
      .wordmark {
        font-size: 26px;
        font-weight: 700;
        letter-spacing: -0.055em;
        color: var(--ink);
        user-select: none;
      }
      .wordmark em { color: var(--accent); font-style: normal; }
      .header-meta { display: flex; align-items: center; gap: 10px; }
      .badge {
        display: inline-flex;
        align-items: center;
        gap: 7px;
        padding: 5px 13px;
        border: 1px solid var(--line);
        border-radius: 999px;
        background: rgba(255, 255, 255, 0.55);
        backdrop-filter: blur(10px);
        font-size: 12px;
        font-weight: 500;
        color: var(--muted);
      }
      .live-dot {
        width: 7px; height: 7px;
        border-radius: 50%;
        background: var(--success);
        box-shadow: 0 0 0 2.5px rgba(5, 150, 105, 0.22);
        flex-shrink: 0;
        animation: pulse 2.4s ease-in-out infinite;
      }
      @keyframes pulse {
        0%, 100% { box-shadow: 0 0 0 2.5px rgba(5, 150, 105, 0.22); }
        50%       { box-shadow: 0 0 0 4px rgba(5, 150, 105, 0.12); }
      }

      /* ── Grid ── */
      .grid { display: grid; grid-template-columns: 1.3fr 1fr; gap: 22px; }

      /* ── Panel ── */
      .panel {
        background: var(--panel);
        border: 1px solid var(--panel-border);
        border-radius: var(--r);
        box-shadow: var(--shadow-panel);
        backdrop-filter: blur(20px);
        -webkit-backdrop-filter: blur(20px);
        overflow: hidden;
      }
      .panel-header {
        padding: 22px 26px 18px;
        border-bottom: 1px solid var(--line);
        display: flex;
        align-items: flex-start;
        justify-content: space-between;
        gap: 12px;
      }
      .panel-header-text h2 {
        font-size: 15px;
        font-weight: 600;
        margin-bottom: 2px;
        letter-spacing: -0.01em;
      }
      .panel-header-text p { color: var(--muted); font-size: 12.5px; }
      .panel-header-text code {
        font-family: ui-monospace, 'Cascadia Code', monospace;
        font-size: 11.5px;
        background: var(--accent-light);
        color: var(--accent);
        padding: 1px 5px;
        border-radius: 4px;
      }
      .panel-count {
        font-size: 22px;
        font-weight: 700;
        color: var(--accent);
        letter-spacing: -0.04em;
        line-height: 1;
        flex-shrink: 0;
      }
      .panel-body { padding: 20px 26px 26px; }

      /* ── Controls ── */
      .controls-row {
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 10px;
        margin-bottom: 14px;
      }
      .field { display: flex; flex-direction: column; gap: 5px; }
      .field-label {
        font-size: 10.5px;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        color: var(--muted);
      }
      select, textarea {
        width: 100%;
        border-radius: var(--r-sm);
        border: 1px solid var(--line);
        padding: 8px 12px;
        font: inherit;
        font-size: 13px;
        background: rgba(255, 255, 255, 0.68);
        color: var(--ink);
        outline: none;
        transition: border-color .15s ease, box-shadow .15s ease;
        -webkit-appearance: none;
      }
      select {
        background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='11' height='7' fill='none'%3E%3Cpath d='M1 1l4.5 4.5L10 1' stroke='%236b7280' stroke-width='1.5' stroke-linecap='round' stroke-linejoin='round'/%3E%3C/svg%3E");
        background-repeat: no-repeat;
        background-position: right 11px center;
        padding-right: 30px;
        cursor: pointer;
      }
      select:focus, textarea:focus {
        border-color: var(--accent);
        box-shadow: 0 0 0 3px var(--accent-ring);
        background: rgba(255, 255, 255, 0.9);
      }
      textarea { min-height: 84px; resize: vertical; line-height: 1.5; }

      .composer-row {
        display: grid;
        grid-template-columns: 1fr auto;
        gap: 10px;
        align-items: end;
        margin-bottom: 18px;
      }

      /* ── Buttons ── */
      .btn {
        border-radius: var(--r-sm);
        border: none;
        padding: 9px 20px;
        font: inherit;
        font-size: 13px;
        font-weight: 600;
        cursor: pointer;
        transition: transform .14s ease, box-shadow .14s ease, opacity .14s ease, background .14s ease;
        white-space: nowrap;
        letter-spacing: -0.01em;
      }
      .btn:hover:not(:disabled) { transform: translateY(-1.5px); box-shadow: 0 5px 16px rgba(0,0,0,0.15); }
      .btn:active:not(:disabled) { transform: translateY(0); box-shadow: 0 1px 4px rgba(0,0,0,0.1); }
      .btn:disabled { opacity: 0.52; cursor: not-allowed; transform: none !important; box-shadow: none !important; }
      .btn-primary { background: var(--ink); color: #fff; }
      .btn-ghost {
        background: rgba(26, 31, 46, 0.07);
        color: var(--ink-2);
        border: 1px solid var(--line);
      }
      .btn-ghost:hover:not(:disabled) { background: rgba(26, 31, 46, 0.11); }
      .btn-selected { background: var(--accent) !important; color: #fff !important; border-color: transparent !important; box-shadow: 0 3px 10px var(--accent-ring) !important; }

      /* ── Loading bar ── */
      .run-loading {
        display: none;
        align-items: center;
        gap: 10px;
        padding: 10px 15px;
        border-radius: var(--r-sm);
        background: var(--accent-light);
        border: 1px solid var(--accent-ring);
        color: var(--accent);
        font-size: 13px;
        font-weight: 500;
        margin-bottom: 14px;
      }
      .run-loading.visible { display: flex; }
      .spinner {
        width: 15px; height: 15px;
        border: 2px solid var(--accent-ring);
        border-top-color: var(--accent);
        border-radius: 50%;
        animation: spin .65s linear infinite;
        flex-shrink: 0;
      }
      @keyframes spin { to { transform: rotate(360deg); } }

      /* ── Lists ── */
      .list { display: grid; gap: 9px; max-height: 490px; overflow-y: auto; padding-right: 3px; }
      .list::-webkit-scrollbar { width: 3px; }
      .list::-webkit-scrollbar-track { background: transparent; }
      .list::-webkit-scrollbar-thumb { background: rgba(26,31,46,0.15); border-radius: 3px; }

      /* ── Cards ── */
      .card {
        border: 1px solid var(--line);
        border-radius: 15px;
        padding: 13px 15px 13px;
        background: rgba(255, 255, 255, 0.55);
        transition: background .15s ease, box-shadow .15s ease, transform .15s ease, border-color .15s ease;
      }
      .card:hover {
        background: rgba(255, 255, 255, 0.88);
        box-shadow: var(--shadow-card);
        transform: translateY(-1px);
        border-color: rgba(255,255,255,0.9);
      }
      .card-title { font-size: 14px; font-weight: 600; margin-bottom: 3px; letter-spacing: -0.01em; }
      .card-sub { font-size: 12px; color: var(--muted); margin-bottom: 9px; }
      .card-desc { font-size: 13px; color: var(--muted); margin-bottom: 10px; line-height: 1.45; }
      .card-actions { display: flex; gap: 7px; margin-top: 11px; }

      /* ── Pills ── */
      .pills { display: flex; flex-wrap: wrap; gap: 5px; margin-bottom: 9px; }
      .pill {
        display: inline-flex;
        align-items: center;
        gap: 4px;
        padding: 2px 9px;
        border-radius: 999px;
        font-size: 11.5px;
        font-weight: 500;
        line-height: 1.5;
      }
      .pill-neutral { background: rgba(26,31,46,0.07); color: var(--ink-2); }
      .pill-accent  { background: var(--accent-light); color: var(--accent); }
      .pill-success { background: var(--success-light); color: var(--success); }
      .pill-danger  { background: var(--danger-light);  color: var(--danger); }
      .pill-muted   { background: rgba(26,31,46,0.05);  color: var(--muted); }

      .dot { width: 5.5px; height: 5.5px; border-radius: 50%; display: inline-block; flex-shrink: 0; }
      .dot-success { background: var(--success); }
      .dot-danger  { background: var(--danger); }

      /* ── Empty ── */
      .empty {
        padding: 36px 20px;
        text-align: center;
        border: 1.5px dashed var(--line);
        border-radius: 15px;
        color: var(--muted);
        background: rgba(255, 255, 255, 0.28);
      }
      .empty-icon { font-size: 28px; margin-bottom: 8px; opacity: .65; }
      .empty p { font-size: 13px; line-height: 1.55; }

      /* ── Run detail ── */
      .detail-panel { margin-top: 18px; padding-top: 18px; border-top: 1px solid var(--line); }
      .detail-title {
        font-size: 10.5px;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        color: var(--muted);
        margin-bottom: 12px;
      }
      .detail-empty {
        padding: 22px;
        text-align: center;
        border: 1.5px dashed var(--line);
        border-radius: var(--r-sm);
        color: var(--muted);
        font-size: 13px;
        background: rgba(255,255,255,0.3);
      }
      .detail-section { margin-bottom: 12px; }
      .detail-section-label {
        font-size: 10.5px;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        color: var(--muted);
        margin-bottom: 5px;
      }
      pre {
        white-space: pre-wrap;
        word-break: break-word;
        padding: 11px 13px;
        border-radius: var(--r-xs);
        background: rgba(26, 31, 46, 0.05);
        border: 1px solid var(--line);
        font-size: 11.5px;
        max-height: 160px;
        overflow-y: auto;
        font-family: ui-monospace, 'Cascadia Code', 'Fira Code', monospace;
        line-height: 1.55;
        color: var(--ink-2);
      }
      pre::-webkit-scrollbar { width: 3px; height: 3px; }
      pre::-webkit-scrollbar-thumb { background: rgba(26,31,46,0.15); border-radius: 3px; }

      /* ── Divider ── */
      .divider { height: 1px; background: var(--line); margin: 14px 0; }

      @media (max-width: 1000px) {
        .grid { grid-template-columns: 1fr; }
        .controls-row, .composer-row { grid-template-columns: 1fr; }
      }
    </style>
  </head>
  <body>
    <div class="shell">
      <header class="header">
        <div class="wordmark">axio<em>m</em></div>
        <div class="header-meta">
          <div class="badge">
            <span class="live-dot"></span>
            ${projectName}
          </div>
        </div>
      </header>

      <div class="grid">
        <!-- Left: Agent Catalog -->
        <section class="panel">
          <div class="panel-header">
            <div class="panel-header-text">
              <h2>Agent Catalog</h2>
              <p>Built-in agents and saved custom agents from <code>.axiom/agents</code></p>
            </div>
            <div class="panel-count" id="agent-count">—</div>
          </div>
          <div class="panel-body">
            <div class="controls-row">
              <div class="field">
                <div class="field-label">Kind</div>
                <select id="agent-kind">
                  <option value="">All</option>
                  <option value="built_in">Built in</option>
                  <option value="custom">Custom</option>
                </select>
              </div>
              <div class="field">
                <div class="field-label">Category</div>
                <select id="agent-category">
                  <option value="">All</option>
                </select>
              </div>
            </div>

            <div class="run-loading" id="run-loading">
              <div class="spinner"></div>
              Running agent — this may take a moment…
            </div>

            <div class="composer-row">
              <div class="field">
                <div class="field-label">Input for selected agent</div>
                <textarea id="run-input" placeholder="Describe what the agent should do…"></textarea>
              </div>
              <button class="btn btn-primary" id="run-agent">Run</button>
            </div>

            <div id="catalog" class="list"></div>
          </div>
        </section>

        <!-- Right: Run History -->
        <section class="panel">
          <div class="panel-header">
            <div class="panel-header-text">
              <h2>Run History</h2>
              <p>Persisted runs from <code>.axiom/runs</code></p>
            </div>
            <div class="panel-count" id="run-count">—</div>
          </div>
          <div class="panel-body">
            <div class="controls-row">
              <div class="field">
                <div class="field-label">Status</div>
                <select id="run-status">
                  <option value="">All</option>
                  <option value="success">Success</option>
                  <option value="error">Error</option>
                </select>
              </div>
              <div class="field">
                <div class="field-label">Date Range</div>
                <select id="run-days">
                  <option value="0">All time</option>
                  <option value="1">Last 24 hours</option>
                  <option value="7">Last 7 days</option>
                  <option value="30">Last 30 days</option>
                </select>
              </div>
            </div>

            <div id="runs" class="list"></div>

            <div class="detail-panel">
              <div class="detail-title">Run Detail</div>
              <div id="run-detail" class="detail-empty">Select a run to inspect its output, tool calls, and metadata.</div>
            </div>
          </div>
        </section>
      </div>
    </div>

    <script>
      const state = { agents: [], runs: [], selectedAgent: null };

      const els = {
        catalog:       document.getElementById("catalog"),
        runs:          document.getElementById("runs"),
        runDetail:     document.getElementById("run-detail"),
        agentKind:     document.getElementById("agent-kind"),
        agentCategory: document.getElementById("agent-category"),
        runStatus:     document.getElementById("run-status"),
        runDays:       document.getElementById("run-days"),
        runInput:      document.getElementById("run-input"),
        runAgent:      document.getElementById("run-agent"),
        runLoading:    document.getElementById("run-loading"),
        agentCount:    document.getElementById("agent-count"),
        runCount:      document.getElementById("run-count"),
      };

      async function fetchJson(url, options) {
        const res = await fetch(url, options);
        if (!res.ok) {
          const data = await res.json().catch(() => ({}));
          throw new Error(data.error || "Request failed");
        }
        return res.json();
      }

      function esc(v) {
        return String(v ?? "")
          .replaceAll("&", "&amp;")
          .replaceAll("<", "&lt;")
          .replaceAll(">", "&gt;");
      }

      function uniqueCategories() {
        return [...new Set(state.agents.map((a) => a.category))].sort();
      }

      function renderCategoryFilter() {
        els.agentCategory.innerHTML =
          '<option value="">All</option>' +
          uniqueCategories().map((c) => \`<option value="\${c}">\${c}</option>\`).join("");
      }

      function filteredAgents() {
        return state.agents.filter((a) => {
          if (els.agentKind.value && a.kind !== els.agentKind.value) return false;
          if (els.agentCategory.value && a.category !== els.agentCategory.value) return false;
          return true;
        });
      }

      function filteredRuns() {
        const days = Number(els.runDays.value);
        const cutoff = days > 0 ? Date.now() - days * 86400000 : 0;
        return state.runs.filter((r) => {
          if (els.runStatus.value === "success" && !r.success) return false;
          if (els.runStatus.value === "error" && r.success) return false;
          if (cutoff && new Date(r.timestamp).getTime() < cutoff) return false;
          return true;
        });
      }

      function renderCatalog() {
        const agents = filteredAgents();
        els.agentCount.textContent = agents.length;
        if (!agents.length) {
          els.catalog.innerHTML = \`<div class="empty"><div class="empty-icon">🤖</div><p>No agents match the current filters.</p></div>\`;
          return;
        }
        els.catalog.innerHTML = agents.map((a) => {
          const sel = state.selectedAgent && (state.selectedAgent.id === a.id || state.selectedAgent.slug === a.slug);
          return \`<article class="card">
            <div class="card-title">\${esc(a.name)}</div>
            <div class="card-desc">\${esc(a.summary)}</div>
            <div class="pills">
              <span class="pill \${a.kind === "built_in" ? "pill-neutral" : "pill-accent"}">\${a.kind === "built_in" ? "Built in" : "Custom"}</span>
              <span class="pill pill-muted">\${esc(a.category)}</span>
              <span class="pill pill-muted">\${a.allowedTools.length} tool\${a.allowedTools.length !== 1 ? "s" : ""}</span>
            </div>
            <div class="pills">\${a.tags.slice(0, 5).map((t) => \`<span class="pill pill-muted">\${esc(t)}</span>\`).join("")}</div>
            <div class="card-actions">
              <button class="btn \${sel ? "btn-selected" : "btn-ghost"}" data-select-agent="\${a.id}">\${sel ? "✓ Selected" : "Select"}</button>
            </div>
          </article>\`;
        }).join("");
      }

      function renderRuns() {
        const runs = filteredRuns();
        els.runCount.textContent = runs.length;
        if (!runs.length) {
          els.runs.innerHTML = \`<div class="empty"><div class="empty-icon">📋</div><p>No runs yet.<br>Select an agent and click <strong>Run</strong> to get started.</p></div>\`;
          return;
        }
        els.runs.innerHTML = runs.map((r) => \`<article class="card">
          <div class="card-title">\${esc(r.agent.name)}</div>
          <div class="card-sub">\${new Date(r.timestamp).toLocaleString()}</div>
          <div class="pills">
            <span class="pill \${r.success ? "pill-success" : "pill-danger"}">
              <span class="dot \${r.success ? "dot-success" : "dot-danger"}"></span>
              \${r.success ? "success" : "error"}
            </span>
            <span class="pill pill-neutral">$\${r.cost.toFixed(4)}</span>
            <span class="pill pill-neutral">\${r.tokensUsed?.total ?? "—"} tok</span>
            <span class="pill pill-neutral">\${(r.duration / 1000).toFixed(1)}s</span>
          </div>
          <div class="card-actions">
            <button class="btn btn-ghost" data-open-run="\${r.id}">Inspect</button>
          </div>
        </article>\`).join("");
      }

      function renderRunDetail(run) {
        if (!run) {
          els.runDetail.className = "detail-empty";
          els.runDetail.textContent = "Select a run to inspect its output, tool calls, and metadata.";
          return;
        }
        els.runDetail.className = "";
        els.runDetail.innerHTML = \`
          <div class="pills" style="margin-bottom:14px;">
            <span class="pill \${run.success ? "pill-success" : "pill-danger"}">
              <span class="dot \${run.success ? "dot-success" : "dot-danger"}"></span>
              \${run.success ? "success" : "error"}
            </span>
            <span class="pill pill-neutral">\${esc(run.authMode)}</span>
            <span class="pill pill-neutral">\${run.loops} loop\${run.loops !== 1 ? "s" : ""}</span>
            <span class="pill pill-neutral">\${run.tokensUsed?.total ?? "—"} tokens</span>
            <span class="pill pill-neutral">$\${run.cost.toFixed(4)}</span>
          </div>
          <div class="detail-section">
            <div class="detail-section-label">Input</div>
            <pre>\${esc(run.input)}</pre>
          </div>
          <div class="detail-section">
            <div class="detail-section-label">Output</div>
            <pre>\${esc(run.output || run.error || "—")}</pre>
          </div>
          \${run.toolCalls?.length ? \`<div class="detail-section">
            <div class="detail-section-label">Tool Calls (\${run.toolCalls.length})</div>
            <pre>\${esc(JSON.stringify(run.toolCalls, null, 2))}</pre>
          </div>\` : ""}
        \`;
      }

      async function refresh() {
        const data = await fetchJson("/api/agents");
        state.agents = [...data.builtIn, ...data.custom];
        renderCategoryFilter();
        renderCatalog();

        const runs = await fetchJson("/api/runs");
        state.runs = runs.items;
        renderRuns();
      }

      async function runSelectedAgent() {
        if (!state.selectedAgent) { alert("Select an agent first."); return; }
        if (!els.runInput.value.trim()) { alert("Provide an input for the agent."); return; }

        els.runAgent.disabled = true;
        els.runLoading.classList.add("visible");
        try {
          const result = await fetchJson("/api/run", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ id: state.selectedAgent.id, kind: state.selectedAgent.kind, input: els.runInput.value }),
          });
          els.runInput.value = "";
          await refresh();
          renderRunDetail(result.result);
        } catch (err) {
          alert(err.message);
        } finally {
          els.runAgent.disabled = false;
          els.runLoading.classList.remove("visible");
        }
      }

      document.addEventListener("click", async (e) => {
        const t = e.target;
        if (!(t instanceof HTMLElement)) return;

        const selectId = t.getAttribute("data-select-agent");
        if (selectId) {
          state.selectedAgent = state.agents.find((a) => a.id === selectId || a.slug === selectId) ?? null;
          renderCatalog();
          return;
        }

        const runId = t.getAttribute("data-open-run");
        if (runId) {
          const data = await fetchJson("/api/runs/" + runId).catch((err) => { alert(err.message); return null; });
          if (data) renderRunDetail(data.item);
        }
      });

      [els.agentKind, els.agentCategory].forEach((el) => el.addEventListener("change", renderCatalog));
      [els.runStatus, els.runDays].forEach((el) => el.addEventListener("change", renderRuns));
      els.runAgent.addEventListener("click", runSelectedAgent);

      refresh().catch((err) => {
        const msg = \`<div class="empty"><p>\${esc(err.message)}</p></div>\`;
        els.catalog.innerHTML = msg;
        els.runs.innerHTML = msg;
      });
    </script>
  </body>
</html>`;
}

async function handleApiRequest(
  req: IncomingMessage,
  res: ServerResponse,
  options: Required<DashboardOptions>
): Promise<boolean> {
  const url = new URL(req.url ?? "/", "http://127.0.0.1");

  if (req.method === "GET" && url.pathname === "/api/agents") {
    const builtIn = getBuiltInAgents();
    const custom = await listSavedAgentDefinitions(path.join(options.projectDir, ".axiom"));
    json(res, { builtIn, custom });
    return true;
  }

  if (req.method === "GET" && url.pathname === "/api/runs") {
    const items = await listRunRecords(path.join(options.projectDir, ".axiom"));
    json(res, { items });
    return true;
  }

  if (req.method === "GET" && url.pathname.startsWith("/api/runs/")) {
    const runId = url.pathname.split("/").pop() ?? "";
    const items = await listRunRecords(path.join(options.projectDir, ".axiom"));
    const item = items.find((run) => run.id === runId);
    if (!item) {
      json(res, { error: "Run not found" }, 404);
      return true;
    }
    json(res, { item });
    return true;
  }

  if (req.method === "POST" && url.pathname === "/api/run") {
    const rawBody = await readRequestBody(req);
    const body = JSON.parse(rawBody) as {
      id: string;
      kind: "built_in" | "custom";
      input: string;
    };

    if (!body.input?.trim()) {
      json(res, { error: "Input is required" }, 400);
      return true;
    }

    let result: AgentResult;
    if (body.kind === "built_in") {
      const agent = getBuiltInAgentById(body.id);
      if (!agent) {
        json(res, { error: "Built-in agent not found" }, 404);
        return true;
      }
      result = await agent.run(body.input);
    } else {
      const customAgent = await loadAgent(body.id, path.join(options.projectDir, ".axiom"));
      if (!customAgent) {
        json(res, { error: "Custom agent not found" }, 404);
        return true;
      }
      result = await customAgent.run(body.input);
    }

    const runs = await listRunRecords(path.join(options.projectDir, ".axiom"));
    json(res, { result: runs[0] ?? result });
    return true;
  }

  return false;
}

export async function startDashboardServer(
  options: DashboardOptions = {}
): Promise<DashboardServerHandle> {
  const projectDir = options.projectDir ?? process.cwd();
  const port = options.port ?? 3210;
  const storageDir = path.join(projectDir, ".axiom");

  configure({
    storageDir,
    projectName: path.basename(projectDir),
    persistRuns: true,
  });

  const server = http.createServer(async (req, res) => {
    try {
      const handled = await handleApiRequest(req, res, {
        projectDir,
        port,
        open: options.open ?? false,
      });

      if (handled) {
        return;
      }

      const url = new URL(req.url ?? "/", "http://127.0.0.1");
      if (req.method === "GET" && (url.pathname === "/" || url.pathname === "/index.html")) {
        html(res, dashboardPage(path.basename(projectDir)));
        return;
      }

      res.writeHead(404, { "Content-Type": "text/plain; charset=utf-8" });
      res.end("Not found");
    } catch (error) {
      json(
        res,
        { error: error instanceof Error ? error.message : String(error) },
        500
      );
    }
  });

  await new Promise<void>((resolve) => server.listen(port, "127.0.0.1", resolve));

  const url = `http://127.0.0.1:${port}`;
  if (options.open) {
    openBrowser(url);
  }

  return {
    port,
    projectDir,
    url,
    async close() {
      await new Promise<void>((resolve, reject) =>
        server.close((error) => (error ? reject(error) : resolve()))
      );
    },
  };
}
