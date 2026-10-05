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
├── scripts/                  ← visual QA, carousel builder, compose capture, provenance, asset promotion, new-deck.py
├── lib/                      ← compose.css (local brand font + tokens for HTML compositions), README
├── presentations/            ← see "Presentations" sub-area below (engine vendored from slides-agent)
│   ├── decks/                ← generated HTML decks
│   ├── briefs/               ← per-deck briefs
│   ├── assets/photos/        ← deck-local photos (optional Pexels downloads), created on demand
│   ├── templates/            ← base.html (starter), components.md, components/          [vendored]
│   ├── scripts/              ← qa.py, serve.sh, export-pdf.sh, export_pdf.py, shots.py, pexels.py [vendored]
│   ├── docs/                 ← design-system.md, engine-parity.md, pdf-export.md, pexels-setup.md [vendored], hosting.md
│   └── tokens.css            ← the engine's brand file, generated from ../01-brand/tokens.json
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

### Outillage des visuels (scripts versionnés)

Tout se mesure et se fabrique avec les scripts de `./scripts/`, jamais avec un script jetable. Aucun ne porte de valeur de marque : couleurs, polices et règles du logo se lisent dans `../01-brand/tokens.json`, les assets dans `../01-brand/assets/`.

| Geste | Commande | Ce qu'il fait |
|---|---|---|
| QA d'un carrousel, d'une composition ou d'une image | `python3 06-graphic-design/scripts/qa-visuel.py <fichier.html\|png>` | Couleurs contre la palette (ΔE76, portées), police, plancher (28 px en portrait, 18 px sinon, chrome 22 px), contraste WCAG, zone de protection du logo. Sortie `--format json`, code 1 en cas d'erreur : utilisable en gate |
| Construire un carrousel | `python3 06-graphic-design/scripts/build-carousel.py <slug>` | Spec `outputs/carrousel-<slug>-<date>/carrousel.json` → `index.html` → `exports/<slug>.pdf` (via `export-carousel-pdf.py`, dégradés rastérisés). `--sans-pdf` pour la QA avant export, `--dry-run` pour lister |
| Capturer une composition HTML | `06-graphic-design/scripts/compose-screenshot.sh <compo.html> <sortie.png> [L] [H]` | Chrome headless, rendu 2× puis redimensionné. La composition linke `lib/compose.css` (police locale + tokens), voir `lib/README.md` |
| Tracer la provenance d'une image générée | `genmeta.finalize_output()` (module `scripts/genmeta.py`) | Extension réelle, tag PNG `ai:generated_by`, fiche `<image>.gen.json` (modèle, prompt, réglages, sha256) |
| Promouvoir un asset validé | `python3 06-graphic-design/scripts/promote-asset.py <source> --dest … --droits … --auteur …` | Rangement au nom conforme dans `../01-brand/assets/`, fiche dans `index.md`, champs de droits obligatoires, fiche de génération reportée |
| Créer un deck aux couleurs de la marque | `python3 06-graphic-design/scripts/new-deck.py <slug> [--titre "…"]` | Copie le starter vendorisé dans `presentations/decks/<slug>.html` et remplace son `:root` neutre par celui de `presentations/tokens.css` ; signale les polices de marque que le `<link>` du starter ne charge pas |

Cycle de vie d'un visuel généré : **staging** (`outputs/`, avec sa fiche `.gen.json`) → **validé** par un humain → **promu** par `promote-asset.py`. Un visuel non promu n'est jamais référencé comme officiel. Les decks gardent leur propre QA (`presentations/scripts/qa.py`, vendorisée depuis slides-agent, ci-dessous) ; `scripts/qa_common.py` porte les calculs de `qa-visuel.py`. Tests de l'outillage : `python3 -m pytest scripts/tests -q` à la racine du dépôt (les tests qui pilotent Chromium sont sautés proprement si Playwright ou le navigateur manquent).

---

## Sub-area 2 — Presentations (HTML decks)

Editorial-grade decks live under `./presentations/`. Reference quality bar: *Monocle × Bloomberg viz × MIT Tech Review print*. Self-contained HTML (one file), exportable to clean 1920×1080 PDF, hostable on any static host.

### The engine is vendored from slides-agent

