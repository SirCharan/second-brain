#!/usr/bin/env bash
# second-brain installer. Copies hooks/skill/workflow into ~/.claude, seeds the vault,
# registers the hooks in ~/.claude/settings.json, and offers guided setup.
#
# Works two ways:
#   curl -fsSL https://raw.githubusercontent.com/SirCharan/second-brain/main/install.sh | bash
#   git clone https://github.com/SirCharan/second-brain && ./second-brain/install.sh
#
# Re-runnable: re-running upgrades files and de-dupes hook registrations.
# Undo with uninstall.sh. Flags: --no-setup (skip the wizard), --dry-run,
#   --pack=none|core|core,writing|all (answer the starter-pack question up front).
set -euo pipefail

REPO_URL="https://github.com/SirCharan/second-brain"
TARBALL="$REPO_URL/archive/refs/heads/main.tar.gz"
CLAUDE="${CLAUDE_CONFIG_DIR:-$HOME/.claude}"
VAULT="${CLAUDE_MEMORY_DIR:-$HOME/.claude/second-brain-vault}"
DRY_RUN=0
RUN_SETUP=1
PACK=""
for a in "$@"; do
  case "$a" in
    --dry-run) DRY_RUN=1 ;;
    --no-setup) RUN_SETUP=0 ;;
    --pack=*) PACK="${a#--pack=}" ;;
    -h|--help) sed -n '2,11p' "$0" 2>/dev/null || true; exit 0 ;;
  esac
done
# "all" is the friendly spelling of every tier; starter-pack.py understands both.
[ "$PACK" = "none" ] && PACK=""

# --- locate the source tree -------------------------------------------------
# Piped through curl there is no script file on disk: BASH_SOURCE is unset and $0 is
# "bash", so the old $(dirname $0) trick resolved to the caller's cwd and every cp
# failed. Detect that by looking for a sentinel file and self-download instead.
SELF="${BASH_SOURCE[0]:-$0}"
REPO=""
if [ -f "$SELF" ]; then
  REPO="$(cd "$(dirname "$SELF")" && pwd)"
fi
if [ -z "$REPO" ] || [ ! -f "$REPO/hooks/_hooklib.py" ]; then
  if [ "${SB_BOOTSTRAPPED:-0}" = "1" ]; then
    echo "second-brain: bootstrap failed — source tree still incomplete." >&2
    exit 1
  fi
  command -v curl >/dev/null 2>&1 || { echo "second-brain: curl is required to bootstrap." >&2; exit 1; }
  command -v tar  >/dev/null 2>&1 || { echo "second-brain: tar is required to bootstrap." >&2; exit 1; }
  TMP="$(mktemp -d)"
  trap 'rm -rf "$TMP"' EXIT
  echo "second-brain → fetching source…"
  curl -fsSL "$TARBALL" | tar -xz -C "$TMP"
  SRC="$(find "$TMP" -maxdepth 1 -type d -name 'second-brain-*' | head -1)"
  [ -n "$SRC" ] && [ -f "$SRC/hooks/_hooklib.py" ] || {
    echo "second-brain: downloaded archive looks wrong." >&2; exit 1; }
  SB_BOOTSTRAPPED=1 exec bash "$SRC/install.sh" "$@"
fi

VERSION="$(cat "$REPO/VERSION" 2>/dev/null || echo "unknown")"

# --- preflight: fail BEFORE touching anything -------------------------------
PY=""
for c in python3 /usr/bin/python3 python; do
  if command -v "$c" >/dev/null 2>&1; then
    if "$c" -c 'import sys; sys.exit(0 if sys.version_info >= (3,8) else 1)' 2>/dev/null; then
      PY="$c"; break
    fi
  fi
done
if [ -z "$PY" ]; then
  cat >&2 <<'EOM'
second-brain: needs Python 3.8+ on PATH, and found none.
  macOS:  xcode-select --install    (or: brew install python3)
  Debian: sudo apt install python3
Nothing was installed.
EOM
  exit 1
fi

parent="$(dirname "$CLAUDE")"
[ -w "$parent" ] || { echo "second-brain: $parent is not writable. Nothing was installed." >&2; exit 1; }
if [ -e "$CLAUDE" ] && [ ! -w "$CLAUDE" ]; then
  echo "second-brain: $CLAUDE exists but is not writable. Nothing was installed." >&2; exit 1
