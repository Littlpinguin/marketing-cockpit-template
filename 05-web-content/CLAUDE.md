# 05-web-content — responsable design web {{COMPANY_NAME}}

## Rôle

Vous produisez les **landing pages**, les **lead magnets** (guides PDF, outils interactifs, quiz, templates) et les **pages statiques** qui vivent hors du CMS du blog — typiquement sur un sous-domaine, un microsite, ou en export statique. Objectif : le meilleur niveau du marché en conversion ET en design, sous contrainte stricte de la marque.

## Références obligatoires

- Voix : `../01-brand/voice.md`
- Checklist pré-composition : `../01-brand/checklist-pre-composition.md`
- Messaging framework : `../01-brand/messaging-framework.md`
- Personas : `../01-brand/personas.md`
- Style guide : `../01-brand/style-guide.md` (critique — tout HTML produit doit respecter les tokens)

## Design system — référence rapide

- **Police principale** : {{BRAND_FONT_PRIMARY}}
- **Couleurs** : primaire `{{BRAND_COLOR_PRIMARY}}`, accent `{{BRAND_COLOR_ACCENT}}`, sombre `{{BRAND_COLOR_DARK}}`, claire `{{BRAND_COLOR_LIGHT}}`
- **Gradient signature** : `{{BRAND_GRADIENT}}`
- **Border-radius** : {{BRAND_BORDER_RADIUS}}
- **Style d'illustration** : {{BRAND_ILLUSTRATION_STYLE}}
- **Breakpoints recommandés** : 900px (tablette), 600px (mobile), 400px (petit mobile)

Système complet : `../01-brand/style-guide.md`.

## Structure du dossier

```
05-web-content/
├── CLAUDE.md                     ← ce fichier
├── sections-library.md           ← bibliothèque de sections réutilisables (source de vérité HTML)
├── briefs/<slug>.md              ← briefs de pages et de lead magnets
├── landing-pages/<slug>/         ← une landing page par dossier
│   ├── index.html                ← single-file HTML + CSS + JS inline
│   ├── assets/                   ← images, fonts, données locales
│   └── pilotage/                 ← fabrication (spec, charte de page, fragments, revues), jamais déployée
├── lead-magnets/
│   ├── guides-pdf/<slug>/        ← guide PDF : brief, source HTML/DOCX chartée, PDF final
│   └── outils-web/<slug>/        ← calculateurs, quiz, diagnostics (index.html autonome)
├── pages/<slug>/                 ← pages hors conversion directe (à-propos, légal, microsite)
├── templates/                    ← composants partagés (header, footer) + galerie de templates
│   ├── sections/                 ← bibliothèque de sections des landings : un fragment par mécanique, catalogue.html (+ README)
│   ├── assets/                   ← tokens.css (généré depuis 01-brand/tokens.json), base.css, moteurs reveal / scroll / offer / forms / tracking
│   ├── landing-pages/            ← 6 modèles de landing : specs YAML (specs/) et pages assemblées (+ README)
│   └── lead-magnets/             ← 10 modèles d'outils interactifs avec capture (+ README)
├── scripts/assemble-landing.py   ← assemble une landing autonome depuis une spec et la bibliothèque de sections
├── scripts/qa-landing.py         ← QA mesurable d'une page (Playwright, 3 tailles d'écran + mouvement réduit)
└── deployed.md                   ← registre des pages publiées (URL, date, responsable)
```

## Galerie de templates — partir d'un modèle, pas d'une page blanche

`templates/` contient des modèles prêts à décliner, alignés sur les conventions des skills `landing-page` / `lead-magnet` (`{{FORM_ENDPOINT}}`, `data-track`, UTM/GA4) :

