#!/usr/bin/env python3
"""The note walk, an mtime-keyed index, and the one keyword ranker. Pure stdlib.

Three callers share this: the memory-recall hook, the MCP tool layer, and the eval
harness. Two copies of the scoring loop existed before and had already drifted —
mcp/sb_core.py globbed a single directory level, so root-level notes and nested
folders were invisible to Claude Desktop and Cursor, and it skipped the head gate.

The index exists because recall runs on every prompt. Without it every prompt opened
and read every note in the vault. Measured on a warm page cache: 489 notes cost
~630ms and 1000 notes ~720ms, on every single prompt, growing linearly — so a vault
in the tens of thousands would approach the hook timeout, and a hook that times out
is skipped with no error. Entries are keyed by (mtime, size), so a warm index
re-reads only the notes that actually changed: 47ms at 1000 notes.
"""

import os, re, glob, time, hashlib

import _hooklib as HL

import sys
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
    os.environ["SB_UTF8_REEXEC"] = "1"
    try:
        os.execv(
            sys.executable,
            [sys.executable, "-X", "utf8", os.path.abspath(__file__), *sys.argv[1:]],
        )
    except Exception:
        pass  # fall through to the stream guard below rather than refusing to run
for _stream in (sys.stdout, sys.stderr):
    if hasattr(_stream, "reconfigure"):
        try:
            _stream.reconfigure(encoding="utf-8", errors="replace")
        except Exception:
            pass

INDEX_V = 1  # bump to invalidate every cached entry after a parse change


def _mem():
    """The vault path, resolved per call rather than cached at import. Callers reload
    _hooklib to point at a different vault (the test suites and the MCP tool layer both
    do), and a module-level copy would silently keep ranking the first one."""
    return HL.MEM


def index_path():
    """One index per vault. The keys are vault-relative, so a shared file would let two
    vaults overwrite each other's entries wherever a relative path happened to match."""
    tag = hashlib.sha1(os.path.realpath(_mem()).encode()).hexdigest()[:10]
    return os.path.join(HL.STATE_DIR, "note-index-%s.json" % tag)


EXCLUDE = {"MEMORY.md", "context.md", "_session-log.md"}
SKIP_DIRS = ("Daily", "Weekly", "_system", "Sessions")
RETIRED = ("retired", "deprecated", "archived", "superseded")
STOP = set(
    "the a an and or of to in on for with is are was were be been this that these those i you "
    "it we they he she how what why when where which who do does did can could should would will "
    "just now then here there my your our their its from into out up down over about as at by so "
    "if not no yes ok okay thanks please help make add use using get got need want like also more "
    "most some any all one two new old via per etc pls better stronger strong full work works".split()
)

# How many DISTINCT query keywords must appear in a note's name or description before
# the note is scored at all. This gate kills generic-prompt noise, but it is also a
# hard recall ceiling: a note whose body answers the question perfectly is unreachable
# when its name and description share fewer than this many words with the prompt.
# Removing it requires a rerank stage in front — measure with tests/eval first.
HEAD_GATE = 2

HEAD_BYTES = 6144  # per-note read cap on the hot path; covers most bodies


def words(s):
    return set(re.findall(r"[a-z0-9]{3,}", s.lower()))


def keywords(query):
    """Content words of a query — what the ranker actually matches on."""
    return {w for w in words(query) if w not in STOP}


def folder_of(p):
    """Top-level folder of a note; '' for a note at the vault root."""
    rel = os.path.relpath(p, _mem())
    return rel.split(os.sep)[0] if os.sep in rel else ""


def is_note(p):
    """A real curated note — excludes index/meta files, journals, backups and dot-dirs.
    Works at ANY depth, so root-level notes and nested folders both count."""
    rel = os.path.relpath(p, _mem())
    parts = rel.split(os.sep)
    b = parts[-1]
    if b in EXCLUDE or b.startswith("_") or b.startswith("."):
        return False
    for d in parts[:-1]:
        if d in SKIP_DIRS or d.startswith("_backup") or d.startswith("."):
            return False
    return True


def all_notes():
    """Every curated note in the vault, any depth (root-level included)."""
    return [
        p
        for p in glob.glob(os.path.join(_mem(), "**", "*.md"), recursive=True)
        if is_note(p)
    ]


