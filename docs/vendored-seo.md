# Registre de vendoring — SEO (claude-seo)

Le template est **standalone au fork** : les capacités d'analyse SEO sont vendorées (copiées et adaptées) plutôt que dépendantes d'un plugin externe. Ce registre trace la provenance, la sélection et la procédure de re-synchronisation.

## Source

| Champ | Valeur |
|---|---|
| Projet | **claude-seo** — AgriciDaniel |
| Repo | https://github.com/AgriciDaniel/claude-seo |
| Marketplace / plugin | `agricidaniel-seo` / `claude-seo` |
| Version vendorée | **1.9.0** (cache local `~/.claude/plugins/cache/agricidaniel-seo/claude-seo/1.9.0/`) |
| Date de vendoring | **2026-07-02** |
| Licence constatée | **MIT** (fichier `LICENSE` du plugin, copyright (c) 2026 agricidaniel) — permissive, copie/modification/redistribution autorisées avec conservation de la notice |

## Sélection

### Vendoré (adapté en français, condensé, intégré au template)

| Fichier du template | Source(s) dans claude-seo | Rôle |
|---|---|---|
| `.claude/skills/seo-audit/SKILL.md` | `skills/seo-audit` + `skills/seo-page` | Audit de site (crawl, score de santé, plan d'action) **et** analyse de page unique |
| `.claude/skills/seo-schema/SKILL.md` | `skills/seo-schema` | Détection/validation/génération JSON-LD ; types actifs/restreints/dépréciés (état fév. 2026) |
| `.claude/skills/seo-geo/SKILL.md` | `skills/seo-geo` | GEO/AEO : AI Overviews, ChatGPT, Perplexity ; crawlers IA, llms.txt, citabilité 134-167 mots |
| `.claude/skills/seo-cluster/SKILL.md` | `skills/seo-cluster` | Clustering par recouvrement de SERP, hub-and-spoke, matrice de maillage |
| `.claude/agents/seo-technical.md` | `agents/seo-technical` (+ éléments de `seo-performance`, `seo-sitemap`) | Crawlabilité, indexation, CWV (INP), rendu JS |
| `.claude/agents/seo-content.md` | `agents/seo-content` | E-E-A-T, lisibilité, contenu mince, citabilité IA |
| `.claude/agents/seo-google.md` | `agents/seo-google` | CrUX / GSC / GA4 via le couplage `/tools-setup` |

La table de délégation de `.claude/skills/seo/SKILL.md` pointe désormais vers ces skills/agents internes (plus vers le plugin).

### Exclu (et pourquoi)

| Élément source | Raison d'exclusion |
|---|---|
| `seo-local`, `seo-maps` | SEO local / Google Business Profile / geo-grid — volumineux, hors du cœur d'une équipe marketing-com généraliste ; extension possible |
| `seo-ecommerce` | Schema produit / Google Shopping / Amazon — spécifique e-commerce ; extension possible |
| `seo-backlinks` | Dépend d'APIs tierces (Moz, Bing WMT, Common Crawl) non configurées dans le template |
| `seo-dataforseo` | Dépend du MCP payant DataForSEO |
| `seo-drift` | Système de baselines/snapshots adossé aux scripts Python du plugin (non vendorés) |
| `seo-hreflang`, `seo-sitemap`, `seo-images`, `seo-image-gen`, `seo-sxo`, `seo-programmatic`, `seo-plan`, `seo-competitor-pages` | Couverts en version condensée dans les skills vendorées (sitemap/images → `seo-audit`), redondants avec des skills du template (`image-generation`, `content-strategy`, `veille-strategy`), ou trop spécialisés pour le périmètre |
| Scripts Python (`scripts/`), rapports PDF, hooks, extensions | Infrastructure propre au plugin ; les skills vendorées utilisent WebFetch/WebSearch/curl et les connecteurs `_integrations/` du template |
| Agents `seo-performance`, `seo-visual`, `seo-schema`, `seo-sitemap`… | Fusionnés dans les 3 agents vendorés ou remplacés par les skills correspondantes |

Si un besoin exclu apparaît : installer le plugin `claude-seo` complet **en complément** (les skills internes restent prioritaires, règle du CLAUDE.md racine), ou re-vendorer la brique.

## Adaptations effectuées

- **Traduction française** et condensation (~6 500 lignes source → ~7 fichiers opérationnels).
- **Ancrage template** : sorties dans `09-seo/audits/`, briefs au format de la skill `seo`, calendrier `02-strategy/calendar/`, placeholders `{{COMPANY_NAME}}`/`{{COMPANY_WEBSITE}}`.
- **Suppression des dépendances** aux scripts Python, à DataForSEO et à claude-blog ; remplacées par WebFetch/WebSearch/curl et le couplage GA4/GSC de `/tools-setup`.
- **Règles du template injectées** : preuve traçable vers `01-brand/messaging-framework.md`, filtre anti-style-IA (agent `seo-content`), crawl plafonné à 50 pages (vs 500).
- **Données périssables signalées** : statistiques GEO et statuts de types schema datés (début 2026) avec consigne de re-vérification.

## Procédure de re-sync

1. Mettre à jour le plugin : `claude plugin update claude-seo` (ou consulter le repo GitHub) ; noter la nouvelle version et son `CHANGELOG.md`.
2. Vérifier que le `LICENSE` est toujours MIT. Si la licence change, **stopper** et arbitrer.
3. Diff des sources vendorées : `skills/{seo-audit,seo-page,seo-schema,seo-geo,seo-cluster}/SKILL.md` et `agents/{seo-technical,seo-content,seo-google}.md` entre l'ancienne et la nouvelle version du cache.
4. Reporter manuellement les changements pertinents dans les fichiers du template (ce sont des **adaptations**, pas des copies : ne jamais écraser).
5. Points de péremption à re-vérifier en priorité : seuils CWV, liste des types schema dépréciés/restreints, liste des crawlers IA, statistiques GEO.
6. Mettre à jour ce registre (version, date) et le `CHANGELOG.md` du template.
