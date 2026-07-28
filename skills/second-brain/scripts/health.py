#!/usr/bin/env python3
"""Audit the memory vault: counts, missing v2 fields, broken wikilinks, orphans, stale, retired."""

import os, re, glob, sys
from datetime import datetime, date

MEM = os.environ.get("CLAUDE_MEMORY_DIR") or os.path.expanduser(
    "~/.claude/second-brain-vault"
)


def _cfg():
    import json

    try:
        with open(os.path.join(MEM, "config.json"), errors="ignore") as f:
            c = json.load(f)
            return c if isinstance(c, dict) else {}
    except Exception:
        return {}


KNOWN = {"wikilink", "wikilinks"} | set(_cfg().get("ignore_names", []))
STALE_DAYS = 120
# Note-size discipline: atomic notes target <=4KB (one concept, injectable whole by
# recall); >8KB is a hard split gate. MOC/index/_Home files are exempt (excluded below).
SPLIT_TARGET = 4096
SPLIT_GATE = 8192
notes = [
    p
    for p in glob.glob(os.path.join(MEM, "**", "*.md"), recursive=True)
    if os.path.basename(p) not in ("MEMORY.md", "context.md", "_session-log.md")
    and "/Daily/" not in p
    and "/Weekly/" not in p
    and "/_system/" not in p
    and "/Sessions/" not in p
    and "/_backup" not in p
    and not os.path.basename(p).startswith("_")
]
# Link targets = EVERY .md in the vault (hubs/indexes start with "_" and are excluded
# from the audited `notes` set above, but they are perfectly valid link targets).
existing = {
    os.path.splitext(os.path.basename(p))[0]
    for p in glob.glob(os.path.join(MEM, "**", "*.md"), recursive=True)
} | {"MEMORY", "context", "_session-log", "_Home"}


def fm(p):
    t = open(p, errors="ignore").read()
    b = {}
    if t.startswith("---\n"):
        e = t.find("\n---", 4)
        # Accept both shapes: top-level fields and the nested `metadata:` form a
        # frontmatter normalizer produces. Top-level wins on conflict.
        for m in re.finditer(r"^(\s*)([A-Za-z_]+):\s*(.*)$", t[4:e], re.M):
            key, val, nested = m.group(2), m.group(3).strip(), bool(m.group(1))
            if nested and key in b:
                continue
            b[key] = val
    return t, b


miss_fields = []
broken = {}
orphans = []
stale = []
retired = []
by_folder = {}
today = date.today()
for p in notes:
    b = os.path.basename(p)
    name = os.path.splitext(b)[0]
    # top-level folder, so <proj>/subdir/x.md counts under <proj> (matches regen-index)
    folder = os.path.relpath(p, MEM).split(os.sep)[0]
    by_folder[folder] = by_folder.get(folder, 0) + 1
    t, f = fm(p)
    for k in ("asserted", "last_confirmed", "source", "confidence", "status"):
        if k not in f:
            miss_fields.append(f"{name} (missing {k})")
            break
    links = [x.strip() for x in re.findall(r"\[\[([^\]|#]+)", t)]
    # Path-form links ([[folder/note]]) resolve on their last segment. Skip template
    # placeholders and code fragments — they are not real link targets.
    links = [l.split("/")[-1] for l in links if not re.search(r"[<>*\"',]", l)]
    bad = [l for l in links if l not in existing and l not in KNOWN]
    if bad:
        broken[name] = bad
    if not links and not name.startswith("_MOC-") and name != "_Home":
        orphans.append(name)
    if f.get("status") == "retired":
        retired.append(name)
    lc = f.get("last_confirmed", "")
    if re.match(r"\d{4}-\d{2}-\d{2}", lc) and f.get("status", "active") == "active":
        age = (today - date.fromisoformat(lc[:10])).days
        if age > STALE_DAYS:
            stale.append((age, name))
print(f"# Memory health\nnotes: {len(notes)} across {len(by_folder)} folders")
print("by folder:", ", ".join(f"{k}={v}" for k, v in sorted(by_folder.items())))
print(f"\nmissing v2 fields: {len(miss_fields)}")
[print("  -", x) for x in miss_fields[:15]]
print(f"\nbroken wikilinks: {len(broken)}")
[print(f"  - {k}: {v}") for k, v in list(broken.items())[:15]]
print(f"\norphans (no outbound links): {len(orphans)}")
[print("  -", x) for x in orphans[:15]]
print(
    f"\nstale (>{STALE_DAYS}d unconfirmed, status=active): {len(stale)} — reconfirm or /second-brain prune"
)
for a, n in sorted(stale, reverse=True)[:15]:
    print(f"  - {n} ({a}d)")
oversized = sorted(
    ((os.path.getsize(p), p) for p in notes if os.path.getsize(p) > SPLIT_GATE),
    reverse=True,
)
print(
    f"\noversized (>{SPLIT_GATE // 1024}KB hard gate; atomic target "
    f"{SPLIT_TARGET // 1024}KB): {len(oversized)} — split and link, never append-forever"
)
for sz, p in oversized[:20]:
    print(f"  - {os.path.relpath(p, MEM)} ({sz // 1024}KB)")
print(f"\nretired (kept, not deleted): {len(retired)}")
