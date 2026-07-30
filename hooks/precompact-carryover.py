#!/usr/bin/env python3
"""PreCompact hook: persist a real state snapshot before context is compacted.

Old version was a static text nudge that saved nothing — if compaction dropped state it was
gone. This tails the transcript and writes the active task, files touched, recent commands, and
errors to _infra/_carryover.md (overwritten each compaction = latest snapshot), then still emits
the compaction-preservation nudge. Ports claude-mem/context-mode's persist-at-compaction idea,
headless. Reads only the transcript TAIL. Never blocks; logs failures.
"""

import os
import sys, os, json, re
from datetime import datetime

import _hooklib as HL

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

NUDGE = (
    "Compaction carry-over — preserve VERBATIM: the active task/plan, files modified this "
    "session, unresolved bugs/errors, key decisions and their rationale, and exact "
    "test/build/deploy commands. Drop resolved tool output and stale exploration first. "
    "A durable snapshot was written to _infra/_carryover.md."
)


def _emit_nudge():
    sys.stdout.write(
        json.dumps(
            {
                "hookSpecificOutput": {
                    "hookEventName": "PreCompact",
                    "additionalContext": NUDGE,
                }
            }
        )
    )


def main():
    _emit_nudge()  # always nudge, even if snapshotting fails
    if not HL.vault_ok():
        return
    try:
        hook = json.loads(sys.stdin.read()) if not sys.stdin.isatty() else {}
    except Exception:
        return
    tpath = hook.get("transcript_path")
    if not tpath or not os.path.exists(tpath):
        return
    cwd = hook.get("cwd") or ""
    branch = hook.get("gitBranch") or ""
    proj = os.path.basename(cwd.rstrip("/")) if cwd else ""

    # one shared parser (1MB tail): a single large tool result used to evict the
    # user/assistant pair from a 512KB window, so the biggest turns captured nothing
    scan = HL.scan_transcript(tpath, max_bytes=1_048_576)
    last_user, last_asst = scan["last_user"], scan["last_asst"]
    files, commands, errors = scan["files"], scan["commands"], scan["errors"]

    now = datetime.now()
    ctx = f"{proj}" + (f"@{branch}" if branch else "") if proj else "(no project)"
    out = [
        "---",
        "name: _carryover",
        "tags: [meta, type/state]",
        f"asserted: {now.strftime('%Y-%m-%d')}",
        "status: active",
        "---",
        "",
        "# Compaction carry-over snapshot",
        "",
        f"Last written **{now.strftime('%Y-%m-%d %H:%M')}** · context: `{ctx}` · "
        "auto-written by the PreCompact hook (overwritten each compaction). ↩ [[_Home]]",
        "",
    ]
    if last_user:
        u = re.sub(r"\s+", " ", last_user).strip()
        out += ["## Active task (last user prompt)", "", u[:600], ""]
    if last_asst:
        a = last_asst.strip()
        # drop capture footer noise
        a = re.sub(r"<!--\s*CAPTURE:.*?-->", "", a, flags=re.S).strip()
        out += ["## Where Claude left off", "", a[:600], ""]
    if files:
        out += (
            ["## Files touched this session"] + [f"- `{f}`" for f in files[-15:]] + [""]
        )
    if commands:
        out += ["## Recent commands"] + [f"- `{c}`" for c in commands[-8:]] + [""]
    if errors:
        # dedup while preserving order
        seen, uniq = set(), []
        for e in errors:
            if e not in seen:
                seen.add(e)
                uniq.append(e)
        out += (
            ["## Unresolved errors/warnings seen"]
            + [f"- {e}" for e in uniq[-6:]]
            + [""]
        )

    path = os.path.join(HL.MEM, "_infra", "_carryover.md")
    try:
        HL.atomic_write(path, "\n".join(out) + "\n")
    except Exception as e:
        HL.log_err("precompact-carryover.write", e)


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        HL.log_err("precompact-carryover", e)
