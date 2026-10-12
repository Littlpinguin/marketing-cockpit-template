# Specs vidéo par plateforme

Référence unique pour tout export du module vidéo. Les skills `video-editing` et `captions` lisent ce fichier avant tout rendu. Les plateformes changent leurs specs régulièrement : en cas de doute sur une limite dure (durée max, poids), vérifier la doc officielle de la plateforme avant l'export.

## Tableau de synthèse

| Plateforme | Ratio prioritaire | Résolution | Durée optimale | Durée max | Sous-titres |
|---|---|---|---|---|---|
| **Instagram Reels** | 9:16 | 1080 × 1920 | 15–30 s | 3 min | Incrustés obligatoires |
| **TikTok** | 9:16 | 1080 × 1920 | 15–34 s | 10 min | Incrustés obligatoires |
| **YouTube Shorts** | 9:16 | 1080 × 1920 | 20–40 s | 3 min | Incrustés recommandés (+ .srt) |
| **LinkedIn** | 9:16 vertical ou 1:1 / 16:9 | 1080 × 1920 / 1080 × 1080 / 1920 × 1080 | 30–90 s | 15 min | Incrustés obligatoires (lecture muette majoritaire) |

Formats d'encodage communs : **MP4 (H.264 + AAC)**, 30 fps (60 fps accepté partout), bitrate vidéo ≥ 8 Mbps en 1080p vertical.

Les valeurs que mesure la QA (formats admis, durée maximale, plancher de débit, loudness et crête) vivent dans `08-video/scripts/plateformes.toml`, que lit `08-video/scripts/qa-video.py`. Les deux fichiers se mettent à jour ensemble : un test vérifie que chaque plateforme du TOML est nommée dans ce fichier.

## Zones de sécurité (9:16)

Sur les formats verticaux, l'interface de la plateforme recouvre les bords. Aucun texte, sous-titre ou élément essentiel dans ces zones :

```
┌─────────────────────┐
│   HAUT ~ 10-12 %    │ ← barre de statut, nom du compte
│                     │
│                     │
│    ZONE UTILE       │   ← texte, sous-titres, visage, produit
│    (centre ~ 65 %)  │
│                     │
│   DROITE ~ 15 %     │ ← boutons like / commentaire / partage (TikTok, Reels)
│   BAS ~ 20-25 %     │ ← légende, description, CTA de la plateforme
└─────────────────────┘
```

Valeurs pratiques en 1080 × 1920 :

