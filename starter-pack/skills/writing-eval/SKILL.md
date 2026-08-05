---
name: writing-eval
description: Graded LLM-as-judge pass for prose — the writing equivalent of anti-slop-design-audit. Scores a piece of writing against an analytic rubric (clarity, anti-slop, voice, structure) with per-criterion reasoning, in detect mode (grade only) or rewrite mode (fix and re-grade), looping until it passes. Use as the pre-ship gate on any substantial prose — docs, README, marketing copy, reports, release notes — or when asked to "grade this writing / score this copy / is this good enough to ship / eval this text". For an unbiased pass, run it in a fresh context (a subagent).
---

# Writing eval — the graded prose gate

The prose counterpart to `anti-slop-design-audit`. Turns the writing skills' rules into a scored pass with a fix loop, so "done" means "measured good", not "looks fine to the author".

## Modes
- **detect** — grade only; output the scorecard + ranked fixes. No edits.
- **rewrite** — fix highest-impact first, then re-grade. Loop until it passes.

## The loop
`draft → grade → fix → re-grade` — exit when no criterion FAILs and at most one is WEAK.

## Rubric (analytic — score each separately, reason before score)
Full rubric with anchors in `references/rubric.md`. The four criteria:
1. **Clarity** — short-enough sentences, one idea each, active voice, one term per concept, no ambiguous pronouns, concrete not vague. (Backed by `simplified-technical-english` + `writing-clearly-and-concisely` + `plain-writing`.)
2. **Anti-slop** — no AI tells (banned openers/words, em-dash spray, rule-of-three padding, uniform sentence length, hedging, empty intros/summaries). (Backed by `stop-slop` + `anti-ai-slop-writing`.)
3. **Voice** — matches the target voice (the product's documented voice when it has one); not generic. If no voice specified, judge for a consistent, human, specific voice.
4. **Structure** — document-level: strong lede/hook, logical argument flow, useful headings, right length for the job. (Backed by `writing-composition`.)

## Objective pre-gate (cheap, deterministic — run first)
Before the LLM judge, get a readability grade (any Flesch-Kincaid tool; `textstat` on PyPI is one line). Fail fast if it breaches the surface ceiling (microcopy ≤ grade 7, marketing ≤ 9, docs ≤ 11), then run the rubric. The number catches drift the judge might rationalize.

## Output
```
WRITING EVAL — <piece> (<detect|rewrite>)
READABILITY: FK grade <n> (ceiling <n>) → PASS/FAIL
CRITERIA:
  - clarity:   PASS|WEAK|FAIL — <observed → why>
  - anti-slop: …
  - voice:     …
  - structure: …
VERDICT: SHIP / REVISE
TOP FIXES: 1. … 2. …
```

## How it fits
Sibling of `anti-slop-design-audit`. Same detect/rewrite/loop shape. Run it in a fresh context (a subagent) for an unbiased score. `writing-router` decides which underlying skills supply each criterion's rules.
