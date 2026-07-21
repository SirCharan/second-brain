"use client";

import { useEffect, useState } from "react";

/**
 * Story section: Claude Code context fills → compact or /clear burns tokens,
 * vs second-brain dumping notes into Obsidian so vault grows while the
 * session stays lean. Plus a 1M-window token economics table past 50%.
 *
 * Content is always in the DOM (no opacity-0 entrance traps).
 */

type Phase = "fill" | "pressure" | "choice" | "aftermath";

const MESSAGES = [
  "debugging rate-limit on the API…",
  "jittered retry on 429 works",
  "auth edge case on token refresh",
  "deploy notes for R2 + edge",
  "why we picked this model router",
  "session decisions for tomorrow",
];

type VaultNote = { path: string; kb: number };

const VAULT_NOTES: VaultNote[] = [
  { path: "Daily/2026-07-21.md", kb: 1.8 },
  { path: "acme/rate-limit.md", kb: 2.4 },
  { path: "auth-flow.md", kb: 3.1 },
  { path: "deploy-r2.md", kb: 1.6 },
  { path: "session/today.md", kb: 2.9 },
  { path: "lessons/retries.md", kb: 1.2 },
];

const PHASE_MS: Record<Phase, number> = {
  fill: 3400,
  pressure: 2600,
  choice: 3000,
  aftermath: 3400,
};

const PHASE_ORDER: Phase[] = ["fill", "pressure", "choice", "aftermath"];

// --- Token economics (transparent assumptions) ---
// Claude Opus 4.8 API: $5 / MTok input, $25 / MTok output (claude.com/pricing).
// Context re-carry tax is input tokens only.
const WINDOW = 1_000_000; // 1M context window
const BASELINE_PCT = 50; // "healthy" re-carry ceiling
const PRICE_PER_MTOK = 5; // Opus 4.8 input $/1M tokens
const PRICE_OUT_PER_MTOK = 25; // Opus 4.8 output (shown in footnote only)
const MODEL_LABEL = "Claude Opus 4.8";
const QUERIES_PER_DAY = 40; // heavy Claude Code day

const CTX_LEVELS = [60, 70, 80, 90, 100] as const;

function extraTokens(pct: number) {
  return Math.max(0, Math.round(WINDOW * (pct - BASELINE_PCT) / 100));
}

function extraDollars(pct: number) {
  return (extraTokens(pct) / 1_000_000) * PRICE_PER_MTOK;
}

function prefersReducedMotion() {
  if (typeof window === "undefined") return true;
  return window.matchMedia("(prefers-reduced-motion: reduce)").matches;
}

export default function ContextStory() {
  const [phase, setPhase] = useState<Phase>("fill");
  const [tick, setTick] = useState(0);
  const [reduced, setReduced] = useState(false);

  useEffect(() => {
    setReduced(prefersReducedMotion());
  }, []);

  useEffect(() => {
    if (reduced) {
      setPhase("aftermath");
      setTick(1);
      return;
    }

    let cancelled = false;
    let phaseIdx = 0;
    let timer: number;

    const run = () => {
      if (cancelled) return;
      const p = PHASE_ORDER[phaseIdx];
      setPhase(p);
      setTick((t) => t + 1);
      timer = window.setTimeout(() => {
        phaseIdx = (phaseIdx + 1) % PHASE_ORDER.length;
        run();
      }, PHASE_MS[p]);
    };

    run();
    return () => {
      cancelled = true;
      window.clearTimeout(timer);
    };
  }, [reduced]);

  const without = withoutState(phase);
  const withSb = withState(phase);

  return (
    <section
      id="context"
      aria-labelledby="context-heading"
      className="relative border-t border-border-soft"
    >
      <div className="mx-auto max-w-6xl px-5 py-20 sm:px-8 sm:py-28">
        <div className="mb-12 max-w-2xl sm:mb-16">
          <p className="mb-3 text-sm text-cool">The context tax</p>
          <h2
            id="context-heading"
            className="display text-[clamp(1.85rem,4vw,2.85rem)] leading-[1.05] text-fg"
          >
            Fill. Compact. Clear.
            <br />
            <span className="text-fg-dim">Or dump it to disk.</span>
          </h2>
          <p className="mt-5 max-w-xl text-sm leading-relaxed text-fg-dim sm:text-[15px]">
            Claude Code keeps working memory in the window. Past ~50% every turn
            re-pays for the bloat. second-brain writes the hard parts into an
            Obsidian vault as you go: vault size goes up, session size does not.
          </p>
        </div>

        <div className="grid gap-4 lg:grid-cols-2 lg:gap-5">
          <StoryPanel
            tone="bad"
            eyebrow="without second-brain"
            title="Everything lives in the window"
            state={without}
            tick={tick}
          />
          <StoryPanel
            tone="good"
            eyebrow="with second-brain"
            title="Vault rises. Session stays light."
            state={withSb}
            tick={tick}
          />
        </div>

        <p className="mt-6 text-center text-xs text-muted sm:text-left">
          Loop is automatic. Same work both sides. Left: session swells. Right:
          notes stream into Obsidian while context stays lean.
        </p>

        <TokenEconomics />
      </div>
    </section>
  );
}

