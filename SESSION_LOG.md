## 2026-06-17 - Atlas canonical repo migration pass

**What we did:**
- Confirmed the intended model: GitHub is source of truth, Atlas owns the canonical development checkout at `/home/drew/GitHub`, and Alienware should not hold authoritative repo state.
- Added `yes`, `trading-scanner`, `trading-scanner-experimental`, and `luke-codex-guide` to `infra/repos.json` so they fit the existing `apps/`, `sites/`, `agents/`, `homelab`, `infra`, `claude-config` structure.
- Upgraded `scripts/clone_manifest.py` from clone-only to clone-or-sync: it clones missing repos, fetches existing repos, fast-forwards clean behind repos with `--pull`, and skips dirty/ahead repos.
- Added `docs/atlas-canonical-github-workspace.md` documenting the Atlas/GitHub/Alienware model and pruning rule.
- Copied the updated manifest and sync script to Atlas.
- Ran the sync on Atlas; it cloned `/home/drew/GitHub/apps/yes` and `/home/drew/GitHub/sites/luke-codex-guide`.
- Pushed infra branch `feat/morning-repo-sync-brief` to GitHub at `963d2a0`.
- Archived clean Alienware-only active checkouts `apps/yes` and `sites/luke-codex-guide` to `C:\Users\drewb\Documents\GitHub-archive\alienware-pruned-2026-06-17\`.
- Left dirty/ahead Alienware repos in place rather than deleting local-only work.
- Verified Hermes still returns `200` at `http://atlas:9119/command-center`.

**Where we stopped:**
- Atlas has the canonical 27-repo manifest shape.
- Alienware active tree no longer contains the clean extra `yes` or `luke-codex-guide` checkouts.
- Remaining Alienware checkouts still include dirty/ahead work that needs commit/push or explicit discard before pruning.
- Atlas also has dirty repos, mostly `.github/` task-sync files plus real work in `llm-debate-union`, `lead-gen-agent`, and both trading scanner repos.

**Next up:**
- Review and commit/push the remaining dirty Atlas repos in batches, then rerun `clone_manifest.py --pull` and archive the matching Alienware checkouts once each repo is clean and represented on GitHub.
- Decide whether `agents/interactive-setup` should get a GitHub repo or be archived/discarded; `DrewBeFree/interactive-setup` does not currently exist.

## 2026-06-17 - Restore Hermes dashboard on Atlas

**What we did:**
- Reproduced `http://atlas:9119/` and `/command-center` returning `500 Internal Server Error`.
- Traced the live Hermes dashboard failure to `FileNotFoundError` for `/home/drew/.hermes/hermes-agent/hermes_cli/web_dist/index.html`.
- Found Hermes had moved to `/home/drew/.hermes/hermes-agent.full`, while the service unit and CLI wrapper still referenced `/home/drew/.hermes/hermes-agent`.
- Restored `/home/drew/.hermes/hermes-agent` as a symlink to `/home/drew/.hermes/hermes-agent.full`.
- Restarted `hermes-dashboard.service` and `hermes-gateway.service`; Hermes rebuilt the web UI and reported `HERMES_DASHBOARD_READY port=9119`.
- Verified `/`, `/command-center`, `/favicon.ico`, and `/api/status` return `200` through `http://atlas:9119`.
- Verified the in-app browser loads `Hermes Agent - Dashboard` at `/command-center` with no captured console errors.

**Where we stopped:**
- Hermes dashboard and Command Center are back up through the Atlas Tailscale nginx proxy.
- `hermes-gateway.service` still logs a Linear MCP OAuth authorization requirement, but that was not the dashboard 500 root cause.

**Next up:**
- If Hermes breaks after a future update, check whether `/home/drew/.hermes/hermes-agent` still points at the active checkout before debugging nginx or browser headers.

## 2026-06-07 - Lead Desk Hub reachable from Alienware

**What we did:**
- Confirmed Alienware could not connect to Atlas ports `3027` or `8017`.
- Confirmed Atlas Tailscale IP is `100.71.165.80`.
- Started persistent user services on Atlas:
  - `lead-gen-api.service` bound to `100.71.165.80:8017`
  - `lead-desk-hub.service` bound to `100.71.165.80:3027`
- Kept the services on the Tailscale IP instead of binding to all interfaces.
- Verified from Alienware that `http://atlas:3027` returns `200` with title `Surf the Webb Lead Desk`.
- Verified from Alienware that `http://atlas:8017/api/dashboard` returns dashboard JSON.

**Where we stopped:**
- The ecosystem portal link `http://atlas:3027` now resolves to the actual Lead Desk Hub from Alienware.
- The backend API is reachable at `http://atlas:8017`.

**Next up:**
- Decide whether to add a cleaner nginx route such as `http://atlas/lead-desk/` later, or keep direct Tailscale ports.

## 2026-06-07 - Correct Lead Desk Hub target

**What we did:**
- Corrected the previous wiki fallback: Lead Gen Agent portal links now point to the actual Atlas Desk Hub target, `http://atlas:3027`.
- Updated the portal lead-count API target to `http://atlas:8017/api/dashboard`.
- Updated `ecosystem.json`, `internal-portal/index.html`, `internal-portal/app.js`, `internal-portal/README.md`, and `internal-portal/portal.test.mjs`.
- Installed/build dependencies for the Lead Gen Agent checkout on Atlas under `/home/drew/GitHub/agents/lead-gen-agent`.
- Deployed the corrected portal files to `/opt/homelab-status-dashboard/ecosystem/`.
- Verified live Atlas HTML links to `http://atlas:3027`, live registry includes `http://atlas:3027` and `http://atlas:8017`, and live JS fetches `http://atlas:8017/api/dashboard`.

**Where we stopped:**
- The ecosystem portal now targets the Desk Hub instead of the wiki.
- The Desk Hub service is still not running on Atlas; the attempt to create persistent user services bound to `0.0.0.0:3027` and `0.0.0.0:8017` was blocked pending explicit approval because it is a lasting network exposure change.

**Next up:**
- Explicitly approve starting persistent Atlas services for `lead-gen-api.service` and `lead-desk-hub.service`, or choose a narrower binding/proxy plan.

## 2026-06-07 - Lead Agent Atlas link fix

**What we did:**
- Reproduced the broken Lead Gen Agent ecosystem links: `127.0.0.1:3027` and `100.117.87.57:3027` are not listening.
- Confirmed Atlas currently has the Lead Gen Agent wiki/project page, but no deployed Lead Desk service on `3027` or `8017`.
- Updated `ecosystem.json`, the ecosystem portal priority card/link, `app.js`, `README.md`, and the portal contract test so Lead Gen Agent points to `http://atlas/wiki/projects/lead-gen-agent/` instead of dead Alienware/local dev URLs.
- Deployed the updated portal files to Atlas at `/opt/homelab-status-dashboard/ecosystem/`.
- Verified live Atlas HTML, registry JSON, and app JS no longer advertise the stale `:3027` links.

**Where we stopped:**
- The live ecosystem portal now routes Lead Agent links to the Atlas-hosted project page.
- The always-on Lead Desk app itself is still not deployed on Atlas.

**Next up:**
- Stand up the Lead Desk service on Atlas under `/opt/homelab/stacks/lead-gen-agent`, then change the portal from the project-page link to the real Atlas service URL.

## 2026-06-06 09:42 - AI Token Dashboard added to ecosystem portal

**What we did:**
- Added `AI Token Dashboard` as a top-level priority link in `internal-portal/index.html`.
- Added `ai-token-dashboard` to `ecosystem.json` with live URL `http://atlas:7474`.
- Updated `internal-portal/README.md` priority links.
- Deployed the updated portal files directly to Atlas under `/opt/homelab-status-dashboard/ecosystem/`.
- Verified `http://atlas/ecosystem/` serves the tile and `http://atlas/ecosystem/ecosystem.json` includes the registry item.

**Where we stopped:**
- Source commit `14ba289` is pushed on branch `feat/morning-repo-sync-brief`.
- Portal validation passed: `python -m json.tool ecosystem.json` and `node internal-portal/portal.test.mjs`.

**Next up:**
- Open/merge the infra branch when the broader morning repo-sync work is ready.

## 2026-06-05 02:41 — AI Dashboard Activity and Settings views

**What we did:**
- Added Activity view: 30-day stacked token chart (full-width), summary cards (sessions/messages/API value), daily breakdown table with per-model color badges
- Added Settings view: editable form for display name, per-subscription monthly costs, API keys (OpenAI/xAI/Gemini with show/hide toggle), Ollama host, GCP project ID
- Added GET /api/config endpoint to app.py — returns current config.json
- Added POST /api/config endpoint — merges and saves updates (handles subscriptions list and api_keys dict separately to avoid clobbering unlisted fields)
- Extracted _send_json() helper in Handler to eliminate duplication
- Wired nav links (Activity, Settings) with switchView() JS; all three views fully functional
- Rewrote MANUAL.md to reflect current architecture (generate-stats.py, atlas deployment, all providers, new views)
- Deployed to atlas; service healthy

**Where we stopped:**
- All three dashboard views working at http://atlas:7474
- Settings saves to ~/services/ai-dashboard/config.json on atlas; Overview picks up changes on next Refresh

**Next up:**
- GCP credits editing in Settings (currently manual config.json edits only)
- Long-term SQLite history to extend beyond the 30-day session file window

## 2026-06-05 00:24 — Atlas backend gateway live for LDU

**What we did:**
- Built FastAPI backend (`backend/main.py`) with unified `/api/llm` endpoint and `/api/health`
- Implemented Gemini (gemini-2.5-flash) server-side; OpenAI, Claude, Grok stubbed
- Added `backend/requirements.txt`, `.env.example`, `start.sh` (auto-venv), `ldu-gateway.service` (systemd)
- Updated `app-config.js` to point gatewayUrl at Atlas (`10.0.0.145:8001`)
- Updated `app.js` hybrid mode to route all cloud providers through `callGateway()` — no API keys in browser
- Resolved merge conflict with app-factory branch, corrected Atlas IP, fixed port conflict (moved to 8001)
- Restored index.html (overwritten by app-factory branch), added app-config.js script tag
- Fixed Gemini model name (gemini-2.5-flash), fixed thinkingConfig placement in API payload
- Added Private Network Access CORS header for browser-to-private-IP requests
- Installed `ldu-gateway` as a persistent systemd service on Atlas (auto-starts on reboot)
- Set up SSH key auth on Atlas for GitHub, added `ldu-update` alias for one-command redeploy
- Bumped version to v0.4.0, updated MANUAL.md with architecture section

**Where we stopped:**
- Gateway live and confirmed working — Gemini turns hitting Atlas with 200 OK
- OpenAI, Claude, Grok return stub text — keys not yet added to Atlas .env

**Next up:**
- Add API keys for OpenAI, Claude, Grok to Atlas `backend/.env` and implement provider functions
- Consider serving frontend from Atlas instead of WSL start_server.py

## 2026-06-01 20:30 — Phase A App Factory wrap-up

**What we did:**
- Cleaned up Phase A E2E test scaffolding (TEST_BASE_BRANCH override, test-only alerts, transcript injection).
- Added lightweight success toast for GitHub blueprint push (feed was not visible in Verdict state).
- Merged feat/app-factory-phase-a into main and deleted the feature branch.
- Confirmed the reliable value is the client-side architecture blueprint push from Engineering Assembly; full remote factory (Action-generated PRs) deprioritized after testing showed no visible results.
- Noted ongoing WSL networking friction for browser access to local services (PocketBase, etc.).

**Where we stopped:**
- Phase A changes merged and cleaned. Blueprint push flow is solid.
- No generated app PRs from the Action after multiple attempts.
- Test code and feature branch removed.

**Next up:**
- Add real LLM provider API keys for live hybrid mode.
- Continue other priorities.

# Session Log

## 2026-05-30 16:41 — Fixed telemetry report persistence bug

**What we did:**
- Identified root cause: `loadHistorySession()` restored stats, but `handleMotionSelect()` called `resetState()` which cleared them
- Fixed by saving stats before `resetState()` and restoring them after (lines 2081-2091 in app.js)
- Verified fix with code simulation: stats now preserve through session load (turns: 15 → 0 → 15)
- Confirmed pre-populated test session has complete telemetry (15 turns, 1,774 tokens, detailed logs)
- Committed fix with detailed message explaining bug and solution

**Where we stopped:**
- Clarification needed: Previous session apparently planned to deploy to Atlas (PowerEdge server), but deployment method/scope was unclear
- Current state: Fix is committed to main, app running locally on http://localhost:8080/, awaiting deployment plan clarification

**Next up:**
- Check with Codex about Atlas deployment plan (Docker container? Persistent backend storage? Accessibility requirements?)
- Once plan is confirmed, set up appropriate deployment infrastructure (docker-compose, reverse proxy, etc.)

## 2026-05-30 - Track workspace cleanup notes

**What we did:**
- Tracked AI workspace cleanup and Atlas wiki deploy issue notes under `docs/`.
- Ignored local wiki `.claude` settings so machine-specific permissions do not stay as untracked noise.

**Where we stopped:**
- Changes are on branch `docs/track-workspace-notes`.

**Next up:**
- Open and merge the follow-up PR.
## 2026-05-30 - Update wiki docs for homelab split

**What we did:**
- Updated wiki docs for `/update-atlas` to point at the `homelab` repo dashboard path.
- Updated workflow conventions to list `infra/` and `homelab/` as separate top-level repos.
- Checked that old `infra/homelab-status-dashboard` references no longer appear in the edited docs.

**Where we stopped:**
- Changes are ready to commit on branch `fix/separate-homelab-repo`.
- Local wiki build was not run because WSL bash was blocked and the wiki venv is Linux-style.

**Next up:**
- Commit/push the wiki doc cleanup.
- Run wiki build/deploy from WSL or Atlas-capable environment later.
## 2026-05-30 - Move homelab status dashboard to homelab repo

**What we did:**
- Moved `homelab-status-dashboard/` out of `infra` and into the sibling `homelab` repo.
- Kept `infra` focused on workspace/repo/wiki tooling rather than homelab service assets.

**Where we stopped:**
- The folder removal is committed and pushed on `infra` branch `fix/separate-homelab-repo`.
- The dashboard folder is committed and pushed in `homelab` branch `feat-lead-gen-agent-v2`.

**Next up:**
- Close the session; later, remove the old ignored `infra\homelab` copy after handles are released.

## 2026-05-30 - Split homelab into sibling repo

**What we did:**
- Created a sibling `C:\Users\drewb\Documents\GitHub\homelab` copy of the nested homelab repo because Windows would not move the active Codex working directory.
- Removed `homelab` as a submodule from the `infra` repo by deleting `.gitmodules` and removing the gitlink from the index.
- Updated `repos.json` so clone scripts treat `homelab` as its own top-level sibling repo.
- Updated `STRUCTURE.md` to distinguish `infra` as workspace/wiki/clone tooling and `homelab` as Alienware + Atlas docs/maps/service plans.
- Added `/homelab/` to `infra/.gitignore` so the old nested folder can sit ignored until it is safe to delete after this session releases its file handle.

**Where we stopped:**
- `infra` is on pushed branch `fix/separate-homelab-repo` with the sibling-repo cleanup committed.
- `homelab` exists as a sibling repo and remains on branch `feat-lead-gen-agent-v2`.
- The old nested `infra/homelab` folder still exists physically because Windows reported it was in use.

**Next up:**
- Push `fix/separate-homelab-repo`.
- After closing this Codex/browser session, delete the old ignored `infra/homelab` folder if no process is using it.

## 2026-05-30 02:50 — camera rotation fix, v0.14.2

**What we did:**
- Diagnosed camera rotation breaking after centering: root cause was missing interpolated newX/newY/newZ values in animateCamera()
- Fixed camera.js to restore position interpolation during animation (lines 76-78)
- Added camera.lookAt() to keep camera aligned with shifting target
- Explicitly disable controls during animation, re-enable + sync spherical coords at end
- Added regression test in camera.test.js to verify interpolation
- Bumped version from v0.14.1 to v0.14.2 (patch for bug fix)
- Updated Command Center (index.html) and state.html to v0.14.2 · 2026-05-30
- Updated terminal scan line with new version
- Regenerated wiki catalog and pushed

**Where we stopped:**
- All version numbers updated, Command Center synced, wiki catalog pushed
- Ready for final commit

**Next up:**
- Commit version + Command Center changes to main
- Deploy wiki to atlas

---

## 2026-05-29 18:37 — UHaul Planner v0.14.1 test & fixes

**What we did:**
- Tested UHaul Load Planner v0.14.0 features from overnight session checklist
- Found 4 UX issues: items spawning inside truck, missing capacity % display, confusing weight warning, camera rotation disabled post-centering
- Fixed all 4 issues and committed to dev/overnight-improvements
- Merged branch to main, bumped version to v0.14.1
- Updated Command Center, state.html, and testing documentation

**Where we stopped:**
- Testing complete, all fixes merged to main, version bumped

**Next up:**
- No pending work

---

## 2026-05-29 17:28 — Game status badge with host cancel control

**What we did:**
- Added prominent status badge to signup page: "✓ Game On" (6+ signups), "⏳ Pending Seat Count" (<6), or "❌ Cancelled"
- Added "🚫 Cancel Game" button to host panel to toggle game cancellation state
- Added `is_cancelled` column to `poker_games` table in Supabase
- Fixed version numbering to v0.7.0 across all files (signup page, host panel, Command Center, state.html)
- Created CLAUDE.md with deployment checklist to prevent missed version/footer updates
- Reserved v1.0 for after first full game playtest with user approval

**Where we stopped:**
- Live on main. v0.7.0 deployed.

**Next up:**
- Play through first complete game and approve for v1.0 release

---

## 2026-05-29 (overnight session 2) — Ollama monitoring + lead gen agent plan

**What we did:**

### Ollama Monitoring Stack (Complete, Production-Ready)
- Created comprehensive monitoring setup guide: `ollama-monitoring-setup.md` (5 approaches analyzed)
- Built custom Prometheus exporter (`ollama-exporter/exporter.py`) collecting model metrics
- Created complete Docker Compose stack: Ollama + Prometheus + Grafana + Node Exporter
- Pre-configured Grafana dashboard "Ollama Overview" (auto-loads on startup)
- Included pre-built alerts, config templates, standalone exporter option
- Comprehensive README with quick-start, troubleshooting, metrics reference

### Facebook/Monday.com Lead Gen Agent (Implementation Plan)
- Created detailed 12-16 hour implementation plan: `facebook-monday-lead-gen-agent.md`
- 4 phases documented: POC (4-6h), Testing (2-3h), Automation (2-4h), Scaling (4-6h)
- Tech stack: Playwright + Claude API + SQLite + homelab cron
- 4 detailed implementation tasks with code sketches (scraper, classifier, state mgmt, agent loop)
- 3 deployment options analyzed (homelab cron recommended, cost-free)
- Risk mitigation: bot detection, privacy, quality assurance
- Success metrics and future enhancements outlined

**Where we stopped:**
- Ollama monitoring: Production-ready, can deploy immediately (`cd ollama-exporter && docker-compose up -d`)
- Lead gen agent: Implementation plan complete, ready for Phase 1 execution

**Next up:**
- Deploy Ollama stack to homelab
- Clarify 6 refinement questions on lead gen agent, start Phase 1 POC
- Monitor Ollama metrics in Grafana, tune dashboard

## 2026-05-29 03:50 — autonomous overnight UHaul improvements setup

**What we did:**
- Set up autonomous work permissions: .claude/settings.json in project root configured to allow Read/Write/Edit/Bash and safe git operations (blocks merges to main, force pushes)
- Created reusable /autonomous-work skill for future autonomous sessions on any project
- Created dev/overnight-improvements branch for accumulated UHaul improvements
- Implemented PWA install banner: iOS Safari users see share-to-home-screen prompt on first visit, dismissible via localStorage
- Recovered and corrected SESSION_LOG.md after accidental overwrite (preserved full history)

**Where we stopped:**
- PWA banner committed and tested; branch pushed to origin
- Permissions configured and tracked in git (will auto-load next session)
- Ready for next session to continue: keyboard shortcuts, modal improvements, performance optimizations, then merge to main as v0.14.0

**Next up:**
- Add keyboard shortcuts (? for help, Ctrl+N for new item, etc.)
- Enhance ModalAddEdit with better input hints and validation feedback
- Optimize Sidebar's uniqueSqFt calculation
- Polish truck recommendation algorithm
- Test, merge, and bump version to v0.14.0

## 2026-05-28 23:12 — CRLF line-ending normalization cleanup

**What we did:**
- Ran logoff on llm-debate-union; discovered 8 files had CRLF → LF line-ending drift (.gitignore, CONTEXT.md, SESSION_LOG.md, app.js, index.html, start_server.py, style.css, sw.js)
- Confirmed via `git diff -w` that no functional code was changed — pure whitespace normalization

**Where we stopped:**
- No open items; pending commit of the line-ending cleanup

**Next up:**
- Commit the CRLF cleanup and push to main
- Optional: add `.gitattributes` with `* text=auto eol=lf` to prevent recurrence

## 2026-05-28 — daily-planner: Ideas, voice dictation, task categories

**What we did:**
- Added Ideas tab: full CRUD (add, delete, timestamp display), Supabase-backed with demo mode support
- Added voice dictation via Web Speech API — mic button on task and idea inputs, toggles `.recording` state
- Added task categories with colored badge rendering (Personal, Urgent, Work); category stored in Supabase `tasks` table

**Where we stopped:**
- All features committed and pushed (a4f2af1)

