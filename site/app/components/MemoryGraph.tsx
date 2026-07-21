/**
 * The signature artifact: an honest picture of what the product IS — a vault of
 * linked notes. Two project clusters; a lesson learned in one (rate-limit.md)
 * fires across the bridge edge into another (retry.md) — the "neuron effect".
 * Pure SVG: fully visible with no JS; the amber recall-pulse only enhances.
 */
type Node = { id: string; x: number; y: number; label?: string; hot?: boolean };

const NODES: Node[] = [
  { id: "auth", x: 150, y: 150, label: "auth.md" },
  { id: "deploy", x: 118, y: 258 },
  { id: "ratelimit", x: 250, y: 205, label: "rate-limit.md", hot: true },
  { id: "schema", x: 205, y: 320 },
  { id: "webhook", x: 470, y: 138, label: "webhook.md" },
  { id: "retry", x: 548, y: 232, label: "retry.md", hot: true },
  { id: "cache", x: 430, y: 300 },
  { id: "queue", x: 560, y: 120 },
];

const N = Object.fromEntries(NODES.map((n) => [n.id, n]));
const EDGES: [string, string][] = [
  ["auth", "ratelimit"],
  ["deploy", "ratelimit"],
  ["schema", "ratelimit"],
  ["webhook", "retry"],
  ["retry", "cache"],
  ["webhook", "queue"],
  ["cache", "webhook"],
];
const BRIDGE: [string, string] = ["ratelimit", "retry"];

export default function MemoryGraph({ className }: { className?: string }) {
  const b0 = N[BRIDGE[0]];
  const b1 = N[BRIDGE[1]];
  return (
    <svg
      className={className}
      viewBox="0 0 660 420"
      fill="none"
      aria-hidden="true"
      preserveAspectRatio="xMidYMid meet"
    >
      {/* faint within-cluster wikilink edges */}
      {EDGES.map(([a, b], i) => (
        <line
          key={i}
          x1={N[a].x}
          y1={N[a].y}
          x2={N[b].x}
          y2={N[b].y}
          stroke="var(--color-line-strong)"
          strokeWidth={1}
        />
      ))}

      {/* the bridge: a lesson crossing from one project to another */}
      <line
        x1={b0.x}
        y1={b0.y}
        x2={b1.x}
        y2={b1.y}
        stroke="var(--color-accent-dim)"
        strokeWidth={1.5}
        strokeOpacity={0.5}
      />
      {/* the recall pulse — a lit segment traveling the bridge (motion only) */}
      <line
        className="g-pulse"
        x1={b0.x}
        y1={b0.y}
        x2={b1.x}
        y2={b1.y}
        stroke="var(--color-accent)"
        strokeWidth={2}
        strokeLinecap="round"
        strokeDasharray="8 34"
        pathLength={42}
      />

      {/* nodes — bare marks, no tile behind them */}
      {NODES.map((n, i) => (
        <g key={n.id}>
          <circle
            className={n.hot ? "g-node" : undefined}
            style={n.hot ? { animationDelay: `${i * 0.4}s` } : undefined}
            cx={n.x}
            cy={n.y}
            r={n.hot ? 6 : 4}
            fill={n.hot ? "var(--color-accent)" : "var(--color-surface-2)"}
            stroke={n.hot ? "var(--color-accent)" : "var(--color-line-strong)"}
            strokeWidth={1.5}
          />
          {n.label && (
            <text
              x={n.x + 12}
              y={n.y + 4}
              className="font-mono"
              fontSize={12}
              fill="var(--color-ink-faint)"
            >
              {n.label}
            </text>
          )}
        </g>
      ))}
    </svg>
  );
}
