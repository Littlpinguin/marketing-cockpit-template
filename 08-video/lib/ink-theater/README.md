# Ink Theater : animation « dessinée à l'encre » pour HyperFrames

## 1. Ce que c'est

Un petit moteur d'animation pour les compositions HyperFrames du module `video`. Il dessine à l'encre sur un SVG : traits qui se tracent, tremblé de la main, « boil » (le trait change d'état 8 à 12 fois par seconde, comme une animation dessinée image par image), écriture manuscrite lettre à lettre, fond papier à grain, et une silhouette de bonhomme animée par des clips de capture de mouvement.

Il est **déterministe** : chaque valeur visuelle est une fonction de la géométrie, d'une graine et de l'instant `t`. Pas d'horloge, pas de hasard non semé. L'image à l'instant `t` est identique à chaque rendu, condition du rendu image par image de HyperFrames.

Contenu du dossier :

```
ink-theater/
├── ink-theater.js          moteur : traits, texte, papier, scène, synchronisation (global InkTheater)
├── ink-puppet.js           silhouette animée par clips (global InkPuppet)
├── clips/                  7 clips de mouvement (<nom>.json), catalogue.json, clips.js (global InkClips)
├── fonts/                  PatrickHand-Regular.ttf et son OFL.txt
├── examples/demo/          composition d'exemple (1080×1920, 6 s)
├── THIRD_PARTY_NOTICES.md  licences de la police et des clips
└── README.md               ce fichier
```

## 2. Installer dans un projet

Copier le dossier dans la racine HyperFrames du projet, sous le nom `ink/` :

```bash
cp -R 08-video/lib/ink-theater 08-video/projets/<slug>/hyperframes/ink
```

Les chemins ci-dessous sont relatifs à `index.html`, qui reste à la racine du projet à côté de `ink/`. Charger dans le `<head>`, dans cet ordre (le moteur avant la silhouette, les clips après) :

```html
<script src="https://cdn.jsdelivr.net/npm/gsap@3.14.2/dist/gsap.min.js"></script>
<script src="ink/ink-theater.js"></script>
<script src="ink/ink-puppet.js"></script>
<script src="ink/clips/clips.js"></script>
<style>
  @font-face { font-family: "Patrick Hand"; src: url("ink/fonts/PatrickHand-Regular.ttf") format("truetype"); }
</style>
```

Pour essayer sans rien écrire, copier la composition d'exemple à la racine du projet HyperFrames, à côté de `ink/` :

```bash
cp 08-video/lib/ink-theater/examples/demo/index.html 08-video/projets/<slug>/hyperframes/index.html
```

La skill `motion-design` fait cette copie quand un projet a besoin de l'encre. Boucle de vérification HyperFrames habituelle : `npx hyperframes lint`, `npx hyperframes check`, `npx hyperframes preview`.

## 3. Contrat de rendu

HyperFrames rend la composition en la parcourant instant par instant. Pour que l'encre suive :

1. **Attendre la police**, puis construire la scène dans `document.fonts.ready.then(…)`. Sans cela, les premières images risquent de s'afficher avec la police de repli.
2. **Créer la timeline en pause** : `gsap.timeline({ paused: true })`.
3. **La lier au rendu** : `InkTheater.attach(tl, scene.rendre, duree)`, avec `duree` égale au `data-duration` de la racine. À appeler **une seule fois par composition** : `attach` ajoute un écouteur `hf-seek` à la fenêtre, et un second appel en ajouterait un second. Le temps reçu par l'écouteur est borné à `[0, duree]`, comme celui que la timeline écrit.
4. **Enregistrer la timeline en dernier** : `window.__timelines["<id>"] = tl`, avec `<id>` identique au `data-composition-id` de la racine, à la fin de la construction. Une timeline enregistrée avant que la scène soit construite est vide pour HyperFrames : le rendu sort blanc.
5. **`data-duration` sur la racine** (et sur le SVG, avec `class="clip"` et `data-start`).
6. **Jamais d'horloge ni de hasard non semé** : ni `Math.random`, ni `Date.now`, ni `requestAnimationFrame`, `setTimeout`, `setInterval`. Un test du dépôt refuse ces appels dans le moteur ; la même règle vaut pour vos compositions. Pour varier un trait, changer sa `graine`.

Comment `attach` synchronise : GSAP anime une valeur `t` de 0 à `duree` sur la timeline, et chaque écriture de cette valeur appelle `scene.rendre(t)`. Cela marche aussi quand HyperFrames se place directement sur un instant (seek). L'événement `hf-seek` est écouté en plus.

Squelette minimal :

```html
<div id="root" data-composition-id="mon-id" data-start="0" data-width="1080" data-height="1920" data-duration="6">
  <svg id="scene" class="clip" data-start="0" data-duration="6" viewBox="0 0 1080 1920" width="1080" height="1920"></svg>
</div>
<script>
  document.fonts.load('64px "Patrick Hand"').then(function () { return document.fonts.ready; }).then(function () {
    var svg = document.getElementById("scene");
    var scene = InkTheater.scene([]);
    scene.ajouter(InkTheater.paper(svg, { graine: 4 }));
    scene.ajouter(InkTheater.writeText(svg, "Bonjour", { x: 540, y: 520, taille: 150, ancre: "middle", duree: 1.4 }));
    var tl = gsap.timeline({ paused: true });
    InkTheater.attach(tl, scene.rendre, 6);
    window.__timelines = window.__timelines || {};
    window.__timelines["mon-id"] = tl;
  });
</script>
```

Ordre de superposition : `paper()` se glisse toujours en premier enfant du SVG, donc sous tout ce qui est dessiné, qu'il soit appelé avant ou après les autres objets. Le reste se superpose dans l'ordre des appels.

## 4. API

Tous les temps sont en secondes, toutes les longueurs en pixels du SVG. Chaque fabrique (`drawPath`, `writeText`, `paper`, `InkPuppet.create`) renvoie `{ element, rendre }` : `element` est le nœud SVG créé, `rendre(t)` dessine l'instant `t`. On les passe à `scene.ajouter(…)`.

### InkTheater

| Fonction | Rôle |
|---|---|
| `InkTheater.drawPath(svg, chemin, options)` | Trait d'encre qui se trace |
| `InkTheater.writeText(svg, texte, options)` | Écriture manuscrite lettre à lettre |
| `InkTheater.paper(svg, options)` | Fond papier teinté, avec grain |
| `InkTheater.scene(objets)` | Regroupe des objets `{ rendre }` : `.ajouter(objet)`, `.rendre(t)` |
| `InkTheater.attach(timeline, rendre, duree)` | Lie un rendu à la timeline GSAP et à `hf-seek` (voir le contrat) |
| `InkTheater.boil(points, t, options)` | Tremblé qui change d'état à cadence fixe |
| `InkTheater.trembler(points, options)` | Tremblé figé d'une liste de points |
| `InkTheater.progression(t, debut, duree)` | Avancement linéaire de 0 à 1, borné ; sans durée, saut de 0 à 1 à `debut` |

**`drawPath(svg, chemin, options)`** : `chemin` est soit une chaîne d'attribut `d` de chemin SVG (échantillonnée dans le navigateur, le SVG doit donc être dans la page), soit un tableau de points `[[x, y], …]`. Le trait est invisible avant `debut`, se trace avec un lissage entrée-sortie jusqu'à `debut + duree`, puis reste.

| Option | Défaut | Rôle |
|---|---|---|
| `debut` | `0` | Début du tracé |
| `duree` | `1` | Durée du tracé |
| `epaisseur` | `4` | Épaisseur du trait |
| `couleur` | `"currentColor"` | Couleur d'encre |
| `tremble` | `1.5` | Amplitude du tremblé en px ; `0` = trait net |
| `cadence` | `10` | Changements d'état du tremblé par seconde ; `0` = figé |
| `graine` | `1` | Graine du tremblé |
| `pas` | `4` | Pas d'échantillonnage d'un chemin donné en chaîne, en px |
| `parent` | le SVG | Nœud où insérer le trait (un `<g>` par exemple) |

**`writeText(svg, texte, options)`** : chaque lettre apparaît à son tour (une espace compte pour un tiers de lettre) et garde une légère rotation de ±2° qui change au rythme du boil. Le texte est découpé par point de code : un émoji reste entier.

| Option | Défaut | Rôle |
|---|---|---|
| `x`, `y` | `0`, `0` | Position de la ligne de base |
| `taille` | `64` | Corps en px |
| `police` | `"Patrick Hand, cursive"` | Famille de police |
| `couleur` | `"currentColor"` | Couleur du texte |
| `ancre` | `"start"` | Alignement : `start`, `middle` ou `end` |
| `debut` | `0` | Instant de la première lettre |
| `duree` | `1` | Durée de l'écriture complète |
| `graine` | `7` | Graine de la rotation des lettres |
| `cadence` | `8` | Changements d'état de la rotation par seconde ; `0` = figée |
| `parent` | le SVG | Nœud où insérer le texte |

**`paper(svg, options)`** : un rectangle plein cadre, teinté, avec un grain fixe (bruit `feTurbulence` à graine constante, qui ne bouge pas d'une image à l'autre).

| Option | Défaut | Rôle |
|---|---|---|
| `couleur` | `"#F5F1E8"` | Teinte du papier |
| `graine` | `3` | Graine du grain, et identifiant du filtre |
| `grain` | `0.9` | Fréquence de base du bruit (plus haut = grain plus fin) |
| `intensite` | `0.08` | Force du grain |

Le filtre de grain est **partagé par graine et par SVG** : un second appel avec la même graine réutilise le filtre du premier et ignore son `grain` et son `intensite`. Une graine par SVG, donc, et une autre graine pour obtenir un autre grain.

**`boil(points, t, options)`** : `amplitude` (défaut `2`), `frequence` (`0.08` : un nouveau point de bruit tous les 12 px de trait environ), `cadence` (`10`), `graine` (`1`). **`trembler(points, options)`** : `amplitude` (`2`), `frequence` (`0.08`), `graine` (`0`). Le tremblé déplace chaque point le long de la normale locale du trait.

Les autres fonctions pures sont exportées pour les tests sous Node et les compositions avancées : `adoucir(p)`, `etatBoil(t, cadence)`, `graineDuBoil(graine, t, cadence)`, `longueur(points)`, `versChemin(points)`, `lettres(texte, debut, duree)`, `aleatoire(graine)`, `hacher(graine, n)`, `bruit(graine, x)`.

### InkPuppet

La silhouette est dessinée par onze segments (tronc, bras, jambes) et un cercle pour la tête, avec le même tremblé et le même boil que les traits. Elle exige que `ink-theater.js` soit chargé avant `ink-puppet.js`.

**`InkPuppet.create(svg, options)`** :

| Option | Défaut | Rôle |
|---|---|---|
| `clip` | | Un clip, par exemple `InkClips.marche` (ou `InkClips["coup-de-pied"]`) |
| `boucle` | `true` | Avec `clip` seul : boucler, ou se figer sur la dernière image (`false`) |
| `sequence` | | Liste d'entrées, à la place de `clip` (voir plus bas) |
| `x`, `y` | `0`, `0` | Position de la hanche, en px (y vers le bas) |
| `echelle` | `400` | Hauteur de la silhouette debout, tête aux pieds, en px |
| `couleur` | `"currentColor"` | Couleur d'encre |
| `epaisseur` | `6` | Épaisseur du trait |
| `graine` | `11` | Graine du tremblé |
| `cadence` | `10` | Changements d'état du tremblé par seconde |
| `tremble` | `1.2` | Amplitude du tremblé en px |
| `parent` | le SVG | Nœud où insérer la silhouette |
| `theatre` | `InkTheater` global | Moteur à utiliser (utile sous Node) |

`clip` ou `sequence` est obligatoire ; chaque clip est validé à la création, une erreur claire en français signale un clip invalide.

**Placement.** La hanche de la première image du clip tombe en `(x, y)` ; les pieds sont environ 0,64 × `echelle` plus bas. Une silhouette de 540 px de haut dont les pieds touchent un sol à `y = 1515` se règle donc avec `x: 540, y: 1170, echelle: 540`. Un clip enregistré avec `--sur-place` ne se déplace pas : pour la faire avancer, décaler son groupe dans un objet de la scène, par exemple

```js
scene.ajouter({ rendre: function (t) {
  marcheur.element.setAttribute("transform", "translate(" + (t * 90) + " 0)");
  marcheur.rendre(t);
} });
```

**Séquences.** `sequence` est une liste d'entrées `{ clip, debut, duree, boucle }` :

| Champ | Défaut | Rôle |
|---|---|---|
| `clip` | | Le clip joué |
| `debut` | `0` | Instant où l'entrée démarre (les entrées sont triées par `debut`) |
| `duree` | | Temps pendant lequel l'entrée avance |
| `boucle` | `true` | `false` : joué une fois |

Règles de durée :

- une entrée **en boucle sans `duree`** boucle jusqu'à l'entrée suivante (la dernière boucle sans fin) ;
- une entrée avec **`duree` explicite** avance pendant ce temps puis tient sa dernière pose ;
- une entrée **`boucle: false` sans `duree`** joue le clip une fois et tient sa dernière image ;
- avant la première entrée, la première image de la première entrée est tenue ;
- entre deux entrées, un **fondu de pose de 0,2 s** (`InkPuppet.FONDU`) part de la pose que l'entrée précédente avait à cet instant.

Dans l'exemple, la marche tourne de 0 à 3,5 s, puis le salut démarre à 3,5 s et ne joue qu'une fois (`boucle: false`, `duree: 2.5`).

**Autres fonctions de `InkPuppet`** :

| Fonction | Rôle |
|---|---|
| `InkPuppet.sequence(entrees)` | Valide les clips et renvoie `{ at(t) }`, la pose de la séquence à l'instant `t` |
| `InkPuppet.pose(clip, t, { boucle })` | Les 13 points du clip à l'instant `t`, interpolés entre deux images (`boucle` : `true` par défaut). Un `t` négatif ou non fini vaut 0 |
| `InkPuppet.valider(clip)` | Renvoie `true` ou lève une erreur : fps non fini ou nul, articulations inattendues, aucune image, image qui n'a pas 13 points, point non fini |
| `InkPuppet.melanger(a, b, x)`, `sequenceAt(entrees, t)`, `versSVG(pose, { x, y, echelle })`, `subdiviser(a, b, n)` | Briques internes, exportées pour les tests |
| `InkPuppet.ARTICULATIONS`, `SEGMENTS`, `FONDU` | Les 13 noms d'articulations, les 11 segments, la durée du fondu (0,2 s) |

**Format d'un clip** (`clips/<nom>.json`) : `{ nom, fps, articulations, images, plan, source, licence }`. `articulations` est toujours `tete, cou, epaule_g, coude_g, main_g, epaule_d, coude_d, main_d, hanche, genou_g, pied_g, genou_d, pied_d`. Chaque image est une liste de 13 points `[x, y]`, normalisés : hanche de la première image en `(0, 0)`, hauteur tête-pieds égale à 1, `y` vers le haut. Les clips `plan: "sagittal"` sont de profil et regardent vers la droite de l'image ; les clips `plan: "frontal"` font face à la caméra.

## 5. Clips livrés

Tableau tiré de `clips/catalogue.json`. `InkClips` est un objet global (chargé par `clips/clips.js`) indexé par le nom du clip : `InkClips.marche`, `InkClips["coup-de-pied"]`.

| Clip | Durée | Plan | Essai CMU | Boucle |
|---|---|---|---|---|
| `marche` | 1,07 s | sagittal, sur place | 02_01 | oui : un cycle de pas complet (1,1 s) |
| `course` | 1,10 s | sagittal, sur place | 09_01 | non : le fichier source dure 1,2 s, trop peu pour une fenêtre de 30 images ou plus qui boucle ; joint visible, à jouer avec `boucle: false` |
| `saut` | 3,33 s | sagittal | 13_11 | non : saut en avant, à jouer une fois |
| `salut` | 2,57 s | frontal | 111_37 | non : geste, à jouer une fois |
| `assis` | 6,00 s | frontal | 143_18 | oui, avec un léger raccord (s'assoit puis se relève) |
| `danse` | 6,00 s | frontal | 05_02 | non : à jouer une fois |
| `coup-de-pied` | 4,00 s | sagittal | 10_01 | non : à jouer une fois |

La durée est celle du catalogue (images moins une, divisées par la cadence de 30 i/s) ; une boucle dure une image de plus. Les clips de la base CMU sont libres de droits, avec citation : voir `THIRD_PARTY_NOTICES.md`.

## 6. Ajouter un clip

Un clip se fabrique depuis un fichier BVH de capture de mouvement (la base CMU en propose des milliers) avec `08-video/scripts/bvh2clip.py`, qui écrit `clips/<nom>.json`, met à jour `clips/catalogue.json` et régénère `clips/clips.js` :

```bash
python3 08-video/scripts/bvh2clip.py 02_01.bvh --nom marche --source "CMU 02_01" --sur-place --debut 1.266667 --fin 2.34
```

| Option | Rôle |
|---|---|
| `--nom` | Nom du clip : minuscules, chiffres et tirets (`coup-de-pied`) |
| `--source` | Origine citée dans les notices (`"CMU 02_01"`) |
| `--plan auto\|frontal\|sagittal` | Plan de projection. `sagittal` : de profil, vers la droite de l'image ; `frontal` : face caméra. `auto` : sagittal si la hanche se déplace de plus d'une demi-hauteur, frontal sinon |
| `--sur-place` | Annule le déplacement horizontal de la hanche (marche, course) |
| `--debut`, `--fin` | Fenêtre en secondes. Défaut : tout le fichier. Les clips livrés font au moins 30 images et au plus 6 s : les tests du dépôt vérifient cette plage |
| `--fps` | Cadence du clip (défaut `30`) |
| `--licence` | Licence écrite dans le clip (défaut : celle de la base CMU) |
| `--sortie` | Dossier de sortie (défaut : `08-video/lib/ink-theater/clips/`) |

**Piège de la pose en T.** Dans les BVH de la base CMU, la première image est souvent une pose de calibration : bras écartés à l'horizontale (de profil, mains à hauteur d'épaule). Le clip saute alors dès l'image suivante, et à chaque tour de boucle. Les sept clips livrés démarrent à `--debut 0.1` pour l'éviter ; faire de même, et décaler `--fin` d'autant. Les tests du dépôt (`scripts/tests/test_video_ink_clips.py`) refusent un clip dont la première image est une pose en T ou dont les deux premières images sont très éloignées.

**Boucler proprement.** Pour un clip qui tourne (marche, course), choisir une fenêtre qui couvre exactement un cycle de pas (début et fin dans la même phase) : c'est ce qui rend la marche livrée sans raccord (`--debut 1.266667 --fin 2.34`, un cycle de 33 images).

**Après l'ajout**, compléter `THIRD_PARTY_NOTICES.md` (clip, essai, description, licence de la source) : un clip sans notice ne se publie pas.

Commandes des sept clips livrés (BVH de la base CMU, via le miroir `una-dinosauria/cmu-mocap`, hors dépôt) :

```bash
S=08-video/scripts/bvh2clip.py
python3 $S 02_01.bvh  --nom marche       --source "CMU 02_01"  --sur-place --debut 1.266667 --fin 2.34
python3 $S 09_01.bvh  --nom course       --source "CMU 09_01"  --sur-place --debut 0.1 --fin 3.1
python3 $S 13_11.bvh  --nom saut         --source "CMU 13_11"  --debut 0.1 --fin 4.1
python3 $S 111_37.bvh --nom salut        --source "CMU 111_37" --plan frontal --debut 0.1 --fin 5.1
python3 $S 143_18.bvh --nom assis        --source "CMU 143_18" --debut 0.1 --fin 6.1
python3 $S 05_02.bvh  --nom danse        --source "CMU 05_02"  --plan frontal --debut 0.1 --fin 6.1
python3 $S 10_01.bvh  --nom coup-de-pied --source "CMU 10_01"  --plan sagittal --debut 0.1 --fin 4.1
```

## 7. Marque

Dans un projet client, l'encre et le papier viennent de la marque, jamais de valeurs en dur :

- couleur d'encre : `var(--brand-dark)` ; couleur de papier : `var(--brand-light)`. Ce sont des variables de `brand.css`, écrit à côté de `frame.md` par `08-video/scripts/brand-frame.py` (lier le fichier avec `<link rel="stylesheet" href="brand.css">`) ;
- elles se passent telles quelles à l'option `couleur` de chaque objet : `InkTheater.paper(svg, { couleur: "var(--brand-light)" })`, `InkTheater.drawPath(svg, chemin, { couleur: "var(--brand-dark)" })`, `InkPuppet.create(svg, { clip: InkClips.marche, couleur: "var(--brand-dark)" })`. Les couleurs de la racine (`color`) se règlent aussi avec ces variables ;
- la couleur d'accent (`var(--brand-accent)`) se réserve à un seul trait ou un seul mot par plan ;
- la police d'écriture : Patrick Hand est libre (OFL), mais si une marque impose une autre écriture manuscrite, **valider ses droits d'embarquement et de rendu vidéo dans `01-brand/droits.md`** avant de remplacer le fichier et le `@font-face`.

L'exemple de ce dossier écrit les teintes du papier et de l'encre en dur pour rester autonome : c'est une démonstration, pas un modèle de projet client.

## 8. Licences

- Le moteur (`ink-theater.js`, `ink-puppet.js`) et la composition d'exemple : licence MIT du dépôt.
- La police Patrick Hand : SIL Open Font License 1.1 (`fonts/OFL.txt`). Elle s'embarque et se redistribue, elle ne se vend pas seule.
- Les clips de mouvement : dérivés de la base de capture de mouvement de la CMU, libre pour tout usage avec citation.

Détail, copyright et citation exacte : `THIRD_PARTY_NOTICES.md`. Ce fichier et `fonts/OFL.txt` doivent suivre le dossier quand il est copié sous `ink/`.
