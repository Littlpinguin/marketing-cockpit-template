# 00-intel — mémoire d'intelligence business (confidentiel, jamais versionné)

## Rôle

Ce dossier est la mémoire vive du copilot : transcriptions de meetings, notes internes, signaux clients et prospects. **Rien ici n'est versionné** (voir `.gitignore` racine) — ce sont des données confidentielles propres à {{COMPANY_NAME}}.

## Alimentation

- **Automatique (recommandé)** : un workflow n8n dépose les transcriptions de meetings (Fireflies, tl;dv, Granola, etc.) dans `inbox/`. Configuration via le module `automatisations` (`/modules`).
- **Manuelle** : glissez n'importe quel fichier (transcription, note, brief, email important) dans `inbox/`.

## Classification

Tout fichier arrivant dans `inbox/` doit être trié vers :

| Dossier | Contenu |
|---|---|
| `interne/` | Réunions d'équipe, décisions internes, points stratégie |
| `clients/<nom>/` | Tout ce qui concerne un client existant |
| `prospects/<nom>/` | Rendez-vous commerciaux, R1, besoins exprimés |

À la classification : renommer en `AAAA-MM-JJ-sujet.md`, ajouter en tête 3-5 lignes de synthèse (participants, décisions, actions, angles de contenu détectés).

## Consultation en début de session

1. Le hook SessionStart signale les fichiers non traités dans `inbox/`.
2. S'il y en a : proposer de les classer avant toute production.
3. Avant de rédiger du contenu stratégique ou commercial, consulter les fichiers récents pertinents (`interne/` pour le positionnement, `clients/`/`prospects/` pour les cas concrets et le vocabulaire terrain).

## Règles

- ❌ Ne jamais committer le contenu de ce dossier ni le citer verbatim dans du contenu public.
- ❌ Ne jamais publier un nom de client/prospect sans accord explicite.
- ✅ Anonymiser toute donnée issue d'ici avant usage dans un livrable public.
