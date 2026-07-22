#!/usr/bin/env python3
"""Shared tool layer for the second-brain MCP servers. Pure stdlib.

Both transports (server_stdio.py, server_http.py) call into here. Two genuinely
missing primitives are built (write_note, rank); the rest are thin wrappers that
shell the existing skills/second-brain/scripts/*.py and return their stdout.

Reuses hooks/_hooklib.py (atomic_write, project_for, scrub_secrets, MEM,
embed_ready, EMBED_*). Located in both install modes the same way export.py does."""

import os, re, sys, glob, time, subprocess

# --- locate _hooklib (hooks dir) + the skill scripts, in either install mode ---
_THIS = os.path.dirname(os.path.abspath(__file__))
_ROOTS = [
    os.environ.get("CLAUDE_PLUGIN_ROOT"),
    os.path.join(_THIS, ".."),  # repo root: mcp/ -> ..
    os.path.expanduser("~/.claude"),  # install.sh layout
]
_HOOK_DIR = next(
    (
        os.path.abspath(os.path.join(r, "hooks"))
        for r in _ROOTS
        if r and os.path.isfile(os.path.join(r, "hooks", "_hooklib.py"))
    ),
    os.path.expanduser("~/.claude/hooks"),
)
sys.path.insert(0, _HOOK_DIR)
import _hooklib as HL  # noqa: E402

MEM = HL.MEM
SCRIPTS = next(
    (
        os.path.abspath(os.path.join(r, "skills", "second-brain", "scripts"))
        for r in _ROOTS
        if r
        and os.path.isfile(
            os.path.join(r, "skills", "second-brain", "scripts", "regen-index.py")
        )
    ),
    os.path.join(_THIS, "..", "skills", "second-brain", "scripts"),
)

SKIP_FOLDERS = ("Daily", "Weekly", "Sessions", "_system")
EXCLUDE = {"MEMORY.md", "context.md", "_session-log.md"}
RETIRED = ("retired", "deprecated", "archived", "superseded")
STOP = set(
    "the a an and or of to in on for with is are was were be been this that these those i you "
    "it we they he she how what why when where which who do does did can could should would will "
    "just now then here there my your our their its from into out up down over about as at by so "
    "if not no yes ok okay thanks please help make add use using get got need want like also more "
    "most some any all one two new old via per etc pls better stronger strong full work works".split()
)
_CHIP = {
    "active": "🟢 **active**",
    "watch": "🟡 **watch**",
    "retired": "⚫ **retired**",
    "real-money": "🔴 **real-money**",
}


def _today():
    return time.strftime("%Y-%m-%d")


def _words(s):
    return set(re.findall(r"[a-z0-9]{3,}", (s or "").lower()))


def _slug(s):
    s = re.sub(r"[^a-z0-9]+", "-", (s or "").lower()).strip("-")
    return (s or "note")[:60]


def _safe_folder(name):
    """A caller-supplied project only becomes a literal folder if it's a clean slug."""
    return bool(name) and bool(re.match(r"^[a-z0-9][a-z0-9_-]*$", name.lower()))


# --------------------------------------------------------------------------- #
# write_note — the missing primitive: deterministic v2 curated-note writer
# --------------------------------------------------------------------------- #
def write_note(
    title,
    body,
    tags=None,
    description=None,
    project=None,
    source="mcp",
    note_type="reference",
    status="active",
):
    """Write a curated v2 note (frontmatter + H1/chip/callout/Related) and re-index.
    Returns the absolute path written. Never overwrites: an existing note gets a
    dated `## Update` section appended instead."""
    title = HL.scrub_secrets((title or "").strip()) or "untitled"
    body = HL.scrub_secrets((body or "").strip())
    name = _slug(title)

    folder = HL.project_for(project) if project else None
    if not folder and _safe_folder(project or ""):
        folder = project.lower()
    dest_dir = os.path.join(MEM, folder) if folder else MEM
    path = os.path.join(dest_dir, name + ".md")

    if description is None:
        first = next((ln.strip() for ln in body.splitlines() if ln.strip()), title)
        description = re.sub(r"\s+", " ", first)[:150]
    description = HL.scrub_secrets(description)

    # existing note -> enrich (append dated update), never clobber
    if os.path.isfile(path):
        try:
            old = open(path, errors="ignore").read().rstrip()
        except Exception:
            old = ""
        old = re.sub(
            r"^(last_confirmed:\s*).*$", r"\g<1>" + _today(), old, count=1, flags=re.M
        )
        HL.atomic_write(path, old + f"\n\n## Update {_today()}\n\n{body}\n")
        _reindex()
        return path

    if not tags:
        tags = ["notes", "project/%s" % (folder or "general"), "type/%s" % note_type]
    chip = _CHIP.get(status, _CHIP["active"])
    moc = "_MOC-%s" % folder if folder else "_MOC"

    fm = (
        "---\n"
        f"name: {name}\n"
        f'title: "{title}"\n'
        f"description: {description}\n"
        f"tags: [{', '.join(tags)}]\n"
        f"asserted: {_today()}\n"
        f"last_confirmed: {_today()}\n"
        f"source: {source}\n"
        "confidence: med\n"
        f"status: {status}\n"
        "supersedes: []\n"
        "metadata:\n"
        f"  type: {note_type}\n"
        "---\n"
    )
    doc = (
        fm + f"\n# {title}\n\n{chip}\n\n"
        f"> [!info] {description}\n\n"
        f"{body}\n\n"
        f"## Related\n- [[{moc}]]\n"
    )
    HL.atomic_write(path, doc)
    _reindex()
    return path


