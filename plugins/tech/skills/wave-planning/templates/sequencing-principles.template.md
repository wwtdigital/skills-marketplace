# Sequencing Principles

Reusable doctrine for ordering work, distilled from past projects. Read this
*before* planning a new project — it lets you generate correct wave ordering without
relearning these lessons. Append new lessons after each project.

## Principles

- **Close foundational seams before the features that depend on them.** A feature
  built on a stub gets torn out and rebuilt once the stub is replaced.
- **Identity before anything that attributes, authorizes, or audits.** RBAC,
  per-actor approvals, and attribution are theatre until the acting identity is
  real.
- **Additive schema/migrations before the features that read them.** Land the data
  model first so feature stories have something real to query.
- **Real data path before polish.** Make a surface trustworthy (real, verified
  end-to-end) before investing in its UX refinement.
- **Name shared contracts before parallel work.** When two stories touch the same
  seam (contract type, build-graph edge), agree the interface in both stories up
  front — don't patch the integration break after merge.

<!-- Add project-specific or newly-learned principles below. Each should be a
portable rule, not a one-off note. -->

## Lessons log

| Date | Project | Lesson |
|---|---|---|
| <YYYY-MM-DD> | <project> | <what ordering mistake/insight to carry forward> |
