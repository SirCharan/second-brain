---
name: how-memory-works
title: "How this memory system works"
description: "The capture → recall → consolidate loop, which hook does what, and the one environment variable that controls the vault path."
tags: [meta, project/_infra, type/reference]
asserted: 2026-01-01
last_confirmed: 2026-01-01
source: user
confidence: high
status: active
supersedes: []
metadata:
  type: reference
---

# How this memory system works

🟢 **active** · shipped with the starter vault. Keep it; recall returns it when you ask how the system behaves.

> [!danger] One variable controls where notes go
> `CLAUDE_MEMORY_DIR` sets the vault path (default `~/.claude/second-brain-vault`). Every hook and script reads it. If it is unset in one place and set in another, captures go to two different vaults and one of them looks frozen.
> Check with: `python3 ~/.claude/skills/second-brain/scripts/doctor.py`

## The loop

| When | Hook | What happens |
|---|---|---|
| Session starts | `session-memory`, `session-resume` | Loads the last-session digest, recent captures, and this vault's index |
| You send a prompt | `memory-recall` | Injects the notes matching your prompt, plus a one-line stats banner |
| You send a prompt | `context-monitor` | Past a fill threshold, writes a resume digest so `/clear` is always safe |
| A reply finishes | `capture-exchange` | Appends a line to `Daily/`, updates the session note, records files and commands |
| You edit a note | `memory-lint` | Warns about missing frontmatter, broken links, or an oversized note |
| Before compaction | `precompact-carryover` | Snapshots the active task, files touched, and unresolved errors |

## Two layers, and why both exist

The **journal** (`Daily/`, `Sessions/`) is automatic and complete. It records everything, which also means it is noisy.

**Curated notes** are the durable layer: one concept each, written deliberately, linked into a hub. Recall ranks these, not the journal. A fact only becomes reliably retrievable once it lives in a curated note.

> [!tip] Turning journal into knowledge
> `/second-brain consolidate` reads recent journal entries and distills them into curated notes. Nothing runs it for you: no scheduled job ships with this. The session-start hook counts your curation backlog and tells you when it has built up, and `_infra/_promote-queue.md` lists every research finding still waiting for a note.

> [!warning] Skip it for long enough and recall goes quiet
> `Daily/` and `Sessions/` grow forever and recall deliberately ignores both — it ranks curated notes only. A vault that is never consolidated keeps capturing perfectly and retrieves nothing, while still reporting a healthy note count.

## Opening this in Obsidian

Two ways, and they differ in one way that matters:

- **Open this folder as its own vault.** Obsidian reads the `.obsidian/` directory inside it. If you installed the starter pack, that directory already holds graph colour groups per folder, a dark theme, and the `_templates` folder wiring.
- **Symlink this folder inside an existing vault** by setting `SECOND_BRAIN_OBSIDIAN_LINK` to the target path, then running `doctor.py --fix` to create and maintain the link. Obsidian then uses the *parent* vault's configuration, and the `.obsidian/` directory here is ignored.

> [!info] No plugins, either way
> The graph, backlinks, search, tags and templates are all core Obsidian features. Nothing here needs a community plugin, and no plugin runs as part of the memory loop.

## Keep notes small

> [!warning] 4 KB target, 8 KB hard limit
> Recall injects several notes per prompt. A 10 KB note is roughly 2,500 tokens, so a handful of them crowds out the conversation and blurs the embedding that makes the note findable.
> Split at the seams and link the pieces. Never grow one note forever.

## Related
- [[_Home]]
- [[note-conventions]] — the exact shape a note takes
- [[MEMORY]]
