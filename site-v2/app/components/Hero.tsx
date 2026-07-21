import MemoryOrrery from "./MemoryOrrery";
import CopyCommand from "./CopyCommand";

export default function Hero() {
  return (
    <section className="relative flex min-h-[100svh] flex-col overflow-hidden pb-16 pt-0">
      <MemoryOrrery />

      <div className="relative z-10 mx-auto flex w-full max-w-6xl flex-1 flex-col justify-end px-5 pb-10 pt-24 sm:px-8 sm:pb-14">
        <div className="max-w-2xl">
          <p className="mb-5 text-sm text-cool sm:text-[15px]">
            Local-first memory for every AI assistant
          </p>

          <h1 className="display text-[clamp(2.75rem,9vw,5.75rem)] text-fg">
            Memory that
            <br />
            <span className="text-accent-hot">outlives</span> the chat.
          </h1>

          <p className="mt-6 max-w-md text-base leading-relaxed text-fg-dim sm:text-lg">
            Sessions write themselves into Markdown on your disk. The next model
            recalls what matters. No account. No cloud lock-in. Clear the window
            whenever you want.
          </p>

          <div className="mt-8 flex flex-col gap-3 sm:flex-row sm:items-center">
            <CopyCommand large className="w-full sm:w-auto" />
            <a
              href="https://github.com/SirCharan/second-brain"
              className="inline-flex items-center justify-center rounded-md border border-border px-4 py-3 text-sm text-fg-dim transition-colors hover:border-fg-dim hover:text-fg"
              rel="noreferrer"
              target="_blank"
            >
              Star on GitHub
            </a>
          </div>

          <p className="mt-4 text-xs text-muted">
            Open source · Apache-2.0 · Claude Code plugin · works offline
          </p>
        </div>

        <p className="mt-16 hidden text-[11px] tracking-[0.14em] text-muted uppercase sm:block">
          hover a node · drag to pan · graph grows like Obsidian
        </p>
      </div>
    </section>
  );
}
