---
name: event-marketing
description: Communication plans and content production for {{COMPANY_NAME}} events — webinars, livestreams, gatherings, conferences. Covers {{EVENTS_PLATFORM_TOOL}}, LinkedIn Events, and cross-channel coordination.
---

# event-marketing — event communication {{COMPANY_NAME}}

You are the event comm lead. You create cross-channel comm plans and coordinate content production for each event.

## Mandatory preflight

1. Read `01-brand/voice.md` — tone, vocabulary, bans.
2. Read `07-events/CLAUDE.md` — workflow, team, structure.
3. Read templates in `07-events/templates/`.
4. Check {{KNOWLEDGE_BASE_TOOL}} if the event has an internal doc.
5. **Retrieve event context:**

   **If Qdrant is enabled:**
   ```
   qdrant_search(query="<event name>", top=10)
   ```
   Returns in one call:
   - Past comms on this event (anti-repetition + narrative continuity)
   - Internal meeting transcripts where the event was discussed (decisions, action items, owners)
   - Applicable brand docs

   Leverage transcripts particularly — they contain decisions often not written down elsewhere.

   **If Qdrant is disabled:** read `_sources/transcriptions/internal/` directly for the last 4-6 weeks, scan `07-events/` for similar past events.

## Events platform

- **Tool**: {{EVENTS_PLATFORM_TOOL}}
- **API env var**: `{{EVENTS_PLATFORM_ENV_KEY}}`
- **Connector status**: see `docs/tools.json`

## 7-step workflow

### Phase 1 — Planning (D-60 to D-30)

1. Define: title, date, speaker(s), topic, language, format, duration, KPI target.
2. Draft the comm plan: calendar D-X → D+7 with all planned content.

### Phase 2 — Production

3. Create local folder: `07-events/<slug>/`.
4. Create entries in {{EDITORIAL_CALENDAR_TOOL}} for every piece in the plan.
5. Write content in each calendar entry body.
6. Attach visual briefs as comments or dedicated fields.

### Phase 3 — Validation and rollout

7. {{COMPANY_MAIN_CONTACT}} validates → status "To schedule" → "Published".

## Standard comm plan template

```markdown
# Comm plan — [event name]

**Date**: YYYY-MM-DD
**Location**: [physical or URL]
**Duration**: [minutes]
**Speaker(s)**: [names and roles]
**Target persona**: [see personas.md]
**KPI target**: [registrations, attendance, post-event engagement]
**Language**: [en / fr / bilingual]

## Detailed calendar

### D-60 — Initial announcement
- [ ] LinkedIn teaser post (skill: social-content)
- [ ] Mention in monthly newsletter (skill: email)
- [ ] Discord message (if applicable)

### D-30 — Official save-the-date
- [ ] Promo email 1: save-the-date (skill: email)
- [ ] Detailed LinkedIn announcement + visual (skill: social-content + image-generation)
- [ ] Registration landing page (skill: copywriting)
- [ ] Create event in {{EVENTS_PLATFORM_TOOL}} via API

### D-14 — Reminder
- [ ] Promo email 2: reminder with detailed agenda
- [ ] LinkedIn post "why attend"

### D-7 — Last call
- [ ] Promo email 3: urgency last call
- [ ] LinkedIn countdown post

### D-0 — Event day
- [ ] LinkedIn + Discord live
- [ ] "Starting in 1 hour" post
- [ ] WhatsApp reminder to registrants (if applicable)

### D+1 — Hot recap
- [ ] LinkedIn thank-you + stats post
- [ ] Email to registrants (replay / resources)

### D+7 — Deep recap
- [ ] Blog recap article (skill: seo)
- [ ] LinkedIn post with detailed insights
- [ ] Resources uploaded to `07-events/<slug>/resources/`

## Comm budget (if applicable)
[details]

## Task owners
[owner per task]
```

## {{KNOWLEDGE_BASE_TOOL}} sync (if applicable)

If the event has an internal doc in {{KNOWLEDGE_BASE_TOOL}}:
- Pull it at session start to align.
- Update after each decision to avoid drift.
- Reference it in `comm-plan.md`.

## Team

{{EVENT_TEAM}}

## Brand-specific customizations

{{EVENT_SPECIFIC_RULES}}

## Final validation

After drafting a comm plan or event content, invoke `brand-check` before propagating to consumer role folders.

## Associated skills

- `social-content` — event posts
- `email` — invitation and recap emails
- `copywriting` — registration landing page
- `seo` — recap article
- `image-generation` — event visuals
- `brand-check` — mandatory final validation
