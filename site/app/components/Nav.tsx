import { Mark, GitHubMark } from "./Mark";

const REPO = "https://github.com/SirCharan/second-brain";

export default function Nav({ mode }: { mode: "ambient" | "interactive" }) {
  return (
    <nav className="nav-in fixed inset-x-0 top-0 z-50 flex justify-center px-4 pt-4">
      <div className="flex w-full max-w-5xl items-center justify-between rounded-full border border-line bg-surface/55 py-2.5 pl-4 pr-2.5 backdrop-blur-md">
        <a href="/" className="flex items-center gap-2.5">
          <Mark />
          <span className="font-display text-lg leading-none">second-brain</span>
        </a>
        <div className="flex items-center gap-1.5">
          {/* graph-mode toggle — the two versions, active shown by weight+color, no dot */}
          <div className="mr-1 hidden items-center rounded-full border border-line p-0.5 text-sm sm:flex">
            <a
              href="/"
              className={`rounded-full px-3 py-1 transition-colors ${
                mode === "ambient" ? "bg-surface-2 text-ink" : "text-ink-faint hover:text-ink-dim"
              }`}
            >
              ambient
            </a>
            <a
              href="/live"
              className={`rounded-full px-3 py-1 transition-colors ${
                mode === "interactive" ? "bg-surface-2 text-ink" : "text-ink-faint hover:text-ink-dim"
              }`}
            >
              interactive
            </a>
          </div>
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
