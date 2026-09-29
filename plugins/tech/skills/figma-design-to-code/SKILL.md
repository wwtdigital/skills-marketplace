---
name: figma-design-to-code
description: >
  Implement Figma designs as code by driving a real browser with playwright-cli: extract tokens
  and measurements from the Figma UI's DOM (not pixels), implement against the token layer, then
  verify with computed styles plus screenshots at multiple widths. Use when asked to implement or
  port a Figma design, build a page from a mockup, match a UI to a Figma file, extract design
  tokens (colors, type scale, radii, spacing) from Figma, or visually verify a UI against a
  design reference. Not for writing into Figma or generating Figma designs from code (use the
  Figma plugin's figma-use / figma-generate-design skills), and not for WWT slide decks (use
  wwtdigital-deck-design).
metadata:
  owner: zachary.lampert@wwt.com
  category: tech
  status: beta
  connectors: []
  version: 0.1.0
---

# Figma design → code

Turn a Figma design into working UI by (1) **reading values out of the Figma UI's DOM**,
(2) implementing against a token layer, (3) verifying with computed styles + screenshots at
multiple widths.

**The single most important thing:** the Figma *canvas* is WebGL — one opaque `<canvas>`, no
DOM for design layers. But the *panels around it* are ordinary DOM, and Figma's Properties
panel exposes **variable/token names alongside resolved values**. So extract with
`snapshot`/`eval`, not screenshots. Screenshots are for judging composition, nothing else.
The CLI's own docs agree: screenshot is "rarely used, as snapshot is more common."

## Before you start

1. Check for the CLI: `command -v playwright-cli`. If it's missing, tell the person to install
   it with `npm install -g @playwright/cli@latest` (needs Node) and stop until they have.
2. Ask for the Figma file or frame URL and the target repo/route, if not already given.
3. The Figma MCP server is optional (fallback only, see below). If its tools aren't available,
   carry on with the browser path; to add it, connect Figma under Connectors in the Claude app
   settings, or run `/mcp` in Claude Code.

## Browser setup

```bash
playwright-cli -s=figma open --headed --persistent \
  --config /path/to/cfg.json https://www.figma.com/files/recents
```

- **`--headed` is an option on `open`, NOT a global flag** — it goes after the subcommand.
  Without it you get a headless browser and the user cannot log in. A `--config` setting
  `viewport: null` only unpins the viewport; it does **nothing** for headed.
- **`--persistent`** keeps the Figma login across sessions. Worth it — login is the only
  friction. Then hand the window to the user to authenticate; don't try to log in for them.
- `-s=<name>` names the session so state persists across invocations.
- Config for unpinned viewport (needed later for responsive testing of *your app*, not Figma):
  `{"browser":{"contextOptions":{"viewport":null}}}`

## Extraction: the DOM, in priority order

### 1. Styles library — whole token layer in one call

With **nothing selected**, the right panel shows the page's local Styles tree. Expand the
folders and dump it — this is the cheapest, highest-yield read available:

```bash
playwright-cli -s=figma --raw eval "el => el.innerText" <tree-ref>
# "Heading\nH1\n· 36/43\nH2\n· 30/36 … Display\nXL\n· 72/76"
```

`· 36/43` is `font-size/line-height`. One call returned a complete 24-style type scale.

### 2. Single selected node — layout, color, radius, *with variable names*

```bash
playwright-cli -s=figma --raw eval \
  "() => document.querySelector('[aria-label=\"Right sidebar\"]')?.innerText"
```

Real output for one swatch:

```
Brand 500 (default)
Layout   Flow Vertical · Width Fixed (110px) · Height Hug (49px)
Radius   radius/card          ← VARIABLE NAME
Border   2.5px · Padding 10px · Gap 2px
Colors   Color/Brand/500      ← VARIABLE NAME
         #F6543C              ← resolved value
Borders  2.5px · All sides · #0F0F0D · Outer alignment
```

Token names come through **without Dev Mode** and without the Enterprise-gated variables
REST endpoint. This is the prize — don't go hunting for a PAT before trying it.

### 3. Layer tree — names are often the token names

In a well-built system file the layer rows *are* the ramp: `Brand 50` … `Brand 900`,
`Brand 500 (default)`. Read them straight from `snapshot`.

### Walking the tree (the only way to get everything)

The panel describes **one node at a time**. Multi-select collapses to a truncated color list
(observed: `58 more`, `11 more`), so bulk selection is useless. Loop instead:

```bash
playwright-cli -s=figma snapshot > /tmp/snap.txt
grep -nE 'row "' /tmp/snap.txt | grep 'level=3'   # find leaf refs
# then per ref: click it, eval the panel, accumulate
```

