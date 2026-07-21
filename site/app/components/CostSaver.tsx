/* Dedicated cost-saver beat — the token proof point + the dump/reset mechanic. */
export default function CostSaver() {
  return (
    <section className="px-6 py-24 sm:px-10 sm:py-28">
      <div className="mx-auto max-w-5xl">
        <h2 className="max-w-2xl font-display text-[clamp(1.9rem,3.6vw,2.9rem)] leading-tight">
          Long sessions get expensive. This one doesn&apos;t.
        </h2>
        <p className="mt-5 max-w-xl text-lg leading-relaxed text-ink-dim">
          Every turn re-sends the whole conversation as input tokens. A long session can push past{" "}
          <span className="text-accent">800,000 tokens</span> re-sent on <em>every</em> message.
        </p>
        <p className="mt-4 max-w-xl leading-relaxed text-ink-dim">
          second-brain watches the window. Near half-full it dumps the session to your vault; you{" "}
          <code className="font-mono text-[0.95em] text-ink">/clear</code>, and the next turns
          restart near-empty. Same work, a fraction of the tokens.
        </p>
      </div>
    </section>
  );
}
