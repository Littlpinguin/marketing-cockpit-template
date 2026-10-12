# État de l'art — écosystème des skills Claude Code pour un copilot marketing (juillet 2026)

> Recherche menée le 2026-07-02. Méthode : recensement via awesome-lists (ComposioHQ, travisvn, VoltAgent), marketplaces (skills.sh, ClaudeSkills.info, SkillsMP), classements 2026 (Composio, Firecrawl, Growth Hackers, AI Builder Club), puis **vérification directe de chaque repo GitHub candidat** (contenu réel du SKILL.md, licence, étoiles, activité).
>
> Déjà vendorisé dans le template (hors périmètre de cette analyse) : `ui-ux-pro-max`, `frontend-design` (Anthropic), `claude-seo` (AgriciDaniel, 25 sub-skills + 18 agents), pack CRO/marketing de Corey Haines (`marketingskills` : copywriting, page-cro, email-sequence, pricing-strategy, customer-research, analytics-tracking, marketing-psychology, cold-email, paid-ads, etc.), `web-artifacts-builder` (Anthropic).
>
> **Bilan : 25 candidates examinées, 6 retenues (VENDORISER), 19 écartées.** La majorité des skills communautaires « marketing » sont soit des coquilles promotionnelles, soit des redites du pack Corey Haines déjà en place. Les vraies valeurs ajoutées sont concentrées chez une poignée d'auteurs (AgriciDaniel, Leonxlnx, CosmoBlk, Community-Access).

---

## 1. Design / UI — et le cas Taste Skill vs ui-ux-pro-max

| Skill / repo | URL | Licence | Étoiles / activité | Apport vs template | Verdict |
|---|---|---|---|---|---|
| **Taste Skill** (Leonxlnx) | https://github.com/Leonxlnx/taste-skill | MIT | **54,7k★**, 3,8k forks, 131 commits, très actif (v2 juin 2026) | Voir analyse détaillée ci-dessous | **VENDORISER** |
| Design Skill (daymade) | https://github.com/daymade/claude-code-skills | MIT | Adoption moyenne | Extraction de design tokens depuis screenshots. Utile ponctuellement, mais `ui-ux-pro-max` + `design-system` couvrent déjà la génération de tokens | IGNORER (redondant) |
| claudedesignskills (freshtechbro) | https://github.com/freshtechbro/claudedesignskills | — | 27 plugins 3D/WebGL/animation | Three.js, Babylon, Rive, Spline : hors besoin d'un copilot marketing (sites vitrines, pas d'expériences 3D) | IGNORER (hors périmètre) |
| GSAP Skills (GreenSock, officiel) | https://github.com/greensock/gsap-skills | Standard GSAP | Officiel, 8 skills | Animations scroll/SplitText pour landing pages haut de gamme. Intéressant mais Taste Skill v2 embarque déjà des squelettes GSAP canoniques ; à reconsidérer seulement si les landing pages du template deviennent très animées | IGNORER (couvert via Taste Skill) |

### Taste Skill vs ui-ux-pro-max : complémentaires, pas concurrents

Vérifié dans le repo : les deux skills n'attaquent pas le même problème.

- **`ui-ux-pro-max`** (déjà vendorisée) = une **base de données de choix** : 161 palettes, 57 paires de fontes, 50+ styles, 99 guidelines UX, 25 types de charts. Elle répond à « quel style/palette/fonte pour ce produit ? ».
- **`taste-skill`** = un **protocole d'exécution anti-slop** : 13+ skills dont `design-taste-frontend` v2 (3 curseurs paramétriques DESIGN_VARIANCE / MOTION_INTENSITY / VISUAL_DENSITY, inférence du langage design depuis le brief, squelettes GSAP canoniques, protocole de redesign-audit, pre-flight check strict, bans typographiques), plus des skills d'image-gen (`imagegen-frontend-web`, `brandkit`). Elle répond à « comment éviter que le rendu ressemble à du template IA générique ? ».

