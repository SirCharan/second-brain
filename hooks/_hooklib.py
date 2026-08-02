#!/usr/bin/env python3
"""Shared helpers for the memory hooks. Python 3.9-safe, stdlib-only.
Import works because Python puts the running script's dir on sys.path[0]."""

import os
import subprocess, re, json, tempfile, time, traceback

import sys
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

# Vault location: $CLAUDE_MEMORY_DIR wins, else a sensible default under ~/.claude.
MEM = os.environ.get("CLAUDE_MEMORY_DIR") or os.path.expanduser(
    "~/.claude/second-brain-vault"
)

# Where the hook scripts actually live. Self-locating via __file__ so it is correct
# in BOTH install modes: install.sh (~/.claude/hooks) and plugin (${CLAUDE_PLUGIN_ROOT}/hooks).
HOOK_DIR = os.path.dirname(os.path.abspath(__file__))

# Stable per-user state dir, independent of install mode. Holds the error log, hook
# state (ctx-monitor / stuck-detector), and the optional semantic-embed venv + index.
# Override with $SECOND_BRAIN_STATE_DIR.
STATE_DIR = os.environ.get("SECOND_BRAIN_STATE_DIR") or os.path.expanduser(
    "~/.second-brain"
)
ERRLOG = os.path.join(STATE_DIR, "hook-errors.log")

# Optional semantic recall (opt-in — NOT part of the stdlib core). `sb-embed setup`
# builds this venv with fastembed; until then embed_ready() is False and recall stays
# keyword-only. The embed script sits next to this file (both install modes).
EMBED_SCRIPT = os.path.join(HOOK_DIR, "memory-embed.py")
EMBED_VENV_PY = os.path.join(
    STATE_DIR,
    "venv-embed",
    *(("Scripts", "python.exe") if os.name == "nt" else ("bin", "python")),
)


def embed_ready():
    """True only if the optional semantic-embed venv + script both exist."""
    return os.path.isfile(EMBED_VENV_PY) and os.path.isfile(EMBED_SCRIPT)


def load_config():
    """Read the vault's config.json (project map, domains, ignore lists, project
    metadata). Missing/broken file → empty dict, so everything degrades to generic
    auto-defaults. Never raises."""
    import json

    try:
        with open(os.path.join(MEM, "config.json"), errors="ignore", encoding="utf-8") as f:
            cfg = json.load(f)
            return cfg if isinstance(cfg, dict) else {}
    except Exception:
        return {}


CONFIG = load_config()



def detach_kwargs():
    """Popen kwargs that let a background refresh outlive this hook, per platform.
    start_new_session is POSIX-only, so Windows gets the equivalent creation flag."""
    if os.name == "nt":
        flags = getattr(subprocess, "CREATE_NEW_PROCESS_GROUP", 0) | getattr(
            subprocess, "DETACHED_PROCESS", 0
        )
        return {"creationflags": flags}
    return {"start_new_session": True}

def vault_ok():
    """True only if the memory dir is present — hooks no-op cleanly otherwise."""
    return os.path.isdir(MEM)


def atomic_write(path, text):
    """Write via temp file in the same dir + os.replace so a concurrent reader
    never sees a truncated/partial file. Returns True on success."""
    d = os.path.dirname(path) or "."
    os.makedirs(d, exist_ok=True)
    fd, tmp = tempfile.mkstemp(dir=d, prefix=".tmp-", suffix=".swap")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            f.write(text)
        os.replace(tmp, path)
        return True
    except Exception:
        try:
            os.unlink(tmp)
        except Exception:
            pass
        raise


