---
name: routing-rules
title: "Routing rules — which skill to load first"
description: "Prose starts at writing-router, UI starts at design-router and anti-slop-design-law, and both end at a graded pre-ship gate."
tags: [meta, project/playbook, type/reference]
asserted: 2026-07-29
last_confirmed: 2026-07-29
source: user
confidence: high
status: active
supersedes: []
metadata:
  type: reference
---

# Routing rules — which skill to load first

🟢 **active**

The starter pack ships overlapping skills on purpose: a router picks between them so they do not
compete. Load the router first, then only what it names.

> [!tip] Prose → `writing-router`
> It collapses five overlapping writing skills onto two axes (clarity, anti-slop), adds
> `writing-composition` for document shape, and ends at `writing-eval` as the graded gate. It also
> resolves the sentence-length rule the individual skills disagree on.

> [!tip] Web UI → `design-router` plus `anti-slop-design-law`
> The router asks one question: does this project already have a brand system? If yes, its tokens
> win. If no, `ui-ux-pro-max` generates the spec and you build against it. The anti-slop law loads on
> every design project regardless, and `anti-slop-design-audit` is the graded gate before shipping.

> [!tip] A build with three or more phases → `gtan-workflow`
> See [[phase-discipline]] for what it enforces.

> [!info] Anything non-trivial starts with an interview
> `discovery` runs a spec interview before any code. It costs one exchange and saves the rebuild that
> follows a wrong assumption.

## The shape both routers share

Route → build → **grade before shipping**. The gate matters more than the routing: `writing-eval` and
`anti-slop-design-audit` both score the finished artifact against a rubric, and both are worth running
in a fresh context so the author is not marking its own work.

## Packs you still have to fetch

Several of these skills route into third-party packs that are not bundled — `ui-ux-pro-max`,
`stop-slop`, `superpowers`, `gstack` and the rest. `starter-pack/manifest.json` in the repo lists
each one with its author, licence and install command.

## Related
- [[_MOC-playbook]]
- [[phase-discipline]]
- [[session-habits]]
