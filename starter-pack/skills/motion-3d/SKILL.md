---
name: motion-3d
description: "Cross-cutting animation & 3D layer for web UI — decides WHICH animation tech to reach for once design-router has picked the primary design skill. NOT a primary/router itself. Load alongside design-router + layout-interaction-design for any UI with motion, transitions, scroll effects, gestures, 3D, or micro-interactions. The rule: default React UI animation → Motion (framer-motion/`motion`); scroll-driven/pinned/timeline/SVG-morph → GSAP; cheap list/reorder polish → auto-animate; designer-authored → Lottie; 3D/WebGL → React Three Fiber but OPT-IN ONLY (never default — prefer SVG/CSS/Lottie first). Always honor prefers-reduced-motion. Trigger on: animation, animate, motion, framer motion, transition, scroll animation, parallax, gsap, scrolltrigger, timeline, 3d, three.js, react three fiber, r3f, webgl, lottie, micro-interaction, microanimation, hover/press effect, entrance animation, page transition, stagger, gesture, spring."
---

# motion-3d — pick the right animation/3D tech

Cross-cutting layer. **Routing is unchanged** — `design-router` still decides the primary skill (a fixed brand system → that brand's own tokens; else `ui-ux-pro-max`). This skill sits ON TOP and answers a narrower question: *given I need motion or 3D, which tool?* Load `layout-interaction-design` alongside for the behavioral mechanics.

> **Precedence over `ui-ux-pro-max`:** the pro-max engine's `--motion` dial emits a GSAP snippet. **motion-3d owns the animation-tech choice — it overrides that.** Run pro-max with `--motion low` (or ignore its GSAP snippet) and let this table decide: Motion is the baseline; treat any pro-max GSAP suggestion as *scroll-only*, not the default.

## Decision table

| Need | Reach for | Notes |
|---|---|---|
| **Default React UI animation** — entrances, layout/FLIP, gestures, `whileInView`, `AnimatePresence` | **Motion** (`motion/react`, formerly framer-motion) | The default. Declarative, SSR-friendly, tree-shakes. `framer-motion` v12 = the same package (legacy alias). |
| **Scroll-driven / pinned / complex timelines / SVG morph / text split** | **GSAP** + `useGSAP()` | Reach for it when Motion's scroll gets awkward. ScrollTrigger, SplitText, Flip, MorphSVG — **all free since v3.13 (2025)**, no license key. `useGSAP()` = SSR-safe auto-cleanup; the component needs `'use client'`. |
| **Cheap list/reorder/expand polish** | **auto-animate** (`@formkit/auto-animate`) | One ref on the parent, 2.3 KB. Great when Motion is overkill. |
| **Designer-authored motion** (After Effects exports) | **Lottie** (`lottie-react`) | Load client-side; guard SSR. `lottie-react` = plain `.json`, easiest SSR; `@lottiefiles/dotlottie-react` = WASM/.lottie, smaller files but more SSR-sensitive. |
| **Tailwind utility keyframes** | `tw-animate-css` (Tailwind **v4**) or `tailwindcss-animate` (v3) | Match the project's Tailwind major — the v4 package will not work on a v3 project. |
| **3D / WebGL** | **React Three Fiber + drei** — **OPT-IN ONLY** | ⚠️ Never the default. Heavy bundle + perf cost. Prefer SVG / CSS / Lottie first. Only add when a project explicitly wants real 3D. A polished personal site is usually better served by SVG effects than by R3F. |

## Always
- Respect **`prefers-reduced-motion`** — gate or reduce every non-essential animation.
- Animate `transform`/`opacity` only (never width/height/top/left). Durations 150–300ms for micro, ≤400ms for transitions; ease-out enter, ease-in exit.
- One or two animated elements per view — motion should convey meaning, not decorate.

## Installed Claude skills backing this (namespaced plugins)
- `ui-ux-pro-max` — its `--motion` dial also emits GSAP; motion-3d has precedence (see note above), so this is a *source of ideas*, not the tech decider.
- `gsap-skills:*` — official GreenSock (useGSAP cleanup, ScrollTrigger, timelines). Marketplace `greensock/gsap-skills`.
- `claude-design-skillstack:motion-framer` — Motion / framer-motion.
- `claude-design-skillstack:animation-components` — Lottie, Magic UI, AOS, Anime.js, React Spring, micro-interactions.
- `claude-design-skillstack:react-three-fiber` — R3F/drei/postprocessing (for the opt-in 3D projects).
- Marketplace `freshtechbro/claudedesignskills` (id `claude-design-skillstack`) also has `threejs-webgl`, `gsap-scrolltrigger`, `lottie-animations`, `spline-interactive`, `locomotive-scroll` if a project needs them.

## npm install recipes (per project, on demand)
```bash
npm i motion                      # React UI animation (import from motion/react)
npm i gsap @gsap/react            # scroll/timeline; GSAP v3.13+, all plugins free
npm i lottie-react                # or @lottiefiles/dotlottie-react
npm i @formkit/auto-animate       # micro list/reorder polish
# 3D (opt-in only): npm i three @react-three/fiber@9 @react-three/drei @react-three/postprocessing
```

## Reference repos
`motiondivision/motion` (CLAUDE.md + 300+ examples) · `pmndrs/react-three-fiber` (docs.pmnd.rs) · `gsimone/awesome-react-three-fiber` · `zhengdechang/awesome-gsap` (no license — don't lift wholesale).

Related: `design-router` · `ui-ux-pro-max` · `layout-interaction-design`.
