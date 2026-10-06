# Modèles de landing pages

Six modèles, un par archétype de page de conversion. Chacun existe en deux fichiers :

- `specs/<modèle>.yaml` : la spec, c'est-à-dire la liste des sections de la bibliothèque `../sections/` dans l'ordre du récit, avec leurs textes (slots). Son en-tête en commentaire raconte la page section par section (l'objection que chacune traite), les marqueurs à brancher, l'état de l'offre et la mesure ;
- `<modèle>.html` : la page autonome qu'en tire `05-web-content/scripts/assemble-landing.py` (un seul fichier, styles et moteurs en ligne). Elle s'ouvre telle quelle dans un navigateur. Ne pas l'éditer à la main : on corrige la spec, puis on réassemble.

Les couleurs et polices viennent de `../assets/tokens.css`, généré depuis `01-brand/tokens.json` : avant le wizard, la palette d'exemple neutre ; après, celle de la marque, sans toucher aux modèles. Le rendu de chaque section, avec sa fiche (objection, quand l'utiliser, quand l'éviter, slots), se voit dans `../sections/catalogue.html`.

**Tout le contenu est fictif** : chaque modèle a sa marque inventée, et ses personnes, avis, chiffres, prix et dates le sont aussi, marqués comme tels sur la page (« avis fictif », « chiffre d'exemple », « personnage fictif »). Les seuls faits réels sont des références légales vérifiées, citées avec leur texte (article, loi, directive) : à revérifier au moment d'adapter.

## Choisir son modèle

| Modèle | Archétype | Conversion (événement de mesure) | Marque fictive |
|---|---|---|---|
| `formation` | Formation payante en cohorte datée, atelier | Billet en GET vers l'outil de vente, deux formules (`begin_checkout`) | Ferlane Formation, organisme qui forme les TPE aux marchés publics |
| `vente-longue` | Offre grand public achetée en ligne, page longue | Ticket à l'unité ou saison complète, en GET vers le paiement (`begin_checkout`, avec les articles) | Terre Voisine, programme saisonnier de potager en carré |
| `lead-magnet` | Ressource gratuite contre un email | Formulaire de capture, case facultative pour la lettre (`generate_lead`) | Encaisse, kit de relance des factures pour indépendants |
| `demo-b2b` | Logiciel vendu avec démonstration | Formulaire qualifiant de demande de démo (`generate_lead`) | Calquai, logiciel de rendez-vous de quai pour entrepôts |
| `prestation` | Prestation de service sur devis | Formulaire de demande de devis (`generate_lead`) | Ouvrance, cabinet d'audit d'accessibilité numérique |
| `evenement` | Événement gratuit sur place et en ligne, webinar | Inscription, mode de participation au choix (`generate_lead`, avec `participation`) | Brivalle, éditeur de logiciel de tournées, et sa matinale |

Chaque page a **une seule conversion** : tous les boutons marqués `data-cta="primaire"` (barre du haut, hero, carte de la FAQ, CTA final, barre mobile) mènent au même bloc. Au plus trois sections épinglées, jamais deux d'affilée sauf le couple problème → pivot ; une ou deux bandes sombres plus le CTA final, jamais deux d'affilée (règles de page : `../sections/README.md` § 1).

## Les six modèles en détail

Les sections sont données dans l'ordre de la page, sous la forme `fragment #id` (l'id est l'ancre de la section).

### formation

- **Sections** : topbar, hero, facts-grid #essentiel, problem-pinned #probleme, letter #lettre, program #programme, quote-interlude #parole, showcase-dark #kit, people #formateurs, testimonials #avis, for-whom #pour-qui, offer-ticket #offre, faq #questions, legal #mentions, final-cta #final, footer #pied, sticky-bar #barre-mobile.
- **À brancher** : `{{URL_CHECKOUT}}`, `{{URL_LISTE_ATTENTE}}`, `{{URL_MENTIONS_LEGALES}}`, `{{URL_CONFIDENTIALITE}}`, l'adresse de contact.
- **Mécaniques** : fiche pratique collée au hero, titre lu par les lecteurs d'écran seulement, dont l'effectif suit l'état de l'offre ; lettre signée de la formatrice juste après le problème (lettrine, paragraphe qui s'encre au défilement, sans signature tracée puisque la personne est fictive) ; citation en respiration avec une annotation à main levée ; billet à deux formules avec remise datée ; état de l'offre (ouverte, liste d'attente, close) et jours restants calculés dans le navigateur.

### vente-longue

- **Sections** : topbar, hero, chapters #sommaire, proof-band #preuves, problem-pinned #probleme, pivot, showcase-dark #kit, journey #parcours, outcomes #resultats, wall #avis, comparison #comparatif, for-whom #pour-qui, bundle-receipt #offre, guarantee #garantie, faq #questions, final-cta #final, footer #pied, sticky-bar #barre-mobile.
- **À brancher** : `{{URL_CHECKOUT}}`, `{{URL_LISTE_ATTENTE}}`, `{{URL_CGV}}`, `{{URL_MENTIONS_LEGALES}}`, `{{URL_CONFIDENTIALITE}}`, l'adresse de contact, les sources du mur d'avis (vidéo, sous-titres).
- **Mécaniques** : sommaire de sept chapitres, puis rail dans la marge ou barre « Chapitre n sur 7 » qui suit la lecture (chaque chapitre vise un id de la page : renommer un id, c'est corriger le sommaire) ; trois épinglages, dont le couple problème → pivot ; jauge « Lettre n sur 32 » sur le parcours ; mur de douze avis dont six repliés, note moyenne avec effectif et source, témoignage vidéo sous-titré avec transcription ; ticket de caisse qui se remplit à chaque case et propose la saison complète dès qu'elle revient moins cher ; garantie juste après le ticket.

### lead-magnet

- **Sections** : topbar, hero, lead-capture #recevoir, program #contenu, evidence-chart #preuve, for-whom #pour-qui, people #auteures, faq #questions, final-cta #final, footer #pied.
- **À brancher** : `{{FORM_ENDPOINT}}`, `{{URL_MENTIONS_LEGALES}}`, `{{URL_CONFIDENTIALITE}}`, l'adresse de contact.
- **Mécaniques** : formulaire tôt dans la page, un seul champ, sans case obligatoire (la demande vaut envoi) ; inscription à la lettre en case facultative, jamais pré-cochée ; programme des six relances sur un rail avec une page du kit en spécimen ; un chiffre, un graphique en barres et sa source, la valeur mise en avant entourée à main levée.

### demo-b2b

- **Sections** : topbar, hero, proof-band #preuves, problem-pinned #probleme, outcomes #changements, journey #parcours, demonstrator #estimation, showcase-dark #securite, ownership-diagram #donnees, testimonials #avis, process #ensuite, form #demo, faq #questions, final-cta #final, footer #pied, sticky-bar #barre-mobile.
- **À brancher** : `{{FORM_ENDPOINT}}`, `{{URL_MENTIONS_LEGALES}}`, `{{URL_CONFIDENTIALITE}}`, l'adresse de contact.
- **Mécaniques** : deux épinglages séparés par une respiration ; calculateur d'attente évitée, avec son hypothèse et sa source sous le résultat (mesuré en `demo_calculate`, jamais compté comme conversion) ; dossier technique pour la DSI en bande sombre ; schéma de propriété des données (ce que le client possède, ce qui s'y branche, les preuves de sortie) ; formulaire sans case de consentement, la mention de confidentialité sous le bouton.

### prestation

- **Sections** : topbar, hero-image-title, problem-evidence #probleme, program #methode, work-wall #realisations (bande sombre), quote-interlude #parole, people #equipe, for-whom #pour-qui, recommender #perimetre, pricing-table #tarifs, form #devis, faq #questions, final-cta #final, footer #pied, sticky-bar #barre-mobile.
- **À brancher** : `{{FORM_ENDPOINT}}`, `{{URL_MENTIONS_LEGALES}}`, `{{URL_CONFIDENTIALITE}}`, l'adresse de contact.
- **Mécaniques** : hero dont le titre porte une pastille, ici la voix d'un lecteur d'écran ; problème en pièces à conviction, titre collant et tampon de verdict, avec une note en marge qui cite la référence légale de la déclaration d'accessibilité ; mur de huit réalisations en index filtrable par secteur, dossiers à feuilleter dans la visionneuse ; citation d’une cliente en respiration, sur fond clair, juste après le mur ; recommandeur en trois questions au plus, puis grille de trois périmètres avec prix « dès » ; aucune section épinglée.

### evenement

- **Sections** : topbar, hero-editorial, outcomes #rapporter, program #programme, people #intervenants, map-pinned #acces, testimonials #avis, for-whom #pour-qui, event-registration #inscription (bande sombre), faq #questions, legal #pratique, final-cta #final, footer #pied, sticky-bar #barre-mobile.
- **À brancher** : `{{FORM_ENDPOINT}}`, `{{URL_ITINERAIRE}}`, `{{URL_MENTIONS_LEGALES}}`, `{{URL_CONFIDENTIALITE}}`, l'adresse de contact.
- **Mécaniques** : hero éditorial, très grand titre sur un filet tracé, puis la ligne de faits (quand, où, programme, prix) ; programme minuté avec un spécimen du cahier remis ; carte des accès tracée au défilement (seul épinglage) ; inscription sur place ou en ligne, l'option sur place se désactive quand la salle est pleine. L'en-tête de la spec décrit les variantes 100 % en ligne (webinar), 100 % sur place et payante.

## Adapter un modèle

1. **Copier la spec** du modèle le plus proche vers `05-web-content/landing-pages/<slug>/pilotage/page.yaml`, puis changer `output` (`05-web-content/landing-pages/<slug>/index.html`), `page` (le slug envoyé avec chaque événement de mesure), `title`, `description`, `og`, `offer` et `tracking`.
2. **Réécrire les slots** avec la vraie matière (skills `copywriting` puis `copy-editing`, doctrine de `01-brand/`) : chaque texte, chaque chiffre avec sa source, chaque objet composé remplacé par un vrai document ou une vraie image. Retirer une section, en ajouter une de la bibliothèque (`python3 05-web-content/scripts/assemble-landing.py --list`, puis `--describe <fragment>` pour ses slots) ou réserver une place à une section sur mesure (`use: _placeholder`). Garder les règles de page et les ancres : chaque `#id` visé par un bouton, le sommaire ou la carte de la FAQ doit exister.
3. **Assembler** : `python3 05-web-content/scripts/assemble-landing.py 05-web-content/landing-pages/<slug>/pilotage/page.yaml --strict`. `--strict` échoue tant qu'un slot prend son texte d'exemple : rien de fictif ne part par oubli.
4. **Contrôler** : `python3 05-web-content/scripts/qa-landing.py 05-web-content/landing-pages/<slug>/index.html`, à zéro erreur. Puis la suite de la skill `landing-page` : revues, brand-check, enregistrement dans `05-web-content/deployed.md`.

Pour regénérer un modèle après une modification de la bibliothèque : `python3 05-web-content/scripts/assemble-landing.py 05-web-content/templates/landing-pages/specs/<modèle>.yaml --strict`, puis `--check` (sortie 1 si la page ne correspond plus à sa spec) et la QA. Les six modèles s'assemblent sans avertissement et passent la QA à zéro erreur ; leurs avertissements restants sont les marqueurs à brancher.

## Marqueurs à brancher

Les liens qui dépendent du site réel restent des marqueurs du dépôt en majuscules, entre doubles accolades : `{{URL_CHECKOUT}}`, `{{URL_LISTE_ATTENTE}}`, `{{URL_CGV}}`, `{{URL_MENTIONS_LEGALES}}`, `{{URL_CONFIDENTIALITE}}`, `{{URL_ITINERAIRE}}`, `{{FORM_ENDPOINT}}` (liste et description dans `docs/placeholders.json`). L'assembleur ne les interprète jamais, la QA les signale jusqu'à la publication, et un formulaire dont l'action est encore un marqueur ne part pas : l'envoi affiche un message de démonstration et la mesure compte `form_demo_submit`, jamais `generate_lead`. Les adresses de contact sont sur le domaine réservé `example.com`. Robots `noindex, nofollow` par défaut ; `index, follow` avec `canonical` pour une page pérenne.

## Migration

Les sept anciens modèles écrits à la main (`comparateur-concurrent`, `essai-saas`, `one-pager-local`, `prestation-service`, `tarifs`, `waitlist-lancement`, `webinar`) ont été retirés : ils restent dans l'historique git. Leurs archétypes se recomposent avec la bibliothèque :

| Ancien modèle | Repartir de |
|---|---|
| `webinar` | `evenement`, variante 100 % en ligne décrite dans l'en-tête de sa spec |
| `prestation-service` | `prestation` |
| `tarifs`, `essai-saas` | `demo-b2b`, en remplaçant le formulaire par `pricing-table` (bouton `primary` sur le plan recommandé) et `comparison` |
| `comparateur-concurrent` | `demo-b2b` avec `comparison` (tableau daté, catégories plutôt que marques tant que la comparaison n'est pas vérifiée) |
| `waitlist-lancement` | `lead-magnet`, la capture devenant l'inscription à la liste d'attente |
| `one-pager-local` | `prestation`, avec `map-pinned` pour la zone d'intervention et `form` pour le rappel |
