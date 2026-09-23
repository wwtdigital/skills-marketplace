# CLAUDE.md — WWT Digital Skills Marketplace

Claude Code context for this repo. Read before making changes.

## What this is

A Claude Code / Cowork **plugin marketplace** for WWT Digital. Marketplace name `wwt-digital`.
Skills are grouped into one plugin per discipline; users install a bundle for their role.
A static site (`site/`, deployed to Vercel) lets people browse and download skills without GitHub.

Target hosting (not yet created):
- Repo: `github.com/wwtdigital/skills-marketplace`
- Site: `https://skills.wwtdigital.com` (hostname is assumed — change in `marketplace.json`,
  `README.md`, `scripts/build_index.py` if different)

## Layout

```
.claude-plugin/marketplace.json   catalog Claude reads; pluginRoot = ./plugins
plugins/<plugin>/
  .claude-plugin/plugin.json      manifest (name must match marketplace entry)
  skills/<skill>/SKILL.md         one folder per skill (+ optional scripts/ references/ assets/)
  README.md                       bundle description + skills table (update when adding a skill)
templates/skill-template/         starting point for new skills; frontmatter has a `metadata` block
scripts/common.py                 shared loaders (stdlib + PyYAML)
scripts/validate.py               lint everything; --strict makes warnings fatal (CI on main)
scripts/build_index.py            writes site/data/index.json + site/downloads/*.skill|*.zip
site/                             static, no build; Vercel Root Directory = site/
.github/workflows/ci.yml          validate on PR; on main rebuild catalog and commit it
.github/CODEOWNERS                one GitHub team per discipline (teams don't exist yet)
```

Plugins: `creative-tech`, `engineering`, `brand-and-voice`, `delivery`, `data-ai`, `marketplace-tooling`.
Only `marketplace-tooling` has a skill so far (`wwt-skill-author`).

## Commands

```
pip install pyyaml
python3 scripts/validate.py            # must be 0 errors before any PR
python3 scripts/build_index.py --check # dry run
python3 scripts/build_index.py         # regenerates site/data + site/downloads (CI does this on main)
claude plugin validate .               # official validator
python3 -m http.server -d site 8080    # preview site locally
```

Test the marketplace itself: `/plugin marketplace add ./` from the repo root, then
`/plugin install marketplace-tooling@wwt-digital`.

## Conventions

- Skill folder name == frontmatter `name`, kebab-case. Prefix `wwt-` only for WWT-brand-specific skills.
- Frontmatter `metadata`: `owner` (@wwt.com), `discipline`, `status` (draft|beta|stable),
  `connectors` (list), `version`. Validator enforces owner/discipline/status.
- Description: what + when (with trigger phrases) + not-for. ≤1024 chars. This is the only
  thing Claude reads to decide whether to load the skill.
- Every skill's workflow includes a verification step.
- No secrets, client names or PII anywhere in `plugins/`. Validator scans for tokens.
- Bump skill `metadata.version` and plugin `version` on every change; marketplace `version`
  when plugins are added/renamed/removed (use `renames` map for renames).
- Don't hand-edit `site/data/` or `site/downloads/` — generated.

## Do not touch without asking

- `.claude-plugin/marketplace.json` plugin names (renaming breaks installs; use `renames`)
- `.github/workflows/ci.yml` bot commit step
- `site/vercel.json` download headers

## Backlog (in rough priority order)

1. Create GitHub repo + teams named in CODEOWNERS; connect Vercel (Root Directory `site/`).
2. Migrate Scott's existing skills as first PRs:
   `staffing-manager`, `wwt-scorecard` → creative-tech; `deslopify` → brand-and-voice;
   `mr-review-assistant`, `agents-md-generator`, `likec4-architect` → engineering.
   Each needs the `metadata` block added and a README table row.
3. Site: skill detail should render the SKILL.md body (build_index could emit it as HTML).
4. Add `relevance` hints to marketplace entries once admins allowlist the marketplace.
5. Consider a Notion intake path for non-git contributors (Notion MCP has upload-skill).
6. Decide on Cowork install wording once verified against the current desktop UI.

## Origin

Scaffolded in a Cowork session on 2026-09-23 by Scott Cullum with Claude. Docs used:
https://docs.claude.com/en/docs/claude-code/plugin-marketplaces
