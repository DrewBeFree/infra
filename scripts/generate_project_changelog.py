#!/usr/bin/env python3
"""Generate the private ecosystem project changelog page.

The page is a static HTML digest of recent git commits and SESSION_LOG headings for
repositories listed in ecosystem.json. It is safe for the internal portal; it does
not read .env files or repository content beyond git metadata and SESSION_LOG.md.
"""
from __future__ import annotations

import argparse
import html
import json
import subprocess
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
ECOSYSTEM_PATH = ROOT / "ecosystem.json"
DEFAULT_OUTPUT = ROOT / "internal-portal" / "changelog.html"
FIELD_SEP = "\x1f"


@dataclass(frozen=True)
class Project:
    name: str
    kind: str
    visibility: str
    summary: str
    path: Path | None
    github_url: str | None
    live_urls: list[str]


def run_git(repo: Path, args: list[str]) -> str:
    result = subprocess.run(
        ["git", "-C", str(repo), *args],
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        timeout=20,
        check=False,
    )
    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip() or f"git {' '.join(args)} failed")
    return result.stdout.strip()


def local_path(value: str | None) -> Path | None:
    if not value:
        return None
    # Windows paths in the registry are useful documentation but not readable on Atlas.
    if ":\\" in value or value.startswith("C:\\"):
        return None
    return Path(value).expanduser()


def load_projects() -> list[Project]:
    registry = json.loads(ECOSYSTEM_PATH.read_text(encoding="utf-8"))
    projects: list[Project] = []

    for section, kind in (("repositories", "repo"), ("dashboards", "dashboard"), ("services", "service")):
        for item in registry.get(section, []):
            name = item.get("displayName") or item.get("name") or item.get("id")
            if not name:
                continue
            path = local_path(item.get("atlasLocalPath") or item.get("localPath"))
            projects.append(
                Project(
                    name=str(name),
                    kind=kind,
                    visibility=str(item.get("visibility", "unknown")),
                    summary=str(item.get("summary", "")),
                    path=path,
                    github_url=item.get("githubUrl"),
                    live_urls=[str(url) for url in item.get("liveUrls", [])],
                )
            )

    return sorted(projects, key=lambda p: (p.kind, p.name.lower()))


def git_commits(repo: Path, limit: int) -> list[dict[str, str]]:
    raw = run_git(repo, ["log", f"-{limit}", "--date=iso-strict", f"--pretty=format:%H{FIELD_SEP}%cI{FIELD_SEP}%s{FIELD_SEP}%an"])
    commits: list[dict[str, str]] = []
    for line in raw.splitlines():
        parts = line.split(FIELD_SEP)
        if len(parts) != 4:
            continue
        sha, committed_at, subject, author = parts
        commits.append({"sha": sha[:8], "committed_at": committed_at, "subject": subject, "author": author})
    return commits


def git_status(repo: Path) -> str:
    status = run_git(repo, ["status", "--short"])
    return "dirty" if status else "clean"


def session_log_entries(repo: Path, limit: int = 5) -> list[str]:
    path = repo / "SESSION_LOG.md"
    if not path.exists():
        return []
    entries: list[str] = []
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        if line.startswith("## "):
            entries.append(line.removeprefix("## ").strip())
        if len(entries) >= limit:
            break
    return entries


def collect(limit: int) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for project in load_projects():
        repo = project.path
        has_repo = bool(repo and (repo / ".git").exists())
        row: dict[str, Any] = {
            "name": project.name,
            "kind": project.kind,
            "visibility": project.visibility,
            "summary": project.summary,
            "path": str(repo) if repo else "",
            "github_url": project.github_url or "",
            "live_urls": project.live_urls,
            "has_repo": has_repo,
            "status": "not local" if not repo else "not a git repo",
            "commits": [],
            "session_logs": [],
            "error": "",
        }
        if has_repo and repo:
            try:
                row["status"] = git_status(repo)
                row["commits"] = git_commits(repo, limit)
                row["session_logs"] = session_log_entries(repo)
            except Exception as exc:  # keep the dashboard useful even if one repo is broken
                row["status"] = "error"
                row["error"] = str(exc)
        rows.append(row)
    return rows


