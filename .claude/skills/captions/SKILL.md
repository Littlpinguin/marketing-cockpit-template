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

## Ce que cette skill ne fait pas

- ❌ Le montage (→ skill `video-editing`)
- ❌ Traduire les sous-titres sans validation d'un locuteur natif
- ❌ Publier
