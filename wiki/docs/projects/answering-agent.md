# answering-agent

An AI-powered voicemail response system for SMBs. Captures voicemails, drafts personalized SMS responses with available appointment slots, and routes them for human approval.

| Field | Value |
| --- | --- |
| Type | agent |
| Repo | https://github.com/DrewBeFree/answering-agent |
| Local path | `agents/answering-agent` |

## How It Works

Answering Agent is an AI-powered voicemail response system for small businesses. When a customer leaves a voicemail via Google Voice, the agent captures the transcript, drafts a personalized SMS reply with available appointment slots, and routes the draft for human approval before sending.

### Pipeline

```
Google Voice voicemail
  → Gmail transcript email
    → Make mailhook (filter + parse)
      → POST to /answering/inbound (PowerEdge)
        → Orchestrator: KB + slots + Claude → draft
          → Draft written to Supabase
            → Web UI: review + click-to-send
```

### Components

| Component | File | Role |
| --- | --- | --- |
| Gmail poller | `gmail_poller.py` | Watches Gmail for new voicemail transcript emails |
| Orchestrator | `orchestrator.py` | Pulls KB + slots, calls Claude, writes draft to Supabase |
| Knowledge base | `kb.yaml` | Business info Claude uses to personalize responses |
| Web UI | (Supabase + frontend) | Shows pending drafts for review and one-click send |

### Knowledge Base (`kb.yaml`)

The KB contains business info the agent uses to craft replies: services offered, hours, contact info, typical appointment slots. Edit this file to keep responses accurate.

### Running the Agent

```bash
# On Atlas
python3 orchestrator.py
```

The agent runs as a persistent service on Atlas and listens for incoming webhooks from Make.

### Reviewing Drafts

Open the web UI (Supabase-backed) to see pending draft responses. Each draft shows:
- The original voicemail transcript
- The proposed SMS reply
- Available appointment slots mentioned

Click **Send** to dispatch the SMS via Google Voice, or **Edit** to modify the draft before sending.

### Status

v0 prototype — orchestrator skeleton and Gmail poller built. Web UI pending.
