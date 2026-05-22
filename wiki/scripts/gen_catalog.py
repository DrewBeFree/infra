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
