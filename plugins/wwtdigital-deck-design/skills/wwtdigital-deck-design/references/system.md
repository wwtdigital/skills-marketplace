## 0. How to work

The order of work is in **The Contract**, section 5. This is the per-slide detail.

1. Ask what the slide has to land before asking what it should look like. One sentence per slide.
   If you cannot write that sentence the slide has no job and should not exist.
2. Pick the slot assembly, not the template. Check the spans sum to 12.
3. **Copy the geometry from `assets/recipes.html` and the tokens from `assets/system.css`.**
   Do not retype a hex value and do not reconstruct a layout from the section 12 table.
4. Tag every slide `data-role="cover|divider|statement|content|data|closing"`. The role sets the
   density band and the substance floor, and `SEQ-04` caps how much of a deck may claim a sparse one.
5. A build that continues the previous slide declares itself: `data-builds-on="prev"`.
6. Run the validator. Fix every FAIL. Record a reason for every accepted WARN.
7. Output self-contained HTML at 1920 × 1080 per slide unless PPTX is asked for. If it is,
   `export_pptx.py` then `verify_pptx.py`, and never render pages to images.

---

## 1. Tokens — paste this block, do not edit it

```css
:root{
  --wwt-blue:#0086EA; --wwt-purple:#330072; --wwt-red:#EE282A;
  --wwt-blue-93:rgba(0,134,234,.93);
  --ink-900:#000000; --ink-800:#1F1F1F; --ink-600:#404040; --ink-500:#656565;
  --ink-400:#808080; --ink-200:#BFBFBF; --ink-100:#E4E4E4;
  --surface:#F6F6F6; --surface-raised:#FFFFFF; --scrim:rgba(0,0,0,.36);

  --grad-brand-v:linear-gradient(180deg,#0086EA 0%,#330072 100%);
  --grad-brand-v-93:linear-gradient(180deg,rgba(0,134,234,.93) 0%,rgba(51,0,114,.93) 100%);
  --grad-brand-diag:linear-gradient(164deg,#0086EA 8%,#330072 63%);
  --grad-brand-h:linear-gradient(90deg,#0086EA 0%,#330072 100%);
  --grad-photo-scrim:linear-gradient(180deg,rgba(255,255,255,0) 0%,rgba(0,0,0,.30) 49%,rgba(0,0,0,.62) 100%);
  --grad-bug:linear-gradient(180deg,#F6F6F6 0%,#FFFFFF 100%);

  --shadow-panel:0 1px 25px 7px rgba(0,0,0,.10);
  --margin-x:72px; --rail-top:56px; --rail-bottom:56px; --content-top:156px;
  --col:126px; --gutter:24px;
  --s1:8px;--s2:16px;--s3:24px;--s4:32px;--s5:40px;--s6:56px;--s7:72px;--s8:96px;--s9:120px;

  --font-sans:'Aptos',system-ui,sans-serif;
  --font-serif:'Aptos Serif',Georgia,serif;
  --font-mono:ui-monospace,'DejaVu Sans Mono',Menlo,Consolas,monospace;
}
```

The stacks are deliberately short. Aptos is embedded, so there is nothing to fall back to and
nothing that should quietly substitute — see section 3.

---

## 2. Canvas and grid

Canvas 1920 × 1080. Margin 72px L/R. Rails 56px top and bottom. Content top 156px.
Grid 12 × 126px with 24px gutters = 1776. Safe area 1776 × 968.

Column left edges: 72, 222, 372, 522, 672, 822, 972, 1122, 1272, 1422, 1572, 1722.
Spans: 4 col 576 · 5 col 726 · 6 col 876 · 7 col 1026 · 8 col 1176 · 12 col 1776.
Headline maximum is 8 columns. Adjacent spans sum to 12.

**Scaling for HTML:** build each slide at a fixed 1920 × 1080, wrap in a container with
`aspect-ratio:16/9;overflow:hidden`, scale with `transform:scale(containerWidth/1920)` and
`transform-origin:top left`. `transform` does not scale computed font size — measure geometry through
the scale factor, never type. Measure contrast at native 1920 resolution.

---

## 3. Typography ladder

### The face is Aptos, and it comes from the machine

