# LLM Inference Benchmarks

> Last generated: 2026-06-09 09:20:15

Inference performance across machines and models. Before/after P40 GPU installation on Atlas.

---

## Latest Results

### Alienware — 2026-06-09 08:58
Host: `http://localhost:11434`

| Model | Context | Tokens/sec | Prompt Latency |
|-------|---------|-----------|----------------|
| `qwen2.5:14b` | 2048 | **13.8** | 157ms |
| `qwen2.5:14b` | 4096 | **13.4** | 144ms |

### Atlas — 2026-06-09 08:59
Host: `http://localhost:11434`

| Model | Context | Tokens/sec | Prompt Latency |
|-------|---------|-----------|----------------|
| `llama3.2:3b` | 2048 | **11.8** | 1766ms |
| `qwen2.5:14b` | 2048 | **3.4** | 7223ms |

---

## Machine Comparison (qwen2.5:14b @ 2048 ctx)

Direct comparison on the same model across all machines.

| Machine | Tokens/sec | Prompt Latency | GPU |
|---------|-----------|----------------|-----|
| Alienware (RTX 4070 TI Super) | **13.8** | 157ms | RTX 4070 TI Super |
| Atlas (PowerEdge) | **3.4** | 7223ms | CPU-only → Tesla P40 |

---

## Run History

### Alienware

| Date | Models Tested | Avg Tokens/sec |
|------|---------------|----------------|
| 2026-06-09 08:58 | `qwen2.5:14b` | 13.6 |

### Atlas

| Date | Models Tested | Avg Tokens/sec |
|------|---------------|----------------|
| 2026-06-09 08:59 | `qwen2.5:14b`, `llama3.2:3b` | 7.6 |

---

## Notes

- All benchmarks run 2-3 iterations per model and context length
- Context length tests: 2048, 4096, 8192 tokens
- Generation target: 100 tokens per run
- Grafana dashboard: [http://atlas:3001](http://atlas:3001) → Benchmarks
- Scripts: `benchmark_inference.py`, `benchmark_exporter.py`
- Run after P40 install: `python3 /tmp/benchmark_inference.py --host http://localhost:11434 --output-dir /home/drew/benchmarks/results --machine-name atlas`
