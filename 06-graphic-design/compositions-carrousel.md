# Carousel composition system

Reference layout system for LinkedIn / social carousels (portrait, **1080×1350**, 4:5). Grounded in senior grid practice (Müller-Brockmann's *Grid Systems*, *The Vignelli Canon*, the Swiss typographic style, the Van de Graaf / Tschichold page canon) and in the hard constraints of mobile legibility (WCAG + screen physics). This is the source of truth for **any carousel or multi-slide visual** produced under *Sub-area 1 — Visuals*; the `image-generation` skill and any carousel layout in `./templates/` inherit from it.

> **Founding principle.** "Premium" is not a magic layout. It is three things: a **constant grid**, **disciplined alternation** of compositions (never two neighbouring slides on the same skeleton), and the **absence of AI tells**. Grid constancy, more than any single effect, produces the "designed by a senior" feeling.

All colours, fonts and illustrations come from the brand tokens (`presentations/tokens.css` → `../01-brand/style-guide.md`). Nothing below is hardcoded to a brand — the numbers are canvas geometry and mobile-legibility constants, not style choices.

---

## 1. Reference grid (set once, valid for every slide)

- **Canvas**: 1080 × 1350 px (4:5 portrait).
- **Margins**: **80 px side · 120 px top · 160 px bottom** → a live content block of **920 × 1070 px**, centred. The 160 px floor keeps vital content clear of the zone where the platform overlays the slide counter and reactions.
- **Columns**: 12 columns of 58 px, 24 px gutters (12×58 + 11×24 = 960).
- **Strong focal point**: upper-right, around (720, 500) — a rule-of-thirds / φ (0.618) intersection. Anchor the key element on an intersection, **never on the geometric centre** (except the closing slide).
- **Baseline**: 9 px step; body leading 45 px.
- **Background**: a brand decision — commit to **one** neutral (`--brand-neutral-dark` **or** `--brand-neutral-light`) and hold it across the whole set. Vary only the shade for rhythm (a subtle radial toward a deeper tone, positioned differently per slide); never flip light↔dark mid-set. Line-art illustration must be drawn for the chosen background (light-on-dark or dark-on-light), and ink + accent must clear WCAG against it (§3).

## 2. Mobile-safe type scale (non-negotiable)

A 1080 px canvas renders at ~390 px on a phone: **perceived size ≈ canvas size × 0.36**. A 30 px body is then only ~11 px on screen — unreadable. Floor table:

| Role | Floor | Comfort target | ≈ on screen (target) |
|---|---|---|---|
| Hook hero (short, cover slide) | 110 px | **130–180 px** | 47–65 px |
| Slide title | 72 px | **88–110 px** | 32–40 px |
| Subtitle | 52 px | **60–72 px** | 22–26 px |
| Body / bullet | **44 px** | **48–56 px** | 17–20 px |
| Caption / source | **28 px** | **32–36 px** | 11–13 px |
| Folio, legal mention | 26 px | 30 px | ~10 px |
| Number anchor (composition 3) | 200 px | **240–330 px** | — |
| Body leading | 1.4 | 1.4–1.6 | — |
| Title / display leading | 1.0 | 1.05–1.15 | — |

Floors assume a ~1080 px-wide canvas; scale proportionally for other widths. These map to the `--carousel-fs-*` tokens in `presentations/tokens.css`.

**Families.** Body in `--font-display` at Regular/Medium, titles at SemiBold/Bold, display at ExtraBold. If the brand declares a secondary script / accent family, reserve it for **one** accent word or hero number per slide — never a whole title. Minimum weight for small text: **500** (a thin weight breaks under the feed's JPEG compression).

## 3. Colour & contrast (WCAG)

Always compute contrast against **your chosen background**, not a nominal one.

- **Ink and accent must reach ≥ 7:1** for body and small text — well above the 4.5:1 WCAG AA floor. The feed compresses and shrinks, so buy margin. Ink = the opposite neutral to the background (`--brand-neutral-light` on a dark bg, `--brand-neutral-dark` on a light one); accent = `--brand-primary` / `--brand-secondary`. Use these for hook, body and numbers.
- **Metadata / subtitles / sources** may sit on a softer tint but must still clear ≥ 4.5:1 (large text ≥ 3:1).
- **Never mute a caption below its floor to "make it discreet".** Drop the size, or lower the ink's opacity while keeping the ratio above the floor — never introduce a low-contrast grey.
- **One accent per slide.** Never a different accent colour from one slide to the next.

## 4. Density & one-second legibility

- **One idea per slide.** Two ideas → two slides.
- **≤ 30 words per slide**; **6–8 body lines** maximum.
- **Line length 30–50 characters** (guaranteed by a ~880 px column at body size; if it overflows, narrow the column or split the slide).
- **Hook ≤ 12 words**, readable in < 1 s — the feed grants a two-second audition before the reader (and the algorithm) decides.
- **One focal point per slide**, built from the four hierarchy levers: size, weight, colour, position.
- **One illustration = one concrete metaphor object.** Never illustrate a concept with another abstract concept: pick a physical object that embodies the idea and reads in 1 s (a battery = saving energy, CTRL+C/V keys = copying without anchoring, a magnifier = checking, a lightbulb = insight). One object per slide, in the brand's line-art language.

---

## 5. The eight compositions (rotate them)

Each composition is a reusable skeleton anchored in a principle. Rotate them; **two neighbouring slides never share the same treatment** (even when they rest on the shared 3-register frame of composition 2: illustration placement, ratio and block type change on every slide).

### 1. Framed cover — *page canon (Tschichold / Van de Graaf)*
Display title (110–160 px) **flush-left, anchored top-left**, 2–4 short lines, the keyword on its own line. One accent word. Large void at the bottom (30–40 %). Illustration absent or very faint. **→ cover / hook.**

### 2. Three-register partition — *vertical triptych (workhorse)*
The default skeleton for content slides (60–70 % of them). Three stacked horizontal bands: **title on top**, full width (72–110 px, 1–3 words, flush-left; never trap it in a narrow column), **illustration alone in the middle** (line-art at full opacity, surrounded by air, never watermarked), **text block at the bottom, full width** (body ≥ 48 px, two-level hierarchy: keyword in accent + rest in ink). The body takes the full live width (≈ 880 px): 30–50 character lines, maximum mobile legibility. **Replaces the old side-by-side text|illustration** (text left / illus right and reverse), dropped because it squeezed the body into a narrow column and broke phone reading. Variety comes from **treatment**, never two neighbouring slides alike: illustration placement (top-right tucked under the title / centred / full-width), illus↔text ratio (dense at the core, airy bullets toward the end), block type (paragraph, bullets). **→ one idea + one visual; the default frame of a carousel, punctuated by a number anchor (3) or a full quote (6) to breathe.**

### 3. Number anchor — *scale contrast (Ruder / Gerstner)*
A giant ExtraBold figure (240–330 px, or in the script / accent family) placed on the focal point, deliberately overflowing its column. Caption (~48 px) hung on its baseline. **→ stat, numbered step, proof.**

### 4. Numbered steps — *repeated module*
A big number in a dedicated left column + step title + micro-description, **3 to 5 items on one spec**, generous leading. The number carries sequential content (≠ decorative 01/02/03 tic). **→ method, checklist, process.**

### 5. Two-column comparison — *two equal fields, horizontal reading*
Two equal-width columns, contrasted headers ("Without" / "With"), items aligned **row by row** so they compare at a glance. A title sets the axis. **→ opposition, before/after, myth/reality.**

### 6. Full quote — *pull-quote + single accent (Vignelli)*
One display line (88–128 px), 6–12 words, a single accent word, huge void around it. A different (deeper) background shade marks the breath. **→ punchline, manifesto, breather between two dense blocks.**

### 7. Hero illustration — *picture window*
Illustration **large and at full opacity** (top or centre — it dominates), crisp title below. The illustration is the subject. **→ key slide, emotional beat.** (Never behind the text as a watermark: it disappears.)

### 8. Signoff / CTA — *closing symmetry*
One-line recap + **a single** action + signoff (avatar + name + role). Symmetric centring, banned everywhere else, becomes the end signal here. **→ last slide only.**

**Connectors.** A **constant footer** (handle + optional counter) locked on the same baseline, out of the bottom danger zone. Optional **continuity**: one element (a rule, an illustration) bleeding from one slide into the next to pull the swipe — sparingly, 1–2 times max. **Red thread (bookend):** one signature motif (a recurring illustration, a totem object) opens the cover, returns once at the core, then closes the signoff — it signs the carousel and creates a sense of loop (mere exposure). One motif only, 2–3 appearances maximum.

## 6. Rhythm of a 9-slide sequence

Arc **Hook → Context → 3× Value → Proof → Breather → Signoff**. A verified alternation (no neighbouring pair shares a skeleton):

| # | Role | Composition |
|---|---|---|
| 1 | Hook | Framed cover |
| 2 | Context / figure | Number anchor |
| 3 | Value 1 | Three-register partition (illus top-right) |
| 4 | Pivot value | Two-column comparison **or** Hero illustration |
| 5 | Value 2 | Three-register partition (illus full-width) |
| 6 | Value 3 | Numbered steps |
| 7 | Proof / rule | Three-register partition (illus tucked under title) |
| 8 | Punchline | Full quote |
| 9 | Signoff | Signoff / CTA |

## 7. "AI / Canva template" tells to ban

**Tell #1: a spaced UPPERCASE label above the title** (the repeated "kicker" / eyebrow). Banned — fold the information into the title itself. Also:

- Rounded icon tile repeated above every title.
- A grid of identical cards; nested cards.
- Systematic centring of everything, on every slide.
- 01/02/03 markers used as decoration (outside real steps).
- Purple→cyan gradient; free glassmorphism / glow; black drop-shadow under CTAs (keep the accent glow, never the black shadow).
- Gradient-filled text; washed grey on colour; a different accent per slide.
- Text touching the edges; monotone spacing (the same value everywhere).
- A generic hook ("10 tips to…") with no point of view.
- Copy side (recall the brand's banned list): em-dash, negative parallelism ("it's not X, it's Y"), hype jargon.

## 8. Mobile checklist (before export)

1. Body ≥ 48 px (never < 44); hook 130–180 px; titles 88–110 px; captions ≥ 32 px.
2. 920 × 1070 block centred (margins 80 / 120 / 160); nothing vital outside it.
3. Contrast: ink or accent on the chosen background; nothing below the WCAG floor.
4. One idea + one focal point per slide; ≤ 30 words; ≤ 6–8 lines.
5. Line length 30–50 characters.
6. Neighbouring slides on different treatment (under a shared 3-register frame: vary illustration placement, ratio, block type).
7. Zero UPPERCASE eyebrow; zero tell from §7.
8. No trailing period on title / hook / kicker / CTA; no em-dash; no Unicode emoji.
9. One accent only; line-art at full opacity (never watermarked).
10. **Real test**: open the exported PDF on a phone and read every slide **without zooming**.

---

## Adapt to your brand

This system is brand-agnostic. Plug your values in one place:

- **Colours** → the four neutral / accent tokens in `presentations/tokens.css` (themselves derived from `../01-brand/style-guide.md`): background = `--brand-neutral-dark` or `--brand-neutral-light`; accent = `--brand-primary` / `--brand-secondary`; ink = the opposite neutral.
- **Type** → `--font-display` (+ `--font-mono` for captions); reserve any script / accent family the brand declares for the single accent word.
- **Illustration** → the brand's own line-art / illustration library (`../01-brand/assets/`), drawn for the chosen background.

The **grid, the mobile-safe scale, the eight compositions, the rhythm rules and the banned tells are universal** and port unchanged.

## Foundations

Müller-Brockmann, *Grid Systems in Graphic Design* · *The Vignelli Canon* · the Swiss typographic style · the Van de Graaf / Tschichold page canon · Gerstner's designed grid · WCAG 1.4.3 (contrast). Platform geometry (LinkedIn carousel / document, 1080×1350, 4:5) per current platform guidance.
