# Infra

Workspace infrastructure, standards, ecosystem navigation, and repository automation for Drew's GitHub projects.

## What lives here

| Area | Purpose |
| --- | --- |
| `STRUCTURE.md` | Workspace directory, naming, and file conventions. |
| `repos.json` | Repository manifest used by clone/catalog tooling. |
| `ecosystem.json` | Private ecosystem registry for apps, services, dashboards, and links. |
| `scripts/` | Automation for cloning, syncing task state, and generating changelogs. |
| `wiki/` | Local MkDocs-style project catalog and supporting generation scripts. |
| `internal-portal/` | Generated internal ecosystem views, including changelog output. |

## Common maintenance commands

Generate the private project changelog:

```bash
python3 scripts/generate_project_changelog.py
```

Generate the wiki project catalog:

```bash
python3 wiki/scripts/gen_catalog.py
```

Clone or refresh repositories from the manifest:

```bash
python3 scripts/clone_manifest.py
```

## Operating notes

- Keep `dev` as the working integration branch; do not make overnight automation changes on `main`.
- Treat `ecosystem.json` and `repos.json` as navigation source-of-truth files.
- Generated files should be regenerated from scripts rather than edited by hand.
