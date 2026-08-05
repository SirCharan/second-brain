---
name: tool-calculator-design
description: >
  Design recipes for single-purpose tools and calculators built on Next.js + Tailwind + Vercel —
  a fee/PnL/position-size calculator, a converter, a form-driven utility.
  Covers input-forward layout, instant (no-submit) recompute, result-as-hero with visual breakdown,
  number formatting, inline per-field validation, shareable/permalink results, mobile-first density,
  and the Minimal/Flat look with one glass result card. Load alongside `design-system` (tokens, a11y).
  Trigger on: "calculator", "build a tool", "converter", "estimator", "margin/PnL/fee calc",
  "input form with live result", "single-purpose utility", or styling an interactive calc page.
---

# Tool / Calculator Design

Pair with `design-system` and **`layout-interaction-design`** (form-button placement & the bottom-not-top
rule §2, per-field validation + loading/empty/error states §4). This skill = interaction + layout for
input→output tools. ✅ consensus · ◐ verify.

## Layout — input-forward ✅
- One clear **column of inputs**, results adjacent (desktop) or directly below (mobile). Minimal required
  fields; familiar numeric conventions — don't reinvent inputs.
- **Sensible defaults pre-filled** so a real result shows on load (never an empty/zero screen).
- Progressive disclosure: split complex flows across steps rather than one dense form; hide "advanced"
  inputs behind a toggle.

## Compute — instant, not submit ✅
- **Real-time recompute** as the user types/drags is the modern default — no submit button, no reload. Lets
  users learn the input→outcome relationship by experimenting.
- ◐ Use an explicit submit only for heavy/expensive computation or multi-step qualifying flows.
- Debounce text inputs lightly (~50–150ms) to avoid thrash; recompute is pure/client-side where possible.

## Inputs ✅
- Pair **number fields with sliders** for ranges (mobile-friendly, invites exploration). Steppers for small
  integer ranges. Clear units/symbols inside or beside the field.
- **Inline validation per field on input** (not on submit): specific message ("Leverage must be 1–200×")
  + in-field outline, not a generic top banner. Validate each step early in multi-step tools.

## Result — the hero ✅
- The result is the **largest, highest-contrast** thing on screen. Pair the number with a **visual**
  (bar/donut/breakdown), not raw digits alone.
- **`font-variant-numeric: tabular-nums`**; locale thousands separators; currency/unit symbols; round to
  meaningful precision. Show the formula/breakdown ("notional = qty × price ÷ leverage") for trust.
- Offer **side-by-side scenario comparison** (e.g. 10× vs 50× margin) where it aids the decision.

## Shareable results ◐ (recommended; verify per case)
Encode inputs in the **URL query string / hash** so a result is bookmarkable & shareable, restored on
load; add a "Copy link" button. Optional "Copy result as text/image" for sharing into chat.

## Density & mobile ✅
Mobile-first — these get linked around in chats. Compact spacing, responsive output tables, plain language
(no jargon), large tap targets (≥44px on mobile). One screen ideally; scroll, don't paginate, short tools.

## Look ✅◐
- **Fonts:** clean sans + mono numerics — **Inter + JetBrains Mono** (wide unambiguous digits) · **Geist +
  Geist Mono** · **IBM Plex Sans + IBM Plex Mono** (finance-credible).
- **Style:** ✅ Minimalism / Flat + Swiss grid to foreground inputs/outputs; ◐ one **Glassmorphism** result
  card for polish. Avoid neumorphism/skeuomorphism — weak affordances on the controls that matter most.
- One accent on the primary action + the live result highlight; everything else neutral.

## Pitfalls
A submit button where instant would do · result buried below inputs at body size · proportional figures
that misalign decimals · validation only on submit · desktop-only layout · no shareable state · jargon labels.

## Sources
webuild.io & calc9.com & convertcalculator.com (calculator UX) · design-system skill (tokens/a11y) ·
typewolf.com (mono picks) · MDN/Tailwind font-variant-numeric.
