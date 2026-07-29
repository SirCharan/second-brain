---
name: editorial-report-design
description: >
  Design recipes for editorial / long-form / research-report web pages — almanacs, deep-research
  write-ups, explainers, thought-leadership, a personal essay site. Covers reading measure, serif body typography, the
  editorial type scale, drop caps / pull quotes / footnotes, charts-embedded-in-prose, TOC/scroll-spy,
  and the Magazine/Swiss/Luxury-serif look. Load alongside `design-system` (tokens, a11y, motion).
  Trigger on: "research report", "long-form", "editorial", "almanac", "explainer", "essay", "article
  layout", "whitepaper", "reading experience", "prose typography", or any text-heavy narrative page.
---

# Editorial / Research-Report Design

Pair with `design-system`. This skill = reading experience, prose typography, and the editorial look.
✅ verified · ◐ judgment.

## Reading measure & body ✅
- Wrap prose in **`max-width: 65ch`** (66 ideal; research converges on 45–75 CPL). Figures, charts, and
  pull quotes may break out wider than the text column.
- **Body 18–20px**, `line-height: 1.6`, a screen-tuned **serif** for sustained reading.
- One **modular ratio 1.25–1.333**; headings on the same fluid `clamp()` scale as the body.

## Type pairings ✅◐
- **Newsreader** (body, opsz) + **Inter** (UI/labels/captions) — warm, screen-tuned for long reading.
- **Source Serif 4** + **Source Sans 3** — matched superfamily, excellent cross-OS hinting.
- **Fraunces** (display/body, soft+wonky axes) + **IBM Plex Sans** (UI) — distinctive masthead.
- EB Garamond is the OSS book-serif option (lower screen contrast — use ≥18px). All via `next/font/google`;
  enable `font-optical-sizing: auto` on opsz families.

## Prose details ✅◐
- **Paragraphs:** pick ONE — space-between (`margin-block: .75–1em`, "web") **or** first-line indent
  (`text-indent: 1.5em`, no top margin, "book"). Never both.
- **Drop cap** (one per article opener, never per section):
  ```css
  .prose > p:first-of-type::first-letter{
    float:left; font-size:3.2em; line-height:.8; padding-right:.06em; font-weight:600; }
  ```
- **Pull quotes:** 1.3–1.5× body, lighter weight, slight negative tracking, indented or full-bleed with a
  hairline rule. **Restate**, never duplicate body verbatim.
- **Footnotes:** superscript `<sup>` refs with tabular figures; render as margin notes (`ch`-wide aside on
  wide viewports, collapse inline/bottom on mobile); focusable back-links.
- `text-wrap: pretty` on body, `balance` on headings; hang punctuation for premium editorial.

## Structure ✅
- **TOC / scroll-spy** for anything long: sticky right rail (desktop) highlighting the current section via
  IntersectionObserver; collapses to a top dropdown on mobile.
- Section dividers as **hairlines or generous whitespace**, not heavy rules. Reading-progress bar ◐ optional.
- **Charts in prose:** embed Recharts/figures full-measure or wider with a caption; keep chart type
  minimal (line/area/bar); reference `design-system` / `dataviz-design` tokens — never default chart colors.
  Number callouts inline use `tabular-nums`.

## Look ✅◐
- ✅ **Editorial/Magazine** (typography-forward, strong hierarchy, asymmetric columns) + ✅ **Swiss** grid
  for rigor. ◐ **Luxury serif** (wide tracking, restrained gold/foil accent) for the cover/title moment.
- Mostly **light-first** (paper-like `--bg` near-white, warm-neutral ink) — long reading on dark is
  fatiguing; offer a dark toggle but tune it (ink ~`#E8E4DC`, not pure white, to cut halation).
- Imagery: atmospheric, full-bleed openers; consistent caption style; one accent color, used in links +
  pull-quote rules only.

## Pitfalls
Full-width body text (>75ch) · sans-serif body for long reading · drop caps everywhere · pull quotes that
repeat the paragraph · default chart colors · no TOC on a 3,000-word page · dark mode with pure-white ink.

## Sources
baymard.com & fonts.google.com/knowledge (measure) · pimpmytype.com (line length/height) · typewolf.com
(serif picks) · moderncss.dev & utopia.fyi (fluid scale) · MDN font-variant-numeric.
