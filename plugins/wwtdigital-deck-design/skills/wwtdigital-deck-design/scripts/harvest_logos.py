#!/usr/bin/env python3
"""
Pull the partner and client logos out of a source deck before rebuilding it.

    python3 scripts/harvest_logos.py "Source Deck.pptx" -o harvested/
    python3 scripts/harvest_logos.py "Source Deck.pptx"            # report only

PRELIMINARY. It finds the marks and reports them; it does not decide how big they should
be on the rebuilt slide. Sizing is a design decision nobody has made yet, and guessing at
it here would put a number into the system that no one chose. See "What this does not do".

WHY THIS EXISTS.

A customer deck was rebuilt into this design system and came back without its partner
logos. Cognition, Windsurf, GitHub Copilot, Claude, Microsoft, Devin, Glean and Gemini,
eight marks across seven slides, all gone. The partner NAMES survived as body text, which
is the tell: the content had been read and the artwork had not.

Nothing objected. The HTML validated, the PPTX verified, and every rule in the set asked
"is what is on this slide correct" while none asked "is everything that was on the source
slide still here". An asset that is silently absent looks exactly like an asset that was
never wanted, which is the same failure shape as REG-27 and REG-42.

A .pptx is a zip. Every image is already sitting in ppt/media/ and every slide's rels file
says which ones it uses. Nothing about this is hard; it simply had to be written down.

HOW A LOGO IS TOLD FROM AN ICON.

By the shape of the box it is placed in, not by looking at the picture. On the deck this
was built against the split was unambiguous:

    logos        1.25 to 2.5 inches wide, 0.3 to 0.6 tall, aspect 2.4:1 to 7.8:1
    icons        exact squares at 0.31in and 0.53in, aspect 1:1
    photographs  large, and usually the only thing that big on the slide

So: wider than it is tall by a clear margin, small in absolute terms, and not a square.
That rule made no judgement calls on the source deck. It will misfire on a wide photograph
crop, which is why every hit is reported with its size for a human to glance at rather
than silently trusted.

WHAT THIS DOES NOT DO.

  * It does not decide a display size. The system has no partner-logo component yet, and
    inventing a width here would be exactly the "element nobody decided on" of REG-47.
  * It does not place anything. It writes files and a manifest; the build uses them.
  * It does not deduplicate by appearance, only by file. The same mark exported twice at
    different sizes is two files in the package and will be two entries here.
  * It does not judge whether a logo SHOULD be carried over. Some belong to a client who
    is no longer in the story.

Exit 1 if the file cannot be read. Exit 0 with a count of 0 if a deck genuinely has none.
"""
import argparse, json, os, re, sys, zipfile

EMU = 914400.0                      # English Metric Units per inch

# The logo envelope, in inches, derived from the deck described above. Deliberately wide:
# the cost of a false positive is a human glancing at a reported thumbnail, and the cost of
# a false negative is a logo silently missing from a client deck.
MIN_W, MAX_W = 0.9, 3.2
MAX_H = 0.9
MIN_RATIO = 2.0                     # wider than it is tall, by a clear margin
ICON_MAX = 1.00                     # anything roughly square and under this is decoration.
                                    # 0.62 at first, which left 0.78in squares in "other"
                                    # and made the report read as if something unclassified
                                    # was lurking. They were icons.


def rels_for(z, slide):
    p = "ppt/slides/_rels/%s.rels" % os.path.basename(slide)
    if p not in z.namelist():
        return {}
    x = z.read(p).decode("utf-8", "replace")
    return {m.group(1): m.group(2)
            for m in re.finditer(r'Id="([^"]+)"[^>]*Target="([^"]+)"', x)}


def pictures(z, slide):
    """Every <p:pic> on a slide: its media part, its placed size in inches, its name."""
    x = z.read(slide).decode("utf-8", "replace")
    rels = rels_for(z, slide)
    out = []
    for blk in re.findall(r"<p:pic>.*?</p:pic>", x, re.S):
        emb = re.search(r'r:embed="([^"]+)"', blk)
        ext = re.search(r'<a:ext cx="(\d+)" cy="(\d+)"', blk)
        nm = re.search(r'name="([^"]*)"', blk)
        if not (emb and ext):
            continue
        tgt = rels.get(emb.group(1), "")
        if "media/" not in tgt:
            continue
        part = "ppt/" + tgt.replace("../", "")
        out.append({"part": part,
                    "w": int(ext.group(1)) / EMU, "h": int(ext.group(2)) / EMU,
                    "name": nm.group(1) if nm else ""})
    return out


