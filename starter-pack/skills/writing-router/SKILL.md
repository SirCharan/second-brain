---
name: writing-router
description: The canonical map of the writing skills — which one to use when, collapsing the five overlapping skills into two axes (clarity + anti-slop) and resolving the sentence-length contradiction between them. Load this FIRST for any writing task to pick the right skills without redundancy, then apply them. Trigger on "write", "draft", "edit prose", "which writing skill", or at the start of any docs/copy/content work.
---

# Writing router

The five writing skills overlap heavily. This is the map: two axes, one composition layer, one graded gate. Load this first, then pull only what the task needs.

**Bundled here:** `simplified-technical-english`, `writing-composition`, `writing-eval`.
**Fetched separately** (see starter-pack/manifest.json): `stop-slop`, `anti-ai-slop-writing`,
`plain-writing`. `writing-clearly-and-concisely` is any Elements of Style reference skill — the
1918 text is public domain.

## Two axes (this is all the line-level skills reduce to)
- **CLARITY** — is each sentence unambiguous and easy to parse?
  - `simplified-technical-english` — procedures/docs: short sentences, one instruction each, consistent terms.
  - `writing-clearly-and-concisely` (Strunk) — sentence strength, cut deadwood.
  - `plain-writing` — plain everyday words, no jargon.
- **ANTI-SLOP** — does it read as human, not AI-generated?
  - `stop-slop` — PRIMARY. The 5-dimension rubric (openers, jargon, contrasts, passive, specificity). Use this one.
  - `anti-ai-slop-writing` — use ONLY as the banned-word dictionary (delve/tapestry/testament…) + punctuation ratios. Don't run its full workflow alongside stop-slop; they duplicate.

## Composition layer (document-level, the real gap the axes don't cover)
- `writing-composition` — hook/lede, argument structure, headings, flow, length. Line-level skills polish sentences; this shapes the whole piece.

## Voice
- Match the product's own documented voice when it has one. Otherwise judge for a consistent, specific, human voice.

## Graded gate
- `writing-eval` — the pre-ship pass (rubric + readability). Run it in a fresh context (a subagent) so the author is not grading its own work.

## RESOLVED: the sentence-length contradiction
The skills disagreed (plain-writing → longer explanatory; anti-ai-slop → mix 4–30 words; stop-slop → shorter, two beats three). **Canonical rule, this wins:**
> **Vary sentence length; median ~15 words, range ~8–25. Never two long (>25w) sentences in a row. Use a long sentence only when the idea genuinely needs it (an explanation that breaks if chopped). Default short; earn every long one.**

This satisfies all three: variety (anti-slop), a short default (stop-slop), and room to explain (plain-writing).

## Compose order for a document
`writing-composition` (shape it) → clarity axis (tighten sentences) → anti-slop axis (de-tell) → `writing-eval` (grade before ship).
