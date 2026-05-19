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

- [ ] **WSL Setup — Move infrastructure work to WSL**
  - Set up WSL development environment
  - Test clone scripts in WSL bash
  - Avoid PowerShell encoding issues for future work

---

## Blocked / Ready

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
  - Automate SESSION_LOG updates (project memory + repo)
  - Automate app registry updates
  - Automate git commits and pushes
  - Backlog integration: export BACKLOG.md → HTML dashboard and/or Leantime/Monday.com sync
  - **Status:** Blocked by Task 2

---

## Notes

- Task 1 is foundational; tasks 2, 3, 4 depend on completion
- Task 3 has hard deadline (PowerEdge arrival ~2026-06-02)
- Task 4 can proceed in parallel once Task 2 templates are clear
- WSL setup needed to avoid PowerShell encoding issues on Windows
