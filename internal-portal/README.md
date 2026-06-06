# Internal Ecosystem Portal

Atlas/Tailscale-only launcher and status/control-ready surface for the DrewBeFree ecosystem.

## Source of truth

- Registry: `../ecosystem.json`
- UI: `index.html`, `style.css`, `app.js`
- Test contract: `portal.test.mjs`

## Atlas deployment

Serve this privately from Atlas, not the public internet.

Static target, using the existing Atlas nginx root:

```bash
mkdir -p /opt/homelab-status-dashboard/ecosystem
rsync -a --delete internal-portal/ /opt/homelab-status-dashboard/ecosystem/
cp ecosystem.json /opt/homelab-status-dashboard/ecosystem/ecosystem.json
```

The deploy script also installs `http://atlas/` as a lightweight redirect to `/ecosystem/`.
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

Then open `http://atlas/` or `http://atlas/ecosystem/` from a Tailscale-connected device.

## Priority links

The first viewport includes priority access tiles for:

- Lead Desk: `http://100.117.87.57:3027`
- AI Dashboard / Grafana: `http://atlas:3001/d/atlas-overview/poweredge-dashboard`
- Leantime: `http://atlas:8095`
- Hermes: `http://100.71.165.80:9119`, a Tailscale-only user-level nginx proxy with Basic Auth.

On mobile, the navigator is an off-canvas sidebar opened by the fixed menu button. Priority links remain visible above filters so operational surfaces are not buried in the directory.
