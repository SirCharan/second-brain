#!/usr/bin/env python3
"""/second-brain doctor — self-test the memory system. `--fix` repairs symlink/dirs + migrates drift.
Read-only without --fix. Always exit 0 (it's a report)."""

import os, re, sys, json, glob, subprocess

HOME = os.path.expanduser("~")
MEM = os.environ.get("CLAUDE_MEMORY_DIR") or os.path.join(
    HOME, ".claude/second-brain-vault"
)
HOOKS = os.path.join(HOME, ".claude/hooks")
# Optional: mirror the vault into your Obsidian app's folder. Set SECOND_BRAIN_OBSIDIAN_LINK
# to that path to enable the symlink check/repair; leave unset to skip it.
VAULT_LINK = os.environ.get("SECOND_BRAIN_OBSIDIAN_LINK", "")
SETTINGS = os.path.join(HOME, ".claude/settings.json")
FIX = "--fix" in sys.argv
rows = []


def chk(name, ok, detail="", warn=False):
    rows.append(
        ("WARN" if (warn and not ok) else ("PASS" if ok else "FAIL"), name, detail)
    )


# interpreter
chk(
    "system python3 (/usr/bin/python3)",
    os.path.exists("/usr/bin/python3"),
    "pinned interpreter for hooks",
)
# vault dir
chk("memory dir present", os.path.isdir(MEM), MEM)
# symlink (optional — only when SECOND_BRAIN_OBSIDIAN_LINK is set)
if VAULT_LINK:
    link_ok = os.path.islink(VAULT_LINK) and os.path.realpath(
        VAULT_LINK
    ) == os.path.realpath(MEM)
    if not link_ok and FIX and os.path.isdir(os.path.dirname(VAULT_LINK)):
        try:
            if os.path.islink(VAULT_LINK) or os.path.exists(VAULT_LINK):
                os.remove(VAULT_LINK)
            os.symlink(MEM, VAULT_LINK)
            link_ok = True
        except Exception as e:
            rows.append(("FAIL", "symlink repair", repr(e)))
    chk("Obsidian vault symlink", link_ok, VAULT_LINK)
# writable dirs
for d in ("Daily", ".recall-state"):
    dp = os.path.join(MEM, d)
    if not os.path.isdir(dp) and FIX:
        try:
            os.makedirs(dp, exist_ok=True)
        except Exception:
            pass
    ok = os.path.isdir(dp) and os.access(dp, os.W_OK)
    chk(f"{d}/ writable", ok, dp, warn=True)
# hook files present + executable
need = [
    "session-memory.sh",
    "session-resume.sh",
    "session-resume.py",
    "capture-exchange.sh",
    "capture-exchange.py",
    "memory-lint.sh",
    "memory-lint.py",
    "memory-recall.sh",
    "memory-recall.py",
    "_hooklib.py",
]
missing = [h for h in need if not os.path.exists(os.path.join(HOOKS, h))]
chk(
    "hook files present",
    not missing,
    ("missing: " + ", ".join(missing)) if missing else f"{len(need)} files",
)
nonexec = [
    h
    for h in need
    if h.endswith(".sh")
    and os.path.exists(os.path.join(HOOKS, h))
    and not os.access(os.path.join(HOOKS, h), os.X_OK)
]
chk(
    "hook wrappers executable",
    not nonexec,
    ("chmod needed: " + ", ".join(nonexec)) if nonexec else "ok",
)
# registration in settings.json
try:
    d = json.load(open(SETTINGS))
    H = d.get("hooks", {})
    cmds = " ".join(
        h.get("command", "")
        for ev in H.values()
        for e in ev
        for h in e.get("hooks", [])
    )
    for want in [
        "session-memory",
        "session-resume",
        "capture-exchange",
        "memory-recall",
        "memory-lint",
    ]:
        chk(f"registered: {want}", want in cmds)
    ntimeout = sum(
        1
        for ev in H.values()
        for e in ev
        for h in e.get("hooks", [])
        if "memory" in h.get("command", "")
        or "capture-exchange" in h.get("command", "")
        or "session-" in h.get("command", "")
    )
    have_to = sum(
        1
        for ev in H.values()
        for e in ev
        for h in e.get("hooks", [])
        if "timeout" in h and "hooks/" in h.get("command", "")
    )
    chk(
        "hook timeouts set",
        have_to >= 5,
        f"{have_to} memory hooks have timeout",
        warn=True,
    )
except Exception as e:
    chk("settings.json parse", False, repr(e))
# migration drift
notes = [
    p
    for p in glob.glob(os.path.join(MEM, "**", "*.md"), recursive=True)
    if os.path.basename(p) not in ("MEMORY.md", "context.md", "_session-log.md")
    and "/Daily/" not in p
    and "/Weekly/" not in p
]
drift = [
    os.path.basename(p)
    for p in notes
    if "\nstatus:" not in open(p, errors="ignore").read()[:400]
    and "\nstatus:" not in ""
]
drift = [
    os.path.basename(p)
    for p in notes
    if not re.search(r"^status:", open(p, errors="ignore").read()[:400], re.M)
]
if drift and FIX:
    try:
        subprocess.run(
            [
                "/usr/bin/python3",
                os.path.join(
                    SK if (SK := os.path.dirname(__file__)) else ".",
                    "migrate-frontmatter.py",
                ),
            ],
            timeout=30,
        )
        drift = [
            os.path.basename(p)
            for p in notes
            if not re.search(r"^status:", open(p, errors="ignore").read()[:400], re.M)
        ]
    except Exception:
        pass
chk(
    "frontmatter v2 coverage",
    not drift,
    (f"{len(drift)} notes missing v2 (run migrate)")
    if drift
    else f"{len(notes)} notes ok",
    warn=True,
)
# error log tail
elog = os.path.join(HOOKS, "hook-errors.log")
if os.path.exists(elog):
    tail = open(elog, errors="ignore").read().strip().splitlines()[-3:]
    chk(
        "hook-errors.log",
        len(tail) == 0,
        ("recent: " + " | ".join(tail)) if tail else "clean",
        warn=True,
    )
else:
    chk("hook-errors.log", True, "none (clean)")

# report
fails = [r for r in rows if r[0] == "FAIL"]
warns = [r for r in rows if r[0] == "WARN"]
print("# /second-brain doctor" + ("  (--fix applied)" if FIX else ""))
for st, name, detail in rows:
    mark = {"PASS": "✓", "WARN": "▲", "FAIL": "✗"}[st]
    print(f"  {mark} {name}" + (f" — {detail}" if detail else ""))
print(
    f"\n{len(rows) - len(fails) - len(warns)} pass · {len(warns)} warn · {len(fails)} fail"
    + (
        ""
        if FIX or not (fails or warns)
        else "   (run `/second-brain doctor --fix` to repair)"
    )
)
