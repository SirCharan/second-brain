#!/usr/bin/env python3
"""UserPromptSubmit hook: watch the real context-window fill and, once it crosses a
threshold, nudge to dump the session to Obsidian and /clear — which resets input-token
cost to ~zero for the next turns. The transcript records true per-turn token usage
(input + cache_creation + cache_read = total prompt tokens that turn), so this is exact,
not a heuristic.

Config (env):
  SECOND_BRAIN_CTX_WINDOW   model context window in tokens (default 200000)
  SECOND_BRAIN_DUMP_PCT     nudge when fill >= this % of the window (default 50)
Nudges once per session per crossing; after a /clear (new session id) it re-arms.
Never blocks. Prints a JSON additionalContext block only when over threshold.
"""

import sys, os, json

sys.path.insert(0, os.path.expanduser("~/.claude/hooks"))
try:
    import _hooklib as HL
except Exception:
    HL = None

WINDOW = int(os.environ.get("SECOND_BRAIN_CTX_WINDOW", "200000") or 200000)
PCT = float(os.environ.get("SECOND_BRAIN_DUMP_PCT", "50") or 50)
STATE_DIR = os.path.expanduser("~/.claude/hooks/.ctx-monitor")


def last_usage_tokens(tpath):
    """Scan the transcript tail for the most recent assistant usage block; return the
    total prompt tokens in context that turn (input + cache_creation + cache_read)."""
    lines = HL.tail_lines(tpath, max_bytes=262144) if HL else []
    total = 0
    for ln in reversed(lines):  # newest first
        ln = ln.strip()
        if '"usage"' not in ln:
            continue
        try:
            d = json.loads(ln)
        except Exception:
            continue
        u = (d.get("message") or {}).get("usage") or d.get("usage")
        if not isinstance(u, dict):
            continue
        total = (
            int(u.get("input_tokens", 0) or 0)
            + int(u.get("cache_creation_input_tokens", 0) or 0)
            + int(u.get("cache_read_input_tokens", 0) or 0)
        )
        if total > 0:
            return total
    return total


def main():
    if HL is None or not HL.vault_ok():
        return
    try:
        hook = json.loads(sys.stdin.read()) if not sys.stdin.isatty() else {}
    except Exception:
        return
    tpath = hook.get("transcript_path")
    sid = hook.get("session_id") or "nosid"
    if not tpath or not os.path.exists(tpath):
        return

    tokens = last_usage_tokens(tpath)
    if tokens <= 0:
        return
    fill = 100.0 * tokens / WINDOW
    if fill < PCT:
        return

    # nudge once per session (re-arms after /clear because the session id changes)
    try:
        os.makedirs(STATE_DIR, exist_ok=True)
        flag = os.path.join(STATE_DIR, sid)
        if os.path.exists(flag):
            return
        open(flag, "w").write(str(tokens))
    except Exception:
        pass

    msg = (
        f"\U0001f9e0 CONTEXT {fill:.0f}% full ({tokens:,}/{WINDOW:,} tokens). To cut cost: "
        f"run `/obsidian dump` (or `python3 ~/.claude/hooks/context-dump.py`) to save this "
        f"session's state to the vault, then `/clear`. The next turns restart near-empty and "
        f"session-resume reloads the digest. Skip only if you're about to finish."
    )
    sys.stdout.write(
        json.dumps(
            {
                "hookSpecificOutput": {
                    "hookEventName": "UserPromptSubmit",
                    "additionalContext": msg,
                }
            }
        )
    )


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        if HL:
            HL.log_err("context-monitor", e)
