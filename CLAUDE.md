# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this is

A Claude Code / Cowork **plugin marketplace** for WWT Digital. Marketplace name `wwt-digital`.
Skills are grouped into one plugin per discipline; users install a bundle for their role.
A Next.js site (`site/`, deployed to Vercel) lets people browse and download skills without GitHub.

Hosting:
- Repo: `github.com/wwtdigital/skills-marketplace` (private)
- Vercel: project `skills-marketplace` in team `wwtd`, Root Directory `site`, Next.js preset,
  production branch `main`. Every pushed branch gets a preview deployment.
- Site: `https://skills-marketplace.wwtdigital.io` (`wwtdigital.io` DNS is managed in the `wwtd` team)

If either changes, `git grep` for it. The site hostname lives in `marketplace.json` `metadata.site`,
every `plugin.json` `homepage`, and `README.md`. The repo slug lives in `scripts/build_index.py`
(`REPO_URL` and the install string), `site/lib/catalog.ts` (`REPO_URL`, a fallback only, since the site
reads the repo from `index.json`), every `plugin.json` `repository`, and `README.md`.

## Layout

```
.claude-plugin/marketplace.json   catalog Claude reads; pluginRoot = ./plugins
plugins/<plugin>/
  .claude-plugin/plugin.json      manifest (name must match marketplace entry)
  skills/<skill>/SKILL.md         one folder per skill (+ optional scripts/ references/ assets/)
  README.md                       bundle description + skills table (update when adding a skill)
templates/skill-template/         starting point for new skills; frontmatter has a `metadata` block
scripts/common.py                 shared loaders (stdlib + PyYAML)
scripts/validate.py               lint everything; --strict makes warnings fatal; --base REF checks version bumps
scripts/build_index.py            writes site/public/data/index.json + site/public/downloads/*.skill|*.zip
site/                             Next.js App Router on Vercel (pages prerendered); Root Directory = site/
.github/workflows/ci.yml          validate on PR; on main rebuild catalog and commit it
.github/CODEOWNERS                one GitHub team per discipline (teams don't exist yet)
```

Plugins: `creative-tech`, `engineering`, `brand-and-voice`, `delivery`, `data-ai`, `marketplace-tooling`.
Only `marketplace-tooling` has a skill so far (`wwt-skill-author`).

## Commands

```
pip install pyyaml                     # Homebrew Python refuses global installs: use a .venv
python3 scripts/validate.py --strict --base origin/main   # what CI runs on a PR; must pass
python3 scripts/build_index.py --check # dry run
python3 scripts/build_index.py         # regenerates site/public/{data,downloads} (CI does this on main)
claude plugin validate .               # official validator

cd site && npm ci
npm run dev                            # http://localhost:3000
npm run build && npm run typecheck     # CI runs the build on every PR
npm start                              # serve the production build
```

There is no test suite. `validate.py` is the lint/test gate, and it always checks the whole repo
(you can't point it at one skill).

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
- `plugin.json` `version` is the release gate: Claude Code skips `/plugin update` and auto-update
  when it's unchanged, so a skill edit without a plugin bump never reaches installed users. It
  overrides any `version` on the marketplace entry (keep it out of `marketplace.json`). Skill
  `metadata.version` is informational only; the site shows it, Claude Code ignores it.
  `validate.py --base` enforces the bumps (see below).
- Don't hand-edit `site/public/data/` or `site/public/downloads/`. Both are generated.

## How the pipeline fits together

- `marketplace.json` is the single source of truth. Both scripts iterate its `plugins[]` and resolve
  each `source` (only relative-path sources are supported) via `common.plugin_dir`. A plugin folder
  that isn't listed there is invisible to validation, the site and Claude.
- The allowed `metadata.discipline` values come from `DISCIPLINES` in `scripts/common.py`, not from
  plugin names. `marketplace-tooling` skills use `discipline: tooling`. Adding a discipline plugin
  means updating `DISCIPLINES`, `marketplace.json`, `CODEOWNERS`, and the template's discipline list.
- CI runs `validate.py --strict` everywhere, so warnings are errors: a description with no
  "Use when…"/"trigger" wording, a description under 80 chars, no "verif"/"check" in the body,
  a body over 250 lines, a missing `metadata.version`. Empty plugins print a `NOTE`, not a warning.
- On PRs CI also passes `--base origin/<base branch>`. Any change under `plugins/<p>/` other than
  `README.md`/`.gitkeep` then needs a higher `plugin.json` version, and a changed existing skill
  needs a higher `metadata.version`. Adding or removing a plugin needs a higher marketplace
  `version`. New plugins and new skills don't need a bump of their own. `--base` diffs against
  the working tree, so uncommitted and untracked files count.
- `build_index.py` quietly drops any skill with structural problems (no SKILL.md, bad frontmatter,
  name mismatch) from the site. Run the validator first. It also reads `git log` for each skill's
  "updated" date, so uncommitted skills show the current time.
- The site reads `site/public/data/index.json` from disk at build time. Nothing is fetched at
  runtime. Its shape is whatever `build()` in `build_index.py` emits (typed in
  `site/lib/catalog.ts`), so change both together. `lib/load.ts` uses `node:fs`, so never import
  it from a `"use client"` component.
- Skill pages live at `/skills/<name>`, and downloads are `<name>.skill`, so skill names must be
  unique across all plugins. `validate.py` enforces this.
- Plugin manifests link to `/#<plugin-name>`, which opens that bundle on the home page. Keep those
  anchor ids.
- When copying `templates/skill-template/`, rename the frontmatter `name: skill-template` and cut
  the `discipline`/`status` option lists down to single values. Otherwise the validator fails.

## Do not touch without asking

- `.claude-plugin/marketplace.json` plugin names (renaming breaks installs; use `renames`)
- `.github/workflows/ci.yml` bot commit step
- `site/vercel.json` download headers

## Backlog (in rough priority order)

1. Create the GitHub teams named in CODEOWNERS.
2. Migrate Scott's existing skills as first PRs:
   `staffing-manager`, `wwt-scorecard` → creative-tech; `deslopify` → brand-and-voice;
   `mr-review-assistant`, `agents-md-generator`, `likec4-architect` → engineering.
   Each needs the `metadata` block added and a README table row.
3. Add `relevance` hints to marketplace entries once admins allowlist the marketplace.
4. Consider a Notion intake path for non-git contributors (Notion MCP has upload-skill).
5. Decide on Cowork install wording once verified against the current desktop UI.

## Origin

Scaffolded in a Cowork session on 2026-09-23 by Scott Cullum with Claude. Docs used:
https://docs.claude.com/en/docs/claude-code/plugin-marketplaces
