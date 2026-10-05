# Bibliothèque de sections des landings

Les sections éprouvées d’une landing de conversion, chacune dans un fragment autonome, plus les moteurs partagés et un assembleur qui en fait une page HTML d’un seul fichier. La méthode (quand une page prend telle mécanique, pourquoi, ce qui la fait échouer) vit dans la skill `landing-page` (`.claude/skills/landing-page/references/sections.md`) ; ce dossier en est l’implémentation.

**Voir avant de choisir** : ouvrir `catalogue.html` dans un navigateur. Chaque section y apparaît, remplie de son contenu d’exemple (marque fictive Meridian Conseil, offre fictive), précédée de sa fiche : objection traitée, quand l’utiliser, quand l’éviter, comportement en mouvement réduit, slots, moteurs.

```
05-web-content/
├── templates/
│   ├── assets/
│   │   ├── tokens.css        ← variables de marque, GÉNÉRÉES depuis 01-brand/tokens.json
│   │   ├── base.css          ← couche sémantique, rythme, typo, composants, kit d'objets
│   │   ├── reveal.js         ← moteur d'apparition (toujours chargé)
│   │   ├── tracking.js       ← relais de mesure dataLayer / gtag, UTM (toujours chargé)
│   │   ├── scroll.js         ← théâtre de défilement : épinglage, progression, jonctions
│   │   ├── offer.js          ← état de l'offre (ouverte, liste d'attente, close), jours restants
│   │   ├── forms.js          ← validation et envoi des formulaires de capture
│   │   ├── viewer.js         ← visionneuse (vidéo, images, dossier à feuilleter)
│   │   ├── annotate.js       ← annotations à main levée (deux par page au plus)
│   │   └── catalogue.css     ← fiches du catalogue seulement
│   └── sections/
│       ├── <nom>.html        ← un fragment par mécanique
│       ├── _placeholder.html ← section provisoire (outil, hors catalogue)
│       ├── catalogue.json    ← spec du catalogue
│       ├── catalogue.html    ← catalogue assemblé (ne pas éditer)
│       └── README.md
└── scripts/
    ├── assemble-landing.py   ← spec → page autonome
    └── qa-landing.py         ← QA mesurable de la page
```

## 1. Choisir ses sections

Une page prend une dizaine de sections, une objection par section, dans l’ordre de la pensée du visiteur (charte § 7) : de quoi s’agit-il, pourquoi maintenant, quoi exactement, pour qui, avec qui, comment ça s’insère dans ma vie, combien, comment je réserve, et ensuite.

| Fragment | Mécanique | Objection | Moteurs | Fond |
|---|---|---|---|---|
| `topbar` | Barre du haut (logo + un bouton), qui s’efface à la descente ; option `cta_after_hero` | Où agir | | clair, collante |
| `hero` | Hero à objet fort, accroche tournante facultative | De quoi s’agit-il, pour qui, jusqu’à quand | (offer pour les jours) | clair |
| `hero-editorial` | Hero éditorial : très grand titre sur la grille, filet tracé, ligne de faits | De quoi s’agit-il, quand, où, combien | (offer pour les jours) | clair |
| `hero-image-title` | Hero à image dans le titre : pastille à hauteur de lettre entre deux mots | De quoi s’agit-il, pour qui, jusqu’à quand | (offer pour les jours) | clair |
| `chapters` | Sommaire après le hero, puis rail de repères dans la marge (dès 1101 px) ou barre « Chapitre n sur N » (petit écran) qui suit la lecture | Où en suis-je, où est ce qui m’intéresse | (script propre) | clair ; rail fixe en marge, barre fixe sous la barre du haut |
| `proof-band` | Bande de preuve immédiate, chiffres qui comptent | Est-ce sérieux | | clair |
| `logos` | Logos clients autorisés | Qui d’autre leur fait confiance | | clair |
| `problem-evidence` | Problème en pièces à conviction, titre collant, tampon de verdict, réponse vers l’offre | Pourquoi maintenant | | clair, colonne collante (non épinglé) |
| `problem-pinned` | Problème épinglé, constat actif déplié | Pourquoi maintenant | scroll | clair, épinglé |
| `pivot` | Basculement typographique, mots encrés au défilement | Et donc, quelle réponse | scroll | clair, épinglé, sortie en fondu |
| `choice-gate` | Porte de choix qui révèle la suite | Laquelle est pour moi | | clair, entrée en fondu |
| `recommender` | Recommandeur : 2 ou 3 questions, puis l’offre conseillée et pourquoi | Laquelle de vos offres est pour moi | | clair |
| `benefits` | Bénéfices ancrés dans un fait | Qu’est-ce que j’y gagne | | clair |
| `journey` | Parcours en scrollytelling (rail, scène) | Concrètement, que fais-je | scroll | clair, épinglé |
| `program` | Programme détaillé, rail, spécimen | Qu’y a-t-il dedans | scroll | clair |
| `quote-interlude` | Citation en respiration, une phrase en grand, annotation facultative | Qu’en dit quelqu’un qui l’a vécu | annotate | clair ou bande sombre (`dark`) |
| `showcase-dark` | Vitrine d’un objet tangible | Qu’est-ce que j’emporte | | bande sombre |
| `map-pinned` | Carte ou schéma tracé au défilement | Compatible avec ma vie | scroll | clair, épinglé |
| `demonstrator` | Démonstrateur : une demande s’écrit et le résultat se compose (`replay`), ou une estimation calculée avec ses sources (`calculator`) | Est-ce que ça marche pour mon cas | | clair ou bande sombre (`dark`), résultat papier |
| `people` | Personnes, biographie en trois temps | Avec qui | | clair |
| `letter` | Lettre signée : typographie de livre, lettrine, signature tracée, paragraphe encré au défilement | Qui est derrière l’offre, pourquoi lui faire confiance | | clair, marge collante |
| `testimonials` | Trois avis signés, chacun avec un résultat | D’autres l’ont-ils fait | | clair |
| `wall` | Mur d’avis qui se déplie, colonne de synthèse qui reste à l’écran | D’autres comme moi l’ont-ils fait, et sont-ils nombreux | viewer | clair |
| `cases` | Cas avant / après, même mesure sur chaque carte | Ça a marché pour d’autres, de combien | | bande sombre ou clair (`dark`) |
| `work-wall` | Mur de réalisations filtrable, en grille ou en index, dossiers à feuilleter | Qu’est-ce que ça produit concrètement, pour quelqu’un comme moi | viewer | clair ou bande sombre (`dark`) |
| `evidence-chart` | Un chiffre, un graphique, une source : conclusion en titre, barres en liste, une mise en avant | Est-ce vrai, et de combien | annotate | clair (carte) |
| `outcomes` | Résultats en respiration, filets tracés | Qu’est-ce que ça change | | clair |
| `for-whom` | Pour qui (`fit`), et pour qui ce n’est pas (`not_fit`) | Est-ce pour moi | | clair |
| `facts-grid` | Fiche pratique en liste de définitions, icônes de jetons, état de l’offre | Quand, où, combien de temps, à quel prix | (offer pour l’état) | clair |
| `process` | Étapes après le clic | Et après | | clair |
| `comparison` | Tableau comparatif daté | Pourquoi cette option | | clair |
| `ownership-diagram` | Schéma de propriété : ce que le client possède, les outils qui s’y branchent, preuves de sortie | Suis-je enfermé chez vous | | clair, bloc possédé sombre |
| `pricing-table` | Grille de 2 ou 3 plans, bascule mensuel / annuel | Quelle formule | | clair, plan recommandé sombre |
| `bundle-receipt` | Ticket de caisse qui se remplit à chaque case, puis propose le pack avec l’économie exacte (formulaire GET) | À la carte ou en pack, combien | offer | clair, ticket collant (grand écran) |
| `offer-ticket` | Bloc de conversion en billet (formulaire GET) | Combien, compris, comment, ensuite | offer | clair |
| `guarantee` | Garantie : sceau et conditions exactes | Et si ça ne me sert pas | | clair |
| `lead-capture` | Formulaire de capture (email) | Que je donne, que je reçois | forms | clair |
| `form` | Formulaire qualifiant (démo, rendez-vous, devis) | Comment je prends contact | forms | clair |
| `event-registration` | Inscription à un événement, sur place ou en ligne | Comment je m’inscris, comment je participe | forms, offer | bande sombre ou clair (`dark`) |
| `faq` | FAQ en accordéon natif, carte collante | Dernières questions | | clair |
| `legal` | Informations légales | Qui vend, à quelles conditions | | clair |
| `final-cta` | CTA final | Je passe à l’action | | bande sombre, rideau |
| `footer` | Pied de page | Mentions | | clair |
| `sticky-bar` | Barre d’action mobile | Agir sans remonter | | fixe, mobile |

