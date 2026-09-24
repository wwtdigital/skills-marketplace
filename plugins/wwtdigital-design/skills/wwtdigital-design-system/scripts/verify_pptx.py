#!/usr/bin/env python3
"""
Verify that a produced PPTX is a real deck rather than a stack of screenshots.

    python3 scripts/verify_pptx.py deck.pptx --html deck.html

This exists because a 91-slide WWT deck went to a client in which every single slide
was one flattened bitmap. No text, no fonts, nothing editable, and nothing in the
system objected. `export_pptx.py` had not been run: something rendered each HTML page
to an image and pasted it onto a slide.

That deck passed every rule we had, because every rule we had inspected HTML. This
script inspects the artefact that actually ships.

Checks, all FAIL:

  TXT-01  the file contains live text at all
  TXT-02  every slide whose HTML source carries text has text in the PPTX
  TXT-03  no slide is a single full-bleed picture and nothing else
  FNT-01  fonts are embedded AND the package is shaped so a reader will use them
  FNT-02  every run names a face in the Aptos family map, so nothing resolves to a
          substitute and nothing asks for a weight PowerPoint cannot express
  PPT-01  the canvas is 12192000 x 6858000 EMU, PowerPoint widescreen
  ZOR-01  decoration that sits behind the text in the HTML sits behind it here too
  FIL-01  every gradient-filled element in the HTML is still gradient-filled here
  PIC-01  baked decoration is the variant the source declares, matched by file hash
  PRB-01  the three rules above could actually run. They need the browser, and a run
          where the probe died used to print a note and then "0 FAIL"

The canvas rule here is PPT-01, not GEO-01. Both files used to call it GEO-01, so the
SKILL.md table's "GEO-01 | Canvas is 1920 x 1080" was the only row a reader could find and
it described the wrong one of two different rules. An id is a name; two rules cannot share
one. Found by check_provenance.py GEN-02.

Exit code 1 on any failure. Run it after export_pptx.py, every time.
"""
import argparse, glob, hashlib, os, re, sys, zipfile
from collections import Counter

# The baked decoration, hashed once, so a picture in the package can be identified as
# the asset it is rather than guessed at from its size. Empty when the skill's assets are
# not beside this script, in which case PIC-01 stays silent rather than guessing.
BAKED_SHA = {}
for _p in glob.glob(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                                 "assets", "export", "*.png")):
    try:
        BAKED_SHA[hashlib.sha1(open(_p, "rb").read()).hexdigest()] = \
            os.path.splitext(os.path.basename(_p))[0]
    except OSError:
        pass

NS = {"a": "http://schemas.openxmlformats.org/drawingml/2006/main",
      "p": "http://schemas.openxmlformats.org/presentationml/2006/main"}

# The five faces the export path is allowed to name. Aptos ships its heavy cuts as
# separate FAMILIES, so a run asking for "Aptos" at bold weight is Aptos Bold, never
# Aptos Black. Anything outside this set means a substitution happened somewhere.
APTOS = {"Aptos", "Aptos SemiBold", "Aptos ExtraBold", "Aptos Black",
         "Aptos Display", "Aptos Serif", "Aptos Narrow"}
CANVAS = (12192000, 6858000)


