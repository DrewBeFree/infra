#!/usr/bin/env bash
set -euo pipefail

PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin
SCRIPT_DIR=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)
OBSIDIAN_DIR=${OBSIDIAN_INFRA_DIR:-$(cd -- "$SCRIPT_DIR/.." && pwd)}
BACKUP_ROOT=${OBSIDIAN_BACKUP_ROOT:-/home/drew/backups/obsidian-wiki}
VAULT_PATH=${OBSIDIAN_VAULT_PATH:-/home/drew/wiki}
RETENTION_DAYS=${OBSIDIAN_BACKUP_RETENTION_DAYS:-90}
RETENTION_COUNT=${OBSIDIAN_BACKUP_RETENTION_COUNT:-250}
SCHEDULE=${OBSIDIAN_BACKUP_CRON_SCHEDULE:-23 * * * *}
MARKER='obsidian-wiki-backup'
LOG_FILE="$BACKUP_ROOT/logs/backup.log"
CRON_LINE="$SCHEDULE OBSIDIAN_VAULT_PATH=$VAULT_PATH OBSIDIAN_BACKUP_ROOT=$BACKUP_ROOT OBSIDIAN_BACKUP_RETENTION_DAYS=$RETENTION_DAYS OBSIDIAN_BACKUP_RETENTION_COUNT=$RETENTION_COUNT $OBSIDIAN_DIR/scripts/backup-obsidian-wiki.sh >> $LOG_FILE 2>&1 # $MARKER"

mkdir -p "$BACKUP_ROOT/logs" "$BACKUP_ROOT/crontab-backups"
TS=$(date +%Y%m%d-%H%M%S)
crontab -l > "$BACKUP_ROOT/crontab-backups/crontab-before-$MARKER-$TS.txt" 2>/dev/null || true

TMP=$(mktemp)
if crontab -l > "$TMP" 2>/dev/null; then
  true
else
  : > "$TMP"
fi
FILTERED=$(mktemp)
grep -Fv "$MARKER" "$TMP" > "$FILTERED" || true
printf '%s\n' "$CRON_LINE" >> "$FILTERED"
crontab "$FILTERED"
rm -f "$TMP" "$FILTERED"

echo "Installed Obsidian wiki backup cron:"
echo "$CRON_LINE"
