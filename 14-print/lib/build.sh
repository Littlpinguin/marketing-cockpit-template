#!/usr/bin/env bash
# Chaîne d'export d'un imprimé.
#   HTML -> PDF (Chrome headless) -> montage 1:1 au format de données + TrimBox/BleedBox (PyMuPDF)
#   -> CMJN sur le profil du papier, PDF/X-4 avec intention de sortie, images Flate 600 dpi,
#      texte vectorisé (Ghostscript) -> texte et gris neutres en K seul (blacktext.py)
#   -> ${OUT}-print.pdf (pour l'imprimeur) ; ${OUT}-qa.pdf (sortie Chrome, texte vivant, pour qa.py)
#
# Usage : 14-print/lib/build.sh source.html output/prefixe
#
# Variables d'environnement :
#   FORMAT_MM        format fini en mm, LxH (défaut 148x210 : A5)
#   BLEED_IMPRIMEUR  fond perdu attendu par l'imprimeur, en mm (défaut 3 ; 2 chez certains)
#   BLEED_MAQUETTE   fond perdu de la maquette HTML, en mm (défaut 3 ; plus large en grand format)
#   ICCDIR           dossier des profils ICC (défaut 14-print/icc)
#   ICC_FICHIER      profil de sortie (défaut PSOuncoated_v3_FOGRA52.icc, papier non couché ;
#                    PSOcoated_v3.icc pour du couché, ISOcoated_v2_eci.icc pour un film ou une bâche)
#   CHROME           chemin de Chrome ou Chromium (détecté sinon)
#   TITRE_PDF        titre du document (certains portails de commande l'affichent)
#   MONTAGE          centre (défaut) ou coin : voir l'étape 2
set -euo pipefail

[ $# -ge 2 ] || { echo "usage : $0 source.html output/prefixe" >&2; exit 2; }
SRC="$(cd "$(dirname "$1")" && pwd)/$(basename "$1")"
mkdir -p "$(dirname "$2")"
OUT="$(cd "$(dirname "$2")" && pwd)/$(basename "$2")"
HERE="$(cd "$(dirname "$0")" && pwd)"

# Chrome ou Chromium : variable CHROME, sinon emplacements usuels (macOS, Linux).
if [ -z "${CHROME:-}" ]; then
  for c in "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" \
           "/Applications/Chromium.app/Contents/MacOS/Chromium" \
           google-chrome google-chrome-stable chromium chromium-browser; do
    if [ -x "$c" ] || command -v "$c" >/dev/null 2>&1; then CHROME="$c"; break; fi
  done
fi
[ -n "${CHROME:-}" ] || { echo "Chrome ou Chromium introuvable : renseigner CHROME=/chemin/vers/chrome" >&2; exit 1; }
command -v gs >/dev/null 2>&1 || { echo "Ghostscript (gs) introuvable" >&2; exit 1; }

ICCDIR="${ICCDIR:-$HERE/../icc}"
[ -d "$ICCDIR" ] || { echo "dossier de profils introuvable : $ICCDIR (voir 14-print/icc/README.md)" >&2; exit 1; }
ICCDIR="$(cd "$ICCDIR" && pwd)"
ICC_FICHIER="${ICC_FICHIER:-PSOuncoated_v3_FOGRA52.icc}"
ICC="$ICCDIR/$ICC_FICHIER"
case "$ICC_FICHIER" in
  ISOcoated_v2*) OI_COND="ISO Coated v2 (ECI), ISO 12647-2:2004 FOGRA39L"; OI_ID="FOGRA39" ;;
  PSOcoated_v3*) OI_COND="PSO Coated v3 (FOGRA51), ISO 12647-2:2013 PS1"; OI_ID="FOGRA51" ;;
  *)             OI_COND="PSO Uncoated v3 (FOGRA52), ISO 12647-2:2013 PS5"; OI_ID="FOGRA52" ;;
esac
BLEED_MAQUETTE="${BLEED_MAQUETTE:-3}"
BLEED_IMPRIMEUR="${BLEED_IMPRIMEUR:-3}"
export FORMAT_MM="${FORMAT_MM:-148x210}"

[ -f "$ICC" ] || { echo "profil manquant : $ICC (voir 14-print/icc/README.md)" >&2; exit 1; }

# 1. Chrome. --virtual-time-budget est INDISPENSABLE : sans lui, Chrome imprime avant
#    d'avoir chargé le CSS externe et sort des pages vides au bon format.
"$CHROME" --headless --disable-gpu --no-pdf-header-footer --virtual-time-budget=10000 \
  --print-to-pdf="${OUT}-qa.pdf" "file://${SRC}" 2>/dev/null

