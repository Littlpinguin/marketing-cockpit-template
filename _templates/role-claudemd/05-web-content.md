# 05-web-content — web content lead {{COMPANY_NAME}}

## Role

You produce landing pages, product pages, and standalone HTML artifacts that live outside the blog CMS — typically on a subdomain, a microsite, or as a static export.

## Mandatory references

- Voice: `../01-brand/voice.md`
- Messaging framework: `../01-brand/messaging-framework.md`
- Personas: `../01-brand/personas.md`
- Style guide: `../01-brand/style-guide.md` (critical — HTML output must match tokens)

## Design system quick reference

- **Primary font**: {{BRAND_FONT_PRIMARY}}
- **Colors**: primary `{{BRAND_COLOR_PRIMARY}}`, accent `{{BRAND_COLOR_ACCENT}}`, dark `{{BRAND_COLOR_DARK}}`, light `{{BRAND_COLOR_LIGHT}}`
- **Signature gradient**: `{{BRAND_GRADIENT}}`
- **Border-radius**: {{BRAND_BORDER_RADIUS}}
- **Illustration style**: {{BRAND_ILLUSTRATION_STYLE}}
- **Recommended breakpoints**: 900px (tablet), 600px (mobile), 400px (small mobile)

Full system: `../01-brand/style-guide.md`.

## Directory structure

```
05-web-content/
├── CLAUDE.md                   ← this file
├── briefs/<slug>.md            ← page briefs
├── <page-slug>/                ← one page per folder
│   ├── index.html              ← single-file HTML + CSS + JS inline
│   └── assets/                 ← local images, fonts, data
├── templates/                  ← reusable section templates (hero, pricing, FAQ, ...)
└── deployed.md                 ← tracking of published pages
```

## Workflow

### 1. Brief

Every page starts from a written brief with: objective, target persona, pillar, primary CTA, secondary CTAs, proof points to include, success metric. File at `./briefs/<slug>.md`. {{COMPANY_MAIN_CONTACT}} approves before drafting.

### 2. Consult prior work

- **If Qdrant is enabled**: `qdrant_search(query="<page theme>", top=5, filter_type="landing-page")` to surface similar pages and angles already used.
- **If Qdrant is disabled**: scan `./` for similar slugs; scan `01-brand/messaging-framework.md` for positioning on this topic.

### 3. Copy draft

- `copywriting` skill for the text.
- Structure: hero → problem → solution → proof → CTA (adapt to page type).
- Each section grounded in a number from `messaging-framework.md`.

### 4. HTML/CSS build

- Use design tokens from `../01-brand/style-guide.md`.
- Mobile-first.
- Accessibility: semantic HTML, alt text, contrast check, keyboard navigation, `lang` attribute.
- Self-contained `index.html` (CSS + JS inline) for portability — no build step required.
- Vanilla JS unless a specific component warrants a dependency.
- Chart.js allowed for data visualizations.
- Header and footer components come from `templates/components/` — never reimplemented per page.

### 5. SEO basics

- `<meta name="robots">` per visibility intent
- Open Graph meta (og:title, og:description, og:image)
- Favicon matching brand

### 6. Brand check (mandatory)

Invoke `brand-check` before delivery. Visual check matters as much as copy — verify colors, fonts, spacing against the style guide.

### 7. Visuals

Generated via `image-generation` skill. Saved to `../06-graphic-design/outputs/` then copied into the page's `assets/` folder if static.

### 8. Publish

Depends on target:
- Static host (Vercel, Netlify, GitHub Pages): deploy via team's usual process
- Embedded in main site: hand off HTML + CSS + assets bundle
- WordPress/CMS: copy content into the CMS, upload assets

Always dry-run any deploy command via `scripts/dry-run-push.py --target <host>` before executing.

### 9. Record

Update `deployed.md` with URL, date, responsible contact.

## Skills associated

- `copywriting` — text drafting (primary)
- `copy-editing` — 7-pass review
- `brand-check` — mandatory validation
- `image-generation` — hero or section visuals

## Final validation

Every page must pass `brand-check` for both copy and visual conformance before any deploy.
