#!/usr/bin/env python3
"""Generate the wiki Projects catalog from the local filesystem, repos.json, and the Command Center."""
from __future__ import annotations

import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

from bs4 import BeautifulSoup

SCAN_DIRS = {"apps": "app", "sites": "site", "agents": "agent"}


def scan_repos(base_dir: Path) -> list[dict]:
    repos = []
    for sub, type_ in SCAN_DIRS.items():
        d = base_dir / sub
        if not d.is_dir():
            continue
        for child in sorted(d.iterdir()):
            if (child / ".git").exists():
                repos.append({"name": child.name, "type": type_, "path": f"{sub}/{child.name}"})
    return repos


def load_manifest(repos_json_path: Path) -> dict:
    if not repos_json_path.is_file():
        return {}
    data = json.loads(repos_json_path.read_text(encoding="utf-8"))
    return {r["name"]: r for r in data.get("repositories", [])}


def load_card_map(card_map_path: Path) -> tuple[dict, dict, dict]:
    if not card_map_path.is_file():
        return {}, {}, {}
    data = json.loads(card_map_path.read_text(encoding="utf-8"))
    overrides = data.pop("_type_overrides", {})
    icon_slugs = data.pop("_icon_slugs", {})
    return data, overrides, icon_slugs


def parse_command_center(index_html_path: Path) -> dict:
    if not index_html_path.is_file():
        return {}
    soup = BeautifulSoup(index_html_path.read_text(encoding="utf-8"), "html.parser")
    cards = {}
    for card in soup.select("a.card"):
        id_el = card.select_one(".card-id")
        if not id_el:
            continue
        card_id = id_el.get_text(strip=True).split("//")[0].strip()
        meta_el = card.select_one(".card-meta")
        meta = meta_el.get_text(strip=True) if meta_el else ""
        version = date = status = None
        if meta.upper() == "LIVE":
            status = "live"
        elif meta.startswith("v") and "·" in meta:
            ver_part, _, date_part = meta.partition("·")
            version = ver_part.strip().lstrip("v")
            date = date_part.strip()
            status = "active"
        name_el = card.select_one(".card-name")
        url_el = card.select_one(".card-url")
        desc_el = card.select_one(".card-desc")
        cards[card_id] = {
            "display_name": name_el.get_text(strip=True) if name_el else None,
            "url": url_el.get_text(strip=True) if url_el else None,
            "description": desc_el.get_text(strip=True) if desc_el else None,
            "version": version,
            "date": date,
            "status": status,
        }
    return cards


def read_description(repo_path: Path) -> str:
    readme = repo_path / "README.md"
    if not readme.is_file():
        return ""
    for line in readme.read_text(encoding="utf-8").splitlines():
        s = line.strip()
        if s and not s.startswith("#") and not s.startswith("!["):
            return s
    return ""


def read_manual(repo_path: Path) -> str:
    manual = repo_path / "MANUAL.md"
    if not manual.is_file():
        return ""
    return manual.read_text(encoding="utf-8").strip()


def github_web_url(clone_url: str | None) -> str | None:
    if not clone_url:
        return None
    return clone_url[:-4] if clone_url.endswith(".git") else clone_url


def enrich(repos: list[dict], manifest: dict, cards: dict, card_map: dict, type_overrides: dict, icon_slugs: dict, base_dir: Path) -> list[dict]:
    enriched = []
    for repo in repos:
        name = repo["name"]
        m = manifest.get(name, {})
        card_id = card_map.get(name)
        card = cards.get(card_id, {}) if card_id else {}
        description = card.get("description") or read_description(base_dir / repo["path"]) or "No description."
        live_url = card.get("url")
        icon_slug = icon_slugs.get(name, name)
        icon_url = f"https://{live_url}/icons/{icon_slug}-192.png" if live_url else None
        enriched.append({
            **repo,
            "type": type_overrides.get(name, repo["type"]),
            "github": m.get("github"),
            "in_manifest": name in manifest,
            "display_name": card.get("display_name") or name,
            "version": card.get("version"),
            "date": card.get("date"),
            "status": card.get("status"),
            "url": live_url,
            "description": description,
            "manual": read_manual(base_dir / repo["path"]),
            "icon_url": icon_url,
        })
    return enriched


def detect_drift(repos: list[dict], manifest: dict, base_dir: Path) -> list[str]:
    warnings = []
    scanned = {r["name"] for r in repos}
    for name in sorted(scanned):
        if name not in manifest:
            warnings.append(f"on disk but missing from repos.json: {name}")
    for name, m in sorted(manifest.items()):
        target = m.get("targetDirectory", "")
        if target.split("/")[0] in SCAN_DIRS and not (base_dir / target).is_dir():
            warnings.append(f"in repos.json but not on disk: {name} ({target})")
    return warnings


