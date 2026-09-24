# THE CONTRACT

**Read this page. Everything after it is reference you look things up in.**

This section exists because the reference did not work. A senior designer built a 91-slide deck from
v3.2 and it came out as white pages: 12% of slides carried a photograph, 2% carried the diamond mesh,
68 of 91 put the headline on the same pixel, median content coverage was 8%, one slide shipped to a
client with "Lorem ipsum" on it, and the whole file was flattened screenshots with no live text. **It
returned zero failures.** Everything below is what should have been on the first page.

### 1. The defaults, which the system never used to state

| | Default | Where it changes |
|---|---|---|
| Headline alignment | **Flush left at x 72** | Four recipes centre: 08, 09, 12, 14 |
| A centred headline | **Centres on x 960** | The content area is 72 to 1848, symmetric about 960. A 1776 box belongs at `left:72`, never `left:0`, which centres on 888 |
| Ground | **`#F6F6F6`**, the surface | `g-grad`/`g-grad-diag` for a gradient slide, photography for cover, divider, closing, and `g-dark` for **at most one slide in five** |
| Panels | **`#FFFFFF` raised off the surface** with `--shadow-panel` | Never grey on white. Inverted, a panel reads as a hole in the page |
| Bands | **A band at the top or bottom of the page runs to that edge and both sides.** A band floating mid-page does not | Recipe 11 is the header, recipe 17 the footer, recipe 07 the inset band that touches nothing |
| Photography | **30% of slides minimum, 40% the target.** A slide counts when its imagery sums to 15% of the canvas, card images included | Cover, divider and closing carry a bleed by definition |
| Background device | **Every light-ground content slide carries one** | Only a table or a chart slide goes without, because data may not sit on the mesh |
| Icons | **From the Blue Steel set only, at a size on the ladder: 24, 32, 48, 64, 96.** They inherit the slide's ink | A branded mark needs a written reason (`ICO-02`) |
| Body copy | **26px**, the default step | 24px inside a card, 20px for a source line. Nothing below 20px, ever |
| Headline measure | **1176px**, eight columns | A centred headline may run the full 1776 |

### 2. The ratios, measured off the two decks we accepted

Not chosen. Derived, and re-derivable with `scripts/calibrate.py`.

| | AI GTM (7 slides) | Built for Success (13) | Floor |
|---|---|---|---|
| Slides carrying a photograph | 29% | 38% | **30%**, and never more than 6 in a row without one |
| Light-ground slides with a background device | 100% | 91% | **every one**, tables and charts excepted |
| Content coverage, thinnest slide | 0.39 | 0.22 | **0.15** |
| Content atoms, thinnest slide | 22 | 11 | **8** |
| Largest share on one architecture | 29% | 23% | **40% ceiling** |
| Slides on the dark emphasis ground | — | — | **20% ceiling**, and never two in a row |

**Every ratio above is a floor except the last two, and the difference matters more than it
looks.** A floor is gamed by doing nothing: no photography, no device, an empty page. A
ceiling is gamed by doing the striking thing everywhere until it stops being striking. Those
are opposite failure modes and they need opposite rules, so do not read `PAT-09` as "use the
dark ground 20% of the time". Read it as "an emphasis page is rare or it is not emphasis".

The recipe gallery is not the calibration source. It shows a mesh on half its recipes and photography
on three quarters because its job is to show every device once. A deck is not a catalogue.

### 3. No design is bad design

**An empty page is a defect in the same way an overfull one is, and it is the more common one.**

Every presence rule in section 14 is paired with a substance test, because a rule that can be
satisfied by adding an element will be. The specific closures, so nobody wastes time discovering them:

- **An empty panel is ground.** It contributes nothing to coverage. One enormous grey rectangle buys
  no density.
- **A slide counts as carrying photography when its imagery sums to 15% of the canvas**, at a
  declared crop, card images included. A thumbnail pushed into a corner is not photography, and the
  deck is checked for gaps as well as share, so meeting the quota on the first four slides and
  coasting does not meet it.
- **An empty component is not a content atom.** Thirty empty chips score zero.
- **Architecture is bucketed.** Nudging a headline 20px does not make a new page style.
- **Sparse roles are capped at 35% of a deck.** Relabelling a thin content slide as a statement
  does not reach the lower bar.
- **A PPTX with no live text is not a deliverable.** `verify_pptx.py` refuses it.

The governing principle, and the test to apply to any rule added later:
**the cheapest way to pass should be the same as the right thing to do.**

### 4. Before you build anything: look at the system

```bash
python3 scripts/teardown.py -o WWT-teardown.html      # then open it
```

**Every token in this system, rendered as a specimen, on one page.** A colour is a swatch with
its measured ratio, a type step is a line set at that size in the real Aptos cut, a shadow is a
card wearing it, the mesh is the actual vector at its actual opacity. It takes two minutes to
read and it is the only part of this skill that shows you the system rather than describing it.

