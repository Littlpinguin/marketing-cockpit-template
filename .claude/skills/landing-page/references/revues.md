# Les quatre revues et leur arbitrage

## Mesurer d'abord

Avant toute revue, le contrôleur assemble la page et lance la QA :

```bash
python3 05-web-content/scripts/qa-landing.py 05-web-content/landing-pages/<slug>/index.html \
  --format json > 05-web-content/landing-pages/<slug>/pilotage/qa.json
```

Les relecteurs partent de ce fichier : ce que le script mesure (débordement, planchers, contraste, titres, alternatives, noms, champs, cibles tactiles, CTA et pli mobile, mouvement réduit, suivi) ne se recalcule pas à la main, il se commente et se priorise.

## Lancer

Les quatre relecteurs partent ensemble, dans un seul message, en lecture seule, une fois la page construite et montrée à l'humain :

| Agent | Grille | Modèle conseillé |
|---|---|---|
| `landing-reviewer-design` | En-têtes, rythme, matières, typographie, mouvement, responsive, boutons, code mort | le plus capable disponible |
| `landing-reviewer-brand` | Voix et anti-style-IA, ton, visuel contre `tokens.json`, preuve, audience, divulgation IA et droits | standard |
| `landing-reviewer-cro` | Récit et objections, porte de choix, CTA, bloc de conversion, urgence, preuve, mesure | le plus capable disponible |
| `landing-reviewer-a11y` | WCAG 2.2 AA en 14 points, à partir de la QA mesurée | standard |

Chaque prompt donne :
- le chemin de la page (`05-web-content/landing-pages/<slug>/index.html`) et de ses fragments ;
- le chemin de la charte de page et de la spec ;
- le chemin de `pilotage/qa.json` ;
- le fichier de rapport attendu, `pilotage/review-<grille>.md`.

Les revues lisent le code et la QA. Elles voient mal le rendu d'ensemble : un en-tête collé, un fond qui masque la matière, un épinglage qui ne se bloque pas, une page qui « fait template ». Les captures et l'œil de l'humain restent la dernière porte.

## Arbitrer

Le contrôleur lit les quatre rapports et écrit `pilotage/fix-wave-brief.md` à partir de `templates/brief-corrections.md`. Ses arbitrages priment sur les rapports :

1. **L'humain d'abord.** Ses décisions (charte § 9) priment sur toute recommandation. Ses mots, et ceux de son document source, se gardent même quand une revue les signale ; ils sont listés comme tels.
2. **Aucun chiffre inventé** pour combler une recommandation : un compteur sans vrai chiffre reste vide, un témoignage absent reste absent.
3. **Une structure, une valeur.** Quand deux revues proposent deux réglages, on en choisit un et on l'écrit avec sa valeur exacte (taille, rayon, durée, longueur de piste, couleur de jeton).
4. **Socle et sections partagées** : corrigés par le contrôleur lui-même, à l'identique pour toutes les pages qui les utilisent.
5. **Décisions business ou légales** (encaissement, remise, consentements, mentions, conditions) : regroupées et posées à l'humain en une fois, à la fin, dans ses mots.
6. **Revue de marque**, triée en trois listes : à corriger d'office, mots de l'humain gardés, décisions à lui poser.
7. **QA** : toute erreur de `qa.json` se corrige ; un avertissement se corrige ou s'assume par écrit dans le brief, avec sa raison.

## Corriger

- **Deux agents** `landing-section-builder` en parallèle, sur des fichiers disjoints : par exemple, l'un prend les fragments des sections 1 à 4, l'autre ceux des sections 5 à 8. Le socle reste au contrôleur.
- Si une correction exige une modification du socle (jeton, moteur, relais de mesure), l'agent la nomme dans son rapport ; le contrôleur l'applique.
- **Rapports** : chacun écrit `pilotage/reports/fix-<lot>.md`, point par point, avec la référence au rapport source (`D-P1-3`, `A11Y-7`, type de constat QA), les points écartés et pourquoi.
- **Constats tardifs et retours de l'humain pendant la vague** : ils partent aux deux agents par `SendMessage`, avec la mention « ils priment sur le brief ».
- **Clôture** : le contrôleur assemble, relance la QA jusqu'à zéro erreur, commite sur go, puis montre la page.
