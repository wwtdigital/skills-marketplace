---
name: marketplace-smoke-test
description: >
  Confirm the WWTDigital skills marketplace is installed and working end to end: the
  plugin loaded, its skills are visible, and the installed versions are current. Use when
  someone says "test the skills marketplace", "is the wwtdigital marketplace working",
  "smoke test the plugin install", or "did my skills install correctly". Reports which
  install path is in use (plugin or standalone .skill) and the installed skill and plugin
  versions, by reading its own files; there is nothing to run and no Python needed. Not
  for validating a skill you are writing; use wwtdigital-skill-author for that.
metadata:
  owner: scott.cullum@wwt.com
  category: admin
  status: beta
  connectors: []
  version: 0.2.0
---

# Marketplace Smoke Test

A tiny skill that exists to prove the marketplace pipeline works: install, skill discovery
and version reporting. Safe to run anywhere; it only reads its own files and needs no
interpreter of any kind.

## Steps

1. Find this skill's folder: the directory this `SKILL.md` was loaded from (Claude Code
   reports it as the skill's base directory). Read the file and take `metadata.version`
   from its frontmatter. Read it from the file, not from memory.
2. Look for the plugin manifest at `../../.claude-plugin/plugin.json` relative to that
   folder (installed plugins are laid out as `<plugin>/skills/<skill>/`).
   - If it exists, the install type is **plugin**: read its `name` and `version`.
   - If it doesn't, the install type is **standalone** (a downloaded `.skill` file), and the
     plugin fields are `n/a`.
3. Report the result to the user as a short table:

   | Check | Result |
   | --- | --- |
   | Skill loaded | yes |
   | Install type | `plugin` or `standalone` |
   | Skill version | `metadata.version` from step 1 |
   | Plugin | `name` from step 2, or n/a |
   | Plugin version | `version` from step 2, or n/a |
   | Path | the skill folder from step 1 |

4. **Verify:** for a plugin install the manifest `name` must be `admin`; anything else means
   the skill was loaded from an unexpected place, so say so and show the path. Then compare
   the skill version with the one shown at
   https://skills-marketplace.wwtdigital.io/skills/marketplace-smoke-test (open it if you
   can, or ask the person to). If the installed one is lower, the install is stale: tell the
   user to run `/plugin marketplace update wwtdigital` and reinstall the plugin. See
   [references/troubleshooting.md](references/troubleshooting.md) for other failures.

## Guardrails

- Read-only. Never modify files, settings, or installed plugins.
- If a file can't be read, report the checks you could do and say which one failed and why.
