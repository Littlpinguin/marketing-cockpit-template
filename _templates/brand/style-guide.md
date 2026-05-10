# Visual identity — {{COMPANY_NAME}}

Source of truth for colors, typography, illustration style, and visual constraints. Read by `05-web-content/`, `06-graphic-design/`, and the `image-generation` skill.

## Colors

| Role | Hex | Notes |
|---|---|---|
| Primary | `{{BRAND_COLOR_PRIMARY}}` | Buttons, links, highlights, key accents |
| Accent | `{{BRAND_COLOR_ACCENT}}` | Secondary emphasis, hover states, badges |
| Dark | `{{BRAND_COLOR_DARK}}` | Body text, dark backgrounds |
| Light | `{{BRAND_COLOR_LIGHT}}` | Page backgrounds, card fills |

### Signature gradient

```
{{BRAND_GRADIENT}}
```

Use for conversion blocks (final CTA sections, pricing callouts). Do not overuse — one per page max.

### Contrast constraints

- Body text on light background: AA minimum, AAA preferred
- Interactive elements: 3:1 minimum against adjacent colors
- Verify with a contrast checker before ship — the `brand-check` skill flags obvious violations but doesn't replace a real check

## Typography

| Usage | Family | Fallback stack |
|---|---|---|
| Primary display | {{BRAND_FONT_PRIMARY}} | `{{BRAND_FONT_PRIMARY}}, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif` |
| Secondary / mono | {{BRAND_FONT_SECONDARY}} | `{{BRAND_FONT_SECONDARY}}, ui-monospace, "SF Mono", Menlo, monospace` |

### Weights used

- Regular (400): body copy
- Medium (500): emphasis
- Semi-bold (600): H3
- Bold (700): H1, H2
- (Add or remove per actual brand usage)

## Spacing and radius

- **Border-radius**: {{BRAND_BORDER_RADIUS}}
- **Base spacing unit**: 8px (multiples: 8, 16, 24, 32, 48, 64)
- **Card padding**: 24px default, 32px for hero cards
- **Section vertical rhythm**: 80-120px between major sections on desktop, 48-72px on mobile

## Illustration style

{{BRAND_ILLUSTRATION_STYLE}}

Examples worth encoding:
- "Minimalist line art, single color + accent, no solid fills"
- "Isometric 3D, pastel palette, no photo-realistic elements"
- "Geometric flat, 2-3 colors per illustration, bold outlines"

## Banned visual tropes

Never produce or commission visuals featuring:

{{BRAND_BANNED_VISUALS}}

Typical items encoded here:
- Stock office photos with diverse smiling teams
- Generic handshakes
- Post-it walls
- Light-bulb-on-head "ideation" clichés
- Generic laptops on desks
- Puzzle-piece metaphors

## Logo

- Safe zone: (equal to the height of the lowercase 'x' in the wordmark)
- Minimum size: (e.g. 24px wide on screen, 15mm in print)
- Do not: recolor, rotate, distort, add effects, embed in a paragraph

Logo assets live in `01-brand/assets/`.

## Components (reusable patterns)

Common UI patterns used on landing pages and decks. Each should exist as HTML snippet in `05-web-content/templates/components/` or as a slide component in `06-graphic-design/presentations/templates/components/`.

- Hero block (headline + sub + CTA)
- Stats showcase (3-4 big numbers in a row)
- Testimonial card
- Pricing table
- FAQ accordion
- Final CTA with gradient background

## AI image generation specifics

The `image-generation` skill reads this file and injects the palette, typography, illustration style, and banned tropes into every prompt. No need to repeat them in individual briefs — just describe the subject.

{{IMAGE_GEN_SPECIFIC_RULES}}
