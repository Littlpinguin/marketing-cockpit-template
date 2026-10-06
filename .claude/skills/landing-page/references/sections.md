# Catalogue des mécaniques de section

Des mécaniques éprouvées sur des landings de conversion, pas un ordre imposé. Pour chaque page, choisir celles qui servent le récit de la spec, leur donner l’objet signature de la page, et garder un seul moment orchestré par section. Ce fichier dit **quand** et **pourquoi** une mécanique sert, et ce qui la fait échouer. Leur implémentation est la bibliothèque `05-web-content/templates/sections/` : un fragment par mécanique (nommé en fin de fiche), ses slots, ses moteurs, et `catalogue.html` qui les montre toutes ; `README.md` y donne les compositions de départ, le format de la spec et les contrats des moteurs.

Chaque fiche donne : l’objection du visiteur qu’elle traite, la mécanique, quand la choisir, les anti-modèles, et le comportement en mouvement réduit (`prefers-reduced-motion: reduce`).

## Squelette de page

- **Socle** (contrôleur) : `<head>` complet, jetons `:root`, CSS de la charte, moteur d’apparition, relais de mesure, configuration de l’offre. L’assembleur (`05-web-content/scripts/assemble-landing.py`) le produit depuis la spec de la page. Les sections viennent ensuite, dans l’ordre du récit, chacune entre ses marqueurs `<!-- section:<id> -->`.
- **Section** : une `<section id="<id>" aria-labelledby="<id>-titre">` qui gère ses marges et son ancre ; l’en-tête en `<div class="section-head">`.
- **Barre du haut** : logo et un seul bouton, la même action que le CTA primaire. Pas de menu complet : chaque lien de sortie est une fuite. Fragment `topbar`.
- **Pied** : mentions, confidentialité, contact. Rien qui concurrence la conversion. Fragment `footer`.

## Hero : un objet fort

- **Fragment** : `hero` (objet en image ou composé avec le kit `.obj`, accroche tournante par `data-rotate`).
- **Objection** : de quoi s’agit-il, pour qui, combien, jusqu’à quand.
- **Mécanique** : d’un côté le `h1`, une accroche sur deux lignes, une phrase, **un seul bouton** et une ligne d’échéance ; de l’autre, un objet fort (le produit en situation, un document réel, une illustration de marque dans une forme signature). Le `h1` est le plus grand texte de la page.
- **Accroche tournante** (optionnelle) : un mot qui change pour nommer les audiences. La version statique se lit par un `<span class="sr-only">`, la version animée est en `aria-hidden`. Pour éviter que la mise en page saute, chaque mot possible occupe la même case de grille en copie invisible, et la hauteur suit le plus long.
- **Quand** : toujours. C’est la section qu’on construit et qu’on fait valider en premier.
- **Anti-modèles** : étiquette au-dessus du `h1`, carte d’information posée sur le visuel, rangée de visages, second bouton qui concurrence le premier, hero centré par réflexe (`01-brand/design-anti-generique.md` § 1d), accroche de trois lignes.
- **Mouvement réduit** : l’accroche montre son premier mot, l’objet est immobile.

## Hero éditorial

- **Fragment** : `hero-editorial` (slot `level` : 1 en tête de page, 2 dans un catalogue).
- **Objection** : de quoi s’agit-il, quand, où, combien.
- **Mécanique** : un très grand titre sur toute la largeur de la grille, posé sur un filet tracé, une accroche courte, un seul bouton et la ligne d’échéance, puis une ligne de faits (date, lieu, format, prix). Aucun objet à côté : la typographie fait l’affiche.
- **Quand** : un événement, une édition datée, une prise de position, dès que le titre suffit à faire l’affiche.
- **Anti-modèles** : titre de plus de trois lignes, étiquette au-dessus du `h1`, plus de quatre faits, second bouton, filets fins et coins carrés partout (le cliché du journal), deux pages de la même marque ouvertes de la même façon.
- **Mouvement réduit** : le filet est tracé d’emblée, rien ne bouge.

## Hero à image dans le titre

