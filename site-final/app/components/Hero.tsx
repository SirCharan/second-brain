"use client";

import { useEffect, useState } from "react";
import GraphField from "./GraphField";
import CopyCommand from "./CopyCommand";
import { GitHubMark } from "./Mark";

const REPO = "https://github.com/SirCharan/second-brain";
const INSTALL = "/plugin marketplace add SirCharan/second-brain";

/** Hero: copy left-pocketed so the graph stays the star on the right.
 *  ?cinematic=1 → launch-reel drama (hotter cascade, lighter scrim). */
export default function Hero() {
  const [cinematic, setCinematic] = useState(false);
  const [reel, setReel] = useState(false);

  useEffect(() => {
    const q = new URLSearchParams(window.location.search);
    setCinematic(q.has("cinematic") || q.has("launch"));
    setReel(q.has("reel")); // pure graph, hide copy for screen record
  }, []);

  return (
    <section
      id="top"
      data-cinematic={cinematic ? "1" : "0"}
      className="relative flex min-h-svh flex-col justify-end overflow-hidden px-6 pb-16 pt-28 sm:justify-center sm:px-10 sm:pb-24 sm:pt-24"
    >
      <GraphField
        mode="interactive"
        cinematic={cinematic}
        className="absolute inset-0 h-full w-full"
      />

      {/* Scrim only under the copy column — lighter in cinematic so the vault reads on video */}
      {!reel && (
        <div
          className="pointer-events-none absolute inset-0"
          style={{
            background: cinematic
              ? [
                  "linear-gradient(to right, rgba(12,10,9,0.72) 0%, rgba(12,10,9,0.35) 26%, transparent 52%)",
                  "linear-gradient(to top, var(--color-bg) 0%, rgba(12,10,9,0.35) 12%, transparent 36%)",
                ].join(", ")
              : [
                  "linear-gradient(to right, rgba(12,10,9,0.88) 0%, rgba(12,10,9,0.62) 28%, rgba(12,10,9,0.22) 48%, transparent 62%)",
                  "linear-gradient(to top, var(--color-bg) 0%, rgba(12,10,9,0.5) 14%, transparent 42%)",
                ].join(", "),
          }}
        />
      )}

      {!reel && (
        <p className="pointer-events-none absolute right-6 top-24 z-10 hidden font-mono text-[11px] text-ink-faint lg:block">
          hover · drag · pan · ⌘/ctrl-scroll zoom
        </p>
      )}

      {!reel && (
        <div className="pointer-events-none relative z-10 mx-auto w-full max-w-6xl">
          <div className="max-w-[min(100%,34rem)]">
            <p className="font-mono text-[11px] tracking-[0.18em] text-accent uppercase">
              local-first · open source · your disk
            </p>

            <h1 className="mt-5 font-display text-[clamp(2.15rem,6.5vw,3.75rem)] leading-[1.05] tracking-tight">
              <span className="block whitespace-nowrap">The chat ends.</span>
              <span className="block whitespace-nowrap text-accent">The memory stays.</span>
            </h1>

            <div className="max-w-md">
              <p className="mt-6 text-base leading-relaxed text-ink-dim sm:text-lg">
                second-brain captures every AI session into Markdown on your machine.
                Switch models, clear the window, close the laptop. Nothing walks away.
              </p>

              <div className="pointer-events-auto mt-9">
                <CopyCommand command={INSTALL} />
                <div className="mt-3 flex flex-wrap items-center gap-x-5 gap-y-2 text-sm text-ink-faint">
                  <span>
                    or <code className="font-mono text-ink-dim">./install.sh</code>
                  </span>
                  <a
                    href={REPO}
                    target="_blank"
                    rel="noreferrer"
                    className="flex items-center gap-1.5 text-ink-dim transition-colors hover:text-ink"
                  >
                    <GitHubMark size={15} />
                    Star on GitHub
                  </a>
                  <span>Apache-2.0</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}
    </section>
  );
}
