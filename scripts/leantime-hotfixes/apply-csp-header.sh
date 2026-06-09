#!/usr/bin/env bash
set -euo pipefail

CONTAINER="${LEANTIME_CONTAINER:-leantime}"
NGINX_CONF="/etc/nginx/nginx.conf"
WORK_DIR="$(mktemp -d)"
BACKUP_SUFFIX="$(date +%Y%m%d%H%M%S)"

cleanup() {
  rm -rf "$WORK_DIR"
}
trap cleanup EXIT

if ! docker ps --format '{{.Names}}' | grep -qx "$CONTAINER"; then
  echo "Leantime container '$CONTAINER' is not running" >&2
  exit 1
fi

docker cp "$CONTAINER:$NGINX_CONF" "$WORK_DIR/nginx.conf"
cp "$WORK_DIR/nginx.conf" "$WORK_DIR/nginx.conf.original"

python3 - "$WORK_DIR/nginx.conf" <<'PY'
from pathlib import Path
import sys

path = Path(sys.argv[1])
text = path.read_text(encoding="utf-8")
old = '    add_header Content-Security-Policy "default-src \'self\' http: https: data: blob: \'unsafe-inline\'" always;'
new = '    add_header Content-Security-Policy "default-src \'self\' http: https: data: blob: \'unsafe-inline\'; script-src \'self\' \'unsafe-inline\' \'unsafe-eval\' unpkg.com" always;'

if new in text:
    print("Leantime nginx CSP hotfix already applied")
elif old in text:
    text = text.replace(old, new, 1)
    path.write_text(text, encoding="utf-8")
else:
    raise SystemExit("Expected nginx CSP header was not found; refusing to patch")
PY

if cmp -s "$WORK_DIR/nginx.conf" "$WORK_DIR/nginx.conf.original"; then
  exit 0
fi

docker exec -u 0 "$CONTAINER" sh -c "cp '$NGINX_CONF' '$NGINX_CONF.bak-csp-htmx-$BACKUP_SUFFIX'"
docker cp "$WORK_DIR/nginx.conf" "$CONTAINER:$NGINX_CONF"

if ! docker exec -u 0 "$CONTAINER" nginx -t; then
  echo "Patched nginx.conf failed nginx -t; restoring backup" >&2
  docker cp "$WORK_DIR/nginx.conf.original" "$CONTAINER:$NGINX_CONF"
  exit 1
fi

docker exec -u 0 "$CONTAINER" nginx -s reload

echo "Applied Leantime nginx CSP hotfix to $CONTAINER"
