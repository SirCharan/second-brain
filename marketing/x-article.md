# X Article — second-brain

**Title (X Article field):** Claude Started Writing My Obsidian Vault Without Me Asking

**Subtitle / preview:** At 20% context it dumps the task, I /clear, and a lesson from one repo fires in another. 1,099 notes. ~$3,400/month I stopped paying to re-send a fat window.

**Cover:** `shots/01-graph-hero.png`

Publish on X, then quote-tweet with the short blurb in `twitter-thread.md`. Vault counts: 2026-08-14. Dump math: live harness (`SECOND_BRAIN_DUMP_PCT=20`, 1M window).

---

I never typed "make a note."

I never ran "ingest this."
I just worked.

A Stop hook wrote every reply into `Daily/` as a one-line Markdown capture. A SessionStart hook opened the next chat already knowing where I left off. A UserPromptSubmit hook pulled only the notes that matched *this* prompt. Not the whole vault. Not the whole transcript.

At 20% of a 1M context window a fourth hook dumped the live task into the vault. I hit `/clear`. The chat went back to zero. The memory did not.

On 6 July 2026 the vault had one daily note. On 14 August it had 1,099 Markdown files, 6,777 `[[wikilinks]]`, and 1,089 of those files already wired to something else. I did not sit down and "build a second brain." I shipped other projects. The graph is what that looks like when you open it in Obsidian.

Full context of my work, in files I own. Claude is 10x sharper on that work because the context survived the `/clear`.

## Project A teaches project B

Vendor memory is locked to one project, or dumped into one blob with no links.

Mine is one graph across 50 repos.

A CLS fix I shipped on a landing page was already a note when a different site started shifting. A Vercel staging gotcha from project A was sitting there when project B hit the same wall. A DuckDB single-writer collision from a signals repo showed up the first time an unrelated dashboard tried the same pattern. Quality gates I wired for one product now load when I open another.

I did not search for them. Claude pulled them because the vault is one graph across every repo I touch.

That is the whole product. Skills compound across projects. Dead chats do not.

Claude Projects keep memory inside a project. ChatGPT keeps one undifferentiated blob. Neither grows a linked graph across the things you build. Close the tab and the model forgets the retry param, the deploy gotcha, the decision you already paid for.

I stopped re-explaining my own work.

## The 20% dump: $3.93 a turn, ~$3,400 a month

Long context rots. Anthropic's own engineering post says it: as the token count climbs, recall from that context gets worse. `/compact` is the slow, lossy pause that summarizes your history away so the window can keep going. You sit through it, then you pay again to re-send what survived.

I stopped using it.

On this machine the monitor fires at **20% of a 1,000,000-token window = 200,000 tokens**. It writes `_infra/_carryover.md` (active task, files, commands, errors). I `/clear`. The next session injects the carryover first. The window is thin. The vault kept the thread.

`/clear` is free. `/compact` re-reads the whole window at full price.

**The model (Opus input, $5 per million tokens):**

| | Tokens re-sent each turn | Cost / turn |
|---|---|---|
| Session sitting at 80% | 800,000 | $4.00 |
| After dump + `/clear` | ~13,000 (harness + recall) | $0.07 |
| **Saved** | **787,000** | **$3.93** |

40 turns a day × 22 workdays × $3.93 = **$3,458 a month** I was burning to remember badly.

Assumptions, so you can rerun it: Opus input $5/MTok, 1M window, dump at 20%, compare against sitting at 80%, 40 turns/day, 22 days. If you sit at 90% instead, the gap is $4.44 a turn / **$3,907 a month**. This is a model, not a metered invoice. The conservative on-disk estimate in `savings.json` is smaller because it only counts what the hooks can prove.

Stuffing everything into the window does not scale. You want the smallest set of high-signal tokens, stored somewhere that outlives the chat. A folder of Markdown on your disk is that somewhere.

## The harness is the 10x

Before I typed a word, Claude was already burning **43,000 tokens** of plugins, skill descriptions, and session junk.

I cut that to **13,000**.

