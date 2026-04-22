# Voice doctrine — {{COMPANY_NAME}}

Source of truth for tone, vocabulary, and style rules. Every producing role (03 through 09) reads this before drafting. The `brand-check` skill uses it as the filter.

## Voice position

{{BRAND_VOICE_POSITION}}

(Two sentences describing where this brand sits on the axes formal/casual, technical/accessible, confident/humble, playful/serious. Avoid single-label summaries like "professional yet approachable" — they don't encode anything the copilot can use.)

## Preferred vocabulary

Use these words intentionally and often:

{{BRAND_VOCABULARY_PREFERRED}}

## Banned vocabulary

Never use these. Claimed terms, clichés, and words the brand has actively rejected:

{{BRAND_VOCABULARY_BANNED}}

## Typography rules

{{TYPOGRAPHY_RULES}}

Examples of rules worth encoding:
- Em dashes vs en dashes vs hyphens
- Serial comma / Oxford comma
- Capitalization in headings (sentence case vs title case)
- Single vs double space after period
- Quotes: curly vs straight, single vs double

## Signature phrases and taglines

Recurring phrasings that feel like house style. Reusable in copy where appropriate:

{{BRAND_TAGLINES}}

## Key numbers (canonical)

Every number cited in published content comes from this list (or `messaging-framework.md`). Numbers outside these lists require explicit external citation.

{{BRAND_TOP_NUMBERS}}

## Language rules

- **Primary language**: {{BRAND_DEFAULT_LANGUAGE}}
- **Bilingual**: {{BRAND_BILINGUAL}}
- **Bilingual production rules**: {{BILINGUAL_RULES}}

## AI disclosure policy

How the brand surfaces AI involvement in public content. Options range from "no disclosure needed for functional assets, disclosure required for public-facing illustrations and audio" to stricter per-channel policies.

(Filled during `/brand-discover`. Consumed by `image-generation` skill and `copy-editing` final pass.)

## What counts as "off-voice"

Examples of phrasings that would fail a brand-check on tone grounds, even if they use allowed vocabulary:

- (3-5 real-world examples collected during `/brand-discover` from rejected drafts or explicit user feedback)
