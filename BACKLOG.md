# Infrastructure Backlog

Strategic work to establish consistent structure, standards, and sync across systems.

---

## Completed

- [x] **Centralize Claude Code config in `claude-config` repo** (2026-05-20)
  - Created private GitHub repo `DrewBeFree/claude-config` as single source of truth
  - Shared: CLAUDE.md, statusline-command.sh, skills (logoff, log-session, update-atlas), commands (kybernet-prep, recap-agents)
  - Per-machine settings under machines/{mac,alienware-windows,alienware-wsl,atlas}
  - Deployed to all 4 environments (Mac, Alienware Windows, Alienware WSL, atlas) using symlinks
  - Added SessionStart hook to auto-pull on every session start — no manual updates needed

- [x] **Test `/log-session` skill in a fresh Claude Code session** (2026-05-20)
  - Verified entry prepends to infra SESSION_LOG.md and pushes via SSH from atlas
  - Confirmed dashboard renders new session block correctly

- [x] **Task 1 — Audit and document directory structure + naming conventions** (2026-05-18)
  - Created STRUCTURE.md with comprehensive standards
  - Created repos.json manifest (15 repos, 14 cloneable)
  - Created clone-all.ps1 (Windows) and clone-all.sh (Linux/macOS) scripts
  - Reorganized: extracted ai-dog-trainer from DrewBeFree, converted DrewBeFree to profile-only

---

## In Progress

- [ ] **WSL Setup — Move infrastructure work to WSL**
  - Set up WSL development environment
  - Test clone scripts in WSL bash
  - Avoid PowerShell encoding issues for future work

---

## Blocked / Ready

- [ ] **Ecosystem project tracking — standardize GitHub Projects + Issues**
  - Inventory existing GitHub Projects and decide which one is the canonical ecosystem board
  - Create/standardize fields: Area, Repo, Visibility, Status, Priority, Deploy Target, Next Action
  - Create matching issue labels across repos: `area/apps`, `area/sites`, `area/agents`, `area/infra`, `visibility/public`, `visibility/private`, `visibility/sensitive`, `deploy/atlas`, `deploy/github-pages`
  - Seed issues for known unfinished work:
    - Commit/push `infra` branch `feat/internal-ecosystem-portal`
    - Commit/push Command Center branch `feat/internal-ecosystem-portal`
    - Deploy internal portal to Atlas at `http://atlas/ecosystem/`
    - Implement UHaul Planner edge/IP restriction before any public exposure
    - Wire portal status/control actions to real commands or documented runbooks
    - Evaluate Leantime as the preferred future self-hosted ecosystem planner once GitHub Projects is in use
  - Add project/issue IDs or URLs back into `ecosystem.json` once the canonical board exists
  - Decide how `BACKLOG.md`, session logs, GitHub Issues, and the internal portal should stay in sync
  - **Status:** Ready; this is the next coordination layer above the portal registry

- [ ] **Cleanup — Remove hardcoded paths, use environment variables**
  - Replace hardcoded `C:\Users\drewb\Documents\GitHub` with dynamic detection
  - Use `repos.json` baseDirectory or environment variables
  - Ensure all scripts work across Windows/Linux/macOS
  - Applied to: clone-all scripts, session log updater, and future utilities
  - **Status:** Ready; can be done in parallel

- [ ] **Task sync receiver — harden raw GitHub issue import before broad rollout**
  - Move the inline raw GitHub issue importer out of `.github/workflows/receive-task-sync.yml` and into `scripts/ecosystem_task_sync.py`.
  - Add tests for `gh-issue:` marker handling, `task-*` marker coexistence, duplicate prevention, and failure reporting.
  - Remove blanket `|| true` from receiver steps so failures are visible.
  - Keep the existing dry-run/report-first contract before `--apply`, especially for Leantime and GitHub Projects writes.
  - Ensure raw issue import does not duplicate BACKLOG-derived tasks that already have `task-*` markers.
  - GitHub issue: https://github.com/DrewBeFree/infra/issues/21
  - **Status:** Ready; created after reviewing the Grok-built Atlas receiver.

- [ ] **Leantime visibility — make admin project lists independent from assignment rows**
  - Root cause: the Leantime menu calls `getProjectHierarchyAssignedToUser()`, which hardcodes `accessStatus: 'assigned'`.
  - Decide whether to maintain a `DrewBeFree/leantime` fork, an upstream PR, or a private `leantime-atlas` overlay repo for source-level patches.
  - Patch admins/owners to use `accessStatus: 'all'` for the menu project hierarchy while preserving assignment-only behavior for regular users.
  - Add/record a durable hotfix script under `scripts/leantime-hotfixes/` if using an overlay instead of a fork.
  - Repair synced project defaults so new API-created projects have `state=1`, `active=1`, and do not require assigning Drew just to be visible.
  - GitHub issue: https://github.com/DrewBeFree/infra/issues/22
  - **Status:** Ready; do not patch the live container ad hoc.

