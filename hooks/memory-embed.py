#!/usr/bin/env python3
"""Semantic index for the memory vault (workstream C).
Runs under the dedicated venv (~/.claude/hooks/.venv-embed) which has fastembed+numpy.
Stores per-note float32 embeddings in a sqlite BLOB; cosine is brute-force numpy
(fast enough for a few hundred notes, no sqlite-vec extension needed).

CLI:
  memory-embed.py build            incremental (re-embed only changed notes, prune deleted)
  memory-embed.py query "<text>" [k]   print top-k as  score\\tname\\tfolder

The recall hook shells into `query` as a guarded, timed fallback. Everything degrades
to a clean no-op if the model/deps are unavailable."""

import os, re, sys, glob, sqlite3, struct

MEM = os.environ.get("CLAUDE_MEMORY_DIR") or os.path.expanduser("~/.claude/second-brain-vault")
DB = os.path.join(MEM, ".embed", "index.db")
MODEL = "BAAI/bge-small-en-v1.5"
EXCLUDE = {"MEMORY.md", "context.md", "_session-log.md"}


# ---------------------------------------------------------------- pure helpers
def is_note(p):
    """Mirror memory-recall's note filter: real curated notes only."""
    b = os.path.basename(p)
    if b in EXCLUDE or b.startswith("_"):
        return False
    if os.path.basename(os.path.dirname(p)) in (
        "Daily",
        "Weekly",
        "_system",
        "Sessions",
    ):
        return False
    return True


def note_text(path):
    """Text to embed: name + description + a slice of the body (frontmatter stripped)."""
    name = os.path.splitext(os.path.basename(path))[0]
    try:
        raw = open(path, errors="ignore").read()
    except Exception:
        return name
    body = re.sub(r"^---\n.*?\n---\n", "", raw, count=1, flags=re.S)
    m = re.search(r"^\s*description:\s*(.+)$", raw, re.M)
    desc = m.group(1).strip().strip("\"'") if m else ""
    return (name.replace("-", " ") + ". " + desc + ". " + body)[:2500]


def pack_vec(vec):
    return struct.pack("%sf" % len(vec), *vec)


def unpack_vec(blob):
    return list(struct.unpack("%sf" % (len(blob) // 4), blob))


def cosine(a, b):
    import numpy as np

    a, b = np.asarray(a, "f4"), np.asarray(b, "f4")
    na, nb = np.linalg.norm(a), np.linalg.norm(b)
    if na == 0 or nb == 0:
        return 0.0
    return float(a.dot(b) / (na * nb))


# ---------------------------------------------------------------- db
def _connect():
    os.makedirs(os.path.dirname(DB), exist_ok=True)
    db = sqlite3.connect(DB)
    db.execute(
        "CREATE TABLE IF NOT EXISTS notes"
        "(path TEXT PRIMARY KEY, name TEXT, folder TEXT, mtime REAL, vec BLOB)"
    )
    return db


_MODEL_CACHE = []


def _embed(texts):
    """Embed a list of strings -> list of float lists. Loads the model once."""
    if not _MODEL_CACHE:
        from fastembed import TextEmbedding

        _MODEL_CACHE.append(TextEmbedding(model_name=MODEL))
    return [list(v) for v in _MODEL_CACHE[0].embed(texts)]


# ---------------------------------------------------------------- commands
def build():
    db = _connect()
    have = {r[0]: r[1] for r in db.execute("SELECT path, mtime FROM notes")}
    on_disk = [p for p in glob.glob(os.path.join(MEM, "*", "*.md")) if is_note(p)]
    disk_set = set(on_disk)
    # prune deleted
    for gone in set(have) - disk_set:
        db.execute("DELETE FROM notes WHERE path=?", (gone,))
    # find changed/new
    todo = [p for p in on_disk if abs(have.get(p, -1) - os.path.getmtime(p)) > 1e-6]
    if todo:
        vecs = _embed([note_text(p) for p in todo])
        for p, v in zip(todo, vecs):
            db.execute(
                "INSERT OR REPLACE INTO notes VALUES (?,?,?,?,?)",
                (
                    p,
                    os.path.splitext(os.path.basename(p))[0],
                    os.path.basename(os.path.dirname(p)),
                    os.path.getmtime(p),
                    pack_vec(v),
                ),
            )
    db.commit()
    print(
        f"indexed: {len(todo)} changed, {len(on_disk)} total, {len(set(have) - disk_set)} pruned"
    )


def query(text, k=6):
    if not os.path.exists(DB):
        return
    db = _connect()
    rows = db.execute("SELECT name, folder, vec FROM notes").fetchall()
    if not rows:
        return
    qv = _embed([text])[0]
    scored = sorted(
        ((cosine(qv, unpack_vec(vec)), name, folder) for name, folder, vec in rows),
        reverse=True,
    )
    for score, name, folder in scored[:k]:
        print(f"{score:.4f}\t{name}\t{folder}")


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "build"
    if cmd == "build":
        build()
    elif cmd == "query":
        query(sys.argv[2], int(sys.argv[3]) if len(sys.argv) > 3 else 6)
