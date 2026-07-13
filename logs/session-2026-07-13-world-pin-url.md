# Ecosystem World PIN URL — 2026-07-13

Host/worktree: `/home/drew/GitHub/infra`
Branch: `dev`

## Goal

Flesh out the ecosystem world page and expose it through a Cloudflare Tunnel URL that requires a PIN before serving the world view.

## Result

Live PIN-gated URL:

```text
https://world.kybernet.tech/
```

Desired future alias once DrewBeFree-zone DNS/API credentials are available:

```text
https://world.drewbefree.com/
```

## Files changed

- `internal-portal/world.html`
  - Added protected-host status badge.
  - Added an orientation panel: high-level map first, details on click.
  - Keeps draggable/expandable regions and active-site strip.
- `internal-portal/pin_gateway.py`
  - New local PIN-gated static gateway for the world page.
  - Binds to `127.0.0.1:8137` by default.
  - Serves deployed static files from `/opt/homelab-status-dashboard/ecosystem` only after a valid PIN creates a signed session cookie.
- `internal-portal/portal.test.mjs`
  - Added coverage for world hosted metadata and gateway markers.
- `ecosystem.json`
  - Added `world` protected route metadata.
- `internal-portal/README.md`
  - Documented live hosted world URL, desired DrewBeFree alias, and local gateway behavior.
- `docs/runbooks/cloudflare-protected-internal-portal.md`
  - Documented `world.kybernet.tech`, gateway service commands, tunnel ingress, validation, and DrewBeFree DNS caveat.

## Runtime changes

Created local secret files outside git:

```text
/home/drew/.config/world-portal-pin.pin
/home/drew/.config/world-portal-pin.env
```

Both are mode `0600`. The `.pin` file stores the generated PIN for Drew to retrieve locally. The `.env` file stores only the PIN hash, session secret, port, host, and root.

Created user systemd service:

```text
/home/drew/.config/systemd/user/world-portal-pin.service
```

Service commands:

```bash
systemctl --user status world-portal-pin.service --no-pager
systemctl --user restart world-portal-pin.service
journalctl --user -u world-portal-pin.service -n 80 --no-pager
```

Updated live cloudflared config:

```text
/home/drew/.cloudflared/config.yml
```

Added ingress routes:

```yaml
- hostname: world.drewbefree.com
  service: http://127.0.0.1:8137
- hostname: world.kybernet.tech
  service: http://127.0.0.1:8137
```

`world.kybernet.tech` DNS was created successfully with `cloudflared tunnel route dns answering-agent world.kybernet.tech`.

## DNS caveat

Attempting to create `world.drewbefree.com` with the current cloudflared certificate created the wrong Kybernet-zone record:

```text
world.drewbefree.com.kybernet.tech
```

This matches the existing repo warning about accidental Kybernet-zone DrewBeFree records. The correct `world.drewbefree.com` record must be created in the `drewbefree.com` Cloudflare zone with DrewBeFree-zone credentials or through the Cloudflare dashboard.

## Verification

Observed test result:

```text
node --test internal-portal/portal.test.mjs
31 pass
0 fail
```

Observed gateway unit status:

```text
systemctl --user is-active world-portal-pin.service
active
```

Observed public HTTPS behavior after rotating the session secret:

```text
HEAD status: HTTP/2 200
Unauth marker: <label for="pin">Access PIN</label>
Auth marker: <strong>High-level map first. Details on click.</strong>
```

Browser check:

```text
https://world.kybernet.tech/
PIN page rendered with Access PIN field and Unlock world button.
```

## Safety notes

- No PIN, PIN hash, session secret, Cloudflare credentials, or tunnel credentials are committed.
- A session cookie was accidentally printed during verification; the gateway session secret was rotated immediately afterward, invalidating it.
- The live Cloudflare tunnel now exposes only the PIN gateway for the world URL, not the whole portal.
- `john.drewbefree.com` was observed to be publicly reachable without a PIN/Access challenge during investigation. This was not changed in this session and should be reviewed separately if that exposure is not intended.
