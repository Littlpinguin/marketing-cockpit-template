---
name: seed-corpus
description: Optional. Ingest the user's recent published content into Qdrant (if enabled) or organize it locally in archive folders (if not) so the copilot starts with real memory instead of blank state. Accepts URLs, file drops, or the fictional _examples/ starter pack.
---

# /seed-corpus — feed real content to the copilot's memory

Load the `copilot-setup` skill first.

## Intent

On day one, the copilot has no past content to learn from. Anti-repetition checks return nothing, voice calibration reads generic templates, and the first drafts lack grounding. This command fixes that by ingesting recent published content.

Two modes depending on what the user has:

- **Mode A — Real corpus**: the user shares URLs or file drops of recent LinkedIn posts, newsletters, blog articles. The best option — the copilot learns the real voice.
- **Mode B — Starter pack**: the user has nothing to share yet. The fictional `_examples/` corpus (Acme SaaS) becomes the seed so the copilot has examples of the expected structures and tones. Replace progressively with real content as it's published.

## Preconditions

- `/brand-discover` has run (we know the voice doctrine).
- `/tools-setup` has run (we know which channels are active).
- **If Qdrant is enabled**: `/connect-qdrant` has run and the cluster is reachable.

If Qdrant is disabled, this command still runs — but instead of ingesting vectors, it organizes content into `examples/`, `editions/`, and `articles/` folders so the fallback file scan has material to work with.

## Flow

### Step 1 — Ask what the user has

Output:

> I'll seed the copilot's memory with your recent content. What do you have on hand?
>
> 1. **URLs**: paste up to 10 URLs of recent LinkedIn posts, X posts, blog articles, and newsletter archive pages. I'll fetch and ingest them.
> 2. **Files**: drop Markdown, `.eml`, or `.html` exports into `_bootstrap/inputs/corpus/`. Tell me "ready" when done.
> 3. **Nothing yet**: I'll install the `_examples/` starter pack (fictional Acme SaaS content). It's not your voice, but it gives the copilot a structure to calibrate against. Replace progressively as you publish.
> 4. **Skip**: the copilot will operate on the brand doctrine alone. Less context, still works.
>
> What would you like? (1 / 2 / 3 / 4)

### Step 2a — URL mode

For each URL:
- `WebFetch` to get the text.
- Classify by content type: LinkedIn post / blog article / newsletter / webinar recap / landing page.
- Extract title, publish date, body, first paragraph (for preview).
- Save as a Markdown file in the appropriate archive folder:
  - LinkedIn → `03-social-media/linkedin/examples/YYYY-MM-DD-<slug>.md`
  - Newsletter → `04-email/newsletter/editions/YYYY-MM-DD-<slug>.md`
  - Blog → `09-blog-seo/articles/YYYY-MM-DD-<slug>.md`
  - Other → `_sources/research/YYYY-MM-DD-<slug>.md`
- Add frontmatter: `source_url`, `ingested_at`, `content_type`, `language`.

Then if Qdrant is enabled, run:
```
python3 _integrations/qdrant/sync.py --all
```

### Step 2b — File drop mode

- Scan `_bootstrap/inputs/corpus/` recursively.
- Read each Markdown file directly; convert `.eml` and `.html` to Markdown (stripping HTML but preserving structure).
- Classify and save to archive folders as in 2a.
- Trigger Qdrant sync if enabled.

### Step 2c — Starter pack mode

- Copy `_examples/acme-saas/*` into the corresponding archive folders:
  - `_examples/acme-saas/linkedin/*` → `03-social-media/linkedin/examples/` (prefix filenames with `EXAMPLE-`)
  - `_examples/acme-saas/newsletter/*` → `04-email/newsletter/editions/` (prefix `EXAMPLE-`)
  - `_examples/acme-saas/articles/*` → `09-blog-seo/articles/` (prefix `EXAMPLE-`)
- Warn the user: "These are fictional. Replace progressively. The `EXAMPLE-` prefix is how I identify them so they can be filtered out or removed later."
- If Qdrant is enabled, sync with `--tag example=true` so anti-repetition queries can be configured to ignore examples by default.

### Step 2d — Skip mode

Do nothing. Return control to the caller.

### Step 3 — Report

Output:

> Corpus seeded. Summary:
>
> - LinkedIn posts ingested: N
> - Newsletter editions: N
> - Blog articles: N
> - Other sources: N
> - Qdrant: [enabled: N chunks indexed / disabled: N files in archive folders]
>
> You can re-run `/seed-corpus` any time to add more. For automated ongoing ingestion (e.g. weekly pull from your Notion, Outline, or blog CMS), run `/connect-qdrant` and then the weekly cron.

### Step 4 — Hand back

Return control.

## Failure modes to avoid

- **Don't fetch URLs behind login**. WebFetch will fail cleanly; report the failure and move on.
- **Don't mix starter-pack with real content without the `EXAMPLE-` prefix**. Users must always be able to distinguish fictional from real.
- **Don't delete anything from `_bootstrap/inputs/corpus/` after ingestion**. Leave the user to decide what to archive.
- **Don't claim Qdrant coverage if it's disabled**. Be explicit about the fallback state.
