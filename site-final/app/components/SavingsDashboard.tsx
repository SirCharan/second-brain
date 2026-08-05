import savings from "../data/savings.json";

/**
 * The receipts for the TokenTax section above it: what the vault has actually
 * saved on ck's own machine. app/data/savings.json is recomputed daily by
 * scripts/compute-savings.mjs (launchd) and committed, so every deploy carries
 * a fresh number and the git history of the file is the audit trail.
 */

const SCRIPT_URL =
  "https://github.com/SirCharan/second-brain/blob/main/site-final/scripts/compute-savings.mjs";

function tok(n: number): string {
  if (Math.abs(n) >= 1e6) return `${(n / 1e6).toFixed(1)}M`;
  if (Math.abs(n) >= 1e3) return `${Math.round(n / 1e3)}k`;
  return `${n}`;
}

function Spark({ points }: { points: { date: string; net_tokens: number }[] }) {
  const W = 560;
  const H = 120;
  const PAD = 8;
  if (points.length === 0) return null;
  const max = Math.max(...points.map((p) => p.net_tokens), 1);
  const x = (i: number) =>
    points.length === 1 ? W / 2 : PAD + (i * (W - PAD * 2)) / (points.length - 1);
  const y = (v: number) => H - PAD - (v / max) * (H - PAD * 2);
  const line = points.map((p, i) => `${x(i)},${y(p.net_tokens)}`).join(" ");
  const last = points[points.length - 1];

  return (
    <svg
      viewBox={`0 0 ${W} ${H}`}
      className="h-24 w-full sm:h-28"
      role="img"
      aria-label={`Net tokens saved by day, ${points[0].date} to ${last.date}`}
    >
      {points.length > 1 && (
        <>
          <polygon
            points={`${PAD},${H - PAD} ${line} ${x(points.length - 1)},${H - PAD}`}
            fill="color-mix(in oklab, var(--color-accent) 10%, transparent)"
          />
          <polyline
            points={line}
            fill="none"
            stroke="var(--color-accent)"
            strokeWidth="2"
            strokeLinecap="round"
            strokeLinejoin="round"
          />
        </>
      )}
      <circle
        cx={x(points.length - 1)}
        cy={y(last.net_tokens)}
        r="3.5"
        fill="var(--color-accent)"
      />
    </svg>
  );
}

export default function SavingsDashboard() {
  const s = savings;
  const days = Math.max(
    1,
    Math.round((Date.parse(s.computed_at) - Date.parse(s.since)) / 86_400_000)
  );
  const computed = s.computed_at.slice(0, 10);
  const a = s.assumptions;

  return (
    <section id="saved" className="border-t border-line px-6 py-24 sm:px-10 sm:py-28">
      <div className="mx-auto max-w-6xl">
        <div className="flex flex-wrap items-end justify-between gap-6">
          <div className="max-w-2xl">
            <p className="font-mono text-[11px] tracking-[0.14em] text-ink-faint uppercase">
              Measured on my machine · recomputed daily
            </p>
            <h2 className="mt-3 font-display text-[clamp(2rem,4vw,3.1rem)] leading-[1.05]">
              The tax above, refused.
              <br />
              <span className="text-ink-dim">This vault&rsquo;s running receipt.</span>
            </h2>
          </div>
          <p className="text-sm text-ink-faint">
            since {s.since} · computed {computed}
          </p>
        </div>

        <div className="mt-12 grid gap-3 sm:grid-cols-3">
          <div className="rounded-2xl border border-line-strong bg-surface-2/50 p-5 shadow-[inset_0_0_0_1px_color-mix(in_oklab,var(--color-accent)_14%,transparent)] sm:p-6">
            <p className="font-mono text-[11px] text-ink-faint">net tokens saved</p>
            <p className="mt-2 font-display text-[clamp(2rem,4vw,2.75rem)] leading-none tracking-tight text-accent">
              {tok(s.net_saved_tokens)}
            </p>
            <p className="mt-2 text-sm text-ink-dim">
              after paying for its own recall injections
            </p>
          </div>
          <div className="rounded-2xl border border-line bg-surface/40 p-5 sm:p-6">
            <p className="font-mono text-[11px] text-ink-faint">worth, at Opus input</p>
            <p className="mt-2 font-display text-[clamp(2rem,4vw,2.75rem)] leading-none tracking-tight text-ink">
              ${s.usd_saved.toLocaleString("en-US")}
            </p>
            <p className="mt-2 text-sm text-ink-dim">${a.usd_per_mtok}/MTok · input only</p>
          </div>
          <div className="rounded-2xl border border-line bg-surface/40 p-5 sm:p-6">
            <p className="font-mono text-[11px] text-ink-faint">of everything I ran</p>
            <p className="mt-2 font-display text-[clamp(2rem,4vw,2.75rem)] leading-none tracking-tight text-ink">
              {s.pct_of_throughput}%
            </p>
            <p className="mt-2 text-sm text-ink-dim">
              {tok(s.throughput_tokens)} tokens through Claude Code in {days} days
            </p>
          </div>
        </div>

        <div className="mt-8 rounded-2xl border border-line bg-surface/40 p-5 sm:p-6">
          <div className="flex flex-wrap items-baseline justify-between gap-2">
            <p className="font-mono text-[11px] text-ink-faint">
              net saved, day by day
            </p>
            <p className="text-sm text-ink-dim">
              {s.sessions.toLocaleString()} sessions · {s.notes.toLocaleString()} notes ·{" "}
              {s.turns.toLocaleString()} captured turns
            </p>
          </div>
          <div className="mt-4">
            <Spark points={s.history} />
          </div>
          {s.history.length < 3 && (
            <p className="mt-2 text-sm text-ink-faint">
              Day {s.history.length} of the series — the line grows as the daily job
              recommits this file.
            </p>
          )}
        </div>

        <p className="mt-8 max-w-3xl text-sm leading-relaxed text-ink-faint">
          <span className="text-ink-dim">The math, in the open.</span> Savings are an
          estimate, not a meter: {a.hit_rate * 100}% of sessions assumed to dodge a{" "}
          {tok(a.tokens_per_hit)}-token re-discovery, {a.resume_rate * 100}% to skip{" "}
          {tok(a.tokens_per_resume)} of context rebuilding, {a.compaction_rate * 100}% to
          avoid a {tok(a.tokens_per_compaction)}-token compaction. Injection cost (
          {tok(s.injection_cost_tokens)} after a {a.cache_mult}× cached-prefix discount)
          is subtracted before anything is claimed. Throughput = transcript bytes ÷{" "}
          {a.bytes_per_token}. Every constant lives in{" "}
          <a
            href={SCRIPT_URL}
            target="_blank"
            rel="noreferrer"
            className="text-ink-dim underline decoration-line-strong underline-offset-4 transition-colors hover:text-ink"
          >
            compute-savings.mjs
          </a>{" "}
          — audit it, tune it, or run it on your own vault.
        </p>
      </div>
    </section>
  );
}
