# Monitoring Backups and Restore

Purpose: prevent silent loss of Atlas Grafana dashboards, Grafana SQLite state, Prometheus TSDB data, provisioning files, Prometheus config/rules, and Docker Compose monitoring files.

## Schedule

Installed by:

```bash
/home/drew/GitHub/infra/monitoring/scripts/install-monitoring-backup-cron.sh
```

Default cron schedule:

```cron
17 3 * * *
```

Default snapshot root:

```text
/home/drew/backups/monitoring/snapshots
```

Default retention:

- 30 days
- 30 newest snapshots

Both are enforced inside `/home/drew/backups/monitoring/snapshots` only.

## What each snapshot contains

- `monitoring-repo-config.tar.gz` — monitoring repo config/provisioning/scripts, excluding `.git` and Prometheus textfile output.
- `prometheus-tsdb.tar.gz` — live file-level backup of the active Prometheus `/prometheus` Docker volume.
- `grafana-varlib.tar.gz` — Grafana `/var/lib/grafana`, including `grafana.db`.
- `grafana-api-dashboards/` — all Grafana dashboards exported through the authenticated API.
- `metadata/` — Docker inspect output, rendered compose config, compose ps, Prometheus runtime info, Prometheus targets, Grafana health, dashboard inventory, active volume names, and active provisioning source.
- `SHA256SUMS` — checksums for snapshot files.

## Monitoring the backups

The backup script writes Prometheus textfile collector metrics to:

```text
/home/drew/GitHub/infra/monitoring/node-exporter-textfile/monitoring_backup.prom
```

Node exporter exposes these as:

- `monitoring_backup_last_run_unixtime`
- `monitoring_backup_last_success_unixtime`
- `monitoring_backup_last_run_status`
- `monitoring_backup_snapshot_count`
- `monitoring_backup_last_snapshot_size_bytes`
- `monitoring_backup_retention_days`
- `monitoring_backup_retention_count`

Alert rules fire if the last successful backup is older than 48 hours or the last run exited non-zero.

## Restore dry run

```bash
/home/drew/GitHub/infra/monitoring/scripts/restore-monitoring-snapshot.sh /home/drew/backups/monitoring/latest
```

## Restore apply

This is destructive to the current monitoring repo files and Prometheus/Grafana Docker volumes. Review the dry run first.

```bash
/home/drew/GitHub/infra/monitoring/scripts/restore-monitoring-snapshot.sh /home/drew/backups/monitoring/latest --apply
```

Post-restore health checks:

```bash
curl -fsS http://127.0.0.1:9090/-/healthy
curl -fsS -u admin:atlas_admin http://127.0.0.1:3001/api/health
```
