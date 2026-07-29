#!/usr/bin/env bash
set -euo pipefail

PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin

SCRIPT_DIR=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)
REPO_DIR=${MONITORING_REPO_DIR:-$(cd -- "$SCRIPT_DIR/.." && pwd)}
BACKUP_ROOT=${MONITORING_BACKUP_ROOT:-/home/drew/backups/monitoring}
RETENTION_DAYS=${MONITORING_BACKUP_RETENTION_DAYS:-30}
RETENTION_COUNT=${MONITORING_BACKUP_RETENTION_COUNT:-30}
TEXTFILE_DIR=${MONITORING_TEXTFILE_DIR:-$REPO_DIR/node-exporter-textfile}
LOG_DIR="$BACKUP_ROOT/logs"
SNAPSHOT_PARENT="$BACKUP_ROOT/snapshots"
TIMESTAMP=$(date -u +%Y%m%dT%H%M%SZ)
SNAPSHOT_DIR="$SNAPSHOT_PARENT/$TIMESTAMP"
LOCK_FILE="$BACKUP_ROOT/.monitoring-backup.lock"
LAST_SUCCESS_FILE="$BACKUP_ROOT/last_success_snapshot"

mkdir -p "$BACKUP_ROOT" "$SNAPSHOT_PARENT" "$LOG_DIR" "$TEXTFILE_DIR"
cd "$REPO_DIR"

write_metrics() {
  local rc="$1"
  local now count size last_success
  now=$(date +%s)
  count=$(find "$SNAPSHOT_PARENT" -mindepth 1 -maxdepth 1 -type d 2>/dev/null | wc -l | tr -d ' ')
  size=0
  if [[ -d "$SNAPSHOT_DIR" ]]; then
    size=$(du -sb "$SNAPSHOT_DIR" 2>/dev/null | awk '{print $1}')
  fi
  last_success=0
  if [[ -s "$LAST_SUCCESS_FILE" ]]; then
    last_success=$(cut -d' ' -f1 "$LAST_SUCCESS_FILE" 2>/dev/null || printf '0')
  fi
  local tmp
  tmp=$(mktemp "$TEXTFILE_DIR/.monitoring_backup.prom.XXXXXX")
  cat > "$tmp" <<METRICS
# HELP monitoring_backup_last_run_unixtime Unix timestamp of the last monitoring backup attempt.
# TYPE monitoring_backup_last_run_unixtime gauge
monitoring_backup_last_run_unixtime $now
# HELP monitoring_backup_last_success_unixtime Unix timestamp of the last successful monitoring backup.
# TYPE monitoring_backup_last_success_unixtime gauge
monitoring_backup_last_success_unixtime $last_success
# HELP monitoring_backup_last_run_status Exit code from the last monitoring backup attempt. 0 means success.
# TYPE monitoring_backup_last_run_status gauge
monitoring_backup_last_run_status $rc
# HELP monitoring_backup_snapshot_count Number of retained monitoring backup snapshot directories.
# TYPE monitoring_backup_snapshot_count gauge
monitoring_backup_snapshot_count $count
# HELP monitoring_backup_last_snapshot_size_bytes Size of the current/last snapshot directory in bytes.
# TYPE monitoring_backup_last_snapshot_size_bytes gauge
monitoring_backup_last_snapshot_size_bytes $size
# HELP monitoring_backup_retention_days Configured age retention for monitoring snapshots.
# TYPE monitoring_backup_retention_days gauge
monitoring_backup_retention_days $RETENTION_DAYS
# HELP monitoring_backup_retention_count Configured count retention for monitoring snapshots.
# TYPE monitoring_backup_retention_count gauge
monitoring_backup_retention_count $RETENTION_COUNT
METRICS
  chmod 0644 "$tmp"
  mv "$tmp" "$TEXTFILE_DIR/monitoring_backup.prom"
}

on_exit() {
  local rc=$?
  if [[ $rc -eq 0 ]]; then
    printf '%s %s\n' "$(date +%s)" "$SNAPSHOT_DIR" > "$LAST_SUCCESS_FILE"
  fi
  write_metrics "$rc" || true
  exit "$rc"
}
trap on_exit EXIT

exec 9>"$LOCK_FILE"
if ! flock -n 9; then
  echo "Another monitoring backup is already running." >&2
  exit 75
fi

