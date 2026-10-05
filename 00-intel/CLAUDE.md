# 00-intel — mémoire d'intelligence business (confidentiel, jamais versionné)

## Rôle

Ce dossier est la mémoire vive du cockpit : transcriptions de meetings, notes internes, signaux clients et prospects. **Rien ici n'est versionné** (voir `.gitignore` racine) — ce sont des données confidentielles propres à {{COMPANY_NAME}}.

## Alimentation

- **Automatique, Google Workspace** : les notes et transcriptions Gemini d'un Drive partagé arrivent dans `inbox/` chaque lundi matin (Apps Script → Drive pour ordinateur → `scripts/sync-intel.py`). Seules les nouveautés circulent : 30 jours d'historique au premier passage, puis uniquement les réunions nouvelles ou modifiées. Entretiens de candidats et comptabilité exclus à la source. Installation et dépannage : `_integrations/drive-transcripts/README.md`.
- **Automatique, n8n** : un workflow n8n dépose les transcriptions de meetings (Fireflies, tl;dv, Granola, etc.) dans `inbox/`. Configuration via le module `automatisations` (`/modules`).
- **Manuelle** : glissez n'importe quel fichier (transcription, note, brief, email important) dans `inbox/`.

## Routines (chaîne Drive)

| Tâche planifiée | Quand | Procédure |
|---|---|---|
| `intel-hebdo` | Lundi, 7 h | `_integrations/drive-transcripts/routine-intel-hebdo.md` : synchro et classement avec synthèse ; les faits urgents sont marqués pour le radar |
| `radar-com` | Lundi, 8 h 30 | `_integrations/drive-transcripts/routine-radar-com.md` : urgents en tête, sujets de communication de la semaine, brief newsletter le premier lundi du mois |

Leurs sorties vivent dans `radar/` (radars hebdomadaires, journal de la routine intel), hors Git comme le reste du dossier.

## Classification

Tout fichier arrivant dans `inbox/` doit être trié vers :

| Dossier | Contenu |
|---|---|
| `interne/` | Réunions d'équipe, décisions internes, points stratégie |
| `clients/<nom>/` | Tout ce qui concerne un client existant |
| `prospects/<nom>/` | Rendez-vous commerciaux, R1, besoins exprimés |
| `partenaires/<nom>/` | Organisations qui travaillent avec {{COMPANY_SHORT_NAME}} sans lui acheter de mission (pratique partagée, co-offre, apport d'affaires) |

À la classification : renommer en `AAAA-MM-JJ-sujet.md`, ajouter en tête 3-5 lignes de synthèse (participants, décisions, actions, angles de contenu détectés) et les champs `categorie`, `signal`, `angles` (et `sensible: finance | rh` si besoin) au frontmatter. Format exact : `_integrations/drive-transcripts/routine-intel-hebdo.md`, étape 2.

## Consultation en début de session

1. Le hook SessionStart signale les fichiers non traités dans `inbox/`.
2. S'il y en a : proposer de les classer avant toute production.
3. Avant de rédiger du contenu stratégique ou commercial, consulter les fichiers récents pertinents (`interne/` pour le positionnement, `clients/`/`prospects/`/`partenaires/` pour les cas concrets et le vocabulaire terrain).

## Règles

- ❌ Ne jamais committer le contenu de ce dossier ni le citer verbatim dans du contenu public.
- ❌ Ne jamais publier un nom de client, prospect ou partenaire sans accord explicite.
- ✅ Anonymiser toute donnée issue d'ici avant usage dans un livrable public.
