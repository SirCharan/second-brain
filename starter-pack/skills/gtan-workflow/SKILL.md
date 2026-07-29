---
name: gtan-workflow
description: "An operating model for large multi-phase product builds — Garry Tan's GStack loop (Think→Plan→Build→Review→Test→Ship→Reflect) bound to an Obsidian-tracked phase discipline. Load at the START of any large/multi-day build (a new site, app, or product with 3+ phases), and re-load at each phase boundary. Enforces: one master plan + one plan-per-phase in the Obsidian vault, proper automated tests every phase, a written reflection before the next phase begins, small batches (one phase at a time, checkpoint between), and spiking risky new stacks in-browser before pinning versions. Maps each loop stage to the installed GStack tools (/office-hours, /autoplan, /design-shotgun, /review, /qa, /ship, /land-and-deploy, /cso, /benchmark). Requires the gstack pack (see starter-pack/manifest.json). Trigger on: build a large product/site/app, multi-phase project, master plan, phase plan, 'break this into phases', GStack, Garry Tan, gtan, Think Plan Build Review Test Ship Reflect, reflect and replan."
---

# gtan-workflow — disciplined multi-phase product builds

The operating model for anything bigger than a single feature (a site, app, or product spanning multiple phases). Adapted from Garry Tan's **GStack** (`garrytan/gstack`, MIT) + your Obsidian-backed reflection discipline.

## The loop (per phase)
**Think → Plan → Build → Review → Test → Ship → Reflect.** Never skip Review/Test/Reflect; they're where quality and learning live.

## Non-negotiables (you)
1. **One master plan + one plan per phase, in the Obsidian vault** (`<vault>/<project>/master-plan.md` + `phase-N-*.md` + `reflections.md`). Plans are living — update as you work; keep adding.
2. **Proper automated tests EVERY phase.** No phase closes without its tests written and green. If the repo has no harness, adding one is the first phase's deliverable.
3. **One phase at a time.** Build → checkpoint with the user → reflect → then next. Do NOT front-load multiple phases in one stretch (that's how errors hide and rework piles up).
4. **Spike risky stacks in-browser BEFORE pinning versions.** A `npm run build` passing is not proof — client-runtime errors slip through. 10-line smoke render first. (Origin: the R3F/React-19 miss — see the project's reflections note.)
5. **Reflect before you replan.** After each phase, append a reflection (what worked, what broke, what to carry forward) to `reflections.md`, then update the next phase's plan with those learnings *before* starting it.

## Stage → GStack tool map
| Loop stage | Use |
|---|---|
| Think | `/office-hours` (forcing questions), interview you (AskUserQuestion) |
| Plan | `/autoplan` (CEO→design→eng review), write the phase plan note |
| Build | the build; `/design-shotgun`→`/design-html` for UI; specialist subagents |
| Review | `/review` (staff-eng audit), `/cso` (security) on sensitive surfaces, adversarial-verify workflow |
| Test | write + run the phase's unit/e2e; `/qa` (live browser); `/benchmark` (Web Vitals) |
| Ship | `/ship` (tests→push→PR); preview deploy between phases |
| Reflect | append to `reflections.md`; update next phase plan |

Final phase only: `/land-and-deploy` → prod + `/canary` post-deploy watch.

## Cadence
Start of build: write master plan + phase stubs. Each phase: Think/Plan (expand that phase's stub) → Build → Review → Test → Ship (preview) → checkpoint with the user → Reflect → expand next stub. One production deploy at the end.

## Install (GStack itself)
`git clone --single-branch --depth 1 https://github.com/garrytan/gstack.git ~/.claude/skills/gstack && cd ~/.claude/skills/gstack && ./setup` (needs `bun`). The setup script registers 23 commands and builds a browser binary, so give it a few minutes and network access.

Related: `second-brain` skill (vault mechanics) · `working-with-claude` (orchestration) · `design-router`.
