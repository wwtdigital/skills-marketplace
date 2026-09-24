#!/usr/bin/env python3
"""
wwt_validate.py — WWTDigital Presentation Design System v1.0 validator.

Drives headless Chromium over a rendered WWT deck and reports every measurable
violation of the design system with a rule ID, slide index, selector and measured
value. Exit code 1 if any FAIL fires.

    python3 wwt_validate.py deck.html
    python3 wwt_validate.py deck.html --roles roles.json --json report.json
    python3 wwt_validate.py deck.html --only GEO,MRK --quiet

roles.json maps slide index to role so the ink-coverage band can be judged:
    {"0":"cover","1":"divider","2":"statement","3":"content","4":"data","5":"closing"}
A slide may instead carry data-role="content" in the markup, which wins.
Slides marked data-role="spec" are documentation specimens: geometry, colour and
mark rules still apply, composition rules do not.

Requires: playwright, pillow, numpy.
"""
import argparse, json, sys, os, math
import re
import collections
from collections import defaultdict

CANVAS_W, CANVAS_H = 1920, 1080

# ---------------------------------------------------------------- design system constants
TOKENS = {
    "#0086EA": "wwt-blue", "#330072": "wwt-purple", "#EE282A": "wwt-red",
    "#000000": "ink-900", "#1F1F1F": "ink-800", "#404040": "ink-600",
    "#656565": "ink-500", "#808080": "ink-400", "#BFBFBF": "ink-200",
    "#E4E4E4": "ink-100", "#F6F6F6": "surface", "#FFFFFF": "white",
    "#FAFAFB": "table-alt", "#111111": "device-body",
    # the dark emphasis ground, node 1892:32. Its own values, not the brand pair darkened.
    "#1D569E": "wwt-blue-dark", "#28115C": "wwt-purple-dark",
}
LADDER = {200, 176, 128, 112, 96, 80, 64, 57, 56, 48, 45, 40, 36, 32, 30, 28, 26, 24, 22, 20}
COLS = [72 + i * 150 for i in range(12)]                      # 72,222,…,1722
SPANS = {576, 726, 876, 1026, 1176, 1326, 1476, 1626, 1776, 426, 276, 126}
INK_BAND = {  # role -> (target_lo, target_hi, hard_floor)
    "cover": (.20, .30, .35), "divider": (.15, .25, .30), "statement": (.25, .35, .40),
    "content": (.35, .45, .50), "data": (.45, .50, .55), "closing": (.20, .30, .35),
}
LOCKUP_ROLES = {"cover", "closing"}   # the source divider carries the bug, not the lockup
RESERVE = (1784, 984, 1920, 1080)   # bug reservation: the mark box plus 19px clearspace,
                                    # rounded out to the 8px grid. 136 x 96.

SEV = {"FAIL": 2, "WARN": 1}
INK = {}   # slide index -> measured ink coverage

# ---------------------------------------------------------------- density and presence
# THE ANTI-GAMING DOCTRINE, and the reason these constants are shaped the way they are.
#
# Every rule that says "X must be present" can be satisfied by adding X and doing nothing
# else. A photography floor invites a thumbnail. A density floor invites one enormous empty
# rectangle. A diversity rule invites nudging a headline 20px. So each presence rule below
# is paired with a substance test, and each threshold is set so that THE CHEAPEST WAY TO
# PASS IS THE RIGHT THING TO DO.
#
# Three specific closures:
#   1. An EMPTY PANEL IS GROUND. It contributes nothing to coverage, so a 1776 x 700 grey
#      box cannot buy a density pass. Same principle GEO-04 already uses.
#   2. A PHOTOGRAPH COUNTS ONLY AT A REAL CROP, and the deck is checked for gaps as well as
#      for share, so front-loading the quota and coasting does not work.
#   3. ARCHITECTURE IS BUCKETED, not exact. Drift cannot move a slide into a new bucket.
#
# Every number here was measured off the two decks we have accepted rather than chosen.
# Re-run scripts/calibrate.py after any change and keep the thresholds outside the spread.
#
#   measured, AI GTM (7 slides) and AI Built for Success (13 slides):
#     photography share            29% / 38%
#     longest photo-free run        5  /  4
#     device on light grounds     100% / 91%   (the one exception is a table slide)
#     content coverage, minimum   0.39 / 0.22
#     content atoms, minimum        22 /  11
#     content words, minimum       117 /  54
#     largest architecture share   29% / 23%
#     architecture entropy        0.96 / 0.95
#   for contrast, the 91-slide RFP deck that prompted these rules:
#     photography 12%, photo-free run 24, device 2%, median coverage 0.08

# role -> (coverage FAIL floor, coverage WARN floor, atom FAIL floor, word FAIL floor)
SUBSTANCE = {
    "content":   (0.15, 0.24, 8, 35),
    "data":      (0.15, 0.24, 8, 35),
    "statement": (0.10, 0.14, 4, 12),
    "cover":     (0.10, 0.13, 3,  6),
    "divider":   (0.08, 0.12, 3,  6),
    "closing":   (0.10, 0.13, 3,  6),
}
# Roles with a lower substance bar. Capped as a share of the deck so that relabelling a
# thin content slide as a statement cannot buy a pass.
SPARSE_ROLES = {"cover", "divider", "statement", "closing"}
SPARSE_MAX = 0.35

# How many photographs the library actually holds, read from the manifest rather than
# typed, so IMG-08's arithmetic follows the library when a frame is added or retired.
def _library_size():
    try:
        d = json.load(open(os.path.join(os.path.dirname(os.path.dirname(
            os.path.abspath(__file__))), "assets", "manifest.json"), encoding="utf-8"))
        return sum(1 for v in d.values() if isinstance(v, dict) and "crops" in v)
    except Exception:
        return 19


LIBRARY_SIZE = _library_size()
# A slide carries photography when the imagery on it SUMS to this much of the canvas.
#
# This was 0.06 and it was the largest single image, which is two mistakes in one number.
# 0.06 is the crop table's smallest entry, the card at 525 x 260, so a rule meant to stop
# a thumbnail standing in for photography was set exactly AT thumbnail size. Decks came
# back with a 726 x 184 strip pushed into the top-right corner, relating to nothing, on
# nine slides of one deck, each one satisfying the rule. The floor was being read as the
# specification, which is what a floor does when it is set where the cheapest answer sits.
#
# And the sum, not the largest, because a slide earns its imagery from the total area the
# reader sees. Three card images in a row at 6.6% each is a card row and it works. One of
# them alone in a corner is a compliance token. Measured across five decks: everything
# judged acceptable sums to 15.4% or more, everything judged wrong sums to 10.7% or less,
# and nothing at all falls in between, so this threshold runs through empty space rather
# than through a judgment call.
PHOTO_MIN_AREA = 0.15
PHOTO_FLOOR = 0.30      # deck share, FAIL below
PHOTO_WARN = 0.40       # the target
PHOTO_MAX_GAP = 6       # consecutive slides with no photograph
ARCH_MAX_SHARE = 0.40
ARCH_MIN_ENTROPY = 0.72
DECK_WARN_LEN = 30
DECK_FAIL_LEN = 40
DUP_HAMMING = 6         # of 256 bits
# The dark emphasis ground, by direction: at most one slide in five, and never two in a row.
# A CEILING, not a floor. See PAT-09.
DARK_MAX_SHARE = 0.20
# Text inside a panel must clear its edge. The defect this catches is text FLUSH to the
# corner, which is what an overridden padding:0 produces. A first cut set the floor at 24
# and failed my own GTM cards at 18/22, which are tight on a 426px card but deliberate.
# 12 separates broken from tight; 24 is the comfortable target and only warns.
PANEL_MIN_INSET = 12
PANEL_TIGHT_INSET = 24
# Relative luminance of the backdrop behind the bug, measured off the rendered plate.
# Above the first the ground reads light and needs the plain .bug; below the second it reads
# dark and needs .bug--dark. The gap between them is deliberately unjudged.
BUG_LIGHT_L = 0.55
BUG_DARK_L = 0.18
# A content panel more than this fraction empty below its last content is a dead box.
PANEL_MAX_EMPTY = 0.35
# How many distinct sizes ONE JOB may use across a deck. Body copy and card interiors are
# counted separately, so this is per job: two allows a deck to shift once, three is drift.
BODY_STEPS_MAX = 2

PLACEHOLDER = ("lorem ipsum", "dolor sit amet", "tk tk", "xxx placeholder",
               "todo:", "tbd:", "[insert", "lipsum")

# ---------------------------------------------------------------- colour helpers
def _lin(c):
    c /= 255.0
    return c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4

def lum(rgb):
    r, g, b = rgb[:3]
    return 0.2126 * _lin(r) + 0.7152 * _lin(g) + 0.0722 * _lin(b)

def contrast(l1, l2):
    hi, lo = max(l1, l2), min(l1, l2)
    return (hi + 0.05) / (lo + 0.05)

def parse_rgb(s):
    if not s or s in ("transparent", "none"):
        return None
    s = s.strip()
    if s.startswith("#"):
        h = s[1:]
        if len(h) == 3:
            h = "".join(c * 2 for c in h)
        return (int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16), 1.0)
    if s.startswith("rgb"):
        n = [float(x) for x in s[s.index("(") + 1:s.index(")")].replace("/", " ").replace(",", " ").split()]
        if len(n) == 3:
            return (n[0], n[1], n[2], 1.0)
        if len(n) >= 4:
            a = n[3] / 100.0 if n[3] > 1 else n[3]
            return (n[0], n[1], n[2], a)
    return None

def hexof(rgb):
    return "#%02X%02X%02X" % (int(round(rgb[0])), int(round(rgb[1])), int(round(rgb[2])))

def near_token(rgb, tol=6):
    """Is this colour a system token (allowing alpha compositing over surface/white)?"""
    if rgb is None:
        return True
    for hx in TOKENS:
        t = parse_rgb(hx)
        if all(abs(rgb[i] - t[i]) <= tol for i in range(3)):
            return True
    # alpha-composited tokens over the two legal grounds
    for ground in ((246, 246, 246), (255, 255, 255), (0, 0, 0)):
        for hx in TOKENS:
            t = parse_rgb(hx)
            for a in (0.93, 0.9, 0.8, 0.72, 0.62, 0.5, 0.36, 0.3, 0.22, 0.18, 0.11, 0.1):
                comp = [t[i] * a + ground[i] * (1 - a) for i in range(3)]
                if all(abs(rgb[i] - comp[i]) <= tol for i in range(3)):
                    return True
    return False

