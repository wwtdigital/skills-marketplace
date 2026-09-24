#!/usr/bin/env python3
"""
Build decks that try to pass the rules while doing no design, and prove each one fails.

    python3 scripts/gaming_fixtures.py --out /tmp/fx

Every presence rule can in principle be satisfied by adding the thing and doing nothing
else. This script is the adversary. It writes one deck per gaming move, then the caller
runs wwt_validate.py over each and checks the expected rule fired.

The moves, and the rule that has to catch each:

  empty_panel     eight slides bulked out with one enormous EMPTY panel      DEN-06 / DEN-07
  thumbnail       a 120 x 90 photograph on a quarter of the slides           IMG-05
  frontload       the photography quota met on the first slides, then none   IMG-06
  mesh_only       a mesh added and nothing else designed                     DEN-06 / DEN-07
  role_shop       thin content slides relabelled as statements               SEQ-04
  nudge           one architecture, headline y nudged 20px per slide          SEQ-02
  cont            content spilled onto "(cont.)" slides                      SEQ-05
  twins           the same slide shipped twice                               SEQ-03
  white_cards     grey cards on a white ground, the inverted elevation       COL-07
  offaxis         a centred headline in a 1776 box at left:0                 TYP-11
  banner          a left-aligned headline run to 1600px                      TYP-04
  ragged          two side-by-side cards with unequal bottoms                GEO-06
  placeholder     Lorem ipsum shipped as body copy                           DEN-08
  dark_overuse    the dark emphasis ground on most of the deck                PAT-09
  dark_run        two dark emphasis slides back to back                       PAT-09

A rule nobody has watched fail is a rule nobody has tested.
"""
import argparse, os

HEAD = """<!DOCTYPE html><html lang="en"><head><meta charset="utf-8">
<title>fixture</title>{FONTS}<style>{CSS}</style></head><body><div class="deck">"""
TAIL = "</div></body></html>"

RAIL = '<div class="rail"><b>Fixture</b> | 2026</div>'
BUG = ('<div class="bug"><div class="stripe"></div><div class="mark">'
       '<img src="{{BUG_MARK}}" alt="" aria-hidden="true"></div></div>')
MESH = '<div class="mesh mesh--h"></div>'
# px units matter: without them the box sizes to the image's intrinsic dimensions, so the
# "thumbnail" fixture rendered a full-bleed photograph and tested nothing.
PHOTO = ('<div class="media abs off-grid" style="left:%dpx;top:%dpx;width:%dpx;height:%dpx">'
         '<img src="{{IMG_keyboard}}" alt="A keyboard on a desk"></div>')

# enough real copy that a legitimate slide clears DEN-07, so each fixture isolates the
# single move it is testing rather than failing for want of words
BODY = ('<p class="t-body ink-mid abs" style="left:72px;top:%dpx;width:1176px">Migrate the right '
        'workloads, modernize the rest, and prove the dollar story every quarter so the '
        'programme keeps its funding through the second year and beyond, with a named owner '
        'on every workstream and a readout the finance team can actually&nbsp;reconcile.</p>')


def slide(inner, ground="g-light", role="content", extra=""):
    return ('<div class="stage"><div data-role="%s" class="slide %s"%s>%s</div></div>'
            % (role, ground, extra, inner))


def head_h1(text, top=140, left=72, width=1176, align=None):
    a = ";text-align:center" if align == "center" else ""
    return ('<h1 class="t-h1 abs" style="left:%dpx;top:%dpx;width:%dpx%s">%s</h1>'
            % (left, top, width, a, text))


def real_slide(i, top=140):
    """A slide that should pass everything, used as filler."""
    return slide(MESH + RAIL + head_h1("Real slide number %d" % i, top)
                 + (BODY % 380)
                 # Sized to their content. At 300px tall holding two short lines these were
                 # 45% dead space, which DEN-09 correctly failed on the negative control.
                 + '<div class="panel abs" style="left:72px;top:640px;width:876px;height:224px;padding:24px">'
                   '<p class="t-label">Named owner</p><p class="t-body-s ink-mid">One accountable team '
                   'from strategy through run, with a decision in ninety days.</p></div>'
                 + '<div class="panel abs" style="left:972px;top:640px;width:876px;height:224px;padding:24px">'
                   '<p class="t-label">Proof before procurement</p><p class="t-body-s ink-mid">Built in '
                   'the lab, measured, and signed off before anybody raises a purchase&nbsp;order.</p></div>'
                 + BUG)


FIXTURES = {}
# attributes to put on the deck wrapper, for fixtures whose gaming move IS an attribute
WRAPPER = {}


