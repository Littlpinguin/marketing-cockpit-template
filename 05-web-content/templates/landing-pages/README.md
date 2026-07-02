# Galerie — templates de landing pages

10 modèles HTML single-file, un par objectif de conversion. Chaque fichier est autonome (CSS + JS inline), responsive (breakpoints 900/600/400 px, à tester à 375 et 1280 px), sémantique et accessible, avec :

- le **bloc de tokens de marque** de `../../sections-library.md` en tête de `<style>` — avec les **valeurs de démo « Meridian Conseil »** (vert profond `#2f6f5e`, laiton `#c8a24b`, Fraunces + Inter en fallback système) et le mapping vers les tokens `{{BRAND_*}}` en commentaire : chaque fichier ouvert tel quel dans un navigateur est une **démo finie**, et le wizard `/start-copilot` (ou la skill `landing-page`) remplace ces valeurs par celles de `01-brand/style-guide.md`, jamais d'ailleurs ;
- une **direction artistique par modèle** (colonne « Ambiance » ci-dessous) déclinée du même langage Meridian : display serif à contrastes marqués, hairlines, grain discret, motif signature de méridiens (`#mrd-mark` / `#mrd-globe` / `#mrd-topo` en SVG inline), révélation au scroll sobre (désactivée si `prefers-reduced-motion`) ;
- des **sections issues de `sections-library.md`** (hero, logos, problème, bénéfices, stats, témoignages, process, pricing, compare, FAQ, capture, CTA final) ;
- un **formulaire branché sur `{{FORM_ENDPOINT}}`** avec attributs `data-track` (`generate_lead`, `cta_click`) conformes aux conventions UTM/GA4 de la skill `landing-page` ;
- un **commentaire « À PERSONNALISER »** en tête de fichier listant exactement quoi remplacer ;
- des **contenus d'exemple 100 % fictifs** (« Meridian Conseil », cabinet de conseil climat inventé — mêmes conventions que `_examples/deck-catalogue/`) : à réécrire via les skills `copywriting` + `copy-editing`, jamais à publier tels quels.

Aucune image externe : mockups et pictos sont des SVG inline à remplacer par de vrais visuels (WebP) au moment de la production.

## Choisir son modèle

