# Log-Session Skill Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Create a `/log-session` skill that auto-generates a session log entry and pushes it to the infra repo (driving the atlas dashboard), memory log, and current project log — then wire it into `/logoff` so all sessions are logged automatically.

**Architecture:** Three files change: a new `log-session/SKILL.md` skill file, the existing `logoff/SKILL.md` skill file (replace steps 6–7 with a call to `/log-session`), and `CLAUDE.md` (same replacement in the Logoff Checklist). No code — these are markdown instruction files for Claude.

**Tech Stack:** Markdown skill files, git CLI, bash

---

## File Map

| Action | File |
|--------|------|
| Create | `/mnt/c/Users/drewb/.claude/skills/log-session/SKILL.md` |
| Modify | `/mnt/c/Users/drewb/.claude/skills/logoff/SKILL.md` |
| Modify | `/mnt/c/Users/drewb/.claude/CLAUDE.md` |

---

### Task 1: Create the `/log-session` skill

**Files:**
- Create: `/mnt/c/Users/drewb/.claude/skills/log-session/SKILL.md`

- [ ] **Step 1: Create the skill directory and file**

Create `/mnt/c/Users/drewb/.claude/skills/log-session/SKILL.md` with this exact content:

```markdown
---
name: log-session
description: Use at the end of any session to auto-generate a session log entry and push it to the infra repo (atlas dashboard), memory log, and current project log.
---

# Log Session

Run this at the end of any session — or mid-session as a checkpoint. Auto-generates the entry from conversation context and pushes everywhere it needs to go.

**Announce at start:** "Running /log-session — capturing this session."

## Steps

Work through all five steps in order. Every step reports its outcome. Skipped steps say "nothing to update" with a reason — never silent.

---

### Step 1 — Generate session entry

Synthesize from conversation context:
- What files were changed or created (from tool calls in this session)
- What problems were solved or goals accomplished
- What the user stated as goals at the start
- Any open items, blockers, or next steps mentioned

Format the entry exactly as:

```
## YYYY-MM-DD HH:MM — <short context phrase>

**What we did:**
- bullet per accomplishment

**Where we stopped:**
- current state, any open items (or "No open items")

**Next up:**
- what comes next (or "No pending work")
```

Use today's date and current time (24h). Keep the context phrase to 5–8 words.

---

### Step 2 — Update infra SESSION_LOG.md

File: `/mnt/c/Users/drewb/Documents/GitHub/infra/SESSION_LOG.md`

This file drives the atlas dashboard at `http://atlas`. Prepend the entry from Step 1 immediately after the `# Session Log` header line (or at the very top if no header exists). Do not append — always prepend.

Report: "✓ infra SESSION_LOG.md updated"

---

### Step 3 — Commit and push infra repo

```bash
cd /mnt/c/Users/drewb/Documents/GitHub/infra
git add SESSION_LOG.md
git commit -m "session: YYYY-MM-DD HH:MM — <context phrase>"
git push
```

Use the same date/context from Step 1 in the commit message.

Report: "✓ infra repo pushed — entry will appear on atlas dashboard"

If push fails, report the error and stop. Do not continue to Steps 4–5.

---

### Step 4 — Update memory session log

Determine the current project key from the working directory path. The key is the path with slashes replaced by hyphens and leading slash dropped. Examples:
- `/mnt/c/Users/drewb/Documents/GitHub` → `-mnt-c-Users-drewb-Documents-GitHub`
- `/mnt/c/Users/drewb/Documents/GitHub/infra` → `-mnt-c-Users-drewb-Documents-GitHub-infra`

File: `/home/drew/.claude/projects/<project-key>/memory/session_log.md`

If the file exists: prepend the entry from Step 1.
If the directory does not exist: report "— memory log: nothing to update (project memory directory not found)"

Report: "✓ memory session log updated" or "— memory log: nothing to update (<reason>)"

---

### Step 5 — Update current project SESSION_LOG.md

Look for `SESSION_LOG.md` in the root of the current repo (use `git rev-parse --show-toplevel` to find the repo root, or fall back to the current working directory).

If found: prepend the entry from Step 1.
If not found: report "— project SESSION_LOG.md: nothing to update (file not present in repo root)"

