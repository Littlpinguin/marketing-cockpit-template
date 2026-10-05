---
title: "Doctrine de mise en page éditoriale imprimée — magazines, fascicules, brochures (A5 en particulier)"
type: doctrine
version: 1.0
auteur: rédigé lors de la production d'un carnet d'événement, généralisé pour tout fascicule imprimé
sources: voir §8 (ouvrages et pages consultés en 2026)
---

# Doctrine de mise en page éditoriale imprimée

Ce document permet de composer un fascicule imprimé correct sans avoir refait la recherche : les principes viennent des ouvrages de référence (Müller-Brockmann, Bringhurst, Hochuli, Tschichold, Lupton, Samara, Butterick) et de la pratique des magazines contemporains ; les chiffres viennent de ces auteurs, des imprimeurs et des guides de prépresse. Chaque énoncé porte sa source. Deux statuts :

- **[CONSENSUS]** : repris par plusieurs sources indépendantes, on ne discute pas, on applique.
- **[PARTI PRIS]** : position d'un auteur ou d'un studio, défendable, à choisir consciemment.

Le document est écrit pour un fascicule A5 (148 × 210 mm) piqué à cheval, composé en HTML/CSS et exporté en PDF, mais les principes valent pour tout imprimé éditorial. Il est organisé ainsi : 1. principes ; 2. règles chiffrées ; 3. échelle typographique et gabarits de texte ; 4. la double page et le rythme d'un fascicule ; 5. répertoire de gabarits de doubles pages A5 ; 6. spécificités du petit format et de l'HTML→PDF ; 7. checklist de relecture ; 8. sources.


## 0. Mode d'emploi rapide : composer un fascicule A5 en dix décisions, dans l'ordre

1. **Format et fabrication** : 148 × 210 mm rogné, fond perdu 3 mm, piqûre à cheval, pages en multiple de 4, papier connu (couché ou non) — §2.1.
2. **Chemin de fer** : la liste des doubles pages avec, pour chacune, son gabarit (§5), son élément dominant et sa densité ; on vérifie la courbe de rythme avant d'ouvrir un fichier de maquette — §4.3.
3. **Marges** : tête 12 · extérieur 12 · intérieur 14 · pied 17 mm (zone 122 × 181 mm) pour un fascicule dense ; ou le canon classique si l'objet est un livre — §2.1.
4. **Corps et interlignage** : 10 / 14,17 pt (= 5 mm) dans la police de marque ; la grille de base est donc de 5 mm, et tout espacement vertical en est un multiple — §2.3, §3.
5. **Grille mère** : 12 colonnes de 6,5 mm, gouttières 4 mm ; texte suivi sur 8/12 ou 9/12 (46–52 signes), jamais sur 6/12 — §2.2, §2.3.
6. **Lignes d'accroche** : A = 12 mm, B = 40 mm, C = 145 mm depuis la coupe haute, communes à toutes les pages ; le surtitre sur A, le premier bloc sur B, les pieds de blocs sur C — §5.0.
7. **Échelle** : 8 / 10 / 12,5 / 16–18 / 20 / 30–36 / 48–64 pt et un chiffre héros de 96–150 pt ; trois niveaux par page au plus ; la couverture plus grande que tout — §3.1.
8. **Constantes** : folio, titre courant, surtitre, filet signature au même endroit partout ; ce sont elles qui autorisent à varier tout le reste — §1.2.
9. **Un héros par double page** (image, chiffre ou titre) et le blanc composé autour de lui, jamais laissé en pied — §1.4, §1.10.
10. **Relecture** : la checklist du §7 sur chaque double page imprimée à l'échelle 1, puis les contrôles automatiques (format, corps, dpi, marges), puis une épreuve pliée et agrafée.

---

---

## 1. Principes (avec leur source)

