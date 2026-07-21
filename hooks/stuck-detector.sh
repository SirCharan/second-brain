#!/usr/bin/env bash
# PostToolUse(Bash): nudge to query memory when the same command keeps failing
DIR="$(cd "$(dirname "${BASH_SOURCE[0]:-$0}")" && pwd)"
PY=/usr/bin/python3; command -v "$PY" >/dev/null 2>&1 || PY=python3
"$PY" "$DIR/stuck-detector.py" 2>/dev/null || true
exit 0
