# Workspace Layout

This page documents the canonical directory structure on the development machine (Alienware) after the 2026-06-20 consolidation pass.

## Top-Level Structure

```
/home/drew/
├── GitHub/                           ← All version-controlled projects (source of truth)
│   ├── personal/                     ← Personal projects and experiments
│   │   ├── llm-debate-union/
│   │   ├── daily-planner/
│   │   └── ...
│   ├── clients/                      ← Client work
│   ├── experiments/                  ← Throwaway tests and spikes
│   ├── apps/                         ← Existing apps
│   ├── homelab/                      ← Homelab documentation
│   ├── infra/                        ← Infrastructure tooling and configs
│   │   ├── monitoring/
│   │   ├── benchmarks/
│   │   └── internal-portal/
│   └── sites/                        ← Public sites
├── hermes/                           ← Hermes Agent (model-agnostic skills & workflows)
├── ecc/                              ← Everything Claude Code harness (Claude Code only)
├── claude-config/                    ← Centralized Claude Code settings (shared across machines)
├── ops/                              ← Atlas operational control plane (separate repo: atlas-ops)
├── services/                         ← Local services (some with their own git repos)
├── actions-runner/                   ← GitHub Actions runner
├── hermes-mobile-proxy/              ← Hermes mobile proxy service
├── atlas-migration-backups/          ← Archive for old copies during migrations
├── Desktop/
├── Documents/
└── ...
```

## Key Principles

- **GitHub/** is the single source of truth for all projects and version-controlled work.
- **hermes/** stays at the top level (works with Codex, Qwen, Grok, Ollama, etc.).
- **ecc/** stays at the top level (Claude Code harness only — read-only reference).
- **claude-config/** stays at the top level (shared across Mac, Alienware, WSL, Atlas).
- **ops/** stays at the top level (separate `atlas-ops` repo for operational runbooks and codex handoffs).
- Old scattered copies were consolidated or backed up under `atlas-migration-backups/`.

## Recent Changes (2026-06-20)

- Merged duplicate `infra/` folders (kept `GitHub/infra/`)
- Deleted duplicate `internal-portal/`
- Deleted old experiment `openclaw-agents/`
- Deleted stray file `-n`
- Moved `llm-debate-union/` → `GitHub/personal/`
- Moved `monitoring/` and `benchmarks/` → `GitHub/infra/`
- Created `atlas-migration-backups/` as the designated archive folder for future migrations

## Related Pages

- [Infrastructure Overview](index.md)
- [Machines](machines.md)
- [Tools](tools.md)
- [Services](services.md)