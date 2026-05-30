# Internal Ecosystem Portal

Atlas/Tailscale-only launcher and status/control-ready surface for the DrewBeFree ecosystem.

## Source of truth

- Registry: `../ecosystem.json`
- UI: `index.html`, `style.css`, `app.js`
- Test contract: `portal.test.mjs`

## Atlas deployment

Serve this privately from Atlas, not the public internet.

Suggested static target:

```bash
sudo mkdir -p /opt/internal-portal
sudo chown drew:drew /opt/internal-portal
rsync -a internal-portal/ /opt/internal-portal/
cp ecosystem.json /opt/internal-portal/ecosystem.json
```

Suggested nginx location under the existing Atlas-only server:

```nginx
location /ecosystem/ {
  alias /opt/internal-portal/;
  index index.html;
  try_files $uri $uri/ /ecosystem/index.html;
}
```

Then open `http://atlas/ecosystem/` from a Tailscale-connected device.