def check_embedding(z, fails, warns):
    """FNT-01, and it used to be a presence check.

    `if not fonts:` was the whole rule. It passed on a deck that carried three font parts,
    a content type, three relationships and a correctly sequenced <p:embeddedFontLst> and
    still rendered in DejaVu Sans on a machine without Aptos, because
    `embedTrueTypeFonts="1"` was missing from <p:presentation> and nothing looked at it.
    Five things have to hold, and a presence check tested one of them. Same doctrine as
    REG-40: a rule that checks whether a thing exists is not a rule that checks it works.
    """
    notes = []
    fonts = [f for f in z.namelist() if f.startswith("ppt/fonts/")]
    if not fonts:
        fails.append(("FNT-01", "deck",
                      "no embedded fonts. Aptos is not on most machines, so every headline "
                      "reflows on open. export_pptx.py embeds them"))
        return fonts, notes

    ct = z.read("[Content_Types].xml").decode("utf-8", "replace")
    if not re.search(r'<Default[^>]*Extension="fntdata"', ct):
        fails.append(("FNT-01", "deck",
                      "%d font part(s) with no <Default Extension=\"fntdata\"> in "
                      "[Content_Types].xml, so the parts are untyped and ignored" % len(fonts)))

    pres = z.read("ppt/presentation.xml").decode("utf-8", "replace")
    if not re.search(r'<p:presentation\b[^>]*embedTrueTypeFonts="(1|true)"', pres):
        fails.append(("FNT-01", "deck",
                      'embedTrueTypeFonts is not set on <p:presentation>. PowerPoint writes '
                      'it whenever it saves with embedding, so a package carrying font data '
                      'without it is not shaped like one PowerPoint made'))

    lst = re.search(r"<p:embeddedFontLst>.*?</p:embeddedFontLst>", pres, re.S)
    if not lst:
        fails.append(("FNT-01", "deck",
                      "%d font part(s) and no <p:embeddedFontLst>, so nothing declares "
                      "which typeface each part is" % len(fonts)))
        return fonts, notes

    # sequence position: CT_Presentation is an ordered sequence and the list belongs after
    # notesSz and before defaultTextStyle. Out of order, the whole file fails to open.
    i_n, i_l = pres.find("<p:notesSz"), pres.find("<p:embeddedFontLst>")
    i_d = pres.find("<p:defaultTextStyle")
    if i_n >= 0 and not (i_n < i_l < (i_d if i_d > 0 else 1 << 30)):
        fails.append(("FNT-01", "deck",
                      "<p:embeddedFontLst> is out of sequence in presentation.xml"))

    rels = z.read("ppt/_rels/presentation.xml.rels").decode("utf-8", "replace")
    targets = {m.group(1): m.group(2) for m in
               re.finditer(r'Id="([^"]+)"[^>]*Target="([^"]+)"', rels)}
    declared = 0
    for fm in re.finditer(r"<p:embeddedFont>(.*?)</p:embeddedFont>", lst.group(0), re.S):
        g = fm.group(1)
        tf = re.search(r'typeface="([^"]*)"', g)
        face = tf.group(1) if tf else "?"
        for slot, rid in re.findall(r'<p:(regular|bold|italic|boldItalic) r:id="([^"]+)"', g):
            declared += 1
            tgt = targets.get(rid)
            if not tgt:
                fails.append(("FNT-01", "deck",
                              "%s/%s points at %s, which is not a relationship"
                              % (face, slot, rid)))
                continue
            part = "ppt/" + tgt.replace("../", "")
            if part not in z.namelist():
                fails.append(("FNT-01", "deck",
                              "%s/%s points at %s, which is not in the package"
                              % (face, slot, part)))
                continue
            # the part has to BE a font, and it has to be the font it claims to be
            data = z.read(part)
            if data[:4] not in (b"\x00\x01\x00\x00", b"true", b"ttcf", b"OTTO"):
                fails.append(("FNT-01", "deck",
                              "%s is not a TrueType or OpenType file (starts %s). Raw TTF "
                              "is what fntdata takes; Word's obfuscated .odttf is not"
                              % (part, data[:4].hex())))
                continue
            name = ttf_family(data)
            if name and face and not name.lower().startswith(face.lower().split()[0]):
                fails.append(("FNT-01", "deck",
                              "%s declares typeface %r and the file's name table says %r"
                              % (part, face, name)))
    orphan = len(fonts) - declared
    if orphan > 0:
        warns.append(("FNT-01", "deck",
                      "%d font part(s) in the package that no embeddedFont slot declares"
                      % orphan))
    notes.append("embedding is a Windows PowerPoint feature: Mac PowerPoint, Keynote, "
                 "Google Slides and LibreOffice ignore it. Aptos installed on the opening "
                 "machine, or a PDF, is the durable answer")
    return fonts, notes


def ttf_family(data):
    """Family name out of a font's name table, so a part can be checked against the
    typeface it claims. Returns None rather than raising on anything unexpected."""
    try:
        import struct
        num = struct.unpack(">H", data[4:6])[0]
        for i in range(num):
            off = 12 + i * 16
            if data[off:off + 4] == b"name":
                o, _ = struct.unpack(">II", data[off + 8:off + 16])
                count, stroff = struct.unpack(">HH", data[o + 2:o + 6])
                best = None
                for j in range(count):
                    r = o + 6 + j * 12
                    pid, eid, lid, nid, ln, so = struct.unpack(">HHHHHH", data[r:r + 12])
                    if nid != 1:
                        continue
                    raw = data[o + stroff + so:o + stroff + so + ln]
                    txt = raw.decode("utf-16-be" if pid == 3 else "latin1", "replace")
                    best = best or txt.strip("\x00").strip()
                return best
    except Exception:
        return None
    return None


def slide_names(z):
    ns = [n for n in z.namelist() if re.fullmatch(r"ppt/slides/slide\d+\.xml", n)]
    return sorted(ns, key=lambda n: int(re.findall(r"\d+", os.path.basename(n))[0]))


