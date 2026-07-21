"use client";

import { useEffect, useRef } from "react";
import {
  forceSimulation,
  forceManyBody,
  forceLink,
  forceCollide,
  forceCenter,
  forceX,
  forceY,
  type Simulation,
  type SimulationNodeDatum,
  type SimulationLinkDatum,
} from "d3-force";

/**
 * Obsidian Graph View motion language (from IMG_9819.MOV):
 * - Force-directed spring web, not orbital rings
 * - Warm yellow / orange / amber / white nodes on pure black
 * - Thin pale links, dense mesh around hubs
 * - Organic settle + continuous micro-jiggle
 * - Cluster expands from a tight seed as notes appear
 */

type GNode = SimulationNodeDatum & {
  id: number;
  r: number;
  color: string;
  born: number;
  heat: number;
};

type GLink = SimulationLinkDatum<GNode> & {
  active: number;
};

const PALETTE = [
  "#f0d24a",
  "#e8c94a",
  "#ecd24f",
  "#e8a838",
  "#d4922a",
  "#f5a623",
  "#f2ede4",
  "#e8e0d0",
  "#c9a35f",
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

function prefersReducedMotion() {
  if (typeof window === "undefined") return true;
  return window.matchMedia("(prefers-reduced-motion: reduce)").matches;
}

function buildGraph(count: number, seed = 42) {
  const rnd = mulberry32(seed);
  const nodes: GNode[] = [];
  const links: GLink[] = [];
  const pick = () => PALETTE[(rnd() * PALETTE.length) | 0];

  // Hub
  nodes.push({
    id: 0,
    r: 6.5,
    color: "#e8a838",
    born: 1,
    heat: 0,
    x: 0,
    y: 0,
  });

  const hubCount = 4;
  for (let i = 1; i <= hubCount; i++) {
    const a = (i / hubCount) * Math.PI * 2 + rnd() * 0.4;
    nodes.push({
      id: i,
      r: 4.2 + rnd() * 1.2,
      color: pick(),
      born: 0,
      heat: 0,
      x: Math.cos(a) * 28,
      y: Math.sin(a) * 28,
    });
    links.push({ source: 0, target: i, active: 0 });
  }

  for (let i = hubCount + 1; i < count; i++) {
    const a = rnd() * Math.PI * 2;
    const dist = 12 + rnd() * 50;
    nodes.push({
      id: i,
      r: 2.2 + rnd() * 2.4,
      color: pick(),
      born: 0,
      heat: 0,
      x: Math.cos(a) * dist,
      y: Math.sin(a) * dist,
    });

    const hub = 1 + ((rnd() * hubCount) | 0);
    links.push({ source: i, target: hub, active: 0 });
    if (rnd() < 0.5) links.push({ source: i, target: 0, active: 0 });
    if (rnd() < 0.55 && i > hubCount + 2) {
      const other = hubCount + 1 + ((rnd() * (i - hubCount - 1)) | 0);
      links.push({ source: i, target: other, active: 0 });
    }
  }

  for (let k = 0; k < Math.floor(count * 0.4); k++) {
    const a = 1 + ((rnd() * (count - 1)) | 0);
    const b = 1 + ((rnd() * (count - 1)) | 0);
    if (a !== b) links.push({ source: a, target: b, active: 0 });
  }

  return { nodes, links };
}

export default function MemoryOrrery() {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const wrapRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const canvas = canvasRef.current;
    const wrap = wrapRef.current;
    if (!canvas || !wrap) return;
    const ctx = canvas.getContext("2d");
    if (!ctx) return;

    const reduced = prefersReducedMotion();
    let w = 0;
    let h = 0;
    let dpr = 1;
    let raf = 0;
    let t0 = performance.now();

    const nodeCount = Math.min(
      78,
      Math.max(52, Math.floor((window.innerWidth * window.innerHeight) / 20000)),
    );
    const { nodes, links } = buildGraph(nodeCount);

    // Local coords around origin; we translate when drawing
    let cx = 0;
    let cy = 0;
    let revealed = reduced ? nodes.length : 1;
    if (reduced) {
      for (const n of nodes) n.born = 1;
    }

    const mouse = { x: 0, y: 0, active: false, hover: -1 };
    const pan = { x: 0, y: 0, ox: 0, oy: 0, dragging: false };

    const sim: Simulation<GNode, GLink> = forceSimulation(nodes)
      .force(
        "charge",
        forceManyBody<GNode>()
          .strength((d) => (d.id === 0 ? -520 : -165))
          .distanceMax(320),
      )
      .force(
        "link",
        forceLink<GNode, GLink>(links)
          .id((d) => d.id)
          .distance((l) => {
            const s = l.source as GNode;
            const t = l.target as GNode;
            if (s.id === 0 || t.id === 0) return 62 + Math.random() * 28;
            return 30 + Math.random() * 42;
          })
          .strength(0.62),
      )
      .force(
        "collide",
        forceCollide<GNode>()
          .radius((d) => d.r + 3.5)
          .iterations(2),
      )
      .force("center", forceCenter(0, 0))
      .force("x", forceX(0).strength(0.04))
      .force("y", forceY(0).strength(0.04))
      .alphaDecay(0.014)
      .velocityDecay(0.32)
      .stop();

    // Warm-start layout in local space
    for (let i = 0; i < 80; i++) sim.tick();

    const toScreen = (n: GNode) => ({
      x: cx + (n.x ?? 0) + pan.x,
      y: cy + (n.y ?? 0) + pan.y,
    });

    const resize = () => {
      const rect = wrap.getBoundingClientRect();
      w = rect.width;
      h = rect.height;
      dpr = Math.min(window.devicePixelRatio || 1, 2);
      canvas.width = Math.floor(w * dpr);
      canvas.height = Math.floor(h * dpr);
      canvas.style.width = `${w}px`;
      canvas.style.height = `${h}px`;
      ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
      // Sit the graph in the right-center (copy lives left)
      cx = w * 0.6;
      cy = h * 0.46;
    };

    resize();

    const onPointerMove = (e: PointerEvent) => {
      const rect = wrap.getBoundingClientRect();
      mouse.x = e.clientX - rect.left;
      mouse.y = e.clientY - rect.top;
      mouse.active = true;

      if (pan.dragging) {
        pan.x = e.clientX - pan.ox;
        pan.y = e.clientY - pan.oy;
      }

      let best = -1;
      let bestD = 16;
      for (let i = 0; i < revealed; i++) {
        if (nodes[i].born < 0.4) continue;
        const p = toScreen(nodes[i]);
        const d = Math.hypot(p.x - mouse.x, p.y - mouse.y);
        if (d < bestD) {
          bestD = d;
          best = i;
        }
      }
      mouse.hover = best;
    };

    const onPointerDown = (e: PointerEvent) => {
      pan.dragging = true;
      pan.ox = e.clientX - pan.x;
      pan.oy = e.clientY - pan.y;
      wrap.setPointerCapture(e.pointerId);
    };
    const onPointerUp = (e: PointerEvent) => {
      pan.dragging = false;
      try {
        wrap.releasePointerCapture(e.pointerId);
      } catch {
        /* ignore */
      }
    };
    const onLeave = () => {
      mouse.active = false;
      mouse.hover = -1;
      pan.dragging = false;
    };

    wrap.addEventListener("pointermove", onPointerMove);
    wrap.addEventListener("pointerdown", onPointerDown);
    wrap.addEventListener("pointerup", onPointerUp);
    wrap.addEventListener("pointerleave", onLeave);
    wrap.addEventListener("pointercancel", onPointerUp);
    window.addEventListener("resize", resize);

    const spawnMs = 32;
    let lastSpawn = performance.now();

    const draw = (now: number) => {
      const elapsed = (now - t0) / 1000;

      // Progressive reveal: vault fills like Obsidian graph load
      if (!reduced && revealed < nodes.length && now - lastSpawn > spawnMs) {
        const n = nodes[revealed];
        n.born = 0.05;
        n.x = (Math.random() - 0.5) * 24;
        n.y = (Math.random() - 0.5) * 24;
        n.vx = (Math.random() - 0.5) * 6;
        n.vy = (Math.random() - 0.5) * 6;
        revealed++;
        lastSpawn = now;
        sim.alpha(Math.max(sim.alpha(), 0.4)).restart();
      }

      for (let i = 0; i < revealed; i++) {
        const n = nodes[i];
        if (n.born < 1) n.born = Math.min(1, n.born + 0.07);
      }

      // Never fully freeze — Obsidian’s graph keeps a quiet breath
      if (!reduced) {
        if (sim.alpha() < 0.028) {
          for (let k = 0; k < 5; k++) {
            const n = nodes[(Math.random() * revealed) | 0];
            n.vx = (n.vx ?? 0) + (Math.random() - 0.5) * 0.4;
            n.vy = (n.vy ?? 0) + (Math.random() - 0.5) * 0.4;
          }
          sim.alpha(0.055).restart();
        }
        sim.tick();
      }

      // Hover neighborhood
      const hoverSet = new Set<number>();
      if (mouse.hover >= 0) {
        hoverSet.add(mouse.hover);
        for (const l of links) {
          const s = typeof l.source === "object" ? l.source.id : (l.source as number);
          const t = typeof l.target === "object" ? l.target.id : (l.target as number);
          if (s === mouse.hover || t === mouse.hover) {
            hoverSet.add(s);
            hoverSet.add(t);
          }
        }
      }

      for (let i = 0; i < nodes.length; i++) {
        const target = hoverSet.has(i) ? 1 : 0;
        nodes[i].heat += (target - nodes[i].heat) * 0.2;
      }
      for (const l of links) {
        const s = typeof l.source === "object" ? l.source.id : (l.source as number);
        const t = typeof l.target === "object" ? l.target.id : (l.target as number);
        const visible = s < revealed && t < revealed;
        const hot =
          visible &&
          (hoverSet.size === 0 || (hoverSet.has(s) && hoverSet.has(t)));
        const target = !visible
          ? 0
          : hot
            ? hoverSet.size
              ? 1
              : 0.6
            : 0.07;
        l.active += (target - l.active) * 0.16;
      }

      ctx.clearRect(0, 0, w, h);

      const wash = ctx.createRadialGradient(cx + pan.x * 0.15, cy + pan.y * 0.15, 8, cx, cy, Math.max(w, h) * 0.42);
      wash.addColorStop(0, "rgba(232, 168, 56, 0.04)");
      wash.addColorStop(1, "rgba(5, 4, 8, 0)");
      ctx.fillStyle = wash;
      ctx.fillRect(0, 0, w, h);

      // Links
      ctx.lineCap = "round";
      for (const l of links) {
        const s = l.source as GNode;
        const t = l.target as GNode;
        if (s.id >= revealed || t.id >= revealed) continue;
        if (s.born < 0.25 || t.born < 0.25) continue;

        const sp = toScreen(s);
        const tp = toScreen(t);
        const a = Math.min(s.born, t.born) * l.active;
        if (a < 0.02) continue;

        const hot =
          mouse.hover >= 0 && hoverSet.has(s.id) && hoverSet.has(t.id);

        ctx.beginPath();
        ctx.moveTo(sp.x, sp.y);
        ctx.lineTo(tp.x, tp.y);
        ctx.strokeStyle = hot
          ? `rgba(242, 237, 228, ${0.62 * a})`
          : `rgba(170, 160, 140, ${0.28 * a})`;
        ctx.lineWidth = hot ? 1.3 : 0.95;
        ctx.stroke();
      }

      // Nodes
      for (let i = 0; i < revealed; i++) {
        const n = nodes[i];
        if (n.born <= 0) continue;
        const p = toScreen(n);
        const pulse = reduced
          ? 1
          : 0.93 + Math.sin(elapsed * 1.5 + n.id * 0.65) * 0.07;
        const r = n.r * n.born * pulse * (1 + n.heat * 0.4);

        if (n.heat > 0.15 || n.id === 0) {
          ctx.beginPath();
          ctx.arc(p.x, p.y, r * (n.id === 0 ? 3.4 : 2.6), 0, Math.PI * 2);
          ctx.fillStyle =
            n.id === 0
              ? `rgba(232, 168, 56, ${0.2 + n.heat * 0.1})`
              : `rgba(232, 168, 56, ${n.heat * 0.16})`;
          ctx.fill();
        }

        const dim =
          mouse.hover >= 0 && !hoverSet.has(n.id) ? 0.22 : 0.95 + n.heat * 0.05;
        ctx.beginPath();
        ctx.arc(p.x, p.y, r, 0, Math.PI * 2);
        ctx.globalAlpha = n.born * dim;
        ctx.fillStyle = n.color;
        ctx.fill();
        ctx.globalAlpha = 1;

        if (n.id === 0) {
          ctx.beginPath();
          ctx.arc(p.x, p.y, r + 3.5, 0, Math.PI * 2);
          ctx.strokeStyle = `rgba(232, 184, 106, ${0.5 * n.born})`;
          ctx.lineWidth = 1;
          ctx.stroke();
        }
      }

      raf = requestAnimationFrame(draw);
    };

    raf = requestAnimationFrame(draw);

    return () => {
      cancelAnimationFrame(raf);
      sim.stop();
      window.removeEventListener("resize", resize);
      wrap.removeEventListener("pointermove", onPointerMove);
      wrap.removeEventListener("pointerdown", onPointerDown);
      wrap.removeEventListener("pointerup", onPointerUp);
      wrap.removeEventListener("pointerleave", onLeave);
      wrap.removeEventListener("pointercancel", onPointerUp);
    };
  }, []);

  return (
    <div
      ref={wrapRef}
      className="absolute inset-0 cursor-grab active:cursor-grabbing"
      aria-hidden
    >
      <canvas ref={canvasRef} className="block h-full w-full" />
      <div className="vignette absolute inset-0" />
    </div>
  );
}
