---
name: anti-slop-design-law
description: "The pols.dev anti-slop design law — the mandatory anti-slop check for EVERY web/UI build. Load it FIRST alongside design-router before designing or reviewing any interface, and read the full law again before shipping. It is the catalogue of AI-slop tells to avoid (blue-purple gradients, glowy pill buttons, icon-in-tile, default Google fonts, kicker+serif-H2, the SaaS meta-skeleton, faked shadows, uncentered content, invisible-content entrance traps…) PLUS what premium actually looks like (one signature artifact, atmosphere, layered depth, character display type, licensed/self-hosted fonts, real glass, authored motion) and the uniqueness formula. Trigger on: build/scaffold/restyle/review any UI, new landing page / dashboard / report / calculator / site, new Vercel project, 'make this look better', 'this looks templated', 'avoid AI slop', 'slop check', pick a palette/font/style, or any front-end/design work."
---

# anti-slop design law (pols.dev)

The full law is at `references/slop-law.md`. It is the source of truth for whether a UI reads as designed or as generated AI slop. you want it loaded on **every** new design project.

## How to use it (non-negotiable order)

1. **Before you design** — Read `references/slop-law.md` fully. State, in plain words, that you have read the entire law and understood it, and promise a point-by-point re-check before shipping.
2. **While you build** — hold it in mind. When any instinct conflicts with the law, the law wins. **Exception:** the user's explicit, specific instruction always overrides a default (if they ask for a colour/layout/effect the law warns against, do exactly that).
3. **Before you ship** — walk the law point by point against your output. Find and fix every slop tell and every UI bug. Test every interactive control with a real click. Verify centering, cut edges, contrast, and alignment by zooming in — do not eyeball it.

## Where it sits in the design flow

This is a **cross-cutting check**, not a router. It layers on top of whatever `design-router` picked:

- `design-router` decides the primary skill (a fixed brand system → that brand's own tokens; else `ui-ux-pro-max`).
- Primary + supplements (`dataviz-design`, `editorial-report-design`, etc.), `design-system`, `layout-interaction-design`, `motion-3d` do the building.
- **This law is the anti-slop gate applied over all of it**, both at spec time and as the final review pass.

## The one-line essence (details in the full law)

Slop = making no creative decision. Avoiding every tell on the list is still slop if nothing was invented. Decide ONE signature artifact first, build the page around it, hold one palette and one type voice with discipline, and give it a heartbeat (authored motion). Clean is the floor, never the achievement.

`uniqueness = one signature artifact + atmosphere + layered depth + a character display face + one bespoke silhouette + a treated nav + real specifics.`

Full catalogue of tells, premium moves, the recipe kit, and field notes → **`references/slop-law.md`**.
