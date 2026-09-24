#!/usr/bin/env python3
"""
Export a built WWT deck to PPTX with live text and baked decoration.

    python3 scripts/export_pptx.py WWT-Deck.html -o WWT-Deck.pptx

Read this before changing anything.

PowerPoint has no clip-path, no mix-blend-mode, no CSS filters and no
pseudo-elements. Every device in this system that uses one is pre-rendered by
`bake_export_assets.py` into `assets/export/`. **Do not try to rebuild those
shapes as PPTX freeforms.** That is what produces the broken crossed bars, the
broken corner bug and the missing diamond mesh. Place the picture.

Everything else survives as native PowerPoint:

  text        real text boxes, so a headline can be retyped
  panels      rectangles with solid fills
  rules       thin rectangles
  photos      pictures, cropped to match CSS object-fit: cover
  logos       pictures

The canvas maps exactly. 1920 x 1080 at 144 DPI is 13.333 x 7.5 inches, which is
PowerPoint's widescreen size, so:

    1 px = 6350 EMU exactly       (914400 / 144)
    1 px = 0.5 pt exactly         (72 / 144)

No rounding anywhere. A 96px headline is 48pt, a 24px body is 12pt.

Fonts: the HTML may embed WOFF2, which PowerPoint cannot read, so the deck embeds the
Aptos TTFs found on this machine (Office carries them; see brand_assets.py, which also
says how to install them). They are not shipped with the skill.
"""
import argparse, base64, json, os, re, sys

import brand_assets

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
EXPORT = os.path.join(ROOT, "assets", "export")

EMU_PX = 6350          # 914400 EMU per inch / 144 px per inch
PT_PX = 0.5            # 72 pt per inch / 144 px per inch
W, H = 1920, 1080

# Ground class -> baked plate. The mesh is already blended into the light plates
# because plus-lighter has no PPTX equivalent (see REG-17).
GROUND = {
    ("g-light", "mesh--h"): "ground-light-mesh-h",
    ("g-light", "mesh--diag"): "ground-light-mesh-diag",
    ("g-light", "mesh--center"): "ground-light-mesh-center",
    ("g-light", None): "ground-light",
    ("g-white", None): "ground-white",
    ("g-grad-diag", None): "ground-grad-diag",
    # The dark emphasis ground is a PAIR: its gradient and its own wider mesh are baked
    # together, because plus-lighter over a gradient is doubly impossible in PPTX.
    ("g-dark", "mesh--dark"): "ground-dark-mesh",
    ("g-dark", None): "ground-dark-mesh",
    ("g-grad", None): "ground-grad-v",
}

# Everything the DOM walk must not emit as a generic box, because a baked
# picture is standing in for it.
# .tri is a gradient-filled SVG under a CSS transform; .ring is an inline SVG
# with a dasharray. Neither survives, so both are placed as pictures.
BAKED = ("mesh", "brandx", "brandx-x", "bug", "stripe", "mark", "arrow",
         "lockup", "tri", "ring")


