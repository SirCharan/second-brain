/**
 * Before / after: session bloat vs vault on disk.
 * Simpler than site-v2 ContextStory — static, scannable, no phase machine.
 */

function Bar({
  label,
  value,
  maxLabel,
  fill,
  warn = false,
}: {
  label: string;
  value: number;
  maxLabel: string;
  fill: string;
  warn?: boolean;
}) {
  return (
    <div>
      <div className="mb-1.5 flex items-baseline justify-between gap-3 text-xs">
        <span className="text-ink-faint">{label}</span>
        <span className={warn ? "text-accent" : "text-ink-dim"}>{maxLabel}</span>
      </div>
      <div className="h-1.5 overflow-hidden rounded-full bg-surface-2">
        <div
          className="h-full rounded-full transition-[width]"
          style={{ width: `${Math.min(100, value)}%`, background: fill }}
        />
      </div>
    </div>
  );
}

export default function ContextTax() {
  return (
    <section id="context" className="border-t border-line px-6 py-24 sm:px-10 sm:py-28">
      <div className="mx-auto max-w-6xl">
        <div className="max-w-2xl">
          <p className="font-mono text-[11px] tracking-[0.14em] text-ink-faint uppercase">
            The context tax
          </p>
          <h2 className="mt-3 font-display text-[clamp(2rem,4vw,3.1rem)] leading-[1.05]">
            Fill. Compact. Clear.
            <br />
            <span className="text-ink-dim">Or write it to disk.</span>
          </h2>
          <p className="mt-5 max-w-xl text-base leading-relaxed text-ink-dim">
            Long chats re-send their history on every turn. Past half full, you pay for
            bloat you already know. second-brain puts the hard parts in Markdown so the
            vault grows and the window stays light.
          </p>
        </div>

        <div className="mt-14 grid gap-4 lg:grid-cols-2">
          {/* WITHOUT */}
          <article className="flex flex-col rounded-2xl border border-line bg-surface/40 p-6 sm:p-7">
            <div className="flex items-start justify-between gap-3">
              <div>
                <p className="font-mono text-[10px] tracking-[0.12em] text-ink-faint uppercase">
                  Without second-brain
                </p>
                <h3 className="mt-1.5 font-display text-xl leading-snug">
                  Everything lives in the window
                </h3>
              </div>
              <span className="shrink-0 rounded-md border border-line px-2 py-1 font-mono text-[10px] text-ink-faint">
                session working
              </span>
            </div>

            <div className="mt-8 space-y-5">
              <Bar
                label="session / context"
                value={52}
                maxLabel="52%"
                fill="var(--color-accent)"
                warn
              />
              <Bar
                label="chat memory (vendor)"
                value={45}
                maxLabel="45%"
                fill="color-mix(in oklab, var(--color-ink-dim) 55%, transparent)"
              />
            </div>

            <div className="mt-7 rounded-xl border border-line bg-bg/50 p-4">
              <div className="flex items-center justify-between text-xs text-ink-faint">
                <span>~/vault (Obsidian)</span>
                <span>size 0.0 KB</span>
              </div>
              <p className="mt-4 text-sm text-ink-faint">nothing on disk — all in the window</p>
            </div>

            <div className="mt-4 rounded-xl border border-line bg-bg/50 p-4 font-mono text-[13px] leading-relaxed text-ink-dim">
              <div className="mb-2 flex justify-between text-[11px] text-ink-faint">
                <span>session transcript</span>
                <span className="text-accent">re-carry taxed</span>
              </div>
              <p>debugging rate-limit on the API…</p>
              <p>jittered retry on 429 works</p>
              <p>auth edge case on token refresh</p>
            </div>

            <p className="mt-auto border-t border-line pt-5 text-sm text-ink-faint">
              History stays in the chat. Nothing hits disk.
            </p>
          </article>

          {/* WITH */}
          <article className="flex flex-col rounded-2xl border border-line-strong bg-surface/60 p-6 shadow-[inset_0_0_0_1px_color-mix(in_oklab,var(--color-accent)_12%,transparent)] sm:p-7">
            <div className="flex items-start justify-between gap-3">
              <div>
                <p className="font-mono text-[10px] tracking-[0.12em] text-accent uppercase">
                  With second-brain
                </p>
                <h3 className="mt-1.5 font-display text-xl leading-snug">
                  Vault rises. Session stays light.
                </h3>
              </div>
              <span className="shrink-0 rounded-md border border-accent/30 bg-accent/10 px-2 py-1 font-mono text-[10px] text-accent">
                capturing
              </span>
            </div>

            <div className="mt-8 space-y-5">
              <Bar
                label="session / context"
                value={28}
                maxLabel="28%"
                fill="var(--color-accent)"
              />
              <div>
                <div className="mb-1.5 flex items-baseline justify-between gap-3 text-xs">
                  <span className="text-ink-faint">Obsidian vault</span>
                  <span className="text-ink-dim">2 notes · 4.2 KB</span>
                </div>
                <div className="h-1.5 overflow-hidden rounded-full bg-surface-2">
                  <div
                    className="h-full rounded-full bg-accent"
                    style={{ width: "38%" }}
                  />
                </div>
              </div>
            </div>

            <div className="mt-7 rounded-xl border border-line bg-bg/50 p-4 font-mono text-[13px]">
              <div className="mb-3 flex items-center justify-between text-[11px] text-ink-faint">
                <span>~/vault (Obsidian)</span>
                <span>
                  size <span className="text-accent">4.2 KB</span>
                </span>
              </div>
              <p className="text-accent">+ Daily/2026-07-21.md</p>
              <p className="text-accent">+ acme/rate-limit.md</p>
              <p className="mt-2 text-ink-faint">→ wrote Daily/2026-07-21.md</p>
            </div>

            <div className="mt-4 rounded-xl border border-line bg-bg/50 p-4 font-mono text-[13px] leading-relaxed text-ink-dim">
              <div className="mb-2 flex justify-between text-[11px] text-ink-faint">
                <span>session transcript</span>
                <span className="text-accent">re-carry lean</span>
              </div>
              <p>debugging rate-limit on the API…</p>
              <p>jittered retry on 429 works</p>
              <p>auth edge case on token refresh</p>
            </div>

            <p className="mt-auto border-t border-line pt-5 text-sm text-ink-dim">
              Work happens. Notes land in Obsidian. Session stays thin.
            </p>
          </article>
        </div>

        <p className="mt-6 max-w-2xl text-sm text-ink-faint">
          Same work both sides. Left: the session swells. Right: notes stream into
          Obsidian while context stays under the tax line.
        </p>
      </div>
    </section>
  );
}