- **Fragment** : `hero-image-title` (slots `level`, `tone` pour la couleur de la pastille).
- **Objection** : de quoi s’agit-il, pour qui, jusqu’à quand.
- **Mécanique** : une petite image glissée entre deux mots du titre, à la hauteur de la lettre, dans une pastille aux couleurs de la marque ; le titre devient l’objet fort. Puis l’accroche, un bouton, l’échéance.
- **Quand** : une petite image dit l’offre mieux qu’un objet posé à côté (le livrable d’un audit, le geste du métier). Une page de capture dont le livrable doit se voir dès l’ouverture garde `hero` et son objet : avec ce hero, la moitié droite d’un grand écran resterait vide.
- **Anti-modèles** : photo de banque d’images, plus d’une image, image en fin de titre (seule sur sa ligne), `alt` qui répète le titre, image chargée de texte, second bouton concurrent.
- **Mouvement réduit** : la pastille est ouverte d’emblée.

## Sommaire des chapitres

- **Fragment** : `chapters` (script propre, aucun moteur).
- **Objection** : où en suis-je, et où est ce qui m’intéresse.
- **Mécanique** : juste après le hero, la liste des chapitres en liens d’ancre, une ligne de description chacun. Ensuite le sommaire suit la lecture : dès 1101 px, un rail de repères dans la marge gauche marque le chapitre en cours ; plus étroit, une barre fine « Chapitre n sur N » sous la barre du haut ouvre la liste. Le rail s’efface devant une bande sombre et devant une jauge narrative.
- **Quand** : page longue, huit sections et plus ou plusieurs écrans épinglés.
- **Anti-modèles** : page courte, plus de neuf chapitres, un chapitre par section (regrouper), intitulé de plus de trois mots, chapitre qui pointe vers une partie cachée par la porte de choix.
- **Mouvement réduit** : même sommaire, même rail, même barre ; le chapitre en cours change sans transition.

## Bande de preuve immédiate

- **Fragment** : `proof-band` (chiffres) ; `logos` (logos autorisés).
- **Objection** : est-ce sérieux.
- **Mécanique** : sous le hero, une rangée compacte de 3 ou 4 faits vérifiables (chiffre en grand, libellé court) ou de logos clients autorisés (`01-brand/droits.md`).
- **Quand** : dès qu’on a des chiffres sourcés ou des logos autorisés.
- **Anti-modèles** : logos dont l’usage n’est pas accordé, chiffres arrondis à la hausse, logos estompés par opacité (le contraste tombe, la QA le mesure).
- **Mouvement réduit** : les chiffres s’affichent à leur valeur finale, sans compteur qui monte.

## Problème épinglé

- **Fragment** : `problem-pinned`.
- **Objection** : pourquoi maintenant.
- **Mécanique** : à gauche, le titre, un chapô et un visuel qui change avec le constat actif ; à droite, une liste numérotée dont seul l’élément actif déplie son texte. La section s’épingle le temps de parcourir les constats (40 à 55 vh par constat). Hors épinglage (petit écran, mouvement réduit), c’est une liste illustrée.
- **Quand** : quand le document source porte de vrais constats, dans les mots de l’audience (`01-brand/personas.md`).
- **Anti-modèles** : registre de la peur, constats inventés, liste épinglée plus haute que l’écran (seul l’élément actif déplie, la liste prend la hauteur de son état le plus haut, recalculée au redimensionnement et une fois les polices chargées).
- **Mouvement réduit** : tous les constats dépliés, visuels en vignettes.

## Problème en pièces à conviction

- **Fragment** : `problem-evidence`.
- **Objection** : pourquoi maintenant, est-ce vraiment mon problème.
- **Mécanique** : 3 à 5 pièces que l’audience reconnaît (un extrait de document, un chiffre sourcé, une phrase entendue), chacune légendée, puis un verdict en tampon et la réponse qui mène à l’offre. Sur grand écran, le titre reste collé à gauche pendant que les pièces défilent, sans épinglage : la section ne compte pas dans le budget de trois.
- **Quand** : le problème se montre mieux qu’il ne se raconte, ou les épinglages de la page sont déjà pris. Une seule section de problème par page : `problem-pinned` ou celle-ci.
- **Anti-modèles** : pièces inventées présentées comme réelles, registre de la peur, plus de cinq pièces, verdict qui accuse le visiteur.
- **Mouvement réduit** : pièces visibles d’emblée, tampon posé sans chute.