### 1.1 La double page est l'unité de composition, pas la page
Le lecteur voit deux pages à la fois et les lit comme une seule surface ; il atterrit sur la page de droite, puis balaie vers la gauche. Les deux pages doivent donc partager des alignements (lignes d'accroche, ligne de base, marges) et une seule idée de composition. **[CONSENSUS]** — Richard Hendel (*On Book Design*, cité par Speakipedia : « facing pages… a single unit ») ; Publitas (« designing spreads instead of isolated pages ») ; Jeremy Leslie, magCulture Live 2024 (la double page comme « attribut physique définissant » du magazine) ; PMG (le lecteur atterrit à droite). Tschichold et Hochuli construisent d'ailleurs le bloc de texte *sur la double page* : les deux marges intérieures réunies forment une colonne de blanc qui ne doit pas dépasser une marge extérieure (Tschichold, *The Form of the Book*, canon 2:3:4:6 : deux fois 2 = 4).

### 1.2 Une grille mère, des lectures multiples ; des constantes qui ne bougent jamais
La grille divise la surface en champs (colonnes × lignes) ; on la lit de plusieurs façons d'une double page à l'autre, mais certains éléments restent au même endroit à chaque page : folio, titre courant, marqueurs de section, marges, ligne d'accroche du texte. C'est la tension entre constantes et variables qui donne l'unité *et* la variété. **[CONSENSUS]** — Müller-Brockmann, *Grid Systems in Graphic Design* (1981) : « The grid system is an aid, not a guarantee » ; Timothy Samara, *Making and Breaking the Grid* : « The greatest danger in using a grid is to succumb to its regularity » ; madegooddesigns.com (folios et titres courants « in the same place issue after issue »). Lupton (*Thinking with Type*) parle de *hang line* : la ligne commune d'où « pend » le texte.

### 1.3 Tout s'accroche à la grille de base (l'interlignage du corps est l'unité verticale)
Les hauteurs de champs, d'images, de cartes, les espaces entre blocs sont des multiples de l'interlignage du texte courant ; après chaque interruption (titre, image, légende) le texte revient « en phase ». Sinon les lignes ne s'alignent ni d'une colonne à l'autre ni à travers la gouttière, et la page paraît flottante sans qu'on sache pourquoi. **[CONSENSUS]** — Müller-Brockmann (les champs « correspond in depth to a specific number of lines of text ») ; Bringhurst, *Elements*, §2.2 (« return… precisely on beat and in phase ») ; Khoi Vinh, *Ordering Disorder* ; gridmakerpro (« no vertical dimension may be a fraction of the unit »).

### 1.4 Le blanc est composé, jamais résiduel
Le blanc autour d'un élément signale son importance plus sûrement que sa taille ; un vide qui reste « en bas » parce que le contenu s'est arrêté n'est pas du blanc, c'est de la place perdue. On décide où va le blanc (en tête, autour du héros, entre les blocs) avant de placer le contenu. **[CONSENSUS]** — Bringhurst (« Space in typography is like time in music ») ; madegooddesigns (« space around an element signals importance more reliably than size alone ») ; Coman/flip180 (le blanc est « any space that a designer chooses to leave empty ») ; Bates/affinity.studio (macro-blanc : « Pull it tight and you get urgency… Open it up and you signal confidence, luxury, or calm »).

### 1.5 La hiérarchie se fait par sauts francs, sur trois niveaux au plus par page
Titre / intertitre ou chapô / corps, avec des rapports de taille nets ; les niveaux intermédiaires (surtitre, légende, folio) sont petits et constants. Un titre de couverture est plus grand que tout titre intérieur ; un titre d'ouverture est plus grand que les titres des pages qui suivent. **[CONSENSUS]** — Lupton (*Thinking with Type*, hiérarchie) ; Bringhurst (échelle classique 6-7-8-9-10-11-12-14-16-18-21-24-36-48-60-72) ; madegooddesigns (« one dominant element… rather than competing focal points »).

### 1.6 Le rythme : alterner dense et aéré, ouvrir fort, fermer explicitement
Une publication est une séquence ; si toutes les doubles pages ont la même densité, le lecteur se fatigue (trop dense) ou s'ennuie (trop aéré). L'ouverture d'un chapitre est le moment le plus « grand » (image pleine page ou titre surdimensionné, un seul élément dominant) ; le climax visuel d'un article tombe au milieu ou au second tiers ; la fin est marquée (cul-de-lampe, colophon, page de citation). Le chemin de fer (flatplan) est l'outil qui rend ce rythme visible avant la maquette. **[CONSENSUS]** — madegooddesigns (« sequences need rhythm… Alternate ») ; BAS-BG ; Publitas ; Makeshoff/designer-daily (« The opening spread is the curtain raiser ») ; Kai Brach, Offscreen (le flatplan « allows you to pace the reading experience ») ; Fonts.com Fontology (end marks).

### 1.7 L'image se cale sur la grille par défaut et la casse à dessein
Bords d'image sur les bords de colonnes et sur la grille de base ; une image dominante par double page, nettement plus grande que les autres (rapport ≥ 2:1) ; le fond perdu et la pleine page sont réservés aux transitions et aux moments forts. La rupture (image qui déborde, silhouette qui habille le texte) est un outil, utilisé rarement et franchement. **[CONSENSUS]** — Müller-Brockmann (les images occupent 1, 2, 3 ou 4 champs ; « the fewer the differences in the size of the illustrations, the quieter the impression ») ; Publitas ; BAS-BG (« one dominant image that is noticeably larger than the rest ») ; Samara (la rupture est un outil).

### 1.8 La lisibilité commande la mesure, la mesure commande le nombre de colonnes
On lit un imprimé à 30–35 cm ; la longueur de ligne confortable est de 45 à 75 signes en colonne unique (66 idéal), 40 à 50 en multicolonne. Le nombre de colonnes se déduit du format et du corps, pas l'inverse. **[CONSENSUS]** — Müller-Brockmann (« read with the eye at a distance of 30-35 cm ») ; Bringhurst §2.1.2 ; Butterick, *Practical Typography* (45–90 signes) ; Tschichold (8 à 12 mots par ligne).

### 1.9 Marges asymétriques et solidaires
Intérieure < tête < extérieure < pied dans le canon classique ; les marges « lock the textblock to the page, lock facing pages to each other, frame the textblock, and protect the textblock » (Bringhurst). En piqûre à cheval de moins de 40 pages, l'ouverture est presque à plat : la marge intérieure n'a pas besoin d'être plus grande que l'extérieure, seule la zone de sécurité compte ; en dos carré collé il faut au contraire élargir l'intérieure. **[CONSENSUS]** sur l'asymétrie et la protection ; **[PARTI PRIS]** classique sur les ratios précis (Tschichold 2:3:4:6, Van de Graaf). — Bringhurst ; Tschichold ; Hendel ; Müller-Brockmann (tolérance de rognage 1–5 mm) ; guides de reliure des imprimeurs de livres.

### 1.10 « Les chiffres sont le visuel » : un seul héros par double page
Quand la donnée est le sujet, elle est traitée comme une image : un chiffre géant, calé sur la grille, avec sa légende, et rien qui lui fasse concurrence sur la double page (pas de deuxième chiffre en dégradé, pas d'image dominante). C'est la pratique des magazines de données (Delayed Gratification, infographies pleine page) ; à confronter à `01-brand/style-guide.md` : si la charte traite les chiffres clés comme des visuels, la règle s'applique telle quelle. **[PARTI PRIS]**, cohérent avec 1.5 et 1.7.

### 1.11 Le petit format demande moins de niveaux et moins de colonnes, pas moins de contraste
Sur A5, une colonne pleine à 10 pt fait ≈ 70 signes, deux colonnes ≈ 34 : la vraie composition à deux colonnes de texte suivi n'est possible qu'à 8–9 pt. On travaille donc en une colonne large + une colonne étroite (légendes, portraits, exergues), et on garde des sauts de taille aussi francs qu'en grand format ; le contraste, pas la profusion, fait le magazine. **[PARTI PRIS]** de cette doctrine, dérivé de 1.5 et 1.8 et vérifié sur les magazines de petit format (Apartamento 17 × 24, Offscreen, Delayed Gratification : voir §4.4).

---

## 2. Règles chiffrées

Les valeurs ci-dessous sont celles des sources ; quand elles divergent, la fourchette est donnée et le choix recommandé pour un fascicule A5 est en gras.

### 2.1 Format, fond perdu, marges, reliure

| Règle | Valeur | Source / statut |
|---|---|---|
| Fond perdu | **3 mm** de chaque côté (5–10 mm en grand format) ; page A5 composée 154 × 216 mm | guides de prépresse ; imprimeurs en ligne ; Müller-Brockmann parle d'une variance de rognage de 1–5 mm **[CONSENSUS]** |
| Zone de sécurité | rien d'important à moins de **5 mm** de la coupe (1/8 in ≈ 3,2 mm au minimum chez les imprimeurs américains) ; côté pli en piqûre à cheval : 3 mm sans détail de part et d'autre du pli | guides de prépresse et d'imprimeurs **[CONSENSUS]** |
| Marges classiques (livre) | inner : head : outer : foot = **2 : 3 : 4 : 6** (Tschichold) ; Van de Graaf : intérieur 1/9 de la largeur, extérieur 2/9, tête 1/9 de la hauteur, pied 2/9 ; bloc de texte ≈ 2/3 × 2/3 de la page (≈ 44 %) — sur A5 : 16 / 25 / 33 / 49 mm, bloc 99 × 136 mm | Tschichold, *The Form of the Book* ; Wikipedia « Canons of page construction » ; retinart.net **[PARTI PRIS classique]** |
| Marges de magazine / brochure | intérieure ≥ **10 mm**, tête 1,25–1,5 × l'intérieure, pied 2–2,5 × l'intérieure ; zone utile 65–75 % de la page. Pour A5 : **tête 12 · extérieur 12 · intérieur 14 · pied 17 mm** (zone 122 × 181 mm) | Coman/flip180media (valeurs), Hendel et Bringhurst (asymétrie : la marge de pied est la plus grande) **[CONSENSUS]** sur l'asymétrie, valeurs **[PARTI PRIS]** |
| Piqûre à cheval | pages en multiple de 4 ; idéale de 8 à 64 pages ; s'ouvre presque à plat, marge intérieure ≈ extérieure ; **creep (chasse)** = (pages − 4) / 4 × épaisseur du papier : pour 24 pages en 120 g (≈ 0,14 mm), ≈ 0,7 mm au cahier central, négligeable sous 40 pages mais à absorber par la zone de sécurité extérieure | guides de piqûre à cheval (« 40 pages ou moins : à peine visible ») ; forums de prépresse **[CONSENSUS]** |
| Dos carré collé (pour mémoire) | marge intérieure élargie de 3 à 6 mm ; jusqu'à 6 mm perdus par page dans le dos ; pas de traversée d'image | guides de reliure **[CONSENSUS]** |

### 2.2 Grille

| Règle | Valeur | Source / statut |
|---|---|---|
| Nombre de colonnes | découle du corps et de la mesure (§2.3), pas l'inverse ; magazine : 2 à 4 colonnes de texte, grilles mères de 5, 7, 9 ou 12 unités ; **A5 : grille mère 12 (ou 6) unités, texte sur 8/12 ou 9/12** | Müller-Brockmann ; madegooddesigns ; Bates ; azuramagazine (nombre impair) **[CONSENSUS]** sur la méthode, nombre **[PARTI PRIS]** |
| Gouttière entre colonnes | = interlignage ou multiple ; **4–5 mm** en print ; ni trop serrée (on lit à travers) ni trop lâche (les colonnes se dissocient) | Samara ; Coman (18 pt pour un interlignage de 12) ; BAS-BG (4–5 mm) **[CONSENSUS]** |
| Grille de base | unité = interlignage du corps ; aucune dimension verticale n'en est une fraction ; hauteurs de champs et d'images en multiples ; **A5 : 5 mm (14,17 pt) pour un corps de 10 pt** | Müller-Brockmann ; Bringhurst §2.2 ; Vinh ; gridmakerpro **[CONSENSUS]** |
| Champs / modules | les images occupent 1, 2, 3 ou 4 champs ; moins de tailles différentes = page plus calme ; espace vertical entre champs = 1 à n lignes | Müller-Brockmann **[PARTI PRIS suisse]**, repris pour l'alignement par Publitas, madegooddesigns |
| Constantes | folio, titre courant, marqueurs de section à la même place sur toutes les pages ; folio et titre courant **7–9 pt** ; folio aligné sur le bord extérieur du bloc de texte | madegooddesigns ; Bringhurst (folios) **[CONSENSUS]** |
| Colonnes asymétriques | la colonne étroite (3/12 ou 4/12) reçoit légendes, notes marginales, portraits, exergues ; toujours du côté extérieur | Bates ; cours WOU (légendes) **[PARTI PRIS répandu]** |

### 2.3 Corps, interlignage, mesure

| Règle | Valeur | Source / statut |
|---|---|---|
| Corps du texte suivi en print | **10–12 pt** (Butterick) ; 9–10 pt en magazine (madegooddesigns) ; 8–12 pt en livre/brochure (Müller-Brockmann) ; pour une sans-serif géométrique à grande hauteur d'x sur non couché : **10 pt**, jamais moins de 9,5 pt pour du texte que l'on lit en continu | practicaltypography.com (rule 2) ; madegooddesigns ; Müller-Brockmann **[CONSENSUS]** sur la fourchette |
| Interlignage | **120–145 %** du corps (Butterick) ; 120–135 % en magazine (madegooddesigns) ; plus pour les sans-serif à grand œil et les lignes longues ; « typesetting without leading is a torture for the reader » (Tschichold). Sans-serif géométrique à 10 pt : **14–14,2 pt (140 %)** | practicaltypography.com (rule 3) ; madegooddesigns ; Tschichold **[CONSENSUS]** |
| Mesure (longueur de ligne) | **45–75 signes** en colonne unique, 66 idéal ; **40–50 en multicolonne** (Bringhurst) ; 45–90 (Butterick) ; 8–12 mots (Tschichold) ; 50–70 (Publitas). Sur A5, pour une sans-serif de chasse moyenne (≈ 0,49 em par signe) à 10 pt : 8/12 = 79 mm ≈ 46 signes, 9/12 = 90 mm ≈ 52, 12/12 = 122 mm ≈ 70 ; **6/12 = 58 mm ≈ 34 signes : interdit pour le texte suivi** | webtypography.net/2.1.2 (Bringhurst) ; practicaltypography.com (rule 4) ; artequalswork.com (Tschichold) **[CONSENSUS]** |
| Légendes et notes | 7–9 pt (7–8 madegooddesigns ; 7–9 BAS-BG) ; **8 pt / 11,3 pt** sur A5 ; mesure ≤ 40 signes en colonne étroite, ≤ 75 en pleine largeur ; jamais 85+ signes à 8 pt | madegooddesigns ; bas-bg.com **[CONSENSUS]** |
| Titres | 30–80 pt (madegooddesigns), 36–72 pt (BAS-BG) en magazine ; sur A5 : ouverture 30–36 pt, géant 48–64 pt, couverture ≥ 44 pt | madegooddesigns ; bas-bg.com **[PARTI PRIS]** de chaque source, cohérents |
| Distance de lecture | 30–35 cm pour un imprimé de format courant : c'est ce qui fixe corps et mesure, indépendamment du format de page | Müller-Brockmann **[CONSENSUS]** |
| Alinéa / paragraphes | retrait de 1 à 4 fois le corps **ou** 4–10 pt d'espace entre paragraphes, pas les deux ; sur A5 à 10/14,17 pt : espace de **5 mm** (une ligne de grille) ou retrait de 5 mm | practicaltypography.com (rule 17) **[CONSENSUS]** |
| Capitales espacées | +5 à 12 % d'interlettrage, réservé aux labels et surtitres | practicaltypography.com (rule 15) ; `01-brand/style-guide.md` **[CONSENSUS]** |

### 2.4 Tailles minimales, défonce, couleur, filets (print, numérique, non couché)

| Règle | Valeur | Source / statut |
|---|---|---|
| Plancher absolu | **texte ≥ 8 pt** en polychromie process ; 4 pt = plancher technique absolu (illisible) ; légendes ≥ 7 pt | prepressure.com ; fasteditor.com **[CONSENSUS]** |
| Texte en défonce (réserve) | ≥ **8–9 pt** et **gras**, jamais de traits fins ; les traits s'amincissent en réserve : « a 1 pt positive line becomes about 2 pt in reverse » ; réservé aux titres et courts fragments | fasteditor.com ; Wikipedia « Reversing type » ; prepressure.com **[CONSENSUS]** |
| Contraste texte/fond | ≥ **4,5:1** pour le texte courant, ≥ 3:1 pour le « grand texte » (≥ 18 pt, ou ≥ 14 pt gras) (WCAG AA, appliqué au print par les guides d'accessibilité) ; en pratique : pas de texte 8 pt en couleur claire ; calculer le contraste de chaque couleur de `01-brand/style-guide.md` sur le papier (ordre de grandeur : un cyan clair saturé sur blanc ≈ 2,4:1, un jaune doré sur blanc ≈ 1,8:1, un anthracite éclairci à 60 % ≈ 3,9:1) | WCAG 2.2 SC 1.4.3 **[CONSENSUS]** sur le seuil |
| Filets | ≥ **0,25 pt** en numérique (0,15–0,2 pt offset), ×2 en réserve ; jamais « hairline » ; réglures écrivables ≥ 0,3 pt et ≥ 40 % d'encre | prepressure.com ; preflight.art ; fasteditor.com **[CONSENSUS]** |
| Résolution | photos et rasters **300 dpi** à taille finale (2 × la linéature) ; trait/bitmap 1 bit 1 200 dpi ; ne jamais agrandir une image de plus de 20 % en maquette | guides de prépresse d'imprimeurs ; guide de préparation des illustrations d'une presse universitaire ; prepressure.com **[CONSENSUS]** |
| Papier non couché | l'encre s'étale (dot gain jusqu'à 20–30 % contre ≈ 5 % sur couché brillant) : les couleurs sortent plus ternes et plus sombres, les gris légers se bouchent, les traits fins s'épaississent ; éviter les gris < 20 %, les textes maigres < 9 pt et les couleurs saturées portant seules un sens (souvent hors gamut CMJN) ; convertir avec le profil du papier (PSO Uncoated v3 / FOGRA52) ou selon la consigne de l'imprimeur | creativepro.com ; guides papetiers **[CONSENSUS]** |

### 2.5 Dispositifs typographiques : lettrines, exergues, chapôs, intertitres, folios, titres courants

| Dispositif | Règle | Source / statut |
|---|---|---|
| Lettrine (drop cap) | 2 à 3 lignes de profondeur (3 = traditionnel) ; **le pied de la lettrine repose exactement sur une ligne de base du texte, son sommet s'aligne sur la hauteur de capitale de la première ligne** ; 2–4 pt d'espace entre la lettrine et le texte ; alignement optique à gauche (A, O, V mordent légèrement dans la marge) ; souvent suivie d'un premier segment en petites capitales ; une seule par article, jamais sur toutes les pages ; à éviter quand le paragraphe s'ouvre sur un guillemet ou ne fait que 2 lignes | cambric.pub « Drop caps » ; infogridpacific « Drop Cap Magic » **[CONSENSUS]** |
| Premier paragraphe | fer à gauche, sans alinéa (l'alinéa signale un *nouveau* paragraphe) | Bringhurst §2.3.1 via webtypography **[CONSENSUS]** |
| Chapô / standfirst / deck | entre le titre et le corps ; corps × 1,2 à × 1,4 (12–14 pt pour un corps de 10), graisse légère ou régulière, 25–45 mots, mesure ≤ 55 signes ; c'est le second point d'entrée de la page et le squelette de la lecture rapide (Monocle garde son « Preface » ; Kinfolk dessine des coupes « text, deck, display ») | magCulture (Monocle redesigned ; Kinfolk) ; Publitas (« stand-firsts, kickers, and drop caps help readers understand exactly where a story begins ») **[CONSENSUS]** |
| Intertitre (crosshead) | même corps que le texte ou un cran au-dessus, graisse forte ; **espace avant nettement supérieur à l'espace après** (une ligne de grille avant, zéro ou une demi-ligne après) pour que le titre « appartienne » au paragraphe qui suit ; jamais en pied de colonne sans au moins deux lignes de texte dessous | Bringhurst §2.2 (retour « en phase » après chaque interruption) ; pratique éditoriale **[CONSENSUS]** |
| Exergue / pull quote | corps × 1,5 à × 2,2 (15–22 pt pour un corps de 10), graisse marquée, mesure courte (25–35 signes) ; placée dans la colonne marginale ou en héros de demi-page ; ne reprend pas mot pour mot une phrase visible à portée de regard ; guillemets de la langue ; ne touche ni filet ni coupe | Makeshoff (les exergues comme « visual hooks ») ; madegooddesigns ; §5 G2/G6 **[CONSENSUS]** sur la fonction, tailles **[PARTI PRIS]** |
| Bloc de citation | espace supplémentaire avant et après (une ligne de grille) ; retrait ou corps réduit d'un cran, pas les deux | Bringhurst §2.3.3 via webtypography **[CONSENSUS]** |
| Folio | même position sur toutes les pages, aligné sur le bord extérieur du bloc de texte (ou centré en pied dans le canon des livres), 7–9 pt ; disparaît sur les pages pleine image | Bringhurst ; madegooddesigns **[CONSENSUS]** |
| Titre courant (running head) | discret (7–9 pt, capitales espacées ou petit gras), en marge extérieure ou en tête, **présent sur toute page courante qui n'a pas de titre** ; Bringhurst déconseille les titres courants dans les livres qui n'en ont pas besoin — dans un fascicule à sections, ils sont au contraire la navigation | Bringhurst ; madegooddesigns ; guides de programmes de conférence (navigation) **[CONSENSUS]** dans le contexte éditorial |
| Cul-de-lampe / marque de fin | un petit signe (hauteur ≈ hauteur d'x ou de capitale) à la fin d'un article qui saute des pages ; un colophon ou une page calme en fin de volume | Fonts.com Fontology ; Wikipedia « End mark » **[CONSENSUS]** |

### 2.6 Veuves, orphelines, césures, drapeau

| Règle | Valeur | Source / statut |
|---|---|---|
| Veuve | dernière ligne d'un paragraphe seule en tête de page ou de colonne : **interdite** (« never begin a page with the last line of a multi-line paragraph ») | Bringhurst §2.4.8 via webtypography **[CONSENSUS]** |
| Orpheline | première ligne d'un paragraphe seule en pied de colonne : à éviter ; mot seul (ou fragment < 12 signes) en dernière ligne d'un paragraphe : à éviter en titre, chapô, exergue, légende, toléré en texte long si le drapeau reste propre (`text-wrap:pretty` le corrige en HTML) | pratique éditoriale ; Kinfolk (« no widows, rivers or ugly breaks ») **[CONSENSUS]** |
| Césures | au moins **2 signes** avant la coupure et **3** après ; **pas plus de 3 lignes consécutives** terminées par une césure ; pas de césure sur la dernière ligne d'un paragraphe ni sur les noms propres et les nombres ; obligatoires en justifié, utiles en drapeau étroit | Bringhurst §2.4.1 et §2.4.3 via webtypography ; Butterick rule 18 **[CONSENSUS]** |
| Drapeau (fer à gauche) | lignes de longueur irrégulière mais sans « trou » (ligne très courte entre deux longues) ni forme en escalier ; on règle par la mesure (§2.3), les césures et, en dernier recours, la réécriture ; le fer à droite (drapeau gauche) est réservé aux légendes courtes de 1–2 lignes | Bringhurst ; Hochuli (voir §2.7) **[CONSENSUS]** |
| Justifié | seulement si les césures sont actives et la mesure ≥ 45 signes ; sinon les rivières apparaissent (Kinfolk les traque explicitement) | Butterick rule 18 ; magCulture (Kinfolk 18) **[CONSENSUS]** |

## 3. Échelle typographique et gabarits de texte pour un A5

L'échelle ci-dessous est calibrée pour une sans-serif géométrique à grande hauteur d'x et à chasse plutôt large (≈ 0,49 em par signe en moyenne, espaces comprises, mesuré à 10 pt ; mesurer celle de la police de marque et ajuster les mesures en conséquence) : une telle police paraît plus grande qu'une humane au même corps, ce qui autorise 9,5–10 pt en texte suivi, mais elle demande un interlignage généreux (≥ 135 %) et des mesures plutôt courtes dans la fourchette (46–60 signes) parce que ses lettres rondes se ressemblent.

### 3.1 Échelle recommandée (parti pris de cette doctrine, construite sur la série de Bringhurst et sur un rapport ≈ 1,25 entre niveaux adjacents)

| Niveau | Corps / interligne | Graisse | Usage | Mesure |
|---|---|---|---|---|
| Folio, mentions | 7,5–8 / 11,3 pt | 500–600 | folio, crédits, colophon | — |
| Légende, note | 8 / 11,3 pt (= 4 mm) | 400 (nom en 600) | légendes, trombinoscope, notes de pied | ≤ 40 signes en colonne étroite, ≤ 75 en large |
| Liste, programme (détail) | 9 / 12,75 pt | 400 | listes, détails d'agenda, tableaux | 30–45 signes |
| **Corps** | **10 / 14,17 pt (= 5 mm)** | 400 | tout texte suivi | **46–70 signes** (8/12, 9/12 ou 12/12) |
| Intertitre | 10 / 14,17 pt | 700 | dans le corps, espace avant 10 mm, après 0 | — |
| Chapô / lede | 12,5 / 17 pt (≈ 6 mm) | 300–400 | sous le titre, 25–45 mots | 45–55 signes |
| Exergue | 16–18 / 20–22,5 pt | 600 | citation dans la marge ou en héros de demi-page | 25–35 signes |
| H2 / titre courant de page | 20 / 22,5 pt | 700 | titre d'une page courante qui n'ouvre pas de chapitre | ≤ 30 signes |
| H1 / ouverture | 30–36 / 32–36 pt | 800 | titre de chapitre | ≤ 3 lignes |
| H1 géant | 48–64 / 46–60 pt | 800 | page de titre, ouverture « affiche » | 1–2 mots |
| Chiffre héros | 96–150 pt, interligne 0,9–1 | 800 | un par double page au plus | 1–4 chiffres |
| Chiffre secondaire | 24–32 pt | 700–800 | cartes de données | — |
| Surtitre / label | 8 / 11,3 pt, capitales, interlettrage 0,08–0,12 em | 600 | rubrique, heure, catégorie | ≤ 3 mots |
| Titre de couverture | ≥ 44 pt | 800 | plus grand que tout titre intérieur | 1–2 lignes |

Note sur les interlignages : tout ce qui n'est pas du corps doit avoir une hauteur totale multiple de 5 mm (une lettrine sur 3 lignes = 15 mm ; un chapô de 3 lignes à 12,5/17 pt = 18 mm → l'arrondir à 20 mm en ajoutant 2 mm sous le chapô ; un exergue de 2 lignes à 18/22,5 = 15,9 mm → 20 mm avec sa marge). Ce n'est pas du purisme : c'est ce qui permet aux blocs de se caler d'une page à l'autre.

### 3.2 Contraste des graisses
Si la police de marque décline plusieurs graisses (300 à 800 par exemple), deux règles : ne pas mettre côte à côte deux graisses adjacentes (400/500, 600/700) — le contraste doit se voir à 2 m ; et ne pas utiliser plus de trois graisses par double page (par exemple 300 chapô, 400 corps, 700–800 titres). Le 800 est réservé aux titres et chiffres, le 300 aux chapôs et grands corps (il devient trop maigre sous 12 pt sur non couché).

### 3.3 Micro-typographie qui compte en print
- Guillemets et apostrophes typographiques de la langue (« » en français, “ ” en anglais) ; espaces insécables devant les unités et les deux-points français ; pas de point final aux titres ; chiffres alignés à droite dans les colonnes horaires ; les nombres et unités ne se séparent pas en fin de ligne (`&nbsp;`).
- Capitales espacées : 5–12 % d'interlettrage (0,05–0,12 em) et jamais sur un titre entier (Butterick ; `01-brand/style-guide.md`).
- Un seul espace après le point ; alinéa *ou* espace entre paragraphes (4–10 pt), pas les deux (Butterick).

## 4. La double page, le rythme, le chemin de fer

### 4.1 Composer la double page
- **Un point d'entrée principal par double page** (titre ou image dominante), des points d'entrée secondaires (chapô, exergue, légendes, lettrine) qui disent « l'article commence ici » (madegooddesigns ; Publitas). **[CONSENSUS]**
- **Le lecteur atterrit à droite** et balaie vers la gauche ; les images sont vues d'abord dans le tiers supérieur (PMG, observations non chiffrées). Conséquence pratique : le titre d'une ouverture peut être à droite avec l'image à gauche, ou l'inverse, mais l'élément dominant occupe la page où l'on veut que le regard s'arrête. **[PARTI PRIS]** d'observation.
- **Alignements traversants** : premières lignes de texte des deux pages à la même hauteur (± 0,5 mm) ; blocs de pied calés sur la même ligne ; filets et images qui traversent le pli calés au dixième de millimètre. Ce que Bringhurst appelle « lock facing pages to each other ». **[CONSENSUS]**
- **Le blanc se répartit sur la double page**, pas sur chaque page séparément : une page pleine peut faire face à une page presque vide si le vide est le halo d'un héros (Bates : « 80 % negative space with a single dense cluster of type commands attention ») ; deux pages tassées en tête avec deux vides en pied ne forment jamais une composition. **[CONSENSUS]** sur le principe, ratio 80 % **[PARTI PRIS de Bates]**.
- **Ce qui traverse la gouttière** en piqûre à cheval : images (idéalement au cahier central), filets, titres en très gros corps ; jamais de texte courant, de visage, de diagonale, ni de détail à moins de 3 mm du pli (guides des imprimeurs sur les images à cheval). **[CONSENSUS]** des imprimeurs.

### 4.2 Le rythme d'un fascicule
- **Trois régimes** : les pages d'entrée (sommaire, mot d'accueil, présentation) se feuillettent — titres brefs, plusieurs points d'entrée ; le cœur (récits, programme, portraits) se lit — typographie discrète, mesure confortable ; les pages de service (règles, QR, notes, à compléter) se consultent — modules distincts, séparés visuellement (Makeshoff/designer-daily ; Kai Brach pour Offscreen). **[CONSENSUS]** sur la structure, formulation en trois modes **[PARTI PRIS de Makeshoff]**.
- **Alternance** : après une double page dense, une double page dominée par l'image ou par un chiffre ; après une double page de texte, une double page de grille (portraits, programme) (madegooddesigns ; BAS-BG ; Publitas). **[CONSENSUS]**
- **Ouvrir fort, une fois par cahier** : une ouverture pleine (image ou titre géant) toutes les 6 à 8 pages ; entre deux ouvertures, les pages courantes gardent la même « taille » de titre. **[CONSENSUS]** sur le principe d'ouverture, périodicité **[PARTI PRIS]** de cette doctrine.
- **Le climax visuel avant la fin** : dans un article, au milieu ou au second tiers (BAS-BG) ; dans un fascicule, la double page la plus spectaculaire n'est pas la dernière : la fin est calme (citation, à compléter, colophon) et signalée (cul-de-lampe, colophon ; Fonts.com Fontology, end marks). **[PARTI PRIS de BAS-BG]** pour la position, **[CONSENSUS]** pour le signal de fin.
- **Répétition + variation** : le rythme naît des constantes (folio, surtitre, filet, marges) *et* des écarts d'échelle entre les doubles pages (Makeshoff ; Samara). Une publication où toutes les pages ont le même en-tête au même endroit et la même densité est perçue comme plate, quelle que soit la qualité de chaque page. **[CONSENSUS]**

### 4.3 Chemin de fer d'un fascicule de 24 pages + couverture (courbe de densité)
Le chemin de fer se dessine avant la maquette, double page par double page, avec pour chacune : le gabarit (G1–G8), l'élément dominant, la densité prévue (aérée / moyenne / dense) et les lignes d'accroche utilisées. Exemple pour un carnet d'événement fictif de deux jours, 24 pages intérieures :

| Double page | Gabarit | Dominant | Densité | Note |
|---|---|---|---|---|
| C2 · 1 | Sommaire + page de titre | titre géant p. 1 | aérée | p. 1 seule à droite : le titre occupe la moitié haute, une carte « appartient à » (champ à remplir) le pied |
| 2 · 3 | G2 texte courant | portrait + exergue | moyenne | mot d'accueil ; première ligne sur B des deux côtés ; l'exergue en héros de la page de droite |
| 4 · 5 | G1a ouverture image | image à fond perdu | aérée → dense | image à gauche, titre à droite, texte court |
| 6 · 7 | G5 trombinoscope | grille de médaillons | régulière | titre à gauche, titre courant à droite |
| 8 · 9 | G3 chiffres + G6 citation | un chiffre géant / une exergue | dense → aérée | le chiffre principal remplit la moitié de p. 8 ; p. 9 = récit court + citation en héros |
| 10 · 11 | G4 programme | colonne d'heures | dense, pas constant | jour 1 et jour 2, même gabarit sur les deux pages |
| 12 · 13 | G2 variante « fiches » (double page centrale) | portraits ø36 + titres de session | moyenne | intervenants ; seule double page où une image peut traverser le pli sans risque |
| 14 · 15 | Service (QR) + infos pratiques | le QR seul | aérée | le QR est l'image de la page |
| 16 → 22 | Notes | réglure | vide | même réglure par double page |
| 23 · 24 | G7 fin | questions à compléter / colophon | moyenne → vide | la dernière double page est calme |
| C3 · C4 | plan / QR | une carte, un QR | aérée | le titre ne touche pas la carte |

Ce tableau se lit aussi comme une courbe : aéré – moyen – aéré/dense – régulier – dense/aéré – dense – moyen – aéré – vide – calme. Si deux doubles pages consécutives ont la même densité *et* le même gabarit, on change l'une des deux.

### 4.4 Ce que font les magazines contemporains de petit et moyen format, et ce qu'on en retient pour un A5

| Titre (format) | Ce qui est documenté | Source |
|---|---|---|
| **Monocle** (200 × 265 mm, 196–300 p.) | Palette fermée Plantin + Helvetica, Helvetica « quite neutral and used at small sizes only » pour légendes et données, d'où une hiérarchie qui « worked each time » (Ken Leung) ; grille à trois colonnes, non couché, isotypes, lettrines dessinées ; rubriques courtes (blurbs, listes, profils d'une page, Q&A) qui « encourage skimming rather than deep reading » ; refonte 2017 : corps augmenté sur retours lecteurs, moins de polices, plus de blanc, « braver about showing less », le chapô (« Preface ») conservé | Coles/FontFeed 2009 ; Design Observer 2014 ; Eye 2007 ; magCulture « Monocle redesigned » |
| **Kinfolk** (228 × 295 mm, 176–194 p.) | Deux familles (serif « quirky » + sans humaniste), trois couleurs, aucune veuve ni rivière ; pages qui semblent « started busier and slowly been reduced and refined » ; **grille à douze colonnes « enabling flexible layouts and varied pacing »** ; papier couché réservé au cahier features ; refonte 2021 : famille sur mesure (serif + sans, coupes texte et display), « frame [the imagery] as best as you can and not let your design ego get in the way » (Alex Hunting) | magCulture (Kinfolk 18, interview Hunting) ; D&AD 2017 ; It's Nice That 2021 |
| **The Gentlewoman** (230 × 300 mm, 304 p.) | Lyon + Futura, texte parfois centré ; sections « very clearly » définies par des **ouvertures pleine page « Part One, Two… »** ; pages « References » en fin de feature qui « punctuate the entire issue » ; couverture = portrait N&B encadré d'une couleur | Fonts In Use n° 9 ; Leslie, AIGA Eye on Design 2015 ; magCulture n° 7, n° 12, n° 33 |
| **Delayed Gratification** (195 × 240 mm, 120 p.) | Chronologie du trimestre, brèves qui débouchent sur features, infographies et photo-essais ; **corps du n° 1 en 7,5 pt, jugé trop petit par les lecteurs** ; un seul designer (Christian Tate) ; « lots of little infographics… but also lots of really big ones », ≈ 5 doubles pages d'infographie par numéro utilisées comme respiration (« if you have just read a ten-page story… you don't want another ten pages like that ») ; l'infographie « telling the last line of a story instantly on the page » | magCulture (Rob Orchard ; DG turns 15 ; DG 39) ; slow-journalism.com |
| **Apartamento** (170 × 240 mm, non couché) | « The same functional layout and typeface selection since 2008 » : Clearface pour les titres, deux graisses de Futura pour tout le reste, texte justifié, nombre de colonnes variable, texte parfois en couleur ; « almost only with typography and photography, playing with the format and the materials » (Omar Sosa) ; dos à motifs pour mériter « a place on their shelves » ; textes plus longs à nombre d'histoires constant | Fonts In Use ; Klim ; marklives ; magCulture ; It's Nice That |
| **Courrier international** (formule 2010, Berliner) | Couple à fort contraste Omnes (sans ronde et lourde) + Freight (Display et Micro), jaune signal, plus de cartes, chronologies et portfolios ; peu de sources analytiques sur la grille actuelle | Fonts In Use (Coles 2010) ; Logo en vue ; Wikipedia |
| **Offscreen** (160 × 220 mm, 128 p., non couché recyclé, cousu à plat) | Refonte n° 16 : « just one type family », plus de blanc, illustrations au trait, format réduit pour « feel even more like a book » ; une police invitée par numéro ; le cas le plus proche d'un fascicule A5 | onemanandhisblog 2017 ; offscreenmag.com/about/production |
| **Works That Work** (Typotheque) | Une seule police (Lava) pour texte, légendes et titres, « the sole constant characteristic » ; design « confident enough not to need to show off » (Biľak) | Fonts In Use (Kupferschmid 2014) ; Stack |
| **Real Review** (115 × 260 mm, 100 p., 60 g) | Pli vertical qui donne « a four-column spread », « every square millimetre counts », « beautiful, but not precious » ; contre-exemple utile : la densité assumée | It's Nice That 2016 ; BP&O 2017 |
| **Weapons of Reason** (116 p.) | Équilibre features / infographies / illustration / photo, « light while communicating the weight of the problems » ; rubrique « What now? » en fin d'article | It's Nice That ; magCulture ; Stack |

**Douze principes transposables à un fascicule A5 de 24 à 32 pages** (chacun appuyé par au moins un des titres ci-dessus ; « convergent » = plusieurs titres) :
1. **Palette typographique fermée, rôles fixes** : deux familles au plus, une par registre ; ou une seule famille avec des coupes distinctes (Works That Work, Offscreen, Monocle, Apartamento — convergent). Une seule famille de marque est donc parfaitement défendable ; ce sont les graisses et les corps qui font les registres.
2. **Le petit corps neutre pour légendes et données, le titrage pour la voix** (Monocle) : la hiérarchie tient si chaque taille a un rôle unique.
3. **Ne jamais descendre sous 8 pt, et 9–10 pt pour lire** : Delayed Gratification a regretté 7,5 pt, Monocle a agrandi son corps (deux titres, même leçon).
4. **Une grille fine, divisible, qui autorise le changement de rythme** : douze colonnes chez Kinfolk « to vary the pace », trois chez Monocle, quatre par pli chez Real Review — la finesse sert la variété, pas la complexité.
5. **Ouvertures de rubrique franches** : pleine page « Part One » (Gentlewoman), noms de section en toutes lettres (Monocle 2017), « section openings » (Square One) ; dans 24 pages, une ouverture par section suffit.
6. **Alterner long et court, la donnée comme respiration** (Orchard : après dix pages de récit, pas dix pages de plus ; WoR ; Monocle — convergent).
7. **Choisir un régime (blanc ou dense) et s'y tenir** : Monocle, Kinfolk et Offscreen vont vers « montrer moins » ; Real Review vers « chaque millimètre compte » ; le mélange des deux dans un même objet donne l'impression de pages inachevées.
8. **Chapô systématique** : la triade titre / chapô / corps est le squelette de la lecture rapide (Monocle « Preface », Kinfolk « text, deck, display »).
9. **Le papier non couché et le format livre font l'objet** (Apartamento, Monocle, Offscreen, Real Review — convergent) : un carnet d'événement en 120 g non couché s'inscrit dans cette lignée.
10. **Le chiffre est un visuel à part entière** : ≈ 5 doubles pages d'infographie par numéro chez DG, cartes et chronologies chez Courrier, data-viz chez WoR ; une donnée-héros par double page vaut une photo.
11. **L'humain plein cadre, traité uniformément** : portrait N&B encadré (Gentlewoman), photo « framed » sans ego (Kinfolk), intérieurs non mis en scène (Apartamento) ; pour un trombinoscope, même cadrage, même traitement.
12. **Penser collection** : dos, tranche, matière (Apartamento, Real Review, TED : tranche peinte) ; un fascicule qu'on garde est un fascicule qu'on a envie de ranger.

### 4.5 Brochures et carnets d'événement : exemples et principes

**Exemples documentés.** TEDGlobal 2013 program guide (Hybrid Design, 168 p., 184 × 241 mm, quadri + 2 Pantone, tranche peinte fluo, un jaune « agent of differentiation ») ; Square One SF conference guide 2019 (104 p., ≈ 124 × 200 mm, riso une couleur sur papier teinté, Apoc + Suisse Int'l, programme, intervenants, guide de la ville, texte justifié, « section openings ») — le modèle direct pour un petit format économique et désirable ; AIGA Design Conference (Sean Adams, FF Real choisie pour « clear information design ») ; livret 3T Warrior Academy (16 p., piqûre à cheval, programme, intervenants, notes, espace de réflexion : « a booklet that would become a personal keepsake ») ; Field Notes (89 × 140 mm, 48 p., piqûre 3 agrafes, 90 g intérieur, kraft en couverture, réglure 6,4 mm, quadrillage 4,7 mm, champs d'identité en 2e de couverture) comme étalon de l'objet à garder ; Real Review (« a precise moment of being useful »).

**Principes (avec règles chiffrées quand elles existent).**
- **Structure canonique** : couverture ; mot d'accueil ; sommaire ou « at a glance » ; programme ; intervenants ; plan / infos pratiques ; partenaires ; notes ; 4e de couverture utile (guides de programmes de conférence, Wikipedia « Program book », Square One — convergent). Remplacer le plan par le lieu et son histoire est un choix de ton, pas une faute de structure.
- **Le programme se comprend sans la mise en page** : « seeing the layout isn't required to understand when and where a session happens » ; une colonne pour l'heure, une par lieu ou par piste (CSS-Tricks, principe web transposable). Chiffres tabulaires obligatoires pour les colonnes d'heures (Butterick, « Alternate figures ») ; **pas de tableau en cage** : « tables should not be set to look like nets with every number enclosed » (Tufte citant Tschichold, *Envisioning Information* p. 55) — filets horizontaux gris clair ou aucun, jamais de verticaux ; timeline graphique seulement à partir de plusieurs pistes parallèles (Tufte, graphical timetables) ; le codage couleur des pistes est un usage répandu, pas une règle chiffrée.
- **Trombinoscope** : légendes 8–10 pt (7 pt minimum dans les petits livres), corps 10 pt (9 pt acceptable en petit format), titre secondaire 14–18 pt, « caption width should be consistent… ideally across the entire spread » (Jostens) ; ≈ 2 mm entre les photos, marge de pied 2 à 4 picas plus haute que les autres, un « eyeline » qui unifie la double page (Herff Jones) ; nom sous ou à côté du portrait (Studio Source). Calcul A5 (non sourcé, dérivé) : 3 × 4 = 12 portraits de ≈ 30–34 mm avec nom 8–9 pt (dense, type index) ; 2 × 3 = 6 portraits de ≈ 50 mm avec fonction et deux lignes (confortable) ; 2 × 2 = 4 avec mini-bio.
- **Pages de notes** : réglures normatives 6,4 mm (narrow US), 7,1 mm (college), 8 mm (adulte UK, Seyès), quadrillage 5 mm en Europe (Wikipedia « Ruled paper ») ; grilles de points à 5 mm chez Leuchtturm1917, Rhodia, Baron Fig, avec des points « très clairs » (Well-Appointed Desk) ; Field Notes 6,4 / 4,7 mm. Retenir **6,5–7 mm de réglure ou 5 mm de points, gris clair**.
- **Faire écrire pour faire garder** : questions ouvertes avec espace de réponse, « space for personal notes » (guides de livrets de conférence), champs d'identité en 2e de couverture (Field Notes) ; le rapport pages éditoriales / pages de notes n'est chiffré par aucune source (dans les exemples : de 20 à 50 %).
- **Fabrication en piqûre à cheval** : pages en multiple de 4, de 8 à 64 ; creep jusqu'à ≈ 3 mm à 32 pages selon le papier (élargir légèrement les marges intérieures ou laisser l'imposition compenser) ; fond perdu 3 mm ; intérieur 105–120 g, couverture 215–270 g, éviter les cartes trop épaisses qui plient mal ; format courant 5,5 × 8,5 in ≈ A5 (guides de piqûre à cheval). Papier et finition qui font l'objet : riso sur papier teinté (Square One), Pantone + tranche peinte (TED), cousu à plat (Offscreen), 60 g (Real Review), kraft (Field Notes).
- **Erreurs fréquentes** : conflits d'intervenants et pauses trop courtes ; navigation impossible sans ouvertures de section (guides de programmes de conférence) ; corps trop petit (DG 7,5 pt) ; tableau en cage de filets (Tufte) ; troisième police ; livret jetable sans page où écrire (guides de livrets d'événement).

