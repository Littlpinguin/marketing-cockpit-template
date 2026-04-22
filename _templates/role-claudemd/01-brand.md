# 01-brand — keeper of the {{COMPANY_NAME}} brand

## Role

This folder is the **single source of truth** for identity, voice, messaging, and visual identity. It produces nothing; it is consulted by every other role (`02-strategy/` through `09-blog-seo/`) before any content is created.

**Absolute rule.** When `01-brand/` and another folder disagree, `01-brand/` wins. Surface the conflict to the user before acting.

## When to consult this folder

| You need to… | Read in priority |
|---|---|
| Write a post, email, page, event script | `voice.md` + `messaging-framework.md` |
| Target a specific audience | `personas.md` |
| Pick a number or a proof point | `messaging-framework.md` (key numbers section) |
| Use a tagline, quote, or signature phrase | `voice.md` (signature phrases) |
| Design a visual, pick a color or font | `style-guide.md` |
| Understand full strategic context | `brand-platform.md` |
| Identify an internal stakeholder | `stakeholders.md` |
| Reuse a visual asset | `assets/` |

## File inventory

These files are created by `/brand-discover`. If any are missing or empty, the wizard has not run to completion or the user deliberately skipped the section (see `_gaps.md`).

| File | Content | When to use |
|---|---|---|
| `voice.md` | Voice position, preferred/banned vocabulary, typography rules, signature phrases, bilingual rules | **Before every draft** |
| `messaging-framework.md` | Central message, per-persona messages, top 10 key numbers, CTA patterns, proof hierarchy | **Before every conversion-oriented piece** |
| `personas.md` | 2-4 personas with goals, frustrations, expectations, channels, main message per persona | **Before any targeted content** |
| `brand-platform.md` | Full strategic document (mission, vision, positioning, values, architecture) | For deep context |
| `style-guide.md` | Colors, typography, logo usage, components, illustration style, banned visual tropes | Before any visual creation |
| `stakeholders.md` | Founders, team, functional roles | When citing a person or assigning an action |
| `assets/` | Logos, banners, illustrations, photos | Reuse existing visuals before generating new ones |

## Universal brand rules (condensed)

Synthesis of `voice.md` and `style-guide.md`. If you only have a minute, this is what matters.

### Tone
{{BRAND_VOICE_POSITION}}

### Vocabulary
- ✅ **Prefer**: {{BRAND_VOCABULARY_PREFERRED}}
- ❌ **Avoid / ban**: {{BRAND_VOCABULARY_BANNED}}

### Typography and colors
- **Primary font**: `{{BRAND_FONT_PRIMARY}}`
- **Primary**: `{{BRAND_COLOR_PRIMARY}}`
- **Accent**: `{{BRAND_COLOR_ACCENT}}`
- **Dark**: `{{BRAND_COLOR_DARK}}`
- **Light**: `{{BRAND_COLOR_LIGHT}}`
- **Signature gradient**: `{{BRAND_GRADIENT}}`
- **Border-radius**: `{{BRAND_BORDER_RADIUS}}`

### Visuals
- ✅ **Prefer**: {{BRAND_ILLUSTRATION_STYLE}}
- ❌ **Ban**: {{BRAND_BANNED_VISUALS}}

### Signature phrases and taglines
{{BRAND_TAGLINES}}

### Top key numbers
{{BRAND_TOP_NUMBERS}}

## Fast access via semantic memory (if enabled)

If Qdrant is enabled (see `.setup-completed` → `features.qdrant.enabled`), this folder is indexed in the configured collection. For any question on voice, vocabulary, numbers, personas, or doctrine, semantic search is faster than a full read:

```
mcp__qdrant__qdrant_search(
  query="<your question in natural language>",
  top=5,
  filter_source_key="brand"
)
```

**Rule.** When information is available via `qdrant_search`, prefer that route over a long `Read`. Full reads remain justified for `voice.md` (short, often read whole) or to confirm the absence of a banned word.

If Qdrant is disabled, read the files directly — this folder is small enough that file reads are cheap.

## Brand consistency filter (5 points)

Before any content ships, the producing role must pass this filter — this is what the `brand-check` skill enforces:

1. **Vocabulary** — no banned word; preferred vocabulary present where relevant
2. **Tone** — aligned with `{{BRAND_VOICE_POSITION}}`
3. **Proof** — every major claim backed by a number from `messaging-framework.md` or a cited external reference
4. **Audience** — target persona identifiable; main message matches their expectation
5. **Visual / format** — colors, font, border-radius match `style-guide.md`

Fail on any point → back to drafting, no publication.

## Conflicts and updates

- **If another `CLAUDE.md` contradicts this folder**: `01-brand/` wins. Surface the conflict.
- **If a rule is missing**: do not invent. Escalate to {{COMPANY_MAIN_CONTACT}}.
- **If a number becomes outdated**: update `messaging-framework.md` and `brand-platform.md` together.

## What this folder does NOT do

- ❌ Produce content (→ roles 03 through 09)
- ❌ Manage the editorial calendar (→ `02-strategy/` + {{EDITORIAL_CALENDAR_TOOL}})
- ❌ Create visuals (→ `06-graphic-design/` + `image-generation` skill)
- ❌ Host the skills themselves (→ `.claude/skills/`) — but every skill must read `01-brand/` before acting.