Do NOT commit this file — it will be picked up by the next commit in the project repo (e.g., by `/logoff`'s final commit step).

Report: "✓ project SESSION_LOG.md updated" or "— project SESSION_LOG.md: nothing to update (<reason>)"

---

## Output Format

After all steps complete, print a summary:

```
Session logged.

✓ infra SESSION_LOG.md — pushed (atlas dashboard updated)
✓ memory log — updated
✓ project SESSION_LOG.md — updated   ← or: — nothing to update
```

## Common Mistakes

- Appending instead of prepending — new entries always go at the top
- Committing files other than `SESSION_LOG.md` to the infra repo
- Forgetting to push — the atlas dashboard reads from GitHub, not the local file
- Skipping steps silently — every step must report its outcome
```

- [ ] **Step 2: Verify the file was created**

```bash
cat "/mnt/c/Users/drewb/.claude/skills/log-session/SKILL.md" | head -5
```

Expected output:
```
---
name: log-session
description: Use at the end of any session to auto-generate a session log entry and push it to the infra repo (atlas dashboard), memory log, and current project log.
---
```

- [ ] **Step 3: Commit**

```bash
cd /mnt/c/Users/drewb/Documents/GitHub/infra
git add docs/superpowers/plans/2026-05-20-log-session-skill.md
git commit -m "Add log-session skill"
```

(The plan file was already created in the infra repo — commit it alongside this task's verification.)

---

### Task 2: Update the `/logoff` skill

**Files:**
- Modify: `/mnt/c/Users/drewb/.claude/skills/logoff/SKILL.md`

- [ ] **Step 1: Read the current file**

Read `/mnt/c/Users/drewb/.claude/skills/logoff/SKILL.md` to confirm current content of steps 6, 7, and 8.

- [ ] **Step 2: Replace steps 6 and 7 with a call to `/log-session`**

Find this block:
```markdown
### 6. Update SESSION_LOG.md (repo)
- Append an entry at the top of `SESSION_LOG.md` in the repo root
- Format:
```
## YYYY-MM-DD — Short description (vX.Y)

**What we did:**
- ...

**Where we stopped:**
- ...

**Next up:**
- ...
```

### 7. Update project memory session log
- Mirror the same entry to `~/.claude/projects/<project>/memory/session_log.md`

### 8. Commit and push everything
```

Replace with:
```markdown
### 6. Run `/log-session`
- Invoke the `/log-session` skill — it auto-generates the session entry and handles:
  - Updating and pushing infra `SESSION_LOG.md` (atlas dashboard)
  - Updating the memory session log
  - Updating the current project `SESSION_LOG.md`
- Every step reports its outcome; skipped steps say "nothing to update"

### 7. Commit and push everything
```

- [ ] **Step 3: Verify the edit looks correct**

```bash
grep -n "log-session\|SESSION_LOG\|memory session" "/mnt/c/Users/drewb/.claude/skills/logoff/SKILL.md"
```

Expected: lines referencing `/log-session` in step 6, no separate step 7 for memory log.

Note: `/mnt/c/Users/drewb/.claude/skills/logoff/SKILL.md` is outside any git repo — no commit needed for this task.

---

### Task 3: Update CLAUDE.md logoff checklist

**Files:**
- Modify: `/mnt/c/Users/drewb/.claude/CLAUDE.md`

- [ ] **Step 1: Read the current Logoff Checklist section**

Read `/mnt/c/Users/drewb/.claude/CLAUDE.md` lines 83–97 to confirm the current step numbering.

- [ ] **Step 2: Replace steps 6, 7, and 8**

Find this block:
```markdown
6. **Update `SESSION_LOG.md`** in the repo root — prepend a new entry
7. **Update project memory session log** — mirror the entry to `~/.claude/projects/<project>/memory/session_log.md`
8. **Commit and push everything** — all of the above in one clean commit to main

Do all steps that apply. Never skip steps 2, 3, 6, 7, and 8 — those always apply after any significant session.
```

Replace with:
```markdown
6. **Run `/log-session`** — auto-generates the session entry and handles infra `SESSION_LOG.md` (atlas dashboard), memory log, and current project `SESSION_LOG.md`
7. **Commit and push everything** — all of the above in one clean commit to main

Do all steps that apply. Never skip steps 2, 3, 6, and 7 — those always apply after any significant session.
```

- [ ] **Step 3: Verify the edit**

```bash
grep -n "log-session\|SESSION_LOG\|memory session\|Never skip" "/mnt/c/Users/drewb/.claude/CLAUDE.md"
```

Expected: step 6 references `/log-session`, step 7 is the commit/push step, "Never skip" line references steps 2, 3, 6, and 7.

Note: `/mnt/c/Users/drewb/.claude/CLAUDE.md` is outside any git repo — no commit needed for this task.

---

### Task 4: Verify end-to-end

- [ ] **Step 1: Confirm skill file is discoverable**

```bash
ls "/mnt/c/Users/drewb/.claude/skills/"
```

Expected output includes: `log-session/` and `logoff/`

- [ ] **Step 2: Confirm logoff skill references log-session**

```bash
grep "log-session" "/mnt/c/Users/drewb/.claude/skills/logoff/SKILL.md"
```

Expected: at least one match in step 6.

- [ ] **Step 3: Confirm CLAUDE.md references log-session**

```bash
grep "log-session" "/mnt/c/Users/drewb/.claude/CLAUDE.md"
```

Expected: one match in the Logoff Checklist.

- [ ] **Step 4: Confirm infra SESSION_LOG.md is writable and pushable**

```bash
cd /mnt/c/Users/drewb/Documents/GitHub/infra && git status && git log --oneline -3
```

Expected: clean working tree, recent commits visible.

- [ ] **Step 5: Run `/log-session` in a new session to validate**

Open a new Claude Code session and type `/log-session`. Verify:
- It announces "Running /log-session — capturing this session."
- It generates a plausible entry from context
- It prepends to `/mnt/c/Users/drewb/Documents/GitHub/infra/SESSION_LOG.md`
- It commits and pushes
- It reports each step's outcome
- The entry appears at `http://atlas` within a few seconds of the push
