#!/bin/sh
# One-time setup for the WWTDigital design system on macOS and Linux.
#
#     sh setup.sh
#
# Written for people who have never installed Python and should not have to. It needs no
# admin password, changes nothing system-wide and touches nothing outside
# ~/.wwtdigital-deck-design:
#
#   1. uv, a small self-contained tool that manages Python (astral.sh/uv). Used from PATH if
#      it is already installed, otherwise a pinned release is downloaded from GitHub into
#      ~/.wwtdigital-deck-design/uv after its SHA-256 is checked.
#   2. A private Python and the packages in requirements.txt, in ~/.wwtdigital-deck-design/venv.
#      uv fetches its own Python, so a missing, old or system-managed Python does not matter.
#   3. A browser for rendering. Google Chrome or Microsoft Edge is used if either is
#      installed; otherwise Playwright's Chromium (~150 MB) is downloaded into
#      ~/.wwtdigital-deck-design/browsers.
#
# Safe to run again: finished steps are skipped. Delete ~/.wwtdigital-deck-design/venv to redo it.
set -eu

HERE=$(cd "$(dirname "$0")" && pwd)
HOME_DIR="${WWT_DESIGN_HOME:-$HOME/.wwtdigital-deck-design}"
VENV="$HOME_DIR/venv"
PY="$VENV/bin/python"
export PLAYWRIGHT_BROWSERS_PATH="$HOME_DIR/browsers"
# Keep uv's Python and download cache inside HOME_DIR too, instead of ~/.local and ~/.cache.
export UV_PYTHON_INSTALL_DIR="$HOME_DIR/python"
export UV_CACHE_DIR="$HOME_DIR/cache"

say() { printf '\n==> %s\n' "$1"; }
fail() { printf '\nSetup stopped: %s\n' "$1" >&2; exit 1; }

mkdir -p "$HOME_DIR"

say "Step 1 of 3: uv (the Python manager)"
if command -v uv >/dev/null 2>&1; then
  UV=$(command -v uv)
elif [ -x "$HOME_DIR/uv/uv" ]; then
  UV="$HOME_DIR/uv/uv"
else
  # uv comes straight from its GitHub release: one pinned version, and the download must match
  # the SHA-256 below before anything is unpacked. Nothing downloaded is ever run as a script.
  # To move to a newer uv, change the version and all four hashes together, here and in
  # setup.ps1 (see CLAUDE.md).
  UV_VERSION="0.12.17"
  case "$(uname -s)-$(uname -m)" in
    Darwin-arm64)
      UV_TARGET="aarch64-apple-darwin"
      UV_SHA256="85f00cbdc6dd3e97eba4c31b4d014375a9fdfe8f570023b84e5102fc3456896b" ;;
    Darwin-x86_64)
      UV_TARGET="x86_64-apple-darwin"
      UV_SHA256="8dcf05a8c809bb3c471d2b614788ba27a6e41298fc8c31ac84b5f4339fd468e5" ;;
    Linux-x86_64)
      UV_TARGET="x86_64-unknown-linux-musl"
      UV_SHA256="6401c4665d8fa2a9893e087c91f585430738e3170f5398a1141483efb4a93310" ;;
    Linux-aarch64|Linux-arm64)
      UV_TARGET="aarch64-unknown-linux-musl"
      UV_SHA256="a6096da273d548cb9f277d237a01ac7344a39ef0f455c0e148e4dc9737c1596b" ;;
    *) fail "this kind of computer ($(uname -sm)) is not supported. Install uv yourself (docs.astral.sh/uv) and run this again." ;;
  esac
  command -v curl >/dev/null 2>&1 || fail "curl is missing, so uv cannot be downloaded."
  command -v tar >/dev/null 2>&1 || fail "tar is missing, so uv cannot be unpacked."
  if command -v shasum >/dev/null 2>&1; then SHA_CMD="shasum -a 256"
  elif command -v sha256sum >/dev/null 2>&1; then SHA_CMD="sha256sum"
  else fail "neither shasum nor sha256sum is available, so the uv download cannot be checked."; fi

  echo "Downloading uv $UV_VERSION into $HOME_DIR/uv (about 20 MB)..."
  TMP=$(mktemp -d "$HOME_DIR/uv-download.XXXXXX")
  trap 'rm -rf "$TMP"' EXIT
  ARCHIVE="uv-$UV_TARGET.tar.gz"
  curl -fsSL -o "$TMP/$ARCHIVE" "https://github.com/astral-sh/uv/releases/download/$UV_VERSION/$ARCHIVE" ||
    fail "uv could not be downloaded. Check the network connection and try again."
  GOT=$($SHA_CMD "$TMP/$ARCHIVE" | cut -d' ' -f1)
  [ "$GOT" = "$UV_SHA256" ] ||
    fail "the uv download did not match its expected checksum, so it was discarded. Try again; if it keeps happening, tell the plugin owner."
  tar -xzf "$TMP/$ARCHIVE" -C "$TMP" || fail "the uv download could not be unpacked."
  mkdir -p "$HOME_DIR/uv"
  cp "$TMP/uv-$UV_TARGET/uv" "$HOME_DIR/uv/uv" && chmod +x "$HOME_DIR/uv/uv" ||
    fail "uv could not be installed into $HOME_DIR/uv."
  rm -rf "$TMP"; trap - EXIT
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
  "$UV" cache clean --quiet 2>/dev/null || true   # the download cache is ~230 MB and not needed again
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
"$PY" "$HERE/../skills/wwtdigital-deck-design/scripts/doctor.py" || true
