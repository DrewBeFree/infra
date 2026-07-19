# Atlas Monitoring Stack - Deployment & Access Guide

## What You're Getting

- **Prometheus**: Time-series metrics database (9090)
- **Grafana**: Beautiful dashboards (3000)
- **node-exporter**: System metrics (CPU, RAM, disk, temp)
- **smartctl-exporter**: SMART health for your Reds & all drives
- **cAdvisor**: Docker container metrics
- **ollama-exporter**: Custom exporter for your Ollama AI stack

Two pre-built dashboards:
1. **Atlas Overview** - System health, containers, load, temps, Ollama status
2. **Storage & SMART Health** - Your Reds, disk errors, temperatures, I/O

---

## Deployment (Do This First)

### 1. Verify you're in the right directory

```bash
ls -la ~/docker-compose.yml ~/prometheus.yml ~/ollama-exporter.js
```

Should show 3 files. If not, you're missing files—check the paths.

### 2. Start the stack

```bash
cd ~
docker compose up -d
```

Watch for output like:
```
Creating atlas-prometheus ... done
Creating atlas-grafana ... done
Creating atlas-node-exporter ... done
Creating atlas-smartctl-exporter ... done
Creating atlas-cadvisor ... done
Creating atlas-ollama-exporter ... done
```

### 3. Verify all containers are healthy

```bash
docker ps
```

All 6 containers should show `Up` and healthy.

### 4. Check Prometheus is scraping

```bash
curl http://localhost:9090/api/v1/targets
```

Should show all 6 targets as "UP" (may take 30 seconds to populate).

---

## Mobile Access via Tailscale (Do This Next)

### 1. Find your Tailscale IP on Atlas

```bash
tailscale ip -4
```

Note this IP. Let's call it `<TAILSCALE_IP>`.

### 2. Open Grafana on Mobile

On any device on your Tailscale network:

```
http://<TAILSCALE_IP>:3000
```

**Login:**
- Username: `admin`
- Password: `atlas_admin`

### 3. (Optional) Change Grafana Password for Security

In Grafana UI:
- Click your avatar (bottom left)
- Change password
- Restart container: `docker compose restart grafana`

---

## First-Time Dashboard Setup

### Dashboards Load Automatically

When you log in, you should see:
- **Atlas** folder
- **Atlas Overview** dashboard
- **Storage & SMART Health** dashboard

Click into either one—they're already connected to Prometheus.

### If Dashboards Don't Load

```bash
# Check provisioning
docker exec atlas-grafana ls -la /etc/grafana/provisioning/dashboards/json/

# Restart Grafana
docker compose restart grafana

# Wait 10 seconds, then refresh browser
```

---

## What to Monitor Immediately

### Overview Tab
- **CPU Usage %** - spike above 80% is worth checking
- **Memory Usage %** - 85%+ is getting tight
- **Load Average (5m)** - > 8 means congestion
- **System Temperature** - watch for trending up
- **Disk Usage** - any drive > 85% should trigger cleanup

### Storage Tab
- **SMART Health Status** - should all be PASS
- **Reallocated Sectors** - if > 10 on any drive, it's aging
- **UDMA CRC Errors** - indicates USB bridge/cable issues (your Reds might show this)
- **Disk Temperature** - Reds typically safe up to 45°C
- **Read/Write Speed** - baseline so you know if performance degrades

### Why This Matters Tonight

Your Reds showed:
- **sdh**: mostly USB translation issues (UDMA CRC errors expected)
- **sdi**: some actual medium errors (reallocated sectors)

The Storage dashboard will **show you in real-time** if these are stable or getting worse.

---

## Tailscale Mobile Optimization

Grafana detects mobile viewport and auto-adjusts:
- Panels stack vertically
- Touch-friendly controls
- Fast refresh (30s default)

**Pro tip:** Save the Grafana URL to your phone's home screen as a web app for one-tap access.

---

## Converting to Persistent Storage (Later)

Once you confirm everything works, we'll:

1. Create Docker volumes for Prometheus & Grafana
2. Update docker-compose.yml
3. Migrate data without losing history
4. Restart and verify

**For now:** Ephemeral is fine. You can always export dashboards if needed.

---

## Troubleshooting

### Grafana won't start

```bash
docker compose logs grafana
# Check for port conflicts or permission issues
```

### Prometheus not scraping

```bash
docker compose logs prometheus
# Check prometheus.yml syntax
```

### SMART metrics missing

```bash
# smartctl-exporter needs privileged mode (it does have it)
docker exec atlas-smartctl-exporter smartctl -a /dev/sda
# If that fails, run:
docker compose restart smartctl-exporter
```

### Can't connect via Tailscale

```bash
# Verify Tailscale is running
tailscale status

# Verify Grafana is listening
curl http://localhost:3000

# Try accessing by container hostname (Docker DNS)
http://atlas-grafana:3000
```

---

## Next Session (When Physically Back)

We'll:
1. Add persistent volumes to prometheus & grafana configs
2. Test drive recovery with `smartctl -a /dev/sdh` and `/dev/sdi`
3. Decide if Reds need reformatting or if they're stable long-term
4. Add GPU metrics if you have the K80 installed by then

---

## Important Notes

- **Password change strongly recommended** for security (especially if accessible remotely)
- **Metrics retention**: Set to 7 days (edge cases rarely need older data)
- **Refresh intervals**: 30s for overview, 60s for SMART (doesn't hammer disk)
- **Alerts**: Currently configured but not sending anywhere (you can add email/Slack later)

---

## Quick Commands Reference

```bash
# Check container status
docker ps

# View logs for any service
docker logs atlas-prometheus
docker logs atlas-grafana
docker logs atlas-smartctl-exporter

# Restart everything
docker compose restart

# Stop stack
docker compose down

# See if Prometheus is scraping
curl http://localhost:9090/api/v1/query?query=up

# Test SMART exporter directly
curl http://localhost:9633/metrics | grep smartctl
```

---

**You now have operational visibility into your infrastructure.**

Access from mobile: `http://<TAILSCALE_IP>:3000`
Default login: `admin` / `atlas_admin`

Enjoy the dashboards. See you next session for persistence & deeper diagnostics.
