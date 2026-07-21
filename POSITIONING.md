# Why second-brain exists — positioning & impact

> A deep look at the problem, who it's for, the strongest value props, an honest competitive map,
> and where we *don't* win. Written to be argued with, not to hype.

## 1. The problem: your AI memory is rented, siloed, and forgetful

Three things are true about AI memory in 2026, and all three are bad for you:

- **It's locked to one vendor.** ChatGPT's memory only works in ChatGPT — and it isn't even
  included in OpenAI's data export, so there's no clean way to take it with you. Claude's memory
  lives on Anthropic's servers and works only inside Claude. Gemini ties memory to your Google
  account and lets you *import in* but never export out. The tell: Anthropic shipped a "memory
  import" flow whose whole job is to *pull your memories out of ChatGPT* — the majors treat memory
  as a **moat**, not as your property. ([portable-ai-memory.org](https://portable-ai-memory.org/blog/ai-memory-portability-problem/),
  [mlq.ai](https://mlq.ai/news/anthropic-launches-prompt-to-extract-user-memories-from-chatgpt/))
- **Every session starts from zero.** Close the tab and the model forgets who you are, what you're
  building, and every decision you made together. People are visibly tired of it — recurring
  Hacker News threads ask how to "stop LLMs from resetting" and give models "long-term memory."
  ([HN](https://news.ycombinator.com/item?id=46252809))
- **Long context rots.** Anthropic's own engineering team puts it plainly: context "must be treated
  as a finite resource with diminishing marginal returns," and *"as the number of tokens in the
  context window increases, the model's ability to accurately recall information from that context
  decreases"* — this is **context rot**. Stuffing everything into the window doesn't scale; you
  need the *smallest* set of high-signal tokens.
  ([Anthropic — effective context engineering](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents))

**second-brain's answer:** keep your memory as plain Markdown files *on your own disk*, feed only
the relevant slice into each session, and let any assistant read and write it. You own it, it
persists, and it never overflows the window.

## 2. Who this impacts

Ranked by fit. Population figures are third-party estimates (vendors rarely publish official MAU);
treat them as directional.

| # | Segment | Size / signal | Why they care |
|---|---------|---------------|---------------|
| 1 | **AI-coding power users** (Claude Code, Cursor, MCP builders) | Claude Code ~4.2M weekly devs; Cursor ~7M MAU; MCP ecosystem in the thousands of servers / millions of SDK pulls | Native to their workflow (hooks, install-anywhere). They hit context loss *every session* and already live in the plugin/MCP distribution channel. This is the wedge. |
| 2 | **PKM / "second brain" crowd** (Obsidian-first) | Obsidian ~1.5M MAU, 5M+ downloads, 2,000+ plugins; *Building a Second Brain* / Zettelkasten movement | They already own a Markdown vault. Auto-capturing AI sessions into it is the feature they'd otherwise hand-build — zero switching cost. |
| 3 | **Local-first / digital-sovereignty** | Local-First Conf, localfirst.fm — small but high-conviction, high word-of-mouth | "Local, no cloud, you own it" is literally their manifesto ([Ink & Switch](https://www.inkandswitch.com/essay/local-first/)). |
| 4 | **Privacy-constrained pros** (legal / medical / finance) | Highest willingness to pay | They legally *can't* paste client/patient data into vendor clouds. Local-first isn't a preference, it's compliance. Needs packaging + trust, not just tooling. |
| 5 | **Teams wanting shared institutional memory** | Expansion, not wedge | A Markdown vault is a git-shareable knowledge base — onboarding, decisions, "why did we do X". |

## 3. The five strongest value props

Each maps a real pain to a concrete mechanism in the tool.

### A. Own it, and switch models freely
Your vault is files on your disk, not rows in a vendor's database. Move between ChatGPT, Claude,
Gemini, and Grok and your accumulated memory comes with you — because it was never trapped in any of
them. This is the [Ink & Switch local-first](https://www.inkandswitch.com/essay/local-first/) ideal
("you own your data, in spite of the cloud") applied to AI memory, and it's riding a regulatory
tailwind: the EU Data Act's portability and provider-switching provisions are phasing in, with
switching fees due to be eliminated by 2027. Lock-in is becoming a liability; ownership is the hedge.

### B. One brain, every model
The same vault feeds any assistant. The interop story is real and standardizing fast:
**Model Context Protocol (MCP)** was created by Anthropic, adopted by OpenAI and Google DeepMind, and
in Dec 2025 donated to the Linux Foundation — a genuinely neutral, community-owned cross-assistant
standard, with an ecosystem that grew from ~100k to millions of server downloads in months.
([MCP overview](https://en.wikipedia.org/wiki/Model_Context_Protocol),
[Anthropic](https://www.anthropic.com/news/model-context-protocol)) A plain-file memory layer is the
simplest thing that works across every one of those clients — no per-vendor integration to rot.

### C. Free your context — stop running out, stop compacting, stop wasting tokens
This is the engineering heart. Today a long chat fills the window until three bad things happen: it
**rots** (recall degrades as tokens pile up), it triggers a **slow, lossy compaction** (a minute-plus
pause that summarizes your history away and quietly drops detail), and every turn **re-carries a
bloated transcript** you pay for again and again — a session pinned at `ctx:100%` is burning tokens
to remember things badly.

second-brain fixes this by keeping your memory in the *vault*, outside the window, so you stop
leaning on the conversation as memory:
- **auto-captures** each session into `Daily/` so nothing depends on your memory or the model's,
- **recalls just-in-time** — only the handful of notes relevant to *this* prompt enter the window,
  the direct countermeasure to context rot (and to paying for a full history every turn),
- lets you **`/clear` and start fresh cheaply** — the next session reloads what matters from the
  vault, so you rarely need to let a chat grow to the point of compaction at all,
- **snapshots before compaction** so if it does happen, the high-signal state (task, files,
  decisions) survives instead of being summarized away, and
- **shards its index**: `MEMORY.md` stays a thin table of contents that grows with *folders*, not
  *notes* (per-folder `_index-*` shards hold the detail), so the index never blows past the model's
  read cap no matter how many hundreds of notes accumulate.

Net effect: you effectively **never run out of context** (it isn't held in the window), **never sit
through a compaction**, and **never re-pay for a bloated transcript**. "My `MEMORY.md` keeps
overflowing" also stops being possible — it structurally can't.

### D. Build a real second brain, hands-free
Obsidian-compatible, `[[wikilinked]]`, frontmatter-versioned notes — the personal knowledge base
you'd want anyway, except it fills itself from your actual work and you can open it in Obsidian for
the graph view. If the tool vanished tomorrow, you'd still have every file.

### E. The neuron effect — skills compound across projects
Because every project's memory lands in *one* linked vault instead of a separate silo, what you
learn in one place carries into the next. A debugging trick discovered in project A, a deploy gotcha
from project B, a prompt pattern that worked in C — all become notes that recall and `[[wikilink]]`
into each other. The graph starts firing like neurons: work on something new and the relevant past
lesson surfaces on its own, even though it came from an unrelated project. This is the core
Zettelkasten promise — *emergent connections between ideas* — applied to your AI work, and it's
precisely what siloed memory can't do. Per-app memory is either **scoped per project** (Claude
Projects keep memory inside a single project) or an **undifferentiated blob** (ChatGPT's one memory
pool with no links); neither gives you cross-project *associative* transfer. Every project you do
makes the next one smarter.

## 4. Competitive landscape (honest)

| Tool | Storage | You own + export? | Cross-LLM? | One-line take |
|---|---|---|---|---|
| **second-brain** | Local plain-Markdown vault | **Yes** — files on disk, Obsidian-native | **Yes** — any assistant that reads the files | Local-first, file-based, no account, hands-free capture |
| Basic Memory | Local Markdown + SQLite index (opt. cloud sync) | Yes | Yes (any MCP client) | **Closest peer** — same file model, ahead on semantic search + phone sync |
| Pieces | On-device (own DB) | Yes | Yes (pick GPT/Claude/Gemini/local) | Strong local cross-LLM peer; dev-focused, OS-level capture, own DB not files |
| mem0 | Self-host DB or cloud | If self-hosted | Yes (provider-agnostic) | Dev SDK + knowledge-graph retrieval; not a readable note vault |
| Letta / MemGPT | Self-host DB or cloud | If self-hosted | Yes | Agent framework, heavy infra, not portable Markdown |
| MCP "memory" (official) | Local single JSON file | Yes | Yes (any MCP client) | Reference server; JSON entities, not human-readable notes |
| Supermemory | Cloud API (OSS server) | Partial | Yes | Universal MCP memory, but cloud-hosted store |
| ChatGPT memory | OpenAI cloud | **No** (not in export) | **No** | Fully locked, single-provider |
| Claude memory + Projects | Anthropic cloud | Limited | **No** | Locked, single-provider |
| Gemini personal context | Google cloud | Import-only | **No** | Locked; import in, no export out |
| Obsidian + Copilot/Smart Connections | Local vault | Yes | Partial | The other true bring-your-own-memory pattern |

The niche nobody else fully owns: **local + file-based + cross-LLM + no account + hands-free hook
capture.** Basic Memory and Pieces are the honest peers; the native memories are the incumbents we're
reacting against.

## 5. Where we honestly don't win

- **No semantic / vector search.** Retrieval is decay-aware keyword ranking + grep, not embeddings.
  mem0, Letta, and Basic Memory will beat flat Markdown on fuzzy recall and knowledge-graph queries
  at scale.
- **Basic Memory and Pieces are real, capable peers.** Basic Memory adds vector search and phone
  sync; Pieces adds OS-level 9-month auto-capture and a large MCP toolset. We win on zero-infra,
  no-account simplicity and native Claude Code fit — not on feature breadth.
- **Native memories win on ubiquity.** They're on by default for hundreds of millions of users with
  zero setup. We ask you to install and own something. That's the trade: effort for control.
- **It's early.** Grep + Markdown is deliberately boring; if your use case needs agentic
  multi-hop retrieval today, a database-backed tool fits better now.

## 6. The narrative

> Every AI vendor is racing to remember you — and to make sure that memory only works inside their
> walls. Your context becomes their moat. second-brain flips it: your memory is a folder of plain
> Markdown files on your own disk. Every assistant reads and writes the same folder, so you can
> switch models on a whim and never re-explain yourself. Sessions stop resetting. Your index never
> overflows. And because it's all one linked graph, a lesson learned in one project fires when you
> start the next — your knowledge compounds instead of scattering. If every AI company disappeared
> tomorrow, you'd still have every note. Own your mind; rent the model.

**Taglines:**
- *Your memory. Every model. Your disk.*
- *One brain for every AI — owned by you.*
- *Stop renting your memory back from the model that stored it.*
- *Switch models on a whim. Keep your mind.*
- *Every project makes the next one smarter.*
- *Never compact a conversation again.*
- *Local-first memory for LLMs.*

## 7. Sources

**Context / the engineering case**
- Anthropic — Effective context engineering ("finite resource", context rot): https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents
- Context rot corroboration: https://www.understandingai.org/p/context-rot-the-emerging-challenge

**Lock-in & portability**
- The AI memory portability problem: https://portable-ai-memory.org/blog/ai-memory-portability-problem/
- Anthropic "memory import" (poach from ChatGPT): https://mlq.ai/news/anthropic-launches-prompt-to-extract-user-memories-from-chatgpt/
- Claude memory limits: https://xtrace.ai/blog/claude-memory-2026-limits-and-fixes

**Interop / MCP**
- MCP overview + governance: https://en.wikipedia.org/wiki/Model_Context_Protocol
- MCP (primary): https://www.anthropic.com/news/model-context-protocol
- MCP ecosystem scale: https://www.pento.ai/blog/a-year-of-mcp-2025-review

**Local-first / PKM**
- Ink & Switch, Local-First Software: https://www.inkandswitch.com/essay/local-first/
- Obsidian local-file philosophy: https://photes.io/blog/posts/is-obsidian-a-local-first-app

**Peers / market**
- Basic Memory (closest peer): https://github.com/basicmachines-co/basic-memory
- mem0 (demand proof: 59k+ stars, $24M raised): https://docs.mem0.ai/open-source/overview
- Pieces long-term memory: https://pieces.app/features/long-term-memory/ai-memory-assistant

**Audience / demand signals**
- Claude Code adoption: https://www.gradually.ai/en/claude-code-statistics/
- Obsidian usage: https://fueler.io/blog/obsidian-usage-revenue-valuation-growth-statistics
- HN "stop LLMs from resetting": https://news.ycombinator.com/item?id=46252809

---

*Caveats: population figures (Obsidian / Claude Code / Cursor MAU) are third-party estimates, not
official. The "ChatGPT memory isn't exportable" and any vendor-acquisition claims are widely
reported but rest on secondary sources — verify before quoting as fact. Everything about our own
architecture is verifiable in this repo.*
