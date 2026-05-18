#!/bin/bash
# Clone all repositories to their target directories
# Usage: ./clone-all.sh
# Or:    ./clone-all.sh /custom/base/path

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
MANIFEST="$SCRIPT_DIR/repos.json"

if [ ! -f "$MANIFEST" ]; then
    echo "Error: repos.json not found at $MANIFEST"
    exit 1
fi

# Use provided base directory or fallback to manifest default
if [ -z "$1" ]; then
    BASE_DIR=$(jq -r '.baseDirectory' "$MANIFEST" | sed 's|\\|/|g')
else
    BASE_DIR="$1"
fi

echo "Cloning repositories to: $BASE_DIR"
echo "Manifest: $MANIFEST"
echo ""

SUCCESS_COUNT=0
SKIP_COUNT=0
FAIL_COUNT=0

# Parse repos from JSON and clone each
jq -c '.repositories[]' "$MANIFEST" | while read -r repo; do
    NAME=$(echo "$repo" | jq -r '.name')
    GIT_URL=$(echo "$repo" | jq -r '.github')
    TARGET_DIR=$(echo "$repo" | jq -r '.targetDirectory')
    TARGET_PATH="$BASE_DIR/$TARGET_DIR"

    # Check if already cloned
    if [ -d "$TARGET_PATH" ]; then
        echo "⊘ $NAME"
        echo "  Already exists at $TARGET_PATH"
        ((SKIP_COUNT++))
        continue
    fi

    # Create parent directory if needed
    PARENT_DIR=$(dirname "$TARGET_PATH")
    mkdir -p "$PARENT_DIR"

    # Clone repository
    echo "→ $NAME"
    echo "  Cloning to: $TARGET_PATH"

    if git clone "$GIT_URL" "$TARGET_PATH" > /dev/null 2>&1; then
        echo "  ✓ Success"
        ((SUCCESS_COUNT++))
    else
        echo "  ✗ Failed"
        ((FAIL_COUNT++))
    fi
    echo ""
done

echo "────────────────────────────────"
echo "Summary:"
echo "  ✓ Cloned: $SUCCESS_COUNT"
echo "  ⊘ Skipped: $SKIP_COUNT"
echo "  ✗ Failed: $FAIL_COUNT"

if [ "$FAIL_COUNT" -gt 0 ]; then
    exit 1
fi
