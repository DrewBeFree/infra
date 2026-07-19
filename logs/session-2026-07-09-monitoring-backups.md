# Grafana/Prometheus Monitoring Backups — 2026-07-09

Host/worktree: `/home/drew/GitHub/infra`
Monitoring path: `/home/drew/GitHub/infra/monitoring`
Branch: `dev`
Remote: `origin/dev`
Commit: not committed in this session because `/home/drew/GitHub/infra` already had unrelated dirty `internal-portal/*` changes and `monitoring/` is currently untracked at the infra repo level.

## Outcome

Installed and verified recurring Grafana/Prometheus monitoring snapshots so dashboards, Grafana SQLite state, Prometheus TSDB data, provisioning files, Prometheus config/rules, and Docker Compose monitoring files can be recovered after future loss.

Latest verified snapshot:

```text
/home/drew/backups/monitoring/snapshots/20260709T033500Z
/home/drew/backups/monitoring/latest -> /home/drew/backups/monitoring/snapshots/20260709T033500Z
```

## Why this was done

Drew reported prior monitoring history/dashboard loss. Prometheus retention had already been extended to `3y`, but there was no verified recurring snapshot path for Grafana/Prometheus state. The goal was future loss prevention, not recovery of already-missing Prometheus history.

## Files intentionally changed

In `/home/drew/GitHub/infra/monitoring`:

- `docker-compose.yml`
  - Added external Grafana data volume `atlas_grafana_data` mounted at `/var/lib/grafana`.
  - Added node-exporter textfile collector mount and flag for backup freshness metrics.
- `alert.rules.yml`
  - Added `MonitoringBackupStale`, `MonitoringBackupFailed`, and `MonitoringBackupMetricMissing` alerts.
- `scripts/monitoring-backup.sh`
  - Creates timestamped snapshots under `/home/drew/backups/monitoring/snapshots`.
  - Backs up Prometheus TSDB, Grafana data, Grafana API dashboard exports, monitoring repo config/provisioning, runtime metadata, and checksums.
  - Writes readable node-exporter textfile metrics.
- `scripts/install-monitoring-backup-cron.sh`
  - Installs idempotent daily cron entry.
- `scripts/restore-monitoring-snapshot.sh`
  - Defaults to dry-run and requires `--apply` for destructive volume/repo restore.
- `MONITORING_BACKUPS.md`
  - Documents backup contents, metrics, schedule, retention, and restore steps.
- `node-exporter-textfile/.gitkeep`
  - Keeps the textfile collector directory present.

Outside the repo:

- `/home/drew/workspace/grafana-prometheus-snapshots/STATE.md`
  - Appended full handoff with changes, verification output, snapshot location, schedule, retention, and restore steps.
- `/home/drew/.hermes/skills/devops/homelab-monitoring/SKILL.md`
  - Patched pitfalls discovered during the run: Docker bind-mounted file inode pinning and node-exporter textfile permission requirements.

## Important findings

- Running Grafana was mounted from stale/deleted path:

```text
/home/drew/monitoring/grafana-provisioning
```

- Grafana `/var/lib/grafana/grafana.db` was in the container writable layer before this work. It is now seeded into persistent Docker volume:

```text
atlas_grafana_data
```

- Prometheus file bind mounts can stay pinned to old inodes after atomic file rewrites. SIGHUP did not load the new `alert.rules.yml`; force-recreating only `atlas-prometheus` fixed the bind and loaded the backup alerts.
- Node exporter textfile collector could not read `0600` `.prom` files. The backup script now writes `monitoring_backup.prom` as `0644` and verification showed `node_textfile_scrape_error=0`.

## Commands run

Representative commands actually run:

