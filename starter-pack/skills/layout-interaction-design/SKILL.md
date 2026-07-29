---
name: layout-interaction-design
description: >
  The BEHAVIORAL layer companion to `design-system` — how a UI is spaced, where actions go, how users
  move through it, and how it responds. Load alongside `design-system` for any non-trivial interactive or
  multi-screen build (Next.js + Tailwind v4 + shadcn/ui on Vercel). Covers: spacing & layout mechanics
  (8pt grid, padding vs margin vs gap, Every-Layout primitives, measure), button & action hierarchy +
  placement/ordering (with the cross-platform disagreement flagged), navigation & routing (top-nav vs
  sidebar vs tabs vs breadcrumbs, multi-step flows, Next.js App Router: Link/prefetch, layouts,
  loading.tsx, parallel & intercepting modal routes, active-link, View Transitions), and interaction
  states + UX heuristics (feedback latency, skeletons vs spinners, validation/error/empty states, focus
  management, Fitts/Hick/Doherty, Nielsen's 10). Trigger on: "where do I put", "button placement",
  "padding/margin/spacing/gap", "navigation", "sidebar vs tabs", "page transition", "multi-step form /
  wizard", "modal route", "loading/empty/error state", "user flow", "how should this behave".
---

# Layout & Interaction Design

The "how it behaves & connects" half of the design family (`design-system` owns "how it looks"). Rules
first, then the Next.js/shadcn implementation. ✅ = from a primary source (cited) · ◐ = well-sourced
judgment. Note: the deep-research verify pass was rate-limited, so claims rest on **primary sources +
corroboration**, not a formal vote — treat ◐ as strong defaults.

---

## 1. Spacing & layout mechanics

**8pt grid** ✅ — size and space everything in multiples of 8 (4 allowed for tight icon/text gaps). Maps to
Tailwind's default scale (`1`=4px, `2`=8px, `4`=16px, `6`=24px, `8`=32px…). One scale, used everywhere.

**The load-bearing rule — "internal ≤ external"** ✅ (Cieden): the space *inside/around* a grouped element
must be **≤** the space *separating* it from other groups. Proximity = grouping; if padding inside a card
≥ the gap between cards, the grouping reads wrong. Concretely: card padding 16–24px → gap between cards
24–32px → section gap 48–64px. Tighten *within*, loosen *between*.

**padding vs margin vs gap** ✅◐ — decision rule:
- **`gap`** = rhythm between siblings in a flex/grid. **Default choice.** No collapsing, no leftover edge
  margin, survives wrapping (margins don't). `flex flex-col gap-4`, `grid gap-6`.
- **`padding`** = breathing room *inside* a container (card, button, section). Always padding for inner space.
- **`margin`** = sparingly, for outer separation a parent can't own (e.g. one-off `mt` on a heading).
  Prefer a `gap` on the parent over per-child margins. Avoid margin for list/stack rhythm.

**Layout primitives** ✅ (Every Layout) — compose pages from a few reusable primitives instead of bespoke
flex per screen. Paste-ready Tailwind:
- **Stack** (vertical rhythm): `<div className="flex flex-col gap-4">`
- **Cluster** (wrapping row, e.g. tags/toolbar): `<div className="flex flex-wrap items-center gap-2">`
- **Sidebar** (sidebar + fluid main, wraps when narrow): `<div className="flex flex-wrap gap-6">` + main `flex-1 basis-[60%]`
- **Center** (constrained reading column): `<div className="mx-auto w-full max-w-prose px-4">`
- **Grid** (responsive auto-fit cards): `<div className="grid gap-6 [grid-template-columns:repeat(auto-fit,minmax(16rem,1fr))]">`
- **Switcher** (N-up that drops to stacked under a threshold): auto-fit grid as above with a min width.

**Measure / content width** ✅ — body text `max-w-prose` (~65ch); app content `max-w-7xl` (1280px) typical;
full-bleed only for dashboards/hero. Never let prose run the full viewport.

**Responsive composition** ✅ — viewport breakpoints for *page* layout (`md: lg:`), Tailwind v4 **container
queries** (`@container` + `@md:`) for *components* that live in variable-width slots (a card in a sidebar
vs a wide grid). Primitives above already wrap without breakpoints — prefer them.

---

## 2. Buttons & action hierarchy

**One primary action per view** ✅ (GOV.UK) — exactly one filled/default button; everything else is
secondary/tertiary. More than one primary dilutes both.

**Hierarchy** ✅ — three+ tiers: **primary** (filled accent, the main CTA) → **secondary** (outline/tonal) →
**tertiary** (ghost/link) → **destructive** (a distinct *warning* style, not just red text). shadcn maps
these to `variant="default" | "secondary" | "outline" | "ghost" | "destructive"`.

**Placement & ordering — ⚠️ platforms disagree (flag, don't assume):** ✅
- **Apple HIG:** primary/affirmative button **far right**, Cancel to its immediate left.
- **Windows / older Android:** affirmative (OK) on the **left**.
- **GOV.UK:** one primary button **left-aligned** to the form edge; no separate Cancel — destructive is a
  warning button or a confirmation page.
- **NN/g's overriding rule:** follow the convention of *your users' dominant platform* and stay consistent;
  a standard order beats a marginally-optimal novel one.
- **House default (pick one & be consistent):** **dialogs/modals → primary RIGHT, Cancel left** (web/Mac
  norm; matches shadcn AlertDialog). **Forms/pages → primary LEFT** at the start of the action row
  (GOV.UK; it's where the eye lands after the last field).

**Form actions get missed in top bars** ✅ (UX Movement) — users finish a form at the *bottom*, so a submit
button in a top action bar is overlooked. Put the primary submit at the **bottom of the form**, left or
left-of-row; on long/mobile forms add a **sticky bottom action bar**.

**Sticky bars** ✅ (Smashing) — sticky nav/action bars hold **≤5 items**; overflow → menu. Hide-on-scroll-down
/ show-on-scroll-up headers should slide in fast (~150–300ms).

**Sizing & hit area** ✅ — min target **44×44px** (touch) / 24px (WCAG floor). Comfortable padding ratio
≈ vertical:horizontal of `1 : 2–2.5` (e.g. `px-4 py-2`, `px-6 py-3` for large). Don't make buttons full-bleed
unless mobile-primary.

**Icon-only buttons** ✅ — always an `aria-label` (and ideally a tooltip). Never ship an icon button a screen
reader announces as "button".

**Destructive actions** ✅ (Adam Silver) — don't *hide* the trigger; gate it behind a **confirmation step**
(AlertDialog or a confirm page) with the destructive verb on the confirm button ("Delete 3 signals").

---

## 3. Navigation & routing

**Pick the nav pattern by IA shape** ◐:
- **Top nav** — ≤~7 flat destinations; marketing & simple apps.
- **Sidebar** — many destinations / app with persistent context (dashboards, docs). Collapsible; group by section.
- **Tabs** — switching *views of the same object* (not navigating away). Keep ≤~5; don't use tabs as primary site nav.
- **Breadcrumbs** — deep hierarchies (≥3 levels) to show location + enable up-navigation. Secondary, not the only nav.

**Multi-step flows / wizards** ◐ — show progress (step N of M), allow back without data loss, validate per
step (§4), one primary action per step ("Continue"), persist state to URL/query so refresh and back work.

**Back & deep-linking** ✅ — every meaningful state should be a URL (filters, tabs, open modal) so back,
refresh, and share work. Don't trap state in component memory.

### Next.js App Router specifics ✅ (nextjs.org)
- **`<Link>` prefetch:** auto-prefetches routes entering the viewport (and on hover), **production only**;
  a plain `<a>` does not. Static routes prefetch fully; dynamic routes prefetch only to the nearest
  **`loading.tsx`** boundary. `prefetch={false}` to opt out; `prefetch={null}`-on-hover to limit to intent.
- **Nested `layout.tsx`** — shared chrome (sidebar/nav) that **persists without unmounting** across
  navigation. Put a dashboard sidebar in `app/(dashboard)/layout.tsx` (route group) so it stays mounted.
- **`loading.tsx`** — drop one in a route folder → Next wraps the page in `<Suspense>`, giving instant
  navigation + a streamed skeleton. Recommended for any dynamic/slow route.
- **Route groups** `(group)` — organize/segment layouts without affecting the URL.
- **Active link** — `const p = usePathname()`; mark active with **prefix match**
  `p === href || p.startsWith(href + '/')`, **special-casing `'/'`** to exact (else it matches everything).
- **Modal routes (deep-linkable)** — **intercepting** `(.)`/`(..)` routes + **parallel** `@slot` routes:
  a `@modal` slot with `default.tsx` returning `null`, an intercepting `(.)photo/[id]` rendering in a
  Modal over the current page on *soft* navigation; a **hard** load/refresh/share hits the real full page.
  Matchers: `(.)` same level, `(..)` one up, `(..)(..)` two up, `(...)` from app root.
- **Page transitions** — **View Transitions API** (Baseline Oct 2025) for route/shared-element morphs;
  gate with `prefers-reduced-motion`; graceful fallback on old browsers.

---

## 4. Interaction states & UX heuristics

**State set per interactive element** ✅ (NN/g) — design **all 7**: default, hover, focus(-visible),
active/pressed, disabled, **loading**, selected. Missing states (esp. focus + loading) is the #1 "templated"
tell. shadcn ships most; verify focus-visible + a loading variant.

**Feedback latency** ✅◐ — Doherty Threshold: respond in **≤400ms** to keep flow. Rules of thumb (Nielsen):
**<0.1s** = feels instant (no indicator) · **<1s** = keep attention, a subtle spinner ok · **>1s** show a
determinate indicator · **>10s** show progress + allow other work. Prefer **optimistic UI** (update
immediately, reconcile on response) for high-confidence mutations.

**Skeletons vs spinners** ✅ (NN/g) — **skeletons** for full-page/section loads roughly **>500ms and <10s**
that have a known layout (they imply structure + progress); **omit for <1s** loads (the flash annoys); a
**determinate progress bar** for **>10s**. Spinners for small inline/indeterminate waits only.

**Feedback channels** ✅◐ — **inline, next to the field/control** for validation and contextual results
(not a top banner); **toast** for transient async confirmations ("Saved") — auto-dismiss ~4–6s, never for
errors that need action; **inline error region** (`role="alert"`) for form/submit errors; **empty states**
are instructional — say what's missing + the next action, never a blank panel.

**Forms** ✅◐ — validate **on blur / per field**, not only on submit; specific in-context messages ("Leverage
must be 1–200×"); show the error at the field with `aria-invalid` + `aria-describedby`; don't disable the
submit button silently (explain what's required); allow paste/autofill (WCAG 2.2).

**Accessible focus on navigation** ✅ — on client-side route change, move focus to the new page's `<h1>`/main
(or an `aria-live` route announcer) so keyboard/SR users aren't stranded; keep a visible `:focus-visible`
ring (see `design-system` §5). Don't trap focus except inside modals (where you *must* trap + restore).

**UX laws to apply** ◐ —
- **Fitts's Law:** make frequent/important targets bigger and closer (or screen-edge "infinite" targets);
  primary actions large, destructive small/guarded.
- **Hick's Law:** fewer choices = faster decisions; reduce options per screen, use progressive disclosure.
- **Jakob's Law:** match platform/competitor conventions (ties back to button order).
- **Nielsen's 10 heuristics** as a review checklist: visibility of system status, match real world, user
  control/undo, consistency, error prevention, recognition over recall, flexibility, minimal aesthetic,
  help users recover from errors, help/docs.

---

## Sources
✅ primary: nextjs.org App Router docs (linking/prefetch, intercepting & parallel routes), every-layout.dev
(Stack/primitives, gap-vs-margin), nngroup.com (OK-Cancel order, skeleton screens, button states,
heuristics), design-system.service.gov.uk (button hierarchy/placement), developer.apple.com HIG (button
order), uxmovement.com (form-button placement), smashingmagazine.com (sticky menus), adamsilver.io
(destructive actions), w3.org WCAG 2.2 (focus-visible), aurorascharff.no (active NavLink). Verify pass was
rate-limited (false-negative votes) — claims rest on these primary sources + corroboration. See
`design-system` for the visual layer this composes with.
