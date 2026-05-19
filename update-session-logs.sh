#!/bin/bash
# Update SESSION_LOG.md in all touched repositories
# Detects repos with recent git activity and updates/creates SESSION_LOG.md
# Reads baseDirectory from repos.json (portable across systems)
# Usage: ./update-session-logs.sh -s "What was done" -e "Where we stopped" -n "What's next"

SUMMARY=""
STOPPED=""
NEXT=""
BASE_DIR=""

while getopts "s:e:n:h" opt; do
    case $opt in
        s) SUMMARY="$OPTARG" ;;
        e) STOPPED="$OPTARG" ;;
        n) NEXT="$OPTARG" ;;
        h) echo "Usage: $0 -s 'summary' -e 'stopped' -n 'next'"; exit 0 ;;
    esac
done

if [ -z "$SUMMARY" ]; then
    echo "Usage: $0 -s 'What was done' -e 'Where we stopped' -n 'What's next'"
    exit 1
fi

# Load base directory from repos.json
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
MANIFEST="$SCRIPT_DIR/repos.json"

if [ ! -f "$MANIFEST" ]; then
    echo "Error: repos.json not found at $MANIFEST"
    exit 1
fi

BASE_DIR=$(jq -r '.baseDirectory' "$MANIFEST" | sed 's|\\|/|g')

# Convert Windows path to WSL path if needed
if [[ "$BASE_DIR" =~ ^C: ]]; then
    # C:/Users/... becomes /mnt/c/Users/...
    BASE_DIR="/mnt/c/${BASE_DIR:3}"
fi

TODAY=$(date +%Y-%m-%d)
REPOS=()

# Find all git repos with recent changes
for dir in "$BASE_DIR"/*; do
    if [ -d "$dir/.git" ]; then
        cd "$dir"

        # Check for uncommitted changes or recent commits (last hour)
        if git status --porcelain | grep -q . || git log --oneline -1 --since="1 hour ago" | grep -q .; then
            REPOS+=("$dir")
        fi

        cd - > /dev/null
    fi
done

if [ ${#REPOS[@]} -eq 0 ]; then
    echo "No repositories with recent changes found."
    exit 0
fi

echo "Found ${#REPOS[@]} repository(ies) with recent changes:"
for repo in "${REPOS[@]}"; do
    echo "  • $(basename "$repo")"
done
echo ""

for repo in "${REPOS[@]}"; do
    repo_name=$(basename "$repo")
    log_path="$repo/SESSION_LOG.md"

    echo "Updating: $repo_name"

    # Create session log entry
    entry="## $TODAY

**What we did:**
$SUMMARY

**Where we stopped:**
$STOPPED

**Next up:**
$NEXT

"

    # Read existing log or create new
    if [ -f "$log_path" ]; then
        existing=$(cat "$log_path")
        new_content="# Session Log

$entry
$existing"
    else
        new_content="# Session Log

$entry"
    fi

    # Write updated log
    echo "$new_content" > "$log_path"

    # Commit and push
    cd "$repo"
    git add SESSION_LOG.md
    git commit -m "Update session log: $TODAY" > /dev/null 2>&1
    git push > /dev/null 2>&1
    cd - > /dev/null

    echo "  ✓ Updated"
done

echo ""
echo "✓ Session logs updated across all touched repositories"
