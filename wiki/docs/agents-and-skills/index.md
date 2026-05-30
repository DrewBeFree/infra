# Agents & Skills

Two different kinds of automation live in this homelab — **agents** and **skills** — and they're easy to conflate. Here's the distinction:

---

## Agents vs. Skills

| | Agents | Skills |
|---|---|---|
| **What they are** | Runnable software processes | Instruction sets for Claude Code |
| **Where they live** | On infrastructure (Atlas, Alienware) | In `~/.claude/skills/` |
| **Who runs them** | The server or a scheduler | Claude Code during a dev session |
| **What triggers them** | Events, webhooks, schedules, or direct invocation | You typing `/skill-name` in Claude Code |
| **What they produce** | Real outputs: messages, drafts, summaries, data | Guided dev workflow actions |
| **Scope** | Persistent, always-on (or event-driven) | In-session only — no side effects after session ends |

**One sentence each:**

- **Agent** — a process that does autonomous work on real data (send a message, draft a response, process a file).
- **Skill** — a procedure Claude follows when you invoke it (run a checklist, generate a log entry, deploy a thing).

The core difference: agents run on servers and produce artifacts; skills run inside Claude's reasoning to guide what you do together.

---

## Quick Reference

### Agents

| Agent | What it does | Lives on |
|---|---|---|
| [Bob](agents.md#bob) | Slack bot backed by local LLM | Atlas (always-on) |
| [Answering Agent](agents.md#answering-agent) | Voicemail → AI draft SMS → human approval | Atlas (always-on) |
| [Recap Agents](agents.md#recap-agents) | Meeting recap pipeline → Kybernet Dashboard | Atlas / scheduled |
| [Interactive Setup](agents.md#interactive-setup) | Architecture reference docs | n/a (docs only) |

### Skills

| Skill | When to invoke |
|---|---|
| [`/log-session`](skills.md#log-session) | End of any session — generate + push session log |
| [`/logoff`](skills.md#logoff) | End of a dev session — full wrap-up checklist |
| [`/update-atlas`](skills.md#update-atlas) | After pushing homelab dashboard changes — deploy to atlas |
