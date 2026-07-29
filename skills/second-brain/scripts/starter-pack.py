#!/usr/bin/env python3
"""starter-pack — install the optional skill/vault starter pack.

Run by setup.py's opt-in step, and re-runnable any time from a clone of the repo:

    python3 ~/.claude/skills/second-brain/scripts/starter-pack.py --tiers core,writing

It copies vendored skills into the Claude config dir, merges extra notes into the vault,
places an Obsidian app config, then regenerates the vault's `_system/` folder so every
installed skill also exists as a linked note.

Nothing is overwritten. A skill directory, vault file or `.obsidian/` that already exists
is left exactly as it is, which is what makes the script safe to re-run.

Third-party packs are never copied — `starter-pack/manifest.json` lists them with their
author, licence and install command, and this script only prints that list.

Flags:
  --tiers core,writing,design   which tiers to install ("all" for every tier)
  --list                        print the tiers and the third-party manifest, install nothing
  --vault PATH                  operate on this vault instead of $CLAUDE_MEMORY_DIR
  --source PATH                 path to the repo's starter-pack/ directory
  --dry-run                     report what would happen, write nothing
"""

import json
import os
import shutil
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
CLAUDE = os.environ.get("CLAUDE_CONFIG_DIR") or os.path.expanduser("~/.claude")
DEFAULT_VAULT = os.environ.get("CLAUDE_MEMORY_DIR") or os.path.join(
    CLAUDE, "second-brain-vault"
)
HOME_LINE = (
    "- [[_MOC-playbook]] — the working rules: session habits, phase discipline, routing"
)


def find_source(explicit=None):
    """Locate the repo's starter-pack/ directory.

    Order: --source, then $SB_STARTER_PACK / $SB_REPO (install.sh exports the latter),
    then a walk up from this file for a git clone, then a copy sitting beside the skill.
    """
    cands = []
    if explicit:
        cands.append(os.path.expanduser(explicit))
    if os.environ.get("SB_STARTER_PACK"):
        cands.append(os.path.expanduser(os.environ["SB_STARTER_PACK"]))
    if os.environ.get("SB_REPO"):
        cands.append(
            os.path.join(os.path.expanduser(os.environ["SB_REPO"]), "starter-pack")
        )
    d = HERE
    for _ in range(5):
        d = os.path.dirname(d)
        cands.append(os.path.join(d, "starter-pack"))
    cands.append(os.path.join(HERE, "..", "starter-pack"))
    for c in cands:
        if os.path.isfile(os.path.join(c, "tiers.json")):
            return os.path.abspath(c)
    return None


def load(path, default=None):
    try:
        with open(path) as f:
            return json.load(f)
    except (OSError, ValueError):
        return default


def parse_tiers(raw, tiers):
    """'core,writing' or 'all' -> an ordered list of valid tier names."""
    names = [t for t in tiers if not t.startswith("_")]
    if not raw:
        return []
    raw = raw.strip().lower()
    if raw in ("all", "*"):
        return names
    picked = [p.strip() for p in raw.replace(" ", ",").split(",") if p.strip()]
    return [p for p in names if p in picked]


def copy_tree_if_absent(src, dst, dry):
    """Copy a directory only when the destination does not exist. Returns True if copied."""
    if os.path.exists(dst):
        return False
    if not dry:
        shutil.copytree(
            src, dst, ignore=shutil.ignore_patterns("__pycache__", ".DS_Store")
        )
    return True


def merge_files_if_absent(src_dir, dst_dir, dry):
    """Copy every file under src_dir into dst_dir, skipping any that already exists."""
    written, skipped = [], []
    for root, _dirs, files in os.walk(src_dir):
        rel = os.path.relpath(root, src_dir)
        target_dir = dst_dir if rel == "." else os.path.join(dst_dir, rel)
        for f in files:
            if f == ".DS_Store":
                continue
            target = os.path.join(target_dir, f)
            if os.path.exists(target):
                skipped.append(target)
                continue
            if not dry:
                os.makedirs(target_dir, exist_ok=True)
                shutil.copy2(os.path.join(root, f), target)
            written.append(target)
    return written, skipped