## Basculement typographique

- **Fragment** : `pivot`.
- **Objection** : et donc, quelle réponse.
- **Mécanique** : une phrase géante qui se révèle mot à mot au défilement (opacité, netteté), puis un trait et la réponse : l’offre comme solution. Piste épinglée courte, avec un temps de tenue pour lire.
- **Quand** : entre le problème et la solution, une fois par page. Le couple problème épinglé → basculement est le seul enchaînement de deux épinglages admis ; une section non épinglée le suit avant tout autre épinglage.
- **Anti-modèles** : dégradé de texte posé sur un élément transformé (certains navigateurs le perdent : transformer le parent, colorer l’enfant), phrase lue mot à mot par les lecteurs d’écran (une copie `sr-only` porte la phrase entière, la version animée est en `aria-hidden`).
- **Mouvement réduit** : la phrase entière, d’emblée.

## Porte de choix qui révèle la suite

- **Fragment** : `choice-gate` (sections de la suite marquées `gated: true` dans la spec).
- **Objection** : laquelle est pour moi.
- **Mécanique** : deux grandes cartes illustrées dont toute la surface est la zone de clic (un vrai `<button>`, étendu par un pseudo-élément). Au choix, la suite de la page apparaît (`hidden` retiré), adaptée à la formule ; un `<noscript>` la rend visible sans script. Un événement de mesure part au choix ; des liens profonds (`?formule=…`, ancres) ouvrent directement la bonne suite.
- **Quand** : seulement pour une offre à variantes réelles.
- **Anti-modèles** : porte qui cache l’essentiel à un visiteur pressé, animations de la partie cachée mesurées avant la révélation (tout vaut zéro : les construire après), glissé automatique à travers plusieurs scènes épinglées (lien direct = saut instantané), focus perdu après la révélation (le donner au titre atteint).
- **Mouvement réduit** : la suite apparaît sans transition.

## Recommandeur d’offre

- **Fragment** : `recommender`.
- **Objection** : laquelle de vos offres est pour moi.
- **Mécanique** : deux ou trois questions courtes, une par écran, en vrais boutons radio ; puis l’offre conseillée, la phrase qui reprend les réponses, ce qu’elle comprend, son prix et son bouton. Une réponse mène à une autre question ou conclut sur une offre, sinon les points départagent. Sur une page à billet, l’offre conseillée règle la formule comme le fait la porte de choix (`landing:choice`, parties `gated` révélées). Mesure : `select_content` avec les réponses.
- **Quand** : trois offres ou plus, ou un bon choix qui dépend du profil ; juste avant la grille tarifaire ou le billet.
- **Anti-modèles** : deux offres seulement (la porte de choix suffit), plus de trois questions sur un même chemin, question sans effet sur le résultat, recommandation sans prix ni contenu, réponse retenue derrière un email.
- **Mouvement réduit** : questions et résultat changent sans transition. Sans script, toutes les offres restent listées avec leur ligne « pour qui ».

## Parcours en scrollytelling

- **Fragment** : `journey`.
- **Objection** : concrètement, qu’est-ce que je fais et qu’est-ce que j’en tire.
- **Mécanique** : un bloc collant d’un écran en deux colonnes. À gauche, « Étape n sur N », un rail qui se remplit jusqu’au point actif, l’étape active sur un panneau, les autres repliées. À droite, une scène `aria-hidden` doublée d’un équivalent `sr-only`, qui change avec l’étape.
- **Quand** : programme, méthode, parcours client en 3 à 6 étapes.
- **Anti-modèles** : plus de 6 étapes, scène qui porte une information absente du texte.
- **Mouvement réduit et petit écran** : liste simple des étapes, chaque scène immobile sous son étape (à côté sur grand écran), jamais masquée.