**Verdict : OUI, vendoriser en plus.** C'est le repo de design le plus adopté de l'écosystème 2026 (54,7k★), MIT, substantiel (vérifié : protocoles paramétriques, pas du vague). Recommandation : vendoriser `design-taste-frontend` (v2) + `redesign-existing-projects` + `brandkit`, pas les 13 skills (les variantes `minimalist-ui`/`industrial-brutalist-ui` sont des presets redondants avec les styles d'ui-ux-pro-max).

---

## 2. Publicité payante (gap réel du template)

| Skill / repo | URL | Licence | Étoiles / activité | Apport vs template | Verdict |
|---|---|---|---|---|---|
| **claude-ads** (AgriciDaniel) | https://github.com/AgriciDaniel/claude-ads | MIT | **6,6k★**, 994 forks, actif (mai 2026) | 22 sub-skills + 10 agents, **250+ checks d'audit vérifiés** : Google (80), Meta (50, incl. Andromeda/CAPI), LinkedIn (27), TikTok (28), Microsoft (24), Apple (35+), Amazon (30+). Harnais pytest de 41 tests (rare). La skill `paid-ads` de Corey Haines déjà vendorisée est stratégique (quel canal, quel budget) ; claude-ads est un **auditeur opérationnel** de comptes existants — rien d'équivalent dans le template | **VENDORISER** |
| claude-marketing (thatrebeccarae) | https://github.com/thatrebeccarae/claude-marketing | — | Adoption modeste | 6 skills paid media (Google/Meta/Microsoft) : sous-ensemble strict de claude-ads | IGNORER (dominé par claude-ads) |
| Higgsfield UGC Pipeline (AKCodez) | https://github.com/AKCodez/higgsfield-claude-skills | — | Niche | Génération de vidéos UGC via Higgsfield : dépend d'un service tiers payant spécifique ; le template a déjà `video-editing`, `ad-creative`, hyperframes (installé par le module vidéo, plugin `hyperframes@hyperframes`) | IGNORER (dépendance tierce, redondant) |
| cognyai/claude-code-marketing-skills | https://github.com/cognyai/claude-code-marketing-skills | — | Vitrine produit COGNY | Connexions temps réel GSC/Google Ads/Meta : c'est un wrapper autour de leur plateforme, pas une skill autonome | IGNORER (coquille commerciale) |

---

## 3. Contenu blog / éditorial

| Skill / repo | URL | Licence | Étoiles / activité | Apport vs template | Verdict |
|---|---|---|---|---|---|
| **claude-blog** (AgriciDaniel) | https://github.com/AgriciDaniel/claude-blog | MIT | **1,3k★**, 223 forks, v1.9.1 (20 mai 2026), 18 releases, 160+ tests | Moteur de production blog complet : 30 sub-skills (8 clusters), 5 agents dont reviewer bloquant, 12 templates auto-sélectionnés, **contrat de livraison à 5 portes (score ≥ 90/100 sinon itération)**, vérification factuelle avec fetch des sources, détection de prose IA (burstiness), pipeline d'images hero, publication multilingue avec hreflang. Le template a `content-strategy` + `seo` + `copywriting`, mais **aucun moteur de production d'articles bout-en-bout avec quality gates**. Même auteur que claude-seo déjà vendorisée → cohérence des conventions | **VENDORISER** |
| **humanize-writing** (jpeggdev) | https://github.com/jpeggdev/humanize-writing | MIT | 31★, 6 forks, jeune | Système d'édition en 8 passes qui traque les patterns d'écriture IA (vocabulaire banni, tells structurels, hedging, transitions répétitives, injection de voix). Vérifié : substantiel malgré sa petite taille. `copy-editing` (Corey Haines) édite pour la clarté/persuasion mais n'a **pas** de protocole anti-détection-IA systématique. Micro-skill, coût de vendorisation quasi nul, gros effet sur la crédibilité des livrables | **VENDORISER** |
| Content Ops (superamped/ai-marketing-skills) | https://github.com/superamped/ai-marketing-skills | MIT | 50★, 11 commits, quasi dormant | 18 skills (ads, contenu, Reddit, research) correctes mais chacune dominée par un équivalent déjà en place (Corey Haines, claude-ads, claude-blog) | IGNORER (redondant, faible traction) |
| Charlie Hills social-media-skills | https://github.com/charlie947/social-media-skills | — | Non vérifiable en profondeur | « Voice-first repurposing » : le concept est déjà couvert par `social-content` + skills carrousel maison | IGNORER (redondant) |

---

## 4. Email

| Skill / repo | URL | Licence | Étoiles / activité | Apport vs template | Verdict |
|---|---|---|---|---|---|
| **email-marketing-bible** (CosmoBlk / George Hartley) | https://github.com/CosmoBlk/email-marketing-bible | MIT | 238★, 34 forks, v1.0 (mars 2026), 908 sources citées | 19 chapitres + **19 playbooks sectoriels** + 47 exemples de design d'emails. Couvre ce que `email` et `email-sequence` (workflows) ne couvrent pas : **délivrabilité (SPF/DKIM/DMARC/BIMI, réputation), conformité (RGPD, CAN-SPAM, CASL), design dark-mode/accessible, comparatif ESP (Klaviyo, Resend, beehiiv…), SMS/WhatsApp/RCS**. C'est une base de connaissances opérationnelle, complémentaire des skills de rédaction existantes | **VENDORISER** |
| Cold-Outreach (staybased) | https://clawskills.sh/skills/staybased-cold-outreach | Non vérifiée (pas de repo GitHub public clair) | Marketplace uniquement | Frameworks Hormozi pour cold email/SMS/LinkedIn : `cold-email` (Corey Haines) couvre déjà le sujet ; provenance et licence floues | IGNORER (redondant + licence non vérifiable) |

---

## 5. Slides / storytelling de présentation

| Skill / repo | URL | Licence | Étoiles / activité | Apport vs template | Verdict |
|---|---|---|---|---|---|
| presentation-writing-claude-skill (marcusnelson) | https://github.com/marcusnelson/presentation-writing-claude-skill | MIT | **1★**, 8 commits | 7 scaffolds narratifs (Pitch, Case, Board, Keynote, Report-Out, Workshop, Close) slide par slide, anti-filler corporate. Contenu vérifié substantiel **mais** la skill `slides` du template intègre déjà les principes Duarte/Reynolds/Tufte et une logique narrative ; adoption nulle (1★) = aucune validation communautaire | IGNORER (recouvrement fort avec `slides`, traction nulle — à réévaluer si le besoin « argumentaire de deck » devient récurrent) |
| academic-pptx-skill (Gabberflast) | https://github.com/Gabberflast/academic-pptx-skill | — | Niche académique | Talks de conférence, soutenances : hors cible marketing | IGNORER (hors périmètre) |
| frontend-slides (zarazhangrui) | https://github.com/zarazhangrui/frontend-slides | — | Modeste | Slides HTML via skills frontend : le template fait déjà exactement ça (`slides` + web-artifacts-builder) | IGNORER (redondant) |

---

## 6. Data-viz / reporting

| Skill / repo | URL | Licence | Étoiles / activité | Apport vs template | Verdict |
|---|---|---|---|---|---|
| Claude-Data-Visualisation-And-Publishing-Plugin (danielrosehill) | https://github.com/danielrosehill/Claude-Data-Visualisation-And-Publishing-Plugin | — | Modeste | Inventaire d'outils viz (Matplotlib, ECharts, D3, Vizzu…). `ui-ux-pro-max` (25 types de charts × 10 stacks), `performance-report` et la skill xlsx d'Anthropic couvrent déjà le besoin d'un copilot marketing | IGNORER (redondant) |
| GA4 Diagnostic MCP (mario-hernandez) | https://github.com/mario-hernandez/google-analytics-mcp-claude-code | — | — | C'est un MCP, pas une skill vendorisable ; et le plugin PostHog + `analytics-tracking` couvrent l'analytics | IGNORER (mauvais format, redondant) |

---

## 7. Accessibilité web (gap réel du template)

| Skill / repo | URL | Licence | Étoiles / activité | Apport vs template | Verdict |
|---|---|---|---|---|---|
| **accessibility-agents** (Community-Access) | https://github.com/Community-Access/accessibility-agents | MIT | 348★, 38 forks, **v6.0.0 (15 juin 2026)**, très actif | 79 agents WCAG **2.2 AA** (contraste, clavier, ARIA, lecteurs d'écran, live regions, formulaires, alt text, documents Office/PDF). Le template produit des landing pages, emails et slides HTML mais n'a **aucune skill d'accessibilité** — risque légal réel (European Accessibility Act en vigueur depuis juin 2025 pour les clients UE). Vendoriser **uniquement le sous-ensemble web** (~8-10 agents : contraste, ARIA, formulaires, alt text, HTML sémantique), pas les 79 | **VENDORISER (sous-ensemble web)** |
| skill-a11y-audit (snapsynapse) | https://github.com/snapsynapse/skill-a11y-audit | — | Modeste | Audit WCAG 2.1 AA drop-in, plus léger. Alternative crédible si les 79 agents ci-dessus paraissent trop lourds, mais WCAG 2.1 < 2.2 et moins actif | IGNORER (dominé par accessibility-agents) |
| claude-a11y-skill (airowe) | https://github.com/airowe/claude-a11y-skill | — | Modeste | axe-core + jsx-a11y : orienté codebases React, pas livrables marketing | IGNORER (orienté dev, pas marketing) |

---

## 8. Traduction / localisation

| Skill / repo | URL | Licence | Étoiles / activité | Apport vs template | Verdict |
|---|---|---|---|---|---|
| **claude-translation-skill** (senshinji) | https://github.com/senshinji/claude-translation-skill | MIT | 10★, jeune | Pipeline multi-agents vérifié : traducteur Sonnet + chercheurs de terminologie parallèles (glossaire web-vérifié avec scores de confiance) + reviewer Opus anti-fabrication + typesetting .docx/.pdf. Le template (clients FR → contenus parfois EN) n'a **rien** pour la localisation de campagnes ; claude-blog apporte le multilingue *blog* mais pas la traduction de documents/campagnes arbitraires. Faible traction mais architecture solide et coût de vendorisation faible | **VENDORISER** (choix « meilleur disponible » dans un domaine pauvre) |
| translate-book (deusyu) | https://github.com/deusyu/translate-book | — | Niche | Traduction de livres entiers PDF/EPUB : hors besoin marketing | IGNORER (hors périmètre) |
| translate (feiskyer/claude-code-settings) | https://github.com/feiskyer/claude-code-settings | — | — | Skill de traduction basique une-passe, sans vérification terminologique | IGNORER (dominé) |

---

## 9. SEO / GEO, research, personas, pricing, growth — rien à ajouter

Domaines vérifiés où **le template est déjà à l'état de l'art**, candidates écartées :

| Skill / repo | URL | Raison de l'écartement |
|---|---|---|
| geo-seo-claude (zubair-trabzada) | https://github.com/zubair-trabzada/geo-seo-claude | GEO/AEO, llms.txt, schema : intégralement couvert par `claude-seo:seo-geo` + `ai-seo` + `schema-markup` déjà en place |
| seo-geo-claude-skills (aaron-he-zhu) | https://github.com/aaron-he-zhu/seo-geo-claude-skills | Idem — sous-ensemble de claude-seo |
| claude-skill-seo-geo-optimizer (199-biotechnologies) | https://github.com/199-biotechnologies/claude-skill-seo-geo-optimizer | Idem |
| ai-marketing-claude (zubair-trabzada) | https://github.com/zubair-trabzada/ai-marketing-claude | 2k★ MIT, substantiel mais **dormant** ; ses 14 skills (audit, copy, funnel, branding, proposals) recouvrent à ~90 % le pack Corey Haines + claude-seo. Orienté « vendre des rapports PDF à des clients d'agence », pas copilot au quotidien |
| Deep-Research-skills (Weizhena) | https://github.com/Weizhena/Deep-Research-skills | Le template a déjà `deep-research` + `veille-strategy` |
| firecrawl-claude-plugin | https://github.com/firecrawl/firecrawl-claude-plugin | Le template a déjà `scraping` ; Firecrawl = dépendance API payante |
| sales-skills/sales | https://github.com/sales-skills/sales | CRM/prospection : couvert par `revops`, `sales-enablement`, `cold-email` |
| linkedin-skills (sergebulaev) | https://github.com/sergebulaev/linkedin-skills | 289★ MIT, v1.0.6 (juillet 2026), substantiel (16 formules de hooks, post audit, humanizer). Mais recouvre `social-content` + les skills carrousel/post maison déjà affûtées par client ; ses intégrations Apify/Publora sont des dépendances payantes. **Second couteau honorable** — à réévaluer si un besoin d'audit algorithmique LinkedIn émerge |
| Personas / pricing / growth (divers marketplaces) | skills.sh, ClaudeSkills.info | Rien trouvé qui dépasse `customer-research`, `pricing-strategy`, `launch-strategy`, `referral-program`, `free-tool-strategy` (Corey Haines) — les skills « persona generator » des marketplaces sont des prompts d'une page sans méthodologie |
| wilwaldon/Claude-Code-Video-Toolkit | https://github.com/wilwaldon/Claude-Code-Video-Toolkit | Remotion + Manim, 55 exemples : le template a hyperframes (installé par le module vidéo, plugin `hyperframes@hyperframes`) + `video-editing` ; Manim est orienté éducation scientifique (depuis octobre 2026, Manim est couvert par les skills vendorisées de manim_skill, section 10) |
| ok-skills / Remotion (mxyhi) | https://github.com/mxyhi/ok-skills | Idem — hyperframes (installé par le module vidéo, plugin `hyperframes@hyperframes`) couvre le besoin vidéo programmatique |

---

## 10. Vidéo (mise à jour du 2026-10-12, studio vidéo v2)

Ajout postérieur à la recherche de juillet : deux sources examinées pour le module vidéo, avec HyperFrames (Apache-2.0) installé comme plugin officiel par `/modules` plutôt que vendorisé. Détail, périmètre et procédure : `docs/vendored-video.md`.

| Skill / repo | URL | Licence | Étoiles / activité | Apport vs template | Verdict |
|---|---|---|---|---|---|
| OpenMontage (calesthio) | https://github.com/calesthio/OpenMontage | AGPLv3 | Non relevé ; commit consulté `9327439` (2026-10-03) | Méthode de production vidéo (pipelines par type de vidéo, validations, contrat de coût, revue, format court, documentaire). Licence incompatible avec le MIT du template | MÉTHODE RÉÉCRITE (rien de copié ; code lourd du template écrit en salle blanche ; voir `docs/vendored-video.md`) |
| manim_skill (adithya-s-k) | https://github.com/adithya-s-k/manim_skill | MIT | Non relevé ; commit vendorisé `cef0450` (2026-01-23) | Planification de scène et bonnes pratiques Manim Community, pour la filière « démonstration conceptuelle ou chiffrée » | VENDORISÉ (`manim-composer`, `manim-ce` ; Markdown seulement, exemples Python non repris) |

## Synthèse — plan de vendorisation recommandé (par priorité)

| # | Skill | URL | Licence | Apport |
|---|---|---|---|---|
| 1 | **taste-skill** (sous-ensemble : design-taste-frontend v2, redesign-existing-projects, brandkit) | https://github.com/Leonxlnx/taste-skill | MIT | Protocole anti-slop paramétrique + motion GSAP, complémentaire de la base de données ui-ux-pro-max |
| 2 | **claude-ads** | https://github.com/AgriciDaniel/claude-ads | MIT | Audit opérationnel paid media 250+ checks sur 7 plateformes — gap total du template |
| 3 | **claude-blog** | https://github.com/AgriciDaniel/claude-blog | MIT | Moteur de production d'articles avec quality gates, fact-checking et multilingue — même auteur que claude-seo |
| 4 | **email-marketing-bible** | https://github.com/CosmoBlk/email-marketing-bible | MIT | Base de connaissances délivrabilité/conformité/design email absente des skills workflow existantes |
| 5 | **accessibility-agents** (sous-ensemble web) | https://github.com/Community-Access/accessibility-agents | MIT | Conformité WCAG 2.2 AA des livrables web — gap total + enjeu légal (EAA) |
| 6 | humanize-writing + claude-translation-skill (bonus, coût quasi nul) | https://github.com/jpeggdev/humanize-writing · https://github.com/senshinji/claude-translation-skill | MIT | Passe anti-détection-IA ; pipeline de traduction vérifiée |

Toutes les recommandations sont MIT : vendorisation légalement propre (conserver les LICENSE et attributions dans `_sources/`).
