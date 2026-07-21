export const meta = {
  name: 'vault-enrich',
  description: 'Enrich every Obsidian memory note to the visual format (H1 title, emoji status chip, colored callouts, headers, dense links) preserving all facts, rebuild MOC hubs + _Home as Mermaid dashboards, and verify no fact was dropped. Self-discovering — no args needed.',
  whenToUse: 'Re-apply the vault visual format after adding notes, or to reformat the whole memory vault. Spec: [[vault-visual-conventions]]. Backs up first; folder-partitioned fan-out; deterministic fact-token verify vs backup.',
  phases: [
    { title: 'Discover' },
    { title: 'Polish' },
    { title: 'Hubs' },
    { title: 'Verify' },
  ],
}

// Shell-expandable token: every use lands inside a bash command the agent runs.
const MEM = '${CLAUDE_MEMORY_DIR:-$HOME/.claude/second-brain-vault}'

// --- Phase 0: discover folders + notes (agent runs bash; script chunks) ---
phase('Discover')
const inv = await agent(
  `Run bash and return the memory-vault note inventory. First back up the vault:
\`BK="/tmp/vault-enrich-backup-$(ls /tmp | wc -l).tar.gz"; tar -czf "$BK" -C "$(dirname "${MEM}")" "$(basename "${MEM}")" && echo "backup:$BK"\`.
Then for every folder under ${MEM}/ EXCEPT Daily, Weekly, _system: list its non-underscore *.md files (absolute paths).
Return the backup path and one entry per folder that has >=1 note.`,
  { label: 'discover', phase: 'Discover', schema: {
    type: 'object', additionalProperties: false,
    required: ['backup', 'folders'],
    properties: {
      backup: { type: 'string' },
      folders: { type: 'array', items: {
        type: 'object', additionalProperties: false, required: ['name', 'files'],
        properties: { name: { type: 'string' }, files: { type: 'array', items: { type: 'string' } } },
      } },
    },
  } }
)
const folderList = (inv?.folders || []).filter(f => f.files?.length)
log(`Backup: ${inv?.backup}. ${folderList.length} folders, ${folderList.reduce((n, f) => n + f.files.length, 0)} notes.`)

// chunk big folders (<=12/agent), combine tiny (<=2) into one batch — no two agents share a file
const batches = []
const tiny = []
for (const f of folderList) {
  if (f.files.length >= 13) for (let i = 0; i < f.files.length; i += 12) batches.push({ label: `${f.name}-${i / 12 + 1}`, files: f.files.slice(i, i + 12) })
  else if (f.files.length <= 2) tiny.push(...f.files)
  else batches.push({ label: f.name, files: f.files })
}
if (tiny.length) batches.push({ label: 'misc-small', files: tiny })

const NOTE_SPEC = `For EACH file (edit in place): keep frontmatter + the 'name:' slug byte-for-byte; add 'title:'; fix
'description' to one clean <=150-char untruncated line; unescape any \\". Body: '# <Human Title>' H1, then an emoji
status chip ('🟢 **active**' / '🟡 **watch**' / '⚫ **retired**' / add '🔴 **real-money**' for live-order/spend/key
notes). Wrap KEY existing sentences (verbatim) in callouts: '> [!danger]' real-money/destructive/kill-switch,
'> [!warning]' gotchas/traps, '> [!tip]' commands/how-to, '> [!info]' current status. Normalise headers to
## Status / ## Details / ## Related; tables only where they aid scanning. '## Related' links [[_MOC-<parent folder>]]
+ 2-4 related notes seen in the text.
HARD INVARIANT — NO FACT MAY BE LOST: every number, %, URL, UPPER_SNAKE flag, commit hash, path, date, and factual
sentence in the ORIGINAL must appear VERBATIM. Only ADD (title/callouts/headers/links) + reorder into sections;
NEVER delete, summarise, paraphrase, or reword. When unsure, keep the original text.`

// --- Phase 1: polish (folder-partitioned parallel) ---
phase('Polish')
const polished = await parallel(batches.map(b => () =>
  agent(`Enrich these ${b.files.length} Obsidian notes (batch "${b.label}") to the vault visual format, preserving every fact.
FILES:\n${b.files.join('\n')}\n\n${NOTE_SPEC}\n\nReturn under 200 words: one line per file + "FACTS-PRESERVED: yes".`,
    { label: `polish:${b.label}`, phase: 'Polish' })))

// --- Phase 2: hubs + _Home ---
phase('Hubs')
const hubs = await parallel([
  ...folderList.map(f => () =>
    agent(`Build/rebuild ${MEM}/${f.name}/_MOC-${f.name}.md as a visual dashboard (create if missing): frontmatter
(name:_MOC-${f.name}, title, description, tags with type/moc, status:active); '# ${f.name} — Map of Content' H1; a
\`\`\`mermaid graph TD of the folder's notes as nodes + their [[links]] as edges (read the notes for real edges);
a status legend; '## Notes' with '- [[slug]] — hook <status emoji>' per note; '## Related MOCs' → [[_Home]] + siblings.
Only edit the _MOC file. Under 100 words.`, { label: `hub:${f.name}`, phase: 'Hubs' })),
  () => agent(`Rebuild ${MEM}/_Home.md as a dashboard: keep name:_Home; '# Home — Second Brain' H1; a \`\`\`mermaid domain
map grouping the MOC hubs by their domain tag; a '> [!info]' active-workstreams callout; a
'## Maps of Content' section linking every [[_MOC-*]] by domain; link [[MEMORY]] + [[context]]. Add, don't delete. Under 100 words.`,
    { label: 'hub:_Home', phase: 'Hubs' }),
])

// --- Phase 3: deterministic-style verify (agent runs the fact-token diff vs backup) ---
phase('Verify')
const verify = await agent(
  `Verify no facts were lost. Extract ${inv?.backup} to a temp dir. For EVERY */*.md note (exclude _*), compare the
backup's body vs the current ${MEM} body: extract fact-tokens (regex: URLs, numbers with %/$, [A-Z][A-Z0-9_]{3,},
7-40 hex commit hashes, *.py/json/ts/js/sh paths, vNN) from each and report any note where a token in the backup is
MISSING from the current version. Also: run ~/.claude/skills/second-brain/scripts/regen-index.py --write, then
~/.claude/skills/second-brain/scripts/health.py; report MEMORY.md size + real broken-link count (excluding
[[_MOC-*]]/[[_Home]] false-positives) + orphans.`,
  { label: 'verify:facts+health', phase: 'Verify' })

return { notes: batches.reduce((n, b) => n + b.files.length, 0), polished: polished.filter(Boolean).length, hubs: hubs.filter(Boolean).length, backup: inv?.backup, verify }
