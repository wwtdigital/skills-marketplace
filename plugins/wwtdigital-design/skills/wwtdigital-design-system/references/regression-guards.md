## 16. Regression guards

Every item below is a defect this system actually shipped, rewritten as something you can check.
They are ordered by how silently they fail. **Run REG-01 through REG-05 before trusting any output;
they are the ones that produce confident, wrong work.**

### REG-01 · The face must be real before any width is measured
Aptos ships its heavy cuts as separate families. `font-family:'Aptos';font-weight:900` finds no 900
face and the browser fakes one from Bold, so headlines render light and every advance width is wrong.
Widows, headline measure and ink coverage all read fiction.
**Verify:** `document.fonts.check('900 96px Aptos')` returns `true` in the rendered page. If it is
false, stop. Do not record a single measurement.

### REG-02 · Measure at native 1920, never through a transform
A stage sampled at a third scale blends neighbouring rows and invents contrast failures.
**Verify:** every `.stage` forced to `transform:none;width:1920px;height:1080px` before sampling, and
colour sampled with a 12% inset so an element's own border is not read as its backdrop.

### REG-03 · Geometry comes from the node, never from the render
The bug was reconstructed by eye and was wrong on every axis for three revisions. The divider was
built from a thumbnail and was wrong in kind, a scrimmed photo instead of a two-part band.
**Verify:** any recipe you did not personally measure gets its node re-pulled and normalised
(sx 0.989487, sy 0.988649) before you touch it. The bug is 275 × 286 at 1754 / 774, bleeding 109 right,
stopping 20 above the bottom, band 101, mark 73 × 38 at 1810 / 1013, centred at 47% across the band.

### REG-04 · The mesh variant is chosen by placement, not by which file you were handed
The fade is baked into one userSpace gradient in absolute coordinates, so exporting the same node from
a different position returns a byte-identical file. Three "different" uploads were the same bytes.
**Verify:** `.mesh--diag` is at `left:0`. It was right-anchored for two revisions and nothing caught it.
`.mesh--center` uses the extended asset, 14 lattice periods (749.389px), never a scaled `--diag`.
Opacity and blend live in CSS; applying `.11` on top of an asset that already carries `.11` reads as a
match when it is not.

### REG-05 · A hyphen is a break opportunity that `&nbsp;` does not close
A hyphenated compound splits at its own hyphen and strands the tail. Aptos has no U+2011, so a
non-breaking hyphen is not available.
**Verify:** hyphenated compounds near the end of a measure are wrapped in `.nb`, not bound with
`&nbsp;`.

### REG-06 · One `::after` per element, so scrims must compose
Two scrim classes that both own `::after` silently cancel. Adding `.scrim-t` once deleted `.scrim-r`
and dropped a headline to 1.87:1 with no warning.
**Verify:** scrims set `--scrim-1` / `--scrim-2` and share one pseudo-element.

### REG-07 · Contrast is sampled, not inferred
`.on-dark` on the `<ul>` instead of an ancestor left bullets at 1.27:1. `.feat h5` beat `.white` and
put headings at 1.16:1 on a photograph. Both looked correct in the markup.
**Verify:** every type-over-image and type-over-gradient pairing has a measured ratio, read from the
rendered backdrop at the 90th percentile for light type and the 10th for dark.

### REG-08 · A variant class ties with its base and loses on source order
`.brandx--r10` never applied. Equal specificity, later rule won.
**Verify:** variants are written `.brandx.brandx--r10`, and set `clip-path:none` when replacing a shape.

### REG-09 · A cropped wedge must be calibrated to the source render
The exported Subtract did not reproduce the silhouette once the canvas clipped it.
**Verify:** any shape the canvas crops is checked against the Figma render, not against its own export.

### REG-10 · Optical placement is per word, not per style
At 176px Black, "AI" overhangs its box by 2px and "MAKE" sits 11px inside it. A 13px swing on one type
style.
**Verify:** the cover arrow's `left` is recomputed from the actual first glyph. Never copied from
another cover. Baseline offset is measured with a zero-height inline-block probe, not from arithmetic.

### REG-11 · Photography resolution is checked against the crop, not assumed
The crop list promised resolution three source frames never had.
**Verify:** `assets/manifest.json` `px` covers the largest crop the frame is listed for. `pair-laptop`,
`team-desks` and `atc-lobby` do not, and carry ⚠ in section 7.

### REG-12 · Composite an alpha PNG onto white before flattening
`.convert('RGB')` on an RGBA source flattens transparency to black.

### REG-13 · Never rebuild a source file with an open-ended replace
`d.replace(d[d.index(x):], new)` truncated a thirteen-slide file to 2958 bytes.
**Verify:** edits are anchored on both sides, and the file's line count is checked after writing.

### REG-14 · The renderer's system libraries are not guaranteed
Headless Chromium fails to launch on a fresh sandbox with `libXdamage.so.1: cannot open shared object
file`.
**Verify:** launch the browser once before starting work rather than discovering it mid-validation.

### REG-15 · A fixed slide inside a fluid stage must be scaled, or it crops silently
Every `.slide` is a fixed 1920 × 1080 box scaled into its `.stage` by the `--k` custom property. If
nothing sets `--k` it stays at 1, the slide overflows a narrower stage, and `overflow:hidden` removes
the right and bottom of every page. No error, no warning, and the HTML is valid.
**The validator cannot see this.** It forces every stage to `transform:none;width:1920px` before
measuring, which is precisely the condition that hides the fault. A screenshot harness that does the
same thing will also report the deck as clean.
**Verify:** open the built file at a browser width below 1920 and read `--k` off a `.stage`. It should
be `clientWidth / 1920`, not 1. `inline_assets.py` now injects the script whenever it sees a `.stage`
and no scaler, so this only recurs if someone passes `--no-fit`.

