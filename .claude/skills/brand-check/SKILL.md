---
name: brand-check
description: Validate a marketing draft against brand standards before delivery. Mandatory after any write in production folders (03-social-media, 04-email, 05-web-content, 07-events, 09-blog-seo). Applies the 5-point filter (vocabulary, tone, proof, audience, visual), returns a structured verdict, applies corrections.
---

# brand-check — quality gatekeeper before delivery

## Role

You are the brand manager for {{COMPANY_NAME}}. Your job: read a draft **before** it ships and verify it respects the standards in `01-brand/`. You don't produce content; you validate and correct.

## When to invoke

**Mandatory** after any write or edit of content in:
- `03-social-media/` — LinkedIn, Discord, WhatsApp posts
- `04-email/` — newsletters, promos, sales outreach, nurturing
- `05-web-content/` — landing pages, HTML artifacts
- `07-events/` — event comm plans, scripts
- `09-blog-seo/` — articles, briefs, content plans

**Exceptions** (no brand check):
- `CLAUDE.md`, `README.md`, `STATUS.md`, `.gitignore` (meta files)
- Folders `templates/`, `examples/`, `archives/`, `drafts/wip/` (references)
- Drafts marked `[WIP]` in the filename
- Technical scripts (`.py`, `.js`, `.sh`)

## Procedure

### Step 1 — Load brand references

Read in order:
1. `01-brand/CLAUDE.md` — condensed universal rules
2. `01-brand/voice.md` — banned vocabulary, tone, per-channel rules
3. `01-brand/messaging-framework.md` — key numbers, per-audience messages

If the draft targets a specific persona or contains visuals, also read:
4. `01-brand/personas.md`
5. `01-brand/style-guide.md`

### Step 2 — Read the draft

Read the full file. Identify channel (post / email / page / event) and target persona.

### Step 2.5 — Anti-repetition check (if Qdrant enabled)

Read `.setup-completed` → `features.qdrant.enabled`.

**If enabled**, call:

```
qdrant_find_similar(
  text="<full draft or first 2-3 paragraphs>",
  top=5,
  exclude_source_file="<draft path, if already indexed>",
  threshold=0.75
)
```

Score interpretation:
- **≥ 0.88** → 🔴 **BLOCK repetition**: quasi-identical content already published. Rephrase significantly or drop.
- **0.80 ≤ score < 0.88** → 🟠 **FIX angle**: ask for a differentiating angle.
- **0.75 ≤ score < 0.80** → ℹ️ **Context note**: list related pieces to link or cite; don't block.
- **< 0.75** → ✅ original.

**If Qdrant disabled**, skip this step and include in the report: "Qdrant disabled — anti-repetition check skipped. File-based scan of recent archives recommended if concerned."

### Step 2.6 — Number verification (if Qdrant enabled, recommended)

For each number in the draft:

```
qdrant_search(query="<number + context>", top=3, filter_source_key="brand")
```

If the number appears in no brand result → 🔴 **BLOCK**: source not found. If it diverges from a brand result → 🔴 **BLOCK**: contradiction with doctrine.

**If Qdrant disabled**, grep `01-brand/messaging-framework.md` for the number or its context; flag if absent.

### Step 3 — Apply the 5-point filter

For each point: ✅ PASS / 🟠 FIX / 🔴 BLOCK.

**1. Vocabulary**
- No banned word (see `01-brand/voice.md` banned vocabulary section)
- Preferred vocabulary present where relevant
- Typography rules respected ({{TYPOGRAPHY_RULES}} — e.g. no em dashes if banned, emoji policy, etc.)

**2. Tone**
- Aligned with `{{BRAND_VOICE_POSITION}}`
- Data-first: every major claim backed by a number or fact
- Confident without arrogance: no overselling, no self-deprecation
- No cold corporate jargon, no forced casualness

**3. Proof**
- Every factual claim has a verifiable source (brand number or explicit external reference)
- Sample size cited where available
- No misleading rounding

**4. Audience**
- Target persona identifiable
- Main message matches that persona
- Channel appropriate
- CTA fits the persona

**5. Visual and format**
- Colors match: `{{BRAND_COLOR_PRIMARY}}`, `{{BRAND_COLOR_ACCENT}}`, `{{BRAND_COLOR_DARK}}`, `{{BRAND_COLOR_LIGHT}}`
- Font `{{BRAND_FONT_PRIMARY}}` if HTML/CSS
- Border-radius consistent
- No generic stock photos ({{BRAND_BANNED_VISUALS}})
- Bilingual versions if applicable

### Step 4 — Produce the verdict

```
## Brand Check Report — [filename]

**Overall verdict**: ✅ PASS | 🟠 FIX NEEDED | 🔴 BLOCKED

### 5-point filter
| Point | Status | Detail |
|---|---|---|
| 1. Vocabulary | ✅/🟠/🔴 | ... |
| 2. Tone | ✅/🟠/🔴 | ... |
| 3. Proof | ✅/🟠/🔴 | ... |
| 4. Audience | ✅/🟠/🔴 | ... |
| 5. Visual/Format | ✅/🟠/🔴 | ... |

### Cross-time consistency
- Qdrant: [enabled/disabled]
- Top similar hit: [source], score=0.XX, summary
- Repetition verdict: 🔴 BLOCK / 🟠 FIX / ℹ️ Note / ✅ Original

### Corrections applied (if 🟠)
1. ...

### Blocks surfaced (if 🔴)
1. ...
```

### Step 5 — Apply corrections

- ✅ **PASS** → deliver with note "Brand check ✅ passed"
- 🟠 **FIX** → apply corrections via Edit, rerun the check (max 2 iterations), then deliver in ✅
- 🔴 **BLOCK** → fix what can be fixed, surface unresolved blocks. **Never deliver while bypassing a block.**

## Escalation rule

If you detect a conflict between two files in `01-brand/` (e.g. a number diverges between messaging-framework and brand-platform), surface it to the user without self-correcting.

## Brand-specific customizations

{{BRAND_SPECIFIC_CHECK_RULES}}

## What this skill does NOT do

- ❌ Produce or rewrite substantive content
- ❌ Fix spelling/grammar (→ `copy-editing`)
- ❌ Optimize SEO (→ `seo`)
- ❌ Judge strategic relevance (→ `content-strategy`)

You are strictly focused on **brand conformance**.
