---
name: copywriting
description: Write web pages, landing pages, and long-form content for {{COMPANY_NAME}}. Uses the design system and reusable section templates.
---

# copywriting — web content authoring {{COMPANY_NAME}}

You draft landing pages, product pages, and long-form web content with the design system and brand voice in mind.

## Étape 0 — Doctrine de marque (OBLIGATOIRE)

Avant d'écrire la moindre ligne de copy :

1. Charger `01-brand/checklist-pre-composition.md` — règles de voix, anti-style-IA, typographie, assets, réutilisation.
2. Charger `01-brand/voice.md` — position de voix, vocabulaire, interdits.

**Ne jamais produire sans.** Si l'un des deux fichiers manque ou contient encore des `{{...}}`, arrêter et lancer `/start-copilot`. Les interdits anti-style-IA (parallélismes négatifs, vocabulaire IA mort, tiret cadratin) s'appliquent à chaque headline, sous-titre et CTA.

## Mandatory preflight

1. Read `01-brand/voice.md` — tone, vocabulary, bans.
2. Read `01-brand/style-guide.md` — visual system, tokens.
3. Read `05-web-content/CLAUDE.md` — structure and technical conventions.
4. Browse existing pages in `05-web-content/` to calibrate tone.
5. **Retrieve source material:**

   **If Qdrant is enabled:**
   ```
   qdrant_search(query="<page theme or angle>", top=8)
   ```
   Use hits:
   - **landing-page** → structures that worked, reusable sections
   - **brand-doc** → canonical phrasing for strategic formulations
   - **newsletter / linkedin-post** → validated phrasings, resonant hooks
   - **transcript** → internal quotes usable ("as [name] said in the sync...")

   For numbers:
   ```
   qdrant_search(query="<stat>", top=3, filter_source_key="brand")
   ```

   **If Qdrant is disabled:** read `01-brand/messaging-framework.md` for positioning and numbers; scan `05-web-content/` for similar pages.

## Design system quick reference

| Element | Value |
|---|---|
| Primary font | {{BRAND_FONT_PRIMARY}} |
| Primary color | `{{BRAND_COLOR_PRIMARY}}` |
| Accent | `{{BRAND_COLOR_ACCENT}}` |
| Dark | `{{BRAND_COLOR_DARK}}` |
| Light | `{{BRAND_COLOR_LIGHT}}` |
| Gradient | `{{BRAND_GRADIENT}}` |
| Border-radius | {{BRAND_BORDER_RADIUS}} |
| Illustration style | {{BRAND_ILLUSTRATION_STYLE}} |

## Section template catalog

Each landing page is assembled from modular sections:

| Section | Use |
|---|---|
| Hero | Main headline + sub-head + primary CTA |
| Problem statement | Persona pain points |
| Solutions / Features | Value proposition in 3-4 blocks |
| Social proof | Client logos, numbers, testimonials |
| Timeline / Process | Process steps |
| Comparison table | vs alternatives |
| Stats showcase | Big numbers |
| Testimonials | Quotes with portrait |
| FAQ accordion | Common questions |
| Case study | Concrete results |
| For whom | Per-persona blocks |
| Final CTA | Conversion block with gradient |

**Default sequence**: Hero → Problem → Solutions → Social Proof → Stats → Testimonials → FAQ → Final CTA.

## Writing principles

### Clarity before creativity

If forced to choose between clear and clever, pick clear. Each page answers ONE question.

### Data as hero

Numbers are the primary visual element. A big number beats a paragraph.

### Benefit over feature

"Find the right expert in 48 hours" > "Access to our network of 100+ experts"

### Specificity over vagueness

"8.8/10 satisfaction (n=136)" > "High satisfaction"

### Scannable

- H2 for each section
- 2-3 sentences max per paragraph
- Generous whitespace
- One CTA per section max
- Mobile-first (test at 375px width)

## Bilingualism (if applicable)

{{BILINGUAL_RULES}}

## Brand-specific customizations

{{COPYWRITING_SPECIFIC_RULES}}

## Pre-delivery checklist

- [ ] Reviewed existing pages for tone
- [ ] One clear value proposition per page
- [ ] Data as hero (numbers visible, not buried)
- [ ] Every number verified against Qdrant brand or cited external source
- [ ] Scannable (headlines, short paragraphs, whitespace)
- [ ] Clear single CTA per section
- [ ] Design system respected (colors, fonts, border-radius)
- [ ] No stock photos ({{BRAND_BANNED_VISUALS}})
- [ ] Brand vocabulary respected
- [ ] Bilingual versions if applicable
- [ ] Mobile-friendly tested

## Associated skills

- `copy-editing` — 7-pass review
- `image-generation` — page visuals
- `seo` — on-page optimization
- `brand-check` — mandatory final validation
