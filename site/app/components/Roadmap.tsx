/* Forward-looking teaser. Everything here is "coming" — do NOT imply it ships today.
   Bare tonal markers, no icon-in-tile, honest framing. */
const NEXT = [
  { t: "A one-click Mac app", d: "Set it up without touching a terminal." },
  { t: "An MCP server", d: "The same memory inside Claude Desktop, ChatGPT, and Cursor." },
  { t: "Semantic search", d: "Find notes by meaning across the whole vault, not just keywords." },
  { t: "Shared team vaults", d: "Institutional memory that lives in git." },
  { t: "Import your history", d: "Pull your existing ChatGPT and Claude chats into the vault." },
];

export default function Roadmap() {
  return (
    <section className="px-6 py-24 sm:px-10 sm:py-28">
      <div className="mx-auto max-w-5xl">
        <div className="flex items-baseline gap-3">
          <h2 className="font-display text-[clamp(1.9rem,3.6vw,2.9rem)] leading-tight">
            Built in the open. What&apos;s next.
          </h2>
          <span className="font-mono text-xs uppercase tracking-widest text-accent">coming soon</span>
        </div>
        <ul className="mt-10 divide-y divide-line border-y border-line">
          {NEXT.map((n) => (
            <li key={n.t} className="flex flex-col gap-1 py-5 sm:flex-row sm:items-baseline sm:gap-6">
              <span className="font-display text-lg text-ink sm:w-64 sm:shrink-0">{n.t}</span>
              <span className="text-[15px] leading-relaxed text-ink-dim">{n.d}</span>
            </li>
          ))}
        </ul>
        <p className="mt-6 text-sm text-ink-faint">
          Follow along on <a href="https://github.com/SirCharan/second-brain" target="_blank" rel="noreferrer" className="text-ink-dim underline decoration-line underline-offset-4 transition-colors hover:text-ink">GitHub</a> — it&apos;s all being built in public.
        </p>
      </div>
    </section>
  );
}
