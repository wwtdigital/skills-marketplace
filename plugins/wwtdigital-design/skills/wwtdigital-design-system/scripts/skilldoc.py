"""
The design system document, whole. SKILL.md is a short router and the sections live in
references/ (the platform warns on a SKILL.md body over a few hundred lines), but several
checks read the document as one text: the rule table (GEN-02), the contract's stated
numbers, the teardown's rule count. They read it through here, in the original order, so a
split can never make a rule or a number quietly disappear from a check.
"""
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PARTS = ["SKILL.md", "references/contract.md", "references/system.md",
         "references/validation-and-export.md", "references/governance.md",
         "references/regression-guards.md"]


def read_skill():
    out = []
    for p in PARTS:
        with open(os.path.join(ROOT, p), encoding="utf-8") as fh:
            out.append(fh.read())
    return "\n".join(out)
