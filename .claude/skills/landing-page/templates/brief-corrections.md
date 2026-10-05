# Lot de corrections : landing « <nom> »

> Écrit par le contrôleur dans `05-web-content/landing-pages/<slug>/pilotage/fix-wave-brief.md`, après lecture des quatre revues et de la QA. Règles d'arbitrage : `.claude/skills/landing-page/references/revues.md`.

## Sources à lire

- `pilotage/qa.json` (sortie de `qa-landing.py --format json`)
- `pilotage/review-design.md`
- `pilotage/review-brand.md` (synthèse du contrôleur : à corriger d'office / gardé / à trancher)
- `pilotage/review-cro.md`
- `pilotage/review-a11y.md`
- `pilotage/page-charter.md`

## Répartition des fichiers (stricte)

- **Agent A** : uniquement `pilotage/sections/<01…04>-*.html` (+ `assets/<ids>/`).
- **Agent B** : uniquement `pilotage/sections/<05…08>-*.html` (+ `assets/<ids>/`).
- **Contrôleur** : le socle (`index.html` hors marqueurs : jetons, CSS commun, moteur d'apparition, relais de mesure, configuration) et toute section partagée avec d'autres pages.
- **Les deux agents** : relire un fichier juste avant de l'éditer, ne pas commiter, ne pas écrire dans `index.html`. Un besoin dans le socle se nomme dans le rapport.

## Arbitrages du contrôleur (ils priment sur les rapports)

1. **<Sujet>** : <décision exacte, avec ses valeurs ou ses textes>.
2. …

**Ce qui ne change pas**, même si une revue le signale : <mots et choix de l'humain, avec la raison>.

**Aucun chiffre inventé** : <compteurs et données qui restent vides>.

**Avertissements QA assumés** : <type de constat, cible, raison>.

## Agent A

- <points, avec leur référence au rapport source : D-P1-3, A11Y-7, CRO-H2, QA `contraste`…>

## Agent B

- <points, avec leur référence au rapport source>

## Contrôleur (socle)

- <points que le contrôleur applique lui-même>

## Vérification (chaque agent)

- Assemblage d'une copie dans le scratchpad, puis `qa-landing.py` : aucune erreur qui vienne de tes fragments.
- `grep` des couleurs en dur : vide sur tes fragments.
- `lint-brand.py` sur tes fragments : sans erreur.

## Rapport

`pilotage/reports/fix-a.md` ou `fix-b.md` : chaque point traité avec sa référence au rapport source, les points écartés et pourquoi, les modifications demandées dans le socle.
