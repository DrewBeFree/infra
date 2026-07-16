# World Portal PIN Rotation — 2026-07-15

## Summary

Rotated the `world.drewbefree.com` PIN gateway credentials on Atlas by updating the local-only secret files. The new PIN value is intentionally not recorded in git.

## Files changed locally

- `/home/drew/.config/world-portal-pin.pin`
- `/home/drew/.config/world-portal-pin.env`

## Backups created locally

- `/home/drew/.config/world-portal-pin.pin.bak-20260715-202507`
- `/home/drew/.config/world-portal-pin.env.bak-20260715-202507`

## Service

- Restarted: `world-portal-pin.service`
- Verified active after restart.

## Verification

Local backend `http://127.0.0.1:8137`:

- Wrong PIN returned `401`.
- New PIN returned `303` and issued `drew_world_session` cookie.
- Authenticated GET returned `200` with `text/html` world page content.

Public URL `https://world.drewbefree.com/`:

- Returned `403 Forbidden` before the PIN page during verification, so the public Cloudflare path was not fully testable from this session.


## Follow-up: 404 on `/ecosystem/world.html`

After the PIN rotation, the public gateway accepted the PIN but old/stale URLs under `/ecosystem/...` returned `404` because the world-specific gateway uses `/opt/homelab-status-dashboard/ecosystem` as its document root. Patched `internal-portal/pin_gateway.py` to strip a leading `/ecosystem/` prefix before resolving static files.

Verification after restart:

- `/` -> `200`
- `/world.html` -> `200`
- `/ecosystem/` -> `200`
- `/ecosystem/world.html` -> `200`
- `/ecosystem/ecosystem.json` -> `200`

Targeted test suite remained green: `31/31`.


## Follow-up: mobile drill-down world UI

Updated `internal-portal/world.html` to make the world view easier to navigate on mobile and more node-oriented:

- Added a `World → category → item` drill panel with breadcrumbs.
- Category taps zoom/focus the map region.
- Item taps highlight the node and open the detail drawer.
- Added stronger 3D globe/layer styling through `globe-shell`, perspective, elevated regions, and selected-node elevation.
- Hid the active-site strip on mobile so it does not fight with drill navigation.
- Deployed updated `world.html` to `/opt/homelab-status-dashboard/ecosystem/world.html`.

Verification:

- Public `https://world.drewbefree.com/` returned the new drill markers after PIN login.
- Browser interaction verified category drill and item detail drawer.
- Headless 390x844 screenshot generated at `/tmp/world-mobile-drill.png` for mobile visual inspection.
- Targeted test suite passed: `31/31`.
- Extracted module script syntax check passed.


## Follow-up: desktop focus correction

Corrected issues found after desktop review:

- Initial world state now has all categories collapsed.
- Fixed `focusRegion()` coordinate math so category clicks do not jump the world to the top-left/out of position.
- Strengthened visible 3D styling with more pronounced globe shell, rings, shadows, elevated regions, and selected/focused depth.

Verification:

- Targeted portal test suite passed: `31/31`.
- Extracted module syntax check passed.
- Public `world.drewbefree.com` contained the deployed markers.
- Browser console verification after clicking Apps Island showed `initiallyOpen: []`, `appsFocused: true`, `appsOpen: true`, `outOfPosition: false`.
- Desktop visual inspection confirmed Apps Island remained visible and no longer jumped to the top-left.


## Follow-up: desktop top-left indicator overlap

Moved the desktop legend panel lower so it no longer overlaps the protected-world note.

Verification after deploy:

- Targeted portal suite passed: `31/31`.
- Extracted module syntax check passed.
- Live browser geometry check showed `overlap: false` between `.hosted-note` and `.legend-panel`.


## Follow-up: revert failed 3D styling only

Reverted the heavy pseudo-3D styling back to the original softer globe treatment while preserving the mobile/drilldown/focus work.

Kept:

- `World → category → item` drill panel and breadcrumbs.
- All categories collapsed on initial load.
- Fixed category focus coordinate math.
- Mobile drill navigation.
- Top-left legend/note overlap fix.

Changed:

- Removed world-frame perspective and `translateZ`/`rotateX` region effects.
- Disabled the added `.globe-shell` overlay.
- Restored the original `ocean-glow` style.
- Kept a subtle focused-region scale/highlight without the broken 3D effect.

Verification after deploy:

- Targeted portal suite passed: `31/31`.
- Extracted module syntax check passed.
- Public marker verification confirmed drilldown preserved and heavy-3D markers removed.
- Browser geometry check after clicking Apps Island: `initiallyOpen: []`, `appsOpen: true`, `outOfPosition: false`, `topLeftOverlap: false`, `globeShellDisplay: none`, `worldPerspective: none`.


## Follow-up: expanded category collapse behavior

Changed region headers to behave as true toggles:

- Clicking a collapsed category opens/focuses it.
- Clicking the same expanded category collapses it.
- Keyboard Enter/Space activation also toggles.
- Dragging a region no longer triggers an accidental toggle on pointer release.

Verification after deploy:

- Targeted portal suite passed: `31/31`.
- Extracted module syntax check passed.
- Live browser event verification on Apps Island showed `before: false`, `afterFirst: true`, `afterSecond: false`.


## Follow-up: bottom active links vs minimap overlap

Adjusted the desktop active-site strip so it no longer spans underneath the bottom-left zoom controls or bottom-right minimap.

Verification after deploy:

- Targeted portal suite passed: `31/31`.
- Extracted module syntax check passed.
- Live browser geometry check showed `activeOverlapsMinimap: false` and `activeOverlapsControls: false`.


## Follow-up: desktop-first simplification

After mobile/iPad iterations proved inaccurate, shifted `world.html` back toward desktop-first behavior instead of optimizing the tablet/phone layout right now.

Changes:

- Moved the drill navigation to a fixed left desktop panel.
- Kept item detail drawer on the right.
- Hid the redundant protected-world note to avoid left-panel collisions.
- Changed the mobile breakpoint from `900px` to `768px` so iPad/tablet widths retain the desktop-oriented layout.
- Kept bottom active links clear of both zoom controls and minimap.

Verification after deploy:

- Targeted portal suite passed: `31/31`.
- Extracted module syntax check passed.
- Live browser geometry check showed:
  - `hostedDisplay: none`
  - `activeMini: false`
  - `activeControls: false`
  - `drillDrawer: false`
  - `appsOutOfPosition: false`
  - `media768: false` at desktop viewport


## Follow-up: fix incorrect world links

Fixed world drawer links defaulting to GitHub when a real runtime/site exists.

Changes:

- Updated `protectedUrlFor()` in `internal-portal/world.html` to choose the most specific protected route across all matching routes instead of the first route. This prevents broad `http://atlas/` portal aliases from stealing `http://atlas/wiki/...` links.
- Added `https://sell.drewbefree.com/` as the `selling-shit` runtime URL in `ecosystem.json`, so Selling Shit opens the actual site before GitHub.
- Added regression checks for route-specific protected rewrites and Selling Shit's live URL.

Live verification examples:

- Selling Shit `Open` → `https://sell.drewbefree.com/`
- Infra `Open` → `https://wiki.drewbefree.com/wiki/`; secondary portal link → `https://portal.drewbefree.com/ecosystem/`; GitHub remains secondary.
- Internal Ecosystem Portal `Open` → `https://portal.drewbefree.com/ecosystem/`
- Ecosystem World `Open` → `https://world.drewbefree.com/`
- No bad `portal.drewbefree.com/ecosystem/wiki...` links found in the rendered page.

Verification:

- `python3 -m json.tool ecosystem.json` passed.
- Targeted portal suite passed: `32/32`.
- Extracted module syntax check passed.
- Deployed both `world.html` and `ecosystem.json` to `/opt/homelab-status-dashboard/ecosystem/`.


## Closeout: desktop-first world portal and link fixes

Host/worktree: `/home/drew/GitHub/infra`
Branch: `dev`
Remote before commit: `origin/dev`

Outcome:

- Kept the world portal desktop-first after mobile/iPad layout attempts proved inaccurate.
- Preserved useful interaction work: drill panel, breadcrumbs, collapsed initial state, click-to-collapse categories, original softer globe styling, and corrected focus behavior.
- Fixed `/ecosystem/...` compatibility in the PIN gateway.
- Fixed protected route rewriting so more specific routes win over broad aliases.
- Added the Selling Shit live URL so the drawer opens `https://sell.drewbefree.com/` before GitHub.
- Added/updated regression coverage and README deploy command.

Commands run:

```bash
git status --short --branch
git log --oneline -5
git diff --stat
./internal-portal/deploy.sh
python3 -m json.tool ecosystem.json >/tmp/ecosystem-json-check.json
node --test internal-portal/portal.test.mjs
python3 <temporary module syntax check for internal-portal/world.html>
python3 <source/deployed/http verification for world.html and ecosystem.json>
```

Observed results:

```text
./internal-portal/deploy.sh
# Wrote internal-portal/changelog.html
# Internal ecosystem portal synced to /opt/homelab-status-dashboard/ecosystem

node --test internal-portal/portal.test.mjs
# pass 32/32

node --check extracted world module
# node_check_exit=0

source/deployed/http verification
# source/deployed/http verification passed
```

Live browser smoke test against `https://world.drewbefree.com/` after PIN unlock:

```text
Selling Shit Open -> https://sell.drewbefree.com/
Infra Open -> https://wiki.drewbefree.com/wiki/
Bad portal/wiki rewrites -> []
Active links do not overlap minimap or controls.
```

Safety notes:

- The actual PIN value is not recorded here.
- Deployed via the official `internal-portal/deploy.sh` path after manual copies made during iteration.
- Unrelated untracked files/directories were left unstaged: `internal-portal/launcher-clean.html`, `logs/session-2026-07-09-monitoring-backups.md`, and `monitoring/`.
- The current design intentionally treats mobile/iPad as secondary; desktop is the verified target.

Next recommended step:

- If more incorrect links are found, fix them in `ecosystem.json` as source-of-truth URL data first, then rerun `./internal-portal/deploy.sh` and the portal test suite.
