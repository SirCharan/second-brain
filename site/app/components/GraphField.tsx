"use client";

import { useEffect, useRef } from "react";
import {
  forceSimulation,
  forceManyBody,
  forceLink,
  forceCollide,
  forceX,
  forceY,
  type Simulation,
} from "d3-force";

type Mode = "ambient" | "interactive";

type GNode = {
  id: number;
  comm: number;
  deg: number;
  color: string;
  r: number;
  cx: number;
  cy: number;
  cs: number;
  born?: number;
  x?: number;
  y?: number;
  vx?: number;
  vy?: number;
  fx?: number | null;
  fy?: number | null;
};
type GLink = { source: GNode | number; target: GNode | number; _on?: boolean };
type Pulse = { link: number; t: number; speed: number };

const COMMUNITIES = [
  { key: "coral", palette: ["#e2532f", "#e0603a", "#d9542c", "#e86a42"], cx: 0.72, cy: 0.66 },
  { key: "tan", palette: ["#c9a35f", "#b8935a", "#caa869", "#bd9a54"], cx: 0.46, cy: 0.5 },
  { key: "yellow", palette: ["#e8c94a", "#ecd24f", "#f0d84a", "#e3c24d"], cx: 0.22, cy: 0.42 },
  { key: "brown", palette: ["#8a6f4a", "#9c7d50", "#7d6543"], cx: 0.4, cy: 0.72 },
  { key: "fan", palette: ["#c9a35f", "#caa869", "#d8b878"], cx: 0.78, cy: 0.24 },
  { key: "grey", palette: ["#b9b3ab", "#a7a199"], cx: 0.5, cy: 0.5 },
];

function mulberry32(seed: number) {
  return () => {
    seed |= 0;
    seed = (seed + 0x6d2b79f5) | 0;
    let t = Math.imul(seed ^ (seed >>> 15), 1 | seed);
    t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
  };
}

function buildGraph(seed: number, scale: number) {
  const rnd = mulberry32(seed);
  const nodes: GNode[] = [];
  const links: GLink[] = [];
  let id = 0;

  const pick = (arr: string[]) => arr[(rnd() * arr.length) | 0];
  const addNode = (comm: number, cs = 0.05) => {
    const c = COMMUNITIES[comm];
    const n: GNode = { id: id++, comm, deg: 0, color: pick(c.palette), r: 3, cx: c.cx, cy: c.cy, cs };
    nodes.push(n);
    return n;
  };
  const addLink = (a: number, b: number) => {
    if (a === b) return;
    links.push({ source: a, target: b });
    nodes[a].deg++;
    nodes[b].deg++;
  };

  const S = scale;
  const sized = [
    { comm: 0, n: Math.round(92 * S) },
    { comm: 1, n: Math.round(64 * S) },
    { comm: 2, n: Math.round(34 * S) },
    { comm: 3, n: Math.round(40 * S) },
  ];
  const hubIds: number[] = [];
  const HUBS_PER: Record<number, number> = { 0: 3, 1: 2, 2: 1, 3: 2 };
  for (const grp of sized) {
    const start = id;
    const gHubs: number[] = [];
    const nh = HUBS_PER[grp.comm] ?? 1;
    for (let hI = 0; hI < nh; hI++) {
      const hub = addNode(grp.comm, 0.09);
      gHubs.push(hub.id);
      hubIds.push(hub.id);
    }
    for (let i = gHubs.length; i < grp.n; i++) {
      const nd = addNode(grp.comm);
      addLink(nd.id, gHubs[(rnd() * gHubs.length) | 0]);
      if (nh > 1 && rnd() < 0.35) addLink(nd.id, gHubs[(rnd() * gHubs.length) | 0]);
      const extra = 2 + ((rnd() * 4) | 0);
      for (let k = 0; k < extra; k++) {
        const other = start + ((rnd() * (id - start)) | 0);
        if (rnd() < 0.6) addLink(nd.id, other);
      }
    }
  }

  const fanHub = addNode(4, 0.12);
  const fanLeaves = Math.round(74 * S);
  for (let i = 0; i < fanLeaves; i++) addLink(addNode(4, 0.02).id, fanHub.id);

  const orphanSpots = [
    [0.12, 0.12], [0.9, 0.42], [0.06, 0.7], [0.5, 0.08], [0.94, 0.72], [0.16, 0.9],
  ];
  for (let i = 0; i < orphanSpots.length; i++) {
    const a = addNode(5, 0.16);
    a.cx = orphanSpots[i][0];
    a.cy = orphanSpots[i][1];
    if (rnd() < 0.6) {
      const b = addNode(5, 0.16);
      b.cx = a.cx + (rnd() - 0.5) * 0.05;
      b.cy = a.cy + (rnd() - 0.5) * 0.08;
      addLink(a.id, b.id);
    }
  }

  for (let i = 0; i < hubIds.length; i++)
    if (rnd() < 0.8) addLink(hubIds[i], hubIds[(i + 1) % hubIds.length]);
  addLink(hubIds[1], fanHub.id);

  for (const n of nodes) n.r = 2.3 + Math.min(n.deg, 40) * 0.32;
  return { nodes, links };
}

