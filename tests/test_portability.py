#!/usr/bin/env python3
"""Portability guards. Stdlib-only, assert-based.
Run: python3 tests/test_portability.py

These are the Windows failures that reached CI once and must not again:
a status glyph printed to a cp1252 console, a hook that only exists as bash, and a
registration that shells out to bash.
"""

import os
import pathlib
import re
import subprocess
import sys

REPO = pathlib.Path(__file__).resolve().parent.parent
HOOKS = REPO / "hooks"
SCRIPTS = REPO / "skills/second-brain/scripts"
GUARD = '_stream.reconfigure(encoding="utf-8"'

sys.path.insert(0, str(SCRIPTS))


def entry_points():
    """Every file a user or a hook registration can invoke directly."""
    return [
        p for p in sorted(HOOKS.glob("*.py")) if not p.name.startswith("test_")
    ] + sorted(SCRIPTS.glob("*.py"))


def test_every_entry_point_survives_a_cp1252_console():
    """Windows consoles default to cp1252. Any file that prints a glyph without the
    UTF-8 guard dies mid-run there, which is how the manifest went unwritten."""
    missing = []
    for p in entry_points():
        text = p.read_text()
        if GUARD in text:
            continue
        if re.search(r"[^\x00-\x7F]", text):
            missing.append(p.relative_to(REPO).as_posix())
    assert not missing, "non-ASCII output without the UTF-8 guard: " + ", ".join(
        missing
    )


def test_hook_commands_force_utf8_mode():
    """Hooks read vault notes. Without -X utf8 a Windows open() uses cp1252 and raises
    on the first emoji, which is how the pack install died mid-run."""
    import importlib.util

    spec = importlib.util.spec_from_file_location("rh2", SCRIPTS / "register-hooks.py")
    rh = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(rh)
    frag = rh.build("/h", "/usr/bin/python3")
    for ev in frag.values():
        for e in ev:
            for h in e["hooks"]:
                assert "-X utf8" in h["command"], h["command"]


def test_entry_points_reexec_into_utf8_mode_on_windows():
    """Scripts a user runs by hand get the same protection as the registered hooks."""
    missing = []
    for p in entry_points():
        text = p.read_text()
        if "SB_UTF8_REEXEC" not in text:
            missing.append(p.relative_to(REPO).as_posix())
    assert not missing, "no UTF-8 re-exec guard: " + ", ".join(missing)


def test_the_reexec_never_fires_from_an_imported_module():
    """_hooklib is imported by every hook. A re-exec there would relaunch the library
    as a script instead of the hook."""
    for p in entry_points():
        text = p.read_text()
        if "SB_UTF8_REEXEC" not in text:
            continue
        assert '__name__ == "__main__"  # never re-exec when imported' in text, (
            f"{p.name} re-execs without a __main__ guard"
        )


def test_no_os_execv_anywhere():
    """os.execv does not replace the process on Windows: the parent exits with its own
    status while the child runs on, so callers read the wrong exit code. CI failed on
    exactly that. Re-exec through subprocess and propagate the child's code."""
    offenders = []
    for p in entry_points():
        if "os.execv" in p.read_text():
            offenders.append(p.relative_to(REPO).as_posix())
    assert not offenders, "os.execv is unreliable on Windows: " + ", ".join(offenders)


def test_glyph_print_would_have_failed_without_the_guard():
    """Proves the guard is load-bearing rather than decorative."""
    out = subprocess.run(
        [sys.executable, "-c", "print('\u2713')"],
        env=dict(os.environ, PYTHONIOENCODING="cp1252"),
        capture_output=True,
        text=True,
    )
    assert out.returncode != 0 and "UnicodeEncodeError" in out.stderr, (
        "cp1252 no longer rejects the glyph; this test needs rewriting"
    )


def test_registered_hooks_all_have_a_python_file():
    """A hook registered but shipped only as bash cannot run on Windows."""
    import importlib.util

    spec = importlib.util.spec_from_file_location("rh", SCRIPTS / "register-hooks.py")
    rh = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(rh)
    for name in rh.OURS:
        assert (HOOKS / f"{name}.py").is_file(), f"{name} is registered but has no .py"
    frag = rh.build(r"C:\h", r"C:\python.exe")
    cmds = [h["command"] for ev in frag.values() for e in ev for h in e["hooks"]]
    assert len(cmds) == len(rh.OURS)
    assert not [c for c in cmds if "bash" in c], (
        "a registration still shells out to bash"
    )
    assert all(c.startswith('"C:\\python.exe"') for c in cmds), cmds[0]


def test_no_posix_only_popen_arguments():
    """start_new_session is POSIX-only; background launches must go through
    _hooklib.detach_kwargs() so Windows gets the equivalent creation flag."""
    offenders = []
    for p in entry_points():
        if p.name == "_hooklib.py":
            continue
        if "start_new_session" in p.read_text():
            offenders.append(p.relative_to(REPO).as_posix())
    assert not offenders, "raw start_new_session outside _hooklib: " + ", ".join(
        offenders
    )


def test_no_hardcoded_path_separators_in_vault_walks():
    """Folder names come from splitting a relative path, which must use os.sep."""
    offenders = []
    for p in entry_points():
        for i, line in enumerate(p.read_text().splitlines(), 1):
            if re.search(r"relpath\([^)]*\)\.split\(\s*[\"']/[\"']\s*\)", line):
                offenders.append(f"{p.relative_to(REPO).as_posix()}:{i}")
    assert not offenders, "split on a literal slash: " + ", ".join(offenders)


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
