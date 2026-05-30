# LLM Debate Union Atlas + PocketBase Deployment

This page tracks the infrastructure-facing implementation plan for moving LLM Debate Union from an Alienware-local PWA to a private Atlas-hosted app with durable PocketBase storage and a cloud-first LLM gateway.

The app-local execution checklist also lives at `apps/llm-debate-union/docs/superpowers/plans/2026-05-30-atlas-pocketbase-cloud-llm.md`.

---
# Atlas PocketBase Cloud LLM Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Deploy `llm-debate-union` as a private Atlas-hosted app with durable PocketBase app storage, cloud LLM calls routed through a server-side gateway, and a Postgres/pgvector memory-vault path for long-term cross-model chat history.

**Architecture:** Atlas serves the static PWA over Tailscale/Nginx, runs PocketBase for fast app-specific records, runs Postgres with pgvector for the durable personal AI memory vault, and runs a small Node gateway for OpenAI/Anthropic/Gemini/xAI API calls. Alienware remains the optional Ollama/GPU backend for local inference and embedding jobs; Atlas does not need a GPU for the cloud-first version.

**Tech Stack:** Vanilla HTML/CSS/JS PWA, Node 20+ gateway, PocketBase on Atlas, PostgreSQL + pgvector on Atlas, optional DuckDB analytics exports, Nginx reverse proxy, systemd user services, PowerShell for local dev scripts, Bash/systemd on Atlas.

---

## Storage Roles

- **PocketBase** is the app backend for `llm-debate-union`: saved sessions, motions, persona prompts, lightweight telemetry, and fast admin inspection.
- **Postgres + pgvector** is the personal AI memory vault: normalized conversations from ChatGPT, Claude, Gemini, Grok, Codex, Ollama/Open WebUI, and future app-generated sessions.
- **DuckDB** is an optional analytics sidecar for reports over exported/snapshotted data; it is not the live app database.
- **Ingestion workers** copy selected PocketBase sessions and external chat exports into Postgres, then embedding workers attach vectors for semantic search.
---

## File Structure

- `server/package.json` - Node gateway package metadata and scripts.
- `server/.env.example` - documented environment variables for provider keys and PocketBase URL.
- `server/src/config.js` - validates environment and exposes provider configuration.
- `server/src/provider-client.js` - calls OpenAI, Anthropic, Gemini, and xAI with one internal response shape.
- `server/src/pocketbase-client.js` - optional server-side audit writes to PocketBase.
- `server/src/index.js` - HTTP routes: health, providers, chat completion proxy.
- `server/tests/provider-client.test.js` - mocked provider tests.
- `server/tests/api.test.js` - gateway route tests with mocked provider calls.
- `app-config.js` - frontend runtime config for gateway/PocketBase URLs.
- `app.js` - replace direct browser API calls with gateway calls and add PocketBase persistence.
- `index.html` - update API settings UI labels to indicate server-side key storage.
- `DEPLOY_ATLAS.md` - Atlas installation, service, Nginx, PocketBase setup, and update commands.
- `pocketbase/schema.json` - documented collections and fields for repeatable setup.
- `memory-db/schema.sql` - Postgres/pgvector schema for the long-term personal AI memory vault.
- `memory-db/README.md` - setup notes for Postgres, pgvector, backups, and ingestion boundaries.
- `server/src/memory-writer.js` - gateway-side helper for writing completed sessions into the memory vault after PocketBase save succeeds.

---

## Task 1: Set Up PocketBase On Atlas

**Files:**
- Create on Atlas: `/home/drew/services/pocketbase/`
- Create on Atlas: `/home/drew/.config/systemd/user/pocketbase.service`
- Create later in repo: `pocketbase/schema.json`

- [ ] **Step 1: SSH into Atlas**

Run from the dev machine:

```powershell
ssh atlas
```

Expected: shell prompt on Atlas.

- [ ] **Step 2: Create PocketBase service directory**

Run on Atlas:

