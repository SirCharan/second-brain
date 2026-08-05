#!/usr/bin/env python3
"""Guided setup for a second-brain vault.

Run by install.sh, and re-runnable any time:
    python3 ~/.claude/skills/second-brain/scripts/setup.py

It does the one thing nothing else did: writes a real `project_map` so captures file
themselves under the right project. Without it every note lands in the vault root.

Safe to re-run — it merges into the existing config rather than replacing it.
With no terminal attached (a `curl | bash` pipeline, or CI) it prints the manual
equivalent and exits 0, so an install never hangs waiting for input.

Flags:
  --non-interactive   print the manual steps and exit, even with a TTY
  --vault PATH        operate on this vault instead of $CLAUDE_MEMORY_DIR
  --pack SPEC         install the starter pack without asking: none, core,
                      "core,writing", or all. install.sh passes this through.
  --verify-capture    run only the live first-capture test and exit.
"""

import json
import os
import subprocess
import sys
import time

# Windows defaults to cp1252 for console output AND for open(, encoding="utf-8"), so both printing a status
# glyph and reading a note containing an emoji raise. Interpreter UTF-8 mode fixes both, and
# can only be set at startup, so re-exec into it once when we were not started that way.
if (
    __name__ == "__main__"  # never re-exec when imported as a library
    and os.name == "nt"
    and not sys.flags.utf8_mode
    and not os.environ.get("SB_UTF8_REEXEC")
    and getattr(sys, "frozen", None) is None
):
    # os.execv does not replace the process on Windows: the parent exits immediately with
    # its own status while the child keeps running, so the caller reads the wrong exit
    # code. Re-run synchronously and pass the child's code up. stdin/stdout are inherited,
    # so a hook still receives its JSON payload.
    import subprocess

    os.environ["SB_UTF8_REEXEC"] = "1"
    try:
        sys.exit(
            subprocess.run(
                [sys.executable, "-X", "utf8", os.path.abspath(__file__), *sys.argv[1:]]
            ).returncode
        )
    except OSError:
        pass  # fall through to the stream guard rather than refusing to run
for _stream in (sys.stdout, sys.stderr):
    if hasattr(_stream, "reconfigure"):
        try:
            _stream.reconfigure(encoding="utf-8", errors="replace")
        except Exception:
            pass

MEM = os.environ.get("CLAUDE_MEMORY_DIR") or os.path.expanduser(
    "~/.claude/second-brain-vault"
)
SCAN_DIRS = ["~/code", "~/src", "~/projects", "~/dev", "~/git", "~/repos", "~/work"]
SKIP_NAMES = {
    "node_modules",
    "venv",
    ".venv",
    "build",
    "dist",
    "target",
    "tmp",
    "temp",
    "second-brain-vault",
    ".claude",
}
MAX_REPOS = 40

# Starter-pack menu. Index -> the --tiers value handed to starter-pack.py.
PACK_CHOICES = {
    "1": ("", "none"),
    "2": ("core", "core — process discipline + the vault workflow"),
    "3": ("core,writing", "core + writing — prose routing and the pre-ship grade"),
    "4": ("core,writing,design", "core + writing + design — everything, 22 skills"),
}


def _c(code, s):
    """Colour only when writing to a terminal, so piped output stays clean."""
    return f"\033[{code}m{s}\033[0m" if sys.stdout.isatty() else s


def bold(s):
    return _c("1", s)


def dim(s):
    return _c("2", s)


def find_repos():
    """Git repositories under the usual code roots, plus the current directory.
    One level deep only: deep scans are slow and pick up vendored checkouts."""
    found = {}
    roots = [os.path.expanduser(d) for d in SCAN_DIRS]
    cwd = os.getcwd()
    if os.path.isdir(os.path.join(cwd, ".git")):
        found[os.path.basename(cwd)] = cwd
    for root in roots:
        if not os.path.isdir(root):
            continue
        try:
            entries = sorted(os.listdir(root))
        except OSError:
            continue
        for name in entries:
            if name.startswith(".") or name in SKIP_NAMES:
                continue
            p = os.path.join(root, name)
            if os.path.isdir(os.path.join(p, ".git")):
                found.setdefault(name, p)
            if len(found) >= MAX_REPOS:
                return found
    return found


def load_config(vault):
    p = os.path.join(vault, "config.json")
    try:
        with open(p, encoding="utf-8") as f:
            cfg = json.load(f)
            return cfg if isinstance(cfg, dict) else {}
    except (OSError, ValueError):
        return {}


