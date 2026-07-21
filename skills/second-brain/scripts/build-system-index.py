#!/usr/bin/env python3
"""build-system-index — populate the vault's _system/ (CLAUDE.md, per-skill + per-workflow notes,
_MOC-system) and _projects.md + per-MOC Links blocks. Idempotent. Local vault only."""

import os, re, glob, shutil, sys

_here = os.path.dirname(os.path.abspath(__file__))
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
sys.path.insert(0, os.path.join(_here, "..", "..", "..", "hooks"))
try:
    import _hooklib as HL

    MEM = HL.MEM
    CONFIG = HL.CONFIG
except Exception:
    MEM = os.environ.get("CLAUDE_MEMORY_DIR") or os.path.expanduser(
        "~/.claude/second-brain-vault"
    )
    CONFIG = {}
HOME = os.path.expanduser("~")
SKILLS_DIR = os.path.join(HOME, ".claude/skills")
CMDS_DIR = os.path.join(HOME, ".claude/commands")
HOOKS_DIR = os.path.join(HOME, ".claude/hooks")
CLAUDE_MD = os.path.join(HOME, ".claude/CLAUDE.md")
SYS = os.path.join(MEM, "_system")


def w(path, text):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    open(path, "w").write(text)


def fm_desc(p):
    t = open(p, errors="ignore").read()
    m = re.search(r"^description:\s*(.+?)(?:\n[a-zA-Z_]+:|\n---)", t, re.S | re.M)
    if not m:
        m = re.search(r"^description:\s*(.+)$", t, re.M)
    return re.sub(r"\s+", " ", m.group(1)).strip().strip("\"'")[:400] if m else ""


# ---------- CLAUDE.md (refreshed copy) ----------
os.makedirs(SYS, exist_ok=True)
if os.path.exists(CLAUDE_MD):
    body = open(CLAUDE_MD, errors="ignore").read()
    w(
        os.path.join(SYS, "CLAUDE.md"),
        "---\nname: CLAUDE\ntags: [meta, type/system]\n---\n\n> Live copy of `~/.claude/CLAUDE.md` — refreshed by `/second-brain index`. ↩ [[_MOC-system]]\n\n"
        + body,
    )

# ---------- skills ----------
skills = (
    sorted(
        d
        for d in os.listdir(SKILLS_DIR)
        if os.path.isfile(os.path.join(SKILLS_DIR, d, "SKILL.md"))
    )
    if os.path.isdir(SKILLS_DIR)
    else []
)
for s in skills:
    desc = fm_desc(os.path.join(SKILLS_DIR, s, "SKILL.md"))
    w(
        os.path.join(SYS, "skills", f"skill-{s}.md"),
        f"---\nname: skill-{s}\ntags: [meta, type/skill]\n---\n\n# 🧩 {s}\n\n{desc}\n\n`~/.claude/skills/{s}/SKILL.md` · ↩ [[_MOC-system]]\n",
    )

# ---------- workflows: hooks + commands + the memory loop ----------
# The memory-system hooks that ship with second-brain.
HOOK_WHAT = {
    "session-memory": ("SessionStart", "inject the vault briefing + log the session"),
    "session-resume": (
        "SessionStart",
        "inject living state — recent captures, notes, rollup, _Home (project-aware)",
    ),
    "memory-recall": (
        "UserPromptSubmit",
        "just-in-time recall of relevant notes + the 📊 stats line",
    ),
    "interview-nudge": (
        "UserPromptSubmit",
        "nudge interview-first on detected larger tasks",
    ),
    "capture-exchange": (
        "Stop",
        "append each exchange to Daily/ + queue research/learnings",
    ),
    "memory-lint": (
        "PostToolUse",
        "warn on missing frontmatter / broken wikilinks / orphans",
    ),
    "stuck-detector": (
        "PostToolUse",
        "nudge to query memory when a command fails repeatedly",
    ),
    "precompact-carryover": ("PreCompact", "carry key state across compaction"),
}
for name, (ev, what) in HOOK_WHAT.items():
    if os.path.exists(os.path.join(HOOKS_DIR, name + ".sh")) or os.path.exists(
        os.path.join(HOOKS_DIR, name + ".py")
    ):
        w(
            os.path.join(SYS, "workflows", f"wf-{name}.md"),
            f"---\nname: wf-{name}\ntags: [meta, type/workflow]\n---\n\n# ⚙ {name}\n\n**Event:** {ev}  \n**Does:** {what}\n\n`~/.claude/hooks/{name}` · ↩ [[_MOC-system]] · [[memory-loop]]\n",
        )
