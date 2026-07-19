#!/usr/bin/env bash
set -euo pipefail

PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin
SCRIPT_DIR=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)
REPO_DIR=${MONITORING_REPO_DIR:-$(cd -- "$SCRIPT_DIR/.." && pwd)}
BACKUP_ROOT=${MONITORING_BACKUP_ROOT:-/home/drew/backups/monitoring}
RETENTION_DAYS=${MONITORING_BACKUP_RETENTION_DAYS:-30}
RETENTION_COUNT=${MONITORING_BACKUP_RETENTION_COUNT:-30}
SCHEDULE=${MONITORING_BACKUP_CRON_SCHEDULE:-17 3 * * *}
MARKER='monitoring-backup: grafana-prometheus-snapshots'
LOG_FILE="$BACKUP_ROOT/logs/monitoring-backup.log"
CRON_LINE="$SCHEDULE MONITORING_BACKUP_ROOT=$BACKUP_ROOT MONITORING_BACKUP_RETENTION_DAYS=$RETENTION_DAYS MONITORING_BACKUP_RETENTION_COUNT=$RETENTION_COUNT $REPO_DIR/scripts/monitoring-backup.sh >> $LOG_FILE 2>&1 # $MARKER"

mkdir -p "$BACKUP_ROOT/logs"
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

echo "Installed monitoring backup cron:"
echo "$CRON_LINE"