def link_playbook_from_home(vault, dry):
    """Add one line to _Home.md's note list so the new hub is reachable from the map.

    Appending rather than shipping the line in vault-template keeps _Home honest when the
    pack is not installed.
    """
    home = os.path.join(vault, "_Home.md")
    if not os.path.isfile(home):
        return False
    text = open(home).read()
    if "_MOC-playbook" in text:
        return False
    anchor = "### 🗂️ Notes"
    if anchor in text:
        text = text.replace(anchor, anchor + "\n" + HOME_LINE, 1)
    else:
        text = text.rstrip("\n") + "\n" + HOME_LINE + "\n"
    if not dry:
        with open(home, "w") as f:
            f.write(text)
    return True


def record_in_install_manifest(vault, dirs, workflows, dry):
    """Append what we created to the install manifest, so uninstall.sh removes it too.

    uninstall.sh already iterates the manifest's `dirs` and `workflows` keys, so nothing
    on that side needs to change.
    """
    mp = os.path.join(vault, "_infra", "_install-manifest.json")
    man = load(mp, {}) or {}
    man["dirs"] = sorted(set(man.get("dirs", [])) | set(dirs))
    man["workflows"] = sorted(set(man.get("workflows", [])) | set(workflows))
    man["starter_pack"] = sorted(
        set(man.get("starter_pack", [])) | set(dirs) | set(workflows)
    )
    if not dry:
        os.makedirs(os.path.dirname(mp), exist_ok=True)
        tmp = mp + ".tmp"
        with open(tmp, "w") as f:
            json.dump(man, f, indent=2)
            f.write("\n")
        os.replace(tmp, mp)
    return mp


def print_manifest(manifest, installed):
    """List the third-party packs the installed skills route into."""
    packs = {
        k: v
        for k, v in manifest.items()
        if not k.startswith("_")
        and (not installed or set(v.get("required_by", [])) & set(installed))
    }
    if not packs:
        return
    print("\n  These skills route into packs written by other people. They are not")
    print("  redistributed here — fetch each one from its author:\n")
    for i, (name, p) in enumerate(sorted(packs.items()), 1):
        needs = f" (needs {', '.join(p['needs'])})" if p.get("needs") else ""
        print(
            f"  {i}. {name} — {p.get('author', 'unknown')}, {p.get('license', '?')}{needs}"
        )
        print(f"     for: {', '.join(p.get('required_by', []))}")
        for cmd in p.get("install", []):
            print(f"     $ {cmd}")
        print()


def do_list(src, tiers, manifest):
    print(f"starter-pack source: {src}\n")
    for name, t in tiers.items():
        if name.startswith("_"):
            continue
        print(f"  {name} — {t['what']}")
        print(f"    skills:    {', '.join(t['skills'])}")
        if t.get("workflows"):
            print(f"    workflows: {', '.join(t['workflows'])}")
        print()
    print_manifest(manifest, installed=None)


