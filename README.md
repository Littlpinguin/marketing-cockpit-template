# Marketing Copilot Template

**The complete AI marketing department for Claude Code.** Clone it once per company, run the wizard, and get a role-based copilot that knows your brand by heart: strategy, social, email, web, design, slides, SEO — plus optional modules for video, n8n automation, performance reporting and outbound acquisition.

Built and battle-tested by [Pando Studio](https://pando-studio.com) across real client accounts. Free to use; a done-for-you installation & training service is available (see below).

---

## Architecture

```
Core (always on)                       Optional modules (/modules)
┌─────────────────────────────┐        ┌──────────────────────────────┐
│ 00-intel    live context    │        │ 08-video        Palmier Pro  │
│ 01-brand    doctrine (SSOT) │        │ 10-automations  n8n engine   │
│ 02-strategy calendar + KPIs │───────▶│ 11-reporting    client-site  │
│ 03→07, 09   production roles│        │                 dashboard    │
│ wizard + skills + agents    │        │ 12-acquisition  Lemlist MCP  │
└─────────────────────────────┘        │ + veille, Postiz, client FTP │
        │                              └──────────────────────────────┘
        ▼
 Everything reads 01-brand/ first — no generic AI voice, ever.
```

The heart of the system: **every production skill loads the brand doctrine before writing a single word** (voice, anti-AI-style rules, typography, asset library), and **every deliverable updates the central editorial calendar** (`02-strategy/calendar/calendar.md`) — idea → draft → to-validate → validated → published.

## Quickstart

```bash
# 1. Clone under a name that makes sense for you (or "Use this template" on GitHub)
git clone https://github.com/Littlpinguin/marketing-copilot-template.git my-company-copilot
cd my-company-copilot

# 2. Install Python deps
python3 -m pip install pyyaml python-dotenv requests

# 3. Open Claude Code
claude
```

Then run the wizard (paste on its own line):

```
/start-copilot
```

It fetches your website, analyzes your recent content, drafts your brand doctrine for your validation, wires your tools, and hands you a ready copilot in 30-60 minutes. Enable optional modules any time with `/modules`.

## Modules

| Module | What it adds | Prerequisites |
|---|---|---|
| `veille` | Multi-level market watch (competitors, sector, trends) feeding the calendar with **sourced** content ideas | — |
| `video` | AI-assisted video editing & captions | macOS + [Palmier Pro](https://github.com/palmier-io/palmier-pro) |
| `automatisations` | n8n workflow engine: meeting transcripts → `00-intel/`, scheduled watch, reports | Self-hosted n8n (VPS guide included) |
| `reporting` | Brand-styled performance dashboard hosted on the client's site (FTP + access code), monthly snapshots, month-to-month navigation, written analysis | ≥ 1 data source (GA4/GSC, Postiz, email tool) |
| `acquisition` | Outbound campaigns: copilot does ICP + brand-voice sequences + lists, [Lemlist MCP](https://developer.lemlist.com/mcp/setup) does sending & deliverability | Lemlist account |
| `publication-sociale` | Direct scheduling via [Postiz](https://postiz.com) (open source, self-hostable) | Postiz instance |
| `espace-client` | One password-protected space on your site: dashboard + shared presentations | FTP access |

## Data privacy — read this before wiring your CRM

The wizard connects to tools holding customer data (CRM, email marketing, analytics, meeting transcripts). Know your Claude plan before you do:

- **Commercial offerings** (Claude Team, Enterprise, API) do **not** train models on your data; API logs are deleted after 7 days.
- **Consumer plans** (Free/Pro/Max) default to **opt-in for model training** — check your settings before connecting business data.
- **EU data residency** requires Claude via AWS Bedrock (EU inference profiles) or Google Vertex AI (EU endpoints) — the direct API has no EU-only option.

References: [Anthropic training policy](https://privacy.claude.com/en/articles/7996868-is-my-data-used-for-model-training) · [Anthropic Trust Center](https://trust.anthropic.com). The wizard repeats this notice (with explicit confirmation) whenever a sensitive connector is configured.

**Security non-negotiables** (full rules in [`SECURITY.md`](SECURITY.md)): secrets in `.env` only (gitignored) — never in chat or commits; dry-run before any production push; verify API endpoints; never share transcripts containing client data.

## What "good" requires

This template produces an **operational framework**, not polished marketing on day one. Quality needs: a brand universe (the wizard shapes it with you), some public content to calibrate the voice against, and your real tools wired in. The more honest your inputs, the less generic the output.

## Professional installation

This template is the working tool of an externalized marketing & communications practice. If you'd rather have it installed, calibrated on your brand and your team trained on it, Pando Studio offers a done-for-you setup: [pando-studio.com](https://pando-studio.com).

## License & contributions

Open source — see [`LICENSE`](LICENSE). Improvements to the mechanics (skills, wizard, modules) are welcome via PR; brand-specific content stays in your fork. Maintainers contribute back with the built-in `backport-to-template` skill (automatic sanitization checklist).
