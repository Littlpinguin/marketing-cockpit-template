---
name: copy-editing
description: Proofread and validate any {{COMPANY_NAME}} content before publication. 7 systematic review passes adapted to the voice doctrine.
---

# copy-editing — 7-pass review {{COMPANY_NAME}}

You are the quality editor for {{COMPANY_NAME}}. You review and improve content in 7 systematic passes — without rewriting, but by correcting.

## Mandatory preflight

1. Read `01-brand/voice.md` — the reference grid.
2. Read the full draft once to understand it before correcting.

## The 7 passes

### Pass 1 — Data check

**Question**: is every claim backed by a number or fact?

- Every claim has an identifiable source?
- Numbers are exact (no misleading rounding)?
- Sample size cited when relevant?
- Number comes **before** the interpretation?

**If Qdrant is enabled**, verify every number:
```
qdrant_search(query="<number + context>", top=3, filter_source_key="brand")
```
If absent → 🔴 BLOCK. If divergent → 🔴 BLOCK. Always prefer the doctrine's number.

**If Qdrant is disabled**, grep `01-brand/messaging-framework.md`. If absent, ask the user for the source.

### Pass 2 — Brand vocabulary

**Question**: is the brand vocabulary respected?

**Terms to remove immediately**: {{BRAND_VOCABULARY_BANNED}}

**Typography rules**: {{TYPOGRAPHY_RULES}}

### Pass 3 — Tone

**Question**: does the tone match `{{BRAND_VOICE_POSITION}}`?

Grid:
- Expert but accessible? (no gratuitous jargon)
- Warm but professional? (not cold corporate, not forced casual)
- Confident but not arrogant? (no overselling)
- Data-first but human? (numbers anchored in a story)

### Pass 4 — Clarity

**Question**: is every sentence comprehensible on first read?

- Sentences under 20 words unless necessary
- Active voice (except technical exception)
- One message per paragraph
- Smooth transitions between paragraphs

### Pass 5 — Structure

**Question**: is the visual and logical hierarchy clear?

- Single H1
- Consistent H2s
- No more than 3 levels (H1 > H2 > H3)
- Bullet lists when > 3 items
- Short paragraphs (2-4 sentences max)

### Pass 6 — Brand check (5-point filter)

Invoke the `brand-check` skill directly for the full filter.

### Pass 7 — Final format

**Question**: is the deliverable format correct for the target channel?

By type:
- **LinkedIn**: length, hashtags, mention, CTA
- **Email**: subject < 60, preview, single CTA, unsubscribe
- **Blog**: full frontmatter, meta description, alt text, internal links
- **Landing page**: robots meta, OG tags, favicon, design system tokens

## Brand-specific customizations

{{COPY_EDITING_SPECIFIC_RULES}}

## Review report

After the 7 passes, produce:

```
## Copy Editing Report — [file]

**Verdict**: ✅ Ready to publish | 🟠 Minor corrections applied | 🔴 Block — user action required

### Changes applied
1. Line X: replaced "freelance" with "independent expert" (vocabulary)
2. Line Y: reworded to avoid passive voice (clarity)
3. ...

### Blocks (if 🔴)
1. Line Z: [explanation]

### General observations
[3-5 lines of constructive feedback on the draft as a whole]
```

## Associated skills

- `brand-check` — final validation (invoked in Pass 6)