`python3 05-web-content/scripts/assemble-landing.py --list` donne la liste, `--describe <fragment>` les slots et leurs champs.

**Compositions de départ** (à adapter au récit de la spec, jamais à recopier par réflexe) :

| Type de page | Sections, dans l’ordre |
|---|---|
| Formation, cohorte, atelier payant | topbar, hero, facts-grid ou proof-band, problem-pinned, letter (la personne répond au problème), journey ou program, quote-interlude ou outcomes (respiration non épinglée), showcase-dark, people, testimonials (wall dès huit avis), for-whom, offer-ticket, faq, legal, final-cta, footer, sticky-bar |
| Offre achetée en ligne (vente longue) | topbar, hero, chapters (sommaire), proof-band, problem-pinned, pivot, … wall (à la place de testimonials dès huit avis), … bundle-receipt (éléments à la carte et pack) ou offer-ticket (une formule : billet horizontal), guarantee juste après, faq, final-cta … |
| Offre à formules réelles | … pivot, choice-gate (deux formules) ou recommender (trois et plus, ou un choix qui dépend du profil), puis les sections de la suite marquées `gated`, offer-ticket (la porte ou le recommandeur règle sa formule) … |
| Capture d’un contenu (guide, liste) | hero avec l’objet du livrable (il se voit dès l’ouverture) ou hero-image-title, lede court, lead-capture tôt, benefits ou program, evidence-chart, people ou testimonials, faq, footer |
| Démo B2B, rendez-vous, devis | topbar, hero, logos, problem-pinned, benefits, journey, demonstrator (`calculator`), ownership-diagram, testimonials, process, form, faq, final-cta, footer |
| Prestation, accompagnement | topbar, hero ou hero-image-title, problem-evidence, program, work-wall (`index`), cases, people, for-whom, recommender, pricing-table (prix « dès »), form, faq, final-cta |
| Événement, webinar | topbar, hero-editorial (sa ligne de faits dit quand, où, combien), program (agenda minuté), people, map-pinned (lieux, fuseaux), event-registration (gratuit) ou offer-ticket (payant), faq, final-cta |
| Tarifs, essai | topbar, hero, logos, pricing-table (`primary` sur le plan recommandé), comparison, testimonials, faq, final-cta |

Les six modèles de `05-web-content/templates/landing-pages/specs/` (formation, vente-longue, lead-magnet, demo-b2b, prestation, evenement) sont ces compositions remplies : partir de l’un d’eux plutôt que d’une page vide.

