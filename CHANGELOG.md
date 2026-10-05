# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

## [Unreleased]

**Fixed.** `01-brand/checklist-pre-composition.md`, `01-brand/design-anti-generique.md` and the in-place v2 `01-brand/personas.md` were never versioned (caught by the `01-brand/*.md` ignore rule), although 28 skills load the first two at step 0 and `/brand-discover` edits the third in place. They now ship with the template.

**Fixed.** SessionStart hook brand snapshot, generalized from a client deployment: the tone line now comes from the `Voice position` section of `01-brand/voice.md` (the broad `voice`/`ton` keywords matched the file's H1 and surfaced its intro sentence instead of the brand's voice), and the mission line from the `Central message` of `01-brand/messaging-framework.md`, which no keyword matched before. Inside a section, a blockquoted value is preferred over the filling instruction above it, and the search stops at the next heading.

**Changed.** `.gitignore` ignores every `.env.*` variant (`.env.production`, `.env.backup`…) except `.env.example`, plus `Thumbs.db`. Role `05-web-content` (live `CLAUDE.md` + `_templates/role-claudemd/`): a deployment ends with a check of the live page (HTTP 200, `robots` tag matching the brief, browser rendering identical to the validated local version). Role `07-events` (same two files): facts taken from automatic meeting transcripts are cross-checked before reuse, and published event comms missing from the local channel archives are pulled back from the calendar tool so anti-repetition reads what actually went out.

**Added.** Google Drive transcripts feed for `00-intel/`, generalized from a client deployment. For teams on Google Workspace whose meetings are noted by Gemini in Meet: an Apps Script exports the shared drive's Google Docs to Markdown every Monday (Google Docs are only 184-byte `.gdoc` shortcuts once mounted by Drive for desktop), `scripts/sync-intel.py` copies the new exports into `00-intel/inbox/`, and two Monday routines take over — `intel-hebdo` (sync + classification with a synthesis header, `signal`/`angles`/`sensible` frontmatter, parallel sub-agents) and `radar-com` (urgent facts first, 3-7 comms topics, newsletter brief on the first Monday of the month). Strictly incremental: 30 days of history on the very first pass, then only Docs created or modified since the previous pass, and already-imported files are recognized by name without being opened (so never re-downloaded). Candidate interviews and accounting meetings never leave the shared drive; empty Gemini notes ("A summary wasn't produced…", created when the meeting language differs from Meet's setting) are filtered on content, never on language. New `00-intel/partenaires/` category and `00-intel/radar/` output folder. Three install-time markers: `INTEL_DRIVE_ID`, `INTEL_DRIVE_ACCOUNT`, `INTEL_REPORT_EMAIL`. See `_integrations/drive-transcripts/README.md`.

**Added.** Machine-checkable brand heritage, generalized from a client deployment. The brand becomes verifiable by script instead of by memory:
- `_templates/brand/tokens.json` — DTCG design tokens (palette, signature gradient, fonts, type scale, radii, logo clear space), filled by `/brand-discover` from the existing `BRAND_*` placeholders; colours may carry a `scope` (folders where a restricted shade is allowed) and a `deltaE_max` tolerance under `$extensions.cockpit`.
- `scripts/build-tokens.py` + `build-tokens.toml` — generates the CSS consumers from `tokens.json` (marker blocks or whole files, declared in the TOML, not in code), `--check` exits 1 on drift, refuses unresolved placeholders and invalid hex. Wired targets: the brand block of `06-graphic-design/presentations/tokens.css` (now between `brand-tokens` markers) and a generated CSS appendix in `style-guide.md`.
- `scripts/lint-brand.py` + `lint-brand.toml` — deterministic brand linter, brand-agnostic code: banned vocabulary (brand charter + anti-AI list EN/FR), em dashes, final period on titles, hashtags (off by default), unresolved placeholders (reuses `lint-placeholders.py`), off-palette hex with ΔE76 tolerance and token scopes, off-brand fonts (read from `tokens.json`), negative parallelisms (EN/FR). Before the wizard, graphic rules are suspended with a single `palette` warning. Text or JSON output, exit 1 on error.
- `scripts/build-inventory.py` + `build-inventory.toml` — builds and checks `_templates/inventory.md` from the production folders (`--add` after each delivery, `--check` for drift and undated files).
- `scripts/relativize-paths.py` — rewrites machine-absolute `file://` / bare absolute URLs of HTML/CSS compositions into relative paths.
- Doctrine gabarits in `_templates/brand/`: `anti-ai-writing-style.md` (anti-AI writing doctrine, mirrored by the linter config), `exemples-rejetes.md` (rejection corpus fed by `brand-check`), `divulgation-ia.md` (default AI disclosure policy, to validate), `droits.md` (rights register: fonts, third-party logos, image rights, AI-derived portraits).
- Tests in `scripts/tests/` (fictitious fixtures): `python3 -m pytest scripts/tests -q`.

