#!/usr/bin/env python3
"""
Check that what the system claims about its Figma source is true and internally consistent.

    python3 scripts/check_provenance.py
    python3 scripts/check_provenance.py --inventory pulled.json   # after a refresh

Two jobs.

WITHOUT --inventory it checks the system against itself: every recipe in
`assets/recipes.html` has an entry in `assets/provenance.json`, every manifest entry has a
recipe, no two recipes claim the same board, and every caption that cites a node id cites one
the manifest knows. No network, no Figma, runs anywhere.

WITH --inventory it checks the system against a fresh pull of the source and reports drift:
boards added, removed, renamed or resized since the manifest was written. See the Refresh
section of SKILL.md for how to produce the inventory file.

WHY THIS EXISTS. The source map used to cite frame names and headline text. Three of its
twenty rows named a headline that is not a frame name at all, two rows claimed a board
another recipe also claimed, and none of it could be verified against the file. Four layouts
sat unbuilt for several revisions while the map said they were covered, because a false claim
reads exactly like a true one (REG-24).

A name is a claim. A node id is checkable. This checks it.

Exit 1 on any FAIL.
"""
import argparse, json, os, re, sys

import skilldoc

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
# Figma node ids in this file are all 3+ digits before the colon. A looser pattern matched
# "16:9" out of board names like "Slide 16:9 - 60" and reported it as an unknown node.
NODE_RE = re.compile(r"\b(\d{3,}:\d+)\b")


def load():
    p = os.path.join(ROOT, "assets", "provenance.json")
    if not os.path.exists(p):
        sys.exit("no assets/provenance.json; the skill is incomplete")
    return json.load(open(p))


