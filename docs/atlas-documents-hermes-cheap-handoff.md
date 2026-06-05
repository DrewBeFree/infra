# Atlas Documents + Hermes Cheap Handoff

Date: 2026-06-05

## Purpose

Capture the safe next steps after the Atlas disk triage, personal Documents planning, and Hermes/Claude/dashboard discussion. This is intentionally a handoff/runbook, not an implementation log. Do not migrate Documents or redirect user folders while Drew is asleep.

## Current Storage Facts

- `C:\Users\drewb\Documents` on Alienware is about 62.25 GB across about 97,811 files.
- Atlas has four currently mounted internal data drives that appear usable:
  - `/mnt/data` on `/dev/sdg1`, about 869 GB free.
  - `/mnt/data1` on `/dev/sdf1`, about 869 GB free.
  - `/mnt/data2` on `/dev/sdd1`, about 869 GB free.
  - `/mnt/data3` on `/dev/sde1`, about 869 GB free.
- The old `/mnt/data4` drive is offline. It previously mapped to `/dev/sdc1`; `/dev/sdc` is currently absent.
- PERC/MegaRAID reported `VD 02/2 is now OFFLINE` after the bay reseat.
- `ipmitool sel` showed a fresh reseat event on `Drive Slot / Bay #0xa4` at 2026-06-05 04:24 EDT.
- Older drive fault history exists for `Drive Slot / Bay #0xa0`.
- iDRAC is configured as static `10.0.0.38`, MAC `5c:f9:dd:f5:2f:0e`, but it is not reachable on the LAN from Atlas.
- Both 6 TB WD Reds should be treated as untrusted:
  - `/dev/sdh` failed `mkfs.ext4` with I/O errors and lost writes.
  - `/dev/sdi1` formatted and mounted at `/mnt/wd6tb-b`, but kernel logs later showed ext4 journal errors, hardware errors, and remount read-only behavior.

## Documents Recommendation

Use an internal Atlas data drive for the real Documents share, not either WD Red.

Recommended initial target:

```text
/mnt/data3/documents/drew
```

Rationale:

- The Documents folder is small enough for any healthy internal 931 GB drive.
- Keeping it off the probation WD Red avoids building the new source of truth on unstable media.
- `/mnt/data4` should be excluded until PERC/iDRAC confirms the bay is healthy again.

## Documents Migration Guardrails

Do first:

1. Confirm which internal data drive will hold Documents.
2. Create an Atlas folder such as `/mnt/data3/documents/drew`.
3. Configure SMB share `Documents` pointing to that folder.
4. Copy from Alienware to Atlas with a verification pass.
5. Test from Alienware as a mapped network location.
6. Test from MacBook as `smb://atlas/Documents` or `smb://100.71.165.80/Documents`.
7. Add Google Drive backup with `rclone` after the Atlas copy is stable.
8. Only then decide whether to redirect Windows Documents or use a junction/symlink.

Avoid for now:

- Do not use `/mnt/data4`.
- Do not use `/mnt/wd6tb-b` for Documents.
- Do not redirect `C:\Users\drewb\Documents` until the SMB share and backup have been tested.
- Do not make Google Drive the primary sync location; use it as backup.

## Suggested Documents Commands Later

Atlas folder and ownership:

```bash
sudo mkdir -p /mnt/data3/documents/drew
sudo chown -R drew:drew /mnt/data3/documents
chmod 750 /mnt/data3/documents/drew
```

SMB config shape:

```ini
[Documents]
   path = /mnt/data3/documents/drew
   browseable = yes
   read only = no
   valid users = drew
   create mask = 0660
   directory mask = 0770
```

Validation commands:

```bash
findmnt /mnt/data3
lsblk -f
sudo testparm
```

Windows copy should use `robocopy` with logging and a dry-run/list pass first.

## Hermes / Claude / Dashboard Improvement Direction

Current Hermes doc is a transition plan. The improvement track should make the Atlas assistant stack operational and visible, not just installed.

Recommended approach:

1. **Health-first dashboard**
   - Show Atlas storage status, PERC/iDRAC warnings, mounted shares, backup freshness, and key services.
   - Flag dangerous states such as missing `/mnt/data4`, ext4 errors, WD Red hardware errors, or stale Google Drive backups.

2. **Runbook-backed actions**
   - Each dashboard warning links to a runbook: storage triage, iDRAC recovery, Documents share, rclone backup, Hermes service restart.
   - Actions should start as documented commands, not one-click destructive controls.

3. **Hermes/Claude handoff lane**
   - Hermes should own reminders, summaries, monitoring, and user-facing check-ins.
   - Claude/Codex should own code edits, repo changes, design specs, and implementation plans.
   - Dashboard should expose what each agent is responsible for and where its logs/memory live.

4. **Morning briefing**
   - Generate a compact daily summary: disk status, service status, backup status, open tasks, and recommended next action.
   - First version can be a script that writes Markdown; later it can feed Hermes or the dashboard.

## Next Approval Question

Before implementation, Drew should choose the first improvement slice:

- Storage/Documents safety dashboard first.
- Hermes service hardening first.
- Morning briefing first.

Recommendation: build the storage/Documents safety dashboard first because the current blocker is hardware trust and backup clarity.
