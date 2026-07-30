#!/usr/bin/env python3
"""/second-brain doctor — self-test the memory system. `--fix` repairs symlink/dirs + migrates drift.
Read-only without --fix. Always exit 0 (it's a report)."""

import os, re, sys, json, glob, subprocess

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

HOME = os.path.expanduser("~")
WINDOWS = os.name == "nt"
# Honour a relocated config dir; the vault default stays under ~/.claude to match
# _hooklib and install.sh, which key off CLAUDE_MEMORY_DIR alone.
CLAUDE_DIR = os.environ.get("CLAUDE_CONFIG_DIR") or os.path.join(HOME, ".claude")
MEM = os.environ.get("CLAUDE_MEMORY_DIR") or os.path.join(
    HOME, ".claude/second-brain-vault"
)
# Locate the hooks dir + how hooks are registered — works in BOTH install modes:
#   plugin:     <plugin_root>/hooks   registered in <plugin_root>/.claude-plugin/plugin.json
#   install.sh: ~/.claude/hooks       registered in ~/.claude/settings.json
_SCRIPTDIR = os.path.dirname(os.path.abspath(__file__))
_CANDIDATES = [
    (
        os.path.join(os.environ["CLAUDE_PLUGIN_ROOT"], "hooks")
        if os.environ.get("CLAUDE_PLUGIN_ROOT")
        else None
    ),
    os.path.join(
        _SCRIPTDIR, "..", "..", "..", "hooks"
    ),  # plugin layout: skills/second-brain/scripts → root/hooks
    os.path.join(CLAUDE_DIR, "hooks"),  # install.sh layout
]
HOOKS = next(
    (
        os.path.abspath(p)
        for p in _CANDIDATES
        if p and os.path.isfile(os.path.join(p, "_hooklib.py"))
    ),
    os.path.join(CLAUDE_DIR, "hooks"),
)
PLUGIN_JSON = os.path.abspath(
    os.path.join(HOOKS, "..", ".claude-plugin", "plugin.json")
)
IS_PLUGIN = os.path.isfile(PLUGIN_JSON)
# plugin.json and settings.json share the same {"hooks": {...}} shape, so the same parse works.
SETTINGS = PLUGIN_JSON if IS_PLUGIN else os.path.join(CLAUDE_DIR, "settings.json")
STATE_DIR = os.environ.get("SECOND_BRAIN_STATE_DIR") or os.path.join(
    HOME, ".second-brain"
)
# Optional: mirror the vault into your Obsidian app's folder. Set SECOND_BRAIN_OBSIDIAN_LINK
# to that path to enable the symlink check/repair; leave unset to skip it.
VAULT_LINK = os.environ.get("SECOND_BRAIN_OBSIDIAN_LINK", "")
FIX = "--fix" in sys.argv
STRICT = "--strict" in sys.argv  # exit non-zero on FAIL, so CI and installers can gate


def _find_python():
    """Any working Python 3.8+, not a hardcoded /usr/bin/python3. Pinning that path
    made doctor FAIL on machines whose Python comes from Homebrew, nix, or a distro."""
    import shutil

    for c in (sys.executable, "python3", "/usr/bin/python3", "python", "py"):
        p = shutil.which(c) if c and not os.path.isabs(c) else c
        if p and os.path.exists(p):
            return p
    return ""


PY3 = _find_python()
rows = []
rows.append(
    (
        "PASS",
        "install mode",
        ("plugin" if IS_PLUGIN else "install.sh (~/.claude)") + f" · hooks: {HOOKS}",
        "",
        False,
    )
)


def chk(name, ok, detail="", warn=False, fix="", optional=False):
    """Record a check. `fix` is the exact command that resolves it — a report that says
    what is wrong without saying what to do is not an onboarding gate. `optional=True`
    keeps a check out of the pass/fail headline (MCP is not part of the core promise)."""
    rows.append(
        (
            "WARN" if (warn and not ok) else ("PASS" if ok else "FAIL"),
            name,
            detail,
            fix,
            optional,
        )
    )


