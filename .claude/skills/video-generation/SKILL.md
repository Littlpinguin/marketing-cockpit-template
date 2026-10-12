---
name: video-generation
description: Génération de rushes vidéo IA pour {{COMPANY_NAME}}, texte vers vidéo ou image vers vidéo, via un MCP multi-modèles (Seedance, Kling, Hailuo, Veo...). Spécification d'un plan en cinq aspects (sujet, mouvement, scène, espace, caméra), prompts en anglais, notes datées par famille de modèles, arbre stock ou génération, grille de choix du fournisseur, discipline de dépense sous le contrat de coût de video-production, et contrôle de fidélité du texte sur tout rush qui fait parler quelqu'un (corrélation d'enveloppe audio). À utiliser pour un plan cinématique, un b-roll animé, une animation de produit, ou régénérer un plan d'un montage. Le montage relève de video-editing, l'orchestration de video-production (et de reel-talking-head pour un reel client).
---

# video-generation : rushes vidéo IA pour {{COMPANY_NAME}}

Vous produisez des **rushes** (jamais le livrable final) via un MCP de génération vidéo multi-modèles (type Magnific/Freepik). La composition et l'assemblage relèvent de `video-editing` ; le projet, les validations et le budget, de `video-production`.

## Avant de générer

1. **Brief et storyboard validés** (`08-video/projets/<slug>/brief.md` et `storyboard.md`, validation 3 de `video-production`) : sujet, mouvement voulu, durée, ratio, audio ou non, référence de départ. Aucun crédit dépensé avant.
2. Style-guide chargé (`01-brand/style-guide.md`) si le rush porte l'identité de la marque.
3. **Stock ou génération ?** Section « Stock ou génération » : réutiliser et chercher avant de générer.
4. **t2v ou i2v ?** Texte vers vidéo pour explorer un concept ; image vers vidéo pour le contrôle et la cohérence (générer d'abord l'image de départ avec `image-generation`, ou partir d'un visuel validé).
5. **Choisir le modèle par le besoin, pas par le prix affiché** : les modèles économiques pour itérer, les modèles les plus complets pour le rendu final validé uniquement (section « Choisir un fournisseur »). Lister le catalogue en session (`video_models_list`) : il évolue en continu, ne jamais figer une liste.

## Spécifier un plan en 5 aspects

Un modèle vidéo invente tout ce que le prompt ne dit pas. Un prompt décrit volontiers le sujet et le décor, et laisse au modèle le mouvement, l'espace et la caméra. Chaque plan se spécifie donc sur cinq aspects : sujet, mouvement, scène, espace, caméra.

- **Le sujet** : qui ou quoi, avec trois à six attributs visuels qui le distinguent (âge, tenue, matière, couleur, accessoire). Dans une série de plans, répéter ces attributs mot pour mot à chaque prompt : un pronom ou « le même personnage » ne garde pas l'identité.
- **Le mouvement** : les actions, dans l'ordre où elles arrivent, et ce qui répond à quoi (une main presse, la matière cède). Un seul geste principal par clip court.
- **La scène** : le lieu, le moment de la journée, la météo, ce qui vit autour. Le texte à l'écran, le logo et les sous-titres n'entrent pas dans le prompt : ils s'ajoutent au montage, avec la marque (un texte dessiné par le modèle n'est ni fiable ni aux couleurs de la marque).
- **L'espace** : l'échelle du plan (très gros plan, gros plan, plan moyen, plan large), la place du sujet dans le cadre, ce qui est au premier plan et à l'arrière-plan, et comment tout cela change pendant le clip.
- **La caméra** : hauteur et angle, focale et profondeur de champ, stabilité, mouvement.

Vocabulaire de caméra, avec le terme anglais à mettre dans le prompt :

- push-in (`slow push-in`), la caméra avance vers le sujet ; pull-out (`pull-out`), elle recule ;
- dolly (`dolly in`, `dolly out`), même déplacement sur rail, plus doux ;
- travelling latéral (`tracking shot`, `truck left`, `truck right`), la caméra longe le sujet ;
- orbit (`orbit around the subject`), la caméra tourne autour ;
- grue (`crane up`, `crane down`), la caméra monte ou descend en découvrant le décor ;
- caméra à l'épaule (`handheld`), légère vie dans le cadre ;
- plan fixe (`static shot`, `locked-off camera`) ;
- bascule de point (`rack focus from ... to ...`), la netteté passe d'un plan à l'autre.

Vocabulaire de lumière : heure dorée (`golden hour`), high key (`high-key lighting`, clair et peu contrasté), low key (`low-key lighting`, sombre et contrasté), contre-jour (`backlit`, `rim light`), sources dans le champ (`practical lights`, lampes visibles dans l'image).

Certains modèles prennent le mouvement de caméra en paramètre (Seedance : `cameraMotion`, avec des valeurs comme `pushIn`, `orbitLeft`, `craneUp`, `handheld`, `static`) : le paramètre se règle en plus du texte, et les deux disent la même chose.

Exemple de prompt complet (image vers vidéo, plan de 6 s) :

```text
Subject: a woman in her fifties, short grey hair, navy linen apron, silver ring on her left hand.
Motion: she presses both thumbs into a spinning lump of wet clay, the wall of the bowl rises slowly, then she lifts her hands away and the bowl keeps turning.
Scene: small pottery workshop late in the afternoon, dust floating in the air, shelves of unglazed bowls in the background. No text, no logo, no watermark.
Space: medium close-up on her hands and the wheel, wheel in the lower third of the frame, shelves soft in the background; the shot ends on a close-up of the bowl rim.
Camera: eye level, 50 mm lens, shallow depth of field, slow push-in on a dolly, steady, rack focus from her hands to the bowl rim in the last second.
Light: warm golden hour light through a side window, soft backlight on the clay dust.
```

## Écrire le prompt : le mouvement d'abord, en anglais

Les modèles vidéo sont mieux calibrés en anglais ; le français concerne le contenu à l'écran, pas le prompt technique.

- Décrire **ce qui bouge**, pas ce qui est statique : sujet, action, caméra nommée (`slow push-in`, `handheld`, `orbit`), ambiance.
- Audio natif si le modèle le prend en charge : `"dialogue"`, `SFX:`, `Ambient noise:`.
- Pour du multi-plan, structurer le prompt en sections (déroulé des plans, inventaire des effets, courbe d'énergie).
- Plans destinés à s'insérer dans un montage existant : écrire les **interdits de raccord** (décor, tenue, lumière identiques), sinon le modèle casse la continuité.

## Notes par famille de modèles

Relevé du catalogue Magnific (`video_models_list`, modèles recommandés et recherche « veo ») le 2026-10-12. Ces notes vieillissent vite : lister le catalogue en session avant tout choix, et faire rafraîchir cette section par l'agent `video-model-scout`. Les recommandations citées sont celles que l'agrégateur publie dans son catalogue, pas un test du template.

- **Seedance (ByteDance)**. La 2.5 est en tête des recommandations du catalogue : clips de 4 à 30 s jusqu'en 1080p, son natif, synchronisation labiale, références image, vidéo et audio, mouvement de caméra en paramètre. La 2.0 monte jusqu'en 4K (4 à 15 s). La 2.0 Fast sert aux brouillons (480p ou 720p).
- **Kling 2.5**. Clips muets de 5 ou 10 s, en 720p ou 1080p ; images de début et de fin fixables (en 720p, l'image de départ est exigée et l'image de fin n'est pas admise). Présenté par l'agrégateur comme le meilleur rapport qualité-prix pour un plan muet.
- **MiniMax Hailuo H3 Max et H3 Max Turbo**. Clips de 5 à 15 s en 480p ou 768p, pour explorer vite le mouvement et la mise en scène. Max accepte des références image, vidéo et audio ; Turbo, non.
- **Google Veo 3.1** (et ses versions Fast et Lite). Clips de 4, 6 ou 8 s, formats 16:9 et 9:16 seulement (pas de 1:1), jusqu'en 4K (1080p pour Lite) ; les effets sonores sont une option qui change le coût.

Tendances de ce relevé, sans promesse : le son natif et la synchronisation labiale se répandent ; un clip dépasse rarement 15 s (Seedance 2.5 va jusqu'à 30 s) ; les versions rapides servent aux brouillons, les versions complètes au définitif ; les formats proposés varient d'un modèle à l'autre, d'où le contrôle du ratio avant de choisir. Plusieurs modèles sont marqués bêta dans le catalogue : en tenir compte pour la fiabilité.

## Stock ou génération

Ordre de `video-production` : réutiliser (`01-brand/assets/`, rushes existants), puis le stock, puis générer. Pour chaque plan :

1. **Un fait réel, une preuve, un document** : stock ou archives, jamais un plan généré, qui ne prouve rien. Pour un montage d'archives : skill `video-documentary` (corpus documentaire et ses licences).
2. **Un lieu ou un geste générique** (ville, nature, atelier, mains au travail) : le stock d'abord, s'il raccorde avec les plans voisins ; la génération sinon.
3. **Un concept abstrait, une métaphore, ce qui n'existe pas** : génération.
4. **Le produit réel** : image vers vidéo depuis des visuels validés (`01-brand/assets/`, photos du produit), avec la première et la dernière image fixées pour garder l'identité du produit. Jamais un produit redessiné par le modèle.
5. **Une personne réelle** : tournage, ou génération seulement avec son consentement explicite (section « Garde-fous et divulgation »).

Le stock se cherche par l'outil `stock_search` du MCP Magnific (`content_type: video`, `video_type: footage`, orientation selon la toile), se regarde à l'image (cadrage, lumière, raccord avec les plans voisins), puis se télécharge par `stock_download`. Licence et crédit de chaque plan vérifiés dans `01-brand/droits.md` et notés dans `decisions.md` ; une licence payante passe par le contrat de coût.

## Choisir un fournisseur

Le modèle se choisit plan par plan, sur une grille qualitative, pas sur un classement :

- **Adéquation à la tâche** : durée, format, son, références d'identité ou de produit dont le plan a besoin.
- **Qualité** : jugée sur un échantillon, pas sur la réputation du modèle ni sur la recommandation du catalogue.
- **Contrôle** : images de début et de fin, références, caméra en paramètre.
- **Fiabilité** : modèle en bêta ou non, échecs déjà notés dans `decisions.md`.
- **Coût** : tarif réel de l'échantillon, solde du budget (`couts.md`) et du compte (`account_balance`).
- **Délai** : temps de génération annoncé par le catalogue, au regard de l'échéance du brief.
- **Continuité avec les plans voisins** : les rendus diffèrent d'un modèle à l'autre ; une même séquence garde un même modèle quand c'est possible.

Le choix et sa justification s'écrivent dans `decisions.md` (sujet « Modèle vidéo »), avec les options écartées. **Jamais de changement de fournisseur ou de modèle sans l'annoncer** : un modèle indisponible est un blocage à signaler, pas l'occasion d'en prendre un autre.

## Discipline de dépense : non négociable

Tout appel payant suit le **contrat de coût de `video-production`** (annonce de l'outil, du modèle, de la raison, échantillon ou série, coût estimé, solde ; `couts.md` à jour ; premier usage validé par l'humain). En plus :

- **Itérer là où c'est inclus** (application web du fournisseur si l'abonnement y donne de l'illimité en basse résolution), **produire par le MCP** une fois la direction validée. On valide la *direction* en basse résolution (cadrage, raccord, mouvement), pas le piqué.
- **Un exemplaire avant la série.** La simulation de coût peut échouer sur la génération vidéo : lancer **un** clip pour connaître le tarif réel, puis décider.
- **Générer en 720p et agrandir en local** quand la source d'origine est en basse définition : le 1080p natif n'invente que du détail, pour un multiple du prix.
- Vérifier le solde en direct (`account_balance`) avant toute série.

## Fidélité du texte : le contrôle le plus important de la chaîne

**Un modèle qui refait parler quelqu'un (synchronisation labiale, génération sur une voix) peut lui faire dire autre chose, avec une synchro labiale parfaite.** Pas un artefact visuel : des phrases entières remplacées. Invisible si l'on ne compare pas au texte d'origine, et catastrophique sur un contenu client.

**Le test, avant de poser tout rush dans un montage (local, quelques secondes, gratuit) :** corréler l'enveloppe d'énergie audio du rush avec la voix d'origine (RMS par fenêtres de 10 ms, corrélation avec recherche de décalage) :

- **au-dessus de 0,9** : fidèle, montable (valeurs observées : 0,97 à 0,99) ;
- **sous 0,5** : texte altéré, **ne pas monter** ; confirmer par transcription (valeurs observées : 0,24 à 0,25).

Les valeurs ne sont jamais ambiguës. Un rush globalement infidèle peut garder des segments fidèles : la corrélation glissante les localise. La même mesure sert à vérifier un mot que la transcription du master déforme sous un effet sonore.

**Faire ce contrôle avant le montage, jamais après** : le découvrir après coûte la reconstruction du montage entier.

## Synchronisation labiale

Sur un plan régénéré, la synchronisation native du modèle ne suffit pas : passage séparé, avec l'audio **exactement de la durée du clip** (sinon les mots sont coupés). Comparer les moteurs de synchronisation **à l'image** (bouche recadrée sur 3 instants) : le prix ne prédit pas la qualité.

## Garde-fous et divulgation

- Visage réel : uniquement avec le **consentement explicite** de la personne, obligatoire dès qu'un plan est régénéré ou synchronisé.
- Jamais de logo tiers fabriqué par IA.
- Mention « Vidéo générée par IA » en légende de la publication, jamais sur le média, selon `01-brand/divulgation-ia.md`.
- Chaque rush produit : sidecar `.json` (modèle, prompt, paramètres, `validated`, `ai_disclosure`) à côté du rush dans `08-video/projets/<slug>/rushes/`, et sa ligne de dépense dans `couts.md`.

## Ce que cette skill ne fait pas

- Monter : skill `video-editing` ; orchestrer un projet : `video-production` ; un reel client : `reel-talking-head`.
- Détourer : skill `video-matting`.
- Les visuels fixes : skill `image-generation`.
- Combler un emplacement d'un montage documentaire par un plan généré : `video-documentary` l'interdit.

---

Méthode inspirée d'OpenMontage (calesthio/OpenMontage, AGPLv3), réécrite pour le template : aucun texte ni code repris. Registre : docs/vendored-video.md.
