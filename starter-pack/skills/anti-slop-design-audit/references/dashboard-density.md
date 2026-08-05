# Dashboard data-density rules

The tell of an AI dashboard is not color — it is low information density and no hierarchy: a uniform grid of evenly-sized cards, one number each, default chart palette. `dataviz-design` owns the palette/dark-surface/token layer; this file adds the numeric density thresholds it is light on. Run this pass on every dashboard/analytics view.

## The core defects → fixes
- **Uniform card grid, everything the same size.** → One **hero metric** (the number the user opens the page for), larger, top-left or top-center. Supporting tiles smaller around it. Not 6 identical cards.
- **Everything evenly spaced, no grouping.** → Group related metrics; use whitespace to separate groups, not to pad a sparse page.
- **Low density — one number per screen of space.** → Analysts want data. Use dense tables, sparklines in rows, small multiples. A dashboard is not a marketing page.
- **Toy charts (default Recharts, 3 rainbow series).** → Semantic series colors (up/down = positive/negative tokens, not red/green rainbow); consider Tremor/Visx for real density; verify contrast on the actual surface.
- **No progressive disclosure.** → Simple view by default; advanced detail behind a toggle/expander. Don't dump every metric at once.

## Numeric thresholds
- **Table/list row height:** 48–52px comfortable · 36–40px dense. Pick one per table; don't let rows default to 64px+ (wastes vertical space, kills density).
- **Number formatting:** tabular-nums (fixed-width digits) so columns align; consistent decimal places per column; abbreviate large values (1.2M) but keep full value in tooltip/title.
- **Hero metric:** 1 per view. Its delta/trend beside it (▲ +4.2%), colored by semantic token.
- **Chart series:** ≤ 5 distinguishable series; beyond that, small multiples or aggregation, not more colors.
- **Grid:** align to an 8pt (or 4pt) grid; column widths sized to content, not all equal.

## Quick dashboard scorecard
- [ ] One clear hero metric, not a uniform card wall.
- [ ] Rows dense (≤ 52px), numbers tabular + aligned.
- [ ] Semantic series palette, contrast-checked on the surface.
- [ ] Sparklines / small multiples / real tables present (not one-number cards only).
- [ ] Progressive disclosure — simple default, advanced on demand.
- [ ] Deliberate grouping + hierarchy, not evenly-spaced everything.

Sources: motherduck (vibecoding dashboards), artofstyleframe (dashboard patterns), developersdigest (AI design slop). Palette/dark-surface tokens: `dataviz-design`.
