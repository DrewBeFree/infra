# Tools

Quick reference for every tool in the homelab stack.

## Alienware Tools

### Ollama

Local LLM runtime. Pulls and serves open-source models (Llama, Mistral, Phi, Qwen) via a REST API at `127.0.0.1:11434`. GPU-accelerated. The engine that runs inference — other tools (Open WebUI, OpenClaw) talk to it.

### Open WebUI

Browser-based chat UI that connects to Ollama (or OpenAI-compatible APIs). Manage model downloads, run conversations with system prompts — no coding required.

### OpenClaw

Custom AI gateway framework. Routes requests between clients and LLM backends, handles API key management, rate limiting, and model routing. Frontend/testing side lives on Alienware for active development; gateway moves to Atlas once stable.

**Plugins:** ollama, slack, memory-core, web-search, anthropic

### VS Code

Primary dev environment. All repos live in WSL under `~/Documents/GitHub/`.

### Whisper (realtime)

OpenAI's speech-to-text model. Realtime variant does live transcription (mic → text). GPU-heavy; stays on Alienware for low-latency use. Batch/offline jobs move to Atlas.

---

## Atlas Tools

### Docker + Portainer

Docker runs containerized services. Portainer is a web UI for managing Docker — start/stop containers, view logs, manage volumes without touching the CLI. Foundation for everything else on Atlas.

### ChromaDB

Vector database for semantic search. Stores embeddings so you can query "what's most relevant to this prompt" and feed results to the LLM. Used by RAG/ingestion pipelines.

### Syncthing

Peer-to-peer file sync between machines (Alienware ↔ Atlas) without a cloud intermediary. Good for notes, project files, or ingestion drop folders.

### Watchdog

File system watcher — monitors a folder for new files and triggers a script when something appears. Example: drop a PDF in `/inbox`, Watchdog fires an ingestion pipeline.

### Ingestion Pipelines

The ETL layer. Takes raw inputs (PDFs, notes, URLs, transcripts), chunks and embeds them, loads into ChromaDB for retrieval. Python scripts, often chained with Watchdog.

### Grafana

Visualization and dashboarding. Connects to data sources (Prometheus, Postgres, logs) and displays metrics as charts/panels. Monitoring service health, system stats, pipeline throughput.

### Plex

Media server. Indexes movie/TV/music libraries and streams to any device. Needs 24/7 uptime for remote access.

### Slack Integrations / Make Automations

Slack bots/webhooks for alerts, summaries, and notifications. Make (formerly Integromat) chains API calls across apps. Both need persistent uptime → Atlas.

---

## Decision Rule

> "Does this need to stay alive while the desktop is asleep, rebooting, or gaming?"

- **YES** → Atlas
- **NO** → Alienware
