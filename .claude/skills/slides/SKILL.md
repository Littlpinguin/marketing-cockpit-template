---
name: slides
description: Generate brand-aligned standalone HTML presentations for {{COMPANY_NAME}}. Editorial-grade output (Monocle / Bloomberg viz / MIT Tech Review print quality bar), strict adherence to 01-brand/ as single source of truth, 1920×1080 frame scaled responsively, triple navigation (drag bar + overview + quick-jump), Playwright QA mandatory before delivery, clean PDF export via canvas-rasterised gradient text. Use whenever the user asks for a presentation, deck, slides, pitch, kickoff, sales deck, investor deck, internal readout or webinar slide deck. Not for static infographics or social images — those go through `image-generation`.
---

# slides — editorial HTML decks for {{COMPANY_NAME}}

You generate self-contained `.html` presentations that are projected live, exported to PDF, or hosted on a static URL. The reference quality bar is *Monocle × Bloomberg viz × MIT Tech Review print* — restraint, hairlines, generous whitespace, one idea per slide. Avoid "AI startup 2025" tropes (bento grids, glassy orbs, four nested radial gradients, fake-bold copy).

## Where the work happens

All slide-related files live under `06-graphic-design/presentations/`:

```
06-graphic-design/presentations/
├── decks/                  ← generated decks (one .html per deck)
├── briefs/                 ← per-deck briefs (intent, audience, decisions, sources)
├── templates/
│   ├── base.html           ← deck skeleton (chrome, nav, print mode, QA hooks)
│   ├── components.md       ← component catalogue + selection guide
│   └── components/         ← paste-ready slide layouts
├── scripts/
│   ├── qa.py               ← Playwright overflow check (mandatory)
│   ├── serve.sh            ← local static server on :5173
│   ├── export-pdf.sh       ← clean 1920×1080 PDF export
│   └── export_pdf.py       ← headless Chromium worker
├── docs/
│   ├── design-system.md    ← principles, anti-patterns, type scale
│   ├── pdf-export.md       ← gradient-text rasterisation explained
│   └── hosting.md          ← Netlify Drop, S3, GitHub Pages, etc.
└── tokens.css              ← slide-specific CSS variables, derived from 01-brand/
```

## When to invoke this skill

- "Make me a deck for [audience] about [topic]"
- "Build a presentation to pitch [project] to [stakeholders]"
- "Turn this brief / transcript / strategy doc into slides"
- "Refresh the [previous deck] in the same style"
- Anything where the deliverable is a projected or shared deck

For a static infographic, social post, or banner, use `image-generation` instead.

## Prerequisites — confirm before starting

1. **Brand setup is complete.** `.setup-completed` exists at the project root. `01-brand/style-guide.md`, `01-brand/voice.md` and `06-graphic-design/presentations/tokens.css` no longer contain `{{...}}` placeholders. If anything still has placeholders, run `/start-copilot` first.
2. **Source material is clear.** Either the user has provided a brief / transcript / memo, OR you have completed the `superpowers:brainstorming` skill flow with them. Never start writing HTML on a vague verbal brief.
3. **The slide map is approved.** Draft a numbered list of slides (eyebrow + headline per slide, 18–24 total) and get explicit user sign-off before generating HTML. This is the single highest-leverage moment to course-correct.

## Procedure (8 phases)

### Phase 1 — Preparation

1. Read all source material thoroughly: brief in `06-graphic-design/presentations/briefs/`, related transcripts in `_sources/transcriptions/`, any cited reports in `_sources/reports/`.
2. Identify audience, decision being made, presentation format (live projected vs autonomous read).
3. Choose a Duarte-style emotional sparkline: pain ↔ hope alternation. Map each beat to a slide intent.
4. Cut to 18–24 slides total, "one idea = one slide". Insert 3–4 "breathing" slides (single big number + one short phrase) between dense ones.

### Phase 2 — Art direction

