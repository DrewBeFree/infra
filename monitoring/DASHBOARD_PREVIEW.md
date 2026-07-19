# Dashboard Preview - What You'll See

## Atlas Overview Dashboard

When you log in and click "Atlas Overview", you'll see (top to bottom):

```
┌─────────────────────────────────────────────────────────────────┐
│ CPU Usage %                      │ Memory Usage %               │
│ ┌─────────────────────────┐      │ ┌─────────────────────────┐  │
│ │        Line chart        │      │ │      Line chart         │  │
│ │  Spikes = heavy work     │      │ │  Should stay < 80%      │  │
│ │  Smooth = balanced load  │      │ │  Steady = healthy       │  │
│ └─────────────────────────┘      │ └─────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│ Load Average (5m)                 │ System Temperature          │
│ ┌─────────────────────────┐      │ ┌─────────────────────────┐  │
│ │  Line chart, 0-8 scale   │      │ │ Thermal monitoring      │  │
│ │  < 4 = no congestion     │      │ │ Watch for trending up   │  │
│ │  > 8 = Atlas is maxed    │      │ │ Healthy: 30-45°C        │  │
│ └─────────────────────────┘      │ └─────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│ Disk Usage by Device                                            │
│ ┌───────────────────────────────────────────────────────────────┐│
│ │ Multi-line chart, one line per drive                         ││
│ │ sda, sdb (internal), sdc-sdf (data drives), sdh-i (Reds)    ││
│ │ Red line: watch for anything crossing 80%                    ││
│ └───────────────────────────────────────────────────────────────┘│
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│ Active Containers              │ Ollama Health Status          │
│ ┌──────────────────────┐      │ ┌──────────────────────────┐  │
│ │  Pie chart           │      │ │  Big green "UP" badge    │  │
│ │  Count of running    │      │ │  or red "DOWN" alert     │  │
│ │  containers          │      │ │  (no data = still ok)    │  │
│ └──────────────────────┘      │ └──────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│ Ollama VRAM Usage by Model     │ Docker Container Memory      │
│ ┌──────────────────────┐      │ ┌──────────────────────────┐  │
│ │  Donut chart         │      │ │  Line chart             │  │
│ │  Which models are    │      │ │  Memory per container   │  │
│ │  loaded in memory    │      │ │  Spikes = inference     │  │
│ └──────────────────────┘      │ └──────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
```

**Refresh rate**: 30 seconds
**Time range**: Last 6 hours
**Mobile**: Panels stack vertically, same data

---

## Storage & SMART Health Dashboard

When you click "Storage & SMART Health", you'll see:

```
┌─────────────────────────────────────────────────────────────────┐
│ SMART Health Status by Device                                   │
│ ┌───────────────────────────────────────────────────────────────┐│
│ │ Device  │ Status                                              ││
│ │ ─────────────────────────────────────────────────────────────── ││
│ │ sda     │ 🟢 PASS                                             ││
│ │ sdb     │ 🟢 PASS                                             ││
│ │ sdc     │ 🟢 PASS                                             ││
│ │ sdh     │ 🟢 PASS  (your Red #1)                              ││
│ │ sdi     │ 🟢 PASS  (your Red #2)                              ││
│ │ sdk     │ 🟢 PASS  (external)                                 ││
│ └───────────────────────────────────────────────────────────────┘│
│ 🚨 If any shows RED → immediate attention needed                 │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│ Reallocated Sectors              │ UDMA CRC Errors             │
│ (Bad blocks being recovered)     │ (USB bridge issues)         │
│ ┌───────────────────────────┐   │ ┌───────────────────────────┐│
│ │  Line chart, 0+ scale      │   │ │  Line chart, 0+ scale     ││
│ │  Healthy = flat at 0       │   │ │  Red Reds may show data   ││
│ │  < 10 = age, watch it      │   │ │  Growing = cable problem  ││
│ │  > 10 = serious aging      │   │ │  Spikes = USB stress      ││
│ └───────────────────────────┘   │ └───────────────────────────┘│
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│ Disk Temperature Monitoring                                     │
│ ┌───────────────────────────────────────────────────────────────┐│
│ │ Multi-line chart (every drive)                                ││
│ │ sda: 32°C                                                     ││
│ │ sdh (Red): 38°C                                               ││
│ │ sdi (Red): 39°C                                               ││
│ │ ✓ All healthy (< 45°C for Reds)                              ││
│ │ ⚠ Yellow line at 40°C = warning threshold                    ││
│ │ 🔴 Red line at 50°C = critical                               ││
│ └───────────────────────────────────────────────────────────────┘│
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│ Disk Read Speed                  │ Disk Write Speed            │
│ ┌───────────────────────────┐   │ ┌───────────────────────────┐│
│ │  Line chart (MB/s)        │   │ │  Line chart (MB/s)        ││
│ │  One line per device      │   │ │  One line per device      ││
│ │  Normal: 50-150 MB/s      │   │ │  Normal: 50-150 MB/s      ││
│ │  Drops = detection point  │   │ │  Spikes = heavy I/O       ││
│ └───────────────────────────┘   │ └───────────────────────────┘│
└─────────────────────────────────────────────────────────────────┘
```

