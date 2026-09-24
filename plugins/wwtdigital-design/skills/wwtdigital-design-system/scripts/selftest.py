#!/usr/bin/env python3
"""
Prove the rules catch every gaming move, and prove they leave good work alone.

    python3 scripts/selftest.py --head ../src/head.html

Builds the fixtures in gaming_fixtures.py, validates each, and checks that the expected
rule fired. The first fixture is the NEGATIVE CONTROL: legitimate work that must come
back clean. A rule set that fails everything is not strict, it is broken, and the control
is the only thing that tells the two apart.

After the HTML-side checks, one more runs: the control fixture's cover is actually
exported through export_pptx.py, and the resulting PPTX's shape order is checked
directly (photo, then Brand X, then the headline text). See REG-43. This is the only
check in this file that touches the exporter, and it needs python-pptx.

Run this after any threshold change. Exit code 1 if the control is dirty, any gaming
move slips through, or the export loses its paint order.
"""
import argparse, os, subprocess, sys, tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)

# fixture -> the rule that has to catch it. Alternatives separated by "|".
EXPECT = {
    "empty_panel": "DEN-06|DEN-07",   # coverage bulked out with one huge empty panel
    "mesh_only":   "DEN-06|DEN-07",   # a background device added, nothing else designed
    "thumbnail":   "IMG-05",          # the photography quota met with 120 x 90 images
    "frontload":   "IMG-06",          # the quota met on the first slides, then nothing
    "role_shop":   "SEQ-04",          # thin slides relabelled to reach a lower bar
    "nudge":       "SEQ-02",          # one architecture, headline nudged 20px a slide
    "cont":        "SEQ-05",          # content spilled onto "(cont.)" slides
    "twins":       "SEQ-03",          # the same slide shipped twice
    "white_cards": "COL-07",          # grey cards on white, the inverted elevation
    "offaxis":     "TYP-11",          # a centred headline in a 1776 box at left:0
    "banner":      "TYP-04",          # a left-aligned headline run past the measure
    "ragged":      "GEO-06",          # a side-by-side set with unequal bottoms
    "placeholder": "DEN-08",          # Lorem ipsum shipped as body copy
    "dark_overuse": "PAT-09",         # the dark emphasis ground on half the deck
    "dark_run":     "PAT-09",         # two dark emphasis slides back to back
    "gallery_claim": "GAL-01",        # a thin deck declaring itself a reference gallery
    "spec_role":    "DEN-06|DEN-07|SEQ-01",  # every slide labelled a documentation specimen
    "false_build":  "SEQ-01|SEQ-03",  # a repeat declaring data-builds-on to clear the rule
    "reuse_photo":  "IMG-07|IMG-08",  # the photography quota met with one frame, reused
}


