#!/usr/bin/env python3
"""Rend un nombre (ou un mot court) en SVG, glyphes convertis en TRACÉS, remplis par un dégradé.

Pourquoi : un texte rempli par un dégradé (CSS background-clip:text ou <text> SVG) est
rastérisé par Ghostscript dès qu'on vectorise les polices (-dNoOutputFonts), et le masque
alpha du background-clip est même perdu à la conversion CMJN : il ne reste qu'un rectangle
de dégradé. En sortant les glyphes en <path>, il n'y a plus ni police ni masque, seulement
des tracés remplis par un dégradé ; chiffres-png.sh les rend ensuite en PNG opaque 600 dpi.

Usage :
  python3 14-print/lib/chiffre-svg.py TEXTE --police chemin/police.woff2 \\
      --de "#RRGGBB" --a "#RRGGBB" [--milieu "#RRGGBB"] [--poids 800] [--espacement 0.0] > sortie.svg

  --police     fichier de la police de marque (ttf, otf, woff ou woff2), variable ou non.
               Défaut : variable POLICE_FICHIER. Typiquement dans 01-brand/assets/fonts/.
  --de / --a   couleurs de départ et d'arrivée du dégradé de marque (01-brand/style-guide.md,
               BRAND_GRADIENT). Défaut : variables DEGRADE_DE / DEGRADE_A.
  --milieu     arrêt intermédiaire facultatif (à 45 %).
  --poids      graisse instanciée si la police est variable (axe wght).
  --espacement interlettrage en em, comme letter-spacing.

Le woff2 demande le paquet brotli (pip install brotli).
"""
import argparse
import os
import sys

from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
from fontTools.ttLib import TTFont


def svg(texte, police, de, a, poids=800, espacement=0.0, milieu=None):
    f = TTFont(police)
    if "fvar" in f:                      # police variable : on instancie la graisse voulue
        from fontTools.varLib.instancer import instantiateVariableFont
        axes = {ax.axisTag: ax for ax in f["fvar"].axes}
        if "wght" in axes:
            w = max(axes["wght"].minValue, min(axes["wght"].maxValue, poids))
            f = instantiateVariableFont(f, {"wght": w}, inplace=False)
    upem = f["head"].unitsPerEm
    glyphset = f.getGlyphSet()
    cmap = f.getBestCmap()
    hmtx = f["hmtx"]
    # Tous les glyphes dans UN SEUL tracé : un transform par glyphe décalerait le repère
    # du dégradé userSpaceOnUse, qui repartirait à zéro sur chaque caractère.
    x = 0.0
    pen = SVGPathPen(glyphset)
    for ch in texte:
        if ord(ch) not in cmap:
            sys.exit(f"caractère absent de la police : {ch!r}")
        nom = cmap[ord(ch)]
        glyphset[nom].draw(TransformPen(pen, (1, 0, 0, 1, x, 0)))
        x += hmtx[nom][0] + espacement * upem
    largeur, hauteur = x - espacement * upem, upem   # pas d'espace fantôme après le dernier glyphe
    # repère SVG : y vers le bas, glyphes dessinés y vers le haut -> on retourne
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {largeur:.0f} {hauteur:.0f}" '
            f'preserveAspectRatio="xMinYMid meet">'
            f'<defs><linearGradient id="degrade" gradientUnits="userSpaceOnUse" '
            f'x1="0" y1="0" x2="{largeur:.0f}" y2="0">'
            f'<stop offset="0" stop-color="{de}"/>'
            + (f'<stop offset=".45" stop-color="{milieu}"/>' if milieu else '')
            + f'<stop offset="1" stop-color="{a}"/>'
            f'</linearGradient></defs>'
            f'<g fill="url(#degrade)" transform="translate(0 {upem*0.76:.0f}) scale(1 -1)">'
            f'<path d="{pen.getCommands()}"/></g></svg>')


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description="Texte court en SVG vectorisé, rempli d'un dégradé.")
    ap.add_argument("texte")
    ap.add_argument("--police", default=os.environ.get("POLICE_FICHIER"))
    ap.add_argument("--de", default=os.environ.get("DEGRADE_DE"))
    ap.add_argument("--a", default=os.environ.get("DEGRADE_A"))
    ap.add_argument("--milieu", default=None)
    ap.add_argument("--poids", type=int, default=800)
    ap.add_argument("--espacement", type=float, default=0.0)
    o = ap.parse_args()
    manque = [n for n, v in (("--police", o.police), ("--de", o.de), ("--a", o.a)) if not v]
    if manque:
        ap.error("à renseigner (argument ou variable d'environnement) : " + ", ".join(manque))
    print(svg(o.texte, o.police, o.de, o.a, o.poids, o.espacement, o.milieu))
