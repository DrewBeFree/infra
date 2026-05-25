# answering-agent

AI voice answering and follow-up for small service businesses. A Retell voice agent answers calls, collects job details, the Python backend drafts a personalized SMS with available appointment slots, and the dashboard keeps a human in the loop before sending.

| Field | Value |
| --- | --- |
| Type | agent |
| Repo | https://github.com/DrewBeFree/answering-agent |
| Local path | `agents/answering-agent` |

## How It Works

Answering Agent is a white-label AI voice answering service for small service businesses (HVAC, roofing, tree service, contractors, etc.). When a customer calls, a Retell AI workflow agent answers and has a real-time conversation — collecting the caller's name, address, service need, urgency, and preferred appointment day. Mid-call, the agent queries live Google Calendar availability and locks in a slot when the caller agrees. After the call, a post-call webhook fires, Claude drafts a personalized SMS reply, and the draft routes to the dashboard for human review before sending.

### Pipeline

```
Customer calls Twilio number
  → Retell AI workflow agent answers (live voice conversation)
    → Collects: name, address, service type, urgency, requested day
      → Agent calls GET /retell/get-availability → returns open slots
        → Agent offers slots; caller agrees to one
          → Agent calls POST /retell/confirm-slot → structured slot stored server-side
            → Call ends → Retell fires POST /retell/post-call
              → orchestrator.py: books agreed slot on Google Calendar
                → Claude drafts personalized SMS reply
                  → Draft + agreed appointment written to Supabase
                    → Slack notification sent
                      → Dashboard (answer.kybernet.tech) shows draft for review
                        → Human clicks Send → /send → Twilio SMS to caller
```

### Components

| Component | File | Role |
| --- | --- | --- |
| FastAPI server | `app.py` | Retell + Twilio webhook handlers, confirm-slot store, /send endpoint, auto-deploy webhook |
| Orchestrator | `orchestrator.py` | Loads client KB + slots, books confirmed appointments, calls Claude, validates output, writes to Supabase |
| Client KB | `clients/<id>/kb.yaml` | Per-client business config: services, hours, guardrails, technicians |
| Agent prompt | `clients/<id>/prompt.txt` | Retell Global Prompt — persona, services, guardrails only (flow handled by workflow nodes) |
| Dashboard | `docs/` | Static GitHub Pages site — 4-column board: New / Drafted / Sent / Escalated |

### Infrastructure

| Component | Detail |
| --- | --- |
| Service | `answering-api.service` — systemd user service on Atlas |
| Public API | Cloudflare Tunnel at `api.kybernet.tech` |
| Auto-deploy | Push to `main` → GitHub Actions → `POST /webhook/deploy` → git pull + restart |
| Dashboard | GitHub Pages (`docs/` folder, CNAME `answer.kybernet.tech`) |
| Voice AI | Retell AI workflow agent — handles inbound calls on the Twilio number |
| Telephony | Twilio — phone number, Retell voice routing, outbound SMS |
| LLM | Claude (Anthropic) — post-call SMS drafting and lead classification |
| Database | Supabase — leads table (caller info, transcript, draft reply, confirmed slot, status) |

### Retell Agent Setup

The agent is a **workflow agent** (not pure LLM). Two layers:

- **Global Prompt** — business knowledge only: persona, services, service area, tone, guardrails. Lives in `clients/<id>/prompt.txt`. Flow instructions do NOT belong here — the workflow nodes handle those.
- **Workflow nodes** — deterministic flow: Greeting → Name → Address → Urgency → Appointment → Get Availability → Offer Times → Confirm Slot → Confirmation → End Call.

**Custom functions:**

| Function | Endpoint | Purpose |
| --- | --- | --- |
| `get_availability` | `POST /retell/get-availability` | Returns open slots from Google Calendar. Response field `slots` stored as dynamic variable `available_slots`. |
| `confirm_slot` | `POST /retell/confirm-slot` | Called mid-call when caller agrees to a time. Receives `start`, `end`, `tech_id`, `label` from `available_slots`. Stores slot server-side keyed by `call_id` for post-call webhook to use. |

**Post-call analysis fields:** `customer_name`, `service_address`, `service_type`, `problem_description`, `urgency`, `requested_day`, `appointment_requested`, `service_area_valid`.

(`confirmed_slot` is no longer an analysis field — the structured slot is captured via `confirm_slot` mid-call.)

### Availability Slot Logic

`compute_candidate_slots()` in `orchestrator.py`:
- Scans up to 14 days of business hours (Mon–Fri 9–5, Sat 10–3)
- Checks real Google Calendar free/busy via OAuth
- Respects 4-hour lead time and 30-minute buffer between appointments
- Offers slots at 9 AM, 11 AM, 1 PM, 3 PM
- **When no preferred day given:** spreads one slot per calendar day (e.g. Tue, Wed, Thu) so the caller isn't offered three same-day times
- **When caller states a preferred day:** returns multiple slots on that day

### Client Onboarding

Each client gets a folder under `clients/`:

```
clients/
  a-couple-two-trees/
    kb.yaml       ← business config
    prompt.txt    ← Retell global prompt (persona + guardrails only)
```

To onboard a new client:
1. Create `clients/<client-id>/kb.yaml` with their business info
2. Write `prompt.txt` with persona, services, guardrails (no scheduling instructions)
3. Paste `prompt.txt` into Retell → Global Prompt
4. Build Retell workflow nodes
5. Register `get_availability` and `confirm_slot` as custom functions in Retell
6. Set Retell post-call webhook to `https://api.kybernet.tech/retell/post-call`
7. Wire the client's Twilio number to Retell

### Service Management

```bash
# Status
systemctl --user status answering-api.service

# Restart
systemctl --user restart answering-api.service

# Live logs
journalctl --user -u answering-api.service -f
```

### Dashboard (answer.kybernet.tech)

Leads are organized into four columns: **New / Drafted / Sent / Escalated**.

Click any card to open the detail modal:
- Structured call summary (name, address, service, urgency) — always visible
- **Transcript ▸** pill — collapsed by default, click to expand the Agent/Caller conversation
- Draft Reply and Agreed Appointment shown below

Cards with a confirmed appointment show a green **Booked** pill; hovering reveals the agreed time.

When a calendar booking fails (slot taken or unstructured data), the lead is still drafted and set to **Escalated** so the operator has a message to send and knows manual calendar entry is needed.

### Pending

- A2P 10DLC carrier approval — outbound SMS to real customers blocked until approved
- `client_id` multi-tenancy — orchestrator currently hardcoded to `a-couple-two-trees` KB
</content>
</invoke>
