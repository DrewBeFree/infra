# Conventions

Naming, directory layout, and file standards across all repos.

## Top-Level Organization

All projects live in `~/Documents/GitHub/` organized by category:

| Directory | Purpose |
| --- | --- |
| `apps/` | Web applications (PWAs) |
| `sites/` | Static/marketing websites |
| `agents/` | Agentic automation projects |
| `infra/` | Infrastructure & homelab setup |
| `notes/` | Loose markdown notes |

## Project Naming

**Format:** `kebab-case` (lowercase, hyphens between words)

Examples: `daily-planner`, `soccer-pickup`, `uhaul-load-planner`, `drewbefree-command-center`

**Exception:** Brand/personal names use CamelCase (`DrewBeFree`)

## Directory Structure

### Web Apps (PWA)

```
project-name/
├── index.html              # Entry point
├── app.js                  # Main logic
├── auth.js                 # Authentication
├── style.css               # Styling
├── sw.js                   # Service worker
├── manifest.json           # PWA config
├── config.js               # Runtime config (git-ignored)
├── config.example.js       # Config template
├── icons/                  # PWA icons (192, 512)
├── docs/                   # Documentation
├── README.md
├── BACKLOG.md
├── SESSION_LOG.md
├── CNAME                   # Domain mapping
└── .gitignore
```

### Static Sites

```
project-name/
├── index.html
├── style.css
├── assets/                 # Images, fonts, media
├── README.md
├── SESSION_LOG.md
├── CNAME
└── .gitignore
```

### Python Projects

```
project-name/
├── app.py                  # Main application
├── requirements.txt
├── tests/
├── scripts/
├── README.md
├── SESSION_LOG.md
├── .env.example
└── .gitignore
```

## Git Workflow

1. **All work on branches** — never commit directly to `main`
2. **Branch naming:** `dev` for general work, `feat/*` for features, `fix/*` for bugs
3. **Merge to main when ready** — then push
4. **No `Co-Authored-By` trailers** in commit messages

## Configuration Pattern

Secrets use a template + git-ignored actual file:

- JavaScript: `config.example.js` (tracked) + `config.js` (ignored)
- Python: `.env.example` (tracked) + `.env` (ignored)

## Common Root Files

Every project includes: `README.md`, `SESSION_LOG.md`, `.gitignore`

Optional: `BACKLOG.md` (roadmap), `CLAUDE.md` (context), `CNAME` (custom domain)

## GitHub Pages Hosting

Apps and sites deploy from `main` branch with custom domains via `CNAME` file. DNS points to GitHub Pages.

## Multi-Machine Clone

`repos.json` in the infra repo lists all repositories with GitHub URLs and target directories. Clone scripts (`clone-all.ps1` / `clone-all.sh`) replicate the full structure on any machine.
