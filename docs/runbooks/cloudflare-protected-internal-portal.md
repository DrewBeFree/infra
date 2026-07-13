# Cloudflare-Protected Internal Portal Runbook

## Goal

Expose the Atlas internal ecosystem portal and high-use local operator surfaces through HTTPS Cloudflare Access hostnames without opening inbound firewall ports.

## Protected Routes

| Public URL | Atlas origin | Fallback |
| --- | --- | --- |
| `https://drewbefree.com/` | GitHub Pages Command Center, Cloudflare proxied | `https://drewbefree.github.io/drewbefree-command-center/` |
| `https://www.drewbefree.com/` | GitHub Pages redirect to apex, Cloudflare proxied | `https://drewbefree.com/` |
| `https://world.kybernet.tech/` | `http://127.0.0.1:8137` PIN gateway -> `/opt/homelab-status-dashboard/ecosystem/world.html` | `http://atlas/ecosystem/world.html` |
| `https://world.drewbefree.com/` | Desired DrewBeFree-zone alias for the same gateway; requires DrewBeFree-zone DNS/API credentials | `https://world.kybernet.tech/` |
| `https://portal.drewbefree.com/` | `http://127.0.0.1/` -> `/ecosystem/launcher.html` | `http://atlas/ecosystem/launcher.html` |
| `https://portal.drewbefree.com/ecosystem/` | `http://127.0.0.1/ecosystem/` | `http://atlas/ecosystem/` |
| `https://wiki.drewbefree.com/wiki/` | `http://127.0.0.1/wiki/` | `http://atlas/wiki/` |
| `https://leads.drewbefree.com/api/dashboard` | `http://100.71.165.80:8017/api/dashboard` | `http://atlas:8017/api/dashboard` |
| `https://leads.drewbefree.com/` | `http://127.0.0.1:3027` | `http://atlas:3027/` |
| `https://grafana.drewbefree.com/` | `http://127.0.0.1:3001` | `http://atlas:3001/` |
| `https://prometheus.drewbefree.com/` | `http://127.0.0.1:9090` | `http://atlas:9090/` |
| `https://scanner.drewbefree.com/` | `http://127.0.0.1:8787` | `http://atlas:8787/` |
| `https://tokens.drewbefree.com/` | `http://127.0.0.1:7474` | `http://atlas:7474/` |
| `https://planning.drewbefree.com/` | `http://127.0.0.1:8095` | `http://atlas:8095/` |
| `https://hermes.drewbefree.com/` | `http://100.71.165.80:9119` | `http://100.71.165.80:9119/` |
| `https://portal.drewbefree.com/status/` | `http://127.0.0.1/status/` | `http://atlas/status/` |

## Cloudflare Setup

1. In Cloudflare Zero Trust, create or choose the DrewBeFree account/team.
2. Create a Cloudflare Tunnel for Atlas.
3. Install `cloudflared` on Atlas using the token from the Cloudflare dashboard.
4. Add one published application route for each protected route in the table.
5. Create a Cloudflare Access self-hosted application for the protected hostnames.
6. Add an Access policy named `drew-only` that allows only Drew's approved email identity.
7. In DrewBeFree DNS, create proxied CNAME/Tunnel records only after the matching Access hostname is covered.
8. Confirm unauthenticated private/incognito access shows the Cloudflare Access login.
9. Confirm authenticated Drew access reaches each app.

When creating DNS manually, each protected app hostname should point at the Atlas tunnel:

```text
world.kybernet.tech      CNAME 188e5c59-c931-49a2-84c9-6646aadcd3c9.cfargotunnel.com
world.drewbefree.com     CNAME 188e5c59-c931-49a2-84c9-6646aadcd3c9.cfargotunnel.com  # desired DrewBeFree-zone alias; do not create in Kybernet zone
wiki.drewbefree.com       CNAME 188e5c59-c931-49a2-84c9-6646aadcd3c9.cfargotunnel.com
grafana.drewbefree.com    CNAME 188e5c59-c931-49a2-84c9-6646aadcd3c9.cfargotunnel.com
prometheus.drewbefree.com CNAME 188e5c59-c931-49a2-84c9-6646aadcd3c9.cfargotunnel.com
tokens.drewbefree.com     CNAME 188e5c59-c931-49a2-84c9-6646aadcd3c9.cfargotunnel.com
planning.drewbefree.com   CNAME 188e5c59-c931-49a2-84c9-6646aadcd3c9.cfargotunnel.com
hermes.drewbefree.com     CNAME 188e5c59-c931-49a2-84c9-6646aadcd3c9.cfargotunnel.com
scanner.drewbefree.com    CNAME 188e5c59-c931-49a2-84c9-6646aadcd3c9.cfargotunnel.com
```

