#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
PATCH_FILE="$ROOT/scripts/leantime-hotfixes/leantime-template-hotfixes.patch"
CONTAINER="${LEANTIME_CONTAINER:-leantime}"
TEMPLATE_DIR="/var/www/html/app/Domain/Tickets/Templates"

if ! docker ps --format '{{.Names}}' | grep -qx "$CONTAINER"; then
  echo "Leantime container '$CONTAINER' is not running" >&2
  exit 1
fi

docker cp "$PATCH_FILE" "$CONTAINER:/tmp/leantime-template-hotfixes.patch"
docker exec "$CONTAINER" sh -lc "
  set -e
  cd '$TEMPLATE_DIR'
  cp milestoneDialog.blade.php milestoneDialog.blade.php.bak-hotfix-\$(date +%Y%m%d%H%M%S)
  cp showList.blade.php showList.blade.php.bak-hotfix-\$(date +%Y%m%d%H%M%S)
  cp showKanban.blade.php showKanban.blade.php.bak-hotfix-\$(date +%Y%m%d%H%M%S)
  patch -p0 < /tmp/leantime-template-hotfixes.patch
  rm -f /var/www/html/storage/framework/views/*.php
"

echo "Applied Leantime template hotfixes to $CONTAINER"
