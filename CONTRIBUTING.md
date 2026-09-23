# Contributing a skill

Anyone at WWT Digital can contribute. There are two paths depending on whether you're
comfortable with git.

## Path A — you use git

1. Fork or branch this repo.
2. Copy `templates/skill-template/` to `plugins/<discipline>/skills/<your-skill>/`.
   Kebab-case names. Pick the discipline whose users will actually run it; if a skill
   spans disciplines, put it where the *owner* sits and tag the others in `metadata`.
3. Write `SKILL.md`. Spend most of your effort on the `description` — it's the only text
   Claude reads when deciding whether to use the skill. Say what it does, when to use it
   (with real trigger phrases), and what it's *not* for.
4. Run the checks:
   ```
   python3 scripts/validate.py --strict --base origin/main
   python3 scripts/build_index.py --check
   claude plugin validate .        # if you have Claude Code installed
   ```
5. Add a row to `plugins/<discipline>/README.md`.
6. Open a PR. The template asks for test prompts a reviewer can paste in.

## Path B — you don't use git

Install `marketplace-tooling@wwt-digital` (or just describe your workflow to Claude in
Cowork) and ask it to "make this a skill for the marketplace". Claude will build the
folder in the correct format. Zip the folder and send it to the discipline owner listed
in `.github/CODEOWNERS`; they'll open the PR for you and credit you as author.

## What gets a skill merged

- **Repeatable.** Someone will run it more than once. One-off analyses are not skills.
- **Triggers cleanly.** The description makes it obvious when Claude should and
  shouldn't reach for it. Reviewers will test with prompts that *should* and *shouldn't*
  trigger it.
- **Verifies its own output.** The workflow includes a check step (open the file, run
  the script, recount the numbers).
- **Safe.** No credentials, no client names or data, no irreversible actions without
  confirmation. Scripts are readable and don't fetch from untrusted sources.
- **Small.** `SKILL.md` body under 250 lines (the validator warns past that, and warnings
  fail CI on `main`). Longer material goes in `references/`.
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
already installed the plugin never get your change. CI fails a PR that changes a plugin or skill
without bumping. Check before you push with
`python3 scripts/validate.py --strict --base origin/main`. README-only edits don't need a bump.

## Adding a plugin (new discipline)

Rare — ask in #wwtd-claude-skills first. If agreed: create `plugins/<name>/` with
`.claude-plugin/plugin.json`, `skills/`, `README.md`; add an entry to
`.claude-plugin/marketplace.json`; add a `CODEOWNERS` line.

## Review checklist (for owners)

- [ ] Description answers what / when / not-for, with trigger phrases
- [ ] Tested with two prompts that should trigger, one that shouldn't
- [ ] No secrets, client data or PII anywhere in the folder
- [ ] Verification step present
- [ ] Validator and build pass in CI
- [ ] Plugin README table updated
- [ ] Versions bumped
