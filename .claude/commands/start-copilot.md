---
name: start-copilot
description: Entry point of the Marketing Copilot wizard. Run once after cloning the template. Walks the user from a fresh repo to a fully configured, company-specific copilot in 30-60 minutes.
---

# /start-copilot — wizard entry point

Load the `copilot-setup` skill first. Do not skip it.

## Intent

Transform this empty template into a production-ready marketing copilot for one specific company, with:
- A validated brand doctrine (voice, design system, personas)
- A populated strategy layer: business & marketing objectives, activated channels & cadence, real personas with objections, customer journey (`02-strategy/`)
- Connectors wired for the tools the company actually uses
- Skills personalized with brand-specific rules
- Optional modules enabled per need, plus brand-compliant image generation
- A clean `.setup-completed` that locks in the configuration

## Flow overview

The wizard orchestrates the sub-commands below. You may run them one by one if you prefer granular control; this entry point chains them with confirmation between each.

1. **Preflight and welcome** (inline, no sub-command)
2. **`/brand-discover`** — public signals → draft doctrine → human validation → **strategy interview** (objectives 12 mois + trimestre SMART, canaux + cadence, personas réels, définitions conversion/lead, parcours client) → write `01-brand/` + pre-fill `02-strategy/`
3. **`/tools-setup`** — pick tools per category → generate role CLAUDE.md → update `.env.example`
4. **`/modules`** — optional, enable optional modules (video, automatisations, reporting, acquisition, veille, publication-sociale, espace-client)
5. **`/validate-setup`** — placeholder lint + sample generation + voice check → write `.setup-completed`

## Step 1 — Welcome and preflight

Output (adapted to the user's apparent expertise):

> Welcome. I'll help you turn this template into a copilot tailored to your company. This takes 30-60 minutes depending on how much material you already have. I won't produce any content until you've validated every section of the draft brand doctrine.
>
> Before we start, three things you should know:
>
> 1. I will never ask you to paste API keys in chat. Keys go into the `.env` file, which stays local and is gitignored.
> 2. Every draft I produce is for your review. Nothing gets written to operational folders until you explicitly approve.
> 3. You can interrupt at any time and resume later by running `/start-copilot` again, or by running individual sub-commands.
>
> Full security rules: `SECURITY.md`.

Then run preflight checks (from `copilot-setup` skill):
- Model is Sonnet 4.6 or better
- Git working tree is clean (or user confirms dirty state)
- Python dependencies are installed
- `.env` exists
- `.setup-completed` does not exist (if it does, offer to re-run individual commands instead)

If any check fails, surface the issue, offer remediation, and pause.

## Step 2 — Ask: how much material does the user have?

Output:

> To personalize this template, I work best with public signals about your company. Before we proceed, please share as much of the following as you can — you can paste URLs or drop files into `_bootstrap/inputs/`:
>
> 1. **Company website URL** — I'll fetch the homepage, about page, and one or two deeper pages.
> 2. **Up to 5 recent blog article URLs** — to calibrate your long-form voice.
> 3. **Up to 10 recent social media post URLs** (LinkedIn, X, Instagram) — to calibrate your short-form voice.
> 4. **Optional**: drop any existing brand doc (PDF, DOCX, Markdown) into `_bootstrap/inputs/`. I'll read them too.
>
> Paste the URLs here when you're ready. If you don't have blog or social presence yet, that's fine — tell me and I'll work from the website alone.

Wait for the user response. Collect the URLs and note them. Do not call `WebFetch` yet — `/brand-discover` does that.

## Step 3 — Chain sub-commands with confirmation

After the user has shared material (or confirmed they have none beyond the website), announce the chain:

> I'll now run the following in sequence. After each, I'll pause so you can review before continuing:
>
> 1. `/brand-discover` — analyze your signals, propose a design system, voice, and draft personas, then run the strategy interview: your business and marketing objectives, activated channels and sustainable cadence, real personas (triggers, objections heard in meetings, vocabulary, anti-personas), definitions of a conversion and a qualified lead, and the customer journey questions. (20-35 min)
> 2. `/tools-setup` — ask which tools you use (email platform, CRM, editorial calendar, etc.) and wire them. (5-10 min)
> 3. `/modules` — enable any optional modules you need (video, automatisations, reporting, acquisition, veille, publication-sociale, espace-client). (2-5 min, optional)
> 4. `/validate-setup` — a final lint, a sample post for you to sanity-check the voice, then I write `.setup-completed`.
>
> Ready to start with `/brand-discover`? (yes / no / go slower)

On "yes", invoke `/brand-discover` with the URLs collected above.

## Step 4 — Between each sub-command, checkpoint

After each sub-command completes, output a one-screen recap:

> **`/brand-discover` complete.**
>
> Files written: `01-brand/voice.md`, `01-brand/style-guide.md`, `01-brand/personas.md`, `01-brand/messaging-framework.md` — and the strategy layer: `02-strategy/objectifs.md`, `02-strategy/parcours-client.md`, `02-strategy/kpi-framework.md`, `02-strategy/channel-strategy.md`.
> Anything you'd like to revisit before moving on? (yes / no)

If yes, return to the sub-command or loop back. If no, announce the next.

## Step 5 — Post-validation cleanup

Once `/validate-setup` succeeds:

1. Move `_bootstrap/inputs/` contents (if any) into `.setup-archive/v0.2-inputs/` to declutter the live tree.
2. Offer the first five recommended actions:
   - Read the generated `01-brand/voice.md` and correct anything I misread.
   - Try `/health-check` to confirm everything is wired.
   - Draft your first LinkedIn post by asking "write a LinkedIn post about X" — brand-check will run automatically.
   - Drop a meeting transcript into `00-intel/inbox/` and ask for a classification session (see `00-intel/CLAUDE.md`).
   - Customize the brand-check rules in `.claude/skills/brand-check/SKILL.md` if you want stricter typography.

## Failure modes to avoid

- **Don't ask for all information upfront.** Let sub-commands ask what they need, when they need it.
- **Don't write to operational folders from this command.** Only sub-commands do.
- **Don't enable optional modules silently.** Module state changes only through `/modules`, which checks prerequisites and records state in `.setup-completed.modules`.
- **Don't skip the security echo at step 1.** Secrets discipline is non-negotiable.
- **Don't produce any marketing content during setup.** Production skills activate only after `.setup-completed` exists.

## If the user wants to restart

If at any point the user wants to wipe and restart:

```bash
rm -rf 01-brand/*.md  # keep CLAUDE.md
rm .setup-completed
# Re-run /start-copilot
```

Warn before any destructive action. Always offer to back up to `.setup-archive/` first.