## Programme ou contenu détaillé

- **Fragment** : `program`.
- **Objection** : qu’est-ce qu’il y a dedans, exactement.
- **Mécanique** : liste des modules ou des livrables, durée et résultat de chacun ; un rail qui se remplit au défilement peut donner le rythme. Un spécimen réel (page de cours, extrait de livrable, capture) vaut mieux qu’une description.
- **Quand** : formation, accompagnement, produit à plusieurs composantes.
- **Anti-modèles** : liste exhaustive qui noie l’essentiel, spécimen non étiqueté comme tel.
- **Mouvement réduit** : rail plein.

## Citation en respiration

- **Fragment** : `quote-interlude` (moteur `annotate`).
- **Objection** : qu’en dit quelqu’un qui l’a vécu.
- **Mécanique** : une seule phrase en grand, sur toute la largeur, signée et datée, avec au plus une annotation à main levée sur les mots qui comptent. Fond clair ou bande sombre (`dark`).
- **Quand** : entre deux sections denses, pour faire respirer la page.
- **Anti-modèles** : citation inventée ou anonyme, plus d’une phrase ou plus de trente mots, compliment sans fait, deux citations de ce type sur la page, bande sombre juste avant ou après une autre.
- **Mouvement réduit** : citation visible d’emblée, annotation posée sans tracé.

## Démonstrateur

- **Fragment** : `demonstrator`, en deux modes. `replay` : une demande s’écrit dans un champ, puis le résultat se compose ligne à ligne ; le visiteur choisit parmi 2 à 4 demandes, Pause et Rejouer restent à portée. `calculator` : le visiteur règle 2 à 4 valeurs et lit une estimation calculée sur la page, avec son détail et la source de chaque coefficient.
- **Objection** : est-ce que ça marche vraiment, pour mon cas.
- **Quand** : produit, méthode ou service dont le résultat se montre mieux qu’il ne se décrit ; après le « comment » (journey, process), avant les preuves ou la conversion.
- **Anti-modèles** : démo truquée ou résultat que le client n’obtiendra pas chez lui, coefficient sans source, estimation présentée comme une promesse, plus de quatre demandes ou réglages, texte important seulement dans l’animation, deux démonstrateurs sur la même page.
- **Mouvement réduit** : chaque demande et son résultat complet s’affichent d’emblée, aucun enchaînement automatique ; le calculateur ne bouge jamais. Sans script : toutes les demandes et leurs résultats à la suite, ou l’exemple calculé et son détail.

## Vitrine d’un objet tangible (bande sombre)

- **Fragment** : `showcase-dark`.
- **Objection** : qu’est-ce que j’emporte de concret.
- **Mécanique** : dans une bande sombre, un objet qui représente le bonus ou le livrable (document, kit, dossier, carte), et des cartes reliées à lui : le survol d’une carte allume la partie de l’objet qui lui correspond, et inversement.
- **Quand** : un bonus ou un livrable qui mérite sa propre section, plutôt qu’une ligne dans une liste.
- **Anti-modèles** : lueurs, ressorts, texte en opacité sur le fond sombre (couleurs pleines).
- **Mouvement réduit** : tout allumé, immobile.

## Carte ou schéma épinglé

- **Fragment** : `map-pinned`.
- **Objection** : est-ce compatible avec ma vie (lieux, fuseaux, rythme, rattrapage).
- **Mécanique** : un schéma ou une carte de marque, des repères posés au défilement, un tracé découvert par un masque (`stroke-dashoffset`), une fin immobile pour lire.
- **Anti-modèles** : tête de tracé qui ressemble à un repère, ondes qui pulsent sans fin (trois passages au plus).
- **Mouvement réduit** : le schéma complet, d’emblée.

## Personnes (experts, intervenants, équipe)

- **Fragment** : `people`.
- **Objection** : avec qui, et sont-ils crédibles.
- **Mécanique** : portrait ou carte de la personne, biographie en trois temps (qui, la preuve, le rôle dans l’offre). Parallaxe légère ou inclinaison réservée aux objets physiques (cartes).
- **Règles** : faits tirés de sources validées seulement, jamais de `00-intel/` ; portrait avec l’accord de la personne (`01-brand/droits.md`) ; mention IA si le portrait est généré ou dérivé (`01-brand/divulgation-ia.md`).
- **Mouvement réduit** : immobile.

