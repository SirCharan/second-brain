import CopyCommand from "./CopyCommand";
import { GitHubMark } from "./Mark";

const REPO = "https://github.com/SirCharan/second-brain";
const INSTALL = "/plugin marketplace add SirCharan/second-brain";

export default function Footer() {
  return (
    <footer className="relative overflow-hidden border-t border-line px-6 pt-24 sm:px-10">
      <div className="mx-auto max-w-6xl">
        <div className="grid gap-12 lg:grid-cols-[1fr_auto] lg:items-end">
          <div>
            <p className="font-display text-[clamp(2.1rem,4.8vw,3.6rem)] leading-[1.05]">
              Own your mind.
              <br />
              <span className="text-accent">Rent the model.</span>
            </p>
            <p className="mt-4 max-w-md text-[15px] leading-relaxed text-ink-dim">
              Install the plugin, keep working. The vault grows under you.
            </p>
            <div className="mt-8 max-w-md">
              <CopyCommand command={INSTALL} />
            </div>
          </div>

          <div className="flex flex-col gap-3 text-sm text-ink-dim sm:flex-row sm:flex-wrap lg:flex-col lg:items-end lg:text-right">
            <a
              href={REPO}
              target="_blank"
              rel="noreferrer"
              className="flex items-center gap-2 transition-colors hover:text-ink lg:justify-end"
            >
              <GitHubMark size={15} />
              GitHub
            </a>
            <a
              href={`${REPO}/blob/main/POSITIONING.md`}
              target="_blank"
              rel="noreferrer"
              className="transition-colors hover:text-ink"
            >
              Why we built it
            </a>
            <a
              href={`${REPO}#install`}
              target="_blank"
              rel="noreferrer"
              className="transition-colors hover:text-ink"
            >
              Install guide
            </a>
            <a href="/" className="transition-colors hover:text-ink">
              Classic landing
            </a>
            <span className="text-ink-faint">Apache-2.0</span>
          </div>
        </div>
      </div>

      <div className="mt-20 flex items-end justify-center" aria-hidden="true">
        <span className="translate-y-[0.12em] select-none font-display text-[clamp(3.4rem,18vw,14rem)] leading-none tracking-tight text-ink/[0.06]">
          second-brain
        </span>
      </div>
    </footer>
  );
}
