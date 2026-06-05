#!/usr/bin/env python3
"""Repo-aware backlog sync for DrewBeFree GitHub + Leantime projects."""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
import re
import sys
import time
import urllib.error
import urllib.request
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Iterable

OWNER = "DrewBeFree"
CHECKBOX_RE = re.compile(r"^(?P<indent>\s*)- \[ \] (?P<title>.+?)\s*$")
HEADING_RE = re.compile(r"^(?P<marks>#{1,6})\s+(?P<title>.+?)\s*$")
MARKER_RE = re.compile(r"task-sync-id:\s*(task-[0-9a-f]{12})")
SKIP_DIRS = {".git", ".venv", "venv", "node_modules", "dist", "build", "__pycache__"}


@dataclass(frozen=True)
class RepoInfo:
    name: str
    display_name: str
    full_name: str
    path: str
    type: str


@dataclass(frozen=True)
class Task:
    stable_id: str
    title: str
    project: str
    area: str
    status: str
    priority: str
    source_file: str
    source_line: int
    section: str
    description: str
    repo_name: str
    repo_full_name: str
    repo_path: str
    repo_type: str


@dataclass(frozen=True)
class LeantimeAction:
    action: str
    stable_id: str
    title: str
    project: str
    project_id: int | None
    ticket_id: int | None = None
    reason: str = ""


@dataclass(frozen=True)
class IssueAction:
    action: str
    stable_id: str
    title: str
    repo_full_name: str
    issue_number: int | None = None
    reason: str = ""


def clean_markdown(text: str) -> str:
    text = re.sub(r"\*\*(.*?)\*\*", r"\1", text.strip())
    return text.replace("`", "").strip(" -")


def norm(path: str) -> str:
    return path.replace("\\", "/").strip("/")


def github_full_name(url_or_name: str) -> str:
    value = url_or_name.removesuffix(".git").rstrip("/")
    if value.startswith("git@github.com:"):
        return value.split(":", 1)[1]
    if "github.com/" in value:
        return value.split("github.com/", 1)[1]
    if "/" in value:
        return value
    return f"{OWNER}/{value}"


def stable_id(relative_path: str, line_no: int, title: str) -> str:
    digest = hashlib.sha1(f"{relative_path}:{line_no}:{title}".encode("utf-8")).hexdigest()
    return f"task-{digest[:12]}"


def load_env(path: Path) -> dict[str, str]:
    values: dict[str, str] = {}
    for raw in path.read_text(encoding="utf-8").splitlines():
        if raw.strip() and not raw.startswith("#") and "=" in raw:
            key, value = raw.split("=", 1)
            values[key.strip()] = value.strip()
    return values


def load_repos(workspace_root: Path, repos_path: Path, ecosystem_path: Path) -> list[RepoInfo]:
    ecosystem_by_name: dict[str, dict[str, Any]] = {}
    if ecosystem_path.exists():
        ecosystem = json.loads(ecosystem_path.read_text(encoding="utf-8"))
        ecosystem_by_name = {str(r["name"]): r for r in ecosystem.get("repositories", []) if r.get("name")}

    repos: list[RepoInfo] = []
    seen_names: set[str] = set()
    if repos_path.exists():
        data = json.loads(repos_path.read_text(encoding="utf-8"))
        for row in data.get("repositories", []):
            name = str(row["name"])
            eco = ecosystem_by_name.get(name, {})
            path = norm(str(row.get("targetDirectory") or ""))
            seen_names.add(name)
            repos.append(RepoInfo(
                name=name,
                display_name=str(eco.get("displayName") or name.replace("-", " ").title()),
                full_name=github_full_name(str(row.get("github") or name)),
                path=path,
                type=str(row.get("type") or eco.get("category") or "repo"),
            ))

    for name, eco in ecosystem_by_name.items():
        if name in seen_names:
            continue
        local_path = eco.get("localPath")
        path = ""
        if local_path and ":" not in str(local_path):
            try:
                path = norm(str(Path(local_path).resolve().relative_to(workspace_root.resolve())))
            except ValueError:
                path = ""
        if not path:
            category = str(eco.get("category") or "repo")
            folder = {"app": "apps", "site": "sites", "agent": "agents", "infrastructure": ""}.get(category, "")
            path = norm(f"{folder}/{name}" if folder else name)
        repos.append(RepoInfo(
            name=name,
            display_name=str(eco.get("displayName") or name.replace("-", " ").title()),
            full_name=github_full_name(str(eco.get("githubUrl") or name)),
            path=path,
            type=str(eco.get("category") or "repo"),
        ))
    return sorted(repos, key=lambda repo: len(repo.path), reverse=True)


