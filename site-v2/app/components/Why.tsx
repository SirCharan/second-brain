const POINTS = [
  {
    title: "Own the files",
    body: "Plain .md on your disk. Version in git. Move between tools. If the plugin vanished tomorrow, you still have every note.",
  },
  {
    title: "One brain, every model",
    body: "The vault is not ChatGPT memory or Claude memory. It is yours. Feed any assistant the slice that matters for this turn.",
  },
  {
    title: "Never run out of window",
    body: "Context rot is real. Keep history outside the chat, recall just-in-time, and /clear without losing the plot.",
  },
] as const;

export default function Why() {
  return (
    <section className="relative border-t border-border-soft">
      <div className="mx-auto grid max-w-6xl gap-12 px-5 py-20 sm:px-8 sm:py-28 lg:grid-cols-12 lg:gap-16">
        <div className="lg:col-span-4">
          <h2 className="display text-[clamp(1.75rem,3.5vw,2.35rem)] leading-[1.08] text-fg">
            Disk, not chat.
            <br />
            <span className="text-fg-dim">No account required.</span>
          </h2>
        </div>
        <ul className="flex flex-col gap-10 lg:col-span-8">
          {POINTS.map((p) => (
            <li
              key={p.title}
              className="grid gap-2 border-l border-accent/40 pl-5 sm:grid-cols-[minmax(0,11rem)_1fr] sm:gap-8 sm:border-l-0 sm:pl-0"
            >
              <h3 className="text-base font-medium text-fg sm:pt-0.5">{p.title}</h3>
              <p className="text-sm leading-relaxed text-fg-dim sm:text-[15px]">{p.body}</p>
            </li>
          ))}
        </ul>
      </div>
    </section>
  );
}
