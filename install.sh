#!/usr/bin/env bash
# second-brain installer (non-plugin path): copy hooks/skill/workflow into ~/.claude,
# seed the vault, and idempotently register the hooks in ~/.claude/settings.json.
# Re-runnable: re-running upgrades files and de-dupes hook registrations.
set -euo pipefail

REPO="$(cd "$(dirname "${BASH_SOURCE[0]:-$0}")" && pwd)"
CLAUDE="${CLAUDE_CONFIG_DIR:-$HOME/.claude}"
VAULT="${CLAUDE_MEMORY_DIR:-$HOME/.claude/second-brain-vault}"
PY=/usr/bin/python3; command -v "$PY" >/dev/null 2>&1 || PY=python3

echo "second-brain → installing into $CLAUDE"
mkdir -p "$CLAUDE/hooks" "$CLAUDE/skills" "$CLAUDE/workflows"

# --- machinery ---
cp "$REPO"/hooks/*.py "$REPO"/hooks/*.sh "$CLAUDE/hooks/"
chmod +x "$CLAUDE"/hooks/*.sh
rm -rf "$CLAUDE/skills/second-brain"
cp -R "$REPO/skills/second-brain" "$CLAUDE/skills/second-brain"
cp "$REPO/workflows/vault-enrich.js" "$CLAUDE/workflows/vault-enrich.js"
echo "  ✓ hooks, skill, workflow copied"

# --- vault ---
if [ ! -d "$VAULT" ]; then
  cp -R "$REPO/vault-template" "$VAULT"
  echo "  ✓ vault created at $VAULT"
else
  echo "  • vault already exists at $VAULT (left as-is)"
fi
if [ ! -f "$VAULT/config.json" ]; then
  cp "$REPO/config.example.json" "$VAULT/config.json"
  echo "  ✓ seeded $VAULT/config.json (edit it to map your repos → folders)"
fi

# --- register hooks in settings.json (idempotent) ---
"$PY" - "$CLAUDE/settings.json" <<'PYEOF'
import json, os, sys, shutil
settings = sys.argv[1]
hooks_dir = os.path.join(os.path.dirname(settings), "hooks")
def cmd(s): return s.replace("HOOKS", hooks_dir)
FRAG = {
  "SessionStart": [
    {"hooks":[{"type":"command","command":cmd('bash "HOOKS/session-memory.sh"'),"timeout":8}]},
    {"hooks":[{"type":"command","command":cmd('bash "HOOKS/session-resume.sh"'),"timeout":8}]},
  ],
  "UserPromptSubmit": [
    {"hooks":[{"type":"command","command":cmd('python3 "HOOKS/interview-nudge.py"')}]},
    {"hooks":[{"type":"command","command":cmd('bash "HOOKS/memory-recall.sh"'),"timeout":5}]},
  ],
  "PostToolUse": [
    {"matcher":"Edit|Write","hooks":[{"type":"command","command":cmd('bash "HOOKS/memory-lint.sh"'),"timeout":5}]},
    {"matcher":"Bash","hooks":[{"type":"command","command":cmd('bash "HOOKS/stuck-detector.sh"'),"timeout":5}]},
  ],
  "Stop": [
    {"matcher":"","hooks":[{"type":"command","command":cmd('bash "HOOKS/capture-exchange.sh"'),"timeout":6}]},
  ],
  "PreCompact": [
    {"hooks":[{"type":"command","command":cmd('python3 "HOOKS/precompact-carryover.py"')}]},
  ],
}
OURS = ("session-memory","session-resume","interview-nudge","memory-recall",
        "memory-lint","stuck-detector","capture-exchange","precompact-carryover")
d = {}
if os.path.exists(settings):
    try: d = json.load(open(settings))
    except Exception: d = {}
    shutil.copy2(settings, settings + ".bak")
H = d.setdefault("hooks", {})
def is_ours(entry):
    return any(o in h.get("command","") for h in entry.get("hooks",[]) for o in OURS)
for ev, entries in FRAG.items():
    existing = [e for e in H.get(ev, []) if not is_ours(e)]  # drop our old copies
    H[ev] = existing + entries
json.dump(d, open(settings,"w"), indent=2)
print("  ✓ hooks registered in", settings)
PYEOF

cat <<EOF

Done. Next steps:
  1. If your vault is NOT the default (~/.claude/second-brain-vault), export it:
       export CLAUDE_MEMORY_DIR="$VAULT"     # add to your shell profile
  2. Restart Claude Code (or start a new session) so the hooks load.
  3. Verify:  python3 "$CLAUDE/skills/second-brain/scripts/doctor.py"

Vault: $VAULT
Edit  $VAULT/config.json  to route your repos into memory folders.
EOF
