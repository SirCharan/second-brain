#!/usr/bin/env python3
"""/second-brain stale — surface notes that haven't been confirmed in a while.

The recall ranker already penalizes stale notes; this makes that visible so you can
re-confirm, retire, or supersede them. Usage:

  stale.py [--days N] [--folder NAME]

Lists notes whose last_confirmed (or asserted) date is older than N days (default 180),
oldest first, with age. Skips notes already status: retired/superseded. Stdlib-only."""

import os, re, sys, glob
from datetime import date

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


def _arg(flag, default=None):
    if flag in sys.argv:
        i = sys.argv.index(flag)
        return sys.argv[i + 1] if i + 1 < len(sys.argv) else default
    return default


def _fm(path):
    try:
        raw = open(path, errors="ignore").read(1200)
    except Exception:
        return {}
    m = re.match(r"^---\n(.*?)\n---", raw, re.S)
    d = {}
    if m:
        for line in m.group(1).splitlines():
            km = re.match(r"^(\w[\w.]*):\s*(.*)$", line)
            if km:
                d[km.group(1)] = km.group(2).strip()
    return d


def main():
    days = int(_arg("--days", "180"))
    only = _arg("--folder")
    if not os.path.isdir(MEM):
        sys.stderr.write(f"no vault at {MEM}\n")
        sys.exit(1)
    today = date.today()
    rows = []
    for path in glob.glob(os.path.join(MEM, "**", "*.md"), recursive=True):
        rel = os.path.relpath(path, MEM)
        top = rel.split(os.sep)[0] if os.sep in rel else ""
        if top in SKIP_DIRS or (only and top != only):
            continue
        d = _fm(path)
        if (d.get("status") or "").lower() in (
            "retired",
            "superseded",
            "deprecated",
            "archived",
        ):
            continue
        ds = d.get("last_confirmed") or d.get("asserted") or ""
        dm = re.search(r"(\d{4})-(\d{2})-(\d{2})", ds)
        if not dm:
            continue
        try:
            age = (
                today - date(int(dm.group(1)), int(dm.group(2)), int(dm.group(3)))
            ).days
        except Exception:
            continue
        if age >= days:
            rows.append(
                (
                    age,
                    d.get("name") or os.path.splitext(os.path.basename(path))[0],
                    top or ".",
                )
            )
    rows.sort(reverse=True)
    print(f"# Stale notes — not confirmed in {days}+ days ({len(rows)} found)\n")
    if not rows:
        print("  (none — vault is fresh)")
        return
    for age, name, folder in rows:
        print(f"  {age:4d}d  [[{name}]]  · {folder}")
    print(
        "\nRe-confirm (bump last_confirmed), retire (status: retired + supersedes), or /second-brain prune."
    )


if __name__ == "__main__":
    main()