# 2. Montage 1:1 (aucune mise à l'échelle) au format de données de l'imprimeur, avec
#    TrimBox = coupe et BleedBox = média. La maquette est composée à BLEED_MAQUETTE de fond
#    perdu ; si l'imprimeur en veut moins, on rogne la différence par côté, le contenu ne bouge pas.
#    Chrome n'imprime pas au millimètre : sa page dépasse toujours un peu le format demandé
#    (mesuré : +0,18 x +0,58 mm sur un A5, +0,38 x +0,69 mm sur une carte de visite).
#    On découpe donc au CENTRE de sa page, sinon tout l'excédent est rejeté d'un seul côté
#    et le dessin sort décentré (0,59 mm d'écart haut/bas mesuré sur une carte).
#    MONTAGE=coin rétablit la découpe depuis le coin haut gauche.
python3 - "$OUT" "$BLEED_IMPRIMEUR" "${MONTAGE:-centre}" "$BLEED_MAQUETTE" <<'PY'
import sys, os, fitz
out, bleed, montage, bleed_maquette = sys.argv[1], float(sys.argv[2]), sys.argv[3], float(sys.argv[4])
MM = 72 / 25.4
# La maquette déborde d'un pixel en bas et à droite ; on rogne à partir de 0,1 mm à l'intérieur
# du contenu Chrome, jamais sur son bord exact (l'arrondi au pixel laissait un filet blanc
# de 0,06 mm en pied, mesuré à 1200 dpi). Le fond perdu réel reste ≥ fond perdu - 0,1 mm.
DEC = 0.1 * MM
ROGNE = (bleed_maquette - bleed) * MM + DEC
fw, fh = (float(v) for v in os.environ.get("FORMAT_MM", "148x210").split("x"))
W, H = (fw + 2 * bleed) * MM, (fh + 2 * bleed) * MM
src = fitz.open(f"{out}-qa.pdf"); dst = fitz.open()
dx = dy = ROGNE
for page in src:
    p = dst.new_page(width=W, height=H)
    dx = dy = ROGNE
    if montage == "centre":
        dx = max(ROGNE, (page.rect.width - W) / 2)
        dy = max(ROGNE, (page.rect.height - H) / 2)
    p.show_pdf_page(fitz.Rect(0, 0, W, H), src, page.number,
                    clip=fitz.Rect(dx, dy, dx + W, dy + H))
    p.set_trimbox(fitz.Rect(bleed * MM, bleed * MM, W - bleed * MM, H - bleed * MM))
    p.set_bleedbox(p.mediabox)
dst.save(f"{out}-monte.pdf")
print(f"{dst.page_count} page(s) montée(s) à {W/MM:.1f} x {H/MM:.1f} mm, fond perdu {bleed:g} mm, "
      f"découpe {montage} (dx {dx/MM:.3f} dy {dy/MM:.3f} mm)")
PY

# 3. Ghostscript : séparation CMJN sur le profil du papier, PDF/X-4 avec intention de sortie,
#    images conservées sans perte (Flate) et limitées à 600 dpi, texte vectorisé (une police
#    variable serait sinon embarquée en Type 3, mal digéré par certains RIP).
#    Jamais -dPDFX=3 : il rend en bitmap toute page contenant de la transparence.
TITRE_PDF="${TITRE_PDF:-$(basename "$OUT")}"
sed -e "s#@ICC@#$ICC#" -e "s#@TITRE@#$TITRE_PDF#" -e "s#@COND@#$OI_COND#" \
    -e "s#@INFO@#$ICC_FICHIER#" -e "s#@ID@#$OI_ID#" "$HERE/pdfx4.ps" > "${OUT}-pdfx4.ps"
# NE PAS toucher à -dMaxShadingBitmapSize : au-delà de la valeur par défaut (256 000),
# Ghostscript perd silencieusement des objets (un titre de couverture disparaissait).
# Les éléments en dégradé sont pré-rendus en PNG 600 dpi (chiffre-svg.py + chiffres-png.sh).
gs -dBATCH -dNOPAUSE -q -sDEVICE=pdfwrite -dPDFX=4 -dNoOutputFonts \
   -sColorConversionStrategy=CMYK -dProcessColorModel=/DeviceCMYK \
   -sOutputICCProfile="$ICC" --permit-file-read="$ICCDIR/" \
   -dAutoFilterColorImages=false -dColorImageFilter=/FlateEncode \
   -dAutoFilterGrayImages=false  -dGrayImageFilter=/FlateEncode \
   -dDownsampleColorImages=true -dColorImageResolution=600 -dColorImageDownsampleThreshold=1.2 -dColorImageDownsampleType=/Bicubic \
   -dDownsampleGrayImages=true  -dGrayImageResolution=600  -dGrayImageDownsampleThreshold=1.2  -dGrayImageDownsampleType=/Bicubic \
   -o "${OUT}-x4.pdf" "${OUT}-pdfx4.ps" "${OUT}-monte.pdf"

# 4. Texte et gris neutres en K seul (profil du papier passé pour le calcul de clarté).
python3 "$HERE/blacktext.py" "${OUT}-x4.pdf" "${OUT}-print.pdf" "$ICC"

rm -f "${OUT}-monte.pdf" "${OUT}-x4.pdf" "${OUT}-pdfx4.ps"
echo "généré : ${OUT}-print.pdf (fond perdu ${BLEED_IMPRIMEUR} mm, ${OI_ID}, PDF/X-4)"
