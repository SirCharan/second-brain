#!/usr/bin/env python3
"""Tests for memory-embed.py pure helpers (no model needed).
Run: python3 ~/.claude/hooks/test_memory_embed.py"""

import os, sys, tempfile, importlib.util

HOOKS = os.path.dirname(os.path.abspath(__file__))


def _load(name, fname):
    spec = importlib.util.spec_from_file_location(name, os.path.join(HOOKS, fname))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


E = _load("memory_embed", "memory-embed.py")


def test_pack_unpack_roundtrip():
    v = [0.1, -2.0, 3.5, 0.0, 42.25]
    out = E.unpack_vec(E.pack_vec(v))
    assert len(out) == len(v)
    for a, b in zip(v, out):
        assert abs(a - b) < 1e-5, (a, b)


def test_cosine():
    assert abs(E.cosine([1, 0, 0], [1, 0, 0]) - 1.0) < 1e-6  # identical
    assert abs(E.cosine([1, 0], [0, 1])) < 1e-6  # orthogonal
    assert E.cosine([1, 0], [-1, 0]) < 0  # opposite
    assert E.cosine([0, 0], [1, 1]) == 0.0  # zero vector safe
    assert E.cosine([1, 1, 0], [2, 2, 0]) > 0.99  # colinear


def test_is_note():
    assert E.is_note("/m/widgets/widgets-v32.md")
    assert not E.is_note("/m/widgets/_MOC-widgets.md")  # underscore
    assert not E.is_note("/m/Daily/2026-07-17.md")  # journal
    assert not E.is_note("/m/x/MEMORY.md")  # excluded index


def test_note_text_strips_frontmatter():
    d = tempfile.mkdtemp()
    p = os.path.join(d, "widgets-expiry-leak.md")
    open(p, "w").write(
        '---\nname: x\ndescription: "the expiry leak note"\ntags: [signals]\n---\n'
        "Body about ATR brackets and expiry.\n"
    )
    t = E.note_text(p)
    assert "widgets expiry leak" in t  # name, dashes->spaces
    assert "the expiry leak note" in t  # description
    assert "ATR brackets" in t  # body
    assert "tags:" not in t  # frontmatter stripped from body slice
    assert "name: x" not in t


def main():
    tests = [v for k, v in sorted(globals().items()) if k.startswith("test_")]
    for t in tests:
        t()
        print(f"  ok  {t.__name__}")
    print(f"\n{len(tests)}/{len(tests)} passed")


if __name__ == "__main__":
    main()
