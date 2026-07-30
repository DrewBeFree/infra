# Hermes WebUI / SSH from Alienware — How It Works

**Date:** 2026-07-30  
**Context:** Obsidian Sync + Syncthing + Atlas backups setup complete. Hermes running on Atlas.

> **Note:** All operational and infrastructure runbooks live under `/logs-and-docs/`.  
> This directory is the canonical source that should be kept in sync with the visible wiki.

## Runtime Location

- Hermes (all tools, file operations, terminal commands) **always executes on Atlas**.
- The WebUI browser tab (whether opened on Alienware or any other machine) is only a client.
- Connection is over Tailscale (`100.71.165.80:9119`) or LAN.
- SSH sessions from Alienware (`ssh drew@100.71.165.80`) land on Atlas.

## Vault & File Access

- Hermes sees the **Atlas copy** of the vault at `/home/drew/wiki`.
- This is the authoritative filesystem for any agent work (reading/writing notes, running scripts, etc.).
- The local copy on Alienware (`C:\Users\drewb\Documents\Obsidian\wiki`) is **not** used by Hermes.

## Sync Layers

| Layer              | Devices                          | Purpose                              | Notes |
|--------------------|----------------------------------|--------------------------------------|-------|
| Obsidian Sync      | Alienware + iPhone               | Live cloud sync for Obsidian app     | Paid subscription, remote vault `wiki` |
| Syncthing          | Alienware ↔ Atlas                | File-level filesystem sync           | Verified 100% complete, idle |
| Atlas Snapshots    | Atlas only                       | Independent point-in-time backups    | Hourly cron, 90-day / 250-snapshot retention |

## Practical Effect

- When you interact with Hermes (WebUI or SSH), it operates against the Atlas vault.
- Changes made in Obsidian on Alienware flow to Atlas via Syncthing.
- Changes made via Hermes on Atlas flow to Alienware via Syncthing.
- Obsidian Sync keeps the iPhone and Alienware Obsidian apps in sync with each other independently of the filesystem layer.

## Summary

The three-device model is stable:

- **iPhone + Alienware Obsidian app** → Obsidian Sync
- **Alienware filesystem** ↔ **Atlas filesystem** → Syncthing
- **Hermes** (WebUI or SSH) → always talks to Atlas copy + its snapshots

No action required on Atlas for Obsidian Sync. The paid subscription is fully utilized on the two devices that actually run the Obsidian client.

## Related Automation

- Hourly card-link checker: `/home/drew/GitHub/infra/scripts/check-card-links.sh`
  - Cron: `0 * * * *`
  - Logs: `/home/drew/backups/card-link-checks/`
  - Currently monitors: `https://world.drewbefree.com/launcher.html`, `https://world.drewbefree.com/`, `https://wiki.drewbefree.com/wiki/`