# Component library

Reusable slide patterns, ready to copy into a new presentation. Each component is a paste-and-adapt block: the structural HTML + the scoped CSS it needs. **Never modify positions, paddings, or animations** — only the textual content. The system was tuned across many iterations and the values are load-bearing.

> All components assume the brand tokens from `tokens.css` are already in `:root`.

## How to use

1. Copy `templates/base.html` to `decks/<your-deck>.html`.
2. Inline `tokens.css` into the `:root { ... }` block.
3. Embed your logo `<symbol id="brand-logo">` (replace the placeholder in base.html).
4. For each slide you want, copy the matching component block from `templates/components/` (or from this catalogue) into the `<main class="stage">` body, between the existing `<section class="slide">` blocks.
5. Update `data-eyebrow` and `data-heading` on every slide — they drive the overview panel.
6. Run `python scripts/qa.py decks/<your-deck>.html` after every meaningful change.

## Selection guide — which component for which beat

The deck is a sparkline of emotional beats (Duarte / Reynolds). Pick components that match the beat, not just the data.

| Narrative beat | Component | When to use |
|---|---|---|
| Opening hook | `hero` | Slide 1. One huge number, one tagline. Sets ambition. |
| Pause / breath | `silence` | Every 4–5 slides. One huge number + one short phrase. Resets the eye. |
| Provocation / quote | `bigquote` | Pull quote, full-screen, dark slide. Used once or twice in a deck. |
| Section opener | `section-head` | Eyebrow + display headline + lede. Marks a chapter boundary. |
| Person in focus | `solo` | Portrait left, content right. Founders, key personas. |
| Asymmetric framing | `origin-grid` | Text left, big number right. The classic "X% of Y" slide. |
| Visualised population | `dot-grid` | A grid of dots with one highlighted — the "us amongst the rest" slide. |
| Process / pipeline | `pipeline` | SVG flow diagram with animated path. End-to-end process explanations. |
| Tool stack | `stack-grid` | 6 cells with logos + cost. Show what powers the system. |
| Funnel | `funnel` | 5 stages with bars. Conversion narratives. |
| Lead magnets / artefacts | `leadmags` | 3 mock book/asset covers. The deliverables slide. |
| KPI strata | `kpi-strata` | 3 horizontal bands of metrics. Layered ambitions. |
| Roadmap | `roadmap` | Timeline with phases. Milestone narratives. |
| Budget | `budget-grid` | 2 cards (one-shot vs recurring). Money slide. |
| Engagement / ask | `engage-stage` | Big number left + list right. Time/effort/expectation. |
| Date hero | `date-hero` | The launch date, huge. Ceremony. |
| Decision | `decision-stage` | "Go or no-go?" + meta. Final slide. |
| Person in focus | `solo` | One associate / persona, portrait + content. |
| Calendar / cadence | `cadence-grid` | Visual calendar of months / blocks. |
| Architecture timeline | `chapters` | 4 columns + horizontal timeline. |
| Lead magnets / artefacts | `leadmags` | 3 mock book covers. The deliverables. |
| KPI strata | `kpi-strata` | 3 horizontal bands of stacked metrics. |
| Engagement / ask | `engage-stage` | Big number left + obligations list right. |

A 24-slide deck typically uses 12–16 components, with 3–4 `silence` slides interleaved.

## Components

### `hero`

The opening slide. Big number + tagline + breathing animation.

```html
<section class="slide" data-eyebrow="introduction" data-heading="Hero">
  <div class="chrome"><!-- chrome rows from base.html --></div>
  <div class="hero">
    <span class="eyebrow reveal">your eyebrow</span>
    <span class="hero-num gradient-text reveal">78<span class="pct">%</span></span>
    <h2 class="hero-tag reveal">Your one-line tagline lives here.</h2>
    <div class="hero-meta reveal" data-stagger>
      <div><strong>label</strong>value</div>
      <div><strong>label</strong>value</div>
    </div>
  </div>
</section>
```