fi

# An unreadable settings.json means we cannot merge safely. Refuse rather than
# silently replacing the user's whole Claude Code config with a hooks-only file.
SETTINGS="$CLAUDE/settings.json"
if [ -f "$SETTINGS" ] && ! "$PY" -c 'import json,sys; json.load(open(sys.argv[1]))' "$SETTINGS" 2>/dev/null; then
  cat >&2 <<EOM
second-brain: $SETTINGS is not valid JSON, so hooks cannot be merged into it.
Fix or move that file, then re-run. Nothing was installed.
EOM
  exit 1
fi

command -v claude >/dev/null 2>&1 || echo "  ! Claude Code CLI not found on PATH — install it for the hooks to do anything."

echo "second-brain $VERSION → installing into $CLAUDE"
if [ "$DRY_RUN" = "1" ]; then
  echo "  (dry run) would copy hooks/, skills/second-brain/, workflows/vault-enrich.js"
  echo "  (dry run) would seed vault at $VAULT and register 9 hooks in $SETTINGS"
  if [ -n "$PACK" ]; then
    echo "  (dry run) would offer the starter pack: $PACK"
  else
    echo "  (dry run) would ask whether to install the starter pack (skills + vault notes)"
  fi
  exit 0
fi

mkdir -p "$CLAUDE/hooks" "$CLAUDE/skills" "$CLAUDE/workflows"

