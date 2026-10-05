# Landing « <nom de l'offre> »

> Spec validée le <AAAA-MM-JJ> par <nom>. Page : `05-web-content/landing-pages/<slug>/index.html`. Brief : `05-web-content/briefs/<slug>.md`.
> Ce fichier vit dans `05-web-content/landing-pages/<slug>/pilotage/spec.md`. Il est figé pendant chaque étape de construction.

## 1. Cadre

| Point | Décision | Source |
|---|---|---|
| Audience | persona(s) de `01-brand/personas.md`, niveau de conscience | réponse du <date> |
| Accès | public indexé / lien direct en `noindex` | |
| URL prévue | `<domaine>/<chemin>` | |
| Objectif unique | | |
| Action de conversion | réservation / rendez-vous / formulaire / achat / téléchargement / appel, vers <outil et URL ou endpoint> | |
| Circuit de vente | qui inscrit, qui facture, qui encaisse, qui confirme | |
| Chiffres affichés | places, prix (HT / TTC), dates, remises | document de l'offre |
| Échéance | date et heure exactes, fuseau | |
| Langues | langue principale ; adaptations éventuelles | `.setup-completed` |
| Source de trafic | canaux et messages d'origine (message match) | |
| Preuves disponibles | personnes (accord pour le portrait), documents, chiffres sourcés, témoignages signés | |
| Visuels | bibliothèque réutilisée / génération (coût) | |
| Mesure | GA4 actif ou non ; événements prévus | `.setup-completed` |

## 2. Direction visuelle : « <nom de l'objet signature> »

L'objet fort du hero et la façon dont il revient dans la page. Le plan de jetons (palette en valeurs de `tokens.json`, rôles typographiques, élément signature) et son auto-critique (`01-brand/design-anti-generique.md` § 3). Les directions écartées, et pourquoi.

## 3. Le récit

| # | Section (`id`) | Objection du visiteur | Mécanique (`references/sections.md`) | Moment orchestré | Fond |
|---|---|---|---|---|---|
| 1 | Hero (`hero`) | de quoi s'agit-il, pour qui, combien, jusqu'à quand | | | fond de page |
| 2 | | pourquoi maintenant | | | |
| … | | | | | |
| n | CTA final (`final`) | je passe à l'action | | | bande sombre |

Épinglages : 3 au plus, jamais deux d'affilée sans respiration, environ 7 écrans captifs au total.

## 4. Comportements et données

- **Configuration de l'offre** (en tête du script du socle) : état (ouverte, liste d'attente, close), dates, prix, places, URL de conversion.
- **Porte de choix** éventuelle : formules, liens profonds, événement de mesure au choix.
- **Échéance** : le HTML montre l'état ouvert, le navigateur calcule l'état réel.
- **Mesure** : événements (`cta_click` avec `cta_position`, `generate_lead`, autres étapes du tunnel) et leurs paramètres.
- **CTA primaire** : `data-cta="primaire"` sur <élément>.

## 5. Textes définitifs, clé par clé

Une sous-section par section, avec un tableau `clé | texte` (une colonne par langue si la page est déclinée).
- Titres sans virgule ni point, sans mot seul en fin de ligne.
- Aucun tiret cadratin ; vocabulaire de `01-brand/voice.md` ; liste bannie de `01-brand/anti-ai-writing-style.md`.
- Espaces insécables en français.
- Textes alternatifs des visuels, avec la mention IA prévue par `01-brand/divulgation-ia.md`.
- Chaque chiffre avec sa source (`messaging-framework.md` ou référence citée).

## 6. Mouvement

Le moment orchestré de chaque section, les transitions de jonction (fondu inversé, dérive, rideau) et le comportement en mouvement réduit.

## 7. Bloc de conversion

Ce que comprend le prix, la remise (et ce qui se passe si on l'oublie), les étapes après le clic, les prérequis, les conditions (seuil de confirmation, rétractation), l'état après clôture.

## 8. Points ouverts

Formulés dans les mots de l'humain : ce que voit le visiteur, pourquoi ça compte, l'option recommandée.

## 9. Vérification

`qa-landing.py` (zéro erreur, avertissements assumés), quatre revues et vague de corrections, `a11y-auditor`, `lint-brand.py`, `brand-check`, UTM et événements, contrôle en ligne après publication.

## 10. Hors périmètre

Ce qui ne sera pas fait dans ce chantier (écritures dans les outils de vente, emails, diffusion, publicité…).
