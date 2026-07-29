# Atlas P40 Grafana No Data — 2026-07-28

Host/worktree: `/home/drew/GitHub/infra`
Branch: `dev`
Commit at start: `2a136f5 overnight: add infra app index`
Remote: `origin/dev` (`git@github.com:DrewBeFree/infra.git`)

## Outcome

Restored Atlas P40 GPU telemetry for the existing Grafana dashboard `Atlas P40 Benchmark Summary` (`uid: atlas-p40-summary`).

Root cause was not proven GPU inactivity. The live NVIDIA exporter service was failing because its systemd unit referenced a stale root-owned path:

```text
/home/drew/monitoring/nvidia-smi-exporter.py
```

The working exporter already existed in the infra repo:

```text
/home/drew/GitHub/infra/monitoring/nvidia-smi-exporter.py
```

The user service was patched outside the repo:

```text
/home/drew/.config/systemd/user/atlas-nvidia-smi-exporter.service
```

Current `ExecStart`:

```ini
ExecStart=/usr/bin/python3 /home/drew/GitHub/infra/monitoring/nvidia-smi-exporter.py --host 0.0.0.0 --port 9701
```

## Why this was done

Drew saw `No data` in Grafana at:

```text
https://grafana.drewbefree.com/d/atlas-p40-summary/atlas-p40-benchmark-summary?orgId=1&from=2026-07-28T23:08:20.926Z&to=2026-07-29T00:28:20.926Z&timezone=browser&var-DS_PROMETHEUS=PBFA97CFB590B2093&refresh=30s
```

The question was whether that meant Qwen/Ollama was not using the P40. Evidence showed Prometheus could not scrape the GPU exporter at all, so Grafana had no basis to display GPU metrics for that window.

## Commands run

```bash
systemctl --user status atlas-nvidia-smi-exporter.service
journalctl --user -u atlas-nvidia-smi-exporter.service -n 50
nvidia-smi
curl -s http://localhost:9090/api/v1/targets | jq -r '.data.activeTargets[] | select(.labels.job=="nvidia_gpu")'
curl -s 'http://localhost:9090/api/v1/query?query=up%7Bjob%3D%22nvidia_gpu%22%7D' | jq .
curl -s -u admin:atlas_admin http://localhost:3001/api/dashboards/uid/atlas-p40-summary | jq -r '.. | objects | select(has("expr")) | .expr'
python3 -m py_compile /home/drew/GitHub/infra/monitoring/nvidia-smi-exporter.py
systemctl --user daemon-reload
systemctl --user restart atlas-nvidia-smi-exporter.service
curl -s http://localhost:9701/metrics | grep -E 'nvidia_gpu_(scrape_success|temperature_celsius|utilization_percent|memory_used_bytes|memory_total_bytes|power_draw_watts)'
curl -fsS 'http://localhost:9090/api/v1/query?query=up%7Bjob%3D%22nvidia_gpu%22%7D'
curl -fsS 'http://localhost:9090/api/v1/query?query=max(nvidia_gpu_temperature_celsius)'
curl -fsS 'http://localhost:9090/api/v1/query?query=max(nvidia_gpu_memory_used_bytes)'
curl -fsS 'http://localhost:9090/api/v1/query?query=max(nvidia_gpu_utilization_percent)'
```

Observed result:

```text
atlas-nvidia-smi-exporter.service: active
ExecStart=/usr/bin/python3 /home/drew/GitHub/infra/monitoring/nvidia-smi-exporter.py --host 0.0.0.0 --port 9701
up{job="nvidia_gpu"}=1
max(nvidia_gpu_temperature_celsius)=89
max(nvidia_gpu_memory_used_bytes)=162529280
max(nvidia_gpu_utilization_percent)=0
Grafana dashboard title: Atlas P40 Benchmark Summary
```

## Related Hermes/Ollama finding

Separate from Grafana, Hermes/Ollama model selection looked malformed in this session.

`/home/drew/.hermes/config.yaml` currently parses as:

```text
model.provider=ollama
model.default=qwen2.5-coder:7b-64k
providers.ollama.models type=str
```

Ollama logs during the failing window included requests using the entire model list as if it were one model path:

```text
GET /v1/models/["qwen2.5:7b","qwen2.5:32b","qwen2.5-coder:7b","qwen2.5-coder:7b-64k","llama3.1:8b","llama3.1:70b","llama3.2:1b","llama3.2:3b","gemma4:latest"]
POST /v1/chat/completions 400
```

Direct Ollama model metadata check for `qwen2.5-coder:7b-64k` succeeded, so the model exists. The likely issue is Hermes config/session state, not the Qwen model file.

Recommended config shape for a later Hermes fix:

```yaml
providers:
  ollama:
    base_url: http://localhost:11434/v1
    models:
      - qwen2.5:7b
      - qwen2.5:32b
      - qwen2.5-coder:7b
      - qwen2.5-coder:7b-64k
      - llama3.1:8b
      - llama3.1:70b
      - llama3.2:1b
      - llama3.2:3b
      - gemma4:latest
```

Start a fresh Hermes session after that change so the active session no longer carries the bad model-list value.

## Commit and push

Docs/handoff commit pending at time of log creation.

## Safety notes

- No Prometheus or Grafana volumes were deleted, pruned, or restored.
- No monitoring dashboard JSON was rewritten.
- No secrets or Grafana credentials were recorded beyond the existing local admin username/password already present in repo docs.
- The live change was a user-level systemd unit path update outside the repo.
- Historical Prometheus samples for the period while the exporter was down cannot be recovered unless a separate backup contains those samples.

## Next recommended step

Fix `/home/drew/.hermes/config.yaml` so `providers.ollama.models` is a YAML list, then start a new Hermes session and run a small Qwen prompt while watching:

```bash
watch -n 2 'curl -fsS "http://localhost:9090/api/v1/query?query=max(nvidia_gpu_utilization_percent)" | jq -r .data.result[0].value[1]'
```