def probe(path):
    """Walk the rendered deck and return a plain description of every slide."""
    from playwright.sync_api import sync_playwright
    from browser import launch
    js = r"""
    () => {
      const px = v => Math.round(parseFloat(v) || 0);
      const out = [];
      document.querySelectorAll('.slide').forEach(slide => {
        const sr = slide.getBoundingClientRect();
        const cls = [...slide.classList];
        const mesh = slide.querySelector('.mesh');
        const scs = getComputedStyle(slide);
        const sgrad = (scs.backgroundImage && scs.backgroundImage.indexOf('linear-gradient') === 0)
                      ? scs.backgroundImage : null;
        const rec = { role: slide.dataset.role || 'content',
                      ground: cls.find(c => c.startsWith('g-')) || null,
                      mesh: mesh ? [...mesh.classList].find(c => c.startsWith('mesh--')) : null,
                      // The Brand X VARIANT, not merely whether one is present. The cover
                      // X and recipe 10's cropped wedge are different shapes from different
                      // Figma nodes, and reporting a boolean here is what made the exporter
                      // paint the cover's plate over a light content slide.
                      brandx: (() => {
                        const bx = slide.querySelector('.brandx-x, .brandx');
                        if (!bx) return null;
                        if (bx.classList.contains('brandx-x')) return 'brandx-cover';
                        if (bx.classList.contains('brandx--r10')) return 'brandx-r10';
                        return 'UNKNOWN:' + [...bx.classList].join('.');
                      })(),
                      groundGrad: sgrad, groundColor: scs.backgroundColor,
                      bug: null, decor: [], icons: [], items: [] };
        // PAINT ORDER COMES FROM THE DOM, not from a list of class names.
        // The old version hardcoded `z: 'bg'` for .tri and 'fg' for everything else, so the
        // Brand X was placed after the text on EVERY cover and painted over the headline.
        // It is semi-transparent, so the headline showed through darkened and the defect
        // looked like a design choice. The browser paints in DOM order; so does PowerPoint,
        // in shape order. Reading the DOM position is the whole answer and there is no list
        // to keep in sync.
        const order = new Map();
        let oi = 0;
        slide.querySelectorAll('*').forEach(n => order.set(n, oi++));
        const firstTextOrder = (() => {
          let best = Infinity;
          slide.querySelectorAll('*').forEach(n => {
            let t = '';
            for (const c of n.childNodes) if (c.nodeType === 3) t += c.textContent;
            if (!t.trim()) return;
            if (n.closest('.rail, .bug, .lockup, .gridover')) return;
            best = Math.min(best, order.get(n));
          });
          return best;
        })();
        rec.firstTextOrder = firstTextOrder;
        rec.brandxOrder = (() => {
          const bx = slide.querySelector('.brandx-x, .brandx');
          return bx ? order.get(bx) : null;
        })();

        // Devices that must be placed as baked pictures, recorded by position only.
        slide.querySelectorAll('.lockup, .arrow, .tri').forEach(n => {
          const r = n.getBoundingClientRect();
          const cl = n.classList;
          let asset;
          if (cl.contains('arrow'))      asset = cl.contains('arrow--down') ? 'arrow-down' : 'arrow-up';
          else if (cl.contains('tri'))   asset = cl.contains('tri--r') ? 'tri-right' : 'tri-left';
          else asset = (n.querySelector('img') && /1F1F1F/.test(n.innerHTML)) ? 'lockup-ink' : 'lockup-white';
          // z matters: the flex triangle is background decoration and sits UNDER
          // the photography, while the lockup and arrow sit over everything. All
          // decor used to be placed last, which put the triangle on top of the photo.
          rec.decor.push({ asset, ord: order.get(n),          // DOM order, nothing else
            x: Math.round(r.left - sr.left), y: Math.round(r.top - sr.top),
            w: Math.round(r.width), h: Math.round(r.height) });
        });
        // ---- ICONS. PowerPoint cannot place an SVG at all, so every .ico has to ship as
        // a raster or it disappears, which is the FDU partner-logo failure repeated with
        // a different asset. They are NOT pre-baked into assets/export the way the lockup
        // and the arrow are: there are 497 of them in five sizes and two inks, and baking
        // that grid would add megabytes to the plugin for plates almost none of which any
        // one deck uses. Instead the icon's own resolved markup and resolved colour are
        // captured here, and the Python side rasterises just the ones this deck contains.
        //
        // The resolved colour is the whole trick. The mark paints with `currentColor`, so
        // the SVG source alone does not say what ink it is. Reading it off the rendered
        // element is the only thing that knows whether this instance is ink, blue, or
        // white on the dark ground.
        slide.querySelectorAll('.ico').forEach(n => {
          const svg = n.querySelector('svg');
          if (!svg) return;
          const r = n.getBoundingClientRect();
          if (r.width < 1 || r.height < 1) return;
          rec.icons.push({ ord: order.get(n),
            x: Math.round(r.left - sr.left), y: Math.round(r.top - sr.top),
            w: Math.round(r.width), h: Math.round(r.height),
            color: getComputedStyle(n).color,
            label: n.getAttribute('aria-label') || '',
            markup: svg.outerHTML });
        });

        const bug = slide.querySelector('.bug');
        if (bug) rec.bug = bug.classList.contains('bug--dark') ? 'dark' : 'light';

        const emitted = [];
        slide.querySelectorAll('*').forEach(n => {
          const cs = getComputedStyle(n);
          if (cs.visibility === 'hidden' || cs.display === 'none') return;
          const r = n.getBoundingClientRect();
          if (r.width < 1 || r.height < 1) return;
          const box = { x: px(r.left - sr.left), y: px(r.top - sr.top),
                        w: px(r.width), h: px(r.height) };
          const classes = [...n.classList];
          const tag = n.tagName.toLowerCase();
          const nord = order.get(n);

          if (tag === 'img') {
            const inMedia = n.closest('.media');
            // object-position, resolved to two fractions. Three slides in the system
            // set it, and a centre crop moved every one of their subjects.
            const op = (() => {
              const parts = (cs.objectPosition || '50% 50%').trim().split(/\s+/);
              const f = v => v.endsWith('%') ? parseFloat(v) / 100
                           : (v === 'left' || v === 'top') ? 0
                           : (v === 'right' || v === 'bottom') ? 1 : 0.5;
              return [f(parts[0] || '50%'), f(parts[1] || parts[0] || '50%')];
            })();
            out_push(rec, { kind: 'img', ord: nord, box, src: n.currentSrc || n.src,
                            natural: [n.naturalWidth, n.naturalHeight],
                            cover: !!inMedia, objPos: op,
                            clip: inMedia ? (() => { const m = inMedia.getBoundingClientRect();
                              return { x: px(m.left - sr.left), y: px(m.top - sr.top),
                                       w: px(m.width), h: px(m.height) }; })() : null,
                            classes });
            return;
          }
          // A painted box is a solid fill OR a gradient. Reading only
          // backgroundColor dropped every .panel--grad from the export and left
          // its white type on the light ground at about 1.1:1.
          const bg = cs.backgroundColor;
          const bgi = cs.backgroundImage;
          const grad = (bgi && bgi.indexOf('linear-gradient') === 0) ? bgi : null;
          const painted = grad || (bg && bg !== 'rgba(0, 0, 0, 0)' && bg !== 'transparent');
          const ownText = [...n.childNodes].some(c => c.nodeType === 3 && c.textContent.trim());
          if (painted && !ownText) {
            out_push(rec, { kind: 'box', ord: nord, box, fill: bg, grad, classes,
                            shadow: cs.boxShadow === 'none' ? null : cs.boxShadow });
          }
          // A painted element that OWNS its text used to emit nothing but the text, because
          // `!ownText` above suppressed the box and the text record's own `grad` and `fill`
          // were probed and then never read on the Python side. `.badge` is exactly that
          // shape: a 96 x 96 plate carrying --grad-brand-v-93 with a white numeral set in
          // it. Three of them anchor the three-step story on a slide in the worked example,
          // and in the PPTX the plate was gone and the white numerals were invisible on the
          // light card. FIL-01 caught it and it had been latent since the gradient work.
          //
          // The plate is emitted here rather than as a fill on the text box, because the
          // text box is deliberately offset by -6/-4 and grown by +12/+8 for optical
          // bearing. Filling it would paint a 108 x 104 plate 6px up and left of a 96 x 96
          // design element, which is a different defect wearing the same fix. One shape at
          // the border box, at the same ordinal, so it lands directly under its own text.
          const radius = parseFloat(cs.borderTopLeftRadius) || 0;
          const fillBox = (painted && ownText) ? box : null;
          // Flex and grid centring, which `textAlign` cannot report. `.badge` is
          // `display:grid;place-items:center` with `text-align:start`, so reading textAlign
          // alone put its numeral hard against the top-left of a 96 x 96 plate that the
          // design centres. `.btn` is `display:flex;align-items:center` and only looked
          // right because its padding happens to be symmetric, which is a coincidence and
          // not a specification. Fourteen elements across the three reference documents
          // depend on one of these two properties.
          const flexy = /flex|grid/.test(cs.display);
          const hMid = flexy && (cs.justifyItems === 'center' || cs.justifyContent === 'center');
          const vMid = flexy && (cs.alignItems === 'center' || cs.alignContent === 'center');
          // Emit one text box per real text element, never per container.
          // An earlier rule ("has any span child") swept up .layer and .caps and
          // wrote every band's contents twice.
          const TEXTTAG = ['h1','h2','h3','h4','h5','h6','p','li','td','th'];
          const wants = ownText || (TEXTTAG.includes(tag) && n.innerText.trim());
          if (wants) {
            if (emitted.some(e => e !== n && e.contains(n))) return;
            emitted.push(n);
            const runs = [];
            const walk = el => {
              el.childNodes.forEach(c => {
                if (c.nodeType === 3) {
                  // HTML collapses whitespace; innerText does not, so a line break
                  // in the markup was arriving as a real break in the deck.
                  // U+00A0 must survive. /\s+/ matches it, so collapsing with \s turned
                  // every non-breaking space in the system into a breaking one and the
                  // exported deck rewrapped: bound word pairs came apart and widows the
                  // HTML had no way to produce appeared in PowerPoint. Collapse only
                  // real whitespace, and never across an nbsp.
                  const t = c.textContent.replace(/[^\S ]+/g, ' ');
                  if (t) runs.push({ t: t,
                    c: getComputedStyle(el).color,
                    w: parseInt(getComputedStyle(el).fontWeight) || 400 });
                } else if (c.nodeType === 1) {
                  if (c.tagName === 'BR') runs.push({ br: true }); else walk(c);
                }});
            };
            walk(n);
            const r1 = document.createRange(); r1.selectNodeContents(n);
            const lineCount = new Set([...r1.getClientRects()].map(q => Math.round(q.top))).size;
            // A text box is drawn with zero internal margin (see tf.margin_* below), so it has
            // to arrive already inset by the element's own CSS padding, or that padding -- the
            // whole reason ul.b li and .svc-col li reserve left space for a bullet -- is silent
            // in the PPTX and the text starts flush at the border edge instead. Every other
            // consumer of `box` (an image, a painted panel) wants the full border box; only
            // text wants the padding box, so this is computed here and nowhere else.
            const pl = parseFloat(cs.paddingLeft) || 0, pt = parseFloat(cs.paddingTop) || 0,
                  pr = parseFloat(cs.paddingRight) || 0, pb = parseFloat(cs.paddingBottom) || 0;
            const tbox = (pl || pt || pr || pb)
              ? { x: box.x + pl, y: box.y + pt, w: box.w - pl - pr, h: box.h - pt - pb }
              : box;
            out_push(rec, { kind: 'text', ord: nord, box: tbox, classes, tag, runs, lines: lineCount,
              text: n.innerText,
              font: cs.fontFamily.split(',')[0].replace(/["']/g, '').trim(),
              size: parseFloat(cs.fontSize),
              weight: parseInt(cs.fontWeight) || 400,
              color: cs.color,
              align: cs.textAlign,
              upper: cs.textTransform === 'uppercase',
              tracking: parseFloat(cs.letterSpacing) || 0,
              leading: cs.lineHeight === 'normal' ? null : parseFloat(cs.lineHeight),
              opacity: parseFloat(cs.opacity),
              grad: grad,
              fill: (painted ? bg : null),
              fillBox: fillBox,
              fillOval: fillBox ? (radius >= box.w / 2 && radius >= box.h / 2) : false,
              fillShadow: (fillBox && cs.boxShadow !== 'none') ? cs.boxShadow : null,
              hMid: hMid, vMid: vMid });
          }
        });
        // PSEUDO-ELEMENT DECORATION. querySelectorAll('*') only ever returns real DOM nodes,
        // so a ::before/::after with content:"" -- every bullet dot (ul.b li::before,
        // .feat::before) and every photo scrim (.media::after) in the system -- is invisible
        // to the walk above. Nothing here ever objected, because there is no rule that reads
        // a pseudo-element; the deck built clean and the PPTX quietly lost the scrim on the
        // cover and every bullet in the deck. Measured: dropping the cover's 36% scrim raised
        // the photo's rendered luminance by 20+ points against the HTML, and two full bullet
        // lists came back with no markers at all.
        //
        // Every current use sets left/top/width/height in px, so the computed style already
        // holds the resolved box; nothing here is "auto" and needs a layout pass to solve.
        // Position is the host's own box plus that offset, because every host is the pseudo's
        // containing block (position:relative host, position:absolute pseudo -- the pattern
        // this whole system uses, not a coincidence).
        //
        // Order is the tricky part. A parent's own DOM order number is LOWER than its
        // children's (querySelectorAll is a pre-order walk), so "host order + a bit" can sort
        // a scrim BEFORE the photo it exists to darken, which paints it invisibly underneath.
        // A ::after paints after everything already inside its element, so the pseudo belongs
        // after the LAST order number anywhere in the host's subtree, not the host's own.
        slide.querySelectorAll('*').forEach(n => {
          ['::before', '::after'].forEach(pseudo => {
            const cs = getComputedStyle(n, pseudo);
            if (!cs.content || cs.content === 'none') return;
            const w = parseFloat(cs.width), h = parseFloat(cs.height);
            if (!(w > 0 && h > 0)) return;
            // A scrim is TWO layers (--scrim-1, --scrim-2, see system.css), so backgroundImage
            // comes back as "linear-gradient(...), linear-gradient(...)" or "linear-gradient(...), none".
            // Passing that whole string through as one gradient is what a plain bullet dot's
            // single-layer background can get away with, but here it left a trailing ", none"
            // the Python side's regex (anchored on a closing paren at the true end) could not
            // match, so the scrim silently fell back to sh.fill.solid() with backgroundColor,
            // which is transparent black on every scrim (the color lives in backgroundIMAGE) --
            // rgb() has no alpha channel, and the result was a fully opaque black plate over
            // the whole photo. Only the FIRST layer is ever real content today (composing two
            // is IMG-04's job in the browser, not this exporter's), so take only that one,
            // matched by depth rather than string position so a nested rgba(...)'s own commas
            // and parens cannot end the match early.
            const bgi = cs.backgroundImage;
            const pgrad = (() => {
              const m = bgi && bgi.match(/linear-gradient\(/);
              if (!m) return null;
              let i = m.index + m[0].length, depth = 1;
              while (i < bgi.length && depth > 0) {
                if (bgi[i] === '(') depth++; else if (bgi[i] === ')') depth--;
                i++;
              }
              return bgi.slice(m.index, i);
            })();
            const pbg = cs.backgroundColor;
            const paintedPseudo = pgrad || (pbg && pbg !== 'rgba(0, 0, 0, 0)' && pbg !== 'transparent');
            if (!paintedPseudo) return;
            const hostR = n.getBoundingClientRect();
            const left = hostR.left + (parseFloat(cs.left) || 0);
            const top = hostR.top + (parseFloat(cs.top) || 0);
            let maxOrd = order.get(n);
            n.querySelectorAll('*').forEach(d => { maxOrd = Math.max(maxOrd, order.get(d)); });
            const rTL = parseFloat(cs.borderTopLeftRadius) || 0;
            rec.items.push({ kind: 'box', ord: maxOrd + 0.5,
              box: { x: Math.round(left - sr.left), y: Math.round(top - sr.top),
                     w: Math.round(w), h: Math.round(h) },
              fill: pbg, grad: pgrad, oval: rTL >= w / 2 && rTL >= h / 2, classes: ['_pseudo'] });
          });
        });
        out.push(rec);
      });
      function out_push(rec, item) { rec.items.push(item); }
      // NOTE on paint order. There are THREE z-bands on a cover, not two: the flex
      // triangle sits under the photograph, the Brand X sits over the photograph and
      // under the headline, and the lockup sits over everything. A bg/fg flag cannot
      // express that, and a first attempt at this fix moved the X under the photo while
      // getting it out from over the headline. Everything now carries its DOM order and
      // is placed in one sorted pass, which is what the browser does.
      return out;
    }
    """
    with sync_playwright() as p:
        b = launch(p)
        pg = b.new_page(viewport={"width": W, "height": H})
        pg.goto("file://" + os.path.abspath(path))
        pg.wait_for_timeout(5000)
        # Measure at native size. The stage scaler is irrelevant to PPTX and
        # would only introduce rounding.
        pg.evaluate("""() => { const d = document.querySelector('.deck');
            if (d) { d.style.maxWidth = 'none'; d.style.padding = '0'; }
            document.querySelectorAll('.stage').forEach(s => {
              s.style.width = '1920px'; s.style.height = '1080px';
              s.style.aspectRatio = 'auto'; s.style.setProperty('--k', '1'); }); }""")
        pg.wait_for_timeout(800)
        slides = pg.evaluate(js)

        # The ring carries its value in a stroke-dasharray, so it cannot be one
        # baked asset. Capture each instance from the live page instead, OPAQUE:
        # it always sits on a white panel, and an opaque PNG avoids the alpha that
        # LibreOffice composited against black when the lockup was done this way.
        import tempfile as _tf
        from PIL import Image as _I
        shots = _tf.mkdtemp(prefix="wwtring")
        n = 0
        for si in range(len(slides)):
            rings = pg.locator(".slide").nth(si).locator(".ring")
            for ri in range(rings.count()):
                el = rings.nth(ri)
                bb = el.bounding_box()
                sb = pg.locator(".slide").nth(si).bounding_box()
                if not bb or not sb:
                    continue
                f = os.path.join(shots, "ring%03d.png" % n); n += 1
                el.screenshot(path=f)
                _I.open(f).convert("RGB").save(f, "PNG")
                slides[si]["items"].append({
                    "kind": "img", "src": f, "cover": False, "clip": None,
                    "classes": ["_ring"], "natural": [0, 0],
                    "box": {"x": round(bb["x"] - sb["x"]), "y": round(bb["y"] - sb["y"]),
                            "w": round(bb["width"]), "h": round(bb["height"])}})

        b.close()
    return slides