cmds = (
    sorted(f[:-3] for f in os.listdir(CMDS_DIR) if f.endswith(".md"))
    if os.path.isdir(CMDS_DIR)
    else []
)
for c in cmds:
    desc = fm_desc(os.path.join(CMDS_DIR, c + ".md")) or "slash command"
    w(
        os.path.join(SYS, "workflows", f"cmd-{c}.md"),
        f"---\nname: cmd-{c}\ntags: [meta, type/workflow]\n---\n\n# ⌘ /{c}\n\n{desc}\n\n`~/.claude/commands/{c}.md` · ↩ [[_MOC-system]]\n",
    )
# memory-loop overview
w(
    os.path.join(SYS, "workflows", "memory-loop.md"),
    "---\nname: memory-loop\ntags: [meta, type/workflow]\n---\n\n# 🔁 The memory loop\n\n"
    "**Each chat** → [[wf-session-memory]] + [[wf-session-resume]] load context.  \n"
    "**Each prompt** → [[wf-memory-recall]] injects relevant notes + the 📊 stats line.  \n"
    "**Each reply** → [[wf-capture-exchange]] journals it to `Daily/`; research/learnings queue for curation.  \n"
    "**Periodically** → `/second-brain consolidate` distills the journal.\n\n↩ [[_MOC-system]]\n",
)


# ---------- _MOC-system ----------
def links(items):
    return "\n".join(f"- [[{i}]]" for i in items)


moc = [
    "---",
    "name: _MOC-system",
    "tags: [meta, type/moc]",
    "---",
    "",
    "# 🖥 System — Map of Content",
    "",
    "The Claude Code config behind this vault. ↩ [[_Home]] · [[_projects]]",
    "",
    "## Standing instructions",
    "- [[CLAUDE]]",
    "",
    "## Workflows",
    "- [[memory-loop]]",
]
moc += [
    f"- [[wf-{n}]]"
    for n, (_, _) in HOOK_WHAT.items()
    if os.path.exists(os.path.join(HOOKS_DIR, n + ".sh"))
    or os.path.exists(os.path.join(HOOKS_DIR, n + ".py"))
]
moc += [f"- [[cmd-{c}]]" for c in cmds]
moc += ["", "## Skills ({})".format(len(skills))]
moc += [f"- [[skill-{s}]]" for s in skills]
moc.append("")
w(os.path.join(MEM, "_MOC-system.md"), "\n".join(moc))

print(
    f"_system: CLAUDE.md + {len(skills)} skills + {len(HOOK_WHAT) + len(cmds) + 1} workflows + _MOC-system"
)

# ---------- projects: _projects.md table + per-MOC Links blocks ----------
# folder → [repo, live URL, local path, one-liner], from config.json "project_meta".
# Empty config → no _projects.md table (skip cleanly).
PROJECTS = {k: tuple(v) for k, v in CONFIG.get("project_meta", {}).items()}


def moc_name(folder):
    return "_MOC-" + folder.lstrip("_")


if PROJECTS:
    rows = ["| Project | GitHub | Live | Local | What |", "|---|---|---|---|---|"]
    for folder, (repo, url, path, desc) in PROJECTS.items():
        mocp = os.path.join(MEM, folder, moc_name(folder) + ".md")
        label = f"[[{moc_name(folder)}]]" if os.path.exists(mocp) else folder
        rows.append(f"| {label} | `{repo}` | {url} | `{path}` | {desc} |")
    w(
        os.path.join(MEM, "_projects.md"),
        "---\nname: _projects\ntags: [meta, type/moc]\n---\n\n# 🗂 Projects\n\nRepos, live URLs, and local paths for every project. ↩ [[_Home]] · [[_MOC-system]]\n\n"
        + "\n".join(rows)
        + "\n",
    )

    # inject/refresh a "## Links" block in each project's _MOC
    BLOCK_RE = re.compile(r"\n## Links\n.*?(?=\n## |\Z)", re.S)
    injected = 0
    for folder, (repo, url, path, desc) in PROJECTS.items():
        mocp = os.path.join(MEM, folder, moc_name(folder) + ".md")
        if not os.path.exists(mocp):
            continue
        t = open(mocp, errors="ignore").read()
        block = f"\n## Links\n- **Repo:** `{repo}`\n- **Live:** {url}\n- **Local:** `{path}`\n- ↩ [[_projects]]\n"
        t = BLOCK_RE.sub("", t).rstrip() + "\n" + block
        open(mocp, "w").write(t)
        injected += 1
    print(
        f"_projects.md written ({len(PROJECTS)} rows); Links blocks in {injected} MOCs"
    )
else:
    print("no project_meta in config.json — skipped _projects.md")
