# Bootstrap Interview — Protocol for a new copilot project

> **Audience** : Claude Code at the root of a fresh clone of this template, when `.setup-completed` does not yet exist.
> **Goal** : Turn this empty template into a ready-to-use marketing copilot for one specific company in 20-40 minutes, starting from the minimum amount of information the user has to type.

## Model recommendation (tell the user on first contact)

Before anything else, greet the user and verify they are running **Claude Opus 4.6**. If they are on a smaller model, explain:

> This bootstrap interview and the operational copilot rely heavily on long-context reasoning and strategic planning. Opus 4.6 is strongly recommended. Smaller models will work for basic setup but will miss nuances during website analysis, brand synthesis, and skill personalization. You can switch model with `/model opus-4-6` in Claude Code.

Then proceed.

## Pre-flight checks (do these first, silently)

Before asking anything, verify:

1. `.setup-completed` does not exist at the project root. If it exists, **stop**: the project is already bootstrapped, just operate normally.
2. `.env` exists. If not, `cp .env.example .env` and tell the user you just created it. You will fill it as the interview progresses.
3. The `_bootstrap/inputs/` folder exists and is writable. This is where the user will drop documents during Phase 0.
4. Python 3.11+ and the dependencies are installed: run `python3 -c "import qdrant_client, google.genai, yaml, dotenv, requests, mcp" 2>/dev/null` and suggest `pip install ...` if it fails.

## Phase 0 — Discovery (the pre-fill)

The goal of Phase 0 is to **extract as much as possible automatically** before asking the user to type anything. A cold questionnaire of 50 questions is demoralizing; a conversation where Claude says "here is what I understood, correct me" is enjoyable.

### Step 0.1 — Ask for the website URL

Prompt the user:

> Welcome. To make this as fast as possible, I'll try to understand your company from existing material before asking you anything. Can you share your website URL? I'll fetch the homepage, the about page, and a couple of content pages to extract your positioning, your voice, your personas, and your visual identity automatically.

Use the `WebFetch` tool on:
- The homepage (`/`)
- `/about` or `/who-we-are` or `/about-us` or `/company`
- `/services` or `/products` or `/what-we-do` (if present)
- 1-2 blog posts or case studies to sample the writing style
- The footer (look for legal name, contact, founders, social links)

Parse and extract:
- **Company name** (from the `<title>` or the homepage H1)
- **Tagline** (often in the hero section)
- **Positioning in 1-2 sentences** (from the about page)
- **Mission and vision** (if explicitly stated)
- **Clients / logos** (from a "trusted by" section)
- **Key numbers / stats** (look for "100+", "10 years", "5M", etc.)
- **Colors** (inspect computed CSS on the homepage if possible, otherwise infer from screenshots)
- **Typography** (same)
- **Writing style samples** (paste 2-3 paragraphs for later reference)
- **Team / founders** (from about or team page)

If `WebFetch` is not available or returns nothing useful, ask the user to paste their homepage text into `_bootstrap/inputs/website-dump.md`.

### Step 0.2 — Ask for existing brand documents

Prompt:

> Do you have any of these documents already? If yes, drop them (or their markdown / PDF exports) into `_bootstrap/inputs/`. I'll read everything and pre-fill the brand doctrine.
>
> - Brand guide / style guide
> - Editorial charter / voice guidelines
> - Vision and mission statement
> - Pitch deck or investor deck
> - Personas or customer profiles
> - Messaging framework / value proposition canvas
> - Positioning document
> - Any strategic document you think is relevant
>
> Formats accepted: `.md`, `.txt`, `.pdf` (I'll read them), `.docx`, `.pptx`, screenshots. You can also paste raw text into files named with any convention — I'll figure it out.
>
> Once you've dropped the files, tell me "ready" and I'll read them.

Wait for the user to say "ready" or equivalent. Then:
- List all files in `_bootstrap/inputs/` recursively
- Read each file (use `Read` on markdown/text; extract text from PDFs via `pdftotext` or similar if available; ask the user to paste content if you can't read a binary format)
- Build a working memory of what you now know about the company
- Cross-reference with what you extracted from the website to detect contradictions

### Step 0.3 — Synthesize the draft profile

Produce a structured draft (just for the user to see, don't write to disk yet):

```
## Draft company profile (to be validated)

**Name**: ...
**Tagline**: ...
**Positioning**: ...
**Mission**: ...
**Vision**: ...
**Key clients / logos**: ...
**Key numbers**: ...
**Core voice traits**: ... (based on sampled writing)
**Banned words / pitfalls detected**: ... (from brand docs if any)
**Detected personas**:
  - Persona 1: [name or role], based on [which section]
  - Persona 2: ...
**Colors detected**: #XXXXXX (primary), #XXXXXX (accent), ...
**Typography detected**: [font]

**Gaps I could not fill from existing material**:
  - [list the things you still need to ask]
```

Present this to the user and ask:

> This is my draft understanding. I'd like to go through it section by section with you. For each one, please tell me: ✅ correct, 🟠 partially correct (explain), or 🔴 wrong (explain). When we're done, I'll write the validated version into `01-brand/`.

## Phase 1 — Identity validation

Walk section by section through the draft profile, asking the user to validate or correct. For each correction, update your working memory. After all sections are validated:

- Write `01-brand/charte-editoriale.md` (voice, tone, vocabulary, banned words, rules by channel)
- Write `01-brand/messaging-framework.md` (central message, messages per audience, key numbers, CTA types)
- Write `01-brand/plateforme-de-marque.md` (full strategic document, 200-500 lines depending on depth)
- Write `01-brand/style-guide.md` (colors, typography, visual language, tone of voice, do's and don'ts)
- Write `01-brand/CLAUDE.md` (the role orchestrator, with placeholders now filled)

If something is missing and the user doesn't know yet, leave a `{{TODO}}` marker and note it in a `01-brand/_gaps.md` file for later.

## Phase 2 — Personas

The user may already have personas (extracted in Phase 0) or not. If not, ask:

> Who are the 2-4 people you want your content to reach? For each one, I need: their role, their top 3 enjeux (goals), their top 3 frustrations, what they expect from you, and which channels they use.

Build them collaboratively. A good persona is concrete (Thomas, 45, VP IT, Canada) not abstract ("the decision maker"). Write the result to `01-brand/personas.md`.

Once personas are stable, also produce a **persona × channel matrix** and a **persona × pillar matrix** to guide content-strategy decisions.

## Phase 3 — Functionalities (tools-agnostic)

The template is tool-agnostic except for Qdrant. For each functionality, ask which tool the user uses, and either activate a built-in connector, generate a custom connector stub, or disable the functionality.

### 3.1 — Editorial calendar

> Where do you plan and track your marketing content? (options: Notion / Airtable / Trello / ClickUp / Google Sheets / custom / none yet)

- If **Notion**: ask for `NOTION_API_KEY`, the database URL (Claude extracts `database_id`), and the exact status name that marks content as "ready to publish" (e.g. `✅ Scheduled`). Save to `.env` and `_integrations/qdrant/config.yaml` under `functionalities.editorial_calendar`.
- If **Airtable**: ask for the API key, base ID, table name. Check if the connector `sources/airtable.py` exists; if not, create a stub with TODO comments and tell the user the first sync will require implementing the stub.
- If **custom / none**: disable the functionality in `config.yaml`, note it as a TODO.

### 3.2 — Email marketing

> How do you send your newsletters and marketing emails? (options: MailerLite / Mailchimp / Resend / Brevo / ConvertKit / custom / none yet)

Same pattern: ask for the API key, the main list/audience ID, and the group or segment you'll usually send to. Save to `.env` and `config.yaml`.

### 3.3 — Knowledge base

> Where do you store your internal knowledge (processes, playbooks, case studies, decisions)? (options: Outline / Notion / Confluence / GitBook / custom / none yet)

If yes, enable the connector and ask for the collection IDs or space keys to ingest. If **none**, skip — you can add it later.

### 3.4 — Events platform

> Do you host webinars, live sessions, or events online? (options: Livestorm / Zoom / Google Meet / Riverside / custom / none)

Livestorm is the only one with a built-in connector today. For others, note the API availability and generate a stub if the user has time to implement.

### 3.5 — CRM

> Do you use a CRM to track sales and leads? (options: HubSpot / Pipedrive / Odoo / Notion / Airtable / custom / none)

Currently CRM integration is a stretch goal: mark it as TODO unless the user wants to implement a connector now.

### 3.6 — Semantic memory (Qdrant)

> **Qdrant is the memory of your copilot.** Without it, each content creation is blind to your past: risk of repetition, contradiction, and inconsistency with your brand doctrine. With it, every agent can ask "has this been said?" and "what's the canonical claim?" in 500 milliseconds.
>
> It's optional — you can activate it now or later. Activation takes 5 minutes and you need a free Qdrant Cloud cluster at https://cloud.qdrant.io.
>
> Do you want to activate Qdrant now? (yes / later)

If **yes**:
- Ask for `QDRANT_URL` and `QDRANT_API_KEY`. Remind the user the key must be a **Cluster API Key** (not a management key), and to quote the value in `.env` if it contains a `|` character.
- Ask for the `GOOGLE_AI_API_KEY` if not already provided.
- Test the connection immediately: `curl -H "api-key: $QDRANT_API_KEY" $QDRANT_URL/collections`. If 403, help the user debug (usually a management key instead of cluster key).
- Run `python3 _integrations/qdrant/init_collection.py` to create the collection.
- Run `python3 _integrations/qdrant/sync.py --source brand` to ingest the freshly-created brand docs from Phase 1.
- Validate with `python3 _integrations/qdrant/sync.py --query "mission of the company" --top 3`.

If **later**: mark `qdrant.enabled: false` in `config.yaml` and add a note in each role CLAUDE.md that says "Qdrant is disabled. Skills will fall back to file reads, which is slower and misses the anti-repetition check."

### 3.7 — Image generation (Gemini nano-banana-pro)

> Your copilot can generate brand-compliant images directly via Google's Gemini `gemini-3-pro-image-preview` (a.k.a. nano-banana-pro). Every prompt is automatically prefixed with your brand guidelines — color palette, typography, illustration style, banned visual tropes — so you don't have to repeat them in each request.
>
> It uses the same `GOOGLE_AI_API_KEY` as the semantic memory. If the key is present, image generation is enabled automatically.
>
> Do you want to activate it? (yes / no)

If **yes**:
- Ensure `GOOGLE_AI_API_KEY` is set and `GOOGLE_AI_IMAGE_MODEL="gemini-3-pro-image-preview"` is in `.env`.
- Ask the user for any **specific visual rules** to add to the prompt prefix:
  - Preferred illustration style (flat, line art, isometric, photo-realistic, collage, ...)
  - Aspect ratios most often needed (square, 16:9, 9:16, 4:5, banner)
  - Banned visual tropes (stock office photos, handshakes, generic laptops, post-its, ...)
  - Mandatory elements (logo position, brand colors, signature gradient, watermark)
- Save these rules to `01-brand/style-guide.md` under a "Visual language" section.
- Enable the `image-generation` skill in `.agents/skills/image-generation.md` by filling the {{placeholder}} sections.
- Test with a sample prompt: "a hero image for our landing page" and show the result to the user.

If **no**: disable the skill in `config.yaml` (`functionalities.image_generation.enabled: false`).

## Phase 4 — Skills personalization

The template ships 9 skills, each with sensible defaults. For each skill, show the user the default and ask if they want to personalize:

1. `brand-check` — the 5-point filter (vocabulary, tone, proof, audience, visual). Ask: "Any custom rules to add? Typographic rules (no em dashes, no emoji in emails, ...), structural rules (always cite a chiffre in the first sentence, ...), or style rules specific to your brand?"
2. `social-content` — LinkedIn, Discord, WhatsApp defaults. Ask: "How many posts per week? Which pillars? Any banned topics?"
3. `email` — newsletters, promos, sales. Ask: "What's your newsletter cadence? Who signs the sales outreach? What's your email voice compared to your social voice?"
4. `copywriting` — long-form web. Ask: "Any section templates you always use on landing pages?"
5. `copy-editing` — the 7-pass quality review. Ask: "Any red flags specific to your brand that should trigger an automatic block?"
6. `content-strategy` — editorial planning, pillar balance. Ask: "What are your content pillars and their target percentages?"
7. `seo` — blog, keywords, optimization. Ask: "Do you have a target keyword list or clusters? What's your meta tag convention?"
8. `event-marketing` — event communication. Ask: "How often do you run events? What's your typical announcement cadence (J-60 to J+7)?"
9. `image-generation` — brand-compliant visuals. Ask: "Any specific visual rules not already captured in the style guide?"

For each personalization, update the `.agents/skills/<skill>.md` file by replacing the `{{BRAND_SPECIFIC_RULES}}` section.

## Phase 5 — Wrap-up and verification

1. Write `.setup-completed` with JSON metadata: `{"completed_at": ISO8601, "company": "...", "qdrant_enabled": true/false, "image_gen_enabled": true/false, "functionalities": [...]}`.
2. Update the root `CLAUDE.md` to remove the bootstrap-detection section and switch to operational mode. The operational root CLAUDE.md is the same as the N2-style orchestrator: identity, architecture table, universal rules, tools inventory, workflows.
3. Run a final verification:
   - `python3 _integrations/qdrant/sync.py --stats` (if Qdrant enabled)
   - `python3 _integrations/qdrant/sync.py --verify` (if Qdrant enabled)
   - Verify `.env` has all the keys the user chose
   - Verify each CLAUDE.md in role folders has no remaining `{{placeholders}}`
4. Show the user a recap and the 5 recommended first actions:
   - "Try `qdrant_search` with a question about your brand"
   - "Draft your first LinkedIn post via the `social-content` skill"
   - "Install the weekly cron: `bash _integrations/qdrant/cron/install.sh`"
   - "Read your fresh `01-brand/charte-editoriale.md` and fix anything I misunderstood"
   - "Drop a first transcript into `_sources/transcriptions/internal/` and run `sync.py --source transcripts`"

## Templates and placeholders

All operational files in this template use **Mustache/Jinja-style placeholders** `{{VARIABLE_NAME}}` that the interview must replace. The canonical variable list is in `_bootstrap/questions.md`.

## Failure modes to avoid

- **Do not ask 50 questions in a row**. Always pre-fill from the website and brand docs first. Ask only for what you couldn't extract.
- **Do not write files before the user has validated the draft**. Users feel disrespected when Claude starts writing `charte-editoriale.md` before they've confirmed the tone. Always show, validate, then write.
- **Do not invent details**. If you don't know the founders, ask. If the website doesn't show a typography, ask. Hallucination is worse than an empty field during bootstrap.
- **Do not skip Phase 3.6 explanation**. Users must understand WHY Qdrant matters before they decide to activate it. An opt-out without explanation is a design smell.
- **Do not leave `{{placeholders}}` in operational files**. Phase 5 must verify zero remaining placeholders before writing `.setup-completed`.
