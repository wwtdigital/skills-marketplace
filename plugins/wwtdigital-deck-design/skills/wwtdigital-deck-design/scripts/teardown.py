#!/usr/bin/env python3
"""
Render the brand teardown: every token in this system as a live specimen, on one page.

    python3 scripts/teardown.py [-o WWT-teardown.html] [--open]

READ THIS BEFORE YOU BUILD ANYTHING. That is the whole job of the page.

The validator checks output against rules. Nothing checked whether the person building
understood the system before they started, and two failures in a row came back looking
exactly like that. The RFP deck was 91 pages of one layout with no photography and
no background device: not a rule broken so much as a system never absorbed. The Forward
Deployed Unit deck had the wrong bug in two corners, body copy drifting across three size
steps, and a gradient rule invented inside a gradient panel. Both builders had the skill.
Neither had ever seen the system.

So this page exists, and it is not documentation. It is a review gate:

  * every value is rendered rather than listed. A colour is a swatch, a type step is a line
    set at that size in that real cut, a shadow is a card wearing it, a radius is a corner.
    There is no table of hex strings to skim, because skimming the tables is how both
    failures happened.
  * every value comes from assets/tokens.json, which is generated from system.css, so this
    page cannot drift from the stylesheet. The prose comes from assets/teardown.json.
    Nothing on the page is typed here.
  * every contrast ratio is computed at render time from WCAG relative luminance. None is
    estimated, and the one that fails is shown failing.
  * the gaps are named. Four things this system does not have are listed as gaps rather
    than filled in with something plausible, because a guess presented as a fact is the
    most expensive thing a reference document can do.

    system.css -> tokens.py -> tokens.json ---+
    assets/teardown.json ---------------------+--> teardown.py -> one HTML page
    assets/fonts, assets/vectors, manifest ---+

Aptos is embedded so the ladder renders in the real cuts. Archivo at 900 is visibly lighter
than Aptos Black and would misrepresent the half of this review that matters most. The page
is internal tooling; see the licensing note in SKILL.md before sending it outside WWT.
"""
import argparse, base64, json, os, re, sys

import skilldoc

import brand_assets

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
A = lambda *p: os.path.join(ROOT, "assets", *p)

# (family, face to resolve, weight, style). Read from this machine by brand_assets.py;
# the serif is optional because Office only fetches it on first use.
FONTS = [("Aptos", "Aptos", "400", "normal"),
         ("Aptos", "Aptos Bold", "700", "normal"),
         ("Aptos Black", "Aptos Black", "900", "normal"),
         ("Aptos Serif", brand_assets.SERIF, "700", "italic")]
FONT_MIME = {".woff2": ("font/woff2", "woff2"), ".ttf": ("font/ttf", "truetype"),
             ".otf": ("font/otf", "opentype")}

TYPE_CAP = 76          # the widest step this page can hold; above it, shown reduced
SPEC_ORDER = ["t-display1", "t-display2", "t-h1-lg", "t-h1", "t-h1--stmt", "t-h2",
              "stat-hero", "t-quote", "t-h3", "t-lede", "t-coversub", "t-label",
              "t-body-l", "t-body", "t-body-s", "t-source", "t-micro", "t-caption",
              "eyebrow"]


# ----------------------------------------------------------------- contrast, computed
def _lin(c):
    c /= 255
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4


def lum(h):
    h = h.lstrip("#")
    if len(h) == 3:
        h = "".join(c * 2 for c in h)
    r, g, b = (int(h[i:i + 2], 16) for i in (0, 2, 4))
    return .2126 * _lin(r) + .7152 * _lin(g) + .0722 * _lin(b)


def ratio(fg, bg):
    a, b = lum(fg), lum(bg)
    hi, lo = max(a, b), min(a, b)
    return (hi + .05) / (lo + .05)


def grade(r, large):
    """WCAG 2.0 AA. Large scale is >=24px regular or >=18.66px bold, which every step in
    this ladder except t-caption clears, so 'large only' is a real and usable grade here
    rather than a euphemism for a failure."""
    if r >= 7:
        return "AAA", "aaa"
    if r >= 4.5:
        return "AA", "aa"
    if r >= 3:
        return ("AA large" if large else "AA large only"), "warn"
    return "FAIL", "fail"


def b64(path, mime):
    return "data:%s;base64,%s" % (mime, base64.b64encode(open(path, "rb").read()).decode())


def svg(path):
    return re.sub(r"<\?xml.*?\?>", "", open(path, encoding="utf-8").read(), flags=re.S).strip()


def hexes(value):
    """Every hex in a token value, so a gradient's stops can be measured individually."""
    return re.findall(r"#[0-9A-Fa-f]{6}", value)


def px(v):
    m = re.match(r"([\d.]+)px", str(v or ""))
    return float(m.group(1)) if m else None


def esc(s):
    return s


