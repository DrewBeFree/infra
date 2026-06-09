#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
PATCH_FILE="$ROOT/scripts/leantime-hotfixes/leantime-project-visibility.patch"
CONTAINER="${LEANTIME_CONTAINER:-leantime}"
SERVICE_DIR="/var/www/html/app/Domain/Projects/Services"
SERVICE_FILE="$SERVICE_DIR/Projects.php"
WORK_DIR="$(mktemp -d)"

cleanup() {
  rm -rf "$WORK_DIR"
}
trap cleanup EXIT

if ! docker ps --format '{{.Names}}' | grep -qx "$CONTAINER"; then
  echo "Leantime container '$CONTAINER' is not running" >&2
  exit 1
fi

if docker exec "$CONTAINER" grep -q 'accessStatus: $accessStatus' "$SERVICE_FILE"; then
  echo "Leantime project visibility hotfix already applied to $CONTAINER"
  exit 0
fi

docker cp "$CONTAINER:$SERVICE_FILE" "$WORK_DIR/Projects.php"
cp "$WORK_DIR/Projects.php" "$WORK_DIR/Projects.php.original"

python3 - "$WORK_DIR/Projects.php" <<'PY'
from pathlib import Path
import sys

path = Path(sys.argv[1])
text = path.read_text(encoding="utf-8")
old = """        // Load all projects user is assigned to
        $projects = $this->projectRepository->getUserProjects(
            userId: $userId,
            projectStatus: $projectStatus,
            clientId: (int) $clientId,
            accessStatus: 'assigned'
        );
"""
new = """        // Owners/admins can manage every project they have global access to.
        // Regular users keep the existing assigned-only menu behavior.
        $accessStatus = Auth::userIsAtLeast(Roles::$admin, true)
            ? 'all'
            : 'assigned';

        // Load projects for the user's menu hierarchy
        $projects = $this->projectRepository->getUserProjects(
            userId: $userId,
            projectStatus: $projectStatus,
            clientId: (int) $clientId,
            accessStatus: $accessStatus
        );
"""
if old not in text:
    raise SystemExit("Expected Projects.php snippet was not found; refusing to patch")
path.write_text(text.replace(old, new, 1), encoding="utf-8")
PY

docker exec "$CONTAINER" sh -c "cd '$SERVICE_DIR' && cp Projects.php Projects.php.bak-project-visibility-\$(date +%Y%m%d%H%M%S)"
docker cp "$WORK_DIR/Projects.php" "$CONTAINER:$SERVICE_FILE"

if ! docker exec "$CONTAINER" php -l "$SERVICE_FILE"; then
  echo "Patched Projects.php failed PHP syntax check; restoring backup" >&2
  docker cp "$WORK_DIR/Projects.php.original" "$CONTAINER:$SERVICE_FILE"
  exit 1
fi

docker exec "$CONTAINER" sh -c "rm -f /var/www/html/storage/framework/views/*.php"

echo "Applied Leantime project visibility hotfix to $CONTAINER"
