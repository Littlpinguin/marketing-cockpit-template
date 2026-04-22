# Setup guide

This document explains the full setup flow, step by step, for both **human-directed** and **Claude-directed** installations.

## TL;DR (for the impatient)

```bash
git clone https://github.com/YOUR_USERNAME/marketing-copilot-template.git your-company-copilot
cd your-company-copilot
pip install qdrant-client google-genai python-dotenv pyyaml requests mcp
claude .   # Claude detects the empty setup and starts the interview automatically
```

Follow the interview. Expect 20-40 minutes. Done.

## Prerequisites

### Software

- **Python 3.11 or later** — required for the Qdrant sync pipeline and the MCP server
- **[Claude Code](https://claude.com/claude-code)** — the CLI that powers the copilot
- **[Claude Opus 4.6](https://claude.com/claude-opus)** — strongly recommended. Smaller models work for basic operation but degrade noticeably on strategic tasks
- **git** — to clone the template and track your customizations
- **macOS** — for the launchd weekly cron (Linux/WSL users can adapt the script to systemd or crontab)

### Accounts

- **[Google AI Studio](https://aistudio.google.com/apikey)** account — for `GOOGLE_AI_API_KEY`. Required. Powers embeddings, enrichment, AND brand-compliant image generation (Gemini nano-banana-pro). One key, three capabilities.
- **[Qdrant Cloud](https://cloud.qdrant.io)** account — optional but strongly recommended. The free tier (1 GB) is enough for a company with up to ~3000 pieces of content. See "Why Qdrant matters" below.
- **Your marketing stack** — whatever tools you already use for editorial calendar, email marketing, knowledge base, events, CRM. You'll tell Claude about them during the interview and it will connect the ones that have built-in connectors.

## Installation steps

### 1. Clone and rename

```bash
git clone https://github.com/YOUR_USERNAME/marketing-copilot-template.git my-copilot
cd my-copilot
```

Rename the folder to something meaningful for your company. The template has no hardcoded paths to itself.

### 2. Install Python dependencies

```bash
python3 -m pip install qdrant-client google-genai python-dotenv pyyaml requests mcp
```

If you use a virtual environment, activate it first.

### 3. Create your `.env` file

```bash
cp .env.example .env
```

You can leave it empty for now — the bootstrap interview will fill it as you make choices. Or, if you already know some of your API keys, fill them now to skip those prompts.

### 4. Drop any existing brand material into `_bootstrap/inputs/`

This is optional but highly recommended. See `_bootstrap/inputs/README.md` for the list of useful documents. The more you drop, the less you have to type during the interview.

### 5. Open Claude Code at the project root

```bash
claude .
```

Make sure you're on Opus 4.6 (`/model` in Claude Code shows the current model).

### 6. Let the interview run

Claude detects that `.setup-completed` does not exist and automatically starts the bootstrap interview. The interview has 5 phases:

- **Phase 0 — Discovery**: Claude fetches your website and reads the files in `_bootstrap/inputs/`
- **Phase 1 — Identity validation**: Claude presents what it understood and you correct it section by section
- **Phase 2 — Personas**: build 2-4 personas collaboratively
- **Phase 3 — Functionalities**: pick your editorial calendar, email marketing, knowledge base, events platform, CRM, Qdrant, and image generation. Tool-agnostic — swap any tool without changing the architecture.
- **Phase 4 — Skills personalization**: customize the 9 skills to match your voice
- **Phase 5 — Wrap-up**: Claude writes `.setup-completed`, runs a verification, and proposes your first 5 actions.

### 7. Install the weekly cron (optional but recommended)

Once bootstrap is complete, install the launchd job that keeps your memory in sync:

```bash
cp _integrations/qdrant/cron/help.{{PROJECT_SLUG}}.qdrant-weekly-sync.plist \
   ~/Library/LaunchAgents/
launchctl load ~/Library/LaunchAgents/help.{{PROJECT_SLUG}}.qdrant-weekly-sync.plist
launchctl list | grep qdrant-weekly-sync
```

Replace `{{PROJECT_SLUG}}` with the slug you chose during the interview (also visible in the generated plist filename).

## Why Qdrant matters (decide before Phase 3)

The template works without Qdrant, but with only about 20% of its value. Here's what you lose without Qdrant:

1. **No anti-repetition check**. The brand-check skill can't compare a new draft against past publications. You'll accidentally ship the same LinkedIn post twice a year because Claude forgot. Qdrant stores every piece of content as a 3072-dimension vector; a similarity search takes ~500ms and returns the top 5 nearest drafts with their scores.

2. **No cross-channel consistency**. A claim in this week's newsletter may contradict last month's blog post, and nobody will notice until a reader points it out. Qdrant lets every agent verify "is this claim consistent with what we've said before?"

3. **No fast access to the brand doctrine**. Each agent has to re-read `01-brand/` (1000+ lines) every session to ground itself. With Qdrant, a targeted query like `qdrant_search("tone rules for LinkedIn", filter="brand")` returns the exact 3 relevant passages in 500ms. Your context window stays focused.

4. **No meeting-to-content surfacing**. Your transcripts and strategic decisions stay invisible to the content agents. With Qdrant, a question like "what did we decide about Odoo positioning in the last sync?" returns the relevant bullet from last week's meeting.

Qdrant costs nothing to start with (free tier covers most small teams) and takes 5 minutes to activate. The bootstrap interview will walk you through it in Phase 3.6.

## Troubleshooting

### "Cannot find module 'qdrant_client'"

```bash
pip install qdrant-client google-genai python-dotenv pyyaml requests mcp
```

### Qdrant returns 403 on every endpoint

You probably have an account management key instead of a cluster API key. Go to Qdrant Cloud → Access Management → API Keys → Create Database API Key, then select your cluster. The correct key looks like a JWT (`eyJ...`), not `uuid|secret`.

### Gemini returns "model not found"

The embedding model is `gemini-embedding-001` (not `text-embedding-004`). The image model is `gemini-3-pro-image-preview`. If either is missing from your API tier, check your Google AI Studio account tier and region.

### launchd cron doesn't fire on Sunday

1. Check the plist is loaded: `launchctl list | grep qdrant-weekly-sync`
2. Check the wrapper is executable: `ls -la _integrations/qdrant/cron/run-weekly-sync.sh`
3. Check the log: `tail _integrations/qdrant/logs/cron-weekly.stderr.log`
4. Manually trigger: `launchctl start help.{{PROJECT_SLUG}}.qdrant-weekly-sync`

### The interview is stuck at Phase 0 (website fetch)

Claude may not have `WebFetch` enabled in your session. Ask the user to paste their homepage text into `_bootstrap/inputs/website-dump.md` and continue.

### I want to restart the bootstrap from scratch

```bash
rm .setup-completed
rm .env
cp .env.example .env
claude .
```

Claude will restart the interview. Existing files in `01-brand/`, `.agents/skills/`, etc. will be overwritten — back them up first if you're iterating.

## Uninstalling

```bash
launchctl unload ~/Library/LaunchAgents/help.{{PROJECT_SLUG}}.qdrant-weekly-sync.plist
rm ~/Library/LaunchAgents/help.{{PROJECT_SLUG}}.qdrant-weekly-sync.plist
rm -rf my-copilot
```

Your Qdrant Cloud cluster remains — delete it manually from the Qdrant dashboard if you no longer need it.