# interpreter
chk(
    "python3 available",
    bool(PY3),
    PY3 or "not found on PATH",
    fix="macOS: xcode-select --install   ·   Debian: sudo apt install python3",
)
# vault dir
chk(
    "memory dir present",
    os.path.isdir(MEM),
    MEM,
    fix=f'mkdir -p "{MEM}"  (or re-run install.sh)',
)
# symlink (optional — only when SECOND_BRAIN_OBSIDIAN_LINK is set)
if VAULT_LINK:
    # A junction reports as a link too, so islink covers both once it exists.
    link_ok = os.path.islink(VAULT_LINK) and os.path.realpath(
        VAULT_LINK
    ) == os.path.realpath(MEM)
    manual = f'ln -s "{MEM}" "{VAULT_LINK}"'
    if WINDOWS:
        manual = f'cmd /c mklink /J "{VAULT_LINK}" "{MEM}"'
    if not link_ok and FIX and os.path.isdir(os.path.dirname(VAULT_LINK)):
        try:
            if os.path.islink(VAULT_LINK) or os.path.exists(VAULT_LINK):
                os.remove(VAULT_LINK)
            os.symlink(MEM, VAULT_LINK, target_is_directory=True)
            link_ok = True
        except OSError:
            # Windows refuses symlinks without Developer Mode or admin. A directory
            # junction needs neither, so try that before reporting anything.
            if WINDOWS:
                try:
                    subprocess.run(
                        ["cmd", "/c", "mklink", "/J", VAULT_LINK, MEM],
                        check=True,
                        capture_output=True,
                    )
                    link_ok = os.path.exists(VAULT_LINK)
                except Exception:
                    pass
        except Exception as e:
            rows.append(("FAIL", "symlink repair", repr(e), "", False))
    # An unlinkable mirror is inconvenient, not broken: the vault itself still works.
    chk("Obsidian vault symlink", link_ok, VAULT_LINK, warn=True, fix=manual)
# writable dirs
for d in ("Daily", ".recall-state"):
    dp = os.path.join(MEM, d)
    if not os.path.isdir(dp) and FIX:
        try:
            os.makedirs(dp, exist_ok=True)
        except Exception:
            pass
    ok = os.path.isdir(dp) and os.access(dp, os.W_OK)
    chk(f"{d}/ writable", ok, dp, warn=True, fix=f'mkdir -p "{dp}"')
# hook files present + executable
# The .py files are what the registrations actually run. The .sh wrappers are a
# hand-invocation convenience and do not exist to be run on Windows at all.
need = [
    "session-memory.py",
    "session-resume.py",
    "capture-exchange.py",
    "memory-lint.py",
    "memory-recall.py",
    "_hooklib.py",
]
if not WINDOWS:
    need += [
        "session-memory.sh",
        "session-resume.sh",
        "capture-exchange.sh",
        "memory-lint.sh",
        "memory-recall.sh",
    ]
missing = [h for h in need if not os.path.exists(os.path.join(HOOKS, h))]
chk(
    "hook files present",
    not missing,
    ("missing: " + ", ".join(missing)) if missing else f"{len(need)} files",
    fix="re-run install.sh to restore the hooks",
)
nonexec = [
    h
    for h in need
    if not WINDOWS
    and h.endswith(".sh")
    and os.path.exists(os.path.join(HOOKS, h))
    and not os.access(os.path.join(HOOKS, h), os.X_OK)
]
chk(
    "hook wrappers executable",
    not nonexec,
    ("chmod needed: " + ", ".join(nonexec)) if nonexec else "ok",
    fix=f'chmod +x "{HOOKS}"/*.sh',
)
# registration in settings.json
try:
    d = json.load(open(SETTINGS, encoding="utf-8"))
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
        chk(
            f"registered: {want}",
            want in cmds,
            fix="re-run install.sh to register the hooks",
        )
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
        if "timeout" in h and "hooks" in h.get("command", "")
    )
    chk(
        "hook timeouts set",
        have_to >= 5,
        f"{have_to} memory hooks have timeout",
        warn=True,
    )
except Exception as e:
    chk(("plugin.json" if IS_PLUGIN else "settings.json") + " parse", False, repr(e))
# migration drift
notes = [
    p
    for p in glob.glob(os.path.join(MEM, "**", "*.md"), recursive=True)
    # Same scope as health.py: journals, session logs, generated system notes and
    # backups are not curated notes, so they never carry full v2 frontmatter.
    if os.path.basename(p) not in ("MEMORY.md", "context.md", "_session-log.md")
    and "/Daily/" not in p
    and "/Weekly/" not in p
    and "/Sessions/" not in p
    and "/_system/" not in p
    and "/_backup" not in p
    and not os.path.basename(p).startswith("_")
]


def _has_status(path):
    """Parse the real frontmatter block — a fixed char window misses notes whose
    description pushes `status:` further down."""
    t = open(path, errors="ignore", encoding="utf-8").read()
    if not t.startswith("---\n"):
        return False
    end = t.find("\n---", 4)
    # Accept both shapes: top-level `status:` and the nested `metadata:` form a
    # frontmatter normalizer produces.
    return bool(re.search(r"^\s*status:", t[4 : end if end > 0 else 4000], re.M))


drift = [os.path.basename(p) for p in notes if not _has_status(p)]
if drift and FIX:
    try:
        subprocess.run(
            [
                PY3 or sys.executable,
                os.path.join(
                    SK if (SK := os.path.dirname(__file__)) else ".",
                    "migrate-frontmatter.py",
                ),
            ],
            timeout=30,
        )
        drift = [os.path.basename(p) for p in notes if not _has_status(p)]
    except Exception:
        pass
