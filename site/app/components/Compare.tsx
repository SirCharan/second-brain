/* Honest comparison. Columns align on a shared grid; our column is tonally
   lifted (not a glowing border). ✓ = amber, – = faint, short words where truer. */

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
      <span className="text-accent" aria-label="yes">✓</span>
    ) : (
      <span className="text-ink-faint" aria-label="no">–</span>
    );
  return <span className="text-ink-dim">{cell.t}</span>;
}

export default function Compare() {
  return (
    <section id="compare" className="px-6 py-24 sm:px-10 sm:py-28">
      <div className="mx-auto max-w-5xl">
        <h2 className="max-w-2xl font-display text-[clamp(1.9rem,3.6vw,2.9rem)] leading-tight">
          The niche nobody else fully owns.
        </h2>
        <p className="mt-4 max-w-xl text-ink-dim">
          Local <span className="text-ink">and</span> file-based{" "}
          <span className="text-ink">and</span> cross-model{" "}
          <span className="text-ink">and</span> hands-free. Most tools give you one or two.
        </p>

        <div className="mt-12 overflow-x-auto">
          <table className="w-full min-w-[640px] border-collapse text-left text-sm">
            <thead>
              <tr>
                <th className="w-[26%] py-3 pr-4 font-normal text-ink-faint">&nbsp;</th>
                {COLS.map((c, i) => (
                  <th
                    key={c}
                    className={`px-4 py-3 align-bottom font-normal ${
                      i === 0
                        ? "rounded-t-lg bg-surface-2/60 font-display text-base text-ink"
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
                  <th scope="row" className="py-3.5 pr-4 text-left font-normal text-ink-dim">
                    {r.label}
                  </th>
                  {r.cells.map((cell, i) => (
                    <td
                      key={i}
                      className={`px-4 py-3.5 ${i === 0 ? "bg-surface-2/60" : ""}`}
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
          Peers earn their keep, honestly: Basic Memory and Pieces add semantic search;
          mem0 adds knowledge-graph retrieval at agent scale. second-brain trades that
          for zero-infra, no-account ownership and native Claude Code fit — grep and
          plain Markdown over a database.
        </p>
      </div>
    </section>
  );
}
