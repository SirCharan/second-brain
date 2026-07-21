import Terminal from "./Terminal";

export default function HowItWorks() {
  return (
    <section id="how" className="px-6 py-24 sm:px-10 sm:py-32">
      <div className="mx-auto max-w-6xl">
        <div className="max-w-2xl">
          <p className="font-mono text-[11px] tracking-[0.14em] text-ink-faint uppercase">
            the loop
          </p>
          <h2 className="mt-3 font-display text-[clamp(2rem,3.8vw,3.1rem)] leading-[1.05]">
            Write once.
            <br />
            Recall anywhere.
          </h2>
          <p className="mt-4 max-w-xl text-base leading-relaxed text-ink-dim sm:text-lg">
            Memory lives in the vault, not the chat. Clear the window, switch tools,
            come back weeks later. The notes are still there.
          </p>
        </div>

        <ol className="mt-16 grid gap-6 lg:grid-cols-3">
          <Step n="1" label="Capture">
            <Terminal label="session · any model" status="working">
              <div className="space-y-1 text-ink-dim">
                <p className="text-ink-faint">you ship a fix together…</p>
                <p className="pt-1">
                  <span className="text-accent">+ captured</span>{" "}
                  <span className="text-ink">acme/rate-limit.md</span>
                </p>
                <p className="pl-5 text-ink-faint">&ldquo;jittered retry on 429&rdquo;</p>
              </div>
            </Terminal>
            <p className="mt-4 text-sm leading-relaxed text-ink-dim">
              Each session lands as a note you can open, edit, and link.
            </p>
          </Step>

          <Step n="2" label="Free the window">
            <Terminal label="context" status="freed">
              <div className="space-y-1 text-ink-dim">
                <p>
                  <span className="text-ink">$ /clear</span>
                </p>
                <p className="text-ink-faint">window empty. history gone.</p>
                <p className="pt-1 text-ink-faint">no compaction pause.</p>
                <p className="text-ink-faint">vault still holds the fix.</p>
              </div>
            </Terminal>
            <p className="mt-4 text-sm leading-relaxed text-ink-dim">
              Stop paying tokens to re-carry a bloated transcript every turn.
            </p>
          </Step>

          <Step n="3" label="Recall">
            <Terminal label="new session · different model" status="recalling">
              <div className="space-y-1 text-ink-dim">
                <p className="text-ink-faint">weeks later, another tool…</p>
                <p className="pt-1">
                  <span className="text-accent">↳ recalled</span>{" "}
                  <span className="text-ink">acme/rate-limit.md</span>{" "}
                  <span className="text-accent">✓</span>
                </p>
                <p className="pl-5 text-ink-faint">surfaced before you asked</p>
              </div>
            </Terminal>
            <p className="mt-4 text-sm leading-relaxed text-ink-dim">
              Only the relevant slice re-enters context. The rest stays on disk.
            </p>
          </Step>
        </ol>
      </div>
    </section>
  );
}

function Step({
  n,
  label,
  children,
}: {
  n: string;
  label: string;
  children: React.ReactNode;
}) {
  return (
    <li className="flex flex-col">
      <div className="mb-4 flex items-baseline gap-3">
        <span className="font-mono text-sm text-accent">{n}</span>
        <span className="font-display text-lg">{label}</span>
      </div>
      {children}
    </li>
  );
}
