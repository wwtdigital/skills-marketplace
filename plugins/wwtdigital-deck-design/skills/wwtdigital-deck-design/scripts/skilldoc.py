"""
The design system document, whole, however it happens to be split on disk.

SKILL.md is a router and the sections live in `references/`, because the full document is
about 2,200 lines and 137 KB and was being loaded before any work began, on every deck:
roughly 35,000 tokens spent before reading the brief. Splitting it saves about 34,000 of
those per activation.

But several checks read the document as ONE text and must keep doing so:

    GEN-02   every rule id in a table is implemented, and every implemented id is in a
             table. Both directions, across every rule family.
    GEN-03   the numbers on THE CONTRACT page are the numbers in the code.
    teardown the rule count it prints

If those read only SKILL.md after a split, they would find almost nothing and report clean.
That is the worst possible outcome: a checker that passes because it has been pointed at an
empty room. It is the same failure this system has hit repeatedly, most recently when
`DOC-03` compared one fact and called it agreement, and when `check_provenance` did not scan
itself and so could not see fourteen of its own rules.

So the split is an implementation detail and this module hides it. Everything reads the
document through `read_skill()`, in the original order, and a section can be moved between
files without any check noticing or caring.

`PARTS` is the contract. If a new reference file carries a rule table or a contract number,
it belongs in this list, and `check_provenance.py`'s `SKL-01` fails when a `references/*.md`
file exists that nothing here reads.
"""
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# In document order, as the single file used to read.
PARTS = [
    "SKILL.md",
    "references/contract.md",
    "references/system.md",
    "references/validation-and-export.md",
    "references/governance.md",
    "references/regression-guards.md",
]


def parts_present():
    return [p for p in PARTS if os.path.exists(os.path.join(ROOT, p))]


def missing():
    return [p for p in PARTS if not os.path.exists(os.path.join(ROOT, p))]


def unlisted():
    """references/*.md that no check reads. A section nobody assembles is a section whose
    rules and numbers are invisible to GEN-02 and GEN-03, which is how a documented rule
    goes unenforced without anything noticing."""
    d = os.path.join(ROOT, "references")
    if not os.path.isdir(d):
        return []
    listed = {os.path.basename(p) for p in PARTS}
    # triage.md and failure-modes.md are prose for a reader, not rule-bearing sections.
    prose = {"triage.md", "failure-modes.md"}
    return sorted(f for f in os.listdir(d)
                  if f.endswith(".md") and f not in listed and f not in prose)


def read_skill():
    """The whole document, in order, as one string."""
    out = []
    for p in parts_present():
        with open(os.path.join(ROOT, p), encoding="utf-8") as fh:
            out.append(fh.read())
    return "\n".join(out)
