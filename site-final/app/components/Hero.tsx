import GraphField from "./GraphField";
import CopyCommand from "./CopyCommand";
import { GitHubMark } from "./Mark";

const REPO = "https://github.com/SirCharan/second-brain";
const INSTALL = "/plugin marketplace add SirCharan/second-brain";

/** Hero copy locked from ck screenshot (final cut). */
export default function Hero() {
  return (
    <section
      id="top"
      className="relative flex min-h-svh flex-col justify-center overflow-hidden px-6 pb-20 pt-24 sm:px-10 sm:pb-24"
    >
      <GraphField mode="ambient" className="absolute inset-0 h-full w-full" />

      <div
        className="pointer-events-none absolute inset-0"
        style={{
          background: [
            "radial-gradient(70% 65% at 22% 55%, rgba(12,10,9,0.78), transparent 68%)",
            "linear-gradient(to top, var(--color-bg) 0%, rgba(12,10,9,0.55) 18%, rgba(12,10,9,0.15) 45%, transparent 68%)",
            "linear-gradient(to right, rgba(12,10,9,0.5) 0%, transparent 50%)",
          ].join(", "),
        }}
      />

      <div className="relative z-10 mx-auto w-full max-w-3xl">
        <p className="font-mono text-[11px] tracking-[0.18em] text-accent uppercase">
          local-first · open source · your disk
        </p>

        <h1 className="mt-6 font-display text-[clamp(2.85rem,7.2vw,5.25rem)] leading-[0.98] tracking-tight">
          The chat ends.
          <br />
          <span className="text-accent">The memory stays.</span>
        </h1>

        <p className="mt-7 max-w-lg text-lg leading-relaxed text-ink-dim sm:text-[1.15rem]">
          second-brain captures every AI session into Markdown on your machine.
          Switch models, clear the window, close the laptop. Nothing walks away.
        </p>

        <div className="mt-10 max-w-xl">
          <CopyCommand command={INSTALL} />
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
            <span>Apache-2.0</span>
          </div>
        </div>
      </div>
    </section>
  );
}
