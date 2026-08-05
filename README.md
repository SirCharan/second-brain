# second-brain

[![CI](https://github.com/SirCharan/second-brain/actions/workflows/ci.yml/badge.svg)](https://github.com/SirCharan/second-brain/actions/workflows/ci.yml)
[![License](https://img.shields.io/badge/license-Apache--2.0-blue.svg)](LICENSE)
[![Version](https://img.shields.io/badge/version-0.6.0-informational.svg)](CHANGELOG.md)
[![Platforms](https://img.shields.io/badge/platforms-macOS%20%7C%20Linux%20%7C%20Windows-lightgrey.svg)](#requirements)

A file-based **second brain for [Claude Code](https://claude.com/claude-code)**. Hooks quietly
capture every session into an Obsidian-compatible Markdown vault, recall the relevant notes into
new prompts, and snapshot state before the context window compacts — so Claude picks up where you
left off across sessions, projects, and machines. A `/second-brain` skill lets you curate, search,
and audit the vault.

No database, no server, no Obsidian plugins at runtime. Just Markdown files with `[[wikilinks]]`,
YAML frontmatter, and a handful of stdlib-only Python/bash hooks. Open the vault in
[Obsidian](https://obsidian.md) if you want the graph view — it's plain Markdown either way.

> **Want just the hooks?** [continuum](https://github.com/SirCharan/continuum) is the stripped-down
> sibling of this repo — the same idea in stdlib Python, with no plugin manifest, no MCP server and
> no test suite. Start there if you want to read the whole thing in one sitting, or start here if
> you want the parts that make it hold up over months of daily use.
>
> | | continuum | second-brain |
> |---|---|---|
> | Install | clone + `./install.sh` | one-line `curl \| bash` |
> | Capture, recall, compaction snapshot | yes | yes |
> | Skill | `/obsidian` | `/second-brain` |
> | Claude Code plugin manifest | no | yes |
> | MCP server | no | yes |
> | Workflows (`vault-enrich`) | no | yes |
> | Tests + CI | no | yes, macOS and Linux |
> | License | MIT | Apache-2.0 |

## Why

Every AI vendor is racing to remember you — and to make sure that memory only works inside *their*
walls. ChatGPT's memory can't leave ChatGPT (it isn't even in the data export); Claude's lives on
Anthropic's servers; Gemini's is tied to your Google account. Your accumulated context becomes their
moat, and every new session still starts from zero.

second-brain flips that. Your memory is a folder of plain Markdown on **your** disk, so:

- **You own it and can switch models freely** — move between ChatGPT, Claude, Gemini, and Grok and
  your memory comes with you, because it was never trapped in any of them.
- **One brain feeds every model** — the same vault is readable by any assistant; nothing is siloed.
  `/second-brain export` flattens it into one portable file to hand to ChatGPT, Gemini, or Grok.
- **Never run out of context, never compact, never waste tokens** — memory lives in the vault, not
  the window, so only the relevant notes are recalled into each prompt. You can `/clear` and start
  fresh cheaply instead of sitting through a slow, lossy compaction or re-paying for a bloated
  transcript every turn. The index is *sharded* too, so `MEMORY.md` never overflows the read limit.
- **Skills compound across projects** — it's one linked vault, not per-project silos, so a trick
  learned in project A surfaces (and links in) when you work on project B — like neurons wiring up.
- **Sessions stop resetting** — captured automatically, recalled automatically, and if this tool
  vanished tomorrow you'd still have every file.

The full argument — who it's for, the competitive landscape, and where it honestly *doesn't* win —
is in **[POSITIONING.md](POSITIONING.md)**.

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

## Requirements

Claude Code and Python 3.8 or newer. macOS, Linux and Windows are each tested in CI on every
commit.

The hooks are Python and are registered to run under your Python interpreter directly, so
`bash` is not required. The `.sh` wrappers in `hooks/` are a convenience for running a hook by
hand on macOS or Linux; nothing depends on them.

**Windows.** Use `install.ps1` in PowerShell:

```powershell
irm https://charandeepkapoor.com/second-brain/install.ps1 | iex
```

(Redirects to `install.ps1` on `main`; the direct path is
`https://raw.githubusercontent.com/SirCharan/second-brain/main/install.ps1`.)

Two things differ. Semantic recall's setup script (`embed-setup.sh`) is bash, so that optional
extra is macOS and Linux only — keyword recall, which is the default, works everywhere. And
mirroring the vault into an existing Obsidian folder via `SECOND_BRAIN_OBSIDIAN_LINK` uses a
directory junction rather than a symlink, because Windows refuses symlinks without Developer
Mode; `doctor.py --fix` handles that automatically and warns rather than fails if both are
blocked. WSL2 also works, using the normal `install.sh`.

## Install

```bash
curl -fsSL https://charandeepkapoor.com/second-brain/install.sh | bash
```

(The URL redirects to `install.sh` on `main` in this repo — same script. Fetch it from
`https://raw.githubusercontent.com/SirCharan/second-brain/main/install.sh` if you prefer the
direct path.)

That copies the hooks, skill, workflow and MCP server into `~/.claude/`, creates your vault from
`vault-template/`, registers the hooks in `~/.claude/settings.json`, and then runs a short
setup wizard that finds your git repositories, writes the routing config, offers to connect
Claude Desktop and Cursor, and ends with a live capture test.

**Mac app.** Prefer clicking to pasting? Download
[Second-Brain-Setup.dmg](https://github.com/SirCharan/second-brain/releases/latest/download/Second-Brain-Setup.dmg)
— a 7-step setup wizard that runs the same installer. The app is unsigned: right-click → Open the
first time, or clear the quarantine flag with
`xattr -dr com.apple.quarantine "/Applications/Second Brain Setup.app"`.

The full walkthrough lives at
[charandeepkapoor.com/second-brain/get-started](https://charandeepkapoor.com/second-brain/get-started).

Restart Claude Code afterwards so the hooks load. Then just work normally — sessions are
captured without you doing anything.

**What it touches.** Six paths, all recorded in `$CLAUDE_MEMORY_DIR/_infra/_install-manifest.json`:
`~/.claude/hooks/`, `~/.claude/skills/second-brain/`, `~/.claude/workflows/vault-enrich.js`,
`~/.claude/mcp/`, your vault, and `~/.claude/settings.json` (backed up to `settings.json.bak`
first). Existing
hooks and settings are merged, never replaced. Re-run it any time to upgrade. Accepting the
optional starter pack below adds skill directories under `~/.claude/skills/`, which are recorded
in the same manifest. The pack's source is installed alongside the skill, so you can add another
tier later without cloning the repo again.

Prefer to read the script before running it? Clone and run it locally:

```bash
git clone https://github.com/SirCharan/second-brain && ./second-brain/install.sh
```

Useful flags: `--dry-run` (show what would happen), `--no-setup` (skip the wizard),
`--pack=core|core,writing|all|none` (answer the starter-pack question up front).

### Starter pack (optional)

A new vault is nearly empty. The graph is the reason to open it in Obsidian at all, and on day
one it has about six nodes. The wizard offers a starter pack to fix that. Say no and nothing
changes: the pack is not required for memory to work.

| Tier | What you get |
|---|---|
| `core` | `gtan-workflow` (Garry Tan's GStack loop, bound to plans in your vault), `discovery` (interview before building), `working-with-claude`, `build-tdd`, `code-review-discipline`, plus the `vault-restructure` workflow |
| `writing` | `writing-router`, `writing-composition`, `writing-eval`, `simplified-technical-english` |
| `design` | `design-router`, `design-system`, `anti-slop-design-law`, `anti-slop-design-audit`, `layout-interaction-design`, `motion-3d`, `dataviz-design`, and the per-type recipes for reports, landing pages, docs sites and calculators |

It also seeds a `_playbook/` folder with the working rules those skills assume, plus two note
templates. An `.obsidian/` config sets graph colour groups per folder and a dark theme. Core
Obsidian features only, no community plugins.

```bash
python3 ~/.claude/skills/second-brain/scripts/starter-pack.py --list          # see everything first
python3 ~/.claude/skills/second-brain/scripts/starter-pack.py --tiers core    # install one tier
```

**Nothing is overwritten.** A skill directory, vault note or `.obsidian/` you already have is
left exactly as it is, so the script is safe to re-run. Installed paths are recorded in the
install manifest, so `uninstall.sh` removes them too.

**Third-party packs are not redistributed.** Several of these skills route into work by other
people — GStack, superpowers, ui-ux-pro-max, stop-slop and others. `starter-pack/manifest.json`
lists each with its author, licence and install command, and the installer prints that list
rather than vendoring anyone's code into this repo.

### Verify

```bash
python3 ~/.claude/skills/second-brain/scripts/doctor.py
```

It reports what is configured and prints the exact command for anything that is not.

### Uninstall

```bash
bash uninstall.sh                 # removes the machinery, keeps every note
bash uninstall.sh --purge-vault   # also deletes the vault (asks first)
```

On Windows: `.\uninstall.ps1` and `.\uninstall.ps1 -PurgeVault`. Either way, removal is driven
by the install manifest, so it takes out exactly what was installed — including any starter-pack
skills — and nothing else.

### Alternative: Claude Code plugin

```
/plugin marketplace add SirCharan/second-brain
/plugin install second-brain
```

The plugin ships the machinery but not your vault, so create one and run the wizard:

```bash
export CLAUDE_MEMORY_DIR="$HOME/.claude/second-brain-vault"   # add to your shell profile
python3 ~/.claude/skills/second-brain/scripts/setup.py
```

Pick one method. Running the plugin and the install script together registers every hook
twice.

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
| `doctor [--fix]` | Self-test the install (plugin **or** install.sh); `--fix` repairs dirs and drift |
| `export [--format …]` | Flatten the whole vault into one portable context file for any model |
| `graph` | Emit a Mermaid `[[wikilink]]` link-graph of the vault |
| `stale [--days N]` | List active notes not confirmed in N+ days |
| `dump` | Write a resume digest to `_infra/_carryover.md` before a `/clear` |
| `embed-setup` | Enable optional semantic recall (one isolated venv; the core stays stdlib) |

## MCP server

An MCP server (`mcp/`) exposes the vault to **Claude Desktop** + **Cursor** (local stdio)
and **ChatGPT** (remote, read-only) — so recall and capture work outside Claude Code too.
The core is pure stdlib; only the ChatGPT endpoint adds one pip package, isolated in a venv.

Claude Desktop + Cursor:

```bash
python3 mcp/mcp-setup.py            # preview the config
python3 mcp/mcp-setup.py --write    # merge into both client configs (backs up first), then restart
```

ChatGPT (remote): **optional / experimental — currently paused.** A read-only remote endpoint
(official `mcp` SDK over Streamable-HTTP behind a cloudflared tunnel) exists but is not part of the
supported path right now. If you want to try it, the setup, tools, and hardening notes live in
[`mcp/README.md`](mcp/README.md).

Eight tools: `recall`, `pull`, `export`, `health`, `stale`, `graph` (read) and `capture`,
`learn` (write). Full detail in [`mcp/README.md`](mcp/README.md).

## Autonomous loop (advanced)

`second-brain-loop.sh` runs a long task across many **fresh** `claude -p` sessions — the "ralph"
dump-and-reset pattern. Each iteration starts with a near-empty context window, does one small
chunk, and persists where it stopped to `_infra/_carryover.md`; the next iteration reads that back.
Context never balloons, so a big task stays cheap without a human pressing `/clear`.

```bash
./second-brain-loop.sh "<task description>" [max_iters]   # max_iters defaults to 15
```

The loop stops early when a session writes `DONE` to `_infra/_loop-status.md`.

> ⚠ **Safety:** each iteration runs `claude -p … --dangerously-skip-permissions`, so sessions
> execute tools (including shell commands) with **no approval prompts**. Run it only on a task and
> working directory you trust, and start with a small `max_iters`.

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
20MB transcript), a `hook-errors.log` (under `~/.second-brain/`, or `$SECOND_BRAIN_STATE_DIR`) for
silent failures, `vault_ok()` no-op guards, and self-locating paths that work in both the plugin
and install.sh layouts.

The **core is pure stdlib** — capture, recall, curation, and every skill command run with zero pip
installs. Semantic recall (embedding-based note matching) is the one **opt-in** extra: run
`bash ~/.claude/skills/second-brain/scripts/embed-setup.sh` (or `/second-brain embed-setup`, or say yes during setup)
to build an isolated venv with `fastembed`. Without it, recall stays keyword-only and everything
degrades cleanly.

## Privacy

The vault is **your** data and is git-ignored by this repo. The machinery ships with zero personal
content. Captured turns are **scrubbed** for high-confidence secret shapes (API keys, tokens,
private keys, JWTs) before they touch disk. Set `SECOND_BRAIN_GIT_AUTOCOMMIT=1` to have each
session commit the vault, so "git-auditable, never lose a note" is literally true (init a git repo
in the vault first). Optionally mirror the vault into your Obsidian app folder by setting
`SECOND_BRAIN_OBSIDIAN_LINK` to that path (then `doctor --fix` maintains the symlink).

## License

Apache-2.0. See [LICENSE](LICENSE).
