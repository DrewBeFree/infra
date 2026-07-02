# Internal Ecosystem Portal

Atlas/Tailscale-only launcher and status/control-ready surface for the DrewBeFree ecosystem.

## Source of truth

- Registry: `../ecosystem.json`
- Private Command Center launcher: `launcher.html`
- Ecosystem UI: `index.html`, `style.css`, `app.js`
- Test contract: `portal.test.mjs`

## Atlas deployment

Serve this privately from Atlas, not the public internet.

Static target, using the existing Atlas nginx root:

```bash
mkdir -p /opt/homelab-status-dashboard/ecosystem
rsync -a --delete internal-portal/ /opt/homelab-status-dashboard/ecosystem/
cp ecosystem.json /opt/homelab-status-dashboard/ecosystem/ecosystem.json
```

The deploy script also installs `http://atlas/` as a lightweight redirect to `/ecosystem/launcher.html`.
On the first run, if the previous status dashboard is still at the Atlas root, it is copied to
`/opt/homelab-status-dashboard/status/` so it remains available at `http://atlas/status/`.

Set `INTERNAL_PORTAL_INSTALL_HOME_REDIRECT=0` to deploy only `/ecosystem/` without changing
the Atlas homepage.

No nginx change is required while `/opt/homelab-status-dashboard` remains the server root. If
the portal later moves outside that root, add a location like this:

```nginx
location /ecosystem/ {
  alias /opt/homelab-status-dashboard/ecosystem/;
  index index.html;
  try_files $uri $uri/ /ecosystem/index.html;
}
```

Then open `http://atlas/`, `http://atlas/ecosystem/launcher.html`, or `http://atlas/ecosystem/` from a Tailscale-connected device.

Direct ecosystem-tree shortcuts:

- Hosted phone URL: `https://portal.drewbefree.com/ecosystem/tree.html`
- Stable hosted alias: `https://portal.drewbefree.com/ecosystem-tree.html` or `https://portal.drewbefree.com/ecosystem-tree/`
- Tailscale fallback: `http://atlas/ecosystem/tree.html` or `http://atlas/ecosystem-tree.html`

Project changelog shortcuts:

- Hosted phone URL: `https://portal.drewbefree.com/ecosystem/changelog.html`
- Tailscale fallback: `http://atlas/ecosystem/changelog.html`
- Generator: `python3 scripts/generate_project_changelog.py --output internal-portal/changelog.html`
- Logoff hook: `./update-session-logs.sh ...` regenerates `internal-portal/changelog.html` after updating touched repo session logs.

On Atlas, the generator maps Drew's Windows registry paths under
`C:\Users\drewb\Documents\GitHub\...` to `/home/drew/GitHub/...` before reading local git
metadata. This keeps `ecosystem.json` portable while letting the deployed changelog show live
clean/dirty state from Atlas checkouts. The generated `internal-portal/changelog.html` file is
ignored when checking the infra repo's own dirty state and recent commits so the changelog does
not mark itself dirty or create a self-referential refresh loop just because it was regenerated.

Related cleanup handoff: `../logs/session-2026-07-02-changelog-repo-cleanup.md`.

## Priority links

The first viewport includes priority access tiles for:

- Lead Desk: `http://100.71.165.80:3027`
- AI Dashboard / Grafana: `http://atlas:3001/d/atlas-overview/poweredge-dashboard`
- AI Token Dashboard: `http://atlas:7474`
- Leantime: `http://100.71.165.80:8095`
- Hermes: `http://100.71.165.80:9119`, a Tailscale-only user-level nginx proxy with Basic Auth.

On mobile, the navigator is an off-canvas sidebar opened by the fixed menu button. Priority links remain visible above filters so operational surfaces are not buried in the directory.

## Live state indicators

The private Command Center launcher shows compact live state on the cards Drew opens most:

- Lead Desk reads `http://atlas:8017/api/dashboard` locally and shows high-fit, draft-ready, and manual-reply counts.
- Grafana tries `http://atlas:3001/api/health` locally and shows `UP` or `DOWN` with the Grafana version when the browser is allowed to read it. If browser CORS blocks the health API, the launcher falls back to a Grafana PNG asset beacon and still shows a reliable `UP`/`DOWN` signal.

When the launcher is opened through `https://portal.drewbefree.com/`, those checks use the protected aliases:

- `https://portal.drewbefree.com/api/dashboard`
- `https://portal.drewbefree.com/api/health`

Keep hosted live checks same-origin on `portal.drewbefree.com`. Cross-origin requests to other Cloudflare Access applications, such as `leads.drewbefree.com`, can be redirected to the Access login flow and blocked by browser CORS before the launcher can read a useful response.

The Lead Desk API path must be routed before the Lead Desk frontend route in `cloudflared` ingress, otherwise `/api/dashboard` is handled by the Next.js frontend and returns 404.

## Cloudflare Access hosted route

The portal can also be reached through Cloudflare Access at:

- `https://portal.drewbefree.com/`
- `https://portal.drewbefree.com/ecosystem/`

The private Command Center-style launcher lives at `launcher.html` and should be
the daily front door once Cloudflare is configured:

- Hosted launcher: `https://portal.drewbefree.com/` -> `http://127.0.0.1/` -> `/ecosystem/launcher.html`
- Atlas/Tailscale fallback: `http://atlas/ecosystem/launcher.html`

When opened from a protected `*.drewbefree.com` hostname, priority links prefer HTTPS Cloudflare Access aliases for Lead Desk, the Atlas wiki, Grafana, AI Token Dashboard, Leantime, and Hermes. Atlas/Tailscale HTTP links remain the fallback and source-of-truth origins.

If DNS must be created manually in the Cloudflare dashboard, add proxied CNAME records pointing at the Atlas tunnel target:

```text
wiki       CNAME 188e5c59-c931-49a2-84c9-6646aadcd3c9.cfargotunnel.com
grafana    CNAME 188e5c59-c931-49a2-84c9-6646aadcd3c9.cfargotunnel.com
prometheus CNAME 188e5c59-c931-49a2-84c9-6646aadcd3c9.cfargotunnel.com
tokens     CNAME 188e5c59-c931-49a2-84c9-6646aadcd3c9.cfargotunnel.com
planning   CNAME 188e5c59-c931-49a2-84c9-6646aadcd3c9.cfargotunnel.com
hermes     CNAME 188e5c59-c931-49a2-84c9-6646aadcd3c9.cfargotunnel.com
scanner    CNAME 188e5c59-c931-49a2-84c9-6646aadcd3c9.cfargotunnel.com
```

Also add the same hostnames to the Drew-only Cloudflare Access application before enabling DNS, so Atlas apps are never exposed without identity protection.

Setup and validation steps live in `../docs/runbooks/cloudflare-protected-internal-portal.md`.
