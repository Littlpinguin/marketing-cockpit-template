# Registre du moteur de slides vendorisé depuis slides-agent

Le moteur de présentations HTML de ce template (starter, composants, catalogue de layouts, QA Playwright, export PDF, et leurs tests) a une **source de vérité unique** : le dépôt public [slides-agent](https://github.com/Littlpinguin/slides-agent). Le template en garde une copie vendorisée, pour qu'un fork fonctionne seul, sans dépendance.

Contrairement aux skills des autres registres (`docs/vendored-*.md`), qui sont des adaptations réécrites à la main, le moteur de slides est un **miroir mécanique** : un seul script l'écrit, `scripts/sync-slides-engine.py`, à partir d'une table explicite et d'adaptations purement mécaniques, toutes listées ici. **Un fichier vendorisé ne s'édite jamais à la main** : chacun porte un en-tête `VENDORED from slides-agent` qui le rappelle, `python3 scripts/sync-slides-engine.py --check` détecte toute retouche, et la prochaine synchronisation l'écraserait.

## Source

<!-- slides-engine-sync:start -->
- Source : <https://github.com/Littlpinguin/slides-agent>, commit `653763f3cd76f6e835d4994774e461b5561bbd75` (2026-10-05)
- Fichiers vendorisés : 60 (18 textes adaptés, 42 copies brutes)
<!-- slides-engine-sync:end -->

Le bloc ci-dessus est réécrit par le script à chaque synchronisation.

- **Licence** : MIT des deux côtés, même auteur ([Jessy Martin](https://jessem.fr), compte GitHub Littlpinguin). Les deux dépôts ont fait évoluer le moteur en parallèle ; slides-agent a repris tout ce que seul le template avait (vue d'ensemble groupée, plein écran, compositions de production), l'a unifié et étendu (QA à planchers mesurables, rastériseur PDF par caractère, 120 layouts), et il est devenu la référence unique : le template le reprend désormais tel quel.
- **Photos du catalogue** : photographies [Pexels](https://www.pexels.com/license/), libres d'usage et de modification ; chaque fichier a sa fiche `.json` (photographe, lien, licence) et la planche 113 du catalogue les crédite. Elles illustrent la famille « Photographie » du catalogue, rien d'autre.
- **Polices** : le starter charge Inter et JetBrains Mono, le catalogue Fraunces et Inter, depuis Google Fonts (licence OFL).

## Table de correspondance

| Source (slides-agent) | Cible (template) | Traitement |
|---|---|---|
| `templates/base.html` | `06-graphic-design/presentations/templates/base.html` | texte adapté ; en-tête avec une note pour les decks copiés |
| `templates/components.md` | `06-graphic-design/presentations/templates/components.md` | texte adapté |
| `scripts/qa.py` | `06-graphic-design/presentations/scripts/qa.py` | texte adapté |
| `scripts/export_pdf.py` | `06-graphic-design/presentations/scripts/export_pdf.py` | texte adapté |
| `scripts/export-pdf.sh` | `06-graphic-design/presentations/scripts/export-pdf.sh` | texte adapté |
| `scripts/serve.sh` | `06-graphic-design/presentations/scripts/serve.sh` | texte adapté + `serve-racine` |
| `scripts/shots.py` | `06-graphic-design/presentations/scripts/shots.py` | texte adapté |
| `scripts/pexels.py` | `06-graphic-design/presentations/scripts/pexels.py` | texte adapté + `pexels-racine`, `pexels-photos`, `pexels-tokens` |
| `docs/engine-parity.md` | `06-graphic-design/presentations/docs/engine-parity.md` | texte adapté |
| `docs/pdf-export.md` | `06-graphic-design/presentations/docs/pdf-export.md` | texte adapté |
| `docs/design-system.md` | `06-graphic-design/presentations/docs/design-system.md` | texte adapté |
| `docs/pexels-setup.md` | `06-graphic-design/presentations/docs/pexels-setup.md` | texte adapté |
| `reference/catalogue-layouts.html` | `_examples/deck-catalogue/catalogue.html` | texte adapté (le catalogue garde son chemin historique, les liens existants tiennent) |
| `reference/LAYOUTS.md` | `_examples/deck-catalogue/LAYOUTS.md` | texte adapté |
| `reference/photos/*.jpg` | `_examples/deck-catalogue/photos/` | copie brute (le catalogue les cite en `photos/…`, chemin relatif inchangé) |
| `reference/photos/*.json` | `_examples/deck-catalogue/photos/` | copie brute (fiches de crédit) |
| `tests/test_qa.py` | `scripts/tests/test_slides_qa.py` | texte adapté + `tests-racine` ; remplace l'ancien `test_qa_slides.py` |
| `tests/test_print.py` | `scripts/tests/test_slides_print.py` | texte adapté + `tests-racine` |
| `tests/test_engine.py` | `scripts/tests/test_slides_engine.py` | texte adapté + `tests-racine` |
| `tests/test_pexels.py` | `scripts/tests/test_slides_pexels.py` | texte adapté + `tests-racine-pathlib`, `tests-pexels-deps` |

Un fichier que la source ne produit plus (une photo retirée en amont) est supprimé de la cible par la synchronisation. Un fichier de slides-agent ni mappé ni écarté est signalé à chaque passage, pour être rangé dans l'une des deux listes en connaissance de cause.

## Adaptations mécaniques

Le script applique, dans cet ordre : les adaptations propres au fichier (sur le texte amont), les réécritures de chemins, puis l'en-tête. Rien d'autre ne change.

### Réécritures de chemins

Appliquées à tous les fichiers texte, en **une seule passe** : un chemin réécrit ne l'est jamais deux fois. Une borne à gauche empêche de toucher un chemin déjà préfixé (`01-brand/tokens.json` reste tel quel, et `../assets/photos/…`, relatif à un deck, aussi).

| Id | Dans slides-agent | Dans le template |
|---|---|---|
| `catalogue` | `reference/catalogue-layouts.html` | `_examples/deck-catalogue/catalogue.html` |
| `index-layouts` | `reference/LAYOUTS.md` | `_examples/deck-catalogue/LAYOUTS.md` |
| `photos-catalogue` | `reference/photos/` | `_examples/deck-catalogue/photos/` |
| `nom-catalogue` | `catalogue-layouts.html` (nom seul) | `catalogue.html` |
| `starter` | `templates/base.html`, `templates/components.md`, `templates/components/` | `06-graphic-design/presentations/templates/…` |
| `scripts` | `scripts/qa.py`, `export_pdf.py`, `export-pdf.sh`, `serve.sh`, `shots.py`, `pexels.py` | `06-graphic-design/presentations/scripts/…` |
| `docs` | `docs/engine-parity.md`, `pdf-export.md`, `design-system.md`, `pexels-setup.md`, `hosting.md` | `06-graphic-design/presentations/docs/…` |
| `tests` | `tests/test_qa.py`, `test_print.py`, `test_engine.py`, `test_pexels.py` | `scripts/tests/test_slides_….py` |
| `pytest` | `pytest tests` | `pytest scripts/tests` (lancé depuis la racine) |
| `tokens` | `brand/tokens.css` | `06-graphic-design/presentations/tokens.css` (voir « Pont des tokens ») |
| `decks` | `presentations/` (aussi dans les URL du serveur local) | `06-graphic-design/presentations/decks/` |
| `photos-decks` | `assets/photos/` | `06-graphic-design/presentations/assets/photos/` |
| `skill-images` | la skill `generate-image` | la skill `image-generation` |

Toutes les commandes vendorisées se lancent donc **depuis la racine du dépôt** : `python3 06-graphic-design/presentations/scripts/qa.py 06-graphic-design/presentations/decks/<deck>.html`.

### Adaptations propres à un fichier

Substitutions littérales, ancrées sur le texte amont. Chacune doit trouver ce texte exactement une fois : si slides-agent l'a changé, la synchronisation s'arrête (code 1, id de l'adaptation dans le message) au lieu de copier un fichier mal adapté.

| Id | Fichier | Avant → après | Pourquoi |
|---|---|---|---|
| `serve-racine` | `serve.sh` | `$(dirname "$0")/..` → `$(dirname "$0")/../../..` | le serveur local sert la racine du dépôt, pour qu'un deck atteigne `01-brand/assets/` en relatif ; les decks s'ouvrent sur `http://localhost:5173/06-graphic-design/presentations/decks/` |
| `pexels-racine` | `pexels.py` | `ROOT = …parent.parent` → `ROOT = …parents[3]` | `.env` et `.cache/` vivent à la racine du dépôt, trois niveaux au-dessus du script |
| `pexels-photos` | `pexels.py` | `ROOT / "assets" / "photos"` → `ROOT / "06-graphic-design" / "presentations" / "assets" / "photos"` | les photos téléchargées vont dans les assets des decks, que `../assets/photos/` atteint depuis `decks/` : les extraits de `components.md` restent justes sans réécriture |
| `pexels-tokens` | `pexels.py` | `ROOT / "brand" / "tokens.css"` → `ROOT / "06-graphic-design" / "presentations" / "tokens.css"` | les traitements `mono` / `duotone` lisent les couleurs dans le fichier de marque du moteur |
| `tests-racine` | `test_slides_qa.py`, `test_slides_print.py`, `test_slides_engine.py` | `ROOT = Path(__file__)…parent.parent` → `…parents[2] / "06-graphic-design" / "presentations"` | `ROOT` désigne le dossier du moteur, qui reproduit l'arborescence de slides-agent (`templates/`, `scripts/`) |
| `tests-racine-pathlib` | `test_slides_pexels.py` | même chose, écrite avec `pathlib` | idem |
| `tests-pexels-deps` | `test_slides_pexels.py` | `from PIL import Image` → `pytest.importorskip(…)` | `requests` et Pillow restent optionnels : sans eux, les tests Pexels sont sautés au lieu de casser la collecte |

### En-tête et copies brutes

Chaque fichier texte reçoit un en-tête `VENDORED from slides-agent` (commentaire `#` après le shebang d'un script, commentaire HTML après le `<!DOCTYPE html>` d'une page, en tête d'un Markdown). Celui du starter ajoute que **le deck copié appartient au projet** : `new-deck.py` retire l'en-tête de la copie. Les photos et leurs fiches `.json` sont copiées octet pour octet, sans en-tête.

Les mentions de `CLAUDE.md`, de l'« onboarding » et de la skill `pexels-photos` dans les fichiers vendorisés désignent ceux de slides-agent. Leurs équivalents ici : la skill `slides`, `/brand-discover`, et la procédure Pexels de la skill `slides` (avec `06-graphic-design/presentations/docs/pexels-setup.md`).

## Pont des tokens

slides-agent garde sa marque dans `brand/tokens.css`, collé dans le `:root` de chaque deck. Le template garde la sienne dans `01-brand/tokens.json` (format DTCG, source unique). Le pont :

1. `scripts/build-tokens.py` génère, entre les marqueurs `brand-tokens` de `06-graphic-design/presentations/tokens.css`, **toutes les variables de marque du moteur avec les noms de slides-agent** : `--brand-primary`, `--brand-secondary`, `--brand-neutral-light` / `-dark`, leurs dérivées `-deep` / `-soft`, `--rule`, `--rule-light`, `--brand-gradient` (et `-vertical`), `--font-display`, `--font-mono`, `--label-accent`, `--label-accent-dark`. La cible et les formules sont déclarées dans `scripts/build-tokens.toml`.
2. Les dérivées suivent les formules de slides-agent (`color-mix` en sRGB : `-deep` = 12 % de noir, `-soft` = 12 % d'alpha, etc.), **écrites en valeurs littérales** : la QA lit les couleurs calculées et ne sait pas lire le `color(srgb …)` d'un `color-mix()`. Les accents d'étiquettes sont poussés par pas de 1 % jusqu'au contraste WCAG de 4,5:1 sur leurs fonds (options `mix` / `amount` / `min_contrast` / `against` de `build-tokens.py`) : une primaire claire est assombrie d'office pour les surtitres.
3. Le reste du `:root` de `tokens.css` (mouvements, rayons, opacités du chrome `--chrome-opacity`, hooks de motif `--brand-pattern`… à `none` par défaut) est écrit à la main, avec les mêmes noms que slides-agent. Le second `:root` (échelle `--carousel-*` des carrousels) est propre au template.
4. Avant le wizard, le bloc porte la **palette d'exemple neutre** de `docs/placeholders.json` (`#1E40AF`, `#F59E0B`, `#0F172A`, `#F8FAFC`, Inter et JetBrains Mono), identique aux valeurs par défaut du starter de slides-agent. Deux tests le garantissent (`test_build_tokens.py`).
5. `python3 06-graphic-design/scripts/new-deck.py <slug>` crée un deck : copie du starter, dont le premier `:root` est remplacé par celui de `tokens.css`. Le starter vendorisé n'est donc jamais retouché par le wizard.
6. `scripts/lint-brand.py` n'applique pas la règle `off-palette` dans un bloc `brand-tokens` : ses nuances sont dérivées de la palette par construction, et `build-tokens.py --check` en garantit la fidélité.

## Ce qui n'est pas vendorisé

| Fichier de slides-agent | Raison |
|---|---|
| `CLAUDE.md` | playbook du produit slides-agent (onboarding, boucle de génération) ; sa doctrine est reprise dans la skill `slides` et `06-graphic-design/CLAUDE.md` |
| `README.md`, `CHANGELOG.md`, `LICENSE` | documents du dépôt slides-agent ; l'historique du moteur se lit dans son CHANGELOG |
| `.gitignore`, `.env.example` | le template a les siens (`.cache/` et `PEXELS_API_KEY` y sont repris) |
| `.claude/*` | skills propres à slides-agent (`create-slides`, `generate-image`, `pexels-photos`) ; le template a `slides` et `image-generation` |
| `brand/*` | `brand/tokens.css` est remplacé par le pont des tokens ; `brand/guidelines.md` par la doctrine de `01-brand/` |
| `assets/*` | les assets du template vivent dans `01-brand/assets/` (catalogue `index.md`) ; les photos propres aux decks dans `06-graphic-design/presentations/assets/photos/` |
| `presentations/*` | decks et exemples de slides-agent ; ceux du template vivent dans `06-graphic-design/presentations/decks/` |
| `scripts/README.md` | index des scripts de slides-agent, qui cite `gen-image.py` ; les scripts sont documentés ici, dans la skill `slides` et dans `06-graphic-design/CLAUDE.md` |
| `scripts/gen-image.py` | le template a sa propre chaîne d'images (skill `image-generation`, `06-graphic-design/scripts/genmeta.py`) |
| `docs/hosting.md` | le template garde son `06-graphic-design/presentations/docs/hosting.md`, adapté à son arborescence (decks + `01-brand/assets/`) |

Restent propres au template, hors moteur : les compositions et l'échelle des carrousels (`06-graphic-design/compositions-carrousel.md`, `--carousel-*`), la QA des visuels (`06-graphic-design/scripts/qa-visuel.py`, `qa_common.py` et leurs tests), `new-deck.py`, `tokens.css`, `hosting.md` et le `README.md` du catalogue.

## Pexels, en option

`pexels.py` (recherche, planche contact, téléchargement, traitement de marque, slide de crédits) est vendorisé mais **optionnel** : il ne sert que si `PEXELS_API_KEY` est posée dans le `.env` de la racine (clé gratuite, procédure pas à pas dans `06-graphic-design/presentations/docs/pexels-setup.md`) et demande `python3 -m pip install requests pillow`. Sans clé, rien ne change : les decks utilisent les assets de la marque. La skill `slides` encadre son usage : un lieu, une matière, un objet ou un geste réels, jamais une photo de stock générique (visuels bannis de `01-brand/style-guide.md`), les assets de `01-brand/assets/` d'abord, droits consignés dans `01-brand/droits.md`, slide de crédits obligatoire.

## Tests

- Vendorisés : `scripts/tests/test_slides_qa.py`, `test_slides_print.py`, `test_slides_engine.py`, `test_slides_pexels.py` (les tests qui pilotent Chromium sont sautés proprement sans Playwright ; les tests Pexels sans `requests` ni Pillow).
- Propres au template : `test_sync_slides_engine.py` (le script, sur une arborescence fictive, et ce registre, qui doit documenter toute la table), `test_new_deck.py` (le pont, dont un deck aux couleurs d'une marque fictive qui doit passer la QA), `test_build_tokens.py` (dérivées et palette d'exemple).

```bash
python3 -m pytest scripts/tests -q
```

## Procédure de re-synchronisation

**Règle de parité** : toute évolution du moteur se fait **dans slides-agent d'abord** (starter, catalogue, QA, docs, tests, et sa table `docs/engine-parity.md`), puis se reprend ici par le script. Jamais l'inverse.

1. **Mettre à jour le checkout** de slides-agent et s'assurer qu'il est commité (le script signale une copie de travail modifiée et le consigne dans ce registre).
2. **Synchroniser** depuis la racine du template :
   ```bash
   python3 scripts/sync-slides-engine.py --source ../slides-agent   # ou SLIDES_AGENT_DIR=…, ou ../slides-agent par défaut
   ```
3. **Lire la sortie** : une adaptation qui ne s'applique plus arrête tout (mettre à jour `ADAPTATIONS` dans le script et la table ci-dessus) ; un fichier amont ni vendorisé ni écarté est signalé (le mapper dans `COPIES` ou l'écarter dans `ECARTES`, et le dire ici).
4. **Vérifier** :
   ```bash
   python3 scripts/sync-slides-engine.py --check
   python3 06-graphic-design/presentations/scripts/qa.py 06-graphic-design/presentations/templates/base.html
   python3 06-graphic-design/presentations/scripts/qa.py _examples/deck-catalogue/catalogue.html --no-engine-check
   python3 -m pytest scripts/tests -q
   python3 scripts/update-readme-counts.py      # nombre de layouts du catalogue
   ```
5. **Consigner** dans `CHANGELOG.md` ce qui change pour les utilisateurs du template, et commiter la synchronisation seule, avec le commit source dans le message.
