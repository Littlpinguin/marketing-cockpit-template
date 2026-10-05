#!/usr/bin/env bash
# Compose la PLAQUE d'une page imprimée : tout ce qui se superpose (fonds, dégradés, opacités,
# filigranes, illustrations, blocs de couleur, icônes) capturé en UNE image opaque, depuis la
# maquette elle-même, donc au pixel près au même endroit que le texte vivant.
#
# Pourquoi : Ghostscript aplatit toute transparence à 72 dpi à la conversion CMJN, un dégradé
# CSS est un background-image rastérisé à 72 dpi, et une image opaque posée dans la page
# masque ce qui est derrière elle sur TOUTE sa boîte. La plaque règle les trois : le PDF ne
# contient plus qu'une image opaque à la bonne résolution, le texte vivant et des vecteurs
# pleins (QR code, filets).
#
# La maquette porte deux modes, pilotés par une classe du <body> :
#   body.impression  mode normal, celui que build.sh imprime : la plaque en image de fond
#                    (<img src="assets/plaque.png"> à fond perdu), le texte vivant, les vecteurs
#                    pleins ; tout le décor superposé est masqué (display:none)
#   body.plaque      uniquement le décor à superposer ; texte et vecteurs pleins masqués
# Ce script copie la maquette en passant <body class="impression"> en <body class="plaque">,
# la capture à la taille de la page (format fini + 2 x BLEED_MAQUETTE) et l'aplatit en RGB.
#
# Usage : 14-print/lib/plaque.sh maquette.html sortie.png [dpi] [fond_hex]
#   dpi      : 600 pour un petit format lu de près, 300 pour une brochure, 150 pour un grand
#              format lu à plus d'un mètre (défaut 300)
#   fond_hex : couleur de fond de la page, sans # (défaut FFFFFF)
#   FORMAT_MM, BLEED_MAQUETTE : comme build.sh ; CHROME : chemin de Chrome ou Chromium.
# Une page par appel : pour une brochure, une plaque par page qui en a besoin.
set -euo pipefail
[ $# -ge 2 ] || { echo "usage : $0 maquette.html sortie.png [dpi] [fond_hex]" >&2; exit 2; }
SRC="$(cd "$(dirname "$1")" && pwd)/$(basename "$1")"
OUT="$2"; DPI="${3:-300}"; FOND="${4:-FFFFFF}"
FORMAT_MM="${FORMAT_MM:-148x210}"; BLEED_MAQUETTE="${BLEED_MAQUETTE:-3}"
if [ -z "${CHROME:-}" ]; then
  for c in "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" \
           "/Applications/Chromium.app/Contents/MacOS/Chromium" \
           google-chrome google-chrome-stable chromium chromium-browser; do
    if [ -x "$c" ] || command -v "$c" >/dev/null 2>&1; then CHROME="$c"; break; fi
  done
fi
[ -n "${CHROME:-}" ] || { echo "Chrome ou Chromium introuvable : renseigner CHROME=/chemin/vers/chrome" >&2; exit 1; }

# Taille de la page en pixels CSS (96 par pouce) et facteur d'échelle pour la résolution visée.
read -r WPX HPX DSF <<<"$(python3 -c "
fw, fh = (float(v) for v in '$FORMAT_MM'.split('x'))
b = float('$BLEED_MAQUETTE')
print(round((fw + 2 * b) / 25.4 * 96), round((fh + 2 * b) / 25.4 * 96), float('$DPI') / 96)")"

# Copie en mode plaque, à côté de la maquette pour que les chemins relatifs restent valides.
TMP="$(dirname "$SRC")/.plaque-$$.html"
trap 'rm -f "$TMP"' EXIT
python3 - "$SRC" "$TMP" <<'PY'
import re, sys
s = open(sys.argv[1], encoding="utf-8").read()
s2, n = re.subn(r'(<body\b[^>]*\bclass="[^"]*)\bimpression\b', r'\1plaque', s, count=1)
if not n:
    sys.exit('la maquette doit porter <body class="impression"> : voir l\'en-tête de plaque.sh')
open(sys.argv[2], "w", encoding="utf-8").write(s2)
PY

"$CHROME" --headless --disable-gpu --hide-scrollbars --virtual-time-budget=15000 \
  --force-device-scale-factor="$DSF" --window-size="$WPX,$HPX" \
  --default-background-color="${FOND}FF" \
  --screenshot="$OUT" "file://$TMP" 2>/dev/null

python3 - "$OUT" "$WPX" <<'PY'
import sys
from PIL import Image
Image.MAX_IMAGE_PIXELS = None
im = Image.open(sys.argv[1]).convert("RGB")      # aucun canal alpha dans le PDF
im.save(sys.argv[1], optimize=True)
print(f"plaque : {im.size[0]} x {im.size[1]} px, opaque, {im.size[0] / (int(sys.argv[2]) / 96):.0f} dpi")
PY
