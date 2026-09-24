# Research

Skills for finding things out and making sense of them: desk and market research, interviews, analysis and synthesis.

Install:

```
/plugin install research@wwtdigital
```

## Skills

Each subfolder of `skills/` is one skill. See the [contribution guide](../../CONTRIBUTING.md) to add one.

| Skill | What it does |
| --- | --- |
| [`brand-scan`](skills/brand-scan/SKILL.md) | Run or read a brandscanner assessment of a company: security posture, tech stack, app reviews, public financials, cohort benchmarks and the saved scorecard. |

## MCP servers

Installing this plugin also connects these MCP servers. The first time a tool is used, run `/mcp` and sign in (OAuth); no keys are stored in the plugin.

| Server | What it does |
| --- | --- |
| `brandscanner` | Brand research: scorecards, tech stack, security posture, app reviews and public financials. Driven by the [`brand-scan`](skills/brand-scan/SKILL.md) skill. |

## Owners

Listed in [`CODEOWNERS`](../../.github/CODEOWNERS). Owners review every change to this plugin.