# ---------------------------------------------------------------- browser probe
PROBE = r"""
(() => {
  const CW = 1920, CH = 1080;
  const q = (el, sel) => el.matches && el.matches(sel);
  const cls = el => (el.className && el.className.toString ? el.className.toString() : '');
  const sel = el => {
    let s = el.tagName.toLowerCase();
    const c = cls(el).trim().split(/\s+/).filter(Boolean).slice(0, 3);
    if (c.length) s += '.' + c.join('.');
    return s;
  };
  const slides = [...document.querySelectorAll('.slide')];
  return slides.map((s, idx) => {
    const sr = s.getBoundingClientRect();
    const k = sr.width / CW || 1;
    const box = el => {
      const r = el.getBoundingClientRect();
      return { x: (r.left - sr.left) / k, y: (r.top - sr.top) / k,
               w: r.width / k, h: r.height / k,
               x2: (r.right - sr.left) / k, y2: (r.bottom - sr.top) / k,
               cx: r.left, cy: r.top, cw: r.width, ch: r.height };
    };
    const nodes = [];
    let di = 0;
    const order = new Map();
    s.querySelectorAll('*').forEach(el => order.set(el, di++));
    s.querySelectorAll('*').forEach(el => {
      const cs = getComputedStyle(el);
      if (cs.display === 'none' || cs.visibility === 'hidden') return;
      const b = box(el);
      if (b.w < 1 || b.h < 1) return;
      // direct text content only (leaf-ish text carriers)
      let txt = '';
      for (const n of el.childNodes) if (n.nodeType === 3) txt += n.textContent;
      txt = txt.trim();
      nodes.push({
        sel: sel(el), tag: el.tagName.toLowerCase(), cls: cls(el),
        box: b, text: txt.slice(0, 60), hasText: txt.length > 0,
        fs: parseFloat(cs.fontSize), lh: (parseFloat(cs.lineHeight) || 0),
        fw: cs.fontWeight, ff: cs.fontFamily, tt: cs.textTransform,
        color: (el.ownerSVGElement && cs.fill && cs.fill !== 'none') ? cs.fill : cs.color,
        bg: cs.backgroundColor, bgImg: cs.backgroundImage,
        op: parseFloat(cs.opacity), blend: cs.mixBlendMode,
        declared: el.getAttribute('data-component')
                  || (el.closest('[data-component]') ? 'inherited' : null),
        alt: el.getAttribute('alt'), ariaHidden: el.getAttribute('aria-hidden'),
        role: el.getAttribute('role'), ariaLabel: el.getAttribute('aria-label'),
        scrollW: el.scrollWidth, clientW: el.clientWidth,
        inChrome: !!(el.closest && el.closest('.gridover, .doc-anno, .spec-note')),
        di: order.get(el),
        subtreeEnd: order.get(el) + el.querySelectorAll('*').length,
        z: (cs.zIndex === 'auto' ? 0 : parseInt(cs.zIndex, 10) || 0),
        parentSel: el.parentElement ? sel(el.parentElement) : null,
        depth: (() => { let d = 0, p = el; while (p && p !== s) { d++; p = p.parentElement; } return d; })(),
        // Subtree substance. `hasText` above is DIRECT text only, which is what made a
        // panel indistinguishable from a panel with something in it: an empty 1776 x 700
        // box counted toward ink exactly like a full one. These three answer "is this
        // element doing a job", which is what every presence rule has to test.
        deepWords: (el.innerText || '').trim().split(/\s+/).filter(Boolean).length,
        deepImgs: el.querySelectorAll('img, svg[viewBox]').length,
        // Photograph IDENTITY, for IMG-07 and IMG-08. By the time the validator sees a
        // deck the assets are inlined, so every src is a base64 blob and the library name
        // is gone. A cheap fingerprint of the blob is enough to answer "is this the same
        // photograph": take the length and three slices, which no two distinct JPEGs in
        // this library collide on. Chrome cannot hash in the page, and hashing four
        // megabytes of base64 per slide would be slower than the rest of the probe.
        // Only real photography counts. The bug mark and the lockup repeat by design.
        photoId: (() => {
          if (el.tagName !== 'IMG') return null;
          const src = el.getAttribute('src') || '';
          if (!src.startsWith('data:image/jp')) return null;   // jpeg == the library
          const r = el.getBoundingClientRect();
          if (r.width * r.height < 40000) return null;         // an icon, not a photograph
          return src.length + ':' + src.slice(60, 76) + src.slice(-16);
        })(),
        deepBoxes: el.querySelectorAll('.panel,.stat,.chip,.badge,.prac,.layer,.feat,table').length,
        // Rendered line geometry. A centred headline sits in a wide box holding narrow
        // text, so box width is not the measure and TYP-04 was reading the wrong number.
        lineRects: (() => {
          try {
            const r = document.createRange(); r.selectNodeContents(el);
            const out = [];
            for (const q of r.getClientRects()) {
              if (q.width < 2 || q.height < 2) continue;
              out.push([Math.round((q.left - sr.left) / k), Math.round((q.right - sr.left) / k)]);
            }
            return out.slice(0, 24);
          } catch (e) { return []; }
        })(),
        align: cs.textAlign,
        padding: cs.padding,
        // Features the PPTX path has no way to express. A deck-local component using one of
        // these degrades silently on export: the test deck's .badge-num lost its gradient
        // and became a white box, and .svc-col's ::before bullet dots vanished entirely.
        unexportable: (() => {
          const bad = [];
          if ((cs.backgroundImage || '').indexOf('linear-gradient') === 0) bad.push('gradient fill');
          if (cs.clipPath && cs.clipPath !== 'none') bad.push('clip-path');
          if (cs.mixBlendMode && cs.mixBlendMode !== 'normal') bad.push('blend mode');
          if (cs.filter && cs.filter !== 'none') bad.push('filter');
          for (const pe of ['::before', '::after']) {
            const q = getComputedStyle(el, pe);
            if (q && q.content && q.content !== 'none' && q.content !== 'normal')
              bad.push('a ' + pe + ' pseudo-element');
          }
          const br = parseFloat(cs.borderTopLeftRadius) || 0;
          if (br > 0 && br >= Math.min(parseFloat(cs.width) || 0, parseFloat(cs.height) || 0) / 2 - 0.5)
            bad.push('a circular border-radius');
          return bad;
        })(),
        // the element's own inset from its nearest positioned .panel ancestor, so a rule
        // can ask whether text is actually inside the box or flush against its edge
        panelInset: (() => {
          const pn = el.parentElement && el.parentElement.closest('.panel');
          if (!pn || pn === el) return null;
          const pr = pn.getBoundingClientRect(), r2 = el.getBoundingClientRect();
          return { l: Math.round((r2.left - pr.left) / k), t: Math.round((r2.top - pr.top) / k),
                   r: Math.round((pr.right - r2.right) / k),
                   b: Math.round((pr.bottom - r2.bottom) / k) };
        })(),
        widow: (() => {
          // Words on the final rendered line, measured across the element's whole text flow
          // (an <em> inside a headline is part of the same flow, not a separate block).
          try {
            const w = document.createTreeWalker(el, NodeFilter.SHOW_TEXT);
            const tns = []; let nd;
            while ((nd = w.nextNode())) if (nd.textContent.trim()) tns.push(nd);
            if (!tns.length) return null;
            const rng = document.createRange();
            const words = [];
            for (const tn of tns) {
              const t = tn.textContent; let i = 0;
              while (i < t.length) {
                while (i < t.length && /\s/.test(t[i])) i++;
                const st = i;
                while (i < t.length && !/\s/.test(t[i])) i++;
                if (i <= st) break;
                rng.setStart(tn, st); rng.setEnd(tn, i);
                const r = rng.getBoundingClientRect();
                if (r.width > 0) words.push([Math.round(r.top), t.slice(st, i)]);
              }
            }
            if (words.length < 3) return null;
            const tops = [...new Set(words.map(x => x[0]))].sort((a, b) => a - b);
            if (tops.length < 2) return null;
            const lastTop = tops[tops.length - 1];
            const onLast = words.filter(x => x[0] === lastTop);
            return onLast.length === 1 ? onLast[0][1] : null;
          } catch (e) { return null; }
        })(),
      });
    });
    return {
      idx, role: s.getAttribute('data-role') || null, slideCls: cls(s),
      buildsOn: s.getAttribute('data-builds-on') || null,
      isGallery: !!document.querySelector('section.doc') ||
                 !!document.querySelector('[data-gallery]'),
      // GAL-01 evidence. A gallery claim switches off the entire deck-level rule family,
      // which is the single cheapest way to make a thin deck pass: add one attribute and
      // density, photography, sequence and the background-device rule all stop applying.
      // So the claim has to be substantiated by something a deck does not have. A
      // reference document explains its specimens, in prose, outside the slides, and
      // attributes each one to a source. A deck does neither.
      // Document furniture, measured outside the slides. Scripts and stylesheets are
      // removed first: a detached clone has no layout, so innerText falls back to
      // textContent and the page's own fit script counted as nine hundred words of prose.
      furniture: idx ? null : (() => {
        const c = document.body.cloneNode(true);
        c.querySelectorAll('.stage, .slide, script, style, noscript, template')
         .forEach(e => e.remove());
        return {
          words: (c.textContent || '').trim().split(/\s+/).filter(Boolean).length,
          heads: c.querySelectorAll('h1,h2,h3,h4').length,
          lists: c.querySelectorAll('table,ul,ol,dl').length,
        };
      })(),
      recipeIds: idx ? null : [...document.querySelectorAll('.slidecap b')]
                  .map(b => (b.textContent.match(/^(\d\d)\b/) || [])[1]).filter(Boolean),
      mapIds: idx ? null : [...document.querySelectorAll('table.spec td:first-child')]
                  .map(t => (t.textContent.match(/^(\d\d)\b/) || [])[1]).filter(Boolean),
      // Every background-image the stylesheet gives to a .mesh--* rule. Collected
      // from the CSS rather than from the DOM so it is still populated on a slide
      // where the mesh art has been misused and no real .mesh element exists.
      meshArt: (() => {
        const out = new Set();
        for (const sh of document.styleSheets) {
          let rules; try { rules = sh.cssRules; } catch (e) { continue; }
          for (const r of rules || []) {
            if (r.selectorText && /\.mesh(--|\b)/.test(r.selectorText)
                && r.style && r.style.backgroundImage
                && r.style.backgroundImage !== 'none') out.add(r.style.backgroundImage);
          }
        }
        return [...out];
      })(),
      k, slideBox: { cx: sr.left, cy: sr.top, cw: sr.width, ch: sr.height },
      w: sr.width / k, h: sr.height / k,
      counts: {
        headline: s.querySelectorAll('.t-display1,.t-display2,.t-h1,.t-h1-lg,.t-h2').length,
        bug: s.querySelectorAll('.bug').length,
        lockup: s.querySelectorAll('.lockup').length,
        mesh: s.querySelectorAll('.mesh').length,
        // .brandx-x is the real cover X and was not counted here, so PAT-01 never saw it.
        brandx: s.querySelectorAll('.brandx, .brandx-x').length,
        // the retired two-div form. Its geometry rules are gone, so an element still
        // asking for it renders 0 x 0 and the node walk skips it: no X, no error.
        brandxOld: s.querySelectorAll('.brandx:not(.brandx--r10)').length,
        // Any Brand X that renders to nothing. The node walk drops sub-pixel boxes, so a
        // slide asking for an X it has no geometry for looked clean. This is how the GTM
        // cover shipped with no X after the class was renamed in one file and not the other.
        brandxDead: [...s.querySelectorAll('.brandx, .brandx-x')].filter(e => {
          const r = e.getBoundingClientRect();
          return r.width < 1 || r.height < 1;
        }).length,
        arrow: s.querySelectorAll('.arrow').length,
        arrowLink: s.querySelectorAll('.arrow--connector,.arrow--link').length,
        dir: s.querySelectorAll('.dir').length,
        tableRows: [...s.querySelectorAll('table.deck tbody')].map(t => t.querySelectorAll('tr').length),
        rowHeights: [...s.querySelectorAll('table.deck tbody tr')].map(r => r.getBoundingClientRect().height / k),
        bulletCounts: [...s.querySelectorAll('ul.b')].map(u => u.querySelectorAll('li').length),
        charts: s.querySelectorAll('svg[viewBox]').length,
        tables: s.querySelectorAll('table.deck').length,
      },
      nodes,
    };
  });
})()
"""

HIDE_TEXT = r"""
(() => {
  // Strip glyphs but keep every painted box, so the plate is the true backdrop a
  // reader sees behind the type — button fills, panel grounds and scrims included.
  let n = 0;
  document.querySelectorAll('.slide *').forEach(el => {
    let t = '';
    for (const c of el.childNodes) if (c.nodeType === 3) t += c.textContent;
    if (t.trim()) {
      el.style.setProperty('color', 'transparent', 'important');
      el.style.setProperty('text-shadow', 'none', 'important');
      if (el.ownerSVGElement) el.style.setProperty('fill', 'transparent', 'important');
      n++;
    }
  });
  document.querySelectorAll('.slide .gridover').forEach(el => el.style.visibility = 'hidden');
  return n;
})()
"""

# ---------------------------------------------------------------- rule engine
class Report:
    def __init__(self):
        self.rows = []

    def add(self, rid, sev, slide, selector, msg):
        self.rows.append({"rule": rid, "sev": sev, "slide": slide,
                          "selector": selector, "detail": msg})

    @property
    def fails(self):
        return [r for r in self.rows if r["sev"] == "FAIL"]

    @property
    def warns(self):
        return [r for r in self.rows if r["sev"] == "WARN"]


EXEMPT_MARGIN = ("media", "brandx", "mesh", "device", "bug", "gridover", "stripe", "mark", "scr", "off-grid")
EXEMPT_RESERVE = ("bug", "stripe", "mark", "gridover", "mesh", "brandx")
TEXT_TOKENS = ("t-display1", "t-display2", "t-h1", "t-h2", "t-h3", "t-label", "t-lede",
               "t-body", "t-body-s", "t-caption", "t-micro", "t-quote", "t-coversub")


def has(node, *names):
    c = " " + node["cls"] + " "
    return any((" " + n + " ") in c for n in names)


def is_exempt_margin(node):
    return has(node, *EXEMPT_MARGIN) or node["tag"] in ("img", "svg", "path", "g")


def rect_overlap(a, b):
    return not (a[2] <= b[0] or b[2] <= a[0] or a[3] <= b[1] or b[3] <= a[1])


