import { Mark, GitHubMark } from "./Mark";

const REPO = "https://github.com/SirCharan/second-brain";

export default function Nav() {
  return (
    <nav className="nav-in fixed inset-x-0 top-0 z-50 flex justify-center px-4 pt-4">
      <div className="flex w-full max-w-5xl items-center justify-between rounded-full border border-line bg-surface/60 py-2.5 pl-4 pr-2.5 backdrop-blur-md">
        <a href="#top" className="flex items-center gap-2.5">
          <Mark />
          <span className="font-display text-lg leading-none">second-brain</span>
        </a>
        <div className="flex items-center gap-1">
          <a
            href="#how"
            className="hidden rounded-full px-3.5 py-1.5 text-sm text-ink-dim transition-colors hover:text-ink sm:block"
          >
            How it works
          </a>
          <a
            href="#compare"
            className="hidden rounded-full px-3.5 py-1.5 text-sm text-ink-dim transition-colors hover:text-ink sm:block"
          >
            Compare
          </a>
          <a
            href={REPO}
            target="_blank"
            rel="noreferrer"
            className="flex items-center gap-2 rounded-full border border-line-strong px-3.5 py-1.5 text-sm text-ink transition-colors hover:bg-surface-2"
          >
            <GitHubMark />
            GitHub
          </a>
        </div>
      </div>
    </nav>
  );
}
