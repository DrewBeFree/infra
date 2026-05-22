# Machines

## Alienware (DREW-ALIENWARE)

| Spec | Value |
| --- | --- |
| OS | Windows 11 Home 64-bit (installed 2025-10-31) |
| Hostname | `DREW-ALIENWARE` |
| Local IP | 10.0.0.91 (Killer E3100G 2.5GbE) |
| Tailscale | 100.117.87.57 |
| SSH | `ssh drew@10.0.0.91` (OpenSSH Server) |
| Role | Dev workstation, GPU workloads |

### Hardware

| Component | Details |
| --- | --- |
| CPU | Intel Core i9-14900F (Raptor Lake, 10nm) |
| Cores | 24 cores / 32 threads (8 P-cores + 16 E-cores) |
| P-core speed | ~5.5 GHz (HT enabled) |
| E-core speed | ~4.3 GHz |
| CPU temp | ~49°C avg |
| RAM | 32 GB DDR5-5600 (2×16 GB SK Hynix, CL46) |
| Motherboard | Alienware 0RF96M (Intel Z690) |
| BIOS | v2.14.0 (2024-12-09) |
| GPU | NVIDIA GeForce RTX 4070 Ti SUPER (Dell, 16 GB VRAM, 4nm) |
| GPU temp | ~46°C |
| GPU driver | 32.0.15.9174 |
| Display | Samsung Odyssey G95C — 5120×1440 @ 60Hz (ultrawide) |
| Storage | 1 TB NVMe (Samsung PM9A1) — 780 GB used / 150 GB free |
| Networking | Killer E3100G 2.5GbE + Intel Wi-Fi 6E AX210 |
| UPS | APC Back-UPS |

### Peripherals

| Device | Model |
| --- | --- |
| Keyboard | Razer BlackWidow |
| Mouse | Razer Basilisk V3 |
| Mouse (BT) | Logitech MX Master 3S |
| Mic | Logitech Blue Yeti Classic |
| Webcam | Logitech C922 Pro |

### Services & Software

| Service | Notes |
| --- | --- |
| Ollama | Local LLM inference, port 11434 |
| WSL | Linux dev environment |
| Syncthing | Peer-to-peer file sync |
| Tailscale | Mesh VPN |
| OpenSSH Server | Remote access |
| Parsec / AnyDesk | Remote desktop |
| NordVPN | VPN client |

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
