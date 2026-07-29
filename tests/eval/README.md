# Recall eval

Retrieval was unmeasured. Recall ranked notes by keyword score and nobody could say
whether a change helped, hurt, or did nothing — so scoring decisions were guesses, and a
regression would have shipped silently.

This measures it. Two scripts, stdlib only, no vault of ours required.

## Run it

```bash
export CLAUDE_MEMORY_DIR=~/.claude/second-brain-vault      # your vault
python3 tests/eval/build_set.py -o ~/.second-brain/eval/queries.jsonl
python3 tests/eval/run_eval.py  ~/.second-brain/eval/queries.jsonl \
        --save ~/.second-brain/eval/baseline.json
```

Then before and after any ranking change:

```bash
python3 tests/eval/run_eval.py ~/.second-brain/eval/queries.jsonl \
        --compare ~/.second-brain/eval/baseline.json --gate
```

`--gate` exits non-zero when hit@k drops, so it works in a pre-commit hook or CI.

## Where the labels come from

Nobody hand-labels anything. Every capture footer already records what a session did and
which notes it was about:

```
- **17:31** [widgets] — (decision) Shipped the cache rewrite || tags: ... || links: [[widgets-cache]]
```

The summary becomes the query, the `links:` become ground truth. That gives a labelled set
with two properties a synthetic one would not have: the query is real user prose, and it
was written at a different time and in different words from the note it points at. Using a
note's own description as the query would instead guarantee a head match and score ~1.0
while proving nothing.

Paraphrase-to-note is also the case recall has to serve — a prompt about a topic should
surface that topic's note.

Lines are skipped when they carry no `links:`, when they are `(raw)` or image fallbacks,
when the summary has fewer than three content words (recall stays silent below that, so
scoring them would flatter the result), and when every linked note is a meta file the
ranker excludes by design. Duplicate summaries are deduped.

## Reading the numbers

`hit@4` is the one that matters: recall injects four notes per prompt, so it is the share
of prompts where the note you were actually working on reached the context window. `hit@1`
is how often it led. `MRR` rewards ranking the right note higher.

**Baseline, measured 2026-07-29** — 212 mined queries against a 489-note vault, shipped
scoring:

| | hit@1 | hit@4 | MRR |
|---|---|---|---|
| keyword scoring as shipped | 0.264 | **0.472** | 0.342 |

It returned *nothing* on only 0.9% of queries, so the failure mode is not silence — it
returns the wrong notes.

Three follow-up measurements, same set, worth knowing before tuning anything:

- **The head gate is not the bottleneck.** Dropping it (`--head-gate 0`) moves hit@4 to
  0.491, about two points.
- **The project bias does not help.** 0.476 without it, 0.472 with. Roughly one query —
  call it neutral, not a win.
- **The ceiling is candidate generation, not the cut.** At k=20 hit is only 0.590, so for
  41% of queries the right note is absent from the top 20 entirely. No reranking of that
  list can recover them, because the note never enters it.

What does recover them is the link graph: expanding one hop from the top 4 puts the
expected note in the candidate pool for **90.1%** of queries, recovering 91 of 112 misses.
A cheap no-LLM version of that (neighbours inherit `parent_score * 0.9`, plus their own
ungated keyword score) reaches **0.599** hit@4. Closing the rest of the gap to 0.901 needs
a rerank stage that can judge relevance, because inherited score is a weak proxy.

Re-measure on your own vault before trusting any of those numbers — they describe one
vault's link density and note conventions.

## The output is yours

`build_set.py` writes your own prose, mined from your journal. It is git-ignored on
purpose. Commit the miner, never a mined set — especially to a public repo.
