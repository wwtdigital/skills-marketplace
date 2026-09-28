"""
Import a third-party dependency, or say what to install and stop cleanly.

WHY THIS EXISTS.

Twenty-one imports of Playwright, Pillow, numpy, python-pptx and lxml sat unguarded
across six scripts. When a package was missing, the script died on a raw traceback:

    Traceback (most recent call last):
      File ".../wwt_validate.py", line 1214, in validate
        from playwright.sync_api import sync_playwright
    ModuleNotFoundError: No module named 'playwright'

`doctor.py` had handled this properly from the start, and `verify_pptx.py` in two places.
Everything else, including `wwt_validate.py`, crashed. That is the wrong way round: the
validator is the one script the contract says never to skip, so a missing package produced
a traceback from precisely the tool a non-technical person was told they must run.

A traceback is not a failure report. It does not say which package, does not say how to
install it, and reads as "this tool is broken" rather than "this machine is missing one
thing". The person who most needs the answer is the one least equipped to read a stack.

    from deps import need
    sync_playwright = need("playwright.sync_api", "sync_playwright")
    Image = need("PIL", "Image", pkg="pillow")

On success it returns the module or the named attribute. On failure it prints the package,
the install line, and the standing advice to run the doctor, then exits 3. Three rather
than 1, so a caller can tell "this machine is not set up" from "your deck has failures".
"""
import sys

EXIT_MISSING = 3

# import name -> (pip name, a clause completing "What stops: ...")
PACKAGES = {
    "playwright": ("playwright", "the validator, the exporter and the doctor cannot render"),
    "PIL": ("pillow", "crops, contrast plates and icon rasterising stop working"),
    "numpy": ("numpy", "contrast sampling and ink coverage cannot be measured"),
    "pptx": ("python-pptx", "PPTX export and verification stop working"),
    "lxml": ("lxml", "the PPTX XML cannot be written or read"),
    "fontTools": ("fonttools", "font name tables cannot be read and woff2 cannot be written"),
}

# Packages come from setup/requirements.txt, installed into ~/.wwtdigital-deck-design/venv by
# setup.sh / setup.ps1. Never advise a system-wide pip install: the users are not technical and
# a bare `python3` on a Mac without developer tools opens an install dialog.


# pip name -> import name, so a caller passing pkg="pillow" still finds the right entry.
_BY_PIP = {v[0]: k for k, v in PACKAGES.items()}


def _fail(mod, exc):
    root = mod.split(".")[0]
    root = _BY_PIP.get(root, root)          # accept either the import or the pip name
    pip, what = PACKAGES.get(root, (root, "this step"))
    sys.stderr.write(
        "\nSETUP NEEDED: %s is not installed.\n"
        "  What stops: %s.\n"
        "  Fix: run the one-time setup again (sh setup/setup.sh, or setup/setup.ps1 on\n"
        "  Windows). It installs %s and the rest into ~/.wwtdigital-deck-design.\n"
        "  Then run:    sh setup/run.sh doctor.py\n"
        "  The doctor reports exactly what this machine can and cannot enforce.\n\n"
        "  (underlying error: %s)\n\n"
        % (root, what, pip, exc))
    sys.exit(EXIT_MISSING)


def need(module, attr=None, pkg=None):
    """Import `module`, or exit 3 with an install line. Returns the module or `attr`."""
    try:
        m = __import__(module, fromlist=["_"] if "." in module or attr else [])
    except Exception as e:                      # ImportError, but also a broken install
        _fail(pkg or module, e)
    if attr is None:
        return m
    try:
        return getattr(m, attr)
    except AttributeError:
        # A SUBMODULE, not an attribute. `PIL.Image` is the common case: importing PIL
        # does not bind PIL.Image, so getattr fails on a perfectly healthy install and
        # the guard reports a missing package that is right there. The first cut of this
        # did exactly that and took the validator down on a machine with Pillow present,
        # which is worse than the traceback it replaced.
        try:
            sub = __import__("%s.%s" % (module, attr), fromlist=[attr])
            return sub
        except Exception as e:
            _fail(pkg or module, e)


def have(module):
    """True if the module imports. For callers that degrade rather than stop."""
    try:
        __import__(module)
        return True
    except Exception:
        return False