**Refresh rate**: 60 seconds (SMART queries are slower)
**Time range**: Last 24 hours
**Mobile**: Table scrolls, charts stack

---

## Why These Specific Metrics Matter for YOU

### Overview Dashboard

- **CPU/Memory/Load**: Tells you if Atlas is breathing or struggling
- **Temperature**: Early warning for hardware problems
- **Disk Space**: Prevents emergency "drive full" incidents
- **Container count**: Quick sanity check (should be ~6-8 steady)
- **Ollama status**: Know if your AI stack is alive
- **Model VRAM**: See which models are loaded (helps tune inference)

### Storage Dashboard

- **SMART Health**: The one metric that predicts failure 95% of the time
- **Reallocated sectors**: Your Reds showed some — this tracks if it's stable or growing
- **UDMA CRC errors**: Specific to USB bridges (your Reds will probably show some spikes)
- **Temperature**: Disks die from heat; Reds are especially thermal-sensitive
- **I/O speed**: Baseline for performance; drops indicate problems
- **Overall**: Tells you if your Reds are "annoying but stable" or "failing soon"

---

## Typical Healthy Patterns

### CPU/Memory
- CPU: Spiky during Ollama inference, flat otherwise
- Memory: Baseline 20-30%, spikes to 50-70% during inference
- Load: < 2 most of the time, spikes during work

### Storage
- All drives: SMART = PASS
- No reallocated sectors OR stable count
- UDMA CRC errors: 0 or occasional isolated spikes
- Temperature: 30-40°C normal, < 45°C safe, > 50°C = thermal issue

### Ollama
- Status: UP (green)
- VRAM usage: matches loaded models (nomic-embed-text ~1.5GB, llama3.2:1b ~2GB)
- Memory spike: visible during inference, returns to baseline after

---

## What to Do If You See Red Flags

| Symptom | Severity | Action |
|---------|----------|--------|
| SMART Health = FAIL | 🔴 Critical | Offline drive immediately. Data loss risk. |
| Reallocated sectors > 100 | 🔴 Critical | Drive failing. Plan replacement. |
| Disk temp > 55°C | 🔴 Critical | Thermal issue. Check airflow. Offline if > 60°C. |
| Memory > 95% | 🟡 Warning | Check what's using RAM. Potential crash risk. |
| Disk space < 5% | 🟡 Warning | Clean up storage. Risk of filesystem corruption. |
| Load > 8 | 🟡 Warning | Atlas is struggling. Reduce concurrent workload. |
| UDMA CRC spikes | ℹ️ Info | USB bridge stress. Check cable. Consider reseating Reds. |

---

## Baseline You Should Capture

**The first time things run smoothly**, record:
- CPU idle %
- Memory baseline (empty)
- Load average (idle)
- Temperature of each drive
- I/O speed per drive

This gives you a **normal** to compare against when debugging.

---

## Mobile Experience

On phone/tablet, Grafana will:
- Stack all panels vertically (no 2-column layout)
- Make text larger and touch-friendly
- Auto-fit width
- Still show all data, just different layout

**Perfect for checking in from anywhere on your Tailscale network.**

---

## Next-Level Monitoring (Session 2+)

Once this is stable, we can add:
- GPU metrics (when K80 installed)
- Email/Slack alerts ("Disk at 85%, SMART warning detected")
- Historical analysis (weekly trends)
- Plex metrics + UPS monitoring
- Unifi network stats
- Backup job status

But first: **get the foundation running.**

---

That's what's waiting for you in Grafana.

Let me know when you've deployed, and we'll verify dashboards are loading.
