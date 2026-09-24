## 14. Validation layer

Bundled at `scripts/wwt_validate.py`: one Python file driving headless Chromium
(`playwright`, `pillow`, `numpy`).

```
python3 scripts/wwt_validate.py deck.html
python3 scripts/wwt_validate.py deck.html --roles roles.json --json report.json
python3 scripts/wwt_validate.py deck.html --only GEO,MRK --quiet
```

Exit code 1 on any FAIL. `data-role="spec"` marks a documentation specimen where geometry, colour and
mark rules apply but composition rules do not.

### Rules

| ID | Rule | Sev |
|---|---|---|
| GEO-01 | Canvas is 1920 × 1080 | FAIL |
| GEO-02 | Type and panels inside 72px margins | FAIL |
| GEO-03 | Nothing below y 1024 | FAIL |
| GEO-04 | Bug reservation x ≥ 1784, y ≥ 984 clear | FAIL |
| GEO-05 | Panel edges on column boundaries, width a legal span | WARN |
| GEO-06 | Sibling panel gap is 24 ± 4 | WARN |
| GEO-07 | Nothing opaque painted over live type (> 6%, by z-index then DOM order) | FAIL |
| TYP-01 | Every font size is on the ladder | FAIL |
| TYP-02 | Exactly one entry point | FAIL |
| TYP-03 | Headline is three lines or fewer; `t-h1--stmt` capped at a 720px block instead | FAIL |
| TYP-04 | Headline ≤ 1176 wide (display exempt) | WARN |
| TYP-05 | No caps at 48px or below (eyebrow exempt) | FAIL |
| TYP-06 | Display lines do not overflow their box | FAIL |
| TYP-07 | Serif only inside `.t-quote` | FAIL |
| TYP-08 | Body measure ≤ 1026 | WARN |
| TYP-09 | Two live text blocks may not overlap (> 12% of the smaller) | FAIL |
| TYP-10 | No single word alone on the last line | FAIL |
| COL-01 | Every colour resolves to a token | FAIL |
| COL-02 | Red is never type or a fill | FAIL |
| COL-03 | Purple is never a flat fill | FAIL |
| COL-04 | Contrast meets AA for the size, measured off the rendered backdrop | FAIL |
| COL-05 | One gradient surface per slide | WARN |
| COL-06 | One red mark per slide | WARN |
| MRK-01 | **Lockup on cover and closing; bug on everything else including dividers** | FAIL |
| MRK-02 | Never both marks | FAIL |
| MRK-03 | Bug unit 275 × 286 at x 1754, bottom offset 20; mark 73 × 38 at 1810, 1013 | FAIL |
| MRK-04 | Lockup 210 × 44 at 44, 52 | FAIL |
| PAT-01 | Mesh and brandx never on the same slide | FAIL |
| PAT-02 | Mesh at opacity .11, plus-lighter, 1205 / 1920 / 1182 × 1080 | FAIL |
| PAT-03 | No table or chart over the mesh | FAIL |
| PAT-04 | A left-justified mesh actually sits at x 0 | FAIL |
| PAT-05 | Mesh is a direct child of `.slide`, and mesh art is never a background-image on anything else | FAIL |
| PAT-06 | No retired two-div Brand X, and no Brand X that renders 0 × 0 | FAIL |
| PAT-08 | Every light-ground content slide carries a background device; tables and charts excepted | FAIL |
| PAT-09 | Deck: the dark emphasis ground on at most one slide in five, and never two in a row. **A ceiling, not a floor** | FAIL |
| SYS-01 | No deck-local class that duplicates a component the system ships. Declare a genuinely new one with `data-component` | FAIL |
| SYS-02 | No deck-local class using a gradient, clip-path, blend mode, filter, pseudo-element or circular radius: **none of them export** | FAIL |
| MRK-05 | The bug variant matches the **measured** backdrop behind it, not the ground class | FAIL |
| GEO-08 | Text is not flush against a panel edge | FAIL under 12px, WARN under 24 |
| DEN-09 | No content panel more than 35% empty below its last content | FAIL |
| COL-08 | No brand-gradient device on a brand-gradient surface | FAIL |
| TYP-12 | One body step per job across a deck: body copy and card interiors counted separately | FAIL over 2 sizes |
| DEN-06 | Coverage inside the role band, **read in both directions**. An empty panel is ground | FAIL under the floor, WARN when thin |
| DEN-07 | Content atoms and words. Fails only when **both** are thin, so a terse table passes and an empty slide does not. The word floor eases on a slide carrying real photography | FAIL |
| DEN-08 | No placeholder copy: lorem ipsum, TBD, "[insert" | FAIL |
| COL-07 | No `g-white` on a content slide, and no panel on a white ground | FAIL |
| GEO-06 | A side-by-side set bottoms out together, within 8px | FAIL |
| TYP-11 | A centred headline centres on 960 unless declared `off-grid` | FAIL |
| IMG-05 | Deck: 30% of slides carry photography, 40% is the target. A slide counts when its imagery SUMS to 15% of the canvas | FAIL |
| IMG-06 | Deck: never more than 6 consecutive slides without one | FAIL |
| IMG-10 | A band in the top or bottom zone bleeds to that edge and both sides | FAIL |
| SEQ-02 | Deck: no architecture on more than 40% of slides, entropy above 0.72 | FAIL |
| SEQ-03 | Deck: the same slide twice, by architecture plus 90% shared words | FAIL |
| SEQ-04 | Deck: sparse roles at most 35% of slides | FAIL |
| SEQ-05 | No "(cont.)" headline anywhere | FAIL |
| SEQ-06 | Deck over 40 slides fails, over 30 warns | FAIL |
| GAL-01 | A reference-gallery claim is substantiated, or withdrawn and the file judged as a deck | FAIL |
| DEN-01 | Ink coverage inside the band for the role | WARN |
| DEN-03 | Six table rows maximum | FAIL |
| DEN-04 | Five bullets maximum per list | FAIL |
| DEN-05 | Table rows ≥ 56px | WARN |
| A11-01 | Every image has alt text, or alt="" plus aria-hidden | FAIL |
| A11-02 | Charts carry `role="img"` and `aria-label` | FAIL |
| A11-03 | Data slides cite a source | WARN |
| A11-04 | Reading order matches visual order | WARN |
| IMG-01 | Photography resolves to a library ID | WARN |
| IMG-02 | Crop is one of the six | WARN |
| IMG-03 | Type over unscrimmed media | FAIL |
| IMG-04 | Measured scrim clears AA | FAIL |
| IMG-07 | No photograph twice on one slide | FAIL |
| IMG-08 | No photograph on two slides in a deck no longer than the library | FAIL |
| MAP-01 | Every recipe in a gallery appears in its source map, and every mapped recipe appears in the gallery | FAIL |
| SEQ-01 | No two consecutive slides share a page style unless the second builds on the first | FAIL |
| TYP-00 | Every type element carries a ladder token; no ad-hoc font-size | FAIL |

