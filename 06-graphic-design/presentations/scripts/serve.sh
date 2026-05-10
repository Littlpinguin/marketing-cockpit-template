#!/usr/bin/env bash
# Local static server. Open http://localhost:5173/decks/ in Chrome.
#
# Uses npx http-server, no install required (downloads on first run).

set -euo pipefail

PORT="${PORT:-5173}"
ROOT="$(cd "$(dirname "$0")/.." && pwd)"

cd "$ROOT"

echo "serving $ROOT on http://localhost:$PORT"
echo "  · open http://localhost:$PORT/decks/ to browse"
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
