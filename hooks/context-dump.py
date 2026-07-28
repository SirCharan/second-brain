#!/usr/bin/env python3
"""On-demand context dump: parse a session transcript and write a resume digest to the
vault (_infra/_carryover.md), so a fresh /clear'd session (or the next loop iteration)
picks up cheaply. This is the automatic/fallback dump; the richest dump is the agent
writing its own carryover via `/second-brain dump`, but this needs no agent in the loop.

Usage:
  context-dump.py [/path/to/transcript.jsonl]
  (no arg → newest transcript under ~/.claude/projects)
Writes _infra/_carryover.md and appends a one-line marker to today's Daily note.
"""

import sys, os, json, glob, re
from datetime import datetime

sys.path.insert(
    0, os.path.dirname(os.path.abspath(__file__))
)  # _hooklib is a sibling (both install modes)
import _hooklib as HL


def newest_transcript():
    fs = glob.glob(os.path.expanduser("~/.claude/projects/**/*.jsonl"), recursive=True)
    return max(fs, key=os.path.getmtime) if fs else None


def extract(tpath):
    """Shared parser: real user prompts, files, commands, and only harness-flagged
    tool errors (the old text scan matched any file containing the word 'error')."""
    scan = HL.scan_transcript(tpath, max_bytes=1_048_576)
    last_user = (scan["last_user"] or "")[:400] or None
    return last_user, scan["files"][-12:], scan["commands"][-8:], scan["errors"][-4:]


def main():
    if not HL.vault_ok():
        print("no vault; skipped")
        return
    tpath = sys.argv[1] if len(sys.argv) > 1 else newest_transcript()
    if not tpath or not os.path.exists(tpath):
        print("no transcript")
        return
    last_user, files, commands, errors = extract(tpath)
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    out = [
        "---",
        "name: _carryover",
        "tags: [meta, type/system]",
        "status: active",
        "---",
        "",
        f"# Carry-over — {now}",
        "",
        "> [!info] Resume digest — written on context dump. session-resume injects this next session.",
        "",
        f"**Last ask:** {last_user or '(unknown)'}",
        "",
        "## Files touched",
        *([f"- `{f}`" for f in files] or ["- (none captured)"]),
        "",
        "## Recent commands",
        *([f"- `{c}`" for c in commands] or ["- (none captured)"]),
        "",
    ]
    if errors:
        out += ["## Unresolved errors", *[f"- {e}" for e in errors], ""]
    out += ["## Related", "- [[_MOC-infra]]", ""]
    path = os.path.join(HL.MEM, "_infra", "_carryover.md")
    HL.atomic_write(path, HL.scrub_secrets("\n".join(out)))
    print(f"dumped → {path} ({len(files)} files, {len(commands)} cmds)")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        HL.log_err("context-dump", e)
        print("dump failed:", e)