### REG-16 · Intentional bleeds are not overflow
Four things are meant to leave the canvas: the two Brand X wedges, `.mesh--h` (32px right, 8px up),
and the bug with its stripe (109px right). An overflow audit that flags them is reading the system
correctly and the report wrongly. **Only a text or content element outside 1920 × 1080 is a defect.**

### REG-22 · An embed that fails, fails silently
A malformed or ignored `<p:embeddedFontLst>` looks perfect on any machine that has the font
installed, which is every machine you will test on. **Verify by removing the font, not by opening the
file.** Rename the Aptos family out of the system font folder, open the deck, and see whether the
type holds. Also check `ppt/fonts/fontN.fntdata` begins `00 01 00 00` — raw TrueType, not Word's
obfuscated `.odttf`.

### REG-21 · A binary bold flag cannot carry a five-weight ladder
`f.bold = weight >= 600` collapses 600, 700, 800 and 900 onto one face. Every headline in the deck
exported as Aptos Bold while the file claimed Aptos Black, and nothing warned about it because the
two differ by 4.4% in set width. **Carry the weight in the typeface name, not the bold flag.**
**Verify:** measure a known string against both faces rather than judging by eye.

### REG-19 · `spPr` is a sequence, and PowerPoint enforces it
ECMA-376 `CT_ShapeProperties` is an ordered sequence: **xfrm, geometry, fill, ln, effectLst.**
Appending a fill element and then moving `<a:ln>` to the end produced
`xfrm, prstGeom, effectLst, gradFill, ln`. LibreOffice renders that happily. PowerPoint repairs the
file by **discarding the out-of-order fill** and falling back to `<p:style>`'s theme accent, so a
blue-to-purple gradient arrives as a plausible flat blue.
**Verify:** dump the `spPr` child order and check it against the sequence above. Let python-pptx
place fills via `fill.gradient()` / `fill.solid()` and effects via `get_or_add_effectLst()`; never
append them by hand.
**Also strip `<p:style>`** from any shape given an explicit fill. It exists only as a fallback, and a
fallback that looks plausible is worse than no fill at all. Same reasoning as `font-synthesis:none`.

### REG-20 · Verify the export in the tool that opens it
The export was checked against LibreOffice, passed at fifteen sample points, and still shipped a
ground with no purple in it, because LibreOffice tolerates malformed ordering and PowerPoint does
not. **A renderer that agrees with you is not a verification.** Anything that cannot be opened in
PowerPoint here is unverified, and should be described that way rather than reported as correct.

### REG-18 · A CSS gradient is a background-image, not a background-color
`.panel--grad` sets `background: var(--grad-brand-v)`. An export that reads only
`backgroundColor` sees `transparent`, drops the panel entirely, and leaves its white type on the
light ground at about 1.1:1. The slide still looks structurally fine, which is why it survived a
review pass.
**Verify:** the probe reads `backgroundImage` as well as `backgroundColor`, and every `.panel--grad`
appears in the export with a `<a:gradFill>`.

### REG-17 · Never rebuild a baked device as a PPTX shape
The crossed bars, the corner bug and the diamond mesh are `clip-path`, `clip-path` and
`mix-blend-mode`. An exporter that tries to reproduce them as freeform shapes produces exactly the
three failures this system was reported for: bars that fill the slide or vanish, a corner device with
the wrong fill, and no mesh at all.
**Verify:** the export places `assets/export/*.png`. If any code path constructs a polygon for these,
it is wrong regardless of how close it looks.

### REG-25 · A grouped vector is one asset, not a repeated shape
The cover X is one group of two paths whose bars are 536.2px and 273.3px. It was rebuilt as two divs
sharing a clip-path at two different heights, which produced 536 and 518 — the ratio wrong by a
factor of two, and the thin bar 90% too heavy. Nothing caught it because both bars were plausible.
**Verify:** when the source hands you a group, ship the group. If two parts of a mark differ, measure
each part's thickness perpendicular to its own axis rather than assuming one shape scaled twice.
This is the third instance of the same failure: the bug, the divider, and now the X.

### REG-35 · Paint order comes from the DOM, not from a list of class names
The exporter hardcoded which devices were background and which were foreground, so the Brand
X was placed after all the text on EVERY cover and painted over the headline. It is
semi-transparent, the type showed through darkened, and it read as a design choice. It
shipped in v3.x and v4.x and a tester found it by eye, not a rule.
A first attempt at the fix moved the X behind the photograph, because a bg/fg flag cannot
express that a cover has THREE z-bands: the flex triangle under the photo, the X over the
photo and under the headline, the lockup over everything.
**Verify:** every device and every item carries its DOM order and they are placed in one
sorted pass. `ZOR-01` in `verify_pptx.py` compares the HTML's decoration-versus-text order
against the PPTX's shape order and fails on a mismatch.

### REG-36 · A component under a new name is invisible to everything
A test deck invented ten classes, six of which duplicated a component the system already
ships: `.badge-num` for `.badge`, `.pill` for `.chip`, `.case-card` for `.panel`,
`.phase-col` for `.medallion`, and three type roles for `.t-label` and `.t-body-s`. Every one
looked right in the browser. The damage landed elsewhere: the badges lost their gradient on
export and became white boxes, the timeline's circles never existed because `.phase-col` has
no ring, `.svc-col`'s bullet dots were `::before` pseudo-elements that cannot export, and the
three invented type roles are why the body size wandered across four steps on adjacent pages.
Nothing objected, because every rule asked "is this element correct" and none asked "is this
element the one the system already has".
**Verify:** `SYS-01` matches deck-local classes against the measurements that DEFINE each
shipped component, so a rename cannot hide. `SYS-02` fails any deck-local class using a
feature the PPTX path cannot express. A deck may still add a component with a real job: it
declares itself with `data-component`, the same way an off-grid element declares its
exception. An undeclared escape hatch would just be loosening the rule.

