# Task Sync Bridge

This keeps local Markdown backlogs, Leantime projects/tasks, GitHub Issues, and GitHub Projects from drifting apart.

## Current Source Of Truth

Markdown backlog files remain the human-editable source for now. The ecosystem collector scans `BACKLOG.md`-style files under `C:\Users\drewb\Documents\GitHub`, maps each file to its owning repo through `repos.json` and `ecosystem.json`, extracts open checklist tasks, assigns stable IDs, and writes sync-ready exports.

The correct model is repo/project owned:

- Each repo/app/site/agent has its own Leantime project.
- Backlog tasks create/update GitHub Issues in the repo they belong to.
- Those issues are added to the matching GitHub Project for that repo/project.
- Leantime tasks are created/updated in the matching Leantime project.

Generated files live in `data/task-sync/`:

- `tasks.json` - canonical normalized task list
- `tasks.md` - quick human review
- `github-issues.json` - issue creation/update payloads
- `leantime-import.csv` - import/reconciliation table for Leantime
- `leantime-projects.json` - read-only export of visible Leantime projects
- `leantime-project-map.json` - generated project-name-to-Leantime-ID map

## Commands

From the infra repo:

```powershell
python scripts/ecosystem_task_sync.py collect --workspace-root C:\Users\drewb\Documents\GitHub --repos repos.json --ecosystem ecosystem.json --out data\task-sync
python -m unittest scripts.tests.test_task_sync
python -m unittest scripts.tests.test_ecosystem_task_sync
```

From Atlas, after the Sync Bot key is saved in `/home/drew/services/task-sync/.env`:

```bash
cd ~/services/task-sync/ecosystem
python3 ecosystem_task_sync.py sync-leantime-projects --env ~/services/task-sync/.env --workspace-root . --repos repos.json --ecosystem ecosystem.json
python3 ecosystem_task_sync.py leantime-project-map --env ~/services/task-sync/.env --tasks data/task-sync/tasks.json --workspace-root . --repos repos.json --ecosystem ecosystem.json --all-repos
python3 ecosystem_task_sync.py sync-leantime --env ~/services/task-sync/.env --tasks data/task-sync/tasks.json --project-map data/task-sync/leantime-project-map.json
python3 ecosystem_task_sync.py sync-github-issues --env ~/services/task-sync/github.env --tasks data/task-sync/tasks.json
python3 ecosystem_task_sync.py sync-github-projects --env ~/services/task-sync/github.env --workspace-root . --repos repos.json --ecosystem ecosystem.json
python3 ecosystem_task_sync.py sync-github-project-items --env ~/services/task-sync/github.env --tasks data/task-sync/tasks.json
```

All sync commands are dry-run by default; pass `--apply` only when the plan looks right. The sync matches existing items using the `task-sync-id: task-...` marker and never deletes Leantime tasks, GitHub Issues, or GitHub Project items.

## Next Live Sync Step

Keep live writes conservative:

1. Review `data/task-sync/tasks.md`.
2. Create or update GitHub Issues from `github-issues.json`.
3. Map the generated `project` values to actual Leantime project IDs.
4. Add a write mode that upserts only tasks carrying a matching `stable_id` marker.

Do not attempt bidirectional overwrite sync until GitHub Project fields and Leantime project/status IDs are mapped. The first safe production mode should be append/update-by-marker, not delete/recreate.

## 2026-06-05 Setup Status

- Local ecosystem scan works and currently finds 30 open tasks across 9 repos.
- Leantime has 25 ecosystem projects; project postcheck reports `create=0`.
- Leantime task sync migrated the original broad-bucket proof-of-life tasks into repo-owned projects; final postcheck reports `skip=30`.
- GitHub issue sync created 30 issues in their owning repos; final postcheck reports `skip=30`.
- GitHub Project sync created missing per-project boards; final postcheck reports `create=0`.
- GitHub Project item sync added the synced issues to their matching project boards; final postcheck reports `skip=30`.
- The Codex GitHub app is still blocked for direct issue creation, but the Atlas `github.env` PAT works for the ecosystem sync.

## Safe Live Sync Rules

- Dry-run first: `sync-leantime` without `--apply`.
- Apply only after reviewing the summary and `leantime-sync-report.json`.
- The sync may create or update tasks, but it does not delete tasks.
- Leantime rate limiting is handled with retry/backoff and `--write-delay`; keep the default delay unless there is a reason to change it.
- If a run is interrupted, rerun dry-run first. Existing marker-managed tasks should become `skip` or `update`, not duplicate creates.
