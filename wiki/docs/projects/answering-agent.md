# answering-agent

An AI-powered voicemail response system for SMBs. Captures voicemails, drafts personalized SMS responses with available appointment slots, and routes them for human approval.

| Field | Value |
| --- | --- |
| Type | agent |
| Repo | https://github.com/DrewBeFree/answering-agent |
| Local path | `agents/answering-agent` |

## How It Works

Answering Agent is an AI-powered voicemail response system for small businesses. When a customer calls the Twilio number, the agent records and transcribes the voicemail, drafts a personalized SMS reply with available appointment slots, and routes the draft for human approval before sending.

### Pipeline

```
Customer calls Twilio number
  → /twilio/voice returns TwiML (greet + record)
    → Twilio transcribes recording
      → /twilio/transcription receives transcript + caller number
        → orchestrator.py: loads KB + slots, calls Claude API
          → Claude drafts personalized SMS reply
            → Draft written to Supabase
              → Slack notification sent
                → Dashboard (answer.kybernet.tech) shows draft for review
                  → Human clicks Send → /send → Twilio SMS to caller
```

### Components

| Component | File | Role |
| --- | --- | --- |
| FastAPI server | `app.py` | Twilio webhook handlers, /send endpoint, auto-deploy webhook |
| Orchestrator | `orchestrator.py` | Loads KB + slots, calls Claude, validates output, writes to Supabase |
| Knowledge base | `kb.yaml` | Business info (services, hours, guardrails) Claude uses to personalize responses |
| Dashboard | `docs/` | Static GitHub Pages site — 4-column board: New / Drafted / Sent / Escalated |

### Infrastructure

| Component | Detail |
| --- | --- |
| Service | `answering-api.service` — systemd user service on Atlas |
| Public API | Cloudflare Tunnel at `api.kybernet.tech` |
| Auto-deploy | Push to `main` → GitHub Actions → `POST /webhook/deploy` → git pull + restart |
| Dashboard | GitHub Pages (`docs/` folder, CNAME `answer.kybernet.tech`) |

### Knowledge Base (`kb.yaml`)

Contains business info the agent uses to craft replies: services offered, service area, tone, technician list, scheduling preferences, and guardrails (phrases never to promise). Edit this file to keep responses accurate without touching code.

### Service Management

```bash
# Status
systemctl --user status answering-api.service

# Restart
systemctl --user restart answering-api.service

# Live logs
journalctl --user -u answering-api.service -f
```

### Reviewing Drafts

Open [answer.kybernet.tech](https://answer.kybernet.tech). Leads are organized into four columns:

- **New** — voicemail received, not yet processed
- **Drafted** — Claude has written a reply, awaiting human review
- **Sent** — SMS dispatched to caller
- **Escalated** — needs human attention (validation failed or ambiguous intent)

Click any card to open the full detail modal. From there you can Send, Escalate, or Remove the lead.

### Pending

- A2P 10DLC carrier approval — outbound SMS to real customers blocked until approved
- Google Calendar free/busy integration (slots currently computed from schedule config only)
