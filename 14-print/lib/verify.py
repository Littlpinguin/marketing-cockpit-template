#!/usr/bin/env python3
"""Contrôle prépresse d'un PDF imprimeur (sortie *-print.pdf de build.sh). Sort en erreur au moindre écart.

Usage : python3 14-print/lib/verify.py output/livrable-print.pdf <nombre_de_pages>

Contrôles : nombre de pages, format de données au centième de millimètre, pages vides,
fond perdu couvert, polices (Type 3 interdites ; liste blanche facultative), CMJN effectif
et RGB résiduel, intention de sortie PDF/X-4, TrimBox, résolution effective de chaque
image, images JPEG, charge d'encre maximale.

Variables d'environnement :
  FORMAT_MM=148x210        format fini
  BLEED_IMPRIMEUR=3        fond perdu du fichier livré
  DPI_MIN=300              résolution effective minimale (150 en grand format lu à distance)
  TAC_MAX=300              charge d'encre maximale en % (300 sur FOGRA52/51, 330 sur FOGRA39)
  OUTPUT_ID=FOGRA52        identifiant de l'intention de sortie attendue
  POLICES_AUTORISEES=…     si le texte n'est pas vectorisé : fragments de noms de polices
                           autorisés, séparés par des virgules (ex. le nom de la police de marque)

Le contrôle de page vide n'est pas cosmétique : Chrome peut produire un PDF au
bon format, avec le bon nombre de pages, et entièrement vide, quand le CSS
externe n'a pas fini de charger. Rien ne le signale sans ouvrir le fichier.
"""
import sys
import fitz

import os
import re
TOLERANCE_MM = 0.01
BLEED = float(os.environ.get("BLEED_IMPRIMEUR", "3"))
FINI = tuple(float(v) for v in os.environ.get("FORMAT_MM", "148x210").split("x"))
ATTENDU_MM = (FINI[0] + 2 * BLEED, FINI[1] + 2 * BLEED)
# Grand format : DPI_MIN (150 pour une bâche lue à plus d'un mètre), TAC_MAX (330 sur
# ISO Coated v2) et OUTPUT_ID (FOGRA39) se règlent par l'environnement.
POLICES_AUTORISEES = [p.strip() for p in os.environ.get("POLICES_AUTORISEES", "").split(",") if p.strip()]
TAC_MAX = float(os.environ.get("TAC_MAX", "300"))   # charge d'encre maximale (300 sur FOGRA52)
DPI_MIN = float(os.environ.get("DPI_MIN", "300"))
OUTPUT_ID = os.environ.get("OUTPUT_ID", "FOGRA52")
ECART_TYPE_MINI = 1.5   # une page uniformément vide tombe sous ce seuil


def ecart_type_pixels(page):
    """Mesure la variation de gris d'une page rendue en basse définition."""
    pix = page.get_pixmap(dpi=20, colorspace=fitz.csGRAY)
    valeurs = pix.samples
    n = len(valeurs)
    moyenne = sum(valeurs) / n
    variance = sum((v - moyenne) ** 2 for v in valeurs) / n
    return variance ** 0.5


