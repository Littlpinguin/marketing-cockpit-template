# Design system reference

The aesthetic target is **editorial scientific premium** — Monocle × Bloomberg viz × MIT Tech Review print. What that means in practice: hairlines, generous whitespace, mono captions in lowercase, asymmetric layouts, slow animations, restraint everywhere.

## Principles

1. **One idea per slide.** If you're tempted to add a second column of bullet points, split.
2. **Three to four breathing slides per 24.** A single big number + one short phrase. They reset the eye.
3. **Emotional sparkline.** Map each slide to a Duarte beat (pain ↔ hope alternation). The deck has a shape.
4. **Visual through-line metaphor.** Pick one — an animation, a marker, an ambient watermark — that recurs and anchors the narrative.
5. **Extreme typographic hierarchy.** Weight 200 versus 700/900. Never weights in between. Same for size: display sizes (96–380px) live very far from body sizes (15–22px).
6. **Asymmetry.** Avoid centred boxes with even margins. Bias content left or right; let whitespace fall where it will.
7. **Slow motion.** Eases of 1.1s+ on `cubic-bezier(0.16, 1, 0.3, 1)`. No bouncy springs, no fast cuts.
8. **Brand mark every slide.** Discreet bottom-right marker in the chrome row. The reader always knows where they are.
9. **Watermark the heroes.** A large ambient brand mark on hero / decision slides only. `mix-blend-mode: multiply` on light, `screen` on dark.
10. **Triple navigation.** Drag bar + overview panel + quick-jump. The presenter has options under pressure.
11. **QA every iteration.** No deck ships without `python scripts/qa.py` returning green.

## Anti-patterns (refuse these)

- Bento grid + dot-grid background + glassmorphism — generic SaaS 2025. Indistinguishable.
- Four levels of text on one slide (section number + eyebrow + h1 + lede + body + caption). Death by PowerPoint.
- Bouncy spring animations. Breaks the slow tone.
- Stock photography of people in suits. Always wrong.
- Em-dash (`—`) in visible content. Use en-dash (`–`) or restructure.
- Any colour or font outside `tokens.css`.
- `place-items: center` on a parent containing a `transform: scale`d frame — centres the original layout box, not the visible rendering. Use `position: absolute; top: 50%; left: 50%; transform: translate(-50%, calc(-50% + yShift)) scale(...)`.
- `fill: url(#gradient)` on an inner `<path>` of a `<symbol>`. `<use>` does not propagate parent CSS into its shadow DOM. Use `fill="currentColor"` and set `color:` on the wrapper.
- `line-height: 0.9` + `letter-spacing: -0.04em` on huge display numbers. Glyphs (`%`, `O`, `9`) clip out of their box. Use `line-height: ≥ 1.05`, `letter-spacing: ≥ -0.025em`, and add the padding/margin compensation pattern from `templates/base.html`.
- Shipping without `python scripts/qa.py`. Don't.

## Token reference

All visual tokens live in `tokens.css`. Three layers:

- **Colour**: `--brand-primary`, `--brand-secondary`, `--brand-neutral-light`, `--brand-neutral-dark` (each with `-soft` and `-deep` variants).
- **Type**: `--font-display`, `--font-mono`. The two families are the only ones loaded.
- **Motion**: `--ease-slow` (1.2s for reveals), `--ease-med` (0.6s for transitions), `--ease-fast` (0.3s for hovers).

Never hardcode hex anywhere in a deck. Reference the tokens. A brand revision then propagates with one edit.

## Typography scale (recommended starting point)

| Usage | Size | Weight |
|---|---|---|
| Display XL (silence numbers, hero) | 320–400px | 200 |
| Display (headlines, big quotes, decision) | 96–220px | 200–700 |
| Body L (ledes, kickers) | 18–22px | 300–400 |
| Body | 15px | 400 |
| Caption mono (eyebrows, labels, captions) | 12–13px | 500 |

Lowercase for mono captions. UPPERCASE only for very short two-or-three-letter codes (`KPI`, `NPS`).

## Frame system

- **Native frame**: 1920×1080. Don't change.
- **Slide padding**: 80px top, 120px sides, **110px bottom** (the bottom value is load-bearing — it leaves room for the chrome row plus a 16px safety gap). Don't reduce.
- **Chrome inset**: 36px vertical, 60px horizontal. The chrome rows (`top` and `bottom`) sit inside this.
- **Bottom-content safe zone**: no element may extend below y=1000. The QA script verifies this on every slide.

## Time-to-deliverable (rough estimate)

For a 20–25 slide deck, first cut to deliverable v1:

- 30 min reading the brief / source material
- 45 min on art direction + slide map
- 2–3 h building components and slides
- 30 min QA + 30 min iterating to "All slides clean"
- 30 min polish

About **5 hours** for a deliverable v1, plus 2–4 iteration rounds of 30–60 min each based on feedback. The QA + polish phase is where most decks visibly improve.
