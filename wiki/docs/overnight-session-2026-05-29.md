# Overnight Session 2026-05-29 — Multi-Project Update

This document summarizes significant features and improvements shipped across multiple projects during the overnight session of **May 29, 2026**.

---

## UHaul Load Planner — v0.14.0

**Auto-Pack + Mobile Polish**

### New Features

- **Auto-Pack Feature** — Click the 📦 Auto-Pack button to automatically arrange all items using a guillotine-based 3D bin packing algorithm. The algorithm:
  - Sorts items by volume (largest first)
  - Respects constraints (height, fragility, weight)
  - Places items efficiently along the truck floor
  - Accounts for wheel wells and internal obstacles
  
- **Mobile UX Improvements**:
  - Input hints in the Add/Edit modal (e.g., "e.g., 36 inches")
  - Auto-focus on the first empty field when modal opens
  - Toast warning when truck weight exceeds 90% of capacity

- **3D Camera Enhancements**:
  - Smooth easing animation on camera reset (Re-center button ⌖)
  - Auto-framing when switching between trucks
  - Improved visual feedback for truck changes

- **iOS PWA Installation**:
  - Install prompt for iOS Safari users on first visit
  - One-tap "Add to Home Screen" for full-screen app experience
  - Dismissible via localStorage

- **Camera Scanning Research** ⚠️ **(Planning/Documentation only — not yet implemented)**
  - Comprehensive guide documenting 5 approaches for auto-capturing item dimensions via device camera
  - Approaches analyzed: Web Camera API, WebXR, ML Detection, Native Bridge, LiDAR
  - Includes pros/cons matrix, implementation difficulty, accuracy/latency tradeoffs, and Phase 1 recommendations
  - Document: `CAMERA_SCANNING_OPTIONS.md` (ready to review; decision point before Phase 1 coding)

