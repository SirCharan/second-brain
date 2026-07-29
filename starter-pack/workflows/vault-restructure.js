export const meta = {
  name: 'vault-restructure',
  description: 'Split oversized notes, merge shards, consolidate obsidian-system notes, rebuild MOC hubs, verify zero fact loss',
  phases: [
    { title: 'Backup', detail: 'tar the vault to ~/.claude/vault-backups' },
    { title: 'Hygiene', detail: 'move backups out, rotate logs, prune state' },
    { title: 'Split', detail: 'one agent per folder — atomize >8KB notes' },
    { title: 'Merge', detail: 'drishti-seo shards + obsidian-system consolidation' },
    { title: 'Hubs', detail: 'per-product _MOC hubs + _Home' },
    { title: 'Finalize', detail: 'regen indexes, refresh context.md, fact-token verify' },
  ],
}

const MEM = '/Users/ck/.claude/projects/-Users-ck/memory'
const SK = '/Users/ck/.claude/skills/obsidian/scripts'
const BK = '/Users/ck/.claude/vault-backups'

const STYLE = `WRITING STYLE (mandatory for every note you write):
- Short active sentences, one idea each. Present tense. Concrete values ("3-min window", not "a short window").
- One term per concept — no synonym variety in technical text.
- No filler (basically/simply/comprehensive/robust), no AI-slop tells (delve/testament/it's worth noting), no throat-clearing intros, no summary outros.`

const NOTE_FORMAT = `NOTE FORMAT (frontmatter v2 + visual conventions):
---
name: <kebab-slug, = filename>
title: "<Human Title>"
description: "<one clean line, <=150 chars>"
tags: [<domain>, project/<folder>, type/<kind>]
asserted: <today YYYY-MM-DD>
last_confirmed: <today>
source: user|inferred|research
confidence: high|med|low
status: active
supersedes: []
---
# <Human Title>
<emoji status chip line: 🟢 **active** / 🟡 **watch** / ⚫ **retired** / add 🔴 **real-money** where live money-flags apply>
<content; wrap KEY facts in callouts: > [!danger] real-money/destructive · > [!warning] gotcha · > [!tip] command/how-to · > [!info] status>
## Related
- [[_MOC-<folder>]]
- <2-4 sibling/related notes>`

const SPLIT_RULES = `SPLIT RULES:
- Every fact token in the parent (number, URL, UPPER_SNAKE flag, commit id, file path, date) must land VERBATIM in exactly one child. A set-based verifier diffs the backup afterward — one lost token fails the whole workflow.
- Children: <=4KB each, kebab-case filename, SAME folder as the parent, in the NOTE FORMAT below.
- Rewrite the PARENT as a <=1KB stub: keep its filename and name, set status: retired, description says "split into atomic notes", body = one line per child link. NEVER delete a file.
- Link every child to [[_MOC-<folder>]], the parent stub, and its closest sibling.`

// ---------------------------------------------------------------- Phase 1: backup
phase('Backup')
const bk = await agent(
  `Run exactly:
mkdir -p ${BK} && tar -czf ${BK}/restructure-pre-$(date +%Y%m%d-%H%M%S).tar.gz -C /Users/ck/.claude/projects/-Users-ck memory && ls -t ${BK}/restructure-pre-*.tar.gz | head -1
Return the backup path and the .md count inside it.`,
  { label: 'tar-backup', schema: { type: 'object', properties: { backup_path: { type: 'string' }, md_count: { type: 'number' } }, required: ['backup_path'] } },
)
if (!bk || !bk.backup_path) throw new Error('backup failed — aborting before any write')
log(`backup: ${bk.backup_path} (${bk.md_count} md files)`)

// ---------------------------------------------------------------- Phase 2: hygiene
phase('Hygiene')
await agent(
  `Vault hygiene for ${MEM}. Run these steps with bash, report what each did (counts). NOTHING here deletes knowledge — only caches, state, and a stale .bak.
1. mv ${MEM}/_infra/_backup-* ${BK}/ 2>/dev/null (the 45-note backup dir out of the searchable vault)
2. mv any ${MEM}/**/*.tar.gz files to ${BK}/
3. rm ${MEM}/MEMORY.md.bak (1 line behind MEMORY.md — verified stale)
4. rm -rf ${MEM}/.ruff_cache (python lint cache, regenerable, does not belong in a vault)
5. Rotate ${MEM}/_session-log.md: keep frontmatter + last 100 lines, archive the rest to ${MEM}/_system/session-log-archive-$(date +%Y%m%d).md
6. find ${MEM}/.recall-state -name '*.json' -mtime +30 -delete (per-session recall state, regenerable)
Return one line per step.`,
  { label: 'hygiene' },
)

