# Status Dashboard

Cross-project status dashboard served from atlas via Tailscale.

## Setup

1. Copy `config.example.js` to `config.js` and add your GitHub PAT
2. On atlas: clone to `/opt/status-dashboard`, add `config.js`, configure Nginx (see deployment section below)
3. Access at `http://atlas` on Tailscale

## Variants

- `index-a.html` — Clean Light
- `index-b.html` — Dark Minimal
- `index-c.html` — Warm Editorial

Default served: `index-a.html`

## Deployment (atlas)

```bash
sudo mkdir -p /opt/status-dashboard
sudo chown drew:drew /opt/status-dashboard
git clone https://github.com/DrewBeFree/status-dashboard.git /opt/status-dashboard
# create config.js manually (see config.example.js)
```

Nginx config (`/etc/nginx/sites-available/status-dashboard`):
```nginx
server {
  listen 80;
  server_name atlas _;
  root /opt/status-dashboard;
  index index-a.html;
  location / { try_files $uri $uri/ =404; }
}
```

## Updating

```bash
ssh drew@atlas
cd /opt/status-dashboard && git pull
```
