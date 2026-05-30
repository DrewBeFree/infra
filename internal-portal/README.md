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

No nginx change is required while `/opt/homelab-status-dashboard` remains the server root. If the portal later moves outside that root, add a location like this:

```nginx
location /ecosystem/ {
  alias /opt/homelab-status-dashboard/ecosystem/;
  index index.html;
  try_files $uri $uri/ /ecosystem/index.html;
}
```

Then open `http://atlas/ecosystem/` from a Tailscale-connected device.
