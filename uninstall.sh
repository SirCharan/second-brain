#!/usr/bin/env bash
# second-brain uninstaller. Reads the manifest install.sh wrote and removes exactly
# what it added: the hooks, the skill, the workflow, and our hook registrations.
#
# Your vault is NOT touched unless you pass --purge-vault. Notes are the point of
# this tool; deleting them by default would be indefensible.
#
#   bash uninstall.sh              # remove machinery, keep every note
#   bash uninstall.sh --purge-vault  # also delete the vault (asks first)
#   bash uninstall.sh --dry-run    # show what would happen
set -euo pipefail

CLAUDE="${CLAUDE_CONFIG_DIR:-$HOME/.claude}"
VAULT="${CLAUDE_MEMORY_DIR:-$HOME/.claude/second-brain-vault}"
PURGE=0
DRY_RUN=0
for a in "$@"; do
  case "$a" in
    --purge-vault) PURGE=1 ;;
    --dry-run) DRY_RUN=1 ;;
    -h|--help) sed -n '2,12p' "$0"; exit 0 ;;
  esac
done

PY=""
for c in python3 /usr/bin/python3 python; do
  command -v "$c" >/dev/null 2>&1 && { PY="$c"; break; }
done
[ -n "$PY" ] || { echo "uninstall: needs python3 on PATH." >&2; exit 1; }

MANIFEST="$VAULT/_infra/_install-manifest.json"
echo "second-brain → uninstalling from $CLAUDE"
[ -f "$MANIFEST" ] || echo "  ! no manifest at $MANIFEST — falling back to the known layout"

DRY_RUN="$DRY_RUN" "$PY" - "$CLAUDE" "$VAULT" "$MANIFEST" <<'PYEOF'
import json, os, shutil, sys
claude, vault, manifest = sys.argv[1], sys.argv[2], sys.argv[3]
dry = os.environ.get("DRY_RUN") == "1"
def say(*a): print(("  (dry run)" if dry else "  ✓"), *a)

OURS = ("session-memory","session-resume","interview-nudge","memory-recall","context-monitor",
        "memory-lint","stuck-detector","capture-exchange","precompact-carryover")
man = {}
if os.path.exists(manifest):
    try: man = json.load(open(manifest))
    except Exception: man = {}

# 1. hook files — only ones we ship, never anything the user added
hooks_dir = os.path.join(claude, "hooks")
shipped = set(man.get("hook_names", OURS)) | {"_hooklib", "memory-embed", "context-dump", "sb_rank"}
removed = 0
if os.path.isdir(hooks_dir):
    for f in sorted(os.listdir(hooks_dir)):
        stem = os.path.splitext(f)[0]
        if stem in shipped and f.endswith((".py", ".sh")):
            if not dry: os.remove(os.path.join(hooks_dir, f))
            removed += 1
say(f"removed {removed} hook file(s)")
# Our own import cache, created the first time a hook ran. Ours to clean up.
pyc = os.path.join(hooks_dir, "__pycache__")
if os.path.isdir(pyc):
    if not dry: shutil.rmtree(pyc, ignore_errors=True)
    say("removed", pyc)

# 2. skill + workflow
for d in man.get("dirs", [os.path.join(claude, "skills", "second-brain")]):
    if os.path.isdir(d):
        if not dry: shutil.rmtree(d)
        say("removed", d)
for w in man.get("workflows", [os.path.join(claude, "workflows", "vault-enrich.js")]):
    if os.path.exists(w):
        if not dry: os.remove(w)
        say("removed", w)

# 3. de-register hooks. Prefer surgical removal over restoring the backup, because the
# backup predates any unrelated settings the user has changed since installing.
settings = man.get("settings") or os.path.join(claude, "settings.json")
if os.path.exists(settings):
    try:
        d = json.load(open(settings))
    except Exception:
        print("  ! settings.json is not valid JSON — left untouched")
        d = None
    if d is not None:
        H = d.get("hooks", {})
        def is_ours(e):
            return any(o in h.get("command", "") for h in e.get("hooks", []) for o in OURS)
        n = 0
        for ev in list(H):
            keep = [e for e in H[ev] if not is_ours(e)]
            n += len(H[ev]) - len(keep)
            if keep: H[ev] = keep
            else: H.pop(ev)
        if not H: d.pop("hooks", None)
        if d.get("env", {}).get("CLAUDE_MEMORY_DIR"):
            d["env"].pop("CLAUDE_MEMORY_DIR", None)
            if not d["env"]: d.pop("env")
        if not dry:
            shutil.copy2(settings, settings + ".pre-uninstall.bak")
            json.dump(d, open(settings, "w"), indent=2)
        say(f"de-registered {n} hook entr(ies) from settings.json")
        bak = man.get("settings_backup")
        if bak and os.path.exists(bak):
            print(f"  • pre-install backup still available: {bak}")
PYEOF

if [ "$PURGE" = "1" ]; then
  if [ "$DRY_RUN" = "1" ]; then
    echo "  (dry run) would delete the vault at $VAULT"
  else
    printf 'Delete the vault and every note at %s? [y/N] ' "$VAULT"
    read -r ans
    case "$ans" in
      y|Y) rm -rf "$VAULT"; echo "  ✓ vault deleted" ;;
      *) echo "  • vault kept" ;;
    esac
  fi
else
  echo "  • vault kept at $VAULT (use --purge-vault to remove it)"
fi

echo
echo "Done. Restart Claude Code so it stops loading the hooks."