Règles de page : une seule section de problème (`problem-pinned` ou `problem-evidence`, qui ne compte pas comme épinglage) ; trois épinglages au plus, et jamais deux d’affilée, avec une seule exception, le couple `problem-pinned` → `pivot`, conçu pour s’enchaîner (le pivot, une phrase seule à l’écran, sert de respiration) ; après ce couple, une section non épinglée avant tout autre épinglage ; une ou deux bandes sombres plus le CTA final, jamais deux d’affilée ; un seul accent fort (le bouton de conversion) ; une seule conversion (tous les `data-cta="primaire"` mènent au même endroit : l’ancre du bloc de conversion ou son bouton d’envoi). Le catalogue enfreint volontairement ces règles pour tout montrer.

## 2. La spec d’une page

Une page s’écrit dans une spec, puis s’assemble :

```bash
python3 05-web-content/scripts/assemble-landing.py 05-web-content/landing-pages/<slug>/pilotage/page.json
python3 05-web-content/scripts/qa-landing.py 05-web-content/landing-pages/<slug>/index.html
```

Formats : JSON (`.json`, toujours disponible), YAML (`.yaml`, `.yml`) ou Markdown à front matter YAML (`.md`), ces deux derniers avec PyYAML. Seuls `title` et `sections` sont obligatoires. `output` se lit depuis la racine du dépôt ; `-o` prime et se lit depuis le dossier courant ; un `file` de section se lit depuis le dossier de la spec.

```yaml
---
output: 05-web-content/landing-pages/bilan-printemps/index.html
title: "Bilan carbone en six semaines"
description: "Six ateliers en petit groupe pour mesurer vos émissions."
lang: fr
page: bilan-printemps            # slug envoyé avec chaque événement de mesure
robots: "noindex, nofollow"      # « index, follow » pour une page pérenne
canonical: https://www.example.com/bilan/
og: {title: "…", description: "…", image: https://www.example.com/og.webp}
favicon: assets/favicon.svg
fonts: ["Inter:wght@400;500;600;700;800", "JetBrains Mono:wght@500;600"]   # Google Fonts, display=swap
assets: inline                   # inline : un seul fichier (défaut) ; link : <link>/<script src> relatifs
ground: dots                     # dots : trame de points de la marque ; plain : aplat
theatre: {progress: true}        # fil de lecture de 3 px en haut (grand écran)
tracking: {mode: datalayer, utm: true}   # datalayer | gtm (+ gtm: GTM-…) | gtag (+ ga4: G-…) | off
offer: {state: open, closes_at: "2027-03-31T23:59:00+02:00", after_close: waitlist}
sections:
  - use: topbar
  - use: hero
    slots:
      title: "Le bilan carbone<br><span class=\"hl\">en six semaines</span>"
      lede: "Six ateliers en petit groupe pour mesurer vos émissions."
      cta_label: Réserver ma place
      cta_href: "#offre"
      deadline: Inscriptions jusqu'au 31 mars 2027
  - use: offer-ticket
    id: offre                    # l'ancre de tous les CTA de la page
    slots: {action: "{{URL_CHECKOUT}}", …}
  - use: _placeholder            # place réservée à une section sur mesure
    id: avant-apres
  - file: sections/07-avant-apres.html     # fragment d'un builder, inséré tel quel
    id: avant-apres
---
Notes libres sur la page (ignorées par l'assembleur).
```

**Clés booléennes.** En YAML 1.1 (PyYAML), une clé nue `yes`, `no`, `on` ou `off` devient `true` ou `false` : le slot visé ne serait jamais rempli. L’assembleur refuse donc toute spec qui porte une clé booléenne (« clé booléenne : YAML lit yes/no/on/off comme des booléens, mettez la clé entre guillemets ») ; c’est pourquoi les colonnes de `for-whom` s’appellent `fit` et `not_fit`, et les cellules du tableau comparatif s’écrivent `{"yes": true, text: …}`.

Clés de section : `use` (nom du fragment) ou `file` (fragment sur mesure, avec `id` obligatoire), `id` (unique sur la page, minuscules et tirets, défaut : le nom du fragment ; c’est l’ancre et la base des `aria-labelledby`), `slots`, `gated` (caché jusqu’au choix de la porte), `samples` (texte d’exemple admis pour cette section). Autres clés de page : `samples` (tout le texte d’exemple admis, pour une démo), `annotate` et `intro` (fiches du catalogue), `engines` (forcer un moteur), `skip_link` (libellé du lien d’évitement), `library` (autre dossier de fragments, lu depuis le dossier de la spec ; `--library` en ligne de commande prime sur elle).

## 3. Les slots

Les fragments lisent leurs valeurs par un sous-ensemble de Mustache, en minuscules :

| Balise | Effet |
|---|---|
| `{{nom}}` | valeur échappée (texte, attribut) |
| `{{{nom}}}` | HTML brut (slots de type `html` : titres avec `<span class="hl">` et `<br>`, objets composés) |
| `{{#nom}}…{{/nom}}` | liste : un rendu par élément ; objet ou valeur vraie : un rendu ; vide, `false`, `null` : rien |
| `{{^nom}}…{{/nom}}` | rendu seulement si la valeur est vide ou fausse |
| `{{.}}` | élément courant d’une liste de textes |
| `{{@index}}`, `{{@index0}}`, `{{@first}}`, `{{@last}}`, `{{@count}}` | variables de boucle |
| `{{a.b}}`, `{{liste.length}}` | champ d’un objet, longueur d’une liste |

Une valeur cherchée dans une boucle remonte au contexte de la section si l’élément ne la porte pas (`{{outcome_label}}` dans `{{#steps}}`). Les marqueurs du dépôt en majuscules (`{{FORM_ENDPOINT}}`, `{{URL_CHECKOUT}}`) ne sont jamais interprétés : ils restent dans la page, la QA et `lint-placeholders.py` les signalent jusqu’à ce qu’ils soient remplacés.