**Changed.** PostToolUse hook `brand-check-reminder.py` runs the linter on the written file and attaches its findings (never blocks a write, falls back to the plain reminder). `brand-check` gains step 0 (deterministic lint), the inventory script in step 2.5 and the rejection-corpus step; `inventory` delegates to the script; `humanize-writing`, `image-generation`, `video-editing`, `design-system` point to the new doctrine files. `/brand-discover` writes `tokens.json`, the four doctrine files and the brand switches of `lint-brand.toml`, then runs `build-tokens.py`; `/validate-setup` checks the generated tokens. `voice.md` gabarit gains default construction rules (no final period on titles, no orphan word at the end of a short block, no em dash). `SECURITY.md`, root `CLAUDE.md` (table « Ce que les skills n'ont pas à juger de mémoire »), `01-brand` and `06-graphic-design` role files, `08-video` point to `divulgation-ia.md` / `tokens.json`. `scripts/lint-placeholders.py` exposes its allow-list as `PLACEHOLDERS_TOLERES`. `.gitignore` ignores the per-project `01-brand/tokens.json`. Requires Python 3.11+ (`tomllib`).

**Added.** Visual QA and visual production tooling, generalized from a client deployment. In `06-graphic-design/scripts/`: `qa-visuel.py` (QA of a carousel, an HTML composition or an image: dominant colours against the `01-brand/tokens.json` palette in ΔE76 with scopes, font, typographic floors, WCAG 2.x contrast, logo clear space and backdrop; JSON output, exit code usable as a gate), `qa_common.py` (shared pure-Python computations: colours, contrast, palette and Lab, tokens.json reader, JS text collector), `build-carousel.py` (carousel engine driven by an `outputs/carrousel-<slug>-<date>/carrousel.json` spec, no brand value in the script: colour roles read from tokens.json and remappable, local font, assets designated by the spec; "portrait / photo" and "thesis" families), `export-carousel-pdf.py` (PDF export that rasterizes gradient text), `compose-screenshot.sh` (2× headless Chrome capture of a composition), `genmeta.py` (provenance of generated images: real extension, `ai:generated_by` PNG tag, `<image>.gen.json` sidecar, C2PA guard), `promote-asset.py` (promotes a validated asset into `01-brand/assets/` with a catalogue entry and mandatory rights fields). `06-graphic-design/lib/compose.css` (composition base: local font + `presentations/tokens.css` tokens) and `lib/README.md` (install the brand font locally, check its licence). 9 test files under `scripts/tests/` (fictional brand, throwaway repos; tests that drive Chromium are skipped cleanly without Playwright). `.gitignore`: `*.gen.json` and carousel PDF exports.

**Changed.** `presentations/scripts/qa.py` merges the existing engine-parity checks with production-tested ones: geometry brought back to the native frame whatever the viewport, typographic floor (18 px content, 12 px chrome, warning under 24 px), font (tokens.json families, else the deck's), WCAG contrast, folios (`.nav-num`, `.tag-folio`), `--lang` language switch, `--bleed`/`data-bleed` overflowing layers, readable capping of findings, `--format json`. Agents `qa-visuel` (tooled procedure, known false positives) and `brand-guardian` (measure before reading, banned visuals). Skills `carousel`, `image-generation` and `slides`, `06-graphic-design/CLAUDE.md` and its role template: pointers to the tooling.

**Dependency.** `build-carousel.py`, `qa-visuel.py` and the font check of `qa.py` read `01-brand/tokens.json` (DTCG format: `color.primary|accent|dark|light`, `font.*`, `logo.*`), brought by the brand-heritage PR: merge that one first.

**Added.** `notify-site` workflow — pings the showcase site (repository_dispatch) whenever skills or agents change on main, so displayed counts stay in sync automatically (site also has a daily-cron fallback). README: skills table now exhaustive (53/53, n8n skills were uncounted), agents and video module rows updated.

**Added.** Video studio backport, generalized from a client production run. Three new skills: `video-generation` (t2v/i2v rushes via a multi-model MCP — motion-first EN prompts, strict spend discipline, and the **audio-envelope text-fidelity check** that catches generative models rewriting what a real person says), `video-matting` (local RobustVideoMatting alpha layers, QC, ProRes 4444 export, and the "regenerate rather than rescue a soft source" lesson), `reel-talking-head` (orchestrator from raw talking-head footage to an edited vertical reel, with two hard validation gates before any spend). Two new agents: `video-art-director`, `video-model-scout`. New doctrine file `08-video/montage.md` (documentary cut/rhythm/sound rules as a measurable pre-export checklist). Skill count: 50 → 53.

**Changed.** `video-editing` — field-tested Palmier Pro guardrails: MCP robustness rules (one call at a time, forced saves, post-crash re-audit, frame-exact trims) and a reliable export path (hidden `.partial`, finalize freeze, silent render death → **segmented export + lossless concat parade**, master transcription check before delivery). `captions` — true karaoke method via editor text clips (per-token whisper timings, homophone proofing) and a libass availability guard. `image-generation` — MCP spend-discipline section (iterate where included, produce via MCP, one sample before any batch, live balance check).

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
