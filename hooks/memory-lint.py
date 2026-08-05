#!/usr/bin/env python3
"""PostToolUse(Edit|Write) hook: warn (never block) on memory-note hygiene issues —
missing frontmatter, unresolved [[wikilinks]], or an orphan (no outbound links).
Prints a short warning to stdout only when something's off; silent otherwise. Exit 0 always."""

import os
import sys, os, json, re, glob

import _hooklib as HL

# Windows defaults to cp1252 for console output AND for open(, encoding="utf-8"), so both printing a status
# glyph and reading a note containing an emoji raise. Interpreter UTF-8 mode fixes both, and
# can only be set at startup, so re-exec into it once when we were not started that way.
if (
    __name__ == "__main__"  # never re-exec when imported as a library
    and os.name == "nt"
    and not sys.flags.utf8_mode
    and not os.environ.get("SB_UTF8_REEXEC")
    and getattr(sys, "frozen", None) is None
):
    # os.execv does not replace the process on Windows: the parent exits immediately with
    # its own status while the child keeps running, so the caller reads the wrong exit
    # code. Re-run synchronously and pass the child's code up. stdin/stdout are inherited,
    # so a hook still receives its JSON payload.
    import subprocess

    os.environ["SB_UTF8_REEXEC"] = "1"
    try:
        sys.exit(
            subprocess.run(
                [sys.executable, "-X", "utf8", os.path.abspath(__file__), *sys.argv[1:]]
            ).returncode
        )
    except OSError:
        pass  # fall through to the stream guard rather than refusing to run
for _stream in (sys.stdout, sys.stderr):
    if hasattr(_stream, "reconfigure"):
        try:
            _stream.reconfigure(encoding="utf-8", errors="replace")
        except Exception:
            pass

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

    txt = open(rp, errors="ignore", encoding="utf-8").read()
    warns = []
    if not txt.startswith("---\n") or txt.find("\n---", 4) == -1:
        warns.append("no YAML frontmatter")
    else:
        # v2 shape. Accept BOTH the top-level and the nested `metadata:` form, since a
        # frontmatter normalizer rewrites notes into the nested one.
        fmb = txt[4 : txt.find("\n---", 4)]
        need = (
            "name",
            "title",
            "description",
            "tags",
            "asserted",
            "last_confirmed",
            "source",
            "confidence",
            "status",
        )
        gone = [k for k in need if not re.search(r"^\s*" + k + r":", fmb, re.M)]
        if gone:
            warns.append("missing v2 field(s): " + ", ".join(gone))
        body = txt[txt.find("\n---", 4) + 4 :]
        if not re.search(r"^# \S", body, re.M):
            warns.append("no `# H1` title line")
        elif not re.search(
            r"[🟢🟡⚫🔴]", body[: body.find("\n##") if "\n##" in body else 600]
        ):
            warns.append(
                "no emoji status chip (🟢 active / 🟡 watch / ⚫ retired / 🔴 real-money)"
            )
        if "## Related" not in body:
            warns.append("no `## Related` section (link its `_MOC-` hub)")
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
    # size gate: atomic notes target <=4KB; >8KB must be split (MOC/index/hub exempt)
    if not b.startswith(("_MOC-", "_index-", "_Home")) and "/Sessions/" not in rp:
        sz = os.path.getsize(rp)
        if sz > 8192:
            warns.append(
                f"{sz // 1024}KB — over the 8KB split gate. Split into <=4KB atomic "
                "notes under the project's _MOC hub; split and link, never append-forever"
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