### REG-37 · Craft defects need craft rules, and they are not gameable by absence
Six defects were reported on a deck that returned **zero failures**: text flush to a panel
edge, the wrong bug variant twice, 43% of a gradient panel empty, a brand rule invisible on
a brand panel, body copy at four sizes, and badges that lost their gradient on export. None
of them is a density or coverage problem, which is what the deck-level rules added last
revision were built for. They are craft, one element at a time.
Note the doctrine difference: REG-30's "price absence" applies to PRESENCE rules, which are
gamed by doing nothing. These are CORRECTNESS rules, which cannot be gamed by absence, so
they need no paired substance test. They need calibration against real decks instead, and
three of the seven were wrong on the first cut and caught by our own documents.

### REG-38 · An exemption is a rule, and nobody had written it
Every rule in this set was calibrated against real work. The exemptions were not. `isGallery`
was one line of probe code, true if the file carried `section.doc` or `data-gallery`, and it
switched off the entire deck-level family in one move: density, substance, photography share,
mesh share, the background-device rule, deck length, role share, consecutive sameness. One
attribute, thirty rules off, and no test of whether the claim was true. The whole rule set had
a back door and it was cheaper to use than any of the gaming moves `selftest.py` was built to
catch. Audit the escape hatches with the same suspicion as the rules: ask of every exemption
what stops an ordinary deck from claiming it.

(Filed as REG-35 for a revision, which was already taken. An id is a name and two things cannot share one; the same collision hid a whole rule family in the table, see REG-40.)

**Verify:** `GAL-01` measures document furniture outside the slides, with scripts and
stylesheets stripped, and requires 300 words of prose, three headings and one table or list.
Our two reference documents clear it by an order of magnitude (9,926 / 83 / 35 and 1,175 / 21 / 1)
and our four decks score 0 to 2 headings. A failed claim is withdrawn rather than reported, so
the file is judged as the deck it is, and the `gallery_claim` fixture proves it.

Two earlier cuts of this rule were wrong. The first counted prose alone and scored a worked-example
deck at 981 words, because a detached clone has no layout and `innerText` silently becomes
`textContent`, so the page's own fit script read as prose. The second demanded a caption per
specimen and failed the spec book at 26 of 44, because its component specimens are explained
by the section around them rather than one at a time.

The audit found three more doors and closed two. `data-role="spec"` dropped a slide out of the
deck census and off the type and colour rules, so labelling a whole deck with it took the census
under four and `validate_deck` returned before it ran anything: a specimen is honoured inside an
adjudicated gallery now and read as ordinary content anywhere else. `data-builds-on` cleared the
page-style repeat rule on trust, so it now has to be true of the markup, which means the headline
changed and the slide did not lose content. Both are in `selftest.py` as `spec_role` and
`false_build`.

**The one still open is `off-grid`,** and it is open on purpose. It excuses an element from the
margin and centring rules on the claim that the Figma node genuinely sits off the grid, which is a
fact about the source that nothing in the validator can see. Twelve of the twenty recipes carry it,
so it is ordinary system vocabulary rather than an escape hatch, and a deck-level ceiling on it
would fail correct work built straight from the recipes. It is named here so the next person knows
it is unchecked rather than checked and passing.

### REG-34 · A ceiling is not a floor with the sign flipped
Every presence rule in this system pushes toward using the library: photography floors, a
device on every light ground, coverage and substance minimums. `PAT-09` is the first rule that
pushes the other way, and the reasoning does not transfer. A floor is satisfied by adding one
qualifying thing, so it needs a substance test beside it. A ceiling is satisfied by restraint,
so it needs no substance test at all, but it does need a **run check**: a deck can sit inside
the share and still put both its emphasis pages side by side, where neither is emphatic
against anything.
**Verify:** `PAT-09` tests the share AND consecutive placement, `max(1, n × 0.2)` so a short
deck is not denied its one emphasis page by rounding, and two fixtures in `selftest.py`
(`dark_overuse`, `dark_run`) prove both halves fire. When adding a ceiling later, ask what the
equivalent of "two in a row" is for it.

### REG-30 · Absence has to cost something, or absence wins
The rule set priced every device on its risk and priced using nothing at zero. Every statement about
the mesh was a restriction (opacity, blend, four box sizes, x 0, not behind data, not in a container,
not with a Brand X, not two devices) and not one said it should be there. Photography carried a crop
list, a mandatory scrim, a measured contrast ratio and resolution warnings. So the safest composition
under the validator was a white page with a headline and a paragraph, which cannot fail IMG-02,
IMG-03, IMG-04, PAT-02, PAT-04 or PAT-05. A designer told to fix every FAIL converged on it.
**Verify:** every presence rule has a paired substance test, and `scripts/selftest.py` proves each
gaming move fails while the negative control stays clean. **Any rule added later must satisfy one
test: the cheapest way to pass it is the right thing to do.**

### REG-31 · Read a band in both directions
`INK_BAND` carried `lo`, `hi` and `floor` per role. `DEN-01` tested `ink > floor` and nothing tested
`lo`, so a deck averaging 8% coverage passed in silence while 52 near-empty slides went to a client.
Half a rule reads as a whole rule in a report that says 0 FAIL.
**Verify:** DEN-06 tests both ends. When adding a band, write both tests before writing either.

### REG-32 · A summary of a file is not the file
Section 12 represents the twenty recipes as a table of slot names. It named a mesh on 1 of 20 rows
when 10 recipes carry one, and it says nothing about alignment at all. Readers built from the table
and invented the geometry: a 1776 box at `left:0`, panels off the column grid, no background device.
**Verify:** the recipes ship as `assets/recipes.html` and the stylesheet as `assets/system.css`. When
the skill describes something it does not ship, the reader reconstructs it, and reconstruction is
where the defects come from.

