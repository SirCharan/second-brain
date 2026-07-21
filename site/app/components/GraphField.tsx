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
  cx: number; // community anchor (fraction of canvas)
  cy: number;
  cs: number; // anchor strength
  x?: number;
  y?: number;
  vx?: number;
  vy?: number;
  fx?: number | null;
  fy?: number | null;
};
type GLink = { source: GNode | number; target: GNode | number };
type Pulse = { link: number; t: number; speed: number };

/* Communities coloured like the real Obsidian graph: a big coral cluster, a tan
   cluster, a yellow arm, a brown-hub cluster, the radial fan, and grey orphans. */
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
    const n: GNode = {
      id: id++,
      comm,
      deg: 0,
      color: pick(c.palette),
      r: 3,
      cx: c.cx,
      cy: c.cy,
      cs,
    };
    nodes.push(n);
    return n;
  };
  const addLink = (a: number, b: number) => {
    if (a === b) return;
    links.push({ source: a, target: b });
    nodes[a].deg++;
    nodes[b].deg++;
  };

  // sizes scale down a bit on small screens
  const S = scale;
  // coral (0), tan (1), yellow (2), brown (3) — clustered communities with a hub each
  const sized = [
    { comm: 0, n: Math.round(92 * S) },
    { comm: 1, n: Math.round(64 * S) },
    { comm: 2, n: Math.round(34 * S) },
    { comm: 3, n: Math.round(40 * S) },
  ];
  const hubIds: number[] = [];
  // coral (our real "drishti") is the dominant cluster with several mega-hubs
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
      addLink(nd.id, gHubs[(rnd() * gHubs.length) | 0]); // attach to a group hub
      if (nh > 1 && rnd() < 0.35) addLink(nd.id, gHubs[(rnd() * gHubs.length) | 0]);
      // dense intra-community mesh — echoes the real vault (~12 edges/node)
      const extra = 2 + ((rnd() * 4) | 0);
      for (let k = 0; k < extra; k++) {
        const other = start + ((rnd() * (id - start)) | 0);
        if (rnd() < 0.6) addLink(nd.id, other);
      }
    }
  }

  // radial fan (community 4): one big hub, many leaves on pure spokes
  const fanHub = addNode(4, 0.12);
  const fanLeaves = Math.round(74 * S);
  for (let i = 0; i < fanLeaves; i++) {
    const leaf = addNode(4, 0.02);
    addLink(leaf.id, fanHub.id);
  }

  // grey orphans: a few pairs (one link) + singletons, scattered to the edges
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

  // a handful of bridges between community hubs
  for (let i = 0; i < hubIds.length; i++)
    if (rnd() < 0.8) addLink(hubIds[i], hubIds[(i + 1) % hubIds.length]);
  addLink(hubIds[1], fanHub.id); // tan hub links to the fan

  for (const n of nodes) n.r = 2.3 + Math.min(n.deg, 40) * 0.32; // size by degree
  return { nodes, links };
}

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

    // seed each node near its community anchor so clusters separate on settle
    const rnd = mulberry32(23);
    for (const n of nodes) {
      n.x = n.cx * w + (rnd() - 0.5) * w * 0.18;
      n.y = n.cy * h + (rnd() - 0.5) * h * 0.18;
    }

    const sim: Simulation<GNode, undefined> = forceSimulation(nodes)
      .force("charge", forceManyBody().strength(scale < 0.6 ? -18 : -26).theta(0.9))
      .force(
        "link",
        forceLink<GNode, GLink>(links)
          .id((d) => d.id)
          .distance((l) => ((l.source as GNode).comm === 4 ? 30 : 24))
          .strength(0.12),
      )
      .force("x", forceX<GNode>((d) => d.cx * w).strength((d) => d.cs))
      .force("y", forceY<GNode>((d) => d.cy * h).strength((d) => d.cs))
      .force("collide", forceCollide<GNode>().radius((d) => d.r + 1.5))
      .alpha(1)
      .alphaDecay(0.02)
      .velocityDecay(0.42);

    if (!reduced) sim.alphaTarget(0.006).restart();

    // view transform (zoom/pan) — interactive only
    let k = 1,
      tx = 0,
      ty = 0;
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

    let mx = w / 2,
      my = h / 2;
    let hover = -1;
    let dragging: GNode | null = null;
    let panning = false;
    let panLast = { x: 0, y: 0 };
    const neighbors = new Set<number>();

    const toGraph = (cx: number, cy: number) => ({ x: (cx - tx) / k, y: (cy - ty) / k });
    function nodeAt(gx: number, gy: number) {
      for (let i = nodes.length - 1; i >= 0; i--) {
        const n = nodes[i];
        const dx = (n.x ?? 0) - gx;
        const dy = (n.y ?? 0) - gy;
        const rr = n.r + 4 / k;
        if (dx * dx + dy * dy < rr * rr) return n;
      }
      return null;
    }
    function computeNeighbors(nid: number) {
      neighbors.clear();
      for (const l of links) {
        const s = (l.source as GNode).id;
        const t = (l.target as GNode).id;
        if (s === nid) neighbors.add(t);
        if (t === nid) neighbors.add(s);
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
      const nid = n ? n.id : -1;
      if (nid !== hover) {
        hover = nid;
        if (nid >= 0) computeNeighbors(nid);
        else neighbors.clear();
      }
      canvas.style.cursor = n ? "grab" : "grab";
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
      if (pulses.length > 7) return;
      pulses.push({ link: (Math.random() * links.length) | 0, t: 0, speed: 0.006 + Math.random() * 0.01 });
    }

    function draw() {
      ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
      ctx.clearRect(0, 0, w, h);
      // ambient parallax vs interactive zoom/pan
      if (mode === "ambient") {
        ctx.translate((mx - w / 2) * 0.01, (my - h / 2) * 0.01);
      } else {
        ctx.translate(tx, ty);
        ctx.scale(k, k);
      }

      // links
      for (const l of links) {
        const s = l.source as GNode;
        const t = l.target as GNode;
        const lit = hover >= 0 && (s.id === hover || t.id === hover);
        ctx.strokeStyle = lit
          ? "rgba(230,165,75,0.55)"
          : hover >= 0
            ? "rgba(243,238,229,0.04)"
            : "rgba(243,238,229,0.09)";
        ctx.lineWidth = (lit ? 1.1 : 0.6) / (mode === "interactive" ? k : 1);
        ctx.beginPath();
        ctx.moveTo(s.x!, s.y!);
        ctx.lineTo(t.x!, t.y!);
        ctx.stroke();
      }

      // pulses
      for (const p of pulses) {
        const l = links[p.link];
        const s = l.source as GNode;
        const t = l.target as GNode;
        const x = s.x! + (t.x! - s.x!) * p.t;
        const y = s.y! + (t.y! - s.y!) * p.t;
        ctx.beginPath();
        ctx.arc(x, y, 2 / (mode === "interactive" ? k : 1), 0, Math.PI * 2);
        ctx.fillStyle = "rgba(230,165,75,0.95)";
        ctx.shadowColor = "rgba(230,165,75,0.9)";
        ctx.shadowBlur = 7;
        ctx.fill();
        ctx.shadowBlur = 0;
      }

      // nodes
      for (const n of nodes) {
        const dim = hover >= 0 && n.id !== hover && !neighbors.has(n.id);
        ctx.globalAlpha = dim ? 0.18 : 1;
        ctx.beginPath();
        ctx.arc(n.x!, n.y!, n.r, 0, Math.PI * 2);
        ctx.fillStyle = n.id === hover ? "#f3eee5" : n.color;
        ctx.fill();
        ctx.globalAlpha = 1;
      }
    }

    let raf = 0;
    let running = true;
    function frame() {
      if (!reduced) {
        pulseClock++;
        if (pulseClock % 30 === 0) spawnPulse();
        for (let i = pulses.length - 1; i >= 0; i--) {
          pulses[i].t += pulses[i].speed;
          if (pulses[i].t >= 1) pulses.splice(i, 1);
        }
      }
      draw();
      if (running) raf = requestAnimationFrame(frame);
    }

    if (reduced) {
      for (let i = 0; i < 400; i++) sim.tick();
      draw();
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
