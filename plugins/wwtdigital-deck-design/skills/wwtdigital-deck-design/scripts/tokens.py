#!/usr/bin/env python3
"""
Export the system's tokens for tools that are not this skill.

    python3 scripts/tokens.py            # write assets/tokens.json and assets/tokens.css
    python3 scripts/tokens.py --check    # exit 1 if either file is stale

Until v4.5 the only way to get a WWT value into anything else was to open `system.css` and
read it, which meant a person retyping a hex into Figma, a web team retyping it again, and
three copies of the palette drifting quietly apart. That is the same failure the recipes
file had: a second copy nobody compared to the first.

So these two files are GENERATED from `system.css` and never edited. `tokens.json` is the
machine-readable form, close enough to the W3C design-token draft to be imported by tools
that read it and plain enough to parse in six lines if not. `tokens.css` is the custom
properties alone, with none of the deck's layout rules, so a web page or an email template
can carry the brand's colour and type without inheriting a 1920 x 1080 slide system.

WHAT THEY DO NOT CARRY, and why it matters: a token file is a palette, not the system. It
has no slot assemblies, no recipe geometry, no density floors, no photography crops, no
export path, and no validator. A deck built from `tokens.css` alone will be on-palette and
off-system, which is most of the way to the 91-slide RFP failure. Anyone consuming these
files for a deck should be sent to `recipes.html` and the validator instead.

    system.css  ->  tokens.py  ->  tokens.json  ->  teardown.py
                                -> tokens.css   ->  other tools

`check_provenance.py` runs the staleness check, so an edit to `system.css` that is not
followed by a regeneration is a hard failure rather than a silent divergence.
"""
import json, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
CSS = os.path.join(ROOT, "assets", "system.css")
OUT_JSON = os.path.join(ROOT, "assets", "tokens.json")
OUT_CSS = os.path.join(ROOT, "assets", "tokens.css")

# Every token is read out of system.css. These tables carry only the things the stylesheet
# cannot state about itself: what a token is FOR, and the constraint on using it. A hex
# with no usage note is how #330072 ended up as a flat fill on somebody's panel.
USAGE = {
    "wwt-blue": ("color", "The signature, and the only flat brand fill in the system"),
    "wwt-purple": ("color", "Gradient terminus ONLY. There is no flat purple fill anywhere"),
    "wwt-red": ("color", "Motif only: the cover arrow and the stat direction mark. Never a "
                         "fill, never type"),
    "wwt-blue-93": ("color", "The accent at 93% opacity, for a surface over photography"),
    "wwt-blue-dark": ("color", "The dark emphasis ground's light stop. Its own measured "
                               "colour, not the brand blue darkened"),
    "wwt-purple-dark": ("color", "The dark emphasis ground's dark stop"),
    "ink-900": ("color", "The headline emphasis clause, and nothing else"),
    "ink-800": ("color", "Headline base"),
    "ink-600": ("color", "Body copy on a light ground"),
    "ink-500": ("color", "Caption and source line"),
    "ink-400": ("color", "Metadata and disabled. 3.65:1, large scale only"),
    "ink-200": ("color", "The mesh and hairlines. Decorative, 1.70:1"),
    "ink-100": ("color", "Rules and table strokes"),
    "surface": ("color", "The deck's default ground"),
    "surface-raised": ("color", "Panels and cards"),
    "scrim": ("color", "Flat wash over full-bleed photography"),
    "grad-brand-v": ("gradient", "The default gradient surface: statement panels, badges"),
    "grad-brand-v-93": ("gradient", "The same at 93%, for a surface over photography"),
    "grad-brand-diag": ("gradient", "Diagonal ground, measured at 164 degrees"),
    "grad-brand-h": ("gradient", "Horizontal, for a band"),
    "grad-dark-diag": ("gradient", "The dark emphasis ground. Capped at one slide in five"),
    "grad-photo-scrim": ("gradient", "Vertical scrim for type over a photograph"),
    "grad-bug": ("gradient", "The corner bug's stripe on a light ground"),
    "shadow-panel": ("shadow", "Every white panel and card"),
    "shadow-float": ("shadow", "An element lifted off a panel"),
    "canvas-w": ("dimension", "Canvas width. The system is not responsive"),
    "canvas-h": ("dimension", "Canvas height"),
    "margin-x": ("dimension", "The hard edge for all type and panels. Only photography and "
                              "the Brand X cross it"),
    "rail-top": ("dimension", "The running header band"),
    "rail-bottom": ("dimension", "Reserved for the corner bug"),
    "content-top": ("dimension", "First content zone below the rail"),
    "col": ("dimension", "One of twelve columns. A span is 126 + n x 150"),
    "gutter": ("dimension", "Column gutter. Pitch is 150"),
    "s1": ("dimension", "Spacing step 1"), "s2": ("dimension", "Spacing step 2"),
    "s3": ("dimension", "Spacing step 3"), "s4": ("dimension", "Spacing step 4"),
    "s5": ("dimension", "Spacing step 5"), "s6": ("dimension", "Spacing step 6"),
    "s7": ("dimension", "Spacing step 7, and the page margin"),
    "s8": ("dimension", "Spacing step 8"), "s9": ("dimension", "Spacing step 9"),
    "font-sans": ("fontFamily", "Aptos. Body, lede, caption, label, rail"),
    "font-serif": ("fontFamily", "Aptos Serif. Bold italic, pull quotes only"),
    "font-mono": ("fontFamily", "Specimen furniture in the reference document, not a deck face"),
}