- **`press Enter` selects ALL children** — it does not drill to one node. Click leaf rows in
  the layers tree instead. (This wasted two attempts.)
- Switching pages **invalidates refs**. Re-`snapshot` after any page change, and prefer the
  `[aria-label="Right sidebar"]` selector over a captured ref.
- Sidebar `innerText` carries chrome noise (`L L Share Comments … Request access`) before the
  node name. Slice from the node name onward. The panel *body* has no stable selector I've
  found — its ref changes per selection.

### Parsing gotchas

Values are **display strings**, not numbers: `Fixed (110px)`, `Hug (49px)`, `· 36/43`, and
`1,920px` — note the **thousands comma**. Strip it before `parseInt`.

## What the DOM cannot give you

The canvas is a single opaque node (`application [ref=…]`). Composition, spacing rhythm,
visual hierarchy, "does it actually look right" — **screenshot for those**, and `Read` the
PNG. Full CSS / box-model output requires Dev Mode, which may not be on the account (check
for a "Get coding, faster / Request access" upsell in the panel — that means no Dev Mode).

## Fallbacks, when no file is open in the browser

1. **Figma MCP** — `get_variable_defs`, `get_design_context`, `get_screenshot`,
   `get_metadata`. Exact, structured. Rate-limits and sometimes 404s; load `/figma-use`
   skills first only if *writing* to Figma.
2. **REST API** — `GET /v1/files/:key/nodes?ids=…` with a PAT returns exact JSON: `fills`,
   `cornerRadius`, `layoutMode`, `itemSpacing`, `padding*`, `style.fontSize`/`letterSpacing`,
   `boundVariables`. No MCP rate limit, diffable. Caveat:
   `GET /v1/files/:key/variables/local` — the clean token source — is **Enterprise-plan
   gated**; below that you get resolved values and must infer names.
3. Screenshots — last resort for values.

## Implementation rules

- **Content-driven, never hard-coded.** Copy, imagery, prices, store lists, footer links come
  from the real sources (gateway / CMS / config). A design is a *layout+style* spec, not a
  content spec. Hard-coded strings are a bug.
- **Extract the token layer first** (colors, spacing, radii, type scale) into the app's tokens
  (e.g. `styles/tokens.css`), then build components against tokens — never scatter literal hex.
  Map Figma's namespaces (`Color/Brand/500`, `radius/card`) onto existing token names.
- If the repo splits a shared platform package from brand apps, keep reusable design in the
  **platform package**; the brand app supplies only theme/manifest/content. Match surrounding
  conventions.
- Run the app **live** while iterating so the user watches changes land. If the harness keeps
  killing background servers, hand them a `! <cmd>` one-liner to run attached.

## Verifying

- **Diff computed styles, not pixels.** `playwright-cli eval "el => getComputedStyle(el).padding" <ref>`
  turns a subjective visual check into a numeric one. Compare against the values extracted above.
- **Then screenshot at ≥2 widths** (~390–430px mobile, ~1400px desktop) and `Read` them for
  composition: eyebrow letter-spacing, pill/button radii, icon-chip colors, hero type scale,
  promo banner, bottom-nav FAB, drawer overlays, safe-area padding.
- **Responsive — the viewport trap:** by default playwright-cli **pins a fixed viewport**, so
  resizing the window does not change `innerWidth` and layout won't reflow. Relaunch with
  `viewport: null` (above), then `resize`. Confirm via `document.documentElement.clientWidth`.
- **Canvas-rendered apps (Flutter web / CanvasKit)** have no queryable DOM — screenshot only.
  Readiness = `flt-glass-pane`/`flutter-view` present; the `<canvas>` is in the glass-pane
  **shadow DOM**, so `querySelector('canvas')` is false. Hash routing → deep links are `/#/route`.
- Drawers/overlays: confirm they open on the route and **close on navigation away**.
- Selectors are **strict-mode**: matching >1 element errors. Prefer `[aria-label='…']` or a
  unique class; `text=Foo` often multi-matches.
- `screenshot` needs `--filename <path>` — a **bare path is parsed as a CSS selector**.

## Gotchas checklist

- Launched headless when the user said headed → `--headed` belongs on `open`.
- Reading pixels for values that were in the DOM all along → snapshot/eval first.
- `press Enter` to "drill in" → multi-selected every child; click the leaf row.
- Panel shows `N more` → you multi-selected; select one node.
- Refs stale after a page switch → re-snapshot.
- `parseInt("1,920px")` → 1. Strip the comma.
- Forgot `--filename` → path treated as a selector, nothing captured.
- Layout won't reflow on resize → viewport pinned; relaunch with `viewport:null`.
- Verifying a canvas app via DOM snapshot → useless; screenshot instead.
- Baked-in demo content that should come from a provider → not done; wire the real source.
