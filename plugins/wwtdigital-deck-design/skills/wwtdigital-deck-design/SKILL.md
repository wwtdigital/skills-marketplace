---
name: "wwtdigital-deck-design"
description: "Build WWTDigital presentations, slides, decks, and branded visual documents using the Figma-derived WWT design system v4.13, and validate any output against it. Use when the user asks for a WWT, WWTDigital or WWT Digital slide, deck, presentation, pitch, divider, cover, or branded HTML/PPTX visual; when they say \"match our template\", \"use the WWT brand\", \"apply the design system\", or \"make it look like WWT\"; when composing a custom WWT slide layout no template covers; or when checking a WWT deck for design-system compliance. Consult this before writing any WWT-branded markup. Not for other brands, generic slide advice, or documents that are not visual (use the presentation skills for copy)."
license: Proprietary
metadata:
  owner: toby.gerber@wwt.com
  category: presentation
  status: beta
  connectors: [figma]
  version: 4.13.0
---

# WWTDigital Presentation Design System v4.13

Source of truth: Figma file `lZ1TThUNRxNN6junV3Sxnk`, section `1659:786` **"Source Files"**,
container frame `1659:787` "Cover 4", holding **25 layout boards**. Every board, every
recipe's node id and every artboard exception is in `assets/provenance.json`, checked by
`scripts/check_provenance.py`. **That file, not this sentence, is the source map.**

This page is a router. The system is in `references/`, and it used to be here: 2,200 lines
and 137 KB, loaded in full before any work began, on every deck. That is about 35,000
tokens spent before reading the brief. Splitting it is worth roughly 34,000 tokens an
activation, and the token ceiling is the most common complaint about this skill.

**`scripts/skilldoc.py` reassembles these files in order**, so `GEN-02`'s rule table and
`GEN-03`'s contract numbers still read the document as one text. A split cannot make a rule
or a threshold quietly vanish from a check.

## Read this first, always

**`references/contract.md`.** One page. The defaults, the measured ratios, the anti-gaming
doctrine, the planning gate and the pipeline. Everything else is reference you look things
up in. Two decks came back wrong from builders who had this skill open and had never read
that page.

## Then, by what you are doing

| Doing | Open |
|---|---|
| Building a slide: tokens, grid, type, colour, photography, components, recipes | `references/system.md` |
| Running the gates, or exporting to PPTX | `references/validation-and-export.md` |
| Changing a rule, a threshold, an asset, or the version | `references/governance.md` |
| Wondering why a rule is shaped the way it is | `references/regression-guards.md` |
| Cutting a long document down to a deck | `references/triage.md` |
| Every way this system has failed | `references/failure-modes.md` |

## Copy geometry from the files, never from a summary

`assets/recipes.html` has the twenty recipes at their real measured numbers.
`assets/system.css` is the one copy of the stylesheet. A summary table has been lossy
before: it named the diamond mesh on one recipe row when ten carry one, and readers who
built from that table invented their own geometry.

## Before your first deck, once

```bash
python3 scripts/doctor.py                            # what this machine can enforce
python3 scripts/teardown.py -o WWT-teardown.html     # the system, rendered. Open it
```

(Run both through `setup/run.sh` as below, or use the `wwtdigital-deck-design-doctor` skill.)

The doctor answers ENFORCED, PARTIAL or DOCUMENTATION. **If it is not ENFORCED, say so when
you hand the deck over.** Aptos is not shipped with this package: it is Microsoft's, and
`scripts/brand_assets.py` finds it on the machine. If the doctor reports it missing, relay
the fix and stop. Never substitute another typeface.

## How to run the scripts

Never call `python3` directly: on a Mac without Apple's developer tools it opens an install
dialog, and on Windows it is often a Store shortcut. Every `python3 scripts/X.py ...` in these
references means:

```
sh "${CLAUDE_PLUGIN_ROOT}/setup/run.sh" X.py ...                                        # macOS, Linux
powershell -NoProfile -ExecutionPolicy Bypass -File "${CLAUDE_PLUGIN_ROOT}/setup/run.ps1" X.py ...   # Windows
```

If it prints **SETUP NEEDED** (exit 3), the person has not run the one-time setup. Assume they are
not technical. Say in plain words that it is a one-time step of a few minutes, needs no admin
password, and downloads a private copy of Python and its tools (about 330 MB of disk space, more only if they
have neither Chrome nor Edge) into a `.wwtdigital-deck-design` folder in their home folder. Ask before
running it, then run `setup/setup.sh` (Windows: `setup/setup.ps1`) the same way and relay any
"Setup stopped" message as written.

## The gates

Nothing ships with a FAIL from `scripts/wwt_validate.py`, and no PPTX ships with a FAIL from
`scripts/verify_pptx.py`. Run both, paste the output, and say which checks could not run.
A missing package prints SETUP NEEDED and exits 3; that is not a passing deck.
