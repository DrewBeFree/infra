# answering-agent

AI voice answering and follow-up for small service businesses. A Retell voice agent answers calls, collects job details, the Python backend drafts a personalized SMS with available appointment slots, and the dashboard keeps a human in the loop before sending.

| Field | Value |
| --- | --- |
| Type | agent |
| Repo | https://github.com/DrewBeFree/answering-agent |
| Local path | `agents/answering-agent` |

## How It Works

Answering Agent is a white-label AI voice answering service for small service businesses (HVAC, roofing, tree service, contractors, etc.). When a customer calls, a Retell AI agent answers and has a real-time conversation — collecting the caller's name, address, service need, and urgency. After the call, a post-call webhook fires, Claude drafts a personalized SMS reply with available appointment slots, and the draft routes to the dashboard for human review before sending.

### Pipeline

```
Customer calls Twilio number
  → Retell AI agent answers (live voice conversation)
    → Collects: name, address, service type, urgency, requested day
      → Call ends → Retell fires POST /retell/post-call
        → orchestrator.py: books agreed slot on Google Calendar if structured slot data is present
          → Claude drafts personalized SMS reply
            → Draft + agreed appointment written to Supabase
              → Slack notification sent
                → Dashboard (answer.kybernet.tech) shows draft for review
                  → Human clicks Send → /send → Twilio SMS to caller
```

### Components

| Component | File | Role |
| --- | --- | --- |
| FastAPI server | `app.py` | Retell + Twilio webhook handlers, /send endpoint, auto-deploy webhook |
| Orchestrator | `orchestrator.py` | Loads client KB + slots, books confirmed appointments, calls Claude, validates output, writes to Supabase |
| Client KB | `clients/<id>/kb.yaml` | Per-client business config: services, hours, guardrails, technicians |
| Prompt generator | `generate_prompt.py` | Builds Retell global prompt from KB YAML |
| Generated prompt | `clients/<id>/prompt.txt` | Output of generate_prompt.py — paste into Retell Global Prompt |
| Dashboard | `docs/` | Static GitHub Pages site — 4-column board: New / Drafted / Sent / Escalated |
| Voicemail greeting | `docs/old-lady-vm2.mp3` | ElevenLabs-generated greeting (currently unused — Retell handles calls) |

### Infrastructure

| Component | Detail |
| --- | --- |
| Service | `answering-api.service` — systemd user service on Atlas |
| Public API | Cloudflare Tunnel at `api.kybernet.tech` |
| Auto-deploy | Push to `main` → GitHub Actions → `POST /webhook/deploy` → git pull + restart |
| Dashboard | GitHub Pages (`docs/` folder, CNAME `answer.kybernet.tech`) |
| Voice AI | Retell AI agent — handles inbound calls on the Twilio number |
| Telephony | Twilio — phone number, Retell voice routing, outbound SMS |
| LLM | Claude (Anthropic) — post-call SMS drafting and lead classification |
| Database | Supabase — leads table (caller info, transcript, draft reply, status) |

### Client Onboarding

Each client gets a folder under `clients/`:

```
clients/
  a-couple-two-trees/
    kb.yaml       ← business config
    prompt.txt    ← generated Retell global prompt
```

To onboard a new client:
1. Create `clients/<client-id>/kb.yaml` with their business info
2. Run `python generate_prompt.py <client-id>` — generates `prompt.txt`
3. Paste `prompt.txt` into Retell → Global Prompt
4. Build Retell flow nodes (Greeting → Service → Name → Address → Urgency → Day → Confirm → End)
5. Set Retell post-call webhook to `https://api.kybernet.tech/retell/post-call`
6. Wire the client's Twilio number to Retell

### Retell Agent Setup

The Retell agent uses two layers:

- **Global Prompt** — business knowledge only: services, service area, tone, guardrails, closing line. Generated from `kb.yaml`.
- **Flow nodes** — handle information collection deterministically (Flex Mode). Variables extracted: `customer_name`, `service_address`, `service_type`, `problem_description`, `urgency`, `requested_day`, `appointment_requested`, `service_area_valid`, `caller_confirmed`, `confirmed_slot`.

`confirmed_slot` should be structured data from the chosen availability result:

```json
{
  "start": "2026-05-26T15:00:00+00:00",
  "end": "2026-05-26T16:30:00+00:00",
  "tech_id": "drew",
  "label": "Tuesday May 26 at 11 AM"
}
```

If Retell sends only human text, the dashboard will show it, but the backend escalates the lead instead of guessing and risking a double booking.

### Knowledge Base (`clients/<id>/kb.yaml`)

Contains business info the orchestrator uses to craft replies: services offered, service area, tone, technician list, scheduling preferences, and guardrails (phrases never to promise). Edit this file to update responses, then re-run `generate_prompt.py --force` to regenerate the Retell prompt.

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

- **New** — call received, not yet processed
- **Drafted** — Claude has written a reply, awaiting human review
- **Sent** — SMS dispatched to caller
- **Escalated** — needs human attention (validation failed or ambiguous intent)

Click any card to open the full detail modal. From there you can Send, Escalate, or Remove the lead.

Cards with a confirmed appointment show a green **Booked** pill; hovering reveals the agreed time.

### Pending

- A2P 10DLC carrier approval — outbound SMS to real customers blocked until approved
- `client_id` multi-tenancy — orchestrator currently hardcoded to `a-couple-two-trees` KB
