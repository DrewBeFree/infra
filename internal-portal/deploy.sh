#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
HOME_ROOT="${INTERNAL_PORTAL_HOME_ROOT:-/opt/homelab-status-dashboard}"
TARGET="${INTERNAL_PORTAL_TARGET:-$HOME_ROOT/ecosystem}"
STATUS_TARGET="${INTERNAL_PORTAL_STATUS_TARGET:-$HOME_ROOT/status}"
INSTALL_HOME_REDIRECT="${INTERNAL_PORTAL_INSTALL_HOME_REDIRECT:-1}"

mkdir -p "$TARGET"
rsync -a --delete "$ROOT/internal-portal/" "$TARGET/"
cp "$ROOT/ecosystem.json" "$TARGET/ecosystem.json"

if [[ "$INSTALL_HOME_REDIRECT" == "1" ]]; then
  if [[ -f "$HOME_ROOT/index.html" && ! -f "$STATUS_TARGET/index.html" ]] && ! grep -q '/ecosystem/' "$HOME_ROOT/index.html"; then
    mkdir -p "$STATUS_TARGET"
    rsync -a \
      --exclude ecosystem \
      --exclude status \
      "$HOME_ROOT/" "$STATUS_TARGET/"
  fi

  cat > "$HOME_ROOT/index.html" <<'HTML'
<!doctype html>
<html lang="en">
  <head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <meta http-equiv="refresh" content="0; url=/ecosystem/">
    <title>DrewBeFree Ecosystem</title>
    <script>window.location.replace("/ecosystem/");</script>
  </head>
  <body>
    <p><a href="/ecosystem/">Open the DrewBeFree Ecosystem portal</a></p>
  </body>
</html>
HTML
fi

echo "Internal ecosystem portal synced to $TARGET"
if [[ "$INSTALL_HOME_REDIRECT" == "1" ]]; then
  echo "Atlas home redirects to /ecosystem/; previous status dashboard is preserved at /status/"
fi
