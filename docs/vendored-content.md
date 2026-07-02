# Contenus vendorisés — attributions, licences, adaptations

> Registre des contenus tiers intégrés au template (skills, agents, références). Chaque entrée documente : la source, la licence constatée au moment du fetch, la version/date, ce qui a été retenu, ce qui a été adapté, ce qui a été exclu. **Règle : licence non confirmée = pas de copie.** Les textes vendorisés sont des adaptations condensées, pas des copies intégrales ; la licence MIT des sources autorise modification et redistribution sous réserve de conservation de l'attribution — c'est le rôle de ce fichier et des bandeaux d'attribution en tête de chaque skill concernée.

Vérification des licences : fichier `LICENSE` de chaque dépôt lu via l'API GitHub (`/repos/{owner}/{repo}/license`) le 2026-07-02.

---

## 1. claude-ads (AgriciDaniel) → skill `ads-audit`

| | |
|---|---|
| **Source** | https://github.com/AgriciDaniel/claude-ads (~6,6k ★) |
| **Licence** | MIT — © 2026 agricidaniel (LICENSE vérifié le 2026-07-02) |
| **Version vendorisée** | v1.7.1 (release du 2026-05-18), branche `main`, commit `283d9d4917` |
| **Fichiers créés** | `.claude/skills/ads-audit/SKILL.md`, `.claude/skills/ads-audit/references/annexes-plateformes.md` |