## 5. Répertoire de gabarits de doubles pages (fascicule A5 piqué à cheval)

Les gabarits ci-dessous forment un système : mêmes marges, même grille mère, même grille de base, mêmes constantes. Ce qui change d'un gabarit à l'autre, c'est la lecture de la grille, la place du blanc et l'élément dominant. Un fascicule de 24 pages en utilise cinq ou six, jamais un seul.

### 5.0 Conventions communes (à déclarer une fois dans le CSS, jamais page par page)

| Élément | Valeur | Justification |
|---|---|---|
| Page rognée | 148 × 210 mm ; page composée 154 × 216 mm (fond perdu 3 mm) | §2.1 |
| Marges depuis la coupe | tête 12 · extérieur 12 · pied 17 · intérieur 14 mm → zone utile 122 × 181 mm (≈ 70 % de la page) | parti pris « magazine » ; le canon des livres (§2.1) donnerait 16 / 25 / 33 / 49 mm et une zone de 45 %, inadaptée à 24 pages denses |
| Grille mère | 12 colonnes de 6,5 mm, gouttières 4 mm ; lue le plus souvent en 6 (colonnes de 17 mm) ou en 4 (27,5 mm) ; découpes usuelles : 8+4, 4+8, 6+6, 9+3, 10+2 (en douzièmes) | §2.2 ; divisibilité (Bates, Vinh) |
| Grille de base | 5 mm exactement (= 14,17 pt) ; corps 10 pt / 14,17 pt ; tout espacement vertical est un multiple de 5 mm ; les blocs de 8 pt sont sur 11,34 pt (= 4 mm, soit 5 lignes de légende = 4 lignes de corps) | §1.3 |
| Lignes d'accroche (depuis la coupe haute) | **A** = 12 mm (tête de zone : surtitre ou haut d'image) · **B** = 40 mm (première ligne de texte des pages courantes, ou haut du premier bloc) · **C** = 145 mm (ligne de pied des blocs bas : cartes, exergues, légendes) · pied de zone = 193 mm | chaque double page en utilise au moins deux, sur ses deux pages : c'est ce qui rend l'unité perceptible malgré des grilles différentes (Lupton, hang line ; madegooddesigns) |
| Constantes | folio et titre courant au même endroit et à la même taille sur toutes les pages (sauf pleine page image) ; un surtitre unique (8 pt capitales espacées) ; le filet signature éventuel | §1.2 |
| Mesures autorisées pour le corps 10 pt | 8/12 (79 mm, ≈ 46 signes) · 9/12 (90 mm, ≈ 52) · 12/12 (122 mm, ≈ 70). Jamais 6/12 (58 mm, ≈ 34 signes) pour du texte suivi ; 6/12 seulement pour des listes ou légendes à 8–9 pt | §2.3 |