mkdir -p "$SNAPSHOT_DIR" "$SNAPSHOT_DIR/metadata" "$SNAPSHOT_DIR/grafana-api-dashboards"

json_get() {
  local url="$1"
  local outfile="$2"
  local auth="${3:-}"
  python3 - "$url" "$outfile" "$auth" <<'PY'
import base64, pathlib, sys, urllib.request
url, outfile, auth = sys.argv[1:4]
headers = {}
if auth:
    headers['Authorization'] = 'Basic ' + base64.b64encode(auth.encode()).decode()
req = urllib.request.Request(url, headers=headers)
with urllib.request.urlopen(req, timeout=30) as resp:
    pathlib.Path(outfile).write_bytes(resp.read())
PY
}

volume_for_mount() {
  local container="$1"
  local destination="$2"
  docker inspect "$container" --format '{{range .Mounts}}{{if eq .Destination "'"$destination"'"}}{{if eq .Type "volume"}}{{.Name}}{{end}}{{end}}{{end}}'
}

source_for_mount() {
  local container="$1"
  local destination="$2"
  docker inspect "$container" --format '{{range .Mounts}}{{if eq .Destination "'"$destination"'"}}{{.Source}}{{end}}{{end}}'
}

# Runtime metadata and live API state.
date -u +%FT%TZ > "$SNAPSHOT_DIR/metadata/created_at_utc.txt"
hostname > "$SNAPSHOT_DIR/metadata/hostname.txt"
docker compose config > "$SNAPSHOT_DIR/metadata/docker-compose.rendered.yml"
docker compose ps > "$SNAPSHOT_DIR/metadata/docker-compose.ps.txt"
docker inspect atlas-prometheus > "$SNAPSHOT_DIR/metadata/atlas-prometheus.inspect.json"
docker inspect atlas-grafana > "$SNAPSHOT_DIR/metadata/atlas-grafana.inspect.json"
docker inspect atlas-node-exporter > "$SNAPSHOT_DIR/metadata/atlas-node-exporter.inspect.json" 2>/dev/null || true
json_get 'http://127.0.0.1:9090/api/v1/status/runtimeinfo' "$SNAPSHOT_DIR/metadata/prometheus-runtimeinfo.json"
json_get 'http://127.0.0.1:9090/api/v1/targets' "$SNAPSHOT_DIR/metadata/prometheus-targets.json"
json_get 'http://127.0.0.1:3001/api/health' "$SNAPSHOT_DIR/metadata/grafana-health.json" 'admin:atlas_admin'
json_get 'http://127.0.0.1:3001/api/search?type=dash-db' "$SNAPSHOT_DIR/metadata/grafana-dashboard-search.json" 'admin:atlas_admin'

# Git/worktree config, provisioning, compose, exporters, and docs.
tar -czf "$SNAPSHOT_DIR/monitoring-repo-config.tar.gz" \
  --exclude='.git' \
  --exclude='node-exporter-textfile/*.prom' \
  --exclude='scripts/__pycache__' \
  -C "$REPO_DIR" .

ACTIVE_PROVISIONING_SOURCE=$(source_for_mount atlas-grafana /etc/grafana/provisioning || true)
printf '%s\n' "${ACTIVE_PROVISIONING_SOURCE:-}" > "$SNAPSHOT_DIR/metadata/active-grafana-provisioning-source.txt"
if [[ -n "${ACTIVE_PROVISIONING_SOURCE:-}" && -d "$ACTIVE_PROVISIONING_SOURCE" ]]; then
  tar -czf "$SNAPSHOT_DIR/active-grafana-provisioning.tar.gz" -C "$ACTIVE_PROVISIONING_SOURCE" .
else
  printf 'Active Grafana provisioning source was missing or not a directory: %s\n' "${ACTIVE_PROVISIONING_SOURCE:-<none>}" > "$SNAPSHOT_DIR/active-grafana-provisioning.MISSING.txt"
fi

# Export dashboards through Grafana's API so UI-created/edited dashboards are recoverable even if provisioning is wrong.
python3 - "$SNAPSHOT_DIR/grafana-api-dashboards" <<'PY'
import base64, json, pathlib, sys, urllib.request
out = pathlib.Path(sys.argv[1])
out.mkdir(parents=True, exist_ok=True)
base = 'http://127.0.0.1:3001'
auth = 'Basic ' + base64.b64encode(b'admin:atlas_admin').decode()

