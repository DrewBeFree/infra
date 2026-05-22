# Versioning

How version numbers are managed and propagated across the ecosystem.

## Version Format

`v{major}.{minor}.{patch} · YYYY-MM-DD`

Three components: **Major Feature . Minor Feature . Bug/Hotfix**

Example: `v1.5.2 · 2026-05-22`

## Rules

| Change type | Bump | Example |
| --- | --- | --- |
| Bug fix / hotfix | Patch (third number) | v1.5.2 → v1.5.3 |
| Minor feature | Minor (second number) | v1.5.2 → v1.6.0 |
| Major feature | Major (first number) | v1.5.2 → v2.0.0 |
| Command Center only | No bump needed | — |

Always update the date to today's date.

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
2. **Terminal scan line** — the `scan ./apps` line in the `.terminal` div must match card versions exactly (e.g. `linksy v0.2.2`)
3. **`state.html`** — update version + date for the same app row

## Propagation Checklist

When you ship a change to a mapped app:

1. Bump the version in the app itself (if applicable)
2. Update the Command Center card (`index.html`)
3. Update `state.html` with matching version + date
4. Commit both the app change and Command Center update in the same push
