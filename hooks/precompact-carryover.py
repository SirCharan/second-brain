#!/usr/bin/env python3
"""PreCompact hook: persist a real state snapshot before context is compacted.

Old version was a static text nudge that saved nothing — if compaction dropped state it was
gone. This tails the transcript and writes the active task, files touched, recent commands, and
errors to _infra/_carryover.md (overwritten each compaction = latest snapshot), then still emits
the compaction-preservation nudge. Ports claude-mem/context-mode's persist-at-compaction idea,
headless. Reads only the transcript TAIL. Never blocks; logs failures.
"""

import sys, os, json, re
from datetime import datetime

import _hooklib as HL

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

    last_user = last_asst = None
    files = []  # ordered-unique files edited/written
    commands = []  # recent bash commands
    errors = []  # error-ish tool_result snippets
    for ln in HL.tail_lines(tpath, max_bytes=524288):
        ln = ln.strip()
        if not ln:
            continue
        try:
            o = json.loads(ln)
        except Exception:
            continue
        if o.get("isSidechain"):
            continue
        t = o.get("type")
        msg = o.get("message") or {}
        c = msg.get("content")
        if t == "user":

            def _real_prompt(s):
                # ignore harness-injected messages, not genuine user turns
                return s and not re.search(
                    r"<task-notification>|SYSTEM NOTIFICATION|<system-reminder>", s
                )

            if isinstance(c, str) and _real_prompt(c.strip()):
                last_user = c.strip()
            elif isinstance(c, list):
                for b in c:
                    if not isinstance(b, dict):
                        continue
                    if b.get("type") == "text" and _real_prompt(
                        b.get("text", "").strip()
                    ):
                        last_user = b["text"].strip()
                    elif b.get("type") == "tool_result" and b.get("is_error"):
                        # only the harness's own failure flag — reading a file that merely
                        # contains the word "error" is not an unresolved error
                        rc = b.get("content")
                        txt = (
                            rc
                            if isinstance(rc, str)
                            else (
                                " ".join(
                                    x.get("text", "") for x in rc if isinstance(x, dict)
                                )
                                if isinstance(rc, list)
                                else ""
                            )
                        )
                        s = re.sub(r"\s+", " ", txt).strip()
                        if s:
                            errors.append(s[:200])
        elif t == "assistant" and isinstance(c, list):
            texts = []
            for b in c:
                if not isinstance(b, dict):
                    continue
                if b.get("type") == "text" and b.get("text", "").strip():
                    texts.append(b["text"].strip())
                elif b.get("type") == "tool_use":
                    name = b.get("name", "")
                    inp = b.get("input") or {}
                    if name in ("Edit", "Write", "NotebookEdit", "MultiEdit"):
                        fp = inp.get("file_path") or inp.get("notebook_path")
                        if fp and fp not in files:
                            files.append(fp)
                    elif name == "Bash":
                        cmd = (inp.get("command") or "").strip()
                        if cmd:
                            commands.append(re.sub(r"\s+", " ", cmd)[:160])
            if texts:
                last_asst = "\n".join(texts)

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
