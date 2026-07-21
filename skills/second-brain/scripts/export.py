#!/usr/bin/env python3
"""/second-brain export — flatten the vault into ONE portable context file any assistant
can read. This is the "one brain feeds every model" primitive: hand the output to ChatGPT,
Gemini, Grok, a fresh Claude, or drop it in an AGENTS.md.

Usage:
  export.py [--format claude|chatgpt|agents-md] [--out PATH] [--include-daily] [--folder NAME]

Default: curated notes only (skips Daily/Weekly/Sessions journals + _infra internals),
grouped by folder, newest-confirmed first, frontmatter stripped to a one-line meta.
No args → prints to stdout. Stdlib-only. Never raises on a bad note (skips it)."""

import os, re, sys, glob

# locate _hooklib in either install mode
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

SKIP_DIRS = ("Daily", "Weekly", "Sessions", "_infra", "_system")
SKIP_NAMES = ("MEMORY.md", "context.md", "_session-log.md")


def _arg(flag, default=None):
    if flag in sys.argv:
        i = sys.argv.index(flag)
        return sys.argv[i + 1] if i + 1 < len(sys.argv) else default
    return default


def parse_note(path):
    """Return (name, title, meta_line, body) with frontmatter stripped. None on failure."""
    try:
        raw = open(path, errors="ignore").read()
    except Exception:
        return None
    fm, body = {}, raw
    m = re.match(r"^---\n(.*?)\n---\n(.*)$", raw, re.S)
    if m:
        body = m.group(2)
        for line in m.group(1).splitlines():
            km = re.match(r"^(\w[\w.]*):\s*(.*)$", line)
            if km:
                fm[km.group(1)] = km.group(2).strip()
    name = fm.get("name") or os.path.splitext(os.path.basename(path))[0]
    title = fm.get("title") or name
    # first H1 as title if present
    h1 = re.search(r"^#\s+(.+)$", body, re.M)
    if h1:
        title = h1.group(1).strip()
    bits = []
    if fm.get("status"):
        bits.append(fm["status"])
    if fm.get("tags"):
        bits.append(fm["tags"].strip("[]"))
    if fm.get("last_confirmed") or fm.get("asserted"):
        bits.append("confirmed " + (fm.get("last_confirmed") or fm.get("asserted")))
    meta = " · ".join(b for b in bits if b)
    # strip the leading H1 + status chip line from body (we render our own header)
    body = re.sub(r"^#\s+.+\n", "", body.strip(), count=1).lstrip()
    body = re.sub(
        r"^\S*\s*\*\*(active|watch|retired|real-money)\*\*.*\n", "", body, count=1
    ).lstrip()
    return name, title, meta, body, fm.get("last_confirmed") or fm.get("asserted") or ""


def main():
    fmt = _arg("--format", "claude")
    out = _arg("--out")
    only = _arg("--folder")
    include_daily = "--include-daily" in sys.argv

    if not os.path.isdir(MEM):
        sys.stderr.write(f"no vault at {MEM}\n")
        sys.exit(1)

    notes = []
    for path in glob.glob(os.path.join(MEM, "**", "*.md"), recursive=True):
        rel = os.path.relpath(path, MEM)
        top = rel.split(os.sep)[0] if os.sep in rel else ""
        if os.path.basename(path) in SKIP_NAMES:
            continue
        if not include_daily and top in SKIP_DIRS:
            continue
        if only and top != only:
            continue
        p = parse_note(path)
        if p:
            notes.append((top or ".", p))

    # group by folder; within a folder, newest-confirmed first
    notes.sort(key=lambda t: (t[0], t[1][4]), reverse=False)
    from collections import OrderedDict

    by_folder = OrderedDict()
    for folder, p in sorted(notes, key=lambda t: (t[0].lower(), -_date_key(t[1][4]))):
        by_folder.setdefault(folder, []).append(p)

    headers = {
        "claude": "# second-brain — memory export\n\nPortable snapshot of a local-first Markdown memory vault (github.com/SirCharan/second-brain). Treat every note below as durable context about the user and their projects. Newest-confirmed facts win.\n",
        "chatgpt": "# My memory (second-brain export)\n\nThis is my accumulated context, exported from a local Markdown vault. Use it as background knowledge about me and my work; ask before assuming anything not written here.\n",
        "agents-md": "# AGENTS.md — memory context (second-brain export)\n\nDurable project + user context for any coding agent. Generated from a local Markdown vault; do not edit here (edit the vault).\n",
    }
    lines = [
        headers.get(fmt, headers["claude"]),
        f"_Exported {_today()} · {len(notes)} notes._\n",
    ]
    for folder, ps in by_folder.items():
        lines.append(f"\n---\n\n## 📁 {folder}\n")
        for name, title, meta, body, _c in ps:
            lines.append(f"### {title}")
            if meta:
                lines.append(f"`{meta}`\n")
            lines.append(body + "\n")

    text = "\n".join(lines).rstrip() + "\n"
    if out:
        with open(out, "w") as f:
            f.write(text)
        sys.stderr.write(f"exported {len(notes)} notes → {out} ({len(text)} bytes)\n")
    else:
        sys.stdout.write(text)


def _date_key(s):
    m = re.search(r"(\d{4})-(\d{2})-(\d{2})", s or "")
    return int(m.group(1) + m.group(2) + m.group(3)) if m else 0


def _today():
    # deterministic-ish; fine for a manual export
    import datetime

    return datetime.date.today().isoformat()


if __name__ == "__main__":
    main()
