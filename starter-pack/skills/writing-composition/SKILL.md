---
name: writing-composition
description: Document-level writing craft — the layer above sentence polish. How to open (lede/hook), structure an argument, write headlines and section headings, order ideas, and size a piece to its job. Use when writing anything longer than a paragraph — READMEs, blog posts, marketing pages, reports, docs, explainers, release notes, essays — or when a draft "reads flat / has no flow / buries the point". The clarity + anti-slop skills fix sentences; this fixes the whole piece.
---

# Writing composition

the writing stack is otherwise all sentence-janitor (clarity + anti-slop). This is the missing layer: the shape of the whole piece. A document with perfect sentences and no structure still fails.

## 1. Open with the point, not a windup
- **Lede first.** State the most interesting/important thing in the first sentence. Never open with a definition, a dictionary quote, "In this post we will…", or a history lesson.
- **Hook by relevance,** not cleverness: the reader's problem, a surprising result, a concrete stake.
- **BLUF for docs** (Bottom Line Up Front): what this is + who it's for + what they can do, in the first two lines.

## 2. Structure the argument
- **One controlling idea** per piece. If you can't state it in a sentence, the piece isn't ready.
- **Order for the reader, not the author.** Most readers want conclusion → reasons → detail (inverted pyramid), not your chronological discovery.
- **One idea per section.** A heading is a promise; the section keeps it.
- **Transitions carry logic** — each section should answer the question the previous one raised.

## 3. Headlines & headings
- Headings are **scannable and specific** — a reader skimming only headings should get the gist. "Why funding flips matter" beats "Overview".
- Front-load keywords; no cute headings that hide content.
- Sentence case, parallel grammar across siblings.

## 4. Flow & rhythm at the paragraph level
- One paragraph = one idea. Topic sentence first.
- Vary paragraph length; a one-line paragraph lands a point.
- Progressive disclosure: simple/important first, edge cases and depth later or behind a fold.

## 5. Length = the job
- Cut anything that doesn't serve the controlling idea. Length is not value.
- Microcopy: ruthless. Docs: complete but no padding. Marketing: shortest path to the one action. Editorial: as long as it earns.

## Fit
Run FIRST when drafting a document (shape it), then the clarity + anti-slop axes (see `writing-router`) tighten the sentences, then `writing-eval` grades it (its "structure" criterion checks this layer). Pairs with `ux-copy` for interface text and `editorial-report-design` for long-form layout.