# The negative control, and the most important fixture here. Rules that fail everything are
# not rules, they are a broken build. This deck is legitimate work: varied architecture,
# photography above the floor, a background device on every light ground, real copy. It has
# to come back clean, and if it ever stops doing so a threshold has drifted too tight.
def control():
    out = []
    out.append(slide(  # cover
        '<div class="media media--bleed scrim-flat"><img src="{{IMG_gaze-rb}}" '
        'alt="A portrait in red and blue light"></div><div class="brandx-x"></div>'
        '<div class="lockup"><img src="{{LOGO_WHITE}}" alt="World Wide Technology"></div>'
        '<h1 class="t-display1 white abs" style="left:201px;top:540px;width:1453px">Make a new'
        '<br>world&nbsp;happen.</h1>'
        '<p class="t-coversub white abs" style="left:212px;top:914px;width:1160px">Strategy to '
        'execution, and everything in&nbsp;between.</p>', ground="", role="cover"))
    out.append(slide(  # statement, gradient ground
        RAIL.replace('class="rail"', 'class="rail on-photo"')
        + '<h1 class="t-h1-lg white abs" style="left:72px;top:330px;width:1500px">Everyone is '
          'buying AI.<br>Fewer than 1 in 4 is<br>getting <em>paid back.</em></h1>'
        + '<p class="t-lede white abs" style="left:72px;top:790px;width:1176px">The difference is '
          'whether you bought a tool or built a&nbsp;system.</p>'
        + BUG.replace('class="bug"', 'class="bug bug--dark"'),   # gradient ground (MRK-05)
        ground="g-grad-diag", role="statement"))
    out.append(real_slide(2))                              # cards
    out.append(slide(  # photo left, prose right
        MESH + RAIL
        + PHOTO % (0, 0, 1103, 1080)   # the declared half crop, ratio 1.02
        + '<h1 class="t-h2 abs" style="left:1122px;top:180px;width:726px">Prove it in the&nbsp;lab.</h1>'
        + (BODY % 420).replace('left:72px', 'left:1122px').replace('width:1176px', 'width:726px')
        + '<div class="panel abs" style="left:1122px;top:700px;width:726px;height:216px;padding:24px">'
          '<p class="t-label">One accountable team</p><p class="t-body-s ink-mid">From strategy '
          'through run, with a named owner on every workstream and a readout finance can '
          'reconcile.</p></div>' + BUG))
    out.append(slide(  # stats
        MESH.replace('mesh--h', 'mesh--diag') + RAIL
        + '<h1 class="t-h1 abs" style="left:72px;top:140px;width:1176px">Investment is up.'
          '<br><em>Value is&nbsp;not.</em></h1>'
        + '<div class="stat abs" style="left:72px;top:460px;width:420px"><p class="val">82%</p>'
          '<p class="lab">Increasing spend</p><p class="note">Executives adding budget to AI '
          'programmes this year, across every sector we serve.</p></div>'
        + '<div class="stat abs" style="left:522px;top:460px;width:420px"><p class="val">23%</p>'
          '<p class="lab">Seeing value</p><p class="note">Reporting widespread, sustained value, '
          'down from thirty-two percent earlier the same year.</p></div>'
        + '<div class="stat abs" style="left:972px;top:460px;width:420px"><p class="val">25%</p>'
          '<p class="lab">In production</p><p class="note">Have moved forty percent or more of '
          'their pilots into production today.</p></div>' + BUG, role="data"))
    out.append(slide(  # table, exempt from PAT-08
        RAIL + '<h1 class="t-h1 abs" style="left:72px;top:140px;width:1176px">Where the work '
                '<em>actually&nbsp;lands.</em></h1>'
        + '<table class="deck abs" style="left:72px;top:400px;width:1776px">'
          '<thead><tr><th>Workstream</th><th>Owner</th><th>Proof</th></tr></thead><tbody>'
          '<tr><td>Discovery and assessment</td><td>WWT Consulting</td><td>Baseline scorecard</td></tr>'
          '<tr><td>Data foundations</td><td>Joint team</td><td>One representative dataset</td></tr>'
          '<tr><td>Production landing zone</td><td>WWT Engineering</td><td>Guardrails signed off</td></tr>'
          '</tbody></table>' + BUG, role="data"))
    out.append(slide(  # photo band, closing
        '<div class="media media--bleed"><img src="{{IMG_twin-rb}}" alt="Two mirrored profiles in '
        'red and blue light"></div>'
        '<div class="scrim-wash" style="inset:0;background:linear-gradient(90deg,rgba(0,0,0,.62),'
        'rgba(0,0,0,.28) 52%,transparent 82%)"></div>'
        '<div class="lockup"><img src="{{LOGO_WHITE}}" alt="World Wide Technology"></div>'
        '<h1 class="t-display2 white abs" style="left:72px;top:640px;width:1100px">Thank you!</h1>'
        '<p class="t-lede white abs" style="left:72px;top:850px;width:820px">One accountable team, '
        'from strategy through run. Let us pick the first hard&nbsp;problem.</p>',
        ground="", role="closing"))
    return out


