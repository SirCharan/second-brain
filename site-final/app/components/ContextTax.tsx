"use client";

import { useEffect, useState } from "react";

/**
 * Animated before/after context story — phases from second-brain-cinema,
 * layout/copy aligned to the final landing screenshot.
 */

type Phase = "fill" | "pressure" | "choice" | "aftermath";

const PHASE_ORDER: Phase[] = ["fill", "pressure", "choice", "aftermath"];
const PHASE_MS: Record<Phase, number> = {
  fill: 3600,
  pressure: 3000,
  choice: 3200,
  aftermath: 3800,
};

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

function sumKb(notes: VaultNote[]) {
  return Math.round(notes.reduce((s, n) => s + n.kb, 0) * 10) / 10;
}

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

function prefersReducedMotion() {
  if (typeof window === "undefined") return true;
  return window.matchMedia("(prefers-reduced-motion: reduce)").matches;
}

export default function ContextTax() {
  const [phase, setPhase] = useState<Phase>("fill");
  const [tick, setTick] = useState(0);
  const [reduced, setReduced] = useState(false);

  useEffect(() => {
    setReduced(prefersReducedMotion());
  }, []);

  useEffect(() => {
    if (reduced) {
      setPhase("fill");
      return;
    }
    let cancelled = false;
    let phaseIdx = 0;
    let timer = 0;

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
          <StoryPanel
            tone="bad"
            eyebrow="Without second-brain"
            title="Everything lives in the window"
            state={without}
            tick={tick}
          />
          <StoryPanel
            tone="good"
            eyebrow="With second-brain"
            title="Vault rises. Session stays light."
            state={withSb}
            tick={tick}
          />
        </div>

        <p className="mt-6 max-w-2xl text-sm text-ink-faint">
          Loop is automatic. Same work both sides. Left: the session swells. Right:
          notes stream into Obsidian while context stays under the tax line.
        </p>
      </div>
    </section>
  );
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
  const barTone =
    state.ctxPct >= 90 ? "danger" : state.ctxPct > 50 ? "warn" : tone === "good" ? "ok" : "neutral";

  return (
    <article
      className={`flex min-h-[520px] flex-col rounded-2xl border p-6 sm:p-7 ${
        tone === "good"
          ? "border-line-strong bg-surface/60 shadow-[inset_0_0_0_1px_color-mix(in_oklab,var(--color-accent)_12%,transparent)]"
          : "border-line bg-surface/40"
      }`}
    >
      <div className="flex items-start justify-between gap-3">
        <div>
          <p
            className={`font-mono text-[10px] tracking-[0.12em] uppercase ${
              tone === "good" ? "text-accent" : "text-ink-faint"
            }`}
          >
            {eyebrow}
          </p>
          <h3 className="mt-1.5 font-display text-xl leading-snug">{title}</h3>
        </div>
        <Badge label={state.badge} tone={state.badgeTone} />
      </div>

      <div className="mt-8 space-y-5">
        <Bar
          label="session / context"
          value={state.ctxPct}
          maxLabel={`${Math.round(state.ctxPct)}%`}
          tone={barTone}
        />
        {tone === "bad" ? (
          <Bar
            label="chat memory (vendor)"
            value={state.memPct}
            maxLabel={`${Math.round(state.memPct)}%`}
            tone={state.memPct > 50 ? "warn" : "neutral"}
          />
        ) : (
          <Bar
            label="Obsidian vault"
            value={Math.min(100, state.vaultKb * 6)}
            maxLabel={
              state.vaultKb > 0
                ? `${state.vault.length} notes · ${state.vaultKb} KB`
                : "0 notes · 0 KB"
            }
            tone={state.vaultKb > 0 ? "ok" : "neutral"}
          />
        )}
      </div>

      <VaultPanel
        notes={state.vault}
        vaultKb={state.vaultKb}
        writeEvent={state.writeEvent}
        tick={tick}
        emptyHint={
          tone === "bad" ? "nothing on disk — all in the window" : "waiting for capture…"
        }
      />

      <div className="mt-4 min-h-[112px] flex-1 rounded-xl border border-line bg-bg/50 p-4 font-mono text-[13px] leading-relaxed">
        <div className="mb-2 flex justify-between text-[11px] text-ink-faint">
          <span>session transcript</span>
          <span>
            re-carry{" "}
            <span className={state.ctxPct > 50 ? "text-accent" : "text-accent"}>
              {state.ctxPct > 50 ? "taxed" : "lean"}
            </span>
          </span>
        </div>
        <ul className="space-y-1.5 text-ink-dim">
          {state.lines.map((line, i) => (
            <li
              key={`${tick}-${i}-${line}`}
              className={
                line.startsWith("$") || line.startsWith("↳")
                  ? "text-accent"
                  : line.startsWith("(")
                    ? "text-ink-faint"
                    : ""
              }
            >
              {line}
            </li>
          ))}
        </ul>
        {state.action && (
          <p
            className={`mt-3 text-[12px] ${
              tone === "good" ? "text-accent" : "text-ink-faint"
            }`}
          >
            {state.action}
          </p>
        )}
      </div>

      <div className="mt-auto flex items-end justify-between gap-3 border-t border-line pt-5">
        <div>
          <p className="text-[11px] text-ink-faint">
            {tone === "bad"
              ? "extra tokens re-carried this session"
              : "extra tokens above 50% line"}
          </p>
          <p
            className={`mt-0.5 font-mono text-xl tabular-nums sm:text-2xl ${
              tone === "bad" && state.tokensWasted > 0 ? "text-accent" : "text-accent"
            }`}
          >
            {state.tokensWasted.toLocaleString()}
          </p>
        </div>
        <p className="max-w-[15rem] text-right text-xs leading-relaxed text-ink-dim">
          {state.footer}
        </p>
      </div>
    </article>
  );
}

function Bar({
  label,
  value,
  maxLabel,
  tone,
}: {
  label: string;
  value: number;
  maxLabel: string;
  tone: "neutral" | "warn" | "danger" | "ok";
}) {
  const fill =
    tone === "ok" || tone === "warn" || tone === "danger"
      ? "var(--color-accent)"
      : "color-mix(in oklab, var(--color-ink-dim) 55%, transparent)";

  return (
    <div>
      <div className="mb-1.5 flex items-baseline justify-between gap-3 text-xs">
        <span className="text-ink-faint">{label}</span>
        <span
          className={
            tone === "warn" || tone === "danger" || tone === "ok"
              ? "text-accent"
              : "text-ink-dim"
          }
        >
          {maxLabel}
        </span>
      </div>
      <div className="h-1.5 overflow-hidden rounded-full bg-surface-2">
        <div
          className="h-full rounded-full transition-[width] duration-700 ease-out motion-reduce:transition-none"
          style={{ width: `${Math.min(100, value)}%`, background: fill }}
        />
      </div>
    </div>
  );
}

function Badge({
  label,
  tone,
}: {
  label: string;
  tone: "neutral" | "warn" | "danger" | "ok";
}) {
  const cls =
    tone === "ok"
      ? "border-accent/30 bg-accent/10 text-accent"
      : tone === "warn" || tone === "danger"
        ? "border-accent/40 bg-accent/10 text-accent"
        : "border-line text-ink-faint";
  return (
    <span
      className={`shrink-0 rounded-md border px-2 py-1 font-mono text-[10px] transition-colors duration-500 ${cls}`}
    >
      {label}
    </span>
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
    <div className="mt-7 rounded-xl border border-line bg-bg/50">
      <div className="flex items-center justify-between border-b border-line px-4 py-2.5 text-[11px] text-ink-faint">
        <span className="font-mono">~/vault (Obsidian)</span>
        <span className="font-mono tabular-nums">
          size{" "}
          <span className={vaultKb > 0 ? "text-accent" : ""}>
            {vaultKb.toFixed(1)} KB
          </span>
        </span>
      </div>
      <div className="min-h-[96px] px-4 py-3 font-mono text-[13px]">
        {notes.length === 0 ? (
          <p className="py-2 text-ink-faint">{emptyHint}</p>
        ) : (
          <ul className="space-y-1">
            {notes.map((n) => (
              <li
                key={`${tick}-${n.path}`}
                className="flex items-center justify-between gap-2 text-accent animate-[fadeIn_0.45s_ease-out]"
              >
                <span className="min-w-0 truncate">
                  <span className="text-accent">+</span> {n.path}
                </span>
                <span className="shrink-0 tabular-nums text-ink-faint">
                  {n.kb.toFixed(1)}k
                </span>
              </li>
            ))}
          </ul>
        )}
        {writeEvent && (
          <p
            key={`${tick}-write`}
            className="mt-2 border-t border-line pt-2 text-[11px] text-accent"
          >
            {writeEvent}
          </p>
        )}
      </div>
      <div className="flex items-end gap-0.5 border-t border-line px-4 py-2">
        {Array.from({ length: 12 }).map((_, i) => {
          const filled = notes.length > 0 && i < Math.min(12, 2 + notes.length * 1.6);
          const h = 6 + ((i * 7) % 18);
          return (
            <div
              key={i}
              className={`w-full rounded-sm transition-colors duration-500 motion-reduce:transition-none ${
                filled ? "bg-accent/70" : "bg-surface-2"
              }`}
              style={{ height: h }}
              aria-hidden
            />
          );
        })}
      </div>
    </div>
  );
}
