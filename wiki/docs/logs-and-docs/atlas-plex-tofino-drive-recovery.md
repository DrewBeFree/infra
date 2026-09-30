# Atlas Plex Media Drive Recovery (tofino USB drive corruption)

**Date:** 2026-09-16
**Context:** Plex on Atlas started 404ing on transcode. Traced to I/O errors on the USB backup drive holding the 2.7TB Plex library. Investigated, decided against migrating off the drive, restarted Plex in place.

> **Note:** All operational and infrastructure runbooks live under `/logs-and-docs/`.
> This directory is the canonical source that should be kept in sync with the visible wiki.

## What Happened

Plex Web playback failed with 404s on `/video/:/transcode/universal/session/.../header`. The Plex log showed the real cause: `I/O error` reading media under `/mnt/tofino-media`, transcoder exiting with code 1.

At 09:04 on 2026-09-16, `/dev/sdh` (5.5TB WD drive, dual-bay USB enclosure, USB 2.0) logged a hardware error, an I/O error at a specific sector, UAS aborts, a USB reset, an aborted ext4 journal, and a remount to read-only. SMART showed the drive PASSED with only one Current_Pending_Sector - on paper, a minor issue.

## Root Cause Was Bigger Than SMART Suggested

A plain, read-only `du`/`ls` scan of the drive (mounted `ro,norecovery`, journal never replayed) surfaced **568 EBADMSG / checksum-invalid errors**, not one or two:

| Folder | Errors | Notes |
|---|---|---|
| `media/Apps` | 440 | Pirated software collection, irrelevant to Plex |
| `media/Movies` | 128 | ~14 distinct titles: Blade Runner 2049 (x3 releases), Avatar: Fire and Ash, Alien Covenant, Ballerina, Bugonia, Anaconda (2025), and others |

`dmesg` confirmed the actual mechanism: `EXT4-fs error (device sdh1): ext4_lookup:1864: inode #...: iget: checksum invalid`. That's ext4 metadata checksum corruption from the journal never being replayed (mounted with `norecovery` after the abort) - **not** ongoing physical media failure. No new hardware/USB errors (UAS reset, SCSI I/O error) occurred after the original 09:05 event; the drive itself has been electrically stable since.

Practical effect: a small number of files are permanently unreadable in their current directory entries (`open()` fails with EBADMSG, confirmed by direct `dd`/`stat` tests), but the bulk of the 2.7TB library reads fine.

## Internal Disk Inventory Was Also Incomplete

While evaluating whether to migrate the library onto internal storage instead, the existing docs/assumptions didn't hold up:

- The prior assumption of 6 physical drives behind the PERC H710P was wrong - at least 8 exist (checked megaraid indices 0-7).
- Megaraid physical index 4 (Seagate `ST91000640SS`, serial `9XG0565000009129TRR1`) reports **SMART failure prediction threshold exceeded**, 118 grown defects.
- `/etc/fstab` has a 5th data volume, `/mnt/data4`, that isn't in any current inventory doc. Its device (UUID `96db7ed1-...`) has been completely absent from the system since the 2026-08-30 boot - `systemd` has silently logged "Expecting device..." for it for over two weeks (`nofail` in fstab meant nothing alerted on it).
- The iDRAC (`10.0.0.38`, documented as static in [machines.md](../infrastructure/machines.md)) is unreachable - ARP resolution `FAILED` even from atlas on the same subnet. No `storcli`/`perccli`/`lsscsi` installed, so there's no authoritative physical-disk-to-bay mapping available in-band either. **Atlas currently has no working out-of-band management.**

## Decision

Given a full seedbox copy of the library exists, re-downloading a handful of corrupted titles is cheap compared to a multi-day migration + rescue effort. The migrate-off-`sdh` plan was dropped entirely:

- `sdh1` stays mounted `ro,norecovery` at `/mnt/wd-tofino-backup`, unmodified. No fsck, no journal replay, no writes.
- `/mnt/tofino-media` symlink left pointing at its original target (nothing moved, no repoint needed).
- `plexmediaserver` re-enabled and restarted against the drive as-is.
- Corrupted titles go on a seedbox re-download list rather than attempting `ddrescue` recovery.

## Current State

- Plex: `active`, `enabled`, verified playing back the originally-failing title (*Good Luck Have Fun Don't Die (2026)*, confirmed **not** one of the corrupted files) with no new drive errors.
- `/dev/sdg` (the other drive in the same USB enclosure, 40 Current_Pending_Sector) was never touched - retirement candidate, out of scope.
- `/dev/sda` (930.5G, unpartitioned) was never touched - its physical backing was never conclusively identified, and it showed intermittent `DID_BAD_TARGET` read errors from background `udisks` probes during the investigation. Not used.
- Full findings and command-level detail logged in `~/recovery/LOG.md` on atlas.

## Open Follow-Ups

- Build a clean re-download list by scanning the Plex library and grepping the server log for transcode failures, rather than relying on the partial list found so far.
- Restore iDRAC network reachability (`10.0.0.38`) - out-of-band management is currently down.
- Identify the physical bay for megaraid index 4 (failure prediction exceeded) and decide on replacement/RMA.
- Investigate the missing `/mnt/data4` volume - device absent since 2026-08-30.
- Longer term: consolidate the Plex library onto one large internal or new drive instead of the aging USB 2.0 enclosure.