Aptos is Microsoft's, so the plugin does not ship it. `scripts/brand_assets.py` finds the cuts on the
machine by the name inside each file: inside PowerPoint/Word for Mac, in the system font folders, in
Office's cloud-font cache on Windows, in `~/.wwtdigital-deck-design/fonts`, or wherever `WWT_FONTS_DIR`
points. (Not Office's cache on a Mac: reading it raises a macOS privacy prompt.) `inline_assets.py`
writes them in as `@font-face` rules and **stops with instructions if a cut is missing.** **Do not
link Google Fonts and do not name a webfont fallback.** If the doctor reports Aptos missing, tell the
person how to install it (Microsoft's free download:
https://www.microsoft.com/en-us/download/details.aspx?id=106087) and stop; do not build around it.

| CSS weight | Cut | Found by full name |
|---|---|---|
| 400 | Aptos Regular | `Aptos` |
| 600 | Aptos SemiBold | `Aptos SemiBold` |
| 700 | Aptos Bold | `Aptos Bold` |
| 800 | Aptos ExtraBold | `Aptos ExtraBold` |
| 900 | **Aptos Black** | `Aptos Black` |
| 700 italic | Aptos Serif Bold Italic | `Aptos Serif Bold Italic` |

The five sans cuts come with Microsoft 365. **Aptos Serif does not**: it is an Office cloud font, so
on most machines it is absent until the Microsoft download is installed. It is only required when a
deck sets a pull quote (`.t-quote`).

**Why the explicit map exists.** Aptos ships its heavy cuts as *separate families*: the Black file
reports family "Aptos Black", subfamily "Regular", not weight 900 of family "Aptos". So
`font-family:'Aptos';font-weight:900` finds no 900 face, and the browser fakes one from Bold. Every
headline renders visibly light and nothing warns you. The `@font-face` rules bind each weight to its
real file, and `font-synthesis:none` makes a missing cut fail loudly instead of quietly.

The source names cuts, not numbers: the Figma divider is `Aptos:Black` for the title and `Aptos:Bold`
for the presenters. Read the ladder's "Face" column as the named cut.

**Aptos Narrow is not part of this design.** Removed at v2.0 by direction. The Figma source does use
it in two places on the divider, the date line and the duration, so this is a deliberate divergence
from the source rather than a correction to it. The token and both font files are gone, so nothing
can fall back into it by accident. Anything that was Narrow is now regular Aptos, which is wider:
the eyebrow grew about 13% on the same string.

| Token | Face | Size | Line | Tracking | Case | Job |
|---|---|---|---|---|---|---|
| display-1 | Black | 200 | .80 | -.07em | Upper | Cover. 2 lines max. Holds 13 chars in a 1453px box |
| display-1 tight | Black | 176 | .80 | -.07em | Upper | Cover, only when 200 genuinely overflows |
| display-2 | Black | 128 | .875 | -.07em | Upper | Closing |
| h1-lg | Black | 112 | .86 | -.065em | Upper | Statement slides |
| h1 | Black | 96 | .875 | -.06em | Upper | Section headline, 8 col, 3 lines max |
| h1--stmt | Black | 96 | **80px** | -.05em | **Sentence** | Sentence-case statement in a narrow measure. The one headline that may run past 3 lines |
| h2 | Black | 80 | .95 | -.06em | Upper | Headline beside a half image or panel |
| h3 | Bold | 48 | 52 | -.03em | Title | Panel heading, chart title |
| label | Bold | 36 | 40 | -.02em | Title | Stat label, feature label, card heading |
| lede | Regular | 45 | 56 | 0 | Sentence | One sentence under a headline |
| body-l | Regular | 32 | 44 | 0 | Sentence | Statement slides |
| body | Regular | 26 | 36 | 0 | Sentence | Default |
| body-s | Regular | 24 | 33 | 0 | Sentence | Cards, bullets, table cells |
| micro | **Bold** | 22 | 28 | 0 | Title | Running header, source lines |
| caption | Regular | 20 | 28 | 0 | Sentence | Sources, credits |
| quote | Serif Bold Italic | 64 | 76 | -.05em | Sentence | Pull quote. Only serif in the system |
| cover-sub | Regular | 40 | 52 | 0 | Sentence | Cover subhead, one line |
| stat-hero | Black | 200 | .80 | -.07em | — | A number as the slide's entry point |
| stat-rail | Black | 57 | 1 | -.07em | — | Numeral on the process rail (recipe 14) |
| stat value | Black | 96 / 64 / 48 | .92 | -.04em | — | Sizes by hierarchy, not by fit |
| badge | Black | 48 | 1 | -.03em | — | Sequence number in a 96 square |

Legal sizes, nothing between: **200 176 128 112 96 80 64 57 56 48 45 40 36 32 30 28 26 24 22 20**.

The **divider title** is an exception worth knowing: 96px Black on an **85px line** with zero tracking,
set inside its gradient band. Not the h1 metrics.

The running header is **Bold 700 throughout**. At 22px, weight 600 is not WCAG large-scale.

### The two-beat headline — the signature
Setup in `--ink-800`, payoff in `--ink-900`, wrapped in `<em>` styled `font-style:normal`. The emphasis
clause is the **last two to four words**. On dark or white-type headlines it inverts to white at 72%
opacity — handle `.white.t-h1 em` and `.on-dark .t-h1 em` together, or the emphasis clause turns black
on a dark photograph and disappears.

### Non-negotiables
Tracking scales with size. Line height below 1 only in display. No uppercase at 48px or below, except
the eyebrow. One serif per deck, and it is a quote. Three lines maximum on any headline, the sole
exception being `t-h1--stmt`, which is capped by block height instead. Display lines never auto-wrap —
break them yourself.

**Never leave one word alone on the last line.** A widow reads as a mistake at slide scale. Bind the
last two words with a non-breaking space, widen the measure by a column, or hand-break the line.
Display headlines are exempt because you break those yourself. Two traps: a hyphen or en dash is its
own break opportunity, so a non-breaking space either side of one does not always hold — widen or
hand-break instead. And binding two words can push a headline onto an extra line, so re-check the
slide after every bind.

---

## 4. Colour

- **Everything in the ladder except the 20px caption is WCAG large-scale text** (24px regular /
  18.7px bold), so 3:1 applies. The 20px caption needs 4.5:1.
- Blue on white 3.75:1, on surface 3.47:1. White on flat blue 3.75:1, which clears large-scale, so
  **solid blue boxes with white type at 24px bold are legal** and are the right treatment when a set of
  peer labels should read as one system rather than as separate cards.
- Brand gradient against white: 3.75:1 at the blue end, 8.54:1 mid, 15.18:1 at purple.
- Red is never type and never a fill. Purple is never a flat fill. Ink 400 needs 22px minimum.

**Per slide: one accent job, one red mark, one gradient surface, one background device.** Process
connectors (`.arrow--connector`) are structural and exempt from the one-mark rule.

---

## 5. Gradients

Brand vertical 180deg 0/100 is the default. Brand vertical 93 for panels over photography. Brand
diagonal 164deg 8%/63% for the Brand X only. Brand horizontal 90deg for anything under 120px tall.
Photo scrim 180deg 0 / .30 at 49% / .62. Bug wedge 180deg #F6F6F6 → #FFFFFF.

Never reverse it, never add a stop, never gradient type.

**A gradient spans the element it belongs to, not each of its parts.** A table header takes one ramp
across the whole row — `table.deck thead tr{background:var(--grad-brand-h)}` with the cells
transparent. Painting the ramp on each `th` restarts it in every column and reads as coloured chips.

---

## 6. Space

| Role | Ink target | Hard floor |
|---|---|---|
| Cover | 20–30% | 35% |
| Divider | 15–25% | 30% |
| Statement | 25–35% | 40% |
| Content | 35–45% | 50% |
| Data | 45–50% | 55% |
| Closing | 20–30% | 35% |

**Ink counts content, not ground.** Photography touching two or more canvas edges is ground. Measure
as a union on a 192 × 108 grid, never a sum of boxes.

Rhythm: headline→lede 32 · lede→body 56 · body→body 24 · **block→block 96** · panel→panel 24 · panel
interior 56 (40 under 500px wide) · last element→bottom edge 96 minimum.

**A panel needs real space under its last line** — 40px minimum, 56 preferred. Copy ending flush
against a panel edge is the most common cramped-looking mistake, and the ink metric will not catch it
because a taller panel scores *worse*. Where the metric and the eye disagree, the eye wins and the
number gets recorded as an accepted WARN.

**A badge overlapping a card needs clearance beneath it too.** Where a badge sits in a card's corner,
the copy under it starts 40px below the badge, not at the panel's normal first baseline.

Nothing centers except a divider title and a card-row headline. Splits run 5/7 or 7/5, never 6/6.

---

## 7. Photography

| Crop | Ratio | Size | Use |
|---|---|---|---|
| bleed | 16:9 | 1920 × 1080 | Cover, divider, closing, statement |
| band | 4.06:1 | 1920 × 473 | Top band, type below it |
| half | 1.02:1 | 1103 × 1080 | Hero left or right |
| inset band | 3.95:1 | 1307 × 331 | Inside the safe area, beside a stat |
| panel inset | 3.46:1 | 796 × 230 | Inside a panel, above its copy |
| card | 2.02:1 | 525 × 260 | Top of a card in a 3-up row |
| wide band | 2.33:1 | 1186 × 509 | Runs off one edge beside a figure column (recipe 08) |
| foot band | 7.27:1 | 1920 × 264 | A sliver across the foot, under a card (recipe 18) |
| three-two | 1.50:1 | 1187 × 791 | Fills the upper right of a split (recipe 21) |

**Where to put an image on a text-led slide.** An 8-column headline leaves a 4-column void at the top
right. A card-crop photograph at 576 × 285 on the last column drops straight into it without pushing
anything off the grid, and is usually the answer to "can this slide have a picture?"

### Scrims compose — this is a real trap

An element has one `::after`. Two scrim classes that both own `::after` silently cancel. Scrims
therefore set custom properties and share one pseudo-element.

```css
.media::after{content:"";position:absolute;inset:0;pointer-events:none;
              background:var(--scrim-1,none),var(--scrim-2,none)}
.scrim-flat{--scrim-1:linear-gradient(rgba(0,0,0,.36),rgba(0,0,0,.36))}
.scrim-grad{--scrim-1:var(--grad-photo-scrim)}
.scrim-r   {--scrim-1:linear-gradient(90deg,rgba(0,0,0,.55) 0%,rgba(0,0,0,.18) 46%,transparent 72%)}
.scrim-t   {--scrim-2:linear-gradient(180deg,rgba(0,0,0,.58) 0%,rgba(0,0,0,.20) 34%,transparent 62%)}
```

**Measure the scrim.** White on the .36 flat scrim over a light area measures 2.52:1 and fails. It only
works where the pixels behind the type sit below about 0.22 relative luminance. Sample the 90th
percentile, not the average. A right-anchored mesh brightens the top-right, where the running header
lives — that pairing needs `.scrim-t`.

**A divider needs no scrim at all**, because its type sits inside opaque panels rather than on the
photograph.

### The photography library

**Signal** is abstract blue-red holographic portraiture, for capability. **Evidence** is documentary —
our people, labs and buildings — for something we actually did.

| ID | Family | Crops | Pixels | Note |
|---|---|---|---|---|
| `gaze-rb` | Signal | bleed, band | 2006 × 1080 | The Figma cover frame. Face right of centre, headline goes left |
| `twin-rb` | Signal | half, bleed | 1920 × 1781 | The Figma closing frame. Strongest red-blue split |
| `eyes-closed` | Signal | half | 1920 × 2040 | Near-square. Hero left or right without recropping |
| `profile-blue` | Signal | bleed, card | 1927 × 1080 | Faces right. Mirror rather than recrop when the layout flips |
| `profile-wide` | Signal | card, inset | 2238 × 1080 | Native 2.07 lands on the card crop with no crop at all |
| `profile-band` | Signal | inset, band | 3291 × 1080 | The only frame wide enough for the inset band |
| `upward` | Signal | half | 1920 × 1955 | Square, subject centred, wants type beside it |
| `network` | Signal | card, inset | 2829 × 1080 | Reads as literal networking. Use sparingly, it dates fastest |
| `neon-tall` | Signal | half | 1793 × 3197 | Tall portrait, magenta and blue |
| `datacenter-aisle` | Signal | half, band, card | 1536 × 1024 ⚠ | Data center aisle, blue and red. The source frame on node `1839:55` and the darkest in the library: p90 luminance 0.09, so white type clears with no scrim. p99 is 0.55 on the specular lights, so keep a headline off the bright rack faces |
| `wave-portrait` | Signal | bleed, band | 1920 × 1507 | Portrait dissolving into red and blue waves |
| `wall-touch` | Evidence | bleed | 1920 × 1081 | Darkest frame in the set. The divider frame |
| `keyboard` | Evidence | band, inset | 1920 × 1278 | Neutral, works under any headline |
| `pair-laptop` | Evidence | band, bleed | 1798 × 772 ⚠ | The default working shot |
| `conversation` | Evidence | card, panel inset | 1712 × 843 | Colleagues mid-conversation |
| `team-desks` | Evidence | band, card | 1800 × 1200 ⚠ | Team at adjoining desks |
| `atc-lobby` | Evidence | card, band | 1682 × 1010 ⚠ | ATC lobby with visitors |
| `hq-confetti` | Evidence | half, panel inset | 1671 × 1114 | HQ exterior. The St. Louis proof shot |
| `phone-street` | Evidence | card | 1800 × 1201 | For device and product slides |

**Every file is at `assets/photos/<id>.jpg`,** sized to cover the full 1920 × 1080 canvas wherever the source allowed it, so the crop list can change later without re-cutting pixels. **⚠ marks a frame whose resolution falls short of a crop it is listed for:** `pair-laptop` is 1798 × 772 against band and bleed; `team-desks` is 1800 × 1200 against band; `atc-lobby` is 1682 × 1010 against band; `datacenter-aisle` is 1536 × 1024, so a 1623-wide crop upscales 6% and a full bleed 25%. Those are upscales, not crops. Take them at a smaller crop or replace the source frame.

Every image carries descriptive alt text. Decorative marks carry `alt="" aria-hidden="true"`.

---

## 8. Background patterns — one device per slide

### Diamond mesh — one asset, three placements

Half-drop tessellation of down-pointing triangles, base 53.53, height 26.96, every row offset half a
base from the row above. **Rows abut, they never overlap.**

One userSpace `linearGradient` shared by all 882 triangles carries the fade, in absolute coordinates.
Exporting the same node from a different position returns a byte-identical file. **The variant is
chosen by where you put it, never by which export you were handed.**

| Class | Asset | Box | Placement |
|---|---|---|---|
| `.mesh--diag` | `assets/vectors/mesh-diag.svg` | 1205 × 1080 | **left-justified, x 0** |
| `.mesh--center` | `assets/vectors/mesh-center.svg` | 1920 × 1080 | spans the page |
| `.mesh--h` | `assets/vectors/mesh-h.svg` | 1182 × 1080 | right-anchored, 32px bleed, 8px lift |
| `.mesh--r` | `assets/vectors/mesh-diag.svg` | 1192 × 1068 | pushed right to left 728, top 6, so the fade runs off the far edge (node 1659:988) |

```css
.mesh{position:absolute;top:0;height:1080px;pointer-events:none;
      opacity:.11;mix-blend-mode:plus-lighter;background-repeat:no-repeat}
.mesh--diag  {left:0;width:1205px;background:url(assets/vectors/mesh-diag.svg) 0 0/1205px 1080px}
.mesh--center{left:0;width:1920px;background:url(assets/vectors/mesh-center.svg) 0 0/1920px 1080px}
.mesh--h     {right:-32px;top:-8px;width:1182px;background:url(assets/vectors/mesh-h.svg) 0 0/1182px 1080px}
```

Content left → `.mesh--h` (the default). Content right → `.mesh--diag`. Centred → `.mesh--center`.

**`.mesh--center` needs a different asset**: a 1205-wide box cannot be centred on a 1920 page, so
extend the field by exactly **14 lattice periods (749.389px)** — an integer number, so the phase holds
and there is no seam — then re-centre the axis on (960, 540).

**Opacity and blend live in CSS, never in the asset.** Compress by collapsing the 882 identical
gradient definitions to one: ~350KB → ~70KB, zero pixel change. Never scale, rotate or re-tile. Never
behind a table or chart.

#### Dark mode: the emphasis ground

**Node 1892:32, and it is a ground option rather than a recipe.** It composes with any layout
whose type is white. `PAT-09` caps it at **one slide in five and never two in a row.**

```css
--wwt-blue-dark:#1D569E;
--wwt-purple-dark:#28115C;
--grad-dark-diag:linear-gradient(165.47deg,#1D569E 8.95%,#28115C 76.88%);
.g-dark{background:var(--grad-dark-diag);color:#fff}
.mesh--dark{left:-262px;width:2384px;height:1080px;
            background:url(assets/vectors/mesh-dark.svg) 0 0/2384px 1080px}
```

**These are its own colours, not the brand pair darkened.** The brand diagonal runs `#0086EA`
to `#330072` at 164°; this runs `#1D569E` to `#28115C` at 165.47°. Lower chroma and much lower
luminance, which is what lets it carry white type: measured on the render, **6.2:1 at the
lightest corner and 15.9:1 at the darkest**, so it clears AA for normal text everywhere.

**The ground and its mesh ship as a pair.** `.mesh--dark` is node 1892:34: the same 1764-path
lattice as `.mesh--center`, but a **separate export with its own gradient axis**
(1022.28, 938.512 → 1683.67, 394.525 against the centre asset's 677.5, 810.9 → 1265, 247.4).
It is not `mesh--center` stretched and must never be substituted for it. Normalised from
2409 × 1092 at x −265 to **2384 × 1080 at left −262**, bleeding 262 off the left and 202 off
the right. The Figma export carried its own `opacity="0.11"` plus-lighter wrapper and both
were stripped, because opacity and blend live in CSS (REG-04).

Because the pair is the device, `g-dark` satisfies `PAT-08` on its own: do not add a second
background device to it, and `PAT-01` still forbids a Brand X alongside a mesh.

For PPTX the pair is baked to one opaque plate, `ground-dark-mesh.png`, since plus-lighter
over a gradient is doubly impossible in PowerPoint.

#### The mesh is background only

**A `.mesh` is a direct child of `.slide` and nothing else.** Never inside a `.panel`, a `.card`, a
`.media`, a `.statband` or any other container, and never painted onto one as a `background-image`.
This is a hard rule, not a preference, and `PAT-05` fails on both routes in.

Three reasons, in the order they bite:

1. **`plus-lighter` composites against what is behind it.** On the page surface that is `#F6F6F6` and
   the lattice reads at 11%, which is the whole design of the effect. On a panel fill it composites
   against the panel and reads as a texture swatch sitting inside a box.
2. **The container clips it.** The fade is one userSpace gradient in absolute coordinates, so a
   1205 × 1080 field cropped into a 426 × 200 card shows an arbitrary slice of the gradient terminus
   rather than the density run the asset was built for.
3. **It does not survive export.** The PPTX path blends the mesh into a single flat ground plate,
   because PowerPoint has no blend modes (REG-17). A mesh inside a container is not part of the
   ground, so it is dropped on export and nothing reports it.

The mesh is a property of the page, the same way the ground colour is. If a container needs
separating from the surface behind it, that is what `.panel` and its shadow are for.

### Brand X
**One grouped vector, node `1799:46`. Not two copies of one clip-path.**
`2130 × 2595.531 at left 349 / top −920`, normalised to `2108 × 2566 at 345 / −910`.
`assets/vectors/brandx-cover.svg`, placed by `.brandx-x`.

**The two bars are deliberately different weights.** Measured off the paths:

| Bar | Long edge | Thickness |
|---|---|---|
| lower-left to upper-right | 2661.3px | **536.2px** |
| upper-left to lower-right | 2661.3px | **273.3px** |

A 0.51 ratio. Two copies of a single clip-path cannot produce that, which is why the earlier
reconstruction gave 536 and 518 and the X read as two equal bars. **Gradients and opacity are baked
into the asset. Do not add opacity on top** — the 92% / 55% pair in the old form was invented.

The separate 36% black scrim over the cover photograph is node `1659:791`, which is what `.scrim-flat`
already is.

`.brandx` with its clip-path survives for one thing only: recipe 10's cropped wedge, which is a
different shape from a different node.

### Flex triangle
The WWT chevron blown past the frame and gradient-filled. Measured from node `1659:964`:
**1329 × 907 at left −519, top 245**, so the head enters at upper-left and the body fills the lower
corner. The source applies `rotate(180deg) scaleX(-1)`, which is a vertical flip; `.tri--l` does that
and `.tri--r` mirrors it. The gradient is baked into the asset in userSpace coordinates, so it never
needs re-deriving. `assets/vectors/flex-triangle.svg`.

**It is background, not foreground.** It sits under photography. In the PPTX export it is placed
immediately after the ground and before any content; placing it with the other decoration put it on
top of the photo.

### Ring
A percentage read as a ring, from the source component `parts-pie`, node `1138:2700`: **208 outer on a
12.48 stroke**, so r 97.76 and circumference 614.2. The value is a `stroke-dasharray`, which keeps the
number a parameter rather than a redrawn path. Because the value varies, it cannot be one baked asset:
the exporter captures each instance opaquely, since it always sits on a white panel.

### Red arrow
93 × 93, 10px stroke `#EE282A`, round caps. The mark is drawn pointing **up and to the right**.
`.arrow--down{transform:scaleY(-1)}` mirrors it to point **down and to the right**, which is how it
sits on the cover. Rotate in 90deg steps only. One per slide.
Bundled at `assets/vectors/arrow-red.svg`. Inline it as live markup rather than a data URI, or the
CSS mirror has nothing to act on.
`<path d="M5 87.9555L88.0258 5M88.0258 71.3644V5H21.6052"/>`

**Placement on a cover is baseline-relative, not box-relative.** The arrow reads as a piece of
punctuation on the headline's first line, so it sits on that line's baseline with a 10px gap to the
first glyph:

```
arrow.top  = headline box top + baseline offset - 93
arrow.left = headline box left + first-glyph bearing - 10 - 93
```

The stroke's round caps carry ink to the edge of the 93 × 93 box on every side, so the ink box and
the CSS box are the same rectangle. No optical correction is needed.

**Baseline offset** is `(lh × fs - 1.2207 × fs) / 2 + 0.93896 × fs`, from Aptos's 2048upem ascent
1923 and descent -577. At display-1 176/.80 that is **127px**. Browsers round the half-leading, so
measure rather than trust the arithmetic: insert an empty `display:inline-block;height:0` span as
the first child and read its `getBoundingClientRect().bottom`.

**First-glyph bearing is per word, not per style.** At 176px Black, "AI" overhangs its box by 2px
and "MAKE" sits 11px inside it, a 13px swing. The two reference covers therefore place the same
arrow at `left:105` and `left:118` with an identical `top:542`. Re-measure when the headline
changes; do not copy the number from another cover.

---

## 9. Logo

**Full lockup** — 210 × 44 at 44, 52, 22px clearspace. White wordmark on photography, gradient and dark
grounds; `#1F1F1F` on `#F6F6F6` and white.

Artwork is bundled: `assets/vectors/logo-full.svg` is the white lockup, and the ink variant is that
same file recoloured at build time rather than a second file, so the two cannot drift apart.
The bug's mark is `assets/vectors/bug-mark.svg`.

**Cover and closing only.** Verified against the source: Cover 4 and Thank you carry the lockup at
43.46, 51.59. **The divider carries the bug, not the lockup** — it was listed as a lockup slide for two
revisions and that was wrong.

### The bug is one component, and its position is exact

Measured from node `1659:861`, normalised to 1920 × 1080:

| | Figma | Canvas |
|---|---|---|
| Unit | x 1772.198, y 783, 278.001 × 289.099 | **x 1754, y 774, 275 × 286** |
| Mark | x 1829.199, y 1025, 73.776 × 38.300 | **x 1810, y 1013, 73 × 38** |

```css
.bug{position:absolute;right:-109px;bottom:20px;width:275px;height:286px;pointer-events:none}
.bug .stripe{position:absolute;inset:0;background:var(--grad-bug);
             clip-path:polygon(100% 0,100% 50.39%,50.37% 100%,0 100%)}
.bug .mark{position:absolute;left:56px;top:239px;width:73px;height:38px}
.bug--dark .stripe{background:linear-gradient(180deg,rgba(255,255,255,.22),rgba(255,255,255,.09))}
.bug--dark .mark img{filter:brightness(0) invert(1)}
```

The unit **bleeds 109px off the right edge**, **stops 20px above the bottom**, and the mark sits low and
near the corner — 37px from the right, 29px from the bottom. Band thickness 101, not 120.

**Reservation: 136 × 96 at x 1784→1920, y 984→1080.** Content may cross the stripe's upper-left half;
nothing crosses that rectangle. **Every slide except the cover and the closing, including dividers.**

---

## 10. Components

`.nb{white-space:nowrap}` is a utility, not a component: wrap any hyphenated compound that lands near
the end of a measure, because the hyphen is a break opportunity that `&nbsp;` does not close.


| Class | Fixed | Variable |
|---|---|---|
| `.rail` | Bold 22, top 56, right 72, right-aligned | Copy, ink or white |
| `.lockup` | 210 × 44 at 44, 52 | White or ink wordmark |
| `.bug` | 275 × 286 unit at 1754/774, 73 × 38 mark at 1810/1013 | Light or dark stripe |
| `.eyebrow` | Bold 24, .16em, upper | Blue or white |
| `.panel` | 56px pad, `--shadow-panel` | White / `--grad` / `--soft`, any span |
| `.stat` | Black value, Bold label, Regular note | 96 / 64 / 48, optional red direction |
| `.chip` | Black 32, 18/28 pad | Blue-on-white or white-on-blue-93 |
| `.badge` | 96 × 96, Black 48, gradient 93 | Number only |
| `.btn` | Bold 30, 20/34 pad, square | Fill, ghost, ghost-white |
| `.feat` | 18px blue dot, Bold 36 label, Regular 28 copy | Width, count |
| `ul.b` | 14px blue dot, 28px Regular, 22px gap | Width, five items max |
| `.media` | Six crops, composable scrims | Crop, scrim, position |
| `.t-quote` | Serif Bold Italic 64, 200px marks | Width, ground |
| `table.deck` | One gradient across the header row, 56px rows | Columns, six rows max |
| `.device` | Phone 300 × 610 r44, tablet 760 × 520 r26 | Position, screenshot |
| `.medallion` | 249px white disc, two concentric shadows | Position (recipe 14) |
| `.arrow` / `.arrow--down` / `.arrow--connector` | 93 × 93, 10px `#EE282A` | Direction |

**Badge placement.** The sequence badge sits flush in a panel corner with no inset — top-left with the
step name beside it, or **top-right with its right edge on the panel's right edge**. Both are corner
treatments taken from the source; a badge floating outside a panel, or inset a few pixels from its
edge, is not.

Utility classes the validator understands: `.off-grid`, `.scrim-wash`, `.doc-anno`, `.t-source`.

**Specificity traps that have shipped bugs.** `.feat h5` sets a colour and beats `.white`; use an inline
colour on dark grounds. `.on-dark ul.b li` needs `.on-dark` on an **ancestor** of the list, not on the
`<ul>` itself.

---

## 11. Layout slots

| Slot | Spans | Band | Accepts | Count |
|---|---|---|---|---|
| HEAD | 5–8 col | y 156→420 | eyebrow, headline, lede | Exactly 1 |
| HERO | 0, 6, 7 or 12 col | full height, or band y 0→473 | media, device, Brand X | 0 or 1 |
| BODY | 4–7 col | y 420→860 | body, bullets, features | 0–2 |
| PANEL | 4, 6 or 12 col | any, 24px gutters | panels | 0–3 |
| PROOF | 3–4 col each | y 620→900 | stat, chip, table, chart | 0–4 |
| MARK | — | rails | rail, bug, lockup, arrow, mesh | Always |

HEAD is mandatory and singular, **or** satisfied by a display-scale number. Spans sum to 12. PROOF sits
below BODY. Maximum three PANELs. Nothing enters the bug reservation. Empty slots stay empty.

**A comparison is a matrix, not a set of cards.** When the reader's job is to compare N options across
the same attributes, use `table.deck`.

**Seven or eight peer labels** go in a 4-up grid of solid blue boxes with white type.

---

## 12. The twenty recipes

| # | Recipe | Slots | Covers |
|---|---|---|---|
| 01 | Cover | HERO 12 · HEAD · lockup | `1659:788` |
| 02 | Divider | HERO 12 · title band + presenter card · bug | Slide 16:9 - 60 |
| 03 | Statement | PANEL grad 5 · HERO 7 bleeding right · HEAD · MARK | `1839:55` |
| 04 | Executive summary | HERO band · gradient title overhanging PANEL 8 | Executive Summary Light |
| 05 | Two-panel compare | HEAD 8 · PANEL 6+6 | Content: 2 Containers |
| 06 | Hero left + stat pair | HERO 7 · HEAD 5 · PROOF | Content - Hero Image Left |
| 07 | Stat strip | PROOF 1 · HERO inset · PROOF 4 | Slides 56, 59 |
| 08 | Metric hero | HEAD centered · HERO band off-left · PANEL + ring · PROOF column | `1659:961` |
| 09 | Card row | HEAD 8 centered · PANEL 4 × 3 · mesh--center | Slides 47, 55 |
| 10 | Feature list + big card | HEAD 5 · BODY 5 · PANEL 7 | Slide 63 — the density ceiling |
| 11 | Split gradient + card | HERO band · HEAD panel · PANEL · badge in the corner | Slides 48, 49, 51 |
| 12 | Matrix | HEAD 8 · PANEL 12 | Transformational Solutions Update |
| 13 | Chart | HEAD 7 · PANEL 7 · PROOF 4 | The Market Is Recovering |
| 14 | Process | HEAD · gradient rail with medallions · PROOF | We Move Hardware Like Nobody Else |
| 15 | Device | HERO device · HEAD 5 · BODY · CTA | Content + Mockup Left / Right |
| 16 | Quote | HERO 7 · HEAD 5 | Slide 28 |
| 17 | Right flex, stat rows | HEAD 4 · PANEL 8 with 3 rows + band · HERO foot band | `1659:986` |
| 18 | Right flex, no image | HEAD 4 · PANEL 8 with 3 rows + band | `1659:1138` |
| 19 | Photo over band | HEAD 4 · HERO 8 · band 8 | `1659:1170` |
| 20 | Split gradient, two ways in | HEAD panel 5 · HERO 7 · PANEL foot with 2 CTAs | `1659:1191` |

There is **no closing recipe**. One shipped through v3.2 and was removed at v3.3 because the source
templates do not contain it: it had been assembled from a "Thank you" frame that is not a layout in
the set. A deck that needs a closing slide uses recipe 03 or 16 and says something.

### Recipe 02 — Divider, exact geometry

Full-bleed photograph with **no scrim**, and a two-part band low on the frame:

| Element | Canvas |
|---|---|
| Gradient title band | left 360, top 614, **1035 × 346** |
| White presenter card | left 1395, top 614, **525 × 346**, running off the right edge |
| Title, 96px Black white, 85px line | left 423, top 669 |
| Subhead, 36px Bold white | left 433, top 858 |
| Presenter names, 36px Bold ink, 56px line | left 1476, top 678 |
| Duration, 24px Regular, Ink 500 | left 1476, top 858 |

Rail white, bug dark. The two panels butt together with no gutter, and the white one bleeds off the
right edge — that asymmetry is the layout's whole character.

---

## 13. Pre-flight checklist

One headline per slide, three lines max, emphasis on the last two to four words · no widows · margins
at 72px · spans sum to 12 · ink coverage inside the band · 40px minimum under a panel's last line and
under any corner badge · mesh variant matches the placement, and the mesh is a direct child of the
slide · bug on every slide except the cover and closing, its 136 × 96 reservation clear · no two consecutive slides on the same page style unless the second builds on the
first · one accent job, one red mark, one gradient surface, one background device · contrast measured on every type-over-image pairing · charts state their takeaway
and cite a source at 22px · alt text everywhere.

**What does not ship:** the same page style twice in a row with nothing building · four columns of body copy · seven or more table rows · a gradient restarting in
each header cell · a reversed or three-stop gradient · red as fill or type · purple as a flat fill ·
centered body copy outside a gradient panel · caps at 48px and below other than the eyebrow · two
background devices on one slide · a left-justified mesh anywhere but x 0 · **a mesh inside a panel,
card or any other container, or mesh art painted on one as a background-image** · a lockup on a divider ·
content inside the bug reservation · a single word alone on a last line · a second serif.

---

## 13b. Rhythm

**Do not use the same page style twice in a row unless the slides build on one another.**

"Page style" is what a reader perceives as a page: the ground, the headline step, and the census of
structural components. Two slides with the same signature look like the same page whatever their
words say. `SEQ-01` computes it and **fails** on a repeat.

**A build clears it, and the build is inferred from the content rather than declared.** Three signals,
any one of which is enough:

| | Signal |
|---|---|
| B1 | An incrementing sequence numeral on both slides. `01` then `02` |
| B2 | Both eyebrows are the same shape around the same separator, the form of a named set: `Engineering · your org` then `Workforce AI · your functions` |
| B3 | **Removed at v4.0.** A shared headline stem is the signature of pagination, not evidence of a build: "X" followed by "X (cont.)" shares its entire stem, so the rule written to prevent repetition was the rule licensing it. Nine continuation slides shipped under it. A real build the two remaining signals miss declares itself with `data-builds-on="prev"` |

**An identical eyebrow or headline is never a build.** That is duplication, and it fails.

Two exemptions. Covers, dividers and closings reset the run, because a section boundary is not a
repeat. And a **reference document is exempt in full** — the spec book shows seventeen recipes in a
row and a component gallery after them, and consecutive sameness is what a gallery is. Detected by
`section.doc` or `[data-gallery]`.

**Where this stands today.** The AI GTM deck has no repeats. The AI Built for Success deck has three
slides on one layout, AI Native Engineering then Workforce AI then Mission AI, cleared by B2 as a
parallel set and reported as WARN so the judgment stays visible.

**B3 was the known weakness when it was written, and it fired.** The fix was to delete it and add the
declaration, not to widen the signals. Inference that clears the wrong thing is worse than an
attribute.

### SEQ-01 is not enough on its own

SEQ-01 compares **adjacent** slides. A deck can pass it on every pair and still be one page ninety-one
times, which is exactly what happened: 68 of 91 slides put the headline on the identical pixel and
SEQ-01 saw nothing, because a table slide and a two-card slide produce different component censuses
even when they share the ground, the headline step, the headline position and the whole architecture.

Three deck-level rules cover what SEQ-01 structurally cannot:

| | |
|---|---|
| `SEQ-02` | No single architecture on more than 40% of a deck, entropy above 0.72. Architecture is **bucketed** (ground, headline band, headline step, where the photography sits, content form) so a 20px nudge cannot manufacture variety |
| `SEQ-03` | The same slide twice: identical architecture plus 90% of the same words. Deliberately not a pixel hash, which flagged the three AI Native slides, a parallel set carrying different content on the same layout |
| `SEQ-04` | Sparse roles at most 35% of a deck, so relabelling thin content slides as statements does not reach the lower substance bar |

---
