---
name: landing-page
description: Playbook de production d'une landing page de conversion pour {{COMPANY_NAME}}, du cadrage à la livraison d'un HTML statique dans 05-web-content/landing-pages/. Méthode en huit phases (doctrine et matière réelle, cadrage en une salve, directions, spec, charte commune posée avant le travail parallèle, construction en parallèle par fichiers disjoints, montrer et appliquer les retours, quatre revues parallèles puis une vague de corrections arbitrée, livraison), six agents dédiés (landing-researcher, landing-section-builder, landing-reviewer-design / -brand / -cro / -a11y) et une QA mesurable (05-web-content/scripts/qa-landing.py). Orchestre cro-page, copywriting, design-direction, design-system, design-review, accessibility-web et brand-check. Utiliser dès que l'utilisateur demande une landing page, une page de vente, une page de capture, une page d'inscription à un événement, une page d'offre ou de campagne, ou la refonte d'une page de conversion. Commande d'entrée : /new-landing.
---

# landing-page : produire une landing page de haut niveau pour {{COMPANY_NAME}}

Une landing réussie se lit comme un seul récit, section par section, et amène son visiteur à une seule action. Ce playbook donne la méthode et le système qui y mènent : il ne donne ni un ordre de sections à recopier ni une apparence. Chaque landing a sa propre direction, sinon toutes les pages finissent pareilles.

**La barre.** Une page faite de cartes blanches empilées qui respecte le plan et passe ses tests reste refusée. Ce qu'on vise : des visuels de marque, un hero construit autour d'un objet fort, un ou deux moments de mise en scène au défilement, une alternance de sections claires et de bandes sombres, et partout de la preuve concrète.

## Contenu du skill

| Fichier | Rôle |
|---|---|
| `references/charte.md` | Modèle de charte de page, copié au démarrage dans `pilotage/page-charter.md` et donné à **chaque** agent : grille, en-têtes, matières, mouvement, interdits, conversion, technique, décisions de l'humain (§ 9, qui prime) |
| `references/sections.md` | Catalogue des mécaniques de section éprouvées : objection servie, quand, pourquoi, anti-modèles, mouvement réduit |
| `references/pieges.md` | Pièges techniques, de session et de marque, avec leur parade, plus les règles tirées des retours d'arbitrage |
| `references/inspiration.md` | Méthode de recherche : benchmark de pages qui convertissent, galeries publiques, filtre de marque |
| `references/revues.md` | Lancer les quatre revues et arbitrer leurs rapports |
| `templates/spec.md` | Squelette de spec de landing |
| `templates/brief-section.md` | Brief d'un agent de section |
| `templates/brief-corrections.md` | Brief d'arbitrage et de vague de corrections |

## Agents (`.claude/agents/`)

| Agent | Phase | Rôle |
|---|---|---|
| `landing-researcher` | 0, en arrière-plan | Benchmark de pages qui convertissent et recherche visuelle, consolidés dans `pilotage/research-notes.md`. Ne code rien |
| `landing-section-builder` | 4 à 7 | Construit ou corrige une section (ou un lot) dans les seuls fichiers qu'on lui confie. Ne commite jamais |
| `landing-reviewer-design` | 7 | Cohérence webdesign : en-têtes, rythme, matières, typographie, mouvement, responsive, boutons |
| `landing-reviewer-brand` | 7 | Marque : voix et anti-style-IA, ton, visuel contre `tokens.json`, preuve, audience, divulgation IA, droits |
| `landing-reviewer-cro` | 7 | Conversion : récit et objections, CTA, bloc de conversion, urgence honnête, preuve, mesure |
| `landing-reviewer-a11y` | 7 | WCAG 2.2 AA en 14 points, sur la QA mesurée et le code |

Les quatre relecteurs sont en lecture seule : ils n'écrivent que leur rapport. Si un type d'agent n'est pas reconnu dans la session (registre chargé au démarrage), dispatcher un agent généraliste dont le prompt commence par « Lis et applique `.claude/agents/<nom>.md` ».

## Où vit quoi

```
05-web-content/
├── briefs/<slug>.md                      ← brief validé (phase 1)
├── landing-pages/<slug>/
│   ├── index.html                        ← la page : HTML + CSS + JS inline, livrable unique
│   ├── assets/                           ← images, polices locales, données
│   └── pilotage/                         ← la fabrication, versionnée, jamais déployée
│       ├── spec.md                       ← spec validée (phase 3)
│       ├── page-charter.md               ← charte de la page (copie de references/charte.md)
│       ├── research-notes.md             ← recherche consolidée (landing-researcher)
│       ├── sections/<nn>-<id>.html       ← un fragment par section, propriété d'un seul agent
│       ├── reports/<nn>-<id>.md          ← rapports des builders
│       ├── review-<grille>.md            ← rapports des revues
│       └── fix-wave-brief.md             ← arbitrage de la vague de corrections
└── scripts/qa-landing.py                 ← QA mesurable (phases 5 à 8)
```

