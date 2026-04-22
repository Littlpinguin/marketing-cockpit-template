---
name: tools-setup
description: Configure the tools the company actually uses (editorial calendar, email marketing, CRM, events platform, knowledge base, analytics, social scheduler, image generation). Wires connectors, updates .env.example, regenerates role CLAUDE.md with real tool names, and updates the README tool-status board.
---

# /tools-setup — pick and wire tools per category

Load the `copilot-setup` skill first.

## Intent

The template ships tool-agnostic. This command records the user's actual stack — which specific tool backs each functionality — and adapts the repo accordingly. After `/tools-setup`, the role `CLAUDE.md` files say "Notion" instead of `{{EDITORIAL_CALENDAR_TOOL}}`, the `.env.example` only lists variables the user needs, and unused connector stubs are removed.

## Inputs

None required at start. This command asks each question interactively.

## Flow

### Step 1 — Load registry

Read `docs/tools.json`. This is the canonical list of categories and supported tools with connector status.

Also read the current `.setup-completed` if it exists (re-run scenario). Preserve previous answers and ask only about gaps or changes.

Echo the security line:

> For each tool, I'll ask for the env variable names and confirm they're set in `.env`. I won't read the actual key values. If a tool has no built-in connector yet, I'll tell you and scaffold a TODO stub — you'll need to implement it before that tool can sync or push.

### Step 2 — Iterate categories

Go through categories in this order (logical flow from content creation to analytics):

1. `editorial_calendar` — where content is planned
2. `email_marketing` — newsletters, promos
3. `knowledge_base` — internal docs, playbooks
4. `events_platform` — webinars, livestreams
5. `crm` — lead and customer data
6. `web_analytics` — reach and conversion
7. `social_scheduler` — optional scheduling layer
8. `semantic_memory` — Qdrant (deferred to `/connect-qdrant`, just record user intent)
9. `image_generation` — Gemini brand-compliant images

For each category, present a structured question:

```
## Category: Editorial calendar

Where do you plan and track your marketing content?

Built-in connectors (ready today):
  - notion ✅

Stubs (you'll need to implement the connector):
  - airtable
  - trello
  - clickup
  - google-sheets
  - custom

Or: none (disable this functionality entirely)

Your choice:
```

Wait for the answer. Then:

### Step 3 — Handle the choice

For each chosen tool:

#### If `connector_status == "ready"`
1. Confirm the env keys (`NOTION_API_KEY`, `NOTION_EDITORIAL_DATABASE_ID`, etc.) are listed in `.env.example`.
2. Ask the user to paste the resource ID (e.g. Notion database URL → extract the UUID). Do not ask for the API key value.
3. Save the resource ID into a placeholder field in `docs/tools.json` (not into `.env`; users fill `.env` themselves).
4. Ask any tool-specific follow-up (Notion: "what's the exact status label that marks content as ready to publish?").

#### If `connector_status == "stub"`
1. Explain: "There's no built-in connector for `<tool>` yet. I'll generate a stub at `_integrations/qdrant/sources/<tool>.py` (for ingestion) and `_integrations/connectors/<tool>.py` (for push). The stubs have TODO comments. You or your developer implement them before first sync."
2. Confirm the user accepts this.
3. Generate the stubs from `_templates/connector-stub.py.tpl` (read the stub template, substitute `<tool>` and category, write the output files).
4. Record the env keys the stub expects in `.env.example`.

#### If `none`
1. Disable the category in the tool registry.
2. Remove corresponding sections from role `CLAUDE.md` at regeneration time (Step 5).
3. Do not add env keys.

### Step 4 — Update `.env.example`

After all categories are processed, rewrite `.env.example` to include:
- Always: `QDRANT_*` and `GOOGLE_AI_*` (documented as optional)
- Only for enabled tools: the env keys listed in `docs/tools.json` for that tool

Do not include env keys for tools the user didn't pick. Keep the file lean.

Present the diff to the user before writing:

> Here's the new `.env.example`. OK to write? (yes / show-only / cancel)

### Step 5 — Regenerate role `CLAUDE.md`

For each of the 9 role folders, read the template at `_templates/role-claudemd/<role>.tpl` and substitute:
- `{{EDITORIAL_CALENDAR_TOOL}}` → the actual chosen tool name, or the line is removed if `none`
- `{{EMAIL_MARKETING_TOOL}}`, `{{EVENTS_PLATFORM_TOOL}}`, etc. — same logic
- Conditional blocks (`{{#if QDRANT_ENABLED}}…{{/if}}`) — keep or remove based on intent recorded

Write the result to `<role>/CLAUDE.md`. Back up the previous version to `.setup-archive/role-claudemd-<ISO8601>/` before overwriting.

Confirm one by one or in bulk, user's choice:

> I'll regenerate all 9 role `CLAUDE.md` files now. Do you want to review each before writing, or should I proceed in bulk? (review-each / bulk / cancel)

### Step 6 — Update the README tool-status board

Read the current `README.md`. Find the `<!-- tool-status:start -->` / `<!-- tool-status:end -->` markers. Replace the content between them with a fresh Markdown table built from the choices + `docs/tools.json`:

```markdown
<!-- tool-status:start -->
| Category | Your tool | Connector |
|---|---|---|
| Editorial calendar | Notion | ✅ Ready |
| Email marketing | MailerLite | ✅ Ready |
| Knowledge base | — | Disabled |
| Events platform | Livestorm | 🟠 Stub — implementation required |
| CRM | — | Disabled |
| Semantic memory (Qdrant) | deferred | Run `/connect-qdrant` to enable |
| Image generation (Gemini) | enabled | ✅ Ready |
<!-- tool-status:end -->
```

### Step 7 — Record wizard log

Append an entry to the in-memory `.setup-completed` structure:

```json
{ "command": "/tools-setup", "at": "ISO 8601", "tools_selected": { ... } }
```

The actual file write happens in `/validate-setup`.

### Step 8 — Hand back

Output:

> Tools configured. Your role CLAUDE.md files now reference your real tools, and `.env.example` only lists the keys you'll need.
>
> Next:
>   - If you want Qdrant-based semantic memory: run `/connect-qdrant`
>   - To ingest your recent content for anti-repetition: `/seed-corpus`
>   - To validate and lock in the setup: `/validate-setup`
>
> You can also revisit tool choices any time by re-running `/tools-setup`.

## Failure modes to avoid

- **Don't write `.env` values.** Only `.env.example`. Users fill `.env` themselves.
- **Don't overwrite role CLAUDE.md without backup.** Always move the previous version to `.setup-archive/`.
- **Don't let the user pick "ready" tools without confirming they have the credentials ready.** If they say "ready" but haven't set env vars, warn that the tool is configured but unused until vars are set.
- **Don't silently change the Qdrant enabled flag here.** `/connect-qdrant` owns that decision.
- **Don't remove `_integrations/qdrant/sources/*.py` files that already exist as built-in connectors.** Only add stubs for new tools.
