---
name: wave-review
description: >
  Run an end-of-wave checkpoint on a Waves→Stories implementation plan. Use when a wave has
  finished, or before starting the next one, to verify each story's acceptance criteria actually
  passed, update the plan document's status markers and AC checkboxes, detect drift between plan
  and reality, re-verify the next wave's dependencies, and capture new sequencing lessons.
  Honours a repo's .claude/wave-conventions.md. Companion to wave-planning. Not for creating a
  new plan (use wave-planning) and not for reviewing a single pull request's code.
metadata:
  owner: andrew.brydon@wwt.com
  category: tech
  status: beta
  connectors: []
  version: 1.0.0
---

# Wave Review

The end-of-wave checkpoint for a plan built with the `wave-planning` skill. A wave
is only "done" when its acceptance criteria are *demonstrably* green and the plan
document reflects what actually shipped. This skill closes that loop: it grades the
wave against its own AC, **updates `docs/implementation-plan.md` in place**, surfaces
drift, and prepares the next wave.

Run it when a wave's stories are merged, or as the first step before starting the
next wave.

## Repo conventions (check first)

Before anything else, check whether the repo has a **`.claude/wave-conventions.md`**
file. If it does, read it: its plan location, story-ID scheme, wave-graph doc and
extra rules **override the defaults in this skill** (e.g. a repo may keep its stories
in `docs/08-stories.md` with `S-###` IDs instead of `docs/implementation-plan.md`
with `Wn-Sn`). Everything else here still applies. If there is no such file, use the
defaults below. When the user wants repo-specific behaviour, offer to create that
file rather than forking this skill.

The defaults below name `docs/implementation-plan.md` and
`docs/sequencing-principles.md`; substitute the convention file's paths where it sets them.

## Inputs

- `docs/implementation-plan.md` (the plan; required).
- `docs/sequencing-principles.md` (the doctrine; updated if new lessons emerge).
- The current state of the codebase / `main` and the merged PRs for the wave.
- The wave to review (ask the user if ambiguous; otherwise infer the most recently
  worked wave from git history and plan status markers).

## The procedure

### Phase 1 — Grade the wave against its AC

For each story in the wave, go AC by AC. **Do not take "done" on faith — verify.**

- Find the **proving test** named in the AC (improvement #3 from `wave-planning`).
  Run it (or the relevant suite) and confirm it's green. If an AC has no proving
  test, that's a finding — flag it and either locate coverage or note the gap.
- For AC without automated coverage, verify by inspecting the code/behavior at the
  named target files and state how it was checked.
- Classify each AC: ✅ met (with passing test) · ⚠️ met-but-unverified (no test) ·
  ❌ not met · ➖ descoped (with reason).

### Phase 2 — Update the plan document in place

Edit `docs/implementation-plan.md` to reflect reality. This is the core action — the
plan is a living doc, not a write-once artifact.

- Flip story **status markers**: 🔴/🟡 → 🟢 when complete.
- Check off AC and append the proving test + a ✅ to each met AC (e.g.
  `**AC3:** … _Proven by: `e2e/auth.spec.ts "unauth → 401"` ✅_`).
- Record any **deviation**: AC that changed meaning, were split, merged, descoped,
  or added mid-wave. Add a short `**Deviation:**` note on the story so the history
  is legible.
- Add an `**Outcome:**` line per completed wave summarizing what actually shipped
  and linking the merged PRs.

### Phase 3 — Detect and reconcile drift

The map and the territory diverge during execution. Surface it explicitly:

- **Scope drift** — stories added, dropped, or resized vs. the original plan.
- **Seam drift** — a named seam (`file:line`) moved, was already closed, or turned
  out to be somewhere else. Update the reality inventory.
- **Status drift** — a capability the plan marked 🟡/🔴 is now 🟢 (or vice-versa)
  for reasons unrelated to this wave.
- **Contract drift** — a shared seam two stories depend on changed shape; check both
  dependent stories still hold.

For each, either update the plan to match reality or flag a real divergence for the
user to decide. Don't silently paper over a divergence.

### Phase 4 — Re-verify the next wave's dependencies

This is `wave-planning` Phase 4, run for real now that a wave has landed.

- Read the next wave's stated **dependencies** and **reality inventory** claims.
- Re-check each against current `main`: is every prerequisite actually 🟢? Did a
  seam this wave relied on move? Are the next wave's named target files still where
  the plan says?
- Update the next wave's entries with anything that changed. Catching this *now*
  saves a mid-wave correction PR.

### Phase 5 — Capture new sequencing lessons

If the wave taught an ordering lesson — a dependency you didn't see coming, a "should
have closed that seam first" — promote it into `docs/sequencing-principles.md` per
`wave-planning` Phase 5. Add a dated row to the lessons log. The doctrine compounds.

## Output — the alignment report

After editing the docs, give the user a concise report:

- **Wave verdict:** on-track ✅ / shipped-with-deviations ⚠️ / blocked ❌.
- **AC scoreboard:** counts of ✅ / ⚠️ / ❌ / ➖ across the wave's stories, with each
  ❌ and ⚠️ named and explained.
- **Drift found & reconciled:** the bullets from Phase 3, and what you changed in the
  plan to match.
- **Next wave readiness:** dependencies re-verified — green to start, or the specific
  prerequisites still outstanding.
- **New principles captured:** any rows added to `sequencing-principles.md`.
- **Plan diff:** a one-line summary of the edits made to `implementation-plan.md`.

## Anti-patterns to avoid

- Marking a story 🟢 without running its proving test → unverified "done."
- Reviewing in your head and not editing the plan doc → the plan rots, drift
  accumulates silently.
- Silently rewriting the plan to match a divergence the user should weigh in on.
- Skipping Phase 4 → walking into the next wave on stale dependency assumptions.
- Letting a hard-won ordering lesson evaporate instead of recording it.
