# Launch posts — Reddit (+ FR channel)

Working drafts for the open-source launch. Rules of engagement first, then two English posts, then a French adaptation.

## Playbook (read before posting)

- **Value first, repo second.** The post must be worth reading even if the reader never clicks. Lead with what you learned building it, not with what you built.
- **Honesty is the growth hack.** Name the limitations before commenters do (French-mixed internals, needs setup, not autopilot, quality depends on inputs). The claude-seo / taste-skill launches that worked all had a visible "limitations" section.
- **Disclose once, clearly.** "I run a small studio, this is our internal tool, there's a paid done-for-you setup but everything is MIT" — one sentence, no more.
- **Reply to every comment for the first 3–4 hours.** Launch-day responsiveness is the single biggest traction factor on Reddit.
- **Check each sub's self-promo rules the same day** (some require the link in a comment, not the post body). Don't cross-post the same text to two subs on the same day.
- **All numbers below are verified on the repo** (43 skills, 9 agents, 52 layouts, 20 templates, 7 modules). Don't round them up in edits.
- **Adjust the "6 months" timeframe to your real history** before posting — Reddit will ask, and the answer must hold.
- Post mid-week, 15:00–17:00 CET (morning US East). Have the 8 screenshots ready — image posts and comment-embedded screenshots outperform text-only.

---

## Post A — r/ClaudeAI

**Title (pick one):**

1. I spent 6 months turning Claude Code into my marketing department (for real client work). Today I'm open-sourcing the whole template — 43 skills, 9 agents, MIT.
2. Our studio runs client marketing entirely from Claude Code. We open-sourced the template: brand doctrine as SSOT, hook-enforced quality gates, 52-layout deck engine.

**Body:**

I run a small marketing studio. Since the start of the year we've been running actual client accounts out of Claude Code — social, email, landing pages, decks, SEO, reporting. Today we're open-sourcing the template we work in every day (MIT).

Repo: https://github.com/Littlpinguin/marketing-cockpit-template

The three design decisions that made it actually work, in case they're useful even if you never clone it:

**1. Brand doctrine as a single source of truth.** `01-brand/` holds voice, banned vocabulary, personas, design tokens, anti-AI-style rules, and a messaging framework where every claim maps to a sourced number. Every production skill loads it before writing a word. This is the difference between "AI content" and content.

**2. Hooks, not hope.** A PostToolUse hook fires a mandatory brand-check whenever content is written to a production folder. We stopped trusting the system prompt to survive the context window — the harness enforces the gate deterministically.

**3. File-based memory.** An editorial calendar with statuses (idea → draft → to-validate → validated → published), per-channel archives, and inventory files. Anti-repetition without a vector DB, fully auditable, survives across sessions.

What's in the box: 43 skills (writing, design, CRO, SEO/GEO, strategy, ads), 9 agents, a setup wizard that reads your website and drafts your brand doctrine for validation, a 52-layout HTML presentation engine with Playwright QA, 10 landing page templates + 10 interactive lead magnets (all single-file, open in a browser), and optional modules for n8n automation, client dashboards, and outbound.

We didn't reinvent what the community already solved: the SEO layer is adapted from claude-seo, design intelligence from ui-ux-pro-max and taste-skill, CRO from Corey Haines' marketingskills — all vendored with licenses verified and provenance registers in `docs/`. Standing on the shoulders of giants, and attributed as such.

