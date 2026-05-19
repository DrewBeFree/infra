# Status Dashboard Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a cross-project status dashboard served from atlas (PowerEdge) via Tailscale, showing last session log and all repo backlogs in 3 visual style variants.

**Architecture:** Three self-contained HTML files (one per style variant) share two external JS files — `data.js` for GitHub API fetching/parsing and `render.js` for DOM construction. A git-ignored `config.js` holds the GitHub PAT. Nginx on atlas serves the files at `http://atlas`.

**Tech Stack:** Pure HTML/CSS/JS, GitHub REST API v3, Nginx on Ubuntu 24.04, Tailscale

---

## File Map

| File | Responsibility |
|------|---------------|
| `apps/status-dashboard/config.js` | GitHub PAT + owner config (git-ignored) |
| `apps/status-dashboard/config.example.js` | Setup template (committed) |
| `apps/status-dashboard/data.js` | GitHub API fetch + markdown parse functions |
| `apps/status-dashboard/render.js` | DOM render functions + `init()` entry point |
| `apps/status-dashboard/index-a.html` | Variant A: Clean Light — loads data.js + render.js |
| `apps/status-dashboard/index-b.html` | Variant B: Dark Minimal — loads data.js + render.js |
| `apps/status-dashboard/index-c.html` | Variant C: Warm Editorial — loads data.js + render.js |
| `apps/status-dashboard/.gitignore` | Ignores config.js |
| `apps/status-dashboard/README.md` | Setup instructions |

---

## Task 1: Repo Setup

**Files:**
- Create: `apps/status-dashboard/.gitignore`
- Create: `apps/status-dashboard/config.example.js`
- Create: `apps/status-dashboard/README.md`
- Create: `apps/status-dashboard/config.js` (local only, not committed)

- [ ] **Step 1: Create the repo directory**

```bash
mkdir -p C:\Users\drewb\Documents\GitHub\apps\status-dashboard
cd C:\Users\drewb\Documents\GitHub\apps\status-dashboard
git init
git checkout -b dev
```

- [ ] **Step 2: Create `.gitignore`**

```
config.js
```

- [ ] **Step 3: Create `config.example.js`**

```js
const CONFIG = {
  token: 'ghp_your_token_here',
  owner: 'DrewBeFree',
  infraRepo: 'infra',
  reposJsonPath: 'repos.json'
};
```

- [ ] **Step 4: Create your local `config.js`**

Go to https://github.com/settings/tokens → Generate new token (classic) → check `repo` scope (read-only for private repos) or `public_repo` if all repos are public. Copy the token.

```js
const CONFIG = {
  token: 'ghp_YOUR_REAL_TOKEN',
  owner: 'DrewBeFree',
  infraRepo: 'infra',
  reposJsonPath: 'repos.json'
};
```

- [ ] **Step 5: Create `README.md`**

```markdown
# Status Dashboard

Cross-project status dashboard served from atlas via Tailscale.

## Setup

1. Copy `config.example.js` to `config.js` and add your GitHub PAT
2. On atlas: clone to `/opt/status-dashboard`, add `config.js`, configure Nginx (see Task 7)
3. Access at `http://atlas` on Tailscale

## Variants

- `index-a.html` — Clean Light
- `index-b.html` — Dark Minimal
- `index-c.html` — Warm Editorial

Default served: `index-a.html`
```

- [ ] **Step 6: Initial commit**

```bash
git add .gitignore config.example.js README.md
git commit -m "init: repo setup with config template"
```

---

## Task 2: Data Layer (`data.js`)

**Files:**
- Create: `apps/status-dashboard/data.js`

- [ ] **Step 1: Create `data.js` with the GitHub API fetch helper**

```js
// data.js

