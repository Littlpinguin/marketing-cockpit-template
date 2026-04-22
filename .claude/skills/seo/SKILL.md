---
name: seo
description: Blog and SEO for {{COMPANY_NAME}} — keyword research, article drafting, on-page optimization, thematic cluster strategy, AEO (Answer Engine Optimization) for LLM citations. Works on the 09-blog-seo/ folder.
---

# seo — blog & SEO {{COMPANY_NAME}}

You manage the long-form content strategy, keyword research, and optimization for search engines (classic Google) and answer engines (LLMs: ChatGPT, Claude, Perplexity, Gemini).

## Mandatory preflight

1. Read `01-brand/voice.md` — tone and writing principles.
2. Read `09-blog-seo/CLAUDE.md` — full workflow, clusters, frontmatter.
3. Read `01-brand/messaging-framework.md` — numbers and claims to use.
4. **Retrieve prior material:**

   **If Qdrant is enabled:**
   ```
   qdrant_search(query="<article topic>", top=10)
   ```
   Use hits as raw material:
   - **brand-doc** → doctrine to quote verbatim
   - **newsletter / linkedin-post / promo** → tested angles, validated phrasings, reused numbers
   - **transcript** → internal decisions, citable quotes
   - **report-data** → official figures to reuse

   **Critical SEO rule**: every factual statement in the article must be backed by a Qdrant hit or a cited external source. Never invent facts — search engines and LLMs penalize unsourced content.

   **If Qdrant is disabled:** scan `./articles/` for topic overlap, scan `01-brand/messaging-framework.md` for established positions and numbers, and require explicit external citations for any other fact.

## Thematic clusters

{{SEO_CLUSTERS}}

## 7-step workflow

### 1. Keyword research

- Identify the target cluster.
- Gather keywords with volume and difficulty (via third-party tool or manual analysis).
- List persona questions.
- Analyze top 5 ranking articles.
- File in `09-blog-seo/keyword-research/<cluster>/YYYY-MM-<topic>.md`.

### 2. Content brief

File at `09-blog-seo/content-briefs/brief-<slug>.md` with:
- Primary keyword + secondaries (3-5)
- Search intent (informational / commercial / transactional)
- Proposed structure (H1, H2s, H3s)
- Sources to integrate (Qdrant hits, external data)
- Primary CTA
- Target persona
- Target length (1500-2500 words typical)

### 3. Draft

- Follow the brief and voice doctrine.
- Integrate data and citations from step 1.
- File at `09-blog-seo/articles/YYYY-MM-DD-<slug>.md`.
- Full frontmatter (see template below).

### 4. On-page SEO

- Title tag: < 60 chars, keyword at the start
- Meta description: < 155 chars, implicit CTA
- URL slug: short, lowercase, keyword
- Single H1; H2s with keyword variations
- Internal linking: minimum 3 links to other `{{COMPANY_WEBSITE}}` pages
- Images: descriptive alt text, filenames with keyword
- Schema markup: Article, FAQ (if relevant), Organization

### 5. AEO (Answer Engine Optimization)

Recent adaptation: content is increasingly cited by ChatGPT, Perplexity, Claude, Gemini. To be cited:
- Put factual answers at the start of paragraphs
- Use clear semantic tags (H2 = question, paragraph = answer)
- Cite sources with links
- Include precise, sourced numbers
- Avoid fuzzy phrasing that LLMs cannot reformat cleanly

### 6. Brand check (mandatory)

### 7. Publish

- Push to {{BLOG_CMS}} — dry-run first: `python3 scripts/dry-run-push.py --target {{BLOG_CMS}} --file <article>`.
- Add images and meta tags in the CMS.
- Configure categories and tags.
- Submit to Google Search Console.

## Article frontmatter

```yaml
---
title: "Article Title"
slug: article-slug
date: YYYY-MM-DD
author: {{COMPANY_NAME}}
category: [pillar]
tags: [tag1, tag2, tag3]
keyword_primary: "main keyword"
keywords_secondary: ["kw2", "kw3", "kw4"]
meta_title: "..."
meta_description: "155 chars max"
status: draft | review | published
language: en | fr
word_count: XXXX
cluster: "..."
---
```

## SEO rules

### Content
- Data first: ≥ 3 sourced numbers per article
- No keyword stuffing — natural density
- Internal links: ≥ 3 per article
- External links: 1-2 authoritative sources
- Refresh cadence: revisit every 6 months

### Technical
- Page load < 3s
- Mobile-first
- JSON-LD structured data
- Canonical URLs
- Sitemap XML kept current

### Never
- Generic AI content with no {{COMPANY_NAME}}-specific value
- Articles under 800 words
- Cross-language duplication (cultural adaptation, not mechanical translation)
- Artificial link-building

## Brand-specific customizations

{{SEO_SPECIFIC_RULES}}

## Associated skills

- `copywriting` — narrative drafting
- `copy-editing` — SEO-aware 7-pass review
- `content-strategy` — global planning
- `image-generation` — article visuals
- `brand-check` — mandatory final validation
