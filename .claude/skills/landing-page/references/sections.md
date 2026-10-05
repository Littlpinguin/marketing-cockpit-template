# Catalogue des mécaniques de section

Des mécaniques éprouvées sur des landings de conversion, pas un ordre imposé. Pour chaque page, choisir celles qui servent le récit de la spec, leur donner l'objet signature de la page, et garder un seul moment orchestré par section. Ce fichier dit **quand** et **pourquoi** une mécanique sert, et ce qui la fait échouer. Leur implémentation est la bibliothèque `05-web-content/templates/sections/` : un fragment par mécanique (nommé en fin de fiche), ses slots, ses moteurs, et `catalogue.html` qui les montre toutes ; `README.md` y donne les compositions de départ, le format de la spec et les contrats des moteurs.

Chaque fiche donne : l'objection du visiteur qu'elle traite, la mécanique, quand la choisir, les anti-modèles, et le comportement en mouvement réduit (`prefers-reduced-motion: reduce`).

## Squelette de page

- **Socle** (contrôleur) : `<head>` complet, jetons `:root`, CSS de la charte, moteur d'apparition, relais de mesure, configuration de l'offre. L'assembleur (`05-web-content/scripts/assemble-landing.py`) le produit depuis la spec de la page. Les sections viennent ensuite, dans l'ordre du récit, chacune entre ses marqueurs `<!-- section:<id> -->`.
- **Section** : une `<section id="<id>" aria-labelledby="<id>-titre">` qui gère ses marges et son ancre ; l'en-tête en `<div class="section-head">`.
- **Barre du haut** : logo et un seul bouton, la même action que le CTA primaire. Pas de menu complet : chaque lien de sortie est une fuite. Fragment `topbar`.
- **Pied** : mentions, confidentialité, contact. Rien qui concurrence la conversion. Fragment `footer`.

## Hero : un objet fort

- **Fragment** : `hero` (objet en image ou composé avec le kit `.obj`, accroche tournante par `data-rotate`).
- **Objection** : de quoi s'agit-il, pour qui, combien, jusqu'à quand.
- **Mécanique** : d'un côté le `h1`, une accroche sur deux lignes, une phrase, **un seul bouton** et une ligne d'échéance ; de l'autre, un objet fort (le produit en situation, un document réel, une illustration de marque dans une forme signature). Le `h1` est le plus grand texte de la page.
- **Accroche tournante** (optionnelle) : un mot qui change pour nommer les audiences. La version statique se lit par un `<span class="sr-only">`, la version animée est en `aria-hidden`. Pour éviter que la mise en page saute, chaque mot possible occupe la même case de grille en copie invisible, et la hauteur suit le plus long.
- **Quand** : toujours. C'est la section qu'on construit et qu'on fait valider en premier.
- **Anti-modèles** : étiquette au-dessus du `h1`, carte d'information posée sur le visuel, rangée de visages, second bouton qui concurrence le premier, hero centré par réflexe (`01-brand/design-anti-generique.md` § 1d), accroche de trois lignes.
- **Mouvement réduit** : l'accroche montre son premier mot, l'objet est immobile.

## Bande de preuve immédiate

- **Fragment** : `proof-band` (chiffres) ; `logos` (logos autorisés).
- **Objection** : est-ce sérieux.
- **Mécanique** : sous le hero, une rangée compacte de 3 ou 4 faits vérifiables (chiffre en grand, libellé court) ou de logos clients autorisés (`01-brand/droits.md`).
- **Quand** : dès qu'on a des chiffres sourcés ou des logos autorisés.
- **Anti-modèles** : logos dont l'usage n'est pas accordé, chiffres arrondis à la hausse, logos estompés par opacité (le contraste tombe, la QA le mesure).
- **Mouvement réduit** : les chiffres s'affichent à leur valeur finale, sans compteur qui monte.

## Problème épinglé

- **Fragment** : `problem-pinned`.
- **Objection** : pourquoi maintenant.
- **Mécanique** : à gauche, le titre, un chapô et un visuel qui change avec le constat actif ; à droite, une liste numérotée dont seul l'élément actif déplie son texte. La section s'épingle le temps de parcourir les constats (40 à 55 vh par constat). Hors épinglage (petit écran, mouvement réduit), c'est une liste illustrée.
- **Quand** : quand le document source porte de vrais constats, dans les mots de l'audience (`01-brand/personas.md`).
- **Anti-modèles** : registre de la peur, constats inventés, liste épinglée plus haute que l'écran (seul l'élément actif déplie, la liste prend la hauteur de son état le plus haut, recalculée au redimensionnement et une fois les polices chargées).
- **Mouvement réduit** : tous les constats dépliés, visuels en vignettes.

