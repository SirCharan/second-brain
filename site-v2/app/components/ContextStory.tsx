"use client";

import { useEffect, useState } from "react";

/**
 * Story section: Claude Code context fills → compact or /clear burns tokens,
 * vs second-brain dumping notes into Obsidian so you can clear for free.
 *
 * Content is always in the DOM (no opacity-0 entrance traps). Animation only
 * drives meters, counts, and phase labels.
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

const VAULT_NOTES = [
  "acme/rate-limit.md",
  "auth-flow.md",
  "deploy-r2.md",
  "session/today.md",
];

const PHASE_MS: Record<Phase, number> = {
  fill: 3200,
  pressure: 2200,
  choice: 2800,
  aftermath: 3200,
};

const PHASE_ORDER: Phase[] = ["fill", "pressure", "choice", "aftermath"];

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

  // Derived visual state from phase (same for every loop)
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
            Claude Code keeps working memory in the window. As it fills, you
            either compact (slow, lossy, expensive) or{" "}
            <span className="mono text-fg">/clear</span> and start from zero.
            second-brain writes the hard parts into Obsidian as you go, so the
            vault keeps the plot and the window can stay light.
          </p>
        </div>

        <div className="grid gap-4 lg:grid-cols-2 lg:gap-5">
          <StoryPanel
            tone="bad"
            eyebrow="without second-brain"
            title="Context is the only memory"
            state={without}
            tick={tick}
          />
          <StoryPanel
            tone="good"
            eyebrow="with second-brain"
            title="Vault holds it. Window stays free."
            state={withSb}
            tick={tick}
          />
        </div>

        <p className="mt-8 text-center text-xs text-muted sm:text-left">
          Loop is automatic. Same session work on both sides. Only the memory
          path changes.
        </p>
      </div>
    </section>
  );
}

type PanelState = {
  ctxPct: number;
  memPct: number;
  tokensWasted: number;
  lines: string[];
  vault: string[];
  badge: string;
  badgeTone: "neutral" | "warn" | "danger" | "ok";
  action: string | null;
  footer: string;
};

function withoutState(phase: Phase): PanelState {
  switch (phase) {
    case "fill":
      return {
        ctxPct: 58,
        memPct: 40,
        tokensWasted: 0,
        lines: MESSAGES.slice(0, 3),
        vault: [],
        badge: "session working",
        badgeTone: "neutral",
        action: null,
        footer: "History piles into the window. Every turn re-pays for it.",
      };
    case "pressure":
      return {
        ctxPct: 94,
        memPct: 88,
        tokensWasted: 12_400,
        lines: MESSAGES.slice(0, 5),
        vault: [],
        badge: "ctx near full",
        badgeTone: "warn",
        action: null,
        footer: "Recall degrades. Latency creeps. You feel the wall.",
      };
    case "choice":
      return {
        ctxPct: 100,
        memPct: 100,
        tokensWasted: 28_900,
        lines: MESSAGES,
        vault: [],
        badge: "must compact or /clear",
        badgeTone: "danger",
        action: "compacting… · or $ /clear",
        footer: "Compaction is slow and lossy. /clear wipes the plot.",
      };
    case "aftermath":
      return {
        ctxPct: 8,
        memPct: 0,
        tokensWasted: 41_200,
        lines: ["(window empty)", "who were we again?"],
        vault: [],
        badge: "amnesia + bill",
        badgeTone: "danger",
        action: null,
        footer: "Tokens spent to remember badly. Start over from zero.",
      };
  }
}

function withState(phase: Phase): PanelState {
  switch (phase) {
    case "fill":
      return {
        ctxPct: 34,
        memPct: 0,
        tokensWasted: 0,
        lines: MESSAGES.slice(0, 3),
        vault: VAULT_NOTES.slice(0, 1),
        badge: "capturing to vault",
        badgeTone: "ok",
        action: null,
        footer: "Same work. Notes land in Obsidian as Markdown.",
      };
    case "pressure":
      return {
        ctxPct: 42,
        memPct: 0,
        tokensWasted: 0,
        lines: MESSAGES.slice(0, 4),
        vault: VAULT_NOTES.slice(0, 3),
        badge: "vault growing",
        badgeTone: "ok",
        action: "+ rate-limit.md · + auth-flow.md",
        footer: "Window stays lean. Knowledge compounds on disk.",
      };
    case "choice":
      return {
        ctxPct: 18,
        memPct: 0,
        tokensWasted: 0,
        lines: ["$ /clear", "context freed"],
        vault: VAULT_NOTES,
        badge: "clear is free",
        badgeTone: "ok",
        action: "dumped → Obsidian vault",
        footer: "No compaction tax. The vault still has every decision.",
      };
    case "aftermath":
      return {
        ctxPct: 22,
        memPct: 0,
        tokensWasted: 0,
        lines: ["new session · Claude", "↳ recalled rate-limit.md ✓"],
        vault: VAULT_NOTES,
        badge: "recalling",
        badgeTone: "ok",
        action: null,
        footer: "Pick up cold. Right notes surface before you re-explain.",
      };
  }
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
  const accent =
    tone === "good"
      ? "border-accent/35"
      : "border-border";

  return (
    <article
      className={[
        "flex min-h-[420px] flex-col overflow-hidden rounded-xl border bg-surface",
        accent,
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

      <div className="flex flex-1 flex-col gap-5 px-5 py-5 sm:px-6">
        {/* Context meter */}
        <Meter
          label="context window"
          value={state.ctxPct}
          tone={
            state.ctxPct >= 90
              ? "danger"
              : state.ctxPct >= 70
                ? "warn"
                : tone === "good"
                  ? "ok"
                  : "neutral"
          }
          suffix={`${Math.round(state.ctxPct)}%`}
        />

        {/* Built-in memory (Claude-side) vs vault */}
        {tone === "bad" ? (
          <Meter
            label="chat memory (vendor)"
            value={state.memPct}
            tone={state.memPct >= 90 ? "danger" : "warn"}
            suffix={`${Math.round(state.memPct)}%`}
          />
        ) : (
          <VaultStack notes={state.vault} tick={tick} />
        )}

        {/* Session log */}
        <div className="min-h-[120px] flex-1 rounded-md border border-border-soft bg-bg px-3 py-3">
          <p className="mono mb-2 text-[10px] text-muted">session</p>
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

        {/* Token waste counter — only meaningful on the bad path */}
        <div className="flex items-end justify-between gap-3 border-t border-border-soft pt-4">
          <div>
            <p className="text-[11px] text-muted">
              {tone === "bad" ? "tokens burned re-carrying history" : "tokens on re-carry"}
            </p>
            <p
              className={[
                "mono mt-0.5 text-xl tabular-nums sm:text-2xl",
                tone === "bad" && state.tokensWasted > 0
                  ? "text-[color:var(--danger)]"
                  : "text-fg",
              ].join(" ")}
            >
              {state.tokensWasted.toLocaleString()}
            </p>
          </div>
          <p className="max-w-[14rem] text-right text-xs leading-relaxed text-fg-dim">
            {state.footer}
          </p>
        </div>
      </div>
    </article>
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
}: {
  label: string;
  value: number;
  tone: "neutral" | "warn" | "danger" | "ok";
  suffix: string;
}) {
  const fill: Record<typeof tone, string> = {
    neutral: "bg-fg-dim",
    warn: "bg-accent",
    danger: "bg-[color:var(--danger)]",
    ok: "bg-accent",
  };

  // Content always visible; width animates. prefers-reduced-motion: no transition.
  return (
    <div>
      <div className="mb-1.5 flex items-baseline justify-between gap-2">
        <span className="text-[11px] text-muted">{label}</span>
        <span className="mono text-[11px] tabular-nums text-fg-dim">{suffix}</span>
      </div>
      <div
        className="h-2 overflow-hidden rounded-full bg-bg"
        role="meter"
        aria-label={label}
        aria-valuenow={Math.round(value)}
        aria-valuemin={0}
        aria-valuemax={100}
      >
        <div
          className={[
            "h-full rounded-full transition-[width] duration-700 ease-out motion-reduce:transition-none",
            fill[tone],
          ].join(" ")}
          style={{ width: `${Math.min(100, Math.max(0, value))}%` }}
        />
      </div>
    </div>
  );
}

function VaultStack({ notes, tick }: { notes: string[]; tick: number }) {
  return (
    <div>
      <div className="mb-1.5 flex items-baseline justify-between gap-2">
        <span className="text-[11px] text-muted">Obsidian vault (on disk)</span>
        <span className="mono text-[11px] tabular-nums text-accent">
          {notes.length} notes
        </span>
      </div>
      <div className="min-h-[52px] rounded-md border border-accent/25 bg-bg px-3 py-2">
        {notes.length === 0 ? (
          <p className="mono text-[12px] text-muted">vault empty…</p>
        ) : (
          <ul className="space-y-1">
            {notes.map((n, i) => (
              <li
                key={`${tick}-${n}`}
                className="mono text-[12px] text-accent-hot sm:text-[13px]"
              >
                <span className="text-accent">+</span> {n}
              </li>
            ))}
          </ul>
        )}
      </div>
    </div>
  );
}
