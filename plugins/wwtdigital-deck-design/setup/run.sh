#!/bin/sh
# Run one of the design system's scripts with the right Python.
#
#     sh run.sh doctor.py
#     sh run.sh inline_assets.py deck.html -o Deck.html
#
# Uses the private Python that setup.sh installs. It never falls back to a bare `python3`:
# on a Mac without Apple's developer tools that command opens an install dialog instead of
# running anything. Exits 3 with a plain-language message when setup has not been run.
HERE=$(cd "$(dirname "$0")" && pwd)
HOME_DIR="${WWT_DESIGN_HOME:-$HOME/.wwtdigital-deck-design}"
PY="$HOME_DIR/venv/bin/python"
export PLAYWRIGHT_BROWSERS_PATH="$HOME_DIR/browsers"

if [ $# -lt 1 ]; then
  echo "usage: sh run.sh <script.py> [arguments]" >&2
  exit 2
fi
if [ ! -x "$PY" ]; then
  cat >&2 <<MSG
SETUP NEEDED: the WWTDigital design system has not been set up on this machine yet.
It is a one-time step, a few minutes, no admin password. It downloads a private copy of
Python and its packages (about 330 MB of disk space, plus about 150 MB for a browser only if neither
Chrome nor Edge is installed) into ~/.wwtdigital-deck-design. To run it:
    sh "$HERE/setup.sh"
MSG
  exit 3
fi
SCRIPT="$1"; shift
exec "$PY" "$HERE/../skills/wwtdigital-deck-design/scripts/$SCRIPT" "$@"
