---
name: "wwtdigital-design-system"
description: "Build WWTDigital presentations, slides, decks, and branded visual documents using the Figma-derived WWT design system v4.10, and validate any output against it. Use when the user asks for a WWT, WWTDigital or WWT Digital slide, deck, presentation, pitch, divider, cover, or branded HTML/PPTX visual; when they say \"match our template\", \"use the WWT brand\", \"apply the design system\", or \"make it look like WWT\"; when composing a custom WWT slide layout no template covers; or when checking a WWT deck for design-system compliance. Consult this before writing any WWT-branded markup. Not for other brands, generic slide advice, or documents that are not visual (use the presentation skills for copy)."
license: Proprietary
metadata:
  owner: toby.gerber@wwt.com
  category: presentation
  status: beta
  connectors: [figma]
  version: 4.11.0
---

# WWTDigital Presentation Design System v4.10

Source of truth: Figma file `lZ1TThUNRxNN6junV3Sxnk`, section `1659:786` **"Source Files"**,
container frame `1659:787` "Cover 4", holding **25 layout boards**. All values measured, then
normalized to a **1920 × 1080** canvas and an 8px rhythm.

Every board, every recipe's node id and every artboard exception is recorded in
`assets/provenance.json` and checked by `scripts/check_provenance.py`. **That file, not this
sentence, is the source map.** This line said the frame was called "Logo Bug Test" for several
revisions; it is not, and nothing could have caught that because a name in prose is not
checkable.

---

# How this skill is laid out

The system is long, so it lives in `references/`. The section numbers inside those files are
unchanged, so "section 14" or "REG-23" means the same thing wherever it is cited.

**Before anything else, read `references/contract.md` end to end.** It is the page that used to
open this file: the defaults, the ratios, the anti-gaming doctrine, the planning gate, how to
treat Figma, the order of work, and what ships (and what does not). Do not build from memory of
it and do not skim it.

| Read | File | Holds |
|---|---|---|
| **Always, first** | `references/contract.md` | THE CONTRACT, sections 1 to 6 |
| While building | `references/system.md` | 0 How to work, 1 Tokens, 2 Canvas and grid, 3 Typography (Aptos), 4 Colour, 5 Gradients, 6 Space, 7 Photography, 8 Background patterns, 9 Logo, 10 Components, 11 Layout slots, 12 The twenty recipes, 13 Pre-flight checklist, 13b Rhythm |
| Before handing over | `references/validation-and-export.md` | 14 Validation layer (the rule table), 17 PPTX export |
| When changing the system | `references/governance.md` | 15 Governance, version history |
| When a rule surprises you | `references/regression-guards.md` | 16 Regression guards, REG-01 onward |
| Before building from prose | `references/triage.md` | Cutting a document down to a deck |
| Once | `references/failure-modes.md` | Every way this system has failed |

## Before the first deck on a machine

Run the doctor (`python3 scripts/doctor.py`, or the `wwtdigital-design-doctor` skill). **The Aptos
fonts are not shipped with this plugin**; they are Microsoft's, and `scripts/brand_assets.py` finds
them on the machine. If the doctor says BLOCKED, relay its fix and stop. Never substitute another
typeface.

## The gates, which the contract explains

Nothing ships without 0 FAIL from `scripts/wwt_validate.py`, and no PPTX ships without 0 FAIL from
`scripts/verify_pptx.py`. Check both, report the output, and say which rules could not run if the
doctor's verdict was not ENFORCED.