**Tech**: Vite + Svelte 5 + Threlte (Three.js)  
**Status**: v0.14.0 ready for user review (PR #52, not yet merged)
- ✅ **Implemented & Testable**: Auto-pack, mobile UX polish (hints + auto-focus + weight warning), 3D camera easing, iOS PWA banner
- 📋 **Planned/Documented (Not Yet Coded)**: Camera scanning research guide, mobile UX improvements roadmap

---

## LLM Debate Union — v0.3.8

**Custom Persona System Prompts**

### New Features

- **Persona Customization Modal** — Click the 🎭 PERSONAS button to customize system prompts for all 6 debate personas:
  - Override default prompts with custom instructions
  - Save per-session in localStorage
  - View default prompts side-by-side
  - Reset individual personas or all at once

- **Dynamic Prompt Application** — Custom prompts automatically apply to all debates in the session, enabling:
  - Persona style tuning (e.g., "make Claude more sarcastic")
  - Argument approach experimentation
  - Topic-specific specialization

**Tech**: Svelte + Claude/OpenAI/Gemini/Ollama APIs  
**Status**: v0.3.8 merged to main, ready for testing with real debates

---

## Daily Planner — Voice + Ideas + Categories

**Voice Dictation + New Ideas Tab**

### New Features

- **Voice Dictation** — 🎤 button on Tasks, Groceries, and Ideas inputs:
  - Web Speech API for natural speech-to-text
  - Create tasks, grocery items, and ideas hands-free
  - Available across all major tabs

- **Task Categories** — Color-coded badges for organizing tasks:
  - Personal, Urgent, Work, and more
  - Visual separation of task types
  - Stored in Supabase `tasks` table

- **Ideas Tab** — New free-form capture space:
  - Quick note-taking for fleeting ideas
  - Auto-timestamped entries
  - Full CRUD: add, delete, view all
  - Real-time Supabase sync across devices

**Tech**: Svelte + Supabase + Web Speech API  
**Status**: All features shipped and live

---

## Infrastructure — Ollama Monitoring + Lead Gen Agent Plan

**Production Monitoring Stack**

### Ollama Monitoring (Complete)

- **Prometheus Exporter** — Custom `ollama-exporter` collecting model metrics (inference time, tokens/sec, VRAM, queue depth)
- **Grafana Dashboards** — Pre-built dashboards:
  - **Ollama Overview** — Model inference performance, queue health, error tracking
  - Built-in alerting rules for slow inference or queue overload
- **Docker Compose Stack** — Complete monitoring setup: Prometheus + Grafana + Node Exporter + cAdvisor + Smart Health Exporter
- **Status**: Production-ready, can deploy to Atlas immediately

### Facebook/Monday.com Lead Gen Agent (Implementation Plan)

- **Comprehensive 12–16 hour roadmap** (`facebook-monday-lead-gen-agent.md`):
  - **Phase 1** (4–6h): POC — single end-to-end cycle (scrape → classify → generate → post)
  - **Phase 2** (2–3h): Refinement — improve accuracy, test at scale
  - **Phase 3** (2–4h): Automation — 24/7 cron monitoring, metrics dashboard
  - **Phase 4** (4–6h): Scaling — multi-platform support, CRM integration, A/B testing

- **Tech Stack**: Playwright + Claude API + SQLite + Homelab Cron
- **Deployment**: Homelab (recommended, cost-free) or AWS Lambda ($5–10/month)

- **Ready for**: Phase 1 POC execution once 6 refinement questions are clarified

---

## Testing Checklist

Use this section to validate that all overnight improvements work correctly.

### UHaul Load Planner (v0.14.0)

**Auto-Pack Feature**
- [ ] Add 5–10 items of varying sizes to a truck layout
- [ ] Click 📦 Auto-Pack button
- [ ] Verify items are arranged without overlaps
- [ ] Verify large items are prioritized (placed first)
- [ ] Verify items don't clip through wheel wells or internal obstacles
- [ ] Test on different truck sizes (Cargo Van, 10', 15', 20', 26')

**Mobile UX — Implemented Features**
- [ ] Open Add Item modal on mobile
- [ ] Verify first input field (item name) auto-focuses
- [ ] Type into the width field and verify hint text is visible (e.g., "e.g., 36 inches")
- [ ] Add an item with weight near 90% of truck capacity
- [ ] Verify weight warning toast appears

**Mobile UX — Future Roadmap** 📋 *(Planning Document — Review, Not Test)*
- [ ] Read `MOBILE_UX_IMPROVEMENTS.md` in uhaul-load-planner/ (in PR #52 or dev/overnight-improvements branch)
- [ ] Review 6 pain points identified (e.g., keyboard navigation, input validation, accessibility)
- [ ] Review phased recommendations (Phase 1 quick wins vs Phase 2 longer-term improvements)
- [ ] **Decision Point**: Which Phase 1 quick wins to prioritize? (guides mobile UX iteration)

**3D Camera**
- [ ] Open 3D view with items loaded
- [ ] Click Re-center button (⌖) multiple times
- [ ] Verify smooth easing animation (not snappy/instant)
- [ ] Switch between two different trucks (Cargo Van → 26')
- [ ] Verify camera auto-frames to show entire new truck with smooth animation
- [ ] Verify truck model updates correctly

**iOS PWA (if on iOS Safari)**
- [ ] Visit app on iOS Safari for first time
- [ ] Verify install prompt appears (usually bottom banner or notification)
- [ ] Dismiss the prompt
- [ ] Verify prompt doesn't reappear (stored in localStorage)
- [ ] Manually add to home screen: Share → "Add to Home Screen"
- [ ] Verify app launches fullscreen without browser chrome

**Camera Scanning Research** 📋 *(Planning Document — Review, Not Test)*
- [ ] Read `CAMERA_SCANNING_OPTIONS.md` in uhaul-load-planner/ (in PR #52 or dev/overnight-improvements branch)
- [ ] Review the 5 approaches: Web Camera API, WebXR, ML Detection, Native Bridge, LiDAR
- [ ] Review pros/cons matrix for each approach
- [ ] Note the recommended Phase 1 approach (likely Web Camera API for immediate availability)
- [ ] Understand tradeoffs: accuracy vs device support vs complexity
- [ ] **Decision Point**: Which approach to implement first? (This decides the next feature phase)

### LLM Debate Union (v0.3.8)

**Custom Persona Prompts**
- [ ] Click 🎭 PERSONAS button in header
- [ ] Modal opens showing all 6 personas
- [ ] Click on one persona's textarea, enter a custom prompt (e.g., "Be very sarcastic")
- [ ] Click "Save" button
- [ ] Verify system message confirms save in the feed
- [ ] Start a new debate with that persona
- [ ] Verify persona's speech reflects the custom prompt tone
- [ ] Click "View Default" to see original prompt
- [ ] Click "Reset" on one persona, verify it returns to default
- [ ] Click "Reset All Prompts", verify all personas reset
- [ ] Verify custom prompts persist across debate sessions (localStorage)

**Debate with Custom Prompts**
- [ ] Customize Claude persona: "Only respond in haikus"
- [ ] Run a debate with Claude as a speaker
- [ ] Verify Claude's responses follow the custom constraint

### Daily Planner

**Voice Dictation**
- [ ] Navigate to Tasks tab
- [ ] Click 🎤 button next to task input
- [ ] Speak a task (e.g., "Buy milk")
- [ ] Verify task text appears in input field
- [ ] Press Enter to add task
- [ ] Repeat for Groceries tab and Ideas tab

**Task Categories**
- [ ] Add a new task
- [ ] Verify category dropdown/selector appears (Personal, Urgent, Work, etc.)
- [ ] Assign a category to a task
- [ ] Verify colored badge appears on the task
- [ ] Switch categories on an existing task
- [ ] Verify badge color updates
- [ ] Reload the page
- [ ] Verify category persists after reload (Supabase sync)

**Ideas Tab**
- [ ] Click on Ideas tab
- [ ] Add an idea by typing and pressing Enter
- [ ] Verify idea appears in list with timestamp
- [ ] Add another idea via voice (click 🎤)
- [ ] Verify both ideas appear with timestamps
- [ ] Delete an idea by clicking ×
- [ ] Verify idea is removed
- [ ] Open app on another device
- [ ] Verify ideas sync in real-time (Supabase)

**Data Sync**
- [ ] Open app on two devices simultaneously
- [ ] Add a task on Device 1
- [ ] Verify task appears on Device 2 within a few seconds
- [ ] Delete an idea on Device 2
- [ ] Verify idea is removed on Device 1

### Infrastructure — Ollama Monitoring

**Deployment Readiness**
- [ ] Read `ollama-monitoring-setup.md` in infra/docs/528/
- [ ] Verify all 10 config files are present in `docs/528/`
- [ ] Review `COPY_PASTE_DEPLOY.md` for deployment steps
- [ ] (When ready) SSH to Atlas and run deployment steps
- [ ] Verify Prometheus is up: `curl http://localhost:9090` (or Tailscale IP)
- [ ] Verify Grafana is up: `curl http://localhost:3001` (or Tailscale IP)
- [ ] Open Grafana dashboard and verify metrics are populating

### Facebook/Monday.com Lead Gen Agent

**Plan Review**
- [ ] Read `facebook-monday-lead-gen-agent.md` in infra/homelab/
- [ ] Review Phase 1 scope (4–6 hours)
- [ ] Verify all 4 implementation tasks have code sketches
- [ ] Confirm 3 deployment options are documented
- [ ] Read through the 6 refinement questions at the end
- [ ] (When ready) Answer the 6 questions to clarify Phase 1 scope

---

## Summary

| Project | ✅ Implemented | 📋 Planned/Documented | Version | Status |
|---------|---|---|---------|--------|
| UHaul Planner | Auto-pack, 3D camera easing, mobile UX polish (hints, auto-focus, weight warning), iOS PWA banner | Camera scanning (5 approaches), Mobile UX roadmap (6 pain points) | v0.14.0 | PR #52 pending review |
| LLM Debate Union | Custom persona prompts | — | v0.3.8 | Merged to main |
| Daily Planner | Voice dictation, ideas tab, task categories | — | Latest | Live |
| Ollama Monitoring | — | Production monitoring stack (docker-compose, dashboards, exporters) | — | Ready to deploy |
| Lead Gen Agent | — | Implementation plan & roadmap (4 phases, 12–16 hours) | Draft | Phase 1 ready |

**Next Steps**:
1. Deploy Ollama monitoring to Atlas
2. Review UHaul PR #52 and merge v0.14.0
3. Test LLM debates with custom personas
4. Clarify 6 lead gen agent questions, start Phase 1 POC