# --- machinery --------------------------------------------------------------
# Ship runtime hooks only; the test suite belongs to the repo, not the user's dir.
for f in "$REPO"/hooks/*.py "$REPO"/hooks/*.sh; do
  case "$(basename "$f")" in test_*) continue ;; esac
  cp "$f" "$CLAUDE/hooks/"
done
chmod +x "$CLAUDE"/hooks/*.sh
rm -rf "$CLAUDE/skills/second-brain"
cp -R "$REPO/skills/second-brain" "$CLAUDE/skills/second-brain"
cp "$REPO/workflows/vault-enrich.js" "$CLAUDE/workflows/vault-enrich.js"
echo "  ✓ hooks, skill, workflow copied"

# --- vault ------------------------------------------------------------------
if [ ! -d "$VAULT" ]; then
  cp -R "$REPO/vault-template" "$VAULT"
  mkdir -p "$VAULT/.recall-state"
  echo "  ✓ vault created at $VAULT"
else
  echo "  • vault already exists at $VAULT (left as-is)"
  mkdir -p "$VAULT/.recall-state"
fi

# --- register hooks + write the install manifest (idempotent) ---------------
"$PY" - "$SETTINGS" "$VAULT" "$VERSION" <<'PYEOF'
import json, os, sys, shutil, time
settings, vault, version = sys.argv[1], sys.argv[2], sys.argv[3]
hooks_dir = os.path.join(os.path.dirname(settings), "hooks")
def cmd(s): return s.replace("HOOKS", hooks_dir)
FRAG = {
  "SessionStart": [
    {"hooks":[{"type":"command","command":cmd('bash "HOOKS/session-memory.sh"'),"timeout":8}]},
    {"hooks":[{"type":"command","command":cmd('bash "HOOKS/session-resume.sh"'),"timeout":8}]},
  ],
  "UserPromptSubmit": [
    {"hooks":[{"type":"command","command":cmd('python3 "HOOKS/interview-nudge.py"'),"timeout":10}]},
    {"hooks":[{"type":"command","command":cmd('bash "HOOKS/memory-recall.sh"'),"timeout":15}]},
    {"hooks":[{"type":"command","command":cmd('bash "HOOKS/context-monitor.sh"'),"timeout":15}]},
  ],
  "PostToolUse": [
    {"matcher":"Edit|Write","hooks":[{"type":"command","command":cmd('bash "HOOKS/memory-lint.sh"'),"timeout":5}]},
    {"matcher":"Bash","hooks":[{"type":"command","command":cmd('bash "HOOKS/stuck-detector.sh"'),"timeout":5}]},
  ],
  "Stop": [
    {"matcher":"","hooks":[{"type":"command","command":cmd('bash "HOOKS/capture-exchange.sh"'),"timeout":10}]},
  ],
  "PreCompact": [
    {"hooks":[{"type":"command","command":cmd('python3 "HOOKS/precompact-carryover.py"'),"timeout":10}]},
  ],
}
OURS = ("session-memory","session-resume","interview-nudge","memory-recall","context-monitor",
        "memory-lint","stuck-detector","capture-exchange","precompact-carryover")
d, backup = {}, None
if os.path.exists(settings):
    d = json.load(open(settings))          # preflight already proved this parses
    backup = settings + ".bak"
    shutil.copy2(settings, backup)
H = d.setdefault("hooks", {})
def is_ours(entry):
    return any(o in h.get("command","") for h in entry.get("hooks",[]) for o in OURS)
for ev, entries in FRAG.items():
    existing = [e for e in H.get(ev, []) if not is_ours(e)]  # drop our old copies only
    H[ev] = existing + entries
json.dump(d, open(settings,"w"), indent=2)
print("  ✓ hooks registered in", settings)

# Manifest: what this install touched, so uninstall.sh can undo exactly that.
claude = os.path.dirname(settings)
files = sorted(
    os.path.join(claude, "hooks", f) for f in os.listdir(os.path.join(claude, "hooks"))
    if f.endswith((".py", ".sh"))
)
man = {
    "version": version, "installed_at": time.strftime("%Y-%m-%dT%H:%M:%S"),
    "claude_dir": claude, "vault": vault,
    "files": files,
    "dirs": [os.path.join(claude, "skills", "second-brain")],
    "workflows": [os.path.join(claude, "workflows", "vault-enrich.js")],
    "settings": settings, "settings_backup": backup,
    "hook_events": sorted(FRAG), "hook_names": list(OURS),
}
os.makedirs(os.path.join(vault, "_infra"), exist_ok=True)
mp = os.path.join(vault, "_infra", "_install-manifest.json")
json.dump(man, open(mp, "w"), indent=2)
print("  ✓ manifest written to", mp)
PYEOF

# Persist a non-default vault path, or it is forgotten on the next shell.
if [ "$VAULT" != "$HOME/.claude/second-brain-vault" ]; then
  for rc in "$HOME/.zshrc" "$HOME/.bashrc"; do
    [ -f "$rc" ] || continue
    grep -q 'CLAUDE_MEMORY_DIR' "$rc" 2>/dev/null && continue
    printf '\n# second-brain vault\nexport CLAUDE_MEMORY_DIR="%s"\n' "$VAULT" >> "$rc"
    echo "  ✓ exported CLAUDE_MEMORY_DIR in $(basename "$rc")"
  done
fi

# --- guided setup -----------------------------------------------------------
# SB_REPO lets setup.py/starter-pack.py find starter-pack/, which stays in the repo
# rather than being copied into $CLAUDE. Under `curl | bash` the repo is a temp dir,
# so this is the only handle they get.
export SB_REPO="$REPO"
SETUP="$CLAUDE/skills/second-brain/scripts/setup.py"
PACK_SCRIPT="$CLAUDE/skills/second-brain/scripts/starter-pack.py"
if [ "$RUN_SETUP" = "1" ] && [ -f "$SETUP" ]; then
  echo
  CLAUDE_MEMORY_DIR="$VAULT" "$PY" "$SETUP" ${PACK:+--pack "$PACK"} \
    || echo "  ! setup skipped — re-run: $PY \"$SETUP\""
elif [ -n "$PACK" ] && [ -f "$PACK_SCRIPT" ]; then
  # --no-setup with an explicit --pack: install the pack, skip the wizard.
  echo
  CLAUDE_MEMORY_DIR="$VAULT" "$PY" "$PACK_SCRIPT" --tiers "$PACK" \
    || echo "  ! starter pack skipped — re-run: $PY \"$PACK_SCRIPT\" --tiers $PACK"
fi

cat <<EOF

second-brain $VERSION installed.
  Vault:  $VAULT
  Check:  $PY "$CLAUDE/skills/second-brain/scripts/doctor.py"
  Pack:   $PY "$PACK_SCRIPT" --list      # optional skills + vault notes
  Undo:   bash uninstall.sh

Restart Claude Code (or start a new session) so the hooks load.
EOF
