# Contributing

Thanks for looking. This is a small, deliberately boring codebase — most changes are a few
lines in one hook.

## The one hard rule

**The core is stdlib-only.** No `pip install` for anything a user needs to run the hooks,
the skill scripts, or the MCP stdio server. CI compiles and tests everything without a
package index, and a pull request that adds a runtime dependency to the core will not pass.

Two exceptions already exist and are opt-in: semantic recall (`embed-setup.sh` builds its
own venv) and the HTTP MCP server (`server_http_sdk.py`, its own venv). If you need a
library, put it behind a venv like those.

## Setup

```bash
git clone https://github.com/SirCharan/second-brain && cd second-brain
python3 -m pytest hooks -q          # unit tests
python3 mcp/test_mcp.py             # MCP round-trip
bash install.sh --dry-run           # see what an install would do
```

To try your changes without touching your real setup, install into a throwaway home:

```bash
FAKE=$(mktemp -d); HOME="$FAKE" bash install.sh --no-setup
HOME="$FAKE" CLAUDE_MEMORY_DIR="$FAKE/.claude/second-brain-vault" \
  python3 "$FAKE/.claude/skills/second-brain/scripts/doctor.py"
```

## Hooks

A hook runs on every session or prompt, so it has to be dull and fast:

- **Never raise.** Wrap the body and log through `_hooklib.log_err`. A crashing hook
  degrades someone's editor.
- **Never block.** Warn and return. The only exceptions are deliberate permission gates.
- **Stay inside the timeout** declared in `install.sh`. Slow work goes in a detached
  subprocess (`context-monitor.py` shows the pattern).
- **Read the transcript through `_hooklib.scan_transcript`.** Do not write a fourth
  parser; three duplicates already caused one silent data-loss bug.
- **Respect `CLAUDE_MEMORY_DIR`.** Never hardcode a vault path, and never assume
  `/usr/bin/python3` exists.

## Tests

Add one for any non-trivial logic. Tests are stdlib `assert`, runnable two ways:

```bash
python3 hooks/test_enforcement.py   # standalone
python3 -m pytest hooks -q          # all together
```

Vault-dependent tests must call `_bind()` first. `MEM` and `CONFIG` freeze at import, so
without it a combined run binds to whichever module imported last. Build fixtures at import
too, not from a `setup()` under `__main__` — pytest calls the test functions directly and
would otherwise run them against an empty vault.

## Changing how recall ranks

Retrieval has a measurement now, so guesses are no longer necessary:

```bash
python3 tests/eval/build_set.py -o ~/.second-brain/eval/queries.jsonl
python3 tests/eval/run_eval.py  ~/.second-brain/eval/queries.jsonl --save before.json
# make your change
python3 tests/eval/run_eval.py  ~/.second-brain/eval/queries.jsonl --compare before.json --gate
```

Quote the hit@4 delta in the pull request. See `tests/eval/README.md` for the baseline and
for what has already been measured and ruled out.

## Pull requests

Keep the diff small and say what breaks if you are wrong. Include:

- what changed and why, in plain sentences
- how you verified it (paste the actual command output)
- whether it changes what `install.sh` touches

CI must be green on macOS and Linux. The `install-smoke` job runs a real install, gates on
`doctor --strict`, and checks that uninstall keeps notes — if you change the installer,
watch that job.

## Reporting a bug

Run `python3 ~/.claude/skills/second-brain/scripts/doctor.py` and paste the output. It
reports your install mode, hook registration, and platform, which is most of the diagnosis.
Do not paste vault contents; they are your notes.