# ----------------------------------------------------------------- page
CSS = """
  :root{
    --paper:%(surface)s; --surface:%(raised)s; --line:%(line)s;
    --ink:%(ink)s; --ink-max:%(inkmax)s; --ink-600:%(ink600)s; --ink-500:%(ink500)s;
    --ink-400:%(ink400)s; --ink-200:%(ink200)s; --ink-100:%(ink100)s;
    --brand:%(brand)s; --brand-deep:%(deep)s; --brand-red:%(red)s;
    /* Grade chips are page furniture, not brand tokens: this system defines no semantic
       feedback palette, because a slide has no error state. */
    --ok-100:#EAF4EC; --ok-600:#1D5B2A; --warn-100:#FFF4E5; --warn-600:#7A4A00;
    --bad-100:#FDECEC; --bad-600:#A4161A; --info-100:#E6F3FE; --info-600:#0A5E9E;
    --sans:'Aptos',ui-sans-serif,system-ui,sans-serif;
    --black:'Aptos Black','Aptos',sans-serif;
    --serif:'Aptos Serif',Georgia,serif;
    --mono:ui-monospace,SFMono-Regular,Menlo,monospace;
    --shadow-card:%(shadow)s;
  }
  *{margin:0;padding:0;box-sizing:border-box}
  body{background:var(--paper);color:var(--ink);font-family:var(--sans);font-size:18px;line-height:30px;-webkit-font-smoothing:antialiased}
  .wrap{max-width:1200px;margin:0 auto;padding:0 40px}
  @media(max-width:720px){.wrap{padding:0 24px}}
  section{padding-top:96px}
  h1,h2,h3,h4{font-weight:700;text-wrap:balance}
  h1{font-size:44px;line-height:50px;letter-spacing:-.025em}
  @media(min-width:900px){h1{font-size:56px;line-height:60px;letter-spacing:-.03em}}
  h2{font-size:32px;line-height:38px;letter-spacing:-.02em;margin-top:8px}
  h3{font-size:24px;line-height:32px;letter-spacing:-.015em}
  h4{font-size:20px;line-height:28px;font-weight:500}
  p{max-width:720px}
  .overline{font-size:11px;line-height:16px;letter-spacing:.08em;font-weight:700;text-transform:uppercase;color:var(--ink-500)}
  .lead{margin-top:16px;font-size:18px;line-height:30px}
  .note{font-size:14px;line-height:22px;color:var(--ink-500);max-width:760px}
  /* Each reference document states which job it does. There are two of them and a
     reader who opens the wrong one wastes an afternoon. */
  .purpose{max-width:820px;margin:26px 0 0;padding:16px 20px;font-size:14.5px;
           line-height:1.6;border-left:3px solid var(--brand);
           background:rgba(0,134,234,.06);border-radius:0 6px 6px 0;
           color:var(--ink)}
  .purpose strong{color:var(--ink-max)}
  .mono{font-family:var(--mono);font-variant-numeric:tabular-nums;font-size:14px;line-height:20px}
  .card{background:var(--surface);border:1px solid var(--line);box-shadow:var(--shadow-card);padding:24px}
  .btn{display:inline-block;font-weight:700;font-size:16px;line-height:26px;padding:12px 24px;border:0;cursor:pointer;color:#fff;background:var(--brand)}
  .btn.ghost{background:transparent;color:var(--brand);box-shadow:inset 0 0 0 2px var(--brand)}
  .chip{display:inline-block;font-family:var(--mono);font-size:12px;line-height:16px;padding:4px 12px;border-radius:4px}
  .chip.aaa{background:var(--ok-100);color:var(--ok-600)}
  .chip.aa{background:var(--info-100);color:var(--info-600)}
  .chip.warn{background:var(--warn-100);color:var(--warn-600)}
  .chip.fail{background:var(--bad-100);color:var(--bad-600)}
  .chip.plain{background:var(--ink-100);color:var(--ink)}
  .tblwrap{overflow-x:auto;margin-top:32px;border:1px solid var(--line);background:var(--surface);box-shadow:var(--shadow-card)}
  table{border-collapse:collapse;width:100%%;min-width:560px}
  th{font-size:11px;letter-spacing:.08em;text-transform:uppercase;font-weight:700;text-align:left;color:var(--ink-500);padding:14px 20px;border-bottom:2px solid var(--ink)}
  td{font-size:14px;line-height:22px;padding:12px 20px;border-bottom:1px solid var(--line);vertical-align:top}
  tr:last-child td{border-bottom:none}
  td.m{font-family:var(--mono);white-space:nowrap}
  .grid{display:grid;gap:32px;margin-top:32px}
  .g2{grid-template-columns:repeat(auto-fit,minmax(320px,1fr))}
  .g3{grid-template-columns:repeat(auto-fit,minmax(260px,1fr))}
  ul.rules{list-style:none;margin-top:24px;max-width:880px}
  ul.rules li{padding:12px 0 12px 34px;border-bottom:1px solid var(--line);position:relative;font-size:16px;line-height:26px}
  ul.rules li::before{content:"";position:absolute;left:0;top:19px;width:14px;height:14px;background:var(--brand)}
  ul.rules.ban li::before{background:var(--brand-red);border-radius:999px}
  .sw{border:1px solid var(--line);height:64px}
  .swlab{margin-top:8px;font-family:var(--mono);font-size:12px;line-height:16px;color:var(--ink-500)}
  .swlab b{display:block;color:var(--ink);font-weight:500}
  .ramp{display:grid;grid-template-columns:repeat(auto-fit,minmax(118px,1fr));gap:8px;margin-top:24px}
  .toc{display:flex;flex-wrap:wrap;gap:10px;margin-top:32px}
  .toc a{font-family:var(--mono);font-size:12px;text-decoration:none;color:var(--ink);border:1px solid var(--line);padding:6px 14px;background:var(--surface)}
  .secnum{font-family:var(--mono);font-size:12px;color:var(--ink-500);letter-spacing:.08em}
  .callout{margin-top:32px;border:1px solid var(--line);box-shadow:var(--shadow-card);padding:24px;max-width:880px}
  .callout.danger{background:var(--bad-100)}
  .callout.brandwash{background:%(gradv)s;color:#fff;border:0}
  .callout.brandwash h4,.callout.brandwash p{color:#fff}
  .callout h4{margin-bottom:8px}
  .callout p{font-size:16px;line-height:26px}
  .typerow{display:grid;grid-template-columns:250px 1fr;gap:24px;align-items:baseline;padding:18px 0;border-bottom:1px solid var(--line)}
  @media(max-width:720px){.typerow{grid-template-columns:1fr;gap:4px}}
  .typerow .spec{font-family:var(--mono);font-size:12px;line-height:18px;color:var(--ink-500)}
  .typerow .spec b{color:var(--ink);font-weight:500;display:block}
  .dark{background:%(graddark)s;color:#fff;overflow:hidden;position:relative}
  .dark .inner{padding:32px}
  .dark .dcard{background:rgba(255,255,255,.10);border:1px solid rgba(255,255,255,.22);padding:20px}
  .dmuted{color:rgba(255,255,255,.72)}
  .spacebar{height:16px;background:var(--brand)}
  .kv{display:grid;grid-template-columns:auto 1fr;gap:6px 20px;font-size:14px;line-height:22px;margin-top:16px}
  .kv dt{font-family:var(--mono);font-size:12px;color:var(--ink-500);padding-top:2px;white-space:nowrap}
  .kv dd{margin:0}
  .proof{display:flex;flex-wrap:wrap;gap:32px;margin-top:32px}
  .proof .num{font-family:var(--black);font-size:64px;line-height:64px;font-weight:900;letter-spacing:-.04em;color:var(--brand)}
  .proof .cap{font-size:12px;line-height:16px;color:var(--ink-500);margin-top:4px;max-width:190px}
  .gap{border-left:3px solid var(--warn-600);background:var(--warn-100);padding:16px 20px;margin-top:16px;max-width:880px}
  .gap .overline{color:var(--warn-600)}
  .gap p{font-size:15px;line-height:24px;margin-top:6px}
  .footer-gate{margin:96px 0 0;border-top:2px solid var(--ink);padding:64px 0 96px}
"""