type PanelState = {
  ctxPct: number;
  memPct: number;
  tokensWasted: number;
  lines: string[];
  vault: VaultNote[];
  vaultKb: number;
  writeEvent: string | null;
  badge: string;
  badgeTone: "neutral" | "warn" | "danger" | "ok";
  action: string | null;
  footer: string;
};

function withoutState(phase: Phase): PanelState {
  switch (phase) {
    case "fill":
      return {
        ctxPct: 52,
        memPct: 45,
        tokensWasted: 0,
        lines: MESSAGES.slice(0, 3),
        vault: [],
        vaultKb: 0,
        writeEvent: null,
        badge: "session working",
        badgeTone: "neutral",
        action: null,
        footer: "History stays in the chat. Nothing hits disk.",
      };
    case "pressure":
      return {
        ctxPct: 78,
        memPct: 82,
        tokensWasted: 18_400,
        lines: MESSAGES.slice(0, 5),
        vault: [],
        vaultKb: 0,
        writeEvent: null,
        badge: "past 50% · tax starts",
        badgeTone: "warn",
        action: null,
        footer: "Every query re-sends the fat history. Vault still empty.",
      };
    case "choice":
      return {
        ctxPct: 96,
        memPct: 100,
        tokensWasted: 38_200,
        lines: MESSAGES,
        vault: [],
        vaultKb: 0,
        writeEvent: null,
        badge: "must compact or /clear",
        badgeTone: "danger",
        action: "compacting… · or $ /clear",
        footer: "Slow, lossy, or wipe. Knowledge never left the window.",
      };
    case "aftermath":
      return {
        ctxPct: 6,
        memPct: 0,
        tokensWasted: 52_800,
        lines: ["(window empty)", "who were we again?"],
        vault: [],
        vaultKb: 0,
        writeEvent: null,
        badge: "amnesia + bill",
        badgeTone: "danger",
        action: null,
        footer: "Tokens spent. Plot gone. Vault still empty.",
      };
  }
}

function withState(phase: Phase): PanelState {
  switch (phase) {
    case "fill": {
      const vault = VAULT_NOTES.slice(0, 2);
      return {
        ctxPct: 28,
        memPct: 0,
        tokensWasted: 0,
        lines: MESSAGES.slice(0, 3),
        vault,
        vaultKb: sumKb(vault),
        writeEvent: "→ wrote Daily/2026-07-21.md",
        badge: "capturing",
        badgeTone: "ok",
        action: null,
        footer: "Work happens. Notes land in Obsidian. Session stays thin.",
      };
    }
    case "pressure": {
      const vault = VAULT_NOTES.slice(0, 4);
      return {
        ctxPct: 31,
        memPct: 0,
        tokensWasted: 0,
        lines: MESSAGES.slice(0, 4),
        vault,
        vaultKb: sumKb(vault),
        writeEvent: "→ wrote auth-flow.md · deploy-r2.md",
        badge: "vault rising",
        badgeTone: "ok",
        action: "session flat · vault +8.9 KB",
        footer: "More knowledge. Not more context. Under the 50% tax line.",
      };
    }
    case "choice": {
      const vault = VAULT_NOTES.slice(0, 6);
      return {
        ctxPct: 14,
        memPct: 0,
        tokensWasted: 0,
        lines: ["$ /clear", "context freed", "vault untouched"],
        vault,
        vaultKb: sumKb(vault),
        writeEvent: "→ dump complete · 6 notes on disk",
        badge: "clear is free",
        badgeTone: "ok",
        action: "dumped → Obsidian vault",
        footer: "Window empties. Disk keeps every decision.",
      };
    }
    case "aftermath": {
      const vault = VAULT_NOTES;
      return {
        ctxPct: 19,
        memPct: 0,
        tokensWasted: 0,
        lines: [
          "new session · Claude",
          "↳ recalled acme/rate-limit.md ✓",
          "↳ recalled auth-flow.md ✓",
        ],
        vault,
        vaultKb: sumKb(vault),
        writeEvent: "← recall from vault (not re-typed)",
        badge: "recalling",
        badgeTone: "ok",
        action: null,
        footer: "Pick up cold. Only the relevant notes re-enter the window.",
      };
    }
  }
}

