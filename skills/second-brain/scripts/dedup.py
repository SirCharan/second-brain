#!/usr/bin/env python3
"""/second-brain dedup — deterministic near-duplicate finder. Stdlib only.

Scans curated notes and prints pairs whose title+description are near-duplicates
(character-trigram Jaccard, boosted when they share tags). Read-only: it only
proposes merge candidates for `reconcile`/`prune` to act on — it never edits.

Usage:
  dedup.py [--threshold 0.55] [--folder NAME]
  dedup.py --selftest        # build a temp vault, assert a known dup is found

Each candidate suggests merging the OLDER note into the newer (by last_confirmed /
asserted), since the newer note holds the fresher facts."""

import os, re, sys, glob, argparse, itertools

# locate _hooklib in either install mode (same shim as export.py)
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
try:
    import _hooklib as HL

    MEM = HL.MEM
except Exception:
    MEM = os.environ.get("CLAUDE_MEMORY_DIR") or os.path.expanduser(
        "~/.claude/second-brain-vault"
    )

SKIP_FOLDERS = ("Daily", "Weekly", "Sessions", "_system")
EXCLUDE = {"MEMORY.md", "context.md", "_session-log.md"}


def _trigrams(s):
    s = re.sub(r"\s+", " ", re.sub(r"[^a-z0-9 ]", "", (s or "").lower())).strip()
    return (
        {s[i : i + 3] for i in range(len(s) - 2)}
        if len(s) >= 3
        else {s}
        if s
        else set()
    )


def _date_key(s):
    m = re.search(r"(\d{4})-(\d{2})-(\d{2})", s or "")
    return m.group(0) if m else ""


def _parse(path):
    """Return {name, folder, title, desc, tags:set, date, tri:set} or None."""
    try:
        head = open(path, errors="ignore").read(6144)
    except Exception:
        return None
    fm = {}
    m = re.match(r"^---\n(.*?)\n---", head, re.S)
    if m:
        for line in m.group(1).splitlines():
            km = re.match(r"^(\w[\w.]*):\s*(.*)$", line)
            if km:
                fm[km.group(1)] = km.group(2).strip()
    name = fm.get("name") or os.path.splitext(os.path.basename(path))[0]
    title = fm.get("title", "").strip("\"'") or name
    desc = fm.get("description", "").strip("\"'")
    tags = {
        t.strip().strip("\"'")
        for t in fm.get("tags", "").strip("[]").split(",")
        if t.strip()
    }
    date = _date_key(fm.get("last_confirmed") or fm.get("asserted") or "")
    return {
        "name": name,
        "folder": os.path.basename(os.path.dirname(path)),
        "title": title,
        "desc": desc,
        "tags": tags,
        "date": date,
        "tri": _trigrams(title + " " + desc),
    }


def _jaccard(a, b):
    if not a or not b:
        return 0.0
    inter = len(a & b)
    return inter / len(a | b) if inter else 0.0


def find_dups(mem, threshold=0.55, only=None):
    notes = []
    for p in glob.glob(os.path.join(mem, "*", "*.md")):
        b = os.path.basename(p)
        if b in EXCLUDE or b.startswith("_"):
            continue
        folder = os.path.basename(os.path.dirname(p))
        if folder in SKIP_FOLDERS or (only and folder != only):
            continue
        n = _parse(p)
        if n and n["tri"]:
            notes.append(n)

    pairs = []
    for a, b in itertools.combinations(notes, 2):
        j = _jaccard(a["tri"], b["tri"])
        # shared-tag boost (ignore the generic project/type buckets), capped at +0.15
        shared = {
            t
            for t in (a["tags"] & b["tags"])
            if not t.startswith(("project/", "type/"))
        }
        score = j + min(0.05 * len(shared), 0.15)
        if score >= threshold:
            older, newer = sorted([a, b], key=lambda n: n["date"])
            pairs.append((score, j, older, newer))
    pairs.sort(key=lambda t: t[0], reverse=True)
    return pairs


def main(argv=None):
    ap = argparse.ArgumentParser(
        description="Find near-duplicate vault notes (read-only)."
    )
    ap.add_argument(
        "--threshold", type=float, default=0.55, help="min score (default 0.55)"
    )
    ap.add_argument("--folder", help="restrict to one project folder")
    ap.add_argument(
        "--selftest", action="store_true", help="run the built-in self-check"
    )
    args = ap.parse_args(argv)

    if args.selftest:
        return _selftest()

    if not os.path.isdir(MEM):
        sys.stderr.write("no vault at %s\n" % MEM)
        sys.exit(1)

    pairs = find_dups(MEM, args.threshold, args.folder)
    if not pairs:
        print("No near-duplicate pairs at threshold %.2f." % args.threshold)
        return
    print(
        "Near-duplicate merge candidates (score ≥ %.2f) — merge OLDER into newer:\n"
        % args.threshold
    )
    for score, j, older, newer in pairs:
        print(
            "• %.2f  [[%s]] (%s) → merge into [[%s]] (%s)"
            % (score, older["name"], older["folder"], newer["name"], newer["folder"])
        )
        print(
            "        title/desc trigram-Jaccard %.2f%s"
            % (j, "  +shared tags" if score > j + 1e-9 else "")
        )
    print(
        "\n%d candidate pair(s). Review with `/second-brain reconcile`; nothing was changed."
        % len(pairs)
    )


def _selftest():
    import tempfile

    d = tempfile.mkdtemp(prefix="sb-dedup-test-")
    os.makedirs(os.path.join(d, "proj"))
    open(os.path.join(d, "proj", "a.md"), "w").write(
        "---\nname: a\ntitle: Drishti signal cadence\n"
        "description: Drishti runs a five minute signal cadence cycle.\n"
        "tags: [signals, project/drishti]\nlast_confirmed: 2026-01-01\nstatus: active\n---\n# A\n"
    )
    open(os.path.join(d, "proj", "b.md"), "w").write(
        "---\nname: b\ntitle: Drishti signal cadence\n"
        "description: Drishti runs a 5 minute signal cadence cycle.\n"
        "tags: [signals, project/drishti]\nlast_confirmed: 2026-06-01\nstatus: active\n---\n# B\n"
    )
    open(os.path.join(d, "proj", "c.md"), "w").write(
        "---\nname: c\ntitle: Vercel deploy token\n"
        "description: Ship ck-delta projects with vercel --prod from web dir.\n"
        "tags: [tooling]\nlast_confirmed: 2026-03-01\nstatus: active\n---\n# C\n"
    )
    pairs = find_dups(d, threshold=0.55)
    assert pairs, "expected the a/b near-dup to be found"
    names = {pairs[0][2]["name"], pairs[0][3]["name"]}
    assert names == {"a", "b"}, "wrong top pair: %r" % names
    # older (2026-01-01) suggested as the merge-away note
    assert pairs[0][2]["name"] == "a", "older note should be the merge source"
    print("ok — dedup selftest passed (found a/b, oldest-first)")


if __name__ == "__main__":
    main()
