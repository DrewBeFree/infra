# Clickable Ecosystem Infographic Map Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace the portal accordion sitemap with a clickable hybrid topology-flow infographic map that includes Atlas, Alienware, ecosystem zones, filters, and drawer launch behavior.

**Architecture:** Keep `ecosystem.json` as the source of truth and continue rendering from `app.js`. Replace only the map rendering path and related styles, preserving the page header, stat bar, sidebar, filters, catalog rows, docs, and detail drawer. Use derived map-zone data instead of adding a second data source.

**Tech Stack:** Static HTML, CSS, browser JavaScript modules, Node test runner.

---

### Task 1: Preserve The Approved Design

**Files:**
- Create: `docs/superpowers/specs/2026-06-02-clickable-ecosystem-infographic-map-design.md`
- Create: `docs/superpowers/plans/2026-06-02-clickable-ecosystem-infographic-map.md`

- [ ] **Step 1: Add the spec document**

Create `docs/superpowers/specs/2026-06-02-clickable-ecosystem-infographic-map-design.md` with the approved hybrid map direction, including Alienware as a local compute node.

- [ ] **Step 2: Add this implementation plan**

Create `docs/superpowers/plans/2026-06-02-clickable-ecosystem-infographic-map.md` so the portal map change is recoverable in future sessions.

### Task 2: Replace Sitemap Markup Shell

**Files:**
- Modify: `internal-portal/index.html`

- [ ] **Step 1: Rename the map section semantics**

Change the `#ecosystemMap` section from `class="sitemap-board"` to `class="system-map-board"` and change its ARIA label to `Ecosystem infographic map`.

- [ ] **Step 2: Replace sitemap columns container**

Replace `<div id="sitemapColumns" class="sitemap-columns"></div>` with `<div id="systemMap" class="system-map" aria-live="polite"></div>`.

- [ ] **Step 3: Update the map node template**

Keep `#mapNodeTemplate`, but add a third child `<span class="node-host"></span>` so node chips can show host/topology placement.

### Task 3: Render Hybrid Map Data

**Files:**
- Modify: `internal-portal/app.js`

- [ ] **Step 1: Add host helpers**

Add `itemHosts(item)` and `primaryHost(item)` helpers that derive hosts from `deployTargets`, `host`, URLs, local paths, and known local-dev items.

- [ ] **Step 2: Add zone builders**

Add `systemMapZones(items)` that returns these zones: source, atlas, alienware, public, docs, sensitive. Each zone contains filtered items and an optional primary node.

- [ ] **Step 3: Replace `renderSitemap()` internals**

Keep the `renderSitemap` function name so existing filter calls still work, but render the new `#systemMap` grid instead of accordion columns.

- [ ] **Step 4: Keep node click behavior**

Update `createMapNode(item)` to populate name, meta, host, visibility, and kind, then open the drawer on click.

### Task 4: Style The Infographic

**Files:**
- Modify: `internal-portal/style.css`

- [ ] **Step 1: Replace sitemap-specific layout styles**

Add styles for `.system-map-board`, `.system-map`, `.map-zone`, `.zone-head`, `.zone-body`, `.zone-primary`, `.map-node`, and `.map-rail`.

- [ ] **Step 2: Add responsive behavior**

Make the map grid collapse from the full topology layout to two columns and then one column on mobile.

- [ ] **Step 3: Preserve motion**

Use existing `fade-in-up` and add small stagger-like transitions for map zones and nodes while respecting reduced-motion rules.

### Task 5: Verify

**Files:**
- Modify: `internal-portal/portal.test.mjs`

- [ ] **Step 1: Update static assertions**

Replace assertions for `.sitemap-column.is-open` with assertions for `.system-map`, `.map-zone`, and Alienware-related map helpers.

- [ ] **Step 2: Run tests**

Run `node --test internal-portal/portal.test.mjs`. Expected: all tests pass.

- [ ] **Step 3: Preview in browser**

Open `http://127.0.0.1:8765/internal-portal/`, confirm the map renders, Alienware is visible, filters affect the map, and clicking a map node opens the drawer.