## Lettre signée

- **Fragment** : `letter`.
- **Objection** : qui est derrière l’offre, et pourquoi lui faire confiance.
- **Mécanique** : une lettre à la première personne, quatre à six paragraphes, en typographie de livre (mesure de 60 à 70 caractères, lettrine, formule d’appel en petites capitales, citation détachée facultative), le portrait ou les initiales en marge, une signature tracée une fois. La police de lecture vient du jeton facultatif `--font-editorial`, sinon de la police du corps.
- **Quand** : l’offre repose sur une personne (fondatrice, formatrice, consultante). Juste après le problème, la personne y répond ; juste avant l’offre, elle s’engage. Une seule par page.
- **Règles** : faits tirés de sources validées seulement ; une signature se vectorise depuis la vraie, avec l’accord de la personne, jamais inventée.
- **Anti-modèles** : biographie en liste de titres, plus de six paragraphes, photo de banque d’images, citation détachée qui dit autre chose que le texte, empattements sur fond crème et accent terracotta par réflexe.
- **Mouvement réduit** : signature déjà tracée, paragraphe encré plein.

## Témoignages

- **Fragment** : `testimonials` (trois avis choisis) ; `wall` pour le mur qui se déplie (fiche suivante).
- **Objection** : d’autres comme moi l’ont-ils fait.
- **Mécanique** : trois vrais avis signés (nom, rôle, contexte), choisis et placés près du bloc de conversion. Chaque avis porte un résultat concret.
- **Anti-modèles** : avis inventés ou anonymes, initiales sur un dégradé illisible (la QA mesure le contraste à chaque arrêt du dégradé), carrousel automatique.
- **Mouvement réduit** : statique.

## Mur d’avis

- **Fragment** : `wall` (moteur `viewer`).
- **Objection** : d’autres comme moi l’ont-ils fait, et sont-ils nombreux.
- **Mécanique** : les premiers avis visibles, le reste déplié par un bouton qui dit combien il en reste, le focus posé sur le premier avis révélé ; à côté, une colonne qui reste à l’écran porte une note moyenne sourcée et une citation phare. Un avis peut avoir sa vidéo, ouverte dans la visionneuse, avec sous-titres et transcription.
- **Quand** : huit avis signés ou plus, quand le nombre fait partie de la preuve (cohorte, produit grand public, service récurrent). Peut coexister avec `testimonials` : le mur plus haut, trois avis près de l’offre.
- **Anti-modèles** : bandeau qui défile tout seul, avis sans accord, note moyenne sans effectif ni source, étoiles décoratives, vidéo sans sous-titres ni transcription, moins de huit avis.
- **Mouvement réduit** : les avis repliés apparaissent d’un coup, la visionneuse s’ouvre sans fondu, la vidéo attend que le visiteur lance la lecture.

## Cas avant / après

- **Fragment** : `cases`.
- **Objection** : est-ce que ça a marché pour d’autres, et de combien.
- **Mécanique** : deux ou trois cartes de mission (contexte, périmètre, une même mesure avant et après en barres à la même échelle, valeurs écrites à côté, une phrase du client signée). La mesure et sa source se disent dans le chapô.
- **Quand** : prestation, accompagnement, conseil, dès qu’on a des missions mesurées et l’accord des clients.
- **Anti-modèles** : cas inventés présentés comme réels, mesures différentes d’une carte à l’autre, barre sans valeur écrite, client nommé sans accord.
- **Mouvement réduit** : barres pleines d’emblée.

## Mur de réalisations