def html_paint_order(path):
    """For each slide: where the decoration sits relative to the text, and how many
    gradient-filled elements there are.

    ZOR-01 exists because the exporter drew the Brand X after all the text on every cover,
    so it painted over the headline. It is semi-transparent, the headline showed through
    darkened, and it read as a design choice. Nothing caught it for several revisions:
    the validator only ever saw the HTML, and this script only checked that text existed.
    A tester found it by eye. That is the gap this closes.
    """
    try:
        from playwright.sync_api import sync_playwright
    except Exception:
        return None
    try:
        with sync_playwright() as pw:
            b = pw.chromium.launch()
            pg = b.new_page(viewport={"width": 1980, "height": 1200})
            pg.goto("file://" + os.path.abspath(path))
            pg.wait_for_timeout(2200)
            out = pg.evaluate("""() => [...document.querySelectorAll('.slide')].map(s => {
                const order = new Map(); let i = 0;
                s.querySelectorAll('*').forEach(n => order.set(n, i++));
                let firstText = Infinity;
                s.querySelectorAll('*').forEach(n => {
                  let t = ''; for (const c of n.childNodes) if (c.nodeType === 3) t += c.textContent;
                  if (!t.trim()) return;
                  if (n.closest('.rail, .bug, .lockup, .gridover')) return;
                  firstText = Math.min(firstText, order.get(n));
                });
                const bx = s.querySelector('.brandx-x, .brandx');
                const bxVariant = !bx ? null
                  : bx.classList.contains('brandx-x') ? 'brandx-cover'
                  : bx.classList.contains('brandx--r10') ? 'brandx-r10'
                  : 'brandx-UNKNOWN';
                let grads = 0;
                s.querySelectorAll('*').forEach(n => {
                  const cs = getComputedStyle(n);
                  if ((cs.backgroundImage || '').indexOf('linear-gradient') !== 0) return;
                  // .brandx belongs in this list for the same reason .bug and .mesh do:
                  // its gradient is real in CSS but it is clipped with clip-path, which
                  // PowerPoint has no equivalent for, so it ships as a baked PNG by
                  // design. Counting it as a gradient that must survive as a gradFill made
                  // FIL-01 fail every slide using recipe 10 for doing exactly the right
                  // thing, and PIC-01 is the rule that actually checks that plate.
                  if (n.closest('.bug, .mesh, .brandx, .brandx-x')) return;
                  const r = n.getBoundingClientRect();
                  if (r.width * r.height < 4000) return;
                  grads++;
                });
                // How many real photographs the SOURCE slide has, so PIC-01 can compare.
                // Only raster media counts: baked decoration is added by the exporter and
                // is legitimately absent from the HTML.
                let photos = 0;
                s.querySelectorAll('img').forEach(n => {
                  const src = n.getAttribute('src') || '';
                  if (!/^data:image\/(jpe?g|png)/.test(src)) return;
                  if (n.closest('.bug, .lockup, .mark')) return;
                  const r = n.getBoundingClientRect();
                  if (r.width * r.height < 40000) return;
                  photos++;
                });
                return { brandxBehindText: bx ? order.get(bx) < firstText : null, grads,
                         photos, brandx: bxVariant };
              })""")
            b.close()
            return out
    except Exception as e:
        print("  note: could not read the HTML source (%s); ZOR-01 and FIL-01 skipped" % e)
        return None


