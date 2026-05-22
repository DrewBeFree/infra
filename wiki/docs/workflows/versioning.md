# Versioning

How version numbers are managed and propagated across the ecosystem.

## Version Format

In the Command Center `card-meta`: `v{major}.{minor} · YYYY-MM-DD`

## Rules

| Change type | Version bump |
| --- | --- |
| Bug fix | Increment minor (v0.1 → v0.2) |
| New feature | Increment minor (v0.1 → v0.2) or major if significant |
| Command Center only | No bump needed |

Always update the date to today's date.

## Command Center Updates

When committing changes to any app repo, also update the corresponding card in the Command Center (`apps/drewbefree-command-center/index.html`).

### Card Mapping

| Repo | Card ID | Display Name |
| --- | --- | --- |
| `golf` | APP_003 | Linksy |
| `poker` | APP_001 | Poker Night |
| `uhaul-load-planner` | APP_002 | UHaul Planner |
| `daily-planner` | APP_004 | Daily Planner |

### What to Update

1. **`card-meta`** — version string + date in the card element
2. **Terminal scan line** — the `scan ./apps` line in the `.terminal` div must match card versions exactly (e.g. `linksy v0.2`)
3. **`state.html`** — update version + date for the same app row

## Propagation Checklist

When you ship a change to a mapped app:

1. Bump the version in the app itself (if applicable)
2. Update the Command Center card (`index.html`)
3. Update `state.html` with matching version + date
4. Commit both the app change and Command Center update in the same push
