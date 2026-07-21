import { ImageResponse } from "next/og";
import { readFileSync } from "fs";
import { join } from "path";

export const runtime = "nodejs";
export const alt = "second-brain — your second brain, wired to every model";
export const size = { width: 1200, height: 630 };
export const contentType = "image/png";

const gambarino = readFileSync(join(process.cwd(), "app/og/Gambarino-Regular.ttf"));

/* Build a small connected graph (communities + edges + a fan) so the social
   unfurl shows the actual product, not a sparse dot field. */
function graphSvg() {
  let s = 0x2f6b1a3d;
  const rnd = () => {
    s |= 0;
    s = (s + 0x6d2b79f5) | 0;
    let t = Math.imul(s ^ (s >>> 15), 1 | s);
    t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
  };
  type P = { x: number; y: number; r: number; c: string };
  const nodes: P[] = [];
  const links: [number, number][] = [];
  const clusters = [
    { x: 300, y: 300, n: 20, pal: ["#e2532f", "#e0603a", "#d9542c"] },
    { x: 200, y: 170, n: 13, pal: ["#c9a35f", "#b8935a", "#caa869"] },
    { x: 90, y: 250, n: 8, pal: ["#e8c94a", "#ecd24f"] },
  ];
  for (const cl of clusters) {
    const hub = nodes.length;
    nodes.push({ x: cl.x, y: cl.y, r: 9, c: cl.pal[0] });
    for (let i = 1; i < cl.n; i++) {
      const a = rnd() * Math.PI * 2;
      const d = 26 + rnd() * 70;
      const idx = nodes.length;
      nodes.push({ x: cl.x + Math.cos(a) * d, y: cl.y + Math.sin(a) * d, r: 3 + rnd() * 3, c: cl.pal[(rnd() * cl.pal.length) | 0] });
      if (rnd() < 0.7) links.push([idx, hub]);
      if (rnd() < 0.4) links.push([idx, hub + ((rnd() * (idx - hub)) | 0)]);
    }
  }
  const fanHub = nodes.length;
  nodes.push({ x: 430, y: 110, r: 10, c: "#caa869" });
  for (let i = 0; i < 18; i++) {
    const a = (-0.2 + (i / 18) * 2.0) * Math.PI;
    const d = 44 + (i % 3) * 12;
    const idx = nodes.length;
    nodes.push({ x: 430 + Math.cos(a) * d, y: 110 + Math.sin(a) * d, r: 2.5 + rnd() * 1.5, c: "#c9a35f" });
    links.push([idx, fanHub]);
  }
  links.push([0, 20], [20, 33], [0, fanHub]);

  const l = links
    .map(([a, b]) => `<line x1="${nodes[a].x.toFixed(1)}" y1="${nodes[a].y.toFixed(1)}" x2="${nodes[b].x.toFixed(1)}" y2="${nodes[b].y.toFixed(1)}" stroke="rgba(243,238,229,0.18)" stroke-width="1"/>`)
    .join("");
  const c = nodes
    .map((n) => `<circle cx="${n.x.toFixed(1)}" cy="${n.y.toFixed(1)}" r="${n.r.toFixed(1)}" fill="${n.c}"/>`)
    .join("");
  const svg = `<svg xmlns="http://www.w3.org/2000/svg" width="540" height="440" viewBox="-10 20 540 440">${l}${c}</svg>`;
  return `data:image/svg+xml;utf8,${encodeURIComponent(svg)}`;
}

export default function OG() {
  return new ImageResponse(
    (
      <div
        style={{
          width: "100%",
          height: "100%",
          display: "flex",
          background: "#0c0a09",
          padding: "72px",
          position: "relative",
          fontFamily: "Gambarino",
        }}
      >
        {/* eslint-disable-next-line @next/next/no-img-element */}
        <img src={graphSvg()} width={540} height={440} style={{ position: "absolute", right: 30, top: 95 }} alt="" />

        <div style={{ display: "flex", flexDirection: "column", justifyContent: "flex-end", width: "100%" }}>
          <div style={{ display: "flex", fontSize: 104, color: "#f3eee5", letterSpacing: "-0.02em" }}>second-brain</div>
          <div style={{ display: "flex", flexWrap: "wrap", marginTop: 18, fontSize: 44, color: "#a99f91" }}>
            Your second brain,&nbsp;<span style={{ color: "#e6a54b" }}>wired to every model.</span>
          </div>
          <div style={{ display: "flex", marginTop: 40, fontSize: 26, color: "#8a8074" }}>
            local-first AI memory · github.com/SirCharan/second-brain
          </div>
          <div style={{ position: "absolute", left: 72, bottom: 60, width: 64, height: 3, background: "#e6a54b" }} />
        </div>
      </div>
    ),
    { ...size, fonts: [{ name: "Gambarino", data: gambarino, style: "normal", weight: 400 }] },
  );
}