def recipes_in_html():
    """Recipe numbers and any node ids cited in their comments, straight from the markup."""
    p = os.path.join(ROOT, "assets", "recipes.html")
    if not os.path.exists(p):
        return {}
    src = open(p, encoding="utf-8", errors="replace").read()
    # Stop before any trailing reference table. The last recipe's block otherwise runs to
    # the end of the file and absorbs every node id in the source map, so recipe 20 was
    # reported as citing eight boards belonging to other recipes.
    cut = re.search(r'<table[^>]*class="spec"', src)
    if cut:
        src = src[:cut.start()]
    out = {}
    marks = list(re.finditer(r"<!--\s*(\d\d)\s+([A-Z][^>]*?)-->", src))
    for k, m in enumerate(marks):
        num = m.group(1)
        end = marks[k + 1].start() if k + 1 < len(marks) else len(src)
        out[num] = set(NODE_RE.findall(src[m.start():end]))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--inventory", help="JSON {node: {name, size:[w,h]}} from a fresh pull")
    ap.add_argument("--quiet", action="store_true")
    a = ap.parse_args()
    man = load()
    recs = man["recipes"]
    boards = {k: v for k, v in man["boards"].items() if not k.startswith("_")}
    fails, warns, notes = [], [], []

    # ---- 1. internal consistency
    html = recipes_in_html()
    if html:
        for num in sorted(html):
            if num not in recs:
                fails.append(("MAP-02", f"recipe {num} is in recipes.html with no manifest entry"))
        for num in sorted(recs):
            if num not in html:
                fails.append(("MAP-02", f"recipe {num} is in the manifest but not in recipes.html"))
        for num, cited in sorted(html.items()):
            if num not in recs:
                continue
            claimed = set(recs[num]["nodes"])
            known = set(boards) | {v["node"] for k, v in man["components"].items()
                                   if not k.startswith("_")} \
                | {man["source"]["section"]["node"], man["source"]["container"]["node"]}
            for nid in cited:
                if nid not in known:
                    fails.append(("MAP-03", f"recipe {num} cites node {nid}, which is not in "
                                            f"the manifest. Either the pull is stale or the "
                                            f"citation is invented"))
            # a caption citing a board node that belongs to a DIFFERENT recipe
            for nid in cited:
                owner = boards.get(nid, {}).get("recipe")
                if owner and owner != num:
                    fails.append(("MAP-04", f"recipe {num} cites {nid}, which the manifest "
                                            f"assigns to recipe {owner}"))
            missing = claimed - cited
            if missing:
                warns.append(("MAP-05", f"recipe {num} claims {', '.join(sorted(missing))} in "
                                        f"the manifest but does not cite it in the markup"))

    # ---- 2. no board claimed twice, every claim resolves
    seen = {}
    for num, r in sorted(recs.items()):
        for nid in r["nodes"]:
            if nid not in boards:
                fails.append(("MAP-06", f"recipe {num} claims {nid}, which is not a board in "
                                        f"the manifest"))
            if nid in seen and seen[nid] != num:
                fails.append(("MAP-07", f"board {nid} is claimed by recipe {seen[nid]} and "
                                        f"recipe {num}. One of them is wrong"))
            seen[nid] = num
    for nid, b in sorted(boards.items()):
        if b.get("recipe") and b["recipe"] not in recs:
            fails.append(("MAP-08", f"board {nid} points at recipe {b['recipe']}, which does "
                                    f"not exist"))
        if b.get("recipe") is None and not b.get("reason"):
            fails.append(("MAP-09", f"board {nid} ({b['name']}) is uncovered with no stated "
                                    f"reason. An uncovered board is a decision; record it"))

    # ---- 3. the artboard exception is declared on both sides
    exc = man["artboard"].get("exceptions", {})
    for nid, e in exc.items():
        if nid not in boards:
            warns.append(("ART-01", f"artboard exception for {nid}, which is not a board"))
            continue
        if list(boards[nid]["size"]) != list(e["authored"]):
            fails.append(("ART-01", f"{nid}: board size {boards[nid]['size']} disagrees with "
                                    f"the exception's authored size {e['authored']}"))
    canon = man["artboard"]["authored"]
    for nid, b in sorted(boards.items()):
        odd = abs(b["size"][0] - canon[0]) > 2 or abs(b["size"][1] - canon[1]) > 2
        if odd and nid not in exc:
            fails.append(("ART-02", f"{nid} ({b['name']}) is {b['size'][0]:.0f} x "
                                    f"{b['size'][1]:.0f}, not the {canon[0]:.1f} x "
                                    f"{canon[1]:.1f} artboard, and has no declared exception. "
                                    f"Normalising its children would be wrong"))
        if not odd and nid in exc:
            fails.append(("ART-02", f"{nid} has an artboard exception but is the standard size"))

    # ---- 4. drift against a fresh pull
    if a.inventory:
        inv = json.load(open(a.inventory))
        inv = {k: v for k, v in inv.items() if not k.startswith("_")}
        for nid, v in sorted(inv.items()):
            if nid not in boards:
                fails.append(("DRIFT-01", f"NEW board {nid} '{v.get('name','')}' is in the "
                                          f"source and not in the manifest. Decide whether it "
                                          f"needs a recipe, then record the decision"))
                continue
            old = boards[nid]
            if v.get("name") and v["name"] != old["name"]:
                notes.append(("DRIFT-02", f"{nid} renamed: '{old['name']}' -> '{v['name']}'. "
                                          f"Harmless, the id is what we key on"))
            if v.get("size") and (abs(v["size"][0] - old["size"][0]) > 2
                                  or abs(v["size"][1] - old["size"][1]) > 2):
                fails.append(("DRIFT-03", f"{nid} RESIZED: {old['size']} -> {v['size']}. Every "
                                          f"measurement taken from it is suspect, and the "
                                          f"normalisation may no longer apply"))
        for nid, b in sorted(boards.items()):
            if nid not in inv:
                sev = warns if b.get("recipe") is None else fails
                sev.append(("DRIFT-04", f"board {nid} ('{b['name']}') is GONE from the source"
                                        + (f", and recipe {b['recipe']} is built from it"
                                           if b.get("recipe") else "")))

    # ---- GEN-01: the generated files still match what generated them.
    # Two files in assets/ are derived rather than authored: the token export, from
    # system.css, and recipes.html, from the spec book's source. Both used to be maintained
    # by hand and recipes.html had already drifted three bug variants, twenty orphan markup
    # fragments and a heading with no table under it before anyone noticed, because nothing
    # compared the copy to the original. A generated file with no staleness check is just a
    # second copy with extra steps.
    import subprocess
    for script, what in (("tokens.py", "assets/tokens.json and assets/tokens.css"),):
        p = os.path.join(HERE, script)
        if not os.path.exists(p):
            fails.append(("GEN-01", f"{script} is missing, so {what} cannot be verified"))
            continue
        r = subprocess.run([sys.executable, p, "--check"], capture_output=True, text=True)
        if r.returncode:
            fails.append(("GEN-01", f"{what} are stale: {r.stdout.strip() or r.stderr.strip()}"))

    # ---- GEN-02: the documented rule set and the implemented rule set are the same set.
    #
    # `IMG-01` sat in the SKILL.md table as "Photography resolves to a library ID, WARN"
    # from the first revision and nothing ever implemented it. Anyone reading the table
    # believed the library was enforced; anyone reading a clean validator run believed the
    # deck had passed that check. Both were wrong for about twenty revisions, and no
    # possible amount of testing would have found it, because the rule that was missing was
    # the rule nobody could see not firing.
    #
    # So the table is checked against the code in both directions. A rule in the docs with
    # no implementation is a lie to the reader. A rule in the code with no documentation is
    # a failure somebody will hit with nothing to read about it.
    doc_ids = set(re.findall(r"^\| ([A-Z]{3}-\d\d) \|", skilldoc.read_skill(), re.M))
    code_ids = set()
    # Every script that can emit a rule id. check_documents.py joined the list at
    # v4.10 and GEN-02 immediately failed its four DOC rules as undocumented, which
    # is the check doing its job: a new rule-emitting script has to be declared here
    # or its rules read as promises nothing keeps.
    for fn in ("wwt_validate.py", "lint_source.py", "verify_pptx.py",
               "check_documents.py", "check_package.py"):
        p = os.path.join(HERE, fn)
        if not os.path.exists(p):
            continue
        body = open(p, encoding="utf-8").read()
        # Only ids in a reporting call or assigned to a rule-id variable count. A mention
        # in a docstring is a reference, not an implementation, and counting those is what
        # would have let IMG-01 keep passing.
        code_ids |= set(re.findall(r'(?:rep\.add|fails\.append|warns\.append)\(\s*\(?\s*"([A-Z]{3}-\d\d)"', body))
        code_ids |= set(re.findall(r'\brid\s*=\s*"([A-Z]{3}-\d\d)"', body))
        # A rule id chosen by a conditional expression, e.g.
        #     rid = "IMG-04" if over_media else "COL-04"
        # Both branches are implementations. Missing this pattern is what made COL-04 and
        # IMG-04 look unimplemented on the first run of this check, which sent me looking
        # for two bugs that were not there before finding the one that was.
        for id_a, id_b in re.findall(
                r'"([A-Z]{3}-\d\d)"\s+if\s+[^\n]*?\s+else\s+"([A-Z]{3}-\d\d)"', body):
            code_ids |= {id_a, id_b}
    for rid in sorted(doc_ids - code_ids):
        fails.append(("GEN-02", f"{rid} is in the SKILL.md rule table and nothing "
                                f"implements it. Documented and unenforced is worse than "
                                f"undocumented: it tells the reader they are covered"))
    for rid in sorted(code_ids - doc_ids):
        fails.append(("GEN-02", f"{rid} can fire and is not in the SKILL.md rule table, so "
                                f"somebody will hit it with nothing to read"))

    # ---- ICO-06: the icon manifest and the icon payload are the same set.
    #
    # Same failure class as GEN-02 and the same reason it needs checking in BOTH
    # directions. A manifest entry with no markup resolves to nothing and the icon
    # silently does not render, which is how the FDU deck lost its partner logos. Markup
    # with no manifest entry is unreachable: `{{ICON_<name>}}` is built from the payload
    # but `ICO-01` validates against the manifest, so an unlisted mark would be rejected
    # by the linter and never used.
    #
    # The markup is one file rather than 497 loose SVGs because a skill package is capped
    # at 200 files and the loose set put this one at 610. Split in two so the manifest
    # stays small enough for lint_source.py to parse inside its 30ms budget.
    ip = os.path.join(ROOT, "assets", "icons", "manifest.json")
    bp = os.path.join(ROOT, "assets", "icons", "icons.json")
    if os.path.exists(ip):
        with open(ip, encoding="utf-8") as fh:
            im = json.load(fh)
        listed = set(im.get("icons", {})) | set(im.get("branded", {}))
        if not os.path.exists(bp):
            fails.append(("ICO-06", "assets/icons/manifest.json lists %d marks and "
                                    "assets/icons/icons.json does not exist, so every "
                                    "placeholder resolves to nothing" % len(listed)))
        else:
            with open(bp, encoding="utf-8") as fh:
                blob = json.load(fh)
            have = set(blob)
            for name in sorted(listed - have):
                fails.append(("ICO-06", f"{name} is in the icon manifest and has no markup "
                                        f"in icons.json. The placeholder resolves to "
                                        f"nothing and the mark silently does not render"))
            for name in sorted(have - listed):
                fails.append(("ICO-06", f"{name} has markup in icons.json and is not in the "
                                        f"manifest, so ICO-01 would reject the name and "
                                        f"nothing can use it"))
            empty = sorted(n for n, v in blob.items() if "<svg" not in (v or ""))
            for name in empty[:6]:
                fails.append(("ICO-06", f"{name} has an entry in icons.json that is not an "
                                        f"SVG"))
        src = im.get("source", {})
        for k in ("file_key", "node", "pulled"):
            if not src.get(k):
                fails.append(("ICO-06", f"the icon manifest does not record {k}. A set with "
                                        f"no provenance cannot be re-pulled or checked"))

    # ---- GEN-03: the numbers on THE CONTRACT page are the numbers in the code.
    #
    # GEN-02 proved rule IDS agree. It says nothing about the VALUES beside them, and the
    # values are what a builder actually copies. At v4.7 the photography floor moved from
    # 20% to 30% and the per-slide test moved from "largest image at 6%" to "imagery sums
    # to 15%". `wwt_validate.py` was updated and section 2 of THE CONTRACT still said 20%
    # with section 3 still saying 6%, so the first page of the skill, the one page the
    # contract insists is not optional reading, disagreed with the validator in two places
    # for two releases. Nothing could catch it, for the same reason GEN-02 exists: a stale
    # number reads exactly like a current one.
    #
    # Scoped to THE CONTRACT rather than the whole file on purpose. The regression register
    # HAS to be able to say "this used to be 20% and here is why it moved", and a check that
    # forbade the old value anywhere would forbid the history that explains it.
    #
    # Two cuts of this check were wrong before this one, and both failures are instructive.
    #
    # The first asserted only that the CURRENT value appears somewhere in the contract, and it
    # passed the exact defect it was written for: "30%" appears in section 1 as the floor and
    # again in section 2's table, so a section 2 still reading "20%" satisfied a presence test
    # on "30%" without contradiction. Presence cannot tell a stale number from a current one
    # when both are on the page.
    #
    # The second added a list of superseded values and forbade them anywhere in the contract.
    # That failed a clean tree, because "20%" is the retired photography floor AND the live
    # `DARK_MAX_SHARE` ceiling. A bare number carries no indication of which rule it belongs
    # to, so a string test cannot be scoped to a constant.
    #
    # What works is anchoring to the line that makes the claim. Each entry names a phrase that
    # identifies its line in the contract, and the value that line has to carry. Reword the
    # line and the check says so, which is correct: a reworded claim needs re-checking.
    #
    # Each entry also states HOW MANY lines should carry its anchor, and that number is not
    # decoration. Two lines state the per-slide photography test, section 1's defaults table
    # and section 3's anti-gaming bullet. Rewording only one of them back to the retired
    # "largest image reaches 6%" left the other saying 15%, the anchor still matched that
    # surviving line, and the check passed a contract that contradicted itself on the same
    # page. A claim made twice has to be checked twice or it is only checked once.
    skill = skilldoc.read_skill()
    cut = skill.find("\n---\n", skill.find("# THE CONTRACT"))
    contract = skill[skill.find("# THE CONTRACT"):cut if cut > 0 else len(skill)]
    vals = {}
    for m in re.finditer(r"^([A-Z_]+) *= *([0-9.]+)", open(
            os.path.join(HERE, "wwt_validate.py"), encoding="utf-8").read(), re.M):
        vals[m.group(1)] = float(m.group(2))

    def pct(name):
        return "%d%%" % round(vals[name] * 100)

    # (constant, anchor phrase, how the line must write the value, how many lines say it)
    CLAIMS = [
        ("PHOTO_FLOOR",    "Slides carrying a photograph",   pct, 1),
        ("PHOTO_FLOOR",    "of slides minimum",              pct, 1),
        ("PHOTO_WARN",     "of slides minimum",              pct, 1),
        ("PHOTO_MIN_AREA", "imagery sums to",                pct, 2),
        ("PHOTO_MAX_GAP",  "never more than",                lambda n: "%d" % vals[n], 1),
        ("ARCH_MAX_SHARE", "Largest share on one architect", pct, 1),
        ("DARK_MAX_SHARE", "Slides on the dark emphasis",    pct, 1),
        ("SPARSE_MAX",     "Sparse roles are capped at",     pct, 1),
    ]
    lines = contract.splitlines()
    for name, anchor, fmt, count in CLAIMS:
        if name not in vals:
            fails.append(("GEN-03", f"{name} is gone from wwt_validate.py but GEN-03 still "
                                    f"expects it. Update CLAIMS in this script in the same "
                                    f"change"))
            continue
        hits = [ln for ln in lines if anchor in ln]
        if len(hits) != count:
            fails.append(("GEN-03", f"{len(hits)} lines in THE CONTRACT contain {anchor!r} "
                                    f"and {name} expects {count}. A claim was added, deleted "
                                    f"or reworded; re-read it against the code and update "
                                    f"CLAIMS to match"))
        want = fmt(name)
        for ln in hits:
            if want not in ln:
                fails.append(("GEN-03", f"{name} is {want} in wwt_validate.py and THE "
                                        f"CONTRACT's {anchor!r} line does not say so: "
                                        f"{ln.strip()[:110]}"))

    # ---- report
    src = man["source"]
    if not a.quiet:
        print("\nWWT provenance check")
        print("  source   %s, section %s '%s'" % (src["file_name"], src["section"]["node"],
                                                  src["section"]["name"]))
        print("  pulled   %s, %d boards" % (src["pulled"], src["board_count"]))
        print("  manifest %d recipes, %d boards, %d uncovered"
              % (len(recs), len(boards),
                 sum(1 for b in boards.values() if b.get("recipe") is None)))
        if a.inventory:
            print("  compared against %s" % a.inventory)
        print()
        for rid, msg in fails:
            print("  FAIL %-9s %s" % (rid, msg))
        for rid, msg in warns:
            print("  WARN %-9s %s" % (rid, msg))
        for rid, msg in notes:
            print("  note %-9s %s" % (rid, msg))
        print("\n  %d FAIL   %d WARN   %d note" % (len(fails), len(warns), len(notes)))
        if not fails:
            print("  every recipe resolves to a node id, no board is claimed twice, and every")
            print("  uncovered board has a recorded reason.")
        unc = [(k, v) for k, v in sorted(boards.items()) if v.get("recipe") is None]
        if unc:
            print("\n  uncovered boards, with the recorded reason:")
            for k, v in unc:
                print("    %-12s %-26s %s" % (k, v["name"], v.get("reason", "")[:78]))
        print()
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
