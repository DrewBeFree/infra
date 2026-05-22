# Logoff Checklist

Steps to run at the end of every significant session.

## The Checklist

Run all steps in order when saying "logoff":

1. **Bump app version** — increment minor for new features, patch for bug fixes
2. **Update Command Center** (`apps/drewbefree-command-center/index.html`) — update `card-meta` version + date for the affected app card
3. **Update state.html** (`apps/drewbefree-command-center/state.html`) — update version + date for the affected app row
4. **Update landing page** — reflect any version/status changes
5. **Update app registry** — update version and status for the app
6. **Run `/log-session`** — auto-generates the session entry (infra SESSION_LOG.md, memory log, and current project SESSION_LOG.md)
7. **Commit and push everything** — all of the above in one clean commit to main
8. **Deploy the wiki** — if wiki content or catalog changed, run `./wiki/deploy.sh` from `infra/`

## Which Steps Always Apply

Steps 2, 3, 6, and 7 always apply after any significant session. Step 8 applies whenever wiki content changed. The others apply only if app code was changed.

## Session Log Format

```markdown
## YYYY-MM-DD (context if needed)

**What we did:**
- ...

**Where we stopped:**
- ...

**Next up:**
- ...
```

Session logs are saved in two places:

1. **Project memory** — `~/.claude/projects/<project>/memory/session_log.md`
2. **Repo file** — `SESSION_LOG.md` in the repo root
