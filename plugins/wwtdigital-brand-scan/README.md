# WWTDigital Brand Scan

Run or read a brandscanner assessment of a company: security posture, tech stack, app reviews,
public financials, cohort benchmarks and the saved scorecard.

This is an add-on to the [Research](../research/README.md) bundle. It installs separately because it
brings an MCP server, and the Research bundle's other skills shouldn't depend on one.

Install:

```
/plugin install wwtdigital-brand-scan@wwtdigital
```

## Skills

Each subfolder of `skills/` is one skill. See the [contribution guide](../../CONTRIBUTING.md) to add one.

| Skill | What it does |
| --- | --- |
| [`brand-scan`](skills/brand-scan/SKILL.md) | Run or read a brandscanner assessment of a company: security posture, tech stack, app reviews, public financials, cohort benchmarks and the saved scorecard. |

## MCP servers

Installing this plugin also connects this MCP server. The first time a tool is used, run `/mcp` and sign in (OAuth); no keys are stored in the plugin.

| Server | What it does |
| --- | --- |
| `brandscanner` | Brand research: scorecards, tech stack, security posture, app reviews and public financials. Driven by the [`brand-scan`](skills/brand-scan/SKILL.md) skill. |

## Owners

Listed in [`CODEOWNERS`](../../.github/CODEOWNERS). Owners review every change to this plugin.
