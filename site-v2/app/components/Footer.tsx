export default function Footer() {
  return (
    <footer className="border-t border-border-soft">
      <div className="mx-auto flex max-w-6xl flex-col gap-4 px-5 py-10 sm:flex-row sm:items-center sm:justify-between sm:px-8">
        <p className="display text-lg text-fg">second-brain</p>
        <p className="text-sm text-muted">
          Local files. Any model. No account.
        </p>
        <div className="flex gap-5 text-sm text-fg-dim">
          <a
            href="https://github.com/SirCharan/second-brain"
            className="hover:text-fg"
            rel="noreferrer"
            target="_blank"
          >
            GitHub
          </a>
          <a href="#install" className="hover:text-fg">
            Install
          </a>
        </div>
      </div>
    </footer>
  );
}
