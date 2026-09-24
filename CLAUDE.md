# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this is

A Claude Code / Cowork **plugin marketplace** for WWTDigital. Marketplace name `wwtdigital`.
Skills are grouped into one plugin per category; users install the bundles they need.
A Next.js site (`site/`, deployed to Vercel) lets people browse and download skills without GitHub.

Hosting:
- Repo: `github.com/wwtdigital/skills-marketplace` (made public 2026-09-23 so the GitHub install
  path needs no org membership or account; the site's downloads already made everything else in it
  public anyway, and `wwtdigital` already runs other public repos, so this isn't out of pattern.
  **Owner calls this temporary, a for-now fix, not a settled decision** — don't assume it stays
  public, and check with the owner before building anything that depends on it staying that way.)
- Vercel: project `skills-marketplace` in team `wwtd`, Root Directory `site`, Next.js preset,
  production branch `main`. Every pushed branch gets a preview deployment.
- Site: `https://skills-marketplace.wwtdigital.io` (`wwtdigital.io` DNS is managed in the `wwtd` team)

If either changes, `git grep` for it. The site hostname lives in `marketplace.json` `metadata.site`,
every `plugin.json` `homepage`, and `README.md`. The repo slug lives in `site/lib/catalog.ts`
(`REPO_URL`, shared by the build scripts and the pages), every `plugin.json` `repository`, and
`README.md`.

## Layout

```
.claude-plugin/marketplace.json   catalog Claude reads; pluginRoot = ./plugins
plugins/<plugin>/
  .claude-plugin/plugin.json      manifest (name must match marketplace entry)
  skills/<skill>/SKILL.md         one folder per skill (+ optional scripts/ references/ assets/)
  README.md                       bundle description + skills table (update when adding a skill)
templates/skill-template/         starting point for new skills; frontmatter has a `metadata` block
site/                             Next.js App Router on Vercel (pages prerendered); Root Directory = site/
site/scripts/validate.ts          lint the whole repo; --strict makes warnings fatal; version-bump checks
site/scripts/build-index.ts       writes site/public/{data/index.json, downloads/, marketplace.json}
site/scripts/lib.ts               shared loaders (marketplace, manifests, SKILL.md frontmatter, hashing)
.github/CODEOWNERS                one GitHub team per category (teams don't exist yet)
```

Plugins: one bundle per category (`presentation`, `research`, `ops`, `admin`, `tech`), plus
standalone opt-in plugins that belong to a category but install separately because they bring
hooks or MCP servers most of that category won't want. Skills so far: `admin` has
`wwt-skill-author` and `marketplace-smoke-test`; `presentation` has `humanizer`; `ops` has
`wwtdigital-onboarding` (Staci Powell); the standalone
`wwtdigital-deck-design` (category `presentation`, from Toby Gerber) has `wwtdigital-deck-design` and
`wwtdigital-deck-design-doctor`. The category plugins replaced the original discipline plugins on
2026-09-23; `renames` maps `marketplace-tooling` → `admin`.

## Commands

All tooling is Node (24+, which runs the `.ts` scripts directly). No Python.

```
cd site && npm ci
npm run dev                            # generates the catalog, then http://localhost:3000
npm run build && npm run typecheck     # the same build Vercel runs: strict validation + catalog + next build
npm start                              # serve the production build
npm run validate -- --strict --base origin/main   # pre-push: lint + version bumps vs main
npm run catalog -- --check             # dry-run the catalog build
claude plugin validate ..              # official validator (not run automatically)
```

There is no test suite. `validate.ts` is the lint/test gate, and it always checks the whole repo
(you can't point it at one skill).

Test the marketplace itself: `/plugin marketplace add ./` from the repo root, then
`/plugin install admin@wwtdigital`.

## Conventions

- Skill folder name == frontmatter `name`, kebab-case. Prefix `wwt-` only for WWT-brand-specific skills.
- Frontmatter `metadata`: `owner` (@wwt.com), `category`, `status` (draft|beta|stable),
  `connectors` (list), `version`. Validator enforces owner/category/status.
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
- `site/public/data/` and `site/public/downloads/` are generated at build time and gitignored.
- `CONTRIBUTING.md` is published as the site's `/contribute` page (read from the repo root at build
  time), for contributors who never open the repo at all. Write it for them: absolute links to the
  site (made relative when rendered), no links assuming repo familiarity.
- Maintainers commit straight to `main` for now (no PRs). A push to `main` deploys production, so
  run `npm --prefix site run build` first; a failed Vercel build leaves the last good deploy up.

## How the pipeline fits together

- `marketplace.json` is the single source of truth. Both scripts iterate its `plugins[]` and resolve
  each `source` (only relative-path sources are supported) via `common.plugin_dir`. A plugin folder
  that isn't listed there is invisible to validation, the site and Claude.
