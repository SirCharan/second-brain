#!/usr/bin/env bash
# Opt-in: build the OPTIONAL semantic-recall venv. The second-brain core is pure stdlib;
# semantic recall (embedding-based note matching) is the one extra that needs a pip install,
# isolated here so it never touches your system Python.
#
#   bash embed-setup.sh
#
# After this, memory-recall + session-resume automatically use semantic recall to fill any
# slots keyword matching leaves empty. Remove the venv to turn it back off — everything
# degrades cleanly to keyword-only.
set -euo pipefail

STATE_DIR="${SECOND_BRAIN_STATE_DIR:-$HOME/.second-brain}"
VENV="$STATE_DIR/venv-embed"

echo "second-brain · building optional semantic-recall venv → $VENV"
mkdir -p "$STATE_DIR"
python3 -m venv "$VENV"
"$VENV/bin/pip" install --quiet --upgrade pip
"$VENV/bin/pip" install --quiet fastembed numpy
echo "✓ ready. First recall downloads the bge-small model (~130MB), then it's local + offline."
echo "  Turn it off anytime:  rm -rf \"$VENV\""
