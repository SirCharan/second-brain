"use client";

import { useEffect, useRef, useState } from "react";

/**
 * Scroll-driven context story.
 * As the user scrolls through this chapter, left panel fills (tax),
 * right panel stays lean while the vault writes notes to disk.
 * Reduced-motion: static mid-story frame, no sticky track.
 */

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

function clamp01(n: number) {
  return Math.max(0, Math.min(1, n));
}

function easeInOut(t: number) {
  return t < 0.5 ? 2 * t * t : 1 - Math.pow(-2 * t + 2, 2) / 2;
}

function lerp(a: number, b: number, t: number) {
  return a + (b - a) * t;
}

type SideState = {
  ctxPct: number;
  memPct: number;
  vaultCount: number;
  vaultKb: number;
  writeEvent: string | null;
  badge: string;
  badgeTone: "neutral" | "warn" | "danger" | "ok";
  lines: string[];
  action: string | null;
  footer: string;
  tokensWasted: number;
};

/** Map scroll progress 0→1 into both panel states (continuous fill). */
function stateAt(progress: number): { bad: SideState; good: SideState } {
  const p = clamp01(progress);
  const e = easeInOut(p);

  // ── WITHOUT: window fills until collapse ──
  let badCtx: number;
  let badMem: number;
  let badBadge: SideState["badge"];
  let badTone: SideState["badgeTone"];
  let badLines: string[];
  let badAction: string | null = null;
  let badFooter: string;
  let badWaste: number;

  if (p < 0.28) {
    const t = e / 0.28;
    badCtx = lerp(32, 58, t);
    badMem = lerp(22, 48, t);
    badBadge = "session working";
    badTone = "neutral";
    badLines = MESSAGES.slice(0, 2 + Math.floor(t * 1));
    badFooter = "History stays in the chat. Nothing hits disk.";
    badWaste = 0;
  } else if (p < 0.55) {
    const t = (e - 0.28) / 0.27;
    badCtx = lerp(58, 82, t);
    badMem = lerp(48, 88, t);
    badBadge = "past 50% · tax starts";
    badTone = "warn";
    badLines = MESSAGES.slice(0, 3 + Math.floor(t * 2));
    badFooter = "Every query re-sends the fat history. Vault still empty.";
    badWaste = Math.round(lerp(0, 18_400, t));
  } else if (p < 0.78) {
    const t = (e - 0.55) / 0.23;
    badCtx = lerp(82, 97, t);
    badMem = lerp(88, 100, t);
    badBadge = "must compact or /clear";
    badTone = "danger";
    badLines = MESSAGES;
    badAction = "compacting… · or $ /clear";
    badFooter = "Slow, lossy, or wipe. Knowledge never left the window.";
    badWaste = Math.round(lerp(18_400, 38_200, t));
  } else {
    const t = (e - 0.78) / 0.22;
    badCtx = lerp(97, 6, t);
    badMem = lerp(100, 0, t);
    badBadge = "amnesia + bill";
    badTone = "danger";
    badLines = ["(window empty)", "who were we again?"];
    badFooter = "Tokens spent. Plot gone. Vault still empty.";
    badWaste = Math.round(lerp(38_200, 52_800, t));
  }

  // ── WITH: vault fills, session stays under tax line ──
  let goodCtx: number;
  let goodBadge: SideState["badge"];
  let goodTone: SideState["badgeTone"] = "ok";
  let goodLines: string[];
  let goodAction: string | null = null;
  let goodFooter: string;
  let vaultCount: number;
  let writeEvent: string | null;

  if (p < 0.22) {
    const t = e / 0.22;
    goodCtx = lerp(18, 28, t);
    vaultCount = t > 0.35 ? 1 : 0;
    if (t > 0.7) vaultCount = 2;
    goodBadge = "capturing";
    goodLines = MESSAGES.slice(0, 2 + Math.floor(t));
    writeEvent = vaultCount > 0 ? `→ wrote ${VAULT_NOTES[vaultCount - 1].path}` : null;
    goodFooter = "Work happens. Notes land in Obsidian. Session stays thin.";
  } else if (p < 0.5) {
    const t = (e - 0.22) / 0.28;
    goodCtx = lerp(28, 32, t);
    vaultCount = 2 + Math.floor(t * 2); // 2→4
    goodBadge = "vault rising";
    goodLines = MESSAGES.slice(0, 3 + Math.floor(t));
    goodAction = "session flat · vault growing";
    writeEvent = `→ wrote ${VAULT_NOTES[Math.min(vaultCount - 1, VAULT_NOTES.length - 1)].path}`;
    goodFooter = "More knowledge. Not more context. Under the 50% tax line.";
  } else if (p < 0.72) {
    const t = (e - 0.5) / 0.22;
    goodCtx = lerp(32, 14, t);
    vaultCount = 4 + Math.floor(t * 2); // 4→6
    goodBadge = "clear is free";
    goodLines = ["$ /clear", "context freed", "vault untouched"];
    goodAction = "dumped → Obsidian vault";
    writeEvent = "→ dump complete · notes on disk";
    goodFooter = "Window empties. Disk keeps every decision.";
  } else {
    const t = (e - 0.72) / 0.28;
    goodCtx = lerp(14, 22, t);
    vaultCount = 6;
    goodBadge = "recalling";
    goodLines = [
      "new session · Claude",
      "↳ recalled acme/rate-limit.md ✓",
      "↳ recalled auth-flow.md ✓",
    ];
    writeEvent = "← recall from vault (not re-typed)";
    goodFooter = "Pick up cold. Only the relevant notes re-enter the window.";
  }

  vaultCount = Math.min(VAULT_NOTES.length, vaultCount);
  const vault = VAULT_NOTES.slice(0, vaultCount);
  const vaultKb = Math.round(vault.reduce((s, n) => s + n.kb, 0) * 10) / 10;

  return {
    bad: {
      ctxPct: badCtx,
      memPct: badMem,
      vaultCount: 0,
      vaultKb: 0,
      writeEvent: null,
      badge: badBadge,
      badgeTone: badTone,
      lines: badLines,
      action: badAction,
      footer: badFooter,
      tokensWasted: badWaste,
    },
    good: {
      ctxPct: goodCtx,
      memPct: 0,
      vaultCount,
      vaultKb,
      writeEvent,
      badge: goodBadge,
      badgeTone: goodTone,
      lines: goodLines,
      action: goodAction,
      footer: goodFooter,
      tokensWasted: 0,
    },
  };
}

