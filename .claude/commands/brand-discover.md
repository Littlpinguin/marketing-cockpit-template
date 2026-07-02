---
name: brand-discover
description: Analyze a company's public signals (website, recent blog articles, recent social posts, optional dropped brand docs) and propose a draft brand doctrine — design system, voice, vocabulary, personas, messaging framework — for human validation section by section. Then runs the strategy interview (business & marketing objectives, channels & cadence, real personas, customer journey). Writes the validated version to 01-brand/ and pre-fills 02-strategy/ (objectifs.md, parcours-client.md, kpi-framework.md, channel-strategy.md).
---

# /brand-discover — propose a draft brand doctrine

Load the `copilot-setup` skill first. Follow its preflight and security rules.

## Intent

Before the copilot can produce content that sounds like the company, the copilot has to understand the company. This command extracts as much as possible from public signals, presents a structured draft, and walks the user through it section by section. Writes happen only on explicit approval.

## Inputs expected

The wizard caller (`/start-copilot`) typically provides:
- Company website URL (required)
- Up to 5 recent blog article URLs
- Up to 10 recent social media post URLs (LinkedIn, X, Instagram)
- Optional brand docs dropped into `_bootstrap/inputs/` (PDF, DOCX, Markdown)

If this command is invoked directly, ask for these inputs in one batch before proceeding.

## Refusal condition

If the user provides **only** the website URL and no blog / social / brand docs, warn:

> I can draft a basic brand profile from just the homepage, but the voice recommendations will be generic. To get a voice that actually sounds like you, I need at least 3 recent content pieces — blog articles, LinkedIn posts, newsletters, anything you've written. Do you want to proceed with the website only, or provide more material? (proceed-thin / add-material)

## Flow

### Step 1 — Collect and fetch

Echo the security rule once:

> For the next step, I'll use `WebFetch` on the URLs you shared. I will not pull anything authenticated — only public pages. If any URL is behind a login, tell me and I'll skip it. The fetched content stays in my session memory and is not written anywhere until you approve.

Use `WebFetch` (or the runtime equivalent) in parallel on:
- Homepage + `/about` (or `/who-we-are`, `/company`) + one deeper product/service page
- Each blog article URL
- Each social post URL (if the platform allows unauthenticated read)

For each fetch, record:
- Plain text content
- Any detected color hex values in CSS
- Any detected font-family declarations
- The page title and meta description

If an URL fails, note it and continue. Do not retry automatically more than once.

Also, read `_bootstrap/inputs/` recursively:
- Text formats (`.md`, `.txt`, `.html`): read directly
- PDF: run `pdftotext` if available; if not, skip and flag for the user
- DOCX, PPTX: flag as unsupported and ask the user to paste the relevant section

### Step 2 — Analyze and synthesize

Build a structured draft **in memory only**. Do not write to disk yet.

#### 2.1 Identity

Extract from homepage and about page:
- **Company name** (from `<title>` or H1)
- **Short name** (often mentioned later in the body)
- **Tagline** (hero section)
- **Positioning** (1-2 sentences combining about + hero)
- **Mission** and **vision** (if stated)
- **Sector** (infer from page content)
- **Audience descriptor** (from hero or about)
- **HQ and founders** (from about or footer)
- **Main marketing contact** (from footer, team page, or ask the user)

If the footer mentions "a registered trademark of …", record the legal entity too.

#### 2.2 Visual identity

From CSS and rendered page:
- **Primary color**: the most-used brand color (not text colors). Look at buttons, links, highlights.
- **Accent color**: the second-most-used brand color.
- **Dark and light neutrals**: background and primary text.
- **Signature gradient**: if detected.
- **Primary font**: from `font-family` declarations, filtered for the main display typography (not fallback stacks).
- **Border-radius**: from buttons/cards.
- **Illustration style**: classify what you see in hero images — photo, line art, isometric, 3D, mixed, geometric, collage.
- **Banned visual tropes**: infer from the current style (e.g. if the site uses line art exclusively, recommend banning stock photos).

If CSS is minified or behind a framework (Next.js, React) and you can't extract cleanly, ask the user to paste the output of `getComputedStyle` on a sample element, or take a screenshot and ask them to send it.

#### 2.3 Voice and vocabulary

