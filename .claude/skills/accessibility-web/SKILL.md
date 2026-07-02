---
name: accessibility-web
description: Référentiel accessibilité web WCAG 2.2 AA pour {{COMPANY_NAME}} — structure et alternatives textuelles, ARIA, clavier et focus, modales, formulaires, contrastes, contenus dynamiques, tableaux, liens. À charger avant de construire ou de relire tout livrable HTML (landing pages 05-web-content/, dashboard 11-reporting/) et pour toute question a11y. La revue automatisée avant livraison est déléguée à l'agent a11y-auditor. Enjeu légal : European Accessibility Act applicable depuis juin 2025.
---

# accessibility-web — référentiel WCAG 2.2 AA {{COMPANY_NAME}}

> Contenu vendorisé et condensé depuis **accessibility-agents** v6.0.0 de Community-Access / Taylor Arndt (MIT) — sous-ensemble web uniquement (10 agents spécialistes sur 80) — voir `docs/vendored-content.md`. Sources d'autorité : [WCAG 2.2](https://www.w3.org/TR/WCAG22/), [ARIA APG](https://www.w3.org/WAI/ARIA/apg/), [axe-core](https://github.com/dequelabs/axe-core).

**Pourquoi c'est bloquant** : l'European Accessibility Act s'applique depuis le 28 juin 2025 aux produits et services numériques vendus dans l'UE (e-commerce inclus). Un livrable web inaccessible est un risque légal, pas seulement un défaut de qualité. Les skills `landing-page` et les pages du dashboard `11-reporting/` passent une revue a11y avant livraison (agent `a11y-auditor`).

## Première règle (avant tout ARIA)

**Ne pas utiliser ARIA si le HTML natif exprime la sémantique.** `<button>` bat `<div role="button">` ; `<dialog>` bat `<div role="dialog">`. Un ARIA incorrect est pire que pas d'ARIA : il casse activement l'expérience lecteur d'écran. Ne jamais ajouter de rôle redondant (`<nav role="navigation">`, `<button role="button">`…). Exception : plusieurs `<nav>` sur une page → `aria-label` distincts.

## 1. Structure, titres, alternatives textuelles (WCAG 1.1.1, 2.4.6)