# The heavy cuts are separate FAMILIES in Aptos, which is the single most expensive fact in
# this system, so the export states it rather than leaving a consumer to infer it from a
# weight number. See REG-01.
FAMILY_FOR_WEIGHT = {
    "400": "Aptos", "700": "Aptos", "900": "Aptos Black",
}

TYPE_USAGE = {
    "t-display1": "Cover headline, one line, nowrap",
    "t-display2": "Divider and statement",
    "t-h1-lg": "The long-headline step",
    "t-h1": "The workhorse headline",
    "t-h1--stmt": "Sentence-case statement. A modifier on t-h1, node 1839:55",
    "t-h2": "Secondary headline",
    "t-h3": "Panel and card title",
    "t-label": "Stat label, list label",
    "t-lede": "Standfirst under a headline",
    "t-body-l": "Body in a wide measure",
    "t-body": "The default body step",
    "t-body-s": "Body inside a card",
    "t-caption": "Figure caption",
    "t-source": "The source line under a chart",
    "t-micro": "Small bold label",
    "t-quote": "Pull quote. Aptos Serif bold italic",
    "t-coversub": "Cover subhead",
    "eyebrow": "The overline. WWT blue, uppercase, .16em tracking",
    "stat-hero": "A display-scale number standing in for a headline",
}


def read_css():
    return open(CSS, encoding="utf-8").read()


def parse_root(css):
    """Every custom property in the :root block, in source order.

    Comments are stripped FIRST. The stylesheet carries long explanatory comments between
    declarations and several of them contain colons and semicolons, so a naive line split
    reads prose as tokens."""
    m = re.search(r":root\s*\{(.*?)\n\}", css, re.S)
    if not m:
        sys.exit("could not find the :root block in system.css")
    body = re.sub(r"/\*.*?\*/", "", m.group(1), flags=re.S)
    out = []
    for name, value in re.findall(r"--([a-z0-9\-]+)\s*:\s*([^;]+);", body, re.I):
        out.append((name.strip(), " ".join(value.split())))
    if not out:
        sys.exit("the :root block parsed to zero tokens")
    return out


def parse_type(css):
    """The type ladder, read off the .t-* and .eyebrow rules.

    Only the declarations the ladder is defined by are exported. A rule that sets no
    font-size is not a step: `.t-h1.t-h1--stmt` is, because it overrides three properties
    of one, and it is exported as a step with its base named."""
    steps = []
    css_nc = re.sub(r"/\*.*?\*/", "", css, flags=re.S)
    for sel, body in re.findall(r"\n(\.t-[a-z0-9\-]+(?:\.t-[a-z0-9\-]+)?|\.eyebrow|\.stat-hero)"
                                r"\s*\{([^}]*)\}", css_nc):
        d = dict(re.findall(r"([a-z\-]+)\s*:\s*([^;]+)", body))
        if "font-size" not in d and "--stmt" not in sel:
            continue
        name = sel.split(".")[-1].lstrip(".")
        base = None
        if sel.count(".") > 1:
            base = sel.split(".")[1]
        step = {"name": name, "usage": TYPE_USAGE.get(name, "")}
        if base:
            step["extends"] = base
        for k, out in (("font-size", "fontSize"), ("line-height", "lineHeight"),
                       ("font-weight", "fontWeight"), ("letter-spacing", "letterSpacing"),
                       ("text-transform", "textTransform"), ("font-family", "fontFamily"),
                       ("font-style", "fontStyle"), ("color", "color")):
            if k in d:
                step[out] = d[k].strip()
        w = step.get("fontWeight")
        if w in FAMILY_FOR_WEIGHT and "fontFamily" not in step:
            step["realFamily"] = FAMILY_FOR_WEIGHT[w]
        steps.append(step)
    if not steps:
        sys.exit("the type ladder parsed to zero steps")
    return steps


def version():
    p = os.path.join(ROOT, "SKILL.md")
    m = re.search(r"v(\d+\.\d+)", open(p, encoding="utf-8").read()[:4000])
    return m.group(1) if m else "unknown"