def validate_slide(s, rep, plate=None, judge_density=True):
    i, role = s["idx"], (s["role"] or "content")
    # A documentation specimen only exists inside documentation. `data-role="spec"` drops a
    # slide out of the deck census and off several type and geometry rules, so on a deck it
    # is a one-attribute exemption with nothing behind it: label every slide `spec` and the
    # census falls under four, `validate_deck` returns early, and thirty rules stop running.
    # The claim is honoured where it is meaningful, which is in an adjudicated gallery, and
    # nowhere else. Only the spec book uses it, so this costs real work nothing. See GAL-01.
    spec = role == "spec" and bool(s.get("isGallery"))
    if role == "spec" and not spec:
        role = "content"   # not a specimen, just a slide: judge it as one, floors included
    nodes = [n for n in s["nodes"] if not n.get("inChrome")]
    text_nodes = [n for n in nodes if n["hasText"] and not has(n, "doc-anno")]

    # ---- GEO
    if abs(s["w"] - CANVAS_W) > 2 or abs(s["h"] - CANVAS_H) > 2:
        rep.add("GEO-01", "FAIL", i, ".slide", f'canvas {s["w"]:.0f} x {s["h"]:.0f}, expected 1920 x 1080')

    for n in nodes:
        if is_exempt_margin(n):
            continue
        if not (n["hasText"] or has(n, "panel", "chip", "badge", "btn")):
            continue
        b = n["box"]
        if b["x"] < 72 - 2:
            rep.add("GEO-02", "FAIL", i, n["sel"], f'left {b["x"]:.0f} < 72')
        if b["x2"] > 1848 + 2:
            rep.add("GEO-02", "FAIL", i, n["sel"], f'right {b["x2"]:.0f} > 1848')
        if n["hasText"] and b["y2"] > 1024 + 2:
            rep.add("GEO-03", "FAIL", i, n["sel"], f'bottom {b["y2"]:.0f} > 1024')

    if s["counts"]["bug"]:
        for n in nodes:
            if has(n, "panel") and not n["hasText"]:
                continue           # an empty panel is a surface the bug may sit on
            if has(n, *EXEMPT_RESERVE) or n["tag"] in ("img", "svg", "path", "g"):
                continue
            if has(n, "scrim-wash"):
                continue
            paints = (n["hasText"] or has(n, "panel", "chip", "badge", "btn", "device", "media")
                      or (parse_rgb(n["bg"]) or (0, 0, 0, 0))[3] > .02
                      or "gradient" in (n["bgImg"] or "") or "url(" in (n["bgImg"] or ""))
            if not paints:
                continue
            if has(n, "media") and (n["box"]["w"] > 1400 or n["box"]["h"] > 1000):
                continue        # bleeding photography is allowed to pass behind the mark
            b = n["box"]
            if rect_overlap((b["x"], b["y"], b["x2"], b["y2"]), RESERVE):
                rep.add("GEO-04", "FAIL", i, n["sel"],
                        f'enters bug reservation by {b["x2"]-RESERVE[0]:.0f} x {b["y2"]-RESERVE[1]:.0f}px')

    for n in nodes:
        if not has(n, "panel") or has(n, "off-grid"):
            continue
        b = n["box"]
        if min(abs(b["x"] - c) for c in COLS) > 4:
            rep.add("GEO-05", "FAIL", i, n["sel"],
                    f'left {b["x"]:.0f} is not a column edge (72 + n x 150). Mark the '
                    f'element off-grid if the source node genuinely sits off the grid')
        if min(abs(b["w"] - sp) for sp in SPANS) > 4:
            rep.add("GEO-05", "FAIL", i, n["sel"],
                    f'width {b["w"]:.0f} is not a legal span (126 + n x 150)')

    # GEO-06. Things the eye reads as a set have to bottom out together. Two cards on the
    # The 91-slide RFP deck shared a top and ended 66px apart, which reads as a mistake however
    # legal each box is on its own.
    pset = [n for n in nodes if has(n, "panel") and n.get("deepWords", 0) > 0]
    for a in range(len(pset)):
        for b2 in range(a + 1, len(pset)):
            ba, bb = pset[a]["box"], pset[b2]["box"]
            if abs(ba["y"] - bb["y"]) <= 4 and abs(ba["x"] - bb["x"]) > 40:
                d = abs(ba["y2"] - bb["y2"])
                if d > 8:
                    rep.add("GEO-06", "FAIL", i, pset[b2]["sel"],
                            f'shares a top with {pset[a]["sel"]} but its bottom is {d:.0f}px '
                            f'away. A side-by-side set bottoms out together')

    # PAT-08. Every slide does at least one act of design beyond typing. A light-ground
    # slide with no mesh, no Brand X, no triangle and no gradient surface is a page, not a
    # slide, and 39 of them shipped in the deck this rule comes from.
    # A table or a chart is the exception, because PAT-03 forbids the mesh behind data.
    if not spec and role in ("content", "data", "statement") \
            and "g-light" in (s.get("slideCls") or "").split() \
            and not has_device(s):
        forms = dominant_form(s)
        if not ({"table", "chart"} & set(forms)):
            rep.add("PAT-08", "FAIL", i, ".slide",
                    'light ground with no background device. Add the mesh placement that '
                    'matches the content position, or a gradient surface. Only a table or '
                    'a chart slide is exempt, because data may not sit on the mesh')

    panels = sorted([n for n in nodes if has(n, "panel") and not has(n, "off-grid")],
                    key=lambda n: n["box"]["x"])
    for a, b in zip(panels, panels[1:]):
        if abs(a["box"]["y"] - b["box"]["y"]) < 12:
            gap = b["box"]["x"] - a["box"]["x2"]
            if 0 < gap and abs(gap - 24) > 4:
                rep.add("GEO-06", "WARN", i, b["sel"], f'panel gap {gap:.0f}, expected 24')

    # ---- TYP
    for n in text_nodes:
        fs = round(n["fs"])
        if fs not in LADDER and fs > 8:
            rep.add("TYP-01", "FAIL", i, n["sel"], f'{fs}px is not on the ladder')
        if n["tt"] == "uppercase" and fs <= 48 and not has(n, "eyebrow"):
            rep.add("TYP-05", "FAIL", i, n["sel"], f'uppercase at {fs}px')
        if has(n, "t-body", "t-body-s", "t-lede") and n["box"]["w"] > 1026 + 4 and not spec:
            rep.add("TYP-08", "WARN", i, n["sel"], f'measure {n["box"]["w"]:.0f} > 1026 (7 col)')
        serif = "serif" in n["ff"].lower() and "sans" not in n["ff"].lower()
        if serif and not has(n, "t-quote"):
            rep.add("TYP-07", "FAIL", i, n["sel"], f'serif outside .t-quote ({n["ff"][:40]})')

    heads = [n for n in nodes if has(n, "t-display1", "t-display2", "t-h1", "t-h1-lg", "t-h2")]
    hero_stats = [n for n in nodes if (has(n, "val", "stat-hero") and n["fs"] >= 96)
                  or (n["hasText"] and n["fs"] >= 128 and not has(n, "qmark"))]
    entry = len(heads) + (1 if (not heads and hero_stats) else 0)
    if not spec:
        if entry != 1:
            rep.add("TYP-02", "FAIL", i, ".slide",
                    f'{len(heads)} headlines and {len(hero_stats)} hero stats; a slide needs exactly one entry point')
    for n in heads:
        lh = n["lh"] or n["fs"] * 1.2
        lines = round(n["box"]["h"] / lh) if lh else 0
        # Three lines is the cap for a display headline: uppercase, short, one thought.
        # The sentence-case statement setting is a different object. Node 1839:55 runs
        # seven lines of it inside a 631 measure on purpose, and the constraint there is
        # that the block fits its panel, not that it fits three lines. Capping it at 3
        # would have meant either rewriting the source's sentence or setting it smaller
        # than the source, so the rule gets the exception rather than the slide.
        if has(n, "t-h1--stmt"):
            if n["box"]["h"] > 720:
                rep.add("TYP-03", "FAIL", i, n["sel"],
                        f'statement block {n["box"]["h"]:.0f}px tall; 720 is the ceiling '
                        f'(nine lines at 80px) before it stops reading as one statement')
        elif lines > 3:
            rep.add("TYP-03", "FAIL", i, n["sel"], f'{lines} lines')
        # TYP-04 used to read BOX width, which is not the measure. A centred headline sits
        # in a wide box holding narrow text, so recipes 12 and 14 tripped it while being
        # correct, and promoting it to FAIL would have broken our own work. It reads the
        # rendered text extent now, and the cap depends on the alignment: a left-aligned
        # headline is a measure and holds to 8 columns, a centred one is a display line
        # and holds to the content width.
        if not spec and not has(n, "t-display1", "t-display2"):
            lr = n.get("lineRects") or []
            widest = max((r[1] - r[0] for r in lr), default=n["box"]["w"])
            cap = 1776 if n.get("align") == "center" else 1176
            if widest > cap + 4:
                rep.add("TYP-04", "FAIL", i, n["sel"],
                        f'headline text runs {widest:.0f}px against a cap of {cap} '
                        f'({"centred, content width" if cap == 1776 else "left-aligned, 8 columns"})')

        # TYP-11. A centred headline centres on the canvas axis, 960, because the content
        # area runs 72 to 1848 and is symmetric about it. Ten slides of the 91-slide RFP deck
        # centred on 888 instead, which is what you get from a 1776 box placed at left:0.
        # Seventy pixels off centre reads as broken, not as centred.
        if not spec and n.get("align") == "center" and not has(n, "off-grid"):
            ctr = n["box"]["x"] + n["box"]["w"] / 2.0
            if abs(ctr - 960) > 20:
                rep.add("TYP-11", "FAIL", i, n["sel"],
                        f'centred headline centres on {ctr:.0f}, {ctr-960:+.0f} off the canvas '
                        f'axis of 960. A 1776 box belongs at left:72, not left:0. Mark it '
                        f'off-grid only if the source node genuinely sits off axis')
        if has(n, "t-display1", "t-display2") and n["scrollW"] > n["clientW"] + 2:
            rep.add("TYP-06", "FAIL", i, n["sel"],
                    f'display line overflows by {n["scrollW"]-n["clientW"]}px')

    # ---- GEO-07 occlusion: nothing opaque may be painted over live type
    painted = [n for n in nodes
               if (has(n, "panel", "media", "device", "badge", "chip", "btn")
                   or (parse_rgb(n["bg"]) or (0, 0, 0, 0))[3] > .85
                   or "url(" in (n["bgImg"] or ""))
               and not has(n, "scrim-wash", "mesh", "brandx", "stripe")]
    for t in text_nodes:
        tb = (t["box"]["x"], t["box"]["y"], t["box"]["x2"], t["box"]["y2"])
        for pnl in painted:
            if pnl is t:
                continue
            # the type is inside this box, so the box is its container, not its lid
            if pnl["di"] <= t["di"] <= pnl["subtreeEnd"]:
                continue
            # paint order: z-index first, then document order
            above = (pnl["z"], pnl["di"]) > (t["z"], t["di"])
            if not above:
                continue
            pb = (pnl["box"]["x"], pnl["box"]["y"], pnl["box"]["x2"], pnl["box"]["y2"])
            if not rect_overlap(tb, pb):
                continue
            # a container that wraps the text is not covering it
            if pb[0] <= tb[0] + 1 and pb[1] <= tb[1] + 1 and pb[2] >= tb[2] - 1 and pb[3] >= tb[3] - 1:
                continue
            ov = ((min(tb[2], pb[2]) - max(tb[0], pb[0])) *
                  (min(tb[3], pb[3]) - max(tb[1], pb[1])))
            frac = ov / max(1.0, (tb[2] - tb[0]) * (tb[3] - tb[1]))
            if frac > 0.06:
                rep.add("GEO-07", "FAIL", i, t["sel"],
                        f'{frac:.0%} of "{t["text"][:24]}" is covered by {pnl["sel"]}')
                break

    # ---- TYP-10 no single word left alone on the last line of a text block. A widow reads as a
    # mistake at slide scale, and it is always fixable: bind the last two words with a non-breaking
    # space, or widen the measure by one column.
    WIDOW_SKIP = ("em", "b", "i", "strong", "span", "td", "th", "a")
    for n in text_nodes:
        w = n.get("widow")
        # display headlines are hand-broken by rule, so a short final line there is deliberate
        if not w or n["tag"] in WIDOW_SKIP or has(n, "t-display1", "t-display2"):
            continue
        if n["fs"] >= 20 and n["box"]["w"] > 120:
            rep.add("TYP-10", "FAIL", i, n["sel"],
                    f'"{w}" is alone on the last line of "{n["text"][:26]}"')

    # ---- TYP-09 two live text blocks may not overlap each other. GEO-07 only catches an opaque
    # box painted over type; two absolutely positioned paragraphs colliding is invisible to it,
    # and is what happens when a headline wraps one line further than it did in the design font.
    tn = [n for n in text_nodes if n["box"]["w"] > 8 and n["box"]["h"] > 8]
    for a_i in range(len(tn)):
        for b_i in range(a_i + 1, len(tn)):
            a, c = tn[a_i], tn[b_i]
            if a["di"] <= c["di"] <= a["subtreeEnd"] or c["di"] <= a["di"] <= c["subtreeEnd"]:
                continue          # one contains the other
            ab = (a["box"]["x"], a["box"]["y"], a["box"]["x2"], a["box"]["y2"])
            cb = (c["box"]["x"], c["box"]["y"], c["box"]["x2"], c["box"]["y2"])
            if not rect_overlap(ab, cb):
                continue
            ov = ((min(ab[2], cb[2]) - max(ab[0], cb[0])) * (min(ab[3], cb[3]) - max(ab[1], cb[1])))
            small = min((ab[2]-ab[0])*(ab[3]-ab[1]), (cb[2]-cb[0])*(cb[3]-cb[1]))
            if ov / max(1.0, small) > 0.12:
                rep.add("TYP-09", "FAIL", i, a["sel"],
                        f'"{a["text"][:22]}" collides with "{c["text"][:22]}" over {ov/small:.0%} of its box')

    # ---- COL
    for n in nodes:
        c = parse_rgb(n["color"])
        if n["hasText"] and c and not near_token(c):
            rep.add("COL-01", "FAIL", i, n["sel"], f'text colour {hexof(c)} is not a token')
        bg = parse_rgb(n["bg"])
        if bg and bg[3] > 0.02 and not near_token(bg):
            rep.add("COL-01", "FAIL", i, n["sel"], f'background {hexof(bg)} is not a token')
        if n["hasText"] and c and abs(c[0] - 238) < 8 and abs(c[1] - 40) < 10 and abs(c[2] - 42) < 10:
            if not has(n, "dir"):
                rep.add("COL-02", "FAIL", i, n["sel"], "red used as type")
        if bg and bg[3] > .5 and abs(bg[0] - 238) < 8 and abs(bg[1] - 40) < 10 and abs(bg[2] - 42) < 10:
            rep.add("COL-02", "FAIL", i, n["sel"], "red used as a fill")
        if bg and bg[3] > .5 and abs(bg[0] - 51) < 6 and abs(bg[1] - 0) < 6 and abs(bg[2] - 114) < 6:
            if "gradient" not in (n["bgImg"] or ""):
                rep.add("COL-03", "FAIL", i, n["sel"], "purple used as a flat fill")

    grads = [n for n in nodes
             if "gradient" in (n["bgImg"] or "")
             and not has(n, "badge", "stripe", "rule-h--brand", "mesh", "brandx", "scrim-wash")
             and n["tag"] != "th" and n["box"]["w"] * n["box"]["h"] > 40000]
    if not spec and len(grads) > 1:
        rep.add("COL-05", "WARN", i, ".slide", f'{len(grads)} gradient surfaces, expected 1')
    reds = s["counts"]["arrow"] - s["counts"]["arrowLink"] + s["counts"]["dir"]
    if not spec and reds > 1:
        rep.add("COL-06", "WARN", i, ".slide", f'{reds} red marks, expected at most 1')

    # COL-07. The relationship, not the colours. Panels are #FFFFFF on the #F6F6F6 surface
    # with --shadow-panel lifting them off it. The 91-slide RFP deck inverted that on 52
    # slides: white ground, #F6F6F6 cards, no shadow, so every panel read as a recessed
    # well. COL-01 passed it because both colours are tokens.
    if not spec and "g-white" in (s.get("slideCls") or "").split():
        if role in ("content", "data"):
            forms = dominant_form(s)
            if not ({"table", "chart"} & set(forms)):
                rep.add("COL-07", "FAIL", i, ".slide",
                        'g-white on a content slide. The deck ground is #F6F6F6; no recipe '
                        'uses g-white, and it carried 57% of the deck that prompted this rule')
        if any(has(n, "panel") for n in nodes):
            rep.add("COL-07", "FAIL", i, ".slide",
                    'a panel on a white ground. Panels are #FFFFFF raised off #F6F6F6; '
                    'inverted they read as holes in the page')

    # COL-08. A brand-gradient device on a brand-gradient surface is invisible and says
    # nothing. The test deck put .rule-h--brand, a 240 x 6 gradient rule, inside a gradient
    # (that class was retired from the system at v4.8, but the references to it in this file
    # stay: a deck built before the removal still carries it, and this rule still has to
    # catch it there. lint_source.py fails any NEW reference via RETIRED.)
    # panel. It is a real system component used where it cannot read.
    if not spec:
        for n in nodes:
            # The bug is exempt: its stripe is a gradient and it sits over whatever the
            # corner happens to hold, which is the point of a corner mark.
            if has(n, "bug", "stripe", "mark", "lockup", "brandx", "brandx-x", "tri", "mesh"):
                continue
            if not has(n, "rule-h--brand") and "linear-gradient" not in (n.get("bgImg") or ""):
                continue
            if n["box"]["w"] * n["box"]["h"] > 0.04 * CANVAS_W * CANVAS_H:
                continue                      # a surface, not a device on one
            for m in nodes:
                if m is n or m["di"] >= n["di"]:
                    continue
                # A clipped wedge reports a full-canvas bounding box while painting a
                # triangle, so it cannot stand in for "the surface underneath". This was a
                # false positive on recipe 11, where the rule and the wedge never touch.
                if has(m, "brandx", "brandx-x", "tri"):
                    continue
                mbg = m.get("bgImg") or ""
                if "linear-gradient" not in mbg:
                    continue
                # It has to be a BRAND gradient. A black or white scrim is a legitimate
                # ground for the brand rule, and matching any gradient failed the closing
                # slide of my own deck, where the rule sits correctly on a dark wash.
                if not any(t in mbg for t in ("0, 134, 234", "51, 0, 114",
                                              "29, 86, 158", "40, 17, 92")):
                    continue
                if m["box"]["w"] * m["box"]["h"] < 0.04 * CANVAS_W * CANVAS_H:
                    continue
                mb = (m["box"]["x"], m["box"]["y"], m["box"]["x2"], m["box"]["y2"])
                nb = (n["box"]["x"], n["box"]["y"], n["box"]["x2"], n["box"]["y2"])
                if rect_overlap(nb, mb):
                    rep.add("COL-08", "FAIL", i, n["sel"],
                            f'a brand-gradient device sitting on {m["sel"]}, which is also a '
                            f'brand gradient. It cannot read against its own ground. The '
                            f'brand rule belongs on a light or photographic surface')
                    break

    # ---- COL-04 / IMG-04 contrast, measured off the backdrop plate
    if plate is not None:
        import numpy as np
        img, ox, oy, scale = plate
        scrimmed = any(has(m, "scrim-flat", "scrim-grad", "scrim-r") for m in nodes) or any(
            "gradient" in (m["bgImg"] or "") and m["box"]["w"] > 1500 and m["box"]["h"] > 900
            for m in nodes)
        for n in text_nodes:
            c = parse_rgb(n["color"])
            if not c:
                continue
            b = n["box"]
            # Inset the sample so the element's own border, inset shadow or chip edge
            # is not mistaken for the backdrop behind its type.
            ix = max(3.0, b["w"] * 0.12); iy = max(3.0, b["h"] * 0.12)
            x0 = int(((b["x"] + ix) * scale) + ox); y0 = int(((b["y"] + iy) * scale) + oy)
            x1 = int(((b["x2"] - ix) * scale) + ox); y1 = int(((b["y2"] - iy) * scale) + oy)
            x0, y0 = max(0, x0), max(0, y0)
            x1, y1 = min(img.shape[1], x1), min(img.shape[0], y1)
            if x1 - x0 < 3 or y1 - y0 < 3:
                continue
            # float32 on the PATCH, because the plate is uint8 now and _lin divides in
            # place, which would truncate on an integer type.
            patch = img[y0:y1, x0:x1].reshape(-1, 3).astype(np.float32)
            L = np.array([lum(p) for p in patch[:: max(1, len(patch) // 900)]])
            if L.size == 0:
                continue
            tl = lum(c)
            # worst case: lightest backdrop for light type, darkest for dark type
            worst = np.percentile(L, 90) if tl > 0.4 else np.percentile(L, 10)
            ratio = contrast(tl, worst)
            need = 3.0 if (n["fs"] >= 24 or (n["fs"] >= 18.66 and int(n["fs"]) and n["fw"] in ("700", "800", "900", "bold"))) else 4.5
            over_media = any(has(m, "media") and rect_overlap(
                (b["x"], b["y"], b["x2"], b["y2"]),
                (m["box"]["x"], m["box"]["y"], m["box"]["x2"], m["box"]["y2"])) for m in nodes)
            rid = "IMG-04" if over_media else "COL-04"
            if ratio < need - 0.02:
                rep.add(rid, "FAIL", i, n["sel"],
                        f'{ratio:.2f}:1 needs {need:.1f}:1 — "{n["text"][:34]}"')
                # IMG-03 is the actionable form of the same failure: there is no scrim to fix.
                if over_media and not scrimmed:
                    rep.add("IMG-03", "FAIL", i, n["sel"],
                            "type over unscrimmed media — add a scrim or move the type")

    # ---- MRK
    nb, nl = s["counts"]["bug"], s["counts"]["lockup"]
    if nb and nl:
        rep.add("MRK-02", "FAIL", i, ".slide", "both bug and lockup present")
    if not spec:
        if role in LOCKUP_ROLES:
            if nl != 1:
                rep.add("MRK-01", "FAIL", i, ".slide", f'{role} needs exactly 1 lockup, found {nl}')
        elif nb != 1:
            rep.add("MRK-01", "FAIL", i, ".slide", f'interior slide needs exactly 1 bug, found {nb}')

    for n in nodes:
        if has(n, "bug"):
            b = n["box"]
            if abs(b["w"] - 275) > 2 or abs(b["h"] - 286) > 2:
                rep.add("MRK-03", "FAIL", i, ".bug", f'unit {b["w"]:.0f} x {b["h"]:.0f}, expected 275 x 286')
            if abs(b["x"] - 1754) > 2:
                rep.add("MRK-03", "FAIL", i, ".bug", f'left edge {b["x"]:.0f}, expected 1754 (bleeds 109 off the right)')
            if abs((1080 - b["y2"]) - 20) > 2:
                rep.add("MRK-03", "FAIL", i, ".bug", f'bottom offset {1080-b["y2"]:.0f}, expected 20')
        if has(n, "mark") and n["tag"] == "div":
            p = [m for m in nodes if has(m, "bug")]
            if p:
                lx = n["box"]["x"] - p[0]["box"]["x"]; ly = n["box"]["y"] - p[0]["box"]["y"]
                cx, cy = lx + n["box"]["w"] / 2, ly + n["box"]["h"] / 2
                if abs(n["box"]["w"] - 73) > 2 or abs(n["box"]["h"] - 38) > 2:
                    rep.add("MRK-03", "FAIL", i, ".bug .mark",
                            f'mark {n["box"]["w"]:.0f} x {n["box"]["h"]:.0f}, expected 73 x 38')
                if abs(n["box"]["x"] - 1810) > 2 or abs(n["box"]["y"] - 1013) > 2:
                    rep.add("MRK-03", "FAIL", i, ".bug .mark",
                            f'mark at {n["box"]["x"]:.0f}, {n["box"]["y"]:.0f}, expected 1810, 1013')
                # the mark must land on the band centreline: 286x + 275y between the two edges
                v = 286 * cx + 275 * cy
                frac = (v - 78650) / 39611.0
                if not (0.40 <= frac <= 0.60):
                    rep.add("MRK-03", "FAIL", i, ".bug .mark",
                            f'mark sits {frac:.0%} across the stripe, expected 50% ± 10')
        if has(n, "lockup"):
            b = n["box"]
            if abs(b["w"] - 210) > 2 or abs(b["h"] - 44) > 2:
                rep.add("MRK-04", "FAIL", i, ".lockup", f'{b["w"]:.0f} x {b["h"]:.0f}, expected 210 x 44')
            if abs(b["x"] - 44) > 2 or abs(b["y"] - 52) > 2:
                rep.add("MRK-04", "FAIL", i, ".lockup", f'at {b["x"]:.0f}, {b["y"]:.0f}, expected 44, 52')

    # MRK-05. The bug variant is chosen by what is ACTUALLY BEHIND IT, measured off the
    # rendered plate, not inferred from the slide's ground class. The test deck used
    # .bug--dark on five light slides, where its white mark vanishes, and the plain .bug on
    # a dark photograph, where its near-white stripe shouts. Two of the six defects reported
    # on that deck were this one rule in opposite directions.
    # A first cut read the g- class and failed recipe 10, whose light ground carries the
    # brand wedge across the bottom-right corner, so the bug genuinely sits on dark purple.
    # Inferring the backdrop from a class is the same mistake as inferring contrast from CSS.
    if not spec and plate is not None:
        import numpy as np
        img, ox, oy, scale = plate
        for n in nodes:
            if not has(n, "bug"):
                continue
            # Sample the strip immediately LEFT of the bug, same vertical band. The bug is
            # painted on top of the plate, so its own box shows the bug rather than the
            # backdrop; the adjacent strip shares whatever ground it sits on.
            x0 = int((1560 * scale) + ox); x1 = int((1740 * scale) + ox)
            y0 = int((860 * scale) + oy);  y1 = int((1050 * scale) + oy)
            x0, y0 = max(0, x0), max(0, y0)
            x1, y1 = min(img.shape[1], x1), min(img.shape[0], y1)
            if x1 - x0 < 4 or y1 - y0 < 4:
                break
            patch = img[y0:y1, x0:x1].reshape(-1, 3).astype(np.float32)
            L = np.array([lum(p) for p in patch[:: max(1, len(patch) // 600)]])
            if L.size == 0:
                break
            med = float(np.median(L))
            is_dark_variant = has(n, "bug--dark")
            if med > BUG_LIGHT_L and is_dark_variant:
                rep.add("MRK-05", "FAIL", i, n["sel"],
                        f'bug--dark on a light backdrop (measured L {med:.2f}). Its mark is '
                        f'white and its stripe is a white wash, so both disappear. Use the '
                        f'plain .bug here')
            elif med < BUG_DARK_L and not is_dark_variant:
                rep.add("MRK-05", "FAIL", i, n["sel"],
                        f'the light .bug on a dark backdrop (measured L {med:.2f}). Its '
                        f'stripe is a near-white plate and it shouts. Use .bug--dark')
            break

    # ---- PAT
    if s["counts"]["mesh"] and s["counts"]["brandx"]:
        rep.add("PAT-01", "FAIL", i, ".slide", "mesh and brandx on the same slide")
    if s["counts"].get("brandxOld"):
        rep.add("PAT-06", "FAIL", i, ".brandx",
                f'{s["counts"]["brandxOld"]} element(s) using the retired two-div Brand X. '
                f'Its geometry rules were deleted at v3.2, so it renders nothing at all. '
                f'Use .brandx-x for cover and divider; .brandx.brandx--r10 is the '
                f'only surviving clip-path instance')
    if s["counts"].get("brandxDead"):
        rep.add("PAT-06", "FAIL", i, ".brandx-x",
                f'{s["counts"]["brandxDead"]} Brand X element(s) render 0 x 0. The class is '
                f'present but the stylesheet gives it no geometry, so the slide has no X and '
                f'nothing else complains')
    for n in nodes:
        if has(n, "mesh"):
            if abs(n["op"] - 0.11) > 0.005:
                rep.add("PAT-02", "FAIL", i, ".mesh", f'opacity {n["op"]}, expected 0.11')
            if n["blend"] != "plus-lighter":
                rep.add("PAT-02", "FAIL", i, ".mesh", f'blend {n["blend"]}, expected plus-lighter')
            # 2384 x 1080 is the dark ground's placement, node 1892:34, bleeding both sides
            MESH_BOX = {(1205, 1080), (1182, 1080), (1920, 1080), (1192, 1068),
                        (2384, 1080)}
            if not any(abs(n["box"]["w"] - w) <= 2 and abs(n["box"]["h"] - h) <= 2
                       for w, h in MESH_BOX):
                rep.add("PAT-02", "FAIL", i, ".mesh",
                        f'{n["box"]["w"]:.0f} x {n["box"]["h"]:.0f} is not a placement '
                        f'(1205/1182/1920 x 1080, or 1192 x 1068 pushed right)')
            # PAT-05. The mesh is ground, not decoration inside a thing. It has to be a
            # direct child of .slide. Nested in a .panel, a .card or a .media it inherits
            # that box's bounds and its blend mode composites against the panel fill
            # instead of the page surface, so the lattice reads as a texture swatch. It
            # also cannot be baked: the PPTX path blends the mesh into ONE ground plate
            # (REG-17), so a mesh inside a container is silently dropped on export.
            if n["depth"] != 1:
                rep.add("PAT-05", "FAIL", i, ".mesh",
                        f'nested inside {n["parentSel"]} at depth {n["depth"]}. '
                        f'The mesh is background only and must be a direct child of .slide')
            # a left-justified asset must actually be left-justified, or its terminus shows
            if has(n, "mesh--diag") and abs(n["box"]["x"]) > 2:
                rep.add("PAT-04", "FAIL", i, ".mesh--diag",
                        f'left-justified asset placed at x {n["box"]["x"]:.0f}; it must sit at x 0')
            mb = (n["box"]["x"], n["box"]["y"], n["box"]["x2"], n["box"]["y2"])
            for d in nodes:
                if d["tag"] == "table" or (d["tag"] == "svg" and d["box"]["w"] > 400):
                    db = (d["box"]["x"], d["box"]["y"], d["box"]["x2"], d["box"]["y2"])
                    if rect_overlap(db, mb):
                        rep.add("PAT-03", "FAIL", i, d["sel"], "data sits on the mesh")

    # PAT-05, second half. The class is not the only way in. Painting the lattice art
    # straight onto a panel with background-image bypasses .mesh entirely and every
    # check above it, which is how testers ended up with the pattern inside content
    # boxes. Match on the art itself, not on the class.
    art = set(s.get("meshArt") or [])
    if art:
        for n in nodes:
            if has(n, "mesh") or not n["bgImg"] or n["bgImg"] == "none":
                continue
            if any(a in n["bgImg"] or n["bgImg"] in a for a in art):
                rep.add("PAT-05", "FAIL", i, n["sel"],
                        "mesh art used as a background-image on something that is not "
                        "the page ground. Background only; use .mesh on the .slide")

    # GEO-08. Text inside a panel has to be inset from its edge. The system's .panel had no
    # default padding and only twelve of twenty-three panels in the recipes set one inline,
    # so a builder copying the wrong recipe got a label flush against the corner and nothing
    # objected. Now .panel carries a default and this catches anyone who overrides it to 0.
    if not spec:
        for n in nodes:
            ins = n.get("panelInset")
            if not ins or not n["hasText"]:
                continue
            m = min(ins["l"], ins["t"])
            if m < PANEL_MIN_INSET:
                rep.add("GEO-08", "FAIL", i, n["sel"],
                        f'text is {m}px from the panel edge, effectively flush. A panel with '
                        f'its padding overridden to 0 puts the label in the corner')
            elif m < PANEL_TIGHT_INSET:
                rep.add("GEO-08", "WARN", i, n["sel"],
                        f'text inset {m}px from the panel edge; {PANEL_TIGHT_INSET} is the '
                        f'comfortable minimum. Deliberate on a dense card, worth a look otherwise')

    # DEN-09. A panel can be 43% empty on a slide that meets its coverage target, which is
    # exactly what happened: a 1112 x 787 gradient panel whose content stopped at 445px, so
    # 342px of it was dead. Slide-level density cannot see inside a box.
    if not spec and not s.get("isGallery"):
        for n in nodes:
            if not has(n, "panel") or n.get("deepWords", 0) < 3:
                continue
            pb = n["box"]
            if pb["h"] < 240:
                continue                      # a band or a tab, not a content box
            low = 0.0
            for m in nodes:
                if m is n or m["di"] <= n["di"] or m["di"] > n["subtreeEnd"]:
                    continue
                if m["hasText"] or m["tag"] == "img" or has(m, "chip", "badge", "stat"):
                    low = max(low, m["box"]["y2"] - pb["y"])
            if low <= 0:
                continue
            empty = (pb["h"] - low) / pb["h"]
            if empty > PANEL_MAX_EMPTY:
                rep.add("DEN-09", "FAIL", i, n["sel"],
                        f'{empty:.0%} of this {pb["w"]:.0f} x {pb["h"]:.0f} panel is empty '
                        f'below its last content ({pb["h"]-low:.0f}px). Shorten the panel or '
                        f'give it something to hold; a slide can hit its coverage target with '
                        f'a dead box inside it')

    # ---- DEN
    for cnt in s["counts"]["tableRows"]:
        if cnt > 6:
            rep.add("DEN-03", "FAIL", i, "table.deck", f'{cnt} rows, maximum 6')
    for h in s["counts"]["rowHeights"]:
        if h < 56 - 2:
            rep.add("DEN-05", "WARN", i, "table.deck tr", f'row height {h:.0f} < 56')
    for cnt in s["counts"]["bulletCounts"]:
        if cnt > 5:
            rep.add("DEN-04", "FAIL", i, "ul.b", f'{cnt} bullets, maximum 5')

    if judge_density and not spec and role in INK_BAND:
        # union coverage on a 192 x 108 grid — overlapping boxes are counted once
        GW, GH = 192, 108
        grid = bytearray(GW * GH)
        for n in nodes:
            if has(n, "gridover", "stripe", "mark", "mesh", "brandx", "scrim-wash") or n["tag"] in ("path", "g", "br"):
                continue
            # photography that touches two or more canvas edges is the ground, not ink
            if has(n, "media"):
                b = n["box"]
                edges = ((b["x"] <= 2) + (b["y"] <= 2)
                         + (b["x2"] >= CANVAS_W - 2) + (b["y2"] >= CANVAS_H - 2))
                if edges >= 2:
                    continue
            # AN EMPTY PANEL IS GROUND. Crediting a painted box regardless of whether it
            # holds anything made the cheapest way to pass a density floor one enormous
            # grey rectangle. A panel earns its area by carrying words or a picture.
            carries = (n["hasText"] or n.get("deepWords", 0) > 0
                       or n.get("deepImgs", 0) > 0 or n["tag"] == "img")
            if has(n, "panel") and not carries:
                continue
            if not (n["hasText"] or has(n, "panel", "media", "device", "badge", "chip")
                    or n["tag"] == "table"):
                continue
            gx0 = max(0, int(n["box"]["x"] / CANVAS_W * GW)); gx1 = min(GW, int(math.ceil(n["box"]["x2"] / CANVAS_W * GW)))
            gy0 = max(0, int(n["box"]["y"] / CANVAS_H * GH)); gy1 = min(GH, int(math.ceil(n["box"]["y2"] / CANVAS_H * GH)))
            for gy in range(gy0, gy1):
                base = gy * GW
                for gx in range(gx0, gx1):
                    grid[base + gx] = 1
        ink = sum(grid) / float(GW * GH)
        INK[i] = ink
        lo, hi, floor = INK_BAND[role]
        if ink > floor:
            rep.add("DEN-01", "WARN", i, ".slide", f'ink {ink:.0%} over the {role} floor of {floor:.0%}')

        # DEN-06. The band was read in one direction only: the code computed lo, hi and
        # floor and then tested `ink > floor`. A deck averaging 8% coverage passed in
        # silence, which is how 52 near-empty slides shipped to a client. Empty is a
        # defect in the same way overfull is, and it is the more common one.
        gallery = bool(s.get("isGallery"))
        f_cov, w_cov, f_atoms, f_words = SUBSTANCE.get(role, SUBSTANCE["content"])
        if gallery:
            pass          # a specimen shows a layout; content volume is not its job
        elif ink < f_cov:
            rep.add("DEN-06", "FAIL", i, ".slide",
                    f'coverage {ink:.0%} under the {role} floor of {f_cov:.0%}. '
                    f'The slide is empty, and an empty panel does not count')
        elif ink < w_cov:
            rep.add("DEN-06", "WARN", i, ".slide",
                    f'coverage {ink:.0%} is thin for {role} (target {w_cov:.0%})')

        # DEN-07. Coverage alone can be bought with structure, so substance is measured
        # separately: content atoms a reader actually reads, and total words. A wall of
        # empty cards scores on neither.
        atoms, words = substance(s)
        # Both measures thin, not either. A table slide is many atoms and few words, a
        # prose slide is few atoms and many words, and both are legitimate; only a slide
        # that is thin on BOTH counts has nothing on it. Testing either way round failed a
        # correct three-row table for having terse cells, which is what a table cell is.
        w_floor = f_words
        big_photo = qualifying_photo(s) >= 0.30   # a slide genuinely led by an image
        if big_photo:
            # A photograph across a fifth of the canvas is doing communicative work, so the
            # word floor eases. This also keeps DEN-07 from pushing people away from
            # photography while IMG-05 pushes them toward it.
            w_floor = int(f_words * 0.6)
        if not gallery and atoms < f_atoms and words < w_floor:
            rep.add("DEN-07", "FAIL", i, ".slide",
                    f'{atoms} content atoms and {words} words, both under the {role} floor of '
                    f'{f_atoms} and {w_floor}{" (eased for photography)" if big_photo else ""}. '
                    f'Cut the slide or give it something to say')
        elif not gallery and role in ("content", "data") and words < 10:
            rep.add("DEN-07", "FAIL", i, ".slide",
                    f'{words} words on a {role} slide. There is nothing here to read')

    # DEN-08. Placeholder copy. One slide of the 91-slide RFP deck went to a client with
    # "Lorem ipsum" as its only body text, and every rule in the system passed it.
    for n in nodes:
        t = (n.get("text") or "").strip().lower()
        if t and any(p in t for p in PLACEHOLDER):
            rep.add("DEN-08", "FAIL", i, n["sel"], f'placeholder copy: "{n["text"][:40]}"')

    # ---- SYS. Deck-local components.
    # THE DEEPEST FINDING FROM THE FDU TEST DECK. The builder invented ten classes, six of
    # which duplicated a component the system already ships:
    #   .badge-num -> .badge     .pill      -> .chip       .case-card -> .panel
    #   .phase-col -> .medallion .panel-h   -> .t-label    .compare-tag -> .t-body-s
    # Every one of them looked right in the browser. The consequences all landed elsewhere:
    # the badges lost their gradient on export and became white boxes, the timeline's
    # circles never existed because .phase-col has no ring, .svc-col's bullet dots were
    # ::before pseudo-elements that cannot export, and three invented type roles at 28, 22
    # and 20 are why the body size wandered across four steps.
    # Nothing objected, because every rule asked "is this element correct" and none asked
    # "is this element the one the system already has".
    if not spec and SYSTEM_CLASSES:
        for n in nodes:
            cl = [c for c in (n.get("cls") or "").split() if c]
            local = [c for c in cl if c not in SYSTEM_CLASSES]
            if not local:
                continue
            bad = n.get("unexportable") or []
            if bad:
                rep.add("SYS-02", "FAIL", i, n["sel"],
                        f'deck-local class .{local[0]} uses {", ".join(bad)}, which the PPTX '
                        f'path cannot express. It will look right in the browser and degrade '
                        f'silently on export. Use a system component, or bake it like the '
                        f'mesh and the bug are baked')
            # A deck MAY add a component when it has a job no existing component does. It
            # declares itself with data-component, the same way an off-grid element declares
            # its exception. My own GTM deck's .prac and .secrail are exactly this case, and
            # an undeclared escape hatch would have meant silently loosening the rule.
            near = nearest_component(n) if not n.get("declared") else None
            if near:
                rep.add("SYS-01", "FAIL", i, n["sel"],
                        f'deck-local class .{local[0]} duplicates .{near[0]}, which the system '
                        f'already ships ({near[1]}). Use it. A near-copy under a new name is '
                        f'invisible to the exporter and to every rule keyed on the real class')

    # ---- A11
    for n in nodes:
        if n["tag"] == "img":
            if n["alt"] is None:
                rep.add("A11-01", "FAIL", i, n["sel"], "img has no alt attribute")
            elif n["alt"] == "" and n["ariaHidden"] != "true" and not has(n, "mark") \
                    and n["parentSel"] and "lockup" not in n["parentSel"]:
                rep.add("A11-01", "WARN", i, n["sel"], 'alt="" without aria-hidden')
        if n["tag"] == "svg" and n["box"]["w"] > 400:
            if n["role"] != "img" or not n["ariaLabel"]:
                rep.add("A11-02", "FAIL", i, n["sel"], 'chart svg needs role="img" and aria-label')
    if s["counts"]["tables"] or any(n["tag"] == "svg" and n["box"]["w"] > 400 for n in nodes):
        if not any(has(n, "t-caption", "t-source") and n["hasText"] for n in s["nodes"]):
            rep.add("A11-03", "WARN", i, ".slide", "data slide with no source caption")

    order = [n for n in text_nodes if n["fs"] >= 20 and not has(n, "rail", "eyebrow")
             and n["parentSel"] and "rail" not in (n["parentSel"] or "")]
    visual = sorted(range(len(order)), key=lambda j: (round(order[j]["box"]["y"] / 40), order[j]["box"]["x"]))
    if visual != sorted(range(len(order))) and len(order) > 2 and not spec:
        bad = sum(1 for a, b in zip(visual, sorted(range(len(order)))) if a != b)
        seq = " > ".join((order[j]["text"][:16] or order[j]["sel"]) for j in visual[:6])
        rep.add("A11-04", "WARN", i, ".slide",
                f'{bad} of {len(order)} text nodes out of reading order; visual sequence is: {seq}')

    # ---- IMG
    for n in nodes:
        if has(n, "media") and n["box"]["h"] > 4:
            ar = n["box"]["w"] / n["box"]["h"]
            CROPS = (1.78, 4.06, 1.02, 3.95, 3.46, 2.02, 2.33, 7.27, 1.50)
            if min(abs(ar / t - 1) for t in CROPS) > 0.03:
                rep.add("IMG-02", "WARN", i, n["sel"],
                        f'crop ratio {ar:.2f} is not one of the nine')


# ---------------------------------------------------------------- driver
def run(path, roles=None, only=None, quiet=False, json_out=None, shots=False):
    from playwright.sync_api import sync_playwright
    from browser import launch
    from PIL import Image
    import numpy as np

    roles = roles or {}
    rep = Report()
    url = path if path.startswith("http") else "file://" + os.path.abspath(path)

    with sync_playwright() as p:
        b = launch(p, args=["--no-sandbox"])
        pg = b.new_page(viewport={"width": 1600, "height": 1100})
        pg.goto(url, wait_until="load", timeout=120000)
        pg.wait_for_timeout(3500)
        try:
            pg.evaluate("document.fonts.ready")
        except Exception:
            pass

        # Measure at native canvas resolution. Stages in the source may be scaled down
        # (a spec book renders several per row), and a plate sampled at a third scale is
        # too coarse for contrast: edge blending with neighbouring rows swamps the reading.
        pg.evaluate("""() => {
          document.querySelectorAll('.stage').forEach(s => {
            s.style.setProperty('width', '1920px', 'important');
            s.style.setProperty('max-width', 'none', 'important');
            s.style.setProperty('--k', '1');
          });
        }""")
        pg.wait_for_timeout(600)

        slides = pg.evaluate(PROBE)
        for s in slides:
            if s["role"] is None:
                s["role"] = roles.get(str(s["idx"]))

        # backdrop plate: hide every text carrier, screenshot each slide, sample behind the type
        pg.evaluate(HIDE_TEXT)
        pg.wait_for_timeout(400)
        els = pg.query_selector_all(".slide")
        plates = {}
        for s in slides:
            try:
                png = els[s["idx"]].screenshot(type="png")
            except Exception:
                continue
            import io
            # uint8, NOT float64. A 1920 x 1080 float64 plate is 50 MB, and this dict holds
            # one per slide until every rule has run, so a 55-slide deck asked the kernel
            # for 2.7 GB and was killed. No traceback, no exit message, just a dead process
            # that looks like a hang: one client deck was never validated once, and
            # nobody knew. uint8 is 6.2 MB a slide, and the patches are converted to float
            # where they are sampled, which is a few thousand pixels rather than two
            # million. Resolution is untouched: REG-02 forbids downsampling the plate,
            # because a stage sampled small blends neighbouring rows and invents contrast
            # failures. Precision is untouched too, because the source pixels were 8-bit.
            arr = np.asarray(Image.open(io.BytesIO(png)).convert("RGB"))
            plates[s["idx"]] = (arr, 0, 0, arr.shape[1] / CANVAS_W)
        b.close()

    adjudicate_gallery(slides, rep)

    for s in slides:
        validate_slide(s, rep, plate=plates.get(s["idx"]))
    validate_sequence(slides, rep)
    validate_map(slides, rep)
    validate_deck(slides, rep, plates)

    if only:
        pref = tuple(x.strip().upper() for x in only.split(","))
        rep.rows = [r for r in rep.rows if r["rule"].split("-")[0] in pref or r["rule"] in pref]

    # ---- output
    rep.rows.sort(key=lambda r: (r["slide"], -SEV[r["sev"]], r["rule"]))
    by_slide = defaultdict(list)
    for r in rep.rows:
        by_slide[r["slide"]].append(r)

    if not quiet:
        print(f"\nWWT design system validator — {len(slides)} slides, {len(rep.rows)} findings")
        print(f"  {len(rep.fails)} FAIL   {len(rep.warns)} WARN\n")
        for idx in sorted(by_slide):
            if idx == -1:
                print("DECK  [whole document]")
            else:
                role = slides[idx]["role"] or "—"
                print(f"slide {idx:>2}  [{role}]")
            for r in by_slide[idx]:
                print(f"   {r['sev']:<4} {r['rule']:<7} {r['selector']:<34} {r['detail']}")
            print()
        if not rep.rows:
            print("  clean\n")
        counts = defaultdict(int)
        for r in rep.rows:
            counts[r["rule"]] += 1
        if counts:
            print("by rule: " + "  ".join(f"{k}={v}" for k, v in sorted(counts.items())))
        if INK:
            print("\nink coverage: " + "  ".join(f"{k}={v:.0%}" for k, v in sorted(INK.items())))

    if json_out:
        with open(json_out, "w") as f:
            json.dump({"slides": len(slides), "fails": len(rep.fails),
                       "warns": len(rep.warns), "findings": rep.rows}, f, indent=1)
        if not quiet:
            print(f"\nwrote {json_out}")

    return 1 if rep.fails else 0



# ---------------------------------------------------------------- SEQ-01 -----
# "Do not use the same page style twice in a row unless the slides build on one
# another." The signature is what a reader actually perceives as a page style:
# the ground, the headline step, and the census of structural components. Two
# slides with the same signature look like the same page.
SIG_PARTS = ("media", "panel", "prac", "layer", "secrail", "stat", "badge",
             "chip", "logorow", "feat", "rule-list")


SUBSTANCE_SKIP = ("rail", "bug", "stripe", "mark", "lockup", "mesh", "brandx", "brandx-x",
                  "tri", "arrow", "gridover", "doc-anno", "spec-note", "slidecap", "cap")


SYSTEM_CLASSES = set()
SYSTEM_COMPONENTS = {}


def load_classes():
    """The system's own class inventory, shipped as assets/classes.json."""
    global SYSTEM_CLASSES, SYSTEM_COMPONENTS
    p = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                     "assets", "classes.json")
    if not os.path.exists(p):
        return
    d = json.load(open(p))
    SYSTEM_CLASSES = set(d.get("classes") or [])
    SYSTEM_COMPONENTS = d.get("components") or {}


# A deck-local class is a duplicate when it does a job a system component already does.
# Matched on the measurements that define each component rather than on its name, because
# the whole problem is that the name is different.
# STRUCTURAL components only, and only where duplication is unambiguous.
# A first version also matched type roles on font metrics: "24px at weight 400" made every
# paragraph a copy of .t-body-s and failed 37 slides of our own spec book, whose components
# legitimately set their own sub-copy at 20 and 22. Type consistency is TYP-12's job.
# Each test is the set of measurements that DEFINE the component, so a rename cannot hide.
DUP_SIGNATURES = (
    ("badge", lambda n: n["tag"] == "div" and 84 <= n["box"]["w"] <= 108
                        and 84 <= n["box"]["h"] <= 108 and n["fs"] >= 40
                        and n["fw"] in ("900", "800")),
    ("medallion", lambda n: n["box"]["w"] > 180 and abs(n["box"]["w"] - n["box"]["h"]) < 12
                            and "a circular border-radius" in (n.get("unexportable") or [])),
    ("panel", lambda n: n["tag"] == "div" and n["box"]["w"] >= 300 and n["box"]["h"] >= 200
                        and n["bg"] == "rgb(255, 255, 255)"
                        and "shadow" not in (n.get("cls") or "")
                        and n.get("deepWords", 0) > 0),
)


def nearest_component(n):
    """Which shipped component this deck-local element is a near-copy of, if any."""
    for name, test in DUP_SIGNATURES:
        try:
            if test(n):
                return name, SYSTEM_COMPONENTS.get(name, "see assets/system.css")
        except Exception:
            continue
    return None


def substance(s):
    """Content atoms and word count: the half of density that structure cannot fake.

    An atom is something a reader reads or reads a number off. Chrome does not count,
    and neither does an empty panel, so a slide of large empty boxes scores zero here
    however much of the canvas it covers.
    """
    atoms = words = 0
    for n in s["nodes"]:
        if has(n, *SUBSTANCE_SKIP) or n["inChrome"]:
            continue
        if n["tag"] in ("br", "path", "g", "svg"):
            continue
        w = len((n.get("text") or "").split())
        if n["hasText"] and w >= 1:
            atoms += 1
            words += w
        elif n["tag"] in ("li", "td", "th"):
            atoms += 1
        elif has(n, "stat", "chip", "badge", "feat", "prac", "layer", "ring") \
                and n.get("deepWords", 0) > 0:
            atoms += 1        # an empty component is not an atom
        elif n["tag"] == "img" and not has(n, "mark"):
            atoms += 1
    return atoms, words


def qualifying_photo(s):
    """TOTAL photography on the slide as a fraction of the canvas.

    The sum, not the largest. A card row of three 525 x 260 images reads as an illustrated
    slide and sums to 19.8%; one of those three alone in a corner reads as nothing and
    sums to 6.6%. Taking the largest cannot tell those apart and it failed a slide the
    creative director judged correct, which is how this was found.

    Marks, logos and the bug are excluded, so brand furniture cannot stand in for
    photography. Card images ARE included: they are related to the content beside them and
    they count.
    """
    total = 0.0
    for n in s["nodes"]:
        if n["tag"] != "img" or has(n, "mark"):
            continue
        if "lockup" in (n["parentSel"] or ""):
            continue
        b = n["box"]
        total += (b["w"] * b["h"]) / float(CANVAS_W * CANVAS_H)
    return min(total, 1.0)


def has_device(s):
    """Does the slide do at least one act of background design?

    A mesh, a Brand X, a flex triangle, a gradient ground, or a deliberate gradient
    panel. A gradient table header is not a background device: it is a component, and
    counting it would hand a pass to a deck of white pages with purple table headers,
    which is exactly the deck this rule exists to fail.
    """
    if s["counts"]["mesh"] or s["counts"]["brandx"]:
        return True
    if any(c in (s.get("slideCls") or "").split()
           for c in ("g-grad", "g-grad-diag", "g-dark")):
        return True
    if any(has(n, "tri", "panel--grad", "panel--grad93", "statband") for n in s["nodes"]):
        return True
    # Detect the gradient by what it IS, not by what it is called. Recipes 14 and 20 author
    # their gradient surfaces as bare divs with an inline background, and a class-only test
    # called both of them undesigned. 4% of the canvas is the floor: it clears a gradient
    # table header, which is a component rather than a background device, and counting one
    # of those would hand a pass to a deck of white pages with purple table rows.
    for n in s["nodes"]:
        bg = n.get("bgImg") or ""
        if "linear-gradient" not in bg:
            continue
        if n["tag"] in ("tr", "th", "td") or has(n, "rule-h--brand", "eyebrow"):
            continue
        area = (n["box"]["w"] * n["box"]["h"]) / float(CANVAS_W * CANVAS_H)
        if area >= 0.04:
            return True
    return False


def dominant_form(s):
    """What the eye reads as the slide's content, bucketed."""
    forms = []
    if any(n["tag"] == "table" for n in s["nodes"]):
        forms.append("table")
    if any(n["tag"] == "svg" and n["box"]["w"] > 400 for n in s["nodes"]):
        forms.append("chart")
    if sum(1 for n in s["nodes"] if has(n, "stat")) >= 2:
        forms.append("stats")
    if sum(1 for n in s["nodes"] if has(n, "panel") and n.get("deepWords", 0) > 2) >= 2:
        forms.append("cards")
    if any(n["tag"] == "li" for n in s["nodes"]):
        forms.append("list")
    return sorted(set(forms)) or ["prose"]


def architecture(s):
    """What a reader perceives as "the same page", in buckets a nudge cannot move.

    The old signature used exact values, so 20px of headline drift or one extra
    decorative element read as a different page style. That is why a deck with 68 of
    91 headlines on the same pixel passed. Ground, headline band, headline step,
    where the photography sits, and the content form. Nothing else.
    """
    ground = "photo"
    for c in (s.get("slideCls") or "").split():
        if c.startswith("g-"):
            ground = c
    head = next((n for n in s["nodes"]
                 if has(n, "t-display1", "t-display2", "t-h1-lg", "t-h1", "t-h2")), None)
    if head is None:
        band, step = "nohead", "none"
    else:
        y = head["box"]["y"]
        band = "top" if y < 200 else ("upper" if y < 380 else ("mid" if y < 620 else "low"))
        step = next(t for t in ("t-display1", "t-display2", "t-h1-lg", "t-h1", "t-h2")
                    if has(head, t))
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
    return "%s|%s|%s|%s|%s" % (ground, band, step, ph, "+".join(dominant_form(s)))


def norm_entropy(counts):
    n = sum(counts)
    if n <= 1:
        return 1.0
    h = -sum((c / n) * math.log(c / n) for c in counts if c)
    k = min(len(counts), n)
    return h / math.log(k) if k > 1 else 1.0


def dhash(arr, size=16):
    """Perceptual hash of a rendered slide, for near-duplicate detection."""
    from PIL import Image
    import numpy as np
    im = Image.fromarray(arr.astype("uint8")).convert("L").resize((size + 1, size),
                                                                  Image.LANCZOS)
    g = np.asarray(im, dtype=int)
    return (g[:, 1:] > g[:, :-1]).flatten()


def layout_signature(s):
    ground = "photo"
    for c in (s.get("slideCls") or "").split():
        if c.startswith("g-"):
            ground = c
    head = "none"
    for n in s["nodes"]:
        for t in ("t-display1", "t-display2", "t-h1-lg", "t-h1", "t-h2"):
            if t in (n.get("cls") or "").split():
                head = t
                break
        if head != "none":
            break
    census = []
    for part in SIG_PARTS:
        k = sum(1 for n in s["nodes"] if part in (n.get("cls") or "").split())
        if k:
            census.append("%s%d" % (part, k))
    tables = sum(1 for n in s["nodes"] if n["tag"] == "table")
    if tables:
        census.append("table%d" % tables)
    return "%s|%s|%s" % (ground, head, ",".join(census))


def _eyebrow(s):
    for n in s["nodes"]:
        if "eyebrow" in (n.get("cls") or "").split() and n["text"]:
            return n["text"].strip()
    return ""


def _headline(s):
    for n in s["nodes"]:
        cl = (n.get("cls") or "").split()
        if any(t in cl for t in ("t-display1", "t-display2", "t-h1-lg", "t-h1", "t-h2")):
            return re.sub(r"\s+", " ", n["text"]).strip()
    return ""


def _numerals(s):
    out = []
    for n in s["nodes"]:
        t = (n["text"] or "").strip()
        if re.fullmatch(r"0?\d{1,2}", t):
            out.append(int(t))
    return out


def builds_on(prev, cur):
    """Infer whether `cur` continues a build begun by `prev`.

    Inference, not declaration, so it is deliberately conservative: it wants
    positive evidence of a parallel set, and an exact repeat of the same eyebrow
    or headline is treated as repetition rather than as a build.
    Returns (bool, reason)."""
    pe, ce = _eyebrow(prev), _eyebrow(cur)
    ph, ch = _headline(prev), _headline(cur)

    # An identical eyebrow or headline is duplication, never a build.
    if (pe and pe == ce) or (ph and ph == ch):
        return False, ""

    # B1 an incrementing sequence numeral on both slides
    pn, cn = _numerals(prev), _numerals(cur)
    if pn and cn and min(cn) == min(pn) + 1:
        return True, "numbered %02d then %02d" % (min(pn), min(cn))

    # B2 both eyebrows are two-part with the same separator: the shape of a
    #    named set, e.g. "WORKFORCE AI - HOW YOUR FUNCTIONS WORK"
    seps = [sep for sep in ("\u00b7", "|", "\u2014", ":") ]
    for sep in seps:
        if pe.count(sep) >= 1 and ce.count(sep) == pe.count(sep):
            a = [x.strip() for x in pe.split(sep)]
            b = [x.strip() for x in ce.split(sep)]
            if len(a) == len(b) and a[0] != b[0]:
                return True, "parallel eyebrow set on %r" % sep

    # B3 IS GONE. It cleared a repeat when the two headlines shared a stem, their opening
    # or closing two words. "X" followed by "X (CONT.)" shares its ENTIRE stem, so the rule
    # written to prevent pagination was the rule licensing it, and nine continuation slides
    # went out under it. A shared stem is the signature of pagination, not evidence of a
    # build. It was flagged as the known weakness when it was written; this is it firing.
    #
    # A real build that the two remaining signals miss declares itself in markup:
    #     <div data-role="content" data-builds-on="prev" class="slide ...">
    # Declaration costs one attribute and cannot be inferred wrongly.
    # A declaration is honoured only if it is true of the markup. `data-builds-on` clears
    # SEQ-01 outright, and SEQ-01 is the rule that catches a deck running the same page
    # style over and over, so an unchecked attribute here is a licence to ship exactly the
    # thing the rule exists to stop. A build adds to what came before. If the headline has
    # not changed, nothing was added: that is the same slide again, wearing a label.
    if (cur.get("buildsOn") or "").strip().lower() in ("prev", "previous", "true", "yes"):
        ph, ch = _headline(prev), _headline(cur)
        if ph and ch and ph.strip().lower() == ch.strip().lower():
            return False, ""
        if substance(cur)[0] < substance(prev)[0]:
            return False, ""
        return True, "declared with data-builds-on"
    return False, ""


GAL_WORDS_MIN = 300   # words of running prose outside the slides
GAL_HEADS_MIN = 3     # section headings outside the slides
GAL_LISTS_MIN = 1     # at least one table or list outside the slides


def adjudicate_gallery(slides, rep):
    """GAL-01: a gallery claim has to be substantiated, or it is withdrawn.

    This was the widest loophole left in the rule set, and I put it there myself. Declaring
    `section.doc` or `data-gallery` switched off the whole deck-level family in one move:
    density, substance, photography share, mesh share, the background-device rule, deck
    length, role share, consecutive sameness. One attribute, thirty rules off, and nothing
    asked whether the file was actually a reference document.

    What makes a reference document one is that it is a document. It has sections, headings,
    running prose and tables, and the specimens sit inside that as illustrations. A deck has
    none of that: its words are all inside the slides, and between one slide and the next
    there is nothing. So the claim is tested against document furniture, measured outside
    the slides, with scripts and stylesheets removed.

    Measured, after the strip:

        spec book v4.4      9,926 words   83 headings   35 tables/lists   claims
        recipes.html        1,175 words   21 headings    1 table          claims
        Built for Success     981 words    2 headings    0                does not
        AI GTM 2026           478 words    1 heading     0                does not
        FDU test deck             0 words  0 headings    0                does not
        GTM customer deck       192 words  0 headings    0                does not

    Two earlier cuts of this rule were wrong and both were caught on our own files. The
    first counted prose alone and scored a worked-example DECK at 981 words, because a
    detached clone has no layout and innerText silently became textContent, so the page's
    own fit script read as prose. The second demanded a caption per specimen and failed the
    spec book at 26 of 44, because its component specimens are explained by the section
    around them rather than one by one. Furniture is the test that separates the six files
    above cleanly, and faking it means writing a reference document around your deck, which
    is more work than fixing the deck.

    A failed claim is not merely reported. It is withdrawn, and the file is judged as the
    deck it is.
    """
    if not slides or not slides[0].get("isGallery"):
        return
    f = slides[0].get("furniture") or {}
    words, heads, lists = f.get("words", 0), f.get("heads", 0), f.get("lists", 0)
    if words >= GAL_WORDS_MIN and heads >= GAL_HEADS_MIN and lists >= GAL_LISTS_MIN:
        return
    why = []
    if words < GAL_WORDS_MIN:
        why.append("%d words of prose outside the slides against a floor of %d"
                   % (words, GAL_WORDS_MIN))
    if heads < GAL_HEADS_MIN:
        why.append("%d section headings against a floor of %d" % (heads, GAL_HEADS_MIN))
    if lists < GAL_LISTS_MIN:
        why.append("no table or list outside the slides")
    rep.add("GAL-01", "FAIL", -1, "deck",
            "this file claims to be a reference gallery, which would switch off every "
            "deck-level rule at once, but it is not built like one: " + "; ".join(why)
            + ". The claim is withdrawn and the file is judged as a deck. A gallery is a "
              "document with sections, prose and tables that happens to contain slides")
    for s in slides:
        s["isGallery"] = False


def validate_deck(slides, rep, plates=None):
    """Rules that only exist at deck level, where the 91-slide RFP failure actually lived.

    Everything the validator did before this was "is this element correct". A deck can be
    correct element by element and still be 91 white pages with one layout, no photography
    and no background device anywhere. Absence was free. These rules price it.

    A gallery is exempt in full. The spec book shows twenty recipes in a row on purpose and
    its specimens are deliberately thin, so judging it as a deck is meaningless.
    """
    if not slides or slides[0].get("isGallery"):
        return
    # `spec` only excuses a slide inside a gallery, and a gallery never reaches this
    # function, so outside one every slide counts. See validate_slide and GAL-01.
    real = [s for s in slides if not (s.get("role") == "spec" and s.get("isGallery"))]
    n = len(real)
    if n < 4:
        return

    # ---- SEQ-06 deck length. A deck is not a document.
    if n > DECK_FAIL_LEN:
        rep.add("SEQ-06", "FAIL", -1, "deck",
                f'{n} slides. Over {DECK_FAIL_LEN} is a document that has been paginated, '
                f'not a presentation. Cut it, or split the appendix into its own file')
    elif n > DECK_WARN_LEN:
        rep.add("SEQ-06", "WARN", -1, "deck", f'{n} slides; over {DECK_WARN_LEN} needs a reason')

    # ---- SEQ-04 role share. Sparse roles carry a lower substance bar, so relabelling a
    # thin content slide as a statement would otherwise buy a pass. Cap the share.
    if n >= 8:
        sparse = sum(1 for s in real if (s.get("role") or "content") in SPARSE_ROLES)
        if sparse / n > SPARSE_MAX:
            rep.add("SEQ-04", "FAIL", -1, "deck",
                    f'{sparse} of {n} slides claim a sparse role (cover, divider, statement, '
                    f'closing), {sparse/n:.0%} against a ceiling of {SPARSE_MAX:.0%}. '
                    f'Those roles exist to be rare')

    # ---- SEQ-05 continuation slides. "(CONT.)" is the signature of pagination, and it is
    # what produced the emptiest pages in the deck this rule comes from.
    for s in real:
        for nd in s["nodes"]:
            if not has(nd, "t-display1", "t-display2", "t-h1-lg", "t-h1", "t-h2"):
                continue
            if re.search(r"\(\s*cont\.?\s*\)", (nd.get("text") or ""), re.I):
                rep.add("SEQ-05", "FAIL", s["idx"], nd["sel"],
                        'a "(cont.)" headline. Content that does not fit is cut, compressed '
                        'into a different recipe, or moved to an appendix document')

    # ---- SEQ-02 architecture diversity, on buckets rather than exact values
    if n >= 6:
        arch = collections.Counter(architecture(s) for s in real)
        top, cnt = arch.most_common(1)[0]
        share = cnt / n
        ent = norm_entropy(list(arch.values()))
        if share > ARCH_MAX_SHARE:
            rep.add("SEQ-02", "FAIL", -1, "deck",
                    f'{cnt} of {n} slides ({share:.0%}) share one page architecture '
                    f'"{top}", over the {ARCH_MAX_SHARE:.0%} ceiling')
        if ent < ARCH_MIN_ENTROPY:
            rep.add("SEQ-02", "FAIL", -1, "deck",
                    f'architecture entropy {ent:.2f} under {ARCH_MIN_ENTROPY:.2f}; '
                    f'{len(arch)} distinct architectures for {n} slides')

    # ---- IMG-07 / IMG-08 photograph IDENTITY.
    #
    # Nothing in the system had ever said a photograph may only appear once. Every rule was
    # about crop, resolution, scrim and share: whether an image is used WELL, never whether
    # it is used TWICE. A twelve-slide deck came back with the same frame on one slide twice
    # and a second frame on two slides, drawing on eight of nineteen available photographs,
    # so this was not scarcity. It returned zero failures, because the thing to check had
    # never been named.
    #
    # The two cases are not the same defect. The same photograph twice on ONE slide is
    # always wrong: it reads as a mistake, never as a motif. Across a deck it depends on
    # arithmetic. Nineteen frames cannot carry forty slides, so a long deck must repeat and
    # a short one has no excuse.
    lib = LIBRARY_SIZE
    per_slide = {}
    for s in real:
        ids = [x["photoId"] for x in s["nodes"] if x.get("photoId")]
        per_slide[s["idx"]] = ids
        dupes = {p for p in ids if ids.count(p) > 1}
        for _ in dupes:
            rep.add("IMG-07", "FAIL", s["idx"], ".slide",
                    "the same photograph appears twice on this slide. It reads as a "
                    "mistake rather than a motif, whatever the crops are")
    across = {}
    for idx, ids in per_slide.items():
        for p in set(ids):
            across.setdefault(p, []).append(idx)
    repeated = {p: v for p, v in across.items() if len(v) > 1}
    if repeated:
        detail = "; ".join("one frame on slides %s" % ", ".join(str(i) for i in v)
                           for v in list(repeated.values())[:4])
        if n <= lib:
            rep.add("IMG-08", "FAIL", -1, "deck",
                    f'{len(repeated)} photograph(s) used on more than one slide in a '
                    f'{n}-slide deck, and the library holds {lib}. {detail}. There is no '
                    f'arithmetic reason to repeat: pick another frame')
        else:
            rep.add("IMG-08", "WARN", -1, "deck",
                    f'{len(repeated)} photograph(s) used on more than one slide. {n} slides '
                    f'against a library of {lib}, so some repetition is unavoidable. Keep '
                    f'repeats far apart and never on adjacent slides')

    # ---- IMG-10 a band at the top or bottom of the page bleeds to its edges.
    #
    # The creative director's rule, in his words: a band can bleed when it is attached to
    # the bottom or the top of the page, like a header and a footer. Not every band. The
    # system ships a counter-example: recipe 07's 1248 x 316 inset band floats mid-page and
    # touches nothing, and it is correct, because it is an image in a layout rather than a
    # header.
    #
    # Measured off the recipes, which is where the rule comes from:
    #   recipe 11   1920 x 473   top 0,   touches left, top, right      a header
    #   recipe 17   1920 x 264   bottom 0, touches left, right, bottom  a footer
    #   recipe 07   1248 x 316   top 198, bottom 566, touches nothing   an inset band
    # And the defect that prompted it: four slides of one deck put a 1776 x 180 band at
    # bottom 100, inset 72 either side, so it floated in the footer zone with a strip of
    # empty ground under it and the page margin showing at both ends.
    #
    # THE THRESHOLD IS CALIBRATED, NOT DERIVED. 150 is the midpoint between the 100 that
    # was judged wrong and the 198 that is correct, which is the widest separation the
    # evidence offers. Two points either side is thin. If a band ever fails this and looks
    # right, the number is the first thing to question, not the slide.
    # NOTE the loop variables. `n` is the slide count in this function and `s` is used as a
    # slide elsewhere in it, so this block binds `sld` and `nd`. The first cut reused both,
    # which left `n` holding a node dict; validate_deck then threw on `if n >= 5`, the
    # exception was swallowed upstream, and EVERY deck-level rule after this point stopped
    # running with no error and no output. The rule under test reported nothing, which read
    # as "it does not fire" rather than "the function died".
    BAND_MIN_W, BAND_RATIO, BAND_EDGE = 900, 2.5, 150
    for sld in real:
        for nd in sld["nodes"]:
            if not has(nd, "media"):
                continue
            b = nd["box"]
            if b["w"] < BAND_MIN_W or b["h"] <= 0 or b["w"] / b["h"] < BAND_RATIO:
                continue
            gap_t, gap_b = b["y"], CANVAS_H - b["y2"]
            edge = "top" if gap_t <= BAND_EDGE else ("bottom" if gap_b <= BAND_EDGE else None)
            if edge is None:
                continue                      # an inset band, mid-page. Recipe 07.
            missing = []
            if (gap_t if edge == "top" else gap_b) > 2:
                missing.append("the %s" % edge)
            if b["x"] > 2:
                missing.append("the left")
            if b["x2"] < CANVAS_W - 2:
                missing.append("the right")
            if missing:
                rep.add("IMG-10", "FAIL", sld["idx"], nd["sel"],
                        f'a {b["w"]:.0f} x {b["h"]:.0f} band sits in the {edge} zone but does '
                        f'not reach {", ".join(missing)}. A band attached to the top or the '
                        f'bottom is a header or a footer and runs to all three edges; a band '
                        f'that floats mid-page does not have to, but this one is not floating')

    # ---- IMG-05 / IMG-06 photography, share and distribution
    ph = [qualifying_photo(s) >= PHOTO_MIN_AREA for s in real]
    if n >= 5:
        share = sum(ph) / n
        if share < PHOTO_FLOOR:
            rep.add("IMG-05", "FAIL", -1, "deck",
                    f'{sum(ph)} of {n} slides ({share:.0%}) carry a photograph at a real crop, '
                    f'under the {PHOTO_FLOOR:.0%} floor, against a {PHOTO_WARN:.0%} target. '
                    f'Nineteen approved frames ship with '
                    f'this system')
        elif share < PHOTO_WARN:
            rep.add("IMG-05", "WARN", -1, "deck",
                    f'photography {share:.0%}, under the {PHOTO_WARN:.0%} target. Acceptable, '
                    f'not good. A slide counts when its imagery sums to {PHOTO_MIN_AREA:.0%} '
                    f'of the canvas')
    if n >= 10:
        run = worst = 0
        start = 0
        for k, v in enumerate(ph):
            if v:
                run = 0
            else:
                if run == 0:
                    start = k
                run += 1
                if run > worst:
                    worst, wstart = run, start
        if worst > PHOTO_MAX_GAP:
            rep.add("IMG-06", "FAIL", -1, "deck",
                    f'{worst} consecutive slides with no photograph, from slide {wstart}. '
                    f'Meeting the share by front-loading and coasting is not meeting it')

    # ---- TYP-12 one body step per JOB, across the deck.
    # The defect Toby reported was pages 7 and 8 setting the same kind of copy at 24px and
    # 20px. A first cut of this rule counted the dominant 18-34px size per slide and failed
    # my own decks for using 20 inside cards and 26 in prose, which are two different jobs
    # and two legitimate steps. Conflating them measured the wrong thing.
    # So: body copy OUTSIDE a panel is one job, body copy INSIDE a panel is another, and
    # each has to be consistent with itself across the deck. A card interior may sit a step
    # below the slide's body; it may not wander.
    # Only elements carrying a SYSTEM BODY TOKEN count. Two earlier cuts of this rule
    # counted "any 18-34px text", which swept in stat notes, chip labels and every
    # component's own sub-copy, and failed my own decks for using 20px inside a card and
    # 26px in prose. Those are different jobs at their own fixed sizes.
    # Scoped this way the rule asks one question: when the deck uses .t-body, does it use
    # the same size every time. A deck that avoids the tokens entirely is SYS-01's problem.
    # t-lede is NOT body copy. It is the one sentence under a headline and has exactly one
    # size by definition, so counting it made every deck look like it used three body steps.
    BODY_TOKENS = ("t-body", "t-body-s", "t-body-l")
    if n >= 5:
        jobs = {"body": {}, "card": {}}
        for sl in real:
            tally = {"body": collections.Counter(), "card": collections.Counter()}
            for nd in sl["nodes"]:
                if not nd["hasText"] or nd["inChrome"] or not has(nd, *BODY_TOKENS):
                    continue
                fs = int(round(nd["fs"]))
                if not (18 <= fs <= 48):
                    continue
                where = "card" if nd.get("panelInset") else "body"
                tally[where][fs] += len((nd.get("text") or "").split())
            for k in ("body", "card"):
                if tally[k]:
                    jobs[k][sl["idx"]] = tally[k].most_common(1)[0][0]
        for k, label in (("body", "body copy"), ("card", "card interiors")):
            per = jobs[k]
            if len(per) < 4:
                continue
            spread = collections.Counter(per.values())
            dom, dom_n = spread.most_common(1)[0]
            off = sorted(x for x, v in per.items() if v != dom)
            if len(spread) > BODY_STEPS_MAX:
                rep.add("TYP-12", "FAIL", -1, "deck",
                        f'{label} is set at {len(spread)} different sizes across the deck '
                        f'({", ".join("%dpx on %d" % (a, b) for a, b in sorted(spread.items()))}). '
                        f'Pick one step for this job and hold it. Dominant is {dom}px; off it '
                        f'on slides {", ".join(str(x) for x in off[:12])}')
            elif off and len(off) / len(per) > 0.4:
                rep.add("TYP-12", "WARN", -1, "deck",
                        f'{label} is {dom}px on {dom_n} of {len(per)} slides and another step '
                        f'on {len(off)}. Consistent is better than merely legal')

    # ---- PAT-09 the emphasis ceiling.
    # Every other presence rule here is a FLOOR: use the library, fill the page, vary the
    # architecture. This one is a CEILING, and it is the first of its kind, so the gaming
    # direction is inverted. Nobody games a ceiling by adding nothing; they game it by
    # deciding the dark ground looks good and using it everywhere, at which point it stops
    # being emphasis and becomes the deck.
    # max(1, ...) so a short deck can still carry one emphasis slide: at 20% a three-slide
    # deck would otherwise be allowed none.
    dark = [sl["idx"] for sl in real if "g-dark" in (sl.get("slideCls") or "").split()]
    if dark:
        cap = max(1, int(n * DARK_MAX_SHARE))
        if len(dark) > cap:
            rep.add("PAT-09", "FAIL", -1, "deck",
                    f'the dark emphasis ground is on {len(dark)} of {n} slides '
                    f'({len(dark)/n:.0%}), over the ceiling of {cap} '
                    f'({DARK_MAX_SHARE:.0%}, one slide in five). It is an emphasis ground: a '
                    f'deck where every page shouts has no emphasis left. Slides: '
                    f'{", ".join(str(x) for x in dark)}')
        # two dark slides in a row is not emphasis either, whatever the share
        runs = [b for a, b in zip(dark, dark[1:]) if b == a + 1]
        if runs:
            rep.add("PAT-09", "FAIL", -1, "deck",
                    f'consecutive dark slides at {", ".join(str(x) for x in runs)}. '
                    f'An emphasis page needs something either side of it to be emphatic '
                    f'against')

    # ---- SEQ-03 the same slide shipped twice.
    # Measured on TEXT plus architecture, not on a pixel hash. The first version hashed the
    # validator's text-hidden plate, which is the plate used for contrast sampling, so any
    # parallel set read as a duplicate: it flagged two of the three AI Native slides, which
    # are the same layout carrying different content on purpose. Layout repetition is what
    # SEQ-01 and SEQ-02 are for. Duplication means the same words.
    def toks(sl):
        t = " ".join((nd.get("text") or "") for nd in sl["nodes"]
                     if not has(nd, "rail", "bug", "stripe", "mark") and not nd["inChrome"])
        return set(re.findall(r"[a-z0-9]+", t.lower()))

    sig = {sl["idx"]: (architecture(sl), toks(sl)) for sl in real}
    ids = sorted(sig)
    seen = set()
    for a in range(len(ids)):
        if ids[a] in seen:
            continue
        aa, ta = sig[ids[a]]
        if len(ta) < 6:
            continue
        for b in range(a + 1, len(ids)):
            if ids[b] in seen:
                continue
            ab, tb = sig[ids[b]]
            if aa != ab or len(tb) < 6:
                continue
            j = len(ta & tb) / float(len(ta | tb))
            if j >= 0.90:
                seen.add(ids[b])
                rep.add("SEQ-03", "FAIL", ids[b], ".slide",
                        f'the same slide as {ids[a]}: identical architecture and '
                        f'{j:.0%} of the same words. One of them is redundant')


def validate_map(slides, rep):
    """MAP-01: every recipe in the gallery appears in the source map, and every
    map row names a recipe that exists.

    Four layouts sat unbuilt for months while the map claimed they were covered,
    because nothing checked the map against the gallery. A claim nobody verifies
    is worse than no claim."""
    if not slides or not slides[0].get("isGallery"):
        return
    gallery = slides[0].get("recipeIds") or []
    mapped = slides[0].get("mapIds") or []
    if not gallery or not mapped:
        return
    for rid in gallery:
        if rid not in mapped:
            rep.add("MAP-01", "FAIL", 0, "table.spec",
                    "recipe %s is in the gallery but not in the source map" % rid)
    for rid in mapped:
        if rid not in gallery:
            rep.add("MAP-01", "FAIL", 0, "table.spec",
                    "the source map lists recipe %s, which does not exist" % rid)


def validate_sequence(slides, rep):
    """SEQ-01: no two consecutive slides on the same page style unless the
    second builds on the first.

    A reference document is exempt in full. The spec book shows seventeen
    recipes in a row and a component gallery after them; consecutive sameness is
    what a gallery IS. Detected by `section.doc` or an explicit [data-gallery].
    This is a narrative rule, and a gallery has no narrative."""
    if slides and slides[0].get("isGallery"):
        return
    prev = None
    for s in slides:
        role = s["role"] or "content"
        if role in ("cover", "closing", "divider") or (role == "spec" and s.get("isGallery")):
            prev = None            # section boundaries reset the run
            continue
        sig = layout_signature(s)
        if prev and sig == prev[1]:
            ok, why = builds_on(prev[0], s)
            if ok:
                rep.add("SEQ-01", "WARN", s["idx"], ".slide",
                        "same page style as slide %d, read as a build (%s)"
                        % (prev[0]["idx"], why))
            else:
                rep.add("SEQ-01", "FAIL", s["idx"], ".slide",
                        "same page style as slide %d and nothing marks it as a build "
                        "(%s)" % (prev[0]["idx"], sig))
        prev = (s, sig)


def main():
    load_classes()
    ap = argparse.ArgumentParser(description="WWTDigital design system validator")
    ap.add_argument("deck", help="path or URL to the rendered deck")
    ap.add_argument("--roles", help="JSON map of slide index to role")
    ap.add_argument("--only", help="comma-separated rule prefixes, e.g. GEO,MRK")
    ap.add_argument("--json", dest="json_out", help="write a JSON report")
    ap.add_argument("--quiet", action="store_true")
    a = ap.parse_args()
    roles = json.load(open(a.roles)) if a.roles else {}
    sys.exit(run(a.deck, roles, a.only, a.quiet, a.json_out))


if __name__ == "__main__":
    main()
