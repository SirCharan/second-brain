#!/usr/bin/env python3
"""Tests for project routing/scaffold, note debt, and the large-task nudge. Stdlib-only, assert-based.
Run: python3 hooks/test_enforcement.py"""

import importlib
import json
import os
import subprocess
import sys
import tempfile

HOOKS = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HOOKS)

_VAULT = tempfile.mkdtemp(prefix="enf-test-vault-")
for _d in ("Daily", "Sessions", "_infra"):
    os.makedirs(os.path.join(_VAULT, _d), exist_ok=True)
with open(os.path.join(_VAULT, "config.json"), "w", encoding="utf-8") as _f:
    json.dump({"project_map": {"widgets": "widgets"}}, _f)
os.environ["CLAUDE_MEMORY_DIR"] = _VAULT

import _hooklib as HL


def _bind():
    """Re-point _hooklib at THIS module's fixture vault. MEM/CONFIG freeze at import,
    and under a combined pytest run another test module may have bound it to its own
    vault, so every vault-dependent test rebinds first."""
    global HL
    os.environ["CLAUDE_MEMORY_DIR"] = _VAULT
    HL = importlib.reload(HL)
    return HL


_bind()


def _run(script, payload, env=None):
    e = dict(os.environ, CLAUDE_MEMORY_DIR=_VAULT)
    e.update(env or {})
    p = subprocess.run(
        [sys.executable, os.path.join(HOOKS, script)],
        input=json.dumps(payload),
        capture_output=True,
        text=True,
        env=e,
        timeout=30,
    )
    return p.returncode, p.stdout, p.stderr


# ---------------------------------------------------------------- routing + scaffold
def test_moc_name_strips_meta_underscore():
    _bind()
    assert HL.moc_name("widgets") == "_MOC-widgets"
    assert HL.moc_name("_infra") == "_MOC-infra"  # matches existing vault links


def test_route_known_project_does_not_reregister():
    _bind()
    folder, is_new = HL.route_project("/x/y/widgets")
    assert folder == "widgets" and is_new is False
    cfg = json.load(open(os.path.join(_VAULT, "config.json"), encoding="utf-8"))
    assert list(cfg["project_map"]) == ["widgets"], "known repo must not add an entry"


def test_route_unknown_repo_registers_and_scaffolds():
    _bind()
    repo = tempfile.mkdtemp(prefix="brand-new-")
    base = os.path.basename(repo).lower()
    folder, is_new = HL.route_project(repo)
    assert is_new is True and folder == base
    assert os.path.isdir(os.path.join(_VAULT, folder)), "project folder not created"
    hub = os.path.join(_VAULT, folder, HL.moc_name(folder) + ".md")
    assert os.path.exists(hub), "hub not created"
    t = open(hub, encoding="utf-8").read()
    for req in ("name:", "status:", "# ", "## Related", "[[_Home]]"):
        assert req in t, f"hub missing {req!r}"
    cfg = json.load(open(os.path.join(_VAULT, "config.json"), encoding="utf-8"))
    assert cfg["project_map"][base] == folder, "config.json not updated"


def test_scaffold_is_idempotent():
    _bind()
    HL.ensure_project_scaffold("widgets")
    hub = os.path.join(_VAULT, "widgets", "_MOC-widgets.md")
    open(hub, "a", encoding="utf-8").write("\nhand-edited marker\n")
    assert HL.ensure_project_scaffold("widgets") is False, "must not recreate"
    assert "hand-edited marker" in open(hub, encoding="utf-8").read(), "clobbered an existing hub"


def test_route_refuses_non_project_dirs():
    _bind()
    for d in (os.path.expanduser("~"), "/tmp", os.path.expanduser("~/Desktop")):
        folder, _ = HL.route_project(d)
        assert folder is None, f"{d} must not become a project folder"


# ---------------------------------------------------------------- note debt
def _transcript(tool_files, text="done"):
    tp = tempfile.mktemp(suffix=".jsonl")
    blocks = [
        {"type": "tool_use", "name": "Edit", "input": {"file_path": f}}
        for f in tool_files
    ] + [{"type": "text", "text": text}]
    turns = [
        {"type": "user", "message": {"role": "user", "content": "do the thing"}},
        {"type": "assistant", "message": {"content": blocks}},
    ]
    open(tp, "w", encoding="utf-8").write("\n".join(json.dumps(t) for t in turns) + "\n")
    return tp


def test_note_debt_raised_then_cleared():
    _bind()
    HL.ensure_project_scaffold("widgets")  # order-independent
    debt = os.path.join(_VAULT, "_infra", "_note-debt.md")
    repo = os.path.join(_VAULT, "..", "widgets-repo")
    # code edited, no vault write -> debt
    tp = _transcript(["/code/widgets/app.py"])
    rc, _, err = _run(
        "capture-exchange.py",
        {"transcript_path": tp, "cwd": "/x/y/widgets", "session_id": "debtsid1"},
    )
    assert rc == 0, err
    assert "debtsid1"[:8] in open(debt, encoding="utf-8").read(), "debt not recorded"

    # a curated note lands in the folder -> debt clears
    note = os.path.join(_VAULT, "widgets", "widgets-thing.md")
    open(note, "w", encoding="utf-8").write("---\nname: widgets-thing\nstatus: active\n---\n# T\n")
    tp2 = _transcript([note])
    rc, _, err = _run(
        "capture-exchange.py",
        {"transcript_path": tp2, "cwd": "/x/y/widgets", "session_id": "debtsid1"},
    )
    assert rc == 0, err
    open_rows = [l for l in open(debt, encoding="utf-8") if l.startswith("- [ ] ")]
    assert not open_rows, f"debt should be cleared, still: {open_rows}"


def test_no_debt_when_only_vault_touched():
    _bind()
    HL.ensure_project_scaffold("widgets")  # order-independent
    debt = os.path.join(_VAULT, "_infra", "_note-debt.md")
    note = os.path.join(_VAULT, "widgets", "widgets-only.md")
    open(note, "w", encoding="utf-8").write("---\nname: widgets-only\nstatus: active\n---\n# T\n")
    tp = _transcript([note])
    _run(
        "capture-exchange.py",
        {"transcript_path": tp, "cwd": "/x/y/widgets", "session_id": "vaultonly"},
    )
    # the file may legitimately not exist yet — a vault with no debt writes none
    have = open(debt, encoding="utf-8").read() if os.path.exists(debt) else ""
    assert "vaultonly" not in have, "note-only session owes nothing"





# ---------------------------------------------------------------- large-task nudge
def test_interview_nudge_names_plan_mode_and_ultracode():
    big = (
        "build a complete new analytics platform with dashboards, a data pipeline, "
        "auth and a marketing site. It must scale to many users, integrate with the "
        "existing systems, and ship with tests and monitoring across every service."
    )
    rc, out, _ = _run("interview-nudge.py", {"prompt": big})
    assert rc == 0
    low = out.lower()
    assert "askuserquestion" in low, "must demand the interview"
    assert "plan mode" in low, "must name plan mode"
    assert "ultracode" in low, "must offer ultracode on a large task"


def test_interview_nudge_silent_on_trivial():
    rc, out, _ = _run("interview-nudge.py", {"prompt": "hi"})
    assert rc == 0 and not out.strip(), "trivial prompt must stay silent"


def main():
    tests = [v for k, v in sorted(globals().items()) if k.startswith("test_")]
    for t in tests:
        t()
        print(f"  ok  {t.__name__}")
    print(f"\n{len(tests)}/{len(tests)} passed")


if __name__ == "__main__":
    main()
