# Services

What runs where, with ports and addresses.

## Notable URLs

| Service | URL | Notes |
| --- | --- | --- |
| Status Dashboard | [http://atlas/](http://atlas/) | Tailscale-only |
| Wiki (this site) | [http://atlas/wiki/](http://atlas/wiki/) | Tailscale-only |
| State page | [https://drewbefree.com/state.html](https://drewbefree.com/state.html) | Public |
| Recap Viewer | [https://recap.drewbefree.com](https://recap.drewbefree.com) | Public |
| Infrastructure Diagram | [https://homelab.drewbefree.com/infrastructure.html](https://homelab.drewbefree.com/infrastructure.html) | Public |

## Atlas Services

| Service | Port | Address | Notes |
| --- | --- | --- | --- |
| SSH | 22 | `drew@10.0.0.105` | Primary access |
| Wiki (this site) | 80 | `http://atlas/wiki/` | Nginx, Tailscale-only |
| Status Dashboard | 80 | `http://atlas/` | Nginx root |
| Portainer | 9443 | `https://atlas:9443` | Docker management UI |
| iDRAC7 | 443 | `https://10.0.0.38` | Out-of-band management |

## Alienware Services

| Service | Port | Address | Notes |
| --- | --- | --- | --- |
| Ollama | 11434 | `127.0.0.1:11434` | LLM inference API |
| Open WebUI | 8080 | `localhost:8080` | Chat interface |
| OpenClaw | 18789 | `127.0.0.1:18789` | AI gateway (dev) |

## Tailscale Addresses

| Machine | IPv4 | IPv6 |
| --- | --- | --- |
| Atlas | 100.71.165.80 | fd7a:115c:a1e0::613a:a550 |
| Alienware | (check `tailscale status`) | — |

## Data Flow

```
Slack message → Slack cloud → OpenClaw (Alienware:18789)
    → Ollama (localhost:11434) → Qwen cloud (inference)
    → response → OpenClaw → Slack → your device

File operations never leave the local machine.
Only AI inference requests go to the cloud.
```

## Security Boundaries

**Trusted zone (local):** OpenClaw config, workspace files, memory, Ollama, local drives

**Cloud zone (outbound only):** Model inference (Qwen), Slack relay, optional web search

No inbound ports exposed publicly. All inter-machine traffic goes through Tailscale.
