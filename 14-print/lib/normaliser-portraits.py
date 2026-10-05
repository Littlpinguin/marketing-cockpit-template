#!/usr/bin/env python3
"""Normalise le cadrage des portraits pour qu'ils s'affichent tous pareil en médaillon.

Des portraits venus de sources différentes (bibliothèque, générations, photos détourées)
ont des marges internes hétérogènes (mesuré : de 0 % à 11 %, dessin occupant de 79 % à
99,8 % de la hauteur). Résultat : certains crânes touchent le bord du cercle, d'autres
flottent trop petits. On recadre chacun dans un carré où le dessin occupe la même hauteur,
à la même place, ce qui permet une règle CSS unique pour tous les médaillons.

Cadrage cible (réglable par variables d'environnement) : image carrée, dessin centré
horizontalement, sommet à MARGE_HAUTE (12 %) du haut, hauteur du dessin à HAUTEUR (84 %).
Le « dessin » est tout pixel plus sombre que SEUIL (245) sur au moins un canal : la méthode
vise des portraits sur fond blanc ou clair uni.

Dans une SÉRIE (cartes, trombinoscope), l'échelle se cale sur la largeur de la TÊTE, pas
sur la hauteur du personnage : à hauteur égale, une silhouette large sort avec une tête plus
grosse que les autres. Ce script cadre sur la hauteur ; vérifier la série à l'œil et
corriger à la main les exceptions.

Usage : python3 14-print/lib/normaliser-portraits.py <dossier_de_png> [fond_hex]
  Les fichiers sont modifiés en place : garder les originaux ailleurs.
"""
import glob
import os
import sys

import numpy as np
from PIL import Image

MARGE_HAUTE = float(os.environ.get("MARGE_HAUTE", "0.12"))
HAUTEUR = float(os.environ.get("HAUTEUR", "0.84"))
SEUIL = int(os.environ.get("SEUIL", "245"))


def normaliser(chemin, fond):
    im = Image.open(chemin)
    if im.mode in ("RGBA", "LA", "P"):        # alpha : aplatir d'abord sur le fond, sinon les
        im = im.convert("RGBA")               # pixels transparents comptent comme du dessin
        plat = Image.new("RGB", im.size, fond)
        plat.paste(im, mask=im.split()[3])
        im = plat
    im = im.convert("RGB")
    a = np.array(im)
    dessin = (a.min(axis=2) < SEUIL)
    ys, xs = np.where(dessin)
    if not len(ys):
        return None
    x0, x1, y0, y1 = xs.min(), xs.max() + 1, ys.min(), ys.max() + 1
    bw, bh = x1 - x0, y1 - y0
    cote = round(bh / HAUTEUR)
    if bw > cote * 0.92:                      # portrait large : on élargit pour ne rien couper
        cote = round(bw / 0.92)
    sortie = Image.new("RGB", (cote, cote), fond)
    sortie.paste(im.crop((x0, y0, x1, y1)), (round((cote - bw) / 2), round(cote * MARGE_HAUTE)))
    sortie.save(chemin)
    return cote


if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    D = sys.argv[1]
    h = (sys.argv[2] if len(sys.argv) > 2 else "FFFFFF").lstrip("#")
    fond = tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))
    n = 0
    for f in sorted(glob.glob(os.path.join(D, "*.png"))):
        c = normaliser(f, fond)
        if c:
            n += 1
            print(f"  {os.path.basename(f):<38} -> {c}x{c} px")
    print(f"{n} portrait(s) normalisé(s) (dessin à {HAUTEUR*100:.0f} %, sommet à {MARGE_HAUTE*100:.0f} %)")
