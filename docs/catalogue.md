# Catalogue du cockpit

Ce fichier rassemble les catalogues sortis du `CLAUDE.md` racine, qui se charge à chaque session et doit rester court : la carte des dossiers, l'exemple de `.setup-completed`, les skills par fonction, les agents et les commandes. Le `CLAUDE.md` garde les consignes (détection du setup, rôle et routage, sécurité, règles universelles, workflows), le module vidéo (tableau des skills et ligne de l'agent `video-reviewer`) et le tableau des contrôles par script.

## Architecture

**Core** (always active):

| Folder | Role | When to use |
|---|---|---|
| `00-intel/` | — (confidential memory) | Meeting transcripts, internal/client/prospect/partner intel — fed by n8n or by the Google Drive transcripts feed (`_integrations/drive-transcripts/`), never versioned |
| `01-brand/` | — (reference) | Single source of truth: identity, design system, voice, personas |
| `02-strategy/` | Head of strategy | Objectives cascade, campaign briefs, calendar, KPIs — **central calendar in `02-strategy/calendar/calendar.md`** |
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
| `08-video/` | `video` | ffmpeg, Node 22; HyperFrames plugin (`hyperframes@hyperframes`) installed by `/modules` (optional: whisper, Manim, documentary corpus dependencies) |
| `10-automatisations/` | `automatisations` | n8n instance |
| `11-reporting/` | `reporting` | ≥ 1 data source (GA4/GSC, Postiz, email tool) |
| `12-acquisition/` | `acquisition` | n8n instance (+ Apify for scraping) |
| `14-print/` | `print` | Chrome or Chromium, Ghostscript ≥ 10, Python (PyMuPDF, Pillow, numpy), paper ICC profile in `14-print/icc/` |
| — | `veille`, `publication-sociale`, `espace-client` | See `/modules` (feeds `00-intel/`, Postiz, FTP client space) |

### `00-intel/` subfolders (confidential — gitignored, see `00-intel/CLAUDE.md`)

| Subfolder | Content | Who feeds it |
|---|---|---|
| `inbox/` | Unprocessed drops (meeting transcripts, notes) | n8n workflow (module `automatisations`), Drive transcripts feed (`scripts/sync-intel.py`, Monday routine `intel-hebdo`) or manual drop |
| `interne/` | Team meetings, internal decisions | Classified from `inbox/` |
| `clients/<name>/` | Everything about an existing client | Classified from `inbox/` |
| `prospects/<name>/` | Sales meetings, expressed needs | Classified from `inbox/` |
| `partenaires/<name>/` | Partners working with the company without buying from it | Classified from `inbox/` |
| `radar/` | Weekly comms radars, intel routine log | Monday routines `intel-hebdo` and `radar-com` |

### `_sources/` subfolders

| Subfolder | Content | Who feeds it |
|---|---|---|
| `reports/` | Raw data, benchmarks, quantitative studies — the canonical source for any number you publish | Manual after each study |
| `research/` | Market watch: external articles, notes, competitor analysis | Manual drop, or automated feed (module `veille`) |

## Exemple de `.setup-completed`

