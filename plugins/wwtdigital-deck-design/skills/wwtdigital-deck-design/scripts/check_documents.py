#!/usr/bin/env python3
"""
Check that the two reference documents agree with the stylesheet and with each other.

    python3 scripts/check_documents.py SPEC-BOOK.html WWT-teardown.html

WHY THIS EXISTS.

This system ships two documents that describe one thing, and they are kept because each
does a job the other cannot:

    the teardown    is for LOOKING AT the system. It renders every token as a live
                    specimen, carries the icon set, the voice rules, the measured contrast
                    ratios and the list of what the system does not have. 600 KB, builds
                    with the standard library alone, so it opens on a machine where
                    Chromium will not install.

    the spec book   is for COPYING GEOMETRY out of. Twenty recipes rendered at full size
                    with their real measured numbers, the component gallery, the
                    background patterns. 17 MB, needs a browser to build.

That split is honest, but it is also exactly the shape of every drift failure this system
has had. Two copies of a fact with nothing comparing them is how `GEN-01`, `GEN-02`,
`GEN-03` and the deleted project-instructions checklist all happened. The documents agreed
on the day they were checked by hand. Nothing made them keep agreeing.

They had already stopped. The spec book's masthead claimed an "18-frame photo library"
against a manifest of 19 and a teardown that said 19, and carried "v1.0" through ten
releases. A reader had no way to tell which number was current. That is fixed at the
source now (build.py resolves the masthead from the manifests), and this script is what
stops the next one.

WHAT IT COMPARES. Only facts that are stated in a checkable form, because a rule that
guesses is worse than no rule:

    DOC-01  every "#FG #BG N.NN" triple recomputes correctly from its own hex values
    DOC-02  every type token's stated size matches assets/system.css
    DOC-03  where both documents state the same fact, they state the same value
    DOC-04  both documents declare what they are for, so a reader who opens the wrong
            one finds out in a sentence rather than an afternoon

It deliberately does NOT try to measure "overlap" or flag duplicated prose. Two documents
explaining the same idea in different words is fine and often good. Two documents stating
different NUMBERS for the same thing is the defect.

Needs Playwright, because both documents compute their content in the browser and reading
the HTML source would measure the template rather than the page. If it cannot run it says
so as a failure, not as a silence: see PRB-01 and REG-50.

Exit 1 on any FAIL.
"""
import argparse, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)

TRIPLE = re.compile(r"(#[0-9A-Fa-f]{6})\s+(#[0-9A-Fa-f]{6})\s+(\d+\.\d\d)")
# The two documents tabulate the type ladder differently, and that is fine: one is a
# spec table, the other a specimen sheet. Both are read, because a rule that only
# understands one document's layout compares nothing. The first cut of this matched
# only the spec book's tab-separated rows, so DOC-03 had exactly ONE fact stated in
# both documents to compare and was close to useless while reporting a clean pass.
#   spec book:  "t-h2\tAptos Black\t80\t76 · .95\t..."
#   teardown:   "t-h2\n80px / .95 · 900 · ..."
TYPEROW = re.compile(r"(t-[a-z0-9-]+)\s*(?:\t[^\t\n]*\t\s*(\d{2,3})\b"
                     r"|\n\s*(\d{2,3})px\s*/)")


def _lin(c):
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4


def lum(h):
    h = h.lstrip("#")
    return (0.2126 * _lin(int(h[0:2], 16) / 255)
            + 0.7152 * _lin(int(h[2:4], 16) / 255)
            + 0.0722 * _lin(int(h[4:6], 16) / 255))


def ratio(a, b):
    la, lb = lum(a), lum(b)
    return (max(la, lb) + 0.05) / (min(la, lb) + 0.05)


def css_type_sizes():
    """The only authority on what a type token is. Both documents answer to this."""
    p = os.path.join(ROOT, "assets", "system.css")
    if not os.path.exists(p):
        return {}
    out = {}
    for m in re.finditer(r"^\.(t-[a-z0-9-]+)\{([^}]*)\}",
                         open(p, encoding="utf-8").read(), re.M | re.S):
        fs = re.search(r"font-size:([0-9.]+)px", m.group(2))
        if fs:
            out[m.group(1)] = float(fs.group(1))
    return out