def _date_in(head):
    """`last_confirmed` (preferred) or `asserted` as YYYY-MM-DD, else None. Tolerates
    both flat v2 (`asserted:`) and nested (`  asserted:` under `metadata:`)."""
    for key in ("last_confirmed", "asserted"):
        m = re.search(r"^\s*" + key + r":\s*([0-9]{4}-[0-9]{2}-[0-9]{2})", head, re.M)
        if m:
            return m.group(1)
    return None


def age_days(date_str):
    """Age of a YYYY-MM-DD string in days; None when absent or unparseable.
    Computed per query, never cached — otherwise freshness decay freezes on disk."""
    if not date_str:
        return None
    try:
        t = time.mktime(time.strptime(date_str, "%Y-%m-%d"))
        return (time.time() - t) / 86400.0
    except Exception:
        return None


def _parse(path):
    """Read one note's head and derive everything the ranker needs. None on failure."""
    try:
        head = open(path, errors="ignore").read(HEAD_BYTES)
    except Exception:
        return None
    m = re.search(r"^description:\s*(.+)$", head, re.M)
    desc = (m.group(1).strip().strip("\"'")) if m else ""
    sm = re.search(r"^\s*status:\s*(.+)$", head, re.M)
    status = (sm.group(1).strip().strip("\"'").lower()) if sm else ""
    return {
        "d": desc,
        "st": status,
        "dt": _date_in(head),
        # Every token in the head, frontmatter included — matches what the shipped
        # ranker matched on, so an index refresh cannot shift scores by itself.
        "bw": sorted(words(head)),
    }


def entries():
    """[(abs_path, entry)] for every note, refreshing changed ones and persisting the
    index when anything moved. Never raises — a broken index degrades to a full re-read."""
    path = index_path()
    try:
        idx = HL.read_json(path, {}) or {}
    except Exception:
        idx = {}
    if idx.get("v") != INDEX_V or not isinstance(idx.get("notes"), dict):
        idx = {"v": INDEX_V, "notes": {}}
    notes = idx["notes"]

    mem = _mem()
    out, live, dirty = [], set(), False
    for p in all_notes():
        rel = os.path.relpath(p, mem)
        live.add(rel)
        try:
            st = os.stat(p)
        except OSError:
            continue
        e = notes.get(rel)
        if (
            not isinstance(e, dict)
            or e.get("m") != st.st_mtime
            or e.get("s") != st.st_size
        ):
            parsed = _parse(p)
            if parsed is None:
                continue
            e = dict(parsed, m=st.st_mtime, s=st.st_size)
            notes[rel] = e
            dirty = True
        out.append((p, e))

    stale = [r for r in notes if r not in live]  # notes deleted since the last run
    if stale:
        for r in stale:
            del notes[r]
        dirty = True
    if dirty:
        try:
            HL.write_json(path, idx)
        except Exception as ex:
            HL.log_err("sb_rank.index", ex)
    return out


def rank(query, project=None, limit=4, head_gate=HEAD_GATE):
    """Decay-aware keyword ranking over curated notes, best first.

    Returns [{name, folder, description, score, path}]. Scoring, the project bias, the
    freshness decay and the tie-break are all preserved exactly as the memory-recall
    hook shipped them, so tests/eval measures the real system rather than a variant.
    """
    kw = keywords(query)
    if not kw:
        return []
    rows = []
    for p, e in entries():
        if e["st"] in RETIRED:
            continue  # never auto-inject facts that were explicitly retired
        name = os.path.splitext(os.path.basename(p))[0]
        folder = folder_of(p)
        hit_name = kw & words(name)
        hit_desc = kw & words(e["d"])
        if len(hit_name | hit_desc) < head_gate:
            continue
        body_extra = (kw & set(e["bw"])) - hit_name - hit_desc
        score = 5 * len(hit_name) + 3 * len(hit_desc) + len(body_extra)
        if project and folder == project:
            score = int(score * 1.5)
        age = age_days(e["dt"])
        if age is not None:
            if age <= 30:
                score = int(score * 1.25)
            elif age > 365:
                score = int(score * 0.6)
            elif age > 180:
                score = int(score * 0.8)
        rows.append(
            {
                "name": name,
                "folder": folder,
                "description": e["d"][:150],
                "score": score,
                "path": p,
            }
        )
    # (score, name) descending — the shipped tie-break was reverse-alphabetical by
    # name. Arbitrary, but kept so the eval baseline reflects what actually ran.
    rows.sort(key=lambda r: (r["score"], r["name"]), reverse=True)
    return rows[:limit] if limit else rows