export default function ContextTax() {
  const trackRef = useRef<HTMLElement>(null);
  const [progress, setProgress] = useState(0.12);
  const [reduced, setReduced] = useState(false);

  useEffect(() => {
    const mq = window.matchMedia("(prefers-reduced-motion: reduce)");
    setReduced(mq.matches);
    const onMq = () => setReduced(mq.matches);
    mq.addEventListener("change", onMq);
    return () => mq.removeEventListener("change", onMq);
  }, []);

  useEffect(() => {
    if (reduced) {
      setProgress(0.4);
      return;
    }

    const el = trackRef.current;
    if (!el) return;

    let raf = 0;
    const update = () => {
      raf = 0;
      const rect = el.getBoundingClientRect();
      const trackH = el.offsetHeight;
      const viewH = window.innerHeight;
      // progress 0 when sticky block hits top, 1 when track end reaches bottom
      const scrolled = -rect.top;
      const range = Math.max(1, trackH - viewH);
      setProgress(clamp01(scrolled / range));
    };

    const onScroll = () => {
      if (!raf) raf = requestAnimationFrame(update);
    };

    update();
    window.addEventListener("scroll", onScroll, { passive: true });
    window.addEventListener("resize", onScroll, { passive: true });
    return () => {
      window.removeEventListener("scroll", onScroll);
      window.removeEventListener("resize", onScroll);
      if (raf) cancelAnimationFrame(raf);
    };
  }, [reduced]);

  const { bad, good } = stateAt(progress);
  const phaseLabel =
    progress < 0.28
      ? "01 · fill"
      : progress < 0.55
        ? "02 · pressure"
        : progress < 0.78
          ? "03 · choice"
          : "04 · aftermath";

  return (
    <section
      id="context"
      ref={trackRef}
      className={
        reduced
          ? "border-t border-line"
          : "relative border-t border-line min-h-[260vh]"
      }
    >
      <div
        className={
          reduced
            ? "px-6 py-24 sm:px-10 sm:py-28"
            : "sticky top-0 flex min-h-svh flex-col justify-center px-6 py-16 sm:px-10 sm:py-20"
        }
      >
        <div className="mx-auto w-full max-w-6xl">
          <div className="flex flex-wrap items-end justify-between gap-4">
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
                Long chats re-send their history on every turn. Past half full, you pay
                for bloat you already know. second-brain puts the hard parts in Markdown
                so the vault grows and the window stays light.
              </p>
            </div>

            {/* scroll progress meter */}
            {!reduced && (
              <div className="mb-1 w-full max-w-[11rem] sm:w-40">
                <div className="flex items-center justify-between font-mono text-[10px] text-ink-faint">
                  <span>{phaseLabel}</span>
                  <span>{Math.round(progress * 100)}%</span>
                </div>
                <div className="mt-1.5 h-1 overflow-hidden rounded-full bg-surface-2">
                  <div
                    className="h-full rounded-full bg-accent transition-[width] duration-100 ease-out"
                    style={{ width: `${progress * 100}%` }}
                  />
                </div>
                <p className="mt-1.5 font-mono text-[10px] text-ink-faint">
                  scroll to play
                </p>
              </div>
            )}
          </div>

          <div className="mt-10 grid gap-4 lg:grid-cols-2">
            <StoryPanel
              tone="bad"
              eyebrow="Without second-brain"
              title="Everything lives in the window"
              state={bad}
            />
            <StoryPanel
              tone="good"
              eyebrow="With second-brain"
              title="Vault rises. Session stays light."
              state={good}
              notes={VAULT_NOTES.slice(0, good.vaultCount)}
            />
          </div>

          <p className="mt-6 max-w-2xl text-sm text-ink-faint">
            {reduced
              ? "Same work both sides. Left: the session swells. Right: notes land in Obsidian."
              : "Scroll to run the loop. Left fills the window. Right writes the vault and stays under the tax line."}
          </p>
        </div>
      </div>
    </section>
  );
}

