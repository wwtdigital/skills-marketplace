#!/usr/bin/env python3
"""
Inline the skill's bundled assets into a slide HTML file, producing one
self-contained document that opens anywhere with no external files.

    python3 scripts/inline_assets.py deck.html -o WWT-Deck.html

Placeholders recognised in the source HTML:

    {{IMG_<id>}}      any id in assets/manifest.json, e.g. {{IMG_wall-touch}}
    {{ICON_<name>}}   any mark in assets/icons/manifest.json, e.g. {{ICON_assessment}}.
                      Raw inline SVG so `currentColor` still reaches it
    {{MESH_DIAG}}     {{MESH_CENTER}}   {{MESH_H}}   {{MESH_DARK}}
    {{TRI}}           {{BRANDX_X}}
    {{LOGO_WHITE}}    {{LOGO_INK}}      {{BUG_MARK}}
    {{ARROW_SVG}}     raw inline SVG, not a data URI, so CSS can recolour it
    {{BRANDX}} {{BRANDX10}}  {{RING}} {{RING2}} {{RING3}} {{CHEVRON}} {{RULE}}
    {{MATRIX}}        {{ICO_INVENTORY}} {{ICO_MISSION}} {{ICO_SHIPPING}}
    {{FONT_FACES}}    a <style> block embedding the Aptos cuts, read from this machine
                      (scripts/brand_assets.py says where it looks; they are not shipped)
    {{SYSTEM_CSS}}    assets/system.css verbatim, the one copy of the stylesheet
    {{SPEC_CHROME_CSS}}  assets/spec-chrome.css, the reference document's own furniture

Exits non-zero if any placeholder is left unresolved, so a typo fails the
build instead of shipping a broken image.
"""
import argparse, base64, json, os, re, sys

import brand_assets

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
A = lambda *p: os.path.join(ROOT, "assets", *p)

MIME = {".svg": "image/svg+xml", ".jpg": "image/jpeg", ".jpeg": "image/jpeg",
        ".png": "image/png", ".webp": "image/webp"}


def uri(path):
    ext = os.path.splitext(path)[1].lower()
    if ext not in MIME:
        sys.exit(f"unknown asset type: {path}")
    with open(path, "rb") as fh:
        return "data:%s;base64,%s" % (MIME[ext], base64.b64encode(fh.read()).decode())


def build_map(html=""):
    m = {}
    # Raw CSS, not a data URI. assets/system.css is the single copy of the stylesheet;
    # anything that carries its own frozen duplicate drifts (REG-28).
    for key, rel in (("SYSTEM_CSS", "system.css"), ("SPEC_CHROME_CSS", "spec-chrome.css")):
        p = A(rel)
        m["{{%s}}" % key] = open(p).read() if os.path.exists(p) else ""
    with open(A("manifest.json")) as fh:
        for pid, meta in json.load(fh).items():
            m["{{IMG_%s}}" % pid] = uri(os.path.join(ROOT, meta["file"]))

    for key, rel in {
        "MESH_DIAG": "vectors/mesh-diag.svg",   "MESH_CENTER": "vectors/mesh-center.svg",
        "MESH_H": "vectors/mesh-h.svg",         "BUG_MARK": "vectors/bug-mark.svg",
        "MESH_DARK": "vectors/mesh-dark.svg",
        "TRI": "vectors/flex-triangle.svg",
        "BRANDX_X": "vectors/brandx-cover.svg",
        "BRANDX": "vectors/x-big.svg",          "BRANDX10": "components/brandx10.svg",
        "RING": "components/ring1.svg",         "RING2": "components/ring2.svg",
        "RING3": "components/ring3.svg",
        "CHEVRON": "components/chevron.svg",    "RULE": "components/rule.svg",
        "MATRIX": "components/matrix.jpg",      "ICO_INVENTORY": "components/ico-inventory.png",
        "ICO_MISSION": "components/ico-mission.png",
        "ICO_SHIPPING": "components/ico-shipping.png",
    }.items():
        m["{{%s}}" % key] = uri(A(*rel.split("/")))

    # The logo ships white. The ink variant is the same artwork recoloured, so it
    # stays one source file and the two can never drift apart.
    with open(A("vectors", "logo-full.svg")) as fh:
        white = fh.read()
    b64 = lambda s: "data:image/svg+xml;base64," + base64.b64encode(s.encode()).decode()
    m["{{LOGO_WHITE}}"] = b64(white)
    m["{{LOGO_INK}}"] = b64(white.replace('fill="white"', 'fill="#1F1F1F"'))

    # The arrow goes in as live markup, not a data URI, because .arrow--down
    # mirrors it with a CSS transform and a data URI cannot be transformed.
    with open(A("vectors", "arrow-red.svg")) as fh:
        m["{{ARROW_SVG}}"] = fh.read().strip()

    # ---- {{ICON_<name>}} for every mark in assets/icons/manifest.json.
    #
    # RAW MARKUP, NEVER A DATA URI, and this is not a preference. 422 of the 429 universal
    # icons paint with `currentColor` so one file serves the light surface and the dark
    # emphasis ground. A data URI is an opaque external document: it cannot see the page's
    # `color`, so every one of them would render black on the dark ground and the whole
    # point of the inheritance would be lost. An <img src="data:..."> also cannot be
    # recoloured by CSS at all, which is the same trap `.arrow` is documented for above.
    #
    # Branded marks resolve through the same placeholder namespace rather than a second
    # one. Keeping them addressable is deliberate: the source sheet says they are not for
    # universal use, which is a reason to WARN and ask for a justification, not a reason to
    # make a WWT deck unable to show the ATC Portal icon on a slide about the ATC Portal.
    # `lint_source.py` ICO-02 is what asks.
    # The markup is one file, not 497 loose SVGs. A skill package is capped at 200 files
    # and the loose set put this one at 610, which is a limit nobody finds out about until
    # it is refused. assets/icons/manifest.json keeps the names and the provenance and
    # stays small enough for the 30ms lint; assets/icons/icons.json carries the megabyte.
    bp = A("icons", "icons.json")
    if os.path.exists(bp):
        with open(bp, encoding="utf-8") as fh:
            for name, svg in json.load(fh).items():
                m["{{ICON_%s}}" % name] = svg.strip()

    if "{{FONT_FACES}}" in html:
        m["{{FONT_FACES}}"] = font_faces(uses_serif(html))
    return m


