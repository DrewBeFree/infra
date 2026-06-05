# Leantime Template Hotfixes

These are local hotfixes for Leantime 3.8.0 template errors seen on Atlas.

The running container was patched on 2026-06-05 for:

- `tickets/editMilestone` new milestone modal: `currentMilestone` was null.
- `tickets/showList`: `$groupBy` was undefined.
- `tickets/showKanban`: `$groupId` was undefined in swimlane header rendering.

Apply after recreating the `leantime` container:

```sh
bash scripts/leantime-hotfixes/apply.sh
```

