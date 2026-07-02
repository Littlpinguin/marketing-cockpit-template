# Deck-catalogue — bibliothèque de layouts de slides

`catalogue.html` est un deck HTML autonome de **52 slides, une par layout**, organisées en **7 familles**. Il sert à deux choses :

1. **Bibliothèque de référence pour la skill `slides`** : quand la skill construit un deck, elle pioche ici le layout adapté à chaque message (voir les tableaux ci-dessous), puis le rhabille aux couleurs de la marque du projet (`01-brand/style-guide.md` + `tokens.css`).
2. **Démo publique du template** : tout est fictif, le fichier peut être ouvert, projeté ou hébergé sans aucune précaution.

Chaque slide est à la fois **l'exemple exécuté et sa propre légende** : le cartouche en bas à droite donne le nom du layout et le cas d'usage. Le cartouche est un `<aside class="legend">` — il ne fait pas partie du layout et ne doit **pas** être recopié dans un deck de production.

## Ouvrir le catalogue

```bash
# Option 1 : double-clic sur catalogue.html (aucune dépendance)
# Option 2 : serveur local
cd _examples/deck-catalogue && python3 -m http.server 8000
# puis http://localhost:8000/catalogue.html
```

Navigation : `←`/`→`/`Espace`, molette, swipe tactile, drag sur la barre de progression, `O` = vue d'ensemble **groupée par familles**, chiffres + `Entrée` = saut direct, `P` = export PDF (rastérisation automatique des textes en dégradé), `F` = **mode plein écran**.

### Mode plein écran (touche F)

La touche `F` (ou le bouton ⛶ de la barre) bascule en plein écran immersif : la slide occupe tout l'écran, la barre de navigation disparaît (`body.presenting`) et **réapparaît quand la souris frôle le bas de l'écran** (`nav-peek`, 90 derniers pixels). Les layouts bord à bord (21, 22, 23) sont conçus pour ce mode : aucun chrome, visuel pleine surface.

## Marque fictive

- **Entreprise** : « Meridian Conseil », cabinet de conseil en stratégie climat. N'existe pas.
- **Personnes, chiffres, tarifs, TJM, URL, logos clients** : tous inventés. L'URL utilise le TLD réservé `.example`. Les « logos » du layout 50 sont des marques imaginaires composées en CSS.
- **Palette du catalogue** (neutre-élégante, propre au catalogue, à remplacer en production) : vert profond `#2f6f5e`, vert clair `#4da585`, sauge `#9ec3ae`, laiton `#c8a24b`, laiton texte `#9a7c30` (contraste sur fond clair), encre `#1c2420`, blanc cassé `#fcfbf8`, dégradé signature vert → laiton.
- **Typographies** : Fraunces (display) + Inter (texte), via Google Fonts avec fallback système. Aucune image externe : logo en SVG inline, « captures » en maquettes 100 % CSS, « photos » en scènes CSS (dégradés + motifs), graphiques en CSS/SVG inline, portraits en avatars-initiales.
- **Lisibilité projecteur** : aucune taille de police sous 18 px à l'échelle 1920×1080, contrastes vérifiés (AA), cartouche `.legend` sans chevauchement — QA Playwright automatisée.
- **Descendantes de titres** : line-height ≥ 1.1 sur tous les niveaux de titres texte. Le span `.grad` (texte en dégradé via `background-clip:text`) ne peint que dans sa boîte : la compensation `padding:.22em .08em; margin:-.22em -.08em` est obligatoire, sinon le bas des g / j / p / q est coupé. Ne pas la réduire.

## Vie graphique de la marque — hooks pattern & angles

Le catalogue embarque un **pattern graphique de marque** (démo : lignes de méridiens/topographie Meridian, SVG inline en data-uri, aucun asset externe) décliné sur les slides pour donner de la vie sans jamais concurrencer le contenu. Trois hooks CSS dans le `:root`, à redéfinir avec le motif de la marque du projet :

| Hook | Rôle | Démo Meridian |
|---|---|---|
| `--brand-pattern` | Filigrane pour fonds clairs/teintés (tracé encre) | Lignes de méridiens, 960×540 |
| `--brand-pattern-light` | Même filigrane pour fonds sombres (tracé blanc cassé) | idem |
| `--corner-motif` | Motif d'angle des slides éditoriales | Arcs concentriques + point laiton, 240×240 |

Les opacités sont pilotées par `--pattern-opacity` (.05, fonds clairs), `--pattern-opacity-dark` (.07, fonds sombres) et `--corner-opacity` (.09).

### Déclinaisons (classes à poser sur la `<section class="plate">`)

| Classe | Effet | Utilisée sur |
|---|---|---|
| `.motif` | Filigrane pleine slide (`--brand-pattern-light`) | Fonds sombres de rythme : 01 couverture, 03 intercalaire, 07 chiffre-choc, 08 silence, 20 CTA |
| `.texture` | Filigrane pleine slide (`--brand-pattern`), opacité plus faible | Fonds teintés : 11 framework, 28 citation + portrait, 41 pyramide, 51 carte |
| `.corner` | Arcs de méridiens dans l'angle haut-droit | Slides éditoriales : 04, 15, 24, 25, 26, 27, 29 |
| `.filet-orn` | Filet typographique portant le logo-mark (élément, pas classe de slide) | 08 silence, 09 citation |