- `metadata.category` must be one of `CATEGORIES` in `site/scripts/lib.ts` *and* equal the category
  of the plugin the skill lives in: the plugin's own name for a category bundle, or the marketplace
  entry's `category` for a standalone plugin (which must name one of `CATEGORIES`). It's redundant
  in the repo but travels with a downloaded `.skill`.
  Adding a category means updating `CATEGORIES`, `marketplace.json`, `CODEOWNERS`, the template,
  and the table in `CONTRIBUTING.md`.
- There is no GitHub Actions (not allowed here). The Vercel build is the CI: `npm run build` runs
  `validate.ts --strict`, then `build-index.ts`, then `next build`. The scripts read `../plugins`
  etc., so the Vercel project must include files outside the Root Directory (the default).
  A validation failure fails the deploy, and Vercel reports that as the commit status on the PR.
  Production keeps serving the last good build.
- `--strict` makes warnings errors: a description with no "Use when…"/"trigger" wording, a
  description under 80 chars, no "verif"/"check" in the body, a body over 250 lines, a missing
  `metadata.version`. Empty plugins print a `NOTE`, not a warning.
- Version bumps: any change under `plugins/<p>/` other than `README.md`/`.gitkeep` needs a higher
  `plugin.json` version, and a changed existing skill needs a higher `metadata.version`. Adding or
  removing a plugin needs a higher marketplace `version`. New plugins and new skills don't need a
  bump of their own. There are two baselines for the same rules:
  - On Vercel, the scripts default to `--prev-catalog auto` and compare per-plugin and per-skill
    `content_hash`es against the live production catalog (`metadata.site` + `/data/index.json`).
    The clone has no `origin/main`. If there's no production catalog yet, the check is skipped
    with a `NOTE`.
  - Locally, `--base origin/main` diffs the working tree, including uncommitted and untracked
    files.
- `build-index.ts` quietly drops any skill with structural problems (no SKILL.md, bad frontmatter,
  name mismatch) from the site. Validation runs first in the build, so this only bites if you run
  it on its own. "updated" dates come from the production catalog when a skill's hash is unchanged,
  otherwise from `git log` (and the current time if that's empty).
- The site reads `site/public/data/index.json` from disk at build time. Nothing is fetched at
  runtime. Its shape is the `Catalog` type in `site/lib/catalog.ts`, which `build-index.ts` also
  uses, so the compiler keeps them in step. `lib/load.ts` uses `node:fs`, so never import
  it from a `"use client"` component.
- Skill pages live at `/skills/<name>`, and downloads are `<name>.skill`, so skill names must be
  unique across all plugins. `validate.ts` enforces this.
- MCP servers live in `plugins/<category>/.mcp.json` (not `plugin.json`, which the validator
  rejects) and connect for everyone who installs that category. `presentation` has
  `artifact-publisher`, `research` has `brandscanner`; both are OAuth-backed http servers, so the
  config is just type + url. The validator requires https, kebab-case names, and `${VAR}`
  references for any header/env value, and runs the secret scan on `.mcp.json`. build-index emits
  them as `mcp_servers` per plugin, which the site shows on the plugin card. Verified: installing
  the plugin registers `plugin:<category>:<server>` in `claude mcp list`.
- Two ways to install the marketplace. The git one (`/plugin marketplace add wwtdigital/skills-marketplace`)
  needs no account or access now that the repo is public. The URL one (`/plugin marketplace add
  https://skills-marketplace.wwtdigital.io/marketplace.json`) needs no GitHub account either: build-index
  generates that file with every plugin as an `archive` source (`downloads/<plugin>.zip` + `sha256`).
  Both use the same marketplace name, so plugin ids are the same. Claude Code only accepts https
  archive URLs on non-loopback hosts, so you can't test it on localhost, and previews are behind
  Vercel auth. Zips are deterministic (fixed mtime), so a `sha256` only changes when content does.
- The marketplace's own top-level `name` (`wwtdigital`, renamed 2026-09-24 from `wwt-digital` for
  consistency with the GitHub org and domain) is what Claude Code registers locally, taken from
  `marketplace.json`'s `name` field, not from the repo slug or URL. Renaming it, unlike renaming a
  *plugin* (which the `renames` map smooths over), has no migration path: anyone who already added
  the marketplace under the old name has it registered as `wwt-digital` locally and needs to
  `/plugin marketplace remove wwt-digital` then re-add before `@wwtdigital` install commands work
  for them, or they'll hit "its network source differs from the one declared" or simply not find
  the new name. Confirmed hands-on: switching a plugin's *source* (URL vs GitHub) under the same
  marketplace name hits that same error and needs the same remove-then-re-add fix, and also drops
  every plugin installed under the old registration (reinstall them after).
