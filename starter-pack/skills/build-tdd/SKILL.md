---
name: build-tdd
description: >
  Runnable wrapper for building a feature test-first with a real completion gate. Chains
  superpowers' test-driven-development → the implementation → verification-before-completion,
  under ponytail's minimal-code discipline (YAGNI, stdlib-first, no unrequested abstractions).
  Requires the superpowers and ponytail packs — see starter-pack/manifest.json.
  Use when you type /build-tdd, or are asked to "build this properly / test-first / with tests", or
  when a feature is non-trivial enough that shipping it untested would be reckless. Skip for
  throwaway scripts and one-line fixes.
---

# build-tdd — feature, test-first, with a completion gate

A thin routine that composes three installed skills so a feature ships correct and lean, not just
"done". Load and follow the named skills in order — don't reimplement them here.

## Steps
1. **Scope tight (ponytail).** Load the `ponytail` skill's mindset first: the simplest thing that
   works, stdlib/existing-utils before new deps, no abstraction you didn't ask for. State the
   smallest surface that satisfies the ask before writing anything.
2. **Red → Green → Refactor (superpowers `test-driven-development`).** Load and follow it: write a
   failing test that pins the behaviour, make it pass with the minimum code, then refactor. For
   your repos use the project runner — Python: `uv run pytest`; TS/JS: `npm test`.
3. **Implement** the feature against the tests, staying inside the Part-1 scope.
4. **Completion gate (superpowers `verification-before-completion`).** Load and follow it before
   claiming done: run the full pre-commit gate (`uv run ruff check && uv run mypy && uv run pytest`
   for Python; `npm run lint && npm run typecheck && npm test` for TS), and for any UI/runtime
   surface actually exercise it (the `verify` / `run` skill), not just green tests.
5. **Ship** per your ship rule (commit + push immediately once the gate is green; use `/ship`).

## Notes
- This is the disciplined path; for a trivial change, just make it — don't ceremony a one-liner.
- Pairs with `gtan-workflow` (which owns the *phase* discipline); build-tdd owns a *single feature*.
