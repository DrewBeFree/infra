# Infrastructure Tools Reference

A quick-reference guide for every tool in the Alienware / PowerEdge stack.

---

## Alienware Tools

### Ollama
Local LLM runtime. Pulls and serves open-source models (Llama, Mistral, Phi, etc.) via a REST API. GPU-accelerated. The engine that actually runs inference — other tools (Open WebUI, OpenClaw) talk to it.

### Open WebUI
Browser-based chat UI that connects to Ollama (or OpenAI-compatible APIs). Lets you talk to local models, manage model downloads, and run conversations with system prompts — no coding required.

### OpenClaw (frontend / testing)
Your custom AI gateway project. The frontend/testing side lives on the Alienware for active development. The gateway (routing, auth, API proxying) moves to the PowerEdge once stable.

### VS Code
Code editor. Primary dev environment for all repos.

### GPU Inference
Not a specific tool — refers to any workload that benefits from the Alienware's GPU: model serving via Ollama, image generation (Stable Diffusion), embeddings at speed, etc.

### Whisper (realtime)
OpenAI's speech-to-text model. The realtime variant does live transcription (mic input → text as you speak). GPU-heavy; stays on Alienware for low-latency use. Batch/offline jobs move to PowerEdge.

---

## PowerEdge Tools

### Docker + Portainer
Docker runs containerized services. Portainer is a web UI for managing Docker — start/stop containers, view logs, manage volumes — without touching the CLI. Foundation for everything else on the PowerEdge.

### ChromaDB
Vector database. Stores embeddings (chunks of text converted to numbers) so you can do semantic similarity search. Used by RAG pipelines — ingest documents, query "what's most relevant to this prompt," feed results to the LLM.

### Syncthing
Peer-to-peer file sync. Keeps folders in sync between machines (Alienware ↔ PowerEdge, or with other devices) without a cloud intermediary. Good for syncing notes, project files, or ingestion drop folders.

### Watchdog (watch folders)
File system watcher — monitors a folder for new files and triggers a script when something appears. Example: drop a PDF in `/inbox`, Watchdog fires an ingestion pipeline automatically.

### Ingestion Pipelines / Scripts
The ETL layer for your AI stack. Takes raw inputs (PDFs, notes, URLs, transcripts), chunks and embeds them, and loads them into ChromaDB for retrieval. Usually Python scripts, possibly chained with Watchdog.

### OpenClaw Gateway
The routing/auth layer of OpenClaw. Proxies requests between clients and LLM backends, handles API key management, rate limiting, and model routing. Runs as a persistent service — needs to be always-on.

### Grafana
Visualization and dashboarding tool. Connects to data sources (Prometheus, Postgres, logs) and displays metrics as charts and panels. Used for monitoring service health, system stats, pipeline throughput, etc.

### Plex
Media server. Indexes your movie/TV/music library and streams it to any device. Needs to run 24/7 for remote access; PowerEdge is the right home.

### Slack Integrations / Make Automations
Slack integrations: bots or webhooks that send messages to Slack (alerts, summaries, notifications from other services).  
Make (formerly Integromat): no-code automation platform that chains together API calls across apps — think IFTTT but more powerful. Both need persistent uptime.

### Dashboards
Generic term for any web-based status UI — could be Grafana, a custom HTML page, or a tool like Dashy/Homer that aggregates links and service status in one place.

---

## Decision Rule

> "Does this need to stay alive while the desktop is asleep, rebooting, or gaming?"

- **YES** → PowerEdge
- **NO** → Alienware
