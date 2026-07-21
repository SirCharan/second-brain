import GraphField from "./GraphField";
import CopyCommand from "./CopyCommand";
import { GitHubMark } from "./Mark";

const REPO = "https://github.com/SirCharan/second-brain";

export default function Hero({ mode }: { mode: "ambient" | "interactive" }) {
  return (
    <section
      id="top"
      className="relative flex min-h-svh flex-col justify-center overflow-hidden px-6 pb-20 pt-28 sm:px-10"
    >
      {/* the signature: a living vault-graph, full-bleed behind everything */}
      <GraphField mode={mode} className="absolute inset-0 h-full w-full" />

      {/* legibility scrim — darker toward the copy, and the graph dissolves into
          the page color at the bottom so the next section starts clean */}
      <div
        className="pointer-events-none absolute inset-0"
        style={{
          background:
            "radial-gradient(90% 70% at 30% 42%, rgba(12,10,9,0.82), rgba(12,10,9,0.35) 55%, transparent 80%), linear-gradient(to bottom, transparent 55%, var(--color-bg) 97%)",
        }}
      />

      <div className="relative z-10 mx-auto w-full max-w-5xl">
        <div className="max-w-2xl">
          <h1 className="font-display text-[clamp(2.7rem,6.4vw,5rem)] leading-[1.01] tracking-tight">
            Your second brain,
            <br />
            <span className="text-accent">wired to every model.</span>
          </h1>
          <p className="mt-6 max-w-lg text-lg leading-relaxed text-ink-dim">
            Local-first memory for your AI assistants. Capture a session once, recall
            it in any model, and keep every byte on your own disk.
          </p>

          <div className="mt-9 max-w-md">
            <CopyCommand command="/plugin marketplace add SirCharan/second-brain" />
            <div className="mt-3 flex flex-wrap items-center gap-x-5 gap-y-2 text-sm text-ink-faint">
              <span>
                or <code className="font-mono text-ink-dim">./install.sh</code>
              </span>
              <a
                href={REPO}
                target="_blank"
                rel="noreferrer"
                className="flex items-center gap-1.5 text-ink-dim transition-colors hover:text-ink"
              >
                <GitHubMark size={15} />
                Star on GitHub
              </a>
              <span className="text-ink-faint">Open source, Apache-2.0</span>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}