**Next up:**
- Trips tab RLS fix (trip_lists INSERT/UPDATE policies) still pending user confirmation in Supabase

---

## 2026-05-28 04:06 — monitoring stack live, all exporters up

**What we did:**
- Deployed Prometheus + Grafana monitoring stack to Atlas via scp + docker compose
- Fixed port conflicts: cAdvisor remapped to 8085 (8080 taken by Portainer), Grafana to 3001 (3000 taken by open-webui)
- Fixed Grafana datasource UID mismatch: dashboard JSONs referenced uid "prometheus" but Grafana assigned "PBFA97CFB590B2093" — patched dashboards and restarted
- Fixed Prometheus scrape targets: all exporters used localhost (unreachable from inside container) — changed to Docker service names (node-exporter:9100, smartctl-exporter:9633, cadvisor:8080, ollama-exporter:9642)
- All 6 monitoring containers healthy: Prometheus, Grafana, node-exporter, smartctl-exporter, cAdvisor, ollama-exporter
- All 4 exporters confirmed up=1 in Prometheus; dashboards populating with live data
- Saved all fixes back to homelab/docs/528/ and pushed to GitHub

**Where we stopped:**
- Stack live at http://100.71.165.80:3001 — both dashboards loading with real data
- Ephemeral volumes (data lost on container restart) — persistent volume migration pending

**Next up:**
- Convert to persistent Docker volumes to retain metric history across restarts
- Change Grafana admin password from default (atlas_admin)
- Watch SMART dashboard for sdh/sdi error trends on the WD Reds
- Future: email/Slack alerts, GPU metrics (K80), Plex/UPS stats

## 2026-05-28 03:24 — monitoring stack deployment guide for Atlas

**What we did:**
- Designed and built a complete Prometheus + Grafana monitoring stack for Atlas
- Created homelab/docs/528/ with 10 ready-to-deploy config files: docker-compose.yml, prometheus.yml, prometheus-scrape.yml, alert.rules.yml, grafana-datasource.yml, dashboards.yml, atlas-overview.json, atlas-storage.json, ollama-exporter.js
- Built 2 pre-built Grafana dashboards: Atlas Overview (CPU, RAM, load, Docker, Ollama) and Storage & SMART Health (SMART pass/fail, disk temps, UDMA CRC errors, I/O)
- Stack includes 6 exporters: node-exporter, cAdvisor, process-exporter, SMART disk health exporter (privileged), Ollama custom Node.js exporter
- Context: Atlas WD Reds showing concerning SMART data (sdh UDMA CRC errors, sdi reallocated sectors) — dashboards surface these in real-time
- Created deployment docs: QUICK_SUMMARY.md, COPY_PASTE_DEPLOY.md, MONITORING_DEPLOYMENT_GUIDE.md, DASHBOARD_PREVIEW.md, 00_START_HERE.txt
- Committed and pushed to homelab repo; infra submodule pointer updated

**Where we stopped:**
- All 10 config files and docs committed in homelab/docs/528/
- Stack not yet deployed on Atlas — user runs COPY_PASTE_DEPLOY.md steps (15–20 min)
- Ephemeral volumes for initial deploy; persistent volume migration is next session

**Next up:**
- SSH into Atlas, follow COPY_PASTE_DEPLOY.md to stand up the stack
- Verify both dashboards load at http://[tailscale-ip]:3000
- Next session: convert to persistent Docker volumes, change Grafana password
- Future: email/Slack alerts when thresholds breach, GPU metrics (K80), Plex/UPS stats

## 2026-05-26 12:27 — repo sync and uhaul delete button

**What we did:**
- Cleaned up CRLF/LF line-ending noise in golf, poker, daily-planner (git restore, no real changes)
- Committed and pushed answering-agent fix: removed erroneous "Rim Jobs" from A Couple Two Trees services prompt
- Merged uhaul-load-planner feature/delete-button-edit-modal → main and pushed (delete button in edit modal, v0.13.1)
- Confirmed Command Center and state.html already at v0.13.1 · 2026-05-26 (version bump was in the feature branch)
- Diagnosed 3D camera angle concern as pre-existing change (42c02e4) — not caused by merge; confirmed working on phone

**Where we stopped:**
- All repos clean and in sync with origin

**Next up:**
- No pending work

## 2026-05-26 12:01 — logoff only, no session work

**What we did:**
- No development work this session — ran /logoff immediately after session start
- Identified leftover uncommitted/unpushed state across repos from prior sessions

**Where we stopped:**
- Unpushed commits (ahead of origin): golf, poker, daily-planner, uhaul-load-planner (feature/delete-button-edit-modal)
- Uncommitted local changes: answering-agent (clients/a-couple-two-trees/prompt.txt)

**Next up:**
- Review and push pending changes in golf, poker, daily-planner
- Decide on uhaul-load-planner feature branch (merge or continue)
- Commit or discard answering-agent prompt.txt change

## 2026-05-26 09:16 — fix atlas wiki conflict after deploy

**What we did:**
- Fixed atlas wiki conflict: stashed local M wiki/docs/index.md on atlas, git pull succeeded
- Restored 18 project pages (git checkout -- wiki/docs/projects/) after erroneous gen_catalog.py run had zeroed them out
- Rebuilt wiki on atlas (gen_catalog.py --timestamp-only + mkdocs build) — http://atlas/wiki/ confirmed working

**Where we stopped:**
- Atlas wiki fully rebuilt; all 18 project pages restored and live

**Next up:**
- No pending work

## 2026-05-26 00:40 — 3D feedback fixes + wiki sync, v0.13.1

**What we did:**
- Identified post-v0.13.0 commits not captured in previous session log: PR #47 (wiki sync) and PR #48 (3D feedback fixes)
- PR #47: added wiki sync GitHub Action, docs/Home.md landing page for GitHub Wiki
- PR #48: 3D visual fixes — cab clipping into attic floor, troika text rendering crash, z-fighting on wheel wells/decals/grid, wheel offset corrections for all trucks, grid/camera/zoom polish; double-click to edit on 3D items added; MANUAL.md + README updated
- Bumped version to v0.13.1 · 2026-05-26 in Command Center card-meta, terminal scan line, and state.html

**Where we stopped:**
- Command Center and state.html updated to v0.13.1; untracked agent artifacts (.agentrules, tests/, json files) left uncommitted

**Next up:**
- Commit Command Center update and push
- Continue 3D roadmap (weight distribution view, stacking UI refinement)
- Phase 2 features from GitHub issues backlog

## 2026-05-25 11:41 — logoff: 3D scene launch, bump to v0.13.0

**What we did:**
- Captured 14 unlogged commits since v0.11.2
- Full Svelte 5 migration: 2D canvas and 3D scene both ported to Svelte components
- Implemented Threlte (Three.js/Svelte) 3D scene: truck model, item boxes, floating labels, orbit camera
- 3D drag-and-drop via raycasting plane, Svelte 5 prop-based pointer events
- 3D physical stacking: item list order determines vertical position
- CI: GitHub Actions workflow for Vite build + GitHub Pages deployment
- Layout UX: sidebar collapses on mobile, empty new layouts prompt truck selection
- Truck size persisted per layout and restored on load
- Fixed layout name overwriting, race conditions on creation, hardcoded truck dims, empty layouts loading as defaults
- Bumped to v0.13.0 · 2026-05-25 in Command Center card-meta, terminal scan line, and state.html
- Rewrote MANUAL.md to document Svelte + Threlte tech stack and 3D scene controls

**Where we stopped:**
- All clean: documentation, Command Center, and state.html at v0.13.0

**Next up:**
- Continue 3D roadmap (weight distribution view, stacking UI refinement)
- Phase 2 features from GitHub issues backlog

## 2026-05-25 09:52 — diagnose trips RLS write permission bugs

**What we did:**
- Investigated "archive list doesn't persist" and "create new list does nothing" in Trips tab
- Root cause: `trip_lists` table has RLS enabled but anon role lacks INSERT and UPDATE policies
- Same pattern as v0.9.3/v0.9.5 fixes (tasks, trip_items got write policies; trip_lists was missed)
- Provided SQL to add anon insert + update policies on `trip_lists` — no code changes needed

**Where we stopped:**
- Fix identified, SQL provided to user; not yet confirmed applied in Supabase

**Next up:**
- User runs the two-policy SQL in Supabase SQL editor to unblock trips create/archive

---

## 2026-05-24 22:36 — pushed vite migration, cleaned up branch

