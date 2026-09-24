# WWTDigital Design System

The WWTDigital presentation design system, packaged so that installing it gives you the
whole thing rather than half of it. One piece is installed separately, once per machine: the
**Aptos fonts**, which are Microsoft's. See First run.

## What you get

**Two skills.**

`wwtdigital-design-doctor` reports what your machine can actually enforce. **Run it first.** It ends
on one of three verdicts: ENFORCED, PARTIAL, or DOCUMENTATION ONLY. Knowing which one you
are is the single most useful thing in this package, because a deck built under PARTIAL is
not a validated deck and should not be described as one.

`wwtdigital-design-system` is the system itself. Tokens, a twelve-column grid on a
1920 × 1080 canvas, twenty layout recipes with their real geometry, four grounds including a
dark emphasis ground capped at one slide in five, nineteen approved photographs with measured
scrim recommendations, 497 icons from Blue Steel 3.0 that inherit the slide's
ink, the Aptos type ladder, an HTML-to-PowerPoint exporter that produces live
editable text, and a validator with about seventy-eight measured rules, every one of them
implemented and documented (check_provenance.py proves it in both directions), including craft rules for panel
insets, dead space inside a box, the bug variant against its measured backdrop, and a check
that no component has been reinvented under a new name. Every recipe traces to a
Figma node id in `assets/provenance.json`, with a documented refresh procedure.

**A hook.** Every time a `.html` file containing slide markup is written or edited, a static
lint runs against it. It takes about 30 milliseconds, needs nothing but the Python standard
library, and catches continuation slides, placeholder copy, an inverted panel on a white
ground, a centred headline off the canvas axis, a mesh nested inside a container, a
side-by-side set with unequal bottoms, retired classes and missing alt text.

The hook **reports, it does not block.** It can never wedge your work. To make it blocking,
remove `|| true` from the end of the command in `hooks/hooks.json`.

**An optional Figma connection.** `.mcp.json` declares Figma's remote MCP server for the two
jobs that need it. **Everything else works without it**, because the recipes carry their own
geometry. One OAuth sign-in, no local app. See below.

## Install

In Claude Code:

```
/plugin marketplace add wwtdigital/skills-marketplace
/plugin install wwtdigital-design@wwtdigital
```

It is a separate plugin rather than part of the `presentation` bundle because it brings a hook
and the Figma MCP server with it, which only people building WWT decks want.

## First run, in order

```bash
python3 "${CLAUDE_PLUGIN_ROOT}/skills/wwtdigital-design-system/scripts/doctor.py"
```

