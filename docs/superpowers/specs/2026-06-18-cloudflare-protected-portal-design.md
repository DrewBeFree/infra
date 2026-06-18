# Cloudflare-Protected Internal Portal Design

## Goal

Make the existing internal ecosystem portal reachable from a normal hosted URL while keeping it private to Drew. The page should feel like the private counterpart to Command Center: a launcher for local apps, projects, dashboards, repos, docs, and Atlas services, but protected before any browser can load the page.

## Existing Foundation

The portal already lives in `infra/internal-portal/` and is deployed to Atlas at `http://atlas/ecosystem/`. It renders from `ecosystem.json`, includes priority operations links, supports filtering/search, and is designed for Atlas/Tailscale-only use.

This work does not replace that portal. It adds a protected hosted access path in front of the same deployed assets.

## Recommended Hosting Model

Use Cloudflare Tunnel plus Cloudflare Access:

- Atlas continues serving the static portal from `/opt/homelab-status-dashboard/ecosystem/`.
- A Cloudflare Tunnel on Atlas maps a private hostname such as `portal.drewbefree.com` or `ops.drewbefree.com` to `http://localhost/ecosystem/` or `http://127.0.0.1/ecosystem/`.
- Additional protected hostnames map high-use local services to their existing Atlas origins:
  - `leads.drewbefree.com` -> `http://127.0.0.1:3027` or the current Lead Desk frontend origin.
  - `wiki.drewbefree.com` -> `http://127.0.0.1/wiki/`.
  - `grafana.drewbefree.com` -> `http://127.0.0.1:3001`.
  - `tokens.drewbefree.com` -> `http://127.0.0.1:7474`.
  - `planning.drewbefree.com` -> `http://127.0.0.1:8095`.
  - `hermes.drewbefree.com` -> `http://127.0.0.1:9119` if Hermes is safe to expose behind Access, otherwise keep the existing Tailscale-only proxy link.
- Cloudflare Access protects that hostname with an allow policy for Drew's email identity before the origin is reachable.
- No inbound router/firewall ports are opened.

Tailscale remains the internal fallback path: `http://atlas/ecosystem/`.

## User Experience

The first screen remains the operational launcher, not a marketing landing page. The header should make the boundary clear with copy such as `Protected by Cloudflare Access` when served from the hosted hostname, while the existing `Atlas/Tailscale only` language can stay valid for the private LAN/tailnet route.

The portal should preserve these sections:

- Priority operations links for high-frequency tools.
- Each priority operation link should prefer a Cloudflare HTTPS URL when the portal is opened from a Cloudflare hostname, and retain its Atlas/Tailscale HTTP URL as a visible fallback in the detail drawer.
- Ecosystem map for scanning apps, sites, agents, infrastructure, docs, and sensitive items.
- Directory rows for repos and project surfaces.
- Services and dashboards rows for Atlas operations.
- Docs/reference links.

## Security Boundaries

The page may list private internal URLs, local paths, service names, and sensitive project metadata, so it must never be deployed to GitHub Pages or exposed without Access.

Required controls:

- Cloudflare Access policy must allow only Drew's approved identity.
- Tunnel origin should point to Atlas' local nginx, not expose additional ports directly.
- Browser-facing protected links should be `https://...drewbefree.com`; Atlas-origin service URLs may remain `http://127.0.0.1`, `http://atlas`, or existing local service ports behind the tunnel.
- Private values such as passwords, tokens, Basic Auth hashes, API keys, and Cloudflare credentials must not be committed.
- Existing sensitive entries in `ecosystem.json` stay marked `sensitive`; Access protects the portal, but does not downgrade sensitive registry metadata.

## Implementation Shape

1. Document the Cloudflare Access deployment path in `internal-portal/README.md`.
2. Add a deployment/runbook doc with exact Cloudflare dashboard steps and Atlas-side commands, while keeping all credential values outside git.
3. Optionally add a small runtime label update in the portal so hosted Access mode says `Cloudflare Access protected` instead of only `Atlas/Tailscale only`.
4. Verify the portal still loads locally and that contract tests pass.

## Verification

Local verification:

- `node --test internal-portal/portal.test.mjs`
- `node --check internal-portal/app.js`
- `node --check internal-portal/dev-server.mjs`
- `git diff --check`

Hosted verification after Cloudflare setup:

- Unauthenticated browser session to the hosted hostname shows Cloudflare Access login, not the portal.
- Authorized Drew login reaches the portal.
- `http://atlas/ecosystem/` still works from the tailnet.
- No tunnel credentials or Access secrets appear in git.

## Open Decision

Choose the final protected hostname. Recommended default: `portal.drewbefree.com`.
