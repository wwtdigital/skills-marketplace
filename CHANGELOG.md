# Changelog

What changed in the marketplace itself: the site, how people install, and the checks behind it.
Changes to the skills and plugins are in the [catalog](https://skills-marketplace.wwtdigital.io/catalog).

Newest first. Dates are the maintainer's local date.

## 2026-09-30

**Site**

- Selecting a plugin card and copying it as text now keeps the connector names ("Needs Notion",
  "Figma included"). The logos are still images; the words sit beside them as hidden text, which
  screen readers read too.
- The install tabs now drive the rest of the page. On the Cowork / Desktop tab, each plugin card and
  skill page shows where to click in Customize (Plugins, Discover, the plugin, Add) instead of a
  `/plugin install` command, which is a Claude Code command. The tab you pick is remembered in your
  browser.

**Install**

- The five category bundles no longer include MCP servers, so installing any of them connects nothing.
  Publishing a page and scanning a brand moved into their own opt-in plugins. The details and what to
  do if you used them are in the [catalog](https://skills-marketplace.wwtdigital.io/catalog).
- The contribution guide now says the same: a skill that needs an MCP server goes in an add-on plugin
  that brings the server.

## 2026-09-28

**Site**

- Connector logos are each service's own colour favicon, saved in the repo and served from the site, so
  nothing is fetched while someone browses. A skill that uses a connector with no saved logo gets a
  plug icon, and the build log says which one is missing.

**Downloads**

- A skill that needs files from the rest of its plugin (the two deck design skills) is no longer offered
  as a standalone `.skill`. Its card says Bundle and downloads the whole plugin.

## 2026-09-25

**Site**

- Light and dark mode toggle in the header. It follows your system setting until you pick one.
- Skill cards and skill pages show the connectors a skill needs as icons.

## 2026-09-24

**Install**

- The marketplace was renamed from `wwt-digital` to `wwtdigital`. If you added it before this date, run
  `/plugin marketplace remove wwt-digital`, add it again, and reinstall the plugins you use.

**Checks**

- Every skill now has trigger tests (`claude plugin eval`), and the build fails if a skill has none. The
  tests stay out of downloads.
- A skill that needs a connector must say what to do when it isn't connected. The site labels each
  connector "Needs X" or "X included".

**Site**

- Added Vercel Web Analytics.

## 2026-09-23

Launch.

- The site went live at skills-marketplace.wwtdigital.io, built with Next.js on Vercel: a home page with
  install tabs, a page for every skill, and a contribute page rendered from `CONTRIBUTING.md`.
- Four ways in: Claude Code from GitHub, Claude Code from the site's marketplace file with no GitHub
  account (each plugin is a zip with a checksum), Cowork / Desktop through Customize, and one-skill
  `.skill` downloads.
- Every deploy runs strict checks on every plugin and skill and enforces version bumps against the live
  catalog. A failed check keeps the last good site up.
- The repo was made public so installing needs no account. Maintainers treat that as a for-now decision.
