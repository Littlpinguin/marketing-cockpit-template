# Canonical placeholder variables

Every template file in this project uses Mustache/Jinja-style placeholders `{{VARIABLE_NAME}}`. This file is the canonical list of all variables the bootstrap interview must collect and replace. If you add a new placeholder to any template, add it here so future maintainers know what it means.

## Identity

| Variable | Description | Example |
|---|---|---|
| `{{COMPANY_NAME}}` | Legal or commercial name | `Acme Inc.` |
| `{{COMPANY_SHORT_NAME}}` | Short form used in casual copy | `Acme` |
| `{{COMPANY_WEBSITE}}` | Primary website URL with https | `https://acme.com` |
| `{{COMPANY_TAGLINE}}` | One-line tagline | `Ship faster, ship better` |
| `{{COMPANY_POSITIONING}}` | 1-2 sentence positioning | `The first developer-first CI platform that scales from solo to enterprise.` |
| `{{COMPANY_MISSION}}` | Mission statement | `Empower every developer to ship with confidence` |
| `{{COMPANY_VISION}}` | Vision statement | `A world where shipping code is boring and boring means reliable` |
| `{{COMPANY_SECTOR}}` | Industry | `DevOps SaaS` |
| `{{COMPANY_AUDIENCE_SHORT}}` | Short audience descriptor for hero lines | `developers and devops teams` |
| `{{COMPANY_HQ}}` | Headquarters location | `Paris, France` |
| `{{COMPANY_FOUNDERS}}` | Founder names, comma-separated | `Alice Dupont, Bob Martin` |
| `{{COMPANY_MAIN_CONTACT}}` | Marketing lead | `Claire Durand, Head of Marketing` |
| `{{SALES_CONTACT}}` | Sales outreach signatory | `Paul Bernard, Sales` |

## Visual identity

| Variable | Description | Example |
|---|---|---|
| `{{BRAND_FONT_PRIMARY}}` | Main typeface | `Inter` |
| `{{BRAND_FONT_SECONDARY}}` | Accent typeface | `JetBrains Mono` |
| `{{BRAND_COLOR_PRIMARY}}` | Primary color hex | `#1E40AF` |
| `{{BRAND_COLOR_ACCENT}}` | Accent color hex | `#F59E0B` |
| `{{BRAND_COLOR_DARK}}` | Dark text / background | `#0F172A` |
| `{{BRAND_COLOR_LIGHT}}` | Light background | `#F8FAFC` |
| `{{BRAND_GRADIENT}}` | Signature gradient CSS | `linear-gradient(90deg, #1E40AF 0%, #F59E0B 100%)` |
| `{{BRAND_BORDER_RADIUS}}` | Typical radius for UI | `12-24px` |
| `{{BRAND_ILLUSTRATION_STYLE}}` | Preferred illustration style | `Minimalist line art, isometric, no stock photos` |
| `{{BRAND_BANNED_VISUALS}}` | Visual tropes to avoid | `stock office photos, handshakes, generic laptops, post-its` |

## Voice and vocabulary

| Variable | Description | Example |
|---|---|---|
| `{{BRAND_VOICE_POSITION}}` | Where the brand sits on voice axes | `Expert accessible: rigorous content, warm delivery` |
| `{{BRAND_VOCABULARY_PREFERRED}}` | Terms to use | `platform, team, ship, deploy, developer` |
| `{{BRAND_VOCABULARY_BANNED}}` | Terms to never use | `solution, innovation, game-changer, disrupt, synergy` |
| `{{BRAND_TAGLINES}}` | Reusable signature lines | `"Ship faster, ship better.", "Boring is the new exciting."` |
| `{{BRAND_TOP_NUMBERS}}` | Top 10 key stats | `"99.9% uptime", "10k+ developers", "50% faster CI"` |
| `{{BRAND_DEFAULT_LANGUAGE}}` | Primary language for content | `en` / `fr` |
| `{{BRAND_BILINGUAL}}` | Bilingual mode | `both` / `en-only` / `fr-only` |
| `{{BILINGUAL_RULES}}` | Rules for producing bilingual content | `EN first, FR cultural adaptation` |
| `{{VOCABULARY_TABLE}}` | Markdown table rows for correct/incorrect vocabulary | (rows only) |
| `{{TYPOGRAPHY_RULES}}` | Specific typographic rules | `No em dashes, one space after period` |

## Personas

