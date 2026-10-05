---
title: "Doctrine de fabrication – brochure piquée à cheval et petits tirages numériques chez un imprimeur en ligne"
type: doctrine
version: 1.0
perimetre: fabrication et prépresse (fond perdu, imposition, couleur, papier, traits, images, QR, épreuvage, préflight). La mise en page éditoriale est traitée dans doctrine-mise-en-page-editoriale.md et n'est pas reprise ici.
chaine: HTML/CSS → Chrome headless (PDF) → Ghostscript (CMJN, texte vectorisé) → PyMuPDF (format) ; contrôles python3 (PyMuPDF, PIL, numpy) et Ghostscript — scripts dans 14-print/lib/
---

# Doctrine de fabrication d'un imprimé en petit tirage numérique

Ce document fixe ce qu'un fichier doit être pour sortir correctement d'un imprimeur en ligne, avec pour cas d'étude le plus exigeant : une brochure piquée à cheval, quadrichromie numérique, papier non couché, quelques dizaines d'exemplaires. Les règles valent pour les autres imprimés (cartons, cartes, affiches) ; ce qui change pour eux est signalé. Il distingue :

- **[EXIGENCE]** : ce que les imprimeurs en ligne demandent explicitement dans leurs fiches techniques ; le non-respect provoque un rejet, une correction automatique non maîtrisée ou un défaut d'impression ;
- **[RECOMMANDATION]** : bonne pratique convergente de plusieurs sources ; le non-respect dégrade le résultat sans être bloquant ;
- **[MESURE]** : fait constaté sur la chaîne de `14-print/lib/` (Chrome 151, Ghostscript 10.07, PyMuPDF 1.28, 2026), reproductible avec les commandes données.

Les exigences d'imprimeurs ont été relevées en 2026 sur les fiches publiques de plusieurs imprimeurs en ligne européens ; elles **varient d'un imprimeur à l'autre**. La fiche technique du produit configuré chez l'imprimeur retenu fait toujours foi, et se consigne dans le README de la production. Les sources générales sont listées en §11.

---

## 0. Les quinze règles fermes (à relire avant tout envoi)

| # | Règle | Valeur | Statut |
|---|---|---|---|
| 1 | Nombre de pages intérieures multiple de 4 ; couverture 4 pages comptée à part ou incluse selon l'imprimeur | ex. 24 + 4 | [EXIGENCE] universelle |
| 2 | Fichier en **pages simples consécutives, dans l'ordre de lecture**, jamais en planches imposées ; l'imprimeur impose lui-même | 1 fichier intérieur (ou 1 seul fichier C1→C4) ; certains imprimeurs demandent 3 fichiers (C1 / C2 + intérieur + C3 / C4) | [EXIGENCE] |
| 3 | Format de données = format fini + fond perdu **de l'imprimeur choisi**, en taille réelle, sans traits de coupe | 2 mm (A5 → 152 × 214) ou 3 mm (A5 → 154 × 216) selon l'imprimeur | [EXIGENCE] |
| 4 | Zone de sécurité : rien d'important à moins de 3–5 mm de la coupe (valeur de la fiche technique) ; côté pli, 3 mm sans détail | ≥ 5 mm partout dans le gabarit | [EXIGENCE] 3 à 5 mm selon l'imprimeur, jusqu'à 15 mm côté reliure pour les dos collés |
| 5 | Couleur en CMJN, séparée avec le **profil du papier** : non couché = PSO Uncoated v3 (FOGRA52) ; couché = PSO Coated v3 (FOGRA51) ou ISO Coated v2 (FOGRA39) selon l'imprimeur | non couché : `PSOuncoated_v3_FOGRA52.icc` | [EXIGENCE] chez une partie des imprimeurs ; d'autres demandent ISO Coated v2 même sur non couché |
| 6 | Charge d'encre totale (TAC) ≤ 300 % ; ≥ 10 % par ton (pas de tons < 10 % qui « ne montent pas ») | 300 % (profil FOGRA52 = 300 %, presses HP Indigo : 280 % recommandés) | [EXIGENCE] chez certains ; [RECOMMANDATION] ailleurs |
| 7 | Texte noir en **100 % K** (pas de noir composé pour le texte courant) ; noir riche réservé aux grands aplats | corps et légendes : 0/0/0/100 | [EXIGENCE] |
| 8 | Filets : ≥ 0,25 pt (0,09 mm) en positif, ≥ 0,5 pt (0,18 mm) en réserve, et ≥ 40 % d'encre pour un filet fin | pas de « hairline », pas de filet pâle à 15 % | [EXIGENCE] (0,125 pt à ≥ 40 % chez les plus tolérants) |
| 9 | Corps minimal 6 pt (imprimeurs) ; 8 pt en pratique pour du non couché ; en réserve : ≥ 8 pt et graisse ≥ 600 | légendes 8 pt, corps 10 pt | [EXIGENCE] 6 pt ; [RECOMMANDATION] 8 pt |
| 10 | Polices incorporées **ou** vectorisées ; PDF non protégé par mot de passe | vectorisé (`-dNoOutputFonts`) accepté presque partout ; certains imprimeurs exigent des polices incorporées | [EXIGENCE] |
| 11 | Résolution : ≥ 300 dpi photos et illustrations tramées à taille finale (250 acceptés chez certains) ; trait 1 bit 1 200 dpi | rasters ≥ 300 dpi ; trait au format vectoriel de préférence | [EXIGENCE] |
| 12 | Transparence : acceptée en PDF/X-4 ; aplatie automatiquement en PDF/X-3 ; ne jamais fournir un PDF < 1.4 avec transparence rendue en bitmap pleine page | PDF/X-4:2010 ou PDF 1.6/1.7 avec transparence native, ou mieux : aucune transparence (plaque opaque) | [EXIGENCE] |
| 13 | Pas de traits de coupe, de repères, de commentaires, de champs de formulaire, de calques (OCG) ; orientation identique sur toutes les pages | | [EXIGENCE] |
| 14 | QR code : module ≥ 0,5 mm (≥ 2 × 2 cm de côté), zone de silence 4 modules, contraste fort, correction d'erreur M ou Q, **testé imprimé** | | [RECOMMANDATION] Denso Wave / ISO 18004 [S13][S14] |
| 15 | Épreuve papier pliée-agrafée avant commande ; contrôle des tons pâles, du QR et du pli ; l'écran ne montre ni le non couché ni le TAC | | [RECOMMANDATION] |

---

## 1. Vocabulaire et grandeurs

| Terme | Définition | Valeur type (A5 piqué) |
|---|---|---|
| Format fini (Endformat, trim) | Le format après coupe | 148 × 210 mm |
| Fond perdu (Anschnitt, bleed) | Bande de couleur ou d'image au-delà de la coupe, supprimée au massicot ; absorbe la tolérance de coupe (jusqu'à ±1 mm annoncé) | 3 mm dans la maquette (154 × 216) ; 2 mm chez une partie des imprimeurs |
| Zone de sécurité (Sicherheitsabstand) | Distance minimale entre la coupe et tout élément important | 12 mm extérieur, 15 mm intérieur dans le gabarit |
| Format de données (Datenformat) | Format fini + fond perdu, ce que doit mesurer chaque page du PDF | 152 × 214 (2 mm) ou 154 × 216 (3 mm) |
| Piqûre à cheval (Rückendrahtheftung, saddle stitch) | Feuilles pliées en deux, emboîtées, agrafées au pli | 24 pages = 6 feuilles + couverture |
| Chasse (Bundzuwachs, creep, shingling) | Décalage des pages intérieures vers l'extérieur du fait de l'épaisseur du papier plié | ≈ 0,7–0,8 mm au cahier central pour 24 p. en 120 g (calcul §2.2) |
| Imposition (Ausschießen) | Disposition des pages sur la feuille d'impression | faite par l'imprimeur |
| TAC (Gesamtfarbauftrag, total area coverage) | Somme C+M+Y+K d'un point, en % | ≤ 300 % |
| TVI (dot gain, engraissement) | Écart entre valeur de ton du fichier et valeur imprimée | 22 % pour FOGRA52 (contre ≈ 13–16 % sur couché) [S11] |
| Profil ICC de sortie | Description colorimétrique du couple presse/papier utilisée pour la séparation | PSO Uncoated v3 (FOGRA52) sur non couché |
| PDF/X | Sous-ensembles ISO 15930 du PDF pour l'échange imprimeur : X-1a (CMJN seul, sans transparence), X-3 (couleur gérée, sans transparence), X-4 (transparence native, calques) | X-4:2010 |
| Intention de sortie (OutputIntent) | Profil ICC déclaré dans le PDF/X qui dit « ce fichier a été séparé pour cette condition d'impression » | à embarquer (`build.sh` le fait) |
| BAT (bon à tirer) | Épreuve validée avant tirage ; « BAT numérique » = simple aperçu à l'écran, sans valeur colorimétrique | à faire sur papier |

