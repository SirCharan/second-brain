---
name: dataviz-design
description: >
  Researched best-practices for designing & building data-dense analytics dashboards,
  trading/financial UIs, charts, and dark-mode design systems. Use when building or
  reviewing a dashboard/analytics UI, choosing a color palette or theme tokens, styling
  charts (Recharts/dataviz), designing PnL/heatmap color, picking typography/motion, or
  structuring information architecture (progressive disclosure, scorecards, simple/advanced).
  Contains: the coordinated cross-filtering interaction model, CVD-safe color systems with
  paste-ready hex/OKLCH tokens, dark-surface elevation, sequential/diverging palettes,
  typography & numerics, motion specs, IA playbook, reference-product teardowns, and 3
  ready-to-use visual identity directions. Stack-agnostic but with Next.js + Tailwind v4 +
  Recharts implementation notes. Trigger on: "dashboard UI", "data viz", "chart colors",
  "dark theme", "design system", "make this UI better", "fintech/trading UI", "pick a palette".
---

# Data-Viz & Analytics UI Design

Synthesized from a deep-research pass (OpenBB Workspace, Bloomberg, TradingView, Stripe,
Mercury, Linear, Apple HIG, IBM Carbon, Datawrapper, Tableau, ColorBrewer, shadcn, Recharts).
**Confidence is labeled per section** — ✅ = survived 3-vote adversarial verification against a
primary source; ◐ = well-sourced design guidance (reputable refs, not formally verified). Treat
◐ as strong defaults, not dogma.

> **Part of the design-skill family.** Load the **`design-system`** skill alongside this one — it owns
> the shared token layer, WCAG 2.2 a11y baseline, shadcn component baseline, motion/responsive defaults,
> the style picker, and the premium-feel checklist. This skill is the **dashboard/data-viz** specialist:
> the deeper dark-surface ladder, CVD-safe diverging P&L, heatmap ramps, and the interaction model below.
> For spacing mechanics, button/action placement, navigation/routing, and interaction states, also load
> **`layout-interaction-design`**.

---

## 1. Interaction model — the spine ✅

For any multi-view analytics tool, the interaction model matters more than the skin. Three
patterns are the verified professional-quant-desk idiom (OpenBB Workspace docs):

1. **Coordinated cross-filtering.** A single store of *shared parameters* (e.g. SL/TP, costs,
   filters, date range, ticker) propagates to **every** view at once. Changing a control in the
   rail re-renders all tabs/charts simultaneously. Implement as one parameter store
   (Context/Zustand/signals) keyed by parameter name; every chart subscribes. *"When widgets
   share parameter names…all widgets in the same group update automatically."*
2. **Inline sparklines in dense tables.** Per-row line/area/bar micro-charts inside table cells
   show trend without leaving the table (equity-per-row, MAE/MFE micro-trend, rolling PnL).
   Tiny axis-less chart or a hand-rolled inline SVG for hundreds of rows.
3. **Selection-driven drill-down / click-to-isolate.** Select a point/range/cell → instantly
   spawn a focused visualization. Click an optimization-surface cell → isolate that param pair's
   equity curve; brush-select a scatter cluster → drill into those trades; select table rows →
   focused PnL chart.

