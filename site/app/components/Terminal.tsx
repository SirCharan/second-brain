/** Honest terminal surface — the tool genuinely runs in a CLI. No fake traffic
 * lights, no toy-SDK syntax highlighting; just a warm panel with a label strip. */
export default function Terminal({
  label,
  status,
  children,
  className = "",
}: {
  label: string;
  status?: string;
  children: React.ReactNode;
  className?: string;
}) {
  return (
    <div
      className={`overflow-hidden rounded-xl border border-line-strong bg-surface/90 shadow-[var(--shadow-lift)] backdrop-blur-sm ${className}`}
    >
      <div className="flex items-center justify-between border-b border-line px-4 py-2.5">
        <span className="font-mono text-xs text-ink-dim">{label}</span>
        {status && (
          <span className="font-mono text-[11px] text-ink-faint">{status}</span>
        )}
      </div>
      <div className="px-4 py-4 font-mono text-[13px] leading-relaxed">{children}</div>
    </div>
  );
}
