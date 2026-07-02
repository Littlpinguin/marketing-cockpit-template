# Marketing Copilot — root orchestrator

> **Model recommendation.** This copilot is designed for **Claude Sonnet 4.6**. The brand doctrine and per-role CLAUDE.md files are personalized enough that Sonnet 4.6 handles strategic reasoning, brand-check, and copy-editing with quality. Opus is overkill for most sessions; Haiku is a reasonable fallback for short, routine tasks (single-post drafting, short replies).

## Setup detection — read this first, every session

If the file `.setup-completed` does **not** exist at the project root, this repo has not been customized for a specific company yet. Do **not** start producing content. Instead, greet the user and suggest:

> This template has not been set up yet. Run `/start-copilot` to launch the wizard. It will fetch your website, analyze your recent posts and articles, propose a draft brand doctrine, let you choose your tools, and prepare the repo in 30-60 minutes.

If `.setup-completed` exists, skip the bootstrap path entirely and operate normally.

---

## Security non-negotiables (apply every session)

See `SECURITY.md` for the full rules. The short list:

1. **Never paste API keys, tokens, or secrets in a chat message or commit.** Use `.env` + `.env.example` with placeholders only. Before every push, grep the diff for secrets.
2. **Never use destructive Bash commands without explicit user confirmation** — `rm -rf`, `git push --force`, `git reset --hard`, `launchctl` on system-wide agents, anything that sends email or hits an external API.
3. **Dry-run before production push.** Any connector that writes to Notion / Airtable / Mailchimp / MailerLite / HubSpot / etc. must first emit the payload to stdout via `scripts/dry-run-push.py` and wait for confirmation.
4. **Verify, do not trust.** Claude can hallucinate API endpoints, field names, package names. Check docs before invoking a new API.
5. **Do not share transcripts publicly** if they contain internal URLs, paths, draft content, or customer data.
6. **Disclosure for AI-generated visuals and audio.** When publishing, declare AI involvement per the brand's disclosure policy (set during `/brand-discover`).

---

## Architecture

This repo is organized by **role**. Each numbered folder represents one marketing function and contains a `CLAUDE.md` that defines the role's scope, inputs, workflow, and validation gates.

**Core** (always active):

| Folder | Role | When to use |
|---|---|---|
| `00-intel/` | — (confidential memory) | Meeting transcripts, internal/client/prospect intel — n8n-fed, never versioned |
| `01-brand/` | — (reference) | Single source of truth: identity, design system, voice, personas |
| `02-strategy/` | Head of communications | Editorial planning, pillars, KPIs; **central calendar in `02-strategy/calendar/calendar.md`** |
| `03-social-media/` | Social media manager | LinkedIn, Discord, WhatsApp, other activated channels |
| `04-email/` | Email marketing manager | Newsletters, promos, sales outreach, lead nurturing |
| `05-web-content/` | Web content lead | Landing pages, static HTML artifacts |
| `06-graphic-design/` | Art director | Visuals, carousels, infographics, AI imagery, **HTML presentations**, mail signatures |
| `07-events/` | Event marketing lead | Webinars, live sessions, gatherings, announcement plans |
| `09-seo/` | Blog & SEO manager | Long-form articles, keyword research, on-page optimization |
| `_sources/` | — (raw material) | Reports, market research — canonical source for published numbers |
| `_integrations/` | — (infrastructure) | Connector code, MCP config, cron |
| `_examples/` | — (starter corpus) | Fictional but realistic content to calibrate tone on day one |

**Optional modules** (inactive by default — enable via `/modules`, state in `.setup-completed.modules`; do not load their `CLAUDE.md` or propose their workflows while inactive):

| Folder | Module | Prerequisites |
|---|---|---|
| `08-video/` | `video` | macOS + Palmier Pro |
| `10-automatisations/` | `automatisations` | n8n instance |
| `11-reporting/` | `reporting` | ≥ 1 data source (GA4/GSC, Postiz, email tool) |
| `12-acquisition/` | `acquisition` | n8n instance (+ Apify for scraping) |
| — | `veille`, `publication-sociale`, `espace-client` | See `/modules` (feeds `00-intel/`, Postiz, FTP client space) |

### `00-intel/` subfolders (confidential — gitignored, see `00-intel/CLAUDE.md`)

