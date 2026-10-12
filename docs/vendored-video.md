# Registre des sources du module vidéo

Ce registre trace tout ce que le module `video` doit à des projets tiers : ce qui est vendorisé (copié avec sa licence), ce qui est installé à côté sans être copié, ce dont seule la méthode a été reprise, réécrite, et ce qui est consulté à l'usage sans entrer dans le dépôt. Il dit aussi ce qui n'a pas été pris, et pourquoi.

Politique commune à tous les registres `docs/vendored-*.md` : on copie des textes (`SKILL.md`, références, règles), avec la licence de leur auteur et un pied de page d'attribution. **Aucun script externe n'est copié ni exécuté sans audit** : les fichiers Python, shell ou JavaScript des dépôts sources restent chez eux.

| Source | Licence | Dans le template |
|---|---|---|
| [heygen-com/hyperframes](https://github.com/heygen-com/hyperframes) | Apache-2.0 | Installé par `/modules` comme plugin Claude Code, rien de copié |
| [calesthio/OpenMontage](https://github.com/calesthio/OpenMontage) | AGPLv3 | Méthode lue puis réécrite, rien de copié ; code lourd écrit en salle blanche |
| Police Patrick Hand, base de capture de mouvement de la CMU | OFL 1.1 ; libre pour tout usage | Livrées avec le moteur ink-theater, notices jointes |
| [yihui-dev/awesome-opus5-5-videos](https://github.com/yihui-dev/awesome-opus5-5-videos) | MIT (dépôt) ; vidéos et prompts à leurs créateurs | Consulté à l'usage, en cache local ignoré par Git, rien de copié |
| [adithya-s-k/manim_skill](https://github.com/adithya-s-k/manim_skill) | MIT | Deux skills vendorisées (`manim-composer`, `manim-ce`) |

## HyperFrames : installé, pas vendorisé

Dépôt : [heygen-com/hyperframes](https://github.com/heygen-com/hyperframes), licence Apache-2.0. HyperFrames est le moteur de composition et de rendu du module : compositions HTML pilotées par une timeline, rendu par Chrome headless, CLI `npx hyperframes`, et des workflows publiés sous forme de skills `hyperframes:*` (`motion-graphics`, `faceless-explainer`, `product-launch-video`, `general-video`, `embedded-captions`…).

Il s'installe comme plugin Claude Code officiel, `hyperframes@hyperframes`, depuis la marketplace `heygen-com/hyperframes`. C'est `/modules` qui l'installe, à l'activation du module `video`, en portée `local` : seul `.claude/settings.local.json`, non versionné, change. La version installée est notée dans `.setup-completed` (`modules.video.hyperframes`) et `/health-check` la compare à celle de `claude plugin list`. Désactiver le module propose de désinstaller le plugin, sans l'imposer.

**Pourquoi pas de copie.**

- L'amont publie vite (CLI, workflows, skills) : une copie figée vieillirait entre deux resynchronisations, et chaque fork devrait la rejouer.
- Le manifeste du plugin verrouille la version du CLI que ses skills appellent : skills et CLI restent accordés sans que le template s'en charge.
- Les skills `hyperframes:*` ne se chargent que là où le module est actif ; un fork sans vidéo n'en porte rien.
- Aucun fichier HyperFrames n'entre dans le dépôt : ni skill, ni preset, ni script.

**Ce que le template ajoute par-dessus.**

- La skill passerelle `motion-design` : la marque dans tout ce qui bouge, le profil de goût et la revue de singularité de `08-video/motion.md`, le choix du workflow, les règles de rendu (pièges connus).
- Une charte de projet générée, jamais écrite à la main : `08-video/scripts/brand-frame.py` écrit `frame.md` (le fichier de design qu'HyperFrames lit en premier) et copie `brand.css`, nouvelle cible de `scripts/build-tokens.py` (`08-video/lib/brand.css`), depuis `01-brand/tokens.json` ; `--check` signale une dérive.
- Le routage : `video-production` choisit la filière, tient les trois validations et le contrat de coût, puis passe la main au workflow par un `BRIEF.md` qui remplace l'entretien d'intention d'HyperFrames.
- La QA du rendu : `08-video/scripts/qa-video.py` et l'agent `video-reviewer`.

**Règles de priorité.**

- Les skills du projet passent avant celles du plugin : toute demande vidéo commence par `video-production`.
- Présentation ou deck : skill `slides`, jamais `hyperframes:slideshow`.
- Presets visuels d'HyperFrames (`frame-presets`) interdits en projet client : le `frame.md` généré fait foi. Seule exception, consignée dans `decisions.md` : la peau de sous-titres (`caption-skin.html`).
- Fournisseurs externes appelés par HyperFrames (voix et musique HeyGen, musique Lyria) : coût ou quota annoncé avant usage, sous le contrat de coût de `video-production`.

## OpenMontage : méthode réécrite, rien de copié

Dépôt : [calesthio/OpenMontage](https://github.com/calesthio/OpenMontage), licence **AGPLv3**. Commit consulté : `9327439db69021ab4b0e2776729bf3b58fdb5a87` (2026-10-03).

**Pourquoi rien n'est copié.** L'AGPLv3 est une licence à copyleft fort : une œuvre qui reprend du texte ou du code sous AGPLv3 doit être redistribuée sous la même licence. Elle est incompatible avec la licence MIT du template, que chaque fork doit pouvoir garder. La méthode de production d'OpenMontage (ses étapes, ses contrôles, ses critères) a donc été lue, puis réécrite avec nos mots dans nos skills et notre doctrine : aucune phrase reprise, aucune structure de tableau recopiée, aucun fichier copié.

| Méthode d'OpenMontage (fichiers consultés) | Où elle vit dans le template |
|---|---|
| Pipelines par type de vidéo et points de validation (`skills/pipelines/`, `skills/meta/checkpoint-protocol.md`) | `video-production` : filières, trois validations bloquantes, contrôle avant rendu |
| Annonce des coûts avant dépense (`AGENT_GUIDE.md`) | `video-production` § « Contrat de coût », `couts.md` du projet |
| Journal de décisions | `video-production` : `decisions.md`, en ajout seul |
| Propositions de concepts (`skills/pipelines/explainer/proposal-director.md`) | `video-production`, étape « Concepts » : deux ou trois concepts, chacun avec son chemin outillé, son coût et son risque |
| Analyse d'une vidéo de référence (`skills/meta/video-reference-analyst.md`) | `video-production`, cadrage : ce qu'on garde, ce qu'on change |
| Format court, typographie (`skills/creative/short-form.md`, `skills/creative/typography.md`) | `08-video/formats.md` |
| Récit, voix (`skills/creative/storytelling.md`, `skills/meta/voice-performance-director.md`) | `08-video/narration.md` |
| Direction de goût (`skills/meta/taste-direction.md`) | `08-video/motion.md` : profil de goût, revue de singularité |
| Pièges d'HyperFrames (`skills/core/hyperframes.md`) | `motion-design` § « Règles de rendu (pièges connus) » |
| Risque de diaporama et variété des scènes (`slideshow_risk`) | `08-video/motion.md` § « Promesse de mouvement et variété », agent `video-reviewer` |
| Relecture d'un rendu (`skills/meta/reviewer.md`) | agent `video-reviewer` |
| Clips tirés d'une vidéo longue (`skills/pipelines/clip-factory/`, `skills/pipelines/podcast-repurpose/`) | `video-repurpose` |
| Démo d'écran (`skills/pipelines/screen-demo/`, `skills/creative/screen-recording.md`) | `08-video/montage.md` § « Démo produit et capture d'écran » |
| Prompting des modèles vidéo (`skills/creative/video-gen-prompting.md`, `skills/creative/prompting/`) | `video-generation` : plan en cinq aspects, notes par famille de modèles |
| Plan de b-roll, stock (`skills/creative/broll-planning.md`, `skills/creative/stock-sourcing-usage.md`) | `video-generation` § « Stock ou génération » |
| Montage documentaire (`skills/pipelines/documentary-montage/`) | `video-documentary`, `08-video/documentaire.md` |
| Animation de personnages, mondes 3D (`skills/pipelines/character-animation/`, `skills/creative/3d-world-generation.md`) | `motion-design` : `references/personnages.md`, `references/3d.md` |

Les fichiers qui reprennent une de ces méthodes le disent en pied de page : « Méthode inspirée d'OpenMontage (calesthio/OpenMontage, AGPLv3), réécrite pour le template : aucun texte ni code repris. Registre : docs/vendored-video.md. » Ce sont les skills `video-production`, `motion-design` et ses trois références (`references/3d.md`, `references/personnages.md`, `references/encre.md`), `video-repurpose`, `video-documentary`, `video-generation`, `reel-talking-head`, et la doctrine `08-video/formats.md`, `08-video/montage.md`, `08-video/narration.md`, `08-video/motion.md` et `08-video/documentaire.md`.

**Non repris** (hors périmètre du module, réévaluables plus tard) : avatars présentateurs, doublage et localisation, Backlot, Remotion, Blender, ManimGL, génération vidéo locale sur GPU, publication automatique. Le code d'OpenMontage n'est pas repris non plus, son moteur d'encre compris : le template a ses propres outils, écrits en salle blanche.

**Protocole de salle blanche.**

- `08-video/scripts/bvh2clip.py`, `08-video/lib/ink-theater/ink-theater.js`, `08-video/lib/ink-theater/ink-puppet.js` et le paquet `08-video/scripts/corpus_documentaire/` (avec sa commande `corpus.py`) ont été écrits d'après une spec fonctionnelle rédigée pour le template (format des clips, primitives de dessin, interface des sources, commandes), par des agents à qui l'ouverture du code d'OpenMontage était interdite par écrit, clone local comme dépôt en ligne.
- Les agents qui ont écrit la doctrine et les skills pouvaient lire les fichiers de méthode de la table ci-dessus, pour les idées seulement, avec la consigne de n'en recopier ni phrase ni structure de tableau. Plusieurs tours de revue ont relu leurs textes contre ces fichiers et réécrit les passages trop proches d'une traduction.
- Les chiffres d'OpenMontage sans source n'ont pas été repris : une valeur chiffrée de la doctrine cite sa source (`docs/etat-de-lart/video-courte.md` ou une page vérifiée) ou se formule comme une mesure à faire.
- Aucun fichier d'OpenMontage n'est dans le dépôt. Un contributeur qui reprend ce travail suit la même règle : lire la méthode, écrire avec ses mots, ne jamais coller.

## Ink-theater : données tierces

Le moteur d'encre (`08-video/lib/ink-theater/ink-theater.js`, `ink-puppet.js`) est du code maison, sous la licence MIT du dépôt, écrit en salle blanche (section précédente). Deux données tierces l'accompagnent :

| Élément | Fichiers | Origine | Licence |
|---|---|---|---|
| Police **Patrick Hand** | `fonts/PatrickHand-Regular.ttf`, `fonts/OFL.txt` | Patrick Wagesreiter, récupérée dans le dépôt Google Fonts (`ofl/patrickhand`) | SIL Open Font License 1.1 : usage commercial et incorporation dans une vidéo admis, vente seule interdite, `OFL.txt` toujours joint |
| 7 clips de mouvement | `clips/*.json`, `clips/catalogue.json`, `clips/clips.js` | Silhouettes 2D (13 articulations projetées sur un plan et normalisées) calculées par `08-video/scripts/bvh2clip.py` depuis des fichiers BVH de la CMU Graphics Lab Motion Capture Database (`http://mocap.cs.cmu.edu`), pris sur le miroir BVH public `una-dinosauria/cmu-mocap` ; les BVH ne sont pas dans le dépôt | Libre pour tout usage, commercial compris ; la citation demandée par la CMU est conservée dans les notices |

Prise CMU de chaque clip (sujet et numéro de prise, le « trial » de la base, par exemple `02_01`), citation exacte et règles de redistribution : `08-video/lib/ink-theater/THIRD_PARTY_NOTICES.md`. Qui copie le dossier dans un projet garde ce fichier et `fonts/OFL.txt` avec lui ; un clip ajouté par `bvh2clip.py` entre dans la table des notices avec sa source.

## Exemples Opus 5.5 : consultés, pas copiés

Source : [yihui-dev/awesome-opus5-5-videos](https://github.com/yihui-dev/awesome-opus5-5-videos), un catalogue de vidéos réalisées avec Claude Opus 5.5, avec leurs prompts. Le dépôt est sous licence MIT, mais il précise que chaque vidéo et chaque prompt appartient à son créateur. Commit relevé à l'écriture de l'outil : `e6c7eee870cbd6d40825d6348a0c5782b3721fe9` (2026-10-12), fichier `data/videos.json` (853 entrées à cette date).

- Rien n'est copié dans le dépôt : ni prompt, ni vidéo, ni affiche, ni extrait du catalogue.
- `08-video/scripts/inspiration.py` récupère `data/videos.json` à l'usage (branche `main`) et le garde dans `.cache/inspiration/opus-5-5-videos.json`, cache local ignoré par Git et valable 7 jours, pour le rendre interrogeable (`chercher`, `montrer`, `categories`).
- `08-video/inspiration.md` règle l'usage : extraire le mécanisme d'une référence et le transposer dans la marque, citer le créateur et le lien de sa publication dans la proposition de concept, montrer un lien et jamais une capture. Recopier un prompt dans un livrable, réutiliser les visuels ou le code d'un créateur, ou présenter une référence comme une création de l'agence est interdit.
- Le catalogue n'est pas figé : un autre commit peut ajouter, retirer ou modifier des entrées. Le registre note le commit vu à l'écriture, pas une version vendorisée.

### Rafraîchir le catalogue

Le cache se renouvelle seul : passé 7 jours, la recherche suivante relit `data/videos.json` sur la branche `main`. Pour relire tout de suite (un ajout annoncé dans le dépôt source, des résultats qui semblent datés), ajouter `--rafraichir` à n'importe quelle commande d'`inspiration.py`. Tant que le format de la source ne change pas, rien d'autre n'est à faire.

Pour remettre le registre à jour (relecture trimestrielle, ou changement constaté dans la source) :

1. Relever le commit courant de la branche `main` du dépôt source, vérifier que la licence est toujours MIT et que la mention « chaque vidéo et chaque prompt appartient à son créateur » figure toujours dans le dépôt. Si l'une ou l'autre a changé, ne plus s'en servir avant d'en avoir décidé.
2. Relire et compter : `python3 08-video/scripts/inspiration.py categories --rafraichir --format json` rend le total, les catégories et les techs.
3. Contrôler le format. Seul `slug` est obligatoire : une entrée sans slug est écartée, mais un autre champ renommé dans la source (`title`, `prompt`, `tech_tags`, `category`, `added`, `author`, `post_url`…) se vide en silence, et la recherche perd en qualité sans aucune erreur. Les signes dans la sortie de l'étape 2 : plus aucune tech, des catégories absentes, un total très inférieur au précédent. Dans ce cas, adapter `normaliser()` dans `inspiration.py` et ses tests (`scripts/tests/test_video_inspiration.py`).
4. Une catégorie nouvelle dans la source ne se filtre pas tant qu'elle manque à `CATEGORIES` dans `inspiration.py` (les choix de `--categorie`) : l'y ajouter, avec sa ligne dans la table de la section « De la catégorie à la filière » de `08-video/inspiration.md`.
5. Reporter le commit, la date et le nombre d'entrées dans le paragraphe « Source » ci-dessus (853 entrées au commit actuel) et dans la docstring d'`inspiration.py`, puis le commit dans `test_registre_complet` (`scripts/tests/test_video_module.py`), qui le vérifie. Lancer `rtk proxy python3 -m pytest scripts/tests/test_video_inspiration.py scripts/tests/test_video_module.py -q`.

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
| `skills/manimce-best-practices/examples/` (six scripts `*.py`, dont cinq cités par `SKILL.md`, et le paquet Python `attention/`) | Politique du template : aucun script externe copié. |
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
