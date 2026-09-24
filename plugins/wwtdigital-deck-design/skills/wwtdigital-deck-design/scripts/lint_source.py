#!/usr/bin/env python3
"""
Lint WWT slide markup statically, in milliseconds, with no dependencies.

    python3 scripts/lint_source.py deck.html
    python3 scripts/lint_source.py deck.html --quiet   # print only on failure

WHY THIS EXISTS, AND WHY IT IS NOT THE VALIDATOR.

`wwt_validate.py` is the real gate. It renders the deck in headless Chromium, screenshots
every slide, samples the backdrop behind the type and measures contrast. It is thorough and
it takes tens of seconds, which means it runs at the end, which means it gets skipped. A
91-slide deck went to a client because step six of a checklist is a step somebody skips at
five o'clock on a Friday.

This is the other half: every check that can be made from the markup itself, fast enough to
run on every single write. It needs nothing but the Python standard library, so it works on
a machine with no Playwright, no Chromium, no numpy. Where the full validator cannot run at
all, this is the only enforcement there is.

It cannot see: contrast, rendered text extent, line breaks, widows, ink coverage, or
anything else that requires layout. It does not try. Passing this is not passing the
validator, and the output says so every time.

Exit 1 on any FAIL so it can gate a hook.
"""
import argparse, html.parser, json, os, re, sys

CANVAS_W, CANVAS_H = 1920, 1080
MARGIN = 72
COLS = [72 + i * 150 for i in range(12)]
SPANS = [126 + i * 150 for i in range(12)]
HEADS = ("t-display1", "t-display2", "t-h1-lg", "t-h1", "t-h2")
DEVICE = ("mesh", "brandx", "brandx-x", "tri", "panel--grad", "panel--grad93", "statband")
PLACEHOLDER = ("lorem ipsum", "dolor sit amet", "xxx placeholder", "todo:", "tbd:",
               "[insert", "lipsum", "tk tk")
# Classes the system has removed. A reference to one is a bug rather than a fallback,
# because the CSS is gone and the element renders at zero size or with no fill while every
# geometry rule skips it for being sub-pixel. Two covers shipped with no Brand X at all and
# a clean validator run, which is REG-27.
RETIRED = ("brandx--a", "brandx--b", "rule-h--brand")
# Why each one went, because the reason is what tells a builder what to do instead. The
# first cut of this check printed the Brand X message for every retired class, so a
# reference to the brand rule was reported as a missing Brand X. A shared message on a
# per-item check is a wrong answer delivered confidently.
RETIRED_WHY = {
    "brandx--a": "removed at v3.2. It has no geometry, so the element renders 0 x 0 and the "
                 "slide has no Brand X at all. Use .brandx-x",
    "brandx--b": "removed at v3.2. It has no geometry, so the element renders 0 x 0 and the "
                 "slide has no Brand X at all. Use .brandx-x",
    "rule-h--brand": "removed at v4.8 by direction. The 240 x 6 brand gradient rule was "
                     "never intended as an element, and it had drifted into the component "
                     "gallery, a recipe, two reference decks and three test decks, on one of "
                     "which it sat inside a gradient panel where it could not read against "
                     "its own ground. Where a label needs separating from its supporting "
                     "copy, let the spacing scale do it",
}
DECK_WARN_LEN, DECK_FAIL_LEN = 30, 40
# The dark emphasis ground: a ceiling, not a floor. Countable from the markup alone, so the
# fast lint can enforce it even where the rendering validator cannot run.
DARK_MAX_SHARE = 0.20
# Void elements never fire handle_endtag, so pushing them onto the stack made it grow
# without bound: every slide after the first read as depth 10, 14, 19 and the slide-close
# detection never fired. The depth numbers looked plausible, which is why it needed a
# timing run rather than a glance to notice.
VOID = {"area", "base", "br", "col", "embed", "hr", "img", "input", "link",
        "meta", "param", "source", "track", "wbr"}


