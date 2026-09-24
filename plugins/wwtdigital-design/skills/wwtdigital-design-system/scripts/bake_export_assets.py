#!/usr/bin/env python3
"""
Bake the CSS-computed decoration into flat PNGs for the PPTX path.

PowerPoint has no clip-path, no blend modes and no CSS filters, so every device
that depends on one has to be pre-rendered. This script is the only thing that
knows how to produce them; re-run it whenever a gradient, the mesh or the bug
geometry changes.

    python3 scripts/bake_export_assets.py            # writes assets/export/

What it makes, and why each one is shaped the way it is:

  ground-<variant>.png   OPAQUE 1920x1080 plates: the light surface with the mesh
                         already blended into it. The mesh uses mix-blend-mode
                         plus-lighter, which cannot be expressed in PPTX, but it
                         only ever sits on one ground (#F6F6F6), so blending it
                         down to flat pixels is lossless in practice.
  brandx-r10.png         RGBA. Recipe 10's cropped corner wedge. A DIFFERENT shape from
                         a different node than the cover X; conflating the two is what put
                         a dark full-bleed plate under the text on a light slide.
  brandx-cover.png       RGBA. The cover X as ONE grouped vector from node 1799:46,
                         gradients and opacity already baked into the asset. Alpha
                         because it sits over photography. Bars 536.2 and 273.3.
  bug-light.png          RGBA 275x286. Stripe and mark composited, already the
  bug-dark.png           right colour, so no filter:invert is needed downstream.

Everything is rendered at 2x and downsampled, so edges on the diagonals are
clean rather than stair-stepped.
"""
import base64, json, os, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
OUT = os.path.join(ROOT, "assets", "export")
SCALE = 2

sys.path.insert(0, HERE)
import inline_assets as ia  # noqa: E402


def uri(rel):
    return ia.uri(os.path.join(ROOT, "assets", *rel.split("/")))


# Kept in lockstep with head.html. If a token changes there it must change here,
# which is why both are listed in one place rather than duplicated per shape.
TOKENS = """
:root{
  --surface:#F6F6F6;
  --grad-brand-diag:linear-gradient(164deg,#0086EA 8%,#330072 63%);
  --grad-dark-diag:linear-gradient(165.47deg,#1D569E 8.95%,#28115C 76.88%);
  --grad-bug:linear-gradient(180deg,#F6F6F6 0%,#FFFFFF 100%);
}
*{margin:0;padding:0;box-sizing:border-box}
body{background:transparent}
.slide{position:relative;width:1920px;height:1080px;overflow:hidden}
.mesh{position:absolute;top:0;height:1080px;opacity:.11;mix-blend-mode:plus-lighter;
      background-repeat:no-repeat}
/* .brandx survives only for recipe 10's cropped wedge. The cover / divider X is one grouped
   vector, brandx-cover.svg, baked below; the .brandx--a / .brandx--b pair that used to
   reconstruct it from two clip-paths is deleted, not deprecated, because it cannot produce the
   source's 0.51 bar ratio and a deprecated rule is one somebody copies. */
.brandx{position:absolute;pointer-events:none;background:var(--grad-brand-diag);
        clip-path:polygon(0 83.2%,20.1% 100%,100% 33.5%,100% 0)}
.bug{position:relative;width:275px;height:286px}
.bug .stripe{position:absolute;inset:0;background:var(--grad-bug);
             clip-path:polygon(100% 0,100% 50.39%,50.37% 100%,0 100%)}
.bug .mark{position:absolute;left:56px;top:239px;width:73px;height:38px}
.bug .mark img{width:100%;height:100%;display:block}
.bug--dark .stripe{background:linear-gradient(180deg,rgba(255,255,255,.22),rgba(255,255,255,.09))}
.bug--dark .mark img{filter:brightness(0) invert(1)}
"""

MESH = {
    "diag":   ("left:0;width:1205px",              "mesh-diag.svg",   "1205px 1080px"),
    "center": ("left:0;width:1920px",              "mesh-center.svg", "1920px 1080px"),
    "h":      ("right:-32px;top:-8px;width:1182px", "mesh-h.svg",     "1182px 1080px"),
}