def render_index(projects: list[dict]) -> str:
    lines = [
        "# Projects",
        "",
        "_Auto-generated by `scripts/gen_catalog.py` — do not edit by hand._",
        "",
    ]
    type_order = ["app", "site", "agent"]
    type_labels = {"app": "Apps", "site": "Sites", "agent": "Agents"}
    by_type: dict[str, list] = {t: [] for t in type_order}
    for p in projects:
        bucket = p["type"] if p["type"] in by_type else "agent"
        by_type[bucket].append(p)
    for t in type_order:
        group = sorted(by_type[t], key=lambda x: x["name"])
        if not group:
            continue
        lines += [f"## {type_labels[t]}", "", "| Project | Version | Status | Repo |", "| --- | --- | --- | --- |"]
        for p in group:
            ver = f"v{p['version']}" if p["version"] else "—"
            status = p["status"] or "—"
            web = github_web_url(p["github"])
            repo_cell = f"[GitHub]({web})" if web else "—"
            name_cell = f"[{p['display_name']}]({p['name']}.md)"
            lines.append(f"| {name_cell} | {ver} | {status} | {repo_cell} |")
        lines.append("")
    return "\n".join(lines)


def render_project_page(p: dict) -> str:
    lines = [f"# {p['display_name']}", ""]
    if p.get("icon_url"):
        lines += [f"![{p['display_name']}]({p['icon_url']})", ""]
    if p["display_name"].lower() != p["name"].lower():
        lines += [f"`{p['name']}`", ""]
    lines += [p["description"], "", "| Field | Value |", "| --- | --- |", f"| Type | {p['type']} |"]
    if p["version"]:
        lines.append(f"| Version | v{p['version']} |")
    if p["date"]:
        lines.append(f"| Updated | {p['date']} |")
    if p["status"]:
        lines.append(f"| Status | {p['status']} |")
    if p["url"]:
        url = p["url"] if p["url"].startswith("http") else f"https://{p['url']}"
        lines.append(f"| Live | {url} |")
    web = github_web_url(p["github"])
    if web:
        lines.append(f"| Repo | {web} |")
    lines.append(f"| Local path | `{p['path']}` |")
    lines.append("")
    if p.get("manual"):
        lines.append(p["manual"])
        lines.append("")
    return "\n".join(lines)


def update_home_timestamp(index_path: Path) -> None:
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    text = index_path.read_text(encoding="utf-8")
    replacement = f"_Last updated: {now}_"
    if re.search(r"_Last updated: [^_\n]+_", text):
        text = re.sub(r"_Last updated: [^_\n]+_", replacement, text)
    else:
        text = re.sub(r"(# [^\n]+\n)", f"\\1\n{replacement}\n", text, count=1)
    index_path.write_text(text, encoding="utf-8")


def main(base_dir=None, output_dir=None, repos_json=None, command_center=None, card_map_path=None):
    script_dir = Path(__file__).resolve().parent          # infra/wiki/scripts
    base_dir = Path(base_dir) if base_dir else script_dir.parents[2]  # GitHub root
    output_dir = Path(output_dir) if output_dir else script_dir.parent / "docs" / "projects"
    repos_json = Path(repos_json) if repos_json else base_dir / "infra" / "repos.json"
    command_center = Path(command_center) if command_center else base_dir / "apps" / "drewbefree-command-center" / "index.html"
    card_map_path = Path(card_map_path) if card_map_path else script_dir / "card_map.json"

    repos = scan_repos(base_dir)
    manifest = load_manifest(repos_json)
    cards = parse_command_center(command_center)
    card_map, type_overrides, icon_slugs = load_card_map(card_map_path)
    projects = enrich(repos, manifest, cards, card_map, type_overrides, icon_slugs, base_dir)

    output_dir.mkdir(parents=True, exist_ok=True)
    for old in output_dir.glob("*.md"):
        old.unlink()
    (output_dir / "index.md").write_text(render_index(projects), encoding="utf-8")
    for p in projects:
        (output_dir / f"{p['name']}.md").write_text(render_project_page(p), encoding="utf-8")

    for w in detect_drift(repos, manifest, base_dir):
        print(f"  [drift] {w}", file=sys.stderr)
    print(f"Generated {len(projects)} project pages in {output_dir}")

    home = script_dir.parent / "docs" / "index.md"
    update_home_timestamp(home)
    print(f"Updated timestamp in {home}")


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--timestamp-only", action="store_true", help="Only update the home page timestamp, skip catalog regeneration")
    args = parser.parse_args()
    if args.timestamp_only:
        script_dir = Path(__file__).resolve().parent
        update_home_timestamp(script_dir.parent / "docs" / "index.md")
        print("Updated timestamp (timestamp-only mode)")
    else:
        main()