def repo_for_path(relative_path: str, repos: list[RepoInfo]) -> RepoInfo:
    rel = norm(relative_path)
    for repo in repos:
        if rel == repo.path or rel.startswith(repo.path + "/"):
            return repo
    name = rel.split("/", 1)[0] or "workspace"
    return RepoInfo(name, name.replace("-", " ").title(), f"{OWNER}/{name}", name, "repo")


def area_for_repo(repo: RepoInfo) -> str:
    return {
        "app": "apps",
        "site": "sites",
        "agent": "agents",
        "infrastructure": "infra",
    }.get(repo.type, repo.type or "ops")


def status_from_section(section: str) -> str:
    lowered = section.lower()
    if "blocked" in lowered:
        return "Blocked"
    if "in progress" in lowered:
        return "In Progress"
    if "ready" in lowered:
        return "Ready"
    return "Backlog"


def priority_from_text(title: str, description: str) -> str:
    text = f"{title}\n{description}".lower()
    if any(word in text for word in ("offline", "failed", "fault", "backup", "security", "deadline", "blocked")):
        return "High"
    if any(word in text for word in ("dashboard", "sync", "automate", "documents", "github projects", "leantime")):
        return "Medium"
    return "Normal"


def iter_backlogs(workspace_root: Path) -> Iterable[Path]:
    for path in workspace_root.rglob("*.md"):
        if any(part in SKIP_DIRS for part in path.parts):
            continue
        if path.name.upper() == "BACKLOG.MD" or "backlog" in path.name.lower():
            yield path


def parse_backlog(path: Path, workspace_root: Path, repos: list[RepoInfo]) -> list[Task]:
    rel = norm(str(path.relative_to(workspace_root)))
    repo = repo_for_path(rel, repos)
    lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
    sections: list[tuple[int, str]] = []
    tasks: list[Task] = []
    idx = 0
    while idx < len(lines):
        line = lines[idx]
        heading = HEADING_RE.match(line)
        if heading:
            level = len(heading.group("marks"))
            sections = [(old_level, name) for old_level, name in sections if old_level < level]
            sections.append((level, clean_markdown(heading.group("title"))))
            idx += 1
            continue

        match = CHECKBOX_RE.match(line)
        if not match:
            idx += 1
            continue

        line_no = idx + 1
        indent = len(match.group("indent"))
        title = clean_markdown(match.group("title"))
        desc_lines: list[str] = []
        lookahead = idx + 1
        while lookahead < len(lines):
            next_line = lines[lookahead]
            next_checkbox = CHECKBOX_RE.match(next_line)
            if HEADING_RE.match(next_line):
                break
            if next_checkbox and len(next_checkbox.group("indent")) <= indent:
                break
            if next_line.strip():
                desc_lines.append(next_line.strip())
            lookahead += 1
        section = " / ".join(name for _, name in sections)
        description = "\n".join(desc_lines)
        tasks.append(Task(
            stable_id=stable_id(rel, line_no, title),
            title=title,
            project=repo.display_name,
            area=area_for_repo(repo),
            status=status_from_section(section),
            priority=priority_from_text(title, description),
            source_file=rel,
            source_line=line_no,
            section=section,
            description=description,
            repo_name=repo.name,
            repo_full_name=repo.full_name,
            repo_path=repo.path,
            repo_type=repo.type,
        ))
        idx = lookahead
    return tasks


def collect_tasks(workspace_root: Path, repos_path: Path, ecosystem_path: Path) -> list[Task]:
    repos = load_repos(workspace_root, repos_path, ecosystem_path)
    tasks: list[Task] = []
    for path in sorted(iter_backlogs(workspace_root)):
        tasks.extend(parse_backlog(path, workspace_root, repos))
    return tasks


def task_from_row(row: dict[str, Any]) -> Task:
    repo_name = str(row.get("repo_name") or row.get("project") or "repo")
    return Task(
        stable_id=str(row["stable_id"]),
        title=str(row["title"]),
        project=str(row.get("project") or repo_name.replace("-", " ").title()),
        area=str(row.get("area") or "ops"),
        status=str(row.get("status") or "Backlog"),
        priority=str(row.get("priority") or "Normal"),
        source_file=str(row.get("source_file") or ""),
        source_line=int(row.get("source_line") or 0),
        section=str(row.get("section") or ""),
        description=str(row.get("description") or ""),
        repo_name=repo_name,
        repo_full_name=str(row.get("repo_full_name") or f"{OWNER}/{repo_name}"),
        repo_path=str(row.get("repo_path") or ""),
        repo_type=str(row.get("repo_type") or "repo"),
    )


def load_tasks(path: Path) -> list[Task]:
    return [task_from_row(row) for row in json.loads(path.read_text(encoding="utf-8"))]


