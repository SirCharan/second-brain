#!/usr/bin/env python3
"""/second-brain pull <query> — the 'unstick' search. Grep-rank across the ENTIRE vault
(notes + Daily/ captures + _system/ skills·workflows·CLAUDE.md) and print the FULL text of
the top matches, so you get the actual answer/fix — not just a title. Bounded output."""
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
MEM = os.environ.get("CLAUDE_MEMORY_DIR") or os.path.expanduser("~/.claude/second-brain-vault")
CAP = 6000            # total chars printed
PERCAP = 2600         # per-note chars
terms = [t.lower() for t in sys.argv[1:] if t.strip()]
if not terms:
    print("usage: pull.py <query terms>"); sys.exit(0)
rows = []
for p in glob.glob(os.path.join(MEM, "**", "*.md"), recursive=True):
    b = os.path.basename(p)
    if b in ("_session-log.md",):     # skip only the raw session log
        continue
    try:
        txt = open(p, errors="ignore").read()
    except Exception:
        continue
    low = txt.lower(); name = os.path.splitext(b)[0].lower()
    score = 0
    for t in terms:
        score += 5 * name.count(t) + low.count(t)
    if score > 0:
        rel = os.path.relpath(p, MEM)
        rows.append((score, rel, txt))
if not rows:
    print("no vault matches for:", " ".join(terms)); sys.exit(0)
rows.sort(key=lambda r: r[0], reverse=True)
out, used = [], 0
for score, rel, txt in rows[:3]:
    body = txt.strip()
    if len(body) > PERCAP:
        body = body[:PERCAP] + "\n… [truncated]"
    chunk = f"\n===== {rel}  (score {score}) =====\n{body}\n"
    if used + len(chunk) > CAP:
        break
    out.append(chunk); used += len(chunk)
extra = len(rows) - len(out)
print("".join(out) + (f"\n(+{extra} more matches — narrow the query or `/second-brain find`)" if extra > 0 else ""))
