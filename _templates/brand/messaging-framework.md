# Messaging framework — {{COMPANY_NAME}}

Source of truth for claims, numbers, and narrative structure. Every producing role reads this before writing anything that converts. The `brand-check` skill verifies numbers against this file.

## Central message

One sentence. What {{COMPANY_NAME}} fundamentally argues. Every piece of content ultimately rolls up to this.

> {{COMPANY_POSITIONING}}

## Messages per persona

| Persona | Sub-message | Primary proof points |
|---|---|---|
| {{PERSONA_1_NAME}} | ... | ... |
| {{PERSONA_2_NAME}} | ... | ... |
| {{PERSONA_3_NAME}} | ... | ... |
| {{PERSONA_4_NAME}} | ... | ... |

## Top key numbers (canonical)

Every published number comes from this list. Any new number needs explicit external citation. The `brand-check` skill blocks content that references a number absent from here without citation.

{{BRAND_TOP_NUMBERS}}

Recommended format for each entry:

```
- [Number + unit] — [short context] (source: [internal report / external study / calculation method], last verified YYYY-MM-DD)
```

Example:

```
- 8.8/10 satisfaction (n=136 customers surveyed Q1 2026) (source: internal NPS survey, last verified 2026-04-01)
- 38 days median time-to-hire (source: internal HR records 2025, last verified 2026-01-10)
- 99.97% uptime 2025 (source: status page aggregation, last verified 2026-01-15)
```

Numbers drift: set a refresh cadence (quarterly is typical) and tag them with the last-verified date.

## CTA patterns

Standard CTAs that work for this brand. Reuse rather than invent.

- **Primary (conversion)**: [one phrase, e.g. "Book a demo"]
- **Secondary (engagement)**: [one phrase, e.g. "Read the benchmark"]
- **Content-to-content**: [one phrase, e.g. "Subscribe to monthly updates"]
- **Sales-to-conversation**: [one phrase, e.g. "Reply to this email — Paul reads every one"]

## Proof hierarchy

From strongest to weakest. Use the strongest available for any claim.

1. Named customer case study with numbers
2. Internal report with methodology + sample size
3. Industry benchmark (Gartner, Forrester, named study) with citation
4. Publicly observable fact (pricing, release history)
5. Logical argument backed by multiple data points
6. Opinion framed as opinion (rare — only for thought-leadership pieces and explicitly flagged)

Skip anything weaker than 6. Unsupported claims never ship.

## Narrative structures that work

Common arcs proven to resonate. Use as starting scaffolds.

- **Contrarian claim + data**: "Everyone says X. Our data shows Y." + 3 numbers.
- **Honest limitation**: "Here's what we're not great at yet. Here's what we're doing about it."
- **Counter-intuitive result**: "We did X expecting Y. Instead we got Z. Here's what we learned."
- **Before / after with numbers**: snapshot of state N months ago vs today, with the 2-3 changes that moved the needle.
- **Deep dive on one metric**: pick one number, unpack the methodology, the caveats, the implications.

## What this file does NOT do

- ❌ Define the brand voice (→ `voice.md`)
- ❌ Define visual identity (→ `style-guide.md`)
- ❌ List personas (→ `personas.md`)
- ❌ Define the editorial calendar (→ `02-strategy/`)
