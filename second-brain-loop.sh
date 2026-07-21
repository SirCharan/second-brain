#!/usr/bin/env bash
# ── second-brain autonomous dump-and-reset loop (ralph pattern) ──────────────
# Each iteration is a FRESH `claude -p` process, so the context window resets to
# ~0 every time = cheap (no ballooning transcript re-sent each turn). State that
# must survive is persisted to the Obsidian vault (_infra/_carryover.md); the
# next iteration reads it back. This is the only way to truly "dump + reset"
# without a human pressing /clear.
#
# Usage:  ~/.claude/second-brain-loop.sh "<task description>" [max_iters]
# COST WARNING: this spawns real Claude sessions in a loop. Start with a small
# max_iters. Uses --dangerously-skip-permissions for unattended runs — only run
# it on a task/dir you trust.
set -euo pipefail
TASK="${1:?usage: second-brain-loop.sh \"<task>\" [max_iters]}"
MAX="${2:-15}"
VAULT="${CLAUDE_MEMORY_DIR:-$HOME/.claude/second-brain-vault}"
STATUS="$VAULT/_infra/_loop-status.md"
mkdir -p "$VAULT/_infra"; : > "$STATUS"

for i in $(seq 1 "$MAX"); do
  echo "──────── iteration $i / $MAX ────────"
  PROMPT="You are continuing a long task across FRESH sessions to save context cost.
TASK: $TASK
1. Read $VAULT/_infra/_carryover.md for where the last iteration stopped (empty on iteration 1).
2. Do only the NEXT small chunk of work.
3. Before you finish, run:  python3 ~/.claude/hooks/context-dump.py
   and write ONE word to $STATUS: DONE if the entire task is complete, otherwise NEXT.
Keep the chunk small so this session never fills its window."
  claude -p "$PROMPT" --dangerously-skip-permissions 2>&1 | tail -40 || true
  python3 ~/.claude/hooks/context-dump.py >/dev/null 2>&1 || true
  if grep -qi '^DONE' "$STATUS" 2>/dev/null; then echo "✓ task reported DONE at iteration $i"; break; fi
done
echo "loop finished."