The slides engine (starter, components, layout catalogue, QA, PDF export and their tests) has one source of truth: [slides-agent](https://github.com/Littlpinguin/slides-agent). Its files carry a `VENDORED from slides-agent` header and are written by `python3 scripts/sync-slides-engine.py` only. **Never edit them by hand**: change slides-agent, then re-sync (`--check` exits 1 on any drift). Mapping, mechanical adaptations and resync procedure: `../docs/vendored-slides.md`. What stays template-owned: `presentations/tokens.css`, `presentations/docs/hosting.md`, `scripts/new-deck.py` and the catalogue's `README.md`.

### How decks are produced

Use the `slides` skill — it wraps the full procedure:

> Use the `slides` skill to draft a 20-slide pitch deck for our Q3 strategy review, audience = exec team, source = `_sources/transcriptions/2026-05-08-strategy-offsite.md`.

The skill enforces:

- 1920×1080 frame, 80×120 slide padding, 110px bottom safe zone
- Brand strict: only `tokens.css` custom properties, only declared font families
- One idea per slide, 3–4 breathing slides per 24; layouts picked by beat from the 120-layout library, no layout twice in a row
- The full presentation engine wired in `templates/base.html` (canonical feature list: `presentations/docs/engine-parity.md`): triple navigation (drag-bar, overview `O` grouped by family, quick-jump digits + Enter), fullscreen mode `F` with nav-peek, auto-numbered folios (`SLIDE_COUNT`), PDF export `P` with per-character rasterisation of gradient text, brand-pattern hooks, optional ambient aurora
- Mandatory Playwright QA before delivery (`presentations/scripts/qa.py`)
- Brand-check gate (5-pass) before delivery

### Brand: how a deck gets it

`01-brand/tokens.json` → `python3 scripts/build-tokens.py` → the brand block of `presentations/tokens.css`, with slides-agent's variable names (`--brand-primary`, `--brand-secondary`, `--brand-neutral-light` / `-dark` and their `-deep` / `-soft` shades, `--rule`, `--brand-gradient`, `--font-display`, `--font-mono`, `--label-accent` / `-dark`, computed to reach WCAG 4.5:1). The starter keeps its neutral example `:root`; `python3 06-graphic-design/scripts/new-deck.py <slug>` copies it into `presentations/decks/` with the `:root` of `tokens.css` instead. Before the wizard, `tokens.css` carries the same neutral example palette as the starter.

### Files of interest

- `presentations/templates/base.html` — the starter: chrome, navigation, print mode, headless hooks, three example slides
- `presentations/templates/components.md` — paste-ready slide components with their known traps
- `../_examples/deck-catalogue/LAYOUTS.md` — index of the 120 layouts in 8 families, by "reach for it when"; `../_examples/deck-catalogue/catalogue.html` executes them all (press `O`)
- `presentations/tokens.css` — the engine's brand file; its brand block is generated from `../01-brand/tokens.json` by `python3 scripts/build-tokens.py` (never edit it by hand)
- `presentations/docs/design-system.md` — principles, anti-patterns, type scale
- `presentations/docs/engine-parity.md` — canonical engine feature list + parity rule (enforced by `presentations/scripts/qa.py`)
- `presentations/docs/pdf-export.md` — gradient-text rasterisation explained
- `presentations/docs/pexels-setup.md` — optional real photography (free `PEXELS_API_KEY` in `.env`)
- `presentations/docs/hosting.md` — Netlify Drop, S3, GitHub Pages, etc.

### Commands (from the repository root)

```bash
python3 06-graphic-design/scripts/new-deck.py <slug> --titre "Deck title"   # new deck, brand :root
./06-graphic-design/presentations/scripts/serve.sh                         # http://localhost:5173/06-graphic-design/presentations/decks/
python3 06-graphic-design/presentations/scripts/qa.py 06-graphic-design/presentations/decks/<deck>.html
python3 06-graphic-design/presentations/scripts/qa.py 06-graphic-design/presentations/decks/<deck>.html --with-pdf
./06-graphic-design/presentations/scripts/export-pdf.sh 06-graphic-design/presentations/decks/<deck>.html
python3 06-graphic-design/presentations/scripts/shots.py 06-graphic-design/presentations/decks/<deck>.html 3 8   # control screenshots
```

### QA

Must return `All slides clean` before delivery (exit 0; warnings are listed, read them). Au-delà du débordement et de la zone de sécurité du chrome, le script contrôle la parité du moteur (`presentations/docs/engine-parity.md`), les planchers typographiques (18 px pour le contenu, 12 px pour le registre des étiquettes : chrome, surtitres, folios, mono ; avertissement `tight-body` sous 24 px), la police (familles `font.*` de `../01-brand/tokens.json`, sinon les variables du deck), le contraste WCAG AA opacité comprise et les folios. Options utiles : `--format json` (agent `qa-visuel`), `--with-pdf`, `--lang <code>`, `--wait <ms>`, `--bleed <sélecteur>`, `--font <famille>`, `--no-folio`, `--no-engine-check` (catalogue seulement), `--screenshots [dossier]`. Ne jamais contourner un constat (`data-bleed` sur du texte, seuil abaissé) : corriger la slide.

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

Follow `01-brand/divulgation-ia.md`, the single reference (what gets disclosed, the wording per channel, the `généré-par-ia:` field of the asset catalogue). Before publishing a third-party logo or a photo of a person, check its status in `01-brand/droits.md`.

## Skills associated

- `image-generation` — brand-compliant AI visuals (primary for sub-area 1)
- `slides` — editorial HTML decks (primary for sub-area 2)
- `carousel` — LinkedIn carousels (spec + `scripts/build-carousel.py`, or hand-written HTML)
- agent `qa-visuel` — measured QA of decks, carousels and visuals with the scripts above, before export
- agent `brand-guardian` — adversarial brand review of a major deliverable, complements `brand-check`
- `brand-check` — visual coherence validation when in doubt; **mandatory** before any deck delivery
- `frontend-design` / `ui-ux-pro-max` — for new slide components or when the brand has no strong visual identity yet

## What this role does NOT do

- ❌ Design the brand identity itself (→ `../01-brand/style-guide.md` exists before any visual)
- ❌ Write the long-form text that surrounds visuals (→ consumer roles provide copy)
- ❌ Publish the visuals or decks (→ consumer roles do that; decks ship via the channel that invited them)
