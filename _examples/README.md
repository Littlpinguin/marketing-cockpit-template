# _examples/

Fictional but realistic content from a made-up company ("Acme SaaS") for seeding the copilot's memory when you don't yet have a corpus of your own published content.

## What's here

```
_examples/acme-saas/
├── brand/                 ← voice, style-guide, personas, messaging (for brand-discover reference, not ingestion)
├── linkedin/              ← 5 LinkedIn posts
├── newsletter/            ← 2 newsletter editions
└── articles/              ← 1 blog article
```

## Who should use this

If you're running `/seed-corpus` on day one and don't yet have published content to ingest, this starter pack gives the copilot calibration examples. It prevents the "blank state" problem — empty archive folders mean anti-repetition checks return nothing, skills have no tone references, and first drafts read generic.

## Important

- These examples are **fictional**. They describe "Acme SaaS" — not your company.
- Files ingested from `_examples/` are tagged with `example=true` in Qdrant so anti-repetition queries can filter them out.
- Replace progressively with your real content. Once you've published 3-5 real pieces in a channel, you can safely delete the example files for that channel.

## License

Public domain. Do what you want.
