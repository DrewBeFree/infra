# Alienware vs PowerEdge — Workload Split

## Hardware

### Alienware
- Windows 11
- Better GPU (primary inference/gaming machine)

### PowerEdge R720xd
- Ubuntu Server 24.04.3 LTS (kernel 6.8.0-90)
- GNOME desktop installed (server/workstation hybrid)
- SSH enabled
- Tailscale installed
- 256 GB RAM
- Dual Xeon
- ~7 TB usable storage

---

## What Should Stay on the Alienware

### Best Uses
- Ollama
- Open WebUI
- OpenClaw frontend/testing
- VS Code
- agent development
- GPU inference
- Whisper realtime jobs
- gaming
- OBS

### Why
- Better GPU
- Better desktop experience
- Faster inference
- Easier experimentation
- Already configured

---

## What Should Move to the PowerEdge

### Best Uses
- ChromaDB
- OpenClaw gateway
- Syncthing
- Watchdog
- ingestion pipelines
- scheduled jobs
- dashboards
- Grafana
- Plex
- Slack integrations
- automation services

### Why
- Always-on system
- Massive RAM
- Stable infrastructure
- Separated from gaming/reboots
- Better for background services

---

## Decision Rule

> "Does this need to stay alive while the desktop is asleep, rebooting, or gaming?"

- **YES** → PowerEdge
- **NO** → Alienware

---

## Recommended Migration Order

1. Docker + Portainer
2. ChromaDB
3. Syncthing
4. Watch folders
5. Ingestion scripts
6. OpenClaw gateway
7. Grafana/dashboard
8. Whisper batch jobs
9. Slack/Make automations