Forme d'exemple du fichier d'état décrit dans `CLAUDE.md`, section « Integrations — runtime state » ; schéma complet : `docs/setup-completed.schema.json`.

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
    "espace-client":       { "enabled": false },
    "print":               { "enabled": false }
  },
  "features": {
    "image_generation": { "enabled": true, "model": "gemini-nano-banana-2.1" }
  }
}
```

## Skills (in `.claude/skills/`)

### Wizard & infrastructure

| Skill | Role | Notes |
|---|---|---|
| `cockpit-setup` | Shared wizard logic | Loaded by every `/start-cockpit`, `/brand-discover`, `/tools-setup`, `/modules`, `/validate-setup`, `/health-check` |
| `sync-template` / `backport-to-template` | Template ↔ fork Git flow | Update from upstream / contribute back sanitized |
| `n8n-builder` | End-to-end n8n workflow creation | 5-phase method: libraries → plan → build (MCP) → QA → REX |
| `n8n-audit` | Review an existing n8n workflow | Against module conventions (architecture, errors, naming, vault) |
| `inventory` | Deliverables index | Maintains `_templates/inventory.md` (anti-repetition) via `scripts/build-inventory.py` |

### Quality gates & review

| Skill | Role | Notes |
|---|---|---|
| `brand-check` | Quality gate before delivery | Mandatory for content in production folders; step 0 = `scripts/lint-brand.py`, feeds `01-brand/exemples-rejetes.md` |
| `strategy-challenger` | Devil's advocate on a strategy | Stress-tests a positioning, offer, funnel or campaign before commit; used by `02-strategy`, produces a critique not a plan |
| `copy-editing` | 7-pass review | Data / vocab / tone / clarity / structure / brand / format |
| `humanize-writing` | 8-pass anti-AI-detection rewrite | Curative pass for text that "sounds AI"; invoked by `copy-editing` as final pass |
| `accessibility-web` | WCAG 2.2 AA reference | Load before building/reviewing any HTML deliverable; automated review delegated to agent `a11y-auditor` |

### Editorial production

| Skill | Role | Notes |
|---|---|---|
| `social-content` | LinkedIn, Discord, WhatsApp | Respects per-channel cadence and tone |
| `email` | Newsletter, promo, sales, nurture | Integrates with configured email tool |
| `email-deliverability` | Email knowledge base | SPF/DKIM/DMARC, compliance, dark-mode design, benchmarks — consultative, produces nothing itself |
| `copywriting` | Long-form web content | Landing pages, product pages |
| `blog-engine` | End-to-end article production | Research → draft → SEO validation → quality score ≥ 90/100; fact-checking with source fetch |
| `seo` | Blog, keyword research, on-page, AEO | Publishes per configured CMS; delegates analysis to `seo-audit` / `seo-schema` / `seo-geo` / `seo-cluster` |
| `content-strategy` | Planning and cross-channel coordination | Pillar balance, cadence |
| `event-marketing` | Event comm plans | D-60 to D+7 announcement waves |
| `translation` | Verified multi-agent translation pipeline | Structure preservation, brand glossary, anti-fabrication review |
| `veille-strategy` | Multi-level market watch | Feeds the editorial calendar with sourced ideas |

### Web & conversion (CRO)

| Skill | Role | Notes |
|---|---|---|
| `landing-page` | Conversion landing pages, end-to-end playbook | 8 phases: doctrine and real material → one-salvo framing → 2-3 directions → spec with final copy → shared charter before parallel work → parallel build by disjoint files → show, listen, apply → measured QA + 4 parallel reviews + one arbitrated fix wave → delivery. Data template (gallery) or bespoke page. Six `landing-*` agents, `/new-landing`, QA `05-web-content/scripts/qa-landing.py` |
| `lead-magnet` | Lead magnets (guide, calculator, quiz…) | Always shipped with the full capture circuit (page → form → automation → nurturing) |
| `cro-page` | Page conversion audit | 7-dimension analysis, prioritized recommendations; orchestrated by `landing-page` |
| `cro-form` | Form optimization | Field pruning, labels, errors, completion rate; orchestrated by `landing-page` / `lead-magnet` |
| `cro-popup` | Popups, modals, banners | Triggers, frequency, RGPD compliance — only on explicit request |
| `cro-pricing` | Pricing strategy & pricing page | Packaging, Good-Better-Best tiers, price psychology |

### Design & visuals

| Skill | Role | Notes |
|---|---|---|
| `image-generation` | Brand-compliant visuals via Gemini | Prompt auto-prefixed with brand style; check `01-brand/assets/` first |
| `slides` | Editorial-grade HTML presentations | 1920×1080 frame, 120-layout library, Playwright QA, clean PDF export; engine vendored from slides-agent |
| `carousel` | LinkedIn carousels (PDF 1080×1350) | Strict type/spacing scales, export pipeline |
| `brandkit` | Brand boards & identity decks | Express the existing brand, or draft an identity proposal for a prospect |
| `design-direction` | Distinctive art direction | Deliberate aesthetic choices for new pages — upstream of `design-system` |
| `design-system` | Web design system generation | Semantic palette, type pairing, CSS tokens — always constrained by `01-brand` tokens |
| `design-review` | UI review before delivery | Brand conformance, WCAG, responsive, perceived performance |
| `design-taste` | Anti-slop execution protocol | Parametric variance/motion/density cursors, GSAP skeletons, pre-flight check |
| `design-redesign` | Audit & modernize an existing site/page | Detects generic-AI patterns, targeted fixes by impact order |

### Video (module `video`)

Tableau tenu dans `CLAUDE.md`, section « Skills », avec la ligne de l'agent `video-reviewer` : `scripts/tests/test_video_module.py` (`test_claude_md_racine`) y vérifie la présence des skills et des contrôles du studio vidéo.

### Print (module `print`)

| Skill | Role | Notes |
|---|---|---|
| `print` | Anything that goes to a printer (booklet, brochure, programme, card, poster, roll-up) | Flatplan → sourced facts → HTML/CSS on a grid → opaque plate for overlays → PDF/X-4 CMYK chain (`14-print/lib/`) → `verify.py` / `qa.py` → agents `print-preflight` + `print-editorial` → paper proof; ordering stays human |

### SEO analysis (support of skill `seo`)

| Skill | Role | Notes |
|---|---|---|
| `seo-audit` | Site or single-page SEO audit | Health score + prioritized action plan in `09-seo/audits/` |
| `seo-schema` | Schema.org structured data | Detect, validate, generate JSON-LD; knows active/deprecated Google types |
| `seo-geo` | AI answer-engine visibility (GEO/AEO) | AI crawler access, passage citability, brand mentions |
| `seo-cluster` | SERP-overlap topic clustering | Hub-and-spoke architecture, internal link matrix |

### Acquisition, data & reporting (modules)

| Skill | Role | Notes |
|---|---|---|
| `sea-google-ads` | Google Ads advisory (module `acquisition`) | Read-only MCP account audit, prioritized optimization plan; delegates numbers to agent `sea-analyst` |
| `ads-audit` | Multi-platform paid media audit | Google/Meta/LinkedIn Ads grids, health score 0-100, quick wins |
| `scraping` | Apify-based scraping | Benchmarks, social audits, watch data |
| `performance-report` | Monthly performance snapshot (module `reporting`) | Feeds the `11-reporting` dashboard; analysis by agent `performance-analyst` |
| `deploy-reporting` | Publishes the dashboard to the client space by FTP (module `reporting`) | Run by hand only (`/deploy-reporting`): file list and destination first, explicit approval, then upload |

## Agents (in `.claude/agents/`)

Sub-agents dispatched (mostly) by skills — they run in parallel and return structured reports.

| Agent | Role | Dispatched by |
|---|---|---|
| `brand-guardian` | Adversarial brand-conformance review of a major deliverable (deck, landing, campaign) | On demand — complements `brand-check` without replacing it |
| `qa-visuel` | Playwright QA of visual HTML deliverables (overflow, font minima, contrast, folios) | Skills `slides` / `carousel`, before PDF export |
| `a11y-auditor` | WCAG 2.2 AA audit (axe-core + manual keyboard/focus/modal checks) | Before delivery of any web deliverable — complements `qa-visuel` |
| `performance-analyst` | Analyzes the monthly `data.json` snapshot: trends, anomalies, 3-5 recommendations | Skill `performance-report` |
| `sea-analyst` | Reads Google Ads account data via MCP (read-only), returns quantified findings | Skill `sea-google-ads` |
| `seo-technical` | Technical SEO: crawlability, indexation, canonicals, CWV, JS rendering | Skill `seo-audit` |
| `seo-content` | Content quality: E-E-A-T, depth, thin content, AI citability | Skills `seo-audit` / `seo` |
| `seo-google` | Google data: CrUX, Search Console, GA4 (only if GA4/GSC coupling is active) | Skills `seo-audit` / `seo` |
| `n8n-debugger` | Diagnoses failed n8n executions (read-only) against known error patterns | `n8n-builder`, module `automatisations` |
| `veille-analyst` | Deep web research on ONE watch level, sourced and dated signals | Skill `veille-strategy` (one per level, in parallel) |
| `print-preflight` | Prepress audit of the final PDF: boxes, colour space, ink coverage, effective image resolution, rules, minimum sizes, residual transparency, QR codes | Skill `print`, before any order and after each rebuild |
| `print-editorial` | Spread-by-spread layout review of a print piece: grid, hierarchy, measure, rhythm, white space, widows | Skill `print`, alongside `print-preflight` |
| `landing-researcher` | Benchmark of converting pages + visual research from public galleries, consolidated in the landing's `pilotage/research-notes.md`; codes nothing | Skill `landing-page`, phase 0, in the background |
| `landing-section-builder` | Builds or fixes one landing section (or a fix batch) in the files it is given only; several run in parallel on disjoint fragments, never commits | Skill `landing-page`, phases 4-7 |
| `landing-reviewer-design` | Read-only web-design coherence review: headings, rhythm, materials, type, motion, responsive, buttons | Skill `landing-page`, phase 7 (in parallel) |
| `landing-reviewer-brand` | Read-only brand review against `01-brand/` (voice, anti-AI, tokens, proof, audience, AI disclosure, rights), runs `lint-brand.py` | Skill `landing-page`, phase 7 (in parallel) |
| `landing-reviewer-cro` | Read-only conversion review: narrative vs objections, CTA inventory, conversion block, honest urgency, proof, measurement | Skill `landing-page`, phase 7 (in parallel) |
| `landing-reviewer-a11y` | Read-only WCAG 2.2 AA review in 14 points, grounded on the `qa-landing.py` measures; `a11y-auditor` stays the delivery gate | Skill `landing-page`, phase 7 (in parallel) |
| `video-art-director` | End-to-end AI visual production from a brief: model choice, prompts, image → upscale → image-to-video → voice chain, iterations (module `video`) | On demand, for a deliverable that chains several models |
| `video-model-scout` | Refreshes the knowledge of the generation catalogue (new models, versions, costs, parameters) | Skill `video-generation`, to update its dated model notes |

La ligne de `video-reviewer` reste dans `CLAUDE.md`, sous le tableau des skills vidéo : le même test y cherche `brand-frame.py --check`.

## Slash commands (in `.claude/commands/`)

| Command | Purpose |
|---|---|
| `/start-cockpit` | Entry point of the wizard. Run once after cloning. Orchestrates the full setup. |
| `/brand-discover` | Analyze website + social + blog to propose a draft brand doctrine for human validation. |
| `/tools-setup` | Pick and configure tools per category. Regenerates role `CLAUDE.md` files based on choices. |
| `/modules` | Enable/disable optional modules (video, automatisations, reporting, acquisition, veille, publication-sociale, espace-client, print). |
| `/validate-setup` | Placeholder lint + sample generation + voice check. Writes `.setup-completed` on success. |
| `/health-check` | Ongoing: verify env vars, MCP servers, hook wiring, cron state. Run monthly. |
| `/new-landing` | Produce a conversion landing page with the `landing-page` playbook, from framing to a QA'd static HTML page. |
