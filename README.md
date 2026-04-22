# Marketing Copilot Template

A role-based AI marketing copilot you clone once per company, run a wizard against, and use every day through Claude Code. English-only repo; produces content in any language configured at setup.

**Recommended model**: Claude Sonnet 4.6. The brand doctrine and per-role `CLAUDE.md` files provide enough context that Sonnet handles strategic reasoning, brand-check, and copy-editing at quality. Opus is overkill for most sessions; Haiku is a reasonable fallback for short, routine tasks (single-post drafting, quick replies).

---

## Before you start (disclaimer)

This template produces an **operational framework**, not a polished marketing output on day one. A qualitative result requires:

- A brand universe (voice, colors, personas, proof points) — the wizard helps you shape this
- At least some public content to calibrate against (website + a few recent posts/articles) — without it, the "voice" the copilot captures will be generic
- Your real tools wired in (email platform, editorial calendar, CMS) — without them, the copilot drafts but you publish manually

**Security non-negotiables** (full rules in [`SECURITY.md`](SECURITY.md)):

- Never paste API keys in chat. Secrets live in `.env` only (gitignored).
- Dry-run before any production push (`scripts/dry-run-push.py`).
- Scope Bash permissions narrowly; don't grant broad `rm:*` or `git push --force:*`.
- Verify API endpoints and package names — Claude can hallucinate them.
- Don't share transcripts publicly if they contain internal URLs, drafts, or customer data.

---

## Quickstart

```bash
# 1. Clone the template under a project name that makes sense for you
git clone <this-repo> my-company-copilot
cd my-company-copilot

# 2. Install Python deps
python3 -m pip install pyyaml python-dotenv requests
# Optional, only if you'll enable Qdrant:
# python3 -m pip install qdrant-client google-genai mcp

# 3. Create .env from the template
cp .env.example .env

# 4. Open in Claude Code on Sonnet 4.6 (or Opus if you prefer)
claude .

# 5. Launch the wizard
/start-copilot
```

The wizard takes 30-60 minutes depending on how much public material you have. It walks you through brand discovery, tool setup, optional Qdrant activation, and a validation sample before writing `.setup-completed`.

---

## Who this is for

**Good fit**:
- SaaS, B2B, consultancies, collectives, agencies with a clear brand voice
- Teams publishing 5+ pieces of content per week across 2+ channels
- Organizations with proprietary data (benchmarks, reports, case studies) to surface
- Any team that wants deterministic brand compliance, not hopeful compliance

**Poor fit**:
- Mass-market B2C with no brand doctrine
- Teams without existing brand guidelines (build them first, then come back)
- Organizations that can't keep an API key in a local `.env` for operational reasons

---

## How it works

### The wizard (run once, resumable)

| Command | Purpose |
|---|---|
| `/start-copilot` | Entry point. Orchestrates the full setup. |
| `/brand-discover` | Analyze your website + recent posts/articles; propose a design system, voice, and personas; validate section by section; write to `01-brand/`. |
| `/tools-setup` | Pick tools per category (email, CRM, editorial calendar, events, KB). Regenerate role `CLAUDE.md` with your real tool names. Update `.env.example`. |
| `/seed-corpus` | Optional. Ingest recent content into Qdrant or into archive folders so the copilot starts with real memory. |
| `/connect-qdrant` | Optional. Enable semantic memory. Callable any time. |
| `/validate-setup` | Placeholder lint + sample generation + voice check. Writes `.setup-completed` on approval. |
| `/health-check` | Ongoing. Verify env vars, MCP servers, hook wiring, cron. Run monthly. |

### The roles (9 folders, one `CLAUDE.md` each)

Each numbered folder represents one marketing function. Claude Code loads the matching `CLAUDE.md` when you work in that folder.

```
01-brand/                ← single source of truth: voice, style-guide, personas, messaging
02-strategy/             ← editorial planning, pillars, KPIs
03-social-media/         ← LinkedIn, Discord, WhatsApp
04-email/                ← newsletters, promos, sales outreach, nurturing
05-web-content/          ← landing pages, standalone HTML
06-graphic-design/       ← visuals, AI image generation
07-events/               ← webinars, launches, comm plans
08-mail-signatures/      ← HTML signatures per team member
09-blog-seo/             ← long-form articles, keyword research
```

### The skills (`.claude/skills/`)

`brand-check`, `social-content`, `email`, `copywriting`, `copy-editing`, `content-strategy`, `seo`, `event-marketing`, `image-generation`. Each skill has an English `SKILL.md` with preflight, workflow, and Qdrant-conditional branches. `brand-check` fires automatically via a PostToolUse hook after any write in production folders.

