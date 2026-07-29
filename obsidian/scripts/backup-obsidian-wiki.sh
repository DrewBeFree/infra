#!/usr/bin/env bash
set -euo pipefail

VAULT="${OBSIDIAN_VAULT_PATH:-/home/drew/wiki}"
BACKUP_ROOT="${OBSIDIAN_BACKUP_ROOT:-/home/drew/backups/obsidian-wiki}"
SNAPSHOT_ROOT="$BACKUP_ROOT/snapshots"
LOG_ROOT="$BACKUP_ROOT/logs"
LOCK_FILE="$BACKUP_ROOT/.backup.lock"
RETENTION_DAYS="${OBSIDIAN_BACKUP_RETENTION_DAYS:-90}"
RETENTION_COUNT="${OBSIDIAN_BACKUP_RETENTION_COUNT:-250}"

if [[ ! -d "$VAULT" ]]; then
  echo "ERROR: vault path does not exist: $VAULT" >&2
  exit 1
fi

mkdir -p "$SNAPSHOT_ROOT" "$LOG_ROOT"

exec 9>"$LOCK_FILE"
if ! flock -n 9; then
  echo "$(date -Is) backup already running; exiting"
  exit 0
fi

TS="$(date +%Y%m%d-%H%M%S)"
TMP_DEST="$SNAPSHOT_ROOT/.${TS}.incomplete"
DEST="$SNAPSHOT_ROOT/$TS"
LATEST_LINK="$BACKUP_ROOT/latest"
LAST_DEST=""

cleanup() {
  if [[ -d "$TMP_DEST" ]]; then
    rm -rf "$TMP_DEST"
  fi
}
trap cleanup EXIT

if [[ -L "$LATEST_LINK" ]]; then
  LAST_DEST="$(readlink -f "$LATEST_LINK" || true)"
fi

RSYNC_ARGS=(
  -a
  --delete
  --human-readable
  --exclude='.stfolder/'
)

if [[ -n "$LAST_DEST" && -d "$LAST_DEST" ]]; then
  RSYNC_ARGS+=(--link-dest="$LAST_DEST")
fi

mkdir -p "$TMP_DEST"

echo "$(date -Is) starting Obsidian wiki backup"
echo "source=$VAULT"
echo "dest=$DEST"

rsync "${RSYNC_ARGS[@]}" "$VAULT/" "$TMP_DEST/"

python3 - "$TMP_DEST" "$VAULT" "$DEST" > "$TMP_DEST/BACKUP-MANIFEST.txt" <<'PY'
from pathlib import Path
import datetime, socket, sys
snapshot = Path(sys.argv[1])
source = Path(sys.argv[2])
final_snapshot = Path(sys.argv[3])
files = [p for p in snapshot.rglob('*') if p.is_file()]
bytes_total = sum(p.stat().st_size for p in files)
print(f"created_at={datetime.datetime.now(datetime.UTC).isoformat()}")
print(f"host={socket.gethostname()}")
print(f"source={source}")
print(f"snapshot={final_snapshot}")
print(f"file_count={len(files)}")
print(f"bytes={bytes_total}")
PY

mv "$TMP_DEST" "$DEST"
ln -sfn "$DEST" "$LATEST_LINK.tmp"
mv -Tf "$LATEST_LINK.tmp" "$LATEST_LINK"
trap - EXIT

echo "$(date -Is) backup complete: $DEST"

python3 - "$SNAPSHOT_ROOT" "$RETENTION_DAYS" "$RETENTION_COUNT" <<'PY'
from pathlib import Path
import datetime, shutil, sys
root = Path(sys.argv[1])
retention_days = int(sys.argv[2])
retention_count = int(sys.argv[3])
cutoff = datetime.datetime.now() - datetime.timedelta(days=retention_days)
snaps = sorted([p for p in root.iterdir() if p.is_dir() and not p.name.startswith('.')], key=lambda p: p.name, reverse=True)
keep = set(snaps[:retention_count])
for snap in snaps:
    if snap in keep:
        continue
    try:
        ts = datetime.datetime.strptime(snap.name, '%Y%m%d-%H%M%S')
    except ValueError:
        continue
    if ts < cutoff:
        print(f"pruning old snapshot: {snap}")
        shutil.rmtree(snap)
PY

echo "$(date -Is) retention check complete"
