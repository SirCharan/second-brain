# Second Brain Setup (macOS)

Friendly Tauri installer for [second-brain](https://github.com/SirCharan/second-brain).
Wraps `install.sh` so non-technical users can wire Claude Code + an Obsidian vault without a terminal.

## What it does

1. Checks for Claude Code, git, and node
2. Clones/pulls `~/second-brain` and runs `install.sh` (streams log output)
3. Installs Obsidian via Homebrew cask if missing
4. Opens the vault in Obsidian (`obsidian://open?path=…`) or Finder
5. **Optional:** wires the MCP server into Claude Desktop + Cursor by running
   `python3 mcp/mcp-setup.py --write` (`setup_mcp` command → the "Connect other apps" step)

Step 5 — the MCP "Connect other apps" wiring — ships in 0.4.0. ChatGPT is a separate remote
endpoint (optional/experimental, currently paused) — set up from a terminal, not this
installer; see `mcp/README.md`.

> Verifying the UI end-to-end needs the Tauri toolchain (`npm run tauri dev`, Rust) —
> not built in this repo change. The Rust command, TS handler, and HTML step are wired
> but should be smoke-tested with a real build.

## Develop

```bash
cd installer
npm install
npm run tauri dev
```

Requires Rust (`cargo`), Node, and Xcode CLT.

## Build

```bash
cd installer
npm run tauri build
```

Artifacts:

- `src-tauri/target/release/bundle/macos/Second Brain Setup.app`
- `src-tauri/target/release/bundle/dmg/Second Brain Setup_0.1.0_*.dmg`

## Gatekeeper (unsigned builds)

This app is not Apple-notarized. First open on a fresh Mac:

1. Right-click the app → **Open** → **Open**
2. Or clear quarantine after downloading the `.dmg`:

```bash
xattr -dr com.apple.quarantine "/Applications/Second Brain Setup.app"
```

## Brand

Matches the landing tokens in `site/app/globals.css` (warm near-black, amber accent, Gambarino display). Do not edit `site/` from this package.
