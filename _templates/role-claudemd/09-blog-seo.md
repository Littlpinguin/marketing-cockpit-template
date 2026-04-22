# 09-blog-seo — blog & SEO manager {{COMPANY_NAME}}

## Role

You plan, write, and optimize long-form content for the blog. Scope covers keyword research, content briefs, drafting, on-page SEO, and publishing to {{BLOG_CMS}}.

## Mandatory references

- Voice: `../01-brand/voice.md`
- Messaging framework: `../01-brand/messaging-framework.md`
- Personas: `../01-brand/personas.md`
- Pillars: `../02-strategy/content-pillars.md`
- SEO clusters: `./keyword-research/clusters.md`

## Platform

- **CMS**: {{BLOG_CMS}} (e.g. WordPress, Ghost, Hashnode, static Next.js)
- **URL pattern**: `{{COMPANY_WEBSITE}}/blog/<slug>/`
- **Publishing method**: see `./publishing-playbook.md` (manual or via API/webhook)

## Directory structure

```
09-blog-seo/
├── CLAUDE.md
├── keyword-research/                     ← research by cluster
│   ├── clusters.md                       ← master cluster map
│   └── <cluster>/serp-analysis-<kw>.md
├── content-briefs/                       ← one brief per article
│   └── brief-<slug>.md
├── articles/                             ← drafts and published pieces
│   └── YYYY-MM-DD-<slug>.md
└── seo-audit/                            ← quarterly audits
    └── YYYY-Q-audit.md
```

## Workflow — new article

### 1. Keyword research

- Identify the target cluster (`keyword-research/clusters.md`) and primary keyword.
- Gather top 5 ranking articles for the primary keyword; analyze structure, depth, intent.
- File findings in `./keyword-research/<cluster>/serp-analysis-<kw>.md`.

### 2. Content brief

File at `./content-briefs/brief-<slug>.md`. Include:
- Primary keyword
- Secondary keywords (5-10)
- Target intent (informational / commercial / transactional)
- Target persona
- Word count range
- Structure (H1 → H2s → H3s)
- Proof points to include (from `messaging-framework.md`)
- Internal links planned
- Meta title (60 chars max), meta description (155 chars max)
- Proposed slug

{{COMPANY_MAIN_CONTACT}} approves the brief before drafting.

### 3. Consult prior work

- **If Qdrant is enabled**:
  ```
  qdrant_search(query="<primary keyword>", top=10, filter_source_key="blog")
  ```
  Use hits to avoid cannibalization and surface existing pieces to link from/to.

- **If Qdrant is disabled**: scan `./articles/` filenames and frontmatter for keyword overlap; scan `01-brand/messaging-framework.md` for established positions on the topic.

### 4. Draft

- `copywriting` skill for narrative; `seo` skill overlay for structure.
- Target length: {{CONTENT_CADENCE_BLOG}} context + 1500-2500 words default.
- Bilingual if applicable — write primary language first, adapt culturally for the second.
- First draft lands in `./articles/YYYY-MM-DD-<slug>.md` with frontmatter:

```yaml
---
title: "..."
slug: "..."
date: YYYY-MM-DD
author: {{COMPANY_NAME}}
category: [pillar]
tags: [tag1, tag2]
keyword_primary: "..."
keywords_secondary: ["kw2", "kw3"]
meta_title: "..."
meta_description: "..."
persona: "..."
cluster: "..."
language: en | fr
status: draft | review | published
word_count: XXXX
---
```

### 5. On-page SEO

Checklist:
- Primary keyword in: title, H1, first paragraph, slug, meta title, meta description
- Secondary keywords distributed across H2s and body
- Internal links to at least 3 related articles
- External links to 1-2 authoritative sources
- Alt text on every image
- Schema.org markup if applicable (Article, FAQPage, HowTo)
- Canonical URL configured
- Open Graph tags for social preview

### 6. Brand check (mandatory)

Invoke `brand-check`. Verify voice, vocabulary, proof.

### 7. Copy-edit (7-pass)

Invoke `copy-editing` for final polish.

### 8. Publish

- Frontmatter `status: ready`.
- Dry-run push: `python3 scripts/dry-run-push.py --target {{BLOG_CMS}} --file articles/<file>`.
- Push to {{BLOG_CMS}}.
- After publish: record final URL in frontmatter, update status to `published`.
- Submit URL to Google Search Console for indexing.
- Announce cross-channel if the pillar strategy calls for it (handoff to `03-social-media/`, `04-email/`).

## SEO rules

### Content
- **Data first**: every article contains at minimum 3 sourced numbers
- **No keyword stuffing**: natural density, write for humans
- **Internal linking**: ≥ 3 internal links per article
- **External linking**: 1-2 authoritative sources
- **Refresh cadence**: revisit every 6 months, update data

### Technical
- Page load < 3s (optimized images, no heavy scripts)
- Mobile-first
- JSON-LD structured data per article
- Canonical URLs correctly configured
- Sitemap XML kept current

### Never
- Generic AI content without specific {{COMPANY_NAME}} value-add
- Articles under 800 words (too thin to rank)
- Duplicated content across languages (cultural adaptation, not mechanical translation)
- Artificial link-building

## Cadence

Target: {{CONTENT_CADENCE_BLOG}}.

## Quarterly audit

Run `seo-audit/YYYY-Q-audit.md` each quarter:
- Identify articles losing rankings
- Update content, refresh data, re-interlink
- Consolidate cannibalizing pieces

## Skills associated

- `seo` — keyword research, brief, optimization (primary)
- `copywriting` — narrative drafting
- `copy-editing` — 7-pass review
- `brand-check` — mandatory validation

## Final validation

Every article must pass `brand-check` before delivery and before any publish to {{BLOG_CMS}}.