function sumKb(notes: VaultNote[]) {
  return Math.round(notes.reduce((s, n) => s + n.kb, 0) * 10) / 10;
}

function StoryPanel({
  tone,
  eyebrow,
  title,
  state,
  tick,
}: {
  tone: "bad" | "good";
  eyebrow: string;
  title: string;
  state: PanelState;
  tick: number;
}) {
  return (
    <article
      className={[
        "flex min-h-[480px] flex-col overflow-hidden rounded-xl border bg-surface",
        tone === "good" ? "border-accent/35" : "border-border",
      ].join(" ")}
    >
      <header className="flex items-start justify-between gap-3 border-b border-border-soft px-5 py-4 sm:px-6">
        <div>
          <p
            className={[
              "text-[11px] tracking-wide uppercase",
              tone === "good" ? "text-accent" : "text-muted",
            ].join(" ")}
          >
            {eyebrow}
          </p>
          <h3 className="mt-1 text-base font-medium text-fg sm:text-lg">{title}</h3>
        </div>
        <StatusBadge label={state.badge} tone={state.badgeTone} />
      </header>

      <div className="flex flex-1 flex-col gap-4 px-5 py-5 sm:px-6">
        {/* Dual meters: session vs vault — always both so growth contrast is obvious */}
        <div className="grid gap-3 sm:grid-cols-2">
          <Meter
            label="session / context"
            value={state.ctxPct}
            tone={
              state.ctxPct >= 90
                ? "danger"
                : state.ctxPct > 50
                  ? "warn"
                  : tone === "good"
                    ? "ok"
                    : "neutral"
            }
            suffix={`${Math.round(state.ctxPct)}%`}
            markAt={50}
          />
          <Meter
            label="Obsidian vault"
            value={Math.min(100, state.vaultKb * 6)}
            tone={tone === "good" && state.vaultKb > 0 ? "ok" : "neutral"}
            suffix={
              state.vaultKb > 0
                ? `${state.vault.length} notes · ${state.vaultKb} KB`
                : "0 notes · 0 KB"
            }
          />
        </div>

        {tone === "bad" && (
          <Meter
            label="chat memory (vendor)"
            value={state.memPct}
            tone={state.memPct >= 90 ? "danger" : state.memPct > 50 ? "warn" : "neutral"}
            suffix={`${Math.round(state.memPct)}%`}
          />
        )}

        {/* Vault file list + write stream */}
        <VaultPanel
          notes={state.vault}
          vaultKb={state.vaultKb}
          writeEvent={state.writeEvent}
          tick={tick}
          emptyHint={
            tone === "bad"
              ? "nothing on disk — all in the window"
              : "waiting for capture…"
          }
        />

        {/* Session log */}
        <div className="min-h-[108px] flex-1 rounded-md border border-border-soft bg-bg px-3 py-3">
          <div className="mb-2 flex items-center justify-between">
            <p className="mono text-[10px] text-muted">session transcript</p>
            <p className="mono text-[10px] text-muted">
              re-carry{" "}
              <span
                className={
                  state.ctxPct > 50 ? "text-[color:var(--danger)]" : "text-fg-dim"
                }
              >
                {state.ctxPct > 50 ? "taxed" : "lean"}
              </span>
            </p>
          </div>
          <ul className="space-y-1.5">
            {state.lines.map((line, i) => (
              <li
                key={`${tick}-${i}-${line}`}
                className={[
                  "mono text-[12px] leading-snug sm:text-[13px]",
                  line.startsWith("$") || line.startsWith("↳")
                    ? "text-accent-hot"
                    : line.startsWith("(")
                      ? "text-muted"
                      : "text-fg-dim",
                ].join(" ")}
              >
                {line}
              </li>
            ))}
          </ul>
          {state.action && (
            <p
              className={[
                "mono mt-3 text-[12px]",
                tone === "good" ? "text-accent" : "text-[color:var(--danger)]",
              ].join(" ")}
            >
              {state.action}
            </p>
          )}
        </div>

        <div className="flex items-end justify-between gap-3 border-t border-border-soft pt-4">
          <div>
            <p className="text-[11px] text-muted">
              {tone === "bad"
                ? "extra tokens re-carried this session"
                : "extra tokens above 50% line"}
            </p>
            <p
              className={[
                "mono mt-0.5 text-xl tabular-nums sm:text-2xl",
                tone === "bad" && state.tokensWasted > 0
                  ? "text-[color:var(--danger)]"
                  : "text-accent",
              ].join(" ")}
            >
              {state.tokensWasted.toLocaleString()}
            </p>
          </div>
          <p className="max-w-[15rem] text-right text-xs leading-relaxed text-fg-dim">
            {state.footer}
          </p>
        </div>
      </div>
    </article>
  );
}