Règles : une slide ne cumule **jamais** `.motif` / `.texture` / `.corner` (un seul `::before` disponible) ; le filigrane reste en `z-index:0`, sous l'aurora, le grain, le contenu, le chrome et le cartouche ; le motif d'angle est en encre — il ne se pose que sur fonds clairs/teintés. Le résultat produit la **variété de fonds attendue entre familles** (clair, teinté, sombre, texturé) tout en restant cohérent : c'est le même motif partout, seuls la couleur du tracé et le dosage changent.

En production : remplacer les data-uri par le motif réel de la marque (recensé dans `01-brand/assets/index.md`), jamais un pattern décoratif générique — voir la section « Vie graphique de la marque » de la skill `slides`.

## Les 52 layouts, par famille

Le message à porter choisit le layout — comparaison, évolution, répartition, flux, hiérarchie (méthode chart-chooser).

### Ouverture & rythme (7)

| # | Layout | Message servi |
|---|--------|---------------|
| 01 | Couverture | Ouvrir le deck : une promesse, un mot en dégradé, fond sombre |
| 02 | Sommaire | Annoncer le déroulé en 3-5 temps maximum |
| 03 | Intercalaire de chapitre | Marquer une rupture dans le récit, un mot-chapitre géant |
| 07 | Chiffre-choc | Un seul chiffre mérite toute la slide |
| 08 | Slide-silence | Respiration toutes les 5-6 slides : une affirmation, c'est tout |
| 09 | Citation XXL | Conviction ou témoignage en texte géant sur fond sombre |
| 21 | Plein fond + voile | Poser une ambiance : visuel CSS bord à bord, voile, texte en bas (mode F) |

### Éditorial & narration (9)

| # | Layout | Message servi |
|---|--------|---------------|
| 04 | Cartes (2 à 4) | Décomposer une idée en facettes équivalentes |
| 15 | Avant / après | Vendre une transformation, panneaux en miroir |
| 22 | Split 50/50, visuel gauche | Alternance image/texte, moitié visuelle bord à bord |
| 23 | Split 50/50, visuel droite | Miroir du 22 pour créer le rythme gauche-droite |
| 24 | Problème vers solution | Formuler la bascule proposée, deux panneaux et une flèche |
| 25 | Pour / contre | Peser une alternative honnêtement, puis donner sa position |
| 26 | FAQ / objections | Désamorcer 4 objections avant qu'elles ne soient posées |
| 27 | Checklist de décision | Auto-diagnostic : acquis cochés, restes à préparer |
| 29 | Définition | Imposer un mot précis, style entrée de dictionnaire |

### Data-visualisation (12)

| # | Layout | Message servi |
|---|--------|---------------|
| 05 | Bandeau KPI | Aligner 3-4 chiffres de même rang |
| 06 | Dot-grid | Rendre une proportion tangible (X sur 100), mieux qu'un camembert |
| 30 | Barres verticales | Comparer 4-6 catégories, une seule accentuée |
| 31 | Barres horizontales | Classer des éléments aux libellés longs, toujours trié |
| 32 | Courbe / aire (SVG) | Montrer une évolution dans le temps, cible en pointillés |
| 33 | Slope chart (SVG) | Comparer deux dates : la pente raconte l'histoire |
| 34 | Donut (SVG) | Composition à 3-4 parts maximum, total au centre |
| 35 | Waterfall | Décomposer un écart entre deux totaux, marche par marche |
| 36 | Heatmap | Croiser deux dimensions, faire ressortir les concentrations |
| 37 | Jauges / bullet | Progression vers des objectifs : réalisé vs cible |
| 38 | Entonnoir | Déperdition par étape, taux entre les niveaux |
| 39 | Grille de chiffres | Panorama factuel dense : 6 chiffres en grille filaire |

### Schémas & processus (12)

| # | Layout | Message servi |
|---|--------|---------------|
| 10 | Pipeline | Séquence de 3-4 étapes ou lots avec connecteurs |
| 11 | Framework lettré | Méthode propriétaire en acronyme, lettres géantes |
| 12 | Quadrant | Arbitrer 4-6 options sur deux axes, zone prioritaire teintée |
| 18 | Timeline horizontale | Calendrier de 4-6 jalons, le jalon critique marqué « Cible » |
| 40 | Cycle | Processus récurrent en 4 temps autour d'un centre |
| 41 | Pyramide | Hiérarchiser des prérequis, la base est le message |
| 42 | Orbites / écosystème | Cartographier des acteurs par proximité du centre de décision |
| 43 | Chronologie verticale | Historique en 4-5 jalons alternés, le présent en bas |
| 44 | Organigramme | Gouvernance ou structure : 2 niveaux, 3 branches max |
| 45 | Process zigzag | Séquence de 5-6 étapes en serpentin lisible |
| 46 | Roadmap trimestres | Synchroniser plusieurs chantiers : couloirs × trimestres |
| 47 | Kanban | Point d'avancement honnête : fait / en cours / à lancer |