- **Fragment** : `work-wall` (moteur `viewer`).
- **Objection** : qu’est-ce que ça produit concrètement, et pour quelqu’un comme moi.
- **Mécanique** : 6 à 24 réalisations réelles, chacune avec son secteur, son année et un résultat. Des filtres masquent ce qui ne concerne pas le visiteur et un compteur dit ce qui reste. Deux affichages : `grid`, des cartes à visuel ; `index`, des rangées numérotées comme une table des matières, avec un aperçu qui reste à côté de la liste au survol sur grand écran. Une réalisation peut s’ouvrir en dossier à feuilleter.
- **Quand** : cabinet, agence, indépendant ou produit qui livre des documents. L’`index` remplace la grille de cartes et le bento.
- **Anti-modèles** : réalisation sans résultat, maquette présentée comme un livrable réel, client nommé sans son accord, filtre qui ne garde qu’un élément, plus de 24 réalisations, survol qui cache le texte.
- **Mouvement réduit** : le filtre s’applique d’un coup, l’aperçu change sans fondu. Sans script, tout est visible et les filtres disparaissent.

## Graphique de preuve sourcé

- **Fragment** : `evidence-chart` (moteur `annotate`).
- **Objection** : est-ce vrai, et de combien.
- **Mécanique** : le titre énonce la conclusion, 2 à 6 barres la montrent, une seule est mise en avant, la source suit le graphique. Les barres sont une liste : la donnée est le balisage, lue telle quelle par les lecteurs d’écran. En option (`poster`, éteint par défaut), le chiffre en affiche sous le titre, coupé par le bas de la section sur grand écran.
- **Quand** : une affirmation de la page tient à une comparaison chiffrée et sourcée. Remplace une rangée de cartes de chiffres.
- **Anti-modèles** : chiffre sans source ou arrondi à la hausse, plus de six barres, deux barres mises en avant, titre qui décrit le graphique au lieu de conclure, échelle tronquée qui grossit l’écart.
- **Mouvement réduit** : barres à leur longueur finale d’emblée, annotation posée sans tracé.

## Résultats (respiration)

- **Fragment** : `outcomes`.
- **Objection** : qu’est-ce que ça change.
- **Mécanique** : une rangée compacte sans carte : pour chaque résultat, un filet, un grand numéro, un titre court et une phrase. Les filets se tracent l’un après l’autre.
- **Quand** : après une section dense, pour faire respirer la page.
- **Mouvement réduit** : filets tracés.

## Pour qui, et pour qui ce n’est pas

- **Fragment** : `for-whom`.
- **Objection** : est-ce pour moi.
- **Mécanique** : deux colonnes courtes, « pour vous si » et « pas pour vous si », dans les mots des personas. Le second volet qualifie et rassure.
- **Anti-modèles** : listes génériques valables pour tout le monde.

## Fiche pratique

- **Fragment** : `facts-grid`.
- **Objection** : quand, où, combien de temps, à quel prix.
- **Mécanique** : 4 à 8 paires étiquette et valeur dans une liste de définitions (date, lieu, durée, format, prix, prérequis, langue, accessibilité) ; un fait peut suivre l’état de l’offre (complet, clos).
- **Quand** : événement, formation, atelier, juste sous le hero ou juste avant le bloc de conversion. Pas sous un `hero-editorial`, dont la ligne de faits dit déjà l’essentiel.
- **Anti-modèles** : chiffres de preuve (c’est `proof-band`), avantages déguisés en faits, phrase dans une étiquette, fait qui contredit le bloc de conversion, icône qui porte seule une information.
- **Mouvement réduit** : statique, tout visible.

## Schéma de propriété

- **Fragment** : `ownership-diagram`.
- **Objection** : suis-je enfermé chez vous, que deviennent mes fichiers si je change d’outil ou de prestataire.
- **Mécanique** : un schéma en vrai HTML, lisible comme deux listes. D’un côté, dans un bloc plein, ce que le client possède (fichiers, données, comptes, documents), chacun avec son format ; de l’autre, les outils ou prestataires qui s’y branchent, l’actuel en trait plein, les autres en pointillé. Une légende, puis deux ou trois preuves vérifiables (format d’export, préavis, passation).
- **Quand** : offre qui s’installe dans les données ou les outils du client, quand la peur de l’enfermement freine la décision ; après la démonstration ou le parcours, ou près de la FAQ.
- **Anti-modèles** : promesse de liberté sans preuve vérifiable, concurrent nommé ou logo d’une marque tierce sans autorisation, schéma qui porte une information absente du texte, plus de cinq éléments de chaque côté.
- **Mouvement réduit** : liaisons tracées d’emblée.

