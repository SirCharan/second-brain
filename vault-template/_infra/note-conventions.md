---
name: note-conventions
title: "Note conventions — the shape every note takes"
description: "Frontmatter fields, the visual body format, status chips, callout types, and the rules for superseding a fact instead of deleting it."
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

# Note conventions — the shape every note takes

🟢 **active** · shipped with the starter vault. Ask "how do I write a note" and recall returns this.

## Frontmatter

```yaml
name: kebab-slug          # must match the filename; links resolve on it, so never rename casually
title: "Human Title"
description: "One line, under 150 characters. This is what recall shows in search results."
tags: [domain, project/<folder>, type/<kind>]
asserted: YYYY-MM-DD      # when the fact was first recorded
last_confirmed: YYYY-MM-DD # bump when you re-verify it; recall favours fresh notes
source: user | inferred | research
confidence: high | med | low
status: active | watch | retired
supersedes: []            # name the older note here when this replaces an earlier claim
```

`description` earns the most attention. Recall matches against it and shows it in results, so a vague description makes a good note unfindable.

## Body

1. `# Human Title` as the first line.
2. A status chip: 🟢 **active** · 🟡 **watch** · ⚫ **retired**. Add 🔴 **real-money** when the note covers live spend, orders, or credentials.
3. Content, with the important facts wrapped in callouts.
4. `## Related`, linking the folder's `_MOC-` hub and two to four sibling notes.

> [!danger] Irreversible, costly, or destructive
> Deleting data, spending money, placing an order, touching production.

> [!warning] A trap that has already bitten someone
> The thing that looks correct and is not.

> [!tip] A command or procedure worth copying
> Exact invocations belong here, not in prose.

> [!info] Current state, as of a date
> Status that will age. Date it so a reader knows when to distrust it.

## Rules

> [!warning] Enrich, never rewrite
> Preserve every number, URL, flag, path, and commit hash verbatim. Add structure and links; do not paraphrase a fact into vagueness.

When a fact changes, the newest wins. Set the old note's `status: retired` and point `supersedes` at the replacement. Nothing gets deleted, so the history stays auditable.

One concept per note. If a note covers three things, three notes linked from a hub retrieve better than one that covers everything.

## Related
- [[_Home]]
- [[how-memory-works]] — the hooks and the loop
- [[welcome]] — a worked example of this format
