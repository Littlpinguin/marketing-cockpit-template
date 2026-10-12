# Référence encre : animation dessinée à la main avec ink-theater

Chargée par `motion-design` quand une vidéo prend le style encre. Doctrine courte dans `08-video/motion.md` § « Encre ». La documentation complète du moteur (API, options, format des clips, licences) est `08-video/lib/ink-theater/README.md` : cette référence dit comment s'en servir dans un projet de marque, elle ne la remplace pas.

## Quand le style encre convient

- Un ton artisanal, pédagogique ou intime : un savoir-faire raconté, une idée expliquée au tableau, une histoire personnelle.
- Un explainer qui gagne à montrer la pensée en train de se dessiner : le trait qui se trace accompagne la phrase qui se dit.
- Un personnage simple, en silhouette, qui marche, salue ou saute.

Il convient moins à une marque dont le style-guide impose un rendu net et géométrique, ou à une vidéo de lancement qui doit montrer un produit tel qu'il est. En cas de doute, la revue de singularité de `08-video/motion.md` tranche.

## Ce que fait le moteur

`08-video/lib/ink-theater/` est un moteur maison, sans dépendance, déterministe : chaque image ne dépend que de la géométrie, d'une graine et de l'instant `t`, condition du rendu image par image d'HyperFrames. Il fournit :

- `InkTheater.drawPath` : un trait d'encre qui se trace, avec le tremblé de la main ;
- `InkTheater.writeText` : une écriture manuscrite lettre à lettre (police Patrick Hand) ;
- `InkTheater.paper` : un fond papier teinté, avec grain ;
- le boil : le trait change d'état à cadence fixe, comme une animation dessinée image par image ;
- `InkPuppet.create` : une silhouette en traits d'encre, animée par les clips de capture de mouvement de `InkClips` ;
- `InkTheater.attach` : la liaison avec la timeline en pause d'HyperFrames.

## Installation dans un projet

Copier le dossier du moteur à la racine du projet HyperFrames, sous le nom `ink/` :

```bash
cp -R 08-video/lib/ink-theater 08-video/projets/<slug>/hyperframes/ink
```

`THIRD_PARTY_NOTICES.md` et `fonts/OFL.txt` suivent le dossier : ils portent les licences de la police et des clips.

## Squelette d'une composition

Même structure que la composition d'exemple `08-video/lib/ink-theater/examples/demo/index.html`, avec les couleurs de la marque au lieu des teintes écrites en dur de la démonstration. `brand.css` est celui que `08-video/scripts/brand-frame.py` a écrit à côté de `frame.md`.

```html
<!doctype html>
<html lang="fr">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=1080, height=1920" />
    <script src="https://cdn.jsdelivr.net/npm/gsap@3.14.2/dist/gsap.min.js"></script>
    <script src="ink/ink-theater.js"></script>
    <script src="ink/ink-puppet.js"></script>
    <script src="ink/clips/clips.js"></script>
    <link rel="stylesheet" href="brand.css" />
    <style>
      @font-face { font-family: "Patrick Hand"; src: url("ink/fonts/PatrickHand-Regular.ttf") format("truetype"); }
      html, body { margin: 0; background: var(--brand-light); }
      #root { position: relative; width: 100%; height: 100%; overflow: hidden; color: var(--brand-dark); }
      #scene { position: absolute; inset: 0; }
    </style>
  </head>
  <body>
    <div id="root" data-composition-id="encre" data-start="0" data-width="1080" data-height="1920" data-duration="8">
      <svg id="scene" class="clip" data-start="0" data-duration="8" viewBox="0 0 1080 1920" width="1080" height="1920"></svg>
    </div>
    <script>
      document.fonts.load('64px "Patrick Hand"').then(function () { return document.fonts.ready; }).then(function () {
        var svg = document.getElementById("scene");
        var scene = InkTheater.scene([]);
        scene.ajouter(InkTheater.paper(svg, { couleur: "var(--brand-light)", graine: 4 }));
        scene.ajouter(InkTheater.writeText(svg, "Le geste d'abord", {
          x: 540, y: 520, taille: 120, ancre: "middle", debut: 0.4, duree: 1.6, couleur: "var(--brand-dark)" }));
        scene.ajouter(InkTheater.drawPath(svg, "M 160 1520 C 420 1470, 690 1560, 920 1500", {
          debut: 0.3, duree: 1.2, epaisseur: 7, couleur: "var(--brand-accent)" }));
        scene.ajouter(InkPuppet.create(svg, {
          sequence: [
            { clip: InkClips.marche, debut: 0, duree: 4 },
            { clip: InkClips.salut, debut: 4, boucle: false }
          ],
          x: 540, y: 1170, echelle: 540, couleur: "var(--brand-dark)" }));
        var tl = gsap.timeline({ paused: true });
        InkTheater.attach(tl, scene.rendre, 8);
        window.__timelines = window.__timelines || {};
        window.__timelines["encre"] = tl;
      });
    </script>
  </body>
</html>
```

