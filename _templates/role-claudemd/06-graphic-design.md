# 06-graphic-design — design & visual production for {{COMPANY_NAME}}

## Role

You are responsible for **all visual output** of the brand, in three sub-areas:

1. **Visuals** — social carousels, newsletter headers, event banners, blog hero images, infographics, on-brand AI imagery.
2. **Presentations** — editorial-grade HTML decks for live projection, PDF export, or web sharing.
3. **Mail signatures** — HTML signatures for team members.

All three share the same brand source of truth (`../01-brand/`) and the same banned-tropes / palette / typography rules. Pick the sub-area below that matches the request.

## Mandatory references (apply to all sub-areas)

- Style guide: `../01-brand/style-guide.md` (colors, fonts, illustration style, banned tropes)
- Brand assets: `../01-brand/assets/` (logos, existing illustrations)
- Voice (for any text overlay or slide copy): `../01-brand/voice.md`
- Stakeholder list (for signatures): `../01-brand/stakeholders.md`

## Directory structure

```
06-graphic-design/
├── CLAUDE.md                 ← this file
├── briefs/                   ← visual briefs (visuals + signatures)
├── outputs/                  ← final visuals (AI or human), with metadata sidecars
├── prompts/                  ← reusable Gemini prompts (hero, carousel, portrait, ...)
├── templates/                ← carousel layouts, header layouts, social card bases
├── references/               ← private moodboard inspiration
├── presentations/            ← see "Presentations" sub-area below
│   ├── decks/                ← generated HTML decks
│   ├── briefs/               ← per-deck briefs
│   ├── templates/            ← base.html, components.md, components/
│   ├── scripts/              ← qa.py, serve.sh, export-pdf.sh, export_pdf.py
│   ├── docs/                 ← design-system.md, hosting.md, pdf-export.md
│   └── tokens.css            ← slide-specific CSS variables
└── mail-signatures/
    ├── README.md             ← scope + workflow
    ├── template.html         ← signature skeleton
    ├── members.yaml          ← team data (optional, single source for batch generation)
    └── generated/            ← per-member HTML + plain-text outputs
```

---

## Sub-area 1 — Visuals (AI or human)

### AI generation via `image-generation` skill

The skill wraps Gemini's image API. It:

1. Reads `../01-brand/style-guide.md` to extract palette, typography, illustration style, and banned visual tropes.
2. Auto-prefixes your prompt with those constraints.
3. Generates the image.
4. Saves to `./outputs/<date>-<slug>.png` with a sidecar `<date>-<slug>.json` recording the final prompt and parameters.
5. Flags visible breaches of the style guide.

Example invocation:

> Use the `image-generation` skill to create a 16:9 hero image for our landing page on "AI for small businesses". Subject: a visual metaphor of gradual transformation.

The skill auto-appends:
- Palette: {{BRAND_COLOR_PRIMARY}} / {{BRAND_COLOR_ACCENT}} / {{BRAND_COLOR_DARK}}
- Style: {{BRAND_ILLUSTRATION_STYLE}}
- Forbidden: {{BRAND_BANNED_VISUALS}}
- Requested format
- Consistency constraint with recently produced visuals

### Workflow

1. **Brief** at `./briefs/<date>-<slug>.md` with: intent, target placement (channel, page, event), persona, mood, copy overlay if any, aspect ratio, deadline, constraints (logo visible, big stat, etc.).
2. **Production**:
   - **AI**: invoke `image-generation`. Multiple variants returned; iterate.
   - **Human designer**: export brief + style guide link. Track in `./briefs/status.md`. Tag designer in {{EDITORIAL_CALENDAR_TOOL}}.
3. **Validation** — checklist for every visual:
   - Colors match primary / accent / neutral palette
   - Illustration style matches `{{BRAND_ILLUSTRATION_STYLE}}`
   - None of the banned tropes `{{BRAND_BANNED_VISUALS}}`
   - Text overlay uses primary font and legal weights
   - Logo placement respects safe zones
   - Contrast sufficient for legibility
   - Invoke `brand-check` on the metadata sidecar if in doubt.
