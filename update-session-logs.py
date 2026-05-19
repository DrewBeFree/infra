#!/usr/bin/env python3
"""Update SESSION_LOG.md in all touched repositories.
Detects repos with recent git activity and updates/creates SESSION_LOG.md.
Reads baseDirectory from repos.json (portable across systems).

Usage: python3 update-session-logs.py -s "What was done" -e "Where we stopped" -n "What's next"
"""

import json
import os
import sys
import subprocess
import argparse
import platform
from pathlib import Path
from datetime import datetime, timedelta

def convert_windows_to_wsl_path(path):
    """Convert Windows path (C:\\Users\\...) to WSL path (/mnt/c/Users/...)"""
    # Handle both backslashes and forward slashes
    path = path.replace("\\", "/")

    # Check if it's a Windows drive letter path
    if len(path) >= 2 and path[1] == ':':
        # C: -> /mnt/c, D: -> /mnt/d, etc.
        drive_letter = path[0].lower()
        rest = path[2:]
        return f"/mnt/{drive_letter}{rest}"

    return path

def is_wsl():
    """Detect if running in WSL"""
    return "microsoft" in platform.release().lower() or "wsl" in platform.release().lower()

def has_recent_changes(repo_path):
    """Check if repo has uncommitted changes or recent commits (last hour)"""
    try:
        # Check for uncommitted changes
        result = subprocess.run(
            ["git", "status", "--porcelain"],
            cwd=repo_path,
            capture_output=True,
            text=True,
            timeout=10
        )
        if result.stdout.strip():
            return True

        # Check for recent commits (last hour)
        result = subprocess.run(
            ["git", "log", "--oneline", "-1", "--since=1 hour ago"],
            cwd=repo_path,
            capture_output=True,
            text=True,
            timeout=10
        )
        if result.stdout.strip():
            return True

        return False
    except Exception:
        return False

def update_session_logs(summary, stopped, next_steps):
    """Update session logs in all touched repositories"""
    script_dir = Path(__file__).parent
    manifest_path = script_dir / "repos.json"

    if not manifest_path.exists():
        print(f"Error: repos.json not found at {manifest_path}")
        sys.exit(1)

    with open(manifest_path, 'r') as f:
        manifest = json.load(f)

    base_dir = manifest["baseDirectory"]

    # Convert Windows path to WSL if needed
    if is_wsl():
        base_dir = convert_windows_to_wsl_path(base_dir)

    today = datetime.now().strftime("%Y-%m-%d")
    touched_repos = []

    # Find all git repos with recent changes
    for item in Path(base_dir).iterdir():
        if item.is_dir() and (item / ".git").exists():
            if has_recent_changes(item):
                touched_repos.append(item)

    if not touched_repos:
        print("No repositories with recent changes found.")
        return

    print(f"Found {len(touched_repos)} repository(ies) with recent changes:")
    for repo in touched_repos:
        print(f"  • {repo.name}")
    print()

    for repo in touched_repos:
        repo_name = repo.name
        log_path = repo / "SESSION_LOG.md"

        print(f"Updating: {repo_name}")

        # Create session log entry
        entry = f"""## {today}

**What we did:**
{summary}

**Where we stopped:**
{stopped}

**Next up:**
{next_steps}

"""

        # Read existing log or create new
        if log_path.exists():
            with open(log_path, 'r') as f:
                existing = f.read()
            new_content = f"""# Session Log

{entry}{existing}"""
        else:
            new_content = f"""# Session Log

{entry}"""

        # Write updated log
        with open(log_path, 'w') as f:
            f.write(new_content)

        # Commit and push
        try:
            subprocess.run(["git", "add", "SESSION_LOG.md"], cwd=repo, capture_output=True, timeout=10)
            subprocess.run(
                ["git", "commit", "-m", f"Update session log: {today}"],
                cwd=repo,
                capture_output=True,
                timeout=10
            )
            subprocess.run(["git", "push"], cwd=repo, capture_output=True, timeout=30)
            print(f"  ✓ Updated")
        except Exception as e:
            print(f"  ✗ Failed to commit/push: {e}")

    print()
    print("✓ Session logs updated across all touched repositories")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Update session logs in touched repositories")
    parser.add_argument("-s", "--summary", required=True, help="What was done")
    parser.add_argument("-e", "--stopped", required=True, help="Where we stopped")
    parser.add_argument("-n", "--next", required=True, help="What's next", dest="next_steps")

    args = parser.parse_args()

    update_session_logs(args.summary, args.stopped, args.next_steps)
