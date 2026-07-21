#!/usr/bin/env python3
"""/second-brain graph — emit a Mermaid link-graph of the vault ([[wikilink]] edges).

Usage:
  graph.py [--out PATH] [--folder NAME] [--min-degree N]

No args → prints a ```mermaid fenced block to stdout (paste into Obsidian / any Markdown).
Nodes = notes; edges = [[wikilinks]]. Orphans (degree 0) are dropped unless --min-degree 0.
Stdlib-only. Never raises on a bad note."""

import os, re, sys, glob

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

SKIP_DIRS = ("Daily", "Weekly", "Sessions")


def _arg(flag, default=None):
    if flag in sys.argv:
        i = sys.argv.index(flag)
        return sys.argv[i + 1] if i + 1 < len(sys.argv) else default
    return default


def note_name(path):
    try:
        raw = open(path, errors="ignore").read(600)
    except Exception:
        return None
    m = re.search(r"^name:\s*(.+)$", raw, re.M)
    return m.group(1).strip() if m else os.path.splitext(os.path.basename(path))[0]


def sanitize(n):
    """Mermaid node id — alnum/underscore only."""
    return "n_" + re.sub(r"[^A-Za-z0-9]", "_", n)


def main():
    out = _arg("--out")
    only = _arg("--folder")
    min_degree = int(_arg("--min-degree", "1"))

    if not os.path.isdir(MEM):
        sys.stderr.write(f"no vault at {MEM}\n")
        sys.exit(1)

    edges, labels, degree = [], {}, {}
    seen = set()
    for path in glob.glob(os.path.join(MEM, "**", "*.md"), recursive=True):
        rel = os.path.relpath(path, MEM)
        top = rel.split(os.sep)[0] if os.sep in rel else ""
        if top in SKIP_DIRS:
            continue
        if only and top != only:
            continue
        src = note_name(path)
        if not src:
            continue
        labels[src] = src
        try:
            body = open(path, errors="ignore").read()
        except Exception:
            continue
        for tgt in re.findall(r"\[\[([^\]|#]+)", body):
            tgt = tgt.strip()
            if not tgt or tgt == src:
                continue
            key = (src, tgt)
            if key in seen:
                continue
            seen.add(key)
            edges.append(key)
            labels.setdefault(tgt, tgt)
            degree[src] = degree.get(src, 0) + 1
            degree[tgt] = degree.get(tgt, 0) + 1

    kept = {n for n in labels if degree.get(n, 0) >= min_degree}
    kept_edges = [(a, b) for a, b in edges if a in kept and b in kept]

    lines = ["```mermaid", "graph LR"]
    for a, b in kept_edges:
        lines.append(f"  {sanitize(a)}[{a}] --> {sanitize(b)}[{b}]")
    if not kept_edges:
        lines.append("  empty[no linked notes yet]")
    lines.append("```")
    text = "\n".join(lines) + "\n"

    if out:
        with open(out, "w") as f:
            f.write(text)
        sys.stderr.write(
            f"graph → {out} ({len(kept)} nodes, {len(kept_edges)} edges)\n"
        )
    else:
        sys.stdout.write(text)


if __name__ == "__main__":
    main()
