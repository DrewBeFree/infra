# Status Dashboard — Design Spec
*2026-05-19*

## Overview

A personal cross-project status dashboard served from the PowerEdge (`atlas`) via Tailscale. Accessible from any Tailscale-connected device (Mac, phone, tablet). Not publicly accessible.

---

## Goals

- See the most recent session log entry at a glance when switching machines
- See a flat prioritized "Up Next" list across all repos
- Drill into any repo's backlog
- Try 3 visual styles to land on a styleguide for all apps

---

## Repo

**Location:** `apps/status-dashboard`  
**Type:** Static HTML, no build tools, no frameworks  
**Hosting:** Nginx on `atlas` (PowerEdge R720xd), port 80  
**Access:** `http://atlas` on Tailscale network

Not deployed to GitHub Pages. Repo may be private or public — the PAT grants read-only access to repo content.

---

## Files

```
status-dashboard/
├── index-a.html          # Variant A — Clean Light
├── index-b.html          # Variant B — Dark Minimal
├── index-c.html          # Variant C — Warm Editorial
├── config.js             # GitHub PAT + owner (git-ignored)
├── config.example.js     # Setup template
├── README.md
├── BACKLOG.md
├── SESSION_LOG.md
└── .gitignore
```

All three HTML files share identical structure and data logic. Only CSS variables and typography differ between variants.

---

## Data Sources

All fetched client-side via GitHub REST API using a personal access token with `repo` (read) scope.

| Data | Source | Endpoint |
|------|--------|----------|
| Repo list | `infra` repo | `repos.json` |
| Last session | `infra` repo | `SESSION_LOG.md` |
| Per-repo backlogs | Each repo in `repos.json` | `BACKLOG.md` |

- `repos.json` is fetched first; all other fetches are driven by its contents
- BACKLOG.md fetches run in parallel via `Promise.allSettled`
- Repos without a BACKLOG.md (404) are skipped silently
- SESSION_LOG.md is parsed to extract the most recent `## YYYY-MM-DD` entry

---

## Layout

Same structure across all 3 variants.

### 1. Header
- Title: "Project Status"
- Last fetched timestamp
- Refresh button (re-fetches all data)

### 2. Status Panel (two cards, side by side)

**Last Session card**
- Date of most recent SESSION_LOG entry
- What we did (bullet list)
- Where we stopped
- Next up

**Up Next card**
- Flat list of first incomplete task from each repo that has one
- Each item labeled with repo name
- Tasks sourced from BACKLOG.md "In Progress" first, then "Ready/Blocked"

### 3. Backlog Accordion

- One collapsible section per repo that has a BACKLOG.md
- Collapsed by default
- Each section shows repo name + count of open tasks as summary
- Expanded view groups tasks by status: **In Progress → Blocked → Ready → Completed**
- Completed tasks are dimmed

---

## Style Variants

### Variant A — Clean Light
- Background: `#f0f4f8`
- Cards: white with subtle border
- Accents: blue (`#2563eb`), green (`#16a34a`), orange (`#ea580c`) for status
- Font: `-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif`
- Inspired by `infra/homelab/infrastructure.html`

### Variant B — Dark Minimal
- Background: `#0d1117`
- Cards: `#161b22` surface with `#30363d` borders
- Accents: muted blue/green, GitHub-style
- Font: same system stack
- Inspired by `apps/recap-viewer/index.html`

### Variant C — Warm Editorial
- Background: `#faf7f2` (cream)
- Cards: white with warm gray border
- Accents: deep ink (`#1a1a1a`), terracotta (`#c4623a`), sage (`#5a7a5a`)
- Font: `Georgia, 'Times New Roman', serif` for headings, system sans for body
- Feels like a personal notebook / field notes

---

## Config

`config.js` (git-ignored):
```js
const CONFIG = {
  token: 'ghp_your_token_here',
  owner: 'DrewBeFree',
  infraRepo: 'homelab',         // repo containing repos.json + SESSION_LOG.md
  reposJsonPath: 'repos.json'
};
```

`config.example.js` is committed as a setup reference.

---

## Nginx Setup (atlas)

```nginx
server {
  listen 80;
  server_name atlas;
  root /opt/status-dashboard;
  index index-a.html;
  location / { try_files $uri $uri/ =404; }
}
```

Repo is cloned to `/opt/status-dashboard` on atlas. To update: `git pull` in that directory.

---

## Out of Scope

- Authentication layer (Tailscale provides access control)
- Write operations (read-only dashboard)
- Automatic refresh interval (manual refresh button only)
- Mobile-specific layout (responsive but not optimized for small screens yet)
- Multi-session log history (only most recent entry shown in status panel)
