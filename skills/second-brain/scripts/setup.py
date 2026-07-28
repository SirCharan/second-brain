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
"""

import json
import os
import subprocess
import sys

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
        with open(p) as f:
            cfg = json.load(f)
            return cfg if isinstance(cfg, dict) else {}
    except (OSError, ValueError):
        return {}


def save_config(vault, cfg):
    p = os.path.join(vault, "config.json")
    os.makedirs(vault, exist_ok=True)
    tmp = p + ".tmp"
    with open(tmp, "w") as f:
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
""")


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

    interactive = sys.stdin.isatty() and "--non-interactive" not in args
    if not interactive:
        manual_steps(vault)
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

    # --- 3. write -----------------------------------------------------------
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

    # --- 4. verify ----------------------------------------------------------
    doctor = os.path.join(os.path.dirname(os.path.abspath(__file__)), "doctor.py")
    if os.path.exists(doctor):
        print(f"\n{bold('3. Checking the install')}")
        env = dict(os.environ, CLAUDE_MEMORY_DIR=vault)
        subprocess.run([sys.executable, doctor], env=env, check=False)

    print(f"""
{bold("Done.")} Restart Claude Code so the hooks load, then just work normally —
sessions are captured automatically.

  Ask it something and watch the memory banner appear.
  Curate a note:   /second-brain capture "<fact>"
  Search:          /second-brain pull "<terms>"
  Re-run setup:    python3 {os.path.abspath(__file__)}
""")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\nSetup cancelled. Nothing was written.")
        sys.exit(0)
