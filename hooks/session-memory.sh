#!/usr/bin/env bash
# SessionStart hook: inject context.md briefing + append a session-start line to the log.
# No pipefail — must never break session start. Always exit 0.
PY=/usr/bin/python3; command -v "$PY" >/dev/null 2>&1 || PY=python3
MEM_DIR="${CLAUDE_MEMORY_DIR:-$HOME/.claude/second-brain-vault}"
CONTEXT="${MEM_DIR}/context.md"
SESSION_LOG="${MEM_DIR}/_session-log.md"
[ -d "$MEM_DIR" ] || exit 0

input="$(cat 2>/dev/null || true)"
source="$(printf '%s' "$input" | "$PY" -c 'import sys,json
try: print(json.load(sys.stdin).get("source",""))
except Exception: print("")' 2>/dev/null || true)"
now="$(date "+%Y-%m-%d %H:%M %Z" 2>/dev/null || date)"

case "$source" in
  startup|clear)
    if [ ! -f "$SESSION_LOG" ]; then
      { printf '%s\n' "# Session Log"
        printf '%s\n\n' "Auto-appended by \`session-memory.sh\` on each fresh session. Newest at bottom. Links: [[MEMORY]] · [[context]]."
      } > "$SESSION_LOG" 2>/dev/null || true
    fi
    printf -- '- **%s** — session started (source: %s)\n' "$now" "$source" >> "$SESSION_LOG" 2>/dev/null || true
    if [ -f "$CONTEXT" ]; then
      printf '%s\n\n' "=== Obsidian-backed memory: full briefing (context.md) ==="
      printf '%s\n' "Your memory lives in the Obsidian vault (symlink to ~/.claude/.../memory). MEMORY.md is the index; notes use [[wikilinks]]. Full context.md below:"
      printf '%s\n' "---"
      cat "$CONTEXT" 2>/dev/null || true
      printf '\n%s\n' "=== end context.md ==="
    fi
    ;;
esac
exit 0
