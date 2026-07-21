#!/usr/bin/env python3
"""Tests for capture-exchange per-session summary note.
Run: python3 ~/.claude/hooks/test_capture_exchange.py"""

import os, sys, tempfile, importlib.util
from datetime import datetime

HOOKS = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HOOKS)
import _hooklib as HL


def _load(name, fname):
    spec = importlib.util.spec_from_file_location(name, os.path.join(HOOKS, fname))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


CE = _load("capture_exchange", "capture-exchange.py")


def test_session_note_accumulates_and_dedups_links():
    tmp = tempfile.mkdtemp()
    old = HL.MEM
    HL.MEM = tmp
    try:
        now = datetime(2026, 7, 17, 15, 0)
        CE._write_session_note(
            now,
            "sid12345678",
            "widgets",
            "main",
            "(win) did thing one",
            ["note-a", "note-b"],
        )
        now2 = datetime(2026, 7, 17, 15, 5)
        CE._write_session_note(
            now2,
            "sid12345678",
            "widgets",
            "main",
            "(decision) did thing two",
            ["note-b", "note-c"],
        )
        path = os.path.join(tmp, "Sessions", "2026-07-17__sid12345.md")
        assert os.path.exists(path), "session note not written"
        txt = open(path).read()
        # both turns logged
        assert "did thing one" in txt and "did thing two" in txt
        # links deduped: note-b appears once, all three present
        assert txt.count("[[note-b]]") == 1, "link not deduped"
        for l in ("note-a", "note-b", "note-c"):
            assert f"[[{l}]]" in txt, f"missing link {l}"
        # frontmatter + structure
        assert txt.startswith("---\n") and "tags: [meta, type/session]" in txt
        assert "## What this session did" in txt and "## Related" in txt
        # description reflects 2 turns
        assert "2 turns" in txt
        print("  ok  test_session_note_accumulates_and_dedups_links")
    finally:
        HL.MEM = old


def test_session_note_no_links():
    tmp = tempfile.mkdtemp()
    old = HL.MEM
    HL.MEM = tmp
    try:
        CE._write_session_note(
            datetime(2026, 7, 17, 9, 0), "abc", "", "", "(raw) something", []
        )
        path = os.path.join(tmp, "Sessions", "2026-07-17__abc.md")
        txt = open(path).read()
        assert "(no linked notes yet)" in txt
        assert "(no project)" in txt
        print("  ok  test_session_note_no_links")
    finally:
        HL.MEM = old


if __name__ == "__main__":
    test_session_note_accumulates_and_dedups_links()
    test_session_note_no_links()
    print("\n2/2 passed")
