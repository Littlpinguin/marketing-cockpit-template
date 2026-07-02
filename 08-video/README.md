# 08-video — montage vidéo assisté par IA

Ce module produit les vidéos courtes de {{COMPANY_NAME}} (Reels, TikTok, Shorts, LinkedIn) avec un pipeline assisté par IA : **Palmier Pro** pour le montage piloté par Claude, **ffmpeg** en fallback pour les opérations simples, et des modèles génératifs pour créer des clips quand il n'y a pas de rushes.

## L'outil principal : Palmier Pro

[Palmier Pro](https://github.com/palmier-io/palmier-pro) est un éditeur vidéo macOS **open source (GPLv3)** qui expose un **serveur MCP** : Claude Code peut piloter la timeline — importer des rushes, poser des cuts, ajouter des transitions, du texte, exporter — pendant que vous gardez la main dans l'interface pour les ajustements fins.

**Prérequis :**

- macOS sur **Apple Silicon** (M1 ou plus récent)
- Palmier Pro installé (voir le repo GitHub pour la dernière release)
- Serveur MCP de Palmier Pro déclaré dans `.mcp.json` du repo (suivre la doc d'installation du projet — vérifier la commande exacte dans leur README, elle peut évoluer)
- **Fonctions génératives sur abonnement** : la génération de clips par les modèles intégrés (Seedance, Kling) nécessite un abonnement Palmier Pro. Le montage classique (cuts, transitions, texte, export) est gratuit et open source.

**Répartition des rôles :**

| Tâche | Qui |
|---|---|
| Structure du montage, cuts, ordre des plans, textes | Claude via MCP Palmier Pro |
| Étalonnage fin, choix esthétiques litigieux | Humain dans l'UI Palmier Pro |
| Validation du hook et du rendu final | Humain, toujours |

## Le fallback : ffmpeg

Quand Palmier Pro n'est pas disponible (pas de Mac, machine CI, opération triviale), **ffmpeg** couvre les opérations simples : découpe, concaténation, ré-encodage, changement de ratio, incrustation de sous-titres, extraction audio.

```bash
brew install ffmpeg   # macOS — sur Linux : apt install ffmpeg
```

La skill `video-editing` produit dans ce cas un **plan de montage ffmpeg** : une suite de commandes commentées, exécutées après votre validation. Les commandes types (recadrage 9:16, concat, burn-in) sont dans les skills `video-editing` et `captions`.

## Générer des clips quand il n'y a pas de rushes

Trois options, par ordre de préférence :

1. **Modèles intégrés Palmier Pro** (Seedance, Kling) — génération directement dans la timeline, sur abonnement. Le plus fluide pour des plans d'illustration courts.
2. **Magnific MCP** — si le serveur MCP Magnific est configuré dans le repo, génération/upscale de clips et d'images hors Palmier Pro, puis import comme rushes.
3. **Banque d'assets de la marque** — toujours vérifier `../01-brand/assets/` et `../06-graphic-design/outputs/` avant de générer : réutiliser > générer.

Tout clip généré respecte les contraintes de `../01-brand/style-guide.md` (palette, style d'illustration `{{BRAND_ILLUSTRATION_STYLE}}`, tropes bannis `{{BRAND_BANNED_VISUALS}}`) et la **politique de disclosure IA** de la marque.

## Les skills du module

| Skill | Ce qu'elle fait |
|---|---|
| `video-editing` (`.claude/skills/video-editing/`) | Workflow complet : brief → structure (hook 3 s, rythme, format cible) → montage MCP Palmier Pro ou plan ffmpeg → habillage aux tokens de marque → export par plateforme |
| `captions` (`.claude/skills/captions/`) | Transcription (whisper local ou API), segments courts lisibles, `.srt` + sous-titres incrustés stylés marque via ffmpeg |

## Specs par plateforme

Durées, ratios, zones de sécurité et règles de sous-titres par plateforme (LinkedIn, Instagram Reels, TikTok, YouTube Shorts) : voir **`formats.md`**. C'est la référence unique — les skills la lisent avant tout export.

## Arborescence de travail

```
08-video/
├── CLAUDE.md          ← rôle, workflow, gates
├── README.md          ← ce fichier
├── formats.md         ← specs par plateforme
├── briefs/            ← un brief par vidéo
├── scripts/           ← scripts validés (hook / corps / CTA)
├── rushes/            ← sources + clips générés (gitignoré)
├── subtitles/         ← .srt par vidéo
└── exports/           ← rendus finaux par plateforme (gitignoré)
```

`rushes/` et `exports/` contiennent des binaires lourds : ils sont dans `.gitignore` — archivage sur le stockage configuré du client, pas dans git.