From the blog articles and social posts:
- **Voice position**: where on the axes formal/casual, technical/accessible, confident/humble, playful/serious does this company sit? Give two sentences, not one label.
- **Preferred vocabulary**: 10-15 words or short phrases that appear repeatedly and feel intentional.
- **Banned vocabulary**: 5-10 words the company seems to actively avoid (you notice this by seeing content where a corporate writer would have used a word but this one doesn't). Flag cliches the brand would likely reject.
- **Signature phrases or taglines**: repeated formulations that feel like "house style."
- **Key numbers**: statistics that appear in multiple pieces ("100+ customers", "99.9% uptime", etc.). Mark each as "recurring (seen N times)" so the user can verify before adoption.
- **Typography rules**: em dashes vs en dashes vs hyphens, serial comma, capitalization in headings.

Be honest about confidence. If you only have 2 blog posts, say "this voice read is tentative, would benefit from more samples."

#### 2.4 Personas

Look for audience signals:
- Explicit mentions ("we serve developers", "for HR leaders")
- Pain points addressed in the content
- Vocabulary that targets a specific audience
- Case study subjects if visible

Propose 2-4 personas. Each persona has:
- Name + role (e.g. "Thomas, 45, VP IT")
- Top 3 goals
- Top 3 frustrations
- What they expect from the company
- Primary channels they use
- The brand's main message to them
- **Hypotheses to confirm in the strategy interview (Step 5)**: likely buying triggers, likely objections, vocabulary they seem to use, and any anti-persona candidates (audiences the site clearly does not address). Label these explicitly as *hypotheses* — the real answers come from the user in Step 5.5, not from inference.

Mark confidence low/medium/high per persona.

#### 2.5 Messaging framework (light)

- Central message (one sentence)
- One sub-message per persona
- Top 10 key numbers (from 2.3)
- Typical CTAs detected on the site

### Step 3 — Present the draft structured

Output the draft as one big readable block, Markdown. Sections clearly delimited. Each section marked with a confidence tag:

```
## Draft brand profile

### 1. Identity  — confidence: HIGH
Name: Acme Inc.
Short name: Acme
Tagline: Ship faster, ship better
...

### 2. Visual identity  — confidence: MEDIUM
Primary color: #1E40AF  (detected on 12+ elements)
Accent: #F59E0B  (buttons, highlights)
...

### 3. Voice & vocabulary  — confidence: MEDIUM
Voice position: Expert accessible. The company writes with the rigor of engineering docs but the warmth of a peer — no marketing jargon.
Preferred vocabulary: ship, deploy, developer, platform, team, reliability, boring (positive), ...
Banned vocabulary: solution, innovation, game-changer, disrupt, revolutionize, synergy, ...
Signature phrases: "Ship faster, ship better", "Boring is the new exciting"
Recurring numbers: "99.9% uptime" (seen 4 times), "10k+ developers" (seen 3 times), ...
Typography rules: no em dashes, serial comma used, sentence case in headings

### 4. Personas  — confidence: LOW (only 2 content samples)
Persona 1: "Thomas, 45, VP IT" — confidence LOW
  Goals: [...]
  Frustrations: [...]
  ...

### 5. Messaging framework (light)  — confidence: MEDIUM
Central message: ...
```

At the end, list **gaps** — things you couldn't extract:

```
### Gaps I couldn't fill
- Founder names (not on the about page)
- Which CRM / email tool is used (will ask in /tools-setup)
- Legal entity name for footer
```

### Step 4 — Section-by-section validation

Ask:

> I'll walk you through the draft one section at a time. For each, tell me:
> ✅ **correct** — lock it in as-is
> 🟠 **partially correct** — describe what to change
> 🔴 **wrong** — explain and we rebuild this section
> **skip** — move on, come back later
>
> Ready to start with Section 1 (Identity)?

Process sections in order: identity → visual → voice → personas → messaging. For each:

1. Show only that section (the user can re-read it).
2. Ask for the verdict.
3. If 🟠 or 🔴, ask precisely what's wrong, edit the section in memory, then re-show before confirming.
4. On ✅, move to the next section.

If the user says "skip", leave the section as `{{TODO}}` markers in the eventual file and note in `01-brand/_gaps.md`.

### Step 5 — Strategy interview (objectives, channels, personas depth, journey)

The brand doctrine says how the company speaks; this step captures **what marketing must achieve and for whom**, so `02-strategy/` starts populated instead of placeholder-ridden. Announce it:

> The brand sections are locked. Before writing the files, I need 15-20 minutes of strategy input: your objectives, your channels, your real personas and their journey. These answers pre-fill `02-strategy/objectifs.md`, `kpi-framework.md`, `parcours-client.md`, `channel-strategy.md` and complete `01-brand/personas.md`. Short, concrete answers beat polished ones — I'll do the reformulation.

Run the sub-steps in order. Everything stays in memory; writes happen in Step 6. Each sub-step supports **skip** (leave `{{TODO}}` markers and log in `01-brand/_gaps.md`).

#### 5.1 Business objectives (12 months)

Ask the leader directly — no reformulation games here, these come from the top:

> What are the 2-3 business objectives of the company over the next 12 months, and for each: how will you know it's reached? (revenue target, number of new clients on a segment, market position…)

Record 2-3 objectives, each with horizon and success indicator. → `objectifs.md` §1 (`BIZ-1` … `BIZ-3`).

#### 5.2 Marketing objectives of the quarter (SMART)

Ask what marketing must deliver **this quarter**, in the user's own words. Then reformulate **2-4 objectives maximum** as SMART (Specific, Measurable, Achievable, Realistic, Time-bound), each explicitly linked to a `BIZ-x` and a persona, and present them for validation — the user's verdict rules, not your phrasing.

For each objective's indicator, capture the **starting value**:
- Ask the user for the current figure, or
- If GA4 / Search Console or the emailing tool connectors are already configured (re-run scenario — check `.setup-completed`), offer to read the value from the source instead.
- If neither is available, mark the value `à relever` and log it in `_gaps.md`. **Never invent a starting value.**

→ `objectifs.md` §2 (`OBJ-1` … `OBJ-4`).

#### 5.3 Activated channels and sustainable cadence

Ask which channels are **actually activated** (LinkedIn, newsletter, blog/SEO, site, events, other) and, per channel, the cadence the team can genuinely hold — an honest "1 post/week" beats an abandoned "3 posts/week".

This list **filters the tables**: at write time (Step 6), remove the rows of non-activated channels in `objectifs.md` §3, `channel-strategy.md` and `kpi-framework.md`. Only what will really be measured stays. The cadences also feed the `{{CONTENT_CADENCE_*}}` placeholders reused by `/tools-setup`.

#### 5.4 Definitions: conversion and qualified lead

Two direct questions:

> Concretely, what counts as a **conversion** on your site? (demo booked, contact form, signup, quote request…)
> And what makes a lead **qualified** in your eyes? (role, budget, timing, structure size…)

→ `{{TYPE_CONVERSION}}` (+ GA4 event name if known) and the "Leads qualifiés" criteria row in `kpi-framework.md`, reused in `objectifs.md` §3.

#### 5.5 Real personas (2-4)

Turn the draft personas validated in Step 4 from *inferred* to *real*. For each persona, ask in one batch:

- **Role and structure**: exact function, size/type of organization, who else weighs on the decision
- **Contact triggers**: what makes this persona reach out to you (the event, deadline or incident that starts the search)
- **Objections heard in meetings**: the 2-3 objections you actually hear in sales conversations — and **how you usually answer each one**
- **Information channels**: where they really get informed (LinkedIn, trade newsletters, communities, events, Google queries)
- **Vocabulary**: their words to use, and the jargon that loses or annoys them

Then close with anti-personas:

> To whom do you say **no**? Which requests or client profiles do you turn down, and why?

Record 1-2 anti-personas with the reason. → `personas.md` (full per-persona blocks: rôle et contexte, déclencheurs d'achat, objections + réponses, canaux fréquentés, vocabulaire, message principal — plus the anti-personas section).

#### 5.6 Journey questions per stage

For each persona × stage (découverte / considération / décision / fidélisation), **propose** the question the persona is asking at that stage, deduced from the triggers and objections collected in 5.5 — do not ask the user to fill a 16-cell matrix cold. Present the pre-filled table; the user validates or corrects line by line. Map each cell to a content/channel suggestion consistent with the activated channels of 5.3. → `parcours-client.md`.

#### 5.7 First signals from `00-intel/` (if already fed)

Check whether `00-intel/` already contains files (`inbox/`, `interne/`, `clients/`, `prospects/` non-empty). If yes, offer:

> You already have field material in `00-intel/`. Want me to scan it for first signals — recurring questions, objections, vocabulary — to seed the "signaux 00-intel" sections of `personas.md` and the journey map?

On yes: read the files, extract signals **reformulated and anonymized** (never verbatim, never a name without consent), present them for approval before inclusion. On no or if empty, skip silently.

### Step 6 — Write validated doctrine and strategy

Once all sections are validated (or explicitly skipped), write these files. Confirm path and content before each write:

- `01-brand/voice.md` — voice position + preferred/banned vocabulary + typography rules + signature phrases
- `01-brand/style-guide.md` — colors + fonts + border-radius + gradients + illustration style + banned visuals
- `01-brand/personas.md` — 2-4 personas with the full v2 block each (rôle et contexte, déclencheurs d'achat, objections + réponses habituelles, canaux fréquentés, vocabulaire à utiliser/éviter, message principal, section « signaux 00-intel »), plus the anti-personas section — all fed by Step 5.5 (and 5.7 if run)
- `01-brand/messaging-framework.md` — central message, per-persona sub-messages, top 10 numbers, CTA types
- `01-brand/_gaps.md` — skipped items to revisit later (only if any)
- `06-graphic-design/presentations/tokens.css` — slide CSS variables. Substitute the same colour and font placeholders as `style-guide.md` (`BRAND_COLOR_PRIMARY`, `BRAND_COLOR_ACCENT`, `BRAND_COLOR_DARK`, `BRAND_COLOR_LIGHT`, `BRAND_GRADIENT`, `BRAND_FONT_PRIMARY`, `BRAND_FONT_SECONDARY`). The `_deep` / `_soft` colour variants resolve via `color-mix()` at runtime — no manual derivation needed.

Read `_templates/brand/voice.md`, `_templates/brand/style-guide.md`, `_templates/brand/messaging-framework.md`. Substitute the validated values in place of `{{PLACEHOLDERS}}`. Write the result to `01-brand/<same-filename>.md`. Apply the same substitution pass to `06-graphic-design/presentations/tokens.css` so the slides skill is ready to inline a brand-aligned design system.

**Exception — `personas.md`**: the reference structure is the v2 file already present at `01-brand/personas.md` (rôle et contexte, déclencheurs d'achat, objections, canaux, vocabulaire, message principal, signaux 00-intel, anti-personas). Edit it **in place**, replacing its `{{PLACEHOLDERS}}` and duplicating the persona block as needed — do not use `_templates/brand/personas.md` if its structure diverges (it may still carry the v1 layout).

Then write the strategy files from Step 5. These four files already live in `02-strategy/` with their v2 structure — **edit them in place**, replacing the `{{PLACEHOLDERS}}` with the validated answers (do not restructure them):

- `02-strategy/objectifs.md` — §1 business objectives (5.1), §2 SMART marketing objectives with starting values (5.2), §3 per-channel targets **filtered to the activated channels** (5.3) with the conversion definition (5.4); fill trimestre en cours, date de révision, validé par, and the first line of the revision history
- `02-strategy/parcours-client.md` — one validated table per persona (5.6); duplicate the persona block for each persona beyond the second
- `02-strategy/kpi-framework.md` — KPI rows filtered to activated channels (5.3), definitions of conversion and qualified lead (5.4), measurement sources named after the actual tools when known (otherwise leave the tool placeholder for `/tools-setup`)
- `02-strategy/channel-strategy.md` — keep only the rows of activated channels, with cadence (5.3) and personas per channel

### Step 7 — Fill root CLAUDE.md visual reference

Update the "Visual identity quick reference" section at the bottom of `CLAUDE.md` (root) with the validated values. This is the only place outside `01-brand/` where these values live, for fast access in every session.

### Step 8 — Wrap-up

Output:

> Brand doctrine and strategy v1 are written. Files:
> - `01-brand/voice.md`
> - `01-brand/style-guide.md`
> - `01-brand/personas.md` (personas réels + anti-personas)
> - `01-brand/messaging-framework.md`
> - `02-strategy/objectifs.md` (cascade business → marketing SMART → cibles par canal)
> - `02-strategy/parcours-client.md` (questions par étape × persona)
> - `02-strategy/kpi-framework.md` (définitions, dont conversion et lead qualifié)
> - `02-strategy/channel-strategy.md` (canaux activés + cadence)
> - `06-graphic-design/presentations/tokens.css` (slide design system)
> - (optional) `01-brand/_gaps.md`
>
> You can edit these any time with your text editor. The copilot reads them directly — no rebuild step required. Objectives are revised each quarter (`02-strategy/objectifs.md` header tells you when).
>
> Next: `/tools-setup` to tell me which tools you use (email platform, CRM, editorial calendar, events). This wires your tools into the right role folders and removes any that don't apply.

Return control. `/start-copilot` picks up from here.

## Failure modes to avoid

- **Don't invent values.** If you can't extract a color from the CSS, ask the user for a screenshot instead of guessing.
- **Don't invent starting values or KPI baselines.** A figure comes from the user or from a configured connector (GA4, emailing tool) — otherwise it's `à relever`, logged in `_gaps.md`.
- **Don't accept a vague marketing objective.** "Be more visible" is not an objective; reformulate it SMART and get explicit validation of the reformulation.
- **Don't skip the anti-persona question or the objections-heard-in-meetings question.** They produce the most useful content angles of the whole interview.
- **Don't copy verbatim from `00-intel/`** into any strategy or persona file — reformulate and anonymize, always.
- **Don't collapse sections to save time.** Section-by-section validation feels slower but prevents rebuild loops later.
- **Don't write the 01-brand/ or 02-strategy/ files before all sections are validated.** Partial writes create stale state.
- **Don't echo back any content the user typed in this session as a "brand voice sample"** unless they explicitly provided it as one. Conversation tone is not brand tone.
- **Don't trust your own confidence tags blindly.** If a section is tagged LOW, lead with that caveat in the prompt to the user.
- **Don't skip the refusal condition.** A brand profile from just the homepage is genuinely weak. Better to tell the user than to pretend the output is good.
