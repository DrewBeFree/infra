# Leantime Template Hotfixes

These are local hotfixes for Leantime 3.8.0 template errors seen on Atlas.

The running container was patched on 2026-06-05 for:

- `tickets/editMilestone` new milestone modal: `currentMilestone` was null.
- `tickets/showList`: `$groupBy` was undefined.
- `tickets/showKanban`: `$groupId` was undefined in swimlane header rendering.

The project visibility hotfix was added on 2026-06-08 for:

- `Projects::getProjectHierarchyAssignedToUser()`: owners/admins should see all globally accessible projects in the menu even when they do not have a row in `zp_relationuserproject`.
- Regular users keep the default assignment-based menu behavior.

The CSP/htmx hotfix was added on 2026-06-08 for:

- `/projects/showMy` favorite/unfavorite htmx actions failing with `EvalError` because nginx added a second CSP header without `script-src`.
- The app-level CSP already allows `script-src 'unsafe-eval'`; this aligns the nginx header so browsers do not block htmx's JavaScript evaluation path.

The htmx View Transitions hotfix was added on 2026-06-08 for:

- `/projects/showMy` favorite/unfavorite htmx actions logging `AbortError: Transition was skipped`.
- Leantime 3.8.0 enables `window.htmx.config.globalViewTransitions`; this disables the global setting while preserving normal htmx swaps.
- The compiled htmx bundle is served with a one-week cache TTL, so the template includes an Atlas query-string cache bust for the patched bundle.

Apply after recreating the `leantime` container:

```sh
bash scripts/leantime-hotfixes/apply.sh
bash scripts/leantime-hotfixes/apply-project-visibility.sh
bash scripts/leantime-hotfixes/apply-csp-header.sh
bash scripts/leantime-hotfixes/apply-disable-htmx-view-transitions.sh
```
