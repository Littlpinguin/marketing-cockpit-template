#!/usr/bin/env python3
"""Remplace les opacités d'un SVG par des couleurs opaques équivalentes sur fond blanc.

Pourquoi : toute transparence (SVG ou CSS) crée un groupe de transparence que
Ghostscript aplatit à 72 dpi lors de la conversion CMYK, quelle que soit la
résolution d'origine. En pré-mélangeant la couleur avec le fond, le rendu est
identique et il n'y a plus de transparence à aplatir.

Ne convient qu'aux éléments posés sur un fond uni connu (le blanc de la page par défaut).
Sur un fond non uni, passer par une plaque (plaque.sh) ou un PNG opaque (svg-en-png.sh).
Le fichier est modifié en place.

Usage : python3 14-print/lib/opacifier-svg.py fichier.svg [couleur_de_fond_hex]
"""
import re, sys

def melange(hexa, alpha, fond=(255, 255, 255)):
    hexa = hexa.lstrip("#")
    if len(hexa) == 3:
        hexa = "".join(c * 2 for c in hexa)
    r, g, b = (int(hexa[i:i+2], 16) for i in (0, 2, 4))
    return "#%02X%02X%02X" % tuple(round(c * alpha + f * (1 - alpha)) for c, f in ((r, fond[0]), (g, fond[1]), (b, fond[2])))

def opacifier(chemin, fond=(255, 255, 255)):
    s = open(chemin, encoding="utf-8").read()
    n = 0
    # <tag ... fill="#xxx" ... fill-opacity="0.5" ...> dans n'importe quel ordre
    def traite(m):
        nonlocal n
        balise = m.group(0)
        for attr_op, attr_col in (("fill-opacity", "fill"), ("stroke-opacity", "stroke"), ("opacity", "fill")):
            mo = re.search(attr_op + r'="([\d.]+)"', balise)
            if not mo:
                continue
            alpha = float(mo.group(1))
            if alpha >= 1:
                balise = balise.replace(mo.group(0), ""); continue
            mc = re.search(attr_col + r'="(#[0-9A-Fa-f]{3,6})"', balise)
            if not mc:
                continue
            balise = balise.replace(mc.group(0), f'{attr_col}="{melange(mc.group(1), alpha, fond)}"')
            balise = balise.replace(mo.group(0), "")
            n += 1
        return balise
    s = re.sub(r"<[a-zA-Z][^>]*>", traite, s)
    open(chemin, "w", encoding="utf-8").write(s)
    return n

if __name__ == "__main__":
    fond = (255, 255, 255)
    if len(sys.argv) > 2:
        h = sys.argv[2].lstrip("#")
        fond = tuple(int(h[i:i+2], 16) for i in (0, 2, 4))
    print(f"{sys.argv[1].split('/')[-1]} : {opacifier(sys.argv[1], fond)} opacité(s) converties")
