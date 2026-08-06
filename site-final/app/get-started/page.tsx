import type { Metadata } from "next";
import Nav from "../components/Nav";
import Footer from "../components/Footer";
import CopyCommand from "../components/CopyCommand";

const REPO = "https://github.com/SirCharan/second-brain";
const INSTALL_SH = "curl -fsSL https://charandeepkapoor.com/second-brain/install.sh | bash";
const INSTALL_PS1 = "irm https://charandeepkapoor.com/second-brain/install.ps1 | iex";
const DMG = `${REPO}/releases/latest/download/Second-Brain-Setup.dmg`;

export const metadata: Metadata = {
  title: "get started — second brain",
  description:
    "Install second-brain, run the wizard, verify the hooks, and connect Claude Desktop, Cursor and Obsidian.",
  alternates: {
    canonical: "https://charandeepkapoor.com/second-brain/get-started",
  },
};

function Step({
  n,
  kicker,
  title,
  children,
}: {
  n: string;
  kicker: string;
  title: string;
  children: React.ReactNode;
}) {
  return (
    <section className="border-t border-line px-6 py-14 sm:px-10 sm:py-16">
      <div className="mx-auto max-w-6xl">
        {/* 44rem fits the install command on one line; prose keeps a 2xl reading measure */}
        <div className="max-w-[44rem] [&>p]:max-w-2xl">
          <p className="font-mono text-[11px] tracking-[0.18em] text-accent uppercase">
            {n} · {kicker}
          </p>
          <h2 className="mt-3 font-display text-[clamp(1.6rem,3vw,2.3rem)] leading-[1.1]">
            {title}
          </h2>
          {children}
        </div>
      </div>
    </section>
  );
}

