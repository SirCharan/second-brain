#!/usr/bin/env python3
"""register-hooks — write the hook registrations and the install manifest.

Lifted out of install.sh so install.ps1 runs the same logic instead of a second copy
that drifts. Idempotent: re-running replaces our own entries and leaves every other
hook the caller has configured untouched.

    python3 register-hooks.py <settings.json> <vault> <version> [--python PATH] [--unregister]

Hooks are registered as `"<python>" "<hooks-dir>/<name>.py"`, not via the bash `.sh`
wrappers. The wrappers only ever pinned an interpreter and swallowed errors; every
hook .py already catches everything and exits 0, and calling Python directly is the
one form that works on Windows too.
"""

import json
import os
import shutil
import sys
import time

# Windows consoles default to cp1252, where the status glyphs this script prints raise
# UnicodeEncodeError and abort it mid-run. UTF-8 with replacement can never raise.
for _stream in (sys.stdout, sys.stderr):
    if hasattr(_stream, "reconfigure"):
        try:
            _stream.reconfigure(encoding="utf-8", errors="replace")
        except Exception:
            pass

# Every hook we own, by event, with its timeout in seconds. One place, two installers.
HOOKS = {
    "SessionStart": [("session-memory", 8), ("session-resume", 8)],
    "UserPromptSubmit": [
        ("interview-nudge", 10),
        ("memory-recall", 15),
        ("context-monitor", 15),
    ],
    "PostToolUse": [("memory-lint", 5, "Edit|Write"), ("stuck-detector", 5, "Bash")],
    "Stop": [("capture-exchange", 10, "")],
    "PreCompact": [("precompact-carryover", 10)],
}
OURS = tuple(h[0] for entries in HOOKS.values() for h in entries)


def quote(path):
    """Windows paths carry spaces and backslashes; a JSON command string needs both kept."""
    return f'"{path}"'


def build(hooks_dir, python):
    frag = {}
    for event, entries in HOOKS.items():
        out = []
        for entry in entries:
            name, timeout = entry[0], entry[1]
            matcher = entry[2] if len(entry) > 2 else None
            script = os.path.join(hooks_dir, name + ".py")
            hook = {
                "type": "command",
                "command": f"{quote(python)} {quote(script)}",
                "timeout": timeout,
            }
            block = {"hooks": [hook]}
            if matcher is not None:
                block["matcher"] = matcher
            out.append(block)
        frag[event] = out
    return frag


def is_ours(entry):
    return any(o in h.get("command", "") for h in entry.get("hooks", []) for o in OURS)


def main(argv):
    if len(argv) < 3:
        print(__doc__.strip(), file=sys.stderr)
        return 2
    settings, vault, version = argv[0], argv[1], argv[2]
    python = sys.executable
    if "--python" in argv:
        i = argv.index("--python")
        if i + 1 < len(argv):
            python = argv[i + 1]
    unregister = "--unregister" in argv

    claude_dir = os.path.dirname(os.path.abspath(settings))
    hooks_dir = os.path.join(claude_dir, "hooks")

    data, backup = {}, None
    if os.path.exists(settings):
        try:
            with open(settings) as f:
                data = json.load(f)
        except ValueError:
            print(
                f"register-hooks: {settings} is not valid JSON — refusing to touch it.",
                file=sys.stderr,
            )
            return 1
        backup = settings + ".bak"
        shutil.copy2(settings, backup)

    registry = data.setdefault("hooks", {})
    frag = {} if unregister else build(hooks_dir, python)
    for event in set(list(registry) + list(frag)):
        kept = [e for e in registry.get(event, []) if not is_ours(e)]
        merged = kept + frag.get(event, [])
        if merged:
            registry[event] = merged
        else:
            registry.pop(event, None)
    if not registry:
        data.pop("hooks", None)

    tmp = settings + ".tmp"
    with open(tmp, "w") as f:
        json.dump(data, f, indent=2)
        f.write("\n")
    os.replace(tmp, settings)
    print(
        f"  ✓ hooks {'de-registered in' if unregister else 'registered in'} {settings}"
    )
    if unregister:
        return 0

    # Manifest: exactly what this install touched, so uninstall can undo that and no more.
    files = []
    if os.path.isdir(hooks_dir):
        files = sorted(
            os.path.join(hooks_dir, f)
            for f in os.listdir(hooks_dir)
            if f.endswith((".py", ".sh"))
        )
    manifest = {
        "version": version,
        "installed_at": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "claude_dir": claude_dir,
        "vault": vault,
        "python": python,
        "files": files,
        "dirs": [os.path.join(claude_dir, "skills", "second-brain")],
        "workflows": [os.path.join(claude_dir, "workflows", "vault-enrich.js")],
        "settings": settings,
        "settings_backup": backup,
        "hook_events": sorted(HOOKS),
        "hook_names": list(OURS),
    }
    infra = os.path.join(vault, "_infra")
    os.makedirs(infra, exist_ok=True)
    mp = os.path.join(infra, "_install-manifest.json")
    with open(mp, "w") as f:
        json.dump(manifest, f, indent=2)
        f.write("\n")
    print(f"  ✓ manifest written to {mp}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
