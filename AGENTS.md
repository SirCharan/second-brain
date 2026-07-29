# Repository conventions

Read this before changing anything here. It applies to humans and to coding agents.

## What this repo is

A file-based memory system for Claude Code: hooks capture sessions into a Markdown vault,
recall pulls relevant notes into new prompts, and a skill curates the result. The product is
the vault; the code exists to keep it correct without anyone maintaining it by hand.

## Hard constraints

**Stdlib only in the core.** Hooks, skill scripts, and the stdio MCP server import nothing
outside the standard library. CI enforces this by compiling and testing with no package
index. Optional extras (semantic recall, the HTTP MCP server) live behind their own venvs.

**Python 3.8+, macOS and Linux.** Both platforms run a real install in CI. Never hardcode
`/usr/bin/python3`; resolve the interpreter or use `sys.executable`. Avoid GNU-only tools —
`timeout`, `sed -i ''`, `stat -f`, and `readlink -f` all differ or are missing on one side.

**One vault path.** Everything reads `CLAUDE_MEMORY_DIR`. A hardcoded vault path is a bug;
it once split the system across two vaults for six days without any error.

**One transcript parser.** `_hooklib.scan_transcript()`. Three copies of that loop already
drifted, and the 256 KB window in one of them silently dropped the largest turns.

**One ranker.** `sb_rank.rank()`. The MCP tool layer used to carry its own copy, and it had
drifted to globbing a single directory level — so notes at the vault root and in nested
folders never ranked for Claude Desktop or Cursor.

**Measure ranking changes.** Retrieval quality has a number now: `tests/eval`. Run it
before and after any change to scoring, the note walk, or the index, and quote the delta in
the pull request. Baseline and the follow-up measurements are in `tests/eval/README.md`.

## Hook rules

Hooks run on every prompt, so they must be invisible when healthy:

- never raise — wrap and `log_err`
- never block — warn and return, unless the hook is deliberately a permission gate
- finish inside the timeout declared in `install.sh`; detach slow work
- degrade to a no-op when the vault is absent (`vault_ok()`)
- write atomically (`atomic_write`), because a reader may be mid-parse

## Note conventions

Notes carry v2 frontmatter and a fixed body shape: `# H1`, a status chip, callouts around
the load-bearing facts, and a `## Related` section linking the folder's `_MOC-` hub. Full
spec ships in `vault-template/_infra/note-conventions.md`.

Two rules matter most. **Enrich, never rewrite** — preserve every number, path, and hash
verbatim. **Supersede, never delete** — set `status: retired` and point `supersedes` at the
replacement, so history stays auditable.

Keep notes at or under 4 KB, 8 KB hard. Recall injects several per prompt, so a large note
crowds the context and blurs its own embedding. Split at the seams and link the pieces.

## Prose

Docs and note bodies use short active sentences, one idea each, concrete values over vague
ones ("within 5s", not "quickly"), and one term per concept. No filler, no AI-slop phrasing,
no throat-clearing introductions or summary conclusions.

## Before you claim it works

- `python3 -m pytest hooks -q` and `python3 mcp/test_mcp.py`
- install into a throwaway `HOME` and run `doctor --strict` (see CONTRIBUTING.md)
- if you touched the installer, watch the `install-smoke` job on both platforms
- version lives in `VERSION` alone — never add a second copy
