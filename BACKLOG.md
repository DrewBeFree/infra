# Infrastructure Backlog

Strategic work to establish consistent structure, standards, and sync across systems.

---

## Completed

- [x] **Task 1 — Audit and document directory structure + naming conventions** (2026-05-18)
  - Created STRUCTURE.md with comprehensive standards
  - Created repos.json manifest (15 repos, 14 cloneable)
  - Created clone-all.ps1 (Windows) and clone-all.sh (Linux/macOS) scripts
  - Reorganized: extracted ai-dog-trainer from DrewBeFree, converted DrewBeFree to profile-only

---

## In Progress

- [ ] **Test `/log-session` skill in a fresh Claude Code session**
  - Open new session, run `/log-session`, confirm entry appears on atlas dashboard
  - Verify `/logoff` calls it correctly at end of an app dev session

- [ ] **WSL Setup — Move infrastructure work to WSL**
  - Set up WSL development environment
  - Test clone scripts in WSL bash
  - Avoid PowerShell encoding issues for future work

---

## Blocked / Ready

- [ ] **Cleanup — Remove hardcoded paths, use environment variables**
  - Replace hardcoded `C:\Users\drewb\Documents\GitHub` with dynamic detection
  - Use `repos.json` baseDirectory or environment variables
  - Ensure all scripts work across Windows/Linux/macOS
  - Applied to: clone-all scripts, session log updater, and future utilities
  - **Status:** Ready; can be done in parallel

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

- [ ] **Unified terminal / cross-machine access**
  - Single window or tool to run commands across Alienware, atlas, and MacBook simultaneously
  - Explore: tmux + SSH, Fabric/Ansible, or MCP SSH tools for Claude
  - Goal: no more juggling 3 terminal windows

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

---

## Notes

- Task 1 is foundational; tasks 2, 3, 4 depend on completion
- Task 3 has hard deadline (PowerEdge arrival ~2026-06-02)
- Task 4 can proceed in parallel once Task 2 templates are clear
- WSL setup needed to avoid PowerShell encoding issues on Windows