| Subfolder | Content | Who feeds it |
|---|---|---|
| `inbox/` | Unprocessed drops (meeting transcripts, notes) | n8n workflow (module `automatisations`) or manual drop |
| `interne/` | Team meetings, internal decisions | Classified from `inbox/` |
| `clients/<name>/` | Everything about an existing client | Classified from `inbox/` |
| `prospects/<name>/` | Sales meetings, expressed needs | Classified from `inbox/` |

### `_sources/` subfolders

| Subfolder | Content | Who feeds it |
|---|---|---|
| `reports/` | Raw data, benchmarks, quantitative studies — the canonical source for any number you publish | Manual after each study |
| `research/` | Market watch: external articles, notes, competitor analysis | Manual drop, or automated feed (module `veille`) |

---

## Universal rules (apply to every role)

1. **Read the role's `CLAUDE.md` first** before producing any content in that folder.
2. **Defer to `01-brand/`** for voice, vocabulary, colors, typography.
3. **Follow the brand language configured at setup.** Monolingual or bilingual is a per-project decision, recorded in `.setup-completed`.
4. **No claim without a source.** Every factual statement must map to a number in `01-brand/messaging-framework.md` or a cited external reference.
5. **Never use banned vocabulary** listed in `01-brand/voice.md`.
6. **Check the central editorial calendar** (`02-strategy/calendar/calendar.md`) before proposing content, and update entry statuses (`idée → brouillon → à-valider → validé → publié`) as work progresses.
7. **Brand-check is mandatory** before delivery for any content in `03-`, `04-`, `05-`, `07-`, `08-`, `09-`, and for any HTML deck produced under `06-graphic-design/presentations/`. The PostToolUse hook fires a reminder; do not bypass it.
8. **Anti-repetition is file-based**: scan the calendar, per-channel archives (`examples/`, `editions/`, `articles/`) and the inventory files maintained by production skills before drafting. No external vector database is involved.
9. **Respect module state.** If a module is disabled in `.setup-completed.modules`, do not load its folder's `CLAUDE.md` or propose its workflows — point the user to `/modules`.

---

## Integrations — runtime state

Runtime configuration lives in `.setup-completed` (JSON). The wizard writes it at the end of `/start-copilot`. Example shape:

```json
{
  "version": "2.0.0",
  "company": "...",
  "language": "fr",
  "bilingual": false,
  "tools": {
    "editorial_calendar": { "name": "calendar-file", "enabled": true },
    "email_marketing":    { "name": "mailerlite", "enabled": true },
    "knowledge_base":     { "name": "outline", "enabled": false },
    "events_platform":    { "name": "none", "enabled": false },
    "crm":                { "name": "none", "enabled": false },
    "web_analytics":      { "name": "ga4-gsc", "enabled": true },
    "social_publishing":  { "name": "postiz", "enabled": false },
    "client_space_ftp":   { "name": "ftp", "enabled": false }
  },
  "modules": {
    "video":               { "enabled": false },
    "automatisations":     { "enabled": true },
    "reporting":           { "enabled": false },
    "acquisition":         { "enabled": false },
    "veille":              { "enabled": true },
    "publication-sociale": { "enabled": false },
    "espace-client":       { "enabled": false }
  },
  "features": {
    "image_generation": { "enabled": true, "model": "gemini-3-pro-image-preview" }
  }
}
```

See `docs/setup-completed.schema.json` for the full schema.

## Skills (in `.claude/skills/`)

| Skill | Role | Notes |
|---|---|---|
| `copilot-setup` | Shared wizard logic | Loaded by every `/start-copilot`, `/brand-discover`, `/tools-setup`, `/seed-corpus`, `/validate-setup`, `/health-check` |
| `brand-check` | Quality gate before delivery | Mandatory for content in production folders |
| `social-content` | LinkedIn, Discord, WhatsApp | Respects per-channel cadence and tone |
| `email` | Newsletter, promo, sales, nurture | Integrates with configured email tool |
| `copywriting` | Long-form web content | Landing pages, product pages |
| `copy-editing` | 7-pass review | Data / vocab / tone / clarity / structure / brand / format |
| `content-strategy` | Planning and cross-channel coordination | Pillar balance, cadence |
| `seo` | Blog, keyword research, on-page | Publishes per configured CMS |
| `event-marketing` | Event comm plans | D-60 to D+7 announcement waves |
| `image-generation` | Brand-compliant visuals via Gemini | Prompt auto-prefixed with brand style |
| `slides` | Editorial-grade HTML presentations | 1920×1080 frame, Playwright QA, clean PDF export |

