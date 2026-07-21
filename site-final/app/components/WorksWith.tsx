/** Honest cross-app compatibility. Real names + status — no logo wall, no tiles. */
export default function WorksWith() {
  const now = [{ name: "Claude Code", note: "hooks, today" }];
  const soon = ["Claude Desktop", "ChatGPT", "Cursor"];

  return (
    <section
      id="works-with"
      aria-label="Works with"
      className="border-t border-line px-6 py-16 sm:px-10 sm:py-20"
    >
      <div className="mx-auto max-w-6xl">
        <p className="font-mono text-[11px] tracking-[0.14em] text-ink-faint uppercase">
          works with
        </p>

        <div className="mt-5 flex flex-wrap items-baseline gap-x-8 gap-y-4 sm:gap-x-10">
          {now.map((t) => (
            <span
              key={t.name}
              className="flex flex-wrap items-baseline gap-x-2 gap-y-1 font-display text-[clamp(1.5rem,3vw,2rem)] text-ink"
            >
              {t.name}
              <span className="font-sans text-xs font-normal tracking-normal text-accent">
                ✓ {t.note}
              </span>
            </span>
          ))}
          {soon.map((n) => (
            <span
              key={n}
              className="flex flex-wrap items-baseline gap-x-2 gap-y-1 font-display text-[clamp(1.5rem,3vw,2rem)] text-ink-dim"
            >
              {n}
              <span className="font-sans text-xs font-normal tracking-normal text-ink-faint">
                via MCP, soon
              </span>
            </span>
          ))}
        </div>

        <p className="mt-6 max-w-2xl text-[15px] leading-relaxed text-ink-dim">
          The vault is plain files, so any model can read it now. Automatic capture and
          recall land in the other apps through a small MCP server we&apos;re building
          next.
        </p>
      </div>
    </section>
  );
}
