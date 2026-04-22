# Qdrant Pipeline — runbook

> **Status of this document**: source of truth for the ingestion workflow. Any change to `sync.py` or the enrichers must be reflected here in the same commit. Drift between code and doc destabilizes the whole system.

## Purpose

Maintain a unified semantic memory of the marketing corpus (published content, transcripts, brand doctrine, internal data, knowledge base) accessible via vector query. The system is **incremental** — each run ingests only the delta since the previous run. **Idempotent** — rerunning `sync.py --all` back to back is a no-op.

## Architecture at a glance

- **One Qdrant collection**: name configured in `config.yaml` (default `knowledge`), 3072 native dimensions (Gemini `gemini-embedding-001`), cosine distance.
- **One local registry**: `registry.json`, gitignored. Source of truth on what is indexed.
- **One config file**: `config.yaml` — describes sources, active enrichers, chunking rules, and the functionalities map (editorial_calendar, email_marketing, ...).
- **Sources**: local folders (brand, content archives, transcripts, research) + API connectors (Notion, Outline, custom).
- **Enrichers**: hash, summary, entities, claims, meeting (transcripts only). Applied in cascade at ingestion.
- **Embedder**: Gemini `gemini-embedding-001` (key `GOOGLE_AI_API_KEY` in `.env`).

## Prerequisites

### Environment variables (`.env`)
```
QDRANT_URL=https://xxxxxxxx.region.cloud.qdrant.io
QDRANT_API_KEY="xxx"                     # Cluster API key (not a management key)
QDRANT_COLLECTION=knowledge              # or whatever you chose during setup
GOOGLE_AI_API_KEY=AIzaSy...
# Plus optional keys based on selected tools: NOTION_API_KEY, OUTLINE_API_KEY, etc.
```

### Dépendances Python
```
pip install qdrant-client google-genai python-dotenv pyyaml requests mcp
```

### Initialisation (à faire UNE fois)
```bash
cd _integrations/qdrant
python3 init_collection.py      # crée la collection avec le schéma + index payload
```
Idempotent : si la collection existe déjà avec le bon schéma, ne fait rien.

## Commandes disponibles (stables, ne jamais les renommer)

```bash
cd _integrations/qdrant

# Ingestion incrémentale de toutes les sources actives dans config.yaml
python3 sync.py --all

# Une seule source
python3 sync.py --source notion
python3 sync.py --source brand
python3 sync.py --source newsletters
python3 sync.py --source transcripts

# Dry-run : affiche ce qui serait ingéré, n'écrit rien
python3 sync.py --all --dry-run
python3 sync.py --source notion --dry-run

# Stats du registre
python3 sync.py --stats

# Ré-ingestion totale d'une source (purge les points Qdrant correspondants + re-scan)
python3 sync.py --source brand --force

# Audit : vérifie la cohérence registry ↔ Qdrant
python3 sync.py --verify

# Test de requête sémantique (debug)
python3 sync.py --query "your question here" --top 5
```

## Les 6 phases du pipeline

### Phase 1 – Détection des changements

Pour chaque source active dans `config.yaml` :

1. **Filesystem** : glob le pattern, exclusions globales + locales appliquées.
2. **Notion** : appel REST `POST /v1/databases/{id}/query` avec filtre sur le statut et la checkbox Validé.
3. **Outline** : `POST /api/documents.list` par collection configurée.
4. **Transcripts** : scan récursif, parsing du format Gemini.

Pour chaque élément trouvé :
- Calcul du **content hash** (SHA-256 du texte normalisé).
- Comparaison au registre :
  - Pas de trace → **nouveau**, à ingérer
  - Hash différent → **modifié**, delete puis ré-ingérer
  - Hash identique → **skip**

### Phase 2 – Chunking

Stratégies par type de contenu :
- **`whole`** : posts courts, emails (1 chunk = 1 doc entier)
- **`by_section_h2`** : newsletters, articles blog (split par section H2)
- **`sliding_window`** : brand docs, longs documents (chunks 600 tokens, overlap 100)
- **`by_transcript_section`** : transcripts Gemini (sections structurelles + bullets Détails groupés par budget de tokens 800-1200)

### Phase 3 – Enrichissement (ordre strict)

1. **`hash`** – SHA-256 pour dédup
2. **`summary`** – 2 phrases factuelles via Gemini 2.5 Flash
3. **`entities`** – extraction de clients, personnes, outils, chiffres, lieux
4. **`claims`** – 3 à 5 affirmations factuelles
5. **`meeting`** – décisions et action items (transcripts uniquement)

