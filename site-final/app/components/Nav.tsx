import { Mark, GitHubMark } from "./Mark";

const REPO = "https://github.com/SirCharan/second-brain";

export default function Nav() {
  return (
    <nav className="fixed inset-x-0 top-0 z-50 flex justify-center px-4 pt-4">
      <div className="flex w-full max-w-6xl items-center justify-between rounded-2xl border border-line bg-surface/55 py-2.5 pl-4 pr-2.5 backdrop-blur-md">
        <a href="#top" className="flex items-center gap-2.5">
          <Mark />
          <span className="font-display text-lg leading-none tracking-tight">
            second-brain
          </span>
        </a>
        <div className="flex items-center gap-1 sm:gap-1.5">
          <a
            href="#context"
            className="hidden rounded-lg px-3 py-1.5 text-sm text-ink-dim transition-colors hover:text-ink md:inline"
          >
            Context tax
          </a>
          <a
            href="#compare"
            className="hidden rounded-lg px-3 py-1.5 text-sm text-ink-dim transition-colors hover:text-ink sm:inline"
          >
            Compare
          </a>
          <a
            href={REPO}
            target="_blank"
            rel="noreferrer"
            className="flex items-center gap-2 rounded-lg border border-line-strong bg-surface-2/40 px-3.5 py-1.5 text-sm text-ink transition-colors hover:bg-surface-2"
          >
            <GitHubMark />
            <span className="hidden sm:inline">GitHub</span>
          </a>
        </div>
      </div>
    </nav>
  );
}
