#!/usr/bin/env python3
"""second-brain MCP server — HTTP transport (for ChatGPT / remote clients).

Serves the SAME JSON-RPC 2.0 core (sb_core) over HTTP POST (Streamable HTTP style:
a single JSON response per POST). Pure stdlib http.server. Bearer-token auth via
$SECOND_BRAIN_MCP_TOKEN (generated + printed if unset). GET /health for a liveness probe.

  python3 server_http.py [--port 8765]

NOTE ON CHATGPT: ChatGPT custom connectors generally expect a public HTTPS URL and
full OAuth 2.1 (dynamic client registration) — a static bearer token may NOT satisfy
that flow. Run this behind `cloudflared tunnel` / `ngrok http` for the public URL;
the bearer token is the interim auth. If the connector rejects it, the documented
fallback is the official `mcp` Python SDK in an isolated venv for this one endpoint."""

import sys, os, json, secrets
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import sb_core as C  # noqa: E402

PROTOCOL = "2024-11-05"
TOKEN = os.environ.get("SECOND_BRAIN_MCP_TOKEN") or secrets.token_urlsafe(24)


def _rpc(req):
    """Same dispatch as the stdio server. Returns a response dict or None (notification)."""
    if not isinstance(req, dict):
        return {
            "jsonrpc": "2.0",
            "id": None,
            "error": {"code": -32600, "message": "invalid request"},
        }
    rid = req.get("id")
    method = req.get("method")
    if rid is None:
        return None
    if method == "initialize":
        return {
            "jsonrpc": "2.0",
            "id": rid,
            "result": {
                "protocolVersion": PROTOCOL,
                "capabilities": {"tools": {}},
                "serverInfo": {"name": "second-brain", "version": "0.4.0"},
            },
        }
    if method == "tools/list":
        return {"jsonrpc": "2.0", "id": rid, "result": {"tools": C.TOOLS}}
    if method == "tools/call":
        p = req.get("params") or {}
        text = C.call_tool(p.get("name", ""), p.get("arguments") or {})
        return {
            "jsonrpc": "2.0",
            "id": rid,
            "result": {"content": [{"type": "text", "text": text}]},
        }
    return {
        "jsonrpc": "2.0",
        "id": rid,
        "error": {"code": -32601, "message": "method not found"},
    }


class Handler(BaseHTTPRequestHandler):
    def log_message(self, *a):  # keep stdout clean (it is not the transport here)
        pass

    def _send(self, code, obj):
        body = json.dumps(obj).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        if self.path.rstrip("/") == "/health":
            self._send(200, {"ok": True, "server": "second-brain", "version": "0.4.0"})
        else:
            self._send(404, {"error": "not found"})

    def do_POST(self):
        auth = self.headers.get("Authorization", "")
        if auth != "Bearer " + TOKEN:
            self._send(
                401,
                {
                    "jsonrpc": "2.0",
                    "id": None,
                    "error": {"code": -32001, "message": "unauthorized"},
                },
            )
            return
        try:
            n = int(self.headers.get("Content-Length") or 0)
            req = json.loads(self.rfile.read(n) or b"{}")
        except Exception as e:
            C.HL.log_err("mcp.http.parse", e)
            self._send(
                400,
                {
                    "jsonrpc": "2.0",
                    "id": None,
                    "error": {"code": -32700, "message": "parse error"},
                },
            )
            return
        try:
            resp = _rpc(req)
        except Exception as e:
            C.HL.log_err("mcp.http.rpc", e)
            resp = {
                "jsonrpc": "2.0",
                "id": None,
                "error": {"code": -32603, "message": "internal error"},
            }
        # notifications get a bare 202
        self._send(200 if resp is not None else 202, resp if resp is not None else {})


def main():
    port = 8765
    if "--port" in sys.argv:
        try:
            port = int(sys.argv[sys.argv.index("--port") + 1])
        except Exception:
            pass
    print("second-brain MCP (HTTP) on :%d" % port)
    print("  vault : %s" % C.MEM)
    print("  token : %s" % TOKEN)
    print("  health: GET  http://localhost:%d/health" % port)
    print("  rpc   : POST http://localhost:%d/  (Authorization: Bearer <token>)" % port)
    print(
        "  public: run `cloudflared tunnel --url http://localhost:%d` for an HTTPS URL"
        % port
    )
    ThreadingHTTPServer(("0.0.0.0", port), Handler).serve_forever()


if __name__ == "__main__":
    main()