### G1 · Ouverture de chapitre
**Intention.** Signaler un changement de section au feuilletage, en moins d'une seconde. C'est la double page la plus « grande » du chapitre ; les pages qui suivent sont plus petites qu'elle.
**Composition, deux variantes à alterner d'un chapitre à l'autre :**
- *G1a, l'image qui casse la grille* : page de gauche = image ou illustration à fond perdu sur toute la page ou sur les deux tiers hauts (jusqu'à 140 mm), aucun texte dessus sauf le surtitre ; page de droite = surtitre sur A, titre 40–60 pt à partir de B, chapô 12,5/17 pt sur 8/12, texte courant qui commence à 100 mm ou pas de texte du tout. Le folio de la page image disparaît, celui de droite reste.
- *G1b, le chiffre héros* : page de gauche = un seul chiffre 96–150 pt calé en pied sur C, légende 12,5 pt en dessous, rien d'autre ; page de droite = titre + texte. Le chiffre occupe au moins 40 % de la hauteur de page, sinon ce n'est pas un héros.
**Règles.** Un seul point d'entrée par double page (le titre) et un seul héros (image ou chiffre, jamais les deux). Le titre est le plus grand texte des 4 à 6 pages qui suivent. Aucun autre chiffre en dégradé sur la double page. Le blanc va *autour* du héros, pas en pied.
**Pièges.** Titre et image qui se disputent le coin haut gauche ; titre d'ouverture plus petit qu'un chiffre de page courante ; texte courant qui démarre sur l'ouverture avec la même densité qu'une page courante ; ouverture qui ressemble trait pour trait à la page suivante (même surtitre, même H1, même hauteur).
Sources : §1.5, §1.6, §1.7 (madegooddesigns, Makeshoff, Publitas, 123RF, InDesignSkills).

