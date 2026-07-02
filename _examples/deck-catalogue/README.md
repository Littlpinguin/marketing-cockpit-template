# Deck-catalogue — bibliothèque de layouts de slides

`catalogue.html` est un deck HTML autonome de **20 slides, une par layout**. Il sert à deux choses :

1. **Bibliothèque de référence pour la skill `slides`** : quand la skill construit un deck, elle pioche ici le layout adapté à chaque type de contenu (voir le tableau ci-dessous), puis le rhabille aux couleurs de la marque du projet (`01-brand/style-guide.md` + `tokens.css`).
2. **Démo publique du template** : tout est fictif, le fichier peut être ouvert, projeté ou hébergé sans aucune précaution.

Chaque slide est à la fois **l'exemple exécuté et sa propre légende** : le cartouche en bas à droite donne le nom du layout et le cas d'usage. Le cartouche est un `<aside class="legend">` — il ne fait pas partie du layout et ne doit **pas** être recopié dans un deck de production.

## Ouvrir le catalogue

```bash
# Option 1 : double-clic sur catalogue.html (aucune dépendance)
# Option 2 : serveur local
cd _examples/deck-catalogue && python3 -m http.server 8000
# puis http://localhost:8000/catalogue.html
```

Navigation : `←`/`→`/`Espace`, molette, swipe tactile, drag sur la barre de progression, `O` = vue d'ensemble, chiffres + `Entrée` = saut direct, `P` = export PDF (rastérisation automatique des textes en dégradé).

## Marque fictive

- **Entreprise** : « Meridian Conseil », cabinet de conseil en stratégie climat. N'existe pas.
- **Personnes, chiffres, tarifs, TJM, URL** : tous inventés. L'URL utilise le TLD réservé `.example`.
- **Palette du catalogue** (neutre-élégante, propre au catalogue, à remplacer en production) : vert profond `#2f6f5e`, vert clair `#4da585`, sauge `#9ec3ae`, laiton `#c8a24b`, encre `#1c2420`, blanc cassé `#fcfbf8`, dégradé signature vert → laiton.
- **Typographies** : Fraunces (display) + Inter (texte), via Google Fonts avec fallback système. Aucune image externe : logo en SVG inline, « captures » en maquettes 100 % CSS, portraits en avatars-initiales.

## Les 20 layouts

| # | Layout | Quand l'utiliser |
|---|--------|------------------|
| 01 | Couverture | Ouvrir le deck : une promesse, un mot en dégradé, fond sombre |
| 02 | Sommaire | Annoncer le déroulé en 3-5 temps maximum |
| 03 | Intercalaire de chapitre | Marquer une rupture dans le récit, un mot-chapitre géant |
| 04 | Cartes (2 à 4) | Décomposer une idée en facettes équivalentes |
| 05 | Bandeau KPI | Aligner 3-4 chiffres de même rang |
| 06 | Dot-grid | Rendre une proportion tangible (X sur 100), mieux qu'un camembert |
| 07 | Chiffre-choc | Un seul chiffre mérite toute la slide |
| 08 | Slide-silence | Respiration toutes les 5-6 slides : une affirmation, c'est tout |
| 09 | Citation | Conviction ou témoignage en texte XXL |
| 10 | Pipeline | Séquence de 3-4 étapes ou lots avec connecteurs |
| 11 | Framework lettré | Méthode propriétaire en acronyme, lettres géantes |
| 12 | Quadrant | Arbitrer 4-6 options sur deux axes, zone prioritaire teintée |
| 13 | Tableau comparatif A/B | Lever une confusion entre deux notions |
| 14 | Figure cliquable + versus | Montrer un produit : maquette CSS + tableau nous/l'existant |
| 15 | Avant / après | Vendre une transformation, panneaux en miroir |
| 16 | Offres comparées | 2-3 scénarios tarifés, le recommandé badgé |
| 17 | Tableau de coûts | Chiffrage détaillé, périmètre retenu surligné |
| 18 | Timeline | Calendrier de 4-6 jalons, le jalon critique marqué « Cible » |
| 19 | Équipe / portraits | Présenter 4-6 intervenants |
| 20 | CTA finale | Clore sur une décision, miroir de la couverture |

## Comment la skill `slides` s'en sert

1. La skill découpe le brief en idées (« 1 idée = 1 slide ») et associe à chaque idée un **type de contenu** (chiffre unique, comparaison, séquence, calendrier…).
2. Pour chaque type, elle ouvre `catalogue.html`, repère la slide correspondante (commentaires `<!-- NN NOM -->` dans le HTML) et **copie la structure** (`<section class="plate">` + composant).
3. Elle remplace la palette et les fonts par celles de la marque (variables CSS en tête de fichier : `--vert`, `--or`, `--grad`, `--font-display`…), retire le cartouche `.legend`, et injecte le vrai contenu.
4. L'invariant technique (frame 1920×1080 scalé, chrome, nav-rail, overview, export PDF avec rastérisation) se reprend tel quel — il est autonome et déjà éprouvé.

Règles héritées des decks sources : aucun tiret cadratin, aucun point final sur les titres, 3-4 slides de respiration par tranche de 20, dégradé réservé aux mots d'impact, aucun contenu sous y = 1000 px (zone du chrome bas).

## Régénérer ou étendre le catalogue

- **Ajouter un layout** : dupliquer une `<section class="plate">`, ajouter le composant dans le bloc CSS des composants, renseigner `data-meta="Layout NN · Nom"` et le cartouche `.legend`. La numérotation des folios et la vue d'ensemble se mettent à jour automatiquement (JS).
- **Contraintes bloquantes** : données 100 % fictives, aucun nom de client réel, aucune capture d'écran réelle, aucun asset externe (tout inline ou généré en CSS ; seule exception tolérée : Google Fonts, avec fallback).
- **Vérification anonymisation** avant tout commit : un grep insensible à la casse des noms de clients réels du studio sur `catalogue.html` doit rendre zéro occurrence.
- **QA visuelle** : ouvrir dans Chrome, parcourir les 20 slides, tester `O`, le drag-bar et l'export `P` ; vérifier qu'aucun contenu ne chevauche le chrome bas.
