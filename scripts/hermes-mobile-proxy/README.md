# Hermes mobile proxy

Hermes dashboard stays bound to Atlas localhost at `127.0.0.1:9119`. Mobile access is provided by a user-level nginx proxy bound only to Atlas's Tailscale IP:

```text
http://100.71.165.80:9119
```

The proxy adds Basic Auth and forwards to Hermes on localhost. The password/hash are intentionally not stored in this repo.

The realtime Hermes endpoints `/api/ws`, `/api/events`, and `/api/pty` are exempt from nginx Basic Auth because mobile Safari does not reliably attach Basic Auth credentials to websocket/EventSource-style background requests. Those endpoints remain reachable only on Atlas's Tailscale IP and still require Hermes' per-session token query parameter. The proxy also strips `Origin` for those realtime endpoints so Hermes' loopback-bound WebSocket guard accepts the tokened connection forwarded by local nginx.

Live files on Atlas:

- Config root: `/home/drew/hermes-mobile-proxy`
- Nginx config: `/home/drew/hermes-mobile-proxy/nginx.conf`
- Password file: `/home/drew/hermes-mobile-proxy/conf/htpasswd`
- User service: `/home/drew/.config/systemd/user/hermes-mobile-proxy.service`

Useful commands:

```bash
systemctl --user status hermes-mobile-proxy.service
systemctl --user restart hermes-mobile-proxy.service
tail -f ~/hermes-mobile-proxy/logs/error.log
```

Verification:

```bash
curl -I http://100.71.165.80:9119/
curl -u drew:'<password>' http://100.71.165.80:9119/
```

Expected behavior: unauthenticated requests return `401`; authenticated requests return the Hermes dashboard HTML and assets.

Realtime verification:

```bash
curl -i 'http://100.71.165.80:9119/api/events?token=invalid&channel=invalid'
```

Expected behavior: nginx should not return a Basic Auth `401`; Hermes should reject the invalid token itself.
