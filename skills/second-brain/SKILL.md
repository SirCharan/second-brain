---
name: second-brain
description: Manage your Obsidian-compatible Claude memory vault — capture, consolidate, reconcile, link, review, health-audit, find, and prune notes. Use when you type /second-brain <subcommand>, or ask to tidy/curate/search memory, distill the Daily journal into notes, find contradictions, or check memory health. The vault is a plain folder of Markdown notes ($CLAUDE_MEMORY_DIR), driven by hooks — NO Obsidian plugins at runtime.
---

# /second-brain — memory vault operations

The vault lives at `$CLAUDE_MEMORY_DIR` (default `~/.claude/second-brain-vault`; open it in Obsidian if you like — the notes are plain `[[wikilinked]]` Markdown). Atomic notes in project folders + meta folders; `MEMORY.md` = thin index; per-folder `_MOC-*` hubs + `_Home`; `Daily/` = auto-captured exchange journal. Frontmatter v2: `name, description, tags:[domain, project/x, type/y], asserted, last_confirmed, source, confidence, status, supersedes, metadata.type`. Project→folder routing and domain grouping come from the vault's `config.json` (see `config.example.json`).

**Core rules:**
- **Never auto-delete.** Retire/supersede via frontmatter (`status: retired`, `supersedes: [[old]]`); pruning only *proposes* archive/merge for you to confirm. Git-auditable.
- **Deterministic recency**, not LLM-judged: newest fact wins; bump `last_confirmed` when re-confirmed.
- **Atomic**: one concept/claim per note; dense `[[wikilinks]]`; keep prose MOCs separate from facts.
- **Distill, don't dump**: consolidation merges/updates existing notes rather than appending duplicates.

Dispatch on the argument after `/second-brain`:

- **VISUAL FORMAT (applies to every note written/updated by `capture`/`learn`/`consolidate`)**: full v2 frontmatter incl. `title` + clean `description`; body = `# <Human Title>` H1 → emoji status chip (`🟢 active`/`🟡 watch`/`⚫ retired`/`🔴 real-money`) → content with colored callouts (`> [!danger]`/`[!warning]`/`[!tip]`/`[!info]`) wrapping key facts → `## Related` with `[[_MOC-<folder>]]` + related notes. Hubs get a ```mermaid``` graph. ENRICH, never rewrite — preserve every fact. Batch/whole-vault re-format = the `vault-enrich` workflow.
- **capture `<fact>`** — write a new atomic note (or update an existing one) in the VISUAL FORMAT above (full v2 frontmatter + H1/status-chip/callouts + `[[links]]` to its `_MOC` and hubs); then run `regen-index.py --write`. Pick folder by project, tags by scheme.
- **learn `<text>`** — curate a research finding or learning **now**: write/update an atomic note in the relevant project folder in the VISUAL FORMAT (v2 frontmatter, `source: research|user`, `confidence`, H1 + status chip + callouts, `[[links]]` to its `_MOC`+hub), supersede-don't-duplicate, then `regen-index.py --write`. This is the on-demand form of the auto write-now rule.
- **consolidate** — first **sweep `_infra/_promote-queue.md`**: for each unchecked `- [ ]` research/learning item, ensure a curated atomic note exists (create/update in its project folder) and flip it to `- [x]`. Then read the last ~2 days of `Daily/*.md`, extract durable decisions/facts/patterns, and **upsert** into curated notes (rewrite if it deepens/contradicts; else create). Mark superseded facts (`status: retired` + `supersedes`), never delete. Then `regen-index.py --write`. Return a short summary only.
- **reconcile** — scan for contradictions across notes (same topic, conflicting claims); set `supersedes`/`status: retired` on the losers, bump `last_confirmed` on the winner. Report the diffs; never silently overwrite.
- **link** — run `health.py`, then for orphan/under-linked notes surface + insert the missing `[[wikilinks]]` (to `_MOC`, hubs, related notes).
- **review** — weekly rollup: read recent `Daily/` + recently-`last_confirmed` notes; write a dated `## Review` block into today's Daily (what changed, open threads, promotion candidates).
- **health** — run `scripts/health.py` and relay: counts, missing v2 fields, broken wikilinks, orphans, stale (>120d), retired.
- **find `<query>`** — run `scripts/find.py <query>` (grep-based ranked search); relay top hits.
- **prune** — run `health.py`; from stale/orphan/duplicate candidates, **propose** a table of archive/merge/retire actions for you to confirm. Apply only what's approved, via `status`/`supersedes` (move to an `_archive/` folder at most — never `rm`).
- **migrate** — run `scripts/migrate-frontmatter.py` to backfill v2 fields on any notes missing them (idempotent).
- **index** — run `scripts/build-system-index.py` to (re)generate the `_system/` folder (CLAUDE.md copy, one note per skill + per workflow, `_MOC-system`) and, if `config.json` has `project_meta`, `_projects.md` + per-MOC Links blocks. Refresh after adding skills/projects or editing CLAUDE.md.
- **pull `<query>`** — the **unstick** search: run `scripts/pull.py <query>` to grep the ENTIRE vault (notes + `Daily/` captures + `_system/`) and return the FULL text of the top matches. Use when blocked — a recurring error, "how did we do X", a forgotten detail — to get the actual answer/fix, not just a title.
- **doctor** — run `scripts/doctor.py` and relay the report (install mode + hooks dir, interpreter, optional vault symlink, writable dirs, hook files + registration + timeouts, migration drift, hook-errors.log tail). Pass `--fix` to recreate dirs and migrate drift. Run this first whenever memory "feels broken". Works for BOTH the plugin and install.sh layouts.
- **dump** — run the bundled `context-dump.py` hook (`${CLAUDE_PLUGIN_ROOT}/hooks/context-dump.py`, or `hooks/context-dump.py` for an install.sh setup) to write a resume digest of the current session to `_infra/_carryover.md` before a `/clear`; the next session's `session-resume` reloads it. This is the action the context-monitor nudge points at.
- **export `[--format claude|chatgpt|agents-md] [--out PATH] [--folder NAME]`** — run `scripts/export.py`; flatten the whole vault into ONE portable context file to hand to any assistant (ChatGPT / Gemini / Grok / a fresh Claude) or drop into an `AGENTS.md`. This is the "one brain feeds every model" primitive.
- **graph `[--folder NAME] [--min-degree N]`** — run `scripts/graph.py`; emit a Mermaid `[[wikilink]]` link-graph of the vault to paste into Obsidian or any Markdown.
- **stale `[--days N] [--folder NAME]`** — run `scripts/stale.py`; list active notes not confirmed in N+ days (default 180), oldest first, so you can re-confirm, retire, or prune them (surfaces the decay the recall ranker already uses).
- **embed-setup** — run `bash scripts/embed-setup.sh` to enable OPTIONAL semantic recall (builds an isolated venv with `fastembed`). The core is pure stdlib; this is the one opt-in extra. Recall/resume auto-use it once present, and degrade cleanly to keyword-only without it.

## MCP server
A pure-stdlib MCP server lives in `mcp/` at the repo root. It exposes the vault to OTHER clients — Claude Desktop + Cursor (local stdio) and ChatGPT (remote HTTP) — with 8 tools: `recall`, `pull`, `export`, `health`, `stale`, `graph` (read) and `capture`, `learn` (write, via a v2-note writer). Install per client with `python3 mcp/mcp-setup.py --write`. Details in `mcp/README.md`.

## Reliability (built-in)
Hooks are hardened for uptime: pinned to `/usr/bin/python3` (pyenv-proof), `timeout`-bounded in settings.json, atomic writes (temp+`os.replace`) on the index/state/notes, transcript **tail**-reads (not full-file), a `hook-errors.log` (under `$SECOND_BRAIN_STATE_DIR`, default `~/.second-brain/`) for silent failures, and `vault_ok()` no-op guards (so hooks stay silent until a vault exists). Shared helpers live in `_hooklib.py` next to the hooks (self-locating — works in both the plugin and install.sh layouts).

Scripts live in `scripts/` next to this file. They are deterministic helpers; the LLM does the judgement (consolidate/reconcile/link/review/prune). Always `tar`-backup the vault before a bulk write.
