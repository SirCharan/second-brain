#!/usr/bin/env bash
# Opt-in: build the OPTIONAL venv for the ChatGPT (Streamable-HTTP) MCP server.
# The second-brain core + stdio/http servers are pure stdlib. Only the ChatGPT
# endpoint (server_http_sdk.py) needs the official `mcp` Python SDK, isolated here
# so it never touches your system Python. Mirrors embed-setup.sh.
#
#   bash mcp-http-setup.sh
#
# After this, run:  bash mcp/run-chatgpt.sh   (starts the server + a cloudflared tunnel).
# Remove the venv to turn it back off — the stdlib stdio/http servers are unaffected.
set -euo pipefail

STATE_DIR="${SECOND_BRAIN_STATE_DIR:-$HOME/.second-brain}"
VENV="$STATE_DIR/venv-mcp"

echo "second-brain · building optional ChatGPT-MCP venv → $VENV"
mkdir -p "$STATE_DIR"
python3 -m venv "$VENV"
"$VENV/bin/pip" install --quiet --upgrade pip
"$VENV/bin/pip" install --quiet mcp
echo "✓ ready. The official mcp SDK is installed in an isolated venv."
echo "  Start the ChatGPT endpoint:  bash mcp/run-chatgpt.sh"
echo "  Turn it off anytime:         rm -rf \"$VENV\""