def save_config(vault, cfg):
    p = os.path.join(vault, "config.json")
    os.makedirs(vault, exist_ok=True)
    tmp = p + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(cfg, f, indent=2)
        f.write("\n")
    os.replace(tmp, p)
    return p


def parse_selection(raw, n):
    """'1,3,5-7' or 'all' or '' -> a set of 1-based indices."""
    raw = raw.strip().lower()
    if raw in ("all", "a", "*"):
        return set(range(1, n + 1))
    if not raw:
        return set()
    out = set()
    for part in raw.replace(" ", ",").split(","):
        if not part:
            continue
        if "-" in part:
            a, _, b = part.partition("-")
            try:
                out.update(range(int(a), int(b) + 1))
            except ValueError:
                continue
        else:
            try:
                out.add(int(part))
            except ValueError:
                continue
    return {i for i in out if 1 <= i <= n}


def _probe(sub, sentinel):
    """Find <layout>/<sub> in both install modes — doctor.py's hooks-dir probe:
    $CLAUDE_PLUGIN_ROOT → repo-relative (plugin layout) → ~/.claude."""
    sd = os.path.dirname(os.path.abspath(__file__))
    claude = os.environ.get("CLAUDE_CONFIG_DIR") or os.path.expanduser("~/.claude")
    cands = [
        (
            os.path.join(os.environ["CLAUDE_PLUGIN_ROOT"], sub)
            if os.environ.get("CLAUDE_PLUGIN_ROOT")
            else None
        ),
        os.path.join(sd, "..", "..", "..", sub),  # plugin layout: scripts → root
        os.path.join(claude, sub),  # install.sh layout
    ]
    return next(
        (
            os.path.abspath(p)
            for p in cands
            if p and os.path.isfile(os.path.join(p, sentinel))
        ),
        None,
    )


def find_mcp_dir():
    return _probe("mcp", "mcp-setup.py")


def first_capture_test(vault):
    """Pipe a synthetic Stop payload through the installed capture-exchange.py and
    check today's Daily note grew — the one end-to-end proof the pipeline works."""
    hooks = _probe("hooks", "_hooklib.py")
    hook = os.path.join(hooks, "capture-exchange.py") if hooks else None
    if not hook or not os.path.isfile(hook):
        print("   ✗ capture-exchange.py not found — re-run install.sh")
        return 1
    day = time.strftime("%Y-%m-%d")
    daily = os.path.join(vault, "Daily", day + ".md")
    before = os.path.getsize(daily) if os.path.exists(daily) else 0
    # the timestamp keeps the entry unique, so the hook's dedupe never eats a re-run
    payload = json.dumps(
        {
            "session_id": "sbverify",
            "cwd": "",
            "hook_event_name": "Stop",
            "last_assistant_message": "<!--CAPTURE: setup verification ping "
            + time.strftime("%H:%M:%S")
            + " || type: context-->",
        }
    )
    env = dict(os.environ, CLAUDE_MEMORY_DIR=vault)
    try:
        subprocess.run(
            [sys.executable, "-X", "utf8", hook],
            input=payload,
            text=True,
            env=env,
            timeout=30,
            check=False,
        )
    except Exception as e:  # noqa: BLE001
        print(f"   ✗ capture hook failed to run ({e})")
        return 1
    after = os.path.getsize(daily) if os.path.exists(daily) else 0
    if after > before:
        print(f"   ✓ live capture works — {daily}")
        return 0
    doctor = os.path.join(os.path.dirname(os.path.abspath(__file__)), "doctor.py")
    print(f"   ✗ capture wrote nothing to {daily}")
    print(f"     diagnose: python3 {doctor} --fix")
    return 1


def manual_steps(vault):
    print(f"""
{bold("Setup was skipped (no terminal attached).")}

Run it any time:
    python3 ~/.claude/skills/second-brain/scripts/setup.py

Or configure by hand — edit {vault}/config.json and map each repo
directory name to a vault folder:

    {{
      "project_map": {{
        "my-api":     "my-api",
        "my-api-web": "my-api"
      }}
    }}

Both entries point at one folder, so a repo and its web front-end share memory.
Then check the install:
    python3 ~/.claude/skills/second-brain/scripts/doctor.py
    python3 ~/.claude/skills/second-brain/scripts/setup.py --verify-capture

Connect Claude Desktop + Cursor to the vault (optional):
    python3 ~/.claude/mcp/mcp-setup.py --write
The ChatGPT/claude.ai remote is experimental — see mcp/README.md.

The optional starter pack (skills + vault notes + an Obsidian config) installs with:
    python3 ~/.claude/skills/second-brain/scripts/starter-pack.py --list
    python3 ~/.claude/skills/second-brain/scripts/starter-pack.py --tiers core
""")