## Bloc de conversion en objet

- **Fragment** : `offer-ticket` (une offre datée ; une seule formule : billet horizontal) ; `pricing-table` (plusieurs plans, prix « dès » possible, bascule mensuel / annuel seulement si un plan a un prix annuel) ; `comparison` (tableau comparatif, région défilante à première colonne fixe sur petit écran) ; `process` (étapes après le clic) ; `guarantee` (la garantie, juste après le billet).
- **Objection** : combien, qu’est-ce qui est compris, comment je réserve, et ensuite.
- **Mécanique** : l’offre comme un objet (billet, carte d’offre, bon de commande) : le prix avec ce qu’il comprend, les éventuelles formules en contrôle segmenté accessible (`fieldset`, vraies radios masquées en `sr-only`), une remise expliquée avec une note en `aria-live`, **le seul bouton à l’accent fort de la page**, puis deux colonnes « Compris » et « La suite ». L’état de l’offre (ouverte, liste d’attente, close) vient de la configuration du socle ; le HTML montre l’état ouvert, le navigateur calcule l’état réel.
- **Quand** : toute page qui vend ou inscrit.
- **Anti-modèles** : prix sans ce qu’il comprend, remise dont on ne dit pas ce qui se passe si on l’oublie, compte à rebours en secondes, compteur de places sans vrai chiffre, prix animé sans équivalent lisible.
- **États** : en liste d’attente, le même bouton mène à la liste ; clos, il reste en place, désactivé et lisible (4,5:1), et un lien dessiné en vrai bouton propose la suite (session suivante, alerte).
- **Garantie** : quand elle existe, un sceau décoratif et ses conditions exactes (échéance datée, démarche, délai de remboursement), jamais un « satisfait ou remboursé » sans conditions.
- **Mouvement réduit** : objet immobile, prix lisible d’emblée.

## Ticket à la carte

- **Fragment** : `bundle-receipt` (moteur `offer`).
- **Objection** : combien ça me coûterait à la carte, et pourquoi prendre le pack.
- **Mécanique** : la liste des éléments à cocher, chacun avec son prix ; à côté, un ticket de caisse, collant sur grand écran, dont les lignes apparaissent à chaque case cochée. Dès que la sélection atteint le prix du pack, le ticket le propose avec l’économie exacte, et un clic bascule vers le pack. Le ticket est un formulaire GET vers l’outil de vente, compté en `begin_checkout` avec ses `items`, et suit l’état de l’offre.
- **Quand** : offre vendue en éléments séparés et en pack (parcours complet, abonnement), juste avant ou à la place du billet. Une offre sans éléments séparés prend le billet (`offer-ticket`).
- **Anti-modèles** : prix à l’unité gonflés pour fabriquer une économie (le total barré est la somme de prix réellement pratiqués), pack qui ne contient pas tous les éléments de la liste, plus de sept éléments, total qui défile tout seul.
- **Mouvement réduit** : les lignes apparaissent sans glisser, le total change sans défiler. Sans script : la liste des prix, le pack et un bouton qui envoie le pack.

## Formulaire de capture

- **Fragment** : `lead-capture` (email contre un contenu) ; `form` (démo, rendez-vous, devis) ; `event-registration` (inscription gratuite à un événement, sur place ou en ligne).
- **Objection** : qu’est-ce que je donne, et qu’est-ce que je reçois.
- **Mécanique** : le moins de champs possible (l’email seul si la suite le permet), chaque champ avec son `<label>`, `autocomplete` sur les champs d’identité, champ piège anti-robots hors champ et en `aria-hidden`, message de confirmation en `role="status"`, erreurs annoncées (`aria-invalid` et `aria-describedby`). Une phrase sous le bouton dit ce qui arrive après l’envoi.
- **Consentement** : recevoir la ressource demandée ne demande aucune case, la demande vaut envoi. L’inscription à une lettre ou à la prochaine édition passe par une case facultative et décochée, mesurée (`optin`). Une demande de démo ou de devis n’a pas de case : la mention de confidentialité et son lien, sous le bouton, suffisent. Un endpoint encore en marqueur fait de l’envoi une démonstration, jamais comptée comme lead.
- **Règles** : `cro-form` pour l’optimisation, `lead-magnet` pour le circuit complet si la page capture un email contre un contenu.
- **Anti-modèles** : placeholder qui tient lieu de label, case pré-cochée, champ qui ne paie pas sa friction.