| Modèle | Objectif de conversion | Ambiance de démo (Meridian) | Quand le choisir | Sections incluses |
|---|---|---|---|---|
| `demo-b2b.html` | Demande de démo | **Clair éditorial** — hero split asymétrique, mockup dashboard, bande de stats sombre | Vente B2B assistée, cycle avec commercial, produit à montrer | Topbar CTA, hero split + mockup, logos, problème, bénéfices, stats, témoignages, process « après le formulaire », formulaire qualifiant (email + entreprise + effectif), FAQ, CTA final |
| `essai-saas.html` | Création de compte d'essai | **Clair tinté frais** — fond crème, product-shot incliné qui déborde, chips « sans CB » | SaaS self-service, activation sans vendeur, friction minimale | Hero centré + badges « sans CB » + product shot, logos, avant/après, bénéfices, témoignages, formulaire email seul, FAQ fin d'essai, CTA final |
| `lead-magnet.html` | Téléchargement contre email | **Crème éditorial** — couverture de guide SVG sombre aux méridiens laiton, sommaire numéroté serif | Capture d'un guide/checklist ; trafic social ou newsletter | Hero 2 colonnes avec formulaire **au-dessus du pli** + mockup couverture, sommaire, bénéfices, témoignage + bio auteur, CTA final — **pas de topbar** (zéro fuite) |
| `webinar.html` | Inscription à un événement | **Sombre premium** — hero nuit à halos, compte à rebours serif laiton, corps clair | Webinar, atelier en ligne, live — inscription datée | Hero sombre date/heure + compte à rebours JS + formulaire au-dessus du pli, « vous repartirez avec », agenda minuté, intervenants, preuve d'édition précédente, CTA replay |
| `prestation-service.html` | Rendez-vous découverte | **Éditorial luxe clair** — grandes marges, timeline hairline, étude de cas en bande sombre | Conseil, agence, prestation packagée à ticket élevé | Hero résultat, problème (défauts du marché), méthode semaine par semaine, livrables, étude de cas, témoignages, offre forfaitaire unique, formulaire qualifié, FAQ |
| `comparateur-concurrent.html` | Démo (intention « alternative à X ») | **Factuel premium** — tableau à thead sombre, zébrures subtiles, différences numérotées | Trafic SEO/SEA sur les requêtes de comparaison ; audience en phase d'évaluation | Hero comparatif honnête, 3 différences, tableau factuel daté, témoignages de switchers, process de migration, FAQ migration, formulaire « outil actuel » |
| `tarifs.html` | Choix d'un plan / entrée en essai | **Clair tinté confiance** — zone pricing crème, plan recommandé en carte sombre surélevée | Page pricing pérenne (à passer en `index`) ; prix = offre validée uniquement | Hero court, toggle mensuel/annuel JS, 3 plans + plan recommandé, garantie, tableau détaillé, témoignages « valeur », FAQ tarifaire, capture « grille détaillée », CTA essai |
| `vente-longue.html` | Achat / candidature directe | **Récit éditorial crème** — mesure 68ch, lettrine, séparateurs méridiens, prix en carte sombre | Programme, formation, offre à ticket moyen vendue sans commercial | Hero promesse, récit long-form (problème → agitation → mécanisme), stack de valeur avec ancrage, garantie, preuve massive, urgence honnête (cohorte datée), FAQ exhaustive, candidature — CTA répété 5× |
| `one-pager-local.html` | Appel téléphonique / rappel | **Chaleureux local** — crème + vert, carte de zone SVG stylisée à pastille pulsante | Service local, zone de chalandise, trafic Google Business / SEO local | Hero service + ville, NAP + horaires, 3 services, zone d'intervention + carte SVG, avis localisés, formulaire de rappel, FAQ locale, **barre d'appel collante mobile**, schema LocalBusiness commenté |
| `waitlist-lancement.html` | Inscription liste d'attente | **Nuit premium** — full dark à halos, globe méridien géant en filigrane, timeline laiton | Pré-lancement produit, bêta privée, validation de demande | Hero sombre plein écran + formulaire email seul, 3 privilèges (accès anticipé, tarif fondateur, coulisses), teaser 3 promesses, calendrier de lancement, compteur social à brancher |

## Patterns CRO appliqués (recherche 2025-2026)

Constantes observées sur les pages qui convertissent le mieux (Unbounce, KlientBoost, teardowns B2B SaaS) et appliquées à tous les modèles :

1. **Hero court** : bénéfice + spécificité en une phrase, sous-titre « pour qui / comment », UN CTA primaire, micro-preuve immédiate. Test des 5 secondes obligatoire.
2. **Preuve avant argumentation** : logos/chiffre juste sous le hero, preuve près de chaque CTA.
3. **Un objectif par page** : CTA identique du hero au final ; pas de navigation complète (logo + CTA suffisent).
4. **Rythme** : alternance argument → preuve → réassurance ; FAQ = objections réelles ; section « que se passe-t-il après le formulaire » sur les pages à formulaire engageant.
5. **Formulaire minimal** : chaque champ au-delà de l'email doit payer sa friction en qualification.
6. **Message match** : le message de la page prolonge celui de la source de trafic (voir brief, skill `landing-page`).

## Workflow d'utilisation

1. Copier le modèle vers `05-web-content/landing-pages/<slug>/index.html`.
2. Dérouler la skill `landing-page` (brief → copy → design sous tokens → tracking → QA → brand-check). Le template fournit la structure ; il ne remplace aucune étape.
3. Remplacer tokens, contenus fictifs, chiffres (messaging framework uniquement), SVG placeholders.
4. `noindex` par défaut (campagne) — passer en `index` pour tarifs, comparateur et one-pager local si pérennes.
5. Enregistrer dans `deployed.md` (URL, UTM, métrique de succès).