function StoryPanel({
  tone,
  eyebrow,
  title,
  state,
  notes = [],
}: {
  tone: "bad" | "good";
  eyebrow: string;
  title: string;
  state: SideState;
  notes?: VaultNote[];
}) {
  const barTone =
    state.ctxPct >= 90
      ? "danger"
      : state.ctxPct > 50
        ? "warn"
        : tone === "good"
          ? "ok"
          : "neutral";

  return (
    <article
      className={`flex min-h-[480px] flex-col rounded-2xl border p-5 sm:min-h-[520px] sm:p-7 ${
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
          <h3 className="mt-1.5 font-display text-lg leading-snug sm:text-xl">{title}</h3>
        </div>
        <Badge label={state.badge} tone={state.badgeTone} />
      </div>

      <div className="mt-7 space-y-4">
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
                ? `${notes.length} notes · ${state.vaultKb} KB`
                : "0 notes · 0 KB"
            }
            tone={state.vaultKb > 0 ? "ok" : "neutral"}
          />
        )}
      </div>

      <VaultPanel
        notes={notes}
        vaultKb={state.vaultKb}
        writeEvent={state.writeEvent}
        emptyHint={
          tone === "bad" ? "nothing on disk — all in the window" : "waiting for capture…"
        }
      />

      <div className="mt-4 min-h-[108px] flex-1 rounded-xl border border-line bg-bg/50 p-4 font-mono text-[13px] leading-relaxed">
        <div className="mb-2 flex justify-between text-[11px] text-ink-faint">
          <span>session transcript</span>
          <span>
            re-carry{" "}
            <span className="text-accent">
              {state.ctxPct > 50 ? "taxed" : "lean"}
            </span>
          </span>
        </div>
        <ul className="space-y-1.5 text-ink-dim">
          {state.lines.map((line, i) => (
            <li
              key={`${i}-${line}`}
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
          <p className="mt-0.5 font-mono text-xl tabular-nums text-accent sm:text-2xl">
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
          className="h-full rounded-full will-change-[width]"
          style={{
            width: `${Math.min(100, Math.max(0, value))}%`,
            background: fill,
            transition: "width 80ms linear",
          }}
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
    <span className={`shrink-0 rounded-md border px-2 py-1 font-mono text-[10px] ${cls}`}>
      {label}
    </span>
  );
}

function VaultPanel({
  notes,
  vaultKb,
  writeEvent,
  emptyHint,
}: {
  notes: VaultNote[];
  vaultKb: number;
  writeEvent: string | null;
  emptyHint: string;
}) {
  return (
    <div className="mt-6 rounded-xl border border-line bg-bg/50">
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
                key={n.path}
                className="flex items-center justify-between gap-2 text-accent"
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
          <p className="mt-2 border-t border-line pt-2 text-[11px] text-accent">
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
              className={`w-full rounded-sm transition-colors duration-300 ${
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