chk(
    "frontmatter v2 coverage",
    not drift,
    (f"{len(drift)} notes missing v2") if drift else f"{len(notes)} notes ok",
    warn=True,
)
# error log tail
elog = os.path.join(STATE_DIR, "hook-errors.log")
if os.path.exists(elog):
    tail = open(elog, errors="ignore", encoding="utf-8").read().strip().splitlines()[-3:]
    chk(
        "hook-errors.log",
        len(tail) == 0,
        ("recent: " + " | ".join(tail)) if tail else "clean",
        warn=True,
    )
else:
    chk("hook-errors.log", True, "none (clean)")

# --- vault content -----------------------------------------------------------
# An empty vault is a valid install and a useless memory. Say so, rather than passing
# silently and leaving the user wondering why recall never returns anything.
_notes = []
for _root, _dirs, _files in os.walk(MEM):
    _rel = os.path.relpath(_root, MEM)
    if any(
        p in ("Daily", "Weekly", "Sessions", "_system")
        or p.startswith((".", "_backup"))
        for p in _rel.split(os.sep)
    ):
        continue
    _notes += [f for f in _files if f.endswith(".md") and not f.startswith("_")]
chk(
    "vault has notes",
    bool(_notes),
    f"{len(_notes)} note(s)" if _notes else "no curated notes yet",
    warn=True,
    fix='start a Claude Code session and work normally, or: /second-brain capture "<fact>"',
)

# project routing — the single most common reason notes land in the wrong place
_cfg_path = os.path.join(MEM, "config.json")
try:
    _pmap = (json.load(open(_cfg_path, encoding="utf-8")) or {}).get("project_map") or {}
except Exception:
    _pmap = {}
chk(
    "project routing configured",
    bool(_pmap),
    f"{len(_pmap)} repo(s) mapped"
    if _pmap
    else "no project_map — notes will land in the vault root",
    warn=True,
    fix=f"python3 {os.path.join(_SCRIPTDIR, 'setup.py')}",
)

# --- MCP: optional, and kept out of the headline ------------------------------
MCP_DIR = os.path.abspath(os.path.join(HOOKS, "..", "mcp"))
_mcp_files = ["sb_core.py", "server_stdio.py", "server_http.py", "mcp-setup.py"]
_mcp_missing = [f for f in _mcp_files if not os.path.isfile(os.path.join(MCP_DIR, f))]
chk(
    "MCP server files",
    not _mcp_missing,
    "not installed" if _mcp_missing else MCP_DIR,
    warn=True,
    optional=True,
    fix="only needed to expose the vault to other apps; clone the repo and run mcp/mcp-setup.py --write",
)
# Claude Desktop's config path is macOS-only; do not report a Linux box as misconfigured
_clients = {"Cursor": os.path.join(HOME, ".cursor/mcp.json")}
if sys.platform == "darwin":
    _clients["Claude Desktop"] = os.path.join(
        HOME, "Library/Application Support/Claude/claude_desktop_config.json"
    )
for cname, cpath in _clients.items():
    reg = False
    try:
        reg = "second-brain" in json.load(open(cpath, encoding="utf-8")).get("mcpServers", {})
    except Exception:
        reg = False
    chk(
        f"MCP registered: {cname}",
        reg,
        cpath if reg else "not registered",
        warn=True,
        optional=True,
        fix="python3 mcp/mcp-setup.py --write",
    )

# --- report -------------------------------------------------------------------
core = [r for r in rows if not r[4]]
opt = [r for r in rows if r[4]]
fails = [r for r in core if r[0] == "FAIL"]
warns = [r for r in core if r[0] == "WARN"]
MARK = {"PASS": "✓", "WARN": "▲", "FAIL": "✗"}

print("# /second-brain doctor" + ("  (--fix applied)" if FIX else ""))
for st, name, detail, _fix, _o in core:
    print(f"  {MARK[st]} {name}" + (f" — {detail}" if detail else ""))
if opt:
    print("\n  optional (MCP — exposes the vault to other apps; not needed for memory)")
    for st, name, detail, _fix, _o in opt:
        print(
            f"  {'✓' if st == 'PASS' else '·'} {name}"
            + (f" — {detail}" if detail else "")
        )

print(
    f"\n{len(core) - len(fails) - len(warns)} pass · {len(warns)} warn · {len(fails)} fail"
)

# Ordered next actions: failures first, then warnings, each with the command to run.
todo = [r for r in fails + warns if r[3]]
if todo:
    print("\nNext:")
    for i, (_st, name, _d, fix, _o) in enumerate(todo, 1):
        print(f"  {i}. {name}\n     {fix}")
elif fails or warns:
    print("\nNext:\n  1. run `/second-brain doctor --fix` to repair what it can")
else:
    print("\nAll good. Restart Claude Code if you just installed, then work normally.")

if STRICT and fails:
    sys.exit(1)