Produced by `scripts/verify_pptx.py`, on the artefact that actually ships. These are the
rules that inspect the PPTX rather than the HTML, and they exist because a 91-slide deck of
flattened screenshots passed everything above.

| Rule | What it checks | Severity |
|---|---|---|
| PPT-01 | Canvas is 12192000 × 6858000 EMU, PowerPoint widescreen | FAIL |
| TXT-01 | The file contains live text at all | FAIL |
| TXT-02 | Every slide whose HTML source carries text has text in the PPTX | FAIL |
| TXT-03 | No slide is a single full-bleed picture and nothing else | FAIL |
| FNT-01 | Fonts are embedded AND the package is shaped so a reader will use them: content type, `embedTrueTypeFonts`, sequence position, one relationship per slot, and each part's name table matches its declared typeface | FAIL |
| FNT-02 | Every run names a face in the Aptos family map | FAIL |
| ZOR-01 | Decoration behind the text in the HTML is behind it in the PPTX | FAIL |
| FIL-01 | Every gradient-filled element keeps its fill | FAIL |
| PIC-01 | Baked decoration is the variant the source declares, matched by file hash | FAIL |
| PRB-01 | The three rules above could actually run. They need Playwright, and a run where the probe died used to print a note and then `0 FAIL` | FAIL |

### Packaging

A skill package is capped at **200 files**. Run `scripts/check_package.py` before shipping.

| Rule | What it checks | Severity |
|---|---|---|
| PKG-01 | The file count is inside the platform limit, and warns at 85% of it | FAIL |
| PKG-02 | No caches or OS junk in the package | FAIL |
| PKG-03 | `SKILL.md` is at the package root | FAIL |

### The two reference documents

There are two, they are kept, and each does a job the other cannot. The teardown is for
**looking at** the system: every token as a live specimen, the icon set, the voice rules, the
measured contrast ratios, the gaps. 600 KB, standard library only, so it opens on a machine
where Chromium will not install. The spec book is for **copying geometry out of**: twenty
recipes at full size with their real numbers, the component gallery, the background patterns.
17 MB, needs a browser to build.

Keeping both costs one thing, which is that they can disagree, and they already had. Run
`scripts/check_documents.py SPEC.html TEARDOWN.html`; `build.py` runs it automatically because
building one without the other is how the gap opened.

