---
name: print
description: Produit un imprimé de {{COMPANY_NAME}} destiné à un imprimeur — carnet, brochure, programme, carton, carte de visite, affiche, kakémono, étiquette. Couvre la méthode complète : chemin de fer, contenus sourcés, maquette HTML/CSS sur grille, plaque opaque pour tout ce qui se superpose, chaîne d'export PDF/X-4 CMJN, contrôles automatiques, audits et préparation de la commande. Utiliser cette skill dès qu'un livrable doit être imprimé sur papier, y compris pour reprendre ou corriger un imprimé existant. Module `print` (dossier `14-print/`). Pour un deck projeté, utiliser `slides` ; pour un carrousel LinkedIn, `carousel`.
---

# print — imprimés {{COMPANY_NAME}}, de la maquette au fichier imprimeur

Tu produis un objet imprimé. Un imprimé n'est pas un écran : il se coupe, il se plie, il s'encre, et **une erreur tirée à cinquante exemplaires ne se corrige pas**. La méthode ci-dessous existe pour que rien ne parte au hasard.

## Préflight

1. **Module actif ?** Lire `.setup-completed.modules.print`. S'il est absent ou `enabled: false` : répondre « Ce module n'est pas actif — lancez `/modules` pour l'activer » et s'arrêter.
2. **Outillage présent ?** `gs --version` (≥ 10), Chrome ou Chromium, `python3 -c "import fitz, PIL, numpy"`, et le profil ICC du papier dans `14-print/icc/` (voir `14-print/icc/README.md`). Un manque se signale avant de composer, pas au moment de l'export.
3. **Gabarit relié à la marque ?** Si `14-print/gabarits/print-a5.css` porte encore les valeurs neutres (`#5D6B7E`, `system-ui`), y reporter d'abord les valeurs de `01-brand/style-guide.md` en suivant les commentaires `← BRAND_*`, et embarquer la police de marque en local (`01-brand/assets/fonts/`).

## Avant tout

Charger, dans cet ordre :

1. `14-print/CLAUDE.md` : la chaîne, les pièges, les seuils par format, les règles fermes.
2. `14-print/doctrine/doctrine-mise-en-page-editoriale.md` : grilles, échelle typographique, rythme, gabarits de doubles pages, checklist de relecture.
3. `14-print/doctrine/doctrine-fabrication-brochure.md` : fond perdu, piqûre à cheval, couleur, encrage, papier, QR, exigences des imprimeurs en ligne, préflight.
4. `01-brand/style-guide.md` et `01-brand/assets/` : palette, typographie, illustrations, et surtout **les assets existants** : on réutilise avant de produire.
5. `01-brand/voice.md` et `01-brand/checklist-pre-composition.md` si le livrable porte du texte rédigé (règles anti-style-IA comprises).
6. Le README d'une production existante de même nature dans `14-print/productions/` : ses pièges sont ceux du prochain.

## Méthode

### 1. Cadrer avant de composer

