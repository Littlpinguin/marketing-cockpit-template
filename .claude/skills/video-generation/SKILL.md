---
name: video-generation
description: Génération de rushes vidéo IA pour {{COMPANY_NAME}} — texte→vidéo ou image→vidéo via un MCP multi-modèles (Kling, Veo, Seedance, Hailuo, Wan…), prompts motion-first en anglais, discipline de dépense stricte, et contrôle de fidélité du texte sur tout rush qui fait parler quelqu'un (corrélation d'enveloppe audio). À utiliser pour produire un plan cinématique, un b-roll animé, une animation de produit, ou régénérer un plan d'un montage. Le montage relève de `video-editing` ; l'orchestration complète d'un reel client de `reel-talking-head`.
---

# video-generation — rushes vidéo IA pour {{COMPANY_NAME}}

Vous produisez des **rushes** (jamais le livrable final) via un MCP de génération vidéo multi-modèles (type Magnific/Freepik). La composition et l'assemblage relèvent de `video-editing`.

## Avant de générer

1. Brief validé (`08-video/briefs/<slug>.md`) : sujet, mouvement voulu, durée, ratio, audio ou non, référence de départ.
2. Style-guide chargé (`01-brand/style-guide.md`) si le rush porte l'identité de la marque.
3. **t2v ou i2v ?** Texte→vidéo pour explorer un concept ; image→vidéo pour le contrôle et la cohérence (générer d'abord l'image de départ avec `image-generation`).
4. **Choisir le modèle par le besoin, pas par le prix affiché** : les modèles économiques pour itérer, les modèles « hero » (Veo, Kling dernière version, Seedance Pro) pour le rendu final validé uniquement. Lister le catalogue en session (`video_models_list`) — il évolue en continu, ne jamais figer une liste.

## Écrire le prompt — motion-first, en anglais

Les modèles vidéo sont mieux calibrés en anglais ; le français concerne le contenu à l'écran, pas le prompt technique.

- Décrire **ce qui bouge**, pas ce qui est statique : sujet + action + caméra nommée (`slow push-in`, `handheld`, `orbit`) + ambiance.
- Audio natif si le modèle le supporte : `"dialogue"`, `SFX:`, `Ambient noise:`.
- Pour du multi-plan, structurer le prompt en sections (timeline des plans, inventaire d'effets, arc d'énergie).
- Plans destinés à s'insérer dans un montage existant : écrire les **interdits de raccord** (décor, tenue, lumière identiques) — sinon le modèle casse la continuité.

## Discipline de dépense — non négociable

- **Itérer là où c'est inclus** (application web du fournisseur si l'abonnement y donne de l'illimité basse résolution), **produire par le MCP** une fois la direction validée. On valide la *direction* en basse résolution (cadrage, raccord, mouvement), pas le piqué.
- **Un exemplaire avant la série.** La simulation de coût peut échouer sur la génération vidéo : lancer **un** clip pour connaître le tarif réel, puis décider.
- **Générer en 720p et upscaler localement** quand la source d'origine est en basse définition : le 1080p natif n'invente que du détail, pour un multiple du prix.
- Vérifier le solde en direct (`account_balance`) avant toute série.

## 🔴 Fidélité du texte — le contrôle le plus important de la chaîne

**Un modèle qui refait parler quelqu'un (lipsync, génération sur une voix) peut lui faire dire autre chose, avec une synchro labiale parfaite.** Pas un artefact visuel : des phrases entières remplacées. Invisible si l'on ne compare pas au texte d'origine, et catastrophique sur un contenu client.

**Le test, avant de poser tout rush dans une timeline — local, quelques secondes, gratuit :** corréler l'enveloppe d'énergie audio du rush avec la voix d'origine (RMS par fenêtres de 10 ms, corrélation avec recherche de décalage) :

- **> 0,9** → fidèle, montable (valeurs observées : 0,97-0,99)
- **< 0,5** → texte altéré, **ne pas monter** ; confirmer par transcription (valeurs observées : 0,24-0,25)

Les valeurs ne sont jamais ambiguës. Un rush globalement infidèle peut garder des segments fidèles : la corrélation glissante les localise. La même mesure sert à vérifier un mot que la transcription du master déforme sous un effet sonore.

**Faire ce contrôle avant le montage, jamais après** : le découvrir après coûte la reconstruction du montage entier.

## Synchronisation labiale

Sur un plan régénéré, le lipsync natif du modèle ne suffit pas : passage séparé, avec l'audio **exactement de la durée du clip** (sinon les mots sont coupés). Comparer les moteurs de lipsync **à l'image** (crop bouche sur 3 instants) : le prix ne prédit pas la qualité.

## Garde-fous et disclosure

- Visage réel = uniquement avec le **consentement explicite** de la personne — obligatoire dès qu'un plan est régénéré ou synchronisé.
- Jamais de logo tiers fabriqué par IA.
- Mention « Vidéo générée par IA » en légende de la publication, jamais sur le média.
- Chaque rush produit : sidecar `.json` (modèle, prompt, params, `validated`, `ai_disclosure`) + ligne de registre dans `08-video/rushes/<slug>/`.

## Ce que cette skill ne fait pas

- ❌ Monter (→ `video-editing`) ni orchestrer un reel complet (→ `reel-talking-head`)
- ❌ Détourer (→ `video-matting`)
- ❌ Les visuels fixes (→ `image-generation`)
