---
name: design-system
description: >
  Shared design FOUNDATIONS for web UI work — the token layer, house stack (Next.js + Tailwind
  v4 + shadcn/ui + Lucide, Recharts for data), system-ui kill, WCAG 2.2 a11y baseline, component
  baseline, motion + responsive defaults, named-style picker, and "premium-feel" checklist distilled
  from Stripe/Vercel/Linear/Robinhood/Apple/Mercury. NOTE: routing lives in `design-router` (loaded
  FIRST) — branded work follows the brand's own tokens; all other UI starts from `ui-ux-pro-max`. This
  skill is the mechanics layer applied ON TOP of whichever primary skill the router picked; it is not
  the entry point. Load it for: token layer, fonts, a11y, motion mechanics, component baseline, or the
  premium-feel review pass.
---

# Design System — shared foundations (mechanics layer)

Researched 2026 baseline for every web UI you ship. **Confidence per claim:** ✅ = verified from a
primary/teardown source; ◐ = well-sourced design judgment (strong default, not dogma).

> **Entry point is `design-router`, not this skill.** The router decides the PRIMARY skill (a fixed brand
> system → that brand's own tokens; everything else → `ui-ux-pro-max`, run its `search.py --design-system` first). THIS
> skill supplies the shared foundations applied on top: (1) load **`layout-interaction-design`** for any
> non-trivial interactive/multi-screen build (spacing, button placement, navigation, states); (2) apply
> the tokens/type/a11y/motion/components + premium-feel checklist from here. Division of labor: the
> primary skill owns the look/spec; `layout-interaction-design` owns spacing mechanics, action hierarchy,
> routing & states; THIS skill owns tokens, type, a11y, motion, components.

---

## 1. Where this fits (routing is in `design-router`)

`design-router` picks the primary skill; the per-type skills below are **optional supplements** you pull
in for domain depth once the primary spec exists (unbranded primary = `ui-ux-pro-max`).

| Building… | Primary (via `design-router`) | Optional supplement for depth |
|---|---|---|
| Data/analytics **dashboard**, trading/signal UI, charts | `ui-ux-pro-max` | `dataviz-design` (cross-filter model, CVD chart palettes, PnL color) |
| **Marketing / landing / GTM** microsite | `ui-ux-pro-max` | `marketing-microsite-design` (hero/section/CTA/pricing patterns) |
| **Editorial / research report**, almanac, explainer | `ui-ux-pro-max` | `editorial-report-design` (reading measure, serif scale, prose charts) |
| **Calculator / single-purpose tool** | `ui-ux-pro-max` | `tool-calculator-design` (input-forward, live recompute) |
| **Docs** site (Fumadocs/Nextra) | `ui-ux-pro-max` | `docs-design` (extend Fumadocs, code-block polish) |
| Anything that must **match an existing brand** | that brand's own token set (brand tokens win) | `dataviz-design` for chart mechanics if it's a dashboard |
| **Creative / culture** side-project | `ui-ux-pro-max` (go expressive) | §6 "bold" styles here; this skill for a11y |

**For EVERY type (the behavioral layer):** also load **`layout-interaction-design`** — spacing/padding/
margin/gap mechanics, button & action placement (incl. the cross-platform order disagreement), navigation
& routing (Next.js App Router: Link/prefetch, layouts, `loading.tsx`, modal routes, active link), and the
full interaction-state set (loading/empty/error, focus management, feedback latency).

If two could apply (e.g. a dashboard that's also a marketing page), pull both supplements and let the
dominant surface win. A brand's own tokens override §3 colors when the brief is "match our brand".

---

## 2. House stack & non-negotiables ✅◐

- **Stack:** Next.js (App Router) + **Tailwind v4** (CSS-first, no `tailwind.config.js`) + **shadcn/ui**
  (init with **Base UI** primitives in 2026: `npx shadcn@latest init --base-ui`) + **Lucide** icons +
  **Recharts** for data. Motion via CSS first, `motion` (ex-Framer) only when needed (§5).
- **Never ship `system-ui` as the brand font.** Pick a real font pair per type (see the per-type
  skill or §4). This single change separates the "product" tier from the "templated" tier.
- **Token-first.** Define semantic CSS variables once; reference them everywhere; never hardcode hex
  in components or charts.
- **Dark vs light:** dashboards & trading = dark-first; tools & docs = either; marketing & editorial =
  often light-first but support both. Never auto-invert semantic colors — re-map them.

---

## 3. Token layer — paste-ready (shadcn + Tailwind v4) ◐

Premium rules baked in: **one saturated accent, everything else neutral; never pure #000/#fff for
text/bg; 8px spacing grid; small consistent radii.** Swap `--accent` per project; keep the rest.

```css
/* globals.css */
@import "tailwindcss";

@theme inline {
  --color-bg: var(--bg);            --color-surface: var(--surface);
  --color-surface-2: var(--surface-2); --color-elevated: var(--elevated);
  --color-ink: var(--ink);          --color-ink-2: var(--ink-2);
  --color-ink-muted: var(--ink-muted); --color-border: var(--border);
  --color-accent: var(--accent);    --color-accent-hover: var(--accent-hover);
  --color-ring: var(--accent);
  --color-pos: var(--pos); --color-neg: var(--neg); --color-warn: var(--warn);
  --radius-sm: 4px; --radius-md: 6px; --radius-lg: 8px; --radius-pill: 9999px;
  --ease-out: cubic-bezier(.16,1,.3,1); --ease-standard: cubic-bezier(.2,0,0,1);
  --dur-fast: 120ms; --dur-base: 200ms; --dur-slow: 320ms;
}

:root {                                  /* LIGHT — never pure white/black */
  --bg:#FFFFFF; --surface:#F6F8FA; --surface-2:#EDF0F3; --elevated:#FFFFFF;
  --ink:#0A1628; --ink-2:#3A4452; --ink-muted:#6B7280; --border:rgba(10,22,40,.10);
  --accent:#635BFF; --accent-hover:#5147E6;      /* ← change per project */
  --pos:#0E9F6E; --neg:#E02424; --warn:#C2700A;
}
.dark {                                  /* DARK — never pure black */
  --bg:#0D0D0F; --surface:#131317; --surface-2:#1A1A20; --elevated:#222229;
  --ink:#F0F0F5; --ink-2:#B0B0BF; --ink-muted:#84848F; --border:rgba(255,255,255,.08); /* ink-muted ≥4.5:1 on dark surfaces */
  --accent:#7C83FF; --accent-hover:#9AA0FF;
  --pos:#22C97A; --neg:#F04F5A; --warn:#E0A800;
}
```

- **Spacing:** 8px grid → `4 · 8 · 12 · 16 · 24 · 32 · 48 · 64 · 96 · 128`. Section padding ≥24–32px;
  let dense content sit inside roomy chrome.
- **Borders:** hairlines, not `<hr>` — 1px at low alpha (`--border`). **Shadows:** minimal; none on flat
  marketing surfaces; soft layered shadow only for true elevation (cards/popovers/modals).
- **Radii:** small + consistent (4/6/8). Reserve `pill` for marketing CTAs, not product chrome.
- For **dense dark dashboards**, `dataviz-design` §2 has the deeper surface/ink ladder, CVD-safe
  diverging P&L, and heatmap ramps — use those there.

---

## 4. Typography ◐ (full detail: per-type skill + research)

- **One modular ratio:** UI/dashboards **1.2**; marketing/editorial **1.25–1.333**. Use `clamp()` fluid
  type, keep a `rem` term so browser zoom works, body ≥16px.
- **Measure:** body `max-width: 60–70ch` (66 ideal); line-height 1.5–1.65 body, 1.05–1.2 headings.
- **Tracking:** negative on large headings only (`-0.02 to -0.03em` ≥24px); `0` body; `+0.05em` on caps.
- **Numerics:** `font-variant-numeric: tabular-nums` on every figure (prices, %, P&L, dates) so digits
  don't jitter. Set on the container, not per cell.
- **Variable fonts** + `font-optical-sizing: auto` on opsz families (Fraunces, Newsreader, Source Serif 4).
- **Default pairs** (all via `next/font/google`): dashboards/tools → **Geist + Geist Mono** or **Inter +
  IBM Plex Mono**; marketing → **Bricolage Grotesque / Fraunces** display + **Geist/Inter** body;
  editorial → **Newsreader / Source Serif 4** body + **Inter** UI; docs → **Inter/Geist + JetBrains Mono**.

---

## 5. A11y, components, motion, responsive ✅◐

**A11y — WCAG 2.2 AA baseline (always):**
- Contrast: body ≥4.5:1, large/UI ≥3:1 (check both themes). Targets ≥24px (44px primary touch).
- Visible `:focus-visible` ring; never bare `outline:none`. Logical tab order; one `<h1>`/page; landmarks.
- Color is never the only signal — pair P&L color with ▲▼/sign. Honor `prefers-reduced-motion` globally.
- Live updates (price/signal ticks) → `aria-live="polite"` / `role="status"`.

```css
:where(a,button,input,select,textarea,[tabindex]):focus-visible{
  outline:2px solid var(--accent); outline-offset:2px; border-radius:4px; }
@media (prefers-reduced-motion: reduce){
  *,*::before,*::after{ animation-duration:.01ms!important; animation-iteration-count:1!important;
    transition-duration:.01ms!important; scroll-behavior:auto!important; } }
```

**Components:** shadcn/ui (own the code; `components/ui/*` IS your design system). Compose with `cva`
variants + `cn()`. Tailwind v4 gotchas: theme in `@theme` (no config.js), OKLCH tokens, `[data-slot]`
styling hooks. **Every interactive element ships 6 states:** default, hover, focus, active, disabled, loading.

**Motion:** CSS transitions for the 90% (hover ~120ms, base ~200ms, slow ~320ms cap, `ease-out`).
`motion` only for spring/gesture/layout/`AnimatePresence` exit orchestration. View Transitions API
(Baseline Oct 2025) for route transitions. **Asymmetric:** enter ~instant/200ms, exit ~150ms opacity.
Spatial/origin-aware (popovers scale from trigger). **No transitions on long lists/tables.**

**Responsive:** mobile-first viewport breakpoints for *page* layout; Tailwind v4 built-in container
queries (`@container`) for *component* layout. Data-dense surfaces get a compact `data-density` mode
(tighter spacing, ≤32px rows) but never below the 24px target floor.

---

## 6. Style picker — name the look, then prompt it ✅◐

Build the **bones** in a credible style, then add **one** texture accent in a hero/scorecard. Reserve
bold styles for side-projects.

**Fintech-safe core (use freely):** **Swiss/International** (grid, sans, typography-as-hero — trust),
**Minimalism** (whitespace, restraint — premium calm), **Editorial/Magazine** (serif display + pull
quotes — authority), **Bento grid** (modular tiles — organized, "keynote"), **Flat/Material** (safe
default), **Glassmorphism** ◐ (frosted cards — *the* premium surface accent, use lightly).

**Use sparingly / side-projects only:** ◐ Neumorphism, Claymorphism, Skeuomorphism, Neo-Brutalism,
Brutalism, Maximalism, Aurora/mesh, Y2K, Synthwave, Memphis, Japandi.

| Type | Primary styles |
|---|---|
| Dashboard | Swiss grid + dark Utilitarian; Glass/Bento for scorecards only |
| Marketing | Bento + Minimalism; Aurora/Glass hero accent |
| Editorial report | Editorial/Magazine + Swiss; Luxury serif for the cover |
| Calculator/tool | Minimalism / Flat + Swiss; one Glass result card |
| Docs | Swiss + Minimalism; Flat-Material components |
| Side-project | Neo-Brutalism / Y2K / Synthwave / Maximalism — distinctiveness > credibility |

---

## 7. Premium-feel checklist — apply to every build ✅

Distilled from Stripe, Vercel/Geist, Linear, Robinhood, Apple, Mercury, Arc. If a generic Tailwind UI
feels "templated," it's usually failing these:

1. **One saturated accent**, everything else neutral — links/primary/active/focus only.
2. **Never pure black/white** for text or bg — deep slate (`#0A1628`) / near-black (`#0D0D0F`); `#000/#fff`
   are only the extreme anchors.
3. **8px spacing grid**; generous section padding; dense content inside roomy chrome.
4. **4–6 size type ramp, one family**; negative tracking on large headings; tabular-nums on all figures.
5. **Semantic color = meaning** (green=up, red=down) applied consistently — never decoration.
6. **Transitions 100–250ms ease-out**, asymmetric (enter ~instant, exit ~150ms), spatial/origin-aware,
   none on long lists.
7. **6 states per interactive element**; visible keyboard focus.
8. **Hairline 1px borders** at low alpha; minimal/zero shadows except true elevation.
9. **Small consistent radii** (4/6/8); pill only for marketing CTAs.
10. **Whitespace = hierarchy** — let content lead, chrome recede.
11. **Constrained gradients** ◐ — ≤3 complementary stops, accents/hero only, never body.
12. **Hard numbers as design** — specific figures over adjectives; data is the decoration in finance UI.
13. **State via environment** — subtle bg tint to signal mode (live/paused, open/closed).
14. **Skeletons over spinners**; instructional empty states (say what's missing + the next action).

---

## 8. Upgrading a ChatGPT/Grok-built project

1. Start at `design-router` → branded work uses the brand's own tokens; everything else runs `ui-ux-pro-max`'s
   `search.py --design-system` for a fresh spec, pulling a §1 supplement only for domain depth. Load this skill on top.
2. Audit against §7. The usual offenders: `system-ui` font, no token layer, flat-gray everything, no
   focus states, default Tailwind blue everywhere, spinners, cramped or inconsistent spacing.
3. Apply in order: **fonts (§4) → token layer (§3) → spacing/grid → components to shadcn → motion → a11y**.
   Fonts + tokens alone usually deliver ~70% of the perceived lift.
4. Verify live on Vercel + run the §5 a11y checklist before calling it done.

---

## Sources
Stripe/Vercel/Linear/Robinhood/Apple/Mercury/Arc teardowns; UX Planet "50 Design Styles"; WCAG 2.2
(w3.org); shadcn/Base UI vs Radix (2026); Motion.dev; Tailwind v4 docs; Typewolf/Google Fonts;
utopia.fyi fluid type. Full per-track notes + URLs synthesized into this skill and the per-type skills.
Treat ◐ as strong defaults; verify palettes with a contrast + CVD checker before shipping.
