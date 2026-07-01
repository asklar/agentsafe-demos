#!/usr/bin/env bash
# new_demo.sh — scaffold a new demo from demos/_template in one command.
#
# Usage:
#   ./new_demo.sh <slug> ["Human Readable Title"]
#
# Example:
#   ./new_demo.sh injection-tripwire "Injection Tripwire"
#   -> creates demos/NN-injection-tripwire/ from the template, with placeholders
#      filled in, ready to edit and run.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")" && pwd)"
SLUG="${1:-}"
TITLE="${2:-}"

if [[ -z "$SLUG" ]]; then
  echo "usage: ./new_demo.sh <slug> [\"Title\"]" >&2
  exit 2
fi

# Normalise slug: lowercase, spaces/underscores -> hyphens.
SLUG="$(echo "$SLUG" | tr '[:upper:] _' '[:lower:]--' | sed 's/[^a-z0-9-]//g')"
[[ -n "$TITLE" ]] || TITLE="$(echo "$SLUG" | tr '-' ' ')"

# Next 2-digit ordinal based on existing demos.
LAST="$(ls -1 "$ROOT/demos" | grep -E '^[0-9]{2}-' | sed 's/-.*//' | sort -n | tail -1 || true)"
NEXT="$(printf '%02d' $(( 10#${LAST:-0} + 1 )))"
NAME="${NEXT}-${SLUG}"
DEST="$ROOT/demos/$NAME"

if [[ -e "$DEST" ]]; then
  echo "already exists: $DEST" >&2
  exit 1
fi

cp -r "$ROOT/demos/_template" "$DEST"
rm -rf "$DEST"/tests/__pycache__ "$DEST"/audit.log.jsonl 2>/dev/null || true

# Fill placeholders.
grep -rl '{{DEMO_TITLE}}\|{{DEMO_DIR}}' "$DEST" | while read -r f; do
  sed -i "s|{{DEMO_TITLE}}|$TITLE|g; s|{{DEMO_DIR}}|$NAME|g" "$f"
done

chmod +x "$DEST/run.sh"

echo "created demos/$NAME"
echo "next:"
echo "  1. edit demos/$NAME/demo.py  (AGENT_PLAN + build_governed)"
echo "  2. ./demos/$NAME/run.sh"
echo "  3. capture/record.sh $NAME"
