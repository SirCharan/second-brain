import CopyCommand from "./CopyCommand";

export default function Install() {
  return (
    <section
      id="install"
      className="relative border-t border-border-soft bg-bg-elevated"
    >
      <div className="mx-auto max-w-6xl px-5 py-20 sm:px-8 sm:py-28">
        <div className="relative overflow-hidden rounded-xl border border-border bg-surface px-6 py-12 sm:px-12 sm:py-16">
          {/* Warm key light — contained, not clipped glow soup */}
          <div
            className="pointer-events-none absolute -right-16 -top-24 h-64 w-64 rounded-full opacity-40"
            style={{
              background:
                "radial-gradient(circle, color-mix(in srgb, var(--accent) 35%, transparent), transparent 70%)",
            }}
            aria-hidden
          />

          <div className="relative max-w-xl">
            <h2 className="display text-[clamp(2rem,5vw,3rem)] leading-[1.05] text-fg">
              Install in one line.
            </h2>
            <p className="mt-4 text-sm leading-relaxed text-fg-dim sm:text-base">
              Claude Code marketplace plugin. Or run{" "}
              <code className="mono text-accent">./install.sh</code> from the
              repo. Your vault starts empty and fills itself from real work.
            </p>

            <div className="mt-8">
              <CopyCommand large className="w-full max-w-xl" />
            </div>

            <div className="mt-8 flex flex-wrap items-center gap-x-6 gap-y-2 text-sm text-muted">
              <a
                href="https://github.com/SirCharan/second-brain"
                className="text-fg-dim transition-colors hover:text-fg"
                rel="noreferrer"
                target="_blank"
              >
                github.com/SirCharan/second-brain
              </a>
              <span className="hidden h-3 w-px bg-border sm:block" aria-hidden />
              <span>Apache-2.0</span>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}
