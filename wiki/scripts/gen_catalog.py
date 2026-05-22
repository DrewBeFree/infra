#!/usr/bin/env python3
"""Generate the wiki Projects catalog from the local filesystem, repos.json, and the Command Center."""
from __future__ import annotations

import json
import sys
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


def load_card_map(card_map_path: Path) -> dict:
    if not card_map_path.is_file():
        return {}
    return json.loads(card_map_path.read_text(encoding="utf-8"))


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
