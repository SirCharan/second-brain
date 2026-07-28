## What this changes

## Why

## How it was verified
Paste the actual output.

```
python3 -m pytest hooks -q
```

- [ ] Tests pass on macOS and Linux (CI)
- [ ] No new runtime dependency in the core (stdlib only)
- [ ] If the installer changed: `install-smoke` is green on both platforms
- [ ] No hardcoded vault path or interpreter
