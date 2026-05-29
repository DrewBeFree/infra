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

**Tech**: Vite + Svelte 5 + Threlte (Three.js)  
**Status**: v0.14.0 ready for user review (PR #52, not yet merged)

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

## Summary

| Project | Change | Version | Status |
|---------|--------|---------|--------|
| UHaul Planner | Auto-pack, 3D polish, mobile UX, PWA banner | v0.14.0 | PR #52 pending review |
| LLM Debate Union | Custom persona prompts | v0.3.8 | Merged to main |
| Daily Planner | Voice dictation, ideas tab, task categories | Latest | Live |
| Ollama Monitoring | Production monitoring stack | — | Ready to deploy |
| Lead Gen Agent | Implementation plan & roadmap | Draft | Phase 1 ready |

**Next Steps**:
1. Deploy Ollama monitoring to Atlas
2. Review UHaul PR #52 and merge v0.14.0
3. Test LLM debates with custom personas
4. Clarify 6 lead gen agent questions, start Phase 1 POC