**Marqueurs ou adresses d’exemple.** Les modèles (`landing-pages/specs/`) écrivent en marqueur chaque lien qui reste à brancher : liens légaux (`{{URL_MENTIONS_LEGALES}}`, `{{URL_CGV}}`, `{{URL_CONFIDENTIALITE}}`), paiement (`{{URL_CHECKOUT}}`), liste d’attente (`{{URL_LISTE_ATTENTE}}`), itinéraire, endpoint de formulaire (`{{FORM_ENDPOINT}}`). La QA les signale jusqu’à la publication, et un formulaire dont l’action est encore un marqueur ne compte jamais de lead (§ 4). Les exemples de la bibliothèque (slots des fragments, `catalogue.json`) gardent des adresses du domaine réservé `https://www.example.com/…` (et ses sous-domaines), pour que le catalogue montre des liens complets ; seul l’exemple d’un endpoint de fragment (`action`) reste un marqueur, pour qu’un slot oublié n’envoie jamais rien.

Chaque slot est documenté dans la fiche du fragment : `type` (`text`, `html`, `url`, `bool`, `list`, `object`, `number`), `doc`, `fields` (pour une liste ou un objet), `example` et, pour un slot facultatif, `default`. **Un slot non rempli prend son exemple et l’assembleur le signale** : le texte fictif ne part jamais en production par oubli. `--strict` transforme chaque avertissement en échec.

**Slots facultatifs.** Un slot qui porte une clé `default` est une option : non rempli, il prend cette valeur, sans avertissement (`--strict` passe). Le catalogue et toute spec en `samples` montrent toujours l’`example`, pour que l’option s’y voie. Exemples : `topbar.cta_after_hero` (`false` : le bouton de la barre ne guette ni le hero ni le bloc de conversion), `evidence-chart.poster` (`null` : pas de chiffre en affiche). Un nouveau slot ajouté à un fragment déjà employé par des modèles prend un `default` neutre, pour que les specs existantes restent à zéro avertissement. `--describe` affiche « facultatif, défaut : … ».

Règles de contenu tenues par les exemples et à tenir dans les vrais textes : titres sans virgule ni point, aucun mot seul en fin de titre (coupures en `<br>` décidées), apostrophe typographique `’` dans tout texte visible (jamais dans un attribut, une URL ou du code ; dans un YAML entre apostrophes, `l’heure` plutôt que `l''heure`), espaces insécables du français (` ` avant `:` et `€`, ` ` avant `?`, `!`, `;` et dans `1 900`), aucun tiret cadratin, un texte de 12 mots ou plus jamais dans une étiquette ou une note en petit corps (plancher de 16 px, 18 px sur bureau), aucun chiffre, avis, logo ni fait sur une personne inventé hors démonstration.

## 4. Les moteurs

Tous sans dépendance, chargés une fois quel que soit le nombre de sections, et neutres sans JavaScript : la page reste lisible, complète et utilisable.

### reveal.js (toujours chargé)

| Attribut | Effet |
|---|---|
| `data-reveal-group` | conteneur : ses `[data-reveal]` entrent ensemble, à 0,1 s d’intervalle, quand son haut atteint ~85 % de l’écran |
| `data-reveal` = `""`, `up`, `left`, `right`, `scale`, `fade` | entrée en opacité et position seules, 0,8 s, courbe `cubic-bezier(0.2, 0.7, 0.2, 1)` |
| `data-count` | un nombre qui compte jusqu’à sa valeur une fois, s’il entre par le bas |

Classes posées : `html.rv-on` (le moteur a démarré et le mouvement est permis : seulement alors `base.css` masque ce qui attend), `.is-in` et `--rv-i` sur chaque élément entré. Sous `prefers-reduced-motion: reduce`, sans `IntersectionObserver` ou sans script : rien n’est masqué, rien ne compte.

### scroll.js (sections épinglées, rails, jonctions)

| Attribut ou classe | Effet |
|---|---|
| `html.sc-motion` | mouvement permis |
| `html.sc-pin` | mouvement permis et écran d’au moins 1101 × 720 px : le seul cas où une section s’épingle. Les mises en page épinglées s’écrivent sous `.sc-pin` |
| `[data-scroll-track]` | piste haute ; reçoit `--p` (0 à 1 : à travers la piste si épinglé, pendant la traversée de l’écran sinon, 1 en mouvement réduit), `--steps`, `data-step` |
| `[data-step-item]`, `[data-step-visual]` | `data-active` sur l’étape courante (épinglé seulement) ; `[data-step-current]` reçoit son numéro |
| `[data-rail]` + `[data-milestone]` | `--rail` (0 à 1) suit la ligne de lecture à 66 % de l’écran ; `data-reached="true"` sur les jalons passés ; plein en mouvement réduit |
| `.reading-progress` | fil de lecture, `--read` (spec : `theatre.progress`) |
| `data-exit="fade"`, `data-enter="fade"` / `"curtain"` | jonctions en fondu inversé ou rideau d’une bande sombre, épinglé seulement (`--exit`, `--enter`). Jamais sur le hero |

Événement : `landing:step` (sur la piste, `detail: { step, steps }`). Une partie révélée plus tard (porte de choix) est prise en compte à `landing:revealed`.

### offer.js (état de l’offre)

Lit `LANDING_CONFIG.offer` (spec `offer`). Le HTML montre toujours l’état ouvert ; le navigateur calcule l’état réel : `state` décidé par l’humain, ou `after_close` une fois `closes_at` passée.