export default function GetStarted() {
  return (
    <>
      <Nav />
      <main>
        <header className="px-6 pb-14 pt-32 sm:px-10 sm:pb-16 sm:pt-40">
          <div className="mx-auto max-w-6xl">
            <p className="font-mono text-[11px] tracking-[0.18em] text-accent uppercase">
              get started
            </p>
            <h1 className="mt-4 max-w-2xl font-display text-[clamp(2.1rem,5vw,3.4rem)] leading-[1.05]">
              Six steps. Most of them optional.
            </h1>
            <p className="mt-5 max-w-xl text-ink-dim">
              Install, run the wizard, verify. Steps 04–06 connect the other
              apps when you want them.
            </p>
          </div>
        </header>

        <Step n="01" kicker="install" title="One command">
          <p className="mt-4 text-[15px] leading-relaxed text-ink-dim">
            macOS, Linux and WSL2:
          </p>
          <div className="mt-4">
            <CopyCommand command={INSTALL_SH} />
          </div>
          <p className="mt-5 text-[15px] leading-relaxed text-ink-dim">
            Windows, in PowerShell:
          </p>
          <div className="mt-4">
            <CopyCommand command={INSTALL_PS1} />
          </div>
          <p className="mt-7 text-[15px] leading-relaxed text-ink-dim">
            Alternative — install as a Claude Code plugin instead:
          </p>
          <div className="mt-4 space-y-2">
            <CopyCommand command="/plugin marketplace add SirCharan/second-brain" prompt=">" />
            <CopyCommand command="/plugin install second-brain" prompt=">" />
          </div>
          <p className="mt-3 text-sm leading-relaxed text-ink-faint">
            Pick one method — running both registers every hook twice.
          </p>
          <p className="mt-7 text-[15px] leading-relaxed text-ink-dim">
            There&apos;s also a Mac app:{" "}
            <a href={DMG} className="text-ink underline decoration-line-strong underline-offset-4 transition-colors hover:decoration-accent">
              Download the .dmg
            </a>
            . It&apos;s unsigned: right-click the app → Open the first time.
          </p>
        </Step>

        <Step n="02" kicker="setup" title="Run the wizard">
          <p className="mt-4 text-[15px] leading-relaxed text-ink-dim">
            The installer hands off to it automatically in your terminal. It
            asks which projects to track, offers the starter pack (22 skills),
            and optional semantic recall. Plugin-path users run it manually:
          </p>
          <div className="mt-4">
            <CopyCommand command="python3 ~/.claude/skills/second-brain/scripts/setup.py" />
          </div>
        </Step>

        <Step n="03" kicker="verify" title="Check it's wired into Claude Code">
          <p className="mt-4 text-[15px] leading-relaxed text-ink-dim">
            Restart Claude Code so the hooks load, then prove capture works —
            this writes a synthetic session through the real hooks:
          </p>
          <div className="mt-4">
            <CopyCommand command="python3 ~/.claude/skills/second-brain/scripts/setup.py --verify-capture" />
          </div>
          <p className="mt-4 text-[15px] leading-relaxed text-ink-dim">
            For the full checkup:
          </p>
          <div className="mt-4">
            <CopyCommand command="python3 ~/.claude/skills/second-brain/scripts/doctor.py" />
          </div>
          <p className="mt-4 text-[15px] leading-relaxed text-ink-dim">
            Doctor reports what&apos;s configured and prints the exact fix for
            anything that isn&apos;t. A captured session looks like a dated
            note in <code className="font-mono text-sm text-ink">Daily/</code>{" "}
            plus a &ldquo;where you left off&rdquo; digest at the next session
            start.
          </p>
        </Step>

        <Step n="04" kicker="connect" title="Claude Desktop &amp; Cursor">
          <p className="mt-4 text-[15px] leading-relaxed text-ink-dim">
            A small MCP server gives both apps recall and capture. Preview the
            config, then apply it:
          </p>
          <div className="mt-4 space-y-2">
            <CopyCommand command="python3 ~/.claude/mcp/mcp-setup.py" />
            <CopyCommand command="python3 ~/.claude/mcp/mcp-setup.py --write" />
          </div>
          <p className="mt-3 text-sm leading-relaxed text-ink-faint">
            Restart Claude Desktop and Cursor after.
          </p>
        </Step>

        <Step n="05" kicker="remote · experimental" title="ChatGPT and claude.ai">
          <p className="mt-4 text-[15px] leading-relaxed text-ink-dim">
            Optional and read-only: a remote MCP endpoint runs behind a tunnel
            so ChatGPT and claude.ai can search the vault. It&apos;s still
            experimental — setup lives in{" "}
            <a
              href={`${REPO}/blob/main/mcp/README.md`}
              target="_blank"
              rel="noreferrer"
              className="text-ink underline decoration-line-strong underline-offset-4 transition-colors hover:decoration-accent"
            >
              mcp/README.md
            </a>
            .
          </p>
        </Step>

        <Step n="06" kicker="browse" title="Open the vault in Obsidian">
          <p className="mt-4 text-[15px] leading-relaxed text-ink-dim">
            Point Obsidian at{" "}
            <code className="font-mono text-sm text-ink">
              ~/.claude/second-brain-vault
            </code>{" "}
            (or wherever <code className="font-mono text-sm text-ink">$CLAUDE_MEMORY_DIR</code>{" "}
            points). It&apos;s plain Markdown either way; the graph view is
            prewired by the starter pack&apos;s{" "}
            <code className="font-mono text-sm text-ink">.obsidian</code>{" "}
            config.
          </p>
        </Step>

        <section className="border-t border-line px-6 py-14 sm:px-10">
          <div className="mx-auto max-w-6xl">
            <div className="flex flex-wrap items-center gap-x-7 gap-y-1 text-sm text-ink-dim">
              <a
                href={REPO}
                target="_blank"
                rel="noreferrer"
                className="py-1.5 transition-colors hover:text-ink"
              >
                GitHub
              </a>
              <a
                href={`${REPO}/blob/main/POSITIONING.md`}
                target="_blank"
                rel="noreferrer"
                className="py-1.5 transition-colors hover:text-ink"
              >
                Why we built it
              </a>
              {/* plain <a>: cross-page nav through the Multi-Zone proxy — next/link prefetch 404s (?_rsc=) */}
              <a href="/second-brain/" className="py-1.5 transition-colors hover:text-ink">
                ← back home
              </a>
            </div>
          </div>
        </section>
      </main>
      <Footer />
    </>
  );
}
