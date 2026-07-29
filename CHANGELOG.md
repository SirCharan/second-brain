# Changelog

Notable changes per release. The current version lives in [`VERSION`](VERSION).

## 0.6.0

### Starter pack (opt-in)

A fresh vault held six notes and no Obsidian configuration, so the graph looked dead on the
day you installed it, and none of the working discipline the skill ecosystem assumes came
with it.

- `starter-pack/` ships 22 skills across three tiers (`core`, `writing`, `design`), a
  `_playbook/` folder of working rules, two note templates, and an `.obsidian/` config with
  per-folder graph colour groups. Core Obsidian features only — no community plugins.
- Offered as step 3 of the setup wizard, and available any time via
  `scripts/starter-pack.py --list` / `--tiers core,writing`. `install.sh --pack=…` answers the
  question up front for a non-interactive install.
- Nothing is overwritten. An existing skill directory, vault note or `.obsidian/` is left
  exactly as it is, which makes the script safe to re-run.
- Installed paths are appended to the install manifest, so `uninstall.sh` removes them with
  no change on its side.
- Third-party packs are referenced, never redistributed: `starter-pack/manifest.json` records
  each one's author, licence, install command and which bundled skill needs it. Every source
  was checked against a live upstream; one skill whose upstream could not be verified is
  listed as unbundled rather than shipped with a guessed URL.
- `build-system-index.py` now honours `CLAUDE_CONFIG_DIR`, so it indexes the right skills
  directory and writes real paths into the `_system/` notes.

## 0.5.0

### Install and setup

Neither documented install path worked before this release. `./install.sh` was
committed non-executable, and the curl one-liner resolved its own location from
`$0`, which is `bash` under a pipe.

- `install.sh` self-downloads and re-execs when run through `curl | bash`.
- Preflight checks Python 3.8+, a writable config dir, and a parseable
  `settings.json` **before** copying anything, so a missing dependency cannot leave
  a half-install.
- Refuses to run when `settings.json` is unparseable, instead of resetting it to `{}`
  and discarding the rest of your Claude Code config.
- Persists `CLAUDE_MEMORY_DIR` to your shell profile for a non-default vault.
- Writes `_infra/_install-manifest.json` recording every file it touched.
- No longer copies the test suite into your hooks directory.
- New flags: `--dry-run`, `--no-setup`.
- New `uninstall.sh`: removes the machinery, de-registers the hooks, and keeps your
  notes unless you pass `--purge-vault`.

### Memory engine

- **Project routing.** A capture resolves its project from the working directory
  instead of the raw directory name, so a subdirectory no longer files notes under
  the wrong project. An unknown repository registers itself on first capture.
- **Automatic hubs.** A new project folder gets a `_MOC-<project>.md` hub without
  waiting for an agent to write one; `regen-index` bootstraps any folder missing one.
- **One transcript parser.** Three near-identical loops became
  `_hooklib.scan_transcript()`, reading a 1 MB tail. The previous 256 KB window let a
  single large tool result push the exchange out of view, so the largest turns
  captured nothing.
- **Note accountability.** A session that changes code but records no note is logged
  and surfaced until a note exists. It never blocks.
- **Note size limits.** 4 KB target, 8 KB hard gate, reported by `health` and warned
  by `memory-lint` on write. Oversized notes blunt retrieval and cost tokens.
- **Shape checks.** `memory-lint` verifies frontmatter fields, a title, a status chip,
  and a `## Related` section, accepting both flat and nested frontmatter.
- **Compaction safety.** `context-monitor` writes the carry-over digest automatically
  at the fill threshold and re-arms as context grows, so `/clear` is always safe.
- **`verify-facts.py`** compares fact tokens between a backup and the current vault as
  whole sets, because facts legitimately move between notes when one is split.

### Fixes

- `health` counted every `[[_MOC-*]]` link as broken and grouped nested folders under
  the wrong parent.
- `doctor` inspected only the first 400 characters for frontmatter, failing notes with
  long descriptions, and disagreed with `health` about which files to audit.
- `regen-index` built the index from a hardcoded folder list, orphaning shards for new
  projects.
- Recall globs were single-level, so root-level and nested notes were invisible.
- `cosine()` imported numpy unconditionally, breaking the test suite on any machine
  without the optional embedding venv. CI had been red since 0.4.1.
- Combined `pytest` runs were order-dependent because the vault path froze at import.

### Removed

- The Tauri `.dmg` installer. It was never smoke-tested, nothing referenced it, and it
  carried 3.7 GB of build output. `install.sh` is the supported path.
- Two unused landing-page apps. Their deployments stay up; only the sources are gone.

### Changed

- One version number, read from `VERSION`. It had drifted to three different values
  across eight files.
- `interview-nudge` recommends planning and multi-agent orchestration for large tasks.
- Test fixtures no longer contain the author's real project names.