### REG-39 · Show the system, do not describe it
REG-32 said a summary of a file is not the file, and the fix was to ship the files. That was half
the answer. Shipping `system.css` and `recipes.html` means the values are all present and correct,
and **nobody reads a stylesheet to learn a design system.** Two decks came back wrong afterwards,
and neither failed on a value being unavailable. They failed on a builder never having seen what
the system looks like: 91 pages of one layout with no photography and no device, then a deck with
the wrong bug in two corners, body copy over three size steps and a gradient device invented inside
a gradient panel. This document was 9,900 words by then and both builders had it open.

A hex string in a table is not a colour. A row reading `t-body | 26px | 400` is not a size. They are
descriptions of things, and a description is what a reader skims on the way to the part they think
they need. The Forward Deployed Unit tester dismissed 39 warnings in one pass, which is what
skimming looks like from the outside.

**Verify:** `scripts/teardown.py` renders every token as a specimen on one page: swatches painted in
the colour with their measured ratio, the ladder set at true size in the real Aptos cuts, shadows on
cards wearing them, radii as corners, the mesh as the actual vector at its actual opacity. It reads
in two minutes and it is step 0b of the order of work, before the plan. Its values come from
`assets/tokens.json` and its prose from `assets/teardown.json`, so it cannot drift from the
stylesheet, and `GEN-01` fails a stale export. When you add a component or a token, the page picks it
up on the next render; if it does not appear, it is not in the tokens, which is its own finding.

**And the page names the gaps.** The things this system does not have are listed as absences: no
positioning work, no motion, and one unchecked exemption. Every one of them would have been easy to
fill with something plausible, and a plausible invention in a reference document is worse than a
blank, because the next person cites it. Iconography sat on that list from v4.5 until v4.10, when a
real library arrived to fill it. Naming the gap is what made it fillable: the entry said "three icon
PNGs on one recipe is not an icon system", which is precisely the brief that got answered.

### REG-47 · An element nobody decided on becomes an element everybody uses
`.rule-h--brand`, a 240 x 6 horizontal brand gradient, was never intended as a component.
It entered the stylesheet, and from there it spread on its own: into the component gallery
with its own annotation describing what it was for, into recipe 10, into both reference
decks, and into three test decks. On one of those it was placed inside a gradient panel,
where a brand gradient cannot read against a brand gradient, and `COL-08` had to be written
to catch it. A rule was built to police an element that should not have existed.

Nothing in the system distinguished "measured from a Figma node and deliberately specified"
from "present in the CSS". Once a class exists, the documentation documents it, the recipes
use it, and the validator defends it. Provenance is what separates the two, and
`provenance.json` covers recipes and components while a bare utility class had no entry at
all.

**Verify:** it is removed from `system.css`, `classes.json`, the component gallery, recipe
10, and both reference decks, in one change, per REG-27. Recipe 10's label margin went from
16 to 40 so the caption below it did not move. `lint_source.py` fails any reference through
`RETIRED`, with a per-class reason, because the first cut of that check printed the Brand X
message for every retired class and reported a brand-rule reference as a missing Brand X.
The three references in `wwt_validate.py` stay on purpose: a deck built before the removal
still carries the class, and `COL-08` still has to catch it there.

### REG-48 · A pseudo-element is not a DOM node, and the exporter only ever walked the DOM
Three components carry real content in a `::before` or `::after`: the bullet dot on `ul.b li`
and `.feat`, and the photo scrim on `.media`, all `content:""` with a painted background.
`export_pptx.py`'s probe walks `slide.querySelectorAll('*')`, which cannot return a
pseudo-element under any circumstances, because it is not a node. Nothing in that walk ever
saw these three rules, so nothing ever painted them, and nothing ever objected: `wwt_validate.py`
has no rule that reads generated content either, so a deck built clean and exported with every
bullet list missing its markers and every scrimmed photo back at full brightness. Measured on
this system's own cover: dropping the 36% scrim raised the photo's rendered luminance by about
20 points against the HTML render of the same file, over a fifth of the visible range, on the
one slide built to prove text stays legible over a photograph.

Fixing the visibility exposed a second, harder mistake. A scrim is drawn as
`background:var(--scrim-1,none),var(--scrim-2,none)`, two layers, so its resolved
`backgroundImage` is `"linear-gradient(...), none"` and not one bare gradient function. The
existing gradient path takes the whole string on the assumption that a background-image is
one layer, which is true of every panel gradient in the system and false of every scrim. Fed
the two-layer string, `parse_gradient`'s end-anchored regex did not match, `apply_gradient`
returned false, and the box fell back to a solid fill read from `backgroundColor` -- transparent
black on every scrim, because the color lives in the image layer, not the color property.
`sh.fill.solid()` has no alpha channel, so "transparent black" became opaque black: the first
attempt at this fix replaced a missing scrim with a fully blacked-out photo, which is a louder
defect than the one it fixed. A parenthesis-depth scan for the first `linear-gradient(...)`,
not a string check, is what tells a scrim's real first layer from its own `, none` fallback.

A third mistake surfaced once bullets started rendering: they painted on top of the second or
third letter of their own list item, not before it. `ul.b li` reserves its bullet's gutter with
`padding-left:40px`, and text boxes are drawn with `tf.margin_left = 0`, so a textbox built from
the li's full border box (padding included) put the text back at the unpadded edge, exactly
where the correctly-placed bullet already sat. This was never a pseudo-element problem: it is
that no text-bearing element's own CSS padding was ever subtracted from its box, and `ul.b li`
is the first component in the system that puts meaningful padding on the text node itself
rather than on a wrapping container.

