# Catalog

What is in the library, and what changed in it. The table is the library as of 2026-10-03. The release
notes under it are newest first. Changes to the site and install paths are in the
[changelog](https://skills-marketplace.wwtdigital.io/changelog).

Anyone who adds or changes a skill adds a line here. Every time a plugin version changes, the entry
looks like `**plugin-name version**` followed by what changed. The build prints a note when a plugin's
current version has no entry.

## The library today

| Plugin | Version | Skills | Brings an MCP server | Owner |
| --- | --- | --- | --- | --- |
| `presentation` | 0.5.0 | `humanizer` 4.1.0 | no | Toby Gerber |
| `wwtdigital-deck-design` (Presentation add-on) | 4.13.1 | `wwtdigital-deck-design` 4.13.0, `wwtdigital-deck-design-doctor` 4.11.0 | Figma | Toby Gerber |
| `wwtdigital-publish-page` (Presentation add-on) | 0.1.0 | `publish-page` 0.1.0 | artifact-publisher | Scott Cullum |
| `research` | 0.5.0 | `pursuit-intel-brief` 1.2.0 | no | Scott Cullum |
| `wwtdigital-brand-scan` (Research add-on) | 0.1.0 | `brand-scan` 0.1.1 | brandscanner | Scott Cullum |
| `ops` | 0.3.3 | `wwtdigital-onboarding` 1.1.1 | no | Staci Powell |
| `admin` | 0.4.3 | `wwtdigital-skill-author` 0.2.1, `marketplace-smoke-test` 0.2.0 | no | Scott Cullum |
| `tech` | 0.3.0 | `figma-design-to-code` 0.1.0, `wave-planning` 1.0.0, `wave-review` 1.0.0 | no | Zak Lampert, Andrew Brydon |

The five category bundles (`presentation`, `research`, `ops`, `admin`, `tech`) bring no MCP servers and no
scripts, so each installs without connecting anything. Anything that does goes in an add-on you opt into.

Skills that read from your own tools say which ones: `pursuit-intel-brief` needs Slack, Notion and
Microsoft 365 connected in Claude, and `wwtdigital-onboarding` needs Notion.

## Release notes

### 2026-10-03

- **tech 0.3.0**: added `wave-planning` 1.0.0 and `wave-review` 1.0.0 (Andrew Brydon). `wave-planning` turns a
  project or large feature into dependency-ordered Waves of Stories, each acceptance criterion tied to the test
  that proves it; `wave-review` is the end-of-wave check that grades a wave against those criteria and updates
  the plan. A repo can set its own plan paths and story IDs in `.claude/wave-conventions.md`. Run
  `/plugin update tech@wwtdigital` to get them.

### 2026-09-30

- **presentation 0.5.0**: `humanizer` only. `publish-page` and the artifact-publisher MCP server moved out.
  If you used `publish-page`, install `wwtdigital-publish-page` (below).
- **research 0.5.0**: `pursuit-intel-brief` only. `brand-scan` and the brandscanner MCP server moved out.
  If you used `brand-scan`, install `wwtdigital-brand-scan` (below).
- **wwtdigital-publish-page 0.1.0**: new add-on. Contains `publish-page` 0.1.0 and the artifact-publisher
  server. Install it with `/plugin install wwtdigital-publish-page@wwtdigital`.
- **wwtdigital-brand-scan 0.1.0**: new add-on. Contains `brand-scan` 0.1.1 and the brandscanner server.
  Install it with `/plugin install wwtdigital-brand-scan@wwtdigital`. `brand-scan` 0.1.1 only changes its
  wording from "the research plugin" to "this plugin".
- **wwtdigital-deck-design 4.13.1**: setup downloads uv from its GitHub release and checks a pinned
  checksum before using it, instead of running a downloaded installer script. The design system itself is
  unchanged.

Why the move: a plugin that needs an exception from corporate IT simply doesn't get installed, and an
MCP server is the kind of thing that can need one. With the servers inside `presentation` and `research`,
one server that couldn't be approved also blocked `humanizer` and `pursuit-intel-brief`. There is no
automatic migration when a skill changes plugins, so anyone who had `publish-page` or `brand-scan`
installed has to install the add-on.

### 2026-09-29

- **tech 0.2.0**: added `figma-design-to-code` 0.1.0 (Zak Lampert). Implements a Figma design as code by
  driving a real browser to read the design's tokens and measurements, then checks the result against the
  design at several widths.
- **research 0.4.2**: `pursuit-intel-brief` 1.2.0 now works at any stage (RFP, RFI or nothing from the
  client yet), checks that Slack, Notion and Microsoft 365 are connected before it starts and asks you to
  sign in if they aren't, and adds two sections to the brief: positioning angles, and the claims in our
  own material that wouldn't survive the client checking them.

### 2026-09-28

- **research 0.4.1**: `pursuit-intel-brief` 1.1.0 reads its internal reference data (comparable deals, rules,
  channel and folder locations) from a team-editable Notion page instead of carrying it in the skill.
- **research 0.4.0**: added `pursuit-intel-brief` 1.0.0, which builds a brief for a pursuit from its Slack
  channel, Notion space and SharePoint folder plus outside research, and publishes only what the team
  doesn't already know.
- **wwtdigital-deck-design 4.13.0**: merged Toby's update. A refreshed library of eighteen approved
  photographs, a shorter router `SKILL.md` with the detail in `references/`, and new scripts for checking
  dependencies and collecting client logos. Still no hooks and no Aptos fonts shipped.

### 2026-09-24

- **wwtdigital-deck-design 4.11.0**: added Toby Gerber's WWT deck design system as its own add-on (first
  named `wwtdigital-design`). A toolkit that builds and validates WWT-branded slides as HTML and
  PowerPoint, with a one-time setup that needs no Python beforehand and no hooks.
- **presentation 0.4.0**: added `publish-page`, and `humanizer` now loads when you ask for it. **presentation
  0.3.0** added `humanizer` (Toby Gerber).
- **ops 0.3.0**: `wwtdigital-onboarding` tells you when its Notion connector isn't set up. **ops 0.2.0**
  added `wwtdigital-onboarding` (Staci Powell).
- **ops 0.3.1**: `wwtdigital-onboarding` escalates to roles instead of named people, so a person moving on
  is one edit. **admin 0.4.1**: `wwtdigital-skill-author` was updated for trigger tests.
- **admin 0.4.0**: `wwt-skill-author` was renamed `wwtdigital-skill-author`, so the old skill page and
  download are gone, and `marketplace-smoke-test` no longer needs Python.
- **research 0.3.0**: added `brand-scan`, which runs or reads a brandscanner assessment of a company.
- Version-only releases, no change to any skill: **ops 0.3.3**, **admin 0.4.3**, **presentation 0.4.3**,
  **research 0.3.2** and **wwtdigital-deck-design 4.11.2**. Versions were raised when trigger tests were
  taken out of plugin downloads, which changed every plugin's content hash.

### 2026-09-23

- The library started as six plugins by discipline (`brand-and-voice`, `creative-tech`, `data-ai`,
  `delivery`, `engineering`, `marketplace-tooling`) and was replaced the same day by five plugins by
  category: `presentation`, `research`, `ops`, `admin`, `tech`. `marketplace-tooling` became `admin`.
- Added `marketplace-smoke-test` (draft), which checks that an install worked.
- **presentation 0.2.0, research 0.2.0**: shipped the artifact-publisher and brandscanner MCP servers inside
  them. They moved out on 2026-09-30.
