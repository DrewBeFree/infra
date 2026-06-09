#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
PATCH_FILE="$ROOT/scripts/leantime-hotfixes/leantime-project-visibility.patch"
CONTAINER="${LEANTIME_CONTAINER:-leantime}"
SERVICE_DIR="/var/www/html/app/Domain/Projects/Services"
SERVICE_FILE="$SERVICE_DIR/Projects.php"

if ! docker ps --format '{{.Names}}' | grep -qx "$CONTAINER"; then
  echo "Leantime container '$CONTAINER' is not running" >&2
  exit 1
fi

if docker exec "$CONTAINER" grep -q 'accessStatus: $accessStatus' "$SERVICE_FILE"; then
  echo "Leantime project visibility hotfix already applied to $CONTAINER"
  exit 0
fi

docker cp "$PATCH_FILE" "$CONTAINER:/tmp/leantime-project-visibility.patch"
docker exec "$CONTAINER" sh -c '
  set -e
  cd /var/www/html/app/Domain/Projects/Services
  cp Projects.php Projects.php.bak-project-visibility-$(date +%Y%m%d%H%M%S)
  patch -p0 < /tmp/leantime-project-visibility.patch
  php -l Projects.php
  rm -f /var/www/html/storage/framework/views/*.php
'

echo "Applied Leantime project visibility hotfix to $CONTAINER"