def marker_from_text(value: Any) -> str | None:
    if value is None:
        return None
    match = MARKER_RE.search(str(value))
    return match.group(1) if match else None


def render_leantime_description(task: Task) -> str:
    parts = [
        task.description.strip(),
        "",
        "---",
        "Synced from Markdown backlog.",
        f"Source: `{task.source_file}:{task.source_line}`",
        f"Repo: `{task.repo_full_name}`",
        f"Section: {task.section or 'n/a'}",
        f"Status: {task.status}",
        f"Priority: {task.priority}",
        f"Project: {task.project}",
        f"task-sync-id: {task.stable_id}",
    ]
    return "\n".join(part for part in parts if part is not None).strip() + "\n"


def render_github_body(task: Task) -> str:
    parts = [
        "Synced from Markdown backlog.",
        "",
        f"Source: `{task.source_file}:{task.source_line}`",
        f"Leantime project: `{task.project}`",
        f"Repo: `{task.repo_full_name}`",
        f"Section: {task.section or 'n/a'}",
        f"Status: {task.status}",
        f"Priority: {task.priority}",
        f"task-sync-id: {task.stable_id}",
    ]
    if task.description.strip():
        parts.extend(["", "## Backlog Notes", "", task.description.strip()])
    return "\n".join(parts).strip() + "\n"


def leantime_status_for(task: Task) -> int:
    status = task.status.lower()
    if "blocked" in status:
        return 1
    if "progress" in status:
        return 4
    return 3


def leantime_values(task: Task, project_id: int, ticket_id: int | None = None) -> dict[str, Any]:
    values: dict[str, Any] = {
        "headline": task.title,
        "description": render_leantime_description(task),
        "projectId": project_id,
        "status": leantime_status_for(task),
        "type": "task",
    }
    if ticket_id is not None:
        values["id"] = ticket_id
    return values


