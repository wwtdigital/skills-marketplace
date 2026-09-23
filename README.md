# WWTDigital Skills Marketplace

A shared catalog of Claude skills for WWTDigital, organised by category. Each
category is a **plugin**; each plugin contains one or more **skills**. Install the
bundles you need and Claude picks up the skills automatically in Claude Code and
Cowork.

Browse the catalog and get step-by-step install help at **https://skills-marketplace.wwtdigital.io**.

## Install

**Claude Code**

```
/plugin marketplace add wwtdigital/skills-marketplace
/plugin install presentation@wwt-digital
```

Repeat `/plugin install <plugin>@wwt-digital` for each bundle you want. Run
`/plugin marketplace update wwt-digital` to pull new skills.

**Cowork / Claude desktop**

Open *Customize → Plugins → Add marketplace* and paste
`https://github.com/wwtdigital/skills-marketplace`, then install the bundles you want.

**No GitHub account?**

The repo is public, so the GitHub route above needs no account or access. If you'd rather skip
GitHub entirely, add the marketplace from the site instead in Claude Code:

```
/plugin marketplace add https://skills-marketplace.wwtdigital.io/marketplace.json
/plugin install presentation@wwt-digital
```

Or download any skill as a `.skill` file from the site and drop it into Cowork
(*Customize → Skills → Add*), or unzip it into `~/.claude/skills/` for Claude Code.

## Plugins

| Plugin | For | Install |
| --- | --- | --- |
| `presentation` | Decks, documents, reports, copy, house style | `/plugin install presentation@wwt-digital` |
| `research` | Desk research, interviews, analysis, synthesis | `/plugin install research@wwt-digital` |
| `ops` | Status reports, staffing, risks, SOWs and estimates | `/plugin install ops@wwt-digital` |
| `admin` | Everyday admin, and tools for contributing to this marketplace | `/plugin install admin@wwt-digital` |
| `tech` | Code review, architecture, repo hygiene, prototyping | `/plugin install tech@wwt-digital` |

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
