---
name: new-landing
description: Produire une landing page de conversion (offre, formation, événement, campagne, liste d'attente, capture) avec le playbook de la skill landing-page, de la doctrine et du cadrage jusqu'à la livraison d'un HTML statique dans 05-web-content/landing-pages/<slug>/, avec QA mesurable (qa-landing.py), quatre revues parallèles et une vague de corrections arbitrée.
---

# /new-landing : lancer une landing page

Charger la skill [`landing-page`](../skills/landing-page/SKILL.md) et la suivre depuis la **phase 0**. Elle porte la méthode, la charte de page, le catalogue des mécaniques de section, les briefs d'agents et les portes de revue.

Arguments éventuels : `$ARGUMENTS` (sujet de la landing, documents source, échéance).

Si `.setup-completed` n'existe pas, s'arrêter et proposer `/start-cockpit` : sans doctrine de marque, une landing se produirait de mémoire.

## Premier tour

1. Lancer `landing-researcher` en arrière-plan avec ce qu'on sait déjà de l'offre et de l'audience.
2. Lire la doctrine (`01-brand/`) et la matière réelle (document de l'offre, chiffres, assets, pages existantes).
3. Choisir entre gabarit de données (galerie `05-web-content/templates/landing-pages/`) et page sur mesure, et le dire.
4. Poser les questions de cadrage de la phase 1, **toutes en une salve**, chacune avec l'option recommandée en premier.

## Règles rappelées ici, parce que ce sont elles qui coûtent le plus quand on les oublie

- Rien ne s'écrit avant le cadrage, et la spec (textes définitifs compris) se fait valider avant la construction.
- Le hero se construit et se montre en premier.
- Chaque agent reçoit la charte de page (`pilotage/page-charter.md`) et possède ses propres fichiers ; seul le contrôleur assemble `index.html` et commite.
- `python3 05-web-content/scripts/qa-landing.py <index.html>` sans erreur avant toute revue finale et avant toute livraison.
- Aucun chiffre, témoignage, logo ni compteur inventé ; urgence en jours, jamais en secondes.
- Commit, push et publication seulement sur go explicite de l'humain, publication par dry-run.