---

## 2. Piqûre à cheval

### 2.1 Nombre de pages, couverture, ordre

- **Multiple de 4** pour les pages intérieures : chaque feuille pliée porte 4 pages. Les produits en ligne vont en général de 4 à 64–128 pages, la reliure collée étant conseillée au-delà de 64 ; au-delà de 40 pages en 120 g, la chasse et le refus de « rester fermé » deviennent des sujets. **[EXIGENCE]**
- **La couverture** compte 4 pages (C1, C2, C3, C4). Selon l'imprimeur, elle se livre soit dans le même PDF que l'intérieur (C1, C2, p. 1…n, C3, C4, « en ordre chronologique, du titre au dos »), soit dans un fichier séparé, soit en trois fichiers (C1 seule, un PDF multipage C2 + intérieur + C3, C4 seule). **Lire la fiche technique du produit configuré ; ne pas deviner.** `lib/assembler.py` produit le fichier complet de validation à partir d'une couverture séparée.
- **Vérifier dans le configurateur si le champ « nombre de pages » inclut la couverture.** Certains distinguent « pages intérieures » et option couverture, d'autres comptent C1 à C4 dans le total.
- **Pages simples, jamais de planches** : les imprimeurs demandent d'exporter les doubles pages en pages simples consécutives et font l'imposition eux-mêmes. **[EXIGENCE]**
- Une page blanche voulue est une page du PDF.

### 2.2 Chasse (creep) : calcul et seuil de visibilité

- Formule courante chez les imprimeurs en ligne : chasse (mm) = pages ÷ 4 × grammage ÷ 1000 ; pour **24 pages en 120 g : 24 ÷ 4 × 0,120 = 0,72 mm** (48 pages en 135 g ≈ 1,6 mm).
- Formule anglo-saxonne : chasse = (pages ÷ 4 − 1) × épaisseur du papier ; 120 g offset ≈ 0,15 mm d'épaisseur → 5 × 0,15 = **0,75 mm** [S15].
- Ce que ça fait : les feuilles intérieures dépassent à la tranche avant coupe ; après massicotage à format, la marge extérieure des pages centrales est réduite d'autant par rapport aux pages près de la couverture. Le pli n'est pas concerné (la marge intérieure ne bouge pas).
- Seuil : sous 40 pages, la chasse est le plus souvent à peine visible et n'a pas besoin d'être compensée ; certains l'ajustent dès 24 pages selon le papier [S15]. **[RECOMMANDATION]** Sous 40 pages en 120 g : ne pas compenser dans le fichier ; absorber par la zone de sécurité extérieure (≥ 5 mm) et par des constantes (folio, filet de marge) placées à ≥ 6 mm de la coupe, dont une dérive de 0,8 mm entre première et dernière page reste invisible à l'œil non averti.
- Les logiciels d'imposition des imprimeurs peuvent compenser la chasse ; aucune documentation publique ne le garantit – d'où la consigne de zone de sécurité plutôt qu'une correction dans le fichier.

### 2.3 Marge côté pli, images à cheval, double page centrale

- Un cahier piqué de 24–32 pages s'ouvre presque à plat : la marge intérieure peut rester proche de la marge extérieure (gabarit : 15 mm intérieur, 12 mm extérieur, hors fond perdu). Pour un dos collé, compter 15 mm côté reliure. **[RECOMMANDATION]** intérieur ≥ 12 mm depuis la coupe.
- **Traversée de gouttière** (filet, image, titre) : possible en piqûre, à trois conditions : même hauteur exacte sur les deux pages, aucun texte ni détail fin *sur* le pli, une bande de 3 mm de part et d'autre du pli sans élément critique (l'alignement des deux moitiés dépend du pliage, tolérance ≈ ±0,5 mm ; à la double page centrale, l'alignement est parfait puisque c'est la même feuille ; sur les autres doubles pages, deux feuilles différentes) [S15]. On lit parfois qu'il faut éviter tout élément qui traverse deux pages sur une piqûre parce que la chasse le désaligne : c'est vrai pour un élément qui traverse **vers la tranche** ; un filet horizontal qui traverse le pli n'est pas concerné par la chasse (elle agit à la tranche, pas au pli).
- La double page centrale est la seule où une image peut traverser sans risque de décalage ; c'est aussi celle où la chasse est maximale à la tranche.

### 2.4 Couverture épaisse et rainage

