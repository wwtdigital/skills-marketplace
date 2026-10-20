# Tech

Skills for engineers and technologists: code review, architecture documentation, repo hygiene, prototyping.

Install:

```
/plugin install tech@wwtdigital
```

## Skills

Each subfolder of `skills/` is one skill. See the [contribution guide](../../CONTRIBUTING.md) to add one.

| Skill | What it does |
| --- | --- |
| `figma-design-to-code` | Implement a Figma design as code: read tokens and measurements from the Figma UI with playwright-cli, build against a token layer, verify with computed styles and screenshots |
| `wave-planning` | Plan a project or large feature as dependency-ordered Waves → Stories, with every acceptance criterion mapped to the test that proves it, anchored to a reality inventory of the codebase |
| `wave-review` | End-of-wave checkpoint: verify each story's acceptance criteria, update the plan in place, reconcile drift, and re-check the next wave's dependencies |
| `wwtdigital-gated-artifact-site` | Host a Claude HTML artifact as its own password-gated site on the WWTD Vercel team at `<name>.wwtdigital.io`, with link previews, Vercel Analytics and security headers, from the `gated-artifact-site` template repo (draft) |

## Owners

Listed in [`CODEOWNERS`](../../.github/CODEOWNERS). Owners review every change to this plugin.