This exists because the two decks that came back wrong did not fail on a rule. They failed on
never having seen the system. One was 91 pages of a single layout with no photography and no
background device; the other had the wrong bug in two corners, body copy drifting across three
size steps, and a gradient device invented inside a gradient panel. Both builders had this
skill open. Neither had looked at the system, because until v4.5 there was nothing to look at
except prose and a table of hex strings, and **a table of hex strings is the thing a reader
skims.**

The page also names what this system does **not** have: no positioning work, no motion, and one
unchecked exemption. Those are gaps, listed as gaps. If you need one of them, it does not exist
yet and you are inventing it. Iconography was on that list until v4.10 and is not any more.

### 4a. Above eight slides, write the plan first. One line per slide: what it has to land, its role, its
recipe, its source material. Then hold it to three constraints.

1. **No headline appears twice.** 91 slides carried 54 headlines in the deck that prompted this.
2. **There are no "(cont.)" slides.** Content that does not fit is cut, compressed into a different
   recipe, or moved into an appendix document. `SEQ-05` fails on the word.
3. **Over 30 slides needs a reason and over 40 fails.** A deck is not a paginated document.

`narrative-crafter` and `slide-planner` exist for this and do it better than an ad-hoc list. Use them
first. **This skill does not start until there is a plan**, because the 91-slide RFP failure happened
before a single slide was composed, and no amount of pixel correctness recovers from it.

### 4b. Two things to establish before the first slide

The first decides whether anything is enforced. The second decides where numbers come from.
**Neither requires Figma**; only reproducing a specific frame does.

**Run the doctor. It decides whether any of this is enforced.**

```bash
python3 scripts/doctor.py
```

Everything in section 14 is a Python file driving headless Chromium. Two people can read
this document and produce very different decks because one of them can execute it and the
other cannot, and until the doctor existed nothing told either of them which they were. It
ends on one of three verdicts and you have to know yours:

| | What is real | What you must say |
|---|---|---|
| **ENFORCED** | everything. The deck is gated | nothing extra |
| **PARTIAL** | the static lint only: continuation slides, placeholder copy, the inverted panel, an off-axis centred headline, a nested mesh, a ragged set | **say the deck is lint-clean, not validated.** Contrast, measure, widows, coverage, substance, photography share and architecture diversity are all unchecked |
| **DOCUMENTATION** | nothing | **do not describe the output as validated.** You have a stylesheet and a reference document |

Getting to ENFORCED is two commands and the doctor prints them. Do that rather than working
around it.

**Establish where geometry comes from, and never invent it.**

**Most decks need no Figma at all.** Say so, because the opposite assumption makes people
without it think they are working in a degraded mode and start guessing, which is the failure
this rule exists to prevent. The twenty recipes in `assets/recipes.html` carry their real
measured geometry. Composing a deck from them is the normal path and it is complete.

Figma is needed for exactly two jobs:

| Job | Needs Figma |
|---|---|
| **Compose a deck** from the twenty recipes, any copy, any slot recombination | **No.** This is most work |
| **Reproduce a specific frame** the user points at | Yes. You cannot reproduce what you cannot measure |
| **Add a new recipe** to the system, or correct an existing one | Yes. A recipe without a node id is a guess |

### The decision procedure

Check your own tool list for `get_design_context` before saying anything about Figma.

