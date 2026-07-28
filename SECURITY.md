# Security

## Reporting a vulnerability

Open a [private security advisory](https://github.com/SirCharan/second-brain/security/advisories/new)
rather than a public issue. Include what an attacker gains and the smallest steps that show
it. Expect a first reply within a week.

## What this software does on your machine

Understand this before you install, because the install pipes a script from the internet
into `bash`. You can read it first: clone the repo and run `./install.sh` locally, or
`bash install.sh --dry-run` to see the plan without changes.

`install.sh` writes to five paths and records all of them in
`$CLAUDE_MEMORY_DIR/_infra/_install-manifest.json`:

- `~/.claude/hooks/` — the hook scripts
- `~/.claude/skills/second-brain/` — the skill and its scripts
- `~/.claude/workflows/vault-enrich.js`
- your vault (default `~/.claude/second-brain-vault`)
- `~/.claude/settings.json` — hook registration, backed up to `settings.json.bak` first

It merges into existing settings and never replaces them, refuses to run if that file is
unparseable, and `uninstall.sh` reverses it while keeping your notes.

Once installed, the hooks run on your session events and **read your Claude Code
transcripts**. That is the product: capturing work into notes requires reading the work.

## What leaves your machine

Nothing, by default. There is no server, no telemetry, no account, and no network call in
the core. Your vault is local Markdown.

Two opt-in features do use the network, and only when you enable them:

- **Semantic recall** downloads an embedding model once (`embed-setup.sh`), then runs it
  locally.
- **The HTTP MCP server** exposes read-only vault tools over a port you start yourself. Do
  not put it on a public address. The bundled bearer-token server is for local testing;
  treat any remote exposure as unreviewed.

## Secrets in your notes

Captures are scrubbed for high-confidence secret shapes — API keys, tokens, private key
blocks, JWTs — before anything is written (`scrub_secrets` in `hooks/_hooklib.py`).

> **This is a regex, not a guarantee.** It catches common formats. It will miss a password
> in prose, an unusual key format, or a credential you paste as ordinary text.

So: treat the vault as sensitive. It is a transcript of your work. If you sync it, sync it
somewhere private. If you commit it to git, keep that repository private — and remember
`SECOND_BRAIN_GIT_AUTOCOMMIT=1` commits the vault for you.

## Reviewing what you already installed

```bash
cat "$CLAUDE_MEMORY_DIR/_infra/_install-manifest.json"   # every file this touched
python3 ~/.claude/skills/second-brain/scripts/doctor.py  # what is active now
```
