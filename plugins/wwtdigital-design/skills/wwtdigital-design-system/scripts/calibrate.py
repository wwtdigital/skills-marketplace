#!/usr/bin/env python3
"""
Measure the deck-level metrics the new rules will test, and print them side by side.

    python3 scripts/calibrate.py good1.html good2.html ... --label a,b,c

This exists so thresholds are derived rather than invented. Every number in this
system that was guessed has had to be widened later: the mesh box list, the crop
list, the display-1 ladder step, the three-line headline cap. A deck-level rule is
worse to guess at than a slide-level one, because it fails whole documents.

Run it on decks we have accepted, read the spread, then set the threshold outside
the spread with margin. Re-run it after any rule change.
"""
import argparse, json, math, os, sys, collections

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import wwt_validate as V  # noqa: E402

CANVAS_W, CANVAS_H = 1920, 1080

# A photograph counts only at a real size. The crop table's smallest entry is the
# card at 525 x 260, which is 6.6% of the canvas, so 6% is the floor below which an
# image is a thumbnail or an icon rather than photography.
PHOTO_MIN_AREA = 0.06


def probe(path):
    from playwright.sync_api import sync_playwright
    with sync_playwright() as p:
        b = p.chromium.launch()
        pg = b.new_page(viewport={"width": 1980, "height": 1200})
        pg.goto("file://" + os.path.abspath(path))
        pg.wait_for_timeout(2500)
        pg.evaluate("""() => document.querySelectorAll('.stage').forEach(s => {
            s.style.setProperty('width','1920px','important');
            s.style.setProperty('max-width','none','important');
            s.style.setProperty('--k','1'); })""")
        pg.wait_for_timeout(500)
        slides = pg.evaluate(V.PROBE)
        b.close()
    return slides


# ---------------------------------------------------------------- metrics
def has(n, *names):
    cl = (n.get("cls") or "").split()
    return any(x in cl for x in names)


def qualifying_photo(s):
    """An <img> inside a .media at a real crop. Icons, logos and marks do not count."""
    best = 0.0
    for n in s["nodes"]:
        if n["tag"] != "img":
            continue
        if has(n, "mark") or (n["parentSel"] or "").find("lockup") >= 0:
            continue
        b = n["box"]
        area = (b["w"] * b["h"]) / float(CANVAS_W * CANVAS_H)
        if area > best:
            best = area
    return best


def substance(s):
    """Content atoms: things a reader actually reads or reads a number off.

    An empty panel is not an atom. Neither is a rail, a bug, a lockup or a mesh.
    This is the half of density that a big grey rectangle cannot fake.
    """
    atoms = 0
    words = 0
    SKIP = ("rail", "bug", "stripe", "mark", "lockup", "mesh", "brandx", "brandx-x",
            "tri", "arrow", "gridover", "doc-anno", "spec-note", "slidecap", "cap")
    for n in s["nodes"]:
        if has(n, *SKIP) or n["inChrome"]:
            continue
        if n["tag"] in ("br", "path", "g", "svg"):
            continue
        w = len((n.get("text") or "").split())
        if n["hasText"] and w >= 1:
            atoms += 1
            words += w
        elif n["tag"] in ("li", "td", "th"):
            atoms += 1
        elif has(n, "stat", "chip", "badge", "feat", "prac", "layer", "ring"):
            atoms += 1
        elif n["tag"] == "img" and not has(n, "mark"):
            atoms += 1
    return atoms, words


def structural(s):
    """Ink coverage, but an EMPTY panel counts as ground rather than as content.

    The old metric credited any .panel regardless of whether it held anything, so the
    cheapest way to pass a density floor was one enormous grey rectangle.
    """
    GW, GH = 192, 108
    grid = bytearray(GW * GH)
    for n in s["nodes"]:
        if has(n, "gridover", "stripe", "mark", "mesh", "brandx", "brandx-x", "scrim-wash") \
                or n["tag"] in ("path", "g", "br"):
            continue
        if has(n, "media"):
            b = n["box"]
            edges = ((b["x"] <= 2) + (b["y"] <= 2)
                     + (b["x2"] >= CANVAS_W - 2) + (b["y2"] >= CANVAS_H - 2))
            if edges >= 2:
                continue
        carries = (n["hasText"] or n.get("deepWords", 0) > 0
                   or n.get("deepImgs", 0) > 0 or n["tag"] == "img")
        if has(n, "panel") and not carries:
            continue                      # an empty panel is ground
        if not (n["hasText"] or has(n, "panel", "media", "device", "badge", "chip")
                or n["tag"] == "table"):
            continue
        b = n["box"]
        gx0 = max(0, int(b["x"] / CANVAS_W * GW)); gx1 = min(GW, int(math.ceil(b["x2"] / CANVAS_W * GW)))
        gy0 = max(0, int(b["y"] / CANVAS_H * GH)); gy1 = min(GH, int(math.ceil(b["y2"] / CANVAS_H * GH)))
        for gy in range(gy0, gy1):
            base = gy * GW
            for gx in range(gx0, gx1):
                grid[base + gx] = 1
    return sum(grid) / float(GW * GH)


