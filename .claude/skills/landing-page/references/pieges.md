# Pièges rencontrés et parades

Les pièges qui reviennent sur toute landing, avec leur parade. Quand un piège se mesure, la colonne « QA » donne l'identifiant de constat de `05-web-content/scripts/qa-landing.py`.

## CSS et mise en page

| Piège | Parade | QA |
|---|---|---|
| Un en-tête de section écrit en `<header>` hérite du style global de la barre du site (collant, fond, rayon) et devient une pastille collée en haut de l'écran | En-tête de section en `<div>`. Même prudence avec `nav` et `footer`. Un vrai `<nav>` (sommaire) reste hors des sections et porte un `aria-label` distinct | |
| `overflow-x: hidden` sur un ancêtre en fait un conteneur de défilement : `position: sticky` ne marche plus | `overflow-x: clip` sur la racine de page, rien sur les ancêtres d'une section épinglée | |
| Un élément décoratif (filigrane, halo, maquette inclinée) dépasse à droite : la page défile horizontalement sur mobile | Le contenir dans un parent en `overflow: clip`, ou le dimensionner en `min()` / `clamp()`. Un `overflow-x: hidden` sur `body` masque le symptôme sans le corriger | `debordement`, `debordement-masque` |
| Un titre épinglé passe sous la barre fixe du haut | Cadre collant décalé de la hauteur de la barre plus une marge ; titre épinglé en `clamp()` borné par la hauteur d'écran | |
| Des sections claires peignent un panneau opaque qui masque la matière du fond de page | Aucune section claire ne déclare de fond opaque ; seules les bandes sombres et les cartes peignent | |
| Couleur de marque en texte sur fond clair : contraste souvent sous 4,5:1 | La mesurer. Si elle échoue, elle sert de fond pastel, de point, de filet ou de dégradé sur de gros chiffres | `contraste` |
| Texte atténué par opacité : le contraste chute (une opacité de 0,6 suffit à passer sous le seuil) | Une couleur pleine `--muted`, calculée pour tenir 4,5:1 | `contraste` |
| Logos ou initiales estompés pour « faire discret » | Couleur pleine ; la discrétion vient du corps et de la graisse | `contraste` |
| Initiales ou texte posés sur un dégradé de marque | Mesurer à chaque arrêt du dégradé ; s'il échoue partout, changer le fond ou la couleur du texte | `contraste` |
| Couleurs empruntées à d'autres pages, hors palette | Jetons du `:root` seulement ; `grep -nE "#[0-9a-fA-F]{3,8}\|rgba?\("` sur les fragments | |
| Petites étiquettes en capitales espacées à 11 px | 12 px au moins, et un libellé court ; une phrase ne se met jamais en étiquette | `plancher-typo` |
| Texte courant à 15 px, ou à 16 px sur bureau | 16 px minimum pour tout texte de 12 mots et plus (erreur), 18 px recommandés sur bureau (avertissement) | `plancher-typo` |
| Mot seul en dernière ligne d'un titre ou d'un bouton | `text-wrap: balance` sur les titres, coupures décidées (`<br>` contrôlé, insécables), libellé de bouton plus court | `mot-orphelin` |

## Mouvement

