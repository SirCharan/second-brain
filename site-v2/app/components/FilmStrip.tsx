const BEATS = [
  {
    n: "01",
    title: "Capture",
    body: "Every session lands as wikilinked Markdown in one vault. Hands-free. Obsidian-compatible.",
  },
  {
    n: "02",
    title: "Clear",
    body: "Free the context window. Compaction is optional. The vault still remembers the hard parts.",
  },
  {
    n: "03",
    title: "Recall",
    body: "Open Claude, Cursor, or Grok tomorrow. The right notes surface before you re-explain yourself.",
  },
] as const;

export default function FilmStrip() {
  return (
    <section
      aria-labelledby="how-heading"
      className="relative border-t border-border-soft bg-bg-elevated"
    >
      <div className="mx-auto max-w-6xl px-5 py-20 sm:px-8 sm:py-28">
        <div className="mb-12 flex flex-col gap-3 sm:mb-16 sm:flex-row sm:items-end sm:justify-between">
          <h2
            id="how-heading"
            className="display max-w-lg text-[clamp(1.85rem,4vw,2.75rem)] leading-[1.05] text-fg"
          >
            Write it once.
            <br />
            Recall it anywhere.
          </h2>
          <p className="max-w-xs text-sm leading-relaxed text-fg-dim">
            Memory lives in the vault, not the conversation. End a session. Switch
            models. Pick up cold.
          </p>
        </div>

        <ol className="grid gap-px overflow-hidden rounded-lg border border-border bg-border sm:grid-cols-3">
          {BEATS.map((b) => (
            <li
              key={b.n}
              className="flex min-h-[220px] flex-col bg-surface p-6 sm:p-8"
            >
              <span className="mono text-xs text-accent">{b.n}</span>
              <h3 className="display mt-6 text-3xl text-fg sm:text-[2rem]">{b.title}</h3>
              <p className="mt-3 flex-1 text-sm leading-relaxed text-fg-dim">{b.body}</p>
            </li>
          ))}
        </ol>
      </div>
    </section>
  );
}
