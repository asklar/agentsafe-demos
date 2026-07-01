#!/usr/bin/env bash
# One command to run this demo. No dependencies beyond Python 3.10+.
set -euo pipefail
cd "$(dirname "$0")"
exec python3 demo.py "$@"