The DrewBeFree apex is different: it stays on the GitHub Pages A records but must be orange-cloud proxied so Cloudflare Access can challenge before GitHub Pages serves the public Command Center. `www.drewbefree.com` should also be proxied; GitHub Pages redirects it to the apex.

The intended public replacement surface is `https://resume.drewbefree.com/`. Keep that hostname out of the Drew-only Access application and point it at the future public resume page.

## Atlas Notes

The tunnel service URLs use Atlas local origins. The browser-facing URLs are HTTPS, but the origin URLs can remain HTTP because `cloudflared` connects from Atlas to local services.

`world.kybernet.tech` is intentionally narrower than the full portal route. It points at `internal-portal/pin_gateway.py` on `127.0.0.1:8137`, which serves the deployed static ecosystem world only after a valid PIN creates a signed short-lived cookie. Keep the PIN hash and session secret in a chmod `600` local environment file; do not commit the PIN, hash, or session secret.

`world.drewbefree.com` is the preferred final alias, but Atlas currently has no DrewBeFree-zone Cloudflare API credentials available to create that DNS record. If using the dashboard, create the CNAME in the `drewbefree.com` zone, not in the Kybernet zone. A mistaken Kybernet-zone record looks like `world.drewbefree.com.kybernet.tech` and should be removed.

Run the world gateway from the user systemd service:

```bash
systemctl --user status world-portal-pin.service --no-pager
systemctl --user restart world-portal-pin.service
journalctl --user -u world-portal-pin.service -n 80 --no-pager
```

Keep this cloudflared ingress above the final `http_status:404` rule:

```yaml
- hostname: world.kybernet.tech
  service: http://127.0.0.1:8137
- hostname: world.drewbefree.com
  service: http://127.0.0.1:8137
```

Keep the Lead Desk API ingress above the Lead Desk frontend ingress:

```yaml
- hostname: leads.drewbefree.com
  path: /api/.*
  service: http://100.71.165.80:8017
- hostname: leads.drewbefree.com
  service: http://100.71.165.80:3027
```

The private launcher uses this path for the Lead Desk high-fit, draft-ready, and manual-reply counts. Grafana health uses `/api/health`.

Route Hermes through the Tailscale nginx proxy at `http://100.71.165.80:9119`, not directly to `127.0.0.1:9119` and not through the older system nginx shim on `127.0.0.1:9120`. Hermes' realtime endpoints (`/api/ws`, `/api/events`, and `/api/pty`) require the user nginx proxy because it forwards WebSocket upgrade headers and strips `Origin` before the request reaches the loopback-bound Hermes dashboard.

No secrets belong in this repo. Do not commit tunnel tokens, credentials JSON files, Access service tokens, passwords, Basic Auth hashes, or API keys.

## Validation

Run locally before deployment:

```bash
node --test internal-portal/portal.test.mjs
node --check internal-portal/app.js
node --check internal-portal/dev-server.mjs
git diff --check
```

After Cloudflare setup:

- `https://world.kybernet.tech/` shows the PIN page before serving the ecosystem world; successful PIN entry opens the world map.
- `https://world.drewbefree.com/` should behave the same after the DrewBeFree-zone DNS alias is created.
- `https://portal.drewbefree.com/` requires Cloudflare Access before Atlas redirects to the private Command Center launcher.
- `https://drewbefree.com/` requires Cloudflare Access before showing the GitHub Pages Command Center.
- `https://portal.drewbefree.com/ecosystem/` requires Cloudflare Access before showing the portal.
- `https://wiki.drewbefree.com/wiki/` requires Cloudflare Access before showing the wiki.
- `https://leads.drewbefree.com/` requires Cloudflare Access before showing Lead Desk.
- `http://atlas/ecosystem/` still works from Tailscale.
