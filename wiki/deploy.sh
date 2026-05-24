#!/bin/bash
# Deploy the wiki to atlas. Run from the dev machine (where all repos are checked out).
set -e

WIKI_DIR="$(cd "$(dirname "$0")" && pwd)"
INFRA_DIR="$(cd "$WIKI_DIR/.." && pwd)"
cd "$WIKI_DIR"

echo "Regenerating project catalog..."
.venv/bin/python scripts/gen_catalog.py

if ! git -C "$INFRA_DIR" diff --quiet -- wiki/docs/projects; then
  echo "ERROR: catalog changed. Commit & push wiki/docs/projects via your branch workflow, then re-run."
  exit 1
fi

echo "Pushing infra..."
git -C "$INFRA_DIR" push

echo "Building on atlas..."
ssh atlas "cd ~/infra && git pull && cd wiki && .venv/bin/python scripts/gen_catalog.py && .venv/bin/python -m mkdocs build -d /opt/wiki"

echo "Done. Refresh http://atlas/wiki/"