```css
.hero { display:flex; flex-direction:column; justify-content:center; gap:48px; height:100%; }
.hero-num { font-size:380px; font-weight:200; line-height:1; }
.hero-num .pct { font-size:0.45em; vertical-align:top; }
.hero-tag { font-size:48px; font-weight:300; max-width:1200px; line-height:1.2; }
.hero-meta { display:flex; gap:80px; font-family:var(--font-mono); font-size:13px; letter-spacing:0.06em; }
.hero-meta strong { display:block; font-family:var(--font-display); font-size:18px; font-weight:500; margin-bottom:4px; }
```

> **Add `.hero-num` to `GRADIENT_TEXT_SELECTORS`** in base.html so it rasterises cleanly in PDF.

---

### `silence` — breathing slide

One huge number, one short phrase. No chrome activity, no animations beyond reveal. Use 3–4 per 24-slide deck.

```html
<section class="slide dark" data-eyebrow="breathing" data-heading="Big number">
  <div class="chrome"><!-- chrome rows --></div>
  <div class="silence">
    <span class="silence-num gradient-text reveal">47</span>
    <p class="silence-tag reveal">A short sentence that anchors this number.</p>
  </div>
</section>
```

```css
.silence { display:flex; flex-direction:column; align-items:center; justify-content:center; gap:48px; height:100%; text-align:center; }
.silence-num { font-size:340px; font-weight:200; line-height:1; }
.silence-tag { font-size:32px; font-weight:300; max-width:900px; opacity:0.85; }
```

> **Add `.silence-num`** to `GRADIENT_TEXT_SELECTORS` if it uses `gradient-text`.

---

### `bigquote` — pull-quote

Editorial pull-quote, full-screen dark, italic display.

```html
<section class="slide dark" data-eyebrow="quote" data-heading="Pull quote">
  <div class="chrome"><!-- chrome rows --></div>
  <div class="bigquote">
    <p class="bigquote-text reveal">
      A short, sharp quote that frames <em>the entire deck</em> in a single sentence.
    </p>
    <span class="bigquote-attrib reveal">— Source, role, year</span>
  </div>
</section>
```

```css
.bigquote { display:flex; flex-direction:column; justify-content:center; gap:48px; height:100%; max-width:1500px; }
.bigquote-text { font-size:132px; font-weight:200; line-height:1.1; letter-spacing:-0.025em; }
.bigquote-text em { font-weight:300; font-style:italic; color:var(--brand-secondary); }
.bigquote-attrib { font-family:var(--font-mono); font-size:14px; letter-spacing:0.08em; opacity:0.6; }
```

---

### `section-head`

Chapter boundary: eyebrow + big headline + lede.

```html
<section class="slide" data-eyebrow="01 · chapter" data-heading="Section title">
  <div class="chrome"><!-- chrome rows --></div>
  <div class="section-head">
    <span class="eyebrow reveal">01 · chapter</span>
    <h1 class="display reveal">A clear, declarative headline<br>that names the chapter.</h1>
    <p class="lede reveal">A one-sentence subtitle that frames what follows.</p>
  </div>
</section>
```

```css
.section-head { display:flex; flex-direction:column; justify-content:center; gap:32px; height:100%; max-width:1400px; }
```

---

### `origin-grid` — asymmetric text + big number

Text on the left, number on the right. The "explainer" pattern.

```html
<section class="slide" data-eyebrow="context" data-heading="Origin">
  <div class="chrome"><!-- chrome rows --></div>
  <div class="origin-grid">
    <div class="origin-text reveal">
      <span class="eyebrow">why this number</span>
      <h2>Where the number comes from, in two sentences. Keep it tight.</h2>
      <p class="lede">Optional supporting line, in lighter weight.</p>
    </div>
    <div class="origin-num-pct reveal">
      <span class="num gradient-text">78</span>
      <span class="pct gradient-text">%</span>
    </div>
  </div>
</section>
```

```css
.origin-grid { display:grid; grid-template-columns: 1fr 1fr; gap:120px; align-items:center; height:100%; }
.origin-text { display:flex; flex-direction:column; gap:24px; }
.origin-text h2 { font-size:48px; font-weight:300; line-height:1.25; max-width:560px; }
.origin-num-pct { display:flex; align-items:flex-start; justify-content:center; }
.origin-num-pct .num { font-size:480px; font-weight:200; line-height:0.9; }
.origin-num-pct .pct { font-size:160px; font-weight:200; margin-top:48px; }
```

---

### `dot-grid` — visualised population

