---
name: brand-discover
description: Analyze a company's public signals (website, recent blog articles, recent social posts, optional dropped brand docs) and propose a draft brand doctrine — design system, voice, vocabulary, personas, messaging framework — for human validation section by section. Writes the validated version to 01-brand/.
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

### Step 5 — Write validated doctrine

Once all five sections are validated (or explicitly skipped), write these files. Confirm path and content before each write:

- `01-brand/voice.md` — voice position + preferred/banned vocabulary + typography rules + signature phrases
- `01-brand/style-guide.md` — colors + fonts + border-radius + gradients + illustration style + banned visuals
- `01-brand/personas.md` — 2-4 personas, each with the full block, plus a persona × channel suggestion matrix (fill the matrix collaboratively if the user has opinions)
- `01-brand/messaging-framework.md` — central message, per-persona sub-messages, top 10 numbers, CTA types
- `01-brand/_gaps.md` — skipped items to revisit later (only if any)

Use the templates at `_templates/brand/` as the structure. Inject the validated values in place of placeholders.

### Step 6 — Fill root CLAUDE.md visual reference

Update the "Visual identity quick reference" section at the bottom of `CLAUDE.md` (root) with the validated values. This is the only place outside `01-brand/` where these values live, for fast access in every session.

### Step 7 — Wrap-up

Output:

> Brand doctrine v1 is written. Files:
> - `01-brand/voice.md`
> - `01-brand/style-guide.md`
> - `01-brand/personas.md`
> - `01-brand/messaging-framework.md`
> - (optional) `01-brand/_gaps.md`
>
> You can edit these any time with your text editor. The copilot reads them directly — no rebuild step required.
>
> Next: `/tools-setup` to tell me which tools you use (email platform, CRM, editorial calendar, events). This wires your tools into the right role folders and removes any that don't apply.

Return control. `/start-copilot` picks up from here.

## Failure modes to avoid

- **Don't invent values.** If you can't extract a color from the CSS, ask the user for a screenshot instead of guessing.
- **Don't collapse sections to save time.** Section-by-section validation feels slower but prevents rebuild loops later.
- **Don't write the 01-brand/ files before all sections are validated.** Partial writes create stale state.
- **Don't echo back any content the user typed in this session as a "brand voice sample"** unless they explicitly provided it as one. Conversation tone is not brand tone.
- **Don't trust your own confidence tags blindly.** If a section is tagged LOW, lead with that caveat in the prompt to the user.
- **Don't skip the refusal condition.** A brand profile from just the homepage is genuinely weak. Better to tell the user than to pretend the output is good.