def run_starter_pack(vault, tiers):
    """Hand the selection to starter-pack.py. Never fails setup: the pack is optional."""
    script = os.path.join(os.path.dirname(os.path.abspath(__file__)), "starter-pack.py")
    if not tiers or not os.path.exists(script):
        return
    env = dict(os.environ, CLAUDE_MEMORY_DIR=vault)
    try:
        subprocess.run(
            [sys.executable, "-X", "utf8", script, "--tiers", tiers],
            env=env,
            check=False,
            timeout=300,
        )
    except Exception as e:  # noqa: BLE001 — an optional extra must not break setup
        print(
            f"   ! starter pack skipped ({e}). Re-run: python3 {script} --tiers {tiers}"
        )


def ask(prompt, default=""):
    try:
        got = input(prompt).strip()
    except (EOFError, KeyboardInterrupt):
        print()
        raise
    return got or default


def main():
    args = sys.argv[1:]
    vault = MEM
    if "--vault" in args:
        i = args.index("--vault")
        if i + 1 < len(args):
            vault = os.path.expanduser(args[i + 1])

    # --pack answers the starter-pack question up front, so an install with no TTY can
    # still request it. "none" (or the flag being absent) means do not ask, do not install.
    pack = None
    for i, a in enumerate(args):
        if a == "--pack" and i + 1 < len(args):
            pack = args[i + 1]
        elif a.startswith("--pack="):
            pack = a.split("=", 1)[1]
    if pack is not None:
        pack = "" if pack.strip().lower() in ("", "none", "no", "n") else pack.strip()

    if "--verify-capture" in args:
        return first_capture_test(vault)

    interactive = sys.stdin.isatty() and "--non-interactive" not in args
    if not interactive:
        manual_steps(vault)
        if pack:
            run_starter_pack(vault, pack)
        return 0

    print(
        f"\n{bold('second-brain setup')}  {dim('(ctrl-c to skip, nothing is written until the end)')}"
    )
    print(f"Vault: {vault}\n")

    cfg = load_config(vault)
    cfg.pop("_comment", None)
    pmap = dict(cfg.get("project_map") or {})

    # --- 1. projects -------------------------------------------------------
    print(bold("1. Which projects should memory track?"))
    repos = find_repos()
    if not repos:
        print(
            dim(
                "   No git repositories found in ~/code, ~/src, ~/projects, ~/dev, ~/git, ~/repos."
            )
        )
        print(
            dim(
                "   You can add them later by re-running this script from a repo directory."
            )
        )
    else:
        names = sorted(repos)
        for i, n in enumerate(names, 1):
            mark = dim(" (already tracked)") if n in pmap else ""
            print(f"   {i:>2}. {n}{mark}  {dim(repos[n])}")
        print(dim("\n   Enter numbers (1,3,5-7), 'all', or blank to skip."))
        try:
            picked = parse_selection(ask("   > "), len(names))
        except (EOFError, KeyboardInterrupt):
            print("Setup cancelled. Nothing was written.")
            return 0
        for i in sorted(picked):
            n = names[i - 1]
            pmap[n] = n
        if picked:
            print(
                f"   {bold(str(len(picked)))} project(s) will route into their own vault folder."
            )

    # --- 2. semantic recall -------------------------------------------------
    print(f"\n{bold('2. Semantic recall?')}")
    print(
        dim(
            "   Keyword recall works out of the box. Semantic recall also finds notes that"
        )
    )
    print(
        dim("   use different words, but needs a one-off ~90 MB local model download.")
    )
    embed = False
    try:
        embed = ask("   Set it up now? [y/N] ").lower().startswith("y")
    except (EOFError, KeyboardInterrupt):
        pass

    # --- 3. starter pack ----------------------------------------------------
    if pack is None:
        print(f"\n{bold('3. Starter pack?')}")
        print(dim("   Skills and vault notes, so the graph is not empty on day one."))
        print(
            dim("   Everything is optional and nothing already on disk is overwritten.")
        )
        for key in sorted(PACK_CHOICES):
            print(f"   [{key}] {PACK_CHOICES[key][1]}")
        try:
            pack = PACK_CHOICES.get(ask("   > ", "1"), ("", ""))[0]
        except (EOFError, KeyboardInterrupt):
            pack = ""

    # --- 4. write -----------------------------------------------------------
    cfg["project_map"] = pmap
    cfg.setdefault("project_prefixes", {})
    os.makedirs(os.path.join(vault, ".recall-state"), exist_ok=True)
    path = save_config(vault, cfg)
    print(f"\n   ✓ wrote {path} ({len(pmap)} project(s))")

    if embed:
        script = os.path.join(
            os.path.dirname(os.path.abspath(__file__)), "embed-setup.sh"
        )
        if os.path.exists(script):
            print(dim("   running embed-setup.sh …"))
            try:
                subprocess.run(["bash", script], timeout=900, check=False)
            except Exception as e:  # noqa: BLE001 — never fail setup over an optional extra
                print(f"   ! embed setup failed ({e}). Recall still works on keywords.")
        else:
            print(f"   ! embed-setup.sh not found next to this script; skipped.")

    if pack:
        print()
        run_starter_pack(vault, pack)

    # --- 5. MCP clients ------------------------------------------------------
    mcp_dir = find_mcp_dir()
    print(f"\n{bold('4. Connect Claude Desktop & Cursor?')}")
    print(dim("   Exposes the vault to other apps over MCP (local stdio)."))
    if mcp_dir:
        mcp_setup = os.path.join(mcp_dir, "mcp-setup.py")
        yes = False
        try:
            yes = ask("   Run mcp-setup.py --write now? [y/N] ").lower().startswith("y")
        except (EOFError, KeyboardInterrupt):
            pass
        if yes:
            env = dict(os.environ, CLAUDE_MEMORY_DIR=vault)
            subprocess.run(
                [sys.executable, "-X", "utf8", mcp_setup, "--write"],
                env=env,
                check=False,
                timeout=120,
            )
        else:
            print(dim(f"   Later: python3 {mcp_setup} --write"))
    else:
        print(
            dim(
                "   mcp/ not found — from a repo checkout: python3 mcp/mcp-setup.py --write"
            )
        )

    # --- 6. ChatGPT / claude.ai remote ---------------------------------------
    print(f"\n{bold('5. ChatGPT / claude.ai remote? [experimental]')}")
    print(dim("   Read-only MCP behind a cloudflared tunnel; needs an isolated venv."))
    if os.name == "nt":
        print(
            dim("   Needs bash — not available on native Windows. See mcp/README.md.")
        )
    elif not mcp_dir:
        print(dim("   mcp/ not found — see mcp/README.md in the repo."))
    else:
        http_setup = os.path.join(mcp_dir, "mcp-http-setup.sh")
        run_chatgpt = os.path.join(mcp_dir, "run-chatgpt.sh")
        yes = False
        try:
            yes = ask("   Build the venv now? [y/N] ").lower().startswith("y")
        except (EOFError, KeyboardInterrupt):
            pass
        if yes:
            try:
                subprocess.run(["bash", http_setup], check=False, timeout=900)
            except Exception as e:  # noqa: BLE001 — optional extra, never fail setup
                print(f"   ! venv build failed ({e}). Re-run: bash {http_setup}")
            # print-only on purpose: the tunnel is never auto-launched
            print(f"   Start it yourself when ready:  bash {run_chatgpt}")
            print(
                dim(
                    "   cloudflared then prints the public https URL to paste into ChatGPT."
                )
            )
        else:
            print(dim(f"   Later: bash {http_setup}   (details in mcp/README.md)"))

    # --- 7. verify ----------------------------------------------------------
    print(f"\n{bold('6. Checking the install')}")
    first_capture_test(vault)
    doctor = os.path.join(os.path.dirname(os.path.abspath(__file__)), "doctor.py")
    if os.path.exists(doctor):
        env = dict(os.environ, CLAUDE_MEMORY_DIR=vault)
        subprocess.run([sys.executable, "-X", "utf8", doctor], env=env, check=False)

    print(f"""
{bold("Done.")} Restart Claude Code so the hooks load, then just work normally —
sessions are captured automatically.

  Ask it something and watch the memory banner appear.
  Curate a note:   /second-brain capture "<fact>"
  Search:          /second-brain pull "<terms>"
  Starter pack:    python3 {os.path.join(os.path.dirname(os.path.abspath(__file__)), "starter-pack.py")} --list
  Re-run setup:    python3 {os.path.abspath(__file__)}
""")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\nSetup cancelled. Nothing was written.")
        sys.exit(0)
