#!/usr/bin/env bash
# inject living vault state on fresh chats
DIR="$(cd "$(dirname "${BASH_SOURCE[0]:-$0}")" && pwd)"
PY=/usr/bin/python3; command -v "$PY" >/dev/null 2>&1 || PY=python3
"$PY" "$DIR/session-resume.py" 2>/dev/null || true
exit 0