```bash
cd /home/drew/GitHub/infra/monitoring

docker compose ps
curl -fsS http://127.0.0.1:9090/api/v1/status/runtimeinfo
docker inspect atlas-prometheus
docker inspect atlas-grafana
curl -fsS -u admin:atlas_admin 'http://127.0.0.1:3001/api/search?type=dash-db'

docker cp atlas-grafana:/var/lib/grafana ./<temp>
docker volume create atlas_grafana_data
docker run --rm -v atlas_grafana_data:/target -v <temp>:/source:ro alpine sh -lc 'cd /source && tar cf - . | tar xf - -C /target && chown -R 472:0 /target'

docker compose config
docker run --rm --entrypoint promtool -v "$PWD/prometheus.yml:/etc/prometheus/prometheus.yml:ro" -v "$PWD/alert.rules.yml:/etc/prometheus/alert.rules.yml:ro" prom/prometheus:latest check config /etc/prometheus/prometheus.yml

docker compose up -d --no-deps prometheus node-exporter grafana
docker compose up -d --no-deps --force-recreate prometheus

scripts/monitoring-backup.sh
scripts/install-monitoring-backup-cron.sh
scripts/restore-monitoring-snapshot.sh /home/drew/backups/monitoring/latest
```

## Verification

Final observed result:

```text
promtool check config /etc/prometheus/prometheus.yml
SUCCESS: /etc/prometheus/prometheus.yml is valid prometheus config file syntax
SUCCESS: 17 rules found

latest=/home/drew/backups/monitoring/snapshots/20260709T033500Z
snapshot_count=2
latest_size=1.1G
sha256sum -c SHA256SUMS: OK
restore helper mode: --dry-run
prometheus_health=Prometheus Server is Healthy.
grafana_health={"database":"ok","version":"13.0.1+security-01","commit":"9bbe672d"}
prometheus_retention=3y
monitoring_backup_last_run_status=0
monitoring_backup_snapshot_count=2
node_textfile_scrape_error=0
time() - monitoring_backup_last_success_unixtime≈47s
backup_rules=[MonitoringBackupStale inactive, MonitoringBackupFailed inactive, MonitoringBackupMetricMissing inactive]
dashboard_count=4 uids=[atlas-overview, atlas-p40-summary, llm-benchmarks, atlas-storage]
```

Final compose state:

```text
atlas-grafana       Up healthy
atlas-prometheus    Up healthy
atlas-node-exporter Up
```

Installed cron:

```cron
17 3 * * * MONITORING_BACKUP_ROOT=/home/drew/backups/monitoring MONITORING_BACKUP_RETENTION_DAYS=30 MONITORING_BACKUP_RETENTION_COUNT=30 /home/drew/GitHub/infra/monitoring/scripts/monitoring-backup.sh >> /home/drew/backups/monitoring/logs/monitoring-backup.log 2>&1 # monitoring-backup: grafana-prometheus-snapshots
```

## Restore path

Dry-run first:

```bash
cd /home/drew/GitHub/infra/monitoring
scripts/restore-monitoring-snapshot.sh /home/drew/backups/monitoring/latest
```

Apply only after reviewing destructive impact:

```bash
cd /home/drew/GitHub/infra/monitoring
scripts/restore-monitoring-snapshot.sh /home/drew/backups/monitoring/latest --apply
```

## Safety notes

- No Prometheus/Grafana volumes were deleted or pruned.
- A pre-change backup was taken before service recreation:

```text
/home/drew/backups/monitoring/prechange-20260709T032635Z
```

- Grafana was recreated only after copying the live container-layer `/var/lib/grafana` into `atlas_grafana_data`.
- Prometheus was force-recreated only after confirming the running container was bound to an old `alert.rules.yml` inode.
- This prevents future silent loss. It does not recover already-missing Prometheus history before the active TSDB window.

## Repo hygiene / next step

Current infra repo status after this work included unrelated pre-existing changes:

```text
 M internal-portal/changelog.html
 M internal-portal/launcher.html
?? internal-portal/launcher-clean.html
?? monitoring/
```

Next recommended step: decide whether `monitoring/` should be tracked in the infra repo. If yes, stage only the monitoring backup files plus this log, review for secrets, then commit separately from the unrelated `internal-portal/*` changes.
