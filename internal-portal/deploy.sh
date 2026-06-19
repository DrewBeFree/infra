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
if [[ -f "$ROOT/internal-portal/sync-links.json" ]]; then
  cp "$ROOT/internal-portal/sync-links.json" "$TARGET/sync-links.json"
fi
find "$TARGET" -type d -exec chmod 755 {} +
find "$TARGET" -type f -exec chmod 644 {} +

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
    <meta http-equiv="refresh" content="0; url=/ecosystem/launcher.html">
    <title>DrewBeFree Private Command Center</title>
    <script>window.location.replace("/ecosystem/launcher.html");</script>
  </head>
  <body>
    <p><a href="/ecosystem/launcher.html">Open the DrewBeFree Private Command Center</a></p>
  </body>
</html>
HTML
fi

echo "Internal ecosystem portal synced to $TARGET"
if [[ "$INSTALL_HOME_REDIRECT" == "1" ]]; then
  echo "Atlas home redirects to /ecosystem/launcher.html; previous status dashboard is preserved at /status/"
fi