function VaultPanel({
  notes,
  vaultKb,
  writeEvent,
  tick,
  emptyHint,
}: {
  notes: VaultNote[];
  vaultKb: number;
  writeEvent: string | null;
  tick: number;
  emptyHint: string;
}) {
  return (
    <div className="rounded-md border border-border-soft bg-bg">
      <div className="flex items-center justify-between border-b border-border-soft px-3 py-2">
        <p className="mono text-[10px] text-muted">~/vault (Obsidian)</p>
        <p className="mono text-[10px] tabular-nums text-fg-dim">
          size{" "}
          <span className={vaultKb > 0 ? "text-accent" : ""}>
            {vaultKb.toFixed(1)} KB
          </span>
        </p>
      </div>
      <div className="min-h-[96px] px-3 py-2">
        {notes.length === 0 ? (
          <p className="mono py-3 text-[12px] text-muted">{emptyHint}</p>
        ) : (
          <ul className="space-y-1">
            {notes.map((n) => (
              <li
                key={`${tick}-${n.path}`}
                className="mono flex items-center justify-between gap-2 text-[12px] sm:text-[13px]"
              >
                <span className="min-w-0 truncate text-accent-hot">
                  <span className="text-accent">+</span> {n.path}
                </span>
                <span className="shrink-0 tabular-nums text-muted">
                  {n.kb.toFixed(1)}k
                </span>
              </li>
            ))}
          </ul>
        )}
        {writeEvent && (
          <p
            key={`${tick}-write`}
            className="mono mt-2 border-t border-border-soft pt-2 text-[11px] text-accent"
          >
            {writeEvent}
          </p>
        )}
      </div>
      {/* Rising stack bars — vault mass growing */}
      <div className="flex items-end gap-0.5 border-t border-border-soft px-3 py-2">
        {Array.from({ length: 12 }).map((_, i) => {
          const filled = notes.length > 0 && i < Math.min(12, 2 + notes.length * 1.6);
          const h = 6 + ((i * 7) % 18);
          return (
            <div
              key={i}
              className={[
                "w-full rounded-sm transition-colors duration-500 motion-reduce:transition-none",
                filled ? "bg-accent/70" : "bg-border-soft",
              ].join(" ")}
              style={{ height: h }}
              aria-hidden
            />
          );
        })}
      </div>
    </div>
  );
}

