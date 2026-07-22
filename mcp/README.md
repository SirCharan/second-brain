# second-brain MCP server

Exposes the vault to other MCP clients — **Claude Desktop**, **Cursor** (local stdio),
and **ChatGPT** (remote HTTP) — so they can recall and capture notes, not just Claude Code.

The core is pure stdlib — no pip, no `mcp` package. One shared tool layer (`sb_core.py`)
behind three transports:
- `server_stdio.py` — JSON-RPC over stdin/stdout (Claude Desktop + Cursor). Stdlib.
- `server_http.py` — the same JSON-RPC over HTTP POST with a bearer token. Stdlib. A
  generic/testing endpoint; **not** for ChatGPT (see below).
- `server_http_sdk.py` — the ChatGPT endpoint: official `mcp` SDK, Streamable-HTTP,
  read-only, no-auth. The one file that needs a pip install, isolated in a venv.

## The 8 tools

| Tool | Kind | Does |
|---|---|---|
| `recall(query, project?, limit?)` | read | Decay-aware keyword ranking (+ optional semantic fill) → top notes |
| `pull(query)` | read | Full-text "unstick" search → the full text of the top matches |
| `export(format?)` | read | Flatten the whole vault into one portable file (`claude`/`chatgpt`/`agents-md`) |
| `health()` | read | Vault audit: counts, missing fields, broken links, orphans, stale |
| `stale(days?)` | read | Active notes not confirmed in N+ days (default 180) |
| `graph(folder?)` | read | Mermaid `[[wikilink]]` link-graph |
| `capture(fact, project?)` | write | Write/update one atomic fact note, then re-index |
| `learn(text, project?)` | write | Curate a research finding / learning as a note, then re-index |

Writes go through `write_note` — full v2 frontmatter + the visual body (H1 → status chip →
callout → `## Related`), secrets scrubbed, folder chosen by `project_for()`, atomic write,
then `regen-index.py --write`. An existing note is enriched with a dated `## Update` section,
never clobbered.

## Install

### Claude Desktop + Cursor (local stdio)

```bash
python3 mcp/mcp-setup.py            # dry-run: preview the config
python3 mcp/mcp-setup.py --write    # merge into both client configs (backs up first)
```

This writes a `second-brain` entry into
`~/Library/Application Support/Claude/claude_desktop_config.json` and `~/.cursor/mcp.json`:

```json
{ "mcpServers": { "second-brain": {
  "command": "/usr/bin/python3",
  "args": ["<abs>/mcp/server_stdio.py"],
  "env": { "CLAUDE_MEMORY_DIR": "<your vault>" }
} } }
```

Restart the client; the `second-brain` tools then appear.

### ChatGPT (remote, Streamable-HTTP, read-only, no-auth)

ChatGPT is the one client that will not accept the stdlib `server_http.py`. It needs the
official `mcp` SDK endpoint (`server_http_sdk.py`), which runs in an isolated venv:

```bash
bash mcp/mcp-http-setup.sh     # one-time: build venv-mcp with `pip install mcp`
bash mcp/run-chatgpt.sh        # start the read-only server + a cloudflared tunnel
```

`run-chatgpt.sh` prints a public `https://…trycloudflare.com` URL. Then, in ChatGPT web
on your account:

1. **Settings → Connectors → Advanced → Developer mode → Create**
2. Paste the tunnel URL. **Authentication: No authentication.**
3. Save. The `second-brain` read tools (`recall`, `pull`, `export`, `health`, `stale`,
   `graph`) appear. The write tools (`capture`, `learn`) are intentionally absent —
   writes stay local via stdio.

Needs `cloudflared` (`brew install cloudflared`).

## Auth: why ChatGPT is no-auth (not bearer)

ChatGPT custom connectors accept **OAuth or no-authentication only — never a static
bearer/API-key** — and expect a proper Streamable-HTTP handshake. So the stdlib
`server_http.py` (bearer) is rejected by ChatGPT; use it only for local testing or a
generic client. The ChatGPT path is `server_http_sdk.py`: read-only + no-auth behind a
tunnel.

**Anyone with the URL can read the vault.** Two mitigations: the endpoint exposes read
tools only (no writes), and for real hardening put **Cloudflare Access** (or a named
tunnel) in front of it instead of the ephemeral quick-tunnel URL.

Claude Desktop and Cursor need none of this — they use the local stdio transport.