- [ ] **Task 2 — Create project templates for apps and sites**
  - Build reusable templates for new app projects (structure, boilerplate, config files)
  - Build reusable templates for new site projects (structure, boilerplate, config files)
  - Create scaffolding tool or checklist to speed up new project creation
  - **Status:** Blocked by WSL setup; unblocks Task 4

- [ ] **Task 3 — Design multi-system sync strategy for .claude memory and projects**
  - Plan sync between local development machine (Alienware) and homelab PowerEdge R720
  - Network share setup for .claude memory
  - Project synchronization approach
  - Symlink/mount strategy
  - Backup/safety considerations
  - Personal Documents storage architecture:
    - Atlas is the source of truth for Drew's actual Documents folder, not Google Drive or three separate machine-local copies
    - Expose from Atlas via SMB as a daily-use share for Alienware and MacBook
    - Prefer mapped network locations/Finder favorites first; use symlinks/junctions only after testing app compatibility
    - Add limited offline sync/cache only for a small active-work folder if needed
    - Back up Atlas Documents to Google Drive with rclone on a scheduled, logged job
    - Include snapshots/versioning before cloud backup so accidental deletes do not immediately become the only backup state
  - **Deadline:** ~2026-06-02 (PowerEdge arrival)
  - **Status:** Blocked by Task 1; can proceed in parallel with Task 2

- [ ] **Task 4 — Automate recurring tasks: logoff checklist, version management, updates**
  - Reduce manual work for version bumping (patch/minor/major)
  - Automate Command Center card updates
  - ~~Automate SESSION_LOG updates (project memory + repo)~~ ✓ done via `/log-session` skill
  - Automate app registry updates
  - Automate git commits and pushes
  - Backlog integration: export BACKLOG.md → HTML dashboard and/or Leantime/Monday.com sync
  - **Status:** Blocked by Task 2

---

- [ ] **Research project metrics + visualization approach**
  - Decide what project-level metrics actually matter (commit activity, deploy frequency, task completion rate, time-to-ship, etc.)
  - Evaluate options: extend current dashboard with Chart.js, GitHub Insights, Grafana (with GitHub plugin or scripted ingest), or other
  - Grafana is great for time-series infra metrics but awkward for event/context-rich project data — confirm or refute with a small experiment
  - Pick the tool and ship a first visual

- [ ] **Unified terminal / cross-machine access**
  - Single window or tool to run commands across Alienware, atlas, and MacBook simultaneously
  - Explore: tmux + SSH, Fabric/Ansible, or MCP SSH tools for Claude
  - Goal: no more juggling 3 terminal windows

- [ ] **Atlas safety dashboard + Hermes handoff lane**
  - Build a health-first dashboard section for storage, shares, backup freshness, and key Atlas services
  - Surface current hazards: offline `/mnt/data4`, PERC/iDRAC access gap, failed WD Reds, stale/missing backups
  - Link each warning to a runbook before adding any one-click controls
  - Define Hermes vs Claude/Codex responsibilities: Hermes for briefings/monitoring/reminders, Claude/Codex for code/design/implementation work
  - Start with a Markdown morning briefing generator, then feed it into Hermes/dashboard once stable
  - Reference: `docs/atlas-documents-hermes-cheap-handoff.md`
- [ ] **Finish homelab-status-dashboard redesign**
  - Complete Command Center-inspired single-page design
  - Fix backlog accordion expand/collapse
  - Deploy final version to atlas

- [ ] **GitHub file structure + multi-machine clone strategy**
  - Document which repos live where (private vs public, infra vs apps)
  - Standardize how new machines clone the full repo set
  - Integrate with clone-all scripts

- [ ] **Docker strategy for homelab tools**
  - Revisit whether status dashboard, Bob, and other tools should run in Docker on atlas
  - Evaluate if Docker simplifies deployment, updates, and cross-machine access
  - Set up Portainer on atlas first, then evaluate containerizing each tool

- [ ] **Wiki — Make all URLs clickable**
  - Live URLs, GitHub links, and local service addresses in project pages should all be hyperlinked
  - Check infrastructure/services.md and project pages for plain-text URLs

- [ ] **Wiki — Upgrade UI**
  - Custom MkDocs Material theme overrides (colors, fonts, card layout)
  - Consider custom CSS for project pages (icon + metadata side-by-side, manual in expandable section)

---

## Notes

- Task 1 is foundational; tasks 2, 3, 4 depend on completion
- Task 3 has hard deadline (PowerEdge arrival ~2026-06-02)
- Task 4 can proceed in parallel once Task 2 templates are clear
- WSL setup needed to avoid PowerShell encoding issues on Windows