## Basculement typographique

- **Fragment** : `pivot`.
- **Objection** : et donc, quelle réponse.
- **Mécanique** : une phrase géante qui se révèle mot à mot au défilement (opacité, netteté), puis un trait et la réponse : l'offre comme solution. Piste épinglée courte, avec un temps de tenue pour lire.
- **Quand** : entre le problème et la solution, une fois par page. Le couple problème épinglé → basculement est le seul enchaînement de deux épinglages admis ; une section non épinglée le suit avant tout autre épinglage.
- **Anti-modèles** : dégradé de texte posé sur un élément transformé (certains navigateurs le perdent : transformer le parent, colorer l'enfant), phrase lue mot à mot par les lecteurs d'écran (une copie `sr-only` porte la phrase entière, la version animée est en `aria-hidden`).
- **Mouvement réduit** : la phrase entière, d'emblée.

## Porte de choix qui révèle la suite

- **Fragment** : `choice-gate` (sections de la suite marquées `gated: true` dans la spec).
- **Objection** : laquelle est pour moi.
- **Mécanique** : deux grandes cartes illustrées dont toute la surface est la zone de clic (un vrai `<button>`, étendu par un pseudo-élément). Au choix, la suite de la page apparaît (`hidden` retiré), adaptée à la formule ; un `<noscript>` la rend visible sans script. Un événement de mesure part au choix ; des liens profonds (`?formule=…`, ancres) ouvrent directement la bonne suite.
- **Quand** : seulement pour une offre à variantes réelles.
- **Anti-modèles** : porte qui cache l'essentiel à un visiteur pressé, animations de la partie cachée mesurées avant la révélation (tout vaut zéro : les construire après), glissé automatique à travers plusieurs scènes épinglées (lien direct = saut instantané), focus perdu après la révélation (le donner au titre atteint).
- **Mouvement réduit** : la suite apparaît sans transition.

## Parcours en scrollytelling

- **Fragment** : `journey`.
- **Objection** : concrètement, qu'est-ce que je fais et qu'est-ce que j'en tire.
- **Mécanique** : un bloc collant d'un écran en deux colonnes. À gauche, « Étape n sur N », un rail qui se remplit jusqu'au point actif, l'étape active sur un panneau, les autres repliées. À droite, une scène `aria-hidden` doublée d'un équivalent `sr-only`, qui change avec l'étape.
- **Quand** : programme, méthode, parcours client en 3 à 6 étapes.
- **Anti-modèles** : plus de 6 étapes, scène qui porte une information absente du texte.
- **Mouvement réduit et petit écran** : liste simple des étapes, chaque scène immobile sous son étape (à côté sur grand écran), jamais masquée.

## Programme ou contenu détaillé

- **Fragment** : `program`.
- **Objection** : qu'est-ce qu'il y a dedans, exactement.
- **Mécanique** : liste des modules ou des livrables, durée et résultat de chacun ; un rail qui se remplit au défilement peut donner le rythme. Un spécimen réel (page de cours, extrait de livrable, capture) vaut mieux qu'une description.
- **Quand** : formation, accompagnement, produit à plusieurs composantes.
- **Anti-modèles** : liste exhaustive qui noie l'essentiel, spécimen non étiqueté comme tel.
- **Mouvement réduit** : rail plein.

## Démonstrateur

- **Fragment** : aucun pour l'instant : section sur mesure, à verser ensuite dans la bibliothèque.
- **Objection** : est-ce que ça marche vraiment, pour mon cas.
- **Mécanique** : une demande s'écrit, le résultat réel apparaît, puis le format suivant ; ou un objet qui se construit (arborescence, document, tableau de bord) ligne à ligne. Les vidéos et boucles ne se chargent et ne tournent qu'à l'écran.
- **Quand** : produit ou méthode dont le résultat se montre mieux qu'il ne se décrit.
- **Anti-modèles** : démo truquée, boucle infinie hors écran, texte important seulement dans l'animation.
- **Mouvement réduit** : l'état final, immobile, avec ses légendes.

## Vitrine d'un objet tangible (bande sombre)

- **Fragment** : `showcase-dark`.
- **Objection** : qu'est-ce que j'emporte de concret.
- **Mécanique** : dans une bande sombre, un objet qui représente le bonus ou le livrable (document, kit, dossier, carte), et des cartes reliées à lui : le survol d'une carte allume la partie de l'objet qui lui correspond, et inversement.
- **Quand** : un bonus ou un livrable qui mérite sa propre section, plutôt qu'une ligne dans une liste.
- **Anti-modèles** : lueurs, ressorts, texte en opacité sur le fond sombre (couleurs pleines).
- **Mouvement réduit** : tout allumé, immobile.

## Carte ou schéma épinglé

- **Fragment** : `map-pinned`.
- **Objection** : est-ce compatible avec ma vie (lieux, fuseaux, rythme, rattrapage).
- **Mécanique** : un schéma ou une carte de marque, des repères posés au défilement, un tracé découvert par un masque (`stroke-dashoffset`), une fin immobile pour lire.
- **Anti-modèles** : tête de tracé qui ressemble à un repère, ondes qui pulsent sans fin (trois passages au plus).
- **Mouvement réduit** : le schéma complet, d'emblée.

## Personnes (experts, intervenants, équipe)

- **Fragment** : `people`.
- **Objection** : avec qui, et sont-ils crédibles.
- **Mécanique** : portrait ou carte de la personne, biographie en trois temps (qui, la preuve, le rôle dans l'offre). Parallaxe légère ou inclinaison réservée aux objets physiques (cartes).
- **Règles** : faits tirés de sources validées seulement, jamais de `00-intel/` ; portrait avec l'accord de la personne (`01-brand/droits.md`) ; mention IA si le portrait est généré ou dérivé (`01-brand/divulgation-ia.md`).
- **Mouvement réduit** : immobile.

## Témoignages

- **Fragment** : `testimonials` (trois avis choisis ; le mur qui se déplie reste sur mesure).
- **Objection** : d'autres comme moi l'ont-ils fait.
- **Mécanique** : de vrais avis signés (nom, rôle, contexte), en mur de colonnes qui se déplie d'un clic, ou trois avis choisis près du bloc de conversion. Un avis porte un résultat, pas un compliment.
- **Anti-modèles** : avis inventés ou anonymes, initiales sur un dégradé illisible (la QA mesure le contraste à chaque arrêt du dégradé), carrousel automatique.
- **Mouvement réduit** : mur déplié ou statique.

## Cas avant / après

- **Fragment** : `cases`.
- **Objection** : est-ce que ça a marché pour d'autres, et de combien.
- **Mécanique** : deux ou trois cartes de mission (contexte, périmètre, une même mesure avant et après en barres à la même échelle, valeurs écrites à côté, une phrase du client signée). La mesure et sa source se disent dans le chapô.
- **Quand** : prestation, accompagnement, conseil, dès qu'on a des missions mesurées et l'accord des clients.
- **Anti-modèles** : cas inventés présentés comme réels, mesures différentes d'une carte à l'autre, barre sans valeur écrite, client nommé sans accord.
- **Mouvement réduit** : barres pleines d'emblée.

## Résultats (respiration)

- **Fragment** : `outcomes`.
- **Objection** : qu'est-ce que ça change.
- **Mécanique** : une rangée compacte sans carte : pour chaque résultat, un filet, un grand numéro, un titre court et une phrase. Les filets se tracent l'un après l'autre.
- **Quand** : après une section dense, pour faire respirer la page.
- **Mouvement réduit** : filets tracés.

## Pour qui, et pour qui ce n'est pas

- **Fragment** : `for-whom`.
- **Objection** : est-ce pour moi.
- **Mécanique** : deux colonnes courtes, « pour vous si » et « pas pour vous si », dans les mots des personas. Le second volet qualifie et rassure.
- **Anti-modèles** : listes génériques valables pour tout le monde.

## Bloc de conversion en objet

- **Fragment** : `offer-ticket` (une offre datée ; une seule formule : billet horizontal) ; `pricing-table` (plusieurs plans, prix « dès » possible, bascule mensuel / annuel seulement si un plan a un prix annuel) ; `comparison` (tableau comparatif, région défilante à première colonne fixe sur petit écran) ; `process` (étapes après le clic) ; `guarantee` (la garantie, juste après le billet).
- **Objection** : combien, qu'est-ce qui est compris, comment je réserve, et ensuite.
- **Mécanique** : l'offre comme un objet (billet, carte d'offre, bon de commande) : le prix avec ce qu'il comprend, les éventuelles formules en contrôle segmenté accessible (`fieldset`, vraies radios masquées en `sr-only`), une remise expliquée avec une note en `aria-live`, **le seul bouton à l'accent fort de la page**, puis deux colonnes « Compris » et « La suite ». L'état de l'offre (ouverte, liste d'attente, close) vient de la configuration du socle ; le HTML montre l'état ouvert, le navigateur calcule l'état réel.
- **Quand** : toute page qui vend ou inscrit.
- **Anti-modèles** : prix sans ce qu'il comprend, remise dont on ne dit pas ce qui se passe si on l'oublie, compte à rebours en secondes, compteur de places sans vrai chiffre, prix animé sans équivalent lisible.
- **États** : en liste d'attente, le même bouton mène à la liste ; clos, il reste en place, désactivé et lisible (4,5:1), et un lien dessiné en vrai bouton propose la suite (session suivante, alerte).
- **Garantie** : quand elle existe, un sceau décoratif et ses conditions exactes (échéance datée, démarche, délai de remboursement), jamais un « satisfait ou remboursé » sans conditions.
- **Mouvement réduit** : objet immobile, prix lisible d'emblée.

## Formulaire de capture

- **Fragment** : `lead-capture` (email contre un contenu) ; `form` (démo, rendez-vous, devis) ; `event-registration` (inscription gratuite à un événement, sur place ou en ligne).
- **Objection** : qu'est-ce que je donne, et qu'est-ce que je reçois.
- **Mécanique** : le moins de champs possible (l'email seul si la suite le permet), chaque champ avec son `<label>`, `autocomplete` sur les champs d'identité, champ piège anti-robots hors champ et en `aria-hidden`, message de confirmation en `role="status"`, erreurs annoncées (`aria-invalid` et `aria-describedby`). Une phrase sous le bouton dit ce qui arrive après l'envoi.
- **Consentement** : recevoir la ressource demandée ne demande aucune case, la demande vaut envoi. L'inscription à une lettre ou à la prochaine édition passe par une case facultative et décochée, mesurée (`optin`). Une demande de démo ou de devis n'a pas de case : la mention de confidentialité et son lien, sous le bouton, suffisent. Un endpoint encore en marqueur fait de l'envoi une démonstration, jamais comptée comme lead.
- **Règles** : `cro-form` pour l'optimisation, `lead-magnet` pour le circuit complet si la page capture un email contre un contenu.
- **Anti-modèles** : placeholder qui tient lieu de label, case pré-cochée, champ qui ne paie pas sa friction.

## FAQ

- **Fragment** : `faq`.
- **Objection** : les dernières questions avant d'agir.
- **Mécanique** : accordéon natif `<details>` / `<summary>` (clavier et lecteurs d'écran sans script), questions réelles venues des ventes ou du support. Variante : à côté, une carte collante qui rappelle l'offre et porte le CTA. JSON-LD `FAQPage` seulement sur une page indexée.
- **Anti-modèles** : questions inventées pour placer un argument, réponses qui renvoient ailleurs que vers la conversion.

## Informations légales

- **Fragment** : `legal`.
- **Mécanique** : une fiche sobre, liste de définitions en deux colonnes ; les liens qui ouvrent un nouvel onglet l'annoncent. Le titre est simple.
- **Quand** : vente directe, formation, événement payant : conditions, rétractation, organisateur, accessibilité.

## CTA final (bande sombre)

- **Fragment** : `final-cta`.
- **Mécanique** : une bande sombre, une composition centrée, un titre sur deux lignes (le chiffre fort ou l'échéance), une phrase et le CTA primaire en variante claire. Entrée en rideau possible.
- **Anti-modèles** : nouvel argument introduit à la fin, second objectif.

## Barre d'action mobile collante

- **Fragment** : `sticky-bar`.
- **Mécanique** : sur mobile, une barre fixe en bas d'écran porte le CTA primaire (ou l'appel, pour une page locale). Elle apparaît après le hero et s'efface devant le pied de page pour ne rien masquer.
- **Règles** : hauteur d'au moins 44 px pour le bouton, `padding-bottom` de la page égal à sa hauteur, même destination que le CTA primaire.

## Théâtre de défilement (transverse)

- **Fragment** : moteur `templates/assets/scroll.js` (`theatre.progress` dans la spec, attributs `data-exit` / `data-enter`).
- **Mécanique** : un fil de lecture de 3 px en haut de l'écran, un sommaire des chapitres sur grand écran, et des transitions de jonction déclarées par attributs (`data-exit` / `data-enter` : fondu inversé, dérive, rideau), toutes liées au défilement, sans épinglage propre.
- **Interdits** : cartes qui s'empilent, transition entre le hero et la section suivante.
- **Mouvement réduit et petit écran** : coupé.