### G2 · Texte courant (lettre, récit, mot d'accueil)
**Intention.** Lire 300 à 700 mots confortablement, à la main, sans effort.
**Composition.** Une seule colonne de 8/12 (79 mm, 46 signes) ou 9/12 (90 mm, 52 signes) à 10/14,17 pt ; la colonne restante (4/12 ou 3/12) porte portraits, exergue, notes marginales, du côté extérieur (là où le pouce tient la page) ; la colonne de texte est côté pli. Première ligne de texte sur B pour les deux pages ; dernière ligne libre, mais jamais au-dessus de 60 % de la hauteur de zone sur la page de gauche si la page de droite continue.
**Lettrine.** Sur exactement 3 lignes : hauteur du sommet des capitales à la ligne de base de la 3e ligne = 3 × 14,17 = 42,5 pt ; graisse forte, couleur d'accent ; 2 mm d'espace à droite ; alignée à gauche sur la marge de colonne. Une seule lettrine par article, seulement si le premier paragraphe fait ≥ 4 lignes.
**Exergue.** 15/19 à 18/22 pt, graisse 600, sur 4/12 (38 mm) ou 5/12 (48 mm) dans la colonne meuble ; à ≥ 40 mm de la phrase qu'elle cite, et jamais mot pour mot une phrase visible sur la même double page ; filet d'accent 1 mm côté texte ; l'exergue ne touche aucun autre filet ni la coupe (≥ 5 mm).
**Signature / date.** 10 pt 600, un blanc de deux lignes (10 mm) au-dessus.
**Rythme.** Quand le texte est court (moins de 60 % de la double page), on ne le tasse pas en tête : on remonte C, on agrandit les portraits (36 → 44 mm) ou on ajoute une exergue pleine largeur ; le blanc va en tête ou entre les blocs, jamais en pied.
Sources : §2.3 (Bringhurst, Butterick, Hochuli) ; §2.5 (lettrines, exergues).

