# Changelog

Notable changes per release. The current version lives in [`VERSION`](VERSION).

## 0.6.0

### Guided onboarding

- The install one-liner moved to the landing domain: `curl -fsSL
  https://charandeepkapoor.com/second-brain/install.sh | bash` (a redirect to the same script on
  `main`; the raw URL still works). Windows: `irm
  https://charandeepkapoor.com/second-brain/install.ps1 | iex`.
- Both installers now ship `mcp/` into `~/.claude/mcp/`, recorded in the install manifest so
  uninstall removes it.
- The setup wizard gained three steps: connect Claude Desktop and Cursor (`mcp-setup.py
  --write`), an opt-in `[experimental]` ChatGPT/claude.ai remote (prints the tunnel command,
  never launches it), and a live capture test that pipes a synthetic session through the
  installed hooks and confirms today's `Daily/` note grew. The test is also standalone:
  `setup.py --verify-capture`.
- `/second-brain setup` is now a conversational in-Claude onboarding checklist wrapping the same
  engines.
- The "Second Brain Setup" macOS app is back (`installer/`, Tauri v2), rebuilt as a 7-step
  wizard over `install.sh` — prereqs with a double-install guard, install, track projects,
  connect apps, ChatGPT (copy-only), Obsidian, done. Ships unsigned as
  `Second-Brain-Setup.dmg` on GitHub Releases.
- The landing site gained `/get-started` — the same six steps as a copy-paste page.

### Windows

Windows was unsupported for four specific reasons, all now fixed. WSL2 always worked because
it is Linux; this is native PowerShell.

- Hooks are registered as `"<python>" "<hook>.py"` instead of `bash "<hook>.sh"`. The wrappers
  only ever pinned an interpreter and swallowed errors, and every hook `.py` already catches
  everything and exits 0 — which matters because a non-zero `UserPromptSubmit` hook blocks the
  prompt. The `.sh` files remain in the repo for running a hook by hand. Registration still
  prefers `/usr/bin/python3` over a pyenv shim, which is what the wrappers were protecting.
- `session-memory` had no Python twin. It does now (`hooks/session-memory.py`), so no hook
  needs a shell.
- `install.ps1` and `uninstall.ps1` are first-class equivalents of the shell scripts. Hook
  registration and the manifest moved into `scripts/register-hooks.py`, which both installers
  call, so the two cannot drift. The Windows interpreter probe tries `py -3` and `python`
  before `python3`, which is the Microsoft Store stub.
- `doctor.py` tries a symlink, falls back to a directory junction (no Developer Mode needed),
  and warns instead of failing if both are refused. It also honours `CLAUDE_CONFIG_DIR`, and no
  longer demands the `.sh` wrappers or an executable bit on Windows.
- The embed venv path (`Scripts\python.exe` vs `bin/python`) and the background-refresh launch
  flags (`start_new_session` is POSIX-only) are now per-platform.
- CI gained a `windows-latest` job that installs via `install.ps1`, asserts no registration
  shells out to bash, runs all nine hooks expecting exit 0, gates on `doctor --strict`, and
  uninstalls. Semantic recall stays macOS and Linux only: its setup script is bash.

### Starter pack (opt-in)

A fresh vault held six notes and no Obsidian configuration, so the graph looked dead on the
day you installed it. None of the working discipline the skills assume came with it either.

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
