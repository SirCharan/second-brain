# Second Brain Setup (macOS)

Friendly Tauri installer for [second-brain](https://github.com/SirCharan/second-brain).
Wraps `install.sh` so non-technical users can wire Claude Code + an Obsidian vault without a terminal.

## What it does (v1)

1. Checks for Claude Code, git, and node
2. Clones/pulls `~/second-brain` and runs `install.sh` (streams log output)
3. Installs Obsidian via Homebrew cask if missing
4. Opens the vault in Obsidian (`obsidian://open?path=…`) or Finder

MCP-server setup is deferred to v2.

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