```bash
mkdir -p /home/drew/services/pocketbase
cd /home/drew/services/pocketbase
```

Expected: current directory is `/home/drew/services/pocketbase`.

- [ ] **Step 3: Download PocketBase**

Run on Atlas, choosing the current Linux amd64 release from PocketBase releases:

```bash
curl -L -o pocketbase.zip https://github.com/pocketbase/pocketbase/releases/download/v0.23.12/pocketbase_0.23.12_linux_amd64.zip
unzip -o pocketbase.zip
chmod +x pocketbase
./pocketbase --version
```

Expected: PocketBase prints a version. If the release URL is stale, open the PocketBase releases page, copy the latest Linux amd64 zip URL, and rerun the same commands with that URL.

- [ ] **Step 4: Create systemd user service**

Run on Atlas:

```bash
mkdir -p /home/drew/.config/systemd/user
cat > /home/drew/.config/systemd/user/pocketbase.service <<'EOF'
[Unit]
Description=PocketBase
After=network.target

[Service]
WorkingDirectory=/home/drew/services/pocketbase
ExecStart=/home/drew/services/pocketbase/pocketbase serve --http=127.0.0.1:8090
Restart=always
RestartSec=5

[Install]
WantedBy=default.target
EOF
systemctl --user daemon-reload
systemctl --user enable --now pocketbase
systemctl --user status pocketbase --no-pager
```

Expected: service is active/running.

- [ ] **Step 5: Verify local PocketBase health on Atlas**

Run on Atlas:

```bash
curl -i http://127.0.0.1:8090/api/health
```

Expected: HTTP 200 with JSON health response.

- [ ] **Step 6: Create admin account**

From a Tailscale-connected browser, temporarily expose or proxy PocketBase through Nginx, or SSH tunnel it:

```powershell
ssh -L 8090:127.0.0.1:8090 atlas
```

Then open `http://127.0.0.1:8090/_/` and create the admin account.

Expected: PocketBase admin dashboard is reachable.

- [ ] **Step 7: Create initial collections manually**

In the PocketBase admin UI, create these collections:

`debate_sessions`
- `title` text, required
- `mode` text, required
- `verdict` text
- `subtext` text
- `transcript` json
- `blueprint` text
- `stats` json

`saved_motions`
- `title` text, required
- `mode` text
- `context` text

`persona_prompts`
- `persona` text, required
- `prompt` text

Expected: collections exist before frontend code is changed.

- [ ] **Step 8: Commit nothing**

No git commit for Atlas setup. Record credentials only in your password manager, never in the repo.

---

## Task 2: Set Up Postgres + pgvector Memory Vault On Atlas

**Files:**
- Create on Atlas: PostgreSQL database `ai_memory`
- Create later in repo: `memory-db/schema.sql`
- Create later in repo: `memory-db/README.md`

- [ ] **Step 1: Check whether Postgres is installed on Atlas**

Run on Atlas:

```bash
psql --version || true
systemctl status postgresql --no-pager || true
```

Expected: either Postgres is already installed/running, or these commands show it is absent. If absent, install PostgreSQL before continuing.

- [ ] **Step 2: Install Postgres and pgvector if missing**

Run on Atlas only if Postgres/pgvector are absent:

```bash
sudo apt update
sudo apt install -y postgresql postgresql-contrib postgresql-16-pgvector
sudo systemctl enable --now postgresql
```

Expected: PostgreSQL service is active. If `postgresql-16-pgvector` is unavailable, install pgvector from the package name available for the Atlas Ubuntu release.

- [ ] **Step 3: Create memory database**

Run on Atlas:

```bash
sudo -u postgres psql -c "CREATE DATABASE ai_memory;"
sudo -u postgres psql -d ai_memory -c "CREATE EXTENSION IF NOT EXISTS vector;"
```

Expected: database exists and vector extension is installed.

- [ ] **Step 4: Create first-pass memory schema**

Run on Atlas:

```bash
sudo -u postgres psql -d ai_memory <<'SQL'
CREATE TABLE IF NOT EXISTS chat_threads (
  id BIGSERIAL PRIMARY KEY,
  source TEXT NOT NULL,
  external_id TEXT,
  title TEXT NOT NULL,
  project TEXT,
  created_at TIMESTAMPTZ,
  imported_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  metadata JSONB NOT NULL DEFAULT '{}'::jsonb
);

CREATE TABLE IF NOT EXISTS chat_messages (
  id BIGSERIAL PRIMARY KEY,
  thread_id BIGINT NOT NULL REFERENCES chat_threads(id) ON DELETE CASCADE,
  role TEXT NOT NULL,
  provider TEXT,
  model TEXT,
  content TEXT NOT NULL,
  message_at TIMESTAMPTZ,
  token_input INTEGER,
  token_output INTEGER,
  metadata JSONB NOT NULL DEFAULT '{}'::jsonb
);

CREATE TABLE IF NOT EXISTS chat_embeddings (
  id BIGSERIAL PRIMARY KEY,
  message_id BIGINT NOT NULL REFERENCES chat_messages(id) ON DELETE CASCADE,
  embedding_model TEXT NOT NULL,
  embedding vector(1536),
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_chat_threads_source ON chat_threads(source);
CREATE INDEX IF NOT EXISTS idx_chat_messages_thread ON chat_messages(thread_id);
CREATE INDEX IF NOT EXISTS idx_chat_messages_provider ON chat_messages(provider);
SQL
```

Expected: tables and indexes are created.

- [ ] **Step 5: Commit nothing**

Atlas database setup is infrastructure state. The repeatable schema file is created in a later task and committed.

---
## Task 3: Create Deployment Branch And Baseline Checks

**Files:**
- Modify only through later tasks.

- [ ] **Step 1: Create branch from main**

Run from `C:\Users\drewb\Documents\GitHub\apps\llm-debate-union`:

```powershell
git checkout main
git pull --ff-only
git checkout -b feat/atlas-pocketbase-cloud-llm
```

Expected: branch `feat/atlas-pocketbase-cloud-llm` exists.

- [ ] **Step 2: Record current status**

```powershell
git status --short --branch
```

Expected: clean except allowed local-only files such as `.claude/`.

- [ ] **Step 3: Verify current app still parses**

```powershell
python -m py_compile start_server.py scripts/build_app.py
```

Expected: no output and exit code 0.

- [ ] **Step 4: Commit nothing**

No commit for this task; it is a setup checkpoint.

---

## Task 4: Add Gateway Test Harness

**Files:**
- Create: `server/package.json`
- Create: `server/src/config.js`
- Create: `server/src/provider-client.js`
- Create: `server/src/index.js`
- Create: `server/tests/provider-client.test.js`
- Create: `server/tests/api.test.js`

- [ ] **Step 1: Create `server/package.json`**

```json
{
  "name": "llm-debate-union-gateway",
  "version": "0.1.0",
  "private": true,
  "type": "module",
  "scripts": {
    "start": "node src/index.js",
    "test": "node --test"
  },
  "dependencies": {},
  "devDependencies": {}
}
```

- [ ] **Step 2: Create minimal config module**

Create `server/src/config.js`:

```js
export function getConfig(env = process.env) {
  return {
    port: Number(env.PORT || 8787),
    allowedOrigin: env.ALLOWED_ORIGIN || "http://localhost:8080",
    providers: {
      openai: { apiKey: env.OPENAI_API_KEY || "", model: env.OPENAI_MODEL || "gpt-4o" },
      anthropic: { apiKey: env.ANTHROPIC_API_KEY || "", model: env.ANTHROPIC_MODEL || "claude-3-5-sonnet-20241022" },
      gemini: { apiKey: env.GEMINI_API_KEY || "", model: env.GEMINI_MODEL || "gemini-1.5-flash" },
      xai: { apiKey: env.XAI_API_KEY || "", model: env.XAI_MODEL || "grok-beta" }
    },
    pocketbaseUrl: env.POCKETBASE_URL || "http://127.0.0.1:8090"
  };
}
```

