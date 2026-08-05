# Audit protocol — severity rubric + output

Grade every finding P0/P1/P2. Record `file:line` for each. Full tell-catalogue + "what premium looks like" lives in `anti-slop-design-law`; this file is the graded rubric.

## P0 — instant "AI-generated" tells (ship-blockers)
Any one of these reads as machine-generated on sight. Fix before ship.

- **Purple→blue (or indigo→violet) gradient hero.** The 2022–23 generated default. Fix: solid brand surface, or a subtle two-stop gradient in brand hues with SVG grain < 0.1 opacity.
- **Three feature cards, each a Lucide icon in a tinted tile + heading + one line.** Fix: asymmetric layout, real content, vary card weight; lead with the strongest.
- **Blurred mesh / aurora blob background** (pink/purple/cyan). Fix: remove, or replace with one authored signature artifact.
- **Inter / system-ui / Geist as the brand display face.** Fix: a character display face for headings (licensed/self-hosted); never `system-ui` as the brand.
- **Untouched shadcn defaults** — default radius, default zinc palette, default card. Fix: customize tokens/radii; make the components yours.
- **`rounded-2xl shadow-lg` on every surface.** Fix: intentional radius scale + real layered depth (see P1 shadows).
- **Centered everything, single column, evenly stacked.** Fix: break the axis — bias content left/right, vary rhythm.
- **Emoji as bullets / section markers.** Fix: real list styling or icons from the system set.
- **Template hero** — big number/stat + supporting stats row + gradient accent. Fix: lead with the actual content/value, not a stat-block skeleton.
- **Numbered sequences (01 / 02 / 03)** used where order carries no meaning. Fix: drop the numbers or use them only for genuine steps.

## P1 — no craft (fix before ship)
- **Flat hierarchy** — headings barely larger than body, one type weight. Fix: a real type scale, decisive size/weight jumps.
- **No signature element** — nothing on the page you'd remember. Fix: decide ONE signature artifact FIRST (the deepest anti-slop-law rule).
- **Faked/boxy shadows** — uniform `box-shadow` with no light source. Fix: layered shadows with consistent light direction, or real elevation tokens.
- **Uniform evenly-spaced grid** — every element the same size/gap. Fix: deliberate density + emphasis (one thing dominates).
- **Generic rainbow chart palette** (default Recharts/library colors). Fix: semantic series palette; verify WCAG on the actual surface.
- **Untreated navigation** — default top bar, no thought. Fix: treat the nav (density, active state, one considered detail).
- **Timid typographic contrast** — weights at 400/600, size jumps of only ~1.5×. Fix: use the extremes — display weights 100/200 OR 800/900 (not 400/600), and size jumps of 3×+ between levels. This is the single biggest "designed vs generated" type signal (Anthropic official guidance).
- **Second-order defaults** — the once-fresh-now-converged picks: Space Grotesk, the "safe-distinctive" choices everyone now reaches for. Fix: flag your own font/color as possibly-converged; pick something the subject actually warrants.
- **Evenly-distributed palette** — colors used in equal amounts. Fix: one dominant color + one sharp accent beats an even spread.

## P2 — polish (optional)
- Micro-spacing off the 8pt grid; optical (not mathematical) alignment.
- Motion: > 300ms, non-transform properties, no `prefers-reduced-motion` guard, no ease-out.
- Missing empty / loading / error states.
- Measure (line length) outside 45–75ch for reading text.

## Calibration (drop false positives)
A tell is only a finding if it is unintentional. A deliberate, on-brand choice (e.g. a chosen accent gradient that is NOT the purple default, a single centered layout that fits the content) is not slop. Keep only real defects; note the intent when you drop one.

## Exit criterion
Re-audit after fixes. **Ship when P0 = 0 and P1 = 0.** P2 is judgment — fix what the timeline allows.

Sources: pols.dev anti-slop law (`anti-slop-design-law`), developersdigest "16 AI-design patterns", monet.design, dev.to/alanwest.