def read(paths):
    from playwright.sync_api import sync_playwright
    from browser import launch
    txt = {}
    with sync_playwright() as pw:
        b = launch(pw)
        for label, p in paths.items():
            pg = b.new_page(viewport={"width": 1500, "height": 1000})
            pg.goto("file://" + os.path.abspath(p))
            pg.wait_for_timeout(3500)
            txt[label] = pg.evaluate("() => document.body.innerText")
            pg.close()
        b.close()
    return txt


def facts(s):
    """Every checkable claim in one document, keyed so the two can be compared."""
    f = {}
    for m in TRIPLE.finditer(s):
        f[("ratio", m.group(1).upper(), m.group(2).upper())] = float(m.group(3))
    for m in TYPEROW.finditer(s):
        px = m.group(2) or m.group(3)
        if px:
            f[("type", m.group(1))] = float(px)
    # Counts that both documents have stated at one time or another, and that have a
    # single authority elsewhere. These are the ones that actually went wrong.
    m = re.search(r"(\d+)-frame photo library", s)
    if m:
        f[("count", "photographs")] = float(m.group(1))
    m = re.search(r"\b(\d+) recipes\b", s)
    if m:
        f[("count", "recipes")] = float(m.group(1))
    return f


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("spec", help="the rendered spec book")
    ap.add_argument("teardown", help="the rendered teardown")
    ap.add_argument("--quiet", action="store_true")
    a = ap.parse_args()

    for p in (a.spec, a.teardown):
        if not os.path.exists(p):
            sys.exit("no such file: %s" % p)

    fails = []
    try:
        txt = read({"spec book": a.spec, "teardown": a.teardown})
    except Exception as e:
        # A gate that cannot run is not a gate, and it must not report a pass. REG-50.
        print("\nWWT document check")
        print("  FAIL DOC-00  the documents could not be rendered (%s), so nothing was "
              "compared. Install Playwright and Chromium, or say plainly that this did "
              "not run" % str(e)[:90])
        print("\n  1 FAIL")
        return 1

    truth = css_type_sizes()
    F = {k: facts(v) for k, v in txt.items()}

    # ---- DOC-01 a stated ratio has to be true of its own two colours
    for doc, d in F.items():
        for key, v in sorted(d.items()):
            if key[0] != "ratio":
                continue
            real = ratio(key[1], key[2])
            if abs(real - v) > 0.05:
                fails.append(("DOC-01", f"{doc}: {key[1]} on {key[2]} is stated as {v}:1 "
                                        f"and is actually {real:.2f}:1"))

    # ---- DOC-02 a stated type size has to match the stylesheet
    for doc, d in F.items():
        for key, v in sorted(d.items()):
            if key[0] != "type" or key[1] not in truth:
                continue
            if abs(truth[key[1]] - v) > 0.5:
                fails.append(("DOC-02", f"{doc}: .{key[1]} is stated as {v:.0f}px and "
                                        f"system.css says {truth[key[1]]:.0f}px"))

    # ---- DOC-03 where both state the same fact, they state the same value
    a_, b_ = F["spec book"], F["teardown"]
    shared = sorted(set(a_) & set(b_))
    for key in shared:
        if abs(a_[key] - b_[key]) > 0.05:
            fails.append(("DOC-03", f"the two documents disagree about {' '.join(map(str, key))}: "
                                    f"spec book {a_[key]}, teardown {b_[key]}"))

    # ---- DOC-04 each document says which job it is for
    for doc, body in txt.items():
        if "What this page is for" not in body and "What this document is for" not in body:
            fails.append(("DOC-04", f"{doc} does not state what it is for. There are two "
                                    f"reference documents and a reader who opens the wrong "
                                    f"one wastes an afternoon"))

    if not a.quiet:
        print("\nWWT document check")
        print("  spec book  %s" % os.path.basename(a.spec))
        print("  teardown   %s" % os.path.basename(a.teardown))
        print("  %d checkable claims in the spec book, %d in the teardown, %d stated in both"
              % (len(a_), len(b_), len(shared)))
        for rid, msg in fails:
            print("  FAIL %-7s %s" % (rid, msg))
        print("\n  %d FAIL" % len(fails))
        if not fails:
            print("  the two documents agree with the stylesheet and with each other.")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