- Les couvertures proposées en ligne pour une brochure piquée montent en général à 250–300 g ; les grammages disponibles dépendent du produit et du papier (offset, recyclé, couché). Vérifier dans le configurateur avant de promettre un papier.
- Au-delà de 200–250 g, la couverture doit être **rainée** avant pliage, sinon le pli casse (fibres blanches sur le dos, surtout si de l'encre couvre le pli). Les imprimeurs en ligne rainent en général les couvertures lourdes (le vérifier sur la fiche produit) ; un dos avec un aplat foncé sur le pli reste le cas le plus fragile [S17]. **[RECOMMANDATION]** Pas d'aplat sombre à cheval sur le pli de couverture ; sens des fibres parallèle au pli (non maîtrisable en ligne, mais un dos blanc pardonne tout).

---

## 3. Fond perdu, zone de sécurité, format de fichier : ce que demandent les imprimeurs en ligne

Fourchettes relevées en 2026 sur les fiches publiques de plusieurs imprimeurs en ligne européens (produit : brochure A5 piquée, ou règles générales de l'imprimeur quand le produit ne les redit pas). Une valeur « fiche technique » dépend de la configuration exacte et se lit sur la fiche générée par le configurateur.

| Critère | Ce qu'on rencontre | Ce qu'on fait |
|---|---|---|
| Fond perdu | **2 mm** chez une partie des imprimeurs, **3 mm** chez les autres pour les magazines piqués ; 1 mm sur certains produits (flyers) | composer à 3 mm, rogner au montage si l'imprimeur en veut 2 (`BLEED_IMPRIMEUR=2`) |
| Zone de sécurité | 3 à 5 mm depuis la coupe ; 5 mm de part et d'autre d'un pli (dépliants) ; parfois par paliers selon le nombre de pages ; jusqu'à 15 mm côté reliure pour les dos collés | ≥ 5 mm partout, 12 / 15 mm dans le gabarit A5 |
| Tolérance de coupe | jusqu'à ±1 mm annoncé, souvent non chiffrée | rien d'important dans la zone de sécurité |
| Livraison des pages | pages simples consécutives, un PDF, ordre de lecture (cas général) ; couverture parfois séparée (obligatoire pour une couverture 6 pages ou une reliure collée) ; parfois 3 fichiers ; l'intérieur commence parfois par une page de droite | lire la fiche ; un fichier par livraison exigée |
| Imposition | faite par l'imprimeur, partout | jamais de planches |
| PDF | **PDF/X-4 ou PDF 1.6** le plus souvent, transparences natives conservées, pas de calques ; PDF/X-3 chez certains (« transparences et calques aplatis automatiquement ») ; « press quality ou PDF/X-1a » chez d'autres ; jamais de mot de passe | PDF/X-4 (`build.sh`) sans transparence résiduelle |
| Mode couleur | CMJN ; le RGB est converti automatiquement, avec un avertissement d'écart (« peut sortir plus pâle ») | séparer soi-même (§4.1) |
| Profil ICC | PSO Coated v3 (FOGRA51) sur couché et **PSO Uncoated v3 (FOGRA52)** sur non couché chez une partie des imprimeurs ; **ISO Coated v2 (FOGRA39)**, éventuellement en variante 300 %, chez d'autres, même pour le non couché | le profil exigé par l'imprimeur retenu ; FOGRA52 par défaut sur non couché |
| TAC | ≤ 300 % et ≥ 10 % par ton quand c'est publié | `verify.py` contrôle `TAC_MAX` |
| Résolution | 250 à 356 dpi pour les photos ; 1 200 dpi pour le trait ; 150 dpi pour les affiches et bâches | `DPI_MIN` |
| Corps minimal | 6 pt quand c'est publié | 8 pt en pratique |
| Filets | 0,125 pt à ≥ 40 % d'encre chez les plus tolérants ; 0,25 pt positif / 0,5 pt en réserve ailleurs ; cadre ≥ 4 mm ou pas de cadre | 0,25 pt / 0,5 pt |
| Polices | incorporées ou vectorisées chez la plupart ; **incorporées et non vectorisées** chez certains (leur préflight automatique lit les corps de texte) ; ne pas vectoriser pour une dorure | vectorisé par défaut ; demander confirmation sinon |
| Noir | texte « 100 % dans le canal K » ; noir profond suggéré pour les aplats (ex. C40 K100) ; surimpression du petit texte noir conseillée | `blacktext.py` |
| Repères | aucun : pas de traits de coupe, de pli ni de repérage, pas de cadre | aucun repère |
| Contrôle des données | option gratuite (format, CMJN, pages, polices) ou payante (résolution, fond perdu, profil, calques, distances, parfois surimpressions), selon l'imprimeur ; sans contrôle, ni surimpression ni orthographe ne sont vérifiées | le cocher si le calendrier le permet |
| Papiers non couchés | offset 80/100/120/150 g, recyclé, « naturel » ; couvertures 250–300 g | lire la disponibilité réelle du produit |
| Épreuves | épreuve couleur d'une page simulant offset + papier ; exemplaire de contrôle non fidèle en couleur ; exemplaire test à l'unité chez certains | §8.2 |
| Quantité minimale | parfois 10 exemplaires | — |

Ce qu'il faut en retenir pour un fichier « universel » : composer avec **3 mm** de fond perdu (le maximum demandé), puis **rogner à 2 mm** au montage si l'imprimeur choisi le demande (§9.3) ; livrer PDF/X-4 avec intention de sortie ; texte 100 % K ; aucun repère ; polices vectorisées **ou** incorporées selon l'imprimeur ; le nombre de fichiers et l'ordre selon la fiche technique.

---

## 4. Couleur

### 4.1 CMJN ou RGB à l'envoi

- Tous les imprimeurs en ligne acceptent le RGB et **le convertissent eux-mêmes** ; tous préviennent d'un écart de couleur. La conversion faite par l'imprimeur l'est avec **son** profil, sans réglage d'intention ni de compensation ; on ne la maîtrise pas.
- **[RECOMMANDATION]** Convertir soi-même, avec le profil du papier, en colorimétrie relative + compensation du point noir (défaut de Ghostscript pour le PDF : intention relative colorimétrique et compensation du point noir activées par défaut [S20]), et livrer un CMJN que l'imprimeur n'a plus qu'à imprimer « preserve numbers ».

### 4.2 Le bon profil pour le non couché, et ce que change un profil couché

| Profil | Base | Papier visé | TAC | Noir max / GCR | Où |
|---|---|---|---|---|---|
| ISO Coated v2 (ECI) | FOGRA39, ISO 12647-2:2004 | couché brillant/mat types 1–2 | **330 %** | GCR moyen | ECI, eci_offset_2009.zip [S18] |
| ISO Coated v2 300 % (ECI) | FOGRA39 | idem, presses/papiers limitant l'encre | 300 % | GCR moyen | idem |
| PSO Coated v3 | FOGRA51, ISO 12647-2:2013 PS1, mesure M1 | couché premium | 300 % | | ECI, pso-coated_v3.zip [S18] |
| **PSO Uncoated v3 (FOGRA52)** | FOGRA52, ISO 12647-2:2013 **PS5 « wood-free uncoated »**, papier 120 g à azurants élevés, mesure M1 | **non couché blanc** | **300 %** | noir max 96 %, GCR moyen, départ du noir 10 %, TVI 22 % | ECI, pso-uncoated_v3_fogra52.zip ; registre ICC [S11][S18] |
| PSO Uncoated ISO12647 (ECI) | FOGRA47, 2009 | non couché, ancien standard (remplacé par FOGRA52) | | | eci_offset_2009.zip ; ne plus l'utiliser pour un nouveau travail |

Licence des profils ECI (texte du registre ICC) : ils peuvent être utilisés, embarqués et échangés sans restriction, mais ni distribués, ni vendus, ni modifiés sans autorisation écrite de l'ECI [S11]. On peut donc l'embarquer dans un PDF et le garder sur la machine de travail ; on ne le republie pas, et jamais dans un dépôt public (`14-print/icc/README.md`).

**Ce que fait un fichier séparé « couché » imprimé sur non couché.** L'imprimeur imprime les valeurs CMJN telles quelles ; il ne re-sépare pas un CMJN. Conséquences mesurées sur les données de caractérisation FOGRA39 (couché) et FOGRA52 (non couché) [S11][S19] :

| Grandeur | Couché FOGRA39 | Non couché FOGRA52 | Effet |
|---|---|---|---|
| Blanc papier L\*a\*b\* | 95 / 0 / −2 | 93,5 / 2,5 / **−10** (azurants, M1) | papier plus bleuté ; les crèmes paraissent plus jaunes par contraste |
| Noir K 100 % L\* | **16** | **32,7** | un noir seul est nettement plus clair sur non couché ; le « noir profond » y plafonne vers L\* 26–29 même à 300–400 % |
| Cyan solide C\* (chroma) | 62 | 53 | cyans et bleus clairs moins saturés |
| Jaune solide C\* | 93 | 72 | jaunes et ors nettement moins saturés |
| Vert C+Y solide C\* | 70 | 43 | le milieu d'un dégradé cyan → jaune (vert) est la partie la plus affaiblie |
| Bleu C+M solide C\* | 51 | 33 | |
| TVI à 50 % | ≈ 13–16 % (courbes A/B) | 22 % (courbe C) | les tons moyens sont plus sombres, les tons pâles se bouchent plus vite |

- Une séparation ISO Coated v2 autorise **330 %** d'encre là où le papier non couché en tolère 300 % (FOGRA52) et où une presse numérique type HP Indigo en recommande 280 % [S25] : sur les zones sombres (dessin au trait très foncé, ombres) le fichier peut dépasser la limite (mesuré : 315 % sur un dessin au trait). Un dépassement sur des traits fins ne provoque ni maculage ni séchage lent en numérique, mais un préflight strict le signale, et l'imprimeur qui exige FOGRA52 est en droit de refuser.
- Les valeurs CMJN issues du profil couché ne sont pas « les meilleures possibles » pour le papier réel. Mesuré sur une couleur de marque cyan saturée : séparée en ISO Coated v2 puis imprimée sur FOGRA52, ΔE ≈ 10,6 par rapport à l'écran ; séparée directement en FOGRA52, ΔE ≈ 7,3. La couleur sera plus terne de toute façon, mais un peu moins fausse avec le bon profil [MESURE].
- La gestion des gris : un gris anthracite d'écran se sépare en quatre encres (≈ 250 % de TAC) : un texte en quatre couleurs. Voir §4.4.

**[EXIGENCE]** Séparer avec PSO Uncoated v3 (FOGRA52) chez les imprimeurs qui l'exigent sur papier offset/naturel ; **[RECOMMANDATION]** faire de même chez tout imprimeur qui n'impose pas un profil couché, et vérifier avec lui s'il exige ISO Coated v2 – dans ce cas livrer ce qu'il demande, avec un TAC ≤ 300 %.

### 4.3 Couleurs de marque saturées, dégradés, banding

- Les couleurs d'écran très saturées (cyans lumineux, verts vifs, oranges, violets électriques) sont souvent **hors gamut CMJN** (sur couché comme sur non couché) : elles sortent plus ternes et peuvent virer. Sur non couché la perte de chroma est d'environ 20 % sur le cyan (C\* 62 → 53) et le blanc papier bleuté (b\* −10) les entoure d'un fond froid [S11][S19]. **[RECOMMANDATION]** Vérifier chaque couleur de `01-brand/style-guide.md` contre le profil du papier ; aucune information ne doit dépendre de la seule saturation d'une couleur ; garder les gros aplats saturés peu nombreux ; ne pas mettre de texte < 9 pt dans une couleur claire sur blanc (mesurer le contraste, souvent sous 3:1).
- Un dégradé qui traverse le vert (cyan → jaune) passe par la zone la plus affaiblie du non couché (C\* 70 → 43) : le milieu paraîtra plus gris que sur écran. C'est acceptable sur des chiffres héros ; à éviter sur de grandes surfaces.
- **Banding** : un dégradé 8 bits offre 256 pas ; il devient visible quand une bande dépasse ≈ 1/32 in (0,8 mm) ; il faut donc un dégradé « long en pourcentage » (≥ 50 % de variation sur au moins un canal) et court en distance, ou du bruit ajouté (0,1–3 %) [S21][S22]. Un dégradé entre deux couleurs de marque contrastées varie de 60–70 % sur au moins un canal : sur 50 mm il produit des pas de 0,3 mm, invisibles. Les dégradés à faible variation (par exemple crème → blanc, 15 % sur 20 mm) sont ceux qui bandent : les faire courts ou les bruiter. La presse numérique tramée (200 lpi équivalent, 8 bits) ne rend pas mieux qu'un fichier 8 bits.

### 4.4 Noir riche, noir seul, gris, aplats pâles

- **Texte : 100 % K.** Règle générale des imprimeurs : texte en noir pur C0 M0 Y0 K100, pas de noir riche sous 12 pt ni sur les traits fins (halo au moindre décalage de repérage, contour flou) [S23]. En numérique le repérage est bon (un seul passage) mais un texte 8 pt en quatre couleurs reste plus flou qu'un texte K seul, et la charge d'encre locale est inutilement élevée. Sur non couché, un K seul (L\* 32,7) est aussi sombre qu'un anthracite composé (≈ L\* 33) : rien n'est perdu à passer le texte en K. `lib/blacktext.py` le fait.
- **Noir riche pour les grands aplats seulement** : C40 K100, ou C60 M40 Y40 K100 (usage courant, TAC 240 %) ; jamais le « registration black » 400 % [S23]. Sur non couché, un noir riche ne descend guère sous L\* 27–29 (mesuré sur FOGRA52 : C60 M40 Y40 K100 → L\* 29,5 ; 400 % → L\* 26,4).
- **Gris** : les gris de texte et de filets se font en K seul (K 50 % pour un gris moyen) ; un gris composé C17 M12 Y13 (ce que donne un #D9D9D9 séparé) est une « rosette » de trois encres qui grisaille irrégulièrement en trame et peut prendre une dominante ; en 0,25 mm il est illisible. **[RECOMMANDATION]** filets et gris légers en K seul, ≥ 15–20 % K.
- **Aplats pâles à 10–15 %** : plancher courant à 10 % par canal (fiches des imprimeurs) ; sous 10 % un ton n'est pas garanti (points isolés, granulation, blanc). Un crème très clair d'écran se sépare typiquement en 2 % C, 5 % M, 16 % Y : les 2 % de cyan et 5 % de magenta sont sous le seuil et n'apportent que du bruit ; un crème « propre » pour l'impression est Y 12–15 % (+ M 3–5 % si l'on veut le réchauffer). Un aplat pâle sur non couché paraît un peu plus sombre qu'à l'écran (TVI 22 %) et sa trame se voit à la loupe : ne pas y placer de texte < 8 pt en réserve.

### 4.5 Presse numérique, non couché : particularités

- Les imprimeurs en ligne impriment un petit tirage en numérique (toner sec ou HP Indigo) mais **demandent les mêmes profils qu'en offset** (FOGRA51/52) : la presse est calibrée pour simuler la condition ISO ; livrer le profil du papier reste juste.
- Le toner se dépose en surface : sur non couché il n'y a pas d'absorption comme en offset (le TVI est géré par la calibration), mais les grands aplats peuvent montrer un léger marbrage (mottling) et une brillance différentielle entre aplat et papier mat ; les traits et le texte sont nets. HP recommande ≤ 280 % de charge d'encre sur Indigo, au-delà l'adhérence est en cause [S25].
- Le non couché matifie et assombrit ; un rendu écran « BAT numérique » ne le montre pas (§8).

---

## 5. Traits, typographie, réserves, texte vectorisé, transparence

### 5.1 Filets et traits

| Cas | Minimum | Statut |
|---|---|---|
| Filet positif (foncé sur clair) | 0,25 pt = 0,09 mm ; 0,125 pt si ≥ 40 % d'encre chez les plus tolérants | **[EXIGENCE]** |
| Filet en réserve (clair sur foncé) | 0,5 pt = 0,18 mm | **[EXIGENCE]** |
| Filet pâle | ≥ 40 % d'encre (un filet fin à 15 % de jaune n'existe pas à l'impression) | **[EXIGENCE]** |
| Cadre autour d'une page | interdit ou ≥ 4 mm de large (sinon la coupe rend l'asymétrie visible) | **[EXIGENCE]** |
| Réglure destinée à l'écriture | 0,25–0,3 mm, K 15–25 %, **vectorielle** (voir §9 : Chrome rastérise les dégradés CSS à 72 dpi) | [MESURE] |

### 5.2 Corps et réserves

- Corps minimal exigé : 6 pt. **[RECOMMANDATION]** 8 pt pour les légendes et 9,5–10 pt pour le texte suivi sur non couché ; ne pas descendre sous 8 pt en couleur claire (mesurer le contraste de chaque couleur de marque sur blanc).
- Texte en réserve (blanc sur aplat) : ≥ 8 pt et graisse ≥ 600 ; jamais de traits fins ni de corps maigre : l'encre « mange » les contreformes (« a 1 pt positive line becomes about 2 pt in reverse ») ; sur non couché l'effet est renforcé par le TVI de 22 % [S11][S24].
- Petit texte noir sur aplat de couleur : la surimpression du noir est conseillée par certains imprimeurs ; un PDF issu de Chrome n'a pas de surimpression : le texte est en réserve dans l'aplat, ce qui est correct en numérique et n'exige rien.

### 5.3 Texte vectorisé ou police incorporée : comportement des RIP

- Les imprimeurs acceptent les polices incorporées ; la plupart acceptent aussi le texte « en tracés » ; **certains demandent explicitement des polices incorporées et non vectorisées** (leur préflight automatique lit les corps de texte).
- Ghostscript documente le revers de `-dNoOutputFonts` : sortie plus lourde, plus lente à traiter, rendu un peu différent, surtout à basse résolution [S20]. Le tracé perd le hinting et l'ajustement de graisse des rastériseurs : sur un RIP à 600–1 200 dpi, l'écart est invisible ; sur une épreuve laser 300–600 dpi le texte vectorisé paraît un peu plus gras ou plus irrégulier que le même texte en police – ne pas juger la graisse du texte sur une épreuve laser.
- Pourquoi vectoriser : Chrome incorpore une police **variable** sous forme **Type 3**, forme que certains RIP digèrent mal (substitution, glyphes manquants) ; un PDF sans police du tout ne pose aucun problème d'incorporation. Contrepartie : plus aucun contrôle de corps n'est possible sur le PDF final (faire le QA sur le PDF « qa » de `build.sh`), et l'imprimeur qui veut des polices incorporées verra un fichier sans police : lui demander confirmation ou lui livrer la version à polices incorporées (celle de Chrome) après test. Une police statique (non variable) s'incorpore normalement.

### 5.4 Transparence et aplatissement

- **PDF/X-4** conserve la transparence : les imprimeurs qui l'acceptent demandent de garder les transparences natives. **PDF/X-3** : transparences et calques sont aplatis automatiquement dans le flux de l'imprimeur, résultat correct en général.
- Ce qui compte : ne **jamais** livrer un PDF où la transparence a été aplatie par rendu bitmap de la page entière (c'est ce que fait Ghostscript si on lui demande PDF/X-3 ou une compatibilité < 1.4 [S20] – testé : `-dPDFX=3` sur une couverture produit trois pages en image 4 370 × 6 120 px, texte compris). Le PDF final reste en 1.6/1.7, déclaré PDF/X-4.
- **Mais dans la chaîne HTML → Ghostscript, la transparence qui traverse la conversion CMJN est aplatie à 72 dpi** [MESURE] : opacités, SMask d'images, groupes. D'où la règle du module : rien de transparent dans le PDF ; tout ce qui se superpose est composé en amont dans une **plaque opaque** (`lib/plaque.sh`), ou aplati sur son fond réel (`lib/aplatir.py`, `lib/opacifier-svg.py`, `lib/svg-en-png.sh`).
- Sources de transparence dans une maquette HTML : `opacity`, `rgba()`, `color-mix()` vers `transparent`, PNG à couche alpha (SMask), `mix-blend-mode`, ombres portées, `background-clip:text` (masque). Réduire ce qui peut l'être en couleur pleine (un `rgba(30,64,175,.18)` sur blanc devient un aplat `#D7DDF1` sans transparence) : résultat identique, rien à aplatir.
- **Une image opaque posée sur un décor masque ce décor sur toute sa boîte**, pas seulement sur son dessin : un portrait au trait posé sur un filigrane le fait disparaître dans tout son rectangle. Le décor et l'image vont ensemble dans la plaque. Un dessin au trait est une silhouette **vide** : le remplir de la couleur de fond sous le trait avant de le superposer, sinon le décor se voit à travers ; et un remplissage depuis les bords suffit rarement (une seule interruption du contour et il s'engouffre dans la silhouette) : épaissir le trait le temps de délimiter l'extérieur, puis lui rendre son épaisseur.

---

## 6. Images

### 6.1 Résolution effective

- Résolution effective = pixels ÷ largeur imprimée en pouces ; c'est elle qui compte, pas les dpi du fichier. Cibles : **300 dpi** photos et illustrations tramées (250 acceptés chez certains, 356 demandés chez d'autres) ; **1 200 dpi** pour le trait 1 bit ; **150 dpi** pour un grand format lu à plus d'un mètre. Au-delà de 2 × la linéature (≈ 600 dpi pour 200–300 lpi équivalents), le surplus n'apporte rien et alourdit le fichier : `build.sh` sous-échantillonne à 600 dpi.
- Un dessin au trait rastérisé en niveaux de gris (anticrénelé) est acceptable dès 300–400 dpi à 25–35 cm de lecture ; à 300 dpi un trait de 0,2 mm est rendu par 2–3 pixels, ses bords sont un peu doux ; préférer 600 dpi ou le vecteur pour les traits fins noirs.
- Chrome et Ghostscript rastérisent certains éléments (§9.4) : vérifier la résolution effective de **tout** raster du PDF **final**, y compris ceux qui n'existaient pas dans les sources (`verify.py`).

### 6.2 Images à couche alpha (PNG transparents)

- Un PNG avec alpha devient une image + un **SMask** (masque de transparence 8 bits) dans le PDF : c'est de la transparence PDF 1.4, aplatie à 72 dpi par la conversion de la chaîne. Aplatir chaque image sur la couleur de son fond réel avant l'export (`lib/aplatir.py`).
- Ghostscript peut ré-encoder les images couleur en JPEG (§9.5) : les images à bords nets (trait) en souffrent ; `build.sh` force Flate (sans perte).

### 6.3 SVG dans un PDF

- Un SVG n'existe pas dans un PDF : Chrome le convertit soit en tracés (vecteur), soit en image. Règle observée [MESURE, §9.4] : SVG à formes pleines et traits sans dégradé, masque ni filtre → vecteur ; SVG contenant `linearGradient`/`radialGradient`, `mask`, `filter`, `opacity` sur un groupe → tout ou partie rastérisé (à ≈ 300–360 dpi quand il est affiché en `<img>`, à 72 dpi quand c'est un fond CSS). Pour du trait, préparer des SVG « plats » (couleurs pleines, pas de dégradé : `lib/opacifier-svg.py`) ou les rendre en PNG opaque à la bonne résolution (`lib/svg-en-png.sh`).

### 6.4 QR code

- **Zone de silence** : 4 modules de vide sur les quatre côtés [S13]. Sur un fond teinté, la zone de silence est de la couleur du fond (unie, sans texte, sans filet). Vérifier que le fond sous le symbole et sa zone de silence ne contient **qu'une seule couleur**.
- **Générer le symbole sans marge** (`border=0` dans la plupart des bibliothèques) et poser la zone de silence en CSS : sinon la largeur CSS s'applique au viewBox entier, marge comprise, et le module tombe sous le seuil.
- **Taille** : module ≥ 0,4–0,5 mm pour la lecture au téléphone à 20–30 cm ; en pratique ≥ 2 × 2 cm de côté pour un QR de version 3–5 [S14]. Taille imprimée = nombre de modules × taille du module (+ 8 modules de marge) [S13]. **La quantité de données fixe la version, donc le module** : une vCard encodée en dur grossit vite ; au-delà d'environ 210 octets, un symbole de 2 cm passe en version 11 et son module tombe sous 0,5 mm. Raccourcir les données (URL courte, téléphone au format E.164) plutôt qu'agrandir le symbole.
- **Contraste** : modules sombres sur fond clair (jamais l'inverse), pas de jaune sur blanc ; un gris foncé K seul convient ; un fond crème (L\* 92–96) est un fond clair correct [S14].
- **Correction d'erreur** : L 7 %, M 15 % (le plus utilisé), Q 25 %, H 30 % ; Q ou H en milieu salissant ; plus le niveau est haut, plus il y a de modules pour la même donnée [S13]. Pour un document manipulé plusieurs jours, sur non couché qui peut se salir : **M au minimum, Q de préférence** ; H seulement si le QR reste grand.
- **Vecteur ou 1 bit** : le QR doit être des tracés pleins ou un bitmap 1 bit ≥ 600 dpi ; jamais un JPEG ni un raster gris ; pas de dégradé, pas de logo au centre sans passer en H.
- **Test** : scanner l'épreuve papier (pas l'écran) avec deux téléphones, à 15 cm et à 40 cm, en lumière de salle ; ouvrir le lien avec un compte tiers (page exigeant une connexion ? lien d'invitation encore valide à la date de l'événement ?).

---

## 7. Papier

| Papier | Épaisseur (approx.) | Opacité ISO 2471 (offset non couché type) | Usage | Remarques |
|---|---|---|---|---|
| Offset 80 g | 0,10 mm | ≈ 91–94 % | courrier | transparence recto-verso visible sur les aplats |
| Offset 100 g | 0,12–0,13 mm | ≈ 94–95 % | brochure économique | aplats du verso perceptibles par transparence |
| **Offset 120 g** | 0,14–0,15 mm | **≈ 96–97 %** | intérieur de brochure | bon compromis : opacité, tenue au stylo, chasse 0,72 mm sur 24 p. |
| Offset 135–150 g | 0,17–0,19 mm | ≈ 98–99 % | intérieur premium | plus rigide, le cahier « bâille » un peu plus, chasse ≈ 1 mm |
| Offset 250 g | ≈ 0,3 mm | > 99 % | couverture | rainage nécessaire, pli propre |
| Recyclé/naturel 300 g | ≈ 0,4 mm | > 99 % | couverture | teinte plus grise, aplats plus ternes ; rainage indispensable |

Valeurs d'opacité relevées sur des fiches papetières d'offsets non couchés du marché (80 g ≈ 91,5–94 %, 100 g ≈ 94,5–95 %, 120 g ≈ 96,5–97 %) [S26].

- **Écriture** : le non couché prend le stylo bille, le feutre fin et le crayon ; le couché brillant refuse le crayon et fait baver le feutre. Pour un carnet où l'on écrit, non couché sans discussion ; 120 g évite que le feutre traverse ; les pages de notes restent blanches (meilleur contraste sous le stylo).
- **Pelliculage** : un pelliculage mat sur une couverture non couchée protège des traces de doigts et des rayures et évite le « frottis » du toner sur les aplats sombres au dos ; il désature un peu et donne un toucher lisse qui n'est plus celui du non couché. Sans pelliculage, éviter les grands aplats sombres en couverture (marquage) ; un vernis acrylique machine est un compromis. Choix de direction artistique ; du point de vue fabrication : couverture ≥ 250 g + pelliculage mat = l'option la plus robuste pour un objet « à garder ».
- **Ce que le non couché fait aux couleurs** : matité (pas de reflet spéculaire, donc noirs moins profonds : L\* 32,7 pour K 100 % contre 16 sur couché), gamut réduit (§4.2), TVI plus fort (22 %), blanc bleuté par les azurants (mesure M1). Ce n'est pas un défaut : c'est un rendu ; l'épreuve doit être jugée avec ces valeurs en tête, pas contre l'écran.

---

## 8. Épreuvage et préflight

### 8.1 Épreuve maison (imprimante de bureau) : ce qu'elle montre et ne montre pas

Montre : la mise en page, le chemin de fer une fois plié et agrafé (imprimer les planches recto-verso au format réel, plier, **emboîter** les feuilles – la première dehors, la feuille centrale au cœur ; empilées, le carnet sort mélangé –, agrafer, feuilleter), la lisibilité des corps, la zone de sécurité, l'alignement des traversées de gouttière, la position du folio, le QR (à scanner sur papier), les coquilles.
Ne montre pas : la couleur (une laser de bureau n'est pas calibrée FOGRA52 et imprime souvent plus saturé), le TVI du non couché, la charge d'encre, la graisse réelle du texte vectorisé (§5.3), la coupe (une A4 pliée n'est pas massicotée : imprimer sur A4 ou A3 avec les traits de coupe *ajoutés à l'épreuve seulement*, couper au cutter), le pelliculage, la chasse réelle.

### 8.2 « BAT numérique » (aperçu écran de l'imprimeur) : ce qu'il ne montre pas

- Il valide le contenu, l'ordre des pages, l'orientation, le format ; il **ne simule ni le papier, ni la couleur, ni le TAC, ni les tons < 10 %**. Un « exemplaire de contrôle » papier n'est pas non plus fidèle en couleur ni en matière.
- Une épreuve couleur (souvent la page de titre, simulant l'offset et le papier) est le seul contrôle colorimétrique disponible en ligne. Pour un petit tirage, l'alternative pragmatique : commander d'abord **un** exemplaire test (ou le minimum de commande) et le juger avant le tirage définitif, si le calendrier le permet.

### 8.3 Préflight automatique faisable avec la chaîne

`lib/verify.py` (PDF final) et `lib/qa.py` (sortie Chrome), complétés par l'agent `print-preflight`, vérifient : version PDF et présence d'une intention de sortie ; MediaBox/TrimBox/BleedBox ; nombre et ordre des pages ; pages vides ; espaces de couleur restants (RGB, ICCBased, Separation) ; polices présentes/Type 3 ; **TAC maximal par page** (rendu CMJN à 150 dpi, plus chaque image CMJN lue à sa résolution native : un rendu sous-échantillonné moyenne un trait fin et sous-estime sa charge – mesuré : 295 % annoncés pour 323 % réels dans des contours d'icônes) ; **résolution effective de chaque image** et son filtre (DCT/Flate) ; images issues de rastérisation ; **épaisseur des traits** (`get_drawings`) et couleurs des filets fins ; corps de texte et couleurs sur le PDF « qa » ; texte hors zone de sécurité ; **taille et zone de silence du QR** ; décodage du QR (OpenCV) ; couverture du fond perdu ; présence d'annotations, calques, chiffrement. Ce que l'automatique ne voit pas : la couleur perçue sur papier, le pli, la coupe, l'agrafe, la lisibilité réelle : d'où l'épreuve papier.

---

## 9. Pièges spécifiques d'une chaîne HTML → Chrome headless → Ghostscript → PyMuPDF

Tout ce paragraphe est [MESURE] sur Chrome 151 (Skia/PDF), Ghostscript 10.07, PyMuPDF 1.28.

### 9.1 Chrome n'imprime pas au millimètre

- `@page { size: 154mm 216mm }` produit une page de **437,04 × 612 pt = 154,18 × 215,90 mm** ; `size: 100mm 100mm` produit 282,96 pt = 99,82 mm. Chrome quantifie le format de page au 1/100 de pouce (0,254 mm) et arrondit tantôt au-dessus, tantôt au-dessous. Le contenu, lui, est mis en page au format CSS demandé, en haut à gauche : il peut déborder du bas ou laisser un filet blanc à droite.
- Conséquence : il faut **toujours** normaliser le format en aval, et **sans mise à l'échelle** si l'on veut une géométrie exacte : `show_pdf_page(rect_cible, src, n, clip=fitz.Rect(x, y, x + W, y + H))` avec un rect cible de même taille que le clip (échelle 1) ; l'astuce « déborder d'un point » (rect cible plus grand que la source) agrandit tout le contenu (mesuré : × 1,0034, soit un décalage de la coupe effective de 0,25 à 0,36 mm par côté). `build.sh` découpe **au centre** de la page Chrome (sinon tout l'excédent part d'un seul côté : 0,59 mm d'écart haut/bas mesuré sur une carte de visite).
- La parade côté maquette : dimensionner `.page` en pixels CSS entiers, arrondis au-dessus, et déclarer `@page` d'un pixel de plus en hauteur, avec `overflow:hidden` sur la page (voir `gabarits/print-a5.css`). Un débord non contenu élargit le document et Chrome réduit toute la page (mesuré : réduction à 0,907, un corps 8 pt sorti à 7,3 pt).
- Chrome accroche les bords des rectangles peints (fonds, bordures) au **pixel CSS (0,2646 mm)** : un filet de 0,6 mm devient 0,79 mm (3 px), un filet de 0,25 mm devient 0,265 mm (1 px), un folio de 7 mm 6,9 mm. Spécifier les épaisseurs en multiples de 0,2646 mm (0,265 / 0,53 / 0,79 mm) évite les surprises ; les tracés SVG et le texte, eux, ne sont pas accrochés.
- `--virtual-time-budget` est indispensable : sans lui, Chrome imprime avant d'avoir chargé le CSS externe et sort des pages vides au bon format, sans message (`verify.py` détecte les pages vides).

### 9.2 Chrome n'écrit que du RGB, jamais de gris ni de noir « pur »

- Toute couleur sort en `rg` DeviceRGB, y compris #000000 et les gris neutres (testé). Ghostscript convertit donc le noir en noir composé (0/0/0 → C87 M78 Y65 K93 avec ISO Coated v2, TAC 323 %) et un anthracite en quatre encres. Le mécanisme `-dDeviceGrayToK` de Ghostscript ne sert à rien puisqu'aucun objet n'est DeviceGray ; `-dBlackText` passerait aussi en noir les textes de couleur. Le seul remède fiable est un post-traitement du flux de contenu (remplacement du tuple CMJN exact du texte par `0 0 0 1 k` : `lib/blacktext.py`, qui traite aussi les gris neutres) ; une conversion `-dUseFastColor` (formule « 255 moins », sans ICC) met bien le noir en K100 mais dégrade les images et les couleurs.

### 9.3 Fond perdu 3 mm dessiné, 2 mm demandé

- Composer à 3 mm et rogner de 1 mm par côté au montage PyMuPDF (`clip` décalé de 1 mm vers une page de 152 × 214 mm pour un A5) donne un fichier exact pour un imprimeur qui veut 2 mm, sans toucher à la maquette (`BLEED_IMPRIMEUR=2`). Ne jamais laisser l'imprimeur « adapter » un format non conforme : certains mettent à l'échelle automatiquement, ce qui déplace la coupe.

### 9.4 Ce que Chrome rastérise (et à quelle résolution)

| Élément CSS/HTML | Sortie Chrome | Résolution mesurée | Risque |
|---|---|---|---|
| Texte, bordures, fonds unis, `border-radius`, SVG inline ou `<img>` sans dégradé/masque/filtre (QR, portraits vectoriels) | vecteur | – | aucun |
| `background-image: linear-gradient / radial-gradient` (réglures, points, fondus), et de même un `<pattern>` dans un SVG inline (qui entraîne tout le SVG) | **motif de tuile (Pattern) contenant une image, 1 px = 1 pt** | **72 dpi** | réglure de 0,25 mm rendue en bande floue de 0,36–0,72 mm, pas irrégulier : défaut visible ; fondu doux : invisible |
| SVG inline à éléments explicites (`<rect>`, `<circle>`, `<line>`, `<path>`) sans dégradé | vecteur | – | aucun : c'est la bonne façon de dessiner réglures, points, filets |
| `background-clip: text` sur dégradé (chiffres héros) | forme du texte en masque vectoriel + image du dégradé | 179–299 dpi selon le conteneur | **masque perdu à la conversion CMJN : il ne reste qu'un rectangle** → `chiffre-svg.py` + `chiffres-png.sh` |
| `<img src="*.svg">` contenant `linearGradient`, `mask`, `filter`, `opacity` de groupe (logo, carte illustrée) | image | 300–360 dpi | acceptable ; préférer un SVG plat pour un logo |
| `radialGradient` à l'intérieur d'un SVG vectoriel (ombrés d'un portrait) | petite image + masque | 72 dpi | invisible (dégradé doux) |
| `box-shadow` (soulignement décoratif) | image « nine-patch » étirée | 90 × 45 dpi | bord net conservé ; préférer une bordure ou un pseudo-élément |
| PNG à alpha | image + SMask (Flate) | résolution du fichier | aplati à 72 dpi par la conversion CMJN → `aplatir.py` |
| `opacity`, `rgba()` | ExtGState `/ca`, groupes de transparence | – | aplatis à 72 dpi par la conversion → plaque ou couleur pleine |

Règle pratique : **tout ce qui doit avoir un bord net et une épaisseur exacte est un élément DOM ou un SVG inline plat**, jamais un `background-image` CSS ; **tout ce qui se superpose va dans la plaque**.

### 9.5 Ghostscript : ce que font les options

- `-sColorConversionStrategy=CMYK -sOutputICCProfile=… -dProcessColorModel=/DeviceCMYK` : conversion ICC de tout le RGB, intention relative colorimétrique + compensation du point noir par défaut ; les dégradés (shadings) RGB sont **rendus en image** puisque l'espace de sortie diffère [S20], résolution bornée par `-dMaxShadingBitmapSize` (256 000 octets par défaut, ≈ 180 dpi sur un grand aplat). **Ne jamais augmenter `-dMaxShadingBitmapSize`** : au-delà du défaut, Ghostscript perd silencieusement des objets (mesuré : un titre de couverture disparaissait). Pré-rendre les dégradés en PNG 600 dpi.
- `-dNoOutputFonts` : texte en tracés (voir §5.3).
- **Ré-encodage des images** : par défaut pdfwrite ré-encode les images couleur en JPEG (qualité mesurée ≈ 55) : artefacts sur le trait. Forcer `-dAutoFilterColorImages=false -dColorImageFilter=/FlateEncode` (et Gray idem) ; sous-échantillonner à 600 dpi (`-dDownsampleColorImages=true -dColorImageResolution=600 -dColorImageDownsampleThreshold=1.2 -dColorImageDownsampleType=/Bicubic`).
- **PDF/X** : `-dPDFX=4` + fichier de définition (intention de sortie avec le profil ICC, `GTS_PDFXVersion (PDF/X-4)` : `lib/pdfx4.ps`) donne un PDF 1.6 avec OutputIntent et métadonnées XMP ; `-dPDFX=3` force PDF 1.3 et **rend en bitmap toute page contenant de la transparence** (testé) : proscrit. `PDFXTrimBoxToMediaBoxOffset` n'a pas d'effet sur une entrée PDF (testé) : poser TrimBox/BleedBox avec PyMuPDF (`page.set_trimbox`, `set_bleedbox`), avant ou après Ghostscript (les deux survivent, testé).
- **Format** : pdfwrite arrondit la MediaBox à 0,01 pt : négligeable, mais toute reconstruction de page par PyMuPDF (`show_pdf_page`) après Ghostscript perd l'intention de sortie et les boîtes : soit finir par Ghostscript, soit ne faire ensuite que des opérations qui conservent le catalogue (`set_trimbox`, mise à jour de flux, `save`).
- **Lecture du profil ICC** sous SAFER : `--permit-file-read=/chemin/du/dossier/` plutôt qu'un `cd` dans le dossier ; ne pas masquer le code de retour de gs par `|| true` sans lire la sortie d'erreur.

### 9.6 Ce que le PDF final doit contenir (et ne pas contenir)

Contenir : pages au format de données exact (ex. A5 : 152 × 214 ou 154 × 216 mm), TrimBox au format fini centrée, BleedBox = MediaBox, OutputIntent (profil du papier), `GTS_PDFXVersion PDF/X-4`, DeviceCMYK partout, images Flate ≥ 300 dpi effectifs, texte en tracés (ou polices incorporées), texte et gris en K seul.
Ne pas contenir : DeviceRGB/ICCBased RGB, Separation/DeviceN inattendus, polices Type 3, annotations, champs, calques, chiffrement, JavaScript, images JPEG à bords nets, motifs rastérisés à 72 dpi, transparence résiduelle, éléments dans les 3 mm du pli de couverture, TAC > plafond du papier.

---

## 10. Checklist de préflight complète avant envoi

Cocher dans l'ordre. « Outil » indique comment vérifier.

**A. Commande et gabarit**
1. Produit configuré chez l'imprimeur ; fiche technique ou gabarit téléchargé ; fond perdu (2 ou 3 mm), zone de sécurité, nombre de fichiers, ordre des pages, profil ICC exigé, PDF/X exigé, polices vectorisées acceptées ou non : notés dans le README de la production. (lecture)
2. Papiers intérieur et couverture disponibles pour ce produit ; pelliculage décidé ; « nombre de pages » du configurateur cohérent (couverture incluse ou non) ; quantité ≥ minimum de commande. (configurateur)
3. Délai : production + livraison au lieu de destination avant la date de remise, avec 3 jours de marge pour un contrôle des données ; date limite d'envoi inscrite au calendrier éditorial. (configurateur)

**B. Fichier : format et structure**
4. Nombre de pages intérieures multiple de 4 + 4 de couverture ; ordre de lecture ; pages simples ; page blanche = page présente. (`verify.py`)
5. Toutes les pages au format de données exact de l'imprimeur, ± 0,05 mm ; même orientation. (`verify.py`)
6. TrimBox = format fini, BleedBox = MediaBox ; pas de traits de coupe ni de repères. (`verify.py`, lecture)
7. Fond perdu réellement couvert sur les quatre côtés de chaque page à fond coloré ; aucun filet blanc au bord. (`verify.py`)
8. Rien d'important à moins de 5 mm de la coupe (texte, logos, QR, médaillons), folio compris ; rien de fin sur le pli ; couverture : rien dans les 3 mm du dos. (`qa.py` + lecture)
9. Traversées de gouttière alignées à la même hauteur sur les deux pages ; images à cheval seulement si nécessaire. (rendu des doubles pages, agent `print-editorial`)

**C. Couleur**
10. PDF entièrement DeviceCMYK (ou CMJN + Gray) : aucun DeviceRGB, ICCBased RGB, Lab, Separation, DeviceN inattendu. (`verify.py`)
11. Séparé avec le profil du papier réel ou celui qu'exige l'imprimeur ; OutputIntent présent et cohérent ; PDF/X-4 déclaré. (`verify.py`)
12. TAC max ≤ plafond du papier (300 % FOGRA52/51, 330 % FOGRA39) sur toutes les pages ; ≤ 280 % si presse Indigo connue. (`verify.py`)
13. Texte courant et légendes en K 100 % ; noir riche seulement sur les aplats ; gris et filets fins en K seul ; aucun ton utile < 10 %. (`blacktext.py`, agent `print-preflight`)
14. Couleurs de marque vérifiées contre le profil du papier (table CMJN cible) ; aucune information ne dépend de la seule saturation d'une couleur ; dégradés ≥ 50 % de variation ou bruités.

**D. Traits, typo, images**
15. Filets ≥ 0,25 pt positif, ≥ 0,5 pt en réserve, ≥ 40 % d'encre ; réglures vectorielles. (agent `print-preflight`)
16. Corps ≥ 8 pt (≥ 6 pt exigé) ; réserves ≥ 8 pt et graisse ≥ 600 ; pas de texte < 9 pt dans une couleur claire sur blanc. (`qa.py` sur le PDF « qa »)
17. Aucune police dans le PDF (vectorisé) **ou** toutes incorporées non Type 3, selon l'imprimeur. (`verify.py`)
18. Résolution effective : ≥ 300 dpi pour toute image (150 en grand format) ; ≥ 600 dpi ou vecteur pour le trait fin ; aucun raster à 72 dpi hors dégradés doux ; images Flate, pas de JPEG sur du trait. (`verify.py`)
19. SVG : ceux qui contiennent dégradé/masque/filtre ont été vérifiés en résolution ou aplatis. (`verify.py`)
20. Transparence : aucune résiduelle (plaque, images aplaties) ; aucun PDF < 1.4 ; aucune page rendue en bitmap. (agent `print-preflight`)

**E. QR code**
21. Module ≥ 0,5 mm, côté ≥ 20 mm ; zone de silence ≥ 4 modules sur les quatre côtés, d'une seule couleur ; contraste sombre sur clair ; niveau M ou Q ; vecteur plein ou 1 bit ≥ 600 dpi ; décodé depuis un rendu 75 dpi de la page (robustesse) et depuis l'épreuve papier ; lien testé avec un compte tiers. (agent `print-preflight` + téléphone)

**F. Épreuve et envoi**
22. Épreuve papier recto-verso pliée-agrafée relue par un tiers (noms propres, numéros de pages, sommaire, QR) ; épreuve de couleur si possible (page de titre, ou un exemplaire test).
23. Nom des fichiers explicite (`brochure-interieur-24p-152x214.pdf`, `brochure-couverture-4p-152x214.pdf`) ; pas de mot de passe ; taille de fichier dans la limite de l'imprimeur ; jamais le fichier complet de validation à la place des fichiers exigés.
24. Contrôle des données de l'imprimeur coché si le calendrier le permet ; commentaires de commande : profil utilisé, couverture séparée ou non, ordre des pages.
25. Sauvegarde du PDF envoyé, de la fiche technique et de la confirmation de commande dans `output/envoi-AAAA-MM-JJ/` (non versionné) ; décision consignée dans le README de la production.

---

## 11. Sources

Les exigences d'imprimeurs (§0, §3) proviennent des fiches publiques « données d'impression » de plusieurs imprimeurs en ligne européens consultées en 2026 ; elles changent : relire la fiche du produit configuré avant chaque commande.

Couleur et profils :
- [S11] Registre ICC, profil PSO Uncoated v3 (FOGRA52) : TAC 300 %, noir max 96 %, GCR moyen, départ du noir 10 %, TVI 22 %, ISO 12647-2:2013 PS5, licence ECI ; données de caractérisation FOGRA52 et FOGRA39 (ISO 28178) — registre de l'International Color Consortium, https://registry.color.org
- [S18] European Color Initiative (ECI), téléchargements des profils offset (PSO Coated v3, PSO Uncoated v3 FOGRA52, ISO Coated v2) : https://www.eci.org/en/downloads
- [S19] ISO Coated v2 / FOGRA39, TAC 330 % et variante 300 % ; FOGRA52 : documentation de prépresse et d'épreuvage (lexiques de spécialistes de l'épreuvage).
- [S25] Charge d'encre en numérique : recommandations de consultants couleur (HP Indigo : 280 %).
- [S23] Noir riche / noir texte : guides techniques d'imprimeurs en ligne (noir standard contre noir riche, couleurs de noir recommandées).
- [S21][S22] Banding : notes techniques d'éditeurs de RIP et de prépresse (bande visible > 1/32 in, ≥ 50 % de variation, bruit 0,1–3 %).
- [S24] Texte en réserve et filets : prepressure.com (règles de préflight) ; synthèse reprise de `doctrine-mise-en-page-editoriale.md` §2.4.

Piqûre, chasse, papier :
- [S15] Guides de piqûre à cheval et de calcul de la chasse (formule (pages ÷ 4 − 1) × épaisseur ; « ≤ 40 pages : à peine visible » ; éléments qui traversent deux pages).
- [S17] Couvertures lourdes et rainage : forums et guides de façonnage.
- [S26] Opacité des offsets non couchés : fiches techniques papetières du marché ; norme ISO 2471:2008.

QR :
- [S13] Denso Wave (inventeur du QR code), « How to make a QR Code » (marge de 4 modules, calcul de la taille) et « Error correction feature » (L/M/Q/H) : https://www.qrcode.com/en/
- [S14] Guides d'impression des QR codes (zone de silence, ≥ 2 × 2 cm, contraste, vecteur) ; norme ISO/IEC 18004.

Outils :
- [S20] Ghostscript, documentation : « High level output devices » (-dPDFX 1/3/4, -dNoOutputFonts, rendu bitmap des pages transparentes sous 1.4, shadings rendus en image, PDFXTrimBoxToMediaBoxOffset) ; « Using Ghostscript » (-sOutputICCProfile, -dRenderIntent, -dBlackPtComp, -dKPreserve, -dBlackText, -dUseFastColor, -dDeviceGrayToK, --permit-file-read) ; « Ghostscript color management » : https://ghostscript.readthedocs.io/en/latest/
- Normes : ISO 15930 (PDF/X), ISO 12647-2 (offset), ISO 18004 (QR).
