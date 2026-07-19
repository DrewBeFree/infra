# ATLAS MONITORING DEPLOYMENT - COPY-PASTE INSTRUCTIONS

## You are here: Remote (not on Atlas yet)
## You need to: Get these files onto Atlas via SSH

---

## STEP 1: Create directories on Atlas

SSH into Atlas and run:

```bash
mkdir -p ~/monitoring/grafana-provisioning/datasources \
         ~/monitoring/grafana-provisioning/dashboards/json
cd ~/monitoring
pwd  # Should show /root/monitoring or /home/drew/monitoring
```

---

## STEP 2: Create docker-compose.yml

On Atlas, run:

```bash
cat > ~/monitoring/docker-compose.yml << 'COMPOSE_EOF'
```

Then paste the ENTIRE content from `/home/claude/docker-compose.yml` (from earlier in this conversation)

Then close with:

```
COMPOSE_EOF
```

Verify:
```bash
head -5 ~/monitoring/docker-compose.yml
```

Should show `version: '3.8'`

---

## STEP 3: Create prometheus.yml

On Atlas:

```bash
cat > ~/monitoring/prometheus.yml << 'PROM_EOF'
```

Paste content from `/home/claude/prometheus.yml`

```
PROM_EOF
```

Verify:
```bash
head -5 ~/monitoring/prometheus.yml
```

Should show `global:`

---

## STEP 4: Create alert.rules.yml

On Atlas:

```bash
cat > ~/monitoring/alert.rules.yml << 'ALERT_EOF'
```

Paste content from `/home/claude/alert.rules.yml`

```
ALERT_EOF
```

---

## STEP 5: Create ollama-exporter.js

On Atlas:

```bash
cat > ~/monitoring/ollama-exporter.js << 'OLLAMA_EOF'
```

Paste content from `/home/claude/ollama-exporter.js`

```
OLLAMA_EOF
```

---

## STEP 6: Create Grafana datasource config

On Atlas:

```bash
cat > ~/monitoring/grafana-provisioning/datasources/prometheus.yml << 'DATASOURCE_EOF'
```

Paste content from `/home/claude/grafana-provisioning/datasources/prometheus.yml`

```
DATASOURCE_EOF
```

---

## STEP 7: Create Grafana dashboards provisioning config

On Atlas:

```bash
cat > ~/monitoring/grafana-provisioning/dashboards/dashboards.yml << 'DASHBOARDS_EOF'
```

Paste content from `/home/claude/grafana-provisioning/dashboards/dashboards.yml`

```
DASHBOARDS_EOF
```

---

## STEP 8: Create Atlas Overview dashboard

On Atlas:

```bash
cat > ~/monitoring/grafana-provisioning/dashboards/json/atlas-overview.json << 'OVERVIEW_EOF'
```

Paste content from `/home/claude/grafana-provisioning/dashboards/json/atlas-overview.json`

```
OVERVIEW_EOF
```

---

## STEP 9: Create Storage dashboard

On Atlas:

```bash
cat > ~/monitoring/grafana-provisioning/dashboards/json/atlas-storage.json << 'STORAGE_EOF'
```

Paste content from `/home/claude/grafana-provisioning/dashboards/json/atlas-storage.json`

```
STORAGE_EOF
```

---

## STEP 10: Verify all files are there

On Atlas:

```bash
ls -la ~/monitoring/
ls -la ~/monitoring/grafana-provisioning/datasources/
ls -la ~/monitoring/grafana-provisioning/dashboards/json/
```

Should show:
- docker-compose.yml ✓
- prometheus.yml ✓
- alert.rules.yml ✓
- ollama-exporter.js ✓
- grafana-provisioning/ (dir) ✓
  - datasources/prometheus.yml ✓
  - dashboards/dashboards.yml ✓
  - dashboards/json/atlas-overview.json ✓
  - dashboards/json/atlas-storage.json ✓

---

## STEP 11: Launch the stack

On Atlas:

```bash
cd ~/monitoring
docker compose up -d
```

Watch for output:
```
Creating atlas-prometheus ... done
Creating atlas-grafana ... done
Creating atlas-node-exporter ... done
Creating atlas-smartctl-exporter ... done
Creating atlas-cadvisor ... done
Creating atlas-ollama-exporter ... done
```

---

## STEP 12: Verify health

On Atlas:

```bash
docker ps
```

All 6 containers should show `Up` and healthy (give it 30 seconds).

---

## STEP 13: Verify Prometheus is scraping

On Atlas:

```bash
curl http://localhost:9090/api/v1/targets 2>/dev/null | grep -o '"health":"[^"]*"' | sort | uniq -c
```

Should show:
```
      6 "health":"up"
```

(If you see "down", wait 30 more seconds and try again)

---

## STEP 14: Get your Tailscale IP

On Atlas:

```bash
tailscale ip -4
```

Write this down. It looks like `100.x.x.x`

---

## STEP 15: Access Grafana from mobile

On any device on your Tailscale network:

```
http://100.x.x.x:3000
```

Login:
- Username: `admin`
- Password: `atlas_admin`

---

## Done!

You should see:
- Atlas folder in Grafana
- Two dashboards: "Atlas Overview" and "Storage & SMART Health"
- Live metrics flowing in

**If something fails, run:**

```bash
docker compose logs -f [service_name]
```

Example:
```bash
docker compose logs -f prometheus
docker compose logs -f grafana
docker compose logs -f smartctl-exporter
```

---

## Notes

- All files are text-based; copy-paste works fine via SSH
- Docker Compose must be installed (`docker-compose --version`)
- Monitoring will persist until you `docker compose down`
- Next session: we convert to persistent volumes

Good luck! You've got this.
