import GraphField from "./GraphField";
import CopyCommand from "./CopyCommand";
import { GitHubMark } from "./Mark";

const REPO = "https://github.com/SirCharan/second-brain";

export default function Hero({ mode }: { mode: "ambient" | "interactive" }) {
  return (
    <section
      id="top"
      className="relative flex min-h-svh flex-col justify-end overflow-hidden px-6 pb-16 pt-24 sm:px-10"
    >
      {/* the signature: a living vault-graph, full-screen, the star of the fold */}
      <GraphField mode={mode} className="absolute inset-0 h-full w-full" />

      {/* scrim weighted to the bottom, where the copy sits — the graph stays clear
          up top and dissolves into the page color at the very bottom */}
      <div
        className="pointer-events-none absolute inset-0"
        style={{
          background:
            "radial-gradient(72% 58% at 26% 80%, rgba(12,10,9,0.84), transparent 72%), linear-gradient(to top, var(--color-bg) 5%, rgba(12,10,9,0.6) 24%, rgba(12,10,9,0.16) 52%, transparent 74%)",
        }}
      />

      <div className="relative z-10 mx-auto w-full max-w-5xl">
        <div className="max-w-2xl">
          <h1 className="font-display text-[clamp(2.7rem,6.4vw,5rem)] leading-[1.01] tracking-tight">
            Your AI forgets.
            <br />
            <span className="text-accent">Your vault doesn&apos;t.</span>
          </h1>
          <p className="mt-6 max-w-lg text-lg leading-relaxed text-ink-dim">
            Local-first memory for AI assistants. Every session lands in Markdown you own,
            and any model reads it back.
          </p>

          <div className="mt-9 max-w-xl">
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

      {/* interaction hint, only where it applies */}
      {mode === "interactive" && (
        <div className="pointer-events-none absolute right-6 top-24 z-10 hidden font-mono text-xs text-ink-faint sm:block">
          hover a node · drag to pan · ⌘/ctrl-scroll to zoom
        </div>
      )}
    </section>
  );
}
