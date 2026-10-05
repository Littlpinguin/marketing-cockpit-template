# 14-print — atelier print et prépresse {{COMPANY_NAME}}

> **Module optionnel** — activer via `/modules` (module `print`). Prérequis : Google Chrome ou Chromium, Ghostscript ≥ 10, Python 3 avec PyMuPDF, Pillow et numpy, et le profil ICC du papier déposé dans `icc/` (voir `icc/README.md`). Tant que le module est inactif, ignorer ce dossier.

## Rôle

Vous êtes l'atelier print de {{COMPANY_NAME}}. Tout ce qui part chez un imprimeur passe par ici : carnets, brochures, programmes, cartons, cartes de visite, affiches, kakémonos, étiquettes. Le rôle couvre les deux métiers que ces livrables demandent, et qui ne se remplacent pas : la **mise en page éditoriale** (ce qui se lit) et la **fabrication** (ce qui s'imprime).

Un imprimé n'est pas un écran : il se coupe, il se plie, il s'encre, et une erreur tirée à cinquante exemplaires ne se corrige pas.

## Références obligatoires

- Doctrine de marque : `../01-brand/style-guide.md` (palette, typographie, illustrations), `../01-brand/voice.md` et `../01-brand/checklist-pre-composition.md` si l'imprimé porte du texte rédigé, `../01-brand/assets/` (réutiliser avant de produire).
- Doctrines du module : `doctrine/doctrine-mise-en-page-editoriale.md` (grilles, échelle, rythme, gabarits de doubles pages, checklist de relecture) et `doctrine/doctrine-fabrication-brochure.md` (fond perdu, piqûre à cheval, couleur, encrage, papier, QR, préflight).
- Calendrier éditorial : `../02-strategy/calendar/calendar.md` — tout imprimé y a une entrée, avec sa date limite d'envoi à l'imprimeur.

## Ce qu'on trouve ici

| Dossier | Contenu |
|---|---|
| `doctrine/` | Les deux corpus de règles, sourcés : mise en page éditoriale et fabrication |
| `lib/` | La chaîne d'export PDF/X-4 CMJN et les contrôles, réutilisables tels quels (voir `lib/README.md`) |
| `gabarits/` | Feuille de style A5 sur grille et page de contrôle, à adapter au format |
| `icc/` | Profils ICC des papiers, **non versionnés** (licence ECI), voir `icc/README.md` |
| `productions/` | Les imprimés produits, un sous-dossier par livrable (ignorés par Git dans le template ; un fork peut versionner leurs sources, jamais les PDF ni les rendus) |

## La règle qui commande tout : aucune transparence dans le PDF

Ghostscript aplatit toute transparence à **72 dpi** lors de la conversion CMJN, quelle que soit la résolution d'origine. Une illustration pleine page passe ainsi de 300 à 72 dpi sans qu'aucun message ne l'annonce. Tout ce qui doit se superposer (filigrane, opacité, dégradé, dessin, bloc de couleur, icône) est donc **composé en amont dans une plaque opaque**, puis aplati sur la couleur de son fond. Le HTML ne porte plus que du texte vivant et des vecteurs pleins.

Ce n'est pas une préférence, c'est une contrainte de la chaîne. Les scripts de `lib/` existent pour l'appliquer.

## La chaîne

```bash
P=14-print/lib
export FORMAT_MM=148x210          # format fini : 148x210 (A5), 210x297 (A4), 55x85 (carte)…
export BLEED_IMPRIMEUR=3          # fond perdu demandé par l'imprimeur retenu : 2 ou 3 mm le plus souvent

python3 $P/normaliser-portraits.py assets/portraits    # cadrage identique des médaillons
python3 $P/aplatir.py assets/illustrations FFFFFF      # supprime les canaux alpha, sur le fond réel
$P/svg-en-png.sh source.svg sortie.png 2000 2000       # SVG à opacités -> PNG opaque
$P/plaque.sh maquette/pages.html assets/plaque.png     # superpositions -> une plaque opaque
$P/build.sh maquette/pages.html output/livrable        # HTML -> PDF/X-4 CMJN
python3 $P/verify.py output/livrable-print.pdf 24      # contrôle prépresse du PDF final
python3 $P/qa.py output/livrable-qa.pdf                # contrôle éditorial de la sortie Chrome
python3 $P/assembler.py output livrable                # fichier complet pour validation
```

`build.sh` enchaîne : Chrome headless → montage 1:1 avec TrimBox et BleedBox → séparation CMJN sur le profil du papier avec intention de sortie PDF/X-4 → texte vectorisé → texte et gris neutres en noir K seul.

## Les pièges, tous constatés et mesurés

