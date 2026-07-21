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
    last_user = None
    files, commands, errors = [], [], []
    for ln in HL.tail_lines(tpath, max_bytes=524288):
        ln = ln.strip()
        if not ln:
            continue
        try:
            d = json.loads(ln)
        except Exception:
            continue
        msg = d.get("message") or {}
        role = msg.get("role")
        content = msg.get("content")
        text = ""
        if isinstance(content, str):
            text = content
        elif isinstance(content, list):
            for b in content:
                if isinstance(b, dict):
                    if b.get("type") == "text":
                        text += b.get("text", "") + "\n"
                    if b.get("type") == "tool_use":
                        ti = b.get("input") or {}
                        if b.get("name") in ("Edit", "Write") and ti.get("file_path"):
                            fp = ti["file_path"]
                            if fp not in files:
                                files.append(fp)
                        if b.get("name") == "Bash" and ti.get("command"):
                            commands.append(ti["command"].strip().split("\n")[0][:120])
        if role == "user" and isinstance(content, str) and not content.startswith("<"):
            last_user = content.strip()[:400]
        if "error" in text.lower() or "traceback" in text.lower():
            m = re.search(r"(?im)^(.*(error|traceback|failed).*)$", text)
            if m:
                errors.append(m.group(1).strip()[:160])
    return last_user, files[-12:], commands[-8:], errors[-4:]


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
