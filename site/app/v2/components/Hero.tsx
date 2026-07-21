import GraphField from "./GraphField";
import CopyCommand from "./CopyCommand";
import { GitHubMark } from "./Mark";

const REPO = "https://github.com/SirCharan/second-brain";
const INSTALL = "/plugin marketplace add SirCharan/second-brain";

export default function Hero() {
  return (
    <section
      id="top"
      className="relative flex min-h-svh flex-col justify-end overflow-hidden px-6 pb-20 pt-28 sm:px-10 sm:pb-24"
    >
      <GraphField mode="ambient" className="absolute inset-0 h-full w-full" />

      {/* dual scrim: left copy pocket + bottom fade into page */}
      <div
        className="pointer-events-none absolute inset-0"
        style={{
          background: [
            "radial-gradient(68% 70% at 18% 78%, rgba(12,10,9,0.88), transparent 70%)",
            "linear-gradient(to top, var(--color-bg) 4%, rgba(12,10,9,0.72) 22%, rgba(12,10,9,0.2) 48%, transparent 70%)",
            "linear-gradient(to right, rgba(12,10,9,0.55) 0%, transparent 42%)",
          ].join(", "),
        }}
      />

      <div className="relative z-10 mx-auto grid w-full max-w-6xl gap-12 lg:grid-cols-[minmax(0,1.15fr)_minmax(0,0.85fr)] lg:items-end">
        <div>
          <p className="font-mono text-[11px] tracking-[0.16em] text-accent uppercase">
            local-first · open source · your disk
          </p>

          <h1 className="mt-5 font-display text-[clamp(2.85rem,6.8vw,5.4rem)] leading-[0.98] tracking-tight">
            The chat ends.
            <br />
            <span className="text-accent">The memory stays.</span>
          </h1>

          <p className="mt-6 max-w-md text-lg leading-relaxed text-ink-dim">
            second-brain captures every AI session into Markdown on your machine.
            Switch models, clear the window, close the laptop. Nothing walks away.
          </p>

          <div className="mt-9 max-w-xl">
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

        {/* right column: quiet proof card, not a fake app window */}
        <aside className="hidden max-w-sm justify-self-end rounded-2xl border border-line bg-surface/55 p-6 backdrop-blur-sm lg:block">
          <p className="font-mono text-[11px] tracking-wide text-ink-faint uppercase">
            what lands on disk
          </p>
          <ul className="mt-4 space-y-3 font-mono text-[13px] leading-relaxed">
            <li className="flex gap-3">
              <span className="text-accent">+</span>
              <span>
                <span className="text-ink">Daily/2026-07-21.md</span>
                <span className="mt-0.5 block text-ink-faint">session capture, auto</span>
              </span>
            </li>
            <li className="flex gap-3">
              <span className="text-accent">+</span>
              <span>
                <span className="text-ink">Projects/acme/rate-limit.md</span>
                <span className="mt-0.5 block text-ink-faint">decision you already paid for</span>
              </span>
            </li>
            <li className="flex gap-3">
              <span className="text-accent">↳</span>
              <span>
                <span className="text-ink">recalled next session</span>
                <span className="mt-0.5 block text-ink-faint">any model, same vault</span>
              </span>
            </li>
          </ul>
          <p className="mt-5 border-t border-line pt-4 text-sm leading-relaxed text-ink-dim">
            Plain files. Grep them, git them, open them in Obsidian. Delete the tool
            and the notes remain.
          </p>
        </aside>
      </div>
    </section>
  );
}
