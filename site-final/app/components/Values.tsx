/** Sticky left column + scrolling value list — scroll behavior locked from /v2 cut. */
const ROWS = [
  {
    title: "It never forgets last week",
    body: "The retry params you set on Tuesday, the bug you fixed last session, the decision you already paid for. It lands in Obsidian and stays. Clear the chat; the vault still knows.",
  },
  {
    title: "Project A carries into project B",
    body: "One linked vault, not a silo per repo. What you learned shipping A shows up when you start B. Skills stack across projects instead of dying in dead chats.",
  },
  {
    title: "Own it. Switch freely.",
    body: "Plain files on your disk. Jump between ChatGPT, Claude, Gemini, and Grok. The memory follows you because it was never trapped in a vendor.",
  },
  {
    title: "Just Markdown. No account.",
    body: "Wikilinked .md files. Offline, git-versioned, no server, no login. Uninstall the tool tomorrow and every note remains yours.",
  },
  {
    title: "Never run out. Never compact.",
    body: "Memory lives outside the window. Recall only what matters for this prompt, and skip the slow compaction that burns tokens to remember badly.",
  },
  {
    title: "It fills itself",
    body: "Obsidian-compatible notes, captured as you work. The vault you meant to keep by hand, building on its own. Always remembering.",
  },
];

export default function Values() {
  return (
    <section id="why" className="border-t border-line px-6 py-24 sm:px-10 sm:py-32">
      <div className="mx-auto max-w-6xl">
        <div className="grid gap-12 lg:grid-cols-[minmax(0,0.9fr)_minmax(0,1.1fr)] lg:gap-20">
          <div className="lg:sticky lg:top-28 lg:self-start">
            <p className="font-mono text-[11px] tracking-[0.14em] text-ink-faint uppercase">
              why it exists
            </p>
            <h2 className="mt-3 font-display text-[clamp(2rem,3.6vw,3rem)] leading-[1.05]">
              Memory on your disk,
              <br />
              <span className="text-ink-dim">not in the chat.</span>
            </h2>
            <p className="mt-5 max-w-sm text-[15px] leading-relaxed text-ink-dim">
              Vendor memory is a moat. second-brain is a folder. That is the whole product
              thesis, stated plainly.
            </p>
          </div>

          <div className="divide-y divide-line border-t border-line">
            {ROWS.map((row, i) => (
              <article
                key={row.title}
                className="grid gap-3 py-8 sm:grid-cols-[3rem_1fr] sm:gap-6"
              >
                <span className="font-mono text-sm text-accent">
                  {String(i + 1).padStart(2, "0")}
                </span>
                <div>
                  <h3 className="font-display text-xl leading-snug sm:text-[1.35rem]">
                    {row.title}
                  </h3>
                  <p className="mt-2 max-w-xl text-[15px] leading-relaxed text-ink-dim">
                    {row.body}
                  </p>
                </div>
              </article>
            ))}
          </div>
        </div>
      </div>
    </section>
  );
}