| Rule | What it checks | Severity |
|---|---|---|
| DOC-01 | A stated `#fg #bg N.NN` ratio is true of its own two colours | FAIL |
| DOC-02 | A stated type size matches `assets/system.css` | FAIL |
| DOC-03 | Where both documents state the same fact, they state the same value | FAIL |
| DOC-04 | Each document says which of the two jobs it is for | FAIL |

### Icons

Lint-only, and deliberately so. After inlining, an icon is raw SVG markup and the name it was
chosen by is gone, so the placeholder is the only place these claims are checkable. They cost
milliseconds and run on every write.

| Rule | What it checks | Severity |
|---|---|---|
| ICO-01 | The mark resolves to a key in `assets/icons/manifest.json` | FAIL |
| ICO-02 | A branded mark carries a written reason in `data-why` | WARN |
| ICO-03 | Every `.ico` declares `aria-label` or `aria-hidden="true"` (WCAG 1.1.1) | FAIL |
| ICO-04 | The size is on the ladder: 24, 32, 48, 64, 96 | FAIL |
| ICO-05 | A multi-colour mark is not placed on the dark emphasis ground | FAIL |

### How the hard measurements work

- **Force every stage to native 1920 width before measuring.** A plate sampled at a third scale blends
  neighbouring rows into the reading and invents contrast failures.
- **Contrast is sampled, not inferred.** Strip glyph colour while leaving every painted box intact,
  screenshot, then read the backdrop behind each text run. 90th percentile for light type, 10th for
  dark. Inset the sample by 12% so the element's own border is not mistaken for its backdrop.
- **Widows are measured across the element's whole text flow**, so an `<em>` inside a headline counts
  as part of the same run.
- **Ink coverage is a union** on a 192 × 108 grid, ±1%. Photography touching two or more canvas edges
  is skipped as ground.
- **Occlusion respects paint order**: an element covers type only if `(z-index, document order)` is
  greater and the type is not a descendant.

### What it deliberately does not check

Whether the story works. Whether the photo is the right photo. The squint test. Whether a rule should
be broken — WARN exists so a designer can override with a recorded reason; FAIL does not have that
door.

---

## 17. PPTX export

**Run the script. Do not reproduce the technique.**

```
python3 scripts/export_pptx.py WWT-Deck.html -o WWT-Deck.pptx
```

The canvas maps exactly, which is why this is possible at all. 1920 × 1080 at 144 DPI is
13.333 × 7.5 inches, PowerPoint's own widescreen size:

| | |
|---|---|
| 1 px | **6350 EMU** exactly (914400 / 144) |
| 1 px | **0.5 pt** exactly (72 / 144) |

So a 96px headline is 48pt and a 24px body is 12pt. No rounding anywhere.

### What cannot cross, and what stands in for it

PowerPoint has no CSS. Four features in this system have no equivalent, and every one of them is
pre-rendered into `assets/export/` by `bake_export_assets.py`. **Run that script for the current
list rather than trusting this table**; it printed the count and this table disagreed with its own
row count for several revisions, and it was missing `brandx-r10.png`, the one asset whose absence
put a dark wedge across a light slide under all of its text.

| CSS | Where | Replaced by |
|---|---|---|
| `clip-path` | Brand X wedges, the bug's stripe | `brandx-cover.png`, `brandx-r10.png`, `bug-light.png`, `bug-dark.png` |
| `mix-blend-mode:plus-lighter` | the diamond mesh | baked into `ground-light-mesh-*.png`, `ground-dark-mesh.png` |
| `filter:brightness(0) invert(1)` | the bug's mark on dark | already the right colour in `bug-dark.png` |
| inline SVG + `transform` | lockup, red arrow, flex triangles | `lockup-white.png`, `lockup-ink.png`, `arrow-up.png`, `arrow-down.png`, `tri-left.png`, `tri-right.png` |

**Every variant needs its own plate, matched by variant and not by selector.** The exporter once
matched `.brandx-x, .brandx` and painted the cover's wedge pair for either, so a light content slide
got the cover's dark artwork stretched across it under all of its text. `PIC-01` in
`verify_pptx.py` now hashes these files and fails when the plate on a slide is not the plate the
source's own classes call for.

**Gradients are native, not baked.** DrawingML has a real linear gradient, so `.g-grad-diag`,
`.g-grad` and every `.panel--grad` export as an editable `<a:gradFill>` carrying your exact stops.
Two conversions do all of it:

| | |
|---|---|
| stops | CSS percent × 1000 is the DrawingML position. `8%` → `pos="8000"`. Both formats hold the end colour past the last stop, so the flat runs match |
| angle | CSS is clockwise from *to top*; DrawingML is clockwise from +x in 60000ths of a degree. **`ang = (cssDeg − 90) mod 360 × 60000`** |

So `linear-gradient(164deg,#0086EA 8%,#330072 63%)` becomes `ang="4440000"`. Sanity checks: CSS 180
(top to bottom) → 90°, CSS 90 (left to right) → 0°.

**Shadows are native too.** `--shadow-panel` maps to `<a:outerShdw>`:

| CSS | DrawingML |
|---|---|
| offset `0 1px` | `dist` = hypot(dx,dy) in EMU, `dir` = atan2(dy,dx) clockwise from +x × 60000 |
| blur `25px` + spread `7px` | `blurRad` = (blur + spread) × 6350 |
| `rgba(0,0,0,.10)` | `srgbClr` + `<a:alpha val="10000"/>` |

**Spread is the one real loss.** CSS expands the shadow shape by the spread before blurring;
DrawingML can only blur. Folding spread into blur is the closest honest approximation and errs soft
rather than tight. Set `shadow.inherit = False` first to drop PowerPoint's dated preset, then write
the real one, or you get both.

**Native gradients are used only at axis-aligned angles: 0, 90, 180, 270.** Everything else falls
back to its baked plate. PowerPoint and LibreOffice disagree about `<a:lin scaled="0">` off-axis:
LibreOffice honours the true geometric angle and matches CSS to within 3 channel levels, while
PowerPoint renormalises and the visible range collapses toward the first stop, so the 164° ground
arrives as light blue to blue with no purple in it at all. A vertical or horizontal gradient is
immune, because vertical is vertical under either reading. That keeps `.panel--grad` editable, which
is where editability actually matters, and keeps the ground exact.

Everything else survives as native PowerPoint: text boxes, rectangles, rules, photographs cropped to
match `object-fit:cover`, and the partner logos. **The type stays live and editable.** That is the
whole point of placing pictures for the decoration rather than exporting the slide as one image.

### Fonts

**PPTX has no font-weight, only a binary bold flag.** `typeface="Aptos"` with `b="1"` resolves to
Aptos **Bold (700)**, and there is no way to ask for 900. Aptos ships its heavy cuts as separate
families, so the weight must be carried in the typeface name:

| CSS weight | PPTX typeface | bold |
|---|---|---|
| 400 | `Aptos` | no |
| 600 | `Aptos SemiBold` | no |
| 700 | `Aptos` | **yes** |
| 800 | `Aptos ExtraBold` | no |
| 900 | `Aptos Black` | no |

This is REG-01 one layer down: the `@font-face` map solves it in HTML, naming the family solves it in
PPTX, and getting it wrong is invisible because Bold and Black differ by only 4.4% in width.
**Verify by measuring, not looking:** "INVESTMENT IS UP." at 96px sets 767px in Black and 735px in
Bold.

**The export embeds the fonts** it finds on the machine (TTF only; see section 3). All Aptos cuts,
including the ones Office installs, are `fsType 0x0008`, Editable Embedding, which is
precisely the permission document embedding needs. `export_pptx.py` writes only the faces the deck
actually uses, full rather than subset, because the point of this path is editable text and a subset
breaks the moment someone types a glyph outside it. A seven-slide deck uses three faces and gains
about 320KB. Pass `--no-embed` to skip it.

```
ppt/fonts/fontN.fntdata                  raw TTF
[Content_Types].xml                      Default Extension="fntdata"
ppt/presentation.xml  <p:embeddedFontLst><p:embeddedFont>
                        <p:font typeface="Aptos Black"/><p:regular r:id="..."/>
```

Two sequences to respect. `<p:embeddedFontLst>` sits after `<p:notesSz>` and before
`<p:defaultTextStyle>`. Inside each `<p:embeddedFont>` the slots run **regular, bold, italic,
boldItalic** — sorting them alphabetically puts bold first and the schema rejects the file.

**Embedding does not remove the need for the font.** PowerPoint for Mac has not reliably supported
embedded fonts, so treat this as belt-and-braces for Windows recipients rather than a guarantee. When
a deck must look identical everywhere, send PDF.

PowerPoint cannot read WOFF2, so the export embeds TTFs. A face the deck uses and the machine lacks
is reported by name when the export runs, and `verify_pptx.py` FNT-01 fails the deck. Without Aptos
present on the opening machine the type reflows: in testing,
the eyebrow wrapped through the headline and three layer labels broke mid-word. Nothing else changed,
which is a useful signal — if the artwork is right and only the text is wrong, it is the font.

---
