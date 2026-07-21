#!/usr/bin/env python3
"""PostToolUse(Edit|Write) hook: warn (never block) on memory-note hygiene issues —
missing frontmatter, unresolved [[wikilinks]], or an orphan (no outbound links).
Prints a short warning to stdout only when something's off; silent otherwise. Exit 0 always."""

import sys, os, json, re, glob

import _hooklib as HL

MEM = HL.MEM
# Structural link targets that intentionally have no note file, plus any
# user-declared ones from config.json "ignore_names".
KNOWN_DANGLERS = {
    "wikilink",
    "wikilinks",
    "MEMORY",
    "context",
    "_session-log",
    "_Home",
} | set(HL.CONFIG.get("ignore_names", []))


def main():
    if not HL.vault_ok():
        return
    try:
        hook = json.loads(sys.stdin.read())
    except Exception:
        return
    fp = (hook.get("tool_input") or {}).get("file_path", "")
    if not fp or not fp.endswith(".md"):
        return
    rp = os.path.realpath(fp)
    if not rp.startswith(os.path.realpath(MEM)):
        return
    b = os.path.basename(rp)
    if b in ("MEMORY.md", "context.md", "_session-log.md") or "/Daily/" in rp:
        return
    if not os.path.exists(rp):
        return

    txt = open(rp, errors="ignore").read()
    warns = []
    if not txt.startswith("---\n") or txt.find("\n---", 4) == -1:
        warns.append("no YAML frontmatter")
    existing = {
        os.path.splitext(os.path.basename(p))[0]
        for p in glob.glob(os.path.join(MEM, "**", "*.md"), recursive=True)
    }
    links = [t.strip() for t in re.findall(r"\[\[([^\]|#]+)", txt)]
    broken = sorted({l for l in links if l not in existing and l not in KNOWN_DANGLERS})
    if broken:
        warns.append(
            "unresolved wikilinks: " + ", ".join(f"[[{x}]]" for x in broken[:5])
        )
    if not links:
        warns.append(
            "orphan note (no outbound [[links]] — link it to its _MOC or a hub)"
        )

    if warns:
        print(f"⚠️ memory-lint ({b}): " + "; ".join(warns))
        print(
            "  (warning only — nothing blocked. Fix frontmatter/links to keep the graph clean.)"
        )


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        HL.log_err("memory-lint", e)
