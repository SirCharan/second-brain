#!/usr/bin/env bash
# file a one-line capture of the finished exchange into today's daily note
DIR="$(cd "$(dirname "${BASH_SOURCE[0]:-$0}")" && pwd)"
PY=/usr/bin/python3; command -v "$PY" >/dev/null 2>&1 || PY=python3
"$PY" "$DIR/capture-exchange.py" 2>/dev/null || true
exit 0
