#!/usr/bin/env python3
"""Clone all repositories to their target directories.
Usage: python3 clone-all.py [optional_base_dir]
Supports both Windows and WSL paths.
"""

import json
import os
import sys
import subprocess
import platform
from pathlib import Path

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

def clone_all(base_dir=None):
    """Clone all repositories from repos.json"""
    script_dir = Path(__file__).parent
    manifest_path = script_dir / "repos.json"

    if not manifest_path.exists():
        print(f"Error: repos.json not found at {manifest_path}")
        sys.exit(1)

    with open(manifest_path, 'r') as f:
        manifest = json.load(f)

    # Use provided base directory or fallback to manifest default
    if base_dir is None:
        base_dir = manifest["baseDirectory"]

    # Convert Windows path to WSL if needed
    if is_wsl():
        base_dir = convert_windows_to_wsl_path(base_dir)

    print(f"Cloning repositories to: {base_dir}")
    print(f"Manifest: {manifest_path}")
    print()

    success_count = 0
    skip_count = 0
    fail_count = 0

    for repo in manifest["repositories"]:
        name = repo["name"]
        git_url = repo["github"]
        target_dir = repo["targetDirectory"]
        target_path = Path(base_dir) / target_dir

        # Check if already cloned
        if target_path.exists():
            print(f"⊘ {name}")
            print(f"  Already exists at {target_path}")
            skip_count += 1
            continue

        # Create parent directory if needed
        target_path.parent.mkdir(parents=True, exist_ok=True)

        # Clone repository
        print(f"→ {name}")
        print(f"  Cloning to: {target_path}")

        try:
            subprocess.run(
                ["git", "clone", git_url, str(target_path)],
                capture_output=True,
                check=True,
                timeout=300
            )
            print(f"  ✓ Success")
            success_count += 1
        except (subprocess.CalledProcessError, subprocess.TimeoutExpired) as e:
            print(f"  ✗ Failed: {e}")
            fail_count += 1

        print()

    print("────────────────────────────────")
    print("Summary:")
    print(f"  ✓ Cloned: {success_count}")
    print(f"  ⊘ Skipped: {skip_count}")
    print(f"  ✗ Failed: {fail_count}")

    return fail_count == 0

if __name__ == "__main__":
    base_dir = sys.argv[1] if len(sys.argv) > 1 else None
    success = clone_all(base_dir)
    sys.exit(0 if success else 1)
