# Leantime Template Hotfixes

These are local hotfixes for Leantime 3.8.0 template errors seen on Atlas.

The running container was patched on 2026-06-05 for:

- `tickets/editMilestone` new milestone modal: `currentMilestone` was null.
- `tickets/showList`: `$groupBy` was undefined.
- `tickets/showKanban`: `$groupId` was undefined in swimlane header rendering.

The project visibility hotfix was added on 2026-06-08 for:

- `Projects::getProjectHierarchyAssignedToUser()`: owners/admins should see all globally accessible projects in the menu even when they do not have a row in `zp_relationuserproject`.
- Regular users keep the default assignment-based menu behavior.

Apply after recreating the `leantime` container:

```sh
bash scripts/leantime-hotfixes/apply.sh
bash scripts/leantime-hotfixes/apply-project-visibility.sh
```
