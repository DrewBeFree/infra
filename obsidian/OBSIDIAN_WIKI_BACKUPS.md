# Obsidian Wiki Backups

Purpose: protect Drew's Obsidian wiki vault from accidental deletion/corruption that syncs across devices.

## Ownership

Operational owner is the infra repo:

```text
/home/drew/GitHub/infra/obsidian/
```

The live vault and backup data stay outside git:

```text
source vault: /home/drew/wiki
backup root:  /home/drew/backups/obsidian-wiki
```

## Sync topology

```text
Alienware: C:\Users\drewb\Documents\Obsidian\wiki
    ⇄ Syncthing
Atlas:     /home/drew/wiki
    → hourly hardlink snapshots
Atlas:     /home/drew/backups/obsidian-wiki/snapshots/
```

Syncthing is sync, not backup. A bad edit/delete can propagate to all synced devices. These Atlas snapshots are the recovery layer.

## Install or repair cron

```bash
/home/drew/GitHub/infra/obsidian/scripts/install-obsidian-wiki-backup-cron.sh
```

Default cron schedule:

```cron
23 * * * *
```

Default retention:

```text
90 days
250 newest snapshots
```

## Run manually

```bash
/home/drew/GitHub/infra/obsidian/scripts/backup-obsidian-wiki.sh
```

## Verify latest backup

```bash
readlink -f /home/drew/backups/obsidian-wiki/latest
sed -n '1,20p' /home/drew/backups/obsidian-wiki/latest/BACKUP-MANIFEST.txt
du -sh /home/drew/backups/obsidian-wiki
crontab -l | grep -F 'obsidian-wiki-backup'
systemctl is-active cron
```

## Restore pattern

Do not restore over the live vault blindly. Inspect first:

```bash
SNAP=/home/drew/backups/obsidian-wiki/latest
rsync -ain --delete "$SNAP/" /home/drew/wiki/
```

If the dry run is correct, stop Obsidian/Syncthing or pause the Syncthing folder before applying a destructive restore:

```bash
SNAP=/home/drew/backups/obsidian-wiki/latest
rsync -a --delete "$SNAP/" /home/drew/wiki/
```

Then resume Syncthing and verify convergence.

## Safety notes

- `.stfolder/` is excluded from snapshots because it is Syncthing metadata.
- Backup snapshots are local to Atlas. They do not protect against total Atlas disk loss.
- Next durability layer should be encrypted off-box backup via `restic` or `borg`.
