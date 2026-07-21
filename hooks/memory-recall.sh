#!/usr/bin/env bash
# inject vault notes relevant to the current prompt (JIT recall)
DIR="$(cd "$(dirname "${BASH_SOURCE[0]:-$0}")" && pwd)"
PY=/usr/bin/python3; command -v "$PY" >/dev/null 2>&1 || PY=python3
"$PY" "$DIR/memory-recall.py" 2>/dev/null || true
exit 0
