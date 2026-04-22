# Bootstrap inputs — drop zone

Optional. Drop any existing brand or company material **before** running `/brand-discover`. The wizard will read everything here and fold it into the draft doctrine, so you don't retype information that already exists.

## What to drop here

Anything that describes your company, brand, voice, or strategy:

- `brand-guide.pdf` (or `.md`, `.docx`)
- `editorial-charter.md`
- `pitch-deck.pdf` or `.pptx`
- `personas.md`
- `vision-mission.md`
- `positioning-statement.md`
- `messaging-framework.md`
- `writing-samples/` — a folder with 5-10 of your best past posts, emails, or articles
- `website-dump.md` — if Claude can't reach your website, paste the homepage text here

## Accepted formats

- **Markdown (`.md`)** and **plain text (`.txt`)** — read as-is
- **PDF** — extracted via `pdftotext` if available
- **Word (`.docx`)** or **PowerPoint (`.pptx`)** — wizard will ask you to export as PDF or paste the relevant section
- **Screenshots (`.png`, `.jpg`)** — described / OCR'd best-effort

## What the wizard does with this content

`/brand-discover` reads this folder recursively, cross-references with `WebFetch` of your website, detects contradictions (e.g. website says "100+ clients", pitch deck says "50+"), and builds a draft company profile. Nothing is written to `01-brand/` until you validate section by section.

## Privacy

- This folder is **gitignored** by default. Your raw material stays local.
- After setup, these files move to `.setup-archive/v0.2-inputs/` so the live tree stays clean.
- The wizard writes to `01-brand/` — those files are tracked. Review before pushing a public repo.

## Re-running later

To refresh the brand profile with new material, drop new files here and run `/brand-discover` again. The wizard is idempotent — it asks what has changed rather than starting from scratch.
