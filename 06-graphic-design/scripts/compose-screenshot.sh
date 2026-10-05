#!/usr/bin/env bash
# ============================================================
# Rend un HTML de composition en PNG via Chrome headless.
# Méthode « générer → composer » (skill image-generation) : l'IA fournit la
# matière, le texte, le vrai logo et les chiffres sont composés en HTML, puis
# capturés ici. Rendu 2× puis redimensionné à la taille cible : texte net.
#
# Usage : compose-screenshot.sh <input.html> <output.png> [largeur] [hauteur] [fond]
#   largeur/hauteur par défaut : 1080 x 1350 (portrait LinkedIn)
#   fond : couleur de fond par défaut de la page, RRGGBBAA sans « # »
#          (défaut FFFFFFFF ; 00000000 pour un fond transparent)
#
# Le HTML doit linker la base de composition (police locale + tokens de marque) :
#   <link rel="stylesheet" href="<chemin relatif>/06-graphic-design/lib/compose.css">
# Voir 06-graphic-design/lib/README.md pour installer la police de marque en local.
#
# Chrome : $CHROME s'il est défini, sinon Google Chrome (macOS), sinon
# google-chrome / chromium / chromium-browser dans le PATH.
# ============================================================
set -euo pipefail

HTML="${1:?input.html requis}"
OUT="${2:?output.png requis}"
W="${3:-1080}"
H="${4:-1350}"
FOND="${5:-FFFFFFFF}"

trouver_chrome() {
  if [ -n "${CHROME:-}" ]; then echo "$CHROME"; return; fi
  local mac="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
  if [ -x "$mac" ]; then echo "$mac"; return; fi
  for nom in google-chrome google-chrome-stable chromium chromium-browser; do
    if command -v "$nom" >/dev/null 2>&1; then command -v "$nom"; return; fi
  done
  echo ""
}

CHROME_BIN="$(trouver_chrome)"
[ -n "$CHROME_BIN" ] || { echo "❌ Chrome introuvable : définir CHROME=/chemin/vers/chrome" >&2; exit 1; }
[ -f "$HTML" ] || { echo "❌ fichier introuvable : $HTML" >&2; exit 2; }

ABS="$(cd "$(dirname "$HTML")" && pwd)/$(basename "$HTML")"
TMP="${OUT%.png}_2x.png"
mkdir -p "$(dirname "$OUT")"

# --virtual-time-budget laisse aux polices locales (font-display:block) le temps
# de se charger : sans elles, Chrome capture une police de repli.
"$CHROME_BIN" --headless=new --disable-gpu --hide-scrollbars --no-sandbox \
  --virtual-time-budget=2500 --force-device-scale-factor=2 \
  --window-size="${W},${H}" --default-background-color="$FOND" \
  --screenshot="$TMP" "file://$ABS" 2>/dev/null

# Redescend le rendu 2× à la taille cible (texte net) : Pillow, sinon sips (macOS).
if python3 -c "import PIL" 2>/dev/null; then
  python3 - "$TMP" "$OUT" "$W" "$H" <<'PY'
import sys
from PIL import Image
src, dst, w, h = sys.argv[1], sys.argv[2], int(sys.argv[3]), int(sys.argv[4])
with Image.open(src) as im:
    im.resize((w, h), Image.LANCZOS).save(dst)
PY
elif command -v sips >/dev/null 2>&1; then
  cp "$TMP" "$OUT"
  sips -z "$H" "$W" "$OUT" >/dev/null
else
  cp "$TMP" "$OUT"
  echo "⚠ ni Pillow ni sips : image laissée en 2× (${W}x${H} × 2)" >&2
fi
rm -f "$TMP"
echo "✅ $OUT (${W}×${H})"
