#!/usr/bin/env python3
"""
Check that this skill can actually be installed, before anyone tries to install it.

    python3 scripts/check_package.py            # check the skill directory
    python3 scripts/check_package.py --zip x.skill

WHY THIS EXISTS.

A skill package is capped at **200 files**. v4.10.0 shipped 610, because the icon library
went in as 497 loose SVGs. Every other gate passed: the self-test was clean, the validator
was clean, the provenance check was clean, the zip built without complaint and the byte
size looked reasonable at 8.6 MB. The package was simply refused at install time, and the
first anyone heard of it was a user hitting the wall.

The lesson is narrow and worth stating plainly: **the packaging step was reviewed for size
and never for shape.** Byte count was measured on every release. File count was measured
on none, so a limit that had never been close became a limit that had been crossed, with
nothing in the pipeline positioned to notice.

    PKG-01  the file count is inside the platform limit
    PKG-02  nothing that should never ship is in the package (caches, OS junk)
    PKG-03  the entry point exists and is a file, not an empty directory

Exit 1 on any FAIL.
"""
import argparse, os, sys, zipfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)

# The platform's cap. Kept as a named constant with the headroom warning below it, because
# a limit you only discover at the boundary is a limit you cross.
FILE_MAX = 200
WARN_AT = 0.85          # say something while there is still room to act

JUNK = (".DS_Store", "Thumbs.db", ".pyc", "__pycache__", ".pytest_cache", ".ipynb_checkpoints")


def listing(path):
    """Every file the package will contain, as the platform would count them."""
    if path.endswith((".zip", ".skill", ".plugin")):
        with zipfile.ZipFile(path) as z:
            return [n for n in z.namelist() if not n.endswith("/")]
    out = []
    for base, dirs, files in os.walk(path):
        dirs[:] = [d for d in dirs if d not in ("__pycache__", ".git")]
        for f in files:
            out.append(os.path.relpath(os.path.join(base, f), path))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--zip", help="check a built .skill/.plugin instead of the directory")
    ap.add_argument("--max", type=int, default=FILE_MAX)
    ap.add_argument("--quiet", action="store_true")
    a = ap.parse_args()

    target = a.zip or ROOT
    if not os.path.exists(target):
        sys.exit("no such path: %s" % target)
    files = listing(target)
    fails, warns = [], []

    # ---- PKG-01 the file count
    n = len(files)
    if n > a.max:
        # Name the biggest directory, because "too many files" without "and they are all
        # here" sends the reader counting by hand.
        by_dir = {}
        for f in files:
            d = os.path.dirname(f) or "(root)"
            by_dir[d] = by_dir.get(d, 0) + 1
        worst = sorted(by_dir.items(), key=lambda kv: -kv[1])[:3]
        where = ", ".join("%s: %d" % (d, c) for d, c in worst)
        fails.append(("PKG-01", "%d files, and the limit is %d. The package will be refused "
                                "at install. Biggest directories: %s" % (n, a.max, where)))
    elif n > a.max * WARN_AT:
        warns.append(("PKG-01", "%d files against a limit of %d. Under, but close enough "
                                "that the next asset set will cross it" % (n, a.max)))

    # ---- PKG-02 nothing that should never ship
    junk = sorted(f for f in files if any(j in f for j in JUNK))
    for f in junk[:8]:
        fails.append(("PKG-02", "%s should not be in the package" % f))
    if len(junk) > 8:
        fails.append(("PKG-02", "and %d more like it" % (len(junk) - 8)))

    # ---- PKG-03 the entry point
    root = ""
    if a.zip:
        tops = {f.split("/")[0] for f in files}
        root = (tops.pop() + "/") if len(tops) == 1 else ""
    if not any(f == root + "SKILL.md" for f in files):
        fails.append(("PKG-03", "no SKILL.md at the package root. Nothing will load it"))

    if not a.quiet:
        print("\nWWT package check — %s" % os.path.basename(os.path.abspath(target)))
        print("  %d files, limit %d, %d to spare" % (n, a.max, max(0, a.max - n)))
        for rid, msg in warns:
            print("  WARN %-7s %s" % (rid, msg))
        for rid, msg in fails:
            print("  FAIL %-7s %s" % (rid, msg))
        print("\n  %d FAIL   %d WARN" % (len(fails), len(warns)))
        if not fails:
            print("  this package will install.")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