**Verify:** `export_pptx.py` reads `getComputedStyle(n, '::before'/'::after')` for every element,
emits a shape for any pseudo whose `content` is not `'none'` and whose resolved background
paints something, and positions it from the host's own box, since every current use is
`position:relative` on the host with the pseudo `position:absolute` in px, never `auto`. Order
is the host's own DOM order plus the highest order number anywhere in its subtree, not the
host's alone, because a `::after` paints after everything already inside its element and a
scrim placed at "host order" can still sort ahead of the photo it exists to darken. Text boxes
are now inset by `paddingLeft/Top/Right/Bottom` before they are ever handed to PowerPoint.
`selftest.py`'s `pseudo_scrim` check exports the control fixture's cover, which already carries
`.scrim-flat`, and fails if no non-text, non-picture shape in it carries an alpha under 90%.
It does not yet cover the bullet dot: the control fixture has no `ul.b` or `.feat` in it, and
giving it one is the honest next step rather than a gap worth leaving undocumented.

### REG-50 · A probe that dies is not a deck that passed
`verify_pptx.py`'s three strongest rules, `ZOR-01`, `FIL-01` and `PIC-01`, all compare the
package against a live render of the HTML, and all three were wrapped in
`if paint and len(paint) >= n`. When the Playwright probe fell over, `paint` came back `None`,
the three rules were skipped, and the script printed `0 FAIL` and exited zero. It printed a
note first, which is not a verdict.

This was found by accident and only because the answer moved. Verifying the badge defect, one
run of the verifier on a deck whose badges had lost their gradient reported clean and the next
three reported the failure. The clean one was the probe dying. Had that run been the only one,
the conclusion would have been that the gradient loss did not exist, and the report would have
said so with a passing gate behind it.

The shape of this is REG-45 with the sign flipped. There, a gate that could not run was
described as a gate. Here, a gate that could not run described itself as a pass, which is
worse, because REG-45 at least leaves the reader to notice the verdict said DOCUMENTATION.

**Verify:** `PRB-01` fails when the probe returns nothing, and fails separately when the HTML
and the PPTX disagree on slide count so the two cannot be compared slide for slide. Any future
rule here that needs the browser belongs inside the same guard. A skipped check is a FAIL, not
a silence.

### REG-49 · A painted element that owns its text was painted as text alone
`.badge` is a 96 × 96 square filled with `--grad-brand-v-93` carrying a white numeral centred
in it. In every PPTX this system produced before v4.9 it exported as the numeral and nothing
else: white type on a white card, invisible, on three slides of the worked example.

The cause was one clause. The probe emitted a `box` record for anything painted, guarded by
`painted && !ownText`, so an element holding its own text was never given a fill. The guard
existed to stop a panel being painted twice, once as a box and once behind its text, and it
worked for every component where the fill and the words live on different elements, which is
almost all of them. `.badge` is the case where they live on the same one. The text record did
carry `grad` and `fill`, probed and then never read on the Python side, which is the tell:
the information was there and the consumer was missing.

Fixing the fill exposed a second thing the exporter could not see. `.badge` centres its numeral
with `display:grid;place-items:center` and its `text-align` is `start`, so reading `textAlign`
alone put the numeral hard against the top-left of a plate the design centres. `.btn` has the
same shape, `display:flex;align-items:center`, and had looked right all along only because its
padding is symmetric, which is a coincidence and not a specification. Fourteen elements across
the three reference documents depend on one of these two properties.

**Verify:** a painted text-bearing element emits its plate at its own **border** box, at the
same paint ordinal, directly under its text. Not as a fill on the text box: that box is offset
by −6/−4 and grown by +12/+8 for optical bearing, so filling it would paint a 108 × 104 plate
six pixels up and left of a 96 × 96 design element, which is a different defect wearing the
same fix. Vertical anchor is MIDDLE and paragraph alignment CENTER only where a flex or grid
host actually centres, read from `alignItems`/`alignContent` and `justifyItems`/
`justifyContent`. `selftest.py`'s `pseudo_bullet` row exports a fixture carrying both a `ul.b`
and a `.badge` and fails if the dots are missing, sit outside the 40px gutter, or the badge
plate has no gradient.

### REG-46 · A rule that reports nothing may not be a rule that found nothing
`IMG-10`'s first cut reused `n` as a loop variable, and `n` is the slide count in the same
function. After the loop `n` held a node dict, `validate_deck` threw on the next comparison,
and every deck-level rule after that point stopped running. The new rule reported nothing,
which reads as "correctly found no problems" rather than "the function died on line two".

Worse was how I tested it: I piped the run through `grep IMG-10` and read the empty result
as a clean pass. The traceback was right there in the output I had filtered out. A test that
greps for the expected string cannot tell silence from failure.

**Verify:** the block binds `sld` and `nd`, and any new deck-level rule should do the same,
because `n`, `s` and `i` are all taken in that function. When a rule reports nothing on a
case built to trip it, read the whole output and check the exit code before believing the
silence.

### REG-44 · A floor set where the cheapest answer sits is a specification
`PHOTO_MIN_AREA` was 0.06, and 0.06 is the crop table's smallest entry. The rule written to
stop a thumbnail standing in for photography was set exactly at thumbnail size, so the
cheapest way to satisfy it was to place the smallest legal image. Decks did. One came back
with a 726 x 184 strip pushed into the top-right corner on nine slides, each instance
identical, each one passing, and the creative director had to ask for imagery on every
single deck for months. The rule was not broken. It was answered.

It also measured the largest single image rather than the total, which is a second mistake
of the same kind: a slide earns its imagery from the area a reader sees. Three card images
in a row is an illustrated slide; one of the three alone in a corner is a compliance token.
The largest-image test cannot tell those apart, and it failed a slide the creative director
judged correct, which is how the mistake surfaced.

**Verify:** a slide now carries photography when its imagery SUMS to 15% of the canvas,
card images included. Measured across five decks, everything judged acceptable sums to
15.4% or more and everything judged wrong sums to 10.7% or less, with nothing in between,
so the threshold runs through empty space rather than through a judgment call. The deck
share moved from a 20% floor and a 25% target to a 30% floor and a 40% target, set by the
creative director rather than derived, because a target is a statement of taste and the
data can only say where the line is clean.

