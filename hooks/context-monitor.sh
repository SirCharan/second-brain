#!/usr/bin/env bash
# UserPromptSubmit: nudge to dump+clear when the context window crosses the threshold
DIR="$(cd "$(dirname "${BASH_SOURCE[0]:-$0}")" && pwd)"
PY=/usr/bin/python3; command -v "$PY" >/dev/null 2>&1 || PY=python3
"$PY" "$DIR/context-monitor.py" 2>/dev/null || true
exit 0
