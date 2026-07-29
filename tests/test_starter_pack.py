#!/usr/bin/env python3
"""Tests for the optional starter pack. Stdlib-only, assert-based.
Run: python3 tests/test_starter_pack.py

Covers the two things that break silently: the pack overwriting something the user
already had, and a private reference leaking out of the vendored skills.
"""

import contextlib
import importlib.util
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PACK = os.path.join(REPO, "starter-pack")
SCRIPT = os.path.join(REPO, "skills", "second-brain", "scripts", "starter-pack.py")

_spec = importlib.util.spec_from_file_location("starter_pack", SCRIPT)
sp = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(sp)

TIERS = json.load(open(os.path.join(PACK, "tiers.json")))
MANIFEST = json.load(open(os.path.join(PACK, "manifest.json")))
TIER_NAMES = [t for t in TIERS if not t.startswith("_")]
ALL_SKILLS = [s for t in TIER_NAMES for s in TIERS[t]["skills"]]


def fresh():
    """A throwaway config dir + seeded vault. Returns (claude_dir, vault)."""
    root = tempfile.mkdtemp(prefix="pack-test-")
    claude = os.path.join(root, ".claude")
    vault = os.path.join(claude, "vault")
    os.makedirs(os.path.join(claude, "skills"))
    shutil.copytree(os.path.join(REPO, "vault-template"), vault)
    return claude, vault


def run(claude, vault, *args):
    """Invoke the installer in-process, with the module's globals pointed at the temp dirs.
    Its progress output is swallowed so the suite's own pass/fail lines stay readable."""
    sp.CLAUDE = claude
    with open(os.devnull, "w") as devnull, contextlib.redirect_stdout(devnull):
        return sp.main(["--source", PACK, "--vault", vault, *args])


# --- 1. the pack manifest and the files on disk agree ------------------------
def test_tiers_match_disk():
    on_disk = {
        d
        for d in os.listdir(os.path.join(PACK, "skills"))
        if os.path.isdir(os.path.join(PACK, "skills", d))
    }
    assert set(ALL_SKILLS) == on_disk, (
        f"tiers.json vs disk: {set(ALL_SKILLS) ^ on_disk}"
    )
    assert len(ALL_SKILLS) == len(set(ALL_SKILLS)), "a skill is listed in two tiers"
    for s in ALL_SKILLS:
        assert os.path.isfile(os.path.join(PACK, "skills", s, "SKILL.md")), (
            f"{s} has no SKILL.md"
        )
    for t in TIER_NAMES:
        for w in TIERS[t].get("workflows", []):
            assert os.path.isfile(os.path.join(PACK, "workflows", w)), (
                f"missing workflow {w}"
            )


def test_manifest_is_complete():
    for name, p in MANIFEST.items():
        if name.startswith("_"):
            continue
        assert p.get("source", "").startswith("https://"), (
            f"{name}: no verifiable source"
        )
        assert p.get("install"), f"{name}: no install commands"
        for dep in p.get("required_by", []):
            assert dep in ALL_SKILLS, (
                f"{name} claims {dep}, which the pack does not ship"
            )


# --- 2. no private references survived the genericisation --------------------
def test_no_private_references():
    """The vendored skills came from a private setup. This is the guard that keeps
    a re-vendored copy from shipping someone's project names or vault links."""
    banned = re.compile(
        r"\[\[|/Users/|delta-design|delta-voice|Delta Exchange|drishti|tatkaal|lakshay"
        r"|Stratzy|quality-judge|writing-nudge|interview-nudge|\bck\b",
        re.I,
    )
    hits = []
    for root, _d, files in os.walk(os.path.join(PACK, "skills")):
        for f in files:
            if not f.endswith(".md"):
                continue
            p = os.path.join(root, f)
            for i, line in enumerate(open(p, errors="ignore"), 1):
                if banned.search(line):
                    hits.append(f"{os.path.relpath(p, PACK)}:{i}")
    assert not hits, "private references in the shipped pack: " + ", ".join(hits[:8])


# --- 3. tier selection ------------------------------------------------------
def test_parse_tiers():
    assert sp.parse_tiers("all", TIERS) == TIER_NAMES
    assert sp.parse_tiers("core", TIERS) == ["core"]
    assert sp.parse_tiers("core,writing", TIERS) == ["core", "writing"]
    assert sp.parse_tiers("writing,core", TIERS) == ["core", "writing"], (
        "order follows tiers.json"
    )
    assert sp.parse_tiers("", TIERS) == []
    assert sp.parse_tiers("nonsense", TIERS) == []


# --- 4. installing ----------------------------------------------------------
def test_dry_run_writes_nothing():
    claude, vault = fresh()
    before = sorted(os.listdir(os.path.join(claude, "skills")))
    run(claude, vault, "--tiers", "all", "--dry-run")
    assert sorted(os.listdir(os.path.join(claude, "skills"))) == before
    assert not os.path.exists(os.path.join(vault, ".obsidian"))
    assert not os.path.exists(os.path.join(vault, "_playbook"))


