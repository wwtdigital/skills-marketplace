#!/usr/bin/env python3
"""
Report what this machine can actually do with the WWT design system.

    python3 scripts/doctor.py

Run this FIRST, before building anything. It exists because the difference between a good
result and a bad one from this system turned out to be mostly environmental, not
instructional. Two people can read the same SKILL.md and get very different decks, because
one of them can run the validator and the other cannot, and nothing told either of them
which one they were.

The output ends in one of three verdicts:

  ENFORCED       everything runs. The rules are real and the deck is gated.
  PARTIAL        the fast static lint runs, the rendering validator does not. Some rules
                 are real, most are not, and you have to say so in your handoff.
  DOCUMENTATION  nothing runs. You have a stylesheet and a reference document. That is
                 useful, but do not describe the output as validated.

Exit code is 0 for ENFORCED, 1 for PARTIAL, 2 for DOCUMENTATION, so a hook or a CI step can
branch on it.
"""
import importlib, json, os, shutil, subprocess, sys

import brand_assets

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)

OK, WARN, BAD = "ok", "warn", "bad"
# The plugin's setup script installs everything into a private Python, so there is one fix
# for every missing package and nobody has to know what pip is.
SETUP = ("run the one-time setup: sh setup/setup.sh (Windows: "
         "powershell -ExecutionPolicy Bypass -File setup\\setup.ps1)")
rows = []


def add(name, state, detail, fix=""):
    rows.append((name, state, detail, fix))


def check_python():
    v = sys.version_info
    add("Python", OK if v >= (3, 8) else BAD,
        "%d.%d.%d" % (v.major, v.minor, v.micro),
        "" if v >= (3, 8) else "3.8 or newer is needed")


def check_module(mod, label, why, needed_for):
    try:
        m = importlib.import_module(mod)
        ver = getattr(m, "__version__", "")
        add(label, OK, ("%s %s" % (label, ver)).strip(), "")
        return True
    except Exception:
        add(label, BAD, "not installed", "%s   (needed for %s)" % (SETUP, needed_for))
        return False


def check_chromium():
    """Launch it. Importing playwright proves nothing; the launch is what fails."""
    try:
        from playwright.sync_api import sync_playwright
        from browser import launch
    except Exception:
        add("Chromium", BAD, "playwright not installed",
            SETUP)
        return False
    try:
        with sync_playwright() as p:
            b = launch(p)
            ver = b.version
            b.close()
        add("Chromium", OK, "launches, %s" % ver, "")
        return True
    except Exception as e:
        msg = str(e)
        fix = "install Google Chrome or Microsoft Edge, or " + SETUP
        if "libXdamage" in msg or "shared libraries" in msg:
            fix = ("system libraries are missing. On a sandbox without apt, fetch the .deb "
                   "files for libxdamage1, libxext6, libxfixes3, libxrandr2, libgbm1, "
                   "libxkbcommon0, libpango, libcairo2, libasound2, extract them locally and "
                   "point LD_LIBRARY_PATH at the extracted lib directory")
        add("Chromium", BAD, msg.strip().split("\n")[0][:88], fix)
        return False


def check_binary(name, label, why):
    p = shutil.which(name)
    if p:
        add(label, OK, p, "")
        return True
    add(label, WARN, "not on PATH", why)
    return False


def check_figma():
    """Look for a configured Figma MCP. Presence of tools is what matters, and this script
    cannot see the host's tool list, so report the plugin config instead and be honest."""
    cfg = os.path.join(os.path.dirname(ROOT), ".mcp.json")
    alt = os.path.join(ROOT, "..", "..", ".mcp.json")
    for c in (cfg, alt):
        if os.path.exists(c):
            try:
                servers = json.load(open(c)).get("mcpServers", {})
            except Exception:
                servers = {}
            if any("figma" in k.lower() for k in servers):
                add("Figma MCP", WARN, "declared in the plugin's .mcp.json",
                    "confirm the Figma desktop app is running with Dev Mode MCP enabled, "
                    "then check the tool list in your session for get_design_context")
                return
    add("Figma MCP", WARN, "cannot be detected from a script",
        "check your session's tool list for get_design_context. Without it you may NOT "
        "invent geometry: copy it from assets/recipes.html only")