FIXTURES["control"] = control


def fx(name):
    def d(f):
        FIXTURES[name] = f
        return f
    return d


@fx("empty_panel")
def _empty_panel():
    """One enormous EMPTY panel per slide. Covers 60% of the canvas and says nothing."""
    out = []
    for i in range(8):
        out.append(slide(MESH + RAIL + head_h1("Bulked out slide %d" % i)
                         + '<div class="panel abs" style="left:72px;top:340px;width:1776px;height:620px"></div>'
                         + BUG))
    return out


@fx("mesh_only")
def _mesh_only():
    """A mesh added to satisfy PAT-08 and nothing else designed."""
    return [slide(MESH + RAIL + head_h1("Mesh and nothing else %d" % i) + BUG) for i in range(8)]


@fx("thumbnail")
def _thumbnail():
    out = []
    for i in range(8):
        s = MESH + RAIL + head_h1("Thumbnail quota %d" % i) + (BODY % 380)
        if i % 4 == 0:
            s += PHOTO % (1600, 820, 120, 90)      # 0.5% of the canvas
        out.append(slide(s + BUG))
    return out


@fx("frontload")
def _frontload():
    out = []
    for i in range(14):
        s = MESH + RAIL + head_h1("Front-loaded %d" % i) + (BODY % 380)
        if i < 4:
            s += PHOTO % (72, 620, 876, 380)
        out.append(slide(s + BUG))
    return out


@fx("role_shop")
def _role_shop():
    """Thin slides relabelled as statements to reach the lower substance bar."""
    out = [real_slide(0), real_slide(1)]
    for i in range(8):
        out.append(slide(MESH + RAIL + head_h1("Relabelled %d" % i, 380) + BUG,
                         role="statement"))
    return out


@fx("nudge")
def _nudge():
    """One architecture, headline nudged 20px each time to defeat an exact signature."""
    return [real_slide(i, top=140 + i * 20) for i in range(10)]


@fx("cont")
def _cont():
    out = [real_slide(0)]
    out.append(slide(MESH + RAIL + head_h1("Technology partnerships") + (BODY % 380) + BUG))
    out.append(slide(MESH + RAIL + head_h1("Technology partnerships (cont.)") + (BODY % 380) + BUG))
    out.append(real_slide(3))
    out.append(real_slide(4))
    return out


@fx("twins")
def _twins():
    s = real_slide(1)
    return [real_slide(0), s, real_slide(2), s, real_slide(4)]


@fx("white_cards")
def _white_cards():
    """Grey cards on a white ground: the inverted elevation, both colours legal tokens."""
    out = []
    for i in range(5):
        out.append(slide(RAIL + head_h1("Inverted elevation %d" % i) + (BODY % 380)
                         + '<div class="panel abs" style="left:72px;top:640px;width:876px;'
                           'height:300px;padding:24px;background:#F6F6F6"><p class="t-label">'
                           'A recessed well</p><p class="t-body-s ink-mid">Grey on white reads as a '
                           'hole in the page rather than a card lifted off it.</p></div>' + BUG,
                         ground="g-white"))
    return out


@fx("offaxis")
def _offaxis():
    """A 1776 box at left:0, which centres on 888 instead of 960."""
    out = [real_slide(0)]
    for i in range(4):
        out.append(slide(MESH + RAIL
                         + head_h1("Centred on nothing %d" % i, left=0, width=1776, align="center")
                         + (BODY % 380) + BUG))
    return out


@fx("banner")
def _banner():
    out = [real_slide(0)]
    for i in range(4):
        out.append(slide(MESH + RAIL
                         + head_h1("A left aligned headline run all the way out to sixteen hundred "
                                   "pixels wide %d" % i, width=1700)
                         + (BODY % 380) + BUG))
    return out


@fx("ragged")
def _ragged():
    out = [real_slide(0)]
    for i in range(4):
        out.append(slide(
            MESH + RAIL + head_h1("Unequal bottoms %d" % i) + (BODY % 340)
            + '<div class="panel abs" style="left:72px;top:600px;width:876px;height:240px;padding:24px">'
              '<p class="t-label">Card A</p><p class="t-body-s ink-mid">Ends at 840.</p></div>'
            + '<div class="panel abs" style="left:972px;top:600px;width:876px;height:360px;padding:24px">'
              '<p class="t-label">Card B</p><p class="t-body-s ink-mid">Ends at 960, a hundred and '
              'twenty pixels lower, on a pair the eye reads as a set.</p></div>' + BUG))
    return out


