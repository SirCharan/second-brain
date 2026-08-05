# Writing eval rubric — anchors

Score each criterion PASS / WEAK / FAIL. Reason first (what you observed, with a quoted example), then the score. Default to the lower grade when unsure.

## 1. Clarity
- **PASS** — sentences carry one idea; active voice dominates; terms are consistent; no pronoun is ambiguous; claims are concrete ("within 5s", "exit code non-zero").
- **WEAK** — mostly clear but ≥2 overlong/multi-idea sentences, or one synonym-swap for a key term, or a vague quantifier ("quickly", "several").
- **FAIL** — passive/nominalized throughout, ambiguous references, or the reader must guess what a sentence means.
- Rules from `simplified-technical-english`, `writing-clearly-and-concisely`, `plain-writing`.

## 2. Anti-slop
- **PASS** — no banned openers ("In today's…", "It's worth noting…"), no banned words (delve, tapestry, testament, leverage), sentence length varies, no forced rule-of-three, no throat-clearing intro or empty summary, no em-dash spray.
- **WEAK** — one or two tells present.
- **FAIL** — reads as AI-generated: multiple tells, uniform rhythm, hedging, filler.
- Rules from `stop-slop` (5-dimension) + `anti-ai-slop-writing` (banned-word dictionary).

## 3. Voice
- **PASS** — consistent, specific, human voice; it matches the product's documented voice when there is one (tone adjectives + word lists).
- **WEAK** — generally fine but drifts generic in places, or one off-tone word.
- **FAIL** — generic corporate/AI voice, or wrong voice for the audience.

## 4. Structure (document-level)
- **PASS** — opens with a real hook/lede (not a definition or a windup); ideas flow in a logical order; headings are useful and scannable; length fits the job (no padding, no truncation).
- **WEAK** — decent but a weak opener, or one section out of order, or slightly padded.
- **FAIL** — no clear through-line, buried lede, or wrong length.
- Craft from `writing-composition`.

## Verdict
- **SHIP** — no FAIL and at most one WEAK, AND readability within the surface ceiling.
- **REVISE** — otherwise. List the ranked fixes.

## Surface readability ceilings (Flesch-Kincaid grade)
- Microcopy / UI text: ≤ 7
- Marketing / landing copy: ≤ 9
- Docs / technical prose: ≤ 11
- Long-form / editorial: ≤ 12 (measure, don't force)
