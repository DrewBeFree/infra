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

## Alienware GUI Access

Alienware can run GUI tools while editing the Atlas working tree.

- Atlas path: `/home/drew/GitHub`
- Windows UNC path: `\\atlas\GitHub`
- Windows mapped drive: `G:\`

Open Codex, OpenAI desktop tools, VS Code, and file pickers against `G:\` or `\\atlas\GitHub`, not `C:\Users\drewb\Documents\GitHub`, when the work should happen on Atlas.

The persistent drive mapping is:

```powershell
net use G: \\atlas\GitHub /persistent:yes
```

If `G:` disappears after a Windows/network reset, rerun that command after confirming `\\atlas\GitHub` is reachable.

Git on Alienware also needs to trust the Samba-owned Atlas checkout tree:

```powershell
git config --global --add safe.directory '%(prefix)///atlas/GitHub/*'
```

## Atlas Home Drive

Use `H:` for Atlas home once Samba exposes the home share. The target should be `\\atlas\drew`, backed by `/home/drew`.

```powershell
net use H: \\atlas\drew /persistent:yes
```

As of 2026-06-17, Atlas exposes `GitHub`, `Documents`, `Storage`, and `Easystore`; `\\atlas\drew` is not exposed yet. Enabling it requires a sudo edit on Atlas, either by uncommenting the standard `[homes]` block in `/etc/samba/smb.conf` with write access and `valid users = %S`, or by adding an explicit `[drew]` share for `/home/drew`, then running `testparm` and restarting Samba.

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
