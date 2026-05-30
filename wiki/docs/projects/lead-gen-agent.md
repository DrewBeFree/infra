# Lead Gen Agent

Private review-gated lead inbox for Facebook and monday.com lead signals. The Phase 1 MVP accepts manually captured opportunities, scores them with transparent rules, creates editable response drafts, and tracks review outcomes without scraping or auto-posting.

| Field | Value |
| --- | --- |
| Type | agent |
| Status | phase-1-mvp |
| Repo | https://github.com/DrewBeFree/lead-gen-agent |
| Local path | `agents/lead-gen-agent` |
| Runtime | FastAPI + SQLite |
| Default branch | `main` |

## Current Workflow

1. Drew manually pastes a source URL, author label, and captured text into the inbox.
2. The app deduplicates the lead by canonical URL or text hash.
3. The scorer produces a transparent score breakdown.
4. The draft worker creates a starter reply that is useful first and promotional only when relevant.
5. Drew edits, copies, approves, rejects, archives, or marks follow-up manually.
6. Every state change is recorded in the SQLite audit trail.

## Guardrails

- No unattended Facebook scraping.
- No unattended public posting.
- No CAPTCHA bypass, account rotation, or bot-evasion behavior.
- No unnecessary personal data collection.
- Human review remains the publishing gate.

## Key Files

| File | Role |
| --- | --- |
| `src/lead_gen_agent/web.py` | FastAPI routes and form endpoints |
| `src/lead_gen_agent/database.py` | SQLite schema, dedupe, lead state, and audit events |
| `src/lead_gen_agent/scoring.py` | Deterministic starter scoring |
| `src/lead_gen_agent/drafts.py` | Starter draft generation |
| `src/lead_gen_agent/evaluation.py` | Fixture calibration runner |
| `NO_AUTO_POSTING_POLICY.md` | Explicit automation guardrail |
| `docs/facebook-monday-lead-gen-agent-v2.md` | Canonical architecture plan |

## Verification

```powershell
$env:PYTHONPATH="src"
python -m unittest discover -s tests -v
python -m lead_gen_agent.evaluation
```

## Next

- Add monday.com webhook simulation.
- Prepare Atlas Docker Compose deployment.
- Replace starter scoring/drafting with a review-gated LLM worker after fixtures are representative.
