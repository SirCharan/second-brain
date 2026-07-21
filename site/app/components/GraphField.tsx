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
  deg: number;
  color: string;
  r: number;
  x?: number;
  y?: number;
  vx?: number;
  vy?: number;
  fx?: number | null;
  fy?: number | null;
};
type GLink = { source: GNode | number; target: GNode | number };
type Pulse = { link: number; t: number; speed: number };

/* warm Obsidian palette — amber heaviest, then honey-yellow, then cream */
const PALETTE = ["#e6a54b", "#e6a54b", "#d98a3d", "#e8c56a", "#e8c56a", "#f0e7d6"];

/* deterministic RNG so the graph looks intentional and identical each load */
function mulberry32(seed: number) {
  return () => {
    seed |= 0;
    seed = (seed + 0x6d2b79f5) | 0;
    let t = Math.imul(seed ^ (seed >>> 15), 1 | seed);
    t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
  };
}

function buildGraph(seed: number, count: number) {
  const rnd = mulberry32(seed);
  const nodes: GNode[] = [];
  for (let i = 0; i < count; i++)
    nodes.push({ id: i, deg: 0, color: PALETTE[(rnd() * PALETTE.length) | 0], r: 3 });

  // a handful of hubs, the rest attach to a nearby hub + a few extra links
  const hubs = [0, 1, 2, 3];
  const links: GLink[] = [];
  const add = (a: number, b: number) => {
    if (a === b) return;
    links.push({ source: a, target: b });
    nodes[a].deg++;
    nodes[b].deg++;
  };
  for (let i = 0; i < count; i++) {
    if (hubs.includes(i)) continue;
    add(i, hubs[(rnd() * hubs.length) | 0]); // spoke to a hub
    if (rnd() < 0.55) add(i, ((rnd() * count) | 0)); // an extra cross-link
  }
  for (let h = 0; h < hubs.length; h++) add(hubs[h], hubs[(h + 1) % hubs.length]); // hub ring

  for (const n of nodes) n.r = 2.4 + Math.min(n.deg, 18) * 0.42; // size by degree
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
    const count = w < 640 ? 42 : 66;
    const { nodes, links } = buildGraph(7, count);

    // seed positions around center so the settle reads as "pathways forming"
    const rnd = mulberry32(19);
    for (const n of nodes) {
      n.x = w / 2 + (rnd() - 0.5) * w * 0.7;
      n.y = h / 2 + (rnd() - 0.5) * h * 0.7;
    }

    const sim: Simulation<GNode, undefined> = forceSimulation(nodes)
      .force("charge", forceManyBody().strength(w < 640 ? -34 : -52))
      .force(
        "link",
        forceLink<GNode, GLink>(links)
          .id((d) => d.id)
          .distance(46)
          .strength(0.28),
      )
      .force("x", forceX(() => w / 2).strength(0.028))
      .force("y", forceY(() => h / 2).strength(0.05))
      .force("collide", forceCollide<GNode>().radius((d) => d.r + 3))
      .alpha(1)
      .alphaDecay(0.018)
      .velocityDecay(0.32);

    if (!reduced) sim.alphaTarget(0.008).restart(); // gentle perpetual drift

    let dpr = Math.min(window.devicePixelRatio || 1, 2);
    function resize() {
      w = parent.clientWidth;
      h = parent.clientHeight;
      dpr = Math.min(window.devicePixelRatio || 1, 2);
      canvas.width = w * dpr;
      canvas.height = h * dpr;
      canvas.style.width = w + "px";
      canvas.style.height = h + "px";
      ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
    }
    resize();
    const ro = new ResizeObserver(resize);
    ro.observe(parent);

    // pointer state
    let mx = w / 2,
      my = h / 2; // for ambient parallax
    let hover = -1;
    let dragging: GNode | null = null;
    const neighbors = new Set<number>();

    function nodeAt(px: number, py: number) {
      for (const n of nodes) {
        const dx = (n.x ?? 0) - px;
        const dy = (n.y ?? 0) - py;
        if (dx * dx + dy * dy < (n.r + 6) * (n.r + 6)) return n;
      }
      return null;
    }
    function computeNeighbors(id: number) {
      neighbors.clear();
      for (const l of links) {
        const s = (l.source as GNode).id;
        const t = (l.target as GNode).id;
        if (s === id) neighbors.add(t);
        if (t === id) neighbors.add(s);
      }
    }

    function toLocal(e: PointerEvent) {
      const rect = canvas.getBoundingClientRect();
      return { x: e.clientX - rect.left, y: e.clientY - rect.top };
    }
    const onMove = (e: PointerEvent) => {
      const p = toLocal(e);
      mx = p.x;
      my = p.y;
      if (mode !== "interactive") return;
      if (dragging) {
        dragging.fx = p.x;
        dragging.fy = p.y;
        sim.alphaTarget(0.2).restart();
        return;
      }
      const n = nodeAt(p.x, p.y);
      const id = n ? n.id : -1;
      if (id !== hover) {
        hover = id;
        if (id >= 0) computeNeighbors(id);
        else neighbors.clear();
      }
      canvas.style.cursor = n ? "grab" : "default";
    };
    const onDown = (e: PointerEvent) => {
      if (mode !== "interactive") return;
      const p = toLocal(e);
      const n = nodeAt(p.x, p.y);
      if (n) {
        dragging = n;
        n.fx = p.x;
        n.fy = p.y;
        canvas.style.cursor = "grabbing";
        sim.alphaTarget(0.25).restart();
      }
    };
    const onUp = () => {
      if (dragging) {
        dragging.fx = null;
        dragging.fy = null;
        dragging = null;
        sim.alphaTarget(0.008); // spring back into the layout
        canvas.style.cursor = "grab";
      }
    };
    if (mode === "interactive") {
      canvas.addEventListener("pointermove", onMove);
      canvas.addEventListener("pointerdown", onDown);
      window.addEventListener("pointerup", onUp);
    } else {
      parent.addEventListener("pointermove", onMove);
    }

    // amber signal pulses traveling edges (the neural firing)
    const pulses: Pulse[] = [];
    let pulseClock = 0;
    function spawnPulse() {
      if (pulses.length > 5) return;
      pulses.push({ link: (Math.random() * links.length) | 0, t: 0, speed: 0.006 + Math.random() * 0.01 });
    }

    function draw() {
      ctx.clearRect(0, 0, w, h);
      // ambient parallax: nudge the whole field a few px toward the pointer
      const ox = mode === "ambient" ? (mx - w / 2) * 0.012 : 0;
      const oy = mode === "ambient" ? (my - h / 2) * 0.012 : 0;
      ctx.save();
      ctx.translate(ox, oy);

      // links
      for (const l of links) {
        const s = l.source as GNode;
        const t = l.target as GNode;
        const lit =
          hover >= 0 && (s.id === hover || t.id === hover);
        ctx.strokeStyle = lit
          ? "rgba(230,165,75,0.5)"
          : hover >= 0
            ? "rgba(243,238,229,0.05)"
            : "rgba(243,238,229,0.11)";
        ctx.lineWidth = lit ? 1.1 : 0.7;
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
        ctx.arc(x, y, 2.2, 0, Math.PI * 2);
        ctx.fillStyle = "rgba(230,165,75,0.95)";
        ctx.shadowColor = "rgba(230,165,75,0.9)";
        ctx.shadowBlur = 8;
        ctx.fill();
        ctx.shadowBlur = 0;
      }

      // nodes
      for (const n of nodes) {
        const dim = hover >= 0 && n.id !== hover && !neighbors.has(n.id);
        ctx.globalAlpha = dim ? 0.22 : 1;
        ctx.beginPath();
        ctx.arc(n.x!, n.y!, n.r, 0, Math.PI * 2);
        ctx.fillStyle = n.id === hover ? "#f3eee5" : n.color;
        ctx.fill();
        ctx.globalAlpha = 1;
      }
      ctx.restore();
    }

    let raf = 0;
    let running = true;
    function frame() {
      if (!reduced) {
        pulseClock++;
        if (pulseClock % 42 === 0) spawnPulse();
        for (let i = pulses.length - 1; i >= 0; i--) {
          pulses[i].t += pulses[i].speed;
          if (pulses[i].t >= 1) pulses.splice(i, 1);
        }
      }
      draw();
      if (running) raf = requestAnimationFrame(frame);
    }

    if (reduced) {
      for (let i = 0; i < 320; i++) sim.tick(); // settle synchronously
      draw();
    } else {
      raf = requestAnimationFrame(frame);
    }

    // pause when tab hidden or field scrolled off-screen (perf)
    const onVis = () => {
      if (document.hidden) {
        running = false;
        cancelAnimationFrame(raf);
        sim.stop();
      } else if (!reduced) {
        running = true;
        sim.alphaTarget(0.008).restart();
        raf = requestAnimationFrame(frame);
      }
    };
    document.addEventListener("visibilitychange", onVis);
    const io = new IntersectionObserver(
      ([e]) => {
        if (reduced) return;
        if (e.isIntersecting) {
          if (!running) {
            running = true;
            sim.alphaTarget(0.008).restart();
            raf = requestAnimationFrame(frame);
          }
        } else {
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
      parent.removeEventListener("pointermove", onMove);
    };
  }, [mode]);

  return (
    <canvas
      ref={canvasRef}
      aria-hidden="true"
      className={className}
      style={{ pointerEvents: mode === "interactive" ? "auto" : "none" }}
    />
  );
}
