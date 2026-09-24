#!/bin/sh
# One-time setup for the WWTDigital design system on macOS and Linux.
#
#     sh setup.sh
#
# Written for people who have never installed Python and should not have to. It needs no
# admin password, changes nothing system-wide and touches nothing outside
# ~/.wwtdigital-design:
#
#   1. uv, a small self-contained tool that manages Python (astral.sh/uv). Used from PATH if
#      it is already installed, otherwise downloaded into ~/.wwtdigital-design/uv.
#   2. A private Python and the packages in requirements.txt, in ~/.wwtdigital-design/venv.
#      uv fetches its own Python, so a missing, old or system-managed Python does not matter.
#   3. A browser for rendering. Google Chrome or Microsoft Edge is used if either is
#      installed; otherwise Playwright's Chromium (~150 MB) is downloaded into
#      ~/.wwtdigital-design/browsers.
#
# Safe to run again: finished steps are skipped. Delete ~/.wwtdigital-design/venv to redo it.
set -eu

HERE=$(cd "$(dirname "$0")" && pwd)
HOME_DIR="${WWT_DESIGN_HOME:-$HOME/.wwtdigital-design}"
VENV="$HOME_DIR/venv"
PY="$VENV/bin/python"
export PLAYWRIGHT_BROWSERS_PATH="$HOME_DIR/browsers"

say() { printf '\n==> %s\n' "$1"; }
fail() { printf '\nSetup stopped: %s\n' "$1" >&2; exit 1; }

mkdir -p "$HOME_DIR"

say "Step 1 of 3: uv (the Python manager)"
if command -v uv >/dev/null 2>&1; then
  UV=$(command -v uv)
elif [ -x "$HOME_DIR/uv/uv" ]; then
  UV="$HOME_DIR/uv/uv"
else
  command -v curl >/dev/null 2>&1 || fail "curl is missing, so uv cannot be downloaded."
  echo "Downloading uv into $HOME_DIR/uv (about 15 MB)..."
  curl -LsSf https://astral.sh/uv/install.sh |
    env UV_INSTALL_DIR="$HOME_DIR/uv" UV_NO_MODIFY_PATH=1 sh >/dev/null ||
    fail "uv could not be downloaded. Check the network connection and try again."
  UV="$HOME_DIR/uv/uv"
fi
echo "Using $UV"

say "Step 2 of 3: Python and the design system's packages"
HASH=$(cksum < "$HERE/requirements.txt" | cut -d' ' -f1)
if [ -x "$PY" ] && [ "$(cat "$HOME_DIR/.requirements" 2>/dev/null)" = "$HASH" ]; then
  echo "Already installed."
else
  [ -x "$PY" ] || "$UV" venv --quiet --python 3.12 "$VENV" ||
    fail "a private Python could not be created. Check the network connection and try again."
  "$UV" pip install --quiet --python "$PY" -r "$HERE/requirements.txt" ||
    fail "the packages could not be installed. Check the network connection and try again."
  echo "$HASH" > "$HOME_DIR/.requirements"
  echo "Installed."
fi

say "Step 3 of 3: a browser for rendering slides"
if [ -d "/Applications/Google Chrome.app" ] || [ -d "/Applications/Microsoft Edge.app" ] ||
   command -v google-chrome >/dev/null 2>&1 || command -v microsoft-edge >/dev/null 2>&1; then
  echo "Using the Chrome or Edge already on this machine."
else
  echo "No Chrome or Edge found. Downloading Chromium (about 150 MB)..."
  "$PY" -m playwright install chromium ||
    fail "the browser could not be downloaded. Installing Google Chrome also fixes this."
fi

say "Checking the result"
"$PY" "$HERE/../skills/wwtdigital-design-system/scripts/doctor.py" || true
