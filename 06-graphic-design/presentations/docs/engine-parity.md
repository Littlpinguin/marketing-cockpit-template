<!--
  VENDORED from slides-agent (https://github.com/Littlpinguin/slides-agent), docs/engine-parity.md,
  by scripts/sync-slides-engine.py. Do not edit here: change slides-agent,
  then run python3 scripts/sync-slides-engine.py. Mentions of CLAUDE.md,
  onboarding and the pexels-photos skill refer to slides-agent.
  Register: docs/vendored-slides.md
  Parity rule in this template: every engine change is made in slides-agent (the repository this page calls this repository), then synced here.
-->
# Engine parity: the canonical feature list of the slides engine

This page is the single reference for what "the full engine" means for any HTML deck built from this repository. It exists because a gap already happened once (a starter without fullscreen while the catalogue had it), and it must not happen again. Downstream copies of the engine, such as the marketing-cockpit template, vendor it from here: change the engine in this repository first, then sync them.

## The parity rule

> **Any engine change is ported to every artefact that carries the engine**: the starter (`06-graphic-design/presentations/templates/base.html`), the decks in flight in `06-graphic-design/presentations/decks/`, and, for the navigation features, the catalogue (`_examples/deck-catalogue/catalogue.html`). **This table is updated in the same commit**, and so is `ENGINE_MARKERS` in `06-graphic-design/presentations/scripts/qa.py`.

A deck does not choose its engine features: it carries all of them. The content varies, the engine does not. `06-graphic-design/presentations/scripts/qa.py` checks the engine markers mechanically and fails a deck, or the starter, that lost one; `scripts/tests/test_slides_qa.py` fails if the starter misses a marker, and `scripts/tests/test_slides_engine.py` drives the behaviours in headless Chromium.

## The canonical features

| # | Feature | Detail | `06-graphic-design/presentations/scripts/qa.py` marker |
|---|---|---|---|
| 1 | **1920×1080 frame scaled to the viewport** | `fit()`: `translate(-50%, calc(-50% + yShift)) scale(s)`, a nav reserve in windowed mode, a 1.5× cap | `stage-frame` |
| 2 | **Chrome rows and auto-numbered folios** | `NN / TOTAL` is injected into every `.nav-num` from `SLIDE_COUNT` (the number of slides). Folios are never hard-coded: inserting or removing a slide needs no renumbering | `auto-folios` (`SLIDE_COUNT`, or the older `querySelector('.nav-num')` loop) |
| 3 | **Triple navigation** | Keyboard (←, →, Space, Page Up / Down, Home, End), wheel debounced 700 ms, touch swipe, drag bar, quick-jump (digits + Enter) | structural |
| 4 | **Overview grouped by family** | `O` key or ⊞ button. Thumbnails grouped by `data-family`, with the catalogue's keys (`ouverture`, `editorial`, `dataviz`, `schema`, `tableau`, `preuve`, `conclusion`, `photo`); a deck without any `data-family` gets one flat grid. A click on the backdrop closes the panel, and while it is open only `O` and `Escape` act | `overview` |
| 5 | **Fullscreen presentation mode** | `F` key or ⛶ button (Fullscreen API with a `webkit` fallback): `body.presenting` hides the nav, `fit()` runs without reserve or cap | `body.presenting`, `requestFullscreen` |
| 6 | **nav-peek** | In presentation mode the nav comes back when the pointer is within 90 px of the bottom edge | `nav-peek` |
| 7 | **PDF export** | `P` key or button: `body.printing-pdf`, per-character canvas rasterisation of gradient text (`GRADIENT_TEXT_SELECTORS`), `window.print()`, restore on `afterprint`. The button shows an exporting state and the overview closes first. Print CSS: one slide per 1920×1080 page, every slide on its own background | `printing-pdf`, `window.print`, `GRADIENT_TEXT_SELECTORS` |
| 8 | **Headless hooks** | `window.__enablePrintMode`, `__disablePrintMode`, `__rasterizeGradients`, `__restoreRaster`, `__go`, `__total`, `__toggleFullscreen`, used by `06-graphic-design/presentations/scripts/export_pdf.py` and `qa.py --with-pdf` | `__enablePrintMode`, `__rasterizeGradients` |
| 9 | **Brand-pattern hooks** | `--brand-pattern`, `--brand-pattern-light`, `--corner-motif` and their opacities in `:root`, drawn by `.texture`, `.motif`, `.corner`, `.filet-orn`. Inert (`none`) until the brand provides a motif | `brand-pattern` (`--brand-pattern`) |
| 10 | **Ambient aurora (optional)** | `.aurora` with two blurred brand-colour discs, rhythm slides only, under the content at `z-index: -1`, exempt from QA, hidden in the PDF | structural |
| 11 | **Descender-safe titles** | `line-height` ≥ 1.1 on text titles; `.gradient-text` carries `padding: 0.22em 0.08em; margin: -0.22em -0.08em; overflow: visible`, never reduced | visual review (QA lists gradient text apart) |
| 12 | **Label-register tokens** | `--chrome-opacity`, `--chrome-opacity-dark`, `--label-accent`, `--label-accent-dark` keep chrome and eyebrows at WCAG 4.5:1 | the QA contrast check |
| 13 | **Brand tokens with their setup mapping** | Neutral working values in `:root`, each brand variable commented with the `BRAND_*` placeholder it maps to; derived values carry their `color-mix()` formula. A wizard replaces values, never writes a `{{...}}` into a CSS value | structural |

## Mechanical check

```bash
python3 06-graphic-design/presentations/scripts/qa.py 06-graphic-design/presentations/decks/<deck>.html          # engine parity, then the rest of the gate
python3 06-graphic-design/presentations/scripts/qa.py 06-graphic-design/presentations/templates/base.html --with-pdf     # the starter, PDF included
```

`ENGINE_MARKERS` in `06-graphic-design/presentations/scripts/qa.py` is the executable mirror of the table above. A deck missing a marker fails with the list of lost features; port them from `06-graphic-design/presentations/templates/base.html`, never rewrite them.

**The catalogue** carries the navigation engine (grouped overview, fullscreen, nav-peek, PDF button with its own rasteriser, `SLIDE_COUNT` folios, brand-pattern hooks) but not the headless hooks: it is a specimen book, so it runs with `--no-engine-check`.

## Adding a feature to the engine

1. Port it into `06-graphic-design/presentations/templates/base.html` and into the decks in flight (and into the catalogue when it is a navigation feature).
2. Add its row to the table above.
3. Add its marker to `ENGINE_MARKERS` in `06-graphic-design/presentations/scripts/qa.py`: `scripts/tests/test_slides_qa.py` then requires it in the starter. Add a behaviour test to `scripts/tests/test_slides_engine.py` when the feature reacts to input.
4. Re-run `06-graphic-design/presentations/scripts/qa.py` on the starter (`--with-pdf`) and on the catalogue, then `python3 -m pytest scripts/tests -q`.

A legacy deck that predates a feature can pass with `--no-engine-check` for a while, but only while its upgrade is planned: the flag is not a permanent regime.