Supporting (◐): **linked brushing** (drag-select in one chart highlights the same data in
others) is a specific form of cross-filtering; **hover-scrub** with a shared crosshair across
stacked time charts (equity + drawdown) reads as one instrument. In Recharts, `syncId` ties
tooltip/brush across charts that share it. Always give the user **overview first, then
zoom/filter, then details on demand** (Shneiderman's mantra).

---

## 2. Color system — paste-ready tokens ◐

### Principles
- **Avoid pure `#000`.** Near-black `#0A0A0A–#16161A` with a faint cool chroma reads as "dark
  glass," eases fatigue, preserves OLED savings.
- **Elevation by luminance, not shadow.** Step surfaces ~+3–5 L (OKLCH) per level; shadows are
  weak on dark bg.
- **CVD safety (~8% of men).** Never rely on red/green *alone* — always add a non-color cue
  (▲/▼, +/−, bar direction, shape). For maximum safety use a **blue/amber** diverging pair.
- **Grayscale-safe.** Vary palette stops by **lightness** so they survive black-and-white
  ("get it right in grayscale").
- **WCAG 1.4.11**: meaningful graphics want ≥ 3:1 contrast vs adjacent colors.

### Dark surface ladder (canvas → highest)
`#0D0D0F` · `#131317` · `#1A1A20` · `#222229` · `#2C2C36`

### Light surface ladder
`#F5F5F7` · `#EDEDF0` · `#E4E4E9` · `#D8D8DF` · `#CCCCD4`

### Ink (text) — dark / light
primary `#F0F0F5` / `#0D0D0F` · secondary `#B0B0BF` / `#3A3A48` · muted `#70707F` / `#70707F` ·
faint `#3A3A48` / `#B0B0BF`

### Diverging PnL — two variants (pick per audience; both need a non-color cue)
- **Trader-convention (dark-tuned), lightness-matched:** loss `#F04F5A` · zero `#3A3A48` · gain `#22C97A`
- **CVD-safe blue/amber (default when accessibility is non-negotiable):** loss `#E07B00` · zero `#3A3A48` · gain `#3B9FE8`

### Sequential heatmap (low→high, viridis-like, perceptually uniform)
`#1A1040` · `#2A3080` · `#1E7A8C` · `#1AA87A` · `#8BC94A` · `#D4D62A` · `#FDE725`
Diverging-at-zero for signed metrics: `#3B9FE8` → `#3A3A48` → `#22C97A`.

### Accents on near-black (base / hover / active), all ≥ 3:1
blue `#3B9FE8`/`#5FB3F0`/`#2882D0` · amber `#E07B00`/`#F59520`/`#C06800` ·
violet `#9B71EA`/`#B38FF0`/`#7E57D0` · teal `#1AA87A`/`#2DC98F`/`#128A63`

### CSS tokens (paste)
```css
:root{
  --surface-0:#0D0D0F; --surface-1:#131317; --surface-2:#1A1A20; --surface-3:#222229; --surface-4:#2C2C36;
  --ink-primary:#F0F0F5; --ink-secondary:#B0B0BF; --ink-muted:#70707F; --ink-faint:#3A3A48;
  --pnl-gain:#22C97A; --pnl-zero:#3A3A48; --pnl-loss:#F04F5A;
  --pnl-cvd-gain:#3B9FE8; --pnl-cvd-loss:#E07B00;
  --accent-blue:#3B9FE8; --accent-amber:#E07B00; --accent-violet:#9B71EA; --accent-teal:#1AA87A;
  --heat-0:#1A1040; --heat-1:#2A3080; --heat-2:#1E7A8C; --heat-3:#1AA87A; --heat-4:#8BC94A; --heat-5:#D4D62A; --heat-6:#FDE725;
}
.light{
  --surface-0:#F5F5F7; --surface-1:#EDEDF0; --surface-2:#E4E4E9; --surface-3:#D8D8DF; --surface-4:#CCCCD4;
  --ink-primary:#0D0D0F; --ink-secondary:#3A3A48; --ink-muted:#70707F; --ink-faint:#B0B0BF;
}
```
Define ramps in **OKLCH** when you can (wide-gamut, perceptually uniform). Never *auto-invert*
semantic colors for dark mode — re-map them.

---

## 3. Typography & numerics ◐
- **Numbers get `font-variant-numeric: tabular-nums`** — always, even inline. Right-align numeric
  table columns so digits line up for scanning.
- Pair a clean UI sans with a mono for figures/data columns (the mono signals "this is data").
- Restrained scale: ~11px labels (uppercase, tracked) · 13px body · 20px tile values · 28–40px
  hero numbers. Tight letter-spacing on large headings.
- Sticky table headers; section headers as visual anchors.

## 4. Motion & micro-interactions ◐
- **150–200ms** for hovers/state; **250–300ms** for panel/modal; Apple-ish easing
  `cubic-bezier(0.32,0.72,0,1)` or `(0.16,1,0.3,1)`. Avoid bounce in serious trading UI (a touch
  of spring is fine in "craft" identities).
- Fade/slide content on tab change; flash/pulse a value when it changes by a threshold; optimistic
  instant UI (Linear) over spinners.
- Honor `prefers-reduced-motion`; gate `backdrop-filter` blur (GPU cost) behind it / capability.

## 5. Depth & materials ◐
- Layered near-black surfaces (luminance ladder above) + hairline borders `rgba(255,255,255,.07)`.
- Glass: `background: rgba(255,255,255,.04); backdrop-filter: blur(20px) saturate(150%); border:1px
  solid rgba(255,255,255,.09)` + soft shadow + faint inner top highlight. Use sparingly (header,
  nav, palette, modals) — not every card.
- A faint radial "aurora" wash behind the canvas adds depth without noise.

---

## 6. Information architecture ◐
- **Progressive disclosure** (NN/g): row 1 = ~5 KPI scorecard tiles (always visible) → row 2 =
  collapsible stat groups (Return / Risk / Path / Robustness) → row 3 = row-click drill-down
  modal. Persist open/collapsed state in `localStorage`.
- **Simple vs Advanced mode**: Simple shows the few controls that matter (SL/TP, date, return
  mode); Advanced reveals filters/costs/methods. Default Simple, persist choice, give experts a
  one-glance escape.
- **Empty/onboarding**: ship a default config that "just works" and produces a non-empty result
  on first load; never show blank charts. Inline `?` tooltips define every stat. Warn when filters
  cut the sample below significance ("Only N trades — may not be significant. Reset?").
- **Density & speed**: tabular numerals, right-aligned numbers, sticky headers, sparkline columns,
  and a **⌘K command palette** (cmdk) for tab nav / presets / set-param / export.

---

## 7. Reference teardowns (what to steal) ◐
- **Bloomberg Terminal** — extreme density without tabs, keyboard-first, color-coded labels as a
  second axis. (Don't copy the monospace monoculture.)
- **TradingView** — interaction *on* the data canvas (drawing/scrub), collapsible indicator panels
  that don't reflow, strategy-as-text beside visuals.
- **OpenBB Workspace** — shared-parameter widget grid; selection-based charting; sparkline tables.
- **Stripe Dashboard** — the stat tile (big number + delta badge + sparkline), section "Learn
  more" tooltips, immaculate right-aligned currency tables.
- **Mercury** — "calm finance": breathing room even when dense, section headers as anchors.
- **Linear / Arc / Raycast** — ⌘K as primary nav, optimistic instant UI, one-click collapse,
  craft-level motion.

---

## 8. Three ready visual-identity directions ◐
Pick one as a starting point; each ships canvas/ink/accent + P&L hexes, type, and motion mood.

### A) Carbon Terminal — dark quant-pro (Bloomberg×Vercel)
Canvas `#0A0A0A` · surface `#111111` · ink `#E8E8E8`/`#6B6B6B` · accent `#00E5FF` ·
P&L `+#00C896` / `−#FF4D4D`. Type: **IBM Plex Sans** + **IBM Plex Mono**. Motion: 120ms ease-out,
200ms panels, no bounce. Dense, authoritative; keep cyan to borders/active. Eye-fatiguing for long
sessions.

### B) Porcelain — light fintech (Stripe×Mercury)
Canvas `#F8F8F7` · surface `#FFFFFF` · ink `#1A1A1A`/`#71717A` · accent `#4F46E5` ·
P&L `+#059669` / `−#DC2626`. Type: **Inter** + **JetBrains Mono** (numbers). Motion: 150ms hover,
250ms spring `cubic-bezier(0.34,1.56,0.64,1)`. Airy, premium, daylight-legible; calibrate heatmap
contrast on white; some quants distrust light.

### C) Obsidian Glass — dark consumer-craft (Arc×Linear×Apple)
Canvas `#0F0E11` · glass surface `rgba(255,255,255,.06)` (border `rgba(255,255,255,.10)`) · ink
`#F0EDE8`/`#8A8490` · accent `#F59E0B` (amber) · P&L `+#34D399` / `−#F87171`. Type: **Geist** +
**Berkeley Mono** (fallback Fira Code). Motion: 180ms data, 300ms `cubic-bezier(0.16,1,0.3,1)`
panels, `backdrop-blur-md`. Warm, tactile, delightful; blur is GPU-heavy → gate on reduced-motion;
keep amber to active states.

---

## 9. Implementation notes (Next.js + Tailwind v4 + Recharts)
- **Tailwind v4**: define tokens as CSS custom properties in `globals.css`, expose to utilities via
  `@theme inline { --color-*: var(--token) }`. Theme switch by scoping vars under `.light`/`.dark`
  (or `[data-theme]`).
- **Charts**: Recharts reads literal colors — reference `var(--token)` or inject from the token set;
  with Recharts v3 use `var(--chart-1)` (not `hsl(var(...))`). Use `syncId` for linked tooltip/brush.
  No native heatmap → render a **CSS grid** of cells colored via `chroma-js`/lerp (avoid Tremor:
  Tremor v3 is incompatible with Tailwind v4).
- **Sparklines**: axis-less `<LineChart>`/inline SVG; memoize.
- **⌘K**: `cmdk` or a hand-rolled overlay; commands = navigate/preset/set-param/export.

---

## 9b. Dashboard a11y, component states, density & live data ✅◐
Dashboard-specific add-ons to the `design-system` baseline:
- **A11y beyond color** ✅: P&L/trend must carry a non-color cue (▲▼, +/−, shape) — never red/green alone.
  Live price/signal ticks → `aria-live="polite"` / `role="status"` so screen readers hear changes. Keep
  charts keyboard-reachable; give each a text summary or data-table fallback. Verify ≥3:1 for series vs
  background and vs adjacent series (WCAG 1.4.11).
- **Component states** ✅: every KPI tile, filter chip, table row, and chart legend ships the 6 states
  (default/hover/focus/active/disabled/loading). Tables get hover-row highlight + sticky header + keyboard
  row focus. Loading = **skeletons that mirror the incoming layout**, not spinners.
- **Live-data UX** ✅: show **last-updated timestamp + sync status + manual refresh**; surface stale/offline
  ("Data as of 10:42" / "Reconnecting…") instead of silent staleness; offer a **pause/freeze** control so
  users can read under motion. Pair each KPI with a sparkline (7–30d) + directional arrow + % delta.
- **Update motion** ◐: 200–400ms count-up/fade on value change to beat change-blindness; list reorder <300ms
  to preserve spatial memory; **no transitions on long rows/tables**. Use `motion` only for layout/spring;
  CSS handles the rest.
- **Density** ◐: ship a comfortable default + a compact `data-density` mode (tighter `--spacing`, ≤32px rows)
  toggled via one attribute — never below the 24px target floor. ~5 KPIs per view, critical metric upper-left.
- **Component layer** ◐: build on shadcn/ui (Base UI primitives, 2026); container queries (Tailwind v4
  `@container`) for cards/panels that live in varying-width slots — more robust than viewport breakpoints.

## 10. Confidence & sources
**Verified ✅ (primary):** coordinated cross-filtering, sparkline tables, selection drill-down —
OpenBB Workspace docs. Everything else is ◐ well-sourced design guidance (not formally verified;
some refs are blog-quality). Validate palettes empirically with a CVD simulator + contrast checker
before shipping.

Sources: OpenBB Workspace (docs.openbb.co/workspace) · Datawrapper colorblindness
(blog.datawrapper.de) · Tableau red/green (tableau.com/blog) · IBM Carbon dataviz
(carbondesignsystem.com/data-visualization/color-palettes) · ColorBrewer (colorbrewer2.org) ·
Apple HIG dark mode · shadcn charts (ui.shadcn.com) · Recharts SynchronizedLineChart · NN/g
progressive disclosure (nngroup.com) · Shneiderman visual-seeking mantra · WCAG 2.1 SC 1.4.11 ·
oklch.com.
