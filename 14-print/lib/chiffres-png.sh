#!/usr/bin/env bash
# Rend des chiffres héros (SVG à dégradé produits par chiffre-svg.py) en PNG opaques 600 dpi.
# Ghostscript rastérise tout dégradé à la conversion CMJN, vers 180 dpi pour les grands
# aplats, et la seule option qui l'améliore (-dMaxShadingBitmapSize) lui fait perdre des
# objets. On pré-rend donc à la résolution voulue, à la hauteur d'usage dans la maquette.
#
# Usage : 14-print/lib/chiffres-png.sh <dossier> nom:hauteur_mm [nom:hauteur_mm …] [fond_hex]
#   <dossier>/nom.svg est rendu en <dossier>/nom.png ; hauteur_mm = hauteur d'affichage
#   dans la maquette ; fond_hex (sans #, défaut FFFFFF) = couleur du fond sous le chiffre.
#   Exemple : 14-print/lib/chiffres-png.sh maquette/assets/chiffres 42:26.8 120:18 FFFFFF
set -euo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
[ $# -ge 2 ] || { echo "usage : $0 <dossier> nom:hauteur_mm [...] [fond_hex]" >&2; exit 2; }
D="$1"; shift
FOND="FFFFFF"
DPI="${DPI:-600}"
SPECS=()
for a in "$@"; do
  case "$a" in
    *:*) SPECS+=("$a") ;;
    *)   FOND="$a" ;;
  esac
done
[ ${#SPECS[@]} -gt 0 ] || { echo "aucun nom:hauteur_mm fourni" >&2; exit 2; }
for spec in "${SPECS[@]}"; do
  n="${spec%%:*}"; hmm="${spec##*:}"
  ratio=$(python3 -c "
import re, sys
s = open(sys.argv[1]).read()
w, h = re.search(r'viewBox=\"0 0 ([\d.]+) ([\d.]+)\"', s).groups()
print(float(w) / float(h))" "$D/$n.svg")
  hpx=$(python3 -c "print(round($hmm / 25.4 * $DPI))")
  wpx=$(python3 -c "print(round($hpx * $ratio))")
  "$HERE/svg-en-png.sh" "$D/$n.svg" "$D/$n.png" "$wpx" "$hpx" "$FOND"
done
