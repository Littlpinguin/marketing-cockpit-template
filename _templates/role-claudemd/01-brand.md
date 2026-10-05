# 01-brand — keeper of the {{COMPANY_NAME}} brand

## Role

This folder is the **single source of truth** for identity, voice, messaging, and visual identity. It produces nothing; it is consulted by every other role (`02-strategy/` through `09-seo/`) before any content is created.

**Absolute rule.** When `01-brand/` and another folder disagree, `01-brand/` wins. Surface the conflict to the user before acting.

## When to consult this folder

| You need to… | Read in priority |
|---|---|
| Write a post, email, page, event script | `voice.md` + `messaging-framework.md` |
| Target a specific audience | `personas.md` |
| Pick a number or a proof point | `messaging-framework.md` (key numbers section) |
| Use a tagline, quote, or signature phrase | `voice.md` (signature phrases) |
| Design a visual, pick a color or font | `style-guide.md` (intent) + `tokens.json` (exact values) |
| Check a draft for AI tells | `anti-ai-writing-style.md` |
| Know what the brand already refused | `exemples-rejetes.md` |
| Publish something AI-generated | `divulgation-ia.md` |
| Publish a third-party logo, a photo of a person, a font | `droits.md` |
| Understand full strategic context | `brand-platform.md` |
| Identify an internal stakeholder | `stakeholders.md` |
| Reuse a visual asset | `assets/` |

**Published examples.** Re-reading the 3 to 5 most recent pieces of the target channel before drafting stays the normal procedure, for anti-repetition as for tone calibration: it is the most reliable material an agent has. What is forbidden is something else: writing a specific deliverable into a skill as *the* model to imitate, which makes every later production converge on it. Quoting a published piece in a discussion, or using it to calibrate: allowed. Freezing it as a reference inside a skill: not allowed.

## Task router

Entry point of any production: read what the row says, in that order, and nothing more. A file already read in the session is not reloaded.

| Deliverable | Files to read, in order |
|---|---|
| Text post or email | `voice.md` → `messaging-framework.md` (key numbers) → `anti-ai-writing-style.md` → `exemples-rejetes.md` |
| Visual | `tokens.json` → `assets/` catalogue → `divulgation-ia.md` → `droits.md` if a third-party logo or a person appears |
| Deck or carousel | the two rows above, text then visual, plus `style-guide.md` (type scale) |
| Web page | `voice.md` → `messaging-framework.md` → `style-guide.md` → `tokens.json` |

## File inventory

These files are created by `/brand-discover`. If any are missing or empty, the wizard has not run to completion or the user deliberately skipped the section (see `_gaps.md`).

| File | Content | When to use |
|---|---|---|
| `voice.md` | Voice position, preferred/banned vocabulary, typography rules, signature phrases, bilingual rules | **Before every draft** |
| `messaging-framework.md` | Central message, per-persona messages, top 10 key numbers, CTA patterns, proof hierarchy | **Before every conversion-oriented piece** |
| `personas.md` | 2-4 personas with goals, frustrations, expectations, channels, main message per persona | **Before any targeted content** |
| `brand-platform.md` | Full strategic document (mission, vision, positioning, values, architecture) | For deep context |
| `style-guide.md` | Colors, typography, logo usage, components, illustration style, banned visual tropes | Before any visual creation |
| `tokens.json` | Palette, gradient, fonts, type scale, radii, logo clear space in DTCG format: the single machine-readable source. CSS consumers are generated from it (`python3 scripts/build-tokens.py`) | Before any CSS, composition or export. Never type a hex code from memory |
| `anti-ai-writing-style.md` | Anti-AI doctrine: writing and formatting rules, banned list (dead AI vocabulary, negative parallelisms, rule of three, em dash) | **Before every draft**, and again at review. One tell is enough to block |
| `exemples-rejetes.md` | Rejection corpus: one entry per rejected draft (faulty excerpt in a code block, reason, rule with its section, retained fix), fed by step 5 of `brand-check` | **With the published examples**, before drafting. The archives say what the brand does, this file what it refused |
| `divulgation-ia.md` | AI disclosure policy: principle, disclosure per content type, wording per channel, `généré-par-ia:` field of the asset catalogue, what is never generated, edge cases | **Before publishing** a generated visual, voice or video. Single reference: other files point here |
| `droits.md` | Rights register: font licences, third-party logo permissions, image rights of people, AI-derived portraits, and the human actions still pending | **Before publishing** a client or partner logo, a photo of a person, a portrait. "à confirmer" is an open question, not a permission |
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

## Access

Read the files directly — this folder is small enough that file reads are cheap. `voice.md` is short and often read whole; for a targeted lookup (a number, a banned word), grep the relevant file (`messaging-framework.md`, `voice.md`) instead of reading everything.

## What the skills never judge from memory

The brand is checkable by script; these checks take precedence over any judgment call.

| Question | File or command |
|---|---|
| Exact value of a color, a font, a radius? | `tokens.json`; `python3 scripts/build-tokens.py --check` |
| Does this text follow the charter (banned words, dashes, titles, hashtags, placeholders, palette, fonts)? | `python3 scripts/lint-brand.py <file>` (step 0 of `brand-check`) |
| Has this topic already been covered, on which channel, when? | `_templates/inventory.md`; `python3 scripts/build-inventory.py --check` |
| May we publish this font, logo or photo? | `droits.md` |
| Must AI involvement be disclosed, and how? | `divulgation-ia.md` |
| Was this phrasing already rejected? | `exemples-rejetes.md` |

## Brand consistency filter (5 points)

Before any content ships, the producing role must pass this filter — this is what the `brand-check` skill enforces. Step 0 runs first: `python3 scripts/lint-brand.py <draft>` (any error blocks).

1. **Vocabulary** — no banned word; preferred vocabulary present where relevant
2. **Tone** — aligned with `{{BRAND_VOICE_POSITION}}`
3. **Proof** — every major claim backed by a number from `messaging-framework.md` or a cited external reference
4. **Audience** — target persona identifiable; main message matches their expectation
5. **Visual / format** — colors, font, border-radius match `style-guide.md`

Fail on any point → back to drafting, no publication.

## Conflicts and updates

- **If another `CLAUDE.md` contradicts this folder**: `01-brand/` wins. Surface the conflict.
- **If a rule is missing**: do not invent. Escalate to {{COMPANY_MAIN_CONTACT}}.
- **If a color or font changes**: edit `tokens.json`, run `python3 scripts/build-tokens.py`, never patch a CSS file by hand.
- **If a word joins the banned list**: add it to `voice.md`, then to `[forbidden-words.charter]` of `scripts/lint-brand.toml`.
- **If a number becomes outdated**: update `messaging-framework.md` and `brand-platform.md` together.

## What this folder does NOT do

- ❌ Produce content (→ roles 03 through 09)
- ❌ Manage the editorial calendar (→ `02-strategy/` + {{EDITORIAL_CALENDAR_TOOL}})
- ❌ Create visuals (→ `06-graphic-design/` + `image-generation` skill)
- ❌ Host the skills themselves (→ `.claude/skills/`) — but every skill must read `01-brand/` before acting.
