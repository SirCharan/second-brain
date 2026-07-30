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
with open(os.path.join(_VAULT, "config.json"), "w", encoding="utf-8") as _f:
    json.dump(
        {
            "project_map": {"widgets": "widgets", "acme-web": "acme"},
            "project_prefixes": {"corp-": "corp", "acme-": "acme"},
        },
        _f,
    )
with open(os.path.join(_VAULT, "MEMORY.md"), "w", encoding="utf-8") as _f:
    _f.write("# MEMORY\n")
os.environ["CLAUDE_MEMORY_DIR"] = _VAULT

HOOKS = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HOOKS)
import importlib

import _hooklib as HL


def _bind():
    """Rebind _hooklib to this module's fixture vault. MEM/CONFIG freeze at import, so
    under a combined pytest run another test module may have bound it to its own vault."""
    global HL
    os.environ["CLAUDE_MEMORY_DIR"] = _VAULT
    HL = importlib.reload(HL)
    return HL


_bind()


def _load(name, fname):
    """Import a dashed-filename hook (e.g. session-resume.py) as a module."""
    spec = importlib.util.spec_from_file_location(name, os.path.join(HOOKS, fname))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


session_resume = _load("session_resume", "session-resume.py")


def test_project_for_exact():
    _bind()
    assert HL.project_for("/home/u/code/widgets") == "widgets"
    assert HL.project_for("/x/y/acme-web/") == "acme"
    assert HL.project_for("widgets") == "widgets"  # bare basename


def test_project_for_prefix():
    _bind()
    assert HL.project_for("/repos/corp-mcp-docs") == "corp"
    assert HL.project_for("/x/acme-anything") == "acme"


def test_project_for_unknown():
    _bind()
    assert HL.project_for("") is None
    assert HL.project_for(None) is None
    assert HL.project_for("/tmp/some-random-repo-xyz") is None


def test_project_for_git_root_fallback():
    _bind()
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


def test_backlog_notice_thresholds():
    """Consolidation is the step nothing runs for you, and skipping it silently breaks
    retrieval: recall ranks curated notes and ignores the journal, so an uncurated
    finding is unreachable no matter how faithfully it was captured."""
    _bind()
    sr = session_resume  # loaded via spec, already bound to the fixture vault
    q = os.path.join(_VAULT, "_infra", "_promote-queue.md")
    today = __import__("datetime").date.today()

    def write(n, age_days):
        day = (today - __import__("datetime").timedelta(days=age_days)).isoformat()
        with open(q, "w", encoding="utf-8") as f:
            f.write("# Promote queue\n\n")
            for i in range(n):
                f.write("- [ ] %s 10:0%d — finding %d\n" % (day, i % 10, i))

    # quiet: a small, fresh backlog is normal working state
    write(2, 0)
    assert sr._backlog_notice() is None, "2 fresh items must not nag"

    # count threshold
    write(sr.BACKLOG_MIN, 0)
    n = sr._backlog_notice()
    assert n and "CURATION BACKLOG" in n and str(sr.BACKLOG_MIN) in n

    # age threshold alone is enough, even with a single item
    write(1, sr.BACKLOG_AGE)
    n = sr._backlog_notice()
    assert n and "oldest" in n, "an old single item must still surface"
    assert "1 finding still" in n, "singular wording: %r" % n

    # escalation
    write(sr.BACKLOG_LOUD, 1)
    assert "🚨" in sr._backlog_notice()
    write(sr.BACKLOG_MIN, 1)
    assert "📥" in sr._backlog_notice()

    # a fully checked-off queue is clean, and a missing file is not an error
    with open(q, "w", encoding="utf-8") as f:
        f.write("# Promote queue\n\n- [x] %s — done\n" % today.isoformat())
    assert sr._backlog_notice() is None, "checked-off items are not a backlog"
    os.remove(q)
    assert sr._backlog_notice() is None
    assert sr._consolidation_backlog() == (0, 0)


def test_backlog_notice_survives_truncation():
    """The notice must sit ABOVE the long sections: TOTAL_MAX trims the tail, and this
    is the one line that must not be the thing dropped."""
    _bind()
    sr = session_resume
    today = __import__("datetime").date.today().isoformat()
    os.makedirs(os.path.join(_VAULT, "_infra"), exist_ok=True)
    with open(os.path.join(_VAULT, "_infra", "_promote-queue.md"), "w", encoding="utf-8") as f:
        f.write("# Promote queue\n\n")
        for i in range(sr.BACKLOG_LOUD + 5):
            f.write("- [ ] %s 10:00 — finding %d\n" % (today, i))
    rc, out, err = _run_hook(
        "session-resume.py", {"source": "startup", "cwd": "/home/u/code/widgets"}
    )
    assert rc == 0, err
    assert "CURATION BACKLOG" in out, "backlog notice missing from resume output"
    head = out[: len(out) // 2]
    assert "CURATION BACKLOG" in head, "notice must be in the first half, not the tail"
    os.remove(os.path.join(_VAULT, "_infra", "_promote-queue.md"))


def test_resume_index_prefers_coverage_over_descriptions():
    """A project index too large to inline with descriptions must degrade to bare links
    for EVERY note, not an alphabetical slice — an unlisted note is one the model never
    learns exists, while a missing description is one recall away."""
    lines = [
        "- [[note-%03d]] — %s" % (i, "a fairly long description " * 4)
        for i in range(60)
    ]
    full = "\n".join(lines)

    fits = session_resume._cap_index(lines, len(full) + 10)
    assert fits == full, "an index under budget must be passed through untouched"

    tight = session_resume._cap_index(lines, 2000)
    assert len(tight) <= 2000 + 80, "must respect the budget (plus the notice line)"
    for i in (0, 30, 59):
        assert "[[note-%03d]]" % i in tight, "every note must still be listed"
    assert "a fairly long description" not in tight, (
        "descriptions should be the thing cut"
    )
    assert "all 60 notes listed" in tight

    # so tight that even bare links cannot fit: then it truncates and says so
    crushed = session_resume._cap_index(lines, 120)
    assert "omitted" in crushed, "an unavoidable truncation must be declared"


def test_resume_payload_is_bounded():
    """The sharded index stopped MEMORY.md overflowing; the overflow then moved into
    this hook, which pasted a whole shard and the whole _Home map verbatim."""
    rc, out, err = _run_hook(
        "session-resume.py", {"source": "startup", "cwd": "/home/u/code/widgets"}
    )
    assert rc == 0, err
    assert len(out) <= session_resume.TOTAL_MAX + 200, (
        "resume payload %d chars exceeds TOTAL_MAX %d"
        % (len(out), session_resume.TOTAL_MAX)
    )
    assert session_resume.SHARD_MAX < session_resume.TOTAL_MAX
    assert session_resume.HOME_MAX < session_resume.TOTAL_MAX


def test_resume_cap_keeps_the_terminator():
    """Truncating the tail must not eat the closing marker, or a reader cannot tell a
    trimmed digest from a crashed hook."""
    long_text = "\n".join("line %d" % i for i in range(500))
    capped = session_resume._cap(long_text, 200, "lines")
    assert len(capped) < len(long_text)
    assert "omitted" in capped
    assert not capped.endswith("\n"), "cap should end on a line boundary"


def test_memory_recall_smoke():
    _bind()
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