- Hiérarchie de titres sans saut (H1 unique → H2 → H3) ; landmarks (`<header>`, `<nav>`, `<main>`, `<footer>`) ; `<title>` de page descriptif ; attribut `lang` correct.
- **Toute image a un `alt`** : descriptif si porteuse de sens (regarder l'image et vérifier que l'alt correspond réellement au contenu) ; `alt=""` si décorative (jamais d'alt absent) ; description longue pour les graphiques/données (figure + figcaption ou texte adjacent).
- SVG : `role="img"` + `<title>` si signifiant, `aria-hidden="true"` si décoratif. Icônes seules : nom accessible obligatoire.
- Ne jamais porter un message clé uniquement par une image (croise la règle email/brand-check du template).

## 2. Clavier et focus (WCAG 2.1.1, 2.4.3, 2.4.7)

- **Tout ce qui ne s'atteint pas, ne s'opère pas ou ne s'échappe pas au clavier seul ne marche pas.**
- Ordre de tabulation = ordre du DOM = ordre visuel. **Jamais de `tabindex` > 0.** `tabindex="0"` avec parcimonie ; `tabindex="-1"` pour le focus programmatique.
- Indicateur de focus toujours visible (grep les `outline: none` / `outline: 0` sans remplacement) — contraste 3:1 contre le composant ET le fond.
- SPA / changements de vue : déplacer le focus sur le titre de la nouvelle vue (`tabindex="-1"` + `focus()`), annoncer le changement.
- Skip link en premier élément focusable ; pas de piège au clavier (sauf modale, voir §4).

## 3. ARIA sur les widgets courants (WAI-ARIA 1.2, APG)

- **Tabs** : `role="tablist"` (+ `aria-label`) ; chaque onglet = `<button role="tab" aria-selected>` ; navigation aux flèches, un seul tab dans l'ordre de tabulation (`tabindex="-1"` sur les inactifs) ; panneaux `role="tabpanel"` + `aria-labelledby`.
- **Accordéons** : bouton avec `aria-expanded` + `aria-controls`.
- **États dynamiques** : `aria-expanded`, `aria-selected`, `aria-checked`, `aria-current` maintenus en JS — un ARIA statique menteur est un bug bloquant.

## 4. Modales et overlays (APG Dialog Pattern)

- **Toujours l'élément natif `<dialog>`** (`role="dialog" aria-modal="true" aria-labelledby="titre"`), jamais des `<div>` sauf contrainte documentée.
- Focus à l'ouverture selon le contenu : confirmation destructive → focus sur l'action la moins destructive (Annuler) ; contenu long → focus sur le titre (`tabindex="-1"`) ; défaut → premier élément focusable.
- Focus piégé dans la modale tant qu'elle est ouverte ; **Échap ferme et rend le focus au déclencheur** ; déclencheur avec `aria-haspopup="dialog"` ; titre de modale en H2 ; arrière-plan inerte.

## 5. Formulaires (WCAG 3.3, 1.3.5)

- **Chaque champ a un `<label for>` associé** (le clic sur le label active le champ — ce qu'`aria-label` ne fait pas). Jamais le `placeholder` comme seul label.
- `autocomplete` sur les champs d'identité (email, name, tel…) ; champs requis indiqués par le texte + `required`/`aria-required` (pas seulement une astérisque colorée).
- Erreurs : message textuel explicite lié au champ (`aria-describedby`), `aria-invalid="true"`, focus déplacé sur la première erreur ou récapitulatif en tête ; jamais la couleur seule.
- Groupes radio/checkbox dans `<fieldset>` + `<legend>` ; feedback de soumission annoncé (voir §7).

## 6. Contrastes et visuel (WCAG 1.4.3, 1.4.11, 2.4.13)

- Texte normal (< 18 px, ou < 14 px gras) : **4,5:1 minimum** — y compris placeholders, légendes, texte secondaire (« c'est juste une caption » n'est pas une excuse).
- Grand texte (≥ 18 px ou ≥ 14 px gras) : 3:1.
- Non-texte 3:1 : bordures de champs, icônes signifiantes, indicateurs de focus, limites de composants.
- Jamais la couleur seule pour porter l'information (statut, erreur, courbe de graphe → doubler d'un motif, libellé ou icône).
- Dark mode : re-vérifier tous les ratios dans les deux thèmes ; respecter `prefers-reduced-motion` (pas d'animation essentielle non désactivable) et `prefers-color-scheme`.
- Ces seuils recoupent l'agent `qa-visuel` (livrables 1920×1080 / carrousels) : `qa-visuel` couvre les decks projetés, `a11y-auditor` couvre les pages web.

## 7. Contenus dynamiques (live regions)

- Toasts / confirmations / états de chargement : `role="status"` (`aria-live="polite"`) pour l'informel, `role="alert"` (`assertive`) pour les erreurs bloquantes uniquement.
- La live region doit exister dans le DOM **avant** l'injection du message ; ne pas abuser d'`assertive` (interrompt la lecture).
- Résultats de recherche / filtres : annoncer le nombre de résultats.

## 8. Tableaux de données

- `<table>` sémantique avec `<th scope="col|row">` (jamais une grille de `<div>` pour des données) ; `<caption>` descriptif.
- Tri : `aria-sort` sur le `<th>` actif, bouton de tri dans l'en-tête ; tableaux complexes → `headers`/`id`.
- Le dashboard `11-reporting/` (tableaux de métriques) est directement concerné.

## 9. Liens

- Texte de lien explicite hors contexte (« Voir le rapport Q3 », jamais « cliquez ici » / « en savoir plus » répétés).
- Ouverture dans un nouvel onglet signalée (texte ou nom accessible) ; liens visuellement distincts autrement que par la couleur seule dans le corps de texte ; pas de liens brisés ou placeholder (`href="#"`).

## Sévérité des constats (modèle de tri)

| Sévérité | Définition | Exemples |
|---|---|---|
| 🔴 Bloquant | Empêche l'accès à la fonction | piège clavier, modale sans échappement, formulaire sans labels, contraste < 3:1 sur le CTA |
| 🟠 Majeur | Dégrade fortement l'usage | hiérarchie de titres cassée, erreurs non annoncées, focus invisible |
| 🟡 Mineur | Friction ou non-conformité isolée | alt perfectible, lien ambigu isolé, aria redondant |

Tout constat cite son critère WCAG (ex. « 2.4.7 Focus Visible »), sa localisation et sa correction proposée.

## Workflow dans le template

1. **En construction** (skill `landing-page`, dashboard) : appliquer ce référentiel dès l'écriture du HTML — l'accessibilité ne se rattrape pas en QA.
2. **Avant livraison** : dispatcher l'agent **`a11y-auditor`** (`.claude/agents/a11y-auditor.md`) qui audite le rendu réel (axe-core + vérifications manuelles ciblées) et rend un verdict par sévérité.
3. **Correction** : corriger les 🔴 et 🟠 avant livraison ; consigner les 🟡 restants dans le fichier de livraison.
