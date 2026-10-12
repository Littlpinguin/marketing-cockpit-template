# Doctrine du motion design de marque

Chargée par `motion-design` et `video-production` pour tout ce qui est animé : titres, chiffres, data visualisation, habillages, logos, transitions de marque, 3D, personnages, encre, Manim. Elle complète `01-brand/style-guide.md` et `01-brand/design-anti-generique.md`, qui priment.

## Principes

- **Le mouvement sert le message.** Chaque animation montre quelque chose : une relation (ceci entraîne cela), une hiérarchie (ceci d'abord), une transformation (avant, après), une quantité (ce chiffre grandit). Un mouvement qui ne montre rien se supprime.
- **La marque est dans les atomes.** Couleurs, polices, graisses et rayons viennent de `frame.md` et `brand.css`, générés depuis `01-brand/tokens.json` par `08-video/scripts/brand-frame.py`. Aucune valeur écrite à la main dans une composition.
- **La composition est libre.** Mise en page, rythme et métaphore visuelle se décident pour chaque vidéo. Deux vidéos de la marque se reconnaissent à leurs atomes, pas à un gabarit commun.
- **Un objet signature, rare.** Si la vidéo a un élément visuel qui lui est propre (une forme, un geste, un motif), il revient sur un ou deux temps forts, pas sur chaque scène. Répété partout, il devient un gabarit.

## Profil de goût

Avant toute production, une phrase de lecture : ce que la vidéo doit faire comprendre ou ressentir, à qui, sur quelle plateforme. « Moderne et épuré » n'est pas une lecture ; « un dirigeant de PME comprend, sans le son, quelle tâche l'outil lui retire » en est une.

Puis trois curseurs, notés de 1 à 5 et consignés dans `decisions.md` avec une ligne de justification :

- **Densité**, de 1 (de l'air : une idée par plan, du vide autour) à 5 (du plein : données, couches et appuis superposés).
- **Énergie du mouvement**, de 1 (posé : tenues longues, entrées douces) à 5 (nerveux : changements rapprochés, accents marqués).
- **Audace**, de 1 (sobre : la marque parle par la justesse) à 5 (signature : un parti pris qui se remarque et se discute).

Les notes se lisent ensemble. Énergie haute et densité basse donnent des temps courts et nets, pas des schémas chargés. Densité haute et énergie basse donnent des cadres stables et des tenues assez longues pour lire.

Articulation avec la skill `design-taste`, qui pose les mêmes curseurs côté web (`VISUAL_DENSITY`, `MOTION_INTENSITY`, `DESIGN_VARIANCE`, notés de 1 à 10) : une note vidéo vaut à peu près la moitié de la note web. Quand une campagne a une landing et une vidéo, partir des curseurs de la landing et les ramener à l'échelle vidéo plutôt que d'en inventer d'autres.

Un profil peut être fixé une fois pour la marque et réutilisé : chaque projet le reprend dans son `decisions.md`, ou dit pourquoi il s'en écarte. L'inscrire dans `01-brand/style-guide.md` est une décision humaine.

## Revue de singularité

Avant de présenter le storyboard, puis avant le rendu, trois questions, réponses écrites dans `decisions.md` :

1. La vidéo est-elle reconnaissable sans le logo ? (Masquer le logo et le plan de fin : la marque reste-t-elle visible ?)
2. Aurait-on pu la produire telle quelle pour un concurrent, en changeant seulement le nom ?
3. Quel plan ne ressemble à aucun gabarit ? (Le nommer.)

Si les réponses sont non, oui et aucun : retravailler avant de rendre, en revenant à la lecture, aux curseurs, à la métaphore visuelle ou à l'objet signature. Les marqueurs du look générique à éviter sont listés dans `01-brand/design-anti-generique.md`.

## Promesse de mouvement et variété

- Une vidéo promise « en mouvement » (motion design, animation, explainer animé) ne retombe jamais en diaporama d'images fixes zoomées lentement. Si les outils disponibles ne permettent pas le mouvement promis, le dire avant de produire et proposer une autre filière ou un autre format. Jamais de substitution silencieuse.
- Jamais trois scènes du même type d'affilée (trois cartons de texte, trois chiffres, trois illustrations) : chaque scène a son sujet visuel principal, différent de celui de la précédente.
- Le constat `fige` de `08-video/scripts/qa-video.py` (image figée 2 s ou plus) se lit comme un signal : tenue voulue sur un temps fort, ou plan mort à animer. Même lecture pour le constat `plan-long`.

## Choisir le moteur

- **HyperFrames, par défaut** : compositions HTML animées, rendues image par image. Le plugin s'installe avec le module `video` (`/modules`) ; ses skills se nomment `hyperframes:*`, et la passerelle de marque est la skill `motion-design`.
- **Manim**, pour une démonstration conceptuelle ou mathématique (une équation qui se transforme, un graphe qui se construit, une preuve visuelle) : `manim-composer` planifie, `manim-ce` écrit le code, le rendu MP4 entre comme plan vidéo dans la composition HyperFrames.
- **ffmpeg**, pour l'assemblage simple : couper, concaténer, recadrer, réencoder, incruster des sous-titres, sans composition animée.
- Le moteur se choisit au concept et se consigne dans `decisions.md`. En changer en cours de projet est une décision : la dire à l'humain avec sa raison, et la consigner. Jamais de changement silencieux.

## Repères typographiques

Les tailles de départ des rôles typographiques sont écrites dans `frame.md` par `08-video/scripts/brand-frame.py`, pour une toile de 1080 px de petit côté :

| Rôle | Taille de départ | Usage |
|---|---|---|
| `display` | 120 px | Titre d'ouverture, mot unique |
| `headline` | 84 px | Titre de scène |
| `title` | 60 px | Intertitre, nom dans un bandeau |
| `body` | 44 px | Texte courant, ligne d'appui |
| `stat` | 160 px | Chiffre mis en avant |
| `label` | 30 px | Source, date, mention courte (police mono, capitales) |

Ces tailles dépassent celles du web : une vidéo se lit sur un téléphone tenu à bout de bras, souvent en mouvement, sans zoom ni retour en arrière, et chaque texte ne reste que quelques secondes. Ce sont des points de départ propres au module, pas une norme externe : ils se vérifient.

- Ne descendre sous la taille `body` qu'après vérification sur un téléphone réel, en main, à distance de lecture normale. Le `label` reste réservé aux mentions courtes.
- Familles, graisses et interlignages viennent de `01-brand/tokens.json` à travers `frame.md`. Pour les changer : modifier les tokens, puis régénérer `frame.md` et `brand.css` avec `python3 08-video/scripts/brand-frame.py <dossier> --aspect <toile>`. Les tailles de départ sont des constantes du script.
- Ne jamais éditer `frame.md` à la main. `brand-frame.py --check` signale toute dérive par rapport à la marque.

## 3D

La 3D sert quand le spectateur doit voir un objet sous plusieurs angles (un produit, une pièce, un emballage) ou parcourir un espace (un lieu, un parcours). Elle ne sert pas à décorer un titre.

Deux niveaux : une **maquette** (volumes simples, sans texture) pour caler caméra, cadrage et mise en place, validée avec le storyboard ; puis la **production** (modèles, matières, lumière) pour le rendu. Aucun asset payant avant la maquette validée.

Détail (sources d'assets, licences, rendu par l'adaptateur Three.js d'HyperFrames) : `.claude/skills/motion-design/references/3d.md`.

## Personnages

Un personnage aide quand la vidéo raconte (quelqu'un vit le problème, puis la solution) ou quand la marque a une mascotte. Il ne s'ajoute pas pour « humaniser » un sujet qui n'en a pas besoin.

Méthode en quatre temps : fiche personnage (silhouette, proportions, palette, expressions, ce qu'il ne fait jamais), rig (articulations et pivots), bibliothèque de poses, actions calées sur les temps forts du script. Détail et techniques (Lottie, marionnette SVG, silhouette à l'encre) : `.claude/skills/motion-design/references/personnages.md`.

## Encre

Style dessiné à la main, produit par le moteur maison `08-video/lib/ink-theater/` : traits qui se tracent, tremblé de la main, boil (le trait change d'état à cadence fixe, comme une animation dessinée image par image), écriture manuscrite lettre à lettre, fond papier, silhouette animée par des clips de capture de mouvement. Le moteur est déterministe et se cale sur la timeline d'HyperFrames.

Il convient à un ton artisanal, pédagogique ou intime, moins à une marque dont le style-guide impose un rendu net et géométrique. L'encre et le papier prennent leurs couleurs dans `brand.css`. Détail : `.claude/skills/motion-design/references/encre.md` et `08-video/lib/ink-theater/README.md`.

## Manim

Pour une démonstration conceptuelle ou mathématique : la skill `manim-composer` planifie la scène plan par plan, puis `manim-ce` écrit le code Manim Community. Couleurs et police viennent de `01-brand/tokens.json`. Le rendu MP4 entre comme un plan dans la composition HyperFrames, qui garde l'habillage de marque. Manim s'installe à part (`pip install manim`).

## Interdits

- Effets génériques : glitch, flash blanc, zoom de transition, particules décoratives, sauf si la marque les revendique dans `01-brand/style-guide.md`.
- Presets visuels d'HyperFrames (`frame-presets`) dans un projet client : le `frame.md` généré par `brand-frame.py` fait foi.
- Toute couleur hors palette, tout dégradé autre que celui de la marque, toute police hors tokens.
- Les tropes bannis de `01-brand/style-guide.md` : {{BRAND_BANNED_VISUALS}}.
- Le logo animé en ouverture : le logo vient au plan de fin, ou discret en zone sûre (`frame.md`).
- Le texte en double : un sous-titre qui répète mot pour mot un carton affiché au même moment. Chaque texte a un seul rôle.

---

Méthode inspirée d'OpenMontage (calesthio/OpenMontage, AGPLv3), réécrite pour le template : aucun texte ni code repris. Registre : docs/vendored-video.md.