def run(cmd):
    return subprocess.run(cmd, capture_output=True, text=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--head", default=os.path.join(HERE, "..", "..", "..", "src", "head.html"))
    ap.add_argument("--keep", action="store_true")
    a = ap.parse_args()
    out = tempfile.mkdtemp(prefix="wwt-selftest-")
    head = os.path.abspath(a.head)
    if not os.path.exists(head):
        # The repo's src/head.html is not in the shipped skill, so on a coworker's machine
        # the self-test used to refuse to run at all. It does not need that file: it needs
        # a document head carrying the system stylesheet and the fonts, and the skill ships
        # both. Compose one rather than sending the user to find a path they do not have.
        css = os.path.join(ROOT, "assets", "system.css")
        if not os.path.exists(css):
            sys.exit("no %s and no assets/system.css to compose one from" % head)
        head = os.path.join(out, "head.html")
        # Mirror src/head.html exactly: FONT_FACES is its own <style> block and sits
        # OUTSIDE the stylesheet, the chrome follows the system CSS, and the file stops at
        # <body> because gaming_fixtures.py slices at the last </style> and appends the
        # rest itself. The first attempt folded the faces inside the style block and
        # dropped the chrome, and the negative control came back DIRTY on four rules, which
        # reads exactly like a real regression.
        chrome = os.path.join(ROOT, "assets", "spec-chrome.css")
        open(head, "w", encoding="utf-8").write(
            "<!DOCTYPE html>\n<html lang=\"en\">\n<head>\n<meta charset=\"utf-8\">\n"
            "<title>WWT selftest</title>\n{{FONT_FACES}}\n<style>\n"
            + open(css, encoding="utf-8").read() + "\n"
            + (open(chrome, encoding="utf-8").read() if os.path.exists(chrome) else "")
            + "\n</style>\n</head>\n<body>\n")
        print("  composed a head from assets/system.css (src/head.html not present)")
    run([sys.executable, os.path.join(HERE, "gaming_fixtures.py"), "--out", out, "--head", head])

    rows = []
    ok = True
    names = ["control"] + sorted(EXPECT)
    for name in names:
        raw = os.path.join(out, name + ".raw.html")
        built = os.path.join(out, name + ".html")
        r = run([sys.executable, os.path.join(HERE, "inline_assets.py"), raw, "-o", built])
        if r.returncode != 0:
            rows.append((name, "BUILD FAIL", "", r.stderr.strip()[:70]))
            ok = False
            continue
        v = run([sys.executable, os.path.join(HERE, "wwt_validate.py"), built, "--quiet",
                 "--json", os.path.join(out, name + ".json")])
        import json
        rep = json.load(open(os.path.join(out, name + ".json")))
        fired = sorted({f["rule"] for f in rep["findings"] if f["sev"] == "FAIL"})
        if name == "control":
            verdict = "CLEAN" if not fired else "DIRTY"
            if fired:
                ok = False
            rows.append((name, verdict, "none", " ".join(fired)))
        else:
            want = EXPECT[name].split("|")
            hit = any(w in fired for w in want)
            if not hit:
                ok = False
            rows.append((name, "CAUGHT" if hit else "MISSED", EXPECT[name], " ".join(fired)))

    # ---- export z-order regression guard (REG-43, exercises REG-23) ----
    # Every check above tests wwt_validate.py against the HTML. None of them ever run
    # export_pptx.py, so the exact defect class REG-23 describes, a background device
    # painted over the headline once the deck reaches PowerPoint, had no test standing
    # over it. The control fixture's cover slide (full-bleed photo, Brand X, white
    # headline) is the scenario that reproduced it originally, so this exports THAT
    # fixture for real and checks the actual shape order in the resulting PPTX, rather
    # than re-reading the HTML or the exporter's source.
    name = "export_order"
    control_html = os.path.join(out, "control.html")
    try:
        if not os.path.exists(control_html):
            raise RuntimeError("control.html was never built (see the control row above)")
        control_pptx = os.path.join(out, "control.pptx")
        r = run([sys.executable, os.path.join(HERE, "export_pptx.py"), control_html,
                 "-o", control_pptx, "--no-embed"])
        if r.returncode != 0:
            raise RuntimeError("export_pptx.py failed: %s" % r.stderr.strip()[-300:])

        from pptx import Presentation
        from pptx.enum.shapes import MSO_SHAPE_TYPE

        brandx_path = os.path.join(ROOT, "assets", "export", "brandx-cover.png")
        brandx_blob = open(brandx_path, "rb").read()

        shapes = list(Presentation(control_pptx).slides[0].shapes)
        brandx_idx = photo_idx = text_idx = None
        best_area = -1
        for idx, sh in enumerate(shapes):
            if sh.shape_type == MSO_SHAPE_TYPE.PICTURE:
                # The Brand X plate is placed unmodified, so it byte-matches its source
                # exactly. The photo does not: it is cropped and re-encoded by PIL on the
                # way in, so this is the one reliable way to tell "the wedge" from "the
                # photo" when both happen to be full-canvas pictures. Area alone cannot
                # do it, and this is exactly why REG-41 existed: a boolean, not an
                # identity check, is how the wrong plate got painted before.
                if brandx_idx is None and sh.image.blob == brandx_blob:
                    brandx_idx = idx
                    continue
                area = sh.width * sh.height
                if area > best_area:
                    best_area, photo_idx = area, idx
            elif text_idx is None and sh.has_text_frame and sh.text_frame.text.strip():
                text_idx = idx

        gaps = [n for n, v in (("brandx", brandx_idx), ("photo", photo_idx),
                                ("headline text", text_idx)) if v is None]
        if gaps:
            raise RuntimeError("could not find in the exported slide: %s" % ", ".join(gaps))

        order_str = "photo=%d brandx=%d text=%d" % (photo_idx, brandx_idx, text_idx)
        if photo_idx < brandx_idx < text_idx:
            rows.append((name, "PASS", "photo<brandx<text", order_str))
        else:
            ok = False
            rows.append((name, "FAIL", "photo<brandx<text", order_str))
    except Exception as e:
        ok = False
        rows.append((name, "ERROR", "photo<brandx<text", str(e)[:160]))

    # ---- pseudo-element decoration guard (REG-48) ----
    # querySelectorAll('*') cannot see a ::before/::after, so the cover's scrim -- the 36%
    # wash the CSS calls .scrim-flat, present on this very control fixture -- exported as
    # nothing at all until export_pptx.py's probe() gained a second pass that reads pseudo
    # computed style directly. Reuses the control.pptx built above rather than a fixture of
    # its own, since the control cover already carries a scrim. The bullet dot and the
    # painted-text plate get their own fixture below rather than an extension of control():
    # the negative control is the one file in this set whose job is to stay unchanged, and
    # this file already records a run where composing its head differently turned it DIRTY
    # on four rules and read exactly like a real regression.
    name = "pseudo_scrim"
    try:
        from lxml import etree
        ns = {"a": "http://schemas.openxmlformats.org/drawingml/2006/main"}
        found = False
        for sh in shapes:
            if sh.shape_type == MSO_SHAPE_TYPE.PICTURE or (sh.has_text_frame and sh.text_frame.text.strip()):
                continue
            alphas = sh._element.findall(".//a:alpha", ns)
            for alpha_el in alphas:
                # NOT "a": main() already binds that to the argparse namespace, and this
                # function shares its scope. REG-46 documented exactly this mistake with a
                # different variable; a loop here nearly made it twice in the same file.
                val = int(alpha_el.get("val", "100000"))
                if val < 90000:          # meaningfully transparent, not just rounding noise
                    found = True
                    break
            if found:
                break
        rows.append((name, "PASS" if found else "FAIL", "a scrim shape with alpha<90%",
                     "found" if found else "no semi-transparent non-text, non-picture shape"))
        if not found:
            ok = False
    except Exception as e:
        ok = False
        rows.append((name, "ERROR", "a scrim shape with alpha<90%", str(e)[:160]))

    # ---- bullet dot and painted-text plate (REG-48, REG-49) ----
    # Two components the control cannot cover. `ul.b li::before` is the bullet dot, a round
    # pseudo in the gutter its host reserves with padding-left:40px, and `.badge` is a
    # painted element that OWNS its text: a gradient square with a white numeral centred in
    # it by place-items, which the exporter dropped entirely because a box was only emitted
    # for elements with no text of their own. Three badges anchor a slide in the worked
    # example and all three exported as invisible white numerals on a light card.
    #
    # Built as its own one-slide page, exported for real, and measured against the numbers
    # the CSS states rather than against a screenshot: the dot is round and sits inside the
    # 40px gutter, ahead of its text; the badge keeps a gradient fill at its own 96 x 96
    # border box, not at the text box's bearing-expanded one.
    name = "pseudo_bullet"
    try:
        body = ('<div class="stage"><div class="slide" data-role="content" '
                'style="background:#F6F6F6">'
                '<ul class="b abs" style="left:200px;top:300px;width:900px">'
                '<li>First item in the list</li><li>Second item in the list</li></ul>'
                '<div class="badge abs" style="left:200px;top:700px">01</div>'
                '</div></div></body></html>')
        with open(head) as fh:
            page = fh.read()
        fx = os.path.join(out, "pseudo.raw.html")
        with open(fx, "w") as fh:
            fh.write(page + body)
        fxb = os.path.join(out, "pseudo.html")
        r = run([sys.executable, os.path.join(HERE, "inline_assets.py"), fx, "-o", fxb])
        if r.returncode != 0:
            raise RuntimeError("inline_assets.py failed: %s" % r.stderr.strip()[-200:])
        fxp = os.path.join(out, "pseudo.pptx")
        r = run([sys.executable, os.path.join(HERE, "export_pptx.py"), fxb,
                 "-o", fxp, "--no-embed"])
        if r.returncode != 0:
            raise RuntimeError("export_pptx.py failed: %s" % r.stderr.strip()[-200:])

        from pptx import Presentation as _P
        EMU = 6350
        sh2 = list(_P(fxp).slides[0].shapes)
        dots = [s for s in sh2 if not (s.has_text_frame and s.text_frame.text.strip())
                and s.shape_type != MSO_SHAPE_TYPE.PICTURE
                and round(s.width / EMU) == 14 and round(s.height / EMU) == 14]
        li_x = min([round(s.left / EMU) for s in sh2
                    if s.has_text_frame and "item in the list" in s.text_frame.text] or [0])
        # The dot lives in the gutter: at or after the list's own left edge, and before the
        # text. The text box carries a -6 optical bearing, so compare against li_x + 6.
        gutter = bool(dots) and all(200 <= round(d.left / EMU) < li_x + 6 for d in dots)
        badge = [s for s in sh2 if not (s.has_text_frame and s.text_frame.text.strip())
                 and round(s.width / EMU) == 96 and round(s.height / EMU) == 96
                 and round(s.left / EMU) == 200 and round(s.top / EMU) == 700]
        grad = bool(badge) and badge[0]._element.findall(
            ".//{http://schemas.openxmlformats.org/drawingml/2006/main}gradFill")
        good = len(dots) == 2 and gutter and bool(grad)
        rows.append((name, "PASS" if good else "FAIL", "2 dots in the gutter + badge plate",
                     "dots=%d gutter=%s badge_gradient=%s"
                     % (len(dots), gutter, bool(grad))))
        if not good:
            ok = False
    except Exception as e:
        ok = False
        rows.append((name, "ERROR", "2 dots in the gutter + badge plate", str(e)[:160]))

    # ---- icons survive the export (REG-52) ----
    # PowerPoint has no SVG, so an icon that is not rasterised simply disappears, which is
    # the FDU partner-logo failure with a different asset. Nothing else in this file would
    # notice: the HTML would validate, the PPTX would have live text and embedded fonts,
    # and the marks would just be gone. Builds a two-slide fixture carrying icons in three
    # inks, exports it for real, and checks the pictures arrive.
    name = "icons_export"
    try:
        icons_raw = os.path.join(out, "icons.raw.html")
        with open(head, encoding="utf-8") as fh:
            page = fh.read()
        with open(icons_raw, "w", encoding="utf-8") as fh:
            fh.write(page + """<div class="stage"><div class="slide" data-role="content"
              style="background:#F6F6F6">
              <span class="ico ico--96 ico--blue abs" style="left:72px;top:300px"
                    role="img" aria-label="Assessment">{{ICON_assessment}}</span>
              <span class="ico ico--48 abs" style="left:300px;top:300px"
                    aria-hidden="true">{{ICON_gear}}</span></div></div>
              <div class="stage"><div class="slide on-dark" data-role="statement"
              style="background:linear-gradient(165deg,#1D569E,#28115C)">
              <span class="ico ico--96 abs" style="left:72px;top:300px"
                    role="img" aria-label="Users">{{ICON_users}}</span>
              </div></div></body></html>""")
        icons_html = os.path.join(out, "icons.html")
        r = run([sys.executable, os.path.join(HERE, "inline_assets.py"),
                 icons_raw, "-o", icons_html])
        if r.returncode != 0:
            raise RuntimeError("inline_assets.py failed: %s" % r.stderr.strip()[-200:])
        # currentColor must survive as RAW MARKUP. A data URI cannot see the page's color,
        # so this is the check that the inliner did not "helpfully" base64 them.
        body = open(icons_html, encoding="utf-8").read()
        if "currentColor" not in body:
            raise RuntimeError("no currentColor in the built file: the icons were inlined "
                               "as data URIs and can no longer take the slide's ink")
        icons_pptx = os.path.join(out, "icons.pptx")
        r = run([sys.executable, os.path.join(HERE, "export_pptx.py"),
                 icons_html, "-o", icons_pptx, "--no-embed"])
        if r.returncode != 0:
            raise RuntimeError("export_pptx.py failed: %s" % r.stderr.strip()[-200:])
        from pptx import Presentation as _P
        from pptx.enum.shapes import MSO_SHAPE_TYPE as _T
        prs = _P(icons_pptx)
        npic = [sum(1 for sh in sl.shapes if sh.shape_type == _T.PICTURE)
                for sl in prs.slides]
        good = len(npic) == 2 and npic[0] >= 2 and npic[1] >= 1
        rows.append((name, "PASS" if good else "FAIL", "icons reach the PPTX",
                     "pictures per slide: %s" % npic))
        if not good:
            ok = False
    except Exception as e:
        ok = False
        rows.append((name, "ERROR", "icons reach the PPTX", str(e)[:160]))

    w = max(len(r[0]) for r in rows)
    print("\nWWT rule self-test")
    print("  %-*s %-7s %-14s %s" % (w, "FIXTURE", "VERDICT", "EXPECTED", "RULES THAT FIRED"))
    for n, v, e, f in rows:
        print("  %-*s %-7s %-14s %s" % (w, n, v, e, f))
    print()
    if ok:
        print("  the control is clean and every gaming move is caught.\n")
    else:
        print("  SELF-TEST FAILED. Either a threshold has drifted or a loophole is open.\n")
    if not a.keep:
        import shutil
        shutil.rmtree(out, ignore_errors=True)
    else:
        print("  fixtures kept in %s\n" % out)
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
