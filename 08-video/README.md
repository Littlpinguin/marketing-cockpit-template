# 08-video : outillage du studio vidéo

Ce module produit les vidéos de {{COMPANY_NAME}} : vidéos courtes (Reels, TikTok, Shorts, LinkedIn), explainers, vidéos produit, motion design de marque, montage de rushes, clips tirés de vidéos longues, montages documentaires, animation à l'encre, 3D, Manim. Toute demande entre par la skill `video-production` ; le rôle, les filières et les validations sont décrits dans `CLAUDE.md`. Ce fichier décrit les outils.

## Trois couches

1. **Le moteur, externe, installé à l'activation du module** (`/modules`) : le plugin HyperFrames, ffmpeg et ffprobe ; en option, whisper, Manim Community, et torch avec open_clip pour la recherche dans le corpus documentaire. Rien de tout cela n'est copié dans le dépôt.
2. **La marque et la méthode, dans le template** (licence MIT) : les skills de `.claude/skills/`, la doctrine de `08-video/*.md`, les scripts de `08-video/scripts/`, le moteur `08-video/lib/ink-theater/` et l'agent `video-reviewer`.
3. **La matière** : `01-brand/assets/` d'abord ; puis le MCP Magnific s'il est connecté (stock vidéo, clips générés, voix, musique, 3D) ; les médias d'HyperFrames (voix locale Kokoro, transcription, détourage) ; le corpus documentaire maison.

## HyperFrames

HyperFrames rend une vidéo à partir d'une composition HTML : le DOM déclare le minutage par des attributs `data-*`, l'animation se positionne à n'importe quel instant, et le rendu se fait image par image. C'est le moteur par défaut du module (`motion.md` § « Choisir le moteur »).

