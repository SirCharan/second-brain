---
name: design-router
description: "The TOP-LEVEL design routing rule — decides WHICH design skill to start from before any web/UI work. Load this FIRST (before design-system) whenever building, scaffolding, restyling, or reviewing any web UI. The rule: a project with its own fixed brand system → that brand's tokens win, no generator; EVERYTHING ELSE → ui-ux-pro-max is the primary START-HERE (run its search.py --design-system first, then build). The per-type skills (dataviz-design, editorial-report-design, marketing-microsite-design, tool-calculator-design, docs-design) are optional SUPPLEMENTS for domain depth, not the default. layout-interaction-design is the behavioral companion in all cases. Requires the ui-ux-pro-max pack (see the starter-pack manifest) for the non-branded branch. Trigger on: build a UI, new landing page / dashboard / report / calculator / docs site, design system, make this look better, this looks templated, pick a palette/font/style, restyle, upgrade a ChatGPT/Grok project, or any front-end/design work."
---

# design-router — pick the right design skill first

Before ANY web/UI design work, decide the starting skill here, then hand off.

## ALWAYS load first: the anti-slop design law

**On every design project, load `anti-slop-design-law` before anything else** (it applies to both
branches below). It is the pols.dev anti-slop law — the catalogue of AI-slop tells plus what premium
actually looks like. Read its `references/slop-law.md` fully at spec time, and run it as the final
point-by-point review pass before shipping. It is a cross-cutting check, not a competing router.

## The decision (one question: does this surface already have a brand system?)

```
Does the project have a fixed brand system — a design-token set, a Figma library,
or brand guidelines you are required to match?
│
├─ YES → those tokens ALWAYS win. Load `design-system` for the mechanics (token layer,
│        a11y, motion) and apply the brand's palette/type on top.
│        Do NOT run ui-ux-pro-max's design-system generator — it would invent a
│        palette you are not allowed to use.
│
└─ NO  → `ui-ux-pro-max` is the PRIMARY / START-HERE skill.
         1. Run its `search.py --design-system` FIRST to get style + palette + font pairing
            + product archetype + anti-patterns (see the `pro-max-search` skill for the exact
            command with the house-stack defaults).
         2. THEN implement against that output.
         3. Pull in a supplement below ONLY if that generic output needs domain depth.
```

## Supplements (use when the generic output isn't enough)

| Project type | Supplement skill | When to add it |
|---|---|---|
| Dashboards / analytics / trading UIs | `dataviz-design` | Cross-filtering model, CVD-safe chart palettes, dark-surface elevation, PnL/heatmap color |
| Research reports / almanacs / explainers / essays | `editorial-report-design` | Reading measure, serif body scale, drop caps, prose-embedded charts, scroll-spy TOC |
| Landing / GTM / launch / pitch sites | `marketing-microsite-design` | Hero structure, section order, CTA hierarchy, pricing tables, conversion patterns |
| Calculators / single-purpose tools | `tool-calculator-design` | Input-forward layout, live recompute, result-as-hero, permalink results |
| Docs sites (Fumadocs/Nextra) | `docs-design` | Extend Fumadocs defaults, code-block polish, nav density |

`layout-interaction-design` = behavioral companion (spacing/8pt grid, button placement & action
hierarchy, nav & Next.js App Router routing, loading/empty/error states, focus & UX heuristics). Load
it alongside the above for any non-trivial interactive or multi-screen build — i.e. nearly always.

## House constants (apply to every branch)

- Stack: **Next.js + Tailwind v4 + shadcn/ui (Base UI primitives) + Lucide + Recharts.**
- **Never ship `system-ui` as the brand font.** Pick a real pairing (ui-ux-pro-max's `--domain typography` / `google-fonts` gives them).
- **Never hardcode hex in components** — use the semantic token layer.
- Verify contrast + CVD before shipping; WCAG 2.2 AA baseline.
- For UI/web changes, open the deployed URL and confirm the change rendered. Tests prove
  correctness, not appearance.

## Why this exists

A bespoke design-skill suite and the community `ui-ux-pro-max` plugin (a 161-palette / 84-style /
73-font-pairing BM25 design-intelligence engine) compete without a router. Rule: **branded work
follows the brand; all other UI defaults to ui-ux-pro-max as the idea/spec engine, and the bespoke
skills fill the gaps it leaves.**

Related: `anti-slop-design-law` (mandatory anti-slop check, load first), `pro-max-search` (how to
invoke the engine), `design-system` (shared foundations/mechanics).