4. **Distribution**:
   - Social media → `../03-social-media/<channel>/assets/`
   - Newsletter → upload in {{EMAIL_MARKETING_TOOL}}
   - Landing page → copy into the page's folder
   - Decks → reference inline from `./presentations/decks/<deck>.html`
   - Always archive the original in `./outputs/`

---

## Sub-area 2 — Presentations (HTML decks)

Editorial-grade decks live under `./presentations/`. Reference quality bar: *Monocle × Bloomberg viz × MIT Tech Review print*. Self-contained HTML (one file), exportable to clean 1920×1080 PDF, hostable on any static host.

### How decks are produced

Use the `slides` skill — it wraps the full procedure:

> Use the `slides` skill to draft a 20-slide pitch deck for our Q3 strategy review, audience = exec team, source = `_sources/transcriptions/2026-05-08-strategy-offsite.md`.

The skill enforces:

- 1920×1080 frame, 80×120 slide padding, 110px bottom safe zone
- Brand strict: only `tokens.css` custom properties, only declared font families
- One idea per slide, 3–4 breathing slides per 24
- Triple navigation (drag-bar, overview `O`, quick-jump digits + Enter) wired in `templates/base.html`
- Mandatory Playwright QA before delivery (`scripts/qa.py`)
- Brand-check gate (5-pass) before delivery

### Files of interest

- `presentations/templates/base.html` — deck skeleton (chrome, nav, print mode, QA hooks)
- `presentations/templates/components.md` — paste-ready slide layouts + selection guide
- `presentations/tokens.css` — slide-specific CSS variables, derived from `../01-brand/style-guide.md`
- `presentations/docs/design-system.md` — principles, anti-patterns, type scale
- `presentations/docs/pdf-export.md` — gradient-text rasterisation explained
- `presentations/docs/hosting.md` — Netlify Drop, S3, GitHub Pages, etc.

### Run a deck locally

```bash
cd 06-graphic-design/presentations
./scripts/serve.sh
# opens on http://localhost:5173/decks/
```

### Export to PDF

```bash
cd 06-graphic-design/presentations
./scripts/export-pdf.sh decks/<your-deck>.html
```

### QA

```bash
cd 06-graphic-design/presentations
python scripts/qa.py decks/<your-deck>.html
```

Must return `All slides clean` before delivery.

---

## Sub-area 3 — Mail signatures

Lightweight utility — see `./mail-signatures/README.md` for the full procedure.

Quick summary:

- Source data: `./mail-signatures/members.yaml` (or per-person briefing).
- Template: `./mail-signatures/template.html` with placeholders `{{NAME}}`, `{{ROLE}}`, `{{EMAIL}}`, `{{PHONE}}`, `{{LINKEDIN_URL}}`, plus brand tokens injected from `../01-brand/style-guide.md`.
- Output: `./mail-signatures/generated/<slug>.html` + `./mail-signatures/generated/<slug>.txt` plain-text fallback.
- Test on Gmail web + Apple Mail + Outlook Desktop before handing off.
- No brand-check gate (utility scope).

---

## Cross-area rules

- **Never** use generic stock photos (see `{{BRAND_BANNED_VISUALS}}`)
- Always check `../01-brand/assets/` before generating new visuals
- Always verify text legibility on background (contrast sensitive)
- Produce visuals at 2× resolution minimum for flexibility
- Sign AI outputs in metadata (`generated_by: gemini-3-pro-image-preview, date: ...`)

## AI disclosure

If the brand has a public AI disclosure policy (set during `/brand-discover`), follow it. Default: public-facing AI illustrations and AI-generated deck imagery → small caption or alt-text note. Internal / functional decorative assets → disclosure optional.

## Skills associated

- `image-generation` — brand-compliant AI visuals (primary for sub-area 1)
- `slides` — editorial HTML decks (primary for sub-area 2)
- `brand-check` — visual coherence validation when in doubt; **mandatory** before any deck delivery
- `frontend-design` / `ui-ux-pro-max` — for new slide components or when the brand has no strong visual identity yet

## What this role does NOT do

- ❌ Design the brand identity itself (→ `../01-brand/style-guide.md` exists before any visual)
- ❌ Write the long-form text that surrounds visuals (→ consumer roles provide copy)
- ❌ Publish the visuals or decks (→ consumer roles do that; decks ship via the channel that invited them)
