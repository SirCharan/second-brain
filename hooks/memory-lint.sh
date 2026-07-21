#!/usr/bin/env bash
# non-blocking hygiene warnings for memory notes
DIR="$(cd "$(dirname "${BASH_SOURCE[0]:-$0}")" && pwd)"
PY=/usr/bin/python3; command -v "$PY" >/dev/null 2>&1 || PY=python3
"$PY" "$DIR/memory-lint.py" 2>/dev/null || true
exit 0