When setting any floor, ask what the cheapest thing that clears it looks like. If the
answer is something you would reject on sight, the floor is in the wrong place.

### REG-45 · A gate that cannot run is not a gate
The validator held one full-resolution float64 screenshot per slide until every rule had
finished. That is 50 MB a slide, so a 55-slide deck asked for 2.7 GB and the kernel killed
the process. No traceback, no message, exit 137, which reads as a hang rather than a
failure. One client deck was never validated once and nobody knew, so its nine corner
thumbnails, its twelve-slide run with no photography and its 55-slide length all shipped
unexamined. Every rule in this document was irrelevant to that deck.

**Verify:** plates are stored as uint8 and converted to float where they are sampled, which
is a few thousand pixels rather than two million. Peak memory on the 55-slide deck went from
a kill to 615 MB, and the three decks that already validated return byte-identical findings.
Resolution is untouched, because REG-02 forbids downsampling the plate. When a check is slow
or heavy, ask what it does on the largest input anyone will really give it, not the one in
front of you.

### REG-41 · A family is not a variant
The exporter matched `.brandx-x, .brandx` and painted one asset, `brandx-cover.png`, across
the full canvas for any of them. The cover X and recipe 10's cropped wedge are different
shapes from different Figma nodes, and the code treated "has a Brand X" as the question. So
every deck built on recipe 10 got the cover's dark wedge pair stretched over a light content
slide, beneath all of its text, and the page was unreadable. It was latent from the day the
variant was added, because neither deck that ships with this system uses recipe 10. The first
deck that did use it came back with the defect on page nine.

The same shape of mistake is one the type ladder already taught: `font-family:'Aptos'` with
`font-weight:900` is a family question answered with a weight, and it silently gives you Bold.
When a component has variants, the code has to ask which one, and an unrecognised answer is a
hard stop rather than a fall back to a sibling.

**Verify:** the probe reports the variant name rather than a boolean, `bake_export_assets.py`
bakes one plate per variant at the geometry in the CSS rule, and an unknown variant raises
rather than guessing. `PIC-01` in `verify_pptx.py` hashes the baked assets and fails when the
plate on a slide is not the plate the source's classes call for. The first cut of PIC-01
counted full-canvas pictures, which the defective slide passed with exactly the right count
and the wrong artwork; identity is the test, not arity.

### REG-42 · Nothing said a photograph may only be used once
Every photography rule in the set was about whether an image is used WELL: the crop list, the
native resolution, the measured scrim, the share of slides, the gap between them. Not one
asked whether it is used TWICE. A twelve-slide deck came back with one frame on a single slide
twice and another frame on two slides, having drawn on eight of nineteen available
photographs, and it returned zero failures. The rule was not broken. It had never been
written, which is the harder kind to notice.

**Verify:** `IMG-07` fails the same photograph twice on one slide, always, because that reads
as a mistake rather than a motif. `IMG-08` is arithmetic: nineteen frames cannot carry forty
slides, so a deck longer than the library warns and a deck no longer than it fails. Both run
in `lint_source.py` off the `{{IMG_*}}` placeholder and in the validator off a fingerprint of
the inlined blob, because after inlining the library name is gone.

### REG-43 · REG-23 was fixed with nothing standing over it
REG-23 documents the defect: a background device keeping its z-order through the export, after
a version that hardcoded the Brand X as background and painted it over a cover's headline. That
version was fixed, correctly, by deriving paint order from the DOM instead of a class-name
list. But the fix lived only in `export_pptx.py` and in a comment explaining it. `selftest.py`
builds every fixture and validates every one of them, and not one of those checks ever calls
`export_pptx.py`. The whole PPTX path could regress to the original class-name-list mistake, or
to any other z-order bug, and the self-test would still print a clean run, because it was never
looking there. A fix with no test over it is a fix that depends on nobody touching that file
again, which is not a property this system relies on anywhere else.

**Verify:** `selftest.py` exports the control fixture's cover through `export_pptx.py --no-embed`
for real and opens the resulting PPTX with `python-pptx`. It identifies the Brand X shape by an
exact blob match against `assets/export/brandx-cover.png` (the one asset placed unmodified,
so it is the one thing in the slide that byte-matches its source; the photo does not, because it
is cropped and re-encoded on the way in — see REG-41 for why an identity check and not a boolean
is what this needs), the photo as the largest remaining picture, and the headline as the first
text-frame shape, then asserts photo before Brand X before text, matching DOM order. This is the
only check in the file that touches the exporter, and it needs `python-pptx` to run.

### REG-40 · A rule in the documentation is a promise
`IMG-01`, "photography resolves to a library ID", sat in the rule table from the first revision as a
WARN. Nothing ever implemented it. For about twenty revisions anyone reading the table believed the
library was enforced, and anyone reading a clean run believed their deck had passed that check. No
amount of testing would have found it: the rule that is missing is the rule nobody can see not
firing. Meanwhile ten rules that do fire were not in the table at all, so a builder who hit `TXT-03`
or `ZOR-01` had nothing to read, and `GEO-01` named two different rules in two different scripts, so
the one row a reader could find described the wrong one.

**Verify:** `check_provenance.py` `GEN-02` compares the documented rule set against the ids the code
can actually emit, in both directions, and fails on either gap. It found all of the above on its
first run. `IMG-01` is implemented now, in `lint_source.py` rather than the validator, because by the
time the assets are inlined every `src` is a base64 blob and the library name is gone: the
placeholder is the only place the claim is checkable. The PPTX family is documented as its own table,
and the canvas rule in `verify_pptx.py` is `PPT-01`.

### REG-54 · The packaging step was reviewed for size and never for shape
v4.10.0 shipped 610 files into a format capped at 200. The icon library went in as 497 loose
SVGs and the package was refused at install. Every gate passed on the way out: the self-test was
clean, the validator was clean, the provenance check was clean, the zip built without complaint
and 8.6 MB looked entirely reasonable next to the 8.1 MB before it.