5. Pick a visual through-line metaphor that aligns with the brand and the deck topic. The metaphor is a recurring motif (an animation, a visual marker, an ambient watermark) that anchors the narrative.
6. Confirm typographic system from `06-graphic-design/presentations/tokens.css`: contrast pair (e.g. weight 200 vs 700/900), display vs body sizes, mono captions. **If `01-brand/style-guide.md` is sparse**, invoke the `ui-ux-pro-max` skill to pick a coherent style + colour system + font pairing aligned with the brand's positioning before going further.
7. Lock the grid: 1920×1080 frame, chrome inset 36×60, slide padding 80×120.
8. Animation principles: slow easing (1.1s `cubic-bezier(0.16, 1, 0.3, 1)`), 0.12s stagger, no bouncy springs, no fast cuts.

### Phase 3 — Components

9. Decide which patterns from `templates/components.md` you'll reuse. Build any new component in isolation first, test at 1920×1080, then weave in. **When a slide beat doesn't fit any documented component**, invoke `frontend-design` to design a new pattern. For richer references (hero treatments, complex layouts, navigation chrome details), use the 21st.dev MCP tools (`mcp__magic__21st_magic_component_builder` / `inspiration` / `refiner`). Treat their output as inspiration: rework geometry to the 1920×1080 frame, respect the chrome safe-zone, and re-apply tokens from `tokens.css` — never paste a generated component verbatim.
10. Test the very first component via Playwright before adding any others — catches scale/typography bugs early.

### Phase 4 — Assets

11. **Brand logo**: embed inline as `<symbol id="brand-logo">` from `01-brand/assets/`. Always `fill="currentColor"` on inner paths — `<use>`'s shadow DOM does NOT receive `fill: url(#gradient)`.
12. **Brand illustrations / photos**: pull from `01-brand/assets/` or `06-graphic-design/outputs/` (visuals previously produced by `image-generation`). Embed SVGs inline; reference rasters with relative paths.
13. **Third-party tool logos** (when needed): try in order — (a) `cdn.simpleicons.org/<slug>/<color>`, (b) `api.iconify.design/logos/<slug>.svg` or `api.iconify.design/simple-icons/<slug>.svg?color=<hex>`, (c) `WebFetch` the official site and extract inline SVG, (d) `google.com/s2/favicons?domain=<domain>&sz=256` PNG fallback.

#### Verified third-party logo sources

✅ Available on `https://cdn.simpleicons.org/<slug>/<hex-no-hash>`:
`anthropic`, `n8n`, `spotify`, `youtube`, `applepodcasts`, `deezer`, `discord`, `claude`, and most major tech brands. Pass the colour as a hex without `#` (e.g. `292E35`).

⚠ Often missing on simpleicons (404), use these alternates:

| Brand | Source |
|---|---|
| Descript | `https://api.iconify.design/logos/descript.svg` |
| MailerLite | Extract inline SVG from `https://www.mailerlite.com/` header HTML |
| Vizard | `https://vizard.ai/img/vizard_new_logo_purple.<hash>.svg` (find current hash via WebFetch) |
| Ausha | `https://www.google.com/s2/favicons?domain=ausha.co&sz=256` (PNG, ~192×192) |
| LinkedIn | `https://api.iconify.design/simple-icons/linkedin.svg?color=<hex>` |

Save fetched logos under `01-brand/assets/<slug>.<ext>` and reference relatively from the deck. Re-verify URLs on each new project — they drift.

### Phase 5 — Content

14. Write copy that respects the voice rules in `01-brand/voice.md`. The banned-vocabulary list is non-negotiable.
15. Punctuation: never use the em-dash (`—`) in visible content. Use en-dash (`–`), comma, or restructure.
16. Every claim is backed by a number, a date, or an explicit source. Cross-check stats against `01-brand/messaging-framework.md` — never publish a number that isn't in there or in `_sources/reports/`.

### Phase 6 — Navigation

17. Triple navigation is already wired in `templates/base.html`: drag-bar, overview panel (`O` / `Esc`), quick-jump (digits + Enter). Plus the classics: ←/→/Space/Page↑↓/Home/End, mouse wheel debounced 700ms, touch swipe. **Do not remove or reimplement.**
18. Frame centering: `transform: translate(-50%, calc(-50% + ${yShift}px)) scale(${scale})` with `yShift = -(24 + nav.offsetHeight)/2`. CSS `place-items: center` does NOT work with `transform: scale()` — the layout box stays 1920×1080.

