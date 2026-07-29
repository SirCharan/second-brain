---
name: working-with-claude
description: >
  Playbook for using Claude / Claude Code most effectively — fastest, cheapest, highest-quality
  output. Load when deciding HOW to do work (not just doing it): whether to use subagents, parallelize,
  or run a Workflow; which orchestration pattern fits (routing / parallel / evaluator-optimizer / judge /
  mixture-of-experts / orchestrator-workers); how to cut tokens & cost; which model (Opus/Sonnet/Haiku/
  Fable); how to brief subagents; how to manage context; and the interview-first discovery discipline.
  Distilled from Anthropic's official guidance (Claude Code best practices, Building Effective Agents,
  multi-agent research system, context engineering, prompt engineering, caching). Trigger on: "use Claude
  effectively", "should I use subagents / parallelize", "use a workflow?", "reduce tokens / cost /
  context", "which model", "speed this up", "orchestrate agents", "mixture of experts / judge / advisor",
  "best practice", "how should we approach this".
---

# Working with Claude — effectiveness playbook

Rule-first. ✅ = Anthropic official · ◐ = derived judgment. The meta-principle from Anthropic: **context is
the scarce resource, and token usage explains ~80% of performance variance** — so the whole game is
maximizing high-signal tokens and minimizing the rest.

---

## 1. Operating loop ✅

**Explore → Plan → Code → Commit.** Read/understand first (plan mode, read-only), write a short spec/plan,
then implement, then commit. **Skip planning only** for ~1-sentence-scope diffs. Don't code before you've
read the relevant code.

**Give Claude a verification check** — a test, build, typecheck, or screenshot. With a check, Claude loops
to pass/fail autonomously; without one, "looks done" is the only signal and you must verify everything.
Bake the check into the request ("…and run `npm run typecheck` until clean").

**Research locally first** ◐ (ECC research-playbook): before web search, inspect local code / logs / config —
most "facts" about your systems live in the repo, the VM, or memory, not the web. Browse only for external or
unstable facts; keep a short evidence trail (`file:line` or url) per claim; stamp dates on things that change.

**Context hygiene** (context degrades as it fills):
- `/clear` between unrelated tasks; don't carry a stale 50k-token thread into a new problem.
- Prefer **subagents for investigation** — they read many files and return a ~1–2k-token summary, keeping
  the main thread clean (see §2).
- On long tasks, compaction summarizes history; tell it what to preserve (file list, test commands,
  open bugs) via CLAUDE.md.

**CLAUDE.md hygiene** ✅ — keep it **ruthlessly short** (bloat → Claude ignores rules). Include commands,
conventions, gotchas, architectural decisions; **exclude** anything inferable from code or standard docs.
Treat it like code: review and prune when behavior drifts.

---

## 2. Delegation & parallelism ✅

**Subagent vs inline — decision rule:**
- **Inline** a single-fact lookup where you know the file/symbol, or a small targeted change.
- **Subagent** when answering means sweeping many files, you want an unbiased second opinion (code
  review in fresh context avoids author bias), or you want to keep big exploration out of the main context.
- **Parallel subagents** (multiple in ONE message) for independent work — Anthropic gets ~90% wall-clock
  savings from 3–5 concurrent subagents, each making parallel tool calls.

**Token tradeoff — respect it** ✅: an agent uses ~**4×** the tokens of a chat turn; a multi-agent system
~**15×** a single agent. **Only fan out when the task value justifies it.** A trivial task does NOT warrant
a workflow (this very request was done with lean targeted research, not a 1M-token fan-out — on purpose).

**Subagent briefing template** (they have zero session context — brief like a new colleague):
```
<task>one concrete objective</task>
<context>only what they need — paths, prior findings, constraints</context>
<constraints>hard rules: length cap, what not to touch</constraints>
<output_format>exact shape you want back</output_format>
```
Cap the response ("under 600 words"). **Model by task** ◐: **Opus** for synthesis/architecture/review;
**Sonnet** for implementation; **Haiku** for cheap noisy work (log scans, file enumeration).

**Workflow tool** — reach for it only when control flow should be deterministic (loops, fan-out over a
list, staged verify) AND the scale is justified. Scout inline first to find the work-list, then pipeline.

---

## 3. Orchestration patterns ✅ (from "Building Effective Agents")