def fmt_date(value: str) -> str:
    if not value:
        return "unknown"
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00")).strftime("%Y-%m-%d %H:%M")
    except ValueError:
        return value


def render(rows: list[dict[str, Any]], output: Path, limit: int) -> None:
    generated_at = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    local_repos = sum(1 for row in rows if row["has_repo"])
    dirty = sum(1 for row in rows if row["status"] == "dirty")
    latest = [dict(commit, project=row["name"]) for row in rows for commit in row["commits"][:1]]
    latest.sort(key=lambda c: c.get("committed_at", ""), reverse=True)

    def link(url: str, label: str) -> str:
        if not url:
            return ""
        return f'<a href="{html.escape(url, quote=True)}" target="_blank" rel="noreferrer">{html.escape(label)}</a>'

    project_rows = []
    project_templates = []
    for idx, row in enumerate(rows):
        commits_html = "".join(
            f"""
            <li>
              <time>{html.escape(fmt_date(commit['committed_at']))}</time>
              <span><code>{html.escape(commit['sha'])}</code> {html.escape(commit['subject'])}<small>{html.escape(commit['author'])}</small></span>
            </li>
            """
            for commit in row["commits"]
        ) or '<li><span class="muted">No local git commits available.</span></li>'
        logs_html = "".join(f"<span>{html.escape(entry)}</span>" for entry in row["session_logs"])
        latest_commit = row["commits"][0] if row["commits"] else None
        latest_date = fmt_date(latest_commit["committed_at"]) if latest_commit else "—"
        row_date = latest_date.split()[0] if latest_commit else "—"
        latest_subject = latest_commit["subject"] if latest_commit else "No local git history"
        live = " ".join(link(url, "open") for url in row["live_urls"][:2])
        detail_id = f"project-detail-{idx}"
        project_rows.append(
            f"""
            <button class="project-row" type="button" data-detail-id="{detail_id}" data-status="{html.escape(row['status'])}">
              <span class="name">{html.escape(row['name'])}</span>
              <time>{html.escape(row_date)}</time>
              <span class="status {html.escape(row['status'].replace(' ', '-'))}">{html.escape(row['status'])}</span>
            </button>
            """
        )
        project_templates.append(
            f"""
            <template id="{detail_id}">
              <p class="eyebrow">{html.escape(row['kind'])} · {html.escape(row['visibility'])}</p>
              <h2>{html.escape(row['name'])}</h2>
              <p class="summary-text">{html.escape(row['summary'])}</p>
              <p class="latest-subject"><strong>Latest:</strong> {html.escape(latest_date)} · {html.escape(latest_subject)}</p>
              <p class="links">{link(row['github_url'], 'GitHub')} {live}</p>
              <p class="path">{html.escape(row['path'])}</p>
              {f'<p class="error">{html.escape(row["error"])}</p>' if row['error'] else ''}
              <div class="detail-grid">
                <section>
                  <h3>Recent commits</h3>
                  <ul>{commits_html}</ul>
                </section>
                <section>
                  <h3>Session log dates</h3>
                  <div class="session-pills">{logs_html or '<span>None found</span>'}</div>
                </section>
              </div>
            </template>
            """
        )

    latest_items = "".join(
        f"<li><time>{html.escape(fmt_date(commit['committed_at']))}</time><span>{html.escape(commit['project'])}: {html.escape(commit['subject'])}</span></li>"
        for commit in latest[:8]
    )

    doc = f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>DrewBeFree Project Changelog</title>
