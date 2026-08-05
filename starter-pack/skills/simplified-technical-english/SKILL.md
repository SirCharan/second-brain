---
name: simplified-technical-english
description: Write clear, unambiguous technical documentation using a pragmatic adaptation of ASD-STE100 Simplified Technical English. Use when writing or reviewing manuals, procedures, step-by-step instructions, API references, runbooks, release notes, tooltips, error messages, or any technical content that must be understood the same way by every reader (including non-native speakers). Trigger on "technical docs", "procedure", "manual", "runbook", "write instructions", "STE", "simplified technical english", "controlled language", "make these docs clearer".
---

# Simplified Technical English (pragmatic)

Controlled-writing rules adapted from ASD-STE100 (the aerospace Simplified Technical English standard) for general technical documentation. Goal: **one text, one meaning, understood the same way by every reader.** Pragmatic, not the rigid aerospace dictionary — use these rules for docs, procedures, and reference text without sounding robotic.

## When to apply
- Procedures, step-by-step instructions, runbooks → apply strictly (imperative, one action per step).
- API refs, config docs, tooltips, error messages → apply strictly (precision matters most).
- Conceptual/overview prose → apply the sentence and word rules; relax the "one instruction per sentence" rule.

## The core rules (fast version)
1. **Short sentences.** Procedures ≤ 20 words. Descriptive text ≤ 25 words. One idea per sentence.
2. **One instruction per sentence.** Two actions → two sentences (or a numbered list). Never chain steps with "and then".
3. **Active voice, present tense.** "The service reads the file." Not "The file is read by the service." Imperative for instructions: "Restart the service." Not "The service should be restarted."
4. **One term, one meaning.** Pick a word for a thing and reuse it everywhere. No synonym variety. `directory` OR `folder` — not both. Never rename a thing mid-document.
5. **No ambiguous pronouns.** If "it"/"this"/"they" could point to more than one noun, repeat the noun. "Restart the service. **The service** then reloads config." Not "It then reloads config."
6. **No noun clusters > 3.** "runtime cache invalidation policy handler" → "handler that invalidates the runtime cache".
7. **Define abbreviations once,** at first use, then reuse consistently. Don't switch between the abbreviation and the spelled-out form.
8. **Say what to do, not only what not to do.** Give the positive instruction first. Warnings state the condition, then the consequence, then the action.
9. **Concrete over vague.** "within 5 seconds" not "quickly". "if the exit code is non-zero" not "if it fails".
10. **Parallel structure in lists.** Every bullet/step starts the same grammatical way (all imperatives, or all nouns). Never mix.

## Procedure format
- Number the steps. One action per step.
- Start each step with the imperative verb: "Open…", "Run…", "Verify…".
- Put the condition before the action: "If the token expired, run `login.sh`." Not "Run `login.sh` if the token expired."
- Warnings/cautions go **before** the step they apply to, never after.

## Sentence checklist (apply while writing)
- Under the word limit? One idea?
- Active? Present or imperative?
- Every pronoun's referent obvious?
- Same term used as elsewhere in the doc?
- Could a non-native reader mis-parse it? → simplify.

## References (load when needed)
- `references/writing-rules.md` — the 9 rule groups in full with before/after examples.
- `references/dictionary.md` — approved plain verbs + a "don't use → use" swap table (kills wordy/vague phrasing).
- `references/checklist.md` — the pre-ship review pass to run on a finished document.

## How to use with the other writing skills
STE governs **clarity and unambiguity**. Pair it with:
- `stop-slop` / `anti-ai-slop-writing` — strip AI tells and filler after the STE pass.
- `writing-clearly-and-concisely` (Strunk) — sentence-level strength and concision.
- `plain-writing` — plain-language word choice.

Order for a doc: draft → STE pass (rules above) → Strunk/plain pass (tighten) → anti-slop pass (de-tell) → checklist.
