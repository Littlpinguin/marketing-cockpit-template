# Architecture

One-page mental model of the Marketing Copilot Template.

## Philosophy

Three principles drive every design decision.

1. **Brand as truth.** `01-brand/` is the single source. Every role defers to it. Contradictions are flagged before publication, not after.
2. **Retrieval-first (when it pays).** At scale, every creative act is preceded by a semantic search. Below scale, file-based reads are faster to reason about and zero-dependency. The copilot works both ways.
3. **Hook-enforced.** The harness enforces the workflow, not Claude's willpower. A PostToolUse hook fires the brand check whenever content is written in a production folder. Deterministic, not hopeful.

## Component map

```
┌──────────────────────────────────────────────────────────────────┐
│  Wizard (run once, resumable)                                    │
│  .claude/commands/                                               │
│  ├── start-copilot.md     ← entry point                          │
│  ├── brand-discover.md    ← analyze public signals, propose      │
│  │                          doctrine, validate section by section│
│  ├── tools-setup.md       ← pick tools, regenerate role docs     │
│  ├── seed-corpus.md       ← optional: ingest recent content      │
│  ├── connect-qdrant.md    ← optional: enable semantic memory     │
│  ├── validate-setup.md    ← lint + sample + user approval        │
│  └── health-check.md      ← ongoing: verify runtime health       │
│                                                                  │
│  Shared wizard skill                                             │
│  .claude/skills/copilot-setup/SKILL.md                           │
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
│  02-strategy/     → content-strategy skill                       │
│  03-social-media/ → social-content skill                         │
│  04-email/        → email skill (uses {{EMAIL_MARKETING_TOOL}})  │
│  05-web-content/  → copywriting skill                            │
│  06-graphic-design/ → image-generation + slides skills           │
│    └── presentations/ → 1920×1080 HTML decks, Playwright QA      │
│    └── mail-signatures/ → HTML signature template generator      │
│  07-events/       → event-marketing skill                        │
│  09-blog-seo/     → seo skill (publishes to {{BLOG_CMS}})        │
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
│  ├── qdrant/                                                     │
│  │   ├── sync.py            ← 6-phase pipeline                   │
│  │   ├── mcp_server.py      ← MCP: qdrant_search, find_similar   │
│  │   ├── sources/           ← notion, outline, transcripts, fs   │
│  │   ├── enrichers/         ← summary, entities, claims, meeting │
│  │   ├── embedders/         ← Gemini embedding-001 (3072 dim)    │
│  │   ├── config.yaml        ← sources, enrichers, task_types     │
│  │   └── cron/              ← macOS launchd weekly sync          │
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
   ├── If Qdrant enabled: qdrant_search(topic="Q1 reliability") for anti-repetition
   ├── If Qdrant enabled: qdrant_search(filter=brand) to verify numbers
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
   ├── If Qdrant enabled: qdrant_find_similar for anti-repetition score
   └── Verdict: ✅ PASS / 🟠 FIX / 🔴 BLOCK
   │
   ▼
If ✅: deliver to user. If 🟠: auto-correct, re-check. If 🔴: surface to user.
   │
   ▼
User reviews. On approval: post archived to examples/, calendar updated.
```

## Qdrant-on vs Qdrant-off

| Concern | Qdrant ON | Qdrant OFF |
|---|---|---|
| Anti-repetition | `qdrant_find_similar` across all indexed content | Read last N files in `<channel>/examples/` |
| Number verification | `qdrant_search(filter=brand)` | Grep `01-brand/messaging-framework.md` |
| Brand doctrine access | `qdrant_search(filter=brand)` — 500 ms, targeted | Full read of `01-brand/*.md` — cheap if small |
| Cross-channel consistency | Single query across all collections | Not available |
| Meeting transcript surfacing | Automatic via ingestion | Manual reads of `_sources/transcriptions/` |
| Setup dependency | Qdrant Cloud + Google AI key | None |
| Recommended when | Volume > 50 pieces / month | Volume ≤ 50 pieces / month |

Flip the flag in `.setup-completed.features.qdrant.enabled`. Skills handle both paths.

## Why this shape

**Role-based folders.** Mirrors how marketing teams actually think. When the user says "the newsletter," the relevant CLAUDE.md is `04-email/CLAUDE.md`, not buried in a common config file. Cognitive locality.

**Separation of doctrine from production.** `01-brand/` is read; everything else writes. This one-way flow means contradictions are always traceable to a doctrine conflict, never to a content-side decision.

**Skills as verbs, roles as nouns.** Roles (noun folders) own their data and workflow. Skills (verb units) are invoked across roles. Writing a LinkedIn post uses the `social-content` skill from the `03-social-media/` role folder. Same skill, different contexts.

**Wizard as separate lifecycle.** Setup is finite and ritualistic; operation is continuous. Separating `.claude/commands/` (setup + health) from `.claude/skills/` (operation) keeps each clear.

**Hook-enforced gate.** Brand-check as a reminder (not a hard block) because Claude's judgment handles edge cases better than a mechanical gate — but the reminder is deterministic so nothing is "forgotten."
