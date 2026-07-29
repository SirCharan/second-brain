---
name: anti-slop-design-audit
description: Runnable graded anti-slop audit for web UI — grades a dashboard, landing page, marketing page, or component against severity-tiered AI-slop tells and either reports (detect mode) or fixes (rewrite mode), looping until clean. Use before shipping any UI, when a design "looks templated / looks AI-generated", to grade a design, or to apply dashboard data-density rules. Trigger on "design audit", "slop check", "review this UI", "does this look AI", "grade this design", "make this less templated", "dashboard density", "before shipping this page". This is the graded PASS; it defers the full tell-catalogue to anti-slop-design-law and token/palette mechanics to design-system / dataviz-design.
---

# Anti-slop design audit

A runnable, graded pass over a UI. Turns the `anti-slop-design-law` catalogue into a scored review with a fix loop. Use it as the pre-ship gate for dashboards, explainer apps, landing and marketing pages.

## What this skill is (and is not)
- **Is:** a severity-tiered audit protocol + a dashboard data-density reference + a detect/rewrite loop, grading the **source code**.
- **Is not:** the tell catalogue (load `anti-slop-design-law` for the full list + what premium looks like) or the token/font/palette mechanics (`design-system`; `dataviz-design` for charts/dark surfaces). This skill *scores and fixes*; those *supply the rules*.
- **Not the whole gate:** this grades code. A visual pass grades the **rendered pixels** (browser screenshot at desktop+mobile). Run this while building, then a fresh-context visual review before shipping — the two halves catch different defects.

## Two modes
- **detect** — grade only. Output the scorecard + a ranked findings list. No edits. Use for "does this look AI / review this UI".
- **rewrite** — fix. Apply fixes highest-severity first, then re-audit. Use for "make this less templated / fix the slop".

## The loop
`scope → audit → calibrate → rewrite → re-audit` — repeat until no P0 and no P1 remain.
1. **scope** — name the artifact (dashboard / landing / marketing / component) and its ONE job.
2. **audit** — walk the P0/P1/P2 rubric (`references/audit-protocol.md`); for dashboards also walk `references/dashboard-density.md`. Record file:line for each finding.
3. **calibrate** — drop false positives (a deliberate brand choice is not a tell). Keep only real defects.
4. **rewrite** (rewrite mode only) — fix P0 first, then P1. Each fix names the tell it removes.
5. **re-audit** — re-run. Exit when P0 = 0 and P1 = 0. P2 are optional polish.

## Severity tiers (summary — full rubric in references)
- **P0 — instant "AI-generated" tells.** Ship-blockers. e.g. purple→blue gradient hero, three-icon-card feature row, untouched shadcn defaults, Inter/system-ui as the brand face, blurred mesh-blob background, everything `rounded-2xl shadow-lg`.
- **P1 — no craft.** Weak/flat hierarchy, no signature element, faked/boxy shadows, uniform evenly-spaced grid, centered-everything, generic rainbow chart palette.
- **P2 — polish.** Micro-spacing, optical alignment, motion timing, empty/loading/error states.

## Output format
**detect:**
```
ARTIFACT: <type> — job: <one line>
SCORE: P0 <n> · P1 <n> · P2 <n>   → <SHIP / BLOCK>
P0:
  - <tell> — <file:line> — fix: <one line>
P1: …
P2: …
```
**rewrite:** apply fixes, then print the re-audit scorecard and the diff summary (tells removed).

## Dashboards — always also run the density pass
Generic dashboards fail on data density, not color. Load `references/dashboard-density.md`: one hero metric, deliberate row heights (48–52px comfortable / 36–40px dense), kill the uniform card grid, semantic (not rainbow) series palette, sparklines/small-multiples over toy charts, progressive disclosure.

## How it fits the design workflow
`design-router` picks the primary (a fixed brand system → that brand's own tokens; else `ui-ux-pro-max`) → build with `design-system` + `layout-interaction-design` + `motion-3d`, holding `anti-slop-design-law` → **run THIS skill as the graded pre-ship gate.** Sibling of `writing-eval` — copy for the same page gets the writing audit, design gets this one.
