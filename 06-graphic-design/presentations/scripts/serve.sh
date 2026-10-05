#!/usr/bin/env bash
# VENDORED from slides-agent (https://github.com/Littlpinguin/slides-agent), scripts/serve.sh,
# by scripts/sync-slides-engine.py. Do not edit here: change slides-agent,
# then run python3 scripts/sync-slides-engine.py. Mentions of CLAUDE.md,
# onboarding and the pexels-photos skill refer to slides-agent.
# Register: docs/vendored-slides.md
# Local static server. Open http://localhost:5173/06-graphic-design/presentations/decks/ in Chrome.
#
# Uses npx http-server, no install required (downloads on first run).

set -euo pipefail

PORT="${PORT:-5173}"
ROOT="$(cd "$(dirname "$0")/../../.." && pwd)"

cd "$ROOT"

echo "serving $ROOT on http://localhost:$PORT"
echo "  · open http://localhost:$PORT/06-graphic-design/presentations/decks/ to browse"
echo "  · press ctrl-c to stop"
echo

if command -v python3 >/dev/null 2>&1; then
  exec python3 -m http.server "$PORT" --bind 127.0.0.1
elif command -v npx >/dev/null 2>&1; then
  exec npx --yes http-server "$ROOT" -p "$PORT" -a 127.0.0.1 -c-1
else
  echo "error: neither python3 nor npx found. install one of them." >&2
  exit 2
fi
