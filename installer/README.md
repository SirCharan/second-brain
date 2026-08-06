# Second Brain Setup (macOS)

Friendly Tauri v2 installer for [second-brain](https://github.com/SirCharan/second-brain).
Wraps `install.sh` and the setup scripts so non-technical users can wire Claude Code +
an Obsidian vault without a terminal.

## The 7 steps

1. **Check your machine** — Claude Code, git, python3 (brew is optional).
   Also probes for a plugin-mode install (`/plugin install second-brain`);
   if found, step 2 is blocked — running both would double-fire every hook.
2. **Install** — clones/pulls `~/second-brain` and runs `install.sh --no-setup`,
   streaming the log into the UI. Project setup is deferred to step 3.
3. **Track your projects** — runs `setup.py --non-interactive` (defaults), or
   "Finish in Terminal" opens Terminal.app with the interactive wizard (needs a TTY).
4. **Connect apps** *(optional)* — wires the MCP server into Claude Desktop + Cursor
   via `python3 mcp/mcp-setup.py --write`.
5. **ChatGPT remote** *(experimental)* — nothing runs; copyable commands only
   (`bash mcp/mcp-http-setup.sh`, `bash mcp/run-chatgpt.sh`). Read-only endpoint;
   see `mcp/README.md`.
6. **Obsidian** — installs via Homebrew cask if missing, and opens the vault
   with an `obsidian://open?path=…` deep link (Finder fallback).
7. **Done** — restart Claude Code so the hooks load, then
   [get started](https://charandeepkapoor.com/second-brain/get-started).

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
npm ci          # or npm install if the lockfile is stale
npx tauri build
```

Artifacts:

- `src-tauri/target/release/bundle/macos/Second Brain Setup.app`
- `src-tauri/target/release/bundle/dmg/Second Brain Setup_<version>_aarch64.dmg`

The release flow copies the DMG to `installer/Second-Brain-Setup.dmg` (gitignored).

## Gatekeeper (unsigned builds)

This app is not Apple-notarized. First open on a fresh Mac:

1. Right-click the app → **Open** → **Open**
2. Or clear quarantine after downloading the `.dmg`:

```bash
xattr -dr com.apple.quarantine "/Applications/Second Brain Setup.app"
```

## Brand

Matches the landing tokens in `site/app/globals.css` (warm near-black, amber accent,
Gambarino display). Do not edit `site/` from this package.
