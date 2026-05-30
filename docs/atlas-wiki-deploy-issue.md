# Atlas Wiki Deploy Issue

## Problem

The wiki deploy script (`./wiki/deploy.sh`) fails on atlas with:

```
ERROR: catalog changed. Commit & push wiki/docs/projects via your branch workflow, then re-run.
```

Root cause: The deploy script generates the project catalog by reading `MANUAL.md` from local clones of all repos, but atlas doesn't have the repos cloned locally.

## Current State

- `repos.json` lists all 17 repos (apps, sites, agents)
- But none of these repos are cloned on atlas (all show as "in repos.json but not on disk")
- The script generates 0 project pages instead of 20
- Catalog generation fails

## Solution Options

1. **Clone all repos on atlas** (current approach)
   - Need: `git clone` all repos into the correct paths
   - Pros: Minimal script changes
   - Cons: Storage overhead, sync maintenance

2. **Fetch MANUAL.md directly from GitHub** (recommended)
   - Script reads from raw.githubusercontent.com instead of disk
   - Pros: No local clones needed, always current
   - Cons: Requires MANUAL.md to be in repo root (currently true)

3. **Run catalog generation locally, commit results**
   - Catalog committed to repo instead of generated on atlas
   - Pros: Simple, reliable
   - Cons: Manual step required for each change

## Related

- Wiki deploys locally (dev machine) without issue
- Atlas can build the wiki once catalog is generated
- This only blocks the final "push to atlas" step

## Status

**Blocked by**: Need to either clone repos on atlas or refactor script to fetch MANUAL.md from GitHub