def rgb(css):
    m = re.match(r"rgba?\(([\d.]+),\s*([\d.]+),\s*([\d.]+)", css or "")
    if not m:
        return (0, 0, 0)
    return tuple(int(float(g)) for g in m.groups())


def alpha(css):
    m = re.match(r"rgba\([^,]+,[^,]+,[^,]+,\s*([\d.]+)\)", css or "")
    return float(m.group(1)) if m else 1.0



# ---------------------------------------------------------------- gradients --
# DrawingML has a real linear gradient, so these do not need baking. Two
# conversions do all the work:
#
#   stops   CSS percent x 1000 is the DrawingML position. Both formats hold the
#           end colour beyond the last stop, so 8%/63% behaves identically.
#   angle   CSS measures clockwise from "to top"; DrawingML measures clockwise
#           from the +x axis in 60000ths of a degree.
#               ang = (cssDeg - 90) mod 360 * 60000
#           Checks: CSS 180 (top to bottom) -> 90deg. CSS 90 (left to right) -> 0.
#
# scaled="0" keeps the true geometric angle. scaled="1" stretches the angle by
# the shape's aspect ratio, which on a 16:9 ground is visibly wrong.
GRAD_RE = re.compile(r"linear-gradient\((.*)\)\s*$", re.S)
STOP_RE = re.compile(r"(rgba?\([^)]*\)|#[0-9a-fA-F]{3,8})\s*([\d.]+)?%?")


