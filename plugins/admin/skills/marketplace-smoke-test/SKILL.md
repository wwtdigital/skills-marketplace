---
name: marketplace-smoke-test
description: >
  Confirm the WWTDigital skills marketplace is installed and working end to end: the
  plugin loaded, its skills are visible, and bundled scripts run. Use when someone says
  "test the skills marketplace", "is the wwt-digital marketplace working", "smoke test the
  plugin install", or "did my skills install correctly". Reports which install path is in
  use (plugin or standalone .skill) and the installed versions. Not for validating a skill
  you are writing; use wwt-skill-author for that.
metadata:
  owner: scott.cullum@wwt.com
  category: admin
  status: draft
  connectors: []
  version: 0.1.3
---

# Marketplace Smoke Test

A tiny skill that exists to prove the marketplace pipeline works: install, skill discovery,
bundled scripts, and version reporting. Safe to run anywhere; it only reads its own files.

## Steps

1. Run the bundled script from this skill's base directory:
   ```
   python3 scripts/report.py
   ```
   It prints JSON with the skill version, the plugin name and version (if installed as a
   plugin), and the install path.
2. Report the result to the user as a short table:

   | Check | Result |
   | --- | --- |
   | Skill loaded | yes |
   | Bundled script ran | yes / no (with the error) |
   | Install type | `plugin` or `standalone` |
   | Skill version | from the script output |
   | Plugin version | from the script output, or n/a |

3. **Verify:** the `skill_version` the script printed must match the `metadata.version` in
   this SKILL.md's frontmatter. If they differ, the install is stale: tell the user to run
   `/plugin marketplace update wwt-digital` and reinstall. See
   [references/troubleshooting.md](references/troubleshooting.md) for other failures.

## Guardrails

- Read-only. Never modify files, settings, or installed plugins.
- If `python3` is unavailable, say so and report the other checks from what you can see.
