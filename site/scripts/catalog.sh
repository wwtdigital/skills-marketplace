#!/bin/sh
# Generate site/public/{data,downloads} from the repo before `next dev` / `next build`.
#   --strict   also run the validator and fail on any warning (npm run build does; dev doesn't)
# On Vercel ($VERCEL is set) both scripts use the live production catalog as the baseline:
# version bumps are checked against it, and unchanged skills keep its "updated" dates.
set -eu
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
VENV="$ROOT/site/.pyenv"

[ -x "$VENV/bin/python" ] || python3 -m venv "$VENV"
"$VENV/bin/python" -c "import yaml" 2>/dev/null || "$VENV/bin/pip" install -q pyyaml
PY="$VENV/bin/python"

PREV=""
[ -n "${VERCEL:-}" ] && PREV="--prev-catalog auto"

# shellcheck disable=SC2086
[ "${1:-}" = "--strict" ] && "$PY" "$ROOT/scripts/validate.py" --strict $PREV
# shellcheck disable=SC2086
"$PY" "$ROOT/scripts/build_index.py" $PREV