**Rule**: always prefer this project's skills over generic skills from external plugins. They are tailored to this repo.

---

## Slash commands (in `.claude/commands/`)

| Command | Purpose |
|---|---|
| `/start-copilot` | Entry point of the wizard. Run once after cloning. Orchestrates the full setup. |
| `/brand-discover` | Analyze website + social + blog to propose a draft brand doctrine for human validation. |
| `/tools-setup` | Pick and configure tools per category. Regenerates role `CLAUDE.md` files based on choices. |
| `/seed-corpus` | Optional: ingest recent content into Qdrant (if enabled) for anti-repetition and retrieval. |
| `/connect-qdrant` | Optional: enable semantic memory. Callable at any time, not only during setup. |
| `/validate-setup` | Placeholder lint + sample generation + voice check. Writes `.setup-completed` on success. |
| `/health-check` | Ongoing: verify env vars, MCP servers, hook wiring, cron state. Run monthly. |

---

## Primary workflows

### Monthly newsletter
1. Marketing lead supplies topics for the month.
2. `email` skill queries Qdrant (if enabled) or reads `04-email/newsletter/editions/` to avoid repeats.
3. Draft lands in `04-email/newsletter/drafts/`.
4. Brand-check fires automatically via PostToolUse hook.
5. Human validates.
6. `scripts/dry-run-push.py --target <email-tool>` emits the payload for review.
7. On confirmation, the connector pushes to the email tool as a draft.
8. Scheduling and send are manual in the email tool UI.

### Social post
1. Read the editorial calendar (if configured) to pick topic and pillar.
2. `social-content` skill queries Qdrant / scans `examples/` for anti-repetition.
3. Draft in the appropriate channel folder.
4. Brand-check fires automatically.
5. Archive to `examples/` on publish.

### Full event
1. `event-marketing` skill builds the comm plan (D-60 → D+7).
2. Create editorial calendar entries with status "To do".
3. Draft content distributed across channel folders.
4. Brand-check at each delivery.
5. Create the event on the configured events platform via connector.
6. Coordinated cross-channel publication.

### Editorial deck (pitch / kickoff / readout)
1. Brief in `06-graphic-design/presentations/briefs/<slug>.md` (audience, decision, sources).
2. `slides` skill drafts a slide map (eyebrow + headline per slide, 18–24 slides) for human approval.
3. On sign-off, deck written to `06-graphic-design/presentations/decks/<slug>.html` from `templates/base.html` + `templates/components/`.
4. `python scripts/qa.py decks/<slug>.html` until "All slides clean".
5. Brand-check fires automatically.
6. Optional: `./scripts/export-pdf.sh decks/<slug>.html` for a PDF leave-behind, or push to a static host (see `presentations/docs/hosting.md`).

### Fresh content ingestion into Qdrant (if enabled)
- Manual: `python3 _integrations/qdrant/sync.py --source <name>`
- Automated: weekly launchd job (Sunday 22:00) running `sync.py --all` + drift audit.

---

## When Qdrant is disabled

The system operates without Qdrant. Each skill's `CLAUDE.md` documents its file-based fallback:
- `brand-check` reads `01-brand/voice.md` directly; anti-repetition check is skipped with an explicit note in the report.
- `social-content` reads the last 5 files in `<channel>/examples/` to calibrate tone.
- `email` reads the last 3 editions in `newsletter/editions/`.

Enable Qdrant later via `/connect-qdrant` — takes 5 minutes if you have a Qdrant Cloud URL + Google AI key.

---

## Visual identity quick reference

Once the wizard has run, values appear here. Before that, treat every field below as a placeholder to be filled by `/brand-discover`.

- **Primary font**: `{{BRAND_FONT_PRIMARY}}`
- **Primary color**: `{{BRAND_COLOR_PRIMARY}}`
- **Accent color**: `{{BRAND_COLOR_ACCENT}}`
- **Dark**: `{{BRAND_COLOR_DARK}}`
- **Light**: `{{BRAND_COLOR_LIGHT}}`
- **Signature gradient**: `{{BRAND_GRADIENT}}`
- **Border-radius**: `{{BRAND_BORDER_RADIUS}}`
- **Illustration style**: `{{BRAND_ILLUSTRATION_STYLE}}`
- **Banned visual tropes**: `{{BRAND_BANNED_VISUALS}}`
- **Full style guide**: `01-brand/style-guide.md`
