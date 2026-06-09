#!/usr/bin/env bash
set -euo pipefail

CONTAINER="${LEANTIME_CONTAINER:-leantime}"
WORK_DIR="$(mktemp -d)"
BACKUP_SUFFIX="$(date +%Y%m%d%H%M%S)"

FILES=(
  "/var/www/html/app/Views/Templates/sections/header.blade.php"
  "/var/www/html/public/assets/js/app/htmx.js"
  "/var/www/html/public/dist/js/compiled-htmx.3.8.0.min.js"
)

cleanup() {
  rm -rf "$WORK_DIR"
}
trap cleanup EXIT

if ! docker ps --format '{{.Names}}' | grep -qx "$CONTAINER"; then
  echo "Leantime container '$CONTAINER' is not running" >&2
  exit 1
fi

for file in "${FILES[@]}"; do
  name="$(basename "$file")"
  docker cp "$CONTAINER:$file" "$WORK_DIR/$name"
  cp "$WORK_DIR/$name" "$WORK_DIR/$name.original"
done

python3 - "$WORK_DIR" <<'PY'
from pathlib import Path
import sys

work_dir = Path(sys.argv[1])

replacements = {
    "header.blade.php": (
        '<script src="{!! BASE_URL !!}/dist/js/compiled-htmx.{!! $version !!}.min.js"></script>',
        '<script src="{!! BASE_URL !!}/dist/js/compiled-htmx.{!! $version !!}.min.js?atlas=disable-vt-20260608"></script>',
    ),
    "htmx.js": (
        "window.htmx.config.globalViewTransitions = true;",
        "window.htmx.config.globalViewTransitions = false;",
    ),
    "compiled-htmx.3.8.0.min.js": (
        "window.htmx.config.globalViewTransitions=!0",
        "window.htmx.config.globalViewTransitions=!1",
    ),
}

for filename, (old, new) in replacements.items():
    path = work_dir / filename
    text = path.read_text(encoding="utf-8")
    if new in text:
        print(f"{filename}: htmx View Transitions hotfix already applied")
    elif old in text:
        path.write_text(text.replace(old, new, 1), encoding="utf-8")
        print(f"{filename}: disabled global htmx View Transitions")
    else:
        raise SystemExit(f"{filename}: expected htmx View Transitions setting was not found")
PY

for file in "${FILES[@]}"; do
  name="$(basename "$file")"
  if cmp -s "$WORK_DIR/$name" "$WORK_DIR/$name.original"; then
    continue
  fi

  docker exec -u 0 "$CONTAINER" sh -c "cp '$file' '$file.bak-view-transitions-$BACKUP_SUFFIX'"
  docker cp "$WORK_DIR/$name" "$CONTAINER:$file"
done

echo "Disabled global htmx View Transitions in $CONTAINER"