| Variable | Description |
|---|---|
| `{{PERSONA_1_NAME}}` | First persona name and role |
| `{{PERSONA_1_DETAILS}}` | Full persona block (enjeux, frustrations, attentes, canaux, message principal) |
| `{{PERSONA_2_NAME}}` | Second persona |
| `{{PERSONA_2_DETAILS}}` | |
| `{{PERSONA_3_NAME}}` | Third (optional) |
| `{{PERSONA_3_DETAILS}}` | |
| `{{PERSONA_4_NAME}}` | Fourth (optional) |
| `{{PERSONA_4_DETAILS}}` | |
| `{{PERSONA_CHANNEL_MATRIX}}` | Markdown table of persona × channel |

## Content pillars and cadences

| Variable | Description | Example |
|---|---|---|
| `{{PILLAR_1}}` | First pillar name + target % + topics + main channel | `Data & Expertise (40%) — stats, benchmarks — LinkedIn, Blog` |
| `{{PILLAR_2}}` | | |
| `{{PILLAR_3}}` | | |
| `{{PILLAR_4}}` | | |
| `{{PILLAR_5}}` | | |
| `{{CONTENT_CADENCE_LINKEDIN}}` | LinkedIn cadence | `4-5 posts / week` |
| `{{CONTENT_CADENCE_NEWSLETTER}}` | Newsletter cadence | `Monthly` |
| `{{CONTENT_CADENCE_BLOG}}` | Blog cadence | `2 articles / month` |
| `{{CONTENT_CADENCE_DISCORD}}` | Discord cadence (if applicable) | `Weekly` |
| `{{CONTENT_CADENCE_WHATSAPP}}` | WhatsApp cadence (if applicable) | `Max 2 / week` |
| `{{CONTENT_KPIS}}` | KPIs to track (bulleted markdown block) | `- LinkedIn impressions\n- Newsletter open rate\n- ...` |

## Skill-specific personalizations

These placeholders are filled by the user during Phase 4 of the bootstrap interview. They represent brand-specific rules injected into each skill template.

| Variable | Used in | Description |
|---|---|---|
| `{{BRAND_SPECIFIC_CHECK_RULES}}` | brand-check.md | Custom rules for the 5-point filter (typographic rules, format rules, etc.) |
| `{{BRAND_SPECIFIC_RULES}}` | multiple skills | Generic bucket for extra rules |
| `{{SOCIAL_VOICE_DOS}}` | social-content.md | Bulleted "what we do" on social |
| `{{SOCIAL_VOICE_DONTS}}` | social-content.md | Bulleted "what we don't do" on social |
| `{{SOCIAL_HOOK_EXAMPLES}}` | social-content.md | 3-5 examples of hooks that work |
| `{{SOCIAL_SPECIFIC_RULES}}` | social-content.md | Brand-specific social rules |
| `{{SOCIAL_EMOJI_RULE}}` | social-content.md | Emoji policy | `Sparingly, max 1 per post` |
| `{{SOCIAL_DASH_RULE}}` | social-content.md | Dash typography rule | `No em dashes` |
| `{{COPYWRITING_SPECIFIC_RULES}}` | copywriting.md | Landing page specific rules |
| `{{COPY_EDITING_SPECIFIC_RULES}}` | copy-editing.md | 7-pass review custom rules |
| `{{STRATEGY_SPECIFIC_RULES}}` | content-strategy.md | Planning-specific rules |
| `{{SEO_CLUSTERS}}` | seo.md | Thematic clusters with keywords and personas |
| `{{SEO_SPECIFIC_RULES}}` | seo.md | SEO custom rules |
| `{{EMAIL_SPECIFIC_RULES}}` | email.md | Email marketing custom rules |
| `{{EMAIL_SIGNATURE_LINE}}` | email.md | Universal closing line | `"Talk soon,"` |
| `{{NEWSLETTER_VOICE}}` | email.md | Newsletter tone description |
| `{{PROMO_VOICE}}` | email.md | Promo email tone description |
| `{{SALES_VOICE}}` | email.md | Sales outreach tone description |
| `{{EVENT_SPECIFIC_RULES}}` | event-marketing.md | Event-specific rules |
| `{{EVENT_TEAM}}` | event-marketing.md | Event team roles |
| `{{IMAGE_GEN_SPECIFIC_RULES}}` | image-generation.md | Image generation rules |
| `{{IMAGE_GEN_EXAMPLES}}` | image-generation.md | 3-5 example prompts that work |
| `{{BLOG_CMS}}` | seo.md, 09-blog-seo | Blog publishing platform | `WordPress` / `Ghost` / `Hashnode` / ... |

