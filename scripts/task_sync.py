#!/usr/bin/env python3
"""Collect Markdown backlog tasks and sync them to Leantime safely."""
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

CHECKBOX_RE = re.compile(r"^(?P<indent>\s*)- \[ \] (?P<title>.+?)\s*$")
HEADING_RE = re.compile(r"^(?P<marks>#{1,6})\s+(?P<title>.+?)\s*$")
MARKER_RE = re.compile(r"task-sync-id:\s*(task-[0-9a-f]{12})")
MARKER_LABEL = "task-sync-id"
SKIP_DIRS = {".git", ".venv", "venv", "node_modules", "dist", "build", "__pycache__"}


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


@dataclass(frozen=True)
class SyncAction:
    action: str
    stable_id: str
    title: str
    project: str
    project_id: int | None
    ticket_id: int | None = None
    reason: str = ""


def clean_markdown(text: str) -> str:
    text = text.strip()
    text = re.sub(r"\*\*(.*?)\*\*", r"\1", text)
    text = text.replace("`", "")
    return text.strip(" -")


def stable_id(relative_path: str, line_no: int, title: str) -> str:
    digest = hashlib.sha1(f"{relative_path}:{line_no}:{title}".encode("utf-8")).hexdigest()
    return f"task-{digest[:12]}"


def classify(relative_path: str, title: str, section: str) -> tuple[str, str]:
    haystack = f"{relative_path} {title} {section}".lower()
    if any(term in haystack for term in ("atlas", "poweredge", "homelab", "idrac", "perc", "smb", "documents", "backup", "docker")):
        return "Atlas / Infra", "infra"
    if any(term in haystack for term in ("app", "command center", "uhaul", "planner", "poker", "golf")):
        return "Apps Portfolio", "apps"
    if any(term in haystack for term in ("site", "business", "kybernet", "dwebb")):
        return "Sites / Business", "sites"
    if any(term in haystack for term in ("agent", "claude", "codex", "hermes", "recap")):
        return "Recap Agents", "agents"
    return "Ecosystem Ops", "ops"


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
    if any(term in text for term in ("offline", "failed", "fault", "backup", "security", "deadline", "blocked")):
        return "High"
    if any(term in text for term in ("dashboard", "sync", "automate", "documents", "github projects", "leantime")):
        return "Medium"
    return "Normal"


def iter_markdown_files(workspace_root: Path) -> Iterable[Path]:
    for path in workspace_root.rglob("*.md"):
        if any(part in SKIP_DIRS for part in path.parts):
            continue
        if path.name.upper() == "BACKLOG.MD" or "backlog" in path.name.lower():
            yield path


def parse_markdown(path: Path, workspace_root: Path) -> list[Task]:
    lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
    rel = path.relative_to(workspace_root).as_posix()
    tasks: list[Task] = []
    sections: list[tuple[int, str]] = []

    idx = 0
    while idx < len(lines):
        line = lines[idx]
        heading = HEADING_RE.match(line)
        if heading:
            level = len(heading.group("marks"))
            sections = [(existing_level, name) for existing_level, name in sections if existing_level < level]
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
        project, area = classify(rel, title, section)
        tasks.append(Task(
            stable_id=stable_id(rel, line_no, title),
            title=title,
            project=project,
            area=area,
            status=status_from_section(section),
            priority=priority_from_text(title, description),
            source_file=rel,
            source_line=line_no,
            section=section,
            description=description,
        ))
        idx = lookahead
    return tasks


def collect(workspace_root: Path) -> list[Task]:
    tasks: list[Task] = []
    for path in sorted(iter_markdown_files(workspace_root)):
        tasks.extend(parse_markdown(path, workspace_root))
    return tasks


def task_from_row(row: dict[str, Any]) -> Task:
    return Task(
        stable_id=str(row["stable_id"]),
        title=str(row["title"]),
        project=str(row["project"]),
        area=str(row.get("area", "ops")),
        status=str(row.get("status", "Backlog")),
        priority=str(row.get("priority", "Normal")),
        source_file=str(row.get("source_file", "")),
        source_line=int(row.get("source_line", 0)),
        section=str(row.get("section", "")),
        description=str(row.get("description", "")),
    )


def load_tasks(path: Path) -> list[Task]:
    return [task_from_row(row) for row in json.loads(path.read_text(encoding="utf-8"))]