def parse_gradient(css):
    """CSS linear-gradient -> (angle_deg, [(rgb, pos_percent), ...]) or None."""
    m = GRAD_RE.search(css or "")
    if not m:
        return None
    body = m.group(1)
    ang = 180.0                                  # CSS default is "to bottom"
    a = re.match(r"\s*([-\d.]+)deg\s*,", body)
    if a:
        ang = float(a.group(1)); body = body[a.end():]
    elif body.lstrip().startswith("to "):
        word = re.match(r"\s*to\s+([a-z ]+),", body)
        if word:
            ang = {"top": 0, "right": 90, "bottom": 180, "left": 270}.get(
                word.group(1).strip(), 180)
            body = body[word.end():]
    stops = []
    for cm in STOP_RE.finditer(body):
        col, pos = cm.group(1), cm.group(2)
        stops.append((rgb(col) if col.startswith("rgb") else hex_rgb(col),
                      float(pos) if pos is not None else None,
                      alpha(col) if col.startswith("rgba") else 1.0))
    if len(stops) < 2:
        return None
    # fill in any implicit positions, evenly spaced
    n = len(stops)
    for i, (c, pos, al) in enumerate(stops):
        if pos is None:
            stops[i] = (c, i * 100.0 / (n - 1), al)
    return ang, stops


def hex_rgb(h):
    h = h.lstrip("#")
    if len(h) == 3:
        h = "".join(c * 2 for c in h)
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


# PowerPoint and LibreOffice disagree about <a:lin scaled="0"> on a non-axis-aligned
# angle. LibreOffice honours the true geometric angle and matches CSS exactly;
# PowerPoint renormalises, and the visible range collapses toward the first stop --
# a blue-to-purple ground arrives as light-blue-to-blue with no purple at all.
#
# Axis-aligned angles (0/90/180/270) are immune: vertical is vertical either way.
# So native gradients are used there and nowhere else, and any other angle falls
# back to its baked plate, which is pixel-exact in both renderers.
AXIS_ALIGNED = (0, 90, 180, 270)




