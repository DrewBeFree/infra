# Cloudflare-Protected Portal Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make the existing Atlas internal ecosystem portal usable as a Cloudflare Access-protected launcher for local apps, projects, docs, dashboards, and services.

**Architecture:** Keep `infra/internal-portal/` as the application and `ecosystem.json` as the registry. Add explicit Cloudflare Access route metadata, teach the portal to prefer HTTPS protected aliases when opened from a protected `*.drewbefree.com` hostname, and document the Cloudflare Tunnel/Access setup with Atlas HTTP origins kept private behind the tunnel.

**Tech Stack:** Static HTML/CSS/ES modules, Node `node:test`, Cloudflare Tunnel, Cloudflare Access, Atlas nginx.

## Global Constraints

- Do not deploy private portal assets to GitHub Pages.
- Do not commit Cloudflare tokens, tunnel credentials, passwords, Basic Auth hashes, or API keys.
- Browser-facing protected links use `https://...drewbefree.com`.
- Atlas-origin services may remain `http://127.0.0.1`, `http://atlas`, or existing local service ports behind Cloudflare Tunnel.
- Tailscale remains the fallback path at `http://atlas/ecosystem/`.
- Preserve existing sensitive registry markings; Cloudflare Access protection does not make sensitive entries public.
- Leave unrelated dirty worktree files untouched.

---

## File Structure

- Modify `ecosystem.json`: add a top-level `protectedAccess` object with the chosen Cloudflare hostnames and their Atlas origin services.
- Modify `internal-portal/index.html`: add internal/protected URL data attributes to priority operation links and make the network pill copy adaptable.
- Modify `internal-portal/app.js`: add hosted-mode detection and protected URL resolution for priority links, registry links, docs, and drawer actions.
- Modify `internal-portal/portal.test.mjs`: add contract coverage for protected route metadata, HTTPS aliases, and adaptive portal code.
- Modify `internal-portal/README.md`: document the protected hosted access path and retained Atlas/Tailscale fallback.
- Create `docs/runbooks/cloudflare-protected-internal-portal.md`: step-by-step Cloudflare dashboard and Atlas setup runbook without secrets.

---

### Task 1: Registry Contract For Protected Local Services

**Files:**
- Modify: `ecosystem.json`
- Modify: `internal-portal/portal.test.mjs`

**Interfaces:**
- Produces: `registry.protectedAccess.routes[]`, where each route has `id`, `label`, `publicUrl`, `origin`, `access`, and `fallbackUrl`.
- Consumes: existing registry loader in `internal-portal/app.js`.

- [ ] **Step 1: Add the failing contract test**

Add this test to `internal-portal/portal.test.mjs` after the existing portal status/control test:

```js
test("protected Access routes cover the local operator surfaces", async () => {
  const registry = await loadRegistry();
  const routes = new Map(registry.protectedAccess.routes.map((route) => [route.id, route]));

  assert.equal(registry.protectedAccess.provider, "cloudflare-access");
  assert.equal(registry.protectedAccess.defaultPolicy, "drew-only");

  const expectedRoutes = [
    ["portal", "https://portal.drewbefree.com/ecosystem/", "http://127.0.0.1/ecosystem/", "http://atlas/ecosystem/"],
    ["wiki", "https://wiki.drewbefree.com/wiki/", "http://127.0.0.1/wiki/", "http://atlas/wiki/"],
    ["lead-desk", "https://leads.drewbefree.com/", "http://127.0.0.1:3027", "http://atlas:3027/"],
    ["grafana", "https://grafana.drewbefree.com/", "http://127.0.0.1:3001", "http://atlas:3001/"],
    ["ai-token-dashboard", "https://tokens.drewbefree.com/", "http://127.0.0.1:7474", "http://atlas:7474/"],
    ["leantime", "https://planning.drewbefree.com/", "http://127.0.0.1:8095", "http://atlas:8095/"],
    ["hermes", "https://hermes.drewbefree.com/", "http://127.0.0.1:9119", "http://100.71.165.80:9119/"]
  ];

  for (const [id, publicUrl, origin, fallbackUrl] of expectedRoutes) {
    const route = routes.get(id);
    assert.ok(route, `missing protected route: ${id}`);
    assert.equal(route.publicUrl, publicUrl);
    assert.equal(route.origin, origin);
    assert.equal(route.fallbackUrl, fallbackUrl);
    assert.equal(route.access, "cloudflare-access");
  }
});
```