- 85 skill folders → 23
- `CLAUDE.md` 35 KB → 11 KB
- Plan mode by default
- Sonnet builds. Haiku does the noisy work
- Dump at 20%, `/clear`, resume from the vault

Then the vault started filling itself.

Every project I finish makes the next one cheaper. Claude is 10x smarter on my work because it finally has my context, in files that survive when I close the tab.

The product that does the capture is **second-brain**. Apache-2.0. Local. A folder of plain text, a handful of Python hooks, a `/second-brain` skill, and an MCP server so Cursor and Claude Desktop read the same disk. No account. No database. Nothing runs inside Obsidian at runtime.

If the tool vanished tomorrow, the notes would still be there.

## Pinpoint

- Writes the note without being asked
- Recalls it in an unrelated repo when the same class of problem shows up
- Dumps at 20% fill. `/clear` is free. `/compact` is the expensive one
- Secrets get scrubbed before they touch disk
- Contradictions get retired, not deleted. Git still sees the fight
- One export file feeds ChatGPT, Gemini, Grok. The brain does not move
- Uninstall the tool tomorrow. The folder stays

Storage remembers. This one works.

## What 39 days actually produced

These are not vibe numbers. They are `find` and a wikilink scrape of the vault this article is about.

| | |
|---|---|
| First daily note | 2026-07-06 |
| Notes | 1,099 |
| `[[wikilinks]]` | 6,777 |
| Notes with at least one link | 1,089 (99%) |
| Session notes | 188 |
| Daily journals | 36 |
| Project routes | 50 |
| Sessions since July 6 | 1,060 |
| Dump trigger | 20% of 1M = 200k tokens |
| Harness overhead | 43k → 13k tokens before I type |
| Saved vs sitting at 80% | $3.93/turn · ~$3,400/month |

The folders are the work: signals products, a personal site, trading tooling, infra gotchas, a playbook, a skill index. One graph.

## How it fills itself

The viral setup is: dump files into `/inbox`, tell the agent to ingest, go to sleep, wake up to a denser graph. That works. It is also a chore you will skip.

This inverts it. The inbox is the work you were going to do anyway.

```
Each session start  →  inject where you left off + the notes that match
Each prompt         →  recall (older unused notes rank down), only what belongs in this turn
Each reply          →  journal a one-line capture into Daily/
At 20% fill         →  dump the live task, then /clear
Before compaction   →  snapshot the live task / files / errors
On demand           →  /second-brain capture · consolidate · reconcile · …
```

`Daily/` is the firehose. Curated atomic notes are the distilled memory. `/second-brain consolidate` turns the former into the latter. Nothing is auto-deleted. A stale fact is retired with `status: retired` and a `supersedes` pointer, so the whole vault is git-auditable.

## The vault that argues

Storage remembers. Linking surfaces. Almost nobody builds the layer that disagrees with you.

`/second-brain reconcile` walks the vault for contradictions on the same topic. Newest confirmed fact wins. The loser is not deleted. It is retired and pointed at the winner. `/second-brain dedup` finds near-duplicate titles first. `/second-brain stale` lists active notes nobody has confirmed in N days.

It hunts contradictions, not agreement. Both parts came from you.

## The stack

Obsidian's CEO (kepano) released official agent skills so an agent can search a vault, write proper wikilinks and callouts, touch Bases and Canvas, and stop treating Obsidian like generic Markdown. That is the format layer.

Karpathy's LLM-wiki pattern is the architecture: drop raw material, let an agent extract entities, write pages, link, kill duplicates. That is the compounding layer.

second-brain is the capture layer those posts assume you will maintain by hand. Hooks do it. The vault is already Obsidian-compatible, so kepano's skills and any other agent that can read a folder can operate the same files.

Claude Code is the native home (hooks + skill + plugin). Cursor and Claude Desktop attach through a local stdio MCP server. `/second-brain export` flattens the vault into one portable file you can hand to ChatGPT, Gemini, or Grok. The brain does not move when the chat does.

Windows, macOS, and Linux each get a real install in CI. The core is stdlib Python. Semantic recall is the one optional extra; without it, keyword recall still works.

## Install

One line:

```bash
curl -fsSL https://charandeepkapoor.com/second-brain/install.sh | bash
```