function TokenEconomics() {
  const rows = CTX_LEVELS.map((pct) => {
    const extra = extraTokens(pct);
    const perQuery = extraDollars(pct);
    const perDay = perQuery * QUERIES_PER_DAY;
    const perMonth = perDay * 22; // workdays
    return { pct, extra, perQuery, perDay, perMonth };
  });

  // second-brain target: stay ≤50% via dump + selective recall
  const saveAt90 = rows.find((r) => r.pct === 90)!;

  return (
    <div className="mt-16 border-t border-border-soft pt-14 sm:mt-20 sm:pt-16">
      <div className="mb-8 max-w-2xl">
        <p className="mb-3 text-sm text-cool">Past 50% on a 1M window</p>
        <h3 className="display text-[clamp(1.5rem,3.2vw,2.15rem)] leading-[1.08] text-fg">
          The tax on every query after half full
        </h3>
        <p className="mt-4 text-sm leading-relaxed text-fg-dim sm:text-[15px]">
          On a{" "}
          <span className="mono text-fg">
            {WINDOW.toLocaleString()}-token
          </span>{" "}
          window, everything above 50% is optional bloat you re-send on{" "}
          <em>every</em> turn. Math:{" "}
          <span className="mono text-fg-dim">
            extra = 1M × (usage% − 50%)
          </span>
          . Costs use{" "}
          <span className="mono text-fg">{MODEL_LABEL}</span> API rates:{" "}
          <span className="mono text-fg">
            ${PRICE_PER_MTOK}/MTok input · ${PRICE_OUT_PER_MTOK}/MTok output
          </span>
          . The tax below is input only (history re-carried each query).
        </p>
      </div>

      {/* Highlight strip */}
      <div className="mb-8 grid gap-3 sm:grid-cols-3">
        <StatCard
          label="at 80% context"
          value={`${(extraTokens(80) / 1000).toFixed(0)}k`}
          hint="extra tokens / query"
        />
        <StatCard
          label="extra cost / query"
          value={`$${extraDollars(80).toFixed(2)}`}
          hint={`${MODEL_LABEL} · $${PRICE_PER_MTOK}/MTok input`}
        />
        <StatCard
          label="saved with second-brain"
          value={`$${saveAt90.perDay.toFixed(0)}/day`}
          hint={`90% → ≤50% · ${QUERIES_PER_DAY} q/day · Opus 4.8`}
          accent
        />
      </div>

      <div className="overflow-x-auto rounded-xl border border-border bg-surface">
        <table className="w-full min-w-[640px] border-collapse text-left text-sm">
          <thead>
            <tr className="border-b border-border-soft text-[11px] text-muted">
              <th className="px-4 py-3 font-medium sm:px-5">Context used</th>
              <th className="px-4 py-3 font-medium sm:px-5">
                Extra tokens / query
                <span className="mt-0.5 block font-normal text-muted">
                  above 50% of 1M
                </span>
              </th>
              <th className="px-4 py-3 font-medium sm:px-5">Extra $ / query</th>
              <th className="px-4 py-3 font-medium sm:px-5">
                Extra $ / day
                <span className="mt-0.5 block font-normal text-muted">
                  {QUERIES_PER_DAY} queries
                </span>
              </th>
              <th className="px-4 py-3 font-medium sm:px-5">
                Saved with second-brain
                <span className="mt-0.5 block font-normal text-muted">
                  stay ≤50% · / mo (22d)
                </span>
              </th>
            </tr>
          </thead>
          <tbody>
            {rows.map((r) => (
              <tr
                key={r.pct}
                className="border-b border-border-soft last:border-0"
              >
                <td className="px-4 py-3.5 sm:px-5">
                  <span className="mono text-fg">{r.pct}%</span>
                  <span className="ml-2 text-xs text-muted">
                    ({((WINDOW * r.pct) / 100 / 1000).toFixed(0)}k carried)
                  </span>
                </td>
                <td className="mono px-4 py-3.5 tabular-nums text-fg-dim sm:px-5">
                  +{r.extra.toLocaleString()}
                </td>
                <td className="mono px-4 py-3.5 tabular-nums text-[color:var(--danger)] sm:px-5">
                  +${r.perQuery.toFixed(2)}
                </td>
                <td className="mono px-4 py-3.5 tabular-nums text-[color:var(--danger)] sm:px-5">
                  +${r.perDay.toFixed(2)}
                </td>
                <td className="mono px-4 py-3.5 tabular-nums text-accent sm:px-5">
                  ${r.perMonth.toFixed(0)}
                  <span className="ml-1 text-xs text-muted">/mo</span>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      <div className="mt-6 grid gap-4 lg:grid-cols-[1fr_auto] lg:items-start">
        <p className="text-xs leading-relaxed text-muted sm:text-[13px]">
          <strong className="font-medium text-fg-dim">How to read this.</strong>{" "}
          At 90% of a 1M window you re-send 900k tokens every query. Only 500k of
          that is under the 50% line — the other{" "}
          <span className="mono text-fg-dim">400k</span> is pure tax (
          <span className="mono text-fg-dim">
            +${extraDollars(90).toFixed(2)}
          </span>{" "}
          / query on {MODEL_LABEL} at ${PRICE_PER_MTOK}/MTok input). second-brain
          keeps the durable memory in Markdown on disk and recalls a small
          slice, so you can <span className="mono text-fg-dim">/clear</span> and
          live under 50%. The “saved” column is that input tax going to zero —
          not free tokens, just not re-paying Opus rates for history you already
          wrote down.
        </p>
        <div className="rounded-lg border border-accent/30 bg-bg px-4 py-3 sm:min-w-[220px]">
          <p className="text-[11px] text-muted">example: 90% → ≤50%</p>
          <p className="mono mt-1 text-2xl text-accent">
            ${saveAt90.perMonth.toFixed(0)}
            <span className="text-sm text-fg-dim">/mo</span>
          </p>
          <p className="mt-1 text-xs text-fg-dim">
            back in your pocket at {QUERIES_PER_DAY} queries/day
          </p>
        </div>
      </div>
    </div>
  );
}

function StatCard({
  label,
  value,
  hint,
  accent = false,
}: {
  label: string;
  value: string;
  hint: string;
  accent?: boolean;
}) {
  return (
    <div
      className={[
        "rounded-xl border px-4 py-4 sm:px-5",
        accent ? "border-accent/35 bg-surface" : "border-border bg-surface",
      ].join(" ")}
    >
      <p className="text-[11px] text-muted">{label}</p>
      <p
        className={[
          "mono mt-1 text-2xl tabular-nums sm:text-[1.75rem]",
          accent ? "text-accent" : "text-fg",
        ].join(" ")}
      >
        {value}
      </p>
      <p className="mt-1 text-xs text-fg-dim">{hint}</p>
    </div>
  );
}

function StatusBadge({
  label,
  tone,
}: {
  label: string;
  tone: PanelState["badgeTone"];
}) {
  const colors: Record<PanelState["badgeTone"], string> = {
    neutral: "text-fg-dim border-border",
    warn: "text-accent-hot border-accent/40",
    danger: "text-[color:var(--danger)] border-[color:var(--danger)]/40",
    ok: "text-accent border-accent/40",
  };
  return (
    <span
      className={[
        "shrink-0 rounded-md border px-2 py-1 text-[11px] leading-none",
        colors[tone],
      ].join(" ")}
    >
      {label}
    </span>
  );
}

function Meter({
  label,
  value,
  tone,
  suffix,
  markAt,
}: {
  label: string;
  value: number;
  tone: "neutral" | "warn" | "danger" | "ok";
  suffix: string;
  markAt?: number;
}) {
  const fill: Record<typeof tone, string> = {
    neutral: "bg-fg-dim/70",
    warn: "bg-accent",
    danger: "bg-[color:var(--danger)]",
    ok: "bg-accent",
  };

  return (
    <div>
      <div className="mb-1.5 flex items-baseline justify-between gap-2">
        <span className="text-[11px] text-muted">{label}</span>
        <span className="mono text-[11px] tabular-nums text-fg-dim">{suffix}</span>
      </div>
      <div
        className="relative h-2 overflow-hidden rounded-full bg-bg"
        role="meter"
        aria-label={label}
        aria-valuenow={Math.round(value)}
        aria-valuemin={0}
        aria-valuemax={100}
      >
        {typeof markAt === "number" && (
          <div
            className="absolute top-0 bottom-0 z-[1] w-px bg-fg/35"
            style={{ left: `${markAt}%` }}
            title={`${markAt}% tax line`}
            aria-hidden
          />
        )}
        <div
          className={[
            "h-full rounded-full transition-[width] duration-700 ease-out motion-reduce:transition-none",
            fill[tone],
          ].join(" ")}
          style={{ width: `${Math.min(100, Math.max(0, value))}%` }}
        />
      </div>
      {typeof markAt === "number" && (
        <p className="mt-1 text-[10px] text-muted">{markAt}% tax line</p>
      )}
    </div>
  );
}