- [ ] **Step 2: Run the test and verify it fails**

Run:

```powershell
node --test internal-portal/portal.test.mjs
```

Expected: FAIL with a message that `registry.protectedAccess` is undefined.

- [ ] **Step 3: Add protected route metadata**

Add this top-level object to `ecosystem.json`, immediately after the existing `access` object:

```json
"protectedAccess": {
  "provider": "cloudflare-access",
  "defaultPolicy": "drew-only",
  "notes": "Browser-facing routes are HTTPS Cloudflare Access hostnames. Origins stay private on Atlas behind cloudflared.",
  "routes": [
    {
      "id": "portal",
      "label": "Internal Ecosystem",
      "publicUrl": "https://portal.drewbefree.com/ecosystem/",
      "origin": "http://127.0.0.1/ecosystem/",
      "fallbackUrl": "http://atlas/ecosystem/",
      "access": "cloudflare-access"
    },
    {
      "id": "wiki",
      "label": "Atlas Wiki",
      "publicUrl": "https://wiki.drewbefree.com/wiki/",
      "origin": "http://127.0.0.1/wiki/",
      "fallbackUrl": "http://atlas/wiki/",
      "access": "cloudflare-access"
    },
    {
      "id": "lead-desk",
      "label": "Lead Desk",
      "publicUrl": "https://leads.drewbefree.com/",
      "origin": "http://127.0.0.1:3027",
      "fallbackUrl": "http://atlas:3027/",
      "access": "cloudflare-access"
    },
    {
      "id": "grafana",
      "label": "Grafana",
      "publicUrl": "https://grafana.drewbefree.com/",
      "origin": "http://127.0.0.1:3001",
      "fallbackUrl": "http://atlas:3001/",
      "access": "cloudflare-access"
    },
    {
      "id": "ai-token-dashboard",
      "label": "AI Token Dashboard",
      "publicUrl": "https://tokens.drewbefree.com/",
      "origin": "http://127.0.0.1:7474",
      "fallbackUrl": "http://atlas:7474/",
      "access": "cloudflare-access"
    },
    {
      "id": "leantime",
      "label": "Leantime",
      "publicUrl": "https://planning.drewbefree.com/",
      "origin": "http://127.0.0.1:8095",
      "fallbackUrl": "http://atlas:8095/",
      "access": "cloudflare-access"
    },
    {
      "id": "hermes",
      "label": "Hermes",
      "publicUrl": "https://hermes.drewbefree.com/",
      "origin": "http://127.0.0.1:9119",
      "fallbackUrl": "http://100.71.165.80:9119/",
      "access": "cloudflare-access"
    }
  ]
},
```

- [ ] **Step 4: Run the test and verify it passes**

Run:

```powershell
node --test internal-portal/portal.test.mjs
```

Expected: PASS.

- [ ] **Step 5: Commit**

```powershell
git add -- ecosystem.json internal-portal/portal.test.mjs
git commit -m "feat: register protected portal routes"
```

---

### Task 2: Adaptive HTTPS Links In The Portal

**Files:**
- Modify: `internal-portal/index.html`
- Modify: `internal-portal/app.js`
- Modify: `internal-portal/portal.test.mjs`

**Interfaces:**
- Consumes: `registry.protectedAccess.routes[]` from Task 1.
- Produces: `protectedUrlFor(url)` and `isProtectedHostedMode()` in `internal-portal/app.js`.

- [ ] **Step 1: Add failing tests for adaptive link behavior**

Add these assertions inside the existing `portal static files are present and load the canonical registry` test in `internal-portal/portal.test.mjs`:

```js
  assert.match(index, /data-protected-route="lead-desk"/);
  assert.match(index, /data-protected-route="grafana"/);
  assert.match(index, /data-protected-route="ai-token-dashboard"/);
  assert.match(index, /data-protected-route="leantime"/);
  assert.match(index, /data-protected-route="hermes"/);
  assert.match(index, /networkStatusLabel/);
  assert.match(app, /function isProtectedHostedMode/);
  assert.match(app, /function protectedRoutes/);
  assert.match(app, /function protectedUrlFor/);
  assert.match(app, /upgradeProtectedLinks/);
  assert.match(app, /Cloudflare Access protected/);
```