def check_assets():
    need = [("assets/system.css", "the stylesheet"),
            ("assets/recipes.html", "the twenty recipes"),
            ("assets/tokens.json", "the token export"),
            ("assets/teardown.json", "the teardown's prose"),
            ("scripts/teardown.py", "the teardown renderer"),
            ("scripts/tokens.py", "the token generator"),
            ("assets/manifest.json", "the photography library"),
            ("assets/export", "baked decoration for PPTX"),
            ("scripts/wwt_validate.py", "the validator"),
            ("scripts/lint_source.py", "the static lint"),
            ("scripts/inline_assets.py", "the asset resolver"),
            ("scripts/export_pptx.py", "the PPTX exporter"),
            ("scripts/verify_pptx.py", "the PPTX verifier")]
    missing = [(p, d) for p, d in need if not os.path.exists(os.path.join(ROOT, p))]
    if missing:
        add("Skill assets", BAD, "%d missing: %s" % (len(missing), ", ".join(p for p, _ in missing)),
            "the skill is incomplete; reinstall it")
        return False
    n = 0
    try:
        n = len(json.load(open(os.path.join(ROOT, "assets", "manifest.json"))))
    except Exception:
        pass
    add("Skill assets", OK, "complete, %d photographs in the library" % n, "")
    return True


def check_brand():
    """The Aptos faces are Microsoft's and the plugin does not ship them. Without them
    nothing can be built, so this is a blocker, not a warning."""
    fonts = {f: brand_assets.font_path(f) for f in brand_assets.CORE}
    missing = [f for f, p in fonts.items() if not p]
    if missing:
        add("Aptos", BAD, "missing: " + ", ".join(missing),
            "install from %s, or see python3 scripts/brand_assets.py" % brand_assets.FONT_DOWNLOAD)
    else:
        where = os.path.dirname(fonts["Aptos"])
        add("Aptos", OK, "five sans cuts, from " + where, "")
    if brand_assets.font_path(brand_assets.SERIF):
        add("Aptos Serif", OK, "found", "")
    else:
        add("Aptos Serif", WARN, "missing, needed only for pull quotes",
            "install the Aptos family from " + brand_assets.FONT_DOWNLOAD)
    return not missing


def main():
    print("\nWWT design system doctor")
    print("  skill at %s\n" % ROOT)

    check_python()
    assets = check_assets()
    brand = check_brand()
    add("Static lint", OK, "runs anywhere Python runs, no dependencies", "")
    have_pw = check_chromium()
    have_pil = check_module("PIL", "Pillow", "pillow", "contrast sampling and baked assets")
    have_np = check_module("numpy", "numpy", "numpy", "luminance measurement")
    have_ft = check_module("fontTools", "fontTools", "fonttools brotli", "font metrics and embedding")
    have_pptx = check_module("pptx", "python-pptx", "python-pptx", "PPTX export")
    check_binary("soffice", "LibreOffice", "optional: renders a PPTX back to an image for eyeballing")
    check_figma()

    w = max(len(r[0]) for r in rows)
    mark = {OK: "  ok  ", WARN: " warn ", BAD: " MISS "}
    for name, state, detail, fix in rows:
        print("  [%s] %-*s %s" % (mark[state], w, name, detail))
        if fix:
            print("           %s%s" % (" " * w, fix))

    full = assets and brand and have_pw and have_pil and have_np
    print()
    if not brand:
        print("  BLOCKED: the Aptos fonts are missing (row above), so")
        print("  inline_assets.py will refuse to build a deck. Fix those first.")
        print()
    if full:
        verdict, code = "ENFORCED", 0
        print("  VERDICT: ENFORCED")
        print("  Everything runs. wwt_validate.py gates the deck, selftest.py proves the rules")
        print("  still catch gaming, and export_pptx.py plus verify_pptx.py gate the PPTX.")
        if not (have_pptx and have_ft):
            print("  PPTX export needs python-pptx and fonttools; HTML is unaffected.")
    elif assets:
        verdict, code = "PARTIAL", 1
        print("  VERDICT: PARTIAL")
        print("  The static lint runs, so continuation slides, placeholder copy, the inverted")
        print("  panel, an off-axis centred headline, a nested mesh and a ragged side-by-side")
        print("  set are all caught. NOT caught: contrast, rendered measure, widows, ink")
        print("  coverage, content substance, photography share, architecture diversity.")
        print("  Say so when you hand the deck over. Do not call it validated.")
    else:
        verdict, code = "DOCUMENTATION", 2
        print("  VERDICT: DOCUMENTATION ONLY")
        print("  You have a stylesheet and a reference document. Useful, but nothing is")
        print("  being checked. Do not describe the output as validated.")
    # The teardown runs on the standard library alone, so it works at every rung. Say so,
    # because the one thing a builder should do before anything else is look at the system,
    # and on a DOCUMENTATION-only machine it is the only thing that still works.
    print("  Before your first deck, whatever the verdict above:")
    print("    python3 scripts/teardown.py -o WWT-teardown.html   # then open it")
    print("  Standard library only, so it renders here. Two decks came back wrong from")
    print("  builders who had the skill and had never seen the system.")
    print()
    if not full:
        print("  To get to ENFORCED:")
        print("    " + SETUP)
        print()
    return code


if __name__ == "__main__":
    sys.exit(main())