### Tableaux & offres (6)

| # | Layout | Message servi |
|---|--------|---------------|
| 13 | Tableau comparatif A/B | Lever une confusion entre deux notions |
| 14 | Figure cliquable + versus | Montrer un produit : maquette CSS + tableau nous/l'existant |
| 16 | Offres comparées (2) | 2 scénarios tarifés, le recommandé badgé |
| 17 | Tableau de coûts | Chiffrage détaillé, périmètre retenu surligné |
| 48 | Trois offres comparées | 3 niveaux d'engagement, traits ✓ en miroir |
| 49 | Matrice de responsabilités | Verrouiller qui décide et qui produit (pastilles R/A/C/I) |

### Preuve & confiance (4)

| # | Layout | Message servi |
|---|--------|---------------|
| 19 | Équipe / portraits | Présenter 4-6 intervenants |
| 28 | Citation + portrait | Faire porter la preuve par un tiers, avatar + verbatim daté |
| 50 | Mosaïque de logos | Prouver par les références, grille filaire monochrome |
| 51 | Carte de couverture | Maillage territorial : carte stylisée SVG, pins, stats |

### Conclusion (2)

| # | Layout | Message servi |
|---|--------|---------------|
| 52 | Récapitulatif | Trois messages à retenir, juste avant la CTA |
| 20 | CTA finale | Clore sur une décision, miroir de la couverture |

## Comment la skill `slides` s'en sert

1. La skill découpe le brief en idées (« 1 idée = 1 slide ») et associe à chaque idée un **type de message** (chiffre unique, comparaison, évolution, répartition, séquence, calendrier, preuve…).
2. Pour chaque type, elle ouvre `catalogue.html`, repère la slide correspondante (commentaires `<!-- NN NOM -->` dans le HTML, attribut `data-family`) et **copie la structure** (`<section class="plate">` + composant).
3. Elle remplace la palette et les fonts par celles de la marque (variables CSS en tête de fichier : `--vert`, `--or`, `--or-text`, `--grad`, `--font-display`…), redéfinit les hooks de pattern (`--brand-pattern`, `--brand-pattern-light`, `--corner-motif`) avec le motif de la marque, retire le cartouche `.legend`, et injecte le vrai contenu.
4. L'invariant technique (frame 1920×1080 scalé, chrome, nav-rail, overview groupée, mode plein écran `F`, export PDF avec rastérisation) se reprend tel quel — il est autonome et déjà éprouvé.

Règles héritées des decks sources : aucun tiret cadratin, aucun point final sur les titres, 3-4 slides de respiration par tranche de 20, dégradé réservé aux mots d'impact, aucune police sous 18 px à l'échelle 1920×1080, aucun contenu dans la zone du cartouche (bas-droite) ni sous y = 1000 px (chrome bas).

## Régénérer ou étendre le catalogue

- **Ajouter un layout** : dupliquer une `<section class="plate">`, ajouter le composant dans le bloc CSS des composants, renseigner `data-meta="Layout NN · Nom"`, `data-family` (ouverture, editorial, dataviz, schema, tableau, preuve, conclusion) et le cartouche `.legend`. La numérotation des folios et la vue d'ensemble groupée se mettent à jour automatiquement (JS).
- **Attention à la règle CSS** `.plate > *:not(...)` : elle force `position:relative` sur les enfants directs des slides ; tout nouvel enfant direct qui doit rester en `position:absolute` (plein fond, splits) doit être ajouté à la liste d'exclusions.
- **Pattern de marque** : pour décliner le filigrane ou l'angle sur une nouvelle slide, poser `.motif`, `.texture` ou `.corner` (une seule des trois) — voir la section « Vie graphique de la marque » ci-dessus. Re-passer la QA après : le filigrane ne doit jamais gêner la lecture du chrome ni du contenu.
- **Contraintes bloquantes** : données 100 % fictives, aucun nom de client réel, aucune capture d'écran réelle, aucun asset externe (tout inline ou généré en CSS/SVG ; seule exception tolérée : Google Fonts, avec fallback). Police ≥ 18 px, contraste AA (utiliser `--or-text` plutôt que `--or` pour du texte doré sur fond clair).
- **Vérification anonymisation** avant tout commit : un grep insensible à la casse des noms de clients réels du studio sur `catalogue.html` et ce README doit rendre zéro occurrence.
- **QA visuelle** : ouvrir dans Chrome, parcourir les 52 slides, tester `O`, `F`, le drag-bar et l'export `P` ; vérifier qu'aucun contenu ne chevauche le cartouche ni le chrome bas (script Playwright : overflow, chevauchements legend, tailles ≥ 18 px, contraste, navigation).