## Functionalities and tools

For each functionality, the interview fills a structured block. See `_integrations/qdrant/config.yaml` and `.env.example` for the exact shape.

### Tool selectors and enable flags

| Variable | Description |
|---|---|
| `{{EDITORIAL_CALENDAR_TOOL}}` | `notion` / `airtable` / `trello` / `clickup` / `google-sheets` / `custom` / `none` |
| `{{EDITORIAL_CALENDAR_ENABLED}}` | `true` / `false` |
| `{{EDITORIAL_CALENDAR_STATUS_FILTER}}` | Exact label that marks content as "ready to publish" | `"Scheduled"` |
| `{{EMAIL_MARKETING_TOOL}}` | `mailerlite` / `mailchimp` / `resend` / `brevo` / `convertkit` / `custom` / `none` |
| `{{EMAIL_MARKETING_ENABLED}}` | `true` / `false` |
| `{{EMAIL_MARKETING_ENV_KEY}}` | Name of the env variable holding the API key | `MAILERLITE_API_KEY` |
| `{{EMAIL_MARKETING_LIST_ID}}` | Main list / audience / group ID |
| `{{KNOWLEDGE_BASE_TOOL}}` | `outline` / `notion` / `confluence` / `gitbook` / `custom` / `none` |
| `{{KNOWLEDGE_BASE_ENABLED}}` | `true` / `false` |
| `{{KNOWLEDGE_BASE_URL}}` | Base URL of the KB | `https://kb.example.com` |
| `{{KNOWLEDGE_BASE_ENV_KEY}}` | Env variable for the KB API key | `OUTLINE_API_KEY` |
| `{{EVENTS_PLATFORM_TOOL}}` | `livestorm` / `zoom` / `riverside` / `google-meet` / `custom` / `none` |
| `{{EVENTS_PLATFORM_ENABLED}}` | `true` / `false` |
| `{{EVENTS_PLATFORM_ENV_KEY}}` | Env variable for events API | `LIVESTORM_API_KEY` |
| `{{CRM_TOOL}}` | `hubspot` / `pipedrive` / `odoo` / `notion` / `airtable` / `custom` / `none` |
| `{{CRM_ENABLED}}` | `true` / `false` |
| `{{QDRANT_ENABLED}}` | `true` / `false` |
| `{{QDRANT_COLLECTION}}` | Name of the Qdrant collection | `knowledge` / `<company-slug>-memory` |
| `{{IMAGE_GENERATION_ENABLED}}` | `true` / `false` |
| `{{NOTION_EDITORIAL_DATABASE_ID}}` | Notion database ID | `abcdef12-3456-4789-abcd-ef0123456789` |
| `{{NOTION_EDITORIAL_DATA_SOURCE_ID}}` | Notion data source ID (for multi-source DBs) | `fedcba98-7654-4321-fedc-ba9876543210` |
| `{{AIRTABLE_BASE_ID}}` | Airtable base ID (if Airtable is chosen) | `appXXXXXXXXXXXXXX` |
| `{{AIRTABLE_TABLE_NAME}}` | Airtable table name | `Editorial Calendar` |

## Email signature template placeholders

Used in `08-mail-signatures/template.html`:

| Variable | Description |
|---|---|
| `{{NAME}}` | Full name of the team member |
| `{{ROLE}}` | Role / title |
| `{{EMAIL}}` | Email address |
| `{{PHONE}}` | Phone (optional) |
| `{{LINKEDIN_URL}}` | LinkedIn profile URL |

## Draft / in-progress markers

| Variable | Description |
|---|---|
| `{{TODO}}` | Marker left in fields the interview couldn't fill, to be completed later |
| `{{MONTH_YEAR}}` | Used in newsletter draft filenames | `MARCH_2026` |

## Project-wide

| Variable | Description | Example |
|---|---|---|
| `{{PROJECT_SLUG}}` | Lowercase dashed slug used in filenames | `acme-marketing-copilot` |
| `{{PROJECT_ROOT}}` | Absolute path of the project | `/Users/alice/code/acme-copilot` |
| `{{SETUP_DATE}}` | ISO 8601 date of bootstrap completion | `2026-04-15` |
