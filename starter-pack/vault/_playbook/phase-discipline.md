---
name: phase-discipline
title: "Phase discipline — how a multi-phase build runs"
description: "One master plan plus one plan per phase in the vault, tests every phase, one phase at a time, and a written reflection before replanning."
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

# Phase discipline — how a multi-phase build runs

🟢 **active**

The rules the `gtan-workflow` skill enforces for anything bigger than a single feature. The loop per
phase is **Think → Plan → Build → Review → Test → Ship → Reflect**, and Review, Test and Reflect are
where the quality and the learning live.

> [!tip] Plans live in this vault, not in the chat
> `<vault>/<project>/master-plan.md`, one `phase-N-*.md` per phase, and one `reflections.md`. Plans
> are living documents: update them as you work. A plan in a chat log disappears at the next `/clear`.

> [!warning] One phase at a time
> Build one phase, checkpoint, reflect, then expand the next phase's plan. Front-loading three phases
> in one stretch is how errors hide behind each other and rework piles up.

> [!warning] Tests every phase, no exceptions
> No phase closes without its tests written and green. If the repo has no test harness, building one
> is the first phase's deliverable.

> [!danger] A passing build is not a passing runtime
> `npm run build` proves the bundle compiles, not that the page renders. Spike a risky new dependency
> in a ten-line smoke render before you pin its version, and open the real page before you call it done.

## Reflect, then replan

After each phase, append to `reflections.md`: what worked, what broke, what carries forward. Then
update the next phase's plan with those learnings *before* starting it. Reflection written after the
next phase has begun changes nothing.

## Related
- [[_MOC-playbook]]
- [[session-habits]]
- [[routing-rules]]
