#!/usr/bin/env python3
"""second-brain MCP server — stdio transport (Claude Desktop + Cursor).

Newline-delimited JSON-RPC 2.0 over stdin/stdout, pure stdlib. Implements the
three methods a client needs: initialize, tools/list, tools/call. Notifications
(no id) are ignored. Never crashes on bad input; failures go to the hook error log."""

import sys, os, json

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import sb_core as C  # noqa: E402

PROTOCOL = "2024-11-05"


def _result(rid, result):
    return {"jsonrpc": "2.0", "id": rid, "result": result}


def _error(rid, code, msg):
    return {"jsonrpc": "2.0", "id": rid, "error": {"code": code, "message": msg}}


def handle(req):
    """Return a response dict, or None for notifications (no reply)."""
    if not isinstance(req, dict):
        return _error(None, -32600, "invalid request")
    rid = req.get("id")
    method = req.get("method")
    if rid is None:  # notification
        return None
    if method == "initialize":
        return _result(
            rid,
            {
                "protocolVersion": PROTOCOL,
                "capabilities": {"tools": {}},
                "serverInfo": {"name": "second-brain", "version": "0.4.0"},
            },
        )
    if method == "tools/list":
        return _result(rid, {"tools": C.TOOLS})
    if method == "tools/call":
        params = req.get("params") or {}
        text = C.call_tool(params.get("name", ""), params.get("arguments") or {})
        return _result(rid, {"content": [{"type": "text", "text": text}]})
    return _error(rid, -32601, "method not found: %s" % method)


def main():
    out = sys.stdout
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        try:
            req = json.loads(line)
        except Exception as e:
            C.HL.log_err("mcp.stdio.parse", e)
            out.write(json.dumps(_error(None, -32700, "parse error")) + "\n")
            out.flush()
            continue
        try:
            resp = handle(req)
        except Exception as e:
            C.HL.log_err("mcp.stdio.handle", e)
            resp = _error(
                req.get("id") if isinstance(req, dict) else None,
                -32603,
                "internal error",
            )
        if resp is not None:
            out.write(json.dumps(resp) + "\n")
            out.flush()


if __name__ == "__main__":
    main()
