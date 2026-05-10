# PDF export

## TL;DR

```bash
# From 06-graphic-design/presentations/
./scripts/export-pdf.sh decks/your-deck.html
# → writes decks/your-deck.pdf
```

Or, from inside the deck in Chrome: press `P` (or click the PDF button in the nav rail) and pick "Save as PDF" in the print dialog.

## Why it's not just `Cmd+P`

Chromium has a documented bug in its PDF rendering pipeline: text styled with `background-clip: text` + a `linear-gradient` fill produces **coloured fringe artefacts** at the edges of multi-line inline-blocks. The bug appears with or without scaling, with or without `box-decoration-break: clone`, with or without `display: inline`. **No CSS combination resolves it** — confirmed by minimal-page tests.

The fix wired into `templates/base.html`:

1. Listen for `Cmd+P` / the PDF button.
2. Toggle `body.printing-pdf`, which the `@media print` block uses to disable scale, animations, blurs, and shadows.
3. Walk every selector in `GRADIENT_TEXT_SELECTORS` and rasterise its text to a `<canvas>` (which doesn't have the bug), then replace the DOM with `<img>` PNG tags.
4. Call `window.print()`.
5. On the `afterprint` event, restore the original DOM and remove the class.

The user sees a one-frame flicker at most. The PDF is artefact-free.

## Headless export script

`scripts/export_pdf.py` does the same thing without the user pressing any key — useful for CI, batch exports, or generating archive copies:

```bash
python3 scripts/export_pdf.py decks/your-deck.html out/your-deck.pdf
```

It launches headless Chromium, calls the `window.__enablePrintMode()` and `window.__rasterizeGradients()` hooks the deck exposes, then `page.pdf()`.

## Page count

If you have 24 slides and the PDF has 25 pages, the last page is blank. Cause: a `page-break-after: always` somewhere instead of `page-break-before: always`. The base template uses the right rule (`page-break-before` from slide 2 onwards, `avoid` on the first), so this only happens if you've added a custom slide that overrides it.

## Other PDF traps and how the template handles them

| Symptom | Cause | What the template does |
|---|---|---|
| Animated SVG paths invisible | `stroke-dashoffset` stuck mid-animation | `body.printing-pdf .pipeline-anim { stroke-dashoffset: 0 !important; animation: none !important; }` |
| Roadmap dots invisible | `transform: scale(0)` initial state | `body.printing-pdf .roadmap-phase::before { transform: scale(1) !important; }` |
| Funnel bars empty | `transform: scaleX(0)` initial state | `body.printing-pdf .funnel-bar::before { transform: scaleX(var(--width, 1)) !important; }` |
| Reveal-animated content invisible | `opacity: 0` initial state | `body.printing-pdf .reveal { opacity: 1 !important; transform: none !important; }` |
| 1px hairline grids render at 2px | Sub-pixel anti-aliasing in PDF pipeline | `body.printing-pdf .dust-grid { display: none; }` (cleaner without than half-broken) |
| Aurora blur halos render badly | `filter: blur(140px)` not honoured | `body.printing-pdf .aurora { display: none; }` |
| Box-shadow banding | Sub-pixel rendering | `body.printing-pdf * { box-shadow: none !important; text-shadow: none !important; }` |

When you add a new component that uses any of these features, **add the matching print override** so it survives the export.

## Adding new gradient-text selectors

The rasteriser only walks selectors listed in `GRADIENT_TEXT_SELECTORS` inside `templates/base.html`. If you add a new component that uses `background-clip: text`, append its selector or you'll see fringes in the PDF for that element.

```js
const GRADIENT_TEXT_SELECTORS = [
  '.gradient-text',
  '.silence-num.gradient',
  '.hero-num',
  '.bigquote em',
  '.decision-q .go',
  '.your-new-component .number', // ← add yours here
];
```

## Email / attachment

`mailto:` does not support attachments — that's a standard, not a Chromium limitation. To email a deck:

1. Export to PDF with the script or the `P` shortcut.
2. Attach the PDF to your email composer manually.

If you want one-click sharing, host the deck (see `hosting.md`) and email the URL.
