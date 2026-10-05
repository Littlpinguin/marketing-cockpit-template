<!--
  VENDORED from slides-agent (https://github.com/Littlpinguin/slides-agent), reference/LAYOUTS.md,
  by scripts/sync-slides-engine.py. Do not edit here: change slides-agent,
  then run python3 scripts/sync-slides-engine.py. Mentions of CLAUDE.md,
  onboarding and the pexels-photos skill refer to slides-agent.
  Register: docs/vendored-slides.md
-->
# Slide layout library

The index of every layout available to this project. Two sources feed it:

1. **`catalogue.html`** — all 120 layouts, executed and captioned, in a single deck. Every slide carries its own legend: layout name and when to use it. Brand and data are fictional, so it is safe to open, screenshot, and share. **Open this first.** Press `O` for the grouped overview.
2. **This file** — the index, for choosing by narrative beat rather than by scrolling a deck.

Every layout listed here is executed in the catalogue. Nothing is described but unbuilt. Plates 114 to 120 are compositions harvested from production decks of the marketing-cockpit template, which had no equivalent among the first 113; paste-ready code for them is in `06-graphic-design/presentations/templates/components.md`, "Compositions harvested from production decks".

## How to use the library

Pick layouts **by the beat you need**, never by scrolling the list from the top. A deck that uses eight different layouts reads as authored; a deck that repeats card grids reads as generated.

Working rule: **no layout twice in a row, and no layout more than twice in a deck.** The only exception is a deliberate rhythm, such as two breathing slides bracketing an argument.

Before building, sketch the beat sequence, then assign one layout per beat. If two adjacent beats want the same layout, one of them is the wrong beat.

---

## Family 1 — Opening and navigation

| Layout | What it does | Reach for it when | Status |
|---|---|---|---|
| `cover` | Full-bleed image or dark plate, oversize title, one-line promise | Slide 1, always | catalogue 01 |
| `cover-editorial` | Cover with a vertical gradient rule at the left edge and a watermark globe | A document that will be read, not projected | catalogue 53 |
| `agenda` | Numbered sections, one line each | Decks over 20 slides, or a workshop | catalogue 02 |
| `section-head` | Chapter divider, oversize numeral, watermark behind | Every new chapter in a long deck | catalogue 03 |
| `chapter-progress` | A character or marker advancing along the chapter rail | A course or a multi-session workbook | catalogue 54 |
| `date-hero` | One date, huge, and what happens on it | A launch, a deadline, a go-live | catalogue 55 |
| `cover-companion` | Cover with a recurring character or portrait beside the title | A workbook or a course, where the companion returns each chapter | catalogue 91 |

## Family 2 — Editorial and rhythm

| Layout | What it does | Reach for it when | Status |
|---|---|---|---|
| `silence` | One sentence, nothing else | After a dense slide, before a turn | catalogue 08 |
| `bignumber` | One number filling half the plate, one line of context | The number *is* the argument | catalogue 07 |
| `bigquote` | Pull-quote, oversize, attributed | Quoting the client back to themselves | catalogue 09 |
| `quote-portrait` | Quote plus a portrait, split | A testimonial with a face | catalogue 28 |
| `definition` | A term, its definition, and what it is not | Fixing vocabulary before an argument | catalogue 29 |
| `lead-block` | A single lead paragraph, generous margins | Opening a chapter with prose | catalogue 56 |
| `statement` | A claim on an ambient dot field | A manifesto beat | catalogue 57 |
| `tension-list` | Rows of opposing forces, each with its own weight | Naming the tensions before resolving them | catalogue 58 |
| `split-visual` | 50/50 visual and text, alternating sides across the deck | Any beat that has one image and one idea | catalogue 22, 23 |
| `fullbleed` | Edge-to-edge image under a readability veil | A mood beat, or a location | catalogue 21 |
| `split-illus` | Chapter opener: copy on one side, brand illustration on the other | Opening a chapter in a long document. Alternate the side each time | catalogue 90 |
| `cards` | Two to four equivalent cards, numbered | One idea with two to four facets of the same rank. Never more than four, never two levels of bullets | catalogue 04 |
| `editorial-foreword` | A side rail (issue number, metadata) and a two-column body opened by a drop cap | A letter, a manifesto, a long opening note meant to be read | catalogue 114 |
| `framed-cartouche` | One founding statement in a corner-bracketed frame, logo and name above, four metadata cells below | A charter, a commitment, a signed manifesto | catalogue 115 |

## Family 3 — Data visualisation

| Layout | What it does | Reach for it when | Status |
|---|---|---|---|
| `dot-grid` | A population drawn as dots, part of it highlighted | "X out of Y" — makes a ratio physical | catalogue 06 |
| `bars-v` | Vertical bars, one accented | Comparing 3 to 6 categories at one moment | catalogue 30 |
| `bars-h` | Horizontal bars, ranked | A ranking, or long category labels | catalogue 31 |
| `line-chart` | Evolution over time | A trend, several periods | catalogue 32 |
| `slope` | Two moments, lines between them | Before and after, on several series at once | catalogue 33 |
| `donut` | One share of a whole | A single proportion that matters | catalogue 34 |
| `waterfall` | A total decomposed into its steps, up and down | "Where does the gap come from" — the best layout for a build-up | catalogue 35 |
| `heatmap` | A grid coloured by intensity | Two dimensions crossed, many cells | catalogue 36 |
| `bullet-gauges` | Progress bars against a target tick | Tracking against objectives | catalogue 37 |
| `funnel` | Stacked narrowing bars | A conversion path, or a market sizing | catalogue 38 |
| `figures-grid` | Six figures in a hairline grid, each with a caption | A factual panorama with no narration | catalogue 39 |
| `kpi-strata` | Three stacked KPI bands, full width | Opening a results review | catalogue 63 |
| `kpi-band` | Three or four figures in a row, each with a one-line caption | Numbers of the same rank, read side by side | catalogue 05 |
| `kpi-trend-cards` | Value, trend chip and comparison per card; the colour judges, the arrow only points | A review where the movement matters as much as the level | catalogue 116 |
| `equation` | Box, operator, box, equals, result | Making a formula visual and memorable | catalogue 59 |
| `spectrum` | An axis with zones and a positioned marker | Placing something on a continuum | catalogue 60 |
| `scen-columns` | Scenario columns, one per hypothesis | P&L cases, pessimistic to optimistic | catalogue 61 |
| `allocation-bars` | Where the money goes, as proportional rows | Use of funds, budget split | catalogue 62 |

## Family 4 — Schemas and diagrams

| Layout | What it does | Reach for it when | Status |
|---|---|---|---|
| `pipeline` | Boxes connected left to right | A linear process, 3 to 5 stages | catalogue 10 |
| `process-flow` | Numbered steps with arrows and captions | A method you want people to reproduce | catalogue 71 |
| `three-step` | A to B to C, oversize | The simplest possible transformation | catalogue 72 |
| `lettered-framework` | An acronym, one cell per letter | Naming your own method | catalogue 11 |
| `quadrant` | Two axes, four zones, plotted dots | Positioning, prioritisation | catalogue 12 |
| `cycle` | A closed loop | Something that repeats, no start and no end | catalogue 40 |
| `pyramid` | Stacked levels, narrowing upward | Maturity levels, hierarchy of needs | catalogue 41 |
| `orbits` | A centre and two rings of satellites | Mapping actors or systems by proximity | catalogue 42 |
| `vertical-timeline` | A vertical rail with dated stops | A history, or a long sequence | catalogue 43 |
| `org-chart` | Nested boxes | Team structure, governance | catalogue 44 |
| `zigzag` | Alternating left-right steps down the plate | A journey with 4 to 6 stages | catalogue 45 |
| `y-split` | A shared trunk that forks into two tracks (`branching-flow` in the marketing-cockpit template) | "Same start, two paths" — one of the most distinctive schemas | catalogue 64 |
| `file-tree` | An indented tree with rails and dots | Site architecture, folder structure, information architecture | catalogue 65 |
| `depth-doors` | Access levels, each with a filled-bar depth indicator | Comparing permission tiers or depths of access | catalogue 93 |
| `annotated-tree` | A monospace tree with numbered call-outs explained beside it | Explaining a file or folder structure — annotate only what matters | catalogue 96 |
| `flow-steps` | Four numbered steps with a guarantee banner underneath | A delivery sequence where the banner carries the risk-reversal | catalogue 102 |
| `deploy-schema` | Blocks with an environment note underneath | Where things run, what talks to what | catalogue 66 |
| `seed-cycle` | A metaphor drawn in stages, with a dormant phase | When a metaphor carries the argument better than a diagram | catalogue 67 |
| `ratio-collapse` | Two quantities converging, drawn to scale | Showing a gap closing or a cost falling | catalogue 68 |
| `journey` | A horizontal line with named stops | A customer path over time | catalogue 69 |
| `value-chain` | Nodes in sequence, each with an output | Where value is added, step by step | catalogue 70 |

## Family 5 — Tables and comparisons

| Layout | What it does | Reach for it when | Status |
|---|---|---|---|
| `table-simple` | Rows and columns, hairlines only | Reference data the audience will read | catalogue 13, without the accented column |
| `table-ab` | Two columns compared, one accented | You versus the alternative | catalogue 13 |
| `comparison-table` | Three columns, you and two rivals | A competitive landscape | catalogue 74 |
| `before-after` | Two panels, mirrored items, the right one accented | Selling a transformation — very high hit rate | catalogue 15 |
| `pros-cons` | Two lists, weighted | An honest arbitration | catalogue 25 |
| `problem-solution` | Problem stated, solution facing it | One problem at a time | catalogue 24 |
| `faq` | Objection, then answer | Pre-empting what the room is thinking | catalogue 26 |
| `checklist` | Ticked and unticked items | A decision checklist, or scope | catalogue 27 |
| `raci-matrix` | Who does what, crossed | Governance of a project | catalogue 49 |
| `cost-table` | Costed lines, one scenario highlighted | The money slide | catalogue 17 |
| `two-modes` | Two columns, each a complete mode of working | Offering a choice of engagement | catalogue 73 |
| `platform-columns` | One column per OS or platform, strictly parallel | A procedure that differs by environment | catalogue 92 |
| `question-answer` | Situation on the left, decision on the right | Turning a list of cases into decisions | catalogue 94 |
| `verdict-cases` | Real cases, each with a verdict mark and its rule | Concrete cases beat an abstract rule | catalogue 95 |
| `legend-table` | Symbol, name, definition and count, one row per mark | A deck reuses symbols or categories: pose them once, early, then never explain them again | catalogue 117 |

## Family 6 — Proof and product

| Layout | What it does | Reach for it when | Status |
|---|---|---|---|
| `browser-mock` | A browser chrome drawn in pure CSS around content | Showing a web page without a screenshot | catalogue 14 |
| `interface-mock` | An app window with a bar and a body, drawn in CSS | Showing a product UI that does not exist yet | catalogue 75 |
| `live-stage` | A screen and a phone staged together | A product that spans devices | catalogue 76 |
| `product-shots` | A stack of overlapping captures | Several screens without several slides | catalogue 77 |
| `activity-wall` | A dense wall of small cards, deliberately overflowing | Volume as the argument: "look how much there is" | catalogue 78 |
| `card-wall-bleed` | Cards running off the top, bottom and right edges; only blank cards bleed (`data-bleed`), the cards that carry text stay inside the frame | A portfolio, an asset library | catalogue 79 |
| `logo-wall` | A mosaic of logos | Clients, integrations, partners | catalogue 50 |
| `partners-band` | A single row of chips with partner names | Light proof, at the bottom of an argument slide | catalogue 80 |
| `proof-grid` | Cells of evidence, each with a figure and a source | Backing a claim with several proofs at once | catalogue 81 |
| `case-study` | Copy on one side, visual on the other, with bullet outcomes | One client story, told properly | catalogue 82 |
| `project-sheet` | A full project record: logo, period, stack, results, consultant portrait | A reference book, one project per slide | catalogue 83 |
| `team-grid` | People in three columns | Who will actually do the work | catalogue 19 |
| `solo` | One person in focus, large portrait | A founder note, or a single expert | catalogue 86 |
| `map-coverage` | Geographic coverage | Territory, sites, footprint | catalogue 51 |
| `screenshot-steps` | A numbered walkthrough in captures | A tutorial or a handover document | catalogue 84 |
| `screenshot-annotated` | One capture, three numbered annotations beside it | A real screenshot carries the argument — never draw arrows on the image | catalogue 87 |
| `screenshot-full` | A single capture filling the plate under its title, nothing else | One screen is the whole demonstration | catalogue 88 |
| `showcase` | Three captures, each with a type, a title and one line | Showing what was actually produced | catalogue 89 |
| `codebox` | A copyable code or prompt block | Anything the reader will retype | catalogue 85 |
| `code-keys` | Code on the left, its two or three significant keys explained on the right | A config file where only a few keys actually matter | catalogue 97 |
| `link-list` | Source, promise, address — three fixed columns | The reader must be able to verify for themselves | catalogue 98 |
| `deliverable-cards` | Cards with an illustration band above the copy | Presenting the pieces of a kit or an offer | catalogue 99 |
| `chip-cloud` | A huge count, then the inventory as a cloud of chips, three highlighted at most | A scope or a catalogue whose extent is the argument | catalogue 118 |
| `avatar-wall` | A dense wall of round, anonymous faces and a counter | The mass of a community or a network is the proof | catalogue 119 |

## Family 7 — Offer and closing

| Layout | What it does | Reach for it when | Status |
|---|---|---|---|
| `pricing-2` | Two offers compared, one recommended | A simple choice | catalogue 16 |
| `pricing-3` | Three tiers, ticks and absences mirrored | The classic anchored ladder — the absence is what sells | catalogue 48 |
| `founder-offer` | One offer with a countdown or a cohort limit | A launch offer with scarcity | catalogue 103 |
| `roadmap` | Phases across quarters | Planning over a year | catalogue 46 |
| `year-ladder` | One row per exercise, the decisive tier accented | Progression across several years | catalogue 101 |
| `timeline` | Dated stops on a horizontal rail, one flagged as the decision | A delivery calendar with a commitment date | catalogue 18 |
| `kanban` | Columns of cards by status | A backlog, or work in flight | catalogue 47 |
| `vision` | Boxes and arrows toward a target state | Where this ends up in two years | catalogue 100 |
| `takeaways` | Three to five things to remember | The penultimate slide of a long deck | catalogue 52 |
| `cta-final` | One decision, one date | The last slide, always | catalogue 20 |
| `ask` | The explicit ask, isolated | An investor deck, or a partnership | catalogue 104 |
| `qr-closing` | Copy and benefits facing a card with one QR code and the address in clear | The ending calls for an action the room can take right now | catalogue 120 |

## Family 8 — Photography

Layouts where a real photograph carries the beat, with text beside the photo, never on it (for text over an image, see `cover` and `fullbleed`). Photos come from `06-graphic-design/presentations/assets/photos/` or from Pexels through the `pexels-photos` skill. Shared rules and paste-ready code: "Photography layouts" in `06-graphic-design/presentations/templates/components.md`. The catalogue plates use real Pexels photos, stored in `_examples/deck-catalogue/photos/` with their credit sidecars.

| Layout | What it does | Reach for it when | Status |
|---|---|---|---|
| `plate` | One small photo in a large empty field, plate number and caption in the margin | A pause after a dense slide, when the image is the evidence | catalogue 105 |
| `diptych` | Two photos, same ratio and height, one shared sentence | Comparing without a chart: before / after, here / there, problem / target | catalogue 106 |
| `letterbox-band` | A panoramic 3:1 band across the top, headline and two columns below | A place or a mood, lighter than `fullbleed`, when the message needs more than one line | catalogue 107 |
| `margin-figure` | Text-led slide, a small photo in a margin column like a sidenote | The words carry the argument; a trace of the real world makes it credible | catalogue 108 |
| `field-notes` | Metadata block (site, date, time, light) and the photo of the place | Site visits, audits, immersions, repeated in series. Your own photos only | catalogue 109 |
| `scale-contrast` | One large photo and one close-up of its texture | Material, craft or quality is the point | catalogue 110 |
| `typology-grid` | Eight photos of the same kind of subject in a strict grid | "It's a pattern", "they all look alike" | catalogue 111 |
| `sequence-strip` | Five frames in one row, read left to right as time | A gesture, a process, a day, shown with real hands | catalogue 112 |
| `photo-credits` | Pexels link and one line per photographer, with the slides it appears on | Always the last slide of a deck that uses Pexels photos; generated by `06-graphic-design/presentations/scripts/pexels.py credits` | catalogue 113 |

---

## Adding a layout

1. Build it as a new slide in `catalogue.html`, on the fictional brand, with data that carries no client information.
2. Give it a `data-family` from the eight above and an `<aside class="legend">` with its name and its "when".
3. Map every colour onto the `:root` tokens. Never leave a literal hex inside a layout.
4. Add its row to the right family table here.
5. If it is worth pasting rather than reading, add the HTML and scoped CSS to `06-graphic-design/presentations/templates/components.md`, with the trap that cost you time the first time.

**Screenshot layouts.** The catalogue ships a reusable `.shotph` placeholder — a browser chrome around a labelled empty frame. Use it rather than embedding an image: it keeps the repository light, it shows the required aspect ratio, and it makes the slide legible before anyone has a capture to drop in.

**Repo hygiene.** This repository is public. Never copy a client deck, a client name, a real price, or a real logo into it. The catalogue's fictional brand exists precisely so that layouts can be shown without exposing anything.