## FAQ

- **Fragment** : `faq`.
- **Objection** : les dernières questions avant d’agir.
- **Mécanique** : accordéon natif `<details>` / `<summary>` (clavier et lecteurs d’écran sans script), questions réelles venues des ventes ou du support. Variante : à côté, une carte collante qui rappelle l’offre et porte le CTA. JSON-LD `FAQPage` seulement sur une page indexée.
- **Anti-modèles** : questions inventées pour placer un argument, réponses qui renvoient ailleurs que vers la conversion.

## Informations légales

- **Fragment** : `legal`.
- **Mécanique** : une fiche sobre, liste de définitions en deux colonnes ; les liens qui ouvrent un nouvel onglet l’annoncent. Le titre est simple.
- **Quand** : vente directe, formation, événement payant : conditions, rétractation, organisateur, accessibilité.

## CTA final (bande sombre)

- **Fragment** : `final-cta`.
- **Mécanique** : une bande sombre, une composition centrée, un titre sur deux lignes (le chiffre fort ou l’échéance), une phrase et le CTA primaire en variante claire. Entrée en rideau possible.
- **Anti-modèles** : nouvel argument introduit à la fin, second objectif.

## Barre d’action mobile collante

- **Fragment** : `sticky-bar`.
- **Mécanique** : sur mobile, une barre fixe en bas d’écran porte le CTA primaire (ou l’appel, pour une page locale). Elle apparaît après le hero et s’efface devant le pied de page pour ne rien masquer.
- **Règles** : hauteur d’au moins 44 px pour le bouton, `padding-bottom` de la page égal à sa hauteur, même destination que le CTA primaire.

## Théâtre de défilement (transverse)

- **Fragment** : moteur `templates/assets/scroll.js` (`theatre.progress` dans la spec, attributs `data-exit` / `data-enter`).
- **Mécanique** : un fil de lecture de 3 px en haut de l’écran et des transitions de jonction déclarées par attributs (`data-exit` / `data-enter` : fondu inversé, dérive, rideau), toutes liées au défilement, sans épinglage propre. Le sommaire des chapitres est une section (`chapters`).
- **Interdits** : cartes qui s’empilent, transition entre le hero et la section suivante.
- **Mouvement réduit et petit écran** : coupé.

## Matières transverses

- **Annotations à main levée** (moteur `annotate`) : un trait tracé une fois sur le mot qui compte (`<mark data-annotate="circle">`). Deux par page au plus, jamais dans un titre qui porte déjà un segment accentué. Sans script, une emphase sobre ; en mouvement réduit, le trait posé sans tracé.
- **Notes en marge** (`.note` dans un `.wrap--notes`, bloc réservé de `base.css`) : la source d’un chiffre, écrite dans la phrase qu’elle documente, flotte dans la marge dès 1101 px et s’ouvre sous la ligne ailleurs. Chaque chiffre de la page peut ainsi porter sa source sans encombrer le texte.
- **Jauge narrative** (champ `gauge` des étapes de `journey` et des modules de `program`) : la progression dite dans l’unité du récit (« Semaine 3 sur 6 »), dans la marge, pendant l’épinglage. Décorative : elle double le moment et le titre.
- **Transitions d’état** (View Transitions) : porte de choix, bascule de la grille tarifaire, recommandeur et filtre du mur de réalisations changent d’état avec un fondu natif, jamais en mouvement réduit ; les noms de transition se posent le temps de la transition seulement.
