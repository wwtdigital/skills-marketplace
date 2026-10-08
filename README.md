# WWTDigital Skills Marketplace

A shared catalog of Claude skills for WWTDigital, organised by category. Each
category is a **plugin**; each plugin contains one or more **skills**. Install the
bundles you need and Claude picks up the skills automatically in Claude Code and
Cowork.

Browse the catalog and get step-by-step install help at **https://skills-marketplace.wwtdigital.io**.
The site and this repo are for the team: the site asks for the **team access key**, which is pinned
in the team Slack channel along with a link that signs you in, and the repo is private.

## Install

**Claude Code** (any machine, no GitHub account; needs Claude Code 2.1.286 or later)

Add this to `~/.claude/settings.json`, with the key from Slack in place of `<team access key>`
(the site's Install tab shows it filled in), then start a new session:

```json
{
  "extraKnownMarketplaces": {
    "wwtdigital": {
      "source": {
        "source": "url",
        "url": "https://skills-marketplace.wwtdigital.io/marketplace.json",
        "headers": { "Authorization": "Bearer <team access key>" }
      },
      "autoUpdate": true
    }
  }
}
```

```
/plugin install presentation@wwtdigital
```

Repeat `/plugin install <plugin>@wwtdigital` for each bundle you want. New skills arrive on their
own, or run `/plugin marketplace update wwtdigital`. If you added `wwtdigital` from GitHub before,
run `/plugin marketplace remove wwtdigital` first and reinstall your plugins after.

**Claude Code, GitHub org members**

If git on your machine is signed in to a GitHub account in the WWTDigital org (`gh auth login`,
then `gh auth setup-git`, or an SSH key), the GitHub route also works:

```
/plugin marketplace add wwtdigital/skills-marketplace
/plugin install presentation@wwtdigital
```

**Cowork / Claude desktop**

Open *Customize → Plugins → + Add → Add marketplace* and paste `wwtdigital/skills-marketplace`.
That dialog only takes a GitHub repo, so it needs a GitHub account in the WWTDigital org. Without
one, download a bundle's `.zip` from the site and use *Customize → Plugins → + Add → Upload plugin*,
or download a single skill as a `.skill` file and use *Customize → Skills → + Add → Upload skill*.
Skills that need the rest of their plugin (setup scripts, shared files) are offered only as the
whole bundle.

## Plugins

| Plugin | For | Install |
| --- | --- | --- |
| `presentation` | Decks, documents, reports, copy, house style | `/plugin install presentation@wwtdigital` |
| `research` | Desk research, interviews, analysis, synthesis | `/plugin install research@wwtdigital` |
| `ops` | Status reports, staffing, risks, SOWs and estimates | `/plugin install ops@wwtdigital` |
| `admin` | Everyday admin, and tools for contributing to this marketplace | `/plugin install admin@wwtdigital` |
| `tech` | Code review, architecture, repo hygiene, prototyping | `/plugin install tech@wwtdigital` |
| `wwtdigital-deck-design` | The WWT deck design system (a Presentation add-on; brings the Figma MCP and a one-time setup) | `/plugin install wwtdigital-deck-design@wwtdigital` |

## Repo layout

```
.claude-plugin/marketplace.json   the catalog Claude reads
plugins/<plugin>/
  .claude-plugin/plugin.json      plugin manifest
  skills/<skill>/SKILL.md         one folder per skill
  README.md                       what's in the bundle
templates/skill-template/         copy this to start a skill
site/                             Next.js site deployed to Vercel
site/scripts/validate.ts          checks manifests and every SKILL.md (runs in every Vercel build)
site/scripts/build-index.ts       builds the catalog, downloads and the URL marketplace.json
```

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md), also published at https://skills-marketplace.wwtdigital.io/contribute. Short version: copy the template into the
right plugin, write a great `description`, run `npm --prefix site run validate`, open a PR.
Install `admin` and ask Claude to "make this a skill" and it will walk
you through it.

## Maintainers

Discipline owners are listed in [`.github/CODEOWNERS`](.github/CODEOWNERS). Marketplace
admin: Scott Cullum (scott.cullum@wwt.com).
