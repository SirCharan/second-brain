#!/usr/bin/env python3
"""Grep-based hybrid search over memory notes. Usage: find.py <query terms...>
Scores name(3) + description(2) + body(1) hits; prints top matches."""
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
terms = [t.lower() for t in sys.argv[1:] if t.strip()]
if not terms:
    print("usage: find.py <query>"); sys.exit(0)
rows=[]
for p in glob.glob(os.path.join(MEM,"**","*.md"),recursive=True):
    b=os.path.basename(p)
    if b in ("MEMORY.md","context.md","_session-log.md") or "/Daily/" in p: continue
    txt=open(p,errors="ignore").read(); low=txt.lower()
    name=os.path.splitext(b)[0]
    m=re.search(r'^description:\s*(.+)$',txt[:600],re.M); desc=(m.group(1).strip().strip('"\'') if m else "")
    score=0
    for t in terms:
        score += 3*name.lower().count(t) + 2*desc.lower().count(t) + low.count(t)
    if score>0:
        rows.append((score,name,os.path.basename(os.path.dirname(p)),desc[:90]))
rows.sort(reverse=True)
if not rows: print("no matches for:", " ".join(terms)); sys.exit(0)
for s,n,f,d in rows[:12]:
    print(f"[{s:>3}] [[{n}]] ({f})" + (f" — {d}" if d else ""))