The byte count was measured on every release for ten releases. The file count was measured on
none. A limit that had never been within an order of magnitude became a limit that had been
crossed by a factor of three, and nothing in the pipeline was positioned to notice, because
nothing in the pipeline had ever needed to look at that axis. **A constraint you have never been
near is a constraint you are not measuring**, and adding one asset class changed which axis
mattered without changing anything that was being watched.

The fix has two halves and the second is the durable one. The markup moved into a single
`icons.json` and the tree went from 610 files to 103. Then `PKG-01` so the next asset set fails
here rather than at a user's install, with a warning at 85% so there is room to act before the
wall rather than at it.

Splitting into two files rather than folding the markup into the manifest is deliberate.
`lint_source.py` reads the manifest on every write inside a 30ms budget, and a megabyte of SVG
in that path would have traded an install failure for a slow linter, which is the kind of fix
that creates the next entry in this register.

**Verify:** `scripts/check_package.py`, run against the directory or a built `.skill`. It reports
the count, the headroom and the three largest directories, because "too many files" without
"and they are all here" sends the reader counting by hand. Checked against the refused v4.10.0
zip, where it names the icon folder.

### REG-53 · Two documents about one system will disagree unless something compares them
The system ships a spec book and a teardown. The split is real, one is for looking at and one is
for copying geometry out of, and each carries material the other does not. Keeping both was the
right call. The price is that they can drift, and they had: the spec book's masthead claimed an
**18-frame photo library** against a manifest of 19 and a teardown that said 19, and carried
**v1.0** through ten releases. Both numbers were typed by hand into a header nobody re-reads.

Asked directly whether the two contradicted each other, a first sweep said no. That sweep compared
hex values, contrast ratios and type tokens and missed the masthead, because "18-frame" does not
match a pattern looking for "19 photographs". **A search for contradictions only finds the
contradictions it was shaped to find**, which is the same lesson as GEN-03's three wrong cuts.

Two fixes, and the order matters. First the counts stopped being typed: `build.py` resolves the
masthead from `manifest.json` and `provenance.json`, and the teardown counts its own gaps rather
than claiming "four" after one left the list. A fact with one source cannot disagree with itself.
Then `check_documents.py` for everything that still has two copies.

`DOC-03`'s first cut read only the spec book's tab-separated type rows, so it found exactly **one**
fact stated in both documents and reported a clean pass on a comparison it had barely made. The
teardown writes the same ladder as `t-h2\n80px / .95`. Reading both layouts took it from 1 shared
fact to 18. A cross-check that understands one side is not a cross-check.

**Verify:** `DOC-01` through `DOC-04`, each proven by reintroducing its defect into a built
document one at a time. `build.py` builds both documents and runs the comparison, so they cannot be
released separately. `DOC-00` fails when the browser is missing rather than passing quietly, per
REG-50.

### REG-52 · An icon set is the element most punished by inconsistency
Iconography sat on the gap list from v4.5 to v4.10 with a one-line entry: three icon PNGs on one
recipe is not an icon system. That entry is what got it filled correctly, because it named what was
missing rather than quietly leaving a hole somebody would fill by improvising.

**Generating icons on demand was the wrong answer and was rejected.** Two marks side by side with
different stroke weights or different optical sizes read as a mistake instantly, and generation
produces a fresh answer every time, so weight, corner radius, terminal style and optical grid all
drift per icon and, worse, drift between two decks for the same client. A generated icon also has no
provenance, and this system's rule is that a name is a claim and a node id is checkable. There would
be nothing to check it against. It is unreviewable at scale too: sixty icons can be reviewed once, a
new icon on every deck forever cannot.

**Four things were wrong on the way in, and each is a rule now.**

`currentColor` only survives as raw inline markup. A data URI is an opaque document that cannot see
the page's `color`, so inlining icons the way photography is inlined would have painted all 422
monochrome marks black, including every one on the dark ground. They go in as markup.

PowerPoint has no SVG at all, so an icon that is not rasterised simply disappears, which is the FDU
partner-logo failure with a different asset. They are not pre-baked: 497 marks across five sizes and
three inks is a grid of thousands of plates almost none of which a deck uses. The exporter
rasterises only what the deck contains, at 4x, reading the colour off the rendered element because
`currentColor` means nothing outside a browser. The first cut launched a browser per icon inside the
slide loop and spent most of the export starting Chromium; it is one session for the deck now.

The rules themselves were written inside the `if n[0] != "img": continue` loop, where they could
never fire on a `<span class="ico">`, which is every icon in the system. A fixture built to break all
four came back clean. That is REG-46 for the second time, and the only reason it was caught is that
the fixture was built to fail before the rules were believed.

And the branded set is a WARN, not a FAIL. The source sheet marks 51 icons with an orange label and
says they are specific to a product or service. That colour is readable out of the export, so the
exclusion is measured rather than judged. But the set includes the ATC content types, `lab`, `demo`,
`workshop`, `training`, `community`, and a WWT deck about the lab should be able to show the lab
mark. `ICO-02` asks for a written reason in `data-why` instead of refusing.

**Verify:** `ICO-01` through `ICO-05` in `lint_source.py`, each proven against a fixture built to
trip it. `assets/icons/manifest.json` records the file key, node id and pull date beside every mark,
and `check_provenance.py` compares it against the folder in both directions. The teardown shows the
ladder at true size and the same row on both grounds, because a table of 497 names says nothing
about whether the set holds together.

### REG-51 · A number in the documentation is a promise too
`GEN-02` proved the rule IDS in the table match the code. It says nothing about the VALUES beside
them, and the value is what a builder copies. At v4.7 the photography floor moved from 20% to 30%
and the per-slide test moved from "largest image at 6%" to "imagery sums to 15%". The validator was
updated. Section 2 of THE CONTRACT went on saying 20% and section 3 went on saying 6% for two
releases, so the one page this skill insists is not optional reading disagreed with the validator in
two places, and contradicted its own section 1 on the same screen.

