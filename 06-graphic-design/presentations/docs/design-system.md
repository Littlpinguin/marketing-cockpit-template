<!--
  VENDORED from slides-agent (https://github.com/Littlpinguin/slides-agent), docs/design-system.md,
  by scripts/sync-slides-engine.py. Do not edit here: change slides-agent,
  then run python3 scripts/sync-slides-engine.py. Mentions of CLAUDE.md,
  onboarding and the pexels-photos skill refer to slides-agent.
  Register: docs/vendored-slides.md
-->
# Design system reference

The aesthetic target is **editorial scientific premium** — Monocle × Bloomberg viz × MIT Tech Review print. What that means in practice: hairlines, generous whitespace, mono captions in lowercase, asymmetric layouts, slow animations, restraint everywhere.

## Principles

1. **One idea per slide.** If you're tempted to add a second column of bullet points, split.
2. **Three to four breathing slides per 24.** A single big number + one short phrase. They reset the eye.
3. **Emotional sparkline.** Map each slide to a Duarte beat (pain ↔ hope alternation). The deck has a shape.
4. **Visual through-line metaphor.** Pick one — an animation, a marker, an ambient watermark — that recurs and anchors the narrative.
5. **Extreme typographic hierarchy.** Weight 200 versus 700/900. Never weights in between. Same for size: display sizes (96–380px) live very far from body sizes (18–24px, never under the 18px floor `06-graphic-design/presentations/scripts/qa.py` enforces).
6. **Asymmetry.** Avoid centred boxes with even margins. Bias content left or right; let whitespace fall where it will.
7. **Slow motion.** Eases of 1.1s+ on `cubic-bezier(0.16, 1, 0.3, 1)`. No bouncy springs, no fast cuts.
8. **Brand mark every slide.** Discreet bottom-right marker in the chrome row. The reader always knows where they are.
9. **Watermark the heroes.** A large ambient brand mark on hero / decision slides only. `mix-blend-mode: multiply` on light, `screen` on dark. When the brand has a recurring motif, the `.texture` (light), `.motif` (dark) and `.corner` classes draw it from the brand-pattern tokens, under the same rule: hero and decision slides, not every slide.
10. **Triple navigation.** Drag bar + overview panel (grouped by `data-family`) + quick-jump. The presenter has options under pressure. The engine behind it is listed in `06-graphic-design/presentations/docs/engine-parity.md`.
11. **QA every iteration.** No deck ships without `python3 06-graphic-design/presentations/scripts/qa.py` returning `All slides clean`.

## Anti-patterns (refuse these)

- Bento grid + dot-grid background + glassmorphism — generic SaaS 2025. Indistinguishable.
- Four levels of text on one slide (section number + eyebrow + h1 + lede + body + caption). Death by PowerPoint.
- Bouncy spring animations. Breaks the slow tone.
- Stock photography of people in suits. Always wrong.
- Em-dash (`—`) in visible content. Use en-dash (`–`) or restructure.
- Any colour or font outside `06-graphic-design/presentations/tokens.css`.
- `place-items: center` on a parent containing a `transform: scale`d frame — centres the original layout box, not the visible rendering. Use `position: absolute; top: 50%; left: 50%; transform: translate(-50%, calc(-50% + yShift)) scale(...)`.
- `fill: url(#gradient)` on an inner `<path>` of a `<symbol>`. `<use>` does not propagate parent CSS into its shadow DOM. Use `fill="currentColor"` and set `color:` on the wrapper.
- `line-height: 0.9` + `letter-spacing: -0.04em` on huge display numbers. Glyphs (`%`, `O`, `9`) clip out of their box. Use `line-height: ≥ 1.1` on text titles (pure numerals may go tighter), `letter-spacing: ≥ -0.025em`, and keep the `.22em / .08em` padding/margin compensation of `.gradient-text` in `06-graphic-design/presentations/templates/base.html`.
- Shipping without `python 06-graphic-design/presentations/scripts/qa.py`. Don't.

## Token reference

All visual tokens live in `06-graphic-design/presentations/tokens.css`. Five groups:

- **Colour**: `--brand-primary`, `--brand-secondary`, `--brand-neutral-light`, `--brand-neutral-dark` (each with `-soft` and `-deep` variants, written as literal colours with their `color-mix()` formula in a comment). The template ships a neutral example palette; the comment next to each base value names the setup placeholder it maps to (`← BRAND_COLOR_PRIMARY`...).
- **Type**: `--font-display`, `--font-mono`. The two families are the only ones loaded.
- **Motion**: `--ease-slow` (1.2s for reveals), `--ease-med` (0.6s for transitions), `--ease-fast` (0.3s for hovers).
- **Label register**: `--chrome-opacity` and `--chrome-opacity-dark` (chrome text), `--label-accent` and `--label-accent-dark` (eyebrows and accent labels). Small text needs WCAG 4.5:1: these values reach it on every light variant and on neutral-dark while keeping the chrome quiet. When QA flags a label, retune them, not the slide.
- **Brand pattern**: `--brand-pattern`, `--brand-pattern-light`, `--corner-motif` (default `none`, so nothing shows) and their opacities `--pattern-opacity`, `--pattern-opacity-dark`, `--corner-opacity`. See "Brand pattern hooks" in `06-graphic-design/presentations/templates/components.md`.

Never hardcode hex anywhere in a deck. Reference the tokens. A brand revision then propagates with one edit.

## Typography scale (recommended starting point)

| Usage | Size | Weight |
|---|---|---|
| Display XL (silence numbers, hero) | 320–400px | 200 |
| Display (headlines, big quotes, decision) | 96–220px | 200–700 |
| Body L (ledes, kickers) | 24–28px | 300–400 |
| Body | 24px (18px floor) | 400 |
| Caption mono (eyebrows, labels, captions) | 12–13px, contrast 4.5:1 | 500 |

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
