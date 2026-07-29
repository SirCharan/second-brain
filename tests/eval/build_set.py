#!/usr/bin/env python3
"""Mine a recall eval set out of a vault's own capture journal. Pure stdlib.

    python3 tests/eval/build_set.py [-o out.jsonl] [--min-keywords 3]

Every capture footer records a one-line summary of what a session did plus the notes
it was about:

    - **17:31** [widgets] — (decision) Shipped the cache rewrite || tags: ... || links: [[widgets-cache]]

That is a labelled retrieval pair nobody had to hand-label: the summary is a real
query in the user's own words, written at a different time and in different words
from the note it points at, and the links are ground truth. Paraphrase-to-note is
also the case recall actually has to serve — a new prompt about a topic should
surface that topic's note.

The output is YOUR vault's prose, so it is git-ignored by default. Do not commit a
mined set to a public repo; commit the miner instead.
"""

import argparse, glob, json, os, re, sys

_HOOKS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "hooks")
sys.path.insert(0, os.path.abspath(_HOOKS))
import sb_rank  # noqa: E402

# - **HH:MM** [project] — (type) summary text || tags: ... || links: [[a]] [[b]]
LINE = re.compile(r"^-\s+\*\*\d{1,2}:\d{2}\*\*\s*(?:\[([^\]]*)\])?\s*[—-]\s*(.*)$")
JUNK = re.compile(r"\(raw\)|\[Image:|^\s*$")


def _summary(rest):
    """The prose half of a capture line: everything before the first `||` metadata
    field, with a leading `(type)` marker stripped."""
    text = rest.split("||")[0].strip()
    return re.sub(
        r"^\((?:decision|win|incident|context|research|learning|milestone)\)\s*",
        "",
        text,
    ).strip()


def mine(mem, min_keywords=3):
    """[{q, expect, project, day}] — one row per usable capture line, deduped."""
    rankable = {os.path.splitext(os.path.basename(p))[0] for p in sb_rank.all_notes()}
    rows, seen_q = [], set()
    for day in sorted(glob.glob(os.path.join(mem, "Daily", "*.md"))):
        for raw in open(day, errors="ignore"):
            m = LINE.match(raw.rstrip())
            if not m:
                continue
            project, rest = (m.group(1) or "").strip(), m.group(2)
            if JUNK.search(rest):
                continue
            links = re.findall(r"\[\[([^\]|#]+)", rest)
            if not links:
                continue  # no ground truth on this line
            q = _summary(rest)
            # The hook stays silent below 3 content words, so those queries never
            # reach recall in practice and measuring them would flatter the score.
            if len(sb_rank.keywords(q)) < min_keywords:
                continue
            # Only keep links the ranker could actually return. `_index-*` and `_MOC-*`
            # are meta files the walk excludes by design, so a query pointing only at
            # those is unanswerable and would depress the score for the wrong reason.
            expect = sorted({l.strip() for l in links if l.strip() in rankable})
            if not expect:
                continue
            key = q.lower()
            if key in seen_q:
                continue  # the same summary is often captured twice a minute apart
            seen_q.add(key)
            rows.append(
                {
                    "q": q,
                    "expect": expect,
                    "project": project or None,
                    "day": os.path.splitext(os.path.basename(day))[0],
                }
            )
    return rows


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument(
        "-o", "--out", default=None, help="write JSONL here (default: stdout)"
    )
    ap.add_argument("--min-keywords", type=int, default=3)
    a = ap.parse_args()

    mem = sb_rank._mem()
    if not os.path.isdir(mem):
        sys.exit("no vault at %s — set CLAUDE_MEMORY_DIR" % mem)
    rows = mine(mem, a.min_keywords)
    if not rows:
        sys.exit(
            "no labelled capture lines found in %s/Daily.\n"
            "The miner needs capture footers that carry `links: [[note]]`." % mem
        )
    text = "".join(json.dumps(r, ensure_ascii=False) + "\n" for r in rows)
    if a.out:
        os.makedirs(os.path.dirname(os.path.abspath(a.out)), exist_ok=True)
        with open(a.out, "w") as f:
            f.write(text)
        multi = sum(1 for r in rows if len(r["expect"]) > 1)
        print(
            "%d queries -> %s  (%d with multiple expected notes)"
            % (len(rows), a.out, multi)
        )
    else:
        sys.stdout.write(text)


if __name__ == "__main__":
    main()
