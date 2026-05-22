# Skills

Skills are instruction sets that Claude Code follows when you invoke them with `/skill-name`. They're not software that runs on a server — they're procedures that run inside Claude's reasoning during a dev session.

A skill is a markdown file in `~/.claude/skills/<name>/SKILL.md`. When you type `/logoff`, Claude reads that file and follows it step by step. Nothing persists after the session; there's no process, no service, no deployment.

Skills live at: `~/.claude/skills/`

---

## log-session

**Invoke:** `/log-session`

Generates a session log entry from conversation context and pushes it everywhere it needs to go. Run this at the end of any session, or as a mid-session checkpoint.

### What it does

1. **Synthesizes the session entry** — reads the conversation to figure out what was done, where things stopped, and what's next. Formats it as a dated entry with `What we did / Where we stopped / Next up`.
2. **Updates infra `SESSION_LOG.md`** — prepends the entry to `/mnt/c/.../infra/SESSION_LOG.md`, which drives the Atlas dashboard at `http://atlas`
3. **Commits and pushes the infra repo** — so the dashboard reflects the new entry immediately
4. **Updates the memory session log** — writes to `~/.claude/projects/<key>/memory/session_log.md` for in-context recall in future sessions
5. **Updates the current project's `SESSION_LOG.md`** — prepends the entry to the repo-local log (if present), ready to be picked up by the next commit

Every step reports its outcome — nothing skipped silently.

### When to use

- End of any session (usually called by `/logoff`)
- Mid-session checkpoint when context window is filling up
- After switching focus to a different repo

---

## logoff

**Invoke:** `/logoff`

Full end-of-session wrap-up checklist. Covers everything that's easy to forget at the end of a session.

### What it does (in order)

1. **Determines what changed** — which app repo(s) were touched, whether it's a bug fix or feature
2. **Bumps the app version** — increments patch (bug fix) or minor (new feature) in the app itself
3. **Updates the Command Center** — updates `card-meta` version + date in `apps/drewbefree-command-center/index.html`
4. **Syncs `state.html`** — keeps the version in `state.html` in sync with the Command Center card (they must always match)
5. **Updates the landing page** — reflects any version or status changes
6. **Updates the app registry** — new version and status
7. **Runs `/log-session`** — generates the session entry and pushes everywhere
8. **Commits and pushes everything** — one clean commit to main

Steps 2–5 only apply when an app repo was touched. Steps 7 and 8 always apply.

### When to use

Every time you're done working. Even for small sessions — the habit is the point.

---

## update-atlas

**Invoke:** `/update-atlas`

Deploys the latest `homelab-status-dashboard` code to Atlas after you've pushed changes to the infra repo.

### What it does

SSHes to Atlas, pulls the latest infra repo, and rsyncs the dashboard files to `/opt/homelab-status-dashboard/` where nginx serves them. Nginx doesn't need to restart — it's serving static files.

### When to use

After pushing any changes to the homelab status dashboard (HTML/CSS/JS files in `infra/`). The dashboard at `http://atlas` won't update until you run this.
