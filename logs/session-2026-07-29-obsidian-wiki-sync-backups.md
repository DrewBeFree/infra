# Obsidian Wiki Sync + Backups — 2026-07-29

Host/repo: `/home/drew/GitHub/infra`
Branch: `dev`
Commit at start: `4d1f6a0 docs: refresh changelog and fix backup script directory resolution`
Remote: `origin/dev`

## Outcome

Set up evidence-backed local backups for Drew's Obsidian wiki vault on Atlas and verified the Syncthing relationship with Alienware.

Final ownership layout:

```text
Runbook:        /home/drew/GitHub/infra/obsidian/OBSIDIAN_WIKI_BACKUPS.md
Backup script:  /home/drew/GitHub/infra/obsidian/scripts/backup-obsidian-wiki.sh
Cron installer: /home/drew/GitHub/infra/obsidian/scripts/install-obsidian-wiki-backup-cron.sh
Backup root:    /home/drew/backups/obsidian-wiki
Latest symlink: /home/drew/backups/obsidian-wiki/latest
Compat wrapper: /home/drew/bin/backup-obsidian-wiki.sh
```

Live vault paths:

```text
Atlas:     /home/drew/wiki
Alienware: C:\Users\drewb\Documents\Obsidian\wiki
```

## Why this was done

Drew was evaluating Obsidian mobile sync and asked whether the PowerEdge copy made Obsidian Sync's one-month history less concerning. The correct safety model is sync for convenience plus independent snapshots/backups on Atlas, because sync alone propagates accidental deletion/corruption.

Drew then corrected the organization: this belongs in an existing operational home such as `infra`, not scattered as a random `/home/drew/bin` script and a handoff log under World Atlas.

## Commands run

Representative commands actually run:

```bash
# Atlas / Syncthing inspection
systemctl --user status syncthing.service --no-pager || true
ss -ltnp | grep 8384 || true
curl -k -fsS https://127.0.0.1:8384/rest/noauth/health || true
syncthing cli --home=/home/drew/.local/state/syncthing config folders list
syncthing cli --home=/home/drew/.local/state/syncthing config devices list

# Alienware SSH verification
ssh -o BatchMode=yes -o ConnectTimeout=8 -i /home/drew/.ssh/hermes_agent_ed25519 drewb@100.117.87.57 "hostname && whoami"
ssh -o BatchMode=yes -o ConnectTimeout=8 -i /home/drew/.ssh/hermes_agent_ed25519 drewb@100.117.87.57 'powershell -NoProfile -ExecutionPolicy Bypass -Command "...C:\Users\drewb\Documents\Obsidian\wiki..."'

# Syncthing cleanup
systemctl --user reset-failed syncthing.service
systemctl --user start syncthing.service
curl -k -fsS https://127.0.0.1:8384/rest/noauth/health

# Backup install and verification
/home/drew/GitHub/infra/obsidian/scripts/backup-obsidian-wiki.sh
/home/drew/GitHub/infra/obsidian/scripts/install-obsidian-wiki-backup-cron.sh
readlink -f /home/drew/backups/obsidian-wiki/latest
sed -n '1,20p' /home/drew/backups/obsidian-wiki/latest/BACKUP-MANIFEST.txt
crontab -l | grep -F 'obsidian-wiki-backup'
systemctl is-active cron
```

Observed results:

```text
Syncthing folder state: idle
Atlas localFiles/globalFiles: 3501 / 3501
Need files/directories/deletes: 0 / 0 / 0
Pull errors / folder errors: 0 / 0
Alienware device: Drew-AlienWare, connected=true, completion=100

Direct Atlas-vs-Alienware file-list comparison:
local_count=3501
remote_count=3502
only_local_count=0
only_remote_count=1
only_remote_sample=['.stfolder/syncthing-folder-12a435.txt']
size_diff_count=0

Syncthing service after cleanup:
syncthing.service active (running)
/rest/noauth/health => { "status": "OK" }

Latest backup manifest from first verified run:
created_at=2026-07-29T21:10:42.510133+00:00
host=atlas
source=/home/drew/wiki
snapshot=/home/drew/backups/obsidian-wiki/snapshots/20260729-171042
file_count=3502
bytes=179599111

Cron:
active
23 * * * * OBSIDIAN_VAULT_PATH=/home/drew/wiki OBSIDIAN_BACKUP_ROOT=/home/drew/backups/obsidian-wiki OBSIDIAN_BACKUP_RETENTION_DAYS=90 OBSIDIAN_BACKUP_RETENTION_COUNT=250 /home/drew/GitHub/infra/obsidian/scripts/backup-obsidian-wiki.sh >> /home/drew/backups/obsidian-wiki/logs/backup.log 2>&1 # obsidian-wiki-backup
```

## Commit and push

```text
Commit subject: ops: add Obsidian wiki backup runbook
Branch: dev
Remote: origin/dev
Push: completed after final handoff update
```

Final git verification commands:

```bash
git diff --cached --check
git commit --amend --no-edit
git push origin dev
git status --short --branch
git log --oneline -3 --decorate
```

## Safety notes

- No Obsidian source notes were modified.
- No Syncthing delete or overwrite operation was run.
- `.stfolder/` is excluded from Atlas backups because it is Syncthing metadata.
- Existing crontab was backed up before modification.
- Backup snapshots are local to Atlas; they protect against bad sync/delete/corruption propagating across devices, but not against total Atlas disk loss.
- The misplaced World Atlas handoff log was removed after migrating this log to infra.

## Next recommended step

Add off-box encrypted backup for `/home/drew/backups/obsidian-wiki` or `/home/drew/wiki` using `restic` or `borg` if Drew wants protection against Atlas disk loss.
