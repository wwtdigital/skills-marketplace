# WWT Digital Skills Marketplace

A shared catalog of Claude skills for WWT Digital, organised by discipline. Each
discipline is a **plugin**; each plugin contains one or more **skills**. Install the
bundle for your role and Claude picks up the skills automatically in Claude Code and
Cowork.

Browse the catalog and get step-by-step install help at **https://skills.wwtdigital.com**.

## Install

**Claude Code**

```
/plugin marketplace add wwtdigital/skills-marketplace
/plugin install creative-tech@wwt-digital
```

Repeat `/plugin install <plugin>@wwt-digital` for each bundle you want. Run
`/plugin marketplace update wwt-digital` to pull new skills.

**Cowork / Claude desktop**

Open *Customize → Plugins → Add marketplace* and paste
`https://github.com/wwtdigital/skills-marketplace`, then install the bundles you want.

**No GitHub access?**

Download any skill as a `.skill` file from the site and drop it into Cowork
(*Customize → Skills → Add*), or unzip it into `~/.claude/skills/` for Claude Code.

## Plugins

| Plugin | For | Install |
| --- | --- | --- |
| `creative-tech` | Creative Technology team | `/plugin install creative-tech@wwt-digital` |
| `engineering` | Software engineers | `/plugin install engineering@wwt-digital` |
| `brand-and-voice` | Anyone producing WWT-branded material | `/plugin install brand-and-voice@wwt-digital` |
| `delivery` | Delivery leads and PMs | `/plugin install delivery@wwt-digital` |
| `data-ai` | Data and AI practitioners | `/plugin install data-ai@wwt-digital` |
| `marketplace-tooling` | Contributors to this repo | `/plugin install marketplace-tooling@wwt-digital` |

## Repo layout

```
.claude-plugin/marketplace.json   the catalog Claude reads
plugins/<plugin>/
  .claude-plugin/plugin.json      plugin manifest
  skills/<skill>/SKILL.md         one folder per skill
  README.md                       what's in the bundle
templates/skill-template/         copy this to start a skill
scripts/validate.py               checks manifests and every SKILL.md
scripts/build_index.py            builds site/data/index.json and site/downloads/*.skill
site/                             static site deployed to Vercel
```

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md). Short version: copy the template into the
right plugin, write a great `description`, run `python3 scripts/validate.py`, open a PR.
Install `marketplace-tooling` and ask Claude to "make this a skill" and it will walk
you through it.

## Maintainers

Discipline owners are listed in [`.github/CODEOWNERS`](.github/CODEOWNERS). Marketplace
admin: Scott Cullum (scott.cullum@wwt.com).
