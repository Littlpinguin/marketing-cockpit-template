---
name: connect-qdrant
description: Enable Qdrant-based semantic memory. Callable any time — during setup or months later. Walks through the 5-minute activation: API key verification, collection creation, initial ingestion of the brand doctrine, and sanity-check query.
---

# /connect-qdrant — enable semantic memory

Load the `copilot-setup` skill first.

## Intent

Qdrant is optional. Each skill in the repo has a file-based fallback — the system works without it. This command turns Qdrant **on** when the user decides the volume justifies it.

## When Qdrant is actually useful

Recommend Qdrant when the user's projected volume exceeds **~10 published pieces per month** across all channels combined. Below that, a file-based scan of `examples/`, `editions/`, and `articles/` is fast enough and more transparent.

Above that threshold, Qdrant delivers:
- Anti-repetition check across months of archives (< 500 ms)
- Cross-channel consistency (a claim in this week's post vs last month's blog)
- Fast retrieval from the brand doctrine without rereading `01-brand/` every session
- Surfaced meeting transcripts and research notes

Below that threshold, the file-based fallback stays faster to reason about, with zero API dependency.

## Flow

### Step 1 — Confirm intent and echo security

Output:

> You're about to enable Qdrant-based semantic memory. Two things:
>
> 1. This adds two external dependencies: a Qdrant Cloud cluster and a Google AI API key for embeddings. Both have free tiers that cover most small teams.
> 2. I will test the API keys by listing collections — I will not print the keys back to you. Keys stay in `.env` only.
>
> Full security rules: `SECURITY.md`.

### Step 2 — Check `.env`

Read `.env` (presence check only, never print values). Look for:
- `QDRANT_URL`
- `QDRANT_API_KEY`
- `QDRANT_COLLECTION` (optional, default `knowledge`)
- `GOOGLE_AI_API_KEY`

If any is missing, ask the user to add it and wait.

If the user doesn't have a Qdrant Cloud cluster yet:

> You'll need a free cluster. Go to https://cloud.qdrant.io, create an account, create a cluster (the free tier is fine for up to ~3000 pieces of content), then:
>
> 1. Grab the cluster URL (not the management URL).
> 2. Create a **Cluster API Key** (Data Access) — not a management key. Management keys return 403 on collection operations, which is the #1 reason first-time setups fail.
> 3. Paste both into `.env` as `QDRANT_URL` and `QDRANT_API_KEY`. Wrap the key in double quotes if it contains a `|`.
>
> Tell me when that's done.

### Step 3 — Test connectivity

Run `curl -s -H "api-key: $QDRANT_API_KEY" $QDRANT_URL/collections -o /tmp/qdrant-test.json -w "%{http_code}"` (loaded from env, never printed).

- `200` → ok.
- `403` → the key is a management key, not a cluster API key. Guide remediation.
- Other → surface the error.

### Step 4 — Create collection

Run `python3 _integrations/qdrant/init_collection.py`. Confirm the collection exists with the expected dimensions (3072 for `gemini-embedding-001`).

### Step 5 — Initial ingestion

Offer two paths:

> Should I seed Qdrant with your brand doctrine now, or do you want to seed a richer corpus (past posts, newsletters, articles)?
>
> 1. **Brand only (fast)**: `python3 _integrations/qdrant/sync.py --source brand` — ingests `01-brand/*.md`. ~30 seconds.
> 2. **Seed with real content**: run `/seed-corpus` to bring in your recent posts, editions, articles. ~2-5 minutes.
> 3. **Skip for now**: I'll enable the feature; you ingest when you're ready.

### Step 6 — Sanity-check query

Run:

```
python3 _integrations/qdrant/sync.py --query "what's our brand voice" --top 3
```

Show the user the top 3 hits and their scores. If scores are < 0.5, something is off (likely wrong collection name or the brand doc is empty).

### Step 7 — Update `.setup-completed`

In-memory only (the file write is owned by `/validate-setup`). Set:

```json
"features": {
  "qdrant": {
    "enabled": true,
    "collection": "<collection_name>",
    "embedding_model": "gemini-embedding-001",
    "rationale": "user-requested enable"
  }
}
```

### Step 8 — Offer weekly cron install

Ask:

> Want to install the weekly sync cron? It runs Sunday at 22:00 via macOS launchd, syncs every source, and audits for drift. You can also run it manually any time with `python3 _integrations/qdrant/sync.py --all`.
>
> Install cron? (yes / later / not-on-macos)

If yes: run `bash _integrations/qdrant/cron/install.sh` (see the cron readme). Confirm load with `launchctl list | grep qdrant`.

### Step 9 — Hand back

Output:

> Qdrant is live. Skills will now use semantic retrieval automatically — `brand-check` anti-repetition, `content-strategy` pillar audit, `social-content` inspiration queries, all on.
>
> You can disable at any time: edit `.setup-completed` to set `features.qdrant.enabled: false`, or re-run this command and choose to disable.

## Failure modes to avoid

- **Don't enable Qdrant without API keys confirmed.** An "enabled but unreachable" flag creates worse UX than disabled.
- **Don't print the API key back to the user, ever.** Presence check only.
- **Don't silently install the cron.** User must opt in explicitly.
- **Don't skip the rationale recording.** The `rationale` field helps the user remember why Qdrant is on a year later.
