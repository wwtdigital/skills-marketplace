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
| [`pursuit-intel-brief`](skills/pursuit-intel-brief/SKILL.md) | Build a supplemental intel brief for a WWT Digital pursuit at any stage (RFP, RFI or nothing yet): reads the pursuit channel, Notion space and SharePoint, researches the client, sizes the deal against past SOWs, checks every claim in our material against wwt.com, and publishes what's new, the positioning angles it supports, and what would blow up if the client checked. |

This bundle has no MCP servers, so it installs without connecting anything. `pursuit-intel-brief` reads
Slack, Notion and Microsoft 365 through the connectors you already have in Claude.

Need to scan a company's digital presence? `brand-scan` used to live here. It moved to its own plugin
because it brings the brandscanner MCP server:
`/plugin install wwtdigital-brand-scan@wwtdigital`.

## Owners

Listed in [`CODEOWNERS`](../../.github/CODEOWNERS). Owners review every change to this plugin.
