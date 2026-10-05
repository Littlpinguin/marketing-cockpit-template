# Architecture

One-page mental model of the Marketing Cockpit Template.

## Philosophy

Three principles drive every design decision.

1. **Brand as truth.** `01-brand/` is the single source. Every role defers to it. Contradictions are flagged before publication, not after.
2. **File-based memory.** Anti-repetition and number verification rely on scanning the calendar, per-channel archives and inventory files. Zero external dependency, fully auditable.
3. **Hook-enforced.** The harness enforces the workflow, not Claude's willpower. A PostToolUse hook fires the brand check whenever content is written in a production folder. Deterministic, not hopeful.

## Component map

```
┌──────────────────────────────────────────────────────────────────┐
│  Wizard (run once, resumable)                                    │
│  .claude/commands/                                               │
│  ├── start-cockpit.md     ← entry point                          │
│  ├── brand-discover.md    ← analyze public signals, propose      │
│  │                          doctrine, validate section by section│
│  ├── tools-setup.md       ← pick tools, regenerate role docs     │
│  ├── modules.md           ← enable/disable optional modules      │
│  ├── validate-setup.md    ← lint + sample + user approval        │
│  └── health-check.md      ← ongoing: verify runtime health       │
│                                                                  │
│  Shared wizard skill                                             │
│  .claude/skills/cockpit-setup/SKILL.md                           │
└──────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────┐
│  Brand doctrine (filled by /brand-discover)                      │
│  01-brand/                                                       │
│  ├── voice.md                                                    │
│  ├── style-guide.md                                              │
│  ├── messaging-framework.md                                      │
│  ├── personas.md                                                 │
│  ├── brand-platform.md                                           │
│  └── assets/                                                     │
└──────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────┐
│  Production roles (CLAUDE.md filled by /tools-setup)             │
│  00-intel/        → confidential memory (gitignored, n8n-fed)    │
│  02-strategy/     → content-strategy skill                       │
│  03-social-media/ → social-content skill                         │
│  04-email/        → email skill (uses {{EMAIL_MARKETING_TOOL}})  │
│  05-web-content/  → copywriting skill                            │
│  06-graphic-design/ → image-generation + slides skills           │
│    └── presentations/ → 1920×1080 HTML decks, Playwright QA      │
│    └── mail-signatures/ → HTML signature template generator      │
│  07-events/       → event-marketing skill                        │
│  09-seo/          → seo skill (publishes to {{BLOG_CMS}})        │
│                                                                  │
│  Optional modules (enable via /modules, state in                 │
│  .setup-completed.modules)                                       │
│  08-video/           → video-editing + captions skills           │
│  10-automatisations/ → n8n workflows                             │
│  11-reporting/       → performance-report skill                  │
│  12-acquisition/     → scraping + outreach (n8n, Apify, Lemlist) │
│  14-print/           → print skill, PDF/X-4 CMYK chain, prepress │
└──────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────┐
│  Skills (.claude/skills/)                                        │
│  brand-check       ← quality gate, runs after every Write/Edit   │
│  social-content                                                  │
│  email             ← dry-run before push                         │
│  copywriting                                                     │
│  copy-editing      ← 7-pass review                               │
│  content-strategy                                                │
│  seo                                                             │
│  event-marketing                                                 │
│  image-generation  ← brand-prefixed Gemini prompts               │
│  slides            ← editorial HTML decks, Playwright QA gate    │
└──────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────┐
│  Integrations                                                    │
│  _integrations/                                                  │
│  └── connectors/            ← one file per tool (ready or stub)  │
│      ├── mailerlite.py                                           │
│      ├── mailchimp.py                                            │
│      └── <tool>.py (stubs generated by /tools-setup)             │
└──────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────┐
│  Hooks and enforcement                                           │
│  .claude/settings.json                                           │
│  └── PostToolUse on Write|Edit                                   │
│      └── .claude/hooks/brand-check-reminder.py                   │
│          (fires only on production folders, not meta files)      │
│                                                                  │
│  scripts/                                                        │
│  ├── lint-placeholders.py  ← blocks /validate-setup if {{*}}     │
│  └── dry-run-push.py       ← mandatory before any real push      │
└──────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────┐
│  Raw material                                                    │
│  _sources/                                                       │
│  ├── transcriptions/                                             │
│  ├── reports/                                                    │
│  └── research/                                                   │
│                                                                  │
│  _examples/                                                      │
│  └── acme-saas/ (fictional corpus for day-one seeding)           │
└──────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────┐
│  Runtime configuration                                           │
│  .setup-completed       ← JSON, written by /validate-setup       │
│  .env                   ← secrets, gitignored                    │
│  docs/setup-completed.schema.json                                │
│  docs/tools.json        ← canonical tool registry                │
│  docs/placeholders.json ← canonical placeholder list             │
└──────────────────────────────────────────────────────────────────┘
```

## Request flow — writing a LinkedIn post

```
User: "Write a LinkedIn post about our Q1 reliability numbers"
   │
   ▼
Claude Code loads CLAUDE.md (root) + 03-social-media/CLAUDE.md
   │
   ▼
Skill auto-resolution: social-content
   │
   ▼
Skill preflight:
   ├── Read 01-brand/voice.md
   ├── Read 3-5 files in 03-social-media/linkedin/examples/
   ├── Scan _templates/inventory.md + calendar for anti-repetition
   ├── Grep 01-brand/messaging-framework.md to verify numbers
   └── Check editorial calendar (if configured)
   │
   ▼
Draft written to 03-social-media/linkedin/drafts/<slug>.md
   │
   ▼
PostToolUse hook fires:
   └── brand-check-reminder.py injects mandatory brand-check reminder
   │
   ▼
brand-check skill runs:
   ├── 5-point filter (vocabulary, tone, proof, audience, visual)
   ├── File-based anti-repetition scan (archives + inventory)
   └── Verdict: ✅ PASS / 🟠 FIX / 🔴 BLOCK
   │
   ▼
If ✅: deliver to user. If 🟠: auto-correct, re-check. If 🔴: surface to user.
   │
   ▼
User reviews. On approval: post archived to examples/, calendar updated.
```

## File-based memory

| Concern | How it works |
|---|---|
| Anti-repetition | Scan the calendar, per-channel archives (`examples/`, `editions/`, `articles/`) and `_templates/inventory.md` |
| Number verification | Grep `01-brand/messaging-framework.md` |
| Brand doctrine access | Full read of `01-brand/*.md` |
| Meeting transcript surfacing | Reads of `00-intel/` (n8n-fed) and `_sources/transcriptions/` |
| Setup dependency | None |

## Why this shape

**Role-based folders.** Mirrors how marketing teams actually think. When the user says "the newsletter," the relevant CLAUDE.md is `04-email/CLAUDE.md`, not buried in a common config file. Cognitive locality.

**Separation of doctrine from production.** `01-brand/` is read; everything else writes. This one-way flow means contradictions are always traceable to a doctrine conflict, never to a content-side decision.

**Skills as verbs, roles as nouns.** Roles (noun folders) own their data and workflow. Skills (verb units) are invoked across roles. Writing a LinkedIn post uses the `social-content` skill from the `03-social-media/` role folder. Same skill, different contexts.

**Wizard as separate lifecycle.** Setup is finite and ritualistic; operation is continuous. Separating `.claude/commands/` (setup + health) from `.claude/skills/` (operation) keeps each clear.

**Hook-enforced gate.** Brand-check as a reminder (not a hard block) because Claude's judgment handles edge cases better than a mechanical gate — but the reminder is deterministic so nothing is "forgotten."
