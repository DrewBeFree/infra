# Directory Structure & Naming Standards

This document establishes consistent naming conventions and organizational standards across all repos.

---

## Top-Level Organization

All projects live in `C:\Users\drewb\Documents\GitHub\` organized by category:

| Directory | Purpose | Count |
|-----------|---------|-------|
| `apps/` | Web applications (PWAs) | 9 projects |
| `sites/` | Static/marketing websites | 3 projects |
| `agents/` | Agentic automation projects | 1 project |
| `infra/` | Infrastructure & homelab setup | Current repo |
| `notes/` | Loose markdown notes | N/A |
| `DrewBeFree/` | Main Python backend | 1 project |

Hidden directories:
- `.claude/` — Claude Code settings (global + per-project)
- `.superpowers/` — Claude superpowers skill archive
- `.obsidian/` — Obsidian vault
- `_worktrees/` — Git worktree isolation directory

---

## Project Naming Convention

**Format:** `kebab-case` (lowercase, hyphens between words)

**Examples:**
- `daily-planner`
- `soccer-pickup`
- `uhaul-load-planner`
- `drewbefree-command-center`
- `recap-agents`

**Exception:** Brand/personal names use CamelCase (`DrewBeFree`)

---

## Directory Structure Template

### Web Apps (PWA Template)

```
project-name/
├── index.html                    # App entry point
├── app.js                        # Main application logic
├── auth.js                       # Authentication handler
├── style.css                     # Styling
├── sw.js                         # Service worker (offline support)
├── manifest.json                 # PWA configuration
├── config.js                     # Runtime configuration (git-ignored)
├── config.example.js             # Config template
├── favicon.png                   # Browser favicon
│
├── icons/                        # PWA icon assets
│   ├── project-name-192.png      # 192x192 icon
│   └── project-name-512.png      # 512x512 icon
│
├── docs/                         # Project documentation
│   └── superpowers/              # Brainstorming records
│
├── README.md                     # Project overview
├── BACKLOG.md                    # Feature roadmap
├── SESSION_LOG.md                # Session history
├── CLAUDE.md                     # Claude Code context (optional)
├── CNAME                         # Domain mapping (GitHub Pages)
│
├── .claude/                      # Claude Code settings
│   ├── settings.json
│   └── settings.local.json
│
├── .superpowers/                 # Brainstorming archive
└── .gitignore                    # Git ignore rules
```

### Static Websites

```
project-name/
├── index.html                    # Entry point
├── style.css                     # Styling
├── favicon.png                   # Browser favicon
│
├── docs/                         # Documentation
├── assets/                       # Images, fonts, media
│
├── README.md
├── SESSION_LOG.md
├── CNAME
│
├── .claude/
└── .gitignore
```

### Python/Backend Projects

```
project-name/
├── app.py                        # Main application
├── requirements.txt              # Python dependencies
├── config.example.py             # Config template
│
├── tests/                        # Test suite
├── docs/                         # Documentation
├── scripts/                      # Utility scripts
│
├── README.md
├── SESSION_LOG.md
├── CLAUDE.md
│
├── .env.example                  # Environment template
├── .claude/
└── .gitignore
```

### Infrastructure / Docker

```
project-name/
├── stacks/                       # Docker Compose stacks
│   └── {service-name}/
│       └── docker-compose.yml
│
├── scripts/                      # Deployment/sync scripts
│   ├── ingest.py
│   └── sync.py
│
├── docs/                         # Architecture & specs
│   ├── ATLAS_OVERVIEW.md
│   └── architecture-*.md
│
├── kb/                           # Knowledge base
├── staging/                      # Interim data
│
├── README.md
├── SESSION_LOG.md
├── CLAUDE.md
│
├── .env.example
└── .gitignore
```

---

## File Naming Conventions

### Standard Root Files

| Filename | Purpose | Used In |
|----------|---------|---------|
| `index.html` | Entry point | All apps & sites |
| `app.js` / `app.py` | Main logic | Most projects |
| `config.js` / `config.py` | Configuration (git-ignored) | Apps, backends |
| `config.example.js` / `config.example.py` | Config template (git-tracked) | Apps, backends |
| `.env.example` | Environment template | Python projects |
| `manifest.json` | PWA metadata | All apps |
| `sw.js` | Service worker | All apps |
| `favicon.png` | Browser icon | All projects |
| `style.css` | Styling | Most projects |
| `auth.js` / `auth.py` | Authentication | Apps with auth |
| `README.md` | Project overview | All projects |
| `BACKLOG.md` | Feature roadmap | Most apps |
| `CLAUDE.md` | Claude Code context | Key projects |
| `SESSION_LOG.md` | Session history | All projects |
| `CNAME` | Domain mapping | Apps, sites |

### Directory Names

- **Standard lowercase:** `docs`, `tests`, `scripts`, `assets`, `icons`, `kb`, `staging`
- **Hidden (dot-prefix):** `.claude`, `.superpowers`, `.git`, `.gitignore`

### Icon Assets

Format: `{project-name}-{size}.png`

Examples:
- `daily-planner-192.png` (192×192, home screen)
- `daily-planner-512.png` (512×512, splash screen)

### Git Branches

| Pattern | Purpose | Examples |
|---------|---------|----------|
| `main` | Production branch (primary) | Main branch, no other naming |
| `dev` | Development/staging | Long-lived development branch |
| `feat/{feature}` | Feature development | `feat/pwa`, `feat/dark-mode`, `feat/dashboard-redesign` |
| `fix/{issue}` | Bug fixes | `fix/cleanup-dead-refs`, `fix/generate-html` |
| `claude/{task}` | Claude Code work | `claude/ai-dog-trainer` |

---

## Configuration File Strategy

### Pattern: Config Template + Git-Ignored Actual

**For JavaScript projects:**
```javascript
// config.example.js (git-tracked)
export const CONFIG = {
  SUPABASE_URL: "YOUR_SUPABASE_URL",
  SUPABASE_KEY: "YOUR_SUPABASE_KEY"
};

