#!/usr/bin/env python3
"""Shared helpers for the memory hooks. Python 3.9-safe, stdlib-only.
Import works because Python puts the running script's dir on sys.path[0]."""

import os, re, tempfile, time, traceback

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
EMBED_VENV_PY = os.path.join(STATE_DIR, "venv-embed", "bin", "python")


def embed_ready():
    """True only if the optional semantic-embed venv + script both exist."""
    return os.path.isfile(EMBED_VENV_PY) and os.path.isfile(EMBED_SCRIPT)


def load_config():
    """Read the vault's config.json (project map, domains, ignore lists, project
    metadata). Missing/broken file → empty dict, so everything degrades to generic
    auto-defaults. Never raises."""
    import json

    try:
        with open(os.path.join(MEM, "config.json"), errors="ignore") as f:
            cfg = json.load(f)
            return cfg if isinstance(cfg, dict) else {}
    except Exception:
        return {}


CONFIG = load_config()


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
        with os.fdopen(fd, "w") as f:
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
        with open(path, errors="ignore") as f:
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
        with open(ERRLOG, "a") as f:
            f.write(line)
        # trim if it grows past ~500 lines
        if os.path.getsize(ERRLOG) > 120_000:
            with open(ERRLOG, errors="ignore") as f:
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
