/** Promise strip copy locked from ck screenshot (below hero). */
const PROMISES = [
  {
    k: "01",
    title: "Your disk, not their cloud",
    body: "Memory is Markdown under your home folder. Export is a folder copy.",
  },
  {
    k: "02",
    title: "Any model, same vault",
    body: "Claude, GPT, Gemini, Grok. The brain does not move when the chat does.",
  },
  {
    k: "03",
    title: "Context that stays lean",
    body: "Recall only what matters. Skip the slow compaction tax on every long thread.",
  },
];

export default function PromiseStrip() {
  return (
    <section
      aria-label="Core promises"
      className="border-y border-line bg-bg px-6 py-16 sm:px-10 sm:py-20"
    >
      <div className="mx-auto grid max-w-6xl gap-12 sm:grid-cols-3 sm:gap-10">
        {PROMISES.map((p) => (
          <div key={p.k}>
            <span className="font-mono text-[11px] tracking-wider text-accent">
              {p.k}
            </span>
            <h2 className="mt-2 font-display text-xl leading-snug sm:text-[1.35rem]">
              {p.title}
            </h2>
            <p className="mt-2 max-w-xs text-[15px] leading-relaxed text-ink-dim">
              {p.body}
            </p>
          </div>
        ))}
      </div>
    </section>
  );
}