200 dots, one highlighted. Use for "1 amongst many" framing.

```html
<section class="slide" data-eyebrow="market" data-heading="Saturation">
  <div class="chrome"><!-- chrome rows --></div>
  <div class="saturation">
    <div class="dot-grid">
      <!-- Repeat 199 dots + 1 .us. JS or hand-write. -->
      <span class="d"></span><span class="d"></span><!-- ... -->
      <span class="d us"></span>
      <!-- ... -->
    </div>
    <div class="saturation-cap reveal">
      <span class="big">1<span class="gradient-text gold-num"> / 200</span></span>
      <p>What the highlighted one represents.</p>
    </div>
  </div>
</section>
```

```css
.saturation { display:grid; grid-template-columns: 1fr 1fr; gap:80px; align-items:center; height:100%; }
.dot-grid { display:grid; grid-template-columns: repeat(20, 1fr); gap:14px; }
.dot-grid .d { width:14px; height:14px; border-radius:50%; background:var(--brand-neutral-dark); opacity:0.18; }
.dot-grid .d.us { background:var(--brand-secondary); opacity:1; box-shadow:0 0 24px var(--brand-secondary-soft); animation:pulseGlow 3s ease-in-out infinite; }
@keyframes pulseGlow { 0%,100% { transform:scale(1); } 50% { transform:scale(1.4); } }
.saturation-cap { display:flex; flex-direction:column; gap:24px; }
.saturation-cap .big { font-size:120px; font-weight:200; }
```

---

### `pipeline` — animated flow

End-to-end process diagram with an animated SVG path. Use for "input → AI → output" stories.

```html
<section class="slide" data-eyebrow="process" data-heading="Pipeline">
  <div class="chrome"><!-- chrome rows --></div>
  <div class="section-head reveal" style="height:auto;">
    <span class="eyebrow">how the pipeline works</span>
    <h1 class="display">Input. Transformation. Output.</h1>
  </div>
  <div class="pipeline-stage reveal">
    <svg class="pipeline-svg" viewBox="0 0 1600 200">
      <path class="pipeline-anim" d="M40,100 L1560,100" stroke="url(#brand-grad)" stroke-width="2" fill="none" pathLength="1" stroke-dasharray="1" stroke-dashoffset="1"/>
      <!-- nodes: -->
      <circle cx="40" cy="100" r="14" fill="var(--brand-primary)"/>
      <circle cx="800" cy="100" r="14" fill="var(--brand-primary)"/>
      <circle cx="1560" cy="100" r="14" fill="var(--brand-secondary)"/>
    </svg>
    <div class="pipeline-labels" data-stagger>
      <div>Input</div>
      <div>Transform</div>
      <div>Output</div>
    </div>
  </div>
</section>
```

```css
.pipeline-stage { margin-top:80px; }
.pipeline-svg { width:100%; height:200px; }
.pipeline-anim { animation: drawIn 1.8s cubic-bezier(0.16,1,0.3,1) 0.3s forwards; }
@keyframes drawIn { to { stroke-dashoffset: 0; } }
.pipeline-labels { display:flex; justify-content:space-between; margin-top:24px; font-family:var(--font-mono); font-size:13px; letter-spacing:0.08em; }
```

> Add `body.printing-pdf .pipeline-anim { stroke-dashoffset: 0 !important; animation: none !important; }` to the print block — animations don't run in PDF.

---

### `stack-grid` — tools / technologies

6 cells in a 3×2 grid, each with a logo + label + cost. Plus a total bar.

```html
<section class="slide" data-eyebrow="stack" data-heading="Tool stack">
  <div class="chrome"><!-- chrome rows --></div>
  <div class="section-head reveal" style="height:auto;">
    <span class="eyebrow">what powers the system</span>
    <h1 class="display">Six tools. <span class="gradient-text">€your-total</span> per month.</h1>
  </div>
  <div class="stack-grid" data-stagger>
    <div class="stack-cell"><img class="stack-icon" src="../assets/logos/tool-1.svg" alt=""><strong>Tool 1</strong><span>€xx / mo</span></div>
    <div class="stack-cell"><img class="stack-icon" src="../assets/logos/tool-2.svg" alt=""><strong>Tool 2</strong><span>€xx / mo</span></div>
    <!-- 4 more -->
  </div>
  <div class="stack-total-bar reveal">
    <span>monthly recurring</span>
    <span class="stack-total-num gradient-text">€your-total</span>
  </div>
</section>
```

