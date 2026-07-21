/* Five value props as an asymmetric bento. Icons are a bespoke set built from the
   brand's own node-graph language (dots + edges), never a generic icon pack, never
   in a tile. Hover shifts tone, no lift. */

type GlyphKind = "neuron" | "own" | "models" | "context" | "grow";

function Glyph({ kind }: { kind: GlyphKind }) {
  const s = { stroke: "var(--color-ink-dim)", strokeWidth: 1.5, fill: "none" as const };
  const dot = (cx: number, cy: number, r = 2.6, hot = false) => (
    <circle cx={cx} cy={cy} r={r} fill={hot ? "var(--color-accent)" : "var(--color-surface-2)"} stroke={hot ? "var(--color-accent)" : "var(--color-ink-dim)"} strokeWidth={1.5} />
  );
  return (
    <svg width="30" height="30" viewBox="0 0 30 30" aria-hidden="true">
      {kind === "neuron" && (
        <>
          <line x1="7" y1="9" x2="22" y2="20" {...s} />
          <line x1="7" y1="9" x2="9" y2="22" {...s} />
          <line x1="22" y1="20" x2="23" y2="8" {...s} />
          {dot(7, 9)}
          {dot(9, 22)}
          {dot(23, 8)}
          {dot(22, 20, 3.2, true)}
        </>
      )}
      {kind === "own" && (
        <>
          <path d="M8 6 H6 V24 H8 M22 6 H24 V24 H22" {...s} strokeLinecap="round" />
          {dot(15, 15, 3.4, true)}
        </>
      )}
      {kind === "models" && (
        <>
          <line x1="8" y1="15" x2="23" y2="7" {...s} />
          <line x1="8" y1="15" x2="23" y2="15" {...s} />
          <line x1="8" y1="15" x2="23" y2="23" {...s} />
          {dot(8, 15, 3.2, true)}
          {dot(23, 7)}
          {dot(23, 15)}
          {dot(23, 23)}
        </>
      )}
      {kind === "context" && (
        <>
          <circle cx="15" cy="15" r="9" {...s} strokeDasharray="2 3" />
          {dot(15, 15, 3.4, true)}
        </>
      )}
      {kind === "grow" && (
        <>
          <line x1="9" y1="22" x2="15" y2="14" {...s} />
          <line x1="15" y1="14" x2="21" y2="8" {...s} />
          <line x1="15" y1="14" x2="22" y2="18" {...s} />
          {dot(9, 22)}
          {dot(15, 14, 3, true)}
          {dot(21, 8)}
          {dot(22, 18)}
        </>
      )}
    </svg>
  );
}

function Prop({
  kind,
  title,
  body,
  className = "",
}: {
  kind: GlyphKind;
  title: string;
  body: string;
  className?: string;
}) {
  return (
    <div
      className={`group rounded-2xl border border-line bg-surface/50 p-6 transition-colors hover:border-line-strong hover:bg-surface-2/50 sm:p-7 ${className}`}
    >
      <Glyph kind={kind} />
      <h3 className="mt-5 font-display text-xl leading-snug">{title}</h3>
      <p className="mt-2 text-[15px] leading-relaxed text-ink-dim">{body}</p>
    </div>
  );
}

export default function ValueProps() {
  return (
    <section className="px-6 py-24 sm:px-10 sm:py-28">
      <div className="mx-auto max-w-5xl">
        <h2 className="max-w-2xl font-display text-[clamp(1.9rem,3.6vw,2.9rem)] leading-tight">
          Not another memory silo. A brain you own.
        </h2>

        <div className="mt-12 grid gap-4 lg:grid-cols-3">
          <Prop
            kind="neuron"
            title="Skills compound across projects"
            body="Everything lands in one linked vault, not per-project silos. A trick learned in one project surfaces — and links itself in — when you start the next. The graph fires like neurons; every project makes the next one smarter."
            className="lg:col-span-2"
          />
          <Prop
            kind="own"
            title="Own it. Switch freely."
            body="Your memory is plain files on your disk. Move between ChatGPT, Claude, Gemini and Grok — it comes with you, because it was never trapped in any of them."
          />
          <Prop
            kind="models"
            title="One brain, every model"
            body="The same vault feeds any assistant. Nothing siloed, nothing to re-explain when you change tools."
          />
          <Prop
            kind="context"
            title="Never run out. Never compact."
            body="Memory lives in the vault, not the window. Recall only what's relevant, /clear freely, and skip the slow, lossy compaction that eats your tokens."
          />
          <Prop
            kind="grow"
            title="A second brain that fills itself"
            body="Obsidian-compatible, wikilinked notes, captured hands-free from your real work. The knowledge base you'd build anyway — building itself."
          />
        </div>
      </div>
    </section>
  );
}
