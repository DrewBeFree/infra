#!/usr/bin/env bash
# check-card-links.sh
# Verifies that key public card links (launcher, world, etc.) return 200/OK.
# Run hourly via cron.

set -euo pipefail

LOG_DIR="/home/drew/backups/card-link-checks"
mkdir -p "$LOG_DIR"
LOG_FILE="$LOG_DIR/check-$(date +%Y%m%d-%H%M).log"

URLS=(
  "https://world.drewbefree.com/launcher.html"
  "https://world.drewbefree.com/"
  "https://wiki.drewbefree.com/wiki/"
)

echo "=== Card link check started at $(date -Iseconds) ===" | tee -a "$LOG_FILE"

for url in "${URLS[@]}"; do
  code=$(curl -s -o /dev/null -w "%{http_code}" --max-time 15 "$url" || echo "000")
  if [[ "$code" =~ ^2 ]]; then
    echo "OK   $code  $url" | tee -a "$LOG_FILE"
  else
    echo "FAIL $code  $url" | tee -a "$LOG_FILE"
  fi
done

echo "=== Check finished ===" | tee -a "$LOG_FILE"