**Sélection.** Le dépôt d'origine couvre 250+ checks sur 7 plateformes via 22 skills, 10 agents et 26 fichiers de référence. Retenu et condensé : l'orchestrateur `ads-audit` (processus, scoring 0-100, priorités, quick wins) + les grilles détaillées **Google Ads** (~80 checks : conversion tracking, wasted spend, négatifs, structure, mots-clés, RSA, réglages, PMax/AI Max/Demand Gen), **Meta Ads** (~50 checks : Pixel/CAPI/EMQ, diversité créative et clustering Entity-ID de l'ère Andromeda/GEM/Lattice, structure, audiences) et **LinkedIn Ads** (27 checks : technique, ciblage/ABM, Thought Leader Ads, lead gen forms, enchères) — les 3 plateformes cœur de cible du template. TikTok, Microsoft, Apple et Amazon sont résumés en annexes courtes (`references/annexes-plateformes.md`).

**Adaptations.** Traduction/condensation en français ; intégration au module `12-acquisition/` (règle dure « audit sans modification », rapport dans `12-acquisition/audits/`, métriques versées dans le snapshot `02-strategy/performance/AAAA-MM/data.json` pour le dashboard `11-reporting/`) ; articulation explicite avec la skill `sea-google-ads` (ads-audit = audit multi-plateformes, sea-google-ads = opérationnel Google via MCP) ; renvois doctrine `01-brand/` pour toute proposition d'annonce et `conformite-rgpd.md` pour Consent Mode v2.

**Exclusions.** Skills de création/génération (ads-create, ads-creative, ads-generate, ads-photoshoot, ads-dna, ads-plan, ads-math, ads-landing, ads-youtube, ads-test, ads-budget, ads-competitor, ads-attribution, ads-server-side-tracking) — hors périmètre audit ; le « 10-Principle Thinking Framework » et le système d'agents parallèles (audit-google, audit-meta…) — remplacés par une exécution inline ; les scripts Python, evals et installeurs ; les notes GAQL détaillées (résumées en 3 règles) ; les benchmarks non essentiels.

---

## 2. claude-blog (AgriciDaniel) → skill `blog-engine`

| | |
|---|---|
| **Source** | https://github.com/AgriciDaniel/claude-blog |
| **Licence** | MIT — © 2025-2026 AgriciDaniel (LICENSE vérifié le 2026-07-02) |
| **Version vendorisée** | v1.9.1 (release du 2026-05-20), branche `main`, commit `49842ea9e7` |
| **Fichier créé** | `.claude/skills/blog-engine/SKILL.md` |

**Sélection.** Le moteur d'origine compte 30 sub-skills, 12 templates, 21 références et 5 agents. Condensé en **une skill maîtresse** : le workflow bout-en-bout (recherche sourcée Tier 1-3 → plan SERP → rédaction → validation SEO → scoring → livraison), les 6 piliers d'optimisation (answer-first, triplet de preuve FLOW, extractibilité IA, fraîcheur), le **quality gate 100 points en 5 catégories avec seuil de livraison ≥ 90/100** et sa logique d'itération (3 max, diagnostic au 3ᵉ échec), le **fact-checking avec fetch des sources** (extraction des claims, scoring VERIFIED/PARAPHRASE/WEAK/NOT FOUND/UNVERIFIED, correction obligatoire < 0.7), les 8 templates de contenu les plus utiles, et l'essentiel du multilingue (**hreflang réciproque + x-default**, localisation culturelle).

**Adaptations.** Traduction/condensation en français ; l'étape 0 doctrine `01-brand/` remplace le système BRAND.md/VOICE.md/DISCOURSE.md du moteur d'origine (et son contrat « untrusted data » à nonce, inutile ici : la doctrine est un fichier de premier parti du repo) ; articulation avec la skill `seo` existante (seo = stratégie/audit + délégation au plugin claude-seo, blog-engine = production d'article) ; livraison dans `09-seo/` + brand-check obligatoire ; seuil de livraison relevé à ≥ 90 (la source livre à 80+ avec « polish mineur »).

**Exclusions.** Les 30 dossiers de sub-skills (routage /blog non transposé — la skill est monolithique) ; le footer communautaire Skool (auto-promotion de l'auteur, retiré) ; les intégrations Gemini (images, TTS audio, NotebookLM), Google APIs (PSI/CrUX/GSC — couvert par `/tools-setup` et le plugin claude-seo), taxonomies CMS, blog-discourse, blog-repurpose (couvert par `social-content`) ; scripts Python de scoring/préflight (le scoring est appliqué par le modèle) ; 4 templates de contenu peu pertinents pour le template.

---

## 3. email-marketing-bible (CosmoBlk) → skill `email-deliverability`

| | |
|---|---|
| **Source** | https://github.com/CosmoBlk/email-marketing-bible (guide : https://emailmarketingskill.com) |
| **Licence** | MIT (LICENSE vérifié le 2026-07-02) |
| **Version vendorisée** | SKILL.md v2.6 (metadata, auteur george-hartley), dernier commit `ff526b0712` du 2026-06-30 |
| **Fichier créé** | `.claude/skills/email-deliverability/SKILL.md` |

**Sélection.** Retenu de la « bible » (19 chapitres, 908 sources) : les garde-fous d'envoi agentiques (hard gates, paquet d'approbation, endpoints mutateurs), la checklist pré-envoi, le **triage délivrabilité** (SPF/DKIM/DMARC avec exigences Outlook/Gmail 2026, réputation domaine, chemin de diagnostic, seuils avec actions, envoi par tiers d'engagement, warm-up, délivrabilité ère IA), la **table de conformité RGPD/CAN-SPAM/CASL/Spam Act**, le protocole de **design dark-mode-safe** (contraintes par défaut, substrats MJML/React Email, archétypes), les benchmarks datés mi-2026 et l'essentiel des playbooks sectoriels.

**Adaptations.** Traduction/condensation en français ; positionnée en **référence consultative** de la skill `email` (qui garde la production, la doctrine et l'anti-répétition) ; croisement systématique avec `docs/etat-de-lart/email.md` — **divergences documentées dans la skill** : longueur d'objet (EMB ≤ 45 car. vs état de l'art 36-50 car. → arbitrage : R7 + message clé < 33 car.), chiffres CTA (+27 %/+42 % vs +45 %/+371 % → ordres de grandeur, règle opérationnelle identique), DMARC (`p=none` toléré par Gmail vs `p=quarantine` exigé par Outlook → règle la plus stricte retenue) ; **conflit d'intérêt signalé** : la recommandation nitrosend de la source partage un fondateur avec le guide (divulgué), non relayée comme choix du template.

**Exclusions.** Sections cold email détaillées (couvert par `12-acquisition/` et sa conformité RGPD, qui fait autorité) ; canaux WhatsApp/SMS/RCS (hors périmètre du template) ; table de sélection de plateformes (l'outil est `{{EMAIL_MARKETING_TOOL}}` via `/tools-setup`) ; recettes de flows détaillées (couvert par les skills `email` / `email-sequence`) ; liens promotionnels vers nitrosend/emailmarketingskill (conservé uniquement en attribution de source).

---

## 4. accessibility-agents (Community-Access) → skill `accessibility-web` + agent `a11y-auditor`

| | |
|---|---|
| **Source** | https://github.com/Community-Access/accessibility-agents |
| **Licence** | MIT — © 2026 Taylor Arndt (LICENSE vérifié le 2026-07-02) |
| **Version vendorisée** | v6.0.0 (release du 2026-06-15), branche `main`, commit `0872b4a776` |
| **Fichiers créés** | `.claude/skills/accessibility-web/SKILL.md`, `.claude/agents/a11y-auditor.md` |

**Sélection.** Le dépôt d'origine compte 80 agents (web, documents Office/PDF/EPUB, desktop, mobile, CI, gestion de repo…). Vendorisé : le **sous-ensemble web uniquement**, soit 10 spécialistes condensés — web-accessibility-wizard (orchestration, modèle de sévérité), alt-text-headings, aria-specialist, keyboard-navigator, modal-specialist, forms-specialist, contrast-master, live-region-controller, tables-data-specialist, link-checker — en **une skill** référentiel WCAG 2.2 AA (9 domaines + modèle de sévérité) et **un agent** d'audit exécutable (axe-core via Playwright + vérifications manuelles clavier/modales/formulaires).

**Adaptations.** Traduction/condensation en français ; ancrage sur les cas d'usage du template : skills `landing-page` (revue a11y avant livraison) et dashboard `11-reporting/` (tableaux de données, live regions) ; contexte légal European Accessibility Act (applicable depuis le 28 juin 2025) explicité comme motif de blocage ; corrections de contraste contraintes aux tokens `01-brand/style-guide.md` ; partage de périmètre documenté avec l'agent `qa-visuel` existant (decks/carrousels vs pages web) ; le wizard interactif multi-phases (vscode_askQuestions) remplacé par un agent dispatché non interactif au format des agents du template.

**Exclusions.** Les ~70 agents hors web : documents (Word/Excel/PowerPoint/PDF/EPUB/markdown), desktop (NVDA, wxPython), mobile, CI/DevOps, gestion GitHub/wiki/release, analytics, WCAG AAA et WCAG 3 preview (le template vise AA), screen-reader-lab, i18n ; le serveur MCP, la CLI Go, l'extension VS Code, le plugin Codex/Gemini, les installeurs et hooks.
