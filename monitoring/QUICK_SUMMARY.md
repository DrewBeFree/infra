# Atlas Monitoring Stack - Executive Summary

## What You Have

A **production-ready observability system** for Atlas:

- **Prometheus**: Metrics collection & storage
- **Grafana**: Beautiful dashboards (mobile-optimized)
- **6 exporters**: System, Docker, Ollama, SMART disk health
- **2 pre-built dashboards**: Overview + Storage (your Reds)
- **Alert rules**: Pre-configured, ready to fire
- **10 config files**: All ready to deploy

---

## Tonight's Mission

1. **Copy-paste 10 files** onto Atlas (via SSH cat heredoc)
2. **docker compose up -d** from ~/monitoring
3. **Access Grafana** on mobile: http://\[tailscale-ip\]:3000
4. **Watch your infrastructure** in real-time

**Time commitment**: 15–20 minutes, remote is fine.

---

## What the Dashboards Show

### Atlas Overview
- **System health**: CPU %, RAM %, load, temperature
- **Storage**: Free space on all drives
- **Docker**: Active containers, memory per container
- **Ollama**: Model status, VRAM usage

### Storage & SMART Health
- **SMART health**: Pass/fail on every drive
- **Disk errors**: Reallocated sectors (bad blocks), UDMA CRC errors
- **Temperature**: Every drive's thermal status (important for your Reds)
- **I/O**: Read/write speed (baseline for comparing performance)

---

## Why This Matters for You Now

Your Reds showed:
- **sdh**: USB bridge translation issues (UDMA CRC errors)
- **sdi**: Some actual medium errors (reallocated sectors)

The Storage dashboard will **show in real-time** if these:
- Are stable (no new errors accruing)
- Are degrading (trending toward failure)
- Need immediate action (pass/fail switch)

---

## Key Metrics to Watch

| Metric | Yellow Flag | Red Flag |
|--------|------------|----------|
| CPU Usage % | > 80% sustained | > 95% |
| Memory Usage % | > 85% | > 95% |
| Load Average (5m) | > 4 | > 8 |
| Disk Space | < 15% free | < 5% free |
| SMART Health | Any warnings | FAIL status |
| Disk Temp | > 40°C (Reds) | > 50°C |
| UDMA CRC Errors | Any trending up | Growing rapidly |

---

## Deployment Steps

### Short version:
1. SSH into Atlas
2. mkdir -p ~/monitoring/{grafana-provisioning/datasources,grafana-provisioning/dashboards/json}
3. Copy 10 files using cat heredoc (see COPY_PASTE_DEPLOY.md)
4. cd ~/monitoring && docker compose up -d
5. Get Tailscale IP: tailscale ip -4
6. Open browser: http://[ip]:3000
7. Login: admin / atlas_admin

### See:
- **COPY_PASTE_DEPLOY.md** for exact file contents & syntax
- **MONITORING_DEPLOYMENT_GUIDE.md** for troubleshooting

---

## Persistence (Next Session)

Tonight: **Ephemeral volumes** (data lost if containers restart)

Next session (when physically back):
- Convert to **persistent Docker volumes**
- Keep Prometheus metrics history (7+ days)
- Keep Grafana settings & custom dashboards
- ~5 minute migration, zero data loss

---

## Security Notes

- Default Grafana password: **atlas_admin** (change on first login)
- Accessed via Tailscale (not internet-exposed)
- Prometheus not password-protected (internal only)
- SMART exporter requires privileged mode (necessary for disk health)

---

## Files Included

1. **docker-compose.yml** — Main stack definition
2. **prometheus-scrape.yml** — Metrics collection config
3. **alert.rules.yml** — Alert definitions (not yet sending)
4. **ollama-exporter.js** — Custom Ollama metrics
5. **grafana-datasource.yml** — Prometheus connection
6. **dashboards.yml** — Dashboard provisioning
7. **atlas-overview.json** — System overview dashboard
8. **atlas-storage.json** — Storage & SMART dashboard
9. **COPY_PASTE_DEPLOY.md** — Step-by-step deployment
10. **MONITORING_DEPLOYMENT_GUIDE.md** — Full reference

---

## Troubleshooting Cheat Sheet

```bash
# Check all containers running
docker ps

# View logs for any service
docker logs atlas-prometheus
docker logs atlas-grafana
docker logs atlas-smartctl-exporter

# Verify Prometheus is scraping
curl http://localhost:9090/api/v1/targets

# Test SMART exporter directly
curl http://localhost:9633/metrics | grep smartctl

# Restart everything
docker compose restart
```

---

## Why Mobile Access Works

- Grafana detects mobile viewport automatically
- Panels stack vertically, touch-friendly
- Tailscale provides secure, private network
- No internet exposure, no port forwarding needed
- Sub-second access on same Tailscale network

Save the URL to your phone home screen as a web app for one-tap access.

---

## Next Steps (After Launch)

✅ **Tonight**: Get it running, verify dashboards load
✅ **Soon**: Change Grafana password
✅ **Session 2**: Convert to persistent volumes, backups
✅ **Session 3**: Add GPU metrics (when K80 installed), email alerts
✅ **Future**: Add Plex, UPS, Unifi stats; create mobile alerts

---

## The Big Picture

You've built:
- ✅ Stable remote Atlas access
- ✅ Working Docker AI stack (Ollama)
- ✅ Distributed storage (internal + USB dock)
- ✅ **NOW**: Real-time observability

The infrastructure is healthy. The monitoring just gives you **visibility**.

You're no longer flying blind on a remote server.

---

## Questions?

If something doesn't work during deployment:
1. Check logs: `docker logs [container_name]`
2. Verify Tailscale IP: `tailscale ip -4`
3. Test Prometheus health: `curl http://localhost:9090/-/healthy`
4. Restart everything: `docker compose down && docker compose up -d`

If Grafana won't load dashboards:
```bash
docker compose restart grafana
# Wait 15 seconds
# Refresh browser
```

---

**You're 20 minutes from real-time visibility into your entire infrastructure.**

Let's go.
