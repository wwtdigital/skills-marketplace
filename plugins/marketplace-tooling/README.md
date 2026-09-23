# Marketplace Tooling

Helpers for contributing to this marketplace: author a new skill in the WWT Digital format and check it before opening a PR.

Install:

```
/plugin install marketplace-tooling@wwt-digital
```

## Skills

Each subfolder of `skills/` is one skill. See the [contribution guide](../../CONTRIBUTING.md) to add one.

| Skill | What it does |
| --- | --- |
| `wwt-skill-author` | Turn a workflow into a marketplace skill, run the checks, draft the PR |
| `marketplace-smoke-test` | Confirm the marketplace install works end to end (draft; test skill) |

## Owners

Listed in [`CODEOWNERS`](../../.github/CODEOWNERS). Owners review every change to this plugin.
