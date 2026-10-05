#!/usr/bin/env python3
"""QA éditoriale et print d'un imprimé, à lancer sur le PDF *-qa.pdf de build.sh
(sortie Chrome, texte vivant). Contrôle ce que verify.py ne voit pas sur un PDF vectorisé :

  - corps de texte sous le minimum,
  - texte qui entre dans les marges de sécurité (côté reliure selon la parité de la page),
  - images placées sous la résolution minimale effective,
  - titres terminés par un point,
  - mots orphelins en fin de bloc,
  - textes qui se chevauchent, texte coupé par un aplat.

Usage : python3 14-print/lib/qa.py output/livrable-qa.pdf [--couverture]

Variables d'environnement (défauts : carnet A5 relié lu à 35 cm) :
  FORMAT_MM=148x210, BLEED_MAQUETTE (ou BLEED_IMPRIMEUR)=3
  SAFE_OUT_MM=12   marge de sécurité depuis la coupe (tête, pied, extérieur)
  SAFE_IN_MM=15    marge de sécurité côté reliure
  CORPS_MIN_PT=8   plus petit corps admis
  DPI_MIN=300      résolution effective minimale des images
  DEBORD_CORPS_PT, DEBORD_MM : un corps (ex. 15, celui des exergues) autorisé à mordre de
                   DEBORD_MM (ex. 6) sur la marge extérieure, quand c'est voulu
  Petit format non relié : SAFE_OUT_MM=3 SAFE_IN_MM=3 CORPS_MIN_PT=6.5
  Grand format lu debout : CORPS_MIN_PT=70 SAFE_OUT_MM=40 SAFE_IN_MM=40 DPI_MIN=150
"""
import os, sys, re
import fitz

MM = 72 / 25.4
# qa.py lit la sortie Chrome, composée au fond perdu de la MAQUETTE (plus large en grand format) ;
# à défaut, celui de l'imprimeur, égal à celui de la maquette sur les petits formats.
BLEED_MM = float(os.environ.get("BLEED_MAQUETTE", os.environ.get("BLEED_IMPRIMEUR", "3")))
FINI = tuple(float(v) for v in os.environ.get("FORMAT_MM", "148x210").split("x"))
PAGE_W, PAGE_H = (FINI[0] + 2*BLEED_MM) * MM, (FINI[1] + 2*BLEED_MM) * MM
BLEED = BLEED_MM * MM
# Marges de sécurité et corps minimal, réglés pour un carnet A5 relié. Un format qui
# n'est ni relié ni lu à distance de lecture (carte de visite, carton) impose ses propres
# valeurs : SAFE_OUT_MM, SAFE_IN_MM et CORPS_MIN_PT les redéfinissent.
SAFE_OUT = float(os.environ.get("SAFE_OUT_MM", "12")) * MM   # depuis la coupe
SAFE_IN = float(os.environ.get("SAFE_IN_MM", "15")) * MM     # côté reliure, depuis la coupe
MIN_PT_LEGENDE = float(os.environ.get("CORPS_MIN_PT", "8")) - 0.1   # tolérance d'arrondi
DPI_MIN = float(os.environ.get("DPI_MIN", "300")) - 5   # tolérance de 5 dpi ; 150 en grand format
DEBORD_CORPS = float(os.environ.get("DEBORD_CORPS_PT", "0"))   # 0 : aucun débord admis
DEBORD = float(os.environ.get("DEBORD_MM", "0")) * MM

def zone_sure(numero, couverture):
    """Rectangle autorisé pour le texte, en points, selon la parité de la page."""
    droite = (numero % 2 == 1)          # p.1 à droite, p.2 à gauche…
    if couverture:                       # C1 droite, C2 gauche, C3 droite, C4 gauche
        droite = (numero % 2 == 1)
    top = BLEED + SAFE_OUT
    bottom = PAGE_H - BLEED - SAFE_OUT
    if droite:
        left = BLEED + SAFE_IN;  right = PAGE_W - BLEED - SAFE_OUT
    else:
        left = BLEED + SAFE_OUT; right = PAGE_W - BLEED - SAFE_IN
    return fitz.Rect(left, top, right, bottom)

