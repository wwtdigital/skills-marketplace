# WWTDigital Publish Page

Publish an HTML or Markdown page as a shareable, access-controlled link, and manage who can open it:
password gate, expiry, per-person share links, revocation.

This is an add-on to the [Presentation](../presentation/README.md) bundle. It installs separately
because it brings an MCP server, and the Presentation bundle's other skills shouldn't depend on one.

Install:

```
/plugin install wwtdigital-publish-page@wwtdigital
```

## Skills

Each subfolder of `skills/` is one skill. See the [contribution guide](../../CONTRIBUTING.md) to add one.

| Skill | What it does |
| --- | --- |
| [`publish-page`](skills/publish-page/SKILL.md) | Publishes an HTML or Markdown page as a shareable, access-controlled link via `artifact-publisher`, and manages who can open it |

## MCP servers

Installing this plugin also connects this MCP server. The first time a tool is used, run `/mcp` and sign in (OAuth); no keys are stored in the plugin.

| Server | What it does |
| --- | --- |
| `artifact-publisher` | Publish HTML pages and reports as shareable, access-controlled links. Used by `publish-page`. |

## Owners

Listed in [`CODEOWNERS`](../../.github/CODEOWNERS). Owners review every change to this plugin.
