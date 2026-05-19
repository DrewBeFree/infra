# Dashboard Redesign Spec — 2026-05-19

## Scope

Visual redesign of `homelab-status-dashboard/index.html`, `data.js`, and `render.js` to apply:
1. Pro Blue color scheme + Space Grotesk font
2. Live indicator in the header
3. Timestamp support in session log display (including same-day multi-session handling)

---

## 1. Color Scheme — Pro Blue

**Palette:**
- Page bg: `#f0f4ff`
- Header bar: `#1e3a5f` (dark navy, full-width)
- Cards/panels: `#ffffff` with `box-shadow: 0 1px 4px rgba(30,58,95,0.12)`
- Accent primary: `#3b82f6` (blue)
- Accent secondary: `#8b5cf6` (purple)
- Accent tertiary: `#06b6d4` (cyan)
- Gradient divider: `linear-gradient(90deg, #3b82f6, #8b5cf6, #06b6d4)`
- Text primary: `#1e3a5f`
- Text secondary: `#3b4a6b`
- Text dim: `#94a3b8`
- Border: `#e0e7ff`
- Tag bg: `#eff6ff`, tag text: `#3b82f6`, tag border: `#bfdbfe`
- Done item text: `#94a3b8` with strikethrough

**Typography:**
- Font: `Space Grotesk` (weights 300, 400, 600, 700)
- Replace all `Share Tech Mono`, `Orbitron`, `Exo 2` references
- Title in header: uppercase, weight 700, `#fff`
- Title accent word: `#60a5fa`

**Header:**
- Full-width dark navy bar (`#1e3a5f`), no separate border
- Left: eyebrow line (small, `#93c5fd`) + title
- Right: live indicator + refresh button
- A 2px gradient divider (`blue → purple → cyan`) sits below the header bar

**Panels:**
- White cards, rounded corners (`border-radius: 8px`), subtle shadow
- Panel title: small caps, `#3b82f6`, no border-bottom (use spacing instead)
- Backlog accordion: white cards, same shadow, `border-radius: 8px`

---

## 2. Live Indicator

**Location:** Header, right side, left of the refresh button.

**States:**
- `fetching` — dot pulses amber (`#f59e0b`), label "FETCHING…"
- `live` — dot pulses green (`#4ade80`) with glow, label "LIVE"
- `error` — dot solid red (`#f87171`), label "ERROR"

**Implementation:**
- Add `id="live-indicator"` span in HTML next to `#last-fetched`
- `render.js` calls `setLiveState('fetching' | 'live' | 'error')` helper
- Called at start of `init()` (fetching), on success (live), on catch (error)
- CSS: `@keyframes pulse` animates `opacity` + `transform: scale`

---

## 3. Session Timestamps

**SESSION_LOG.md format change:**
- New format: `## YYYY-MM-DD HH:MM — context`
- Old format (`## YYYY-MM-DD — context`) remains supported; displayed as date-only
- Going forward all session log entries include time

**Parser changes (`data.js`):**
- `fetchSessionLog()` returns an array of session objects (not just one)
- Each session object: `{ date, time, context, did, stopped, next }`
- `time` is null if not present in the header
- Group returned sessions by date; `fetchSessionLog()` returns `{ today: [...], earlier: [...] }`
  - `today` = all sessions whose date matches today's date, sorted newest-first
  - `earlier` = most recent session from a prior date (for reference)
- If `today` is empty, fall back to the single most recent session from `earlier`

**Render changes (`render.js`):**
- Most recent session (first in array): rendered fully expanded
- Same-day earlier sessions: rendered as `<details>` with `<summary>` showing the timestamp + context, body showing full content — collapsed by default
- If only one session today (or falling back to a prior date): no accordion, just the expanded view
- Timestamp shown next to date: `2026-05-19 · 14:32` format; date-only if no time

---

## Files Changed

| File | Changes |
|------|---------|
| `index.html` | Full CSS rewrite (Pro Blue), add live indicator markup |
| `render.js` | Live indicator state helper, updated session render for multi-session + timestamps |
| `data.js` | `fetchSessionLog()` returns array grouped by today/earlier, parse time from header |

No changes to `config.js` or `config.example.js`.

---

## 4. Backlog Grouped by Type

`repos.json` already has a `type` field on each repo (`app`, `site`, `agent`, `infrastructure`). The backlog section renders repos grouped under labeled section headers rather than a flat list.

**Section order:** Infrastructure → Apps → Sites → Agents

**Section labels** (small caps, styled like the existing `.section-label` dividers):
- `infrastructure` → "Infrastructure"
- `app` → "Apps"
- `site` → "Sites"
- `agent` → "Agents"

**Implementation:**
- `fetchAllBacklogs()` receives the full repo list (which includes `type`); attach `type` to each backlog result
- `renderBacklogAccordion()` groups backlogs by type, renders a section label before each group
- Groups with no BACKLOG.md results are omitted entirely
- Accordion behavior (expand/collapse per repo) unchanged

**Files changed:** `data.js` (pass type through), `render.js` (grouping + section labels)

---

## Out of Scope

- Backend changes
- Persistence of session timestamps in historical entries (old entries show date-only gracefully)
- Auto-refresh on a timer
