## 15. Governance

A new component needs a job no existing component does, a fixed internal spec, and two slides that
need it. Token changes are minor versions; geometry, margin and grid changes are major. Assets are
versioned with the system, not alongside it: if a frame is replaced or a mesh re-exported, update
`assets/manifest.json` in the same change.

**Deleting a rule is not finished until its callers are gone.** Grep for them in the same change
(REG-27).

**A new rule has to pass three tests before it ships.**

1. **Run it against the accepted decks first.** More rules in this system have turned out wrong than
   slides have. `TYP-04` read box width rather than text extent and would have failed two correct
   recipes on promotion. The mesh box list, the crop list, the display-1 ladder step and the
   three-line headline cap were all narrower than the source.
2. **Derive the threshold, do not choose it.** `scripts/calibrate.py` prints the spread across
   accepted decks. Set the threshold outside it with margin and record both numbers in the code.
3. **Prove the cheapest way to pass is the right thing to do.** Add a fixture to
   `gaming_fixtures.py` that satisfies the rule while doing no design, and make it fail. Then check
   the negative control is still clean.

A rule nobody has watched fail is a rule nobody has tested.

Current: **v4.10**. Minor in structure, material in effect: the system has an icon library.
497 marks from Blue Steel 3.0, Figma node `87131:514`, 429 universal and 68 branded, each
re-cut to a 16-unit viewBox and painted with `currentColor` so one file serves the light
surface and the dark ground. `.ico` and a fixed five-step ladder are in `system.css`,
`{{ICON_<name>}}` resolves through the inliner as raw markup, the exporter rasterises just the
marks a deck uses, and `ICO-01` through `ICO-05` enforce the set, the ladder, the accessible
name and the branded exclusion. Iconography leaves the gap list it has been on since v4.5.
See REG-52, REG-53 and REG-54.

Previously: **v4.9**. Minor in structure, material in effect: `export_pptx.py` now reads
`::before`/`::after` computed style, so a bullet dot (`ul.b li`, `.feat`) and a photo scrim
(`.media`) survive into the PPTX instead of silently vanishing, since neither is a DOM node
the old probe could ever see. A text-bearing element's own CSS padding is now subtracted from
its box before it becomes a PowerPoint textbox, which `ul.b li` needed to keep its bullet from
landing on top of its own second letter. Verifying that work turned up two more: a painted
element that owns its text now exports its own plate, so `.badge` stops shipping as an
invisible white numeral on a light card, and flex and grid centring is read from the
properties that actually carry it rather than from `text-align`. `verify_pptx.py` gained
`PRB-01`, because three of its rules need the browser and a run where the probe died used to
report `0 FAIL`. See REG-48, REG-49 and REG-50.

Previously: **v4.8**. Minor. `.rule-h--brand` is retired by direction: it was never intended
as an element, and it is removed from the stylesheet, the class inventory, the component
gallery, recipe 10 and both reference decks in one change. A band at the top or bottom of
the page must now reach that edge and both sides (`IMG-10`). See REG-47 and REG-46.

Previously: **v4.7**. Minor in structure, material in effect: the photography floor moved
from 20% to 30% with a 40% target, and a slide now counts as carrying photography when its
imagery SUMS to 15% of the canvas rather than when its largest single image reaches 6%.
The validator also no longer runs out of memory on a deck over about forty slides, which
it had been doing silently. See REG-44 and REG-45.

Previously: **v4.6**. Minor: no geometry, margin or grid changed. Three defects from a
client build are closed, each with the rule that would have caught it: a Brand X
variant painted with the wrong plate (`PIC-01`), a photograph used twice (`IMG-07`,
`IMG-08`), and font embedding that was present and unusable (`FNT-01`, now five checks
instead of one).

Previously: **v4.5**. Minor: no geometry, margin or grid changed. What changed is what the
system shows you (`scripts/teardown.py`), what it exports for other tools
(`assets/tokens.json`, `assets/tokens.css`) and two new consistency checks that caught real
defects on their first run (`GEN-01` staleness, `GEN-02` docs against code).

Three principles, each one paid for:

1. **When a rule and a good slide disagree, check the rule against the source first.** More rules in
   this system have been wrong than slides have.
2. **When a recipe looks nothing like the source, re-pull the node rather than adjusting it.** Nudging
   a wrong reconstruction converges on a different wrong answer.
3. **When a rule is missing, add it and re-run against both reference documents before trusting it.**

---
