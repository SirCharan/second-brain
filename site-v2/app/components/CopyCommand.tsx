"use client";

import { useState } from "react";

const CMD = "/plugin marketplace add SirCharan/second-brain";

export default function CopyCommand({
  className = "",
  large = false,
}: {
  className?: string;
  large?: boolean;
}) {
  const [copied, setCopied] = useState(false);

  async function copy() {
    try {
      await navigator.clipboard.writeText(CMD);
      setCopied(true);
      window.setTimeout(() => setCopied(false), 1600);
    } catch {
      // fallback: select nothing loud
    }
  }

  return (
    <button
      type="button"
      onClick={copy}
      className={[
        "group mono inline-flex max-w-full items-center gap-3 rounded-md border border-border bg-surface text-left text-fg transition-colors duration-200",
        "hover:border-accent/50 hover:bg-bg-elevated",
        large ? "px-4 py-3 text-[13px] sm:text-sm" : "px-3 py-2 text-xs sm:text-[13px]",
        className,
      ].join(" ")}
      aria-label={copied ? "Copied install command" : "Copy install command"}
    >
      <span className="shrink-0 text-accent" aria-hidden>
        $
      </span>
      <span className="min-w-0 truncate text-fg-dim group-hover:text-fg">{CMD}</span>
      <span
        className={[
          "ml-auto shrink-0 text-[11px] tracking-wide uppercase transition-colors",
          copied ? "text-accent-hot" : "text-muted group-hover:text-fg-dim",
        ].join(" ")}
      >
        {copied ? "copied" : "copy"}
      </span>
    </button>
  );
}