# --------------------------------------------------------------------- type --
# PPTX has no font-weight. It has a binary bold flag, so `typeface="Aptos"` with
# b="1" resolves to Aptos BOLD (700) and there is no way to ask for 900. Aptos
# ships its heavy cuts as separate FAMILIES, so the weight has to be carried in
# the typeface name instead. Exactly the trap REG-01 describes on the HTML side;
# the @font-face map solves it there, and naming the family solves it here.
#
#   400 -> Aptos                b=0
#   600 -> Aptos SemiBold       b=0
#   700 -> Aptos                b=1     (the only real bold face)
#   800 -> Aptos ExtraBold      b=0
#   900 -> Aptos Black          b=0
WEIGHT_FAMILY = {
    "Aptos": {400: ("Aptos", False), 600: ("Aptos SemiBold", False),
              700: ("Aptos", True),  800: ("Aptos ExtraBold", False),
              900: ("Aptos Black", False)},
}


def face_for(family, weight):
    """CSS family + weight -> the PPTX typeface name and bold flag."""
    table = WEIGHT_FAMILY.get(family)
    if not table:
        return family, weight >= 600          # Aptos Serif and anything else
    if weight in table:
        return table[weight]
    near = min(table, key=lambda w: abs(w - weight))
    return table[near]


def strip_theme_style(shape):
    """Remove <p:style> from a shape we are giving an explicit fill.

    <p:style> carries a fillRef pointing at the theme's accent1. If PowerPoint
    ever rejects our fill it silently falls back to that, so a broken gradient
    arrives as a plausible blue rather than as something obviously wrong. Same
    reasoning as font-synthesis:none in the HTML: fail visibly or not at all."""
    el = shape._element
    st = el.find("{http://schemas.openxmlformats.org/presentationml/2006/main}style")
    if st is not None:
        el.remove(st)


def apply_gradient(shape, css, force=False):
    """Write <a:gradFill> into the shape at the schema-correct position.

    ECMA-376 CT_ShapeProperties is a SEQUENCE: xfrm, geometry, fill, ln,
    effectLst. Appending the fill and then shuffling <a:ln> to the end produced
    `xfrm, prstGeom, effectLst, gradFill, ln`, which LibreOffice renders happily
    and PowerPoint repairs by DISCARDING the fill and falling back to the theme
    colour. So let python-pptx place the element, then rewrite its children.
    See REG-19."""
    from lxml import etree
    g = parse_gradient(css)
    if not g:
        return False
    ang, stops = g
    ns = "http://schemas.openxmlformats.org/drawingml/2006/main"
    q = lambda t: "{%s}%s" % (ns, t)

    shape.fill.gradient()                       # inserts <a:gradFill> in sequence
    spPr = shape._element.spPr
    grad = spPr.find(q("gradFill"))
    if grad is None:
        return False
    for child in list(grad):
        grad.remove(child)
    grad.set("flip", "none")
    grad.set("rotWithShape", "1")

    lst = etree.SubElement(grad, q("gsLst"))
    for (r, gg, b), pos, al in stops:
        gs = etree.SubElement(lst, q("gs"))
        gs.set("pos", str(int(round(max(0.0, min(100.0, pos)) * 1000))))
        clr = etree.SubElement(gs, q("srgbClr"))
        clr.set("val", "%02X%02X%02X" % (r, gg, b))
        if al < 1.0:
            a_el = etree.SubElement(clr, q("alpha"))
            a_el.set("val", str(int(round(al * 100000))))
    lin = etree.SubElement(grad, q("lin"))
    lin.set("ang", str(int(round(((ang - 90) % 360) * 60000))))
    lin.set("scaled", "0")
    return True



# ------------------------------------------------------------------ shadows --
# DrawingML <a:outerShdw> maps to CSS box-shadow with one real loss: there is no
# `spread`. CSS expands the shadow shape by the spread BEFORE blurring; PPTX can
# only blur. Folding the spread into the blur radius is the closest honest
# approximation, and it errs soft rather than tight.
#
#   dist    hypot(dx, dy) in EMU
#   dir     atan2(dy, dx) clockwise from +x, in 60000ths of a degree
#   blurRad (blur + spread) in EMU
#   alpha   the rgba alpha, in 1000ths of a percent
SHADOW_RE = re.compile(
    r"(rgba?\([^)]*\))\s*(-?[\d.]+)px\s+(-?[\d.]+)px\s+(-?[\d.]+)px(?:\s+(-?[\d.]+)px)?")


def apply_shadow(shape, css):
    """CSS box-shadow -> <a:outerShdw>. Returns False if there is nothing to do."""
    import math
    from lxml import etree
    m = SHADOW_RE.search(css or "")
    if not m:
        return False
    col = m.group(1)
    dx, dy, blur = (float(m.group(i)) for i in (2, 3, 4))
    spread = float(m.group(5) or 0)
    r, g, b = rgb(col)
    al = alpha(col)

    ns = "http://schemas.openxmlformats.org/drawingml/2006/main"
    spPr = shape._element.spPr
    # get_or_add keeps effectLst in sequence after <a:ln>; appending it by hand
    # is what broke the fill ordering in the first place.
    eff = spPr.get_or_add_effectLst()
    for child in list(eff):
        eff.remove(child)
    sh = etree.SubElement(eff, "{%s}outerShdw" % ns)
    sh.set("blurRad", str(int(round((blur + spread) * EMU_PX))))
    sh.set("dist", str(int(round(math.hypot(dx, dy) * EMU_PX))))
    sh.set("dir", str(int(round((math.degrees(math.atan2(dy, dx)) % 360) * 60000))))
    sh.set("rotWithShape", "0")
    clr = etree.SubElement(sh, "{%s}srgbClr" % ns)
    clr.set("val", "%02X%02X%02X" % (r, g, b))
    a_el = etree.SubElement(clr, "{%s}alpha" % ns)
    a_el.set("val", str(int(round(al * 100000))))
    return True


_ICON_CACHE = {}


def _icon_key(ic):
    return (ic["markup"], ic["color"], int(ic["w"]), int(ic["h"]))