Writing the check took three attempts and each failure is worth more than the rule.

The first asserted the current value appears somewhere in the contract. It passed the live defect:
"30%" was already on the page in section 1, so section 2 reading "20%" contradicted nothing the
check could see. **Presence cannot tell a stale number from a current one when both are present.**

The second listed superseded values and forbade them anywhere in the contract. It failed a clean
tree, because "20%" is the retired photography floor and also the live `DARK_MAX_SHARE` ceiling. **A
bare number carries no indication of which rule owns it,** so a string test cannot be scoped to a
constant.

The third anchors each constant to the line that makes its claim, and it still missed one case:
reworded one of the two lines stating the per-slide test, the other still said 15%, the anchor
matched the survivor and the check passed a self-contradicting page. **A claim made twice has to be
checked twice or it is only checked once.**

**Verify:** `GEN-03` pairs each constant with a phrase identifying its line, the value that line
must carry, and how many lines carry that anchor. All three parts are load-bearing. Seven
deliberate reversions were run against it one at a time and all seven fail. When you move a
threshold, expect to update `CLAIMS` in the same change, and when you reword a claim expect
`GEN-03` to ask you to re-check it, which is the rule working rather than the rule complaining.

### REG-33 · Test the rules against good work, not just against bad
A first pass at the substance rule failed a correct three-row table for having terse cells, and
tested photography in a way that would have pushed people away from using it. Both were caught only
because there is a negative control fixture that legitimate work has to pass.
**Verify:** `selftest.py` runs the control first. A rule set that fails everything is not strict, it
is broken, and only the control tells the two apart.

### REG-29 · The export must carry what the typography depends on
Two things the HTML relies on were being thrown away in the PPTX path, both silently.
`textContent.replace(/\s+/g,' ')` collapsed whitespace, and `\s` matches U+00A0, so **every
non-breaking space in the system became a breaking space** and the exported deck rewrapped: bound word
pairs came apart and widows appeared that the HTML could not produce. Separately, the cover crop always
centred, ignoring `object-position`, which moved the subject on all three slides that set it.
**Verify:** collapse with `/[^\S ]+/g`, never `/\s+/g`. Read `objectPosition` in the probe and offset
the crop by `overflow × fraction`. Then diff the exported line breaks against the HTML, because a
rewrap is the kind of defect that looks like a design choice.

### REG-26 · The mesh is ground, and a class is not the only way to break that
Testers were putting the diamond pattern inside content boxes. It is a background device: nested in a
panel its `plus-lighter` blend composites against the panel fill instead of the page surface, the
container clips a gradient authored in absolute page coordinates, and the PPTX path drops it silently
because the mesh only exists there as part of one flat ground plate.
**Verify:** PAT-05 fails a `.mesh` whose parent is not the `.slide`, **and** fails any element that
paints mesh art through `background-image`. The second half matters: the class is the obvious route in
and the stylesheet is the quiet one.

### REG-27 · Deleting a rule is not finished until its callers are gone
Removing `.brandx--a` and `.brandx--b` left two files still asking for them. `.brandx` on its own has
no width or height, so those elements rendered 0 × 0, the node walk skips sub-pixel boxes, and both
covers shipped with no Brand X at all and a clean validator run. The same shape of bug produced the
GTM deck's missing X when the class was renamed in one file and not the other.
**Verify:** PAT-06 fails a retired `.brandx` reference and, separately, any Brand X that measures
0 × 0. Grep for callers in the same commit that deletes a rule.

### REG-28 · One copy of the system CSS, or it drifts
The GTM deck kept its own frozen copy of the design system stylesheet. It fell a revision behind, so
the cover asked for `.brandx-x` against a stylesheet that had never heard of it.
**Verify:** every build composes the head from one source and adds only its own deck-local block.
A deck that carries a full copy of the system CSS is a bug waiting for the next token change.

### REG-24 · A coverage claim nobody checks is worse than no claim
The recipe-to-source map said recipe 06 covered "Right flex 2/3 image" and recipe 11 covered
"Slide 49". Neither reproduced those frames. The false entries made four missing layouts look
covered, so nobody went looking, and the gap sat there through several revisions. The map also
stopped at 17 after four recipes were added to the gallery.
**Verify:** MAP-01 checks the gallery against the map in both directions and fails on either
mismatch. **Name source nodes by id, not by frame name** — an id is checkable, a name is a claim.

### REG-23 · Background decoration must keep its z-order through the export
All decoration was placed after the content, which put the flex triangle on top of the photograph it
is meant to sit behind. HTML order carried it; the export flattened it.
**Verify:** `.tri` is placed immediately after the ground plate; the lockup and the arrow are placed
last. Anything new that is background gets `z: 'bg'`.

### Rules that were wrong, not the slides
Recipe 08 shipped for several revisions as a scrimmed full-bleed photograph with a hero number. Node
`1659:961` is nothing of the sort: a centred h2, a photo band off the left edge, a card overhanging it
with a ring, and a figure column right. It was never checked against the node. Four further layouts
(`1659:986`, `1138`, `1170`, `1191`) were absent entirely, which is why the recipe count was seventeen
against a source that has more. Recipe 03 was a mesh-and-headline statement slide with a lede; node
`1839:55` is a full-height gradient panel against a photograph that bleeds off the right, with a
seven-line sentence-case headline. TYP-03's three-line cap would have rejected the source, so the rule
took the exception.
The uppercase cap outlawed the eyebrow. The one-headline rule outlawed the two recipes that lead with
a stat. The crop list was missing a crop the source uses. MRK-01 required a lockup on dividers when
the source puts the bug there, and passed a wrong divider for three revisions. TYP-09 and TYP-10 did
not exist until a build shipped defects the rule set could not see.
