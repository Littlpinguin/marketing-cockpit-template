# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

## [Unreleased]

**Added.** 4 web-animation skills vendored from [claudedesignskills](https://github.com/freshtechbro/claudedesignskills) (MIT): `animation-gsap` (GSAP + ScrollTrigger), `animation-animejs`, `animation-lottie`, `animation-scroll-reveal` (AOS & co) — SKILL.md + references only, no scripts (see `docs/vendored-animation.md` for scope, field-tested guardrails and re-sync procedure). Skill count: 45 → 49.

**Added.** `strategy-challenger` skill — devil's advocate that stress-tests a positioning, offer, funnel or campaign against 13 marketing frameworks turned into challenge questions (`SKILL.md` + `frameworks.md`). Wired into the root routing table and skills catalogue, and into the `02-strategy` role (live `CLAUDE.md` + `_templates/role-claudemd/02-strategy.md`): challenges a campaign brief before human validation. Skill count: 49 → 50.

## [2.0.0] — The complete AI marketing department (major rework)

**Core.** Brand doctrine injected as step 0 in every production skill (anti-AI writing + anti-generic design doctrines), central editorial calendar with validation statuses, `00-intel/` live context (n8n-fed meeting transcripts, gitignored), strategy cascade (objectives → briefs → personas → journey), marketing-director routing at the root.

**43 internal skills, 9 agents.** Vendored and adapted from the best MIT/Apache community sources (claude-seo, ui-ux-pro-max, taste-skill, frontend-design, claude-ads, claude-blog, and more — see `docs/vendored-*.md` for full attribution), plus battle-tested production skills (slides, carousel, image-generation) and 2026 state-of-the-art rules (sourced, in `docs/etat-de-lart/`).

**7 optional modules** via `/modules`: video (Palmier Pro), n8n automations, client-site performance dashboard (FTP + access code), acquisition (Lemlist MCP + Google Ads read-only MCP), market watch, Postiz publishing, client space.

**Demos (fictional brand “Meridian Conseil”).** 52-layout slide catalogue with fullscreen mode and brand-pattern hooks, 10 landing pages + 10 interactive lead magnets (tested), 4-month dashboard demo that works on double-click.

**Removed.** Qdrant (file-based anti-repetition only), `/seed-corpus`, `/connect-qdrant`.

**Wizard.** `/modules`, strategy interview in `/brand-discover`, data-privacy gate on sensitive connectors, extended `/health-check`, SessionStart hook.

## [0.3.1] — Wizard / slides plumbing fixes (post-0.3.0 audit)

### Fixed
- **`/brand-discover` now fills `06-graphic-design/presentations/tokens.css`** alongside the four `01-brand/` files. Without this, `/validate-setup`'s placeholder linter would fail on unfilled slide tokens, blocking every setup. The substitution uses the same colour and font placeholders as `01-brand/style-guide.md` — no extra wizard inputs required.
- **`tokens.css` refactored to derive `_deep`/`_soft` colour variants and the mono font family from values the wizard already captures.** Variants resolve at runtime via `color-mix(in srgb, ...)`; `--font-mono` falls back to `BRAND_FONT_SECONDARY` then to the system mono stack. Removes 10 placeholders that v0.3.0 introduced but never wired to the wizard.
- **`docs/placeholders.json`** cleaned up — only the placeholders the wizard actually fills are listed in `visual_identity`.
- **`/tools-setup`** copy updated from "9 role folders" to "8" to reflect the v0.3.0 consolidation.
- **`scripts/qa.py`** docstring synced with the new `decks/` folder convention.

## [0.3.0] — Editorial HTML decks + role consolidation

### Added
- **`slides` skill** at `.claude/skills/slides/SKILL.md` — generates editorial-grade standalone HTML presentations (Monocle / Bloomberg viz / MIT Tech Review print quality bar). 1920×1080 fixed frame scaled responsively, triple navigation (drag-bar + overview panel `O` + quick-jump), Playwright QA mandatory before delivery, clean PDF export via canvas-rasterised gradient text.
- **`06-graphic-design/presentations/`** — full deck-authoring sub-area with `templates/base.html` (deck skeleton), `templates/components.md` (paste-ready slide layouts catalogue), `tokens.css` (slide-specific CSS variables derived from `01-brand/style-guide.md`), `scripts/qa.py`, `scripts/serve.sh`, `scripts/export-pdf.sh`, `scripts/export_pdf.py`, plus `docs/design-system.md` / `docs/hosting.md` / `docs/pdf-export.md`.
- **Brand-check gate extended** to HTML decks. The PostToolUse hook now fires on writes under `06-graphic-design/presentations/decks/` in addition to the existing production folders.
- **"Editorial deck" workflow** added to the root orchestrator's "Primary workflows" section.

### Changed
- **Role consolidation under `06-graphic-design/`.** The role now covers three sub-areas: visuals (existing), HTML presentations (new), mail signatures (moved from `08-mail-signatures/`). Single `CLAUDE.md` covers all three; sub-area-specific docs live in `06-graphic-design/presentations/docs/` and `06-graphic-design/mail-signatures/README.md`. Cross-area rules (banned visuals, palette discipline, AI disclosure) apply uniformly.
- **`06-graphic-design/CLAUDE.md`** rewritten to reflect the three-sub-area scope, with quick references to the deck workflow (`./scripts/serve.sh`, `./scripts/export-pdf.sh`, `python scripts/qa.py`).
- **Root `CLAUDE.md`** updated: role table goes from 9 to 8 entries (08 folded into 06); skill table gains the `slides` row; brand-check rule mentions HTML decks.

### Removed
- **`08-mail-signatures/`** as a top-level role folder. Content moved verbatim into `06-graphic-design/mail-signatures/README.md` (relative paths updated to reflect the new depth). Numbering keeps a gap (no renumbering of `09-blog-seo/`).
- `_templates/role-claudemd/08-mail-signatures.md` — superseded by the consolidated `06-graphic-design.md` template.

## [0.2.0] — Wizard-driven setup

### Added
- **Slash-command wizard** (`.claude/commands/`) replaces the v0.1 monolithic interview. Entry point: `/start-copilot`. Sub-commands: `/brand-discover`, `/tools-setup`, `/seed-corpus`, `/connect-qdrant`, `/validate-setup`, `/health-check`.
- **Shared wizard skill** at `.claude/skills/copilot-setup/SKILL.md` — central logic (placeholder lint, tool registry, security rules, `.setup-completed` schema) loaded by every wizard command.
- **Brand discovery** from public signals: the wizard fetches the company website, up to 5 recent blog posts and 5-10 social posts the user links, then proposes a draft design system, voice, vocabulary, personas. Everything is reviewed section-by-section before being written to `01-brand/`.
- **Tool-aware generation**: role `CLAUDE.md` files are rendered from `_templates/role-claudemd/` based on actual tools selected in `/tools-setup`. No more `{{EDITORIAL_CALENDAR_TOOL}}` leaking into operational docs.
- **Tool-status board** auto-generated in `README.md` from `docs/tools.json`. Connectors marked ✅ Ready / 🟠 Stub / ❌ Not supported.
- **Security disclaimer** (`SECURITY.md`) — explicit rules for secrets, permissions, dry-run mode, AI hallucinations, and disclosure.
- **Starter corpus** in `_examples/` — 5 LinkedIn posts, 2 newsletters, 1 blog article for a fictional "Acme SaaS", reusable as Qdrant seed when the user has no corpus yet.
- **Placeholder linter** (`scripts/lint-placeholders.py`) — blocks setup lockdown if any `{{*}}` remain in operational files.
- **`.setup-completed` schema** — documented JSON shape at `docs/setup-completed.schema.json` with validator.
- **Dry-run mode** for all outbound connectors (`scripts/dry-run-push.py`) — preview outgoing payloads before enabling production push.

### Changed
- **English throughout.** All operational templates, skills, prompts, and docs are now in English. Content produced by the copilot follows the brand language configured at setup time (single language or bilingual).
- **Qdrant repositioned** from "strongly recommended" to "scale-dependent." Below ~50 published pieces per month across all channels, the file-based fallback works fine. Each skill now has a documented `if qdrant_enabled / else` branch.
- Skills moved from `.agents/skills/` to `.claude/skills/` to align with Claude Code conventions.
- Role `CLAUDE.md` files are now templates in `_templates/role-claudemd/`. The instances in `01-brand/`, `02-strategy/`, etc. are generated by `/tools-setup` and contain no placeholders post-wizard.

### Removed
- `_bootstrap/interview.md` and `_bootstrap/questions.md` — archived to `.setup-archive/v0.1/`.
- `README.fr.md` — archived. Language of the operational copilot is chosen at wizard time; the repo itself is English-only.
- `SETUP.md` — replaced by the wizard and the new `README.md` quickstart.

## [0.1.0] — 2026-04-15

### Added
- Initial template release
- 9 role folders (brand, strategy, social media, email, web content, graphic design, events, mail signatures, blog & SEO) each with its CLAUDE.md template
- 8 generic marketing skills (brand-check, social-content, email, copywriting, copy-editing, content-strategy, seo, event-marketing)
- Qdrant semantic memory pipeline (sync.py, utils.py, init_collection.py, mcp_server.py) with Gemini embedding-001 (3072 dim)
- 4 source connectors: filesystem, notion, outline, transcripts
- 5 enrichers: hash, summary, entities, claims, meeting
- Brand check hook (PostToolUse) that forces brand validation before content delivery
- Weekly multi-source cron with drift detection (macOS launchd)
- Bootstrap interview in 5 phases (discovery, identity, personas, functionalities, skills) with website auto-analysis
- Tools-agnostic design: functionalities first, tools second (Notion / Airtable / MailerLite / Mailchimp / Outline / Confluence / etc.)
- MIT License