def prerender_icons(recs, tmp):
    """Rasterise every distinct .ico in the deck, in ONE browser session.

    PowerPoint has no SVG. The lockup and the arrow solve that by being pre-baked into
    assets/export, but that answer does not scale here: 497 marks across five sizes and
    three inks is a grid of thousands of plates, almost none of which a given deck uses.
    These are made per build instead, so the plugin carries vectors and the PPTX carries
    the handful of rasters this deck actually needs.

    One browser for the whole deck rather than one per icon. The first cut launched
    Chromium inside the slide-writing loop and a thirteen-slide deck spent most of its
    export starting browsers.

    Rendered at 4x and reduced with LANCZOS. At 96px an icon's drawn line is about 7px and
    at 24px it is under 2px, which a 1x rasteriser turns to mush on the diagonals. That is
    the same reason bake_export_assets.py renders at 2x; icons need more because they are
    finer than anything else in the system.

    The colour comes from the ELEMENT, not the file. `currentColor` means nothing outside
    a browser, so rasterising the source as-is produces black on every slide, including
    the ones where the mark is meant to be white on the dark emphasis ground.
    """
    jobs = {}
    for rec in recs:
        for ic in rec.get("icons", []):
            jobs.setdefault(_icon_key(ic), ic)
    if not jobs:
        return 0
    try:
        from playwright.sync_api import sync_playwright
        from browser import launch
        from PIL import Image
    except Exception:
        return 0
    S = 4
    with sync_playwright() as pw:
        b = launch(pw)
        pg = b.new_page(viewport={"width": 900, "height": 900})
        for n, (key, ic) in enumerate(jobs.items()):
            w, h = max(1, int(ic["w"])), max(1, int(ic["h"]))
            col = ic["color"] or "#1F1F1F"
            svg = ic["markup"].replace("currentColor", col)
            pg.set_content(
                "<!DOCTYPE html><meta charset='utf-8'><style>*{margin:0;padding:0}"
                "html,body{background:transparent}"
                "#b{width:%dpx;height:%dpx;color:%s}#b svg{width:100%%;height:100%%;display:block}"
                "</style><div id='b'>%s</div>" % (w * S, h * S, col, svg))
            pg.wait_for_timeout(60)
            out = os.path.join(tmp, "ico-%03d.png" % n)
            pg.locator("#b").screenshot(path=out, omit_background=True)
            im = Image.open(out).resize((w, h), Image.LANCZOS)
            im.save(out)
            _ICON_CACHE[key] = out
        b.close()
    return len(jobs)


def rasterise_icon(ic, tmp):
    return _ICON_CACHE.get(_icon_key(ic))


def data_to_file(src, tmp, n):
    if src.startswith("data:"):
        head, b64 = src.split(",", 1)
        ext = ".png" if "png" in head else (".svg" if "svg" in head else ".jpg")
        p = os.path.join(tmp, "img%03d%s" % (n, ext))
        with open(p, "wb") as fh:
            fh.write(base64.b64decode(b64))
        return p
    return src if os.path.exists(src) else None


