const COLS = ["second-brain", "ChatGPT memory", "Claude memory", "mem0", "Basic Memory"];

type Cell = { t: string } | { v: boolean };
const rows: { label: string; cells: Cell[] }[] = [
  {
    label: "Where it's stored",
    cells: [
      { t: "your disk" },
      { t: "OpenAI cloud" },
      { t: "Anthropic cloud" },
      { t: "DB / cloud" },
      { t: "your disk" },
    ],
  },
  {
    label: "You own & export it",
    cells: [{ v: true }, { v: false }, { t: "limited" }, { t: "self-host" }, { v: true }],
  },
  {
    label: "Works across models",
    cells: [{ v: true }, { v: false }, { v: false }, { v: true }, { v: true }],
  },
  {
    label: "Auto-captures sessions",
    cells: [{ v: true }, { t: "auto" }, { t: "auto" }, { v: false }, { v: false }],
  },
  {
    label: "No account, no server",
    cells: [{ v: true }, { v: false }, { v: false }, { v: false }, { v: true }],
  },
];

function CellView({ cell }: { cell: Cell }) {
  if ("v" in cell)
    return cell.v ? (
      <span className="text-accent" aria-label="yes">
        ✓
      </span>
    ) : (
      <span className="text-ink-faint" aria-label="no">
        –
      </span>
    );
  return <span className="text-ink-dim">{cell.t}</span>;
}

export default function Compare() {
  return (
    <section id="compare" className="px-6 py-24 sm:px-10 sm:py-28">
      <div className="mx-auto max-w-6xl">
        <div className="max-w-2xl">
          <p className="font-mono text-[11px] tracking-[0.14em] text-ink-faint uppercase">
            honest map
          </p>
          <h2 className="mt-3 font-display text-[clamp(2rem,3.6vw,3rem)] leading-[1.05]">
            Local files. Any model.
            <br />
            No account.
          </h2>
          <p className="mt-4 max-w-xl text-ink-dim">
            File-based, cross-model, hands-free. Most tools pick one of those and call it done.
          </p>
        </div>

        <p className="mt-10 font-mono text-xs text-ink-faint sm:hidden">swipe the table →</p>
        <div className="mt-3 overflow-x-auto rounded-2xl border border-line sm:mt-12">
          <table className="w-full min-w-[680px] border-collapse text-left text-sm">
            <thead>
              <tr className="border-b border-line bg-surface/40">
                <th className="sticky left-0 z-10 w-[24%] bg-surface/95 py-3.5 pr-4 pl-4 font-normal text-ink-faint backdrop-blur-sm sm:pl-5">
                  &nbsp;
                </th>
                {COLS.map((c, i) => (
                  <th
                    key={c}
                    className={`px-4 py-3.5 align-bottom font-normal ${
                      i === 0
                        ? "bg-surface-2/70 font-display text-base text-ink"
                        : "text-ink-dim"
                    }`}
                  >
                    {c}
                  </th>
                ))}
              </tr>
            </thead>
            <tbody>
              {rows.map((r) => (
                <tr key={r.label} className="border-t border-line">
                  <th
                    scope="row"
                    className="sticky left-0 z-10 bg-bg/95 py-3.5 pr-4 pl-4 text-left font-normal text-ink-dim backdrop-blur-sm sm:pl-5"
                  >
                    {r.label}
                  </th>
                  {r.cells.map((cell, i) => (
                    <td
                      key={i}
                      className={`px-4 py-3.5 ${i === 0 ? "bg-surface-2/50" : ""}`}
                    >
                      <CellView cell={cell} />
                    </td>
                  ))}
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        <p className="mt-6 max-w-2xl text-sm leading-relaxed text-ink-faint">
          Where peers beat us: Basic Memory and Pieces add semantic search; mem0 adds
          knowledge-graph retrieval at agent scale. second-brain trades that for zero-infra,
          no-account ownership and native Claude Code fit: grep and plain Markdown over a
          database.
        </p>
      </div>
    </section>
  );
}