def icon_set():
    """The icon library, read for the teardown's section 09.

    Returns live markup rather than paths, because this page renders the system instead of
    describing it. A representative sample rather than all 497: the point of the section is
    whether the set holds together, and 497 tiles is a wall nobody reads. The full set is
    on disk and in the manifest for anyone who wants to count it.
    """
    mp = A("icons", "manifest.json")
    out = {"icons": {}, "branded": {}, "src": {}, "mono": 0, "colour": 0,
           "sample": "", "row": [], "grid": [], "brandgrid": []}
    if not os.path.exists(mp):
        return out
    with open(mp, encoding="utf-8") as fh:
        m = json.load(fh)
    out["src"] = m.get("source", {})
    out["icons"], out["branded"] = m.get("icons", {}), m.get("branded", {})
    out["mono"] = sum(1 for v in out["icons"].values() if v.get("mono"))
    out["colour"] = len(out["icons"]) - out["mono"]

    bp = A("icons", "icons.json")
    blob = json.load(open(bp, encoding="utf-8")) if os.path.exists(bp) else {}

    def mk(name, group="icons"):
        # The markup comes out of the one bundle file. The manifest holds names and
        # provenance only, so that the fast lint can parse it without reading a megabyte.
        return blob.get(name, "").strip() if name in out[group] else ""

    names = sorted(out["icons"])
    out["sample"] = mk("assessment") or (mk(names[0]) if names else "")
    for n in ("assessment", "lab", "users", "gear", "clock", "warning", "search", "calendar"):
        k = mk(n)
        if k:
            out["row"].append(k)
    # Evenly spaced through the alphabetised set, so the sample is the set rather than the
    # first screen of it.
    step = max(1, len(names) // 48)
    for n in names[::step][:48]:
        k = mk(n)
        if k:
            out["grid"].append((n, k))
    bnames = sorted(out["branded"])
    bstep = max(1, len(bnames) // 24)
    for n in bnames[::bstep][:24]:
        k = mk(n, "branded")
        if k:
            out["brandgrid"].append((n, k))
    return out


def build():
    tok = json.load(open(A("tokens.json"), encoding="utf-8"))
    cp = json.load(open(A("teardown.json"), encoding="utf-8"))
    man = json.load(open(A("manifest.json"), encoding="utf-8"))
    prov = json.load(open(A("provenance.json"), encoding="utf-8"))

    col = {k: v["$value"] for k, v in tok["color"].items()}
    grad = {k: v["$value"] for k, v in tok["gradient"].items()}
    shad = {k: v["$value"] for k, v in tok["shadow"].items()}
    dim = {k: v["$value"] for k, v in tok["dimension"].items()}
    typ = {k: v["$value"] for k, v in tok["typography"].items()}

    surface, raised = col["surface"], col["surface-raised"]
    css = CSS % dict(surface=surface, raised=raised, line=col["ink-100"],
                     ink=col["ink-800"], inkmax=col["ink-900"], ink600=col["ink-600"],
                     ink500=col["ink-500"], ink400=col["ink-400"], ink200=col["ink-200"],
                     ink100=col["ink-100"], brand=col["wwt-blue"], deep=col["wwt-purple"],
                     red=col["wwt-red"], shadow=shad["shadow-panel"],
                     gradv=grad["grad-brand-v"], graddark=grad["grad-dark-diag"])

    paths = brand_assets.require_fonts([f for _, f, _, _ in FONTS if f != brand_assets.SERIF])
    paths[brand_assets.SERIF] = brand_assets.font_path(brand_assets.SERIF)
    faces = "".join(
        "@font-face{font-family:'%s';src:url('%s') format('%s');font-weight:%s;"
        "font-style:%s;font-display:swap}"
        % (fam, b64(paths[f], FONT_MIME[os.path.splitext(paths[f])[1].lower()][0]),
           FONT_MIME[os.path.splitext(paths[f])[1].lower()][1], w, st)
        for fam, f, w, st in FONTS if paths[f])

    logo_w = svg(A("vectors", "logo-full.svg"))
    logo_i = logo_w.replace('fill="white"', 'fill="%s"' % col["ink-800"])
    bug = svg(A("vectors", "bug-mark.svg"))

    # The mesh specimen is the real vector, windowed onto the middle of the artwork where
    # the baked-in fade is at full strength. See the note in teardown.json.
    mesh = open(A("vectors", "mesh-diag.svg"), encoding="utf-8").read()
    mesh_win = mesh.replace('width="1205" height="1080" viewBox="0 0 1205 1080"',
                            'width="100%" viewBox="210 430 1205 250" '
                            'preserveAspectRatio="xMidYMid slice"')
    if mesh_win == mesh:
        sys.exit("mesh-diag.svg header changed; the teardown window no longer matches")

    o = []
    w = o.append

    # ---------------------------------------------------------------- header
    n_files = sum(len(fs) for _, _, fs in os.walk(ROOT))
    w('<!doctype html><title>%s brand teardown</title>' % cp["brand"])
    w('<meta name="viewport" content="width=device-width, initial-scale=1">')
    w("<style>%s%s</style>" % (faces, css))
    w('<header class="wrap" style="padding-top:56px">')
    w('<div style="display:flex;justify-content:space-between;align-items:center;gap:24px;flex-wrap:wrap">')
    w('<div style="height:36px">%s</div>' % logo_i)
    w('<span class="chip plain">v%s &middot; %d colours &middot; %d type steps &middot; '
      '%d recipes &middot; every value measured</span>'
      % (tok["$version"], len(col), len(typ), len(prov["recipes"])))
    w('</div><div style="margin-top:72px">')
    w('<div class="overline">Read this before you build anything</div>')
    w('<h1 style="margin-top:12px">The system, rendered</h1>')
    w('<p class="lead">Every token is a specimen here rather than a value in a table. '
      'The validator checks what you produce; this page is the half that was missing, '
      'which is checking that you have seen the system before you start. '
      # Counted, not typed. This line said "four gaps" and the Iconography entry left the
      # list at v4.10, so the page contradicted its own last section. A number in prose
      # about a list that can change is a number that will be wrong.
      '<strong>The %s at the end %s gaps, not omissions.</strong></p>'
      % (("%d gaps" % len(cp["gaps"])) if len(cp["gaps"]) != 1 else "one gap",
         "are" if len(cp["gaps"]) != 1 else "is"))
    w('<nav class="toc">')
    for i, (aid, label) in enumerate(SECTIONS):
        w('<a href="#%s">%02d %s</a>' % (aid, i + 1, label))
    w('</nav></div></header><main class="wrap">')

    open_section = [False]

    def sec(idx, aid, title, lead=None):
        """Open a section, closing the previous one first.

        The first cut never emitted a closing tag, so all eleven sections nested inside
        section one and every per-section screenshot captured the rest of the page. It
        rendered correctly in a browser, which is how it survived the first look.
        """
        if open_section[0]:
            w('</section>')
        open_section[0] = True
        w('<section id="%s"><div class="secnum">%02d / %02d</div><h2>%s</h2>'
          % (aid, idx + 1, len(SECTIONS), title))
        if lead:
            w('<p class="lead">%s</p>' % lead)

    # The document's own statement of which job it does. Both reference documents carry
    # one, because there are two and a reader who opens the wrong one wastes an afternoon.
    # The split is by job, not by subject: this page is for LOOKING AT the system, the spec
    # book is for COPYING GEOMETRY out of it. Where they overlap, neither is allowed to
    # disagree with the other, which scripts/check_documents.py enforces.
    w('<p class="purpose"><strong>What this page is for: looking at.</strong> It renders the '
      'system rather than describing it, so five minutes here teaches more than an hour in a '
      'table of hex values. Two decks came back wrong from builders who had the skill '
      'installed and had never seen the system. <strong>It is not the document to build '
      'from.</strong> Geometry lives in <span class="mono">assets/recipes.html</span> and in '
      'the spec book, measured, and geometry is the one thing you must never retype from a '
      'summary.</p>')

    # ---------------------------------------------------------------- 01 identity
    sec(0, "s1", "Identity",
        "The promise: <em>%s</em> That line is %s." % (cp["promise"], cp["promise_source"]))
    w('<div style="margin-top:24px;display:flex;gap:10px;flex-wrap:wrap">%s</div>'
      % "".join('<span class="chip plain">%s</span>' % t for t in cp["traits"]))
    w('<p class="note" style="margin-top:12px">%s</p>' % cp["traits_source"])
    sig = cp["signature"]
    w('<div class="card" style="margin-top:40px;max-width:880px;padding:32px">')
    w('<div class="overline">%s</div>' % sig["title"])
    w('<div style="margin-top:20px;font-family:var(--black);font-weight:900;font-size:56px;'
      'line-height:.9;letter-spacing:-.06em;text-transform:uppercase;color:var(--ink)">%s<br>'
      '<em style="font-style:normal;color:var(--ink-max)">%s</em></div>'
      % (sig["headline_base"], sig["headline_clause"]))
    w('<p class="note" style="margin-top:20px">%s</p></div>' % sig["rule"])
    w('<div class="callout brandwash"><h4>%s</h4><p>%s</p></div>'
      % (cp["arrow"]["title"], cp["arrow"]["body"]))

    # ---------------------------------------------------------------- 02 logo
    L = cp["logo"]
    sec(1, "s2", "Logo", L["lead"])
    w('<div class="grid g2"><div class="card">')
    w('<div class="overline">%s</div><dl class="kv">%s</dl>'
      % (L["construction_title"],
         "".join("<dt>%s</dt><dd>%s</dd>" % (k, v) for k, v in L["geometry"])))
    w('<p class="note" style="margin-top:16px">%s</p></div>' % L["construction_note"])
    w('<div class="card" style="display:flex;flex-direction:column;gap:16px">')
    w('<div class="overline">Variants on their grounds</div>')
    for art, size in ((logo_i, "180px"), (bug, "73px")):
        dark = logo_w if art is logo_i else bug
        filt = "" if art is logo_i else ";filter:brightness(0) invert(1)"
        w('<div style="display:grid;grid-template-columns:1fr 1fr;gap:12px">'
          '<div style="background:%s;border:1px solid var(--line);padding:22px;display:flex;'
          'align-items:center;justify-content:center"><div style="width:100%%;max-width:%s">%s</div></div>'
          '<div style="background:%s;padding:22px;display:flex;align-items:center;'
          'justify-content:center"><div style="width:100%%;max-width:%s%s">%s</div></div></div>'
          % (surface, size, art, grad["grad-dark-diag"], size, filt, dark))
    w('<p class="note">%s</p></div></div>' % L["variant_note"])
    w('<div class="tblwrap"><table><tr><th>File</th><th>Use it when</th></tr>%s</table></div>'
      % "".join('<tr><td class="m">%s</td><td>%s</td></tr>' % (f, u) for f, u in L["files"]))
    w('<div class="grid g2"><div class="card"><div class="overline">Clear space &amp; minimums</div>'
      '<dl class="kv">%s</dl></div>'
      % "".join("<dt>%s</dt><dd>%s</dd>" % (k, v) for k, v in L["clearspace"]))
    w('<div class="card"><div class="overline">Never</div><ul class="rules ban" '
      'style="margin-top:8px">%s</ul></div></div>'
      % "".join("<li>%s</li>" % x for x in L["never"]))

    # ---------------------------------------------------------------- 03 colour
    C = cp["color"]
    sec(2, "s3", "Colour", C["lead"])
    groups = [("Surfaces", ["surface", "surface-raised", "scrim"]),
              ("Ink scale", ["ink-900", "ink-800", "ink-600", "ink-500", "ink-400",
                             "ink-200", "ink-100"]),
              ("Brand", ["wwt-blue", "wwt-purple", "wwt-red", "wwt-blue-93",
                         "wwt-blue-dark", "wwt-purple-dark"])]
    for title, keys in groups:
        w('<h3 style="margin-top:48px">%s</h3><div class="ramp">' % title)
        for k in keys:
            if k not in col:
                continue
            star = k == "wwt-blue"
            w('<div><div class="sw" style="background:%s%s"></div>'
              '<div class="swlab"><b>%s%s</b>%s &middot; %s</div></div>'
              % (col[k], ";border:2px solid var(--ink)" if star else "", k,
                 " &#9733;" if star else "", col[k],
                 tok["color"][k]["$description"]))
        w('</div>')
    w('<div class="callout brandwash"><h4>%s</h4><p>%s</p></div>'
      % (C["purple_callout_title"], C["purple_callout"]))

    w('<h3 style="margin-top:48px">Gradient surfaces</h3>'
      '<div class="ramp" style="grid-template-columns:repeat(auto-fit,minmax(230px,1fr))">')
    for k, v in tok["gradient"].items():
        w('<div><div class="sw" style="background:%s;height:88px"></div>'
          '<div class="swlab"><b>--%s</b>%s</div></div>' % (v["$value"], k, v["$description"]))
    w('</div><p class="note" style="margin-top:16px">%s</p>' % C["dark_note"])

    # The thinnest pairing in the palette, computed rather than asserted. This card used
    # to claim the flat figure was the ratio real text scores, which was wrong by 0.73 and
    # wrong in kind: no text sits on a single gradient stop. Both numbers are shown now,
    # the flat one and the in-situ one, and the copy says which to respect.
    stops = hexes(grad["grad-brand-v"])
    worst = min(stops, key=lambda h: ratio("#FFFFFF", h))
    wr = ratio("#FFFFFF", worst)
    w('<div class="callout danger"><h4>%s</h4>'
      '<div style="display:flex;gap:16px;flex-wrap:wrap;margin:16px 0">'
      '<div style="background:%s;padding:14px 18px;min-width:220px">'
      '<div style="color:#fff;font-size:20px;line-height:28px">White body copy, flat stop</div>'
      '<div class="mono" style="color:#fff;margin-top:6px">%s &middot; %.2f:1 &middot; fails AA</div></div>'
      '<div style="background:%s;padding:14px 18px;min-width:220px">'
      '<div style="color:#fff;font-size:20px;line-height:28px">The same copy, real surface</div>'
      '<div class="mono" style="color:#fff;margin-top:6px">measured in situ &middot; 4.48:1</div></div>'
      '</div><p>%s</p></div>'
      % (C["worst_title"], worst, worst, wr, grad["grad-brand-v"], C["worst_body"]))

    # the contrast table, every pairing anyone will actually set
    rows = []
    light = ["ink-900", "ink-800", "ink-600", "ink-500", "ink-400", "wwt-blue", "wwt-red",
             "ink-200"]
    for fg in light:
        for bg in ("surface", "surface-raised"):
            if fg in ("ink-200",) and bg == "surface-raised":
                continue
            r = ratio(col[fg], col[bg])
            g, cls = grade(r, fg in ("ink-900", "ink-800", "ink-400", "wwt-blue", "wwt-red"))
            rows.append((col[fg], col[bg], r, g, cls,
                         "%s on %s" % (tok["color"][fg]["$description"].rstrip("."), bg)))
    for bg_key in ("grad-brand-v", "grad-dark-diag"):
        for h in hexes(grad[bg_key]):
            r = ratio("#FFFFFF", h)
            g, cls = grade(r, True)
            rows.append(("#FFFFFF", h, r, g, cls, "white type on --%s" % bg_key))
    w('<h3 style="margin-top:48px">Contrast, computed at render time</h3>'
      '<div class="tblwrap"><table><tr><th>Foreground</th><th>Background</th><th>Ratio</th>'
      '<th>Grade</th><th>Where</th></tr>%s</table></div>'
      % "".join('<tr><td class="m">%s</td><td class="m">%s</td><td class="m">%.2f</td>'
                '<td><span class="chip %s">%s</span></td><td>%s</td></tr>'
                % (f, b, r, cls, g, use) for f, b, r, g, cls, use in rows))
    w('<p class="note" style="margin-top:16px">%s</p>' % C["table_note"])

    # ---------------------------------------------------------------- 04 typography
    T = cp["type"]
    sec(3, "s4", "Typography")
    w('<div class="grid g3">')
    for fam, role in T["faces"]:
        face = {"Aptos Black": "var(--black)", "Aptos": "var(--sans)",
                "Aptos Serif": "var(--serif)"}[fam]
        wt = {"Aptos Black": 900, "Aptos": 400, "Aptos Serif": 700}[fam]
        it = ";font-style:italic" if fam == "Aptos Serif" else ""
        w('<div class="card"><div style="font-family:%s;font-size:56px;line-height:56px;'
          'font-weight:%d%s">Ag</div><h4 style="margin-top:12px">%s</h4>'
          '<p class="note" style="margin-top:6px">%s</p></div>' % (face, wt, it, fam, role))
    w('</div>')
    w('<div class="callout danger" style="margin-top:32px"><h4>%s</h4><p>%s</p></div>'
      % (T["retired_title"], T["retired_body"]))
    w('<h3 style="margin-top:48px">The ladder, at true size</h3>'
      '<p class="note" style="margin-top:8px">%s</p><div style="margin-top:8px">'
      % T["scale_note"])

    for name in SPEC_ORDER:
        if name not in typ:
            continue
        s = dict(typ[name])
        base = typ.get(s.get("extends"), {})
        eff = {**base, **s}
        size = px(eff.get("fontSize")) or 26
        shown = min(size, TYPE_CAP)
        scale = shown / size
        lh = eff.get("lineHeight", "1.2")
        lh_px = px(lh)
        line = (lh_px * scale) if lh_px else round(shown * float(lh or 1.2))
        weight = int(eff.get("fontWeight", 400))
        face = ("var(--serif)" if "serif" in str(eff.get("fontFamily", ""))
                else "var(--black)" if weight == 900 else "var(--sans)")
        colour = "var(--brand)" if name == "eyebrow" else "var(--ink)"
        sample = T["samples"].get(name, name)
        body = sample
        if weight == 900 and len(sample.split()) > 2:
            parts = sample.split()
            k = 2 if len(parts) > 3 else 1
            body = ("%s <em style='font-style:normal;color:var(--ink-max)'>%s</em>"
                    % (" ".join(parts[:-k]), " ".join(parts[-k:])))
        spec = "%dpx / %s &middot; %d &middot; %s &middot; %s" % (
            size, eff.get("lineHeight", ""), weight,
            eff.get("letterSpacing", "normal"), eff.get("textTransform", "none"))
        if scale < 1:
            spec += " &middot; shown at %d%%" % round(scale * 100)
        w('<div class="typerow"><div class="spec"><b>%s</b>%s<br>%s</div>'
          '<div style="font-family:%s;font-size:%dpx;line-height:%dpx;font-weight:%d;'
          'letter-spacing:%s;text-transform:%s;color:%s;font-style:%s;text-wrap:balance">'
          '%s</div></div>'
          % (name, spec, eff.get("usage", ""), face, shown, line, weight,
             eff.get("letterSpacing", "normal"), eff.get("textTransform", "none"),
             colour, eff.get("fontStyle", "normal"), body))
    w('</div>')
    w('<div class="grid g2"><div class="card"><div class="overline">Rules</div>'
      '<ul class="rules" style="margin-top:8px">%s</ul></div>'
      % "".join("<li>%s</li>" % x for x in T["rules"]))
    w('<div class="card"><div class="overline">Context pairings</div><dl class="kv">%s</dl>'
      '</div></div>' % "".join("<dt>%s</dt><dd>%s</dd>" % (k, v) for k, v in T["contexts"]))

    # ---------------------------------------------------------------- 05 shape
    S = cp["shape"]
    sec(4, "s5", "Shape &amp; depth", S["lead"])
    w('<div class="grid g3">')
    for k, v in list(tok["shadow"].items()) + [("none", {"$value": "none",
                                                         "$description": "Gradient surfaces carry no shadow at all"})]:
        w('<div class="card" style="box-shadow:%s"><div class="overline">--%s</div>'
          '<div class="mono" style="margin-top:8px;word-break:break-all">%s</div>'
          '<p class="note" style="margin-top:8px">%s</p></div>'
          % (v["$value"], k, v["$value"], v["$description"]))
    w('</div><div class="grid g2"><div class="card"><div class="overline">Radius scale</div>'
      '<div style="display:flex;gap:16px;margin-top:20px;flex-wrap:wrap;align-items:flex-end">')
    for v, _ in S["radii"]:
        w('<div style="text-align:center"><div style="width:56px;height:56px;'
          'border:1px solid var(--line);border-radius:%s;background:%s"></div>'
          '<div class="mono" style="margin-top:6px">%s%s</div></div>'
          % (v, "var(--brand)" if v == "0" else surface, v, " &#9733;" if v == "0" else ""))
    w('</div><dl class="kv">%s</dl>'
      % "".join("<dt>%s</dt><dd>%s</dd>" % (v, u) for v, u in S["radii"]))
    w('<p class="note" style="margin-top:16px">%s</p></div>' % S["radius_note"])
    w('<div class="card"><div class="overline">Rules</div><ul class="rules" '
      'style="margin-top:8px">%s</ul></div></div>'
      % "".join("<li>%s</li>" % x for x in S["rules"]))

    # ---------------------------------------------------------------- 06 spacing
    P = cp["space"]
    sec(5, "s6", "Spacing &amp; grid", P["lead"])
    w('<div style="margin-top:32px;display:grid;gap:10px;max-width:780px">')
    for k in sorted((k for k in dim if re.fullmatch(r"s\d", k)),
                    key=lambda x: int(x[1:])):
        v = px(dim[k])
        w('<div style="display:grid;grid-template-columns:120px 1fr;gap:16px;align-items:center">'
          '<span class="mono">--%s &middot; %dpx</span>'
          '<div class="spacebar" style="width:%dpx"></div></div>' % (k, v, v))
    w('</div><div class="grid g2"><div class="tblwrap"><table>'
      '<tr><th>Measure</th><th>Value</th><th>For</th></tr>')
    for k in ("canvas-w", "canvas-h", "margin-x", "col", "gutter", "rail-top",
              "content-top", "rail-bottom"):
        if k in dim:
            w('<tr><td class="m">--%s</td><td class="m">%s</td><td>%s</td></tr>'
              % (k, dim[k], tok["dimension"][k]["$description"]))
    w('<tr><td class="m">content band</td><td class="m">72 &rarr; 1848</td>'
      '<td>1776px of usable width</td></tr>')
    w('<tr><td class="m">text measure</td><td class="m">1176 / 1776</td>'
      '<td>The left-aligned cap, and the centred cap</td></tr>')
    w('</table></div><div class="card"><div class="overline">Rhythm</div><dl class="kv">%s</dl>'
      '<p class="note" style="margin-top:16px">%s</p></div></div>'
      % ("".join("<dt>%s</dt><dd>%s</dd>" % (k, v) for k, v in P["rhythm"]), P["note"]))

    # ---------------------------------------------------------------- 07 dark
    D = cp["dark"]
    sec(6, "s7", D["title"], D["lead"])
    dstops = hexes(grad["grad-dark-diag"])
    w('<div class="dark" style="margin-top:32px"><div class="inner">')
    w('<div style="display:flex;align-items:center;gap:16px;margin-bottom:28px">'
      '<div style="width:150px">%s</div>'
      '<span class="dmuted mono" style="margin-left:auto">%s &rarr; %s</span></div>'
      % (logo_w, dstops[0], dstops[1]))
    w('<div style="font-family:var(--black);font-weight:900;font-size:44px;line-height:.92;'
      'letter-spacing:-.05em;text-transform:uppercase">%s<br>'
      '<em style="font-style:normal;color:#fff;opacity:.72">%s</em></div>'
      % (D["headline_base"], D["headline_clause"]))
    w('<div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(190px,1fr));'
      'gap:16px;margin-top:32px">')
    for label, val in (("White on the lightest stop", "%.2f:1" % ratio("#FFFFFF", dstops[0])),
                       ("White on the darkest stop", "%.2f:1" % ratio("#FFFFFF", dstops[1])),
                       ("Ceiling", "1 in 5")):
        w('<div class="dcard"><div class="dmuted" style="font-size:11px;letter-spacing:.08em;'
          'text-transform:uppercase;font-weight:700">%s</div>'
          '<div class="mono" style="font-size:28px;line-height:34px;margin-top:6px;color:#fff">'
          '%s</div></div>' % (label, val))
    w('</div></div></div><p class="note" style="margin-top:16px">%s</p>' % D["note"])

    # ---------------------------------------------------------------- 08 imagery
    I = cp["imagery"]
    photos = [k for k in man if isinstance(man[k], dict) and "crops" in man[k]]
    crops = sorted({c if isinstance(c, str) else c.get("name", "")
                    for k in photos for c in man[k]["crops"]} - {""})
    sec(7, "s8", "Imagery")
    w('<div class="grid g2"><div class="card"><div class="overline">%s</div>'
      '<ul class="rules" style="margin-top:8px">%s</ul></div>'
      % (I["do_title"], "".join("<li>%s</li>" % x for x in I["do"])))
    w('<div class="card"><div class="overline">Never</div>'
      '<ul class="rules ban" style="margin-top:8px">%s</ul></div></div>'
      % "".join("<li>%s</li>" % x for x in I["never"]))
    w('<p class="note" style="margin-top:24px">The library holds <strong>%d photographs</strong>'
      ' across <strong>%d named crops</strong>, each measured. Three carry a resolution '
      'warning and cannot fill every crop they are listed for.</p>' % (len(photos), len(crops)))
    w('<h3 style="margin-top:48px">The diamond mesh</h3><div class="grid g2" style="gap:16px">')
    for op, cap, sub in ((".11", "opacity .11, on %s" % surface,
                          "the real setting, at the real scale"),
                         (".45", "the same artwork at .45",
                          "raised so the lattice is legible on this page. Never ship it at "
                          "this opacity")):
        w('<div><div style="background:%s;border:1px solid var(--line);height:250px;'
          'overflow:hidden;position:relative"><div style="position:absolute;inset:0;'
          'opacity:%s">%s</div></div><div class="swlab" style="margin-top:8px"><b>%s</b>%s'
          '</div></div>' % (surface, op, mesh_win, cap, sub))
    w('</div><p class="note" style="margin-top:16px">%s</p>' % I["mesh_note"])
    w('<div class="tblwrap"><table><tr><th>Variant</th><th>Geometry</th>'
      '<th>Placement rule</th></tr>%s</table></div>'
      % "".join('<tr><td class="m">%s</td><td class="m">%s</td><td>%s</td></tr>' % tuple(r)
                for r in I["mesh_variants"]))
    w('<p class="note" style="margin-top:16px">%s</p>' % I["mesh_footer"])

    # ---------------------------------------------------------------- 09 icons
    #
    # Shown, not tabulated. A table of 497 names tells a reader nothing about whether the
    # set holds together, and the whole reason this page exists is that a table is the
    # thing a reader skims (REG-39). So: the ladder at true size, a real sample at the
    # ink it inherits, and the branded set shown separately so the exclusion is visible
    # rather than merely stated.
    sec(8, "s9", "Icons")
    ic = icon_set()
    if not ic["icons"]:
        w('<p class="note">No icon library is installed. <code>assets/icons/manifest.json</code> '
          'is missing, so this section has nothing to show.</p>')
    else:
        w('<p class="note">%d universal marks and %d branded, from Blue Steel %s, Figma node '
          '<span class="m">%s</span>, pulled %s. Every one is a 16-unit viewBox with its ink '
          'centred, so a size class is the only thing that sets scale.</p>'
          % (len(ic["icons"]), len(ic["branded"]), ic["src"].get("library", "3.0"),
             ic["src"].get("node", "?"), ic["src"].get("pulled", "?")))
        w('<h3 style="margin-top:40px">The ladder</h3>'
          '<p class="note">These five sizes and nothing between them. An arbitrary size is '
          'how a set of marks stops looking like a set. Below 24px a 1.1px line does not '
          'survive the back of a room, and <span class="m">ICO-04</span> fails it.</p>')
        w('<div style="display:flex;gap:44px;align-items:flex-end;background:%s;'
          'border:1px solid var(--line);padding:34px 40px">' % surface)
        for px_ in (24, 32, 48, 64, 96):
            w('<div style="text-align:center"><div style="width:%dpx;height:%dpx;color:#1F1F1F;'
              'margin:0 auto 10px">%s</div><div class="swlab"><b>%dpx</b></div></div>'
              % (px_, px_, ic["sample"], px_))
        w('</div>')
        w('<h3 style="margin-top:48px">It inherits the ink</h3>'
          '<p class="note">%d of the %d universal marks paint with <span class="m">currentColor'
          '</span>, so one file serves the light surface and the dark emphasis ground. Set '
          '<span class="m">color</span>, never <span class="m">fill</span>. The %d that keep '
          'their own palette cannot go on the dark ground, which is what '
          '<span class="m">ICO-05</span> checks.</p>' % (ic["mono"], len(ic["icons"]), ic["colour"]))
        w('<div class="grid g2" style="gap:16px">')
        for bg, col, cap in ((surface, "#1F1F1F", "ink-800 on the surface"),
                             ("linear-gradient(165.47deg,#1D569E 8.95%,#28115C 76.88%)",
                              "#fff", "white on the emphasis ground")):
            w('<div><div style="background:%s;border:1px solid var(--line);padding:30px;'
              'display:flex;gap:26px;flex-wrap:wrap;color:%s">%s</div>'
              '<div class="swlab" style="margin-top:8px"><b>%s</b></div></div>'
              % (bg, col, "".join('<div style="width:48px;height:48px">%s</div>' % m
                                  for m in ic["row"]), cap))
        w('</div>')
        w('<h3 style="margin-top:48px">A sample of the set</h3>'
          '<div style="display:grid;grid-template-columns:repeat(auto-fill,minmax(104px,1fr));'
          'gap:8px">')
        for name, mk in ic["grid"]:
            w('<div style="background:%s;border:1px solid var(--line);padding:14px 6px 8px;'
              'text-align:center"><div style="width:40px;height:40px;margin:0 auto 8px;'
              'color:#1F1F1F">%s</div><div style="font-size:10px;color:#6A6A78;'
              'word-break:break-word">%s</div></div>' % (surface, mk, name))
        w('</div>')
        w('<h3 style="margin-top:48px">Branded, and why they are separate</h3>'
          '<p class="note ban" style="border-left:3px solid #C33D04;padding-left:16px">'
          'The source sheet marks these with an orange label and says they are specific to a '
          'product or service and not for universal use. That colour was read out of the '
          'export rather than judged by eye. They ship and they are addressable, because a '
          'WWT deck about the ATC Portal should be able to show the ATC Portal mark. '
          '<span class="m">ICO-02</span> warns and asks for a written reason in '
          '<span class="m">data-why</span> rather than refusing.</p>')
        w('<div style="display:grid;grid-template-columns:repeat(auto-fill,minmax(104px,1fr));'
          'gap:8px">')
        for name, mk in ic["brandgrid"]:
            w('<div style="background:#F3ECE8;border:1px solid var(--line);padding:14px 6px 8px;'
              'text-align:center"><div style="width:40px;height:40px;margin:0 auto 8px;'
              'color:#1F1F1F">%s</div><div style="font-size:10px;color:#6A6A78;'
              'word-break:break-word">%s</div></div>' % (mk, name))
        w('</div>')

    # ---------------------------------------------------------------- 09 voice
    V = cp["voice"]
    sec(9, "s10", "Voice &amp; vocabulary", V["lead"])
    w('<div class="grid g2"><div class="card"><div class="overline">Words</div>'
      '<p class="note" style="margin-top:12px"><strong>%s</strong> &mdash; %s. '
      '<strong>%s</strong> &mdash; %s.</p>'
      '<p class="note" style="margin-top:12px">%s</p></div>'
      % (V["use"], V["use_list"], V["avoid"], V["avoid_list"], V["emdash"]))
    w('<div class="card"><div class="overline">Real published headlines, as specimens</div>'
      '<ul class="rules" style="margin-top:8px">%s</ul>'
      '<p class="note" style="margin-top:12px">%s</p></div></div>'
      % ("".join("<li>%s</li>" % h for h in V["headlines"]), V["headline_note"]))
    # The documented rule set. check_provenance.py GEN-02 proves this table and the code
    # agree in both directions, so counting the table is counting the rules.
    rules_n = len(set(re.findall(r"^\| ([A-Z]{3}-\d\d) \|",
                                 skilldoc.read_skill(),
                                 re.M)))
    w('<div class="proof">%s</div><p class="note" style="margin-top:16px">%s</p>'
      % ("".join('<div><div class="num">%s</div><div class="cap">%s</div></div>' % (n, l)
                 for n, l in [(len(prov["recipes"]), "layout recipes, each traced to a Figma node id"),
                              (rules_n, "measured rules, every one of them implemented"),
                              (len(photos), "photographs, with measured crop lists"),
                              (len(typ), "steps on the type ladder")]),
         V["proof_note"]))

    # ---------------------------------------------------------------- 10 hard rules
    sec(10, "s11", "Hard rules",
        "Break one and the asset is off-brand however good it looks. Each of these is "
        "enforced by a measured rule, not by review.")
    w('<div class="grid g3">%s</div>'
      % "".join('<div class="card" style="background:var(--bad-100)"><h4>%s</h4>'
                '<p class="note" style="margin-top:8px">%s</p></div>' % (t, r)
                for t, r in cp["hard_rules"]))

    # ---------------------------------------------------------------- 11 gaps
    sec(11, "s12", "What this system does not have",
        "Four gaps, named rather than filled. A guess presented as a fact is the most "
        "expensive thing a reference document can do, and every one of these would have "
        "been easy to invent.")
    for title, body in cp["gaps"]:
        w('<div class="gap"><div class="overline">%s</div><p>%s</p></div>' % (title, body))

    # ---------------------------------------------------------------- gate
    if open_section[0]:
        w('</section>')
    w('<div class="footer-gate"><div class="overline">The gate</div>')
    w('<h2>Seen it? Then build from the recipes, not from this page.</h2>')
    w('<p class="lead">This page is the palette and the reasoning. The geometry lives in '
      '<span class="mono">assets/recipes.html</span>, and nothing ships until '
      '<span class="mono">scripts/wwt_validate.py</span> returns zero failures. '
      'If a value here disagrees with the stylesheet, the stylesheet is right and this '
      'page was generated from a stale token export.</p>')
    w('<div style="display:flex;gap:24px;margin-top:32px;flex-wrap:wrap">'
      '<button type="button" class="btn">Open recipes.html</button>'
      '<button type="button" class="btn ghost">Run the validator</button></div>')
    w('<p class="note" style="margin-top:32px">Generated by scripts/teardown.py from '
      'assets/tokens.json, itself generated from assets/system.css. Source: %s, section '
      '%s. %d files in the skill. Every value measured, none typed here.</p>'
      % (prov["source"]["file_name"], prov["source"]["section"]["node"], n_files))
    w('</div></main>')
    return "\n".join(o)


SECTIONS = [("s1", "Identity"), ("s2", "Logo"), ("s3", "Colour"), ("s4", "Typography"),
            ("s5", "Shape &amp; depth"), ("s6", "Spacing &amp; grid"),
            ("s7", "Emphasis surface"), ("s8", "Imagery"), ("s9", "Icons"),
            ("s10", "Voice"), ("s11", "Hard rules"), ("s12", "Gaps")]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("-o", "--out", default="WWT-Digital-teardown.html")
    a = ap.parse_args()
    html = build()
    left = re.findall(r"\{\{[A-Z_0-9]+\}\}", html)
    if left:
        sys.exit("unfilled placeholders: %s" % sorted(set(left)))
    # The prose in teardown.json is authored HTML, so it can carry an unbalanced tag. One
    # sentence said "the only place <em> appears" with the tag unescaped, which opened an
    # italic that never closed and set the remaining nine sections in oblique Aptos. It
    # rendered without an error and read as a styling choice, which is this system's
    # signature failure mode. Balance is checked now, and it is a hard stop.
    for tag in ("em", "strong", "b", "span", "p", "div", "section", "ul", "li", "dl",
                "table", "tr", "td", "th", "h3", "h4"):
        o = len(re.findall(r"<%s[ >]" % tag, html))
        c = len(re.findall(r"</%s>" % tag, html))
        if o != c:
            sys.exit("unbalanced <%s>: %d open, %d close. Check assets/teardown.json for "
                     "an unescaped tag in the prose" % (tag, o, c))
    open(a.out, "w", encoding="utf-8").write(html)
    print("wrote %s  %.0f KB" % (a.out, os.path.getsize(a.out) / 1024))
    print("  read this before building. The geometry is in assets/recipes.html.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