def read_json(path, default=None):
    import json

    try:
        with open(path, errors="ignore", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {} if default is None else default


def write_json(path, obj):
    import json

    atomic_write(path, json.dumps(obj))


def log_err(hook, exc):
    """Append one capped line to hook-errors.log; never raises. Keeps the log bounded."""
    try:
        line = "%s\t%s\t%s\n" % (
            time.strftime("%Y-%m-%d %H:%M:%S"),
            hook,
            (repr(exc) if not isinstance(exc, str) else exc)[:300],
        )
        os.makedirs(os.path.dirname(ERRLOG), exist_ok=True)
        with open(ERRLOG, "a", encoding="utf-8") as f:
            f.write(line)
        # trim if it grows past ~500 lines
        if os.path.getsize(ERRLOG) > 120_000:
            with open(ERRLOG, errors="ignore", encoding="utf-8") as f:
                tail = f.readlines()[-300:]
            atomic_write(ERRLOG, "".join(tail))
    except Exception:
        pass


# Repo/dir → memory folder. Fully driven by config.json:
#   "project_map":      {"myapp": "myapp", "myapp-web": "myapp"}   exact basename → folder
#   "project_prefixes": {"acme-": "acme"}                          basename prefix → folder
# Both optional; empty → project_for() returns None (notes land in the vault root).
_PROJ_EXACT = CONFIG.get("project_map", {})
_PROJ_PREFIX = CONFIG.get("project_prefixes", {})


def _proj_lookup(b):
    if b in _PROJ_EXACT:
        return _PROJ_EXACT[b]
    for prefix, folder in _PROJ_PREFIX.items():
        if b.startswith(prefix):
            return folder
    return None


def project_for(cwd):
    """Map a cwd (full path or bare basename) to a memory folder.
    Exact basename → prefix rules → git-root fallback (so a subdir/worktree of a
    known repo still resolves). Returns None if unknown. Never raises."""
    if not cwd:
        return None
    hit = _proj_lookup(os.path.basename(cwd.rstrip("/")).lower())
    if hit:
        return hit
    try:  # git-root fallback: resolve repo top-level, retry on its basename
        import subprocess

        root = subprocess.run(
            ["git", "-C", cwd, "rev-parse", "--show-toplevel"],
            capture_output=True,
            text=True,
            timeout=2,
        ).stdout.strip()
        if root:
            return _proj_lookup(os.path.basename(root).lower())
    except Exception:
        pass
    return None


# Folders that are not projects — never auto-register or scaffold these. A generic list:
# checkout parents, scratch dirs, OS folders, and common repo subdirs.
_NON_PROJECT = {
    "claude",
    "code",
    "src",
    "repos",
    "projects",
    "tmp",
    "temp",
    "desktop",
    "documents",
    "downloads",
    "home",
    "web",
    "app",
    "worktrees",
    "node_modules",
}


def _git_root(cwd):
    """Absolute path of the enclosing git repo top-level, or None. Never raises."""
    try:
        import subprocess

        return (
            subprocess.run(
                ["git", "-C", cwd, "rev-parse", "--show-toplevel"],
                capture_output=True,
                text=True,
                timeout=2,
            ).stdout.strip()
            or None
        )
    except Exception:
        return None


def register_project(folder, repo_basename=None):
    """Add repo_basename → folder to the vault's config.json project_map.
    Idempotent; returns True when the file was changed. Never raises."""
    try:
        path = os.path.join(MEM, "config.json")
        cfg = read_json(path, {}) or {}
        pm = cfg.setdefault("project_map", {})
        key = (repo_basename or folder).lower()
        if pm.get(key) == folder:
            return False
        pm[key] = folder
        atomic_write(path, json.dumps(cfg, indent=2) + "\n")
        _PROJ_EXACT[key] = folder  # keep this process consistent with disk
        return True
    except Exception as e:
        log_err("hooklib.register_project", e)
        return False


_MOC_TEMPLATE = """---
name: _MOC-{moc}
title: "{title} — hub"
description: "Entry point for {title}: architecture, decisions, incidents, and release log."
tags: [{domain}, project/{folder}, type/moc]
asserted: {today}
last_confirmed: {today}
source: inferred
confidence: med
status: active
supersedes: []
metadata:
  node_type: memory
  type: moc
---

# {title} — hub

🟡 **watch** · auto-created when this project first appeared. Fill the sections as notes land.

> [!info] What this is
> One entry point for everything about {title}. Keep this hub thin — links and one-line hooks only, no body facts.

## Architecture

## Decisions

## Incidents & gotchas

## Release log

## Related
- [[_Home]]
- [[MEMORY]]
"""


def moc_name(folder):
    """Hub note name for a folder. Meta folders drop the leading underscore
    (_infra → _MOC-infra) so the name matches the links the vault already uses."""
    return "_MOC-" + folder.lstrip("_")


def ensure_project_scaffold(folder, domain=None):
    """Create MEM/<folder>/ and a thin _MOC hub if missing. Idempotent — returns True
    only when it created the hub, and NEVER overwrites an existing one. Never raises."""
    if not folder or not vault_ok():
        return False
    try:
        d = os.path.join(MEM, folder)
        os.makedirs(d, exist_ok=True)
        path = os.path.join(d, moc_name(folder) + ".md")
        if os.path.exists(path):
            return False
        title = folder.lstrip("_").replace("-", " ").title()
        atomic_write(
            path,
            _MOC_TEMPLATE.format(
                moc=moc_name(folder)[5:],
                folder=folder,
                title=title,
                domain=domain or CONFIG.get("domains", {}).get(folder, ["notes"])[0],
                today=time.strftime("%Y-%m-%d"),
            ),
        )
        return True
    except Exception as e:
        log_err("hooklib.ensure_project_scaffold", e)
        return False


def route_project(cwd):
    """cwd → (folder, is_new). Resolves via project_for(); when the repo is unknown it
    registers the git-root basename as a new project folder and scaffolds it, so a note
    can never land in the vault root. Returns (None, False) when cwd is not a project."""
    if not cwd:
        return None, False
    hit = project_for(cwd)
    if hit:
        ensure_project_scaffold(hit)
        return hit, False
    root = _git_root(cwd) or cwd
    home = os.path.expanduser("~")
    # A home dir that is itself a git repo would otherwise register a junk project
    # named after the user account.
    if os.path.realpath(root) == os.path.realpath(home):
        return None, False
    base = os.path.basename(root.rstrip("/")).lower()
    if (
        not base
        or base in _NON_PROJECT
        or base.startswith(".")
        or base == os.path.basename(home).lower()
    ):
        return None, False
    folder = re.sub(r"[^a-z0-9._-]+", "-", base).strip("-")
    if not folder:
        return None, False
    register_project(folder, base)
    ensure_project_scaffold(folder)
    return folder, True


_HARNESS_RE = re.compile(
    r"<task-notification>|SYSTEM NOTIFICATION|<system-reminder>|<command-name>|<local-command"
)


def real_prompt(s):
    """True for genuine user text; False for harness-injected messages
    (task notifications, system reminders, slash-command preambles)."""
    return bool(s) and not _HARNESS_RE.search(s)



# --- Multi-client hook envelope (Claude snake_case + Grok camelCase) ---
# Grok stdin uses camelCase (sessionId, transcriptPath, stopHookActive, …).
# Claude Code uses snake_case. normalize_hook() writes both so existing readers keep working.

_HOOK_KEY_GROUPS = (
    ("session_id", ("session_id", "sessionId")),
    ("transcript_path", ("transcript_path", "transcriptPath")),
    ("stop_hook_active", ("stop_hook_active", "stopHookActive")),
    ("cwd", ("cwd", "workspaceRoot", "workspace_root")),
    ("gitBranch", ("gitBranch", "git_branch")),
    ("prompt", ("prompt",)),
    ("source", ("source",)),
    ("reason", ("reason",)),
    ("tool_name", ("tool_name", "toolName")),
    ("tool_input", ("tool_input", "toolInput")),
    ("tool_response", ("tool_response", "toolResult", "tool_result")),
    ("last_assistant_message", ("last_assistant_message", "lastAssistantMessage")),
    ("hook_event_name", ("hook_event_name", "hookEventName")),
)


def _first_key(d, keys):
    for k in keys:
        if k in d and d[k] not in (None, ""):
            return d[k]
    return None


def normalize_hook(hook):
    """Return a shallow copy of the hook dict with dual-case aliases filled in.
    Never raises; bad input → {}."""
    if not isinstance(hook, dict):
        return {}
    out = dict(hook)
    for canon, keys in _HOOK_KEY_GROUPS:
        val = _first_key(out, keys)
        if val is None:
            continue
        for k in keys:
            out.setdefault(k, val)
        out[canon] = val
    # Grok often has workspaceRoot but not cwd — ensure cwd is set for project_for()
    if not out.get("cwd"):
        wr = out.get("workspaceRoot") or out.get("workspace_root")
        if wr:
            out["cwd"] = wr
    return out


def emit_hook_context(text, event_name=None):
    """Write hook → model context. Claude Code injects plain stdout on SessionStart /
    UserPromptSubmit. Grok docs ignore passive stdout; it may honor Claude-compatible
    hookSpecificOutput.additionalContext. Always also write a side-channel file under
    the vault when GROK_SESSION_ID is set so AGENTS can force a read.
    Never raises."""
    if not text:
        return
    text = text if text.endswith("\n") else text + "\n"
    is_grok = bool(
        os.environ.get("GROK_SESSION_ID")
        or os.environ.get("GROK_HOOK_EVENT")
        or (event_name and "grok" in (event_name or "").lower())
    )
    # Detect Grok from envelope field names left in env by runner
    try:
        # Side-channel for model-compliance fallback
        sid = os.environ.get("GROK_SESSION_ID") or os.environ.get("CLAUDE_SESSION_ID") or ""
        if sid and vault_ok():
            inj = os.path.join(MEM, ".grok-inject")
            os.makedirs(inj, exist_ok=True)
            safe = re.sub(r"[^A-Za-z0-9_-]", "_", sid)[:64] or "nosession"
            atomic_write(os.path.join(inj, safe + ".md"), text)
    except Exception as e:
        log_err("emit_hook_context.sidechannel", e)
    try:
        if is_grok or os.environ.get("GROK_SESSION_ID"):
            ev = (
                event_name
                or os.environ.get("GROK_HOOK_EVENT")
                or "UserPromptSubmit"
            )
            # Normalize env form session_start → SessionStart-ish for Claude compat
            ev_map = {
                "session_start": "SessionStart",
                "user_prompt_submit": "UserPromptSubmit",
                "stop": "Stop",
            }
            ev = ev_map.get(ev, ev)
            if ev and ev[0].islower():
                # session_start already mapped; leave Pascal if already
                pass
            payload = {
                "hookSpecificOutput": {
                    "hookEventName": ev if ev[0].isupper() or ev in (
                        "SessionStart", "UserPromptSubmit", "Stop"
                    ) else ev,
                    "additionalContext": text.rstrip("\n"),
                }
            }
            # Prefer PascalCase event names Grok docs use
            he = payload["hookSpecificOutput"]["hookEventName"]
            if he == "session_start":
                payload["hookSpecificOutput"]["hookEventName"] = "SessionStart"
            elif he == "user_prompt_submit":
                payload["hookSpecificOutput"]["hookEventName"] = "UserPromptSubmit"
            sys.stdout.write(json.dumps(payload) + "\n")
        else:
            sys.stdout.write(text)
        sys.stdout.flush()
    except Exception as e:
        log_err("emit_hook_context", e)
        try:
            sys.stdout.write(text)
        except Exception:
            pass


# Tool names that mean "file write/edit" across Claude Code and Grok
_FILE_EDIT_TOOLS = frozenset({
    "Edit", "Write", "NotebookEdit", "MultiEdit",
    "search_replace", "write",  # Grok; write tool rare but possible
})
_BASH_TOOLS = frozenset({"Bash", "run_terminal_command"})


def _content_blocks(o):
    """Return content blocks from a Claude (message.content) or Grok (top-level content) row."""
    msg = o.get("message") or {}
    c = msg.get("content") if msg else None
    if c is None:
        c = o.get("content")
    return c


def _tool_calls_from_row(o, c):
    """Yield (name, input_dict) from Claude tool_use blocks or Grok tool_calls."""
    if isinstance(c, list):
        for b in c:
            if not isinstance(b, dict):
                continue
            if b.get("type") == "tool_use":
                yield b.get("name", ""), b.get("input") or {}
    # Grok: top-level tool_calls: [{name, arguments: json-str|dict}]
    for tc in o.get("tool_calls") or []:
        if not isinstance(tc, dict):
            continue
        name = tc.get("name") or ""
        args = tc.get("arguments") or tc.get("input") or {}
        if isinstance(args, str):
            try:
                args = json.loads(args)
            except Exception:
                args = {}
        if not isinstance(args, dict):
            args = {}
        yield name, args


def scan_transcript(tpath, max_bytes=1048576):
    """Parse the tail of a session transcript — the single shared parser used by
    capture-exchange, precompact-carryover and context-dump. Skips sidechains and
    harness-injected user messages. Returns a dict:
      last_user, last_asst: str|None — last genuine user prompt / assistant text
      files: ordered-unique file paths from Edit/Write/NotebookEdit/MultiEdit calls
      commands: recent Bash commands (whitespace-collapsed, 160 chars)
      errors: tool_result snippets the harness flagged is_error (200 chars)
    Accepts Claude Code JSONL (type + message.content + tool_use) and Grok
    chat_history.jsonl (top-level content + tool_calls). The 1MB default tail
    matters: with a smaller window one large tool result evicts the user/assistant
    pair and a big turn captures nothing."""
    last_user = last_asst = None
    files, commands, errors = [], [], []
    for ln in tail_lines(tpath, max_bytes=max_bytes):
        ln = ln.strip()
        if not ln:
            continue
        try:
            o = json.loads(ln)
        except Exception:
            continue
        if o.get("isSidechain"):  # skip subagent turns
            continue
        t = o.get("type")
        c = _content_blocks(o)
        if t == "user":
            if isinstance(c, str) and real_prompt(c.strip()):
                last_user = c.strip()
            elif isinstance(c, list):
                for b in c:
                    if not isinstance(b, dict):
                        continue
                    if b.get("type") == "text" and real_prompt(
                        b.get("text", "").strip()
                    ):
                        last_user = b["text"].strip()
                    elif b.get("type") == "tool_result" and b.get("is_error"):
                        rc = b.get("content")
                        txt = (
                            rc
                            if isinstance(rc, str)
                            else (
                                " ".join(
                                    x.get("text", "") for x in rc if isinstance(x, dict)
                                )
                                if isinstance(rc, list)
                                else ""
                            )
                        )
                        s = re.sub(r"\s+", " ", txt).strip()
                        if s:
                            errors.append(s[:200])
        elif t == "tool_result":
            # Grok (and some Claude shapes): tool results as top-level rows
            if o.get("is_error") or o.get("isError"):
                rc = c if c is not None else o.get("result") or o.get("output")
                txt = rc if isinstance(rc, str) else (
                    " ".join(x.get("text", "") for x in rc if isinstance(x, dict))
                    if isinstance(rc, list) else str(rc or "")
                )
                s = re.sub(r"\s+", " ", txt).strip()
                if s:
                    errors.append(s[:200])
        elif t == "assistant":
            texts = []
            if isinstance(c, str) and c.strip():
                texts.append(c.strip())
            elif isinstance(c, list):
                for b in c:
                    if not isinstance(b, dict):
                        continue
                    if b.get("type") == "text" and b.get("text", "").strip():
                        texts.append(b["text"].strip())
            for name, inp in _tool_calls_from_row(o, c):
                if name in _FILE_EDIT_TOOLS:
                    fp = (
                        inp.get("file_path")
                        or inp.get("notebook_path")
                        or inp.get("path")
                        or inp.get("target_file")
                    )
                    if fp and fp not in files:
                        files.append(fp)
                elif name in _BASH_TOOLS:
                    cmd = (inp.get("command") or "").strip()
                    if cmd:
                        commands.append(re.sub(r"\s+", " ", cmd)[:160])
            if texts:
                last_asst = "\n".join(texts)
    return {
        "last_user": last_user,
        "last_asst": last_asst,
        "files": files,
        "commands": commands,
        "errors": errors,
    }


def tail_lines(path, max_bytes=262144):
    """Return the last ~max_bytes of a (possibly huge) file as a list of complete lines.
    Drops the first partial line. For reading the end of a 20MB+ transcript cheaply."""
    try:
        sz = os.path.getsize(path)
        with open(path, "rb") as f:
            if sz > max_bytes:
                f.seek(sz - max_bytes)
            chunk = f.read()
        text = chunk.decode("utf-8", errors="ignore")
        lines = text.split("\n")
        if sz > max_bytes and len(lines) > 1:
            lines = lines[1:]  # drop partial first line
        return lines
    except Exception:
        return []


# Secret patterns redacted before any raw transcript text is written to the vault.
# Conservative: only high-confidence token shapes, so prose is never mangled.
_SECRET_PATTERNS = [
    r"sk-[A-Za-z0-9_-]{16,}",  # OpenAI / generic sk- keys
    r"sk-ant-[A-Za-z0-9_-]{16,}",  # Anthropic
    r"ghp_[A-Za-z0-9]{20,}",  # GitHub PAT (classic)
    r"github_pat_[A-Za-z0-9_]{20,}",  # GitHub PAT (fine-grained)
    r"gho_[A-Za-z0-9]{20,}",  # GitHub OAuth
    r"xox[baprs]-[A-Za-z0-9-]{10,}",  # Slack
    r"AKIA[0-9A-Z]{16}",  # AWS access key id
    r"AIza[0-9A-Za-z_-]{30,}",  # Google API key
    r"(?:r8_|hf_|pk_live_|sk_live_)[A-Za-z0-9]{16,}",  # Replicate / HF / Stripe live
    r"eyJ[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}",  # JWT
    r"-----BEGIN (?:RSA |EC |OPENSSH |DSA |PGP )?PRIVATE KEY-----",  # private key header
    # KEY=VALUE / "token": "..." shapes with a long opaque value (keyword case-insensitive)
    r"(?i:(?:api[_-]?key|secret|token|password|passwd|bearer))\s*[=:]\s*['\"]?[A-Za-z0-9_\-\.]{16,}",
]
_SECRET_RE = re.compile("|".join(_SECRET_PATTERNS))


def scrub_secrets(text):
    """Redact high-confidence secret token shapes from text before it is written to the
    vault. Returns the scrubbed string (unchanged if nothing matched). Never raises."""
    if not text:
        return text
    try:
        return _SECRET_RE.sub("[REDACTED]", text)
    except Exception:
        return text