| Attribut | Effet |
|---|---|
| `html[data-offer-state]` | `open`, `waitlist` ou `closed` |
| `[data-offer-show="waitlist closed"]` | visible seulement dans ces états (marqué `hidden` dans le HTML) |
| `[data-offer-countdown]` + `data-many` (« … {n} jours »), `data-one`, `data-zero` | jours restants ; sans script, la date statique reste. Jamais de secondes |
| `[data-offer-text-<état>]`, `[data-offer-href-<état>]`, `[data-offer-action-<état>]`, `[data-offer-disabled-<état>]` | texte, lien, action de formulaire ou désactivation dans cet état |

Événement : `landing:offer` (`detail: { state, days }`).

### forms.js (formulaires de capture)

Sur `form[data-form]` : contrôle des champs requis, de l’email et des cases obligatoires au submit, messages liés (`aria-invalid`, `aria-describedby`, `#<champ>-error`), focus sur la première erreur, `data-invalid` sur le formulaire refusé ; puis envoi en `fetch` (POST, FormData), confirmation dans la région `role="status"` (`[data-form-status]`), repli sur l’envoi natif si `fetch` échoue. Champ piège `.hp` : rempli, rien ne part. Messages : `data-error-required`, `data-error-email`, `data-error-consent`, `data-msg-success`, `data-msg-failure`, `data-msg-unwired`.

**Envoi de démonstration.** Un formulaire dont l’action est encore un marqueur `{{…}}` (ou vide) est marqué `data-demo` dès le chargement. À l’envoi valide, rien ne part sur le réseau, l’état de succès s’affiche (message `data-msg-success` suivi de `data-msg-unwired`) et la mesure compte `form_demo_submit` à la place de `generate_lead` : une démo ou un modèle pas encore branché ne gonfle jamais les leads.

**Consentement.** Recevoir la ressource demandée ne demande aucune case : l’envoi du formulaire vaut demande. Une inscription en plus (lettre, prochaine édition) passe par une case facultative, jamais pré-cochée, marquée `data-optin` (slot `optin` de `lead-capture` et `event-registration`) ; `generate_lead` porte alors `optin: true` ou `false`. Une case obligatoire (`consent_required` de `lead-capture`) ne sert que quand un consentement conditionne vraiment l’envoi. Les formulaires de démo, de rendez-vous ou de devis (`form`) n’ont pas de case : la demande fonde le traitement, et la mention de confidentialité, avec son lien, est toujours sous le bouton.

### viewer.js (visionneuse)

Un seul `<dialog>` modal, construit à la première ouverture et partagé par toutes les sections (`wall`, `work-wall`, ou tout lien qui porte l’attribut) : une image, une vidéo, un lecteur intégré ou du HTML tenu dans un `<template>`, seul ou en pages à feuilleter (« 2 / 6 »). Le contrat complet est en tête de `viewer.js`.

| Attribut | Effet |
|---|---|
| `data-viewer` = `""`, `image`, `video`, `iframe`, `html` | ouvre la visionneuse au clic (type deviné depuis la source si vide) |
| `href` ou `data-viewer-src` | la source ; `#id` désigne un `<template>` dont les `[data-viewer-page]` deviennent des pages |
| `data-viewer-pages` (+ `data-viewer-count`) | pages en images : un motif avec `{n}`, ou une liste d’URL |
| `data-viewer-group` | déclencheurs feuilletés ensemble, dans l’ordre de la page (les cachés sont sautés) |
| `data-viewer-title`, `data-viewer-caption`, `data-viewer-alt` | titre du dialogue, légende, texte de remplacement d’une image |
| `data-viewer-poster`, `data-viewer-captions` (`.vtt`), `data-viewer-captions-lang`, `data-viewer-crossorigin` | affiche et sous-titres d’une vidéo |
| `data-viewer-id` | identifiant envoyé avec `viewer_open` |
| `data-viewer-js` | déclencheur sans destination hors script (bouton, HTML en ligne) : `hidden` dans le balisage, le moteur le montre |

Comportement : `showModal()` (le reste de la page devient inerte), titre et légende liés, bouton de fermeture, Échap, flèches et Début / Fin dans une suite, balayage au doigt, défilement de la page bloqué, vidéo mise en pause et retirée à la fermeture, focus rendu au déclencheur. Précédent et suivant ne bouclent jamais. Styles injectés à la première ouverture (aucun fichier CSS de moteur, palette de la bande sombre). Mouvement réduit : ni fondu ni zoom, et la vidéo attend que le visiteur lance la lecture. **Neutre sans JavaScript** : les liens mènent au média. Événement `landing:viewer` (`detail: { open, type, id, pages }`) et mesure `viewer_open` ; API `window.landingViewer.open(déclencheur)`, `window.landingViewer.close()`.

### annotate.js (annotations à main levée)

Un trait irrégulier posé sur un mot ou une phrase et tracé une fois à son entrée à l’écran, à la couleur `--hl` (jamais l’accent du bouton de conversion). Balisage, dans un slot de type `html` : `<mark data-annotate="underline">deux mots</mark>`, avec `underline`, `highlight`, `strike`, `circle`, `box` (1 à 3 mots, sans retour à la ligne) ou `bracket`.

- **Dosage** : deux annotations par page au plus ; jamais dans un titre qui porte déjà un `.hl`.
- **Chargement** : déclaré par `evidence-chart` et `quote-interlude` ; ailleurs, ajouter `engines: [annotate]` à la spec.
- **Sans script**, ou sur une page qui ne charge pas le moteur : une emphase sobre en `--hl` (bloc réservé de `base.css`), jamais le surlignage jaune du navigateur.
- **Mouvement réduit** (ou sans `IntersectionObserver`) : le trait est posé d’emblée, sans tracé. Il se recalcule (sans se retracer) quand les lignes changent : redimensionnement, polices chargées, partie révélée par la porte de choix.

