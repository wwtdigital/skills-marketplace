#!/usr/bin/env python3
"""
Find the Aptos faces this skill needs but does not ship.

    python3 scripts/brand_assets.py          # report what was found, and where

WHY THEY ARE NOT IN THE PACKAGE. Aptos is Microsoft's typeface. Microsoft 365 licenses you
to use it; it does not license anyone to redistribute the files, and this plugin is
published on a public marketplace. So the faces are looked up on the machine instead, and a
missing one stops the build with instructions rather than falling back to something that
looks nearly right.

WHERE FONTS ARE LOOKED FOR, in order:
  $WWT_FONTS_DIR                 one or more folders, separated like PATH
  ~/.wwtdigital-design/fonts
  assets/fonts                   an internal copy that still bundles them
  Microsoft Office itself        PowerPoint/Word/Excel/Outlook for Mac carry Aptos inside
                                 the app bundle; Office's cloud-font cache on Mac and Windows
  the system font folders        where the Microsoft download or a manual install puts them

Fonts are matched by the name stored INSIDE the file, not by its filename. Office's cloud
cache names files by number (CloudFonts/Aptos Serif/48155170935.ttf), so a filename match
would miss the most common place the serif lives.
"""
import os, struct, sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
HOME = os.path.expanduser("~")
USER_DIR = os.path.join(HOME, ".wwtdigital-design")

FONT_DOWNLOAD = "https://www.microsoft.com/en-us/download/details.aspx?id=106087"

# Full name (name table id 4) -> the filename the bundled copy used. The five sans cuts
# come with Office. Aptos Serif is a cloud font: Office downloads it the first time
# someone picks it, so it is often missing, and it is only needed for pull quotes.
CORE = ["Aptos", "Aptos SemiBold", "Aptos Bold", "Aptos ExtraBold", "Aptos Black"]
SERIF = "Aptos Serif Bold Italic"
BUNDLED_NAME = {
    "Aptos": "Aptos", "Aptos SemiBold": "Aptos-SemiBold", "Aptos Bold": "Aptos-Bold",
    "Aptos ExtraBold": "Aptos-ExtraBold", "Aptos Black": "Aptos-Black",
    SERIF: "Aptos-Serif-Bold-Italic",
}


def _dirs():
    env = [d for d in os.environ.get("WWT_FONTS_DIR", "").split(os.pathsep) if d]
    out = env + [os.path.join(USER_DIR, "fonts"), os.path.join(ROOT, "assets", "fonts")]
    if sys.platform == "darwin":
        out += ["/Applications/Microsoft %s.app/Contents/Resources/DFonts" % app
                for app in ("PowerPoint", "Word", "Excel", "Outlook")]
        out += [os.path.join(HOME, "Library/Group Containers/UBF8T346G9.Office/FontCache"),
                os.path.join(HOME, "Library/Fonts"), "/Library/Fonts"]
    elif os.name == "nt":
        local = os.environ.get("LOCALAPPDATA", "")
        out += [os.path.join(local, "Microsoft", "FontCache"),
                os.path.join(local, "Microsoft", "Windows", "Fonts"),
                os.path.join(os.environ.get("WINDIR", r"C:\Windows"), "Fonts")]
    else:
        out += [os.path.join(HOME, ".local/share/fonts"), os.path.join(HOME, ".fonts"),
                "/usr/local/share/fonts", "/usr/share/fonts"]
    return out


def _full_names(path):
    """Full name and PostScript name from a TTF/OTF name table, lower-cased. Reads only
    the table directory and the name table, so scanning a system font folder is cheap."""
    try:
        with open(path, "rb") as f:
            head = f.read(12)
            if len(head) < 12 or head[:4] not in (b"\x00\x01\x00\x00", b"OTTO", b"true"):
                return set()
            n = struct.unpack(">H", head[4:6])[0]
            table = f.read(16 * n)
            for i in range(n):
                tag, _, off, ln = struct.unpack(">4sIII", table[16 * i:16 * i + 16])
                if tag == b"name":
                    break
            else:
                return set()
            f.seek(off)
            d = f.read(ln)
        _, count, strings = struct.unpack(">HHH", d[:6])
        names = set()
        for i in range(count):
            pid, _, lid, nid, l, o = struct.unpack(">6H", d[6 + 12 * i:18 + 12 * i])
            if nid in (4, 6) and pid == 3 and lid == 0x409:
                s = d[strings + o:strings + o + l].decode("utf-16-be", "replace").lower()
                names.add(s.replace("-", " ") if nid == 6 else s)
        return names
    except (OSError, struct.error):
        return set()


_found = None


def find_fonts():
    """{full name: path} for every face this skill uses that exists on the machine.
    A WOFF2 is only picked up by its bundled filename; its name table is compressed."""
    global _found
    if _found is not None:
        return _found
    want = {n.lower(): n for n in BUNDLED_NAME}
    by_file = {v.lower() + ".woff2": k for k, v in BUNDLED_NAME.items()}
    _found = {}
    for d in _dirs():
        if not os.path.isdir(d):
            continue
        for base, _, files in os.walk(d):
            for fn in files:
                p = os.path.join(base, fn)
                ext = os.path.splitext(fn)[1].lower()
                if ext == ".woff2":
                    face = by_file.get(fn.lower())
                    hits = [face] if face else []
                elif ext in (".ttf", ".otf"):
                    hits = [want[n] for n in _full_names(p) if n in want]
                else:
                    continue
                for face in hits:
                    _found.setdefault(face, {}).setdefault(ext, p)
        if all(f in _found for f in BUNDLED_NAME):
            break
    return _found


def font_path(face, formats=(".woff2", ".ttf", ".otf")):
    got = find_fonts().get(face, {})
    for ext in formats:
        if ext in got:
            return got[ext]
    return None


def fonts_help(missing):
    return (
        "Aptos is not installed where this skill can find it. Missing: %s\n"
        "  The fonts are Microsoft's and are not shipped with the plugin. Any one of these fixes it:\n"
        "  - Mac with Microsoft 365: nothing to do for the five sans cuts, they are read from\n"
        "    inside PowerPoint.app. For Aptos Serif, use it once in PowerPoint so Office downloads it.\n"
        "  - Install the family from Microsoft: %s\n"
        "  - Put the .ttf files in ~/.wwtdigital-design/fonts, or point WWT_FONTS_DIR at them.\n"
        "  Run `python3 scripts/brand_assets.py` to see what was found."
        % (", ".join(missing), FONT_DOWNLOAD))


def require_fonts(faces, formats=(".woff2", ".ttf", ".otf")):
    """{face: path} for every face, or exit with instructions naming the missing ones."""
    got = {f: font_path(f, formats) for f in faces}
    missing = [f for f, p in got.items() if not p]
    if missing:
        sys.exit(fonts_help(missing))
    return got


def report():
    rows = [(f, font_path(f)) for f in CORE + [SERIF]]
    print("Fonts")
    for f, p in rows:
        print("  %-26s %s" % (f, p or "MISSING" + (" (pull quotes only)" if f == SERIF else "")))
    core_ok = all(p for f, p in rows if f != SERIF)
    if not core_ok:
        print("\n" + fonts_help([f for f, p in rows if not p]))
    return 0 if core_ok else 1


if __name__ == "__main__":
    sys.exit(report())
