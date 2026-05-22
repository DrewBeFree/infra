# Machines

## Alienware

| Spec | Value |
| --- | --- |
| OS | Windows 11 |
| GPU | High-end (primary inference/gaming) |
| Role | Dev workstation, GPU workloads |

### Best Uses

- Ollama / Open WebUI (GPU inference)
- OpenClaw frontend/testing
- VS Code + WSL development
- Whisper realtime transcription
- Gaming, OBS
- Agent development

### Why Alienware

- Better GPU → faster inference
- Better desktop experience
- Easier experimentation
- Already configured for dev

---

## Atlas (PowerEdge R720xd)

| Spec | Value |
| --- | --- |
| OS | Ubuntu Server 24.04.4 LTS |
| CPU | Dual Xeon (24 cores) |
| RAM | 256 GB |
| Storage | ~7 TB usable |
| Hostname | `atlas` |
| Local IP | 10.0.0.105 (static via Netplan) |
| Tailscale | 100.71.165.80 |
| iDRAC7 | 10.0.0.38 (static) |
| SSH | `ssh drew@10.0.0.105` |
| GPU | None (K80 sold — inference stays on Alienware) |

### Best Uses

- Docker + Portainer
- ChromaDB (vector DB)
- Syncthing (peer-to-peer file sync)
- Watchdog / ingestion pipelines
- Scheduled jobs / automation
- Grafana dashboards
- Plex media server
- Slack integrations
- OpenClaw gateway (production)
- Wiki + status dashboard

### Why Atlas

- Always-on (survives desktop sleep/reboot/gaming)
- Massive RAM for in-memory workloads
- Stable infrastructure host
- Separated from interactive desktop

---

## Migration Order

When moving services from Alienware to Atlas:

1. Docker + Portainer
2. ChromaDB
3. Syncthing
4. Watch folders
5. Ingestion scripts
6. OpenClaw gateway
7. Grafana / dashboards
8. Whisper batch jobs
9. Slack / Make automations