Classes posées : `html.an-on` (moteur actif), `.an-pending`, `.is-drawn`, `svg.an-svg` (calque décoratif `aria-hidden`).

### tracking.js (mesure)

`LANDING_CONFIG.tracking.mode` : `datalayer` (défaut, `dataLayer.push({ event, … })`), `gtm` (idem, conteneur GTM chargé par l’assembleur), `gtag` (`gtag('event', …)`, gtag.js chargé avec l’ID GA4 de la spec), `off` (rien ne part ; l’assembleur ne déclare alors aucun `dataLayer`, la QA vérifie seulement les crochets `data-track`). Rien ne quitte la page en mode `datalayer` sans balise : les événements attendent un conteneur.

| Événement | Déclencheur | Paramètres |
|---|---|---|
| `cta_click` | clic sur `data-track="cta_click"` (ou tout `data-cta` / `data-cta-position` sans `data-track`) | `cta_position`, `cta_label`, `cta_primary`, `link_url` |
| `generate_lead` | envoi valide d’un `form[data-track="generate_lead"]` | `form_id`, `lead_source`, `optin` (case `data-optin` cochée ou non), ses `data-track-<param>` (`participation`…) |
| `begin_checkout` | envoi du billet ou du ticket (`form[data-track="begin_checkout"]`) | `formula` (radio cochée, ou champ caché d’une formule unique), `value` (son `data-price`), `currency`, `items` (tableau GA4 lu dans `data-checkout-items`, JSON écrit par `bundle-receipt` : articles cochés ou pack) |
| `form_demo_submit` | envoi d’un formulaire dont l’action est encore un marqueur (`data-demo`), **à la place** de son événement | `form_event` (l’événement remplacé), `form_id`, et les paramètres de cet événement |
| `select_content` | choix dans la porte (`choice-gate`) ; demande choisie dans `demonstrator` (`replay`) | `content_type`, `content_id` |
| `select_content` | recommandation affichée (`recommender`) | `content_type` (son slot `param`), `content_id` (l’offre conseillée), `answers` (« question:réponse » séparés par des virgules) |
| `select_content` | filtre de `work-wall` | `content_type: filtre`, `content_id` (la valeur du filtre) |
| `viewer_open` | ouverture de la visionneuse (`viewer.js`) | `content_type` (image, video, iframe, html), `content_id` (`data-viewer-id`), `pages` |
| `demo_calculate` (slot `track_event`) | premier réglage du calculateur de `demonstrator`, une fois par chargement de la page | `content_type` (slot `track_type`), `content_id` (id de la section) |
| `faq_open` | ouverture d’une question | `question` |
| tout autre nom | clic sur un lien ou bouton `data-track="<nom>"`, ou appel de `window.landingTrack(nom, paramètres)` par une section | ses `data-track-<param>`, ou les paramètres passés |

Chaque événement porte aussi `page_slug` et les UTM de la visite (`utm_source`, `utm_medium`, `utm_campaign`, `utm_content`, `utm_term`, `gclid`), gardés le temps de la session. **Passage des UTM** : ajoutés aux liens de conversion sortants (`a[data-cta]`, `a[data-track]` absolus) et en champs cachés à chaque `form[data-track]` ; `data-utm="off"` exclut un lien ou un formulaire. `generate_lead` et `begin_checkout` se marquent comme conversions clés côté GA4 (action manuelle).

### Événements entre sections

| Événement (`document`) | Émis par | Écouté par |
|---|---|---|
| `landing:choice` (`detail: { param, value, label }`, plus `source: 'recommender'` quand il vient du recommandeur) | `choice-gate`, `recommender` | `offer-ticket` (coche la formule `value`) ; tout élément `[data-for="valeur …"]` est affiché ou masqué |
| `landing:revealed` | `choice-gate`, `recommender` (parties `gated` révélées) | `scroll.js` (nouvelles pistes), `topbar`, `chapters`, `annotate.js` (recalcul des traits) |
| `landing:offer` (`detail: { state, days }`) | `offer.js` | toute section qui doit suivre l’état (`bundle-receipt`, `event-registration`…) |
| `landing:sticky-bar` (`detail: { visible }`) | `sticky-bar` | `topbar` (sous 768 px, son bouton se retire tant que la barre mobile est visible) |
| `landing:viewer` (`detail: { open, type, id, pages }`) | `viewer.js` | toute section qui doit suivre la visionneuse |
| `landing:step` (sur la piste, `detail: { step, steps }`) | `scroll.js` | la section épinglée elle-même |

## 5. L’assemblage

- **Un seul fichier** par défaut (`assets: inline`) : `tokens.css`, `base.css`, puis le style de chaque fragment utilisé (une seule fois, même si le fragment sert deux fois) dans un `<style>` du `<head>` ; la configuration `window.LANDING_CONFIG` en tête ; les moteurs nécessaires puis les scripts des fragments en fin de `<body>`. `assets: link` pose des `<link>` et `<script src>` relatifs vers `templates/assets/` (prévisualisation dans le dépôt seulement : une page publiée est autonome).
- **Moteurs chargés** : `reveal` et `tracking` toujours ; `scroll`, `offer`, `forms`, `viewer`, `annotate` quand une section les déclare (`engines` de sa fiche) ou que la spec les force (`engines`), `offer` quand la spec a un `offer`, `scroll` quand elle a un `theatre.progress`. Ordre de chargement : reveal, scroll, offer, forms, viewer, annotate, tracking.
- **Page** : `<html lang>`, `<meta viewport>`, titre, description, `robots`, canonique, Open Graph, favicon, polices Google en `display=swap`, lien d’évitement vers `<main id="contenu">`, régions dans l’ordre `header` (barre du haut), `main` (sections et parties `gated`), `footer`, `after` (barre mobile).
- **Garde-fous** : l’assembleur n’écrit qu’un fichier ; il refuse une sortie dans un dossier `pilotage/` et n’y écrit ni n’y supprime jamais rien (il peut y lire une spec ou un fragment). La balise `<meta name="generator" content="assemble-landing.py · sha256:…">` porte l’empreinte de ce qu’il a écrit : une page retouchée à la main depuis (sections de builders insérées, micro-retouches) ou une page qu’il n’a pas produite n’est pas écrasée sans `--force`.
- **Contrôles** : `--check` (sortie 1 si la page ne correspond plus à la spec et aux fragments : c’est le test du catalogue), `--strict`, `--list`, `--describe`.

