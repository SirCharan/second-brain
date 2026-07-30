#!/usr/bin/env python3
"""Idempotently add v2 frontmatter fields (asserted,last_confirmed,source,confidence,status,supersedes)
to any memory note missing them. Safe to re-run. Defaults dates to file mtime."""

import os, re, glob, sys

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

_here = os.path.dirname(os.path.abspath(__file__))
_HD = next(
    (
        p
        for p in (
            os.path.join(os.environ["CLAUDE_PLUGIN_ROOT"], "hooks")
            if os.environ.get("CLAUDE_PLUGIN_ROOT")
            else None,
            os.path.join(
                os.path.dirname(os.path.abspath(__file__)), "..", "..", "..", "hooks"
            ),
            os.path.expanduser("~/.claude/hooks"),
        )
        if p and os.path.isfile(os.path.join(p, "_hooklib.py"))
    ),
    os.path.expanduser("~/.claude/hooks"),
)
sys.path.insert(0, _HD)
sys.path.insert(0, os.path.join(_here, "..", "..", "..", "hooks"))
import _hooklib as HL
from datetime import datetime

MEM = os.environ.get("CLAUDE_MEMORY_DIR") or os.path.expanduser(
    "~/.claude/second-brain-vault"
)
NEW = ["asserted", "last_confirmed", "source", "confidence", "status", "supersedes"]
ch = 0
for p in glob.glob(os.path.join(MEM, "**", "*.md"), recursive=True):
    b = os.path.basename(p)
    if b in ("MEMORY.md", "context.md", "_session-log.md") or "/Daily/" in p:
        continue

    try:
        t = open(p, errors="ignore").read()
    except Exception:
        continue
    if not t.startswith("---\n"):
        continue
    e = t.find("\n---", 4)
    if e == -1:
        continue
    present = {m.group(1) for m in re.finditer(r"^([A-Za-z_]+):", t[4 : e + 1], re.M)}
    d = datetime.fromtimestamp(os.path.getmtime(p)).strftime("%Y-%m-%d")
    dv = {
        "asserted": d,
        "last_confirmed": d,
        "source": "inferred",
        "confidence": "med",
        "status": "active",
        "supersedes": "[]",
    }
    add = [f"{k}: {dv[k]}" for k in NEW if k not in present]
    if add:
        HL.atomic_write(p, "---\n" + "\n".join(add) + "\n" + t[4:])
        ch += 1
print(f"migrated {ch} note(s)")
