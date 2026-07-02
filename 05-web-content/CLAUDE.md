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
│   └── assets/                   ← images, fonts, données locales
├── lead-magnets/
│   ├── guides-pdf/<slug>/        ← guide PDF : brief, source HTML/DOCX chartée, PDF final
│   └── outils-web/<slug>/        ← calculateurs, quiz, diagnostics (index.html autonome)
├── pages/<slug>/                 ← pages hors conversion directe (à-propos, légal, microsite)
├── templates/                    ← composants partagés (header, footer) + galerie de templates
│   ├── landing-pages/            ← 10 modèles de landing pages par objectif (+ README)
│   └── lead-magnets/             ← 10 modèles d'outils interactifs avec capture (+ README)
└── deployed.md                   ← registre des pages publiées (URL, date, responsable)
```

## Galerie de templates — partir d'un modèle, pas d'une page blanche

`templates/` contient une galerie de modèles single-file prêts à décliner, alignés sur `sections-library.md` (mêmes tokens `{{BRAND_*}}`, mêmes classes) et sur les conventions des skills `landing-page` / `lead-magnet` (`{{FORM_ENDPOINT}}`, `data-track`, UTM/GA4) :

- **`templates/landing-pages/`** — 10 modèles par objectif de conversion : démo B2B, essai SaaS, capture de lead magnet, webinar, prestation de service, comparateur vs concurrent, tarifs, vente long-form, one-pager local, waitlist/lancement. Tableau de choix dans `templates/landing-pages/README.md`.
- **`templates/lead-magnets/`** — 10 outils interactifs (HTML/JS vanilla) avec gate de capture email : calculateur de ROI, diagnostic par score, quiz de positionnement, comparateur de scénarios, grader, checklist interactive, générateur de brief, estimateur de budget, simulateur avant/après, mini-benchmark sectoriel. Tableau de choix dans `templates/lead-magnets/README.md`.

Règle d'usage : **copier le modèle vers `landing-pages/<slug>/` ou `lead-magnets/outils-web/<slug>/`**, puis dérouler la skill correspondante — le modèle fournit structure et logique, il ne dispense d'aucune étape (brief, copy, tokens, tracking, brand-check). Les contenus d'exemple (« Meridian Conseil », données et formules placeholder) sont fictifs et ne se publient jamais tels quels.

## Règle n°1 — réutiliser avant de créer

La friction réelle mesurée sur ce type de projet n'est pas d'écrire une section, c'est la **divergence** : chaque page qui réinvente son hero ou sa FAQ crée un dialecte visuel de plus à maintenir, et la marque se dilue page après page.

Avant d'écrire le moindre bloc HTML :

1. **Lire `sections-library.md`** — si une section du type recherché existe, la décliner (contenu, pas structure).
2. **Scanner `landing-pages/` et `pages/`** — si une page proche existe, repartir de ses sections.
3. **`templates/`** — header et footer viennent toujours de là.
4. Créer une nouvelle section **seulement si aucune ne couvre le besoin** — et dans ce cas, l'ajouter à `sections-library.md` dans la foulée pour la prochaine fois.

## Skills orchestrées — ordre d'invocation

Les deux skills maîtresses de ce dossier sont **`landing-page`** et **`lead-magnet`** (`.claude/skills/`). Elles orchestrent les skills internes du template — le copilot est autonome, aucune skill externe n'est requise. Si une skill interne listée manque (template partiellement synchronisé), la skill maîtresse applique le fallback inline documenté.

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
| 11 | Revue design / QA visuelle | `design-review` | checklist QA de la skill `landing-page` |
| 12 | Validation finale | `brand-check` | — (**obligatoire**) |
| 13 | Mesure | `performance-report` (module `reporting`) | noter les métriques dans `deployed.md` |

**Règle de préséance design (non négociable).** Les skills de design (`design-direction`, `design-system`, `design-review`) ne sont JAMAIS invoquées à froid : toujours charger d'abord les tokens de `../01-brand/style-guide.md` et les injecter dans la demande, en précisant explicitement que **la marque prime sur tout style générique**. Une skill design propose des compositions, des hiérarchies, des interactions — pas une palette ni une typographie : celles-là viennent de `01-brand/`.

## Workflows

### Landing page → skill `landing-page`

Tout est dans `.claude/skills/landing-page/SKILL.md` : brief → structure CRO → copy → design sous tokens → build → tracking → QA responsive + vitesse → brand-check → livraison dans `landing-pages/<slug>/`.

### Lead magnet → skill `lead-magnet`

Tout est dans `.claude/skills/lead-magnet/SKILL.md` : typologie → production par type → **circuit de capture complet obligatoire** (formulaire → n8n → outil emailing → nurturing). Un lead magnet sans capture d'email est un PDF perdu.

### Page simple (à-propos, légal, microsite) — workflow inline

1. **Brief** dans `briefs/<slug>.md` : objectif, persona, CTA, preuves, métrique de succès. {{COMPANY_MAIN_CONTACT}} valide avant rédaction.
2. **Consulter l'existant** — scanner `landing-pages/`, `pages/`, `_templates/inventory.md` et `../01-brand/messaging-framework.md`.
3. **Copy** via la skill `copywriting` — chaque section ancrée dans un chiffre du messaging framework.
4. **Build** selon les conventions techniques ci-dessous, sections issues de `sections-library.md`.
5. **Brand-check**, puis livraison dans `pages/<slug>/`.

## Conventions techniques (toutes pages)

- Tokens de `../01-brand/style-guide.md` déclarés en CSS custom properties dans `:root` (voir bloc de référence dans `sections-library.md`).
- Mobile-first ; tester à 375px, 600px, 900px, 1280px.
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

## Enregistrement et mesure

- Mettre à jour `deployed.md` : URL, date, responsable, UTM de campagne, métrique de succès attendue.
- Mettre à jour le calendrier éditorial (`../02-strategy/calendar/calendar.md`) : statut `publié`.
- Si le module `reporting` est actif : les conversions des landing pages et les téléchargements de lead magnets remontent dans `../11-reporting/` (voir skill `performance-report`).

## Validation finale

Chaque page passe `brand-check` — copy ET conformité visuelle (couleurs, polices, espacements contre le style guide) — avant tout déploiement.