Établir, et faire valider : l'**objectif** de l'imprimé (ce qu'il doit produire chez celui qui le tient), le **format fini**, la **reliure**, le **nombre de pages** (multiple de 4 en piqûre à cheval), le **papier**, le **tirage**, l'**imprimeur**, et la **date limite d'envoi** en remontant depuis la date de livraison (production + transport + 3 jours de marge). Inscrire cette date au calendrier éditorial.

Lire la **fiche technique de l'imprimeur** pour le produit configuré : fond perdu, zone de sécurité, profil ICC, PDF/X, polices vectorisées acceptées ou non, nombre de fichiers et ordre des pages. La consigner dans le README de la production (`14-print/productions/README.md` donne la structure).

Écrire le **chemin de fer** double page par double page avant toute maquette : gabarit, élément dominant, densité. Vérifier que chaque double page tombe bien en vis-à-vis : une double page conçue à cheval sur une pliure est perdue.

### 2. Sourcer les faits

Ouvrir `contenus/00-faits-verifies.md` et n'y mettre que des faits vérifiés, avec leur source et leur date. **Un fait absent de ce fichier n'entre pas dans le livrable.** Les chiffres viennent de `01-brand/messaging-framework.md` ou de ce qui a été communiqué publiquement, jamais d'une estimation. Calculer ce qui se calcule (distances, durées, totaux) plutôt que l'estimer. Un écart entre deux sources (un chiffre publié contre celui de la doctrine) se remonte à l'humain, il ne se tranche pas seul.

### 3. Composer sur une grille

Partir de `14-print/gabarits/print-a5.css`, adapté au format (le commentaire d'en-tête donne le calcul des dimensions de page en pixels). Poser une grille de base dont l'unité est l'interligne du corps, et des lignes d'accroche communes aux deux pages d'une double. Varier les découpes de la grille d'une double à l'autre, garder le même rythme vertical : c'est ce qui distingue un imprimé d'un document.

Un héros par double page, et un seul. Le blanc se compose, il ne se subit pas.

Sur un support lu debout et à distance (affiche, kakémono, stand) : peu de texte, un titre, deux chiffres clés avec un libellé court plutôt qu'un paragraphe, un appel à l'action ; corps lisibles à 3 m.

### 4. Préparer les images et la plaque

Aucune transparence ne doit subsister dans le PDF (voir `14-print/CLAUDE.md`) :

```bash
P=14-print/lib
python3 $P/normaliser-portraits.py <dossier>          # médaillons au cadrage identique
python3 $P/aplatir.py <dossier|image> <fond_hex>      # alpha supprimé, sur le fond réel
python3 $P/opacifier-svg.py <fichier.svg> [fond_hex]  # opacités SVG -> couleurs pleines
$P/svg-en-png.sh in.svg out.png <w> <h> [fond_hex]    # SVG à dégradé ou masque -> PNG opaque
```

Tout ce qui se **superpose** (filigrane, dégradé, dessin posé sur un décor, bloc de couleur sous une illustration) se compose dans une **plaque opaque** : la maquette porte deux modes (`body.impression` / `body.plaque`, voir l'en-tête de `lib/plaque.sh` et la fin du gabarit), et la plaque est capturée depuis la maquette elle-même, donc au pixel près :

```bash
$P/plaque.sh maquette/pages.html maquette/assets/plaque.png 600 <fond_hex>
```

Le HTML ne porte plus que le texte vivant et des vecteurs pleins (QR, filets). Pour caler un élément de la plaque sur du texte, relever sa position **dans le PDF** (boîte d'encre mesurée sur un rendu), jamais de tête ni sur les boîtes de ligne.

Pour un chiffre en dégradé, jamais de `background-clip: text` :

```bash
python3 $P/chiffre-svg.py 42 --police 01-brand/assets/fonts/<police>.woff2 --de "<couleur 1>" --a "<couleur 2>" > maquette/assets/chiffres/42.svg
$P/chiffres-png.sh maquette/assets/chiffres 42:26.8      # rendu 600 dpi à la hauteur d'usage (mm)
```

QR code : générer le symbole **sans zone de silence**, poser la zone de silence (4 modules) en CSS sur un fond d'une seule couleur ; garder les données courtes pour que le module reste ≥ 0,5 mm.

### 5. Exporter et contrôler

```bash
export FORMAT_MM=148x210 BLEED_IMPRIMEUR=3          # valeurs de la fiche technique de l'imprimeur
$P/build.sh maquette/pages.html output/livrable
python3 $P/verify.py output/livrable-print.pdf <pages>
python3 $P/qa.py output/livrable-qa.pdf
```

Les deux contrôles doivent répondre OK. Ils vérifient le format au centième de millimètre, les boîtes, la couleur, l'encrage, les résolutions du **PDF final**, les polices, les corps minimaux, les marges, les chevauchements, les orphelins. Pour un petit format ou un grand format, régler d'abord les seuils (`14-print/CLAUDE.md`, « Seuils selon le format ») : les défauts visent un carnet A5 et refusent à tort une carte de visite.

### 6. Faire auditer

Dispatcher les deux agents **en parallèle** avant la commande :

- `print-preflight` sur le PDF final ;
- `print-editorial` sur la maquette et le rendu.

Puis passer le texte au filtre `brand-check` (vocabulaire, ton, preuve, visuel). Corriger, reconstruire, relancer les contrôles. Ne jamais livrer sur la foi d'un seul regard.

### 7. Épreuve et commande

Imprimer en taille réelle sur une imprimante de bureau, plier, **emboîter** les feuilles (la première dehors, la centrale au cœur), agrafer, relire à bout de bras. C'est le seul contrôle qui dit si le corps de texte tient et si l'ordre des pages est juste. Faire relire les noms propres par quelqu'un d'autre. Scanner les QR sur le papier, avec deux téléphones.

Puis revérifier chez l'imprimeur le fond perdu attendu, la livraison en pages simples, le grammage réellement disponible, et préparer la commande. **La commande, le paiement et l'envoi des fichiers restent une action humaine** : présenter le récapitulatif (fichiers, produit, options, date limite) et attendre la validation.

## Checklist avant commande

- [ ] `verify.py` et `qa.py` OK sur la dernière version des fichiers, avec les seuils du format
- [ ] `print-preflight` et `print-editorial` passés sur le PDF final, défauts bloquants corrigés
- [ ] `brand-check` passé sur les textes
- [ ] Épreuve papier pliée et relue à bout de bras, noms propres relus par quelqu'un d'autre, QR scannés sur papier
- [ ] Fiche technique de l'imprimeur et décisions consignées dans le README de la production
- [ ] Divulgation IA selon la politique de la marque si une illustration de l'imprimé est générée : mention au colophon, au même corps que les crédits d'impression
- [ ] Entrée du calendrier éditorial à jour (statut, date limite d'envoi)

## Ce qui fait échouer un imprimé

- Composer avant d'avoir le chemin de fer et la fiche technique de l'imprimeur.
- Faire confiance à l'écran pour la couleur : une couleur de marque saturée est souvent hors gamut CMJN et sortira plus terne, surtout sur papier non couché.
- Laisser un texte sous 8 pt (6,5 pt sur une carte), un filet sous 0,25 pt, ou une réserve blanche en petit corps.
- Un dégradé, une opacité ou une image posée sans vérifier ce qu'elle devient après conversion. Toujours mesurer sur le PDF final.
- Un chiffre non sourcé, un nom mal orthographié, un QR non testé.
- Livrer à l'imprimeur le fichier complet de validation au lieu des fichiers qu'il exige.