### Semantic memory (optional — volume-dependent)

Qdrant is **optional**. Below ~50 published pieces per month, the file-based fallback (reading `01-brand/` and recent archives directly) is fast enough and zero-dependency. Above that threshold, Qdrant starts to pay off: anti-repetition across months of accumulated content, semantic retrieval from the brand doctrine in 500 ms, cross-channel consistency checks. A small team publishing a weekly newsletter and a handful of LinkedIn posts doesn't need it. A consultancy producing 2 posts/day across channels plus a monthly newsletter and weekly articles will feel the difference.

Enable any time with `/connect-qdrant`. Disable by editing `.setup-completed.features.qdrant.enabled`.

### Tool agnosticism (per-tool status below)

<!-- tool-status:start -->
| Category | Default options | Ready connectors |
|---|---|---|
| Editorial calendar | Notion, Airtable, Trello, ClickUp, Google Sheets, custom, none | **Notion** ✅ — others are stubs |
| Email marketing | MailerLite, Mailchimp, Resend, Brevo, ConvertKit, custom, none | **MailerLite** ✅, **Mailchimp** ✅ — others are stubs |
| Knowledge base | Outline, Notion, Confluence, GitBook, custom, none | **Outline** ✅, **Notion** ✅ — others are stubs |
| Events platform | Livestorm, Zoom, Riverside, Google Meet, custom, none | All stubs (v0.2.1 roadmap) |
| CRM | HubSpot, Pipedrive, Odoo, Notion, Airtable, custom, none | All stubs |
| Semantic memory | Qdrant (+ Google AI for embeddings) | **Qdrant** ✅ |
| Image generation | Gemini `gemini-3-pro-image-preview` | **Gemini** ✅ |
| Web analytics | GA4, Plausible, Fathom, custom, none | All stubs |
| Social scheduler | Buffer, Hootsuite, Later, Typefully, custom, none | All stubs |
<!-- tool-status:end -->

For a stub, `/tools-setup` scaffolds a TODO file at `_integrations/connectors/<tool>.py`. Implementation is typically an hour. See `_integrations/CONTRIBUTING.md` for the connector contract.

---

## Philosophy

Three principles drive the design (full detail in [`docs/architecture.md`](docs/architecture.md)):

1. **Brand as truth** — `01-brand/` is the source. Everything defers to it. Contradictions are flagged before publication.
2. **Retrieval-first when it pays** — Qdrant is recommended at scale, skipped at lower volume. Skills handle both paths.
3. **Hook-enforced** — The harness enforces the workflow, not Claude's willpower. PostToolUse fires brand-check automatically.

---

## What this is not

- It is **not** a replacement for your judgment on what to publish.
- It is **not** a substitute for a brand strategy. It encodes the strategy; it doesn't invent it.
- It is **not** a zero-dependency system. Claude Code is required; Google AI + Qdrant are recommended at scale.
- It is **not** a content-marketing plug-and-play. Without a voice doctrine and real corpus, the output will read generic.

---

## Status

**Version 0.2.0 — alpha.**

- Wizard-driven setup replaces the v0.1 monolithic interview.
- 9 role folders, 9 skills, Qdrant pipeline, Gemini image generation, brand-check hook.
- 4 ready connectors (Notion, Outline, MailerLite, Mailchimp). Others are stubs — contributions welcome.

See [`CHANGELOG.md`](CHANGELOG.md) for the full version history.

---

## Extending your copy

This is a template to clone and adapt, not an open-source project soliciting PRs. Once you've run the wizard, your copy is yours — diverge freely.

Common extensions you'll likely build in your own copy:

- **New connectors** for tools the template doesn't ship ready (Airtable, Resend, Brevo, Livestorm, HubSpot, your in-house CMS). Start from `docs/tools.json` and any existing connector in `_integrations/connectors/` as a pattern.
- **Linux/WSL cron** equivalents if you're not on macOS (the shipped cron uses launchd; systemd or crontab maps cleanly).
- **Domain-specific skills** — a PR newsletter generator, a case-study builder, a recurring report ghostwriter, a podcast show-notes skill. Place them in `.claude/skills/<name>/SKILL.md`.
- **New enrichers** — pillar classifier, sentiment, tonality match — wired in `_integrations/qdrant/config.yaml`.

If you build something reusable and want to share it back to this template upstream, open an issue or a discussion on the source repo — no pressure, no expectation.

---

## License

MIT. See [`LICENSE`](LICENSE). Clone, fork, adapt, ship.
