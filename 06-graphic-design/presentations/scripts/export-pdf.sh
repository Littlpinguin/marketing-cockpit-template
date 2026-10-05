#!/usr/bin/env bash
# VENDORED from slides-agent (https://github.com/Littlpinguin/slides-agent), scripts/export-pdf.sh,
# by scripts/sync-slides-engine.py. Do not edit here: change slides-agent,
# then run python3 scripts/sync-slides-engine.py. Mentions of CLAUDE.md,
# onboarding and the pexels-photos skill refer to slides-agent.
# Register: docs/vendored-slides.md
# Headless Chromium PDF export — 1 slide per page at 1920×1080.
#
# Usage:
#   ./06-graphic-design/presentations/scripts/export-pdf.sh 06-graphic-design/presentations/decks/your-deck.html [output.pdf]
#
# Requires Python + Playwright:
#   pip install playwright && playwright install chromium

set -euo pipefail

if [ $# -lt 1 ]; then
  echo "usage: $0 <06-graphic-design/presentations/decks/your-deck.html> [output.pdf]" >&2
  exit 2
fi

INPUT="$1"
OUTPUT="${2:-${INPUT%.html}.pdf}"
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

if [ ! -f "$INPUT" ]; then
  echo "error: file not found: $INPUT" >&2
  exit 2
fi

python3 "$SCRIPT_DIR/export_pdf.py" "$INPUT" "$OUTPUT"

echo
echo "ok · $OUTPUT"
