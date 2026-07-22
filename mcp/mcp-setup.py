#!/usr/bin/env python3
"""second-brain MCP — client setup. Prints (default) or applies (--write) the config
for Claude Desktop + Cursor stdio, and prints the ChatGPT (HTTP) instructions.

  python3 mcp-setup.py            # dry-run: print what would change
  python3 mcp-setup.py --write    # merge into the client configs (backs up first)

Stdlib only. Idempotent: re-running just re-writes the same second-brain block."""

import os, sys, json, shutil, time

_THIS = os.path.dirname(os.path.abspath(__file__))
SERVER = os.path.join(_THIS, "server_stdio.py")
HTTP_SERVER = os.path.join(_THIS, "server_http.py")
HOME = os.path.expanduser("~")
MEM = os.environ.get("CLAUDE_MEMORY_DIR") or os.path.join(
    HOME, ".claude/second-brain-vault"
)
WRITE = "--write" in sys.argv

CLIENTS = {
    "Claude Desktop": os.path.join(
        HOME, "Library/Application Support/Claude/claude_desktop_config.json"
    ),
    "Cursor": os.path.join(HOME, ".cursor/mcp.json"),
}

ENTRY = {
    "command": "/usr/bin/python3",
    "args": [SERVER],
    "env": {"CLAUDE_MEMORY_DIR": MEM},
}


def merge(path):
    """Merge the second-brain server into an existing config, preserving other servers."""
    cfg = {}
    if os.path.isfile(path):
        try:
            cfg = json.load(open(path))
        except Exception:
            cfg = {}
    cfg.setdefault("mcpServers", {})
    cfg["mcpServers"]["second-brain"] = ENTRY
    return cfg


def main():
    print("second-brain MCP setup  (%s)\n" % ("--write" if WRITE else "dry-run"))
    print("  server : %s" % SERVER)
    print("  vault  : %s\n" % MEM)

    for name, path in CLIENTS.items():
        cfg = merge(path)
        if WRITE:
            os.makedirs(os.path.dirname(path), exist_ok=True)
            if os.path.isfile(path):
                shutil.copy2(path, path + ".bak-%d" % int(time.time()))
            with open(path, "w") as f:
                json.dump(cfg, f, indent=2)
            print("  [written] %s: %s" % (name, path))
        else:
            print("  [%s] would write %s:" % (name, path))
            print(json.dumps({"mcpServers": {"second-brain": ENTRY}}, indent=2))
        print()

    print("ChatGPT (remote HTTP — no local file):")
    print("  1. Start:  SECOND_BRAIN_MCP_TOKEN=<pick-one> python3 %s" % HTTP_SERVER)
    print(
        "  2. Tunnel: cloudflared tunnel --url http://localhost:8765   (public HTTPS URL)"
    )
    print("  3. In ChatGPT, add a custom connector pointing at that URL,")
    print("     Authorization: Bearer <token>.")
    print("  CAVEAT: ChatGPT connectors may require full OAuth 2.1 + dynamic client")
    print("  registration; the bearer token is interim. See mcp/README.md.")
    if WRITE:
        print("\nDone. Restart Claude Desktop / Cursor to load the second-brain tools.")


if __name__ == "__main__":
    main()