@fx("dark_overuse")
def _dark_overuse():
    """The dark ground used because it looks good, which is how a ceiling gets gamed.

    Every other presence rule here is a floor and gets gamed by doing nothing. This one is a
    ceiling, so it gets gamed by doing the striking thing everywhere until it stops being
    striking.
    """
    out = []
    for i in range(10):
        dark = i % 2 == 0            # 5 of 10, way over one in five
        out.append(slide(
            ('<div class="mesh mesh--dark"></div>' if dark else MESH)
            + RAIL.replace('class="rail"', 'class="rail on-photo"' if dark else 'class="rail"')
            + head_h1("Emphasis everywhere %d" % i).replace('class="t-h1 abs"',
                                                            'class="t-h1 white abs"' if dark else 'class="t-h1 abs"')
            + (BODY % 380).replace('class="t-body ink-mid abs"',
                                   'class="t-body white abs"' if dark else 'class="t-body ink-mid abs"')
            + BUG, ground="g-dark" if dark else "g-light"))
    return out


@fx("dark_run")
def _dark_run():
    """Within the share, but two in a row, so neither is emphatic against anything."""
    out = [real_slide(0), real_slide(1)]
    for i in range(2):
        out.append(slide(
            '<div class="mesh mesh--dark"></div>'
            + RAIL.replace('class="rail"', 'class="rail on-photo"')
            + head_h1("Back to back %d" % i).replace('class="t-h1 abs"', 'class="t-h1 white abs"')
            + (BODY % 380).replace('class="t-body ink-mid abs"', 'class="t-body white abs"')
            + BUG, ground="g-dark"))
    out += [real_slide(4), real_slide(5), real_slide(6), real_slide(7)]
    return out


@fx("gallery_claim")
def _gallery_claim():
    """The cheapest move in the whole system: declare the deck a reference gallery.

    One attribute on the wrapper and the entire deck-level family stops applying. Density,
    substance, photography share, mesh share, the background-device rule, deck length, role
    share and consecutive sameness, all off, because the spec book legitimately needs that
    exemption and nothing checked whether the claim was true. These twelve slides are the
    thinnest thing the rule set can otherwise describe.
    """
    return [slide(RAIL + head_h1("Claimed exemption %d" % i) + BUG) for i in range(12)]


WRAPPER["gallery_claim"] = 'data-gallery="yes"'


@fx("spec_role")
def _spec_role():
    """Every slide labelled a documentation specimen.

    `data-role="spec"` meant "this is a figure in the spec book", and it dropped a slide out
    of the deck census and off the type and colour rules. Labelling the whole deck with it
    took the census under four, which returned out of the deck-level family before it ran a
    single rule. Same shape of hole as the gallery claim, different attribute.
    """
    return [slide(RAIL + head_h1("Specimen %d" % i) + BUG, role="spec") for i in range(12)]


@fx("false_build")
def _false_build():
    """The same slide twice, the second one declaring that it builds on the first.

    `data-builds-on` clears the page-style repeat rule on trust. The headline is identical,
    so nothing has been built on: it is the same slide with an attribute.
    """
    out = []
    for i in range(10):
        out.append(slide(RAIL + head_h1("One story, told once") + (BODY % 380) + BUG,
                         extra=' data-builds-on="prev"' if i else ""))
    return out


@fx("reuse_photo")
def _reuse_photo():
    """The photography quota met by using one frame over and over.

    Every photography rule was about whether an image is used well: the crop, the
    resolution, the scrim, the share, the gap. None asked whether it is the same image, so
    the cheapest way to clear IMG-05 and IMG-06 was one photograph on every slide, plus one
    slide carrying it twice.
    """
    out = []
    for i in range(10):
        s = MESH + RAIL + head_h1("One frame, ten times %d" % i) + (BODY % 380)
        s += PHOTO % (72, 560, 876, 420)
        if i == 3:
            s += PHOTO % (996, 560, 852, 420)     # and twice on one slide
        out.append(slide(s + BUG))
    return out


@fx("placeholder")
def _placeholder():
    out = [real_slide(0)]
    out.append(slide(MESH + RAIL + head_h1("Partnerships")
                     + '<p class="t-body ink-mid abs" style="left:72px;top:380px;width:1176px">'
                       'Lorem ipsum</p>' + BUG))
    out += [real_slide(2), real_slide(3), real_slide(4)]
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="/tmp/fx")
    ap.add_argument("--head", default=os.path.join(
        os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
        "..", "src", "head.html"))
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    src = open(os.path.abspath(a.head)).read()
    j = src.rindex("</style>")
    shared = src[:j]
    for name, fn in sorted(FIXTURES.items()):
        html = shared + "</style></head><body><div class='deck' %s>" % WRAPPER.get(name, "") \
               + "\n".join(fn()) + "</div></body></html>"
        p = os.path.join(a.out, name + ".raw.html")
        open(p, "w").write(html)
        print("  wrote", p)


if __name__ == "__main__":
    main()