**Honest limitations:** built in a French studio, so some internal skill files are still in French (Claude doesn't care; output language is set at setup — English-first internals are the top roadmap item). It's an operational framework, not autopilot: sending stays behind dry-run gates and human validation is a designed-in step. And on an empty brand with no published content to calibrate against, the output will be as generic as any other AI.

Disclosure: there's a paid done-for-you installation service for companies that want it, but the entire template is MIT with nothing held back.

Happy to answer anything about the architecture, the hook setup, what broke in production, or what I'd do differently. AMA.

---

## Post B — r/DigitalMarketing (or r/MarketingAutomation)

*Angle: workflow learnings for marketers, not code. Check the sub's rules — if links are restricted, put the repo in the first comment.*

**Title (pick one):**

1. I ran an AI "marketing department" on real client accounts for 6 months. Here's what it genuinely automated, what it can't do, and the whole system (open-sourced, free).
2. What actually survived 6 months of doing client marketing with an AI copilot — and what still needs a human. I open-sourced the full setup.

**Body:**

I run a small externalized marketing practice. For the past 6 months, most of our production — social posts, newsletters, landing pages, sales decks, SEO articles, monthly client reporting — has gone through an AI copilot we built on Claude Code. We just open-sourced it (MIT, link in comments / below per sub rules), but this post is about what we learned, because most "AI marketing" advice skips the operational reality.

**What it genuinely automated:**
- First drafts in the brand's actual voice — because the system loads a written brand doctrine (voice rules, banned words, sourced proof points) before every single piece. Generic prompts produce generic sludge; a doctrine file doesn't.
- Anti-repetition — it checks the editorial calendar and archives before proposing anything, so you stop publishing the same "3 lessons" post every six weeks.
- The unglamorous 60%: deck layouts, landing page scaffolding, UTM/GA4 conventions, monthly reporting dashboards with a written analysis section.

**What it can't do (and we stopped pretending):**
- Strategy from nothing. It runs a strategy interview and proposes, but if you can't articulate an objective, it amplifies the vagueness.
- Taste. Someone who can tell good marketing from bad has to validate. We built human validation into the workflow as a hard step, not a suggestion.
- Autopilot publishing. Everything that sends (email, social) goes through a dry-run preview and a human click. Anyone selling you full autopilot marketing is selling you a brand incident.

**The one principle that changed our output quality:** treat the brand like a database, not a vibe. Write down the voice, the banned vocabulary, the personas, the numbers you're allowed to claim (with sources) — then force every AI output through that filter with an automated check. The filter matters more than the model.

The whole thing is free and open source — 43 skills, 20 ready-to-use page templates, a 52-layout presentation engine, reporting dashboards. Fair warning: it runs in Claude Code (a terminal tool, ~30–60 min guided setup) and it's a framework, not a magic button. Disclosure: my studio sells a done-for-you installation, but nothing is paywalled.

Happy to share specifics — prompts, the brand-doctrine template, the reporting setup — in the comments.

---

## Post FR — canal francophone

*Pour un canal FR (LinkedIn perso, communauté Claude FR, forum growth FR). Adaptation du Post A, ton plus direct. Sur LinkedIn : ajouter les captures (catalogue de slides + dashboard) en images.*

**Titre :**

J'ai passé 6 mois à transformer Claude Code en département marketing pour mes clients. Aujourd'hui je l'open-source — 43 skills, 9 agents, licence MIT.

**Corps :**

Je dirige un petit studio marketing. Depuis six mois, nos comptes clients tournent en production sur Claude Code : social, email, landing pages, présentations, SEO, reporting mensuel. Aujourd'hui, on ouvre le template qu'on utilise tous les jours.

Repo : https://github.com/Littlpinguin/marketing-cockpit-template

Les trois décisions d'architecture qui ont tout changé :

**1. La doctrine de marque comme source de vérité unique.** Un dossier `01-brand/` : voix, vocabulaire interdit, personas, tokens design, règles anti-style-IA, et un cadre de messages où chaque affirmation renvoie à un chiffre sourcé. Chaque skill de production le charge avant d'écrire un mot. C'est ça, la différence entre « du contenu IA » et du contenu.

**2. Des hooks, pas de la bonne volonté.** Un hook PostToolUse déclenche un brand-check obligatoire dès qu'un contenu atterrit dans un dossier de production. On ne fait plus confiance au prompt système pour survivre à la fenêtre de contexte : c'est le harnais qui impose le gate.

**3. La mémoire en fichiers.** Un calendrier éditorial à statuts (idée → brouillon → à-valider → validé → publié), des archives par canal, des inventaires. Anti-répétition sans base vectorielle, auditable, persistant entre les sessions.

Dans la boîte : 43 skills, 9 agents, un wizard qui lit votre site et rédige votre doctrine de marque pour validation, un moteur de présentations HTML à 52 layouts avec QA Playwright, 10 templates de landing pages + 10 lead magnets interactifs, et des modules optionnels (automatisation n8n, dashboard client, outbound).

On n'a pas réinventé ce que la communauté avait déjà résolu : le SEO vient de claude-seo, l'intelligence design d'ui-ux-pro-max et de taste-skill, le CRO des marketingskills de Corey Haines — le tout vendorisé, licences vérifiées, registres de provenance dans `docs/`.

**Limites, en toute franchise :** une partie des fichiers internes est encore en français (aucun impact à l'exécution — la langue de sortie se configure au setup ; l'anglais intégral est en tête de roadmap). Ce n'est pas un pilote automatique : tout envoi passe par un dry-run et une validation humaine. Et sur une marque vide, sans contenu publié pour calibrer la voix, le résultat sera aussi générique que n'importe quelle IA.

Transparence : le studio propose une installation clé en main pour les boîtes qui préfèrent, mais l'intégralité du template est en MIT, rien n'est retenu.

Questions bienvenues — architecture, hooks, ce qui a cassé en prod, ce que je referais autrement.