| Piège | Parade | QA |
|---|---|---|
| Le CSS masque les éléments à révéler sans condition, et le script se tait sous `prefers-reduced-motion` : le contenu reste invisible pour toujours | Le masquage initial dépend d'une classe que le script pose sur `<html>`, seulement s'il démarre et si le mouvement n'est pas réduit | `mouvement-reduit-masque` |
| En mouvement réduit, le contenu n'apparaît qu'en arrivant à l'écran | En mouvement réduit, le moteur d'apparition ne fait rien : tout est visible au chargement | `mouvement-reduit-apparition` |
| Réduction du mouvement par `animation-duration: .01ms` : une animation infinie boucle alors à toute vitesse | `animation: none` (ou une seule itération) sous `prefers-reduced-motion: reduce` | `mouvement-reduit-anime` |
| Animations infinies (ondes, pulsations, défilement de logos) | Trois itérations au plus ; une boucle ne tourne qu'à l'écran | `mouvement-reduit-anime` |
| `visibility: hidden` dans une entrée (ou un utilitaire qui le pose) : titres et boutons sortent du clavier et des lecteurs d'écran tant que le défilement n'y est pas | Entrées en opacité et position seules | |
| Rebond déguisé (courbe à dépassement plus un écrasement) | Courbe douce sans dépassement, 0,9 s au plus | |
| Animations mesurées dans une partie `hidden` : tout vaut zéro et se déclenche trop tôt | Construire les animations après la révélation, puis recalculer les déclencheurs | |
| Glissé automatique à travers plusieurs scènes épinglées | Lien direct = saut instantané ; seul le premier choix au clic glisse | |
| Focus perdu après un saut d'ancre ou une révélation | `tabindex="-1"` sur le titre atteint, puis `focus({ preventScroll: true })` | |
| Le mot qui tourne dans l'accroche fait sauter la mise en page | Une copie invisible par mot dans la même case de grille ; la hauteur suit le plus long | |
| Dégradé de texte (`background-clip: text`) perdu sur un élément transformé ou en mouvement | Transformation sur le parent, couleur sur un enfant ; pas de dégradé sur des chiffres qui défilent | |
| Liste stylée sans puces, que certains lecteurs d'écran taisent | `role="list"` sur chaque liste stylée | |
| Date ou état calculé une fois pour toutes dans le HTML | Configuration unique en tête du script ; HTML = état ouvert ; l'état réel se calcule dans le navigateur | |
| Compte à rebours à la seconde | Urgence en jours, avec une vraie date de clôture | `compte-a-rebours` |

## Conversion et accessibilité