Chaque enricher peut échouer silencieusement (log WARN). Le chunk est ingéré avec ce qui est disponible.

**Important pour Gemini 2.5 Flash** : le `thinkingConfig: {thinkingBudget: 0}` est obligatoire dans les generationConfig sinon le modèle consomme tout le budget en réflexion interne avant de produire la réponse. Ce paramètre est déjà câblé dans `enrichers/__init__.py`.

### Phase 4 – Embedding Gemini

- Modèle : `gemini-embedding-001` (API `embedContent`)
- Dimensions : 3072 natives
- Task type : `RETRIEVAL_DOCUMENT` à l'ingestion, `RETRIEVAL_QUERY` à la requête
- Input = `content_text` brut (pas le résumé)
- Retry : 3 tentatives avec backoff 1s/4s/16s
- Rate limit : `sleep 0.2s` entre appels

### Phase 5 – Upsert Qdrant

- ID déterministe : `uuid5(namespace, source_file + chunk_index)` – ré-ingérer le même contenu produit les mêmes IDs
- Delete des anciens points avant upsert en cas de update (évite les fantômes)
- Batch 50 points par appel

### Phase 6 – Mise à jour du registre

Après chaque doc ingéré avec succès, MAJ de `registry.json` :

```json
{
  "version": 1,
  "last_sync": {
    "all": "2026-04-15T10:30:00Z",
    "notion": "2026-04-15T10:30:00Z"
  },
  "entries": {
    "path/to/file.md": {
      "content_hash": "a1b2c3...",
      "ingested_at": "2026-04-15T10:30:05Z",
      "source_key": "newsletters",
      "type": "newsletter",
      "chunks_total": 5,
      "qdrant_point_ids": ["uuid-1", "uuid-2", "uuid-3", "uuid-4", "uuid-5"]
    }
  }
}
```

Le registre est **commité dans git** : c'est l'état de vérité.

## Serveur MCP (utilisation dans Claude Code)

Une fois la base ingérée, le serveur MCP custom (`mcp_server.py`) est exposé dans Claude Code via `.mcp.json`. Il offre 3 outils que les skills appellent directement :

- **`mcp__qdrant__qdrant_search(query, top, filter_type, filter_source_key, filter_channel)`** – recherche sémantique avec filtres optionnels
- **`mcp__qdrant__qdrant_find_similar(text, top, exclude_source_file, threshold)`** – anti-répétition pour brand-check
- **`mcp__qdrant__qdrant_stats()`** – état de la collection

## Troubleshooting

### `{"error":"forbidden"}` sur toutes les requêtes Qdrant
- Probable : clé de management au lieu de clé cluster. Va sur Qdrant Cloud → Access Management → Create Database API Key.
- Vérifier aussi que le cluster n'est pas en pause (free tier s'auto-suspend après inactivité).

### Gemini retourne 429 (rate limit)
- Diminue `batch_size` dans `config.yaml`
- Augmente `sleep_between_calls_sec`

### Gemini 2.5 Flash retourne des résumés tronqués ("N2 s", "X est une")
- Le `thinkingBudget: 0` est manquant dans `generationConfig`. Vérifier `enrichers/__init__.py`.

### Drift entre registry et Qdrant après `--force`
- Bug historique : la branche `--force` ne passait pas `existing` pour deleter les anciens points. Corrigé en 0.1.0.
- Si drift persistant : `python3 sync.py --verify` pour diagnostiquer, puis nettoyage manuel via scroll + delete.

### Notion filter ne retourne rien
- Vérifier l'exact match du statut. Copier depuis Notion directement, ne pas retaper (caractères invisibles comme 2 espaces après un emoji).

## Historique des runs significatifs

Consigner ici tout changement structurel (nouvelle source, nouveau champ de payload, changement de modèle d'embedding). Format : `YYYY-MM-DD – Changement – Impact`.

- **{{SETUP_DATE}}** – Initialisation du pipeline pour {{COMPANY_NAME}}.

## Ce que ce runbook NE couvre PAS (volontairement)

- **Orchestration cron** – géré séparément dans `cron/`
- **Ingestion d'images** – hors scope, les images sont référencées par chemin dans le payload mais pas embedded
- **Performance scores** (engagement, taux d'ouverture) – hors scope v1
