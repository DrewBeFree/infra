# Agents

Agents are autonomous software processes that do real work. They run on infrastructure (typically Atlas), respond to events or schedules, and produce tangible outputs — messages sent, drafts written, data updated. They're not chatbots you talk to; they're pipelines with intelligence wired in.

---

## Bob

A Slack bot backed by a local LLM on Atlas. Responds to DMs and @mentions using `llama3.2:1b` — no cloud API, no cost per message.

| | |
|---|---|
| Repo | [DrewBeFree/bob](https://github.com/DrewBeFree/bob) |
| Local path | `agents/bob` |
| Runs on | Atlas (`bob.service` — systemd user service) |
| Project page | [projects/bob](../projects/bob.md) |

### How it works

1. Slack sends an event (DM or @mention) via Socket Mode to the bot process running on Atlas
2. Bob's `bot.py` receives it, builds a prompt (tiny system prompt + today's date + the user's message)
3. Calls Ollama's `/api/chat` at `http://127.0.0.1:11434` — fully local, no external API
4. Streams the response back to Slack

### Key design choices

- **Local model only** — `llama3.2:1b` keeps response times fast on Atlas CPU; no GPU needed for conversation
- **No conversation history** — each message is stateless; Bob doesn't remember previous turns in a thread
- **Date injection** — today's date is always added to the system prompt so Bob never hallucinates the date

### Service management

```bash
# Status
systemctl --user status bob.service

# Restart (after config changes)
systemctl --user restart bob.service

# Live logs
journalctl --user -u bob.service -f
```

### Changing the model

Edit `MODEL` in `bot.py`, then restart the service. Any model pulled via `docker exec ollama ollama pull <name>` is available.

---

## Answering Agent

An AI-powered voicemail response system for small businesses. Receives inbound calls via Twilio, transcribes voicemails, drafts personalized SMS replies with available appointment slots, and routes them for human approval before sending.

| | |
|---|---|
| Repo | [DrewBeFree/answering-agent](https://github.com/DrewBeFree/answering-agent) |
| Local path | `agents/answering-agent` |
| Runs on | Atlas (`answering-api.service` — systemd user service, FastAPI) |
| Public API | [api.kybernet.tech](https://api.kybernet.tech) (Cloudflare Tunnel) |
| UI | [answer.kybernet.tech](https://answer.kybernet.tech) (GitHub Pages) |
| Project page | [projects/answering-agent](../projects/answering-agent.md) |

### How it works

```
Customer calls Twilio number
  → /twilio/voice returns TwiML (greet + record)
    → Twilio transcribes recording
      → /twilio/transcription receives transcript + caller number
        → orchestrator.py: loads KB + slots, calls Claude API
          → Claude drafts personalized SMS reply
            → Draft written to Supabase
              → Slack notification sent
                → Web UI shows draft for human review
                  → Human clicks Send → /send → Twilio SMS to caller
```

### Components

| File | Role |
|---|---|
| `app.py` | FastAPI server — Twilio webhooks, /send endpoint, auto-deploy webhook |
| `orchestrator.py` | Loads KB + computes slots, calls Claude, validates output, writes to Supabase |
| `kb.yaml` | Business info (services, hours, guardrails) Claude uses to personalize replies |
| `docs/` | Static dashboard (GitHub Pages) — 4-column board: New / Drafted / Sent / Escalated |

### Key design choices

- **Twilio end-to-end** — inbound calls, transcription, and outbound SMS all through Twilio; no Google Voice dependency
- **Human-in-the-loop** — Claude drafts, a human approves in the dashboard. No SMS goes out automatically.
- **Knowledge base (`kb.yaml`)** — editable business context so responses stay accurate without retraining
- **Supabase as state store** — drafts, status (new/drafted/sent/escalated), and audit trail
- **Auto-deploy** — push to main triggers GitHub Actions → `POST /webhook/deploy` → git pull + systemctl restart on Atlas

### Service management

```bash
# Status
systemctl --user status answering-api.service

# Restart
systemctl --user restart answering-api.service

# Live logs
journalctl --user -u answering-api.service -f
```

---

## Recap Agents

Automated meeting recap pipeline for Undeniable Reliabilly. Pulls transcripts from Google Drive and Motion, updates the knowledge base, and regenerates the Kybernet Dashboard.

| | |
|---|---|
| Repo | [DrewBeFree/recap-agents](https://github.com/DrewBeFree/recap-agents) |
| Local path | `agents/recap-agents` |
| Runs on | Atlas / scheduled |
| Dashboard | [drewbefree.github.io/recap-agents](https://drewbefree.github.io/recap-agents/) |
| Project page | [projects/recap-agents](../projects/recap-agents.md) |

### How it works

Transcripts from Google Drive and Motion are pulled, processed, and used to update a knowledge base that drives the Kybernet Dashboard — a running view of decisions, action items, and context from team meetings.

---

## Interactive Setup

Architecture and setup documentation for the homelab AI stack. Not a runnable agent — a collection of design docs covering the Alienware/Atlas split, OpenClaw architecture, and Bob's design.

| | |
|---|---|
| Repo | [DrewBeFree/interactive-setup](https://github.com/DrewBeFree/interactive-setup) |
| Local path | `agents/interactive-setup` |
| Project page | [projects/interactive-setup](../projects/interactive-setup.md) |

Contains:
- OpenClaw + Homelab architecture overview
- Bob system architecture doc
- `architecture.md` — overall agent stack design
- `specv1.md` — original spec
