# _sources — raw material

Raw data that feeds every AI role of the copilot. Everything here is indexed in Qdrant (collection configured in `_integrations/qdrant/config.yaml`) when Qdrant is enabled, or read directly from disk by skills' file-based fallback when it isn't.

## Structure

```
_sources/
├── transcriptions/
│   ├── internal/            # Internal meetings (strategy, syncs, board)
│   └── clients/             # Client meetings, one folder per client
│       └── <client-name>/
├── reports/                 # Raw data (internal studies, benchmarks, industry reports)
└── research/                # Market intelligence — external articles, notes, observations
```

## What each subfolder is for

### `transcriptions/` — meeting minutes

- **Format**: Markdown, ideally Gemini Notes format (H3 sections: Summary / Résumé, Next steps / Étapes suivantes, Details / Détails with timestamps). The parser handles both English and French heading variants.
- **Fed by**: manual drop after each important meeting.
- **Naming convention**: `YYYY-MM-DD-subject.md`.
- **Special chunking**: structural H3 sections each become their own chunk; inside Details, bullets are grouped by token budget (see `_integrations/qdrant/utils.py::chunk_by_transcript_section`).
- **Value**: contains decisions and action items usable as source of truth by content agents ("what did we decide about X at the last sync?").

### `reports/` — quantitative data

- **Format**: Markdown, ideally structured with H2 sections.
- **Fed by**: manual drop when a new study / benchmark / internal research is complete.
- **Naming convention**: `YYYY-MM-DD-type-subject.md`.
- **Value**: canonical source for every number cited in published content. Agents must verify each number against this folder (via `qdrant_search(filter_source_key="reports")` if Qdrant is on, or grep if it isn't).

### `research/` — market intelligence

Landing pad for all external market intelligence: competitor observations, industry trends, regulation updates, AI progress, news. Keeps the copilot current without relying on stale training data.

**Automation candidates** (not shipped):
- RSS feeds (industry blogs, analyst firms, competitor newsrooms)
- Third-party newsletters parsed via a Gmail integration + Gemini auto-summary
- Google Alerts / Talkwalker turned into markdown
- Web agents monitoring key pages (competitor pricing, release notes, job boards)
- Competitor analysis screenshots via Gemini vision OCR

**Extension suggestion**: add Python scripts in `_integrations/research/` that drop markdown files matching the convention below, then trigger `sync.py --source research` after each drop.

**Recommended file shape** for research items (manual or automated):

```markdown
---
source: "Gartner Report 2026"
url: "https://www.gartner.com/..."
author: "Gartner Research"
date: 2026-04-15
tags: [industry, trends, ai]
---

# Title of the article

## Summary (1-2 sentences)
...

## Key points
- ...
- ...

## Relevance to our company
...

## Quotable excerpt
"..." (page/section)
```

## Metadata extracted at ingestion

- `source_type`: transcription | report | research-note
- `client`: client name (if under `transcriptions/clients/`)
- `date`: extracted from filename or frontmatter
- `tags`: from frontmatter or detected in content
- `participants`: for transcripts, extracted from the header
- `entities`: extracted by the `entities` enricher (clients, people, tools, numbers)
- `summary`: 2-sentence auto-summary
- `claims`: 3-5 factual claims
- `decisions` and `action_items`: transcripts only, extracted by the `meeting` enricher

## Manual ingestion

```bash
cd _integrations/qdrant
python3 sync.py --source transcripts
python3 sync.py --source reports
python3 sync.py --source research
# or everything at once
python3 sync.py --all
```

## Privacy

- Files under these subfolders are **gitignored** by default (see `.gitignore`).
- Only this `README.md` and `.gitkeep` files are tracked.
- Raw meeting transcripts, internal reports, and research notes stay on your local machine. Qdrant Cloud holds the embeddings (numerical vectors) and the chunked text payload. For sensitive content, consider self-hosting Qdrant instead — a flag is available in `_integrations/qdrant/config.yaml`.