def _reindex():
    try:
        subprocess.run(
            ["/usr/bin/python3", os.path.join(SCRIPTS, "regen-index.py"), "--write"],
            capture_output=True,
            timeout=30,
            env=_env(),
        )
    except Exception as e:
        HL.log_err("mcp.reindex", e)


# --------------------------------------------------------------------------- #
# rank — self-contained decay-aware keyword ranker (mirrors memory-recall.py,
# does NOT import or modify it)
# --------------------------------------------------------------------------- #
def _age_days(head):
    for key in ("last_confirmed", "asserted"):
        m = re.search(r"^\s*" + key + r":\s*(\d{4}-\d{2}-\d{2})", head, re.M)
        if m:
            try:
                t = time.mktime(time.strptime(m.group(1), "%Y-%m-%d"))
                return (time.time() - t) / 86400.0
            except Exception:
                return None
    return None


def rank(query, project=None, limit=5):
    """Decay-aware keyword ranking over curated notes. Returns
    [{name, folder, description, score}], best first. Optional semantic fill."""
    kw = {w for w in _words(query) if w not in STOP}
    rows = []
    if kw:
        for p in glob.glob(os.path.join(MEM, "*", "*.md")):
            b = os.path.basename(p)
            if b in EXCLUDE or b.startswith("_"):
                continue
            folder = os.path.basename(os.path.dirname(p))
            if folder in SKIP_FOLDERS:
                continue
            name = os.path.splitext(b)[0]
            try:
                head = open(p, errors="ignore").read(6144)
            except Exception:
                continue
            sm = re.search(r"^\s*status:\s*(.+)$", head, re.M)
            if sm and sm.group(1).strip().strip("\"'").lower() in RETIRED:
                continue
            m = re.search(r"^description:\s*(.+)$", head, re.M)
            desc = (m.group(1).strip().strip("\"'")) if m else ""
            hit_name = kw & _words(name)
            hit_desc = kw & _words(desc)
            body_extra = (kw & _words(head)) - hit_name - hit_desc
            score = 5 * len(hit_name) + 3 * len(hit_desc) + 1 * len(body_extra)
            if score <= 0:
                continue
            if project and folder == project:
                score = int(score * 1.5)
            age = _age_days(head)
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
                    "description": desc[:150],
                    "score": score,
                }
            )
        rows.sort(key=lambda r: r["score"], reverse=True)
    rows = rows[:limit]

    need = limit - len(rows)
    if need > 0 and HL.embed_ready():
        have = {r["name"] for r in rows}
        rows += _semantic_fill(query, have, need)
    return rows[:limit]


def _semantic_fill(query, exclude, need):
    try:
        r = subprocess.run(
            [HL.EMBED_VENV_PY, HL.EMBED_SCRIPT, "query", query, "12"],
            capture_output=True,
            text=True,
            timeout=10,
            env=_env(),
        )
    except Exception:
        return []
    out = []
    for line in r.stdout.splitlines():
        parts = line.split("\t")
        if len(parts) != 3:
            continue
        score, name, folder = parts
        try:
            if float(score) < 0.5 or name in exclude:
                continue
        except ValueError:
            continue
        desc = ""
        try:
            head = open(os.path.join(MEM, folder, name + ".md"), errors="ignore").read(
                2048
            )
            sm = re.search(r"^\s*status:\s*(.+)$", head, re.M)
            if sm and sm.group(1).strip().strip("\"'").lower() in RETIRED:
                continue
            m = re.search(r"^description:\s*(.+)$", head, re.M)
            desc = (m.group(1).strip().strip("\"'"))[:150] if m else ""
        except Exception:
            pass
        out.append({"name": name, "folder": folder, "description": desc, "score": 0})
        if len(out) >= need:
            break
    return out


