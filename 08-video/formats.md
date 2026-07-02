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
