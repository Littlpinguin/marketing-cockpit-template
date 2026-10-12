# Registre des sources du module vidéo

Ce registre trace tout ce que le module `video` doit à des projets tiers : ce qui est vendorisé (copié avec sa licence), ce qui est installé à côté sans être copié, et ce dont seule la méthode a été reprise, réécrite. Il dit aussi ce qui n'a pas été pris, et pourquoi.

Politique commune à tous les registres `docs/vendored-*.md` : on copie des textes (`SKILL.md`, références, règles), avec la licence de leur auteur et un pied de page d'attribution. **Aucun script externe n'est copié ni exécuté sans audit** : les fichiers Python, shell ou JavaScript des dépôts sources restent chez eux.

## Manim : skills vendorisées

Deux skills du dépôt public [adithya-s-k/manim_skill](https://github.com/adithya-s-k/manim_skill) servent la filière « démonstration conceptuelle ou chiffrée » du module : l'une planifie la scène, l'autre écrit le code Manim. Date de vendorisation : **2026-10-12**.

| Skill du template | Source | Commit | Licence |
|---|---|---|---|
| `.claude/skills/manim-composer/` | `skills/manim-composer` | `cef045011722d285692e3381d12d4d637da56e18` (2026-01-23) | MIT, © 2026 Adithya S Kolavi |
| `.claude/skills/manim-ce/` | `skills/manimce-best-practices` | idem | idem |

Licence constatée sur disque au moment de la copie : le fichier `LICENSE` à la racine du dépôt source (copié en `manim-composer/LICENSE.txt`) et `skills/manimce-best-practices/LICENSE.txt` (copié en `manim-ce/LICENSE.txt`) sont identiques. C'est le texte MIT standard, © 2026 Adithya S Kolavi. Chaque `SKILL.md` renvoie à son `LICENSE.txt` dans son pied de page.

Manim Community Edition lui-même (la bibliothèque Python) n'est pas copié : il s'installe à côté, par `pip install manim`, et `/modules` détecte sa présence.

### Périmètre copié

31 fichiers, tous en Markdown ou en texte, récupérés au commit figé :

- `manim-composer/` (6 fichiers) : `SKILL.md`, `references/narrative-patterns.md`, `references/scene-examples.md`, `references/visual-techniques.md`, `templates/scenes-template.md`, `LICENSE.txt`.
- `manim-ce/` (25 fichiers) : `SKILL.md`, `LICENSE.txt` et les 23 fichiers de `rules/` : `3d`, `animation-groups`, `animations`, `axes`, `camera`, `cli`, `colors`, `config`, `creation-animations`, `graphing`, `grouping`, `latex`, `lines`, `mobjects`, `positioning`, `scenes`, `shapes`, `styling`, `text-animations`, `text`, `timing`, `transform-animations`, `updaters`.

### Adaptations

Les fichiers de `references/`, `templates/` et `rules/` sont repris tels quels. Seuls les deux `SKILL.md` changent :

- **Nom** : `manim-ce` remplace `manimce-best-practices` (convention de nommage par famille du template). `manim-composer` garde son nom.
- **Description** : celle d'origine, avec une dernière ligne ajoutée : « Module vidéo du cockpit : l'entrée est la skill video-production. »
- **Note d'intégration** en français, juste après le frontmatter : source et commit, place dans la chaîne (`video-production` choisit la filière, `manim-composer` planifie, `manim-ce` code, le rendu MP4 entre comme plan dans une composition HyperFrames), couleurs et polices lues dans `01-brand/tokens.json`, installation de Manim à part.
- **Renvois aux exemples Python** : dans `manim-ce/SKILL.md`, les huit renvois à `examples/*.py` et `templates/*.py` ne sont plus des liens. Le nom du fichier reste en texte, suivi de « (exemple non vendorisé : voir le dépôt source) ». Les liens vers `rules/*.md` sont conservés.
- **Pied de page d'attribution** en fin de chaque `SKILL.md`.

Un point de lecture : la description d'origine de `manim-composer` cite encore `manimce-best-practices` et `manimgl-best-practices`. Elle est gardée telle quelle, et la note d'intégration de la skill précise que le premier nom se lit `manim-ce` ici et que le second n'est pas vendorisé.

### Non repris, et pourquoi

| Élément de la source | Raison |
|---|---|
| `skills/manimce-best-practices/examples/*.py` (5 exemples) | Politique du template : aucun script externe copié. |
| `skills/manimce-best-practices/templates/*.py` (3 gabarits de scène) | Idem. |
| `skills/manimgl-best-practices/` | ManimGL est la variante personnelle de 3Blue1Brown (imports `manimlib`, CLI `manimgl`, rendu OpenGL interactif). ManimCE est le standard communautaire, installable par `pip` et piloté en ligne de commande (`manim -qh`) : c'est lui que le module pilote. |

### Procédure de resynchronisation

1. Choisir le nouveau commit sur le dépôt source, relire son journal depuis `cef0450` (renommages, règles ajoutées ou retirées) et vérifier que la licence est toujours MIT.
2. Rejouer la récupération avec `<sha>` à la place du commit courant (seuls le Markdown et les licences sont récupérés, jamais un `.py`) :

   ```bash
   SHA=<nouveau-commit>
   SRC=adithya-s-k/manim_skill
   get() { mkdir -p "$(dirname "$2")"; gh api "repos/$SRC/contents/$1?ref=$SHA" -H "Accept: application/vnd.github.raw" > "$2"; }
   D=.claude/skills/manim-composer
   get skills/manim-composer/SKILL.md $D/SKILL.md
   for f in narrative-patterns scene-examples visual-techniques; do get skills/manim-composer/references/$f.md $D/references/$f.md; done
   get skills/manim-composer/templates/scenes-template.md $D/templates/scenes-template.md
   get LICENSE $D/LICENSE.txt
   D=.claude/skills/manim-ce
   get skills/manimce-best-practices/SKILL.md $D/SKILL.md
   get skills/manimce-best-practices/LICENSE.txt $D/LICENSE.txt
   for f in $(gh api "repos/$SRC/contents/skills/manimce-best-practices/rules?ref=$SHA" --jq '.[].name'); do
     get skills/manimce-best-practices/rules/$f $D/rules/$f
   done
   ```

3. Réappliquer les adaptations ci-dessus sur les deux `SKILL.md` (nom, description, note d'intégration, renvois aux exemples, pied de page). Les fichiers de `references/`, `templates/` et `rules/` s'écrasent tels quels.
4. Si la source ajoute ou retire des règles, mettre à jour la liste des 23 règles et le décompte de fichiers de ce registre.
5. Mettre à jour le commit et la date dans le tableau ci-dessus et dans les deux pieds de page, puis lancer `rtk proxy python3 -m pytest scripts/tests/test_video_module.py -q`.
