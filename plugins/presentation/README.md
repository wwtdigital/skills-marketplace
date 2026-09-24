# Presentation

Skills for anything you put in front of people: decks, documents, reports and copy, in the WWT house style.

Install:

```
/plugin install presentation@wwtdigital
```

## Skills

Each subfolder of `skills/` is one skill. See the [contribution guide](../../CONTRIBUTING.md) to add one.

| Skill | What it does |
| --- | --- |
| `humanizer` | Rewrites AI-sounding text so it reads like a person wrote it (from Toby Gerber) |

Building WWT-branded decks? The design system is a separate add-on, because it brings the
Figma MCP server and a toolkit with its own one-time setup: `/plugin install wwtdigital-design@wwtdigital`.

## MCP servers

Installing this plugin also connects these MCP servers. The first time a tool is used, run `/mcp` and sign in (OAuth); no keys are stored in the plugin.

| Server | What it does |
| --- | --- |
| `artifact-publisher` | Publish HTML pages and reports as shareable, access-controlled links. |

## Owners

Listed in [`CODEOWNERS`](../../.github/CODEOWNERS). Owners review every change to this plugin.