- [ ] **Step 3: Write failing provider test**

Create `server/tests/provider-client.test.js`:

```js
import test from "node:test";
import assert from "node:assert/strict";
import { normalizeProviderName, estimateTokens } from "../src/provider-client.js";

test("normalizes app persona provider names", () => {
  assert.equal(normalizeProviderName("chatgpt"), "openai");
  assert.equal(normalizeProviderName("claude"), "anthropic");
  assert.equal(normalizeProviderName("gemini"), "gemini");
  assert.equal(normalizeProviderName("grok"), "xai");
});

test("estimates tokens from text length", () => {
  assert.equal(estimateTokens("12345678"), 2);
});
```

- [ ] **Step 4: Run failing test**

```powershell
cd server
npm test
```

Expected: FAIL because `provider-client.js` does not export the functions yet.

- [ ] **Step 5: Implement minimal provider utilities**

Create `server/src/provider-client.js`:

```js
export function normalizeProviderName(modelKey) {
  const map = {
    chatgpt: "openai",
    claude: "anthropic",
    gemini: "gemini",
    grok: "xai"
  };
  return map[modelKey] || modelKey;
}

export function estimateTokens(text) {
  return Math.max(1, Math.round(String(text || "").length / 4));
}

export async function callProvider({ modelKey, systemPrompt, userMessage, config, fetchImpl = fetch }) {
  const provider = normalizeProviderName(modelKey);
  if (!config.providers[provider] || !config.providers[provider].apiKey) {
    throw new Error(`Provider not configured: ${provider}`);
  }

  return callOpenAICompatible({ provider, modelKey, systemPrompt, userMessage, config, fetchImpl });
}

async function callOpenAICompatible({ provider, systemPrompt, userMessage, config, fetchImpl }) {
  const providerConfig = config.providers[provider];
  const endpointByProvider = {
    openai: "https://api.openai.com/v1/chat/completions",
    xai: "https://api.x.ai/v1/chat/completions"
  };

  if (!endpointByProvider[provider]) {
    return {
      text: `${provider} gateway stub: ${userMessage}`,
      inputTokens: estimateTokens(systemPrompt + userMessage),
      outputTokens: estimateTokens(userMessage)
    };
  }

  const response = await fetchImpl(endpointByProvider[provider], {
    method: "POST",
    headers: {
      "Authorization": `Bearer ${providerConfig.apiKey}`,
      "Content-Type": "application/json"
    },
    body: JSON.stringify({
      model: providerConfig.model,
      messages: [
        { role: "system", content: systemPrompt },
        { role: "user", content: userMessage }
      ]
    })
  });

  if (!response.ok) throw new Error(`${provider} API failed: ${response.status}`);
  const data = await response.json();
  const text = data.choices?.[0]?.message?.content || "";
  return {
    text,
    inputTokens: data.usage?.prompt_tokens || estimateTokens(systemPrompt + userMessage),
    outputTokens: data.usage?.completion_tokens || estimateTokens(text)
  };
}
```

- [ ] **Step 6: Add initial gateway route**

Create `server/src/index.js`:

```js
import http from "node:http";
import { getConfig } from "./config.js";
import { callProvider } from "./provider-client.js";

export function createServer({ config = getConfig(), fetchImpl = fetch } = {}) {
  return http.createServer(async (req, res) => {
    res.setHeader("Access-Control-Allow-Origin", config.allowedOrigin);
    res.setHeader("Access-Control-Allow-Headers", "Content-Type");
    res.setHeader("Access-Control-Allow-Methods", "GET,POST,OPTIONS");
    if (req.method === "OPTIONS") return sendJson(res, 204, {});

    if (req.method === "GET" && req.url === "/health") {
      return sendJson(res, 200, { ok: true });
    }

    if (req.method === "POST" && req.url === "/api/complete") {
      const body = await readJson(req);
      const result = await callProvider({ ...body, config, fetchImpl });
      return sendJson(res, 200, result);
    }

    return sendJson(res, 404, { error: "not found" });
  });
}

function sendJson(res, status, data) {
  res.statusCode = status;
  res.setHeader("Content-Type", "application/json");
  res.end(JSON.stringify(data));
}

function readJson(req) {
  return new Promise((resolve, reject) => {
    let raw = "";
    req.on("data", chunk => raw += chunk);
    req.on("end", () => {
      try { resolve(raw ? JSON.parse(raw) : {}); } catch (err) { reject(err); }
    });
  });
}

if (import.meta.url === `file://${process.argv[1]}`) {
  const config = getConfig();
  createServer({ config }).listen(config.port, () => {
    console.log(`llm-debate-union gateway listening on ${config.port}`);
  });
}
```

- [ ] **Step 7: Write route test**

Create `server/tests/api.test.js`:

```js
import test from "node:test";
import assert from "node:assert/strict";
import { createServer } from "../src/index.js";
import { getConfig } from "../src/config.js";

test("health route returns ok", async () => {
  const server = createServer({ config: getConfig({ PORT: "0" }) });
  await new Promise(resolve => server.listen(0, resolve));
  const { port } = server.address();
  const response = await fetch(`http://127.0.0.1:${port}/health`);
  assert.equal(response.status, 200);
  assert.deepEqual(await response.json(), { ok: true });
  server.close();
});
```

- [ ] **Step 8: Run tests**

```powershell
cd server
npm test
```

Expected: PASS.

- [ ] **Step 9: Commit**

```powershell
git add server
git commit -m "feat: add cloud llm gateway skeleton"
```

---

## Task 5: Replace Browser API Calls With Gateway Calls

**Files:**
- Create: `app-config.js`
- Modify: `index.html`
- Modify: `app.js`

- [ ] **Step 1: Create runtime config**

Create `app-config.js`:

```js
window.LDU_CONFIG = {
  gatewayUrl: "http://localhost:8787",
  pocketbaseUrl: "http://localhost:8090"
};
```

- [ ] **Step 2: Load config before app**

In `index.html`, add before `app.js`:

```html
<script src="app-config.js"></script>
<script src="app.js"></script>
```

- [ ] **Step 3: Add gateway caller in `app.js`**

Add near API call implementations:

```js
async function callGateway(modelKey, systemPrompt, userMessage) {
  const gatewayUrl = window.LDU_CONFIG?.gatewayUrl || "http://localhost:8787";
  const response = await fetch(`${gatewayUrl}/api/complete`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ modelKey, systemPrompt, userMessage })
  });
  if (!response.ok) throw new Error(`Gateway failed: ${response.status}`);
  return response.json();
}
```

- [ ] **Step 4: Update `fetchLlmCompletion()` hybrid mode**

Replace direct key lookups in hybrid mode with:

```js
if (mode === 'hybrid') {
  try {
    return await callGateway(modelKey, systemPrompt, userMessage);
  } catch (err) {
    console.warn("Gateway unavailable; falling back to Ollama/simulation", err);
  }

  const host = localStorage.getItem('ollama_host') || 'http://localhost:11434';
  try {
    return await callOllama(host, modelKey, systemPrompt, userMessage);
  } catch (_) {
    const simulatedText = getSimulatedSpeech(speakerId);
    return {
      text: simulatedText,
      inputTokens: Math.round((systemPrompt.length + userMessage.length) / 4),
      outputTokens: Math.round(simulatedText.length / 4)
    };
  }
}
```

- [ ] **Step 5: Update API config copy**

In `index.html`, change any copy saying cloud provider keys are saved in browser localStorage to say:

```html
Cloud provider API keys are configured on the Atlas gateway. This browser only stores display preferences and optional Ollama host settings.
```

- [ ] **Step 6: Run local smoke test**

Terminal 1:

```powershell
cd server
$env:OPENAI_API_KEY="dummy"
npm start
```

Terminal 2:

```powershell
python start_server.py
```

Expected: app loads at `http://localhost:8080`; simulated mode still works.