def test_one_tier_installs_only_that_tier():
    claude, vault = fresh()
    run(claude, vault, "--tiers", "core")
    got = set(os.listdir(os.path.join(claude, "skills")))
    assert set(TIERS["core"]["skills"]) <= got
    assert not (set(TIERS["design"]["skills"]) & got), (
        "design tier leaked into a core install"
    )
    assert os.path.isfile(os.path.join(claude, "workflows", "vault-restructure.js"))


def test_vault_content_and_obsidian():
    claude, vault = fresh()
    run(claude, vault, "--tiers", "core")
    for rel in (
        "_playbook/_MOC-playbook.md",
        "_playbook/session-habits.md",
        "_templates/note.md",
    ):
        assert os.path.isfile(os.path.join(vault, rel)), f"missing {rel}"
    obs = os.path.join(vault, ".obsidian")
    assert os.path.isfile(os.path.join(obs, "graph.json"))
    graph = json.load(open(os.path.join(obs, "graph.json")))
    assert graph["colorGroups"], "graph config has no colour groups"
    # core plugins only: a community-plugins list would break the no-plugins promise
    assert not os.path.exists(os.path.join(obs, "community-plugins.json"))
    assert "_MOC-playbook" in open(os.path.join(vault, "_Home.md")).read()


def test_never_overwrites():
    claude, vault = fresh()
    # a skill the user already has, under a name the pack also ships
    mine = os.path.join(claude, "skills", "discovery")
    os.makedirs(mine)
    open(os.path.join(mine, "SKILL.md"), "w").write("MINE, DO NOT TOUCH\n")
    # a vault note and an Obsidian config the user already has
    os.makedirs(os.path.join(vault, "_playbook"), exist_ok=True)
    open(os.path.join(vault, "_playbook", "session-habits.md"), "w").write("MY NOTE\n")
    os.makedirs(os.path.join(vault, ".obsidian"))
    open(os.path.join(vault, ".obsidian", "app.json"), "w").write("{}\n")

    run(claude, vault, "--tiers", "all")
    assert open(os.path.join(mine, "SKILL.md")).read() == "MINE, DO NOT TOUCH\n"
    assert (
        open(os.path.join(vault, "_playbook", "session-habits.md")).read()
        == "MY NOTE\n"
    )
    assert open(os.path.join(vault, ".obsidian", "app.json")).read() == "{}\n"
    assert not os.path.exists(os.path.join(vault, ".obsidian", "graph.json")), (
        "an existing .obsidian must be left whole, not merged into"
    )


def test_rerun_is_a_noop():
    claude, vault = fresh()
    run(claude, vault, "--tiers", "all")
    stamp = {
        p: os.path.getmtime(os.path.join(claude, "skills", p))
        for p in os.listdir(os.path.join(claude, "skills"))
    }
    home_before = open(os.path.join(vault, "_Home.md")).read()
    run(claude, vault, "--tiers", "all")
    after = {
        p: os.path.getmtime(os.path.join(claude, "skills", p))
        for p in os.listdir(os.path.join(claude, "skills"))
    }
    assert stamp == after, "a re-run rewrote something"
    home_after = open(os.path.join(vault, "_Home.md")).read()
    assert home_after == home_before, "_Home.md gained a second playbook link"
    assert home_after.count("_MOC-playbook") == 1


def test_records_paths_for_uninstall():
    claude, vault = fresh()
    run(claude, vault, "--tiers", "core")
    man = json.load(open(os.path.join(vault, "_infra", "_install-manifest.json")))
    dirs = set(man["dirs"])
    for s in TIERS["core"]["skills"]:
        assert os.path.join(claude, "skills", s) in dirs, (
            f"{s} not recorded for uninstall"
        )
    assert any(w.endswith("vault-restructure.js") for w in man["workflows"])


def test_list_needs_no_vault():
    """--list must work from a clone with nothing installed."""
    out = subprocess.run(
        [sys.executable, SCRIPT, "--list", "--source", PACK],
        capture_output=True,
        text=True,
        timeout=60,
    )
    assert out.returncode == 0, out.stderr
    assert "gstack" in out.stdout and "garrytan" in out.stdout
    for t in TIER_NAMES:
        assert t in out.stdout


if __name__ == "__main__":
    failed = 0
    for name, fn in sorted(globals().items()):
        if not name.startswith("test_") or not callable(fn):
            continue
        try:
            fn()
            print(f"  ok   {name}")
        except AssertionError as e:
            failed += 1
            print(f"  FAIL {name}: {e}")
        except Exception as e:  # noqa: BLE001 — report, do not stop the suite
            failed += 1
            print(f"  ERR  {name}: {type(e).__name__}: {e}")
    print(f"\n{'FAILED' if failed else 'all passed'} ({failed} failure(s))")
    sys.exit(1 if failed else 0)