# --------------------------------------------------------------------------- #
# thin wrappers over the existing scripts
# --------------------------------------------------------------------------- #
def _env():
    e = dict(os.environ)
    e["CLAUDE_MEMORY_DIR"] = MEM
    return e


def _run(script, *args):
    try:
        r = subprocess.run(
            ["/usr/bin/python3", os.path.join(SCRIPTS, script), *args],
            capture_output=True,
            text=True,
            timeout=45,
            env=_env(),
        )
        return (r.stdout or "") + (
            ("\n[stderr] " + r.stderr) if r.stderr.strip() else ""
        )
    except Exception as e:
        return f"error running {script}: {e!r}"


def recall(query, project=None, limit=5):
    hits = rank(query, project=project, limit=limit)
    if not hits:
        return "No matching notes."
    lines = []
    for h in hits:
        line = "- [[%s]] (%s)" % (h["name"], h["folder"])
        if h["description"]:
            line += " — " + h["description"]
        lines.append(line)
    return "\n".join(lines)


def pull(query):
    return _run("pull.py", *str(query).split())


def export(fmt="claude"):
    return _run("export.py", "--format", fmt or "claude")


def graph(folder=None):
    return _run("graph.py", *(["--folder", folder] if folder else []))


def stale(days=180):
    return _run("stale.py", "--days", str(days or 180))


def health():
    return _run("health.py")


def capture(fact, project=None):
    title = " ".join(str(fact).split()[:8]) or "note"
    p = write_note(title, fact, project=project, source="mcp", note_type="fact")
    return "captured -> " + p


def learn(text, project=None):
    title = " ".join(str(text).split()[:8]) or "learning"
    p = write_note(
        title, text, project=project, source="research", note_type="learning"
    )
    return "learned -> " + p


# --------------------------------------------------------------------------- #
# tool registry (JSON-schema) + dispatch
# --------------------------------------------------------------------------- #
def _t(name, desc, props, required):
    return {
        "name": name,
        "description": desc,
        "inputSchema": {"type": "object", "properties": props, "required": required},
    }


_S = {"type": "string"}
_I = {"type": "integer"}
TOOLS = [
    _t(
        "recall",
        "Recall the most relevant vault notes for a query (decay-aware keyword ranking, optional semantic fill).",
        {"query": _S, "project": _S, "limit": _I},
        ["query"],
    ),
    _t(
        "pull",
        "Full-text 'unstick' search: return the full text of the top matching notes across the whole vault.",
        {"query": _S},
        ["query"],
    ),
    _t(
        "export",
        "Flatten the whole vault into one portable context file. format: claude|chatgpt|agents-md.",
        {"format": _S},
        [],
    ),
    _t(
        "health",
        "Audit the vault: counts, missing fields, broken links, orphans, stale notes.",
        {},
        [],
    ),
    _t(
        "stale",
        "List active notes not confirmed in N+ days (default 180).",
        {"days": _I},
        [],
    ),
    _t(
        "graph",
        "Emit a Mermaid link-graph of the vault (optionally one folder).",
        {"folder": _S},
        [],
    ),
    _t(
        "capture",
        "Write/update one atomic fact note in the vault, then re-index.",
        {"fact": _S, "project": _S},
        ["fact"],
    ),
    _t(
        "learn",
        "Curate a research finding or learning as a note in the vault, then re-index.",
        {"text": _S, "project": _S},
        ["text"],
    ),
]

_DISPATCH = {
    "recall": lambda a: recall(
        a.get("query", ""), a.get("project"), int(a.get("limit") or 5)
    ),
    "pull": lambda a: pull(a.get("query", "")),
    "export": lambda a: export(a.get("format", "claude")),
    "health": lambda a: health(),
    "stale": lambda a: stale(int(a.get("days") or 180)),
    "graph": lambda a: graph(a.get("folder")),
    "capture": lambda a: capture(a.get("fact", ""), a.get("project")),
    "learn": lambda a: learn(a.get("text", ""), a.get("project")),
}


def call_tool(name, args):
    """Dispatch a tool call. Returns a text string. Never raises."""
    fn = _DISPATCH.get(name)
    if not fn:
        return "unknown tool: %s" % name
    try:
        return str(fn(args or {}))
    except Exception as e:
        HL.log_err("mcp.call.%s" % name, e)
        return "error in %s: %r" % (name, e)
