# Charte d'une landing : modèle

Chaque agent qui touche à la page reçoit ce fichier, en plus de son brief. Le contrôleur le copie au démarrage dans `05-web-content/landing-pages/<slug>/pilotage/page-charter.md`, remplace chaque `<…>` par la valeur de la page (lue dans `01-brand/tokens.json` et la spec, jamais de mémoire), puis y ajoute au § 9 les décisions que l'humain prend en cours de route. **Le § 9 prime sur tout le reste**, brief compris.

Chaque section est forte seule, mais la page se lit comme un seul récit. En cas de doute, faire comme les sections déjà construites de la page, pas comme une autre page.

## 1. Recherche d'inspiration (avant de coder)

Lire `pilotage/research-notes.md`. S'il ne couvre pas le besoin de la section, chercher 4 à 6 références de très haut niveau selon `references/inspiration.md`, les ouvrir et les regarder vraiment (en images, pas sur leur titre). Le rapport cite les 3 références qui ont le plus servi, avec l'URL et ce qu'on en a pris. Écarter ce qui contredit la marque (§ 6).

## 2. Grille et rythme

Les jetons sont posés une seule fois, dans le `:root` du socle, et toutes les sections en héritent. Aucun fragment ne redéclare une couleur, une police ni une valeur de rythme. Une page assemblée depuis la bibliothèque les reçoit de `05-web-content/templates/assets/tokens.css` (généré depuis `01-brand/tokens.json`) et de `base.css` (couche sémantique `--ink`, `--muted`, `--hl`, `--line`… que la classe `band-dark` repointe sur la palette sombre) : un fragment sur mesure lit ces mêmes noms.

| Jeton | Bureau | ≤ 768 px | Valeur de la page |
|---|---|---|---|
| `--wrap` (largeur utile) | `min(1280px, 100% - 100px)` | `100% - 40px` | `<…>` |
| `--section-gap` (section claire, marge verticale) | 96 à 120 px | 56 à 64 px | `<…>` |
| `--band-gap` (bande sombre, marge verticale) | 120 px | 80 px | `<…>` |
| `--head-gap` (en-tête → contenu) | 56 px | 40 px | `<…>` |
| `--intro-gap` (titre → intro) | 20 px | 16 px | `<…>` |

- **Points de rupture** : une seule liste pour toute la page, écrite en dur (`@media` ne lit pas les variables), par exemple 1280, 1100 (deux colonnes → une), 900 (les paires de cartes s'empilent), 768 (typographie mobile), 640. Les exceptions se documentent dans le fragment.
- **Bandes sombres** : une ou deux bandes de contenu au plus, plus le CTA final. Jamais deux bandes sombres d'affilée.
- **Densité** : une section dense est suivie d'une respiration (titre centré, beaucoup d'air).
- **Fond de page** : le fond de page porte la matière de la marque (aplat, grain, motif). Les sections claires ne le recouvrent pas d'un panneau opaque ni d'un halo ; seules les bandes sombres et les cartes peignent.
- **Défilement** : `overflow-x: hidden` sur un ancêtre casse `position: sticky`. Utiliser `overflow-x: clip` sur la racine de page, et rien sur les ancêtres d'une section épinglée.

## 3. En-tête de section (le même partout)

- **Balise** : `<div class="section-head">`. `header`, `nav` et `footer` restent réservés aux repères de la page (barre, pied), qu'un sélecteur global finit toujours par styler.
- **Aucune pastille de sur-titre** (eyebrow) : l'en-tête commence par son titre. Une information utile au-dessus du titre s'écrit en texte simple. Les badges d'état (« Complet », « Spécimen », « Votre formule ») restent permis.
- **Titre `h2`** :
  - taille `<…>` sur bureau, `<…>` sous 768 px, graisse `<…>`, `text-wrap: balance` ;
  - une seule structure de titre pour toute la page (par exemple un segment fort accentué, puis la suite) ;
  - **ni virgule ni point** : on reformule, ou on passe à la ligne ;
  - **aucun mot seul en fin de bloc** (titre, accroche, bouton, étiquette) : on contrôle les coupures à chaque taille d'écran.
- **Intro** : `<…>` px, `max-width` 60 à 65 caractères.
- **Alignement** : centré pour une section de récit, à gauche quand la section est en deux colonnes.
- **Hero** : son `h1` est plus grand que tous les `h2`. Une page porte un seul `h1`, et les niveaux ne se sautent pas.
- **Échelle typographique** : celle de `01-brand/style-guide.md`. Planchers mesurés par `qa-landing.py` : 12 px pour toute étiquette, 16 px minimum pour le texte courant (erreur en dessous), 18 px recommandés sur bureau (avertissement entre 16 et 18 px).

## 4. Composants et matières