// ---------------------------------------------------------------- Phase 3: splits (folder-partitioned, no shared files)
phase('Split')
const SPLITS = [
  ['_skills', `SPECIAL CASE — ${MEM}/_skills/anti-slop-law-FULL.md (85KB) is a verbatim mirror of the anti-slop-design-law skill, not memory. Do NOT split. Rewrite it as a <=1KB pointer stub: keep name, status: retired, description "mirror of the skill — read the skill file", body links to the real source ~/.claude/skills/anti-slop-design-law/references/slop-law.md and [[_MOC-skills]]. Fact tokens in it are exempt from the verifier ONLY because the skill file still holds them — say so in the stub.`],
  ['trade-stack', `Split ${MEM}/trade-stack/reflections.md (31KB append-log) by shipped unit — kite-control-bot, zerodha-placement-P0-incident, cred-custody-registry, per-account-execution, tg-notification-scale (adjust to actual content) — plus a thin trade-stack-timeline.md index of dated one-liners. Also split ${MEM}/trade-stack/phase-5.md (10KB) into its 2-3 natural sub-topics.`],
  ['whispr', `Split ${MEM}/whispr/whispr-build-plan.md (30KB, ~12 version sections) into: whispr-architecture.md (stable design), whispr-openwispr-rebrand.md (rename/TCC story), whispr-release-log.md (dated one-liner per version, thin), plus extra child notes if any single one would exceed 4KB.`],
  ['sbbi', `Four jobs in ${MEM}/sbbi/:
1. sbbi/ops/loop-engineering-spec.md (25KB, spec v2.1) — atomize into loop-stack, external-state-spine, agent-map, claims-schema, cost-failure-controls children (in sbbi/ops/).
2. sbbi/plans/loop-engineering-v1-narrative.md (26KB) — ~80% overlaps the spec. Facts unique to the narrative move into the spec children; then rewrite the narrative as a retired stub with supersedes pointing at the spec children.
3. sbbi/plans/channel-analysis-india.md (22KB) — split into format-teardown, india-thesis, content-strategy, research-brief-template (the template is reusable — surface it).
4. sbbi/plans/channel-setup.md (13KB), sbbi/plans/bangalore-cafe-restaurant-numbers.md (12KB), sbbi/research/source-spine-config.md (9KB) — split each at its natural seams.`],
  ['zerodha-tg-bot', `Split ${MEM}/zerodha-tg-bot/dhan-groww-mirror.md (25KB single Details blob) into: broker-adapter (Dhan/Groww specifics), mirror-logic (order copy semantics), mirror-gotchas (traps + fixes).`],
  ['ck-dot-com', `Three jobs in ${MEM}/ck-dot-com/:
1. reflections.md (20KB append-log) — split by shipped unit; the "subagent deployed live-money repo without authorization" incident becomes its own note (type/incident, 🔴 chip) — it is a safety precedent and currently unfindable.
2. mission-control-redesign.md (18KB) — split at natural seams.
3. redesign/three-worlds-buildoff.md (15KB) — split at natural seams (children stay in redesign/).`],
  ['drishti', `Split these ${MEM}/drishti/ notes at their natural seams (each child <=4KB): drishti-app-landing.md (20KB), drishti-winrate-workstream.md (19KB), drishti-signal-overhaul-r1-r5-plan.md (18KB), drishti-winrate-fable-briefing.md (14KB), drishti-wr-failures-ledger.md (14KB), drishti-twa-cursor-handover.md (12KB), posthog-paid-video-dashboard.md (8.5KB — split only if it has 2+ clear topics, else trim frontmatter/dead sections to get under 8KB). Winrate notes: keep the workstream/briefing/ledger separation but dedupe repeated background across them — shared background becomes one child all three link.`],
  ['tatkaal', `Split ${MEM}/tatkaal/drishti-pulse.md (14KB) into: the two-repo reality (ck-delta/drishti-pulse backend vs ck-delta/tatkaal web — keep this precise), the R2 publishing pipeline, and operational gotchas.`],
  ['stratzy', `Split ${MEM}/stratzy/stratzy-almanac.md (12KB) at its natural seams into <=4KB children.`],
]
const splitResults = await parallel(
  SPLITS.map(([folder, job]) => () =>
    agent(
      `<task>Split oversized memory notes in the ${folder} folder of ck's Obsidian vault into small atomic notes. Zero fact loss.</task>
<context>Vault: ${MEM}. Today: run \`date +%Y-%m-%d\` for frontmatter dates. Read each note fully before splitting.
${job}</context>
<rules>
${SPLIT_RULES}
${NOTE_FORMAT}
${STYLE}
</rules>
<output_format>One line per parent: "<parent>: N children — <child names>". Under 200 words total.</output_format>`,
      { label: `split:${folder}`, phase: 'Split' },
    ),
  ),
)
log(`splits done: ${splitResults.filter(Boolean).length}/${SPLITS.length} folder agents succeeded`)

