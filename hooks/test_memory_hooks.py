#!/usr/bin/env python3
"""Tests for the memory hooks (project mapping, junk filter, recall scoring, smoke).
Stdlib-only, assert-based. Run: python3 hooks/test_memory_hooks.py
Sets up a throwaway fixture vault + config.json BEFORE importing _hooklib (config is
read at import), so project_for() is exercised against a known generic map."""

import os, sys, json, subprocess, tempfile, importlib.util

# --- fixture vault + config, wired via $CLAUDE_MEMORY_DIR before _hooklib loads ---
_VAULT = tempfile.mkdtemp(prefix="sb-test-vault-")
for _d in ("Daily", "Sessions", "_infra"):
    os.makedirs(os.path.join(_VAULT, _d), exist_ok=True)
with open(os.path.join(_VAULT, "config.json"), "w") as _f:
    json.dump(
        {
            "project_map": {"widgets": "widgets", "acme-web": "acme"},
            "project_prefixes": {"corp-": "corp", "acme-": "acme"},
        },
        _f,
    )
with open(os.path.join(_VAULT, "MEMORY.md"), "w") as _f:
    _f.write("# MEMORY\n")
os.environ["CLAUDE_MEMORY_DIR"] = _VAULT

HOOKS = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HOOKS)
import _hooklib as HL


def _load(name, fname):
    """Import a dashed-filename hook (e.g. session-resume.py) as a module."""
    spec = importlib.util.spec_from_file_location(name, os.path.join(HOOKS, fname))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


session_resume = _load("session_resume", "session-resume.py")


def test_project_for_exact():
    assert HL.project_for("/home/u/code/widgets") == "widgets"
    assert HL.project_for("/x/y/acme-web/") == "acme"
    assert HL.project_for("widgets") == "widgets"  # bare basename


def test_project_for_prefix():
    assert HL.project_for("/repos/corp-mcp-docs") == "corp"
    assert HL.project_for("/x/acme-anything") == "acme"


def test_project_for_unknown():
    assert HL.project_for("") is None
    assert HL.project_for(None) is None
    assert HL.project_for("/tmp/some-random-repo-xyz") is None


def test_project_for_git_root_fallback():
    """A subdir/worktree of a known repo resolves via git top-level basename."""
    base = tempfile.mkdtemp()
    repo = os.path.join(base, "widgets")  # basename is in the map
    sub = os.path.join(repo, "src", "deep")
    os.makedirs(sub)
    subprocess.run(["git", "-C", repo, "init", "-q"], check=True)
    # from a deep subdir, basename("deep") is unknown -> git-root fallback finds "widgets"
    assert HL.project_for(sub) == "widgets"
    # a git repo whose name isn't in the map still returns None
    other = os.path.join(base, "unknownrepo")
    os.makedirs(other)
    subprocess.run(["git", "-C", other, "init", "-q"], check=True)
    assert HL.project_for(other) is None


def test_is_junk():
    assert session_resume._is_junk("- **12:53** [x] — (raw) [Image: source: /p.png]")
    assert session_resume._is_junk("- **11:46** [y] — (raw) https://foo")
    assert not session_resume._is_junk(
        "- **19:44** [widgets] — (win) Shipped remix workshop"
    )
    assert not session_resume._is_junk(
        "- **10:00** [acme] — (decision) rolled back v32"
    )


def test_body_extra_formula():
    """body_extra = keywords in body but NOT already counted in name/desc."""

    def words(s):
        import re

        return set(re.findall(r"[a-z0-9]{3,}", s.lower()))

    kw = {"expiry", "winrate", "widgets", "regime"}
    hit_name = kw & words("widgets winrate workstream")  # {widgets, winrate}
    hit_desc = kw & words("path to target regime capped")  # {regime}
    head = "widgets winrate ... expiry brackets ... regime era"
    body_extra = (kw & words(head)) - hit_name - hit_desc
    assert body_extra == {"expiry"}  # only the body-only keyword survives
    score = 5 * len(hit_name) + 3 * len(hit_desc) + 1 * len(body_extra)
    assert score == 5 * 2 + 3 * 1 + 1 * 1 == 14


def _run_hook(script, payload):
    p = subprocess.run(
        [sys.executable, os.path.join(HOOKS, script)],
        input=json.dumps(payload),
        capture_output=True,
        text=True,
        timeout=30,
    )
    return p.returncode, p.stdout, p.stderr


def test_session_resume_smoke_no_raw():
    rc, out, err = _run_hook(
        "session-resume.py", {"source": "startup", "cwd": "/home/u/code/widgets"}
    )
    assert rc == 0, err
    # raw/image junk must not appear in the resume digest
    assert "(raw)" not in out, "raw capture leaked into resume"
    assert "[Image:" not in out, "image capture leaked into resume"
    assert "resume" in out


def test_memory_recall_smoke():
    rc, out, err = _run_hook(
        "memory-recall.py",
        {
            "prompt": "widgets winrate expiry regime selectivity",
            "cwd": "/home/u/code/widgets",
            "session_id": "test-smoke",
        },
    )
    assert rc == 0, err
    assert "memory:" in out  # always-on stats line


def main():
    tests = [v for k, v in sorted(globals().items()) if k.startswith("test_")]
    passed = 0
    for t in tests:
        t()
        print(f"  ok  {t.__name__}")
        passed += 1
    print(f"\n{passed}/{len(tests)} passed")


if __name__ == "__main__":
    main()