# The dark emphasis ground, node 1892:32. Baked for the same reason as the light plates:
# the mesh blends with plus-lighter, which has no PowerPoint equivalent, and here it sits on
# a gradient rather than a flat surface so there is even less chance of faking it downstream.
# One picture, and it cannot drift.
DARK = ("left:-262px;width:2384px", "mesh-dark.svg", "2384px 1080px")


def page(body, extra=""):
    return ("<!DOCTYPE html><meta charset='utf-8'><style>%s%s</style>%s"
            % (TOKENS, extra, body))


def shoot(pg, html, sel, path, opaque):
    pg.set_content(html)
    pg.wait_for_timeout(350)
    pg.locator(sel).screenshot(path=path, omit_background=not opaque)


def main():
    os.makedirs(OUT, exist_ok=True)
    from playwright.sync_api import sync_playwright
    from PIL import Image

    made = []
    with sync_playwright() as p:
        b = p.chromium.launch()
        pg = b.new_page(viewport={"width": 1920, "height": 1200},
                        device_scale_factor=SCALE)

        # Ground plates. Opaque on purpose: the mesh is blended into the surface
        # rather than floated over it, because plus-lighter has no PPTX analogue.
        for name, (pos, svg, size) in MESH.items():
            css = (".slide{background:var(--surface)}"
                   ".m{%s;background-image:url(%s);background-size:%s}" % (pos, uri("vectors/" + svg), size))
            html = page("<div class='slide'><div class='mesh m'></div></div>", css)
            f = os.path.join(OUT, "ground-light-mesh-%s.png" % name)
            shoot(pg, html, ".slide", f, opaque=True)
            made.append(f)

        # The dark emphasis ground: gradient plus its own wider mesh, blended down to flat
        # pixels. Opaque, because it is a ground.
        css = (".slide{background:var(--grad-dark-diag)}"
               ".m{%s;background-image:url(%s);background-size:%s}"
               % (DARK[0], uri("vectors/" + DARK[1]), DARK[2]))
        html = page("<div class='slide'><div class='mesh m'></div></div>", css)
        f = os.path.join(OUT, "ground-dark-mesh.png")
        shoot(pg, html, ".slide", f, opaque=True)
        made.append(f)

        # Gradient grounds. PPTX can do a linear gradient fill, but not reliably
        # through a converter at an arbitrary angle, and these are exact brand
        # values. A plate is one picture and cannot drift.
        for name, css_bg in (("grad-diag", "var(--grad-brand-diag)"),
                             ("grad-v", "linear-gradient(180deg,#0086EA 0%,#330072 100%)"),
                             ("white", "#FFFFFF"),
                             ("light", "var(--surface)")):
            html = page("<div class='slide' style='background:%s'></div>" % css_bg)
            f = os.path.join(OUT, "ground-%s.png" % name)
            shoot(pg, html, ".slide", f, opaque=True)
            made.append(f)

        # Cover X. ONE grouped vector from node 1799:46, alpha because it sits over
        # the photograph. It is not two copies of one clip-path: the bars are 536.2
        # and 273.3 wide, a deliberate 0.51 ratio that a shared clip-path cannot give.
        with open(os.path.join(ROOT, "assets", "vectors", "brandx-cover.svg")) as fh:
            xsvg = fh.read()
        html = page("<div class='slide'><div style='position:absolute;left:345px;top:-910px;"
                    "width:2108px;height:2566px'>%s</div></div>" % xsvg,
                    "div>svg{width:100%;height:100%;display:block}")
        f = os.path.join(OUT, "brandx-cover.png")
        shoot(pg, html, ".slide", f, opaque=False)
        made.append(f)

        # Recipe 10's cropped wedge, and it needed its own plate.
        #
        # This was the bug: the exporter matched `.brandx-x, .brandx` and painted
        # brandx-cover.png full canvas for any of them. The cover X and the r10 wedge are
        # different shapes from different nodes, so every deck using recipe 10 got the
        # cover's dark wedge pair stretched across a light slide, under all the text. It
        # was latent from the day the variant was added, because neither of the two decks
        # that ship with the system uses recipe 10. The first deck that did use it came
        # back with an illegible page nine.
        #
        # The geometry is the CSS rule verbatim: inset 0, the diagonal gradient, clipped to
        # a corner triangle. Alpha, because it sits on whatever ground the slide has.
        html = page("<div class='slide'><div class='bx'></div></div>",
                    ".bx{position:absolute;inset:0;background:var(--grad-brand-diag);"
                    "clip-path:polygon(100% 16.1%,100% 100%,50.9% 100%)}")
        f = os.path.join(OUT, "brandx-r10.png")
        shoot(pg, html, ".slide", f, opaque=False)
        made.append(f)

        # The lockup. An SVG data URI in HTML; PowerPoint cannot place SVG, and
        # screenshotting it off the live page picked up a black plate.
        with open(os.path.join(ROOT, "assets", "vectors", "logo-full.svg")) as fh:
            logo = fh.read()
        for name, svg in (("lockup-white", logo),
                          ("lockup-ink", logo.replace('fill="white"', 'fill="#1F1F1F"'))):
            html = page("<div style='width:210px;height:44px'>%s</div>" % svg,
                        "div>svg{width:100%;height:100%;display:block}")
            f = os.path.join(OUT, "%s.png" % name)
            shoot(pg, html, "div", f, opaque=False)
            made.append(f)

        # The red arrow. Inline SVG in HTML so CSS can mirror it; a picture here,
        # already mirrored, because .arrow--down is a transform PPTX will not carry.
        with open(os.path.join(ROOT, "assets", "vectors", "arrow-red.svg")) as fh:
            arrow_svg = fh.read().strip()
        for name, flip in (("arrow-down", "scaleY(-1)"), ("arrow-up", "none")):
            html = page("<div style='width:93px;height:93px;transform:%s'>%s</div>"
                        % (flip, arrow_svg),
                        "div>svg{width:100%;height:100%;display:block}")
            f = os.path.join(OUT, "%s.png" % name)
            shoot(pg, html, "div", f, opaque=False)
            made.append(f)

        # Flex triangles. clip-path is not involved here, but the shape is an SVG
        # with a userSpace gradient and a CSS transform, none of which PPTX carries.
        with open(os.path.join(ROOT, "assets", "vectors", "flex-triangle.svg")) as fh:
            tri = fh.read()
        for name, flip in (("tri-left", "scaleY(-1)"), ("tri-right", "scaleY(-1) scaleX(-1)")):
            html = page("<div style='width:1329px;height:907px;transform:%s'>%s</div>"
                        % (flip, tri), "div>svg{width:100%;height:100%;display:block}")
            f = os.path.join(OUT, "%s.png" % name)
            shoot(pg, html, "div", f, opaque=False)
            made.append(f)

        # The bug, both variants, mark already composited and already the right
        # colour so nothing downstream has to reproduce filter:brightness(0) invert(1).
        mark = uri("vectors/bug-mark.svg")
        for variant in ("light", "dark"):
            cls = "bug bug--dark" if variant == "dark" else "bug"
            html = page("<div class='%s'><div class='stripe'></div>"
                        "<div class='mark'><img src='%s'></div></div>" % (cls, mark))
            f = os.path.join(OUT, "bug-%s.png" % variant)
            shoot(pg, html, ".bug", f, opaque=False)
            made.append(f)

        b.close()

    # Downsample the 2x renders to canvas pixels. The diagonals are the whole
    # reason for rendering at 2x, so this is a LANCZOS reduction, not a resize.
    manifest = {}
    for f in made:
        im = Image.open(f)
        im = im.resize((im.width // SCALE, im.height // SCALE), Image.LANCZOS)
        im.save(f)
        k = os.path.basename(f)[:-4]
        manifest[k] = {"file": "assets/export/%s.png" % k, "px": list(im.size),
                       "alpha": im.mode == "RGBA"}
        print("  %-28s %4d x %-4d %s" % (k, im.width, im.height,
                                         "RGBA" if im.mode == "RGBA" else "opaque"))
    with open(os.path.join(OUT, "manifest.json"), "w") as fh:
        json.dump(manifest, fh, indent=1)
    print("\n%d assets -> assets/export/" % len(manifest))


if __name__ == "__main__":
    main()
