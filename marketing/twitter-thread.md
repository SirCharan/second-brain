# X thread — second-brain (personal)

Paste-ready. Voice: first person, ck. Register: semichenkko / polydao / SpikeCalls / chewadot / Nazik2053 — ALL-CAPS lede, short lines, before→after, graph as proof.

Every number is from the live vault or the live harness (`SECOND_BRAIN_DUMP_PCT=20`, `SECOND_BRAIN_CTX_WINDOW=1000000` in `~/.claude/settings.json`). Do not reuse the Harvard sophomore story.

Token math (show in article, punch in thread):
- Opus input $5 / million tokens
- Dump fires at 20% of 1M = 200,000 tokens, writes `_infra/_carryover.md`, `/clear`
- Next session resumes from the vault (~13k fixed overhead, measured 2026-08-14)
- A session that would have sat at 80% re-sends 800,000 tokens every turn = $4.00
- After dump+clear: ~13,000 tokens = $0.07
- Saved per turn: **$3.93**
- 40 turns/day × 22 workdays = **$3,458/month**

---

## POST 1 — hero note-tweet

**Media:** `shots/01-graph-hero.mp4` or `shots/01-graph-hero.png`

```
CLAUDE STARTED WRITING MY OBSIDIAN VAULT WITHOUT ME ASKING

I never typed "make a note."
I never ran "ingest this."
I just worked.

A hook captured every session into Markdown on my disk.
Another hook recalled the right notes on the next prompt.
At 20% of the context window it dumped the live task into the vault and I hit /clear.

The chat went back to zero.
The memory did not.

July 6: one daily note.
Mid-August: 1,099 notes. 6,777 links. 99% of them wired.

A CLS fix I shipped in one repo fired when a different repo started janking.
A Vercel staging gotcha from project A was sitting there when project B hit the same wall.
Claude already knew. I did not re-explain it.

The model did not get smarter.
The machine around it did.

Full context of my work. In files I own.
That is what 10x actually looks like.

Repo + the $3,400/month math in the replies.
```

---

## POST 2 — it writes while you work

**Media:** `shots/03-daily-note.png`

```
Most "AI second brains" still wait for you to dump an inbox at 2 AM.

This one does not wait.

Stop hook: every reply lands in Daily/ as a one-line capture.
SessionStart: the next chat opens already knowing where I left off.
UserPromptSubmit: only the notes that match THIS prompt come back in. Not the whole vault. Not the whole transcript.

I have not filed a note by hand in weeks.
The graph is a side effect of work I was going to do anyway.
```

---

## POST 3 — project A teaches project B

**Media:** `shots/04-linked-note.png` or `shots/04-home.png`

```
Vendor memory is locked to one project, or dumped into one blob with no links.

Mine is one graph across 50 repos.

A DuckDB single-writer collision I hit in a signals repo showed up the first time an unrelated dashboard tried the same pattern.
A PageSpeed / CLS fix from a landing page was already a note when a different site started shifting.
Quality gates I wired for one product now load when I open another.

I did not search for them.
Claude pulled them because the vault is one brain, not a silo per folder.

That is the whole product.
Skills compound. Dead chats do not.
```

---

## POST 4 — the 20% dump (money)

**Media:** `shots/07-landing-or-install.png` (token-tax section) or a /context screenshot

```
At 20% of a 1M window the hook dumps the live task into Obsidian and I /clear.

200,000 tokens. Then zero.

/compact would re-read the whole window at full price. I stopped using it.

Math, Opus input at $5/MTok:

A session sitting at 80% re-sends 800,000 tokens every turn. $4.00.
After the dump: ~13,000 tokens of harness + recall. $0.07.

Saved: $3.93 a turn.
40 turns a day × 22 workdays = $3,458 a month I was burning to remember badly.

The vault kept the thread.
The window got thin again.
```

---

## POST 5 — the harness is the 10x

**Media:** `shots/01-graph-hero.png`

```
Before I typed a word, Claude was already burning 43,000 tokens of plugins, skill descriptions, and session junk.

I cut that to 13,000.
Merged 85 skill folders into 23.
CLAUDE.md 35KB → 11KB.
Plan mode by default. Sonnet builds. Haiku does the noisy work.

Then the vault started filling itself.

Every project I finish makes the next one cheaper.
Claude is 10x smarter on MY work because it finally has MY context. A rented memory blob dies when I close the tab. These files do not.

10x is not the model.
10x is the machine around it.
```

---

## POST 6 — pinpoint advantages

**Media:** `shots/05-reconcile.png`

```
Pinpoint, because vague tools die in the feed:

• Writes the note without being asked
• Recalls it in an unrelated repo when the same class of problem shows up
• Dumps at 20% fill, /clear is free, /compact is the expensive one
• Secrets get scrubbed before they touch disk
• Contradictions get retired, not deleted. Git still sees the fight.
• One export file feeds ChatGPT, Gemini, Grok. The brain does not move
• Uninstall the tool tomorrow. The folder stays
• Windows, macOS, Linux. Stdlib Python. No account

Storage remembers.
This one works.
```

---

## POST 7 — CTA

**Media:** `shots/07-landing-or-install.png`

```
Own your mind. Rent the model.

Repo: https://github.com/SirCharan/second-brain
Site: https://charandeepkapoor.com/second-brain

curl -fsSL https://charandeepkapoor.com/second-brain/install.sh | bash

Walkthrough: https://charandeepkapoor.com/second-brain/get-started

The article under this post has the 20% dump math and the 39-day vault counts.
```

---

## FIRST REPLY (always)

```
Measured, mid-August, this vault:

1,099 notes
6,777 [[wikilinks]]
1,089 notes with at least one link
50 project routes
1,060 sessions since July 6

Dump trigger: 20% of a 1M window
That is 200k tokens.
Harness overhead: 43k → 13k before I type
Saved vs sitting at 80%: $3.93 a turn
About $3,400 a month
Opus input $5/MTok
40 turns a day, 22 days

Obsidian is the viewer.
The product is the folder.
```

---

## Quote-tweet / article post

```
Claude writes my Obsidian vault without being asked.

At 20% context it dumps the task, I /clear, and the next chat already knows what I learned in a different repo last month.

1,099 notes. 6,777 links. ~$3,400/month I stopped paying to re-send a bloated window.

The article is the honest version.
```

---

## Posting notes

- Post 1 is the long Note. 2–7 are replies.
- Graph on 1 and 5. Daily capture on 2. Home/linked note on 3. Landing or /context on 4. Retired note on 6.
- If you only post one thing: Post 1 + first reply + article.
