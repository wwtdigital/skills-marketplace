# Contributing a skill

Anyone at WWT Digital can contribute a skill, with or without a GitHub account. This page is
also published at https://skills-marketplace.wwtdigital.io/contribute.

## Pick a category

Every skill lives in one of five category plugins. Pick the one whose users will actually run it.

| Category | For skills that… |
| --- | --- |
| `presentation` | produce something people see: decks, documents, reports, copy, house style |
| `research` | find things out and make sense of them: desk research, interviews, analysis, synthesis |
| `ops` | run projects and teams: status reports, staffing, risks, SOWs and estimates |
| `admin` | handle everyday admin, and tools for this marketplace itself |
| `tech` | help engineers and technologists: code review, architecture, repo hygiene, prototyping |

Not sure? Pick the closest one and say so when you submit it. A reviewer will move it if needed.

## Without git or a GitHub account

1. Get Claude to build the skill for you. Install the `admin` bundle with the two commands below
   (in Claude Code; no GitHub account needed), then describe your workflow and say "make this a
   skill for the marketplace". Claude builds the folder in the right format and checks it.

   ```
   /plugin marketplace add https://skills-marketplace.wwtdigital.io/marketplace.json
   /plugin install admin@wwt-digital
   ```

   Or start from the [skill template](https://skills-marketplace.wwtdigital.io/downloads/skill-template.zip)
   and fill in `SKILL.md` yourself, using the checklist further down this page.
2. Zip the skill folder.
3. Send it to the marketplace admin, scott.cullum@wwt.com, or post it in #wwtd-claude-skills.
   Include two prompts that *should* make Claude use the skill and one that *shouldn't*.
   A maintainer adds it to the repo and credits you as the owner.

## With git

1. Branch this repo.
2. Copy `templates/skill-template/` to `plugins/<category>/skills/<your-skill>/`. Use a
   kebab-case name, and set `metadata.category` to the same category.
3. Write `SKILL.md`. Spend most of your effort on the `description`: it's the only text
   Claude reads when deciding whether to use the skill. Say what it does, when to use it
   (with real trigger phrases), and what it's *not* for.
4. Add a row to `plugins/<category>/README.md` and bump the versions (see
   [Versioning](#versioning)).
5. Run the checks (Node 24+):
   ```
   npm ci --prefix site           # once
   npm --prefix site run validate -- --strict --base origin/main
   ```
6. Open a PR with the test prompts. The Vercel preview build is the CI: it fails if anything
   doesn't pass the checks.

## What gets a skill merged

- **Repeatable.** Someone will run it more than once. One-off analyses are not skills.
- **Triggers cleanly.** The description makes it obvious when Claude should and
  shouldn't reach for it. Reviewers test with prompts that *should* and *shouldn't*
  trigger it.
- **Verifies its own output.** The workflow includes a check step (open the file, run
  the script, recount the numbers).
- **Safe.** No credentials, no client names or data, no irreversible actions without
  confirmation. Scripts are readable and don't fetch from untrusted sources.
- **Small.** `SKILL.md` body under 250 lines. Longer material goes in `references/`.
- **Owned.** `metadata.owner` is a real WWT email that will answer questions.

## Skill lifecycle

`metadata.status` moves `draft → beta → stable`. Drafts are merged so people can try
them but are labelled on the site. A skill unused for six months gets flagged for
removal; the owner has a month to object.

## Versioning

Bump `metadata.version` in the skill and `version` in the plugin's `plugin.json` on
every change (patch for wording, minor for new behaviour, major for changed triggers).
Bump the marketplace `version` when plugins are added, renamed or removed. Use the
marketplace `renames` map if you rename a plugin so existing installs migrate.

The plugin version is what Claude Code checks for updates: if it doesn't go up, people who
already installed the plugin never get your change. The site build fails if a plugin or skill
changed without a bump (it compares against the live site). README-only edits don't need a bump.

## Adding a category

Rare. Ask in #wwtd-claude-skills first. If agreed: create `plugins/<name>/` with
`.claude-plugin/plugin.json`, `skills/` and `README.md`; add it to
`.claude-plugin/marketplace.json`, to `CATEGORIES` in `site/scripts/lib.ts`, to the template,
and to `.github/CODEOWNERS`.

## Review checklist (for owners)

- [ ] Description answers what / when / not-for, with trigger phrases
- [ ] Tested with two prompts that should trigger, one that shouldn't
- [ ] No secrets, client data or PII anywhere in the folder
- [ ] Verification step present
- [ ] Site build passes (the Vercel preview, or `npm --prefix site run build`)
- [ ] Plugin README table updated
- [ ] Versions bumped