def html_text_per_slide(path):
    """How many words each source slide holds, so TXT-02 knows what to expect."""
    try:
        from playwright.sync_api import sync_playwright
    except Exception:
        return None
    try:
        with sync_playwright() as pw:
            b = pw.chromium.launch()
            pg = b.new_page(viewport={"width": 1980, "height": 1200})
            pg.goto("file://" + os.path.abspath(path))
            pg.wait_for_timeout(2000)
            out = pg.evaluate("""() => [...document.querySelectorAll('.slide')].map(s => {
                const c = s.cloneNode(true);
                c.querySelectorAll('.gridover,.doc-anno,.spec-note').forEach(e => e.remove());
                return (c.innerText || '').trim().split(/\\s+/).filter(Boolean).length;
            })""")
            b.close()
            return out
    except Exception as e:
        print("  note: could not read the HTML source (%s); TXT-02 skipped" % e)
        return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("pptx")
    ap.add_argument("--html", help="the HTML the deck was exported from, for TXT-02")
    ap.add_argument("--quiet", action="store_true")
    a = ap.parse_args()

    fails, warns = [], []
    z = zipfile.ZipFile(a.pptx)
    names = slide_names(z)
    n = len(names)

    pres = z.read("ppt/presentation.xml").decode("utf-8", "replace")
    m = re.search(r'sldSz[^>]*cx="(\d+)"[^>]*cy="(\d+)"', pres)
    if m and (int(m.group(1)), int(m.group(2))) != CANVAS:
        fails.append(("PPT-01", "deck",
                      "canvas %s x %s EMU, expected %d x %d (13.333 x 7.5in)"
                      % (m.group(1), m.group(2), *CANVAS)))

    fonts, font_notes = check_embedding(z, fails, warns)

    total_runs = 0
    faces = Counter()
    per_slide = []
    for k, nm in enumerate(names):
        x = z.read(nm).decode("utf-8", "replace")
        runs = re.findall(r"<a:t>(.*?)</a:t>", x, re.S)
        words = sum(len(r.split()) for r in runs)
        total_runs += len(runs)
        for t in re.findall(r'typeface="([^"]*)"', x):
            if t:
                faces[t] += 1
        pics = x.count("<p:pic>")
        shapes = x.count("<p:sp>")
        # a slide that is one picture at full canvas and nothing else is a screenshot
        full = False
        if pics == 1 and shapes == 0 and not runs:
            # Scan EVERY a:ext, not the first. The first one in a slide is the group
            # shape's own 0 x 0 placeholder, so a single regex silently measured nothing
            # and the check reported zero flattened slides on a deck that was entirely
            # flattened.
            for cx, cy in re.findall(r'<a:ext cx="(\d+)" cy="(\d+)"', x):
                if int(cx) > CANVAS[0] * 0.97 and int(cy) > CANVAS[1] * 0.97:
                    full = True
                    break
        per_slide.append(dict(idx=k, runs=len(runs), words=words, pics=pics,
                              shapes=shapes, flat=full))

    flat = [s["idx"] for s in per_slide if s["flat"]]
    if flat:
        fails.append(("TXT-03", "slides " + ",".join(map(str, flat[:14])) + ("..." if len(flat) > 14 else ""),
                      "%d of %d slides are a single full-bleed picture with no text. That is a "
                      "screenshot deck: nothing is editable and the type is pixels. Run "
                      "export_pptx.py, do not render pages to images" % (len(flat), n)))

    if total_runs == 0:
        fails.append(("TXT-01", "deck",
                      "no live text anywhere in %d slides. The client cannot fix a typo and "
                      "cannot copy a line out of it" % n))

    bad = {f: c for f, c in faces.items() if f not in APTOS}
    if bad:
        fails.append(("FNT-02", "deck",
                      "faces outside the Aptos map: %s. A weight is not a family here; "
                      "Aptos Black is its own family and 'Aptos' + bold gives Aptos Bold"
                      % ", ".join("%s x%d" % (k, v) for k, v in sorted(bad.items()))))

    if a.html:
        paint = html_paint_order(a.html)
        # A gate that cannot run is not a gate, and this one used to degrade to a pass.
        # When the Playwright probe fell over, html_paint_order returned None, ZOR-01,
        # FIL-01 and PIC-01 were all skipped, and the script printed "0 FAIL" and exited
        # zero. It did print a note first, but a note is not a verdict: a run of this
        # verifier on a deck whose badges had lost their gradient reported clean, and the
        # only reason anyone noticed was that the next three runs did not. Three of the
        # eight rules here need the browser, so if it is not there say so as a FAIL.
        if paint is None:
            fails.append(("PRB-01", "deck",
                          "the HTML probe could not run, so ZOR-01, FIL-01 and PIC-01 "
                          "were not checked. Paint order, gradient fills and baked "
                          "artwork identity are unverified. Install Playwright and "
                          "Chromium, or say plainly that these three did not run"))
        elif len(paint) < n:
            fails.append(("PRB-01", "deck",
                          "the HTML source has %d slides and the PPTX has %d, so the two "
                          "cannot be compared slide for slide and ZOR-01, FIL-01 and "
                          "PIC-01 were not checked" % (len(paint), n)))
        if paint and len(paint) >= n:
            zbad, fbad = [], []
            for k, nm in enumerate(names):
                x = z.read(nm).decode("utf-8", "replace")
                i = x.find("<p:spTree>")
                shapes = list(re.finditer(r"<p:(sp|pic)>.*?</p:\1>", x[i:], re.S))
                first_text = next((j for j, m in enumerate(shapes)
                                   if "<a:t>" in m.group(0)), None)
                # the Brand X is the only full-canvas picture on a cover
                bx_idx = next((j for j, m in enumerate(shapes)
                               if m.group(1) == "pic"
                               and re.search(r'<a:ext cx="1219\d{4}" cy="685\d{4}"', m.group(0))
                               and j > 0), None)
                want_behind = paint[k].get("brandxBehindText")
                if want_behind and first_text is not None and bx_idx is not None \
                        and bx_idx > first_text:
                    zbad.append(k)
                got = sum(1 for m in shapes if "<a:gradFill" in m.group(0))
                if paint[k]["grads"] and got < paint[k]["grads"]:
                    fbad.append((k, paint[k]["grads"], got))
            if zbad:
                fails.append(("ZOR-01", "slides " + ",".join(map(str, zbad[:12])),
                              "decoration that sits BEHIND the text in the HTML is painted "
                              "OVER it here. On a cover that means the Brand X covering the "
                              "headline. Paint order comes from DOM order"))
            # ---- PIC-01 baked decoration matches the variant the source declares.
            #
            # The first cut of this rule counted full-canvas pictures and it was the wrong
            # test. The slide that shipped illegible had exactly the right NUMBER of
            # pictures, a ground plate and one Brand X, and the wrong ARTWORK in the second
            # one: the exporter matched any Brand X and painted the cover's plate onto a
            # light content slide. Counting would never have caught it, and a rule that
            # cannot catch the defect it was written for is worse than no rule, because it
            # reads as coverage.
            #
            # So compare identity. Each baked device is a file whose bytes are known, so
            # hash the assets once and ask whether the plate on the slide is the plate the
            # source's own classes call for.
            pbad = []
            if BAKED_SHA:
                for k, nm in enumerate(names):
                    want = paint[k].get("brandx")          # e.g. 'brandx-r10', or None
                    x = z.read(nm).decode("utf-8", "replace")
                    rp = "ppt/slides/_rels/%s.rels" % os.path.basename(nm)
                    if rp not in z.namelist():
                        continue
                    tmap = {m.group(1): m.group(2) for m in re.finditer(
                        r'Id="([^"]+)"[^>]*Target="([^"]+)"',
                        z.read(rp).decode("utf-8", "replace"))}
                    got = set()
                    for rid, tgt in tmap.items():
                        if "media/" not in tgt:
                            continue
                        part = "ppt/" + tgt.replace("../", "")
                        if part not in z.namelist():
                            continue
                        h = hashlib.sha1(z.read(part)).hexdigest()
                        if h in BAKED_SHA and BAKED_SHA[h].startswith("brandx"):
                            got.add(BAKED_SHA[h])
                    if want and got and want not in got:
                        pbad.append((k, want, sorted(got)))
                    elif not want and got:
                        pbad.append((k, "no Brand X", sorted(got)))
            if pbad:
                fails.append(("PIC-01", "slides " + ",".join(str(t[0]) for t in pbad[:12]),
                              "the export carries a different Brand X from the one the "
                              "source declares: "
                              + "; ".join("slide %d wants %s, has %s" % (k, w, ",".join(g))
                                          for k, w, g in pbad[:6])
                              + ". Every variant is a different shape from a different node, "
                                "so the wrong plate lands as artwork the design never had"))
            if fbad:
                fails.append(("FIL-01", "slides " + ",".join(str(k) for k, _, _ in fbad[:12]),
                              "gradient-filled elements lost their fill: "
                              + "; ".join("slide %d had %d, has %d" % t for t in fbad[:6])
                              + ". A deck-local class with a gradient is invisible to the "
                                "exporter and becomes a flat box"))
        src = html_text_per_slide(a.html)
        if src and len(src) >= n:
            empty = [s["idx"] for s in per_slide
                     if src[s["idx"]] >= 12 and s["words"] < max(3, src[s["idx"]] * 0.25)]
            if empty:
                fails.append(("TXT-02", "slides " + ",".join(map(str, empty[:14])),
                              "%d slides carry far less text than their HTML source, so text "
                              "was dropped or flattened in export" % len(empty)))

    if not a.quiet:
        print("\nWWT PPTX verifier — %s" % os.path.basename(a.pptx))
        print("  %d slides   %d text runs   %d embedded font file(s)   %d flattened"
              % (n, total_runs, len(fonts), len(flat)))
        if faces:
            print("  faces: " + ", ".join("%s x%d" % (k, v) for k, v in sorted(faces.items())))
        for n in font_notes:
            print("  note:  " + n)
        print()
        for rid, where, msg in fails:
            print("  FAIL %-7s %-22s %s" % (rid, where, msg))
        for rid, where, msg in warns:
            print("  WARN %-7s %-22s %s" % (rid, where, msg))
        print("\n  %d FAIL   %d WARN\n" % (len(fails), len(warns)))
        if not fails:
            print("  live text, embedded fonts, nothing flattened.\n")

    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
