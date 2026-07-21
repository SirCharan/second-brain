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

/**
 * Hybrid graph for the final landing:
 * - Physics + hover + drag + pan + ⌘/ctrl-zoom from /live
 * - Soft progressive birth + quiet breath from cinema (second-brain-cinema)
 */

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
  { key: "coral", palette: ["#e2532f", "#e0603a", "#d9542c", "#e86a42"], cx: 0.64, cy: 0.62 },
  { key: "tan", palette: ["#c9a35f", "#b8935a", "#caa869", "#bd9a54"], cx: 0.48, cy: 0.52 },
  { key: "yellow", palette: ["#e8c94a", "#ecd24f", "#f0d84a", "#e3c24d"], cx: 0.3, cy: 0.46 },
  { key: "brown", palette: ["#8a6f4a", "#9c7d50", "#7d6543"], cx: 0.44, cy: 0.64 },
  { key: "fan", palette: ["#c9a35f", "#caa869", "#d8b878"], cx: 0.72, cy: 0.3 },
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
    [0.12, 0.12],
    [0.9, 0.42],
    [0.06, 0.7],
    [0.5, 0.08],
    [0.94, 0.72],
    [0.16, 0.9],
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

  for (let i = 0; i < hubIds.length; i++) addLink(hubIds[i], hubIds[(i + 1) % hubIds.length]);
  addLink(hubIds[1], fanHub.id);
  for (let i = 0; i < 22; i++) {
    const a = (rnd() * nodes.length) | 0;
    const b = (rnd() * nodes.length) | 0;
    if (nodes[a].comm !== nodes[b].comm && nodes[a].comm !== 5 && nodes[b].comm !== 5)
      addLink(a, b);
  }

  for (const n of nodes) n.r = 2.3 + Math.min(n.deg, 40) * 0.32;
  return { nodes, links };
}

const nid = (x: GNode | number) => (typeof x === "object" ? x.id : x);

/** Default: punchy wire-up. cinematic=true: launch-reel drama (faster cascade, hotter pulses). */
const TIMING = {
  default: { GROW_MS: 720, REVEAL_MS: 48, REVEAL_BATCH: 4, SEED_FRAC: 0.05, pulseEvery: 28, maxPulses: 9 },
  cinematic: { GROW_MS: 520, REVEAL_MS: 32, REVEAL_BATCH: 7, SEED_FRAC: 0.02, pulseEvery: 14, maxPulses: 16 },
} as const;