- **Cartes**, une seule famille : fond, rayon (`<…>`, un cran de plus pour une carte héroïque), ombre au repos, ombre et soulèvement au survol (4 px au plus), filet éventuel. Rayons intérieurs concentriques.
- **Visuels** : de la bibliothèque `01-brand/assets/` d'abord. Un visuel généré porte la mention prévue par `01-brand/divulgation-ia.md` (alt-text, et mention visible là où la politique la demande). Une photo de personne exige son accord (`01-brand/droits.md`).
- **Chiffres et numéros** : graisse forte, couleur ou dégradé de marque seulement sur de gros corps où le contraste se mesure.
- **Boutons** : une variante sur fond clair, une sur fond sombre. **L'accent fort (dégradé, couleur vive) est réservé au bouton de conversion principal.** Libellé court, un verbe ; le prix vit à côté de ce qu'il comprend, pas dans le bouton. Hauteur d'au moins 44 px sur mobile.
- **Couleurs** :
  - **texte atténué** : une couleur pleine (`--muted`), jamais une opacité sur du texte ;
  - **couleur de marque en texte sur fond clair** : seulement si son contraste mesuré tient 4,5:1 (3:1 au-delà de 24 px). Sinon, elle sert de fond pastel, de point, de filet ou de dégradé sur de gros chiffres ;
  - **sur fond sombre** : couleurs pleines, pas d'opacité ;
  - **aucune couleur en dur** hors du `:root`. Contrôle : `grep -nE "#[0-9a-fA-F]{3,8}|rgba?\(" pilotage/sections/*.html`.
- **Focus** : anneau de 3 px avec un retrait de 2 à 4 px, d'une couleur qui tient 3:1 sur chaque fond (sombre sur le clair, clair sur les bandes sombres).

## 5. Mouvement (vocabulaire commun)

- **Apparitions** : un seul moteur pour la page, dans le socle. Le conteneur porte `data-reveal-group`, les éléments `data-reveal` (`up`, `left`, `right`, `scale`). Les entrées jouent sur **l'opacité et la position seules** : `visibility: hidden` retire titres et boutons du clavier et des lecteurs d'écran tant que le défilement n'y est pas.
  - Le masquage initial ne s'applique que si le script a démarré **et** que `prefers-reduced-motion` vaut `no-preference` (classe posée sur `<html>` par le script). Sans script ou en mouvement réduit, tout est visible.
  - Blocs : montée de 24 à 44 px en 0,7 à 0,9 s, décalage de 0,08 à 0,12 s ; déclenchement vers 85 % de la hauteur de l'écran.
- **Courbe** : `cubic-bezier(0.2, 0.7, 0.2, 1)` ou équivalent (`power3.out`). Durées de 0,9 s au plus. **Aucun ressort, aucun rebond.**
- **Un seul moment orchestré par section**, pas trois. `01-brand/design-anti-generique.md` § 1e : l'excès d'animation est un marqueur du look IA.
- **Épinglage** : seulement à partir d'environ 1100 px de large et 720 px de haut, hors mouvement réduit. Réalisé en `position: sticky` sur une piste haute (`height: calc(100vh + <étapes> × <n>vh)`), progression calculée au défilement.
  - Une section épinglée doit **vraiment se bloquer** au défilement.
  - Une animation qui raconte une progression (tracé, allumage successif) s'épingle, sinon le visiteur voit un état intermédiaire.
  - Trois épinglages au plus, jamais deux d'affilée sans respiration, environ 7 écrans de défilement captif au total.
- **Transitions entre sections** : fondu inversé (la section qui part s'efface, la suivante apparaît, sans superposition), dérive ou rideau, en lien avec le défilement, et seulement là où elles apportent. Jamais de cartes qui s'empilent. Aucune transition entre le hero et la section suivante.
- **Inclinaison 3D** : ±6° au plus, seulement sur des objets physiques (billet, carte, document), avec un pointeur fin (`(hover: hover) and (pointer: fine)`).
- **Animations infinies** : trois itérations au plus ; une boucle ne tourne que lorsqu'elle est à l'écran.
- **`prefers-reduced-motion: reduce`** : rien ne bouge, tout est visible, les états finaux sont affichés d'emblée (`animation: none`, pas une durée de 0,01 ms qui boucle à l'infini). Une scène épinglée devient une liste simple.

## 6. Interdits de marque

