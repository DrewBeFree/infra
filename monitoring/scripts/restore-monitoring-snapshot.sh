#!/usr/bin/env bash
set -euo pipefail

PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin
SCRIPT_DIR=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)
REPO_DIR=${MONITORING_REPO_DIR:-$(cd -- "$SCRIPT_DIR/.." && pwd)}
SNAPSHOT=${1:-}
MODE=${2:---dry-run}
PROM_VOLUME=${PROMETHEUS_RESTORE_VOLUME:-0db9bc6fd1bc569ef3a64c0487b0b21283e1ac21784891087f3aaf0cc531a9fb}
GRAFANA_VOLUME=${GRAFANA_RESTORE_VOLUME:-atlas_grafana_data}

if [[ -z "$SNAPSHOT" || ! -d "$SNAPSHOT" ]]; then
  echo "Usage: $0 /home/drew/backups/monitoring/snapshots/YYYYmmddTHHMMSSZ [--apply]" >&2
  exit 2
fi

for required in monitoring-repo-config.tar.gz prometheus-tsdb.tar.gz grafana-varlib.tar.gz SHA256SUMS; do
  if [[ ! -f "$SNAPSHOT/$required" ]]; then
    echo "Missing $SNAPSHOT/$required" >&2
    exit 3
  fi
done

cat <<INFO
Snapshot: $SNAPSHOT
Mode: $MODE
Repo dir: $REPO_DIR
Prometheus restore volume: $PROM_VOLUME
Grafana restore volume: $GRAFANA_VOLUME

This restore overwrites monitoring repo files and the Prometheus/Grafana Docker volumes.
It stops only grafana/prometheus via docker compose before restoring volumes.
INFO

if [[ "$MODE" != "--apply" ]]; then
  cat <<DRYRUN

Dry run only. To apply after reviewing the impact:
  $0 "$SNAPSHOT" --apply

Manual equivalent restore steps:
  cd "$REPO_DIR"
  docker compose stop grafana prometheus
  tar -xzf "$SNAPSHOT/monitoring-repo-config.tar.gz" -C "$REPO_DIR"
  docker run --rm -v "$PROM_VOLUME:/target" -v "$SNAPSHOT:/backup:ro" alpine sh -lc 'rm -rf /target/* /target/.[!.]* /target/..?* 2>/dev/null || true; tar -xzf /backup/prometheus-tsdb.tar.gz -C /target'
  docker volume create "$GRAFANA_VOLUME"
  docker run --rm -v "$GRAFANA_VOLUME:/target" -v "$SNAPSHOT:/backup:ro" alpine sh -lc 'rm -rf /target/* /target/.[!.]* /target/..?* 2>/dev/null || true; tar -xzf /backup/grafana-varlib.tar.gz -C /target'
  docker compose up -d prometheus grafana

Then verify:
  curl -fsS http://127.0.0.1:9090/-/healthy
  curl -fsS -u admin:atlas_admin http://127.0.0.1:3001/api/health
DRYRUN
  exit 0
fi

cd "$REPO_DIR"
sha256sum -c "$SNAPSHOT/SHA256SUMS"
docker compose stop grafana prometheus
tar -xzf "$SNAPSHOT/monitoring-repo-config.tar.gz" -C "$REPO_DIR"
docker volume inspect "$PROM_VOLUME" >/dev/null
docker volume create "$GRAFANA_VOLUME" >/dev/null
docker run --rm -v "$PROM_VOLUME:/target" -v "$SNAPSHOT:/backup:ro" alpine sh -lc 'rm -rf /target/* /target/.[!.]* /target/..?* 2>/dev/null || true; tar -xzf /backup/prometheus-tsdb.tar.gz -C /target'
docker run --rm -v "$GRAFANA_VOLUME:/target" -v "$SNAPSHOT:/backup:ro" alpine sh -lc 'rm -rf /target/* /target/.[!.]* /target/..?* 2>/dev/null || true; tar -xzf /backup/grafana-varlib.tar.gz -C /target'
docker compose up -d prometheus grafana
curl -fsS http://127.0.0.1:9090/-/healthy >/dev/null
curl -fsS -u admin:atlas_admin http://127.0.0.1:3001/api/health >/dev/null
echo "Restore applied and health checks passed."
