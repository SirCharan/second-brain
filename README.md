# second-brain

A file-based **second brain for [Claude Code](https://claude.com/claude-code)**. Hooks quietly
capture every session into an Obsidian-compatible Markdown vault, recall the relevant notes into
new prompts, and snapshot state before the context window compacts — so Claude picks up where you
left off across sessions, projects, and machines. A `/second-brain` skill lets you curate, search,
and audit the vault.

No database, no server, no Obsidian plugins at runtime. Just Markdown files with `[[wikilinks]]`,
YAML frontmatter, and a handful of stdlib-only Python/bash hooks. Open the vault in
[Obsidian](https://obsidian.md) if you want the graph view — it's plain Markdown either way.

## How it works

```
Each session start   →  inject "where you left off" + relevant notes into the chat
Each prompt          →  recall notes matching the prompt (decay-aware ranking)
Each reply           →  journal a one-line capture into Daily/
Before compaction    →  snapshot the live task/files/errors so nothing is lost
On demand            →  /second-brain capture · consolidate · find · pull · health · …
```

The capture journal (`Daily/`) is the firehose; **curated atomic notes** are the distilled memory.
`/second-brain consolidate` turns the former into the latter. Notes are never auto-deleted — stale
facts are retired via `status: retired` + `supersedes`, so the whole vault is git-auditable.

## Install

### Option A — Claude Code plugin (recommended)

```
/plugin marketplace add SirCharan/second-brain
/plugin install second-brain
```

Then create your vault (the plugin ships the machinery, not your data):

```bash
export CLAUDE_MEMORY_DIR="$HOME/.claude/second-brain-vault"   # add to your shell profile
mkdir -p "$CLAUDE_MEMORY_DIR"
# optional: seed it with the starter layout + config from this repo
#   cp -R vault-template/. "$CLAUDE_MEMORY_DIR/"
```

> The hooks no-op silently until `$CLAUDE_MEMORY_DIR` points at an existing directory, so nothing
> breaks before you create the vault. Restart Claude Code after setting the variable.

### Option B — install script (no plugin system)

```bash
git clone https://github.com/SirCharan/second-brain
cd second-brain
./install.sh
```

`install.sh` copies the hooks/skill/workflow into `~/.claude/`, creates the vault from
`vault-template/`, seeds `config.json`, and merges the hook registrations into
`~/.claude/settings.json` (backing it up first). It's idempotent — re-run it to upgrade.

## Configuration

Everything is optional. An empty `config.json` (`{}`) works — notes land in the vault root and
folders auto-discover. Edit `$CLAUDE_MEMORY_DIR/config.json` to route repos into folders:

| Field | Type | What it does |
|---|---|---|
| `project_map` | `{basename: folder}` | Exact repo/dir name → memory folder (routes captures) |
| `project_prefixes` | `{prefix: folder}` | Basename prefix → folder, for families of repos |
| `domains` | `{folder: [domain, title]}` | Groups folders under domain headings in `MEMORY.md` |
| `domain_order` | `[[domain, heading], …]` | Order + emoji headings for the TOC |
| `ignore_names` | `[string, …]` | Wikilink targets with no note file (silences lint warnings) |
| `project_meta` | `{folder: [repo, url, path, desc]}` | Renders a project table via `/second-brain index` |

See [`config.example.json`](config.example.json) for a worked example.

## The `/second-brain` skill

| Subcommand | Does |
|---|---|
| `capture "<fact>"` | Write/update one atomic note, re-index |
| `learn "<text>"` | Curate a research finding or learning now |
| `consolidate` | Distill the `Daily/` journal + promote-queue into curated notes |
| `reconcile` | Find contradicting notes, set supersedes/retired |
| `link` | Insert missing `[[wikilinks]]` on orphan notes |
| `review` | Weekly rollup into today's Daily note |
| `health` | Audit: counts, missing fields, broken links, orphans, stale |
| `find "<query>"` | Ranked grep search over note titles/descriptions |
| `pull "<query>"` | Full-text search returning the matching notes' full text (use when stuck) |
| `prune` | Propose (never auto-apply) archive/merge candidates |
| `migrate` | Backfill frontmatter to v2 on older notes |
| `index` | Rebuild the `_system/` folder + project table |
| `doctor [--fix]` | Self-test the install; `--fix` repairs dirs and drift |

## Vault conventions

- **One concept per note.** Dense `[[wikilinks]]`. Keep prose hubs (`_MOC-*`) separate from facts.
- **Frontmatter v2:** `name` (immutable kebab slug — links depend on it), `title`, `description`,
  `tags: [domain, project/x, type/y]`, `asserted`, `last_confirmed`, `source`, `confidence`,
  `status`, `supersedes`, `metadata.type`.
- **Body:** `# Title` → emoji status chip (🟢 active / 🟡 watch / ⚫ retired / 🔴 real-money) →
  colored callouts (`> [!danger|warning|tip|info]`) wrapping the key facts → `## Related`.
- **Never delete.** Retire + supersede. Newest confirmed fact wins.

`vault-template/example/` contains a worked example note — read it, then delete the folder.

## Reliability

Hooks are built to stay out of your way: pinned to `/usr/bin/python3` (pyenv-proof),
`timeout`-bounded, atomic writes (temp + `os.replace`), transcript **tail**-reads (never load a
20MB transcript), a `hook-errors.log` for silent failures, and `vault_ok()` no-op guards. Pure
stdlib — no pip installs.

## Privacy

The vault is **your** data and is git-ignored by this repo. The machinery ships with zero personal
content. Optionally mirror the vault into your Obsidian app folder by setting
`SECOND_BRAIN_OBSIDIAN_LINK` to that path (then `doctor --fix` maintains the symlink).

## License

Apache-2.0. See [LICENSE](LICENSE).
