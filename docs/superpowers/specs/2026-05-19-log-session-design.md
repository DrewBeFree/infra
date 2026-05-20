# Design: `/log-session` Skill + Logoff Integration

**Date:** 2026-05-19
**Status:** Approved

---

## Problem

Session logging was entirely manual. After every conversation, the user had to remember to update three places (infra `SESSION_LOG.md`, project `SESSION_LOG.md`, memory log) and push the infra repo so the atlas dashboard reflects the latest work. This kept breaking down in practice.

---

## Goal

One command — `/log-session` — auto-generates a session entry and pushes it everywhere it needs to go, including the infra repo that drives the atlas dashboard. `/logoff` (app sessions) calls it automatically so no session ever goes unlogged.

---

## Architecture

Two changes:

1. **New `/log-session` skill** — core engine for all session logging
2. **Updated CLAUDE.md logoff checklist** — steps 6 and 7 replaced by a single "run `/log-session`" step

---

## `/log-session` Skill Behavior

Steps execute in order. Every step reports its outcome — skipped steps say "nothing to update" rather than silently passing.

### Step 1 — Auto-generate summary
Synthesize from conversation context:
- What files were changed or created
- What problems were solved
- What tools were run (git operations, config changes, etc.)
- What the user stated as goals at the start

Format as standard 3-section entry:
```
## YYYY-MM-DD HH:MM — <short context phrase>

**What we did:**
- ...

**Where we stopped:**
- ...

**Next up:**
- ...
```

### Step 2 — Update infra `SESSION_LOG.md`
Prepend the entry to `/mnt/c/Users/drewb/Documents/GitHub/infra/SESSION_LOG.md`.
This file is fetched by the atlas dashboard via GitHub API.

### Step 3 — Commit and push infra repo
Commit only `SESSION_LOG.md` on `main`. Push immediately.
No version bumps or other files touched.

### Step 4 — Update memory session log
Mirror the entry to `~/.claude/projects/<current-project>/memory/session_log.md`.
If the memory directory doesn't exist: "nothing to update."

### Step 5 — Update current project `SESSION_LOG.md`
If `SESSION_LOG.md` exists in the current repo root, prepend the same entry.
If not present: "nothing to update."

---

## Integration with `/logoff`

Current logoff checklist (CLAUDE.md) steps 6 and 7 are replaced:

| Before | After |
|--------|-------|
| Step 6: Update `SESSION_LOG.md` in repo root | Step 6: Run `/log-session` |
| Step 7: Update project memory session log | *(absorbed into `/log-session`)* |
| Step 8: Commit and push everything | Step 7: Commit and push app repo |

The app repo commit (version bump, Command Center, state.html) remains a separate push from the infra repo push done by `/log-session`. Two repos, two commits, no mixing.

---

## Skipped Step Reporting

Every step always produces a line of output:
- ✓ Done: brief confirmation
- — Skipped: "nothing to update" with reason (e.g., "no SESSION_LOG.md in current repo")

This keeps the output readable and confirms the skill ran completely.

---

## Out of Scope

- Auto-running at session end (hooks) — too hard to summarize context reliably
- Pushing to any repo other than infra and the current project repo
- Editing past session entries