Ce qui compte dans ce squelette (contrat de rendu détaillé au § 3 du README du moteur) :

- la scène se construit après le chargement de la police, dans `document.fonts.ready` ;
- la timeline est créée en pause, liée par `InkTheater.attach(tl, scene.rendre, duree)` **une seule fois par composition**, avec `duree` égale au `data-duration` de la racine ;
- `window.__timelines["<id>"]` est enregistré en dernier, avec l'`id` du `data-composition-id` ;
- `data-duration` figure sur la racine et sur le SVG (qui porte `class="clip"` et `data-start`) : HyperFrames ne peut pas déduire la durée d'une animation d'encre.

## Couleurs de marque

- Encre : `var(--brand-dark)` ; papier : `var(--brand-light)`. Les variables se passent telles quelles à l'option `couleur` de chaque objet.
- Accent (`var(--brand-accent)`) : un seul trait ou un seul mot par plan.
- Sur un fond sombre de la marque, inverser : papier `var(--brand-dark)`, encre `var(--brand-text-on-dark)`.
- Jamais de teinte écrite en dur dans un projet client : la démonstration du moteur en contient pour rester autonome, ce n'est pas un modèle.

## Silhouette et clips

- `InkPuppet.create(svg, { clip, ... })` pour un clip seul, ou `{ sequence: [...] }` pour enchaîner des clips, avec un fondu de pose de 0,2 s entre deux entrées. Placement par `x`, `y` (la hanche) et `echelle` (hauteur tête aux pieds).
- `InkClips` donne les clips livrés : `marche`, `course`, `saut`, `salut`, `assis`, `danse`, `coup-de-pied` (`InkClips["coup-de-pied"]` pour un nom à tiret). Durée, plan (profil ou face) et bouclage de chacun : tableau du § 5 du README.
- Un clip qui manque se fabrique depuis un fichier BVH de capture de mouvement avec `08-video/scripts/bvh2clip.py`, qui écrit le clip, met à jour `clips/catalogue.json` et régénère `clips/clips.js` :

```bash
python3 08-video/scripts/bvh2clip.py 02_01.bvh --nom marche --source "CMU 02_01" --sur-place --debut 1.266667 --fin 2.34
```

  Démarrer après la pose de calibration de la première image (`--debut` de 0,1 s au moins), cadrer la fenêtre sur l'action, et compléter `THIRD_PARTY_NOTICES.md` avant toute publication (§ 6 du README).

## Garde-fous

- **Boil entre 8 et 12 changements par seconde** (option `cadence`, la plage du README ; défauts du moteur : 10 pour un trait, 8 pour un texte). Hors de cette plage, on perd l'effet de dessin animé image par image.
- **Peu de traits qui se tracent en même temps.** L'œil suit un geste à la fois ; plusieurs tracés simultanés se lisent comme du bruit.
- **Écriture lisible** : des mots courts, un corps au moins égal à la taille `body` de `frame.md` (44 px sur une toile de 1080 px de petit côté), une durée d'écriture qui laisse le temps de lire le mot une fois tracé.
- **Déterminisme** : pour varier un trait, changer sa `graine`. Ni `Math.random`, ni horloge, ni `requestAnimationFrame` dans la composition.
- **Police** : Patrick Hand est sous licence libre (OFL). Une autre écriture manuscrite imposée par la marque demande d'abord la vérification de ses droits d'embarquement et de rendu vidéo dans `01-brand/droits.md`.

Contrôles avant rendu : `npx hyperframes lint`, `npx hyperframes check`, puis un aperçu.

---

Méthode inspirée d'OpenMontage (calesthio/OpenMontage, AGPLv3), réécrite pour le template : aucun texte ni code repris. Registre : docs/vendored-video.md.