def fetch(path):
    req = urllib.request.Request(base + path, headers={'Authorization': auth})
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read().decode())

search = fetch('/api/search?type=dash-db')
(out / 'index.json').write_text(json.dumps(search, indent=2, sort_keys=True) + '\n')
for item in search:
    uid = item.get('uid')
    if not uid:
        continue
    data = fetch('/api/dashboards/uid/' + uid)
    safe = ''.join(c if c.isalnum() or c in ('-', '_', '.') else '_' for c in uid)
    (out / f'{safe}.json').write_text(json.dumps(data, indent=2, sort_keys=True) + '\n')
print(f'exported {len(search)} dashboards')
PY

# Prometheus TSDB volume. This is a live, file-level backup of immutable blocks + WAL/head files.
PROM_VOLUME=$(volume_for_mount atlas-prometheus /prometheus)
if [[ -z "$PROM_VOLUME" ]]; then
  echo 'Could not identify Prometheus /prometheus Docker volume.' >&2
  exit 20
fi
printf '%s\n' "$PROM_VOLUME" > "$SNAPSHOT_DIR/metadata/prometheus-volume-name.txt"
docker run --rm \
  -v "$PROM_VOLUME:/source:ro" \
  -v "$SNAPSHOT_DIR:/backup" \
  alpine sh -lc "tar -czf /backup/prometheus-tsdb.tar.gz --exclude=lock -C /source ."

# Grafana persistent data. Prefer the mounted volume after migration; before migration, fall back to docker cp from the container layer.
GRAFANA_VOLUME=$(volume_for_mount atlas-grafana /var/lib/grafana || true)
printf '%s\n' "${GRAFANA_VOLUME:-}" > "$SNAPSHOT_DIR/metadata/grafana-volume-name.txt"
if [[ -n "${GRAFANA_VOLUME:-}" ]]; then
  docker run --rm \
    -v "$GRAFANA_VOLUME:/source:ro" \
    -v "$SNAPSHOT_DIR:/backup" \
    alpine sh -lc "tar -czf /backup/grafana-varlib.tar.gz -C /source ."
else
  docker cp atlas-grafana:/var/lib/grafana "$SNAPSHOT_DIR/grafana-varlib"
  tar -czf "$SNAPSHOT_DIR/grafana-varlib.tar.gz" -C "$SNAPSHOT_DIR/grafana-varlib" .
  rm -rf "$SNAPSHOT_DIR/grafana-varlib"
fi

# Checksums and retention.
(
  cd "$SNAPSHOT_DIR"
  find . -type f ! -name SHA256SUMS -print0 | sort -z | xargs -0 sha256sum > SHA256SUMS
)
ln -sfn "$SNAPSHOT_DIR" "$BACKUP_ROOT/latest"

# Retain by count and by age inside the dedicated snapshot parent only.
if [[ "$RETENTION_COUNT" =~ ^[0-9]+$ && "$RETENTION_COUNT" -gt 0 ]]; then
  mapfile -t OLD_BY_COUNT < <(find "$SNAPSHOT_PARENT" -mindepth 1 -maxdepth 1 -type d | sort -r | tail -n +$((RETENTION_COUNT + 1)))
  if [[ ${#OLD_BY_COUNT[@]} -gt 0 ]]; then
    rm -rf -- "${OLD_BY_COUNT[@]}"
  fi
fi
if [[ "$RETENTION_DAYS" =~ ^[0-9]+$ && "$RETENTION_DAYS" -gt 0 ]]; then
  find "$SNAPSHOT_PARENT" -mindepth 1 -maxdepth 1 -type d -mtime +"$RETENTION_DAYS" -exec rm -rf {} +
fi

cat > "$SNAPSHOT_DIR/RESTORE-README.txt" <<RESTORE
Snapshot: $SNAPSHOT_DIR
Created UTC: $(cat "$SNAPSHOT_DIR/metadata/created_at_utc.txt")
Prometheus volume: $PROM_VOLUME
Grafana volume: ${GRAFANA_VOLUME:-container-layer copy at backup time}

Use the repo restore helper for dry-run restore commands:
  $REPO_DIR/scripts/restore-monitoring-snapshot.sh $SNAPSHOT_DIR

Do not restore over live volumes without stopping affected containers first.
RESTORE

echo "Monitoring backup snapshot complete: $SNAPSHOT_DIR"