| Piège | Parade | QA |
|---|---|---|
| CTA primaire sous le pli sur mobile (le formulaire du hero passe sous l'objet visuel) | Remonter le bouton, ou porter le CTA par une barre collante | `cta-pli` |
| Plusieurs boutons vers plusieurs destinations | Un objectif : les boutons secondaires mènent au bloc de conversion | `cta-hors-objectif` |
| Lien `href="#"` ou ancre vers un id disparu après une refonte | Chaque CTA a une destination réelle ; vérifier les ancres après chaque assemblage | `cta-destination` |
| Bouton de 36 px sur mobile | 44 px au moins pour un CTA, 24 px pour toute cible | `cible-tactile` |
| Champ sans `<label>`, placeholder en guise de label | `<label for>` visible, ou `aria-label` si le contexte visuel suffit | `champ-sans-label` |
| Bouton icône sans nom | Texte `sr-only` ou `aria-label` ; l'icône en `aria-hidden` | `nom-accessible` |
| Deux `h1` (barre et hero), niveau sauté (`h2` puis `h4`) | Un seul `h1` ; les cartes d'une section `h2` portent des `h3` | `titres-h1`, `titres-ordre` |
| Suivi déclaré mais aucun événement au clic | Relais `data-track` vers `dataLayer` / `gtag` dans le socle | `tracking` |
| Endpoint de formulaire laissé en placeholder | Le brancher avant publication, ou garder la page en brouillon | `cta-destination`, `placeholder` |

## Session et outillage

| Piège | Parade |
|---|---|
| Plusieurs agents écrivent dans le même fichier : des modifications se perdent | Un fragment par agent (`pilotage/sections/<nn>-<id>.html`), le socle au contrôleur, assemblage par script |
| Réassembler une page retouchée à la main efface les retouches | `assemble-landing.py` refuse d'écraser une page dont l'empreinte a changé ; reporter la retouche dans la spec ou le fragment, et `--force` seulement pour perdre volontairement la retouche |
| Une limite d'usage coupe plusieurs agents d'un coup | Assembler et commiter ce qui est fini, puis reprendre chaque agent par `SendMessage` avec « relis d'abord l'état actuel de ton fichier » |
| Une action refusée à un agent (suppression, navigation) est proposée par un autre | La soumettre à l'humain ; personne ne la refait sans son accord |
| Navigation vers les galeries d'inspiration refusée aux agents de section | Recherche faite en amont par `landing-researcher`, consignée dans `research-notes.md` |
| Spec modifiée pendant qu'un agent travaille | Figer la spec pendant une étape, ou prévenir l'agent par `SendMessage` |
| Un outil d'écriture transforme les échappements `\u` en caractères littéraux | Écrire les caractères spéciaux (espaces insécables du français) par un script, puis contrôler les octets |
| Compter des occurrences avec `grep -c` sur un HTML minifié (une seule ligne) | `grep -o "<motif>" \| wc -l` |
| Une sortie d'outil condensée ou réécrite par un proxy induit en erreur | Écrire la sortie brute dans un fichier et la relire ; recouper toute lecture surprenante |
| Un serveur local lancé par un agent s'arrête avec lui | Les serveurs se lancent par le contrôleur, en arrière-plan, avec un journal dans le scratchpad |
| Chemins absolus (`file:///…`, chemins de la machine) dans le HTML livré | `python3 scripts/relativize-paths.py` avant livraison |

## Marque dans les visuels

| Piège | Parade |
|---|---|
| Logo épaissi ou recoloré pour rester lisible une fois réduit | Fichier d'origine, taille augmentée plutôt que trait modifié |
| Reflet, halo ou forme qui passe derrière le logo | Effets limités aux zones sans logo, zone de protection respectée |
| Mot banni écrit dans une illustration générée | Relire le texte contenu dans les images, pas seulement les `alt` |
| Visuel généré sans mention | Mention selon `01-brand/divulgation-ia.md` (alt-text, et mention visible si la politique la demande) |

## Règles tirées des arbitrages

Ces règles viennent de retours d'arbitrage sur des landings livrées. Elles valent par défaut (charte § 9), sauf décision contraire de l'humain :

| Retour type | Règle |
|---|---|
| « Ce n'est pas assez visuel » sur une page conforme au plan | La barre est le rendu : objet fort, visuels de marque, mise en scène au défilement, bandes sombres. Des cartes blanches empilées sont refusées |
| « Je veux voir vite » | Montrer après chaque étape, et lancer l'étape suivante sans attendre la réponse |
| « Fais tout en même temps » | Paralléliser par propriété de fichiers, après avoir posé les textes, la charte et un emplacement par section |
| « Supprime ces petites pilules » | Pas de pastille de sur-titre ; les badges d'état restent permis |
| « Retire les virgules et les points des titres » | Ni virgule ni point dans un titre (`h1` à `h4`, cartes, étapes, questions hors `?`) |
| « Ce mot tout seul à la ligne » | Les coupures d'un titre se décident ; aucun mot seul en fin de bloc |
| « Le hero est trop chargé » | Un titre, une accroche sur deux lignes, un bouton, l'objet visuel |
| « Supprime cette phrase » (phrase qui décrit ce que les cartes montrent) | Toute phrase qui n'apprend rien au visiteur est supprimée |
| « Mets juste un verbe sur le bouton » | Bouton de conversion : un verbe court, sans prix |
| « Le fond doit se voir partout » | Aucune section claire ne recouvre le fond de page |
| « Pas de cartes qui se superposent au défilement » | Fondu inversé entre les sections ; rien après le hero |
| « Cette section doit se bloquer » | Une animation de progression pilotée par le défilement s'épingle pour de bon |
| « La même section doit être identique partout » | Une section présente sur deux pages est une seule section, au pixel près |
| « Je ne comprends pas ce point ouvert » | Un point ouvert s'écrit dans les mots de l'humain : ce que voit le visiteur, et pourquoi ça compte |
| « Le document source dit autre chose » | Le document source fait foi contre la demande ; on signale l'écart |
| « Non, garde ce fichier » | Une action refusée ne se refait pas ailleurs sans accord |
| « Tu peux pousser » | Push, publication et fusion seulement sur go explicite, à chaque fois |
