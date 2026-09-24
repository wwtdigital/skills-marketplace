# How this system has actually failed

Every entry here happened. Each one passed visual review, and most of them passed the
validator of their day. Read it once before you build; the patterns repeat.

The full forensic analysis of the worst case is in the project folder as
`RFP-Failure-Analysis.md`. This is the short version plus the older failures.

---

## The one that changed the system: 91 white pages, zero failures

A senior designer built a 91-slide RFP response on v3.2. Measured off the delivered file:

| | Measured | System expects |
|---|---|---|
| Slides carrying a photograph | **12%** | 20% floor, 29 to 38% in accepted decks |
| Slides carrying the diamond mesh | **2%** | every light-ground content slide |
| Slides on `g-white` | **52 of 91** | no recipe uses `g-white` at all |
| Median content coverage | **8%** | 15% floor, 22 to 39% in accepted decks |
| Headlines at the identical pixel y=236 | **68 of 91** | 40% ceiling on one architecture |
| Distinct headlines | **54 for 91 slides** | no headline twice |
| Slides titled "(cont.)" | **9** | none |
| Live text in the PPTX | **zero** | every text element |

**It returned zero failures.** Five things made that possible, and all five are now closed.

`DEN-01` computed a density band with `lo`, `hi` and `floor` and then tested only
`ink > floor`. Nothing tested the floor from below, so 52 near-empty slides passed in
silence. → `DEN-06`, and REG-31.

`SEQ-01` signal B3 cleared a repeated page style when two headlines shared a stem. "X"
followed by "X (cont.)" shares its entire stem, so the rule written to prevent pagination
was the rule licensing it. → B3 deleted, `SEQ-05` bans the word, and REG-32.

`SEQ-01` only ever compared **adjacent** slides. A deck can pass on every pair and still be
one page ninety-one times, because a table slide and a two-card slide produce different
component censuses even when the ground, headline step, headline position and architecture
are identical. → `SEQ-02` at deck level on bucketed architecture.

`TYP-04` and `GEO-05` were **WARN**. They were broken on 57 of 80 text slides and on every
panel, and a deck can break a WARN forever and still report 0 FAIL. → both FAIL, and
`TYP-04` re-metriced to rendered text rather than box width.

**Nothing asked whether the PPTX contained text.** All 91 slides were single flattened
bitmaps at 1919 × 1080, the rounding tell of a screenshot pipeline. → `verify_pptx.py`.

### The deeper cause, which is worth more than the five fixes

Every statement the skill made about the mesh was a restriction. Opacity must be .11, blend
must be plus-lighter, the box must be one of four sizes, `--diag` must sit at x 0, never
behind data, never inside a container, never with a Brand X, never two devices on a slide.
Ten constraints, five FAIL rules, and not one sentence saying it should be there.
Photography carried a crop list, a mandatory scrim, a measured contrast ratio and resolution
warnings.

**So the safest composition under the validator was a white page with a headline and a
paragraph**, which cannot fail `IMG-02`, `IMG-03`, `IMG-04`, `PAT-02`, `PAT-04` or `PAT-05`.
Tell a designer under deadline to fix every FAIL and they converge on it. That is not a
misunderstanding of the page styles; it is the incentive gradient in the rule set.

→ REG-30. Every presence rule now has a paired substance test, and any rule added later must
satisfy one test: **the cheapest way to pass it is the right thing to do.**

---

## Geometry reconstructed by eye, three times

The logo bug was rebuilt from a render and was wrong on all four axes for three revisions.
The divider was built from a thumbnail and was the wrong layout in kind. The Brand X was
rebuilt as two copies of one clip-path, which gave bars of 536 and 518 against a source that
is 536.2 and 273.3, a deliberate 0.51 ratio a shared shape cannot produce.

**Geometry comes from the node, never from a picture of the node.** If you have Figma, pull
it and cite the id. If you do not, copy from `assets/recipes.html` and invent nothing.
→ REG-03, REG-25.

---

## Rules that were wrong, not the slides

More rules in this system have turned out wrong than slides have. Check the rule against the
source first.

The uppercase cap outlawed the eyebrow. The one-headline rule outlawed the two recipes that
lead with a stat. The crop list was missing a crop the source uses. `MRK-01` demanded a
lockup on dividers when the source puts the bug there, and passed a wrong divider for three
revisions. The mesh box list was missing a placement. The display-1 ladder said step down at
twelve characters when the source sets thirteen at 200px. `TYP-03` capped headlines at three
lines when node 1839:55 sets seven on purpose. `TYP-04` measured box width, which failed two
correct centred recipes. A first pass at `DEN-07` failed a correct three-row table for having
terse cells, and would have pushed people away from photography while `IMG-05` pushed them
toward it.

That last pair was caught only because `selftest.py` runs a **negative control**: legitimate
work that has to come back clean. A rule set that fails everything is broken, not strict, and
only the control tells the two apart. → REG-33.

---

## Silent failures in the export path

Each of these produced a plausible-looking wrong result, which is the pattern.

A malformed `spPr` child order was tolerated by LibreOffice and discarded by PowerPoint, so
every gradient fell back to a theme accent and looked like a blue that was almost right.
**A renderer that agrees with you is not a verification.** → REG-19, REG-20.

`typeface="Aptos"` with `b="1"` resolves to Aptos Bold. Aptos ships its heavy cuts as
separate families, so Black needs `typeface="Aptos Black"`. Every headline rendered slightly
light and nothing warned. → the weight-to-family map.

`textContent.replace(/\s+/g, ' ')` destroyed every U+00A0 in the deck, because `\s` matches
it. Bound word pairs came apart and the exported deck grew widows the HTML could not
produce. → REG-29.

The cover crop always centred, ignoring `object-position`, which moved the subject on all
three slides that set it. → REG-29.

Deleting `.brandx--a` and `.brandx--b` left two files still calling them. `.brandx` alone has
no geometry, so those elements rendered 0 × 0, the node walk skips sub-pixel boxes, and two
covers shipped with no Brand X and a clean validator run. → `PAT-06`, REG-27.

---

## Drift between copies

The GTM deck kept its own frozen copy of the system stylesheet. It fell a revision behind, so
its cover asked for `.brandx-x` against CSS that had never heard of the class.

There is one copy now, `assets/system.css`, and everything resolves it as a placeholder.
**When the skill describes something it does not ship, the reader reconstructs it, and
reconstruction is where the defects come from.** → REG-28, REG-32.

---

## The meta-pattern

**Every failure in this system was a case where the wrong thing looked plausible.** A theme
blue standing in for a discarded gradient. Aptos Bold for Aptos Black. Two equal bars instead
of a 0.51 ratio. LibreOffice agreeing with a malformed file. Sixty-eight identical slides
reading as twenty layouts because the component census differed. Half a density band reading
as a whole one in a report that says 0 FAIL.

Which is why this system prefers measured checks over judgment, fails loudly rather than
degrading gracefully (`font-synthesis:none`, stripped `<p:style>`), and keeps an adversary
and a control in the test suite.

**Nothing is correct because it looks correct. And no design is bad design.**