def render_leantime_description(task: Task) -> str:
    parts = [
        task.description.strip(),
        "",
        "---",
        "Synced from Markdown backlog.",
        f"Source: `{task.source_file}:{task.source_line}`",
        f"Section: {task.section or 'n/a'}",
        f"Status: {task.status}",
        f"Priority: {task.priority}",
        f"Project: {task.project}",
        f"{MARKER_LABEL}: {task.stable_id}",
    ]
    return "\n".join(part for part in parts if part is not None).strip() + "\n"


def leantime_values(task: Task, project_id: int, ticket_id: int | None = None) -> dict[str, Any]:
    values: dict[str, Any] = {
        "headline": task.title,
        "description": render_leantime_description(task),
        "projectId": project_id,
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

    issue_rows = []
    for task in tasks:
        body = [
            f"Source: `{task.source_file}:{task.source_line}`",
            f"Project: {task.project}",
            f"Status: {task.status}",
            f"Priority: {task.priority}",
            f"Stable ID: `{task.stable_id}`",
        ]
        if task.description:
            body.extend(["", task.description])
        issue_rows.append({
            "title": task.title,
            "body": "\n".join(body),
            "labels": [f"area/{task.area}", f"priority/{task.priority.lower()}", "sync/backlog"],
            "stable_id": task.stable_id,
        })
    (out_dir / "github-issues.json").write_text(json.dumps(issue_rows, indent=2) + "\n", encoding="utf-8")

    md_lines = ["# Task Sync Export", "", f"Generated tasks: {len(tasks)}", ""]
    for task in tasks:
        md_lines.append(f"- [{task.status}] **{task.title}** ({task.project}, {task.priority})")
        md_lines.append(f"  - Source: `{task.source_file}:{task.source_line}`")
        md_lines.append(f"  - Stable ID: `{task.stable_id}`")
    (out_dir / "tasks.md").write_text("\n".join(md_lines) + "\n", encoding="utf-8")


def load_env(path: Path) -> dict[str, str]:
    values: dict[str, str] = {}
    for raw in path.read_text(encoding="utf-8").splitlines():
        raw = raw.strip()
        if not raw or raw.startswith("#") or "=" not in raw:
            continue
        key, value = raw.split("=", 1)
        values[key] = value
    return values


def leantime_rpc(base_url: str, api_key: str, method: str, params: dict[str, Any], retries: int = 5) -> dict[str, Any]:
    payload = json.dumps({"method": method, "jsonrpc": "2.0", "id": "task-sync", "params": params}).encode("utf-8")
    request = urllib.request.Request(
        base_url.rstrip("/") + "/api/jsonrpc",
        data=payload,
        headers={"Content-Type": "application/json", "x-api-key": api_key},
        method="POST",
    )
    for attempt in range(retries + 1):
        try:
            with urllib.request.urlopen(request, timeout=30) as response:
                return json.loads(response.read().decode("utf-8"))
        except urllib.error.HTTPError as exc:
            if exc.code != 429 or attempt >= retries:
                raise
            retry_after = exc.headers.get("Retry-After")
            try:
                delay = float(retry_after) if retry_after else 2 ** attempt
            except ValueError:
                delay = 2 ** attempt
            time.sleep(max(delay, 1.0))
    raise RuntimeError("unreachable retry state")


def require_rpc_result(result: dict[str, Any], action: str) -> Any:
    if "error" in result:
        raise RuntimeError(f"{action} returned error: {result['error']}")
    return result.get("result")


def marker_from_ticket(ticket: dict[str, Any]) -> str | None:
    for field in ("description", "tags", "headline"):
        value = ticket.get(field)
        if value is None:
            continue
        match = MARKER_RE.search(str(value))
        if match:
            return match.group(1)
    return None


def index_tickets_by_marker(tickets: Iterable[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    indexed: dict[str, dict[str, Any]] = {}
    for ticket in tickets:
        marker = marker_from_ticket(ticket)
        if marker and marker not in indexed:
            indexed[marker] = ticket
    return indexed


def project_map_ids(project_map: dict[str, Any]) -> dict[str, int]:
    ids: dict[str, int] = {}
    for name, value in project_map.items():
        if isinstance(value, dict) and value.get("id") is not None:
            ids[name] = int(value["id"])
        elif isinstance(value, int):
            ids[name] = value
    return ids


def plan_leantime_sync(tasks: list[Task], project_map: dict[str, Any], existing_tickets: list[dict[str, Any]]) -> list[SyncAction]:
    projects = project_map_ids(project_map)
    existing = index_tickets_by_marker(existing_tickets)
    actions: list[SyncAction] = []

    for task in tasks:
        project_id = projects.get(task.project)
        if project_id is None:
            actions.append(SyncAction("missing-project", task.stable_id, task.title, task.project, None, reason="no Leantime project mapping"))
            continue

        ticket = existing.get(task.stable_id)
        desired = leantime_values(task, project_id, int(ticket["id"]) if ticket and ticket.get("id") is not None else None)
        if ticket is None:
            actions.append(SyncAction("create", task.stable_id, task.title, task.project, project_id))
            continue

        ticket_id = int(ticket["id"])
        current_headline = str(ticket.get("headline", ""))
        current_description = str(ticket.get("description", ""))
        current_project_id = int(ticket.get("projectId") or ticket.get("project_id") or project_id)
        if (
            current_headline != desired["headline"]
            or current_description.strip() != desired["description"].strip()
            or current_project_id != project_id
        ):
            actions.append(SyncAction("update", task.stable_id, task.title, task.project, project_id, ticket_id=ticket_id))
        else:
            actions.append(SyncAction("skip", task.stable_id, task.title, task.project, project_id, ticket_id=ticket_id, reason="already current"))
    return actions


def summarize_actions(actions: list[SyncAction]) -> dict[str, int]:
    summary: dict[str, int] = {}
    for action in actions:
        summary[action.action] = summary.get(action.action, 0) + 1
    return summary


def fetch_leantime_tickets(base_url: str, api_key: str) -> list[dict[str, Any]]:
    result = require_rpc_result(leantime_rpc(base_url, api_key, "leantime.rpc.tickets.getAll", {"limit": 10000}), "get tickets")
    if not isinstance(result, list):
        raise RuntimeError(f"expected ticket list, got {type(result).__name__}")
    return result


def apply_leantime_action(base_url: str, api_key: str, action: SyncAction, task: Task) -> int | None:
    if action.project_id is None:
        return None
    if action.action == "create":
        result = require_rpc_result(
            leantime_rpc(base_url, api_key, "leantime.rpc.tickets.addTicket", {"values": leantime_values(task, action.project_id)}),
            f"create {task.stable_id}",
        )
        if isinstance(result, dict):
            return int(result.get("id") or result.get("ticketId") or 0) or None
        return int(result) if result else None
    if action.action == "update" and action.ticket_id is not None:
        require_rpc_result(
            leantime_rpc(base_url, api_key, "leantime.rpc.tickets.updateTicket", {"values": leantime_values(task, action.project_id, action.ticket_id)}),
            f"update {task.stable_id}",
        )
        return action.ticket_id
    return action.ticket_id


def cmd_collect(args: argparse.Namespace) -> int:
    workspace_root = Path(args.workspace_root).resolve()
    out_dir = Path(args.out).resolve()
    tasks = collect(workspace_root)
    write_exports(tasks, out_dir)
    print(f"collected {len(tasks)} tasks into {out_dir}")
    return 0


def cmd_projects(args: argparse.Namespace) -> int:
    env = load_env(Path(args.env))
    base_url = env.get("LEANTIME_BASE_URL")
    api_key = env.get("LEANTIME_API_KEY")
    if not base_url or not api_key:
        print("missing LEANTIME_BASE_URL or LEANTIME_API_KEY", file=sys.stderr)
        return 2
    try:
        result = leantime_rpc(base_url, api_key, "leantime.rpc.Projects.Projects.getAll", {"showClosedProjects": False})
    except Exception as exc:
        print(f"leantime project export failed: {exc.__class__.__name__}: {exc}", file=sys.stderr)
        return 1
    if "error" in result:
        print(f"leantime project export returned error: {result['error']}", file=sys.stderr)
        return 1
    out = Path(args.out).resolve()
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(result.get("result") or [], indent=2) + "\n", encoding="utf-8")
    count = len(result.get("result") or []) if isinstance(result.get("result"), list) else "ok"
    print(f"leantime projects exported: {count} -> {out}")
    return 0


def cmd_probe(args: argparse.Namespace) -> int:
    env = load_env(Path(args.env))
    base_url = env.get("LEANTIME_BASE_URL")
    api_key = env.get("LEANTIME_API_KEY")
    if not base_url or not api_key:
        print("missing LEANTIME_BASE_URL or LEANTIME_API_KEY", file=sys.stderr)
        return 2
    try:
        result = leantime_rpc(base_url, api_key, "leantime.rpc.tickets.getAll", {"limit": 5})
    except urllib.error.HTTPError as exc:
        print(f"leantime probe failed: HTTP {exc.code}", file=sys.stderr)
        return 1
    except Exception as exc:
        print(f"leantime probe failed: {exc.__class__.__name__}: {exc}", file=sys.stderr)
        return 1
    if "error" in result:
        print(f"leantime probe returned error: {result['error']}", file=sys.stderr)
        return 1
    count = len(result.get("result") or []) if isinstance(result.get("result"), list) else "ok"
    print(f"leantime probe ok: tickets={count}")
    return 0


def cmd_sync_leantime(args: argparse.Namespace) -> int:
    env = load_env(Path(args.env))
    base_url = env.get("LEANTIME_BASE_URL")
    api_key = env.get("LEANTIME_API_KEY")
    if not base_url or not api_key:
        print("missing LEANTIME_BASE_URL or LEANTIME_API_KEY", file=sys.stderr)
        return 2

    tasks = load_tasks(Path(args.tasks))
    project_map = json.loads(Path(args.project_map).read_text(encoding="utf-8"))
    existing = fetch_leantime_tickets(base_url, api_key)
    actions = plan_leantime_sync(tasks, project_map, existing)
    summary = summarize_actions(actions)

    report = {
        "mode": "apply" if args.apply else "dry-run",
        "summary": summary,
        "actions": [asdict(action) for action in actions],
        "applied": [],
        "errors": [],
    }
    if args.report:
        report_path = Path(args.report).resolve()
        report_path.parent.mkdir(parents=True, exist_ok=True)
        report_path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")

    print("leantime sync plan:", ", ".join(f"{key}={value}" for key, value in sorted(summary.items())) or "no actions")
    if not args.apply:
        print("dry-run only; pass --apply to create/update Leantime tasks")
        return 0

    by_id = {task.stable_id: task for task in tasks}
    applied = 0
    for action in actions:
        if action.action not in {"create", "update"}:
            continue
        try:
            ticket_id = apply_leantime_action(base_url, api_key, action, by_id[action.stable_id])
        except Exception as exc:
            report["errors"].append({"action": asdict(action), "error": f"{exc.__class__.__name__}: {exc}"})
            break
        report["applied"].append({"action": action.action, "stable_id": action.stable_id, "ticket_id": ticket_id})
        applied += 1
        if args.write_delay > 0:
            time.sleep(args.write_delay)
    if args.report:
        report_path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(f"leantime sync applied: {applied} create/update actions")
    if report["errors"]:
        print(f"leantime sync stopped after error: {report["errors"][-1]["error"]}", file=sys.stderr)
        return 1
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)

    collect_parser = sub.add_parser("collect", help="Collect markdown backlog tasks into sync exports")
    collect_parser.add_argument("--workspace-root", default=str(Path.cwd().parent), help="Root to scan for BACKLOG.md files")
    collect_parser.add_argument("--out", default=str(Path.cwd() / "data" / "task-sync"), help="Output directory")
    collect_parser.set_defaults(func=cmd_collect)

    projects_parser = sub.add_parser("leantime-projects", help="Export readable Leantime projects for ID mapping")
    projects_parser.add_argument("--env", default=os.path.expanduser("~/services/task-sync/.env"), help="Env file with LEANTIME_BASE_URL and LEANTIME_API_KEY")
    projects_parser.add_argument("--out", default="data/task-sync/leantime-projects.json", help="Output JSON path")
    projects_parser.set_defaults(func=cmd_projects)

    probe_parser = sub.add_parser("leantime-probe", help="Check Leantime API connectivity without printing secrets")
    probe_parser.add_argument("--env", default=os.path.expanduser("~/services/task-sync/.env"), help="Env file with LEANTIME_BASE_URL and LEANTIME_API_KEY")
    probe_parser.set_defaults(func=cmd_probe)

    sync_parser = sub.add_parser("sync-leantime", help="Create/update Leantime tasks from generated task exports")
    sync_parser.add_argument("--env", default=os.path.expanduser("~/services/task-sync/.env"), help="Env file with LEANTIME_BASE_URL and LEANTIME_API_KEY")
    sync_parser.add_argument("--tasks", default="data/task-sync/tasks.json", help="Generated tasks.json path")
    sync_parser.add_argument("--project-map", default="data/task-sync/leantime-project-map.json", help="Leantime project map JSON path")
    sync_parser.add_argument("--report", default="data/task-sync/leantime-sync-report.json", help="Sync report output path")
    sync_parser.add_argument("--apply", action="store_true", help="Actually create/update Leantime tasks; default is dry-run")
    sync_parser.add_argument("--write-delay", type=float, default=0.75, help="Seconds to sleep between Leantime write calls")
    sync_parser.set_defaults(func=cmd_sync_leantime)
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
