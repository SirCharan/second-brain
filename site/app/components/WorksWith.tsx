/* Honest cross-app compatibility. Real names + status, no fake logo wall, no tiles.
   Claude Code works today (hooks); the rest come via the MCP server. */
export default function WorksWith() {
  const now = [{ name: "Claude Code", note: "hooks, today" }];
  const soon = ["Claude Desktop", "ChatGPT", "Cursor"];
  return (
    <section className="px-6 py-16 sm:px-10">
      <div className="mx-auto max-w-5xl">
        <p className="font-mono text-xs uppercase tracking-widest text-ink-faint">works with</p>
        <div className="mt-5 flex flex-wrap items-baseline gap-x-8 gap-y-4">
          {now.map((t) => (
            <span key={t.name} className="flex items-baseline gap-2 font-display text-2xl text-ink">
              {t.name}
              <span className="font-sans text-xs text-accent">✓ {t.note}</span>
            </span>
          ))}
          {soon.map((n) => (
            <span key={n} className="flex items-baseline gap-2 font-display text-2xl text-ink-dim">
              {n}
              <span className="font-sans text-xs text-ink-faint">via MCP, soon</span>
            </span>
          ))}
        </div>
        <p className="mt-5 max-w-xl text-sm leading-relaxed text-ink-faint">
          The vault is plain files, so any model can read it now. Automatic capture and recall land
          in the other apps through a small MCP server we&apos;re building next.
        </p>
      </div>
    </section>
  );
}