```css
.stack-grid { display:grid; grid-template-columns: repeat(3, 1fr); gap:24px; margin-top:48px; }
.stack-cell { background:var(--brand-neutral-light-soft); border:1px solid var(--rule); border-radius:8px; padding:24px; display:flex; flex-direction:column; gap:12px; aspect-ratio:1.4; }
.stack-icon { width:40px; height:40px; }
.stack-cell strong { font-size:18px; font-weight:500; }
.stack-cell span { font-family:var(--font-mono); font-size:12px; opacity:0.6; margin-top:auto; }
.stack-total-bar { display:flex; justify-content:space-between; align-items:baseline; padding:24px 0; border-top:1px solid var(--rule); margin-top:32px; }
.stack-total-num { font-size:64px; font-weight:200; }
```

---

### `funnel` — 5-stage conversion bars

```html
<section class="slide" data-eyebrow="funnel" data-heading="Conversion">
  <div class="chrome"><!-- chrome rows --></div>
  <div class="section-head reveal" style="height:auto;">
    <span class="eyebrow">the funnel</span>
    <h1 class="display">From reach to signed contract.</h1>
  </div>
  <div class="funnel" data-stagger>
    <div class="funnel-row"><span>Reach</span><div class="funnel-bar" style="--width:1"></div><span>10,000</span></div>
    <div class="funnel-row"><span>Engaged</span><div class="funnel-bar" style="--width:0.6"></div><span>6,000</span></div>
    <div class="funnel-row"><span>Lead</span><div class="funnel-bar" style="--width:0.25"></div><span>2,500</span></div>
    <div class="funnel-row"><span>MQL</span><div class="funnel-bar" style="--width:0.08"></div><span>800</span></div>
    <div class="funnel-row"><span>Closed</span><div class="funnel-bar" style="--width:0.015"></div><span>150</span></div>
  </div>
</section>
```

```css
.funnel { display:flex; flex-direction:column; gap:18px; margin-top:48px; }
.funnel-row { display:grid; grid-template-columns:160px 1fr 120px; gap:24px; align-items:center; font-family:var(--font-mono); font-size:13px; }
.funnel-bar { height:36px; background:var(--rule); border-radius:4px; position:relative; overflow:hidden; }
.funnel-bar::before { content:''; position:absolute; inset:0; background:var(--brand-gradient); transform-origin:left; transform: scaleX(var(--width, 1)); transition: transform 1.4s cubic-bezier(0.16,1,0.3,1); }
```

---

### `roadmap` — phased timeline

```html
<section class="slide" data-eyebrow="roadmap" data-heading="Plan">
  <div class="chrome"><!-- chrome rows --></div>
  <div class="section-head reveal" style="height:auto;">
    <span class="eyebrow">timeline</span>
    <h1 class="display">12 weeks, five phases.</h1>
  </div>
  <div class="roadmap reveal">
    <div class="roadmap-track"></div>
    <div class="roadmap-phases" data-stagger>
      <div class="roadmap-phase"><strong>W1–2</strong><span>Discovery</span></div>
      <div class="roadmap-phase"><strong>W3–4</strong><span>Design</span></div>
      <div class="roadmap-phase"><strong>W5–8</strong><span>Build</span></div>
      <div class="roadmap-phase"><strong>W9–10</strong><span>Test</span></div>
      <div class="roadmap-phase"><strong>W11–12</strong><span>Launch</span></div>
    </div>
  </div>
</section>
```

```css
.roadmap { position:relative; margin-top:80px; padding:48px 0; }
.roadmap-track { position:absolute; top:50%; left:0; right:0; height:2px; background:var(--rule); }
.roadmap-track::before { content:''; position:absolute; inset:0; background:var(--brand-gradient); transform-origin:left; transform:scaleX(0); animation:trackFill 2.5s cubic-bezier(0.16,1,0.3,1) 0.3s forwards; }
@keyframes trackFill { to { transform:scaleX(1); } }
.roadmap-phases { display:flex; justify-content:space-between; position:relative; }
.roadmap-phase { display:flex; flex-direction:column; align-items:center; gap:8px; position:relative; padding-top:36px; }
.roadmap-phase::before { content:''; position:absolute; top:-6px; width:14px; height:14px; border-radius:50%; background:var(--brand-secondary); transform:scale(0); animation:dotPop 0.6s cubic-bezier(0.34, 1.56, 0.64, 1) 1.5s forwards; }
@keyframes dotPop { to { transform:scale(1); } }
.roadmap-phase strong { font-family:var(--font-mono); font-size:13px; }
.roadmap-phase span { font-size:14px; opacity:0.8; }
```

