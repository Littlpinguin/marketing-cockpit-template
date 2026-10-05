# Chaîne d'export et contrôles

Scripts réutilisables pour tout imprimé. Aucun ne contient de valeur de marque : couleurs, police et formats arrivent par arguments ou variables d'environnement.

## Dépendances

| Outil | Rôle | Vérification |
|---|---|---|
| Google Chrome ou Chromium | HTML → PDF, captures (plaques, SVG) | détecté automatiquement, sinon `export CHROME=/chemin/vers/chrome` |
| Ghostscript ≥ 10 | séparation CMJN, PDF/X-4, vectorisation | `gs --version` |
| Python 3.10+ avec PyMuPDF, Pillow, numpy | montage, contrôles, K seul | `python3 -c "import fitz, PIL, numpy"` |
| fontTools (+ brotli pour le woff2) | `chiffre-svg.py` uniquement | `python3 -c "import fontTools"` |
| Profil ICC du papier | séparation et intention de sortie | voir `../icc/README.md` |

```bash
python3 -m pip install --user pymupdf pillow numpy fonttools brotli
```

## Réglages

Paramétrés par variables d'environnement :

```bash
export FORMAT_MM=148x210        # format fini ; défaut A5
export BLEED_IMPRIMEUR=3        # fond perdu attendu par l'imprimeur (2 ou 3 mm le plus souvent)
export ICCDIR=14-print/icc      # dossier des profils ; défaut 14-print/icc
export ICC_FICHIER=PSOuncoated_v3_FOGRA52.icc   # papier non couché (défaut)
```

Petit format non relié (carte de visite, carton) :

```bash
export FORMAT_MM=55x85 BLEED_IMPRIMEUR=2
export SAFE_OUT_MM=3 SAFE_IN_MM=3 CORPS_MIN_PT=6.5     # qa.py : les défauts visent un carnet A5
```

Grand format (kakémono, affiche, bâche), mêmes scripts, autres seuils :

```bash
export BLEED_MAQUETTE=13                   # fond perdu de la maquette HTML ; build.sh rogne au fond perdu imprimeur
export ICC_FICHIER=ISOcoated_v2_eci.icc    # film ou toile couchés : FOGRA39 au lieu de FOGRA52
export DPI_MIN=150 TAC_MAX=330 OUTPUT_ID=FOGRA39       # verify.py et qa.py
export CORPS_MIN_PT=70 SAFE_OUT_MM=40 SAFE_IN_MM=40    # qa.py : lisible à 3 m, 4 cm de garde
```

## Scripts

| Script | Rôle |
|---|---|
| `build.sh` | HTML → PDF/X-4 CMJN : Chrome, montage 1:1 avec TrimBox et BleedBox, séparation sur profil papier, texte vectorisé, noir et gris neutres en K seul |
| `verify.py` | Contrôle prépresse du PDF **final** : pages, format, PDF/X, intention de sortie, TrimBox, RGB résiduel, JPEG, charge d'encre, résolutions, fond perdu, polices |
| `qa.py` | Contrôle éditorial de la sortie Chrome : corps minimaux, marges de sécurité, dpi, titres, orphelins, chevauchements, texte sous aplat |
| `plaque.sh` | Capture en une image opaque tout ce qui se superpose sur une page (mode `body.plaque` de la maquette) |
| `assembler.py` | Assemble couverture et intérieur en un fichier complet de validation |
| `normaliser-portraits.py` | Recadre les portraits dans un carré au cadrage identique, pour des médaillons réguliers |
| `aplatir.py` | Supprime les canaux alpha en aplatissant chaque image sur son fond réel |
| `svg-en-png.sh` | Rend un SVG à opacités, dégradés ou masques en PNG opaque haute définition |
| `opacifier-svg.py` | Convertit les opacités d'un SVG en couleurs opaques équivalentes sur un fond uni |
| `chiffre-svg.py` | Rend un nombre en SVG, glyphes en tracés, dégradé continu (police et couleurs en arguments) |
| `chiffres-png.sh` | Rend ces SVG en PNG 600 dpi, seul moyen de garder un dégradé net |
| `blacktext.py` | Passe le texte, les filets et les gris neutres en noir K seul |
| `pdfx4.ps` | Intention de sortie PDF/X-4 pour Ghostscript (substituée par `build.sh`) |

## Exemple : une carte de visite avec plaque

```bash
P=14-print/lib; D=14-print/productions/exemple-carte
export FORMAT_MM=55x85 BLEED_MAQUETTE=3 BLEED_IMPRIMEUR=2
$P/plaque.sh $D/maquette/recto.html $D/maquette/assets/plaque-recto.png 600
$P/build.sh  $D/maquette/recto.html $D/output/carte-recto
SAFE_OUT_MM=3 SAFE_IN_MM=3 CORPS_MIN_PT=6.5 python3 $P/qa.py $D/output/carte-recto-qa.pdf
python3 $P/verify.py $D/output/carte-recto-print.pdf 1
```

Le profil ICC n'est **jamais** versionné : licence ECI, usage et embarquement libres, redistribution interdite (voir `../icc/README.md`).