# The photography library, for IMG-01. Read from the manifest that ships beside this
# script, so the check is against the real library rather than a list typed here. Empty if
# the manifest is missing, in which case IMG-01 stays silent rather than guessing.
def _library():
    p = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                     "..", "assets", "manifest.json")
    try:
        d = json.load(open(p, encoding="utf-8"))
    except Exception:
        return set()
    return {k for k, v in d.items() if isinstance(v, dict) and "crops" in v}


LIBRARY = _library()


# The icon library, for ICO-01 and ICO-02. Same reasoning as _library() above: read the
# real manifest rather than a list typed here, and stay silent if it is missing instead of
# guessing. Two sets, because the branded marks are shipped and addressable but carry a
# condition, so they have to be told apart from the universal ones.
def _icons():
    p = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                     "..", "assets", "icons", "manifest.json")
    try:
        d = json.load(open(p, encoding="utf-8"))
    except Exception:
        return set(), set(), set()
    uni, brand = d.get("icons", {}), d.get("branded", {})
    # The marks that do NOT paint with currentColor. 422 of the 429 universal icons are
    # monochrome and take the slide's ink; these keep their own palette whatever the
    # ground, which is a legible icon on the light surface and an invisible one on the
    # dark. ICO-05 is the only rule that needs to know the difference.
    colour = {k for k, v in list(uni.items()) + list(brand.items()) if not v.get("mono")}
    return set(uni), set(brand), colour


ICONS, ICONS_BRANDED, ICONS_COLOUR = _icons()

# The fixed ladder from system.css. An icon at any other size is how a set of marks stops
# looking like a set, and nothing under 24px survives the back of a room on a 1920 canvas.
ICON_SIZES = (24, 32, 48, 64, 96)


def px(style, prop):
    m = re.search(r"(?:^|;)\s*%s\s*:\s*(-?[\d.]+)px" % prop, style or "")
    return float(m.group(1)) if m else None


class Slide:
    def __init__(self, cls, role, builds_on, line):
        self.cls = cls.split()
        self.role = role
        self.builds_on = builds_on
        self.line = line
        self.nodes = []          # (tag, classes, style, text, line, depth, parent_classes)
        self.text = []

    @property
    def ground(self):
        return next((c for c in self.cls if c.startswith("g-")), None)


class Parser(html.parser.HTMLParser):
    """Walks the markup and records slides, their elements and their inline geometry.

    Slide boundaries are tracked with a counter local to the open slide rather than by
    comparing against a global stack depth. The depth version had a subtle failure: one
    slide in a 2,400-line document never closed, which swallowed the seven slides after it
    AND the documentation prose between them, so the linter read its own rule table as
    placeholder copy and reported twelve false positives. A counter that starts at zero
    when the slide opens and closes it when it returns below zero cannot drift, whatever
    the slide is nested inside.
    """

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.slides = []
        self.stack = []          # (tag, classes) for the element's parent chain
        self.cur = None
        self.inner = 0           # open elements inside the current slide
        self.is_gallery = False

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        cls = a.get("class", "")
        classes = cls.split()
        if tag == "section" and "doc" in classes:
            self.is_gallery = True
        if a.get("data-gallery") is not None:
            self.is_gallery = True
        opened_slide = False
        if "slide" in classes and self.cur is None:
            self.cur = Slide(cls, a.get("data-role"), a.get("data-builds-on"),
                             self.getpos()[0])
            self.slides.append(self.cur)
            self.inner = 0
            opened_slide = True
        if self.cur is not None and not opened_slide:
            parent = self.stack[-1][1] if self.stack else []
            parent_tag = self.stack[-1][0] if self.stack else "?"
            self.cur.nodes.append([tag, classes, a.get("style", ""), "",
                                   self.getpos()[0], self.inner, parent, a, parent_tag])
        if tag not in VOID:
            self.stack.append((tag, classes))
            if self.cur is not None and not opened_slide:
                self.inner += 1

    def handle_startendtag(self, tag, attrs):
        """A self-closing tag: record it, but touch neither the stack nor the counter.

        Routing this through handle_starttag leaked one increment per tag. The spec book
        inlines SVGs full of <path/>, <circle/> and <stop/>, so on those slides the counter
        never returned below zero, the slide never closed, and it swallowed the seven
        slides and all the prose that followed.
        """
        if self.cur is None:
            return
        a = dict(attrs)
        parent = self.stack[-1][1] if self.stack else []
        parent_tag = self.stack[-1][0] if self.stack else "?"
        self.cur.nodes.append([tag, a.get("class", "").split(), a.get("style", ""), "",
                               self.getpos()[0], self.inner, parent, a, parent_tag])

    def handle_endtag(self, tag):
        if tag in VOID:
            return
        if self.stack:
            self.stack.pop()
        if self.cur is None:
            return
        self.inner -= 1
        if self.inner < 0:                    # the slide's own closing tag
            self.cur = None
            self.inner = 0

    def handle_data(self, data):
        t = data.strip()
        if not t or self.cur is None:
            return
        self.cur.text.append(t)
        if self.cur.nodes:
            self.cur.nodes[-1][3] = (self.cur.nodes[-1][3] + " " + t).strip()