def qa(chemin, couverture=False):
    doc = fitz.open(chemin)
    problemes = []
    for page in doc:
        n = page.number + 1
        zs = zone_sure(n, couverture)
        # Le folio est souvent volontairement hors zone, en pied : on l'exclut.
        d = page.get_text("dict")
        for bloc in d["blocks"]:
            if bloc["type"] != 0: continue
            for ligne in bloc["lines"]:
                for span in ligne["spans"]:
                    txt = span["text"].strip()
                    if not txt: continue
                    taille = span["size"]
                    r = fitz.Rect(span["bbox"])
                    est_folio = (txt.isdigit() and r.y0 > PAGE_H - 16*MM)
                    if taille < MIN_PT_LEGENDE:
                        problemes.append(f"p{n}: corps {taille:.1f} pt < {MIN_PT_LEGENDE+0.1:g} pt : « {txt[:40]} »")
                    if not est_folio and not zs.contains(r):
                        # tolérance de 0,5 mm pour les arrondis de glyphes ; un corps déclaré
                        # (une exergue, par ex.) peut mordre sur la marge extérieure, c'est voulu
                        voulu = DEBORD_CORPS and abs(taille - DEBORD_CORPS) <= 0.5
                        tol = DEBORD if voulu else 1.4
                        if not fitz.Rect(zs.x0-tol, zs.y0-1.4, zs.x1+tol, zs.y1+1.4).contains(r):
                            cote = []
                            if r.x0 < zs.x0: cote.append("gauche")
                            if r.x1 > zs.x1: cote.append("droite")
                            if r.y0 < zs.y0: cote.append("haut")
                            if r.y1 > zs.y1: cote.append("bas")
                            problemes.append(f"p{n}: texte hors marge de sécurité ({', '.join(cote)}) : « {txt[:40]} »")
            # Titres avec point final : lignes en gros corps
            for ligne in bloc["lines"]:
                t = "".join(s["text"] for s in ligne["spans"]).strip()
                sz = max((s["size"] for s in ligne["spans"]), default=0)
                if sz >= 13 and t.endswith(".") and not t.endswith("..."):
                    problemes.append(f"p{n}: titre terminé par un point : « {t[:50]} »")
            # Orphelins : dernière ligne d'un bloc multi-lignes réduite à un seul mot court
            lignes = ["".join(s["text"] for s in l["spans"]).strip() for l in bloc["lines"]]
            lignes = [l for l in lignes if l]
            if len(lignes) >= 2 and len(lignes[-2]) > 25:     # vrai paragraphe, pas une colonne
                derniere = lignes[-1]
                if len(derniere.split()) == 1 and len(derniere) <= 12 and not derniere.isdigit() \
                        and not re.match(r"^\d\d:\d\d$", derniere):
                    problemes.append(f"p{n}: mot orphelin en fin de bloc : « {derniere} » (bloc : « {lignes[0][:30]}… »)")
        # Chevauchement : deux lignes de texte dont les boîtes se recouvrent nettement
        # trahissent un bloc passé sous un autre (une carte posée sur du texte, par ex.).
        lignes_bb = []
        for bloc in d["blocks"]:
            if bloc["type"] != 0: continue
            for ligne in bloc["lines"]:
                r = fitz.Rect(ligne["bbox"])
                if r.width > 3 and r.height > 3: lignes_bb.append((r, "".join(sp["text"] for sp in ligne["spans"]).strip()))
        vus = set()
        for i in range(len(lignes_bb)):
            for j in range(i + 1, len(lignes_bb)):
                a, ta = lignes_bb[i]; b, tb = lignes_bb[j]
                inter = a & b
                if inter.is_empty or inter.width < 4 or inter.height < 3: continue
                aire = inter.width * inter.height
                if aire > 0.35 * min(a.width * a.height, b.width * b.height):
                    if ta == tb and abs(a.x0 - b.x0) < 2 and abs(a.y0 - b.y0) < 2:
                        continue        # texte en dégradé : Chrome superpose le texte et son raster
                    cle = (ta[:20], tb[:20])
                    if cle in vus: continue
                    vus.add(cle)
                    problemes.append(f"p{n}: chevauchement de textes : « {ta[:30]} » / « {tb[:30]} »")
        # Texte sous un aplat : un rectangle plein dessiné APRÈS une ligne de texte la masque.
        # On liste les rectangles remplis (cartes) et on cherche les lignes de texte
        # entièrement contenues dedans qui ne font pas partie du contenu de la carte
        # (heuristique : la ligne est plus haute que le haut du rectangle de moins de 1 mm
        # ou déborde de lui). Approximation volontairement conservatrice.
        rects = []
        for dr in page.get_drawings():
            if dr.get("fill") is None: continue
            r = dr["rect"]
            if r.width > 30 * MM and r.height > 8 * MM and r.width < 140 * MM:
                rects.append(r)
        for r in rects:
            for (lb, tl) in lignes_bb:
                # le raster d'un chiffre en dégradé est un rectangle qui contient exactement
                # son texte transparent : ce n'est pas un aplat qui masque, on l'ignore
                if tl.strip().isdigit() and abs(lb.y0 - r.y0) < 3 * MM and abs(lb.x0 - r.x0) < 3 * MM:
                    continue
                # ligne qui chevauche le bord haut du rectangle : elle passe dessous
                if lb.x0 < r.x1 and lb.x1 > r.x0 and lb.y0 < r.y0 - 0.5 and lb.y1 > r.y0 + 0.5:
                    problemes.append(f"p{n}: texte coupé par un aplat : « {tl[:30]} »")
        # Images : dpi effectif
        for img in page.get_images(full=True):
            xref = img[0]
            try:
                info = doc.extract_image(xref)
                pw, ph = info["width"], info["height"]
            except Exception:
                continue
            for rect in page.get_image_rects(xref):
                if rect.width <= 0: continue
                dpi = pw / (rect.width / 72)
                if dpi < DPI_MIN:
                    problemes.append(f"p{n}: image {pw}x{ph}px affichée à {dpi:.0f} dpi (< {DPI_MIN+5:g})")
    if problemes:
        print(f"QA {chemin} : {len(problemes)} point(s)")
        for pb in problemes: print("  -", pb)
        return False
    print(f"QA OK {chemin} : {doc.page_count} pages, corps ≥ {MIN_PT_LEGENDE+0.1:g} pt, texte dans les marges, images ≥ {DPI_MIN+5:g} dpi")
    return True

if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    couv = "--couverture" in sys.argv
    sys.exit(0 if qa(sys.argv[1], couv) else 1)