<meta name="theme-color" content="#071015">
<style>
:root {{ color-scheme: dark; --bg:#050a0e; --panel:#0a151d; --panel2:#0d1b25; --border:#143143; --text:#d7f4fa; --muted:#7fb3c5; --dim:#426d7c; --accent:#00d4ff; --ok:#00ff88; --warn:#f59e0b; --bad:#ff6b35; }}
* {{ box-sizing:border-box; }}
html {{ font-size:14px; }}
body {{ margin:0; background:radial-gradient(circle at top left,#102635,#050a0e 46%); color:var(--text); font-family:ui-sans-serif,system-ui,-apple-system,Segoe UI,sans-serif; }}
a {{ color:var(--accent); text-decoration:none; }}
a:hover {{ text-decoration:underline; }}
.wrap {{ max-width:1600px; margin:0 auto; padding:10px 12px 28px; }}
header {{ display:grid; grid-template-columns:minmax(0,1fr) auto; gap:12px; align-items:end; border-bottom:1px solid var(--border); padding-bottom:6px; margin-bottom:6px; }}
header p {{ margin:.08rem 0; }}
h1 {{ margin:0; font-size:clamp(1.35rem,2.6vw,2.25rem); letter-spacing:-0.05em; }}
.eyebrow {{ margin:0 0 2px; color:var(--accent); text-transform:uppercase; letter-spacing:.22em; font-size:.6rem; }}
.muted,.path {{ color:var(--muted); }}
.path {{ overflow-wrap:anywhere; font-size:.72rem; margin:.4rem 0; }}
.stats {{ display:grid; grid-template-columns:repeat(4,minmax(110px,1fr)); gap:6px; margin:8px 0; }}
.stat,.latest,.project-row {{ background:rgba(10,21,29,.88); border:1px solid var(--border); border-radius:7px; box-shadow:0 10px 30px rgba(0,0,0,.22); }}
.stat {{ padding:5px 9px; }}
.stat strong {{ display:block; font-size:1.08rem; line-height:1; }}
.latest {{ margin:8px 0 10px; }}
.latest summary {{ cursor:pointer; padding:5px 9px; color:var(--muted); text-transform:uppercase; letter-spacing:.16em; font-size:.64rem; }}
.latest ul,.drawer ul {{ list-style:none; padding:0; margin:0; }}
.latest li,.drawer li {{ display:grid; grid-template-columns:145px minmax(0,1fr); gap:10px; padding:7px 0; border-top:1px solid rgba(127,179,197,.14); }}
time {{ color:var(--muted); font-variant-numeric:tabular-nums; white-space:nowrap; }}
.project-list {{ display:grid; grid-template-columns:repeat(auto-fit,minmax(285px,1fr)); gap:3px; align-items:start; }}
.project-row {{ display:grid; grid-template-columns:minmax(0,1fr) 82px 58px; gap:6px; align-items:center; min-height:24px; padding:2px 7px; cursor:pointer; color:inherit; font:inherit; text-align:left; width:100%; }}
.project-row:hover,.project-row.is-active {{ border-color:rgba(0,212,255,.5); background:rgba(13,27,37,.96); }}
.name {{ font-weight:700; color:#fff; overflow:hidden; text-overflow:ellipsis; white-space:nowrap; }}
.meta,.subject {{ display:none; }}
.status {{ justify-self:end; white-space:nowrap; border:1px solid var(--border); border-radius:999px; padding:1px 5px; color:var(--muted); text-transform:uppercase; font-size:.52rem; }}
.status.clean {{ color:var(--ok); border-color:rgba(0,255,136,.34); }}
.status.dirty {{ color:var(--warn); border-color:rgba(245,158,11,.4); }}
.status.error {{ color:var(--bad); border-color:rgba(255,107,53,.42); }}
.drawer-backdrop {{ position:fixed; inset:0; background:rgba(0,0,0,.48); opacity:0; pointer-events:none; transition:opacity .18s ease; z-index:20; }}
.drawer {{ position:fixed; top:0; right:0; width:min(560px,92vw); height:100vh; overflow:auto; background:rgba(10,21,29,.98); border-left:1px solid rgba(0,212,255,.35); box-shadow:-20px 0 60px rgba(0,0,0,.5); transform:translateX(102%); transition:transform .2s ease; z-index:21; padding:18px; }}
.drawer.is-open,.drawer-backdrop.is-open {{ transform:translateX(0); opacity:1; pointer-events:auto; }}
.drawer-close {{ float:right; border:1px solid var(--border); background:#071015; color:var(--text); border-radius:999px; padding:5px 10px; cursor:pointer; }}
.summary-text,.latest-subject {{ margin:.2rem 0 .5rem; color:#bdd5df; }}
.links {{ display:flex; flex-wrap:wrap; gap:10px; margin:.35rem 0; }}
.detail-grid {{ display:grid; grid-template-columns:minmax(0,1.5fr) minmax(240px,.8fr); gap:18px; }}
h3 {{ margin:8px 0 6px; color:var(--muted); font-size:.68rem; letter-spacing:.18em; text-transform:uppercase; }}
code {{ color:#fff; background:#071015; border:1px solid rgba(127,179,197,.14); border-radius:4px; padding:1px 5px; }}
small {{ display:block; color:var(--dim); margin-top:2px; }}
.session-pills {{ display:flex; flex-wrap:wrap; gap:6px; }}
.session-pills span {{ border:1px solid rgba(0,212,255,.28); color:var(--muted); border-radius:999px; padding:3px 8px; font-size:.72rem; }}
.error {{ color:var(--bad); }}
@media (max-width:920px) {{
  header,.latest li,.drawer li,.detail-grid {{ grid-template-columns:1fr; }}
  .stats {{ grid-template-columns:repeat(2,1fr); }}
  .project-list {{ grid-template-columns:1fr; }}
  .project-row {{ grid-template-columns:minmax(0,1fr) 82px 58px; }}
}}
</style>
</head>
<body>
<div class="wrap">
<header>
  <div>
    <p class="eyebrow">Private ecosystem history</p>
    <h1>Project Changelog</h1>
    <p class="muted">Compact rows from local git metadata and SESSION_LOG headings. Updated {html.escape(generated_at)}.</p>
  </div>
  <p><a href="launcher.html">Launcher</a> · <a href="index.html">Registry</a> · <a href="tree.html">Tree</a></p>
</header>
<section class="stats">
  <div class="stat"><span class="muted">Projects</span><strong>{len(rows)}</strong></div>
  <div class="stat"><span class="muted">Local git repos</span><strong>{local_repos}</strong></div>
  <div class="stat"><span class="muted">Dirty</span><strong>{dirty}</strong></div>
  <div class="stat"><span class="muted">Commits/project</span><strong>{limit}</strong></div>
</section>
<details class="latest">
  <summary>Latest changes across local repos</summary>
  <ul>{latest_items}</ul>
</details>
<section class="project-list" aria-label="Project changelog rows">
{''.join(project_rows)}
</section>
{''.join(project_templates)}
<div id="drawerBackdrop" class="drawer-backdrop" hidden></div>
<aside id="projectDrawer" class="drawer" aria-hidden="true" aria-label="Project changelog details">
  <button id="drawerClose" class="drawer-close" type="button">Close</button>
  <div id="drawerContent"></div>
</aside>
<script>
const drawer = document.getElementById('projectDrawer');
const drawerContent = document.getElementById('drawerContent');
const drawerBackdrop = document.getElementById('drawerBackdrop');
const drawerClose = document.getElementById('drawerClose');
function closeDrawer() {{
  drawer.classList.remove('is-open');
  drawerBackdrop.classList.remove('is-open');
  drawer.setAttribute('aria-hidden', 'true');
  drawerBackdrop.hidden = true;
  document.querySelectorAll('.project-row.is-active').forEach((row) => row.classList.remove('is-active'));
}}
function openDrawer(button) {{
  const template = document.getElementById(button.dataset.detailId);
  if (!template) return;
  drawerContent.replaceChildren(template.content.cloneNode(true));
  document.querySelectorAll('.project-row.is-active').forEach((row) => row.classList.remove('is-active'));
  button.classList.add('is-active');
  drawerBackdrop.hidden = false;
  drawer.classList.add('is-open');
  drawerBackdrop.classList.add('is-open');
  drawer.setAttribute('aria-hidden', 'false');
}}
document.querySelectorAll('.project-row').forEach((button) => button.addEventListener('click', () => openDrawer(button)));
drawerClose.addEventListener('click', closeDrawer);
drawerBackdrop.addEventListener('click', closeDrawer);
document.addEventListener('keydown', (event) => {{ if (event.key === 'Escape') closeDrawer(); }});
</script>
</div>
</body>
</html>
"""
    doc = "\n".join(line.rstrip() for line in doc.splitlines()) + "\n"
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(doc, encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate internal project changelog HTML from local ecosystem repos.")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--limit", type=int, default=8, help="recent commits per local repo")
    args = parser.parse_args()

    rows = collect(args.limit)
    render(rows, args.output, args.limit)
    print(f"Wrote {args.output}")
    print(f"Projects: {len(rows)}; local git repos: {sum(1 for row in rows if row['has_repo'])}")


if __name__ == "__main__":
    main()