**Dans le playbook** (`.claude/skills/landing-page/SKILL.md`) : en phase 4, le contrôleur écrit `pilotage/page.json` et assemble le socle (sections de la bibliothèque remplies, `_placeholder` pour chaque section sur mesure) ; en phase 5, chaque builder écrit son fragment dans `pilotage/sections/<nn>-<id>.html`, et le contrôleur remplace l’entrée `_placeholder` par `file: sections/<nn>-<id>.html` puis réassemble (ou insère le fragment entre les marqueurs, s’il a retouché la page à la main entre-temps).

## 6. Les jetons et la base

- `assets/tokens.css` est généré par `python3 scripts/build-tokens.py` (cible déclarée dans `scripts/build-tokens.toml`) depuis `01-brand/tokens.json`. Avant le wizard, il porte la palette d’exemple neutre de `docs/placeholders.json` (bleu profond `#1E40AF`, ambre `#F59E0B`, ardoise `#0F172A`, blanc cassé `#F8FAFC`, Inter et JetBrains Mono). Les couleurs de texte dérivées (texte atténué, segment accentué des titres, texte du bouton de conversion, bordures de champs, erreurs) sont poussées jusqu’à leur contraste WCAG sur chacun de leurs fonds : changer la marque ne casse pas les contrastes.
- `assets/base.css` pose une **couche sémantique** que les sections lisent seule : `--ink`, `--paper`, `--surface`, `--surface-2`, `--muted`, `--hl` (segment accentué), `--tint`, `--tint-accent`, `--line`, `--line-strong`, `--focus`, `--gradient`. La classe `band-dark` repointe ces noms sur la palette sombre : une section fonctionne sur les deux fonds sans une ligne de plus.
- Rythme : `--wrap`, `--section-gap`, `--band-gap`, `--head-gap`, `--intro-gap`. Typographie fluide : `--t-h1` > `--t-display` > `--t-h2` > `--t-h3`, `--t-lead`, `--t-body` (16 px, 18 px dès 1024 px), `--t-small` (14 px, moins de 12 mots), `--t-label` (13 px, étiquettes). Points de rupture : 1280, 1100 (deux colonnes → une, épinglage dès 1101 × 720), 900, 768, 640.
- Composants : `.section`, `.wrap`, `.section-head` (`--center`), `.section-title`, `.section-intro`, `.hl`, `.lede`, `.label`, `.badge` (badges d’état, jamais au-dessus d’un titre), `.btn` (`--primary` : le seul accent fort, 19 px gras ; `--light` sur fond sombre ; `--secondary` ; `--block`), `.card` (`--lift`), `.list-check` (`.list-cross`), champs (`.field`, `.field__label`, `.field__input`, `.field__select`, `.field__hint`, `.field__error`, `.consent`, `.hp`, `.form-status`), `.sr-only`, `.skip-link`.
- **Kit d’objets composés** (`.obj` et `.obj-sheet`, `.obj-stack`, `.obj-window`, `.obj-head`, `.obj-mark`, `.obj-kpi`, `.obj-bars` / `.obj-bar`, `.obj-chart`, `.obj-grid`, `.obj-check`, `.obj-mail`, `.obj-avatar`, `.obj-lines`, `.obj-chip`, `.obj-stamp`, `.obj-highlight`, `.obj-strike`) : de quoi composer un objet de hero, une scène ou un visuel de constat sans CSS nouveau. Toujours dans un conteneur `aria-hidden="true" data-qa-decor` : le sens est porté par le vrai texte à côté.
- **Notes en marge** (bloc réservé de `base.css`, principe de Tufte CSS, MIT) : la source d’un chiffre ou une précision s’écrit dans la phrase qu’elle documente, juste après la ponctuation, dans un `<p>` ou un `<li>` d’un slot de type `html` :

  ```html
  <span class="note"><span class="note__body" role="note">Source : enquête de 2026, 412 répondants.</span></span>
  ```

  Dès 1101 px, dans un `.wrap.wrap--notes`, la colonne de texte garde une mesure de `--note-measure` et la note flotte dans la marge droite (`--note-w`, `--note-gap`), au corps courant ; ailleurs (petit écran, section sans `.wrap--notes`), elle s’ouvre en bloc numéroté sous la ligne de son appel. L’appel et le numéro viennent d’un compteur de page masqué aux aides techniques : la note est lue en place, annoncée comme note. Aucun script, identique en mouvement réduit. `.wrap--notes` réserve la marge sur tout le `.wrap` : il ne convient qu’à une section dont le `.wrap` porte une seule colonne de texte (section sur mesure, par exemple). Aucun fragment de la bibliothèque ne le pose encore ; dans leurs slots `html`, la note s’ouvre donc sous sa ligne.
