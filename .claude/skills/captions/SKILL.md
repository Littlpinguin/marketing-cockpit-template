---
name: captions
description: Sous-titrage vidéo pour {{COMPANY_NAME}} — transcription (whisper local ou API), découpage en segments courts lisibles, fichier .srt propre et sous-titres incrustés (burned-in) stylés aux couleurs de la marque via ffmpeg. À utiliser dès qu'une vidéo doit être sous-titrée : Reels, TikTok, Shorts, LinkedIn, webinaire, interview. Pour le montage complet → skill `video-editing`.
---

# captions — sous-titrage stylé marque

Vous produisez, pour chaque vidéo, deux livrables : un **`.srt`** propre dans `08-video/subtitles/`, et une version **burned-in** (sous-titres incrustés) conforme aux specs de `08-video/formats.md` et aux tokens de `01-brand/style-guide.md`.

## Étape 1 — Transcription

### Option A — whisper local (gratuit, privé, recommandé)

```bash
# Installation une fois : pip install -U openai-whisper  (ou faster-whisper, plus rapide)
# Le modèle "medium" est un bon équilibre précision/vitesse pour le français.
whisper 08-video/exports/<slug>.mp4 --model medium --language fr \
  --output_format srt --output_dir 08-video/subtitles/
```

### Option B — API de transcription