- Cowork / desktop app install, corrected 2026-09-23 after testing against the real UI twice (first
  pass was wrong, see below). Customize > Plugins > + Add > **Add marketplace** is a single field
  that only accepts a GitHub `owner/repo` or a git-clone URL to github.com/gitlab.com/bitbucket.org
  (confirmed by screenshot: "A GitHub owner/repo or a Git repository URL", and it rejects our
  hosted marketplace.json with "This host isn't supported..."). There is no separate "Marketplace
  URL" option in this dialog. (An earlier pass here wrongly claimed a three-way GitHub-repo /
  Git-URL / Marketplace-URL dropdown, and that "both work, url too" meant the plain URL was
  accepted; that dropdown is real but belongs to the *admin* managed-settings schema
  (`allowedPluginMarketplaces`), not this end-user dialog. "Both work, url too" meant entering the
  GitHub repo as `owner/repo` and as a full `https://github.com/...` URL, both valid for this one
  field.) So for Cowork/Desktop: GitHub repo access works via Add marketplace; no-GitHub-account
  users need **Upload plugin** with the downloaded `.zip` instead — the URL/no-GitHub path only
  works today via the Claude Code CLI (`/plugin marketplace add <url>` in a terminal), not this GUI
  dialog. Once a marketplace is added, its plugins show up in the Plugins list to enable (that step
  itself, and the exact enable/install wording, wasn't watched happen). Customize
  > Plugins > + Add > **Upload plugin** and Customize > Skills > + Add > **Upload skill** exist
  exactly there (confirmed), but no one has actually uploaded one of this repo's `.zip`/`.skill`
  files through them — the site's claim that they work assumes our zips (plugin files at the zip
  root; skill files inside a folder named for the skill) match what those buttons expect. Owner
  decided 2026-09-23 not to test that upload, so treat it as documented-but-unverified until
  someone does. None of this is guaranteed for other orgs; their admins can disable user-added
  marketplaces, plugin uploads, or skill uploads independently.
- Plugin manifests link to `/#<plugin-name>`, which opens that bundle on the home page. Keep those
  anchor ids.
- When copying `templates/skill-template/`, rename the frontmatter `name: skill-template` and cut
  the `category`/`status` option lists down to single values. Otherwise the validator fails.

- `wwtdigital-deck-design` ships **no Aptos fonts**: they're Microsoft's and the repo is public. Its
  `scripts/brand_assets.py` finds Aptos on the machine by the name inside each file (PowerPoint.app
  on Mac carries the five sans cuts; Aptos Serif is an Office cloud font, only needed for pull
  quotes; Microsoft's free download has all of them). It deliberately skips Office's Mac cloud-font
  cache (`~/Library/Group Containers/UBF8T346G9.Office`): reading another app's container from the
  Claude desktop app raises a macOS "access data from other apps" prompt and blocks until answered. Don't re-add the font files. WWT brand
  material (photos, logos, icons, the recipe 12 solution matrix) is fine in the repo (owner, 2026-09-24). Its SKILL.md is a short router: the sections live in `references/`, and its scripts
  that parse the document read it through `scripts/skilldoc.py`.
  Users are assumed non-technical with no working Python, so the plugin has **no hooks** (hooks run in
  whatever shell exists, PowerShell on Windows without Git Bash, and a bare `python3` on a Mac without
  developer tools pops an install dialog). Instead `setup/setup.sh` / `setup.ps1` (run once, with the
  user's OK, offered by the skill) installs uv, a uv-managed Python 3.12 and `setup/requirements.txt`
  into `~/.wwtdigital-deck-design/venv`, and a browser only if there's no Chrome/Edge; every script runs
  via `setup/run.sh` / `run.ps1`, which exits 3 with "SETUP NEEDED" instead of touching system
  Python. `scripts/browser.py` launches installed Chrome/Edge first. Where scripts execute in Cowork
  (host vs VM) is unverified; if it's a VM, the PowerPoint.app font lookup won't find anything.

## Do not touch without asking

- `.claude-plugin/marketplace.json` plugin names (renaming breaks installs; use `renames`)
- `site/vercel.json` download headers

## Backlog (in rough priority order)

1. Create the GitHub teams named in CODEOWNERS.
2. Migrate Scott's existing skills: `staffing-manager` → ops; `deslopify` → presentation;
   `mr-review-assistant`, `agents-md-generator`, `likec4-architect` → tech; `wwt-scorecard` →
   admin (unconfirmed; could be research). Each needs the `metadata` block and a README row.
3. Add `relevance` hints to marketplace entries once admins allowlist the marketplace.
4. Consider a Notion intake path for non-git contributors (Notion MCP has upload-skill).

## Origin

Scaffolded in a Cowork session on 2026-09-23 by Scott Cullum with Claude. Docs used:
https://docs.claude.com/en/docs/claude-code/plugin-marketplaces