def build(slides, out, tmp):
    from pptx import Presentation
    from pptx.util import Emu, Pt
    from pptx.dml.color import RGBColor
    from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
    from PIL import Image
    used_faces = set()

    ALIGN = {"left": PP_ALIGN.LEFT, "center": PP_ALIGN.CENTER, "right": PP_ALIGN.RIGHT}
    prs = Presentation()
    prs.slide_width, prs.slide_height = Emu(W * EMU_PX), Emu(H * EMU_PX)
    blank = prs.slide_layouts[6]
    E = lambda v: Emu(int(round(v * EMU_PX)))
    nimg = [0]

    def picture(sl, path, x, y, w, h):
        sl.shapes.add_picture(path, E(x), E(y), E(w), E(h))

    nico = prerender_icons(slides, tmp)
    if nico:
        print("rasterised %d distinct icon%s for the PPTX" % (nico, "" if nico == 1 else "s"))

    for i, rec in enumerate(slides):
        sl = prs.slides.add_slide(blank)

        # 1. ground plate, or nothing when a bleed photo is the ground
        key = (rec["ground"], rec["mesh"]) if rec["mesh"] else (rec["ground"], None)
        plate = GROUND.get(key) or GROUND.get((rec["ground"], None))
        placed = False
        if rec.get("groundGrad") and not rec["mesh"]:
            bg = sl.shapes.add_shape(1, E(0), E(0), E(W), E(H))
            bg.line.fill.background(); bg.shadow.inherit = False
            if apply_gradient(bg, rec["groundGrad"]):
                placed = True                      # axis-aligned: safe and editable
            else:
                bg._element.getparent().remove(bg._element)   # off-axis: use the plate
        if not placed and plate:
            picture(sl, os.path.join(EXPORT, plate + ".png"), 0, 0, W, H)

        # ONE ordered pass. Decoration and content are interleaved by DOM order, which is
        # the order the browser paints them in and the order PowerPoint paints shapes in.
        # x may be negative: the flex triangle is meant to run off the frame.
        stream = []
        for d in rec["decor"]:
            stream.append((d.get("ord", 1 << 30), "decor", d))
        for ic in rec.get("icons", []):
            stream.append((ic.get("ord", 1 << 30), "icon", ic))
        if rec["brandx"] and rec.get("brandxOrder") is not None:
            stream.append((rec["brandxOrder"], "brandx", None))
        for it in rec["items"]:
            stream.append((it.get("ord", 1 << 30), "item", it))
        stream.sort(key=lambda t: t[0])

        for _ord, kind, payload in stream:
            if kind == "decor":
                d = payload
                picture(sl, os.path.join(EXPORT, d["asset"] + ".png"),
                        d["x"], d["y"], d["w"], d["h"])
                continue
            if kind == "icon":
                # Rasterised here, at this deck's own sizes and inks, rather than pulled
                # from a pre-baked plate. Rendered at 4x and reduced, because an icon is
                # 1.1px of line on a 16 grid and a 1x raster of that is mush. The fill is
                # substituted from the element's RESOLVED colour: the source paints with
                # `currentColor`, which means nothing outside a browser.
                p = rasterise_icon(payload, tmp)
                if p:
                    picture(sl, p, payload["x"], payload["y"], payload["w"], payload["h"])
                continue
            if kind == "brandx":
                # One asset per variant. Both plates are full-canvas RGBA with the shape
                # painted and the rest transparent, so the placement is the same and only
                # the artwork differs. An unrecognised variant is a hard stop rather than a
                # guess: guessing here shipped a dark plate under a light slide's text.
                asset = rec["brandx"]
                if not asset or asset.startswith("UNKNOWN"):
                    raise SystemExit(
                        "slide %d carries a Brand X this exporter does not know (%s). Add a "
                        "baked plate for it in bake_export_assets.py and map it here; do "
                        "not fall back to another variant's artwork." % (i + 1, asset))
                path = os.path.join(EXPORT, asset + ".png")
                if not os.path.exists(path):
                    raise SystemExit("missing %s. Run scripts/bake_export_assets.py" % path)
                picture(sl, path, 0, 0, W, H)
                continue
            it = payload
            cls = it.get("classes", [])
            if any(c in BAKED for c in cls):
                continue

            if it["kind"] == "img":
                if any(c in BAKED for c in cls):
                    continue
                p = data_to_file(it["src"], tmp, nimg[0]); nimg[0] += 1
                if not p or p.endswith(".svg"):
                    continue
                b = it["box"]
                if it["cover"] and it["clip"]:
                    # CSS object-fit: cover. Crop the source to the frame's
                    # aspect rather than letting PowerPoint stretch it.
                    c = it["clip"]
                    im = Image.open(p)
                    sr, tr = im.width / im.height, c["w"] / c["h"]
                    # object-position, not a fixed centre. "center 40%" means the point
                    # 40% down the image lands 40% down the frame, so the crop offset is
                    # the overflow times that fraction.
                    ox, oy = it.get("objPos") or (0.5, 0.5)
                    if sr > tr:
                        nw = int(im.height * tr); l = int(round((im.width - nw) * ox))
                        im = im.crop((l, 0, l + nw, im.height))
                    else:
                        nh = int(im.width / tr); t = int(round((im.height - nh) * oy))
                        im = im.crop((0, t, im.width, t + nh))
                    p2 = p.rsplit(".", 1)[0] + "-crop.jpg"
                    im.convert("RGB").save(p2, quality=92)
                    picture(sl, p2, c["x"], c["y"], c["w"], c["h"])
                else:
                    picture(sl, p, b["x"], b["y"], b["w"], b["h"])
                continue

            if it["kind"] == "box":
                b = it["box"]
                # 9 = MSO_AUTO_SHAPE_TYPE.OVAL. A pseudo-element bullet is round because its
                # CSS is (border-radius:50%), and a rectangle in its place reads as a mistake,
                # not a dot.
                shape_type = 9 if it.get("oval") else 1
                sh = sl.shapes.add_shape(shape_type, E(b["x"]), E(b["y"]), E(b["w"]), E(b["h"]))
                strip_theme_style(sh)
                sh.line.fill.background()
                sh.shadow.inherit = False          # drop PowerPoint's dated preset
                if not (it.get("grad") and apply_gradient(sh, it["grad"])):
                    sh.fill.solid()
                    sh.fill.fore_color.rgb = RGBColor(*rgb(it["fill"]))
                if it.get("shadow"):
                    apply_shadow(sh, it["shadow"])  # then put the real one back
                continue

            # text
            #
            # First its own plate, if it has one. See the probe's fillBox note: a painted
            # element that owns its text emitted no fill at all until v4.9, so .badge's
            # gradient square went missing and took its white numeral's legibility with it.
            fb = it.get("fillBox")
            if fb:
                plate = sl.shapes.add_shape(9 if it.get("fillOval") else 1,
                                            E(fb["x"]), E(fb["y"]), E(fb["w"]), E(fb["h"]))
                strip_theme_style(plate)
                plate.line.fill.background()
                plate.shadow.inherit = False
                if not (it.get("grad") and apply_gradient(plate, it["grad"])):
                    plate.fill.solid()
                    plate.fill.fore_color.rgb = RGBColor(*rgb(it["fill"]))
                if it.get("fillShadow"):
                    apply_shadow(plate, it["fillShadow"])

            b = it["box"]
            tb = sl.shapes.add_textbox(E(b["x"] - 6), E(b["y"] - 4),
                                       E(b["w"] + 12), E(b["h"] + 8))
            tf = tb.text_frame
            tf.word_wrap = True
            tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = 0
            # TOP is right for the overwhelming majority: a headline set in a slot sits at
            # the slot's top and grows down. MIDDLE only where the CSS actually centres it.
            # The -6/-4 bearing and the +12/+8 growth are symmetric, so a centred anchor
            # still lands on the element's own centre.
            tf.vertical_anchor = MSO_ANCHOR.MIDDLE if it.get("vMid") else MSO_ANCHOR.TOP
            # If the browser set it on one line, PowerPoint must not wrap it. A
            # substituted font is wider, and wrapping is what put the eyebrow
            # through the headline in an earlier build.
            tf.word_wrap = it.get("lines", 2) > 1

            groups, cur = [], []
            for run in it.get("runs") or [{"t": it["text"], "c": it["color"], "w": it["weight"]}]:
                if run.get("br"):
                    groups.append(cur); cur = []
                else:
                    cur.append(run)
            groups.append(cur)

            for i, grp in enumerate(g for g in groups if g):
                para = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
                para.alignment = (PP_ALIGN.CENTER if it.get("hMid")
                                  else ALIGN.get(it["align"], PP_ALIGN.LEFT))
                if it["leading"]:
                    para.line_spacing = Pt(it["leading"] * PT_PX)
                for run in grp:
                    txt = run["t"]
                    if not txt:
                        continue
                    r = para.add_run()
                    r.text = txt.upper() if it["upper"] else txt
                    f = r.font
                    face, is_bold = face_for(it["font"], run.get("w", it["weight"]))
                    used_faces.add(face)
                    f.name = face
                    f.size = Pt(round(it["size"] * PT_PX, 1))
                    f.bold = is_bold
                    f.color.rgb = RGBColor(*rgb(run.get("c") or it["color"]))
                    if it["tracking"]:
                        # PPTX character spacing is in points, same 0.5 factor.
                        r.font._rPr.set("spc", str(int(round(it["tracking"] * PT_PX * 100))))

        # 2. the bug is the ONE thing that is always last. It is the corner mark and
        # nothing may cross it (GEO-04 reserves its box), so its z-order is not a
        # judgement call the way the other devices' are.
        if rec["bug"]:
            picture(sl, os.path.join(EXPORT, "bug-%s.png" % rec["bug"]), 1754, 774, 275, 286)

    prs.save(out)
    return used_faces



# ----------------------------------------------------------- font embedding --
# PPTX carries fonts as parts: ppt/fonts/fontN.fntdata, a Default content-type
# for the extension, a relationship per face, and <p:embeddedFontLst> in
# presentation.xml. All six Aptos cuts are fsType 0x0008 (Editable Embedding),
# which is exactly the permission this uses.
#
# Two things to know:
#   * CT_Presentation is a SEQUENCE. <p:embeddedFontLst> goes after <p:notesSz>
#     and before <p:defaultTextStyle>. Same class of trap as REG-19.
#   * .fntdata here is raw TTF, not Word's obfuscated .odttf. If that is ever
#     wrong the embed fails SILENTLY and the deck still looks right on a machine
#     that has Aptos installed. Test on a machine without it. See REG-22.
#   * WHAT EMBEDDING DOES NOT COVER, and say this out loud when handing a deck over.
#     Embedded fonts are a Windows PowerPoint feature. PowerPoint for Mac, Keynote,
#     Google Slides and LibreOffice all ignore ppt/fonts/ entirely. Measured: with Aptos
#     hidden from the OS, LibreOffice rendered a correctly embedded deck end to end in
#     DejaVu Sans. So embedding is a fallback, not a guarantee. The durable answers are
#     Aptos installed on the opening machine, which Microsoft 365 provides, or a PDF.
# Typeface -> slot -> the face brand_assets.py resolves on this machine (by the name
# inside the file, so Office's numbered cloud-font files are found too).
FACE_FILES = {
    "Aptos":           {"regular": "Aptos", "bold": "Aptos Bold"},
    "Aptos SemiBold":  {"regular": "Aptos SemiBold"},
    "Aptos ExtraBold": {"regular": "Aptos ExtraBold"},
    "Aptos Black":     {"regular": "Aptos Black"},
    "Aptos Serif":     {"boldItalic": brand_assets.SERIF},
}
RT_FONT = "http://schemas.openxmlformats.org/officeDocument/2006/relationships/font"