| Piège | Ce qui se passe | Parade |
|---|---|---|
| CSS externe et Chrome | pages vides au bon format, sans aucun message | `--virtual-time-budget=10000` ; `verify.py` détecte les pages vides |
| `overflow: visible` sur la page | un débord élargit le document, Chrome réduit toute la page (mesuré : corps 8 pt sorti à 7,3) | garder `overflow: hidden`, faire déborder par une `@page` d'un pixel de plus |
| Police variable | Chrome l'embarque en Type 3, mal digéré par les RIP | `-dNoOutputFonts` : texte vectorisé |
| Transparence | aplatie à 72 dpi | composer en amont dans une plaque, aplatir sur le fond |
| Image opaque posée sur un décor | elle masque le décor sur **toute sa boîte**, pas seulement sur son dessin | l'intégrer à la plaque au lieu de la poser dans la page |
| Dégradé sur du texte | rastérisé, et le masque est perdu à la conversion : il ne reste qu'un rectangle | `chiffre-svg.py` (glyphes en tracés) puis `chiffres-png.sh` (600 dpi) |
| `-dMaxShadingBitmapSize` augmenté | Ghostscript perd silencieusement des objets | ne jamais y toucher |
| `background-image` CSS, `<pattern>` SVG | rastérisés à 72 dpi | `<rect>` et `<circle>` explicites en SVG inline |
| Chrome et les couleurs | n'émet que du RGB, le noir et les gris deviennent des composés quatre couleurs | `blacktext.py` : texte et gris neutres en K seul |
| Profil couché sur papier non couché | couleurs plus ternes que l'épreuve, encrage trop fort | PSO Uncoated v3 (FOGRA52) sur non couché |
| Flexbox colonne | l'image d'un chiffre est étirée en largeur | `align-self: flex-start` |
| Contrôle de résolution | invisible avant conversion | contrôler le PDF **final**, jamais la sortie Chrome |
| Charge d'encre d'un trait fin | un rendu sous-échantillonné la moyenne et la sous-estime | lire chaque image CMJN à sa résolution native (`verify.py` le fait) |
| Calage d'un élément sur du texte | les boîtes de ligne partent de l'ascendante : ≈ 1 mm d'erreur | mesurer la boîte d'**encre** sur un rendu, relever la position dans le PDF |
| QR code | une zone de silence intégrée au SVG fait tomber le module sous 0,5 mm | générer le symbole sans marge, poser la zone de silence en CSS, sur un fond d'une seule couleur |

## Méthode

Pour produire un imprimé, invoquer la skill **`print`**, qui déroule la méthode complète, du chemin de fer au fichier imprimeur.

Deux agents complètent le travail, à dispatcher avant toute commande :

- **`print-preflight`** : audit prépresse du PDF final (format, boîtes, couleur, encrage, résolutions, filets, polices, QR) ;
- **`print-editorial`** : revue de mise en page double page par double page (grille, hiérarchie, rythme, mesure de ligne, blancs).

## Seuils selon le format

Les valeurs par défaut des contrôles visent un carnet A5 relié lu à 35 cm. Un autre format impose les siennes, par variables d'environnement (détail dans `lib/README.md`) :

| Format | Réglages |
|---|---|
| Carnet, brochure, programme (défaut) | marges de sécurité 12 / 15 mm, corps ≥ 8 pt, ≥ 300 dpi, TAC ≤ 300 % |
| Petit format non relié (carte de visite, carton) | `SAFE_OUT_MM=3 SAFE_IN_MM=3 CORPS_MIN_PT=6.5` |
| Grand format lu debout (kakémono, affiche, bâche) | `BLEED_MAQUETTE` élargi, `DPI_MIN=150`, profil et `TAC_MAX` du support, `CORPS_MIN_PT=70`, gardes de 40 mm |

## Règles fermes

1. **Aucun livrable n'est commandé sans que `verify.py` et `qa.py` répondent OK**, sans les deux audits d'agents, et sans une épreuve papier à l'échelle 1 (pliée et agrafée pour une brochure).
2. **Le format de données se lit chez l'imprimeur**, jamais de mémoire : fond perdu attendu, pages simples ou planches, couverture séparée, profil exigé, grammages réellement disponibles. On le consigne dans le README de la production.
3. **Un fait imprimé est définitif.** Tout chiffre, date ou nom propre est sourcé avant composition, dans `contenus/00-faits-verifies.md` à côté des contenus. Un fait absent de ce fichier n'entre pas dans le livrable.
4. **La doctrine de marque prime** : `01-brand/` pour la palette, la typographie et les illustrations ; on réutilise les assets existants avant d'en produire ; brand-check avant commande.
5. **Divulgation IA** : si une illustration de l'imprimé est générée, la mentionner selon la politique de divulgation de la marque, au colophon ou en mention discrète.