class Report:
    def __init__(self):
        self.rows = []

    def add(self, rid, sev, slide, line, msg):
        self.rows.append((rid, sev, slide, line, msg))

    @property
    def fails(self):
        return [r for r in self.rows if r[1] == "FAIL"]


def headline_nodes(s):
    return [n for n in s.nodes if any(h in n[1] for h in HEADS)]


def lint(path):
    src = open(path, encoding="utf-8", errors="replace").read()
    p = Parser()
    p.feed(src)
    rep = Report()
    slides = p.slides
    gallery = p.is_gallery

    # ---- whole-file checks
    for m in re.finditer(r"""(?:font-family\s*:[^;"']*|var\(\s*)(--font-narrow|['"]?Aptos Narrow)""", src):
        rep.add("TYP-00", "FAIL", None, src[:m.start()].count("\n") + 1,
                "Aptos Narrow is used here. It was removed at v2.0 by direction; everything "
                "that was Narrow is regular Aptos, which is wider, so old measures do not carry")
        break
    for r in RETIRED:
        m = re.search(r'class="[^"]*\b%s\b' % re.escape(r), src)
        if m:
            rep.add("PAT-06", "FAIL", None, src[:m.start()].count("\n") + 1,
                    f".{r} is retired: {RETIRED_WHY[r]}")

    if not gallery and len(slides) > DECK_FAIL_LEN:
        rep.add("SEQ-06", "FAIL", None, None,
                f"{len(slides)} slides. Over {DECK_FAIL_LEN} is a paginated document, not a "
                f"presentation. Cut it, or split the appendix into its own file")
    elif not gallery and len(slides) > DECK_WARN_LEN:
        rep.add("SEQ-06", "WARN", None, None, f"{len(slides)} slides; over {DECK_WARN_LEN} needs a reason")

    # ---- PAT-09 the emphasis ceiling, countable without layout
    if not gallery:
        dark = [i for i, sl in enumerate(slides) if "g-dark" in sl.cls]
        if dark:
            cap = max(1, int(len(slides) * DARK_MAX_SHARE))
            if len(dark) > cap:
                rep.add("PAT-09", "FAIL", None, None,
                        f"the dark emphasis ground is on {len(dark)} of {len(slides)} slides, "
                        f"over the ceiling of {cap} (one in five). It is an emphasis ground: a "
                        f"deck where every page shouts has no emphasis left")
            runs = [b for a_, b in zip(dark, dark[1:]) if b == a_ + 1]
            if runs:
                rep.add("PAT-09", "FAIL", None, None,
                        f"consecutive dark slides at {', '.join(str(x) for x in runs)}. An "
                        f"emphasis page needs something either side of it")

    seen_heads = {}
    for i, s in enumerate(slides):
        # ---- role
        if s.role is None:
            rep.add("ROLE-01", "WARN", i, s.line,
                    'no data-role. The role sets the density band and the substance floor')

        # ---- placeholder copy
        for n in s.nodes:
            low = (n[3] or "").lower()
            if low and any(ph in low for ph in PLACEHOLDER):
                rep.add("DEN-08", "FAIL", i, n[4], f'placeholder copy: "{n[3][:44]}"')

        # ---- headlines
        for n in headline_nodes(s):
            txt = re.sub(r"\s+", " ", n[3] or "").strip()
            style = n[2]
            if re.search(r"\(\s*cont\.?\s*\)", txt, re.I):
                rep.add("SEQ-05", "FAIL", i, n[4],
                        'a "(cont.)" headline. Content that does not fit is cut, compressed '
                        'into a different recipe, or moved to an appendix document')
            # A gallery repeats on purpose: it is showing the same headline in two
            # layouts. Only a deck can duplicate.
            key = re.sub(r"\s*\(cont\.?\)\s*", "", txt, flags=re.I).lower()
            if key and len(key) > 8 and not gallery:
                if key in seen_heads and seen_heads[key] != i:
                    rep.add("SEQ-03", "FAIL", i, n[4],
                            f'this headline already appeared on slide {seen_heads[key]}. '
                            f'A repeated headline is duplication, never a build')
                else:
                    seen_heads[key] = i
            left, width = px(style, "left"), px(style, "width")
            centred = "text-align:center" in (style or "").replace(" ", "")
            if centred and left is not None and width is not None and "off-grid" not in n[1]:
                ctr = left + width / 2.0
                if abs(ctr - 960) > 20:
                    rep.add("TYP-11", "FAIL", i, n[4],
                            f'centred headline centres on {ctr:.0f}, {ctr-960:+.0f} off the '
                            f'canvas axis of 960. A {width:.0f} box belongs at '
                            f'left:{(1920-width)/2:.0f}, not left:{left:.0f}')
            if (not centred) and width is not None and width > 1180 \
                    and not any(t in n[1] for t in ("t-display1", "t-display2")):
                rep.add("TYP-04", "WARN", i, n[4],
                        f'left-aligned headline box is {width:.0f}px against a 1176 measure. '
                        f'The validator measures the rendered text, which may be narrower')

        # ---- the mesh is background only
        for n in s.nodes:
            if "mesh" not in n[1]:
                continue
            # The parent element itself, not a depth count. A mesh whose parent carries
            # .slide is correct; anything else is nested.
            if "slide" not in (n[6] or []):
                where = "<%s%s>" % (n[8], ("." + ".".join(n[6][:2])) if n[6] else "")
                rep.add("PAT-05", "FAIL", i, n[4],
                        f'mesh sits inside {where}. The mesh is background only and must be '
                        f'a direct child of .slide')

        # ---- every slide does one act of design
        if not gallery and s.role in ("content", "data", "statement") and s.ground == "g-light":
            has_dev = any(any(d in n[1] for d in DEVICE) for n in s.nodes) \
                or any("linear-gradient" in (n[2] or "") for n in s.nodes)
            is_data = any(n[0] == "table" for n in s.nodes) \
                or any(n[0] == "svg" for n in s.nodes)
            if not has_dev and not is_data:
                rep.add("PAT-08", "FAIL", i, s.line,
                        'light ground with no background device. Add the mesh placement that '
                        'matches the content position, or a gradient surface. Only a table or '
                        'chart slide is exempt, because data may not sit on the mesh')

        # ---- the ground and panel relationship
        if s.ground == "g-white":
            if s.role in ("content", "data") and not any(n[0] == "table" for n in s.nodes):
                rep.add("COL-07", "FAIL", i, s.line,
                        'g-white on a content slide. The deck ground is #F6F6F6 and no recipe '
                        'uses g-white; it carried 57% of the deck that prompted this rule')
            if any("panel" in n[1] for n in s.nodes):
                rep.add("COL-07", "FAIL", i, s.line,
                        'a panel on a white ground. Panels are #FFFFFF raised off #F6F6F6; '
                        'inverted they read as holes in the page')

        # ---- geometry: margins, columns, spans, and sets that must line up
        panels = []
        for n in s.nodes:
            style = n[2]
            left, top = px(style, "left"), px(style, "top")
            width, height = px(style, "width"), px(style, "height")
            # This linter must stay a strict SUBSET of wwt_validate.py. It was briefly
            # stricter: it failed a scrim that covers to the canvas edge and a photograph
            # placed as a bare <img>, both of which bleed on purpose (REG-16) and both of
            # which the validator passes. A fast pre-check that fails things the real gate
            # allows teaches people to ignore it, which is worse than not having it.
            slide_relative = "slide" in (n[6] or [])
            bleeds = (n[0] == "img"                      # photography and device art bleed
                      or any("scrim" in c or c.startswith("scr") for c in n[1])
                      or any(c in n[1] for c in
                             ("media", "mesh", "brandx", "brandx-x", "bug", "stripe", "mark",
                              "tri", "device", "gridover", "spec-note", "doc-anno", "lockup",
                              "arrow", "ring", "medallion", "statband")))
            offgrid = "off-grid" in n[1] or bleeds
            if not slide_relative:
                offgrid = True          # nested: coordinates are not slide-relative
            if left is not None and width is not None and not offgrid:
                if left < MARGIN - 1:
                    rep.add("GEO-02", "FAIL", i, n[4], f'left {left:.0f} is inside the 72px margin')
                if left + width > CANVAS_W - MARGIN + 1:
                    rep.add("GEO-02", "FAIL", i, n[4],
                            f'right edge {left+width:.0f} is past the 1848 margin')
            if "panel" in n[1] and not offgrid:
                if left is not None and min(abs(left - c) for c in COLS) > 4:
                    rep.add("GEO-05", "FAIL", i, n[4],
                            f'panel left {left:.0f} is not a column edge (72 + n x 150). Mark it '
                            f'off-grid if the source node genuinely sits off the grid')
                if width is not None and min(abs(width - sp) for sp in SPANS) > 4:
                    rep.add("GEO-05", "FAIL", i, n[4],
                            f'panel width {width:.0f} is not a legal span (126 + n x 150)')
            if "panel" in n[1] and left is not None and top is not None \
                    and width is not None and height is not None:
                panels.append((left, top, width, height, n[4]))
        for a in range(len(panels)):
            for b in range(a + 1, len(panels)):
                la, ta, wa, ha, lna = panels[a]
                lb, tb, wb, hb, lnb = panels[b]
                if abs(ta - tb) <= 4 and abs(la - lb) > 40 and abs((ta + ha) - (tb + hb)) > 8:
                    rep.add("GEO-06", "FAIL", i, lnb,
                            f'shares a top with the panel on line {lna} but its bottom is '
                            f'{abs((ta+ha)-(tb+hb)):.0f}px away. A side-by-side set bottoms out together')

        # ---- accessibility, the part visible without layout
        for n in s.nodes:
            if n[0] != "img":
                continue
            attrs = n[7]
            if "alt" not in attrs:
                rep.add("A11-01", "FAIL", i, n[4], "img has no alt attribute")
            elif attrs.get("alt") == "" and attrs.get("aria-hidden") != "true" \
                    and "mark" not in n[1] and "lockup" not in (n[6] or []):
                rep.add("A11-01", "WARN", i, n[4], 'alt="" without aria-hidden="true"')

            # ---- IMG-01 photography resolves to a library ID.
            # This rule was in the SKILL.md table from the start and nothing ever
            # implemented it, which `check_provenance.py` GEN-02 now catches. It has to
            # live here rather than in the validator, because by the time the assets are
            # inlined every src is a base64 blob and the library name is gone. So the
            # placeholder is the only place the claim is checkable.
            src_a = attrs.get("src", "")
            m = re.fullmatch(r"\{\{IMG_([A-Za-z0-9_\-]+)\}\}", src_a.strip())
            if m and LIBRARY and m.group(1) not in LIBRARY:
                rep.add("IMG-01", "FAIL", i, n[4],
                        f'photograph "{m.group(1)}" is not in assets/manifest.json. '
                        f'Either it is a typo or the image is not in the library, and an '
                        f'image outside the library has no measured crop list')
            elif src_a.startswith("{{") and not m and "IMG_" in src_a:
                rep.add("IMG-01", "FAIL", i, n[4],
                        f'malformed photography placeholder {src_a!r}')

        # ---- ICO-01..04, the icon rules. Their own pass over the nodes.
        #
        # These first lived inside the `if n[0] != "img": continue` loop above, where they
        # could never fire on a <span class="ico">, which is every icon in the system. A
        # fixture built to break all four came back clean. REG-46 exactly: a rule that
        # reports nothing may not be a rule that found nothing.
        #
        # They belong here rather than in the validator for the same reason as IMG-01:
        # after inlining, an icon is raw SVG markup and the name it was chosen by is gone,
        # so the placeholder is the only place the claim is checkable.
        for n in s.nodes:
            if "ico" not in n[1]:
                continue
            txt = n[3] or ""
            found = re.findall(r"\{\{ICON_([A-Za-z0-9_\-]+)\}\}", txt)
            if not found and "{{ICON" in txt:
                rep.add("ICO-01", "FAIL", i, n[4],
                        f'malformed icon placeholder in {txt[:44]!r}')
            for name in found:
                if not (ICONS or ICONS_BRANDED):
                    break
                if name in ICONS_BRANDED:
                    # NOT a failure. The source sheet says these are specific to a product
                    # or service and not for universal use, which is a reason to ask why,
                    # not a reason to make a WWT deck unable to show the ATC Portal mark on
                    # a slide about the ATC Portal. data-why carries the written reason.
                    if not n[7].get("data-why"):
                        rep.add("ICO-02", "WARN", i, n[4],
                                f'"{name}" is branded to a product or service and is not '
                                f'for universal use. Keep it and say why in data-why, or '
                                f'pick a universal mark')
                elif name not in ICONS:
                    rep.add("ICO-01", "FAIL", i, n[4],
                            f'icon "{name}" is not in assets/icons/manifest.json. Either '
                            f'it is a typo or the mark is not in the Blue Steel set, and '
                            f'an icon from outside the set matches nothing else on the '
                            f'slide')
            if not found:
                continue
            # An icon carries meaning or it is decoration, and it has to say which. A
            # screen reader announcing nothing where a meaningful mark sits, and one
            # announcing "image" forty times down a gallery, are the same defect.
            if not n[7].get("aria-label") and n[7].get("aria-hidden") != "true":
                rep.add("ICO-03", "FAIL", i, n[4],
                        'an .ico needs aria-label="..." if it carries meaning or '
                        'aria-hidden="true" if it is decoration. WCAG 1.1.1')
            # ---- ICO-05 a multi-colour mark cannot take the dark ground's ink.
            # Seven of the set keep their own palette. On g-dark or inside .on-dark the
            # surrounding marks turn white and these stay as drawn, which reads as a
            # rendering fault rather than a choice.
            dark = (s.ground in ("g-dark",)) or "on-dark" in s.cls \
                or "on-dark" in (n[6] or [])
            for name in found:
                if dark and name in ICONS_COLOUR:
                    rep.add("ICO-05", "FAIL", i, n[4],
                            f'"{name}" is a multi-colour mark and cannot take the dark '
                            f'ground\'s ink. Every mark around it turns white and this one '
                            f'will not. Use a monochrome mark here')
            sizes = [c for c in n[1] if c.startswith("ico--") and c[5:].isdigit()]
            if not sizes:
                rep.add("ICO-04", "FAIL", i, n[4],
                        'an .ico needs a size from the ladder: '
                        + ", ".join("ico--%d" % s for s in ICON_SIZES))
            for c in sizes:
                if int(c[5:]) not in ICON_SIZES:
                    rep.add("ICO-04", "FAIL", i, n[4],
                            f'.{c} is not on the icon ladder '
                            f'({", ".join(str(s) for s in ICON_SIZES)}). Nothing under '
                            f'{ICON_SIZES[0]}px survives the back of a room')

        # ---- IMG-07 the same photograph twice on ONE slide.
        # Cheap here, because before inlining the placeholder still carries the library
        # name. The validator checks the same thing by fingerprinting the inlined blob.
        names = [m.group(1) for m in
                 (re.fullmatch(r"\{\{IMG_([A-Za-z0-9_\-]+)\}\}",
                               (x[7].get("src") or "").strip()) for x in s.nodes
                  if x[0] == "img") if m]
        for nm in {x for x in names if names.count(x) > 1}:
            rep.add("IMG-07", "FAIL", i, s.line,
                    f'photograph "{nm}" appears twice on this slide')

    # ---- IMG-08 the same photograph on more than one slide.
    # A deck no longer than the library has no arithmetic reason to repeat.
    where = {}
    for i, sl in enumerate(slides):
        for m in (re.fullmatch(r"\{\{IMG_([A-Za-z0-9_\-]+)\}\}", (x[7].get("src") or "").strip())
                  for x in sl.nodes if x[0] == "img"):
            if m:
                where.setdefault(m.group(1), set()).add(i)
    rep_names = {k: sorted(v) for k, v in where.items() if len(v) > 1}
    if rep_names and not gallery:
        lib = len(LIBRARY) or 19
        sev = "FAIL" if len(slides) <= lib else "WARN"
        for nm, idxs in sorted(rep_names.items()):
            rep.add("IMG-08", sev, -1, 0,
                    f'photograph "{nm}" is on slides {", ".join(str(x) for x in idxs)}. '
                    f'{len(slides)} slides against a library of {lib}'
                    + ("; pick another frame" if sev == "FAIL" else "; keep repeats apart"))

    return rep, len(slides), gallery


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("deck")
    ap.add_argument("--quiet", action="store_true", help="print only when something fails")
    a = ap.parse_args()
    if not os.path.exists(a.deck):
        return 0
    try:
        rep, n, gallery = lint(a.deck)
    except Exception as e:                       # never break a write on a parse problem
        print("wwt lint: could not parse %s (%s)" % (os.path.basename(a.deck), e))
        return 0

    if a.quiet and not rep.rows:
        return 0
    print("\nwwt source lint — %s, %d slide(s)%s"
          % (os.path.basename(a.deck), n, ", gallery" if gallery else ""))
    if not rep.rows:
        print("  clean on the static checks.")
    for rid, sev, slide, line, msg in sorted(rep.rows, key=lambda r: (r[2] is None, r[2] or 0, r[0])):
        where = "deck" if slide is None else "slide %d" % slide
        at = " line %d" % line if line else ""
        print("  %-4s %-8s %-9s%s  %s" % (sev, rid, where, at, msg))
    print("\n  %d FAIL   %d WARN" % (len(rep.fails), len(rep.rows) - len(rep.fails)))
    print("  Static checks only. Contrast, rendered measure, widows, ink coverage and the")
    print("  deck-level density and photography rules need wwt_validate.py. Passing this")
    print("  is not passing the validator.\n")
    return 1 if rep.fails else 0


if __name__ == "__main__":
    sys.exit(main())
