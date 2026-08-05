#!/usr/bin/env python3
"""SessionStart hook: inject the context.md briefing and log the session start.

Ported from session-memory.sh so the hook runs where bash does not (native Windows).
The .sh wrapper stays in the repo for anyone invoking it by hand.

Never raises and never blocks a session: every failure path falls through to exit 0.
"""

import json
import os
import sys
import time

# Windows defaults to cp1252 for console output AND for open(, encoding="utf-8"), so both printing a status
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

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
try:
    import _hooklib as HL

    MEM = HL.MEM
except Exception:  # a hook must run even if the shared lib is missing
    MEM = os.environ.get("CLAUDE_MEMORY_DIR") or os.path.expanduser(
        "~/.claude/second-brain-vault"
    )

CONTEXT = os.path.join(MEM, "context.md")
SESSION_LOG = os.path.join(MEM, "_session-log.md")

LOG_HEADER = (
    "# Session Log\n\n"
    "Auto-appended by `session-memory` on each fresh session. Newest at bottom. "
    "Links: [[MEMORY]] · [[context]].\n\n"
)


def read_source():
    """The hook payload names the session's origin: startup, clear, resume or compact."""
    try:
        raw = sys.stdin.read()
    except Exception:
        return ""
    try:
        return json.loads(raw).get("source", "") or ""
    except Exception:
        return ""


def main():
    if not os.path.isdir(MEM):
        return
    source = read_source()
    now = time.strftime("%Y-%m-%d %H:%M %Z")

    if source in ("startup", "clear"):
        try:
            if not os.path.isfile(SESSION_LOG):
                with open(SESSION_LOG, "w", encoding="utf-8") as f:
                    f.write(LOG_HEADER)
            with open(SESSION_LOG, "a", encoding="utf-8") as f:
                f.write(f"- **{now}** — session started (source: {source})\n")
        except OSError:
            pass  # a log we cannot write is not worth failing a session over
        if os.path.isfile(CONTEXT):
            try:
                with open(CONTEXT, encoding="utf-8", errors="replace") as f:
                    body = f.read()
            except OSError:
                body = ""
            out = [
                "=== second-brain memory: full briefing (context.md) ===",
                "",
                f"Your memory is the Markdown vault at {MEM}. MEMORY.md is the index; "
                "notes link with [[wikilinks]]. Full context.md below:",
                "---",
                body,
                "=== end context.md ===",
            ]
            sys.stdout.write("\n".join(out) + "\n")
    elif source in ("resume", "compact"):
        # The conversation already carries the briefing (on compact it was just
        # summarised), but never leave a session blind to memory.
        sys.stdout.write(
            f"🧠 Memory: vault at {MEM} (index [[MEMORY]], hubs [[_MOC-*]], briefing "
            "[[context]]). Stuck or repeating a failure? Run `/second-brain pull <terms>` "
            "before guessing. Substantive work still needs a curated note.\n"
        )


if __name__ == "__main__":
    try:
        main()
    except Exception:
        pass