def classify(p):
    w, h = p["w"], p["h"]
    if h <= 0 or w <= 0:
        return "empty"
    ratio = w / h
    if abs(ratio - 1.0) < 0.45 and w <= ICON_MAX:
        return "icon"
    if MIN_W <= w <= MAX_W and h <= MAX_H and ratio >= MIN_RATIO:
        return "logo"
    if w >= 4.0 or h >= 3.0:
        return "photo"
    return "other"


def harvest(src, outdir=None):
    if not zipfile.is_zipfile(src):
        sys.exit("not a .pptx (or not readable): %s" % src)
    z = zipfile.ZipFile(src)
    slides = sorted([n for n in z.namelist()
                     if re.fullmatch(r"ppt/slides/slide\d+\.xml", n)],
                    key=lambda n: int(re.findall(r"\d+", n)[-1]))
    found, counts = {}, {"logo": 0, "icon": 0, "photo": 0, "other": 0, "empty": 0}
    for n, slide in enumerate(slides, 1):
        for p in pictures(z, slide):
            kind = classify(p)
            counts[kind] += 1
            if kind != "logo":
                continue
            e = found.setdefault(p["part"], {"slides": [], "w": p["w"], "h": p["h"],
                                             "names": set()})
            e["slides"].append(n)
            e["names"].add(p["name"])
            e["w"], e["h"] = max(e["w"], p["w"]), max(e["h"], p["h"])

    man = {"source": os.path.basename(src), "slides": len(slides),
           "counts": counts, "logos": {}}
    for part, e in sorted(found.items(), key=lambda kv: kv[1]["slides"][0]):
        stem = re.sub(r"[^a-z0-9]+", "-", os.path.splitext(os.path.basename(part))[0].lower())
        rec = {"part": part,
               "placed_in": [round(e["w"], 2), round(e["h"], 2)],
               "ratio": round(e["w"] / e["h"], 2) if e["h"] else None,
               "slides": sorted(set(e["slides"])),
               "shape_names": sorted(n for n in e["names"] if n)}
        if outdir:
            os.makedirs(outdir, exist_ok=True)
            dst = os.path.join(outdir, stem + os.path.splitext(part)[1])
            with open(dst, "wb") as fh:
                fh.write(z.read(part))
            rec["file"] = os.path.relpath(dst)
            rec["bytes"] = os.path.getsize(dst)
        man["logos"][stem] = rec
    z.close()
    if outdir:
        with open(os.path.join(outdir, "harvested.json"), "w", encoding="utf-8") as fh:
            json.dump(man, fh, indent=1, sort_keys=True)
    return man


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("source", help="the .pptx being rebuilt")
    ap.add_argument("-o", "--out", help="write the images and harvested.json here")
    ap.add_argument("--json", action="store_true", help="machine-readable, nothing else")
    a = ap.parse_args()
    man = harvest(a.source, a.out)

    if a.json:
        print(json.dumps(man, indent=1, sort_keys=True))
        return 0

    c, lg = man["counts"], man["logos"]
    print("\nLogo harvest — %s" % man["source"])
    print("  %d slides, %d pictures: %d look like logos, %d icons, %d photographs, %d other"
          % (man["slides"], sum(c.values()), c["logo"], c["icon"], c["photo"], c["other"]))
    if not lg:
        print("\n  No partner logos found. If the deck visibly has some, they may be grouped\n"
              "  shapes or vector drawings rather than pictures; say so rather than assuming\n"
              "  the deck has none.\n")
        return 0
    print("\n  %-22s %-13s %-7s %s" % ("mark", "placed (in)", "ratio", "on slides"))
    for stem, r in lg.items():
        print("  %-22s %-13s %-7s %s"
              % (stem[:22], "%.2f x %.2f" % tuple(r["placed_in"]), r["ratio"],
                 ", ".join(map(str, r["slides"]))))
    used = sorted({s for r in lg.values() for s in r["slides"]})
    print("\n  %d distinct marks across slides %s" % (len(lg), ", ".join(map(str, used))))
    if a.out:
        print("  written to %s/ with harvested.json" % a.out)
    else:
        print("  report only. Pass -o DIR to extract them.")
    print("\n  Sizing is NOT decided here. The system has no partner-logo component yet, so\n"
          "  pick the placement with a designer rather than taking the source deck's numbers,\n"
          "  which were set for a different grid.\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
