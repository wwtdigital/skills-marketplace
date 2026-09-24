---
name: wwtdigital-skill-author
description: >
  Author a new Claude skill for the WWTDigital skills marketplace, or get an existing one
  ready to submit, with or without a git checkout of the repo. Use when someone says "make
  this a skill", "add a skill to the marketplace", "turn this workflow into a skill",
  "package this for the team", or "how do I contribute a skill". Produces a SKILL.md in the
  WWTDigital format (description with trigger phrases, metadata block, numbered steps, a
  connector check, a verification step), then either runs the marketplace validator in a
  checkout or applies its rules by hand as a checklist, and drafts the PR or the
  zip-and-send handoff with test prompts. Not for skills that live outside this marketplace,
  and not for checking whether an install is working; use marketplace-smoke-test for that.
metadata:
  owner: scott.cullum@wwt.com
  category: admin
  status: beta
  connectors: []
  version: 0.2.0
---

# WWTDigital Skill Author

Turns a repeatable workflow into a skill that passes the marketplace's checks on the first
try. There are two ways to contribute, and this skill supports both:

- **In a checkout** of `github.com/wwtdigital/skills-marketplace`: scaffold from the template,
  run the validator, open a PR.
- **No checkout** (most contributors): build the skill folder in a scratch location, apply the
  same rules by hand, zip it, and send it to a maintainer.

Work out which path applies in step 1 and say so before writing anything.

## Inputs

Ask for these one at a time, before writing anything:

1. What the skill does, in the person's own words, and 3–5 phrases people actually say when
   they want it (these become the trigger phrases in the description).
2. Which category it belongs to: `presentation`, `research`, `ops`, `admin` or `tech`. These
   are the only categories. If they're unsure, propose one from the table in the
   [contribution guide](https://skills-marketplace.wwtdigital.io/contribute) and say a
   reviewer can move it.
3. Which connectors it needs (Slack, Notion, Microsoft 365, GitLab, …), if any.
4. An example of a good finished output, if one exists.

## Steps

1. **Pick the path.** Look for a folder containing `.claude-plugin/marketplace.json` and
   `templates/skill-template/` (the current folder or a parent). If found, this is a checkout:
   follow steps 2–9 and then **A**. If not, ask whether they have one; if not, create the
   skill folder in a scratch location (for example `~/Desktop/<skill-name>/`) and follow
   steps 2–9 and then **B**.
2. **Name it.** Kebab-case, and the folder name must equal the frontmatter `name`. Use the
   `wwtdigital-` prefix only when the skill is WWT-brand-specific (WWT templates, WWT process,
   WWT vocabulary); a general-purpose skill gets no prefix. Names must be unique across every
   plugin: check the skills list at https://skills-marketplace.wwtdigital.io (or
   `plugins/*/skills/` in a checkout). Brand spelling is "WWTDigital", no space, everywhere.
3. **Scaffold.** In a checkout, copy `templates/skill-template/` to
   `plugins/<category>/skills/<skill-name>/`. Without one, download
   https://skills-marketplace.wwtdigital.io/downloads/skill-template.zip or write `SKILL.md`
   from the template shape below. Either way, set `name` and cut the `category` and `status`
   option lists in the template down to single values.
4. **Write the description first.** It is the only text Claude reads when deciding whether to
   use the skill. It must say *what* the skill does, *when* to use it with the words
   "Use when" followed by the quoted trigger phrases from input 1, and what it is *not for*,
   naming any neighbouring skill it could be confused with. Keep it under 1,024 characters
   and over 80.
5. **Fill the metadata block:** `owner` (a real @wwt.com address that will answer questions),
   `category` (from input 2), `status: draft` for a new skill, `connectors` (a list, `[]` if
   none), `version: 0.1.0` for a new skill.
6. **Connector check comes first.** If `connectors` lists anything, the skill's first step
   must check whether that connector's tools are available and, if they aren't, tell the
   person how to connect it and stop, rather than answering without it. The build rejects a
   skill that names a connector without this. Use this pattern (it is what
   `wwtdigital-onboarding` in `ops` does under "Before the first answer"):

   > If no <Connector> tools are available, the connector isn't set up. Don't answer from
   > memory. In the Claude app, open **Connectors** in settings, find <Connector>, choose
   > **Connect** and sign in with a WWT account, then ask again. In Claude Code, run `/mcp`
   > to see whether it's listed and signed in. If it isn't offered at all, the workspace
   > admin controls which connectors are available. Then stop.