- **Installation** : plugin Claude Code officiel `hyperframes@hyperframes` (marketplace `heygen-com/hyperframes`, licence Apache-2.0), installé par `/modules` en portée `local` (seul `.claude/settings.local.json`, non versionné, est modifié). La version installée est notée dans `.setup-completed` (`modules.video.hyperframes`) et contrôlée par `/health-check`. Après l'installation, redémarrer la session pour charger les skills.
- **Skills `hyperframes:*`** : le routeur `hyperframes:hyperframes`, les domaines (`hyperframes:hyperframes-core`, `hyperframes:hyperframes-cli`, `hyperframes:hyperframes-animation`, `hyperframes:hyperframes-keyframes`, `hyperframes:hyperframes-audio`, `hyperframes:hyperframes-registry`, `hyperframes:media-use`) et les workflows que `video-production` choisit : `motion-graphics`, `faceless-explainer`, `product-launch-video`, `pr-to-video`, `music-to-video`, `general-video`, `talking-head-recut`, `embedded-captions`.
- **CLI** : `npx hyperframes init`, `lint`, `check`, `preview`, `render`, `timeline`, `transcribe`, `tts`. Dans une installation en plugin, chaque commande passe par le lanceur du plugin, qui fixe la version du CLI (règle de la skill `hyperframes:hyperframes`).
- **La marque par construction** : `scripts/brand-frame.py` écrit dans chaque projet `frame.md` (le fichier de design qu'HyperFrames lit en premier) et `brand.css` (les mêmes valeurs en variables CSS), depuis `01-brand/tokens.json`. On ne les édite jamais à la main ; aucun preset visuel d'HyperFrames dans un projet client (seule exception : la peau de sous-titres, `video-production`).
- **Médias** : la voix locale et gratuite de Kokoro (`npx hyperframes tts`, voix française `ff_siwis`, `narration.md`) ; la connexion à HeyGen (voix, musique) est un fournisseur externe, annoncé sous le contrat de coût. Licence de la musique générée : `video-production` § « Contrat de coût ».

## ffmpeg et ffprobe

Découpe, concaténation, recadrage, réencodage, normalisation du son, incrustation de sous-titres, extraction d'images ; ffprobe pour les mesures. Utilisés par `video-editing` (voie B), `captions`, `video-repurpose`, `qa-video.py` et `corpus.py`.

```bash
brew install ffmpeg   # macOS ; sous Linux : apt install ffmpeg
```

L'incrustation de sous-titres par ffmpeg demande une build avec libass : `ffmpeg -filters | grep subtitles` doit répondre (skill `captions`).

## whisper (facultatif)

Transcription locale et privée par `whisper-cli` (`brew install whisper-cpp`), avec un modèle ggml dont le chemin se déclare dans `.env` (`WHISPER_MODEL`, voir `.env.example`). Elle sert à `qa-video.py --script` (le rendu dit-il le script ?), à `captions` et à `video-repurpose`. Sans whisper, `qa-video.py` le signale (constat `transcription-indisponible`) sans échouer ; la transcription au mot d'HyperFrames reste une autre voie, toujours avec un modèle multilingue et la langue (`npx hyperframes transcribe <vidéo> --model small --language fr`) : son modèle par défaut, `small.en`, traduit l'audio français en anglais.

## Manim (facultatif)

Manim Community, pour une démonstration conceptuelle ou mathématique : `manim-composer` planifie, `manim-ce` écrit le code, le rendu MP4 entre comme plan vidéo dans une composition HyperFrames. Installation : `pip install manim`, puis `manim checkhealth` ; `/modules` le détecte par `manim --version`.

## Corpus documentaire (facultatif pour la recherche)

`scripts/corpus.py` constitue un corpus d'archives libres par thème (Internet Archive, Wikimedia Commons, NASA, et Pexels ou Pixabay avec une clé gratuite dans `.env`), filtre les licences, télécharge, puis indexe et cherche par description (CLIP). La constitution du corpus et les crédits n'ont besoin que de la bibliothèque standard et de ffmpeg ; l'index et la recherche demandent `pip install -r 08-video/requirements-corpus.txt`. Les thèmes vivent dans `corpus/themes/` (versionné, exemple : `exemple-savoir-faire.toml`), les clips dans `corpus/<thème>/` (non versionné). Doctrine : `documentaire.md` ; skill : `video-documentary`.

## Ink-theater

`lib/ink-theater/` est un moteur d'animation « dessinée à l'encre » écrit pour le template : traits qui se tracent, tremblé, écriture manuscrite, fond papier, silhouette animée par des clips de capture de mouvement. Il est déterministe, condition du rendu image par image d'HyperFrames. Les clips sont produits par `scripts/bvh2clip.py` depuis la base de capture de mouvement de CMU ; la police Patrick Hand est sous licence OFL. Mode d'emploi : `lib/ink-theater/README.md` et la référence `encre.md` de la skill `motion-design`.

## Bibliothèque d'inspiration

`scripts/inspiration.py` interroge une bibliothèque de vidéos de référence réalisées avec Claude Opus 5.5 (dépôt `yihui-dev/awesome-opus5-5-videos`), téléchargée au moment de l'usage et gardée 7 jours dans `.cache/inspiration/` ; rien n'en est copié dans le dépôt. Elle nourrit les concepts et le storyboard : on en extrait un mécanisme, jamais un look, et les références retenues se consignent dans `projets/<slug>/references.md`. Méthode : `inspiration.md`.

## Matière : réutiliser avant de générer

1. **Les assets de la marque** : `../01-brand/assets/` et les visuels déjà produits dans `../06-graphic-design/outputs/`.
2. **Le stock** : le MCP Magnific (`stock_search`, `stock_download`), le corpus documentaire. Licences et crédits vérifiés dans `01-brand/droits.md`.
3. **La génération** : clips (`video-generation`), images (`image-generation`), voix et musique, sous le contrat de coût de `video-production` et jamais avant la validation du storyboard.

Tout plan généré respecte `../01-brand/style-guide.md` (palette, style d'illustration `{{BRAND_ILLUSTRATION_STYLE}}`, tropes bannis `{{BRAND_BANNED_VISUALS}}`) et se déclare selon `../01-brand/divulgation-ia.md`.

## Les skills du module

| Skill | Ce qu'elle fait |
|---|---|
| `video-production` | Point d'entrée de toute demande vidéo : objectif, filière, dossier de projet, trois validations, contrat de coût, passation à HyperFrames, QA, livraison |
| `motion-design` | La marque dans tout ce qui bouge : `frame.md` et `brand.css`, profil de goût, revue de singularité, workflow HyperFrames ; références 3D, personnages, encre |
| `video-editing` | Montage de rushes : voie HyperFrames (`talking-head-recut`, `general-video`) ou plan ffmpeg ; coupe des silences, recadrage suivi, export normalisé |
| `captions` | Transcription, `.srt`, sous-titres incrustés aux couleurs de la marque, karaoké, sous-titres designés HyperFrames |
| `reel-talking-head` | D'une vidéo brute face caméra à un reel monté, avec deux arrêts avant toute dépense |
| `video-generation` | Rushes IA : plan en cinq aspects, notes par famille de modèles, stock ou génération, choix du fournisseur, fidélité du texte |
| `video-matting` | Détourage local d'un sujet filmé (calque alpha) |
| `video-repurpose` | D'une vidéo longue (webinar, interview, podcast) à des clips sociaux notés et validés |
| `video-documentary` | Essai filmé sur archives libres : emplacements, corpus, recherche CLIP, crédits |
| `manim-composer` | Planifier une animation Manim scène par scène (vendorisée, MIT) |
| `manim-ce` | Écrire le code Manim Community (vendorisée, MIT) |

Agent du module : `video-reviewer`, revue d'un rendu en lecture seule avant livraison.

## Les scripts

| Script | Ce qu'il fait | Exemple |
|---|---|---|
| `qa-video.py` | QA mesurable d'un rendu : durée, format, codec, débit, loudness, noirs, images figées, silences, rythme, fidélité de la narration ; images de plans, planche contact, rapport | `python3 08-video/scripts/qa-video.py <rendu.mp4> --plateforme reels --duree 45 --script <script.md>` |
| `controle-sous-titres.py` | Forme des sous-titres d'un projet selon `sous-titres.toml` (lignes, caractères, durée, vitesse, chevauchements, coupes, fidélité au script, taille dans la composition) ; sort 1 sur erreur, et le hook du module le lance à chaque écriture | `python3 08-video/scripts/controle-sous-titres.py 08-video/projets/<slug>` |
| `brand-frame.py` | Écrit `frame.md` et `brand.css` d'un projet HyperFrames depuis `01-brand/tokens.json` ; `--check` sort 1 sur une dérive | `python3 08-video/scripts/brand-frame.py 08-video/projets/<slug>/hyperframes --aspect 1080x1920` |
| `bvh2clip.py` | Convertit un fichier de capture de mouvement BVH en clip 2D pour ink-theater | `python3 08-video/scripts/bvh2clip.py <fichier.bvh> --nom marche --source "CMU 02_01"` |
| `corpus.py` | Corpus documentaire : `build`, `list`, `index`, `search`, `credits` | `python3 08-video/scripts/corpus.py build 08-video/corpus/themes/<thème>.toml` |
| `inspiration.py` | Bibliothèque d'inspiration : `chercher`, `montrer`, `categories` | `python3 08-video/scripts/inspiration.py chercher "time saved counter" --top 8` |

`plateformes.toml` porte les valeurs mesurées par `qa-video.py` (formats, durée maximale, débit, loudness) ; il se met à jour avec `formats.md`. Chaque script a son `--help`.

## Arborescence

```
08-video/
├── CLAUDE.md                rôle, filières, validations
├── README.md                ce fichier
├── formats.md               specs par plateforme, format court
├── montage.md               coupe, rythme, son, démo produit
├── narration.md             écrire pour l'oreille, voix, mix
├── motion.md                motion de marque, moteur, 3D, personnages, encre, Manim
├── documentaire.md          montage sur archives
├── inspiration.md           vidéos de référence : chercher, extraire, transposer
├── requirements-corpus.txt  dépendances facultatives du corpus
├── lib/
│   ├── brand.css            charte générée par scripts/build-tokens.py
│   └── ink-theater/         moteur d'encre, clips, police, notices
├── scripts/                 qa-video.py, plateformes.toml, brand-frame.py, bvh2clip.py,
│                            corpus.py, corpus_documentaire/, inspiration.py,
│                            controle-sous-titres.py, sous-titres.toml
├── corpus/
│   ├── themes/              fichiers de thème (versionnés)
│   └── <thème>/             clips, fiches, images clés, index (non versionnés)
└── projets/<slug>/          un dossier par vidéo (structure dans CLAUDE.md)
```

## Ce qui n'est pas versionné

Les médias lourds s'archivent sur le stockage du client, pas dans Git (`.gitignore`, bloc `08-video`) : `projets/*/rushes/` et `projets/*/exports/`, tout fichier audio ou vidéo sous `projets/`, les sorties et caches d'HyperFrames (`renders/`, `snapshots/`, `node_modules/`, `.media/`, et les images de détourage `frames_fg/` et `frames_bg/` d'un projet de sous-titres designés), les images et `rapport.json` de `qa/` (seul `rapport.md` se versionne), les corpus documentaires hors `corpus/themes/`, et les anciens dossiers `08-video/rushes/` et `08-video/exports/`. Restent versionnables dans un fork : `brief.md`, `script.md`, `storyboard.md`, `references.md`, `decisions.md`, `sous-titres/`, les compositions HyperFrames, et les images et polices de leur dossier `assets/`.
