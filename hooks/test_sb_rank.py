#!/usr/bin/env python3
"""Tests for sb_rank: the note walk, the mtime index, and the shared ranker.
Stdlib-only, assert-based. Run: python3 hooks/test_sb_rank.py

Builds a throwaway vault BEFORE importing sb_rank, because _hooklib freezes MEM at
import. Covers what the two divergent rankers used to get wrong: notes at the vault
root and in nested folders must both rank, retired notes must never rank, and a
stale index entry must be refreshed rather than served."""

import os, sys, json, time, tempfile, importlib

_VAULT = tempfile.mkdtemp(prefix="sb-rank-vault-")
_STATE = tempfile.mkdtemp(prefix="sb-rank-state-")
os.environ["CLAUDE_MEMORY_DIR"] = _VAULT
os.environ["SECOND_BRAIN_STATE_DIR"] = _STATE

HOOKS = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HOOKS)
import _hooklib as HL
import sb_rank


def _bind():
    """Rebind to this module's fixture vault. MEM freezes at import, so under a
    combined pytest run another module may have bound it elsewhere."""
    global HL, sb_rank
    os.environ["CLAUDE_MEMORY_DIR"] = _VAULT
    os.environ["SECOND_BRAIN_STATE_DIR"] = _STATE
    HL = importlib.reload(HL)
    sb_rank = importlib.reload(sb_rank)
    return sb_rank


def _note(rel, name, desc, body="", status="active", date=None):
    p = os.path.join(_VAULT, rel)
    os.makedirs(os.path.dirname(p) or _VAULT, exist_ok=True)
    date = date or time.strftime("%Y-%m-%d")
    with open(p, "w", encoding="utf-8") as f:
        f.write(
            "---\nname: %s\ndescription: %s\nasserted: %s\nlast_confirmed: %s\n"
            "status: %s\n---\n\n# %s\n\n%s\n"
            % (name, desc, date, date, status, name, body)
        )
    return p


def _setup():
    """Build the fixture vault. Called at IMPORT, not from __main__ — pytest collects
    test functions directly and would otherwise run them against an empty vault."""
    # a root-level note and a deeply nested one — both invisible to the old MCP ranker
    _note("root-level-widget.md", "root-level-widget", "widget cache tuning at root")
    _note(
        "alpha/nested/deep/buried-widget.md",
        "buried-widget",
        "widget cache tuning nested deep",
    )
    _note("alpha/plain-note.md", "plain-note", "unrelated turnip farming guide")
    _note(
        "alpha/retired-widget.md",
        "retired-widget",
        "widget cache tuning but retired",
        status="retired",
    )
    _note("Daily/2026-01-01.md", "journal", "widget cache journal line")
    _note("alpha/_MOC-alpha.md", "_MOC-alpha", "widget cache hub")
    _note(
        "alpha/body-only.md",
        "body-only",
        "nothing in the head here",
        body="widget cache tuning appears only in the body of this note",
    )


_setup()


def test_walk_includes_root_and_nested():
    _bind()
    names = {os.path.splitext(os.path.basename(p))[0] for p in sb_rank.all_notes()}
    assert "root-level-widget" in names, "root-level notes must be walked"
    assert "buried-widget" in names, "nested folders must be walked"
    assert "journal" not in names, "Daily/ is a journal, not a note"
    assert "_MOC-alpha" not in names, "underscore-prefixed files are meta, not notes"


def test_folder_of():
    _bind()
    assert sb_rank.folder_of(os.path.join(_VAULT, "root-level-widget.md")) == ""
    assert sb_rank.folder_of(os.path.join(_VAULT, "alpha", "plain-note.md")) == "alpha"
    assert (
        sb_rank.folder_of(os.path.join(_VAULT, "alpha", "nested", "deep", "x.md"))
        == "alpha"
    )


def test_rank_matches_root_and_nested():
    _bind()
    got = [r["name"] for r in sb_rank.rank("widget cache tuning", limit=10)]
    assert "root-level-widget" in got, got
    assert "buried-widget" in got, got
    assert "plain-note" not in got, got


def test_retired_never_ranks():
    _bind()
    got = [r["name"] for r in sb_rank.rank("widget cache tuning", limit=10)]
    assert "retired-widget" not in got, "retired notes must never be injected"