def architecture(s):
    """What a reader perceives as "the same page", bucketed so a nudge cannot move it.

    Exact values were the flaw in the old signature: 20px of headline drift, or one
    extra decorative element in the census, read as a different page style. These
    buckets only change when the composition changes.
    """
    ground = "photo"
    for c in (s.get("slideCls") or "").split():
        if c.startswith("g-"):
            ground = c
    head = None
    for n in s["nodes"]:
        if has(n, "t-display1", "t-display2", "t-h1-lg", "t-h1", "t-h2"):
            head = n
            break
    if head is None:
        hb, hstep = "nohead", "none"
    else:
        y = head["box"]["y"]
        hb = "top" if y < 200 else ("upper" if y < 380 else ("mid" if y < 620 else "low"))
        hstep = next(t for t in ("t-display1", "t-display2", "t-h1-lg", "t-h1", "t-h2")
                     if has(head, t))
    # where the photography sits, which is the strongest thing the eye reads
    ph = "none"
    for n in s["nodes"]:
        if not has(n, "media"):
            continue
        b = n["box"]
        if b["w"] > 1700 and b["h"] > 1000:
            ph = "bleed"
        elif b["h"] > 900:
            ph = "left" if b["x"] < 700 else "right"
        elif b["w"] > 1400:
            ph = "band"
        else:
            ph = "inset"
        break
    # the dominant content form
    forms = []
    if any(n["tag"] == "table" for n in s["nodes"]):
        forms.append("table")
    if sum(1 for n in s["nodes"] if has(n, "stat")) >= 2:
        forms.append("stats")
    if sum(1 for n in s["nodes"] if has(n, "panel") and n.get("deepWords", 0) > 2) >= 2:
        forms.append("cards")
    if any(n["tag"] == "li" for n in s["nodes"]):
        forms.append("list")
    if any(n["tag"] == "svg" and n["box"]["w"] > 400 for n in s["nodes"]):
        forms.append("chart")
    if not forms:
        forms.append("prose")
    return "%s|%s|%s|%s|%s" % (ground, hb, hstep, ph, "+".join(sorted(set(forms))))


def entropy(counts):
    n = sum(counts)
    if n <= 1:
        return 1.0
    h = -sum((c / n) * math.log(c / n) for c in counts if c)
    hmax = math.log(min(len(counts), n)) if min(len(counts), n) > 1 else 1.0
    return h / hmax if hmax else 1.0


SPARSE_ROLES = {"cover", "divider", "statement", "closing"}


def report(label, slides):
    real = [s for s in slides if not s.get("isGallery") or True]
    n = len(real)
    photos = [qualifying_photo(s) for s in real]
    ok = [p >= PHOTO_MIN_AREA for p in photos]
    # longest run with no qualifying photograph
    run = best = 0
    for v in ok:
        run = 0 if v else run + 1
        best = max(best, run)
    light = [s for s in real if "g-light" in (s.get("slideCls") or "")]
    dev = [s for s in light if s["counts"]["mesh"] or s["counts"]["brandx"]
           or any(has(x, "tri") for x in s["nodes"])]
    subs = [substance(s) for s in real]
    strc = [structural(s) for s in real]
    arch = collections.Counter(architecture(s) for s in real)
    roles = collections.Counter((s.get("role") or "content") for s in real)
    sparse = sum(v for k, v in roles.items() if k in SPARSE_ROLES)

    print("\n=== %s  (%d slides) ===" % (label, n))
    print("  photography, qualifying (>=%.0f%% of canvas) : %d  = %.0f%%"
          % (PHOTO_MIN_AREA * 100, sum(ok), 100.0 * sum(ok) / n))
    print("  longest run of slides with no photograph    : %d" % best)
    print("  light-ground slides                         : %d" % len(light))
    print("  of those carrying a background device       : %d  = %s"
          % (len(dev), ("%.0f%%" % (100.0 * len(dev) / len(light))) if light else "n/a"))
    at = sorted(a for a, w in subs); wd = sorted(w for a, w in subs)
    print("  content atoms per slide   min %2d  p10 %2d  median %2d  max %2d"
          % (at[0], at[max(0, int(.1 * len(at)) - 1)], at[len(at) // 2], at[-1]))
    print("  words per slide           min %2d  p10 %2d  median %2d  max %2d"
          % (wd[0], wd[max(0, int(.1 * len(wd)) - 1)], wd[len(wd) // 2], wd[-1]))
    ss = sorted(strc)
    print("  structural coverage       min %.2f p10 %.2f median %.2f max %.2f"
          % (ss[0], ss[max(0, int(.1 * len(ss)) - 1)], ss[len(ss) // 2], ss[-1]))
    print("  distinct architectures    : %d for %d slides" % (len(arch), n))
    print("  largest single share      : %.0f%%  (%s)"
          % (100.0 * arch.most_common(1)[0][1] / n, arch.most_common(1)[0][0]))
    print("  architecture entropy      : %.2f  (1.00 = perfectly even)" % entropy(list(arch.values())))
    print("  sparse roles (cover/divider/statement/closing): %d = %.0f%%"
          % (sparse, 100.0 * sparse / n))
    lowest = sorted(range(n), key=lambda i: subs[i][0])[:5]
    print("  thinnest slides by atoms  : %s"
          % ", ".join("#%d(%d atoms,%d words,cov %.2f)" % (i, subs[i][0], subs[i][1], strc[i])
                      for i in lowest))
    return dict(n=n, photo=100.0 * sum(ok) / n, gap=best,
                dev=(100.0 * len(dev) / len(light)) if light else None,
                atoms_min=at[0], atoms_p10=at[max(0, int(.1 * len(at)) - 1)],
                words_min=wd[0], cov_min=ss[0], cov_p10=ss[max(0, int(.1 * len(ss)) - 1)],
                arch=len(arch), maxshare=100.0 * arch.most_common(1)[0][1] / n,
                ent=entropy(list(arch.values())), sparse=100.0 * sparse / n)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("files", nargs="+")
    ap.add_argument("--label")
    ap.add_argument("--json")
    a = ap.parse_args()
    labels = (a.label.split(",") if a.label else [os.path.basename(f) for f in a.files])
    out = {}
    for f, lab in zip(a.files, labels):
        out[lab] = report(lab, probe(f))
    if a.json:
        json.dump(out, open(a.json, "w"), indent=1)
    print()


if __name__ == "__main__":
    main()
