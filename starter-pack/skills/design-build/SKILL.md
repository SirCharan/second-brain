---
name: design-build
description: >
  Runnable wrapper for building a web UI the right way end-to-end — the design pipeline as one
  routine. Chains design-router → the picked primary (the project's own brand tokens when it has
  them, else ui-ux-pro-max --design-system) → layout-interaction-design + motion-3d → live-URL verification,
  with the taste levers in step 2 applied. Use when you type /design-build, or are asked
  to build/restyle/upgrade any page, dashboard, landing, report, or calculator, or to
  "make this look better / less templated". Requires the ui-ux-pro-max pack — see
  starter-pack/manifest.json. See `design-router` for the full routing map.
---

# design-build — the web-UI pipeline, end-to-end

Composes the design skills in the right order so the result is intentional and on-brand, not
default-shadcn. Load and follow each named skill — this file is the running order, not a substitute.

## Steps
0. **Load the anti-slop law (anti-slop-design-law).** FIRST, on every build. Read its
   `references/slop-law.md` fully; state you've read it and will re-check point-by-point before
   shipping. It's the anti-slop gate over this whole pipeline (see step 6).
1. **Route (design-router).** One question: does the project have a fixed brand system (a token
   set, a Figma library, brand guidelines you must match)? → those tokens always win, plus
   `design-system` for mechanics. Everything else → `ui-ux-pro-max` is primary: run its `search.py --design-system` FIRST (see `pro-max-search`
   for the exact command) to get palette/fonts/style/archetype, then build against it.
2. **Apply taste.** Before writing components, apply these taste levers: a real font pair (never `system-ui`), a semantic token layer (no
   hardcoded hex), deliberate spacing rhythm, one committed art direction, and the anti-patterns to
   avoid (generic purple gradients, default shadcn, centred-everything). Name the aesthetic explicitly.
3. **Pull domain depth (supplement skill)** for the page type: dashboard/trading → `dataviz-design`;
   landing/GTM → `marketing-microsite-design`; report/almanac → `editorial-report-design`;
   calculator/tool → `tool-calculator-design`; docs → `docs-design`.
4. **Behaviour + motion.** Load `layout-interaction-design` (spacing, action hierarchy, nav/routing,
   loading/empty/error states) and `motion-3d` (Motion default; GSAP for scroll; R3F opt-in only;
   honour `prefers-reduced-motion`).
5. **Verify live.** Build, deploy, and open the actual URL to confirm it rendered. Tests ≠ UX.
6. **Anti-slop final pass (anti-slop-design-law).** Walk `references/slop-law.md` point by point
   against the shipped UI: kill every slop tell, fix every UI bug, click every interactive control,
   zoom-verify centering/cut-edges/contrast/alignment. Confirm there's a real signature, not just a
   clean-but-dead page.

## Notes
- House stack: Next.js + Tailwind v4 + shadcn/ui (Base UI) + Lucide + Recharts.
- Do NOT run the pro-max generator when the project has a fixed brand system — its palette is already decided.
- Full routing detail: `design-router`.