def embed_fonts(path, faces):
    """Rewrite the .pptx zip with the given typefaces embedded."""
    import shutil, zipfile, tempfile
    plan, missing = [], []
    for face in faces:
        for slot, name in FACE_FILES.get(face, {}).items():
            src = brand_assets.font_path(name, (".ttf", ".otf"))
            if src:
                plan.append((face, slot, src))
            else:
                missing.append(name)
    # Loud, not silent: a deck without its faces reflows on every machine without Aptos,
    # and verify_pptx FNT-01 will fail it anyway. Say why here, where it can be fixed.
    if missing:
        print("WARNING: " + brand_assets.fonts_help(sorted(set(missing))), file=sys.stderr)
    if not plan:
        return 0

    zin = zipfile.ZipFile(path)
    items = {n: zin.read(n) for n in zin.namelist()}
    zin.close()

    ct = items["[Content_Types].xml"].decode()
    if "fntdata" not in ct:
        ct = ct.replace("<Types ", '<Types ', 1)
        i = ct.index(">", ct.index("<Types")) + 1
        ct = (ct[:i] + '<Default Extension="fntdata" '
              'ContentType="application/x-fontdata"/>' + ct[i:])
    items["[Content_Types].xml"] = ct.encode()

    rels = items["ppt/_rels/presentation.xml.rels"].decode()
    used = [int(m) for m in re.findall(r'Id="rId(\d+)"', rels)] or [0]
    nid = max(used) + 1

    by_face, adds = {}, []
    for n, (face, slot, src) in enumerate(plan, 1):
        part = "ppt/fonts/font%d.fntdata" % n
        with open(src, "rb") as fh:
            items[part] = fh.read()
        rid = "rId%d" % nid; nid += 1
        adds.append('<Relationship Id="%s" Type="%s" Target="fonts/font%d.fntdata"/>'
                    % (rid, RT_FONT, n))
        by_face.setdefault(face, []).append((slot, rid))
    rels = rels.replace("</Relationships>", "".join(adds) + "</Relationships>")
    items["ppt/_rels/presentation.xml.rels"] = rels.encode()

    lst = ["<p:embeddedFontLst>"]
    for face, slots in by_face.items():
        lst.append('<p:embeddedFont><p:font typeface="%s" pitchFamily="34" charset="0"/>' % face)
        # CT_EmbeddedFontDataIdList is a sequence: regular, bold, italic,
        # boldItalic. Sorting alphabetically put bold first and the schema
        # rejected it. Same trap as REG-19, caught pre-flight this time.
        SLOT_ORDER = ("regular", "bold", "italic", "boldItalic")
        for slot in SLOT_ORDER:
            for sl_name, rid in slots:
                if sl_name == slot:
                    lst.append('<p:%s r:id="%s"/>' % (slot, rid))
        lst.append("</p:embeddedFont>")
    lst.append("</p:embeddedFontLst>")
    xml = "".join(lst)

    pres = items["ppt/presentation.xml"].decode()
    # sequence position: after notesSz, before defaultTextStyle
    m = re.search(r"<p:notesSz[^>]*/>", pres)
    if m:
        pres = pres[:m.end()] + xml + pres[m.end():]
    else:
        pres = pres.replace("<p:defaultTextStyle>", xml + "<p:defaultTextStyle>", 1)
    # embedTrueTypeFonts="1" on <p:presentation>. This was missing for every revision up
    # to 4.6 and the parts, content type, relationships and list were all correct without
    # it, which is why nothing looked wrong. PowerPoint writes this attribute whenever it
    # saves with "Embed fonts in the file", so a package that carries font data without it
    # is not shaped like one PowerPoint made. Match what PowerPoint does.
    #
    # saveSubsetFonts is set to 0 deliberately: these are whole fonts, not subsets, and
    # claiming a subset we did not make is a claim a reader cannot check.
    if "embedTrueTypeFonts=" not in pres:
        pres = re.sub(r"(<p:presentation\b)", r'\1 embedTrueTypeFonts="1"', pres, count=1)
    pres = pres.replace('saveSubsetFonts="1"', 'saveSubsetFonts="0"')
    items["ppt/presentation.xml"] = pres.encode()

    tmp = path + ".tmp"
    with zipfile.ZipFile(tmp, "w", zipfile.ZIP_DEFLATED) as z:
        for n, data in items.items():
            z.writestr(n, data)
    shutil.move(tmp, path)
    return len(plan)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("source")
    ap.add_argument("-o", "--out", required=True)
    ap.add_argument("--no-embed", action="store_true",
                    help="do not embed the Aptos faces in the deck")
    ap.add_argument("--no-fit", action="store_true",
                    help="skip the stage-scaling script (single-slide exports only)")
    args = ap.parse_args()

    missing = [k for k in ("brandx-cover", "brandx-r10", "bug-light", "bug-dark",
                          "ground-light-mesh-h")
               if not os.path.exists(os.path.join(EXPORT, k + ".png"))]
    if missing:
        sys.exit("baked assets missing: %s\nrun scripts/bake_export_assets.py first"
                 % ", ".join(missing))

    import tempfile
    with tempfile.TemporaryDirectory() as tmp:
        slides = probe(args.source)
        faces = build(slides, args.out, tmp)
    if not args.no_embed:
        n = embed_fonts(args.out, faces)
        print("embedded %d font file(s): %s" % (n, ", ".join(sorted(faces))))
    print("wrote %s (%d slides, %.2f MB)"
          % (args.out, len(slides), os.path.getsize(args.out) / 1048576))


if __name__ == "__main__":
    main()
