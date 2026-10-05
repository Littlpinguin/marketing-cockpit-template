#!/usr/bin/env python3
"""Passe le noir et les GRIS du texte et des filets en noir K seul, dans tous les flux de contenu.

Chrome n'émet que du RGB ; Ghostscript convertit donc un gris foncé de texte (le « noir »
d'une charte est souvent un anthracite) en un noir composé quatre couleurs, typiquement
au-delà de 250 % de charge d'encre. Sur du texte à 8-10 pt, un composé quatre couleurs
expose au moindre défaut de repérage ; la règle prépresse est : texte en K seul. Sur
papier non couché (FOGRA52), K 100 % est aussi sombre que le composé (L* ≈ 33).

Le tuple exact dépend du profil : on le relève dans le PDF plutôt que de le coder en dur,
en cherchant la couleur de remplissage sombre la plus fréquente (le texte courant).

Le texte courant n'est pas le seul gris d'une page : une mention en gris moyen ressort elle
aussi en quadri (mesuré sur une carte de visite : TAC 159 % sur un fût de 0,21 mm). Tout gris
NEUTRE est donc converti vers le K de même clarté, calculé par le profil du papier ; les
couleurs de marque (non neutres), elles, restent en quadri.

Usage : python3 14-print/lib/blacktext.py in.pdf out.pdf [profil.icc]
  profil.icc : à défaut, variable ICC_PROFIL, sinon 14-print/icc/PSOuncoated_v3_FOGRA52.icc.
  Sans profil lisible, seul le noir dominant est converti (les autres gris restent en quadri).
"""
import collections
import os
import re
import sys

import fitz

if len(sys.argv) < 3:
    sys.exit(__doc__)
src, dst = sys.argv[1], sys.argv[2]
ICC = (sys.argv[3] if len(sys.argv) > 3 else
       os.environ.get("ICC_PROFIL") or
       os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "icc",
                    "PSOuncoated_v3_FOGRA52.icc"))
doc = fitz.open(src)
TUPLE = re.compile(r'\b(\d*\.?\d+) (\d*\.?\d+) (\d*\.?\d+) (\d*\.?\d+) (k|K)\b')


def flux_de_contenu():
    """Tous les flux qui portent des opérateurs graphiques : contenus de page et XObjects Form."""
    vus = set()
    for page in doc:
        for x in page.get_contents():
            if x not in vus:
                vus.add(x)
                yield x
    for xref in range(1, doc.xref_length()):
        if xref in vus or not doc.xref_is_stream(xref):
            continue
        if '/Form' in doc.xref_object(xref, compressed=False):
            vus.add(xref)
            yield xref


# 1. Relever le noir dominant : le tuple sombre le plus fréquent (somme > 2.2, K > .5).
compte = collections.Counter()
for xref in list(flux_de_contenu()):
    s = doc.xref_stream(xref).decode('latin1', errors='ignore')
    for m in TUPLE.finditer(s):
        c, mm, y, k = (float(m.group(i)) for i in range(1, 5))
        if c + mm + y + k > 2.2 and k > .5:
            compte[m.group(0)[:-2]] += 1
if not compte:
    print("aucun noir composé trouvé")
    doc.save(dst)
    sys.exit(0)
noir, n_occ = compte.most_common(1)[0]
pat = re.compile(re.escape(noir) + r' (k|K)\b')


# 1 bis. Les autres gris neutres : convertis vers le K de même clarté (profil du papier).
def lab(cmjn):
    from PIL import Image, ImageCms
    im = Image.new("CMYK", (1, 1), tuple(round(v * 255) for v in cmjn))
    out = ImageCms.profileToProfile(im, ICC, ImageCms.createProfile("LAB"),
                                    outputMode="LAB", renderingIntent=1)
    L, a, b = out.getpixel((0, 0))
    return L * 100 / 255, a - 128, b - 128


def k_equivalent(cmjn):
    """K seul de même clarté, ou None si la couleur n'est pas neutre."""
    try:
        L, a, b = lab(cmjn)
    except Exception:
        return None
    if abs(a) > 4 or abs(b) > 4:          # couleur de marque : on n'y touche pas
        return None
    lo, hi = 0.0, 1.0
    for _ in range(14):                    # dichotomie sur K
        mid = (lo + hi) / 2
        if lab((0, 0, 0, mid))[0] > L:
            lo = mid
        else:
            hi = mid
    return round((lo + hi) / 2, 3)


gris = collections.Counter()
for xref in list(flux_de_contenu()):
    s = doc.xref_stream(xref).decode('latin1', errors='ignore')
    for m in TUPLE.finditer(s):
        t = m.group(0)[:-2]
        if t != noir:
            gris[t] += 1
remplaces = {}
if os.path.exists(ICC):
    for t in gris:
        cmjn = tuple(float(v) for v in t.split())
        if sum(cmjn) < .15:                # quasi blanc : rien à gagner
            continue
        k = k_equivalent(cmjn)
        if k is not None and k > .02:
            remplaces[t] = k
else:
    print(f"profil introuvable ({ICC}) : seuls les remplissages du noir dominant passent en K")

# 2. Substituer par K seul.
n, m_autres = 0, 0
motifs = [(pat, '0 0 0 1 ')] + [(re.compile(re.escape(t) + r' (k|K)\b'), f'0 0 0 {v} ')
                                for t, v in remplaces.items()]
for xref in list(flux_de_contenu()):
    s = doc.xref_stream(xref).decode('latin1', errors='ignore')
    total = 0
    for i, (p_, rempl) in enumerate(motifs):
        s, k = p_.subn(lambda mm: rempl + mm.group(1), s)
        total += k
        if i == 0:
            n += k
        else:
            m_autres += k
    if total:
        doc.update_stream(xref, s.encode('latin1'))
doc.save(dst, garbage=1, deflate=True)
print(f"noir dominant relevé : {noir} k ({n_occ} occurrences) -> {n} remplissages passés en K 100 %")
for t, v in remplaces.items():
    print(f"  gris neutre {t} k -> K {v*100:.0f} %")
if m_autres:
    print(f"  {m_autres} remplissages de gris neutres passés en K seul")
