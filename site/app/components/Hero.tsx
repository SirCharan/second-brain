import MemoryGraph from "./MemoryGraph";
import Terminal from "./Terminal";
import CopyCommand from "./CopyCommand";
import { GitHubMark } from "./Mark";

const REPO = "https://github.com/SirCharan/second-brain";

export default function Hero() {
  return (
    <section
      id="top"
      className="relative flex min-h-svh flex-col justify-center overflow-hidden px-6 pb-16 pt-28 sm:px-10"
    >
      {/* signature atmosphere: the vault-as-graph, bleeding off the right edge */}
      <MemoryGraph className="pointer-events-none absolute right-[-8%] top-1/2 hidden w-[60%] max-w-3xl -translate-y-1/2 opacity-90 lg:block" />

      <div className="mx-auto w-full max-w-5xl">
        <div className="max-w-2xl">
          <h1 className="font-display text-[clamp(2.6rem,6vw,4.6rem)] leading-[1.02] tracking-tight">
            Your memory, every model,{" "}
            <span className="text-accent">your disk.</span>
          </h1>
          <p className="mt-6 max-w-xl text-lg leading-relaxed text-ink-dim">
            A local-first memory for your AI assistants. It captures every session
            into plain Markdown you own, then recalls what matters — in any model,
            across every project. Switch tools freely. Never re-explain yourself.
          </p>

          <div className="mt-9 max-w-md">
            <CopyCommand command="/plugin marketplace add SirCharan/second-brain" />
            <div className="mt-3 flex items-center gap-5 text-sm text-ink-faint">
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
            </div>
          </div>
        </div>

        {/* honest artifact, overlapping the graph — layer crossing + bleed */}
        <div className="mt-14 max-w-md lg:mt-16 lg:max-w-lg lg:translate-x-[42%]">
          <Terminal label="~/second-brain-vault" status="local · yours">
            <div className="space-y-1 text-ink-dim">
              <p>
                <span className="text-accent">+ captured</span>{" "}
                <span className="text-ink">acme/rate-limit.md</span>
              </p>
              <p className="pl-6 text-ink-faint">“back off 429s with jittered retry”</p>
              <p className="pt-2">
                <span className="text-ink">$ /clear</span>{" "}
                <span className="text-ink-faint">— context freed</span>
              </p>
              <p className="pt-2 text-ink-faint">new session · a different model</p>
              <p>
                <span className="text-accent">↳ recalled</span>{" "}
                <span className="text-ink">acme/rate-limit.md</span>{" "}
                <span className="text-accent">✓</span>
              </p>
              <p className="pl-6 text-ink-faint">surfaced before you asked</p>
            </div>
          </Terminal>
        </div>
      </div>
    </section>
  );
}
