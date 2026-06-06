# Hermes mobile proxy

Hermes dashboard stays bound to Atlas localhost at `127.0.0.1:9119`. Mobile access is provided by a user-level nginx proxy bound only to Atlas's Tailscale IP:

```text
http://100.71.165.80:9119
```

The proxy adds Basic Auth and forwards to Hermes on localhost. The password/hash are intentionally not stored in this repo.

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