### Phase 7 — Playwright QA (non-negotiable)

19. Run `python scripts/qa.py decks/<your-deck>.html` from `06-graphic-design/presentations/`. It must return `All slides clean`. The script verifies:
    - No element overflows the 1920×1080 frame.
    - Bottom-content vs bottom-chrome gap ≥ 16px on every slide.
20. Re-test at 1366×768 and 1024×600 to confirm responsive scaling. Visually inspect each screenshot in `/tmp/`.

### Phase 8 — Brand-check + delivery

21. **Brand-check is mandatory** for every deck before delivery (5-pass: vocabulary / tone / proof / audience / visual). Decks fall under the same gate as social, email, and web content. The PostToolUse hook fires the reminder; do not bypass it.
22. Keep `v1` intact during iteration. If the user revises, save as `v2`. Once approved, optionally remove `v1`.
23. Confirm the user has previewed the deck (`./scripts/serve.sh`, then open `http://localhost:5173/decks/<your-deck>.html`) before claiming done.

## Typography traps (already-resolved patterns)

| Symptom | Cause | Fix |
|---|---|---|
| `%` or `O` clipped on huge display text | `line-height < 1` plus aggressive negative letter-spacing | `line-height: 1.05–1.15`, `letter-spacing: -0.025em` max, `padding: 0.08em 0.06em; margin: -0.08em -0.06em; overflow: visible` |
| Gradient text renders differently after `transform: scale()` | `-webkit-background-clip: text` plus sub-pixel rendering | `display: inline-block; transform: translateZ(0); -webkit-font-smoothing: antialiased; text-rendering: geometricPrecision` |
| Coloured halos around gradient text in PDF/print | `background-clip: text` plus `display: inline-block` clip incorrectly in print | In `@media print`, replace gradient with solid `var(--brand-primary-deep)` or `var(--brand-secondary-deep)` |
| Number + unit wrapping to two lines | `display: block` or grid column too narrow | `display: inline-flex; align-items: baseline; white-space: nowrap`, widen the column |
| Logo invisible after embedding | `fill: url(#grad)` does not traverse `<use>` shadow DOM | `fill="currentColor"` inside `<symbol>`, set `color:` on the wrapper |
| Element overflowing the bottom chrome row | Content component too tall, padding-bottom too short | Audit via Playwright, reduce font-sizes / paddings / gaps; never shrink slide padding-bottom below 110px |

## CRITICAL — bottom chrome safe zone

The bottom chrome (`.chrome-row.bottom` containing the brand mark + signature) sits at `inset: 36px` from the frame. Its content occupies y ≈ 1014 → 1044 in the native 1920×1080 frame.

**Hard rule**: no content element may extend below y=1000. The QA script verifies `chrome_row.top - lowest_content_bottom ≥ 16px` on every slide.

**Slides typically at risk**: anything with a section-head + dense grid + footer-bar combo (pipelines, stack grids, funnels, budgets, roadmaps).

**Fix when overlap is detected**:

1. Shrink display element font-sizes (numbers, totals).
2. Shrink grid paddings/gaps.
3. Shrink `margin-top` of section-head / intermediate components.
4. If the content is conceptually too dense → split into two slides. "One idea = one slide" is the discipline that keeps the layout calm.

## CRITICAL — PDF export uses canvas rasterisation for gradient text

Chromium has a documented bug in its PDF pipeline with `background-clip: text` + `linear-gradient`: coloured artefact lines appear at the edges of multi-line inline-blocks. **No CSS combination fixes it** (tested: `box-decoration-break: clone`, `display: inline`, `isolation: isolate`, padding/margin resets — all fail).

The solution wired into `templates/base.html`: before `window.print()`, walk every gradient-text selector, render each into a `<canvas>` with the same gradient, replace the DOM with `<img>` PNGs, then restore on `afterprint`.

