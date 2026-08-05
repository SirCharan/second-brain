---
name: marketing-microsite-design
description: >
  Design recipes for marketing / landing / GTM microsites (product launches, pitch sites, campaign
  pages) built on Next.js + Tailwind + Vercel.
  Covers the proven hero structure, section order, CTA hierarchy, social proof, pricing tables,
  conversion best-practices, entrance/scroll motion, font pairings, and the Bento/Minimal/Aurora
  look. Load alongside the `design-system` skill (it owns tokens, a11y, motion mechanics).
  Trigger on: "landing page", "marketing site", "GTM microsite", "launch page", "pitch site",
  "hero section", "pricing page", "convert", or styling a product-marketing page.
---

# Marketing / Microsite Design

Pair with `design-system` (foundations + premium checklist) and **`layout-interaction-design`** (CTA/
button placement §2, nav §3, scroll/entrance states §4). This skill = layout, conversion, and the
marketing look. ✅ strong consensus · ◐ situational.

## Hero — above the fold ✅ (element order)
1. **Eyebrow/kicker** — often a social-proof micro-line ("Used by 5,000+ traders").
2. **Headline** — one idea, **<10 words**, benefit not feature.
3. **Subhead** — 1–2 lines clarifying the headline.
4. **Primary CTA** + optional **secondary** (ghost) CTA.
5. **Product visual** (screenshot/loop) above the fold.
6. **Trust strip** (logos/rating) right under the fold line.

## CTA hierarchy ✅
- **One** primary action, repeated *identically* at top, mid (after proof), and bottom; **sticky CTA on
  mobile**. Don't invent a new primary verb per section.
- Secondary CTA is visually subordinate (ghost/text), never a competing color.
- Place the CTA *beside the value statement*, not floating alone. ◐ On focused landing pages, strip the
  top nav to reduce exits.

## Section rhythm ✅
Hero → value prop → how-it-works (3 steps) → benefits/features → social proof → pricing → FAQ → final
CTA. One idea per section; alternate background shades (`--bg` / `--surface`) to segment.

## Social proof ✅
Twice minimum: a logo/rating strip high (under hero) + testimonials/case studies near each CTA. Specific
numbers ("5,000 users", "4.8★") beat vague praise.

## Pricing tables ✅
- **3 tiers** (anchoring; most pick tier 2). Highlight the recommended/middle plan — contrasting border +
  "Most Popular" badge is the single most reliable conversion lever.
- Checkmark feature grid for scanning; monthly/annual toggle; page must load <2s. ◐ A high "Enterprise /
  Contact us" tier anchors even if few choose it.

## Conversion specifics ✅
Message-match the inbound ad/headline; remove distractions; benefit-first copy; **speed = conversion**
(~7–10% drop per added second). Optimize the hero image; lazy-load below the fold.

## Motion ✅
- Baseline: subtle **fade-up on enter** via IntersectionObserver (not scroll listeners); stagger cards
  30–50ms; durations <700ms (micro <300ms). Animate **transform + opacity only**.
- Scroll-driven effects via CSS `animation-timeline: view()` where supported; graceful fallback.
- **Always gate behind `prefers-reduced-motion`** — reduced users get instant content, same function.

## Type & look
- **Fonts:** characterful display + clean body. Pairs: **Bricolage Grotesque** + Geist · **Fraunces**
  (opsz) + Inter · **Space Grotesk** + IBM Plex Sans. Bigger ratio (1.333) for drama; tracking
  `-0.02 to -0.03em` on the hero headline; `text-wrap: balance` on headings.
- **Style:** ✅ Bento grid + Minimalism for the bones; ◐ one **Aurora/mesh** or **Glassmorphism** accent in
  the hero (≤3 complementary gradient stops) for a distinctive, non-templated moment. Neo-brutalism only
  if "bold challenger" is the explicit brief — it reads unserious for a fintech pitch.
- **Light vs dark** ◐: default light for broad B2B/consumer trust; dark fits dev-tools/crypto identity
  (matches the house stack). Support both; keep contrast.

## Pitfalls
Multiple competing CTAs · feature-listing instead of benefit copy · stock-photo heroes (use real product
shots) · motion that delays content · pricing with >3 tiers · slow LCP from an unoptimized hero image.

## Sources
goprimer.com (hero formula) · involve.me (landing structure) · saashero.net (CTA placement) ·
kinde.com & designstudiouiux.com (pricing that converts) · motion.dev & joshwcomeau.com (scroll motion).
