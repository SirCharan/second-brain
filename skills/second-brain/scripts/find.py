#!/usr/bin/env python3
"""Grep-based hybrid search over memory notes. Usage: find.py <query terms...>
Scores name(3) + description(2) + body(1) hits; prints top matches."""
import os, re, glob, sys
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
