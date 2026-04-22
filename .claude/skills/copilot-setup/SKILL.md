---
name: copilot-setup
description: "Shared logic for wizard slash commands (/start-copilot, /brand-discover, /tools-setup, /seed-corpus, /connect-qdrant, /validate-setup, /health-check). Centralizes preflight checks, tool registry mutation, placeholder linting, security rules, and .setup-completed schema."
---

# copilot-setup — shared wizard skill

Every wizard slash command loads this skill first and follows the rules here before doing anything specific. This keeps the wizard coherent across commands and avoids duplicating logic.

## Invariants (never violate these)

1. **One step per message.** Never batch multiple decisions in a single message. Each step: explain, ask, wait for confirmation, then proceed.
2. **No silent defaults.** If a value is missing, ask for it. Never assume.
3. **No writes before validation.** For any generated artifact (brand doctrine, role CLAUDE.md, setup metadata), present the draft, get explicit approval, then write.
4. **No secrets in messages or commits.** Secrets go to `.env` only. Never echo a secret back to the user — ask them to verify `.env` on their side.
5. **Destructive operations require confirmation.** File deletion, `.setup-archive/` moves, git force operations, launchctl (system agents) all require an explicit "yes" from the user.
6. **English only in repo artifacts.** All files produced by the wizard (CLAUDE.md, skill bodies, docs, scripts) are in English. Content produced later by the copilot itself follows the brand language chosen at setup.

## Preflight checks (run at every wizard entry)

Call these in order, silently. If any fail, surface the failure with a remediation suggestion.

1. **Model check.** Confirm the current session is on Sonnet 4.6 or better. If the user is on Haiku, warn that wizard-phase quality (brand discovery, sample generation) benefits from Sonnet or Opus, and offer to continue anyway. If on Opus, proceed — it's overkill for this but does no harm.
2. **Git state.** `git status --porcelain`. If the working tree is dirty, ask whether to stash, commit, or proceed anyway.
3. **Python deps.** `python3 -c "import yaml, dotenv, requests"`. If missing, suggest `pip install pyyaml python-dotenv requests`. (qdrant-client, google-genai, mcp only needed if `/connect-qdrant` will run.)
4. **`.env` exists.** If not, `cp .env.example .env` and tell the user. Never read secrets from `.env` in a message — only check presence.
5. **`.setup-completed` state.** Exists? The wizard is for first-time setup. Offer to re-run specific commands (`/tools-setup`, `/brand-discover`) individually if the user wants to reconfigure.

## Reference files — load these when needed

| File | When to load |
|---|---|
| `docs/placeholders.json` | Any time you fill or validate templates |
| `docs/tools.json` | `/tools-setup`, to know which connectors are ready vs. stubs |
| `docs/setup-completed.schema.json` | `/validate-setup`, to produce a conforming `.setup-completed` |
| `SECURITY.md` | Preflight display, before any step that touches secrets or external APIs |
| `_examples/` | `/seed-corpus`, as fallback corpus when the user has nothing to ingest |

## Placeholder discipline

The template uses `{{UPPERCASE_UNDERSCORE}}` placeholders (Mustache-style). The canonical list is `docs/placeholders.json`.

Before any command completes:
- Run `python3 scripts/lint-placeholders.py --paths 01-brand 02-strategy 03-social-media 04-email 05-web-content 06-graphic-design 07-events 08-mail-signatures 09-blog-seo .claude/skills`.
- If the exit code is non-zero, the command cannot proceed. Surface the list of remaining placeholders and the files they live in.
- `/validate-setup` is the only command that hard-blocks on residual placeholders — other commands can warn and continue if the user accepts.

## Tool registry mutation

When `/tools-setup` records a tool choice:
1. Read `docs/tools.json`.
2. Update `.setup-completed` in-memory (the real write happens in `/validate-setup`).
3. For the picked tool, check `connector_status`:
   - `ready` → no action, the connector file already exists.
   - `stub` → prompt the user: "This tool has no built-in connector yet. The wizard will generate a TODO stub at `_integrations/qdrant/sources/<tool>.py`. You or your developer will need to implement it before the first sync."
   - `unsupported` → refuse and list supported alternatives.
4. Regenerate any role `CLAUDE.md` that references this tool category: read `_templates/role-claudemd/<role>.md`, substitute tool placeholders, write to `<role>/CLAUDE.md`. Always back up the previous version to `.setup-archive/role-claudemd-<ISO8601>/` before overwriting.

## Security rules echo

At the start of every wizard command, echo one sentence about the security expectations relevant to that command, and point to `SECURITY.md`. Example:

- `/start-copilot`: "This wizard will ask you to paste URLs and tool names. It will never ask you to paste an API key in chat — keys go into `.env` only. Full rules: `SECURITY.md`."
- `/tools-setup`: "For each tool you pick, I'll ask you to confirm the `.env` variable name and whether the key is set. I will not read the key value itself."
- `/connect-qdrant`: "Qdrant setup reads `QDRANT_URL` and `QDRANT_API_KEY` from `.env`. I will test the connection but never print the key back to you."

## `.setup-completed` writing

Only `/validate-setup` writes this file. Shape (matches `docs/setup-completed.schema.json`):

```json
{
  "version": "0.2.0",
  "completed_at": "ISO 8601",
  "company": "string",
  "company_website": "URL",
  "language": "en | fr | es | de | pt",
  "bilingual": false,
  "tools": {
    "editorial_calendar": { "name": "notion|airtable|trello|clickup|google-sheets|custom|none", "enabled": true },
    "email_marketing":    { "name": "mailerlite|mailchimp|resend|brevo|convertkit|custom|none", "enabled": true },
    "knowledge_base":     { "name": "outline|notion|confluence|gitbook|custom|none", "enabled": false },
    "events_platform":    { "name": "livestorm|zoom|riverside|google-meet|custom|none", "enabled": false },
    "crm":                { "name": "hubspot|pipedrive|odoo|notion|airtable|custom|none", "enabled": false }
  },
  "features": {
    "qdrant":           { "enabled": false, "rationale": "string" },
    "image_generation": { "enabled": true,  "model": "gemini-3-pro-image-preview" },
    "weekly_cron":      { "enabled": false }
  },
  "wizard_log": [
    { "command": "/start-copilot",   "at": "ISO 8601" },
    { "command": "/brand-discover",  "at": "ISO 8601" },
    { "command": "/tools-setup",     "at": "ISO 8601" },
    { "command": "/validate-setup",  "at": "ISO 8601" }
  ]
}
```

## Reentry policy

Each slash command must be idempotent. Running `/tools-setup` a second time must read current state, show what's already configured, and ask what to change — not start from scratch.

## What this skill does NOT do

- It doesn't produce marketing content (that's `social-content`, `email`, `copywriting`, etc.).
- It doesn't run brand-check (that's `brand-check`).
- It doesn't call external APIs directly — connectors in `_integrations/` do that.
- It doesn't store secrets. Only reads presence.

Wizard commands stay focused on orchestration and consent. Production skills stay focused on production.
