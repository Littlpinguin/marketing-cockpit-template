# Parité de moteur — liste canonique des features du système de slides

Ce document est la **référence unique** de ce que « le moteur complet » veut dire
pour toute présentation HTML produite dans ce repo. Il existe parce qu'un écart
s'est déjà produit (starter sans plein écran alors que le catalogue l'avait) et
qu'il ne doit pas se reproduire.

## La règle de parité (non négociable)

> **Toute évolution du moteur se porte dans TOUS les artefacts** :
> le starter (`templates/base.html`), le deck-catalogue
> (`_examples/deck-catalogue/catalogue.html`) et les decks en cours dans
> `decks/` — **et cette liste se met à jour** dans le même commit.

Un deck ne « choisit » pas ses features de moteur : il embarque tout. Le
contenu varie, le moteur non. `scripts/qa.py` vérifie mécaniquement la présence
des marqueurs du moteur (voir tableau) et **échoue** si un deck ou le starter
n'a pas le moteur complet.

## Les features canoniques du moteur

| # | Feature | Détail | Marqueur qa.py |
|---|---------|--------|----------------|
| 1 | **Frame 1920×1080 scalée responsive** | `fit()` : `transform: translate(-50%, calc(-50% + yShift)) scale(s)`, réserve de nav en mode fenêtré, cap 1.5× | (structurel) |
| 2 | **Chrome haut/bas + folios auto-numérotés** | Les folios `NN / TOTAL` sont injectés par JS depuis `SLIDE_COUNT` (= nombre de slides). Jamais de folio codé en dur ; insertion/suppression de slide = zéro renumérotation | `SLIDE_COUNT` |
| 3 | **Navigation triple** | Clavier (`←`/`→`/Espace/Page↑↓/Home/End) + molette debouncée 700 ms + swipe tactile + drag-bar de progression + quick-jump (chiffres + `Entrée`) | (structurel) |
| 4 | **Overview groupée par familles** | Touche `O` / bouton ⊞, vignettes groupées par `data-family` (ouverture, editorial, dataviz, schema, tableau, preuve, conclusion), clic hors panneau = fermeture, touches de navigation bloquées panneau ouvert | `overview` |
| 5 | **Mode plein écran** | Touche `F` / bouton ⛶ (Fullscreen API + fallback `webkit`) → `body.presenting` : nav masquée, `fit()` sans réserve ni cap | `body.presenting`, `requestFullscreen` |
| 6 | **nav-peek** | En mode `presenting`, la nav réapparaît quand le pointeur passe à moins de 90 px du bas de l'écran | `nav-peek` |
| 7 | **Export PDF** | Touche `P` / bouton PDF : `body.printing-pdf`, rastérisation canvas des textes en dégradé (`GRADIENT_TEXT_SELECTORS`), `window.print()`, restauration sur `afterprint`. CSS print : 1 slide = 1 page 1920×1080 | `printing-pdf`, `window.print` |
| 8 | **Hooks de pattern de marque** | `--brand-pattern` / `--brand-pattern-light` / `--corner-motif` (+ `--pattern-opacity`, `--pattern-opacity-dark`, `--corner-opacity`) dans le `:root`, consommés par `.motif` / `.texture` / `.corner` / `.filet-orn` | `--brand-pattern` |
| 9 | **Fix des descendantes** | `line-height ≥ 1.1` sur tous les titres texte ; sur le texte en dégradé (`background-clip: text`), compensation `padding: .22em .08em; margin: -.22em -.08em; overflow: visible` — ne jamais la réduire | (revue visuelle QA) |

## Vérification mécanique

```bash
cd 06-graphic-design/presentations
python scripts/qa.py decks/<deck>.html        # parité moteur + overflow + safe-zone + typo, police, contraste, folios
python scripts/qa.py ../../_examples/deck-catalogue/catalogue.html   # le catalogue aussi
```

La constante `ENGINE_MARKERS` de `scripts/qa.py` est le **miroir exécutable**
du tableau ci-dessus. Si tu ajoutes une feature au moteur :

1. Porter la feature dans `templates/base.html` **et**
   `_examples/deck-catalogue/catalogue.html` **et** les decks en cours.
2. Ajouter sa ligne au tableau ci-dessus.
3. Ajouter son marqueur à `ENGINE_MARKERS` dans `scripts/qa.py`.
4. Re-passer `qa.py` sur tous les artefacts.

Un deck hérité qui n'a pas encore le moteur complet peut passer en
`--no-engine-check` **temporairement**, mais la mise à niveau doit être
planifiée : ce flag n'est pas un régime permanent.

## D'où vient le moteur de référence

Le moteur QA-é vit dans `_examples/deck-catalogue/catalogue.html` (52 layouts)
et dans le starter `templates/base.html` (4 slides d'exemple, placeholders
`{{...}}`). Les deux sont à parité. Pour un nouveau deck : copier le starter,
y coller le `tokens.css` rempli, et piocher les layouts dans le catalogue —
le moteur vient d'office avec.
