#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
TARGET="${INTERNAL_PORTAL_TARGET:-/opt/internal-portal}"

mkdir -p "$TARGET"
rsync -a --delete "$ROOT/internal-portal/" "$TARGET/"
cp "$ROOT/ecosystem.json" "$TARGET/ecosystem.json"

echo "Internal ecosystem portal synced to $TARGET"