def main(argv=None):
    args = list(argv if argv is not None else sys.argv[1:])

    def opt(flag, default=None):
        if flag in args:
            i = args.index(flag)
            if i + 1 < len(args):
                return args[i + 1]
        return default

    src = find_source(opt("--source"))
    if not src:
        print(
            "starter-pack: could not find the repo's starter-pack/ directory.\n"
            "  Clone the repo and re-run with --source:\n"
            "    git clone https://github.com/SirCharan/second-brain\n"
            "    python3 second-brain/skills/second-brain/scripts/starter-pack.py "
            "--source second-brain/starter-pack --tiers all",
            file=sys.stderr,
        )
        return 1

    tiers = load(os.path.join(src, "tiers.json"), {}) or {}
    manifest = load(os.path.join(src, "manifest.json"), {}) or {}
    if "--list" in args:
        do_list(src, tiers, manifest)
        return 0

    vault = os.path.expanduser(opt("--vault") or DEFAULT_VAULT)
    dry = "--dry-run" in args
    picked = parse_tiers(opt("--tiers"), tiers)
    if not picked:
        print(
            "starter-pack: nothing selected (use --tiers core,writing,design or --list)."
        )
        return 0

    tag = "  (dry run)" if dry else "  ✓"
    print(f"starter-pack → {', '.join(picked)} into {CLAUDE}")

    # --- skills + workflows ------------------------------------------------
    made_dirs, made_workflows, present = [], [], []
    skills_root = os.path.join(CLAUDE, "skills")
    wf_root = os.path.join(CLAUDE, "workflows")
    if not dry:
        os.makedirs(skills_root, exist_ok=True)
        os.makedirs(wf_root, exist_ok=True)
    installed_skills = []
    for tier in picked:
        for s in tiers[tier]["skills"]:
            srcd, dstd = os.path.join(src, "skills", s), os.path.join(skills_root, s)
            if not os.path.isdir(srcd):
                print(f"  ! {s} missing from the pack source, skipped")
                continue
            installed_skills.append(s)
            if copy_tree_if_absent(srcd, dstd, dry):
                made_dirs.append(dstd)
            else:
                present.append(s)
        for w in tiers[tier].get("workflows", []):
            srcf, dstf = os.path.join(src, "workflows", w), os.path.join(wf_root, w)
            if os.path.isfile(srcf) and not os.path.exists(dstf):
                if not dry:
                    shutil.copy2(srcf, dstf)
                made_workflows.append(dstf)
    print(
        f"{tag} {len(made_dirs)} skill(s), {len(made_workflows)} workflow(s) installed"
    )
    if present:
        print(f"  • already present, left as-is: {', '.join(sorted(present))}")

    # --- vault seed ---------------------------------------------------------
    if os.path.isdir(vault):
        seed = os.path.join(src, "vault")
        if os.path.isdir(seed):
            written, skipped = merge_files_if_absent(seed, vault, dry)
            print(
                f"{tag} {len(written)} vault note(s) added"
                + (f", {len(skipped)} left as-is" if skipped else "")
            )
        obs_src, obs_dst = (
            os.path.join(src, "obsidian"),
            os.path.join(vault, ".obsidian"),
        )
        if os.path.isdir(obs_src):
            if copy_tree_if_absent(obs_src, obs_dst, dry):
                print(f"{tag} Obsidian config written to {obs_dst}")
            else:
                print(f"  • {obs_dst} exists, left as-is")
        if link_playbook_from_home(vault, dry):
            print(f"{tag} _Home.md now links the playbook hub")
    else:
        print(f"  ! no vault at {vault}; skills installed, vault content skipped")

    # --- manifest + system index -------------------------------------------
    if (made_dirs or made_workflows) and os.path.isdir(vault):
        mp = record_in_install_manifest(vault, made_dirs, made_workflows, dry)
        print(f"{tag} recorded in {mp}")

    index = os.path.join(HERE, "build-system-index.py")
    if os.path.isfile(index) and os.path.isdir(vault) and not dry:
        env = dict(os.environ, CLAUDE_MEMORY_DIR=vault, CLAUDE_CONFIG_DIR=CLAUDE)
        try:
            subprocess.run([sys.executable, index], env=env, check=False, timeout=120)
        except Exception as e:  # noqa: BLE001 — an index refresh is never worth failing over
            print(
                f"  ! could not refresh _system/ ({e}). Run /second-brain index later."
            )

    print_manifest(manifest, installed_skills)
    print("  Restart Claude Code so the new skills load.")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\nstarter-pack: cancelled.")
        sys.exit(0)
