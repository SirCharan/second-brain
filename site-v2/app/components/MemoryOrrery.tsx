"use client";

import { useEffect, useRef } from "react";

type Node = {
  x: number;
  y: number;
  r: number;
  phase: number;
  speed: number;
  orbit: number;
  cx: number;
  cy: number;
  label?: string;
  heat: number;
};

const LABELS = [
  "rate-limit.md",
  "auth-flow",
  "deploy notes",
  "why-we-chose-r2",
  "session/07-14",
  "mcp-quirks",
  "vault/index",
  "lesson: retries",
  "prd-v2",
  "clear-safe",
];

function prefersReducedMotion() {
  if (typeof window === "undefined") return true;
  return window.matchMedia("(prefers-reduced-motion: reduce)").matches;
}

/**
 * Signature visual: a living memory orrery.
 * Nodes orbit a warm core; filaments light under the cursor.
 * Canvas only — no fake macOS windows, no purple glow soup.
 */
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
    let raf = 0;
    let w = 0;
    let h = 0;
    let dpr = 1;
    let t0 = performance.now();
    let nodes: Node[] = [];
    const mouse = { x: 0.55, y: 0.42, tx: 0.55, ty: 0.42, active: false };

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
      seed();
    };

    const seed = () => {
      const count = Math.min(48, Math.max(28, Math.floor((w * h) / 28000)));
      const cx = w * 0.58;
      const cy = h * 0.46;
      nodes = Array.from({ length: count }, (_, i) => {
        const orbit = 40 + (i % 7) * 28 + Math.random() * 40;
        const phase = Math.random() * Math.PI * 2;
        return {
          x: cx + Math.cos(phase) * orbit,
          y: cy + Math.sin(phase) * orbit * 0.62,
          r: 1.4 + Math.random() * 2.2,
          phase,
          speed: 0.08 + Math.random() * 0.18,
          orbit,
          cx: cx + (Math.random() - 0.5) * w * 0.12,
          cy: cy + (Math.random() - 0.5) * h * 0.1,
          label: i < LABELS.length ? LABELS[i] : undefined,
          heat: 0,
        };
      });
    };

    const onMove = (e: PointerEvent) => {
      const rect = wrap.getBoundingClientRect();
      mouse.tx = (e.clientX - rect.left) / rect.width;
      mouse.ty = (e.clientY - rect.top) / rect.height;
      mouse.active = true;
    };
    const onLeave = () => {
      mouse.active = false;
    };

    wrap.addEventListener("pointermove", onMove);
    wrap.addEventListener("pointerleave", onLeave);
    window.addEventListener("resize", resize);
    resize();

    const draw = (now: number) => {
      const elapsed = (now - t0) / 1000;
      mouse.x += (mouse.tx - mouse.x) * 0.06;
      mouse.y += (mouse.ty - mouse.y) * 0.06;

      ctx.clearRect(0, 0, w, h);

      // Deep field — cool vignette wash, not a grid
      const field = ctx.createRadialGradient(
        w * 0.58,
        h * 0.46,
        20,
        w * 0.55,
        h * 0.5,
        Math.max(w, h) * 0.7,
      );
      field.addColorStop(0, "rgba(212, 160, 84, 0.07)");
      field.addColorStop(0.35, "rgba(107, 143, 163, 0.04)");
      field.addColorStop(1, "rgba(5, 4, 8, 0)");
      ctx.fillStyle = field;
      ctx.fillRect(0, 0, w, h);

      const coreX = w * 0.58 + (mouse.x - 0.5) * 18;
      const coreY = h * 0.46 + (mouse.y - 0.5) * 12;
      const mx = mouse.x * w;
      const my = mouse.y * h;

      // Update positions
      for (const n of nodes) {
        const ang = n.phase + (reduced ? 0 : elapsed * n.speed * 0.35);
        const ox = Math.cos(ang) * n.orbit;
        const oy = Math.sin(ang) * n.orbit * 0.58;
        n.x = n.cx + ox + (mouse.x - 0.5) * 24 * (n.orbit / 200);
        n.y = n.cy + oy + (mouse.y - 0.5) * 16 * (n.orbit / 200);

        const dx = n.x - mx;
        const dy = n.y - my;
        const dist = Math.hypot(dx, dy);
        const target = mouse.active && dist < 140 ? 1 - dist / 140 : 0;
        n.heat += (target - n.heat) * 0.12;
      }

      // Filaments between nearby nodes
      ctx.lineWidth = 1;
      for (let i = 0; i < nodes.length; i++) {
        for (let j = i + 1; j < nodes.length; j++) {
          const a = nodes[i];
          const b = nodes[j];
          const d = Math.hypot(a.x - b.x, a.y - b.y);
          if (d > 110) continue;
          const heat = Math.max(a.heat, b.heat);
          const base = 0.04 + (1 - d / 110) * 0.08;
          const alpha = base + heat * 0.35;
          ctx.beginPath();
          ctx.moveTo(a.x, a.y);
          ctx.lineTo(b.x, b.y);
          ctx.strokeStyle =
            heat > 0.15
              ? `rgba(232, 184, 106, ${alpha})`
              : `rgba(107, 143, 163, ${alpha * 0.85})`;
          ctx.stroke();
        }
      }

      // Core — the vault
      const coreGlow = ctx.createRadialGradient(coreX, coreY, 0, coreX, coreY, 90);
      coreGlow.addColorStop(0, "rgba(232, 184, 106, 0.28)");
      coreGlow.addColorStop(0.4, "rgba(212, 160, 84, 0.08)");
      coreGlow.addColorStop(1, "rgba(212, 160, 84, 0)");
      ctx.fillStyle = coreGlow;
      ctx.beginPath();
      ctx.arc(coreX, coreY, 90, 0, Math.PI * 2);
      ctx.fill();

      ctx.beginPath();
      ctx.arc(coreX, coreY, 5.5, 0, Math.PI * 2);
      ctx.fillStyle = "#e8b86a";
      ctx.fill();
      ctx.beginPath();
      ctx.arc(coreX, coreY, 12, 0, Math.PI * 2);
      ctx.strokeStyle = "rgba(232, 184, 106, 0.45)";
      ctx.lineWidth = 1;
      ctx.stroke();

      // Orbit rings (thin, incomplete arcs — not dashed orbit cliche spam)
      ctx.save();
      ctx.translate(coreX, coreY);
      ctx.scale(1, 0.58);
      for (const rad of [70, 130, 190]) {
        ctx.beginPath();
        ctx.arc(0, 0, rad, 0.2, Math.PI * 1.6);
        ctx.strokeStyle = "rgba(107, 143, 163, 0.08)";
        ctx.lineWidth = 1;
        ctx.stroke();
      }
      ctx.restore();

      // Nodes
      for (const n of nodes) {
        const pulse = reduced
          ? 0
          : Math.sin(elapsed * 2 + n.phase) * 0.15 + 0.85;
        const r = n.r * (1 + n.heat * 0.8) * pulse;

        if (n.heat > 0.2) {
          ctx.beginPath();
          ctx.arc(n.x, n.y, r * 4, 0, Math.PI * 2);
          ctx.fillStyle = `rgba(212, 160, 84, ${n.heat * 0.12})`;
          ctx.fill();
        }

        ctx.beginPath();
        ctx.arc(n.x, n.y, r, 0, Math.PI * 2);
        ctx.fillStyle =
          n.heat > 0.3
            ? `rgba(242, 237, 228, ${0.75 + n.heat * 0.25})`
            : `rgba(163, 158, 150, ${0.35 + n.heat * 0.4})`;
        ctx.fill();

        if (n.label && n.heat > 0.45) {
          ctx.font = "500 11px var(--font-mono), ui-monospace, monospace";
          ctx.fillStyle = `rgba(242, 237, 228, ${n.heat * 0.9})`;
          ctx.fillText(n.label, n.x + 8, n.y - 6);
        }
      }

      // Cursor tether to core when active
      if (mouse.active) {
        ctx.beginPath();
        ctx.moveTo(coreX, coreY);
        ctx.lineTo(mx, my);
        ctx.strokeStyle = "rgba(212, 160, 84, 0.12)";
        ctx.lineWidth = 1;
        ctx.stroke();
      }

      raf = requestAnimationFrame(draw);
    };

    raf = requestAnimationFrame(draw);

    return () => {
      cancelAnimationFrame(raf);
      window.removeEventListener("resize", resize);
      wrap.removeEventListener("pointermove", onMove);
      wrap.removeEventListener("pointerleave", onLeave);
    };
  }, []);

  return (
    <div ref={wrapRef} className="absolute inset-0" aria-hidden>
      <canvas ref={canvasRef} className="block h-full w-full" />
      <div className="vignette absolute inset-0" />
    </div>
  );
}
