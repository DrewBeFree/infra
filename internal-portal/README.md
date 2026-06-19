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

## Priority links

The first viewport includes priority access tiles for:

- Lead Desk: `http://100.117.87.57:3027`
- AI Dashboard / Grafana: `http://atlas:3001/d/atlas-overview/poweredge-dashboard`
- AI Token Dashboard: `http://atlas:7474`
- Leantime: `http://atlas:8095`
- Hermes: `http://100.71.165.80:9119`, a Tailscale-only user-level nginx proxy with Basic Auth.

On mobile, the navigator is an off-canvas sidebar opened by the fixed menu button. Priority links remain visible above filters so operational surfaces are not buried in the directory.

## Cloudflare Access hosted route

The portal can also be reached through Cloudflare Access at:

- `https://portal.drewbefree.com/`
- `https://portal.drewbefree.com/ecosystem/`

The private Command Center-style launcher lives at `launcher.html` and should be
the daily front door once Cloudflare is configured:

- Hosted launcher: `https://portal.drewbefree.com/` -> `http://127.0.0.1/` -> `/ecosystem/launcher.html`
- Atlas/Tailscale fallback: `http://atlas/ecosystem/launcher.html`

When opened from a protected `*.drewbefree.com` hostname, priority links prefer HTTPS Cloudflare Access aliases for Lead Desk, the Atlas wiki, Grafana, AI Token Dashboard, Leantime, and Hermes. Atlas/Tailscale HTTP links remain the fallback and source-of-truth origins.

Setup and validation steps live in `../docs/runbooks/cloudflare-protected-internal-portal.md`.
