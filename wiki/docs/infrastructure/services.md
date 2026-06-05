# Services

What runs where, with ports and addresses.

## Notable URLs

| Service | URL | Notes |
| --- | --- | --- |
| Status Dashboard | [http://atlas/](http://atlas/) | Tailscale-only |
| Wiki (this site) | [http://atlas/wiki/](http://atlas/wiki/) | Tailscale-only |
| Leantime | [http://atlas:8095](http://atlas:8095) | Tailscale-only planning cockpit |
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
| Leantime | 8095 | `http://atlas:8095` | Docker Compose planning cockpit, bound to Atlas Tailscale IP |
| iDRAC7 | 443 | `https://10.0.0.38` | Out-of-band management |

## Planning And Sync

| Surface | Location | Notes |
| --- | --- | --- |
| Ecosystem portal | [http://atlas/ecosystem/](http://atlas/ecosystem/) | Front door for repo, project, Leantime, GitHub Project, and synced issue links |
| Leantime | [http://atlas:8095](http://atlas:8095) | Per-repo/project planning cockpit |
| Task sync runbook | `docs/task-sync.md` | Markdown backlog to Leantime, GitHub Issues, and GitHub Projects |
| Sync link index | `data/task-sync/links.md` | Generated human-readable index of GitHub Project, Leantime, repo, and issue links |
| Leantime hotfix runbook | `scripts/leantime-hotfixes/README.md` | Reapply Atlas Leantime 3.8.0 template fixes after container recreation |

Current expected planning shape:

- Leantime has one project for each ecosystem repo/project in `ecosystem.json`.
- GitHub has matching per-project boards, with two known extras still open: `** Project Template **` and `U-Haul Load Planner Roadmap`.
- The sync bridge is append/update-by-marker only. It does not delete Leantime tasks, GitHub Issues, or GitHub Project items.
- The live Sync Bot secrets stay on Atlas in `/home/drew/services/task-sync/.env` and `/home/drew/services/task-sync/github.env`; do not commit them.

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