def test_head_gate_blocks_body_only_match():
    """Documents the current ceiling: a note whose BODY answers the query but whose
    name and description share fewer than HEAD_GATE words is unreachable. When the
    rerank stage lands and the gate goes, this assertion should be inverted."""
    _bind()
    got = [r["name"] for r in sb_rank.rank("widget cache tuning", limit=10)]
    assert "body-only" not in got, got
    loose = [
        r["name"] for r in sb_rank.rank("widget cache tuning", limit=10, head_gate=0)
    ]
    assert "body-only" in loose, "head_gate=0 must let a body-only match through"


def test_project_bias_and_freshness():
    _bind()
    plain = sb_rank.rank("widget cache tuning", limit=10)
    biased = sb_rank.rank("widget cache tuning", project="alpha", limit=10)
    s_plain = {r["name"]: r["score"] for r in plain}
    s_biased = {r["name"]: r["score"] for r in biased}
    assert s_biased["buried-widget"] > s_plain["buried-widget"], (
        "project bias must lift"
    )
    assert s_biased["root-level-widget"] == s_plain["root-level-widget"], (
        "a root note is not in project 'alpha' and must not be lifted"
    )

    old = _note(
        "alpha/ancient-widget.md",
        "ancient-widget",
        "widget cache tuning long ago",
        date="2019-01-01",
    )
    _bind()
    fresh_row = next(
        r
        for r in sb_rank.rank("widget cache tuning", limit=10)
        if r["name"] == "buried-widget"
    )
    old_row = next(
        r
        for r in sb_rank.rank("widget cache tuning", limit=10)
        if r["name"] == "ancient-widget"
    )
    assert old_row["score"] < fresh_row["score"], (
        "a 7-year-old note must decay below a fresh one"
    )
    os.remove(old)


def test_index_written_and_reused():
    _bind()
    sb_rank.rank("widget cache tuning")
    assert os.path.isfile(sb_rank.index_path()), "ranking must persist an index"
    idx = json.load(open(sb_rank.index_path(), encoding="utf-8"))
    assert idx["v"] == sb_rank.INDEX_V
    assert any("buried-widget" in k for k in idx["notes"]), idx["notes"].keys()
    before = os.path.getmtime(sb_rank.index_path())
    time.sleep(0.01)
    sb_rank.rank("widget cache tuning")  # nothing changed on disk
    assert os.path.getmtime(sb_rank.index_path()) == before, (
        "an unchanged vault must not rewrite the index"
    )


def test_index_refreshes_a_changed_note():
    _bind()
    sb_rank.rank("widget cache tuning")  # warm the index
    time.sleep(0.01)  # mtime has sub-second resolution but give it room
    _note("alpha/plain-note.md", "plain-note", "widget cache tuning now relevant")
    got = [r["name"] for r in sb_rank.rank("widget cache tuning", limit=10)]
    assert "plain-note" in got, "an edited note must be re-read, not served stale"
    _note("alpha/plain-note.md", "plain-note", "unrelated turnip farming guide")


def test_index_drops_a_deleted_note():
    _bind()
    p = _note("alpha/temporary.md", "temporary", "widget cache tuning temporary")
    assert "temporary" in [
        r["name"] for r in sb_rank.rank("widget cache tuning", limit=10)
    ]
    os.remove(p)
    got = [r["name"] for r in sb_rank.rank("widget cache tuning", limit=10)]
    assert "temporary" not in got, "a deleted note must leave the index"
    idx = json.load(open(sb_rank.index_path(), encoding="utf-8"))
    assert not any("temporary" in k for k in idx["notes"]), "stale key must be pruned"


def test_broken_index_degrades_to_a_full_read():
    _bind()
    with open(sb_rank.index_path(), "w", encoding="utf-8") as f:
        f.write("{not json at all")
    got = [r["name"] for r in sb_rank.rank("widget cache tuning", limit=10)]
    assert "buried-widget" in got, "a corrupt index must not break recall"


def test_empty_query_ranks_nothing():
    _bind()
    assert sb_rank.rank("") == []
    assert sb_rank.rank("the and or of to") == [], "stopwords alone are not a query"


if __name__ == "__main__":
    fns = [v for k, v in sorted(globals().items()) if k.startswith("test_")]
    for fn in fns:
        fn()
        print("ok  %s" % fn.__name__)
    print("\n%d passed" % len(fns))
