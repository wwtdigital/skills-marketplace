---
name: skill-template
description: >
  One or two sentences saying WHAT this skill does and WHEN Claude should use it.
  List the trigger phrases people actually say ("review this SOW", "make a status report").
  Say what it is NOT for if there's a nearby skill it could be confused with.
  This field is the only thing Claude reads to decide whether to load the skill — make it count.
metadata:
  owner: your-name@wwt.com
  discipline: creative-tech | engineering | brand-and-voice | delivery | data-ai | tooling
  status: draft | beta | stable
  connectors: []          # e.g. [slack, notion, microsoft-365] — connectors this skill needs
  version: 0.1.0
---

# Skill Name

One paragraph: what problem this solves, who it's for, what the output looks like.

## Inputs

What Claude needs from the user before starting. Which of these should it ask for
up front vs. infer or default?

## Steps

1. Numbered, concrete, in the order Claude should do them.
2. Name the tools or connectors to use at each step.
3. Include the verification step (check the numbers, open the file, run the test).

## Output

Exact shape of the deliverable: file format, structure, tone, length. Point to
`assets/` for templates and `references/` for longer background material.

## Guardrails

Things this skill must never do (send messages without confirmation, write to
production systems, invent data). Keep this short and specific.

## Examples

**User says:** "…"
**Claude does:** …

<!--
Optional folders next to this file:
  scripts/      deterministic helpers Claude can run (Python/Node/shell)
  references/   long docs Claude reads on demand; keep SKILL.md itself short
  assets/       templates, boilerplate, images the output is built from
-->
