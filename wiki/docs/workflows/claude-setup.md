# Claude Code Setup

Configuration, skills, and conventions for working with Claude Code.

## Subagent Model Selection

When spawning subagents, pick the model based on the task:

| Model | Use for |
| --- | --- |
| **haiku** | Mechanical tasks: file search, grep, read, list, simple lookups |
| **sonnet** | Judgment tasks: architecture, code review, debugging, synthesis, exploration |

Default to haiku for Explore-type agents unless the task requires reasoning.

## Memory System

Claude Code has a persistent file-based memory at `~/.claude/projects/<project>/memory/`. Memory types:

- **user** — role, preferences, knowledge
- **feedback** — corrections and confirmed approaches
- **project** — ongoing work, goals, deadlines
- **reference** — pointers to external resources

Each memory is a `.md` file with frontmatter. An index file (`MEMORY.md`) provides quick lookup.

## Session Logs

At the start of every conversation, read both the memory session log and `SESSION_LOG.md` to restore context. At the end, write an entry to both.

## Skills (Superpowers)

Available skills for structured workflows:

- **brainstorming** — idea → design → spec through collaborative dialogue
- **writing-plans** — spec → detailed implementation plan with TDD steps
- **subagent-driven-development** — execute plans with fresh subagent per task + two-stage review
- **executing-plans** — execute plans in a parallel session
- **test-driven-development** — red/green/refactor cycle
- **debugging** — structured root-cause analysis
- **finishing-a-development-branch** — merge prep + cleanup

## Global Instructions (CLAUDE.md)

The global `~/.claude/CLAUDE.md` defines:

- Session log format and locations
- Git commit style (no Co-Authored-By)
- Subagent model selection rules
- Repository organization
- Branching workflow
- Version management rules
- Logoff checklist

Project-level `CLAUDE.md` files can override or extend these.

## Branching Workflow

All development work goes on a branch — never commit directly to `main`.

- `dev` for general work
- `feat/description` for features
- `fix/description` for bugs

Merge to main and push when ready.