async function ghFetch(path) {
  const url = `https://api.github.com/repos/${CONFIG.owner}/${path}`;
  const res = await fetch(url, {
    headers: {
      Authorization: `token ${CONFIG.token}`,
      Accept: 'application/vnd.github.v3+json'
    }
  });
  if (!res.ok) return null;
  const json = await res.json();
  return atob(json.content.replace(/\n/g, ''));
}
```

- [ ] **Step 2: Add `fetchRepos()` — loads repos.json**

```js
async function fetchRepos() {
  const raw = await ghFetch(`${CONFIG.infraRepo}/contents/${CONFIG.reposJsonPath}`);
  if (!raw) return [];
  const data = JSON.parse(raw);
  return data.repositories || [];
}
```

- [ ] **Step 3: Add `fetchSessionLog()` — parses most recent SESSION_LOG entry**

SESSION_LOG.md format:
```
## 2026-05-18

**What we did:**
- bullet

**Where we stopped:**
- text

**Next up:**
- text
```

```js
async function fetchSessionLog() {
  const raw = await ghFetch(`${CONFIG.infraRepo}/contents/SESSION_LOG.md`);
  if (!raw) return null;

  // Split on ## headings, skip the first element (before first ##)
  const blocks = raw.split(/^## /m).filter(b => b.trim());
  if (!blocks.length) return null;

  const block = blocks[0]; // most recent entry
  const dateMatch = block.match(/^(\d{4}-\d{2}-\d{2}[^\n]*)/);
  const date = dateMatch ? dateMatch[1].trim() : 'Unknown date';

  function extractSection(label) {
    const re = new RegExp(`\\*\\*${label}\\*\\*([\\s\\S]*?)(?=\\*\\*|$)`);
    const m = block.match(re);
    if (!m) return [];
    return m[1].split('\n')
      .map(l => l.replace(/^[-*]\s*/, '').trim())
      .filter(Boolean);
  }

  return {
    date,
    did: extractSection('What we did:'),
    stopped: extractSection('Where we stopped:'),
    next: extractSection('Next up:')
  };
}
```

- [ ] **Step 4: Add `parseBacklog()` — parses BACKLOG.md text into grouped tasks**

BACKLOG.md format:
```
## In Progress
- [ ] task text
- [x] done task

## Completed
- [x] done task
```

```js
function parseBacklog(raw, repoName) {
  const sections = {};
  const blocks = raw.split(/^## /m).filter(b => b.trim());

  for (const block of blocks) {
    const lines = block.split('\n');
    const heading = lines[0].trim();
    const tasks = lines.slice(1)
      .filter(l => /^- \[[ x]\]/.test(l.trim()))
      .map(l => ({
        done: /^- \[x\]/i.test(l.trim()),
        text: l.replace(/^- \[[ x]\]\s*/i, '').trim(),
        repo: repoName
      }));
    if (tasks.length) sections[heading] = tasks;
  }

  return { repo: repoName, sections };
}
```

- [ ] **Step 5: Add `fetchAllBacklogs()` — fetches BACKLOG.md for every repo in parallel**

```js
async function fetchAllBacklogs(repos) {
  const results = await Promise.allSettled(
    repos.map(async repo => {
      const raw = await ghFetch(`${repo.name}/contents/BACKLOG.md`);
      if (!raw) return null;
      return parseBacklog(raw, repo.name);
    })
  );

  return results
    .filter(r => r.status === 'fulfilled' && r.value !== null)
    .map(r => r.value);
}
```

- [ ] **Step 6: Add `getUpNext()` — flat list of first incomplete task per repo**

```js
function getUpNext(backlogs) {
  const upNext = [];
  const priority = ['In Progress', 'Blocked', 'Ready', 'Blocked / Ready'];

  for (const backlog of backlogs) {
    let found = false;
    for (const heading of priority) {
      if (found) break;
      const tasks = backlog.sections[heading] || [];
      const incomplete = tasks.filter(t => !t.done);
      if (incomplete.length) {
        upNext.push(incomplete[0]);
        found = true;
      }
    }
    // Fallback: any incomplete task in any section
    if (!found) {
      for (const tasks of Object.values(backlog.sections)) {
        const incomplete = tasks.filter(t => !t.done);
        if (incomplete.length) {
          upNext.push(incomplete[0]);
          break;
        }
      }
    }
  }

  return upNext;
}
```

- [ ] **Step 7: Verify data.js in browser console**

Open `index-a.html` (Task 4) in browser. Open DevTools console and run:

```js
fetchRepos().then(r => console.log('repos:', r.length, r.map(x=>x.name)));
fetchSessionLog().then(s => console.log('session:', s));
fetchAllBacklogs([{name:'infra'}]).then(b => console.log('backlog:', b));
```

Expected: repos array with 15 entries, session object with `date/did/stopped/next`, backlog array with sections.

- [ ] **Step 8: Commit**

```bash
git add data.js
git commit -m "feat: add GitHub API data layer"
```

---

## Task 3: Render Layer (`render.js`)

**Files:**
- Create: `apps/status-dashboard/render.js`

- [ ] **Step 1: Create `render.js` with `renderHeader()`**

```js
// render.js

function renderHeader(lastFetched) {
  document.getElementById('last-fetched').textContent =
    `Fetched ${lastFetched.toLocaleTimeString()}`;
}
```

- [ ] **Step 2: Add `renderLastSession()`**

```js
function renderLastSession(session) {
  const el = document.getElementById('last-session');
  if (!session) {
    el.innerHTML = '<p class="empty">No session log found.</p>';
    return;
  }

  const listItems = arr => arr.map(t => `<li>${t}</li>`).join('');

  el.innerHTML = `
    <div class="session-date">${session.date}</div>
    <div class="session-section">
      <div class="section-label">What we did</div>
      <ul>${listItems(session.did)}</ul>
    </div>
    <div class="session-section">
      <div class="section-label">Where we stopped</div>
      <ul>${listItems(session.stopped)}</ul>
    </div>
    <div class="session-section">
      <div class="section-label">Next up</div>
      <ul>${listItems(session.next)}</ul>
    </div>
  `;
}
```

- [ ] **Step 3: Add `renderUpNext()`**

```js
function renderUpNext(upNext) {
  const el = document.getElementById('up-next');
  if (!upNext.length) {
    el.innerHTML = '<p class="empty">No pending tasks found.</p>';
    return;
  }

  el.innerHTML = upNext.map(task => `
    <div class="up-next-item">
      <span class="up-next-repo">${task.repo}</span>
      <span class="up-next-text">${task.text}</span>
    </div>
  `).join('');
}
```

- [ ] **Step 4: Add `renderBacklogAccordion()`**

```js
function renderBacklogAccordion(backlogs) {
  const el = document.getElementById('backlog');
  const ORDER = ['In Progress', 'Blocked', 'Blocked / Ready', 'Ready', 'Completed'];

  el.innerHTML = backlogs.map(backlog => {
    const openCount = Object.values(backlog.sections)
      .flat()
      .filter(t => !t.done).length;

    const sectionsHtml = ORDER
      .filter(h => backlog.sections[h])
      .map(h => {
        const tasks = backlog.sections[h];
        return `
          <div class="bl-section">
            <div class="bl-section-label">${h}</div>
            <ul>
              ${tasks.map(t => `
                <li class="${t.done ? 'done' : ''}">${t.text}</li>
              `).join('')}
            </ul>
          </div>
        `;
      }).join('');

    return `
      <details class="bl-repo">
        <summary class="bl-summary">
          <span class="bl-repo-name">${backlog.repo}</span>
          <span class="bl-open-count">${openCount} open</span>
        </summary>
        <div class="bl-body">${sectionsHtml}</div>
      </details>
    `;
  }).join('');
}
```

- [ ] **Step 5: Add `renderError()` and `renderLoading()`**

```js
function renderLoading() {
  ['last-session', 'up-next', 'backlog'].forEach(id => {
    document.getElementById(id).innerHTML = '<p class="loading">Loading…</p>';
  });
}

function renderError(msg) {
  ['last-session', 'up-next', 'backlog'].forEach(id => {
    document.getElementById(id).innerHTML = `<p class="error">${msg}</p>`;
  });
}
```

- [ ] **Step 6: Add `init()` — entry point**

```js
async function init() {
  renderLoading();
  try {
    const repos = await fetchRepos();
    const [session, backlogs] = await Promise.all([
      fetchSessionLog(),
      fetchAllBacklogs(repos)
    ]);
    const upNext = getUpNext(backlogs);

    renderHeader(new Date());
    renderLastSession(session);
    renderUpNext(upNext);
    renderBacklogAccordion(backlogs);
  } catch (err) {
    renderError(`Failed to load data: ${err.message}`);
  }
}

document.addEventListener('DOMContentLoaded', () => {
  init();
  document.getElementById('refresh-btn').addEventListener('click', init);
});
```

- [ ] **Step 7: Commit**

```bash
git add render.js
git commit -m "feat: add DOM render layer"
```

---

## Task 4: Variant A — Clean Light (`index-a.html`)

**Files:**
- Create: `apps/status-dashboard/index-a.html`

- [ ] **Step 1: Create `index-a.html`**

```html
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Project Status</title>
<style>
*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

:root {
  --bg: #f0f4f8;
  --surface: #ffffff;
  --border: #e2e8f0;
  --text: #1a2332;
  --muted: #64748b;
  --accent-blue: #2563eb;
  --accent-green: #16a34a;
  --accent-orange: #ea580c;
  --accent-red: #dc2626;
  --radius: 10px;
}

body {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
  background: var(--bg);
  color: var(--text);
  font-size: 14px;
  line-height: 1.6;
  padding: 32px 24px 80px;
  max-width: 1100px;
  margin: 0 auto;
}

/* Header */
header {
  display: flex;
  align-items: baseline;
  justify-content: space-between;
  flex-wrap: wrap;
  gap: 12px;
  margin-bottom: 32px;
  padding-bottom: 20px;
  border-bottom: 1px solid var(--border);
}
h1 { font-size: 22px; font-weight: 700; }
.header-meta { display: flex; align-items: center; gap: 14px; }
#last-fetched { font-size: 12px; color: var(--muted); }
#refresh-btn {
  font-size: 12px; font-weight: 600;
  background: var(--accent-blue); color: white;
  border: none; border-radius: 6px;
  padding: 6px 14px; cursor: pointer;
  transition: opacity 0.15s;
}
#refresh-btn:hover { opacity: 0.85; }

/* Status panel */
.status-panel {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
  margin-bottom: 32px;
}
@media (max-width: 700px) { .status-panel { grid-template-columns: 1fr; } }

.card {
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  padding: 20px;
}
.card-title {
  font-size: 11px; font-weight: 700;
  text-transform: uppercase; letter-spacing: 0.1em;
  color: var(--muted); margin-bottom: 14px;
}

/* Last Session */
.session-date { font-size: 15px; font-weight: 700; margin-bottom: 12px; color: var(--accent-blue); }
.session-section { margin-bottom: 10px; }
.section-label {
  font-size: 10px; font-weight: 700;
  text-transform: uppercase; letter-spacing: 0.1em;
  color: var(--muted); margin-bottom: 4px;
}
#last-session ul { padding-left: 16px; }
#last-session li { font-size: 13px; color: var(--text); margin-bottom: 2px; }

/* Up Next */
.up-next-item {
  display: flex; gap: 10px; align-items: baseline;
  padding: 8px 0; border-bottom: 1px solid var(--border);
}
.up-next-item:last-child { border-bottom: none; }
.up-next-repo {
  font-size: 10px; font-weight: 700;
  text-transform: uppercase; letter-spacing: 0.08em;
  color: var(--accent-blue); white-space: nowrap; flex-shrink: 0;
  background: #eff6ff; padding: 2px 6px; border-radius: 4px;
}
.up-next-text { font-size: 13px; color: var(--text); }

/* Backlog accordion */
.backlog-title {
  font-size: 11px; font-weight: 700;
  text-transform: uppercase; letter-spacing: 0.1em;
  color: var(--muted); margin-bottom: 12px;
  display: flex; align-items: center; gap: 10px;
}
.backlog-title::after { content: ''; flex: 1; height: 1px; background: var(--border); }

details.bl-repo {
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  margin-bottom: 8px;
  overflow: hidden;
}
summary.bl-summary {
  display: flex; align-items: center; justify-content: space-between;
  padding: 14px 18px; cursor: pointer;
  font-weight: 600; font-size: 14px;
  list-style: none; user-select: none;
}
summary.bl-summary::-webkit-details-marker { display: none; }
summary.bl-summary:hover { background: var(--bg); }
.bl-open-count {
  font-size: 11px; font-weight: 600;
  background: #eff6ff; color: var(--accent-blue);
  padding: 2px 8px; border-radius: 10px;
}
.bl-body { padding: 0 18px 16px; }
.bl-section { margin-bottom: 12px; }
.bl-section-label {
  font-size: 10px; font-weight: 700;
  text-transform: uppercase; letter-spacing: 0.1em;
  color: var(--muted); margin-bottom: 6px; margin-top: 12px;
}
.bl-section ul { padding-left: 16px; }
.bl-section li { font-size: 13px; margin-bottom: 4px; }
.bl-section li.done { color: var(--muted); text-decoration: line-through; }

/* Utility */
.empty, .loading { color: var(--muted); font-size: 13px; font-style: italic; }
.error { color: var(--accent-red); font-size: 13px; }
</style>
</head>
<body>

<header>
  <h1>Project Status</h1>
  <div class="header-meta">
    <span id="last-fetched">Loading…</span>
    <button id="refresh-btn">Refresh</button>
  </div>
</header>

<div class="status-panel">
  <div class="card">
    <div class="card-title">Last Session</div>
    <div id="last-session"></div>
  </div>
  <div class="card">
    <div class="card-title">Up Next</div>
    <div id="up-next"></div>
  </div>
</div>

<div class="backlog-title">Backlogs</div>
<div id="backlog"></div>

<script src="config.js"></script>
<script src="data.js"></script>
<script src="render.js"></script>
</body>
</html>
```

- [ ] **Step 2: Open in browser and verify**

Open `index-a.html` in a browser (double-click or `open index-a.html`). Expected:
- Header shows "Project Status" with a Refresh button
- Loading state appears briefly
- Last Session card populates with date, bullets
- Up Next card shows flat task list with repo labels
- Backlog section shows one `<details>` per repo, collapsed

Check browser console for errors. Common issue: CORS — GitHub API works fine from `file://` with a PAT.

- [ ] **Step 3: Commit**

```bash
git add index-a.html
git commit -m "feat: add variant A (clean light)"
```

---

## Task 5: Variant B — Dark Minimal (`index-b.html`)

**Files:**
- Create: `apps/status-dashboard/index-b.html`

- [ ] **Step 1: Copy `index-a.html` to `index-b.html` and replace only the `:root` and body/header color variables**

Replace the entire `<style>` block's `:root` and color-bearing rules with:

```css
:root {
  --bg: #0d1117;
  --surface: #161b22;
  --border: #30363d;
  --text: #e6edf3;
  --muted: #8b949e;
  --accent-blue: #58a6ff;
  --accent-green: #3fb950;
  --accent-orange: #d29922;
  --accent-red: #f85149;
  --radius: 8px;
}

body {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
  background: var(--bg);
  color: var(--text);
  font-size: 14px;
  line-height: 1.6;
  padding: 32px 24px 80px;
  max-width: 1100px;
  margin: 0 auto;
}
```

Also update these rules to use dark variants:
- `.up-next-repo`: change `background: #eff6ff` → `background: #1f3358`
- `.bl-open-count`: change `background: #eff6ff` → `background: #1f3358`
- `summary.bl-summary:hover`: change `background: var(--bg)` → `background: #0d1117`
- `#refresh-btn`: same blue, looks fine on dark

- [ ] **Step 2: Open in browser and verify**

Open `index-b.html`. Expected: same layout as A but dark background, all text readable, no leftover white elements.

- [ ] **Step 3: Commit**

```bash
git add index-b.html
git commit -m "feat: add variant B (dark minimal)"
```

---

## Task 6: Variant C — Warm Editorial (`index-c.html`)

**Files:**
- Create: `apps/status-dashboard/index-c.html`

- [ ] **Step 1: Copy `index-a.html` to `index-c.html` and replace the `<style>` block**

Replace `:root` and font rules:

```css
:root {
  --bg: #faf7f2;
  --surface: #ffffff;
  --border: #e8e0d4;
  --text: #1a1a1a;
  --muted: #8a7f72;
  --accent-blue: #c4623a;
  --accent-green: #5a7a5a;
  --accent-orange: #c4623a;
  --accent-red: #b83232;
  --radius: 6px;
}

body {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
  background: var(--bg);
  color: var(--text);
  font-size: 14px;
  line-height: 1.7;
  padding: 40px 28px 80px;
  max-width: 1000px;
  margin: 0 auto;
}

h1 {
  font-family: Georgia, 'Times New Roman', serif;
  font-size: 26px;
  font-weight: 700;
  letter-spacing: -0.5px;
}

.session-date {
  font-family: Georgia, 'Times New Roman', serif;
  font-size: 16px;
  font-weight: 700;
  margin-bottom: 12px;
  color: var(--accent-blue);
}
```

Also update:
- `.up-next-repo`: change `background: #eff6ff` → `background: #f5ede4; color: var(--accent-blue)`
- `.bl-open-count`: change `background: #eff6ff` → `background: #f5ede4; color: var(--accent-blue)`

- [ ] **Step 2: Open in browser and verify**

Open `index-c.html`. Expected: cream background, serif headings, terracotta accents, warm editorial feel.

- [ ] **Step 3: Commit**

```bash
git add index-c.html
git commit -m "feat: add variant C (warm editorial)"
```

---

## Task 7: Deploy to Atlas

**Prerequisites:** SSH access to atlas (`ssh drew@atlas` or `ssh drew@100.71.165.80`), Nginx installed on atlas.

- [ ] **Step 1: Push the repo to GitHub**

On your Windows machine or Mac:
```bash
# In apps/status-dashboard/
git remote add origin https://github.com/DrewBeFree/status-dashboard.git
git push -u origin dev
```

Create the repo at https://github.com/new first (private, no template).

- [ ] **Step 2: SSH into atlas and clone the repo**

```bash
ssh drew@atlas
sudo mkdir -p /opt/status-dashboard
sudo chown drew:drew /opt/status-dashboard
git clone https://github.com/DrewBeFree/status-dashboard.git /opt/status-dashboard
```

- [ ] **Step 3: Create `config.js` on atlas**

```bash
cat > /opt/status-dashboard/config.js << 'EOF'
const CONFIG = {
  token: 'ghp_YOUR_REAL_TOKEN',
  owner: 'DrewBeFree',
  infraRepo: 'infra',
  reposJsonPath: 'repos.json'
};
EOF
```

- [ ] **Step 4: Install Nginx if not already installed**

```bash
sudo apt list --installed 2>/dev/null | grep nginx
# If not installed:
sudo apt update && sudo apt install -y nginx
```

- [ ] **Step 5: Create Nginx config**

```bash
sudo tee /etc/nginx/sites-available/status-dashboard << 'EOF'
server {
  listen 80;
  server_name atlas _;
  root /opt/status-dashboard;
  index index-a.html;
  location / { try_files $uri $uri/ =404; }
}
EOF
```

- [ ] **Step 6: Enable the site and reload Nginx**

```bash
sudo ln -s /etc/nginx/sites-available/status-dashboard /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default
sudo nginx -t
sudo systemctl reload nginx
```

Expected output of `nginx -t`: `syntax is ok` and `test is successful`

- [ ] **Step 7: Verify from atlas locally**

```bash
curl -s http://localhost | head -5
```

Expected: first few lines of `index-a.html` HTML.

- [ ] **Step 8: Verify from Mac via Tailscale**

On your Mac browser: open `http://atlas`

Expected: Clean Light dashboard loads, data populates within a few seconds.

- [ ] **Step 9: Test all three variants**

- `http://atlas/index-a.html` — Clean Light
- `http://atlas/index-b.html` — Dark Minimal
- `http://atlas/index-c.html` — Warm Editorial

- [ ] **Step 10: To update the dashboard after future changes**

```bash
ssh drew@atlas
cd /opt/status-dashboard && git pull
```

---

## Future Updates Workflow

After changing any HTML/JS file:
1. Commit and push to GitHub from your dev machine
2. SSH to atlas: `cd /opt/status-dashboard && git pull`
3. No Nginx restart needed — Nginx serves static files directly

`config.js` on atlas is never overwritten by `git pull` because it's in `.gitignore`.
