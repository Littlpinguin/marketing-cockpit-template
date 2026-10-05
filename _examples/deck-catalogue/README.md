# Deck-catalogue : bibliothèque de layouts de slides

`catalogue.html` est un deck HTML autonome de **120 planches, une par layout**, réparties en **8 familles**. Il sert à deux choses :

1. **Bibliothèque de référence pour la skill `slides`** : pour chaque temps du récit, la skill choisit un layout dans l'index `LAYOUTS.md` (colonne « reach for it when »), le regarde exécuté ici, puis le reconstruit aux couleurs de la marque du projet (`06-graphic-design/presentations/tokens.css`, généré depuis `01-brand/tokens.json`).
2. **Démo publique du template** : tout est fictif, le fichier peut être ouvert, projeté ou hébergé sans aucune précaution.

Chaque planche est à la fois **l'exemple exécuté et sa propre légende** : le cartouche en bas à droite donne le nom du layout et le cas d'usage. Le cartouche est un `<aside class="legend">` : il ne fait pas partie du layout et ne se recopie **pas** dans un deck de production.

## Vendorisé depuis slides-agent

`catalogue.html`, `LAYOUTS.md` et `photos/` viennent de [slides-agent](https://github.com/Littlpinguin/slides-agent), la source de vérité du moteur de slides, et sont écrits par `python3 scripts/sync-slides-engine.py` : **ne pas les éditer ici**. Un nouveau layout s'ajoute dans slides-agent (procédure en bas de `LAYOUTS.md`), puis se reprend par synchronisation. Ce README, lui, est propre au template. Registre complet : `docs/vendored-slides.md`.

## Ouvrir le catalogue

```bash
# Option 1 : double-clic sur catalogue.html (aucune dépendance)
# Option 2 : serveur local, depuis la racine du dépôt
./06-graphic-design/presentations/scripts/serve.sh
# puis http://localhost:5173/_examples/deck-catalogue/catalogue.html
```

Navigation : `←`/`→`/`Espace`, molette, swipe tactile, drag sur la barre de progression, `O` = vue d'ensemble **groupée par familles**, chiffres + `Entrée` = saut direct, `P` = export PDF (rastérisation des textes en dégradé), `F` = **mode plein écran** (la barre de navigation disparaît et réapparaît quand la souris frôle le bas de l'écran).

## Les 120 layouts

L'index complet, famille par famille, avec pour chaque layout ce qu'il fait et quand le choisir, est **`LAYOUTS.md`** (en anglais) : c'est par lui qu'on commence, jamais en faisant défiler le deck. Répartition des planches dans la vue d'ensemble (`data-family`) :

| Famille | Clé | Planches |
|---|---|---|
| Ouverture & rythme | `ouverture` | 11 |
| Éditorial & narration | `editorial` | 15 |
| Data-visualisation | `dataviz` | 18 |
| Schémas & processus | `schema` | 24 |
| Tableaux & offres | `tableau` | 12 |
| Preuve & produit | `preuve` | 24 |
| Conclusion | `conclusion` | 7 |
| Photographie | `photo` | 9 |

Les planches 114 à 120 sont des compositions observées dans des decks de production de ce template (édito, cartouche encadré, KPI avec tendance, légende des repères, nuage de pastilles, mur de communauté, clôture avec QR) ; leur code prêt à coller est dans `06-graphic-design/presentations/templates/components.md`.

**Règle de variété** : jamais deux fois de suite le même layout, jamais plus de deux fois dans un deck. Un deck qui enchaîne huit layouts différents se lit comme écrit ; un deck qui répète des grilles de cartes se lit comme généré.

## Marque fictive

- **Entreprise** : « Meridian Conseil », cabinet de conseil en stratégie climat. N'existe pas.
- **Personnes, chiffres, tarifs, TJM, URL, logos clients** : tous inventés. L'URL utilise le TLD réservé `.example`.
- **Palette du catalogue** (propre au catalogue, à ne pas reprendre en production) : vert profond `#2f6f5e`, vert clair `#4da585`, sauge `#9ec3ae`, laiton `#c8a24b`, laiton texte `#806728` (contraste AA sur fond clair), encre `#1c2420`, blanc cassé `#fcfbf8`, dégradé signature vert → laiton.
- **Typographies** : Fraunces (display), Inter (texte) et une pile monospace système pour les étiquettes, via Google Fonts avec repli système.
- **Images** : logo en SVG inline, « captures » en maquettes CSS (placeholder `.shotph`), portraits en avatars-initiales. Seule la famille « Photographie » (planches 105 à 113) utilise de vraies photos : des photographies Pexels rangées dans `photos/`, chacune avec sa fiche de crédit `.json` (photographe, lien, licence), et créditées sur la planche 113.
- **Lisibilité projecteur** : contenu ≥ 18 px, étiquettes ≥ 12 px à l'échelle 1920×1080, contrastes AA, cartouche sans chevauchement : les 120 planches passent la QA des decks.

## Vie graphique de la marque : hooks pattern

Le catalogue embarque un **pattern de marque** de démonstration (lignes de méridiens en SVG inline) décliné par les classes `.motif` (fonds sombres), `.texture` (fonds clairs), `.corner` (angle des slides éditoriales) et `.filet-orn` (filet typographique), pilotées par les variables `--brand-pattern`, `--brand-pattern-light`, `--corner-motif` et leurs opacités. Le starter et `tokens.css` portent les mêmes hooks, **inertes** (`none`) tant que la marque n'a pas de motif réel validé : jamais de motif décoratif générique en production. Documentation : section « Brand pattern hooks » de `06-graphic-design/presentations/templates/components.md`.

## Comment la skill `slides` s'en sert

1. Elle découpe le brief en temps du récit (« 1 idée = 1 slide ») et associe à chaque temps un layout de `LAYOUTS.md`.
2. Elle ouvre `catalogue.html`, repère la planche (attribut `data-family`, cartouche, commentaires du HTML) et en reprend **la géométrie**, jamais le contenu ni l'enchaînement : le catalogue n'a pas d'arc narratif, c'est ce qui le rend sûr à lire.
3. Elle reconstruit le layout dans un deck créé par `06-graphic-design/scripts/new-deck.py` : variables de la marque (`--brand-*`, `--font-*`, `--label-accent`) à la place de celles du catalogue (`--vert`, `--or`, `--or-text`, `--grad`…), cartouche `.legend` retiré, vrai contenu.
4. Le moteur (cadre 1920×1080 scalé, chrome, navigation, vue d'ensemble, plein écran, export PDF) vient du starter, déjà complet.

## QA du catalogue

```bash
python3 06-graphic-design/presentations/scripts/qa.py _examples/deck-catalogue/catalogue.html --no-engine-check
```

Le catalogue est un livre de spécimens, pas un deck complet (pas de hooks d'impression headless) : d'où `--no-engine-check`. Ses `.plate` et ses folios `.tag-folio` sont détectés d'office, son cartouche `.legend` n'est pas audité. Attendu : 0 erreur sur les 120 planches (des avertissements `tight-body` restent, lisibles). Dans un fork configuré, `01-brand/tokens.json` déclare les polices de la marque, pas celles du catalogue : ajouter `--font Fraunces --font Inter`. Un layout repris du catalogue doit, lui, passer la QA dans le deck.