**Fonts.** On a Mac with Microsoft 365 there is usually nothing to do: the five sans cuts are
read from inside PowerPoint. Aptos Serif (pull quotes only) is an Office cloud font; use it once
in PowerPoint and Office downloads it. Anywhere else, install the family from
[Microsoft](https://www.microsoft.com/en-us/download/details.aspx?id=106087), or put the `.ttf`
files in `~/.wwtdigital-design/fonts` (or point `WWT_FONTS_DIR` at them).

`python3 scripts/brand_assets.py` shows exactly what was found and where.

If the verdict is not ENFORCED the doctor prints the commands that fix it:

```bash
python3 -m pip install --user playwright pillow numpy fonttools brotli python-pptx
python3 -m playwright install chromium
```

If pip refuses with "externally managed environment" (Homebrew Python, recent Linux), install
into a virtualenv instead. Don't override that guard with `--break-system-packages`.

Then read `THE CONTRACT`, the first page of the design system skill. It holds the defaults,
the ratios, the anti-gaming doctrine and the planning gate. Everything after it is reference
you look things up in.

## How to ask for a deck

Full version, with worked examples and the reasoning: `PROMPTING.md`. The
five things that change the output most, if you read nothing else:

1. **Brief it like a designer.** Who is in the room, what you need them to do afterwards, how
   long, and the source material attached rather than described.
2. **Ask for imagery on purpose.** Left alone the default lands too few images. Say you want to
   land near 40% of slides and that images must relate to content, anchor a card or form a real
   background. Asked for vaguely, imagery arrives as corner thumbnails, which is worse than none.
3. **Name the output format in the first message.** PPTX and HTML have different font stories and
   different licence positions. See Licensing below.
4. **Never ask Claude to open the built file.** After inlining it is megabytes of base64. That is
   what the scripts are for, and reading it is the usual cause of hitting a usage limit.
5. **Ask for the measurement, not the opinion.** "Run the validator and paste the output" rather
   than "does this look right". Every defect this system has shipped passed visual review first.

**Model.** Build on Claude Opus 5.5 at `xhigh` effort: a deck build is long-horizon agentic work
and Opus 5.5 defaults to `medium`, a level below where you want it. Claude Fable 5.1 when Opus 5.5
at higher effort still falls short. Claude Sonnet 5 for iterating on a deck that already exists.
Not Haiku, which has a 200K context and no effort setting. The guide explains how to re-derive
this when the lineup changes.

## Figma

`.mcp.json` points at Figma's **remote** MCP server, `https://mcp.figma.com/mcp`. It is the
one Figma recommends, it has the broader feature set, and it does not need the Figma desktop
app running. You authenticate once through Figma's OAuth flow: run `/mcp`, pick **figma**,
choose **Authenticate**, then **Allow Access**.

An earlier version of this plugin pointed at the desktop server on `127.0.0.1:3845`, which
only exists while Figma desktop is open with Dev Mode MCP enabled. It refused the connection
on the first machine that installed the plugin, which is how we learned to ship the remote
one instead.

**Figma is optional and most work does not need it.** The twenty recipes ship with their real
measured geometry, so composing a deck from them is the normal, complete path. Figma is needed
for two jobs only: reproducing a specific frame somebody points at, and adding or correcting a
recipe.

If Figma is absent the plugin will not ask you for a link, because a link nobody can open is
worse than no link. It says once that it is composing from the bundled recipes, then builds.
If Figma is present and the request names a frame, it pulls the node and cites the node id.

Either way **nothing is invented.** Geometry comes from a node with its id cited, or from a
recipe with its number cited, and the two are never confused. Guessing at geometry has
produced three of this system's worst defects.

## Working on the system itself

```bash
cd skills/wwtdigital-design-system
python3 scripts/lint_source.py deck.html                 # 30ms, no dependencies
python3 scripts/inline_assets.py deck.html -o Deck.html  # resolve the assets and fonts
python3 scripts/wwt_validate.py Deck.html                # the gate. 0 FAIL, WARNs with reasons
python3 scripts/export_pptx.py Deck.html -o Deck.pptx    # live text, baked decoration
python3 scripts/verify_pptx.py Deck.pptx --html Deck.html # refuses a screenshot deck
python3 scripts/selftest.py                              # after ANY rule change
python3 scripts/check_documents.py Spec.html Teardown.html  # the two references agree
python3 scripts/check_package.py                         # 200-file cap, BEFORE shipping
python3 scripts/calibrate.py good1.html good2.html       # re-derive the deck-level ratios
```

`selftest.py` is the one people skip and should not. It builds thirteen decks that each try
to satisfy a rule while doing no design, proves each one fails, and proves a fourteenth
deck of legitimate work still comes back clean. That negative control is what distinguishes a
strict rule set from a broken one, and it has already caught two rules of ours that were
wrong.

## Where the real answers live

`SKILL.md` summarises. The summary has been lossy before: it named the diamond mesh on one of
twenty recipe rows when ten recipes carry one, and readers building from that table invented
their own geometry. **Copy from the files.**

| Want | Open |
|---|---|
| The stylesheet, every token and component | `assets/system.css` |
| The geometry of all twenty recipes | `assets/recipes.html` |
| Photography: id, family, crops, pixels, scrim | `assets/manifest.json` |
| Icons: every name, its Figma component, branded or not | `assets/icons/manifest.json` |
| How to cut a document down to a deck | `references/triage.md` |
| Every way this system has failed | `references/failure-modes.md` |

## Licensing, read once

This plugin is published on a public marketplace, so it ships **no Aptos files**.
`scripts/brand_assets.py` finds them on your machine.

Aptos is proprietary to Microsoft. A Microsoft 365 subscription, or Microsoft's own download,
grants use of the font, not the right to redistribute it, self-host it as a webfont or inline it
into something handed to a client. Inlining it into an HTML deck that goes to a customer is a
different act from using it internally. If a deliverable leaves WWT as HTML rather than PPTX or
PDF, confirm the licence position first. Document embedding in PPTX and PDF is the normal and
permitted route (every Aptos cut is marked Editable Embedding).

Photography in `assets/photos` is WWT brand material. Partner marks are third-party
trademarks and are not included.

---

v4.10.0. Major at 4.0, because the rule set gained a deck level and two rules changed what they
measure. Version history and every regression guard are in the design system skill.