## Gabarit de données ou page sur mesure

- **Gabarit de données** : la galerie `05-web-content/templates/landing-pages/` et les sections de `05-web-content/sections-library.md`. On copie un modèle et on remplace les données (textes, chiffres, visuels, endpoint). À choisir pour une offre de type courant, un délai court, ou une série de pages de même forme (pages partenaires, pages locales, éditions successives d'un événement). Le modèle ne dispense de rien : brief, charte, QA, revues de marque et de conversion, brand-check. Les phases 2, 4 et 5 se réduisent à l'adaptation du modèle.
- **Page sur mesure** : tout le playbook. À choisir pour une offre phare, un lancement, un ticket élevé, une page qui doit porter sa propre signature visuelle. Une section qu'on crée ici et qui servira ailleurs entre ensuite dans `sections-library.md` (règle « réutiliser avant de créer »).

Dans les deux cas, une section qui figure sur deux pages est **la même section** : même structure, mêmes jetons, au pixel près. On la recopie à l'identique depuis la bibliothèque, on ne la redessine pas.

## Phase 0 : doctrine et matière réelle

1. **Doctrine**, jamais de mémoire :
   - `01-brand/checklist-pre-composition.md`, `01-brand/voice.md`, `01-brand/anti-ai-writing-style.md` ;
   - `01-brand/messaging-framework.md` (chiffres clés et hiérarchie de preuves), `01-brand/personas.md` ;
   - `01-brand/style-guide.md` et `01-brand/tokens.json` (valeurs exactes de couleur, police, rayon) ;
   - `01-brand/design-anti-generique.md` (marqueurs du look IA, workflow en deux passes) ;
   - `01-brand/divulgation-ia.md` et `01-brand/droits.md` (visuels générés, logos tiers, personnes) ;
   - `01-brand/exemples-rejetes.md` (ce que la marque a déjà refusé) ;
   - `05-web-content/CLAUDE.md` (conventions techniques, publication).
   Si un de ces fichiers manque ou porte encore des `{{...}}`, arrêter et lancer `/start-cockpit`.
2. **Matière réelle** : le document de l'offre (programme, proposition commerciale, fiche produit), les chiffres de `_sources/reports/`, le calendrier `02-strategy/calendar/calendar.md`, les assets de `01-brand/assets/` et de leur catalogue, les pages déjà produites dans `05-web-content/landing-pages/`. L'intel de `00-intel/` est confidentielle : on reformule, et aucun fait sur une personne n'en vient.
3. **Nom de l'offre** : vérifier que le nom ou la marque affichés ont le droit de porter un prix et des dates (marque tierce, partenaire, programme officiel).
4. **Recherche** : lancer tout de suite `landing-researcher` en arrière-plan, avec l'offre, l'audience et les besoins de section pressentis. Sa synthèse arrive pendant le cadrage.

## Phase 1 : cadrage, en une seule salve

Poser toutes les questions bloquantes en une fois (outil de question à choix s'il existe), chacune avec l'option recommandée en premier et la conséquence de chaque option :

1. **Audience et accès** : page publique indexée (balise `robots`, JSON-LD, liens depuis le site) ou lien direct en `noindex`.
2. **Objectif unique et action de conversion** : réservation, prise de rendez-vous, formulaire, achat, téléchargement, appel. Une page, un objectif, un CTA primaire.
3. **Circuit de vente** : qui inscrit, qui facture, qui encaisse, qui envoie la confirmation. Ce choix réécrit le bloc de conversion, les étapes et la FAQ : il se tranche avant d'écrire ces textes.
4. **Chiffres affichés** : places, prix (HT ou TTC), dates, remises, échéance. Signaler chaque écart entre la demande et le document source : le document fait foi.
5. **Preuves disponibles** : vraies personnes (avec leur accord pour le portrait), vrais documents, vrais chiffres, vrais témoignages. Ce qui manque ne s'invente pas.
6. **Visuels** : réutiliser la bibliothèque, ou générer (skill `image-generation`), avec le coût de chaque option.
7. **Source de trafic et mesure** : d'où viennent les visiteurs (message match), suivi d'audience actif ou non dans `.setup-completed`.

Un point ouvert se formule dans les mots de l'humain : ce que voit le visiteur, et pourquoi ça compte. Jamais dans ceux de l'outil.

Les réponses vont dans `05-web-content/briefs/<slug>.md` (objectif, cible et niveau de conscience, offre, source de trafic, preuves, métrique de succès). {{COMPANY_MAIN_CONTACT}} valide le brief avant la suite.

## Phase 2 : directions

Montrer 2 ou 3 directions visuelles en maquettes rapides (widget, capture ou page jetable dans le scratchpad), chacune nommée par son **objet signature** : l'élément dont on se souviendra. En recommander une. Écarter toute direction qui reprend la signature d'une autre page de la marque. Appliquer le workflow en deux passes de `01-brand/design-anti-generique.md` § 3 (plan de jetons, puis auto-critique contre le brief) et la skill `design-direction`, en injectant les jetons de `01-brand/tokens.json` : la marque prime, la skill décide des compositions, jamais des couleurs ni des polices.

L'humain choisit. Détailler ensuite la conception dans la conversation et la faire valider.

## Phase 3 : spec

Écrire `pilotage/spec.md` à partir de `templates/spec.md` :

- le cadre (réponses de la phase 1, avec leur source) ;
- la direction retenue et son objet signature ;
- le récit : une ligne par section, l'objection du visiteur qu'elle traite, la mécanique (`references/sections.md`), son moment orchestré, son fond ;
- les comportements : état de l'offre (ouverte, liste d'attente, close) piloté par **une seule configuration** en tête du script, porte de choix éventuelle, liens profonds, échéance, événements de mesure ;
- **les textes définitifs, clé par clé**, dans chaque langue de la marque. La structure CRO vient de la skill `cro-page`, le texte de la skill `copywriting` (puis `copy-editing` si l'enjeu le justifie), chaque chiffre de `messaging-framework.md` ou d'une source citée.

La spec est figée pendant chaque étape de construction. Si elle doit changer, prévenir les agents en cours.

## Phase 4 : poser avant de paralléliser

Le contrôleur (l'agent principal), seul, prépare ce qui suit, puis le montre :

1. **`index.html` socle** : `<head>` complet (titre, description, `robots`, Open Graph, favicon, `<meta name="viewport">`), bloc `:root` des jetons (`05-web-content/sections-library.md`, valeurs de `01-brand/tokens.json`), CSS commun de la charte (base, en-tête de section, famille de cartes, boutons, focus, bandes sombres), **un seul moteur d'apparition** (attributs `data-reveal`, opacité seule, coupé par `prefers-reduced-motion`), le relais de mesure (`data-track` vers `dataLayer` / `gtag`), et la configuration de l'offre.
2. **Une paire de marqueurs par section**, à sa place définitive, avec une section provisoire (id, `aria-labelledby`, titre) pour que la page s'affiche à chaque étape :
   ```html
   <!-- section:hero -->
   <section id="hero" aria-labelledby="hero-titre">…</section>
   <!-- /section:hero -->
   ```
3. `pilotage/page-charter.md`, copié depuis `references/charte.md` et complété (§ 9 : les décisions déjà prises), et `pilotage/research-notes.md` à côté.

**Le hero d'abord.** Le construire, le montrer à l'humain et le faire valider avant de lancer le reste : un hero raté entraîne toute la page.

## Phase 5 : construction en parallèle

- **Un agent par section** : un `landing-section-builder` propriétaire d'un seul fragment, `pilotage/sections/<nn>-<id>.html` (la `<section>`, son `<style>` préfixé par `#<id>`, son `<script>` éventuel enfermé dans une fonction). Personne d'autre n'écrit dans ce fichier, et aucun builder n'écrit dans `index.html`. Les lancer tous dans un seul message, chacun avec un brief tiré de `templates/brief-section.md`.
- **Assemblage** : à réception d'un rapport, le contrôleur remplace le contenu entre les marqueurs de la section par le fragment, avec un script qui vérifie que chaque marqueur existe une seule fois :
  ```python
  import re, pathlib
  page = pathlib.Path("05-web-content/landing-pages/<slug>/index.html")
  html = page.read_text(encoding="utf-8")
  for frag in sorted(page.parent.glob("pilotage/sections/*.html")):
      sid = frag.stem.split("-", 1)[1]
      debut, fin = f"<!-- section:{sid} -->", f"<!-- /section:{sid} -->"
      assert html.count(debut) == 1 and html.count(fin) == 1, sid
      motif = re.compile(re.escape(debut) + r".*?" + re.escape(fin), re.S)
      html = motif.sub(lambda _: f"{debut}\n{frag.read_text(encoding='utf-8').strip()}\n{fin}", html)
  page.write_text(html, encoding="utf-8")
  ```
  Puis `python3 05-web-content/scripts/qa-landing.py <index.html>` et un commit, sur go de l'humain si la session l'exige.
- **Recherche visuelle** : elle se fait en amont (`landing-researcher`), parce que la navigation des agents de section sur les galeries peut leur être refusée. Les builders lisent `research-notes.md`.
- **Limite d'usage** : si des agents sont coupés, assembler et commiter ce qui est fini, puis reprendre chacun par `SendMessage` avec l'endroit où il s'est arrêté et la consigne « relis d'abord l'état actuel de ton fichier ». Ne jamais relancer un agent neuf qui repartirait de zéro.

## Phase 6 : montrer, écouter, appliquer

- **Montrer** après chaque étape : donner à l'humain le chemin ou l'URL locale de la page (serveur statique lancé depuis la racine du dépôt si la page lit `01-brand/assets/`), avec la liste des points à regarder, puis enchaîner l'étape suivante sans attendre.
- **Appliquer un retour** : il s'applique, puis s'écrit au § 9 de `pilotage/page-charter.md`. S'il vaut pour toutes les landings, proposer de le reporter dans la doctrine (`01-brand/style-guide.md`, `01-brand/exemples-rejetes.md`) ou dans ce skill.
- **Micro-retouches** : le contrôleur les fait lui-même, par un remplacement scripté qui vérifie la chaîne d'origine (`assert texte in html`), puis QA et commit.
- **Ce que les revues ne voient pas** : un en-tête collé, un fond qui masque la matière, un épinglage absent, une page qui « fait template ». L'œil de l'humain reste la dernière porte.

## Phase 7 : mesure, quatre revues, une vague de corrections

1. **Mesure** : `python3 05-web-content/scripts/qa-landing.py <index.html> --format json > pilotage/qa.json`. Les relecteurs partent de ces constats au lieu de les recalculer.
2. **Revues** : lancer les quatre relecteurs en parallèle, dans un seul message, en lecture seule. Chacun écrit `pilotage/review-<grille>.md` (`references/revues.md`).
3. **Arbitrage** : le contrôleur écrit `pilotage/fix-wave-brief.md` à partir de `templates/brief-corrections.md`. Les décisions de l'humain priment, aucun chiffre n'est inventé, une structure reçoit une seule valeur, les décisions business ou légales sont posées à l'humain en une fois.
4. **Corrections** : deux `landing-section-builder` en parallèle, sur des fragments disjoints (par exemple les sections 1 à 4 pour l'un, 5 à 8 pour l'autre). Le socle (`index.html` hors marqueurs) et toute section partagée avec d'autres pages se corrigent par le contrôleur, à l'identique partout. Les constats tardifs et les retours de l'humain partent aux deux agents par `SendMessage`, avec la mention « ils priment sur le brief ».
5. **Clôture** : assembler, relancer la QA jusqu'à zéro erreur, montrer la page.

## Phase 8 : livraison

1. **Contrôles bloquants** :
   - `qa-landing.py` sans erreur aux trois tailles d'écran et en mouvement réduit ; les avertissements restants sont listés et assumés dans le rapport de livraison ;
   - agent `a11y-auditor` (rendu réel, axe-core, parcours clavier complet) : aucun constat bloquant ni majeur ;
   - `python3 scripts/lint-brand.py 05-web-content/landing-pages/<slug>/index.html` sans erreur ;
   - skill `brand-check` (texte et visuel) : verdict positif ;
   - aucun secret ni identifiant en dur dans le diff (l'ID de mesure vit dans la configuration, jamais écrit au hasard).
2. **Budget** : HTML, CSS et JS inline sous 200 Ko ; images en WebP dimensionnées à l'usage, `loading="lazy"` hors hero ; polices en `font-display: swap` ; aucun script bloquant ; cible LCP < 2,5 s.
3. **Enregistrement** : UTM et métrique de succès dans `05-web-content/deployed.md`, calendrier éditorial à jour, `python3 scripts/build-inventory.py --add 05-web-content/landing-pages/<slug>/index.html` pour l'index anti-répétition, conversions signalées au module `reporting` s'il est actif.
4. **Publication** : suivre `05-web-content/CLAUDE.md` § Publication (dry-run obligatoire), sans le dossier `pilotage/`. Contrôler ensuite la page en ligne : HTTP 200, balise `robots` conforme au brief, rendu identique à la version validée.
5. **Commit, push, publication** : seulement sur go explicite de l'humain, à chaque fois.

## Mesure : UTM et événements

**UTM** (toute URL diffusée vers la page, kebab-case, minuscules) :

| Paramètre | Contenu | Exemples |
|---|---|---|
| `utm_source` | Plateforme d'origine | `linkedin`, `newsletter`, `google`, `partenaire-x` |
| `utm_medium` | Type de canal | `social`, `email`, `cpc`, `qr`, `referral` |
| `utm_campaign` | Slug de campagne + année | `{{CAMPAIGN_SLUG}}-2026` |
| `utm_content` | Variante ou emplacement | `post-1`, `cta-hero`, `cta-final` |

Le tableau des URL trackées va dans le brief et dans `deployed.md`.

**Événements** :

- chaque CTA porte `data-track` (`cta_click` au clic, avec `data-cta-position` : `hero`, `offre`, `final`…), le formulaire `data-track="generate_lead"` ; le CTA primaire porte en plus `data-cta="primaire"`, que la QA lit pour savoir quelle conversion protéger ;
- si `web_analytics` est activé dans `.setup-completed` (GA4) : snippet gtag avec `{{GA4_MEASUREMENT_ID}}`, et un relais qui transforme ces attributs en événements `gtag('event', …)` ou `dataLayer.push(…)`, avec la formule et la langue en paramètres. `generate_lead` se marque comme conversion clé côté GA4 (action manuelle, à signaler) ;
- sinon : les attributs restent posés, pour brancher la mesure plus tard sans retoucher le HTML.

La QA vérifie les deux cas : suivi déclaré, un événement doit partir au clic de chaque CTA primaire ; suivi absent, le crochet `data-track` doit être là.

## Règles dures

- **Contenu** : aucun chiffre, client, logo, témoignage, compteur ni fait sur une personne inventé. Un compteur sans vrai chiffre reste vide.
- **Une page, un objectif** : tous les boutons mènent à la conversion ou à l'étape de choix qui y conduit. Pas de navigation complète : logo et CTA suffisent.
- **Urgence honnête** : vraies places, vraie date de clôture, comptées en jours. Jamais de compte à rebours en secondes.
- **Fichiers** : un fichier, un propriétaire. Aucun agent n'écrit dans un fichier qu'on ne lui a pas confié ; le contrôleur seul assemble et commite.
- **Actions refusées** : une action refusée à un agent (suppression, navigation, écriture) n'est refaite par personne sans l'accord de l'humain.
- **Outils tiers** : toute écriture dans un outil de vente, d'emailing ou de calendrier passe par un dry-run montré, puis un go.
- **Mouvement** : `prefers-reduced-motion: reduce` affiche tout, d'emblée, et rien ne bouge.

## Skills orchestrées

| Skill | Rôle dans le playbook | Repli si absente |
|---|---|---|
| `cro-page` | Structure CRO (phase 3) et regard CRO en revue | Ordre des objections de `references/charte.md` § 7 |
| `copywriting` / `copy-editing` | Textes définitifs de la spec | Aucun : obligatoires |
| `design-direction` / `design-system` / `design-taste` | Directions et système visuel, sous les jetons de `01-brand/tokens.json` | `sections-library.md` + `style-guide.md` |
| `design-review` | Regard UI en complément de `landing-reviewer-design` | La grille de l'agent |
| `accessibility-web` | Référentiel WCAG 2.2 AA chargé avant de construire | Grille de `landing-reviewer-a11y` |
| `cro-form` / `lead-magnet` | Formulaire de capture ; circuit complet si la page capture un email contre un contenu | Règles formulaire de `references/sections.md` |
| `image-generation` | Visuels manquants, après la bibliothèque | Assets de `01-brand/assets/` |
| `brand-check` | Validation finale obligatoire | Aucun : obligatoire |
| `performance-report` | Suivi des conversions (module `reporting`) | Notes de mesure dans `deployed.md` |

## Checklist de livraison

- [ ] Brief validé par {{COMPANY_MAIN_CONTACT}} ; spec validée, textes définitifs clé par clé
- [ ] Direction choisie par l'humain, objet signature nommé, aucune signature reprise d'une autre page
- [ ] Charte de page à jour (§ 9 : toutes les décisions de l'humain)
- [ ] Un seul objectif, `data-cta="primaire"` posé, CTA primaire visible sans défiler sur mobile
- [ ] `qa-landing.py` : zéro erreur ; avertissements restants listés et assumés
- [ ] Quatre revues rendues, vague de corrections arbitrée et appliquée
- [ ] `a11y-auditor` sans bloquant ni majeur ; `lint-brand.py` et `brand-check` au vert
- [ ] UTM et événements en place ; `deployed.md`, calendrier et inventaire à jour
- [ ] Publication par dry-run, sans `pilotage/` ; contrôle en ligne fait