**What we did:**
- Deleted stale feat/vite-migration branch (local and confirmed remote didn't exist)
- Pushed 3 unpushed commits to origin/main: configure svelte plugin for vite, complete phase 1 features and fixes, add testing and 3d svelte libraries
- Bumped version to v0.11.2 in Command Center card, state.html, and terminal scan line
- Updated MANUAL.md to document phase 1 features (furniture presets, door fit check, weight/payload indicator) and Vite build instructions

**Where we stopped:**
- All clean: working tree empty, origin/main up to date at v0.11.2

**Next up:**
- Continue 3D roadmap (rendering layer, stacking logic)
- Phase 2 features from GitHub issues backlog

## 2026-05-24 20:40 — Vite migration merged, version bumped

**What we did:**
- Reviewed `feat/vite-migration` branch (1 commit ahead of main — Issue #31: monolithic index.html → Vite ES modules)
- Merged `feat/vite-migration` into `main` via fast-forward; pushed to origin
- Bumped version to v0.11.1 (patch: catches up missed v0.11.0 Command Center update + Vite refactor)
- Updated Command Center card-meta, terminal scan line, and state.html to v0.11.1 · 2026-05-24

**Where we stopped:**
- Version files updated; final commit + push pending (logoff step 7)

**Next up:**
- Continue 3D roadmap (rendering layer, stacking logic)
- Review MANUAL.md for Vite migration changes

## 2026-05-24 20:07 — confirm_slot, booking fallback, dashboard UI

**What we did:**
- Diagnosed voicemail not appearing: calendar booking failure caused early return with no draft; fixed to always continue to Claude and draft SMS even when booking fails (status → escalated)
- Added POST /retell/confirm-slot custom function — agent calls it mid-call when caller agrees to a slot, stores structured slot (start/end/tech_id/label) server-side by call_id; post-call webhook prefers this over text analysis field
- Fixed availability offering: when no preferred day given, now spreads one slot per calendar day instead of filling all 3 from the same day
- Added transcript accordion (collapsed by default) with pill label on main dashboard modal; structured summary always visible above it
- Matched all-leads expanded row to main modal: structured summary always visible, Transcript pill accordion below
- Fixed mobile header layout on both pages; transcript key-value grid stacks vertically on narrow screens
- Cleaned up Retell global prompt — removed Scheduling section (workflow handles it), removed duplicate closing line
- Updated MANUAL.md to reflect confirm_slot pipeline, workflow agent setup, custom functions, slot logic

**Where we stopped:**
- All changes merged and deployed on Atlas (v0.5.2)
- confirm_slot registered in Retell workflow but not yet end-to-end tested on a real call

**Next up:**
- Test a real call end-to-end: slot offered → caller agrees → confirm_slot fires → calendar booked
- A2P 10DLC carrier approval (outbound SMS still blocked)
- client_id multi-tenancy

## 2026-05-24 13:13 — uhaul 3D model + multi-truck features

**What we did:**
- Merged feat/3d-data-model branch (5 Codex commits) into main
- 3D-native data model foundation: migrateItem() backfills hIn, weightLbs, fragility, z, rotation on all items (load, default, new)
- Basic multi-truck support in 2D view
- Improved layout management UX
- Polish pass on multi-truck support before handoff
- Service worker: removed empty no-op fetch handler
- Bumped app to v0.10.0; updated Command Center card, terminal scan line, and state.html

**Where we stopped:**
- Branch merged to main, version bumped, housekeeping committed
- No open items in this feature set

**Next up:**
- Continue 3D roadmap (rendering layer, stacking logic)
- Multi-truck UX polish as needed

## 2026-05-24 12:42 — calendar booking fix + booked pill UI

**What we did:**
- Fixed 400 Bad Request from Google Calendar freeBusy/event insert: naive confirmed-slot datetimes now localized to BUSINESS_TZ before API calls
- Added Booked pill to dashboard cards (index.html + all.html): glowing green pill with appointment tooltip when confirmed_slot is set
- Merged fix/confirmed-slot-calendar-booking to main; auto-deploy landed on Atlas at v0.5.1
- Verified end-to-end: fake Retell webhook with open slot → freeBusy check passes → Calendar event created → confirmed_slot persisted → lead drafted
- Updated MANUAL.md: noted Booked pill, removed resolved pending item

**Where we stopped:**
- All changes merged, deployed, and verified on Atlas (v0.5.1)
- No uncommitted changes

**Next up:**
- A2P 10DLC carrier approval (outbound SMS still blocked)
- client_id multi-tenancy (orchestrator hardcoded to a-couple-two-trees)
- Push Codex commits (user has pending work)

## 2026-05-24 07:35 — Fix: Retell call_analyzed gate (verified live)

**What we did:**
- Fixed empty-lead bug: /retell/post-call now only processes the call_analyzed event (call_started/call_ended lack transcript + custom_analysis_data, and dedup was dropping the analyzed event) — v0.5.1, deployed to atlas
- Verified a live VM call end to end: lead captured name "Johnny", intent new_job, confirmed_slot "Tuesday June 2 at 11 AM", draft SMS pinned to that time
- Confirmed Supabase confirmed_slot column exists; Retell get_availability function + confirmed_slot analysis field are registered and firing

**Where we stopped:**
- Full pipeline verified on the live VM: live calendar offer → caller agrees → call_analyzed → captured → draft pinned + saved to Supabase
- Old empty lead 98de750d (from the pre-fix call) can be trashed in the dashboard

**Next up:**
- Revisit multi-tenant calendar auth (issue #24) when adding more technicians/clients
- Optional cleanup: root kb.yaml is unused on the VM (.env points to clients/ KB), so the repo's pending root-kb.yaml deletion is safe to commit

## 2026-05-24 07:03 — Live calendar availability + confirmed slot

**What we did:**
- Added POST /retell/get-availability so the Retell agent can pull real open slots mid-call (offer-only); returns spoken phrase + structured slots
- Wired real Google Calendar free/busy into compute_candidate_slots() (was mocked): honors business hours, buffer, lead time, busy blocks in America/New_York
- Fixed service-account creds to request calendar.readonly scope; fixed drew's google_cal_id typo (drew.befree → drewbefree)
- Added OAuth fallback to calendar creds (service account if present, else calendar_token.json) — single-owner runs on OAuth, SA deferred to multi-tenant
- Verified live against the real calendar end-to-end on atlas (v0.5.0): VM reflects real busy times (Monday OOO/league correctly skipped)
- Removed placeholder tech billy from prefer_tech_order (fake calendar would mask real conflicts)
- Wired confirmed_slot: /retell/post-call reads it, Claude pins the draft SMS to the agreed time, persisted to leads.confirmed_slot (guarded write)
- Deployed to atlas; copied calendar_token.json to the VM, repointed VM .env KB_PATH to clients/ KB
- Filed GitHub issue #24 (multi-tenant calendar auth) and added it to the Answering Agent project board

**Where we stopped:**
- Calendar availability live on the VM via OAuth; confirmed_slot code deployed (v0.5.0)
- Pending manual steps: run `alter table leads add column confirmed_slot text;` in Supabase; register Retell custom function get_availability + post-call analysis field confirmed_slot

**Next up:**
- Register the Retell get_availability custom function + confirmed_slot analysis field so offer → capture → draft flows end to end
- Add the Supabase confirmed_slot column
- Revisit multi-tenant calendar auth (issue #24) when adding more technicians/clients
- Optional: root kb.yaml is now unused on the VM, so the repo's pending root-kb.yaml deletion is safe to commit

## 2026-05-24 05:25 — U-Haul product roadmap + GitHub backlog

**What we did:**
- Wrote docs/PRODUCT_ROADMAP.md — U-Haul acquisition pitch + phased roadmap (3D-native data model, 2D top-down as first render mode) + Appendix A with web-verified truck specs (cargo van → 26')
- Wrote docs/TASKS.md — 30-issue breakdown across 5 milestones
- Created 10 labels, 5 milestones, 30 GitHub issues (#1–30 aligned to TASKS.md)
- Created GitHub Projects board #5 "U-Haul Load Planner Roadmap" with all 30 issues
- Committed docs on feat/product-roadmap-tasks, merged to main (ff), pushed, deleted branch
- Resolved gh auth (missing project scope); user regenerated a minimal-scope PAT after a token leak + device-flow rate limits

**Where we stopped:**
- All complete on main; board live with 30 items; auth locked to project/read:org/repo/workflow
- Pre-existing uncommitted WIP (CNAME, README, index.html, manifest.json, sw.js) left untouched

**Next up:**
- Issue #1 — refactor to 3D-native data model (foundation)
- Research issues #27–30 (trailer/U-Box specs, furniture preset data, supply→SKU mapping, U-Haul app architecture)

## 2026-05-24 03:56 — Dashboard UI polish + dark theme

**What we did:**
- Formatted transcript in modal: structured summary grid + styled Agent/Caller conversation turns
- Card snippets now show extracted data (service · urgency · address) instead of raw transcript
- Reverted to dark slate theme (#1a2236 background) on both index.html and all.html
- Replaced Remove button with SVG trash icon positioned in card footer
- Added confirmation modal before removing any lead (Cancel / Remove)
- Applied same dark theme + confirm modal to all.html
- Bumped app version to 0.4.0

**Where we stopped:**
- Dashboard polished and deployed; full Retell pipeline still live
- A2P 10DLC approval still pending
- Google Calendar slots still mocked

**Next up:**
- Wire real Google Calendar free/busy into compute_candidate_slots()
- client_id multi-tenancy (orchestrator hardcoded to a-couple-two-trees)
- Connect ElevenLabs to Retell for Grandma Rachel voice

## 2026-05-24 03:27 — Retell AI integration + client KB structure

**What we did:**
- Integrated Retell AI as the live voice agent (replaces Twilio passive voicemail)
- Added POST /retell/post-call webhook endpoint — receives Retell's post-call payload, short-circuits on out-of-area or no-appointment calls, hands off to orchestrator
- Added call_id dedup to prevent double processing when Retell fires multiple webhook events
- Built generate_prompt.py — generates Retell global prompt from kb.yaml (knowledge only, no collection logic)
- Reorganized KB into clients/a-couple-two-trees/ folder structure for multi-client support
- Generated ElevenLabs Grandma Rachel voicemail greeting (old-lady-vm2.mp3), served at api.kybernet.tech
- Bumped app version to 0.3.0
- Closed GitHub issues #11, #14, #15, #16, #19, #20, #21
- Rewrote MANUAL.md to reflect Retell pipeline

**Where we stopped:**
- Full pipeline working end-to-end: Twilio → Retell AI conversation → webhook → Claude → Supabase → dashboard
- A2P 10DLC approval still pending on Twilio
- Google Calendar slots still mocked

**Next up:**
- Wire real Google Calendar free/busy into compute_candidate_slots()
- client_id multi-tenancy (orchestrator hardcoded to a-couple-two-trees)
- Connect ElevenLabs to Retell for Grandma Rachel voice in the agent

## 2026-05-23 20:17 — SMS compliance + wiki pipeline update + logoff automation

**What we did:**
- Added SMS opt-in checkbox and full consent disclosure to kybernet-tech contact form
- Added validation: phone number requires SMS consent checkbox before submit
- Pushed kybernet-tech (A2P 10DLC compliance gap closed)
- Updated wiki agents.md — answering agent section rewritten for Twilio pipeline
- Discovered MANUAL.md in each repo is the source gen_catalog.py pulls into wiki project pages
- Rewrote MANUAL.md in answering-agent repo to reflect current Twilio pipeline
- Added git-revision-date-localized plugin to mkdocs.yml (last-updated timestamp on every wiki page)
- Installed plugin on atlas venv, added to wiki requirements.txt
- Deployed wiki successfully — answering-agent page now current
- Added step 8 (update MANUAL.md) and step 9 (deploy wiki) to /logoff skill
- Updated CLAUDE.md via claude-config with same steps, pushed to claude-config repo

**Where we stopped:**
- All repos committed and pushed
- Wiki live and current at http://atlas/wiki/
- A2P 10DLC carrier approval still pending on Twilio

**Next up:**
- Once A2P approved, test outbound SMS end-to-end with a real number
- Stop/disable answering-poller on atlas (gmail poller, now deprecated)
- Wire real Google Calendar free/busy into compute_candidate_slots()

## 2026-05-23 19:02 — Twilio pipeline + dashboard + auto-deploy

**What we did:**
- Replaced Gmail/Google Voice ingestion with Twilio end-to-end (inbound voice, recording, transcription)
- Built /twilio/voice, /twilio/recording, /twilio/transcription, /send endpoints in app.py
- Fixed caller number: Twilio includes From in transcription callback — no API lookup needed
- Added caller_name extraction from Claude agent output, written back to Supabase
- Redesigned dashboard to 4-column status board (New/Drafted/Sent/Escalated), each showing 3 most recent cards
- Added modal on card click with full voicemail, draft reply, slots, and action buttons
- Added Remove button on all leads (index.html and all.html)
- Added CORS middleware (answer.kybernet.tech → api.kybernet.tech)
- Set up GitHub Actions auto-deploy: push to main triggers /webhook/deploy → git pull + systemctl restart
- Added STARTED_AT and updated /health endpoint (version + started_at)
- Added "last updated" deploy-info header to index.html and all.html (fetches /health on load)

**Where we stopped:**
- Last updated indicator committed and pushed (bdc6aa1)
- A2P 10DLC approval still pending on Twilio — outbound SMS to real customers blocked until approved
- Gmail poller (answering-poller systemd service) should be stopped/disabled on atlas

**Next up:**
- Verify auto-deploy fires on next push
- Stop/disable answering-poller on atlas: systemctl --user stop answering-poller && systemctl --user disable answering-poller
- Add Cloudflare CNAME: answer → drewbefree.github.io (DNS only) if not already done
- Once A2P approved, test outbound SMS to a real customer number

## 2026-05-22 21:50 — Cloudflare tunnel + Twilio outbound SMS

**What we did:**
- Installed cloudflared on atlas, created Tunnel for api.kybernet.tech (issue #9 ✓)
- Added /twilio/voice and /twilio/recording endpoints for inbound calls (issue #10)
- Added /send endpoint for outbound SMS via Twilio (issue #11 ✓)
- Updated dashboard UI: Send button now calls /send instead of copying to clipboard
- Served static dashboard from FastAPI at api.kybernet.tech
- Tested Gmail poller: working end-to-end (voicemail → Claude draft → Supabase)
- Confirmed Twilio credentials in .env, basic webhook structure in place

**Where we stopped:**
- Issue #11 (outbound SMS) complete and deployed
- Issue #10 (Twilio inbound) closed/backlogged — transcription config too complex
- Gmail poller confirmed working as primary ingestion
- Dashboard live at https://api.kybernet.tech
- User wants unified Twilio number with transcription next

**Next up:**
- Issue #10 revisited: simplify Twilio inbound transcription (fetch via API instead of webhook)
- Issue #2: wire Google Calendar free/busy into slot computation

## 2026-05-22 19:05 — kybernet-tech privacy/terms pages + footer fix

**What we did:**
- Created privacy.html and terms.html for Twilio A2P campaign registration
- Both pages match the site's design (same fonts, colors, nav, footer)
- Privacy policy covers SMS opt-in/out, data collection, sharing, and retention
- Terms covers SMS messaging terms, scheduling links, liability, and governing law
- Added Privacy Policy and Terms of Service links to the footer of index.html
- Fixed root cause bug: global `nav { position: fixed }` CSS was pulling the footer `<nav>` out of the footer and rendering it at the top of the page — fixed by changing footer nav to a `<div>`
- Fixed secondary CSS bug: `flex-wrap: gap` was invalid, changed to `flex-wrap: wrap; gap: 16px`
- All changes committed and pushed to main

**Where we stopped:**
- Live site deployed successfully (GitHub Pages build confirmed via gh CLI)
- CDN cache propagation may still be in progress for some users

**Next up:**
- Verify footer links are visible on live site after CDN propagates
- Twilio A2P submission is already in — await carrier approval

## 2026-05-22 02:40 — Add Agents & Skills wiki section

**What we did:**
- Created `wiki/docs/agents-and-skills/` with three pages: index.md, agents.md, skills.md
- index.md: differentiator table (agents vs skills) + quick reference for all agents and skills
- agents.md: detailed entries for Bob, Answering Agent, Recap Agents, Interactive Setup — pipelines, design choices, project links
- skills.md: detailed entries for /log-session, /logoff, /update-atlas — step-by-step breakdowns and when-to-use
- Added "Agents & Skills" section to mkdocs.yml nav and wiki home page
- Deployed via ./wiki/deploy.sh; built in 1.02s

**Where we stopped:**
- Wiki live at http://atlas/wiki/ with new Agents & Skills section; no open items

**Next up:**
- Make all URLs clickable in wiki
- Upgrade wiki UI

## 2026-05-22 02:32 — Bob session log backfill

**What we did:**
- Noticed bob SESSION_LOG.md hadn't been updated after dev→main merge and MANUAL.md addition
- Backfilled bob/SESSION_LOG.md with the 2026-05-22 01:59 entry covering those changes
- Pushed bob repo to origin/main

**Where we stopped:**
- Bob fully deployed on Atlas; repo up to date on main; session logs accurate

**Next up:**
- Consider conversation history / multi-turn context in bot.py
- Optionally re-enable Alienware OpenClaw for non-Slack use cases

## 2026-05-22 02:29 — Alienware specs added to wiki machines page

**What we did:**
- Updated `wiki/docs/infrastructure/machines.md` with detailed Alienware hardware specs from Speccy report
- Added CPU (i9-14900F, 24c/32t), RAM (32 GB DDR5-5600), GPU (RTX 4070 Ti SUPER 16 GB), display (5120×1440 Odyssey G95C), storage, networking, peripherals, and services tables
- Committed to feat branch, merged to main, deployed via `./wiki/deploy.sh`
- Wiki rebuilt on atlas in 0.58s

**Where we stopped:**
- Wiki live at http://atlas/wiki/ with updated machines page; no open items

**Next up:**
- Make all URLs clickable in wiki
- Upgrade wiki UI

## 2026-05-21 20:46 — Atlas OpenClaw to custom Bob Slack bot

**What we did:**
- Diagnosed duplicate Ollama runtimes on Atlas (Docker + systemd conflict); killed stuck runner with `docker restart ollama`
- Confirmed local llama3.2:3b and 1b both too slow for OpenClaw's 6800-token system prompt on CPU
- Pulled llama3.2:1b to Atlas Docker Ollama
- Built lightweight Python Slack bot (bob) using Slack Bolt + Ollama /api/chat directly — tiny system prompt, fast responses
- Deployed as `bob.service` systemd user service on Atlas
- Diagnosed competing socket mode conflict: Alienware's OpenClaw (Windows scheduled task, pid 18004) was intercepting all Slack events
- Stopped Alienware OpenClaw (gateway stop + taskkill)
- Fixed `app_mention` event handler so @mentions in channels work alongside DMs
- Added dynamic date injection to system prompt to fix hallucinated dates
- Created `github.com/DrewBeFree/bob` repo with bot.py, requirements.txt, bob.service

**Where we stopped:**
- Bob is live on Atlas, responding to DMs and @mentions using llama3.2:1b
- Alienware OpenClaw disabled (service stopped, process killed)
- Bob repo exists on dev branch — not yet merged to main

**Next up:**
- Merge bob dev → main
- Consider conversation history / multi-turn context in bot.py
- Optionally re-enable Alienware OpenClaw for other use cases (non-Slack)

## 2026-05-20 22:29 — Twilio path C backlog + Slack notification

**What we did:**
- Added Slack notification to orchestrator (fires after draft created, uses Bob webhook)
- Deployed notification to atlas via rsync + systemd restart
- Decided to replace Google Voice + Gmail poller with Twilio end-to-end (Path C)
- Opened GitHub Issues #9 (Cloudflare Tunnel), #10 (Twilio inbound TwiML), #11 (Twilio outbound click-to-send), all assigned to 0.2.0 milestone
- User signed up for Twilio, has live credentials (SID + Auth Token), chose a Twilio number over porting GV

**Where we stopped:**
- Issue #1 (Slack notifications) shipped
- Twilio credentials in hand, no number purchased yet
- Issues #9–11 written and ready for next session

**Next up:**
- #9: Install cloudflared on atlas, create tunnel for api.kybernet.tech
- #10: Add /twilio/voice and /twilio/recording endpoints to app.py
- #11: Add /send endpoint + update UI Send button to call it
- User to buy a Twilio number before next session

## 2026-05-20 20:42 — answering-agent ingestion pipeline + deploy

**What we did:**
- Wrote gmail_poller.py: polls Gmail every 60s for GV voicemail emails, parses caller number/name and transcript, calls process_voicemail() directly
- Fixed orchestrator validate_agent_output: handle None draft_sms gracefully
- Fixed process_email: mark_read in finally block so it always fires on error
- Updated Gmail query to in:anywhere (GV emails were landing in Trash due to a filter)
- Fixed caller name parsing: handles "New voicemail from Bob Smith" format (contact name) in addition to phone number format
- Deployed answering-poller as user systemd service on atlas (100.71.165.80) with linger enabled — always-on
- Moved ui/ to docs/ for GitHub Pages; added CNAME for answer.kybernet.tech
- Enabled GitHub Pages on private repo (GitHub Pro); UI is live at answer.kybernet.tech
- Opened GitHub Issues #1–7 with semantic version milestones (0.2.0, 0.3.0, 1.0.0)
- Added Slack notification (Bob webhook) when a draft is ready — fires after draft written to Supabase
- Tested full end-to-end: real voicemail from friend → Gmail → atlas poller → Claude → Supabase → UI → Slack notification

**Where we stopped:**
- Issue #1 (Slack notifications) complete and deployed
- Issue #2 (Google Calendar real free/busy) is next in 0.2.0 milestone
- Atlas deploy is still rsync-based (Issue #3 auto-deploy not done yet)

**Next up:**
- #2: Wire real Google Calendar free/busy into compute_candidate_slots()
- #3: Auto-deploy on atlas (git clone + webhook or cron pull)
- #4: 72h no-response escalation cron

## 2026-05-20 05:13 — Centralize Claude Code config in claude-config repo

**What we did:**
- Fixed Mac statusline rendering ANSI codes as literal text (switched to bash + `$'...'` syntax)
- Added 5h/7d rate limit usage to statusline via `rate_limits.*.used_percentage`
- Audited Claude config across Mac, Alienware Windows, Alienware WSL, and atlas — only Alienware Windows and atlas had full setups
- Created `claude-config` private GitHub repo as single source of truth: shared CLAUDE.md, statusline, skills (logoff, log-session, update-atlas), commands (kybernet-prep, recap-agents), per-machine settings under machines/{mac,alienware-windows,alienware-wsl,atlas}
- Deployed via setup.sh (Mac/WSL/atlas) and setup.ps1 (Windows) — all four use symlinks (Developer Mode on Windows)
- Added SessionStart hook to all four machine configs to auto-pull on session start

**Where we stopped:**
- All four environments running off the repo, auto-pulling on startup
- No open items

**Next up:**
- No pending work

## 2026-05-20 01:19 — Fix atlas dashboard deploy + session accordion

**What we did:**
- Diagnosed /update-atlas failure: deploy.sh was pointing to /opt/homelab-status-dashboard which wasn't a git repo; infra repo lives at ~/infra on atlas
- Fixed deploy.sh to git pull from ~/infra, then rsync files to /opt/homelab-status-dashboard (where nginx serves from)
- Diagnosed session accordion not showing older entries: browser had cached old data.js which returned `fallback` (single session) instead of `previous` (array)
- Traced the root cause: nginx config was never actually updated (sed command didn't save), so /opt was still being served
- Restored config.js to /opt after rsync wiped it; added explicit cp to deploy.sh so config.js is always preserved
- Committed and pushed all deploy.sh fixes to infra main

**Where we stopped:**
- Dashboard accordion now working; deploy pipeline fully functional
- deploy.sh: git pull → rsync → cp config.js

**Next up:**
- Verify /update-atlas end-to-end in next session
- Consider using sudo to point nginx root directly at ~/infra/homelab-status-dashboard to eliminate the rsync step

---

## 2026-05-20 00:43 — WSL statusLine fix + log-session skill

**What we did:**
- Diagnosed why `/statusline` kept saying "not set up" — the statusline-setup skill checks `.zshrc` for PS1 and always gives a false negative; the real setup is a standalone bash script
- Root cause: WSL uses `/home/drew/.claude/settings.json` (was missing `statusLine`); PowerShell uses `/mnt/c/Users/drewb/.claude/settings.json` (had it)
- Fixed WSL statusLine by adding the config to `/home/drew/.claude/settings.json`
- Saved memory so we never run statusline-setup again for this
- Designed and built `/log-session` skill: auto-generates session entry, pushes to infra `SESSION_LOG.md` (atlas dashboard), memory log, and current project log
- Updated `/logoff` skill to call `/log-session` as its final logging step
- Updated `CLAUDE.md` logoff checklist to match (steps 6 & 7 collapsed into one)
- Pushed infra repo (spec, plan, this entry)

**Where we stopped:**
- `/log-session` skill is live but requires a new Claude Code session to be discoverable

**Next up:**
- Open a new session and run `/log-session` to confirm it shows up on atlas

---

## 2026-05-19 — Dashboard redesign + deploy to atlas

**What we did:**
- Verified dashboard was not deployed to atlas; fixed WSL SSH using Windows key
- Merged infra dev → main and pushed to GitHub
- Cloned infra repo on atlas; confirmed nginx already configured at /opt/homelab-status-dashboard
- Redesigned dashboard with Pro Blue theme: Space Grotesk font, navy header, blue→purple→cyan gradient divider, white cards on light blue-gray bg
- Added live indicator: pulsing dot (amber=fetching, green=live, red=error)
- Added session timestamp support (YYYY-MM-DD HH:MM format) with same-day session stacking
- Grouped backlog by type: Infrastructure / Apps / Sites / Agents
- Added +N remaining badge to Up Next; infra sorted to top
- Added hosting machine indicator (⬡ atlas) in header eyebrow
- Added XSS-safe esc() helper in render.js

**Where we stopped:**
- Mobile browser may need hard refresh to pick up sort order change
- `http://atlas` shortname not resolving on Windows (hosts file fix pending)

**Next up:**
- Verify mobile shows infra first after hard refresh
- Add `100.71.165.80 atlas` to Windows hosts file for shortname access
- Use `## YYYY-MM-DD HH:MM — context` format for all future session log entries

---

## 2026-05-19 — homelab-status-dashboard build + housekeeping

**What we did:**
- Designed and built homelab-status-dashboard (data.js, render.js, index.html) inside infra repo
- Wrote design spec and implementation plan to docs/superpowers/
- Fixed UTF-8 decode bug and session log date parsing in data.js
- Redesigned dashboard with Command Center-inspired dark aesthetic (single index.html)
- Partially deployed to atlas — data loads, backlog accordion not expanding yet
- Moved interactive-setup/ from infra/ to agents/interactive-setup/, inited as own git repo
- Added interactive-setup to repos.json
- Added 4 new backlog items (unified terminal, dashboard redesign, clone strategy, Docker strategy)

**Where we stopped:**
- infra dev branch not yet merged to main or pushed
- interactive-setup not yet pushed to GitHub
- Dashboard backlog accordion expand/collapse still broken
- Dashboard redesign not fully verified on atlas

**Next up:**
- Fix backlog accordion expand/collapse
- Verify redesigned index.html on atlas
- Merge infra dev → main and push
- Create interactive-setup GitHub repo and push
- Tackle unified terminal / cross-machine access

---

## 2026-05-18

**What we did:**
- Created STRUCTURE.md with directory standards and naming conventions
- Created repos.json manifest (14 cloneable repos)
- Created clone-all.ps1 and clone-all.sh scripts for multi-system setup
- Reorganized: extracted ai-dog-trainer from DrewBeFree, converted DrewBeFree to profile-only
- Created BACKLOG.md for persistent infrastructure task tracking
- Built update-session-logs wrapper scripts (PowerShell & Bash) for multi-repo SESSION_LOG updates
- Updated scripts to read baseDirectory from repos.json for cross-system compatibility

**Where we stopped:**
- Wrapper scripts tested and committed, ready for WSL setup

**Next up:**
- Set up WSL development environment, test scripts in bash, then proceed to Task 2 (project templates)

# Session Log

## 2026-05-18 â€” Repository reorganization: Extract ai-dog-trainer from DrewBeFree

**What we did:**
- Created new `ai-dog-trainer` repository under `apps/`
- Extracted dog trainer code from DrewBeFree: app.py, requirements.txt, static/, etc.
- Initialized git repo locally and pushed to GitHub
- Converted DrewBeFree to profile-only repository (GitHub profile README)
- Updated `repos.json` to add ai-dog-trainer and remove DrewBeFree from cloning manifest
- Result: cleaner organization with ai-dog-trainer as standalone app

**Where we stopped:**
- Repository reorganization complete
- All repos committed and pushed
- repos.json updated with new structure

**Next up:**
- Task 1 still in progress: update SESSION_LOG and close out

---

## 2026-05-18 â€” Task 1: Audit & document directory structure + naming conventions

**What we did:**
- Scanned entire GitHub directory structure across all 7 categories (apps/, sites/, agents/, infra/, notes/, DrewBeFree/, _worktrees/)
- Analyzed project patterns: 9 web apps, 3 sites, 1 agent, infra, backend
- Documented directory structure templates for 4 project types (PWA, static site, Python, Docker)
- Identified naming conventions: kebab-case projects, lowercase standard dirs, git branch patterns (main/dev/feat/fix/claude)
- Created `STRUCTURE.md` â€” comprehensive reference documenting all standards, templates, and documentation requirements
- Created `repos.json` â€” manifest listing all 15 repositories with GitHub URLs and target directories
- Created `clone-all.ps1` â€” PowerShell script to clone entire structure on Windows
- Created `clone-all.sh` â€” Bash script to clone entire structure on Linux/macOS

**Where we stopped:**
- Task 1 complete and all deliverables committed
- Multi-machine setup now supported: any machine can run clone script to replicate folder structure

**Next up:**
- Task 2: Create project templates for apps and sites (blocked by Task 1 âœ… now unblocked)

---

## 2026-05-18 â€” Infrastructure repo creation and backlog setup

**What we did:**
- Created new `infra` GitHub repository (separate from `homelab`)
- Moved broad infrastructure docs from homelab to infra root:
  - `infrastructure-tools.md` â€” tools reference for Alienware + PowerEdge
  - `alienware-vs-poweredge.md` â€” workload split decision rule
- Created `INFRASTRUCTURE.md` â€” strategic backlog and task list
- Established priority order for infrastructure work:
  1. Directory structure + naming conventions
  2. Project templates
  3. Multi-system sync strategy (deadline: 2026-06-02)
  4. Automation of recurring tasks

**Where we stopped:**
- Infra repo initialized and pushed to GitHub
- Infrastructure backlog documented and prioritized
- Task list created (internal tracking)

**Next up:**
- Task #1: Audit and document directory structure + naming conventions
- Define directory hierarchy standards
- Establish file naming conventions
- Document project organization strategy


## 2026-05-30 - Internal ecosystem portal design handoff

**What we did:**
- Decided the internal projects page should be an Atlas/Tailscale-only ecosystem portal rather than another public Command Center-style page.
- Settled on a single source of truth above the repos, wiki, Command Center, homelab, dashboards, agents, and sites.
- Chose visibility levels: `public`, `private`, and `sensitive`, with UHaul Planner moved behind a Sensitive / IP filter and removed from public Command Center until IP direction is clear.
- Agreed the portal should become a comprehensive launcher plus status/control surface, starting with launcher/status-ready foundations.

**Where we stopped:**
- No implementation started yet; we intentionally kept this as design context for a fresh implementation thread.
- Recommended placement: canonical registry in `infra/ecosystem.json`; internal portal UI/deploy assets under `infra/internal-portal`, served privately from Atlas/Tailscale.

**Next up:**
- In a fresh desktop Codex session rooted at `C:\Users\drewb\Documents\GitHub\infra`, design and implement the internal ecosystem portal around the canonical registry.
- Include UHaul Planner public visibility cleanup in the implementation plan.

## 2026-05-30 - Track lead-gen-agent as a project

**What we did:**
- Added `lead-gen-agent` to `infra/repos.json` so clone/update tooling treats it as an agent repo.
- Added `lead-gen-agent` to `ecosystem.json` and the internal portal registry contract.
- Added an Atlas wiki project page and linked it from the project and agent catalogs.
- Confirmed `DrewBeFree/lead-gen-agent` now has `main` as its GitHub default branch.
- Merged infra PR #4 and deployed the updated Atlas wiki plus internal portal registry.

**Where we stopped:**
- `infra/main` includes the lead-gen-agent project tracking docs.
- Atlas wiki verifies `http://atlas/wiki/projects/lead-gen-agent/`.
- Atlas internal portal registry verifies `lead-gen-agent` in `http://atlas/ecosystem/ecosystem.json`.

**Next up:**
- Continue lead-gen implementation from `DrewBeFree/lead-gen-agent`.

## 2026-05-30 03:05 EDT - Build internal ecosystem portal

**What we did:**
- Created `feat/internal-ecosystem-portal` in `infra` and built the canonical `ecosystem.json` registry with repos, services, dashboards, docs, deploy targets, GitHub links, local paths, live URLs, visibility levels, and status/control metadata.
- Added the Atlas/Tailscale-only static portal under `internal-portal/`, including search, visibility/category filters, launcher links, service/dashboard sections, docs links, and control-ready action buttons.
- Marked UHaul Planner as `sensitive`, added the Sensitive / IP filter requirement, and removed it from the public Command Center on its own matching branch.
- Added a Node contract test suite for the registry, portal, UHaul sensitivity, and public Command Center cleanup; verified the portal in the in-app browser.

**Where we stopped:**
- Infra branch `feat/internal-ecosystem-portal` has new uncommitted portal/registry files plus pre-existing uncommitted `SESSION_LOG.md` and `wiki/docs/index.md` changes that were already present at session start.
- Command Center branch `feat/internal-ecosystem-portal` has the UHaul public card and scan-line entry removed.

**Next up:**
- Review and commit/push the infra and Command Center branches.
- Deploy `internal-portal/` plus `ecosystem.json` to Atlas and wire nginx at `http://atlas/ecosystem/`.
- Implement the actual UHaul edge/IP restriction before exposing it anywhere public again.

## 2026-05-30 03:05 EDT - Polish portal preview and link behavior

**What we did:**
- Reworked the internal portal UI into a darker, sleeker operator-console style.
- Fixed local-preview link behavior so Atlas wiki/docs links resolve to local markdown files while previewing from `127.0.0.1`.
- Changed status/control buttons from disabled placeholders into a details drawer that shows the intended command, docs, links, and deploy targets.
- Added a Node-based `internal-portal/dev-server.mjs` preview server and started it live at `http://127.0.0.1:8765/internal-portal/`.

**Where we stopped:**
- The local preview server is running as Node process `15280`.
- HTTP checks for the portal, `ecosystem.json`, and a local wiki project doc all returned `200`.
- Browser automation transport dropped during the visual refresh, but the in-app browser is already pointed at the live preview URL and can be refreshed manually.

**Next up:**
- Visually review the redesigned portal in the in-app browser.
- Commit/push both feature branches when the look and behavior feel right.
- Deploy the same assets to Atlas under `http://atlas/ecosystem/`.

## 2026-05-30 03:05 EDT - Commit, push, and deploy ecosystem portal

**What we did:**
- Fast-forward merged `feat/internal-ecosystem-portal` into `main` for both `infra` and `drewbefree-command-center`.
- Pushed `main` for both repos to GitHub.
- Pulled `infra` on Atlas and deployed the internal portal under the existing nginx root at `/opt/homelab-status-dashboard/ecosystem/`.
- Verified `http://atlas/ecosystem/` and `http://atlas/ecosystem/ecosystem.json` both return `200`; verified deployed JSON schema is `drewbefree.ecosystem.v1`.
- Updated deploy docs and registry metadata to use the live sudo-free Atlas path.

**Where we stopped:**
- The portal is live on Atlas at `http://atlas/ecosystem/`.
- UHaul Planner is removed from public Command Center and tracked as sensitive in the portal registry.
- The actual UHaul IP/edge restriction is still future work.

**Next up:**
- Review the live Atlas portal from Tailscale.
- Open/seed GitHub Project issues for the remaining portal control hooks, UHaul restriction, and possible future Leantime evaluation.

## 2026-05-30 03:05 EDT - Add ecosystem tracking backlog item

**What we did:**
- Added a dedicated `BACKLOG.md` item for standardizing GitHub Projects + Issues across the ecosystem.
- Captured the canonical board decision, fields, labels, known unfinished portal/UHaul work, and future sync between `BACKLOG.md`, session logs, GitHub Issues, and the internal portal.

**Where we stopped:**
- The backlog now has a ready item named `Ecosystem project tracking — standardize GitHub Projects + Issues`.

**Next up:**
- Inventory existing GitHub Projects, choose the canonical ecosystem board, then seed issues for the known unfinished work.

## 2026-05-30 03:11 EDT - Logoff checkpoint after ecosystem portal deploy

**What we did:**
- Confirmed `infra/main` and `drewbefree-command-center/main` are pushed after the ecosystem portal work.
- Confirmed the internal portal is deployed on Atlas at `http://atlas/ecosystem/`.
- Corrected the ecosystem session-log headings to include timestamps.

**Where we stopped:**
- `drewbefree-command-center` is clean on `main`.
- `infra` is on `main` with only the pre-existing `wiki/docs/index.md` timestamp edit still uncommitted.
- Local preview on `127.0.0.1:8765` is no longer needed because Atlas is live.

**Next up:**
- Start a fresh session for GitHub Projects/Issues cleanup, Leantime evaluation planning, or UHaul IP/edge restriction work.

## 2026-05-30 — LLM Debate Union Atlas deployment plan

**What we did:**
- Added infra wiki workflow plan for deploying LLM Debate Union on Atlas with PocketBase, a cloud LLM gateway, and a Postgres + pgvector memory-vault path.
- Linked the workflow from the LLM Debate Union project wiki page.
- Created branch `feat/llm-debate-union-atlas-pocketbase-plan` for infra wiki changes.
- Verified Atlas identity and service context: Dell PowerEdge R720, Ubuntu 24.04, Tailscale `100.71.165.80`.

**Where we stopped:**
- Infra wiki changes are local on the feature branch and not committed yet.
- Postgres + pgvector installation on Atlas is blocked by sudo/Docker permissions.

**Next up:**
- Commit/push the infra wiki plan after final review.
- Add service documentation under homelab/infra once Postgres and the LLM gateway are live.

## 2026-05-30 17:32:00 -04:00 - Atlas Postgres pgvector memory vault

**What we did:**
- Verified Atlas Docker/Compose, PocketBase, native Postgres, and sudo state from the LLM Debate Union workspace.
- Confirmed Docker Compose is available and existing Atlas containers are healthy; native Postgres was not installed.
- Confirmed `sudo -n` still requires a password for `drew`, so provisioned Postgres through Docker without sudo.
- Created `/home/drew/services/postgres-memory-vault` with `pgvector/pgvector:pg16`, database `ai_memory`, local-only bind `127.0.0.1:5432`, and restart policy `unless-stopped`.
- Verified `vector` extension, `chat_threads`, `chat_messages`, `chat_embeddings`, a rollback smoke insert, and container health after restart.

**Where we stopped:**
- Atlas now runs `postgres-memory-vault` as the long-term AI memory/search database alongside PocketBase.
- The secret `.env` lives only on Atlas at `/home/drew/services/postgres-memory-vault/.env` with `600` permissions.

**Next up:**
- Document the repeatable schema in the app repo `memory-db/` task.
- Wire future gateway/ingestion workers to `postgres://ai_memory:<secret>@127.0.0.1:5432/ai_memory` from Atlas-local services only.

## 2026-05-30 18:18:00 -04:00 - Merge LLM Debate Union Atlas infra branch

**What we did:**
- Committed the Atlas memory vault service session-log update on `feat/llm-debate-union-atlas-pocketbase-plan`.
- Pushed the feature branch, fast-forward merged it into `main`, and pushed `infra/main` to GitHub.
- Confirmed the related app branch `feat/atlas-pocketbase-cloud-llm` was also merged and pushed to `llm-debate-union/main`.

**Where we stopped:**
- `infra/main` includes the LLM Debate Union Atlas workflow docs and memory-vault service log.
- Atlas `postgres-memory-vault` is live and verified.

**Next up:**
- Continue app-side memory schema/docs and cloud gateway work from `llm-debate-union/main`.

## 2026-05-30 18:29:00 -04:00 - Track LLM Debate Union Atlas testing in GitHub Project

**What we did:**
- Created five testing issues in `DrewBeFree/llm-debate-union` for PocketBase, Postgres/pgvector, cloud gateway, ingestion, and repeatable testing docs.
- Added issues #4-#8 to GitHub Project #7, `Infra`.
- Verified the Infra project now has six items total, including the existing wiki deploy item plus the five LLM Debate Union testing items.

**Where we stopped:**
- Atlas testing work is represented in the GitHub Project with status `To triage`.

**Next up:**
- Triage the project items and continue implementation from the LLM Debate Union memory schema/docs and gateway tasks.

## 2026-05-31 00:18:00 -04:00 - Install Leantime planning cockpit on Atlas

**What we did:**
- Installed Leantime 3.8.0 on Atlas as a Docker Compose stack at `/home/drew/services/leantime`.
- Bound the app to the Atlas Tailscale IP on port `8095` and verified it at `http://atlas:8095`.
- Completed first-run setup for `drew@atlas.local`; generated admin credentials live only on Atlas in `/home/drew/services/leantime/admin-login.txt`.
- Seeded Leantime with current projects and tasks from the Infra project, LLM Debate Union testing issues, and infra backlog/current coordination items.
- Updated `ecosystem.json` and `wiki/docs/infrastructure/services.md` to include Leantime.
- Verified login redirect, container health after restart, and seeded task counts by project.

**Where we stopped:**
- Leantime is live as the private planning cockpit.
- Local infra and app session logs have uncommitted updates from this install.

**Next up:**
- User should log in and review the first cockpit pass.
- Decide whether to add a lightweight GitHub-to-Leantime sync script.

## 2026-05-31 15:01:20 -04:00 - Accordion ecosystem sitemap

**What we did:**
- Reworked the internal portal's primary view into a sitemap/org-chart style ecosystem map.
- Added accordion branches for Public Surface, Private Workbench, Sensitive / Controlled, Atlas Operations, and Docs & Planning.
- Kept branch counts visible while collapsing detailed nodes by default; search/filter views auto-expand matching branches.
- Verified the local preview at `http://127.0.0.1:8765/internal-portal/`, including an interaction check where `uhaul` opens only the sensitive UHaul Planner branch.
- Ran `node --test internal-portal/portal.test.mjs`, `node --check internal-portal/app.js`, `node --check internal-portal/dev-server.mjs`, and `git diff --check`.
- Fast-forward merged `feat/ecosystem-portal-sitemap` into `main`, pushed `infra/main`, and deployed to Atlas.

**Where we stopped:**
- Atlas portal is live at `http://atlas/ecosystem/` with the accordion sitemap assets deployed.
- `http://atlas/ecosystem/` and `http://atlas/ecosystem/ecosystem.json` both return `200`.
- Local preview server is running on `127.0.0.1:8765` for immediate browser review.

**Next up:**
- Review the sitemap/accordion feel in the browser and tune branch labels, grouping, or default-open behavior if needed.
- Continue future backlog items: UHaul IP/edge restriction, portal control hooks/runbooks, and Leantime/GitHub planning sync.

## 2026-05-31 15:36:21 -04:00 - Portal sidebar navigation and rendered wiki links

**What we did:**
- Added a left sidebar navigator to the internal portal with expandable registry-driven groups matching the sitemap branches.
- Replaced the sitemap's native details accordions with custom expandable sections so node lists ease in smoothly as branches open.
- Updated local Atlas wiki URL mapping to use rendered `wiki/site` pages instead of raw `wiki/docs/*.md` Markdown.
- Added a dev-server rewrite so old local `/wiki/docs/.../*.md` URLs serve the corresponding rendered MkDocs page.
- Verified local preview at `http://127.0.0.1:8765/internal-portal/`; the sidebar renders, medium-width toolbar no longer overflows, and `/wiki/docs/agents-and-skills/agents.md` returns rendered HTML.
- Ran `node --test internal-portal/portal.test.mjs`, `node --check internal-portal/app.js`, `node --check internal-portal/dev-server.mjs`, and `git diff --check`.
- Fast-forward merged `feat/portal-sidebar-wiki-links` into `main`, pushed `infra/main`, and deployed to Atlas.

**Where we stopped:**
- Atlas portal is live at `http://atlas/ecosystem/` with sidebar navigation and smooth sitemap branch expansion.
- `http://atlas/ecosystem/`, `http://atlas/ecosystem/ecosystem.json`, and `http://atlas/wiki/agents-and-skills/agents/` return `200` with rendered HTML where applicable.
- Local preview server is running on `127.0.0.1:8765` with the updated dev-server rewrite active.

**Next up:**
- Review the sidebar grouping/order in the browser and decide whether sidebar item clicks should open resources directly or focus/open the matching portal detail drawer.
- Continue future backlog items: UHaul IP/edge restriction, portal control hooks/runbooks, and Leantime/GitHub planning sync.

## 2026-05-31 17:51:10 -04:00 - Structural ecosystem map and catalog density pass

**What we did:**
- Reworked the portal map columns around local GitHub workspace structure: Agents, Apps, Homelab, Infra, Notes, and Sites.
- Changed map expansion to a global expand/collapse state so clicking any map header opens or closes all columns together with eased panel motion.
- Normalized expanded map column heights across wrapped rows with CSS grid row stretching.
- Dedupe-filtered sidebar/map branch display entries by label so repeated resources like Atlas Wiki do not appear twice in the navigator.
- Replaced the Services & Dashboards card grid with compact service-catalog rows containing inline state, visibility/type badges, target text, and tight right-side actions.
- Made the UHaul sensitive banner conditional on UHaul Planner being visible under the active search/filter state.
- Added the `@DrewBeFree Ecosystem` header identity, bundled `internal-portal/assets/pixelated-drew.png`, and added a served-file last-updated indicator in the header.
- Added fade-in motion to portal surfaces and dynamic rows/cards.
- Verified locally in the in-app browser: avatar loads, structural map buckets render, all map columns expand together, heights sync, sidebar duplicates are gone, compact ops rows render, and public filtering hides UHaul Planner plus its banner.
- Ran `node --test internal-portal/portal.test.mjs`, `node --check internal-portal/app.js`, `node --check internal-portal/dev-server.mjs`, and `git diff --check`.
- Fast-forward merged `feat/portal-structural-map-density` into `main`, pushed `infra/main`, and deployed to Atlas.

**Where we stopped:**
- Atlas portal is live at `http://atlas/ecosystem/` with the structural map, compact ops rows, header avatar, fade motion, and conditional UHaul banner.
- `http://atlas/ecosystem/`, `http://atlas/ecosystem/ecosystem.json`, and `http://atlas/ecosystem/assets/pixelated-drew.png` all return `200`.
- Local preview server is still running on `127.0.0.1:8765`.

**Next up:**
- Review the portal visually on Atlas and decide whether sidebar item clicks should open external resources directly or select/focus the matching portal detail drawer first.
- Consider adding live health data from OpenObserve/Prometheus/Better Stack as a telemetry layer under the existing ecosystem catalog.

## 2026-05-31 18:16:12 -04:00 - Portal filter modal pass

**What we did:**
- Replaced the always-visible visibility and type segmented controls with a single compact `Filters` button in the toolbar.
- Added a centered filter modal containing the existing Visibility and Type controls.
- Kept the active filter state visible on the toolbar button as `Visibility / Type`.
- Wired modal open, close, Escape handling, summary updates, and existing filter behavior without changing the registry contract.
- Verified locally in the in-app browser that the modal opens, Public/Apps filters update the summary and results, and closing the modal resets `aria-expanded`.
- Ran `node --test internal-portal/portal.test.mjs`, `node --check internal-portal/app.js`, `node --check internal-portal/dev-server.mjs`, and `git diff --check`.
- Fast-forward merged `feat/portal-filter-modal` into `main`, pushed `infra/main`, and deployed to Atlas.

**Where we stopped:**
- Atlas portal is live at `http://atlas/ecosystem/` with search plus a single filter modal button.
- `http://atlas/ecosystem/` and `http://atlas/ecosystem/ecosystem.json` return `200`; deployed HTML/JS include `filterModal` and `openFilterModal`.
- Local preview server is still running on `127.0.0.1:8765`.

**Next up:**
- Review the filter modal on Atlas and decide whether filter changes should auto-close the modal after selection or stay open for multi-step filtering.
- Continue exploring live health/telemetry integration under the ecosystem catalog.

## 2026-05-31 20:28:29 -04:00 - Portal sidebar app icons

**What we did:**
- Added app icons beside each entry in the Apps sidebar group, using bundled local assets instead of remote favicon guesses.
- Added a local AI Dog Trainer SVG icon and reused the Drew avatar for the DrewBeFree Profile sidebar row.
- Included Public Command Center in the Apps icon treatment so every visible Apps sidebar row has an image icon.
- Removed the redundant descriptive subtext from sidebar entries, keeping the rows compact and launcher-like.
- Verified locally in the in-app browser that the Apps sidebar has 14 rows, 14 icon slots, 14 image icons, and 0 legacy small subtext labels.
- Ran `node --check internal-portal/app.js`, `node --check internal-portal/dev-server.mjs`, `node --test internal-portal/portal.test.mjs`, and `git diff --check`.
- Fast-forward merged `feat/sidebar-app-icons` into `main`, pushed `infra/main`, and deployed to Atlas.

**Where we stopped:**
- Atlas portal is live at `http://atlas/ecosystem/` with sidebar app icons and compact no-subtext rows.
- `http://atlas/ecosystem/` and `http://atlas/ecosystem/assets/app-icons/ai-dog-trainer.svg` both return `200`.
- Latest portal commit on `main` is `8d579ec` (`feat: add portal sidebar app icons`).

**Next up:**
- Review the icon sizing/visual rhythm on Atlas and decide whether non-app sidebar groups should get their own smaller glyph treatment too.
- Continue exploring live health/telemetry integration under the existing ecosystem catalog.

## 2026-05-31 20:45:35 -04:00 - Portal sidebar icon gradient polish

**What we did:**
- Updated the Apps sidebar icon tiles to use a blue-to-gray gradient background with a subtle light border and inset shine.
- Inset the app image glyphs so the gradient background remains visible behind each app icon.
- Verified locally in the in-app browser that the Apps sidebar still has 14 rows, 14 icon slots, 0 old subtext labels, and the computed icon background is the new `linear-gradient(145deg, ...)`.
- Ran `node --check internal-portal/app.js`, `node --check internal-portal/dev-server.mjs`, `node --test internal-portal/portal.test.mjs`, and `git diff --check`.
- Fast-forward merged `feat/sidebar-icon-gradient` into `main`, pushed `infra/main`, and deployed to Atlas.

**Where we stopped:**
- Atlas portal is live at `http://atlas/ecosystem/` with blue-to-gray gradient app icon backgrounds.
- `http://atlas/ecosystem/` returns `200`, and deployed `style.css` includes the icon gradient rule.
- Latest portal style commit on `main` is `9c672ee` (`style: add sidebar app icon gradients`).

**Next up:**
- Review the gradient strength on Atlas and tune the inset/padding if the app glyphs feel too small.
- Continue exploring live health/telemetry integration under the existing ecosystem catalog.

## 2026-05-31 20:55:31 -04:00 - Portal promoted to Atlas homepage

**What we did:**
- Updated the internal portal deploy script so `http://atlas/` becomes a lightweight redirect to `/ecosystem/`.
- Preserved the previous Homelab/Atlas status dashboard under `/status/` on first deploy.
- Updated `ecosystem.json` so the internal portal owns `http://atlas/`, while the old status dashboard points to `http://atlas/status/`.
- Updated local preview URL mapping, portal README, and tests for the new Atlas homepage behavior.
- Ran `node --check internal-portal/app.js`, `node --check internal-portal/dev-server.mjs`, `node --test internal-portal/portal.test.mjs`, `node -e` JSON parse validation for `ecosystem.json`, and `git diff --check`.
- Fast-forward merged `feat/portal-atlas-home` into `main`, pushed `infra/main`, and deployed to Atlas.

**Where we stopped:**
- Opening `http://atlas/` in the in-app browser redirects to `http://atlas/ecosystem/` and shows the portal brand.
- `http://atlas/ecosystem/` returns `200`.
- `http://atlas/status/` returns `200` and preserves the old status dashboard.
- Latest homepage commit on `main` is `d56a029` (`feat: make portal the atlas homepage`).

**Next up:**
- Review the new homepage flow on Atlas and decide whether `/ecosystem/` should remain visible or whether nginx should serve the portal directly at `/` later.
- Continue exploring live health/telemetry integration under the existing ecosystem catalog.

## 2026-05-31 21:16:42 -04:00 - UHaul banner default-homepage fix

**What we did:**
- Diagnosed why the UHaul sensitive banner still appeared on the portal homepage: `renderAttention()` treated the default `All / All` view as an active visible UHaul result.
- Changed the banner condition so it only appears when UHaul is visible and the user has explicitly surfaced it by searching `uhaul`/`u-haul` or filtering to `Sensitive`.
- Updated the portal static test contract to assert the new `uhaulIntent` behavior.
- Verified locally that the default homepage hides `#uhaulBanner`.
- Ran `node --check internal-portal/app.js`, `node --check internal-portal/dev-server.mjs`, `node --test internal-portal/portal.test.mjs`, `node -e` JSON parse validation for `ecosystem.json`, and `git diff --check`.
- Fast-forward merged `fix/uhaul-banner-intent` into `main`, pushed `infra/main`, and deployed to Atlas.

**Where we stopped:**
- Opening `http://atlas/` redirects to `http://atlas/ecosystem/` and the UHaul banner is hidden by default.
- Deployed `app.js` includes the `uhaulIntent` condition.
- Latest fix commit on `main` is `ab952ba` (`fix: hide uhaul banner until explicitly surfaced`).

**Next up:**
- Review whether the UHaul app row itself should remain visible in the default Apps sidebar, or whether sensitive apps should also require an explicit Sensitive filter.
- Continue exploring live health/telemetry integration under the existing ecosystem catalog.

## 2026-05-31 21:38:24 -04:00 - Unified portal filters and compact rows

**What we did:**
- Removed the dedicated UHaul sensitive banner from the portal entirely.
- Replaced repository cards with compact catalog rows using inline visibility/type/state badges, target text, and `Open`/`Details` actions.
- Moved deeper repository/service/dashboard info into the existing detail drawer so rows stay dense while still exposing links, docs, deploy targets, and command hooks.
- Changed filtering to use one shared `matchesItemFilters()` path across repositories, services, dashboards, docs, map nodes, and sidebar groups.
- Verified locally that the Sensitive filter leaves only sensitive rows across repo/ops/docs streams, and the Apps filter includes app repos plus app-bucket dashboard entries.
- Verified locally that rows render at compact medium-width heights with no repository cards and no UHaul banner node.
- Ran `node --check internal-portal/app.js`, `node --check internal-portal/dev-server.mjs`, `node --test internal-portal/portal.test.mjs`, `node -e` JSON parse validation for `ecosystem.json`, and `git diff --check`.
- Fast-forward merged `feat/portal-unified-filter-density` into `main`, pushed `infra/main`, and deployed to Atlas.

**Where we stopped:**
- Opening `http://atlas/` redirects to `http://atlas/ecosystem/`.
- Atlas portal has no `uhaulBanner`, no repository cards, 24 compact repo rows, 16 ops rows, and 5 docs rows in the default view.
- Deployed HTML includes `catalog-list`, and the browser check confirmed row actions are `Open` and `Details`.
- Latest feature commit on `main` is `0dd1ee2` (`feat: unify portal filters and compact directory`).

**Next up:**
- Do a dedicated mobile viewport review and tune the one-column row stacking, sidebar group behavior, and topbar density.
- Continue exploring live health/telemetry integration under the existing ecosystem catalog.

## 2026-06-02 16:41:52 -04:00 - Portal infographic map prototype

**What we did:**
- Created a visual mockup for three ecosystem map directions and chose a hybrid metro/topology direction.
- Documented the approved design and implementation plan under `docs/superpowers/`.
- Replaced the internal portal accordion sitemap with a clickable infographic-style system map.
- Added zones for Source + Repos, Atlas Core, Alienware Local Compute, Public Edge, Docs + Planning, and Sensitive Controls.
- Made Alienware visible as its own local compute/workstation zone with Ollama, Open WebUI, OpenClaw, LLM Debate Union, Lead Gen Agent, and Ollama Monitoring represented from the canonical registry.
- Preserved shared search/filter behavior and existing detail drawer launch behavior from map nodes.
- Fixed the map host classifier so GitHub repository URLs do not make private repos appear in Public Edge.
- Confirmed the `surfthewebb.com` note as a taxonomy guard: custom/public domains should not force items into the `sites` repo bucket; repo family remains based on canonical local path/category.
- Ran `node --test internal-portal/portal.test.mjs` successfully after rerunning outside the Windows sandbox spawn restriction.
- Verified locally in the in-app browser at `http://127.0.0.1:8765/internal-portal/` that the map renders, Alienware appears, clicking the Alienware zone opens Ollama details, and filtering narrows the whole portal.

**Where we stopped:**
- Work is on branch `feat/portal-infographic-map` and ready to merge after review/commit.
- The local portal preview server is running on `http://127.0.0.1:8765/internal-portal/`.

**Next up:**
- Do a dedicated mobile viewport pass for the new map and sidebar together.
- Merge to `main`, push, and deploy to Atlas when approved.

## 2026-06-02 16:59:34 -04:00 - Ollama Monitoring portal links

**What we did:**
- Traced the missing Grafana/Ollama Monitoring links to thin metadata in `ecosystem.json`.
- Updated the `Ollama Monitoring` dashboard entry to open the provisioned Grafana dashboard route at `http://localhost:3000/d/ollama-overview/ollama-overview`.
- Added Prometheus, README, setup, Grafana dashboard JSON, and docker-compose deploy metadata to the dashboard entry.
- Added `Ollama Monitoring README` and `Ollama Monitoring Setup` to the main portal Docs stream.
- Added a portal regression test for the Grafana URL, docs, and Alienware docker-compose deploy target.
- Verified locally that the portal row Open link points to the Grafana dashboard and the Docs section includes the Ollama Monitoring docs.

**Where we stopped:**
- Work is on branch `fix/ollama-monitoring-links` and ready to merge after commit.
- Local preview remains available at `http://127.0.0.1:8765/internal-portal/`.

**Next up:**
- Commit, merge to `main`, and push.
- Deploy the updated registry/portal to Atlas when ready.

## 2026-06-02 17:16:17 -04:00 - Atlas portal infographic deployment

**What we did:**
- Deployed the updated internal portal to Atlas by pulling `infra/main` and running `internal-portal/deploy.sh` on Atlas.
- Confirmed Atlas pulled through `73dee8c` (`fix: add ollama monitoring links`), including the infographic map work and Ollama Monitoring link/docs metadata.
- Verified `http://127.0.0.1/`, `http://127.0.0.1/ecosystem/`, and `http://127.0.0.1/status/` return `200` from Atlas.
- Verified the deployed portal files include the Grafana dashboard route `http://localhost:3000/d/ollama-overview/ollama-overview`, `Ollama Monitoring README`, `Ollama Monitoring Setup`, and the `Alienware Local Compute` map zone.

**Where we stopped:**
- Atlas portal files are synced to `/opt/homelab-status-dashboard/ecosystem`.
- Atlas home still redirects to `/ecosystem/`, and the old status dashboard remains preserved at `/status/`.
- Local repo is on `main`.

**Next up:**
- Review the deployed portal from the browser at `http://atlas/ecosystem/`.
- Do a dedicated mobile viewport pass for the new infographic map/sidebar layout.

## 2026-06-02 17:23:56 -04:00 - Surf The Webb Framer site tracking

**What we did:**
- Added `Surf The Webb` to `infra/ecosystem.json` as a public `site` managed externally by Framer.
- Kept Framer as the deployment/source-of-truth surface rather than inventing a GitHub checkout.
- Updated portal bucketing so explicit `category: "site"` entries appear under Sites even without a local repo folder.
- Updated launcher action labels so Ollama Monitoring now shows visible `Grafana` and `Prometheus` buttons instead of a generic `Open` button.
- Added regression coverage for external-managed site entries and Surf The Webb specifically.
- Verified locally that the Sites navigator shows 4 entries including Surf The Webb, Surf opens `https://surfthewebb.com/`, and Ollama Monitoring actions show `Grafana`, `Prometheus`, and `Details`.

**Where we stopped:**
- Work is on branch `fix/surf-the-webb-framer-site`.
- Local verification passes, but the branch is not committed, merged, pushed, or deployed yet.

**Next up:**
- Commit, merge to `main`, push, and deploy to Atlas.

## 2026-06-02 17:27:40 -04:00 - Surf The Webb portal deployment

**What we did:**
- Committed `5e2b947` (`fix: track surf the webb framer site`) and fast-forward merged it into `main`.
- Pushed `infra/main` to GitHub.
- Deployed the updated portal to Atlas by pulling `main` and running `internal-portal/deploy.sh`.
- Verified Atlas serves `http://127.0.0.1/` and `http://127.0.0.1/ecosystem/` with `200`.
- Verified deployed files include `Surf The Webb`, `https://surfthewebb.com`, and visible `Grafana` / `Prometheus` action-label logic.

**Where we stopped:**
- Local repo is clean on `main`.
- Atlas portal is deployed from `/opt/homelab-status-dashboard/ecosystem`.

**Next up:**
- Review `http://atlas/ecosystem/` visually and do the dedicated mobile pass.

## 2026-06-02 17:41:49 -04:00 - Derived portal docs index

**What we did:**
- Fixed the portal docs drift where `Docs + Planning` and the lower Docs list only read top-level `registry.docs`, while map/dashboard nodes used nested resource `docs`.
- Added a derived docs index in `internal-portal/app.js` that combines top-level docs with nested docs from repositories, services, and dashboards.
- Removed duplicated top-level Ollama Monitoring docs from `ecosystem.json`; those docs now live with the `Ollama Monitoring` dashboard entry and are surfaced automatically.
- Updated tests to assert the derived docs index exists and that Ollama Monitoring docs are not duplicated into top-level `registry.docs`.
- Verified locally that `Docs + Planning`, the lower Docs list, and Ollama Monitoring row all show the same Grafana/Prometheus/docs metadata path.

**Where we stopped:**
- Work is on branch `fix/portal-derived-doc-index`.
- Verification passes locally, but the fix is not committed, merged, pushed, or deployed yet.

**Next up:**
- Commit, merge to `main`, push, and deploy to Atlas.

## 2026-06-02 18:00:57 -04:00 - Atlas Grafana link correction

**What we did:**
- Corrected the canonical `Ollama Monitoring` dashboard entry in `ecosystem.json` so Grafana and Prometheus link to Atlas (`http://atlas:3000` and `http://atlas:9090`) instead of Alienware-local `localhost` URLs.
- Updated the monitoring deploy target host from `alienware` to `atlas` and marked the status as `live`.
- Updated portal regression coverage to assert the Atlas Grafana/Prometheus URLs and Atlas deploy host.
- Verified the local rendered portal row shows `Grafana` and `Prometheus` actions pointed at Atlas.
- Committed `d9cd0fa` (`fix: point monitoring links at atlas`), merged to `main`, pushed, and deployed the portal on Atlas.
- Verified Atlas serves `/ecosystem/` with `200`, Grafana with `200`, and Prometheus with `302`.

**Where we stopped:**
- The portal behavior fix is committed, pushed, merged, and deployed at `d9cd0fa`.
- Atlas portal files under `/opt/homelab-status-dashboard/ecosystem` include the corrected Atlas monitoring links.

**Next up:**
- Review `http://atlas/ecosystem/` visually from the browser.
- Decide whether to stop any Alienware-local Docker monitoring containers started during diagnosis.

## 2026-06-02 18:11:57 -04:00 - Atlas Grafana port correction

**What we did:**
- Corrected the `Ollama Monitoring` Grafana launcher from `http://atlas:3000` to the browser-facing Atlas Grafana port `http://atlas:3001`.
- Added the full tailnet Grafana URL `http://atlas.tail401605.ts.net:3001/d/ollama-overview/ollama-overview` as an alternate live URL in `ecosystem.json`.
- Updated the compact portal action renderer so duplicate Grafana URLs do not crowd out the Prometheus action.
- Updated portal tests to assert the `3001` Grafana dashboard URL and tailnet alternate.
- Verified locally that the rendered row shows `Grafana` -> `http://atlas:3001/d/ollama-overview/ollama-overview` and `Prometheus` -> `http://atlas:9090/`.
- Committed `23d2a53` (`fix: use atlas grafana port`), merged to `main`, pushed, and deployed to Atlas.
- Verified Atlas serves `/ecosystem/` with `200`, Grafana on `3001` with `302`, and Prometheus with `302`.

**Where we stopped:**
- The portal behavior fix is committed, pushed, merged, and deployed at `23d2a53`.
- Atlas portal files under `/opt/homelab-status-dashboard/ecosystem` include the corrected `3001` Grafana links.

**Next up:**
- Review `http://atlas/ecosystem/` visually from the browser.
- Decide whether to stop any Alienware-local Docker monitoring containers started during diagnosis.

## 2026-06-02 18:36:00 -04:00 - PowerEdge Grafana dashboard route

**What we did:**
- Corrected the Grafana dashboard route from the missing `ollama-overview` path to `http://atlas:3001/d/atlas-overview/poweredge-dashboard`.
- Updated the full tailnet alternate to `http://atlas.tail401605.ts.net:3001/d/atlas-overview/poweredge-dashboard`.
- Updated the dashboard JSON doc link to `https://github.com/DrewBeFree/homelab/blob/main/docs/528/atlas-overview.json`.
- Updated portal regression coverage for the PowerEdge dashboard route and Atlas overview JSON link.
- Verified the local rendered portal row shows `Grafana` -> `http://atlas:3001/d/atlas-overview/poweredge-dashboard` and `Prometheus` -> `http://atlas:9090/`.
- Committed `2a24fa9` (`fix: link poweredge grafana dashboard`), merged to `main`, pushed, and deployed to Atlas.
- Verified Atlas serves `/ecosystem/` with `200`, the PowerEdge Grafana route with `302`, and the deployed registry includes the corrected URLs.

**Where we stopped:**
- The portal behavior fix is committed, pushed, merged, and deployed at `2a24fa9`.
- Atlas portal files under `/opt/homelab-status-dashboard/ecosystem` include the corrected PowerEdge Grafana dashboard route.

**Next up:**
- Review `http://atlas/ecosystem/` visually from the browser and click through the Grafana launcher while authenticated.
- Consider splitting host dashboards and Ollama-specific metrics into separate portal entries if the current `Ollama Monitoring` label feels too broad.

## 2026-06-02 19:05:28 -04:00 - Atlas monitoring entry rename

**What we did:**
- Renamed the monitoring dashboard entry from `Ollama Monitoring` / `ollama-monitoring` to `Atlas / PowerEdge Monitoring` / `atlas-poweredge-monitoring`.
- Updated the summary to describe Atlas PowerEdge host, storage, and local LLM metrics instead of implying the whole dashboard is Ollama-only.
- Pointed the entry `localPath`, docker-compose deploy target, Prometheus config path, and deployment guide at the `homelab/docs/528` monitoring bundle.
- Kept the Ollama exporter README as a supporting doc link because Ollama remains one metric source.
- Updated portal tests to assert the new ID, name, docs, and dashboard route.
- Verified locally that the rendered portal row shows `Atlas / PowerEdge Monitoring` with `Grafana` and `Prometheus` actions, and no `Ollama Monitoring` row.
- Committed `f254194` (`fix: rename atlas monitoring entry`), merged to `main`, pushed, and deployed to Atlas.
- Verified Atlas serves `/ecosystem/` with `200`, and the deployed registry contains `atlas-poweredge-monitoring` / `Atlas / PowerEdge Monitoring`.

**Where we stopped:**
- The portal behavior fix is committed, pushed, merged, and deployed at `f254194`.
- Atlas portal files under `/opt/homelab-status-dashboard/ecosystem` have the corrected monitoring identity.

**Next up:**
- Review `http://atlas/ecosystem/` visually from the browser and click through the Grafana launcher while authenticated.
- Consider a future split between Atlas host monitoring and Ollama-specific metrics if they grow into separate dashboards.

## 2026-06-02 19:18:10 -04:00 - Hermes Atlas ecosystem entry

**What we did:**
- Confirmed Hermes is installed on Atlas at `/home/drew/.hermes/hermes-agent`, with CLI wrapper `/home/drew/.local/bin/hermes`.
- Confirmed the install is git-based from `git@github.com:NousResearch/hermes-agent.git` and reports `Hermes Agent v0.15.1`.
- Added `Hermes Agent` to `ecosystem.json` as a private Atlas `agent-runtime` service.
- Documented safe dashboard access through an SSH tunnel: start Hermes on Atlas with `/home/drew/.local/bin/hermes dashboard --host 127.0.0.1 --port 9119 --no-open --skip-build`, tunnel with `ssh -L 9119:127.0.0.1:9119 atlas`, then open `http://localhost:9119`.
- Added Hermes README and web dashboard README links, install/deploy metadata, and `accessCommands`.
- Updated the portal drawer command rendering to show `accessCommands`, and labeled port `9119` links as `Hermes`.
- Added regression coverage for the Hermes registry entry and access commands.
- Committed `39b56d6` (`feat: track hermes atlas install`), merged to `main`, pushed, and deployed to Atlas.
- Verified Atlas serves `/ecosystem/` with `200`, and the deployed registry includes `hermes-agent`, `Hermes Agent`, `http://localhost:9119`, and `/home/drew/.local/bin/hermes`.

**Where we stopped:**
- The Hermes portal entry is committed, pushed, merged, and deployed at `39b56d6`.
- Local `infra/main` is clean and aligned with `origin/main`.

**Next up:**
- Review `http://atlas/ecosystem/` visually and open the Hermes Details drawer to confirm the access commands are easy to follow.
- Decide whether to start a persistent Hermes dashboard service later; current recommendation is SSH tunnel only because the dashboard can expose API keys.

## 2026-06-06 07:14:54 -04:00 - Morning repo freshness and Atlas workspace

**What we did:**
- Created branch `feat/morning-repo-sync-brief`.
- Added `scripts/repo_freshness.py` to fetch repos, fast-forward clean behind repos, and write JSON/Markdown morning-brief reports.
- Added `scripts/compare_repo_freshness.py` to compare Alienware and Atlas reports and produce `repo-drift.md`.
- Added `scripts/clone_manifest.py` for cloning every repo in `repos.json` to a target workspace.
- Added `scripts/install_repo_freshness_windows.ps1` plus Atlas user systemd service/timer files.
- Updated `repos.json` to include `adhd-snap`, `DrewBeFree`, and `llm-debate-union`, and removed stale `interactive-setup`.
- Created canonical Atlas workspace `/home/drew/GitHub` and cloned the manifest repo set there.
- Installed Atlas user timer `repo-freshness-atlas.timer` for 6:45 AM daily.
- Installed Windows scheduled task `Morning Repo Freshness` for 6:45 AM daily.
- Verified Atlas timer job completes successfully and writes `/home/drew/infra/data/morning-brief/atlas-repo-freshness.*`.
- Verified Windows scheduled task completes successfully and writes `data/morning-brief/alienware-repo-freshness.*`.
- Generated a current drift report showing Atlas canonical workspace clean/current and Alienware with 17 repos needing attention.

**Where we stopped:**
- The morning freshness workflow is installed on both machines and generating ignored report artifacts under `data/morning-brief/`.
- The infra changes are uncommitted on branch `feat/morning-repo-sync-brief`.
- Current drift report flags real local work/branch differences, including `llm-debate-union`, `infra`, `homelab`, `DrewBeFree`, and several app repos.

**Next up:**
- Wire `data/morning-brief/repo-drift.md` into the future Hermes/dashboard morning brief renderer.
- Decide which Alienware dirty/ahead repos should be committed, pushed, or intentionally left local.

## 2026-06-02 19:23:05 -04:00 - Hermes dashboard runtime start

**What we did:**
- Diagnosed SSH tunnel errors (`channel open failed: connect failed`) as Atlas having no listener on `127.0.0.1:9119`.
- Confirmed `hermes dashboard --status` reported no running dashboard process.
- Started Hermes dashboard on Atlas bound to localhost only with `/home/drew/.local/bin/hermes dashboard --host 127.0.0.1 --port 9119 --no-open --skip-build`.
- Verified Atlas is listening on `127.0.0.1:9119` with Hermes PID `2692293`.

**Where we stopped:**
- Hermes dashboard is running on Atlas behind localhost-only binding.
- Alienware should connect with `ssh -L 9119:127.0.0.1:9119 atlas`, then open `http://localhost:9119`.

**Next up:**
- If the tunnel still shows connection refused, restart the SSH tunnel after the Atlas dashboard process is running.
- Decide whether Hermes dashboard should remain manual/tunneled or get a user systemd service.

## 2026-06-05 18:10 EDT - Atlas storage, task sync, portal, and Leantime handoff

**What we did:**
- Added the Documents-on-Atlas recommendation to `BACKLOG.md`: Atlas as source of truth, SMB/mapped access for Alienware and MacBook, limited offline cache only if needed, snapshots/versioning, and scheduled rclone backup to Google Drive.
- Added `docs/atlas-documents-hermes-cheap-handoff.md` and a backlog lane for an Atlas safety dashboard plus Hermes handoff/morning briefing work.
- Built `scripts/task_sync.py` and `scripts/ecosystem_task_sync.py` with tests, generated task-sync reports under `data/task-sync/`, and created `docs/task-sync.md`.
- Synced the ecosystem planning shape: 25 Leantime projects, 30 marker-managed Leantime tasks, matching GitHub Issues, matching GitHub Projects, and generated `data/task-sync/links.md`.
- Updated the internal ecosystem portal to load `sync-links.json`, expose per-project GitHub/Leantime/repo/issue links, keep sidebar and main sections collapsed by default, animate accordion opening/closing, and show one Atlas Wiki link plus relevant non-wiki docs.
- Repaired Leantime live state: Drew assigned to all expected projects, NULL project state/active values fixed, and marker-managed task statuses corrected from false Done to New/In Progress/Blocked.
- Hotfixed the running Leantime 3.8.0 container templates for milestone creation, list view, and Kanban rendering, then captured those fixes in `scripts/leantime-hotfixes/`.
- Updated the Atlas Wiki Services page with the planning/sync surfaces and runbook links.

**Where we stopped:**
- Local verification passes for sync tests and portal tests.
- The running Leantime container has the latest Kanban template patch applied, but the authenticated browser was at login, so final Kanban visual confirmation still needs Drew after login/refresh.
- GitHub still has 27 open Projects because `** Project Template **` and `U-Haul Load Planner Roadmap` remain extra boards outside the 25 expected ecosystem projects.

**Next up:**
- Refresh Leantime Kanban after login; if it still fails, capture the newest stack trace and update `scripts/leantime-hotfixes/`.
- Decide whether to archive the two extra GitHub Projects.
- Decide whether to create a dedicated `DrewBeFree/leantime-atlas` repo for durable Leantime overlays/image patches.

## 2026-06-06 01:14 EDT - Lead Desk ecosystem priority tile

**What we did:**
- Added the Lead Gen Agent Lead Desk Hub live URL to `ecosystem.json`.
- Added a top-strip `Likely Leads` tile in the internal ecosystem portal that links to `http://127.0.0.1:3027`.
- Wired the tile to read `http://127.0.0.1:8017/api/dashboard` and show the high-fit lead count when the local Lead Desk backend is running.
- Deployed the updated portal files to Atlas at `/opt/homelab-status-dashboard/ecosystem`.

**Where we stopped:**
- `http://atlas/ecosystem/` shows `3 Likely Leads` in the top dashboard strip and links to the local Lead Desk.
- The Lead Desk local backend/frontend are running on ports `8017` and `3027`.

**Next up:**
- Keep the tile dynamic once the collector/digest worker replaces the seeded review queue.

## 2026-06-06 02:05 EDT - Mobile portal navigator and priority operations links

**What we did:**
- Created branch `feat/mobile-ops-portal-links`.
- Added a real off-canvas mobile navigator to the internal ecosystem portal.
- Added first-viewport priority links for Lead Desk, AI Dashboard/Grafana, Leantime, and Hermes.
- Changed Lead Desk portal links from `127.0.0.1` to Alienware Tailscale `http://100.117.87.57:3027`.
- Changed Hermes from a broken direct `localhost:9119` phone link into a priority button that opens the Hermes details drawer and tunnel instructions.
- Deployed the updated portal files and `ecosystem.json` to Atlas.

**Where we stopped:**
- `http://atlas/ecosystem/` shows the priority links and mobile navigator.
- Browser checks confirmed the Lead Desk link points to Tailscale and Hermes opens the details drawer.
- Portal tests pass.

**Next up:**
- Keep the priority link list curated as more operator surfaces become always-on.

## 2026-06-06 02:35 EDT - Hermes mobile Tailscale proxy

**What we did:**
- Created branch `feat/hermes-mobile-proxy`.
- Set up a user-level nginx proxy on Atlas at `http://100.71.165.80:9119`.
- Kept Hermes itself bound to `127.0.0.1:9119` and forwarded to it locally.
- Added Basic Auth on the proxy and verified unauthenticated requests return `401`.
- Enabled `hermes-mobile-proxy.service` as a user systemd service; `linger=yes` is active for Drew so it can survive login sessions.
- Updated `ecosystem.json`, the internal portal Hermes priority link, and added `scripts/hermes-mobile-proxy/` runbook/templates.
- Deployed the updated internal portal files and registry to Atlas.

**Where we stopped:**
- `http://100.71.165.80:9119` returns the Hermes dashboard after Basic Auth.
- `http://atlas/ecosystem/` links Hermes directly to the Tailscale proxy.
- Tailscale Serve remains disabled at the tailnet level, so this uses user nginx instead.

**Next up:**
- Consider rotating the Basic Auth password into a password manager.
- If Tailscale Serve is later enabled, decide whether to replace the user nginx proxy with native Serve.

## 2026-06-06 02:49 EDT - Hermes mobile realtime proxy fixed

**What we did:**
- Investigated mobile Hermes repeatedly prompting for login and chat being unusable.
- Found nginx Basic Auth was challenging Safari's background realtime requests for `/api/ws`, `/api/events`, and `/api/pty`.
- Exempted those realtime endpoints from nginx Basic Auth while keeping Hermes' session-token auth and the Tailscale-only bind.
- Stripped `Origin` for those realtime endpoints so Hermes' loopback-bound WebSocket guard accepts the tokened connection forwarded by local nginx.
- Deployed the updated nginx config to Atlas and restarted `hermes-mobile-proxy.service`.

**Where we stopped:**
- WebSocket probes through `http://100.71.165.80:9119` now return `101` upgrades for `/api/events`, `/api/ws`, and `/api/pty`.
- The dashboard page still requires Basic Auth; invalid realtime tokens are rejected by Hermes without a browser Basic Auth challenge.

**Next up:**
- Reopen or hard-refresh Hermes on mobile and retry chat.
- Consider replacing the Basic Auth layer with native Tailscale Serve if tailnet Serve is enabled later.

## 2026-06-06 02:56 EDT - Hermes proxy Basic Auth password rotated

**What we did:**
- Rotated the Atlas Hermes mobile proxy Basic Auth password for user `drew`.
- Restarted `hermes-mobile-proxy.service`.
- Verified the previous generated password is rejected and the new user-provided password returns the Hermes dashboard.
- Verified the realtime `/api/events` websocket path still upgrades successfully after the rotation.

**Where we stopped:**
- Hermes mobile proxy is active at `http://100.71.165.80:9119`.
- The repo does not store the Basic Auth password or hash.

**Next up:**
- Use the updated password from the user's password manager or shared context when accessing Hermes from mobile.
## 2026-06-07 - Restore Lead Desk leads on Atlas

**What we did:**
- Investigated the missing 9 leads after moving the Desk Hub to Atlas.
- Found the Atlas service had initialized a fresh empty SQLite DB, while Alienware still had the 9-lead DB.
- Backed up the empty Atlas DB and restored the Alienware DB onto Atlas.
- Restarted the Atlas Lead Desk services.
- Verified `http://atlas:8017/api/dashboard` reports 9 total leads, 3 high-fit leads, and 9 draft-ready leads.

**Where we stopped:**
- The Atlas Desk Hub now has the expected 9 leads.

**Next up:**
- Decide whether Atlas is now the sole source of truth for Lead Desk data, or add a backup/sync workflow.

## 2026-06-08 - Review Grok Leantime sync workflow

**What we did:**
- Confirmed the new Leantime sync work is infra-related, not yes-app related.
- Found the Grok-built central receiver at `/home/drew/infra/.github/workflows/receive-task-sync.yml` and the app trigger at `/home/drew/GitHub/apps/trading-scanner-experimental/.github/workflows/trigger-task-sync.yml`.
- Confirmed the trigger dispatches `task-sync-request` to `DrewBeFree/infra` with full `source_repo` payload.
- Confirmed the receiver runs existing `ecosystem_task_sync.py` paths, then adds a raw issue importer that creates Leantime tickets with `task-sync-id: gh-issue:DrewBeFree/trading-scanner-experimental#N` markers.
- Noted conflict risk: raw issue import can duplicate BACKLOG-derived tasks that already use `task-*` markers, because it dedupes only on the `gh-issue:` marker.

**Where we stopped:**
- The trigger side is structurally compatible with infra.
- The receiver side is useful but should be tightened before broad rollout: remove `|| true`, do dry-run/report gating, unify marker/dedupe behavior, and avoid creating duplicate Leantime tickets for issues already mapped from BACKLOG tasks.

**Next up:**
- Decide whether raw GitHub issue import should be a separate mode or folded into `ecosystem_task_sync.py` with tests.
- Add tests for `gh-issue:` mapping and duplicate prevention before enabling this across more repos.

## 2026-06-09 - Sync LLM benchmark Grafana source of truth

**What we did:**
- Updated the `atlas-poweredge-monitoring` entry in `ecosystem.json` from the stale `atlas-overview/poweredge-dashboard` Grafana route to the actual LLM benchmark dashboard route: `http://atlas:3001/d/llm-benchmarks/llm-inference-benchmarks?orgId=1&from=now-6h&to=now&timezone=browser&refresh=5m`.
- Updated the tailnet Grafana URL, dashboard JSON doc label, dashboard JSON link, and Grafana deploy target note.
- The source for this sync now lives in `infra/llm-bench-dashboard/config/source-of-truth.json`; run `npm run sync-source` from that nested repo after dashboard metadata changes.

**Where we stopped:**
- `ecosystem.json` parses successfully and no longer contains the stale `atlas-overview/poweredge-dashboard` route.
- Parent `infra` repo still has unrelated pre-existing dirty changes, so this registry/session-log change was not committed there.

**Next up:**
- Export the live Grafana dashboard JSON for UID `llm-benchmarks` and save it under `infra/llm-bench-dashboard/grafana/atlas-poweredge-llm-benchmark.json`.

## 2026-06-09 - Atlas AI operating system plan

**What we did:**
- Created `docs/atlas-ai-operating-system-plan.md` to define Atlas as the durable shared source of truth for Codex, ChatGPT, Claude, Gemini, Grok, local Ollama models, and future agents.
- Captured the distinction that proprietary models do not need to literally live on Atlas; they need to query the same Atlas-hosted knowledge, repos, logs, decisions, configs, dashboards, and runbooks.
- Defined layers for access, Git workspace, knowledge vault, search/memory index, model access, agent/tooling, observability, and backup/recovery.
- Added a concrete P40 readiness plan for tomorrow, June 10, 2026.
- Added first build targets for a Markdown knowledge vault, `atlas-context`, and memory indexing.

**Where we stopped:**
- The plan doc is created but not committed in the parent `infra` repo because the parent branch already has several unrelated dirty changes.
- The failed screenshot/deploy chase was intentionally dropped; the focus is now Atlas as the shared AI operating system.

**Next up:**
- Use the plan to build Phase 0 before the P40 install: NoMachine/SSH reliability, central Git workspace, knowledge vault skeleton, baseline benchmarks, and first decision/runbook files.

## 2026-06-09 - Create Atlas AI OS Leantime project

**What we did:**
- Added `data/task-sync/atlas-ai-operating-system-leantime.json` with a Leantime project spec and ten tasks from `docs/atlas-ai-operating-system-plan.md`.
- Added `scripts/create_leantime_project_from_plan.mjs`, a marker-based Leantime project/task sync helper for this plan.
- Ran a dry-run against Atlas Leantime: create 1 project and 10 tickets.
- Applied the project and tickets to Leantime. The first apply hit the Leantime rate limit after creating the project and four tickets; after cooldown, the remaining six tickets were created with a slower write delay.
- Final postcheck reports `skip-ticket=10`, meaning all planned tasks are current in Leantime.

**Where we stopped:**
- Leantime project: `Atlas AI Operating System`, project ID `34`, URL `http://atlas:8095/projects/showProject/34`.
- Reports copied back into `data/task-sync/`:
  - `atlas-ai-operating-system-leantime-after-cooldown.json`
  - `atlas-ai-operating-system-leantime-apply-final.json`
  - `atlas-ai-operating-system-leantime-postcheck.json`

**Next up:**
- Open `http://atlas:8095/projects/showProject/34` and use it as the working board for Phase 0 before the P40 install.

## 2026-06-09 - Add Atlas AI OS Leantime milestones

**What we did:**
- Added five milestones to `data/task-sync/atlas-ai-operating-system-leantime.json`:
  - Foundation already completed
  - P40 readiness and benchmark proof
  - Knowledge vault and searchable memory
  - Multi-model Atlas access layer
  - GitHub and Leantime source-of-truth sync
- Added completed foundation tickets and marked them `Done`: plan doc, Leantime project, benchmark dashboard repo/site, canonical Grafana route, benchmark source-of-truth config, and Atlas helper automation.
- Updated `scripts/create_leantime_project_from_plan.mjs` to sync native Leantime milestone tickets, map `Done` to Leantime status `0`, attach tasks to milestones, and normalize Leantime's empty dependency/date fields during postchecks.
- Applied the milestone/task updates to Atlas Leantime project `34`. The first apply hit the Leantime rate limit; after cooldown the resume apply completed 22 writes.
- Final postcheck reports `skip-milestone=5` and `skip-ticket=17`, meaning Leantime matches the repo-backed spec.
- Updated `docs/atlas-ai-operating-system-plan.md` with the milestone list, completed foundation work, and the source-of-truth rule: repo spec -> Leantime; GitHub issue mirroring is not automatic yet.

**Where we stopped:**
- Leantime project `Atlas AI Operating System` now has milestones and completed work marked Done.
- Reports copied back into `data/task-sync/`:
  - `atlas-ai-operating-system-leantime-milestones-after-429-dry-run.json`
  - `atlas-ai-operating-system-leantime-milestones-apply-resume.json`
  - `atlas-ai-operating-system-leantime-milestones-diffcheck.json`
  - `atlas-ai-operating-system-leantime-milestones-postcheck-final.json`
- Parent `infra` repo remains dirty with pre-existing unrelated changes plus the new Atlas AI OS/task-sync artifacts; nothing was committed.

**Next up:**
- Decide whether GitHub Issues should mirror the same stable-id spec, then wire that intentionally through the existing GitHub task-sync path instead of relying on Leantime to sync back.
- Use the P40 readiness milestone as the working board for pre-install access checks and the controlled before benchmark.

## 2026-06-09 - Scaffold repo-wide Leantime milestones

**What we did:**
- Added `scripts/generate_repo_milestone_spec.mjs` to generate a repo-wide milestone/task spec from `repos.json`, `ecosystem.json`, `data/task-sync/tasks.json`, and `data/task-sync/leantime-project-map.json`.
- Generated `data/task-sync/repo-milestones.json` covering 25 registered repo projects.
- Added `scripts/sync_repo_milestones_to_leantime.mjs`, an idempotent Leantime sync for repo-wide milestones and completed foundation tickets using `repo-sync-id: ...` markers.
- Added read/write delay and batching controls so large Leantime runs can survive rate limits:
  - `--read-delay`
  - `--write-delay`
  - `--project`
  - `--limit-actions`
- Updated `docs/task-sync.md` with generation, dry-run, batch apply, and single-project apply commands.
- Ran a live Leantime dry-run from Atlas. It found 25 repos, 100 milestones to create, and 84 completed foundation tickets to create.

**Where we stopped:**
- No repo-wide live Leantime writes were applied yet. The current report is dry-run only: `data/task-sync/repo-milestones-leantime-dry-run.json`.
- The repo-wide rollout is ready to apply in batches because a full apply is roughly 184 writes and Leantime rate-limits both reads and writes.

**Next up:**
- Apply repo-wide milestones in batches with `--limit-actions 25`, or apply one repo at a time with `--project "Project Name"`.
- After all batches are applied, run a final dry-run and expect `skip-milestone=100` and `skip-ticket=84`.

## 2026-06-09 - Partially apply repo-wide Leantime milestones

**What we did:**
- Started applying the repo-wide Leantime milestone rollout from `data/task-sync/repo-milestones.json`.
- Applied six controlled batches with `--limit-actions 25`, `--read-delay 12000`, and `--write-delay 12000`.
- Batch reports on Atlas:
  - `data/task-sync/repo-milestones-leantime-apply-batch-01.json`
  - `data/task-sync/repo-milestones-leantime-apply-batch-02.json`
  - `data/task-sync/repo-milestones-leantime-apply-batch-03.json`
  - `data/task-sync/repo-milestones-leantime-apply-batch-04.json`
  - `data/task-sync/repo-milestones-leantime-apply-batch-05.json`
  - `data/task-sync/repo-milestones-leantime-apply-batch-06.json`
- Confirmed each of the first six batches applied 25 records, for 150 repo-wide milestone/foundation records applied total.
- Answered the benchmark-context aside: the canonical initial local suite is `poweredge-p40-local-llm-control-suite` v1.0 with `temperature=0`, `seed=42`, `num_ctx=4096`, `num_predict=768`, and five homelab operations prompts.

**Where we stopped:**
- Batch 7 could not be launched because Atlas SSH stopped returning through this Codex tool session; even `ssh atlas "echo atlas-ok"` timed out.
- Expected remaining creates after six successful batches: 34 records.
- Final postcheck has not been run yet.

**Next up:**
- Resume from Atlas or a fresh Codex session with:
  `cd /home/drew/GitHub/infra && node scripts/sync_repo_milestones_to_leantime.mjs --apply --read-delay 12000 --write-delay 12000 --limit-actions 25 --env /home/drew/services/task-sync/.env --spec data/task-sync/repo-milestones.json --report data/task-sync/repo-milestones-leantime-apply-batch-07.json`
- Then run one final apply batch if needed and a dry-run postcheck expecting `skip-milestone=100` and `skip-ticket=84`.

## 2026-06-09 - Create P40 prep day checklist

**What we did:**
- Created `docs/p40-prep-2026-06-09-checklist.md` as a step-by-step operating checklist for today.
- Focused the checklist on getting Atlas visible, recording firmware state, updating BIOS safely, optionally updating iDRAC, running the pre-P40 benchmark, and saving evidence.
- Included known Atlas facts: PowerEdge R720xd, iDRAC7 at `https://10.0.0.38`, virtual console confirmed working, and the canonical Grafana benchmark dashboard URL.
- Added explicit stop conditions so technical work does not turn into guesswork.

**Where we stopped:**
- The checklist exists locally in the infra repo and is ready to open on the Atlas monitor.
- BIOS update has not been performed in this session.
- Pre-P40 benchmark has not been run in this session.

**Next up:**
- Put Atlas on a monitor or iDRAC virtual console, then work through `docs/p40-prep-2026-06-09-checklist.md` in order.

## 2026-06-09 - Audit workspace branch cleanup

**What we did:**
- Audited Git repositories under `C:\Users\drewb\Documents\GitHub`.
- Saved the audit report to `data/git-cleanup/branch-cleanup-audit-2026-06-09.json`.
- Found 28 Git repos, 17 dirty repos, and 68 safe local branch-delete candidates.
- Added `scripts/cleanup_merged_branches.ps1`, which reads the saved audit and deletes only listed local branches with `git branch -d`.
- Dry-ran the cleanup script and confirmed it plans 68 deletions, with no deletes performed in dry-run.
- The largest target is `infra`: 27 safe merged local branches. The script does not touch dirty files, `main`, `master`, `dev`, current branches, or unmerged branches.

**Where we stopped:**
- Actual branch deletion did not run because the approval system timed out twice before executing the destructive command.
- No branch deletion was confirmed from this cleanup step.

**Next up:**
- Run the cleanup apply when approval is available:
  `powershell -ExecutionPolicy Bypass -File C:\Users\drewb\Documents\GitHub\infra\scripts\cleanup_merged_branches.ps1 -AuditPath C:\Users\drewb\Documents\GitHub\infra\data\git-cleanup\branch-cleanup-audit-2026-06-09.json -ReportPath C:\Users\drewb\Documents\GitHub\infra\data\git-cleanup\branch-cleanup-apply-2026-06-09.json -Apply`
- After deletion, rerun the branch audit and then handle dirty worktrees separately repo by repo.

## 2026-06-09 - Patch Leantime milestone date issue

**What we did:**
- Investigated Chrome console errors showing Leantime Gantt failures: negative SVG `<rect>` widths in `compiled-gantt-component.3.8.0.min.js`.
- Identified the likely root cause: our JSON-RPC milestone sync bypassed Leantime's normal milestone form defaults and allowed blank `editFrom` / `editTo` values.
- Patched `scripts/generate_repo_milestone_spec.mjs` so repo-wide milestones include explicit `start_date` / `due_date` values.
- Regenerated `data/task-sync/repo-milestones.json` with valid milestone date ranges.
- Patched `scripts/sync_repo_milestones_to_leantime.mjs` and `scripts/create_leantime_project_from_plan.mjs` so missing milestone dates default to `2026-06-09` instead of blank strings.
- Added `start_date` values to `data/task-sync/atlas-ai-operating-system-leantime.json`.
- Added `docs/leantime-milestone-500-repair.md` with the exact Atlas repair commands and log collection steps if the 500 persists.

**Where we stopped:**
- The repo-side fix is prepared.
- The live Leantime repair has not been applied yet because Atlas SSH/API access still needs to be run from Atlas or a working session.
- The `/api/users?profileImage=` 500 may be separate and needs Docker logs if it continues after milestone date repair.

**Next up:**
- On Atlas, run the repair commands in `docs/leantime-milestone-500-repair.md`.
- After repair, reload the Leantime milestone page and confirm the Gantt negative-width errors stop.
- If `/api/users?profileImage=` still returns 500, capture `docker logs leantime --tail 120`.

## 2026-06-11 - Identify P40 checklist DOCX origin

**What we did:**
- Inspected `C:\Users\drewb\Documents\00-inbox\Atlas_R720xd_Tesla_P40_Install_Checklist.docx`.
- Read filesystem metadata and DOCX core properties.
- Found the file owner is `Drew-AlienWare\drewb`.
- Found DOCX creator metadata is `python-docx`.
- Found the Windows `Zone.Identifier` alternate data stream points to a ChatGPT download/referrer URL.

**Where we stopped:**
- The file appears to have been generated programmatically with `python-docx` and downloaded from ChatGPT on June 5, 2026 around 7:49 PM.

**Next up:**
- If exact conversation authorship matters, open the ChatGPT referrer conversation from the `Zone.Identifier` metadata.

## 2026-06-10 - Triage checkout block before LLM Debate Union feedback

**What we did:**
- Read infra project memory and repo session logs before touching the workspace.
- Confirmed `infra` is on `feat/morning-repo-sync-brief` with tracked and untracked local changes, so Git is correctly blocking branch checkout to avoid overwriting work.
- Confirmed `apps/llm-debate-union` is also dirty on `fix-api-key-stored-indicators`, with implementation, README, session-log, test, script, docs, and output changes.
- Identified `llm-debate-union` in the infra registry and existing task-sync data, so new user feedback can be captured as backlog items once provided.

**Where we stopped:**
- No stash, commit, checkout, or file cleanup was performed.
- The immediate guidance is to park dirty work before branch switching, preferably with named stashes if the goal is only to record backlog feedback.

**Next up:**
- Capture Drew's LLM Debate Union feedback and convert it into backlog items.
- If branch switching is needed first, stash dirty work in `infra` and/or `apps/llm-debate-union` with clear messages, then checkout the target branch.

## 2026-06-10 - Clean merged local infra branches

**What we did:**
- Audited local infra branches against `main`.
- Deleted 26 local branches that were already merged into `main` using `git branch -d`.
- Verified the remaining local branches are `main`, `dev`, `feat/morning-repo-sync-brief`, `docs-log-lead-gen-project-deploy`, and `feat-track-lead-gen-agent`.

**Where we stopped:**
- The infra local branch list is cleaned up.
- The worktree is still dirty on `feat/morning-repo-sync-brief`; no working-tree changes were stashed, committed, or removed.
- The two non-current topic branches left are not merged into `main`, so they were preserved.

**Next up:**
- Decide whether to keep or separately inspect `docs-log-lead-gen-project-deploy` and `feat-track-lead-gen-agent`.
- Park or commit the dirty `feat/morning-repo-sync-brief` work before switching branches.

## 2026-06-10 - Add cross-repo branch cleanup issue to Infra project

**What we did:**
- Turned the cross-repo merged-branch cleanup idea into GitHub issue `DrewBeFree/infra#36`.
- Added the issue to GitHub Project `Infra` with status `To triage`.
- Confirmed the issue tracks auditing all repos under `C:\Users\drewb\Documents\GitHub`, deleting only safely merged local branches, preserving dirty/current/unmerged branches, and avoiding remote branch deletion unless separately approved.

**Where we stopped:**
- The branch cleanup is now captured as backlog instead of interrupting Atlas monitor/P40 prep work.

**Next up:**
- Return focus to getting Atlas visible on the monitor.
- Later, use issue #36 to run a repo-by-repo branch cleanup with a report and cautious deletion rules.

## 2026-06-10 - Park GitHub/Leantime sync concern and stage NoMachine install

**What we did:**
- Created GitHub issue `DrewBeFree/infra#37` to verify whether GitHub issue/project items are syncing into Leantime after a GitHub browser CSP warning.
- Added issue #37 to the GitHub Project `Infra` with status `To triage`.
- Checked Atlas NoMachine state over SSH: `nxserver` was not installed, no `nxserver.service` existed, and port `4000` was not listening.
- Confirmed Atlas is `x86_64` Ubuntu 24.04.4 LTS with `dpkg`, `apt-get`, desktop sessions, and `graphical.target`.
- Verified the current official NoMachine Linux amd64 DEB from NoMachine's download page is version `9.6.3_1`, with MD5 `34d5882d1a1d20bbe9d5f7b3e2f35f12`.
- Downloaded the DEB on Windows, verified the MD5 locally, copied it to Atlas at `/tmp/nomachine_9.6.3_1_amd64.deb`, and verified the MD5 on Atlas.

**Where we stopped:**
- NoMachine installation is blocked on Atlas sudo password entry; `sudo dpkg -i /tmp/nomachine_9.6.3_1_amd64.deb` requires an interactive password prompt.
- Atlas package staging is complete; install itself has not run.

**Next up:**
- In an interactive terminal, run `ssh atlas` then `sudo dpkg -i /tmp/nomachine_9.6.3_1_amd64.deb`.
- After install, verify `/usr/NX/bin/nxserver --status`, `systemctl status nxserver`, and port `4000`.

## 2026-06-10 - Verify NoMachine server on Atlas

**What we did:**
- Verified the NoMachine install completed on Atlas.
- Confirmed `/usr/NX/bin/nxserver --status` reports new connections enabled and `nxserver`, `nxnode`, and `nxd` enabled.
- Confirmed `nxserver.service` is enabled and active/running.
- Confirmed Atlas is listening on port `4000` for IPv4 and IPv6.
- Confirmed Windows can reach `atlas:4000`, resolving to Tailscale address `100.71.165.80`.

**Where we stopped:**
- Atlas NoMachine server is ready for client connection.
- The client-side visual login/test has not been confirmed yet.

**Next up:**
- Open NoMachine on Windows and connect to `atlas` or `100.71.165.80` using port `4000`.
- Confirm the Atlas desktop appears and can be used as the monitor/visual console for P40 prep.

## 2026-06-10 - Diagnose Atlas Ethernet internet issue

**What we did:**
- Confirmed Drew successfully connected to Atlas from Alienware using NoMachine.
- Investigated Atlas network state after the desktop showed no normal internet access.
- Found `eno1` has carrier at 1 Gbps and is the plugged-in Ethernet port.
- Found the active NetworkManager profile `eno1` has `ipv4.method: disabled`, so Atlas has no IPv4 address and no IPv4 default route.
- Found Atlas does have IPv6 internet connectivity through `eno1`; IPv6 ping and HTTPS to Cloudflare succeeded.
- Found DNS is also incomplete for normal public names: only Tailscale DNS is configured, and public names like `github.com` do not resolve.

**Where we stopped:**
- Root cause is likely the active `eno1` profile disabling IPv4 DHCP, plus no public DNS resolver on the physical interface.
- Attempting to modify the active NetworkManager profile over SSH failed with `Insufficient privileges`, so the fix needs to be run interactively on Atlas with sudo.

**Next up:**
- In the NoMachine terminal on Atlas, run `sudo nmcli connection modify eno1 ipv4.method auto ipv6.method auto connection.autoconnect yes` then `sudo nmcli connection up eno1`.
- Verify `ip -br addr show eno1`, `ip route`, `resolvectl query github.com`, and `ping -c 2 1.1.1.1`.

## 2026-06-10 - Restore Atlas IPv4/DNS internet

**What we did:**
- Drew ran the NetworkManager fix interactively on Atlas through NoMachine.
- Confirmed `eno1` now has IPv4 address `10.0.0.145/24`.
- Confirmed default IPv4 route exists: `default via 10.0.0.1 dev eno1`.
- Confirmed DNS resolves `github.com` through `eno1`.
- Verified from SSH that `ping -c 2 1.1.1.1` succeeds with 0% packet loss.
- Verified from SSH that `curl -I https://github.com` returns HTTP `200`.
- Confirmed the active `eno1` profile is now `ipv4.method auto`, `ipv6.method auto`, and `connection.autoconnect yes`.

**Where we stopped:**
- Atlas internet access is restored over Ethernet port 1.
- NoMachine remains usable as the visual console from Alienware.

**Next up:**
- Continue the P40 prep checklist: keep Atlas visible, record BIOS/iDRAC state, and proceed to firmware/pre-P40 benchmark steps only after confirming console access remains reliable.

## 2026-06-10 - Add Ubuntu Pro enablement backlog item

**What we did:**
- Discussed whether to enable Ubuntu Pro on Atlas.
- Decided it is useful but should wait until Atlas visibility, internet, Software Updater, firmware state, and P40 prep are stable.
- Created GitHub issue `DrewBeFree/infra#38` titled `Enable Ubuntu Pro on Atlas after P40 prep stabilizes`.
- Added issue #38 to the GitHub Project `Infra` with status `To triage`.

**Where we stopped:**
- Drew is running Software Updater on Atlas through NoMachine.
- Ubuntu Pro enablement is parked as backlog instead of interrupting the current update/P40 prep flow.

**Next up:**
- Let Software Updater finish, note whether a reboot is required, then continue the P40 prep checklist.
- Later, use issue #38 to attach Atlas to Ubuntu Pro and document enabled services.

## 2026-06-10 - Locate pre-P40 benchmark evidence

**What we did:**
- Searched local infra and Atlas for the already-run pre-P40 benchmark evidence.
- Confirmed the local `infra/llm-bench-dashboard/data/benchmarks.sqlite` contains only synthetic sample rows, not the real baseline.
- Found the real Atlas benchmark result files on Atlas at `/home/drew/benchmarks/results/`.
- Identified the full pre-P40 Atlas baseline as `/home/drew/benchmarks/results/benchmark_atlas_20260609_093237.json`.
- Copied the benchmark JSON files to `C:\tmp\` for inspection.
- Confirmed the full Atlas baseline timestamp is `2026-06-09T09:32:37.653281`, host `http://localhost:11434`, models `qwen2.5:14b` and `llama3.2:3b`, context lengths `512, 1024, 2048, 4096, 8192`, and `runs_per_model` 2.

**Where we stopped:**
- The pre-P40 baseline has been found and does not need to be rerun before BIOS/P40 work unless we decide the prior benchmark methodology is insufficient.

**Next up:**
- Use `/home/drew/benchmarks/results/benchmark_atlas_20260609_093237.json` as the before-P40 comparison baseline.
- Consider copying or committing a summarized benchmark evidence note later so the result is not only on Atlas.

## 2026-06-10 - Confirm Atlas post-reboot health and firmware identity

**What we did:**
- Reviewed Drew's post-reboot Atlas checks from NoMachine.
- Confirmed Atlas booted cleanly, `eno1` retained `10.0.0.145/24`, and IPv4 internet works with 0% packet loss to `1.1.1.1`.
- Confirmed `curl -I https://github.com` returns HTTP `200`.
- Confirmed `systemctl --user --failed` reports `0 loaded units listed`.
- Confirmed expected Docker services are running after reboot, including `ollama`, `open-webui`, `atlas-grafana`, `benchmark-exporter`, `leantime`, and monitoring containers.
- Recorded firmware identity from `dmidecode`: product `PowerEdge R720`, service tag `8J8BBZ1`, BIOS `2.0.19`, BIOS date `08/29/2013`.
- Noted correction: prior docs/checklist said R720xd, but the machine itself reports R720; use service tag `8J8BBZ1` for Dell firmware downloads.

**Where we stopped:**
- Atlas is healthy enough to proceed toward BIOS update prep.
- Drew attempted `https://10.0.0.38` in the shell; that URL needs to be opened in a browser, not executed as a command.

**Next up:**
- Open `https://10.0.0.38` in a browser and confirm iDRAC login plus virtual console before any BIOS update.
- Download the BIOS package from Dell using service tag `8J8BBZ1` and update BIOS only first.

## 2026-06-10 - Check physical monitor no-signal state

**What we did:**
- Drew connected a keyboard, mouse, and monitor directly to Atlas, with the monitor connected to the front video port.
- The monitor showed no signal.
- Verified over SSH that Atlas is up, with uptime around 31 minutes after the update reboot.
- Verified GDM/display-manager is active/running, though `systemctl is-system-running` reports `degraded`.

**Where we stopped:**
- Atlas OS is alive, so the no-signal problem is likely the physical display path, monitor input, VGA cable/adapter direction, or front-vs-rear VGA behavior.

**Next up:**
- Check monitor input and cable/adapter path.
- Try rear VGA if available.
- Avoid moving the only Ethernet cable from port 1 to iDRAC unless a second cable or physical console recovery path is available.

## 2026-06-10 - Start Atlas BIOS 2.9.0 update

**What we did:**
- Downloaded Dell BIOS package `BIOS_8P8WX_LN_2.9.0.BIN` for PowerEdge R720/R720-xd.
- Copied it to Atlas at `/tmp/BIOS_8P8WX_LN_2.9.0.BIN`.
- Verified SHA256 matched Dell's published checksum: `0fc8f43ddc93e71857a51ee8867521701a8396ef31feb97a637639c22376204d`.
- Ran the updater on Atlas; validation reported `Server BIOS 12G`, package version `2.9.0`, installed version `2.0.19`.
- Confirmed the updater loaded the BIOS image and asked to reboot.
- Atlas began rebooting for the BIOS update.

**Where we stopped:**
- Atlas has not yet returned on SSH after the BIOS update reboot.
- Polling for about 12 minutes showed no SSH over `atlas`; LAN `10.0.0.145:22` and Tailscale `100.71.165.80:22` were also unreachable.
- This may still be normal during BIOS flash/reboot; do not power-cycle while the update may be in progress.

**Next up:**
- Continue waiting and observe the physical server front panel/fans/activity.
- When Atlas returns, verify BIOS with `sudo dmidecode -s bios-version` and post-reboot health checks.

## 2026-06-10 - Confirm Atlas BIOS 2.9.0 update

**What we did:**
- Confirmed Atlas returned after the BIOS update reboot.
- Verified LAN SSH on `10.0.0.145:22` and Tailscale SSH on `100.71.165.80:22`.
- Verified `eno1` retained `10.0.0.145/24` and default route via `10.0.0.1`.
- Verified internet with `ping 1.1.1.1` and `curl -I https://github.com` returning HTTP `200`.
- Verified `systemctl --user --failed` reports `0 loaded units listed`.
- Verified expected Docker services are running, including `ollama`, `open-webui`, `atlas-grafana`, `benchmark-exporter`, and `leantime`.
- Drew confirmed `sudo dmidecode -s bios-version` is now `2.9.0` and `sudo dmidecode -s bios-release-date` is `12/06/2019`.

**Where we stopped:**
- Atlas BIOS update is complete and confirmed.
- Atlas is healthy after the BIOS update.

**Next up:**
- Proceed to P40 install prep when the card arrives.
- After installing the P40, verify with `lspci | grep -i -E "nvidia|tesla|3d|vga"` before driver work.

## 2026-06-10 - Save P40 install runbook and update task spec

**What we did:**
- Added `docs/p40-install-2026-06-10-runbook.md` with simple arrival-day steps for shutdown, physical P40 install, first boot, driver check, Ollama/GPU validation, after-P40 benchmarks, and evidence capture.
- Updated `data/task-sync/atlas-ai-operating-system-leantime.json` so completed prep work is reflected in the repo-backed Leantime source:
  - `Phase 0 - Verify Atlas access layer` -> `Done`
  - `Phase 0 - Run pre-P40 LLM benchmark baseline` -> `Done`
  - `P40 install day - Validate hardware and driver` -> `Ready`
  - `P40 install day - Run same-model and larger-model benchmarks` -> `Ready`
- Validated the JSON spec after editing.

**Where we stopped:**
- Live Leantime has not yet been synced from the updated repo spec.
- No GitHub issue was closed for BIOS/P40 prep because the tracked P40 items are primarily in the Atlas AI OS Leantime spec.

**Next up:**
- When ready, run the Atlas Leantime sync for `data/task-sync/atlas-ai-operating-system-leantime.json`.
- Use `docs/p40-install-2026-06-10-runbook.md` when the P40 arrives.

## 2026-06-11 - Answer pre-P40 benchmark evidence lookup

**What we did:**
- Checked infra and LLM benchmark session logs for the June 10 pre-P40 benchmark evidence.
- Confirmed the real Atlas baseline was previously located at `/home/drew/benchmarks/results/benchmark_atlas_20260609_093237.json`.
- Confirmed local inspection copies exist at `C:\tmp\benchmark_atlas_20260609_085941.json` and `C:\tmp\benchmark_atlas_20260609_093237.json`.
- Summarized the full baseline file: models `qwen2.5:14b` and `llama3.2:3b`, context lengths `512, 1024, 2048, 4096, 8192`, two runs per model/context.

**Where we stopped:**
- The pre-P40 baseline information is visible and does not need to be rerun just to establish before-state evidence.
- The committed repo dashboard SQLite still only contains synthetic sample rows; the real baseline evidence is on Atlas plus copied JSON in `C:\tmp`.

**Next up:**
- After P40 install, run the same-model and larger-model after-P40 benchmarks from `docs/p40-install-2026-06-10-runbook.md`.
- Consider copying or committing a summarized evidence note so the real baseline is not only in Atlas/C:\tmp.

## 2026-06-11 - Reconfirm pre-P40 LLM benchmark evidence

**What we did:**
- Re-read the infra and llm-bench-dashboard session logs for the P40 prep benchmark context.
- Confirmed the local dashboard SQLite/results data is synthetic sample data, not the real baseline.
- Confirmed the real pre-P40 Atlas baseline JSON is still copied at `C:\tmp\benchmark_atlas_20260609_093237.json` and recorded on Atlas as `/home/drew/benchmarks/results/benchmark_atlas_20260609_093237.json`.
- Summarized the baseline: timestamp `2026-06-09T09:32:37.653281`, host `http://localhost:11434`, models `qwen2.5:14b` and `llama3.2:3b`, contexts `512, 1024, 2048, 4096, 8192`, `runs_per_model` 2.

**Where we stopped:**
- The pre-P40 evidence is visible locally and in the infra logs; no after-P40 benchmark was checked in this turn.

**Next up:**
- Use `/home/drew/benchmarks/results/benchmark_atlas_20260609_093237.json` as the before-P40 comparison file when running the post-install same-model and larger-model benchmarks.

## 2026-06-11 - Evaluate final local model downloads before P40 install

**What we did:**
- Checked Atlas disk, memory, and installed Ollama models before the P40 install.
- Confirmed Atlas has about 314 GB free on `/` and 251 GiB RAM available, so model storage is not the limiting factor.
- Confirmed installed local Ollama models: `llama3.2:1b`, `llama3.2:3b`, `qwen2.5:14b`, `gemma4:latest`, `nomic-embed-text:latest`, and `llama3.1:70b`.
- Recommended a small final pre-P40 local-only expansion instead of downloading many overlapping models.

**Where we stopped:**
- No new models were downloaded in this turn.
- Recommended candidates for a final pre-P40 spectrum are a 7/8B general model, a 7B code model, and a 32B model likely to show the P40's practical value.

**Next up:**
- If approved, pull the selected models on Atlas and run a bounded pre-P40 local benchmark before physically installing the P40.

## 2026-06-11 - Run final local pre-P40 benchmark spectrum

**What we did:**
- Added `docs/pre-p40-final-local-llm-spectrum-benchmark.md` with exact local-only pre/post P40 reproduction steps.
- Updated `docs/p40-install-2026-06-10-runbook.md` to point at the final spectrum runbook for the post-install repeat.
- Pulled three additional local Ollama models on Atlas: `llama3.1:8b`, `qwen2.5-coder:7b`, and `qwen2.5:32b`.
- Confirmed all benchmark traffic was local Ollama at `http://localhost:11434`; no paid cloud API credits were used.
- Started a broad 7-model, 5-context, 2-run sweep, then stopped it after about 39 minutes because `gemma4:latest` was consuming too much install-day time.
- Replaced that with a tiered repeatable test:
  - Core spectrum: `llama3.2:1b`, `llama3.2:3b`, `llama3.1:8b`, `qwen2.5-coder:7b`, `qwen2.5:14b` at contexts `512, 2048, 4096`, one run each.
  - Large smoke: `gemma4:latest`, `qwen2.5:32b`, `llama3.1:70b` at context `512`, one run each.
- Saved and validated Atlas JSON results:
  - `/home/drew/benchmarks/results/benchmark_atlas_pre_p40_core_spectrum_20260611.json`
  - `/home/drew/benchmarks/results/benchmark_atlas_pre_p40_large_smoke_20260611.json`
- Copied both JSON files to `C:\tmp\`.
- Key CPU baseline results:
  - `llama3.2:1b`: about `23-25 tok/s`.
  - `llama3.2:3b`: about `11-13 tok/s`.
  - `llama3.1:8b`: about `5-6 tok/s`.
  - `qwen2.5-coder:7b`: about `5.5-6.4 tok/s`.
  - `qwen2.5:14b`: about `3.0-3.6 tok/s`.
  - `gemma4:latest` smoke: `5.77 tok/s`.
  - `qwen2.5:32b` smoke: `1.79 tok/s`.
  - `llama3.1:70b` smoke: timed out, recorded as `0` successful runs.

**Where we stopped:**
- Final local pre-P40 benchmark evidence exists on Atlas and in `C:\tmp`.
- The documented post-P40 repeat commands are ready.

**Next up:**
- Install the P40.
- After driver/Ollama GPU validation, rerun the post-P40 commands from `docs/pre-p40-final-local-llm-spectrum-benchmark.md` with the post-P40 output filenames.

## 2026-06-11 - Add pre-P40 benchmark results HTML

**What we did:**
- Added `docs/pre-p40-final-local-llm-results.html` as a standalone local report page for the final pre-P40 local Ollama benchmark results.
- The page presents both completed benchmark tests:
  - Core spectrum from `benchmark_atlas_pre_p40_core_spectrum_20260611.json`.
  - Large smoke from `benchmark_atlas_pre_p40_large_smoke_20260611.json`.
- Included KPI tiles, horizontal throughput bars, result tables, file paths, and the replication contract for post-P40 comparison.
- Confirmed the inline JavaScript parses with `node --check`.
- Attempted a Playwright/browser render, but the Windows sandbox could not start the browser process.

**Where we stopped:**
- HTML report exists at `docs/pre-p40-final-local-llm-results.html`.
- Visual browser verification was not completed because the browser runtime failed in the sandbox.

**Next up:**
- Open `docs/pre-p40-final-local-llm-results.html` in a normal browser for a quick visual check.
- After the P40 install, add the post-P40 results to the same report or create a paired post-P40 comparison page.

## 2026-06-11 - Correct benchmark report run counts and graphs

**What we did:**
- Rebuilt `docs/pre-p40-final-local-llm-results.html` after noticing the first version only showed the final pre-install run and therefore made every row look like `runs = 1`.
- Added the June 9 two-run Atlas baseline from `benchmark_atlas_20260609_093237.json`.
- Kept the final core spectrum and large smoke tests as separate sections so run counts remain per source JSON, not merged silently.
- Added graph panels:
  - June 9 baseline throughput curves.
  - Final core spectrum throughput bars.
  - Overlap check for models/contexts present in both benchmark passes.
  - Large smoke throughput bars with the 70B timeout preserved.
- Added an explicit “Why Some Runs Are 1” explanation.
- Confirmed the inline JavaScript parses with `node --check`.

**Where we stopped:**
- The report file is updated and should show the corrected structure after browser refresh.

**Next up:**
- Refresh the in-app browser tab currently open to `file:///C:/Users/drewb/Documents/GitHub/infra/docs/pre-p40-final-local-llm-results.html`.

## 2026-06-11 - Add graph axis labels and final core curves

**What we did:**
- Updated `docs/pre-p40-final-local-llm-results.html` so graph panels have explicit X/Y labels.
- Added a `Final Core Curves` line chart showing all five final core models across context lengths.
- Kept `June 9 Baseline Curves` and `Overlap Check` as limited-scope two-model views because only `llama3.2:3b` and `qwen2.5:14b` exist in both the June 9 baseline and final core data.
- Confirmed the old benchmark HTML pages still exist:
  - `infra/llm-bench-dashboard/dashboard/index.html`
  - `infra/llm-bench-dashboard/site/index.html`
- Confirmed the updated inline JavaScript parses with `node --check`.

**Where we stopped:**
- The current report should show axis labels and a five-model final core curve after browser refresh.

**Next up:**
- If we want the old dashboard look with real data, export/convert the Atlas JSON files into the old dashboard's `window.LLM_BENCH_DATA` format.

## 2026-06-11 - Locate Grafana-style LLM benchmark dashboard

**What we did:**
- Confirmed the dark two-panel dashboard screenshot is the live Grafana benchmark dashboard, not the beige static pre-P40 HTML report.
- Found the canonical Grafana routes and metadata in `llm-bench-dashboard/config/source-of-truth.json`.
- Confirmed supporting docs in `llm-bench-dashboard/docs/grafana-dashboard.md`.
- Confirmed the local static dashboard files still exist at `llm-bench-dashboard/dashboard/index.html` and `llm-bench-dashboard/site/index.html`.

**Where we stopped:**
- The Grafana dashboard URL is `http://atlas:3001/d/llm-benchmarks/llm-inference-benchmarks?orgId=1&from=now-6h&to=now&timezone=browser&refresh=5m`.
- The tailnet URL is `http://atlas.tail401605.ts.net:3001/d/llm-benchmarks/llm-inference-benchmarks?orgId=1&from=now-6h&to=now&timezone=browser&refresh=5m`.

**Next up:**
- Decide whether to keep using live Grafana for that view or restyle the current pre-P40 static HTML report to match the Grafana dashboard look.

## 2026-06-11 - Restore live Grafana benchmark data

**What we did:**
- Diagnosed the empty Grafana benchmark dashboard by checking Grafana, Prometheus, Docker services, scrape targets, and the benchmark exporter.
- Found Grafana was healthy, but `atlas-prometheus` had been cleanly stopped at about `2026-06-10 04:12 EDT` and was still exited.
- Restarted `atlas-prometheus`; verified Prometheus became healthy and all scrape targets were up, including `benchmarks` at `host.docker.internal:9700`.
- Confirmed live Prometheus now returns benchmark data:
  - `benchmark_tokens_per_sec`: 50 series.
  - `benchmark_prompt_latency_ms`: 50 series.
  - `benchmark_total_latency_ms`: 50 series.
  - `benchmark_last_run_timestamp`: 5 series.
- Confirmed Grafana datasource `Prometheus` points to `http://prometheus:9090` and the `llm-benchmarks` dashboard references the live `benchmark_*` metric names.
- Added `docs/llm-benchmark-data-inventory.md` documenting all known benchmark data locations, live telemetry paths, and the Prometheus monitoring gap.
- Corrected `llm-bench-dashboard/config/source-of-truth.json` and `llm-bench-dashboard/site/source-of-truth.js` to use the actual live metric names.

**Where we stopped:**
- Live Grafana should have benchmark data again after refresh.
- Prometheus/Grafana time-series history is missing for roughly `2026-06-10 04:12 EDT` through `2026-06-11 01:30 EDT`; raw benchmark JSON evidence was not lost.

**Next up:**
- After the P40 install, save post-P40 benchmark JSON files beside the existing Atlas results, copy them to `C:\tmp`, and then merge the post-P40 data into the static report and/or Grafana dashboard export.

## 2026-06-11 - Check Atlas disk visibility

**What we did:**
- Checked Atlas disk visibility while investigating why fewer disks appear in Ubuntu than the physical drive count in the PowerEdge.
- Confirmed Linux sees disks presented by `DELL PERC H710P`, not raw physical drive models.
- Confirmed the PCI storage controller is `Broadcom / LSI MegaRAID SAS 2208`, matching the PERC H710P family.
- `lsblk` shows six PERC-presented logical disks: `sda` through `sdf`; four are mounted as data volumes, one is the boot/root disk, and one appears unmounted.

**Where we stopped:**
- The most likely explanation is hardware RAID/virtual disk presentation by the PERC controller.
- Exact physical-slot-to-virtual-disk mapping still needs PERC/iDRAC/BIOS inventory or RAID CLI tooling such as `perccli`, `storcli`, or Dell OpenManage.

**Next up:**
- Before changing disk layout, inspect the PERC virtual disk and physical disk config from iDRAC/System Setup or install/use a read-only RAID CLI.

## 2026-06-11 - Reframe P40 install risk

**What we did:**
- Updated `docs/p40-install-2026-06-10-runbook.md` to frame the Tesla P40 as a reasonable low-cost homelab GPU experiment, not a guaranteed supported Dell configuration.
- Added checks for exact chassis variant, riser/slot layout, dual 750W PSU awareness, passive P40 airflow, and iDRAC/PSU/PCIe warnings.
- Added evidence items for chassis variant, PSU wattage/warnings, and idle/first-load GPU temperature.
- Commented on `DrewBeFree/infra#42` with the corrected install framing.

**Where we stopped:**
- The install plan now matches the current view: the P40 is not a bad purchase, but Atlas should be treated as an R720/R720xd-family controlled install with power/fit/firmware/cooling stop points.

**Next up:**
- If installing tonight, do only the physical install, boot/driver/Ollama validation, and post-P40 benchmark. Do not combine with RAID/storage changes.

## 2026-06-11 - Assess pre-P40 benchmark sufficiency

**What we did:**
- Reviewed the saved Atlas benchmark artifacts in `C:\tmp` and the infra benchmark docs.
- Confirmed the local Atlas evidence includes:
  - June 9 single-context two-run baseline: 4 successful runs.
  - June 9 context sweep two-run baseline: 20 successful runs.
  - June 10 final core spectrum: 15 successful runs.
  - June 10 large smoke: 2 successful runs plus one recorded 70B timeout.
- Compared overlapping CPU baseline points between the June 9 context sweep and June 10 final spectrum:
  - `llama3.2:3b`: about `+3%` to `+9%`.
  - `qwen2.5:14b`: about `-2%` to `-5%`.

**Where we stopped:**
- The pre-P40 data is sufficient for an install-day before/after comparison. It is not publication-grade statistical benchmarking, but it is enough to detect the expected GPU step-change.

**Next up:**
- Proceed with the P40 install only as a controlled hardware experiment, then run the documented post-P40 benchmark immediately after GPU validation.

## 2026-06-12 - Add P40 install snapshot capture

**What we did:**
- Added `scripts/atlas-p40-snapshot.sh` to capture timestamped P40 install/load evidence.
- Copied the script to Atlas at `/home/drew/benchmarks/atlas-p40-snapshot.sh`.
- Took the first snapshot after confirming Ollama had loaded `llama3.2:3b` onto the Tesla P40.
- Snapshot directory:
  - `/home/drew/benchmarks/results/p40-install-snapshots/20260612_011936_post-ollama-gpu-first-load`
- Captured `nvidia-smi`, GPU query CSV, Docker/Ollama state, Ollama tags, Prometheus health/queries, Grafana health, and Ollama VRAM metrics.

**Where we stopped:**
- User-level snapshot data is working. `dmesg` capture needs sudo if kernel logs are required.
- Latest snapshot symlink points to `/home/drew/benchmarks/results/p40-install-snapshots/latest`.

**Next up:**
- Run the snapshot script before and after each post-P40 benchmark phase, plus after any thermal/load concern.

## 2026-06-12 - Update P40 benchmark HTML reports

**What we did:**
- Updated `docs/pre-p40-final-local-llm-results.html` so it now presents both the pre-P40 baselines and the first post-P40 core spectrum run.
- Added post-P40 core graphs, a pre/post speedup graph, a post-P40 results table, updated KPIs, and a note that the large-model post smoke test is still pending.
- Added `scripts/build-llm-dashboard-results.js` to regenerate the static dashboard data from the saved JSON benchmark files in `C:\tmp`.
- Regenerated `llm-bench-dashboard/dashboard/results.js` with real aggregate data for four benchmark files and 43 result rows, replacing the synthetic sample export.
- Updated `docs/llm-benchmark-data-inventory.md` with the post-P40 JSON/log files, snapshot directories, dashboard data generator, and Ollama VRAM metric names.

**Where we stopped:**
- The static HTML report and both dashboard HTML files now have access to the post-P40 core benchmark data.
- Syntax checks passed for the report inline script, dashboard scripts, generated results export, and generator script.
- In-app browser verification was attempted but the browser runtime failed to start under the current sandbox.

**Next up:**
- Run the post-P40 large smoke test tomorrow, copy the raw JSON to `C:\tmp`, rerun `node scripts/build-llm-dashboard-results.js`, and add the post-large section to the static report.

## 2026-06-12 - Add benchmark interpretation and Hermes guidance

**What we did:**
- Added a plain-English per-test recap section to `docs/pre-p40-final-local-llm-results.html`.
- Added model color badges and compact model labels throughout the recap cards and benchmark tables.
- Added model-use recommendations for Hermes monitoring, routing, coding help, general chat, heavier synthesis, and large-model experiments.
- Added a Hermes utilization/monitoring section explaining current Grafana/Prometheus coverage, Ollama VRAM metrics, Hermes proxy access, and remaining GPU telemetry work.

**Where we stopped:**
- The report now explains what each benchmark means, which models to use when, and how Hermes should consume the results operationally.
- Script parse and DOM-stub render checks passed for the new recap, recommendation, and Hermes sections.
- In-app browser automation still fails under the sandbox, so visual verification should be done by refreshing the open file tab.

**Next up:**
- After the post-P40 large smoke test, update the recommendation cards with 32B/70B post-P40 results and decide whether either belongs in Hermes as a default profile.

## 2026-06-12 - Version and visualize P40 report for Grafana

**What we did:**
- Saved a pre-redesign version copy at `docs/versions/pre-p40-final-local-llm-results.2026-06-12-before-visual-grafana-redesign.html`.
- Updated `docs/pre-p40-final-local-llm-results.html` with a new quick-read visual board: P40 verdict, pre/post lift bars, status lights, and three model decision cards.
- Added `scripts/build-grafana-p40-summary.js`.
- Generated Grafana import files:
  - `llm-bench-dashboard/grafana/atlas-p40-benchmark-summary.json`
  - `llm-bench-dashboard/grafana/atlas-p40-benchmark-summary-api-payload.json`
- Updated Grafana docs to describe UI import, API import, Prometheus datasource mapping, and the current auth status.

**Where we stopped:**
- HTML and Grafana JSON validation passed.
- Atlas Grafana health is reachable and reports database `ok`.
- Live Grafana import was attempted, but `admin:admin` is not valid anymore, so importing the dashboard requires the current Grafana admin password or an API token.

**Next up:**
- Import `atlas-p40-benchmark-summary.json` through `http://atlas:3001/dashboard/import`, selecting the `Prometheus` datasource, or POST the API payload with valid Grafana credentials.

## 2026-06-12 - Import Atlas P40 summary Grafana dashboard

**What we did:**
- Incorporated the dashboard critique into the Grafana P40 summary direction: a phone-friendly Atlas Capacity row, AI Ops panels, storage/network rows, and explicit missing-metric callouts.
- Updated `scripts/build-grafana-p40-summary.js` to generate a 20-panel dashboard with:
  - Atlas Capacity, Ollama Health, Loaded Models, VRAM Used, RAM Used, Hotspot Temp, Power Draw, and Root Disk.
  - Compute saturation, benchmark throughput, prompt latency, VRAM by model, disk IO, and network throughput.
  - Text panels for missing GPU/request metrics and Hermes operating rules.
- Regenerated:
  - `llm-bench-dashboard/grafana/atlas-p40-benchmark-summary.json`
  - `llm-bench-dashboard/grafana/atlas-p40-benchmark-summary-api-payload.json`
- Imported the dashboard into live Atlas Grafana with UID `atlas-p40-summary`.
- Verified live Grafana API reports title `Atlas P40 Benchmark Summary`, 20 panels, and URL `/d/atlas-p40-summary/atlas-p40-benchmark-summary`.
- Checked the new Prometheus expressions against Atlas; all tested expressions returned successfully.

**Where we stopped:**
- Live P40 summary dashboard is available at `http://atlas:3001/d/atlas-p40-summary/atlas-p40-benchmark-summary`.
- GPU compute utilization, NVIDIA GPU temperature, NVIDIA GPU power, requests/min, queue depth, and average response time are still missing because the corresponding exporters/metrics are not wired yet.

**Next up:**
- Add a DCGM or `nvidia-smi` exporter for P40 GPU temp/util/power, then add Ollama request-flow metrics so the AI Ops row can show requests/min, queue depth, and response time.

## 2026-06-12 - Define missing AI Ops exporter path

**What we did:**
- Reviewed the P40 summary dashboard gap around missing AI Ops metrics.
- Confirmed the static infra repo currently has the Grafana dashboard/report artifacts, but not the live Atlas Docker compose or Prometheus scrape config.
- Identified the clean implementation split:
  - Add NVIDIA/P40 telemetry first via a host-side `nvidia-smi` exporter or DCGM exporter.
  - Add request-flow metrics second through an Ollama-facing proxy or caller instrumentation.

**Where we stopped:**
- Grafana can show these panels once Prometheus has the metrics, but Prometheus still needs GPU telemetry and request-flow scrape targets.

**Next up:**
- Deploy the GPU exporter on Atlas, add the Prometheus scrape job, update the Grafana dashboard panels, then decide whether Hermes/Open WebUI/benchmarks should route through an instrumented Ollama proxy for requests/min, queue depth, and response time.

## 2026-06-12 - Prepare P40 follow-up for tomorrow

**What we did:**
- Updated `docs/llm-benchmark-data-inventory.md` with the live P40 summary dashboard URL, missing AI Ops metrics, candidate metric names, implementation order, and tomorrow morning checklist.
- Updated `llm-bench-dashboard/docs/grafana-dashboard.md` with the two-pass plan for P40 GPU telemetry first and Hermes/Ollama request-flow metrics second.
- Added `docs/p40-next-morning-checklist-2026-06-13.md` as the dedicated morning run sheet.
- Updated `docs/p40-install-2026-06-10-runbook.md` so it reflects the actual post-install state: P40 installed, driver working, Ollama GPU access working, and core post-P40 benchmark complete.
- Scheduled a one-time thread wake-up for 2026-06-13 at 8:00 AM local time with the morning kickoff list.

**Where we stopped:**
- Atlas is ready for the next work block, but continuous NVIDIA GPU telemetry is not in Prometheus/Grafana yet and the post-P40 large-model smoke test is still pending.

**Next up:**
- Tomorrow morning, open `docs/p40-next-morning-checklist-2026-06-13.md`, verify services, take a `morning-prep` snapshot, add the NVIDIA exporter, update Grafana GPU panels, then run the large smoke test after telemetry is visible.

## 2026-06-12 - Compare Atlas and Alienware CPUs

**What we did:**
- Queried Atlas with `lscpu` and confirmed it has dual Intel Xeon E5-2643 v2 CPUs: 2 sockets, 6 cores per socket, 12 total cores, 24 threads, 3.50 GHz base, 3.80 GHz max.
- Queried Alienware from Windows and confirmed it has an Intel Core i9-14900F: 24 cores, 32 logical processors.
- Checked saved LLM benchmark JSON files in `C:\tmp` and confirmed Alienware CPU inference was roughly 4x faster than Atlas CPU inference on `qwen2.5:14b`, while Atlas with the P40 is now faster than Alienware CPU for the tested local LLM workloads.

**Where we stopped:**
- CPU-wise, Alienware is clearly faster. Atlas wins for local LLM serving only when the Tesla P40 is used.

**Next up:**
- Treat Atlas CPU as service/server capacity and the P40 as the AI accelerator; do not expect Atlas CPU-only workloads to outperform Alienware.

## 2026-06-12 - Add CPU comparison to P40 report and wiki

**What we did:**
- Saved a report version snapshot at `docs/versions/pre-p40-final-local-llm-results.2026-06-12-before-cpu-comparison.html`.
- Added a `CPU Reality Check` section to `docs/pre-p40-final-local-llm-results.html` explaining that Alienware has the faster CPU, while Atlas wins for local LLM serving because of the Tesla P40.
- Added a dedicated wiki page at `wiki/docs/infrastructure/atlas-p40-cpu-comparison.md`.
- Linked the new page from `wiki/mkdocs.yml`, `wiki/docs/infrastructure/index.md`, and `wiki/docs/infrastructure/machines.md`.
- Updated `wiki/docs/infrastructure/machines.md` and `alienware-vs-poweredge.md` so they no longer claim Atlas has no GPU or that inference stays on Alienware.

**Where we stopped:**
- HTML inline JavaScript parses successfully.
- MkDocs build could not run in this sandbox because neither PATH Python nor bundled Python has `mkdocs` installed.
- Structural checks confirmed the new wiki page exists, the MkDocs nav references it, and stale P40-absent wording was removed from the touched docs.

**Next up:**
- When back on Atlas or a dev shell with the wiki venv, run `mkdocs build --strict` from `infra/wiki`, then deploy the wiki so `http://atlas/wiki/` shows the new comparison page.

## 2026-06-12 - Re-orient on homelab next steps

**What we did:**
- Reviewed the homelab memory log and parent infra session log to locate the active Atlas/P40 workstream.

**Where we stopped:**
- The freshest steps are in the parent infra repo: P40 is installed and working, the core benchmark is recorded, but continuous NVIDIA GPU telemetry and the post-P40 large-model smoke test are still pending.

**Next up:**
- Continue from `docs/p40-next-morning-checklist-2026-06-13.md`: verify services, take a `morning-prep` snapshot, add NVIDIA GPU telemetry to Prometheus/Grafana, run the large smoke test, then update the reports and wiki.

## 2026-06-12 - Summarize Atlas P40 completion status

**What we did:**
- Re-read the P40 next-morning checklist, P40 install runbook, and latest infra session entries to summarize the current completion state.

**Where we stopped:**
- P40 physical install, NVIDIA driver validation, Ollama GPU access, live P40 summary dashboard import, and the core post-P40 benchmark are complete.
- The remaining gap is to add continuous NVIDIA GPU telemetry to Prometheus/Grafana before the next heavy benchmark, then run and publish the post-P40 large-model smoke test.

**Next up:**
- Verify services, take a `morning-prep` snapshot, add the NVIDIA exporter and Prometheus scrape job, update Grafana GPU panels, run the large smoke test, regenerate dashboard/report data, and deploy the wiki update.

## 2026-06-12 - Re-scope P40 follow-up requirements

**What we did:**
- Clarified that the remaining P40 follow-up items are mostly optional once NVIDIA and Ollama GPU acceleration are already working.

**Where we stopped:**
- The P40 is operational. Continuous GPU telemetry remains useful for monitoring and safe long-running workloads, but the large-model smoke test, JSON copy, dashboard/report regeneration, wiki deploy, and request-flow metrics are not required for basic success.

**Next up:**
- Prioritize telemetry if Atlas will run sustained local LLM workloads. Defer the benchmark/report/wiki/request-metrics work unless a stronger evidence trail or polished documentation is needed.

## 2026-06-12 - Add optional P40 follow-ups to GitHub backlog

**What we did:**
- Created GitHub backlog issues in `DrewBeFree/infra` for the remaining optional Atlas/P40 follow-ups:
  - `infra#46` - Add Atlas P40 GPU telemetry to Prometheus and Grafana.
  - `infra#47` - Run optional post-P40 large-model smoke test and update report.
  - `infra#49` - Build and deploy Atlas P40 CPU comparison wiki update.
  - `infra#48` - Add Hermes and Ollama request-flow metrics.

**Where we stopped:**
- The P40 install itself remains considered successful. Remaining work is now parked as explicit GitHub backlog instead of being treated as required completion work.

**Next up:**
- Prioritize `infra#46` when ready to harden Atlas monitoring; leave the benchmark/report/wiki/request-metrics issues until there is a reason to polish or extend observability.
## 2026-06-14 - Recall Grafana VRAM follow-up

**What we did:**
- Re-read the infra memory and repo session logs around the Atlas P40/Grafana work.
- Confirmed the remembered Grafana add-on was the NVIDIA/P40 telemetry exporter work, not a separate VRAM-only panel.

**Where we stopped:**
- The P40 summary dashboard already has Ollama VRAM metrics/panels; the remaining Grafana gap is continuous GPU telemetry from a host-side `nvidia-smi` exporter or DCGM exporter.

**Next up:**
- If continuing the work, deploy the GPU exporter on Atlas, add the Prometheus scrape job, update Grafana panels, then run the large-model smoke test once telemetry is visible.
## 2026-06-14 - Add Atlas P40 GPU telemetry to Grafana

**What we did:**
- Added `scripts/atlas-nvidia-smi-exporter.py`, a small Prometheus exporter for `nvidia-smi` P40 metrics.
- Added `scripts/atlas-nvidia-smi-exporter.service` and deployed it on Atlas as the enabled/active user service `atlas-nvidia-smi-exporter.service`.
- Updated Atlas Prometheus at `/home/drew/monitoring/prometheus.yml` with scrape job `nvidia_gpu` targeting `host.docker.internal:9701`, then restarted `atlas-prometheus`.
- Verified Prometheus returns `nvidia_gpu_scrape_success`, GPU utilization, NVIDIA temperature, power draw, memory used/total, and memory-utilization metrics.
- Updated `scripts/build-grafana-p40-summary.js`, regenerated the P40 Grafana JSON/API payload, and imported the live dashboard at `http://atlas:3001/d/atlas-p40-summary/atlas-p40-benchmark-summary`.
- Verified live Grafana API reports 25 panels and includes the new P40 VRAM, GPU utilization, GPU temperature, GPU power, and P40 telemetry panels.
- Updated the P40 docs and snapshot script; deployed the snapshot script to Atlas.
- Captured a post-telemetry snapshot at `/home/drew/benchmarks/results/p40-install-snapshots/20260613_224306_post-gpu-telemetry`.

**Where we stopped:**
- Continuous NVIDIA/P40 telemetry is live in Prometheus and Grafana.
- The exporter is enabled and active under user systemd, and `drew` has `Linger=yes` so the service can return after reboot.
- The only snapshot warning was the known non-sudo `dmesg` permission failure.
- Local validation passed for the Grafana generator, JSON parsing, and Python exporter compile.

**Next up:**
- Run the post-P40 large-model smoke test now that GPU telemetry is visible.
- Optionally add Hermes/Ollama request-flow metrics for requests/minute, queue depth, and response time.
