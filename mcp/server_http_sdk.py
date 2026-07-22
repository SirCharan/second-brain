#!/usr/bin/env python3
"""second-brain MCP server — ChatGPT endpoint (Streamable-HTTP, READ-ONLY, NO auth).

READ-ONLY BY DESIGN. Registers only the six read tools from sb_core
(recall, pull, export, health, stale, graph). The write tools (capture, learn)
are deliberately omitted — writes stay local via the stdio server. So the worst a
holder of the public URL can do is read your vault (mitigate with Cloudflare Access
or a named tunnel; see mcp/README.md).

WHY THE SDK + NO AUTH: ChatGPT custom connectors (Settings → Connectors → Advanced →
Developer mode) accept OAuth or NO-AUTH only — NOT a static bearer/API-key — and expect
a proper Streamable-HTTP handshake. The hand-rolled stdlib server_http.py (bearer) is
rejected by ChatGPT; this file uses the official `mcp` SDK's Streamable-HTTP transport
with no auth, and is meant to run behind a cloudflared tunnel.

This is the ONE file in the repo allowed to import a non-stdlib package (`mcp`), and only
because it runs under the isolated venv built by mcp-http-setup.sh (venv-mcp). Everything
else stays pure stdlib.

  # build the venv first:  bash mcp/mcp-http-setup.sh
  $SECOND_BRAIN_STATE_DIR/venv-mcp/bin/python mcp/server_http_sdk.py
  # or just:              bash mcp/run-chatgpt.sh

SDK VERSION ASSUMPTION: written against the official `mcp` Python SDK's FastMCP API
(mcp >= 1.9, which added the streamable-http transport). FastMCP(host, port) + @mcp.tool()
+ mcp.run(transport="streamable-http"). If the installed SDK differs, the orchestrator can
smoke-test and adjust these three call sites."""

import os, sys

# same both-mode import shim the other servers use: sb_core self-locates _hooklib.
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import sb_core as C  # noqa: E402

from mcp.server.fastmcp import FastMCP  # noqa: E402  (non-stdlib; venv-mcp only)

PORT = int(os.environ.get("SECOND_BRAIN_MCP_PORT") or 8765)

mcp = FastMCP("second-brain", host="127.0.0.1", port=PORT)


# --- READ tools only. Each just forwards to sb_core (no logic here). ---
@mcp.tool()
def recall(query: str, project: str = "", limit: int = 5) -> str:
    """Recall the most relevant vault notes for a query (decay-aware keyword ranking)."""
    return C.recall(query, project or None, limit)


@mcp.tool()
def pull(query: str) -> str:
    """Full-text 'unstick' search: full text of the top matching notes across the vault."""
    return C.pull(query)


@mcp.tool()
def export(format: str = "claude") -> str:
    """Flatten the whole vault into one portable context file. format: claude|chatgpt|agents-md."""
    return C.export(format)


@mcp.tool()
def health() -> str:
    """Audit the vault: counts, missing fields, broken links, orphans, stale notes."""
    return C.health()


@mcp.tool()
def stale(days: int = 180) -> str:
    """List active notes not confirmed in N+ days (default 180)."""
    return C.stale(days)


@mcp.tool()
def graph(folder: str = "") -> str:
    """Emit a Mermaid link-graph of the vault (optionally one folder)."""
    return C.graph(folder or None)


if __name__ == "__main__":
    print(
        "second-brain MCP (Streamable-HTTP, read-only, no-auth) on 127.0.0.1:%d" % PORT
    )
    print("  vault : %s" % C.MEM)
    print("  tools : recall, pull, export, health, stale, graph  (writes stay local)")
    print("  public: run `cloudflared tunnel --url http://127.0.0.1:%d`" % PORT)
    mcp.run(transport="streamable-http")
