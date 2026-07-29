---
name: pro-max-search
description: "How to drive the ui-ux-pro-max plugin's search.py design-intelligence engine with the house-stack defaults baked in. Load this when the design-router (or your own judgment) has decided ui-ux-pro-max is the skill for a NON-Delta UI task and you need the exact command to generate a design system, look up a palette, font pairing, chart palette, or stack best-practices. Covers: locating the installed search.py, invoking it by absolute path from the project root (never cd), the --design-system generator + dials (--variance/--motion/--density), --persist MASTER+Overrides, and copy-paste templates defaulting to Next.js + Tailwind v4 + shadcn/ui. Requires the ui-ux-pro-max pack (see starter-pack/manifest.json). Trigger on: run ui-ux-pro-max, generate a design system, pro-max search, palette/font/chart lookup, --design-system."
---

# pro-max-search — driving the ui-ux-pro-max engine

Operational wrapper around the `ui-ux-pro-max` plugin's `search.py`. The `ui-ux-pro-max` skill itself has the full domain reference; this skill is the fast path with your defaults.

## 0. Locate the script (installed as a plugin, path varies by version)

```bash
SEARCH=$(find ~/.claude/plugins -name search.py -path '*ui-ux-pro-max*' 2>/dev/null | head -1)
[ -z "$SEARCH" ] && echo "NOT INSTALLED — run: /plugin marketplace add nextlevelbuilder/ui-ux-pro-max-skill && /plugin install ui-ux-pro-max@ui-ux-pro-max-skill"
echo "$SEARCH"
```

**Invoke by absolute path from the PROJECT ROOT — do NOT `cd` into the script's dir.** Python auto-adds the script's own directory to `sys.path`, so `from core import …` resolves fine from anywhere. And `--persist` writes its `design-system/` folder to **cwd**, so you must be standing in the project root (cd-ing into the plugin cache would write it there instead):

```bash
cd /path/to/your/project
python3 "$SEARCH" "<query>" ...        # macOS: python3 (Windows: python)
```

If Python is missing: `brew install python3` (no pip deps — pure stdlib).

## 1. Generate a design system (ALWAYS the first move for a new unbranded UI)

```bash
python3 "$SEARCH" "<product-type industry tone density keywords>" --design-system -p "Project Name" --stack nextjs
```

- Query = **multi-dimensional**: product + industry + tone + density (e.g. `"fintech trading dashboard dark data-dense professional"`), not just `"dashboard"`.
- `--stack`: default to `nextjs` or `shadcn` for the house stack. (Others: react, vue, svelte, astro, swiftui, flutter, react-native.)
- Returns: pattern, style, color palette, typography pairing, effects, anti-patterns.
- Add `-f markdown` to get docs-friendly output instead of the ASCII box.

### Dials (optional, only with --design-system) — defaults in bold

| Dial | 1-3 | 4-7 | 8-10 | Use for |
|---|---|---|---|---|
| `--variance` | centered/minimal | **balanced/modern** | bold/asymmetric | brand tone |
| `--motion` | subtle | **standard** | complex (attaches GSAP snippet) | marketing = higher, dashboard = lower |
| `--density` | spacious (marketing) | **standard** | dense (dashboards/trading) | trading UIs → 8-10 |

Trading/analytics dashboard example (a common case):
```bash
python3 "$SEARCH" "crypto perps analytics dashboard dark data-dense" --design-system -p "Acme Dashboard" --stack nextjs --variance 5 --density 9 --motion 3
```

## 2. Persist across sessions (bigger projects)

```bash
python3 "$SEARCH" "<query>" --design-system --persist -p "Project Name"           # writes design-system/<slug>/MASTER.md
python3 "$SEARCH" "<query>" --design-system --persist -p "Project Name" --page "dashboard"   # + <slug>/pages/dashboard.md
```
Paths use a project **slug** (project name lowercased, spaces→dashes), written under **cwd**. So for `-p "Acme Dashboard"` → `design-system/acme-dashboard/MASTER.md` + `design-system/acme-dashboard/pages/dashboard.md`. When building a page: read the project's `MASTER.md`; if its `pages/<page>.md` exists, those rules override the master.

## 3. Deep-dive a single dimension (after the design system)

```bash
python3 "$SEARCH" "<keyword>" --domain <domain>
```
Valid domains (argparse-enforced): `style` `color` `chart` `landing` `product` `ux` `typography` `icons` `gsap` `react` `web` `google-fonts` · plus `--stack <name>` for framework best-practices. (There is no `prompt` domain — AI-prompt/CSS keywords are folded into `style`.)

Common lookups:
```bash
python3 "$SEARCH" "fintech vibrant dark" --domain color         # palette
python3 "$SEARCH" "professional modern" --domain typography     # font pairing
python3 "$SEARCH" "real-time dashboard" --domain chart          # chart type + lib
python3 "$SEARCH" "animation accessibility loading" --domain ux # pre-delivery UX pass
python3 "$SEARCH" "app-router rsc rendering" --stack nextjs      # stack best-practices
```

## Notes

- This is the engine for **unbranded** work (see `design-router`). When the project has a fixed brand system, use its tokens instead — do not run the generator.
- After generating, still honor your house constants: real font (never `system-ui`), semantic tokens (no hardcoded hex), WCAG 2.2 AA + CVD check, verify the deployed URL.
- The bundled `ui-ux-pro-max` skill also ships `design`, `brand`, `ui-styling`, `banner-design`, `slides` sub-skills — reach for those for logos/brand/banners/presentations.
