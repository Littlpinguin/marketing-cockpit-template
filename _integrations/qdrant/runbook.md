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

### Initialization (one-off)
```bash
cd _integrations/qdrant
python3 init_collection.py      # creates the collection with schema + payload indexes
```
Idempotent: if the collection already exists with the correct schema, it's a no-op.

## Available commands (stable — never rename)

```bash
cd _integrations/qdrant

# Incremental ingestion of every source active in config.yaml
python3 sync.py --all

# Single source
python3 sync.py --source notion
python3 sync.py --source brand
python3 sync.py --source newsletters
python3 sync.py --source transcripts

# Dry-run: print what would be ingested, write nothing
python3 sync.py --all --dry-run
python3 sync.py --source notion --dry-run

# Registry stats
python3 sync.py --stats

# Full re-ingestion of one source (purges Qdrant points for that source + rescans)
python3 sync.py --source brand --force

# Audit: verify registry ↔ Qdrant consistency
python3 sync.py --verify

# Sample semantic query (debug)
python3 sync.py --query "your question here" --top 5
```

## The 6-phase pipeline

### Phase 1 — Change detection

For every active source in `config.yaml`:

1. **Filesystem**: glob the pattern, apply global + local exclusions.
2. **Notion**: REST call `POST /v1/databases/{id}/query` with filters on status and optional validation checkbox.
3. **Outline**: `POST /api/documents.list` per configured collection.
4. **Transcripts**: recursive scan, Gemini-format parsing.

For every matched item:
- Compute the **content hash** (SHA-256 of normalized text).
- Compare to the registry:
  - Not present → **new**, ingest
  - Hash differs → **modified**, delete then re-ingest
  - Hash identical → **skip**

### Phase 2 — Chunking

Strategies per content type:
- **`whole`**: short posts, emails (1 chunk = full document)
- **`by_section_h2`**: newsletters, blog articles (split per H2 section)
- **`sliding_window`**: brand docs, long documents (600-token chunks, 100-token overlap)
- **`by_transcript_section`**: Gemini transcripts (structural sections + Details bullets grouped by 800-1200 token budget)

### Phase 3 — Enrichment (strict order)

1. **`hash`** — SHA-256 for deduplication
2. **`summary`** — 2 factual sentences via Gemini 2.5 Flash
3. **`entities`** — extraction of clients, people, tools, numbers, locations
4. **`claims`** — 3 to 5 factual statements
5. **`meeting`** — decisions and action items (transcripts only)

Each enricher may fail silently (WARN log). The chunk is ingested with whatever fields are available.

**Important for Gemini 2.5 Flash**: `thinkingConfig: {thinkingBudget: 0}` is mandatory in `generationConfig`. Without it, the model consumes its entire budget in internal reasoning before producing output. Already wired in `enrichers/__init__.py`.

### Phase 4 — Gemini embedding

- Model: `gemini-embedding-001` (API `embedContent`)
- Dimensions: 3072 native
- Task type: `RETRIEVAL_DOCUMENT` at ingestion, `RETRIEVAL_QUERY` at query
- Input: raw `content_text` (not the summary)
- Retry: 3 attempts with 1s/4s/16s backoff
- Rate limit: `sleep 0.2s` between calls

### Phase 5 — Qdrant upsert

- Deterministic IDs: `uuid5(namespace, source_file + chunk_index)` — reingesting the same content produces the same IDs
- Delete old points before upsert on update (avoids ghost entries)
- Batch 50 points per call

### Phase 6 — Registry update

After every successfully ingested doc, `registry.json` is updated:

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

The registry is the **state of truth**. It lives gitignored by default since content hashes change frequently.

## MCP server (inside Claude Code)

Once the collection is populated, the custom MCP server (`mcp_server.py`) is exposed to Claude Code via `.mcp.json`. It offers 3 tools skills call directly:

- **`mcp__qdrant__qdrant_search(query, top, filter_type, filter_source_key, filter_channel)`** — semantic search with optional filters
- **`mcp__qdrant__qdrant_find_similar(text, top, exclude_source_file, threshold)`** — anti-repetition check for brand-check
- **`mcp__qdrant__qdrant_stats()`** — collection state

## Troubleshooting

### `{"error":"forbidden"}` on every Qdrant request
- Most likely: management key instead of cluster API key. Go to Qdrant Cloud → Access Management → Create Database API Key.
- Also check the cluster is not paused (free tier auto-suspends after inactivity).

### Gemini returns 429 (rate limit)
- Lower `batch_size` in `config.yaml`
- Raise `sleep_between_calls_sec`

### Gemini 2.5 Flash returns truncated summaries (e.g. "Acme s", "X is a")
- `thinkingBudget: 0` missing from `generationConfig`. Check `enrichers/__init__.py`.

### Drift between registry and Qdrant after `--force`
- Historical bug: the `--force` branch didn't pass `existing` to delete old points. Fixed in 0.1.0.
- If drift persists: `python3 sync.py --verify` to diagnose, then manual scroll + delete.

### Notion filter returns nothing
- Verify exact status match. Copy from Notion directly — do not retype (invisible characters such as double spaces after an emoji are common).

## Run history

Log here any structural change (new source, new payload field, embedding model change). Format: `YYYY-MM-DD — change — impact`.

- **{{SETUP_DATE}}** — pipeline initialized for {{COMPANY_NAME}}.

## Out of scope (intentionally)

- **Cron orchestration** — handled separately in `cron/`
- **Image ingestion** — images referenced by path in payloads; not embedded
- **Performance scores** (engagement, open rate) — out of scope for v0.2
