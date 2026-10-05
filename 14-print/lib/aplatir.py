#!/usr/bin/env python3
"""Aplatit les PNG à canal alpha sur la couleur de leur fond réel dans la maquette.

Pourquoi : Ghostscript aplatit les masques de transparence (SMask) lors de la conversion
CMJN et les rastérise à 72 dpi, quelle que soit la résolution de l'image d'origine. Une
illustration pleine page passait ainsi de 296 dpi à 72 dpi. Sans alpha, il n'y a plus rien
à aplatir : l'image traverse la chaîne intacte.

Chaque image est aplatie sur la couleur du fond sur lequel elle est RÉELLEMENT posée dans
la maquette ; le rendu est identique, la transparence disparaît. Une image posée sur un
fond non uni (dégradé, photo, filigrane) ne s'aplatit pas ici : elle entre dans la plaque
(voir plaque.sh).

Usage :
  python3 14-print/lib/aplatir.py <image.png | dossier> [fond_hex]
      fond_hex : couleur du fond sous l'image, sans # (défaut FFFFFF). Un dossier est traité
      en entier (PNG uniquement), tous ses fichiers sur le même fond.
  python3 14-print/lib/aplatir.py --carte fonds.json
      fonds.json : {"chemin/relatif/au/json.png": "FFFFFF", "autre.png": "E8EEF7", ...}
      pour les maquettes où chaque illustration a son propre fond.

Les fichiers sont modifiés en place : garder les originaux dans les assets de la marque.
"""
import json
import os
import sys

from PIL import Image


def hex_rgb(h):
    h = h.lstrip("#")
    if len(h) == 3:
        h = "".join(c * 2 for c in h)
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def aplatir(chemin, fond):
    im = Image.open(chemin)
    if im.mode not in ("RGBA", "LA", "P") and "transparency" not in im.info:
        return False
    im = im.convert("RGBA")
    plat = Image.new("RGB", im.size, fond)
    plat.paste(im, mask=im.split()[3])
    plat.save(chemin)
    return True


def main(argv):
    if len(argv) < 2:
        sys.exit(__doc__)
    n = 0
    if argv[1] == "--carte":
        carte = argv[2]
        base = os.path.dirname(os.path.abspath(carte))
        for rel, fond in json.load(open(carte, encoding="utf-8")).items():
            p = os.path.normpath(os.path.join(base, rel))
            if os.path.exists(p) and aplatir(p, hex_rgb(fond)):
                print(f"  {rel} -> aplati sur #{fond.lstrip('#')}")
                n += 1
    else:
        cible = argv[1]
        fond = hex_rgb(argv[2]) if len(argv) > 2 else (255, 255, 255)
        fichiers = ([os.path.join(cible, f) for f in sorted(os.listdir(cible)) if f.lower().endswith(".png")]
                    if os.path.isdir(cible) else [cible])
        for f in fichiers:
            if aplatir(f, fond):
                print(f"  {os.path.basename(f)} -> aplati sur #{'%02X%02X%02X' % fond}")
                n += 1
    print(f"{n} image(s) aplatie(s)")


if __name__ == "__main__":
    main(sys.argv)
