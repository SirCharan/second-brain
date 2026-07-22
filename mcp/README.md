# second-brain MCP server

Exposes the vault to other MCP clients — **Claude Desktop**, **Cursor** (local stdio),
and **ChatGPT** (remote HTTP) — so they can recall and capture notes, not just Claude Code.

Pure stdlib. No pip, no `mcp` package. One shared tool layer (`sb_core.py`) behind two
transports: `server_stdio.py` (JSON-RPC over stdin/stdout) and `server_http.py`
(the same JSON-RPC over HTTP POST).

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

### ChatGPT (remote HTTP)

```bash
SECOND_BRAIN_MCP_TOKEN=<pick-one> python3 mcp/server_http.py        # :8765
cloudflared tunnel --url http://localhost:8765                       # public HTTPS URL
```

Add a custom connector in ChatGPT pointing at the tunnel URL, with
`Authorization: Bearer <token>`. `GET /health` is a liveness probe.

## OAuth caveat (ChatGPT)

ChatGPT custom connectors generally expect a **public HTTPS URL and full OAuth 2.1**
(with dynamic client registration). A static **bearer token may not satisfy** that flow —
it is the interim auth here. If the connector rejects the bearer token, the documented
fallback is to add the official `mcp` Python SDK in an isolated venv (mirroring
`skills/second-brain/scripts/embed-setup.sh`) for that one endpoint. Claude Desktop and
Cursor need none of this — they use the local stdio transport.
