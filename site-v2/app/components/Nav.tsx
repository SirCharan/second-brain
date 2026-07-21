import CopyCommand from "./CopyCommand";

export default function Nav() {
  return (
    <header className="relative z-20 mx-auto flex w-full max-w-6xl items-center justify-between gap-4 px-5 pt-8 sm:px-8 sm:pt-10">
      <a href="/" className="group flex items-baseline gap-2">
        <span className="display text-[1.35rem] leading-none tracking-tight text-fg sm:text-[1.5rem]">
          second-brain
        </span>
        <span className="hidden text-[11px] text-muted sm:inline">v2 cinema</span>
      </a>

      <nav className="flex items-center gap-3 sm:gap-4">
        <a
          href="https://github.com/SirCharan/second-brain"
          className="hidden text-sm text-fg-dim transition-colors hover:text-fg sm:inline"
          rel="noreferrer"
          target="_blank"
        >
          GitHub
        </a>
        <CopyCommand className="hidden md:inline-flex" />
        <a
          href="#install"
          className="rounded-md bg-accent px-3.5 py-2 text-sm font-medium text-[#1a1208] transition-colors hover:bg-accent-hot"
        >
          Install
        </a>
      </nav>
    </header>
  );
}