Ceux de `01-brand/style-guide.md` (tropes visuels bannis), de `01-brand/voice.md` (vocabulaire), de `01-brand/anti-ai-writing-style.md` (tiret cadratin, parallélismes négatifs, vocabulaire IA, règle de trois) et de `01-brand/design-anti-generique.md` § 1 (dégradé violet par défaut, emojis en icônes, héros centré par réflexe, excès d'animation, cartes de faible densité), plus :

- polices autres que celles de `01-brand/tokens.json` ;
- photo de banque d'images générique ;
- texte dont l'opacité le ferait passer sous 4,5:1 ;
- halo, forme ou aplat posé derrière le logo, sauf si la charte le prévoit ; logo recoloré ou épaissi ;
- mot banni écrit dans une illustration (relire le texte des images, pas seulement les `alt`).

Rédaction : la langue et le registre de `01-brand/voice.md`. Une version dans une autre langue est une adaptation, avec sa typographie (espaces insécables en français).

## 7. Conversion

- **Un seul objectif** par page. Tous les boutons mènent à l'étape de choix ou à la conversion, jamais ailleurs. Le CTA primaire porte `data-cta="primaire"`.
- **Une objection par section**, dans un ordre qui suit la pensée du visiteur, par exemple : de quoi s'agit-il, pourquoi maintenant, quoi exactement, pour qui, avec qui, comment ça s'insère dans ma vie, combien, comment je réserve, et ensuite. Une section qui ne répond à aucune objection sort de la page.
- **Preuve concrète** plutôt qu'affirmation : vraies personnes, vrais documents, vrais chiffres sourcés. Aucun chiffre inventé, aucun compteur fictif.
- **Urgence honnête** : places et date de clôture réelles, comptées en jours, jamais en secondes.
- **Lecture en diagonale** : un titre et une phrase suffisent à comprendre chaque section.
- **Prix** : il n'apparaît qu'avec ce qu'il comprend (« Compris »), les étapes après le clic (« La suite ») et les conditions.
- **Hero** : un titre, une accroche sur deux lignes, une phrase au plus, **un seul bouton**, une ligne d'échéance s'il y en a une, et l'objet visuel. Ni étiquette au-dessus du `h1`, ni carte d'information posée sur le visuel, ni rangée de visages, ni second bouton concurrent.
- **Mobile** : le CTA primaire est visible sans défiler, ou une barre d'action collante le porte.
- **Mesure** : chaque CTA porte `data-track` et sa position ; le formulaire `data-track="generate_lead"`.

## 8. Technique

- **Ce qui est interdit à un agent** :
  - écrire hors de ses fichiers : `index.html` (le socle) appartient au contrôleur, chaque fragment `pilotage/sections/<nn>-<id>.html` à un seul builder ;
  - commiter, pousser, publier ;
  - supprimer un fichier qu'il n'a pas créé, ou demander à un autre agent de refaire une action qu'on lui a refusée ;
  - piloter un navigateur sur un site de production ou un compte connecté.
- **Fragments** : une `<section id="<id>" aria-labelledby="<id>-titre">`, son `<style>` dont chaque sélecteur commence par `#<id>`, son `<script>` éventuel enfermé dans une fonction et qui ne touche qu'à sa section. Les jetons du `:root` seulement.
- **Textes** : ceux de la spec, clé par clé. Un texte manquant se signale, il ne s'invente pas.
- **Listes** : `role="list"` sur toute `<ul>` ou `<ol>` stylée sans puces (sinon certains lecteurs d'écran la taisent).
- **Contenu révélé après un choix** : attribut `hidden`, plus un `<noscript>` qui le rend visible sans script. Les animations de la partie cachée se construisent après la révélation ; le focus va au titre atteint (`tabindex="-1"`, `focus({ preventScroll: true })`).
- **État de l'offre** : une seule configuration en tête du script du socle (dates, prix, places, état). Le HTML statique montre l'état ouvert ; l'état réel (liste d'attente, clôture) se calcule dans le navigateur.
- **QA** : `python3 05-web-content/scripts/qa-landing.py <page>` sur un assemblage du fragment (copie dans le scratchpad pour un builder), zéro erreur avant de rendre.

## 9. Décisions de l'humain (priment sur tout le reste)

Les règles suivantes valent pour toute landing, sauf décision contraire écrite ici :

- **Hero allégé** : un titre, une accroche sur deux lignes, un seul bouton. Pas de carte d'information ni de rangée de visages.
- **Pas de pastille de sur-titre.**
- **Ni virgule ni point dans les titres.**
- **Aucun mot seul en fin de titre, d'accroche ou de bouton.**
- **Fond de page visible** : aucune section claire ne le recouvre d'un aplat ou d'un halo.
- **Transitions** : fondu inversé ; pas d'effet de cartes qui se superposent ; rien entre le hero et la section suivante.
- **Une section épinglée se bloque** pour de bon, sinon elle ne fonctionne pas.
- **Aucune phrase de remplissage** : ce qui n'apprend rien au visiteur, ou décrit ce que les cartes montrent déjà, est supprimé, même bien écrit.
- **Contraste mesuré, jamais estimé** : une couleur de texte passe par le calcul (QA ou formule WCAG) avant d'être retenue.
- **Urgence honnête** : en jours, avec de vrais chiffres.

Décisions propres à cette page (date, décision, raison) :

- `<AAAA-MM-JJ>` : `<décision>` (`<raison>`)