- [ ] **Step 7: Commit**

```powershell
git add app-config.js index.html app.js
git commit -m "feat: route cloud model calls through gateway"
```

---

## Task 6: Add PocketBase Persistence

**Files:**
- Create: `pocketbase/schema.json`
- Modify: `app.js`
- Modify: `index.html`

- [ ] **Step 1: Create documented schema**

Create `pocketbase/schema.json`:

```json
{
  "collections": {
    "debate_sessions": {
      "fields": {
        "title": "text",
        "mode": "text",
        "verdict": "text",
        "subtext": "text",
        "transcript": "json",
        "blueprint": "text",
        "stats": "json",
        "created": "datetime"
      }
    },
    "saved_motions": {
      "fields": {
        "title": "text",
        "mode": "text",
        "context": "text",
        "created": "datetime"
      }
    },
    "persona_prompts": {
      "fields": {
        "persona": "text",
        "prompt": "text",
        "updated": "datetime"
      }
    }
  }
}
```

- [ ] **Step 2: Add PocketBase helper functions**

Add in `app.js` near history functions:

```js
function getPocketBaseUrl() {
  return window.LDU_CONFIG?.pocketbaseUrl || "http://localhost:8090";
}

async function saveSessionRemote(historyItem) {
  const response = await fetch(`${getPocketBaseUrl()}/api/collections/debate_sessions/records`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(historyItem)
  });
  if (!response.ok) throw new Error(`PocketBase save failed: ${response.status}`);
  return response.json();
}

async function fetchRemoteSessions() {
  const response = await fetch(`${getPocketBaseUrl()}/api/collections/debate_sessions/records?sort=-created&perPage=50`);
  if (!response.ok) throw new Error(`PocketBase fetch failed: ${response.status}`);
  const data = await response.json();
  return data.items || [];
}
```

- [ ] **Step 3: Save both local and remote**

In `saveSessionToHistory()`, after `localStorage.setItem(...)`, add:

```js
saveSessionRemote(historyItem).catch(err => {
  console.warn("Remote session save failed; local history retained", err);
});
```

- [ ] **Step 4: Make history render use remote first**

In `openHistoryModal()`, replace existing body with:

```js
async function openHistoryModal() {
  renderHistory();
  fetchRemoteSessions()
    .then(remoteItems => renderHistory(remoteItems))
    .catch(err => console.warn("Remote history unavailable; using local history", err));
  toggleModal('modalHistory', true);
}
```

Update `renderHistory(savedHistoryOverride)` signature:

```js
function renderHistory(savedHistoryOverride) {
  const container = document.getElementById('historyList');
  if (!container) return;
  let savedHistory = savedHistoryOverride || [];
  if (!savedHistoryOverride) {
    try {
      savedHistory = JSON.parse(localStorage.getItem('debate_history') || '[]');
    } catch (e) {
      console.error("Failed to load history:", e);
    }
  }
```

- [ ] **Step 5: Verify graceful fallback**

Run only the app without PocketBase:

```powershell
python start_server.py
```

Expected: completing a debate still saves locally; console warning says remote save failed.

- [ ] **Step 6: Commit**

```powershell
git add app.js pocketbase/schema.json
git commit -m "feat: add PocketBase session persistence"
```

---

## Task 7: Document Atlas Deployment

**Files:**
- Create: `server/.env.example`
- Create: `DEPLOY_ATLAS.md`

- [ ] **Step 1: Create env example**

Create `server/.env.example`:

```bash
PORT=8787
ALLOWED_ORIGIN=http://atlas
POCKETBASE_URL=http://127.0.0.1:8090
OPENAI_API_KEY=
OPENAI_MODEL=gpt-4o
ANTHROPIC_API_KEY=
ANTHROPIC_MODEL=claude-3-5-sonnet-20241022
GEMINI_API_KEY=
GEMINI_MODEL=gemini-1.5-flash
XAI_API_KEY=
XAI_MODEL=grok-beta
```