> Add to print overrides: `.roadmap-track::before { transform:scaleX(1) !important; }` and `.roadmap-phase::before { transform:scale(1) !important; }`.

---

### `budget-grid` — 2 cards, one-shot vs recurring

```html
<section class="slide" data-eyebrow="budget" data-heading="Money">
  <div class="chrome"><!-- chrome rows --></div>
  <div class="section-head reveal" style="height:auto;">
    <span class="eyebrow">investment</span>
    <h1 class="display">What it costs.</h1>
  </div>
  <div class="budget-grid" data-stagger>
    <div class="budget-block">
      <span class="eyebrow">one-shot</span>
      <span class="budget-num">€xx,xxx</span>
      <ul class="budget-list">
        <li>Discovery + design</li>
        <li>Build</li>
        <li>Launch</li>
      </ul>
    </div>
    <div class="budget-block dark">
      <span class="eyebrow">recurring monthly</span>
      <span class="budget-num gradient-text">€x,xxx</span>
      <ul class="budget-list">
        <li>Hosting + tools</li>
        <li>Maintenance</li>
        <li>Iteration</li>
      </ul>
    </div>
  </div>
</section>
```

```css
.budget-grid { display:grid; grid-template-columns:1fr 1fr; gap:32px; margin-top:48px; }
.budget-block { padding:48px; border:1px solid var(--rule); border-radius:8px; display:flex; flex-direction:column; gap:24px; }
.budget-block.dark { background:var(--brand-neutral-dark); color:var(--brand-neutral-light); border:none; }
.budget-num { font-size:96px; font-weight:200; line-height:1; }
.budget-list { list-style:none; font-family:var(--font-mono); font-size:13px; line-height:1.8; opacity:0.7; }
```

---

### `decision-stage` — final slide

The "Go or no-go?" closer.

```html
<section class="slide" data-eyebrow="decision" data-heading="Go or no-go">
  <div class="chrome"><!-- chrome rows --></div>
  <div class="decision-stage">
    <span class="eyebrow reveal">final question</span>
    <h1 class="decision-q reveal"><span class="go gradient-text">Go</span> or <span class="nogo">no-go</span>?</h1>
    <div class="decision-meta reveal" data-stagger>
      <div><strong>budget</strong>your number</div>
      <div><strong>timeline</strong>your timeline</div>
      <div><strong>owner</strong>your name</div>
      <div><strong>start date</strong>YYYY-MM-DD</div>
    </div>
  </div>
</section>
```

```css
.decision-stage { display:flex; flex-direction:column; justify-content:center; gap:48px; height:100%; }
.decision-q { font-size:240px; font-weight:200; line-height:1; letter-spacing:-0.025em; }
.decision-q .nogo { opacity:0.4; }
.decision-meta { display:flex; gap:80px; font-family:var(--font-mono); font-size:13px; }
.decision-meta strong { display:block; font-family:var(--font-display); font-size:18px; font-weight:500; margin-bottom:4px; }
```

> Add `.decision-q .go` to `GRADIENT_TEXT_SELECTORS`.

---

### `solo` — person in focus

Portrait left, content right. For founders, key personas, named decision-makers.

```html
<section class="slide" data-eyebrow="associate" data-heading="Person name">
  <div class="chrome"><!-- chrome rows --></div>
  <div class="solo">
    <div class="solo-portrait reveal">
      <img src="../assets/illustrations/portrait-name.svg" alt="">
    </div>
    <div class="solo-content">
      <span class="eyebrow reveal">role</span>
      <h2 class="solo-name reveal">First Last</h2>
      <p class="solo-territory reveal">Their territory in two short lines. What they own. What they bring.</p>
      <ul class="solo-tags reveal" data-stagger>
        <li>Tag one</li>
        <li>Tag two</li>
        <li>Tag three</li>
      </ul>
    </div>
  </div>
</section>
```