// ---------------------------------------------------------------- Phase 4: merges
phase('Merge')
const merges = await parallel([
  () =>
    agent(
      `<task>Merge the six over-atomized drishti-seo shards at the ROOT of ck's vault into one note in drishti/.</task>
<context>Vault: ${MEM}. Files: drishti-seo-content-engine.md, drishti-seo-phase-a.md ... drishti-seo-phase-e.md (all at vault root, 1.2-2.7KB each — shards of ONE plan). Read all six.</context>
<rules>
- Create ${MEM}/drishti/drishti-seo-plan.md holding the full merged plan (if it exceeds 8KB, make drishti-seo-plan.md the hub and one child per phase group). Every fact token from all six moves in verbatim.
- Rewrite each original as a <=300-byte retired stub (status: retired, supersedes: [[drishti-seo-plan]], body = one pointer line) and MOVE the stubs into ${MEM}/drishti/ so the vault root stays clean. Never delete.
${NOTE_FORMAT}
${STYLE}
</rules>
<output_format>List created/rewritten files. Under 120 words.</output_format>`,
      { label: 'merge:drishti-seo', phase: 'Merge' },
    ),
  () =>
    agent(
      `<task>Consolidate ck's scattered obsidian-memory-system knowledge (17 notes) into one hub + three canonical notes + a dated changelog.</task>
<context>Vault: ${MEM}. Read these first:
_infra/: obsidian-memory-integration.md, obsidian-memory-research.md, memory-hook-upgrades-2026-07.md, memory-upgrades-2026-07-17.md, context-dump-system.md, vault-visual-conventions.md, second-brain-oss.md, second-brain-plugin.md, second-brain-handover.md, second-brain-marketing.md (13KB — oversized), second-brain-installer-app.md, session-2026-07-22-second-brain-launch.md
_playbook/obsidian-publish-workflow.md · sbbi/ops/obsidian-sync-workflow.md
Also true TODAY (2026-07-27 overhaul — include these facts): CLAUDE_MEMORY_DIR is set in settings.json env + launchd plist and every hook/script reads it; the canonical vault is ${MEM}; the obsidian skill is canonical, second-brain skill is OSS-export-only; capture-exchange uses a shared 1MB scan_transcript in _hooklib.py with a harness-noise filter, Daily dedupe, and Files/Commands/Errors sections in Sessions notes; context-monitor auto-runs context-dump.py at the fill threshold (re-arms at 1.3x) so compaction is a non-event; note size law = 4KB target / 8KB hard gate (health.py + memory-lint enforce); OBSIDIAN_AUTO_CONSOLIDATE=1 weekly; verify-facts.py does set-based fact verification.</context>
<rules>
- Create in _infra/: obsidian-memory-system.md (the hub: what the system is, mermaid graph of hooks->vault->recall loop, links to everything below), obsidian-memory-architecture.md (hooks, scripts, env var, data flow — canonical), obsidian-memory-changelog.md (dated one-liners distilled from the two upgrade notes + research note + today's overhaul).
- KEEP and enrich: vault-visual-conventions.md (conventions canon), _playbook/obsidian-publish-workflow.md (workflow canon). Retire sbbi/ops/obsidian-sync-workflow.md as a stub pointing at the _playbook note.
- Retire as stubs (status: retired, supersedes -> the new canonical note that absorbed their facts): obsidian-memory-integration, obsidian-memory-research, memory-hook-upgrades-2026-07, memory-upgrades-2026-07-17. context-dump-system.md: fold its facts into obsidian-memory-architecture and retire as stub.
- second-brain-* notes are about the OSS PRODUCT, not the memory system: keep them, but split second-brain-marketing.md (13KB) into <=4KB children and add a second-brain-oss hub line in obsidian-memory-system.md linking the cluster.
- Every fact token from every touched note must survive verbatim somewhere. Each new note <=4KB (hub may be up to 8KB).
${NOTE_FORMAT}
${STYLE}
</rules>
<output_format>List created/kept/retired files, one line each. Under 200 words.</output_format>`,
      { label: 'merge:obsidian-system', phase: 'Merge' },
    ),
])
if (merges.filter(Boolean).length < 2) log('WARNING: a merge agent failed — verify phase will catch any loss')