**Figma present, and the request names a frame** (a `figma.com` URL in the message, "match
this frame", "implement this design", "like the one in the file"). Pull the node. Normalise
sx 0.989487, sy 0.988649 from the 1940.4 × 1092.4 artboard. **Cite the node id** in the
slide's caption or a comment: an id is checkable, a frame name is a claim.

**Figma present, request does not name a frame, and a frame would plainly help** (they are
asking for something the twenty recipes do not cover). Ask once, with
`AskUserQuestion`: do they have a Figma link for this layout, or should you compose from the
recipes. **Offer composing from the recipes as the first option**, because it is usually the
right answer. If they have no link, proceed from the recipes and do not mention it again.

**Figma absent.** Do not ask for a link. A link you cannot open is worse than no link,
because it sets up an expectation you cannot meet. Say once, in a sentence, that you are
composing from the twenty bundled recipes rather than reading the Figma source, then build.
**You may recombine slots, change copy, change photography and change density. You may not
invent a coordinate, a span, or a device placement.** If the user pastes a Figma URL anyway,
tell them plainly that Figma is not connected, offer the nearest recipe, and ask whether they
want to send a screenshot instead so you can at least match the composition by eye while
taking every number from the recipes.

**Nothing fits, with or without Figma.** Assemble from the slot grid in section 11. Keep
every panel on a column edge and a legal span, and let `GEO-05` check you.

### A Figma frame is not automatically authoritative either

Node 1839:55 is 6038px tall because a text box overflowed and the frame grew with it, so
every layer position that depended on frame height was unusable in it. **Check that the frame
is 1092.4 tall before trusting a percentage read off it.** When a frame is malformed, take
the values that are authored at slide scale, take the rest from the recipes, and say which
you did which for.

### Never claim provenance you do not have

A caption that cites a node id when the geometry actually came from a recipe is worse than
one that cites nothing, because the next person treats it as verified. Cite the node id when
you pulled the node. Cite the recipe number when you composed from a recipe. Both are honest;
mixing them up is how a false coverage claim gets into the system, which has happened before
(REG-24).

---

### 4c. Refreshing against Figma

**The source file changes. Re-pull it periodically and diff, rather than assuming.**

```bash
python3 scripts/check_provenance.py                          # internal consistency, no Figma
python3 scripts/check_provenance.py --inventory pulled.json  # drift against a fresh pull
```

To produce `pulled.json`, with Figma connected:

1. `get_metadata` on the section node in `assets/provenance.json` → `source.section.node`.
   It returns a large tree; read it from the tool-result file rather than into the transcript.
2. Take every **direct child of the container frame**. Those are the layout boards.
3. Write `{"<node id>": {"name": "...", "size": [w, h]}, ...}` and run the checker against it.
4. Act on what it reports, then update the manifest and its `pulled` date in the same change.

What each finding means:

| | |
|---|---|
| `DRIFT-01` new board | A layout was added. Decide whether the system needs a recipe for it, then **record the decision in `boards`** with a `reason`, even if the answer is no. An undecided board gets re-raised every refresh and eventually ignored |
| `DRIFT-02` renamed | Harmless. The manifest keys on the node id precisely so a rename cannot break anything |
| `DRIFT-03` resized | **Serious.** Every measurement taken from that board is suspect and the normalisation may no longer apply. Re-pull the board and re-verify the recipe built from it |
| `DRIFT-04` board gone | If a recipe is built from it, the recipe now reproduces something that does not exist. Decide whether to keep it as a system layout or retire it |

**The artboard is not uniform, so check the board size before normalising anything.** Most
boards are authored at 1940.4 × 1092.4 and normalise by sx 0.989487, sy 0.988649. Board
`1659:1020`, which recipe 10 comes from, is **already 1920 × 1080**: its child coordinates are
final and applying the factors to them introduces a 1% error. That exception is declared in
the manifest and `ART-02` fails any board that is off-size without one.

**Two boards are currently uncovered**, both recorded with reasons in the manifest:
`1659:898` and `1659:1059`. `1659:1417` "Thank you" is out of scope by direction.

---

### 5. The order of work

```bash
# 0. environment   once per machine, and after any reinstall
python3 scripts/doctor.py
# 0b. LOOK AT THE SYSTEM   once, before your first deck, and after any token change
python3 scripts/teardown.py -o WWT-teardown.html       # every token as a specimen. Open it
# 1. plan          narrative-crafter -> slide-planner
# 2. build         copy geometry from assets/recipes.html, tokens from assets/system.css
python3 scripts/lint_source.py deck.html               # 30ms, no dependencies, runs anywhere
python3 scripts/inline_assets.py deck.html -o WWT-Deck.html
python3 scripts/wwt_validate.py WWT-Deck.html          # 0 FAIL, every WARN with a reason
# 3. export        only if PPTX was asked for
python3 scripts/export_pptx.py WWT-Deck.html -o WWT-Deck.pptx
python3 scripts/verify_pptx.py WWT-Deck.pptx --html WWT-Deck.html
# 4. after any rule or threshold change
python3 scripts/selftest.py                            # control clean, 19 gaming moves caught,
                                                       # and the export's paint order checked for real (REG-43)
# 5. after any change to system.css
python3 scripts/tokens.py                              # regenerate the token export
# 6. periodically      re-pull the Figma source and diff (section 4c)
python3 scripts/check_provenance.py                    # also proves the docs match the code
```

**Nothing ships without 0 FAIL from `wwt_validate.py`, and no PPTX ships without 0 FAIL from
`verify_pptx.py`.** Neither is optional and neither takes a minute.

### 6. Where the real answers live

`SKILL.md` summarises. The summary has been lossy before: section 12 named a mesh on 1 of 20 recipe
rows when 10 recipes carry one, and readers building from that table invented their own geometry.

**Copy from the files, not from the summary.**

| Want | Open |
|---|---|
| **The system, shown rather than described** | `scripts/teardown.py`, then open what it writes. Start here |
| The stylesheet, every token and component | `assets/system.css` |
| The tokens, for anything that is not this skill | `assets/tokens.json`, `assets/tokens.css`. Generated; see the caveat below |
| The geometry of all twenty recipes | `assets/recipes.html`, each with a generated node-id comment |
| Which Figma node every recipe came from | `assets/provenance.json` |
| Photography: id, family, crops, pixels, scrim | `assets/manifest.json` |
| What correct looks like, rendered | the spec book HTML that ships alongside |
| **How to cut a document down to a deck** | `references/triage.md`. Read it before building from prose |
| **How this system has actually failed** | `references/failure-modes.md`. Read it once |

**On the token export.** `assets/tokens.json` and `assets/tokens.css` are generated from
`system.css` by `scripts/tokens.py`, so Figma, a web team, an email template or another LLM
can consume the brand's colour and type without reading this file. They are a **palette, not
the system**: no slot assemblies, no recipe geometry, no density floors, no crop lists, no
export path, no validator. A deck built from `tokens.css` alone will be on-palette and
off-system, which is most of the way to the 91-slide RFP failure. Send anyone building a deck to
`recipes.html` and the validator instead. Regenerate after any edit to `system.css`;
`check_provenance.py` fails on a stale export (`GEN-01`).

---

### What ships in this skill

The assets are bundled, with one exception: **the Aptos fonts are not in the package.** They are
Microsoft's and this plugin is published publicly. `scripts/brand_assets.py` finds them on the
machine, and `doctor.py` reports them. Nothing else needs to be re-derived, re-exported or asked for.

```
assets/system.css             THE STYLESHEET. One copy. Edit this, not a duplicate
assets/tokens.json            GENERATED token export, for tools that are not this skill
assets/tokens.css             GENERATED custom properties only, no layout. A palette, not the system
assets/teardown.json          the prose the teardown page asserts. Values come from tokens.json
assets/recipes.html           GENERATED from the spec book source. The twenty recipes, real geometry
assets/spec-chrome.css        the reference document's own furniture, not part of the system
scripts/brand_assets.py       finds the Aptos cuts on this machine (NOT SHIPPED)
assets/export/*.png           decoration baked flat for PPTX (see section 17)
assets/manifest.json          19 photographs: id, family, crops, pixels, ratio
assets/photos/*.jpg           the library itself, sized for the 1920 canvas
assets/vectors/               mesh-diag, mesh-center, mesh-h, mesh-dark, logo-full,
                              bug-mark, bug-mark-white, arrow-red, x-big,
                              bug-intersect, pattern-source, flex-triangle,
                              brandx-cover (the cover X, one group)
assets/icons/manifest.json    497 marks from Blue Steel 3.0: names, provenance,
                              mono flag, branded flag. Small, so the fast lint
                              can parse it. THIS is what ICO-01 validates against
assets/icons/icons.json       the markup, one file rather than 497. A package is
                              capped at 200 files and the loose set made it 610
assets/components/            recipe 14 parts: rings, chevron, rule, matrix,
                              brandx10, three icons
scripts/doctor.py             RUN FIRST. Reports what this machine can actually enforce
scripts/check_package.py      RUN BEFORE SHIPPING. 200-file cap, junk, entry point
scripts/check_documents.py    proves the two reference documents agree with the CSS
                              and with each other. build.py runs it for you
scripts/teardown.py           RUN SECOND. Writes the system as one page of live specimens
scripts/tokens.py             regenerates the token export from system.css. --check for staleness
assets/provenance.json        THE SOURCE MAP. Every recipe's Figma node id, every board,
                              every artboard exception, and the date of the last pull
scripts/check_provenance.py   checks the map against itself, and against a fresh pull
scripts/lint_source.py        static markup lint, 30ms, zero dependencies, hookable
scripts/browser.py            starts the installed Chrome or Edge, Playwright's Chromium as fallback
scripts/wwt_validate.py       the validator in section 14
references/triage.md          worked examples of cutting a document down to a deck
references/failure-modes.md   every way this system has failed, and what closed each one
scripts/verify_pptx.py        refuses a screenshot deck: live text, fonts, no flattening
scripts/selftest.py           proves the rules catch gaming and leave good work alone
scripts/gaming_fixtures.py    the adversarial decks selftest.py runs
scripts/calibrate.py          re-derives the deck-level ratios from accepted decks
scripts/roles.json            worked example of a roles override file
scripts/inline_assets.py      resolves {{IMG_*}}, {{SYSTEM_CSS}} and friends into one file,
                              and injects the stage-scaling script (see REG-15)
scripts/bake_export_assets.py re-renders assets/export from the live CSS
scripts/export_pptx.py        HTML -> PPTX, live text, baked decoration
```

Two layers. The **slot grid** is the primitive layer: any layout is an assembly of six slots. The
**recipes** are twenty documented assemblies covering the source layouts.

---