- **Jauge narrative** (`.gauge`, `.gauge--step`, `.gauge--live`, `.gauge__label`) : où en est le lecteur, dans l’unité du récit (« Semaine 3 sur 6 »). Elle se remplit par le champ facultatif `gauge` de chaque élément de `journey` (`steps[].gauge`) et de `program` (`modules[].gauge`), en HTML de phrase avec la valeur en `<b>` (« Atelier <b>3</b> sur 6 ») : tous les éléments ou aucun. `.gauge--step` précède le moment de chaque étape partout où le théâtre ne tourne pas ; sous `.sc-pin`, `.gauge--live` porte une étiquette par étape dans la marge gauche et montre celle de l’étape active, par le rang, sans script. Décorative (`aria-hidden="true" data-qa-decor`) : elle double le moment et le titre, jamais une information absente du texte.
- **Police de lecture facultative** : `--font-editorial`, une police de texte (souvent à empattements) que `tokens.css` ne génère pas. `letter` la lit avec un repli sur la police du corps (`var(--font-editorial, var(--font-body, var(--font-display)))`) : sans elle, la lettre garde la police de la page. À déclarer dans la marque seulement si elle en a une.

## 7. Écrire un nouveau fragment

Un besoin qui revient sur deux pages devient un fragment (règle « réutiliser avant de créer »). Structure de `sections/<nom>.html` :

```html
<script type="application/json" data-section-meta>
{
  "id": "<nom>",                       // = nom du fichier
  "name": "…", "objection": "…", "when": "…", "avoid": "…", "reduced_motion": "…",
  "region": "main",                    // header | main | footer | after
  "engines": ["scroll"],               // moteurs nécessaires, facultatif
  "slots": { "title": {"type": "html", "doc": "…", "example": "…"}, … }
}
</script>
<style data-section-style="<nom>">
.s-<nom> { … }                         /* sélecteurs préfixés .s-<nom>, variables sémantiques seules */
</style>
<!-- section:{{id}} -->
<section id="{{id}}" class="s-<nom> section" aria-labelledby="{{id}}-titre" data-section="<nom>">
  <div class="wrap">
    <div class="section-head"><h2 id="{{id}}-titre" class="section-title">{{{title}}}</h2></div>
    …
  </div>
</section>
<!-- /section:{{id}} -->
<script data-section-script="<nom>">
(function () { document.querySelectorAll('.s-<nom>').forEach(function (s) { … }); })();
</script>
```

**Transitions d’état (View Transitions).** Un changement d’état dans la page (porte de choix, bascule mensuel / annuel, recommandeur, filtre du mur de réalisations) peut passer par `document.startViewTransition`, jamais sous `prefers-reduced-motion: reduce` ni sans l’API (l’état change alors d’un coup), et jamais pendant la saisie d’un champ. Les `view-transition-name` se posent seulement le temps de la transition, sur les deux ou trois éléments qui doivent se répondre, puis se retirent (`.finished`) : deux éléments de même nom sur la page font échouer la transition. Seules exceptions, les barres fixes (`topbar`, `sticky-bar`) gardent un nom permanent `vt-<id>`, unique par construction, pour rester immobiles pendant toute transition de la page. Sous `reduce`, `::view-transition-group(*)` et ses paires perdent leur animation. Pas de « types » de transition (absents de Firefox).

Conventions : style et script valent pour toutes les instances de la page (ils sont émis une fois) ; aucune couleur ni police en dur (`grep -nE "#[0-9a-fA-F]{3,8}|rgba?\("` vide) ; en-tête en `<div class="section-head">`, sans pastille de sur-titre ; listes stylées en `role="list"` ; entrées par `data-reveal` ; mise en page épinglée sous `.sc-pin`, état final visible sans script et en mouvement réduit ; CTA avec `data-track` et `data-cta-position`, `{{#primary}} data-cta="primaire"{{/primary}}` sur un CTA de conversion ; textes de 12 mots et plus au corps courant. Puis : ajouter la section à `catalogue.json`, réassembler le catalogue, `qa-landing.py` à zéro erreur, `python3 -m pytest scripts/tests/test_assemble_landing.py -q`.

## 8. QA du catalogue et des modèles

`python3 05-web-content/scripts/qa-landing.py 05-web-content/templates/sections/catalogue.html` : **0 erreur**, 7 avertissements assumés, tous `cta-hors-objectif` : le catalogue montre côte à côte des conversions qu’une vraie page n’aurait pas ensemble (les trois boutons de la grille tarifaire, le ticket à la carte, le formulaire de capture, le formulaire qualifiant, l’inscription à l’événement). Une page réelle n’en garde qu’une. La QA relève jusqu’à 3 000 textes par écran (`--max-textes`) : le catalogue, le plus long des documents, en compte un peu plus de 2 000 et passe en entier, sans avertissement `troncature`.

Les six modèles (`landing-pages/specs/*.yaml`) s’assemblent avec `--strict` sans avertissement et passent la QA à **0 erreur** ; leurs avertissements restants sont les marqueurs à brancher (`placeholder`, `cta-destination`).

**Passe de mesure de la QA.** Quand la page déclare un suivi, la QA clique chaque CTA primaire ; pour un bouton d’envoi, elle remplit les champs requis avec des valeurs de test (`prenom@example.com`, nom, URL, première option d’une liste), coche les cases requises et envoie le formulaire. Toute requête qui quitte la page est interceptée par Playwright et reçoit un 200 vide : rien ne part réellement. Elle attend `generate_lead` (ou `begin_checkout`) d’un endpoint réel, `form_demo_submit` d’un endpoint en marqueur, et signale en erreur une démo comptée comme lead ou partie sur le réseau.

Ce que la bibliothèque ne couvre pas encore (à construire sur mesure, puis à verser ici) : le comparateur avant / après (seulement quand la transformation se voit), les photos passées à l’encre de la marque en duotone, les états d’illustration pilotés par le défilement.
