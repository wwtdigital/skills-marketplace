# <Project / Feature Name> — Implementation Plan

One paragraph: where we are now → where this plan gets us.

## Reading this plan

- Work is organized into **Waves**, each with a **goal**, **dependencies**, and
  **stories** (`W1-S1`, …) with **acceptance criteria (AC)** written to be verified.
- Every AC names the **test that proves it** — an AC is not "done" until its
  assertion is green.
- 🟢 = already real / scaffold exists. 🟡 = partially built. 🔴 = net-new.

## Reality inventory

| Capability | Status |
|---|---|
| <thing that already works> | 🟢 |
| <thing partially built> | 🟡 |
| <thing not started> | 🔴 |

**Blocking seams** (the specific cuts that unlock the goal):

1. **<seam name>** — `<file>:<line>` does `<stub/hard-coded thing>`; until closed,
   `<consequence>`.
2. …

**Core insight:** <one paragraph — given what exists, the small set of cuts +
net-new features that unlock the whole goal>.

---

## Wave 1 — <name> (<role, e.g. foundation>)

**Goal:** <one sentence>

**Why first:** <dependency rationale — what is meaningless/fake until this lands>

**Dependencies:** <prior waves, or "none">

### W1-S1 — <story title> 🟢|🟡|🔴
<one-line description of the change>
- **AC1:** <verifiable statement>. _Proven by: `<test file / case>`._
- **AC2:** <verifiable statement, incl. a negative case if tricky>. _Proven by: `<test>`._
- **Shared seam:** <if applicable — the contract type / boundary also touched by W?-S?>
- **Files:** `<path>`, `<path>`.

### W1-S2 — <story title> 🟢|🟡|🔴
…

---

## Wave 2 — <name>

**Goal:** …
**Why first:** …
**Dependencies:** W1

### W2-S1 — …
…