```css
.solo { display:grid; grid-template-columns: 480px 1fr; gap:96px; align-items:center; height:100%; }
.solo-portrait img { width:100%; height:auto; max-height:640px; object-fit:contain; }
.solo-content { display:flex; flex-direction:column; gap:24px; max-width:880px; }
.solo-name { font-size:88px; font-weight:200; line-height:1.05; letter-spacing:-0.025em; }
.solo-territory { font-size:22px; font-weight:300; line-height:1.4; opacity:0.85; }
.solo-tags { list-style:none; display:flex; flex-wrap:wrap; gap:8px; margin-top:16px; }
.solo-tags li { font-family:var(--font-mono); font-size:12px; padding:6px 12px; border:1px solid var(--rule); border-radius:var(--radius-pill); }
```

---

### `cadence-grid` — calendar / cadence visual

A visual rhythm chart (months × blocks per month) with stats on the right.

```html
<section class="slide" data-eyebrow="cadence" data-heading="Production rhythm">
  <div class="chrome"><!-- chrome rows --></div>
  <div class="section-head reveal" style="height:auto;">
    <span class="eyebrow">cadence</span>
    <h1 class="display">One month of output, visualised.</h1>
  </div>
  <div class="cadence-grid reveal">
    <div class="cadence-months" data-stagger>
      <!-- repeat per month -->
      <div class="cadence-month">
        <span class="cadence-month-label">Jan</span>
        <div class="cadence-blocks">
          <span class="b filled"></span><span class="b filled"></span>
          <span class="b filled"></span><span class="b"></span>
        </div>
      </div>
      <!-- ... 7 more -->
    </div>
    <div class="cadence-stats" data-stagger>
      <div><strong>32</strong><span>units / month</span></div>
      <div><strong>4×</strong><span>per week</span></div>
      <div><strong>8 mo</strong><span>steady state</span></div>
    </div>
  </div>
</section>
```

```css
.cadence-grid { display:grid; grid-template-columns: 1fr 280px; gap:80px; margin-top:48px; }
.cadence-months { display:grid; grid-template-columns: repeat(8, 1fr); gap:12px; }
.cadence-month { display:flex; flex-direction:column; gap:8px; }
.cadence-month-label { font-family:var(--font-mono); font-size:11px; opacity:0.6; }
.cadence-blocks { display:grid; grid-template-columns: repeat(2, 1fr); gap:4px; }
.cadence-blocks .b { aspect-ratio:1; background:var(--rule); border-radius:2px; }
.cadence-blocks .b.filled { background:var(--brand-primary); }
.cadence-stats { display:flex; flex-direction:column; gap:24px; padding-left:32px; border-left:1px solid var(--rule); }
.cadence-stats strong { display:block; font-size:48px; font-weight:200; line-height:1; }
.cadence-stats span { font-family:var(--font-mono); font-size:12px; opacity:0.6; }
```

---

### `chapters` — 4-column timeline

Four phases on a horizontal timeline. Used for "the seasons of the project" or "the chapters of a podcast season".

```html
<section class="slide" data-eyebrow="architecture" data-heading="Chapters">
  <div class="chrome"><!-- chrome rows --></div>
  <div class="section-head reveal" style="height:auto;">
    <span class="eyebrow">structure</span>
    <h1 class="display">Four chapters. One arc.</h1>
  </div>
  <div class="chapters reveal" data-stagger>
    <div class="chapter">
      <span class="chapter-num">01</span>
      <h3>Chapter title</h3>
      <p>One short line per chapter — what it covers, no more.</p>
    </div>
    <div class="chapter"><span class="chapter-num">02</span><h3>Chapter</h3><p>Line</p></div>
    <div class="chapter"><span class="chapter-num">03</span><h3>Chapter</h3><p>Line</p></div>
    <div class="chapter"><span class="chapter-num">04</span><h3>Chapter</h3><p>Line</p></div>
  </div>
</section>
```

