#!/usr/bin/env python3
"""Assemble le fichier complet de validation d'une brochure à couverture séparée.

Une brochure piquée se livre souvent en deux fichiers (à vérifier chez l'imprimeur) :
  - <prefixe>-couverture-print.pdf : les 4 pages de couverture C1, C2, C3, C4
  - <prefixe>-interieur-print.pdf  : les pages intérieures
Ce script produit un troisième fichier, pour la validation humaine uniquement, jamais
pour l'imprimeur :
  - <prefixe>-complet.pdf : C1, C2, pages intérieures, C3, C4, dans l'ordre de lecture

Usage : python3 14-print/lib/assembler.py <dossier_output> <prefixe> ["Titre du document"]
"""
import os
import sys

import fitz

if len(sys.argv) < 3:
    sys.exit(__doc__)
OUT, PREF = sys.argv[1], sys.argv[2]
TITRE = sys.argv[3] if len(sys.argv) > 3 else f"{PREF}, complet pour validation"

cv = fitz.open(os.path.join(OUT, f"{PREF}-couverture-print.pdf"))
it = fitz.open(os.path.join(OUT, f"{PREF}-interieur-print.pdf"))
if cv.page_count != 4:
    sys.exit(f"la couverture compte {cv.page_count} pages au lieu de 4 (C1, C2, C3, C4)")
doc = fitz.open()

doc.insert_pdf(cv, from_page=0, to_page=0)      # C1
doc.insert_pdf(cv, from_page=1, to_page=1)      # C2, intérieur de couverture
doc.insert_pdf(it)                              # pages intérieures
doc.insert_pdf(cv, from_page=2, to_page=2)      # C3, intérieur du dos
doc.insert_pdf(cv, from_page=3, to_page=3)      # C4

chemin = os.path.join(OUT, f"{PREF}-complet.pdf")
doc.set_metadata({"title": TITRE, "producer": "14-print/lib/assembler.py"})
doc.save(chemin, garbage=3, deflate=True)
print(f"{doc.page_count} pages -> {os.path.basename(chemin)} "
      f"(C1, C2, 1 à {it.page_count}, C3, C4)")