- Marge haute : **200 px**
- Marge basse : **420 px** (les sous-titres se placent juste au-dessus, centrés, ~ y = 1350–1500)
- Marge droite : **160 px** (colonne d'icônes TikTok/Reels)
- Marge gauche : **60 px**

## Détail par plateforme

### Instagram Reels

- 9:16 strict ; la couverture affichée dans la grille du profil est recadrée en 1:1 ou 4:5 → prévoir un plan de couverture lisible au centre.
- Optimum d'engagement : 15–30 s ; au-delà de 60 s, la complétion chute.
- Pas de watermark TikTok (l'algorithme le pénalise).
- Sous-titres incrustés : indispensables, l'audio est coupé par défaut dans le feed.

### TikTok

- 9:16 strict, tourné natif vertical (pas de 16:9 pillarboxé).
- Optimum : 15–34 s pour maximiser la complétion et la relecture (loop) ; les formats longs (1–3 min) fonctionnent seulement si la rétention à 3 s est déjà bonne.
- La colonne d'icônes à droite est plus envahissante que sur Reels : respecter strictement la marge de 160 px.
- Texte on-screen dès la première frame : le hook doit être lisible à l'arrêt sur image.

### YouTube Shorts

- ≤ 3 min en 9:16 pour être classé Short ; optimum 20–40 s.
- Seule plateforme où le fichier `.srt` séparé a de la valeur (indexation, traduction auto) : livrer **burn-in + .srt uploadé**.
- Le titre du Short est visible en bas : ne pas dupliquer l'info dans la zone basse de la vidéo.

### LinkedIn

- Le vertical 9:16 fonctionne désormais dans le feed, mais le 1:1 reste le plus sûr pour l'affichage desktop ; 16:9 pour les extraits de webinaire/interview posés.
- Optimum : 30–90 s ; ton plus posé que TikTok, mais les mêmes règles de rétention s'appliquent (hook 3 s, cuts serrés).
- Lecture muette quasi systématique dans le feed : sous-titres incrustés non négociables.
- Upload natif obligatoire (jamais un lien YouTube : portée divisée).

## Sous-titres — règles transverses

Détail du workflow dans la skill `captions`. L'essentiel :

- **Segments courts** : 1–2 lignes, ≤ 42 caractères par ligne, 1–3 s d'affichage par segment.
- **Position** : centrés, au-dessus de la zone basse de sécurité (jamais dans les 420 px du bas en 9:16).
- **Style** : police `{{BRAND_FONT_PRIMARY}}`, couleurs de la marque (`{{BRAND_COLOR_LIGHT}}` sur fond/liseré `{{BRAND_COLOR_DARK}}`), contraste suffisant sur tout arrière-plan.
- **Livraison** : burned-in pour toutes les plateformes ; `.srt` en plus pour YouTube.

## Déclinaison multi-plateformes d'une même vidéo

Ordre de production recommandé : **monter en 9:16** (le plus contraint), puis décliner :

1. 9:16 master → Reels, TikTok, Shorts (mêmes fichiers, hooks/CTA éventuellement adaptés au ton de la plateforme).
2. 9:16 → 1:1 LinkedIn : recadrer ou poser le 9:16 sur fond de marque (`{{BRAND_COLOR_DARK}}`) avec le logo.
3. Ne jamais étirer ; toujours recadrer ou letterboxer aux couleurs de la marque.

## Format court : repères de production

Ces repères valent pour Reels, TikTok, Shorts et la vidéo LinkedIn. Les chiffres sourcés de rétention, de durée et de lecture sans le son sont dans `docs/etat-de-lart/video-courte.md` ; ce qui suit est la méthode de production qui en découle.

### Accroche

- La première seconde se lit à l'arrêt sur image : une phrase, un objet ou une tension, visibles dès la première image. Ni logo, ni jingle, ni plan d'installation.
- Test : mettre le rendu en pause sur sa première image. Si l'on ne comprend pas de quoi parle la vidéo, l'accroche n'existe pas encore.
- Le texte à l'écran reformule l'accroche dite, pour ceux qui regardent sans le son.
- Trois variantes d'accroche par vidéo, écrites avant le reste du script et validées par un humain (validation du script dans la skill `video-production`).
- Décrochage dans les premières secondes et structure accroche, valeur, révélation, appel : `docs/etat-de-lart/video-courte.md` (règles R1 et R2).

### Longueur de la narration

Aucun nombre de mots par durée n'est fixé ici : le débit dépend de la voix, de la langue et du ton. Il se mesure.

1. Produire l'échantillon de la voix retenue sur un passage représentatif du script (`narration.md` § « Direction de voix »).
2. Mesurer son débit : mots de l'échantillon divisés par sa durée en secondes, pauses comprises.
3. Budget de mots : débit multiplié par la durée visée, moins une marge pour les respirations, le silence du temps fort et la tenue de l'appel à l'action final.
4. Couper le texte pour tenir ce budget avant toute génération complète. Jamais accélérer la voix pour faire entrer un texte trop long.

Détail et exemple de calcul : `narration.md` § « Calibrer la longueur ».

### Texte à l'écran

- Une idée par carton. Deux niveaux de texte simultanés au plus (un titre et une ligne d'appui, ou un carton et les sous-titres).
- Durée d'affichage : au moins le temps de lire le carton deux fois à voix basse. Vérification : lecture chronométrée sur le rendu, par quelqu'un qui découvre le texte.
- Tailles de départ des rôles typographiques : celles du `frame.md` que `08-video/scripts/brand-frame.py` écrit pour chaque projet (doctrine : `motion.md` § « Repères typographiques »). Les vérifier sur un téléphone réel, tenu à bout de bras, avant de valider le storyboard.
- Vitesse de lecture des sous-titres : elle se compte en caractères par seconde, espaces et ponctuation compris. Repère publié en français : entre 12 et 15 caractères par seconde, deux lignes au plus ([charte du CSA de la Fédération Wallonie-Bruxelles relative à la qualité des mesures d'accessibilité, 2019, article 6](https://www.csa.be/wp-content/uploads/documents-csa/20191015-Charte-accessibilité.pdf)). Contrôle : diviser le nombre de caractères de chaque segment du `.srt` par sa durée. Un segment de 30 caractères demande donc au moins 2 secondes.

### Zones de sécurité selon la toile

- **9:16 (1080 × 1920)** : marges de la section « Zones de sécurité (9:16) » ci-dessus, soit 200 px en haut, 420 px en bas, 60 px à gauche et 160 px à droite.
- **1:1 (1080 × 1080) et 16:9 (1920 × 1080)** : marge de titre de 5 % de chaque dimension, soit 54 px sur un côté de 1080 px et 96 px sur un côté de 1920 px. En 1:1, 54 px partout ; en 16:9, 54 px en haut et en bas, 96 px à gauche et à droite.
- `brand-frame.py` reprend ces valeurs dans le `frame.md` de chaque projet (clés `safe-top`, `safe-bottom`, `safe-left`, `safe-right`) : les compositions les lisent là, sans les recopier.
- `qa-video.py` ne mesure pas les zones de sécurité. L'agent `video-reviewer` les vérifie à l'œil sur les images de plans (`plan-NN.jpg`) et la planche contact que produit la QA.
