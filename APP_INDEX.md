# App Index

Quick navigation for the infra repository's ecosystem and portal maintenance surfaces.

| Area | Path | Purpose |
| --- | --- | --- |
| Ecosystem registry | `ecosystem.json` | Canonical inventory for private apps, services, dashboards, and access routes. |
| Repository manifest | `repos.json` | Source list for workspace cloning, cataloging, and repo automation. |
| Internal portal | `internal-portal/` | Static ecosystem views and deployable Atlas portal assets. |
| Project wiki | `wiki/` | MkDocs-style catalog and infrastructure documentation. |
| Monitoring stack | `monitoring/` | Prometheus, Grafana, exporters, backup scripts, and deployment notes. |
| Automation scripts | `scripts/` | Workspace inventory, changelog generation, and repo sync helpers. |
| Session logs | `logs/` | Human-readable notes from infrastructure maintenance sessions. |

## Common entry points

- Start with `README.md` for repo-wide maintenance commands.
- Use `internal-portal/README.md` before changing generated portal assets.
- Regenerate derived outputs from scripts instead of hand-editing generated files.
- Keep overnight automation on `dev`; never commit these changes on `main`.
