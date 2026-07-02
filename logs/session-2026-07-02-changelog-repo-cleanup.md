# Internal Portal Changelog Repo Cleanup — 2026-07-02

Host/worktree: `/home/drew/GitHub/infra`
Branch: `main`
Remote: `origin/main` (`git@github.com:DrewBeFree/infra.git`)
Checkpoint before this handoff: `95a89f4 chore: refresh deployed changelog`

## Outcome

Fixed the internal ecosystem changelog source so Atlas can resolve Drew's Windows-style repo registry paths to local Atlas checkouts, added the missing `john-share` project to the registry/sync contract, regenerated and deployed the changelog, and cleaned normal project repos back to a clean/up-to-date state.

The deployed changelog now includes `John Share` and shows only the live Hermes Agent service checkout as dirty.

## Why this was done

The portal was showing stale/inaccurate dirty counts because the static changelog had not been regenerated after repo cleanup and the generator skipped many registry entries whose `localPath` values were Windows paths. `john-share` existed on disk but was absent from `ecosystem.json`, so it could not appear in the portal.

## Files intentionally changed

- `ecosystem.json`
  - Added `john-share` as `John Share` with sensitive visibility.
- `internal-portal/sync-links.json`
  - Added a matching `john-share` placeholder so registry/sync counts stay aligned.
- `internal-portal/portal.test.mjs`
  - Added `john-share` to the required repo contract.
- `scripts/generate_project_changelog.py`
  - Maps `C:\Users\drewb\Documents\GitHub\...` paths to `/home/drew/GitHub/...` on Atlas.
  - Ignores the generated `internal-portal/changelog.html` file when checking the infra repo's dirty status and recent commits, preventing self-generated dirty rows and self-referential changelog refresh loops.
- `internal-portal/changelog.html`
  - Regenerated and deployed static changelog output.

## Commands run

```bash
cd /home/drew/GitHub/infra
git status --short --branch
git log --oneline -5
python3 scripts/generate_project_changelog.py --output internal-portal/changelog.html --limit 25
./internal-portal/deploy.sh
```

Focused ad-hoc verifier was created under `/tmp` with a `hermes-verify-` prefix, executed, and removed. It checked JSON parsing, Python compilation/import, Windows-path mapping, John registry/sync/test/changelog inclusion, generated/deployed dirty rows, project repo cleanliness, and infra git alignment.

Observed result:

```text
INFO project repos scanned: 35
PASS ecosystem.json parses
PASS sync-links.json parses
PASS generate_project_changelog.py compiles
PASS Windows GitHub path maps to Atlas checkout
PASS ecosystem includes john-share
PASS john-share display name is John Share
PASS john-share visibility is sensitive
PASS john-share resolves to existing git repo
PASS sync-links includes john-share
PASS portal test required repo list includes john-share
PASS generator exits successfully
PASS generated changelog includes John Share
PASS generated dirty rows limited to Hermes Agent service
PASS deployed changelog exists
PASS deployed changelog includes John Share
PASS deployed dirty rows limited to Hermes Agent service
PASS project repos clean and up-to-date
PASS infra working tree clean
PASS infra branch aligned with origin/main
SUMMARY ad-hoc verification passed
```

## Cleanup / repo hygiene performed

Committed and pushed low-risk task-sync workflow additions in:

```text
/home/drew/GitHub/agents/answering-agent
/home/drew/GitHub/agents/bob
/home/drew/GitHub/agents/recap-agents
```

Review-staged, rather than committed, larger or local/runtime changes:

```text
/home/drew/repo-cleanup-review-20260702-012818/patches/lead-gen-agent-review.patch
/home/drew/repo-cleanup-review-20260702-012818/patches/personal-llm-debate-union-review.patch
/home/drew/repo-cleanup-review-20260702-012818/patches/trading-scanner-heartbeat-runtime.patch
/home/drew/repo-cleanup-review-20260702-012818/files/personal__llm-debate-union/
```

## Safety notes

- No `.env` contents, credentials, venvs, caches, or private runtime files were committed.
- `personal/llm-debate-union` untracked local/runtime files were moved to the review folder instead of being deleted.
- `lead-gen-agent` and `personal/llm-debate-union` tracked changes were stashed/review-staged rather than swept into unrelated commits.
- `trading-scanner` had only a tracked runtime heartbeat diff; the diff was backed up before restoring the file.
- The live Hermes Agent install at `/home/drew/.hermes/hermes-agent` remains dirty by design. It is outside the normal project repo scan and should not be reset/stashed without explicit approval.

## Current known exception

The changelog still reports this dirty row:

```text
Hermes Agent
```

Current live service checkout status at last inspection:

```text
/home/drew/.hermes/hermes-agent
 M agent/conversation_loop.py
 M agent/prompt_builder.py
 M agent/system_prompt.py
 M package-lock.json
?? daily-planner/
?? tests/test_qwen_text_json_tool_call.py
```

## Next recommended step

Decide how to handle `/home/drew/.hermes/hermes-agent`:

1. Leave it dirty because it is active Hermes runtime/dev work.
2. Stash it after confirming no live session depends on the edits.
3. Commit it in the Hermes Agent repo if those changes are intentional.
4. Exclude live Hermes service checkouts from changelog dirty counts if the portal should only track project repos.