Pick the simplest that fits; compose them.
- **Prompt chaining** — sequential steps, each on the prior output; add a gate/check between.
- **Routing** — classify the input, send to a specialist path. Separation of concerns.
- **Parallelization** — *sectioning* (split into independent subtasks) or *voting* (run the same task N
  times, take consensus). Great for coverage and for reducing variance.
- **Evaluator-optimizer (advisor/critic)** — one agent generates, another critiques against criteria, loop
  until it passes. Use when you have clear quality criteria and iteration helps.
- **Orchestrator-workers** — a lead decomposes dynamically and delegates to workers, then synthesizes. Best
  when subtasks aren't known up front.

Related ◐: **LLM-as-judge** (a fresh agent scores output against a rubric — keep it blind to the author's
reasoning); **mixture-of-experts / ensemble** (N independent attempts from different angles → synthesize
the best); **adversarial verification** (spawn skeptics prompted to *refute* a finding; kill on majority).

**Workflows vs agents** ✅: workflows = predefined code paths (predictable, repeatable); agents =
model-directed (flexible, for uncertain outcomes). Prefer the workflow when the steps are known.

---

## 4. Token / cost / speed cheat-sheet ✅

- **Prompt caching:** cache reads ≈ **0.1× base** input cost. TTL **5 min** (free write) / **1 hr** (2×
  write). Put the **stable prefix first** (instructions/context), mutable content last. Editing tools /
  system prompt / web-search toggle **invalidates that level + everything downstream** — so don't churn the
  prefix. Sleeping a loop past 5 min loses the warm cache.
- **Model selection:** **Haiku** = cheap/fast, high-volume or simple; **Sonnet** = balanced default;
  **Opus** = reasoning-heavy / agentic; **Fable 5** = frontier. Don't run Opus on log-scanning; don't run
  Haiku on architecture.
- **Cut tokens:** **Batches API = 50% off** (async, <1h); **Tool Search ≈ 37%** savings on tool-heavy work
  (load tool schemas on demand); cap `max_tokens`; ask for **concise output** ("answer in 2 sentences"
  beats "<100 words"); strip redundant context; pass IDs/paths and fetch just-in-time instead of pre-loading.
- **Speed:** streaming (best perceived latency); short prompts; **parallel tool calls** in one message;
  caching (near-zero latency on reads); Fast mode (Opus) ≈ 2.5× output speed at premium price.
- **Self-aware rule:** the cost of fanning out is real — match the machinery to the task. Most asks want a
  focused single thread or a few parallel subagents, not a giant workflow.

---

## 5. Interview / discovery discipline ✅ (Anthropic's own recommendation)

For any non-trivial task, **get a full download before building** — Anthropic's best-practices doc literally
recommends: open minimal, have Claude **interview you with AskUserQuestion**, write the spec, then build in
a fresh context. you want this as default behavior.

**Before starting non-trivial work, ask (interactive pills, `multiSelect` where useful):**
1. **Scope** — what's in / explicitly out?
2. **Target environment** — where does this run/deploy? (repo, VM, Vercel project, model)
3. **Output shape** — file? skill? dashboard? report? what format?
4. **Tradeoffs** — speed vs thoroughness, cost ceiling, simplicity vs power.
5. **Done-criteria** — how will we know it's finished and correct (tests? live URL?).

Surface the ambiguities the user *didn't* spell out. **Skip the interview** only for one-line lookups,
single trivial commands, or when the same question was already answered this turn. Recommend a default
when you ask, so it's a confirmation, not a blank.

---

## Sources (✅ official Anthropic)
- Claude Code best practices — code.claude.com/docs/en/best-practices
- Building Effective Agents — anthropic.com/research/building-effective-agents
- How we built our multi-agent research system — anthropic.com/engineering/multi-agent-research-system
- Effective context engineering for AI agents — anthropic.com/engineering/effective-context-engineering-for-ai-agents
- Prompt engineering & extended thinking — platform.claude.com/docs (build-with-claude)
- Prompt caching · Batch processing · Reduce latency · Token-saving / advanced tool use — platform.claude.com/docs + anthropic.com/news
- Companion: the installed `claude-api` skill (model IDs/pricing/params) and `claude-code-guide` agent (Claude Code features).