```css
.chapters { display:grid; grid-template-columns: repeat(4, 1fr); gap:32px; margin-top:64px; position:relative; }
.chapters::before { content:''; position:absolute; top:32px; left:0; right:0; height:1px; background:var(--rule); }
.chapter { display:flex; flex-direction:column; gap:16px; padding-top:56px; position:relative; }
.chapter::before { content:''; position:absolute; top:25px; left:0; width:14px; height:14px; border-radius:50%; background:var(--brand-secondary); }
.chapter-num { font-family:var(--font-mono); font-size:11px; letter-spacing:0.10em; opacity:0.6; }
.chapter h3 { font-size:28px; font-weight:400; line-height:1.2; }
.chapter p { font-size:15px; line-height:1.5; opacity:0.75; }
```

---

### `leadmags` — three deliverable covers

Three mock "book" or document covers, used for the artefacts / lead magnets / deliverables slide.

```html
<section class="slide" data-eyebrow="deliverables" data-heading="Lead magnets">
  <div class="chrome"><!-- chrome rows --></div>
  <div class="section-head reveal" style="height:auto;">
    <span class="eyebrow">artefacts</span>
    <h1 class="display">Three deliverables, three audiences.</h1>
  </div>
  <div class="leadmags reveal" data-stagger>
    <div class="leadmag">
      <div class="leadmag-cover" style="background:var(--brand-primary);">
        <span class="leadmag-tag">guide</span>
        <h4>Cover title</h4>
      </div>
      <p class="leadmag-cap">Who it's for, in one short line.</p>
    </div>
    <div class="leadmag">
      <div class="leadmag-cover" style="background:var(--brand-secondary);color:var(--brand-neutral-dark);">
        <span class="leadmag-tag">checklist</span>
        <h4>Cover title</h4>
      </div>
      <p class="leadmag-cap">Audience.</p>
    </div>
    <div class="leadmag">
      <div class="leadmag-cover" style="background:var(--brand-neutral-dark);color:var(--brand-neutral-light);">
        <span class="leadmag-tag">template</span>
        <h4>Cover title</h4>
      </div>
      <p class="leadmag-cap">Audience.</p>
    </div>
  </div>
</section>
```

```css
.leadmags { display:grid; grid-template-columns: repeat(3, 1fr); gap:32px; margin-top:48px; }
.leadmag { display:flex; flex-direction:column; gap:16px; }
.leadmag-cover { aspect-ratio:3/4; padding:32px; display:flex; flex-direction:column; justify-content:space-between; border-radius:6px; color:var(--brand-neutral-light); }
.leadmag-tag { font-family:var(--font-mono); font-size:11px; letter-spacing:0.10em; text-transform:lowercase; opacity:0.7; }
.leadmag h4 { font-size:32px; font-weight:300; line-height:1.15; }
.leadmag-cap { font-size:14px; opacity:0.7; }
```

---

### `kpi-strata` — three stacked KPI bands

Three horizontal layers, each with its own metrics. Use for "influence / reach / conversion" trios.

```html
<section class="slide" data-eyebrow="kpi" data-heading="Targets">
  <div class="chrome"><!-- chrome rows --></div>
  <div class="section-head reveal" style="height:auto;">
    <span class="eyebrow">targets</span>
    <h1 class="display">Three layers, three metrics each.</h1>
  </div>
  <div class="kpi-strata reveal" data-stagger>
    <div class="kpi-layer">
      <span class="kpi-level">Layer 1 · Influence</span>
      <div class="kpi-stats">
        <div><strong>10k</strong><span>followers</span></div>
        <div><strong>+20%</strong><span>quarterly</span></div>
        <div><strong>3</strong><span>publications</span></div>
      </div>
    </div>
    <div class="kpi-layer">
      <span class="kpi-level">Layer 2 · Reach</span>
      <div class="kpi-stats">
        <div><strong>50k</strong><span>monthly</span></div>
        <div><strong>4 min</strong><span>avg session</span></div>
        <div><strong>12</strong><span>countries</span></div>
      </div>
    </div>
    <div class="kpi-layer">
      <span class="kpi-level">Layer 3 · Conversion</span>
      <div class="kpi-stats">
        <div><strong>2.5%</strong><span>signup rate</span></div>
        <div><strong>€xx</strong><span>LTV</span></div>
        <div><strong>×8</strong><span>ROI 12 mo</span></div>
      </div>
    </div>
  </div>
</section>
```

