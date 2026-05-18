# Infrastructure Backlog

Strategic work to establish consistent structure, standards, and sync across systems.

## Priority Order

### 1. Audit and document directory structure + naming conventions

Review current repo organization and establish clear, consistent naming standards for:
- Directory hierarchy and organization (apps/, sites/, infra/, agents/, notes/)
- File naming (branches, configs, assets, etc.)
- Project naming conventions
- Path management across systems (multi-machine sync strategy)

**Deliverables:**
- `STRUCTURE.md` — Comprehensive standards documentation covering directory hierarchy, naming conventions, project templates, and documentation standards
- `repos.json` — Manifest listing all repositories with GitHub URLs and target directories
- `clone-all.ps1` — PowerShell script to clone all repos with correct folder structure on Windows
- `clone-all.sh` — Bash script to clone all repos with correct folder structure on Linux/macOS

**Status:** ✅ Complete (2026-05-18)

**Outcome:** New machines can now replicate the entire folder structure by running a single clone script with the manifest.

---

### 2. Create project templates for apps and sites

Build reusable templates for:
- New app projects (structure, boilerplate, config files)
- New site projects (structure, boilerplate, config files)
- Scaffolding tool or checklist to speed up new project creation

Base templates on established standards from Task 1.

**Status:** Pending (blocked by Task 1)

---

### 3. Design multi-system sync strategy for .claude memory and projects

Plan how `.claude` memory system, projects, and work sync between:
- Local development machine
- Homelab PowerEdge R720 (arriving ~2026-06-02)

Include:
- Network share setup for .claude memory
- Project synchronization approach
- Symlink/mount strategy
- Backup/safety considerations

**Status:** Pending (blocked by Task 1)

**ETA:** 2026-06-02

---

### 4. Automate recurring tasks: logoff checklist, version management, updates

Reduce manual work for:
- Version bumping (patch/minor/major)
- Command Center card updates
- SESSION_LOG updates (project memory + repo)
- App registry updates
- Git commits and pushes
- Backlog integration: export BACKLOG.md → HTML dashboard and/or Leantime/Monday.com sync

Consider integrating with /logoff skill or creating helper scripts/automation.

**Status:** Pending (blocked by Task 2)

---

## Notes

- Task 1 is foundational; tasks 2 & 3 depend on its output
- Task 3 has a hard deadline (homelab arrival 2026-06-02)
- Task 4 can proceed in parallel once Task 2 is clear on templates