def build():
    css = read_css()
    root = parse_root(css)
    steps = parse_type(css)
    prov = {}
    pp = os.path.join(ROOT, "assets", "provenance.json")
    if os.path.exists(pp):
        prov = json.load(open(pp, encoding="utf-8"))

    doc = {
        "$schema": "https://design-tokens.github.io/community-group/format/",
        "$description":
            "WWTDigital presentation design system, token export. GENERATED by "
            "scripts/tokens.py from assets/system.css; do not edit. Every value was "
            "measured off a Figma node before it entered the stylesheet. This file is a "
            "palette, not the system: it carries no layout, no recipe geometry, no density "
            "rules and no validator, so a deck built from it alone will be on-palette and "
            "off-system. For a deck, use assets/recipes.html and scripts/wwt_validate.py.",
        "$version": version(),
        "$source": prov.get("source", {}),
        "color": {}, "gradient": {}, "shadow": {}, "dimension": {}, "fontFamily": {},
        "typography": {},
        "$unexported": [],
    }
    for name, value in root:
        kind, usage = USAGE.get(name, (None, None))
        if kind is None:
            doc["$unexported"].append(name)
            continue
        doc[kind][name] = {"$value": value, "$type": kind, "$description": usage}
    for s in steps:
        doc["typography"][s.pop("name")] = {"$type": "typography", "$value": s}

    doc["$notes"] = {
        "aptosFamilies":
            "Aptos ships its heavy cuts as separate FAMILIES. font-family:'Aptos' with "
            "font-weight:900 finds nothing and the browser fakes a bold from Bold, which "
            "renders every headline light and changes its measure. Each typography step "
            "carries realFamily for this reason. Aptos Narrow was removed at v2.0: the "
            "token and both files are gone.",
        "contrast":
            "White body copy on the light end of --grad-brand-v measures 3.75:1 and fails "
            "AA at body size. It clears large scale, so a 96px white headline on the same "
            "surface is fine. Type over photography is not fixed at all: it is sampled from "
            "the rendered backdrop per slide.",
        "caseAndGradients":
            "Headlines are uppercase and colour is carried by gradients rather than by a "
            "palette. Both are deliberate and both contradict the usual house rules of "
            "general-purpose brand-kit tooling. Do not normalise them away.",
    }
    js = json.dumps(doc, indent=2, ensure_ascii=False) + "\n"

    lines = [
        "/* ============================================================",
        "   WWT DIGITAL DESIGN SYSTEM  ·  tokens.css  ·  v%s" % doc["$version"],
        "",
        "   GENERATED by scripts/tokens.py from assets/system.css. Do not edit.",
        "",
        "   The custom properties alone, with none of the deck's layout rules, so a web",
        "   page, an email template or a Figma import can carry the brand's colour and type",
        "   without inheriting a 1920 x 1080 slide system.",
        "",
        "   This is a palette, not the system. No slots, no recipe geometry, no density",
        "   floors, no photography crops, no export path, no validator. A deck built from",
        "   this file alone will be on-palette and off-system.",
        "",
        "   Aptos ships its heavy cuts as SEPARATE FAMILIES: use font-family:'Aptos Black'",
        "   for 900, never font-family:'Aptos';font-weight:900.",
        "   ============================================================ */",
        ":root{",
    ]
    for name, value in root:
        kind, usage = USAGE.get(name, (None, None))
        note = ("  /* %s */" % usage) if usage else ""
        lines.append("  --%s:%s;%s" % (name, value, note))
    lines.append("}")
    lines.append("")
    lines.append("/* The type ladder. Sizes are canvas pixels on 1920 x 1080; scale them")
    lines.append("   proportionally for any other surface rather than picking new numbers. */")
    for step in parse_type(css):
        name = step["name"]
        decls = []
        for k, css_k in (("fontFamily", "font-family"), ("fontSize", "font-size"),
                         ("lineHeight", "line-height"), ("fontWeight", "font-weight"),
                         ("letterSpacing", "letter-spacing"),
                         ("textTransform", "text-transform"), ("fontStyle", "font-style"),
                         ("color", "color")):
            if k in step:
                decls.append("%s:%s" % (css_k, step[k]))
        if "realFamily" in step and "fontFamily" not in step:
            decls.insert(0, "font-family:'%s'" % step["realFamily"])
        # A variant selector is doubled so it wins on specificity rather than on source
        # order. Equal specificity loses, which is REG-08 and has cost a revision before.
        sel = ".%s.%s" % (step["extends"], name) if "extends" in step else ".%s" % name
        lines.append("%s{%s}%s" % (sel, ";".join(decls),
                                    ("  /* %s */" % step["usage"]) if step["usage"] else ""))
    cs = "\n".join(lines) + "\n"
    return js, cs


def main():
    js, cs = build()
    check = "--check" in sys.argv
    stale = []
    for path, text in ((OUT_JSON, js), (OUT_CSS, cs)):
        cur = open(path, encoding="utf-8").read() if os.path.exists(path) else None
        if cur != text:
            stale.append(os.path.basename(path))
            if not check:
                open(path, "w", encoding="utf-8").write(text)
    if check:
        if stale:
            print("STALE: %s no longer match system.css. Run scripts/tokens.py"
                  % ", ".join(stale))
            return 1
        print("tokens.json and tokens.css are current")
        return 0
    doc = json.loads(js)
    print("wrote assets/tokens.json and assets/tokens.css")
    print("  %d colours, %d gradients, %d dimensions, %d type steps"
          % (len(doc["color"]), len(doc["gradient"]), len(doc["dimension"]),
             len(doc["typography"])))
    if doc["$unexported"]:
        print("  not exported, no usage note on record: %s"
              % ", ".join(doc["$unexported"]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
