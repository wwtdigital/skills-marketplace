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
| `humanizer` | Rewrites AI-sounding text so it reads like a person wrote it; ask for it ("humanize this", "de-AI this") (from Toby Gerber) |

This bundle has no MCP servers, so it installs without connecting anything.

Two add-ons install separately, because each brings something the bundle shouldn't depend on:

- Building WWT-branded decks? The design system has a toolkit with its own one-time setup:
  `/plugin install wwtdigital-deck-design@wwtdigital`.
- Need to publish a page as a shareable link? `publish-page` used to live here. It moved to its own
  plugin because it brings the artifact-publisher MCP server:
  `/plugin install wwtdigital-publish-page@wwtdigital`.

## Owners

Listed in [`CODEOWNERS`](../../.github/CODEOWNERS). Owners review every change to this plugin.