# Aptos ships its heavier cuts as separate FAMILIES — the Black file reports family
# "Aptos Black", not weight 900 of family "Aptos". So asking for `font-family:Aptos;
# font-weight:900` finds nothing and the browser fakes a bold, which is why headlines
# came out light. These rules bind each weight to its real file and end the guessing.
# Aptos Narrow was removed at v2.0 by direction: the design does not use it. Dropping the
# faces as well as the token means nothing can quietly fall back into it.
#
# The files come from this machine, not the package (brand_assets.py). A bundled WOFF2 is
# used if there is one; otherwise the TTF that Office or the Microsoft download installed.
FACES = [
    ("Aptos",        400, "normal", "Aptos"),
    ("Aptos",        600, "normal", "Aptos SemiBold"),
    ("Aptos",        700, "normal", "Aptos Bold"),
    ("Aptos",        800, "normal", "Aptos ExtraBold"),
    ("Aptos",        900, "normal", "Aptos Black"),
    ("Aptos Serif",  700, "italic", brand_assets.SERIF),
]
FORMAT = {".woff2": ("font/woff2", "woff2"), ".ttf": ("font/ttf", "truetype"),
          ".otf": ("font/otf", "opentype")}


def uses_serif(html):
    """Aptos Serif is only for pull quotes, and it is the cut most machines lack (Office
    fetches it on first use). Require it only when the deck sets one. Checked before the
    stylesheet is inlined, because system.css defines .t-quote whether it is used or not."""
    return bool(re.search(r"""class\s*=\s*["'][^"']*\bt-quote\b|var\(\s*--font-serif|Aptos Serif""", html))


def font_faces(serif=True):
    faces = [f for f in FACES if serif or f[3] != brand_assets.SERIF]
    paths = brand_assets.require_fonts([f[3] for f in faces])
    if not serif and brand_assets.font_path(brand_assets.SERIF):
        faces = FACES
        paths[brand_assets.SERIF] = brand_assets.font_path(brand_assets.SERIF)
    out = ["<style>"]
    for fam, weight, style, face in faces:
        mime, fmt = FORMAT[os.path.splitext(paths[face])[1].lower()]
        with open(paths[face], "rb") as fh:
            b64 = base64.b64encode(fh.read()).decode()
        out.append(
            "@font-face{font-family:'%s';font-style:%s;font-weight:%d;font-display:block;"
            "src:url(data:%s;base64,%s) format('%s')}" % (fam, style, weight, mime, b64, fmt))
    # No synthetic bolding or slanting anywhere. If a weight is missing it should look
    # wrong in review, not be quietly faked at render time.
    out.append("html{font-synthesis:none;-webkit-font-smoothing:antialiased}")
    out.append("</style>")
    return "\n".join(out)


# Every .slide is a fixed 1920 x 1080 box scaled into its .stage by the --k custom
# property. If nothing sets --k it stays at 1, the slide overflows a narrower stage, and
# `overflow:hidden` crops the right and bottom of every page with no error anywhere.
# The validator cannot catch this: it forces every stage to native size before measuring,
# which is exactly the condition that hides it. So the script ships with the build.
FIT = """
<script>
(function(){
  var stages = document.querySelectorAll('.stage');
  function fit(){ stages.forEach(function(st){
    st.style.setProperty('--k', (st.clientWidth / 1920).toFixed(6)); }); }
  fit();
  window.addEventListener('resize', fit);
  if (window.ResizeObserver){ var ro = new ResizeObserver(fit); stages.forEach(function(s){ ro.observe(s); }); }
  if (document.fonts) document.fonts.ready.then(fit);
})();
</script>
"""


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("source")
    ap.add_argument("-o", "--out", required=True)
    ap.add_argument("--no-fit", action="store_true",
                    help="skip the stage-scaling script (single-slide exports only)")
    args = ap.parse_args()

    with open(args.source) as fh:
        html = fh.read()
    for k, v in build_map(html).items():
        html = html.replace(k, v)

    left = sorted(set(re.findall(r"\{\{[A-Za-z0-9_\-]+\}\}", html)))
    if left:
        sys.exit("unresolved placeholders: " + ", ".join(left))

    needs_fit = ('class="stage' in html or "class='stage" in html)
    has_fit = "--k" in html and "clientWidth / 1920" in html
    if needs_fit and not has_fit and not args.no_fit:
        if "</body>" in html:
            html = html.replace("</body>", FIT + "</body>", 1)
        else:
            html += FIT
        print("added the stage-scaling script")
    if needs_fit and not ("clientWidth / 1920" in html) and args.no_fit:
        print("WARNING: .stage present but scaling skipped — slides will crop below 1920px")

    with open(args.out, "w") as fh:
        fh.write(html)
    print("wrote %s (%.2f MB)" % (args.out, os.path.getsize(args.out) / 1048576))


if __name__ == "__main__":
    main()
