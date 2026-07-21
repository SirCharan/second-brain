"use client";

import { useState } from "react";

export default function CopyCommand({
  command,
  prompt = "$",
}: {
  command: string;
  prompt?: string;
}) {
  const [copied, setCopied] = useState(false);

  async function copy() {
    try {
      await navigator.clipboard.writeText(command);
      setCopied(true);
      setTimeout(() => setCopied(false), 1600);
    } catch {
      /* clipboard blocked — the command is still visible to select manually */
    }
  }

  return (
    <button
      onClick={copy}
      className="group flex w-full items-start gap-3 rounded-md border border-line bg-surface/70 px-4 py-3 text-left font-mono text-xs leading-relaxed text-ink transition-colors hover:border-line-strong hover:bg-surface-2/70 sm:text-sm"
      aria-label={`Copy: ${command}`}
    >
      <span className="select-none pt-px text-accent">{prompt}</span>
      <code className="min-w-0 flex-1 break-words">{command}</code>
      <span
        className="shrink-0 select-none pt-px text-xs text-ink-faint transition-colors group-hover:text-ink-dim"
        aria-live="polite"
      >
        {copied ? "copied" : "copy"}
      </span>
    </button>
  );
}