### G3 · Page de chiffres (bento de données)
**Intention.** « Les chiffres sont le visuel » : un chiffre principal, quatre à six secondaires, une phrase de contexte.
**Composition.** Le chiffre principal fait ≥ 3 fois la taille des secondaires (96–120 pt contre 24–32 pt) et occupe une carte 8/12 × 70–90 mm ; les secondaires vont sur des cartes 4/12 ou 6/12 de hauteur constante (35 ou 40 mm) ; le bento remplit la zone entre B et C — s'il reste plus de 20 mm, on augmente la hauteur des cartes, on ne laisse pas de vide sous le bento. Une légende de 8/11,3 pt sous chaque chiffre, deux lignes maximum, jamais plus de 40 signes par ligne. Le chiffre est calé en bas de sa carte (ligne de base commune) ; unité et signe (%, M, +) à la moitié de sa taille.
**Couleur.** Dégradé de marque (s'il existe) sur le seul chiffre principal ; les secondaires en couleur primaire ou foncée de la marque, jamais tous en dégradé (sinon plus rien n'est héros).
**Piège technique.** Chiffre en dégradé = raster à l'export, et masque perdu à la conversion CMJN : passer par `14-print/lib/chiffre-svg.py` puis `chiffres-png.sh` (§6.2).
Sources : §1.10 ; `01-brand/style-guide.md` ; Delayed Gratification (§4.4).