Selectors to keep up-to-date in the rasteriser (in `templates/base.html`, `GRADIENT_TEXT_SELECTORS` constant):

```js
const GRADIENT_TEXT_SELECTORS = [
  '.gradient-text',
  '.silence-num.gradient',
  '.hero-num',
  '.bigquote em',
  '.decision-q .go',
  '.decision-q .nogo',
  // add any new selector that uses background-clip: text
];
```

If you add a new component that uses gradient text, **append its selector to that list**, otherwise the PDF will show artefacts on that element.

Other print rules already wired:

- `*`: `-webkit-print-color-adjust: exact` (forces gradients / backgrounds)
- `.stage-frame`: `transform: none` in print mode (cancels scaling)
- `.slide`: `page-break-before: always` from slide 2 onwards (avoids a blank trailing page)
- `.reveal`: `opacity: 1; transform: none` (skip reveal animations)
- aurora / dust-grid: `display: none` in print (filter-blur and 1px linear-gradients render unreliably)
- `*`: `box-shadow: none; text-shadow: none` (banding / halos in print)

See `06-graphic-design/presentations/docs/pdf-export.md` for full detail.

## Brand-strict rules (enforce always)

- Use **only** custom properties from `06-graphic-design/presentations/tokens.css`. No hardcoded hex anywhere in the deck.
- Use **only** the font families declared in `tokens.css` (which mirror `01-brand/style-guide.md`). No third family snuck in.
- Logo lives in the bottom-right chrome on every slide via `<use href="#brand-logo">`.
- Border-radius is 4–50px or pill — never 0 (unless the brand explicitly requires it).
- Alternate light vs dark slide backgrounds for rhythm. A 24-slide deck shouldn't be 24 cream slides in a row.
- Numbers as heroes: huge display, gradient or solid; secondary text small. Restraint everywhere.
- Forbidden: bento grids, gratuitous glassmorphism, stock photography, fake-bold marketing copy, anything in `{{BRAND_BANNED_VISUALS}}`.

## Editorial rules

- 5-point brand-check before delivery: vocabulary / tone / proof / audience / visual.
- No em-dash (`—`) in visible content.
- Banned vocabulary lives in `01-brand/voice.md`. Re-read before writing copy.
- Every assertion is anchored to a number, date, or named source.

## Delivery modes

The user has three delivery modes. Default to (A) — never push a heavy stack on them.

**A. Local presentation**

```
cd 06-graphic-design/presentations
./scripts/serve.sh
```

Starts a static server on `http://localhost:5173`. Open the deck, press `→` to advance, `O` for overview, `P` to print to PDF.

**B. PDF export**

```
cd 06-graphic-design/presentations
./scripts/export-pdf.sh decks/<your-deck>.html
```

Renders the deck to a clean 1920×1080 PDF (one slide per page) using Chromium headless. See `docs/pdf-export.md` for the gradient-text rasterisation detail.

**C. Online sharing**

The deck is a single HTML file with all assets either inlined or referenced via relative paths. Drop the project folder (or just `decks/` plus `01-brand/assets/`) onto any static host. See `docs/hosting.md` for Netlify Drop, GitHub Pages, S3, and other targets.

## Final deliverable

A single file: `06-graphic-design/presentations/decks/<topic>-<date>-<version>.html`, alongside any third-party logo files referenced via relative path. Self-contained (opens in Chrome with no server needed), shareable as-is via `./scripts/serve.sh`, exportable to PDF via `./scripts/export-pdf.sh`, hostable on any static host (see `docs/hosting.md`).

## Brand-specific customizations

{{SLIDES_SPECIFIC_RULES}}

## Associated skills

- `brand-check` — mandatory 5-pass before delivery
- `image-generation` — when the deck needs a hero image, atmospheric photo, or illustrated metaphor not already in `01-brand/assets/`
- `frontend-design` / `ui-ux-pro-max` — when a slide beat needs a new component or the brand has no strong visual identity yet
- `superpowers:brainstorming` — entry point when the user starts from a blank page (Path B)
