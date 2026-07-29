---
name: discovery
description: >
  Interview-first discovery routine — run an interactive spec interview BEFORE building anything
  non-trivial. Use when you type /discovery, or at the start of any larger task (new site/app/feature/
  dashboard/report/tool, a multi-step build, or a vague "make it better" ask). Turns a fuzzy ask into a confirmed spec + plan
  before code. Skip for one-line lookups, trivial fixes, or when you already answered this turn.
---

# /discovery — interview-first spec, then plan

the standing rule (CLAUDE.md + working-with-claude): get a full download before building. This
operationalizes it. Adapted from Anthropic's "interview-first spec" guidance.

## Steps
1. **Read the room first.** Skim the relevant code/memory (spawn an Explore subagent if scope is
   uncertain) so questions are informed, not generic. Recall: `/second-brain pull <terms>` if stuck.
2. **Interview with `AskUserQuestion`** — 2–4 questions, `multiSelect: true` where apt. Cover the five
   axes, and **recommend a default in each** (first option, "(Recommended)") so it's a confirmation,
   not a blank:
   - **Scope** — what's in / explicitly out.
   - **Target environment** — repo, stack, deploy target, live vs sandbox (esp. money systems).
   - **Output shape** — files, UI, report, API; format + where it lands.
   - **Tradeoffs** — speed vs thoroughness, cost ceiling (OpenRouter cap), token budget.
   - **Done-criteria** — how you will know it's finished + how to verify.
   Surface the ambiguities you might not have spelled out — that's the value.
3. **Restate the spec** in 2–3 lines from the answers; note assumptions taken.
4. **`TaskCreate` a plan** (for 3+ step work) and execute step-by-step, marking tasks inline.
5. **Hand the work a verification check** (test/build/live URL) so it self-checks, not guesses "done".

## Notes
- If it's genuinely small, say so and just do it — don't ceremony a one-liner.
- For large multi-phase builds, escalate to `gtan-workflow`; for the pure UI pipeline, `/design-build`.
- Reach for this yourself at the start of any larger task; nothing forces it on you.
