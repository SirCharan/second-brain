import { ImageResponse } from "next/og";
import { readFileSync } from "fs";
import { join } from "path";

export const runtime = "nodejs";
export const alt = "second-brain — your second brain, wired to every model";
export const size = { width: 1200, height: 630 };
export const contentType = "image/png";

const gambarino = readFileSync(join(process.cwd(), "app/og/Gambarino-Regular.ttf"));

// a small, deterministic node cluster (nodes = notes) for the top-right field
const DOTS = [
  [880, 90, 7, "#e6a54b"], [960, 140, 4, "#e8c56a"], [1030, 96, 5, "#f0e7d6"],
  [910, 200, 5, "#d98a3d"], [1000, 220, 9, "#e6a54b"], [1080, 170, 4, "#e8c56a"],
  [850, 160, 4, "#f0e7d6"], [1090, 250, 5, "#e6a54b"], [960, 300, 4, "#e8c56a"],
  [1040, 320, 6, "#e6a54b"], [900, 280, 4, "#d98a3d"], [1120, 120, 3, "#f0e7d6"],
] as const;

export default function OG() {
  return new ImageResponse(
    (
      <div
        style={{
          width: "100%",
          height: "100%",
          display: "flex",
          flexDirection: "column",
          justifyContent: "flex-end",
          background: "#0c0a09",
          padding: "72px",
          position: "relative",
          fontFamily: "Gambarino",
        }}
      >
        {DOTS.map(([x, y, r, c], i) => (
          <div
            key={i}
            style={{
              position: "absolute",
              left: x,
              top: y,
              width: r * 2,
              height: r * 2,
              borderRadius: r,
              background: c as string,
            }}
          />
        ))}
        <div style={{ display: "flex", fontSize: 104, color: "#f3eee5", letterSpacing: "-0.02em" }}>
          second-brain
        </div>
        <div style={{ display: "flex", flexWrap: "wrap", marginTop: 18, fontSize: 44, color: "#a99f91" }}>
          Your second brain,&nbsp;
          <span style={{ color: "#e6a54b" }}>wired to every model.</span>
        </div>
        <div style={{ display: "flex", marginTop: 40, fontSize: 26, color: "#8a8074" }}>
          local-first AI memory · github.com/SirCharan/second-brain
        </div>
        <div style={{ position: "absolute", left: 72, bottom: 60, width: 64, height: 3, background: "#e6a54b" }} />
      </div>
    ),
    { ...size, fonts: [{ name: "Gambarino", data: gambarino, style: "normal", weight: 400 }] },
  );
}