def write_exports(tasks: list[Task], out_dir: Path) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    rows = [asdict(task) for task in tasks]
    (out_dir / "tasks.json").write_text(json.dumps(rows, indent=2) + "\n", encoding="utf-8")
    with (out_dir / "leantime-import.csv").open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()) if rows else ["stable_id", "title"])
        writer.writeheader()
        writer.writerows(rows)
    (out_dir / "github-issues.json").write_text(json.dumps([
        {
            "repo_full_name": task.repo_full_name,
            "title": task.title,
            "body": render_github_body(task),
            "stable_id": task.stable_id,
        }
        for task in tasks
    ], indent=2) + "\n", encoding="utf-8")
    lines = ["# Ecosystem Task Sync Export", "", f"Generated tasks: {len(tasks)}", ""]
    for task in tasks:
        lines.append(f"- [{task.status}] **{task.title}** ({task.project}, {task.priority})")
        lines.append(f"  - Repo: `{task.repo_full_name}`")
        lines.append(f"  - Source: `{task.source_file}:{task.source_line}`")
        lines.append(f"  - Stable ID: `{task.stable_id}`")
    (out_dir / "tasks.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def rpc_post(url: str, headers: dict[str, str], payload: dict[str, Any], retries: int = 5) -> dict[str, Any]:
    data = json.dumps(payload).encode("utf-8")
    request = urllib.request.Request(url, data=data, headers=headers, method="POST")
    for attempt in range(retries + 1):
        try:
            with urllib.request.urlopen(request, timeout=30) as response:
                return json.loads(response.read().decode("utf-8"))
        except urllib.error.HTTPError as exc:
            if exc.code != 429 or attempt >= retries:
                raise
            time.sleep(max(float(exc.headers.get("Retry-After") or 2**attempt), 1.0))
    raise RuntimeError("unreachable retry state")


def leantime_rpc(base_url: str, api_key: str, method: str, params: dict[str, Any]) -> dict[str, Any]:
    return rpc_post(
        base_url.rstrip("/") + "/api/jsonrpc",
        {"Content-Type": "application/json", "x-api-key": api_key},
        {"method": method, "jsonrpc": "2.0", "id": "ecosystem-task-sync", "params": params},
    )


def require_result(result: dict[str, Any], action: str) -> Any:
    if "error" in result:
        raise RuntimeError(f"{action} returned error: {result['error']}")
    return result.get("result")


def fetch_leantime_projects(base_url: str, api_key: str) -> list[dict[str, Any]]:
    result = require_result(leantime_rpc(base_url, api_key, "leantime.rpc.Projects.Projects.getAll", {"showClosedProjects": False}), "get projects")
    if not isinstance(result, list):
        raise RuntimeError(f"expected project list, got {type(result).__name__}")
    return result


def fetch_leantime_tickets(base_url: str, api_key: str) -> list[dict[str, Any]]:
    result = require_result(leantime_rpc(base_url, api_key, "leantime.rpc.tickets.getAll", {"limit": 10000}), "get tickets")
    if not isinstance(result, list):
        raise RuntimeError(f"expected ticket list, got {type(result).__name__}")
    return result


def project_map_from(projects: list[dict[str, Any]], names: Iterable[str]) -> dict[str, dict[str, Any]]:
    by_name = {str(project.get("name")): project for project in projects}
    out: dict[str, dict[str, Any]] = {}
    for name in sorted(set(names)):
        project = by_name.get(name)
        out[name] = {"id": project.get("id"), "name": name} if project else {"id": None, "name": name, "missing": True}
    return out


def project_ids(project_map: dict[str, Any]) -> dict[str, int]:
    out: dict[str, int] = {}
    for name, value in project_map.items():
        if isinstance(value, dict) and value.get("id") is not None:
            out[name] = int(value["id"])
        elif isinstance(value, int):
            out[name] = value
    return out


def index_tickets(tickets: Iterable[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    out: dict[str, dict[str, Any]] = {}
    for ticket in tickets:
        marker = marker_from_text(ticket.get("description")) or marker_from_text(ticket.get("headline"))
        if marker and marker not in out:
            out[marker] = ticket
    return out


def plan_leantime(tasks: list[Task], project_map: dict[str, Any], tickets: list[dict[str, Any]]) -> list[LeantimeAction]:
    ids = project_ids(project_map)
    existing = index_tickets(tickets)
    actions: list[LeantimeAction] = []
    for task in tasks:
        project_id = ids.get(task.project)
        if project_id is None:
            actions.append(LeantimeAction("missing-project", task.stable_id, task.title, task.project, None))
            continue
        ticket = existing.get(task.stable_id)
        if ticket is None:
            actions.append(LeantimeAction("create", task.stable_id, task.title, task.project, project_id))
            continue
        ticket_id = int(ticket["id"])
        current_project_id = int(ticket.get("projectId") or ticket.get("project_id") or project_id)
        if (
            str(ticket.get("headline", "")) != task.title
            or str(ticket.get("description", "")).strip() != render_leantime_description(task).strip()
            or current_project_id != project_id
            or int(ticket.get("status") or -999) != leantime_status_for(task)
        ):
            actions.append(LeantimeAction("update", task.stable_id, task.title, task.project, project_id, ticket_id))
        else:
            actions.append(LeantimeAction("skip", task.stable_id, task.title, task.project, project_id, ticket_id, "already current"))
    return actions


def apply_leantime(base_url: str, api_key: str, action: LeantimeAction, task: Task) -> int | None:
    if action.project_id is None:
        return None
    if action.action == "create":
        result = require_result(leantime_rpc(base_url, api_key, "leantime.rpc.tickets.addTicket", {"values": leantime_values(task, action.project_id)}), f"create {task.stable_id}")
        return int(result.get("id") if isinstance(result, dict) else result)
    if action.action == "update" and action.ticket_id is not None:
        require_result(leantime_rpc(base_url, api_key, "leantime.rpc.tickets.updateTicket", {"values": leantime_values(task, action.project_id, action.ticket_id)}), f"update {task.stable_id}")
        return action.ticket_id
    return action.ticket_id


def github_request(token: str, method: str, path: str, payload: dict[str, Any] | None = None) -> Any:
    request = urllib.request.Request(
        "https://api.github.com" + path,
        data=json.dumps(payload).encode("utf-8") if payload is not None else None,
        headers={
            "Accept": "application/vnd.github+json",
            "Authorization": f"Bearer {token}",
            "X-GitHub-Api-Version": "2022-11-28",
            "Content-Type": "application/json",
            "User-Agent": "drewbefree-ecosystem-task-sync",
        },
        method=method,
    )
    with urllib.request.urlopen(request, timeout=30) as response:
        body = response.read().decode("utf-8")
        return json.loads(body) if body else None


def github_graphql(token: str, query: str, variables: dict[str, Any]) -> dict[str, Any]:
    result = rpc_post(
        "https://api.github.com/graphql",
        {
            "Accept": "application/vnd.github+json",
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
            "User-Agent": "drewbefree-ecosystem-task-sync",
        },
        {"query": query, "variables": variables},
    )
    if result.get("errors"):
        raise RuntimeError(f"GitHub GraphQL errors: {result['errors']}")
    return result["data"]


def fetch_issues(token: str, repo_full_name: str) -> list[dict[str, Any]]:
    issues: list[dict[str, Any]] = []
    page = 1
    while True:
        batch = github_request(token, "GET", f"/repos/{repo_full_name}/issues?state=all&per_page=100&page={page}")
        if not batch:
            break
        issues.extend(issue for issue in batch if "pull_request" not in issue)
        if len(batch) < 100:
            break
        page += 1
    return issues


def index_issues(issues: Iterable[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    out: dict[str, dict[str, Any]] = {}
    for issue in issues:
        marker = marker_from_text(issue.get("body")) or marker_from_text(issue.get("title"))
        if marker and marker not in out:
            out[marker] = issue
    return out


def plan_issues(tasks: list[Task], existing_by_repo: dict[str, list[dict[str, Any]]]) -> list[IssueAction]:
    indexed = {repo: index_issues(issues) for repo, issues in existing_by_repo.items()}
    actions: list[IssueAction] = []
    for task in tasks:
        issue = indexed.get(task.repo_full_name, {}).get(task.stable_id)
        if issue is None:
            actions.append(IssueAction("create", task.stable_id, task.title, task.repo_full_name))
            continue
        number = int(issue["number"])
        if str(issue.get("title", "")) != task.title or str(issue.get("body", "")).strip() != render_github_body(task).strip() or issue.get("state") != "open":
            actions.append(IssueAction("update", task.stable_id, task.title, task.repo_full_name, number))
        else:
            actions.append(IssueAction("skip", task.stable_id, task.title, task.repo_full_name, number, "already current"))
    return actions


def apply_issue(token: str, action: IssueAction, task: Task) -> int | None:
    payload = {"title": task.title, "body": render_github_body(task)}
    if action.action == "create":
        issue = github_request(token, "POST", f"/repos/{task.repo_full_name}/issues", payload)
        return int(issue["number"])
    if action.action == "update" and action.issue_number is not None:
        payload["state"] = "open"
        issue = github_request(token, "PATCH", f"/repos/{task.repo_full_name}/issues/{action.issue_number}", payload)
        return int(issue["number"])
    return action.issue_number


def summary(actions: Iterable[Any]) -> dict[str, int]:
    out: dict[str, int] = {}
    for action in actions:
        out[action.action] = out.get(action.action, 0) + 1
    return out


def write_report(path: str | None, report: dict[str, Any]) -> None:
    if not path:
        return
    target = Path(path).resolve()
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")


def cmd_collect(args: argparse.Namespace) -> int:
    workspace = Path(args.workspace_root).resolve()
    tasks = collect_tasks(workspace, Path(args.repos).resolve(), Path(args.ecosystem).resolve())
    write_exports(tasks, Path(args.out).resolve())
    print(f"collected {len(tasks)} tasks into {Path(args.out).resolve()}")
    return 0


def cmd_sync_projects(args: argparse.Namespace) -> int:
    env = load_env(Path(args.env))
    repos = load_repos(Path(args.workspace_root).resolve(), Path(args.repos).resolve(), Path(args.ecosystem).resolve())
    existing = {str(project.get("name")): project for project in fetch_leantime_projects(env["LEANTIME_BASE_URL"], env["LEANTIME_API_KEY"])}
    missing = [repo for repo in repos if repo.display_name not in existing]
    report = {"mode": "apply" if args.apply else "dry-run", "create": [asdict(repo) for repo in missing], "applied": [], "errors": []}
    print(f"leantime project sync plan: create={len(missing)}, skip={len(repos) - len(missing)}")
    if args.apply:
        for repo in missing:
            try:
                result = require_result(
                    leantime_rpc(env["LEANTIME_BASE_URL"], env["LEANTIME_API_KEY"], "leantime.rpc.projects.addProject", {"values": {"name": repo.display_name, "details": f"Synced ecosystem project for {repo.full_name}.", "clientId": None, "state": 1, "type": "project"}}),
                    f"create project {repo.display_name}",
                )
            except Exception as exc:
                report["errors"].append({"project": repo.display_name, "error": f"{exc.__class__.__name__}: {exc}"})
                break
            report["applied"].append({"project": repo.display_name, "id": result})
            time.sleep(args.write_delay)
    write_report(args.report, report)
    print(f"leantime projects applied: {len(report['applied'])}")
    return 1 if report["errors"] else 0


def cmd_project_map(args: argparse.Namespace) -> int:
    env = load_env(Path(args.env))
    tasks = load_tasks(Path(args.tasks)) if Path(args.tasks).exists() else []
    names = [task.project for task in tasks]
    if args.all_repos:
        repos = load_repos(Path(args.workspace_root).resolve(), Path(args.repos).resolve(), Path(args.ecosystem).resolve())
        names.extend(repo.display_name for repo in repos)
    mapping = project_map_from(fetch_leantime_projects(env["LEANTIME_BASE_URL"], env["LEANTIME_API_KEY"]), names)
    write_report(args.out, mapping)
    print(f"leantime project map exported: {len(mapping)} projects, missing={sum(1 for v in mapping.values() if v.get('id') is None)}")
    return 0


def cmd_sync_leantime(args: argparse.Namespace) -> int:
    env = load_env(Path(args.env))
    tasks = load_tasks(Path(args.tasks))
    project_map = json.loads(Path(args.project_map).read_text(encoding="utf-8"))
    actions = plan_leantime(tasks, project_map, fetch_leantime_tickets(env["LEANTIME_BASE_URL"], env["LEANTIME_API_KEY"]))
    report = {"mode": "apply" if args.apply else "dry-run", "summary": summary(actions), "actions": [asdict(a) for a in actions], "applied": [], "errors": []}
    print("leantime sync plan:", ", ".join(f"{k}={v}" for k, v in sorted(report["summary"].items())) or "no actions")
    if args.apply:
        by_id = {task.stable_id: task for task in tasks}
        for action in actions:
            if action.action not in {"create", "update"}:
                continue
            try:
                ticket_id = apply_leantime(env["LEANTIME_BASE_URL"], env["LEANTIME_API_KEY"], action, by_id[action.stable_id])
            except Exception as exc:
                report["errors"].append({"action": asdict(action), "error": f"{exc.__class__.__name__}: {exc}"})
                break
            report["applied"].append({"action": action.action, "stable_id": action.stable_id, "ticket_id": ticket_id})
            time.sleep(args.write_delay)
    else:
        print("dry-run only; pass --apply to create/update Leantime tasks")
    write_report(args.report, report)
    print(f"leantime sync applied: {len(report['applied'])}")
    return 1 if report["errors"] else 0


def cmd_sync_issues(args: argparse.Namespace) -> int:
    env = load_env(Path(args.env))
    tasks = load_tasks(Path(args.tasks))
    repos = sorted(set(task.repo_full_name for task in tasks))
    existing = {repo: fetch_issues(env["GITHUB_TOKEN"], repo) for repo in repos}
    actions = plan_issues(tasks, existing)
    report = {"mode": "apply" if args.apply else "dry-run", "summary": summary(actions), "actions": [asdict(a) for a in actions], "applied": [], "errors": []}
    print("github issue sync plan:", ", ".join(f"{k}={v}" for k, v in sorted(report["summary"].items())) or "no actions")
    if args.apply:
        by_id = {task.stable_id: task for task in tasks}
        for action in actions:
            if action.action not in {"create", "update"}:
                continue
            try:
                issue_number = apply_issue(env["GITHUB_TOKEN"], action, by_id[action.stable_id])
            except Exception as exc:
                report["errors"].append({"action": asdict(action), "error": f"{exc.__class__.__name__}: {exc}"})
                break
            report["applied"].append({"action": action.action, "stable_id": action.stable_id, "repo_full_name": action.repo_full_name, "issue_number": issue_number})
            time.sleep(args.write_delay)
    else:
        print("dry-run only; pass --apply to create/update GitHub issues")
    write_report(args.report, report)
    print(f"github issue sync applied: {len(report['applied'])}")
    return 1 if report["errors"] else 0


def cmd_github_projects(args: argparse.Namespace) -> int:
    env = load_env(Path(args.env))
    owner = env.get("GITHUB_OWNER") or args.owner
    print(json.dumps(fetch_github_projects(env["GITHUB_TOKEN"], owner), indent=2))
    return 0


def fetch_github_owner(token: str, owner: str) -> dict[str, Any]:
    query = """
    query($login: String!) {
      user(login: $login) { id login }
    }
    """
    return github_graphql(token, query, {"login": owner})["user"]


def fetch_github_projects(token: str, owner: str) -> list[dict[str, Any]]:
    query = """
    query($login: String!) {
      user(login: $login) {
        projectsV2(first: 100) { nodes { id number title url closed } }
      }
    }
    """
    data = github_graphql(token, query, {"login": owner})
    return data.get("user", {}).get("projectsV2", {}).get("nodes", [])


def create_github_project(token: str, owner_id: str, title: str) -> dict[str, Any]:
    query = """
    mutation($ownerId: ID!, $title: String!) {
      createProjectV2(input: {ownerId: $ownerId, title: $title}) {
        projectV2 { id number title url closed }
      }
    }
    """
    data = github_graphql(token, query, {"ownerId": owner_id, "title": title})
    return data["createProjectV2"]["projectV2"]


def fetch_project_item_issue_ids(token: str, owner: str, number: int) -> set[str]:
    query = """
    query($login: String!, $number: Int!, $cursor: String) {
      user(login: $login) {
        projectV2(number: $number) {
          items(first: 100, after: $cursor) {
            pageInfo { hasNextPage endCursor }
            nodes {
              content {
                ... on Issue { id }
              }
            }
          }
        }
      }
    }
    """
    issue_ids: set[str] = set()
    cursor: str | None = None
    while True:
        data = github_graphql(token, query, {"login": owner, "number": number, "cursor": cursor})
        items = data["user"]["projectV2"]["items"]
        for node in items["nodes"]:
            content = node.get("content") or {}
            if content.get("id"):
                issue_ids.add(content["id"])
        if not items["pageInfo"]["hasNextPage"]:
            return issue_ids
        cursor = items["pageInfo"]["endCursor"]


def add_issue_to_project(token: str, project_id: str, issue_node_id: str) -> str:
    query = """
    mutation($projectId: ID!, $contentId: ID!) {
      addProjectV2ItemById(input: {projectId: $projectId, contentId: $contentId}) {
        item { id }
      }
    }
    """
    data = github_graphql(token, query, {"projectId": project_id, "contentId": issue_node_id})
    return data["addProjectV2ItemById"]["item"]["id"]


def cmd_sync_github_projects(args: argparse.Namespace) -> int:
    env = load_env(Path(args.env))
    token = env["GITHUB_TOKEN"]
    owner = env.get("GITHUB_OWNER") or args.owner
    repos = load_repos(Path(args.workspace_root).resolve(), Path(args.repos).resolve(), Path(args.ecosystem).resolve())
    existing = {project["title"]: project for project in fetch_github_projects(token, owner) if not project.get("closed")}
    missing = [repo for repo in repos if repo.display_name not in existing]
    report = {"mode": "apply" if args.apply else "dry-run", "create": [asdict(repo) for repo in missing], "applied": [], "errors": []}
    print(f"github project sync plan: create={len(missing)}, skip={len(repos) - len(missing)}")
    if args.apply:
        owner_id = fetch_github_owner(token, owner)["id"]
        for repo in missing:
            try:
                project = create_github_project(token, owner_id, repo.display_name)
            except Exception as exc:
                report["errors"].append({"project": repo.display_name, "error": f"{exc.__class__.__name__}: {exc}"})
                break
            report["applied"].append(project)
            time.sleep(args.write_delay)
    write_report(args.report, report)
    print(f"github projects applied: {len(report['applied'])}")
    return 1 if report["errors"] else 0


def cmd_sync_github_project_items(args: argparse.Namespace) -> int:
    env = load_env(Path(args.env))
    token = env["GITHUB_TOKEN"]
    owner = env.get("GITHUB_OWNER") or args.owner
    tasks = load_tasks(Path(args.tasks))
    projects = {project["title"]: project for project in fetch_github_projects(token, owner) if not project.get("closed")}
    repos = sorted(set(task.repo_full_name for task in tasks))
    issues_by_marker: dict[str, dict[str, Any]] = {}
    for repo in repos:
        issues_by_marker.update(index_issues(fetch_issues(token, repo)))

    actions: list[dict[str, Any]] = []
    item_cache: dict[int, set[str]] = {}
    for task in tasks:
        project = projects.get(task.project)
        issue = issues_by_marker.get(task.stable_id)
        if not project:
            actions.append({"action": "missing-project", "stable_id": task.stable_id, "project": task.project, "repo_full_name": task.repo_full_name})
            continue
        if not issue:
            actions.append({"action": "missing-issue", "stable_id": task.stable_id, "project": task.project, "repo_full_name": task.repo_full_name})
            continue
        project_number = int(project["number"])
        if project_number not in item_cache:
            item_cache[project_number] = fetch_project_item_issue_ids(token, owner, project_number)
        if issue["node_id"] in item_cache[project_number]:
            actions.append({"action": "skip", "stable_id": task.stable_id, "project": task.project, "repo_full_name": task.repo_full_name, "issue_number": issue["number"]})
        else:
            actions.append({"action": "add", "stable_id": task.stable_id, "project": task.project, "project_id": project["id"], "repo_full_name": task.repo_full_name, "issue_number": issue["number"], "issue_node_id": issue["node_id"]})

    report = {"mode": "apply" if args.apply else "dry-run", "summary": summary(type("A", (), {"action": a["action"]})() for a in actions), "actions": actions, "applied": [], "errors": []}
    print("github project item sync plan:", ", ".join(f"{k}={v}" for k, v in sorted(report["summary"].items())) or "no actions")
    if args.apply:
        for action in actions:
            if action["action"] != "add":
                continue
            try:
                item_id = add_issue_to_project(token, action["project_id"], action["issue_node_id"])
            except Exception as exc:
                report["errors"].append({"action": action, "error": f"{exc.__class__.__name__}: {exc}"})
                break
            report["applied"].append({**action, "item_id": item_id})
            time.sleep(args.write_delay)
    else:
        print("dry-run only; pass --apply to add GitHub issues to Projects")
    write_report(args.report, report)
    print(f"github project items applied: {len(report['applied'])}")
    return 1 if report["errors"] else 0


def parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description=__doc__)
    sub = p.add_subparsers(dest="command", required=True)
    default_workspace = str(Path.cwd().parent)
    default_repos = "repos.json"
    default_ecosystem = "ecosystem.json"

    c = sub.add_parser("collect")
    c.add_argument("--workspace-root", default=default_workspace)
    c.add_argument("--repos", default=default_repos)
    c.add_argument("--ecosystem", default=default_ecosystem)
    c.add_argument("--out", default="data/task-sync")
    c.set_defaults(func=cmd_collect)

    sp = sub.add_parser("sync-leantime-projects")
    sp.add_argument("--env", default=os.path.expanduser("~/services/task-sync/.env"))
    sp.add_argument("--workspace-root", default=default_workspace)
    sp.add_argument("--repos", default=default_repos)
    sp.add_argument("--ecosystem", default=default_ecosystem)
    sp.add_argument("--report", default="data/task-sync/leantime-project-sync-report.json")
    sp.add_argument("--apply", action="store_true")
    sp.add_argument("--write-delay", type=float, default=0.75)
    sp.set_defaults(func=cmd_sync_projects)

    pm = sub.add_parser("leantime-project-map")
    pm.add_argument("--env", default=os.path.expanduser("~/services/task-sync/.env"))
    pm.add_argument("--tasks", default="data/task-sync/tasks.json")
    pm.add_argument("--workspace-root", default=default_workspace)
    pm.add_argument("--repos", default=default_repos)
    pm.add_argument("--ecosystem", default=default_ecosystem)
    pm.add_argument("--all-repos", action="store_true")
    pm.add_argument("--out", default="data/task-sync/leantime-project-map.json")
    pm.set_defaults(func=cmd_project_map)

    sl = sub.add_parser("sync-leantime")
    sl.add_argument("--env", default=os.path.expanduser("~/services/task-sync/.env"))
    sl.add_argument("--tasks", default="data/task-sync/tasks.json")
    sl.add_argument("--project-map", default="data/task-sync/leantime-project-map.json")
    sl.add_argument("--report", default="data/task-sync/leantime-sync-report.json")
    sl.add_argument("--apply", action="store_true")
    sl.add_argument("--write-delay", type=float, default=0.75)
    sl.set_defaults(func=cmd_sync_leantime)

    gi = sub.add_parser("sync-github-issues")
    gi.add_argument("--env", default=os.path.expanduser("~/services/task-sync/github.env"))
    gi.add_argument("--tasks", default="data/task-sync/tasks.json")
    gi.add_argument("--report", default="data/task-sync/github-issue-sync-report.json")
    gi.add_argument("--apply", action="store_true")
    gi.add_argument("--write-delay", type=float, default=0.25)
    gi.set_defaults(func=cmd_sync_issues)

    gp = sub.add_parser("github-projects")
    gp.add_argument("--env", default=os.path.expanduser("~/services/task-sync/github.env"))
    gp.add_argument("--owner", default=OWNER)
    gp.set_defaults(func=cmd_github_projects)

    sgp = sub.add_parser("sync-github-projects")
    sgp.add_argument("--env", default=os.path.expanduser("~/services/task-sync/github.env"))
    sgp.add_argument("--owner", default=OWNER)
    sgp.add_argument("--workspace-root", default=default_workspace)
    sgp.add_argument("--repos", default=default_repos)
    sgp.add_argument("--ecosystem", default=default_ecosystem)
    sgp.add_argument("--report", default="data/task-sync/github-project-sync-report.json")
    sgp.add_argument("--apply", action="store_true")
    sgp.add_argument("--write-delay", type=float, default=0.5)
    sgp.set_defaults(func=cmd_sync_github_projects)

    sgpi = sub.add_parser("sync-github-project-items")
    sgpi.add_argument("--env", default=os.path.expanduser("~/services/task-sync/github.env"))
    sgpi.add_argument("--owner", default=OWNER)
    sgpi.add_argument("--tasks", default="data/task-sync/tasks.json")
    sgpi.add_argument("--report", default="data/task-sync/github-project-item-sync-report.json")
    sgpi.add_argument("--apply", action="store_true")
    sgpi.add_argument("--write-delay", type=float, default=0.25)
    sgpi.set_defaults(func=cmd_sync_github_project_items)
    return p


def main(argv: list[str] | None = None) -> int:
    args = parser().parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
