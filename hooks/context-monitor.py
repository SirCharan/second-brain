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

import os
import sys, os, json

# Windows defaults to cp1252 for console output AND for open(), so both printing a status
# glyph and reading a note containing an emoji raise. Interpreter UTF-8 mode fixes both, and
# can only be set at startup, so re-exec into it once when we were not started that way.
if (
    __name__ == "__main__"  # never re-exec when imported as a library
    and os.name == "nt"
    and not sys.flags.utf8_mode
    and not os.environ.get("SB_UTF8_REEXEC")
    and getattr(sys, "frozen", None) is None
):
    # os.execv does not replace the process on Windows: the parent exits immediately with
    # its own status while the child keeps running, so the caller reads the wrong exit
    # code. Re-run synchronously and pass the child's code up. stdin/stdout are inherited,
    # so a hook still receives its JSON payload.
    import subprocess

    os.environ["SB_UTF8_REEXEC"] = "1"
    try:
        sys.exit(
            subprocess.run(
                [sys.executable, "-X", "utf8", os.path.abspath(__file__), *sys.argv[1:]]
            ).returncode
        )
    except OSError:
        pass  # fall through to the stream guard rather than refusing to run
for _stream in (sys.stdout, sys.stderr):
    if hasattr(_stream, "reconfigure"):
        try:
            _stream.reconfigure(encoding="utf-8", errors="replace")
        except Exception:
            pass

sys.path.insert(
    0, os.path.dirname(os.path.abspath(__file__))
)  # _hooklib is a sibling (both install modes)
try:
    import _hooklib as HL
except Exception:
    HL = None

WINDOW = int(os.environ.get("SECOND_BRAIN_CTX_WINDOW", "200000") or 200000)
PCT = float(os.environ.get("SECOND_BRAIN_DUMP_PCT", "50") or 50)
STATE_DIR = (
    os.path.join(HL.STATE_DIR, ".ctx-monitor")
    if HL
    else os.path.expanduser("~/.second-brain/.ctx-monitor")
)


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

    # Fire on each crossing; re-arm when context grows another 30% past the last dump
    # (also re-arms after /clear, because the session id changes).
    try:
        os.makedirs(STATE_DIR, exist_ok=True)
        flag = os.path.join(STATE_DIR, sid)
        prev = 0
        if os.path.exists(flag):
            try:
                prev = int(open(flag).read().strip() or 0)
            except Exception:
                prev = 0
        if prev and tokens <= prev * 1.3:
            return
        open(flag, "w").write(str(tokens))
    except Exception:
        pass

    # Auto-persist session state to the vault, detached so the prompt never waits.
    # Compaction and /clear become non-events: the carryover digest is always current.
    try:
        import subprocess

        dump = os.path.join(
            os.path.dirname(os.path.abspath(__file__)), "context-dump.py"
        )
        if os.path.exists(dump):
            subprocess.Popen(
                [sys.executable, "-X", "utf8", dump, tpath],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                **(HL.detach_kwargs() if HL else {}),
            )
    except Exception as e:
        if HL:
            HL.log_err("context-monitor.dump", e)

    msg = (
        f"\U0001f9e0 CONTEXT {fill:.0f}% full ({tokens:,}/{WINDOW:,} tokens). Session state "
        f"auto-saved to the vault (`_infra/_carryover.md`) — `/clear` is safe anytime, and "
        f"session-resume reloads the digest. For a richer hand-written snapshot first, run "
        f"`/second-brain dump`."
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
