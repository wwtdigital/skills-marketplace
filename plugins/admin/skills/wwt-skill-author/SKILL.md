---
name: wwt-skill-author
description: >
  Author a new Claude skill for the WWT Digital skills marketplace, or get an existing
  skill ready to submit. Use when someone says "make this a skill", "add a skill to the
  marketplace", "turn this workflow into a skill", "package this for the team", or asks
  how to contribute a skill. Produces a SKILL.md in the WWT Digital format inside the
  right category plugin, runs the marketplace validator, and drafts the PR description.
  Not for editing skills that live outside this marketplace.
metadata:
  owner: scott.cullum@wwt.com
  category: admin
  status: beta
  connectors: []
  version: 0.1.2
---

# WWT Skill Author

Turns a repeatable workflow into a skill that passes the marketplace's checks on the
first try. Works for engineers in a checkout of the repo and for non-engineers who will
hand the finished folder to a maintainer.

## Inputs

Ask for these before writing anything (one question at a time):

1. What the skill does, in the user's words, and 3–5 phrases people say when they want it.
2. Which category plugin it belongs to (`presentation`, `research`, `ops`, `admin`,
   `tech`). If unsure, propose one.
3. Which connectors it needs (Slack, Notion, Microsoft 365, GitLab…), if any.
4. An example of a good finished output, if one exists.

## Steps

1. Locate the marketplace root (the folder containing `.claude-plugin/marketplace.json`).
   If not in a checkout, work in a scratch folder and tell the user to zip and send it.
2. Copy `templates/skill-template/` to `plugins/<category>/skills/<skill-name>/`.
   Name in kebab-case; prefix with `wwt-` only if the skill is WWT-brand specific.
3. Write the `description` first. It must answer *what* and *when*, include the trigger
   phrases from step 1, and name exclusions if a neighbouring skill overlaps. Keep it
   under 1,024 characters.
4. Fill the body. Prefer numbered steps over prose. Put anything longer than a screen
   into `references/` and link to it. Put deterministic work into `scripts/`.
5. Add a verification step to the skill's own workflow — every marketplace skill checks
   its output before handing it over.
6. Run `npm --prefix site run validate -- --strict --base origin/main` from the marketplace root
   (after `npm ci --prefix site` once) and fix everything it reports. Then run
   `npm --prefix site run catalog -- --check` to confirm the skill will
   appear correctly on the site.
7. Add a row to the plugin's `README.md` skills table, and bump the plugin's `plugin.json`
   `version` (plus the skill's `metadata.version` if it already existed). Without the plugin
   bump, people who already installed the plugin never get the change.
8. Draft the PR using `.github/PULL_REQUEST_TEMPLATE.md`. Include two or three test
   prompts a reviewer can paste to see the skill trigger.

## Output

A folder `plugins/<category>/skills/<skill-name>/` containing `SKILL.md` and optional
`scripts/`, `references/`, `assets/`; a passing validator run; a PR description.

## Guardrails

- Never put credentials, tokens, customer names or client data in a skill.
- Never commit or push; leave that to the contributor.
- Do not edit other skills in the same PR unless the user asks.

## Examples

**User says:** "Turn my weekly client status email process into a skill for the delivery team."
**Claude does:** asks the four input questions, scaffolds
`plugins/delivery/skills/client-status-report/`, writes the description with triggers like
"status report", "weekly update for the client", runs the validator, drafts the PR.