```css
.kpi-strata { display:flex; flex-direction:column; gap:24px; margin-top:48px; }
.kpi-layer { padding:32px; border:1px solid var(--rule); border-radius:6px; display:grid; grid-template-columns: 240px 1fr; gap:48px; align-items:center; }
.kpi-level { font-family:var(--font-mono); font-size:13px; letter-spacing:0.08em; opacity:0.7; }
.kpi-stats { display:grid; grid-template-columns: repeat(3, 1fr); gap:48px; }
.kpi-stats strong { display:block; font-size:48px; font-weight:200; line-height:1; }
.kpi-stats span { font-family:var(--font-mono); font-size:12px; opacity:0.6; }
```

---

### `engage-stage` — big number + obligations list

Used for the "what you commit to" / "what we ask of you" slide. Big number on the left, list of items on the right.

```html
<section class="slide" data-eyebrow="commitment" data-heading="What we need">
  <div class="chrome"><!-- chrome rows --></div>
  <div class="engage-stage">
    <div class="engage-num-wrap reveal">
      <span class="engage-num gradient-text">3 h</span>
      <span class="engage-num-cap">per month</span>
    </div>
    <ul class="engage-list" data-stagger>
      <li class="engage-item"><strong>One recording session</strong><span>90 min, you talk, we capture.</span></li>
      <li class="engage-item"><strong>One review block</strong><span>30 min on edits.</span></li>
      <li class="engage-item"><strong>One social push</strong><span>One post + reshare on launch day.</span></li>
    </ul>
  </div>
</section>
```

```css
.engage-stage { display:grid; grid-template-columns: 1fr 1fr; gap:96px; align-items:center; height:100%; }
.engage-num-wrap { display:flex; flex-direction:column; align-items:flex-start; gap:8px; }
.engage-num { font-size:280px; font-weight:200; line-height:0.95; }
.engage-num-cap { font-family:var(--font-mono); font-size:14px; letter-spacing:0.08em; opacity:0.6; }
.engage-list { list-style:none; display:flex; flex-direction:column; gap:24px; }
.engage-item { padding:24px 0; border-top:1px solid var(--rule); }
.engage-item strong { display:block; font-size:24px; font-weight:500; margin-bottom:6px; }
.engage-item span { font-size:16px; opacity:0.75; }
```

> Add `.engage-num` to `GRADIENT_TEXT_SELECTORS`.

---

### `date-hero` — launch date

Huge date display + context. Used as the penultimate slide before the decision.

```html
<section class="slide dark" data-eyebrow="launch" data-heading="Launch date">
  <div class="chrome"><!-- chrome rows --></div>
  <div class="date-hero">
    <span class="eyebrow reveal">launch</span>
    <div class="date-mega reveal">
      <span class="day gradient-text">21<span class="month">.09</span></span>
      <span class="year">2026</span>
    </div>
    <p class="date-context reveal">A short line of context — why this date, who's expected, what happens.</p>
  </div>
</section>
```

```css
.date-hero { display:flex; flex-direction:column; justify-content:center; gap:48px; height:100%; }
.date-mega { display:flex; align-items:flex-end; gap:32px; }
.date-mega .day { font-size:380px; font-weight:200; line-height:0.9; letter-spacing:-0.025em; }
.date-mega .month { font-size:0.6em; }
.date-mega .year { font-size:96px; font-weight:200; opacity:0.5; padding-bottom:32px; }
.date-context { font-size:22px; max-width:880px; opacity:0.85; }
```

> Add `.date-mega .day` to `GRADIENT_TEXT_SELECTORS`.

---

## Adding a new component

If none of the above fits a beat in your deck, build a new one:

1. Sketch it on paper. One idea, one slide. If it has more than 3 distinct elements, split.
2. Build the CSS scoped under a single root class.
3. Write the HTML with a `data-eyebrow` and `data-heading`.
4. If it uses gradient text via `background-clip: text`, append the selector to `GRADIENT_TEXT_SELECTORS` in base.html — otherwise it'll have artefacts in PDF.
5. Run QA. Verify the bottom-content gap to chrome ≥ 16px on every viewport.

The discipline that keeps the system coherent: copy what's there before inventing something new.
