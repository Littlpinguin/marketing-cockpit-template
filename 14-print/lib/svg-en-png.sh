#!/usr/bin/env bash
# Rend un SVG en PNG opaque haute définition, via Chrome headless.
# Un SVG qui porte des opacités, un dégradé, un masque ou un filtre est aplati ou rastérisé
# par Ghostscript à la conversion CMJN, parfois à 72 dpi. Rendu en PNG opaque à la bonne
# résolution, il traverse la chaîne intact.
# Usage : 14-print/lib/svg-en-png.sh source.svg sortie.png largeur_px hauteur_px [fond_hex]
#   fond_hex : couleur du fond sur lequel le SVG sera posé, sans # (défaut FFFFFF).
#   Pour viser 600 dpi : largeur_px = largeur d'affichage en mm / 25,4 x 600.
#   CHROME : chemin de Chrome ou Chromium (détecté sinon).
set -euo pipefail
[ $# -ge 4 ] || { echo "usage : $0 source.svg sortie.png largeur_px hauteur_px [fond_hex]" >&2; exit 2; }
SRC="$(cd "$(dirname "$1")" && pwd)/$(basename "$1")"; OUT="$2"; W="$3"; H="$4"
FOND="${5:-FFFFFF}"
if [ -z "${CHROME:-}" ]; then
  for c in "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" \
           "/Applications/Chromium.app/Contents/MacOS/Chromium" \
           google-chrome google-chrome-stable chromium chromium-browser; do
    if [ -x "$c" ] || command -v "$c" >/dev/null 2>&1; then CHROME="$c"; break; fi
  done
fi
[ -n "${CHROME:-}" ] || { echo "Chrome ou Chromium introuvable : renseigner CHROME=/chemin/vers/chrome" >&2; exit 1; }
TMP="$(mktemp -d)"
cat > "$TMP/r.html" <<EOF
<!doctype html><html><head><meta charset="utf-8"><style>
html,body{margin:0;padding:0;background:#${FOND}}
img{display:block;width:${W}px;height:${H}px}
</style></head><body><img src="file://$SRC"></body></html>
EOF
"$CHROME" --headless --disable-gpu --hide-scrollbars --virtual-time-budget=8000 \
  --default-background-color=${FOND}FF \
  --screenshot="$OUT" --window-size="$W,$H" "file://$TMP/r.html" 2>/dev/null
rm -rf "$TMP"
python3 - "$OUT" <<'PY'
import sys
from PIL import Image
Image.MAX_IMAGE_PIXELS = None
im = Image.open(sys.argv[1]).convert("RGB")   # aplati, sans canal alpha
im.save(sys.argv[1])
print(f"  {sys.argv[1].split('/')[-1]} : {im.size[0]}x{im.size[1]} px, opaque")
PY