const nid = (x: GNode | number) => (typeof x === "object" ? x.id : x);

export default function GraphField({
  mode = "ambient",
  className = "",
}: {
  mode?: Mode;
  className?: string;
}) {
  const canvasRef = useRef<HTMLCanvasElement>(null);

  useEffect(() => {
    const canvas = canvasRef.current!;
    if (!canvas) return;
    const parent = canvas.parentElement!;
    const ctx = canvas.getContext("2d")!;
    const reduced = window.matchMedia("(prefers-reduced-motion: reduce)").matches;

    let w = parent.clientWidth;
    let h = parent.clientHeight;
    const scale = w < 700 ? 0.42 : w < 1100 ? 0.72 : 1;
    const { nodes, links } = buildGraph(11, scale);
    const rnd = mulberry32(23);

    // adjacency (numeric) for placing a new node next to an already-shown neighbour
    const incident = new Map<number, number[]>();
    for (const l of links) {
      const a = l.source as number;
      const b = l.target as number;
      (incident.get(a) ?? incident.set(a, []).get(a)!).push(b);
      (incident.get(b) ?? incident.set(b, []).get(b)!).push(a);
    }

    // progressive reveal: the vault wires itself up in real time
    const active: GNode[] = [];
    const activeLinks: GLink[] = [];
    const shown = new Uint8Array(nodes.length);
    let cursor = 0;
    const GROW_MS = 460;

    const linkForce = forceLink<GNode, GLink>(activeLinks)
      .id((d) => d.id)
      .distance((l) => ((l.source as GNode).comm === 4 ? 30 : 24))
      .strength(0.12);

    const sim: Simulation<GNode, undefined> = forceSimulation(active)
      .force("charge", forceManyBody().strength(scale < 0.6 ? -18 : -26).theta(0.9))
      .force("link", linkForce)
      .force("x", forceX<GNode>((d) => d.cx * w).strength((d) => d.cs))
      .force("y", forceY<GNode>((d) => d.cy * h).strength((d) => d.cs))
      .force("collide", forceCollide<GNode>().radius((d) => d.r + 1.5))
      .alpha(0.9)
      .alphaDecay(0.02)
      .velocityDecay(0.42);
    sim.stop();

    function reveal(count: number, now: number) {
      for (let c = 0; c < count && cursor < nodes.length; c++) {
        const n = nodes[cursor++];
        // place beside a revealed neighbour so the link visibly grows out of it
        let placed = false;
        const inc = incident.get(n.id);
        if (inc) {
          for (const o of inc) {
            if (shown[o]) {
              n.x = (nodes[o].x ?? n.cx * w) + (rnd() - 0.5) * 22;
              n.y = (nodes[o].y ?? n.cy * h) + (rnd() - 0.5) * 22;
              placed = true;
              break;
            }
          }
        }
        if (!placed) {
          n.x = n.cx * w + (rnd() - 0.5) * w * 0.14;
          n.y = n.cy * h + (rnd() - 0.5) * h * 0.14;
        }
        n.born = now;
        shown[n.id] = 1;
        active.push(n);
      }
      for (const l of links) {
        if (l._on) continue;
        if (shown[nid(l.source)] && shown[nid(l.target)]) {
          l._on = true;
          activeLinks.push(l);
        }
      }
      sim.nodes(active);
      linkForce.links(activeLinks);
      sim.alpha(Math.max(sim.alpha(), 0.7)).restart();
    }

    let dpr = Math.min(window.devicePixelRatio || 1, 2);
    function resize() {
      w = parent.clientWidth;
      h = parent.clientHeight;
      dpr = Math.min(window.devicePixelRatio || 1, 2);
      canvas.width = w * dpr;
      canvas.height = h * dpr;
      canvas.style.width = w + "px";
      canvas.style.height = h + "px";
    }
    resize();
    const ro = new ResizeObserver(resize);
    ro.observe(parent);

    // view transform + pointer state
    let k = 1, tx = 0, ty = 0;
    let mx = w / 2, my = h / 2;
    let hover = -1;
    let dragging: GNode | null = null;
    let panning = false;
    let panLast = { x: 0, y: 0 };
    const neighbors = new Set<number>();

    const toGraph = (cx: number, cy: number) => ({ x: (cx - tx) / k, y: (cy - ty) / k });
    function nodeAt(gx: number, gy: number) {
      for (let i = active.length - 1; i >= 0; i--) {
        const n = active[i];
        const dx = (n.x ?? 0) - gx;
        const dy = (n.y ?? 0) - gy;
        const rr = n.r + 4 / k;
        if (dx * dx + dy * dy < rr * rr) return n;
      }
      return null;
    }
    function computeNeighbors(nnid: number) {
      neighbors.clear();
      for (const l of activeLinks) {
        const s = nid(l.source);
        const t = nid(l.target);
        if (s === nnid) neighbors.add(t);
        if (t === nnid) neighbors.add(s);
      }
    }
    const local = (e: PointerEvent) => {
      const rect = canvas.getBoundingClientRect();
      return { x: e.clientX - rect.left, y: e.clientY - rect.top };
    };
    const onMove = (e: PointerEvent) => {
      const p = local(e);
      mx = p.x;
      my = p.y;
      if (mode !== "interactive") return;
      if (dragging) {
        const g = toGraph(p.x, p.y);
        dragging.fx = g.x;
        dragging.fy = g.y;
        sim.alphaTarget(0.15).restart();
        return;
      }
      if (panning) {
        tx += p.x - panLast.x;
        ty += p.y - panLast.y;
        panLast = p;
        return;
      }
      const g = toGraph(p.x, p.y);
      const n = nodeAt(g.x, g.y);
      const nnid = n ? n.id : -1;
      if (nnid !== hover) {
        hover = nnid;
        if (nnid >= 0) computeNeighbors(nnid);
        else neighbors.clear();
      }
      canvas.style.cursor = "grab";
    };
    const onDown = (e: PointerEvent) => {
      if (mode !== "interactive") return;
      const p = local(e);
      const g = toGraph(p.x, p.y);
      const n = nodeAt(g.x, g.y);
      if (n) {
        dragging = n;
        n.fx = g.x;
        n.fy = g.y;
        canvas.style.cursor = "grabbing";
        sim.alphaTarget(0.2).restart();
      } else {
        panning = true;
        panLast = p;
        canvas.style.cursor = "grabbing";
      }
    };
    const onUp = () => {
      if (dragging) {
        dragging.fx = null;
        dragging.fy = null;
        dragging = null;
        sim.alphaTarget(0.006);
      }
      panning = false;
      canvas.style.cursor = "grab";
    };
    const onWheel = (e: WheelEvent) => {
      if (mode !== "interactive") return;
      e.preventDefault();
      const rect = canvas.getBoundingClientRect();
      const px = e.clientX - rect.left;
      const py = e.clientY - rect.top;
      const factor = Math.exp(-e.deltaY * 0.0016);
      const nk = Math.max(0.35, Math.min(4, k * factor));
      tx = px - (px - tx) * (nk / k);
      ty = py - (py - ty) * (nk / k);
      k = nk;
    };
    if (mode === "interactive") {
      canvas.addEventListener("pointermove", onMove);
      canvas.addEventListener("pointerdown", onDown);
      window.addEventListener("pointerup", onUp);
      canvas.addEventListener("wheel", onWheel, { passive: false });
    } else {
      parent.addEventListener("pointermove", onMove);
    }

    const pulses: Pulse[] = [];
    let pulseClock = 0;
    function spawnPulse() {
      if (pulses.length > 7 || activeLinks.length === 0) return;
      pulses.push({ link: (Math.random() * activeLinks.length) | 0, t: 0, speed: 0.006 + Math.random() * 0.01 });
    }

    const growOf = (n: GNode, now: number) => {
      if (reduced || n.born == null) return 1;
      const g = Math.min(1, (now - n.born) / GROW_MS);
      return g * g * (3 - 2 * g); // smoothstep
    };

    function draw(now: number) {
      ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
      ctx.clearRect(0, 0, w, h);
      if (mode === "ambient") ctx.translate((mx - w / 2) * 0.01, (my - h / 2) * 0.01);
      else {
        ctx.translate(tx, ty);
        ctx.scale(k, k);
      }
      const sw = mode === "interactive" ? k : 1;

      for (const l of activeLinks) {
        const s = l.source as GNode;
        const t = l.target as GNode;
        const g = Math.min(growOf(s, now), growOf(t, now));
        if (g <= 0.01) continue;
        const lit = hover >= 0 && (s.id === hover || t.id === hover);
        ctx.strokeStyle = lit
          ? `rgba(230,165,75,${0.55 * g})`
          : hover >= 0
            ? `rgba(243,238,229,${0.04 * g})`
            : `rgba(243,238,229,${0.09 * g})`;
        ctx.lineWidth = (lit ? 1.1 : 0.6) / sw;
        ctx.beginPath();
        ctx.moveTo(s.x!, s.y!);
        ctx.lineTo(t.x!, t.y!);
        ctx.stroke();
      }

      for (const p of pulses) {
        const l = activeLinks[p.link];
        if (!l) continue;
        const s = l.source as GNode;
        const t = l.target as GNode;
        const x = s.x! + (t.x! - s.x!) * p.t;
        const y = s.y! + (t.y! - s.y!) * p.t;
        ctx.beginPath();
        ctx.arc(x, y, 2 / sw, 0, Math.PI * 2);
        ctx.fillStyle = "rgba(230,165,75,0.95)";
        ctx.shadowColor = "rgba(230,165,75,0.9)";
        ctx.shadowBlur = 7;
        ctx.fill();
        ctx.shadowBlur = 0;
      }

      for (const n of active) {
        const g = growOf(n, now);
        const dim = hover >= 0 && n.id !== hover && !neighbors.has(n.id);
        ctx.globalAlpha = (dim ? 0.18 : 1) * g;
        ctx.beginPath();
        ctx.arc(n.x!, n.y!, n.r * (0.4 + 0.6 * g), 0, Math.PI * 2);
        ctx.fillStyle = n.id === hover ? "#f3eee5" : n.color;
        ctx.fill();
        ctx.globalAlpha = 1;
      }
    }

    let raf = 0;
    let running = true;
    let lastReveal = 0;
    function frame(now: number) {
      if (!reduced) {
        if (cursor < nodes.length && now - lastReveal > 55) {
          reveal(6, now);
          lastReveal = now;
        }
        pulseClock++;
        if (pulseClock % 30 === 0) spawnPulse();
        for (let i = pulses.length - 1; i >= 0; i--) {
          pulses[i].t += pulses[i].speed;
          if (pulses[i].t >= 1) pulses.splice(i, 1);
        }
      }
      draw(now);
      if (running) raf = requestAnimationFrame(frame);
    }

    if (reduced) {
      reveal(nodes.length, 0);
      for (let i = 0; i < 400; i++) sim.tick();
      draw(0);
    } else {
      raf = requestAnimationFrame(frame);
    }

    const onVis = () => {
      if (document.hidden) {
        running = false;
        cancelAnimationFrame(raf);
        sim.stop();
      } else if (!reduced) {
        running = true;
        sim.alphaTarget(0.006).restart();
        raf = requestAnimationFrame(frame);
      }
    };
    document.addEventListener("visibilitychange", onVis);
    const io = new IntersectionObserver(
      ([e]) => {
        if (reduced) return;
        if (e.isIntersecting && !running) {
          running = true;
          sim.alphaTarget(0.006).restart();
          raf = requestAnimationFrame(frame);
        } else if (!e.isIntersecting) {
          running = false;
          cancelAnimationFrame(raf);
          sim.stop();
        }
      },
      { threshold: 0 },
    );
    io.observe(parent);

    return () => {
      running = false;
      cancelAnimationFrame(raf);
      sim.stop();
      ro.disconnect();
      io.disconnect();
      document.removeEventListener("visibilitychange", onVis);
      canvas.removeEventListener("pointermove", onMove);
      canvas.removeEventListener("pointerdown", onDown);
      window.removeEventListener("pointerup", onUp);
      canvas.removeEventListener("wheel", onWheel);
      parent.removeEventListener("pointermove", onMove);
    };
  }, [mode]);

  return (
    <canvas
      ref={canvasRef}
      aria-hidden="true"
      className={className}
      style={{ pointerEvents: mode === "interactive" ? "auto" : "none", touchAction: mode === "interactive" ? "none" : undefined }}
    />
  );
}
