# Cloudflare-Protected Internal Portal Runbook

## Goal

Expose the Atlas internal ecosystem portal and high-use local operator surfaces through HTTPS Cloudflare Access hostnames without opening inbound firewall ports.

## Protected Routes

| Public URL | Atlas origin | Fallback |
| --- | --- | --- |
| `https://portal.drewbefree.com/` | `http://127.0.0.1/ecosystem/launcher.html` | `http://atlas/ecosystem/launcher.html` |
| `https://portal.drewbefree.com/ecosystem/` | `http://127.0.0.1/ecosystem/` | `http://atlas/ecosystem/` |
| `https://wiki.drewbefree.com/wiki/` | `http://127.0.0.1/wiki/` | `http://atlas/wiki/` |
| `https://leads.drewbefree.com/` | `http://127.0.0.1:3027` | `http://atlas:3027/` |
| `https://grafana.drewbefree.com/` | `http://127.0.0.1:3001` | `http://atlas:3001/` |
| `https://prometheus.drewbefree.com/` | `http://127.0.0.1:9090` | `http://atlas:9090/` |
| `https://scanner.drewbefree.com/` | `http://127.0.0.1:8787` | `http://atlas:8787/` |
| `https://tokens.drewbefree.com/` | `http://127.0.0.1:7474` | `http://atlas:7474/` |
| `https://planning.drewbefree.com/` | `http://127.0.0.1:8095` | `http://atlas:8095/` |
| `https://hermes.drewbefree.com/` | `http://127.0.0.1:9119` | `http://100.71.165.80:9119/` |
| `https://portal.drewbefree.com/status/` | `http://127.0.0.1/status/` | `http://atlas/status/` |

## Cloudflare Setup

1. In Cloudflare Zero Trust, create or choose the DrewBeFree account/team.
2. Create a Cloudflare Tunnel for Atlas.
3. Install `cloudflared` on Atlas using the token from the Cloudflare dashboard.
4. Add one published application route for each protected route in the table.
5. Create a Cloudflare Access self-hosted application for the protected hostnames.
6. Add an Access policy named `drew-only` that allows only Drew's approved email identity.
7. Confirm unauthenticated private/incognito access shows the Cloudflare Access login.
8. Confirm authenticated Drew access reaches each app.

## Atlas Notes

The tunnel service URLs use Atlas local origins. The browser-facing URLs are HTTPS, but the origin URLs can remain HTTP because `cloudflared` connects from Atlas to local services.

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

- `https://portal.drewbefree.com/` requires Cloudflare Access before showing the private Command Center launcher.
- `https://portal.drewbefree.com/ecosystem/` requires Cloudflare Access before showing the portal.
- `https://wiki.drewbefree.com/wiki/` requires Cloudflare Access before showing the wiki.
- `https://leads.drewbefree.com/` requires Cloudflare Access before showing Lead Desk.
- `http://atlas/ecosystem/` still works from Tailscale.
