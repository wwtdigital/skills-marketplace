---
name: "wwtdigital-design-doctor"
description: "Check what this machine can actually enforce for the WWT design system, and report whether a deck built here will be validated, lint-checked only, or unchecked. Use when starting any WWT deck (run it before building); when the user asks whether the validator will run, why their output differs from someone else's, or what they need installed, including whether the Aptos fonts are on the machine; when a WWT script fails to launch; and when handing a deck over and needing to state honestly how much of it was checked. Not for checking a finished deck's design (that is the design system's validator)."
license: Proprietary
metadata:
  owner: toby.gerber@wwt.com
  category: presentation
  status: beta
  connectors: []
  version: 4.11.0
---

# WWT design system doctor

Report what this environment can enforce, then say plainly what the person may and may not
claim about a deck built here.

## Why this runs first

The difference between a good and a bad result from the WWT design system has turned out to
be mostly environmental. Everything that enforces the rules is a Python script driving
headless Chromium. Two people can read the same specification and produce very different
decks, because one of them can execute it and the other cannot, and nothing told either of
them which one they were.

A 91-slide deck went to a client with 12% photography, 2% mesh usage, 8% median content
coverage, "Lorem ipsum" on one slide and no live text anywhere in the file, and it was
described as built on the design system. Most of those defects have rules against them. None
of the rules ran.

## What to do

Run the doctor:

```bash
python3 "${CLAUDE_PLUGIN_ROOT}/skills/wwtdigital-design-system/scripts/doctor.py"
```

Report the verdict to the user in plain language, then act on it. **First, if the doctor
prints BLOCKED**, the Aptos fonts are missing. They are Microsoft's and the plugin does not ship
them, so no deck can be built until they are installed. Relay the fix the doctor prints
(`python3 scripts/brand_assets.py` shows the detail) and stop there. Do not substitute another font.

**ENFORCED.** Everything runs. Proceed normally and follow `THE CONTRACT` in the design
system skill. The deck will be gated by `wwt_validate.py` before it ships and by
`verify_pptx.py` if a PowerPoint is produced.

**PARTIAL.** The static lint runs; the rendering validator does not. Continue, but tell the
user explicitly which rules are live and which are not, and repeat it when handing the deck
over. Offer the two install commands the doctor prints, because getting to ENFORCED is
usually thirty seconds of work rather than a project. Never describe a PARTIAL deck as
validated.

**DOCUMENTATION ONLY.** Say so before building anything. The person has a stylesheet and a
reference document, which is genuinely useful, but nothing is being checked and the output
must not be described as validated. Ask whether they want to install the prerequisites or
proceed knowingly.

## Figma

**Report Figma as optional, because it is.** The twenty recipes ship with their real measured
geometry, so composing a deck needs no Figma connection at all. Only two jobs need it:
reproducing a specific frame somebody points at, and adding or correcting a recipe.

Getting this emphasis wrong is actively harmful. Someone told they are missing a prerequisite
starts guessing at geometry to compensate, and guessing at geometry has produced three of this
system's worst defects. Someone told they are on the normal path composes from the recipes and
gets a correct deck.

The doctor cannot detect an MCP server from inside a script. Check the session's own tool list
for `get_design_context` and report what you find:

**Present.** Say that frame reproduction is available as well as recipe composition.

**Absent.** Say that recipe composition is available, which is most work, and that frame
reproduction is not. Do not ask for a Figma link; a link nobody can open is worse than no
link. Mention the one-time sign-in only if they want frame reproduction: the plugin declares
Figma's remote server at `https://mcp.figma.com/mcp`, and connecting is `/mcp`, select
**figma**, **Authenticate**, **Allow Access**.

Either way: **nothing is invented.** Geometry comes from the node, with its id cited, or from
`assets/recipes.html`, with the recipe number cited. Never cite a node id for geometry that
came from a recipe.

## Do not

Do not proceed silently past a PARTIAL or DOCUMENTATION verdict. The failure this exists to
prevent was not somebody ignoring a rule, it was somebody believing sixty rules were being
enforced when none of them were.