7. **Fill the body.** Numbered steps, in order, naming the tools used at each one. Keep the
   body under 250 lines: anything longer than a screen goes in `references/` with a link
   from SKILL.md; templates and boilerplate go in `assets/`; deterministic work goes in
   `scripts/`. Don't assume the person running a script has Python (a Mac without developer
   tools opens an install dialog on `python3`); prefer no script, or say what the script
   needs and what to do without it.
8. **Add a verification step** to the skill's own workflow: open the file, recount the
   numbers, run the test. Every marketplace skill checks its output before handing it over.
9. **Guardrails and examples.** Short, specific guardrails (no sending without confirmation,
   no writes to production systems, no invented data). One or two "User says / Claude does"
   examples.

### A. In a checkout

10. Run the checks from the repo root and fix everything they report:
    ```
    npm ci --prefix site                                          # once
    npm --prefix site run validate -- --strict --base origin/main
    ```
    `--strict` turns warnings into errors, exactly as the Vercel build does.
11. Add a row to `plugins/<category>/README.md`'s skills table.
12. Bump versions. `plugin.json` `version` is the release gate: people who already installed
    the plugin get nothing until it rises, and the build fails if the plugin changed without
    it. The skill's `metadata.version` is informational (the site shows it). A **new skill**
    needs the plugin bump only. A **change to an existing skill** needs both.
13. Draft the PR from `.github/PULL_REQUEST_TEMPLATE.md`, with two prompts that should
    trigger the skill and one that shouldn't. The Vercel preview build is the CI. Leave the
    commit, push and PR creation to the contributor.

### B. No checkout

10. Do the validator's checks by hand and show the result as a checklist:
    - `name` is kebab-case and equals the folder name; not already on the site
    - description is 80–1,024 characters, says what, has "Use when" plus quoted trigger
      phrases, and a not-for line
    - metadata has `owner` ending in @wwt.com, `category` (one of the five), `status`,
      `connectors` (a list) and `version`
    - if `connectors` is non-empty, the first step checks for it and says how to connect it
    - body is under 250 lines and includes a verification step
    - no secrets, tokens, client names or PII anywhere in the folder
11. Zip the skill folder (the zip should contain the `<skill-name>/` folder with `SKILL.md`
    inside it, not a loose `SKILL.md`).
12. Tell the person to send the zip to **scott.cullum@wwt.com** or post it in
    **#wwtd-claude-skills**, with two prompts that should trigger the skill and one that
    shouldn't. Draft that message for them. A maintainer adds it to the repo, bumps the
    versions and credits them as the owner.

## Standalone plugins

A skill that brings a hook, an MCP server or a large toolkit that most people in its
category won't want can ship as its own opt-in plugin instead of inside the category bundle
(`wwtdigital-deck-design` is the example). Don't build one unasked: if the skill looks like
it needs that, say so and have the person ask in #wwtd-claude-skills first. See "Standalone
plugins" in the contribution guide.

## Verify before handing over

- Read the description back as Claude would: do the two should-trigger prompts obviously
  match it, and does the shouldn't-trigger prompt obviously not?
- Path A: the validator reported 0 errors, 0 warnings.
- Path B: every checklist line is ticked, and the zip opens to `<skill-name>/SKILL.md`.

## Output

A folder `<skill-name>/` (under `plugins/<category>/skills/` in a checkout) containing
`SKILL.md` and optional `scripts/`, `references/`, `assets/`; either a passing validator run
and a PR description, or a ticked checklist, a zip and a drafted handoff message. Both
include the three test prompts.

## Guardrails

- Never put credentials, tokens, customer names or client data in a skill. Everything in the
  repo is published on the site.
- Never commit or push; leave that to the contributor.
- Do not edit other skills in the same change unless the person asks.
- Do not create a standalone plugin, add an MCP server or add a category on your own.

## Examples

**User says:** "Turn my weekly client status email process into a skill for the ops team."
**Claude does:** asks the four input questions one at a time, finds no checkout, builds
`~/Desktop/client-status-report/SKILL.md` with triggers like "status report" and "weekly
update for the client", walks the checklist, zips the folder and drafts the message to
#wwtd-claude-skills with three test prompts.

**User says:** "Add a skill to the marketplace that summarises our Notion retro pages."
**Claude does:** finds the checkout, scaffolds `plugins/research/skills/retro-summary/` from
the template, sets `connectors: [notion]` and writes the Notion connector check as step 1,
runs the validator, adds the README row, bumps `plugins/research/.claude-plugin/plugin.json`,
drafts the PR.
