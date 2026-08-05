---
name: docs-design
description: >
  Design guidance for documentation sites on Next.js + Tailwind + Vercel, especially Fumadocs (also
  Nextra/Starlight). Lightweight: it tells you what Fumadocs ships by default
  (sidebar, TOC, search, Shiki code blocks, theme switch) so you EXTEND rather than rebuild, plus what
  to customize (theme tokens, code-block polish, nav density, fonts) and the Swiss/Minimal docs look.
  Load alongside `design-system` (tokens, a11y). Trigger on: "docs site", "documentation",
  "Fumadocs", "Nextra", "API docs", "developer docs", "sidebar/TOC", or styling a docs site.
---

# Docs-Site Design (Fumadocs-first)

Pair with `design-system` and **`layout-interaction-design`** (sidebar/tabs/breadcrumbs nav §3, active-link
+ persistent route-group layout for Next.js). Docs live or die on **scan-ability**: strict type scale,
generous whitespace, restrained color. Don't rebuild what the framework gives you. ✅ verified · ◐ situational.

## Use Fumadocs, customize — don't rebuild ✅
Fumadocs (Next.js-native, the right pick for the house stack) ships out of the box:
- Left **sidebar nav tree** (collapsible desktop; mobile navbar), on-page **TOC** right rail,
  built-in **search** (Orama/flexsearch core), **theme switcher**, breadcrumbs, GitHub-link slot.
- **Code blocks** via Shiki (v16, Oct 2025 defaults to the JS regex engine — works on Cloudflare Workers);
  `DynamicCodeBlock` for runtime highlighting.
- Layout **tabs/dropdowns** for product sections (from `meta.json` root folders).

**Customize via props/slots, not forks:** `defaultOpenLevel` (sidebar expansion), collapsibility,
sidebar footer/banner, inject custom JSX above the TOC or in the sidebar via `components`/`slots`, `nav`,
`themeSwitch`, prefetching, `tabs={false}`.

## Nav / density ✅
Group by section/folder; **collapse deep trees by default** (open level 1). Keep the TOC for in-page jumps
on long pages. Aim for ≤2 levels visible at rest; let search carry deep lookups.

## Search ✅
Wire the built-in search (good to large scale); only move to Algolia at large scale.

## Code blocks ✅
Shiki by default — add a **copy button**, **filename/title**, **line highlighting**, and **language tabs**
for multi-language. ◐ Twoslash for typed-TS hovers if relevant. Match the code theme to your token palette,
not a clashing default.

## Versioning ◐
Not first-class in Fumadocs — handle via separate routes/branches or per-version content directories; don't
expect a built-in switcher.

## Look & type ✅◐
- **Style:** Swiss / International Typographic + Minimalism; Flat-Material components. Nothing decorative —
  color carries meaning (callout intents: note/warn/danger), not flourish.
- **Fonts:** readable sans + good mono — **Inter + JetBrains Mono** · **Geist + Geist Mono** (Vercel-native,
  matches Next.js docs aesthetic). Body ~16px, measure ~70–75ch for docs prose (slightly wider than essays).
- Theme tokens from `design-system` §3; ensure ≥4.5:1 in both light/dark (Fumadocs defaults are usually fine
  but verify any custom accent).

## Pitfalls
Rebuilding sidebar/TOC/search Fumadocs already provides · clashing default code theme · everything expanded
in the sidebar · prose measure too wide · custom accent that fails contrast in one theme.

## Frameworks ◐
Fumadocs (default for this stack), Nextra v4, Starlight (Astro) are the 2026 contenders — stay on Fumadocs
for Next.js + Tailwind + Vercel.

## Sources
fumadocs.dev (docs layout, codeblock, v16 blog) · pkgpulse.com (Fumadocs vs Nextra vs Starlight 2026) ·
design-system skill (tokens/a11y/type).