Windows:

```powershell
irm https://charandeepkapoor.com/second-brain/install.ps1 | iex
```

That copies hooks, skill, workflow, and MCP into `~/.claude/`, creates a vault from `vault-template/`, registers the hooks, then runs a short wizard: find your git repos, write routing, offer Claude Desktop + Cursor, live-capture test.

Prefer clicking: [Second-Brain-Setup.dmg](https://github.com/SirCharan/second-brain/releases/latest/download/Second-Brain-Setup.dmg). Unsigned — right-click → Open the first time.

Prefer the plugin:

```
/plugin marketplace add SirCharan/second-brain
/plugin install second-brain
```

Pick one path. Running both registers every hook twice.

A fresh vault has about six nodes, which is why the graph looks dead on day one. The wizard offers a starter pack (`core`, `writing`, `design`). Core Obsidian features only. Nothing already on disk is overwritten.

Walkthrough: [charandeepkapoor.com/second-brain/get-started](https://charandeepkapoor.com/second-brain/get-started)

## The skill, in one table

| Command | What it does |
|---|---|
| `capture` / `learn` | Write or update one atomic note, re-index |
| `consolidate` | Distill `Daily/` + the promote-queue into curated notes |
| `reconcile` | Contradictions → supersede / retire |
| `link` | Insert missing `[[wikilinks]]` on orphans |
| `review` | Weekly rollup into today's Daily |
| `health` | Counts, missing fields, broken links, orphans, stale |
| `find` / `pull` | Ranked titles, or full-text when you are stuck |
| `prune` | Propose archive/merge. Never auto-apply |
| `export` | One portable file for any model |
| `graph` | Mermaid link-graph of the vault |
| `stale` | Active notes not confirmed in N days |
| `dump` | Resume digest before `/clear` |
| `doctor [--fix]` | Self-test the install |
| `embed-setup` | Optional semantic recall |

Notes stay small on purpose (4 KB target, 8 KB hard). Recall injects several per prompt; a novel-length note crowds the window and blurs itself.

## Honest comparison

Local, file-based, cross-model, no account, hands-free capture. Most tools manage one of those.

| | second-brain | ChatGPT memory | Claude memory | mem0 | Basic Memory |
|---|---|---|---|---|---|
| Stored | your disk | OpenAI cloud | Anthropic cloud | DB / cloud | your disk |
| You own & export | yes | no | limited | if self-hosted | yes |
| Across models | yes | no | no | yes | yes |
| Auto-captures sessions | yes | auto, in-app | auto, in-app | no | no |
| No account, no server | yes | no | no | no | yes |

Basic Memory and Pieces are real peers. Basic Memory is ahead on semantic search and phone sync. Pieces is ahead on OS-level capture. Native vendor memories win on ubiquity. They are on by default for hundreds of millions of people. second-brain asks you to install something. That is the trade: effort for control.

Where this one does not win: retrieval is keyword ranking plus grep, with older unused notes ranked down, unless you opt into embeddings. If you need agentic multi-hop over a database today, use a database. Grep plus Markdown is deliberately boring.

## What I do in the morning now

I do not open a textbook of my own notes.

I open the graph, or I start a chat. The chat already has where I left off. If I `/clear`, the next session reloads from the vault instead of from a compacted transcript. If I am stuck, `/second-brain pull` returns the actual paragraph, not a title.

Some mornings there is a node I do not recognize. That is the point. The system kept growing in the background while I was in a different repo.

Tuition for a second brain used to be willpower. This one cost an afternoon of wiring hooks, then it cost nothing, because the capture is the work.

Own your mind. Rent the model.

---

Repo: [github.com/SirCharan/second-brain](https://github.com/SirCharan/second-brain)
Site: [charandeepkapoor.com/second-brain](https://charandeepkapoor.com/second-brain)
Positioning (the argument, including where we lose): [POSITIONING.md](https://github.com/SirCharan/second-brain/blob/main/POSITIONING.md)

Obsidian skills (kepano): [github.com/kepano/obsidian-skills](https://github.com/kepano/obsidian-skills)