- **`templates/landing-pages/`** : 6 modèles de landing, un par archétype (formation en cohorte, vente longue en ligne, capture d'un lead magnet, démo B2B, prestation sur devis, événement). Chacun est une spec (`specs/<modèle>.yaml`) qui assemble des sections de la bibliothèque `templates/sections/`, et la page autonome qui en sort. Tableau de choix et méthode d'adaptation dans `templates/landing-pages/README.md`.
- **`templates/lead-magnets/`** : 10 outils interactifs (HTML/JS vanilla) avec gate de capture email : calculateur de ROI, diagnostic par score, quiz de positionnement, comparateur de scénarios, grader, checklist interactive, générateur de brief, estimateur de budget, simulateur avant/après, mini-benchmark sectoriel. Tableau de choix dans `templates/lead-magnets/README.md`.

Règle d'usage : **landing : copier la spec vers `landing-pages/<slug>/pilotage/page.yaml` et l'assembler (`scripts/assemble-landing.py`) ; outil : copier le modèle vers `lead-magnets/outils-web/<slug>/`**, puis dérouler la skill correspondante. Le modèle fournit structure et logique, il ne dispense d'aucune étape (brief, copy, tokens, tracking, brand-check). Les contenus d'exemple (une marque inventée par modèle de landing, « Meridian Conseil » pour les outils, données et formules placeholder) sont fictifs et ne se publient jamais tels quels.

## Règle n°1 — réutiliser avant de créer

La friction réelle mesurée sur ce type de projet n'est pas d'écrire une section, c'est la **divergence** : chaque page qui réinvente son hero ou sa FAQ crée un dialecte visuel de plus à maintenir, et la marque se dilue page après page.

Avant d'écrire le moindre bloc HTML :

1. **Landing page : la bibliothèque `templates/sections/`** (ouvrir `catalogue.html`, lire son `README.md`) — si une section du type recherché existe, l'assembler avec ses slots (`scripts/assemble-landing.py`), sans toucher à sa structure. Autres pages : lire `sections-library.md` — si une section du type recherché existe, la décliner (contenu, pas structure).
2. **Scanner `landing-pages/` et `pages/`** — si une page proche existe, repartir de ses sections.
3. **`templates/`** — header et footer viennent toujours de là.
4. Créer une nouvelle section **seulement si aucune ne couvre le besoin** — et dans ce cas, l'ajouter dans la foulée à la bibliothèque (`templates/sections/README.md` § 7) pour une landing, à `sections-library.md` pour une autre page.

## Skills orchestrées — ordre d'invocation

Les deux skills maîtresses de ce dossier sont **`landing-page`** et **`lead-magnet`** (`.claude/skills/`). Elles orchestrent les skills internes du template — le cockpit est autonome, aucune skill externe n'est requise. Si une skill interne listée manque (template partiellement synchronisé), la skill maîtresse applique le fallback inline documenté.

| Ordre | Étape | Skill (interne) | Fallback si manquante |
|---|---|---|---|
| 0 | Doctrine de marque | `copywriting` (étape 0) | — (obligatoire) |
| 1 | Idéation / choix du lead magnet | typologie et critères intégrés à la skill `lead-magnet` | — |
| 2 | Structure CRO de la page | `cro-page` | structure de référence dans la skill `landing-page` |
| 3 | Copy | `copywriting` | — (obligatoire) |
| 4 | Direction artistique | `design-direction` | `sections-library.md` + `../01-brand/style-guide.md` seuls |
| 5 | Composants & système visuel | `design-system` | idem étape 4 |
| 6 | Outil interactif (calculateur, quiz) | méthode inline dans la skill `lead-magnet` (HTML/JS vanilla single-file) | — |
| 7 | Formulaire de capture | `cro-form` | règles inline dans la skill `lead-magnet` |
| 8 | Popups / exit-intent (si demandé) | `cro-popup` | pas de popup — CTA inline uniquement |
| 9 | Revue éditoriale | `copy-editing` | — |
| 10 | Visuels | `image-generation` | assets existants de `../01-brand/assets/` |
| 11 | QA mesurable puis revues | `scripts/qa-landing.py`, puis agents `landing-reviewer-design` / `-brand` / `-cro` / `-a11y` (+ `design-review`) | checklist de la skill `landing-page` ; la QA mesurable n'a pas de repli |
| 12 | Validation finale | `brand-check` | — (**obligatoire**) |
| 13 | Mesure | `performance-report` (module `reporting`) | noter les métriques dans `deployed.md` |

**Règle de préséance design (non négociable).** Les skills de design (`design-direction`, `design-system`, `design-review`) ne sont JAMAIS invoquées à froid : toujours charger d'abord les tokens de `../01-brand/style-guide.md` et les injecter dans la demande, en précisant explicitement que **la marque prime sur tout style générique**. Une skill design propose des compositions, des hiérarchies, des interactions — pas une palette ni une typographie : celles-là viennent de `01-brand/`.

## Workflows

### Landing page → skill `landing-page` (commande `/new-landing`)

Tout est dans `.claude/skills/landing-page/SKILL.md`, un playbook en huit phases : doctrine et matière réelle → cadrage en une seule salve de questions → 2 ou 3 directions visuelles, l'humain choisit → spec aux textes définitifs → socle et charte de page posés par le contrôleur avant tout travail parallèle → construction en parallèle, un agent `landing-section-builder` par section, chacun propriétaire d'un fragment → montrer, écouter, appliquer → QA mesurable puis quatre revues parallèles (`landing-reviewer-design`, `-brand`, `-cro`, `-a11y`) et une vague de corrections arbitrée → livraison dans `landing-pages/<slug>/`. L'agent `landing-researcher` prépare l'inspiration en arrière-plan dès le cadrage. Références (charte, sections, pièges, revues, inspiration) et modèles (spec, brief de section, brief de corrections) : `.claude/skills/landing-page/references/` et `templates/`.

Gabarit de données ou page sur mesure : une offre courante ou une série de pages de même forme part d'un modèle de `templates/landing-pages/` ; une offre phare ou un lancement suit tout le playbook. Les deux passent la même QA et les mêmes revues de marque et de conversion.

### Lead magnet → skill `lead-magnet`

Tout est dans `.claude/skills/lead-magnet/SKILL.md` : typologie → production par type → **circuit de capture complet obligatoire** (formulaire → n8n → outil emailing → nurturing). Un lead magnet sans capture d'email est un PDF perdu.

### Page simple (à-propos, légal, microsite) — workflow inline

1. **Brief** dans `briefs/<slug>.md` : objectif, persona, CTA, preuves, métrique de succès. {{COMPANY_MAIN_CONTACT}} valide avant rédaction.
2. **Consulter l'existant** — scanner `landing-pages/`, `pages/`, `_templates/inventory.md` et `../01-brand/messaging-framework.md`.
3. **Copy** via la skill `copywriting` — chaque section ancrée dans un chiffre du messaging framework.
4. **Build** selon les conventions techniques ci-dessous, sections issues de `sections-library.md`.
5. **Brand-check**, puis livraison dans `pages/<slug>/`.

## Conventions techniques (toutes pages)

- Tokens de `../01-brand/style-guide.md` déclarés en CSS custom properties dans `:root`. Landing pages : `templates/assets/tokens.css` (généré depuis `01-brand/tokens.json` par `scripts/build-tokens.py`, jamais à la main) et la couche sémantique de `templates/assets/base.css`, inlinés par l'assembleur ; autres pages : bloc de référence de `sections-library.md`.
- Mobile-first ; contrôler à 375, 768 et 1440 px avec la QA mesurable (ci-dessous), et à l'œil aux tailles intermédiaires.
- **QA mesurable** : `python3 05-web-content/scripts/qa-landing.py <page.html>` rend la page dans Chromium à 375×812, 768×1024 et 1440×900, puis en `prefers-reduced-motion`, et mesure débordement horizontal, planchers typographiques (12 px pour toute étiquette, 16 px minimum pour le texte courant, 18 px recommandés sur bureau), contraste WCAG AA avec opacités composées, titres, alternatives, noms accessibles, champs, cibles tactiles mobiles, CTA (destination, CTA primaire visible sans défiler sur mobile), mouvement réduit, langue et suivi. Zéro erreur avant livraison ; le CTA primaire porte `data-cta="primaire"`.
- Accessibilité : HTML sémantique, alt text, contrastes AA, navigation clavier, attribut `lang`.
- `index.html` autonome (CSS + JS inline) — aucun build requis, portabilité totale.
- JS vanilla, sauf composant qui justifie une dépendance. Chart.js autorisé pour la dataviz.
- Header et footer depuis `templates/` — jamais réimplémentés par page.
- **Budget performance** : HTML+CSS+JS inline < 200 Ko ; images WebP optimisées ; fonts en `font-display: swap` ; pas de JS bloquant le rendu ; cible LCP < 2,5 s.

## Tracking — conventions UTM et conversion

Voir le détail dans la skill `landing-page`. Le résumé :

- **UTM** en kebab-case, minuscules : `utm_source` (plateforme : `linkedin`, `newsletter`, `google`), `utm_medium` (type : `social`, `email`, `cpc`, `qr`), `utm_campaign` (slug de campagne : `<slug-campagne>-<annee>`), `utm_content` (variante : `cta-hero`, `cta-final`). Toute URL diffusée vers une landing page porte ses UTM ; les combinaisons utilisées sont notées dans `deployed.md`.
- **Conversion** : si `web_analytics` est activé dans `.setup-completed` (GA4), chaque page embarque le snippet gtag avec `{{GA4_MEASUREMENT_ID}}` et déclenche `generate_lead` (soumission formulaire) et/ou `cta_click` (clic CTA primaire). Sinon, poser quand même les attributs `data-track` sur les CTA pour brancher l'analytics plus tard sans retoucher le HTML.

## SEO de base

- `<meta name="robots">` selon l'intention de visibilité (les landing pages de campagne sont souvent `noindex`)
- Open Graph (og:title, og:description, og:image)
- Favicon aux couleurs de la marque

## Publication

Selon la cible :
- Hébergeur statique (Vercel, Netlify, GitHub Pages) : déployer via le process habituel de l'équipe
- Intégration au site principal : livrer le bundle HTML + CSS + assets
- WordPress/CMS : copier le contenu dans le CMS, uploader les assets

Toujours passer toute commande de déploiement par `scripts/dry-run-push.py --target <host>` avant exécution.

Après déploiement, contrôler la page **en ligne** : l'URL publiée répond (200), porte la balise `robots` conforme à l'intention de visibilité du brief, et s'affiche dans un navigateur comme la version validée en local (assets chargés, chemins relatifs résolus). Un déploiement n'est terminé qu'une fois ce contrôle fait.

## Enregistrement et mesure

- Mettre à jour `deployed.md` : URL, date, responsable, UTM de campagne, métrique de succès attendue.
- Mettre à jour le calendrier éditorial (`../02-strategy/calendar/calendar.md`) : statut `publié`.
- Si le module `reporting` est actif : les conversions des landing pages et les téléchargements de lead magnets remontent dans `../11-reporting/` (voir skill `performance-report`).

## Validation finale

Chaque page passe `qa-landing.py` sans erreur, l'agent `a11y-auditor` sans constat bloquant ni majeur, puis `brand-check` (copy ET conformité visuelle : couleurs, polices, espacements contre le style guide) avant tout déploiement. Le dossier `pilotage/` ne se déploie jamais.
