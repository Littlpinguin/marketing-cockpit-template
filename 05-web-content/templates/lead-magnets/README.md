# Galerie — templates d'outils interactifs (lead magnets)

10 outils HTML/JS vanilla single-file avec **capture d'email intégrée**, conformes à la skill `lead-magnet` : l'utilisateur obtient d'abord un aperçu de son résultat (donner avant de capturer), l'email débloque le détail complet. Les formats interactifs convertissent à 30-50 % contre 3-10 % pour un PDF statique (moyennes du marché 2025) — et leurs réponses **segmentent le nurturing**.

Chaque fichier contient :

- le bloc de tokens de marque de `../../sections-library.md` — avec les **valeurs de démo « Meridian Conseil »** (vert profond `#2f6f5e`, laiton `#c8a24b`, Fraunces + Inter en fallback système, aucune ressource externe chargée) et le mapping vers les tokens `{{BRAND_*}}` en commentaire : chaque outil ouvert tel quel dans un navigateur est une **démo finie**, et le wizard `/start-copilot` (ou la skill `lead-magnet`) remplace ces valeurs par celles de `01-brand/style-guide.md` ;
- une **direction artistique par outil** (colonne « Ambiance » ci-dessous) déclinée du langage Meridian : display serif, hairlines, grain discret, motif signature de méridiens en SVG inline, curseurs et cases customisés aux couleurs de marque ;
- une **logique JS fonctionnelle** dont les données/formules sont des **placeholders commentés** (`── PLACEHOLDER ──`) à remplacer par vos vraies hypothèses ;
- un **gate de capture** (`bindGate`) branché sur `{{FORM_ENDPOINT}}` : POST du formulaire (email + champs cachés de segmentation) vers n8n/outil emailing, événement `generate_lead`, déblocage du résultat complet. Endpoint non configuré → déblocage local en mode démo (console) ;
- des contenus d'exemple fictifs (« Meridian Conseil ») à réécrire via `copywriting`.

**Rappel skill `lead-magnet`** : un outil sans circuit complet est un lead perdu — page de capture (voir `../landing-pages/lead-magnet.html`), automatisation, séquence de nurturing (une branche par profil/segment), mesure.

## Choisir son modèle

| Modèle | Cas d'usage | Ambiance de démo (Meridian) | Ce qu'il faut personnaliser |
|---|---|---|---|
| `calculateur-roi.html` | Chiffrer un coût caché ou un gain — leads « en mode projet », très qualifiés | **Outil clair** — curseurs verts cerclés laiton, résultat en carte sombre aux méridiens, chiffre serif géant | Les 3 curseurs d'entrée, les constantes de calcul (`QUALITY_RATE`, `INTERNAL_SAVING`…), les 4 leviers du rapport |
| `diagnostic-score.html` | Auto-audit noté /100 avec profils — segmentation forte du nurturing | **Audit sérieux** — questions en hairlines numérotées, score dans un anneau SVG animé sur carte sombre | Les 10 questions et leurs 3 catégories, les seuils des 3 profils (`PROFILES`), les recommandations par profil |
| `quiz-positionnement.html` | Quiz de personnalité pro (1 question/écran + progression) — viralité et segmentation | **Crème chaleureux** — pastilles A/B/C, compteur serif italique, profil filigrané d'un globe méridien | Les 6 questions, les 4 profils (nom, description, pistes), le mapping réponse → profil |
| `comparateur-scenarios.html` | Aider à arbitrer entre 2-3 stratégies (statu quo / internaliser / accompagner) | **Arbitrage clair** — 3 colonnes hiérarchisées, scénario recommandé liseré vert, verdict en bandeau sombre | Les scénarios, les formules de coût/délai/risque, les libellés de verdict |
| `grader.html` | « Notez votre X » de A à E — audit express d'un actif existant | **Examen sombre** — full dark, note serif géante laiton clair, gate en îlot crème contrasté | Les 8 critères et leurs pondérations (`data-w`), les seuils et commentaires des notes (`GRADES`) |
| `checklist-interactive.html` | Checklist de projet avec progression sauvegardée (localStorage) — nurturing long | **Atelier clair** — phases 01-04 serif italique, barre de progression sticky en dégradé vert→laiton | Les 4 phases et 20 points, la clé `STORAGE_KEY`, le livrable PDF envoyé par email |
| `generateur-brief.html` | Générer un document utile (brief, plan, cahier des charges) copiable | **Papier à en-tête** — brief rendu comme une feuille blanche à en-tête méridien et corps serif | Les 6 champs du formulaire, le gabarit `buildBrief()`, la version enrichie promise par email |
| `estimateur-budget.html` | Fourchette budgétaire en direct — **qualifie le budget du lead** | **Chiffrage tinté** — postes en cartes crème, fourchette min–max serif laiton sur carte sombre | Les postes et fourchettes (`data-min`/`data-max`), le facteur multi-sites, les explications de fourchette |
| `simulateur-avant-apres.html` | Projection avant/après à 12 mois selon le niveau d'investissement (format original) | **Bascule** — colonne « avant » crème désaturée face à la colonne « après » vert profond, flèche SVG | Les 3 indicateurs, les 4 niveaux (`LEVELS` : projections, verdicts, prérequis) |
| `mini-benchmark.html` | Position vs médianes sectorielles (format original) — ⚠ les médianes fournies sont **fictives** : les remplacer par des données réelles sourcées (`_sources/reports/`) avant mise en ligne | **Données claires** — barres comparatives hairline, médiane en losange laiton, verdicts en pilules | Les 4 métriques, les secteurs et médianes (`SECTORS`), les verdicts par nombre d'indicateurs devant |

## Conventions de capture (tous les modèles)

- **Aperçu d'abord** : le score/chiffre principal est visible sans email ; le détail (décomposition, recommandations, rapport) est derrière le gate.
- **Champs cachés de segmentation** : `lead_magnet` (slug) + la donnée clé (`score`, `profil`, `budget_min/max`, `niveau`…) partent avec l'email → tags et branches de nurturing dans l'outil emailing.
- **RGPD** : finalité annoncée sous le bouton, lien `{{URL_CONFIDENTIALITE}}`, désinscription en un clic. Opt-in distinct si la séquence dépasse la livraison ({{LEGAL_OPTIN_POLICY}}).
- **Bouton en bénéfice** (« Recevoir mon rapport détaillé »), jamais « Envoyer ».
- **Tracking** : `generate_lead` émis au submit si GA4 est chargé (snippet gtag à insérer avec `{{GA4_MEASUREMENT_ID}}`, voir skill `landing-page`).

## Workflow d'utilisation

1. Copier le modèle vers `05-web-content/lead-magnets/outils-web/<slug>/index.html`.
2. Faire valider la logique (entrées, formules, restitution) **avant** de personnaliser le code — skill `lead-magnet`, étape 2.
3. Remplacer tokens, données placeholder, contenus fictifs ; tout chiffre publié vient du messaging framework ou de `_sources/reports/`.
4. Brancher le circuit complet : `{{FORM_ENDPOINT}}` → n8n → outil emailing → séquence (une branche par profil).
5. QA (375/600/900/1280 px, logique testée), brand-check, puis `deployed.md`.