- [ ] **Step 2: Run the test and verify it fails**

Run:

```powershell
node --test internal-portal/portal.test.mjs
```

Expected: FAIL because `data-protected-route` and protected-link functions do not exist yet.

- [ ] **Step 3: Add protected route attributes to priority links**

In `internal-portal/index.html`, replace the network pill and priority links with this shape:

```html
    <div id="networkStatusLabel" class="network-pill"><span></span> Atlas/Tailscale only</div>
```

```html
      <a href="http://atlas:3027/" data-protected-route="lead-desk" target="_blank" rel="noreferrer">
        <span>Lead Desk</span>
        <strong>Morning leads</strong>
      </a>
      <a href="http://atlas:3001/d/atlas-overview/poweredge-dashboard" data-protected-route="grafana" target="_blank" rel="noreferrer">
        <span>AI Dashboard</span>
        <strong>Atlas metrics</strong>
      </a>
      <a href="http://atlas:7474" data-protected-route="ai-token-dashboard" target="_blank" rel="noreferrer">
        <span>AI Token Dashboard</span>
        <strong>Usage + costs</strong>
      </a>
      <a href="http://atlas:8095" data-protected-route="leantime" target="_blank" rel="noreferrer">
        <span>Leantime</span>
        <strong>Projects</strong>
      </a>
      <a href="http://100.71.165.80:9119" data-protected-route="hermes" target="_blank" rel="noreferrer">
        <span>Hermes</span>
        <strong>Dashboard</strong>
      </a>
```

Also change the lead desk stat card link to:

```html
      <a class="ops-link-card" id="leadDeskCard" href="http://atlas:3027/" data-protected-route="lead-desk" target="_blank" rel="noreferrer" title="3 likely leads / 9 total in Lead Desk">
```

- [ ] **Step 4: Implement hosted-mode URL resolution**

In `internal-portal/app.js`, after `isLocalPreview()`, add:

```js
function isProtectedHostedMode() {
  return window.location.protocol === "https:" && /(^|\.)drewbefree\.com$/i.test(window.location.hostname);
}

function protectedRoutes() {
  return state.registry?.protectedAccess?.routes || [];
}

function protectedRouteById(id) {
  return protectedRoutes().find((route) => route.id === id);
}

function appendPath(baseUrl, sourceUrl) {
  try {
    const base = new URL(baseUrl);
    const source = new URL(sourceUrl);
    const basePath = base.pathname.endsWith("/") ? base.pathname.slice(0, -1) : base.pathname;
    const sourcePath = source.pathname === "/" ? "" : source.pathname;
    base.pathname = `${basePath}${sourcePath}` || "/";
    base.search = source.search;
    base.hash = source.hash;
    return base.toString();
  } catch {
    return baseUrl;
  }
}

function protectedUrlFor(url) {
  if (!isProtectedHostedMode() || !isWebUrl(url)) {
    return url;
  }

  const lower = String(url).toLowerCase();
  const route = protectedRoutes().find((candidate) => {
    const fallback = String(candidate.fallbackUrl || "").toLowerCase();
    const origin = String(candidate.origin || "").toLowerCase();
    return lower === fallback || lower.startsWith(fallback) || lower === origin || lower.startsWith(origin);
  });

  if (!route) {
    return url;
  }

  return appendPath(route.publicUrl, url);
}
```

Then update `resolvedUrl(url)` so the final return goes through `protectedUrlFor`:

```js
function resolvedUrl(url) {
  if (!url) {
    return "#";
  }

  if (url.startsWith("http://atlas/")) {
    return protectedUrlFor(atlasWikiToLocal(url));
  }

  return protectedUrlFor(url);
}
```

Add this function before `bindControls()`:

```js
function upgradeProtectedLinks() {
  document.querySelectorAll("[data-protected-route]").forEach((link) => {
    const route = protectedRouteById(link.dataset.protectedRoute);
    if (!route) {
      return;
    }

    link.dataset.internalHref = link.getAttribute("href") || route.fallbackUrl;
    link.dataset.protectedHref = route.publicUrl;
    link.href = isProtectedHostedMode() ? route.publicUrl : route.fallbackUrl;
  });

  const networkLabel = $("#networkStatusLabel");
  if (networkLabel) {
    networkLabel.innerHTML = isProtectedHostedMode()
      ? "<span></span> Cloudflare Access protected"
      : "<span></span> Atlas/Tailscale only";
  }
}
```

Call it in `init()` immediately after registry data loads:

```js
    state.registry = registry;
    state.syncLinks = syncLinks;
    upgradeProtectedLinks();
```

- [ ] **Step 5: Run the tests and syntax check**

Run:

```powershell
node --test internal-portal/portal.test.mjs
node --check internal-portal/app.js
```

Expected: both commands pass.

- [ ] **Step 6: Commit**

```powershell
git add -- internal-portal/index.html internal-portal/app.js internal-portal/portal.test.mjs
git commit -m "feat: prefer protected portal links"
```

---

### Task 3: Cloudflare Access Runbook

**Files:**
- Create: `docs/runbooks/cloudflare-protected-internal-portal.md`
- Modify: `internal-portal/README.md`
- Modify: `internal-portal/portal.test.mjs`

**Interfaces:**
- Consumes: `registry.protectedAccess.routes[]`.
- Produces: human-run Cloudflare setup instructions and validation checklist.

- [ ] **Step 1: Add failing docs coverage**

Add this test to `internal-portal/portal.test.mjs` near the deploy/readme tests:

```js
test("Cloudflare Access runbook documents protected hosted portal setup", async () => {
  const readme = await readFile(new URL("./README.md", import.meta.url), "utf8");
  const runbook = await readFile(new URL("../docs/runbooks/cloudflare-protected-internal-portal.md", import.meta.url), "utf8");

  assert.match(readme, /Cloudflare Access/);
  assert.match(readme, /https:\/\/portal\.drewbefree\.com\/ecosystem\//);
  assert.match(runbook, /cloudflared/);
  assert.match(runbook, /Access policy/);
  assert.match(runbook, /leads\.drewbefree\.com/);
  assert.match(runbook, /wiki\.drewbefree\.com/);
  assert.match(runbook, /No secrets belong in this repo/);
});
```

- [ ] **Step 2: Run the test and verify it fails**

Run:

```powershell
node --test internal-portal/portal.test.mjs
```

Expected: FAIL because the runbook file does not exist.

- [ ] **Step 3: Create the runbook**

Create `docs/runbooks/cloudflare-protected-internal-portal.md`:

```markdown
# Cloudflare-Protected Internal Portal Runbook

## Goal

Expose the Atlas internal ecosystem portal and high-use local operator surfaces through HTTPS Cloudflare Access hostnames without opening inbound firewall ports.

## Protected Routes

| Public URL | Atlas origin | Fallback |
| --- | --- | --- |
| `https://portal.drewbefree.com/ecosystem/` | `http://127.0.0.1/ecosystem/` | `http://atlas/ecosystem/` |
| `https://wiki.drewbefree.com/wiki/` | `http://127.0.0.1/wiki/` | `http://atlas/wiki/` |
| `https://leads.drewbefree.com/` | `http://127.0.0.1:3027` | `http://atlas:3027/` |
| `https://grafana.drewbefree.com/` | `http://127.0.0.1:3001` | `http://atlas:3001/` |
| `https://tokens.drewbefree.com/` | `http://127.0.0.1:7474` | `http://atlas:7474/` |
| `https://planning.drewbefree.com/` | `http://127.0.0.1:8095` | `http://atlas:8095/` |
| `https://hermes.drewbefree.com/` | `http://127.0.0.1:9119` | `http://100.71.165.80:9119/` |

## Cloudflare Setup

1. In Cloudflare Zero Trust, create or choose the DrewBeFree account/team.
2. Create a Cloudflare Tunnel for Atlas.
3. Install `cloudflared` on Atlas using the token from the Cloudflare dashboard.
4. Add one published application route for each protected route in the table.
5. Create a Cloudflare Access self-hosted application for the protected hostnames.
6. Add an Access policy named `drew-only` that allows only Drew's approved email identity.
7. Confirm unauthenticated private/incognito access shows the Cloudflare Access login.
8. Confirm authenticated Drew access reaches each app.