// ---------------------------------------------------------------- Phase 5: hubs
phase('Hubs')
const disc = await agent(
  `List the top-level note folders of ${MEM}: every directory except Daily, Weekly, Sessions, _system, dot-dirs and _backup*. Return JSON {"folders": [...]}.`,
  { label: 'discover-folders', phase: 'Hubs', schema: { type: 'object', properties: { folders: { type: 'array', items: { type: 'string' } } }, required: ['folders'] } },
)
const folders = (disc && disc.folders) || []
const groups = []
for (let i = 0; i < folders.length; i += 4) groups.push(folders.slice(i, i + 4))
await parallel(
  groups
    .map((g, gi) => () =>
      agent(
        `<task>Build or rebuild the _MOC hub note for each of these vault folders: ${g.join(', ')}.</task>
<context>Vault: ${MEM}. For each folder F, write ${MEM}/F/_MOC-F.md (note: hubs for _infra/_playbook/_skills are _MOC-infra/_MOC-playbook/_MOC-skills — no double underscore; check what existing notes link to via grep "_MOC-" and match THAT name). Read the folder's notes (names + descriptions) first.</context>
<rules>
- A hub is ONE ENTRY POINT to the product's whole knowledge: sections Architecture / Decisions / Incidents & gotchas / Release log / Plans (include a section only if the folder has such notes), each section = wikilinks + one-line hooks. A \`\`\`mermaid\`\`\` mini-graph of the 5-10 most connected notes at top.
- THIN: links + one-liners only, no body facts, <=4KB. Frontmatter v2, tags include type/moc. Link back to [[_Home]] and [[MEMORY]].
- Do not touch any non-_MOC file.
${STYLE}
</rules>
<output_format>One line per hub written. Under 100 words.</output_format>`,
        { label: `hubs:${gi + 1}/${groups.length}`, phase: 'Hubs' },
      ),
    )
    .concat([
      () =>
        agent(
          `Rebuild ${MEM}/_Home.md as the vault's front door: keep name _Home; H1 "# 🏠 Home — Second Brain"; a \`\`\`mermaid\`\`\` domain map (Signals/Delta/Personal/Tooling/Meta); Entry points section ([[MEMORY]], Daily/, [[obsidian-memory-system]]); a Maps of Content section linking EVERY _MOC-* hub that exists after this run (glob for them). Thin, <=3KB. ${STYLE}`,
          { label: 'hubs:_Home', phase: 'Hubs' },
        ),
    ]),
)

// ---------------------------------------------------------------- Phase 6: finalize + verify
phase('Finalize')
await agent(
  `Run exactly, report each command's last output line:
cd ${SK} && python3 regen-index.py --write && python3 build-system-index.py`,
  { label: 'regen-indexes', phase: 'Finalize' },
)
await agent(
  `<task>Rewrite ${MEM}/context.md — the "orient any new LLM" file loaded at SessionStart. It is 47 days stale (June 2026 expiry math, pre-rebrand naming).</task>
<context>Sources of truth to read: ${MEM}/MEMORY.md, the _MOC-* hubs, _infra/obsidian-memory-system.md, ~/.claude/CLAUDE.md (projects + access section). Today: run date.</context>
<rules>
- Content: who ck is, the active projects one paragraph each (drishti, tatkaal two-repo reality, lakshay, whispr/OpenWispr, sbbi, delta work), where memory lives and how to use it (recall/capture footer/obsidian skill), current infra gotchas — sourced from the hubs, not invented.
- Add frontmatter v2 (name: context, status: active, asserted today). <=8KB. Wikilink to hubs instead of duplicating their content.
${STYLE}
</rules>
<output_format>Confirm size and sections. Under 80 words.</output_format>`,
  { label: 'context-refresh', phase: 'Finalize' },
)
const verify = await agent(
  `Run exactly:
python3 ${SK}/verify-facts.py ${bk.backup_path}
python3 ${SK}/health.py | sed -n '1,3p;/oversized/,+3p;/broken wikilinks/p'
EXCEPTION: tokens missing ONLY because they lived in _skills/anti-slop-law-FULL.md (now a pointer stub to the anti-slop-design-law skill file) are acceptable — check the skill file still holds them. Everything else missing = FAIL.
Return JSON: {"missing": <count of unacceptable missing tokens>, "notes": <health note count>, "oversized": <count>, "broken_links": <count>, "detail": "<one line>"}.`,
  { label: 'verify-facts', phase: 'Finalize', schema: { type: 'object', properties: { missing: { type: 'number' }, notes: { type: 'number' }, oversized: { type: 'number' }, broken_links: { type: 'number' }, detail: { type: 'string' } }, required: ['missing'] } },
)
log(`verify: missing=${verify ? verify.missing : '?'} oversized=${verify ? verify.oversized : '?'} broken=${verify ? verify.broken_links : '?'}`)
return { backup: bk.backup_path, verify, splits: splitResults.filter(Boolean).length }
