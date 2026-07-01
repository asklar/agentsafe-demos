#!/usr/bin/env bash
# record.sh — repeatable demo capture for the agentlab.
#
# Usage:
#   capture/record.sh <demo-dir>            # e.g. capture/record.sh 00-hello-gate
#   capture/record.sh <demo-dir> --plain    # skip asciinema, just tee a text log
#
# Produces, under capture/out/<demo-dir>/:
#   run.txt         always — the raw terminal output (great for READMEs/diffs)
#   run.cast        if `asciinema` is installed — replayable terminal recording
#   run.gif|run.svg if a converter is installed (agg or svg-term-cli)
#
# The pipeline degrades gracefully: with zero tools installed you still get
# run.txt, which is enough to paste into a README. Nothing here is required to
# run a demo — it's purely for turning a demo into shareable content.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
DEMO="${1:-}"
MODE="${2:-}"

if [[ -z "$DEMO" ]]; then
  echo "usage: capture/record.sh <demo-dir> [--plain]" >&2
  echo "available demos:" >&2
  ls -1 "$ROOT/demos" | grep -v '^_template$' | sed 's/^/  - /' >&2
  exit 2
fi

DEMO_DIR="$ROOT/demos/$DEMO"
if [[ ! -x "$DEMO_DIR/run.sh" && ! -f "$DEMO_DIR/demo.py" ]]; then
  echo "no runnable demo at $DEMO_DIR" >&2
  exit 1
fi

OUT="$ROOT/capture/out/$DEMO"
mkdir -p "$OUT"
RUN_CMD=("$DEMO_DIR/run.sh")
[[ -x "$DEMO_DIR/run.sh" ]] || RUN_CMD=(python3 "$DEMO_DIR/demo.py")

echo ">> capturing '$DEMO' -> $OUT"

# 1) Always capture plain text output.
"${RUN_CMD[@]}" | tee "$OUT/run.txt"
echo ">> wrote $OUT/run.txt"

if [[ "$MODE" == "--plain" ]]; then
  exit 0
fi

# 2) asciinema cast (replayable), if available.
if command -v asciinema >/dev/null 2>&1; then
  asciinema rec --overwrite --command "${RUN_CMD[*]}" "$OUT/run.cast" >/dev/null
  echo ">> wrote $OUT/run.cast  (play: asciinema play $OUT/run.cast)"

  # 3) Convert to GIF/SVG if a converter is present.
  if command -v agg >/dev/null 2>&1; then
    agg "$OUT/run.cast" "$OUT/run.gif" && echo ">> wrote $OUT/run.gif"
  elif command -v svg-term >/dev/null 2>&1; then
    svg-term --in "$OUT/run.cast" --out "$OUT/run.svg" && echo ">> wrote $OUT/run.svg"
  else
    echo ">> (install 'agg' or 'svg-term-cli' to auto-generate a GIF/SVG)"
  fi
else
  echo ">> (install 'asciinema' for a replayable .cast recording)"
fi

echo ">> done. Assets in $OUT"