## Atlas Notes

The tunnel service URLs use Atlas local origins. The browser-facing URLs are HTTPS, but the origin URLs can remain HTTP because `cloudflared` connects from Atlas to local services.

No secrets belong in this repo. Do not commit tunnel tokens, credentials JSON files, Access service tokens, passwords, Basic Auth hashes, or API keys.

## Validation

Run locally before deployment:

```bash
node --test internal-portal/portal.test.mjs
node --check internal-portal/app.js
node --check internal-portal/dev-server.mjs
git diff --check
```

After Cloudflare setup:

- `https://portal.drewbefree.com/ecosystem/` requires Cloudflare Access before showing the portal.
- `https://wiki.drewbefree.com/wiki/` requires Cloudflare Access before showing the wiki.
- `https://leads.drewbefree.com/` requires Cloudflare Access before showing Lead Desk.
- `http://atlas/ecosystem/` still works from Tailscale.
```

- [ ] **Step 4: Update README**

Append this section to `internal-portal/README.md`:

```markdown
## Cloudflare Access hosted route

The portal can also be reached through Cloudflare Access at:

- `https://portal.drewbefree.com/ecosystem/`

When opened from a protected `*.drewbefree.com` hostname, priority links prefer HTTPS Cloudflare Access aliases for Lead Desk, the Atlas wiki, Grafana, AI Token Dashboard, Leantime, and Hermes. Atlas/Tailscale HTTP links remain the fallback and source-of-truth origins.

Setup and validation steps live in `../docs/runbooks/cloudflare-protected-internal-portal.md`.
```

- [ ] **Step 5: Run docs test**

Run:

```powershell
node --test internal-portal/portal.test.mjs
```

Expected: PASS.

- [ ] **Step 6: Commit**

```powershell
git add -- docs/runbooks/cloudflare-protected-internal-portal.md internal-portal/README.md internal-portal/portal.test.mjs
git commit -m "docs: add Cloudflare portal runbook"
```

---

### Task 4: Final Verification

**Files:**
- Verify: `ecosystem.json`
- Verify: `internal-portal/index.html`
- Verify: `internal-portal/app.js`
- Verify: `internal-portal/dev-server.mjs`
- Verify: `docs/runbooks/cloudflare-protected-internal-portal.md`

**Interfaces:**
- Consumes: all previous task outputs.
- Produces: a verified branch ready for Cloudflare setup.

- [ ] **Step 1: Run full local checks**

Run:

```powershell
node --test internal-portal/portal.test.mjs
node --check internal-portal/app.js
node --check internal-portal/dev-server.mjs
python -m json.tool ecosystem.json > $null
git diff --check
```

Expected: all commands pass with exit code `0`.

- [ ] **Step 2: Confirm no secrets are staged**

Run:

```powershell
git diff --cached --name-only
git diff --cached -- . ":(exclude)SESSION_LOG.md"
```

Expected: staged changes contain only registry/docs/portal source changes; no Cloudflare token, credential JSON, password, or API key appears.

- [ ] **Step 3: Commit session log if this branch is ready to pause**

Update `SESSION_LOG.md` and `C:\Users\drewb\.Codex\projects\infra\memory\session_log.md` with the same entry. Then run:

```powershell
git add -- SESSION_LOG.md docs/superpowers/plans/2026-06-18-cloudflare-protected-portal.md
git commit -m "docs: plan Cloudflare-protected portal"
```

Expected: plan and log are committed without staging unrelated dirty files.

## Self-Review

- Spec coverage: The plan covers protected hostnames, local app links, HTTPS browser-facing URLs, Atlas HTTP origins, docs, tests, and no-secret constraints.
- Placeholder scan: No `TBD`, `TODO`, `implement later`, or undefined edge-case instructions are present.
- Type consistency: `protectedAccess.routes[]`, `isProtectedHostedMode()`, `protectedRoutes()`, `protectedUrlFor()`, and `upgradeProtectedLinks()` are named consistently across tasks.
