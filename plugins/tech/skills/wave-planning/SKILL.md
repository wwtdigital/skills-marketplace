---
name: wave-planning
description: >
  Build a spec-lite, dependency-ordered implementation plan for a software project or large
  feature. Use when the user wants to plan a project, scope a body of work into shippable units,
  write an implementation or roadmap doc, break an epic into stories, or set up a repeatable
  planning framework. Produces a Waves→Stories plan with verifiable acceptance criteria mapped
  to tests, anchored to a reality inventory, plus a reusable sequencing-principles doctrine.
  Honours a repo's .claude/wave-conventions.md for plan paths and story IDs. Not for reviewing
  a wave that has already been built (use wave-review), and not for writing a single ticket or
  a status report.
metadata:
  owner: andrew.brydon@wwt.com
  category: tech
  status: beta
  connectors: []
  version: 1.0.0
---

# Wave Planning

A repeatable framework for planning software projects and large features. It sits
between heavyweight formal specs and unstructured "vibe coding": precise enough that
"done" is checkable, cheap enough to write in sentences, and living next to the code.

The output is two documents:

1. `docs/implementation-plan.md` — the plan itself (Waves → Stories → executable AC).
2. `docs/sequencing-principles.md` — reusable doctrine for *why* work is ordered the
   way it is, so future planning doesn't rediscover the same lessons.

Templates for both live in `templates/` next to this file. Copy and fill them — do
not invent a different structure.

## Repo conventions (check first)

Before anything else, check whether the repo has a **`.claude/wave-conventions.md`**
file. If it does, read it: its plan location, story-ID scheme, wave-graph doc and
extra rules **override the defaults in this skill** (e.g. a repo may keep its stories
in `docs/08-stories.md` with `S-###` IDs instead of `docs/implementation-plan.md`
with `Wn-Sn`). Everything else here still applies. If there is no such file, use the
defaults below. When the user wants repo-specific behaviour, offer to create that
file rather than forking this skill.

## When to use this

- Planning a new project or a multi-week feature.
- Turning a vague goal ("make it real", "ship collaboration") into ordered, shippable
  units.
- Breaking an epic into stories that an agent or a teammate can pick up cold.

## The procedure

Work through these phases in order. Do not skip the reality inventory — it is what
keeps the plan honest.

### Phase 1 — Reality inventory (anchor to the codebase as it is)

Before planning any work, audit what already exists. Imagined architecture is the
single biggest source of wasted planning.

- Explore the codebase. Build a table of capabilities that are **already real**
  (🟢), **partially built** (🟡), and **net-new** (🔴).
- Name the precise **seams** that block everything else — the specific files/lines
  where a stub, hard-coded value, or fake boundary stands between mock and real
  (e.g. `getCurrentUser()` at `http.ts:26` returning a hard-coded id). Cite
  `file:line`.
- State the core insight in one paragraph: given what exists, what is the *small*
  set of cuts + net-new features that unlock the whole goal?

### Phase 2 — Carve into Waves

A **Wave** is a coherent milestone with a single goal and a clear "why now."

- Each wave: a **goal** (one sentence), its **dependencies** (which earlier waves
  must land first), and a **"why first" rationale**.
- Order waves by dependency, not by excitement. Foundational seams come first —
  building features on a stubbed foundation means tearing them out later (e.g.
  "RBAC is theatre until identity is real" → identity wave precedes RBAC wave).
- Capture each non-obvious ordering decision; it feeds Phase 5.

### Phase 3 — Stories with executable acceptance criteria

A **Story** (`W<wave>-S<n>`, e.g. `W6-S1`) is one focused, independently
reviewable, revertible unit — ideally one branch / one PR (~200–1200 lines).

Each story has:

- A status marker (🟢/🟡/🔴) and a one-line description.
- **Numbered acceptance criteria** (`AC1…ACn`), each written so it is *verifiable*,
  not an opinion. "Returns 401 (distinct from the RBAC 403)" — not "auth works."
- The **named target files** the story will touch.

**Improvement #3 — make the AC executable.** This is the highest-leverage part of
the framework. For every AC, name the assertion that proves it:

- Map each AC to a test: `AC3 → covered by e2e/auth.spec.ts "unauth → 401"`.
- If no test exists yet, the story's work includes writing it; the AC is not "done"
  until its assertion is green.
- The story's PR description must list each AC with its proving test and a ✅ when
  green. This converts prose AC into a machine-checkable contract — formal-spec
  confidence at spec-lite cost.
- For the 1–2 trickiest AC per wave, add a **negative case or concrete example
  payload** to kill ambiguity ("@mention to a non-member → no notification").

When two stories touch a **shared seam** (a contract type, a build-graph edge, an
API shape), name that shared contract in *both* stories' entries so the interface
is agreed before any parallel work starts — not patched after merge.

### Phase 4 — Verify dependency claims before each wave starts

The reality inventory is accurate only at authoring time. Before starting a wave,
re-verify its dependency claims against the current main branch. A 🟡 may have
become 🟢, or a seam may have moved. Catching drift here saves a correction PR later.

This checkpoint is a recurring action, not a one-off — run the **`wave-review`**
skill at the end of each wave to grade the just-finished wave against its AC, update
this plan document in place, reconcile drift, and re-verify the next wave's
dependencies before you start it.

### Phase 5 — Distill sequencing principles (the reusable doctrine)

**Improvement #5.** The "why first" rationales from Phase 2 are gold but die as
one-offs. Promote them into `docs/sequencing-principles.md` as reusable rules:

- Generalize each ordering decision into a portable principle ("never build
  attribution/RBAC on a stubbed identity"; "close seams before features that depend
  on them"; "additive migrations before the features that read them").
- This doc carries across projects. On the next project, read it *first* — it lets
  you (or an agent) generate correct wave ordering without relearning the lessons.
- After a project, append any newly-learned ordering lessons. The doctrine
  compounds.

## Output checklist

A complete plan has:

- [ ] A reality inventory table (🟢/🟡/🔴) and named seams with `file:line`.
- [ ] A one-paragraph core insight.
- [ ] Waves with goal, dependencies, and "why first."
- [ ] Stories (`Wn-Sn`) with status, numbered verifiable AC, and target files.
- [ ] **Every AC mapped to a proving test** (Phase 3 / improvement #3).
- [ ] Shared seams named in both touching stories.
- [ ] `docs/sequencing-principles.md` capturing the ordering doctrine (improvement #5).

## Anti-patterns to avoid

- Planning against imagined architecture (skip the inventory) → wasted work.
- AC as opinions ("works well", "is fast") → unverifiable, drift creeps in.
- Big-bang stories → un-reviewable, un-revertible.
- Ordering by excitement instead of dependency → rework when foundations shift.
- Letting "why first" reasoning evaporate instead of capturing it as doctrine.
