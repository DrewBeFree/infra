# Atlas Canonical GitHub Workspace

## Model

- GitHub is the source of truth for all DrewBeFree repositories.
- Atlas is the primary development machine and owns the canonical working tree at `/home/drew/GitHub`.
- Alienware is a client machine for browser access, SSH, SMB, and occasional local testing. It should not hold authoritative repo state.
- `infra/repos.json` is the manifest for the workspace layout.

## Layout

Repos are cloned under the same top-level groups on Atlas and any temporary local checkout:

- `apps/`
- `sites/`
- `agents/`
- `homelab`
- `infra`
- `claude-config`

Run this from Atlas to clone missing repos and fast-forward clean existing repos:

```bash
python3 /home/drew/infra/scripts/clone_manifest.py \
  --manifest /home/drew/infra/repos.json \
  --base /home/drew/GitHub \
  --ssh \
  --pull
```

The sync command does not overwrite dirty or locally-ahead repos. It fetches, fast-forwards clean behind repos, and reports anything needing human review.

## Alienware Pruning Rule

Before removing a local Alienware checkout:

1. Confirm the repo exists in `infra/repos.json`.
2. Confirm the matching Atlas checkout exists under `/home/drew/GitHub`.
3. Confirm the Alienware checkout has no uncommitted, unpushed, or unique local work.
4. Archive first if uncertain; delete only after the archive is no longer needed.

Extra local checkouts that have a GitHub remote should be added to `infra/repos.json` before pruning Alienware.
