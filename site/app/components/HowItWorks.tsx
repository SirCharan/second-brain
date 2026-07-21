import Terminal from "./Terminal";

/* The loop, told as three honest frames: a note written with one model survives
   /clear and is recalled by another. Connected by the amber pulse, not a rail. */
export default function HowItWorks() {
  return (
    <section id="how" className="px-6 py-24 sm:px-10 sm:py-32">
      <div className="mx-auto max-w-5xl">
        <h2 className="font-display text-[clamp(1.9rem,3.6vw,2.9rem)] leading-tight">
          Write it once. Recall it anywhere.
        </h2>
        <p className="mt-4 max-w-xl text-ink-dim">
          Memory lives in the vault, not the conversation. So you can end a session,
          free the context, switch models — and pick up exactly where you were.
        </p>

        <div className="mt-14 grid items-stretch gap-4 lg:grid-cols-[1fr_auto_1fr_auto_1fr]">
          <Terminal label="session · GPT-style" status="working">
            <div className="space-y-1 text-ink-dim">
              <p className="text-ink-faint">you solve a gnarly bug together…</p>
              <p className="pt-1">
                <span className="text-accent">+ captured</span>{" "}
                <span className="text-ink">acme/rate-limit.md</span>
              </p>
              <p className="pl-6 text-ink-faint">“jittered retry on 429”</p>
            </div>
          </Terminal>

          <Connector />

          <Terminal label="context" status="freed">
            <div className="space-y-1 text-ink-dim">
              <p>
                <span className="text-ink">$ /clear</span>
              </p>
              <p className="text-ink-faint">no compaction. no bloated history.</p>
              <p className="pt-1 text-ink-faint">the window is empty again —</p>
              <p className="text-ink-faint">the vault still remembers.</p>
            </div>
          </Terminal>

          <Connector />

          <Terminal label="new session · Claude" status="recalling">
            <div className="space-y-1 text-ink-dim">
              <p className="text-ink-faint">weeks later, a different tool…</p>
              <p className="pt-1">
                <span className="text-accent">↳ recalled</span>{" "}
                <span className="text-ink">acme/rate-limit.md</span>{" "}
                <span className="text-accent">✓</span>
              </p>
              <p className="pl-6 text-ink-faint">surfaced before you asked</p>
            </div>
          </Terminal>
        </div>
      </div>
    </section>
  );
}

/* bespoke connector: a rounded-cap track with an amber pulse traveling it.
   Horizontal on wide screens, vertical when the frames stack. */
function Connector() {
  return (
    <div className="flex items-center justify-center lg:w-10">
      <svg
        className="h-8 w-px lg:h-px lg:w-10"
        viewBox="0 0 40 2"
        preserveAspectRatio="none"
        aria-hidden="true"
      >
        <line x1="0" y1="1" x2="40" y2="1" stroke="var(--color-line-strong)" strokeWidth="2" strokeLinecap="round" />
        <line
          className="g-pulse"
          x1="0"
          y1="1"
          x2="40"
          y2="1"
          stroke="var(--color-accent)"
          strokeWidth="2"
          strokeLinecap="round"
          strokeDasharray="6 36"
          pathLength={42}
        />
      </svg>
    </div>
  );
}
