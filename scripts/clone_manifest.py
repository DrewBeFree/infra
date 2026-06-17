#!/usr/bin/env python3
"""Clone or sync every repo in repos.json into a target workspace."""

from __future__ import annotations

import argparse
import json
import subprocess
from pathlib import Path


def ssh_url(repo_url: str) -> str:
    path = repo_url.rstrip("/").removesuffix(".git").split("github.com/")[-1]
    return f"git@github.com:{path}.git"


def run(cmd: list[str], cwd: Path | None = None, dry_run: bool = False) -> subprocess.CompletedProcess[str]:
    if dry_run:
        location = f" cwd={cwd}" if cwd else ""
        print(f"DRY {' '.join(cmd)}{location}")
        return subprocess.CompletedProcess(cmd, 0, "", "")
    return subprocess.run(cmd, cwd=cwd, text=True, capture_output=True, check=False)


def output(result: subprocess.CompletedProcess[str]) -> str:
    return (result.stdout or result.stderr).strip()


def git(repo: Path, *args: str, dry_run: bool = False) -> subprocess.CompletedProcess[str]:
    return run(["git", *args], cwd=repo, dry_run=dry_run)


def is_git_repo(target: Path) -> bool:
    return (target / ".git").exists()


def upstream_counts(target: Path) -> tuple[int, int] | None:
    upstream = output(git(target, "rev-parse", "--abbrev-ref", "--symbolic-full-name", "@{u}"))
    if not upstream or "fatal:" in upstream.lower():
        return None
    counts = output(git(target, "rev-list", "--left-right", "--count", "HEAD...@{u}")).split()
    if len(counts) != 2:
        return None
    return int(counts[0]), int(counts[1])


def sync_existing(target: Path, name: str, do_pull: bool, dry_run: bool) -> bool:
    if not is_git_repo(target):
        print(f"FAIL {name}: exists but is not a git repo: {target}")
        return False

    fetch = git(target, "fetch", "--all", "--prune", dry_run=dry_run)
    if fetch.returncode:
        print(f"FAIL {name}: fetch failed: {output(fetch)}")
        return False

    if not do_pull:
        print(f"PRESENT {name}: {target}")
        return True

    dirty = output(git(target, "status", "--porcelain"))
    if dirty:
        print(f"SKIP {name}: dirty working tree ({len(dirty.splitlines())} changes): {target}")
        return True

    counts = upstream_counts(target)
    if counts is None:
        print(f"SKIP {name}: no upstream configured: {target}")
        return True

    ahead, behind = counts
    if ahead:
        print(f"SKIP {name}: local branch is ahead by {ahead}: {target}")
        return True
    if behind == 0:
        print(f"CURRENT {name}: {target}")
        return True

    pull = git(target, "pull", "--ff-only", dry_run=dry_run)
    if pull.returncode:
        print(f"FAIL {name}: pull failed: {output(pull)}")
        return False
    print(f"PULLED {name}: {target}")
    return True


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", type=Path, default=Path("repos.json"))
    parser.add_argument("--base", type=Path, required=True)
    parser.add_argument("--ssh", action="store_true", help="Convert GitHub URLs to SSH.")
    parser.add_argument("--pull", action="store_true", help="Fast-forward clean existing repos after fetching.")
    parser.add_argument("--dry-run", action="store_true", help="Print git operations without running them.")
    args = parser.parse_args()

    manifest = json.loads(args.manifest.read_text(encoding="utf-8"))
    args.base.mkdir(parents=True, exist_ok=True)
    failed = 0

    for repo in manifest["repositories"]:
        target = args.base / repo["targetDirectory"]
        if target.exists():
            if not sync_existing(target, repo["name"], args.pull, args.dry_run):
                failed += 1
            continue
        target.parent.mkdir(parents=True, exist_ok=True)
        url = ssh_url(repo["github"]) if args.ssh else repo["github"]
        print(f"CLONE {repo['name']}: {target}")
        result = run(["git", "clone", url, str(target)], dry_run=args.dry_run)
        if result.returncode:
            failed += 1
            print(f"FAIL {repo['name']}: {output(result) or f'exit {result.returncode}'}")

    raise SystemExit(1 if failed else 0)


if __name__ == "__main__":
    main()
