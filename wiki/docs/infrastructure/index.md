# Infrastructure

The DrewBeFree homelab runs across two machines connected via Tailscale, with workloads split by a simple decision rule.

## Machines

| Machine | OS | Role | Access |
| --- | --- | --- | --- |
| **Alienware** | Windows 11 | GPU inference, dev, gaming | Local desktop |
| **Atlas** (PowerEdge R720xd) | Ubuntu Server 24.04 | Always-on services | `ssh drew@10.0.0.105` / Tailscale `100.71.165.80` |

## Decision Rule

> "Does this need to stay alive while the desktop is asleep, rebooting, or gaming?"

- **YES** → Atlas (PowerEdge)
- **NO** → Alienware

## Network

- **Local LAN:** 10.0.0.0/24
- **Tailscale mesh:** Alienware + Atlas + mobile devices
- **Atlas services** exposed only via Tailscale — no public ports
- **iDRAC7** (out-of-band management): 10.0.0.38

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    TRUSTED ZONE (Local)                          │
│  • Dev repos (Alienware WSL)                                    │
│  • Ollama + Open WebUI (GPU inference)                          │
│  • OpenClaw gateway (dev)                                       │
│  • VS Code                                                      │
└─────────────────────────────────────────────────────────────────┘
                          │ Tailscale
                          ▼
┌─────────────────────────────────────────────────────────────────┐
│                    ATLAS (Always-on)                             │
│  • Docker + Portainer                                           │
│  • Wiki (this site)                                             │
│  • Status dashboard                                             │
│  • ChromaDB, Syncthing, Plex                                    │
│  • Ingestion pipelines                                          │
│  • Grafana dashboards                                           │
└─────────────────────────────────────────────────────────────────┘
```

## Pages

- [Machines](machines.md) — hardware specs and workload assignments
- [Tools](tools.md) — what each tool does and where it runs
- [Services](services.md) — ports, addresses, and what runs where
