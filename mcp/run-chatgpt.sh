#!/usr/bin/env bash
# Start the second-brain ChatGPT MCP endpoint: the read-only Streamable-HTTP server
# (server_http_sdk.py, under venv-mcp) + a cloudflared tunnel for a public HTTPS URL.
#
#   bash mcp/run-chatgpt.sh
#
# Then in ChatGPT (web, your account): Settings → Connectors → Advanced → Developer mode
# → Create → paste the https://… trycloudflare URL printed below, Auth = No authentication.
# The `second-brain` read tools (recall, pull, export, health, stale, graph) then appear.
set -euo pipefail

STATE_DIR="${SECOND_BRAIN_STATE_DIR:-$HOME/.second-brain}"
VENV="$STATE_DIR/venv-mcp"
PY="$VENV/bin/python"
PORT="${SECOND_BRAIN_MCP_PORT:-8765}"
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# --- preflight ---
if [ ! -x "$PY" ]; then
  echo "✗ venv-mcp missing ($VENV). Build it first:  bash mcp/mcp-http-setup.sh" >&2
  exit 1
fi
if ! command -v cloudflared >/dev/null 2>&1; then
  echo "✗ cloudflared not installed. Install it:  brew install cloudflared" >&2
  exit 1
fi

# --- launch the server in the background, stop it on exit ---
echo "→ starting read-only MCP server on 127.0.0.1:$PORT"
"$PY" "$HERE/server_http_sdk.py" &
SERVER_PID=$!
trap 'kill "$SERVER_PID" 2>/dev/null || true' EXIT
sleep 2

echo "→ opening cloudflared tunnel (public HTTPS URL below; Auth = No authentication in ChatGPT)"
echo
cloudflared tunnel --url "http://127.0.0.1:$PORT"