export default function GraphField({
  mode = "interactive",
  cinematic = false,
  className = "",
}: {
  mode?: Mode;
  /** Launch-video mode: denser cascade, hotter pulses, stronger birth kicks. */
  cinematic?: boolean;
  className?: string;
}) {
  const canvasRef = useRef<HTMLCanvasElement>(null);

  useEffect(() => {
    const canvas = canvasRef.current!;
    if (!canvas) return;
    const parent = canvas.parentElement!;
    const ctx = canvas.getContext("2d")!;
    const reduced = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
    const T = cinematic ? TIMING.cinematic : TIMING.default;
    const { GROW_MS, REVEAL_MS, REVEAL_BATCH, SEED_FRAC } = T;

    let w = parent.clientWidth;
    let h = parent.clientHeight;
    const scale = w < 700 ? 0.42 : w < 1100 ? 0.72 : 1;
    const { nodes, links } = buildGraph(cinematic ? 17 : 11, scale);
    const rnd = mulberry32(cinematic ? 41 : 23);

    const incident = new Map<number, number[]>();
    for (const l of links) {
      const a = l.source as number;
      const b = l.target as number;
      (incident.get(a) ?? incident.set(a, []).get(a)!).push(b);
      (incident.get(b) ?? incident.set(b, []).get(b)!).push(a);
    }

    const active: GNode[] = [];
    const activeLinks: GLink[] = [];
    const shown = new Uint8Array(nodes.length);
    let cursor = 0;

    const linkForce = forceLink<GNode, GLink>(activeLinks)
      .id((d) => d.id)
      .distance((l) => ((l.source as GNode).comm === 4 ? 32 : 26))
      .strength(0.1);

    const charge = cinematic
      ? scale < 0.6
        ? -28
        : -42
      : scale < 0.6
        ? -18
        : -26;
    const sim: Simulation<GNode, undefined> = forceSimulation(active)
      .force("charge", forceManyBody().strength(charge).theta(0.9))
      .force("link", linkForce)
      .force(
        "x",
        forceX<GNode>((d) => d.cx * w).strength((d) => d.cs * (cinematic ? 0.7 : 0.85)),
      )
      .force(
        "y",
        forceY<GNode>((d) => d.cy * h).strength((d) => d.cs * (cinematic ? 0.7 : 0.85)),
      )
      .force("collide", forceCollide<GNode>().radius((d) => d.r + (cinematic ? 2.2 : 1.8)))
      .alpha(cinematic ? 1 : 0.82)
      .alphaDecay(cinematic ? 0.012 : 0.016)
      .velocityDecay(cinematic ? 0.38 : 0.46);
    sim.stop();

    function reveal(count: number, now: number) {
      const kick = cinematic ? 3.8 : 1.6;
      const scatter = cinematic ? 22 : 14;
      for (let c = 0; c < count && cursor < nodes.length; c++) {
        const n = nodes[cursor++];
        let placed = false;
        const inc = incident.get(n.id);
        if (inc) {
          for (const o of inc) {
            if (shown[o]) {
              // birth near a neighbour — spring out so links read as growth
              n.x = (nodes[o].x ?? n.cx * w) + (rnd() - 0.5) * scatter;
              n.y = (nodes[o].y ?? n.cy * h) + (rnd() - 0.5) * scatter;
              n.vx = (rnd() - 0.5) * kick;
              n.vy = (rnd() - 0.5) * kick;
              placed = true;
              break;
            }
          }
        }
        if (!placed) {
          n.x = n.cx * w + (rnd() - 0.5) * w * (cinematic ? 0.12 : 0.08);
          n.y = n.cy * h + (rnd() - 0.5) * h * (cinematic ? 0.12 : 0.08);
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
      sim.alpha(Math.max(sim.alpha(), cinematic ? 0.55 : 0.32)).restart();
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
    const ro = new ResizeObserver(() => {
      resize();
      if (reduced) draw(performance.now());
    });
    ro.observe(parent);

    let k = 1,
      tx = 0,
      ty = 0;
    let mx = w / 2,
      my = h / 2;
    let hover = -1;
    let dragging: GNode | null = null;
    let panning = false;
    let panLast = { x: 0, y: 0 };
    const neighbors = new Set<number>();

    const toGraph = (cx: number, cy: number) => ({
      x: (cx - tx) / k,
      y: (cy - ty) / k,
    });
    function nodeAt(gx: number, gy: number) {
      for (let i = active.length - 1; i >= 0; i--) {
        const n = active[i];
        const dx = (n.x ?? 0) - gx;
        const dy = (n.y ?? 0) - gy;
        const rr = n.r + 14 / k;
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
        sim.alphaTarget(0.12).restart();
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
      canvas.style.cursor = n ? "pointer" : "grab";
    };
    const onDown = (e: PointerEvent) => {
      if (mode !== "interactive") return;
      // don't steal when target is outside canvas (copy layer handles itself)
      const p = local(e);
      const g = toGraph(p.x, p.y);
      const n = nodeAt(g.x, g.y);
      if (n) {
        dragging = n;
        n.fx = g.x;
        n.fy = g.y;
        canvas.style.cursor = "grabbing";
        sim.alphaTarget(0.16).restart();
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
        sim.alphaTarget(0.004);
      }
      panning = false;
      if (mode === "interactive") canvas.style.cursor = "grab";
    };
    const onWheel = (e: WheelEvent) => {
      if (mode !== "interactive") return;
      // never hijack page scroll — zoom only with ⌘/ctrl (or trackpad pinch)
      if (!e.ctrlKey && !e.metaKey) return;
      e.preventDefault();
      const rect = canvas.getBoundingClientRect();
      const px = e.clientX - rect.left;
      const py = e.clientY - rect.top;
      // softer zoom curve
      const factor = Math.exp(-e.deltaY * 0.0011);
      const nk = Math.max(0.4, Math.min(3.2, k * factor));
      tx = px - ((px - tx) * nk) / k;
      ty = py - ((py - ty) * nk) / k;
      k = nk;
    };

    if (mode === "interactive") {
      canvas.addEventListener("pointermove", onMove);
      canvas.addEventListener("pointerdown", onDown);
      window.addEventListener("pointerup", onUp);
      canvas.addEventListener("wheel", onWheel, { passive: false });
      canvas.style.cursor = "grab";
    } else {
      parent.addEventListener("pointermove", onMove);
    }

    const pulses: Pulse[] = [];
    let pulseClock = 0;
    function spawnPulse() {
      if (pulses.length > T.maxPulses || activeLinks.length === 0) return;
      const n = cinematic ? 2 : 1;
      for (let i = 0; i < n; i++) {
        pulses.push({
          link: (Math.random() * activeLinks.length) | 0,
          t: 0,
          speed: (cinematic ? 0.008 : 0.004) + Math.random() * 0.008,
        });
      }
    }

    const growOf = (n: GNode, now: number) => {
      if (reduced || n.born == null) return 1;
      const g = Math.min(1, (now - n.born) / GROW_MS);
      // ease-out cubic + slight overshoot for cinematic pop
      if (cinematic) {
        const t = 1 - Math.pow(1 - g, 3);
        return Math.min(1.12, t * 1.08);
      }
      return 1 - Math.pow(1 - g, 3);
    };

    // slow dramatic zoom-out while vault fills (cinematic only)
    let camK = cinematic ? 1.35 : 1;
    let camTx = cinematic ? -w * 0.06 : 0;
    let camTy = cinematic ? -h * 0.04 : 0;
    const t0 = performance.now();

    function draw(now: number) {
      ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
      ctx.clearRect(0, 0, w, h);

      const useK = mode === "interactive" ? k * camK : camK;
      const useTx = mode === "interactive" ? tx + camTx : camTx;
      const useTy = mode === "interactive" ? ty + camTy : camTy;

      if (mode === "ambient" && !cinematic) {
        ctx.translate((mx - w / 2) * 0.008, (my - h / 2) * 0.008);
      } else {
        ctx.translate(useTx, useTy);
        ctx.scale(useK, useK);
      }
      const sw = mode === "interactive" || cinematic ? useK : 1;

      for (const l of activeLinks) {
        const s = l.source as GNode;
        const t = l.target as GNode;
        const g = Math.min(growOf(s, now), growOf(t, now));
        if (g <= 0.02) continue;
        const lit = hover >= 0 && (s.id === hover || t.id === hover);
        const baseA = cinematic ? 0.16 : 0.11;
        ctx.strokeStyle = lit
          ? `rgba(230,165,75,${(cinematic ? 0.65 : 0.42) * Math.min(1, g)})`
          : hover >= 0
            ? `rgba(243,238,229,${0.035 * Math.min(1, g)})`
            : `rgba(243,238,229,${baseA * Math.min(1, g)})`;
        ctx.lineWidth = (lit ? 1.25 : cinematic ? 0.7 : 0.55) / sw;
        ctx.lineCap = "round";
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
        const pr = (cinematic ? 2.4 : 1.6) / sw;
        ctx.beginPath();
        ctx.arc(x, y, pr, 0, Math.PI * 2);
        ctx.fillStyle = "rgba(230,165,75,0.9)";
        ctx.shadowColor = "rgba(230,165,75,0.75)";
        ctx.shadowBlur = cinematic ? 10 : 4;
        ctx.fill();
        ctx.shadowBlur = 0;
      }

      for (const n of active) {
        const g = growOf(n, now);
        const dim = hover >= 0 && n.id !== hover && !neighbors.has(n.id);
        const alpha = (dim ? 0.16 : 1) * Math.min(1, g);
        ctx.globalAlpha = alpha;
        const rr = n.r * (0.3 + 0.7 * Math.min(1, g));
        // birth halo
        if (cinematic && g < 1.05 && g > 0.05) {
          ctx.beginPath();
          ctx.arc(n.x!, n.y!, rr * 2.2, 0, Math.PI * 2);
          ctx.fillStyle = `rgba(230,165,75,${0.12 * (1 - Math.min(1, g))})`;
          ctx.fill();
        }
        ctx.beginPath();
        ctx.arc(n.x!, n.y!, rr, 0, Math.PI * 2);
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
        // staged cascade: slow start, then flood, then settle
        let batch: number = REVEAL_BATCH;
        let interval: number = REVEAL_MS;
        if (cinematic) {
          const p = cursor / Math.max(1, nodes.length);
          if (p < 0.15) {
            batch = 3;
            interval = 55;
          } else if (p < 0.7) {
            batch = 9;
            interval = 22;
          } else {
            batch = 4;
            interval = 40;
          }
          // slow pull-back so the full vault enters frame
          const age = Math.min(1, (now - t0) / 9000);
          camK = 1.35 - age * 0.38;
          camTx = -w * 0.06 * (1 - age * 0.5);
          camTy = -h * 0.04 * (1 - age * 0.5);
        }
        if (cursor < nodes.length && now - lastReveal > interval) {
          reveal(batch, now);
          lastReveal = now;
        }
        // alive breath after settle
        if (cursor >= nodes.length && sim.alpha() < 0.028 && !dragging) {
          const nJ = cinematic ? 8 : 3;
          for (let i = 0; i < nJ; i++) {
            const n = active[(Math.random() * active.length) | 0];
            if (!n || n.fx != null) continue;
            n.vx = (n.vx ?? 0) + (Math.random() - 0.5) * (cinematic ? 0.55 : 0.22);
            n.vy = (n.vy ?? 0) + (Math.random() - 0.5) * (cinematic ? 0.55 : 0.22);
          }
          sim.alpha(cinematic ? 0.07 : 0.04).restart();
        }
        pulseClock++;
        if (pulseClock % T.pulseEvery === 0) spawnPulse();
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
      sim.stop();
      draw(0);
    } else {
      // tiny seed, then cascade
      const seed = Math.max(cinematic ? 3 : 6, Math.floor(nodes.length * SEED_FRAC));
      const t = performance.now();
      reveal(seed, t - GROW_MS);
      for (let i = 0; i < (cinematic ? 20 : 40); i++) sim.tick();
      lastReveal = t;
      raf = requestAnimationFrame(frame);
    }

    const onVis = () => {
      if (document.hidden) {
        running = false;
        cancelAnimationFrame(raf);
        sim.stop();
      } else if (!reduced) {
        running = true;
        sim.alphaTarget(0.004).restart();
        raf = requestAnimationFrame(frame);
      }
    };
    document.addEventListener("visibilitychange", onVis);
    const io = new IntersectionObserver(
      ([e]) => {
        if (reduced) return;
        if (e.isIntersecting && !running) {
          running = true;
          sim.alphaTarget(0.004).restart();
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
  }, [mode, cinematic]);

  return (
    <canvas
      ref={canvasRef}
      aria-hidden="true"
      className={className}
      style={{
        pointerEvents: mode === "interactive" ? "auto" : "none",
        touchAction: mode === "interactive" ? "pan-y" : undefined,
      }}
    />
  );
}