Si pas de GPU/temps local : une API de speech-to-text (par ex. l'API OpenAI Whisper, `model=whisper-1`, sortie `srt`). Clé dans `.env`, jamais en dur. Attention : la vidéo part alors chez un tiers — vérifier que le contenu n'est pas confidentiel avant l'envoi.

### Relecture obligatoire

La transcription brute contient toujours des erreurs : noms propres, marque ({{COMPANY_NAME}}), vocabulaire métier, chiffres. Relire intégralement et corriger avant tout burn-in — un chiffre faux incrusté est une faute publique. Vérifier aussi le vocabulaire banni de `01-brand/voice.md` si le script est retouché.

## Étape 2 — Découpage en segments lisibles

Whisper produit des segments trop longs pour du vertical. Redécouper le `.srt` :

- **≤ 42 caractères par ligne, 2 lignes max** — en 9:16, viser plutôt **≤ 25 caractères, 1 ligne** (gros et centré).
- **1 à 3 s par segment**, synchronisé sur le rythme de parole ; jamais un segment à cheval sur un cut.
- Couper aux frontières naturelles (groupes de sens), pas au milieu d'un groupe nominal.
- Ponctuation minimale : pas de point final sur chaque segment ; garder `?` et `!` qui portent le ton.
- Mots-clés en MAJUSCULES avec parcimonie (1 par segment max) pour l'emphase.

```srt
1
00:00:00,000 --> 00:00:01,800
Vous perdez 3 heures par semaine

2
00:00:01,800 --> 00:00:03,200
sur VOS reportings ?
```

## Étape 3 — Livrable 1 : le `.srt`

- Nommage : `08-video/subtitles/<slug>.srt` (même slug que la vidéo).
- Encodage UTF-8, timecodes `HH:MM:SS,mmm`, numérotation continue.
- Usage : upload YouTube (indexation + traduction auto), archivage, ré-édition.

## Étape 4 — Livrable 2 : burn-in stylé marque via ffmpeg

Les sous-titres incrustés reprennent les tokens de `01-brand/style-guide.md`. Deux méthodes :

### Méthode simple — filtre `subtitles` avec style forcé

```bash
# Police et couleurs de marque. Les couleurs ASS sont en &HAABBGGRR& (BGR inversé !) :
# convertir {{BRAND_COLOR_LIGHT}} et {{BRAND_COLOR_DARK}} avant de remplir PrimaryColour/OutlineColour.
# MarginV=110 ≈ sous-titres au-dessus de la zone basse de sécurité en 1080×1920 (cf. formats.md).
ffmpeg -i 08-video/exports/<slug>-tiktok.mp4 \
  -vf "subtitles=08-video/subtitles/<slug>.srt:force_style='FontName={{BRAND_FONT_PRIMARY}},FontSize=15,Bold=1,PrimaryColour=&H00FFFFFF&,OutlineColour=&H00000000&,BorderStyle=1,Outline=2,Shadow=0,Alignment=2,MarginV=110'" \
  -c:v libx264 -preset slow -crf 18 -c:a copy \
  08-video/exports/<slug>-tiktok-sub.mp4
```

Prérequis : la police `{{BRAND_FONT_PRIMARY}}` installée sur la machine (sinon fallback silencieux — vérifier visuellement). `FontSize` s'exprime relativement à la résolution de la piste ASS : contrôler le rendu sur une frame avant l'export complet :

```bash
# Contrôle visuel rapide : extraire une frame sous-titrée à t=2 s
ffmpeg -i 08-video/exports/<slug>-tiktok-sub.mp4 -ss 2 -frames:v 1 tmp/controle.png
```

### Méthode fine — fichier `.ass` (styles par segment, karaoké, positions)

Pour un style au segment près (mot surligné, changement de couleur, position variable), convertir en `.ass` et éditer le bloc `[V4+ Styles]` :

```bash
ffmpeg -i 08-video/subtitles/<slug>.srt 08-video/subtitles/<slug>.ass
# éditer les styles, puis :
ffmpeg -i <video>.mp4 -vf "ass=08-video/subtitles/<slug>.ass" -c:a copy <video>-sub.mp4
```

C'est la voie pour reproduire les styles « mot à mot » type TikTok — à réserver aux vidéos à fort enjeu, le coût d'édition est réel.

⚠️ **Vérifier que le ffmpeg de la machine embarque libass avant de promettre un burn-in** (`ffmpeg -filters | grep subtitles`) : certaines builds n'ont ni `subtitles` ni `drawtext`. Dans ce cas, l'incrustation passe par l'éditeur vidéo (méthode ci-dessous).

### Méthode karaoké dans l'éditeur (Palmier Pro) — le vrai « mot actif »

Pour un karaoké type Reels (groupe de 3-5 mots visible, mot actif coloré), la voie robuste est de poser les sous-titres **comme clips texte dans l'éditeur**, pas en burn-in ffmpeg :

1. **Transcrire avec les timings par token** : `whisper-cli -ml 1` (timings au mot — indispensable ; la transcription automatique intégrée aux éditeurs découpe en groupes de 1-2 mots aux timings approximatifs : ne pas l'utiliser quand on maîtrise le SRT).
2. **Regrouper en chunks de 3-5 mots**, coupés aux frontières de sens, sans segment à cheval sur un cut.
3. **Poser chaque chunk comme un clip texte** avec l'animation de surbrillance de l'éditeur (preset type `highlightBlock`/`highlightPop` + couleur du mot actif `{{BRAND_COLOR_ACCENT}}`), fond `{{BRAND_COLOR_DARK}}` semi-opaque, centré à ~65 % de la hauteur.
4. **Relire les homophones** : la transcription écrit ce qu'elle entend (« qu'il dit » pour « qui le dit ») — corriger dans le texte affiché, l'audio, lui, est juste.
5. Si le montage insère un cold open, **décaler la grille** d'autant et reconstituer les sous-titres du cold open à la main.

Le rendu est vectoriel (pas de perte au réencodage), éditable au mot près, et survit aux changements de montage — trois avantages décisifs sur le burn-in.

## Règles de placement (rappel de `08-video/formats.md`)

- 9:16 (1080×1920) : centrés, au-dessus de la marge basse de 420 px (≈ `MarginV` 100–130), jamais dans la colonne d'icônes à droite.
- 1:1 et 16:9 (LinkedIn) : centrés bas, marge ≥ 8 % de la hauteur.
- Contraste : liseré (`Outline`) ou bandeau `{{BRAND_COLOR_DARK}}` systématique — le fond vidéo change, le sous-titre doit rester lisible sur chaque plan.

## Checklist avant livraison

- [ ] Transcription relue à 100 % (noms, chiffres, vocabulaire de marque)
- [ ] Segments : 1 ligne ≤ 25 car. en 9:16 (max 2 × 42), 1–3 s, pas de segment à cheval sur un cut
- [ ] `.srt` livré dans `08-video/subtitles/<slug>.srt` (UTF-8)
- [ ] Burn-in : police `{{BRAND_FONT_PRIMARY}}`, couleurs de la marque, hors zones de sécurité
- [ ] Contrôle visuel sur au moins 3 frames (début, milieu, fin)
- [ ] Pour YouTube : burn-in **et** `.srt` fournis

## Règles état de l'art (2026)

Voir `docs/etat-de-lart/video-courte.md` pour le détail sourcé :

1. **Sous-titres incrustés sur 100 % des vidéos livrées** : ~85 % des vidéos social sont regardées sans le son (jusqu'à 92 % sur mobile), et les sous-titres augmentent jusqu'à +80 % la probabilité de finir la vidéo.
2. **Test de validation avant livraison : la vidéo se comprend-elle entièrement en muet ?** Aucune information clé portée uniquement par la bande-son ; texte d'écran pour les infos essentielles.
3. **Placement : gros, centrés, dans la zone sûre** (éviter le tiers bas recouvert par l'UI des plateformes), 1-2 lignes max, mots-clés mis en évidence.

## Ce que cette skill ne fait pas

- ❌ Le montage (→ skill `video-editing`)
- ❌ Traduire les sous-titres sans validation d'un locuteur natif
- ❌ Publier
