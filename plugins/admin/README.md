# Admin

Everyday admin skills, plus tools for contributing to this marketplace: author a new skill and check an install.

Install:

```
/plugin install admin@wwtdigital
```

## Skills

Each subfolder of `skills/` is one skill. See the [contribution guide](../../CONTRIBUTING.md) to add one.

| Skill | What it does |
| --- | --- |
| `wwtdigital-skill-author` | Turn a workflow into a marketplace skill, with or without a git checkout: writes it in the marketplace format, runs the checks (or walks them by hand), drafts the PR or the zip-and-send handoff |
| `marketplace-smoke-test` | Confirm the marketplace install works end to end: install type, skill and plugin versions, read from its own files (nothing to run) |

## Owners

Listed in [`CODEOWNERS`](../../.github/CODEOWNERS). Owners review every change to this plugin.