// config.js (git-ignored, created by developer)
export const CONFIG = {
  SUPABASE_URL: "https://actual-project.supabase.co",
  SUPABASE_KEY: "actual-key-here"
};
```

**For Python projects:**
```
.env.example (git-tracked)
SUPABASE_URL=YOUR_SUPABASE_URL
SUPABASE_KEY=YOUR_SUPABASE_KEY

.env (git-ignored, created by developer)
SUPABASE_URL=https://actual-project.supabase.co
SUPABASE_KEY=actual-key-here
```

---

## Technology Stack by Project Type

| Project Type | Tech Stack | Examples |
|---|---|---|
| **Web App (PWA)** | HTML/CSS/JS, Service Worker, Manifest | daily-planner, recipes, poker |
| **Static Site** | HTML/CSS, GitHub Pages | kybernet-tech, photography |
| **Backend/API** | Python Flask | DrewBeFree |
| **Agentic** | Python, script-based, integrations | recap-agents |
| **Infrastructure** | Docker Compose, Python scripts | homelab atlas stacks |

---

## Common Root Files: All Projects

Every project should include:

```
README.md              # Overview, setup instructions, usage
SESSION_LOG.md         # Session-by-session progress log
.gitignore            # Ignore config.js, .env, .superpowers/, etc.
.claude/              # Claude Code settings (settings.json, settings.local.json)
```

**Optional:**
- `BACKLOG.md` — Feature roadmap (used in most apps)
- `CLAUDE.md` — Codebase documentation (used in key projects)
- `CNAME` — Custom domain (apps & sites only)

---

## Git Workflow

1. **All work on branches** — never commit directly to `main`
2. **Branch naming:** `dev` for general work, `feat/*` for features, `fix/*` for bugs
3. **Merge to main when ready** — then push
4. **Commit message style:** Clear, concise, no `Co-Authored-By` trailers (see CLAUDE.md)

---

## GitHub Pages Hosting

Apps and sites use GitHub Pages with custom domains:

1. Domain mapping set in repository `CNAME` file
2. DNS configured to point to GitHub Pages
3. Repository must be public or GitHub Pages must be enabled
4. Branch: Deploy from `main` branch

Example `CNAME` file:
```
daily-planner.drewb.dev
```

---

## Documentation Standards

### README.md

Every project must have a `README.md` covering:
- Project description (1-2 sentences)
- Quick start / setup instructions
- Technology stack
- Key features / current state
- Known issues (if any)

### SESSION_LOG.md

Append a dated entry after every significant session:

```markdown
## YYYY-MM-DD

**What we did:**
- ...

**Where we stopped:**
- ...

**Next up:**
- ...
```

### BACKLOG.md (Apps)

Feature roadmap for planned work:
- Organized by priority or category
- Status indicators (pending, in progress, completed, blocked)
- Brief description per item

---

## Enforcement

- New projects use this template structure
- Naming follows kebab-case convention
- All root projects maintain README.md, SESSION_LOG.md, .gitignore
- Apps & sites include manifest.json, sw.js, favicon.png, icons/
- Configuration uses template pattern (config.example.js / .env.example)

---

## Related Documents

- `alienware-vs-poweredge.md` — Workload split decision rule
- `infrastructure-tools.md` — Tools reference for both systems
- `INFRASTRUCTURE.md` — Strategic backlog and task list
