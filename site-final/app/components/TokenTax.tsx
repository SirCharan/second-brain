/**
 * Cost of re-carrying context past 50% on a 1M window.
 * Same math as site-v2, fewer cards, one clear takeaway.
 */

const WINDOW = 1_000_000;
const BASELINE = 50;
const PRICE = 5; // $/MTok input, Claude Opus 4.8
const Q_DAY = 40;
const DAYS_MO = 22;

const ROWS = [60, 70, 80, 90, 100] as const;

function extraTok(pct: number) {
  return Math.max(0, Math.round((WINDOW * (pct - BASELINE)) / 100));
}
function extraUsd(pct: number) {
  return (extraTok(pct) / 1_000_000) * PRICE;
}
function money(n: number) {
  return n.toLocaleString("en-US", {
    style: "currency",
    currency: "USD",
    minimumFractionDigits: n % 1 === 0 ? 0 : 2,
    maximumFractionDigits: 2,
  });
}

export default function TokenTax() {
  const at90 = {
    extra: extraTok(90),
    perQ: extraUsd(90),
    perDay: extraUsd(90) * Q_DAY,
    perMo: extraUsd(90) * Q_DAY * DAYS_MO,
  };

  return (
    <section id="tax" className="border-t border-line px-6 py-24 sm:px-10 sm:py-28">
      <div className="mx-auto max-w-6xl">
        <div className="max-w-2xl">
          <p className="font-mono text-[11px] tracking-[0.14em] text-ink-faint uppercase">
            Past 50% on a 1M window
          </p>
          <h2 className="mt-3 font-display text-[clamp(2rem,4vw,3.1rem)] leading-[1.05]">
            Every query past half full
            <br />
            <span className="text-ink-dim">re-pays for history.</span>
          </h2>
          <p className="mt-5 max-w-xl text-base leading-relaxed text-ink-dim">
            On a 1M-token window, everything above 50% is optional bloat you re-send
            each turn. Math:{" "}
            <code className="font-mono text-sm text-ink">
              extra = 1M × (usage% − 50%)
            </code>
            . Prices use Claude Opus 4.8 input at $5/MTok. Output cost is separate.
          </p>
        </div>

        {/* three big numbers — one idea each */}
        <div className="mt-12 grid gap-3 sm:grid-cols-3">
          <Stat
            label="at 90% context"
            value="400k"
            hint="extra tokens re-sent every query"
          />
          <Stat
            label="extra cost / query"
            value={money(at90.perQ)}
            hint="Opus 4.8 · $5/MTok input only"
          />
          <Stat
            label="saved if you stay ≤50%"
            value={`${money(at90.perDay)}/day`}
            hint={`${Q_DAY} queries/day · 90% → ≤50%`}
            hot
          />
        </div>

        <div className="mt-10 overflow-x-auto rounded-2xl border border-line">
          <table className="w-full min-w-[640px] border-collapse text-left text-sm">
            <thead>
              <tr className="border-b border-line bg-surface/50">
                <th className="px-4 py-3.5 font-normal text-ink-faint sm:px-5">
                  Context used
                </th>
                <th className="px-4 py-3.5 font-normal text-ink-faint">
                  Extra tokens / query
                </th>
                <th className="px-4 py-3.5 font-normal text-ink-faint">Extra $ / query</th>
                <th className="px-4 py-3.5 font-normal text-ink-faint">
                  Extra $ / day
                  <span className="mt-0.5 block text-[11px] text-ink-faint/80">
                    {Q_DAY} queries
                  </span>
                </th>
                <th className="px-4 py-3.5 font-normal text-accent sm:pr-5">
                  Kept with second-brain
                  <span className="mt-0.5 block text-[11px] text-ink-faint">
                    stay ≤50% · /mo ({DAYS_MO}d)
                  </span>
                </th>
              </tr>
            </thead>
            <tbody>
              {ROWS.map((pct) => {
                const tok = extraTok(pct);
                const q = extraUsd(pct);
                const day = q * Q_DAY;
                const mo = day * DAYS_MO;
                return (
                  <tr key={pct} className="border-t border-line">
                    <td className="px-4 py-3.5 text-ink sm:px-5">
                      <span className="font-display text-base">{pct}%</span>
                      <span className="ml-2 text-ink-faint">
                        ({(WINDOW * pct) / 100 / 1000}k carried)
                      </span>
                    </td>
                    <td className="px-4 py-3.5 font-mono text-ink-dim">
                      +{tok.toLocaleString()}
                    </td>
                    <td className="px-4 py-3.5 font-mono text-ink-dim">+{money(q)}</td>
                    <td className="px-4 py-3.5 font-mono text-ink-dim">+{money(day)}</td>
                    <td className="px-4 py-3.5 font-mono text-accent sm:pr-5">
                      {money(mo)}
                      <span className="text-ink-faint"> /mo</span>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>

        <div className="mt-8 grid gap-6 lg:grid-cols-[1fr_auto] lg:items-end">
          <p className="max-w-2xl text-sm leading-relaxed text-ink-faint">
            <span className="text-ink-dim">How to read this.</span> At 90% you re-send
            900k tokens every query. Only 500k sits under the 50% line — the other 400k
            is pure tax ({money(at90.perQ)} / query). second-brain keeps durable memory
            on disk and recalls a small slice, so you can{" "}
            <code className="font-mono text-ink-dim">/clear</code> and live under 50%.
            “Saved” is that input tax going to zero — not free tokens, just not re-paying
            Opus for history you already wrote down.
          </p>
          <aside className="rounded-2xl border border-line-strong bg-surface/50 px-6 py-5 text-left sm:min-w-[220px]">
            <p className="font-mono text-[11px] text-ink-faint">example: 90% → ≤50%</p>
            <p className="mt-1 font-display text-3xl text-accent">
              {money(at90.perMo)}
              <span className="text-xl text-ink-dim">/mo</span>
            </p>
            <p className="mt-1 text-sm text-ink-dim">
              back in your pocket at {Q_DAY} queries/day
            </p>
          </aside>
        </div>
      </div>
    </section>
  );
}

function Stat({
  label,
  value,
  hint,
  hot = false,
}: {
  label: string;
  value: string;
  hint: string;
  hot?: boolean;
}) {
  return (
    <div
      className={`rounded-2xl border p-5 sm:p-6 ${
        hot
          ? "border-line-strong bg-surface-2/50 shadow-[inset_0_0_0_1px_color-mix(in_oklab,var(--color-accent)_14%,transparent)]"
          : "border-line bg-surface/40"
      }`}
    >
      <p className="font-mono text-[11px] text-ink-faint">{label}</p>
      <p
        className={`mt-2 font-display text-[clamp(2rem,4vw,2.75rem)] leading-none ${
          hot ? "text-accent" : "text-ink"
        }`}
      >
        {value}
      </p>
      <p className="mt-2 text-sm text-ink-dim">{hint}</p>
    </div>
  );
}