- [ ] **Step 2: Create deployment doc**

Create `DEPLOY_ATLAS.md` with:

```markdown
# Atlas Deployment

This app is private and should be served over Tailscale only.

## Layout On Atlas

- App: `/home/drew/services/llm-debate-union/app`
- Gateway: `/home/drew/services/llm-debate-union/server`
- PocketBase: `/home/drew/services/pocketbase`

## PocketBase

Download PocketBase on Atlas, then run it as a systemd user service on port `8090`.
Create these collections in the admin UI using `pocketbase/schema.json` as the field guide:

- `debate_sessions`
- `saved_motions`
- `persona_prompts`

## Gateway

Copy `server/.env.example` to `server/.env` and fill provider keys on Atlas only.
Never commit `.env`.

## Nginx

Proxy:

- `/llm-debate-union/` -> static app files
- `/llm-debate-union/api/` -> gateway `127.0.0.1:8787`
- `/llm-debate-union/pb/` -> PocketBase `127.0.0.1:8090`

## Update Flow

From dev machine:

```bash
git push origin main
ssh atlas "cd /home/drew/services/llm-debate-union/app && git pull && systemctl --user restart llm-debate-union-gateway"
```
```

- [ ] **Step 3: Commit docs**

```powershell
git add DEPLOY_ATLAS.md server/.env.example
git commit -m "docs: add Atlas deployment guide"
```

---

## Task 8: Document Memory Vault Schema And Boundaries

**Files:**
- Create: `memory-db/schema.sql`
- Create: `memory-db/README.md`

- [ ] **Step 1: Create committed schema file**

Create `memory-db/schema.sql` with the same SQL used on Atlas in Task 2.

- [ ] **Step 2: Create memory README**

Create `memory-db/README.md`:

```markdown
# Personal AI Memory Vault

This database stores normalized long-term chat history across model providers and local tools.

## Role

Postgres + pgvector is the canonical long-term store. PocketBase remains the lightweight app backend for LLM Debate Union.

## Sources

- ChatGPT exports
- Claude exports
- Gemini/Grok exports or API logs
- Codex session logs
- Ollama/Open WebUI exports
- LLM Debate Union sessions copied from PocketBase

## Tables

- `chat_threads` - one conversation/session/thread
- `chat_messages` - individual messages or model turns
- `chat_embeddings` - vector embeddings for semantic search

## Boundary

Do not store provider API keys here. Keys live only in the Atlas gateway `.env` or a future secrets manager.
```

- [ ] **Step 3: Commit**

```powershell
git add memory-db/schema.sql memory-db/README.md
git commit -m "docs: add personal AI memory vault schema"
```

---
## Task 9: Final Verification And Merge

**Files:**
- All changed files.

- [ ] **Step 1: Run gateway tests**

```powershell
cd server
npm test
```

Expected: PASS.

- [ ] **Step 2: Run app locally**

```powershell
python start_server.py
```

Expected: app available at `http://localhost:8080`.

- [ ] **Step 3: Manual browser checks**

- Simulated debate still works.
- Hybrid mode attempts gateway first.
- If gateway is off, hybrid falls back without crashing.
- Completed session remains in local history.
- With PocketBase running, completed session appears after local storage is cleared.

- [ ] **Step 4: Merge and push**

```powershell
git checkout main
git merge feat/atlas-pocketbase-cloud-llm
git push origin main
```

Expected: main includes deployment work.

---

## Self-Review

- Scope is intentionally cloud-first and storage-first; no Atlas GPU work is included.
- PocketBase is used only for `llm-debate-union` app state, not as the global personal AI memory store.
- Postgres + pgvector is explicitly added as the cross-model personal chat memory vault.
- DuckDB is reserved for analytics/export workflows, not live app state.
- API keys are moved out of browser storage and into Atlas gateway environment variables.
- The plan preserves simulation and Ollama fallback behavior.





