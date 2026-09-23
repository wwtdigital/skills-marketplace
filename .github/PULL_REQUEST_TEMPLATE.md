## What

<!-- One sentence: which skill(s), which plugin, new or changed. -->

## Why

<!-- Who asked for it / what repeated task it removes. -->

## Try it

Paste these into Claude with the plugin installed. The first two should trigger the skill; the third should not.

1. 
2. 
3. (should NOT trigger) 

## Checklist

- [ ] `python3 scripts/validate.py --strict --base origin/main` passes
- [ ] `python3 scripts/build_index.py --check` passes
- [ ] Description covers what / when / not-for
- [ ] No secrets, client data or PII in the folder
- [ ] Verification step included in the skill's workflow
- [ ] Plugin `README.md` table updated
- [ ] `metadata.version` and plugin `version` bumped