### G4 · Page de programme
**Intention.** Trouver l'heure et le lieu en trois secondes, sans lire.
**Composition.** Une journée par page, même gabarit sur les deux pages ; heures en colonne fixe de 14 mm alignées sur les deux-points, 11 pt 700 ; intitulés 10 pt 600, détails 8,5–9 pt 400 sur une seule ligne. Un créneau = une ligne de grille de base par ligne de texte + 3 mm ; **le pas entre créneaux est constant sur les deux pages** (jamais une page « serrée » et une page « aérée » côte à côte : c'est le nombre de créneaux qui varie, pas le pas). La première ligne des deux journées est à la même hauteur (B).
**Couleur.** Trois catégories au plus (travail / repas / social), signalées par une couleur de fond claire ou un filet, avec la légende sur la première page seulement ; le texte des blocs colorés reste dans la couleur de texte (jamais du blanc 8 pt sur une couleur claire) ; l'optionnel est en pointillé ou en gris, pas une 4e couleur.
**Pied.** La note du lendemain (départ, checkout) en 9 pt sur 8/12 maximum, jamais 85 signes par ligne ; ou comme dernier créneau.
Sources : §2.3 (mesure des notes), §2.6 (défonce et couleur), designer-daily (les pages « service » sont « chunked into distinct, visually separate modules »).

### G5 · Trombinoscope
**Intention.** Reconnaître les gens ; le carnet sert de « qui est qui » pendant l'événement.
**Composition A5.** 3 × 4 par page (12 par page, 24 sur la double), médaillons ø30 mm sur un pas horizontal de 40 mm et vertical de 44 mm (portrait + 2 lignes de légende) ; ou 3 × 3 avec ø34 mm si le nombre le permet. Légende centrée sous le médaillon : nom 8,5–9 pt 600, ville ou fonction 8 pt 400 en couleur pleine (pas d'opacité). Le titre de section n'est que sur la page de gauche ; la page de droite porte un **titre courant** (« Participants · 13–24 ») sur A pour ne pas laisser 25 mm de vide au-dessus de la première rangée. Si des filets relient les médaillons pour dire « un seul collectif », ils traversent la gouttière : interrompus 3 mm avant le pli, repris 3 mm après, à la même hauteur exacte (règle des images à cheval des imprimeurs).
**Portraits.** Même cadrage (buste, visage à 55–60 % de la hauteur du médaillon), même densité de trait, même traitement des accents de couleur : dans une grille de 24, l'œil compare, et un portrait plus pâle se voit immédiatement (Müller-Brockmann : moins de différences = page plus calme).

### G6 · Page de citation
**Intention.** Respirer, mémoriser une phrase, marquer une transition. C'est la seule page où le blanc est majoritaire à dessein.
**Composition.** Citation 20–26 pt, graisse 600–700, sur 8/12 ou 9/12, calée en tête de zone ou centrée sur la ligne médiane (108 mm), jamais posée en pied comme une note ; guillemets de la langue de la citation ; attribution 9 pt 400 à 5 mm sous la dernière ligne, alignée sur la première lettre du texte (pas sur le guillemet) ; traduction éventuelle 10 pt 300 sous l'attribution. Le reste de la page est vide, folio compris. Une seule citation par cahier de 8 pages ; sinon l'effet s'use.
Sources : §1.4 (le blanc composé), §2.5 (exergues).

### G7 · Pages de fin : à compléter, notes, colophon
- **À compléter** : amorces 10–11 pt 700 ; réglures pleines à 8 mm d'espacement, épaisseur 0,3–0,4 pt, encre à 100 % ou ≥ 40 % (un filet à 20 % de gris disparaît sous le stylo sur non couché) ; 3 blocs par page au plus ; les cartes remplissent la zone B → C.
- **Notes** : réglure 6,5–7 mm ou grille de points 5 mm, épaisseur 0,25–0,3 pt, gris 20–25 % ; la même réglure sur les deux pages d'une double page ; en-tête « Notes » sur A, avec le jour ou la session si le programme le permet.
- **Colophon** : 8/11,3 pt, un seul bloc de 6 à 8 lignes calé en pied de zone (C ou pied) et sur la marge extérieure ; police, tirage, crédits d'illustration, adresse ; logo ≥ 12 mm au-dessus. La page reste largement blanche : c'est un usage (fin de volume), pas un vide.
Sources : pratique des carnets et field notes (§4.5) ; imprimeurs pour les épaisseurs de filets (§2.7).

### G8 · Couverture (rappel)
Le titre est le plus grand texte de l'objet ; un seul visuel, qui tient la page (fond perdu ou ≥ 50 % de la surface) ; date et lieu en un bloc de 12–14 pt ; pas de vocabulaire d'interface (badges, pilules) ; logo à taille de marque (12–18 mm), fond nu ; le dos est vide en piqûre à cheval. Le sommaire en C2 hiérarchise (numéros gros, sections principales en gras, annexes en petit).

### 5.9 Schémas (double page vue à plat ; A, B, C = lignes d'accroche ; ▓ = image ou héros, ≡ = texte courant, ○ = médaillon, □ = carte)

```
G1a ouverture image             G1b ouverture chiffre           G2 texte courant
┌──────────┬──────────┐        ┌──────────┬──────────┐        ┌──────────┬──────────┐
│▓▓▓▓▓▓▓▓▓▓│ surtitre A│        │          │ surtitre A│        │ surtitre │          │A
│▓▓▓▓▓▓▓▓▓▓│ TITRE     │        │          │ TITRE    │        │ ○  ≡≡≡≡≡ │ ≡≡≡≡≡    │B
│▓▓▓▓▓▓▓▓▓▓│ chapô    │B       │          │ chapô    │B       │    ≡≡≡≡≡ │ ≡≡≡≡≡    │
│▓▓▓▓▓▓▓▓▓▓│          │        │  42      │ ≡≡≡≡≡    │        │ ○  ≡≡≡≡≡ │ ≡≡≡≡≡ ex.│
│▓▓▓▓▓▓▓▓▓▓│ ≡≡≡≡≡    │        │  (héros) │ ≡≡≡≡≡    │        │    ≡≡≡≡≡ │ ≡≡≡≡≡ ex.│
│▓▓▓▓▓▓▓▓▓▓│ ≡≡≡≡≡    │C       │ légende  │          │C       │ ○  ≡≡≡≡≡ │ sign.    │C
│          │       12 │        │       12 │       13 │        │ 2        │        3 │
└──────────┴──────────┘        └──────────┴──────────┘        └──────────┴──────────┘

G3 chiffres (bento)             G4 programme                    G5 trombinoscope
┌──────────┬──────────┐        ┌──────────┬──────────┐        ┌──────────┬──────────┐
│ surtitre │ surtitre │A       │ Jour 1   │ Jour 2   │A       │ TITRE    │ t. courant│A
│ TITRE    │ TITRE    │        │ 09:00 □□ │ 07:00 □□ │B       │ ○  ○  ○  │ ○  ○  ○  │B
│ chapô    │ ≡≡≡≡≡    │B       │ 10:00 □□ │ 09:00 □□ │        │ ○  ○  ○  │ ○  ○  ○  │
│ ┌──────┐ │ ≡≡≡≡≡    │        │ 12:00 □□ │ 10:30 □□ │        │ ○  ○  ○  │ ○  ○  ○  │
│ │ 100  │ │          │        │ 14:00 □□ │ 12:00 □□ │        │ ○  ○  ○  │ ○  ○  ○  │
│ └──────┘ │ « exergue│        │ 17:00 □□ │ 14:00 □□ │        │          │          │
│ □ □ □ □  │   héros »│C       │ 19:00 □□ │ 22:00 □□ │C       │ légende  │          │C
│        8 │        9 │        │       10 │       11 │        │        6 │        7 │
└──────────┴──────────┘        └──────────┴──────────┘        └──────────┴──────────┘
```
Ce qui ne change jamais d'un schéma à l'autre : la position du folio, la ligne A du surtitre ou du titre courant, la ligne C des pieds de blocs, les marges. Ce qui change : la lecture de la grille, l'élément dominant, la place du blanc.

## 6. Spécificités du petit format (A5) et de la chaîne HTML → PDF

### 6.1 Ce qui marche à l'échelle A5, ce qui ne marche pas
- **Une colonne large + une colonne étroite** (8/12 + 4/12, ou 9/12 + 3/12) est la structure la plus robuste : texte suivi à 46–52 signes, marge « meuble » pour portraits, notes, exergues, légendes (Bates : « a narrow outer column becomes a margin note zone » ; cours WOU : légendes dans les colonnes étroites extérieures). **[CONSENSUS]** sur la lisibilité, **[PARTI PRIS]** sur la structure.
- **Deux colonnes égales de texte suivi** ne marchent qu'à 8–9 pt (≈ 40 signes) : c'est le régime « guide pratique », pas le régime « lecture ». En 10 pt, deux colonnes de 58 mm donnent 34 signes : drapeau troué, césures obligatoires. À réserver aux listes, programmes, fiches pratiques, légendes.
- **Trois colonnes** : uniquement pour des grilles d'objets (trombinoscope 3 × 4, sommaires, tableaux horaires), jamais pour du texte.
- **Le titre géant fonctionne mieux qu'en grand format** : sur une page de 148 mm, un mot à 60–72 pt occupe la largeur et fait « affiche » ; c'est l'outil d'ouverture le moins coûteux (madegooddesigns, InDesignSkills : « big, bold typography » sur les ouvertures).
- **Les images pleine page et à fond perdu** sont proportionnellement plus fortes qu'en A4 : une par cahier de 8 pages suffit à rythmer.
- **Les corps petits ne descendent pas avec le format** : on lit un A5 à la même distance qu'un A4 ; 10 pt reste 10 pt. Ce sont les marges et le nombre de niveaux qui se réduisent, pas la taille du texte.
- **Le pied de page est plus visible qu'en grand format** (il est près de la main) : folio et titre courant y sont naturels ; les notes de bas de page en 8 pt sur toute la largeur (85+ signes) sont, elles, à proscrire.
- **La piqûre à cheval de 24–32 pages s'ouvre presque à plat** : les traversées de gouttière (filet, image, titre en deux morceaux) sont possibles, avec la règle des imprimeurs : rien de fin ni de textuel *sur* le pli, une zone de 3 mm de chaque côté du pli sans détail, et les deux moitiés calées à la même hauteur exacte (guides des imprimeurs). Le creep (chasse) d'un 24 pages en 120 g est d'environ 0,7 mm au cahier central : négligeable, mais le folio et le fil de marge doivent rester à ≥ 6 mm de la coupe extérieure pour l'absorber.

### 6.2 Contraintes de la chaîne HTML/CSS → Chrome headless → PDF
- **Césures** : `hyphens:auto` avec `lang` correct est supporté par Chrome, mais l'impression headless en PDF ne les rend pas de façon fiable (bug Chromium 353304848, ouvert). Solutions : élargir la mesure pour ne pas dépendre des césures ; insérer `&shy;` à la main sur les mots longs des colonnes étroites ; ou utiliser Hyphenopoly. `text-wrap:pretty` (Chrome ≥ 117) évite les mots seuls en fin de paragraphe et `text-wrap:balance` équilibre titres et exergues, mais ni l'un ni l'autre ne remplace la relecture du drapeau.
- **Grille de base** : la déclarer explicitement (`line-height` en pt ou mm, jamais en valeur relative arrondie par le moteur), et exprimer tous les espacements verticaux dans la même unité (`--u`). Un `line-height:14pt` avec des marges de 4 mm ne s'aligne jamais ; `line-height:14.17pt` (= 5 mm) avec des marges en multiples de 5 mm s'aligne toujours.
- **Chiffres en dégradé (`background-clip:text`)** : Chrome les rastérise à l'export (image + masque), et le masque est perdu à la conversion CMJN : il ne reste qu'un rectangle de dégradé. En print, jamais de `background-clip:text` : glyphes en tracés (`14-print/lib/chiffre-svg.py`) rendus en PNG 600 dpi (`chiffres-png.sh`). À l'écran, ne jamais combiner un `letter-spacing` négatif sur un `inline-block` sans compenser par un `padding-right` équivalent : le dernier glyphe est tranché.
- **Polices variables** : vectoriser le texte à l'export (Ghostscript `-dNoOutputFonts`) évite les polices Type3 mal digérées par certains RIP ; en contrepartie plus aucune QA textuelle n'est possible sur le PDF final, il faut la faire sur le PDF « qa » (texte vivant).
- **Profil couleur** : convertir en CMYK avec le profil du papier réel (PSO Uncoated v3 / FOGRA52 pour du non couché) ou livrer selon la consigne de l'imprimeur ; convertir avec ISO Coated v2 sur du non couché donne une épreuve écran plus saturée que le tirage.
- **Fond perdu** : composer directement au format rogné + 3 mm (154 × 216 pour A5), avec une page HTML d'un pixel plus grande que le format de données, et laisser `14-print/lib/build.sh` rogner au montage (au centre, à l'échelle 1) pour éviter le liseré blanc des arrondis.
- **Contrôles automatiques** utiles et suffisants : format et nombre de pages, CMYK, absence de polices, corps minimal par span, texte hors zone de sécurité, dpi effectif des images, titres à point final, mot orphelin en fin de bloc. Ils ne voient ni les vides, ni les alignements de double page, ni la mesure : d'où la checklist du §7.

## 7. Checklist de relecture éditoriale d'une double page

À passer sur la double page ouverte à plat, imprimée à l'échelle 1 sur un papier proche du papier final. Chaque ligne se coche ou se corrige ; les renvois indiquent la règle.

### A. La double page comme unité
1. Un seul point d'entrée principal (titre, image ou chiffre) ; le regard sait par où commencer en moins d'une seconde.
2. Les deux pages partagent au moins deux lignes d'accroche (tête de zone, première ligne de texte, ligne de pied). Vérifier à la règle : premières lignes de texte des deux pages à la même hauteur ± 0,5 mm.
3. Le blanc est placé (tête, entre les blocs, autour du héros), pas subi (un vide de plus de 25 mm en pied de page qui ne « tient » rien = tassement).
4. Densité de la double page cohérente avec sa place dans le rythme (ouverture aérée, pages courantes denses, page de citation vide) ; comparer avec la double page précédente et la suivante sur le chemin de fer.
5. Rien d'important à moins de 5 mm de la coupe ni à moins de 8 mm du pli (piqûre à cheval : les 3 mm centraux disparaissent à la lecture).
6. Aucun élément (texte, médaillon, filet) ne touche un autre élément sans l'avoir décidé : chevauchements, texte qui traverse un filet, légende collée à une image.

### B. Grille et alignements
7. Toutes les colonnes de texte tombent sur la grille mère ; aucune largeur « à la main ».
8. Toutes les lignes de texte courant tombent sur la grille de base (interligne constant, hauteurs de blocs multiples de l'unité).
9. Les blocs en pied (cartes, exergues, légendes) sont calés sur la ligne de pied commune, pas posés « au plus bas ».
10. Une image qui casse la grille le fait franchement (fond perdu, ou dépassement ≥ 1 colonne) ; jamais de dépassement de 2–3 mm qui ressemble à une erreur.

### C. Typographie
11. Corps de texte suivi ≥ 9,5 pt (10 pt sur non couché), interligne 130–145 % ; légendes ≥ 8 pt ; rien sous 7 pt.
12. Mesure : 45–75 signes par ligne en colonne unique, 40–50 en multicolonne ; en dessous de 40, colonne trop étroite (drapeau troué) ; au-dessus de 80, ligne trop longue (retour à la ligne pénible).
13. Hiérarchie lisible en trois niveaux au plus par page (titre / intertitre ou chapô / corps), avec des sauts francs (rapport ≥ 1,25 entre niveaux adjacents, ≥ 2 entre titre et corps).
14. Pas de veuve (dernière ligne d'un paragraphe seule en tête de colonne), pas d'orpheline (première ligne seule en pied), pas de mot seul en dernière ligne de titre, chapô, exergue ou légende.
15. Drapeau propre : pas de « trou » (ligne courte entre deux longues), pas plus de trois lignes consécutives de longueur croissante ou décroissante ; césures autorisées, jamais plus de trois consécutives.
16. Lettrine : sur un nombre entier de lignes, sommet aligné sur la hauteur de capitale de la première ligne, pied sur la ligne de base de la dernière ligne couverte.
17. Exergue : ne répète pas une phrase visible à moins de 40 mm ; ne touche aucun filet ; sa taille est comprise entre le corps × 1,5 et le titre / 2.
18. Texte en couleur claire ou en défonce : ≥ 9 pt et graisse ≥ 600 ; contraste ≥ 4,5:1 pour tout texte sous 18 pt (ou sous 14 pt gras).
19. Capitales espacées seulement pour les surtitres et labels (≤ 3 mots), jamais un titre entier.
20. Ponctuation et micro-typo : guillemets de la langue, apostrophes courbes, espaces insécables devant les unités, pas de point final aux titres, chiffres alignés dans les colonnes horaires.

### D. Image, illustration, couleur
21. Une image par double page « domine » (la plus grande) ; les autres lui sont subordonnées d'au moins un rapport 2:1.
22. Fond perdu réel de 3 mm sur toute image qui touche la coupe ; rien de significatif (visage, texte dans l'image) à moins de 5 mm de la coupe.
23. Portraits d'une même grille : même cadrage, même style, même densité de trait.
24. Légende sous ou à côté de l'image, alignée sur sa marge, 8–9 pt, jamais centrée sous une image calée à gauche.
25. Couleur : la page fonctionne en niveaux de gris (imprimer un test N&B) ; aucun sens porté par la seule saturation d'une couleur de marque (souvent hors gamut CMJN, ternit sur non couché).
26. Filets ≥ 0,25 pt ; réglures destinées au stylo ≥ 0,3 pt et ≥ 40 % de noir.

### E. Constantes et navigation
27. Folio présent, à la même place et à la même taille sur toutes les pages (sauf pleine page image), et cohérent avec le sommaire.
28. Titre courant ou surtitre présent sur toute page courante qui n'a pas de titre, y compris la page de droite d'une double page dont le titre est à gauche.
29. Renvois internes exacts (« page 12 », « facing page », « back cover ») vérifiés sur la maquette imposée.
30. Éléments à compléter par le lecteur : réglures écrivables (épaisseur, gris), espace suffisant (≥ 8 mm par ligne d'écriture).

### F. Contrôle final
31. Imprimer la double page à l'échelle 1 sur papier proche du papier final ; lire à 35–40 cm ; regarder à 2 m ; retourner la page (test « à l'envers ») pour juger les masses.
32. Passer les contrôles automatiques (format, fond perdu, corps minimum, dpi, hors marge) ET une relecture humaine des noms propres, dates, heures.

## 8. Sources

Ouvrages et pages consultés en 2026 (recherche web + lecture). Les ouvrages sont cités à travers des extraits, résumés ou recensions en ligne quand le texte intégral n'est pas accessible.

### 8.1 Grilles, rythme, image, typographie
- Josef Müller-Brockmann, *Grid Systems in Graphic Design / Raster Systeme* (1981) — extraits, texte numérisé et notes de lecture.
- Timothy Samara, *Making and Breaking the Grid*.
- Ellen Lupton, *Thinking with Type* (grilles, hiérarchie, *hang line*).
- Beth Tondreau, *Layout Essentials* ; Kimberly Elam, *Grid Systems*.
- Mark Boulton, « Five simple steps to designing grid systems » ; Khoi Vinh, *Ordering Disorder*.
- Robert Bringhurst, *The Elements of Typographic Style* (§2.1.2 mesure, §2.2 grille de base « on beat and in phase », §2.3–2.4 paragraphes, césures, veuves) ; édition web : webtypography.net.
- Jan Tschichold, *The Form of the Book* (canon 2:3:4:6) ; Wikipedia « Canons of page construction » (Van de Graaf).
- Richard Hendel, *On Book Design* ; Craig Mod, « Let's talk about margins ».
- Matthew Butterick, *Practical Typography* (règles 2, 3, 4, 15, 17, 18 ; « Alternate figures ») : practicaltypography.com.
- Guides de maquette éditoriale et de grille de base de studios et de blogs de design (madegooddesigns, affinity.studio, bas-bg, Publitas, designer-daily, azuramagazine, InDesignSkills, flip180media).
- Chemin de fer et rythme : Kai Brach (Offscreen), « How to plan a magazine » ; magCulture (flatplan masterclass, magCulture Live) ; études d'oculométrie sur l'imprimé.
- Fin d'article : Fonts.com Fontology « End marks » ; Wikipedia « End mark ».
- Prépresse et reliure : prepressure.com ; preflight.art (hairline) ; fasteditor.com (épaisseurs et corps minimaux) ; guides de préparation des illustrations de presses universitaires ; guides de reliure, de piqûre à cheval et d'images à cheval d'imprimeurs ; creativepro.com (papier non couché).
- Chaîne HTML → PDF : caniuse « css-hyphens » ; ticket Chromium 353304848 (césures en impression headless) ; dépendance de la césure à la langue déclarée du document.
- Accessibilité : WCAG 2.2, critère 1.4.3 (contraste minimal).

### 8.2 Magazines contemporains
- Monocle : magCulture « Monocle redesigned » ; Design Observer ; Eye Magazine ; FontFeed (S. Coles, 2009).
- Kinfolk : magCulture (Kinfolk 18, entretien avec Alex Hunting) ; D&AD 2017 ; It's Nice That (refonte 2021).
- The Gentlewoman : Fonts In Use (n° 9) ; AIGA Eye on Design ; magCulture (n° 7, 12, 33).
- Delayed Gratification : magCulture (Rob Orchard ; « DG turns 15 » ; DG 39) ; slow-journalism.com (infographies de Christian Tate).
- Apartamento : Fonts In Use ; Klim Type Foundry ; Marklives (Omar Sosa) ; magCulture ; It's Nice That.
- Courrier international : Fonts In Use (S. Coles, 2010) ; Logo en vue.
- Offscreen : recension de la refonte n° 16 ; page « Production » du magazine.
- Works That Work : Fonts In Use (Kupferschmid, 2014) ; Stack.
- Real Review : It's Nice That (2016) ; BP&O (2017).
- Weapons of Reason : It's Nice That ; magCulture ; Stack.

### 8.3 Brochures, carnets d'événement, notes, programmes
- Guides d'événement : TEDGlobal 2013 program guide (Communication Arts) ; Square One SF conference guide, AIGA Design Conference, Brand New Conference (Fonts In Use).
- Guides de conception de livrets d'événement et de programmes de conférence ; Wikipedia « Program book ».
- Programmes et tableaux : CSS-Tricks « Building a conference schedule with CSS grid » ; Edward Tufte, *Envisioning Information* et « Graphical timetables » ; règles des filets dans les tableaux.
- Trombinoscopes : guides de mise en page des yearbooks (Jostens, Herff Jones, Studio Source).
- Carnets et réglures : Field Notes ; Wikipedia « Ruled paper » ; comparatifs de grilles de points (Well-Appointed Desk).
- Lettrines : cambric.pub « Drop caps » ; infogridpacific « Drop Cap Magic ».