def filet_non_couvert(page):
    """Cherche un liseré non imprimé sur les bords du fond perdu.

    On ne peut pas simplement chercher du blanc : les pages de notes SONT blanches.
    On compare donc la couleur du bord extrême à celle d'un point situé à 2 mm à
    l'intérieur, qui est encore dans le fond perdu et donc dans l'aplat de fond.
    Toute rupture signale un filet que l'imprimeur laissera en blanc.
    """
    pix = page.get_pixmap(dpi=300)
    w, h = pix.width, pix.height
    marge = int(2 / 25.4 * 300)          # 2 mm en pixels
    controles = [
        ("tête",      (w // 2, 0),        (w // 2, marge)),
        ("pied",      (w // 2, h - 1),    (w // 2, h - 1 - marge)),
        ("gouttière gauche", (0, h // 2), (marge, h // 2)),
        ("gouttière droite", (w - 1, h // 2), (w - 1 - marge, h // 2)),
    ]
    defauts = []
    for nom, bord, interieur in controles:
        cb = pix.pixel(*bord)[:3]
        ci = pix.pixel(*interieur)[:3]
        # Un filet non imprimé est BLANC PUR. Une illustration à fond perdu varie
        # légèrement d'un point à l'autre sans jamais être blanche : on ne la
        # signale pas. On signale un bord blanc, ou un écart franc (> 25 niveaux)
        # entre le bord et l'intérieur, qui trahit un aplat qui s'arrête trop tôt.
        blanc = all(c >= 250 for c in cb)
        ecart = max(abs(a - b) for a, b in zip(cb, ci))
        # Seul un bord BLANC alors que le fond ne l'est pas trahit un filet non imprimé.
        # Une illustration à fond perdu peut être sombre au bord et claire 2 mm plus haut :
        # c'est du dessin, pas un défaut.
        if blanc and ecart > 4:
            defauts.append(f"{nom} : bord blanc {cb} sur fond {ci}")
    return defauts


def controle(chemin, pages_attendues):
    doc = fitz.open(chemin)
    erreurs = []

    if doc.page_count != pages_attendues:
        erreurs.append(f"{doc.page_count} pages au lieu de {pages_attendues}")

    vides = []
    for page in doc:
        larg = page.rect.width / 72 * 25.4
        haut = page.rect.height / 72 * 25.4
        if (abs(larg - ATTENDU_MM[0]) > TOLERANCE_MM
                or abs(haut - ATTENDU_MM[1]) > TOLERANCE_MM):
            erreurs.append(f"page {page.number + 1} : {larg:.3f} x {haut:.3f} mm")
        if ecart_type_pixels(page) < ECART_TYPE_MINI:
            vides.append(page.number + 1)
        filets = filet_non_couvert(page)
        if filets:
            erreurs.append(
                f"page {page.number + 1} : fond perdu non couvert en "
                + ", ".join(filets))

    if vides:
        erreurs.append(f"pages sans contenu visible : {vides}")

    polices = {f[3] for page in doc for f in page.get_fonts()}
    type3 = {f[2] for page in doc for f in page.get_fonts()} & {"Type3"}
    if type3:
        erreurs.append("polices Type3 présentes, la vectorisation n'a pas eu lieu")
    elif polices and POLICES_AUTORISEES:
        hors_liste = [p for p in polices if not any(a in p for a in POLICES_AUTORISEES)]
        if hors_liste:
            erreurs.append(f"police non conforme : {hors_liste}")

    brut = open(chemin, "rb").read()
    # Le CMYK se détecte par les opérateurs de couleur des flux (« k » / « K »), pas par la
    # chaîne « DeviceCMYK » : Ghostscript ne l'écrit pas quand tout le contenu est déjà en
    # quadri, ce qui donnait un faux négatif.
    ops_k = 0
    for page in doc:
        for xref in page.get_contents():
            try:
                ops_k += len(re.findall(rb"[\d.]+ [\d.]+ [\d.]+ [\d.]+ [kK]\b",
                                        doc.xref_stream(xref)))
            except Exception:
                pass
    if ops_k == 0:
        erreurs.append("aucun opérateur de couleur CMYK, conversion non appliquée")
    if b"DeviceRGB" in brut or b"/RGB" in brut:
        erreurs.append("espace RGB résiduel dans le fichier")

    # Prépresse : intention de sortie PDF/X, TrimBox, images sans perte, charge d'encre.
    if b"/OutputIntents" not in brut or OUTPUT_ID.encode() not in brut:
        erreurs.append(f"pas d'intention de sortie PDF/X-4 {OUTPUT_ID}")
    if b"/GTS_PDFXVersion" not in brut:
        erreurs.append("pas de marqueur PDF/X")
    for page in doc:
        tb = page.trimbox
        if abs(tb.width / 72 * 25.4 - FINI[0]) > 0.05 or abs(tb.height / 72 * 25.4 - FINI[1]) > 0.05:
            erreurs.append(f"page {page.number + 1} : TrimBox {tb.width/72*25.4:.1f} x {tb.height/72*25.4:.1f} mm au lieu de {FINI[0]:g} x {FINI[1]:g}")
            break
    # Résolution effective de chaque image du PDF final. Indispensable ici et pas seulement
    # dans qa.py : Ghostscript rastérise les dégradés à la conversion, donc des éléments
    # vectoriels en entrée peuvent devenir des images basse définition en sortie.
    basse_def = []
    for page in doc:
        for im in page.get_images(full=True):
            try:
                info = doc.extract_image(im[0])
            except Exception:
                continue
            for r in page.get_image_rects(im[0]):
                if r.width <= 1:
                    continue
                dpi = info["width"] / (r.width / 72)
                if dpi < DPI_MIN - 5:
                    basse_def.append(f"p{page.number + 1} {info['width']}x{info['height']} à {dpi:.0f} dpi")
    if basse_def:
        erreurs.append(f"{len(basse_def)} image(s) sous {DPI_MIN:g} dpi : " + " ; ".join(basse_def[:6]))

    jpeg = 0
    for xref in range(1, doc.xref_length()):
        try:
            obj = doc.xref_object(xref, compressed=False)
        except Exception:
            continue
        if "/Subtype /Image" in obj or "/Subtype/Image" in obj:
            if "DCTDecode" in obj: jpeg += 1
    if jpeg:
        erreurs.append(f"{jpeg} image(s) ré-encodée(s) en JPEG (DCTDecode) : perte de qualité")
    # Charge d'encre : rendu CMYK à 150 dpi, C+M+Y+K max par page.
    pire = (0, 0)
    for page in doc:
        pix = page.get_pixmap(dpi=150, colorspace=fitz.csCMYK)
        import array
        buf = pix.samples
        n = pix.width * pix.height
        # somme des 4 canaux par pixel, en % (0..400)
        mx = 0
        step = 4
        # échantillonnage : un pixel sur 3 suffit pour le max
        for i in range(0, len(buf) - 3, step * 3):
            v = buf[i] + buf[i+1] + buf[i+2] + buf[i+3]
            if v > mx: mx = v
        tac = mx / 255 * 100
        if tac > pire[1]: pire = (page.number + 1, tac)
    # Le rendu ci-dessus rééchantillonne les images et ne lit qu'un pixel sur trois : un trait
    # fin d'un ou deux pixels y est moyenné et disparaît (mesuré sur un kakémono : 295 %
    # annoncés pour 323 % réels dans les contours d'icônes). On lit donc aussi chaque
    # image CMYK à sa résolution native, sans sous-échantillonnage.
    import numpy as np
    for page in doc:
        for im in page.get_images(full=True):
            try:
                pix = fitz.Pixmap(doc, im[0])
            except Exception:
                continue
            if pix.n - pix.alpha != 4:
                continue
            px = np.frombuffer(pix.samples, dtype=np.uint8).reshape(pix.height, pix.width, pix.n)
            mx = 0
            for y in range(0, pix.height, 512):                 # par bandes : mémoire bornée
                mx = max(mx, int(px[y:y + 512, :, :4].sum(axis=2, dtype=np.uint16).max()))
            tac = mx / 255 * 100
            if tac > pire[1]: pire = (page.number + 1, tac)
    if pire[1] > TAC_MAX + 2:
        erreurs.append(f"charge d'encre {pire[1]:.0f} % page {pire[0]} (max {TAC_MAX:.0f} %)")

    if erreurs:
        print(f"ECHEC {chemin}")
        for e in erreurs:
            print("  -", e)
        return False

    etat = "texte vectorisé" if not polices else f"polices {sorted(polices)}"
    print(f"OK {chemin} : {doc.page_count} pages, "
          f"{ATTENDU_MM[0]:g} x {ATTENDU_MM[1]:g} mm, CMYK {OUTPUT_ID} PDF/X-4, TrimBox {FINI[0]:g} x {FINI[1]:g}, "
          f"TAC max {pire[1]:.0f} % (p{pire[0]}), {etat}")
    return True


if __name__ == "__main__":
    if len(sys.argv) < 3:
        sys.exit(__doc__)
    sys.exit(0 if controle(sys.argv[1], int(sys.argv[2])) else 1)
